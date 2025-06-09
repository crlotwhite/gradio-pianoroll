# API 레퍼런스

Gradio PianoRoll 컴포넌트의 완전한 API 문서입니다. 클래스, 메서드, 속성, 이벤트 등의 상세한 설명을 제공합니다.

## 🎹 PianoRoll 클래스

### 클래스 정의

```python
class PianoRoll(Component):
    """
    Gradio용 피아노롤 컴포넌트
    MIDI 노트 편집, 음성 합성, 오디오 분석 기능을 제공합니다.
    """
```

### 생성자 파라미터

#### `__init__(self, value=None, *, audio_data=None, curve_data=None, segment_data=None, use_backend_audio=False, ...)`

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `value` | `dict \| None` | `None` | 초기 피아노롤 데이터 |
| `audio_data` | `str \| None` | `None` | 백엔드 오디오 데이터 (base64 또는 URL) |
| `curve_data` | `dict \| None` | `None` | 선형 곡선 데이터 (F0, loudness 등) |
| `segment_data` | `list \| None` | `None` | 구간 데이터 (발음 타이밍 등) |
| `use_backend_audio` | `bool` | `False` | 백엔드 오디오 엔진 사용 여부 |
| `label` | `str \| I18nData \| None` | `None` | 컴포넌트 라벨 |
| `every` | `Timer \| float \| None` | `None` | 자동 업데이트 간격 |
| `inputs` | `Component \| Sequence[Component] \| set[Component] \| None` | `None` | 입력 컴포넌트들 |
| `show_label` | `bool \| None` | `None` | 라벨 표시 여부 |
| `scale` | `int \| None` | `None` | 상대적 크기 |
| `min_width` | `int` | `160` | 최소 너비 (픽셀) |
| `interactive` | `bool \| None` | `None` | 상호작용 가능 여부 |
| `visible` | `bool` | `True` | 가시성 |
| `elem_id` | `str \| None` | `None` | HTML DOM ID |
| `elem_classes` | `list[str] \| str \| None` | `None` | HTML DOM 클래스 |
| `render` | `bool` | `True` | 렌더링 여부 |
| `key` | `int \| str \| tuple[int \| str, ...] \| None` | `None` | 컴포넌트 키 |
| `preserved_by_key` | `list[str] \| str \| None` | `"value"` | 키로 보존할 속성들 |
| `width` | `int \| None` | `1000` | 컴포넌트 너비 (픽셀) |
| `height` | `int \| None` | `600` | 컴포넌트 높이 (픽셀) |

### 기본 메서드

#### `preprocess(self, payload)`

프론트엔드에서 전송된 데이터를 전처리합니다.

**파라미터:**
- `payload`: 프론트엔드에서 전송된 피아노롤 데이터

**반환값:**
- 전처리된 데이터 (사용자 함수로 전달)

#### `postprocess(self, value)`

백엔드에서 처리된 데이터를 후처리하여 프론트엔드로 전송합니다.

**파라미터:**
- `value`: 사용자 함수에서 반환된 피아노롤 데이터

**반환값:**
- 후처리된 데이터 (프론트엔드로 전송)

#### `example_payload(self)`

예제 입력 데이터를 반환합니다.

**반환값:**
- 기본 구조의 피아노롤 데이터

#### `example_value(self)`

예제 출력 데이터를 반환합니다.

**반환값:**
- 여러 노트가 포함된 피아노롤 데이터

#### `api_info(self)`

API 스키마 정보를 반환합니다.

**반환값:**
- JSON Schema 형태의 API 정보

### 백엔드 데이터 관리 메서드

#### `update_backend_data(self, audio_data=None, curve_data=None, segment_data=None, use_backend_audio=None)`

백엔드 데이터를 일괄 업데이트합니다.

**파라미터:**
- `audio_data` (optional): 새로운 오디오 데이터
- `curve_data` (optional): 새로운 곡선 데이터
- `segment_data` (optional): 새로운 구간 데이터
- `use_backend_audio` (optional): 백엔드 오디오 사용 여부

#### `set_audio_data(self, audio_data: str)`

오디오 데이터를 설정합니다.

**파라미터:**
- `audio_data`: base64 인코딩된 오디오 데이터 또는 URL

#### `set_curve_data(self, curve_data: dict)`

곡선 데이터를 설정합니다.

**파라미터:**
- `curve_data`: 곡선 데이터 딕셔너리

#### `set_segment_data(self, segment_data: list)`

