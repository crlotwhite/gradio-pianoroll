"""
Tests for Note class.

This test suite covers the Note class functionality including automatic timing
calculations, data conversion, and manipulation methods.
"""

import pytest
from gradio_pianoroll import Note
from .conftest import FLOAT_TOLERANCE, TEMPO, PIXELS_PER_BEAT, SAMPLE_RATE, PPQN


class TestNoteCreation:
    """Test Note class creation and initialization."""
    
    def test_note_creation_basic(self, default_note_data):
        """Test basic note creation."""
        note = Note(**default_note_data)
        
        assert note.pitch == 60
        assert note.velocity == 100
        assert note.lyric == "테스트"
        assert note.start_pixels == 80.0
        assert note.duration_pixels == 160.0
        assert note.id is not None
        assert note.id.startswith("note-")
    
    def test_note_creation_with_id(self):
        """Test note creation with custom ID."""
        custom_id = "custom-note-123"
        note = Note(
            pitch=60, start_pixels=80, duration_pixels=160, id=custom_id
        )
        
        assert note.id == custom_id
    
    def test_note_creation_defaults(self):
        """Test note creation with minimal parameters."""
        note = Note(pitch=60)
        
        # Check defaults
        assert note.velocity == 100
        assert note.lyric == ""
        assert note.start_pixels == 0.0
        assert note.duration_pixels == 80.0
        assert note.pixels_per_beat == 80.0
        assert note.tempo == 120.0
        assert note.sample_rate == 44100
        assert note.ppqn == 480


class TestTimingProperties:
    """Test automatic timing calculations."""
    
    def test_timing_calculations_one_beat(self):
        """Test timing calculations for a one-beat note."""
        note = Note(
            pitch=60, start_pixels=80, duration_pixels=80,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=TEMPO,
            sample_rate=SAMPLE_RATE, ppqn=PPQN
        )
        
        # Start timing (1 beat = 0.5 seconds at 120 BPM)
        assert abs(note.start_beats - 1.0) < FLOAT_TOLERANCE
        assert abs(note.start_seconds - 0.5) < FLOAT_TOLERANCE
        assert note.start_ticks == PPQN
        assert note.start_samples == SAMPLE_RATE // 2
        
        # Duration timing (1 beat)
        assert abs(note.duration_beats - 1.0) < FLOAT_TOLERANCE
        assert abs(note.duration_seconds - 0.5) < FLOAT_TOLERANCE
        assert note.duration_ticks == PPQN
        assert note.duration_samples == SAMPLE_RATE // 2
        
        # End timing
        assert abs(note.end_seconds - 1.0) < FLOAT_TOLERANCE
    
    def test_timing_calculations_two_beats(self):
        """Test timing calculations for a two-beat note."""
        note = Note(
            pitch=64, start_pixels=0, duration_pixels=160,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=TEMPO
        )
        
        # Start at beginning
        assert abs(note.start_beats - 0.0) < FLOAT_TOLERANCE
        assert abs(note.start_seconds - 0.0) < FLOAT_TOLERANCE
        assert note.start_ticks == 0
        assert note.start_samples == 0
        
        # Duration (2 beats = 1 second at 120 BPM)
        assert abs(note.duration_beats - 2.0) < FLOAT_TOLERANCE
        assert abs(note.duration_seconds - 1.0) < FLOAT_TOLERANCE
        assert note.duration_ticks == PPQN * 2
        assert note.duration_samples == SAMPLE_RATE
    
    def test_timing_flicks_calculation(self):
        """Test flicks timing calculation."""
        note = Note(
            pitch=60, start_pixels=80, duration_pixels=80,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=TEMPO
        )
        
        # Flicks calculation: (pixels * 60 * 705600000) / (pixels_per_beat * tempo)
        expected_start_flicks = (80 * 60 * 705600000) / (80 * 120)
        expected_duration_flicks = (80 * 60 * 705600000) / (80 * 120)
        
        assert abs(note.start_flicks - expected_start_flicks) < 1000
        assert abs(note.duration_flicks - expected_duration_flicks) < 1000
    
    def test_timing_different_tempo(self):
        """Test timing calculations with different tempo."""
        note = Note(
            pitch=60, start_pixels=80, duration_pixels=80,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=60  # Half speed
        )
        
        # At 60 BPM, 1 beat = 1 second
        assert abs(note.start_seconds - 1.0) < FLOAT_TOLERANCE
        assert abs(note.duration_seconds - 1.0) < FLOAT_TOLERANCE
        assert abs(note.end_seconds - 2.0) < FLOAT_TOLERANCE


