#!/usr/bin/env python3
"""
Gradio PianoRoll Comprehensive Demo
Description: 피아노롤 노트 편집, 오디오 합성, 특성 분석을 모두 지원하는 통합 데모
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

# 합성기 설정
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

# 로그 최적화를 위한 전역 변수들
_last_synthesis_config = {}
_last_wave_type = None
_synthesis_count = 0

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
    """사인파 생성 - 순수한 톤"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_sawtooth_wave(frequency, duration, sample_rate):
    """톱니파 생성 (배음 합성 방식) - 밝고 날카로운 소리"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)
    
    # 배음 합성으로 더 음악적인 톱니파 생성
    max_harmonic = min(20, int(sample_rate / (2 * frequency)))  # 나이퀴스트 한계
    for n in range(1, max_harmonic + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)
    
    return wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave

def generate_square_wave(frequency, duration, sample_rate):
    """사각파 생성 (배음 합성 방식) - 거칠고 공격적인 소리"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)
    
    # 홀수 배음만 사용하여 사각파 생성
    max_harmonic = min(15, int(sample_rate / (2 * frequency)))
    for n in range(1, max_harmonic + 1, 2):  # 홀수만
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)
    
    return wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave

def generate_triangle_wave(frequency, duration, sample_rate):
    """삼각파 생성 (배음 합성 방식) - 부드럽고 따뜻한 소리"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)
    
    # 홀수 배음, n^2로 감쇄
    max_harmonic = min(12, int(sample_rate / (2 * frequency)))
    for n in range(1, max_harmonic + 1, 2):  # 홀수만
        amplitude = 1.0 / (n * n)
        phase = np.pi if (n-1)//2 % 2 == 1 else 0  # 교대로 위상 반전
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t + phase)
    
    return wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave

def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    """하모닉스가 있는 복합 파형 생성 - 풍부한 배음"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # 기본 주파수 (강함)
    wave += 1.0 * np.sin(2 * np.pi * frequency * t)

    # 하모닉스 추가 (1/n으로 감소하되 좀 더 강하게)
    max_harmonic = min(harmonics, int(sample_rate / (2 * frequency)))
    for n in range(2, max_harmonic + 1):
        amplitude = 0.8 / n  # 더 강한 배음
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # 정규화
    return wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave

def generate_fm_wave(frequency, duration, sample_rate, mod_freq=None, mod_depth=3.0):
    """FM 파형 생성 - 금속성, 벨 같은 소리"""
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    
    # 모듈레이터 주파수를 기본 주파수에 비례하게 설정
    if mod_freq is None:
        mod_freq = frequency * 1.5  # 1.5배 비율로 더 특징적인 FM 사운드
    
    # 모듈레이터
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # 주파수 변조된 캐리어
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier

