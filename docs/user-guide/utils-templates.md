# 🎨 연구자용 Utils - templates 모듈

`gradio_pianoroll.utils.templates` 모듈은 연구자들이 빠르게 프로토타입을 만들 수 있도록 다양한 분야별 템플릿을 제공합니다.

## 📦 모듈 Import

```python
from gradio_pianoroll.utils import templates
```

## 🎯 기본 템플릿

### `create_basic_template()`

가장 간단한 피아노롤 템플릿을 생성합니다.

```python
def create_basic_template() -> gr.Blocks
```

**예제**:
```python
from gradio_pianoroll.utils import templates

# 3줄로 피아노롤 완성
demo = templates.create_basic_template()
demo.launch()
```

**기능**:
- 기본 피아노롤 컴포넌트
- 노트 수 표시
- 즉시 사용 가능

## 🎤 TTS 연구자용 템플릿

### `create_tts_template()`

TTS 연구자를 위한 텍스트 입력 → 노트 시각화 템플릿을 생성합니다.

```python
def create_tts_template() -> gr.Blocks
```

**예제**:
```python
# TTS 연구자용 템플릿
demo = templates.create_tts_template()
demo.launch()
```

**기능**:
- 텍스트 입력 필드
- 단어별 노트 자동 생성
- 실시간 시각화
- 한국어 지원

**사용 시나리오**:
```python
# 입력: "안녕하세요 피아노롤입니다"
# 출력: 각 단어가 노트로 변환되어 시각화
```

### TTS 템플릿 커스터마이징

```python
def custom_tts_template():
    """커스터마이즈된 TTS 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    def advanced_tts_processing(text, pitch_shift, tempo):
        """고급 TTS 처리"""
        words = text.split()
        notes = []

        for i, word in enumerate(words):
            pitch = 60 + pitch_shift + (i % 12)
            notes.append((pitch, i * 0.5, 0.5))

        return research.from_notes(notes, lyrics=words, tempo=tempo)

    with gr.Blocks() as demo:
        gr.Markdown("## 🎤 고급 TTS 분석")

        with gr.Row():
            text_input = gr.Textbox(label="입력 텍스트")
            pitch_shift = gr.Slider(-12, 12, 0, label="피치 조정")
            tempo_slider = gr.Slider(60, 180, 120, label="템포")

        piano_roll = PianoRoll(height=400)

        inputs = [text_input, pitch_shift, tempo_slider]
        text_input.submit(advanced_tts_processing, inputs, piano_roll)

    return demo
```

## 🎵 MIDI 생성 연구자용 템플릿

### `create_midi_generation_template()`

MIDI 생성 모델 출력 시각화 템플릿을 생성합니다.

```python
def create_midi_generation_template() -> gr.Blocks
```

**예제**:
```python
# MIDI 생성 연구자용 템플릿
demo = templates.create_midi_generation_template()
demo.launch()
```

**기능**:
- 생성할 노트 수 조절
- C major scale 기반 생성
- 랜덤 벨로시티
- 실시간 생성 및 시각화

### MIDI 생성 템플릿 커스터마이징

```python
def advanced_midi_template():
    """고급 MIDI 생성 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    def generate_with_style(scale_type, length, velocity_variation):
        """스타일별 MIDI 생성"""
        scales = {
            "C Major": [60, 62, 64, 65, 67, 69, 71, 72],
            "A Minor": [57, 59, 60, 62, 64, 65, 67, 69],
            "D Dorian": [62, 64, 65, 67, 69, 71, 72, 74],
            "Chromatic": list(range(60, 73))
        }

        scale = scales.get(scale_type, scales["C Major"])
        notes = []

        for i in range(length):
            pitch = scale[i % len(scale)]
            velocity = 100 + np.random.randint(-velocity_variation, velocity_variation)
            velocity = max(1, min(127, velocity))

            notes.append({
                "pitch": pitch,
                "start": i * 0.5,
                "duration": 0.4,
                "velocity": velocity
            })

        return research.from_midi_generation(notes)

    with gr.Blocks() as demo:
        gr.Markdown("## 🎵 고급 MIDI 생성")

        with gr.Row():
            scale_dropdown = gr.Dropdown(
                choices=["C Major", "A Minor", "D Dorian", "Chromatic"],
                value="C Major",
                label="스케일"
            )
            length_slider = gr.Slider(4, 32, 8, step=1, label="길이")
            velocity_var = gr.Slider(0, 30, 10, label="벨로시티 변화")

        piano_roll = PianoRoll(height=400)
        generate_btn = gr.Button("생성", variant="primary")

        inputs = [scale_dropdown, length_slider, velocity_var]
        generate_btn.click(generate_with_style, inputs, piano_roll)

    return demo
```

## 📊 오디오 분석 연구자용 템플릿

### `create_audio_analysis_template()`

