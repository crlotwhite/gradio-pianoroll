#!/usr/bin/env python3
"""
Synthesizer Demo: Audio Synthesis and Playback
Description: PianoRoll 노트에서 오디오를 합성하고 재생하는 기능을 보여줍니다.
Author: gradio-pianoroll
"""

import gradio as gr
import numpy as np
import io
import base64
import wave
import tempfile
import os
from gradio_pianoroll import PianoRoll

# 합성기 설정
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

def midi_to_frequency(midi_note):
    """MIDI 노트 번호를 주파수로 변환 (A4 = 440Hz)"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def create_adsr_envelope(attack, decay, sustain, release, duration, sample_rate):
    """ADSR 엔벨로프 생성"""
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

    # 서스테인 구간이 음수가 되지 않도록 조정
    if sustain_samples < 0:
        sustain_samples = 0
        total_samples = attack_samples + decay_samples + release_samples

    envelope = np.zeros(total_samples)

    # Attack 단계
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay 단계
    if decay_samples > 0:
        start_idx = attack_samples
        end_idx = attack_samples + decay_samples
        envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)

    # Sustain 단계
    if sustain_samples > 0:
        start_idx = attack_samples + decay_samples
        end_idx = start_idx + sustain_samples
        envelope[start_idx:end_idx] = sustain

    # Release 단계
    if release_samples > 0:
        start_idx = attack_samples + decay_samples + sustain_samples
        envelope[start_idx:] = np.linspace(sustain, 0, release_samples)

    return envelope

def generate_sine_wave(frequency, duration, sample_rate):
    """사인파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_sawtooth_wave(frequency, duration, sample_rate):
    """톱니파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * (t * frequency % 1) - 1

def generate_square_wave(frequency, duration, sample_rate):
    """사각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sign(np.sin(2 * np.pi * frequency * t))

