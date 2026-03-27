from datetime import datetime
from pathlib import Path

import streamlit as st

from generator import generate_frames
from renderer import create_video_from_frames
from utils import get_output_dir, save_frames


st.set_page_config(page_title="VideoGen V1 - AI Video Generator", layout="wide")
st.title("VideoGen V1 - AI Video Generator")

st.sidebar.header("Controls")
prompt = st.sidebar.text_area("Prompt", value="Cyberpunk city at night", height=100)
num_frames = st.sidebar.slider(
    "Frames",
    min_value=8,
    max_value=64,
    value=24,
)
fps = st.sidebar.slider(
    "FPS",
    min_value=8,
    max_value=30,
    value=14,
)
motion_level = st.sidebar.selectbox("Motion", options=["low", "medium", "high"], index=1)
style = st.sidebar.selectbox("Style", options=["cinematic", "anime", "realistic"], index=0)
resolution_option = st.sidebar.selectbox(
    "Resolution",
    options=["384 (balanced)", "512 (high quality)", "768 (ultra)", "1080p (upscaled)"],
    index=1,
)

if resolution_option.startswith("384"):
    width, height = 384, 384
    upscale_factor = 1
elif resolution_option.startswith("512"):
    width, height = 512, 512
    upscale_factor = 1
elif resolution_option.startswith("768"):
    width, height = 768, 768
    upscale_factor = 1
else:
    width, height = 768, 768
    upscale_factor = 2

if st.button("Generate Video", type="primary"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
        st.stop()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = get_output_dir()
        frame_dir = base_dir / "frames" / f"run_{timestamp}"
        video_dir = base_dir / "videos"
        video_path = video_dir / f"oasis_{timestamp}.mp4"

        try:
            status = st.empty()
            status.info("Generating frames...")

            frames = generate_frames(
                prompt=prompt,
                num_frames=num_frames,
                motion_level=motion_level,
                style=style,
                width=width,
                height=height,
                prompt_schedule=None,
            )

            if upscale_factor > 1:
                from upscaler import upscale_frames
                st.write("Upscaling to 1080p...")
                frames = upscale_frames(frames, target_size=(1920, 1080))

            st.write(f"Frames: {len(frames)}, FPS: {fps}")

            status.info("Saving frames...")
            save_frames(frames, str(frame_dir))

            status.info("Rendering video...")
            create_video_from_frames(str(frame_dir), str(video_path), fps=fps)

            status.success("Done!")

            st.success(f"Video saved: {video_path}")
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
            st.video(video_bytes)
            with open(video_path, "rb") as f:
                st.download_button(
                    label="Download Video",
                    data=f,
                    file_name=video_path.name,
                    mime="video/mp4",
                )
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