구간 데이터를 설정합니다.

**파라미터:**
- `segment_data`: 구간 데이터 리스트

#### `enable_backend_audio(self, enable: bool = True)`

백엔드 오디오 사용을 설정합니다.

**파라미터:**
- `enable`: 백엔드 오디오 사용 여부

## 📊 데이터 구조

### PianoRoll Value 구조

```python
{
    "notes": [
        {
            "id": "note-1234567890-abcde",
            "start": 80.0,                    # 시작 위치 (픽셀)
            "duration": 160.0,                # 지속 시간 (픽셀)
            "startFlicks": 3528000000,        # 시작 위치 (플릭스)
            "durationFlicks": 7056000000,     # 지속 시간 (플릭스)
            "startSeconds": 1.0,              # 시작 시간 (초)
            "durationSeconds": 2.0,           # 지속 시간 (초)
            "endSeconds": 3.0,                # 종료 시간 (초)
            "startBeats": 1.0,                # 시작 박자
            "durationBeats": 2.0,             # 지속 박자
            "startTicks": 480,                # 시작 틱
            "durationTicks": 960,             # 지속 틱
            "startSample": 44100,             # 시작 샘플
            "durationSamples": 88200,         # 지속 샘플
            "pitch": 60,                      # MIDI 피치 (0-127)
            "velocity": 100,                  # MIDI 벨로시티 (0-127)
            "lyric": "안녕"                   # 가사 텍스트
        }
    ],
    "tempo": 120,                            # BPM 템포
    "timeSignature": {                       # 박자표
        "numerator": 4,
        "denominator": 4
    },
    "editMode": "select",                    # 편집 모드
    "snapSetting": "1/4",                    # 스냅 설정
    "pixelsPerBeat": 80,                     # 확대/축소 레벨
    "sampleRate": 44100,                     # 샘플레이트
    "ppqn": 480,                            # PPQN
    "audio_data": "data:audio/wav;base64,UklGRigAAABXQVZFZm10...",  # 백엔드 오디오
    "curve_data": {                          # 곡선 데이터
        "f0_curve": [...],
        "loudness_curve": [...],
        "voicing_curve": [...]
    },
    "segment_data": [                        # 구간 데이터
        {
            "start": 0.0,
            "end": 1.0,
            "type": "phoneme",
            "value": "ㅇ",
            "confidence": 0.95
        }
    ],
    "use_backend_audio": false               # 백엔드 오디오 사용 여부
}
```

### Note 객체 구조

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `id` | `string` | ✅ | 고유 식별자 |
| `start` | `number` | ✅ | 시작 위치 (픽셀) |
| `duration` | `number` | ✅ | 지속 시간 (픽셀) |
| `startFlicks` | `number` | ✅ | 시작 위치 (플릭스) |
| `durationFlicks` | `number` | ✅ | 지속 시간 (플릭스) |
| `startSeconds` | `number` | ✅ | 시작 시간 (초) |
| `durationSeconds` | `number` | ✅ | 지속 시간 (초) |
| `endSeconds` | `number` | ✅ | 종료 시간 (초) |
| `startBeats` | `number` | ✅ | 시작 박자 |
| `durationBeats` | `number` | ✅ | 지속 박자 |
| `startTicks` | `integer` | ✅ | 시작 틱 |
| `durationTicks` | `integer` | ✅ | 지속 틱 |
| `startSample` | `integer` | ✅ | 시작 샘플 |
| `durationSamples` | `integer` | ✅ | 지속 샘플 |
| `pitch` | `number` | ✅ | MIDI 피치 (0-127) |
| `velocity` | `number` | ✅ | MIDI 벨로시티 (0-127) |
| `lyric` | `string` | ❌ | 가사 텍스트 |

### Curve Data 구조

```python
{
    "f0_curve": {
        "type": "line",
        "points": [
            {"x": 0, "y": 300},
            {"x": 10, "y": 305},
            {"x": 20, "y": 298}
        ],
        "color": "#ff6b6b",
        "lineWidth": 2
    },
    "loudness_curve": {
        "type": "line", 
        "points": [
            {"x": 0, "y": 100},
            {"x": 10, "y": 120},
            {"x": 20, "y": 90}
        ],
        "color": "#4ecdc4",
        "lineWidth": 2
    },
    "voicing_curve": {
        "type": "segments",
        "segments": [
            {"start": 0, "end": 100, "value": 1, "color": "#95e1d3"},
            {"start": 100, "end": 200, "value": 0, "color": "#f38ba8"}
        ]
    }
}
```

