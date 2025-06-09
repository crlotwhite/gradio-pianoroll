#!/usr/bin/env python3
"""
F0 Analysis Demo: Fundamental Frequency Analysis
Description: 오디오 파일에서 F0(기본 주파수)를 추출하여 PianoRoll에 시각화하는 기능을 보여줍니다.
Author: gradio-pianoroll
"""

import gradio as gr
import numpy as np
import tempfile
import os
import wave
from gradio_pianoroll import PianoRoll

# librosa 추가 임포트
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ librosa 사용 가능")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa가 설치되지 않음. F0 분석 기능이 제한됩니다.")

def extract_f0_from_audio(audio_file_path, f0_method="pyin"):
    """
    오디오 파일에서 F0(기본 주파수) 추출
    """
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 F0 분석을 수행할 수 없습니다"

    try:
        print(f"🎵 F0 추출 시작: {audio_file_path}")

        # 오디오 로드
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - 샘플레이트: {sr}Hz")
        print(f"   - 길이: {len(y)/sr:.2f}초")

        # F0 추출 방법 선택
        if f0_method == "pyin":
            # PYIN 알고리즘 사용 (더 정확하지만 느림)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                sr=sr,
                fmin=librosa.note_to_hz('C2'),  # 약 65Hz
                fmax=librosa.note_to_hz('C7')   # 약 2093Hz
            )
        else:
            # 기본 피치 추출
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            f0 = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                f0.append(pitch if pitch > 0 else np.nan)
            f0 = np.array(f0)

        # 시간 축 계산
        hop_length = 512  # librosa 기본값
        frame_times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)

        # NaN 값 처리 및 스무딩
        valid_indices = ~np.isnan(f0)
        if np.sum(valid_indices) == 0:
            return None, "유효한 F0 값을 찾을 수 없습니다"

        # 유효한 F0 값만 사용
        valid_f0 = f0[valid_indices]
        valid_times = frame_times[valid_indices]

        print(f"   - 추출된 F0 포인트: {len(valid_f0)}")
        print(f"   - F0 범위: {np.min(valid_f0):.1f}Hz ~ {np.max(valid_f0):.1f}Hz")

        # voiced/unvoiced 정보도 함께 반환
        result_data = {
            'times': frame_times,  # 전체 시간 축
            'f0_values': f0,  # 전체 F0 (NaN 포함)
            'valid_times': valid_times,  # 유효한 시간만
            'valid_f0_values': valid_f0,  # 유효한 F0만
            'sample_rate': sr,
            'duration': len(y) / sr,
            'hop_length': hop_length
        }

        # PYIN에서 voiced 정보 추가
        if f0_method == "pyin" and 'voiced_flag' in locals() and 'voiced_probs' in locals():
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs
        else:
            # 다른 방법의 경우 F0 존재 여부로 voiced 추정
            voiced_flag = ~np.isnan(f0)
            voiced_probs = voiced_flag.astype(float)
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs

        return result_data, "F0 추출 완료"

    except Exception as e:
        print(f"❌ F0 추출 오류: {e}")
        return None, f"F0 추출 오류: {str(e)}"

