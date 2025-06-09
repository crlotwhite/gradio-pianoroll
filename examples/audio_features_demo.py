#!/usr/bin/env python3
"""
Audio Features Demo: Multi-Feature Audio Analysis
Description: F0, loudness, voicing 등 여러 오디오 특성을 동시에 분석하고 시각화하는 기능을 보여줍니다.
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

# librosa 추가 임포트
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ librosa 사용 가능")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa가 설치되지 않음. 오디오 특성 분석 기능이 제한됩니다.")

# 합성기 설정 (오디오 생성용)
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

def midi_to_frequency(midi_note):
    """MIDI 노트 번호를 주파수로 변환 (A4 = 440Hz)"""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def generate_sine_wave(frequency, duration, sample_rate):
    """사인파 생성"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def synthesize_simple_audio(piano_roll_data):
    """간단한 오디오 합성 (특성 분석용)"""
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 전체 길이 계산
    max_end_time = 0
    for note in notes:
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    total_duration = min(max_end_time + 0.5, MAX_DURATION)
    total_samples = int(total_duration * SAMPLE_RATE)
    audio_buffer = np.zeros(total_samples)

    # 각 노트 처리 (간단한 사인파)
    for note in notes:
        pitch = note['pitch']
        velocity = note.get('velocity', 100)
        
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        
        if start_seconds >= total_duration:
            continue
            
        if start_seconds + duration_seconds > total_duration:
            duration_seconds = total_duration - start_seconds
            
        if duration_seconds <= 0:
            continue

        frequency = midi_to_frequency(pitch)
        volume = velocity / 127.0 * 0.3  # 볼륨 조정
        
        # 간단한 사인파 생성
        wave = generate_sine_wave(frequency, duration_seconds, SAMPLE_RATE)
        
        # 오디오 버퍼에 추가
        start_sample = int(start_seconds * SAMPLE_RATE)
        end_sample = start_sample + len(wave)
        
        if start_sample < total_samples:
            end_sample = min(end_sample, total_samples)
            audio_length = end_sample - start_sample
            if audio_length > 0:
                audio_buffer[start_sample:end_sample] += wave[:audio_length] * volume

    # 정규화
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9

    return audio_buffer

def create_temp_wav_file(audio_data, sample_rate):
    """임시 WAV 파일 생성"""
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        audio_16bit = (audio_data * 32767).astype(np.int16)
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        return temp_path
    except Exception as e:
        print(f"임시 WAV 파일 생성 오류: {e}")
        return None

