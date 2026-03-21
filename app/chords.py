from __future__ import annotations

import argparse
from pathlib import Path

import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _infer_triad(chroma_vector: np.ndarray) -> str:
    """Infer a basic major/minor triad from a single chroma vector."""
    root = int(np.argmax(chroma_vector))
    major_third = chroma_vector[(root + 4) % 12]
    minor_third = chroma_vector[(root + 3) % 12]
    root_name = NOTE_NAMES[root]

    if major_third - minor_third > 0.05:
        return root_name
    elif minor_third - major_third > 0.05:
        return f"{root_name}m"
    else:
        return root_name


def detect_chords(path: str | Path) -> list:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    chroma = librosa.feature.chroma_stft(y=waveform, sr=sample_rate)

    # Group frames into ~1 second blocks for stable, human-readable chord changes.
    hop_length = 512
    frames_per_second = sample_rate / hop_length
    block_size = max(1, int(round(frames_per_second)))

    chords: list[str] = []
    for start in range(0, chroma.shape[1], block_size):
        block = chroma[:, start : start + block_size]
        if block.size == 0:
            continue
        block_mean = np.mean(block, axis=1)
        chord = _infer_triad(block_mean)

        if not chords or chords[-1] != chord:
            chords.append(chord)

    return chords


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect simple chord progression from audio.")
    parser.add_argument("audio_path", help="Path to input audio file")
    args = parser.parse_args()

    result = detect_chords(args.audio_path)
    print(result)


if __name__ == "__main__":
    main()
