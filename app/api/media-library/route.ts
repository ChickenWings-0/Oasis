import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const VIDEO_DIR = path.join(process.cwd(), 'public/generated-videos');
const AUDIO_DIR = path.join(process.cwd(), 'public/generated-audio');

if (!fs.existsSync(VIDEO_DIR)) {
  fs.mkdirSync(VIDEO_DIR, { recursive: true });
}

if (!fs.existsSync(AUDIO_DIR)) {
  fs.mkdirSync(AUDIO_DIR, { recursive: true });
}

const VIDEO_EXTENSIONS = new Set(['.mp4', '.mov', '.webm', '.mkv']);
const AUDIO_EXTENSIONS = new Set(['.mp3', '.wav', '.m4a', '.aac', '.ogg']);

function readLibraryFiles(dirPath: string, allowedExtensions: Set<string>): string[] {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  return entries
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .filter((filename) => allowedExtensions.has(path.extname(filename).toLowerCase()))
    .sort((a, b) => b.localeCompare(a));
}

export async function GET() {
  try {
    const videos = readLibraryFiles(VIDEO_DIR, VIDEO_EXTENSIONS);
    const audios = readLibraryFiles(AUDIO_DIR, AUDIO_EXTENSIONS);

    return NextResponse.json({
      videos,
      audios,
    });
  } catch (error) {
    console.error('Media library API error:', error);
    return NextResponse.json({ error: 'Failed to load media library' }, { status: 500 });
  }
}
