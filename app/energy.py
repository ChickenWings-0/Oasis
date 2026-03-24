from __future__ import annotations
import librosa
import numpy as np
from pathlib import Path


def analyze_energy_profile(path: str | Path, segment_duration: int = 10) -> list:
    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)

    # Beat tracking
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    total_duration = librosa.get_duration(y=y, sr=sr)

    raw_scores = []
    segments = []

    for start in range(0, int(total_duration), segment_duration):
        end = min(start + segment_duration, total_duration)

        segment = y[int(start * sr):int(end * sr)]
        if len(segment) == 0:
            continue

        # Features
        rms = np.mean(librosa.feature.rms(y=segment))
        centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sr))
        zcr = np.mean(librosa.feature.zero_crossing_rate(segment))

        score = (rms * 2.5) + (centroid / 5000) + (zcr * 2.0)

        raw_scores.append(score)
        segments.append((start, end))

    # Smooth scores
    smoothed = []
    window = 2

    for i in range(len(raw_scores)):
        start_i = max(0, i - window)
        end_i = min(len(raw_scores), i + window + 1)
        smoothed.append(np.mean(raw_scores[start_i:end_i]))

    # Normalize scores
    max_score = max(smoothed) if smoothed else 1

    results = []

    for i, score in enumerate(smoothed):
        norm = score / max_score if max_score > 0 else 0

        # Detect peaks (drops)
        prev_score = smoothed[i-1] if i > 0 else score
        next_score = smoothed[i+1] if i < len(smoothed)-1 else score

        is_peak = score > prev_score and score > next_score and norm > 0.75

        if is_peak:
            label = "DROP 🔥"
        elif norm < 0.25:
            label = "calm"
        elif norm < 0.5:
            label = "chill"
        elif norm < 0.75:
            label = "build"
        else:
            label = "intense"

        results.append({
            "start": int(segments[i][0]),
            "end": int(segments[i][1]),
            "label": label
        })

    return results
