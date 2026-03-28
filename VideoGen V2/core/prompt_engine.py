from core.models import PromptPlan
from typing import Optional, Dict
import random
import re


MOTION_KEYWORDS = {
    "driving": {
        "tokens": "car moving, motion blur, forward movement",
        "suggested_motion": "pan_right",
    },
    "flying": {
        "tokens": "flying, aerial motion, dynamic movement",
        "suggested_motion": "zoom_out",
    },
    "walking": {
        "tokens": "walking, forward motion",
        "suggested_motion": "pan_right",
    },
    "running": {
        "tokens": "fast motion, motion blur",
        "suggested_motion": "pan_right",
    },
    "floating": {
        "tokens": "floating, slow drift",
        "suggested_motion": "breathe",
    },
}

ENVIRONMENT_KEYWORDS = {
    "city": "urban environment, buildings, streets",
    "forest": "trees, nature, dense forest",
    "ocean": "water, waves, horizon",
    "space": "stars, galaxy, cosmic background",
}

LIGHTING_KEYWORDS = {
    "night": "dark, night lighting, low light",
    "sunset": "warm lighting, orange tones",
    "neon": "neon lights, vibrant glow",
    "cinematic": "dramatic lighting, high contrast",
}

STYLE_CONFIGS = {
    "cinematic": {
        "positive": "cinematic lighting, high contrast, volumetric light, film still",
        "negative": "cartoon, anime, low quality, blurry",
        "guidance_scale": 6.5,
        "img2img_strength": 0.45,
        "controlnet_scale": 0.8,
    },
    "anime": {
        "positive": "anime style, cel shading, vibrant colors",
        "negative": "realistic, photorealistic, dull colors",
        "guidance_scale": 7.0,
        "img2img_strength": 0.5,
        "controlnet_scale": 0.85,
    },
    "realistic": {
        "positive": "photorealistic, natural lighting, DSLR",
        "negative": "anime, cartoon, illustration",
        "guidance_scale": 6.0,
        "img2img_strength": 0.4,
        "controlnet_scale": 0.75,
    },
}


def detect_keywords(prompt: str) -> Dict:
    prompt_lower = prompt.lower()

    detected = {
        "motion_tokens": [],
        "environment_tokens": [],
        "lighting_tokens": [],
        "suggested_motion": None,
    }

    for key, value in MOTION_KEYWORDS.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, prompt_lower):
            detected["motion_tokens"].append(value["tokens"])
            if detected["suggested_motion"] is None:
                detected["suggested_motion"] = value["suggested_motion"]

    for key, value in ENVIRONMENT_KEYWORDS.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, prompt_lower):
            detected["environment_tokens"].append(value)

    for key, value in LIGHTING_KEYWORDS.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, prompt_lower):
            detected["lighting_tokens"].append(value)

    return detected


def build_enhanced_prompt(user_prompt: str, detected: Dict, style_config: Dict) -> str:
    components = []

    components.append(user_prompt)

    if detected["motion_tokens"]:
        components.append("motion: " + ", ".join(detected["motion_tokens"]))

    if detected["environment_tokens"]:
        components.append("environment: " + ", ".join(detected["environment_tokens"]))

    if detected["lighting_tokens"]:
        components.append("lighting: " + ", ".join(detected["lighting_tokens"]))

    components.append(style_config["positive"])

    components.append("consistent scene, temporal coherence, same composition, stable objects")

    return ", ".join(components)


def build_negative_prompt(style_config: Dict) -> str:
    return ", ".join([
        style_config["negative"],
        "frame jump, inconsistent frames, flickering, temporal instability",
        "different scene, changing composition, morphing objects",
        "distorted, low detail, blurry, artifacts"
    ])


def resolve_motion(motion_preset: str, detected_motion: Optional[str]) -> str:
    if motion_preset == "auto":
        return detected_motion if detected_motion else "breathe"
    return motion_preset


def create_prompt_plan(
    user_prompt: str,
    style: str = "cinematic",
    motion_preset: str = "auto",
    seed: Optional[int] = None,
    num_frames: int = 16,
    width: int = 512,
    height: int = 512,
) -> PromptPlan:
    detected = detect_keywords(user_prompt)

    style_config = STYLE_CONFIGS.get(style, STYLE_CONFIGS["cinematic"])

    enhanced_prompt = build_enhanced_prompt(user_prompt, detected, style_config)

    negative_prompt = build_negative_prompt(style_config)

    motion = resolve_motion(motion_preset, detected["suggested_motion"])

    if seed is None:
        seed = random.randint(0, 1_000_000)

    return PromptPlan(
        base_prompt=user_prompt,
        enhanced_prompt=enhanced_prompt,
        negative_prompt=negative_prompt,
        style=style,
        motion_preset=motion,
        num_frames=num_frames,
        width=width,
        height=height,
        seed=seed,
        guidance_scale=style_config["guidance_scale"],
        img2img_strength=style_config["img2img_strength"],
        controlnet_conditioning_scale=style_config["controlnet_scale"],
    )
