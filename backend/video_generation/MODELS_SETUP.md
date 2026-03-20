# Video Generation Models Setup Guide

## Overview

The video generation system now supports multiple backends:
1. **Simple Text-Based** (default) - Fast, no API required
2. **HuggingFace API** - AI-powered text-to-video
3. **Local Diffusers** - Run models locally (requires GPU)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set HuggingFace API Token

For HuggingFace-powered generation, you need a free API token:

```bash
# Linux/Mac
export HF_TOKEN="your_huggingface_api_token"

# Windows PowerShell
$env:HF_TOKEN = "your_huggingface_api_token"
```

Get your token from: https://huggingface.co/settings/tokens

---

## Usage Examples

### Simple Text-Based Generation (No API Required)
```bash
python generate_video.py \
  --prompt "A beautiful sunset over the ocean with waves crashing" \
  --duration 10 \
  --output output.mp4
```

### Using HuggingFace Zeroscope V2 XL (Recommended)
```bash
python generate_video.py \
  --prompt "A cat walking through a sunny garden" \
  --model huggingface \
  --model-id cerspense/zeroscope_v2_XL \
  --steps 25 \
  --output output.mp4
```

### Using Alternative HuggingFace Models
```bash
# Zeroscope V2 576w (faster, lower quality)
python generate_video.py \
  --prompt "A robot dancing in the rain" \
  --model huggingface \
  --model-id cerspense/zeroscope_v2_576w \
  --steps 20 \
  --output output.mp4

# DAMO VideoGen
python generate_video.py \
  --prompt "A bicycle riding through mountains" \
  --model huggingface \
  --model-id damo-vilab/text-to-video-ms-1.7b \
  --steps 30 \
  --output output.mp4
```

---

## Available HuggingFace Models

| Model | Quality | Speed | VRAM Req | Best For |
|-------|---------|-------|----------|----------|
| `cerspense/zeroscope_v2_XL` | ⭐⭐⭐⭐ High | ⏱️ Slow | 12GB | Production |
| `cerspense/zeroscope_v2_576w` | ⭐⭐⭐ Medium | ⏱️ Medium | 6GB | Balance |
| `damo-vilab/text-to-video-ms-1.7b` | ⭐⭐ Lower | ⏱️ Fast | 4GB | Testing |

---

## Python API Usage

### Basic Text-Based Generation
```python
from generate_video import generate_video

success = generate_video(
    prompt="A spaceship flying through an asteroid field",
    duration=10,
    output_path="space.mp4"
)
```

### Using HuggingFace Model
```python
from generate_video import generate_video

success = generate_video(
    prompt="A magical forest with glowing trees",
    model_type="huggingface",
    model_id="cerspense/zeroscope_v2_XL",
    num_inference_steps=25,
    output_path="forest.mp4"
)
```

### Using Model Classes Directly
```python
from models import get_model

# Get HuggingFace model
model = get_model(
    model_type="huggingface",
    model_id="cerspense/zeroscope_v2_XL"
)

# Generate video
result = model.generate(
    prompt="An underwater city",
    num_inference_steps=25,
    output_path="underwater.mp4"
)

if result['success']:
    print(f"Video saved to: {result['output_path']}")
    print(f"Metadata: {result['metadata']}")
else:
    print(f"Error: {result['error']}")
```

---

## HuggingFace API Limitations

- **Rate Limiting**: Free tier has limited concurrent requests
- **Timeout**: 5-minute timeout per request (videos take 2-5 minutes)
- **Concurrent Requests**: Limited on free tier
- **Cost**: Free tier available, paid tier for production

### Recommended for Production:
- Use queue-based async job processing (Celery + Redis)
- Implement retry logic with exponential backoff
- Cache frequently used prompts
- Monitor API usage and costs

---

## Local Diffusers Setup (Advanced)

For local GPU inference without API calls:

### 1. Install Additional Dependencies
```bash
# Uncomment in requirements.txt and install:
pip install torch diffusers transformers accelerate
```

### 2. Usage
```python
from generate_video import generate_video

success = generate_video(
    prompt="A phoenix rising from flames",
    model_type="local_diffusers",
    output_path="phoenix.mp4"
)
```

### Requirements:
- **NVIDIA GPU** with 12GB+ VRAM (recommended)
- PyTorch with CUDA support
- 30-60 seconds per video generation
- No API key needed

---

## Integration with Next.js API Route

Update `app/api/generate-video/route.ts` to use the AI model:

```typescript
const args = [
  BACKEND_SCRIPT,
  '--prompt', prompt,
  '--duration', duration.toString(),
  '--output', outputFile,
  '--model', 'huggingface',
  '--model-id', 'cerspense/zeroscope_v2_576w',
  '--steps', '25'
];
```

Or add environment variable:
```bash
# .env.local
NEXT_PUBLIC_VIDEO_MODEL=huggingface
HUGGINGFACE_API_TOKEN=your_token_here
```

---

## Troubleshooting

### "HuggingFace API token not configured"
```bash
export HF_TOKEN="your_token"
# Verify:
echo $HF_TOKEN
```

### "API Error: 429 - Rate Limited"
- Free tier has concurrent request limits
- Implement queue-based generation
- Consider upgrading HuggingFace plan

### "Timeout Error (>5 minutes)"
- Model is taking too long
- Try faster model: `zeroscope_v2_576w`
- Reduce `--steps` to 20

### CUDA Out of Memory
- Use `cerspense/zeroscope_v2_576w` instead
- Reduce inference steps
- Free up other GPU processes

---

## Environment Variables

```bash
# Required for HuggingFace
HF_TOKEN=hf_xxxxxxxxxxxxxxxx

# Optional - customize API behavior
HF_API_URL=https://api-inference.huggingface.co/models
VIDEO_GENERATION_TIMEOUT=300  # seconds
```

---

## Next Steps

1. ✅ Install dependencies and set HF_TOKEN
2. ✅ Test with simple text-based generation
3. ✅ Test with HuggingFace API
4. ✅ Integrate with Next.js API route
5. ✅ Set up job queue for production
6. ✅ Monitor and optimize performance

---

## References

- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [Zeroscope Models](https://huggingface.co/cerspense/zeroscope_v2_XL)
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [DAMO VideoGen](https://huggingface.co/damo-vilab/text-to-video-ms-1.7b)
