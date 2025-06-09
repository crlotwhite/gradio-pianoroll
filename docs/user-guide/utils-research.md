# 🔬 연구자용 Utils - research 모듈

`gradio_pianoroll.utils.research` 모듈은 연구자들이 피아노롤 컴포넌트를 쉽게 활용할 수 있도록 다양한 헬퍼 함수를 제공합니다. TypedDict 기반의 타입 안전한 API를 제공합니다.

## 📦 모듈 Import

```python
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research
from gradio_pianoroll.data_models import PianoRollData  # 타입 힌트용 (선택사항)
```

## 🎯 빠른 생성 함수들

### `from_notes()`

간단한 노트 리스트에서 피아노롤 데이터를 생성합니다. TypedDict 형식의 데이터를 반환합니다.

```python
def from_notes(notes: List[Tuple[int, float, float]],
               tempo: int = 120,
               lyrics: Optional[List[str]] = None) -> PianoRollData
```

**매개변수**:
- `notes`: `(pitch, start_time_sec, duration_sec)` 튜플들의 리스트
- `tempo`: BPM (기본값: 120)
- `lyrics`: 가사 리스트 (선택사항)

**예제**:
```python
# C-E-G 코드 생성 (타입 안전)
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
data: PianoRollData = research.from_notes(notes, tempo=120)
piano_roll = PianoRoll(value=data)

# 가사와 함께
notes = [(60, 0, 0.5), (62, 0.5, 0.5)]
lyrics = ["안녕", "하세요"]
data = research.from_notes(notes, lyrics=lyrics)

# 자동 유효성 검사 및 데이터 정리
invalid_notes = [(999, 0, 1)]  # 잘못된 피치
data = research.from_notes(invalid_notes)  # 자동으로 수정됨
```

### `from_midi_numbers()`

MIDI 노트 번호 리스트에서 피아노롤을 생성합니다.

```python
def from_midi_numbers(midi_notes: List[int],
                     durations: Optional[List[float]] = None,
                     start_times: Optional[List[float]] = None,
                     tempo: int = 120) -> Dict
```

**예제**:
```python
# C major scale
midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
data = research.from_midi_numbers(midi_notes)

# 커스텀 타이밍
midi_notes = [60, 64, 67]
start_times = [0, 0.5, 1.0]  # 동시에, 0.5초 후, 1초 후
durations = [2.0, 1.5, 1.0]  # 서로 다른 길이
data = research.from_midi_numbers(midi_notes, durations, start_times)
```

### `from_frequencies()`

주파수(Hz) 리스트에서 피아노롤을 생성합니다.

```python
def from_frequencies(frequencies: List[float],
                    durations: Optional[List[float]] = None,
                    start_times: Optional[List[float]] = None,
                    tempo: int = 120) -> Dict
```

**예제**:
```python
# A4, B4, C5 주파수
frequencies = [440, 493.88, 523.25]
data = research.from_frequencies(frequencies)

# F0 곡선에서 추출한 주파수들
f0_curve = [220.1, 221.5, 223.2, 225.0]  # 변화하는 F0
data = research.from_frequencies(f0_curve, durations=[0.1]*4, start_times=[i*0.1 for i in range(4)])
```

## 🤖 모델 출력 변환 함수들

### `from_tts_output()`

TTS 모델의 정렬 결과를 피아노롤로 변환합니다.

```python
def from_tts_output(text: str,
                    alignment: List[Tuple[str, float, float]],
                    f0_data: Optional[List[float]] = None,
                    tempo: int = 120) -> Dict
```

**예제**:
```python
# TTS 모델 정렬 결과
text = "안녕하세요"
alignment = [("안", 0.0, 0.5), ("녕", 0.5, 1.0), ("하", 1.0, 1.3), ("세", 1.3, 1.6), ("요", 1.6, 2.0)]

# F0 데이터와 함께
f0_data = [220, 230, 240, 235, 225, 220, 215, 210]  # 8프레임의 F0
data = research.from_tts_output(text, alignment, f0_data)

piano_roll = PianoRoll(value=data)
```

### `from_midi_generation()`

MIDI 생성 모델 출력을 피아노롤로 변환합니다.

```python
def from_midi_generation(generated_sequence: List[Dict],
                        tempo: int = 120) -> Dict
```

**예제**:
```python
# 생성 모델 출력 예시
generated_sequence = [
    {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100},
    {"pitch": 64, "start": 0.5, "duration": 0.5, "velocity": 90},
    {"pitch": 67, "start": 1.0, "duration": 1.0, "velocity": 95, "lyric": "생성됨"}
]

data = research.from_midi_generation(generated_sequence)
piano_roll = PianoRoll(value=data)
```

## 🚀 템플릿 생성 함수들

### `quick_demo()`

3줄로 피아노롤 데모를 만듭니다.

```python
def quick_demo(notes: List[Tuple[int, float, float]],
               title: str = "Quick Piano Roll Demo",
               tempo: int = 120,
               **component_kwargs) -> gr.Blocks
```

**예제**:
```python
# 초간단 데모 생성
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
demo = research.quick_demo(notes, "내 TTS 모델 결과")
demo.launch()

# 컴포넌트 옵션 추가
demo = research.quick_demo(notes, "고급 데모", height=600, width=1200)
```

### `create_pianoroll_with_data()`

데이터와 함께 피아노롤 컴포넌트가 포함된 Gradio 데모를 생성합니다.