오디오 분석 결과 시각화 템플릿을 생성합니다.

```python
def create_audio_analysis_template() -> gr.Blocks
```

**예제**:
```python
# 오디오 분석 연구자용 템플릿
demo = templates.create_audio_analysis_template()
demo.launch()
```

**기능**:
- 오디오 파일 업로드
- F0 곡선 자동 시각화
- 피아노롤 그리드 정렬
- 예시 F0 데이터 생성

### 오디오 분석 템플릿 실제 활용

```python
def real_audio_analysis_template():
    """실제 오디오 분석을 위한 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    import librosa  # 실제 오디오 분석용

    def analyze_real_audio(audio_file):
        """실제 오디오 파일 분석"""
        if not audio_file:
            return None

        # 오디오 로드
        y, sr = librosa.load(audio_file)

        # F0 추출
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, sr=sr,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7')
        )

        # 유효한 F0만 추출
        valid_f0 = f0[~np.isnan(f0)]

        # 피아노롤로 변환 (샘플링해서 노트로 표현)
        sampled_f0 = valid_f0[::len(valid_f0)//10]  # 10개 노트로 샘플링
        data = research.from_frequencies(sampled_f0)

        return data

    with gr.Blocks() as demo:
        gr.Markdown("## 📊 실제 오디오 F0 분석")

        audio_input = gr.Audio(label="분석할 오디오", type="filepath")
        piano_roll = PianoRoll(height=400)

        audio_input.change(analyze_real_audio, audio_input, piano_roll)

    return demo
```

## 📄 논문 Figure 생성용 템플릿

### `create_paper_figure_template()`

연구 논문용 깔끔한 Figure 생성 템플릿을 제공합니다.

```python
def create_paper_figure_template() -> gr.Blocks
```

**예제**:
```python
# 논문 Figure 생성용 템플릿
demo = templates.create_paper_figure_template()
demo.launch()
```

**기능**:
- 논문용 예시 데이터
- 적절한 크기 (800x300)
- 깔끔한 시각화
- 스크린샷 캡처 안내

### 논문 Figure 고급 활용

```python
def publication_ready_template():
    """출판용 고품질 Figure 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    def create_figure(title, data_type, custom_notes):
        """출판용 Figure 생성"""
        if data_type == "모델 출력 예시":
            # 모델 출력을 시뮬레이션
            notes = [(60, 0, 0.5), (64, 0.5, 0.5), (67, 1.0, 0.5), (72, 1.5, 1.0)]
            lyrics = ["Model", "Output", "Example", "Data"]
        elif data_type == "비교 분석":
            # 비교 분석용 데이터
            notes = [(60, 0, 0.3), (60, 0.5, 0.3), (64, 1.0, 0.5), (67, 1.5, 0.7)]
            lyrics = ["Baseline", "Proposed", "Method", "Results"]
        else:
            # 커스텀 데이터
            notes = eval(custom_notes) if custom_notes else [(60, 0, 1)]
            lyrics = None

        data = research.from_notes(notes, lyrics=lyrics)
        return data

    with gr.Blocks() as demo:
        gr.Markdown("## 📄 출판용 Figure 생성기")

        with gr.Row():
            title_input = gr.Textbox(
                label="Figure 제목",
                value="Model Output Comparison"
            )
            data_type = gr.Dropdown(
                choices=["모델 출력 예시", "비교 분석", "커스텀"],
                value="모델 출력 예시",
                label="데이터 타입"
            )

        custom_notes = gr.Textbox(
            label="커스텀 노트 (Python 리스트 형식)",
            value="[(60, 0, 1), (64, 1, 1)]",
            visible=False
        )

        piano_roll = PianoRoll(
            height=300,
            width=800,
            # 논문용 설정
        )

        export_btn = gr.Button("Figure 생성", variant="primary")

        # 데이터 타입에 따른 UI 변경
        def update_ui(data_type):
            return gr.update(visible=(data_type == "커스텀"))

        data_type.change(update_ui, data_type, custom_notes)

        inputs = [title_input, data_type, custom_notes]
        export_btn.click(create_figure, inputs, piano_roll)

    return demo
```

## 🎭 통합 템플릿

### `create_all_templates()`

모든 템플릿을 탭으로 보여주는 통합 데모를 생성합니다.

```python
def create_all_templates() -> gr.Blocks
```

**예제**:
```python
# 모든 템플릿을 한 번에
demo = templates.create_all_templates()
demo.launch()
```

**기능**:
- 5개 탭으로 모든 템플릿 제공
- 탭별 독립적 기능
- 전체 기능 미리보기

## 🛠️ 템플릿 커스터마이징 가이드

### 1. 기본 템플릿 확장

