# 기본 사용법

이 가이드에서는 Gradio PianoRoll 컴포넌트의 기본적인 사용법을 설명합니다.

## 🚀 빠른 시작

### 1. 기본 설치 및 import

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.data_models import PianoRollData, Note  # TypedDict 지원
```

### 2. 가장 간단한 예제

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

with gr.Blocks() as demo:
    piano_roll = PianoRoll(height=400)

demo.launch()
```

### 3. 초기 데이터와 함께 사용

```python
# TypedDict 타입 힌트 사용 (선택사항)
from gradio_pianoroll.data_models import PianoRollData

# 초기 데이터 정의
initial_data: PianoRollData = {
    "notes": [
        {
            "id": "note_1",
            "start": 0,
            "duration": 160,
            "pitch": 60,  # C4
            "velocity": 100,
            "lyric": "안녕"
        },
        {
            "id": "note_2",
            "start": 160,
            "duration": 160,
            "pitch": 64,  # E4
            "velocity": 90,
            "lyric": "하세요"
        }
    ],
    "tempo": 120,
    "timeSignature": {"numerator": 4, "denominator": 4},
    "editMode": "select",
    "snapSetting": "1/4",
    "pixelsPerBeat": 80
}

with gr.Blocks() as demo:
    piano_roll = PianoRoll(value=initial_data, height=600)

demo.launch()
```

## 📊 데이터 구조 이해하기

### PianoRoll 데이터 형식 (TypedDict)

```python
from gradio_pianoroll.data_models import PianoRollData, Note, TimeSignature

# 전체 구조
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
```

### 개별 노트 구조

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
    startFlicks: Optional[float]
    # ... 기타 타이밍 필드들
```

## 🎯 이벤트 처리

### 기본 이벤트 리스너

```python
def handle_note_change(piano_roll_data):
    """노트 변경 시 호출되는 함수"""
    notes = piano_roll_data.get("notes", [])
    print(f"현재 노트 개수: {len(notes)}")

    # TypedDict 사용 시 IDE 자동완성 지원
    for note in notes:
        print(f"노트: pitch={note['pitch']}, lyric={note.get('lyric', '')}")

    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll()

    # 노트 변경 시 이벤트
    piano_roll.change(
        fn=handle_note_change,
        inputs=piano_roll,
        outputs=piano_roll
    )

demo.launch()
```

### 재생 이벤트

```python
def on_play(event_data):
    print("재생 시작!")
    return "재생 중..."

def on_pause(event_data):
    print("일시정지!")
    return "일시정지됨"

def on_stop(event_data):
    print("정지!")
    return "정지됨"

with gr.Blocks() as demo:
    piano_roll = PianoRoll()
    status = gr.Textbox(label="상태")

    # 재생 이벤트들
    piano_roll.play(on_play, outputs=status)
    piano_roll.pause(on_pause, outputs=status)
    piano_roll.stop(on_stop, outputs=status)

demo.launch()
```

## 🔧 데이터 유효성 검사

### 자동 유효성 검사

컴포넌트는 자동으로 데이터를 검사하고 문제가 있을 때 경고를 출력합니다:

```python
# 잘못된 데이터
bad_data = {
    "notes": [
        {"pitch": 999, "start": 0, "duration": 100}  # 잘못된 피치
    ],
    "tempo": -50  # 잘못된 템포
}

# 컴포넌트가 자동으로 검사하고 경고 출력
piano_roll = PianoRoll(value=bad_data)
# UserWarning: Initial piano roll value validation failed:
#   - Note 0: 'pitch' must be between 0 and 127
#   - 'tempo' must be a positive number
```

### 수동 검사

```python
from gradio_pianoroll.data_models import validate_piano_roll_data, clean_piano_roll_data

def safe_update_pianoroll(data):
    """안전한 피아노롤 업데이트"""
    # 1. 데이터 정리
    cleaned_data = clean_piano_roll_data(data)

    # 2. 유효성 검사
    errors = validate_piano_roll_data(cleaned_data)
    if errors:
        print("데이터 오류:")
        for error in errors:
            print(f"  - {error}")
        return None

    # 3. 안전한 데이터 반환
    return cleaned_data
```

## 🎵 연구자용 유틸리티 활용

### research 모듈 사용

```python
from gradio_pianoroll.utils import research

# 간단한 노트 생성
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]  # (pitch, start_sec, duration_sec)
data = research.from_notes(notes, tempo=120)

piano_roll = PianoRoll(value=data)
```

### 3줄로 데모 만들기

```python
from gradio_pianoroll.utils import research

notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
demo = research.quick_demo(notes, title="내 TTS 모델 결과")
demo.launch()
```

## 🔍 디버깅 팁

### 1. 데이터 구조 확인

```python
def debug_data(piano_roll_data):
    """데이터 구조 디버깅"""
    print("=== 피아노롤 데이터 구조 ===")
    print(f"템포: {piano_roll_data.get('tempo')}")
    print(f"노트 개수: {len(piano_roll_data.get('notes', []))}")

    for i, note in enumerate(piano_roll_data.get('notes', [])):
        print(f"노트 {i}: {note}")

    return piano_roll_data

piano_roll.change(debug_data, inputs=piano_roll, outputs=piano_roll)
```

### 2. TypedDict 타입 체크

```python
from gradio_pianoroll.data_models import PianoRollData
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 개발 시에만 타입 체크
    def type_safe_function(data: PianoRollData) -> PianoRollData:
        # IDE에서 자동완성과 타입 검사 지원
        notes = data["notes"]  # List[Note] 타입으로 추론
        tempo = data["tempo"]  # int 타입으로 추론
        return data
```

### 3. 일반적인 오류와 해결법

| 오류 | 원인 | 해결법 |
|------|------|---------|
| `KeyError: 'notes'` | 필수 필드 누락 | `clean_piano_roll_data()` 사용 |
| `TypeError: 'NoneType'` | None 데이터 전달 | 데이터 유효성 검사 추가 |
| `UserWarning: validation failed` | 잘못된 데이터 값 | 데이터 범위 확인 (pitch: 0-127, tempo > 0) |

## 📝 다음 단계

- [연구자용 유틸리티](utils-research.md) - 고급 헬퍼 함수들
- [음성 합성](synthesizer.md) - 오디오 생성 기능
- [오디오 분석](audio-analysis.md) - F0, 음량 분석
- [API 참조](../api/components.md) - 전체 API 문서