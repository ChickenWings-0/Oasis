from __future__ import annotations

from pathlib import Path

import gradio as gr

from app.config import OUTPUT_DIR
from app.analysis import detect_bpm, detect_key
from app.chords import detect_chords_from_path
from app.difficulty import detect_difficulty
from app.energy import analyze_energy_profile
from app.equalizer import EQ_PRESETS, run_equalizer
from app.explain import explain_song
from app.generate import MOOD_PROMPTS, generate_music_clip as generate_music
from app.music_logic import (
    analyze_audio_character,
    build_music_dna,
    enrich_metadata_with_analysis,
)
from app.separation import separate_audio
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
    except Exception as e:
        message = f"Instrument separation failed: {e}"
        gr.Error(message)
        return message, None, None, None, None, None, None, None, None, None, None, None, None


def run_audio_analysis(audio_path: str):
    if not audio_path:
        message = "Please upload an audio file before analysis."
        gr.Warning(message)
        return message, "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    input_path = Path(audio_path)
    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        message = "Invalid format. Please upload a WAV or MP3 file."
        gr.Warning(message)
        return message, "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

    try:
        bpm_result = detect_bpm(path=input_path)
        bpm_value = bpm_result.get("bpm", "")
        key_result = detect_key(path=input_path)
        chords = detect_chords_from_path(path=input_path)
        strum_result = analyze_strumming(path=input_path)

        resolved_bpm = float(bpm_value) if bpm_value else 120.0
        dna = build_music_dna(str(input_path), resolved_bpm, chords)
        character = dna["character"]
        energy_profile = dna["energy"]

        character_text = "\n".join([
            f"• {k.replace('_',' ').title()}: {v}"
            for k, v in character.items()
        ])

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

        bpm_text = str(round(float(bpm_value), 2)) if bpm_value not in ("", None) else ""
        key_text = str(key_result.get("key", ""))
        scale_text = str(key_result.get("scale", ""))
        chords_text = ", ".join(chords) if chords else "No chords detected"
        clean_tabs = []
        for entry in guitar_tabs:
            if isinstance(entry, dict):
                tab = str(entry.get("tab", "unknown"))
            else:
                tab = str(entry)
            clean_tabs.append(tab if tab != "unknown" else "N/A")
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
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        import gradio as gr
        gr.Error(f"Audio analysis failed: {str(e)}")
        return str(e), "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""


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


def update_eq_from_preset(preset_name):
    return EQ_PRESETS.get(preset_name, EQ_PRESETS["Flat"])


def run_equalizer_ui(audio_path, g1, g2, g3, g4, g5, g6, g7, g8):
    if not audio_path:
        return "Please upload an audio file.", None

    try:
        output = run_equalizer(audio_path, g1, g2, g3, g4, g5, g6, g7, g8)
        if not output:
            return "Equalization failed. Please try a shorter clip.", None
        return "Equalization complete.", output

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

        with gr.Tab("🎛️ Sound Equalizer"):

            eq_input = gr.File(label="Upload Audio (WAV/MP3)", type="filepath")

            eq_preset_dropdown = gr.Dropdown(
                choices=list(EQ_PRESETS.keys()),
                value="Flat",
                label="EQ Preset"
            )

            eq_band_1 = gr.Slider(-12, 12, value=0, label="60 Hz")
            eq_band_2 = gr.Slider(-12, 12, value=0, label="150 Hz")
            eq_band_3 = gr.Slider(-12, 12, value=0, label="400 Hz")
            eq_band_4 = gr.Slider(-12, 12, value=0, label="1 kHz")
            eq_band_5 = gr.Slider(-12, 12, value=0, label="2.4 kHz")
            eq_band_6 = gr.Slider(-12, 12, value=0, label="6 kHz")
            eq_band_7 = gr.Slider(-12, 12, value=0, label="12 kHz")
            eq_band_8 = gr.Slider(-12, 12, value=0, label="16 kHz")

            eq_apply_btn = gr.Button("Apply Equalizer")

            eq_status = gr.Textbox(label="Status", interactive=False)
            eq_output = gr.Audio(label="Equalized Output")

            eq_preset_dropdown.change(
                fn=update_eq_from_preset,
                inputs=[eq_preset_dropdown],
                outputs=[
                    eq_band_1,
                    eq_band_2,
                    eq_band_3,
                    eq_band_4,
                    eq_band_5,
                    eq_band_6,
                    eq_band_7,
                    eq_band_8,
                ],
            )

            eq_apply_btn.click(
                fn=lambda: ("Applying EQ... please wait", None),
                inputs=None,
                outputs=[eq_status, eq_output],
                show_progress="hidden",
            ).then(
                fn=run_equalizer_ui,
                inputs=[
                    eq_input,
                    eq_band_1,
                    eq_band_2,
                    eq_band_3,
                    eq_band_4,
                    eq_band_5,
                    eq_band_6,
                    eq_band_7,
                    eq_band_8,
                ],
                outputs=[eq_status, eq_output],
            )

    return demo


def main() -> None:
    app = build_ui()
    app.launch(share=False)


if __name__ == "__main__":
    main()