```python
def extend_basic_template():
    """기본 템플릿을 확장하는 방법"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll

    # 기본 템플릿에 기능 추가
    with gr.Blocks() as demo:
        gr.Markdown("# 확장된 피아노롤")

        # 기본 피아노롤
        piano_roll = PianoRoll()

        # 추가 기능들
        with gr.Row():
            tempo_slider = gr.Slider(60, 180, 120, label="템포")
            clear_btn = gr.Button("클리어")

        # 이벤트 핸들러
        def update_tempo(piano_roll_data, new_tempo):
            if piano_roll_data:
                piano_roll_data['tempo'] = new_tempo
            return piano_roll_data

        tempo_slider.change(update_tempo, [piano_roll, tempo_slider], piano_roll)

    return demo
```

### 2. 다중 모델 비교 템플릿

```python
def multi_model_comparison_template():
    """여러 모델을 비교하는 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    def generate_model_outputs(input_text):
        """여러 모델의 출력 시뮬레이션"""
        # 모델 A
        notes_a = [(60 + i, i * 0.5, 0.4) for i in range(len(input_text.split()))]
        data_a = research.from_notes(notes_a, lyrics=input_text.split())

        # 모델 B
        notes_b = [(64 + i*2, i * 0.3, 0.6) for i in range(len(input_text.split()))]
        data_b = research.from_notes(notes_b, lyrics=input_text.split())

        return data_a, data_b

    with gr.Blocks() as demo:
        gr.Markdown("## 🔬 모델 비교 분석")

        input_text = gr.Textbox(label="입력 텍스트", value="모델 비교 테스트")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### 모델 A")
                piano_roll_a = PianoRoll(height=300)

            with gr.Column():
                gr.Markdown("### 모델 B")
                piano_roll_b = PianoRoll(height=300)

        compare_btn = gr.Button("모델 비교", variant="primary")
        compare_btn.click(
            generate_model_outputs,
            inputs=input_text,
            outputs=[piano_roll_a, piano_roll_b]
        )

    return demo
```

### 3. 실시간 분석 템플릿

```python
def realtime_analysis_template():
    """실시간 분석용 템플릿"""
    import gradio as gr
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    def realtime_update(text_input, analysis_mode):
        """실시간 업데이트 처리"""
        if not text_input.strip():
            return None

        words = text_input.split()

        if analysis_mode == "음성학적":
            # 음성학적 분석 시뮬레이션
            notes = [(60 + len(word), i * 0.3, len(word) * 0.1) for i, word in enumerate(words)]
        else:
            # 음악적 분석
            notes = [(60 + i * 2, i * 0.5, 0.5) for i, word in enumerate(words)]

        return research.from_notes(notes, lyrics=words)

    with gr.Blocks() as demo:
        gr.Markdown("## ⚡ 실시간 분석")

        with gr.Row():
            text_input = gr.Textbox(
                label="실시간 입력",
                placeholder="타이핑하면 실시간으로 분석됩니다..."
            )
            analysis_mode = gr.Radio(
                choices=["음성학적", "음악적"],
                value="음성학적",
                label="분석 모드"
            )

        piano_roll = PianoRoll(height=400)

        # 실시간 업데이트 (입력 시마다 자동 실행)
        text_input.change(
            realtime_update,
            inputs=[text_input, analysis_mode],
            outputs=piano_roll
        )

        analysis_mode.change(
            realtime_update,
            inputs=[text_input, analysis_mode],
            outputs=piano_roll
        )

    return demo
```

## 💡 템플릿 활용 팁

### 1. 템플릿 선택 가이드

```python
# 연구 분야에 따른 템플릿 선택
research_areas = {
    "TTS/음성합성": "create_tts_template()",
    "MIDI 생성": "create_midi_generation_template()",
    "오디오 분석": "create_audio_analysis_template()",
    "논문 작성": "create_paper_figure_template()",
    "일반 프로토타입": "create_basic_template()"
}
```

### 2. 빠른 프로토타이핑

```python
# 1분 만에 프로토타입 만들기
from gradio_pianoroll.utils import templates

# 1. 적절한 템플릿 선택
demo = templates.create_tts_template()

# 2. 필요하면 커스터마이징
# (위의 커스터마이징 예제 참조)

# 3. 실행
demo.launch()
```

### 3. 템플릿 결합

```python
def combined_template():
    """여러 템플릿을 결합하는 방법"""
    import gradio as gr
    from gradio_pianoroll.utils import templates

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("TTS"):
                templates.create_tts_template()

            with gr.Tab("MIDI"):
                templates.create_midi_generation_template()

            with gr.Tab("분석"):
                templates.create_audio_analysis_template()

    return demo
```

## 🔗 관련 문서

- [Research 모듈](utils-research.md) - 헬퍼 함수 상세 가이드
- [Migration Guide](../getting-started/migration-guide.md) - 기존 코드 마이그레이션
- [예제 모음](../examples/) - 실제 활용 예제들
- [API 문서](../api/components.md) - 전체 API 참조