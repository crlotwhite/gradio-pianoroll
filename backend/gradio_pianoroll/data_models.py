"""
Piano Roll 데이터 모델과 유효성 검사 함수들

현재 dict 기반 구조를 유지하면서 타입 안전성과 유효성 검사를 개선합니다.
"""

from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any, Union
import warnings


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


def validate_note(note: Dict[str, Any]) -> List[str]:
    """
    노트 데이터 유효성 검사

    Args:
        note: 검사할 노트 데이터

    Returns:
        오류 메시지 리스트 (빈 리스트면 유효)
    """
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


def validate_piano_roll_data(data: Dict[str, Any]) -> List[str]:
    """
    피아노롤 데이터 전체 유효성 검사

    Args:
        data: 검사할 피아노롤 데이터

    Returns:
        오류 메시지 리스트 (빈 리스트면 유효)
    """
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
    data: Dict[str, Any], context: str = "Piano roll data"
) -> Dict[str, Any]:
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


def create_default_piano_roll_data() -> PianoRollData:
    """기본 피아노롤 데이터 생성"""
    return {
        "notes": [],
        "tempo": 120,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": 80,
        "sampleRate": 44100,
        "ppqn": 480,
    }


def ensure_note_ids(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    노트들에 ID가 없으면 자동 생성

    Args:
        data: 피아노롤 데이터

    Returns:
        ID가 보장된 데이터
    """
    if "notes" not in data:
        return data

    from .timing_utils import generate_note_id

    modified = False
    for note in data["notes"]:
        if "id" not in note or not note["id"]:
            note["id"] = generate_note_id()
            modified = True

    if modified:
        print(
            f"🔧 Auto-generated IDs for {sum(1 for note in data['notes'] if not note.get('id'))} notes"
        )

    return data


def clean_piano_roll_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    피아노롤 데이터 정리 (None 값 제거, 기본값 설정 등)

    Args:
        data: 정리할 데이터

    Returns:
        정리된 데이터
    """
    if not data:
        return create_default_piano_roll_data()

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

    return cleaned
