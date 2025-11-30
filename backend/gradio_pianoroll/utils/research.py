"""
Helper function library for researchers.

This module enables researchers to easily use the piano roll component
by processing complex tasks through simple function calls.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import gradio as gr

from ..timing_utils import generate_note_id
from ..data_models import (
    PianoRollDataClass,
    NoteData,
    clean_piano_roll_data,
)

# =============================================================================
# 1. Quick Creation Functions
# =============================================================================


def from_notes(
    notes: List[Tuple[int, float, float]],
    tempo: int = 120,
    lyrics: Optional[List[str]] = None,
) -> PianoRollDataClass:
    """
    Create piano roll data from a simple note list.

    Args:
        notes: List of (pitch, start_time_sec, duration_sec) tuples.
        tempo: BPM (default: 120).
        lyrics: Lyrics list (optional).

    Returns:
        Piano roll data dictionary.

    Example:
        notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]  # C-E-G chord
        data = from_notes(notes, tempo=120)
    """
    pixels_per_beat = 80

    piano_roll_notes = []
    for i, (pitch, start_sec, duration_sec) in enumerate(notes):
        # Convert seconds to pixels
        start_pixels = start_sec * (tempo / 60) * pixels_per_beat
        duration_pixels = duration_sec * (tempo / 60) * pixels_per_beat

        note_data = {
            "id": generate_note_id(),
            "start": start_pixels,
            "duration": duration_pixels,
            "pitch": pitch,
            "velocity": 100,
        }

        # Add lyrics if available
        if lyrics and i < len(lyrics):
            note_data["lyric"] = lyrics[i]

        piano_roll_notes.append(note_data)

    result: dict = {
        "notes": piano_roll_notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    return clean_piano_roll_data(result)


def from_midi_numbers(
    midi_notes: List[int],
    durations: Optional[List[float]] = None,
    start_times: Optional[List[float]] = None,
    tempo: int = 120,
) -> PianoRollDataClass:
    """
    Create piano roll from MIDI note number list.

    Args:
        midi_notes: MIDI note numbers (0-127).
        durations: Duration of each note (seconds). Defaults to 1 second for all.
        start_times: Start time of each note (seconds). Defaults to sequential placement.
        tempo: BPM.

    Example:
        # C major scale
        midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
        data = from_midi_numbers(midi_notes)
    """
    if durations is None:
        durations = [1.0] * len(midi_notes)
    if start_times is None:
        start_times = [i * 1.0 for i in range(len(midi_notes))]

    notes = list(zip(midi_notes, start_times, durations))
    return from_notes(notes, tempo)


def from_frequencies(
    frequencies: List[float],
    durations: Optional[List[float]] = None,
    start_times: Optional[List[float]] = None,
    tempo: int = 120,
) -> PianoRollDataClass:
    """
    Create piano roll from frequency (Hz) list.

    Args:
        frequencies: Frequency values (Hz).
        durations: Duration of each note (seconds).
        start_times: Start time of each note (seconds).
        tempo: BPM.

    Example:
        # A4, B4, C5
        frequencies = [440, 493.88, 523.25]
        data = from_frequencies(frequencies)
    """
    # Convert frequency to MIDI note number
    midi_notes = [int(round(69 + 12 * np.log2(f / 440))) for f in frequencies]
    return from_midi_numbers(midi_notes, durations, start_times, tempo)


# =============================================================================
# 2. Model Output Conversion Functions
# =============================================================================


def from_tts_output(
    text: str,
    alignment: List[Tuple[str, float, float]],
    f0_data: Optional[List[float]] = None,
    tempo: int = 120,
) -> PianoRollDataClass:
    """
    Convert TTS model alignment result to piano roll.

    Args:
        text: Original text.
        alignment: (word/phoneme, start_time, end_time) tuples.
        f0_data: F0 curve data (optional).
        tempo: BPM.

    Returns:
        Piano roll data.

    Example:
        alignment = [("an", 0.0, 0.5), ("nyeong", 0.5, 1.0)]
        f0_data = [220, 230, 240, 235, 225]  # 5 frames of F0
        data = from_tts_output("hello", alignment, f0_data)
    """
    pixels_per_beat = 80
    notes = []

    for word, start_time, end_time in alignment:
        duration = end_time - start_time

        # If F0 data is available, use average F0 of the segment as pitch
        if f0_data:
            # Simple segment mapping (more sophisticated mapping needed in practice)
            f0_segment_start = int(start_time * len(f0_data) / alignment[-1][2])
            f0_segment_end = int(end_time * len(f0_data) / alignment[-1][2])
            segment_f0 = f0_data[f0_segment_start:f0_segment_end]
            avg_f0 = np.mean([f for f in segment_f0 if f > 0]) if segment_f0 else 220
            pitch = int(round(69 + 12 * np.log2(avg_f0 / 440)))
        else:
            pitch = 60  # Default: C4

        note = {
            "id": generate_note_id(),
            "start": start_time * (tempo / 60) * pixels_per_beat,
            "duration": duration * (tempo / 60) * pixels_per_beat,
            "pitch": max(0, min(127, pitch)),  # Clamp to MIDI range
            "velocity": 100,
            "lyric": word,
        }
        notes.append(note)

    result = {
        "notes": notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    # Add F0 curve data
    if f0_data:
        result["line_data"] = _create_f0_line_data(
            f0_data, alignment[-1][2], tempo, pixels_per_beat
        )

    return clean_piano_roll_data(result)


def from_midi_generation(generated_sequence: List[Dict], tempo: int = 120) -> PianoRollDataClass:
    """
    Convert MIDI generation model output to piano roll.

    Args:
        generated_sequence: [{"pitch": int, "start": float, "duration": float, "velocity": int}, ...].
        tempo: BPM.

    Example:
        sequence = [
            {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100},
            {"pitch": 64, "start": 0.5, "duration": 0.5, "velocity": 90}
        ]
        data = from_midi_generation(sequence)
    """
    pixels_per_beat = 80
    notes = []

    for note_data in generated_sequence:
        note = {
            "id": generate_note_id(),
            "start": note_data["start"] * (tempo / 60) * pixels_per_beat,
            "duration": note_data["duration"] * (tempo / 60) * pixels_per_beat,
            "pitch": note_data["pitch"],
            "velocity": note_data.get("velocity", 100),
        }

        # Include lyrics or additional info if available
        if "lyric" in note_data:
            note["lyric"] = note_data["lyric"]
        if "phoneme" in note_data:
            note["phoneme"] = note_data["phoneme"]

        notes.append(note)

    result = {
        "notes": notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    return clean_piano_roll_data(result)


def _create_f0_line_data(
    f0_values: List[float], total_duration: float, tempo: int, pixels_per_beat: int
) -> Dict:
    """Convert F0 data to LineLayer format."""
    data_points = []

    for i, f0 in enumerate(f0_values):
        if f0 > 0:  # Valid F0 only
            time_sec = (i / len(f0_values)) * total_duration
            x_pixel = time_sec * (tempo / 60) * pixels_per_beat

            # Convert F0 to MIDI note, then to Y coordinate
            midi_note = 69 + 12 * np.log2(f0 / 440)
            y_pixel = (127 - midi_note) * 20  # 20 is NOTE_HEIGHT

            data_points.append({"x": x_pixel, "y": y_pixel})

    return {
        "f0_curve": {
            "color": "#FF6B6B",
            "lineWidth": 2,
            "yMin": 0,
            "yMax": 2560,
            "position": "overlay",
            "renderMode": "piano_grid",
            "data": data_points,
        }
    }


# =============================================================================
# 3. Template Creation Functions
# =============================================================================


def create_pianoroll_with_data(data: Dict, **component_kwargs) -> gr.Blocks:
    """
    Create a Gradio demo with a PianoRoll component from data.

    Args:
        data: Piano roll data.
        **component_kwargs: Additional arguments to pass to PianoRoll component.

    Returns:
        Gradio Blocks demo.
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
) -> gr.Blocks:
    """
    Create a piano roll demo in 3 lines.

    Args:
        notes: (pitch, start_time, duration) note list.
        title: Demo title.
        tempo: BPM.
        **component_kwargs: Additional arguments to pass to PianoRoll component.

    Returns:
        Gradio Blocks demo.

    Example:
        notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
        demo = quick_demo(notes, "My TTS Model Result")
        demo.launch()
    """
    import gradio as gr
    from ..pianoroll import PianoRoll

    data = from_notes(notes, tempo)

    with gr.Blocks(title=title) as demo:
        gr.Markdown(f"# {title}")
        piano_roll = PianoRoll(value=data, height=400, **component_kwargs)
        gr.JSON(label="Piano Roll Data", value=data)

    return demo