def generate_triangle_wave(frequency, duration, sample_rate):
    """삼각파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1

def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    """하모닉스가 있는 복합 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # 기본 주파수
    wave += np.sin(2 * np.pi * frequency * t)

    # 하모닉스 추가 (진폭은 1/n로 감소)
    for n in range(2, harmonics + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # 정규화
    wave = wave / np.max(np.abs(wave))
    return wave

def generate_fm_wave(frequency, duration, sample_rate, mod_freq=5.0, mod_depth=2.0):
    """FM 파형 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 모듈레이터
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # 주파수 변조된 캐리어
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier

def generate_complex_wave(frequency, duration, sample_rate, wave_type='complex'):
    """복합 파형 생성 (여러 기법 결합)"""
    if wave_type == 'sine':
        return generate_sine_wave(frequency, duration, sample_rate)
    elif wave_type == 'sawtooth':
        return generate_sawtooth_wave(frequency, duration, sample_rate)
    elif wave_type == 'square':
        return generate_square_wave(frequency, duration, sample_rate)
    elif wave_type == 'triangle':
        return generate_triangle_wave(frequency, duration, sample_rate)
    elif wave_type == 'harmonic':
        return generate_harmonic_wave(frequency, duration, sample_rate, harmonics=7)
    elif wave_type == 'fm':
        return generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.1, mod_depth=3.0)
    else:  # 'complex' - 여러 파형 결합
        # 기본 톱니파 + 하모닉스 + FM
        base = generate_sawtooth_wave(frequency, duration, sample_rate) * 0.6
        harmonic = generate_harmonic_wave(frequency, duration, sample_rate, harmonics=4) * 0.3
        fm = generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.05, mod_depth=1.0) * 0.1

        return base + harmonic + fm

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    """PianoRoll 데이터에서 오디오 합성"""
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 전체 길이 계산 (마지막 노트 끝까지)
    max_end_time = 0
    for note in notes:
        # 픽셀을 초로 변환 (템포와 픽셀 퍼 비트 고려)
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    # 최대 길이 제한
    total_duration = min(max_end_time + 1.0, MAX_DURATION)  # 1초 버퍼 추가
    total_samples = int(total_duration * SAMPLE_RATE)

    # 최종 오디오 버퍼
    audio_buffer = np.zeros(total_samples)

    # 각 노트 처리
    for i, note in enumerate(notes):
        try:
            # 노트 속성
            pitch = note['pitch']
            velocity = note.get('velocity', 100)

            # 시간 계산
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            # 범위 체크
            if start_seconds >= total_duration:
                continue

            # 전체 길이를 넘지 않도록 지속시간 조정
            if start_seconds + duration_seconds > total_duration:
                duration_seconds = total_duration - start_seconds

            if duration_seconds <= 0:
                continue

            # 주파수 계산
            frequency = midi_to_frequency(pitch)

            # 볼륨 계산 (velocity를 0-1로 정규화)
            volume = velocity / 127.0

            # 복합 파형 생성
            base_wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

            # 추가 효과: 비브라토 (주파수 변조)
            t = np.linspace(0, duration_seconds, len(base_wave), False)
            vibrato_freq = 4.5  # 4.5Hz 비브라토
            vibrato_depth = 0.02  # 2% 주파수 변조
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)

            # 비브라토 적용
            vibrato_wave = base_wave * vibrato

            # 추가 효과: 트레몰로 (진폭 변조)
            tremolo_freq = 3.0  # 3Hz 트레몰로
            tremolo_depth = 0.1  # 10% 진폭 변조
            tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)

            # 트레몰로 적용
            final_wave = vibrato_wave * tremolo

            # ADSR 엔벨로프 적용
            envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)

            # 엔벨로프와 파형 길이 조정
            min_length = min(len(final_wave), len(envelope))
            note_audio = final_wave[:min_length] * envelope[:min_length] * volume * 0.25  # 볼륨 조정

            # 오디오 버퍼에 추가
            start_sample = int(start_seconds * SAMPLE_RATE)
            end_sample = start_sample + len(note_audio)

            # 버퍼 범위 내에서만 추가
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                audio_length = end_sample - start_sample
                if audio_length > 0:
                    audio_buffer[start_sample:end_sample] += note_audio[:audio_length]

        except Exception as e:
            print(f"노트 처리 오류: {e}")
            continue

    # 클리핑 방지 (정규화)
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9  # 90%로 제한

    return audio_buffer

def audio_to_base64_wav(audio_data, sample_rate):
    """오디오 데이터를 base64 인코딩된 WAV로 변환"""
    if audio_data is None or len(audio_data) == 0:
        return None

    # 16비트 PCM으로 변환
    audio_16bit = (audio_data * 32767).astype(np.int16)

    # 메모리에서 WAV 파일 생성
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 모노
        wav_file.setsampwidth(2)  # 16비트
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())

    # base64 인코딩
    buffer.seek(0)
    wav_data = buffer.read()
    base64_data = base64.b64encode(wav_data).decode('utf-8')

    return f"data:audio/wav;base64,{base64_data}"

def create_temp_wav_file(audio_data, sample_rate):
    """Gradio Audio 컴포넌트용 임시 WAV 파일 생성"""
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        # 16비트 PCM으로 변환
        audio_16bit = (audio_data * 32767).astype(np.int16)

        # 임시 파일 생성
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 모노
            wav_file.setsampwidth(2)  # 16비트
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        # 파일 디스크립터 닫기
        os.close(temp_fd)

        return temp_path
    except Exception as e:
        print(f"임시 WAV 파일 생성 오류: {e}")
        return None

def synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    """오디오 합성 및 피아노롤에 전달"""
    print("=== 합성 함수 호출됨 ===")
    print("Piano roll data:", piano_roll)
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")

    # 오디오 합성
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        print("오디오 합성 실패")
        return piano_roll, "오디오 합성 실패", None

    # base64로 변환 (피아노롤용)
    audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)

    # Gradio Audio 컴포넌트용 WAV 파일 생성
    gradio_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)

    # 피아노롤 데이터에 오디오 데이터 추가
    updated_piano_roll = piano_roll.copy() if piano_roll else {}
    updated_piano_roll['audio_data'] = audio_base64
    updated_piano_roll['use_backend_audio'] = True

    print(f"🔊 [synthesize_and_play] 백엔드 오디오 데이터 설정:")
    print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
    print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")

    status_message = f"오디오 합성 완료 ({wave_type} 파형): {len(audio_data)} 샘플, 지속시간: {len(audio_data)/SAMPLE_RATE:.2f}초"

    return updated_piano_roll, status_message, gradio_audio_path

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll Synthesizer Demo") as demo:
    gr.Markdown("# 🎵 PianoRoll Synthesizer Demo")
    gr.Markdown("노트를 편집하고 '🎶 오디오 합성' 버튼을 클릭하여 오디오를 생성하고 재생해보세요!")

    with gr.Row():
        with gr.Column(scale=3):
            # 합성기 초기값
            initial_value_synth = {
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
                        "pitch": 62,  # D4
                        "velocity": 100,
                        "lyric": "레"
                    },
                    {
                        "start": 320,
                        "duration": 160,
                        "pitch": 64,  # E4
                        "velocity": 100,
                        "lyric": "미"
                    },
                    {
                        "start": 480,
                        "duration": 160,
                        "pitch": 65,  # F4
                        "velocity": 100,
                        "lyric": "파"
                    }
                ],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "use_backend_audio": False  # 처음에는 백엔드 오디오 비활성화
            }
            piano_roll_synth = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_synth,
                elem_id="piano_roll_synth"
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ ADSR 설정")
            attack_slider = gr.Slider(
                minimum=0.001,
                maximum=1.0,
                value=0.01,
                step=0.001,
                label="Attack (초)"
            )
            decay_slider = gr.Slider(
                minimum=0.001,
                maximum=1.0,
                value=0.1,
                step=0.001,
                label="Decay (초)"
            )
            sustain_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.01,
                label="Sustain (레벨)"
            )
            release_slider = gr.Slider(
                minimum=0.001,
                maximum=2.0,
                value=0.3,
                step=0.001,
                label="Release (초)"
            )

            gr.Markdown("### 🎵 파형 설정")
            wave_type_dropdown = gr.Dropdown(
                choices=[
                    ("복합 파형 (Complex)", "complex"),
                    ("하모닉 합성 (Harmonic)", "harmonic"),
                    ("FM 합성 (FM)", "fm"),
                    ("톱니파 (Sawtooth)", "sawtooth"),
                    ("사각파 (Square)", "square"),
                    ("삼각파 (Triangle)", "triangle"),
                    ("사인파 (Sine)", "sine")
                ],
                value="complex",
                label="파형 타입",
                info="각 노트는 다양한 파형을 순환하여 사용"
            )

    with gr.Row():
        btn_synthesize = gr.Button("🎶 오디오 합성", variant="primary", size="lg")
        status_text = gr.Textbox(label="상태", interactive=False)

    # Gradio Audio 컴포넌트 (비교용)
    with gr.Row():
        gr.Markdown("### 🔊 Gradio Audio 비교")
        gradio_audio_output = gr.Audio(
            label="백엔드 생성 오디오 (비교용)",
            type="filepath",
            interactive=False
        )

    output_json_synth = gr.JSON(label="결과 데이터")

    # 합성기 이벤트
    btn_synthesize.click(
        fn=synthesize_and_play,
        inputs=[
            piano_roll_synth,
            attack_slider,
            decay_slider,
            sustain_slider,
            release_slider,
            wave_type_dropdown
        ],
        outputs=[piano_roll_synth, status_text, gradio_audio_output],
        show_progress=True
    )

    # 이벤트 리스너 설정
    def log_play_event(event_data=None):
        print("🎵 재생 이벤트 트리거:", event_data)
        return f"재생 시작: {event_data if event_data else '재생 중'}"

    def log_pause_event(event_data=None):
        print("⏸️ 일시정지 이벤트 트리거:", event_data)
        return f"일시정지: {event_data if event_data else '일시정지됨'}"

    def log_stop_event(event_data=None):
        print("⏹️ 정지 이벤트 트리거:", event_data)
        return f"정지: {event_data if event_data else '정지됨'}"

    piano_roll_synth.play(log_play_event, outputs=status_text)
    piano_roll_synth.pause(log_pause_event, outputs=status_text)
    piano_roll_synth.stop(log_stop_event, outputs=status_text)

    # JSON 출력 업데이트
    piano_roll_synth.change(lambda x: x, inputs=piano_roll_synth, outputs=output_json_synth)

if __name__ == "__main__":
    demo.launch() 