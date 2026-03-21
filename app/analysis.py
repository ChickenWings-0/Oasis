from __future__ import annotations

import argparse
import json
from pathlib import Path

import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def detect_bpm(path: str | Path) -> dict:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    tempo, _ = librosa.beat.beat_track(y=waveform, sr=sample_rate)

    return {"bpm": float(tempo)}


def detect_key(path: str | Path) -> dict:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    chroma = librosa.feature.chroma_stft(y=waveform, sr=sample_rate)
    chroma_energy = np.mean(chroma, axis=1)
    dominant_pitch_class = int(np.argmax(chroma_energy))

    return {
        "key": NOTE_NAMES[dominant_pitch_class],
        "scale": "major",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze audio for BPM and key.")
    parser.add_argument("audio_path", help="Path to the input audio file")
    args = parser.parse_args()

    result = {}
    result.update(detect_bpm(args.audio_path))
    result.update(detect_key(args.audio_path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
