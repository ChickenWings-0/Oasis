from __future__ import annotations

import json
import re

import numpy as np

GUITAR_TAB_MAP = {
    "C": "x32010",
    "Cm": "x35543",
    "C7": "x32310",
    "C#": "x46664",
    "C#m": "x46654",
    "C#7": "x46464",
    "D": "xx0232",
    "Dm": "xx0231",
    "D7": "xx0212",
    "D#": "x68886",
    "D#m": "x68876",
    "D#7": "x68686",
    "E": "022100",
    "Em": "022000",
    "E7": "020100",
    "F": "133211",
    "Fm": "133111",
    "F7": "131211",
    "F#": "244322",
    "F#m": "244222",
    "F#7": "242322",
    "G": "320003",
    "Gm": "355333",
    "G7": "320001",
    "G#": "466544",
    "G#m": "466444",
    "G#7": "464544",
    "A": "x02220",
    "Am": "x02210",
    "A7": "x02020",
    "A#": "688766",
    "A#m": "688666",
    "A#7": "686766",
    "B": "x24442",
    "Bm": "x24432",
    "B7": "x21202",
    "Csus4": "x33011",
    "Dsus4": "xx0233",
    "Esus4": "022200",
    "Fsus4": "133311",
    "Gsus4": "330013",
    "Asus4": "x02230",
    "Cadd9": "x32030",
    "Dadd9": "xx0230",
    "Eadd9": "024100",
    "Fadd9": "133013",
    "Gadd9": "320203",
    "Aadd9": "x02420",
    "Cmaj7": "x32000",
    "Dm7": "xx0211",
    "Em7": "022030",
    "Fmaj7": "xx3210",
    "Am7": "x02010",
    "Bm7": "x24232",
}

GUITAR_VOICINGS_MAP = {
    "C": ["x32010", "x35553", "x3x553"],
    "Cm": ["x35543", "8-10-10-8-8-8", "x3x543"],
    "Cmaj7": ["x32000", "x35453", "x3x453"],
    "Cm7": ["x35343", "8-10-8-8-8-8", "x3x343"],
    "C7": ["x32310", "x35353", "x3x353"],
    "D": ["xx0232", "x57775", "x5x775"],
    "Dm": ["xx0231", "x57765", "x5x765"],
    "Dm7": ["xx0211", "x57565", "x5x565"],
    "D7": ["xx0212", "x54535", "x5x435"],
    "E": ["022100", "x79997", "x7x997"],
    "Em": ["022000", "x79987", "x7x987"],
    "Em7": ["022030", "x79787", "x7x787"],
    "E7": ["020100", "x76757", "x7x657"],
    "F": ["133211", "x8-10-10-10-8-x", "xx3211"],
    "Fm": ["133111", "x8-10-10-9-8-x", "xx3111"],
    "Fmaj7": ["xx3210", "x8-10-10-9-10-x", "1x2210"],
    "F7": ["131211", "x8-10-8-9-8-x", "xx3211"],
    "G": ["320003", "355433", "3x0003"],
    "Gm": ["355333", "x-10-12-12-11-10", "3x333x"],
    "G7": ["320001", "353433", "3x0001"],
    "A": ["x02220", "577655", "x0x655"],
    "Am": ["x02210", "577555", "x0x555"],
    "Am7": ["x02010", "575555", "x0x555"],
    "A7": ["x02020", "575655", "x0x655"],
    "B": ["x24442", "799877", "x2x877"],
    "Bm": ["x24432", "799777", "x2x777"],
    "Bm7": ["x24232", "797777", "x2x777"],
    "B7": ["x21202", "797877", "x2x877"],
}

POWER_CHORD_MAP = {
    "C": "x355xx",
    "C#": "x466xx",
    "D": "x577xx",
    "D#": "x688xx",
    "E": "022xxx",
    "F": "133xxx",
    "F#": "244xxx",
    "G": "355xxx",
    "G#": "466xxx",
    "A": "x022xx",
    "A#": "x133xx",
    "B": "x244xx",
}

