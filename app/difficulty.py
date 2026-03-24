from __future__ import annotations


def detect_difficulty(bpm: float, chords: list, strum_pattern: str) -> str:
    score = 0

    # Tempo factor
    if bpm > 140:
        score += 2
    elif bpm > 110:
        score += 1

    # Chord complexity
    if len(set(chords)) > 5:
        score += 2
    elif len(set(chords)) > 3:
        score += 1

    # Rhythm complexity
    if "free" in strum_pattern:
        score += 2
    elif "moderate" in strum_pattern:
        score += 1

    if score <= 2:
        return "Beginner"
    elif score <= 4:
        return "Intermediate"
    else:
        return "Advanced"
