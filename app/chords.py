from __future__ import annotations

import argparse
from pathlib import Path

import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def detect_chords(
    waveform: np.ndarray,
    sr: int,
    key: str | None = None,
    scale: str | None = None,
) -> dict[str, object]:
    sample_rate = int(sr)
    key = str(key or "C")
    scale = str(scale or "major")
    hop_length = 512
    min_chord_duration = 0.5

    audio = np.asarray(waveform, dtype=np.float32)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)

    if audio.size == 0:
        return {"chords": [], "confidence": 0.0}

    if float(np.max(np.abs(audio))) <= 1e-8:
        return {"chords": [], "confidence": 0.0}

    chroma = librosa.feature.chroma_cqt(y=audio, sr=int(sample_rate), hop_length=hop_length)
    low_freq_boost = np.linspace(1.5, 1.0, chroma.shape[0], dtype=np.float32)
    chroma = chroma * low_freq_boost[:, None]

    frame_count = chroma.shape[1]
    if frame_count == 0:
        return {"chords": [], "confidence": 0.0}

    _, beat_frames = librosa.beat.beat_track(y=audio, sr=int(sample_rate), hop_length=hop_length)
    beat_frames = np.asarray(beat_frames, dtype=int)

    if beat_frames.size < 4:
        beat_frames = np.arange(0, frame_count, 4, dtype=int)

    beat_frames = beat_frames[(beat_frames >= 0) & (beat_frames < frame_count)]
    if beat_frames.size == 0 or beat_frames[0] != 0:
        beat_frames = np.concatenate(([0], beat_frames))
    if beat_frames[-1] != frame_count:
        beat_frames = np.concatenate((beat_frames, [frame_count]))

    beat_chroma = librosa.util.sync(chroma, idx=beat_frames, aggregate=np.mean)
    beat_times = librosa.frames_to_time(beat_frames, sr=int(sample_rate), hop_length=hop_length)

    templates = _build_chord_templates()
    labels: list[str] = []
    similarities: list[float] = []

    for i in range(beat_chroma.shape[1]):
        vec = beat_chroma[:, i].astype(np.float32)
        vec_norm = float(np.linalg.norm(vec))
        if vec_norm <= 1e-8:
            labels.append("N")
            similarities.append(0.0)
            continue

        best_label = "N"
        best_score = -1.0
        for label, template in templates.items():
            score = _cosine_similarity(vec, template)
            if not _is_chord_in_key(label, key, scale):
                score *= 0.4
            if score > best_score:
                best_score = score
                best_label = label

        labels.append(best_label)
        similarities.append(float(max(0.0, best_score)))

    labels = _smooth_single_frame_noise(labels)
    labels = _smooth_multi_pass_patterns(labels)

    chords: list[dict[str, object]] = []
    if labels:
        seg_label = labels[0]
        seg_start = float(beat_times[0])
        for i in range(1, len(labels)):
            if labels[i] != seg_label:
                seg_end = float(beat_times[i])
                chords.append({"chord": seg_label, "start": round(seg_start, 4), "end": round(seg_end, 4)})
                seg_label = labels[i]
                seg_start = float(beat_times[i])

        final_end_idx = min(len(beat_times) - 1, len(labels))
        seg_end = float(beat_times[final_end_idx])
        chords.append({"chord": seg_label, "start": round(seg_start, 4), "end": round(seg_end, 4)})

    # Enforce minimum duration and merge short segments to neighbors.
    filtered_chords = _merge_short_segments_into_neighbors(chords, min_chord_duration=min_chord_duration)
    filtered_chords = _merge_similar_chords(filtered_chords)

    confidence = float(np.mean(similarities)) if similarities else 0.0
    if labels and len(set(labels)) > len(labels) * 0.7:
        confidence *= 0.7

    return {
        "chords": filtered_chords,
        "confidence": float(np.clip(confidence, 0.0, 1.0)),
    }


