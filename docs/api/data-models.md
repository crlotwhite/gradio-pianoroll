# Data Models API 참조

`gradio_pianoroll.data_models` 모듈은 TypedDict 기반의 타입 안전한 데이터 구조와 유효성 검사 함수들을 제공합니다.

## 📋 TypedDict 클래스들

### PianoRollData

피아노롤의 전체 데이터 구조를 정의합니다.

```python
class PianoRollData(TypedDict, total=False):
    # 필수 필드들
    notes: List[Note]
    tempo: int
    timeSignature: TimeSignature
    editMode: str
    snapSetting: str

    # 선택적 필드들 (자동으로 기본값 설정됨)
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
```

**기본값들**:
- `tempo`: 120
- `timeSignature`: `{"numerator": 4, "denominator": 4}`
- `editMode`: `"select"`
- `snapSetting`: `"1/4"`
- `pixelsPerBeat`: 80.0
- `sampleRate`: 44100
- `ppqn`: 480

### Note

개별 노트의 데이터 구조를 정의합니다.

```python
class Note(TypedDict, total=False):
    # 필수 필드들
    id: str              # 자동 생성됨
    start: float         # 시작 위치 (픽셀)
    duration: float      # 지속 시간 (픽셀)
    pitch: int           # MIDI 노트 번호 (0-127)
    velocity: int        # 음량 (0-127)

    # 선택적 필드들
    lyric: Optional[str]     # 가사
    phoneme: Optional[str]   # 음성학 표기

    # 타이밍 필드들 (자동 계산됨)
    startSeconds: Optional[float]
    durationSeconds: Optional[float]
    endSeconds: Optional[float]
    startFlicks: Optional[float]
    durationFlicks: Optional[float]
    startBeats: Optional[float]
    durationBeats: Optional[float]
    startTicks: Optional[int]
    durationTicks: Optional[int]
    startSample: Optional[int]
    durationSamples: Optional[int]
```

**유효 범위**:
- `pitch`: 0-127 (MIDI 표준)
- `velocity`: 0-127 (MIDI 표준)
- `start`, `duration`: 양수

### TimeSignature

박자표 정보를 정의합니다.

```python
class TimeSignature(TypedDict):
    numerator: int      # 분자 (예: 4/4의 4)
    denominator: int    # 분모 (예: 4/4의 4)
```

**일반적인 값들**:
- 4/4 박자: `{"numerator": 4, "denominator": 4}`
- 3/4 박자: `{"numerator": 3, "denominator": 4}`
- 6/8 박자: `{"numerator": 6, "denominator": 8}`

### LineLayerConfig

곡선 레이어 설정을 정의합니다.

```python
class LineLayerConfig(TypedDict, total=False):
    visible: bool
    color: str
    lineWidth: float
    opacity: float
    renderMode: str     # "curve", "steps", "points"
    yAxisLabel: Optional[str]
    yAxisMin: Optional[float]
    yAxisMax: Optional[float]
```

## 🔧 유효성 검사 함수들

### validate_piano_roll_data()

피아노롤 데이터의 유효성을 검사합니다.

```python
def validate_piano_roll_data(data: Dict[str, Any]) -> List[str]:
    """
    피아노롤 데이터 유효성 검사

    Args:
        data: 검사할 데이터

    Returns:
        List[str]: 오류 메시지 리스트 (빈 리스트면 유효함)
    """
```

**예제**:
```python
from gradio_pianoroll.data_models import validate_piano_roll_data

# 데이터 검사
errors = validate_piano_roll_data(data)
if errors:
    print("유효성 검사 실패:")
    for error in errors:
        print(f"  - {error}")
else:
    print("데이터가 유효합니다!")
```

### validate_and_warn()

유효성 검사를 수행하고 문제가 있으면 경고를 출력합니다.

```python
def validate_and_warn(data: Dict[str, Any], context: str = "Piano roll data") -> Dict[str, Any]:
    """
    유효성 검사 + 경고 출력

    Args:
        data: 검사할 데이터
        context: 오류 발생 맥락 (경고 메시지에 포함)

    Returns:
        Dict: 입력 데이터 (수정되지 않음)
    """
```

