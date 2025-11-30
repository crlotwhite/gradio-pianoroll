"""
Pytest configuration and shared fixtures for gradio_pianoroll tests.

This module contains fixtures and configuration that are shared across all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add the backend directory to the Python path for imports
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))


# =============================================================================
# Common Constants for Testing
# =============================================================================

# Standard test values for timing calculations
DEFAULT_PIXELS_PER_BEAT = 80.0
DEFAULT_TEMPO = 120.0
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_PPQN = 480  # Pulses Per Quarter Note (MIDI standard)

# Flicks constant (from Facebook's Flicks library)
FLICKS_PER_SECOND = 705600000


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def default_timing_params():
    """
    Provide default timing parameters for tests.
    
    Returns:
        dict: Dictionary with pixels_per_beat, tempo, sample_rate, and ppqn.
    """
    return {
        "pixels_per_beat": DEFAULT_PIXELS_PER_BEAT,
        "tempo": DEFAULT_TEMPO,
        "sample_rate": DEFAULT_SAMPLE_RATE,
        "ppqn": DEFAULT_PPQN,
    }


@pytest.fixture
def test_note_params():
    """
    Provide sample note parameters for testing note creation.
    
    Returns:
        dict: Dictionary with note properties.
    """
    return {
        "note_id": "note-test-12345",
        "start_pixels": 160.0,  # 2 beats at 80 pixels/beat
        "duration_pixels": 80.0,  # 1 beat
        "pitch": 60,  # Middle C (C4)
        "velocity": 100,
        "lyric": "라",
    }


@pytest.fixture
def various_tempos():
    """
    Provide a list of various tempos for parametrized testing.
    
    Returns:
        list: List of tempo values (BPM).
    """
    return [60.0, 90.0, 120.0, 140.0, 180.0, 200.0]


@pytest.fixture
def various_zoom_levels():
    """
    Provide a list of various zoom levels for parametrized testing.
    
    Returns:
        list: List of pixels_per_beat values.
    """
    return [20.0, 40.0, 80.0, 160.0, 320.0]
