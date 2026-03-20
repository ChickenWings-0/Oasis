#!/usr/bin/env python3
"""
Quick setup and test guide for video generation
"""

import subprocess
import time
import os
from pathlib import Path

print("=" * 70)
print("OASIS VIDEO GENERATION - QUICK START GUIDE")
print("=" * 70)

print("\n✅ STEP 1: Ensure backend is running")
print("-" * 70)
print("Run in terminal:")
print("  npm run dev")
print("\nThis starts the Next.js server on http://localhost:3000")

print("\n✅ STEP 2: Access the video generator")
print("-" * 70)
print("Open in browser:\n")
print("  Option A (Recommended): http://localhost:3000/video_generation.html")
print("  Option B (React Page):  http://localhost:3000/video-generator")
print("  Option C (Standalone):  file:///c:/java%20d=files/oasis/video_generation.html")

print("\n✅ STEP 3: Test the video generation")
print("-" * 70)
print("1. Enter prompt: 'A sunset where a car is going'")
print("2. Select model: 'Simple' (fastest)")
print("3. Duration: 5 seconds")
print("4. Inference steps: 25")
print("5. Click 'Generate Video'")
print("6. Wait 5-30 seconds for video to generate")

print("\n✅ Available Models:")
print("-" * 70)
print("  • Simple       - Instant (< 10 seconds) - RECOMMENDED")
print("  • HuggingFace  - 1-5 minutes (requires HF_TOKEN)")
print("  • Replicate    - 2-5 minutes (requires REPLICATE_API_TOKEN)")
print("  • Local        - 5-15 minutes (requires GPU)")

print("\n✅ Troubleshooting:")
print("-" * 70)
print("Error: 'HTTP 405: Method Not Allowed'")
print("  → Make sure you're accessing via http://localhost:3000/")
print("  → Don't open the HTML file directly (file://)")
print("")
print("Error: 'Connection refused'")
print("  → Run 'npm run dev' to start the server")
print("")
print("Error: 'API Error'")
print("  → Check backend logs in terminal")
print("  → Try the 'Simple' model first")

print("\n✅ Files:")
print("-" * 70)
print("  HTML Page:        public/video_generation.html")
print("  React Component:  app/video-generator/VideoGeneratorPage.tsx")
print("  API Endpoint:     app/api/generate-video/route.ts")
print("  Backend:          backend/video_generation/generate_video.py")
print("  Generated videos: public/generated-videos/")

print("\n" + "=" * 70)
print("Ready to test! 🎬")
print("=" * 70)
print("\n1. Start backend: npm run dev")
print("2. Open: http://localhost:3000/video_generation.html")
print("3. Generate your first video!")
