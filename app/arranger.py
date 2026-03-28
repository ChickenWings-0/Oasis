from __future__ import annotations

import pretty_midi


class Arranger:
    """Combine melody, chord, bass, and drum events into a multi-track MIDI."""

    NOTE_END_GAP_SEC = 0.005

    def arrange(
        self,
        note_events: list[dict],
        chord_progression: list[dict],
        bass_events: list[dict],
        drum_events: list[dict],
        bpm: float,
    ) -> pretty_midi.PrettyMIDI:
        bpm_val = float(bpm)
        if bpm_val <= 0:
            raise ValueError("bpm must be > 0")

        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm_val)

        melody_inst = pretty_midi.Instrument(program=81, name="Melody")
        chords_inst = pretty_midi.Instrument(program=0, name="Chords")
        bass_inst = pretty_midi.Instrument(program=33, name="Bass")
        drums_inst = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")

        self._add_melody_notes(melody_inst, note_events)
        self._add_chord_notes(chords_inst, chord_progression)
        self._add_bass_notes(bass_inst, bass_events)
        self._add_drum_notes(drums_inst, drum_events, bpm_val)

        midi.instruments.extend([melody_inst, chords_inst, bass_inst, drums_inst])
        return midi

    def _add_melody_notes(self, instrument: pretty_midi.Instrument, events: list[dict]) -> None:
        for event in events:
            midi_note = self._safe_int(event.get("midi"))
            start = self._safe_float(event.get("start", event.get("start_sec")))
            end = self._safe_float(event.get("end", event.get("end_sec")))
            if midi_note is None or start is None or end is None:
                continue
            if end <= start:
                continue

            end = self._apply_note_end_gap(start, end)

            velocity = self._bounded_velocity(event.get("velocity"), default=100)
            instrument.notes.append(
                pretty_midi.Note(
                    velocity=velocity,
                    pitch=max(0, min(127, midi_note)),
                    start=max(0.0, start),
                    end=max(0.0, end),
                )
            )

    def _add_chord_notes(self, instrument: pretty_midi.Instrument, chords: list[dict]) -> None:
        for chord in chords:
            start = self._safe_float(chord.get("start", chord.get("start_sec")))
            end = self._safe_float(chord.get("end", chord.get("end_sec")))
            notes = chord.get("notes", [])
            if start is None or end is None or end <= start:
                continue
            if not isinstance(notes, list):
                continue

            duration = end - start
            pulse_len = duration / 4.0
            if pulse_len <= 0.0:
                continue

            for note in notes:
                midi_note = self._safe_int(note)
                if midi_note is None:
                    continue

                base_velocity = self._bounded_velocity(chord.get("velocity"), default=90)
                for i in range(4):
                    pulse_start = start + i * pulse_len
                    pulse_end = pulse_start + pulse_len * 0.8
                    if pulse_start >= end:
                        continue
                    pulse_end = min(pulse_end, end)
                    pulse_end = self._apply_note_end_gap(pulse_start, pulse_end)

                    # Downbeats stronger than offbeats for rhythmic chord motion.
                    velocity = base_velocity + (8 if i % 2 == 0 else -6)
                    velocity = self._bounded_velocity(velocity, default=base_velocity)

                    instrument.notes.append(
                        pretty_midi.Note(
                            velocity=velocity,
                            pitch=max(0, min(127, midi_note)),
                            start=max(0.0, pulse_start),
                            end=max(0.0, pulse_end),
                        )
                    )

    def _add_bass_notes(self, instrument: pretty_midi.Instrument, events: list[dict]) -> None:
        for event in events:
            midi_note = self._safe_int(event.get("note", event.get("midi")))
            start = self._safe_float(event.get("start", event.get("start_sec")))
            end = self._safe_float(event.get("end", event.get("end_sec")))
            if midi_note is None or start is None or end is None:
                continue
            if end <= start:
                continue

            end = self._apply_note_end_gap(start, end)

            velocity = self._bounded_velocity(event.get("velocity"), default=95)
            instrument.notes.append(
                pretty_midi.Note(
                    velocity=velocity,
                    pitch=max(0, min(127, midi_note)),
                    start=max(0.0, start),
                    end=max(0.0, end),
                )
            )

    def _add_drum_notes(self, instrument: pretty_midi.Instrument, events: list[dict], bpm: float) -> None:
        # Use a 16th-note duration when drum note end time is not supplied.
        default_drum_len = (60.0 / bpm) / 4.0

        for event in events:
            midi_note = self._safe_int(event.get("note", event.get("midi")))
            start = self._safe_float(event.get("start", event.get("start_sec")))
            if midi_note is None or start is None:
                continue

            end = self._safe_float(event.get("end", event.get("end_sec")))
            if end is None or end <= start:
                end = start + default_drum_len

            velocity = self._bounded_velocity(event.get("velocity"), default=90)
            instrument.notes.append(
                pretty_midi.Note(
                    velocity=velocity,
                    pitch=max(0, min(127, midi_note)),
                    start=max(0.0, start),
                    end=max(0.0, end),
                )
            )

    @staticmethod
    def _safe_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bounded_velocity(value: object, default: int) -> int:
        try:
            velocity = int(round(float(value)))
        except (TypeError, ValueError):
            velocity = int(default)
        return max(1, min(127, velocity))

    def _apply_note_end_gap(self, start: float, end: float) -> float:
        trimmed = float(end) - float(self.NOTE_END_GAP_SEC)
        min_end = float(start) + 1e-4
        return max(min_end, trimmed)
