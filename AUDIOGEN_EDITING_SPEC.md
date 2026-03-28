# AudioGen and Editing: Features and Specifications

## 1. AudioGen

### 1.1 Features
- Text-to-music generation from natural-language prompts.
- Style-aware generation for genres such as lo-fi, pop, trap, ambient, and cinematic.
- Melody-guided generation using extracted humming melody events.
- Chord-aware arrangement with melody, chords, bass, and drums.
- Automatic key and tempo integration during generation.
- Offline-first processing for local workflows.

### 1.2 Specifications
- Inputs:
  - prompt: string
  - duration_seconds: integer
  - genre: string (optional)
  - key: string (optional)
  - scale: string (optional: major/minor)
  - seed: integer (optional)
  - guide_audio_wav: path (optional)
  - melody_events: list of note events (optional)
- Outputs:
  - generated_audio: WAV file
  - arrangement_midi: MIDI file (multi-track when pipeline is used)
  - analysis_metadata: JSON-compatible object (BPM, key, scale, confidence)
- Performance/quality:
  - Target sample rate: 44.1 kHz for rendered output.
  - Supports CPU fallback paths where GPU is unavailable.
  - Includes normalization and anti-silence handling.
  - Deterministic behavior supported through seed control.

## 2. Editing

### 2.1 Features
- Audio trimming by time range.
- Clip splitting and segment extraction.
- Volume gain and loudness normalization.
- Fade-in and fade-out transitions.
- Tempo and timing adjustment workflows.
- Pitch and key shift operations.
- Chord and harmony-aware support tools.
- Guitar tab mapping from chord sequences.
- Harmonic function analysis and progression detection.

### 2.2 Specifications
- Inputs:
  - audio_path: WAV/MP3 path
  - edit_params:
    - start_time_sec, end_time_sec
    - gain_db
    - fade_in_sec, fade_out_sec
    - tempo_ratio
    - semitone_shift
  - harmony_params (optional):
    - chords: list[string]
    - key: string
    - scale: string
- Outputs:
  - edited_audio: WAV file
  - optional_stems: separated stems where available
  - edit_report: JSON-compatible summary of changes
  - harmony_report:
    - functions: list of { chord, function }
    - progression_type: string
  - guitar_tabs:
    - list of { chord, tab, capo_suggestion }
- Reliability rules:
  - Use non-destructive editing (source file remains unchanged).
  - Use safe defaults to reduce click/pop artifacts on cuts.
  - Return structured errors for invalid input or unsupported operations.

## 3. Example Output Shapes

```json
{
  "audiogen": {
    "input": {
      "prompt": "Lo-fi chill beat with warm bass",
      "duration_seconds": 8,
      "genre": "lofi",
      "seed": 42
    },
    "output": {
      "generated_audio": "outputs/musicgen.wav",
      "analysis_metadata": {
        "bpm": 92,
        "key": "C",
        "scale": "major",
        "confidence": 0.84
      }
    }
  },
  "editing": {
    "harmony_report": {
      "functions": [
        {"chord": "C", "function": "tonic"},
        {"chord": "G", "function": "dominant"}
      ],
      "progression_type": "pop progression"
    },
    "guitar_tabs": [
      {"chord": "F", "tab": "133211", "capo_suggestion": 1}
    ]
  }
}
```
