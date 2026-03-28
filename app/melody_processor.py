from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_INTERVALS = np.array([0, 2, 4, 5, 7, 9, 11], dtype=int)
MINOR_INTERVALS = np.array([0, 2, 3, 5, 7, 8, 10], dtype=int)

# Krumhansl-Schmuckler key profiles (major/minor)
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88], dtype=np.float64)
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17], dtype=np.float64)


@dataclass
class MelodyEvent:
    midi: int
    start: float
    end: float
    confidence: float | None = None

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


class MelodyProcessor:
    """Post-process melody events for rhythmic and tonal musical usability.

    Input event shape expected by process:
    [{"midi": int, "start": float, "end": float, "confidence": optional float}]

    Output:
    (processed_events, bpm, key, scale)
    where key is a pitch name like "C" and scale is "major" or "minor".
    """

    def __init__(
        self,
        min_bpm: float = 60.0,
        max_bpm: float = 180.0,
        default_bpm: float = 120.0,
        low_confidence_threshold: float = 0.6,
    ) -> None:
        self.min_bpm = float(min_bpm)
        self.max_bpm = float(max_bpm)
        self.default_bpm = float(default_bpm)
        self.low_confidence_threshold = float(low_confidence_threshold)

    def process(self, events: list[dict]) -> tuple[list[dict[str, float | int]], float, str, str]:
        parsed = self._normalize_events(events)
        if not parsed:
            bpm = float(self.default_bpm)
            return [], bpm, "C", "major"

        bpm = self._detect_bpm(parsed)
        quantized = self._quantize_events(parsed, bpm)
        quantized = self._merge_adjacent_same_pitch(quantized)

        key_root, mode = self._detect_key_and_scale(quantized)
        scale_pitch_classes = self._build_scale_pitch_classes(key_root, mode)

        constrained = self._enforce_scale(quantized, scale_pitch_classes)
        constrained = self._merge_adjacent_same_pitch(constrained)

        output = [
            {
                "midi": int(ev.midi),
                "start": round(float(ev.start), 4),
                "end": round(float(ev.end), 4),
            }
            for ev in constrained
            if ev.end > ev.start
        ]

        return output, float(round(bpm, 2)), PITCH_CLASS_NAMES[key_root], mode

    def _normalize_events(self, events: Iterable[dict]) -> list[MelodyEvent]:
        normalized: list[MelodyEvent] = []
        for event in events:
            if "midi" not in event:
                continue

            start_val = event.get("start", event.get("start_sec"))
            end_val = event.get("end", event.get("end_sec"))
            if start_val is None or end_val is None:
                continue

            try:
                midi = int(round(float(event["midi"])))
                start = float(start_val)
                end = float(end_val)
            except (TypeError, ValueError):
                continue

            if not np.isfinite(midi) or not np.isfinite(start) or not np.isfinite(end):
                continue

            if end < start:
                start, end = end, start

            confidence_raw = event.get("confidence")
            confidence = None
            if confidence_raw is not None:
                try:
                    confidence = float(confidence_raw)
                except (TypeError, ValueError):
                    confidence = None

            normalized.append(MelodyEvent(midi=midi, start=start, end=end, confidence=confidence))

        normalized.sort(key=lambda ev: (ev.start, ev.end, ev.midi))
        return normalized

    def _detect_bpm(self, events: list[MelodyEvent]) -> float:
        if len(events) < 2:
            return self.default_bpm

        onsets = np.array([ev.start for ev in events], dtype=np.float64)
        iois = np.diff(onsets)
        iois = iois[np.isfinite(iois) & (iois > 1e-4)]
        if iois.size == 0:
            return self.default_bpm

        median_ioi = float(np.median(iois))
        if median_ioi <= 1e-6:
            return self.default_bpm

        bpm = 60.0 / median_ioi
        return float(np.clip(bpm, self.min_bpm, self.max_bpm))

    def _quantize_events(self, events: list[MelodyEvent], bpm: float) -> list[MelodyEvent]:
        bpm_safe = max(1e-6, float(bpm))
        beat_sec = 60.0 / bpm_safe
        grid = beat_sec / 4.0  # 16th-note grid

        quantized: list[MelodyEvent] = []
        for ev in events:
            start_grid_pos = round(ev.start / grid) * grid
            end_grid_pos = round(ev.end / grid) * grid

            # Soft quantization: retain part of the original human timing feel.
            q_start = ev.start + 0.7 * (start_grid_pos - ev.start)
            q_end = ev.end + 0.7 * (end_grid_pos - ev.end)

            if q_end <= q_start:
                q_end = q_start + grid

            # Minimum duration is one grid unit.
            if (q_end - q_start) < grid:
                q_end = q_start + grid

            quantized.append(
                MelodyEvent(
                    midi=int(ev.midi),
                    start=float(max(0.0, q_start)),
                    end=float(max(0.0, q_end)),
                    confidence=ev.confidence,
                )
            )

        quantized.sort(key=lambda e: (e.start, e.end, e.midi))
        return quantized

    def _merge_adjacent_same_pitch(self, events: list[MelodyEvent], tolerance: float = 1e-6) -> list[MelodyEvent]:
        if not events:
            return []

        merged: list[MelodyEvent] = [events[0]]
        for ev in events[1:]:
            prev = merged[-1]
            if ev.midi == prev.midi and ev.start <= (prev.end + tolerance):
                prev.end = max(prev.end, ev.end)
                if prev.confidence is None:
                    prev.confidence = ev.confidence
                elif ev.confidence is not None:
                    prev.confidence = float((prev.confidence + ev.confidence) / 2.0)
            else:
                merged.append(ev)

        return merged

    def _detect_key_and_scale(self, events: list[MelodyEvent]) -> tuple[int, str]:
        if not events:
            return 0, "major"

        histogram = np.zeros(12, dtype=np.float64)
        for ev in events:
            duration = max(ev.duration, 1e-4)
            pitch_class = int(ev.midi) % 12
            histogram[pitch_class] += duration

        total = float(np.sum(histogram))
        if total <= 1e-8:
            return 0, "major"

        histogram = histogram / total

        best_score = -np.inf
        best_root = 0
        best_mode = "major"

        for root in range(12):
            major_profile = np.roll(MAJOR_PROFILE, root)
            minor_profile = np.roll(MINOR_PROFILE, root)

            major_score = self._cosine_similarity(histogram, major_profile)
            minor_score = self._cosine_similarity(histogram, minor_profile)

            if major_score > best_score:
                best_score = major_score
                best_root = root
                best_mode = "major"
            if minor_score > best_score:
                best_score = minor_score
                best_root = root
                best_mode = "minor"

        return best_root, best_mode

    def _build_scale_pitch_classes(self, root: int, mode: str) -> set[int]:
        intervals = MAJOR_INTERVALS if mode == "major" else MINOR_INTERVALS
        return {int((root + i) % 12) for i in intervals}

    def _enforce_scale(self, events: list[MelodyEvent], scale_pitch_classes: set[int]) -> list[MelodyEvent]:
        if not events:
            return []

        constrained: list[MelodyEvent] = []
        for ev in events:
            midi = int(ev.midi)
            pitch_class = midi % 12
            confidence = ev.confidence

            needs_adjust = confidence is None or confidence < self.low_confidence_threshold
            if needs_adjust and pitch_class not in scale_pitch_classes:
                midi = self._snap_to_nearest_scale_midi(midi, scale_pitch_classes)

            constrained.append(MelodyEvent(midi=midi, start=ev.start, end=ev.end, confidence=confidence))

        constrained.sort(key=lambda e: (e.start, e.end, e.midi))
        return constrained

    def _snap_to_nearest_scale_midi(self, midi: int, scale_pitch_classes: set[int]) -> int:
        candidates: list[int] = []
        center_octave = midi // 12

        for octave in range(center_octave - 2, center_octave + 3):
            for pc in scale_pitch_classes:
                candidates.append(octave * 12 + int(pc))

        # Guard fallback (should not occur if scales are built correctly).
        if not candidates:
            return midi

        best = min(candidates, key=lambda c: (abs(c - midi), c))
        return int(best)

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        a_norm = float(np.linalg.norm(a))
        b_norm = float(np.linalg.norm(b))
        if a_norm <= 1e-12 or b_norm <= 1e-12:
            return -np.inf
        return float(np.dot(a, b) / (a_norm * b_norm))
