"""
Tests for PianoRollBackendData class.

This test suite covers the backend data management functionality for
audio, curve, and segment data in the piano roll component.
"""

import pytest
from gradio_pianoroll import PianoRollBackendData


class TestBackendDataCreation:
    """Test PianoRollBackendData creation and initialization."""
    
    def test_empty_creation(self):
        """Test creating empty backend data."""
        backend_data = PianoRollBackendData()
        
        assert backend_data.audio_data is None
        assert backend_data.curve_data == {}
        assert backend_data.segment_data == []
        assert backend_data.use_backend_audio is False
    
    def test_creation_with_parameters(self):
        """Test creating backend data with initial parameters."""
        backend_data = PianoRollBackendData(
            audio_data="test-audio-data",
            curve_data={"test_curve": [1, 2, 3]},
            segment_data=[{"type": "phoneme", "value": "a"}],
            use_backend_audio=True
        )
        
        assert backend_data.audio_data == "test-audio-data"
        assert backend_data.curve_data == {"test_curve": [1, 2, 3]}
        assert backend_data.segment_data == [{"type": "phoneme", "value": "a"}]
        assert backend_data.use_backend_audio is True


class TestAudioDataManagement:
    """Test audio data management."""
    
    def test_set_audio(self, backend_data):
        """Test setting audio data."""
        audio_data = "data:audio/wav;base64,UklGRi4AAABXQVZFZm10..."
        
        backend_data.set_audio(audio_data)
        
        assert backend_data.audio_data == audio_data
    
    def test_set_audio_url(self, backend_data):
        """Test setting audio data with URL."""
        audio_url = "https://example.com/audio.wav"
        
        backend_data.set_audio(audio_url)
        
        assert backend_data.audio_data == audio_url
    
    def test_set_audio_overwrite(self, backend_data):
        """Test overwriting existing audio data."""
        backend_data.set_audio("first-audio")
        backend_data.set_audio("second-audio")
        
        assert backend_data.audio_data == "second-audio"


class TestCurveDataManagement:
    """Test curve data management."""
    
    def test_add_curve(self, backend_data):
        """Test adding curve data."""
        curve_data = {
            "data": [{"x": 0, "y": 100}, {"x": 10, "y": 200}],
            "color": "#FF0000",
            "dataType": "f0"
        }
        
        backend_data.add_curve("pitch_curve", curve_data)
        
        assert "pitch_curve" in backend_data.curve_data
        assert backend_data.curve_data["pitch_curve"] == curve_data
    
    def test_add_multiple_curves(self, backend_data):
        """Test adding multiple curve datasets."""
        f0_curve = {"dataType": "f0", "data": []}
        loudness_curve = {"dataType": "loudness", "data": []}
        
        backend_data.add_curve("f0", f0_curve)
        backend_data.add_curve("loudness", loudness_curve)
        
        assert len(backend_data.curve_data) == 2
        assert backend_data.curve_data["f0"] == f0_curve
        assert backend_data.curve_data["loudness"] == loudness_curve
    
    def test_update_curve(self, backend_data):
        """Test updating existing curve data."""
        original_curve = {"data": [1, 2, 3]}
        updated_curve = {"data": [4, 5, 6]}
        
        backend_data.add_curve("test_curve", original_curve)
        backend_data.add_curve("test_curve", updated_curve)  # Update
        
        assert backend_data.curve_data["test_curve"] == updated_curve
    
    def test_remove_curve(self, backend_data):
        """Test removing curve data."""
        backend_data.add_curve("removable", {"data": []})
        assert "removable" in backend_data.curve_data
        
        backend_data.remove_curve("removable")
        assert "removable" not in backend_data.curve_data
    
    def test_remove_nonexistent_curve(self, backend_data):
        """Test removing non-existent curve (should not error)."""
        backend_data.remove_curve("nonexistent")  # Should not raise error
        assert backend_data.curve_data == {}


