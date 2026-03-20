"""
Video Generation Models Module
Provides an abstraction layer for different video generation backends
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
import os
import requests
from pathlib import Path
import time
import json

logger = logging.getLogger(__name__)


class VideoGenerationModel(ABC):
    """Abstract base class for video generation models"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video from a prompt.
        
        Args:
            prompt: Text description of the video
            duration: Video duration (model-specific)
            **kwargs: Additional model-specific parameters
        
        Returns:
            Dictionary with keys:
                - 'success': bool
                - 'output_path': str (if successful)
                - 'error': str (if failed)
                - 'metadata': dict (model-specific metadata)
        """
        pass


class HuggingFaceVideoModel(VideoGenerationModel):
    """
    Hugging Face video generation model using the Inference API.
    Supports models like:
    - text2video-zero
    - damo-vilab/text-to-video-ms-1.7b
    - cerspense/zeroscope_v2_576w
    - cerspense/zeroscope_v2_XL
    """
    
    def __init__(
        self,
        model_id: str = "cerspense/zeroscope_v2_XL",
        api_token: Optional[str] = None,
        api_url: str = "https://hf.space"
    ):
        """
        Initialize the Hugging Face video model.
        
        Args:
            model_id: HF model identifier
            api_token: HuggingFace API token (falls back to HF_TOKEN env var)
            api_url: Base URL for HF inference API
        """
        self.model_id = model_id
        self.api_token = api_token or os.getenv("HF_TOKEN")
        self.api_url = api_url
        # Use serverless inference API endpoint
        self.model_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        if not self.api_token:
            logger.warning(
                "HuggingFace API token not provided. "
                "Set HF_TOKEN environment variable or pass api_token parameter."
            )
    
    def generate(
        self,
        prompt: str,
        duration: Optional[int] = None,
        num_inference_steps: int = 25,
        output_path: str = "output.mp4",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video using HuggingFace Inference API.
        
        Args:
            prompt: Text description of the video
            duration: Not used by HF API (model generates fixed duration)
            num_inference_steps: Number of inference steps (default: 25)
            output_path: Path to save the video
            **kwargs: Additional parameters (height, width, etc.)
        
        Returns:
            Dictionary with generation results
        """
        try:
            if not self.api_token:
                return {
                    'success': False,
                    'error': 'HuggingFace API token not configured',
                    'output_path': None,
                    'metadata': {}
                }
            
            logger.info(f"Generating video with {self.model_id}")
            logger.info(f"Prompt: {prompt[:100]}...")
            
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "num_inference_steps": num_inference_steps,
                }
            }
            
            # Add optional parameters
            if "height" in kwargs:
                payload["parameters"]["height"] = kwargs["height"]
            if "width" in kwargs:
                payload["parameters"]["width"] = kwargs["width"]
            
            logger.info(f"Calling API: {self.model_url}")
            response = requests.post(
                self.model_url,
                headers=headers,
                json=payload,
                timeout=300  # 5 minute timeout for video generation
            )
            
            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"API Error ({response.status_code}): {error_msg}")
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {error_msg}",
                    'output_path': None,
                    'metadata': {}
                }
            
            # Save the video file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✓ Video successfully saved to: {output_path}")
            
            return {
                'success': True,
                'output_path': str(output_path),
                'error': None,
                'metadata': {
                    'model': self.model_id,
                    'prompt': prompt,
                    'num_inference_steps': num_inference_steps,
                    'file_size': output_path.stat().st_size,
                }
            }
            
        except requests.exceptions.Timeout:
            error_msg = "Video generation timed out (>5 minutes)"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'metadata': {}
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'output_path': None,
                'metadata': {}
            }
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'output_path': None,
                'metadata': {}
            }


