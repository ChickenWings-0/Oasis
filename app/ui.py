from __future__ import annotations

from datetime import datetime
from pathlib import Path

import gradio as gr

from app.config import OUTPUT_DIR
from app.analysis import detect_bpm, detect_key
from app.chords import detect_chords
from app.generate import generate_music_clip as generate_music
from app.humming import (
    extract_melody_events,
    preprocess_humming_wav,
    render_melody_guide_wav,
    save_melody_events_json,
    save_melody_events_midi,
)
from app.music_logic import enrich_metadata_with_analysis
from app.separation import separate_audio
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
        return message, "", "", "", "", "", "", "", "", ""

    input_path = Path(audio_path)
    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        message = "Invalid format. Please upload a WAV or MP3 file."
        gr.Warning(message)
        return message, "", "", "", "", "", "", "", "", ""

    try:
        bpm_result = detect_bpm(path=input_path)
        bpm_value = bpm_result.get("bpm", "")
        key_result = detect_key(path=input_path)
        chords = detect_chords(path=input_path)

        prompt = "default music prompt"
        analysis_data = enrich_metadata_with_analysis(
            str(input_path),
            prompt,
            chords,
            float(bpm_value) if bpm_value else 120.0
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
            f"Mood: {metadata.get('mood')}\n"
            f"Tempo: {metadata.get('tempo')}\n"
            f"Genre: {metadata.get('genre')}"
        )
        chord_groups_text = f"Major: {chord_groups['major']}, Minor: {chord_groups['minor']}"
        bassline_text = ", ".join(bassline)

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
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        import gradio as gr
        gr.Error(f"Audio analysis failed: {str(e)}")
        return str(e), "", "", "", "", "", "", "", "", ""


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


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Oasis Music Module") as demo:
        gr.Markdown("# Oasis Music Module")

        with gr.Tab("Text -> Music"):
            prompt_input = gr.Textbox(
                label="Prompt",
                value="Lo-fi chill beat with soft piano and warm bass, relaxing nighttime mood",
                lines=3,
            )
            with gr.Row():
                preset_lofi = gr.Button("Lo-fi")
                preset_cinematic = gr.Button("Cinematic")
                preset_ambient = gr.Button("Ambient")

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

            preset_lofi.click(fn=set_preset_lofi, inputs=None, outputs=prompt_input)
            preset_cinematic.click(fn=set_preset_cinematic, inputs=None, outputs=prompt_input)
            preset_ambient.click(fn=set_preset_ambient, inputs=None, outputs=prompt_input)

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

        with gr.Tab("Humming -> Analysis"):
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

        with gr.Tab("Instrument Separation"):
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

        with gr.Tab("Audio Analysis"):
            analysis_input = gr.File(label="Upload Audio (WAV/MP3)", file_types=[".wav", ".mp3"], type="filepath")
            analysis_btn = gr.Button("Analyze Audio")
            analysis_status_output = gr.Textbox(label="Status", interactive=False)
            analysis_bpm_output = gr.Textbox(label="BPM", interactive=False)
            analysis_key_output = gr.Textbox(label="Key", interactive=False)
            analysis_scale_output = gr.Textbox(label="Scale", interactive=False)
            analysis_chords_output = gr.Textbox(label="Chords", interactive=False)
            guitar_tabs_output = gr.Textbox(label="Guitar Tabs", interactive=False)
            keyboard_notes_output = gr.Textbox(label="Keyboard Notes", interactive=False)
            metadata_output = gr.Textbox(label="Metadata", interactive=False)
            chord_groups_output = gr.Textbox(label="Chord Groups", interactive=False)
            bassline_output = gr.Textbox(label="Bassline", interactive=False)

            (
                analysis_btn.click(
                    fn=lambda: "Analyzing audio...",
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
                    ],
                    show_progress="full",
                )
            )

        with gr.Tab("Tempo Control"):
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

    return demo


def main() -> None:
    app = build_ui()
    app.launch()


if __name__ == "__main__":
    main()
