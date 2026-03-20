'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

type PanelSection = 'media' | 'oasis' | 'audio' | 'effects' | 'text' | 'filters' | 'ai';
type ClipType = 'video' | 'audio' | 'text';
type Resolution = '480p' | '720p' | '1080p';
type LibraryCategory = 'cinematic' | 'vlog' | 'reels';
type ExportFormat = 'mp4' | 'webm';
type ExportQuality = '720p' | '1080p' | '4k';

interface TimelineClip {
  id: string;
  name: string;
  type: ClipType;
  start: number;
  duration: number;
  color: string;
  sourceUrl?: string;
}

interface TimelineTrack {
  id: string;
  name: string;
  type: ClipType;
  clips: TimelineClip[];
}

interface LibraryVideo {
  id: string;
  title: string;
  duration: number;
  category: LibraryCategory;
  isFavorite: boolean;
  url: string;
}

interface LibraryAudio {
  id: string;
  title: string;
  duration: number;
  style: string;
  isFavorite: boolean;
}

interface DragPayload {
  dragType: 'timeline-clip' | 'library-video' | 'library-audio' | 'title-template';
  clipId?: string;
  sourceTrackId?: string;
  libraryId?: string;
}

interface ContextMenuState {
  clipId: string;
  trackId: string;
  x: number;
  y: number;
}

const TIMELINE_SECONDS = 120;
const PIXELS_PER_SECOND_BASE = 12;

const effectsList = ['Fade', 'Zoom', 'Glitch', 'Slide', 'Warp', 'Flash'];
const filterList = ['Cinematic', 'Vintage', 'Noir', 'Teal & Orange', 'Soft Glow', 'Cold HDR'];
const titleTemplates = ['Lower Third', 'Bold Intro', 'Neon Subtitle', 'Minimal Caption'];

function randomId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

function cloneTracks(tracks: TimelineTrack[]): TimelineTrack[] {
  return tracks.map((track) => ({
    ...track,
    clips: track.clips.map((clip) => ({ ...clip })),
  }));
}

function makeInitialTracks(): TimelineTrack[] {
  return [
    {
      id: 'video-track-1',
      name: 'Video Track 1',
      type: 'video',
      clips: [
        { id: randomId('clip'), name: 'Intro Scene', type: 'video', start: 0, duration: 18, color: 'bg-indigo-500/70' },
        { id: randomId('clip'), name: 'City B-roll', type: 'video', start: 20, duration: 16, color: 'bg-purple-500/70' },
      ],
    },
    {
      id: 'video-track-2',
      name: 'Video Track 2',
      type: 'video',
      clips: [{ id: randomId('clip'), name: 'Overlay Motion', type: 'video', start: 8, duration: 10, color: 'bg-blue-500/70' }],
    },
    {
      id: 'audio-track-1',
      name: 'Audio Track 1',
      type: 'audio',
      clips: [{ id: randomId('clip'), name: 'Background Pulse', type: 'audio', start: 0, duration: 42, color: 'bg-cyan-500/60' }],
    },
    {
      id: 'text-track-1',
      name: 'Text Layer 1',
      type: 'text',
      clips: [{ id: randomId('clip'), name: 'Intro Title', type: 'text', start: 2, duration: 8, color: 'bg-violet-500/70' }],
    },
  ];
}

function makeDefaultLibraryVideos(): LibraryVideo[] {
  return [
    { id: randomId('libv'), title: 'Cyber Alley', duration: 14, category: 'cinematic', isFavorite: true, url: '/generated-videos/video_1773985493561.mp4' },
    { id: randomId('libv'), title: 'Fog Walk', duration: 10, category: 'cinematic', isFavorite: false, url: '/generated-videos/video_1774008644512.mp4' },
    { id: randomId('libv'), title: 'Vlog Cutaway', duration: 9, category: 'vlog', isFavorite: false, url: '/generated-videos/video_1773983804542.mp4' },
    { id: randomId('libv'), title: 'Reel Transition', duration: 6, category: 'reels', isFavorite: true, url: '/generated-videos/video_1773982935889.mp4' },
  ];
}

function makeDefaultLibraryAudio(): LibraryAudio[] {
  return [
    { id: randomId('liba'), title: 'Night Drive', duration: 48, style: 'cinematic', isFavorite: true },
    { id: randomId('liba'), title: 'Lo-Fi Pulse', duration: 36, style: 'lo-fi', isFavorite: false },
    { id: randomId('liba'), title: 'Intense Build', duration: 42, style: 'intense', isFavorite: false },
  ];
}

