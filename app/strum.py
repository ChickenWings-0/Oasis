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


def classify_rhythm(
    waveform: np.ndarray,
    sr: int,
) -> dict[str, float | str | list[float]]:
    """Classify rhythmic style using IOI CV + ratio-quantization error (full music)."""
    audio = np.asarray(waveform, dtype=np.float32)
    if audio.size == 0:
        return {
            "style": "unknown",
            "regularity": 0.0,
            "confidence": 0.0,
            "onsets": [],
            "cv": 1.0,
            "ratio_error": 1.0,
        }

    onsets = _extract_music_onsets(audio, int(sr))

    if len(onsets) < 4:
        return {
            "style": "unknown",
            "regularity": 0.0,
            "confidence": 0.0,
            "onsets": onsets,
            "cv": 1.0,
            "ratio_error": 1.0,
        }

    iois = np.diff(np.asarray(onsets, dtype=np.float64))
    iois = iois[np.isfinite(iois) & (iois > 1e-4)]
    iois = iois[(iois > 0.05) & (iois < 2.0)]
    if iois.size == 0:
        return {
            "style": "unknown",
            "regularity": 0.0,
            "confidence": 0.0,
            "onsets": onsets,
            "cv": 1.0,
            "ratio_error": 1.0,
        }

    mean_ioi = float(np.mean(iois))
    if mean_ioi <= 1e-8:
        cv = 1.0
    else:
        cv = float(np.std(iois) / mean_ioi)

    median_ioi = float(np.median(iois))
    if median_ioi <= 1e-8:
        ratio_error = 1.0
    else:
        ratios = iois / median_ioi
        rounded = np.round(ratios * 4.0) / 4.0
        ratio_error = float(np.mean(np.abs(ratios - rounded)))

    if cv < 0.15 and ratio_error < 0.1:
        style = "metronomic"
    elif cv < 0.25:
        style = "steady"
    elif cv < 0.4:
        style = "syncopated"
    else:
        style = "free/rubato"

    regularity = float(np.clip(1.0 - (0.6 * min(cv, 1.0) + 0.4 * min(ratio_error, 1.0)), 0.0, 1.0))
    confidence = float(max(0.0, (1.0 - cv) * (1.0 - ratio_error)))

    return {
        "style": style,
        "regularity": regularity,
        "confidence": confidence,
        "onsets": onsets,
        "cv": cv,
        "ratio_error": ratio_error,
    }


def _extract_music_onsets(waveform: np.ndarray, sr: int) -> list[float]:
    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=1)
    waveform = np.nan_to_num(waveform, nan=0.0, posinf=0.0, neginf=0.0)

    onset_frames = librosa.onset.onset_detect(
        y=waveform,
        sr=sr,
        backtrack=False,
        pre_max=5,
        post_max=5,
        pre_avg=20,
        post_avg=20,
        delta=0.05,
        wait=1,
    )
    times = librosa.frames_to_time(onset_frames, sr=sr)
    return list(times.astype(float))


def estimate_strum_pattern(strums: list) -> str:
    if len(strums) < 3:
        return "insufficient data"

    iois = np.diff(np.asarray(strums, dtype=np.float64))
    iois = iois[np.isfinite(iois) & (iois > 1e-4)]
    if iois.size == 0:
        return "insufficient data"

    mean_ioi = float(np.mean(iois))
    cv = float(np.std(iois) / mean_ioi) if mean_ioi > 1e-8 else 1.0
    median_ioi = float(np.median(iois))
    if median_ioi > 1e-8:
        ratios = iois / median_ioi
        rounded = np.round(ratios * 4.0) / 4.0
        ratio_error = float(np.mean(np.abs(ratios - rounded)))
    else:
        ratio_error = 1.0

    if cv < 0.15 and ratio_error < 0.1:
        return "metronomic"
    if cv < 0.25:
        return "steady"
    if cv < 0.4:
        return "syncopated"
    return "free/rubato"


def analyze_strumming(path: str | Path) -> dict:
    audio_path = Path(path).expanduser().resolve()
    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    rhythm = classify_rhythm(y, sr=sr)
    strums = rhythm.get("onsets", [])
    pattern = str(rhythm.get("style", "insufficient data"))

    return {
        "count": len(strums),
        "pattern": pattern,
        "times": strums[:20],  # limit for UI readability
        "regularity": float(rhythm.get("regularity", 0.0)),
        "confidence": float(rhythm.get("confidence", 0.0)),
    }


def main():
    path = sys.argv[1]
    result = analyze_strumming(path)
    print(result)


if __name__ == "__main__":
    main()
