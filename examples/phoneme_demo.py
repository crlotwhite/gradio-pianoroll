#!/usr/bin/env python3
"""
Phoneme Demo: Korean G2P (Grapheme-to-Phoneme) Conversion
Description: 한국어 가사를 음소로 변환하는 G2P 기능과 음소 매핑 관리를 보여줍니다.
Author: gradio-pianoroll
"""

import gradio as gr
from gradio_pianoroll import PianoRoll

# 사용자 정의 음소 매핑 (전역 상태)
user_phoneme_map = {}

def initialize_phoneme_map():
    """기본 한국어 음소 매핑으로 초기화"""
    global user_phoneme_map
    user_phoneme_map = {
        '가': 'g a',
        '나': 'n a',
        '다': 'd a',
        '라': 'l aa',
        '마': 'm a',
        '바': 'b a',
        '사': 's a',
        '아': 'aa',
        '자': 'j a',
        '차': 'ch a',
        '카': 'k a',
        '타': 't a',
        '파': 'p a',
        '하': 'h a',
        '도': 'd o',
        '레': 'l e',
        '미': 'm i',
        '솔': 's o l',
        '시': 's i',
        '안녕': 'aa n ny eo ng',
        '하세요': 'h a s e y o',
        '노래': 'n o l ae',
        '사랑': 's a l a ng',
        '행복': 'h ae ng b o k',
        '음악': 'eu m a k',
        '피아노': 'p i a n o'
    }

# 프로그램 시작 시 음소 매핑 초기화
initialize_phoneme_map()

def get_phoneme_mapping_for_dataframe():
    """DataFrame용 음소 매핑 리스트 반환"""
    global user_phoneme_map
    return [[k, v] for k, v in user_phoneme_map.items()]

def add_phoneme_mapping(lyric: str, phoneme: str):
    """새로운 음소 매핑 추가"""
    global user_phoneme_map
    user_phoneme_map[lyric.strip()] = phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"'{lyric}' → '{phoneme}' 매핑이 추가되었습니다."

def reset_phoneme_mapping():
    """음소 매핑을 기본값으로 재설정"""
    initialize_phoneme_map()
    return get_phoneme_mapping_for_dataframe(), "음소 매핑이 기본값으로 재설정되었습니다."

def mock_g2p(text: str) -> str:
    """
    커스텀 매핑을 사용한 한국어 G2P 함수
    """
    global user_phoneme_map

    # 텍스트를 소문자로 변환하고 공백 제거
    text = text.strip()

    # 커스텀 매핑에서 찾기
    if text in user_phoneme_map:
        return user_phoneme_map[text]

    # 찾지 못하면 각 글자별로 처리
    result = []
    for char in text:
        if char in user_phoneme_map:
            result.append(user_phoneme_map[char])
        else:
            # 알 수 없는 글자는 그대로 반환
            result.append(char)

    return ' '.join(result)

def auto_generate_missing_phonemes(piano_roll_data):
    """가사는 있지만 음소가 없는 노트에 대해 자동으로 음소 생성"""
    if not piano_roll_data or 'notes' not in piano_roll_data:
        return piano_roll_data, "피아노롤 데이터가 없습니다."

    # 현재 노트 복사
    notes = piano_roll_data['notes'].copy()
    updated_notes = []
    changes_made = 0

    for note in notes:
        note_copy = note.copy()

        # 가사가 있으면 처리
        lyric = note.get('lyric', '').strip()
        current_phoneme = note.get('phoneme', '').strip()

        if lyric:
            # G2P 실행하여 새 음소 생성
            new_phoneme = mock_g2p(lyric)

            # 기존 음소와 다르거나 없으면 업데이트
            if not current_phoneme or current_phoneme != new_phoneme:
                note_copy['phoneme'] = new_phoneme
                changes_made += 1
                print(f"   - G2P 적용: '{lyric}' -> '{new_phoneme}'")
        else:
            # 가사가 없으면 음소 제거
            if current_phoneme:
                note_copy['phoneme'] = None
                changes_made += 1
                print(f"   - 음소 제거 (가사 없음)")

        updated_notes.append(note_copy)

    if changes_made > 0:
        # 업데이트된 피아노롤 데이터 반환
        updated_piano_roll = piano_roll_data.copy()
        updated_piano_roll['notes'] = updated_notes
        return updated_piano_roll, f"자동 G2P 완료: {changes_made}개 노트 업데이트됨"
    else:
        return piano_roll_data, "G2P를 적용할 변경사항이 없습니다."

