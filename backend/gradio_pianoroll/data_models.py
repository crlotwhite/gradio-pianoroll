"""
Piano Roll 데이터 모델과 유효성 검사 함수들

현재 dict 기반 구조를 유지하면서 타입 안전성과 유효성 검사를 개선합니다.
"""

from __future__ import annotations

import logging
import warnings
import dataclasses
from typing import Any, Dict, List, Optional, TypedDict, Union

logger = logging.getLogger(__name__)


class TimeSignature(TypedDict):
    """박자표 정보"""

    numerator: int
    denominator: int


class Note(TypedDict, total=False):
    """노트 정보 - total=False로 일부 필드 선택적"""

    # 필수 필드들
    id: str
    start: float
    duration: float
    pitch: int
    velocity: int

    # 선택적 타이밍 필드들
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

    # 텍스트 필드들
    lyric: Optional[str]
    phoneme: Optional[str]


class LineDataPoint(TypedDict):
    """라인 데이터 포인트"""

    x: float
    y: float


class LineLayerConfig(TypedDict, total=False):
    """라인 레이어 설정"""

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
    data: List[LineDataPoint]


class PianoRollData(TypedDict, total=False):
    """피아노롤 전체 데이터 구조"""

    # 필수 필드들
    notes: List[Note]
    tempo: int
    timeSignature: TimeSignature
    editMode: str
    snapSetting: str

    # 선택적 필드들
    pixelsPerBeat: Optional[float]
    sampleRate: Optional[int]
    ppqn: Optional[int]

    # 백엔드 데이터
    audio_data: Optional[str]
    curve_data: Optional[Dict[str, Any]]
    segment_data: Optional[List[Dict[str, Any]]]
    line_data: Optional[Dict[str, LineLayerConfig]]
    use_backend_audio: Optional[bool]

    # 파형 데이터
    waveform_data: Optional[List[Dict[str, float]]]


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
class PianoRollDataClass:
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
    def from_dict(cls, data: Dict[str, Any]) -> "PianoRollDataClass":
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
        return dataclasses.asdict(self)


def validate_note(note: Union[Dict[str, Any], NoteData]) -> List[str]:
    """
    노트 데이터 유효성 검사

    Args:
        note: 검사할 노트 데이터

    Returns:
        오류 메시지 리스트 (빈 리스트면 유효)
    """
    if dataclasses.is_dataclass(note):
        note = dataclasses.asdict(note)

    errors = []

    # 필수 필드 검사
    required_fields = ["id", "start", "duration", "pitch", "velocity"]
    for field in required_fields:
        if field not in note:
            errors.append(f"Required field '{field}' is missing")

    # 타입 검사
    if "start" in note and not isinstance(note["start"], (int, float)):
        errors.append("'start' must be a number")
    if "duration" in note and not isinstance(note["duration"], (int, float)):
        errors.append("'duration' must be a number")
    if "pitch" in note and not isinstance(note["pitch"], int):
        errors.append("'pitch' must be an integer")
    if "velocity" in note and not isinstance(note["velocity"], int):
        errors.append("'velocity' must be an integer")

    # 범위 검사
    if "pitch" in note and not (0 <= note["pitch"] <= 127):
        errors.append("'pitch' must be between 0 and 127")
    if "velocity" in note and not (0 <= note["velocity"] <= 127):
        errors.append("'velocity' must be between 0 and 127")
    if "start" in note and note["start"] < 0:
        errors.append("'start' must be non-negative")
    if "duration" in note and note["duration"] <= 0:
        errors.append("'duration' must be positive")

    return errors


def validate_piano_roll_data(data: Union[Dict[str, Any], PianoRollDataClass]) -> List[str]:
    """
    피아노롤 데이터 전체 유효성 검사

    Args:
        data: 검사할 피아노롤 데이터

    Returns:
        오류 메시지 리스트 (빈 리스트면 유효)
    """
    if dataclasses.is_dataclass(data):
        data = dataclasses.asdict(data)

    errors = []

    if not isinstance(data, dict):
        return ["Piano roll data must be a dictionary"]

    # 필수 필드 검사
    required_fields = ["notes", "tempo", "timeSignature", "editMode", "snapSetting"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Required field '{field}' is missing")

    # notes 검사
    if "notes" in data:
        if not isinstance(data["notes"], list):
            errors.append("'notes' must be a list")
        else:
            for i, note in enumerate(data["notes"]):
                note_errors = validate_note(note)
                for error in note_errors:
                    errors.append(f"Note {i}: {error}")

    # tempo 검사
    if "tempo" in data:
        if not isinstance(data["tempo"], (int, float)) or data["tempo"] <= 0:
            errors.append("'tempo' must be a positive number")

    # timeSignature 검사
    if "timeSignature" in data:
        ts = data["timeSignature"]
        if dataclasses.is_dataclass(ts):
            ts = dataclasses.asdict(ts)
        if not isinstance(ts, dict):
            errors.append("'timeSignature' must be a dictionary")
        else:
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


def validate_and_warn(
    data: Union[Dict[str, Any], PianoRollDataClass], context: str = "Piano roll data"
) -> Union[Dict[str, Any], PianoRollDataClass]:
    """
    데이터 유효성 검사하고 경고 출력

    Args:
        data: 검사할 데이터
        context: 컨텍스트 정보

    Returns:
        원본 데이터 (유효성 검사 통과 시) 또는 빈 dict (실패 시)
    """
    errors = validate_piano_roll_data(data)

    if errors:
        warning_msg = f"{context} validation failed:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        warnings.warn(warning_msg, UserWarning, stacklevel=2)
        return {}

    return data


def create_default_piano_roll_data() -> PianoRollDataClass:
    """기본 피아노롤 데이터 생성"""
    return PianoRollDataClass(
        notes=[],
        tempo=120,
        timeSignature=TimeSignatureData(4, 4),
        editMode="select",
        snapSetting="1/4",
        pixelsPerBeat=80,
        sampleRate=44100,
        ppqn=480,
    )


def ensure_note_ids(data: Union[Dict[str, Any], PianoRollDataClass]) -> Union[Dict[str, Any], PianoRollDataClass]:
    """
    노트들에 ID가 없으면 자동 생성

    Args:
        data: 피아노롤 데이터

    Returns:
        ID가 보장된 데이터
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
        logger.debug(
            "🔧 Auto-generated IDs for %d notes",
            sum(1 for note in data["notes"] if not note.get("id")),
        )

    return data


def clean_piano_roll_data(data: Union[Dict[str, Any], PianoRollDataClass]) -> PianoRollDataClass:
    """
    피아노롤 데이터 정리 (None 값 제거, 기본값 설정 등)

    Args:
        data: 정리할 데이터

    Returns:
        정리된 데이터
    """
    if not data:
        return create_default_piano_roll_data()

    if dataclasses.is_dataclass(data):
        data = dataclasses.asdict(data)

    # 기본값 설정
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

    # 선택적 필드들 (None이 아닌 경우만 포함)
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

    return PianoRollDataClass.from_dict(cleaned)
