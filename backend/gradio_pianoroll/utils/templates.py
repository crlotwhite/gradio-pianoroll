"""
연구자용 템플릿 생성 모듈

이 모듈은 연구자들이 빠르게 프로토타입을 만들 수 있도록
다양한 분야별 템플릿을 제공합니다.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    import gradio as gr

from .research import from_notes, from_midi_numbers, from_frequencies


def create_basic_template() -> gr.Blocks:
    """기본 피아노롤 템플릿 (3줄로 만들기)"""
    import gradio as gr
    from ..pianoroll import PianoRoll

    with gr.Blocks() as demo:
        piano_roll = PianoRoll()
        piano_roll.change(
            lambda x: f"Notes: {len(x.get('notes', []))}",
            inputs=piano_roll,
            outputs=gr.Textbox(),
        )
    return demo


def create_tts_template() -> gr.Blocks:
    """TTS 연구자용 템플릿"""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def visualize_tts_output(text_input):
        """TTS 모델 출력을 피아노롤에 표시"""
        words = text_input.split()
        notes = []
        for i, word in enumerate(words):
            notes.append(
                {
                    "id": f"note_{i}",
                    "start": i * 160,
                    "duration": 160,
                    "pitch": 60 + (i % 12),
                    "velocity": 100,
                    "lyric": word,
                }
            )
        return {"notes": notes, "tempo": 120}

    with gr.Blocks(title="TTS 연구자용 피아노롤") as demo:
        gr.Markdown("## 🎤 TTS 모델 결과 시각화")

        with gr.Row():
            text_input = gr.Textbox(
                label="입력 텍스트", placeholder="안녕하세요 피아노롤입니다"
            )
            generate_btn = gr.Button("생성", variant="primary")

        piano_roll = PianoRoll(height=400)
        generate_btn.click(visualize_tts_output, inputs=text_input, outputs=piano_roll)

    return demo


def create_midi_generation_template() -> gr.Blocks:
    """MIDI 생성 연구자용 템플릿"""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def generate_midi_sequence(seed_notes, length):
        """MIDI 생성 모델 호출 (예시)"""
        notes = []
        scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale

        for i in range(length):
            notes.append(
                {
                    "id": f"generated_{i}",
                    "start": i * 80,
                    "duration": 80,
                    "pitch": scale[i % len(scale)],
                    "velocity": np.random.randint(80, 120),
                }
            )

        return {"notes": notes, "tempo": 120}

    with gr.Blocks(title="MIDI 생성 연구자용") as demo:
        gr.Markdown("## 🎵 MIDI 생성 모델 데모")

        with gr.Row():
            length_slider = gr.Slider(4, 32, value=8, step=1, label="생성할 노트 수")
            generate_btn = gr.Button("생성", variant="primary")

        piano_roll = PianoRoll(height=400)
        generate_btn.click(
            lambda length: generate_midi_sequence([], length),
            inputs=length_slider,
            outputs=piano_roll,
        )

    return demo


def create_audio_analysis_template() -> gr.Blocks:
    """오디오 분석 연구자용 템플릿"""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def analyze_audio_simple(audio_file):
        """오디오 파일을 분석해서 F0 곡선 표시"""
        if not audio_file:
            return None

        # 예시 F0 데이터 생성
        time_points = np.linspace(0, 3, 100)  # 3초간
        f0_values = 220 + 50 * np.sin(2 * np.pi * 0.5 * time_points)  # 간단한 F0 곡선

        # F0 데이터를 라인 데이터로 변환
        line_data = {
            "f0_curve": {
                "color": "#FF6B6B",
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,
                "position": "overlay",
                "renderMode": "piano_grid",
                "data": [
                    {"x": t * 80, "y": (127 - (69 + 12 * np.log2(f / 440))) * 20}
                    for t, f in zip(time_points, f0_values)
                ],
            }
        }

        return {"notes": [], "tempo": 120, "line_data": line_data}

    with gr.Blocks(title="오디오 분석 연구자용") as demo:
        gr.Markdown("## 📊 오디오 F0 분석 시각화")

        audio_input = gr.Audio(label="분석할 오디오 파일", type="filepath")
        piano_roll = PianoRoll(height=400)

        audio_input.change(analyze_audio_simple, inputs=audio_input, outputs=piano_roll)

    return demo


def create_paper_figure_template() -> gr.Blocks:
    """연구 논문용 Figure 생성 템플릿"""
    import gradio as gr
    from ..pianoroll import PianoRoll

    def create_paper_figure(title, notes_data):
        """논문용 깔끔한 피아노롤 Figure"""
        return {"notes": notes_data.get("notes", []), "tempo": 120, "title": title}

    with gr.Blocks(title="논문 Figure 생성용") as demo:
        gr.Markdown("## 📄 연구 논문용 피아노롤 Figure")

        with gr.Row():
            title_input = gr.Textbox(
                label="Figure 제목", value="Model Output Visualization"
            )
            export_btn = gr.Button("PNG로 내보내기")

        piano_roll = PianoRoll(
            height=300,
            width=800,
            value={
                "notes": [
                    {
                        "id": "1",
                        "start": 0,
                        "duration": 160,
                        "pitch": 60,
                        "velocity": 100,
                        "lyric": "Example",
                    },
                    {
                        "id": "2",
                        "start": 160,
                        "duration": 160,
                        "pitch": 64,
                        "velocity": 100,
                        "lyric": "Data",
                    },
                ]
            },
        )

    return demo


def create_all_templates() -> gr.Blocks:
    """모든 템플릿을 탭으로 보여주는 통합 데모"""
    import gradio as gr

    with gr.Blocks(title="🎹 연구자용 피아노롤 템플릿들") as demo:
        gr.Markdown(
            """
        # 🎹 연구자용 피아노롤 템플릿

        각 탭은 서로 다른 연구 분야에 맞는 간단한 시작 템플릿을 제공합니다.
        필요한 템플릿의 코드를 복사해서 사용하세요!
        """
        )

        with gr.Tabs():
            with gr.Tab("🎯 기본"):
                create_basic_template()

            with gr.Tab("🎤 TTS 연구"):
                create_tts_template()

            with gr.Tab("🎵 MIDI 생성"):
                create_midi_generation_template()

            with gr.Tab("📊 오디오 분석"):
                create_audio_analysis_template()

            with gr.Tab("📄 논문 Figure"):
                create_paper_figure_template()

    return demo
