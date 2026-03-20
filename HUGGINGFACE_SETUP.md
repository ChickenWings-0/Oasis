# HuggingFace AI Video Generation Setup Guide

## Overview

Your OASIS system is now optimized for **HuggingFace Zeroscope v2 XL** - a state-of-the-art AI video generation model that creates realistic, high-quality videos from text prompts.

## ✅ Current Setup

- **Model**: Zeroscope v2 XL (cerspense/zeroscope_v2_XL)
- **API**: HuggingFace Inference API
- **HF_TOKEN**: Already configured in `.env.local`
- **Quality**: Excellent (realistic, detailed scenes)
- **Speed**: 2-5 minutes per video

## 🎯 How to Use

### 1. Open the Video Generator
```
http://localhost:3000/video_generation.html
```

### 2. Select Model
- **Default**: HuggingFace (🤖 Zeroscope v2 XL) - BEST QUALITY
- Model is now pre-selected for you

### 3. Enter Prompt
Examples of good prompts:
- "A sunset over the ocean with waves"
- "A car driving through a forest at sunset"
- "A astronaut walking on the moon"
- "A futuristic city at night with neon lights"
- "A hot air balloon floating in the sky"

**Tips for better results:**
- Be descriptive and specific
- Include lighting/mood (sunset, nighttime, foggy, etc.)
- Mention colors and textures
- Keep it between 10-500 characters

### 4. Adjust Parameters
- **Duration**: 5-60 seconds (default: 5 seconds is good for first test)
- **Inference Steps**: 
  - Fast (10-20): Quicker generation, decent quality
  - Medium (25-30): Balanced (default: 25)
  - Quality (40-50): Slower but higher quality

### 5. Generate Video
- Click "GENERATE VIDEO"
- **Wait 2-5 minutes** (progress spinner shows it's working)
- Video appears when ready
- Automatically saved to `public/generated-videos/`

## 📊 Model Comparison

| Model | Speed | Quality | API Required | Cost |
|-------|-------|---------|--------------|------|
| **HuggingFace** | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent | Yes (Free) | Free |
| **Replicate** | ⚡⚡ Medium | ⭐⭐⭐⭐ Very Good | Yes (Paid) | ~$0.15/video |
| **Local Diffusers** | ⚡ Slow | ⭐⭐⭐⭐⭐ Excellent | No | Free (GPU needed) |
| **Simple** | ⚡⚡⚡ Instant | ⭐⭐ Basic | No | Free |

## 🔧 Advanced Configuration

### Change Model Quality
Edit inference steps:
- **Fast**: 10-15 steps (~2 minutes)
- **Medium**: 25 steps (~3 minutes) - Recommended
- **High**: 40-50 steps (~4-5 minutes)

### Try Different HF Models
In `backend/video_generation/models.py`, line 59:
```python
model_id: str = "cerspense/zeroscope_v2_XL",  # Change this
```

Alternative models:
- `cerspense/zeroscope_v2_576w` (smaller, faster)
- `damo-vilab/text-to-video-ms-1.7b` (different style)
- `text2video-zero/text2video-zero-base` (experimental)

## ⚡ Troubleshooting

### "Error: HuggingFace API token not configured"
- **Fix**: Ensure `.env.local` has `HF_TOKEN` set
- Get token from: https://huggingface.co/settings/tokens

### "API Error: 503 Service Unavailable"
- **Cause**: HuggingFace model is loading (first request)
- **Fix**: Wait 2-3 minutes, then try again
- **Note**: First request may take longer as model initializes

### "Error: HTTP 429: Too Many Requests"
- **Cause**: Rate limited by HuggingFace
- **Fix**: Wait a few minutes before next request

### Slow Generation
- **Cause**: Server is busy or model is processing
- **Expected**: 2-5 minutes is normal
- **Tip**: Use `--steps 25` or lower for faster results

## 📈 Performance Tips

1. **Start with defaults**: 
   - Duration: 5 seconds
   - Steps: 25
   - This is ~3 minutes total

2. **Increase quality gradually**:
   - If happy with results but want better: increase steps to 40
   - If taking too long: decrease steps to 15-20

3. **Monitor backend logs**:
   - Check terminal running `npm run dev`
   - See real-time progress of video generation

## 🎓 Understanding Parameters

- **Duration (5-60s)**: How long the video will be
  - Shorter = faster generation
  - Longer = better for detailed stories

- **Inference Steps (10-50)**: How many times the model refines the video
  - Lower = faster but lower quality
  - Higher = slower but better quality
  - Sweet spot: 25 steps for 3-4 minutes

## 🚀 Next Steps

1. ✅ Test with "Simple" model (instant feedback)
2. ✅ Try HuggingFace with short prompts first
3. ✅ Experiment with different prompts
4. ✅ Increase steps for better quality if needed
5. ⭐ Share your favorite videos!

## 📚 Resources

- HuggingFace: https://huggingface.co
- Zeroscope Model: https://huggingface.co/cerspense/zeroscope_v2_XL
- Get Free API Token: https://huggingface.co/settings/tokens
- Prompt Engineering Tips: https://huggingface.co/docs/inference-endpoints/guides/prompt_engineering

## 💡 Pro Tips

- **Good prompts** are key to good videos
- Start simple, get more creative with experience
- Use descriptive language (colors, lighting, mood)
- Video generation is both art and science
- Experiment with different step counts
