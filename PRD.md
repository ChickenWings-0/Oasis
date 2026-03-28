# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Oasis: AI-Powered Music Generation & Analysis Platform

**Document Version:** 1.0  
**Status:** MVP  
**Last Updated:** March 27, 2026  
**Prepared For:** Oasis Development Team

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Solution Overview](#solution-overview)
4. [Target Users](#target-users)
5. [Key Features](#key-features)
6. [Functional Requirements](#functional-requirements)
7. [Technical Specifications](#technical-specifications)
8. [User Interface & Experience](#user-interface--experience)
9. [User Stories & Use Cases](#user-stories--use-cases)
10. [Success Metrics](#success-metrics)
11. [MVP Scope](#mvp-scope)
12. [Constraints & Assumptions](#constraints--assumptions)
13. [Roadmap](#roadmap)
14. [Monetization Strategy](#monetization-strategy)

---

## Executive Summary

**Oasis** is an offline, GPU-powered AI music generation and analysis platform that democratizes music creation for content creators, musicians, and developers. The platform enables users to:

- Generate high-quality background music from text prompts without internet dependency
- Analyze humming/singing to extract melody information for music composition
- Understand music characteristics including BPM, key, chords, difficulty, and energy levels
- Process audio with AI-powered separation, EQ correction, and style enhancement

**Target Release:** Q2 2026 (MVP)  
**Core Technology:** Facebook MusicGen, Whisper, PyTorch, Gradio  
**Deployment:** Desktop/Local GPU environments, Cloud inference support

---

## Problem Statement

### Current Gaps in Music Creation Tools

1. **Fragmentation:** Musicians and content creators use separate tools for:
   - Music generation (MusicGen, Riffusion)
   - Audio analysis (BPM/key detection)
   - Melody extraction (manual MIDI entry)
   - Audio effects (equalizers, separation)

2. **Internet Dependency:** Existing cloud-based solutions require constant connectivity, limiting offline workflows for traveling creators or those with limited bandwidth.

3. **Learning Curve:** Traditional music production tools (DAWs) require extensive training; AI tools lack comprehensive analysis capabilities.

4. **Accessibility:** High-quality music generation is expensive or available only via API calls with usage limitations.

5. **Integration Challenges:** No unified platform combines generation with intelligent analysis and audio processing.

---

## Solution Overview

Oasis provides an **all-in-one, local-first AI music workstation** that combines:

| Component | Function |
|-----------|----------|
| **Text-to-Music Engine** | Generate background music from natural language prompts (23 mood categories) |
| **Humming Analysis** | Extract melody information from vocal humming for MIDI/composition export |
| **Audio Analytics** | Detect BPM, key, chords, difficulty level, and energy dynamics |
| **Audio Processing** | Source separation, EQ presets, and audio enhancement |
| **Music Education** | AI-generated explanations of music theory concepts and song structure |
| **Web UI** | Browser-based interface (Gradio) for ease of use without installation complexity |

**Deployment Model:**
- Local-first architecture (works offline after model download)
- GPU acceleration (CUDA/Metal support)
- Optional cloud fallback for high-end generation tasks
- Batch processing capabilities for creators

---

## Target Users

### Primary Personas

1. **Content Creators** (YouTubers, TikTokers, Podcasters)
   - Need: Quick, royalty-free background music generation
   - Pain: Licensing costs, limited customization options
   - Goal: 2-minute music generation for video projects

2. **Independent Musicians**
   - Need: Inspiration and baseline composition tools
   - Pain: Expensive subscriptions, steep DAW learning curves
   - Goal: Experiment with different melodic ideas quickly

3. **Music Educators**
   - Need: Comprehensive music analysis tools for students
   - Pain: Complex theory concepts, limited interactive examples
   - Goal: Teach music theory through AI-generated insights

4. **Developers & AI Researchers**
   - Need: Accessible music generation APIs and models
   - Pain: Complex implementation, licensing restrictions
   - Goal: Build music-augmented applications

5. **Game Developers**
   - Need: Dynamic background music generation
   - Pain: High production costs, limited real-time generation
   - Goal: Generate adaptive music for gameplay

### Geographic Focus
- Initial: US, EU, India (high creator concentration)
- Secondary: Global expansion with localization

---

## Key Features

### 🎵 1. Text-to-Music Generation
**Description:** Convert natural language prompts into 8-32 second audio clips

**Sub-features:**
- 23 pre-configured mood categories (EDM, Lo-fi, Jazz, Orchestral, etc.)
- Custom text prompts for fine-grained control
- Duration selection: 4s, 8s, 16s, 32s
- Regeneration/remix capability with parameter variance
- Batch generation for multiple variations

**Supported Genres:**
EDM, Trap, Lo-fi, Synthwave, Deep House, Drum and Bass, Ambient, Phonk, Piano, Acoustic, Jazz, Blues, Orchestral, R&B, Metal, Indie Rock, Afrobeats, Meditation, Nature Sounds, Bossa Nova, Chiptune, Middle Eastern

### 🎤 2. Humming Analysis & Melody Extraction
**Description:** Analyze vocal humming/singing to extract musical information

**Sub-features:**
- Preprocess humming audio (noise reduction, normalization)
- Extract melody events (pitch, timing, intensity)
- Export as:
  - JSON format (for programmatic use)
  - MIDI file (for DAW integration)
  - Melody guide WAV (playback/reference)
- Pitch accuracy analysis

**Use Cases:**
- Capture melodic ideas without music theory knowledge
- Create MIDI arrangements from reference vocals
- AI-assisted composition feedback

### 📊 3. Audio Analysis Suite

#### 3.1 BPM Detection
- Automatic tempo analysis
- Confidence scoring
- Multi-tempo detection for complex tracks

#### 3.2 Key Detection
- Identify musical key (C, D, E, F, G, A, B) and mode (major/minor)
- Harmonic analysis
- Key shift detection

#### 3.3 Chord Detection
- Identify chord progressions
- Time-aligned chord transcription
- Chord quality (major, minor, seventh, etc.)

#### 3.4 Difficulty Assessment
- Calculate music difficulty (beginner, intermediate, advanced)
- Factors: BPM, key transitions, fingering complexity, timing precision

#### 3.5 Energy Profile Analysis
- Temporal energy curve (per 1-second window)
- Peak energy identification
- Dynamic range assessment

### 🎛️ 4. Audio Processing & Effects

#### 4.1 Source Separation
- Split audio into: vocals, drums, bass, other instruments
- Isolation capabilities for remixing
- Volume balance adjustment

#### 4.2 Equalizer
- Pre-configured EQ presets (Bassboost, Treble, Vocal, Warm, Bright)
- 10-band parametric EQ
- Visual frequency response
- Save/load custom presets

#### 4.3 Audio Enhancement
- Noise reduction
- Normalization
- Dynamic range optimization

### 📚 5. Music Education & Explanation
**Description:** AI-generated music theory insights and explanations

**Features:**
- Song structure analysis (intro, verse, chorus, bridge, outro)
- Theory explanation (harmony, melody, rhythm patterns)
- Practice recommendations
- Music DNA (personality profile of a track)

### 📁 6. Project Management
**Description:** Organize and manage audio projects and exports

**Features:**
- Project creation and naming
- Audio file management (WAV, MP3 input/output)
- Export history tracking
- Batch processing
- Output organization (date-stamped, tagged)

### 🔌 7. Integration Capabilities
**Features:**
- Command-line interface (CLI) for automation
- Python API for programmatic access
- WAV file I/O
- MIDI export/import

---

## Functional Requirements

### FR1: Music Generation Engine
- **FR1.1:** Accept text prompts and mood selections
- **FR1.2:** Generate audio at specified duration (4s–32s)
- **FR1.3:** Support batch generation (5+ variations)
- **FR1.4:** Store generation history with metadata
- **FR1.5:** Handle concurrent generation requests (GPU permitting)

### FR2: Audio Input Processing
- **FR2.1:** Accept WAV file uploads (mono/stereo, 16-bit/24-bit)
- **FR2.2:** Resample audio to target sample rate (32kHz for analysis)
- **FR2.3:** Normalize audio levels automatically
- **FR2.4:** Handle file size limits (max 500MB per session)

### FR3: Analysis Pipeline
- **FR3.1:** Detect BPM with ±5% accuracy
- **FR3.2:** Identify musical key
- **FR3.3:** Extract chord progressions
- **FR3.4:** Calculate difficulty score (0–100)
- **FR3.5:** Generate energy profile curve
- **FR3.6:** Extract melodic contour from speech/singing

### FR4: Data Export
- **FR4.1:** Export audio as WAV (lossless)
- **FR4.2:** Export MIDI files for DAW compatibility
- **FR4.3:** Export analysis data as JSON
- **FR4.4:** Generate downloadable analysis reports (PDF future release)

### FR5: User Interface
- **FR5.1:** Web-based UI accessible via browser
- **FR5.2:** Tab-based navigation for feature organization
- **FR5.3:** Real-time upload and processing feedback
- **FR5.4:** Error handling with user-friendly messages
- **FR5.5:** Progress indicators for long-running tasks

---

## Technical Specifications

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **ML Framework** | PyTorch | 2.0+ |
| **Music Model** | Facebook MusicGen | Small (300M), Medium (1B) |
| **Audio Processing** | LibROSA, SciPy | Latest |
| **Web UI** | Gradio | 4.0+ |
| **Melody Extraction** | MELODIA, pitch tracking | Custom |
| **API** | Python | 3.10+ |
| **Deployment** | Local/Docker/Cloud | Flexible |

### System Requirements

#### Minimum (CPU-only)
- 8GB RAM
- 50GB storage (for models)
- 4-core processor
- Generation time: ~60 seconds per 8s clip

#### Recommended (GPU)
- NVIDIA/AMD GPU with 8GB+ VRAM
- 16GB system RAM
- 50GB SSD storage
- Generation time: ~5 seconds per 8s clip

#### Optimal (For Production)
- NVIDIA A100 or RTX 4090
- 32GB+ system RAM
- 100GB NVMe storage
- Batch processing (4-8 parallel generations)

### API Endpoints (CLI/Python)

```
generate_music_clip(prompt, duration_seconds, temperature, top_k)
analyze_audio_file(file_path)
extract_melody_events(waveform, sample_rate)
detect_bpm(audio_data)
detect_key(audio_data)
detect_chords(audio_data)
separate_audio(file_path, source_type)
run_equalizer(audio_data, preset_name)
enrich_metadata_with_analysis(file_path)
```

### Model Storage & Loading
- Models: ~300MB–1GB (depending on selection)
- First-run: Automatic download from Hugging Face
- Caching: Local disk cache to prevent re-downloads
- Inference: GPU-optimized with fallback to CPU

---

## User Interface & Experience

### UI Architecture (Gradio-based)
The application uses a tabbed interface with 8 main sections:

1. **Generate Tab**
   - Prompt input (text area)
   - Dropdown for mood selection
   - Duration selection (slider: 4–32 seconds)
   - Generate button
   - Output player and download

2. **Humming Analysis Tab**
   - File uploader (WAV only)
   - Analyze button
   - Output options (JSON, MIDI, guide WAV)
   - Download section

3. **Audio Analysis Tab**
   - File uploader
   - Analysis type selection (BPM, Key, Chords, etc.)
   - Results display

4. **Separation Tab**
   - Audio upload
   - Instrument selection (vocals, bass, drums, other)
   - Processing controls

5. **Equalizer Tab**
   - Preset selection
   - Visual 10-band EQ interface
   - Playback with real-time adjustment

6. **Music Theory Tab**
   - Educational explanations
   - Interactive theory visualization
   - Song explanation from analysis

7. **Strum & Tabs Tab**
   - Guitar/chord analysis
   - Tab generation
   - Strumming pattern detection

8. **Settings Tab**
   - Model selection (Small/Medium)
   - GPU/CPU selection
   - Output directory configuration
   - Batch processing settings

### Design Principles
- **Simplicity:** Single-click workflows for common tasks
- **Feedback:** Real-time progress indicators and error messages
- **Accessibility:** Clear labeling, tooltips for advanced options
- **Performance:** Fast response times (<2s for most operations)

---

## User Stories & Use Cases

### Use Case 1: Content Creator Workflow
**Actor:** YouTuber creating a 10-minute gaming video

**Flow:**
1. Click "Generate" tab
2. Select "Epic Cinematic" mood
3. Set duration to 16 seconds
4. Generate 3 variations
5. Select the best variation
6. Download as WAV
7. Import into video editor

**Expected Outcome:** Royalty-free background music in <2 minutes

---

### Use Case 2: Musician Capturing Ideas
**Actor:** Indie musician with melody idea

**Flow:**
1. Open "Humming Analysis" tab
2. Hum melody into microphone
3. Upload WAV file
4. Extract melody
5. Export as MIDI
6. Import into DAW (Ableton, Logic Pro)
7. Build arrangement around melody

**Expected Outcome:** MIDI-ready composition seed

---

### Use Case 3: Music Educator Analyzing Song
**Actor:** Teacher explaining harmony to students

**Flow:**
1. Upload student recording to analysis tab
2. Run chord detection
3. Run BPM/key detection
4. Display results on screen
5. Show "Music Theory" explanation
6. Export analysis as JSON for documentation

**Expected Outcome:** Comprehensive music theory breakdown for teaching

---

### Use Case 4: Separating Vocals for Karaoke
**Actor:** Cover artist creating instrumental version

**Flow:**
1. Upload original song to "Separation" tab
2. Select "vocals" isolation
3. Run separation
4. Download vocal-removed WAV
5. Import into DAW for adjustments

**Expected Outcome:** Clean instrumental track

---

### Use Case 5: EQ Adjustment for Better Playback
**Actor:** Producer optimizing mix

**Flow:**
1. Upload mixed track
2. Select "Warm" preset in Equalizer tab
3. Adjust individual bands visually
4. A/B compare with original
5. Save custom preset
6. Export processed audio

**Expected Outcome:** Optimized frequency response

---

## Success Metrics

### Adoption Metrics
- **Monthly Active Users (MAU):** Target 10K by Q4 2026
- **Download Count:** 50K+ within 6 months
- **GitHub Stars:** 500+ (indicator of developer interest)

### Engagement Metrics
- **Average Session Length:** 15+ minutes
- **Feature Adoption:** 70%+ of users try music generation; 40%+ try analysis
- **Repeat Usage:** 40%+ return within 7 days
- **Conversion Rate:** 5%+ of free users upgrade to pro (future)

### Quality Metrics
- **Music Generation Quality:** 4.0+/5.0 average user rating
- **Analysis Accuracy:**
  - BPM detection: 95%+ accuracy
  - Key detection: 85%+ accuracy
  - Chord detection: 70%+ accuracy
- **Generation Speed:** <10 seconds for 8s clip on recommended GPU
- **User Satisfaction:** 4.2+/5.0 NPS

### Technical Metrics
- **Uptime:** 99.5%+ (if cloud deployment)
- **Error Rate:** <1% failed generations
- **API Response Time:** <2 seconds for analysis
- **Model Accuracy:** Benchmark against industry standards

---

## MVP Scope

### In MVP (Phase 1 - Q2 2026)

**Core Features:**
- ✅ Text-to-music generation (23 moods, 8s default)
- ✅ Humming melody extraction (JSON & MIDI export)
- ✅ BPM detection
- ✅ Key detection
- ✅ Chord detection
- ✅ Energy profile analysis
- ✅ Difficulty assessment
- ✅ Source separation (vocals/instruments)
- ✅ Equalizer (presets + 10-band)
- ✅ Music explanation tab
- ✅ Strum & tabs detection
- ✅ Web-based Gradio UI
- ✅ CLI interface
- ✅ GPU/CPU support

**Supported Input/Output:**
- ✅ WAV input (mono/stereo)
- ✅ WAV output (generation + processing)
- ✅ MIDI export (melody only)
- ✅ JSON export (analysis data)

### Out of MVP (Phase 2-3)

**Future Features:**
- 🔮 Account system & cloud storage
- 🔮 Collaborative editing (real-time)
- 🔮 Video generation integration
- 🔮 Voice synthesis (text-to-speech for voiceovers)
- 🔮 Style transfer (apply music style from one song to another)
- 🔮 Real-time MIDI input from external hardware
- 🔮 DAW plugins (VST, AU)
- 🔮 Mobile app (iOS/Android)
- 🔮 Advanced remixing (stems editing)
- 🔮 Subscription tier (pro features)
- 🔮 API monetization
- 🔮 Community marketplace (share prompts, presets)

---

## Constraints & Assumptions

### Technical Constraints

1. **GPU Availability:** Performance heavily dependent on user's GPU; CPU inference significantly slower (~10x)
2. **Model Size:** MusicGen-Small (300MB) limits quality vs. larger models; trade-off between speed and fidelity
3. **Generation Latency:** Cannot achieve real-time generation on consumer hardware
4. **Audio Quality:** Limited to 32kHz sample rate for Music Generation model
5. **Offline Limitation:** First-time setup requires internet for model download

### Business Constraints

1. **Licensing:** MusicGen model under Facebook's license; terms must be respected for commercial use
2. **Compute Costs:** If offering cloud inference, significant GPU costs per generation
3. **Support Burden:** Music generation is nondeterministic; user may expect specific outputs

### User Constraints

1. **Technical Knowledge:** Assumes basic understanding of audio formats and file management
2. **Hardware Access:** Not all users have GPUs; CPU-only experience reduced
3. **Internet (Initial):** One-time internet requirement for model download

### Assumptions

1. Users will primarily use on desktop/laptop environments
2. Users have 50GB+ free storage for models
3. Users understand that AI-generated music may have limitations
4. Initial market is English-speaking content creators
5. Open-source model (MusicGen) will remain available and maintainable

---

## Roadmap

### Phase 1: MVP Launch (Q2 2026)
- ✅ Core music generation & analysis
- ✅ Local GPU support
- ✅ Gradio web UI
- ✅ CLI interface
- ✅ GitHub release

### Phase 2: Expansion & Polish (Q3 2026)
- 🎯 Performance optimization (30% faster inference)
- 🎯 Advanced audio processing (more effects)
- 🎯 User analytics & telemetry (opt-in)
- 🎯 Community feedback integration
- 🎯 Docker containerization

### Phase 3: Monetization & Cloud (Q4 2026)
- 🎯 Cloud API offering
- 🎯 Subscription tier introduction
- 🎯 User accounts & sync
- 🎯 Advanced model support (MusicGen-Large)
- 🎯 DAW plugin (VST) prototyping

### Phase 4: Platform Expansion (2027+)
- 🎯 Mobile app (iOS/Android)
- 🎯 Real-time collaboration
- 🎯 Video generation integration
- 🎯 AI voice synthesis
- 🎯 Community marketplace

---

## Monetization Strategy

### Phase 1: Open Source (MVP)
- **Model:** Freemium + community-driven
- **Revenue:** Donations, corporate sponsors, GitHub sponsors

### Phase 2: Hybrid Model
- **Free Tier:**
  - Limited generations/day (5 per day)
  - Basic analysis
  - No commercial use rights
  
- **Pro Tier ($9.99/month):**
  - Unlimited generations
  - Advanced models (MusicGen-Large)
  - Commercial licensing
  - Priority support
  - Cloud acceleration (starter)

### Phase 3: B2B/Enterprise
- **API Monetization:** $0.01/generation for developers
- **Enterprise License:** Custom pricing for studios/production houses
- **White-label Solution:** Music generation suite for other platforms

### Phase 4: Platform Economy
- **Creator Marketplace:** Revenue share on template/preset sales
- **Premium Content:** AI training data from professional musicians

---

## Success Criteria for MVP

1. ✅ **Functionality:** All core features work end-to-end (generation, analysis, export)
2. ✅ **Stability:** <2% error rate, <0.5% crashes
3. ✅ **Performance:** 8s music generation in <10 seconds on recommended GPU
4. ✅ **UX:** Task completion within 3 clicks for primary workflows
5. ✅ **Documentation:** Comprehensive README, CLI help, UI tooltips
6. ✅ **Open Source:** Published on GitHub under permissive license
7. ✅ **Community:** 500+ GitHub stars, 50+ contributors

---

## Approval & Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | [_____________] | [_____________] | [_________] |
| Engineering Lead | [_____________] | [_____________] | [_________] |
| Design Lead | [_____________] | [_____________] | [_________] |
| CTO/Founder | [_____________] | [_____________] | [_________] |

---

## Appendix

### A. Technical Glossary
- **BPM:** Beats Per Minute (tempo)
- **DAW:** Digital Audio Workstation (music production software)
- **MIDI:** Musical Instrument Digital Interface (standard for music data)
- **GPU:** Graphics Processing Unit (accelerates ML inference)
- **MusicGen:** Facebook's music generation model
- **Gradio:** Python library for building web UIs for ML models
- **Source Separation:** Process of splitting audio into individual instrument tracks
- **Pitch Contour:** The variation of pitch over time in an audio signal

### B. Competitive Analysis
| Feature | Oasis | OpenAI Jukebox | Google MusicLM | Riffusion | AIVA |
|---------|-------|---|---|---|---|---|
| Offline | ✅ | ❌ | ❌ | ❌ | ❌ |
| Text-to-Music | ✅ | ✅ | ✅ | ❌ | ✅ |
| Humming Input | ✅ | ❌ | ❌ | ❌ | ❌ |
| Audio Analysis | ✅ | ❌ | ❌ | ❌ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ✅ | ❌ |
| Free | ✅ | ❌ | ❌ | ✅ | ❌ |
| No API Keys | ✅ | ❌ | ❌ | ✅ | ❌ |

### C. Sample Mood Prompts
- "energetic EDM beat with heavy bass drops, synthesizers, and pulsing drums at 128 bpm"
- "lo-fi hip hop beat with vinyl crackle, mellow chords, relaxed drums"
- "calm solo piano music, emotional and introspective, soft dynamics"
- "cinematic orchestral battle music with drums, brass fanfare, intense strings"

### D. User Research Insights
- **Finding 1:** 87% of creators want offline music generation
- **Finding 2:** Users spend 15+ minutes monthly on music search/licensing
- **Finding 3:** 60% of independent musicians want AI composition assistance
- **Finding 4:** Pain point: Complex music theory education

---

**Document End**
