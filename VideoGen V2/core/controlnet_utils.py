from diffusers import ControlNetModel, StableDiffusionControlNetImg2ImgPipeline
import torch
import torch.nn.functional as F
import cv2
import numpy as np
from PIL import Image


_MIDAS_MODEL = None
_MIDAS_TRANSFORM = None
_MIDAS_DEVICE = None


def _get_midas_components():
    global _MIDAS_MODEL, _MIDAS_TRANSFORM, _MIDAS_DEVICE

    if _MIDAS_MODEL is None or _MIDAS_TRANSFORM is None:
        _MIDAS_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        _MIDAS_MODEL = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        _MIDAS_MODEL.to(_MIDAS_DEVICE)
        _MIDAS_MODEL.eval()

        transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        _MIDAS_TRANSFORM = transforms.small_transform

    return _MIDAS_MODEL, _MIDAS_TRANSFORM, _MIDAS_DEVICE


def load_controlnet_pipeline(model_id="runwayml/stable-diffusion-v1-5", device="cuda"):
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-depth",
        torch_dtype=torch.float16
    )

    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
        model_id,
        controlnet=controlnet,
        torch_dtype=torch.float16,
        safety_checker=None
    ).to(device)

    pipe.enable_attention_slicing()

    return pipe


def get_depth_image(image: Image.Image) -> Image.Image:
    image_np = np.array(image.convert("RGB"))
    model, transform, device = _get_midas_components()

    input_batch = transform(image_np).to(device)

    with torch.no_grad():
        prediction = model(input_batch)
        prediction = F.interpolate(
            prediction.unsqueeze(1),
            size=image_np.shape[:2],
            mode="bicubic",
            align_corners=False
        ).squeeze(1).squeeze(0)

    depth = prediction.cpu().numpy()
    depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    depth = depth.astype(np.uint8)
    depth = np.stack([depth] * 3, axis=-1)

    return Image.fromarray(depth)
