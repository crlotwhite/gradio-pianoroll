"""
Timing and note utility functions for the PianoRoll backend.

This module provides conversion utilities between pixels, flicks, seconds, beats, ticks, and samples,
as well as note creation helpers. These are used for synchronizing frontend and backend timing logic
in the piano roll application.

Functions:
    - generate_note_id: Generate a unique note ID (compatible with frontend algorithm)
    - pixels_to_flicks: Convert pixels to flicks (for precise timing)
    - pixels_to_seconds: Convert pixels to seconds (for audio processing)
    - pixels_to_beats: Convert pixels to musical beats
    - pixels_to_ticks: Convert pixels to MIDI ticks
    - pixels_to_samples: Convert pixels to audio samples
    - calculate_all_timing_data: Get all timing representations for a pixel value
    - create_note_with_timing: Create a note dict with all timing data
"""

import time
import random
import string


def generate_note_id() -> str:
    """
    Generate a unique note ID using the same algorithm as the frontend.
    Format: note-{timestamp}-{random_string}
    Returns:
        str: Unique note ID string.
    """
    timestamp = int(time.time() * 1000)  # Milliseconds like Date.now()
    random_chars = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"note-{timestamp}-{random_chars}"


def pixels_to_flicks(pixels: float, pixels_per_beat: float, tempo: float) -> float:
    """
    Convert pixels to flicks for accurate timing calculation.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
        tempo (float): Tempo in BPM.
    Returns:
        float: Flicks value (precise timing unit).
    """
    FLICKS_PER_SECOND = 705600000
    return (pixels * 60 * FLICKS_PER_SECOND) / (pixels_per_beat * tempo)


def pixels_to_seconds(pixels: float, pixels_per_beat: float, tempo: float) -> float:
    """
    Convert pixels to seconds for direct audio processing.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
        tempo (float): Tempo in BPM.
    Returns:
        float: Time in seconds.
    """
    return (pixels * 60) / (pixels_per_beat * tempo)


def pixels_to_beats(pixels: float, pixels_per_beat: float) -> float:
    """
    Convert pixels to beats for musical accuracy.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
    Returns:
        float: Number of beats.
    """
    return pixels / pixels_per_beat


def pixels_to_ticks(pixels: float, pixels_per_beat: float, ppqn: int = 480) -> int:
    """
    Convert pixels to MIDI ticks for MIDI compatibility.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
        ppqn (int, optional): Pulses Per Quarter Note. Defaults to 480.
    Returns:
        int: MIDI tick value.
    """
    beats = pixels_to_beats(pixels, pixels_per_beat)
    return int(beats * ppqn)


def pixels_to_samples(
    pixels: float, pixels_per_beat: float, tempo: float, sample_rate: int = 44100
) -> int:
    """
    Convert pixels to audio samples for precise digital audio processing.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
        tempo (float): Tempo in BPM.
        sample_rate (int, optional): Audio sample rate. Defaults to 44100.
    Returns:
        int: Number of audio samples.
    """
    seconds = pixels_to_seconds(pixels, pixels_per_beat, tempo)
    return int(seconds * sample_rate)


def calculate_all_timing_data(
    pixels: float,
    pixels_per_beat: float,
    tempo: float,
    sample_rate: int = 44100,
    ppqn: int = 480,
) -> dict:
    """
    Calculate all timing representations for a given pixel value.
    Args:
        pixels (float): Pixel value to convert.
        pixels_per_beat (float): Number of pixels per beat (zoom level).
        tempo (float): Tempo in BPM.
        sample_rate (int, optional): Audio sample rate. Defaults to 44100.
        ppqn (int, optional): Pulses Per Quarter Note. Defaults to 480.
    Returns:
        dict: Dictionary with keys 'seconds', 'beats', 'flicks', 'ticks', 'samples'.
    """
    return {
        "seconds": pixels_to_seconds(pixels, pixels_per_beat, tempo),
        "beats": pixels_to_beats(pixels, pixels_per_beat),
        "flicks": pixels_to_flicks(pixels, pixels_per_beat, tempo),
        "ticks": pixels_to_ticks(pixels, pixels_per_beat, ppqn),
        "samples": pixels_to_samples(pixels, pixels_per_beat, tempo, sample_rate),
    }


def create_note_with_timing(
    note_id: str,
    start_pixels: float,
    duration_pixels: float,
    pitch: int,
    velocity: int,
    lyric: str,
    pixels_per_beat: float = 80,
    tempo: float = 120,
    sample_rate: int = 44100,
    ppqn: int = 480,
) -> dict:
    """
    Create a note with all timing data calculated from pixel values.
    Args:
        note_id (str): Unique identifier for the note.
        start_pixels (float): Start position in pixels.
        duration_pixels (float): Duration in pixels.
        pitch (int): MIDI pitch (0-127).
        velocity (int): MIDI velocity (0-127).
        lyric (str): Lyric text for the note.
        pixels_per_beat (float, optional): Zoom level in pixels per beat. Defaults to 80.
        tempo (float, optional): BPM tempo. Defaults to 120.
        sample_rate (int, optional): Audio sample rate. Defaults to 44100.
        ppqn (int, optional): Pulses per quarter note for MIDI tick calculations. Defaults to 480.
    Returns:
        dict: Dictionary containing note data with all timing representations.
    """
    start_timing = calculate_all_timing_data(
        start_pixels, pixels_per_beat, tempo, sample_rate, ppqn
    )
    duration_timing = calculate_all_timing_data(
        duration_pixels, pixels_per_beat, tempo, sample_rate, ppqn
    )
    return {
        "id": note_id,
        "start": start_pixels,
        "duration": duration_pixels,
        "startFlicks": start_timing["flicks"],
        "durationFlicks": duration_timing["flicks"],
        "startSeconds": start_timing["seconds"],
        "durationSeconds": duration_timing["seconds"],
        "endSeconds": start_timing["seconds"] + duration_timing["seconds"],
        "startBeats": start_timing["beats"],
        "durationBeats": duration_timing["beats"],
        "startTicks": start_timing["ticks"],
        "durationTicks": duration_timing["ticks"],
        "startSample": start_timing["samples"],
        "durationSamples": duration_timing["samples"],
        "pitch": pitch,
        "velocity": velocity,
        "lyric": lyric,
    }