def generate_complex_wave(frequency, duration, sample_rate, wave_type='complex'):
    """복합 파형 생성 (여러 기법 결합)"""
    global _last_wave_type
    
    # 파형 타입이 변경되었을 때만 로그 출력
    if wave_type != _last_wave_type:
        print(f"  🎵 파형 변경: {_last_wave_type} → {wave_type}")
        _last_wave_type = wave_type
    
    if wave_type == 'sine':
        return generate_sine_wave(frequency, duration, sample_rate)
    elif wave_type == 'sawtooth':
        return generate_sawtooth_wave(frequency, duration, sample_rate)
    elif wave_type == 'square':
        return generate_square_wave(frequency, duration, sample_rate)
    elif wave_type == 'triangle':
        return generate_triangle_wave(frequency, duration, sample_rate)
    elif wave_type == 'harmonic':
        return generate_harmonic_wave(frequency, duration, sample_rate, harmonics=8)
    elif wave_type == 'fm':
        return generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 2.1, mod_depth=4.0)
    else:  # 'complex' - 단순화된 복합 파형
        # 톱니파 기반에 약간의 FM 추가
        base = generate_sawtooth_wave(frequency, duration, sample_rate) * 0.8
        fm_component = generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.7, mod_depth=1.5) * 0.2
        return base + fm_component

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    """PianoRoll 데이터에서 오디오 합성 (ADSR + 다양한 파형)"""
    global _last_synthesis_config, _synthesis_count
    
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 현재 설정
    current_config = {
        'wave_type': wave_type,
        'attack': round(attack, 3),
        'decay': round(decay, 3), 
        'sustain': round(sustain, 2),
        'release': round(release, 3),
        'tempo': tempo,
        'note_count': len(notes)
    }
    
    # 설정이 변경되었거나 첫 번째 합성일 때만 상세 로그 출력
    config_changed = current_config != _last_synthesis_config
    _synthesis_count += 1
    
    if config_changed or _synthesis_count == 1:
        print(f"🎛️ 합성 설정 #{_synthesis_count}: {wave_type} 파형, ADSR({attack:.3f},{decay:.3f},{sustain:.2f},{release:.3f})")
        print(f"📝 노트 수: {len(notes)}, 템포: {tempo}BPM")
        _last_synthesis_config = current_config.copy()
    else:
        print(f"🔄 합성 #{_synthesis_count}: 동일 설정으로 재합성")

    # 전체 길이 계산
    max_end_time = 0
    for note in notes:
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    total_duration = min(max_end_time + 1.0, MAX_DURATION)
    total_samples = int(total_duration * SAMPLE_RATE)
    audio_buffer = np.zeros(total_samples)

    # 파형별 효과 설정
    vibrato_settings = {
        'sine': (0.0, 0.0),      # 순수한 사인파는 효과 없음
        'sawtooth': (4.5, 0.015), # 가벼운 비브라토
        'square': (0.0, 0.0),     # 사각파는 효과 없이 거칠게
        'triangle': (5.0, 0.02),  # 부드러운 비브라토
        'harmonic': (4.0, 0.025), # 풍부한 비브라토
        'fm': (6.0, 0.03),        # FM은 더 빠른 비브라토
        'complex': (4.5, 0.02)    # 적당한 비브라토
    }
    
    tremolo_settings = {
        'sine': (0.0, 0.0),       # 순수한 사인파는 효과 없음  
        'sawtooth': (2.5, 0.08),  # 가벼운 트레몰로
        'square': (0.0, 0.0),     # 사각파는 효과 없이
        'triangle': (3.0, 0.06),  # 부드러운 트레몰로
        'harmonic': (2.8, 0.1),   # 풍부한 트레몰로
        'fm': (3.5, 0.12),        # FM은 더 강한 트레몰로
        'complex': (3.0, 0.08)    # 적당한 트레몰로
    }

    vibrato_freq, vibrato_depth = vibrato_settings.get(wave_type, (4.5, 0.02))
    tremolo_freq, tremolo_depth = tremolo_settings.get(wave_type, (3.0, 0.08))

    # 각 노트 처리 (고급 합성) - 개별 노트 로그는 설정 변경시에만 출력
    processed_notes = 0
    for i, note in enumerate(notes):
        try:
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
            volume = velocity / 127.0

            # 개별 노트 로그는 설정이 변경되었을 때만 출력 (최대 3개)
            if config_changed and i < 3:
                print(f"  노트 {i+1}: MIDI {pitch} ({frequency:.1f}Hz), {duration_seconds:.2f}초")
            elif config_changed and i == 3:
                print(f"  ... 및 {len(notes)-3}개 노트 더")

            # 복합 파형 생성
            base_wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

            # 파형별 효과 적용
            t = np.linspace(0, duration_seconds, len(base_wave), False)
            
            # 비브라토 (주파수 변조) - 파형별로 다르게
            if vibrato_depth > 0:
                vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
                vibrato_wave = base_wave * vibrato
            else:
                vibrato_wave = base_wave

            # 트레몰로 (진폭 변조) - 파형별로 다르게
            if tremolo_depth > 0:
                tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)
                final_wave = vibrato_wave * tremolo
            else:
                final_wave = vibrato_wave

            # ADSR 엔벨로프 적용
            envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)
            final_wave = final_wave[:len(envelope)] * envelope * volume

            # 오디오 버퍼에 추가
            start_sample = int(start_seconds * SAMPLE_RATE)
            end_sample = start_sample + len(final_wave)
            
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                audio_length = end_sample - start_sample
                if audio_length > 0:
                    audio_buffer[start_sample:end_sample] += final_wave[:audio_length]
                    processed_notes += 1

        except Exception as e:
            if config_changed:  # 오류 로그도 설정 변경시에만 출력
                print(f"❌ 노트 {note.get('pitch', 'unknown')} 합성 오류: {e}")
            continue

    # 정규화
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9
        print(f"✅ 오디오 합성 완료: {processed_notes}개 노트, {len(audio_buffer)/SAMPLE_RATE:.2f}초")
    else:
        print("⚠️ 오디오 합성 결과가 무음입니다")

    return audio_buffer