def create_f0_line_data(f0_data, tempo=120, pixelsPerBeat=80):
    """
    F0 데이터를 LineLayer용 line_data 형식으로 변환
    F0 곡선이 피아노롤 그리드의 정확한 피치 위치에 표시되도록 함
    """
    if not f0_data:
        return None

    try:
        times = f0_data['times']
        f0_values = f0_data['f0_values']

        # 피아노롤 상수 (GridComponent와 동일)
        NOTE_HEIGHT = 20
        TOTAL_NOTES = 128

        def hz_to_midi(frequency):
            """주파수(Hz)를 MIDI 노트 번호로 변환"""
            if frequency <= 0:
                return 0
            return 69 + 12 * np.log2(frequency / 440.0)

        def midi_to_y_coordinate(midi_note):
            """MIDI 노트 번호를 피아노롤 Y 좌표로 변환 (GridComponent와 동일)"""
            return (TOTAL_NOTES - 1 - midi_note) * NOTE_HEIGHT + NOTE_HEIGHT/2

        # 데이터 포인트 생성 (피아노롤 좌표계 사용)
        data_points = []
        valid_f0_values = []

        for time, f0 in zip(times, f0_values):
            if not np.isnan(f0) and f0 > 0:
                # Hz를 MIDI로 변환
                midi_note = hz_to_midi(f0)

                # MIDI 범위 체크 (0-127)
                if 0 <= midi_note <= 127:
                    # 시간(초)을 픽셀 X 좌표로 변환
                    x_pixel = time * (tempo / 60) * pixelsPerBeat

                    # MIDI를 피아노롤 Y 좌표로 변환
                    y_pixel = midi_to_y_coordinate(midi_note)

                    data_points.append({
                        "x": float(x_pixel),
                        "y": float(y_pixel)
                    })
                    valid_f0_values.append(f0)

        if not data_points:
            print("⚠️ 유효한 F0 데이터 포인트가 없습니다")
            return None

        # F0 값 범위 정보 (표시용)
        min_f0 = float(np.min(valid_f0_values))
        max_f0 = float(np.max(valid_f0_values))
        min_midi = hz_to_midi(min_f0)
        max_midi = hz_to_midi(max_f0)

        # Y 범위를 전체 피아노롤 범위로 설정
        y_min = 0
        y_max = TOTAL_NOTES * NOTE_HEIGHT

        line_data = {
            "f0_curve": {
                "color": "#FF6B6B",  # 빨간색
                "lineWidth": 3,
                "yMin": y_min,
                "yMax": y_max,
                "position": "overlay",  # 그리드 위에 오버레이
                "renderMode": "piano_grid",  # F0 전용 렌더링 모드
                "visible": True,
                "opacity": 0.8,
                "data": data_points,
                # 메타데이터
                "dataType": "f0",
                "unit": "Hz",
                "originalRange": {
                    "minHz": min_f0,
                    "maxHz": max_f0,
                    "minMidi": min_midi,
                    "maxMidi": max_midi
                }
            }
        }

        print(f"📊 F0 LineData 생성됨: {len(data_points)} 포인트")
        print(f"   - F0 범위: {min_f0:.1f}Hz ~ {max_f0:.1f}Hz")
        print(f"   - MIDI 범위: {min_midi:.1f} ~ {max_midi:.1f}")
        print(f"   - 렌더링 모드: 피아노롤 그리드 정렬")

        return line_data

    except Exception as e:
        print(f"❌ F0 LineData 생성 오류: {e}")
        return None

def analyze_audio_f0(piano_roll, audio_file, f0_method="pyin"):
    """업로드된 오디오 파일에서 F0를 추출하고 피아노롤에 표시"""
    print("=== F0 분석 시작 ===")
    print(f"오디오 파일: {audio_file}")
    print(f"F0 방법: {f0_method}")

    if not audio_file:
        return piano_roll, "오디오 파일을 업로드해 주세요.", None

    if not LIBROSA_AVAILABLE:
        return piano_roll, "librosa가 설치되지 않아 F0 분석을 수행할 수 없습니다. 'pip install librosa'로 설치해 주세요.", None

    try:
        # F0 추출
        f0_data, f0_status = extract_f0_from_audio(audio_file, f0_method)

        if f0_data is None:
            return piano_roll, f"F0 분석 실패: {f0_status}", audio_file

        # 피아노롤 데이터 업데이트
        updated_piano_roll = piano_roll.copy() if piano_roll else {
            "notes": [],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80
        }

        # 곡선 데이터 생성
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        line_data = create_f0_line_data(f0_data, tempo, pixels_per_beat)

        if line_data:
            updated_piano_roll['line_data'] = line_data

        # 상태 메시지 생성
        status_parts = [f0_status]

        if line_data:
            curve_count = len(line_data)
            curve_types = list(line_data.keys())
            status_parts.append(f"{curve_count}개 곡선 ({', '.join(curve_types)}) 시각화 완료")

            # 각 특성에 대한 범위 정보 추가
            for curve_name, curve_info in line_data.items():
                if 'originalRange' in curve_info:
                    range_info = curve_info['originalRange']
                    if 'minHz' in range_info:  # F0
                        status_parts.append(f"F0: {range_info['minHz']:.1f}~{range_info['maxHz']:.1f}Hz")

        duration = f0_data.get('duration', 0)
        status_parts.append(f"⏱️ {duration:.2f}초")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, audio_file

    except Exception as e:
        error_message = f"F0 분석 중 오류 발생: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, audio_file

