from __future__ import annotations

import json

import librosa
import numpy as np


TEMPOS = ["slow", "medium", "fast"]


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
