from datetime import datetime
from pathlib import Path

import streamlit as st

from generator import generate_frames
from renderer import create_video_from_frames
from utils import blend_frames, get_output_dir, save_frames


st.set_page_config(page_title="OASIS - AI Video Generator", layout="wide")
st.title("OASIS - AI Video Generator")

st.sidebar.header("Controls")
prompt = st.sidebar.text_area("Prompt", value="Cyberpunk city at night", height=100)
num_frames = st.sidebar.slider("Frames", min_value=4, max_value=24, value=8)
motion_level = st.sidebar.selectbox("Motion", options=["low", "medium", "high"], index=1)
motion_type = st.sidebar.selectbox(
    "Camera Motion",
    options=["none", "zoom_in", "zoom_out", "pan_left", "pan_right"],
    index=0
)
style = st.sidebar.selectbox("Style", options=["cinematic", "anime", "realistic"], index=0)
resolution = st.sidebar.selectbox("Resolution", options=[256, 384, 512], index=0)

if st.button("Generate Video", type="primary"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
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
                width=resolution,
                height=resolution,
                motion_type=motion_type,
            )

            status.info("Smoothing frames...")
            frames = blend_frames(frames)

            status.info("Saving frames...")
            save_frames(frames, str(frame_dir))

            status.info("Rendering video...")
            create_video_from_frames(str(frame_dir), str(video_path))

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
