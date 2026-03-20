#!/usr/bin/env python3
"""
Video Editing Module
Supports editing operations: trim, merge, speed, and audio controls.
"""

import argparse
from pathlib import Path
from typing import Optional
import logging

from PIL import Image

from moviepy.editor import AudioFileClip, VideoFileClip, afx, concatenate_videoclips, vfx

if not hasattr(Image, "ANTIALIAS") and hasattr(Image, "Resampling"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _validate_time_range(start_time: float, end_time: float, duration: float) -> None:
    if start_time < 0:
        raise ValueError("start_time must be >= 0")

    if end_time <= 0:
        raise ValueError("end_time must be > 0")

    if start_time >= end_time:
        raise ValueError("start_time must be less than end_time")

    if start_time >= duration:
        raise ValueError("start_time cannot be beyond video duration")


def edit_video(
    input_path: str,
    output_path: str,
    start_time: float,
    end_time: float,
    merge_input_path: Optional[str] = None,
    audio_input_path: Optional[str] = None,
    speed: float = 1.0,
    mute: bool = False,
    volume: float = 1.0,
) -> str:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input video not found: {input_file}")

    if speed <= 0:
        raise ValueError("speed must be greater than 0")

    if volume < 0:
        raise ValueError("volume must be >= 0")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading input video: %s", input_file)
    merge_file: Optional[Path] = Path(merge_input_path) if merge_input_path else None
    audio_file: Optional[Path] = Path(audio_input_path) if audio_input_path else None

    if merge_file and not merge_file.exists():
        raise FileNotFoundError(f"Merge input video not found: {merge_file}")

    if audio_file and not audio_file.exists():
        raise FileNotFoundError(f"Audio input file not found: {audio_file}")

    opened_clips = []
    opened_audio_clips = []

    try:
        primary_clip = VideoFileClip(str(input_file))
        opened_clips.append(primary_clip)
        working_clip = primary_clip

        if merge_file:
            logger.info("Loading merge video: %s", merge_file)
            merge_clip = VideoFileClip(str(merge_file)).resize(primary_clip.size)
            opened_clips.append(merge_clip)
            working_clip = concatenate_videoclips([primary_clip, merge_clip], method="compose")
            opened_clips.append(working_clip)

        duration = float(working_clip.duration)

        effective_end = min(end_time, duration)
        _validate_time_range(start_time, effective_end, duration)

        logger.info("Applying trim: start=%s, end=%s", start_time, effective_end)
        edited = working_clip.subclip(start_time, effective_end)
        opened_clips.append(edited)

        if speed != 1.0:
            logger.info("Applying speed factor: %s", speed)
            edited = edited.fx(vfx.speedx, speed)
            opened_clips.append(edited)

        if audio_file and not mute:
            logger.info("Applying external audio track: %s", audio_file)
            external_audio = AudioFileClip(str(audio_file))
            opened_audio_clips.append(external_audio)

            if external_audio.duration < edited.duration:
                external_audio = afx.audio_loop(external_audio, duration=edited.duration)
                opened_audio_clips.append(external_audio)

            external_audio = external_audio.subclip(0, edited.duration)
            opened_audio_clips.append(external_audio)
            edited = edited.set_audio(external_audio)
            opened_clips.append(edited)

        if mute:
            logger.info("Muting audio")
            edited = edited.without_audio()
            opened_clips.append(edited)
        elif edited.audio is not None and volume != 1.0:
            logger.info("Applying volume factor: %s", volume)
            edited = edited.volumex(volume)
            opened_clips.append(edited)

        logger.info("Writing output video: %s", output_file)
        edited.write_videofile(
            str(output_file),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(output_file.with_suffix(".temp-audio.m4a")),
            remove_temp=True,
            logger=None,
        )
    finally:
        for clip in reversed(opened_clips):
            try:
                clip.close()
            except Exception:
                pass

        for audio_clip in reversed(opened_audio_clips):
            try:
                audio_clip.close()
            except Exception:
                pass

    return str(output_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Edit a video file")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", required=True, help="Output video file path")
    parser.add_argument("--start", type=float, required=True, help="Trim start time in seconds")
    parser.add_argument("--end", type=float, required=True, help="Trim end time in seconds")
    parser.add_argument("--merge-input", help="Optional second video file path to append")
    parser.add_argument("--audio-input", help="Optional external audio file path")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed factor (0.25-4.0)")
    parser.add_argument("--mute", action="store_true", help="Mute audio")
    parser.add_argument("--volume", type=float, default=1.0, help="Audio volume factor (0.0-2.0)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = edit_video(
            input_path=args.input,
            output_path=args.output,
            start_time=args.start,
            end_time=args.end,
            merge_input_path=args.merge_input,
            audio_input_path=args.audio_input,
            speed=args.speed,
            mute=args.mute,
            volume=args.volume,
        )
        print(f"SUCCESS: {output}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
