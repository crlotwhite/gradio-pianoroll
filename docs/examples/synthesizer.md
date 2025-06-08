# 신디사이저 데모 (Synthesizer Demo)

🎵 **신디사이저 데모**는 피아노롤에서 생성한 음표들을 실제 오디오로 합성하고 재생하는 기능을 보여줍니다.
다양한 파형과 ADSR 엔벨로프를 적용하여 풍부한 사운드를 만들 수 있습니다.

## 🎯 학습 목표

- 실시간 오디오 합성 시스템 이해
- ADSR 엔벨로프의 개념과 적용
- 다양한 파형 타입의 특성 비교
- 백엔드 오디오 엔진 활용법
- 웨이브폼 시각화 기능

## 📋 핵심 코드

### 1. 기본 설정

```python
import gradio as gr
import numpy as np
from gradio_pianoroll import PianoRoll

# 신디사이저 설정
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # 최대 10초

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    """피아노롤 데이터에서 오디오 합성"""
    if not piano_roll_data or 'notes' not in piano_roll_data:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # 총 길이 계산
    max_end_time = 0
    for note in notes:
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    total_duration = min(max_end_time + 1.0, MAX_DURATION)
    total_samples = int(total_duration * SAMPLE_RATE)
    audio_buffer = np.zeros(total_samples)

    # 각 음표 처리
    for note in notes:
        pitch = note['pitch']
        velocity = note.get('velocity', 100)

        # 시간 계산
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

        if start_seconds >= total_duration or duration_seconds <= 0:
            continue

        # 주파수 계산
        frequency = midi_to_frequency(pitch)
        volume = velocity / 127.0

        # 복합 파형 생성
        wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

        # ADSR 엔벨로프 적용
        envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)
        note_audio = wave * envelope * volume * 0.25

        # 오디오 버퍼에 추가
        start_sample = int(start_seconds * SAMPLE_RATE)
        end_sample = start_sample + len(note_audio)

        if start_sample < total_samples:
            end_sample = min(end_sample, total_samples)
            audio_length = end_sample - start_sample
            if audio_length > 0:
                audio_buffer[start_sample:end_sample] += note_audio[:audio_length]

    # 클리핑 방지 (정규화)
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9

    return audio_buffer
```

### 2. UI 구성

```python
with gr.Blocks() as demo:
    gr.Markdown("## 🎹 신디사이저 데모")

    with gr.Row():
        with gr.Column(scale=3):
            # 피아노롤 컴포넌트
            piano_roll_synth = PianoRoll(
                height=600,
                width=1000,
                value=initial_value_synth,
                use_backend_audio=True  # 백엔드 오디오 엔진 사용
            )

        with gr.Column(scale=1):
            # ADSR 설정
            gr.Markdown("### 🎛️ ADSR 설정")
            attack_slider = gr.Slider(0.001, 1.0, 0.01, label="Attack (초)")
            decay_slider = gr.Slider(0.001, 1.0, 0.1, label="Decay (초)")
            sustain_slider = gr.Slider(0.0, 1.0, 0.7, label="Sustain (레벨)")
            release_slider = gr.Slider(0.001, 2.0, 0.3, label="Release (초)")

            # 파형 설정
            wave_type_dropdown = gr.Dropdown(
                choices=[
                    ("복합 파형", "complex"),
                    ("하모닉 합성", "harmonic"),
                    ("FM 합성", "fm"),
                    ("톱니파", "sawtooth"),
                    ("사각파", "square"),
                    ("삼각파", "triangle"),
                    ("사인파", "sine")
                ],
                value="complex",
                label="파형 타입"
            )

    # 합성 버튼
    btn_synthesize = gr.Button("🎶 오디오 합성", variant="primary")

    # 이벤트 처리
    btn_synthesize.click(
        fn=synthesize_and_play,
        inputs=[piano_roll_synth, attack_slider, decay_slider,
                sustain_slider, release_slider, wave_type_dropdown],
        outputs=[piano_roll_synth, status_text, audio_output],
        show_progress=True
    )
```

