from core.models import PromptPlan
from core.camera_motion import get_camera_transform
from core.controlnet_utils import get_depth_image
from PIL import Image
import cv2
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


def match_color(prev, curr):
    matched = np.empty_like(curr)

    for c in range(3):
        src = curr[:, :, c].ravel()
        ref = prev[:, :, c].ravel()

        src_values, src_idx, src_counts = np.unique(src, return_inverse=True, return_counts=True)
        ref_values, ref_counts = np.unique(ref, return_counts=True)

        src_quantiles = np.cumsum(src_counts).astype(np.float64)
        src_quantiles /= src_quantiles[-1]
        ref_quantiles = np.cumsum(ref_counts).astype(np.float64)
        ref_quantiles /= ref_quantiles[-1]

        interp_ref_values = np.interp(src_quantiles, ref_quantiles, ref_values)
        matched[:, :, c] = interp_ref_values[src_idx].reshape(curr[:, :, c].shape).astype(np.uint8)

    prev_mean, prev_std = prev.mean(axis=(0, 1)), prev.std(axis=(0, 1))
    matched_mean, matched_std = matched.mean(axis=(0, 1)), matched.std(axis=(0, 1))
    normalized = (matched.astype(np.float32) - matched_mean) * (prev_std / (matched_std + 1e-6)) + prev_mean
    return np.clip(normalized, 0, 255).astype(np.uint8)


def warp_frame_with_flow(prev_frame: Image.Image, target_frame: Image.Image) -> Image.Image:
    prev_np = np.array(prev_frame.convert("RGB"))
    target_np = np.array(target_frame.convert("RGB"))

    prev_gray = cv2.cvtColor(prev_np, cv2.COLOR_RGB2GRAY)
    target_gray = cv2.cvtColor(target_np, cv2.COLOR_RGB2GRAY)

    flow = cv2.calcOpticalFlowFarneback(
        prev_gray,
        target_gray,
        None,
        0.5,
        3,
        21,
        3,
        5,
        1.2,
        0
    )

    h, w = prev_gray.shape
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (grid_x + flow[:, :, 0]).astype(np.float32)
    map_y = (grid_y + flow[:, :, 1]).astype(np.float32)

    warped = cv2.remap(
        prev_np,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    return Image.fromarray(warped)


def extract_identity_embedding(image: Image.Image) -> np.ndarray:
    image_np = np.array(image.convert("RGB"), dtype=np.float32)
    small = cv2.resize(image_np, (32, 32), interpolation=cv2.INTER_AREA)
    embedding = small.reshape(-1)
    norm = np.linalg.norm(embedding) + 1e-6
    return embedding / norm


def enforce_identity_consistency(
    image: Image.Image,
    identity_reference: Image.Image,
    identity_embedding: np.ndarray,
    min_similarity: float = 0.90
) -> Image.Image:
    current_embedding = extract_identity_embedding(image)
    similarity = float(np.dot(identity_embedding, current_embedding))

    if similarity >= min_similarity:
        return image

    current_np = np.array(image).astype(np.float32)
    reference_np = np.array(identity_reference).astype(np.float32)
    corrected = np.clip(0.85 * current_np + 0.15 * reference_np, 0, 255).astype(np.uint8)
    return Image.fromarray(corrected)


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
    identity_reference = keyframes[0]
    identity_embedding = extract_identity_embedding(identity_reference)
    base_seed = prompt_plan.seed if prompt_plan.seed is not None else 42
    seed = base_seed
    generator = torch.Generator(device=device).manual_seed(seed)

    for k in range(len(keyframes) - 1):
        start_frame = keyframes[k]
        end_frame = keyframes[k + 1]
        prev_frame = start_frame

        for i in range(1, CHUNK_SIZE):
            global_i = k * CHUNK_SIZE + i
            if global_i >= prompt_plan.num_frames:
                break

            transform = get_camera_transform(
                prompt_plan.motion_preset,
                global_i,
                prompt_plan.num_frames
            )

            if i < 3:
                strength = 0.55
            else:
                strength = 0.35
            strength = max(0.25, min(0.6, strength))

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

            if i == 1:
                temporal_reference = identity_reference
            else:
                temporal_reference = Image.blend(identity_reference, prev_frame, 0.2)

            warped_prev = apply_transform(prev_frame, transform)
            warped_prev = warp_frame_with_flow(warped_prev, transformed)

            if controlnet_pipe is not None:
                image = controlnet_pipe(
                    prompt=prompt_plan.enhanced_prompt,
                    negative_prompt=prompt_plan.negative_prompt,
                    image=warped_prev,
                    control_image=depth_image,
                    ip_adapter_image=temporal_reference,
                    controlnet_conditioning_scale=prompt_plan.controlnet_conditioning_scale,
                    strength=strength,
                    guidance_scale=prompt_plan.guidance_scale,
                    num_inference_steps=prompt_plan.num_inference_steps,
                    generator=generator
                ).images[0]
            else:
                image = transformed

            curr_np = np.array(image)

            if i > 1:
                prev_np = np.array(prev_frame)
                stabilized = match_color(prev_np, curr_np)
                image = Image.fromarray(stabilized)
            else:
                curr_np = np.clip(curr_np, 0, 255).astype(np.uint8)
                image = Image.fromarray(curr_np)

            image = enforce_identity_consistency(image, identity_reference, identity_embedding)

            if i > 1:
                image = Image.blend(prev_frame, image, 0.85)

            frames.append(image)
            prev_frame = image

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
    seed = base_seed
    generator = torch.Generator(device=device).manual_seed(seed)

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

    if controlnet_pipe is not None:
        controlnet_pipe.load_ip_adapter(
            "h94/IP-Adapter",
            subfolder="models",
            weight_name="ip-adapter_sd15.bin"
        )
        controlnet_pipe.set_ip_adapter_scale(0.5)

    identity_reference = first
    identity_embedding = extract_identity_embedding(identity_reference)
    prev_frame = first
    target = first

    # generate sequence
    for i in range(1, prompt_plan.num_frames):
        print(f"Generating frame {i+1}/{prompt_plan.num_frames}")

        transform = get_camera_transform(
            prompt_plan.motion_preset,
            i,
            prompt_plan.num_frames
        )

        transformed = apply_transform(target, transform)

        t = i / (prompt_plan.num_frames - 1) if prompt_plan.num_frames > 1 else 0
        strength = 0.35 + 0.1 * np.sin(t * np.pi)
        strength = max(0.25, min(0.6, strength))

        canny = get_depth_image(transformed)

        if i == 1:
            temporal_reference = identity_reference
        else:
            temporal_reference = Image.blend(identity_reference, prev_frame, 0.2)

        warped_prev = warp_frame_with_flow(prev_frame, transformed)

        if controlnet_pipe is not None:
            # always use controlnet
            image = controlnet_pipe(
                prompt=prompt_plan.enhanced_prompt,
                negative_prompt=prompt_plan.negative_prompt,
                image=warped_prev,
                control_image=canny,
                ip_adapter_image=temporal_reference,
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

        curr_np = np.array(image)

        if i > 1:
            prev_np = np.array(prev_frame)
            stabilized = match_color(prev_np, curr_np)
            image = Image.fromarray(stabilized)
        else:
            curr_np = np.clip(curr_np, 0, 255).astype(np.uint8)
            image = Image.fromarray(curr_np)

        image = enforce_identity_consistency(image, identity_reference, identity_embedding)

        if i > 1:
            image = Image.blend(prev_frame, image, 0.85)

        prev_frame = image
        target = image

        frames.append(image)

    return frames
