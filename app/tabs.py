from __future__ import annotations

import json

GUITAR_TAB_MAP = {
    "C": "x32010",
    "Cm": "x35543",
    "C#": "x46664",
    "C#m": "x46654",
    "D": "xx0232",
    "Dm": "xx0231",
    "D#": "x68886",
    "D#m": "x68876",
    "E": "022100",
    "Em": "022000",
    "F": "133211",
    "Fm": "133111",
    "F#": "244322",
    "F#m": "244222",
    "G": "320003",
    "Gm": "355333",
    "G#": "466544",
    "G#m": "466444",
    "A": "x02220",
    "Am": "x02210",
    "A#": "688766",
    "A#m": "688666",
    "B": "x24442",
    "Bm": "x24432",
}

KEYBOARD_NOTE_MAP = {
    "C": ["C", "E", "G"],
    "Cm": ["C", "D#", "G"],
    "C#": ["C#", "F", "G#"],
    "C#m": ["C#", "E", "G#"],
    "D": ["D", "F#", "A"],
    "Dm": ["D", "F", "A"],
    "D#": ["D#", "G", "A#"],
    "D#m": ["D#", "F#", "A#"],
    "E": ["E", "G#", "B"],
    "Em": ["E", "G", "B"],
    "F": ["F", "A", "C"],
    "Fm": ["F", "G#", "C"],
    "F#": ["F#", "A#", "C#"],
    "F#m": ["F#", "A", "C#"],
    "G": ["G", "B", "D"],
    "Gm": ["G", "A#", "D"],
    "G#": ["G#", "C", "D#"],
    "G#m": ["G#", "B", "D#"],
    "A": ["A", "C#", "E"],
    "Am": ["A", "C", "E"],
    "A#": ["A#", "D", "F"],
    "A#m": ["A#", "C#", "F"],
    "B": ["B", "D#", "F#"],
    "Bm": ["B", "D", "F#"],
}


def generate_guitar_tabs(chords: list) -> list:
    tabs = []
    for chord in chords:
        chord_name = str(chord).strip().replace("maj", "").replace("min", "m")
        tabs.append(GUITAR_TAB_MAP.get(chord_name, "unknown"))
    return tabs


def generate_keyboard_notes(chords: list) -> list:
    notes = []
    for chord in chords:
        chord_name = str(chord).strip().replace("maj", "").replace("min", "m")
        notes.append(KEYBOARD_NOTE_MAP.get(chord_name, []))
    return notes


def generate_tabs_data(chords: list) -> dict:
    return {
        "guitar_tabs": generate_guitar_tabs(chords),
        "keyboard_notes": generate_keyboard_notes(chords),
    }


def main() -> None:
    test_chords = ["C", "G", "Am", "F"]
    result = generate_tabs_data(test_chords)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