def audio_array_to_base64_wav(audio_data, sample_rate):
    """numpy 배열을 base64 WAV로 변환"""
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        audio_16bit = (audio_data * 32767).astype(np.int16)
        buffer = io.BytesIO()

        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        buffer.seek(0)
        wav_data = buffer.read()
        base64_data = base64.b64encode(wav_data).decode('utf-8')
        return f"data:audio/wav;base64,{base64_data}"

    except Exception as e:
        print(f"Base64 WAV 변환 오류: {e}")
        return None

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
        # 오디오 로드 (로그 최소화)
        y, sr = librosa.load(audio_file_path, sr=None)
        duration = len(y) / sr
        
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
                    'duration': duration,
                    'hop_length': hop_length
                }
                status_messages.append("F0 추출 완료")
                
                valid_f0 = f0[~np.isnan(f0)]
                if len(valid_f0) > 0:
                    f0_range = f"{np.min(valid_f0):.1f}~{np.max(valid_f0):.1f}Hz"
                    status_messages.append(f"F0범위: {f0_range}")
                
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
                    'duration': duration,
                    'hop_length': hop_length
                }
                status_messages.append("Loudness 추출 완료")
                
                db_range = f"{np.min(loudness_db):.1f}~{np.max(loudness_db):.1f}dB"
                status_messages.append(f"Loudness범위: {db_range}")
                
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
                    'duration': duration,
                    'hop_length': hop_length,
                    'voiced_ratio': voiced_ratio
                }
                status_messages.append(f"Voicing 추출 완료 ({voiced_ratio:.1%} voiced)")
                
            except Exception as e:
                status_messages.append(f"Voice/Unvoice 추출 실패: {str(e)}")

        if features:
            features['duration'] = duration
            features['sample_rate'] = sr
            final_status = f"분석완료 {duration:.2f}초 | " + " | ".join(status_messages)
            return features, final_status
        else:
            return None, "모든 특성 추출 실패"

    except Exception as e:
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

        return combined_line_data if combined_line_data else None

    except Exception as e:
        print(f"❌ 곡선 데이터 생성 오류: {e}")
        return None

def synthesize_and_analyze(piano_roll, attack, decay, sustain, release, wave_type, f0_method="pyin"):
    """노트에서 오디오를 합성하고 특성 분석"""
    global _last_synthesis_config, _synthesis_count
    
    # 현재 분석 설정
    current_analysis_config = {
        'wave_type': wave_type,
        'attack': round(attack, 3),
        'decay': round(decay, 3),
        'sustain': round(sustain, 2), 
        'release': round(release, 3),
        'f0_method': f0_method
    }
    
    # 설정 변경 여부 확인
    analysis_config_changed = (
        current_analysis_config.get('wave_type') != _last_synthesis_config.get('wave_type') or
        current_analysis_config.get('attack') != _last_synthesis_config.get('attack') or
        current_analysis_config.get('decay') != _last_synthesis_config.get('decay') or
        current_analysis_config.get('sustain') != _last_synthesis_config.get('sustain') or
        current_analysis_config.get('release') != _last_synthesis_config.get('release') or
        'f0_method' not in _last_synthesis_config or
        current_analysis_config.get('f0_method') != _last_synthesis_config.get('f0_method', 'pyin')
    )
    
    if analysis_config_changed or _synthesis_count <= 1:
        print("=" * 50)
        print("🎵 오디오 합성 및 특성 분석 시작")
        print(f"📊 선택된 파형: {wave_type}")
        print(f"🎛️ ADSR 설정: A={attack:.3f}, D={decay:.3f}, S={sustain:.2f}, R={release:.3f}")
        print(f"🔬 F0 분석 방법: {f0_method}")
    else:
        print("🔄 동일 설정으로 재분석 시작")

    # 1. 오디오 합성
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)
    if audio_data is None:
        print("❌ 오디오 합성 실패")
        return piano_roll, "오디오 합성 실패", None

    # 2. base64로 변환 (피아노롤용)
    audio_base64 = audio_array_to_base64_wav(audio_data, SAMPLE_RATE)
    if audio_base64 and analysis_config_changed:
        print(f"📦 Base64 변환 완료: {len(audio_base64)} 문자")

    # 3. 임시 WAV 파일 생성
    temp_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)
    if temp_audio_path is None:
        print("❌ 임시 WAV 파일 생성 실패")
        return piano_roll, "임시 오디오 파일 생성 실패", None

    try:
        # 4. 오디오 특성 분석
        if LIBROSA_AVAILABLE:
            if analysis_config_changed:
                print("🔍 오디오 특성 분석 시작...")
            features, analysis_status = extract_audio_features(
                temp_audio_path, f0_method, 
                include_f0=True, include_loudness=True, include_voicing=True
            )
        else:
            if analysis_config_changed:
                print("⚠️ librosa 미설치로 특성 분석 생략")
            features = None
            analysis_status = "librosa 미설치"

        # 5. 피아노롤 업데이트
        updated_piano_roll = piano_roll.copy() if piano_roll else {}
        updated_piano_roll['audio_data'] = audio_base64
        updated_piano_roll['use_backend_audio'] = True

        # 6. 곡선 데이터 생성 및 추가
        line_data = None
        if features:
            tempo = updated_piano_roll.get('tempo', 120)
            pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)
            
            line_data = create_multi_feature_line_data(features, tempo, pixels_per_beat)
            if line_data and analysis_config_changed:
                print(f"📈 {len(line_data)}개 특성 곡선 생성됨")

        # 7. 상태 메시지 생성
        status_parts = [
            f"✅ {wave_type.upper()} 파형으로 오디오 합성 완료",
            f"ADSR: A={attack:.3f} D={decay:.3f} S={sustain:.2f} R={release:.3f}",
            f"길이: {len(audio_data)/SAMPLE_RATE:.2f}초"
        ]

        if features:
            status_parts.append(analysis_status)
            
            if line_data:
                curve_count = len(line_data)
                status_parts.append(f"{curve_count}개 특성 곡선 시각화")

        status_message = " | ".join(status_parts)
        
        if analysis_config_changed:
            print(f"📋 최종 상태: {status_message}")
            print("=" * 50)
        
        # f0_method를 _last_synthesis_config에 저장
        _last_synthesis_config['f0_method'] = f0_method

        return updated_piano_roll, status_message, temp_audio_path

    except Exception as e:
        error_message = f"특성 분석 중 오류 발생: {str(e)}"
        print(f"❌ {error_message}")
        if analysis_config_changed:
            print("=" * 50)
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

