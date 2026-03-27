from diffusers import StableDiffusionPipeline
from diffusers import DPMSolverMultistepScheduler
import torch
import os
import cv2
import numpy as np
import time

from core.prompt_engine import create_prompt_plan
from core.frame_engine import generate_frames
from core.controlnet_utils import load_controlnet_pipeline
from utils.video_utils import smooth_frames, interpolate_frames

# ----------------------------

# CONFIG

# ----------------------------

MODEL_ID = "runwayml/stable-diffusion-v1-5"
device = "cuda" if torch.cuda.is_available() else "cpu"

# 🔥 DEBUG GPU

print("CUDA available:", torch.cuda.is_available())
print("Using device:", device)

# ----------------------------

# USER INPUT

# ----------------------------

print("\n=== VideoGen V2 ===\n")

prompt = input("Enter prompt: ") + ", cinematic lighting, realistic colors, high detail, natural color grading"

num_frames = input("Number of frames [default 12]: ")
num_frames = int(num_frames) if num_frames.strip() else 12

fps = input("FPS (playback only) [default 12]: ")
fps = int(fps) if fps.strip() else 12

print("\nResolution:")
print("1) 512x512 (fast)")
print("2) 768x768 (better quality)")
res_choice = input("Choice [1/2, default 1]: ")

if res_choice == "2":
    width, height = 768, 768
else:
    width, height = 512, 512

# ----------------------------

# OUTPUT SETUP (D DRIVE)

# ----------------------------

timestamp = int(time.time())
OUTPUT_DIR = f"D:/VideoGenOutputs/run_{timestamp}"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\nOutput folder: {OUTPUT_DIR}")

# ----------------------------

# LOAD MODELS

# ----------------------------

print("\nLoading pipelines...")

controlnet_pipe = load_controlnet_pipeline(MODEL_ID, device)

if controlnet_pipe is not None:
    controlnet_pipe.scheduler = DPMSolverMultistepScheduler.from_config(controlnet_pipe.scheduler.config)

text2img = StableDiffusionPipeline(
vae=controlnet_pipe.vae,
text_encoder=controlnet_pipe.text_encoder,
tokenizer=controlnet_pipe.tokenizer,
unet=controlnet_pipe.unet,
scheduler=controlnet_pipe.scheduler,
safety_checker=None,
feature_extractor=None,
).to(device)

text2img.scheduler = controlnet_pipe.scheduler

# 🔥 PERFORMANCE BOOSTS

text2img.enable_attention_slicing()

# 🔥 TRY XFORMERS (SAFE TRY)

try:
    text2img.enable_xformers_memory_efficient_attention()
    if controlnet_pipe is not None:
        controlnet_pipe.enable_xformers_memory_efficient_attention()
    print("xFormers enabled")
except Exception as e:
    print("xFormers not available:", e)

# ----------------------------

# CREATE PLAN

# ----------------------------

print("Creating prompt plan...")

negative_prompt = "red fog, red tint, oversaturated red, monochrome red, red fog, red tint, oversaturated colors, color shift, orange tint, unrealistic lighting, distortion, blurry, low detail, inconsistent colors"

try:
    plan = create_prompt_plan(
    user_prompt=prompt,
    style="cinematic",
    motion_preset="auto",
    num_frames=num_frames,
    width=width,
    height=height,
    negative_prompt=negative_prompt
    )
except TypeError:
    plan = create_prompt_plan(
    user_prompt=prompt,
    style="cinematic",
    motion_preset="auto",
    num_frames=num_frames,
    width=width,
    height=height
    )

# ----------------------------

# GENERATE FRAMES

# ----------------------------

print("Generating frames...\n")

# 🔥 NO GRAD = BIG SPEED BOOST

with torch.no_grad():
    frames = generate_frames(
plan,
text2img_pipe=text2img,
img2img_pipe=None,
controlnet_pipe=controlnet_pipe,
device=device
)

# 🔥 VRAM DEBUG

if device == "cuda":
    print("VRAM used:", round(torch.cuda.memory_allocated() / 1e9, 2), "GB")

# temporal smoothing (important)

frames = smooth_frames(frames, alpha=0.7)

# optional interpolation (increase FPS feel)

frames = interpolate_frames(frames, factor=2)

fps = fps * 2

print("\nFrames generated.\n")

# ----------------------------

# SAVE FRAMES

# ----------------------------

print("Saving frames...")

for i, frame in enumerate(frames):
    frame.save(f"{OUTPUT_DIR}/frame_{i:03d}.png")

print("Frames saved.\n")

# ----------------------------

# CREATE VIDEO

# ----------------------------

print("Creating video...")

frame_array = [np.array(f) for f in frames]
height, width = frame_array[0].shape[:2]

video_path = f"{OUTPUT_DIR}/output.mp4"

out = cv2.VideoWriter(
video_path,
cv2.VideoWriter_fourcc(*"mp4v"),
fps,
(width, height)
)

for frame in frame_array:
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out.write(frame_bgr)

out.release()

print(f"\nVideo saved at: {video_path}")

# ----------------------------

# DONE

# ----------------------------

print("\n=== DONE ===\n")
