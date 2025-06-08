# 설치 가이드

이 페이지에서는 Gradio PianoRoll 컴포넌트를 설치하는 방법을 안내합니다.

## 🔧 시스템 요구사항

### 필수 요구사항
- **Python**: 3.10 이상
- **운영체제**: Windows, macOS, Linux
- **브라우저**: Chrome, Firefox, Safari, Edge (최신 버전 권장)

### 권장 사항
- **RAM**: 8GB 이상 (오디오 분석 작업 시)
- **Python 가상환경** 사용 권장

## 📦 기본 설치

### 1. PyPI에서 설치 (권장)

```bash
pip install gradio-pianoroll
```

### 2. 개발 버전 설치

최신 개발 버전을 설치하려면:

```bash
pip install git+https://github.com/crlotwhite/gradio-pianoroll.git
```

### 3. 소스코드에서 설치

```bash
git clone https://github.com/crlotwhite/gradio-pianoroll.git
cd gradio-pianoroll
pip install -e .
```

## 🎵 추가 패키지 설치

### F0 분석 기능 사용 시

F0 분석 및 오디오 처리 기능을 사용하려면 `librosa`를 설치해야 합니다:

```bash
pip install librosa
```

### 완전한 설치 (모든 기능)

```bash
pip install gradio-pianoroll librosa numpy
```

## 🔍 설치 확인

설치가 완료되었는지 확인하려면:

### 1. Python에서 확인

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

print("✅ Gradio PianoRoll이 성공적으로 설치되었습니다!")

# 간단한 테스트
with gr.Blocks() as demo:
    piano_roll = PianoRoll()

print("🎹 PianoRoll 컴포넌트가 정상적으로 생성되었습니다!")
```

### 2. 명령행에서 확인

```bash
python -c "from gradio_pianoroll import PianoRoll; print('설치 성공!')"
```

## 🐛 문제 해결

### 일반적인 설치 오류

#### 1. Permission denied 오류

**Windows/macOS/Linux:**
```bash
pip install --user gradio-pianoroll
```

또는 가상환경 사용:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install gradio-pianoroll
```

#### 2. Python 버전 호환성 오류

Python 3.10 이상이 필요합니다:
```bash
python --version  # 버전 확인
```

#### 3. Dependency 충돌 오류

```bash
pip install --upgrade pip
pip install --force-reinstall gradio-pianoroll
```

#### 4. librosa 설치 오류

**Windows에서 librosa 설치 시:**
```bash
# Microsoft Visual C++ 14.0이 필요할 수 있습니다
pip install --only-binary=all librosa
```

**macOS에서:**
```bash
# Homebrew가 설치되어 있다면
brew install portaudio
pip install librosa
```

**Ubuntu/Debian에서:**
```bash
sudo apt-get install portaudio19-dev python3-dev
pip install librosa
```

### 브라우저 호환성

| 브라우저 | 지원 여부 | 오디오 재생 | 추천도 |
|---------|-----------|-------------|--------|
| Chrome | ✅ 완전 지원 | ✅ | ⭐⭐⭐ |
| Firefox | ✅ 완전 지원 | ✅ | ⭐⭐⭐ |
| Safari | ✅ 지원 | ✅ | ⭐⭐ |
| Edge | ✅ 지원 | ✅ | ⭐⭐ |
| IE | ❌ 미지원 | ❌ | - |

## 🚀 다음 단계

설치가 완료되었다면:

1. **[빠른 시작](../quickstart/index.md)**: 기본 사용법 익히기
2. **[기본 데모](../examples/basic-usage.md)**: 첫 번째 예제 실행
3. **[예제 모음](../examples/index.md)**: 다양한 기능 살펴보기

## 📞 도움이 필요하세요?

- **GitHub Issues**: [문제 신고 및 질문](https://github.com/crlotwhite/gradio-pianoroll/issues)
- **Documentation**: [전체 문서](../index.md)
- **Examples**: [실행 가능한 예제들](../examples/index.md)