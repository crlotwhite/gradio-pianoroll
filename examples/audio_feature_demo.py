import gradio as gr
from gradio_pianoroll import PianoRoll

from common_utils import (
    LIBROSA_AVAILABLE,
    synthesize_and_analyze_features,
    analyze_uploaded_audio_features,
    generate_feature_demo_audio
)

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
    gr.Markdown("## 🎵 Audio Feature Analysis Demo")
    if LIBROSA_AVAILABLE:
        gr.Markdown("Create audio from PianoRoll notes and analyze F0 and loudness, or upload your own audio for analysis!")
    else:
        gr.Markdown("⚠️ **librosa is not installed**: Run `pip install librosa` to install it.")

    with gr.Row():
        with gr.Column(scale=3):
            # Audio feature analysis initial value
            initial_value_features = {
                "notes": [
                    {
                        "start": 0,
                        "duration": 320,
                        "pitch": 60,  # C4
                        "velocity": 100,
                        "lyric": "도"
                    },
                    {
                        "start": 320,
                        "duration": 320,
                        "pitch": 64,  # E4
                        "velocity": 90,
                        "lyric": "미"
                    },
                    {
                        "start": 640,
                        "duration": 320,
                        "pitch": 67,  # G4
                        "velocity": 95,
                        "lyric": "솔"
                    }
                ],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }
            piano_roll_features = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_features,
                elem_id="piano_roll_features",  # Unique ID
                use_backend_audio=True  # Use backend audio engine
            )
    with gr.Row():
        with gr.Column():
            btn_analyze_generated = gr.Button(
                "🎶 Create Audio from Notes & Analyze",
                variant="primary",
                size="lg",
                interactive=LIBROSA_AVAILABLE
            )

    with gr.Row():
        with gr.Column():
            btn_analyze_uploaded = gr.Button(
                "📤 Analyze Uploaded Audio",
                variant="secondary",
                size="lg",
                interactive=LIBROSA_AVAILABLE
            )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ Synthesizer Settings")

            # ADSR settings
            attack_features = gr.Slider(
                minimum=0.001,
                maximum=1.0,
                value=0.01,
                step=0.001,
                label="Attack (seconds)"
            )
            decay_features = gr.Slider(
                minimum=0.001,
                maximum=1.0,
                value=0.1,
                step=0.001,
                label="Decay (seconds)"
            )
            sustain_features = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.01,
                label="Sustain (level)"
            )
            release_features = gr.Slider(
                minimum=0.001,
                maximum=2.0,
                value=0.3,
                step=0.001,
                label="Release (seconds)"
            )

            # Waveform settings
            wave_type_features = gr.Dropdown(
                choices=[
                    ("Complex", "complex"),
                    ("Harmonic", "harmonic"),
                    ("FM", "fm"),
                    ("Sawtooth", "sawtooth"),
                    ("Square", "square"),
                    ("Triangle", "triangle"),
                    ("Sine", "sine")
                ],
                value="complex",
                label="Waveform Type"
            )
        with gr.Column():
            gr.Markdown("### 📊 Analysis Settings")

            # Select features to analyze
            include_f0_features = gr.Checkbox(
                label="F0 (fundamental frequency) analysis",
                value=True
            )
            include_loudness_features = gr.Checkbox(
                label="Loudness (loudness) analysis",
                value=True
            )
            include_voicing_features = gr.Checkbox(
                label="Voice/Unvoice (voiced/unvoiced) analysis",
                value=True
            )

            # F0 analysis method
            f0_method_features = gr.Dropdown(
                choices=[
                    ("PYIN (accurate, slow)", "pyin"),
                    ("PipTrack (fast, less accurate)", "piptrack")
                ],
                value="pyin",
                label="F0 Extraction Method"
            )

            # Loudness settings
            loudness_use_db_features = gr.Checkbox(
                label="Display Loudness in dB",
                value=True
            )
            with gr.Row():
                loudness_y_min_features = gr.Number(
                    label="Loudness minimum value (auto if empty)",
                    value=None
                )
                loudness_y_max_features = gr.Number(
                    label="Loudness maximum value (auto if empty)",
                    value=None
                )

            # Voice/Unvoice settings
            voicing_use_probs_features = gr.Checkbox(
                label="Display Voice/Unvoice as probabilities",
                value=True,
                info="Unchecked: Display as binary (0/1)"
            )
        with gr.Column():
            gr.Markdown("### 🎤 Upload Audio")
            audio_upload_features = gr.Audio(
                label="Audio file to analyze",
                type="filepath",
                interactive=True
            )

            btn_generate_feature_demo = gr.Button(
                "🎵 Generate Demo Audio for Feature Analysis",
                variant="secondary"
            )
            gr.Markdown("📄 Generate a test audio with F0 and loudness changing over time.")

    with gr.Row():
        with gr.Column():
            features_status_text = gr.Textbox(
                label="Analysis Status",
                interactive=False,
                lines=4
            )

    with gr.Row():
        with gr.Column():
            # Reference audio playback
            reference_audio_features = gr.Audio(
                label="Analyzed Audio (reference)",
                type="filepath",
                interactive=False
            )

    with gr.Row():
        with gr.Column():
            output_json_features = gr.JSON(label="Audio Feature Analysis Result")

    # Audio feature analysis tab event processing

    # Analyze generated audio button
    btn_analyze_generated.click(
        fn=synthesize_and_analyze_features,
        inputs=[
            piano_roll_features,
            attack_features,
            decay_features,
            sustain_features,
            release_features,
            wave_type_features,
            include_f0_features,
            include_loudness_features,
            include_voicing_features,
            f0_method_features,
            loudness_y_min_features,
            loudness_y_max_features,
            loudness_use_db_features,
            voicing_use_probs_features
        ],
        outputs=[piano_roll_features, features_status_text, reference_audio_features],
        show_progress=True
    )

    # Analyze uploaded audio button
    btn_analyze_uploaded.click(
        fn=analyze_uploaded_audio_features,
        inputs=[
            piano_roll_features,
            audio_upload_features,
            include_f0_features,
            include_loudness_features,
            include_voicing_features,
            f0_method_features,
            loudness_y_min_features,
            loudness_y_max_features,
            loudness_use_db_features,
            voicing_use_probs_features
        ],
        outputs=[piano_roll_features, features_status_text, reference_audio_features],
        show_progress=True
    )

    # Generate demo audio and analyze button
    def create_and_analyze_feature_demo():
        """Generate demo audio for feature analysis and automatically analyze it."""
        demo_audio_path = generate_feature_demo_audio()
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

            # Perform audio feature analysis (F0, loudness, voice/unvoice)
            updated_piano_roll, status, _ = analyze_uploaded_audio_features(
                initial_piano_roll, demo_audio_path,
                include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin",
                loudness_y_min=None, loudness_y_max=None, loudness_use_db=True, voicing_use_probs=True
            )

            return updated_piano_roll, status, demo_audio_path, demo_audio_path
        else:
            return initial_value_features, "Failed to generate demo audio.", None, None

    btn_generate_feature_demo.click(
        fn=create_and_analyze_feature_demo,
        outputs=[piano_roll_features, features_status_text, audio_upload_features, reference_audio_features],
        show_progress=True
    )

    # Update JSON output when note changes
    def update_features_json_output(piano_roll_data):
        return piano_roll_data

    piano_roll_features.change(
        fn=update_features_json_output,
        inputs=[piano_roll_features],
        outputs=[output_json_features],
        show_progress=False
    )

    # Log play event
    def log_features_play_event(event_data=None):
        print("🔊 Features Play event triggered:", event_data)
        return f"Play started: {event_data if event_data else 'Playing'}"

    def log_features_pause_event(event_data=None):
        print("🔊 Features Pause event triggered:", event_data)
        return f"Paused: {event_data if event_data else 'Paused'}"

    def log_features_stop_event(event_data=None):
        print("🔊 Features Stop event triggered:", event_data)
        return f"Stopped: {event_data if event_data else 'Stopped'}"

    piano_roll_features.play(log_features_play_event, outputs=features_status_text)
    piano_roll_features.pause(log_features_pause_event, outputs=features_status_text)
    piano_roll_features.stop(log_features_stop_event, outputs=features_status_text)

    if not LIBROSA_AVAILABLE:
        gr.Markdown("⚠️ librosa is required")

if __name__ == "__main__":
    demo.launch()
