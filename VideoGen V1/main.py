from datetime import datetime
from pathlib import Path

from generator import generate_frames
from music_integration import combine_video_music, generate_music
from renderer import create_video_from_frames
from utils import get_output_dir, save_frames


def main() -> None:
    base_dir = get_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame_dir = base_dir / "frames" / f"run_{timestamp}"
    frame_dir.mkdir(parents=True, exist_ok=True)

    prompt = input("Enter prompt: ").strip()
    if not prompt:
        print("Prompt cannot be empty.")
        return

    frame_count_input = input("Enter number of frames (default 8): ").strip()
    if frame_count_input:
        try:
            num_frames = int(frame_count_input)
            if num_frames < 1:
                print("Frame count must be at least 1. Using default 8.")
                num_frames = 8
        except ValueError:
            print("Invalid frame count. Using default 8.")
            num_frames = 8
    else:
        num_frames = 8

    resolution_input = input(
        "Select resolution: 1) 384x384 (balanced), 2) 512x512 (high quality), 3) 768x768 (ultra quality), 4) 1080p (upscaled) [default 1]: "
    ).strip()
    if resolution_input == "1":
        width, height = 384, 384
        upscale_factor = 1
    elif resolution_input == "2":
        width, height = 512, 512
        upscale_factor = 1
    elif resolution_input == "3":
        width, height = 768, 768
        upscale_factor = 1
    elif resolution_input == "4":
        width, height = 768, 768
        upscale_factor = 2
    else:
        width, height = 384, 384
        upscale_factor = 1

    try:
        motion_level = "medium"
        style = "cinematic"
        frames = generate_frames(
            prompt=prompt,
            num_frames=num_frames,
            motion_level=motion_level,
            style=style,
            width=width,
            height=height,
        )
        if upscale_factor > 1:
            from upscaler import upscale_frames
            print("Upscaling frames for high resolution output...")
            frames = upscale_frames(
                frames,
                target_size=(1920, 1080)
            )
        save_frames(frames, str(frame_dir))

        video_dir = base_dir / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)

        video_path = str(video_dir / f"video_{timestamp}.mp4")
        create_video_from_frames(str(frame_dir), video_path)

        print(f"Video saved at: {video_path}")

        choice = input("Generate music? (y/n): ").strip().lower()

        if choice == "y":
            use_custom = input("Use custom audio prompt? (y/n): ").strip().lower()

            if use_custom == "y":
                audio_prompt = input("Enter audio prompt: ").strip()
            else:
                audio_prompt = prompt

            audio_path = generate_music(audio_prompt)

            final_output = str(video_dir / f"final_{timestamp}.mp4")

            combine_video_music(video_path, audio_path, final_output)

            print(f"Final video with music saved at: {final_output}")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
