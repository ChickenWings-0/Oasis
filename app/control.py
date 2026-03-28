from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from app.analysis import detect_key
from app.config import OUTPUT_DIR

NOTE_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11,
}


def _load_audio(path: str | Path) -> tuple[np.ndarray, int, Path]:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    return waveform, sample_rate, audio_path


def _save_audio(waveform: np.ndarray, sample_rate: int, output_name: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_name
    sf.write(str(output_path), waveform, sample_rate)
    return str(output_path.resolve())


def _sanitize_key_name(key_name: str) -> str:
    cleaned = key_name.strip().replace(" major", "").replace(" minor", "")
    cleaned = cleaned.replace("maj", "").replace("min", "m")
    if cleaned.endswith("m"):
        cleaned = cleaned[:-1]
    return cleaned


def _estimate_tempo(y: np.ndarray, sr: int) -> float:
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        return float(tempo[0]) if tempo.size > 0 else 0.0
    return float(tempo)


def change_bpm(path: str | Path, target_bpm: float) -> str:
    waveform, sample_rate, audio_path = _load_audio(path)

    if target_bpm <= 0:
        raise ValueError("target_bpm must be greater than 0")

    original_bpm = _estimate_tempo(waveform, sample_rate)
    if original_bpm <= 0:
        raise RuntimeError("Unable to estimate original BPM")

    rate = float(target_bpm) / float(original_bpm)

    print(f"Original BPM: {original_bpm}")
    print(f"Target BPM: {target_bpm}")
    print(f"Rate: {rate}")

    stretched = librosa.effects.time_stretch(waveform, rate=rate)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"bpm_changed_{audio_path.stem}_{stamp}.wav"
    return _save_audio(stretched, sample_rate, output_name)


def change_pitch_scale(path: str | Path, target_key: str) -> str:
    waveform, sample_rate, audio_path = _load_audio(path)

    current_key_info = detect_key(path)
    current_key = _sanitize_key_name(str(current_key_info.get("key", "")))
    target_key_clean = _sanitize_key_name(target_key)

    if current_key not in NOTE_TO_SEMITONE:
        raise RuntimeError(f"Detected key is unsupported: {current_key}")
    if target_key_clean not in NOTE_TO_SEMITONE:
        raise ValueError(f"target_key is unsupported: {target_key_clean}")

    current_semitone = NOTE_TO_SEMITONE[current_key]
    target_semitone = NOTE_TO_SEMITONE[target_key_clean]
    semitone_shift = target_semitone - current_semitone

    shifted = librosa.effects.pitch_shift(waveform, sr=sample_rate, n_steps=semitone_shift)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"key_changed_{audio_path.stem}_{stamp}.wav"
    return _save_audio(shifted, sample_rate, output_name)


def apply_section_tempo(path: str | Path, sections: list) -> str:
    waveform, sample_rate, audio_path = _load_audio(path)

    if not sections:
        raise ValueError("sections cannot be empty")

    original_bpm = _estimate_tempo(waveform, sample_rate)
    if original_bpm <= 0:
        raise RuntimeError("Unable to estimate original BPM from full audio")

    full_duration = len(waveform) / float(sample_rate)
    output_segments: list[np.ndarray] = []
    rate_cache: dict[float, float] = {}

    for section in sections:
        start_sec = float(section.get("start", 0.0))
        end_sec = float(section.get("end", 0.0))
        target_bpm = float(section.get("bpm", 0.0))

        if target_bpm <= 0:
            raise ValueError("Each section bpm must be greater than 0")

        start_sec = max(0.0, min(start_sec, full_duration))
        end_sec = max(0.0, min(end_sec, full_duration))
        if end_sec <= start_sec:
            continue

        start_idx = int(round(start_sec * sample_rate))
        end_idx = int(round(end_sec * sample_rate))
        segment = waveform[start_idx:end_idx]

        if segment.size == 0:
            continue

        if target_bpm not in rate_cache:
            rate_cache[target_bpm] = float(target_bpm) / float(original_bpm)

        rate = rate_cache[target_bpm]

        print(f"Original BPM: {original_bpm}")
        print(f"Target BPM: {target_bpm}")
        print(f"Rate: {rate}")

        stretched_segment = librosa.effects.time_stretch(segment, rate=rate)
        expected_len = max(1, int(len(segment) / rate))
        stretched_segment = stretched_segment[:expected_len]

        if len(stretched_segment) < expected_len:
            stretched_segment = np.pad(
                stretched_segment,
                (0, expected_len - len(stretched_segment)),
                mode="constant",
            )

        output_segments.append(stretched_segment)

    if not output_segments:
        raise RuntimeError("No valid sections were processed")

    combined = np.concatenate(output_segments, axis=0)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"section_tempo_{audio_path.stem}_{stamp}.wav"
    return _save_audio(combined, sample_rate, output_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audio control layer: BPM, key, and section tempo changes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bpm_parser = subparsers.add_parser("change-bpm", help="Change overall BPM")
    bpm_parser.add_argument("audio_path", help="Path to input audio")
    bpm_parser.add_argument("target_bpm", type=float, help="Target BPM")

    key_parser = subparsers.add_parser("change-key", help="Change overall key")
    key_parser.add_argument("audio_path", help="Path to input audio")
    key_parser.add_argument("target_key", help="Target key (e.g., C, D#, Am)")

    section_parser = subparsers.add_parser("section-tempo", help="Apply tempo per section")
    section_parser.add_argument("audio_path", help="Path to input audio")
    section_parser.add_argument(
        "sections_json",
        help='JSON list, e.g. [{"start":0,"end":5,"bpm":80},{"start":5,"end":10,"bpm":120}]',
    )

    args = parser.parse_args()

    if args.command == "change-bpm":
        output = change_bpm(args.audio_path, args.target_bpm)
    elif args.command == "change-key":
        output = change_pitch_scale(args.audio_path, args.target_key)
    else:
        from pathlib import Path

        sections_arg = args.sections_json

        sections_path = Path(sections_arg).expanduser().resolve()

        if sections_path.exists() and sections_path.is_file():
            with open(sections_path, "r") as f:
                sections = json.load(f)
        else:
            sections = json.loads(sections_arg)
        output = apply_section_tempo(args.audio_path, sections)

    print(output)


if __name__ == "__main__":
    main()
