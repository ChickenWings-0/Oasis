# Video Generation Feature - Setup Guide

## Overview

The **Video Generator** feature enables users to create videos from text prompts using multiple backends:

- **AI-Powered** (Optional): HuggingFace text-to-video models for photorealistic videos
- **Simple Text-Based** (Default): Fast, lightweight text rendering with animations
- **Local Diffusers** (Advanced): Run models directly on GPU for full control

### Backends

| Backend | Quality | Speed | API Key | Storage |
|---------|---------|-------|---------|---------|
| Simple Text-Based | ⭐⭐ Basic | ⚡ Fast | ❌ None | 💾 Small |
| HuggingFace API | ⭐⭐⭐⭐ High | ⏱️ Slow | ✅ Free | 💾 Medium |
| Local Diffusers | ⭐⭐⭐⭐ High | ⏱️ Medium | ❌ None | 💾 Large |

This feature consists of:

- **Frontend**: Next.js page with a user-friendly UI for entering prompts and adjusting video parameters
- **Backend API**: Next.js API route that handles requests
- **Python Worker**: Flexible video generation with multiple model backends

## Quick Start

### 1. Install Python Dependencies

Navigate to the backend directory and install required packages:

```bash
cd backend/video_generation
pip install -r requirements.txt
```

Or from the project root:

```bash
pip install -r backend/video_generation/requirements.txt
```

### 2. Update Navbar (Optional)

Add the video generator link to your Navbar component:

```tsx
import { VideoGeneratorNavLink } from '@/components/VideoGeneratorNavLink';

export default function Navbar() {
  return (
    <nav>
      {/* Other nav items */}
      <VideoGeneratorNavLink />
    </nav>
  );
}
```

### 3. Create Output Directory

Ensure the public directory exists for storing generated videos:

```bash
mkdir -p public/generated-videos
```

### 4. Start the Development Server

```bash
npm run dev
```

Then navigate to: **http://localhost:3000/video-generator**

## Features

✨ **Multiple Backends** - Simple text-based or AI-powered generation
🤖 **HuggingFace Integration** - Access to Zeroscope, DAMO, and other text-to-video models
⚡ **Fast Processing** - Generate videos in seconds (simple) or minutes (AI)
🎯 **Customizable Duration** - Choose between 5-60 seconds (simple mode)
📝 **Smart Prompts** - Describe any video concept (10-500 characters)
🎬 **Video Preview** - Watch and download generated videos
🔧 **Extensible** - Add new models easily through the model abstraction layer

## Documentation

**New Model System:** See [MODELS_SETUP.md](./MODELS_SETUP.md) for detailed configuration and usage
**Examples:** See [examples.py](./examples.py) for code examples

## API Endpoint

### POST `/api/generate-video`

Generate a video from a text prompt.

**Request Body:**
```json
{
  "prompt": "A beautiful sunset over mountains with birds flying",
  "duration": 15,
  "model": "huggingface"
}
```

**Response:**
```json
{
  "success": true,
  "videoUrl": "/generated-videos/video_1234567890.mp4",
  "message": "Video generated successfully"
}
```

**Error Responses:**
- `400`: Invalid or missing prompt, duration out of range
- `500`: Server error during video generation

## Quick Setup for HuggingFace Models

### 1. Get a Free HuggingFace API Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy your token

### 2. Set Environment Variable

```bash
# Linux/Mac
export HF_TOKEN="hf_xxxxxxxxxxxxxxxx"

# Windows PowerShell
$env:HF_TOKEN = "hf_xxxxxxxxxxxxxxxx"

# Windows CMD
set HF_TOKEN=hf_xxxxxxxxxxxxxxxx
```

### 3. Test with Python

```bash
cd backend/video_generation
python generate_video.py \
  --prompt "A cat in a sunny garden" \
  --model huggingface \
  --output test.mp4
```

### 4. Advanced: Configure in Next.js

Add to `.env.local`:
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxx
NEXT_PUBLIC_VIDEO_MODEL=huggingface
```

Update `app/api/generate-video/route.ts` to pass the model parameter.

## File Structure

```
oasis/
├── app/
│   ├── api/
│   │   └── generate-video/
│   │       └── route.ts               # API endpoint
│   └── video-generator/
│       └── page.tsx                   # Video generator page
├── components/
│   ├── VideoGeneratorForm.tsx        # Main form component
│   └── VideoGeneratorNavLink.tsx     # Navigation link
├── backend/
│   └── video_generation/
│       ├── generate_video.py         # Main generation script (updated)
│       ├── models.py                 # NEW: Model abstraction layer
│       ├── examples.py               # NEW: Usage examples
│       ├── __init__.py
│       ├── requirements.txt          # Python dependencies (updated)
│       ├── README.md                 # This file
│       └── MODELS_SETUP.md          # NEW: Detailed model configuration
└── public/
    └── generated-videos/            # Output videos (auto-created)
```

### New Files Added

- **`models.py`**: Abstraction layer for different video generation backends
  - `VideoGenerationModel` (abstract base class)
  - `HuggingFaceVideoModel` (HuggingFace Inference API)
  - `LocalDiffusersModel` (Local GPU inference)
  - `get_model()` factory function

- **`examples.py`**: Practical code examples
  - Simple text-based generation
  - HuggingFace API usage
  - Batch processing
  - Model comparison
  - Error handling patterns

- **`MODELS_SETUP.md`**: Comprehensive model configuration guide
  - Model descriptions and comparisons
  - Setup instructions
  - Troubleshooting

## Configuration

### Video Generation Backend Selection

**Default (Simple Text-Based):**
```bash
python generate_video.py \
  --prompt "Your video description" \
  --duration 10 \
  --output output.mp4
