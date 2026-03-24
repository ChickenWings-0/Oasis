import librosa
import numpy as np
import scipy.signal as signal
import soundfile as sf
from pathlib import Path
from datetime import datetime


def normalize_safe(y):
    max_val = np.max(np.abs(y))
    if max_val > 0:
        return y / max_val * 0.95
    return y


def safe_filter(func, y):
    try:
        out = func(y)
        if np.isnan(out).any() or np.isinf(out).any():
            return y
        return out
    except:
        return y


def safe_time_stretch(y, rate):
    try:
        return librosa.effects.time_stretch(y, rate=rate)
    except:
        return y


def safe_pitch_shift(y, sr, steps):
    try:
        return librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
    except:
        return y


def high_cut(y, sr, cutoff):
    def f(sig):
        nyquist = sr / 2
        b, a = signal.butter(2, cutoff / nyquist, btype="low")
        return signal.filtfilt(b, a, sig)

    return safe_filter(f, y)


def high_pass_filter(y, sr, cutoff):
    def f(sig):
        nyquist = sr / 2
        b, a = signal.butter(2, cutoff / nyquist, btype="high")
        return signal.filtfilt(b, a, sig)

    return safe_filter(f, y)


def low_cut(y, sr, cutoff=120):
    def f(sig):
        b, a = signal.butter(2, cutoff / (sr / 2), btype="high")
        return signal.filtfilt(b, a, sig)

    return safe_filter(f, y)


def gentle_saturation(y, amount=0.8):
    return np.tanh(y * amount)


def light_reverb(y, sr, decay=0.2):
    delay = int(0.02 * sr)
    if delay <= 0 or delay >= len(y):
        return y
    echo = np.zeros_like(y)
    echo[delay:] = y[:-delay]

    out = y + decay * echo

    # Remove bass buildup from the reverb tail.
    out = low_cut(out, sr, cutoff=120)

    return out


def gentle_gain(y, gain=1.02):
    return y * gain


def apply_style_transfer(path: str, style: str) -> str:
    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)

    y = normalize_safe(y)

    # ---------------- STYLE LOGIC ---------------- #

    # -------- LOFI CHILL --------
    if style == "lofi_chill":
        y = safe_time_stretch(y, 0.97)
        y = high_cut(y, sr, 5000)
        y += np.random.randn(len(y)) * 0.0005

    # -------- BASS BOOST (CONTROLLED) --------
    elif style == "bass_boost":
        y = y + 0.02 * np.sin(np.linspace(0, 20, len(y)))

    # -------- EDM CLUB --------
    elif style == "edm_club":
        y = safe_time_stretch(y, 1.03)
        y = high_pass_filter(y, sr, 120)
        y = gentle_saturation(y, 0.8)

    # -------- CINEMATIC --------
    elif style == "cinematic":
        y = safe_pitch_shift(y, sr, -1)
        y = light_reverb(y, sr, 0.4)

    # -------- AMBIENT SPACE --------
    elif style == "ambient_space":
        y = high_cut(y, sr, 3500)
        y = light_reverb(y, sr, 0.6)

    # -------- VOCAL FOCUS --------
    elif style == "vocal_focus":
        y = high_pass_filter(y, sr, 150)
        y = high_cut(y, sr, 6000)
        y = gentle_saturation(y, 0.6)

    # -------- ACOUSTIC SOFT --------
    elif style == "acoustic_soft":
        y = high_cut(y, sr, 4500)

    # -------- VINTAGE RADIO --------
    elif style == "vintage_radio":
        y = high_pass_filter(y, sr, 400)
        y = high_cut(y, sr, 2500)

    # -------- PARTY MODE --------
    elif style == "party_mode":
        y = gentle_saturation(y, 0.9)

    # -------- NIGHT DRIVE --------
    elif style == "night_drive":
        y = high_cut(y, sr, 6000)
        y = light_reverb(y, sr, 0.2)

    # -------- HYPERPOP --------
    elif style == "hyperpop":
        y = safe_time_stretch(y, 1.1)
        y = safe_pitch_shift(y, sr, 2)
        y = high_cut(y, sr, 8000)

    # -------- HEADPHONE IMMERSION --------
    elif style == "headphone_immersion":
        y = light_reverb(y, sr, 0.3)

    # -------- BACKGROUND CHILL --------
    elif style == "background_chill":
        y = y * 0.85
        y = high_cut(y, sr, 5000)

    # -------- STUDIO CLEAN --------
    elif style == "studio_clean":
        pass

    # -------- EPIC TRAILER --------
    elif style == "epic_trailer":
        y = safe_pitch_shift(y, sr, -2)
        y = light_reverb(y, sr, 0.5)

    # -------- DREAMY --------
    elif style == "dreamy":
        y = high_cut(y, sr, 4000)
        y = light_reverb(y, sr, 0.6)

    # -------- UNDERWATER --------
    elif style == "underwater":
        y = high_cut(y, sr, 2000)
        y = y * 0.7

    # -------- TELEPHONE --------
    elif style == "telephone":
        y = high_pass_filter(y, sr, 500)
        y = high_cut(y, sr, 3000)

    # -------- HALL CONCERT --------
    elif style == "hall_concert":
        y = light_reverb(y, sr, 0.7)

    # -------- MONO CLASSIC --------
    elif style == "mono_classic":
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        # keep waveform, do NOT flatten

    # Global low-end management for all non bass-boost styles.
    if style != "bass_boost":
        y = low_cut(y, sr, cutoff=100)
        y = high_pass_filter(y, sr, 80)

    # ---------------- SAVE ---------------- #

    print(f"STYLE APPLIED: {style}")

    y = y - np.mean(y)
    y = normalize_safe(y)

    output_dir = audio_path.parent / "styled"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"styled_{style}_{timestamp}.wav"

    sf.write(str(output_path), y, sr)

    return str(output_path)
