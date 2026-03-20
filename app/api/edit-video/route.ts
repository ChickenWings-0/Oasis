import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';

const EDIT_SCRIPT = path.join(process.cwd(), 'backend/video_generation/edit_video.py');
const OUTPUT_DIR = path.join(process.cwd(), 'public/generated-videos');
const UPLOAD_DIR = path.join(OUTPUT_DIR, 'uploads');
const GENERATED_AUDIO_DIR = path.join(process.cwd(), 'public/generated-audio');

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

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

if (!fs.existsSync(GENERATED_AUDIO_DIR)) {
  fs.mkdirSync(GENERATED_AUDIO_DIR, { recursive: true });
}

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    const primarySourceType = String(formData.get('primarySourceType') ?? 'upload');
    const primaryLibraryFile = String(formData.get('primaryLibraryFile') ?? '');
    const inputFile = formData.get('video');

    const mergeEnabled = String(formData.get('mergeEnabled') ?? 'false') === 'true';
    const mergeSourceType = String(formData.get('mergeSourceType') ?? 'upload');
    const mergeLibraryFile = String(formData.get('mergeLibraryFile') ?? '');
    const mergeFile = formData.get('mergeVideo');

    const audioSourceType = String(formData.get('audioSourceType') ?? 'none');
    const audioLibraryFile = String(formData.get('audioLibraryFile') ?? '');
    const audioFile = formData.get('audioFile');

    const startRaw = formData.get('start');
    const endRaw = formData.get('end');
    const speedRaw = formData.get('speed');
    const volumeRaw = formData.get('volume');
    const muteRaw = formData.get('mute');

    const primaryInputPath = await resolveVideoInputPath({
      sourceType: primarySourceType,
      libraryFile: primaryLibraryFile,
      uploadedFile: inputFile,
      timestamp: Date.now(),
      suffix: 'primary',
    });

    if (!primaryInputPath) {
      return NextResponse.json({ error: 'Primary video is required' }, { status: 400, headers: corsHeaders });
    }

    const timestamp = Date.now();

    const mergeInputPath = mergeEnabled
      ? await resolveVideoInputPath({
          sourceType: mergeSourceType,
          libraryFile: mergeLibraryFile,
          uploadedFile: mergeFile,
          timestamp,
          suffix: 'merge',
        })
      : null;

    if (mergeEnabled && !mergeInputPath) {
      return NextResponse.json({ error: 'Merge video is required when merge is enabled' }, { status: 400, headers: corsHeaders });
    }

    const audioInputPath = await resolveAudioInputPath({
      sourceType: audioSourceType,
      libraryFile: audioLibraryFile,
      uploadedFile: audioFile,
      timestamp,
    });

    if (audioSourceType !== 'none' && !audioInputPath) {
      return NextResponse.json({ error: 'Audio source is invalid or missing' }, { status: 400, headers: corsHeaders });
    }

    const start = Number(startRaw);
    const end = Number(endRaw);
    const speed = Number(speedRaw ?? 1);
    const volume = Number(volumeRaw ?? 1);
    const mute = String(muteRaw ?? 'false') === 'true';

    if (!Number.isFinite(start) || !Number.isFinite(end)) {
      return NextResponse.json({ error: 'Invalid trim values' }, { status: 400, headers: corsHeaders });
    }

    if (start < 0 || end <= start) {
      return NextResponse.json({ error: 'Invalid trim range' }, { status: 400, headers: corsHeaders });
    }

    if (!Number.isFinite(speed) || speed < 0.25 || speed > 4) {
      return NextResponse.json({ error: 'Speed must be between 0.25 and 4.0' }, { status: 400, headers: corsHeaders });
    }

    if (!Number.isFinite(volume) || volume < 0 || volume > 2) {
      return NextResponse.json({ error: 'Volume must be between 0.0 and 2.0' }, { status: 400, headers: corsHeaders });
    }

    const outputFilename = `edited_${timestamp}.mp4`;
    const outputPath = path.join(OUTPUT_DIR, outputFilename);

    const result = await editVideoWithPython({
      inputPath: primaryInputPath,
      outputPath,
      mergeInputPath,
      audioInputPath,
      start,
      end,
      speed,
      volume,
      mute,
    });

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Video editing failed' },
        { status: 500, headers: corsHeaders }
      );
    }

    return NextResponse.json(
      {
        success: true,
        videoUrl: `/generated-videos/${outputFilename}`,
      },
      { status: 200, headers: corsHeaders }
    );
  } catch (error) {
    console.error('Edit video error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500, headers: corsHeaders });
  }
}

