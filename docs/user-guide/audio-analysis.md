# 오디오 특성 분석

Gradio PianoRoll 컴포넌트는 고급 오디오 분석 기능을 제공하여 음성과 음악의 다양한 특성을 시각화하고 분석할 수 있습니다. 이 가이드에서는 F0(기본 주파수), Loudness(음량), Voice/Unvoice 분석 등 주요 오디오 특성 분석 기능을 상세히 설명합니다.

## 📊 지원하는 오디오 특성

### 1. F0 (Fundamental Frequency) 분석
기본 주파수(피치) 추출 및 시각화:
- **PYIN 알고리즘**: 높은 정확도, 긴 처리 시간
- **PipTrack 알고리즘**: 빠른 처리, 중간 정확도
- 실시간 피치 곡선 시각화
- MIDI 노트와 연동된 피치 매핑

### 2. Loudness 분석
음량(데시벨) 추출 및 시각화:
- RMS(Root Mean Square) 기반 음량 계산
- 데시벨 변환 옵션
- 시간에 따른 음량 변화 곡선
- 사용자 정의 Y축 범위 설정

### 3. Voice/Unvoice 분석
유성음/무성음 구분:
- 확률 기반 또는 이진 분류
- 음성학적 특성 분석
- 발음 품질 평가 지원

## 🎵 기본 사용법

### 노트에서 오디오 생성 후 분석

```python
import gradio as gr
from gradio_pianoroll import PianoRoll, PianoRollBackendData, Note

def analyze_generated_audio(piano_roll_data):
    """피아노롤 노트에서 오디오를 생성하고 분석"""
    
    # 신디사이저 설정
    adsr_settings = {
        "attack": 0.01,
        "decay": 0.1,
        "sustain": 0.7,
        "release": 0.3
    }
    
    # 분석할 특성 선택
    analysis_settings = {
        "include_f0": True,
        "include_loudness": True,
        "include_voicing": True,
        "f0_method": "pyin"
    }
    
    # 백엔드에서 오디오 생성 및 분석 수행
    # (실제 구현은 backend 함수 참조)
    
    return piano_roll_data

with gr.Blocks() as demo:
    # 백엔드 데이터 설정
    backend_data = PianoRollBackendData()
    backend_data.enable_backend_audio(True)  # 백엔드 오디오 엔진 사용
    
    # Note 클래스로 초기 노트 생성
    initial_note = Note(
        pitch=60,
        velocity=100,
        lyric="도",
        start_pixels=0,
        duration_pixels=320
    )
    
    piano_roll = PianoRoll(
        value={
            "notes": [initial_note.to_dict()],
            "tempo": 120
        },
        backend_data=backend_data
    )
    
    analyze_btn = gr.Button("오디오 생성 & 분석")
    analyze_btn.click(
        fn=analyze_generated_audio,
        inputs=[piano_roll],
        outputs=[piano_roll]
    )
```

### 업로드된 오디오 분석

```python
def analyze_uploaded_audio(piano_roll_data, audio_file):
    """업로드된 오디오 파일 분석 (새로운 방식)"""
    
    if not audio_file:
        return piano_roll_data
    
    # 오디오 특성 추출
    features = extract_audio_features(
        audio_file_path=audio_file,
        f0_method="pyin",
        include_f0=True,
        include_loudness=True,
        include_voicing=True
    )
    
    # 백엔드 데이터로 분석 결과 적용 (새로운 방식)
    piano_roll.add_curve_data("f0_curve", features.get("f0", []))
    piano_roll.add_curve_data("loudness_curve", features.get("loudness", []))
    piano_roll.add_curve_data("voicing_curve", features.get("voicing", []))
    
    return piano_roll_data

def analyze_uploaded_audio_legacy(piano_roll_data, audio_file):
    """업로드된 오디오 파일 분석 (기존 방식)"""
    
    if not audio_file:
        return piano_roll_data
    
    # 오디오 특성 추출
    features = extract_audio_features(
        audio_file_path=audio_file,
        f0_method="pyin",
        include_f0=True,
        include_loudness=True,
        include_voicing=True
    )
    
    # 기존 방식: 딕셔너리에 직접 추가
    piano_roll_data["curve_data"] = {
        "f0_curve": features.get("f0", []),
        "loudness_curve": features.get("loudness", []),
        "voicing_curve": features.get("voicing", [])
    }
    
    return piano_roll_data

with gr.Blocks() as demo:
    backend_data = PianoRollBackendData()
    piano_roll = PianoRoll(backend_data=backend_data)
    audio_input = gr.Audio(type="filepath")
    
    analyze_btn = gr.Button("업로드된 오디오 분석")
    analyze_btn.click(
        fn=analyze_uploaded_audio,
        inputs=[piano_roll, audio_input],
        outputs=[piano_roll]
    )
```

