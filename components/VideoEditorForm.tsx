'use client';

import { useEffect, useMemo, useState } from 'react';

type MediaLibraryResponse = {
  videos: string[];
  audios: string[];
};

export default function VideoEditorForm() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [primarySourceType, setPrimarySourceType] = useState<'upload' | 'library'>('upload');
  const [primaryLibraryFile, setPrimaryLibraryFile] = useState('');

  const [mergeEnabled, setMergeEnabled] = useState(false);
  const [mergeSourceType, setMergeSourceType] = useState<'upload' | 'library'>('upload');
  const [mergeVideoFile, setMergeVideoFile] = useState<File | null>(null);
  const [mergeLibraryFile, setMergeLibraryFile] = useState('');

  const [audioSourceType, setAudioSourceType] = useState<'none' | 'upload' | 'library'>('none');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioLibraryFile, setAudioLibraryFile] = useState('');

  const [sourcePreviewUrl, setSourcePreviewUrl] = useState('');
  const [editedVideoUrl, setEditedVideoUrl] = useState('');

  const [duration, setDuration] = useState(0);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(0);

  const [speed, setSpeed] = useState(1);
  const [mute, setMute] = useState(false);
  const [volume, setVolume] = useState(1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mediaLibrary, setMediaLibrary] = useState<MediaLibraryResponse>({ videos: [], audios: [] });
  const [loadingLibrary, setLoadingLibrary] = useState(false);
  const [inspectorTab, setInspectorTab] = useState<'video' | 'audio' | 'speed'>('video');

  const maxEnd = useMemo(() => (duration > 0 ? duration : 1), [duration]);

  useEffect(() => {
    const loadLibrary = async () => {
      setLoadingLibrary(true);
      try {
        const response = await fetch('/api/media-library');
        if (!response.ok) {
          throw new Error('Failed to load media library');
        }

        const data = (await response.json()) as MediaLibraryResponse;
        setMediaLibrary(data);

        if (data.videos.length > 0 && !primaryLibraryFile) {
          setPrimaryLibraryFile(data.videos[0]);
        }

        if (data.videos.length > 1 && !mergeLibraryFile) {
          setMergeLibraryFile(data.videos[1]);
        }

        if (data.audios.length > 0 && !audioLibraryFile) {
          setAudioLibraryFile(data.audios[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load media library.');
      } finally {
        setLoadingLibrary(false);
      }
    };

    loadLibrary();
  }, []);

  useEffect(() => {
    if (primarySourceType === 'library' && primaryLibraryFile) {
      setSourcePreviewUrl(`/generated-videos/${primaryLibraryFile}`);
      return;
    }

    if (primarySourceType === 'upload' && videoFile) {
      const objectUrl = URL.createObjectURL(videoFile);
      setSourcePreviewUrl(objectUrl);
      return () => URL.revokeObjectURL(objectUrl);
    }

    setSourcePreviewUrl('');
  }, [primarySourceType, primaryLibraryFile, videoFile]);

  const onSelectPrimaryFile = (file: File | null) => {
    setError('');
    setEditedVideoUrl('');

    if (!file) {
      setVideoFile(null);
      setDuration(0);
      setStart(0);
      setEnd(0);
      return;
    }

    if (!file.type.startsWith('video/')) {
      setError('Please select a valid video file.');
      return;
    }

    setVideoFile(file);
  };

  const onSelectMergeFile = (file: File | null) => {
    setError('');

    if (!file) {
      setMergeVideoFile(null);
      return;
    }

    if (!file.type.startsWith('video/')) {
      setError('Please select a valid merge video file.');
      return;
    }

    setMergeVideoFile(file);
  };

  const onSelectAudioFile = (file: File | null) => {
    setError('');

    if (!file) {
      setAudioFile(null);
      return;
    }

    if (!file.type.startsWith('audio/')) {
      setError('Please select a valid audio file.');
      return;
    }

    setAudioFile(file);
  };

  const handleMetadataLoaded = (metadataDuration: number) => {
    const rounded = Math.max(1, Math.floor(metadataDuration));
    setDuration(rounded);
    setStart(0);
    setEnd(rounded);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (end <= start) {
      setError('End time must be greater than start time.');
      return;
    }

    if (primarySourceType === 'upload' && !videoFile) {
      setError('Please upload a primary video.');
      return;
    }

    if (primarySourceType === 'library' && !primaryLibraryFile) {
      setError('Please select a primary video from Oasis library.');
      return;
    }

    if (mergeEnabled && mergeSourceType === 'upload' && !mergeVideoFile) {
      setError('Please upload a merge video.');
      return;
    }

    if (mergeEnabled && mergeSourceType === 'library' && !mergeLibraryFile) {
      setError('Please select a merge video from Oasis library.');
      return;
    }

    if (audioSourceType === 'upload' && !audioFile) {
      setError('Please upload an audio file.');
      return;
    }

    if (audioSourceType === 'library' && !audioLibraryFile) {
      setError('Please select an Oasis audio file.');
      return;
    }

    setLoading(true);
    setError('');
    setEditedVideoUrl('');

    try {
      const formData = new FormData();
      formData.append('primarySourceType', primarySourceType);
      formData.append('primaryLibraryFile', primaryLibraryFile);
      formData.append('start', String(start));
      formData.append('end', String(end));
      formData.append('speed', String(speed));
      formData.append('mute', String(mute));
      formData.append('volume', String(volume));
      formData.append('mergeEnabled', String(mergeEnabled));
      formData.append('mergeSourceType', mergeSourceType);
      formData.append('mergeLibraryFile', mergeLibraryFile);
      formData.append('audioSourceType', audioSourceType);
      formData.append('audioLibraryFile', audioLibraryFile);

      if (primarySourceType === 'upload' && videoFile) {
        formData.append('video', videoFile);
      }

      if (mergeEnabled && mergeSourceType === 'upload' && mergeVideoFile) {
        formData.append('mergeVideo', mergeVideoFile);
      }

      if (audioSourceType === 'upload' && audioFile) {
        formData.append('audioFile', audioFile);
      }

      const response = await fetch('/api/edit-video', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to edit video');
      }

      setEditedVideoUrl(data.videoUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while editing the video.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[1400px] mx-auto p-4 md:p-5 bg-slate-900 rounded-xl border border-slate-700 shadow-2xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="h-14 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between px-4">
          <div className="text-slate-300 text-sm">Creator Studio</div>
          <div className="text-white font-medium">oasis_project.orc</div>
          <button
            type="submit"
            disabled={loading || (primarySourceType === 'upload' && !videoFile) || (primarySourceType === 'library' && !primaryLibraryFile)}
            className={`px-5 py-2 rounded-md text-sm font-semibold transition-colors ${
              loading ? 'bg-slate-700 text-slate-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white'
            }`}
          >
            {loading ? 'Exporting...' : 'Export'}
          </button>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[60px_320px_1fr_340px] gap-3">
          <aside className="bg-slate-950 border border-slate-800 rounded-lg py-3 flex flex-col items-center gap-5 text-slate-400 text-lg">
            <button type="button" className="hover:text-white">◉</button>
            <button type="button" className="hover:text-white">▶</button>
            <button type="button" className="hover:text-white">✚</button>
            <button type="button" className="hover:text-white">⌗</button>
            <button type="button" className="hover:text-white">𝕋</button>
            <button type="button" className="hover:text-white">♫</button>
            <button type="button" className="hover:text-white">⇪</button>
          </aside>

          <aside className="bg-slate-950 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold">All Media</h3>
              <span className="text-xs text-slate-500">Library</span>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4 max-h-56 overflow-auto pr-1">
              {mediaLibrary.videos.map((videoName) => (
                <button
                  type="button"
                  key={videoName}
                  onClick={() => {
                    setPrimarySourceType('library');
                    setPrimaryLibraryFile(videoName);
                  }}
                  className={`relative rounded-md border ${primaryLibraryFile === videoName && primarySourceType === 'library' ? 'border-indigo-500' : 'border-slate-700'} overflow-hidden bg-slate-800 hover:border-indigo-400`}
                >
                  <video src={`/generated-videos/${videoName}`} muted preload="metadata" className="w-full h-20 object-cover" />
                  <span className="absolute left-1 right-1 bottom-1 text-[10px] text-white bg-black/50 rounded px-1 truncate">{videoName}</span>
                </button>
              ))}
              {mediaLibrary.videos.length === 0 && (
                <div className="col-span-2 h-20 border border-slate-700 rounded-md text-slate-500 text-xs flex items-center justify-center">
                  No generated videos yet
                </div>
              )}
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-slate-300 mb-1">Primary Source</label>
                <select
                  value={primarySourceType}
                  onChange={(e) => setPrimarySourceType(e.target.value as 'upload' | 'library')}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading}
                >
                  <option value="upload">Upload</option>
                  <option value="library">Oasis Library</option>
                </select>
              </div>

              {primarySourceType === 'upload' ? (
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => onSelectPrimaryFile(e.target.files?.[0] ?? null)}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading}
                />
              ) : (
                <select
                  value={primaryLibraryFile}
                  onChange={(e) => setPrimaryLibraryFile(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading || loadingLibrary}
                >
                  {mediaLibrary.videos.length === 0 && <option value="">No videos found</option>}
                  {mediaLibrary.videos.map((videoName) => (
                    <option key={videoName} value={videoName}>{videoName}</option>
                  ))}
                </select>
              )}

              <label className="flex items-center gap-2 text-slate-300">
                <input type="checkbox" checked={mergeEnabled} onChange={(e) => setMergeEnabled(e.target.checked)} disabled={loading} />
                Merge second video
              </label>

              {mergeEnabled && (
                <>
                  <select
                    value={mergeSourceType}
                    onChange={(e) => setMergeSourceType(e.target.value as 'upload' | 'library')}
                    className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                    disabled={loading}
                  >
                    <option value="upload">Upload Merge Video</option>
                    <option value="library">Oasis Merge Video</option>
                  </select>
                  {mergeSourceType === 'upload' ? (
                    <input
                      type="file"
                      accept="video/*"
                      onChange={(e) => onSelectMergeFile(e.target.files?.[0] ?? null)}
                      className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                      disabled={loading}
                    />
                  ) : (
                    <select
                      value={mergeLibraryFile}
                      onChange={(e) => setMergeLibraryFile(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                      disabled={loading || loadingLibrary}
                    >
                      {mediaLibrary.videos.length === 0 && <option value="">No videos found</option>}
                      {mediaLibrary.videos.map((videoName) => (
                        <option key={videoName} value={videoName}>{videoName}</option>
                      ))}
                    </select>
                  )}
                </>
              )}

              <div>
                <label className="block text-slate-300 mb-1">Audio Track</label>
                <select
                  value={audioSourceType}
                  onChange={(e) => setAudioSourceType(e.target.value as 'none' | 'upload' | 'library')}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading}
                >
                  <option value="none">Keep Original</option>
                  <option value="upload">Upload Audio</option>
                  <option value="library">Use Oasis Audio</option>
                </select>
              </div>

              {audioSourceType === 'upload' && (
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => onSelectAudioFile(e.target.files?.[0] ?? null)}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading}
                />
              )}

              {audioSourceType === 'library' && (
                <select
                  value={audioLibraryFile}
                  onChange={(e) => setAudioLibraryFile(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 text-white border border-slate-700 rounded-md"
                  disabled={loading || loadingLibrary}
                >
                  {mediaLibrary.audios.length === 0 && <option value="">No audio found</option>}
                  {mediaLibrary.audios.map((audioName) => (
                    <option key={audioName} value={audioName}>{audioName}</option>
                  ))}
                </select>
              )}
            </div>
          </aside>

          <section className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold">Media Player</h3>
              <span className="text-xs text-slate-500">9:16</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-black/70 flex items-center justify-center min-h-[360px]">
              {sourcePreviewUrl ? (
                <video
                  src={sourcePreviewUrl}
                  controls
                  className="max-h-[420px] w-auto rounded-md"
                  onLoadedMetadata={(e) => handleMetadataLoaded(e.currentTarget.duration)}
                />
              ) : (
                <div className="text-slate-500 text-sm">Select primary video to preview</div>
              )}
            </div>

            <div className="mt-4 bg-slate-900 border border-slate-800 rounded-lg p-3">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>{`${start.toString().padStart(2, '0')}:${(0).toString().padStart(2, '0')}`}</span>
                <span>{duration > 0 ? `00:${duration.toString().padStart(2, '0')}` : '00:00'}</span>
              </div>

              <div className="space-y-2">
                <div className="h-8 rounded bg-indigo-500/30 border border-indigo-400/40 px-2 flex items-center text-[11px] text-indigo-100">
                  Video Layer · {Math.max(0, end - start)}s {mergeEnabled ? '+ merged clip' : ''}
                </div>
                {audioSourceType !== 'none' && (
                  <div className="h-8 rounded bg-cyan-500/20 border border-cyan-400/40 px-2 flex items-center text-[11px] text-cyan-100">
                    Audio Layer · External Track
                  </div>
                )}
                <div className="h-8 rounded bg-violet-500/20 border border-violet-400/40 px-2 flex items-center text-[11px] text-violet-100">
                  Text/Overlay Layer · Ready
                </div>
              </div>
            </div>
          </section>

          <aside className="bg-slate-950 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-2 text-sm mb-4">
              <button
                type="button"
                onClick={() => setInspectorTab('video')}
                className={`px-3 py-1.5 rounded ${inspectorTab === 'video' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                Video
              </button>
              <button
                type="button"
                onClick={() => setInspectorTab('audio')}
                className={`px-3 py-1.5 rounded ${inspectorTab === 'audio' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                Audio
              </button>
              <button
                type="button"
                onClick={() => setInspectorTab('speed')}
                className={`px-3 py-1.5 rounded ${inspectorTab === 'speed' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                Speed
              </button>
            </div>

            {inspectorTab === 'video' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-2">Trim Start: {start}s</label>
                  <input
                    type="range"
                    min="0"
                    max={Math.max(0, end - 1)}
                    value={start}
                    onChange={(e) => setStart(parseInt(e.target.value, 10))}
                    className="w-full"
                    disabled={loading || duration <= 0}
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-2">Trim End: {end}s</label>
                  <input
                    type="range"
                    min={Math.min(maxEnd, start + 1)}
                    max={maxEnd}
                    value={end}
                    onChange={(e) => setEnd(parseInt(e.target.value, 10))}
                    className="w-full"
                    disabled={loading || duration <= 0}
                  />
                </div>
              </div>
            )}

            {inspectorTab === 'audio' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-2">Volume: {volume.toFixed(2)}</label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={volume}
                    onChange={(e) => setVolume(parseFloat(e.target.value))}
                    className="w-full"
                    disabled={loading || mute}
                  />
                </div>

                <label className="flex items-center gap-2 text-slate-300 text-sm">
                  <input type="checkbox" checked={mute} onChange={(e) => setMute(e.target.checked)} disabled={loading} />
                  Mute output
                </label>
              </div>
            )}

            {inspectorTab === 'speed' && (
              <div>
                <label className="block text-sm text-slate-300 mb-2">Playback Speed: {speed.toFixed(2)}x</label>
                <input
                  type="range"
                  min="0.25"
                  max="4"
                  step="0.25"
                  value={speed}
                  onChange={(e) => setSpeed(parseFloat(e.target.value))}
                  className="w-full"
                  disabled={loading}
                />
              </div>
            )}
          </aside>
        </div>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-900 border border-red-700 rounded-lg">
          <p className="text-red-200">
            <span className="font-semibold">Error:</span> {error}
          </p>
        </div>
      )}

      {editedVideoUrl && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-white mb-4">Edited Video</h3>
          <video src={editedVideoUrl} controls className="w-full rounded-lg border border-slate-600 shadow-lg" />
          <a
            href={editedVideoUrl}
            download
            className="inline-block mt-4 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
          >
            Download Edited Video
          </a>
        </div>
      )}
    </div>
  );
}
