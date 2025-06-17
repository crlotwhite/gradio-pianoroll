import gradio as gr
from common_utils import clear_and_regenerate_waveform, synthesize_and_play
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
    with gr.TabItem("🎵 Synthesizer Demo"):
        gr.Markdown("## 🎹 PianoRoll with Synthesizer Demo")
        gr.Markdown(
            "Edit notes and click '🎶 Synthesize Audio' to generate audio and play it!"
        )

        with gr.Row():
            with gr.Column(scale=3):
                # Synthesizer initial value using research utilities
                notes = [
                    (60, 0.0, 0.5),
                    (62, 0.5, 0.5),
                    (64, 1.0, 0.5),
                    (65, 1.5, 0.5),
                ]
                lyrics = ["도", "레", "미", "파"]
                initial_value_synth = research.from_notes(
                    notes, tempo=120, lyrics=lyrics
                )
                initial_value_synth["curve_data"] = {}
                initial_value_synth["use_backend_audio"] = False
                piano_roll_synth = PianoRoll(
                    height=600,
                    width=1000,
                    value=initial_value_synth,
                    elem_id="piano_roll_synth",  # Unique ID
                    use_backend_audio=False,  # Initially use frontend engine, switch to backend for synthesize
                )

            with gr.Column(scale=1):
                gr.Markdown("### 🎛️ ADSR Settings")
                attack_slider = gr.Slider(
                    minimum=0.001,
                    maximum=1.0,
                    value=0.01,
                    step=0.001,
                    label="Attack (seconds)",
                )
                decay_slider = gr.Slider(
                    minimum=0.001,
                    maximum=1.0,
                    value=0.1,
                    step=0.001,
                    label="Decay (seconds)",
                )
                sustain_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.01,
                    label="Sustain (level)",
                )
                release_slider = gr.Slider(
                    minimum=0.001,
                    maximum=2.0,
                    value=0.3,
                    step=0.001,
                    label="Release (seconds)",
                )

                gr.Markdown("### 🎵 Waveform Settings")
                wave_type_dropdown = gr.Dropdown(
                    choices=[
                        ("Complex Waveform (Complex)", "complex"),
                        ("Harmonic Synthesis (Harmonic)", "harmonic"),
                        ("FM Synthesis (FM)", "fm"),
                        ("Sawtooth Wave (Sawtooth)", "sawtooth"),
                        ("Square Wave (Square)", "square"),
                        ("Triangle Wave (Triangle)", "triangle"),
                        ("Sine Wave (Sine)", "sine"),
                    ],
                    value="complex",
                    label="Waveform Type",
                    info="Each note uses different waveforms cyclically",
                )

        with gr.Row():
            with gr.Column():
                btn_synthesize = gr.Button(
                    "🎶 Synthesize Audio", variant="primary", size="lg"
                )
                status_text = gr.Textbox(label="Status", interactive=False)

        with gr.Row():
            with gr.Column():
                btn_regenerate = gr.Button(
                    "🔄 Regenerate Waveform", variant="secondary", size="lg"
                )

        # Add gradio Audio component for comparison
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔊 Gradio Audio Comparison")
                gradio_audio_output = gr.Audio(
                    label="Backend-generated audio (comparison)",
                    type="filepath",
                    interactive=False,
                )

        with gr.Row():
            with gr.Column():
                output_json_synth = gr.JSON(label="Result Data")

        # Synthesizer tab events
        btn_synthesize.click(
            fn=synthesize_and_play,
            inputs=[
                piano_roll_synth,
                attack_slider,
                decay_slider,
                sustain_slider,
                release_slider,
                wave_type_dropdown,
            ],
            outputs=[piano_roll_synth, status_text, gradio_audio_output],
            show_progress=True,
        )

        # Waveform regeneration button event
        btn_regenerate.click(
            fn=clear_and_regenerate_waveform,
            inputs=[
                piano_roll_synth,
                attack_slider,
                decay_slider,
                sustain_slider,
                release_slider,
                wave_type_dropdown,
            ],
            outputs=[piano_roll_synth, status_text, gradio_audio_output],
            show_progress=True,
        )

        # Event listener settings
        def log_play_event(event_data=None):
            print("🎵 Play event triggered:", event_data)
            return f"Play started: {event_data if event_data else 'Playing'}"

        def log_pause_event(event_data=None):
            print("⏸️ Pause event triggered:", event_data)
            return f"Paused: {event_data if event_data else 'Paused'}"

        def log_stop_event(event_data=None):
            print("⏹️ Stop event triggered:", event_data)
            return f"Stopped: {event_data if event_data else 'Stopped'}"

        piano_roll_synth.play(log_play_event, outputs=status_text)
        piano_roll_synth.pause(log_pause_event, outputs=status_text)
        piano_roll_synth.stop(log_stop_event, outputs=status_text)

        # Add input event processing (G2P processing)
        def handle_synth_input(lyric_data):
            print("🎵 Synthesizer tab - Input event triggered:", lyric_data)
            return f"Lyric input detected: {lyric_data if lyric_data else 'Input detected'}"

        piano_roll_synth.input(handle_synth_input, outputs=status_text)

        # Update JSON output when note changes
        piano_roll_synth.change(
            lambda x: x, inputs=piano_roll_synth, outputs=output_json_synth
        )

if __name__ == "__main__":
    demo.launch()
