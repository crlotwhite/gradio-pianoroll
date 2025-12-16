"""
Analysis tools for piano roll data.

This module provides functions to analyze and automatically
convert various data formats to piano roll format.
"""

from __future__ import annotations

from typing import Dict, List, Union

import numpy as np

from ..data_models import PianoRollDataClass
from .converters import from_frequencies, from_midi_generation, from_notes, from_tts_output


def analyze_notes(piano_roll_data: Dict) -> Dict:
    """
    Extract note statistics from piano roll data.

    Args:
        piano_roll_data: Piano roll data dictionary containing notes.

    Returns:
        Dictionary with analysis results including:
        - total_notes: Number of notes
        - pitch_range: Lowest, highest pitch and range
        - avg_pitch: Average pitch
        - avg_velocity: Average velocity
        - avg_note_duration_sec: Average note duration in seconds
        - total_playback_time_sec: Total playback time
        - rhythm_analysis: Shortest, longest note and standard deviation

    Example:
        >>> data = {"notes": [{"pitch": 60, "duration": 80, "start": 0, "velocity": 100}], "tempo": 120, "pixelsPerBeat": 80}
        >>> stats = analyze_notes(data)
        >>> stats["total_notes"]
        1
    """
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
        "avg_pitch": round(float(np.mean(pitches)), 1),
        "avg_velocity": round(float(np.mean(velocities)), 1),
        "avg_note_duration_sec": round(float(np.mean(durations_sec)), 2),
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
            "std_deviation": round(float(np.std(durations_sec)), 3),
        },
    }


def auto_analyze(
    model_output_data: Union[List, Dict], output_type: str = "auto"
) -> PianoRollDataClass:
    """
    Automatically analyze model output and convert to piano roll format.

    This function attempts to detect the format of the input data and
    convert it to the appropriate piano roll format.

    Args:
        model_output_data: Model output data in various formats.
        output_type: Type hint for conversion. One of:
            - "auto": Automatically detect format
            - "tts": TTS alignment data
            - "midi_generation": MIDI generation model output
            - "frequencies": List of frequencies in Hz

    Returns:
        Piano roll data dictionary.

    Example:
        >>> # Auto-detect note tuples
        >>> data = auto_analyze([(60, 0, 1), (64, 1, 1)])
        >>> len(data["notes"])
        2

        >>> # Auto-detect MIDI generation format
        >>> midi_data = [{"pitch": 60, "start": 0, "duration": 1}]
        >>> data = auto_analyze(midi_data)
        >>> len(data["notes"])
        1
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
