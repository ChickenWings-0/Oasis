from pathlib import Path
import subprocess

import cv2


def convert_to_web_video(input_path: str, output_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-vcodec",
        "libx264",
        "-acodec",
        "aac",
        output_path,
    ]
    subprocess.run(cmd, check=True)


def create_video_from_frames(frame_dir: str, output_path: str, fps: int = 6) -> None:
    frame_path = Path(frame_dir)
    if not frame_path.exists() or not frame_path.is_dir():
        raise ValueError(f"Frame directory not found: {frame_dir}")

    image_files = sorted(frame_path.glob("*.png"))
    if not image_files:
        raise ValueError(f"No PNG frames found in: {frame_dir}")

    first_frame = cv2.imread(str(image_files[0]))
    if first_frame is None:
        raise ValueError(f"Could not read first frame: {image_files[0]}")

    height, width, _ = first_frame.shape

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_path = str(output_file).replace(".mp4", "_temp.mp4")

    writer = cv2.VideoWriter(
        temp_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for: {output_path}")

    try:
        for image_file in image_files:
            frame = cv2.imread(str(image_file))
            if frame is None:
                raise ValueError(f"Could not read frame: {image_file}")
            writer.write(frame)
    finally:
        writer.release()

    convert_to_web_video(temp_path, str(output_file))