# =============================================================================
# 4. Analysis Tools
# =============================================================================


def analyze_notes(piano_roll_data: Dict) -> Dict:
    """Extract note statistics from piano roll."""
    notes = piano_roll_data.get("notes", [])

    if not notes:
        return {"error": "No note data"}

    pitches = [note["pitch"] for note in notes]
    velocities = [note["velocity"] for note in notes]
    durations = [note["duration"] for note in notes]

    pixels_per_beat = piano_roll_data.get("pixelsPerBeat", 80)
    tempo = piano_roll_data.get("tempo", 120)

    # Convert pixels to seconds
    durations_sec = [d / pixels_per_beat * 60 / tempo for d in durations]

    return {
        "total_notes": len(notes),
        "pitch_range": {
            "lowest": min(pitches),
            "highest": max(pitches),
            "range": max(pitches) - min(pitches),
        },
        "avg_pitch": round(np.mean(pitches), 1),
        "avg_velocity": round(np.mean(velocities), 1),
        "avg_note_duration_sec": round(np.mean(durations_sec), 2),
        "total_playback_time_sec": round(
            max([n["start"] + n["duration"] for n in notes])
            / pixels_per_beat
            * 60
            / tempo,
            2,
        ),
        "rhythm_analysis": {
            "shortest_note_sec": round(min(durations_sec), 3),
            "longest_note_sec": round(max(durations_sec), 3),
            "std_deviation": round(np.std(durations_sec), 3),
        },
    }


# =============================================================================
# 5. Auto Analysis Function
# =============================================================================


def auto_analyze(
    model_output_data: Union[List, Dict], output_type: str = "auto"
) -> PianoRollDataClass:
    """
    Automatically analyze model output and convert to piano roll format.

    Args:
        model_output_data: Model output data.
        output_type: "auto", "tts", "midi_generation", "frequencies".

    Returns:
        Piano roll data.
    """
    if output_type == "auto":
        # Auto-detect by examining data format
        if isinstance(model_output_data, list) and len(model_output_data) > 0:
            if (
                isinstance(model_output_data[0], (tuple, list))
                and len(model_output_data[0]) >= 3
            ):
                # Assume (pitch, time, duration) format
                return from_notes(model_output_data)
            elif (
                isinstance(model_output_data[0], dict)
                and "pitch" in model_output_data[0]
            ):
                # Assume MIDI generation model output
                return from_midi_generation(model_output_data)

    elif output_type == "tts":
        # Process as TTS alignment data
        return from_tts_output("", model_output_data)

    elif output_type == "midi_generation":
        return from_midi_generation(model_output_data)

    elif output_type == "frequencies":
        return from_frequencies(model_output_data)

    # Default: return empty piano roll
    return from_notes([])
