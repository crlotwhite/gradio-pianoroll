"""
Unit tests for data_models module.

Tests cover:
- NoteData: Dataclass creation and serialization
- TimeSignatureData: Dataclass creation and serialization
- PianoRollData: Dataclass creation and serialization
- validate_note: Note validation
- validate_piano_roll_data: Full piano roll validation
- create_default_piano_roll_data: Default data creation
- ensure_note_ids: Auto-generation of note IDs
- clean_piano_roll_data: Data cleaning and defaults
"""

import pytest
from gradio_pianoroll.data_models import (
    # Primary dataclasses
    NoteData,
    TimeSignatureData,
    LineDataPointData,
    LineLayerConfigData,
    PianoRollData,
    # TypedDict aliases
    NoteDict,
    TimeSignatureDict,
    PianoRollDataDict,
    # Legacy aliases
    Note,
    TimeSignature,
    PianoRollDataClass,
    # Utility functions
    validate_note,
    validate_piano_roll_data,
    validate_and_warn,
    create_default_piano_roll_data,
    ensure_note_ids,
    clean_piano_roll_data,
)


# =============================================================================
# Tests for NoteData
# =============================================================================

class TestNoteData:
    """Tests for NoteData dataclass."""

    def test_create_minimal_note(self):
        """Test creating a note with only required fields."""
        note = NoteData(
            id="note-1",
            start=0.0,
            duration=100.0,
            pitch=60,
            velocity=100,
        )
        assert note.id == "note-1"
        assert note.start == 0.0
        assert note.duration == 100.0
        assert note.pitch == 60
        assert note.velocity == 100
        assert note.lyric is None
        assert note.phoneme is None

    def test_create_full_note(self):
        """Test creating a note with all fields."""
        note = NoteData(
            id="note-2",
            start=100.0,
            duration=50.0,
            pitch=72,
            velocity=80,
            startFlicks=1000.0,
            durationFlicks=500.0,
            startSeconds=0.5,
            durationSeconds=0.25,
            endSeconds=0.75,
            startBeats=1.0,
            durationBeats=0.5,
            startTicks=480,
            durationTicks=240,
            startSample=22050,
            durationSamples=11025,
            lyric="라",
            phoneme="la",
        )
        assert note.lyric == "라"
        assert note.phoneme == "la"
        assert note.startFlicks == 1000.0

    def test_from_dict(self):
        """Test creating NoteData from dictionary."""
        data = {
            "id": "note-3",
            "start": 200.0,
            "duration": 80.0,
            "pitch": 65,
            "velocity": 90,
            "lyric": "다",
        }
        note = NoteData.from_dict(data)
        assert note.id == "note-3"
        assert note.pitch == 65
        assert note.lyric == "다"

    def test_to_dict(self):
        """Test converting NoteData to dictionary."""
        note = NoteData(
            id="note-4",
            start=0.0,
            duration=100.0,
            pitch=60,
            velocity=100,
        )
        data = note.to_dict()
        assert isinstance(data, dict)
        assert data["id"] == "note-4"
        assert data["pitch"] == 60
        assert data["lyric"] is None


# =============================================================================
# Tests for TimeSignatureData
# =============================================================================

class TestTimeSignatureData:
    """Tests for TimeSignatureData dataclass."""

    def test_create_default(self):
        """Test creating 4/4 time signature."""
        ts = TimeSignatureData(numerator=4, denominator=4)
        assert ts.numerator == 4
        assert ts.denominator == 4

    def test_create_waltz(self):
        """Test creating 3/4 time signature."""
        ts = TimeSignatureData(numerator=3, denominator=4)
        assert ts.numerator == 3
        assert ts.denominator == 4

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {"numerator": 6, "denominator": 8}
        ts = TimeSignatureData.from_dict(data)
        assert ts.numerator == 6
        assert ts.denominator == 8

    def test_from_dict_defaults(self):
        """Test default values when fields are missing."""
        ts = TimeSignatureData.from_dict({})
        assert ts.numerator == 4
        assert ts.denominator == 4

    def test_to_dict(self):
        """Test converting to dictionary."""
        ts = TimeSignatureData(numerator=5, denominator=4)
        data = ts.to_dict()
        assert data == {"numerator": 5, "denominator": 4}