### Segment Data 구조

```python
[
    {
        "start": 0.0,               # 구간 시작 시간 (초)
        "end": 0.5,                 # 구간 종료 시간 (초)
        "type": "phoneme",          # 구간 타입
        "value": "ㅇ",              # 구간 값/텍스트
        "confidence": 0.95          # 신뢰도 (0-1, 선택사항)
    },
    {
        "start": 0.5,
        "end": 1.0,
        "type": "phoneme",
        "value": "ㅏ",
        "confidence": 0.98
    }
]
```

## 🎵 이벤트

PianoRoll 컴포넌트는 다음 이벤트들을 지원합니다:

### `change`
노트 데이터가 변경될 때 발생

```python
piano_roll.change(
    fn=handle_change,
    inputs=[piano_roll],
    outputs=[output_component]
)
```

### `input`
사용자 입력이 있을 때 발생 (실시간)

```python
piano_roll.input(
    fn=handle_input,
    inputs=[piano_roll],
    outputs=[output_component]
)
```

### `play`
재생이 시작될 때 발생

```python
piano_roll.play(
    fn=handle_play,
    inputs=[piano_roll],
    outputs=[status_text]
)
```

### `pause`
재생이 일시정지될 때 발생

```python
piano_roll.pause(
    fn=handle_pause,
    inputs=[piano_roll],
    outputs=[status_text]
)
```

### `stop`
재생이 정지될 때 발생

```python
piano_roll.stop(
    fn=handle_stop,
    inputs=[piano_roll],
    outputs=[status_text]
)
```

### `clear`
모든 노트가 지워질 때 발생

```python
piano_roll.clear(
    fn=handle_clear,
    inputs=[piano_roll],
    outputs=[output_component]
)
```

## 🔧 유틸리티 함수

### 노트 ID 생성

#### `generate_note_id() -> str`

고유한 노트 ID를 생성합니다.

**반환값:**
- `"note-{timestamp}-{random_string}"` 형태의 문자열

**예제:**
```python
note_id = generate_note_id()
# "note-1672531200000-a1b2c"
```

### 시간 변환 함수들

#### `pixels_to_flicks(pixels: float, pixels_per_beat: float, tempo: float) -> float`

픽셀을 플릭스로 변환합니다.

**파라미터:**
- `pixels`: 픽셀 값
- `pixels_per_beat`: 박자당 픽셀 수
- `tempo`: BPM 템포

**반환값:**
- 플릭스 값

#### `pixels_to_seconds(pixels: float, pixels_per_beat: float, tempo: float) -> float`

픽셀을 초로 변환합니다.

#### `pixels_to_beats(pixels: float, pixels_per_beat: float) -> float`

픽셀을 박자로 변환합니다.

#### `pixels_to_ticks(pixels: float, pixels_per_beat: float, ppqn: int = 480) -> int`

픽셀을 MIDI 틱으로 변환합니다.

#### `pixels_to_samples(pixels: float, pixels_per_beat: float, tempo: float, sample_rate: int = 44100) -> int`

픽셀을 오디오 샘플로 변환합니다.

#### `calculate_all_timing_data(pixels: float, pixels_per_beat: float, tempo: float, sample_rate: int = 44100, ppqn: int = 480) -> dict`

주어진 픽셀 값에 대한 모든 시간 표현을 계산합니다.

**반환값:**
```python
{
    'seconds': 1.0,
    'beats': 1.0,
    'flicks': 3528000000,
    'ticks': 480,
    'samples': 44100
}
```

### 노트 생성 함수

#### `create_note_with_timing(note_id: str, start_pixels: float, duration_pixels: float, pitch: int, velocity: int, lyric: str, pixels_per_beat: float = 80, tempo: float = 120, sample_rate: int = 44100, ppqn: int = 480) -> dict`

모든 타이밍 데이터가 계산된 노트를 생성합니다.

**파라미터:**
- `note_id`: 노트 ID
- `start_pixels`: 시작 위치 (픽셀)
- `duration_pixels`: 지속 시간 (픽셀)
- `pitch`: MIDI 피치 (0-127)
- `velocity`: MIDI 벨로시티 (0-127)
- `lyric`: 가사 텍스트
- `pixels_per_beat`: 박자당 픽셀 수
- `tempo`: BPM 템포
- `sample_rate`: 샘플레이트
- `ppqn`: PPQN

**반환값:**
- 완전한 노트 객체

