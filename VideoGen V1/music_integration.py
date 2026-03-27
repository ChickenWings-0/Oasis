import sys
from pathlib import Path
import subprocess
from datetime import datetime

from utils import get_output_dir


# Add oasis_music_module to path
current = Path(__file__).resolve()
music_root = None

for parent in [current.parent, *current.parents]:
    candidate = parent / "oasis_music_module"
    if candidate.exists():
        music_root = candidate
        break

if music_root is None:
    raise RuntimeError("oasis_music_module not found")

# DEBUG (leave for now)
print("Music root:", music_root)
print("Contents:", list(music_root.iterdir()))

if str(music_root) not in sys.path:
    sys.path.insert(0, str(music_root))

from app.generate import generate_music_clip


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


def build_music_prompt(prompt: str, style: str) -> str:
    style_map = {
        "synthwave": "retro electronic synthwave, atmospheric, cyberpunk vibe",
        "ambient": "soft ambient soundscape, calm, atmospheric",
        "orchestral": "cinematic orchestral music, strings, epic",
        "jpop": "upbeat japanese pop music, anime style",
        "dark_ambient": "dark ambient, horror atmosphere, deep textures",
    }

    style_desc = style_map.get(style, "ambient background music")

    return f"{style_desc}, inspired by: {prompt}"


def generate_music(prompt: str) -> str:
    base_dir = get_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_dir = base_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    try:
        output_path = generate_music_clip(
            prompt=prompt,
            duration_seconds=10,
        )

        return str(output_path)

    except Exception as e:
        print(f"Music module failed: {e}")
        return None


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
