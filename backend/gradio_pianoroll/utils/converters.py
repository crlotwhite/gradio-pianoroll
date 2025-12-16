"""
Data conversion functions for creating piano roll data.

This module provides functions to convert various data formats
(notes, MIDI numbers, frequencies, TTS output, MIDI generation)
into the piano roll data format.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from ..data_models import PianoRollDataClass, clean_piano_roll_data
from ..timing_utils import generate_note_id
from ._internal import _create_f0_line_data

# =============================================================================
# Quick Creation Functions
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
        >>> notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]  # C-E-G chord
        >>> data = from_notes(notes, tempo=120)
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

    Returns:
        Piano roll data dictionary.

    Example:
        >>> # C major scale
        >>> midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
        >>> data = from_midi_numbers(midi_notes)
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

    Returns:
        Piano roll data dictionary.

    Example:
        >>> # A4, B4, C5
        >>> frequencies = [440, 493.88, 523.25]
        >>> data = from_frequencies(frequencies)
    """
    # Convert frequency to MIDI note number
    midi_notes = [int(round(69 + 12 * np.log2(f / 440))) for f in frequencies]
    return from_midi_numbers(midi_notes, durations, start_times, tempo)


# =============================================================================
# Model Output Conversion Functions
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
        >>> alignment = [("an", 0.0, 0.5), ("nyeong", 0.5, 1.0)]
        >>> f0_data = [220, 230, 240, 235, 225]  # 5 frames of F0
        >>> data = from_tts_output("hello", alignment, f0_data)
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

    result: dict = {
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


def from_midi_generation(
    generated_sequence: List[Dict], tempo: int = 120
) -> PianoRollDataClass:
    """
    Convert MIDI generation model output to piano roll.

    Args:
        generated_sequence: List of note dictionaries with keys:
            - pitch (int): MIDI pitch
            - start (float): Start time in seconds
            - duration (float): Duration in seconds
            - velocity (int, optional): Note velocity
        tempo: BPM.

    Returns:
        Piano roll data dictionary.

    Example:
        >>> sequence = [
        ...     {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100},
        ...     {"pitch": 64, "start": 0.5, "duration": 0.5, "velocity": 90}
        ... ]
        >>> data = from_midi_generation(sequence)
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

    result: dict = {
        "notes": notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    return clean_piano_roll_data(result)
