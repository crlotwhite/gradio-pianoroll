"""
UI builder functions for creating Gradio demos with piano roll.

This module provides convenient functions to quickly create
Gradio demos with the PianoRoll component.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from .converters import from_notes

if TYPE_CHECKING:
    import gradio as gr


def create_pianoroll_with_data(data: Dict, **component_kwargs) -> "gr.Blocks":
    """
    Create a Gradio demo with a PianoRoll component from data.

    Args:
        data: Piano roll data dictionary.
        **component_kwargs: Additional arguments to pass to PianoRoll component.

    Returns:
        Gradio Blocks demo.

    Example:
        >>> from gradio_pianoroll.utils.converters import from_notes
        >>> data = from_notes([(60, 0, 1)])
        >>> demo = create_pianoroll_with_data(data)
        >>> # demo.launch()
    """
    import gradio as gr

    from ..pianoroll import PianoRoll

    with gr.Blocks() as demo:
        piano_roll = PianoRoll(value=data, **component_kwargs)

    return demo


def quick_demo(
    notes: List[Tuple[int, float, float]],
    title: str = "Quick Piano Roll Demo",
    tempo: int = 120,
    **component_kwargs,
) -> "gr.Blocks":
    """
    Create a piano roll demo in 3 lines.

    This is a convenience function for quickly creating a demo
    to visualize note data.

    Args:
        notes: (pitch, start_time, duration) note list.
        title: Demo title.
        tempo: BPM.
        **component_kwargs: Additional arguments to pass to PianoRoll component.

    Returns:
        Gradio Blocks demo.

    Example:
        >>> notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
        >>> demo = quick_demo(notes, "My TTS Model Result")
        >>> # demo.launch()
    """
    import gradio as gr

    from ..pianoroll import PianoRoll

    data = from_notes(notes, tempo)

    with gr.Blocks(title=title) as demo:
        gr.Markdown(f"# {title}")
        piano_roll = PianoRoll(value=data, height=400, **component_kwargs)
        gr.JSON(label="Piano Roll Data", value=data)

    return demo
