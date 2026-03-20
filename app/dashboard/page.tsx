export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 py-12 px-4">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold text-white mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <a
            href="/oasis-studio"
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:bg-slate-700 transition-colors"
          >
            <h2 className="text-2xl font-semibold text-white mb-2">🎞️ Oasis Studio</h2>
            <p className="text-slate-300">Professional AI-first editing workspace with timeline, library, and export.</p>
          </a>

          <a
            href="/video-generator"
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:bg-slate-700 transition-colors"
          >
            <h2 className="text-2xl font-semibold text-white mb-2">🎬 Video Generator</h2>
            <p className="text-slate-300">Create AI videos from text prompts.</p>
          </a>

          <a
            href="/video-editor"
            className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:bg-slate-700 transition-colors"
          >
            <h2 className="text-2xl font-semibold text-white mb-2">✂️ Video Editor</h2>
            <p className="text-slate-300">Upload and edit videos with trim, speed, and audio controls.</p>
          </a>
        </div>
      </div>
    </main>
  );
}
