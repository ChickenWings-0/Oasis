from typing import List

import cv2
import numpy as np
import streamlit as st
import torch
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
from PIL import Image
from prompt_engine import PromptSchedule

torch.backends.cudnn.benchmark = True


MODEL_ID = "runwayml/stable-diffusion-v1-5"


def get_canny(image):
    image = np.array(image)
    edges = cv2.Canny(image, 100, 200)
    edges = np.stack([edges] * 3, axis=-1)
    return Image.fromarray(edges)


@st.cache_resource
def load_pipeline():
    controlnet = ControlNetModel.from_pretrained(
        "models/controlnet-canny",
        torch_dtype=torch.float16,
    )
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        MODEL_ID,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        safety_checker=None,
    ).to("cuda")
    pipe.enable_attention_slicing()
    return pipe


def generate_frames(
    prompt: str,
    num_frames: int,
    motion_level: str = "medium",
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
    pipe = load_pipeline()

    try:
        pipe.enable_xformers_memory_efficient_attention()
    except:
        pass

    num_inference_steps = 20
    if style == "anime":
        style_prompt = "anime style, cel shading, bold outlines, flat shading, vibrant colors, 2D animation frame"
        negative_prompt = "photorealistic, realistic lighting, shadows, dull colors"
        guidance_scale = 6.5
        style_strength = 0.65
    elif style == "realistic":
        style_prompt = "photorealistic, natural lighting, DSLR, 35mm lens, subtle colors"
        negative_prompt = "anime, cartoon, illustration, exaggerated colors"
        guidance_scale = 6.5
        style_strength = 0.5
    else:
        style_prompt = "cinematic lighting, high contrast, dramatic shadows, film still, volumetric lighting, film grain"
        negative_prompt = "flat lighting, cartoon, anime"
        guidance_scale = 6.5
    negative_prompt += ", blurry, distorted, warped, deformed, text mutation"

    frames: List[Image.Image] = []
    for i in range(num_frames):
        print(f"Generating frame {i + 1}/{num_frames}...")
        if prompt_schedule:
            current_prompt = prompt_schedule.get_prompt(i)
        else:
            current_prompt = prompt
        enhanced_prompt = f"{current_prompt}, {style_prompt}, same scene, consistent composition, stable object, no distortion, clear details"

        if i == 0:
            control_image = Image.new("RGB", (width, height), "black")
        else:
            control_image = get_canny(frames[-1])

        image = pipe(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        ).images[0]

        image = image.resize((width, height))
        frames.append(image)

    return frames
