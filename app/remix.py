from __future__ import annotations
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from datetime import datetime

from app.energy import analyze_energy_profile


def remix_audio(path: str | Path, tempo_factor: float = 1.2) -> str:
    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)

    # Get energy profile
    energy_profile = analyze_energy_profile(audio_path)

    segments = []

    for seg in energy_profile:
        start = int(seg["start"] * sr)
        end = int(seg["end"] * sr)

        segment_audio = y[start:end]

        if len(segment_audio) == 0:
            continue

        label = seg["label"]

        # Tempo logic based on energy
        if "DROP" in label or label == "intense":
            factor = tempo_factor + 0.1
        elif label == "build":
            factor = tempo_factor
        else:
            factor = tempo_factor - 0.2

        segment_audio = librosa.effects.time_stretch(segment_audio, rate=max(0.6, factor))

        segments.append({
            "label": label,
            "audio": segment_audio
        })

    # Separate by energy type
    calm = [s["audio"] for s in segments if s["label"] == "calm"]
    build = [s["audio"] for s in segments if s["label"] == "build"]
    drops = [s["audio"] for s in segments if "DROP" in s["label"]]
    intense = [s["audio"] for s in segments if s["label"] == "intense"]

    # Build remix structure
    remix_order = []

    if calm:
        remix_order.append(calm[0])
    if build:
        remix_order.append(build[0])
    if drops:
        remix_order.append(drops[0])
    if intense:
        remix_order.append(intense[0])

    # Add second drop if exists
    if len(drops) > 1:
        remix_order.append(drops[1])

    # Fallback if empty
    if not remix_order:
        remix_order = [s["audio"] for s in segments]

    remixed = np.concatenate(remix_order)

    # Slight pitch lift
    remixed = librosa.effects.pitch_shift(remixed, sr=sr, n_steps=1)

    # Save output
    output_dir = audio_path.parent / "remixed"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"remix_energy_{timestamp}.wav"

    sf.write(str(output_path), remixed, sr)

    return str(output_path)


def remix_audio_advanced(path: str, sections: list) -> str:
    import librosa
    import soundfile as sf
    import numpy as np
    from pathlib import Path
    from datetime import datetime

    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    total_len = len(y)

    output_segments = []

    MIN_SAMPLES = int(0.5 * sr)  # 0.5 sec minimum

    for sec in sections:
        try:
            start = max(0, int(sec["start"] * sr))
            end = min(total_len, int(sec["end"] * sr))

            if end <= start:
                continue

            segment = y[start:end]

            # skip too small segments
            if len(segment) < MIN_SAMPLES:
                continue

            action = sec.get("action", "normal")
            intensity = float(sec.get("intensity", 1.0))

            if action == "drop":
                segment = librosa.effects.time_stretch(segment, rate=1.4 * intensity)
                segment = librosa.effects.pitch_shift(segment, sr=sr, n_steps=2)

            elif action == "build":
                segment = librosa.effects.time_stretch(segment, rate=1.2 * intensity)

            elif action == "slow":
                segment = librosa.effects.time_stretch(segment, rate=0.75 * intensity)

            else:
                segment = librosa.effects.time_stretch(segment, rate=1.0)

            output_segments.append(segment)

        except Exception as e:
            print("Segment error:", e)
            continue

    # IMPORTANT: NO FULL FALLBACK
    if not output_segments:
        print("No valid segments — using first 10 seconds as fallback")
        output_segments = [y[:10 * sr]]

    remixed = np.concatenate(output_segments)

    max_val = np.max(np.abs(remixed))
    if max_val > 0:
        remixed = remixed / max_val

    output_dir = audio_path.parent / "remixed"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"advanced_{timestamp}.wav"

    sf.write(str(output_path), remixed, sr)

    return str(output_path)


def remix_with_style(path: str, style: str) -> str:
    audio_path = Path(path).expanduser().resolve()

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)

    if style == "lofi":
        y = librosa.effects.time_stretch(y, rate=0.9)
        y = librosa.effects.preemphasis(y, coef=0.97)
        y = y * 0.7  # softer

    elif style == "edm":
        y = librosa.effects.time_stretch(y, rate=1.2)
        y = y * 1.2  # louder

    elif style == "high_energy":
        y = librosa.effects.time_stretch(y, rate=1.3)
        y = y * 1.3

    elif style == "slow_reverb":
        y = librosa.effects.time_stretch(y, rate=0.8)

    # normalize
    y = y / np.max(np.abs(y))

    output_dir = audio_path.parent / "remixed"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"style_{style}_{timestamp}.wav"

    sf.write(str(output_path), y, sr)

    return str(output_path)