class LocalDiffusersModel(VideoGenerationModel):
    """
    Local video generation using Hugging Face Diffusers library.
    Requires significant VRAM and compute resources.
    
    Supported models:
    - AnimateDiff
    - Zeroscope
    - ModelScope
    
    Note: Requires NVIDIA CUDA GPU (10-24GB VRAM). Intel/AMD GPUs or CPU processing will be extremely slow.
    """
    
    def __init__(
        self,
        model_id: str = "cerspense/zeroscope_v2_576w",
        device: Optional[str] = None,
        dtype: str = "float16"
    ):
        """
        Initialize local Diffusers model.
        
        Args:
            model_id: Model identifier from Hugging Face Hub
            device: 'cuda' for GPU, 'cpu' for CPU, or None to auto-detect
            dtype: 'float16' or 'float32'
        """
        self.model_id = model_id
        self.dtype = dtype
        self.pipeline = None
        
        # Auto-detect device if not specified
        if device is None:
            self.device = self._detect_device()
        else:
            self.device = device
    
    def _detect_device(self) -> str:
        """Auto-detect the best available device"""
        try:
            import torch
            
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                logger.info(f"✓ CUDA available: {device_name}")
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info("✓ MPS (Metal Performance Shaders) available")
                return "mps"
            else:
                logger.warning("⚠️  No GPU acceleration available. Will use CPU (very slow)")
                return "cpu"
        except Exception as e:
            logger.warning(f"Failed to detect device: {e}. Falling back to CPU.")
            return "cpu"
    
    def _load_pipeline(self):
        """Lazy load the pipeline on first use"""
        if self.pipeline is not None:
            return
        
        try:
            from diffusers import DPMSolverMultistepScheduler, DiffusionPipeline
            import torch
            
            logger.info(f"Loading pipeline for {self.model_id}...")
            
            torch_dtype = torch.float16 if self.dtype == "float16" else torch.float32
            
            self.pipeline = DiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch_dtype,
            )
            self.pipeline = self.pipeline.to(self.device)
            
            # Optimize pipeline
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            self.pipeline.enable_attention_slicing()
            
            logger.info("✓ Pipeline loaded successfully")
            
        except ImportError as e:
            logger.error(f"Missing required package: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load pipeline: {e}", exc_info=True)
            raise
    
    def generate(
        self,
        prompt: str,
        duration: Optional[int] = None,
        num_inference_steps: int = 25,
        output_path: str = "output.mp4",
        height: int = 576,
        width: int = 576,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video using local Diffusers pipeline.
        
        Note: This requires NVIDIA CUDA GPU with at least 10GB VRAM.
        CPU processing will be extremely slow (hours).
        
        Args:
            prompt: Text description
            duration: Not used (Diffusers generates fixed frame count)
            num_inference_steps: Number of steps (25-50 recommended)
            output_path: Output file path
            height: Video height (default 576)
            width: Video width (default 576)
        
        Returns:
            Generation results
        """
        # Check if running on CPU
        if self.device == "cpu":
            error_msg = (
                "❌ Local Diffusers model requires NVIDIA CUDA GPU (10-24GB VRAM). "
                "CPU processing would take many hours. "
                "Please try: Simple (instant), HuggingFace (API), or Replicate (API) models instead."
            )
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'metadata': {'device': 'cpu', 'model': self.model_id}
            }
        
        try:
            self._load_pipeline()
            
            logger.info(f"Generating video locally")
            logger.info(f"Model: {self.model_id}")
            logger.info(f"Resolution: {width}x{height}, Steps: {num_inference_steps}")
            logger.info(f"Device: {self.device}")
            
            # Generate video
            video_frames = self.pipeline(
                prompt=prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
            ).frames
            
            # Save video
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            from moviepy import ImageSequenceClip
            import numpy as np
            
            frames = [np.array(frame) for frame in video_frames]
            video = ImageSequenceClip(frames, fps=8)
            video.write_videofile(str(output_path), codec='libx264')
            
            logger.info(f"✓ Video saved to: {output_path}")
            
            return {
                'success': True,
                'output_path': str(output_path),
                'error': None,
                'metadata': {
                    'model': self.model_id,
                    'prompt': prompt,
                    'resolution': f"{width}x{height}",
                    'num_inference_steps': num_inference_steps,
                    'frame_count': len(video_frames),
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'output_path': None,
                'metadata': {}
            }


class ReplicateVideoModel(VideoGenerationModel):
    """
    Replicate.com video generation model using the replicate Python client.
    More reliable than HuggingFace Inference API.
    
    Supported models:
    - anotherjesse/zeroscope-v2-xl (Recommended)
    - anotherjesse/zeroscope-v2-576w
    """
    
    def __init__(
        self,
        model_id: str = "anotherjesse/zeroscope-v2-xl",
        api_token: Optional[str] = None
    ):
        """
        Initialize Replicate video model.
        
        Args:
            model_id: Replicate model identifier (owner/model-name)
            api_token: Replicate API token (falls back to REPLICATE_API_TOKEN env var)
        """
        self.model_id = model_id
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        
        if not self.api_token:
            logger.warning(
                "Replicate API token not provided. "
                "Set REPLICATE_API_TOKEN environment variable or pass api_token parameter."
            )
    
    def generate(
        self,
        prompt: str,
        duration: Optional[int] = None,
        num_inference_steps: int = 50,
        output_path: str = "output.mp4",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video using Replicate API via Python client.
        
        Args:
            prompt: Text description of the video
            duration: Not used by Replicate (model generates ~6 seconds)
            num_inference_steps: Number of inference steps (default: 50)
            output_path: Path to save the video
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with generation results
        """
        try:
            if not self.api_token:
                return {
                    'success': False,
                    'error': 'Replicate API token not configured',
                    'output_path': None,
                    'metadata': {}
                }
            
            logger.info(f"Generating video with {self.model_id}")
            logger.info(f"Prompt: {prompt[:100]}...")
            
            try:
                import replicate
            except ImportError:
                return {
                    'success': False,
                    'error': 'replicate package not installed. Install with: pip install replicate',
                    'output_path': None,
                    'metadata': {}
                }
            
            # Set API token
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
            
            logger.info(f"Calling Replicate API...")
            
            # Run model prediction
            input_data = {
                "prompt": prompt,
                "num_frames": kwargs.get("num_frames", 24),
                "num_inference_steps": num_inference_steps,
            }
            
            # Remove num_inference_steps if model doesn't support it
            if "num_inference_steps" in kwargs:
                input_data["num_inference_steps"] = kwargs["num_inference_steps"]
            
            output = replicate.run(
                self.model_id,
                input=input_data,
            )
            
            if not output:
                return {
                    'success': False,
                    'error': 'No output from Replicate',
                    'output_path': None,
                    'metadata': {}
                }
            
            # Handle list or string output
            if isinstance(output, list):
                output_url = output[0] if output else None
            else:
                output_url = output
            
            if not output_url:
                return {
                    'success': False,
                    'error': 'No video output from API',
                    'output_path': None,
                    'metadata': {}
                }
            
            # Download video
            logger.info(f"Downloading video from {str(output_url)[:50]}...")
            video_response = requests.get(str(output_url), timeout=60)
            
            if video_response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Failed to download video',
                    'output_path': None,
                    'metadata': {}
                }
            
            # Save video
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(video_response.content)
            
            logger.info(f"✓ Video successfully saved to: {output_path}")
            
            return {
                'success': True,
                'output_path': str(output_path),
                'error': None,
                'metadata': {
                    'model': self.model_id,
                    'prompt': prompt,
                    'num_inference_steps': num_inference_steps,
                    'file_size': output_path.stat().st_size,
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'output_path': None,
                'metadata': {}
            }


def get_model(
    model_type: str = "huggingface",
    **config
) -> VideoGenerationModel:
    """
    Factory function to get a video generation model.
    
    Args:
        model_type: 'huggingface', 'replicate', or 'local_diffusers'
        **config: Model-specific configuration
    
    Returns:
        VideoGenerationModel instance
    """
    if model_type.lower() == "huggingface":
        return HuggingFaceVideoModel(**config)
    elif model_type.lower() == "replicate":
        return ReplicateVideoModel(**config)
    elif model_type.lower() == "local_diffusers":
        return LocalDiffusersModel(**config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
