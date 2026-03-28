from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from app.arranger import Arranger
from app.bass_generator import BassGenerator
from app.chord_generator import ChordGenerator
from app.config import OUTPUT_DIR
from app.drum_generator import DrumGenerator
from app.melody_processor import MelodyProcessor
from app.renderer import Renderer


class MusicPipeline:
    """End-to-end note-event to rendered WAV pipeline."""

    def __init__(
        self,
        sf2_path: str | Path | None = None,
        output_dir: Path = OUTPUT_DIR,
        melody_processor: MelodyProcessor | None = None,
        chord_generator: ChordGenerator | None = None,
        drum_generator: DrumGenerator | None = None,
        bass_generator: BassGenerator | None = None,
        arranger: Arranger | None = None,
        renderer: Renderer | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.sf2_path = Path(sf2_path).expanduser() if sf2_path else self._resolve_soundfont_from_env()
        self.output_dir = Path(output_dir)

        self.melody_processor = melody_processor or MelodyProcessor()
        self.chord_generator = chord_generator or ChordGenerator()
        self.drum_generator = drum_generator or DrumGenerator()
        self.bass_generator = bass_generator or BassGenerator()
        self.arranger = arranger or Arranger()
        self.renderer = renderer or Renderer()

        self.logger = logger or logging.getLogger(__name__)

    def run(self, events: list[dict], genre: str = "lofi") -> Path:
        """Run the full note-to-music pipeline and return the rendered WAV path."""
        if not isinstance(events, list):
            raise TypeError("events must be a list of melody event dictionaries")

        if self.sf2_path is None:
            raise ValueError(
                "No SoundFont configured. Provide sf2_path to MusicPipeline(...) or set OASIS_SF2_PATH."
            )

        self.logger.debug("Pipeline start: raw note events=%d, genre=%s", len(events), genre)

        # 1) Melody cleanup + tempo/key inference.
        note_events, bpm, key, scale = self.melody_processor.process(events)
        self.logger.debug(
            "MelodyProcessor: events=%d, bpm=%.2f, key=%s, scale=%s",
            len(note_events),
            bpm,
            key,
            scale,
        )

        # 2) Chord generation.
        chords = self.chord_generator.generate(note_events, key, scale, genre=genre)
        self.logger.debug("ChordGenerator: bars=%d", len(chords))

        # 3) Drum generation (single bar template) + expand to arrangement duration.
        drum_template = self.drum_generator.generate(bpm, genre)
        arrangement_end = self._estimate_arrangement_end(note_events, chords)
        drums = self._tile_drum_pattern(drum_template, bpm, arrangement_end)
        self.logger.debug(
            "DrumGenerator: template_events=%d, tiled_events=%d, arrangement_end=%.3f",
            len(drum_template),
            len(drums),
            arrangement_end,
        )

        # 4) Bass generation from chords.
        bass = self.bass_generator.generate(chords)
        self.logger.debug("BassGenerator: events=%d", len(bass))

        # 5) Arrange all tracks to MIDI.
        midi = self.arranger.arrange(
            note_events=note_events,
            chord_progression=chords,
            bass_events=bass,
            drum_events=drums,
            bpm=bpm,
        )
        self.logger.debug("Arranger: tracks=%d", len(midi.instruments))

        # 6) Render MIDI to WAV.
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_wav = self.output_dir / f"music_pipeline_{stamp}.wav"

        _, rendered_path = self.renderer.render(midi, self.sf2_path, output_wav)
        self.logger.debug("Renderer: output=%s", rendered_path)

        return rendered_path

    def _estimate_arrangement_end(self, note_events: list[dict], chords: list[dict]) -> float:
        melody_end = max((float(e.get("end", e.get("end_sec", 0.0))) for e in note_events), default=0.0)
        chord_end = max((float(c.get("end", c.get("end_sec", 0.0))) for c in chords), default=0.0)

        end_time = max(melody_end, chord_end)
        return max(1.0, float(end_time))

    def _tile_drum_pattern(self, template_events: list[dict], bpm: float, total_duration: float) -> list[dict]:
        if not template_events:
            return []

        bar_duration = (60.0 / max(float(bpm), 1e-6)) * 4.0
        bars = max(1, int((total_duration + 1e-9) // bar_duration + (1 if total_duration % bar_duration > 1e-9 else 0)))

        tiled: list[dict] = []
        for bar_idx in range(bars):
            offset = bar_idx * bar_duration
            for event in template_events:
                start = float(event.get("start", 0.0)) + offset
                if start > total_duration + 1e-6:
                    continue
                tiled.append(
                    {
                        "note": int(event["note"]),
                        "start": round(start, 4),
                        "velocity": int(event.get("velocity", 90)),
                    }
                )

        tiled.sort(key=lambda e: (float(e["start"]), int(e["note"])))
        return tiled

    @staticmethod
    def _resolve_soundfont_from_env() -> Path | None:
        env_value = os.environ.get("OASIS_SF2_PATH")
        if not env_value:
            return None

        path = Path(env_value).expanduser()
        return path