## 🎛️ ADSR 엔벨로프

### 개념 이해

ADSR은 음의 시간에 따른 음량 변화를 제어하는 시스템입니다:

- **Attack (어택)**: 음이 시작되어 최대 음량에 도달하는 시간
- **Decay (디케이)**: 최대 음량에서 서스테인 레벨로 감소하는 시간
- **Sustain (서스테인)**: 음이 지속되는 동안 유지되는 음량 레벨
- **Release (릴리즈)**: 음이 끝날 때 0으로 감소하는 시간

### 구현 코드

```python
def create_adsr_envelope(attack, decay, sustain, release, duration, sample_rate):
    """ADSR 엔벨로프 생성"""
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

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
```

### 파라미터 가이드

| 설정 | Attack | Decay | Sustain | Release | 효과 |
|------|--------|-------|---------|---------|------|
| 피아노 | 0.01 | 0.3 | 0.3 | 0.5 | 즉시 시작, 빠른 감쇠 |
| 스트링 | 0.1 | 0.2 | 0.8 | 1.0 | 부드러운 시작과 끝 |
| 오르간 | 0.0 | 0.0 | 1.0 | 0.1 | 즉시 시작, 일정 음량 |
| 패드 | 0.5 | 0.5 | 0.7 | 2.0 | 매우 부드러운 전체 |

## 🌊 파형 타입

### 1. 기본 파형

#### 사인파 (Sine Wave)
```python
def generate_sine_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)
```
- **특성**: 가장 순수한 음색, 배음 없음
- **용도**: 베이스, 부드러운 리드

#### 톱니파 (Sawtooth Wave)
```python
def generate_sawtooth_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * (t * frequency % 1) - 1
```
- **특성**: 모든 배음 포함, 밝고 거친 음색
- **용도**: 브라스, 리드 신스

#### 사각파 (Square Wave)
```python
def generate_square_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sign(np.sin(2 * np.pi * frequency * t))
```
- **특성**: 홀수 배음만 포함, 중공한 음색
- **용도**: 클라리넷, 칩튠 음색

#### 삼각파 (Triangle Wave)
```python
def generate_triangle_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1
```
- **특성**: 홀수 배음, 사각파보다 부드러움
- **용도**: 플루트, 부드러운 리드

### 2. 고급 파형

#### 하모닉 합성 (Harmonic Synthesis)
```python
def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # 기본 주파수
    wave += np.sin(2 * np.pi * frequency * t)

    # 배음 추가 (진폭은 1/n로 감소)
    for n in range(2, harmonics + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    return wave / np.max(np.abs(wave))
```
- **특성**: 자연스러운 악기 음색 모방
- **용도**: 현악기, 관악기 시뮬레이션

#### FM 합성 (Frequency Modulation)
```python
def generate_fm_wave(frequency, duration, sample_rate, mod_freq=5.0, mod_depth=2.0):
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # 모듈레이터
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # 주파수 변조된 캐리어
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier
```
- **특성**: 복잡하고 다이내믹한 음색
- **용도**: 벨, 전자음, 특수 효과

## 🎚️ 실시간 효과

### 비브라토 (Vibrato)
```python
# 주파수 변조
vibrato_freq = 4.5  # 4.5Hz
vibrato_depth = 0.02  # 2% 주파수 변조
vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
```

### 트레몰로 (Tremolo)
```python
# 음량 변조
tremolo_freq = 3.0  # 3Hz
tremolo_depth = 0.1  # 10% 음량 변조
tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)
```

## 📊 웨이브폼 시각화

