from pathlib import Path
import subprocess
from datetime import datetime

from utils import get_output_dir


def get_music_style(prompt: str) -> str:
    """
    Suggest music style based on prompt.
    """
    prompt_lower = prompt.lower()

    if "cyberpunk" in prompt_lower:
        return "synthwave"
    elif "fantasy" in prompt_lower:
        return "orchestral"
    elif "anime" in prompt_lower:
        return "jpop"
    else:
        return "ambient"


def generate_music(prompt: str, style: str) -> str:
    base_dir = get_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_dir = base_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    output_path = audio_dir / f"music_{style}_{timestamp}.wav"

    # TEMP FIX: generate silent audio if real module not connected
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=stereo",
                "-t",
                "10",
                str(output_path),
            ],
            check=True,
        )
    except Exception as e:
        print(f"Audio generation failed: {e}")

    return str(output_path)


def combine_video_music(video_path: str, audio_path: str, output_path: str) -> str:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"FFmpeg error: {e}")
        return video_path

    return output_path
