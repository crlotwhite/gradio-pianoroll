"""
Integration tests for the PianoRoll component.

This test suite covers end-to-end workflows, component integration,
and the clean API demonstrated in the demo files.
"""

import pytest
import numpy as np
from gradio_pianoroll import (
    PianoRoll, PianoRollBackendData, Note,
    create_pitch_curve_data, audio_array_to_base64_wav,
    hz_to_pixels, time_to_pixels
)
from .conftest import FLOAT_TOLERANCE, TEMPO, PIXELS_PER_BEAT, SAMPLE_RATE, PPQN


class TestCleanApiWorkflow:
    """Test the clean API workflow from the demo."""
    
    def test_basic_clean_api_setup(self):
        """Test basic clean API setup as shown in clean_api_example.py."""
        # 1. Create backend data object
        backend_data = PianoRollBackendData()
        
        # 2. Create sample audio
        sample_rate = 44100
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Simple melody: A4, C5, E5
        frequencies = [440, 523.25, 659.25]
        audio = np.zeros_like(t)
        
        for i, freq in enumerate(frequencies):
            start = i * len(t) // 3
            end = (i + 1) * len(t) // 3
            audio[start:end] = np.sin(2 * np.pi * freq * t[start:end]) * 0.3
        
        # 3. Add audio data
        sample_audio = audio_array_to_base64_wav(audio, sample_rate)
        backend_data.set_audio(sample_audio)
        
        # 4. Add pitch curve
        times = np.linspace(0, 3.0, 100)
        frequencies_curve = 440 + 50 * np.sin(2 * np.pi * 0.5 * times)  # Vibrato
        pitch_curve = create_pitch_curve_data(frequencies_curve, times)
        backend_data.add_curve("f0_curve", pitch_curve)
        
        # 5. Enable backend audio
        backend_data.enable_backend_audio(True)
        
        # 6. Create piano roll with clean initialization
        piano_roll = PianoRoll(
            backend_data=backend_data,
            width=1200,
            height=400
        )
        
        # Verify setup
        assert piano_roll.backend_data.has_data() is True
        assert piano_roll.backend_data.use_backend_audio is True
        assert "f0_curve" in piano_roll.backend_data.curve_data
        assert piano_roll.width == 1200
        assert piano_roll.height == 400
    
    def test_programmatic_note_addition(self):
        """Test adding notes programmatically."""
        piano_roll = PianoRoll()
        
        # Add notes using the new API
        note_id1 = piano_roll.add_note(
            pitch=60, start_pixels=80, duration_pixels=160, lyric="Clean"
        )
        note_id2 = piano_roll.add_note(
            pitch=64, start_pixels=320, duration_pixels=160, lyric="API"
        )
        
        # Verify notes were added
        assert len(piano_roll.value["notes"]) == 5  # 3 default + 2 new
        
        # Find the added notes
        added_notes = [note for note in piano_roll.value["notes"] 
                      if note["id"] in [note_id1, note_id2]]
        assert len(added_notes) == 2
        
        # Verify note properties
        note1 = next(note for note in added_notes if note["id"] == note_id1)
        assert note1["pitch"] == 60
        assert note1["start"] == 80
        assert note1["duration"] == 160
        assert note1["lyric"] == "Clean"
        
        note2 = next(note for note in added_notes if note["id"] == note_id2)
        assert note2["pitch"] == 64
        assert note2["start"] == 320
        assert note2["lyric"] == "API"


class TestAdvancedDataProcessing:
    """Test advanced data processing workflows."""
    
    def test_note_analysis_workflow(self):
        """Test analyzing notes using the Note class."""
        # Create piano roll with custom notes
        backend_data = PianoRollBackendData()
        piano_roll = PianoRoll(backend_data=backend_data)
        
        # Clear default notes and add custom ones
        piano_roll.value["notes"] = []
        
        # Add notes with different properties
        note_id1 = piano_roll.add_note(pitch=60, start_pixels=0, duration_pixels=80, velocity=100)
        note_id2 = piano_roll.add_note(pitch=64, start_pixels=80, duration_pixels=160, velocity=90)
        note_id3 = piano_roll.add_note(pitch=67, start_pixels=240, duration_pixels=80, velocity=110)
        
        # Extract notes for analysis
        notes = []
        for note_data in piano_roll.value["notes"]:
            note = Note.from_dict(
                note_data,
                pixels_per_beat=piano_roll.value.get("pixelsPerBeat", 80),
                tempo=piano_roll.value.get("tempo", 120)
            )
            notes.append(note)
        
        # Analyze the notes
        assert len(notes) == 3
        
        # Check pitch range
        pitches = [note.pitch for note in notes]
        assert min(pitches) == 60
        assert max(pitches) == 67
        
        # Check total duration
        total_duration = max(note.end_seconds for note in notes)
        # Note 3: starts at 240 pixels (3 beats = 1.5s) + 80 pixels (1 beat = 0.5s) = 2.0s
        assert abs(total_duration - 2.0) < FLOAT_TOLERANCE


class TestComplexWorkflows:
    """Test complex, real-world workflows."""
    
    def test_round_trip_data_preservation(self):
        """Test that data is preserved through multiple processing steps."""
        # Create complex initial data
        backend_data = PianoRollBackendData(
            audio_data="data:audio/wav;base64,test_data",
            curve_data={
                "pitch": {"data": [{"x": 0, "y": 1200}], "color": "#FF0000"},
                "loudness": {"data": [{"x": 0, "y": 800}], "color": "#00FF00"}
            },
            segment_data=[
                {"start": 0.0, "end": 1.0, "type": "phoneme", "value": "test"}
            ],
            use_backend_audio=True
        )
        
        # Create piano roll
        piano_roll = PianoRoll(backend_data=backend_data)
        
        # Add custom note
        note_id = piano_roll.add_note(pitch=72, start_pixels=120, duration_pixels=80, lyric="round_trip")
        
        # Process through postprocess (simulating frontend interaction)
        output1 = piano_roll.postprocess(piano_roll.value)
        
        # Verify all data is present
        assert output1["audio_data"] == "data:audio/wav;base64,test_data"
        assert len(output1["curve_data"]) == 2
        assert len(output1["segment_data"]) == 1
        assert output1["use_backend_audio"] is True 