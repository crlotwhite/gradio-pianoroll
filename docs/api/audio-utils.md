# Audio Utils API

오디오 데이터를 피아노롤 좌표계로 변환하고 커브 데이터를 생성하는 헬퍼 함수들입니다. numpy 배열, 리스트, 단일 값 등 다양한 데이터 형식을 지원하여 AI/ML 전문가들이 쉽게 사용할 수 있습니다.

## 설치 및 임포트

```python
from gradio_pianoroll import (
    PianoRoll,
    PianoRollBackendData,
    Note,
    hz_to_pixels,
    time_to_pixels,
    hz_and_time_to_pixels,
    create_pitch_curve_data,
    create_loudness_curve_data,
    audio_array_to_base64_wav,
    librosa_f0_to_pixels,
    librosa_rms_to_pixels
)
```

## 주요 함수 개요

| 함수명 | 설명 | 입력 | 출력 |
|--------|------|------|------|
| `hz_to_pixels` | Hz를 Y좌표로 변환 | 주파수(Hz) | Y좌표(픽셀) |
| `time_to_pixels` | 시간을 X좌표로 변환 | 시간(초) | X좌표(픽셀) |
| `create_pitch_curve_data` | F0 커브 데이터 생성 | 주파수+시간 배열 | 완전한 커브 데이터 |
| `create_loudness_curve_data` | 라우드니스 커브 생성 | 음량+시간 배열 | 완전한 커브 데이터 |
| `audio_array_to_base64_wav` | 오디오 배열을 WAV로 변환 | numpy 배열 | base64 문자열 |

## 🎯 빠른 시작

### 간단한 Hz 변환

```python
import numpy as np
from gradio_pianoroll import hz_to_pixels, time_to_pixels

# 단일 값 변환
a4_y = hz_to_pixels(440.0)  # A4 → 1290.0 pixels

# 배열 변환 (numpy, list 모두 지원)
freqs = [440.0, 523.25, 659.25]  # A4, C5, E5
y_coords = hz_to_pixels(freqs)
print(y_coords)  # [1290.0, 1230.0, 1170.0]

# 시간 변환
times = [0.5, 1.0, 1.5]  # 초
x_coords = time_to_pixels(times, tempo=120)
print(x_coords)  # [80.0, 160.0, 240.0]
```

### librosa와 함께 사용

```python
import librosa
from gradio_pianoroll import create_pitch_curve_data, PianoRoll

# 오디오 분석
y, sr = librosa.load("audio.wav")
f0, voiced_flag, voiced_probs = librosa.pyin(y, sr=sr)

# 시간축 계산
times = librosa.frames_to_time(np.arange(len(f0)), sr=sr)

# 유효한 F0만 필터링
valid_mask = voiced_flag & (f0 > 0)
valid_f0 = f0[valid_mask]
valid_times = times[valid_mask]

# 피치 커브 생성
pitch_curve = create_pitch_curve_data(valid_f0, valid_times)

# 새로운 방식: 백엔드 데이터 사용
backend_data = PianoRollBackendData()
backend_data.add_curve("f0_curve", pitch_curve)

piano_roll = PianoRoll(
    value={"notes": []},
    backend_data=backend_data
)

# 기존 방식도 여전히 지원
piano_roll_legacy = PianoRoll(value={
    "notes": [],
    "line_data": {"f0_curve": pitch_curve}
})
```

## 📚 상세 API 문서

### hz_to_pixels()

**Signature:**
```python
hz_to_pixels(frequency: Union[float, np.ndarray, List[float]]) -> Union[float, np.ndarray]
```

주파수(Hz)를 피아노롤 Y좌표로 변환합니다.

**Parameters:**
- `frequency`: 주파수 값 (Hz) - 단일값, 리스트, numpy 배열 모두 지원

**Returns:**
- 입력과 같은 타입의 Y좌표 값 (픽셀)

**Examples:**
```python
# 음계 변환
notes = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
}

for note_name, freq in notes.items():
    y_pos = hz_to_pixels(freq)
    print(f"{note_name}: {freq:.2f}Hz → Y={y_pos:.1f}px")

# NumPy 배열 처리
freq_array = np.array(list(notes.values()))
y_positions = hz_to_pixels(freq_array)
```