## ⚙️ 고급 설정

### F0 분석 설정

```python
def extract_f0_with_custom_settings(audio_file_path, method="pyin"):
    """F0 추출 커스텀 설정"""
    
    if method == "pyin":
        # PYIN 방법: 높은 정확도
        f0_data = librosa.pyin(
            audio_data,
            fmin=80,      # 최소 주파수 (Hz)
            fmax=400,     # 최대 주파수 (Hz)
            sr=sample_rate,
            frame_length=2048,
            hop_length=512
        )
    elif method == "piptrack":
        # PipTrack 방법: 빠른 처리
        pitches, magnitudes = librosa.piptrack(
            audio_data,
            sr=sample_rate,
            threshold=0.1,
            fmin=80,
            fmax=400
        )
        
    return f0_data
```

### Loudness 분석 설정

```python
def extract_loudness_with_custom_settings(audio_file_path):
    """Loudness 추출 커스텀 설정"""
    
    # RMS 에너지 계산
    rms_energy = librosa.feature.rms(
        y=audio_data,
        frame_length=2048,
        hop_length=512
    )
    
    # 데시벨 변환
    loudness_db = librosa.amplitude_to_db(
        rms_energy,
        ref=np.max  # 최대값 기준 정규화
    )
    
    return loudness_db
```

### Voice/Unvoice 분석 설정

```python
def extract_voicing_with_custom_settings(audio_file_path):
    """Voice/Unvoice 분석 커스텀 설정"""
    
    # 유성음 확률 계산
    voicing_probs = []
    
    for frame in frames:
        # 스펙트럴 특성 기반 분류
        spectral_centroid = librosa.feature.spectral_centroid(frame)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(frame)
        
        # 간단한 휴리스틱 분류
        if spectral_centroid > threshold and zero_crossing_rate < threshold:
            voicing_probs.append(1.0)  # 유성음
        else:
            voicing_probs.append(0.0)  # 무성음
    
    return voicing_probs
```

## 🎛️ 신디사이저 설정

### ADSR 엔벨로프

```python
def configure_adsr_envelope():
    """ADSR 엔벨로프 설정"""
    
    adsr_config = {
        "attack": 0.01,    # Attack 시간 (초): 0.001 ~ 1.0
        "decay": 0.1,      # Decay 시간 (초): 0.001 ~ 1.0  
        "sustain": 0.7,    # Sustain 레벨: 0.0 ~ 1.0
        "release": 0.3     # Release 시간 (초): 0.001 ~ 2.0
    }
    
    return adsr_config
```

### 파형 타입

```python
def configure_waveform_type():
    """파형 타입 설정"""
    
    waveform_options = {
        "complex": "복합 파형 (하모닉 + FM)",
        "harmonic": "하모닉 합성",
        "fm": "FM 합성",
        "sawtooth": "톱니파",
        "square": "사각파", 
        "triangle": "삼각파",
        "sine": "사인파"
    }
    
    return waveform_options
```

## 📈 시각화 옵션

### F0 곡선 시각화

```python
def create_f0_visualization(f0_data, tempo=120, pixels_per_beat=80):
    """F0 데이터를 피아노롤 좌표계로 변환"""
    
    line_data = []
    
    for i, f0_value in enumerate(f0_data):
        if f0_value > 0:  # 유효한 F0 값만
            # 시간을 픽셀 좌표로 변환
            time_seconds = i * hop_length / sample_rate
            x_pixels = time_seconds * (tempo / 60) * pixels_per_beat
            
            # 주파수를 MIDI 노트로 변환
            midi_note = 12 * np.log2(f0_value / 440) + 69
            y_pixels = (127 - midi_note) * 10  # 피아노롤 Y 좌표
            
            line_data.append({"x": x_pixels, "y": y_pixels})
    
    return {
        "f0_curve": {
            "type": "line",
            "points": line_data,
            "color": "#ff6b6b",
            "lineWidth": 2
        }
    }
```

