"""
Unit tests for timing_utils module.

Tests cover:
- generate_note_id: Unique ID generation
- pixels_to_flicks: Pixel to flicks conversion
- pixels_to_seconds: Pixel to seconds conversion
- pixels_to_beats: Pixel to beats conversion
- pixels_to_ticks: Pixel to MIDI ticks conversion
- pixels_to_samples: Pixel to audio samples conversion
- calculate_all_timing_data: Combined timing data calculation
- create_note_with_timing: Note creation with timing data
"""

import pytest
import re
from gradio_pianoroll.timing_utils import (
    generate_note_id,
    pixels_to_flicks,
    pixels_to_seconds,
    pixels_to_beats,
    pixels_to_ticks,
    pixels_to_samples,
    calculate_all_timing_data,
    create_note_with_timing,
)


# =============================================================================
# Constants for Testing
# =============================================================================

FLICKS_PER_SECOND = 705600000


# =============================================================================
# Tests for generate_note_id
# =============================================================================

class TestGenerateNoteId:
    """Tests for generate_note_id function."""

    def test_format(self):
        """Test that generated ID matches expected format."""
        note_id = generate_note_id()
        # Format: note-{timestamp}-{5 random chars}
        pattern = r"^note-\d+-[a-z0-9]{5}$"
        assert re.match(pattern, note_id), f"ID '{note_id}' doesn't match expected format"

    def test_uniqueness(self):
        """Test that multiple calls generate unique IDs."""
        ids = [generate_note_id() for _ in range(100)]
        assert len(set(ids)) == 100, "Generated IDs are not unique"

    def test_starts_with_note(self):
        """Test that ID starts with 'note-' prefix."""
        note_id = generate_note_id()
        assert note_id.startswith("note-")


# =============================================================================
# Tests for pixels_to_flicks
# =============================================================================

class TestPixelsToFlicks:
    """Tests for pixels_to_flicks function."""

    def test_zero_pixels(self, default_timing_params):
        """Test conversion of zero pixels."""
        result = pixels_to_flicks(
            0.0,
            default_timing_params["pixels_per_beat"],
            default_timing_params["tempo"],
        )
        assert result == 0.0

    def test_one_beat_at_120bpm(self):
        """Test one beat at 120 BPM (0.5 seconds)."""
        pixels_per_beat = 80.0
        tempo = 120.0
        pixels = 80.0  # 1 beat

        result = pixels_to_flicks(pixels, pixels_per_beat, tempo)
        
        # 1 beat at 120 BPM = 0.5 seconds = 0.5 * FLICKS_PER_SECOND
        expected = 0.5 * FLICKS_PER_SECOND
        assert abs(result - expected) < 1, f"Expected {expected}, got {result}"

    def test_one_second_at_60bpm(self):
        """Test conversion that equals exactly 1 second."""
        pixels_per_beat = 80.0
        tempo = 60.0
        pixels = 80.0  # 1 beat at 60 BPM = 1 second

        result = pixels_to_flicks(pixels, pixels_per_beat, tempo)
        
        assert abs(result - FLICKS_PER_SECOND) < 1

    def test_scaling_with_tempo(self):
        """Test that flicks scale inversely with tempo."""
        pixels_per_beat = 80.0
        pixels = 80.0

        flicks_at_60 = pixels_to_flicks(pixels, pixels_per_beat, 60.0)
        flicks_at_120 = pixels_to_flicks(pixels, pixels_per_beat, 120.0)

        # At double tempo, same pixel distance should be half the time
        assert abs(flicks_at_60 - 2 * flicks_at_120) < 1


# =============================================================================
# Tests for pixels_to_seconds
# =============================================================================

class TestPixelsToSeconds:
    """Tests for pixels_to_seconds function."""

    def test_zero_pixels(self, default_timing_params):
        """Test conversion of zero pixels."""
        result = pixels_to_seconds(
            0.0,
            default_timing_params["pixels_per_beat"],
            default_timing_params["tempo"],
        )
        assert result == 0.0

    def test_one_beat_at_120bpm(self):
        """Test one beat at 120 BPM equals 0.5 seconds."""
        result = pixels_to_seconds(80.0, 80.0, 120.0)
        assert abs(result - 0.5) < 1e-10

    def test_one_beat_at_60bpm(self):
        """Test one beat at 60 BPM equals 1 second."""
        result = pixels_to_seconds(80.0, 80.0, 60.0)
        assert abs(result - 1.0) < 1e-10

    def test_four_beats_at_120bpm(self):
        """Test four beats at 120 BPM equals 2 seconds."""
        result = pixels_to_seconds(320.0, 80.0, 120.0)
        assert abs(result - 2.0) < 1e-10


# =============================================================================
# Tests for pixels_to_beats
# =============================================================================

class TestPixelsToBeats:
    """Tests for pixels_to_beats function."""

    def test_zero_pixels(self):
        """Test conversion of zero pixels."""
        result = pixels_to_beats(0.0, 80.0)
        assert result == 0.0

    def test_one_beat(self):
        """Test exactly one beat."""
        result = pixels_to_beats(80.0, 80.0)
        assert result == 1.0

    def test_fractional_beat(self):
        """Test half beat."""
        result = pixels_to_beats(40.0, 80.0)
        assert result == 0.5

    def test_multiple_beats(self):
        """Test multiple beats."""
        result = pixels_to_beats(320.0, 80.0)
        assert result == 4.0

    def test_different_zoom(self):
        """Test with different zoom level."""
        result = pixels_to_beats(160.0, 40.0)
        assert result == 4.0


# =============================================================================
# Tests for pixels_to_ticks
# =============================================================================

