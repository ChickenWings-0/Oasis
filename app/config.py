from __future__ import annotations

from pathlib import Path

import torch

MODEL_ID = "facebook/musicgen-small"
SAMPLE_RATE = 32000
DEFAULT_DURATION_SECONDS = 8
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def get_device() -> str:
    """Return the best available inference device."""
    return "cuda" if torch.cuda.is_available() else "cpu"
