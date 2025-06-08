# Components API 참조

이 페이지에서는 Gradio PianoRoll 컴포넌트의 모든 API를 상세히 설명합니다.

## PianoRoll 클래스

### 생성자

```python
PianoRoll(
    value=None,
    height=600,
    width=1000,
    elem_id=None,
    elem_classes=None,
    visible=True,
    interactive=True,
    use_backend_audio=False,
    **kwargs
)
```

#### 매개변수

| 매개변수 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `value` | `dict \| None` | `None` | 초기 피아노롤 데이터 |
| `height` | `int` | `600` | 컴포넌트 높이 (픽셀) |
| `width` | `int` | `1000` | 컴포넌트 너비 (픽셀) |
| `elem_id` | `str \| None` | `None` | HTML 요소 ID |
| `elem_classes` | `list[str] \| str \| None` | `None` | CSS 클래스 |
| `visible` | `bool` | `True` | 컴포넌트 표시 여부 |
| `interactive` | `bool` | `True` | 사용자 입력 허용 여부 |
| `use_backend_audio` | `bool` | `False` | 백엔드 오디오 엔진 사용 여부 |

### 데이터 구조

#### PianoRoll 데이터 형식

```python
{
    "notes": [
        {
            "id": "note_0",           # 음표 고유 ID (선택사항)
            "start": 0,               # 시작 위치 (픽셀)
            "duration": 160,          # 지속 시간 (픽셀)
            "pitch": 60,              # MIDI 노트 번호 (0-127)
            "velocity": 100,          # 세기 (0-127)
            "lyric": "가사",          # 가사 (선택사항)
            "phoneme": "g a s a"      # 음성학 표기 (선택사항)
        }
    ],
    "tempo": 120,                     # 템포 (BPM)
    "timeSignature": {                # 박자표
        "numerator": 4,               # 분자
        "denominator": 4              # 분모
    },
    "editMode": "select",             # 편집 모드
    "snapSetting": "1/4",             # 스냅 설정
    "pixelsPerBeat": 80,              # 박자당 픽셀 수
    "curve_data": {},                 # 곡선 데이터 (선택사항)
    "line_data": {},                  # 라인 데이터 (선택사항)
    "audio_data": "data:audio/wav;base64,...",  # 오디오 데이터 (선택사항)
    "use_backend_audio": false        # 백엔드 오디오 사용 여부
}
```

#### Note 객체

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `id` | `string` | ❌ | 음표 고유 식별자 |
| `start` | `number` | ✅ | 시작 위치 (픽셀 단위) |
| `duration` | `number` | ✅ | 지속 시간 (픽셀 단위) |
| `pitch` | `number` | ✅ | MIDI 노트 번호 (0-127) |
| `velocity` | `number` | ❌ | 음량/세기 (0-127, 기본값: 100) |
| `lyric` | `string` | ❌ | 가사 텍스트 |
| `phoneme` | `string` | ❌ | 음성학적 표기 |

#### 편집 모드

| 모드 | 설명 | 기본 동작 |
|------|------|----------|
| `"select"` | 선택 모드 | 음표 선택, 이동, 크기 조정 |
| `"create"` | 생성 모드 | 새 음표 생성 |
| `"delete"` | 삭제 모드 | 음표 삭제 |

#### 스냅 설정

| 값 | 설명 | 픽셀 단위 (80 pixels/beat 기준) |
|----|------|--------------------------------|
| `"1/1"` | 온음표 | 320 픽셀 |
| `"1/2"` | 2분음표 | 160 픽셀 |
| `"1/4"` | 4분음표 | 80 픽셀 |
| `"1/8"` | 8분음표 | 40 픽셀 |
| `"1/16"` | 16분음표 | 20 픽셀 |
| `"1/32"` | 32분음표 | 10 픽셀 |

### 메서드

#### `update(value=None, **kwargs)`

컴포넌트 값을 업데이트합니다.

```python
piano_roll.update(value=new_data, visible=True)
```

#### `postprocess(value)`

프론트엔드로 전송하기 전에 데이터를 후처리합니다.

#### `preprocess(value)`

백엔드에서 받은 데이터를 전처리합니다.

## 고급 데이터 구조

### Curve Data (곡선 데이터)

웨이브폼이나 기타 시각화 데이터를 저장합니다.

```python
{
    "curve_data": {
        "waveform_data": [
            {
                "x": 0,      # X 좌표 (픽셀)
                "min": -0.5, # 최소값
                "max": 0.5   # 최대값
            }
        ]
    }
}
```

### Line Data (라인 데이터)

F0, 음량, 유성음/무성음 등의 분석 결과를 시각화합니다.