class TestNoteManipulation:
    """Test note manipulation methods."""
    
    def test_move_to(self):
        """Test moving note to new position."""
        note = Note(pitch=60, start_pixels=80, duration_pixels=80)
        original_duration = note.duration_seconds
        
        note.move_to(160)
        
        assert note.start_pixels == 160
        assert abs(note.duration_seconds - original_duration) < FLOAT_TOLERANCE
    
    def test_resize(self):
        """Test resizing note duration."""
        note = Note(pitch=60, start_pixels=80, duration_pixels=80)
        original_start = note.start_seconds
        
        note.resize(160)
        
        assert note.duration_pixels == 160
        assert abs(note.start_seconds - original_start) < FLOAT_TOLERANCE
        assert abs(note.duration_beats - 2.0) < FLOAT_TOLERANCE
    
    def test_transpose(self):
        """Test transposing note pitch."""
        note = Note(pitch=60)  # C4
        
        note.transpose(12)  # Up one octave
        assert note.pitch == 72  # C5
        
        note.transpose(-24)  # Down two octaves
        assert note.pitch == 48  # C3
    
    def test_transpose_clamping(self):
        """Test pitch clamping during transposition."""
        note = Note(pitch=127)  # Highest MIDI note
        
        note.transpose(10)  # Should clamp to 127
        assert note.pitch == 127
        
        note = Note(pitch=0)  # Lowest MIDI note
        note.transpose(-10)  # Should clamp to 0
        assert note.pitch == 0


class TestContextUpdate:
    """Test updating musical context."""
    
    def test_update_context(self):
        """Test updating musical context parameters."""
        note = Note(pitch=60, start_pixels=80, duration_pixels=80)
        
        original_seconds = note.start_seconds
        
        # Update tempo (should change timing)
        note.update_context(tempo=60)
        assert note.tempo == 60
        assert note.start_seconds != original_seconds
        
        # Update pixels per beat
        note.update_context(pixels_per_beat=40)
        assert note.pixels_per_beat == 40
        
        # Update sample rate
        note.update_context(sample_rate=22050)
        assert note.sample_rate == 22050
        
        # Update PPQN
        note.update_context(ppqn=960)
        assert note.ppqn == 960
    
    def test_partial_context_update(self):
        """Test updating only some context parameters."""
        note = Note(pitch=60, start_pixels=80, duration_pixels=80)
        
        original_tempo = note.tempo
        original_sample_rate = note.sample_rate
        
        # Update only pixels per beat
        note.update_context(pixels_per_beat=40)
        
        assert note.pixels_per_beat == 40
        assert note.tempo == original_tempo  # Should remain unchanged
        assert note.sample_rate == original_sample_rate  # Should remain unchanged


