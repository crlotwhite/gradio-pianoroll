"""
Tests for audio_utils module.

This test suite covers the audio utility functions that handle coordinate conversions,
curve generation, and audio processing for the piano roll component.
"""

import pytest
import numpy as np
import math

from gradio_pianoroll.audio_utils import (
    hz_to_midi, midi_to_y_pixels, hz_to_pixels,
    time_to_pixels, hz_and_time_to_pixels,
    create_pitch_curve_data, create_loudness_curve_data,
    audio_array_to_base64_wav, librosa_f0_to_pixels, librosa_rms_to_pixels
)
from .conftest import FLOAT_TOLERANCE


class TestHzConversion:
    """Test frequency to pixel coordinate conversion."""
    
    def test_hz_to_midi_a4(self):
        """Test A4 (440Hz) converts to MIDI 69."""
        result = hz_to_midi(440.0)
        assert abs(result - 69.0) < FLOAT_TOLERANCE
    
    def test_hz_to_midi_c4(self):
        """Test C4 (261.63Hz) converts to MIDI 60."""
        result = hz_to_midi(261.63)
        expected = 69 + 12 * math.log2(261.63 / 440.0)
        assert abs(result - expected) < FLOAT_TOLERANCE
        assert abs(result - 60.0) < 0.1  # Allow small tolerance for C4
    
    def test_hz_to_midi_array(self):
        """Test array input for Hz to MIDI conversion."""
        frequencies = np.array([440.0, 523.25])  # A4, C5
        result = hz_to_midi(frequencies)
        assert isinstance(result, np.ndarray)
        assert abs(result[0] - 69.0) < FLOAT_TOLERANCE
        assert abs(result[1] - 72.0) < 0.1  # C5 ≈ MIDI 72
    
    def test_hz_to_midi_list(self):
        """Test list input for Hz to MIDI conversion."""
        frequencies = [440.0, 523.25]  # A4, C5
        result = hz_to_midi(frequencies)
        assert isinstance(result, np.ndarray)
        assert len(result) == 2
    
    def test_hz_to_midi_invalid_values(self):
        """Test handling of zero and negative frequencies."""
        result = hz_to_midi([0, -100, 440])
        assert result[0] == 0  # Zero frequency
        assert result[1] == 0  # Negative frequency
        assert abs(result[2] - 69.0) < FLOAT_TOLERANCE  # Valid frequency
    
    def test_midi_to_y_pixels(self):
        """Test MIDI note to Y pixel conversion."""
        # MIDI 60 (C4) should be at a specific Y coordinate
        result = midi_to_y_pixels(60)
        expected = (128 - 1 - 60) * 20 + 10  # (127-60)*20 + 10 = 1350
        assert abs(result - expected) < FLOAT_TOLERANCE
    
    def test_hz_to_pixels_direct(self):
        """Test direct Hz to pixels conversion."""
        # Test A4 (440Hz)
        result = hz_to_pixels(440.0)
        midi_note = hz_to_midi(440.0)
        expected = midi_to_y_pixels(midi_note)
        assert abs(result - expected) < FLOAT_TOLERANCE


class TestTimeConversion:
    """Test time to pixel coordinate conversion."""
    
    def test_time_to_pixels_basic(self):
        """Test basic time to pixels conversion."""
        # 1 second at 120 BPM with 80 pixels per beat
        # 120 BPM = 2 beats per second
        # 1 second = 2 beats = 2 * 80 = 160 pixels
        result = time_to_pixels(1.0, tempo=120, pixels_per_beat=80)
        assert abs(result - 160.0) < FLOAT_TOLERANCE
    
    def test_time_to_pixels_array(self):
        """Test array input for time conversion."""
        times = np.array([0.5, 1.0, 1.5])
        result = time_to_pixels(times, tempo=120, pixels_per_beat=80)
        expected = np.array([80.0, 160.0, 240.0])
        np.testing.assert_allclose(result, expected, rtol=FLOAT_TOLERANCE)
    
    def test_time_to_pixels_different_tempo(self):
        """Test time conversion with different tempo."""
        result = time_to_pixels(1.0, tempo=60, pixels_per_beat=80)
        # 60 BPM = 1 beat per second = 80 pixels
        assert abs(result - 80.0) < FLOAT_TOLERANCE
    
    def test_hz_and_time_to_pixels(self, sample_frequencies, sample_times):
        """Test combined frequency and time conversion."""
        x_pixels, y_pixels = hz_and_time_to_pixels(
            sample_frequencies, sample_times,
            tempo=120, pixels_per_beat=80
        )
        
        # Check array shapes match
        assert x_pixels.shape == y_pixels.shape
        assert len(x_pixels) == len(sample_frequencies)
        
        # Check X coordinates (time)
        expected_x = time_to_pixels(sample_times, tempo=120, pixels_per_beat=80)
        np.testing.assert_allclose(x_pixels, expected_x, rtol=FLOAT_TOLERANCE)
        
        # Check Y coordinates (frequency)
        expected_y = hz_to_pixels(sample_frequencies)
        np.testing.assert_allclose(y_pixels, expected_y, rtol=FLOAT_TOLERANCE)
    
    def test_hz_and_time_shape_mismatch(self):
        """Test error handling for mismatched array shapes."""
        with pytest.raises(ValueError, match="must have the same shape"):
            hz_and_time_to_pixels([440, 523], [1.0])


