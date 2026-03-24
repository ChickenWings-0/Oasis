from __future__ import annotations
import sys
import librosa
import numpy as np
from pathlib import Path


def detect_strums(path: str | Path) -> list:
    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)

    # detect onset frames (strum points)
    onset_frames = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        backtrack=True,
        pre_max=30,
        post_max=30,
        pre_avg=200,
        post_avg=200,
        delta=0.3,
        wait=20
    )

    times = librosa.frames_to_time(onset_frames, sr=sr)

    return list(times)


def estimate_strum_pattern(strums: list) -> str:
    if len(strums) < 3:
        return "insufficient data"

    intervals = np.diff(strums)

    mean = np.mean(intervals)
    std_dev = np.std(intervals)

    if std_dev < 0.05:
        return "very steady"
    elif std_dev < 0.15:
        return "steady"
    elif std_dev < 0.3:
        return "moderate"
    else:
        return "free / expressive"


def analyze_strumming(path: str | Path) -> dict:
    strums = detect_strums(path)
    pattern = estimate_strum_pattern(strums)

    return {
        "count": len(strums),
        "pattern": pattern,
        "times": strums[:20]  # limit for UI readability
    }


def main():
    path = sys.argv[1]
    result = analyze_strumming(path)
    print(result)


if __name__ == "__main__":
    main()