class TestPixelsToTicks:
    """Tests for pixels_to_ticks function."""

    def test_zero_pixels(self):
        """Test conversion of zero pixels."""
        result = pixels_to_ticks(0.0, 80.0)
        assert result == 0

    def test_one_beat_default_ppqn(self):
        """Test one beat with default PPQN (480)."""
        result = pixels_to_ticks(80.0, 80.0)
        assert result == 480

    def test_half_beat_default_ppqn(self):
        """Test half beat with default PPQN."""
        result = pixels_to_ticks(40.0, 80.0)
        assert result == 240

    def test_custom_ppqn(self):
        """Test with custom PPQN value."""
        result = pixels_to_ticks(80.0, 80.0, ppqn=960)
        assert result == 960


# =============================================================================
# Tests for pixels_to_samples
# =============================================================================

class TestPixelsToSamples:
    """Tests for pixels_to_samples function."""

    def test_zero_pixels(self, default_timing_params):
        """Test conversion of zero pixels."""
        result = pixels_to_samples(
            0.0,
            default_timing_params["pixels_per_beat"],
            default_timing_params["tempo"],
        )
        assert result == 0

    def test_one_second_worth(self):
        """Test conversion of one second worth of pixels."""
        # At 60 BPM, 1 beat = 1 second
        result = pixels_to_samples(80.0, 80.0, 60.0, 44100)
        assert result == 44100

    def test_half_second(self):
        """Test conversion of 0.5 seconds (1 beat at 120 BPM)."""
        result = pixels_to_samples(80.0, 80.0, 120.0, 44100)
        assert result == 22050


# =============================================================================
# Tests for calculate_all_timing_data
# =============================================================================

class TestCalculateAllTimingData:
    """Tests for calculate_all_timing_data function."""

    def test_returns_all_keys(self, default_timing_params):
        """Test that result contains all expected keys."""
        result = calculate_all_timing_data(
            80.0,
            default_timing_params["pixels_per_beat"],
            default_timing_params["tempo"],
        )
        expected_keys = {"seconds", "beats", "flicks", "ticks", "samples"}
        assert set(result.keys()) == expected_keys

    def test_consistency(self):
        """Test that individual functions match combined result."""
        pixels = 160.0
        pixels_per_beat = 80.0
        tempo = 120.0

        result = calculate_all_timing_data(pixels, pixels_per_beat, tempo)

        assert result["seconds"] == pixels_to_seconds(pixels, pixels_per_beat, tempo)
        assert result["beats"] == pixels_to_beats(pixels, pixels_per_beat)
        assert result["flicks"] == pixels_to_flicks(pixels, pixels_per_beat, tempo)
        assert result["ticks"] == pixels_to_ticks(pixels, pixels_per_beat)
        assert result["samples"] == pixels_to_samples(pixels, pixels_per_beat, tempo)


# =============================================================================
# Tests for create_note_with_timing
# =============================================================================

class TestCreateNoteWithTiming:
    """Tests for create_note_with_timing function."""

    def test_returns_all_fields(self, test_note_params, default_timing_params):
        """Test that result contains all expected fields."""
        result = create_note_with_timing(
            note_id=test_note_params["note_id"],
            start_pixels=test_note_params["start_pixels"],
            duration_pixels=test_note_params["duration_pixels"],
            pitch=test_note_params["pitch"],
            velocity=test_note_params["velocity"],
            lyric=test_note_params["lyric"],
            pixels_per_beat=default_timing_params["pixels_per_beat"],
            tempo=default_timing_params["tempo"],
        )

        expected_keys = {
            "id", "start", "duration",
            "startFlicks", "durationFlicks",
            "startSeconds", "durationSeconds", "endSeconds",
            "startBeats", "durationBeats",
            "startTicks", "durationTicks",
            "startSample", "durationSamples",
            "pitch", "velocity", "lyric",
        }
        assert set(result.keys()) == expected_keys

    def test_basic_values(self, test_note_params):
        """Test that basic note values are correctly set."""
        result = create_note_with_timing(
            note_id=test_note_params["note_id"],
            start_pixels=test_note_params["start_pixels"],
            duration_pixels=test_note_params["duration_pixels"],
            pitch=test_note_params["pitch"],
            velocity=test_note_params["velocity"],
            lyric=test_note_params["lyric"],
        )

        assert result["id"] == test_note_params["note_id"]
        assert result["start"] == test_note_params["start_pixels"]
        assert result["duration"] == test_note_params["duration_pixels"]
        assert result["pitch"] == test_note_params["pitch"]
        assert result["velocity"] == test_note_params["velocity"]
        assert result["lyric"] == test_note_params["lyric"]

    def test_end_seconds_calculation(self):
        """Test that endSeconds equals startSeconds + durationSeconds."""
        result = create_note_with_timing(
            note_id="test",
            start_pixels=160.0,
            duration_pixels=80.0,
            pitch=60,
            velocity=100,
            lyric="test",
        )

        expected_end = result["startSeconds"] + result["durationSeconds"]
        assert abs(result["endSeconds"] - expected_end) < 1e-10

    def test_timing_consistency(self):
        """Test that timing values are consistent with each other."""
        result = create_note_with_timing(
            note_id="test",
            start_pixels=80.0,  # 1 beat
            duration_pixels=80.0,  # 1 beat
            pitch=60,
            velocity=100,
            lyric="test",
            pixels_per_beat=80.0,
            tempo=120.0,
        )

        # At 120 BPM, 1 beat = 0.5 seconds
        assert abs(result["startBeats"] - 1.0) < 1e-10
        assert abs(result["durationBeats"] - 1.0) < 1e-10
        assert abs(result["startSeconds"] - 0.5) < 1e-10
        assert abs(result["durationSeconds"] - 0.5) < 1e-10
