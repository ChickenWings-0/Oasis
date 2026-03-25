import random
from typing import List

import torch
from diffusers import StableDiffusionImg2ImgPipeline, StableDiffusionPipeline
from PIL import Image


MODEL_ID = "runwayml/stable-diffusion-v1-5"


def generate_frames(
    prompt: str,
    num_frames: int,
    motion_level: str = "medium",
    style: str = "cinematic",
    width: int = 256,
    height: int = 256,
) -> List[Image.Image]:
    """Generate a list of frames from a text prompt using Stable Diffusion v1.5."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if num_frames < 1:
        raise ValueError("num_frames must be at least 1.")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for Phase 1.")

    print("Loading model...")
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
        strength = 0.65
    elif style == "realistic":
        style_prompt = "photorealistic, natural lighting, DSLR, 35mm lens, subtle colors"
        negative_prompt = "anime, cartoon, illustration, exaggerated colors"
        guidance_scale = 5.5
        num_inference_steps = 28
        strength = 0.5
    else:
        style_prompt = "cinematic lighting, high contrast, dramatic shadows, film still, volumetric lighting, film grain"
        negative_prompt = "flat lighting, cartoon, anime"
        guidance_scale = 7.5
        num_inference_steps = 32
        strength = 0.6
    enhanced_prompt = f"{prompt}, {style_prompt}, same scene, consistent lighting, same camera angle, highly detailed"
    if motion_level == "low":
        motion_adjustment = -0.1
    elif motion_level == "high":
        motion_adjustment = 0.1
    else:
        motion_adjustment = 0.0
    final_strength = max(0.0, min(1.0, strength + motion_adjustment))

    frames: List[Image.Image] = []
    for i in range(num_frames):
        print(f"Generating frame {i + 1}/{num_frames}...")
        seed = base_seed + i
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
            ).images[0]
        else:
            image = img2img_pipe(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                image=frames[-1],
                strength=final_strength,
                generator=generator,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
            ).images[0]
        frames.append(image)

    return frames
