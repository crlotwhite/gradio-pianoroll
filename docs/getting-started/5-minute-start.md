# 5분 시작 가이드

이 가이드를 통해 5분 안에 Gradio PianoRoll을 사용하여 첫 번째 데모를 만들어보세요! 🚀

## 📋 준비사항

```bash
pip install gradio-pianoroll
```

## 🎯 1단계: 첫 번째 피아노롤 (1분)

가장 간단한 피아노롤을 만들어보세요:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

with gr.Blocks(title="내 첫 피아노롤") as demo:
    gr.Markdown("# 🎹 내 첫 피아노롤")
    piano_roll = PianoRoll(height=400)

demo.launch()
```

**✅ 체크포인트**: 브라우저에서 피아노롤이 표시되어야 합니다.

## 🎵 2단계: 데이터와 함께 시작 (2분)

TypedDict를 사용해 타입 안전한 초기 데이터를 추가해보세요:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.data_models import PianoRollData

# 타입 안전한 초기 데이터
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
            "velocity": 100,
            "lyric": "하세요"
        },
        {
            "id": "note_3",
            "start": 320,
            "duration": 160,
            "pitch": 67,  # G4
            "velocity": 100,
            "lyric": "피아노"
        }
    ],
    "tempo": 120,
    "timeSignature": {"numerator": 4, "denominator": 4},
    "editMode": "select",
    "snapSetting": "1/4"
}

with gr.Blocks(title="데이터가 있는 피아노롤") as demo:
    gr.Markdown("# 🎹 초기 데이터가 있는 피아노롤")
    piano_roll = PianoRoll(value=initial_data, height=500)

demo.launch()
```

**✅ 체크포인트**: 3개의 노트가 표시되고 가사가 보여야 합니다.

## 🔄 3단계: 인터랙션 추가 (1분)

노트 변경을 감지하는 이벤트를 추가해보세요:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.data_models import PianoRollData

def handle_changes(piano_roll_data):
    """노트 변경 시 호출되는 함수"""
    notes = piano_roll_data.get("notes", [])

    # 간단한 분석
    note_count = len(notes)
    if notes:
        pitches = [note["pitch"] for note in notes]
        pitch_range = f"{min(pitches)} ~ {max(pitches)}"
        lyrics = [note.get("lyric", "") for note in notes if note.get("lyric")]
        lyric_text = ", ".join(lyrics) if lyrics else "가사 없음"
    else:
        pitch_range = "노트 없음"
        lyric_text = "노트 없음"

    summary = f"노트 개수: {note_count} | 음역: {pitch_range} | 가사: {lyric_text}"
    return piano_roll_data, summary

# 이전 단계의 initial_data 사용
with gr.Blocks(title="인터랙티브 피아노롤") as demo:
    gr.Markdown("# 🎹 인터랙티브 피아노롤")

    piano_roll = PianoRoll(value=initial_data, height=500)
    info_text = gr.Textbox(
        label="📊 실시간 정보",
        value="노트를 편집해보세요!",
        interactive=False
    )

    # 노트 변경 시 실시간 업데이트
    piano_roll.change(
        fn=handle_changes,
        inputs=piano_roll,
        outputs=[piano_roll, info_text]
    )

