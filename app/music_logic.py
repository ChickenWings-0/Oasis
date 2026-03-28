from __future__ import annotations

import json

import librosa
import numpy as np


TEMPOS = ["slow", "medium", "fast"]


def analyze_metadata(chords: list, bpm: int | None, rhythm_style: str) -> dict:
    """Create stable, explainable metadata from harmony, tempo, and rhythm style."""
    if not chords:
        return {
            "genre": "unknown",
            "mood": "unknown",
            "difficulty": "unknown",
            "tempo_type": "unknown",
            "confidence": 0.0,
        }

    normalized_chords = [str(c).strip().upper() for c in chords if str(c).strip()]
    if not normalized_chords:
        return {
            "genre": "unknown",
            "mood": "unknown",
            "difficulty": "unknown",
            "tempo_type": "unknown",
            "confidence": 0.0,
        }

    total_chords = len(normalized_chords)
    unique_chords = len(set(normalized_chords))

    lower_chords = [c.lower() for c in normalized_chords]
    minor_count = sum(1 for c in lower_chords if "m" in c and "maj" not in c)
    major_count = total_chords - minor_count
    seventh_count = sum(1 for c in lower_chords if "7" in c)

    minor_ratio = minor_count / total_chords
    major_ratio = major_count / total_chords
    chord_complexity = sum(1 for c in lower_chords if "7" in c or "dim" in c)

    if bpm is None:
        tempo_type = "unknown"
    elif bpm < 80:
        tempo_type = "slow"
    elif bpm <= 120:
        tempo_type = "medium"
    else:
        tempo_type = "fast"

    style = str(rhythm_style).strip().lower()

    if bpm is None and style == "steady":
        genre = "ambient"
    elif bpm is not None and bpm < 90 and minor_ratio > 0.5:
        genre = "lofi"
    elif bpm is not None and 90 <= bpm <= 130 and style in ["metronomic", "steady"]:
        genre = "pop"
    elif bpm is not None and bpm > 120 and style == "syncopated":
        genre = "trap"
    elif style == "free":
        genre = "ambient"
    else:
        genre = "unknown"

    if minor_ratio > 0.65:
        mood = "sad"
    elif major_ratio > 0.65:
        mood = "happy"
    elif bpm is not None and bpm > 120:
        mood = "energetic"
    elif style == "free":
        mood = "calm"
    else:
        mood = "neutral"

    score = 0
    if bpm is not None and bpm > 120:
        score += 1
    if unique_chords > 4:
        score += 1
    if chord_complexity > 0:
        score += 1
    if style == "syncopated":
        score += 1

    if score <= 1:
        difficulty = "easy"
    elif score == 2:
        difficulty = "medium"
    else:
        difficulty = "hard"

    confidence = 0.5
    if bpm is not None:
        confidence += 0.2
    if total_chords > 4:
        confidence += 0.2
    if style != "unknown":
        confidence += 0.1
    confidence = min(1.0, confidence)

    _ = seventh_count

    return {
        "genre": genre,
        "mood": mood,
        "difficulty": difficulty,
        "tempo_type": tempo_type,
        "confidence": confidence,
    }


def analyze_audio_character(path: str) -> dict[str, str]:
    y, sr = librosa.load(path, sr=None, mono=True)

    energy_level = float(np.mean(librosa.feature.rms(y=y)))
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    zero_crossing = float(np.mean(librosa.feature.zero_crossing_rate(y=y)))

    # Additional features
    spectral_flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo)

    softness = "high" if centroid < 1200 else "medium" if centroid < 2500 else "low"
    brightness = "dark" if centroid < 1000 else "balanced" if centroid < 2500 else "bright"
    energy = "low" if energy_level < 0.03 else "medium" if energy_level < 0.08 else "high"
    warmth = "warm" if centroid < 1500 else "neutral" if centroid < 2800 else "cold"
    density = "sparse" if zero_crossing < 0.05 else "medium" if zero_crossing < 0.12 else "dense"
    aggressiveness = "low" if (energy_level < 0.04 and tempo < 100) else "medium" if (energy_level < 0.08 and tempo < 130) else "high"

    # Dynamics (variation in loudness)
    dynamic_range = float(np.std(librosa.feature.rms(y=y)))
    dynamics = "low" if dynamic_range < 0.01 else "medium" if dynamic_range < 0.03 else "high"

    # Harmonic richness
    harmonic_richness = "low" if spectral_flatness > 0.5 else "medium" if spectral_flatness > 0.2 else "high"

    # Ambience (proxy via spectral spread)
    ambience = "dry" if bandwidth < 1500 else "moderate" if bandwidth < 3000 else "spacious"

    # Groove tightness (based on onset consistency)
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    groove = "tight" if len(onsets) > 50 else "loose"

    return {
        "softness": softness,
        "brightness": brightness,
        "energy": energy,
        "warmth": warmth,
        "density": density,
        "aggressiveness": aggressiveness,
        "dynamics": dynamics,
        "harmonic_richness": harmonic_richness,
        "ambience": ambience,
        "groove": groove,
    }