**예제**:
```python
from gradio_pianoroll.data_models import validate_and_warn

# 자동 검사 및 경고
validated_data = validate_and_warn(user_input, "사용자 입력 데이터")
```

### clean_piano_roll_data()

피아노롤 데이터를 정리하고 기본값을 설정합니다.

```python
def clean_piano_roll_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    데이터 정리 및 기본값 설정

    Args:
        data: 원본 데이터

    Returns:
        Dict: 정리된 데이터 (기본값 추가, None 값 제거 등)
    """
```

**예제**:
```python
from gradio_pianoroll.data_models import clean_piano_roll_data

# 불완전한 데이터
raw_data = {
    "notes": [{"pitch": 60, "start": 0}],  # duration 누락
    "tempo": None,                         # None 값
    # timeSignature 누락
}

# 자동으로 기본값 설정
cleaned_data = clean_piano_roll_data(raw_data)
print(cleaned_data)
# {
#     "notes": [{"pitch": 60, "start": 0, "duration": 80.0, "velocity": 100, "id": "note_..."}],
#     "tempo": 120,
#     "timeSignature": {"numerator": 4, "denominator": 4},
#     "editMode": "select",
#     "snapSetting": "1/4",
#     "pixelsPerBeat": 80.0
# }
```

## 🎯 사용 패턴

### 타입 안전한 함수 작성

```python
from gradio_pianoroll.data_models import PianoRollData, Note
from typing import List

def analyze_melody(data: PianoRollData) -> Dict[str, float]:
    """타입 안전한 멜로디 분석 함수"""
    notes: List[Note] = data["notes"]

    # IDE에서 자동완성 지원
    pitches = [note["pitch"] for note in notes]

    return {
        "평균_피치": sum(pitches) / len(pitches) if pitches else 0,
        "음역": max(pitches) - min(pitches) if pitches else 0,
        "노트_개수": len(notes)
    }

# 사용
result = analyze_melody(piano_roll_data)
```

### 안전한 데이터 처리

```python
from gradio_pianoroll.data_models import validate_and_warn, clean_piano_roll_data

def safe_process_data(raw_data):
    """안전한 데이터 처리 파이프라인"""
    # 1. 데이터 정리
    cleaned = clean_piano_roll_data(raw_data)

    # 2. 유효성 검사 및 경고
    validated = validate_and_warn(cleaned, "프로세싱 데이터")

    # 3. 추가 처리
    return validated

# 사용
processed_data = safe_process_data(user_input)
piano_roll = PianoRoll(value=processed_data)
```

### TypedDict와 일반 dict 혼용

```python
# TypedDict 방식 (권장)
data: PianoRollData = {
    "notes": [{"pitch": 60, "start": 0, "duration": 160}],
    "tempo": 120
}

# 일반 dict 방식 (호환됨)
data = {
    "notes": [{"pitch": 60, "start": 0, "duration": 160}],
    "tempo": 120
}

# 둘 다 동일하게 작동
piano_roll = PianoRoll(value=data)
```

## 🚨 일반적인 오류와 해결법

| 오류 메시지 | 원인 | 해결법 |
|-------------|------|--------|
| `'pitch' must be between 0 and 127` | MIDI 범위 벗어남 | 피치값을 0-127로 조정 |
| `'tempo' must be a positive number` | 음수 또는 0 템포 | 양수 템포 설정 |
| `'notes' must be a list` | notes가 리스트가 아님 | 노트를 리스트로 감싸기 |
| `Missing required field 'pitch'` | 필수 필드 누락 | 모든 노트에 pitch 추가 |
| `'duration' must be positive` | 음수 또는 0 길이 | 양수 duration 설정 |

## 📝 타입 체크 설정

TypeScript처럼 타입 체크를 활용하려면:

```python
# mypy 설정 (.mypy.ini)
[mypy]
python_version = 3.10
strict = True

# 코드에서
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 개발 시에만 타입 체크
    def type_safe_function(data: PianoRollData) -> PianoRollData:
        return data
```

이제 IDE에서 완전한 자동완성과 타입 검사를 받을 수 있습니다! 🎉