class TestCurveDataGeneration:
    """Test curve data generation for piano roll."""
    
    def test_create_pitch_curve_data(self, sample_frequencies, sample_times):
        """Test pitch curve data generation."""
        curve_data = create_pitch_curve_data(
            sample_frequencies, sample_times,
            tempo=120, pixels_per_beat=80
        )
        
        # Check structure
        assert isinstance(curve_data, dict)
        assert "data" in curve_data
        assert "color" in curve_data
        assert "dataType" in curve_data
        assert curve_data["dataType"] == "f0"
        
        # Check data points
        data_points = curve_data["data"]
        assert len(data_points) == len(sample_frequencies)
        
        # Check first data point
        first_point = data_points[0]
        assert "x" in first_point
        assert "y" in first_point
        
        # Verify coordinates match conversion functions
        expected_x = time_to_pixels(sample_times[0], tempo=120, pixels_per_beat=80)
        expected_y = hz_to_pixels(sample_frequencies[0])
        assert abs(first_point["x"] - expected_x) < FLOAT_TOLERANCE
        assert abs(first_point["y"] - expected_y) < FLOAT_TOLERANCE
    
    def test_create_pitch_curve_invalid_data(self):
        """Test pitch curve with invalid frequency data."""
        with pytest.raises(ValueError, match="No valid frequency data found"):
            create_pitch_curve_data([0, np.nan, -1], [0, 1, 2])
    
    def test_create_loudness_curve_data(self):
        """Test loudness curve data generation."""
        loudness_values = [0.1, 0.8, 0.3, 0.9]
        times = [0, 1, 2, 3]
        
        curve_data = create_loudness_curve_data(
            loudness_values, times,
            tempo=120, pixels_per_beat=80, use_db=False
        )
        
        # Check structure
        assert isinstance(curve_data, dict)
        assert "data" in curve_data
        assert "dataType" in curve_data
        assert curve_data["dataType"] == "loudness"
        assert curve_data["unit"] == "normalized"
        
        # Check data normalization
        data_points = curve_data["data"]
        assert len(data_points) == len(loudness_values)
    
    def test_create_loudness_curve_db_mode(self):
        """Test loudness curve in dB mode."""
        loudness_db = [-60, -20, -10, 0]  # dB values
        times = [0, 1, 2, 3]
        
        curve_data = create_loudness_curve_data(
            loudness_db, times, use_db=True, y_min=-60, y_max=0
        )
        
        assert curve_data["unit"] == "dB"
        assert curve_data["originalRange"]["y_min"] == -60
        assert curve_data["originalRange"]["y_max"] == 0
    
    def test_create_loudness_curve_shape_mismatch(self):
        """Test error handling for mismatched shapes."""
        with pytest.raises(ValueError, match="must have the same shape"):
            create_loudness_curve_data([0.1, 0.2], [1, 2, 3])


class TestAudioProcessing:
    """Test audio array processing functions."""
    
    def test_audio_array_to_base64_wav(self, sample_audio):
        """Test conversion of audio array to base64 WAV."""
        result = audio_array_to_base64_wav(sample_audio, sample_rate=44100)
        
        # Check format
        assert isinstance(result, str)
        assert result.startswith("data:audio/wav;base64,")
        
        # Check base64 content exists
        base64_part = result.split(",")[1]
        assert len(base64_part) > 0
    
    def test_audio_array_normalization(self):
        """Test audio normalization during conversion."""
        # Create audio that would clip (values > 1.0)
        loud_audio = np.array([0.5, 1.5, -2.0, 0.8])  # Contains clipping values
        
        result = audio_array_to_base64_wav(loud_audio, normalize=True)
        assert isinstance(result, str)
        assert result.startswith("data:audio/wav;base64,")
    
    def test_audio_array_no_normalization(self):
        """Test audio without normalization."""
        audio = np.array([0.1, 0.2, -0.3, 0.4])
        
        result = audio_array_to_base64_wav(audio, normalize=False)
        assert isinstance(result, str)
        assert result.startswith("data:audio/wav;base64,")


@pytest.mark.skipif(
    not pytest.importorskip("librosa", reason="librosa not available"),
    reason="librosa required for these tests"
)
class TestLibrosaIntegration:
    """Test librosa integration functions."""
    
    def test_librosa_f0_to_pixels(self):
        """Test F0 extraction results conversion."""
        # Mock F0 data from librosa
        f0_values = np.array([440.0, np.nan, 523.25, 0, 659.25])
        
        x_pixels, y_pixels = librosa_f0_to_pixels(
            f0_values, sr=22050, hop_length=512
        )
        
        # Should filter out NaN and zero values
        assert len(x_pixels) == 3  # Only valid values
        assert len(y_pixels) == 3
        
        # Check that coordinates are reasonable
        assert np.all(x_pixels >= 0)
        assert np.all(y_pixels >= 0)
    
    def test_librosa_rms_to_pixels(self):
        """Test RMS extraction results conversion."""
        # Mock RMS data
        rms_values = np.array([0.1, 0.5, 0.8, 0.2])
        
        x_pixels, y_pixels = librosa_rms_to_pixels(
            rms_values, sr=22050, hop_length=512, to_db=False
        )
        
        assert len(x_pixels) == len(rms_values)
        assert len(y_pixels) == len(rms_values)
        assert np.all(x_pixels >= 0)
        assert np.all(y_pixels >= 0)
    
    def test_librosa_rms_to_pixels_db_mode(self):
        """Test RMS conversion in dB mode."""
        rms_values = np.array([0.1, 0.5, 1.0, 0.2])
        
        x_pixels, y_pixels = librosa_rms_to_pixels(
            rms_values, sr=22050, hop_length=512, to_db=True
        )
        
        # In dB mode, should normalize from -60dB to 0dB
        assert len(x_pixels) == len(rms_values)
        assert len(y_pixels) == len(rms_values)
        
        # Y values should be in piano roll range
        assert np.all(y_pixels >= 0)
        assert np.all(y_pixels <= 2560)  # Piano roll height 