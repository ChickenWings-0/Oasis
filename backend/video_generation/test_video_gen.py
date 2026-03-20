#!/usr/bin/env python3
"""
Test video generation using moviepy
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import ImageSequenceClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_video_with_moviepy():
    """Create a test video using PIL frames and moviepy"""
    output_dir = Path("output_videos")
    output_dir.mkdir(exist_ok=True)
    
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    # Create 60 frames (2 seconds at 30fps)
    width, height = 1280, 720
    num_frames = 60
    
    logger.info("Creating frames...")
    frames = []
    
    for frame_idx in range(num_frames):
        # Calculate color gradient
        progress = frame_idx / num_frames
        r = int(100 + progress * 155)
        g = int(100 + (1-progress) * 155)
        b = int(150)
        
        # Create image
        img = Image.new('RGB', (width, height), (r, g, b))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"Test Video - Frame {frame_idx + 1}/{num_frames}"
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Convert to numpy array and add to frames list
        frame_array = np.array(img)
        frames.append(frame_array)
        
        if (frame_idx + 1) % 15 == 0:
            logger.info(f"  Created {frame_idx + 1}/{num_frames} frames")
    
    # Create video using moviepy
    logger.info("Creating video with moviepy...")
    output_video = output_dir / "test_video.mp4"
    
    try:
        # Create video clip with 30 fps
        clip = ImageSequenceClip(frames, fps=30)
        
        # Write video file
        clip.write_videofile(str(output_video))
        
        logger.info(f"✓ Video created successfully: {output_video}")
        file_size = output_video.stat().st_size / (1024*1024)
        logger.info(f"  Size: {file_size:.2f} MB")
        logger.info(f"  Duration: {len(frames) / 30:.1f} seconds")
        return output_video
        
    except Exception as e:
        logger.error(f"✗ Error creating video: {e}")
        raise

if __name__ == "__main__":
    video_path = create_test_video_with_moviepy()
    logger.info(f"Test video generated at: {video_path}")
