# 설치하기

이 페이지에서는 Gradio PianoRoll 컴포넌트를 설치하고 개발 환경을 설정하는 방법을 안내합니다.

## 📋 시스템 요구사항

### Python 버전
- **Python 3.8 이상** (권장: Python 3.10+)

### 운영체제
- **Windows**: Windows 10 이상
- **macOS**: macOS 10.14 이상  
- **Linux**: Ubuntu 18.04, CentOS 7 이상

## 🚀 기본 설치

### 1. pip을 통한 설치

```bash
pip install gradio-pianoroll
```

### 2. 개발 버전 설치 (최신 기능)

```bash
pip install git+https://github.com/crlotwhite/gradio-pianoroll.git
```

### 3. 설치 확인

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

print("✅ Gradio PianoRoll이 성공적으로 설치되었습니다!")
```

## 📦 선택적 의존성

기능에 따라 추가 패키지가 필요할 수 있습니다:

### 🎵 오디오 분석 기능

F0 분석, loudness 분석 등의 고급 오디오 기능을 사용하려면:

```bash
pip install librosa soundfile
```

### 🎹 MIDI 지원

MIDI 파일 입출력을 위해:

```bash
pip install mido
```

### 🔊 고급 오디오 처리

추가 오디오 형식 지원 및 성능 향상:

```bash
pip install ffmpeg-python numba
```

### 전체 기능 설치

모든 기능을 한 번에 설치하려면:

```bash
pip install gradio-pianoroll[all]
```

또는 개별 설치:

```bash
pip install gradio-pianoroll librosa soundfile mido ffmpeg-python numba
```

## 🛠️ 개발 환경 설정

### 1. 저장소 클론

```bash
git clone https://github.com/crlotwhite/gradio-pianoroll.git
cd gradio-pianoroll
```

### 2. 가상환경 생성 (권장)

=== "conda"
    ```bash
    conda create -n pianoroll python=3.10
    conda activate pianoroll
    ```

=== "venv"
    ```bash
    python -m venv pianoroll-env
    
    # Windows
    pianoroll-env\Scripts\activate
    
    # macOS/Linux
    source pianoroll-env/bin/activate
    ```

### 3. 개발 의존성 설치

```bash
pip install -e ".[dev]"
```

### 4. 프론트엔드 빌드 (필요시)

```bash
cd frontend
npm install
npm run build
cd ..
```

## 🧪 설치 테스트

### 1. 기본 기능 테스트

```python
# test_installation.py
import gradio as gr
from gradio_pianoroll import PianoRoll

def test_basic():
    """기본 피아노롤 컴포넌트 테스트"""
    piano_roll = PianoRoll(
        value={
            "notes": [
                {
                    "start": 80,
                    "duration": 80,
                    "pitch": 60,
                    "velocity": 100,
                    "lyric": "테스트"
                }
            ],
            "tempo": 120
        }
    )
    
    with gr.Blocks() as demo:
        piano_roll.render()
    
    print("✅ 기본 기능 테스트 통과")

if __name__ == "__main__":
    test_basic()
```

### 2. 오디오 기능 테스트

```python
# test_audio.py
def test_audio_features():
    """오디오 분석 기능 테스트"""
    try:
        import librosa
        print("✅ librosa 사용 가능")
        
        import soundfile as sf
        print("✅ soundfile 사용 가능")
        
        # 간단한 F0 추출 테스트
        import numpy as np
        
        # 테스트 신호 생성 (440Hz 사인파)
        sr = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        y = np.sin(2 * np.pi * 440 * t)
        
        # F0 추출
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=2000, sr=sr)
        print(f"✅ F0 추출 테스트 완료: {len(f0)}개 프레임")
        
    except ImportError as e:
        print(f"⚠️ 오디오 기능을 위해 추가 패키지 설치 필요: {e}")

if __name__ == "__main__":
    test_audio_features()
```

### 3. 전체 데모 실행

```bash
cd demo
python app.py
```

브라우저에서 `http://localhost:7860`으로 접속하여 모든 기능을 확인할 수 있습니다.

## ❗ 문제 해결

### 일반적인 설치 문제

#### 1. **librosa 설치 실패**

```bash
# conda 사용
conda install -c conda-forge librosa

# 또는 시스템 의존성 설치
# Ubuntu/Debian
sudo apt-get install libsndfile1-dev

# macOS
brew install libsndfile

# 그 후 pip 설치
pip install librosa
```

#### 2. **NumPy 버전 충돌**

```bash
pip install --upgrade numpy
pip install --force-reinstall librosa
```

#### 3. **FFmpeg 관련 오류**

```bash
# Windows (chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# 그 후
pip install ffmpeg-python
```

#### 4. **권한 오류 (Windows)**

관리자 권한으로 명령 프롬프트를 실행하거나:

```bash
pip install --user gradio-pianoroll
```

### 성능 최적화

#### 1. **numba 설치** (librosa 성능 향상)

```bash
pip install numba
```

#### 2. **멀티코어 활용**

```python
import os
os.environ['NUMBA_NUM_THREADS'] = '4'  # CPU 코어 수에 맞게 조정
```

## 🔄 업데이트

### 최신 버전으로 업데이트

```bash
pip install --upgrade gradio-pianoroll
```

### 개발 버전으로 업데이트

```bash
pip install --upgrade git+https://github.com/crlotwhite/gradio-pianoroll.git
```

## 📝 환경 변수 설정

필요에 따라 환경 변수를 설정할 수 있습니다:

```bash
# .env 파일 또는 shell 설정
export GRADIO_PIANOROLL_CACHE_DIR="/path/to/cache"
export GRADIO_PIANOROLL_LOG_LEVEL="INFO"
export LIBROSA_CACHE_DIR="/path/to/librosa/cache"
```

## ✅ 설치 완료 체크리스트

- [ ] Python 3.8+ 설치 확인
- [ ] gradio-pianoroll 패키지 설치
- [ ] 기본 import 테스트 통과
- [ ] 선택적 의존성 설치 (librosa, mido 등)
- [ ] 데모 실행 성공
- [ ] 오디오 기능 테스트 통과

모든 항목이 체크되었다면 설치가 완료되었습니다! 🎉

---

**다음 단계**: [빠른 시작](quick-start.md)에서 첫 번째 예제를 만들어보세요! 