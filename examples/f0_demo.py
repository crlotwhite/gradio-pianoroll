import gradio as gr
from gradio_pianoroll import PianoRoll

from common_utils import (
    LIBROSA_AVAILABLE,
    analyze_audio_f0,
    generate_f0_demo_audio
)

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
    gr.Markdown("## 🎵 F0 (Fundamental Frequency) Analysis Demo")
    if LIBROSA_AVAILABLE:
        gr.Markdown("Upload an audio file and extract F0 to visualize in PianoRoll!")
    else:
        gr.Markdown("⚠️ **librosa is not installed**: Run `pip install librosa` to install it.")

    with gr.Row():
        with gr.Column(scale=3):
            # F0 initial value (empty piano roll)
            initial_value_f0 = {
                "notes": [],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }
            piano_roll_f0 = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_f0,
                elem_id="piano_roll_f0",  # Unique ID
                use_backend_audio=False  # Use frontend audio engine
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Upload Audio")

            audio_input = gr.Audio(
                label="Audio file to analyze",
                type="filepath",
                interactive=True
            )

            gr.Markdown("### ⚙️ F0 Extraction Settings")
            f0_method_dropdown = gr.Dropdown(
                choices=[
                    ("PYIN (accurate, slow)", "pyin"),
                    ("PipTrack (fast, less accurate)", "piptrack")
                ],
                value="pyin",
                label="F0 Extraction Method"
            )
            gr.Markdown("💡 **PYIN** is more accurate but takes longer to process.")

            btn_analyze_f0 = gr.Button(
                "🔬 Start F0 Analysis",
                variant="primary",
                size="lg",
                interactive=LIBROSA_AVAILABLE
            )

            btn_generate_demo = gr.Button(
                "🎵 Generate Demo Audio",
                variant="secondary"
            )
            gr.Markdown("📄 Generate a test audio with F0 changing over time.")

            if not LIBROSA_AVAILABLE:
                gr.Markdown("⚠️ librosa is required")

    with gr.Row():
        with gr.Column():
            f0_status_text = gr.Textbox(
                label="Analysis Status",
                interactive=False,
                lines=6
            )

    with gr.Row():
        with gr.Column():
            # Reference audio playback
            reference_audio = gr.Audio(
                label="Original Audio (reference)",
                type="filepath",
                interactive=False
            )

    with gr.Row():
        with gr.Column():
            output_json_f0 = gr.JSON(label="F0 Analysis Result")

    # F0 tab event processing

    # F0 analysis button
    btn_analyze_f0.click(
        fn=analyze_audio_f0,
        inputs=[piano_roll_f0, audio_input, f0_method_dropdown],
        outputs=[piano_roll_f0, f0_status_text, reference_audio],
        show_progress=True
    )

    # Demo audio generation button
    def create_and_analyze_demo():
        """Create demo audio and automatically analyze F0."""
        demo_audio_path = generate_f0_demo_audio()
        if demo_audio_path:
            # Initial piano roll data
            initial_piano_roll = {
                "notes": [],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }

            # Perform F0 analysis
            updated_piano_roll, status, _ = analyze_audio_f0(initial_piano_roll, demo_audio_path, "pyin")

            return updated_piano_roll, status, demo_audio_path, demo_audio_path
        else:
            return initial_value_f0, "Failed to generate demo audio.", None, None

    btn_generate_demo.click(
        fn=create_and_analyze_demo,
        outputs=[piano_roll_f0, f0_status_text, audio_input, reference_audio],
        show_progress=True
    )

    # Update JSON output when note changes
    def update_f0_json_output(piano_roll_data):
        return piano_roll_data

    piano_roll_f0.change(
        fn=update_f0_json_output,
        inputs=[piano_roll_f0],
        outputs=[output_json_f0],
        show_progress=False
    )

    # Log play event
    def log_f0_play_event(event_data=None):
        print("📊 F0 Play event triggered:", event_data)
        return f"Play started: {event_data if event_data else 'Playing'}"

    def log_f0_pause_event(event_data=None):
        print("📊 F0 Pause event triggered:", event_data)
        return f"Paused: {event_data if event_data else 'Paused'}"

    def log_f0_stop_event(event_data=None):
        print("📊 F0 Stop event triggered:", event_data)
        return f"Stopped: {event_data if event_data else 'Stopped'}"

    piano_roll_f0.play(log_f0_play_event, outputs=f0_status_text)
    piano_roll_f0.pause(log_f0_pause_event, outputs=f0_status_text)
    piano_roll_f0.stop(log_f0_stop_event, outputs=f0_status_text)

if __name__ == "__main__":
    demo.launch()
