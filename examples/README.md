# PianoRoll Examples

이 폴더에는 `gradio-pianoroll` 컴포넌트의 다양한 기능을 보여주는 독립적인 예제들이 포함되어 있습니다.

## 📋 예제 목록

### 1. `basic_demo.py` - 기본 사용법
- **목적**: PianoRoll 컴포넌트의 가장 기본적인 사용법
- **기능**: 
  - 노트 편집 및 데이터 확인
  - JSON 출력 및 디버깅
- **실행**: `python basic_demo.py`

### 2. `synthesizer_demo.py` - 오디오 합성
- **목적**: 노트에서 실제 오디오를 생성하고 재생
- **기능**:
  - ADSR 엔벨로프 설정
  - 다양한 파형 타입 (사인파, 톱니파, 복합파형 등)
  - 비브라토, 트레몰로 효과
  - 백엔드 오디오 통합
- **실행**: `python synthesizer_demo.py`
- **요구사항**: `numpy`, `wave`

### 3. `phoneme_demo.py` - 한국어 음소 변환
- **목적**: 한국어 가사를 음소로 자동 변환
- **기능**:
  - G2P (Grapheme-to-Phoneme) 자동 변환
  - 음소 매핑 관리 및 편집
  - 일괄 음소 생성 및 삭제
- **실행**: `python phoneme_demo.py`

### 4. `f0_analysis_demo.py` - F0 분석
- **목적**: 오디오에서 기본 주파수(F0) 추출 및 시각화
- **기능**:
  - PYIN, PipTrack 알고리즘 지원
  - F0 곡선 피아노롤 오버레이
  - 데모 오디오 생성
- **실행**: `python f0_analysis_demo.py`
- **요구사항**: `librosa`

### 5. `audio_features_demo.py` - 복합 오디오 특성 분석
- **목적**: F0, loudness, voice/unvoice 등 다중 특성 분석
- **기능**:
  - 여러 특성 동시 분석
  - 다중 곡선 시각화
  - 업로드 오디오 분석
- **실행**: `python audio_features_demo.py`
- **요구사항**: `librosa`

## 🚀 빠른 시작

### 기본 예제 실행
```bash
cd examples
python basic_demo.py
```

### 고급 기능 (librosa 필요)
```bash
pip install librosa
python f0_analysis_demo.py
```

## 📦 의존성

각 예제는 독립적으로 실행됩니다. 필요한 의존성:

- **모든 예제**: `gradio`, `gradio-pianoroll`
- **synthesizer_demo.py**: `numpy`
- **f0_analysis_demo.py, audio_features_demo.py**: `librosa`

## 💡 사용 팁

1. **기본부터 시작**: `basic_demo.py`로 시작해서 기본 조작법을 익히세요
2. **오디오 합성**: `synthesizer_demo.py`에서 ADSR 파라미터를 조정해보세요
3. **음소 변환**: `phoneme_demo.py`에서 한국어 단어를 추가하고 G2P를 테스트하세요
4. **오디오 분석**: 본인의 음성이나 음악 파일을 업로드해서 분석해보세요

## 🔧 커스터마이징

각 예제 파일은 완전히 독립적이므로:
- 원하는 기능만 복사해서 사용 가능
- 매개변수 및 UI를 자유롭게 수정 가능
- 여러 예제의 기능을 조합하여 새로운 앱 제작 가능

## 📚 참고

- [PianoRoll API 문서](../docs/api/)
- [사용자 가이드](../docs/user-guide/)
- [오디오 유틸리티](../docs/api/audio-utils.md) 