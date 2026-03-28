from __future__ import annotations

import re

import numpy as np


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NAME_TO_PC = {name: i for i, name in enumerate(NOTE_NAMES)}


class BassGenerator:
    """Generate simple basslines from chord progressions."""

    def __init__(self, min_midi: int = 36, max_midi: int = 60, default_velocity: int = 95) -> None:
        self.min_midi = int(min_midi)
        self.max_midi = int(max_midi)
        self.default_velocity = int(default_velocity)

    def generate(self, chords: list[dict]) -> list[dict[str, int | float]]:
        """Return bass MIDI note events synced to chord timing.

        Input chord shape expected:
        [{"chord": "Cm", "start": float, "end": float, "notes": [midi, ...]}]

        Output shape:
        [{"note": int, "start": float, "end": float, "velocity": int}]
        """
        bass_events: list[dict[str, int | float]] = []

        for idx, chord in enumerate(chords):
            start_raw = chord.get("start", chord.get("start_sec"))
            end_raw = chord.get("end", chord.get("end_sec"))
            if start_raw is None or end_raw is None:
                continue

            try:
                start = float(start_raw)
                end = float(end_raw)
            except (TypeError, ValueError):
                continue

            if not np.isfinite(start) or not np.isfinite(end):
                continue
            if end <= start:
                continue

            duration = end - start
            beat_len = duration / 4.0
            note_len = max(0.05, beat_len * 0.9)

            root_midi = self._extract_root_midi(chord)
            root_midi = self._fit_to_range(root_midi)
            fifth_midi = self._fit_to_range(root_midi + 7)

            # Root on beat 1
            bass_events.append(
                {
                    "note": int(root_midi),
                    "start": round(float(start), 4),
                    "end": round(float(min(end, start + note_len)), 4),
                    "velocity": int(self.default_velocity),
                }
            )

            # Fifth on beat 3
            fifth_start = start + 2.0 * beat_len
            if fifth_start < end:
                bass_events.append(
                    {
                        "note": int(fifth_midi),
                        "start": round(float(fifth_start), 4),
                        "end": round(float(min(end, fifth_start + note_len)), 4),
                        "velocity": int(max(1, self.default_velocity - 5)),
                    }
                )

            # Optional octave variation on beat 4 for every other chord.
            if idx % 2 == 1:
                octave_start = start + 3.0 * beat_len
                octave_note = self._fit_to_range(root_midi + 12)
                if octave_start < end:
                    bass_events.append(
                        {
                            "note": int(octave_note),
                            "start": round(float(octave_start), 4),
                            "end": round(float(min(end, octave_start + note_len * 0.8)), 4),
                            "velocity": int(max(1, self.default_velocity - 8)),
                        }
                    )

        bass_events.sort(key=lambda e: (float(e["start"]), int(e["note"])))
        return bass_events

    def _extract_root_midi(self, chord: dict) -> int:
        notes = chord.get("notes")
        if isinstance(notes, list) and notes:
            midi_values = [int(round(float(n))) for n in notes if self._is_number(n)]
            if midi_values:
                root = min(midi_values)
                return self._fit_to_range(root)

        name = str(chord.get("chord", "C"))
        pc = self._parse_chord_root_pitch_class(name)
        if pc is None:
            pc = 0

        # Start from C3-octave region and fit into requested range.
        base = 48 + int(pc)
        return self._fit_to_range(base)

    def _parse_chord_root_pitch_class(self, chord_name: str) -> int | None:
        text = chord_name.strip()
        if not text:
            return None

        match = re.match(r"^([A-Ga-g])([#b]?)", text)
        if not match:
            return None

        letter = match.group(1).upper()
        accidental = match.group(2)
        token = letter + accidental

        flat_alias = {
            "Db": "C#",
            "Eb": "D#",
            "Gb": "F#",
            "Ab": "G#",
            "Bb": "A#",
            "Cb": "B",
            "Fb": "E",
        }

        if token in flat_alias:
            token = flat_alias[token]

        if token not in NAME_TO_PC:
            return None

        return int(NAME_TO_PC[token])

    def _fit_to_range(self, midi_note: int) -> int:
        note = int(round(float(midi_note)))

        while note < self.min_midi:
            note += 12
        while note > self.max_midi:
            note -= 12

        note = int(np.clip(note, self.min_midi, self.max_midi))
        return note

    @staticmethod
    def _is_number(value: object) -> bool:
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False
