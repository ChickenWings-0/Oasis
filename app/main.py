from __future__ import annotations

import argparse
from pathlib import Path

try:
    from app.config import MODEL_ID, get_device
    from app.generate import analyze_audio_file, generate_music_clip
except ModuleNotFoundError:
    from config import MODEL_ID, get_device
    from generate import analyze_audio_file, generate_music_clip


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Offline local text-to-music prototype.\n"
            "Text-generation mode with optional post-generation analysis."
        ),
        epilog=(
            "Examples (Windows / PowerShell):\n"
            "  python -m app.main --prompt \"Cinematic ambient pad with soft piano\" --duration 6\n"
            "  python -m app.main --prompt \"Lo-fi chill beat\" --duration 4 --guide-audio-wav outputs\\melody_guide.wav"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Lo-fi chill beat with soft piano and warm bass, relaxing nighttime mood",
        help="Text prompt used in text-generation mode.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=8,
        help="Target generated clip duration in seconds (text-generation mode).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional generation seed for repeatable sampling behavior.",
    )
    parser.add_argument(
        "--guide-audio-wav",
        type=str,
        default=None,
        help="Optional guide WAV for experimental guide-conditioned generation (A/B test).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_prompt = args.prompt

    try:
        print("Mode: text-generation")
        device = get_device()
        print(f"Model ID: {MODEL_ID}")
        print(f"Detected device: {device}")
        print(f"Prompt: {sample_prompt}")
        print(f"Duration (s): {args.duration}")
        print(f"Seed: {args.seed}")
        if args.guide_audio_wav:
            print(f"Guide conditioning WAV: {args.guide_audio_wav}")
            print("Note: guide-audio conditioning is experimental; text-only remains the primary generation path.")

        output_path = generate_music_clip(
            prompt=sample_prompt,
            duration_seconds=args.duration,
            seed=args.seed,
            guide_audio_wav=Path(args.guide_audio_wav) if args.guide_audio_wav else None,
        )
        print(f"Saved generated audio to: {output_path}")
        print(f"File exists: {output_path.exists()}")

        print("Artifacts summary:")
        print(f"- Output WAV: {output_path.resolve()}")

        analysis = analyze_audio_file(output_path)
        print(f"Estimated BPM: {analysis['bpm']}")
        print(f"Estimated Key/Scale: {analysis['key']} {analysis['scale']}")
    except Exception as exc:
        print(f"Generation failed: {exc}")
        raise


if __name__ == "__main__":
    main()
