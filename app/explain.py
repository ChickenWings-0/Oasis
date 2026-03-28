from __future__ import annotations


def explain_song(
    bpm: float,
    key: str,
    scale: str,
    chords: list,
    strum_pattern: str,
    character: dict = None,
) -> str:
    explanation = []

    if bpm < 80:
        explanation.append("The track has a slow tempo, creating a relaxed and laid-back atmosphere.")
    elif bpm < 120:
        explanation.append("The tempo sits in a moderate range, making the track feel balanced and easy to follow.")
    else:
        explanation.append("The fast tempo gives the track a high-energy and dynamic feel.")

    explanation.append(f"It is composed in the key of {key} {scale}.")

    if chords:
        explanation.append(f"The harmonic structure includes chords like {', '.join(chords[:4])}, contributing to its musical character.")

    explanation.append(f"The strumming pattern is {strum_pattern}, which reflects the rhythmic consistency of the piece.")

    if character:
        explanation.append(
            f"The track feels {character.get('energy', 'balanced')} in energy, "
            f"{character.get('warmth', 'neutral')} in warmth, and "
            f"{character.get('brightness', 'balanced')} in brightness."
        )

    return " ".join(explanation)
