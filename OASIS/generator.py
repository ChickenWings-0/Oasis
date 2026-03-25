import random
from typing import List

import streamlit as st
import torch
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
from PIL import Image
from motion import apply_camera_motion
from prompt_engine import PromptSchedule


MODEL_ID = "runwayml/stable-diffusion-v1-5"


@st.cache_resource
def load_pipelines():
    text2img_pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
    ).to("cuda")

    img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
    ).to("cuda")

    return text2img_pipe, img2img_pipe


def generate_frames(
    prompt: str,
    num_frames: int,
    motion_level: str = "medium",
    motion_type: str = "none",
    style: str = "cinematic",
    width: int = 256,
    height: int = 256,
    prompt_schedule=None,
) -> List[Image.Image]:
    """Generate a list of frames from a text prompt using Stable Diffusion v1.5."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if num_frames < 1:
        raise ValueError("num_frames must be at least 1.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for Phase 1.")

    print("Loading model...")
    text2img_pipe, img2img_pipe = load_pipelines()
    text2img_pipe.enable_attention_slicing()
    img2img_pipe.enable_attention_slicing()

    text2img_pipe.enable_vae_slicing()
    img2img_pipe.enable_vae_slicing()

    try:
        text2img_pipe.enable_xformers_memory_efficient_attention()
        img2img_pipe.enable_xformers_memory_efficient_attention()
    except:
        pass
    base_seed = random.randint(0, 100000)
    if style == "anime":
        style_prompt = "anime style, cel shading, bold outlines, flat shading, vibrant colors, 2D animation frame"
        negative_prompt = "photorealistic, realistic lighting, shadows, dull colors"
        guidance_scale = 8.5
        num_inference_steps = 35
        style_strength = 0.65
    elif style == "realistic":
        style_prompt = "photorealistic, natural lighting, DSLR, 35mm lens, subtle colors"
        negative_prompt = "anime, cartoon, illustration, exaggerated colors"
        guidance_scale = 5.5
        num_inference_steps = 28
        style_strength = 0.5
    else:
        style_prompt = "cinematic lighting, high contrast, dramatic shadows, film still, volumetric lighting, film grain"
        negative_prompt = "flat lighting, cartoon, anime"
        guidance_scale = 7.5
        num_inference_steps = 32
        style_strength = 0.6
    base_strength = style_strength
    if motion_level == "low":
        strength = base_strength - 0.1
    elif motion_level == "high":
        strength = base_strength + 0.1
    else:
        strength = base_strength
    strength = max(0.3, min(0.8, strength))

    frames: List[Image.Image] = []
    for i in range(num_frames):
        print(f"Generating frame {i + 1}/{num_frames}...")
        if prompt_schedule:
            current_prompt = prompt_schedule.get_prompt(i)
        else:
            current_prompt = prompt
        enhanced_prompt = f"{current_prompt}, {style_prompt}, same scene, same composition, consistent lighting"
        seed = base_seed + i
        generator = torch.Generator(device="cuda").manual_seed(seed)
        decay = 1.0 - (i / num_frames) * 0.3
        adjusted_strength = strength * decay
        adjusted_strength = max(0.32, min(0.5, adjusted_strength))

        if i == 0:
            image = text2img_pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
            ).images[0]
        else:
            # Blend prior frame with the first frame to prevent cumulative artifact drift.
            source_image = Image.blend(frames[-1], frames[0], 0.3)
            image = img2img_pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                image=source_image,
                strength=adjusted_strength,
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
            ).images[0]

        image = apply_camera_motion(image, i, num_frames, motion_type)
        frames.append(image)

    return frames
