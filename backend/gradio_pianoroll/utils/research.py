"""
연구자를 위한 헬퍼 함수 라이브러리

이 모듈은 연구자들이 피아노롤 컴포넌트를 쉽게 사용할 수 있도록
복잡한 작업들을 간단한 함수 호출로 처리할 수 있게 해줍니다.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import gradio as gr

from ..timing_utils import generate_note_id
from ..data_models import PianoRollData, Note, clean_piano_roll_data

# =============================================================================
# 1. 빠른 생성 함수들 (Quick Creation)
# =============================================================================


def from_notes(
    notes: List[Tuple[int, float, float]],
    tempo: int = 120,
    lyrics: Optional[List[str]] = None,
) -> PianoRollData:
    """
    간단한 노트 리스트에서 피아노롤 데이터 생성

    Args:
        notes: (pitch, start_time_sec, duration_sec) 튜플들의 리스트
        tempo: BPM (기본값: 120)
        lyrics: 가사 리스트 (선택사항)

    Returns:
        피아노롤 데이터 딕셔너리

    Example:
        notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]  # C-E-G 코드
        data = from_notes(notes, tempo=120)
    """
    pixels_per_beat = 80

    piano_roll_notes = []
    for i, (pitch, start_sec, duration_sec) in enumerate(notes):
        # 초를 픽셀로 변환
        start_pixels = start_sec * (tempo / 60) * pixels_per_beat
        duration_pixels = duration_sec * (tempo / 60) * pixels_per_beat

        note_data = {
            "id": generate_note_id(),
            "start": start_pixels,
            "duration": duration_pixels,
            "pitch": pitch,
            "velocity": 100,
        }

        # 가사가 있으면 추가
        if lyrics and i < len(lyrics):
            note_data["lyric"] = lyrics[i]

        piano_roll_notes.append(note_data)

    result: PianoRollData = {
        "notes": piano_roll_notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    return clean_piano_roll_data(result)


def from_midi_numbers(
    midi_notes: List[int],
    durations: Optional[List[float]] = None,
    start_times: Optional[List[float]] = None,
    tempo: int = 120,
) -> PianoRollData:
    """
    MIDI 노트 번호 리스트에서 피아노롤 생성

    Args:
        midi_notes: MIDI 노트 번호들 (0-127)
        durations: 각 노트의 길이(초). None이면 모두 1초
        start_times: 각 노트의 시작 시간(초). None이면 순차적 배치
        tempo: BPM

    Example:
        # C major scale
        midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
        data = from_midi_numbers(midi_notes)
    """
    if durations is None:
        durations = [1.0] * len(midi_notes)
    if start_times is None:
        start_times = [i * 1.0 for i in range(len(midi_notes))]

    notes = list(zip(midi_notes, start_times, durations))
    return from_notes(notes, tempo)


def from_frequencies(
    frequencies: List[float],
    durations: Optional[List[float]] = None,
    start_times: Optional[List[float]] = None,
    tempo: int = 120,
) -> PianoRollData:
    """
    주파수(Hz) 리스트에서 피아노롤 생성

    Args:
        frequencies: 주파수 값들 (Hz)
        durations: 각 노트의 길이(초)
        start_times: 각 노트의 시작 시간(초)
        tempo: BPM

    Example:
        # A4, B4, C5
        frequencies = [440, 493.88, 523.25]
        data = from_frequencies(frequencies)
    """
    # 주파수를 MIDI 노트 번호로 변환
    midi_notes = [int(round(69 + 12 * np.log2(f / 440))) for f in frequencies]
    return from_midi_numbers(midi_notes, durations, start_times, tempo)


# =============================================================================
# 2. 모델 출력 변환 함수들 (Model Output Conversion)
# =============================================================================


def from_tts_output(
    text: str,
    alignment: List[Tuple[str, float, float]],
    f0_data: Optional[List[float]] = None,
    tempo: int = 120,
) -> Dict:
    """
    TTS 모델의 정렬 결과를 피아노롤로 변환

    Args:
        text: 원본 텍스트
        alignment: (단어/음소, 시작시간, 종료시간) 튜플들
        f0_data: F0 곡선 데이터 (선택사항)
        tempo: BPM

    Returns:
        피아노롤 데이터

    Example:
        alignment = [("안", 0.0, 0.5), ("녕", 0.5, 1.0)]
        f0_data = [220, 230, 240, 235, 225]  # 5개 프레임의 F0
        data = from_tts_output("안녕", alignment, f0_data)
    """
    pixels_per_beat = 80
    notes = []

    for word, start_time, end_time in alignment:
        duration = end_time - start_time

        # F0 데이터가 있으면 해당 구간의 평균 F0를 피치로 사용
        if f0_data:
            # 간단한 구간 매핑 (실제로는 더 정교한 매핑 필요)
            f0_segment_start = int(start_time * len(f0_data) / alignment[-1][2])
            f0_segment_end = int(end_time * len(f0_data) / alignment[-1][2])
            segment_f0 = f0_data[f0_segment_start:f0_segment_end]
            avg_f0 = np.mean([f for f in segment_f0 if f > 0]) if segment_f0 else 220
            pitch = int(round(69 + 12 * np.log2(avg_f0 / 440)))
        else:
            pitch = 60  # 기본값: C4

        note = {
            "id": generate_note_id(),
            "start": start_time * (tempo / 60) * pixels_per_beat,
            "duration": duration * (tempo / 60) * pixels_per_beat,
            "pitch": max(0, min(127, pitch)),  # MIDI 범위로 제한
            "velocity": 100,
            "lyric": word,
        }
        notes.append(note)

    result = {
        "notes": notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }

    # F0 곡선 데이터 추가
    if f0_data:
        result["line_data"] = _create_f0_line_data(
            f0_data, alignment[-1][2], tempo, pixels_per_beat
        )

    return result


def from_midi_generation(generated_sequence: List[Dict], tempo: int = 120) -> Dict:
    """
    MIDI 생성 모델 출력을 피아노롤로 변환

    Args:
        generated_sequence: [{"pitch": int, "start": float, "duration": float, "velocity": int}, ...]
        tempo: BPM

    Example:
        sequence = [
            {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100},
            {"pitch": 64, "start": 0.5, "duration": 0.5, "velocity": 90}
        ]
        data = from_midi_generation(sequence)
    """
    pixels_per_beat = 80
    notes = []

    for note_data in generated_sequence:
        note = {
            "id": generate_note_id(),
            "start": note_data["start"] * (tempo / 60) * pixels_per_beat,
            "duration": note_data["duration"] * (tempo / 60) * pixels_per_beat,
            "pitch": note_data["pitch"],
            "velocity": note_data.get("velocity", 100),
        }

        # 가사나 추가 정보가 있으면 포함
        if "lyric" in note_data:
            note["lyric"] = note_data["lyric"]
        if "phoneme" in note_data:
            note["phoneme"] = note_data["phoneme"]

        notes.append(note)

    return {
        "notes": notes,
        "tempo": tempo,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4",
        "pixelsPerBeat": pixels_per_beat,
    }


def _create_f0_line_data(
    f0_values: List[float], total_duration: float, tempo: int, pixels_per_beat: int
) -> Dict:
    """F0 데이터를 LineLayer 형식으로 변환"""
    data_points = []

    for i, f0 in enumerate(f0_values):
        if f0 > 0:  # 유효한 F0만
            time_sec = (i / len(f0_values)) * total_duration
            x_pixel = time_sec * (tempo / 60) * pixels_per_beat

            # F0를 MIDI 노트로 변환 후 Y 좌표로 변환
            midi_note = 69 + 12 * np.log2(f0 / 440)
            y_pixel = (127 - midi_note) * 20  # 20은 NOTE_HEIGHT

            data_points.append({"x": x_pixel, "y": y_pixel})

    return {
        "f0_curve": {
            "color": "#FF6B6B",
            "lineWidth": 2,
            "yMin": 0,
            "yMax": 2560,
            "position": "overlay",
            "renderMode": "piano_grid",
            "data": data_points,
        }
    }


# =============================================================================
# 3. 템플릿 생성 함수들 (Template Creation)
# =============================================================================


def create_pianoroll_with_data(data: Dict, **component_kwargs) -> gr.Blocks:
    """
    데이터로부터 PianoRoll 컴포넌트가 포함된 Gradio 데모 생성

    Args:
        data: 피아노롤 데이터
        **component_kwargs: PianoRoll 컴포넌트에 전달할 추가 인자들

    Returns:
        Gradio Blocks 데모
    """
    import gradio as gr
    from ..pianoroll import PianoRoll

    with gr.Blocks() as demo:
        piano_roll = PianoRoll(value=data, **component_kwargs)

    return demo


def quick_demo(
    notes: List[Tuple[int, float, float]],
    title: str = "Quick Piano Roll Demo",
    tempo: int = 120,
    **component_kwargs,
) -> gr.Blocks:
    """
    3줄로 피아노롤 데모 만들기

    Args:
        notes: (pitch, start_time, duration) 노트 리스트
        title: 데모 제목
        tempo: BPM
        **component_kwargs: PianoRoll 컴포넌트에 전달할 추가 인자들

    Returns:
        Gradio Blocks 데모

    Example:
        notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
        demo = quick_demo(notes, "내 TTS 모델 결과")
        demo.launch()
    """
    import gradio as gr
    from ..pianoroll import PianoRoll

    data = from_notes(notes, tempo)

    with gr.Blocks(title=title) as demo:
        gr.Markdown(f"# {title}")
        piano_roll = PianoRoll(value=data, height=400, **component_kwargs)
        gr.JSON(label="피아노롤 데이터", value=data)

    return demo


# =============================================================================
# 4. 분석 도구들 (Analysis Tools)
# =============================================================================


def analyze_notes(piano_roll_data: Dict) -> Dict:
    """피아노롤에서 노트 통계 추출"""
    notes = piano_roll_data.get("notes", [])

    if not notes:
        return {"error": "노트 데이터가 없습니다"}

    pitches = [note["pitch"] for note in notes]
    velocities = [note["velocity"] for note in notes]
    durations = [note["duration"] for note in notes]

    pixels_per_beat = piano_roll_data.get("pixelsPerBeat", 80)
    tempo = piano_roll_data.get("tempo", 120)

    # 픽셀을 초로 변환
    durations_sec = [d / pixels_per_beat * 60 / tempo for d in durations]

    return {
        "총_노트_수": len(notes),
        "음역대": {
            "최저음": min(pitches),
            "최고음": max(pitches),
            "음역": max(pitches) - min(pitches),
        },
        "평균_피치": round(np.mean(pitches), 1),
        "평균_벨로시티": round(np.mean(velocities), 1),
        "평균_노트_길이_초": round(np.mean(durations_sec), 2),
        "총_재생시간_초": round(
            max([n["start"] + n["duration"] for n in notes])
            / pixels_per_beat
            * 60
            / tempo,
            2,
        ),
        "리듬_분석": {
            "최단_노트_초": round(min(durations_sec), 3),
            "최장_노트_초": round(max(durations_sec), 3),
            "표준편차": round(np.std(durations_sec), 3),
        },
    }


# =============================================================================
# 5. 자동 분석 함수
# =============================================================================


def auto_analyze(
    model_output_data: Union[List, Dict], output_type: str = "auto"
) -> Dict:
    """
    모델 출력을 자동으로 분석해서 피아노롤 형식으로 변환

    Args:
        model_output_data: 모델 출력 데이터
        output_type: "auto", "tts", "midi_generation", "frequencies"

    Returns:
        피아노롤 데이터
    """
    if output_type == "auto":
        # 데이터 형식을 보고 자동 감지
        if isinstance(model_output_data, list) and len(model_output_data) > 0:
            if (
                isinstance(model_output_data[0], (tuple, list))
                and len(model_output_data[0]) >= 3
            ):
                # (pitch, time, duration) 형식으로 추정
                return from_notes(model_output_data)
            elif (
                isinstance(model_output_data[0], dict)
                and "pitch" in model_output_data[0]
            ):
                # MIDI 생성 모델 출력으로 추정
                return from_midi_generation(model_output_data)

    elif output_type == "tts":
        # TTS 정렬 데이터로 처리
        return from_tts_output("", model_output_data)

    elif output_type == "midi_generation":
        return from_midi_generation(model_output_data)

    elif output_type == "frequencies":
        return from_frequencies(model_output_data)

    # 기본값: 빈 피아노롤 반환
    return from_notes([])
