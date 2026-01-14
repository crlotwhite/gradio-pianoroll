"""
Piano Roll data models and validation functions.

This module provides both TypedDict (for JSON serialization type hints) and
dataclass (for internal processing) representations of piano roll data.

Recommended usage:
- Use dataclasses (NoteData, PianoRollData) for internal processing
- TypedDicts are kept for JSON schema documentation and backwards compatibility
"""

from __future__ import annotations

import logging
import warnings
import dataclasses
from typing import Any, Dict, List, Optional, TypedDict, Union

logger = logging.getLogger(__name__)

# ============================================================================
# TypedDict Definitions (for JSON serialization type hints)
# ============================================================================


class TimeSignatureDict(TypedDict):
    """Time signature JSON structure."""

    numerator: int
    denominator: int


class NoteDict(TypedDict, total=False):
    """
    Note JSON structure - total=False makes some fields optional.

    This TypedDict documents the expected JSON format for notes.
    For internal processing, use the NoteData dataclass instead.
    """

    # Required fields
    id: str
    start: float
    duration: float
    pitch: int
    velocity: int

    # Optional timing fields
    startFlicks: Optional[float]
    durationFlicks: Optional[float]
    startSeconds: Optional[float]
    durationSeconds: Optional[float]
    endSeconds: Optional[float]
    startBeats: Optional[float]
    durationBeats: Optional[float]
    startTicks: Optional[int]
    durationTicks: Optional[int]
    startSample: Optional[int]
    durationSamples: Optional[int]

    # Text fields
    lyric: Optional[str]
    phoneme: Optional[str]


class LineDataPointDict(TypedDict):
    """Line data point JSON structure."""

    x: float
    y: float


class LineLayerConfigDict(TypedDict, total=False):
    """Line layer configuration JSON structure."""

    color: str
    lineWidth: float
    yMin: float
    yMax: float
    position: Optional[str]
    renderMode: Optional[str]
    visible: Optional[bool]
    opacity: Optional[float]
    dataType: Optional[str]
    unit: Optional[str]
    originalRange: Optional[Dict[str, Any]]
    data: List[LineDataPointDict]


class PianoRollDataDict(TypedDict, total=False):
    """
    Piano roll complete data JSON structure.

    This TypedDict documents the expected JSON format.
    For internal processing, use the PianoRollData dataclass instead.
    """

    # Required fields
    notes: List[NoteDict]
    tempo: int
    timeSignature: TimeSignatureDict
    editMode: str
    snapSetting: str

    # Optional fields
    pixelsPerBeat: Optional[float]
    sampleRate: Optional[int]
    ppqn: Optional[int]

    # Backend data
    audio_data: Optional[str]
    curve_data: Optional[Dict[str, Any]]
    segment_data: Optional[List[Dict[str, Any]]]
    line_data: Optional[Dict[str, LineLayerConfigDict]]
    use_backend_audio: Optional[bool]

    # Waveform data
    waveform_data: Optional[List[Dict[str, float]]]


# Legacy aliases for backwards compatibility
TimeSignature = TimeSignatureDict
Note = NoteDict
LineDataPoint = LineDataPointDict
LineLayerConfig = LineLayerConfigDict

# ============================================================================
# Dataclass Definitions (for internal processing)
# ============================================================================


