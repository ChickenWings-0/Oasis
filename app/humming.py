from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly


def _to_mono_float32(waveform: np.ndarray) -> tuple[np.ndarray, str]:
    """Convert input waveform to mono float32 in [-1, 1] when possible."""
    if waveform.ndim == 1:
        mono = waveform
        channel_status = "mono"
    elif waveform.ndim == 2:
        channels = waveform.shape[1]
        channel_status = f"stereo/mono-downmix ({channels} channels)"
        mono = np.mean(waveform, axis=1)
    else:
        raise ValueError(f"Unsupported waveform shape: {waveform.shape}")

    if mono.dtype == np.int16:
        mono = mono.astype(np.float32) / 32768.0
    elif mono.dtype == np.int32:
        mono = mono.astype(np.float32) / 2147483648.0
    elif mono.dtype == np.uint8:
        mono = (mono.astype(np.float32) - 128.0) / 128.0
    else:
        mono = mono.astype(np.float32)

    return mono, channel_status


def preprocess_humming_wav(
    wav_path: Path,
    target_sample_rate: int = 32000,
) -> dict[str, object]:
    """Load and preprocess a humming/whistling WAV for future melody steps."""
    if not wav_path.exists():
        raise FileNotFoundError(f"Humming file not found: {wav_path}")
    if wav_path.suffix.lower() != ".wav":
        raise ValueError("Only WAV input is supported in this checkpoint.")
    if target_sample_rate <= 0:
        raise ValueError("target_sample_rate must be > 0")

    source_sample_rate, waveform = wavfile.read(str(wav_path))
    mono, channel_status = _to_mono_float32(waveform)

    resampled = False
    if source_sample_rate != target_sample_rate:
        mono = resample_poly(mono, target_sample_rate, source_sample_rate).astype(np.float32)
        resampled = True

    peak = float(np.max(np.abs(mono))) if mono.size else 0.0
    if peak > 1.0:
        mono = mono / peak
        normalized = True
    elif peak > 0.0:
        mono = mono / peak
        normalized = True
    else:
        normalized = False

    duration_seconds = float(mono.shape[0] / target_sample_rate)

    return {
        "input_path": str(wav_path.resolve()),
        "input_sample_rate": int(source_sample_rate),
        "target_sample_rate": int(target_sample_rate),
        "resampled": resampled,
        "channel_status": channel_status,
        "duration_seconds": round(duration_seconds, 3),
        "num_samples": int(mono.shape[0]),
        "normalized": normalized,
        "waveform": mono,
    }


