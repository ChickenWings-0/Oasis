import VideoGeneratorForm from '@/components/VideoGeneratorForm';

export default function VideoGeneratorPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 py-12 px-4">
      <div className="container mx-auto">
        {/* Header */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            🎬 Video Generator
          </h1>
          <p className="text-xl text-slate-300">
            Create stunning AI-generated videos from text prompts
          </p>
        </div>

        {/* Video Generator Form */}
        <VideoGeneratorForm />

        {/* Info Section */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="text-3xl mb-3">✨</div>
            <h3 className="text-lg font-semibold text-white mb-2">AI-Powered</h3>
            <p className="text-slate-300">Advanced AI models generate videos from your text descriptions</p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="text-lg font-semibold text-white mb-2">Fast Processing</h3>
            <p className="text-slate-300">Generate professional-quality videos in minutes, not hours</p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold text-white mb-2">Customizable</h3>
            <p className="text-slate-300">Adjust duration and details to match your vision perfectly</p>
          </div>
        </div>
      </div>
    </main>
  );
}
