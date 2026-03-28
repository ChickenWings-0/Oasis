from __future__ import annotations

import numpy as np


class DrumGenerator:
    """Generate one-bar drum MIDI patterns on a 16-step grid."""

    KICK = 36
    SNARE = 38
    HIHAT = 42

    def __init__(self) -> None:
        self._genre_patterns = {
            "lofi": {
                "kick": [0, 8],            # steps 1, 9
                "snare": [4, 12],          # steps 5, 13
                "hihat": list(range(0, 16, 2)),
            },
            "trap": {
                "kick": [0, 3, 7, 10, 14],
                "snare": [4, 12],          # steps 5, 13
                "hihat": list(range(16)),
            },
            "pop": {
                "kick": [0, 4, 8, 12],     # steps 1, 5, 9, 13
                "snare": [4, 12],          # steps 5, 13
                "hihat": list(range(0, 16, 2)),
            },
        }

        self._hihat_velocity_pattern = [100, 60, 80, 60, 100, 60, 80, 60, 100, 60, 80, 60, 100, 60, 80, 60]

        self._genre_swing = {
            "lofi": 0.33,
            "pop": 0.12,
            "trap": 0.0,
        }

    def generate(self, bpm: float, genre: str) -> list[dict[str, int | float]]:
        """Return one bar of drum MIDI events.

        Output format:
        [{"note": int, "start": float, "velocity": int}]
        """
        bpm_val = float(bpm)
        if not np.isfinite(bpm_val) or bpm_val <= 0:
            raise ValueError("bpm must be a positive number")

        genre_key = str(genre).strip().lower()
        if genre_key not in self._genre_patterns:
            raise ValueError("genre must be one of: lofi, trap, pop")

        # 16th-note step duration in seconds (4 steps per beat).
        step_duration = 60.0 / bpm_val / 4.0
        swing_amount = float(self._genre_swing.get(genre_key, 0.0))

        pattern = self._genre_patterns[genre_key]
        rng = np.random.default_rng()

        events: list[dict[str, int | float]] = []
        events.extend(self._build_events_for_steps(pattern["kick"], self.KICK, step_duration, swing_amount, rng))
        events.extend(self._build_events_for_steps(pattern["snare"], self.SNARE, step_duration, swing_amount, rng))
        events.extend(self._build_events_for_steps(pattern["hihat"], self.HIHAT, step_duration, swing_amount, rng))

        events.sort(key=lambda x: (float(x["start"]), int(x["note"])))
        return events

    def _build_events_for_steps(
        self,
        steps: list[int],
        note: int,
        step_duration: float,
        swing_amount: float,
        rng: np.random.Generator,
    ) -> list[dict[str, int | float]]:
        out: list[dict[str, int | float]] = []

        for step in steps:
            if step < 0 or step > 15:
                continue

            velocity = self._compute_velocity(note=note, step=step, rng=rng)

            time = float(step * step_duration)
            if step % 2 == 1:
                time += float(swing_amount) * float(step_duration)

            out.append(
                {
                    "note": int(note),
                    "start": round(time, 4),
                    "velocity": velocity,
                }
            )

        return out

    def _compute_velocity(self, note: int, step: int, rng: np.random.Generator) -> int:
        if note == self.HIHAT:
            base = int(self._hihat_velocity_pattern[step % 16])
        elif note == self.KICK:
            base = int(rng.integers(100, 121))
        elif note == self.SNARE:
            base = int(rng.integers(90, 111))
        else:
            base = 90

        # Slight variation to avoid exact repetition while retaining groove shape.
        variation = int(rng.integers(-5, 6))
        velocity = base + variation

        if note == self.KICK:
            return int(np.clip(velocity, 100, 120))
        if note == self.SNARE:
            return int(np.clip(velocity, 90, 110))
        return int(np.clip(velocity, 1, 127))