### time_to_pixels()

**Signature:**
```python
time_to_pixels(time_seconds: Union[float, np.ndarray, List[float]], 
               tempo: float = 120, 
               pixels_per_beat: float = 80) -> Union[float, np.ndarray]
```

시간(초)을 피아노롤 X좌표로 변환합니다.

**Parameters:**
- `time_seconds`: 시간 값 (초)
- `tempo`: 템포 (BPM, 기본값: 120)
- `pixels_per_beat`: 박자당 픽셀 수 (기본값: 80)

**Examples:**
```python
# 다양한 템포에서의 변환
times = [0, 0.5, 1.0, 1.5, 2.0]

for tempo in [60, 120, 180]:
    x_coords = time_to_pixels(times, tempo=tempo)
    print(f"템포 {tempo}BPM: {x_coords}")

# 줌 레벨 변경
x_normal = time_to_pixels(times, pixels_per_beat=80)   # 기본
x_zoomed = time_to_pixels(times, pixels_per_beat=160)  # 2배 확대
```

### create_pitch_curve_data()

**Signature:**
```python
create_pitch_curve_data(frequency: Union[np.ndarray, List[float]], 
                        time_seconds: Union[np.ndarray, List[float]],
                        tempo: float = 120,
                        pixels_per_beat: float = 80,
                        color: str = "#FF6B6B",
                        line_width: int = 3,
                        opacity: float = 0.8) -> Dict[str, Any]
```

완전한 F0 커브 데이터를 생성합니다.

**Parameters:**
- `frequency`: 주파수 배열 (Hz)
- `time_seconds`: 시간 배열 (초)
- `tempo`: 템포 (BPM)
- `pixels_per_beat`: 박자당 픽셀 수
- `color`: 커브 색상 (기본값: "#FF6B6B")
- `line_width`: 선 두께 (기본값: 3)
- `opacity`: 투명도 0-1 (기본값: 0.8)

**Returns:**
- 피아노롤 LineLayer용 완전한 커브 데이터 딕셔너리

**Examples:**
```python
# 글라이드 효과 생성
duration = 3.0
num_points = 300
times = np.linspace(0, duration, num_points)

# A4에서 C5로 부드럽게 상승
start_freq, end_freq = 440.0, 523.25
frequencies = start_freq + (end_freq - start_freq) * (times / duration)

# 비브라토 추가
vibrato = 5 * np.sin(2 * np.pi * 6 * times)  # 6Hz 비브라토
frequencies += vibrato

# 커브 데이터 생성
pitch_curve = create_pitch_curve_data(
    frequencies, times,
    color="#FF4444",
    line_width=4,
    opacity=0.9
)

# 여러 커브 조합
curves = {
    "main_melody": pitch_curve,
    "harmony": create_pitch_curve_data(
        frequencies * 1.25,  # 완전 4도 위
        times,
        color="#4444FF",
        line_width=2
    )
}
```

### create_loudness_curve_data()

**Signature:**
```python
create_loudness_curve_data(loudness: Union[np.ndarray, List[float]], 
                          time_seconds: Union[np.ndarray, List[float]],
                          tempo: float = 120,
                          pixels_per_beat: float = 80,
                          use_db: bool = True,
                          y_min: Optional[float] = None,
                          y_max: Optional[float] = None,
                          color: str = "#4ECDC4",
                          line_width: int = 2,
                          opacity: float = 0.6) -> Dict[str, Any]
```

완전한 라우드니스 커브 데이터를 생성합니다.

**Examples:**
```python
# RMS 에너지 분석
y, sr = librosa.load("audio.wav")
rms = librosa.feature.rms(y=y, hop_length=512)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

# dB 스케일로 변환
rms_db = 20 * np.log10(np.maximum(rms/np.max(rms), 1e-6))

# 라우드니스 커브 생성
loudness_curve = create_loudness_curve_data(
    rms_db, times,
    use_db=True,
    y_min=-60,  # -60dB 최소값
    y_max=0,    # 0dB 최대값
    color="#00CCCC"
)

# 다중 특성 분석
spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
brightness_curve = create_loudness_curve_data(
    spectral_centroids, times,
    use_db=False,
    color="#FFAA00",
    line_width=1
)
```

