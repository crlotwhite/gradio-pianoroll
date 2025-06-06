# F0 분석 데모 설정 가이드

이 가이드는 `demo/app.py`의 F0 분석 기능을 사용하기 위한 설정 방법을 설명합니다.

## 📋 필수 조건

### 1. Python 패키지 설치

F0 분석을 위해 다음 패키지가 필요합니다:

```bash
pip install librosa
```

이미 설치된 경우 다음과 같이 확인할 수 있습니다:
```bash
python -c "import librosa; print('librosa 버전:', librosa.__version__)"
```

### 2. 선택적 패키지 (성능 향상을 위해 권장)

```bash
# FFMPEG (다양한 오디오 포맷 지원)
pip install ffmpeg-python

# 수치 연산 가속
pip install numba

# 오디오 I/O 성능 향상
pip install soundfile
```

## 🚀 사용 방법

### 1. 데모 실행

```bash
cd demo
python app.py
```

### 2. F0 분석 데모 접근

1. 웹 브라우저에서 Gradio 인터페이스 열기
2. "📊 F0 Analysis Demo" 탭 클릭
3. 다음 중 하나 선택:
   - **오디오 파일 업로드**: WAV, MP3, FLAC 등 지원
   - **데모 오디오 생성**: 테스트용 스위프 톤 자동 생성

### 3. F0 분석 실행

1. F0 추출 방법 선택:
   - **PYIN (권장)**: 더 정확하지만 처리 시간이 김
   - **PipTrack**: 빠르지만 덜 정확함

2. "🔬 F0 분석 시작" 버튼 클릭

3. 결과 확인:
   - 피아노롤에서 빨간색 F0 곡선 표시
   - 분석 상태창에서 상세 정보 확인
   - Layer Control Panel(L키)에서 레이어 제어

## 📊 분석 결과 해석

### F0 곡선 표시

- **X축**: 시간 (초 단위)
- **Y축**: 주파수 (Hz 단위)
- **색상**: 빨간색 (#FF6B6B)
- **위치**: 피아노롤 중앙

### 레이어 제어 (L키 누름)

- **표시/숨김**: 눈 아이콘 클릭
- **투명도**: 슬라이더로 조절
- **레이어 순서**: 🔼/🔽 버튼으로 이동
- **정보 표시**:
  - F0 범위 (Hz)
  - 데이터 포인트 수
  - 레이어 위치

## 🎵 지원 오디오 포맷

### 기본 지원
- WAV (모든 샘플레이트)
- FLAC
- AU
- M4A/AAC (librosa를 통해)

### 추가 지원 (ffmpeg 설치 시)
- MP3
- OGG
- WMA
- 기타 대부분의 오디오 포맷

## ⚙️ F0 추출 알고리즘

### PYIN (기본값, 권장)
- **장점**: 높은 정확도, 노이즈에 강함
- **단점**: 처리 시간이 상대적으로 김
- **용도**: 정확한 F0 분석이 필요한 경우

### PipTrack
- **장점**: 빠른 처리 속도
- **단점**: 정확도가 떨어질 수 있음
- **용도**: 실시간 처리나 빠른 분석이 필요한 경우

## 🔧 고급 설정

### F0 범위 조정

코드에서 F0 추출 범위를 조정할 수 있습니다:

```python
# demo/app.py의 extract_f0_from_audio 함수에서
f0, voiced_flag, voiced_probs = librosa.pyin(
    y,
    fmin=librosa.note_to_hz('C2'),  # 최소 주파수 (기본: ~65Hz)
    fmax=librosa.note_to_hz('C7')   # 최대 주파수 (기본: ~2093Hz)
)
```

### 시간 해상도 조정

```python
# hop_length를 조정하여 시간 해상도 변경
hop_length = 512  # 기본값 (약 11.6ms @ 44.1kHz)
hop_length = 256  # 더 높은 해상도 (약 5.8ms @ 44.1kHz)
```

## 🐛 문제 해결

### librosa 설치 실패
```bash
# conda 사용하는 경우
conda install -c conda-forge librosa

# 또는 시스템 의존성 설치 후
sudo apt-get install libsndfile1-dev  # Ubuntu/Debian
brew install libsndfile               # macOS
pip install librosa
```

### 오디오 파일 로드 실패
1. 파일 포맷 확인 (지원 포맷인지)
2. 파일 경로에 특수문자나 한글이 있는지 확인
3. 파일 권한 확인
4. ffmpeg 설치 여부 확인

### F0 추출 결과가 없음
1. 오디오가 음성인지 확인 (악기나 노이즈는 F0가 명확하지 않을 수 있음)
2. F0 범위 설정이 적절한지 확인
3. 오디오 품질 확인 (너무 낮은 품질은 F0 추출이 어려울 수 있음)

## 📈 확장 가능성

이 데모를 기반으로 다음과 같은 기능을 추가할 수 있습니다:

### 추가 특성 분석
```python
# Spectral centroid
spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)

# Zero crossing rate
zcr = librosa.feature.zero_crossing_rate(y)

# MFCC
mfccs = librosa.feature.mfcc(y=y, sr=sr)

# 이들을 LineLayer로 시각화
line_data = {
    "f0": {...},
    "spectral_centroid": {...},
    "zcr": {...}
}
```

### 실시간 분석
- 마이크 입력을 실시간으로 분석
- WebRTC를 통한 브라우저 마이크 접근
- 스트리밍 F0 분석

### 음성 특성 분석
- Voice/Unvoice 감지
- Formant 분석
- Loudness 분석
- Harmonic/Noise ratio

이 데모는 LineLayer 시스템의 강력함을 보여주는 실제 예시이며, 다양한 음성 및 오디오 분석 애플리케이션의 기초로 활용할 수 있습니다.