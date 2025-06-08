# 빠른 시작

이 가이드를 통해 Gradio PianoRoll을 5분 만에 시작할 수 있습니다!

## 🚀 첫 번째 PianoRoll 만들기

### 1. 기본 설정

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

# 간단한 피아노롤 생성
with gr.Blocks() as demo:
    piano_roll = PianoRoll()

demo.launch()
```

### 2. 초기 데이터가 있는 PianoRoll

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

# 초기 음표가 있는 피아노롤
initial_data = {
    "notes": [
        {
            "start": 0,
            "duration": 160,
            "pitch": 60,  # C4
            "velocity": 100,
            "lyric": "도"
        },
        {
            "start": 160,
            "duration": 160,
            "pitch": 64,  # E4
            "velocity": 100,
            "lyric": "미"
        },
        {
            "start": 320,
            "duration": 160,
            "pitch": 67,  # G4
            "velocity": 100,
            "lyric": "솔"
        }
    ],
    "tempo": 120,
    "timeSignature": {"numerator": 4, "denominator": 4}
}

with gr.Blocks() as demo:
    piano_roll = PianoRoll(
        value=initial_data,
        height=400,
        width=800
    )

demo.launch()
```

## 🎛️ 기본 컨트롤

### 편집 모드

PianoRoll은 3가지 편집 모드를 제공합니다:

- **Select (선택)**: 기본 모드, 음표 선택 및 이동
- **Create (생성)**: 새 음표 생성
- **Delete (삭제)**: 음표 삭제

### 키보드 단축키

| 키 | 기능 |
|---|---|
| `S` | Select 모드로 전환 |
| `C` | Create 모드로 전환 |
| `D` | Delete 모드로 전환 |
| `Space` | 재생/정지 |
| `Delete` | 선택된 음표 삭제 |

## 🎵 기본 조작법

### 1. 음표 생성하기

1. 키보드에서 `C` 키를 눌러 Create 모드로 전환
2. 원하는 위치에 마우스 클릭
3. 드래그하여 음표 길이 조정

### 2. 음표 편집하기

1. 키보드에서 `S` 키를 눌러 Select 모드로 전환
2. 음표를 클릭하여 선택
3. 드래그하여 위치 이동
4. 모서리를 드래그하여 길이 조정

### 3. 음표 삭제하기

**방법 1:** Delete 모드 사용
1. 키보드에서 `D` 키를 눌러 Delete 모드로 전환
2. 삭제할 음표 클릭

**방법 2:** 키보드 단축키 사용
1. Select 모드에서 음표 선택
2. `Delete` 키 누르기

## 📊 데이터 처리

### 음표 데이터 가져오기

```python
def get_piano_roll_data(piano_roll_data):
    print("현재 음표들:")
    for i, note in enumerate(piano_roll_data.get('notes', [])):
        print(f"음표 {i+1}: 음높이={note['pitch']}, 시작={note['start']}, 길이={note['duration']}")
    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll()
    output = gr.JSON()

    # 버튼 클릭 시 데이터 출력
    btn = gr.Button("데이터 확인")
    btn.click(get_piano_roll_data, piano_roll, output)

demo.launch()
```

### 음표 데이터 수정하기

```python
def add_c_major_chord(piano_roll_data):
    """C 메이저 코드 추가"""
    if piano_roll_data is None:
        piano_roll_data = {"notes": [], "tempo": 120}

    # C 메이저 코드 (C4, E4, G4)
    chord_notes = [
        {"start": 0, "duration": 320, "pitch": 60, "velocity": 100},  # C4
        {"start": 0, "duration": 320, "pitch": 64, "velocity": 100},  # E4
        {"start": 0, "duration": 320, "pitch": 67, "velocity": 100},  # G4
    ]

    piano_roll_data["notes"] = chord_notes
    return piano_roll_data

with gr.Blocks() as demo:
    piano_roll = PianoRoll()

    btn = gr.Button("C 메이저 코드 추가")
    btn.click(add_c_major_chord, piano_roll, piano_roll)

demo.launch()
```

## 🎹 실용적인 예제

### 스케일 생성기

