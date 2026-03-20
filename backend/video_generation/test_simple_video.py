#!/usr/bin/env python3
"""
Quick test script to generate a simple test video using PIL only
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_test_video():
    """Create a simple test video using PIL and ffmpeg"""
    output_dir = Path("output_videos")
    output_dir.mkdir(exist_ok=True)
    
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    # Create 30 frames (1 second at 30fps)
    width, height = 1280, 720
    num_frames = 30
    
    print("Creating frames...")
    for frame_idx in range(num_frames):
        # Calculate color
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
        
        # Save frame
        frame_path = frames_dir / f"frame_{frame_idx:04d}.png"
        img.save(frame_path)
        
        if (frame_idx + 1) % 10 == 0:
            print(f"  {frame_idx + 1}/{num_frames} frames created")
    
    # Create video using ffmpeg
    print("\nCreating video with ffmpeg...")
    output_video = output_dir / "test_video.mp4"
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-framerate", "30",
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_video)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Video created successfully: {output_video}")
        print(f"  Size: {output_video.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"✗ Error creating video:")
        print(result.stderr)
    
    return output_video

if __name__ == "__main__":
    video_path = create_test_video()
