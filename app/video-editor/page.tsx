import VideoEditorForm from '@/components/VideoEditorForm';

export default function VideoEditorPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 py-12 px-4">
      <div className="container mx-auto">
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-white mb-4">✂️ Video Editor</h1>
          <p className="text-xl text-slate-300">Edit your videos with trim, speed, and audio controls</p>
        </div>

        <VideoEditorForm />
      </div>
    </main>
  );
}