class TestSegmentDataManagement:
    """Test segment data management."""
    
    def test_add_segment(self, backend_data):
        """Test adding segment data."""
        segment = {
            "start": 0.5,
            "end": 1.0,
            "type": "phoneme",
            "value": "a",
            "confidence": 0.95
        }
        
        backend_data.add_segment(segment)
        
        assert len(backend_data.segment_data) == 1
        assert backend_data.segment_data[0] == segment
    
    def test_add_multiple_segments(self, backend_data):
        """Test adding multiple segments."""
        segments = [
            {"start": 0.0, "end": 0.5, "type": "phoneme", "value": "h"},
            {"start": 0.5, "end": 1.0, "type": "phoneme", "value": "e"},
            {"start": 1.0, "end": 1.5, "type": "phoneme", "value": "l"},
            {"start": 1.5, "end": 2.0, "type": "phoneme", "value": "o"}
        ]
        
        for segment in segments:
            backend_data.add_segment(segment)
        
        assert len(backend_data.segment_data) == 4
        assert backend_data.segment_data == segments
    
    def test_clear_segments(self, backend_data):
        """Test clearing all segment data."""
        # Add some segments first
        backend_data.add_segment({"start": 0, "end": 1, "type": "test", "value": "1"})
        backend_data.add_segment({"start": 1, "end": 2, "type": "test", "value": "2"})
        
        assert len(backend_data.segment_data) == 2
        
        backend_data.clear_segments()
        
        assert len(backend_data.segment_data) == 0
        assert backend_data.segment_data == []


class TestBackendAudioControl:
    """Test backend audio engine control."""
    
    def test_enable_backend_audio(self, backend_data):
        """Test enabling backend audio."""
        assert backend_data.use_backend_audio is False
        
        backend_data.enable_backend_audio(True)
        
        assert backend_data.use_backend_audio is True
    
    def test_disable_backend_audio(self, backend_data):
        """Test disabling backend audio."""
        backend_data.enable_backend_audio(True)
        assert backend_data.use_backend_audio is True
        
        backend_data.enable_backend_audio(False)
        
        assert backend_data.use_backend_audio is False
    
    def test_enable_backend_audio_default(self, backend_data):
        """Test enabling backend audio with default parameter."""
        backend_data.enable_backend_audio()  # No parameter = True
        
        assert backend_data.use_backend_audio is True


class TestDataStatus:
    """Test data status checking."""
    
    def test_has_data_empty(self, backend_data):
        """Test has_data with empty backend data."""
        assert backend_data.has_data() is False
    
    def test_has_data_with_audio(self, backend_data):
        """Test has_data with audio data."""
        backend_data.set_audio("test-audio")
        
        assert backend_data.has_data() is True
    
    def test_has_data_with_curves(self, backend_data):
        """Test has_data with curve data."""
        backend_data.add_curve("test", {"data": []})
        
        assert backend_data.has_data() is True
    
    def test_has_data_with_segments(self, backend_data):
        """Test has_data with segment data."""
        backend_data.add_segment({"start": 0, "end": 1, "type": "test", "value": "test"})
        
        assert backend_data.has_data() is True
    
    def test_has_data_backend_audio_only(self, backend_data):
        """Test has_data with only backend audio flag (should be False)."""
        backend_data.enable_backend_audio(True)
        
        # Backend audio flag alone doesn't count as "data"
        assert backend_data.has_data() is False


class TestSerialization:
    """Test data serialization."""
    
    def test_to_dict_empty(self, backend_data):
        """Test converting empty backend data to dict."""
        data_dict = backend_data.to_dict()
        
        expected = {
            "audio_data": None,
            "curve_data": {},
            "segment_data": [],
            "use_backend_audio": False
        }
        
        assert data_dict == expected
    
    def test_to_dict_full(self):
        """Test converting full backend data to dict."""
        backend_data = PianoRollBackendData(
            audio_data="test-audio",
            curve_data={"f0": {"data": [1, 2, 3]}},
            segment_data=[{"start": 0, "end": 1, "type": "phoneme", "value": "a"}],
            use_backend_audio=True
        )
        
        data_dict = backend_data.to_dict()
        
        expected = {
            "audio_data": "test-audio",
            "curve_data": {"f0": {"data": [1, 2, 3]}},
            "segment_data": [{"start": 0, "end": 1, "type": "phoneme", "value": "a"}],
            "use_backend_audio": True
        }
        
        assert data_dict == expected
    
    def test_to_dict_preserves_structure(self, backend_data):
        """Test that to_dict preserves nested data structures."""
        complex_curve = {
            "data": [{"x": 0, "y": 100}, {"x": 10, "y": 200}],
            "color": "#FF0000",
            "metadata": {"created": "2024-01-01", "version": 1}
        }
        
        backend_data.add_curve("complex", complex_curve)
        data_dict = backend_data.to_dict()
        
        assert data_dict["curve_data"]["complex"] == complex_curve


