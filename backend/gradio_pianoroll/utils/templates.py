"""
Template generation module for researchers.

This module provides various domain-specific templates
to help researchers quickly create prototypes.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    import gradio as gr

from .research import from_notes, from_midi_numbers, from_frequencies


def create_basic_template() -> gr.Blocks:
    """Basic piano roll template (create in 3 lines)."""
    import gradio as gr
    from ..pianoroll import PianoRoll

    with gr.Blocks() as demo:
        piano_roll = PianoRoll()
        piano_roll.change(
            lambda x: f"Notes: {len(x.get('notes', []))}",
            inputs=piano_roll,
            outputs=gr.Textbox(),
        )
    return demo


def create_tts_template() -> gr.Blocks:
    """TTS researcher template."""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def visualize_tts_output(text_input):
        """Display TTS model output in piano roll."""
        words = text_input.split()
        notes = []
        for i, word in enumerate(words):
            notes.append(
                {
                    "id": f"note_{i}",
                    "start": i * 160,
                    "duration": 160,
                    "pitch": 60 + (i % 12),
                    "velocity": 100,
                    "lyric": word,
                }
            )
        return {"notes": notes, "tempo": 120}

    with gr.Blocks(title="TTS Researcher Piano Roll") as demo:
        gr.Markdown("## 🎤 TTS Model Result Visualization")

        with gr.Row():
            text_input = gr.Textbox(
                label="Input Text", placeholder="Hello this is a piano roll"
            )
            generate_btn = gr.Button("Generate", variant="primary")

        piano_roll = PianoRoll(height=400)
        generate_btn.click(visualize_tts_output, inputs=text_input, outputs=piano_roll)

    return demo


def create_midi_generation_template() -> gr.Blocks:
    """MIDI generation researcher template."""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def generate_midi_sequence(seed_notes, length):
        """MIDI generation model call (example)."""
        notes = []
        scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale

        for i in range(length):
            notes.append(
                {
                    "id": f"generated_{i}",
                    "start": i * 80,
                    "duration": 80,
                    "pitch": scale[i % len(scale)],
                    "velocity": np.random.randint(80, 120),
                }
            )

        return {"notes": notes, "tempo": 120}

    with gr.Blocks(title="MIDI Generation Researcher") as demo:
        gr.Markdown("## 🎵 MIDI Generation Model Demo")

        with gr.Row():
            length_slider = gr.Slider(4, 32, value=8, step=1, label="Number of notes to generate")
            generate_btn = gr.Button("Generate", variant="primary")

        piano_roll = PianoRoll(height=400)
        generate_btn.click(
            lambda length: generate_midi_sequence([], length),
            inputs=length_slider,
            outputs=piano_roll,
        )

    return demo


def create_audio_analysis_template() -> gr.Blocks:
    """Audio analysis researcher template."""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def analyze_audio_simple(audio_file):
        """Analyze audio file and display F0 curve."""
        if not audio_file:
            return None

        # Example F0 data generation
        time_points = np.linspace(0, 3, 100)  # 3 seconds
        f0_values = 220 + 50 * np.sin(2 * np.pi * 0.5 * time_points)  # Simple F0 curve

        # Convert F0 data to line data
        line_data = {
            "f0_curve": {
                "color": "#FF6B6B",
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,
                "position": "overlay",
                "renderMode": "piano_grid",
                "data": [
                    {"x": t * 80, "y": (127 - (69 + 12 * np.log2(f / 440))) * 20}
                    for t, f in zip(time_points, f0_values)
                ],
            }
        }

        return {"notes": [], "tempo": 120, "line_data": line_data}

    with gr.Blocks(title="Audio Analysis Researcher") as demo:
        gr.Markdown("## 📊 Audio F0 Analysis Visualization")

        audio_input = gr.Audio(label="Audio file to analyze", type="filepath")
        piano_roll = PianoRoll(height=400)

        audio_input.change(analyze_audio_simple, inputs=audio_input, outputs=piano_roll)

    return demo


def create_paper_figure_template() -> gr.Blocks:
    """Research paper figure generation template."""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def create_paper_figure(title, notes_data):
        """Create clean piano roll figure for papers."""
        return {"notes": notes_data.get("notes", []), "tempo": 120, "title": title}

    with gr.Blocks(title="Paper Figure Generator") as demo:
        gr.Markdown("## 📄 Research Paper Piano Roll Figure")

        with gr.Row():
            title_input = gr.Textbox(
                label="Figure Title", value="Model Output Visualization"
            )
            export_btn = gr.Button("Export to PNG")

        piano_roll = PianoRoll(
            height=300,
            width=800,
            value={
                "notes": [
                    {
                        "id": "1",
                        "start": 0,
                        "duration": 160,
                        "pitch": 60,
                        "velocity": 100,
                        "lyric": "Example",
                    },
                    {
                        "id": "2",
                        "start": 160,
                        "duration": 160,
                        "pitch": 64,
                        "velocity": 100,
                        "lyric": "Data",
                    },
                ]
            },
        )

    return demo


def create_all_templates() -> gr.Blocks:
    """Combined demo showing all templates in tabs."""
    import gradio as gr

    with gr.Blocks(title="🎹 Researcher Piano Roll Templates") as demo:
        gr.Markdown(
            """
        # 🎹 Researcher Piano Roll Templates

        Each tab provides simple starting templates for different research areas.
        Copy the code of the template you need!
        """
        )

        with gr.Tabs():
            with gr.Tab("🎯 Basic"):
                create_basic_template()

            with gr.Tab("🎤 TTS Research"):
                create_tts_template()

            with gr.Tab("🎵 MIDI Generation"):
                create_midi_generation_template()

            with gr.Tab("📊 Audio Analysis"):
                create_audio_analysis_template()

            with gr.Tab("📄 Paper Figure"):
                create_paper_figure_template()

    return demo
