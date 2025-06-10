# F0 분석과 피아노롤 시각화

기본 주파수(F0) 분석 결과를 PianoRoll 컴포넌트에서 시각화하고 활용하는 방법을 설명합니다.

## 개요

F0(Fundamental Frequency)는 음성과 음악에서 가장 중요한 특성 중 하나입니다. gradio-pianoroll은 librosa를 활용하여 F0를 추출하고 이를 피아노롤에서 시각화할 수 있습니다.

## 기본 F0 분석

```python
import gradio as gr
import librosa
import numpy as np
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.audio_utils import librosa_f0_to_pixels

def analyze_f0(audio_file):
    """오디오 파일에서 F0 추출"""
    if audio_file is None:
        return None, "오디오 파일을 업로드하세요."

    try:
        # 오디오 로드
        y, sr = librosa.load(audio_file, sr=22050)

        # F0 추출 (PYIN 알고리즘 사용)
        f0 = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        f0_values = f0[0]  # 주파수 값들

        # 유효한 F0 값만 추출 (NaN 제거)
        valid_f0 = f0_values[~np.isnan(f0_values)]

        if len(valid_f0) == 0:
            return None, "F0를 추출할 수 없습니다."

        # 피아노롤용 곡선 데이터 생성
        curve_data = librosa_f0_to_pixels(f0_values, sr=sr)

        # 평균 피치 정보
        avg_f0 = np.mean(valid_f0)
        avg_midi = librosa.hz_to_midi(avg_f0)

        info_text = f"""
        F0 분석 결과:
        - 평균 주파수: {avg_f0:.2f} Hz
        - 평균 MIDI 노트: {avg_midi:.1f}
        - 유효한 F0 포인트: {len(valid_f0)}개
        - 전체 길이: {len(f0_values)}개
        """

        return curve_data, info_text

    except Exception as e:
        return None, f"오류 발생: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# F0 분석 데모")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="분석할 오디오 파일",
                type="filepath"
            )
            analyze_btn = gr.Button("F0 분석 시작")

        with gr.Column():
            f0_info = gr.Textbox(
                label="분석 결과",
                lines=6,
                interactive=False
            )

    piano_roll = PianoRoll(
        label="F0 시각화",
        height=400,
        width=800
    )

    analyze_btn.click(
        fn=analyze_f0,
        inputs=audio_input,
        outputs=[piano_roll, f0_info]
    )

if __name__ == "__main__":
    demo.launch()
```

## 고급 F0 분석

### 다중 F0 추출 방법 비교

```python
def compare_f0_methods(audio_file):
    """여러 F0 추출 방법 비교"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 1. PYIN 방법
    f0_pyin, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
    )

    # 2. YIN 방법 (piptrack 사용)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    f0_yin = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        f0_yin.append(pitch if pitch > 0 else np.nan)
    f0_yin = np.array(f0_yin)

    return {
        'pyin': f0_pyin,
        'yin': f0_yin,
        'voiced_probability': voiced_probs
    }
```

### 실시간 F0 추적

```python
def real_time_f0_tracking(audio_stream, chunk_size=1024):
    """실시간 F0 추적"""
    buffer = []
    f0_history = []

    def process_chunk(chunk):
        buffer.extend(chunk)

        if len(buffer) >= chunk_size:
            # 최근 데이터로 F0 추출
            y = np.array(buffer[-chunk_size:])
            f0, _, _ = librosa.pyin(y, fmin=80, fmax=400)

            # 유효한 F0만 히스토리에 추가
            valid_f0 = f0[~np.isnan(f0)]
            if len(valid_f0) > 0:
                f0_history.append(np.mean(valid_f0))

            # 버퍼 크기 제한
            if len(buffer) > chunk_size * 2:
                buffer = buffer[-chunk_size:]

        return f0_history

    return process_chunk
```

## 피아노롤과 F0 연동

### F0 곡선을 노트로 변환