def generate_f0_demo_audio():
    """
    F0 분석 데모용 간단한 오디오 생성
    """
    print("🎵 F0 분석 데모 오디오 생성 중...")

    # 간단한 톱니파 톤 생성 (100Hz에서 400Hz)
    duration = 3.0  # 3초
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 시간에 따라 주파수가 변화하는 사인파 생성 (100Hz -> 400Hz)
    start_freq = 100
    end_freq = 400
    instantaneous_freq = start_freq + (end_freq - start_freq) * (t / duration)

    # 주파수 변조된 사인파 생성
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
    audio = 0.3 * np.sin(phase)  # 볼륨 조정

    # WAV 파일로 저장
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)

            # 16비트 PCM으로 변환
            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ 데모 오디오 생성됨: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ 데모 오디오 생성 실패: {e}")
        return None

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll F0 Analysis Demo") as demo:
    gr.Markdown("# 📊 PianoRoll F0 Analysis Demo")
    if LIBROSA_AVAILABLE:
        gr.Markdown("오디오 파일을 업로드하고 F0를 추출하여 PianoRoll에서 시각화해보세요!")
    else:
        gr.Markdown("⚠️ **librosa가 설치되지 않음**: `pip install librosa`를 실행하여 설치하세요.")

    with gr.Row():
        with gr.Column(scale=3):
            # F0 초기값 (빈 피아노롤)
            initial_value_f0 = {
                "notes": [],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }
            piano_roll_f0 = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_f0,
                elem_id="piano_roll_f0"
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎤 오디오 업로드")

            audio_input = gr.Audio(
                label="분석할 오디오 파일",
                type="filepath",
                interactive=True
            )

            gr.Markdown("### ⚙️ F0 추출 설정")
            f0_method_dropdown = gr.Dropdown(
                choices=[
                    ("PYIN (정확, 느림)", "pyin"),
                    ("PipTrack (빠름, 부정확)", "piptrack")
                ],
                value="pyin",
                label="F0 추출 방법"
            )
            gr.Markdown("💡 **PYIN**이 더 정확하지만 처리 시간이 더 오래 걸립니다.")

            btn_analyze_f0 = gr.Button(
                "🔬 F0 분석 시작",
                variant="primary",
                size="lg",
                interactive=LIBROSA_AVAILABLE
            )

            btn_generate_demo = gr.Button(
                "🎵 데모 오디오 생성",
                variant="secondary"
            )
            gr.Markdown("📄 시간에 따라 F0가 변화하는 테스트 오디오를 생성합니다.")

            if not LIBROSA_AVAILABLE:
                gr.Markdown("⚠️ librosa가 필요합니다")

    with gr.Row():
        f0_status_text = gr.Textbox(
            label="분석 상태",
            interactive=False,
            lines=6
        )

    with gr.Row():
        # 참조 오디오 재생
        reference_audio = gr.Audio(
            label="원본 오디오 (참조용)",
            type="filepath",
            interactive=False
        )

    output_json_f0 = gr.JSON(label="F0 분석 결과")

    # F0 탭 이벤트 처리

    # F0 분석 버튼
    btn_analyze_f0.click(
        fn=analyze_audio_f0,
        inputs=[piano_roll_f0, audio_input, f0_method_dropdown],
        outputs=[piano_roll_f0, f0_status_text, reference_audio],
        show_progress=True
    )

    # 데모 오디오 생성 버튼
    def create_and_analyze_demo():
        """데모 오디오 생성 및 자동 F0 분석"""
        demo_audio_path = generate_f0_demo_audio()
        if demo_audio_path:
            # 초기 피아노롤 데이터
            initial_piano_roll = {
                "notes": [],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }

            # F0 분석 수행
            updated_piano_roll, status, _ = analyze_audio_f0(initial_piano_roll, demo_audio_path, "pyin")

            return updated_piano_roll, status, demo_audio_path, demo_audio_path
        else:
            return initial_value_f0, "데모 오디오 생성 실패.", None, None

    btn_generate_demo.click(
        fn=create_and_analyze_demo,
        outputs=[piano_roll_f0, f0_status_text, audio_input, reference_audio],
        show_progress=True
    )

    # 노트 변경 시 JSON 출력 업데이트
    def update_f0_json_output(piano_roll_data):
        return piano_roll_data

    piano_roll_f0.change(
        fn=update_f0_json_output,
        inputs=[piano_roll_f0],
        outputs=[output_json_f0],
        show_progress=False
    )

    # 재생 이벤트 로그
    def log_f0_play_event(event_data=None):
        print("📊 F0 재생 이벤트 트리거:", event_data)
        return f"재생 시작: {event_data if event_data else '재생 중'}"

    def log_f0_pause_event(event_data=None):
        print("📊 F0 일시정지 이벤트 트리거:", event_data)
        return f"일시정지: {event_data if event_data else '일시정지됨'}"

    def log_f0_stop_event(event_data=None):
        print("📊 F0 정지 이벤트 트리거:", event_data)
        return f"정지: {event_data if event_data else '정지됨'}"

    piano_roll_f0.play(log_f0_play_event, outputs=f0_status_text)
    piano_roll_f0.pause(log_f0_pause_event, outputs=f0_status_text)
    piano_roll_f0.stop(log_f0_stop_event, outputs=f0_status_text)

if __name__ == "__main__":
    demo.launch() 