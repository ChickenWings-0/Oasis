from __future__ import annotations

import argparse
import json
from pathlib import Path

import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
COMMON_BPMS = [60, 70, 80, 90, 100, 110, 120, 130, 140]


def detect_bpm_robust(
    waveform: np.ndarray,
    sr: int,
) -> dict[str, float | int | str | None]:
    """Detect BPM robustly for full music input."""
    sr_i = int(sr)
    if sr_i <= 0:
        raise ValueError("sr must be > 0")

    y = np.asarray(waveform, dtype=np.float32)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)

    if y.size == 0:
        return {
            "bpm": None,
            "confidence": 0.0,
            "method": "empty_waveform",
        }

    bpm_raw = 120.0
    confidence = 0.0
    method = "fallback_default"

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr_i)
    beats = np.asarray(beats, dtype=int)
    if beats.size >= 2 and np.isfinite(float(tempo)) and float(tempo) > 0:
        bpm_raw = float(tempo)
        if bpm_raw < 70.0:
            bpm_raw *= 2.0
        elif bpm_raw > 180.0:
            bpm_raw /= 2.0

        beat_times = librosa.frames_to_time(beats, sr=sr_i)
        iois = _compute_valid_iois(list(beat_times))
        confidence = float(min(1.0, beats.size / 20.0))
        method = "beat_track"
    else:
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr_i,
            pre_max=5,
            post_max=5,
            pre_avg=20,
            post_avg=20,
            delta=0.05,
            wait=1,
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr_i)
        iois = _compute_valid_iois(list(onset_times))
        if iois.size < 3:
            return {
                "bpm": None,
                "confidence": 0.0,
                "method": "unstable_ioi",
            }

        if iois.size > 0:
            median_ioi = float(np.median(iois))
            if median_ioi > 1e-6:
                bpm_raw = 60.0 / median_ioi
                if bpm_raw < 70.0:
                    bpm_raw *= 2.0
                elif bpm_raw > 180.0:
                    bpm_raw /= 2.0

                confidence = float(min(1.0, len(onset_frames) / 20.0))
                method = "onset_ioi_fallback"

    bpm = int(round(float(np.clip(bpm_raw, 60.0, 200.0))))
    bpm = int(min(COMMON_BPMS, key=lambda x: abs(x - bpm)))
    return {
        "bpm": bpm,
        "confidence": float(np.clip(confidence, 0.0, 1.0)),
        "method": method,
    }


def _compute_valid_iois(onsets: list[float]) -> np.ndarray:
    if len(onsets) < 2:
        return np.array([], dtype=np.float64)
    iois = np.diff(np.asarray(onsets, dtype=np.float64))
    iois = iois[np.isfinite(iois) & (iois > 0.1) & (iois < 2.0)]
    return iois


def detect_bpm(path: str | Path) -> dict:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    return detect_bpm_robust(
        waveform=waveform,
        sr=int(sample_rate),
    )


def detect_key(path: str | Path) -> dict:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    if np.asarray(waveform).size == 0:
        return {
            "key": "C",
            "scale": "major",
        }

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
