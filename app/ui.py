from __future__ import annotations

from datetime import datetime
from pathlib import Path

import gradio as gr

from app.config import OUTPUT_DIR
from app.generate import generate_music_clip as generate_music
from app.humming import (
    extract_melody_events,
    preprocess_humming_wav,
    render_melody_guide_wav,
    save_melody_events_json,
    save_melody_events_midi,
)
from app.separation import separate_audio


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
    except Exception:
        message = "Music generation failed. Please try again with a shorter duration or a different prompt."
        gr.Error(message)
        return message, None, None


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

    return demo


def main() -> None:
    app = build_ui()
    app.launch()


if __name__ == "__main__":
    main()