# =============================================================================
# Tests for PianoRollData
# =============================================================================

class TestPianoRollData:
    """Tests for PianoRollData dataclass."""

    def test_create_empty(self):
        """Test creating empty piano roll data."""
        pr = PianoRollData(
            notes=[],
            tempo=120,
            timeSignature=TimeSignatureData(4, 4),
            editMode="select",
            snapSetting="1/4",
        )
        assert pr.tempo == 120
        assert len(pr.notes) == 0
        assert pr.editMode == "select"

    def test_create_with_notes(self):
        """Test creating piano roll with notes."""
        notes = [
            NoteData(id="n1", start=0, duration=100, pitch=60, velocity=100),
            NoteData(id="n2", start=100, duration=100, pitch=62, velocity=90),
        ]
        pr = PianoRollData(
            notes=notes,
            tempo=140,
            timeSignature=TimeSignatureData(4, 4),
            editMode="draw",
            snapSetting="1/8",
        )
        assert len(pr.notes) == 2
        assert pr.notes[0].pitch == 60
        assert pr.tempo == 140

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "notes": [
                {"id": "n1", "start": 0, "duration": 100, "pitch": 60, "velocity": 100},
            ],
            "tempo": 100,
            "timeSignature": {"numerator": 3, "denominator": 4},
            "editMode": "erase",
            "snapSetting": "1/16",
        }
        pr = PianoRollData.from_dict(data)
        assert pr.tempo == 100
        assert len(pr.notes) == 1
        assert isinstance(pr.notes[0], NoteData)
        assert pr.timeSignature.numerator == 3

    def test_from_dict_defaults(self):
        """Test default values when fields are missing."""
        pr = PianoRollData.from_dict({})
        assert pr.tempo == 120
        assert pr.editMode == "select"
        assert pr.snapSetting == "1/4"

    def test_to_dict(self):
        """Test converting to dictionary."""
        pr = PianoRollData(
            notes=[NoteData(id="n1", start=0, duration=100, pitch=60, velocity=100)],
            tempo=120,
            timeSignature=TimeSignatureData(4, 4),
            editMode="select",
            snapSetting="1/4",
        )
        data = pr.to_dict()
        assert isinstance(data, dict)
        assert data["tempo"] == 120
        assert len(data["notes"]) == 1


# =============================================================================
# Tests for Legacy Aliases
# =============================================================================

class TestLegacyAliases:
    """Tests for backwards compatibility aliases."""

    def test_piano_roll_data_class_alias(self):
        """Test that PianoRollDataClass is same as PianoRollData."""
        assert PianoRollDataClass is PianoRollData

    def test_note_is_note_dict(self):
        """Test that Note is alias for NoteDict."""
        assert Note is NoteDict

    def test_time_signature_is_dict(self):
        """Test that TimeSignature is alias for TimeSignatureDict."""
        assert TimeSignature is TimeSignatureDict


# =============================================================================
# Tests for validate_note
# =============================================================================

class TestValidateNote:
    """Tests for validate_note function."""

    def test_valid_note(self):
        """Test validation of valid note."""
        note = {
            "id": "n1",
            "start": 0,
            "duration": 100,
            "pitch": 60,
            "velocity": 100,
        }
        errors = validate_note(note)
        assert len(errors) == 0

    def test_valid_note_dataclass(self):
        """Test validation of valid NoteData."""
        note = NoteData(id="n1", start=0, duration=100, pitch=60, velocity=100)
        errors = validate_note(note)
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        note = {"start": 0}
        errors = validate_note(note)
        assert "Required field 'id' is missing" in errors
        assert "Required field 'duration' is missing" in errors
        assert "Required field 'pitch' is missing" in errors
        assert "Required field 'velocity' is missing" in errors

    def test_invalid_pitch_range(self):
        """Test validation of invalid pitch range."""
        note = {
            "id": "n1",
            "start": 0,
            "duration": 100,
            "pitch": 128,  # Invalid: max is 127
            "velocity": 100,
        }
        errors = validate_note(note)
        assert any("pitch" in e and "between 0 and 127" in e for e in errors)

    def test_invalid_velocity_range(self):
        """Test validation of invalid velocity range."""
        note = {
            "id": "n1",
            "start": 0,
            "duration": 100,
            "pitch": 60,
            "velocity": -1,  # Invalid: min is 0
        }
        errors = validate_note(note)
        assert any("velocity" in e and "between 0 and 127" in e for e in errors)

    def test_negative_start(self):
        """Test validation of negative start time."""
        note = {
            "id": "n1",
            "start": -10,
            "duration": 100,
            "pitch": 60,
            "velocity": 100,
        }
        errors = validate_note(note)
        assert any("start" in e and "non-negative" in e for e in errors)

    def test_zero_duration(self):
        """Test validation of zero duration."""
        note = {
            "id": "n1",
            "start": 0,
            "duration": 0,
            "pitch": 60,
            "velocity": 100,
        }
        errors = validate_note(note)
        assert any("duration" in e and "positive" in e for e in errors)


