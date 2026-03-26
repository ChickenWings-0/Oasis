from realesrgan import RealESRGANer
from basicsr.archs.srvgg_arch import SRVGGNetCompact
from PIL import Image
import torch
import numpy as np
import cv2


_model = None


def load_upscaler():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_path = "models/realesr-general-x4v3.pth"

    model = SRVGGNetCompact(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_conv=32,
        upscale=4,
        act_type='prelu'
    )

    upscaler = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=model,
        dni_weight=None,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=True if device == "cuda" else False,
    )
    return upscaler


def upscale_frames(frames):
    model = load_upscaler()
    upscaled = []

    for i, frame in enumerate(frames):
        print(f"Upscaling frame {i+1}/{len(frames)}...")
        if frame is None:
            continue
        frame = frame.convert("RGB")
        with torch.no_grad():
            # Convert PIL -> numpy (RGB -> BGR)
            frame_np = np.array(frame)
            frame_np = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

            # Upscale
            sr_image, _ = model.enhance(frame_np, outscale=2)

            # Convert back (BGR -> RGB -> PIL)
            sr_image = cv2.cvtColor(sr_image, cv2.COLOR_BGR2RGB)
            sr_image = Image.fromarray(sr_image)
        upscaled.append(sr_image)

    return upscaled