def extract_audio_features(audio_file_path, f0_method="pyin", include_f0=True, include_loudness=True, include_voicing=True):
    """오디오 파일에서 F0, loudness, voice/unvoice 추출"""
    if not LIBROSA_AVAILABLE:
        return None, "librosa가 설치되지 않아 오디오 특성 분석을 수행할 수 없습니다"

    features = {}
    status_messages = []

    try:
        print(f"🎵 오디오 특성 분석 시작: {audio_file_path}")

        # 오디오 로드
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - 샘플레이트: {sr}Hz")
        print(f"   - 길이: {len(y)/sr:.2f}초")

        hop_length = 512

        # F0 추출
        if include_f0:
            try:
                if f0_method == "pyin":
                    f0, voiced_flag, voiced_probs = librosa.pyin(
                        y, sr=sr,
                        fmin=librosa.note_to_hz('C2'),
                        fmax=librosa.note_to_hz('C7')
                    )
                else:
                    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                    f0 = []
                    for t in range(pitches.shape[1]):
                        index = magnitudes[:, t].argmax()
                        pitch = pitches[index, t]
                        f0.append(pitch if pitch > 0 else np.nan)
                    f0 = np.array(f0)
                    voiced_flag = ~np.isnan(f0)
                    voiced_probs = voiced_flag.astype(float)

                frame_times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)

                features['f0'] = {
                    'times': frame_times,
                    'f0_values': f0,
                    'voiced_flag': voiced_flag,
                    'voiced_probs': voiced_probs,
                    'sample_rate': sr,
                    'duration': len(y) / sr,
                    'hop_length': hop_length
                }
                status_messages.append("F0 추출 완료")
                
                valid_f0 = f0[~np.isnan(f0)]
                if len(valid_f0) > 0:
                    print(f"   - F0 범위: {np.min(valid_f0):.1f}Hz ~ {np.max(valid_f0):.1f}Hz")
                
            except Exception as e:
                status_messages.append(f"F0 추출 실패: {str(e)}")

        # Loudness 추출
        if include_loudness:
            try:
                rms_energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]
                frame_times = librosa.frames_to_time(np.arange(len(rms_energy)), sr=sr, hop_length=hop_length)

                # dB로 변환
                max_rms = np.max(rms_energy)
                if max_rms > 0:
                    loudness_db = 20 * np.log10(rms_energy / max_rms)
                    loudness_db = np.maximum(loudness_db, -60)
                else:
                    loudness_db = np.full_like(rms_energy, -60)

                # 0-1로 정규화
                loudness_normalized = (loudness_db + 60) / 60

                features['loudness'] = {
                    'times': frame_times,
                    'rms_values': rms_energy,
                    'loudness_db': loudness_db,
                    'loudness_normalized': loudness_normalized,
                    'sample_rate': sr,
                    'duration': len(y) / sr,
                    'hop_length': hop_length
                }
                status_messages.append("Loudness 추출 완료")
                print(f"   - RMS 범위: {np.min(rms_energy):.6f} ~ {np.max(rms_energy):.6f}")
                
            except Exception as e:
                status_messages.append(f"Loudness 추출 실패: {str(e)}")

        # Voice/Unvoice 추출
        if include_voicing and 'f0' in features:
            try:
                voicing_data = features['f0']  # F0에서 voiced 정보 사용
                voiced_ratio = np.sum(voicing_data['voiced_flag']) / len(voicing_data['voiced_flag'])
                
                features['voicing'] = {
                    'times': voicing_data['times'],
                    'voiced_flag': voicing_data['voiced_flag'],
                    'voiced_probs': voicing_data['voiced_probs'],
                    'sample_rate': sr,
                    'duration': len(y) / sr,
                    'hop_length': hop_length,
                    'voiced_ratio': voiced_ratio
                }
                status_messages.append("Voice/Unvoice 추출 완료")
                print(f"   - Voiced 비율: {voiced_ratio:.1%}")
                
            except Exception as e:
                status_messages.append(f"Voice/Unvoice 추출 실패: {str(e)}")

        if features:
            features['duration'] = len(y) / sr
            features['sample_rate'] = sr
            return features, " | ".join(status_messages)
        else:
            return None, "모든 특성 추출 실패"

    except Exception as e:
        print(f"❌ 오디오 특성 분석 오류: {e}")
        return None, f"오디오 특성 분석 오류: {str(e)}"