NOTE_ALIAS = {
    "CB": "B",
    "DB": "C#",
    "EB": "D#",
    "FB": "E",
    "GB": "F#",
    "AB": "G#",
    "BB": "A#",
    "B#": "C",
    "E#": "F",
}

OPEN_CHORD_SET = {"C", "G", "D", "A", "E", "Am", "Em", "Dm"}
KEYBOARD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "dominant7": [0, 4, 7, 10],
}

MAJOR_DEGREES = ["I", "ii", "iii", "IV", "V", "vi", "vii\u00b0"]
MINOR_DEGREES = ["i", "ii\u00b0", "III", "iv", "v", "VI", "VII"]
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

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
    parsed_sequence: list[tuple[str, str, str]] = []
    for chord in chords:
        chord_label = str(chord).strip()
        root, quality = _parse_chord(chord_label)
        lookup_name = _build_lookup_name(root, quality)
        parsed_sequence.append((chord_label, root, lookup_name))

    capo_choice = _choose_progression_capo(parsed_sequence)
    tabs: list[dict[str, object]] = []

    prev_position = 0.0
    for chord_label, root, lookup_name in parsed_sequence:
        candidates = GUITAR_VOICINGS_MAP.get(lookup_name)
        if not candidates:
            single = GUITAR_TAB_MAP.get(lookup_name)
            candidates = [single] if single else []

        if candidates:
            tab = _pick_best_voicing(candidates, prev_position)
        else:
            tab = POWER_CHORD_MAP.get(root, "unknown")

        prev_position = _tab_position(tab)

        tabs.append(
            {
                "chord": chord_label,
                "tab": tab,
                "capo_suggestion": int(capo_choice),
            }
        )

    return tabs


def analyze_harmony(chords: list, key: str, scale: str) -> dict:
    degree_map = _build_degree_map(key=key, scale=scale)
    functions = []
    degree_sequence: list[str] = []

    for chord in chords:
        chord_label = str(chord).strip()
        root, _quality = _parse_chord(chord_label)
        degree = degree_map.get(root)
        degree_sequence.append(degree or "?")
        functions.append({
            "chord": chord_label,
            "function": _degree_to_function(degree),
        })

    progression_type = _detect_progression(degree_sequence)
    return {
        "functions": functions,
        "progression_type": progression_type,
    }


def generate_keyboard_notes(chords: list) -> list:
    note_names, _details = _generate_keyboard_notes_with_voice_leading(chords)
    return note_names


def _generate_keyboard_notes_with_voice_leading(chords: list) -> tuple[list[list[str]], list[dict[str, object]]]:
    keyboard_notes: list[list[str]] = []
    detailed: list[dict[str, object]] = []

    previous_voicing: list[int] | None = None

    for idx, chord_entry in enumerate(chords):
        if isinstance(chord_entry, dict):
            chord_label = str(chord_entry.get("chord", "")).strip()
            start = float(chord_entry.get("start", idx))
            end = float(chord_entry.get("end", idx + 1))
        else:
            chord_label = str(chord_entry).strip()
            start = float(idx)
            end = float(idx + 1)

        root, quality = _parse_chord(chord_label)
        voicing = _best_keyboard_voicing(root, quality, previous_voicing)
        previous_voicing = voicing

        names = [_midi_to_note_name(n) for n in voicing]
        keyboard_notes.append(names)
        detailed.append(
            {
                "notes": [int(n) for n in voicing],
                "start": float(start),
                "end": float(end),
            }
        )

    return keyboard_notes, detailed


def generate_tabs_data(chords: list) -> dict:
    keyboard_notes, keyboard_notes_detailed = _generate_keyboard_notes_with_voice_leading(chords)
    return {
        "guitar_tabs": generate_guitar_tabs(chords),
        "keyboard_notes": keyboard_notes,
        "keyboard_notes_detailed": keyboard_notes_detailed,
    }


