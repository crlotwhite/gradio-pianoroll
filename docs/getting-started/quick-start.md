# 빠른 시작

10분 안에 첫 번째 피아노롤 애플리케이션을 만들어보세요!

## 🎯 학습 목표

이 가이드를 완료하면 다음을 할 수 있습니다:
- [x] 기본 피아노롤 컴포넌트 생성
- [x] 노트 데이터 처리
- [x] 이벤트 핸들링
- [x] 가사와 MIDI 데이터 관리

## 🚀 첫 번째 애플리케이션

### 1단계: 기본 템플릿

새 파일 `my_pianoroll.py`를 만들고 다음 코드를 입력하세요:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

# 기본 노트 데이터
initial_notes = {
    "notes": [
        {
            "start": 80,     # 시작 위치 (픽셀)
            "duration": 80,  # 지속 시간 (픽셀)
            "pitch": 60,     # MIDI 피치 (C4)
            "velocity": 100, # 음량 (0-127)
            "lyric": "안녕"   # 가사
        },
        {
            "start": 160,
            "duration": 160,
            "pitch": 64,     # E4
            "velocity": 90,
            "lyric": "하세요"
        }
    ],
    "tempo": 120,  # BPM
    "timeSignature": {"numerator": 4, "denominator": 4},
    "editMode": "select",
    "snapSetting": "1/4"
}

def process_notes(notes_data):
    """노트 데이터 처리 함수"""
    print("=== 노트 데이터 받음 ===")
    print(f"노트 개수: {len(notes_data.get('notes', []))}")
    print(f"템포: {notes_data.get('tempo', 120)} BPM")
    
    # 각 노트 정보 출력
    for i, note in enumerate(notes_data.get('notes', [])):
        print(f"노트 {i+1}: {note.get('lyric', '?')} "
              f"(피치: {note.get('pitch', 0)}, "
              f"시작: {note.get('start', 0)}px)")
    
    return notes_data

# Gradio 인터페이스 생성
with gr.Blocks(title="내 첫 번째 피아노롤") as demo:
    gr.Markdown("# 🎹 내 첫 번째 피아노롤")
    
    # 피아노롤 컴포넌트
    piano_roll = PianoRoll(
        height=400,
        width=800,
        value=initial_notes
    )
    
    # 처리 버튼
    process_btn = gr.Button("🔄 노트 데이터 처리", variant="primary")
    
    # 출력 영역
    output_json = gr.JSON(label="노트 데이터")
    
    # 이벤트 연결
    process_btn.click(
        fn=process_notes,
        inputs=piano_roll,
        outputs=[piano_roll, output_json]
    )

if __name__ == "__main__":
    demo.launch()
```

### 2단계: 실행

```bash
python my_pianoroll.py
```

브라우저에서 `http://localhost:7860`이 자동으로 열립니다.

### 3단계: 기본 조작 해보기

1. **노트 편집**: 그리드에서 노트를 클릭하고 드래그
2. **가사 편집**: 노트를 더블클릭하여 가사 입력
3. **데이터 확인**: "노트 데이터 처리" 버튼 클릭

## 🎼 노트 편집 기능

### 편집 모드

툴바에서 편집 모드를 변경할 수 있습니다:

```python
# 편집 모드 설정
"editMode": "draw"    # 그리기 모드
"editMode": "select"  # 선택 모드  
"editMode": "erase"   # 지우기 모드
```

### 스냅 설정

노트가 그리드에 맞춰지는 간격을 설정합니다:

```python
"snapSetting": "1/1"   # 온음표
"snapSetting": "1/2"   # 2분음표
"snapSetting": "1/4"   # 4분음표
"snapSetting": "1/8"   # 8분음표
"snapSetting": "1/16"  # 16분음표
```

## 🎹 실제 예제: 간단한 멜로디

더 복잡한 예제를 만들어보겠습니다:

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

def create_melody():
    """간단한 멜로디 생성"""
    return {
        "notes": [
            # 도레미파솔라시도
            {"start": 0,   "duration": 80, "pitch": 60, "velocity": 100, "lyric": "도"},  # C4
            {"start": 80,  "duration": 80, "pitch": 62, "velocity": 100, "lyric": "레"},  # D4
            {"start": 160, "duration": 80, "pitch": 64, "velocity": 100, "lyric": "미"},  # E4
            {"start": 240, "duration": 80, "pitch": 65, "velocity": 100, "lyric": "파"},  # F4
            {"start": 320, "duration": 80, "pitch": 67, "velocity": 100, "lyric": "솔"},  # G4
            {"start": 400, "duration": 80, "pitch": 69, "velocity": 100, "lyric": "라"},  # A4
            {"start": 480, "duration": 80, "pitch": 71, "velocity": 100, "lyric": "시"},  # B4
            {"start": 560, "duration": 160, "pitch": 72, "velocity": 100, "lyric": "도"}, # C5
        ],
        "tempo": 120,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4"
    }

