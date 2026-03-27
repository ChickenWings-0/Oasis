from core.models import PromptPlan
from core.camera_motion import get_camera_transform
from core.controlnet_utils import get_depth_image
from PIL import Image
import numpy as np
import torch
import math


def apply_transform(image: Image.Image, transform) -> Image.Image:
    width, height = image.size

    # Never allow zoom-out below the source size to avoid empty regions.
    scale = max(float(transform.scale), 1.0)
    new_w = max(int(round(width * scale)), width)
    new_h = max(int(round(height * scale)), height)
    scaled = image.resize((new_w, new_h), Image.LANCZOS)

    # Center crop origin on the scaled canvas.
    base_left = (new_w - width) // 2
    base_top = (new_h - height) // 2

    # Requested translation in source pixels, clamped to motion policy.
    shift_x = int(transform.translate_x * width)
    shift_y = int(transform.translate_y * height)
    shift_x = max(min(shift_x, width // 6), -width // 6)
    shift_y = max(min(shift_y, height // 6), -height // 6)

    # Further clamp by available margins so crop never leaves scaled image.
    max_x = min(width // 6, base_left)
    max_y = min(height // 6, base_top)
    shift_x = max(min(shift_x, max_x), -max_x)
    shift_y = max(min(shift_y, max_y), -max_y)

    left = base_left + shift_x
    top = base_top + shift_y

    return scaled.crop((left, top, left + width, top + height))


def generate_keyframes(prompt_plan, text2img_pipe, num_frames, device):
    CHUNK_SIZE = 28
    keyframes = []

    base_seed = prompt_plan.seed if prompt_plan.seed is not None else 42

    for k, _ in enumerate(range(0, num_frames, CHUNK_SIZE)):
        seed = base_seed + k * 1000
        generator = torch.Generator(device=device).manual_seed(seed)

        keyframe = text2img_pipe(
            prompt=prompt_plan.enhanced_prompt,
            negative_prompt=prompt_plan.negative_prompt,
            guidance_scale=prompt_plan.guidance_scale,
            num_inference_steps=prompt_plan.num_inference_steps,
            width=prompt_plan.width,
            height=prompt_plan.height,
            generator=generator
        ).images[0]

        keyframes.append(keyframe)

    return keyframes


def generate_frames_chunked(prompt_plan, text2img_pipe, controlnet_pipe, device):
    CHUNK_SIZE = 28
    keyframes = generate_keyframes(prompt_plan, text2img_pipe, prompt_plan.num_frames, device)

    if not keyframes:
        return []

    frames = [keyframes[0]]
    base_seed = prompt_plan.seed if prompt_plan.seed is not None else 42

    for k in range(len(keyframes) - 1):
        start_frame = keyframes[k]
        end_frame = keyframes[k + 1]

        for i in range(1, CHUNK_SIZE):
            global_i = k * CHUNK_SIZE + i
            if global_i >= prompt_plan.num_frames:
                break

            transform = get_camera_transform(
                prompt_plan.motion_preset,
                global_i,
                prompt_plan.num_frames
            )

            seed = base_seed + (global_i * 3)
            generator = torch.Generator(device=device).manual_seed(seed)

            t = global_i / (prompt_plan.num_frames - 1) if prompt_plan.num_frames > 1 else 0
            strength = 0.35 + 0.1 * np.sin(t * np.pi)

            alpha = i / CHUNK_SIZE

            start_np = np.array(start_frame).astype(np.float32)
            end_np = np.array(end_frame).astype(np.float32)

            target = (1 - alpha) * start_np + alpha * end_np
            target = target.astype(np.uint8)
            target = Image.fromarray(target)

            transformed = apply_transform(target, transform)

            depth_image = get_depth_image(transformed)

            noise = np.random.normal(0, 2, np.array(transformed).shape).astype(np.float32)
            noisy = np.clip(np.array(transformed).astype(np.float32) + noise, 0, 255).astype(np.uint8)
            transformed = Image.fromarray(noisy)

            if controlnet_pipe is not None:
                image = controlnet_pipe(
                    prompt=prompt_plan.enhanced_prompt,
                    negative_prompt=prompt_plan.negative_prompt,
                    image=transformed,
                    control_image=depth_image,
                    controlnet_conditioning_scale=prompt_plan.controlnet_conditioning_scale,
                    strength=strength,
                    guidance_scale=prompt_plan.guidance_scale,
                    num_inference_steps=prompt_plan.num_inference_steps,
                    generator=generator
                ).images[0]
            else:
                image = transformed

            image = np.array(image)
            image = np.clip(image, 0, 255).astype(np.uint8)
            image = Image.fromarray(image)

            frames.append(image)

    if len(frames) < prompt_plan.num_frames:
        frames.append(keyframes[-1])

    return frames


def generate_frames(
    prompt_plan: PromptPlan,
    text2img_pipe,
    img2img_pipe=None,
    controlnet_pipe=None,
    device="cuda"
):
    frames = []

    base_seed = prompt_plan.seed if prompt_plan.seed is not None else 42

    generator = torch.Generator(device=device).manual_seed(base_seed)

    # first frame (text2img)
    first = text2img_pipe(
        prompt=prompt_plan.enhanced_prompt,
        negative_prompt=prompt_plan.negative_prompt,
        guidance_scale=prompt_plan.guidance_scale,
        num_inference_steps=prompt_plan.num_inference_steps,
        width=prompt_plan.width,
        height=prompt_plan.height,
        generator=generator
    ).images[0]

    frames.append(first)

    target = first
    reference_mean = None

    # generate sequence
    for i in range(1, prompt_plan.num_frames):
        print(f"Generating frame {i+1}/{prompt_plan.num_frames}")

        transform = get_camera_transform(
            prompt_plan.motion_preset,
            i,
            prompt_plan.num_frames
        )

        transformed = apply_transform(target, transform)

        seed = base_seed + (i * 3)
        generator = torch.Generator(device=device).manual_seed(seed)

        t = i / (prompt_plan.num_frames - 1) if prompt_plan.num_frames > 1 else 0
        strength = 0.35 + 0.1 * np.sin(t * np.pi)

        canny = get_depth_image(target)

        if controlnet_pipe is not None:
            # always use controlnet
            image = controlnet_pipe(
                prompt=prompt_plan.enhanced_prompt,
                negative_prompt=prompt_plan.negative_prompt,
                image=target,
                control_image=canny,
                controlnet_conditioning_scale=prompt_plan.controlnet_conditioning_scale,
                strength=strength,
                guidance_scale=prompt_plan.guidance_scale,
                num_inference_steps=prompt_plan.num_inference_steps,
                generator=generator
            ).images[0]
        elif img2img_pipe is not None:
            image = img2img_pipe(
                prompt=prompt_plan.enhanced_prompt,
                negative_prompt=prompt_plan.negative_prompt,
                image=transformed,
                strength=strength,
                guidance_scale=prompt_plan.guidance_scale,
                num_inference_steps=prompt_plan.num_inference_steps,
                generator=generator
            ).images[0]
        else:
            image = transformed

        curr = np.array(image).astype(np.float32)

        if reference_mean is None:
            reference_mean = np.mean(curr, axis=(0, 1))

        curr_mean = np.mean(curr, axis=(0, 1))

        scale = reference_mean / (curr_mean + 1e-6)

        curr = curr * scale
        curr = np.clip(curr, 0, 255)

        image = Image.fromarray(curr.astype(np.uint8))
        target = image

        frames.append(image)

    return frames
