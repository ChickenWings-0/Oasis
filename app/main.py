from __future__ import annotations

import argparse
from pathlib import Path

try:
    from app.config import MODEL_ID, get_device
    from app.generate import analyze_audio_file, generate_music_clip
    from app.humming import (
        extract_melody_events,
        preprocess_humming_wav,
        save_melody_events_json,
        save_melody_events_midi,
    )
except ModuleNotFoundError:
    from config import MODEL_ID, get_device
    from generate import analyze_audio_file, generate_music_clip
    from humming import (
        extract_melody_events,
        preprocess_humming_wav,
        save_melody_events_json,
        save_melody_events_midi,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline local text-to-music prototype")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Lo-fi chill beat with soft piano and warm bass, relaxing nighttime mood",
        help="Text prompt for generation",
    )
    parser.add_argument("--duration", type=int, default=8, help="Clip duration in seconds")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    parser.add_argument(
        "--humming-wav",
        type=str,
        default=None,
        help="Optional path to a humming/whistling WAV for preprocessing.",
    )
    parser.add_argument(
        "--humming-target-sr",
        type=int,
        default=32000,
        help="Target sample rate for humming preprocessing.",
    )
    parser.add_argument(
        "--melody-out",
        type=str,
        default=None,
        help="Optional JSON path to save extracted melody events.",
    )
    parser.add_argument(
        "--melody-midi-out",
        type=str,
        default=None,
        help="Optional MIDI path to save extracted melody events as .mid.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_prompt = args.prompt

    try:
        if args.humming_wav:
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

            if args.melody_out:
                saved = save_melody_events_json(melody_events, Path(args.melody_out))
                print(f"Saved melody events JSON: {saved.resolve()}")

            if args.melody_midi_out:
                saved_midi = save_melody_events_midi(melody_events, Path(args.melody_midi_out))
                print(f"Saved melody events MIDI: {saved_midi.resolve()}")
            return

        device = get_device()
        print(f"Model ID: {MODEL_ID}")
        print(f"Detected device: {device}")
        print(f"Prompt: {sample_prompt}")
        print(f"Duration (s): {args.duration}")
        print(f"Seed: {args.seed}")

        output_path = generate_music_clip(
            prompt=sample_prompt,
            duration_seconds=args.duration,
            seed=args.seed,
        )
        print(f"Saved generated audio to: {output_path}")
        print(f"File exists: {output_path.exists()}")

        analysis = analyze_audio_file(output_path)
        print(f"Estimated BPM: {analysis['bpm']}")
        print(f"Estimated Key/Scale: {analysis['key']} {analysis['scale']}")
    except Exception as exc:
        print(f"Generation failed: {exc}")
        raise


if __name__ == "__main__":
    main()