### Loudness 곡선 시각화

```python
def create_loudness_visualization(loudness_data, y_min=-60, y_max=0):
    """Loudness 데이터 시각화"""
    
    line_data = []
    
    for i, loudness_value in enumerate(loudness_data):
        time_seconds = i * hop_length / sample_rate
        x_pixels = time_seconds * (tempo / 60) * pixels_per_beat
        
        # Y축 정규화 (데시벨 → 픽셀)
        normalized_y = (loudness_value - y_min) / (y_max - y_min)
        y_pixels = (1 - normalized_y) * 600  # 600px 높이 기준
        
        line_data.append({"x": x_pixels, "y": y_pixels})
    
    return {
        "loudness_curve": {
            "type": "line",
            "points": line_data,
            "color": "#4ecdc4",
            "lineWidth": 2
        }
    }
```

## 🔧 실용적인 활용법

### 1. 음성 분석 워크플로우

```python
def voice_analysis_workflow(audio_file):
    """음성 분석 완전 워크플로우"""
    
    # 1단계: 기본 특성 추출
    features = extract_audio_features(
        audio_file_path=audio_file,
        f0_method="pyin",
        include_f0=True,
        include_loudness=True, 
        include_voicing=True
    )
    
    # 2단계: 피아노롤 데이터 생성
    piano_roll_data = {
        "notes": [],
        "tempo": 120,
        "curve_data": {
            "f0_curve": create_f0_line_data(features["f0"]),
            "loudness_curve": create_loudness_line_data(features["loudness"]),
            "voicing_curve": create_voicing_line_data(features["voicing"])
        },
        "use_backend_audio": True
    }
    
    # 3단계: 분석 리포트 생성
    analysis_report = {
        "평균_f0": np.mean([f for f in features["f0"] if f > 0]),
        "f0_범위": [np.min(features["f0"]), np.max(features["f0"])],
        "평균_loudness": np.mean(features["loudness"]),
        "유성음_비율": np.mean(features["voicing"])
    }
    
    return piano_roll_data, analysis_report
```

### 2. 실시간 분석 모니터링

```python
def setup_realtime_analysis():
    """실시간 분석 설정"""
    
    with gr.Blocks() as demo:
        piano_roll = PianoRoll(use_backend_audio=True)
        
        # 분석 설정 UI
        with gr.Row():
            f0_toggle = gr.Checkbox(label="F0 분석", value=True)
            loudness_toggle = gr.Checkbox(label="Loudness 분석", value=True)
            voicing_toggle = gr.Checkbox(label="Voice/Unvoice 분석", value=True)
        
        with gr.Row():
            f0_method = gr.Dropdown(
                choices=[("PYIN", "pyin"), ("PipTrack", "piptrack")],
                value="pyin",
                label="F0 방법"
            )
            
        # 실시간 업데이트
        def update_analysis(piano_roll_data, f0_enabled, loudness_enabled, 
                          voicing_enabled, method):
            # 실시간 분석 로직
            return piano_roll_data
        
        # 주기적 업데이트 (예: 1초마다)
        timer = gr.Timer(1.0)
        timer.tick(
            fn=update_analysis,
            inputs=[piano_roll, f0_toggle, loudness_toggle, voicing_toggle, f0_method],
            outputs=[piano_roll]
        )
```

### 3. 음질 평가 도구