```python
{
    "line_data": {
        "f0_curve": {
            "color": "#FF6B6B",
            "lineWidth": 3,
            "yMin": 0,
            "yMax": 2560,
            "position": "overlay",
            "renderMode": "piano_grid",
            "visible": true,
            "opacity": 0.8,
            "data": [
                {
                    "x": 0,    # X 좌표 (픽셀)
                    "y": 1200  # Y 좌표 (픽셀)
                }
            ],
            "dataType": "f0",
            "unit": "Hz"
        }
    }
}
```

#### Line Data 속성

| 속성 | 타입 | 설명 |
|------|------|------|
| `color` | `string` | 선 색상 (hex, rgb, rgba) |
| `lineWidth` | `number` | 선 두께 (픽셀) |
| `yMin` | `number` | Y축 최소값 |
| `yMax` | `number` | Y축 최대값 |
| `position` | `string` | 위치 (`"overlay"`, `"background"`) |
| `renderMode` | `string` | 렌더링 모드 (`"piano_grid"`, `"independent_range"`) |
| `visible` | `boolean` | 표시 여부 |
| `opacity` | `number` | 투명도 (0.0-1.0) |
| `data` | `array` | 데이터 포인트 배열 |
| `dataType` | `string` | 데이터 타입 (`"f0"`, `"loudness"`, `"voicing"`) |
| `unit` | `string` | 단위 (`"Hz"`, `"dB"`, `"normalized"`) |

## 상수 및 제한사항

### MIDI 범위

| 항목 | 값 | 설명 |
|------|----|----- |
| `MIDI_MIN` | 0 | 최소 MIDI 노트 번호 |
| `MIDI_MAX` | 127 | 최대 MIDI 노트 번호 |
| `MIDDLE_C` | 60 | 중앙 C (C4) |
| `CONCERT_A` | 69 | 표준 A (A4, 440Hz) |

### 기본값

| 설정 | 값 | 설명 |
|------|----|----- |
| `DEFAULT_TEMPO` | 120 | 기본 템포 (BPM) |
| `DEFAULT_PIXELS_PER_BEAT` | 80 | 기본 박자당 픽셀 수 |
| `DEFAULT_NOTE_HEIGHT` | 20 | 기본 음표 높이 (픽셀) |
| `DEFAULT_VELOCITY` | 100 | 기본 음표 세기 |

### 제한사항

| 항목 | 제한 | 설명 |
|------|------|------|
| 최대 음표 수 | 1000 | 성능 고려사항 |
| 최대 지속시간 | 10분 | 오디오 합성 시 |
| 최소 템포 | 30 BPM | UI 제한 |
| 최대 템포 | 300 BPM | UI 제한 |

## 유틸리티 함수

### MIDI 변환

```python
def midi_to_frequency(midi_note):
    """MIDI 번호를 주파수로 변환"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def frequency_to_midi(frequency):
    """주파수를 MIDI 번호로 변환"""
    return 69 + 12 * math.log2(frequency / 440.0)
```

### 시간 변환

```python
def pixels_to_seconds(pixels, tempo, pixels_per_beat):
    """픽셀을 초로 변환"""
    beats = pixels / pixels_per_beat
    return beats * (60.0 / tempo)

def seconds_to_pixels(seconds, tempo, pixels_per_beat):
    """초를 픽셀로 변환"""
    beats = seconds * (tempo / 60.0)
    return beats * pixels_per_beat
```

## 타입 정의

TypeScript 스타일 타입 정의:

```typescript
interface Note {
    id?: string;
    start: number;
    duration: number;
    pitch: number;
    velocity?: number;
    lyric?: string;
    phoneme?: string;
}

interface TimeSignature {
    numerator: number;
    denominator: number;
}

interface PianoRollData {
    notes: Note[];
    tempo?: number;
    timeSignature?: TimeSignature;
    editMode?: "select" | "create" | "delete";
    snapSetting?: "1/1" | "1/2" | "1/4" | "1/8" | "1/16" | "1/32";
    pixelsPerBeat?: number;
    curve_data?: object;
    line_data?: object;
    audio_data?: string;
    use_backend_audio?: boolean;
}
```

## 예제

### 기본 사용

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

with gr.Blocks() as demo:
    piano_roll = PianoRoll(
        value={
            "notes": [
                {"start": 0, "duration": 80, "pitch": 60, "velocity": 100}
            ],
            "tempo": 120
        },
        height=400,
        width=800
    )

demo.launch()
```

### 이벤트 처리

```python
def on_change(data):
    print(f"음표 수: {len(data.get('notes', []))}")
    return data

piano_roll.change(on_change, piano_roll, piano_roll)
```

이 API 참조를 통해 Gradio PianoRoll의 모든 기능을 완전히 활용할 수 있습니다.