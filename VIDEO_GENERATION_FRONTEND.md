# Video Generation Frontend Pages

## Summary

Created comprehensive frontend pages for testing the AI video generation system. Multiple implementation options are available:

---

## 1. **Standalone HTML Page** (Easy to Use)

**File:** [video_generation.html](video_generation.html)

### Features:
- 🎨 Modern UI with gradient design
- 📝 Text prompt input with validation
- 🎬 Model selection (Simple, HuggingFace, Replicate, Local)
- ⏱️ Duration slider (5-60 seconds)
- 🔧 Inference steps control
- 📊 Real-time status updates
- 🎥 Video preview with player

### How to Use:
1. Open `video_generation.html` in your browser
2. Enter a video prompt (min 10, max 500 characters)
3. Select a generation model:
   - **Simple**: Instant (no API needed)
   - **HuggingFace**: 1-5 minutes
   - **Replicate**: 2-5 minutes
   - **Local**: 5-15 minutes (GPU required)
4. Adjust duration and inference steps
5. Click "Generate Video"
6. Watch the generated video in real-time

### Direct Link:
```
file:///c:/java%20d=files/oasis/video_generation.html
```

---

## 2. **React/Next.js Component** (For Integration)

**File:** [app/video-generator/VideoGeneratorPage.tsx](app/video-generator/VideoGeneratorPage.tsx)

### Features:
- ✨ Full React component with hooks
- 🎨 Tailwind CSS styling
- 📱 Fully responsive design
- 🔄 API integration ready
- 📝 Form validation
- 🎥 Inline video preview

### Usage:
```tsx
import VideoGeneratorPage from '@/app/video-generator/VideoGeneratorPage';

export default function Page() {
  return <VideoGeneratorPage />;
}
```

---

## 3. **Updated Video Generator Form Component**

**File:** [components/VideoGeneratorForm.tsx](components/VideoGeneratorForm.tsx)

### New Features Added:
- ✅ Model selection dropdown
- ✅ Inference steps slider
- ✅ Backward compatible with existing code
- ✅ Enhanced form validation
- ✅ Detailed model descriptions

### Usage (Existing Page):
```tsx
import VideoGeneratorForm from '@/components/VideoGeneratorForm';

export default function VideoGeneratorPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 py-12 px-4">
      <div className="container mx-auto">
        <h1 className="text-5xl font-bold text-white mb-4">🎬 Video Generator</h1>
        <VideoGeneratorForm 
          onVideoGenerated={(url) => console.log('Video:', url)} 
        />
      </div>
    </main>
  );
}
```

---

## API Endpoints

### POST `/api/generate-video`

**Request:**
```json
{
  "prompt": "A beautiful sunset landscape with mountains",
  "duration": 5,
  "model": "simple",
  "steps": 25
}
```

**Response (Success):**
```json
{
  "success": true,
  "videoUrl": "/generated-videos/video_1234567890.mp4",
  "message": "Video generated successfully"
}
```

**Response (Error):**
```json
{
  "error": "Error message describing what went wrong",
  "status": 400
}
```

**Validation Rules:**
- `prompt`: 10-500 characters (required)
- `duration`: 5-60 seconds (required)
- `model`: One of `simple`, `huggingface`, `replicate`, `local`
- `steps`: 10-50 (optional, default: 25)

---

## Model Information

### Simple (Default)
- **Speed:** Instant (< 10 seconds)
- **Quality:** Medium
- **Cost:** Free
- **Requirements:** None
- **Use Case:** Quick testing, development

### HuggingFace
- **Speed:** 1-5 minutes  
- **Quality:** High
- **Cost:** Free (with API token)
- **Requirements:** `HF_TOKEN` environment variable
- **Use Case:** Production use, good quality

### Replicate
- **Speed:** 2-5 minutes
- **Quality:** Very High
- **Cost:** Pay-per-use (starts free)
- **Requirements:** `REPLICATE_API_TOKEN` environment variable
- **Use Case:** High-quality production videos

