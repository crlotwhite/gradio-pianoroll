"""
pytest configuration and shared fixtures for gradio-pianoroll tests.
"""

import pytest
import numpy as np
from gradio_pianoroll import PianoRoll, PianoRollBackendData, Note

# Test constants
SAMPLE_RATE = 44100
TEMPO = 120
PIXELS_PER_BEAT = 80
PPQN = 480

@pytest.fixture
def default_note_data():
    """Standard note data for testing."""
    return {
        "pitch": 60,  # C4
        "velocity": 100,
        "lyric": "테스트",
        "start_pixels": 80.0,
        "duration_pixels": 160.0,
        "pixels_per_beat": PIXELS_PER_BEAT,
        "tempo": TEMPO,
        "sample_rate": SAMPLE_RATE,
        "ppqn": PPQN
    }

@pytest.fixture
def sample_frequencies():
    """Sample frequency data for testing."""
    return [440.0, 523.25, 659.25]  # A4, C5, E5

@pytest.fixture
def sample_times():
    """Sample time data for testing."""
    return [0.5, 1.0, 1.5]  # seconds

@pytest.fixture
def backend_data():
    """Clean backend data instance for testing."""
    return PianoRollBackendData()

@pytest.fixture
def sample_audio():
    """Generate sample audio for testing."""
    duration = 1.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    # Simple sine wave at A4 (440 Hz)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    return audio

@pytest.fixture
def piano_roll_instance():
    """Clean PianoRoll instance for testing."""
    return PianoRoll()

# Tolerance for floating point comparisons
FLOAT_TOLERANCE = 1e-6 