def build_music_dna(path: str, bpm: float, chords: list) -> dict:
    from app.energy import analyze_energy_profile

    metadata = build_music_metadata(path=path, prompt="", bpm=bpm)
    character = analyze_audio_character(path)
    energy = analyze_energy_profile(path)

    return {
        "metadata": metadata,
        "character": character,
        "energy": energy,
        "bpm": bpm,
        "chords": chords,
    }


def build_music_metadata(path: str, prompt: str, bpm: float) -> dict:
    _ = prompt
    y, sr = librosa.load(path, sr=None, mono=True)

    # Energy (loudness)
    rms = np.mean(librosa.feature.rms(y=y))

    # Brightness
    centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))

    if bpm < 60 and rms < 0.04:
        mood = "ambient"
    elif bpm < 70:
        mood = "calm"
    elif bpm < 85:
        mood = "relaxed"
    elif bpm < 100:
        mood = "chill"
    elif bpm < 115:
        mood = "groovy"
    elif bpm < 130:
        mood = "energetic"
    elif bpm < 145:
        mood = "uplifting"
    elif bpm < 160:
        mood = "intense"
    elif bpm < 180:
        mood = "aggressive"
    else:
        mood = "chaotic"

    if centroid < 1200:
        if bpm < 80:
            genre = "ambient"
        elif bpm < 110:
            genre = "lofi"
        else:
            genre = "chillhop"
    elif centroid < 2000:
        if bpm < 90:
            genre = "acoustic"
        elif bpm < 120:
            genre = "pop"
        elif bpm < 140:
            genre = "indie"
        else:
            genre = "dance"
    elif centroid < 3000:
        if bpm < 100:
            genre = "jazz"
        elif bpm < 130:
            genre = "rock"
        elif bpm < 150:
            genre = "funk"
        else:
            genre = "disco"
    else:
        if bpm < 120:
            genre = "electronic"
        elif bpm < 140:
            genre = "edm"
        elif bpm < 160:
            genre = "techno"
        elif bpm < 180:
            genre = "trance"
        else:
            genre = "hardcore"

    if bpm < 80:
        tempo = TEMPOS[0]
    elif bpm < 130:
        tempo = TEMPOS[1]
    else:
        tempo = TEMPOS[2]

    return {
        "mood": mood,
        "tempo": tempo,
        "genre": genre,
    }


def classify_chords(chords: list) -> dict:
    major = []
    minor = []

    for chord in chords:
        chord_name = str(chord).strip()
        if not chord_name:
            continue
        if chord_name.endswith("m"):
            minor.append(chord_name)
        else:
            major.append(chord_name)

    return {
        "major": major,
        "minor": minor,
    }


def generate_bassline(chords: list) -> list:
    bassline = []

    for chord in chords:
        chord_name = str(chord).strip()
        if not chord_name:
            continue

        root = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in ["#", "b"]:
            root = chord_name[:2]

        bassline.extend([root, root])

    return bassline


def enrich_metadata_with_analysis(path: str, prompt: str, chords: list, bpm: float) -> dict:
    metadata = build_music_metadata(path=path, prompt=prompt, bpm=bpm)
    chord_groups = classify_chords(chords)
    bassline = generate_bassline(chords)

    return {
        "metadata": metadata,
        "chords": chord_groups,
        "bassline": bassline,
    }


def main() -> None:
    test_prompt = "chill lofi track with piano, guitar, bass and soft drums"
    test_chords = ["C", "G", "Am", "F"]

    result = enrich_metadata_with_analysis(test_prompt, test_chords)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
