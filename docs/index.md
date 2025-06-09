# 🎹 Gradio PianoRoll

한국어 가사와 음성 합성을 지원하는 고급 피아노롤 컴포넌트입니다.

!!! info "데모 확인하기"
    실제 동작을 확인하려면 [데모](https://github.com/crlotwhite/gradio-pianoroll/tree/main/demo)를 실행해보세요!

## ✨ 주요 기능

### 🎼 피아노롤 편집
- 직관적인 노트 편집 (그리기, 선택, 이동, 크기 조절)
- 가사 입력 및 편집
- 템포 및 박자 설정
- 다양한 스냅 옵션

### 🎵 신디사이저
- 실시간 오디오 생성
- ADSR 엔벨로프 제어
- 다양한 파형 지원 (사인파, 톱니파, 사각파 등)
- 복합 파형 및 FM 합성

### 🗣️ 음소 처리 (G2P)
- 한국어 가사를 음소로 자동 변환
- 사용자 정의 음소 매핑
- 실시간 음소 생성 및 편집

### 📊 오디오 분석
- F0 (기본 주파수) 분석 및 시각화
- Loudness 분석
- Voice/Unvoice 감지
- librosa 기반 고급 분석

### 🎨 LineLayer 시각화
- 다양한 시간 기반 데이터 시각화
- 피치 곡선, 음량 곡선, 특성 곡선
- 레이어 제어 (표시/숨김, 투명도, 순서)
- 실시간 데이터 업데이트

## 🚀 빠른 시작

### 1. 설치

```bash
pip install gradio-pianoroll
```

### 2. 기본 사용법

```python
import gradio as gr
from gradio_pianoroll import PianoRoll, PianoRollBackendData, Note

# Note 클래스로 간편한 노트 생성
note = Note(
    pitch=60,
    velocity=100,
    lyric="안녕",
    start_pixels=80,
    duration_pixels=80
)

# 백엔드 데이터 설정 (선택적)
backend_data = PianoRollBackendData()

# 피아노롤 컴포넌트
piano_roll = PianoRoll(
    height=600,
    width=1000,
    value={
        "notes": [note.to_dict()],
        "tempo": 120,
        "timeSignature": {"numerator": 4, "denominator": 4}
    },
    backend_data=backend_data
)

def process_notes(notes_data):
    print("받은 노트:", notes_data)
    # 새로운 노트 추가 예제
    piano_roll.add_note(pitch=64, start_pixels=160, duration_pixels=80, lyric="하세요")
    return notes_data

with gr.Blocks() as demo:
    piano_roll.render()
    piano_roll.change(process_notes, inputs=piano_roll, outputs=piano_roll)

demo.launch()
```

### 3. 데모 실행

전체 기능을 확인하려면 데모를 실행해보세요:

```bash
cd demo
python app.py
```

## 📚 문서 가이드

### 🎯 사용자별 추천 경로

=== "처음 사용자"
    1. [설치하기](getting-started/installation.md) - 환경 설정
    2. [빠른 시작](getting-started/quick-start.md) - 첫 번째 예제
    3. [기본 사용법](user-guide/basic-usage.md) - 노트 편집 방법

=== "음악 개발자"
    1. [신디사이저](user-guide/synthesizer.md) - 오디오 생성
    2. [음소 처리](user-guide/phoneme-processing.md) - 가사 처리
    3. [API 참조](developer/api-reference.md) - 개발 참고

=== "음성 연구자"
    1. [오디오 분석](user-guide/audio-analysis.md) - F0/Loudness 분석
    2. [LineLayer 시각화](advanced/line-layer.md) - 데이터 시각화
    3. [타이밍 변환](advanced/timing-conversions.md) - 정밀 타이밍

=== "AI/ML 개발자"
    1. [Audio Utils API](api/audio-utils.md) - Hz/시간 변환 헬퍼
    2. [오디오 분석](user-guide/audio-analysis.md) - librosa 통합
    3. [코드 예제](developer/examples.md) - 실제 구현 예제

=== "개발자"
    1. [API 참조](developer/api-reference.md) - 컴포넌트 API
    2. [코드 예제](developer/examples.md) - 실제 구현 예제
    3. [타이밍 변환](advanced/timing-conversions.md) - 내부 시스템

## 🛠️ 기술 스택

- **Frontend**: TypeScript, Svelte, Canvas API
- **Backend**: Python, Gradio, NumPy
- **Audio**: librosa, soundfile, wave
- **G2P**: 한국어 커스텀 매핑 시스템

## 📖 주요 문서

| 문서 | 설명 | 대상 |
|------|------|------|
| [빠른 시작](getting-started/quick-start.md) | 10분 안에 시작하기 | 모든 사용자 |
| [기본 사용법](user-guide/basic-usage.md) | 노트 편집의 모든 것 | 일반 사용자 |
| [신디사이저](user-guide/synthesizer.md) | 오디오 생성 및 ADSR | 음악 개발자 |
| [오디오 분석](user-guide/audio-analysis.md) | F0/Loudness 분석 | 음성 연구자 |
| [Audio Utils API](api/audio-utils.md) | Hz/시간 변환 헬퍼 함수 | AI/ML 개발자 |
| [LineLayer](advanced/line-layer.md) | 고급 시각화 기능 | 고급 사용자 |
| [API 참조](developer/api-reference.md) | 개발자 레퍼런스 | 개발자 |

## 🎯 실제 사용 사례

- **음성 합성 연구**: F0 곡선 편집 및 분석
- **음악 교육**: 피아노롤 기반 학습 도구
- **언어학 연구**: 한국어 음소 분석
- **오디오 프로덕션**: MIDI 기반 작곡 도구

## 💡 도움이 필요하신가요?

- 📖 [문서](getting-started/installation.md)에서 자세한 사용법 확인
- 🐛 [Issues](https://github.com/crlotwhite/gradio-pianoroll/issues)에서 버그 신고
- 💬 [Discussions](https://github.com/crlotwhite/gradio-pianoroll/discussions)에서 질문하기
- 📧 프로젝트 관련 문의는 GitHub Issues를 이용해주세요

---

**다음 단계**: [설치하기](getting-started/installation.md)에서 환경 설정을 시작하세요! 🚀 
