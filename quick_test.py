#!/usr/bin/env python3
"""
Quick test for HuggingFace and Replicate API models
"""

import os
import subprocess
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env.local'
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get tokens
hf_token = os.getenv('HF_TOKEN')
replicate_token = os.getenv('REPLICATE_API_TOKEN')

logger.info("="*70)
logger.info("VIDEO GENERATION API TESTS - QUICK VERSION")
logger.info("="*70)

logger.info(f"\nAPI Tokens Status:")
logger.info(f"  HF_TOKEN: {'✓ Found' if hf_token else '✗ Not found'}")
logger.info(f"  REPLICATE_API_TOKEN: {'✓ Found' if replicate_token else '✗ Not found'}")

# Test 1: Simple generation
logger.info("\n[1/3] Testing Simple Text-Based Generation...")
env = os.environ.copy()
result = subprocess.run([
    sys.executable, 'backend/video_generation/generate_video.py',
    '--prompt', 'A smooth fade-in animation from blue to purple with text',
    '--duration', '5',
    '--output', 'backend/video_generation/output_videos/test_simple.mp4'
], capture_output=True, text=True, env=env, timeout=120)

if result.returncode == 0:
    size = Path('backend/video_generation/output_videos/test_simple.mp4').stat().st_size / (1024*1024)
    logger.info(f"  ✓ PASSED - Generated {size:.2f} MB video")
else:
    logger.error(f"  ✗ FAILED - {result.stderr[-200:]}")

# Test 2: HuggingFace API
if hf_token:
    logger.info("\n[2/3] Testing HuggingFace API Generation...")
    logger.info("  (This will take 1-5 minutes, please wait...)")
    env = os.environ.copy()
    env['HF_TOKEN'] = hf_token
    result = subprocess.run([
        sys.executable, 'backend/video_generation/generate_video.py',
        '--prompt', 'Professional animation with geometric shapes flowing smoothly',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_hf.mp4',
        '--model', 'huggingface',
        '--steps', '20'
    ], capture_output=True, text=True, env=env, timeout=600)
    
    if result.returncode == 0:
        hf_file = Path('backend/video_generation/output_videos/test_hf.mp4')
        if hf_file.exists():
            size = hf_file.stat().st_size / (1024*1024)
            logger.info(f"  ✓ PASSED - Generated {size:.2f} MB video via HuggingFace API")
        else:
            logger.error(f"  ✗ FAILED - No output file created")
    else:
        err = result.stderr.split('\n')[-3]
        logger.error(f"  ✗ FAILED - {err}")
else:
    logger.info("\n[2/3] HuggingFace API - SKIPPED (no HF_TOKEN)")

# Test 3: Replicate API
if replicate_token:
    logger.info("\n[3/3] Testing Replicate API Generation...")
    logger.info("  (This will take 1-5 minutes, please wait...)")
    env = os.environ.copy()
    env['REPLICATE_API_TOKEN'] = replicate_token
    result = subprocess.run([
        sys.executable, 'backend/video_generation/generate_video.py',
        '--prompt', 'Beautiful landscape with rolling hills and sunset',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_replicate.mp4',
        '--model', 'replicate',
    ], capture_output=True, text=True, env=env, timeout=600)
    
    if result.returncode == 0:
        rep_file = Path('backend/video_generation/output_videos/test_replicate.mp4')
        if rep_file.exists():
            size = rep_file.stat().st_size / (1024*1024)
            logger.info(f"  ✓ PASSED - Generated {size:.2f} MB video via Replicate API")
        else:
            logger.error(f"  ✗ FAILED - No output file created")
    else:
        err = result.stderr.split('\n')[-3]
        logger.error(f"  ✗ FAILED - {err}")
else:
    logger.info("\n[3/3] Replicate API - SKIPPED (no REPLICATE_API_TOKEN)")

logger.info("\n" + "="*70)
logger.info("Testing complete! Check output_videos/ for generated files.")
logger.info("="*70)
