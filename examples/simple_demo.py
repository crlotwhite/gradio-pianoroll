import gradio as gr
from common_utils import convert_basic
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
    gr.Markdown("## Basic PianoRoll Demo")

    with gr.Row():
        with gr.Column():
            # Set initial value using research utilities
            notes = [(60, 0.5, 0.5), (64, 1.0, 1.0)]
            lyrics = ["안녕", "하세요"]
            initial_value_basic = research.from_notes(notes, tempo=120, lyrics=lyrics)
            piano_roll_basic = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_basic,
                elem_id="piano_roll_basic",  # Unique ID
                use_backend_audio=False,  # Use frontend audio engine
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
        show_progress=True,
    )

if __name__ == "__main__":
    demo.launch()
