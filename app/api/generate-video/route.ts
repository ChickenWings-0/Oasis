import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import { spawn } from 'child_process';
import fs from 'fs';

const BACKEND_SCRIPT = path.join(process.cwd(), 'backend/video_generation/generate_video.py');
const OUTPUT_DIR = path.join(process.cwd(), 'public/generated-videos');

function getPythonExecutable(): string {
  if (process.env.PYTHON_PATH) {
    return process.env.PYTHON_PATH;
  }

  const windowsVenvPython = path.join(process.cwd(), '.venv', 'Scripts', 'python.exe');
  if (fs.existsSync(windowsVenvPython)) {
    return windowsVenvPython;
  }

  const unixVenvPython = path.join(process.cwd(), '.venv', 'bin', 'python');
  if (fs.existsSync(unixVenvPython)) {
    return unixVenvPython;
  }

  return 'python';
}

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// Handle OPTIONS request for CORS
export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, duration, model = 'simple', steps = 25 } = body;

    // Validation
    if (!prompt || typeof prompt !== 'string') {
      return NextResponse.json(
        { error: 'Invalid or missing prompt' },
        { status: 400 }
      );
    }

    if (prompt.length < 10 || prompt.length > 500) {
      return NextResponse.json(
        { error: 'Prompt must be between 10 and 500 characters' },
        { status: 400 }
      );
    }

    if (!duration || duration < 5 || duration > 60) {
      return NextResponse.json(
        { error: 'Duration must be between 5 and 60 seconds' },
        { status: 400 }
      );
    }

    if (!['simple', 'huggingface', 'replicate', 'local_diffusers'].includes(model)) {
      return NextResponse.json(
        { error: 'Invalid model. Must be: simple, huggingface, replicate, or local_diffusers' },
        { status: 400 }
      );
    }

    if (steps < 10 || steps > 50) {
      return NextResponse.json(
        { error: 'Steps must be between 10 and 50' },
        { status: 400 }
      );
    }

    // Generate unique filename
    const timestamp = Date.now();
    const outputFile = path.join(OUTPUT_DIR, `video_${timestamp}.mp4`);
    const videoUrl = `/generated-videos/video_${timestamp}.mp4`;

    // Call Python backend
    const result = await generateVideoWithPython(prompt, duration, outputFile, model, steps);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Failed to generate video' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      videoUrl,
      message: 'Video generated successfully',
    }, {
      status: 200,
      headers: corsHeaders
    });
  } catch (error) {
    console.error('Video generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500, headers: corsHeaders }
    );
  }
}

function generateVideoWithPython(
  prompt: string,
  duration: number,
  outputPath: string,
  model: string = 'simple',
  steps: number = 25
): Promise<{ success: boolean; error?: string }> {
  return new Promise((resolve) => {
    try {
      const args = [
        BACKEND_SCRIPT,
        '--prompt',
        prompt,
        '--duration',
        duration.toString(),
        '--output',
        outputPath,
        '--model',
        model,
        '--steps',
        steps.toString(),
      ];

      const pythonProcess = spawn(getPythonExecutable(), args);

      let stderr = '';
      let stdout = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log(`Python output: ${data}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error(`Python error: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true });
        } else {
          resolve({
            success: false,
            error: stderr || `Process exited with code ${code}`,
          });
        }
      });

      pythonProcess.on('error', (error) => {
        resolve({
          success: false,
          error: error.message,
        });
      });
    } catch (error) {
      resolve({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });
}