def _build_chord_templates() -> dict[str, np.ndarray]:
    qualities = {
        "": [0, 4, 7],       # major
        "m": [0, 3, 7],      # minor
        "7": [0, 4, 7, 10],  # dominant 7th
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
        "dim": [0, 3, 6],    # diminished
        "sus": [0, 5, 7],    # suspended (sus4)
        "5": [0, 7],         # power chord (root + fifth)
    }

    templates: dict[str, np.ndarray] = {}
    for root in range(12):
        root_name = NOTE_NAMES[root]
        for suffix, intervals in qualities.items():
            vec = np.zeros(12, dtype=np.float32)
            for interval in intervals:
                vec[(root + interval) % 12] = 1.0
            norm = float(np.linalg.norm(vec))
            if norm > 0.0:
                vec = vec / norm
            templates[f"{root_name}{suffix}"] = vec
    return templates


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = float(np.linalg.norm(a))
    b_norm = float(np.linalg.norm(b))
    if a_norm <= 1e-8 or b_norm <= 1e-8:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


def _smooth_single_frame_noise(labels: list[str]) -> list[str]:
    if len(labels) < 3:
        return labels

    smoothed = labels[:]
    for i in range(1, len(labels) - 1):
        if labels[i - 1] == labels[i + 1] and labels[i] != labels[i - 1]:
            smoothed[i] = labels[i - 1]
    return smoothed


def _smooth_multi_pass_patterns(labels: list[str], passes: int = 2) -> list[str]:
    if len(labels) < 3:
        return labels

    smoothed = labels[:]
    for _ in range(max(1, int(passes))):
        # Fix ABA patterns (middle isolated frame).
        for i in range(1, len(smoothed) - 1):
            if smoothed[i - 1] == smoothed[i + 1] and smoothed[i] != smoothed[i - 1]:
                smoothed[i] = smoothed[i - 1]

        # Fix ABBA patterns (two-frame island between same labels).
        if len(smoothed) >= 4:
            for i in range(1, len(smoothed) - 2):
                if smoothed[i - 1] == smoothed[i + 2] and (
                    smoothed[i] != smoothed[i - 1] or smoothed[i + 1] != smoothed[i - 1]
                ):
                    smoothed[i] = smoothed[i - 1]
                    smoothed[i + 1] = smoothed[i - 1]

    return smoothed


def _note_name_to_pitch_class(note_name: str) -> int:
    norm = str(note_name).strip().upper()
    aliases = {
        "DB": "C#",
        "EB": "D#",
        "GB": "F#",
        "AB": "G#",
        "BB": "A#",
        "CB": "B",
        "FB": "E",
        "B#": "C",
        "E#": "F",
    }
    norm = aliases.get(norm, norm)
    if norm in NOTE_NAMES:
        return NOTE_NAMES.index(norm)
    return 0


def _split_chord_label(chord_label: str) -> tuple[str, str]:
    text = str(chord_label)
    if text == "N":
        return "N", ""

    if len(text) >= 2 and text[1] in {"#", "b"}:
        root = text[:2]
        suffix = text[2:]
    else:
        root = text[:1]
        suffix = text[1:]
    return root, suffix


def _is_chord_in_key(chord_label: str, key: str, scale: str) -> bool:
    root, _ = _split_chord_label(chord_label)
    if root == "N":
        return True

    root_pc = _note_name_to_pitch_class(root)
    key_pc = _note_name_to_pitch_class(key)
    mode = str(scale).strip().lower()

    if mode == "minor":
        intervals = [0, 2, 3, 5, 7, 8, 10]
    else:
        intervals = [0, 2, 4, 5, 7, 9, 11]

    in_key_pcs = {(key_pc + i) % 12 for i in intervals}
    return root_pc in in_key_pcs


