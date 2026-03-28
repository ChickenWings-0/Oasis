import numpy as np
import scipy.signal as signal
import soundfile as sf
import time
from pathlib import Path
from datetime import datetime


EQ_PRESETS = {
    "Flat": [0, 0, 0, 0, 0, 0, 0, 0],
    "Bass Boost": [10, 8, 3, -2, -4, -3, 0, 0],
    "EDM / Club": [8, 6, -3, -2, 3, 6, 7, 5],
    "Cinematic": [7, 5, -2, 2, 4, 5, 7, 8],
    "Ambient / Space": [5, 4, -5, -6, -3, 4, 8, 9],
    "Vocal Focus": [-5, -3, -2, 4, 7, 6, 3, 2],
    "Acoustic Soft": [-1, 2, 3, 3, 4, 3, 2, 1],
    "Vintage Radio": [-10, -6, 3, 6, 5, -4, -8, -10],
}


EQ_BAND_FREQS = [60, 150, 400, 1000, 2400, 6000, 12000, 16000]


def peaking_eq(y, sr, freq, gain_db, Q=1.0):
    freq = max(20.0, min(float(freq), float(sr) * 0.45))
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / (2 * Q)

    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A

    b = np.array([b0, b1, b2]) / a0
    a = np.array([1, a1 / a0, a2 / a0])

    return signal.lfilter(b, a, y)


def apply_eq(y, sr, gains):
    print("Applying EQ...")

    for freq, gain in zip(EQ_BAND_FREQS, gains):
        y = peaking_eq(y, sr, freq, gain, Q=0.7)

    return y


def process_in_chunks(audio_path, gains, chunk_seconds=5):
    output = []

    with sf.SoundFile(audio_path, mode="r") as input_file:
        sr = int(input_file.samplerate)
        chunk_size = max(1, sr * int(chunk_seconds))

        chunk_index = 0
        for chunk in input_file.blocks(blocksize=chunk_size, dtype="float32", always_2d=False):
            chunk_index += 1
            print(f"Processing chunk {chunk_index}")

            if isinstance(chunk, np.ndarray) and chunk.ndim > 1:
                chunk = np.mean(chunk, axis=1)

            chunk_eq = apply_eq(chunk, sr, gains)
            output.append(chunk_eq)

    if not output:
        raise ValueError("Input audio is empty or unreadable.")

    return np.concatenate(output), sr


def normalize_audio(y):
    max_val = np.max(np.abs(y))
    if max_val > 0:
        return y / max_val * 0.95
    return y


def run_equalizer(audio_path, g1, g2, g3, g4, g5, g6, g7, g8):
    try:
        gains = [g1, g2, g3, g4, g5, g6, g7, g8]
        print("EQ GAINS:", gains)

        y_eq, sr = process_in_chunks(audio_path, gains)

        y_eq = y_eq - np.mean(y_eq)
        max_val = np.max(np.abs(y_eq))
        if max_val > 0:
            y_eq = y_eq / max_val * 0.95

        output_dir = Path(audio_path).parent / "equalized"
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / f"eq_{datetime.now().strftime('%H%M%S')}.wav"
        sf.write(str(output_path), y_eq, sr)
        print("Output path:", output_path)

        time.sleep(0.1)
        return str(output_path)
    except Exception as e:
        print("EQ ERROR:", e)
        return None