```python
def f0_to_notes(f0_values, sr=22050, note_threshold=0.1):
    """F0 곡선을 개별 노트로 변환"""
    notes = []
    current_note = None

    hop_length = 512  # librosa 기본값
    frame_duration = hop_length / sr  # 초 단위

    for i, f0 in enumerate(f0_values):
        if np.isnan(f0) or f0 <= 0:
            # 무음 구간 - 현재 노트 종료
            if current_note:
                current_note['duration_pixels'] = (i - current_note['start_frame']) * frame_duration * 80
                notes.append(current_note)
                current_note = None
        else:
            midi_note = librosa.hz_to_midi(f0)

            if current_note is None:
                # 새 노트 시작
                current_note = {
                    'pitch': round(midi_note),
                    'start_pixels': i * frame_duration * 80,
                    'start_frame': i,
                    'velocity': 100
                }
            else:
                # 피치 변화 감지
                pitch_diff = abs(midi_note - current_note['pitch'])
                if pitch_diff > note_threshold:
                    # 기존 노트 종료하고 새 노트 시작
                    current_note['duration_pixels'] = (i - current_note['start_frame']) * frame_duration * 80
                    notes.append(current_note)

                    current_note = {
                        'pitch': round(midi_note),
                        'start_pixels': i * frame_duration * 80,
                        'start_frame': i,
                        'velocity': 100
                    }

    # 마지막 노트 처리
    if current_note:
        current_note['duration_pixels'] = (len(f0_values) - current_note['start_frame']) * frame_duration * 80
        notes.append(current_note)

    return notes
```

### F0 기반 멜로디 생성

```python
def generate_melody_from_f0(f0_values, quantize_to_scale=True):
    """F0 곡선에서 멜로디 생성"""
    # 유효한 F0만 추출
    valid_f0 = f0_values[~np.isnan(f0_values)]

    if len(valid_f0) == 0:
        return []

    # MIDI 노트로 변환
    midi_notes = librosa.hz_to_midi(valid_f0)

    if quantize_to_scale:
        # C 메이저 스케일로 양자화
        c_major = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        quantized_notes = []

        for note in midi_notes:
            octave = int(note // 12)
            semitone = int(note % 12)

            # 가장 가까운 스케일 노트 찾기
            closest_semitone = min(c_major, key=lambda x: abs(x - semitone))
            quantized_note = octave * 12 + closest_semitone
            quantized_notes.append(quantized_note)

        midi_notes = quantized_notes

    # 노트 리스트 생성
    notes = []
    for i, pitch in enumerate(midi_notes):
        note = {
            'pitch': int(pitch),
            'start_pixels': i * 40,  # 좀 더 조밀하게
            'duration_pixels': 40,
            'velocity': 100
        }
        notes.append(note)

    return notes
```

## 음성 분석 활용

### 보컬 피치 분석

```python
def vocal_pitch_analysis(audio_file):
    """보컬 음성의 피치 분석"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 스펙트로그램에서 하모닉 분리
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # 하모닉 성분에서 F0 추출
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y_harmonic,
        fmin=librosa.note_to_hz('C3'),  # 보컬 범위
        fmax=librosa.note_to_hz('C6')
    )

    # 보컬 특성 분석
    vocal_stats = {
        'range_semitones': np.ptp(librosa.hz_to_midi(f0[~np.isnan(f0)])),
        'avg_pitch': np.mean(f0[~np.isnan(f0)]),
        'pitch_stability': np.std(f0[~np.isnan(f0)]),
        'voiced_ratio': np.mean(voiced_flag)
    }

    return f0, vocal_stats
```

### 악기 피치 추적

```python
def instrument_pitch_tracking(audio_file, instrument_type='violin'):
    """악기별 최적화된 피치 추적"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 악기별 주파수 범위 설정
    ranges = {
        'violin': ('G3', 'E7'),
        'cello': ('C2', 'C6'),
        'piano': ('A0', 'C8'),
        'guitar': ('E2', 'E6')
    }

    fmin, fmax = ranges.get(instrument_type, ('C2', 'C7'))

    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz(fmin),
        fmax=librosa.note_to_hz(fmax),
        threshold=0.1,  # 악기에 따라 조정
        frame_length=2048
    )

    return f0, voiced_probs
```

## 참고 자료

- [Librosa F0 분석 문서](https://librosa.org/doc/main/generated/librosa.pyin.html)
- [피아노롤 기본 사용법](basic-usage.md)
- [오디오 특성 분석](audio-features.md)

## 다음 단계

- [오디오 특성 종합 분석](audio-features.md)
- [음성 합성과 F0 연동](synthesizer.md)
- [실시간 오디오 처리](../user-guide/audio-analysis.md)