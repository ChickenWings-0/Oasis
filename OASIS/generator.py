import random
from typing import List

import numpy as np
import streamlit as st
import torch
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
from PIL import Image
from prompt_engine import PromptSchedule


MODEL_ID = "runwayml/stable-diffusion-v1-5"


def shift_frame_for_motion(frame, motion_type, frame_index, total_frames):
    width, height = frame.size
    frame_np = np.array(frame)

    shift = int((frame_index / total_frames) * 40)
    if shift <= 0:
        return frame

    if motion_type == "pan_right":
        shifted = np.roll(frame_np, -shift, axis=1)
        shifted[:, -shift:, :] = np.random.randint(0, 255, (height, shift, 3), dtype=np.uint8)
    elif motion_type == "pan_left":
        shifted = np.roll(frame_np, shift, axis=1)
        shifted[:, :shift, :] = np.random.randint(0, 255, (height, shift, 3), dtype=np.uint8)
    else:
        return frame

    return Image.fromarray(shifted)


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

    if hasattr(text2img_pipe, "enable_vae_slicing"):
        text2img_pipe.enable_vae_slicing()

    if hasattr(img2img_pipe, "enable_vae_slicing"):
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
        guidance_scale = 6.5
        num_inference_steps = 35
        style_strength = 0.65
    elif style == "realistic":
        style_prompt = "photorealistic, natural lighting, DSLR, 35mm lens, subtle colors"
        negative_prompt = "anime, cartoon, illustration, exaggerated colors"
        guidance_scale = 6.5
        num_inference_steps = 28
        style_strength = 0.5
    else:
        style_prompt = "cinematic lighting, high contrast, dramatic shadows, film still, volumetric lighting, film grain"
        negative_prompt = "flat lighting, cartoon, anime"
        guidance_scale = 6.5
        num_inference_steps = 32
        style_strength = 0.6
    negative_prompt += ", blurry, distorted, warped, deformed, text mutation"
    if motion_level == "low":
        adjusted_strength = 0.20
    elif motion_level == "medium":
        adjusted_strength = 0.24
    else:
        adjusted_strength = 0.28

    frames: List[Image.Image] = []
    for i in range(num_frames):
        print(f"Generating frame {i + 1}/{num_frames}...")
        if prompt_schedule:
            current_prompt = prompt_schedule.get_prompt(i)
        else:
            current_prompt = prompt
        enhanced_prompt = f"{current_prompt}, {style_prompt}, same scene, consistent composition, stable object, no distortion, clear details"
        seed = base_seed + i * 2
        generator = torch.Generator(device="cuda").manual_seed(seed)

        if i == 0:
            image = text2img_pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
                return_dict=True,
            ).images[0]
            image = image.resize((width, height))
        else:
            source_image = frames[-1]
            source_image = shift_frame_for_motion(
                source_image,
                motion_type,
                i,
                num_frames,
            )
            source_image = Image.blend(source_image, frames[0], 0.15)
            # Ensure img2img source uses the configured resolution.
            source_image = source_image.resize((width, height))
            image = img2img_pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                image=source_image,
                strength=adjusted_strength,
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
                return_dict=True,
            ).images[0]

        image = image.resize((width, height))
        image = np.array(image)
        image = np.clip(image, 0, 255).astype(np.uint8)
        image = Image.fromarray(image)
        frames.append(image)

    return frames