```python
def create_pianoroll_with_data(data: Dict, **component_kwargs) -> gr.Blocks
```

**예제**:
```python
# 기존 데이터로 데모 생성
data = research.from_notes([(60, 0, 1), (64, 1, 1)])
demo = research.create_pianoroll_with_data(data, height=500)
demo.launch()
```

## 📊 분석 도구들

### `analyze_notes()`

피아노롤에서 노트 통계를 추출합니다.

```python
def analyze_notes(piano_roll_data: Dict) -> Dict
```

**예제**:
```python
# 피아노롤 데이터 분석
stats = research.analyze_notes(piano_roll_data)
print(stats)
# 출력:
# {
#   "총_노트_수": 3,
#   "음역대": {"최저음": 60, "최고음": 67, "음역": 7},
#   "평균_피치": 63.7,
#   "평균_벨로시티": 100.0,
#   "평균_노트_길이_초": 1.0,
#   "총_재생시간_초": 3.0,
#   "리듬_분석": {...}
# }
```

### `auto_analyze()`

모델 출력을 자동으로 분석해서 피아노롤 형식으로 변환합니다.

```python
def auto_analyze(model_output_data: Union[List, Dict],
                output_type: str = "auto") -> Dict
```

**예제**:
```python
# 자동 타입 감지
model_output = [(60, 0, 1), (64, 1, 1)]  # (pitch, time, duration) 형식
data = research.auto_analyze(model_output)

# 타입 명시
tts_output = [("안", 0.0, 0.5), ("녕", 0.5, 1.0)]
data = research.auto_analyze(tts_output, "tts")

# MIDI 생성 모델 출력
midi_output = [{"pitch": 60, "start": 0, "duration": 1, "velocity": 100}]
data = research.auto_analyze(midi_output, "midi_generation")
```

## 🔧 실전 사용 예제

### TTS 연구자 워크플로우

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

def tts_demo():
    def process_tts_output(text, model_alignment, f0_curve):
        """TTS 모델 출력 처리"""
        # 1. TTS 정렬 데이터를 피아노롤로 변환
        data = research.from_tts_output(text, model_alignment, f0_curve)

        # 2. 통계 분석
        stats = research.analyze_notes(data)

        return data, stats

    with gr.Blocks() as demo:
        gr.Markdown("## TTS 모델 출력 분석")

        # 입력
        text_input = gr.Textbox(label="입력 텍스트")
        # ... 기타 입력들

        # 출력
        piano_roll = PianoRoll(height=400)
        stats_output = gr.JSON(label="통계")

        # 처리 버튼
        process_btn = gr.Button("분석")
        process_btn.click(process_tts_output, inputs=[...], outputs=[piano_roll, stats_output])

    return demo
```

### MIDI 생성 연구자 워크플로우

```python
def midi_generation_demo():
    def generate_and_visualize(prompt, length):
        """MIDI 생성 및 시각화"""
        # 1. 모델 실행 (예시)
        generated_notes = your_midi_model.generate(prompt, length)

        # 2. 피아노롤로 변환
        data = research.from_midi_generation(generated_notes)

        # 3. 분석
        stats = research.analyze_notes(data)

        return data, f"Generated {len(generated_notes)} notes"

    with gr.Blocks() as demo:
        # ... UI 구성
        pass

    return demo
```

### 오디오 분석 연구자 워크플로우

```python
def audio_analysis_demo():
    def analyze_audio_features(audio_file):
        """오디오 파일 분석"""
        # 1. 오디오에서 F0 추출
        f0_curve = extract_f0_from_audio(audio_file)

        # 2. 주파수를 피아노롤로 변환
        data = research.from_frequencies(f0_curve)

        # 3. 통계 분석
        stats = research.analyze_notes(data)

        return data, stats

    with gr.Blocks() as demo:
        # ... UI 구성
        pass

    return demo
```

## 💡 팁과 모범 사례

### 1. 단계별 접근

```python
# ✅ 좋은 예: 단계별로 명확하게
notes = [(60, 0, 1), (64, 1, 1)]
data = research.from_notes(notes)
piano_roll = PianoRoll(value=data)

# ❌ 피할 것: 한 줄에 모든 것
piano_roll = PianoRoll(value=research.from_notes([(60, 0, 1)]))
```

### 2. 데이터 검증

```python
# 데이터 생성 후 검증
data = research.from_notes(notes)
stats = research.analyze_notes(data)
print(f"생성된 노트 수: {stats['총_노트_수']}")
```

### 3. 재사용 가능한 함수

```python
def create_scale_visualization(root_note: int, scale_type: str):
    """재사용 가능한 스케일 시각화 함수"""
    scales = {
        "major": [0, 2, 4, 5, 7, 9, 11, 12],
        "minor": [0, 2, 3, 5, 7, 8, 10, 12]
    }

    intervals = scales.get(scale_type, scales["major"])
    midi_notes = [root_note + interval for interval in intervals]

    return research.from_midi_numbers(midi_notes)

# 사용
c_major = create_scale_visualization(60, "major")
a_minor = create_scale_visualization(57, "minor")
```

## 🔗 관련 문서

- [Migration Guide](../getting-started/migration-guide.md) - 기존 코드 마이그레이션
- [Templates 모듈](utils-templates.md) - 템플릿 사용법
- [API 문서](../api/components.md) - 전체 API 참조