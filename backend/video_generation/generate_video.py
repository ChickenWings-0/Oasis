#!/usr/bin/env python3
"""
Text-to-Video Generation Module
Generates videos from text prompts using AI models or simple text rendering
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import logging
import os

# Load environment variables from .env.local
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env.local'
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not required, can use system env vars

# Handle relative imports for both module and script execution
try:
    from .models import get_model, HuggingFaceVideoModel
except ImportError:
    # When run as script, use direct import
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from models import get_model, HuggingFaceVideoModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _generate_simple_fallback(
    prompt: str,
    duration: int = 10,
    output_path: str = 'output.mp4',
    fps: int = 24,
    resolution: tuple = (1280, 720)
) -> bool:
    """Fallback simple text-based video generation (if advanced generator not available)"""
    logger.info("Using simple fallback text-based video generation")
    try:
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        import textwrap
        
        logger.info(f"Starting video generation: {prompt[:50]}...")
        logger.info(f"Duration: {duration}s, Resolution: {resolution}, FPS: {fps}")
        
        frames = []
        total_frames = duration * fps
        
        # Simple blue background with white text
        for frame_idx in range(total_frames):
            img = Image.new('RGB', resolution, (40, 44, 52))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 50)
            except:
                font = ImageFont.load_default()
            
            text = prompt[:40]
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (resolution[0] - text_width) // 2
            y = (resolution[1] - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            frames.append(np.array(img))
        
        # Save video
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        video = ImageSequenceClip(frames, fps=fps)
        video.write_videofile(str(output_path), codec='libx264')
        
        logger.info(f"✓ Video saved: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in fallback generation: {e}", exc_info=True)
        return False


def generate_video_with_ai(
    prompt: str,
    model_type: str = "huggingface",
    output_path: str = 'output.mp4',
    duration: Optional[int] = None,
    **model_kwargs
) -> bool:
    """
    Generate a video using an AI model (HuggingFace, etc).
    
    Args:
        prompt: Text description of the video
        model_type: Type of model to use ('huggingface', 'local_diffusers')
        output_path: Path to save the generated video
        duration: Video duration (some models may not support this)
        **model_kwargs: Additional model-specific parameters
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Using AI model: {model_type}")
        
        # Separate model config from generation parameters
        model_config = {}
        generation_params = {}
        
        # Model config parameters (for __init__)
        model_config_keys = {'model_id', 'api_token', 'api_url', 'device', 'dtype'}
        
        # Split kwargs
        for key, value in model_kwargs.items():
            if key in model_config_keys:
                model_config[key] = value
            else:
                generation_params[key] = value
        
        # Get the appropriate model
        model = get_model(model_type=model_type, **model_config)
        
        # Generate video
        result = model.generate(
            prompt=prompt,
            duration=duration,
            output_path=output_path,
            **generation_params
        )
        
        if result['success']:
            logger.info(f"✓ Video generated successfully")
            if result.get('metadata'):
                logger.info(f"Metadata: {result['metadata']}")
            return True
        else:
            logger.error(f"Video generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        logger.error(f"Missing required library: {e}")
        return False
    except Exception as e:
        logger.error(f"Error with AI generation: {str(e)}", exc_info=True)
        return False


def generate_video(
    prompt: str,
    duration: int = 10,
    output_path: str = 'output.mp4',
    fps: int = 24,
    resolution: tuple = (1280, 720),
    model_type: Optional[str] = None,
    **model_kwargs
) -> bool:
    """
    Generate a video from a text prompt.
    
    Args:
        prompt: Text description of the video
        duration: Video duration in seconds
        output_path: Path to save the generated video
        fps: Frames per second
        resolution: Video resolution (width, height)
        model_type: 'simple' (advanced templates), 'huggingface', 'replicate', 'local_diffusers'
                   If 'simple' or None, uses advanced template-based generation.
        **model_kwargs: Additional model-specific parameters
    
    Returns:
        True if successful, False otherwise
    """
    # 'simple' model uses advanced template-based generation (no API)
    if model_type == 'simple' or model_type is None:
        logger.info("Using advanced template-based video generation (no API required)")
        try:
            from advanced_generate import VideoGenerator
            
            generator = VideoGenerator(output_path=output_path)
            return generator.generate(
                prompt=prompt,
                duration=duration,
                fps=fps,
                width=resolution[0],
                height=resolution[1]
            )
        except ImportError:
            logger.warning("Advanced generator not available, using fallback")
            # Fallback to old simple generation if advanced not available
            return _generate_simple_fallback(
                prompt=prompt,
                duration=duration,
                output_path=output_path,
                fps=fps,
                resolution=resolution
            )
    
    # Use AI model if specified
    if model_type:
        return generate_video_with_ai(
            prompt=prompt,
            model_type=model_type,
            output_path=output_path,
            duration=duration,
            width=resolution[0],
            height=resolution[1],
            **model_kwargs
        )
    
    # Fallback to simple text-based video generation
    logger.info("Falling back to simple text-based generation")
    return _generate_simple_fallback(
        prompt=prompt,
        duration=duration,
        output_path=output_path,
        fps=fps,
        resolution=resolution
    )


def main():
    parser = argparse.ArgumentParser(
        description='Generate a video from a text prompt'
    )
    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Text description for the video'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Video duration in seconds (default: 10, max: 60)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output.mp4',
        help='Output video file path'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=24,
        help='Frames per second (default: 24)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1280,
        help='Video width in pixels (default: 1280)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=720,
        help='Video height in pixels (default: 720)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        choices=['simple', 'huggingface', 'replicate', 'local_diffusers'],
        help='Video generation model: simple (instant), huggingface, replicate, or local_diffusers'
    )
    parser.add_argument(
        '--model-id',
        type=str,
        default='cerspense/zeroscope_v2_XL',
        help='HuggingFace model ID (default: cerspense/zeroscope_v2_XL)'
    )
    parser.add_argument(
        '--steps',
        type=int,
        default=25,
        help='Number of inference steps for AI models (default: 25)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if len(args.prompt) < 10 or len(args.prompt) > 500:
        logger.error("Prompt must be between 10 and 500 characters")
        sys.exit(1)
    
    if args.duration < 5 or args.duration > 60:
        logger.error("Duration must be between 5 and 60 seconds")
        sys.exit(1)
    
    # Generate video
    success = generate_video(
        prompt=args.prompt,
        duration=args.duration,
        output_path=args.output,
        fps=args.fps,
        resolution=(args.width, args.height),
        model_type=args.model,
        model_id=args.model_id,
        num_inference_steps=args.steps
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