def auto_generate_all_phonemes(piano_roll):
    """모든 가사에 대해 자동으로 음소 생성"""
    print("=== 모든 음소 자동 생성 ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    updated_count = 0
    for note in notes:
        lyric = note.get('lyric')
        if lyric:
            phoneme = mock_g2p(lyric)
            note['phoneme'] = phoneme
            updated_count += 1
            print(f"자동 생성: '{lyric}' -> '{phoneme}'")

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, f"{updated_count}개 노트의 음소가 자동 생성되었습니다"

def clear_all_phonemes(piano_roll):
    """모든 노트의 음소를 지우기"""
    print("=== 모든 음소 지우기 ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "피아노롤 데이터가 없습니다."

    notes = piano_roll['notes'].copy()

    for note in notes:
        note['phoneme'] = None

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, "모든 음소가 지워졌습니다."

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll Phoneme Demo") as demo:
    gr.Markdown("# 🗣️ PianoRoll Phoneme Demo")
    gr.Markdown("가사를 수정하면 G2P(Grapheme-to-Phoneme)가 자동으로 실행되어 음소를 표시합니다. 수동으로 음소를 편집할 수도 있습니다.")

    with gr.Row():
        with gr.Column(scale=3):
            # 음소 초기값
            initial_value_phoneme = {
                "notes": [
                    {
                        "id": "note_0",
                        "start": 0,
                        "duration": 160,
                        "pitch": 60,  # C4
                        "velocity": 100,
                        "lyric": "안녕",
                        "phoneme": "aa n ny eo ng"  # 미리 설정된 음소
                    },
                    {
                        "id": "note_1",
                        "start": 160,
                        "duration": 160,
                        "pitch": 62,  # D4
                        "velocity": 100,
                        "lyric": "하세요",
                        "phoneme": "h a s e y o"
                    },
                    {
                        "id": "note_2",
                        "start": 320,
                        "duration": 160,
                        "pitch": 64,  # E4
                        "velocity": 100,
                        "lyric": "음악",
                        "phoneme": "eu m a k"
                    },
                    {
                        "id": "note_3",
                        "start": 480,
                        "duration": 160,
                        "pitch": 65,  # F4
                        "velocity": 100,
                        "lyric": "피아노"
                    }
                ],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4"
            }
            piano_roll_phoneme = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_phoneme,
                elem_id="piano_roll_phoneme"
            )

        with gr.Column(scale=1):
            gr.Markdown("### 📝 음소 매핑 관리")

            # 현재 매핑 리스트 표시
            phoneme_mapping_dataframe = gr.Dataframe(
                headers=["가사", "음소"],
                datatype=["str", "str"],
                value=get_phoneme_mapping_for_dataframe(),
                label="현재 음소 매핑",
                interactive=True,
                wrap=True
            )

            gr.Markdown("#### ➕ 새 매핑 추가")
            with gr.Row():
                add_lyric_input = gr.Textbox(
                    label="가사",
                    placeholder="예: 라",
                    scale=1
                )
                add_phoneme_input = gr.Textbox(
                    label="음소",
                    placeholder="예: l aa",
                    scale=1
                )
            btn_add_mapping = gr.Button("➕ 매핑 추가", variant="primary", size="sm")

            gr.Markdown("### 🔧 일괄 작업")
            with gr.Row():
                btn_auto_generate = gr.Button("🤖 모든 음소 자동 생성", variant="primary")
                btn_clear_phonemes = gr.Button("🗑️ 모든 음소 지우기", variant="secondary")

            btn_reset_mapping = gr.Button("🔄 매핑을 기본값으로 재설정", variant="secondary")

    with gr.Row():
        phoneme_status_text = gr.Textbox(label="상태", interactive=False)

    output_json_phoneme = gr.JSON(label="음소 데이터")

    # 음소 탭 이벤트 처리

    # 매핑 추가
    btn_add_mapping.click(
        fn=add_phoneme_mapping,
        inputs=[add_lyric_input, add_phoneme_input],
        outputs=[phoneme_mapping_dataframe, phoneme_status_text],
        show_progress=False
    ).then(
        fn=lambda: ["", ""],  # 입력 필드 재설정
        outputs=[add_lyric_input, add_phoneme_input]
    )

    # 재설정
    btn_reset_mapping.click(
        fn=reset_phoneme_mapping,
        outputs=[phoneme_mapping_dataframe, phoneme_status_text],
        show_progress=False
    )

    # 가사 입력 시 자동 G2P 처리
    def handle_phoneme_input_event(piano_roll_data):
        """가사 입력 이벤트 처리 - 피아노롤 변경 감지 및 음소 생성"""
        print("🗣️ 음소 탭 - 입력 이벤트 트리거")
        print(f"   - 피아노롤 데이터: {type(piano_roll_data)}")

        if not piano_roll_data or 'notes' not in piano_roll_data:
            return piano_roll_data, "피아노롤 데이터가 없습니다."

        return auto_generate_missing_phonemes(piano_roll_data)

    piano_roll_phoneme.input(
        fn=handle_phoneme_input_event,
        inputs=[piano_roll_phoneme],
        outputs=[piano_roll_phoneme, phoneme_status_text],
        show_progress=False
    )

    # 노트 변경 시 자동 음소 생성
    def handle_phoneme_change_event(piano_roll_data):
        """노트 변경 시 자동 음소 생성 처리"""
        return auto_generate_missing_phonemes(piano_roll_data)

    piano_roll_phoneme.change(
        fn=handle_phoneme_change_event,
        inputs=[piano_roll_phoneme],
        outputs=[piano_roll_phoneme, phoneme_status_text],
        show_progress=False
    )

    # 자동 음소 생성 (수동 버튼)
    btn_auto_generate.click(
        fn=auto_generate_all_phonemes,
        inputs=[piano_roll_phoneme],
        outputs=[piano_roll_phoneme, phoneme_status_text],
        show_progress=True
    )

    # 모든 음소 지우기
    btn_clear_phonemes.click(
        fn=clear_all_phonemes,
        inputs=[piano_roll_phoneme],
        outputs=[piano_roll_phoneme, phoneme_status_text],
        show_progress=False
    )

    # 노트 변경 시 JSON 출력 업데이트 (자동 음소 처리와 별도)
    def update_json_output(piano_roll_data):
        return piano_roll_data

    piano_roll_phoneme.change(
        fn=update_json_output,
        inputs=[piano_roll_phoneme],
        outputs=[output_json_phoneme],
        show_progress=False
    )

    # 재생 이벤트 로그
    def log_phoneme_play_event(event_data=None):
        print("🗣️ 음소 재생 이벤트 트리거:", event_data)
        return f"재생 시작: {event_data if event_data else '재생 중'}"

    def log_phoneme_pause_event(event_data=None):
        print("🗣️ 음소 일시정지 이벤트 트리거:", event_data)
        return f"일시정지: {event_data if event_data else '일시정지됨'}"

    def log_phoneme_stop_event(event_data=None):
        print("🗣️ 음소 정지 이벤트 트리거:", event_data)
        return f"정지: {event_data if event_data else '정지됨'}"

    piano_roll_phoneme.play(log_phoneme_play_event, outputs=phoneme_status_text)
    piano_roll_phoneme.pause(log_phoneme_pause_event, outputs=phoneme_status_text)
    piano_roll_phoneme.stop(log_phoneme_stop_event, outputs=phoneme_status_text)

if __name__ == "__main__":
    demo.launch() 