type EditVideoArgs = {
  inputPath: string;
  outputPath: string;
  mergeInputPath: string | null;
  audioInputPath: string | null;
  start: number;
  end: number;
  speed: number;
  volume: number;
  mute: boolean;
};

type ResolveInputArgs = {
  sourceType: string;
  libraryFile: string;
  uploadedFile: FormDataEntryValue | null;
  timestamp: number;
  suffix: string;
};

type ResolveAudioInputArgs = {
  sourceType: string;
  libraryFile: string;
  uploadedFile: FormDataEntryValue | null;
  timestamp: number;
};

function sanitizeFilename(filename: string): string {
  const baseName = path.basename(filename).trim();
  if (!baseName || baseName.includes('..')) {
    return '';
  }
  return baseName;
}

function resolveLibraryVideoPath(filename: string): string | null {
  const safeName = sanitizeFilename(filename);
  if (!safeName) {
    return null;
  }

  const candidatePath = path.join(OUTPUT_DIR, safeName);
  if (fs.existsSync(candidatePath) && fs.statSync(candidatePath).isFile()) {
    return candidatePath;
  }

  return null;
}

function resolveLibraryAudioPath(filename: string): string | null {
  const safeName = sanitizeFilename(filename);
  if (!safeName) {
    return null;
  }

  const candidatePath = path.join(GENERATED_AUDIO_DIR, safeName);
  if (fs.existsSync(candidatePath) && fs.statSync(candidatePath).isFile()) {
    return candidatePath;
  }

  return null;
}

async function writeUploadedFile(uploadedFile: File, targetPath: string): Promise<void> {
  const fileBuffer = Buffer.from(await uploadedFile.arrayBuffer());
  fs.writeFileSync(targetPath, fileBuffer);
}

async function resolveVideoInputPath(args: ResolveInputArgs): Promise<string | null> {
  if (args.sourceType === 'library') {
    return resolveLibraryVideoPath(args.libraryFile);
  }

  if (!(args.uploadedFile instanceof File) || !args.uploadedFile.type.startsWith('video/')) {
    return null;
  }

  const targetPath = path.join(UPLOAD_DIR, `source_${args.suffix}_${args.timestamp}.mp4`);
  await writeUploadedFile(args.uploadedFile, targetPath);
  return targetPath;
}

async function resolveAudioInputPath(args: ResolveAudioInputArgs): Promise<string | null> {
  if (args.sourceType === 'none') {
    return null;
  }

  if (args.sourceType === 'library') {
    return resolveLibraryAudioPath(args.libraryFile);
  }

  if (!(args.uploadedFile instanceof File) || !args.uploadedFile.type.startsWith('audio/')) {
    return null;
  }

  const ext = path.extname(args.uploadedFile.name) || '.mp3';
  const targetPath = path.join(UPLOAD_DIR, `audio_${args.timestamp}${ext}`);
  await writeUploadedFile(args.uploadedFile, targetPath);
  return targetPath;
}

function editVideoWithPython(args: EditVideoArgs): Promise<{ success: boolean; error?: string }> {
  return new Promise((resolve) => {
    const commandArgs = [
      EDIT_SCRIPT,
      '--input',
      args.inputPath,
      '--output',
      args.outputPath,
      '--start',
      args.start.toString(),
      '--end',
      args.end.toString(),
      '--speed',
      args.speed.toString(),
      '--volume',
      args.volume.toString(),
    ];

    if (args.mergeInputPath) {
      commandArgs.push('--merge-input', args.mergeInputPath);
    }

    if (args.audioInputPath) {
      commandArgs.push('--audio-input', args.audioInputPath);
    }

    if (args.mute) {
      commandArgs.push('--mute');
    }

    const pythonProcess = spawn(getPythonExecutable(), commandArgs);

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true });
        return;
      }

      resolve({
        success: false,
        error: extractPythonError(stderr, stdout, code),
      });
    });

    pythonProcess.on('error', (error) => {
      resolve({ success: false, error: error.message });
    });
  });
}

function extractPythonError(stderr: string, stdout: string, code: number | null): string {
  const combined = `${stderr}\n${stdout}`
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  const explicitError = combined.reverse().find((line) => line.startsWith('ERROR:'));
  if (explicitError) {
    return explicitError;
  }

  const traceStartIndex = combined.findIndex((line) => line.startsWith('Traceback'));
  if (traceStartIndex >= 0) {
    return combined.slice(traceStartIndex).join('\n');
  }

  const stderrLines = stderr
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  if (stderrLines.length > 0) {
    return stderrLines.slice(-8).join('\n');
  }

  const stdoutLines = stdout
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  if (stdoutLines.length > 0) {
    return stdoutLines.slice(-8).join('\n');
  }

  return `Process exited with code ${code ?? 'unknown'}`;
}
