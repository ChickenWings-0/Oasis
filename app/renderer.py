from __future__ import annotations

from pathlib import Path

import numpy as np
import pretty_midi
from scipy.io import wavfile


class Renderer:
    """Render PrettyMIDI to WAV audio using FluidSynth."""

    def __init__(self, sample_rate: int = 44100, min_rms: float = 0.1) -> None:
        self.sample_rate = int(sample_rate)
        self.min_rms = float(min_rms)

    def render(
        self,
        midi: pretty_midi.PrettyMIDI,
        sf2_path: str | Path,
        output_path: str | Path,
    ) -> tuple[np.ndarray, Path]:
        if not isinstance(midi, pretty_midi.PrettyMIDI):
            raise TypeError("midi must be a pretty_midi.PrettyMIDI instance")

        soundfont = Path(sf2_path).expanduser().resolve()
        if not soundfont.exists() or soundfont.suffix.lower() != ".sf2":
            raise FileNotFoundError(f"SoundFont (.sf2) not found: {soundfont}")

        out_path = Path(output_path).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            waveform = midi.fluidsynth(fs=self.sample_rate, sf2_path=str(soundfont))
        except Exception as exc:
            raise RuntimeError(
                "FluidSynth rendering failed. Ensure FluidSynth and pyfluidsynth are installed "
                "and the provided .sf2 file is valid."
            ) from exc

        if waveform is None or np.size(waveform) == 0:
            waveform = self._fallback_tone(duration_sec=2.0, channels=1)

        waveform = np.asarray(waveform, dtype=np.float32)
        waveform = np.nan_to_num(waveform, nan=0.0, posinf=0.0, neginf=0.0)

        # Normalize to full-scale if possible.
        peak = float(np.max(np.abs(waveform))) if waveform.size else 0.0
        if peak > 1e-8:
            waveform = waveform / peak

        # Ensure output is audible by boosting low-RMS renders.
        rms = self._rms(waveform)
        if 1e-8 < rms < self.min_rms:
            waveform = waveform * (self.min_rms / rms)
            peak = float(np.max(np.abs(waveform))) if waveform.size else 0.0
            if peak > 1.0:
                waveform = waveform / peak

        # If still silent/nearly silent, replace with an audible fallback tone.
        if self._rms(waveform) <= 1e-8:
            channels = 1 if waveform.ndim == 1 else waveform.shape[1]
            waveform = self._fallback_tone(duration_sec=2.0, channels=channels)

        wav_int16 = (np.clip(waveform, -1.0, 1.0) * 32767).astype(np.int16)
        wavfile.write(str(out_path), self.sample_rate, wav_int16)

        return waveform.astype(np.float32), out_path

    @staticmethod
    def _rms(waveform: np.ndarray) -> float:
        if waveform.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(waveform.astype(np.float32)))))

    def _fallback_tone(self, duration_sec: float, channels: int) -> np.ndarray:
        samples = max(1, int(round(duration_sec * self.sample_rate)))
        t = np.arange(samples, dtype=np.float32) / float(self.sample_rate)
        mono = (0.2 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.float32)

        if channels <= 1:
            return mono

        stereo = np.repeat(mono[:, None], channels, axis=1)
        return stereo.astype(np.float32)