demo.launch()
```

**✅ 체크포인트**: 노트를 편집하면 하단 텍스트가 실시간으로 업데이트되어야 합니다.

## 🚀 4단계: 연구자용 헬퍼 사용 (1분)

연구자용 유틸리티로 더 쉽게 데이터를 생성해보세요:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

def create_scale_notes(scale_type):
    """다양한 스케일 생성"""
    scales = {
        "C Major": [(60, 0, 0.5), (62, 0.5, 0.5), (64, 1.0, 0.5), (65, 1.5, 0.5),
                   (67, 2.0, 0.5), (69, 2.5, 0.5), (71, 3.0, 0.5), (72, 3.5, 0.5)],
        "C Minor": [(60, 0, 0.5), (62, 0.5, 0.5), (63, 1.0, 0.5), (65, 1.5, 0.5),
                   (67, 2.0, 0.5), (68, 2.5, 0.5), (70, 3.0, 0.5), (72, 3.5, 0.5)],
        "Pentatonic": [(60, 0, 0.5), (62, 0.5, 0.5), (64, 1.0, 0.5),
                      (67, 1.5, 0.5), (69, 2.0, 0.5)]
    }

    notes = scales.get(scale_type, scales["C Major"])
    lyrics = ["도", "레", "미", "파", "솔", "라", "시", "도"]

    # research 모듈로 쉽게 데이터 생성
    return research.from_notes(notes, tempo=120, lyrics=lyrics[:len(notes)])

def analyze_current_notes(piano_roll_data):
    """현재 노트 분석"""
    return research.analyze_notes(piano_roll_data)

with gr.Blocks(title="연구자용 피아노롤") as demo:
    gr.Markdown("# 🎹 연구자용 도구 활용")

    with gr.Row():
        scale_dropdown = gr.Dropdown(
            choices=["C Major", "C Minor", "Pentatonic"],
            value="C Major",
            label="🎼 스케일 선택"
        )
        generate_btn = gr.Button("🎵 생성", variant="primary")

    piano_roll = PianoRoll(height=500)

    with gr.Row():
        analysis_output = gr.JSON(label="📊 노트 분석")

    # 스케일 생성
    generate_btn.click(
        fn=create_scale_notes,
        inputs=scale_dropdown,
        outputs=piano_roll
    )

    # 실시간 분석
    piano_roll.change(
        fn=analyze_current_notes,
        inputs=piano_roll,
        outputs=analysis_output
    )

demo.launch()
```

**✅ 체크포인트**: 드롭다운에서 스케일을 선택하면 해당 음계가 생성되고, 분석 결과가 표시되어야 합니다.

## 🎉 완성! 보너스 기능들

### TypedDict 자동완성 활용

```python
from gradio_pianoroll.data_models import PianoRollData, Note
from typing import List

def type_safe_function(data: PianoRollData) -> PianoRollData:
    """타입 안전한 함수 - IDE에서 자동완성 지원!"""
    notes: List[Note] = data["notes"]

    # IDE가 자동으로 필드를 추천합니다
    for note in notes:
        print(f"Pitch: {note['pitch']}")  # 자동완성!
        print(f"Lyric: {note.get('lyric', '')}")  # 안전한 접근!

    return data
```

### 데이터 유효성 자동 검사

```python
from gradio_pianoroll.data_models import validate_and_warn

# 잘못된 데이터 입력 시 자동 경고
bad_data = {
    "notes": [{"pitch": 999}],  # 잘못된 피치
    "tempo": -50               # 잘못된 템포
}

piano_roll = PianoRoll(value=bad_data)  # 자동으로 경고 출력!
```

### 3줄 데모 생성

```python
from gradio_pianoroll.utils import research

# 단 3줄로 완전한 데모 생성!
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
demo = research.quick_demo(notes, title="내 AI 모델 결과")
demo.launch()
```

## 📝 다음 학습 추천

1. **[기본 사용법](../user-guide/basic-usage.md)** - 더 자세한 사용법
2. **[연구자용 유틸리티](../user-guide/utils-research.md)** - 고급 헬퍼 함수들
3. **[음성 합성](../user-guide/synthesizer.md)** - 오디오 생성
4. **[오디오 분석](../user-guide/audio-analysis.md)** - F0, 음량 분석

## 🆘 문제 해결

### 자주 발생하는 오류

| 오류 | 해결법 |
|------|--------|
| `ModuleNotFoundError: gradio_pianoroll` | `pip install gradio-pianoroll` |
| `KeyError: 'notes'` | `clean_piano_roll_data()` 사용 |
| 타입 경고 | TypedDict import 및 타입 힌트 추가 |

### 데이터 검증

```python
from gradio_pianoroll.data_models import validate_piano_roll_data

# 데이터 문제 진단
errors = validate_piano_roll_data(your_data)
if errors:
    print("문제점:", errors)
```

축하합니다! 🎉 이제 Gradio PianoRoll의 기본 사용법을 마스터했습니다!