from __future__ import annotations

import librosa
import numpy as np


def classify_input(waveform, sr) -> dict:
    """Classify audio characteristics for full music analysis."""
    if sr is None or int(sr) <= 0:
        raise ValueError("sr must be a positive integer sample rate")

    audio = np.asarray(waveform, dtype=np.float32)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)

    if audio.size == 0:
        return {
            "type": "full_music",
            "confidence": 0.0,
            "features": {
                "flatness": 1.0,
                "onset_var": 1.0,
                "bandwidth": 0.0,
                "harmonic_ratio": 0.0,
                "score": 0.0,
            },
        }

    flatness = float(np.mean(librosa.feature.spectral_flatness(y=audio)))

    onset_env = librosa.onset.onset_strength(y=audio, sr=int(sr))
    onset_var = float(np.var(onset_env)) if onset_env.size else 0.0

    bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=int(sr))))

    harmonic, percussive = librosa.effects.hpss(audio)
    harmonic_energy = float(np.sum(np.square(harmonic, dtype=np.float32)))
    percussive_energy = float(np.sum(np.square(percussive, dtype=np.float32)))
    total_energy = harmonic_energy + percussive_energy
    harmonic_ratio = harmonic_energy / total_energy if total_energy > 1e-6 else 0.0

    score = 0.0
    if flatness < 0.08:
        score += 1.0
    if onset_var < 0.05:
        score += 1.0
    if bandwidth < 2000.0:
        score += 1.0
    if harmonic_ratio > 0.75:
        score += 1.0

    input_type = "full_music"

    return {
        "type": input_type,
        "confidence": float(score / 4.0),
        "features": {
            "flatness": flatness,
            "onset_var": onset_var,
            "bandwidth": bandwidth,
            "harmonic_ratio": harmonic_ratio,
            "score": score,
        },
    }