def create_multi_feature_line_data(features, tempo=120, pixels_per_beat=80):
    """여러 오디오 특성을 결합하여 line_data 생성"""
    combined_line_data = {}

    try:
        # F0 곡선 추가
        if 'f0' in features:
            f0_data = features['f0']
            times = f0_data['times']
            f0_values = f0_data['f0_values']

            # 피아노롤 상수
            NOTE_HEIGHT = 20
            TOTAL_NOTES = 128

            def hz_to_midi(frequency):
                if frequency <= 0:
                    return 0
                return 69 + 12 * np.log2(frequency / 440.0)

            def midi_to_y_coordinate(midi_note):
                return (TOTAL_NOTES - 1 - midi_note) * NOTE_HEIGHT + NOTE_HEIGHT/2

            # F0 데이터 포인트 생성
            f0_points = []
            valid_f0_values = []

            for time, f0 in zip(times, f0_values):
                if not np.isnan(f0) and f0 > 0:
                    midi_note = hz_to_midi(f0)
                    if 0 <= midi_note <= 127:
                        x_pixel = time * (tempo / 60) * pixels_per_beat
                        y_pixel = midi_to_y_coordinate(midi_note)
                        f0_points.append({"x": float(x_pixel), "y": float(y_pixel)})
                        valid_f0_values.append(f0)

            if f0_points:
                min_f0 = float(np.min(valid_f0_values))
                max_f0 = float(np.max(valid_f0_values))
                
                combined_line_data['f0_curve'] = {
                    "color": "#FF6B6B",
                    "lineWidth": 3,
                    "yMin": 0,
                    "yMax": TOTAL_NOTES * NOTE_HEIGHT,
                    "position": "overlay",
                    "renderMode": "piano_grid",
                    "visible": True,
                    "opacity": 0.8,
                    "data": f0_points,
                    "dataType": "f0",
                    "unit": "Hz",
                    "originalRange": {
                        "minHz": min_f0,
                        "maxHz": max_f0,
                        "minMidi": hz_to_midi(min_f0),
                        "maxMidi": hz_to_midi(max_f0)
                    }
                }

        # Loudness 곡선 추가
        if 'loudness' in features:
            loudness_data = features['loudness']
            times = loudness_data['times']
            loudness_db = loudness_data['loudness_db']

            loudness_points = []
            for time, value in zip(times, loudness_db):
                if not np.isnan(value):
                    x_pixel = time * (tempo / 60) * pixels_per_beat
                    # -60dB ~ 0dB를 0 ~ 2560 픽셀로 변환
                    normalized_value = (value + 60) / 60
                    y_pixel = normalized_value * 2560
                    loudness_points.append({"x": float(x_pixel), "y": float(max(0, min(2560, y_pixel)))})

            if loudness_points:
                combined_line_data['loudness_curve'] = {
                    "color": "#4ECDC4",
                    "lineWidth": 2,
                    "yMin": 0,
                    "yMax": 2560,
                    "position": "overlay",
                    "renderMode": "independent_range",
                    "visible": True,
                    "opacity": 0.6,
                    "data": loudness_points,
                    "dataType": "loudness",
                    "unit": "dB",
                    "originalRange": {
                        "min": float(np.min(loudness_db)),
                        "max": float(np.max(loudness_db)),
                        "y_min": -60,
                        "y_max": 0
                    }
                }

        # Voice/Unvoice 곡선 추가
        if 'voicing' in features:
            voicing_data = features['voicing']
            times = voicing_data['times']
            voiced_probs = voicing_data['voiced_probs']

            voicing_points = []
            for time, value in zip(times, voiced_probs):
                if not np.isnan(value):
                    x_pixel = time * (tempo / 60) * pixels_per_beat
                    y_pixel = value * 2560  # 0-1을 0-2560 픽셀로 변환
                    voicing_points.append({"x": float(x_pixel), "y": float(max(0, min(2560, y_pixel)))})

            if voicing_points:
                combined_line_data['voicing_curve'] = {
                    "color": "#9B59B6",
                    "lineWidth": 2,
                    "yMin": 0,
                    "yMax": 2560,
                    "position": "overlay",
                    "renderMode": "independent_range",
                    "visible": True,
                    "opacity": 0.6,
                    "data": voicing_points,
                    "dataType": "voicing",
                    "unit": "probability",
                    "originalRange": {
                        "min": 0.0,
                        "max": 1.0,
                        "voiced_ratio": voicing_data.get('voiced_ratio', 0.0),
                        "y_min": 0,
                        "y_max": 1
                    }
                }

        if combined_line_data:
            print(f"📊 결합된 LineData 생성됨: {len(combined_line_data)} 곡선")
            return combined_line_data
        else:
            print("⚠️ 곡선 데이터가 생성되지 않음")
            return None

    except Exception as e:
        print(f"❌ 결합된 LineData 생성 오류: {e}")
        return None