class TestDataConversion:
    """Test data conversion methods."""
    
    def test_to_dict(self):
        """Test converting note to dictionary."""
        note = Note(
            pitch=60, velocity=100, lyric="테스트",
            start_pixels=80, duration_pixels=160,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=TEMPO
        )
        
        data = note.to_dict()
        
        # Check required fields
        required_fields = [
            "id", "start", "duration", "pitch", "velocity", "lyric",
            "startFlicks", "durationFlicks", "startSeconds", "durationSeconds",
            "endSeconds", "startBeats", "durationBeats", "startTicks",
            "durationTicks", "startSample", "durationSamples"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Check basic values
        assert data["pitch"] == 60
        assert data["velocity"] == 100
        assert data["lyric"] == "테스트"
        assert data["start"] == 80
        assert data["duration"] == 160
    
    def test_from_dict(self):
        """Test creating note from dictionary."""
        note_data = {
            "id": "test-note-from-dict",
            "start": 120,
            "duration": 80,
            "pitch": 67,
            "velocity": 90,
            "lyric": "딕셔너리"
        }
        
        note = Note.from_dict(
            note_data, 
            pixels_per_beat=PIXELS_PER_BEAT,
            tempo=TEMPO,
            sample_rate=SAMPLE_RATE,
            ppqn=PPQN
        )
        
        assert note.id == "test-note-from-dict"
        assert note.start_pixels == 120
        assert note.duration_pixels == 80
        assert note.pitch == 67
        assert note.velocity == 90
        assert note.lyric == "딕셔너리"
        assert note.pixels_per_beat == PIXELS_PER_BEAT
        assert note.tempo == TEMPO
    
    def test_from_dict_defaults(self):
        """Test creating note from dictionary with missing optional fields."""
        minimal_data = {
            "start": 80,
            "duration": 160,
            "pitch": 60
        }
        
        note = Note.from_dict(minimal_data)
        
        assert note.velocity == 100  # Default
        assert note.lyric == ""      # Default
        assert note.id is not None   # Should be generated
    
    def test_round_trip_conversion(self):
        """Test that dict conversion is reversible."""
        original_note = Note(
            pitch=64, velocity=85, lyric="원본",
            start_pixels=240, duration_pixels=120,
            pixels_per_beat=PIXELS_PER_BEAT, tempo=TEMPO
        )
        
        # Convert to dict and back
        note_dict = original_note.to_dict()
        restored_note = Note.from_dict(
            note_dict,
            pixels_per_beat=PIXELS_PER_BEAT,
            tempo=TEMPO,
            sample_rate=SAMPLE_RATE,
            ppqn=PPQN
        )
        
        # Check that all values match
        assert restored_note.pitch == original_note.pitch
        assert restored_note.velocity == original_note.velocity
        assert restored_note.lyric == original_note.lyric
        assert restored_note.start_pixels == original_note.start_pixels
        assert restored_note.duration_pixels == original_note.duration_pixels
        
        # Check timing calculations match
        assert abs(restored_note.start_seconds - original_note.start_seconds) < FLOAT_TOLERANCE
        assert abs(restored_note.duration_seconds - original_note.duration_seconds) < FLOAT_TOLERANCE


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_duration_note(self):
        """Test note with zero duration."""
        note = Note(pitch=60, start_pixels=80, duration_pixels=0)
        
        assert note.duration_seconds == 0
        assert note.duration_beats == 0
        assert note.duration_ticks == 0
        assert note.duration_samples == 0
        assert note.end_seconds == note.start_seconds
    
    def test_extreme_pitch_values(self):
        """Test notes with extreme pitch values."""
        # Minimum MIDI pitch
        note_low = Note(pitch=0)
        assert note_low.pitch == 0
        
        # Maximum MIDI pitch
        note_high = Note(pitch=127)
        assert note_high.pitch == 127
    
    def test_extreme_velocity_values(self):
        """Test notes with extreme velocity values."""
        # Minimum velocity
        note_quiet = Note(pitch=60, velocity=0)
        assert note_quiet.velocity == 0
        
        # Maximum velocity
        note_loud = Note(pitch=60, velocity=127)
        assert note_loud.velocity == 127
    
    def test_very_long_note(self):
        """Test note with very long duration."""
        note = Note(pitch=60, start_pixels=0, duration_pixels=8000)  # 100 beats
        
        expected_duration_beats = 100
        expected_duration_seconds = 100 * 60 / TEMPO  # 50 seconds at 120 BPM
        
        assert abs(note.duration_beats - expected_duration_beats) < FLOAT_TOLERANCE
        assert abs(note.duration_seconds - expected_duration_seconds) < FLOAT_TOLERANCE 