def analyze_melody(notes_data):
    """멜로디 분석"""
    notes = notes_data.get('notes', [])
    
    if not notes:
        return notes_data, "노트가 없습니다."
    
    # 음역대 분석
    pitches = [note.get('pitch', 0) for note in notes]
    min_pitch = min(pitches)
    max_pitch = max(pitches)
    
    # 가사 추출
    lyrics = [note.get('lyric', '') for note in notes if note.get('lyric')]
    
    analysis = f"""
    📊 멜로디 분석 결과:
    - 노트 개수: {len(notes)}개
    - 음역대: {min_pitch} ~ {max_pitch} (MIDI)
    - 음역 폭: {max_pitch - min_pitch} 반음
    - 가사: {' '.join(lyrics)}
    - 총 길이: {max(note.get('start', 0) + note.get('duration', 0) for note in notes)}px
    """
    
    return notes_data, analysis

with gr.Blocks() as demo:
    gr.Markdown("# 🎵 멜로디 생성기")
    
    piano_roll = PianoRoll(
        height=500,
        width=1000,
        value=create_melody()
    )
    
    with gr.Row():
        btn_analyze = gr.Button("📊 멜로디 분석", variant="primary")
        btn_clear = gr.Button("🗑️ 초기화", variant="secondary")
    
    analysis_output = gr.Textbox(
        label="분석 결과",
        lines=8,
        interactive=False
    )
    
    # 이벤트 핸들링
    btn_analyze.click(
        fn=analyze_melody,
        inputs=piano_roll,
        outputs=[piano_roll, analysis_output]
    )
    
    btn_clear.click(
        fn=lambda: create_melody(),
        outputs=piano_roll
    )

demo.launch()
```

## 🎯 이벤트 핸들링

피아노롤은 다양한 이벤트를 지원합니다:

```python
def on_note_change(notes_data):
    """노트가 변경될 때"""
    print("노트가 변경되었습니다!")
    return notes_data

def on_play():
    """재생 버튼 클릭 시"""
    print("재생 시작!")
    return "재생 중..."

def on_pause():
    """일시정지 버튼 클릭 시"""
    print("일시정지!")
    return "일시정지됨"

# 이벤트 연결
piano_roll.change(on_note_change, inputs=piano_roll, outputs=piano_roll)
piano_roll.play(on_play, outputs=status_text)
piano_roll.pause(on_pause, outputs=status_text)
```

## 📝 노트 데이터 구조

각 노트는 다음 속성을 가집니다:

```python
note = {
    "start": 80,        # 시작 위치 (픽셀)
    "duration": 80,     # 지속 시간 (픽셀)
    "pitch": 60,        # MIDI 피치 (0-127)
    "velocity": 100,    # 음량 (0-127)
    "lyric": "안녕",     # 가사 (선택사항)
    
    # 자동 생성되는 추가 데이터
    "id": "note-123-abc",           # 고유 ID
    "startSeconds": 0.25,           # 시작 시간 (초)
    "durationSeconds": 0.25,        # 지속 시간 (초)
    "startBeats": 0.5,              # 시작 비트
    "durationBeats": 0.5            # 지속 비트
}
```

## 🔧 고급 설정

### 크기 및 스타일

```python
piano_roll = PianoRoll(
    height=600,         # 높이
    width=1200,         # 너비
    show_label=True,    # 라벨 표시
    interactive=True,   # 편집 가능
    elem_id="my-piano", # HTML ID
    elem_classes=["custom-piano"]  # CSS 클래스
)
```

### 초기 설정

```python
initial_data = {
    "notes": [],
    "tempo": 140,       # 빠른 템포
    "timeSignature": {"numerator": 3, "denominator": 4},  # 3/4 박자
    "editMode": "draw", # 그리기 모드로 시작
    "snapSetting": "1/8",  # 8분음표 스냅
    "pixelsPerBeat": 100   # 줌 레벨
}
```

## 🎊 축하합니다!

첫 번째 피아노롤 애플리케이션을 성공적으로 만들었습니다! 🎉

### 다음 학습 단계

1. **[기본 사용법](../user-guide/basic-usage.md)**: 노트 편집의 모든 기능
2. **[신디사이저](../user-guide/synthesizer.md)**: 실제 오디오 생성
3. **[음소 처리](../user-guide/phoneme-processing.md)**: 한국어 G2P 기능

### 유용한 팁

- **키보드 단축키**: 
  - `D`: 그리기 모드
  - `S`: 선택 모드  
  - `E`: 지우기 모드
  - `Space`: 재생/일시정지

- **마우스 조작**:
  - 클릭: 노트 선택
  - 드래그: 노트 이동
  - 더블클릭: 가사 편집
  - 휠: 수평 스크롤

---

**계속 학습하기**: [기본 사용법](../user-guide/basic-usage.md)에서 더 자세한 편집 기능을 알아보세요! 