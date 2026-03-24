from __future__ import annotations

from datetime import datetime
from pathlib import Path

import gradio as gr

from app.config import OUTPUT_DIR
from app.analysis import detect_bpm, detect_key
from app.chords import detect_chords
from app.difficulty import detect_difficulty
from app.energy import analyze_energy_profile
from app.explain import explain_song
from app.generate import MOOD_PROMPTS, generate_music_clip as generate_music
from app.humming import (
    extract_melody_events,
    preprocess_humming_wav,
    render_melody_guide_wav,
    save_melody_events_json,
    save_melody_events_midi,
)
from app.music_logic import (
    analyze_audio_character,
    build_music_dna,
    enrich_metadata_with_analysis,
    generate_music_insight,
    suggest_actions,
)
from app.separation import separate_audio
from app.style_transfer import apply_style_transfer
from app.strum import analyze_strumming
from app.tabs import generate_tabs_data


def run_text_to_music(prompt: str, duration: int):
    if not prompt or not str(prompt).strip():
        message = "Please enter a prompt before generating music."
        gr.Warning(message)
        return message, None, None

    try:
        output_path = generate_music(
            prompt=prompt,
            duration_seconds=int(duration),
        )
        resolved = str(output_path.resolve())
        return "Music generation complete.", resolved, resolved
    except Exception as e:
        import traceback
        traceback.print_exc()
        import gradio as gr
        gr.Error(f"Generation failed: {str(e)}")
        return str(e), None, None


def run_humming_analysis(humming_wav_path: str):
    if not humming_wav_path:
        message = "Please upload a WAV file before running analysis."
        gr.Warning(message)
        return message, None, None, None, None, None

    try:
        wav_path = Path(humming_wav_path)
        if wav_path.suffix.lower() != ".wav":
            message = "Invalid audio format. Please upload a .wav file."
            gr.Warning(message)
            return message, None, None, None, None, None

        preprocess_info = preprocess_humming_wav(wav_path=wav_path)
        melody_events = extract_melody_events(
            waveform=preprocess_info["waveform"],
            sample_rate=preprocess_info["target_sample_rate"],
        )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = OUTPUT_DIR / f"melody_events_{stamp}.json"
        midi_path = OUTPUT_DIR / f"melody_events_{stamp}.mid"
        guide_path = OUTPUT_DIR / f"melody_guide_{stamp}.wav"

        save_melody_events_json(melody_events, json_path)
        save_melody_events_midi(melody_events, midi_path)
        render_melody_guide_wav(
            events=melody_events,
            output_path=guide_path,
            sample_rate=preprocess_info["target_sample_rate"],
        )

        summary = (
            "Humming analysis complete.\n"
            f"Input path: {preprocess_info['input_path']}\n"
            f"Input sample rate: {preprocess_info['input_sample_rate']}\n"
            f"Target sample rate: {preprocess_info['target_sample_rate']}\n"
            f"Resampled: {preprocess_info['resampled']}\n"
            f"Channel status: {preprocess_info['channel_status']}\n"
            f"Duration (s): {preprocess_info['duration_seconds']}\n"
            f"Extracted melody events: {len(melody_events)}"
        )

        return (
            "Processing complete.",
            summary,
            str(json_path.resolve()),
            str(midi_path.resolve()),
            str(guide_path.resolve()),
            str(guide_path.resolve()),
        )
    except Exception:
        message = "Humming analysis failed. Please upload a valid WAV clip (5-10 seconds) and try again."
        gr.Error(message)
        return message, None, None, None, None, None


def run_instrument_separation(audio_path: str):
    print("Running separation on:", audio_path)
    if not audio_path:
        message = "Please upload an audio file before extracting instruments."
        gr.Warning(message)
        return message, None, None, None, None, None, None, None, None, None, None, None, None

    input_path = Path(audio_path)
    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        message = "Invalid format. Please upload a WAV or MP3 file."
        gr.Warning(message)
        return message, None, None, None, None, None, None, None, None, None, None, None, None

    try:
        stems = separate_audio(path=input_path)

        drums = stems.get("drums")
        bass = stems.get("bass")
        vocals = stems.get("vocals")
        other = stems.get("other")

        return (
            "Instrument separation complete.",
            drums, drums, drums,
            bass, bass, bass,
            vocals, vocals, vocals,
            other, other, other,
        )
    except Exception:
        message = "Instrument separation failed. Please try another file or check Demucs installation."
        gr.Error(message)
        return message, None, None, None, None, None, None, None, None, None, None, None, None


