#!/usr/bin/env python3
"""
Basic Demo: Simple PianoRoll Usage
Description: 가장 기본적인 PianoRoll 컴포넌트 사용법을 보여줍니다.
Author: gradio-pianoroll
"""

import gradio as gr
from gradio_pianoroll import PianoRoll

def convert_basic(piano_roll):
    """기본 변환 함수 - 받은 데이터를 그대로 반환"""
    print("=== Basic Convert function called ===")
    print("Received piano_roll:")
    print(piano_roll)
    print("Type:", type(piano_roll))
    return piano_roll

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll Basic Demo") as demo:
    gr.Markdown("# 🎹 PianoRoll Basic Demo")
    gr.Markdown("가장 기본적인 PianoRoll 컴포넌트 사용법을 보여줍니다. 노트를 편집하고 '변환 & 디버그' 버튼을 클릭해보세요!")

    # 기본 설정으로 PianoRoll 생성
    initial_value_basic = {
        "notes": [
            {
                "start": 80,
                "duration": 80,
                "pitch": 60,
                "velocity": 100,
                "lyric": "안녕"
            },
            {
                "start": 160,
                "duration": 160,
                "pitch": 64,
                "velocity": 90,
                "lyric": "하세요"
            }
        ],
        "tempo": 120,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4"
    }
    
    piano_roll_basic = PianoRoll(
        height=600,
        width=1000,
        value=initial_value_basic,
        elem_id="piano_roll_basic"
    )

    with gr.Row():
        btn_basic = gr.Button("🔄 변환 & 디버그", variant="primary")

    output_json_basic = gr.JSON(label="Piano Roll Data")

    # 이벤트 연결
    btn_basic.click(
        fn=convert_basic,
        inputs=piano_roll_basic,
        outputs=output_json_basic,
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch() 