@dataclasses.dataclass
class TimeSignatureData:
    numerator: int
    denominator: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeSignatureData":
        return cls(
            numerator=data.get("numerator", 4),
            denominator=data.get("denominator", 4),
        )

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class NoteData:
    id: str
    start: float
    duration: float
    pitch: int
    velocity: int
    startFlicks: Optional[float] = None
    durationFlicks: Optional[float] = None
    startSeconds: Optional[float] = None
    durationSeconds: Optional[float] = None
    endSeconds: Optional[float] = None
    startBeats: Optional[float] = None
    durationBeats: Optional[float] = None
    startTicks: Optional[int] = None
    durationTicks: Optional[int] = None
    startSample: Optional[int] = None
    durationSamples: Optional[int] = None
    lyric: Optional[str] = None
    phoneme: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoteData":
        field_names = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: data.get(k) for k in field_names}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class LineDataPointData:
    x: float
    y: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineDataPointData":
        return cls(x=data.get("x", 0.0), y=data.get("y", 0.0))

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class LineLayerConfigData:
    color: str
    lineWidth: float
    yMin: float
    yMax: float
    position: Optional[str] = None
    renderMode: Optional[str] = None
    visible: Optional[bool] = None
    opacity: Optional[float] = None
    dataType: Optional[str] = None
    unit: Optional[str] = None
    originalRange: Optional[Dict[str, Any]] = None
    data: List[LineDataPointData] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineLayerConfigData":
        points = [LineDataPointData.from_dict(p) for p in data.get("data", [])]
        field_names = {f.name for f in dataclasses.fields(cls) if f.name != "data"}
        filtered = {k: data.get(k) for k in field_names}
        return cls(data=points, **filtered)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class PianoRollData:
    """
    Primary dataclass for piano roll data processing.

    Use this class for internal data manipulation. For JSON serialization,
    call to_dict() to convert to a dictionary.
    """

    notes: List[NoteData]
    tempo: int
    timeSignature: TimeSignatureData
    editMode: str
    snapSetting: str
    pixelsPerBeat: Optional[float] = None
    sampleRate: Optional[int] = None
    ppqn: Optional[int] = None
    audio_data: Optional[str] = None
    curve_data: Optional[Dict[str, Any]] = None
    segment_data: Optional[List[Dict[str, Any]]] = None
    line_data: Optional[Dict[str, LineLayerConfigData]] = None
    use_backend_audio: Optional[bool] = None
    waveform_data: Optional[List[Dict[str, float]]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PianoRollData":
        """Create PianoRollData from a dictionary."""
        notes = [
            n if isinstance(n, NoteData) else NoteData.from_dict(n)
            for n in data.get("notes", [])
        ]
        ts_data = data.get("timeSignature", {})
        time_sig = (
            ts_data
            if isinstance(ts_data, TimeSignatureData)
            else TimeSignatureData.from_dict(ts_data)
        )
        line_data_src = data.get("line_data")
        if line_data_src is not None:
            line_data = {
                k: v if isinstance(v, LineLayerConfigData) else LineLayerConfigData.from_dict(v)
                for k, v in line_data_src.items()
            }
        else:
            line_data = None
        return cls(
            notes=notes,
            tempo=data.get("tempo", 120),
            timeSignature=time_sig,
            editMode=data.get("editMode", "select"),
            snapSetting=data.get("snapSetting", "1/4"),
            pixelsPerBeat=data.get("pixelsPerBeat"),
            sampleRate=data.get("sampleRate"),
            ppqn=data.get("ppqn"),
            audio_data=data.get("audio_data"),
            curve_data=data.get("curve_data"),
            segment_data=data.get("segment_data"),
            line_data=line_data,
            use_backend_audio=data.get("use_backend_audio"),
            waveform_data=data.get("waveform_data"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return dataclasses.asdict(self)


# Legacy alias for backwards compatibility
PianoRollDataClass = PianoRollData


# ============================================================================
# Validation Classes
# ============================================================================


@dataclasses.dataclass
class ValidationResult:
    """
    검증 결과를 담는 데이터 클래스.

    Attributes:
        is_valid: 검증 통과 여부
        errors: 오류 메시지 목록
        warnings: 경고 메시지 목록
    """

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    @classmethod
    def success(cls) -> "ValidationResult":
        """성공 결과를 반환합니다."""
        return cls(is_valid=True, errors=[], warnings=[])

    @classmethod
    def failure(cls, errors: List[str], warnings: Optional[List[str]] = None) -> "ValidationResult":
        """실패 결과를 반환합니다."""
        return cls(is_valid=False, errors=errors, warnings=warnings or [])

    def has_errors(self) -> bool:
        """오류가 있는지 확인합니다."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """경고가 있는지 확인합니다."""
        return len(self.warnings) > 0

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """다른 결과와 병합합니다."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
        )


class NoteValidator:
    """Note 데이터 검증기."""

    # 필수 필드 목록
    REQUIRED_FIELDS = ["id", "start", "duration", "pitch", "velocity"]

    @classmethod
    def to_dict(cls, note: Union[Dict[str, Any], NoteData]) -> Dict[str, Any]:
        """노트를 딕셔너리로 변환합니다."""
        if dataclasses.is_dataclass(note):
            return dataclasses.asdict(note)
        return dict(note)

    @classmethod
    def validate_required_fields(cls, note: Dict[str, Any]) -> List[str]:
        """필수 필드 유효성을 검증합니다."""
        errors = []
        for field in cls.REQUIRED_FIELDS:
            if field not in note:
                errors.append(f"Required field '{field}' is missing")
        return errors

    @classmethod
    def validate_types(cls, note: Dict[str, Any]) -> List[str]:
        """타입 유효성을 검증합니다."""
        errors = []

        if "start" in note and not isinstance(note["start"], (int, float)):
            errors.append("'start' must be a number")
        if "duration" in note and not isinstance(note["duration"], (int, float)):
            errors.append("'duration' must be a number")
        if "pitch" in note and not isinstance(note["pitch"], int):
            errors.append("'pitch' must be an integer")
        if "velocity" in note and not isinstance(note["velocity"], int):
            errors.append("'velocity' must be an integer")

        return errors

    @classmethod
    def validate_range(cls, note: Dict[str, Any]) -> List[str]:
        """범위 유효성을 검증합니다."""
        errors = []

        if "pitch" in note and not (0 <= note["pitch"] <= 127):
            errors.append("'pitch' must be between 0 and 127")
        if "velocity" in note and not (0 <= note["velocity"] <= 127):
            errors.append("'velocity' must be between 0 and 127")
        if "start" in note and note["start"] < 0:
            errors.append("'start' must be non-negative")
        if "duration" in note and note["duration"] <= 0:
            errors.append("'duration' must be positive")

        return errors

    @classmethod
    def validate(cls, note: Union[Dict[str, Any], NoteData]) -> ValidationResult:
        """
        노트 전체를 검증합니다.

        Args:
            note: 검증할 노트 데이터.

        Returns:
            ValidationResult: 검증 결과.
        """
        note_dict = cls.to_dict(note)

        all_errors = []
        all_errors.extend(cls.validate_required_fields(note_dict))
        all_errors.extend(cls.validate_types(note_dict))
        all_errors.extend(cls.validate_range(note_dict))

        return ValidationResult.failure(all_errors) if all_errors else ValidationResult.success()


class PianoRollValidator:
    """PianoRoll 데이터 검증기."""

    # 필수 필드 목록
    REQUIRED_FIELDS = ["notes", "tempo", "timeSignature", "editMode", "snapSetting"]

    @classmethod
    def to_dict(cls, data: Union[Dict[str, Any], PianoRollData]) -> Dict[str, Any]:
        """데이터를 딕셔너리로 변환합니다."""
        if dataclasses.is_dataclass(data):
            return dataclasses.asdict(data)
        return dict(data)

    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any]) -> List[str]:
        """필수 필드 유효성을 검증합니다."""
        errors = []
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Required field '{field}' is missing")
        return errors

    @classmethod
    def validate_notes(cls, data: Dict[str, Any]) -> List[str]:
        """노트 목록을 검증합니다."""
        errors = []

        if "notes" not in data:
            return errors

        if not isinstance(data["notes"], list):
            return ["'notes' must be a list"]

        for i, note in enumerate(data["notes"]):
            note_errors = NoteValidator.validate(note)
            for error in note_errors.errors:
                errors.append(f"Note {i}: {error}")

        return errors

    @classmethod
    def validate_tempo(cls, data: Dict[str, Any]) -> List[str]:
        """템포를 검증합니다."""
        if "tempo" in data:
            if not isinstance(data["tempo"], (int, float)) or data["tempo"] <= 0:
                return ["'tempo' must be a positive number"]
        return []

    @classmethod
    def validate_time_signature(cls, data: Dict[str, Any]) -> List[str]:
        """타임 시그니처를 검증합니다."""
        errors = []

        if "timeSignature" not in data:
            return errors

        ts = data["timeSignature"]
        if dataclasses.is_dataclass(ts):
            ts = dataclasses.asdict(ts)

        if not isinstance(ts, dict):
            return ["'timeSignature' must be a dictionary"]

        if (
            "numerator" not in ts
            or not isinstance(ts["numerator"], int)
            or ts["numerator"] <= 0
        ):
            errors.append("'timeSignature.numerator' must be a positive integer")
        if (
            "denominator" not in ts
            or not isinstance(ts["denominator"], int)
            or ts["denominator"] <= 0
        ):
            errors.append("'timeSignature.denominator' must be a positive integer")

        return errors

    @classmethod
    def validate(cls, data: Union[Dict[str, Any], PianoRollData]) -> ValidationResult:
        """
        피아노롤 전체 데이터를 검증합니다.

        Args:
            data: 검증할 피아노롤 데이터.

        Returns:
            ValidationResult: 검증 결과.
        """
        # 딕셔너리인지 확인
        data_dict = cls.to_dict(data)

        if not isinstance(data_dict, dict):
            return ValidationResult.failure(["Piano roll data must be a dictionary"])

        all_errors = []
        all_errors.extend(cls.validate_required_fields(data_dict))
        all_errors.extend(cls.validate_notes(data_dict))
        all_errors.extend(cls.validate_tempo(data_dict))
        all_errors.extend(cls.validate_time_signature(data_dict))

        return ValidationResult.failure(all_errors) if all_errors else ValidationResult.success()


