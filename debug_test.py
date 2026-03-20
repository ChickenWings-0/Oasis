#!/usr/bin/env python3
"""
Debug test to see full error messages
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load tokens
load_dotenv(Path('.env.local'))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

hf_token = os.getenv('HF_TOKEN')
replicate_token = os.getenv('REPLICATE_API_TOKEN')

logger.info(f"HF_TOKEN loaded: {bool(hf_token)}")
logger.info(f"REPLICATE_API_TOKEN loaded: {bool(replicate_token)}")

# Test HuggingFace directly
if hf_token:
    logger.info("\n=== Testing HuggingFace Model Directly ===")
    try:
        from backend.video_generation.models import HuggingFaceVideoModel
        
        model = HuggingFaceVideoModel(
            model_id="cerspense/zeroscope_v2_576w",
            api_token=hf_token
        )
        
        logger.info(f"Model URL: {model.model_url}")
        logger.info(f"Model ID: {model.model_id}")
        logger.info(f"API Token present: {bool(model.api_token)}")
        
        # Test generation
        result = model.generate(
            prompt="A test video with smooth transitions",
            output_path="test_hf_debug.mp4",
            num_inference_steps=20
        )
        
        logger.info(f"Result: {result}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

# Test Replicate directly
if replicate_token:
    logger.info("\n=== Testing Replicate Model Directly ===")
    try:
        from backend.video_generation.models import ReplicateVideoModel
        
        model = ReplicateVideoModel(
            api_token=replicate_token
        )
        
        logger.info(f"Model ID: {model.model_id}")
        logger.info(f"API Token present: {bool(model.api_token)}")
        
        # Test generation
        result = model.generate(
            prompt="A test landscape video",
            output_path="test_replicate_debug.mp4",
        )
        
        logger.info(f"Result: {result}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