```python
def create_scale(scale_type, start_note=60):
    """다양한 스케일 생성"""
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "minor": [0, 2, 3, 5, 7, 8, 10, 12],
        "pentatonic": [0, 2, 4, 7, 9, 12]
    }

    if scale_type not in scales:
        return {"notes": [], "tempo": 120}

    notes = []
    for i, interval in enumerate(scales[scale_type]):
        note = {
            "start": i * 80,
            "duration": 80,
            "pitch": start_note + interval,
            "velocity": 100
        }
        notes.append(note)

    return {"notes": notes, "tempo": 120}

with gr.Blocks() as demo:
    gr.Markdown("# 🎼 스케일 생성기")

    with gr.Row():
        scale_dropdown = gr.Dropdown(
            choices=["major", "minor", "pentatonic"],
            value="major",
            label="스케일 종류"
        )
        start_note_slider = gr.Slider(
            minimum=36, maximum=84, value=60,
            label="시작 음표 (MIDI 번호)"
        )

    piano_roll = PianoRoll(height=400, width=800)

    btn = gr.Button("스케일 생성")
    btn.click(
        create_scale,
        inputs=[scale_dropdown, start_note_slider],
        outputs=piano_roll
    )

demo.launch()
```

## 🔄 이벤트 처리

### 재생 이벤트 처리

```python
def on_play_start():
    return "▶️ 재생 시작됨"

def on_play_pause():
    return "⏸️ 재생 일시정지됨"

def on_play_stop():
    return "⏹️ 재생 정지됨"

with gr.Blocks() as demo:
    piano_roll = PianoRoll()
    status = gr.Textbox(label="상태")

    # 이벤트 리스너 등록
    piano_roll.play(on_play_start, outputs=status)
    piano_roll.pause(on_play_pause, outputs=status)
    piano_roll.stop(on_play_stop, outputs=status)

demo.launch()
```

## 💡 유용한 팁

### 1. MIDI 노트 번호 계산

```python
def note_to_midi(note_name, octave):
    """음표 이름을 MIDI 번호로 변환"""
    notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
             'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return notes[note_name] + (octave + 1) * 12

# 예: C4는 MIDI 60
c4 = note_to_midi('C', 4)  # 60
a4 = note_to_midi('A', 4)  # 69
```

### 2. 시간 단위 변환

```python
def beats_to_pixels(beats, pixels_per_beat=80):
    """박자를 픽셀로 변환"""
    return beats * pixels_per_beat

def seconds_to_pixels(seconds, tempo=120, pixels_per_beat=80):
    """초를 픽셀로 변환"""
    beats = seconds * (tempo / 60)
    return beats * pixels_per_beat

# 예: 1박자 = 80픽셀, 2초 = ?픽셀 (120 BPM)
one_beat = beats_to_pixels(1)  # 80
two_seconds = seconds_to_pixels(2, 120)  # 320
```

### 3. 코드 생성 도우미

```python
def create_chord(root_note, chord_type="major"):
    """코드 생성 도우미"""
    chords = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "sus4": [0, 5, 7],
        "sus2": [0, 2, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8]
    }

    if chord_type not in chords:
        return []

    return [root_note + interval for interval in chords[chord_type]]

# 예: C 메이저 코드
c_major = create_chord(60, "major")  # [60, 64, 67] = C4, E4, G4
```

## 🔗 다음 단계

기본 사용법을 익혔다면 더 고급 기능을 살펴보세요:

### 🟢 초급
- **[기본 데모](../examples/basic-usage.md)**: 상세한 기본 기능 설명

### 🟡 중급
- **[신디사이저 데모](../examples/synthesizer.md)**: 오디오 합성 기능
- **[음성학 처리](../examples/phoneme-processing.md)**: G2P 변환 기능

### 🔴 고급
- **[F0 분석](../examples/f0-analysis.md)**: 오디오 신호 분석
- **[오디오 특성 분석](../examples/audio-features.md)**: 종합적인 오디오 분석

### 📚 참고 자료
- **[API 참조](../api/components.md)**: 전체 컴포넌트 명세
- **[가이드](../guides/)**: 기능별 상세 설명

---

🎉 **축하합니다!** 이제 Gradio PianoRoll을 사용할 준비가 되었습니다.
궁금한 점이 있으면 [GitHub Issues](https://github.com/crlotwhite/gradio-pianoroll/issues)에서 질문해주세요!