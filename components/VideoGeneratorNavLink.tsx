'use client';

export function VideoGeneratorNavLink() {
  return (
    <a
      href="/video-generator"
      className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors text-white"
    >
      <span>🎬</span>
      <span>Video Generator</span>
    </a>
  );
}
