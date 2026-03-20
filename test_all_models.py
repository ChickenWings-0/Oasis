#!/usr/bin/env python3
"""
Test all video generation models with API tokens from .env.local
Tests:
1. Simple text-based generation (no API required)
2. HuggingFace API with HF_TOKEN
3. Replicate API with REPLICATE_API_TOKEN
4. Local Diffusers (if GPU available)
"""

import os
import subprocess
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent / '.env.local'
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tokens():
    """Check if API tokens are loaded"""
    logger.info("\n" + "="*60)
    logger.info("API TOKEN STATUS")
    logger.info("="*60)
    
    hf_token = os.getenv('HF_TOKEN')
    replicate_token = os.getenv('REPLICATE_API_TOKEN')
    
    logger.info(f"HF_TOKEN:              {'✓ Loaded' if hf_token else '✗ Not found'}")
    logger.info(f"REPLICATE_API_TOKEN:   {'✓ Loaded' if replicate_token else '✗ Not found'}")
    logger.info(f"NEXT_PUBLIC_VIDEO_MODEL: {os.getenv('NEXT_PUBLIC_VIDEO_MODEL', 'Not set')}")
    
    return hf_token is not None, replicate_token is not None

def test_simple_generation():
    """Test 1: Simple text-based generation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: SIMPLE TEXT-BASED GENERATION")
    logger.info("="*60)
    
    cmd = [
        sys.executable,
        'backend/video_generation/generate_video.py',
        '--prompt', 'A beautiful gradient animation with blue to purple transition',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_simple.mp4',
    ]
    
    # Create environment with dotenv loaded
    env = os.environ.copy()
    env.update({
        'HF_TOKEN': os.getenv('HF_TOKEN', ''),
        'REPLICATE_API_TOKEN': os.getenv('REPLICATE_API_TOKEN', '')
    })
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        if result.returncode == 0:
            output_path = Path('backend/video_generation/output_videos/test_simple.mp4')
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✓ PASSED - Size: {size_mb:.2f} MB")
            return True
        else:
            logger.error(f"✗ FAILED - {result.stderr[:200]}")
            return False
    except Exception as e:
        logger.error(f"✗ FAILED - {e}")
        return False

def test_huggingface_generation():
    """Test 2: HuggingFace API generation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: HUGGINGFACE API GENERATION")
    logger.info("="*60)
    
    if not os.getenv('HF_TOKEN'):
        logger.warning("⊘ SKIPPED - HF_TOKEN not set")
        return None
    
    cmd = [
        sys.executable,
        'backend/video_generation/generate_video.py',
        '--prompt', 'A professional video with geometric shapes and smooth transitions',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_huggingface.mp4',
        '--model', 'huggingface',
        '--model-id', 'cerspense/zeroscope_v2_576w',
        '--steps', '20'
    ]
    
    # Create environment with API token
    env = os.environ.copy()
    env['HF_TOKEN'] = os.getenv('HF_TOKEN', '')
    
    try:
        logger.info("Calling HuggingFace API... (this may take 1-5 minutes)")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
        if result.returncode == 0:
            output_path = Path('backend/video_generation/output_videos/test_huggingface.mp4')
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ PASSED - Size: {size_mb:.2f} MB")
                return True
            else:
                logger.warning("⊘ PARTIAL - Script completed but file not found")
                return False
        else:
            # Log some of the error
            error_lines = result.stderr.split('\n')[-5:]
            error_msg = '\n'.join(error_lines)
            logger.error(f"✗ FAILED - {error_msg[:300]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("✗ TIMEOUT - Generation took too long (>10 minutes)")
        return False
    except Exception as e:
        logger.error(f"✗ FAILED - {e}")
        return False

def test_replicate_generation():
    """Test 3: Replicate API generation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: REPLICATE API GENERATION")
    logger.info("="*60)
    
    if not os.getenv('REPLICATE_API_TOKEN'):
        logger.warning("⊘ SKIPPED - REPLICATE_API_TOKEN not set")
        return None
    
    cmd = [
        sys.executable,
        'backend/video_generation/generate_video.py',
        '--prompt', 'A stunning landscape with rolling hills and beautiful sunset',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_replicate.mp4',
        '--model', 'replicate',
        '--steps', '30'
    ]
    
    # Create environment with API token
    env = os.environ.copy()
    env['REPLICATE_API_TOKEN'] = os.getenv('REPLICATE_API_TOKEN', '')
    
    try:
        logger.info("Calling Replicate API... (this may take 1-5 minutes)")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
        if result.returncode == 0:
            output_path = Path('backend/video_generation/output_videos/test_replicate.mp4')
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ PASSED - Size: {size_mb:.2f} MB")
                return True
            else:
                logger.warning("⊘ PARTIAL - Script completed but file not found")
                return False
        else:
            error_lines = result.stderr.split('\n')[-5:]
            error_msg = '\n'.join(error_lines)
            logger.error(f"✗ FAILED - {error_msg[:300]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("✗ TIMEOUT - Generation took too long (>10 minutes)")
        return False
    except Exception as e:
        logger.error(f"✗ FAILED - {e}")
        return False

def test_local_diffusers_generation():
    """Test 4: Local Diffusers generation (GPU required)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: LOCAL DIFFUSERS GENERATION")
    logger.info("="*60)
    
    try:
        import torch
        if not torch.cuda.is_available():
            logger.warning("⊘ SKIPPED - CUDA/GPU not available (required for local models)")
            return None
    except ImportError:
        logger.warning("⊘ SKIPPED - torch not available")
        return None
    
    cmd = [
        sys.executable,
        'backend/video_generation/generate_video.py',
        '--prompt', 'An artistic animation with vibrant colors and smooth motion',
        '--duration', '5',
        '--output', 'backend/video_generation/output_videos/test_local_diffusers.mp4',
        '--model', 'local_diffusers',
        '--width', '576',
        '--height', '576',
        '--steps', '25'
    ]
    
    try:
        logger.info("Running local Diffusers pipeline... (this will take 5-15 minutes on GPU)")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            output_path = Path('backend/video_generation/output_videos/test_local_diffusers.mp4')
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ PASSED - Size: {size_mb:.2f} MB")
                return True
            else:
                logger.warning("⊘ PARTIAL - Script completed but file not found")
                return False
        else:
            error_lines = result.stderr.split('\n')[-5:]
            error_msg = '\n'.join(error_lines)
            logger.error(f"✗ FAILED - {error_msg[:300]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("✗ TIMEOUT - Generation took too long (>15 minutes)")
        return False
    except Exception as e:
        logger.error(f"✗ FAILED - {e}")
        return False

if __name__ == "__main__":
    hf_available, replicate_available = check_tokens()
    
    results = {
        "Simple": test_simple_generation(),
        "HuggingFace": test_huggingface_generation() if hf_available else None,
        "Replicate": test_replicate_generation() if replicate_available else None,
        "LocalDiffusers": test_local_diffusers_generation(),
    }
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for model_name, result in results.items():
        if result is True:
            status = "✓ PASSED"
        elif result is False:
            status = "✗ FAILED"
        else:
            status = "⊘ SKIPPED"
        logger.info(f"{model_name:20} {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    logger.info(f"\nTotal: {passed} passed out of {len([r for r in results.values() if r is not None])} available tests")
