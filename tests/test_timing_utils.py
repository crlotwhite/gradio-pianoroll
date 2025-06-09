"""
Tests for timing_utils module.

This test suite covers timing conversion functions and note ID generation
that ensure synchronization between frontend and backend timing logic.
"""

import pytest
import re
from gradio_pianoroll.timing_utils import (
    generate_note_id, pixels_to_flicks, pixels_to_seconds,
    pixels_to_beats, pixels_to_ticks, pixels_to_samples,
    calculate_all_timing_data, create_note_with_timing
)
from .conftest import FLOAT_TOLERANCE, TEMPO, PIXELS_PER_BEAT, SAMPLE_RATE, PPQN


class TestNoteIdGeneration:
    """Test note ID generation."""
    
    def test_generate_note_id_format(self):
        """Test that note ID follows the correct format."""
        note_id = generate_note_id()
        
        # Should match format: note-{timestamp}-{random_string}
        pattern = r'^note-\d+-[a-z0-9]{5}$'
        assert re.match(pattern, note_id), f"Invalid note ID format: {note_id}"
    
    def test_generate_note_id_unique(self):
        """Test that generated IDs are unique."""
        id1 = generate_note_id()
        id2 = generate_note_id()
        assert id1 != id2, "Generated IDs should be unique"
    
    def test_generate_note_id_starts_with_note(self):
        """Test that all IDs start with 'note-'."""
        for _ in range(5):
            note_id = generate_note_id()
            assert note_id.startswith("note-"), f"ID should start with 'note-': {note_id}"


class TestPixelConversions:
    """Test pixel to various timing unit conversions."""
    
    def test_pixels_to_flicks(self):
        """Test pixels to flicks conversion."""
        # 80 pixels at 120 BPM should be 1 beat
        # 1 beat = 60/120 = 0.5 seconds
        # 0.5 seconds = 0.5 * 705600000 = 352800000 flicks
        result = pixels_to_flicks(PIXELS_PER_BEAT, PIXELS_PER_BEAT, TEMPO)
        expected = 352800000.0  # 0.5 seconds in flicks
        assert abs(result - expected) < 1000, f"Expected ~{expected}, got {result}"
    
    def test_pixels_to_seconds(self):
        """Test pixels to seconds conversion."""
        # 160 pixels at 120 BPM with 80 pixels per beat = 2 beats = 1 second
        result = pixels_to_seconds(160, PIXELS_PER_BEAT, TEMPO)
        expected = 1.0
        assert abs(result - expected) < FLOAT_TOLERANCE
    
    def test_pixels_to_beats(self):
        """Test pixels to beats conversion."""
        result = pixels_to_beats(PIXELS_PER_BEAT, PIXELS_PER_BEAT)
        assert abs(result - 1.0) < FLOAT_TOLERANCE
        
        result = pixels_to_beats(160, PIXELS_PER_BEAT)
        assert abs(result - 2.0) < FLOAT_TOLERANCE
    
    def test_pixels_to_ticks(self):
        """Test pixels to MIDI ticks conversion."""
        # 80 pixels = 1 beat = 480 ticks (at 480 PPQN)
        result = pixels_to_ticks(PIXELS_PER_BEAT, PIXELS_PER_BEAT, PPQN)
        assert result == PPQN
        
        # 160 pixels = 2 beats = 960 ticks
        result = pixels_to_ticks(160, PIXELS_PER_BEAT, PPQN)
        assert result == PPQN * 2
    
    def test_pixels_to_samples(self):
        """Test pixels to audio samples conversion."""
        # 160 pixels at 120 BPM = 1 second = 44100 samples (at 44.1kHz)
        result = pixels_to_samples(160, PIXELS_PER_BEAT, TEMPO, SAMPLE_RATE)
        assert result == SAMPLE_RATE
    
    def test_pixels_to_samples_half_second(self):
        """Test half-second conversion to samples."""
        # 80 pixels at 120 BPM = 0.5 seconds = 22050 samples
        result = pixels_to_samples(PIXELS_PER_BEAT, PIXELS_PER_BEAT, TEMPO, SAMPLE_RATE)
        expected = SAMPLE_RATE // 2
        assert result == expected


class TestTimingCalculations:
    """Test comprehensive timing calculations."""
    
    def test_calculate_all_timing_data(self):
        """Test calculation of all timing representations."""
        pixels = 160  # 2 beats at default settings
        
        result = calculate_all_timing_data(
            pixels, PIXELS_PER_BEAT, TEMPO, SAMPLE_RATE, PPQN
        )
        
        # Check all keys present
        expected_keys = {'seconds', 'beats', 'flicks', 'ticks', 'samples'}
        assert set(result.keys()) == expected_keys
        
        # Check values
        assert abs(result['seconds'] - 1.0) < FLOAT_TOLERANCE  # 2 beats = 1 second
        assert abs(result['beats'] - 2.0) < FLOAT_TOLERANCE    # 160 pixels = 2 beats
        assert result['ticks'] == PPQN * 2                     # 2 beats = 960 ticks
        assert result['samples'] == SAMPLE_RATE                # 1 second = 44100 samples
    
    def test_calculate_all_timing_data_different_params(self):
        """Test timing calculations with different parameters."""
        pixels = 100
        pixels_per_beat = 50
        tempo = 90
        
        result = calculate_all_timing_data(
            pixels, pixels_per_beat, tempo, SAMPLE_RATE, PPQN
        )
        
        # 100 pixels / 50 pixels_per_beat = 2 beats
        assert abs(result['beats'] - 2.0) < FLOAT_TOLERANCE
        
        # 2 beats at 90 BPM = 2 * (60/90) = 1.333... seconds
        expected_seconds = 2 * 60 / 90
        assert abs(result['seconds'] - expected_seconds) < FLOAT_TOLERANCE