### audio_array_to_base64_wav()

**Signature:**
```python
audio_array_to_base64_wav(audio_data: np.ndarray, 
                         sample_rate: int = 44100,
                         normalize: bool = True) -> str
```

numpy 오디오 배열을 base64 WAV 문자열로 변환합니다.

**Examples:**
```python
# 합성 오디오 생성
duration = 2.0
sr = 44100
t = np.linspace(0, duration, int(duration * sr))

# A4 사인파 생성
audio = 0.3 * np.sin(2 * np.pi * 440 * t)

# ADSR 엔벨로프 적용
fade_len = int(0.1 * sr)
audio[:fade_len] *= np.linspace(0, 1, fade_len)    # Attack
audio[-fade_len:] *= np.linspace(1, 0, fade_len)   # Release

# base64 변환
audio_base64 = audio_array_to_base64_wav(audio, sr)

# 피아노롤에 설정
piano_roll = PianoRoll(value={
    "notes": [],
    "audio_data": audio_base64,
    "use_backend_audio": True
})
```

## 🚀 librosa 통합 함수

### librosa_f0_to_pixels()

librosa F0 추출 결과를 직접 픽셀 좌표로 변환합니다.

```python
import librosa
from gradio_pianoroll import librosa_f0_to_pixels

# F0 추출
y, sr = librosa.load("vocal.wav", sr=22050)
f0, voiced_flag, voiced_probs = librosa.pyin(y, sr=sr, hop_length=512)

# 직접 픽셀 좌표로 변환
f0_x_pixels, f0_y_pixels = librosa_f0_to_pixels(
    f0, sr=sr, hop_length=512, tempo=120
)

print(f"유효한 F0 포인트: {len(f0_x_pixels)}개")
```

### librosa_rms_to_pixels()

librosa RMS 추출 결과를 직접 픽셀 좌표로 변환합니다.

```python
# RMS 추출
rms = librosa.feature.rms(y=y, hop_length=512)[0]

# 픽셀 좌표로 변환 (dB 스케일)
rms_x_pixels, rms_y_pixels = librosa_rms_to_pixels(
    rms, sr=sr, hop_length=512, to_db=True
)
```

## 🔧 고급 활용 예제

### 실시간 오디오 분석 파이프라인

```python
def analyze_audio_realtime(audio_file, tempo=120):
    """실시간 오디오 분석 결과를 피아노롤로 시각화"""
    
    # 오디오 로드
    y, sr = librosa.load(audio_file, sr=22050)
    
    # 특성 추출
    f0, voiced_flag, voiced_probs = librosa.pyin(y, sr=sr)
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # 시간축
    hop_length = 512
    times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)
    
    # 신뢰도 높은 F0만 사용
    reliable_mask = voiced_flag & (f0 > 0) & (voiced_probs > 0.8)
    
    curves = {}
    
    # F0 커브
    if np.any(reliable_mask):
        curves["f0"] = create_pitch_curve_data(
            f0[reliable_mask], times[reliable_mask], 
            tempo=tempo, color="#FF6B6B"
        )
    
    # RMS 커브 (dB)
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
    rms_db = 20 * np.log10(np.maximum(rms/np.max(rms), 1e-6))
    
    curves["loudness"] = create_loudness_curve_data(
        rms_db, rms_times, tempo=tempo,
        use_db=True, y_min=-40, y_max=0, color="#4ECDC4"
    )
    
    # MFCC 첫 번째 계수 (spectral centroid와 유사)
    mfcc_times = librosa.frames_to_time(np.arange(mfccs.shape[1]), sr=sr, hop_length=hop_length)
    curves["timbre"] = create_loudness_curve_data(
        mfccs[1], mfcc_times, tempo=tempo,  # 두 번째 MFCC 계수
        use_db=False, color="#9B59B6", line_width=1
    )
    
    # 오디오 데이터
    audio_base64 = audio_array_to_base64_wav(y, sr)
    
    return {
        "notes": [],
        "tempo": tempo,
        "line_data": curves,
        "audio_data": audio_base64,
        "use_backend_audio": True
    }
```

### AI 모델 출력 후처리