def analyze_generated_audio_features(piano_roll, include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin"):
    """노트에서 오디오를 생성하고 특성 분석"""
    print("=== 생성된 오디오 특성 분석 ===")

    # 오디오 합성
    audio_data = synthesize_simple_audio(piano_roll)
    if audio_data is None:
        return piano_roll, "오디오 합성 실패", None

    # 임시 WAV 파일 생성
    temp_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)
    if temp_audio_path is None:
        return piano_roll, "임시 오디오 파일 생성 실패", None

    try:
        # 오디오 특성 분석
        features, analysis_status = extract_audio_features(
            temp_audio_path, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"오디오 특성 분석 실패: {analysis_status}", temp_audio_path

        # 피아노롤 업데이트
        updated_piano_roll = piano_roll.copy() if piano_roll else {}

        # 곡선 데이터 생성
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        line_data = create_multi_feature_line_data(features, tempo, pixels_per_beat)

        if line_data:
            updated_piano_roll['line_data'] = line_data

        # 상태 메시지 생성
        status_parts = [f"오디오 합성 완료", analysis_status]

        if line_data:
            curve_count = len(line_data)
            status_parts.append(f"{curve_count}개 특성 곡선 시각화 완료")

            # 각 특성 범위 정보 추가
            for curve_name, curve_info in line_data.items():
                if 'originalRange' in curve_info:
                    range_info = curve_info['originalRange']
                    if 'minHz' in range_info:  # F0
                        status_parts.append(f"F0: {range_info['minHz']:.1f}~{range_info['maxHz']:.1f}Hz")
                    elif 'min' in range_info and 'voiced_ratio' not in range_info:  # Loudness
                        unit = curve_info.get('unit', '')
                        status_parts.append(f"Loudness: {range_info['min']:.1f}~{range_info['max']:.1f}{unit}")
                    elif 'voiced_ratio' in range_info:  # Voice/Unvoice
                        voiced_ratio = range_info['voiced_ratio']
                        status_parts.append(f"Voicing: {voiced_ratio:.1%} voiced")

        duration = features.get('duration', 0)
        status_parts.append(f"⏱️ {duration:.2f}초")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, temp_audio_path

    except Exception as e:
        error_message = f"특성 분석 중 오류 발생: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, temp_audio_path

def analyze_uploaded_audio_features(piano_roll, audio_file, include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin"):
    """업로드된 오디오 파일의 특성 분석"""
    print("=== 업로드된 오디오 특성 분석 ===")
    print(f"오디오 파일: {audio_file}")

    if not audio_file:
        return piano_roll, "오디오 파일을 업로드해 주세요.", None

    if not LIBROSA_AVAILABLE:
        return piano_roll, "librosa가 설치되지 않아 오디오 특성 분석을 수행할 수 없습니다. 'pip install librosa'로 설치해 주세요.", None

    try:
        # 오디오 특성 분석
        features, analysis_status = extract_audio_features(
            audio_file, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"오디오 특성 분석 실패: {analysis_status}", audio_file

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

        line_data = create_multi_feature_line_data(features, tempo, pixels_per_beat)

        if line_data:
            updated_piano_roll['line_data'] = line_data

        # 상태 메시지 생성
        status_parts = [analysis_status]

        if line_data:
            curve_count = len(line_data)
            curve_types = list(line_data.keys())
            status_parts.append(f"{curve_count}개 곡선 ({', '.join(curve_types)}) 시각화 완료")

            # 각 특성 범위 정보 추가
            for curve_name, curve_info in line_data.items():
                if 'originalRange' in curve_info:
                    range_info = curve_info['originalRange']
                    if 'minHz' in range_info:  # F0
                        status_parts.append(f"F0: {range_info['minHz']:.1f}~{range_info['maxHz']:.1f}Hz")
                    elif 'min' in range_info and 'voiced_ratio' not in range_info:  # Loudness
                        unit = curve_info.get('unit', '')
                        status_parts.append(f"Loudness: {range_info['min']:.1f}~{range_info['max']:.1f}{unit}")
                    elif 'voiced_ratio' in range_info:  # Voice/Unvoice
                        voiced_ratio = range_info['voiced_ratio']
                        status_parts.append(f"Voicing: {voiced_ratio:.1%} voiced")

        duration = features.get('duration', 0)
        status_parts.append(f"⏱️ {duration:.2f}초")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, audio_file

    except Exception as e:
        error_message = f"업로드된 오디오 분석 중 오류 발생: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, audio_file

def generate_feature_demo_audio():
    """특성 분석 데모용 다양한 특성을 가진 오디오 생성"""
    print("🎵 특성 분석용 데모 오디오 생성 중...")

    duration = 4.0  # 4초
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 다양한 특성을 가진 오디오 생성
    audio = np.zeros_like(t)

    # 구간 1 (0-1초): C4에서 C5로 + 볼륨 증가
    mask1 = (t >= 0) & (t < 1)
    t1 = t[mask1]
    f1_start, f1_end = 261.63, 523.25  # C4에서 C5
    freq1 = f1_start + (f1_end - f1_start) * (t1 / 1.0)
    phase1 = 2 * np.pi * np.cumsum(freq1) / sample_rate
    vol1 = 0.1 + 0.4 * (t1 / 1.0)  # 0.1에서 0.5로 증가
    audio[mask1] = vol1 * np.sin(phase1)

    # 구간 2 (1-2초): C5에서 G4로 + 일정 볼륨
    mask2 = (t >= 1) & (t < 2)
    t2 = t[mask2] - 1
    f2_start, f2_end = 523.25, 392.00  # C5에서 G4
    freq2 = f2_start + (f2_end - f2_start) * (t2 / 1.0)
    phase2 = 2 * np.pi * np.cumsum(freq2) / sample_rate
    audio[mask2] = 0.5 * np.sin(phase2)

    # 구간 3 (2-3초): A4 고정 + 볼륨 감소 (트레몰로 효과)
    mask3 = (t >= 2) & (t < 3)
    t3 = t[mask3] - 2
    freq3 = 440.0  # A4 고정
    phase3 = 2 * np.pi * freq3 * t3
    vol3 = 0.5 * (1 - t3 / 1.0) * (1 + 0.3 * np.sin(2 * np.pi * 6 * t3))  # 트레몰로
    audio[mask3] = vol3 * np.sin(phase3)

    # 구간 4 (3-4초): 복합음 (A4 + E5) + 페이드 아웃
    mask4 = (t >= 3) & (t < 4)
    t4 = t[mask4] - 3
    freq4a, freq4b = 440.0, 659.25  # A4 + E5
    phase4a = 2 * np.pi * freq4a * t4
    phase4b = 2 * np.pi * freq4b * t4
    vol4 = 0.4 * (1 - t4 / 1.0)  # 페이드 아웃
    audio[mask4] = vol4 * (0.6 * np.sin(phase4a) + 0.4 * np.sin(phase4b))

    # WAV 파일로 저장
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ 특성 분석용 데모 오디오 생성됨: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ 특성 분석용 데모 오디오 생성 실패: {e}")
        return None

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll Audio Features Demo") as demo:
    gr.Markdown("# 🔊 PianoRoll Audio Features Demo")
    if LIBROSA_AVAILABLE:
        gr.Markdown("오디오 파일을 업로드하고 F0, loudness 등 다양한 특성을 분석해보세요!")
    else:
        gr.Markdown("⚠️ **librosa가 설치되지 않음**: `pip install librosa`를 실행하여 설치하세요.")

    with gr.Row():
        with gr.Column(scale=3):
            # 초기값 (빈 피아노롤)
            initial_value = {
                "notes": [],
                "tempo": 120,
                "timeSignature": {"numerator": 4, "denominator": 4},
                "editMode": "select",
                "snapSetting": "1/4",
                "pixelsPerBeat": 80
            }
            piano_roll = PianoRoll(
                height=600,
                width=1000,
                value=initial_value,
                elem_id="piano_roll_features"
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎤 오디오 업로드")

            audio_input = gr.Audio(
                label="분석할 오디오 파일",
                type="filepath",
                interactive=True
            )

            gr.Markdown("### ⚙️ 분석 설정")
            f0_method_dropdown = gr.Dropdown(
                choices=[
                    ("PYIN (정확, 느림)", "pyin"),
                    ("PipTrack (빠름, 부정확)", "piptrack")
                ],
                value="pyin",
                label="F0 추출 방법"
            )

            btn_analyze = gr.Button(
                "🔬 특성 분석 시작",
                variant="primary",
                size="lg",
                interactive=LIBROSA_AVAILABLE
            )

    with gr.Row():
        status_text = gr.Textbox(
            label="분석 상태",
            interactive=False,
            lines=4
        )

    with gr.Row():
        reference_audio = gr.Audio(
            label="원본 오디오 (참조용)",
            type="filepath",
            interactive=False
        )

    output_json = gr.JSON(label="특성 분석 결과")

    # 이벤트 처리
    def simple_analyze_features(piano_roll, audio_file, f0_method):
        """간단한 분석 래퍼"""
        return analyze_uploaded_audio_features(
            piano_roll, audio_file, 
            include_f0=True, include_loudness=True, include_voicing=False, 
            f0_method=f0_method
        )
    
    btn_analyze.click(
        fn=simple_analyze_features,
        inputs=[piano_roll, audio_input, f0_method_dropdown],
        outputs=[piano_roll, status_text, reference_audio],
        show_progress=True
    )

    # JSON 출력 업데이트
    piano_roll.change(
        fn=lambda x: x,
        inputs=[piano_roll],
        outputs=[output_json],
        show_progress=False
    )

if __name__ == "__main__":
    demo.launch() 