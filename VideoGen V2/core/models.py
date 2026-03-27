from dataclasses import dataclass
from typing import Optional, Dict, Tuple


@dataclass
class PromptPlan:
    base_prompt: str
    enhanced_prompt: str
    negative_prompt: str
    prompt_schedule: Optional[Dict[int, str]] = None

    style: str = "cinematic"

    motion_preset: str = "static"
    easing: str = "ease_in_out"

    num_frames: int = 16
    fps: int = 12
    width: int = 512
    height: int = 512
    seed: Optional[int] = None
    guidance_scale: float = 6.5
    num_inference_steps: int = 12
    img2img_strength: float = 0.40
    controlnet_conditioning_scale: float = 0.4

    apply_temporal_smoothing: bool = True
    interpolation_multiplier: int = 2
    upscale_to: Optional[Tuple[int, int]] = None


@dataclass
class CameraTransform:
    translate_x: float = 0.0
    translate_y: float = 0.0
    scale: float = 1.0
    rotate: float = 0.0


@dataclass
class VideoMetrics:
    avg_ssim: float
    flow_smoothness: float
    edge_consistency: float
    prompt_adherence: float
    overall_score: float
