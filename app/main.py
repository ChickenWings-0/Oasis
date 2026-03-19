from __future__ import annotations

try:
    from app.config import MODEL_ID, get_device
    from app.generate import analyze_audio_file, generate_music_clip
except ModuleNotFoundError:
    from config import MODEL_ID, get_device
    from generate import analyze_audio_file, generate_music_clip


def main() -> None:
    sample_prompt = "Lo-fi chill beat with soft piano and warm bass, relaxing nighttime mood"

    try:
        device = get_device()
        print(f"Model ID: {MODEL_ID}")
        print(f"Detected device: {device}")
        print(f"Prompt: {sample_prompt}")

        output_path = generate_music_clip(prompt=sample_prompt)
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