def _midi_to_note_name(midi_note: int) -> str:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (midi_note // 12) - 1
    return f"{names[midi_note % 12]}{octave}"


def _freq_to_midi(freq_hz: float) -> int:
    return int(round(69 + 12 * np.log2(freq_hz / 440.0)))


def _estimate_frame_pitch_autocorr(
    frame: np.ndarray,
    sample_rate: int,
    min_hz: float = 80.0,
    max_hz: float = 1000.0,
) -> float | None:
    frame = frame.astype(np.float32)
    frame = frame - np.mean(frame)

    rms = float(np.sqrt(np.mean(frame * frame)))
    if rms < 0.01:
        return None

    corr = np.correlate(frame, frame, mode="full")
    corr = corr[corr.size // 2 :]
    if corr[0] <= 0:
        return None

    corr = corr / corr[0]
    min_lag = int(sample_rate / max_hz)
    max_lag = int(sample_rate / min_hz)
    if max_lag <= min_lag or max_lag >= corr.size:
        return None

    search = corr[min_lag : max_lag + 1]
    best_idx = int(np.argmax(search))
    best_lag = min_lag + best_idx
    strength = float(search[best_idx])

    if strength < 0.25 or best_lag <= 0:
        return None
    return float(sample_rate / best_lag)


def extract_melody_events(
    waveform: np.ndarray,
    sample_rate: int,
    frame_ms: int = 40,
    hop_ms: int = 20,
    min_event_duration_sec: float = 0.12,
    merge_gap_sec: float = 0.06,
    pitch_smooth_window: int = 5,
) -> list[dict[str, object]]:
    """Extract a simple monophonic melody event list from a waveform."""
    frame_len = max(1, int(sample_rate * frame_ms / 1000.0))
    hop_len = max(1, int(sample_rate * hop_ms / 1000.0))

    frame_times: list[float] = []
    frame_freqs: list[float | None] = []
    for start in range(0, max(1, waveform.size - frame_len + 1), hop_len):
        frame = waveform[start : start + frame_len]
        if frame.size < frame_len:
            break
        frame_times.append(start / sample_rate)
        freq = _estimate_frame_pitch_autocorr(frame, sample_rate)
        frame_freqs.append(freq)

    if not frame_freqs:
        return []

    # Median smoothing across nearby voiced frames reduces jitter before note quantization.
    smoothed_freqs: list[float | None] = []
    half_win = max(1, int(pitch_smooth_window) // 2)
    for i, f in enumerate(frame_freqs):
        if f is None:
            smoothed_freqs.append(None)
            continue

        lo = max(0, i - half_win)
        hi = min(len(frame_freqs), i + half_win + 1)
        local = [x for x in frame_freqs[lo:hi] if x is not None]
        if local:
            smoothed_freqs.append(float(np.median(local)))
        else:
            smoothed_freqs.append(None)

    raw_points: list[dict[str, object]] = []
    for t, f in zip(frame_times, smoothed_freqs):
        if f is None:
            continue
        midi = _freq_to_midi(f)
        raw_points.append(
            {
                "time_sec": round(float(t), 3),
                "freq_hz": round(float(f), 2),
                "midi": int(midi),
                "note": _midi_to_note_name(midi),
            }
        )

    if not raw_points:
        return []

    events: list[dict[str, object]] = []
    current = {
        "start_sec": raw_points[0]["time_sec"],
        "end_sec": raw_points[0]["time_sec"],
        "midi": raw_points[0]["midi"],
        "note": raw_points[0]["note"],
        "freq_values": [raw_points[0]["freq_hz"]],
    }

    for point in raw_points[1:]:
        gap = float(point["time_sec"]) - float(current["end_sec"])
        same_note = int(point["midi"]) == int(current["midi"])
        # Do not bridge across larger gaps; this keeps silence handling explicit.
        if same_note and gap <= (hop_ms / 1000.0 + 1e-6):
            current["end_sec"] = point["time_sec"]
            current["freq_values"].append(point["freq_hz"])
        else:
            avg_freq = float(np.mean(current["freq_values"]))
            events.append(
                {
                    "start_sec": round(float(current["start_sec"]), 3),
                    "end_sec": round(float(current["end_sec"]), 3),
                    "duration_sec": round(float(current["end_sec"]) - float(current["start_sec"]), 3),
                    "midi": int(current["midi"]),
                    "note": str(current["note"]),
                    "avg_freq_hz": round(avg_freq, 2),
                }
            )
            current = {
                "start_sec": point["time_sec"],
                "end_sec": point["time_sec"],
                "midi": point["midi"],
                "note": point["note"],
                "freq_values": [point["freq_hz"]],
            }

    avg_freq = float(np.mean(current["freq_values"]))
    events.append(
        {
            "start_sec": round(float(current["start_sec"]), 3),
            "end_sec": round(float(current["end_sec"]), 3),
            "duration_sec": round(float(current["end_sec"]) - float(current["start_sec"]), 3),
            "midi": int(current["midi"]),
            "note": str(current["note"]),
            "avg_freq_hz": round(avg_freq, 2),
        }
    )

    # Merge adjacent same-note events separated by tiny gaps.
    merged: list[dict[str, object]] = []
    for event in events:
        if not merged:
            merged.append(event)
            continue

        prev = merged[-1]
        gap = float(event["start_sec"]) - float(prev["end_sec"])
        same_note = int(event["midi"]) == int(prev["midi"])
        if same_note and gap <= merge_gap_sec:
            prev_start = float(prev["start_sec"])
            prev_end = float(prev["end_sec"])
            event_end = float(event["end_sec"])
            prev_dur = max(1e-6, prev_end - prev_start)
            event_dur = max(1e-6, event_end - float(event["start_sec"]))
            prev["end_sec"] = round(event_end, 3)
            prev["duration_sec"] = round(float(prev["end_sec"]) - float(prev["start_sec"]), 3)
            weighted = (float(prev["avg_freq_hz"]) * prev_dur + float(event["avg_freq_hz"]) * event_dur) / (
                prev_dur + event_dur
            )
            prev["avg_freq_hz"] = round(weighted, 2)
        else:
            merged.append(event)

    # Suppress short notes; keep only events with musically meaningful duration.
    filtered = [e for e in merged if float(e["duration_sec"]) >= min_event_duration_sec]

    return filtered


def save_melody_events_json(events: list[dict[str, object]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    return output_path


def save_melody_events_midi(
    events: list[dict[str, object]],
    output_path: Path,
    tempo_bpm: int = 120,
    velocity: int = 80,
    ticks_per_beat: int = 480,
) -> Path:
    """Export extracted melody events as a standard MIDI file."""
    try:
        import mido
    except ImportError as exc:
        raise ImportError("mido is required for MIDI export. Install with: pip install mido") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)

    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tempo = mido.bpm2tempo(tempo_bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

    event_messages: list[tuple[float, object]] = []
    for event in events:
        start_sec = max(0.0, float(event["start_sec"]))
        end_sec = max(start_sec, float(event["end_sec"]))
        note = int(event["midi"])

        event_messages.append((start_sec, mido.Message("note_on", note=note, velocity=velocity, time=0)))
        event_messages.append((end_sec, mido.Message("note_off", note=note, velocity=0, time=0)))

    event_messages.sort(key=lambda x: (x[0], 0 if x[1].type == "note_off" else 1))

    last_time_sec = 0.0
    for when_sec, msg in event_messages:
        delta_sec = max(0.0, when_sec - last_time_sec)
        delta_ticks = int(round(mido.second2tick(delta_sec, ticks_per_beat, tempo)))
        msg.time = delta_ticks
        track.append(msg)
        last_time_sec = when_sec

    mid.save(str(output_path))
    return output_path


def render_melody_guide_wav(
    events: list[dict[str, object]],
    output_path: Path,
    sample_rate: int = 32000,
    amplitude: float = 0.2,
) -> Path:
    """Render a simple sine-wave guide track from melody events."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    if amplitude <= 0:
        raise ValueError("amplitude must be > 0")

    if not events:
        raise ValueError("No melody events to render.")

    end_time = max(float(event["end_sec"]) for event in events)
    total_samples = max(1, int(np.ceil(end_time * sample_rate)))
    guide = np.zeros(total_samples, dtype=np.float32)

    fade_samples = max(1, int(0.005 * sample_rate))

    for event in events:
        start_sec = max(0.0, float(event["start_sec"]))
        end_sec = max(start_sec, float(event["end_sec"]))
        midi_note = int(event["midi"])

        start_idx = int(round(start_sec * sample_rate))
        end_idx = int(round(end_sec * sample_rate))
        if end_idx <= start_idx:
            continue

        length = end_idx - start_idx
        t = np.arange(length, dtype=np.float32) / float(sample_rate)
        freq = 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        tone = np.sin(2.0 * np.pi * freq * t).astype(np.float32)

        fade_len = min(fade_samples, length // 2)
        if fade_len > 0:
            fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
            fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
            tone[:fade_len] *= fade_in
            tone[-fade_len:] *= fade_out

        guide[start_idx:end_idx] += amplitude * tone

    peak = float(np.max(np.abs(guide))) if guide.size else 0.0
    if peak > 1.0:
        guide = guide / peak

    wav_int16 = (np.clip(guide, -1.0, 1.0) * 32767).astype(np.int16)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(output_path), sample_rate, wav_int16)
    return output_path