class TestNoteCreation:
    """Test note creation with timing data."""
    
    def test_create_note_with_timing(self):
        """Test creation of note with all timing data."""
        note_data = create_note_with_timing(
            note_id="test-note-1",
            start_pixels=80,
            duration_pixels=160,
            pitch=60,
            velocity=100,
            lyric="테스트",
            pixels_per_beat=PIXELS_PER_BEAT,
            tempo=TEMPO,
            sample_rate=SAMPLE_RATE,
            ppqn=PPQN
        )
        
        # Check basic fields
        assert note_data["id"] == "test-note-1"
        assert note_data["start"] == 80
        assert note_data["duration"] == 160
        assert note_data["pitch"] == 60
        assert note_data["velocity"] == 100
        assert note_data["lyric"] == "테스트"
        
        # Check timing calculations
        # Start: 80 pixels = 1 beat = 0.5 seconds
        assert abs(note_data["startSeconds"] - 0.5) < FLOAT_TOLERANCE
        assert abs(note_data["startBeats"] - 1.0) < FLOAT_TOLERANCE
        assert note_data["startTicks"] == PPQN
        assert note_data["startSample"] == SAMPLE_RATE // 2
        
        # Duration: 160 pixels = 2 beats = 1 second
        assert abs(note_data["durationSeconds"] - 1.0) < FLOAT_TOLERANCE
        assert abs(note_data["durationBeats"] - 2.0) < FLOAT_TOLERANCE
        assert note_data["durationTicks"] == PPQN * 2
        assert note_data["durationSamples"] == SAMPLE_RATE
        
        # End time: start + duration = 0.5 + 1.0 = 1.5 seconds
        assert abs(note_data["endSeconds"] - 1.5) < FLOAT_TOLERANCE
    
    def test_create_note_with_timing_zero_duration(self):
        """Test note creation with zero duration."""
        note_data = create_note_with_timing(
            note_id="zero-duration",
            start_pixels=100,
            duration_pixels=0,
            pitch=72,
            velocity=80,
            lyric="",
            pixels_per_beat=PIXELS_PER_BEAT,
            tempo=TEMPO
        )
        
        # Duration should be zero in all units
        assert note_data["durationSeconds"] == 0
        assert note_data["durationBeats"] == 0
        assert note_data["durationTicks"] == 0
        assert note_data["durationSamples"] == 0
        
        # End time should equal start time
        assert abs(note_data["endSeconds"] - note_data["startSeconds"]) < FLOAT_TOLERANCE
    
    def test_create_note_timing_consistency(self):
        """Test that all timing representations are consistent."""
        note_data = create_note_with_timing(
            note_id="consistency-test",
            start_pixels=240,  # 3 beats
            duration_pixels=80,  # 1 beat
            pitch=67,
            velocity=90,
            lyric="일관성",
            pixels_per_beat=PIXELS_PER_BEAT,
            tempo=TEMPO,
            sample_rate=SAMPLE_RATE,
            ppqn=PPQN
        )
        
        # Cross-verify timing calculations
        # Beats to seconds: beats * (60 / tempo)
        beats_to_seconds = note_data["startBeats"] * 60 / TEMPO
        assert abs(note_data["startSeconds"] - beats_to_seconds) < FLOAT_TOLERANCE
        
        # Ticks to beats: ticks / ppqn
        ticks_to_beats = note_data["startTicks"] / PPQN
        assert abs(note_data["startBeats"] - ticks_to_beats) < FLOAT_TOLERANCE
        
        # Samples to seconds: samples / sample_rate
        samples_to_seconds = note_data["startSample"] / SAMPLE_RATE
        assert abs(note_data["startSeconds"] - samples_to_seconds) < FLOAT_TOLERANCE


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_pixels(self):
        """Test conversion of zero pixel values."""
        assert pixels_to_seconds(0, PIXELS_PER_BEAT, TEMPO) == 0
        assert pixels_to_beats(0, PIXELS_PER_BEAT) == 0
        assert pixels_to_ticks(0, PIXELS_PER_BEAT, PPQN) == 0
        assert pixels_to_samples(0, PIXELS_PER_BEAT, TEMPO, SAMPLE_RATE) == 0
    
    def test_very_small_pixels(self):
        """Test conversion of very small pixel values."""
        small_pixels = 0.1
        
        result_seconds = pixels_to_seconds(small_pixels, PIXELS_PER_BEAT, TEMPO)
        assert result_seconds > 0
        assert result_seconds < 0.1  # Should be very small
        
        result_beats = pixels_to_beats(small_pixels, PIXELS_PER_BEAT)
        assert result_beats > 0
        assert result_beats < 0.1
    
    def test_large_pixel_values(self):
        """Test conversion of large pixel values."""
        large_pixels = 8000  # 100 beats
        
        result_seconds = pixels_to_seconds(large_pixels, PIXELS_PER_BEAT, TEMPO)
        expected_seconds = 100 * 60 / TEMPO  # 100 beats in seconds
        assert abs(result_seconds - expected_seconds) < FLOAT_TOLERANCE
        
        result_beats = pixels_to_beats(large_pixels, PIXELS_PER_BEAT)
        assert abs(result_beats - 100.0) < FLOAT_TOLERANCE 