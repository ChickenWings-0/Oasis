from __future__ import annotations
import librosa
import numpy as np
from pathlib import Path


def analyze_energy_profile(path: str | Path, segment_duration: int = 10) -> list:
    audio_path = Path(path).expanduser().resolve()

    waveform, sr = librosa.load(str(audio_path), sr=None, mono=True)
    total_duration = librosa.get_duration(y=waveform, sr=sr)

    rms = librosa.feature.rms(
        y=waveform,
        frame_length=2048,
        hop_length=512,
    )[0]

    frame_times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=512,
    )

    rms_norm = rms / (np.max(rms) + 1e-6)

    def moving_average(x: np.ndarray, window: int = 5) -> np.ndarray:
        kernel = np.ones(window) / window
        padded = np.pad(x, (window // 2, window // 2), mode="edge")
        return np.convolve(padded, kernel, mode="valid")[: len(x)]

    smooth = moving_average(rms_norm, 5)

    drops: list[float] = []
    for i in range(5, len(smooth) - 5):
        before = np.mean(smooth[i - 5:i])
        after = np.mean(smooth[i:i + 5])

        if before < 0.3 and (after - before) > 0.4:
            drops.append(float(frame_times[i]))

    filtered: list[float] = []
    for t in drops:
        if not filtered or (t - filtered[-1]) >= 1.5:
            filtered.append(round(t, 2))
    drops = filtered

    results = []
    for seg_start in range(0, int(total_duration), segment_duration):
        seg_end = min(seg_start + segment_duration, total_duration)
        mask = (frame_times >= float(seg_start)) & (frame_times < float(seg_end))
        segment_energy = smooth[mask]

        if len(segment_energy) == 0:
            continue

        avg_energy = float(np.mean(segment_energy))
        has_drop = any(float(seg_start) <= d < float(seg_end) for d in drops)

        if has_drop:
            label = "DROP 🔥"
        elif avg_energy < 0.15:
            label = "calm"
        elif avg_energy < 0.35:
            label = "chill"
        elif avg_energy < 0.55:
            label = "build"
        elif avg_energy < 0.75:
            label = "energetic"
        else:
            label = "intense"

        results.append(
            {
                "start": int(seg_start),
                "end": int(seg_end),
                "label": label,
            }
        )

    return results
