import gradio as gr
from gradio_pianoroll import PianoRoll


def passthrough(piano_roll):
    """Return the PianoRoll data unchanged."""
    return piano_roll


demo = gr.Interface(fn=passthrough, inputs=PianoRoll(), outputs=PianoRoll())

if __name__ == "__main__":
    demo.launch()
