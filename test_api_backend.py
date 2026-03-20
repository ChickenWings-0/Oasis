#!/usr/bin/env python3
"""
Test script for the video generation backend API
Tests the backend generate_video.py with CLI arguments
"""

import subprocess
import sys
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cli_generation():
    """Test the generate_video.py script with CLI arguments"""
    
    script_path = Path("backend/video_generation/generate_video.py")
    output_path = Path("backend/video_generation/output_videos/test_cli_video.mp4")
    
    logger.info("Testing CLI video generation...")
    logger.info(f"Script: {script_path}")
    logger.info(f"Output: {output_path}")
    
    # Test prompt
    prompt = "A colorful gradient animation with text overlay showing a test video"
    
    cmd = [
        sys.executable,
        str(script_path),
        "--prompt",
        prompt,
        "--duration",
        "5",
        "--output",
        str(output_path),
    ]
    
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info("Running...")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        logger.info("STDOUT:")
        logger.info(result.stdout)
        
        if result.stderr:
            logger.error("STDERR:")
            logger.error(result.stderr)
        
        logger.info(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ Video created successfully!")
                logger.info(f"  File: {output_path}")
                logger.info(f"  Size: {size_mb:.2f} MB")
                return True
            else:
                logger.error("Script ran but video file not created")
                return False
        else:
            logger.error(f"Script failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Script timed out after 120 seconds")
        return False
    except Exception as e:
        logger.error(f"Error running script: {e}")
        return False


def test_api_models():
    """Check which models are available and their configuration"""
    logger.info("\n" + "="*50)
    logger.info("Available Video Generation Models")
    logger.info("="*50)
    
    models_info = {
        "huggingface": {
            "status": "Requires HF_TOKEN env var",
            "models": ["cerspense/zeroscope_v2_XL", "cerspense/zeroscope_v2_576w"],
            "local": False
        },
        "replicate": {
            "status": "Requires REPLICATE_API_TOKEN env var",
            "models": ["cjwbw/text-to-video"],
            "local": False
        },
        "local_diffusers": {
            "status": "Requires GPU (10-24GB VRAM)",
            "models": ["cerspense/zeroscope_v2_576w", "AnimateDiff"],
            "local": True
        }
    }
    
    for model_type, info in models_info.items():
        logger.info(f"\n{model_type.upper()}")
        logger.info(f"  Status: {info['status']}")
        logger.info(f"  Models: {', '.join(info['models'])}")
        logger.info(f"  Local Only: {info['local']}")

if __name__ == "__main__":
    test_api_models()
    logger.info("\n" + "="*50)
    success = test_cli_generation()
    logger.info("="*50)
    if success:
        logger.info("\n✓ API backend test PASSED")
    else:
        logger.info("\n✗ API backend test FAILED")
