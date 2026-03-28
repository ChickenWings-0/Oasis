# ARCHITECTURE DOCUMENT
## Oasis: AI-Powered Music Generation & Analysis Platform

**Document Version:** 1.0  
**Status:** MVP  
**Last Updated:** March 27, 2026  
**Target Audience:** Developers, DevOps Engineers, Technical Architects

---

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Module Dependencies](#module-dependencies)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Database & Storage Design](#database--storage-design)
9. [API Architecture](#api-architecture)
10. [Security Architecture](#security-architecture)
11. [Performance & Scalability](#performance--scalability)
12. [Error Handling & Logging](#error-handling--logging)
13. [Development Workflow](#development-workflow)

---

## System Overview

### Vision
Oasis is a **local-first, GPU-accelerated music generation and analysis platform** that processes audio without internet dependency after initial setup. The system architecture prioritizes:

- **Offline-first operation** (works without internet after model download)
- **GPU acceleration** for inference speed
- **Modular components** for extensibility
- **Web-based interface** for accessibility
- **CLI support** for automation

### Architecture Principles

| Principle | Implementation |
|-----------|-----------------|
| **Separation of Concerns** | Modular Python packages (generation, analysis, processing) |
| **Single Responsibility** | Each module handles one domain (BPM detection, key detection, etc.) |
| **CLI + Web Dual Interface** | Command-line for automation, web UI for interactive use |
| **Stateless Design** | Each request independent; shared state only for model caching |
| **Fail-Safe Defaults** | CPU fallback if GPU unavailable; graceful error handling |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                             │
├─────────────────────────────────────────────────────────────────┤
│  Web UI (Gradio)      │      CLI (argparse)                     │
│  • Browser-based      │      • Programmatic access             │
│  • Tab navigation     │      • Batch processing                │
│  • Real-time feedback │      • Automation scripts              │
└────────────┬──────────────────────────┬────────────────────────┘
             │                          │
┌────────────▼──────────────────────────▼────────────────────────┐
│                    API LAYER (Python)                          │
├─────────────────────────────────────────────────────────────────┤
│  • generate_music_clip()                                        │
│  • analyze_audio_file()                                         │
│  • extract_melody_events()                                      │
│  • detect_bpm() / detect_key() / detect_chords()              │
│  • separate_audio() / run_equalizer()                          │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│              CORE PROCESSING MODULES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ GENERATION ENGINE                                       │  │
│  │ ├─ generate.py (MusicGen inference)                   │  │
│  │ └─ Model management & caching                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ ANALYSIS SUITE                                          │  │
│  │ ├─ analysis.py (BPM, key detection)                   │  │
│  │ ├─ chords.py (chord progression)                      │  │
│  │ ├─ difficulty.py (complexity assessment)              │  │
│  │ ├─ energy.py (energy profile)                         │  │
│  │ └─ strum.py (guitar/strumming detection)             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ AUDIO PROCESSING                                        │  │
│  │ ├─ separation.py (source separation)                  │  │
│  │ ├─ equalizer.py (EQ effects)                          │  │
│  │ ├─ remix.py (remixing & stem processing)              │  │
│  │ └─ style_transfer.py (style adaptation)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ SPECIALIZED ANALYSIS                                    │  │
│  │ ├─ humming.py (melody extraction)                     │  │
│  │ ├─ tabs.py (guitar tab generation)                    │  │
│  │ ├─ explain.py (music theory education)                │  │
│  │ └─ music_logic.py (high-level music insights)         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│            EXTERNAL LIBRARIES & MODELS                         │
├─────────────────────────────────────────────────────────────────┤
│  • PyTorch (inference engine)                                  │
│  • Transformers (model loading/management)                     │
│  • LibROSA (audio analysis)                                    │
│  • SciPy (signal processing)                                   │
│  • Facebook MusicGen (text-to-music model)                     │
│  • MELODIA (melody extraction algorithm)                      │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│            HARDWARE / COMPUTE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  • GPU (CUDA/Metal acceleration) OR CPU fallback              │
│  • RAM (8GB min, 16GB recommended)                            │
│  • Storage (50GB+ for models)                                 │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ LOCAL FILE SYSTEM   │
    ├─────────────────────┤
    │ • Models cache      │
    │ • Output files      │
    │ • Config/presets    │
    └─────────────────────┘
```

---

## Component Architecture

### 1. **UI Layer** (Entry Points)

#### 1.1 Web UI (`ui.py` - Gradio)
```python
# File: app/ui.py
# Responsibilities:
# - Tab-based interface (8 tabs)
# - User input validation
# - Real-time feedback & progress
# - File upload/download handling

Tabs:
  1. Generate Tab → run_text_to_music()
  2. Humming Analysis → run_humming_analysis()
  3. Audio Analysis → run_analysis_pipeline()
  4. Separation → run_source_separation()
  5. Equalizer → run_equalizer_adjustment()
  6. Music Theory → run_explanation_analysis()
  7. Strum/Tabs → run_tab_generation()
  8. Settings → configure_environment()
```

**Key Functions:**
- `run_text_to_music(prompt, duration)` - Wrapper for music generation
- `run_humming_analysis(wav_path)` - Melody extraction workflow
- `run_analysis_pipeline(audio_file)` - Multi-analysis execution
- Error handling with user-friendly messages

#### 1.2 CLI Interface (`main.py`)
```python
# File: app/main.py
# Responsibilities:
# - Argument parsing
# - CLI workflow orchestration
# - Batch processing support

Modes:
  1. Text-to-Music: --prompt "..." --duration 8
  2. Humming Analysis: --humming-wav "file.wav" --melody-out "output.json"
  3. Audio Analysis: --analyze-audio "input.wav"
```

**Key Functions:**
- `parse_args()` - CLI argument parser
- `main()` - Orchestrates CLI workflow

---

### 2. **API Layer** (Business Logic)

#### 2.1 Generation Module (`generate.py`)
```python
# Responsibilities:
# - Load MusicGen model on first run
# - Generate music from text prompts
# - Manage model caching
# - Handle GPU/CPU selection

Key Functions:
  • load_musicgen_model() → Model cached
  • generate_music_clip(prompt, duration_seconds, temperature, top_k) 
    → WAV file path
  • analyze_audio_file(file_path) 
    → Waveform + metadata
```

**Data Flow:**
```
Text Prompt → Model Setup → Forward Pass → WAV Generation → Output File
```

**Model Details:**
- Model ID: `facebook/musicgen-small`
- Sample Rate: 32,000 Hz
- Device: CUDA (if available) → CPU fallback
- Caching: `~/.cache/huggingface/hub/`

#### 2.2 Analysis Suite

##### 2.2.1 BPM Detection (`analysis.py`)
```python
def detect_bpm(audio_data: np.ndarray, sr: int) → Dict:
    # Uses librosa onset detection
    # Returns: {"bpm": float, "confidence": float, "multiple_tempos": List}
```

##### 2.2.2 Key Detection (`analysis.py`)
```python
def detect_key(audio_data: np.ndarray, sr: int) → Dict:
    # Uses chroma feature analysis
    # Returns: {"key": str, "mode": str, "confidence": float}
    # Keys: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
    # Modes: major, minor
```

##### 2.2.3 Chord Detection (`chords.py`)
```python
def detect_chords(audio_data: np.ndarray, sr: int) → List[Dict]:
    # Time-aligned chord detection
    # Returns: [{"chord": "C major", "start_time": 0.0, "end_time": 2.0}, ...]
```

##### 2.2.4 Difficulty Assessment (`difficulty.py`)
```python
def detect_difficulty(audio_data, sr, bpm, key_changes) → Dict:
    # Factors: BPM, key transitions, rhythmic complexity
    # Returns: {"difficulty": 0-100, "level": "beginner|intermediate|advanced"}
```

##### 2.2.5 Energy Analysis (`energy.py`)
```python
def analyze_energy_profile(audio_data, sr) → Dict:
    # Per-second energy curve
    # Returns: {"energy_curve": [0.0-1.0], "peak_energy": float, "dynamic_range": float}
```

#### 2.3 Audio Processing

##### 2.3.1 Source Separation (`separation.py`)
```python
def separate_audio(file_path: Path, source_type: str) → Path:
    # Uses demucs or spleeter (configurable)
    # source_type: "vocals" | "drums" | "bass" | "other"
    # Returns: Path to isolated audio file
```

##### 2.3.2 Equalizer (`equalizer.py`)
```python
def run_equalizer(audio_data, preset_name: str) → np.ndarray:
    # Preset library: Bassboost, Treble, Vocal, Warm, Bright
    # Returns: Processed audio array
    
EQ_PRESETS = {
    "Bassboost": {60: 6dB, 250: 3dB},
    "Treble": {4000: 4dB, 8000: 5dB},
    "Vocal": {3000: 5dB, 5000: 3dB},
    "Warm": {60: 3dB, 1000: 2dB},
    "Bright": {8000: 4dB, 16000: 3dB}
}
```

#### 2.4 Specialized Analysis

##### 2.4.1 Melody Extraction (`humming.py`)
```python
def extract_melody_events(waveform: np.ndarray, sample_rate: int) → List[Dict]:
    # Uses MELODIA algorithm via librosa
    # Returns: [{"pitch": 440.0, "confidence": 0.95, "time": 0.5}, ...]

def preprocess_humming_wav(wav_path: Path) → Dict:
    # Normalize, resample to target_sr
    # Returns: {"waveform": np.ndarray, "target_sample_rate": int}

def save_melody_events_json(events: List[Dict], output_path: Path) → None:
    # Export melody data for use in DAWs

def save_melody_events_midi(events: List[Dict], output_path: Path) → None:
    # Convert to MIDI format for sequencers
```

##### 2.4.2 Guitar Analysis (`strum.py`)
```python
def analyze_strumming(audio_data, sr) → Dict:
    # Detect strumming patterns, chord voicings
    # Returns: {"strumming_pattern": str, "complexity": int, "tempo": float}

def generate_tabs_data(audio_data, sr) → Dict:
    # Generate ASCII tab notation
    # Returns: {"tabs": str, "fingerings": List}
```

##### 2.4.3 Music Explanation (`explain.py`)
```python
def explain_song(audio_analysis: Dict) → str:
    # AI-generated music theory explanation
    # Inputs: BPM, key, chords, energy profile
    # Returns: Human-readable explanation

def generate_music_insight(analysis_dict: Dict) → str:
    # Summary of musical characteristics
```

#### 2.5 Music Logic (`music_logic.py`)
```python
def build_music_dna(analysis_results: Dict) → Dict:
    # Create personality profile
    # Returns: {"energy_level": str, "complexity": str, "mood": str, ...}

def analyze_audio_character(audio_data, sr) → Dict:
    # Comprehensive audio character assessment
    
def suggest_actions(analysis_dict: Dict) → List[str]:
    # Recommend next processing steps
    
def enrich_metadata_with_analysis(file_path: Path) → Dict:
    # Full pipeline: analyze + insights
```

---

## Data Flow

### Flow 1: Text-to-Music Generation
```
User Input (Text Prompt + Duration)
         ↓
    Gradio UI validates input
         ↓
  api.generate_music_clip(prompt, duration)
         ↓
  Load MusicGen model (cached after 1st run)
         ↓
  Model inference (GPU-accelerated)
         ↓
  Generate audio tensor (32kHz, mono/stereo)
         ↓
  Save WAV to /outputs/musicgen_[TIMESTAMP].wav
         ↓
  Return file path to user
         ↓
   User downloads or hydrates for further processing
```

### Flow 2: Humming Analysis → MIDI Export
```
User uploads WAV file
         ↓
  UI validates format (.wav only)
         ↓
  preprocess_humming_wav() 
    • Load audio
    • Resample to 32kHz
    • Normalize levels
         ↓
  extract_melody_events()
    • Apply MELODIA algorithm
    • Extract pitch contour
    • Confidence scoring
         ↓
  save_melody_events_midi()
    • Convert pitch/time to MIDI notes
    • Save to /outputs/melody_events_[TIMESTAMP].mid
         ↓
  save_melody_events_json()
    • Export raw data for analysis/display
         ↓
  render_melody_guide_wav()
    • Generate audible guide track (sine wave)
    • Save to /outputs/melody_guide_[TIMESTAMP].wav
         ↓
  Return all three files to user
```

### Flow 3: Audio Analysis Pipeline
```
User uploads audio file
         ↓
analyze_audio_file(file_path)
         ↓
┌────────────────────────────────────────┐
│ Parallel Analysis Execution            │
├────────────────────────────────────────┤
│ • detect_bpm()     → tempo info         │
│ • detect_key()     → key/mode           │
│ • detect_chords()  → chord progression  │
│ • analyze_energy() → energy curve       │
│ • detect_difficulty() → complexity     │
│ • detect_chords() → chord progression   │
└────────────────────────────────────────┘
         ↓
  enrich_metadata_with_analysis()
         ↓
  build_music_dna() - Create music personality
         ↓
  suggest_actions() - Recommend next steps
         ↓
  Display results in Analysis tab
         ↓
  Export JSON with all results
```

### Flow 4: Source Separation
```
User uploads audio file + selects source type
         ↓
UI validates format
         ↓
separate_audio(file_path, source_type)
         ↓
Load separation model (demucs/spleeter)
         ↓
Forward inference pass
         ↓
Save isolated source to /outputs/
         ↓
Return processed audio for playback/download
```

---

## Module Dependencies

### Dependency Graph

```
ui.py (Gradio Interface)
  ├── generate.py (Music generation)
  ├── analysis.py (BPM, key detection)
  ├── chords.py (Chord detection)
  ├── difficulty.py (Difficulty assessment)
  ├── energy.py (Energy analysis)
  ├── separation.py (Source separation)
  ├── equalizer.py (EQ effects)
  ├── humming.py (Melody extraction)
  │   └── preprocess_humming_wav()
  │   └── extract_melody_events()
  │   └── save_melody_events_json()
  │   └── save_melody_events_midi()
  │   └── render_melody_guide_wav()
  ├── strum.py (Guitar analysis)
  ├── tabs.py (Tab generation)
  ├── explain.py (Music explanations)
  ├── music_logic.py (High-level insights)
  ├── remix.py (Audio remixing)
  ├── style_transfer.py (Style transfer)
  └── control.py (State management)

main.py (CLI Interface)
  ├── config.py (Configuration)
  ├── generate.py
  ├── analysis.py
  ├── humming.py
  └── [other modules as needed]

External Dependencies:
  ├── torch (PyTorch)
  ├── transformers (Model loading)
  ├── librosa (Audio analysis)
  ├── scipy (Signal processing)
  ├── numpy (Numerical computing)
  ├── gradio (Web UI)
  ├── scipy.io.wavfile (WAV I/O)
  └── demucs/spleeter (optional, for separation)
```

---

## Technology Stack

### Core Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.10+ | Primary development |
| **ML Framework** | PyTorch | 2.0+ | Inference engine |
| **Model Hub** | Hugging Face Transformers | 4.30+ | Model management |
| **Audio I/O** | scipy.io.wavfile | Latest | WAV reading/writing |
| **Audio Analysis** | LibROSA | 0.10.0+ | Feature extraction |
| **Signal Processing** | SciPy | 1.10.0+ | DSP algorithms |
| **Numerical** | NumPy | 1.24.0+ | Array operations |
| **Web UI** | Gradio | 4.0+ | Browser interface |
| **CLI** | argparse | Built-in | Command-line interface |

### Models

| Model | Source | Size | Purpose | License |
|-------|--------|------|---------|---------|
| **MusicGen-Small** | Meta AI | 300MB | Text-to-music | CC-BY-NC 4.0 |
| **MELODIA** | Salamon et al. | N/A | Melody extraction | BSD |

### Optional Dependencies

- **demucs** (Facebook) - Advanced source separation (~500MB)
- **spleeter** (Deezer) - Vocal removal (~500MB)

### Development Stack

| Tool | Purpose |
|------|---------|
| **pytest** | Unit testing |
| **pre-commit** | Code linting & formatting |
| **black** | Code formatter |
| **flake8** | Linter |
| **mypy** | Type checking |
| **docker** | Containerization |

---

## Deployment Architecture

### 1. **Local Deployment (MVP)**

```
User Machine
├── Installation: git clone + pip install -r requirements.txt
├── First Run: Model download from Hugging Face (~5 min)
├── Model Cache: ~/.cache/huggingface/hub/
├── Runtime: Gradio web server on localhost:7860
├── GPU Detection: CUDA/Metal auto-detection
└── Outputs: ./outputs/ directory
```

**Setup Steps:**
```bash
# 1. Clone repository
git clone https://github.com/ChickenWings-0/Oasis.git
cd Oasis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Gradio UI
python -m app.ui

# 5. Access browser
# http://localhost:7860
```

**Or run CLI:**
```bash
python -m app.main --prompt "cinematic ambient" --duration 8
python -m app.main --humming-wav output.wav --melody-out melody.json
```

### 2. **Docker Deployment**

```dockerfile
# Dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

WORKDIR /app

# Install Python
RUN apt-get update && apt-get install -y python3.10 python3-pip

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/

# Expose Gradio port
EXPOSE 7860

# Run Gradio UI
CMD ["python", "-m", "app.ui", "--server_name", "0.0.0.0"]
```

**Build & Run:**
```bash
docker build -t oasis:latest .
docker run --gpus all -p 7860:7860 -v $(pwd)/outputs:/app/outputs oasis:latest
```

### 3. **Cloud Deployment (Future)**

**Option A: AWS Lambda (CPU-only)**
- Ideal for: Simple analysis tasks
- Cold start: ~10 seconds
- Max timeout: 15 minutes

**Option B: AWS SageMaker**
- Ideal for: Production music generation
- GPU instances: p3.2xlarge or better
- Auto-scaling: Based on queue depth

**Option C: Google Cloud Run**
- Ideal for: Serverless API
- GPU support: NVIDIA T4/V100
- Pay-per-use pricing

---

## Database & Storage Design

### Local Storage Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── main.py (CLI entry point)
│   ├── ui.py (Gradio interface)
│   ├── config.py
│   ├── generate.py
│   ├── analysis.py
│   ├── chords.py
│   ├── difficulty.py
│   ├── energy.py
│   ├── equalizer.py
│   ├── explain.py
│   ├── humming.py
│   ├── music_logic.py
│   ├── remix.py
│   ├── separation.py
│   ├── strum.py
│   ├── style_transfer.py
│   ├── tabs.py
│   ├── control.py
│   └── __pycache__/
│
├── outputs/ (Generated files)
│   ├── musicgen_20260327_120530.wav
│   ├── melody_events_20260327_120530.json
│   ├── melody_events_20260327_120530.mid
│   ├── analysis_results_20260327_120530.json
│   └── ...
│
├── models/ (Optional local cache override)
│   ├── musicgen-small/
│   └── melodia/
│
├── presets/ (User custom configurations)
│   ├── eq_presets.json
│   ├── generation_profiles.json
│   └── audio_profiles.json
│
├── requirements.txt
├── README.md
├── PRD.md
├── ARCHITECTURE.md
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── LICENSE
```

### Model Cache Location

**Default Hugging Face Cache:**
```
Linux/Mac: ~/.cache/huggingface/hub/
Windows: C:\Users\<username>\.cache\huggingface\hub\

Structure:
~/.cache/huggingface/hub/
├── models--facebook--musicgen-small/
│   ├── snapshots/
│   │   └── <commit-hash>/
│   │       ├── config.json
│   │       ├── pytorch_model.bin
│   │       └── processor_config.json
│   └── blobs/
```

### Output File Naming Convention

```
<type>_<timestamp>_<hash>.wav

Examples:
- musicgen_20260327_150230_a3f9.wav
- melody_guide_20260327_150230_b7c2.wav
- separation_vocals_20260327_150230_c1e5.wav

JSON Analysis:
- analysis_20260327_150230.json
- melody_events_20260327_150230.json
```

### JSON Data Structures

**Analysis Results:**
```json
{
  "file": "input.wav",
  "timestamp": "2026-03-27T15:02:30Z",
  "bpm": {
    "value": 120,
    "confidence": 0.92,
    "multiple_tempos": [120, 60]
  },
  "key": {
    "note": "C",
    "mode": "major",
    "confidence": 0.87
  },
  "chords": [
    {"chord": "C major", "start_time": 0.0, "end_time": 2.0},
    {"chord": "G major", "start_time": 2.0, "end_time": 4.0}
  ],
  "energy_profile": [0.2, 0.3, 0.5, 0.8, 0.7, ...],
  "difficulty": {
    "score": 45,
    "level": "intermediate"
  },
  "music_dna": {
    "energy_level": "high",
    "complexity": "moderate",
    "mood": "uplifting"
  }
}
```

**Melody Events:**
```json
[
  {
    "time": 0.0,
    "pitch": 440.0,
    "confidence": 0.95,
    "duration": 0.5
  },
  {
    "time": 0.5,
    "pitch": 493.88,
    "confidence": 0.92,
    "duration": 0.5
  }
]
```

### No Database (MVP)

- **Rationale:** Local-first design, stateless processing
- **Sessions:** In-memory during runtime only
- **Persistence:** File system (JSON outputs, WAV files)
- **Future:** SQLite for project management (Phase 2)

---

## API Architecture

### Python API

**Module:** `app/__init__.py`

```python
# Public API

from app.generate import generate_music_clip
from app.analysis import detect_bpm, detect_key
from app.chords import detect_chords
from app.difficulty import detect_difficulty
from app.energy import analyze_energy_profile
from app.humming import extract_melody_events, preprocess_humming_wav
from app.separation import separate_audio
from app.equalizer import run_equalizer
from app.explain import explain_song
from app.music_logic import build_music_dna, suggest_actions

# Programmatic usage example:
from app import generate_music_clip, detect_bpm

# Generate music
output_path = generate_music_clip(
    prompt="lo-fi chill beat",
    duration_seconds=8,
    temperature=0.9,
    top_k=250
)

# Analyze BPM
bpm_info = detect_bpm(audio_data="output.wav")
print(f"Detected BPM: {bpm_info['bpm']} (confidence: {bpm_info['confidence']})")
```

### REST API (Future)

```
POST /api/v1/generate
  Request: { "prompt": "string", "duration": int }
  Response: { "file_url": "string", "status": "success" }

POST /api/v1/analyze
  Request: { "file": "wav_file" }
  Response: { "bpm": {...}, "key": {...}, "chords": [...] }

GET /api/v1/models
  Response: { "available_models": [...] }
```

---

## Security Architecture

### Input Validation

```python
# File upload validation
def validate_audio_file(file_path: Path) -> bool:
    """
    Checks:
    - File extension (.wav, .mp3, .flac)
    - File size (max 500MB)
    - Magic number (WAV header validation)
    - Corrupted header detection
    """
    return valid

# Text prompt validation
def validate_prompt(prompt: str) -> bool:
    """
    Checks:
    - Length (max 512 characters)
    - No malicious code/injection
    - Unicode safety
    """
    return valid
```

### Output Sanitization

- **Filenames:** Sanitized timestamps + hash (prevent directory traversal)
- **JSON Export:** Validated JSON schema
- **WAV Export:** Header validation before writing

### Model Security

- **Model Source:** Official Hugging Face only
- **Model Verification:** SHA256 hash verification
- **Model Integrity:** Check for compromised versions
- **Sandboxing:** Model runs in isolated process (future)

### Environment Security

- **API Keys:** Not required (local-first)
- **Credentials:** None stored locally (by design)
- **Sensitive Data:** No personal data collection

---

## Performance & Scalability

### Performance Targets

| Operation | Target Time | Hardware |
|-----------|-----------|----------|
| Music Generation (8s) | 5-10 sec | GPU (8GB) |
| BPM Detection | 500ms | CPU |
| Key Detection | 800ms | CPU |
| Chord Detection | 2 sec | CPU |
| Melody Extraction | 3 sec | CPU |
| Total Analysis | <10 sec | CPU |
| Source Separation | 20-40 sec | GPU |

### GPU Optimization

```python
# Model parallelism (for multi-GPU)
model = MusicgenForConditionalGeneration.from_pretrained(
    "facebook/musicgen-small",
    device_map="auto",  # Multi-GPU distribution
    torch_dtype=torch.float16  # Reduced precision for speed
)

# Batch inference (generate 4 variations simultaneously)
batch_size = 4
prompts = [prompt] * batch_size
outputs = model.generate(
    descriptions=prompts,
    max_new_tokens=1024,
    do_sample=True,
    top_k=250,
    temperature=0.95
)
```

### Memory Management

**Memory Usage (MusicGen-Small):**
- Model weights: 300MB
- Inference (32s audio): 2-4GB VRAM
- CPU buffer: 1-2GB
- OS overhead: ~2GB

**Total:** ~6-8GB (fits within 8GB consumer GPUs)

### Caching Strategy

```python
# Model caching (first-run download)
transformers.cache_manager.SymmetricWarmer(
    _CACHING_ENABLED=True,
    _CACHE_DIR="~/.cache/huggingface/hub/"
)

# In-memory inference cache (optional future)
@functools.lru_cache(maxsize=10)
def cached_detection(audio_hash):
    return detect_bpm(audio_hash)
```

### Scalability Approach

**Horizontal Scaling (Multiple Machines):**
```
Load Balancer
├── Worker 1 (GPU)
├── Worker 2 (GPU)
├── Worker 3 (CPU-only)
└── Worker 4 (CPU-only)

Queue: Redis/RabbitMQ
Job Management: Celery/Ray
```

---

## Error Handling & Logging

### Error Hierarchy

```python
class OasisException(Exception):
    """Base exception for all Oasis errors"""
    pass

class InputValidationError(OasisException):
    """Invalid user input"""
    pass

class ModelLoadError(OasisException):
    """Failed to load ML model"""
    pass

class InferenceError(OasisException):
    """Model inference failed"""
    pass

class AudioProcessingError(OasisException):
    """Audio processing error"""
    pass

class FileIOError(OasisException):
    """File read/write error"""
    pass
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/oasis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage:
logger.info("Music generation started")
logger.error("Model loading failed", exc_info=True)
```

### Error Recovery

```python
def generate_music_clip_with_fallback(prompt, duration):
    try:
        # Attempt GPU inference
        device = "cuda" if torch.cuda.is_available() else "cpu"
        result = model.to(device).generate(...)
    except RuntimeError as e:
        logger.warning(f"GPU inference failed: {e}, retrying on CPU")
        # Fallback to CPU
        result = model.to("cpu").generate(...)
    except ModelNotFoundError:
        logger.error("Model download failed")
        raise ModelLoadError("Could not load MusicGen model")
    
    return result
```

---

## Development Workflow

### Git Workflow

```
main (stable releases)
  └── develop (integration branch)
      ├── feature/music-generation
      ├── feature/audio-analysis
      ├── bugfix/gpu-crash
      └── docs/architecture
```

### Branching Convention

```
feature/description     - New features
bugfix/issue-id         - Bug fixes
docs/document-name      - Documentation
refactor/component-name - Refactoring
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with commits
3. Push to GitHub
4. Create PR with description
5. Code review + tests pass
6. Merge to `develop`
7. Release cycle: `develop` → `main`

### Testing Strategy

```
Unit Tests
├── test_generate.py (Music generation)
├── test_analysis.py (BPM/key detection)
├── test_humming.py (Melody extraction)
├── test_separation.py (Source separation)
└── test_equalizer.py (EQ processing)

Integration Tests
├── test_full_pipeline.py (End-to-end workflows)
└── test_cli_interface.py (CLI commands)

Performance Tests
├── test_inference_speed.py (Generation latency)
└── test_memory_usage.py (Memory consumption)
```

**Run Tests:**
```bash
pytest tests/ -v
pytest tests/test_generate.py::test_music_generation -v
pytest tests/ --cov=app  # Coverage report
```

### Documentation Standards

```
Module docstrings
├── Function signature
├── Docstring (description, params, returns)
├── Type hints
└── Usage example

Example:
def detect_bpm(audio_data: np.ndarray, sr: int = 22050) → Dict[str, float]:
    """
    Detect BPM using onset detection.
    
    Args:
        audio_data: Audio waveform (1D or 2D array)
        sr: Sample rate (default 22050 Hz)
    
    Returns:
        {"bpm": float, "confidence": float, "multiple_tempos": List[float]}
    
    Example:
        >>> bpm_info = detect_bpm(audio, sr=22050)
        >>> print(f"BPM: {bpm_info['bpm']}")
    """
    ...
```

---

## Deployment Checklist

### Pre-Release
- [ ] All tests passing (100% critical path coverage)
- [ ] Performance benchmarks meet targets
- [ ] Documentation complete and reviewed
- [ ] Security audit completed
- [ ] Model integrity verified
- [ ] Requirements.txt frozen with versions

### Release
- [ ] Tag version (semantic versioning: v1.0.0)
- [ ] Build Docker image
- [ ] Push to Docker Hub
- [ ] Create GitHub release with notes
- [ ] Update README with new features

### Post-Release
- [ ] Monitor error logs
- [ ] Track user feedback
- [ ] Performance monitoring
- [ ] Update roadmap based on usage

---

## Future Architecture Enhancements

### Phase 2 (Q3 2026)
- [ ] SQLite project management
- [ ] User session persistence
- [ ] Real-time collaboration (WebSocket)
- [ ] Advanced caching layer (Redis)
- [ ] Distributed batch processing (Celery + Redis)

### Phase 3 (Q4 2026+)
- [ ] MicroServices architecture (separate generation/analysis services)
- [ ] Event-driven architecture (message queues)
- [ ] GraphQL API (in addition to REST)
- [ ] WebAssembly (WASM) inference (browser-based)
- [ ] gRPC for inter-service communication

---

**Document End**
