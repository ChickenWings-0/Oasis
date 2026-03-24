from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from scipy.io import wavfile
from scipy.signal import correlate
from scipy.signal import resample_poly
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


MOOD_PROMPTS: dict[str, str] = {
    "EDM / Club Banger": "energetic EDM beat with heavy bass drops, synthesizers, and pulsing drums at 128 bpm, club music",
    "Trap / Hip-Hop": "dark trap beat with 808 bass, hi-hats, and atmospheric pads, hip hop production, 140 bpm",
    "Lo-fi Chill": "lo-fi hip hop beat with vinyl crackle, mellow chords, relaxed drums, chill study music",
    "Synthwave": "synthwave retro 80s electronic music with lush synthesizers, driving beat, nostalgic neon vibes",
    "Deep House": "deep house music with groovy bassline, smooth synthesizers, four-on-the-floor drums, midnight dance floor",
    "Drum and Bass": "fast drum and bass with rapid breakbeats, heavy sub-bass, aggressive energy, 174 bpm",
    "Ambient": "ambient atmospheric music with evolving synthesizer pads, ethereal textures, slow floating soundscape",
    "Phonk": "phonk music with memphis rap samples, dark twisted bass, aggressive drums, drifting energy",
    "Calm Piano": "calm solo piano music, emotional and introspective, soft dynamics, gentle melody",
    "Acoustic Guitar": "fingerpicked acoustic guitar, warm and intimate, folk style, gentle arpeggios",
    "Jazz": "smooth jazz with saxophone lead, soft piano chords, upright bass, brushed drums, late night bar vibe",
    "Blues": "soulful blues guitar with electric guitar riffs, steady rhythm, emotional and raw, Delta blues feel",
    "Orchestral": "cinematic orchestral music with strings, brass, and dramatic crescendos, epic film score feeling",
    "R&B / Soul": "modern R&B soul music with warm chord progressions, smooth bass, subtle drums, emotional vocals bed",
    "Epic Cinematic": "epic cinematic orchestral battle music with massive drums, brass fanfare, intense strings, heroic",
    "Metal": "heavy metal music with distorted electric guitars, fast double kick drums, aggressive energy",
    "Indie Rock": "indie rock with jangly guitars, energetic drums, catchy melody, stadium anthemic feel",
    "Afrobeats": "afrobeats music with percussion, talking drums, bright guitar riffs, danceable groove, West African rhythm",
    "Meditation": "peaceful meditation music with singing bowls, soft pads, nature ambience, slow breathing rhythm",
    "Nature Sounds": "gentle acoustic music blended with nature sounds, birds, stream, forest atmosphere, peaceful",
    "Sleep Drone": "slow droning ambient music, very soft, hypnotic, warm bass tones, for sleep and relaxation",
    "Bossa Nova": "bossa nova Brazilian jazz with nylon string guitar, light percussion, romantic and breezy",
    "8-Bit Game": "retro video game chiptune music with 8-bit synth melodies, catchy loop, upbeat pixel adventure mood",
    "Middle Eastern": "Middle Eastern music with oud, darbuka drums, haunting scales, traditional yet modern fusion",
}


def load_musicgen(model_id: str = MODEL_ID, device: str | None = None):
    """Load MusicGen model and processor for local inference."""
    resolved_device = device or get_device()
    processor = AutoProcessor.from_pretrained(model_id)
    model = MusicgenForConditionalGeneration.from_pretrained(model_id)
    model.to(resolved_device)
    model.eval()
    return processor, model, resolved_device


def build_output_path(output_dir: Path = OUTPUT_DIR, prefix: str = "musicgen") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"{prefix}_{timestamp}.wav"


def _load_conditioning_audio(wav_path: Path, target_sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    if not wav_path.exists():
        raise FileNotFoundError(f"Guide audio file not found: {wav_path}")

    source_sr, waveform = wavfile.read(str(wav_path))
    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)

    if waveform.dtype == np.int16:
        mono = waveform.astype(np.float32) / 32768.0
    elif waveform.dtype == np.int32:
        mono = waveform.astype(np.float32) / 2147483648.0
    elif waveform.dtype == np.uint8:
        mono = (waveform.astype(np.float32) - 128.0) / 128.0
    else:
        mono = waveform.astype(np.float32)

    if source_sr != target_sample_rate:
        mono = resample_poly(mono, target_sample_rate, source_sr).astype(np.float32)

    peak = float(np.max(np.abs(mono))) if mono.size else 0.0
    if peak > 1.0:
        mono = mono / peak
    elif peak > 0.0:
        mono = mono / peak

    return mono


def generate_music_clip(
    prompt: str,
    duration_seconds: int = DEFAULT_DURATION_SECONDS,
    model_id: str = MODEL_ID,
    output_dir: Path = OUTPUT_DIR,
    seed: int | None = None,
    guide_audio_wav: Path | None = None,
) -> Path:
    """Generate a short clip from text and save it as WAV."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than 0.")

    processor, model, device = load_musicgen(model_id=model_id)
    max_new_tokens = max(1, int(duration_seconds * 50))

    try:
        if guide_audio_wav is None:
            inputs = processor(text=[prompt], padding=True, return_tensors="pt")
        else:
            guide_audio = _load_conditioning_audio(guide_audio_wav, target_sample_rate=SAMPLE_RATE)
            inputs = processor(
                text=[prompt],
                audio=guide_audio,
                sampling_rate=SAMPLE_RATE,
                padding=True,
                return_tensors="pt",
            )
    except Exception as exc:
        raise RuntimeError(f"Guide-audio preprocessing failed: {exc}") from exc

    inputs = {key: value.to(device) for key, value in inputs.items()}

    if seed is not None:
        torch.manual_seed(seed)
        if device == "cuda":
            torch.cuda.manual_seed_all(seed)

    try:
        with torch.no_grad():
            audio_values = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True)
    except Exception as exc:
        if guide_audio_wav is not None:
            raise RuntimeError(
                f"Guide-audio conditioning failed with current Transformers interface: {exc}. "
                "No text-only fallback was executed."
            ) from exc
        raise

    sample_rate = getattr(model.config.audio_encoder, "sampling_rate", SAMPLE_RATE)
    waveform = audio_values[0].detach().cpu().numpy().squeeze()
    waveform = np.clip(waveform, -1.0, 1.0)
    waveform_int16 = (waveform * 32767).astype(np.int16)

    output_prefix = "musicgen_guided" if guide_audio_wav is not None else "musicgen"
    output_path = build_output_path(output_dir=output_dir, prefix=output_prefix).resolve()
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