def _are_similar_chords(chord_a: str, chord_b: str) -> bool:
    root_a, suffix_a = _split_chord_label(chord_a)
    root_b, suffix_b = _split_chord_label(chord_b)

    if root_a == "N" or root_b == "N":
        return chord_a == chord_b
    if root_a != root_b:
        return False

    major_family = {"", "7", "maj7", "sus", "5"}
    minor_family = {"m", "min7"}

    if suffix_a == suffix_b:
        return True
    if suffix_a in major_family and suffix_b in major_family:
        return True
    if suffix_a in minor_family and suffix_b in minor_family:
        return True
    return False


def _merge_similar_chords(chords: list[dict[str, object]]) -> list[dict[str, object]]:
    if not chords:
        return []

    merged: list[dict[str, object]] = [dict(chords[0])]
    for chord in chords[1:]:
        current = dict(chord)
        prev = merged[-1]

        prev_label = str(prev.get("chord", "N"))
        curr_label = str(current.get("chord", "N"))
        if _are_similar_chords(prev_label, curr_label):
            prev["end"] = max(float(prev["end"]), float(current["end"]))
            prev["end"] = round(float(prev["end"]), 4)
        else:
            merged.append(current)

    return merged


def _merge_short_segments_into_neighbors(
    chords: list[dict[str, object]],
    min_chord_duration: float = 0.5,
) -> list[dict[str, object]]:
    if not chords:
        return []

    segments: list[dict[str, object]] = [dict(c) for c in chords]

    i = 0
    while i < len(segments):
        current = segments[i]
        duration = float(current["end"]) - float(current["start"])

        if duration >= min_chord_duration or len(segments) == 1:
            i += 1
            continue

        if i == 0:
            segments[1]["start"] = float(current["start"])
            del segments[0]
            continue

        if i == len(segments) - 1:
            segments[i - 1]["end"] = float(current["end"])
            del segments[i]
            i = max(0, i - 1)
            continue

        prev_duration = float(segments[i - 1]["end"]) - float(segments[i - 1]["start"])
        next_duration = float(segments[i + 1]["end"]) - float(segments[i + 1]["start"])

        if prev_duration >= next_duration:
            segments[i - 1]["end"] = float(current["end"])
            del segments[i]
            i = max(0, i - 1)
        else:
            segments[i + 1]["start"] = float(current["start"])
            del segments[i]

    cleaned: list[dict[str, object]] = []
    for seg in segments:
        start = round(float(seg["start"]), 4)
        end = round(float(seg["end"]), 4)
        if end > start:
            cleaned.append({"chord": seg["chord"], "start": start, "end": end})

    return cleaned


def _infer_triad(chroma_vector: np.ndarray) -> str:
    """Infer a basic major/minor triad from a single chroma vector."""
    root = int(np.argmax(chroma_vector))
    major_third = chroma_vector[(root + 4) % 12]
    minor_third = chroma_vector[(root + 3) % 12]
    root_name = NOTE_NAMES[root]

    if major_third - minor_third > 0.05:
        return root_name
    elif minor_third - major_third > 0.05:
        return f"{root_name}m"
    else:
        return root_name


def detect_chords_from_path(path: str | Path, key: str = "C", scale: str = "major") -> list[str]:
    audio_path = Path(path).expanduser().resolve()
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    waveform, sample_rate = librosa.load(str(audio_path), sr=None, mono=True)
    detected = detect_chords(waveform=waveform, sr=int(sample_rate), key=key, scale=scale)
    segments = detected.get("chords", [])

    chord_names: list[str] = []
    for seg in segments:
        label = str(seg.get("chord", "")).strip()
        if not label or label == "N":
            continue
        if not chord_names or chord_names[-1] != label:
            chord_names.append(label)

    return chord_names


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect simple chord progression from audio.")
    parser.add_argument("audio_path", help="Path to input audio file")
    args = parser.parse_args()

    result = detect_chords_from_path(args.audio_path)
    print(result)


if __name__ == "__main__":
    main()