# Gradio 인터페이스
with gr.Blocks(title="PianoRoll Comprehensive Demo") as demo:
    gr.Markdown("# 🎹 PianoRoll Comprehensive Demo")
    gr.Markdown("노트를 편집하고 오디오를 합성한 후 특성을 분석하거나, 오디오 파일을 업로드하여 분석해보세요!")

    with gr.Row():
        with gr.Column(scale=3):
            # 초기값 (샘플 노트)
            initial_value = {
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
                "pixelsPerBeat": 80
            }
            piano_roll = PianoRoll(
                height=600,
                width=1000,
                value=initial_value,
                elem_id="piano_roll_main"
            )

        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ 오디오 합성 설정")
            
            # ADSR 설정
            gr.Markdown("**ADSR 엔벨로프**")
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

            # 파형 설정
            gr.Markdown("**파형 타입**")
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
                label="파형 타입"
            )

            # F0 추출 방법
            gr.Markdown("**특성 분석 설정**")
            f0_method_dropdown = gr.Dropdown(
                choices=[
                    ("PYIN (정확, 느림)", "pyin"),
                    ("PipTrack (빠름, 부정확)", "piptrack")
                ],
                value="pyin",
                label="F0 추출 방법"
            )

            # 버튼들
            btn_synthesize = gr.Button(
                "🎶 노트 합성 + 특성 분석",
                variant="primary",
                size="lg"
            )

    with gr.Row():
        # 오디오 업로드 
        gr.Markdown("### 🎤 오디오 파일 분석")
        
    with gr.Row():
        with gr.Column(scale=2):
            audio_input = gr.Audio(
                label="분석할 오디오 파일",
                type="filepath",
                interactive=True
            )
        with gr.Column(scale=1):
            btn_analyze_uploaded = gr.Button(
                "🔬 업로드 파일 분석",
                variant="secondary",
                interactive=LIBROSA_AVAILABLE
            )

    with gr.Row():
        status_text = gr.Textbox(
            label="상태",
            interactive=False,
            lines=3
        )

    with gr.Row():
        reference_audio = gr.Audio(
            label="생성/원본 오디오 (참조용)",
            type="filepath",
            interactive=False
        )

    output_json = gr.JSON(label="피아노롤 데이터")

    # 이벤트 처리
    btn_synthesize.click(
        fn=synthesize_and_analyze,
        inputs=[
            piano_roll,
            attack_slider,
            decay_slider,
            sustain_slider,
            release_slider,
            wave_type_dropdown,
            f0_method_dropdown
        ],
        outputs=[piano_roll, status_text, reference_audio],
        show_progress=True
    )
    
    btn_analyze_uploaded.click(
        fn=analyze_uploaded_audio_features,
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