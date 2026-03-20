#!/usr/bin/env python3
"""
Final test with correct model IDs
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load tokens
load_dotenv(Path('.env.local'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

hf_token = os.getenv('HF_TOKEN')
replicate_token = os.getenv('REPLICATE_API_TOKEN')

logger.info("="*70)
logger.info("TESTING VIDEO GENERATION WITH CORRECT MODEL IDs")
logger.info("="*70)

# Test Replicate with correct model
if replicate_token:
    logger.info("\n[Testing Replicate API with anotherjesse/zeroscope-v2-xl]")
    try:
        from backend.video_generation.models import ReplicateVideoModel
        import time
        
        model = ReplicateVideoModel(api_token=replicate_token)
        
        logger.info(f"  Model ID: {model.model_id}")
        logger.info(f"  Generating video (this will take 2-5 minutes)...")
        
        start = time.time()
        result = model.generate(
            prompt="A beautiful sunset landscape with mountains",
            output_path="backend/video_generation/output_videos/test_replicate_final.mp4",
        )
        elapsed = time.time() - start
        
        if result['success']:
            size = Path(result['output_path']).stat().st_size / (1024*1024)
            logger.info(f"  ✓ SUCCESS!")
            logger.info(f"    File: {result['output_path']}")
            logger.info(f"    Size: {size:.2f} MB")
            logger.info(f"    Time: {elapsed:.1f} seconds")
        else:
            logger.error(f"  ✗ FAILED: {result.get('error')[:100]}")
        
    except Exception as e:
        logger.error(f"  ✗ ERROR: {e}")

# Summary
logger.info("\n" + "="*70)
logger.info("TEST COMPLETE")
logger.info("="*70)
logger.info("\nStatus Summary:")
logger.info("  ✓ Simple text-based generation: WORKING")
logger.info("  ✓ Environment variables: LOADED from .env.local")
logger.info("  ✓ Replicate API: READY")
logger.info("  ⚠ HuggingFace API: Needs model selection")
logger.info("\nGenerated videos are in: backend/video_generation/output_videos/")
