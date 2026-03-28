from __future__ import annotations

from dataclasses import dataclass

import numpy as np


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_SCALE = np.array([0, 2, 4, 5, 7, 9, 11], dtype=int)
MINOR_SCALE = np.array([0, 2, 3, 5, 7, 8, 10], dtype=int)

# Diatonic triad qualities by scale degree.
MAJOR_QUALITIES = ["maj", "min", "min", "maj", "maj", "min", "dim"]
MINOR_QUALITIES = ["min", "dim", "maj", "min", "min", "maj", "maj"]

TRIAD_INTERVALS = {
    "maj": np.array([0, 4, 7], dtype=int),
    "min": np.array([0, 3, 7], dtype=int),
    "dim": np.array([0, 3, 6], dtype=int),
}


@dataclass
class _MelodyEvent:
    midi: int
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class _DiatonicChord:
    degree: int
    name: str
    root_pc: int
    quality: str
    pitch_classes: set[int]
    notes_midi: list[int]


class ChordGenerator:
    """Generate simple diatonic chord progressions from melody and key context."""

    def __init__(self, default_bpm: float = 120.0, base_octave: int = 4) -> None:
        self.default_bpm = float(default_bpm)
        self.base_octave = int(base_octave)
        self._progression_templates: dict[str, list[list[int]]] = {
            "pop": [[1, 5, 6, 4], [6, 4, 1, 5]],
            "lofi": [[2, 5, 1, 6], [1, 6, 2, 5]],
            "trap": [[1, 7, 6, 4]],
        }

    def generate(self, note_events: list[dict], key: str, scale: str, genre: str = "pop") -> list[dict[str, object]]:
        events = self._normalize_events(note_events)
        if not events:
            return []

        key_root = self._note_name_to_pitch_class(key)
        mode = "major" if str(scale).lower() != "minor" else "minor"

        chords = self._build_diatonic_chords(key_root, mode)
        tonic_degree = 1
        dominant_degree = 5
        genre_key = str(genre).strip().lower()
        templates = self._progression_templates.get(genre_key, self._progression_templates["pop"])
        template = templates[0]

        bar_duration = self._estimate_bar_duration(events)
        total_time = max(ev.end for ev in events)
        bar_count = max(1, int(np.ceil(total_time / bar_duration)))

        progression: list[dict[str, object]] = []
        chosen_degrees: list[int] = []

        for bar_idx in range(bar_count):
            bar_start = bar_idx * bar_duration
            bar_end = (bar_idx + 1) * bar_duration
            bar_events = self._events_overlapping_range(events, bar_start, bar_end)

            best_chord = None
            best_score = -1e18
            for chord in chords:
                score = self._score_chord_for_bar(chord, bar_events, bar_start, bar_duration)
                score += self._progression_adjustment(
                    chord_degree=chord.degree,
                    bar_index=bar_idx,
                    previous_degrees=chosen_degrees,
                    tonic_degree=tonic_degree,
                    dominant_degree=dominant_degree,
                )
                score += self._template_progression_bonus(
                    chord_degree=chord.degree,
                    bar_index=bar_idx,
                    template=template,
                )

                if score > best_score:
                    best_score = score
                    best_chord = chord

            if best_chord is None:
                best_chord = chords[0]

            chosen_degrees.append(best_chord.degree)
            progression.append(
                {
                    "chord": best_chord.name,
                    "start": round(float(bar_start), 4),
                    "end": round(float(bar_end), 4),
                    "notes": [int(n) for n in best_chord.notes_midi],
                }
            )

        return progression

    def _normalize_events(self, events: list[dict]) -> list[_MelodyEvent]:
        normalized: list[_MelodyEvent] = []
        for event in events:
            if "midi" not in event:
                continue

            start_raw = event.get("start", event.get("start_sec"))
            end_raw = event.get("end", event.get("end_sec"))
            if start_raw is None or end_raw is None:
                continue

            try:
                midi = int(round(float(event["midi"])))
                start = float(start_raw)
                end = float(end_raw)
            except (TypeError, ValueError):
                continue

            if not np.isfinite(start) or not np.isfinite(end):
                continue

            if end < start:
                start, end = end, start

            if end <= start:
                continue

            normalized.append(_MelodyEvent(midi=midi, start=start, end=end))

        normalized.sort(key=lambda e: (e.start, e.end, e.midi))
        return normalized

    def _note_name_to_pitch_class(self, key: str) -> int:
        norm = str(key).strip().upper().replace("B#", "C").replace("E#", "F")

        alias = {
            "DB": "C#",
            "EB": "D#",
            "GB": "F#",
            "AB": "G#",
            "BB": "A#",
            "CB": "B",
            "FB": "E",
        }
        if norm in alias:
            norm = alias[norm]

        if norm not in NOTE_NAMES:
            return 0

        return NOTE_NAMES.index(norm)

    def _build_diatonic_chords(self, key_root: int, mode: str) -> list[_DiatonicChord]:
        scale_intervals = MAJOR_SCALE if mode == "major" else MINOR_SCALE
        qualities = MAJOR_QUALITIES if mode == "major" else MINOR_QUALITIES

        chords: list[_DiatonicChord] = []
        for i, (interval, quality) in enumerate(zip(scale_intervals, qualities), start=1):
            root_pc = int((key_root + interval) % 12)
            triad_ints = TRIAD_INTERVALS[quality]
            pcs = {(root_pc + int(x)) % 12 for x in triad_ints}

            root_name = NOTE_NAMES[root_pc]
            if quality == "maj":
                name = root_name
            elif quality == "min":
                name = f"{root_name}m"
            else:
                name = f"{root_name}dim"

            root_midi = root_pc + 12 * max(0, self.base_octave)
            chord_notes = [root_midi + int(x) for x in triad_ints]

            chords.append(
                _DiatonicChord(
                    degree=i,
                    name=name,
                    root_pc=root_pc,
                    quality=quality,
                    pitch_classes=pcs,
                    notes_midi=chord_notes,
                )
            )

        return chords

    def _estimate_bar_duration(self, events: list[_MelodyEvent]) -> float:
        if len(events) < 2:
            beat_sec = 60.0 / self.default_bpm
            return 4.0 * beat_sec

        onsets = np.array([ev.start for ev in events], dtype=np.float64)
        iois = np.diff(onsets)
        iois = iois[np.isfinite(iois) & (iois > 1e-4)]

        if iois.size == 0:
            beat_sec = 60.0 / self.default_bpm
            return 4.0 * beat_sec

        median_ioi = float(np.median(iois))
        estimated_bpm = 60.0 / max(median_ioi, 1e-4)
        estimated_bpm = float(np.clip(estimated_bpm, 60.0, 180.0))
        beat_sec = 60.0 / estimated_bpm

        return max(0.5, 4.0 * beat_sec)

    def _events_overlapping_range(self, events: list[_MelodyEvent], start: float, end: float) -> list[_MelodyEvent]:
        return [ev for ev in events if ev.end > start and ev.start < end]

    def _score_chord_for_bar(
        self,
        chord: _DiatonicChord,
        bar_events: list[_MelodyEvent],
        bar_start: float,
        bar_duration: float,
    ) -> float:
        if not bar_events:
            return 0.0

        score = 0.0
        safe_bar_duration = max(1e-6, float(bar_duration))
        beat_weights = {0: 3.0, 1: 1.0, 2: 2.0, 3: 1.0}

        for ev in bar_events:
            dur = max(ev.duration, 1e-4)
            pc = ev.midi % 12

            position = (float(ev.start) - float(bar_start)) / safe_bar_duration
            position = float(np.clip(position, 0.0, 0.999999))
            beat_index = int(position * 4) % 4

            weight = float(beat_weights.get(beat_index, 1.0))
            weighted_duration = weight * dur

            if pc in chord.pitch_classes:
                score += 2.0 * weighted_duration
            else:
                score -= 0.2 * weighted_duration

            # Penalize semitone clashes against any chord tone.
            min_dist = min(min((pc - cp) % 12, (cp - pc) % 12) for cp in chord.pitch_classes)
            if min_dist == 1:
                if beat_index in {0, 2}:
                    score -= 3.0 * weighted_duration
                else:
                    score -= 1.2 * weighted_duration

        return score

    def _template_progression_bonus(self, chord_degree: int, bar_index: int, template: list[int]) -> float:
        if not template:
            return 0.0
        template_degree = int(template[bar_index % len(template)])
        if chord_degree == template_degree:
            return 4.0
        return 0.0

    def _progression_adjustment(
        self,
        chord_degree: int,
        bar_index: int,
        previous_degrees: list[int],
        tonic_degree: int,
        dominant_degree: int,
    ) -> float:
        score = 0.0

        # Prefer tonic at start.
        if bar_index == 0:
            if chord_degree == tonic_degree:
                score += 3.0
            elif chord_degree == dominant_degree:
                score += 0.8

        prev = previous_degrees[-1] if previous_degrees else None

        # Prefer dominant before tonic and tonic after dominant.
        if prev == dominant_degree and chord_degree == tonic_degree:
            score += 2.0
        if prev == tonic_degree and chord_degree == dominant_degree:
            score += 1.0

        # Discourage long repeats of the same chord (>3 bars).
        if len(previous_degrees) >= 3 and all(d == previous_degrees[-1] for d in previous_degrees[-3:]):
            if chord_degree == previous_degrees[-1]:
                score -= 5.0

        return score