# =============================================================================
# Tests for validate_piano_roll_data
# =============================================================================

class TestValidatePianoRollData:
    """Tests for validate_piano_roll_data function."""

    def test_valid_data(self):
        """Test validation of valid piano roll data."""
        data = {
            "notes": [
                {"id": "n1", "start": 0, "duration": 100, "pitch": 60, "velocity": 100},
            ],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
        }
        errors = validate_piano_roll_data(data)
        assert len(errors) == 0

    def test_valid_dataclass(self):
        """Test validation of valid PianoRollData."""
        pr = PianoRollData(
            notes=[NoteData(id="n1", start=0, duration=100, pitch=60, velocity=100)],
            tempo=120,
            timeSignature=TimeSignatureData(4, 4),
            editMode="select",
            snapSetting="1/4",
        )
        errors = validate_piano_roll_data(pr)
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        data = {"tempo": 120}
        errors = validate_piano_roll_data(data)
        assert any("notes" in e for e in errors)
        assert any("timeSignature" in e for e in errors)
        assert any("editMode" in e for e in errors)
        assert any("snapSetting" in e for e in errors)

    def test_invalid_tempo(self):
        """Test validation of invalid tempo."""
        data = {
            "notes": [],
            "tempo": 0,  # Invalid
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
        }
        errors = validate_piano_roll_data(data)
        assert any("tempo" in e and "positive" in e for e in errors)

    def test_invalid_note_in_list(self):
        """Test validation of invalid note in notes list."""
        data = {
            "notes": [
                {"id": "n1", "start": 0, "duration": 100, "pitch": 60, "velocity": 100},
                {"id": "n2", "pitch": 200},  # Invalid pitch
            ],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
        }
        errors = validate_piano_roll_data(data)
        assert any("Note 1" in e for e in errors)


# =============================================================================
# Tests for create_default_piano_roll_data
# =============================================================================

class TestCreateDefaultPianoRollData:
    """Tests for create_default_piano_roll_data function."""

    def test_returns_piano_roll_data(self):
        """Test that function returns PianoRollData instance."""
        result = create_default_piano_roll_data()
        assert isinstance(result, PianoRollData)

    def test_default_values(self):
        """Test default values are correct."""
        result = create_default_piano_roll_data()
        assert result.tempo == 120
        assert result.editMode == "select"
        assert result.snapSetting == "1/4"
        assert result.pixelsPerBeat == 80
        assert result.sampleRate == 44100
        assert result.ppqn == 480
        assert len(result.notes) == 0

    def test_default_time_signature(self):
        """Test default time signature is 4/4."""
        result = create_default_piano_roll_data()
        assert result.timeSignature.numerator == 4
        assert result.timeSignature.denominator == 4


# =============================================================================
# Tests for ensure_note_ids
# =============================================================================

class TestEnsureNoteIds:
    """Tests for ensure_note_ids function."""

    def test_adds_missing_ids(self):
        """Test that missing IDs are generated."""
        data = {
            "notes": [
                {"start": 0, "duration": 100, "pitch": 60, "velocity": 100},
                {"start": 100, "duration": 100, "pitch": 62, "velocity": 90},
            ],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
        }
        result = ensure_note_ids(data)
        assert "id" in result["notes"][0]
        assert "id" in result["notes"][1]
        assert result["notes"][0]["id"] != result["notes"][1]["id"]

    def test_preserves_existing_ids(self):
        """Test that existing IDs are preserved."""
        data = {
            "notes": [
                {"id": "my-custom-id", "start": 0, "duration": 100, "pitch": 60, "velocity": 100},
            ],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
        }
        result = ensure_note_ids(data)
        assert result["notes"][0]["id"] == "my-custom-id"

    def test_works_with_dataclass(self):
        """Test that function works with PianoRollData."""
        note = NoteData(id="", start=0, duration=100, pitch=60, velocity=100)
        pr = PianoRollData(
            notes=[note],
            tempo=120,
            timeSignature=TimeSignatureData(4, 4),
            editMode="select",
            snapSetting="1/4",
        )
        result = ensure_note_ids(pr)
        assert result.notes[0].id != ""