### 웨이브폼 데이터 생성
```python
def calculate_waveform_data(audio_data, pixels_per_beat, tempo, target_width=1000):
    """오디오 데이터에서 웨이브폼 시각화 데이터 계산"""
    audio_duration = len(audio_data) / SAMPLE_RATE
    total_pixels = (tempo / 60) * pixels_per_beat * audio_duration
    samples_per_pixel = len(audio_data) / total_pixels

    waveform_points = []

    for pixel in range(int(total_pixels)):
        start_sample = int(pixel * samples_per_pixel)
        end_sample = int((pixel + 1) * samples_per_pixel)

        if start_sample < len(audio_data):
            pixel_data = audio_data[start_sample:end_sample]
            min_val = float(np.min(pixel_data))
            max_val = float(np.max(pixel_data))

            waveform_points.append({
                'x': pixel,
                'min': min_val,
                'max': max_val
            })

    return waveform_points
```

## 💡 실습 가이드

### 1. 기본 합성 실습

1. **기본 음표 생성**
   - C4, E4, G4로 C 메이저 코드 만들기
   - 템포 120으로 설정

2. **ADSR 실험**
   - Attack: 0.01 → 0.5 (부드러운 시작)
   - Decay: 0.1 → 1.0 (긴 감쇠)
   - Sustain: 0.7 → 0.3 (약한 지속)
   - Release: 0.3 → 2.0 (긴 여운)

3. **파형 비교**
   - 각 파형별로 같은 음표 합성
   - 음색 차이 비교 분석

### 2. 악기 시뮬레이션

#### 피아노 시뮬레이션
```python
# 설정
wave_type = "complex"
attack = 0.01
decay = 0.3
sustain = 0.3
release = 0.8
```

#### 스트링 시뮬레이션
```python
# 설정
wave_type = "harmonic"
attack = 0.1
decay = 0.2
sustain = 0.8
release = 1.5
```

#### 오르간 시뮬레이션
```python
# 설정
wave_type = "sine"
attack = 0.0
decay = 0.0
sustain = 1.0
release = 0.1
```

### 3. 고급 실습

1. **멜로디 라인 만들기**
   - 8마디 멜로디 작성
   - 다양한 리듬 패턴 적용

2. **코드 진행 만들기**
   - I-V-vi-IV 진행 (C-G-Am-F)
   - 각 코드 4박자씩

3. **베이스라인 추가**
   - 낮은 옥타브로 루트 음 추가
   - 긴 음표로 안정감 제공

## ❓ 문제 해결

### 자주 묻는 질문

**Q: 오디오가 재생되지 않아요**
A: `use_backend_audio=True` 설정을 확인하고, 브라우저 오디오 권한을 확인하세요.

**Q: 음이 깨지거나 왜곡돼요**
A: 음표가 너무 많거나 velocity가 높을 수 있습니다. 음표 수를 줄이거나 velocity를 낮춰보세요.

**Q: ADSR 설정이 적용되지 않아요**
A: "🎶 오디오 합성" 버튼을 다시 클릭하여 새로운 설정으로 재합성하세요.

### 성능 최적화

1. **메모리 사용량 줄이기**
   - 최대 지속시간 제한 (MAX_DURATION)
   - 음표 수 제한 (권장: 50개 이하)

2. **CPU 사용량 줄이기**
   - 복잡한 파형보다 기본 파형 사용
   - 샘플레이트 조정 (44100 → 22050)

## 🔗 다음 단계

신디사이저 기능을 익혔다면 다음 예제들을 확인해보세요:

- **[음성학 처리](phoneme-processing.md)**: 가사와 음성학 데이터 활용
- **[F0 분석](f0-analysis.md)**: 실제 오디오에서 음높이 추출
- **[오디오 특성 분석](audio-features.md)**: 종합적인 오디오 분석

## 📚 관련 자료

- [신디사이저 가이드](../guides/synthesizer.md): 상세한 오디오 합성 이론
- [타이밍 변환](../guides/timing-conversions.md): 픽셀-시간 변환 원리
- [API 참조](../api/events.md): 오디오 관련 이벤트 명세