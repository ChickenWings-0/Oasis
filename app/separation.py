from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import torch

from app.config import OUTPUT_DIR

REQUIRED_STEMS = ("drums", "bass", "vocals", "other")


def _ffmpeg_bin_candidates() -> list[Path]:
    candidates: list[Path] = []

    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    if local_app_data:
        # Winget symlink aliases path (ffmpeg.exe, ffprobe.exe, ffplay.exe)
        candidates.append(local_app_data / "Microsoft" / "WinGet" / "Links")

        # Gyan shared build installed by winget.
        candidates.extend(
            local_app_data.glob(
                "Microsoft/WinGet/Packages/Gyan.FFmpeg.Shared*/ffmpeg-*/bin"
            )
        )

        # Gyan static build (still useful for ffmpeg.exe even if torchcodec prefers shared DLLs).
        candidates.extend(
            local_app_data.glob(
                "Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin"
            )
        )

    program_files = Path(os.environ.get("ProgramFiles", ""))
    if program_files:
        candidates.append(program_files / "ffmpeg" / "bin")

    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[Path] = []
    for path in candidates:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)

    return unique


def _augment_env_with_ffmpeg(env: dict[str, str]) -> dict[str, str]:
    merged = dict(env)
    existing_path = merged.get("PATH", "")
    prefix: list[str] = []

    for folder in _ffmpeg_bin_candidates():
        if (folder / "ffmpeg.exe").exists():
            prefix.append(str(folder))

    if prefix:
        merged["PATH"] = os.pathsep.join(prefix + [existing_path]) if existing_path else os.pathsep.join(prefix)

    return merged


def _find_demucs_stem_dir(output_root: Path) -> Path:
    """Find the directory produced by Demucs that contains all required stems."""
    candidates = []
    for path in output_root.rglob("*"):
        if not path.is_dir():
            continue
        if all((path / f"{stem}.wav").exists() for stem in REQUIRED_STEMS):
            candidates.append(path)

    if not candidates:
        raise FileNotFoundError(
            "Demucs did not produce the expected stems (drums.wav, bass.wav, vocals.wav, other.wav)."
        )

    # Prefer the most recently modified candidate.
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def separate_audio(path: str | Path) -> Dict[str, str]:
    """Separate an input audio file into drums, bass, vocals, and other stems using Demucs."""
    input_path = Path(path).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    # Keep each run in its own folder so previous outputs are never overwritten.
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_root = OUTPUT_DIR / f"separated_{stamp}"
    run_output_root.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    base_command = [
        sys.executable,
        "-m",
        "demucs",
        str(input_path),
        "-o",
        str(run_output_root),
        "--float32",
    ]

    env = _augment_env_with_ffmpeg(os.environ.copy())
    env["TORCHAUDIO_USE_BACKEND"] = "soundfile"

    # Prefer CUDA when available, but fall back to CPU if CUDA execution fails.
    tried = []
    for target_device in ([device, "cpu"] if device == "cuda" else ["cpu"]):
        command = [*base_command, "-d", target_device]
        tried.append(target_device)
        try:
            subprocess.run(command, check=True, env=env)
            break
        except Exception as exc:
            if target_device == "cpu":
                raise RuntimeError(
                    "Demucs separation failed. Ensure Demucs is installed with `pip install demucs` "
                    f"and ffmpeg is available in PATH. Devices tried: {', '.join(tried)}. "
                    f"Original error: {exc}"
                ) from exc

    stem_source_dir = _find_demucs_stem_dir(run_output_root)
    final_dir = OUTPUT_DIR / f"stems_{stamp}"
    final_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, str] = {}
    for stem in REQUIRED_STEMS:
        src = stem_source_dir / f"{stem}.wav"
        dst = final_dir / f"{stem}.wav"
        shutil.copy2(src, dst)
        result[stem] = str(dst.resolve())

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Separate an audio file into Demucs stems.")
    parser.add_argument("input_audio", help="Path to input audio file")
    args = parser.parse_args()

    stems = separate_audio(path=args.input_audio)
    for stem, stem_path in stems.items():
        print(f"{stem}: {stem_path}")


if __name__ == "__main__":
    main()