def run_audio_analysis(audio_path: str):
    if not audio_path:
        message = "Please upload an audio file before analysis."
        gr.Warning(message)
        return message, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    input_path = Path(audio_path)
    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        message = "Invalid format. Please upload a WAV or MP3 file."
        gr.Warning(message)
        return message, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    try:
        bpm_result = detect_bpm(path=input_path)
        bpm_value = bpm_result.get("bpm", "")
        key_result = detect_key(path=input_path)
        chords = detect_chords(path=input_path)
        strum_result = analyze_strumming(path=input_path)

        resolved_bpm = float(bpm_value) if bpm_value else 120.0
        dna = build_music_dna(str(input_path), resolved_bpm, chords)
        character = dna["character"]
        energy_profile = dna["energy"]

        character_text = "\n".join([
            f"• {k.replace('_',' ').title()}: {v}"
            for k, v in character.items()
        ])

        insight_text = generate_music_insight(character)
        suggestions = suggest_actions(character)
        suggestions_text = "\n".join(suggestions) if suggestions else "No changes suggested."

        prompt = "default music prompt"
        analysis_data = enrich_metadata_with_analysis(
            str(input_path),
            prompt,
            chords,
            resolved_bpm
        )
        metadata = analysis_data["metadata"]
        chord_groups = analysis_data["chords"]
        bassline = analysis_data["bassline"]

        tabs_data = generate_tabs_data(chords)

        guitar_tabs = tabs_data["guitar_tabs"]
        keyboard_notes = tabs_data["keyboard_notes"]

        bpm_text = str(round(float(bpm_value), 2)) if bpm_value != "" else ""
        key_text = str(key_result.get("key", ""))
        scale_text = str(key_result.get("scale", ""))
        chords_text = ", ".join(chords) if chords else "No chords detected"
        clean_tabs = [tab if tab != "unknown" else "N/A" for tab in guitar_tabs]
        guitar_tabs_text = " | ".join(clean_tabs)
        keyboard_notes_text = ", ".join(["-".join(notes) for notes in keyboard_notes])
        metadata_text = (
            f"Mood: {metadata.get('mood')}\n\n"
            f"Tempo: {metadata.get('tempo')}\n\n"
            f"Genre: {metadata.get('genre')}"
        )
        chord_groups_text = (
            f"Major: {chord_groups['major']}\n"
            f"Minor: {chord_groups['minor']}"
        )
        bassline_text = ", ".join(bassline)
        strum_count = str(strum_result.get("count", ""))
        strum_pattern = str(strum_result.get("pattern", ""))
        difficulty = detect_difficulty(
            float(bpm_value),
            chords,
            strum_pattern
        )
        explanation = explain_song(
            resolved_bpm,
            key_text,
            scale_text,
            chords,
            strum_pattern,
            character=character,
        )

        energy_text = "\n".join([
            f"{item['start']}-{item['end']}s: {item['label']}"
            for item in energy_profile
        ])
        explanation_text = explanation.replace(". ", ".\n\n").strip()

        return (
            "Audio analysis complete.",
            bpm_text,
            key_text,
            scale_text,
            chords_text,
            guitar_tabs_text,
            keyboard_notes_text,
            metadata_text,
            chord_groups_text,
            bassline_text,
            strum_count,
            strum_pattern,
            difficulty,
            explanation_text,
            energy_text,
            character_text,
            insight_text,
            suggestions_text,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        import gradio as gr
        gr.Error(f"Audio analysis failed: {str(e)}")
        return str(e), "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""


def run_section_tempo(audio_path, table_data):
    if not audio_path:
        return None

    print("RAW TABLE DATA:", table_data)

    from app.control import apply_section_tempo

    sections = []

    for _, row in table_data.iterrows():
        try:
            start = float(row["start"])
            end = float(row["end"])
            bpm = float(row["bpm"])

            if end <= start:
                continue

            sections.append({
                "start": start,
                "end": end,
                "bpm": bpm
            })

        except:
            continue

    print("PARSED SECTIONS:", sections)

    # sort sections by start time
    sections = sorted(sections, key=lambda x: x["start"])

    # check overlaps
    for i in range(len(sections) - 1):
        if sections[i]["end"] > sections[i + 1]["start"]:
            import gradio as gr
            gr.Error("Sections must not overlap.")
            return None

    print("FINAL SORTED SECTIONS:", sections)

    if not sections:
        import gradio as gr
        gr.Error("No valid sections provided.")
        return None

    try:
        output_path = apply_section_tempo(audio_path, sections)
        return output_path
    except Exception as e:
        import gradio as gr
        gr.Error(f"Tempo processing failed: {str(e)}")
        return None


def set_preset_lofi() -> str:
    return "Lo-fi chill beat with soft piano and warm bass"


def set_preset_cinematic() -> str:
    return "Cinematic orchestral music with emotional strings and build-up"


def set_preset_ambient() -> str:
    return "Ambient relaxing soundscape with soft pads and slow evolving textures"


def update_prompt_from_mood(mood, current_text):
    if mood == "Custom":
        return current_text

    return MOOD_PROMPTS.get(mood, current_text)


def run_style_transfer(audio_path, style):
    if not audio_path:
        return "Please upload an audio file.", None

    style_map = {
        "Lo-fi Chill": "lofi_chill",
        "Bass Boost": "bass_boost",
        "EDM / Club": "edm_club",
        "Cinematic": "cinematic",
        "Ambient / Space": "ambient_space",
        "Vocal Focus": "vocal_focus",
        "Acoustic Soft": "acoustic_soft",
        "Vintage Radio": "vintage_radio",
        "Party Mode": "party_mode",
        "Night Drive": "night_drive",
        "Hyperpop": "hyperpop",
        "Headphone Immersion": "headphone_immersion",
        "Background Chill": "background_chill",
        "Studio Clean": "studio_clean",
        "Epic Trailer": "epic_trailer",
        "Dreamy": "dreamy",
        "Underwater": "underwater",
        "Telephone Effect": "telephone",
        "Hall Concert": "hall_concert",
        "Mono Classic": "mono_classic",
    }
    style_key = style_map.get(style, "studio_clean")

    try:
        output = apply_style_transfer(audio_path, style_key)
        return "Transformation complete.", output

    except Exception as e:
        import traceback
        traceback.print_exc()
        import gradio as gr
        gr.Error(str(e))
        return f"Error: {str(e)}", None


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Oasis Music Module") as demo:
        gr.Markdown("# Oasis Music Module")

        with gr.Tab("🎼 AI Music Generator"):
            gr.Markdown("### 🎼 Choose Style or Write Your Own Prompt")

            mood_dropdown = gr.Dropdown(
                choices=["Custom"] + list(MOOD_PROMPTS.keys()),
                value="Custom",
                label="Quick Style Presets"
            )

            prompt_input = gr.Textbox(
                label="Custom Prompt",
                placeholder="Describe the music you want to generate...",
                lines=3,
            )

            gr.Markdown(
                "👉 Select a preset to auto-fill the prompt\n"
                "👉 Or choose 'Custom' to write your own"
            )

            duration_input = gr.Slider(
                minimum=2,
                maximum=10,
                step=1,
                value=8,
                label="Duration (seconds)",
            )
            generate_btn = gr.Button("Generate")
            text_status_output = gr.Textbox(label="Status", interactive=False)
            output_audio = gr.Audio(label="Generated Audio", type="filepath")
            output_wav_file = gr.File(label="Download WAV")

            mood_dropdown.change(
                fn=update_prompt_from_mood,
                inputs=[mood_dropdown, prompt_input],
                outputs=[prompt_input]
            )

            (
                generate_btn.click(
                    fn=lambda: "Generating music...",
                    inputs=None,
                    outputs=[text_status_output],
                    show_progress="hidden",
                ).then(
                    fn=run_text_to_music,
                    inputs=[prompt_input, duration_input],
                    outputs=[text_status_output, output_audio, output_wav_file],
                    show_progress="full",
                )
            )

        with gr.Tab("🎤 Hum Your Idea"):
            gr.Markdown("Tip: Use short humming clips (5–10 seconds) for best results")
            humming_input = gr.File(label="Upload Humming WAV", file_types=[".wav"], type="filepath")
            analyze_btn = gr.Button("Analyze")
            humming_status_output = gr.Textbox(label="Status", interactive=False)
            summary_output = gr.Textbox(label="Analysis Summary", lines=10)
            json_path_output = gr.File(label="Download JSON")
            midi_path_output = gr.File(label="Download MIDI")
            guide_audio_output = gr.Audio(label="Guide Audio", type="filepath")
            guide_wav_download = gr.File(label="Download Guide WAV")

            (
                analyze_btn.click(
                    fn=lambda: "Processing humming...",
                    inputs=None,
                    outputs=[humming_status_output],
                    show_progress="hidden",
                ).then(
                    fn=run_humming_analysis,
                    inputs=[humming_input],
                    outputs=[humming_status_output, summary_output, json_path_output, midi_path_output, guide_audio_output, guide_wav_download],
                    show_progress="full",
                )
            )

        with gr.Tab("🎚️ Split the Song"):
            separation_input = gr.File(label="Upload Audio (WAV/MP3)", file_types=[".wav", ".mp3"], type="filepath")
            separation_btn = gr.Button("Extract Instruments")
            separation_status_output = gr.Textbox(label="Status", interactive=False)

            drums_audio = gr.Audio(label="Drums", type="filepath")
            drums_path = gr.Textbox(label="Drums Path", interactive=False)
            drums_download = gr.File(label="Download Drums")

            bass_audio = gr.Audio(label="Bass", type="filepath")
            bass_path = gr.Textbox(label="Bass Path", interactive=False)
            bass_download = gr.File(label="Download Bass")

            vocals_audio = gr.Audio(label="Vocals", type="filepath")
            vocals_path = gr.Textbox(label="Vocals Path", interactive=False)
            vocals_download = gr.File(label="Download Vocals")

            other_audio = gr.Audio(label="Other", type="filepath")
            other_path = gr.Textbox(label="Other Path", interactive=False)
            other_download = gr.File(label="Download Other")

            (
                separation_btn.click(
                    fn=lambda: "Extracting instruments...",
                    inputs=None,
                    outputs=[separation_status_output],
                    show_progress="hidden",
                ).then(
                    fn=run_instrument_separation,
                    inputs=[separation_input],
                    outputs=[
                        separation_status_output,
                        drums_audio,
                        drums_path,
                        drums_download,
                        bass_audio,
                        bass_path,
                        bass_download,
                        vocals_audio,
                        vocals_path,
                        vocals_download,
                        other_audio,
                        other_path,
                        other_download,
                    ],
                    show_progress="full",
                )
            )

        with gr.Tab("🧠 Understand Your Music"):
            analysis_input = gr.File(label="Upload Audio (WAV/MP3)", file_types=[".wav", ".mp3"], type="filepath")
            analysis_btn = gr.Button("Analyze Audio")
            analysis_status_output = gr.Textbox(label="Status", interactive=False)

            gr.Markdown("### 🎧 Core Analysis")
            analysis_bpm_output = gr.Textbox(label="Tempo (BPM)", interactive=False)
            analysis_key_output = gr.Textbox(label="Key Signature", interactive=False)
            analysis_scale_output = gr.Textbox(label="Scale Type", interactive=False)

            gr.Markdown("### 🎼 Musical Structure")
            analysis_chords_output = gr.Textbox(label="Detected Chords", interactive=False)
            guitar_tabs_output = gr.Textbox(label="Guitar Tabs (Playable)", interactive=False)
            keyboard_notes_output = gr.Textbox(label="Keyboard Notes", interactive=False)

            gr.Markdown("### 🧠 Intelligence")
            metadata_output = gr.Textbox(label="Metadata", interactive=False)
            analysis_difficulty_output = gr.Textbox(label="Difficulty", interactive=False)

            gr.Markdown("### 🎸 Rhythm")
            analysis_strum_count_output = gr.Textbox(label="Strum Count", interactive=False)
            analysis_strum_pattern_output = gr.Textbox(label="Strumming Style", interactive=False)

            gr.Markdown("### 📊 Energy Profile")
            analysis_energy_output = gr.Textbox(
                label="Energy Timeline",
                interactive=False,
                lines=6
            )

            gr.Markdown("### 🎚️ Sound Character")

            analysis_character_output = gr.Textbox(
                label="Audio Character Profile",
                interactive=False,
                lines=8
            )

            gr.Markdown("### 🧠 Music Insight")

            analysis_insight_output = gr.Textbox(
                label="Music Insight",
                interactive=False
            )

            gr.Markdown("### 💡 Suggestions")

            analysis_suggestions_output = gr.Textbox(
                label="Suggested Enhancements",
                interactive=False
            )

            gr.Markdown("### 🎼 Harmonic Analysis")
            chord_groups_output = gr.Textbox(label="Chord Groups", interactive=False)
            bassline_output = gr.Textbox(label="Bassline", interactive=False)

            gr.Markdown("### 💬 Explanation")
            analysis_explanation_output = gr.Textbox(label="Explanation", interactive=False, lines=6)

            (
                analysis_btn.click(
                    fn=lambda: "Analyzing audio... please wait",
                    inputs=None,
                    outputs=[analysis_status_output],
                    show_progress="hidden",
                ).then(
                    fn=run_audio_analysis,
                    inputs=[analysis_input],
                    outputs=[
                        analysis_status_output,
                        analysis_bpm_output,
                        analysis_key_output,
                        analysis_scale_output,
                        analysis_chords_output,
                        guitar_tabs_output,
                        keyboard_notes_output,
                        metadata_output,
                        chord_groups_output,
                        bassline_output,
                        analysis_strum_count_output,
                        analysis_strum_pattern_output,
                        analysis_difficulty_output,
                        analysis_explanation_output,
                        analysis_energy_output,
                        analysis_character_output,
                        analysis_insight_output,
                        analysis_suggestions_output,
                    ],
                    show_progress="full",
                )
            )

        with gr.Tab("🎛️ Control the Groove"):
            audio_input = gr.File(label="Upload Audio", type="filepath")
            sections_table = gr.Dataframe(
                headers=["start", "end", "bpm"],
                datatype=["number", "number", "number"],
                value=[
                    [0, 5, 80],
                    [5, 10, 120]
                ],
                row_count=(2, "dynamic"),
                col_count=(3, "fixed"),
                interactive=True,
                label="Tempo Sections"
            )
            apply_btn = gr.Button("Apply Tempo Changes")
            output_audio = gr.Audio(label="Processed Audio")

            apply_btn.click(
                fn=run_section_tempo,
                inputs=[audio_input, sections_table],
                outputs=[output_audio],
            )

        with gr.Tab("🎨 Transform Your Sound"):

            gr.Markdown(
                "### 🎨 Transform Your Sound\n"
                "Change the vibe of your audio instantly using style presets.\n\n"
                "👉 Upload a track\n"
                "👉 Choose a style\n"
                "👉 Transform it"
            )

            style_input = gr.File(
                label="Upload Audio (WAV/MP3)",
                type="filepath"
            )

            style_dropdown = gr.Dropdown(
                choices=[
                    "Lo-fi Chill",
                    "Bass Boost",
                    "EDM / Club",
                    "Cinematic",
                    "Ambient / Space",
                    "Vocal Focus",
                    "Acoustic Soft",
                    "Vintage Radio",
                    "Party Mode",
                    "Night Drive",
                    "Hyperpop",
                    "Headphone Immersion",
                    "Background Chill",
                    "Studio Clean",
                    "Epic Trailer",
                    "Dreamy",
                    "Underwater",
                    "Telephone Effect",
                    "Hall Concert",
                    "Mono Classic",
                ],
                value="Lo-fi Chill",
                label="Select Style"
            )

            style_btn = gr.Button("🎨 Transform Audio")

            style_status = gr.Textbox(
                label="Status",
                interactive=False
            )

            style_output = gr.Audio(label="Styled Output")

            style_btn.click(
                fn=lambda: ("Transforming audio... please wait", None),
                inputs=None,
                outputs=[style_status, style_output],
                show_progress="hidden",
            ).then(
                fn=run_style_transfer,
                inputs=[style_input, style_dropdown],
                outputs=[style_status, style_output]
            )

    return demo


def main() -> None:
    app = build_ui()
    app.launch()


if __name__ == "__main__":
    main()
