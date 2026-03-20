from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from scipy.io import wavfile
from scipy.signal import correlate
from transformers import AutoProcessor, MusicgenForConditionalGeneration

try:
    from app.config import (
        DEFAULT_DURATION_SECONDS,
        MODEL_ID,
        OUTPUT_DIR,
        SAMPLE_RATE,
        get_device,
    )
except ModuleNotFoundError:
    from config import DEFAULT_DURATION_SECONDS, MODEL_ID, OUTPUT_DIR, SAMPLE_RATE, get_device


def load_musicgen(model_id: str = MODEL_ID, device: str | None = None):
    """Load MusicGen model and processor for local inference."""
    resolved_device = device or get_device()
    processor = AutoProcessor.from_pretrained(model_id)
    model = MusicgenForConditionalGeneration.from_pretrained(model_id)
    model.to(resolved_device)
    model.eval()
    return processor, model, resolved_device


def build_output_path(output_dir: Path = OUTPUT_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"musicgen_{timestamp}.wav"


def generate_music_clip(
    prompt: str,
    duration_seconds: int = DEFAULT_DURATION_SECONDS,
    model_id: str = MODEL_ID,
    output_dir: Path = OUTPUT_DIR,
    seed: int | None = None,
) -> Path:
    """Generate a short clip from text and save it as WAV."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than 0.")

    processor, model, device = load_musicgen(model_id=model_id)
    max_new_tokens = max(1, int(duration_seconds * 50))

    inputs = processor(text=[prompt], padding=True, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    if seed is not None:
        torch.manual_seed(seed)
        if device == "cuda":
            torch.cuda.manual_seed_all(seed)

    with torch.no_grad():
        audio_values = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True)

    sample_rate = getattr(model.config.audio_encoder, "sampling_rate", SAMPLE_RATE)
    waveform = audio_values[0].detach().cpu().numpy().squeeze()
    waveform = np.clip(waveform, -1.0, 1.0)
    waveform_int16 = (waveform * 32767).astype(np.int16)

    output_path = build_output_path(output_dir=output_dir).resolve()
    wavfile.write(str(output_path), sample_rate, waveform_int16)
    return output_path


def _to_mono_float(waveform: np.ndarray) -> np.ndarray:
    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)
    if waveform.dtype == np.int16:
        return waveform.astype(np.float32) / 32768.0
    return waveform.astype(np.float32)


def estimate_bpm(waveform: np.ndarray, sample_rate: int) -> float | None:
    """Very basic BPM estimation using autocorrelation of short-time energy."""
    if waveform.size < sample_rate:
        return None

    frame_size = 2048
    hop_size = 512
    if waveform.size < frame_size + hop_size:
        return None

    energies = []
    for start in range(0, waveform.size - frame_size, hop_size):
        frame = waveform[start : start + frame_size]
        energies.append(float(np.sum(frame * frame)))

    energy = np.array(energies, dtype=np.float32)
    energy = energy - np.mean(energy)
    if np.allclose(energy, 0.0):
        return None

    auto = correlate(energy, energy, mode="full")
    auto = auto[auto.size // 2 :]

    min_bpm = 60
    max_bpm = 180
    min_lag = int((60.0 / max_bpm) * sample_rate / hop_size)
    max_lag = int((60.0 / min_bpm) * sample_rate / hop_size)
    if max_lag <= min_lag or max_lag >= auto.size:
        return None

    best_lag = min_lag + int(np.argmax(auto[min_lag : max_lag + 1]))
    if best_lag <= 0:
        return None
    return 60.0 * sample_rate / (best_lag * hop_size)


def estimate_key(waveform: np.ndarray, sample_rate: int) -> tuple[str, str]:
    """Very basic key/scale estimation from pitch-class energy profile."""
    n = waveform.size
    if n < sample_rate:
        return "Unknown", "Unknown"

    spectrum = np.abs(np.fft.rfft(waveform))
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    profile = np.zeros(12, dtype=np.float64)
    valid = (freqs >= 27.5) & (freqs <= 4186.0)
    valid_freqs = freqs[valid]
    valid_mags = spectrum[valid]
    if valid_freqs.size == 0:
        return "Unknown", "Unknown"

    midi = np.rint(69 + 12 * np.log2(valid_freqs / 440.0)).astype(int)
    pitch_classes = np.mod(midi, 12)
    for pc, mag in zip(pitch_classes, valid_mags):
        profile[int(pc)] += float(mag)

    if np.allclose(profile, 0.0):
        return "Unknown", "Unknown"

    major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    best_score = -np.inf
    best_root = 0
    best_mode = "Major"
    for shift in range(12):
        major_score = float(np.dot(profile, np.roll(major_template, shift)))
        minor_score = float(np.dot(profile, np.roll(minor_template, shift)))
        if major_score > best_score:
            best_score = major_score
            best_root = shift
            best_mode = "Major"
        if minor_score > best_score:
            best_score = minor_score
            best_root = shift
            best_mode = "Minor"

    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return note_names[best_root], best_mode


def analyze_audio_file(wav_path: Path) -> dict[str, object]:
    """Return optional, basic post-generation analysis from a WAV file."""
    sample_rate, waveform = wavfile.read(str(wav_path))
    mono = _to_mono_float(waveform)

    bpm = estimate_bpm(mono, sample_rate)
    key, scale = estimate_key(mono, sample_rate)

    return {
        "bpm": round(float(bpm), 2) if bpm is not None else None,
        "key": key,
        "scale": scale,
    }
