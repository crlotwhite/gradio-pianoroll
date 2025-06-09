import gradio as gr
from gradio_pianoroll import PianoRoll
from common_utils import (
    convert_basic,
)

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
    gr.Markdown("## Basic PianoRoll Demo")

    with gr.Row():
        with gr.Column():
            # Set initial value
            initial_value_basic = {
                "notes": [
                    {
                        "start": 80,
                        "duration": 80,
                        "pitch": 60,
                        "velocity": 100,
                        "lyric": "안녕"
                    },
                    {
                        "start": 160,
                        "duration": 160,
                        "pitch": 64,
                        "velocity": 90,
                        "lyric": "하세요"
                    }
                ],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4"
            }
            piano_roll_basic = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_basic,
                elem_id="piano_roll_basic",  # Unique ID
                use_backend_audio=False  # Use frontend audio engine
            )

    with gr.Row():
        with gr.Column():
            output_json_basic = gr.JSON()

    with gr.Row():
        with gr.Column():
            btn_basic = gr.Button("🔄 Convert & Debug", variant="primary")

    # Basic tab events
    btn_basic.click(
        fn=convert_basic,
        inputs=piano_roll_basic,
        outputs=output_json_basic,
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch()