```python
def process_ai_singing_synthesis(ai_f0_pred, ai_loudness_pred, phoneme_durations, tempo=120):
    """AI 노래 합성 모델의 출력을 피아노롤로 변환"""
    
    # 프레임을 시간으로 변환 (25ms 프레임 가정)
    frame_duration = 0.025
    times = np.arange(len(ai_f0_pred)) * frame_duration
    
    # F0 후처리 (평활화)
    from scipy import signal
    smoothed_f0 = signal.savgol_filter(ai_f0_pred, 15, 3)
    
    # 보이싱된 구간만 추출 (임계값 기반)
    voiced_mask = ai_f0_pred > 80  # 80Hz 이상
    
    # 커브 생성
    curves = {}
    
    if np.any(voiced_mask):
        curves["ai_f0"] = create_pitch_curve_data(
            smoothed_f0[voiced_mask], times[voiced_mask],
            tempo=tempo, color="#E74C3C", line_width=3
        )
    
    # 라우드니스 커브
    curves["ai_loudness"] = create_loudness_curve_data(
        ai_loudness_pred, times, tempo=tempo,
        use_db=False, color="#3498DB", line_width=2
    )
    
    # 음소 경계 표시 (세그먼트 데이터로)
    segment_data = []
    current_time = 0
    
    for i, duration in enumerate(phoneme_durations):
        segment_data.append({
            "start": current_time,
            "end": current_time + duration,
            "type": "phoneme",
            "value": f"phoneme_{i}",
            "confidence": 1.0
        })
        current_time += duration
    
    return {
        "notes": [],
        "tempo": tempo,
        "line_data": curves,
        "segment_data": segment_data
    }
```

### 배치 처리 최적화

```python
def batch_process_audio_files(file_list, batch_size=4, tempo=120):
    """다수의 오디오 파일을 배치로 효율적 처리"""
    
    all_results = {}
    
    for i in range(0, len(file_list), batch_size):
        batch_files = file_list[i:i+batch_size]
        
        # 병렬 처리 (multiprocessing)
        from multiprocessing import Pool
        
        with Pool(processes=batch_size) as pool:
            batch_results = pool.map(
                lambda f: analyze_audio_realtime(f, tempo), 
                batch_files
            )
        
        # 결과 저장
        for file_path, result in zip(batch_files, batch_results):
            filename = os.path.basename(file_path)
            all_results[filename] = result
    
    return all_results
```

## ⚡ 성능 최적화 팁

### 메모리 효율적 처리

```python
# 대용량 배열 처리 시
def process_large_f0_array(f0_array, times_array, chunk_size=10000):
    """대용량 F0 배열을 청크 단위로 처리"""
    
    all_data_points = []
    
    for i in range(0, len(f0_array), chunk_size):
        chunk_f0 = f0_array[i:i+chunk_size]
        chunk_times = times_array[i:i+chunk_size]
        
        # 유효한 값만 처리
        valid_mask = np.isfinite(chunk_f0) & (chunk_f0 > 0)
        if np.any(valid_mask):
            x, y = hz_and_time_to_pixels(
                chunk_f0[valid_mask], 
                chunk_times[valid_mask]
            )
            
            chunk_points = [
                {"x": float(x_val), "y": float(y_val)} 
                for x_val, y_val in zip(x, y)
            ]
            all_data_points.extend(chunk_points)
    
    return all_data_points
```

### GPU 가속 (CuPy 사용)

```python
try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

def gpu_accelerated_conversion(frequencies, times):
    """GPU를 사용한 고속 좌표 변환"""
    if not GPU_AVAILABLE:
        return hz_and_time_to_pixels(frequencies, times)
    
    # GPU로 데이터 전송
    freq_gpu = cp.asarray(frequencies)
    times_gpu = cp.asarray(times)
    
    # GPU에서 계산
    midi_gpu = 69 + 12 * cp.log2(freq_gpu / 440.0)
    y_gpu = (128 - 1 - midi_gpu) * 20 + 10
    x_gpu = times_gpu * (120 / 60.0) * 80
    
    # CPU로 결과 반환
    return cp.asnumpy(x_gpu), cp.asnumpy(y_gpu)
```

이 API를 사용하면 복잡한 좌표 변환 로직을 신경 쓰지 않고도 오디오 분석 결과를 피아노롤에서 직관적으로 시각화할 수 있습니다. 