def validate_note(note: Union[Dict[str, Any], NoteData]) -> List[str]:
    """
    Validate note data.

    Args:
        note: Note data to validate.

    Returns:
        List of error messages (empty list if valid).
    """
    result = NoteValidator.validate(note)
    return result.errors


def validate_piano_roll_data(data: Union[Dict[str, Any], PianoRollData]) -> List[str]:
    """
    Validate entire piano roll data.

    Args:
        data: Piano roll data to validate.

    Returns:
        List of error messages (empty list if valid).
    """
    result = PianoRollValidator.validate(data)
    return result.errors


def validate_and_warn(
    data: Union[Dict[str, Any], PianoRollData], context: str = "Piano roll data"
) -> Union[Dict[str, Any], PianoRollData]:
    """
    Validate data and output warnings.

    Args:
        data: Data to validate.
        context: Context information.

    Returns:
        Original data (if validation passes) or empty dict (if fails).
    """
    errors = validate_piano_roll_data(data)

    if errors:
        warning_msg = f"{context} validation failed:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        warnings.warn(warning_msg, UserWarning, stacklevel=2)
        return {}

    return data


def create_default_piano_roll_data() -> PianoRollData:
    """Create default piano roll data."""
    return PianoRollData(
        notes=[],
        tempo=120,
        timeSignature=TimeSignatureData(4, 4),
        editMode="select",
        snapSetting="1/4",
        pixelsPerBeat=80,
        sampleRate=44100,
        ppqn=480,
    )


