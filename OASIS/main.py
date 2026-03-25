import json
from pathlib import Path

from generator import generate_frames
from renderer import create_video_from_frames
from utils import save_frames


CONFIG_PATH = Path("config.json")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_output_dir() -> str:
    config = load_config()
    output_dir = config.get("output_dir")

    if not output_dir:
        output_dir = input("Enter output directory (e.g., D:/OASIS_OUTPUTS/frames): ").strip()
        if not output_dir:
            output_dir = "outputs/frames/"
        config["output_dir"] = output_dir
        save_config(config)
        return output_dir

    change = input("Change output directory? (y/n): ").strip().lower()
    if change == "y":
        new_output_dir = input("Enter output directory (e.g., D:/OASIS_OUTPUTS/frames): ").strip()
        if new_output_dir:
            config["output_dir"] = new_output_dir
            save_config(config)
            output_dir = new_output_dir

    return output_dir


def main() -> None:
    frame_dir = get_output_dir()

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
        "Select resolution: 1) 256x256 (fast), 2) 384x384 (balanced), 3) 512x512 (high quality) [default 1]: "
    ).strip()
    if resolution_input == "2":
        width, height = 384, 384
    elif resolution_input == "3":
        width, height = 512, 512
    else:
        width, height = 256, 256

    try:
        frames = generate_frames(prompt, num_frames, motion_level, style, width=width, height=height)
        save_frames(frames, frame_dir)

        video_path = str(Path(frame_dir).parent / "output.mp4")
        create_video_from_frames(frame_dir, video_path)

        print(f"Video saved at: {video_path}")
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