### Local Diffusers
- **Speed:** 5-15 minutes
- **Quality:** Highest
- **Cost:** Free (electricity)
- **Requirements:** GPU with 10-24GB VRAM
- **Use Case:** Maximum quality, offline generation

---

## Testing Instructions

### Test 1: Simple Generation (Instant)
1. Open [video_generation.html](video_generation.html)
2. Enter: `"A smooth blue gradient fading to purple"`
3. Select: `Simple` model
4. Set: Duration 5s, Steps 25
5. Click: "Generate Video"
6. ✅ Should complete in < 10 seconds

### Test 2: Try Different Prompts
```
Examples:
- "A professional corporate animation with smooth transitions"
- "An artistic landscape with mountains and sunset"
- "A geometric pattern animation in vibrant colors"
- "A calm ocean wave flowing smoothly"
```

### Test 3: API Model Selection
1. Select "HuggingFace" or "Replicate" model
2. Note: These require API tokens from `.env.local`
3. If functioning, videos will be more detailed and AI-generated

### Test 4: Duration & Quality Settings
- Experiment with different durations (5s - 60s)
- Adjust inference steps (10 - 50) for quality vs speed tradeoff

---

## Environment Setup

### For HTML Testing:
```bash
# No setup needed! Just open video_generation.html in browser
# Make sure the backend API is running on localhost:3000
```

### For React Component Testing:
```bash
# Ensure Next.js dev server is running
npm run dev

# Then navigate to:
http://localhost:3000/video-generator
```

### API Tokens (Optional):
```env
# .env.local
HF_TOKEN=hf_your_token_here
REPLICATE_API_TOKEN=r8_your_token_here
```

---

## Troubleshooting

### "Video generation failed - API Error"
- ✅ Solution: API endpoint responds with error
- Check backend logs: `python backend/video_generation/generate_video.py`
- Verify model tokens in `.env.local`

### "Connection refused"
- ✅ Solution: Backend API not running
- Start backend: `npm run dev` or `python -m uvicorn app.main:app`

### "Prompt validation error"
- ✅ Solution: Prompt doesn't meet requirements
- Requirements: 10-500 characters, non-empty
- Try: "A simple test video with smooth transitions"

### "Duration out of range"
- ✅ Solution: Selected invalid duration
- Valid range: 5-60 seconds
- Default: 5 seconds

---

## File Structure

```
oasis/
├── video_generation.html          # ← Standalone HTML page (RECOMMENDED)
├── app/
│   ├── video-generator/
│   │   ├── page.tsx              # Main page
│   │   ├── VideoGeneratorPage.tsx # ← New React component
│   │   └── route.ts              # API endpoint
│   └── api/
│       └── generate-video/
│           └── route.ts          # Video generation endpoint
├── components/
│   └── VideoGeneratorForm.tsx     # ← Updated with new features
└── backend/
    └── video_generation/
        ├── generate_video.py      # CLI interface
        ├── models.py             # AI model implementations
        └── output_videos/        # Generated videos
```

---

## Quick Start

### Option 1: Standalone HTML (Recommended for Testing)
```bash
# 1. Ensure backend is running
npm run dev

# 2. Open in browser
# file:///c:/java%20d=files/oasis/video_generation.html

# 3. Start generating videos!
```

### Option 2: React Component (For Integration)
```bash
# 1. Backend running
npm run dev

# 2. Navigate to
# http://localhost:3000/video-generator

# 3. Use the integrated form
```

---

## Next Steps

1. ✅ Test the HTML page with simple model
2. ✅ Verify API integration works
3. ✅ Add API tokens for HuggingFace/Replicate
4. ✅ Deploy to production
5. ✅ Monitor video generation performance

---

## Support

For issues or questions:
- Check [models.py](backend/video_generation/models.py) for model docs
- Review [generate_video.py](backend/video_generation/generate_video.py) for CLI usage
- Check logs in `backend/video_generation/output_videos/`

---

**Created:** March 20, 2026  
**Status:** ✅ Ready for Testing
