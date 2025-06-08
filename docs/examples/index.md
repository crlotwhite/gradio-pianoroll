# 예제 모음 (Examples)

이 섹션에서는 Gradio PianoRoll의 다양한 기능을 보여주는 실제 동작 예제들을 제공합니다.
각 예제는 `demo/app.py` 파일의 탭들을 기반으로 구성되어 있으며, 난이도별로 정리되어 있습니다.

## 📊 난이도별 예제

### 🟢 초급 (Beginner)

#### [기본 데모 (Basic Demo)](basic-usage.md)
- 피아노롤 컴포넌트의 기본 사용법
- 노트 생성, 편집, 삭제
- 기본적인 데이터 구조 이해
- JSON 출력 확인

**학습 목표**: PianoRoll 컴포넌트의 기본 개념 이해

### 🟡 중급 (Intermediate)

#### [신디사이저 데모 (Synthesizer Demo)](synthesizer.md)
- 실시간 오디오 합성
- ADSR 엔벨로프 조정
- 다양한 파형 타입 선택
- 백엔드 오디오 엔진 사용

**학습 목표**: 오디오 합성 기능 활용법 마스터

#### [음성학 처리 (Phoneme Processing)](phoneme-processing.md)
- G2P (Grapheme-to-Phoneme) 자동 변환
- 사용자 정의 음성학 매핑
- 가사-음성학 변환 관리
- 일괄 처리 기능

**학습 목표**: 음성학적 데이터 처리 방법 이해

### 🔴 고급 (Advanced)

#### [F0 분석 (F0 Analysis)](f0-analysis.md)
- 오디오에서 기본 주파수(F0) 추출
- librosa를 이용한 신호 처리
- F0 곡선 시각화
- PYIN 및 PipTrack 알고리즘 비교

**학습 목표**: 오디오 신호 분석 및 시각화 기술

#### [오디오 특성 분석 (Audio Feature Analysis)](audio-features.md)
- 종합적인 오디오 특성 분석
- F0, 음량, 유성음/무성음 동시 분석
- LineLayer를 이용한 다중 곡선 표시
- 업로드된 오디오 파일 분석

**학습 목표**: 고급 오디오 분석 및 시각화 기술

## 🛠️ 예제 실행 방법

### 1. 환경 설정

```bash
# 기본 패키지 설치
pip install gradio-pianoroll

# F0 분석 기능을 위해 추가 패키지 설치
pip install librosa

# 개발 환경에서 실행할 경우
cd pianoroll
pip install -e .
```

### 2. 데모 실행

```bash
# 메인 데모 실행
python demo/app.py

# 브라우저에서 http://localhost:7860 접속
```

### 3. 각 탭 별 기능 테스트

1. **🎼 Basic Demo**: 기본 피아노롤 조작
2. **🎵 Synthesizer Demo**: 오디오 합성 및 재생
3. **🗣️ Phoneme Demo**: 음성학적 변환
4. **📊 F0 Analysis Demo**: F0 분석
5. **🔊 Audio Feature Analysis**: 종합 분석

## 📋 예제별 필요 사항

| 예제 | 필수 패키지 | 난이도 | 소요 시간 |
|------|------------|--------|----------|
| Basic Demo | `gradio-pianoroll` | 🟢 초급 | 5분 |
| Synthesizer | `gradio-pianoroll`, `numpy` | 🟡 중급 | 15분 |
| Phoneme Processing | `gradio-pianoroll` | 🟡 중급 | 10분 |
| F0 Analysis | `gradio-pianoroll`, `librosa` | 🔴 고급 | 20분 |
| Audio Features | `gradio-pianoroll`, `librosa`, `numpy` | 🔴 고급 | 30분 |

## 💡 학습 팁

1. **순서대로 학습**: 기본 데모부터 시작해서 단계적으로 고급 기능으로 진행
2. **코드 분석**: 각 예제의 소스 코드를 `demo/app.py`에서 확인
3. **실습 위주**: 문서만 읽지 말고 직접 실행하고 수정해보기
4. **디버깅**: 브라우저 개발자 도구와 Python 콘솔 로그 활용

## 🔗 관련 문서

- [API 참조](../api/components.md): 컴포넌트 상세 명세
- [가이드](../guides/): 기능별 상세 설명
- [개발](../development/): 커스터마이징 및 기여 방법

---

각 예제는 독립적으로 실행 가능하며, 실제 연구나 프로젝트에서 참고할 수 있는 완전한 코드를 제공합니다.