def ensure_note_ids(data: Union[Dict[str, Any], PianoRollData]) -> Union[Dict[str, Any], PianoRollData]:
    """
    Auto-generate IDs for notes if missing.

    Args:
        data: Piano roll data.

    Returns:
        Data with guaranteed IDs.
    """
    notes = None
    if dataclasses.is_dataclass(data):
        notes = data.notes
    else:
        notes = data.get("notes") if isinstance(data, dict) else None

    if notes is None:
        return data

    from .timing_utils import generate_note_id

    missing_count = 0
    for note in notes:
        if dataclasses.is_dataclass(note):
            if not getattr(note, "id", None):
                note.id = generate_note_id()
                missing_count += 1
        else:
            if "id" not in note or not note["id"]:
                note["id"] = generate_note_id()
                missing_count += 1

    if missing_count:
        logger.debug("🔧 Auto-generated IDs for %d notes", missing_count)

    return data


def clean_piano_roll_data(data: Union[Dict[str, Any], PianoRollData]) -> PianoRollData:
    """
    Clean piano roll data (remove None values, set defaults, etc.).

    Args:
        data: Data to clean.

    Returns:
        Cleaned data.
    """
    if not data:
        return create_default_piano_roll_data()

    if dataclasses.is_dataclass(data):
        data = dataclasses.asdict(data)

    # Set default values
    cleaned = {
        "notes": data.get("notes", []),
        "tempo": data.get("tempo", 120),
        "timeSignature": data.get("timeSignature", {"numerator": 4, "denominator": 4}),
        "editMode": data.get("editMode", "select"),
        "snapSetting": data.get("snapSetting", "1/4"),
        "pixelsPerBeat": data.get("pixelsPerBeat", 80),
        "sampleRate": data.get("sampleRate", 44100),
        "ppqn": data.get("ppqn", 480),
    }

    # Optional fields (include only if not None)
    optional_fields = [
        "audio_data",
        "curve_data",
        "segment_data",
        "line_data",
        "use_backend_audio",
        "waveform_data",
    ]

    for field in optional_fields:
        if field in data and data[field] is not None:
            cleaned[field] = data[field]

    return PianoRollData.from_dict(cleaned)
