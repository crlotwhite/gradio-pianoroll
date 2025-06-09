"""
연구자용 최소 템플릿 모음

이 파일은 연구자들이 빠르게 시작할 수 있는 최소한의 템플릿들을 제공합니다.
새로운 모듈 구조(utils.research)를 사용합니다.
"""

import gradio as gr
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

# =============================================================================
# 1. 기본 피아노롤 (3줄로 만들기)
# =============================================================================

def basic_pianoroll():
    """가장 간단한 피아노롤 - 3줄로 완성"""
    with gr.Blocks() as demo:
        piano_roll = PianoRoll()
    return demo

# =============================================================================
# 2. TTS 연구자용 템플릿
# =============================================================================

def tts_researcher_template():
    """TTS 연구자를 위한 텍스트 입력 → 노트 시각화"""

    def visualize_text(text):
        """텍스트를 단어별로 노트화"""
        words = text.split()
        notes = [(60 + i % 12, i * 0.5, 0.5) for i, word in enumerate(words)]
        data = research.from_notes(notes, lyrics=words)
        return data

    with gr.Blocks() as demo:
        gr.Markdown("## 🎤 TTS 연구자용 피아노롤")

        text_input = gr.Textbox(label="입력 텍스트", placeholder="안녕하세요 피아노롤입니다")
        piano_roll = PianoRoll(height=400)

        text_input.submit(visualize_text, inputs=text_input, outputs=piano_roll)

    return demo

# =============================================================================
# 3. MIDI 생성 연구자용 템플릿
# =============================================================================

def midi_generation_template():
    """MIDI 생성 모델 출력 시각화"""

    def generate_scale(scale_type):
        """스케일 생성 예시"""
        scales = {
            "C Major": [60, 62, 64, 65, 67, 69, 71, 72],
            "A Minor": [57, 59, 60, 62, 64, 65, 67, 69],
            "G Major": [55, 57, 59, 60, 62, 64, 66, 67]
        }
        midi_notes = scales.get(scale_type, scales["C Major"])
        data = research.from_midi_numbers(midi_notes)
        return data

    with gr.Blocks() as demo:
        gr.Markdown("## 🎵 MIDI 생성 연구자용")

        scale_dropdown = gr.Dropdown(
            choices=["C Major", "A Minor", "G Major"],
            value="C Major",
            label="스케일 선택"
        )
        piano_roll = PianoRoll(height=400)

        scale_dropdown.change(generate_scale, inputs=scale_dropdown, outputs=piano_roll)

    return demo

# =============================================================================
# 4. 오디오 분석 연구자용 템플릿
# =============================================================================

def audio_analysis_template():
    """오디오 분석 결과 시각화 (F0 곡선)"""

    def show_f0_curve():
        """F0 곡선 시각화 예시"""
        import numpy as np

        # 예시 F0 데이터 생성 (사인파)
        time_points = np.linspace(0, 3, 100)
        f0_values = 220 + 50 * np.sin(2 * np.pi * 0.5 * time_points)

        # from_frequencies를 사용해서 주파수 데이터를 시각화
        data = research.from_frequencies(f0_values[:10])  # 처음 10개만 노트로 표시

        return data

    with gr.Blocks() as demo:
        gr.Markdown("## 📊 오디오 분석 연구자용")

        generate_btn = gr.Button("F0 곡선 표시", variant="primary")
        piano_roll = PianoRoll(height=400)

        generate_btn.click(show_f0_curve, outputs=piano_roll)

    return demo

# =============================================================================
# 5. 논문 Figure 생성용 템플릿
# =============================================================================

def paper_figure_template():
    """연구 논문용 깔끔한 Figure 생성"""

    # 논문용 예시 데이터
    example_notes = [(60, 0, 0.5), (64, 0.5, 0.5), (67, 1.0, 0.5), (72, 1.5, 1.0)]
    example_data = research.from_notes(example_notes, tempo=120)

    with gr.Blocks() as demo:
        gr.Markdown("## 📄 논문 Figure 생성용")

        piano_roll = PianoRoll(
            value=example_data,
            height=300,
            width=800
        )

        gr.Markdown("**사용법**: 위 피아노롤을 스크린샷으로 캡처하여 논문에 사용")

    return demo

# =============================================================================
# 실행 및 테스트
# =============================================================================

if __name__ == "__main__":
    # 모든 템플릿을 탭으로 보여주는 통합 데모
    with gr.Blocks(title="🎹 연구자용 피아노롤 템플릿들") as demo:
        gr.Markdown("""
        # 🎹 연구자용 피아노롤 템플릿

        각 탭은 서로 다른 연구 분야에 맞는 간단한 시작 템플릿을 제공합니다.
        """)

        with gr.Tabs():
            with gr.Tab("🎯 기본"):
                basic_pianoroll()

            with gr.Tab("🎤 TTS 연구"):
                tts_researcher_template()

            with gr.Tab("🎵 MIDI 생성"):
                midi_generation_template()

            with gr.Tab("📊 오디오 분석"):
                audio_analysis_template()

            with gr.Tab("📄 논문 Figure"):
                paper_figure_template()

    demo.launch()