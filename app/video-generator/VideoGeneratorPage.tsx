'use client';

import { useState } from 'react';
import Image from 'next/image';

export default function VideoGenerator() {
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('simple');
  const [duration, setDuration] = useState(5);
  const [steps, setSteps] = useState(25);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState('info');
  const [videoUrl, setVideoUrl] = useState('');
  const [videoMetadata, setVideoMetadata] = useState('');

  const modelDescriptions = {
    simple: 'Fast text-based generation with animated gradients (instant)',
    huggingface: 'AI-powered video generation using HuggingFace API (1-5 minutes)',
    replicate: 'High-quality AI generation via Replicate (2-5 minutes)',
    local: 'Premium local generation with Diffusers (5-15 minutes, GPU required)'
  };

  const handleClear = () => {
    setPrompt('');
    setModel('simple');
    setDuration(5);
    setSteps(25);
    setVideoUrl('');
    setVideoMetadata('');
    setStatus('');
  };

  const handleGenerate = async () => {
    // Validation
    if (!prompt.trim()) {
      setStatus('Please enter a prompt');
      setStatusType('error');
      return;
    }

    if (prompt.length < 10) {
      setStatus('Prompt must be at least 10 characters');
      setStatusType('error');
      return;
    }

    if (prompt.length > 500) {
      setStatus('Prompt cannot exceed 500 characters');
      setStatusType('error');
      return;
    }

    setLoading(true);
    setStatus('🎬 Generating video... This may take a few minutes.');
    setStatusType('info');
    setVideoUrl('');

    try {
      const response = await fetch('/api/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          duration: duration,
          model: model,
          steps: steps
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate video');
      }

      setVideoUrl(data.videoUrl);
      setVideoMetadata(`
        ✓ Video generated successfully!
        Prompt: ${prompt}
        Duration: ${duration}s | Model: ${model}
      `);
      setStatus('✓ Video generated successfully!');
      setStatusType('success');

    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
      setStatusType('error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = () => {
    switch (statusType) {
      case 'success':
        return 'text-green-600 bg-green-50';
      case 'error':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-blue-600 bg-blue-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-pink-600 py-12 px-4">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            🎬 AI Video Generator
          </h1>
          <p className="text-gray-600">OASIS - Create videos from text prompts</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="space-y-6">
            {/* Prompt */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 uppercase tracking-wide mb-2">
                Video Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the video you want to generate. Be creative and specific!"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-600 focus:ring-2 focus:ring-purple-200 resize-none"
                rows={4}
                maxLength={500}
              />
              <p className="text-xs text-gray-500 mt-2">
                {prompt.length}/500 characters
              </p>
            </div>

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 uppercase tracking-wide mb-2">
                Generation Model
              </label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-600 focus:ring-2 focus:ring-purple-200"
              >
                <option value="simple">Simple (Instant - No API)</option>
                <option value="huggingface">HuggingFace (AI-Powered)</option>
                <option value="replicate">Replicate (Recommended)</option>
                <option value="local">Local Diffusers (GPU-Required)</option>
              </select>
              <p className="text-xs text-gray-500 mt-2">
                {modelDescriptions[model as keyof typeof modelDescriptions]}
              </p>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 uppercase tracking-wide mb-2">
                Duration: <span className="text-purple-600">{duration}s</span>
              </label>
              <input
                type="range"
                min="5"
                max="60"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>5s</span>
                <span>60s</span>
              </div>
            </div>

            {/* Inference Steps */}
            <div>
              <label className="block text-sm font-semibold text-gray-800 uppercase tracking-wide mb-2">
                Inference Steps: <span className="text-purple-600">{steps}</span>
              </label>
              <input
                type="range"
                min="10"
                max="50"
                value={steps}
                onChange={(e) => setSteps(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Fast</span>
                <span>Quality</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">More steps = better quality but slower</p>
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transform hover:-translate-y-1 transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wide"
              >
                {loading ? '🔄 Generating...' : '🎬 Generate Video'}
              </button>
              <button
                onClick={handleClear}
                className="flex-1 bg-gray-200 text-gray-800 font-semibold py-3 px-6 rounded-lg hover:bg-gray-300 transition uppercase tracking-wide"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Preview Section */}
          <div className="space-y-6">
            {/* Status */}
            {status && (
              <div className={`p-4 rounded-lg ${getStatusColor()} border border-current border-opacity-20`}>
                <p className="font-semibold text-sm">{status}</p>
              </div>
            )}

            {/* Video Preview */}
            {videoUrl && (
              <div className="bg-gray-100 rounded-lg overflow-hidden">
                <video
                  src={videoUrl}
                  controls
                  className="w-full bg-black"
                />
                <div className="p-4 bg-gray-50 border-t border-gray-200 text-sm text-gray-700">
                  <p className="font-semibold mb-2">✓ Video Generated Successfully!</p>
                  <p className="text-xs whitespace-pre-wrap">{videoMetadata}</p>
                </div>
              </div>
            )}

            {/* Info Box */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">📋 Model Information</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p><strong>Simple:</strong> Fast local generation, no API required</p>
                <p><strong>HuggingFace:</strong> AI-powered with HF API token</p>
                <p><strong>Replicate:</strong> Most reliable, requires Replicate API key</p>
                <p><strong>Local:</strong> Highest quality but requires GPU (10-24GB VRAM)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