```python
def audio_quality_assessment(audio_file):
    """오디오 품질 평가"""
    
    features = extract_audio_features(audio_file)
    
    quality_metrics = {
        "피치_안정성": calculate_f0_stability(features["f0"]),
        "음량_일관성": calculate_loudness_consistency(features["loudness"]),
        "잡음_수준": calculate_noise_level(features),
        "전체_점수": 0.0
    }
    
    # 종합 점수 계산
    quality_metrics["전체_점수"] = (
        quality_metrics["피치_안정성"] * 0.4 +
        quality_metrics["음량_일관성"] * 0.3 +
        (1 - quality_metrics["잡음_수준"]) * 0.3
    )
    
    return quality_metrics

def calculate_f0_stability(f0_data):
    """F0 안정성 계산"""
    valid_f0 = [f for f in f0_data if f > 0]
    if len(valid_f0) < 2:
        return 0.0
    
    # 변동 계수 계산 (낮을수록 안정)
    cv = np.std(valid_f0) / np.mean(valid_f0)
    stability = max(0, 1 - cv)
    
    return stability
```

## 🎯 성능 최적화

### 1. 처리 속도 향상

```python
def optimize_analysis_speed():
    """분석 속도 최적화 팁"""
    
    # 짧은 오디오 파일용 빠른 설정
    fast_settings = {
        "f0_method": "piptrack",  # PYIN 대신 PipTrack 사용
        "hop_length": 1024,       # 더 큰 hop size
        "frame_length": 2048,     # 적절한 frame size
    }
    
    # 긴 오디오 파일용 정확한 설정  
    accurate_settings = {
        "f0_method": "pyin",      # 높은 정확도
        "hop_length": 512,        # 작은 hop size
        "frame_length": 2048,     # 표준 frame size
    }
    
    return fast_settings, accurate_settings
```

### 2. 메모리 사용 최적화

```python
def optimize_memory_usage(audio_file, chunk_size=10.0):
    """메모리 사용 최적화 (청크 단위 처리)"""
    
    # 긴 오디오를 청크로 나누어 처리
    audio_data, sr = librosa.load(audio_file)
    chunk_samples = int(chunk_size * sr)
    
    all_features = {"f0": [], "loudness": [], "voicing": []}
    
    for i in range(0, len(audio_data), chunk_samples):
        chunk = audio_data[i:i+chunk_samples]
        
        # 청크별 분석
        chunk_features = extract_audio_features_chunk(chunk, sr)
        
        # 결과 병합
        for key in all_features:
            all_features[key].extend(chunk_features[key])
    
    return all_features
```

## 📝 문제해결

### 일반적인 문제들

**Q: F0 분석 결과가 부정확해요**
- PYIN 방법 사용을 권장합니다
- fmin, fmax 파라미터를 음성 범위에 맞게 조정하세요
- 노이즈가 많은 오디오는 전처리가 필요할 수 있습니다

**Q: 분석 속도가 너무 느려요**
- PipTrack 방법을 사용해보세요
- hop_length를 증가시켜 시간 해상도를 낮추세요
- 청크 단위 처리를 고려해보세요

**Q: 시각화가 제대로 안 보여요**
- curve_data 형식이 올바른지 확인하세요
- 좌표 변환 계산을 다시 확인하세요
- 브라우저 콘솔에서 오류 메시지를 확인하세요

### 디버깅 팁

```python
def debug_analysis_pipeline(audio_file):
    """분석 파이프라인 디버깅"""
    
    print(f"🔍 오디오 파일 분석 시작: {audio_file}")
    
    try:
        # 오디오 로드 확인
        audio_data, sr = librosa.load(audio_file)
        print(f"✅ 오디오 로드 성공: {len(audio_data)} 샘플, {sr}Hz")
        
        # F0 분석 확인
        f0_data = extract_f0_from_audio(audio_file)
        valid_f0_count = len([f for f in f0_data if f > 0])
        print(f"✅ F0 분석 완료: {valid_f0_count}/{len(f0_data)} 유효한 프레임")
        
        # Loudness 분석 확인
        loudness_data = extract_loudness_from_audio(audio_file)
        print(f"✅ Loudness 분석 완료: {len(loudness_data)} 프레임")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 실패: {str(e)}")
        return False
```

이 가이드를 통해 Gradio PianoRoll 컴포넌트의 강력한 오디오 분석 기능을 효과적으로 활용할 수 있습니다. 음성학, 음악학, 오디오 처리 등 다양한 분야에서 활용 가능한 전문적인 분석 도구로 사용하세요! 