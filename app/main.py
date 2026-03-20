from __future__ import annotations

import argparse
from pathlib import Path

try:
    from app.config import MODEL_ID, get_device
    from app.generate import analyze_audio_file, generate_music_clip
    from app.humming import (
        extract_melody_events,
        preprocess_humming_wav,
        render_melody_guide_wav,
        save_melody_events_json,
        save_melody_events_midi,
    )
except ModuleNotFoundError:
    from config import MODEL_ID, get_device
    from generate import analyze_audio_file, generate_music_clip
    from humming import (
        extract_melody_events,
        preprocess_humming_wav,
        render_melody_guide_wav,
        save_melody_events_json,
        save_melody_events_midi,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Offline local text-to-music prototype (text generation + humming analysis).\n"
            "Use text mode by default, or pass --humming-wav for analysis/export mode."
        ),
        epilog=(
            "Examples (Windows / PowerShell):\n"
            "  python -m app.main --prompt \"Cinematic ambient pad with soft piano\" --duration 6\n"
            "  python -m app.main --humming-wav outputs\\musicgen_20260320_015111.wav\n"
            "  python -m app.main --humming-wav outputs\\musicgen_20260320_015111.wav --melody-out outputs\\melody_events.json\n"
            "  python -m app.main --humming-wav outputs\\musicgen_20260320_015111.wav --melody-midi-out outputs\\melody_events.mid\n"
            "  python -m app.main --humming-wav outputs\\musicgen_20260320_015111.wav --melody-guide-out outputs\\melody_guide.wav\n"
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
    parser.add_argument(
        "--humming-wav",
        type=str,
        default=None,
        help="Input humming/whistling WAV path (enables humming-analysis mode).",
    )
    parser.add_argument(
        "--humming-target-sr",
        type=int,
        default=32000,
        help="Target sample rate for humming preprocessing/resampling.",
    )
    parser.add_argument(
        "--melody-out",
        type=str,
        default=None,
        help="Optional output path to save extracted melody events as JSON.",
    )
    parser.add_argument(
        "--melody-midi-out",
        type=str,
        default=None,
        help="Optional output path to save extracted melody events as MIDI (.mid).",
    )
    parser.add_argument(
        "--melody-guide-out",
        type=str,
        default=None,
        help="Optional output path to save rendered guide melody WAV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_prompt = args.prompt

    try:
        if args.humming_wav:
            print("Mode: humming-analysis")
            humming_info = preprocess_humming_wav(
                wav_path=Path(args.humming_wav),
                target_sample_rate=args.humming_target_sr,
            )
            melody_events = extract_melody_events(
                waveform=humming_info["waveform"],
                sample_rate=humming_info["target_sample_rate"],
            )
            print("Humming preprocessing info:")
            print(f"Input path: {humming_info['input_path']}")
            print(f"Input sample rate: {humming_info['input_sample_rate']}")
            print(f"Target sample rate: {humming_info['target_sample_rate']}")
            print(f"Resampled: {humming_info['resampled']}")
            print(f"Channel status: {humming_info['channel_status']}")
            print(f"Duration (s): {humming_info['duration_seconds']}")
            print(f"Num samples: {humming_info['num_samples']}")
            print(f"Normalized: {humming_info['normalized']}")
            print(f"Extracted melody events: {len(melody_events)}")
            for event in melody_events[:20]:
                print(event)

            output_json_path: Path | None = None
            output_midi_path: Path | None = None
            output_guide_path: Path | None = None

            if args.melody_out:
                saved = save_melody_events_json(melody_events, Path(args.melody_out))
                print(f"Saved melody events JSON: {saved.resolve()}")
                output_json_path = saved.resolve()

            if args.melody_midi_out:
                saved_midi = save_melody_events_midi(melody_events, Path(args.melody_midi_out))
                print(f"Saved melody events MIDI: {saved_midi.resolve()}")
                output_midi_path = saved_midi.resolve()

            if args.melody_guide_out:
                saved_guide = render_melody_guide_wav(
                    events=melody_events,
                    output_path=Path(args.melody_guide_out),
                    sample_rate=humming_info["target_sample_rate"],
                )
                print(f"Saved melody guide WAV: {saved_guide.resolve()}")
                output_guide_path = saved_guide.resolve()

            print("Artifacts summary:")
            print(f"- Output JSON: {output_json_path if output_json_path else 'not saved'}")
            print(f"- Output MIDI: {output_midi_path if output_midi_path else 'not saved'}")
            print(f"- Output Guide WAV: {output_guide_path if output_guide_path else 'not saved'}")
            return

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