# =============================================================================
# Tests for clean_piano_roll_data
# =============================================================================

class TestCleanPianoRollData:
    """Tests for clean_piano_roll_data function."""

    def test_returns_piano_roll_data(self):
        """Test that function returns PianoRollData instance."""
        data = {
            "notes": [],
            "tempo": 140,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "draw",
            "snapSetting": "1/8",
        }
        result = clean_piano_roll_data(data)
        assert isinstance(result, PianoRollData)

    def test_sets_defaults_for_missing_fields(self):
        """Test that missing fields get default values."""
        data = {"notes": []}
        result = clean_piano_roll_data(data)
        assert result.tempo == 120
        assert result.editMode == "select"
        assert result.pixelsPerBeat == 80

    def test_preserves_existing_values(self):
        """Test that existing values are preserved."""
        data = {
            "notes": [],
            "tempo": 180,
            "timeSignature": {"numerator": 3, "denominator": 4},
            "editMode": "erase",
            "snapSetting": "1/16",
        }
        result = clean_piano_roll_data(data)
        assert result.tempo == 180
        assert result.editMode == "erase"
        assert result.snapSetting == "1/16"

    def test_handles_empty_data(self):
        """Test handling of empty/None data."""
        result = clean_piano_roll_data({})
        assert isinstance(result, PianoRollData)
        assert result.tempo == 120

    def test_handles_none(self):
        """Test handling of None."""
        result = clean_piano_roll_data(None)
        assert isinstance(result, PianoRollData)


# =============================================================================
# Tests for LineDataPointData
# =============================================================================

class TestLineDataPointData:
    """Tests for LineDataPointData dataclass."""

    def test_create(self):
        """Test creating a data point."""
        point = LineDataPointData(x=100.0, y=0.5)
        assert point.x == 100.0
        assert point.y == 0.5

    def test_from_dict(self):
        """Test creating from dictionary."""
        point = LineDataPointData.from_dict({"x": 50.0, "y": 0.8})
        assert point.x == 50.0
        assert point.y == 0.8

    def test_to_dict(self):
        """Test converting to dictionary."""
        point = LineDataPointData(x=75.0, y=0.3)
        data = point.to_dict()
        assert data == {"x": 75.0, "y": 0.3}


# =============================================================================
# Tests for LineLayerConfigData
# =============================================================================

class TestLineLayerConfigData:
    """Tests for LineLayerConfigData dataclass."""

    def test_create_minimal(self):
        """Test creating with minimal required fields."""
        config = LineLayerConfigData(
            color="#FF0000",
            lineWidth=2.0,
            yMin=0.0,
            yMax=1.0,
        )
        assert config.color == "#FF0000"
        assert config.lineWidth == 2.0
        assert config.visible is None

    def test_from_dict_with_data(self):
        """Test creating from dictionary with data points."""
        data = {
            "color": "#00FF00",
            "lineWidth": 1.5,
            "yMin": -1.0,
            "yMax": 1.0,
            "data": [
                {"x": 0.0, "y": 0.0},
                {"x": 100.0, "y": 0.5},
            ],
        }
        config = LineLayerConfigData.from_dict(data)
        assert len(config.data) == 2
        assert isinstance(config.data[0], LineDataPointData)
        assert config.data[1].x == 100.0

    def test_to_dict(self):
        """Test converting to dictionary."""
        config = LineLayerConfigData(
            color="#0000FF",
            lineWidth=3.0,
            yMin=0.0,
            yMax=100.0,
            data=[LineDataPointData(x=50.0, y=50.0)],
        )
        data = config.to_dict()
        assert data["color"] == "#0000FF"
        assert len(data["data"]) == 1