def _parse_chord(chord: str) -> tuple[str, str]:
    text = re.sub(r"\s+", "", str(chord).strip())
    if not text:
        return "C", "major"

    match = re.match(r"^([A-Ga-g])([#b]?)(.*)$", text)
    if not match:
        return "C", "major"

    root_base = match.group(1).upper()
    accidental = match.group(2)
    suffix = match.group(3).lower()

    root = _normalize_note(f"{root_base}{accidental}")

    if "maj7" in suffix:
        quality = "major7"
    elif "min7" in suffix or ("m7" in suffix and "maj7" not in suffix):
        quality = "minor7"
    elif suffix in {"7", "dom7", "dominant7", "dominant"} or ("7" in suffix and "maj7" not in suffix and "m7" not in suffix):
        quality = "dominant7"
    elif "sus" in suffix:
        quality = "sus"
    elif "add" in suffix:
        quality = "add"
    elif suffix.startswith("min") or (suffix.startswith("m") and not suffix.startswith("maj")):
        quality = "minor"
    else:
        quality = "major"

    return root, quality


def _normalize_note(note: str) -> str:
    cleaned = str(note).strip()
    if not cleaned:
        return "C"

    base = cleaned[0].upper()
    accidental = ""
    if len(cleaned) > 1 and cleaned[1] in {"#", "b", "B"}:
        accidental = "b" if cleaned[1] in {"b", "B"} else "#"
    normalized = f"{base}{accidental}"
    return NOTE_ALIAS.get(normalized.upper(), normalized.upper())


def _build_lookup_name(root: str, quality: str) -> str:
    if quality == "minor":
        return f"{root}m"
    if quality == "minor7":
        return f"{root}m7"
    if quality == "major7":
        return f"{root}maj7"
    if quality == "dominant7":
        return f"{root}7"
    if quality == "sus":
        return f"{root}sus4"
    if quality == "add":
        return f"{root}add9"
    return root


def _pick_best_voicing(candidates: list[str], previous_position: float) -> str:
    return min(candidates, key=lambda tab: abs(_tab_position(tab) - previous_position))


def _tab_position(tab: str) -> float:
    digits = [int(ch) for ch in str(tab) if ch.isdigit()]
    positive = [d for d in digits if d > 0]
    if not positive:
        return 0.0
    return float(min(positive))


def _choose_progression_capo(parsed_sequence: list[tuple[str, str, str]]) -> int:
    best_capo = 0
    best_score = -1

    for capo in range(0, 8):
        score = 0
        for _chord_label, root, lookup_name in parsed_sequence:
            transposed_root = _transpose_root_down(root, capo)
            suffix = _extract_quality_suffix(lookup_name)
            transposed_lookup = f"{transposed_root}{suffix}"
            if transposed_lookup in OPEN_CHORD_SET:
                score += 1

        if score > best_score:
            best_score = score
            best_capo = capo

    return int(best_capo)


def _extract_quality_suffix(lookup_name: str) -> str:
    if len(lookup_name) >= 2 and lookup_name[1] in {"#", "b"}:
        return lookup_name[2:]
    return lookup_name[1:]


def _transpose_root_down(root: str, semitones: int) -> str:
    if root not in NOTE_NAMES:
        return root
    idx = NOTE_NAMES.index(root)
    return NOTE_NAMES[(idx - int(semitones)) % 12]


def _build_degree_map(key: str, scale: str) -> dict[str, str]:
    key_root = _normalize_note(str(key).strip())
    if key_root not in NOTE_NAMES:
        key_root = "C"

    key_index = NOTE_NAMES.index(key_root)
    mode = str(scale).strip().lower()

    if mode == "minor":
        intervals = [0, 2, 3, 5, 7, 8, 10]
        labels = MINOR_DEGREES
    else:
        intervals = [0, 2, 4, 5, 7, 9, 11]
        labels = MAJOR_DEGREES

    mapping: dict[str, str] = {}
    for interval, label in zip(intervals, labels):
        note = NOTE_NAMES[(key_index + interval) % 12]
        mapping[note] = label
    return mapping