export default function OasisStudio() {
  const [projectName, setProjectName] = useState('oasis_project.orc');
  const [activeSection, setActiveSection] = useState<PanelSection>('media');
  const [resolution, setResolution] = useState<Resolution>('1080p');
  const [showGrid, setShowGrid] = useState(true);
  const [showSafeArea, setShowSafeArea] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playhead, setPlayhead] = useState(0);
  const [timelineZoom, setTimelineZoom] = useState(1.2);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [libraryView, setLibraryView] = useState<'recent' | 'favorites' | 'categories'>('recent');
  const [categoryFilter, setCategoryFilter] = useState<LibraryCategory | 'all'>('all');

  const [uploadedMedia, setUploadedMedia] = useState<File[]>([]);
  const [oasisVideos, setOasisVideos] = useState<LibraryVideo[]>(makeDefaultLibraryVideos());
  const [oasisAudio, setOasisAudio] = useState<LibraryAudio[]>(makeDefaultLibraryAudio());

  const [tracks, setTracks] = useState<TimelineTrack[]>(makeInitialTracks());

  const [aiPrompt, setAiPrompt] = useState('Cinematic drone shot over neon city in rain');
  const [aiAudioStyle, setAiAudioStyle] = useState('cinematic');
  const [aiMode, setAiMode] = useState<'video' | 'audio' | 'smart'>('video');
  const [aiProgress, setAiProgress] = useState(0);
  const [aiGenerating, setAiGenerating] = useState(false);

  const [exportOpen, setExportOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState<ExportFormat>('mp4');
  const [exportQuality, setExportQuality] = useState<ExportQuality>('1080p');
  const [exportProgress, setExportProgress] = useState(0);
  const [exporting, setExporting] = useState(false);

  const previewRef = useRef<HTMLVideoElement | null>(null);
  const timelineRef = useRef<HTMLDivElement | null>(null);

  const historyRef = useRef<TimelineTrack[][]>([cloneTracks(makeInitialTracks())]);
  const historyIndexRef = useRef(0);

  const pixelsPerSecond = PIXELS_PER_SECOND_BASE * timelineZoom;
  const timelineWidth = TIMELINE_SECONDS * pixelsPerSecond;

  const selectedClip = useMemo(() => {
    for (const track of tracks) {
      const clip = track.clips.find((item) => item.id === selectedClipId);
      if (clip) {
        return clip;
      }
    }
    return null;
  }, [tracks, selectedClipId]);

  const filteredVideos = useMemo(() => {
    let list = [...oasisVideos];
    if (libraryView === 'favorites') {
      list = list.filter((item) => item.isFavorite);
    }
    if (libraryView === 'categories' && categoryFilter !== 'all') {
      list = list.filter((item) => item.category === categoryFilter);
    }
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      list = list.filter((item) => item.title.toLowerCase().includes(query));
    }
    return list;
  }, [oasisVideos, libraryView, categoryFilter, searchQuery]);

  const filteredAudio = useMemo(() => {
    let list = [...oasisAudio];
    if (libraryView === 'favorites') {
      list = list.filter((item) => item.isFavorite);
    }
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      list = list.filter((item) => item.title.toLowerCase().includes(query) || item.style.toLowerCase().includes(query));
    }
    return list;
  }, [oasisAudio, libraryView, searchQuery]);

  const canUndo = historyIndexRef.current > 0;
  const canRedo = historyIndexRef.current < historyRef.current.length - 1;

  const commitTracks = (nextTracks: TimelineTrack[]) => {
    const snapshot = cloneTracks(nextTracks);
    const trimmed = historyRef.current.slice(0, historyIndexRef.current + 1);
    trimmed.push(snapshot);
    historyRef.current = trimmed;
    historyIndexRef.current = trimmed.length - 1;
    setTracks(snapshot);
  };

  const handleUndo = () => {
    if (historyIndexRef.current <= 0) {
      return;
    }
    historyIndexRef.current -= 1;
    setTracks(cloneTracks(historyRef.current[historyIndexRef.current]));
  };

  const handleRedo = () => {
    if (historyIndexRef.current >= historyRef.current.length - 1) {
      return;
    }
    historyIndexRef.current += 1;
    setTracks(cloneTracks(historyRef.current[historyIndexRef.current]));
  };

  const updateSelectedClip = (changes: Partial<TimelineClip>) => {
    if (!selectedClipId) {
      return;
    }

    const nextTracks = tracks.map((track) => ({
      ...track,
      clips: track.clips.map((clip) => (clip.id === selectedClipId ? { ...clip, ...changes } : clip)),
    }));
    commitTracks(nextTracks);
  };

  const addClipToTrack = (trackType: ClipType, clip: TimelineClip) => {
    const targetTrack = tracks.find((track) => track.type === trackType);
    if (!targetTrack) {
      return;
    }

    const nextTracks = tracks.map((track) => {
      if (track.id !== targetTrack.id) {
        return track;
      }
      return { ...track, clips: [...track.clips, clip] };
    });

    commitTracks(nextTracks);
    setSelectedClipId(clip.id);
  };

  const removeClip = (trackId: string, clipId: string) => {
    const nextTracks = tracks.map((track) => {
      if (track.id !== trackId) {
        return track;
      }
      return { ...track, clips: track.clips.filter((clip) => clip.id !== clipId) };
    });
    commitTracks(nextTracks);
    if (selectedClipId === clipId) {
      setSelectedClipId(null);
    }
  };

  const splitClip = (trackId: string, clipId: string) => {
    const targetTrack = tracks.find((track) => track.id === trackId);
    const targetClip = targetTrack?.clips.find((clip) => clip.id === clipId);
    if (!targetTrack || !targetClip || targetClip.duration <= 2) {
      return;
    }

    const splitPoint = Math.floor(targetClip.duration / 2);
    const leftClip: TimelineClip = { ...targetClip, duration: splitPoint };
    const rightClip: TimelineClip = {
      ...targetClip,
      id: randomId('clip'),
      name: `${targetClip.name} (Part 2)`,
      start: targetClip.start + splitPoint,
      duration: targetClip.duration - splitPoint,
    };

    const nextTracks = tracks.map((track) => {
      if (track.id !== trackId) {
        return track;
      }

      const clips = track.clips.flatMap((clip) => {
        if (clip.id !== clipId) {
          return [clip];
        }
        return [leftClip, rightClip];
      });

      return { ...track, clips };
    });

    commitTracks(nextTracks);
    setSelectedClipId(rightClip.id);
  };

  const trimClipStart = (clipId: string) => {
    const clip = selectedClip;
    if (!clip || clip.id !== clipId || clip.duration <= 1) {
      return;
    }
    updateSelectedClip({ start: clip.start + 1, duration: clip.duration - 1 });
  };

  const trimClipEnd = (clipId: string) => {
    const clip = selectedClip;
    if (!clip || clip.id !== clipId || clip.duration <= 1) {
      return;
    }
    updateSelectedClip({ duration: clip.duration - 1 });
  };

  const handleMediaUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) {
      return;
    }
    setUploadedMedia((prev) => [...files, ...prev]);
  };

  const startAiGeneration = () => {
    if (aiGenerating) {
      return;
    }

    setAiGenerating(true);
    setAiProgress(0);

    const timer = setInterval(() => {
      setAiProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setAiGenerating(false);

          if (aiMode === 'video') {
            setOasisVideos((prevVideos) => [
              {
                id: randomId('libv'),
                title: `AI Clip ${prevVideos.length + 1}`,
                duration: 10,
                category: 'cinematic',
                isFavorite: false,
                url: '/generated-videos/video_1773982629439.mp4',
              },
              ...prevVideos,
            ]);
          }

          if (aiMode === 'audio') {
            setOasisAudio((prevAudio) => [
              {
                id: randomId('liba'),
                title: `${aiAudioStyle} Track ${prevAudio.length + 1}`,
                duration: 36,
                style: aiAudioStyle,
                isFavorite: false,
              },
              ...prevAudio,
            ]);
          }

          return 100;
        }

        return prev + Math.floor(Math.random() * 17 + 6);
      });
    }, 400);
  };

  const runSmartEdit = () => {
    const nextTracks = tracks.map((track) => {
      if (track.type !== 'text') {
        return track;
      }

      const autoSubtitles: TimelineClip = {
        id: randomId('clip'),
        name: 'Auto Subtitles',
        type: 'text',
        start: 4,
        duration: 20,
        color: 'bg-violet-500/70',
      };

      return { ...track, clips: [autoSubtitles, ...track.clips] };
    });

    commitTracks(nextTracks);
  };

  const startExport = () => {
    if (exporting) {
      return;
    }

    setExporting(true);
    setExportProgress(0);

    const timer = setInterval(() => {
      setExportProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setExporting(false);
          return 100;
        }
        return prev + 8;
      });
    }, 350);
  };

  const togglePlayPause = async () => {
    const player = previewRef.current;
    if (!player) {
      setIsPlaying((prev) => !prev);
      return;
    }

    if (player.paused) {
      await player.play();
      setIsPlaying(true);
      return;
    }

    player.pause();
    setIsPlaying(false);
  };

  const handleSeek = (value: number) => {
    setPlayhead(value);
    if (previewRef.current && Number.isFinite(previewRef.current.duration) && previewRef.current.duration > 0) {
      const target = Math.min(previewRef.current.duration, value);
      previewRef.current.currentTime = target;
    }
  };

  const handlePreviewTimeUpdate = () => {
    if (!previewRef.current) {
      return;
    }
    setPlayhead(Math.floor(previewRef.current.currentTime));
  };

  const handleTrackDrop = (event: React.DragEvent<HTMLDivElement>, targetTrackId: string) => {
    event.preventDefault();
    setContextMenu(null);

    const payloadRaw = event.dataTransfer.getData('text/plain');
    if (!payloadRaw) {
      return;
    }

    const payload = JSON.parse(payloadRaw) as DragPayload;
    const targetTrack = tracks.find((track) => track.id === targetTrackId);
    if (!targetTrack) {
      return;
    }

    const rect = event.currentTarget.getBoundingClientRect();
    const relativeX = event.clientX - rect.left;
    const rawStart = Math.max(0, relativeX / pixelsPerSecond);
    const nextStart = snapToGrid ? Math.round(rawStart) : Number(rawStart.toFixed(2));

    if (payload.dragType === 'timeline-clip' && payload.clipId && payload.sourceTrackId) {
      let draggedClip: TimelineClip | null = null;

      const removedTracks = tracks.map((track) => {
        if (track.id !== payload.sourceTrackId) {
          return track;
        }

        const clip = track.clips.find((item) => item.id === payload.clipId);
        if (clip) {
          draggedClip = clip;
        }

        return { ...track, clips: track.clips.filter((item) => item.id !== payload.clipId) };
      });

      if (!draggedClip) {
        return;
      }

      const placedClip: TimelineClip = { ...draggedClip, start: nextStart, type: targetTrack.type };
      const nextTracks = removedTracks.map((track) => {
        if (track.id !== targetTrack.id) {
          return track;
        }

        return { ...track, clips: [...track.clips, placedClip] };
      });

      commitTracks(nextTracks);
      setSelectedClipId(placedClip.id);
      return;
    }

    if (payload.dragType === 'library-video' && payload.libraryId && targetTrack.type === 'video') {
      const libraryItem = oasisVideos.find((video) => video.id === payload.libraryId);
      if (!libraryItem) {
        return;
      }

      const newClip: TimelineClip = {
        id: randomId('clip'),
        name: libraryItem.title,
        type: 'video',
        start: nextStart,
        duration: libraryItem.duration,
        color: 'bg-indigo-500/70',
        sourceUrl: libraryItem.url,
      };

      const nextTracks = tracks.map((track) => {
        if (track.id !== targetTrack.id) {
          return track;
        }
        return { ...track, clips: [...track.clips, newClip] };
      });

      commitTracks(nextTracks);
      setSelectedClipId(newClip.id);
      return;
    }

    if (payload.dragType === 'library-audio' && payload.libraryId && targetTrack.type === 'audio') {
      const libraryItem = oasisAudio.find((audio) => audio.id === payload.libraryId);
      if (!libraryItem) {
        return;
      }

      const newClip: TimelineClip = {
        id: randomId('clip'),
        name: libraryItem.title,
        type: 'audio',
        start: nextStart,
        duration: libraryItem.duration,
        color: 'bg-cyan-500/60',
      };

      const nextTracks = tracks.map((track) => {
        if (track.id !== targetTrack.id) {
          return track;
        }
        return { ...track, clips: [...track.clips, newClip] };
      });

      commitTracks(nextTracks);
      setSelectedClipId(newClip.id);
      return;
    }

    if (payload.dragType === 'title-template' && payload.libraryId && targetTrack.type === 'text') {
      const newClip: TimelineClip = {
        id: randomId('clip'),
        name: payload.libraryId,
        type: 'text',
        start: nextStart,
        duration: 6,
        color: 'bg-violet-500/70',
      };

      const nextTracks = tracks.map((track) => {
        if (track.id !== targetTrack.id) {
          return track;
        }
        return { ...track, clips: [...track.clips, newClip] };
      });

      commitTracks(nextTracks);
      setSelectedClipId(newClip.id);
    }
  };

  const setDragPayload = (event: React.DragEvent, payload: DragPayload) => {
    event.dataTransfer.setData('text/plain', JSON.stringify(payload));
  };

  useEffect(() => {
    const onWindowClick = () => setContextMenu(null);
    window.addEventListener('click', onWindowClick);
    return () => window.removeEventListener('click', onWindowClick);
  }, []);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
        event.preventDefault();
        handleUndo();
      }

      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'y') {
        event.preventDefault();
        handleRedo();
      }

      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        localStorage.setItem('oasis-studio-save', JSON.stringify({ projectName, tracks, oasisVideos, oasisAudio }));
      }

      if (event.code === 'Space') {
        const target = event.target as HTMLElement | null;
        if (target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) {
          return;
        }
        event.preventDefault();
        void togglePlayPause();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [projectName, tracks, oasisVideos, oasisAudio]);

  useEffect(() => {
    const saved = localStorage.getItem('oasis-studio-save');
    if (!saved) {
      return;
    }

    try {
      const parsed = JSON.parse(saved) as {
        projectName?: string;
        tracks?: TimelineTrack[];
        oasisVideos?: LibraryVideo[];
        oasisAudio?: LibraryAudio[];
      };

      if (parsed.projectName) {
        setProjectName(parsed.projectName);
      }

      if (parsed.tracks && Array.isArray(parsed.tracks)) {
        setTracks(parsed.tracks);
        historyRef.current = [cloneTracks(parsed.tracks)];
        historyIndexRef.current = 0;
      }

      if (parsed.oasisVideos && Array.isArray(parsed.oasisVideos)) {
        setOasisVideos(parsed.oasisVideos);
      }

      if (parsed.oasisAudio && Array.isArray(parsed.oasisAudio)) {
        setOasisAudio(parsed.oasisAudio);
      }
    } catch {
      localStorage.removeItem('oasis-studio-save');
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem('oasis-studio-save', JSON.stringify({ projectName, tracks, oasisVideos, oasisAudio }));
    }, 700);

    return () => clearTimeout(timer);
  }, [projectName, tracks, oasisVideos, oasisAudio]);

  const previewSource = selectedClip?.sourceUrl || oasisVideos[0]?.url || '/generated-videos/video_1773982629439.mp4';

  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black text-white p-3 md:p-4">
      <div className="mx-auto max-w-[1700px] rounded-2xl border border-slate-800/80 bg-slate-950/80 backdrop-blur-md shadow-[0_0_40px_rgba(88,80,236,0.18)] overflow-hidden">
        <header className="h-16 border-b border-slate-800/80 px-4 md:px-6 flex items-center justify-between bg-slate-950/90">
          <div className="flex items-center gap-4">
            <div className="font-semibold tracking-wide text-lg">
              Oasis <span className="text-indigo-400">Studio</span>
            </div>
            <input
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2 md:gap-3">
            <button
              type="button"
              onClick={handleUndo}
              disabled={!canUndo}
              className="px-3 py-1.5 text-sm rounded-md border border-slate-700 bg-slate-900 disabled:opacity-40"
            >
              Undo
            </button>
            <button
              type="button"
              onClick={handleRedo}
              disabled={!canRedo}
              className="px-3 py-1.5 text-sm rounded-md border border-slate-700 bg-slate-900 disabled:opacity-40"
            >
              Redo
            </button>
            <button
              type="button"
              onClick={() => setActiveSection('ai')}
              className="px-3 py-1.5 text-sm rounded-md bg-gradient-to-r from-blue-500 to-purple-500 shadow-[0_0_14px_rgba(99,102,241,0.6)]"
            >
              AI Generate
            </button>
            <button
              type="button"
              onClick={() => setExportOpen((prev) => !prev)}
              className="px-3 py-1.5 text-sm rounded-md border border-slate-700 bg-slate-900"
            >
              Save / Export
            </button>
            <button type="button" className="h-9 w-9 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" />
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr_320px] min-h-[620px]">
          <aside className="border-r border-slate-800 bg-slate-950/70 p-4 space-y-4">
            <div className="grid grid-cols-2 gap-2 text-sm">
              {[
                { key: 'media', label: '📁 Media' },
                { key: 'oasis', label: '🎥 Oasis Library' },
                { key: 'audio', label: '🎵 Audio Library' },
                { key: 'effects', label: '✂️ Effects' },
                { key: 'text', label: '📝 Text & Titles' },
                { key: 'filters', label: '🎨 Filters' },
                { key: 'ai', label: '🤖 AI Tools' },
              ].map((item) => (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setActiveSection(item.key as PanelSection)}
                  className={`rounded-md border px-2 py-2 text-left ${
                    activeSection === item.key
                      ? 'border-indigo-500 bg-indigo-500/20 text-indigo-200'
                      : 'border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {activeSection === 'media' && (
              <div className="space-y-3">
                <div className="text-sm text-slate-300">Uploads</div>
                <input type="file" multiple onChange={handleMediaUpload} className="w-full text-xs text-slate-300" />
                <div className="space-y-2 max-h-64 overflow-auto pr-1">
                  {uploadedMedia.map((file, index) => (
                    <div key={`${file.name}-${index}`} className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-300">
                      {file.name}
                    </div>
                  ))}
                  {uploadedMedia.length === 0 && <div className="text-xs text-slate-500">No uploads yet</div>}
                </div>
              </div>
            )}

            {activeSection === 'oasis' && (
              <div className="space-y-3">
                <div className="flex gap-2 text-xs">
                  {(['recent', 'favorites', 'categories'] as const).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => setLibraryView(mode)}
                      className={`px-2 py-1 rounded ${libraryView === mode ? 'bg-indigo-500/20 text-indigo-200' : 'bg-slate-900 text-slate-400'}`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
                <input
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="Search clips"
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                />
                {libraryView === 'categories' && (
                  <select
                    value={categoryFilter}
                    onChange={(event) => setCategoryFilter(event.target.value as LibraryCategory | 'all')}
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                  >
                    <option value="all">All categories</option>
                    <option value="cinematic">Cinematic</option>
                    <option value="vlog">Vlog</option>
                    <option value="reels">Reels</option>
                  </select>
                )}
                <div className="grid grid-cols-2 gap-2 max-h-72 overflow-auto pr-1">
                  {filteredVideos.map((item) => (
                    <div key={item.id} className="rounded-md border border-slate-800 bg-slate-900 p-2">
                      <video src={item.url} muted preload="metadata" className="h-16 w-full object-cover rounded" />
                      <div className="mt-1 text-[11px] text-slate-300 truncate">{item.title}</div>
                      <button
                        type="button"
                        draggable
                        onDragStart={(event) => setDragPayload(event, { dragType: 'library-video', libraryId: item.id })}
                        onClick={() =>
                          addClipToTrack('video', {
                            id: randomId('clip'),
                            name: item.title,
                            type: 'video',
                            start: Math.max(0, playhead),
                            duration: item.duration,
                            color: 'bg-indigo-500/70',
                            sourceUrl: item.url,
                          })
                        }
                        className="mt-1 w-full rounded bg-indigo-500/20 text-indigo-200 text-[11px] py-1"
                      >
                        Add to timeline
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'audio' && (
              <div className="space-y-3">
                <input
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  placeholder="Search audio"
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                />
                <div className="space-y-2 max-h-72 overflow-auto pr-1">
                  {filteredAudio.map((item) => (
                    <div key={item.id} className="rounded-md border border-slate-800 bg-slate-900 p-2">
                      <div className="text-sm text-slate-200">{item.title}</div>
                      <div className="text-xs text-slate-500">{item.style} · {item.duration}s</div>
                      <button
                        type="button"
                        draggable
                        onDragStart={(event) => setDragPayload(event, { dragType: 'library-audio', libraryId: item.id })}
                        onClick={() =>
                          addClipToTrack('audio', {
                            id: randomId('clip'),
                            name: item.title,
                            type: 'audio',
                            start: Math.max(0, playhead),
                            duration: item.duration,
                            color: 'bg-cyan-500/60',
                          })
                        }
                        className="mt-2 w-full rounded bg-cyan-500/20 text-cyan-200 text-xs py-1"
                      >
                        Add audio
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeSection === 'effects' && (
              <div className="grid grid-cols-2 gap-2">
                {effectsList.map((item) => (
                  <button key={item} type="button" className="rounded-md border border-slate-800 bg-slate-900 px-2 py-2 text-xs text-slate-300 hover:border-indigo-500">
                    {item}
                  </button>
                ))}
              </div>
            )}

            {activeSection === 'text' && (
              <div className="space-y-2">
                {titleTemplates.map((template) => (
                  <button
                    key={template}
                    type="button"
                    draggable
                    onDragStart={(event) => setDragPayload(event, { dragType: 'title-template', libraryId: template })}
                    onClick={() =>
                      addClipToTrack('text', {
                        id: randomId('clip'),
                        name: template,
                        type: 'text',
                        start: Math.max(0, playhead),
                        duration: 6,
                        color: 'bg-violet-500/70',
                      })
                    }
                    className="w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-left hover:border-violet-500"
                  >
                    {template}
                  </button>
                ))}
              </div>
            )}

            {activeSection === 'filters' && (
              <div className="grid grid-cols-2 gap-2">
                {filterList.map((item) => (
                  <button key={item} type="button" className="rounded-md border border-slate-800 bg-slate-900 px-2 py-2 text-xs text-slate-300 hover:border-purple-500">
                    {item}
                  </button>
                ))}
              </div>
            )}

            {activeSection === 'ai' && (
              <div className="space-y-3">
                <div className="flex gap-2 text-xs">
                  {(['video', 'audio', 'smart'] as const).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      onClick={() => setAiMode(mode)}
                      className={`px-2 py-1 rounded ${aiMode === mode ? 'bg-indigo-500/20 text-indigo-200' : 'bg-slate-900 text-slate-400'}`}
                    >
                      {mode.toUpperCase()}
                    </button>
                  ))}
                </div>

                {aiMode !== 'smart' && (
                  <>
                    <textarea
                      value={aiPrompt}
                      onChange={(event) => setAiPrompt(event.target.value)}
                      className="w-full h-20 rounded-md border border-slate-700 bg-slate-900 p-2 text-sm"
                      placeholder="Describe your generation"
                    />
                    {aiMode === 'audio' && (
                      <select
                        value={aiAudioStyle}
                        onChange={(event) => setAiAudioStyle(event.target.value)}
                        className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                      >
                        <option value="cinematic">Cinematic</option>
                        <option value="lo-fi">Lo-Fi</option>
                        <option value="intense">Intense</option>
                      </select>
                    )}
                    <button
                      type="button"
                      onClick={startAiGeneration}
                      disabled={aiGenerating}
                      className="w-full rounded-md bg-gradient-to-r from-blue-500 to-purple-500 py-2 text-sm font-medium disabled:opacity-60"
                    >
                      {aiGenerating ? 'Generating...' : `Generate ${aiMode}`}
                    </button>
                    {aiGenerating && (
                      <div>
                        <div className="h-2 rounded bg-slate-800 overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500" style={{ width: `${Math.min(aiProgress, 100)}%` }} />
                        </div>
                        <div className="text-xs text-slate-400 mt-1">{Math.min(aiProgress, 100)}% complete</div>
                      </div>
                    )}
                  </>
                )}

                {aiMode === 'smart' && (
                  <div className="space-y-2">
                    <button type="button" onClick={runSmartEdit} className="w-full rounded-md border border-slate-700 bg-slate-900 py-2 text-sm">
                      Auto-cut on beats
                    </button>
                    <button type="button" onClick={runSmartEdit} className="w-full rounded-md border border-slate-700 bg-slate-900 py-2 text-sm">
                      Scene detection
                    </button>
                    <button type="button" onClick={runSmartEdit} className="w-full rounded-md border border-slate-700 bg-slate-900 py-2 text-sm">
                      Auto subtitles
                    </button>
                  </div>
                )}
              </div>
            )}
          </aside>

          <section className="border-r border-slate-800 bg-black/40 p-4 md:p-5">
            <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <div>Preview Canvas</div>
                <div className="flex items-center gap-2">
                  <select
                    value={resolution}
                    onChange={(event) => setResolution(event.target.value as Resolution)}
                    className="bg-slate-900 border border-slate-700 rounded px-2 py-1"
                  >
                    <option value="480p">480p</option>
                    <option value="720p">720p</option>
                    <option value="1080p">1080p</option>
                  </select>
                  <button
                    type="button"
                    onClick={() => previewRef.current?.requestFullscreen()}
                    className="rounded border border-slate-700 px-2 py-1"
                  >
                    Fullscreen
                  </button>
                </div>
              </div>

              <div className="relative aspect-video rounded-lg overflow-hidden bg-black border border-slate-800 flex items-center justify-center">
                <video
                  ref={previewRef}
                  src={previewSource}
                  className="h-full w-full object-contain"
                  controls={false}
                  onTimeUpdate={handlePreviewTimeUpdate}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />
                {showGrid && (
                  <div className="pointer-events-none absolute inset-0 grid grid-cols-3 grid-rows-3">
                    {Array.from({ length: 9 }).map((_, index) => (
                      <div key={index} className="border border-white/10" />
                    ))}
                  </div>
                )}
                {showSafeArea && <div className="pointer-events-none absolute inset-[8%] border border-indigo-400/40 rounded" />}
              </div>

              <div className="mt-3 flex items-center gap-3">
                <button type="button" onClick={() => void togglePlayPause()} className="rounded-md border border-slate-700 px-3 py-1.5 text-sm">
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                <input
                  type="range"
                  min={0}
                  max={TIMELINE_SECONDS}
                  value={playhead}
                  onChange={(event) => handleSeek(Number(event.target.value))}
                  className="flex-1"
                />
                <label className="text-xs text-slate-400 flex items-center gap-1">
                  <input type="checkbox" checked={showGrid} onChange={(event) => setShowGrid(event.target.checked)} /> Grid
                </label>
                <label className="text-xs text-slate-400 flex items-center gap-1">
                  <input type="checkbox" checked={showSafeArea} onChange={(event) => setShowSafeArea(event.target.checked)} /> Safe Area
                </label>
              </div>
            </div>

            <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-3 md:hidden text-sm text-slate-400">
              Timeline is hidden on small screens for performance. Use tablet/desktop width.
            </div>
          </section>

          <aside className="bg-slate-950/70 p-4 space-y-3">
            <div className="text-sm font-semibold text-slate-200">Properties</div>

            {!selectedClip && <div className="text-xs text-slate-500">Select a clip from timeline to edit properties.</div>}

            {selectedClip && (
              <>
                <div className="rounded-md border border-slate-800 bg-slate-900 p-3 space-y-2 text-sm">
                  <div className="text-slate-200 font-medium truncate">{selectedClip.name}</div>
                  <div className="text-slate-500 text-xs">Type: {selectedClip.type}</div>

                  <label className="text-xs text-slate-400 block">Duration</label>
                  <input
                    type="number"
                    min={1}
                    value={selectedClip.duration}
                    onChange={(event) => updateSelectedClip({ duration: Math.max(1, Number(event.target.value) || 1) })}
                    className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
                  />

                  <label className="text-xs text-slate-400 block">Speed</label>
                  <input type="range" min={0.25} max={4} step={0.25} defaultValue={1} className="w-full" />

                  <label className="text-xs text-slate-400 block">Opacity</label>
                  <input type="range" min={0} max={1} step={0.05} defaultValue={1} className="w-full" />

                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="text-[11px] text-slate-500">Position</label>
                      <input type="number" defaultValue={0} className="w-full rounded border border-slate-700 bg-slate-950 px-1 py-1 text-xs" />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-500">Scale</label>
                      <input type="number" defaultValue={100} className="w-full rounded border border-slate-700 bg-slate-950 px-1 py-1 text-xs" />
                    </div>
                    <div>
                      <label className="text-[11px] text-slate-500">Rotation</label>
                      <input type="number" defaultValue={0} className="w-full rounded border border-slate-700 bg-slate-950 px-1 py-1 text-xs" />
                    </div>
                  </div>
                </div>

                <div className="rounded-md border border-slate-800 bg-slate-900 p-3 space-y-2 text-sm">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Audio</div>
                  <label className="text-xs text-slate-400 block">Volume</label>
                  <input type="range" min={0} max={1.5} step={0.05} defaultValue={1} className="w-full" />
                  <label className="text-xs text-slate-400 block">Fade In</label>
                  <input type="range" min={0} max={8} step={0.5} defaultValue={0} className="w-full" />
                  <label className="text-xs text-slate-400 block">Fade Out</label>
                  <input type="range" min={0} max={8} step={0.5} defaultValue={0} className="w-full" />
                </div>

                <div className="rounded-md border border-slate-800 bg-slate-900 p-3 space-y-2 text-sm">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Text</div>
                  <select className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs">
                    <option>Inter</option>
                    <option>SF Pro</option>
                    <option>Montserrat</option>
                  </select>
                  <input type="number" defaultValue={42} className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs" />
                  <input type="color" defaultValue="#8b5cf6" className="w-full h-8 rounded border border-slate-700 bg-slate-950" />
                  <select className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs">
                    <option>Fade In</option>
                    <option>Slide Up</option>
                    <option>Typewriter</option>
                  </select>
                </div>
              </>
            )}

            <div className="rounded-md border border-slate-800 bg-slate-900 p-3 text-xs text-slate-400">
              Shortcuts: Space (Play/Pause), Ctrl+Z (Undo), Ctrl+S (Save)
            </div>
          </aside>
        </div>

        <section className="hidden md:block border-t border-slate-800 bg-slate-950/80 p-4">
          <div className="flex items-center justify-between mb-3 text-xs text-slate-400">
            <div className="flex items-center gap-3">
              <span>Timeline</span>
              <label className="flex items-center gap-1">
                <input type="checkbox" checked={snapToGrid} onChange={(event) => setSnapToGrid(event.target.checked)} /> Snap
              </label>
            </div>
            <div className="flex items-center gap-3">
              <span>Zoom</span>
              <input
                type="range"
                min={0.8}
                max={3}
                step={0.1}
                value={timelineZoom}
                onChange={(event) => setTimelineZoom(Number(event.target.value))}
              />
            </div>
          </div>

          <div ref={timelineRef} className="overflow-auto rounded-lg border border-slate-800 bg-black/40">
            <div style={{ width: timelineWidth + 120 }} className="relative">
              <div className="sticky top-0 z-10 bg-slate-950/95 border-b border-slate-800">
                <div className="ml-24 h-8 relative">
                  {Array.from({ length: Math.floor(TIMELINE_SECONDS / 5) + 1 }).map((_, index) => {
                    const second = index * 5;
                    const left = second * pixelsPerSecond;
                    return (
                      <div key={second} className="absolute top-0 bottom-0" style={{ left }}>
                        <div className="h-2 w-px bg-slate-600" />
                        <div className="text-[10px] text-slate-500 mt-1">{`00:${second.toString().padStart(2, '0')}`}</div>
                      </div>
                    );
                  })}
                  <div className="absolute top-0 bottom-0 w-px bg-red-500" style={{ left: playhead * pixelsPerSecond }} />
                </div>
              </div>

              {tracks.map((track) => (
                <div
                  key={track.id}
                  className="flex border-b border-slate-900 last:border-b-0"
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={(event) => handleTrackDrop(event, track.id)}
                >
                  <div className="w-24 shrink-0 px-2 py-3 text-xs text-slate-400 border-r border-slate-900">
                    {track.name}
                  </div>

                  <div className="relative h-16" style={{ width: timelineWidth }}>
                    {track.clips.map((clip) => {
                      const left = clip.start * pixelsPerSecond;
                      const width = Math.max(56, clip.duration * pixelsPerSecond);
                      const selected = selectedClipId === clip.id;

                      return (
                        <div
                          key={clip.id}
                          draggable
                          onDragStart={(event) => setDragPayload(event, { dragType: 'timeline-clip', clipId: clip.id, sourceTrackId: track.id })}
                          onClick={() => setSelectedClipId(clip.id)}
                          onContextMenu={(event) => {
                            event.preventDefault();
                            setContextMenu({ clipId: clip.id, trackId: track.id, x: event.clientX, y: event.clientY });
                          }}
                          className={`absolute top-3 h-10 rounded-md border px-2 py-1 cursor-grab active:cursor-grabbing ${clip.color} ${
                            selected ? 'border-white shadow-[0_0_12px_rgba(99,102,241,0.8)]' : 'border-transparent'
                          }`}
                          style={{ left, width }}
                        >
                          <div className="flex items-center justify-between gap-1">
                            <span className="text-[11px] truncate">{clip.name}</span>
                            <div className="flex gap-1">
                              <button
                                type="button"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  trimClipStart(clip.id);
                                }}
                                className="text-[10px] px-1 rounded bg-black/20"
                              >
                                ◀
                              </button>
                              <button
                                type="button"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  trimClipEnd(clip.id);
                                }}
                                className="text-[10px] px-1 rounded bg-black/20"
                              >
                                ▶
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {contextMenu && (
          <div
            className="fixed z-50 min-w-40 rounded-md border border-slate-700 bg-slate-900 shadow-2xl"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            <button
              type="button"
              onClick={() => {
                splitClip(contextMenu.trackId, contextMenu.clipId);
                setContextMenu(null);
              }}
              className="block w-full text-left px-3 py-2 text-sm hover:bg-slate-800"
            >
              Split / Cut
            </button>
            <button
              type="button"
              onClick={() => {
                removeClip(contextMenu.trackId, contextMenu.clipId);
                setContextMenu(null);
              }}
              className="block w-full text-left px-3 py-2 text-sm hover:bg-slate-800 text-red-300"
            >
              Delete Clip
            </button>
          </div>
        )}

        {exportOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-40">
            <div className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-950 p-4 space-y-3">
              <div className="text-lg font-semibold">Export Project</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400">Format</label>
                  <select
                    value={exportFormat}
                    onChange={(event) => setExportFormat(event.target.value as ExportFormat)}
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-2 py-2 text-sm"
                  >
                    <option value="mp4">MP4</option>
                    <option value="webm">WebM</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400">Quality</label>
                  <select
                    value={exportQuality}
                    onChange={(event) => setExportQuality(event.target.value as ExportQuality)}
                    className="w-full rounded-md border border-slate-700 bg-slate-900 px-2 py-2 text-sm"
                  >
                    <option value="720p">720p</option>
                    <option value="1080p">1080p</option>
                    <option value="4k">4K</option>
                  </select>
                </div>
              </div>

              <button
                type="button"
                onClick={startExport}
                disabled={exporting}
                className="w-full rounded-md bg-gradient-to-r from-indigo-500 to-purple-500 py-2 font-medium disabled:opacity-60"
              >
                {exporting ? 'Exporting...' : 'Start Export'}
              </button>

              {(exporting || exportProgress > 0) && (
                <div>
                  <div className="h-2 rounded bg-slate-800 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500" style={{ width: `${Math.min(exportProgress, 100)}%` }} />
                  </div>
                  <div className="mt-1 text-xs text-slate-400 flex justify-between">
                    <span>{Math.min(exportProgress, 100)}%</span>
                    <span>{`${Math.max(1, Math.ceil((100 - exportProgress) / 8))} min remaining`}</span>
                  </div>
                </div>
              )}

              <button
                type="button"
                onClick={() => setExportOpen(false)}
                className="w-full rounded-md border border-slate-700 py-2 text-sm"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
