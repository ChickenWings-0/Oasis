from pathlib import Path
from typing import List, Optional

from PIL import Image


def save_frames(frames: List[Image.Image], output_dir: Optional[str] = None) -> None:
    """Save generated frames as frame_000.png, frame_001.png, ..."""
    if not frames:
        raise ValueError("frames cannot be empty.")

    target_dir = Path(output_dir) if output_dir else Path("outputs/frames")
    target_dir.mkdir(parents=True, exist_ok=True)

    for i, frame in enumerate(frames):
        frame_path = target_dir / f"frame_{i:03d}.png"
        frame.save(frame_path)


def blend_frames(frames: List[Image.Image], alpha: float = 0.7) -> List[Image.Image]:
    if not frames:
        return []

    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be between 0.0 and 1.0")

    blended_frames: List[Image.Image] = [frames[0].copy()]
    for i in range(1, len(frames)):
        prev = blended_frames[-1].convert("RGB")
        curr = frames[i].convert("RGB")
        blended = Image.blend(prev, curr, alpha)
        blended_frames.append(blended)

    return blended_frames
