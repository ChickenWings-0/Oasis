'use client';

import { useState } from 'react';

export default function VideoGeneratorForm() {
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('simple');
  const [duration, setDuration] = useState(10);
  const [steps, setSteps] = useState(25);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [progress, setProgress] = useState(0);

  const modelDescriptions = {
    simple: 'Fast text-based generation with animated gradients (instant)',
    huggingface: 'AI-powered video generation using HuggingFace API (1-5 minutes)',
    replicate: 'High-quality AI generation via Replicate (2-5 minutes)',
    local: 'Premium local generation with Diffusers (5-15 minutes, GPU required)'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setVideoUrl('');
    setProgress(0);
    setLoading(true);

    try {
      const response = await fetch('/api/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          duration,
          model,
          steps,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        try {
          const errorData = JSON.parse(text);
          throw new Error(errorData.error || `HTTP ${response.status}`);
        } catch (e) {
          throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
        }
      }

      const data = await response.json();
      setVideoUrl(data.videoUrl);
      setProgress(100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl">
      <h2 className="text-3xl font-bold text-white mb-2">AI Video Generator</h2>
      <p className="text-slate-300 mb-6">Transform your text into engaging videos using AI</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Text Prompt Input */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Video Prompt
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want your video to show. Be creative and detailed!"
            className="w-full h-32 px-4 py-3 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
            disabled={loading}
          />
          <p className="text-xs text-slate-400 mt-1">Min 10 characters, max 500 characters</p>
        </div>

        {/* Model Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Generation Model
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-4 py-3 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500"
            disabled={loading}
          >
            <option value="simple">Simple (Instant - No API)</option>
            <option value="huggingface">HuggingFace (AI-Powered)</option>
            <option value="replicate">Replicate (Recommended)</option>
            <option value="local">Local Diffusers (GPU-Required)</option>
          </select>
          <p className="text-xs text-slate-400 mt-1">
            {modelDescriptions[model as keyof typeof modelDescriptions]}
          </p>
        </div>

        {/* Duration Slider */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Video Duration: {duration}s
          </label>
          <input
            type="range"
            min="5"
            max="60"
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            disabled={loading}
          />
          <p className="text-xs text-slate-400 mt-1">5 - 60 seconds</p>
        </div>

        {/* Inference Steps */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Inference Steps: {steps}
          </label>
          <input
            type="range"
            min="10"
            max="50"
            value={steps}
            onChange={(e) => setSteps(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            disabled={loading}
          />
          <p className="text-xs text-slate-400 mt-1">More steps = better quality but slower (10-50)</p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !prompt.trim()}
          className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 ${
            loading || !prompt.trim()
              ? 'bg-slate-600 cursor-not-allowed opacity-50'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating Video... {progress}%
            </span>
          ) : (
            'Generate Video'
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mt-6 p-4 bg-red-900 border border-red-700 rounded-lg">
          <p className="text-red-200">
            <span className="font-semibold">Error:</span> {error}
          </p>
        </div>
      )}

      {/* Video Preview */}
      {videoUrl && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-white mb-4">Generated Video</h3>
          <video
            src={videoUrl}
            controls
            className="w-full rounded-lg border border-slate-600 shadow-lg"
          />
          <a
            href={videoUrl}
            download
            className="inline-block mt-4 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
          >
            Download Video
          </a>
        </div>
      )}
    </div>
  );
}