class TestComplexOperations:
    """Test complex operations combining multiple features."""
    
    def test_full_workflow(self, backend_data, sample_audio):
        """Test a complete workflow with all data types."""
        # Set audio
        backend_data.set_audio("data:audio/wav;base64,test")
        
        # Add pitch curve
        pitch_curve = {
            "data": [{"x": 0, "y": 1290}, {"x": 80, "y": 1230}],
            "color": "#FF6B6B",
            "dataType": "f0"
        }
        backend_data.add_curve("pitch", pitch_curve)
        
        # Add loudness curve
        loudness_curve = {
            "data": [{"x": 0, "y": 500}, {"x": 80, "y": 800}],
            "color": "#4ECDC4",
            "dataType": "loudness"
        }
        backend_data.add_curve("loudness", loudness_curve)
        
        # Add segments
        phonemes = [
            {"start": 0.0, "end": 0.3, "type": "phoneme", "value": "h"},
            {"start": 0.3, "end": 0.6, "type": "phoneme", "value": "e"},
            {"start": 0.6, "end": 0.9, "type": "phoneme", "value": "l"},
            {"start": 0.9, "end": 1.2, "type": "phoneme", "value": "o"}
        ]
        for phoneme in phonemes:
            backend_data.add_segment(phoneme)
        
        # Enable backend audio
        backend_data.enable_backend_audio(True)
        
        # Verify everything is set
        assert backend_data.has_data() is True
        assert backend_data.audio_data == "data:audio/wav;base64,test"
        assert len(backend_data.curve_data) == 2
        assert len(backend_data.segment_data) == 4
        assert backend_data.use_backend_audio is True
        
        # Test serialization
        data_dict = backend_data.to_dict()
        assert all(key in data_dict for key in 
                  ["audio_data", "curve_data", "segment_data", "use_backend_audio"])
    
    def test_selective_data_management(self, backend_data):
        """Test managing different types of data independently."""
        # Add curves only
        backend_data.add_curve("f0", {"data": []})
        backend_data.add_curve("loudness", {"data": []})
        
        assert backend_data.has_data() is True
        assert backend_data.audio_data is None
        assert len(backend_data.segment_data) == 0
        
        # Remove one curve
        backend_data.remove_curve("f0")
        assert len(backend_data.curve_data) == 1
        assert "loudness" in backend_data.curve_data
        
        # Add audio later
        backend_data.set_audio("test-audio")
        assert backend_data.audio_data == "test-audio"
        
        # Clear segments (should not affect other data)
        backend_data.clear_segments()
        assert len(backend_data.segment_data) == 0
        assert backend_data.has_data() is True  # Still has curve and audio
    
    def test_data_replacement_workflow(self, backend_data):
        """Test replacing data in a typical workflow."""
        # Initial setup
        backend_data.set_audio("initial-audio")
        backend_data.add_curve("initial_curve", {"data": [1, 2, 3]})
        
        # Replace audio
        backend_data.set_audio("updated-audio")
        assert backend_data.audio_data == "updated-audio"
        
        # Replace curve
        backend_data.add_curve("initial_curve", {"data": [4, 5, 6]})
        assert backend_data.curve_data["initial_curve"]["data"] == [4, 5, 6]
        
        # Add new curve alongside existing
        backend_data.add_curve("additional_curve", {"data": [7, 8, 9]})
 