## 📱 사용 예제

### 기본 사용법

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

def process_piano_roll(piano_roll_data):
    # 노트 데이터 처리
    notes = piano_roll_data.get("notes", [])
    tempo = piano_roll_data.get("tempo", 120)
    
    # 분석 또는 처리 로직
    for note in notes:
        print(f"Note: {note['pitch']} at {note['startSeconds']}s")
    
    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll(
        label="MIDI 에디터",
        height=600,
        width=1000
    )
    
    piano_roll.change(
        fn=process_piano_roll,
        inputs=[piano_roll],
        outputs=[piano_roll]
    )

demo.launch()
```

### 백엔드 오디오 활용

```python
def synthesize_and_update(piano_roll_data):
    # 노트에서 오디오 생성
    audio_data = synthesize_audio(piano_roll_data)
    
    # 오디오 분석
    features = analyze_audio(audio_data)
    
    # 피아노롤에 결과 적용
    piano_roll_data["audio_data"] = audio_data
    piano_roll_data["curve_data"] = features["curves"]
    piano_roll_data["use_backend_audio"] = True
    
    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll(use_backend_audio=True)
    
    generate_btn = gr.Button("오디오 생성")
    generate_btn.click(
        fn=synthesize_and_update,
        inputs=[piano_roll],
        outputs=[piano_roll]
    )
```

### 실시간 분석

```python
def realtime_analysis(piano_roll_data):
    # 실시간 분석 로직
    if piano_roll_data.get("notes"):
        # F0 분석
        f0_data = extract_f0(piano_roll_data)
        
        # 결과 업데이트
        piano_roll_data["curve_data"] = {
            "f0_curve": create_f0_line_data(f0_data)
        }
    
    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll()
    
    # 실시간 업데이트 (0.5초마다)
    timer = gr.Timer(0.5)
    timer.tick(
        fn=realtime_analysis,
        inputs=[piano_roll],
        outputs=[piano_roll]
    )
```

## 🔍 디버깅

### 컴포넌트 상태 확인

```python
def debug_piano_roll(piano_roll_data):
    """피아노롤 상태 디버깅"""
    
    print("=== PianoRoll Debug Info ===")
    print(f"Notes count: {len(piano_roll_data.get('notes', []))}")
    print(f"Tempo: {piano_roll_data.get('tempo', 'N/A')}")
    print(f"Edit mode: {piano_roll_data.get('editMode', 'N/A')}")
    print(f"Pixels per beat: {piano_roll_data.get('pixelsPerBeat', 'N/A')}")
    print(f"Backend audio enabled: {piano_roll_data.get('use_backend_audio', False)}")
    
    # 노트별 상세 정보
    for i, note in enumerate(piano_roll_data.get('notes', [])):
        print(f"Note {i}: pitch={note.get('pitch')}, "
              f"start={note.get('startSeconds')}s, "
              f"duration={note.get('durationSeconds')}s")
    
    return piano_roll_data
```

### 오류 처리

```python
def safe_piano_roll_processing(piano_roll_data):
    """안전한 피아노롤 처리"""
    
    try:
        # 데이터 유효성 검사
        if not isinstance(piano_roll_data, dict):
            raise ValueError("Piano roll data must be a dictionary")
        
        if "notes" not in piano_roll_data:
            piano_roll_data["notes"] = []
        
        # 노트 유효성 검사
        valid_notes = []
        for note in piano_roll_data["notes"]:
            if validate_note(note):
                valid_notes.append(note)
            else:
                print(f"Invalid note skipped: {note}")
        
        piano_roll_data["notes"] = valid_notes
        
        return piano_roll_data
        
    except Exception as e:
        print(f"Error processing piano roll data: {e}")
        return {"notes": [], "tempo": 120}

def validate_note(note):
    """노트 유효성 검사"""
    required_fields = ["id", "start", "duration", "pitch", "velocity"]
    
    for field in required_fields:
        if field not in note:
            return False
    
    # 값 범위 검사
    if not (0 <= note["pitch"] <= 127):
        return False
    if not (0 <= note["velocity"] <= 127):
        return False
    if note["duration"] <= 0:
        return False
        
    return True
```

이 API 레퍼런스를 통해 Gradio PianoRoll 컴포넌트의 모든 기능을 체계적으로 활용할 수 있습니다. 각 메서드와 속성의 상세한 동작을 이해하고 효과적인 음악/오디오 애플리케이션을 개발하세요! 