def _best_keyboard_voicing(root: str, quality: str, previous_voicing: list[int] | None) -> list[int]:
    intervals = KEYBOARD_INTERVALS.get(quality, KEYBOARD_INTERVALS["major"])

    root_pc = _note_name_to_pitch_class(root)
    root_candidates = _root_midi_candidates(root_pc, low=48, high=72)

    candidates: list[list[int]] = []
    for root_midi in root_candidates:
        for inv in _all_inversion_offsets(intervals):
            voicing = [int(root_midi + off) for off in inv]
            voicing = _fit_voicing_to_range(voicing, low=48, high=72)
            voicing = [int(np.clip(n, 48, 72)) for n in voicing]
            candidates.append(voicing)

    if not candidates:
        fallback = [60, 64, 67]
        return fallback

    if previous_voicing is None:
        return min(candidates, key=lambda v: abs(float(np.mean(v)) - 60.0))

    return min(candidates, key=lambda v: _voice_leading_cost(v, previous_voicing))


def _all_inversion_offsets(intervals: list[int]) -> list[list[int]]:
    out: list[list[int]] = []
    n = len(intervals)
    for i in range(n):
        rotated = intervals[i:] + [x + 12 for x in intervals[:i]]
        out.append([int(x) for x in rotated])
    return out


def _root_midi_candidates(root_pc: int, low: int = 48, high: int = 72) -> list[int]:
    candidates: list[int] = []
    for midi in range(int(low), int(high) + 1):
        if midi % 12 == int(root_pc):
            candidates.append(midi)
    return candidates


def _fit_voicing_to_range(notes: list[int], low: int = 48, high: int = 72) -> list[int]:
    fitted = [int(n) for n in notes]
    if not fitted:
        return fitted

    while min(fitted) < int(low):
        fitted = [n + 12 for n in fitted]
    while max(fitted) > int(high):
        fitted = [n - 12 for n in fitted]

    return fitted


def _voice_leading_cost(current: list[int], previous: list[int]) -> float:
    curr_sorted = sorted(int(n) for n in current)
    prev_sorted = sorted(int(n) for n in previous)

    pair_count = min(len(curr_sorted), len(prev_sorted))
    movement = float(sum(abs(curr_sorted[i] - prev_sorted[i]) for i in range(pair_count)))

    curr_pcs = {n % 12 for n in curr_sorted}
    prev_pcs = {n % 12 for n in prev_sorted}
    common_tones = len(curr_pcs.intersection(prev_pcs))

    return movement - (5.0 * common_tones)


def _midi_to_note_name(midi_note: int) -> str:
    note = int(np.clip(int(midi_note), 0, 127))
    pc = note % 12
    octave = (note // 12) - 1
    return f"{NOTE_NAMES[pc]}{octave}"


def _note_name_to_pitch_class(note_name: str) -> int:
    normalized = _normalize_note(note_name)
    if normalized in NOTE_NAMES:
        return NOTE_NAMES.index(normalized)
    return 0


def _degree_to_function(degree: str | None) -> str:
    if not degree:
        return "other"

    tonic = {"I", "i", "vi", "VI"}
    subdominant = {"ii", "ii\u00b0", "IV", "iv"}
    dominant = {"V", "v", "vii\u00b0", "VII"}

    if degree in tonic:
        return "tonic"
    if degree in subdominant:
        return "subdominant"
    if degree in dominant:
        return "dominant"
    return "other"


def _canonical_degree(degree: str) -> str:
    return str(degree).replace("\u00b0", "").lower()


def _contains_progression(sequence: list[str], pattern: list[str]) -> bool:
    if len(sequence) < len(pattern):
        return False

    for i in range(0, len(sequence) - len(pattern) + 1):
        if sequence[i:i + len(pattern)] == pattern:
            return True
    return False


def _detect_progression(degrees: list[str]) -> str:
    canonical = [_canonical_degree(d) for d in degrees if d and d != "?"]
    if _contains_progression(canonical, ["i", "v", "vi", "iv"]):
        return "pop progression"
    if _contains_progression(canonical, ["vi", "iv", "i", "v"]):
        return "pop progression"
    if _contains_progression(canonical, ["i", "iv", "v"]):
        return "basic progression"
    if _contains_progression(canonical, ["ii", "v", "i"]):
        return "jazz progression"
    return "unknown"


def main() -> None:
    test_chords = ["C", "G", "Am", "F"]
    result = generate_tabs_data(test_chords)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