```

**Using HuggingFace Model:**
```bash
python generate_video.py \
  --prompt "Your video description" \
  --model huggingface \
  --model-id cerspense/zeroscope_v2_XL \
  --steps 25 \
  --output output.mp4
```

**Using Local Diffusers:**
```bash
python generate_video.py \
  --prompt "Your video description" \
  --model local_diffusers \
  --output output.mp4
```

### Command-Line Arguments

```
generate_video.py [OPTIONS]

OPTIONS:
  --prompt TEXT              Video description (10-500 chars) [required]
  --model [huggingface|local_diffusers]
                            Model backend selection [optional]
  --model-id TEXT           HuggingFace model ID
                            [default: cerspense/zeroscope_v2_XL]
  --steps INTEGER           Inference steps for AI models [default: 25]
  --duration INTEGER        Video duration in seconds [default: 10]
  --output PATH             Output video file path [default: output.mp4]
  --fps INTEGER             Frames per second [default: 24]
  --width INTEGER           Video width pixels [default: 1280]
  --height INTEGER          Video height pixels [default: 720]
```

### Environment Variables

```bash
# Required for HuggingFace models
HF_TOKEN=hf_xxxxxxxxxxxxxxxx

# Optional
HF_API_URL=https://api-inference.huggingface.co/models
VIDEO_GENERATION_TIMEOUT=300
```

### Simple Text-Based Parameters (in `generate_video.py`)

You can customize:
- **Resolution**: Default 1280x720
- **FPS**: Default 24 frames per second
- **Color Palette**: Modify the `colors` list in the function
- **Animation Effects**: Adjust scaling and transitions
- **Font**: Change `arial.ttf` to use different fonts

## Troubleshooting

### General Issues

**Issue: "Python script not found"**
- Ensure the path in `route.ts` is correct
- Check that `generate_video.py` exists in `backend/video_generation/`

**Issue: "Missing required library"**
- Install dependencies: `pip install -r backend/video_generation/requirements.txt`
- Ensure FFmpeg is installed on your system

**Issue: "Video not generating"**
- Check server logs for Python errors
- Verify prompt is between 10-500 characters
- Ensure sufficient disk space in `public/generated-videos/`

### HuggingFace Model Issues

**Issue: "HuggingFace API token not configured"**
```bash
# Set your token
export HF_TOKEN="hf_your_token_here"

# Verify it's set
echo $HF_TOKEN
```

**Issue: "API Error: 429 - Rate Limited"**
- Free tier has limited concurrent requests
- Wait a moment and retry
- Consider using local simple generation as fallback
- Implement queue-based generation with retry logic

**Issue: "API timeout (>5 minutes)"**
- Try faster model: `cerspense/zeroscope_v2_576w`
- Reduce inference steps: `--steps 20` (default 25)
- Check HuggingFace availability status

**Issue: "Invalid model ID"**
- Verify model exists: https://huggingface.co/models?task=text-to-video
- Check spelling of model ID
- Popular models:
  - `cerspense/zeroscope_v2_XL` (high quality)
  - `cerspense/zeroscope_v2_576w` (fast)
  - `damo-vilab/text-to-video-ms-1.7b` (alternative)

### Local Model Issues

**Issue: "CUDA Out of Memory"**
- Use smaller model: `cerspense/zeroscope_v2_576w`
- Reduce inference steps
- Free GPU memory: `nvidia-smi`

**Issue: "Diffusers not installed"**
```bash
# Uncomment optional dependencies in requirements.txt
pip install diffusers torch transformers accelerate
```

### FFmpeg Installation

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Windows:**
- Download from: https://ffmpeg.org/download.html
- Or use: `choco install ffmpeg`
- Ensure it's in your PATH
  - **Windows**: `choco install ffmpeg` (if using Chocolatey) or download from ffmpeg.org
  - **Mac**: `brew install ffmpeg`
  - **Linux**: `sudo apt-get install ffmpeg`

## Future Enhancements

- [ ] Integration with GPT-4 for better prompt interpretation
- [ ] Runway or similar AI video API integration
- [ ] Video effects library (transitions, filters)
- [ ] Multi-scene video composition
- [ ] Voice-over and music generation
- [ ] Video templates system
- [ ] Batch processing for multiple videos
- [ ] Video analytics dashboard

## Performance Notes

- First video generation takes longer due to frame rendering
- Default settings (1280x720, 24fps) balance quality and speed
- Longer videos take proportionally more time
- Generated videos are stored in `public/` for easy access

## Security Considerations

- Validate all user inputs (implemented in API route)
- Sanitize prompt text before passing to Python
- Limit concurrent video generation requests
- Consider adding authentication if needed
- Implement rate limiting for API endpoints

## Environment Variables (Optional)

Add to `.env.local` for production:

```
NEXT_PUBLIC_VIDEO_API_ENDPOINT=/api/generate-video
VIDEO_MAX_DURATION=60
VIDEO_MAX_PROMPT_LENGTH=500
ENABLE_VIDEO_GENERATION=true
```

## Testing

To test the video generator locally:

1. Navigate to `/video-generator`
2. Enter a prompt (10-500 characters)
3. Adjust duration (5-60 seconds)
4. Click "Generate Video"
5. Watch the progress indicator
6. Preview and download when complete

Example prompts to test:
- "A serene forest landscape with sunlight filtering through trees"
- "An abstract animation with geometric shapes and vibrant colors"
- "A peaceful ocean beach with waves gently rolling onto shore"

---

**Questions or Issues?** Check the troubleshooting section or review the code comments in the generated files.
