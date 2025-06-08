# Events API 참조

이 페이지에서는 Gradio PianoRoll 컴포넌트의 모든 이벤트를 상세히 설명합니다.

## 이벤트 개요

PianoRoll 컴포넌트는 다음과 같은 이벤트를 지원합니다:

| 이벤트 | 트리거 조건 | 반환 데이터 |
|--------|-------------|-------------|
| `change` | 데이터 변경 시 | 전체 피아노롤 데이터 |
| `input` | 가사 입력 시 | 가사 변경 데이터 |
| `play` | 재생 시작 시 | 재생 상태 정보 |
| `pause` | 재생 일시정지 시 | 재생 상태 정보 |
| `stop` | 재생 정지 시 | 재생 상태 정보 |

## 기본 이벤트

### change

데이터가 변경될 때 발생하는 가장 기본적인 이벤트입니다.

```python
def on_change(piano_roll_data):
    """피아노롤 데이터가 변경될 때 호출"""
    print(f"음표 수: {len(piano_roll_data.get('notes', []))}")
    return piano_roll_data

piano_roll.change(
    fn=on_change,
    inputs=piano_roll,
    outputs=piano_roll
)
```

#### 트리거 조건
- 음표 생성, 편집, 삭제
- 템포 변경
- 편집 모드 변경
- 스냅 설정 변경

#### 매개변수
- `piano_roll_data`: 전체 피아노롤 데이터 (dict)

### input

가사 입력 시 발생하는 이벤트입니다.

```python
def on_input(lyric_data):
    """가사 입력 시 호출 (G2P 처리 등)"""
    if lyric_data:
        note_id = lyric_data.get('noteId')
        new_lyric = lyric_data.get('newLyric')
        print(f"노트 {note_id}의 가사가 '{new_lyric}'로 변경됨")
    return f"가사 입력 감지: {lyric_data}"

piano_roll.input(
    fn=on_input,
    inputs=piano_roll,
    outputs=status_text
)
```

#### 트리거 조건
- 음표의 가사 텍스트 변경

#### 매개변수
- `lyric_data`: 가사 변경 정보 (dict)
  ```python
  {
      "noteId": "note_0",     # 음표 ID
      "newLyric": "안녕",     # 새로운 가사
      "oldLyric": "hello"     # 이전 가사 (선택사항)
  }
  ```

## 오디오 이벤트

### play

재생 시작 시 발생하는 이벤트입니다.

```python
def on_play(event_data=None):
    """재생 시작 시 호출"""
    print("▶️ 재생 시작됨")
    return "재생 중..."

piano_roll.play(
    fn=on_play,
    outputs=status_text
)
```

#### 트리거 조건
- 스페이스바 키 누름
- 재생 버튼 클릭 (UI가 있는 경우)
- 프로그래밍적 재생 시작

#### 매개변수
- `event_data`: 재생 이벤트 정보 (dict, 선택사항)

### pause

재생 일시정지 시 발생하는 이벤트입니다.

```python
def on_pause(event_data=None):
    """재생 일시정지 시 호출"""
    print("⏸️ 재생 일시정지됨")
    return "일시정지됨"

piano_roll.pause(
    fn=on_pause,
    outputs=status_text
)
```

#### 트리거 조건
- 재생 중 스페이스바 키 누름
- 일시정지 버튼 클릭

#### 매개변수
- `event_data`: 일시정지 이벤트 정보 (dict, 선택사항)

### stop

재생 정지 시 발생하는 이벤트입니다.

```python
def on_stop(event_data=None):
    """재생 정지 시 호출"""
    print("⏹️ 재생 정지됨")
    return "정지됨"

piano_roll.stop(
    fn=on_stop,
    outputs=status_text
)
```

#### 트리거 조건
- 재생 완료
- 명시적 정지 명령
- 다른 음표 편집 시작

#### 매개변수
- `event_data`: 정지 이벤트 정보 (dict, 선택사항)

## 이벤트 체이닝

여러 이벤트를 연결하여 복잡한 워크플로우를 만들 수 있습니다.

### 예제: G2P 자동 처리

```python
def auto_g2p_processor(piano_roll_data):
    """가사 변경 시 자동으로 G2P 처리"""
    if not piano_roll_data or 'notes' not in piano_roll_data:
        return piano_roll_data, "데이터 없음"

    updated_notes = []
    changes_count = 0

    for note in piano_roll_data['notes']:
        note_copy = note.copy()
        lyric = note.get('lyric', '')

        if lyric and not note.get('phoneme'):
            # G2P 처리 (간단한 예제)
            phoneme = korean_g2p(lyric)
            note_copy['phoneme'] = phoneme
            changes_count += 1

        updated_notes.append(note_copy)

    updated_data = piano_roll_data.copy()
    updated_data['notes'] = updated_notes

    status = f"G2P 처리 완료: {changes_count}개 음표"
    return updated_data, status

# 이벤트 체이닝
piano_roll.input(
    fn=auto_g2p_processor,
    inputs=piano_roll,
    outputs=[piano_roll, status_text]
).then(
    fn=lambda data: f"업데이트 완료: {len(data.get('notes', []))} 음표",
    inputs=piano_roll,
    outputs=log_text
)
```

### 예제: 재생 상태 관리

```python
class PlaybackManager:
    def __init__(self):
        self.is_playing = False
        self.current_position = 0

    def on_play_start(self):
        self.is_playing = True
        return "▶️ 재생 시작", "playing"

    def on_play_pause(self):
        self.is_playing = False
        return "⏸️ 일시정지", "paused"

    def on_play_stop(self):
        self.is_playing = False
        self.current_position = 0
        return "⏹️ 정지", "stopped"

manager = PlaybackManager()

# 재생 이벤트 등록
piano_roll.play(
    fn=manager.on_play_start,
    outputs=[status_text, state_text]
)
piano_roll.pause(
    fn=manager.on_play_pause,
    outputs=[status_text, state_text]
)
piano_roll.stop(
    fn=manager.on_play_stop,
    outputs=[status_text, state_text]
)
```

## 고급 이벤트 처리

### 조건부 이벤트 처리

```python
def conditional_handler(piano_roll_data, condition):
    """조건에 따라 다른 처리 수행"""
    if not piano_roll_data:
        return piano_roll_data, "데이터 없음"

    notes_count = len(piano_roll_data.get('notes', []))

    if condition == "validate":
        # 유효성 검사
        valid_notes = [n for n in piano_roll_data['notes']
                      if 0 <= n.get('pitch', 0) <= 127]
        if len(valid_notes) != notes_count:
            return piano_roll_data, f"⚠️ 유효하지 않은 음표 발견"
        return piano_roll_data, f"✅ 모든 음표 유효 ({notes_count}개)"

    elif condition == "analyze":
        # 분석
        pitches = [n.get('pitch', 0) for n in piano_roll_data['notes']]
        if pitches:
            avg_pitch = sum(pitches) / len(pitches)
            return piano_roll_data, f"📊 평균 음높이: {avg_pitch:.1f}"

    return piano_roll_data, "처리 완료"

# 조건부 처리
condition_dropdown = gr.Dropdown(["validate", "analyze"], value="validate")

piano_roll.change(
    fn=conditional_handler,
    inputs=[piano_roll, condition_dropdown],
    outputs=[piano_roll, status_text]
)
```

### 이벤트 필터링

```python
def filtered_change_handler(piano_roll_data, last_data_state):
    """중요한 변경사항만 처리"""
    if not piano_roll_data or not last_data_state:
        return piano_roll_data, piano_roll_data, "초기 데이터"

    current_notes = piano_roll_data.get('notes', [])
    last_notes = last_data_state.get('notes', [])

    # 음표 수 변경 감지
    if len(current_notes) != len(last_notes):
        action = "추가" if len(current_notes) > len(last_notes) else "삭제"
        return piano_roll_data, piano_roll_data, f"음표 {action}: {abs(len(current_notes) - len(last_notes))}개"

    # 템포 변경 감지
    current_tempo = piano_roll_data.get('tempo', 120)
    last_tempo = last_data_state.get('tempo', 120)
    if current_tempo != last_tempo:
        return piano_roll_data, piano_roll_data, f"템포 변경: {last_tempo} → {current_tempo} BPM"

    return piano_roll_data, piano_roll_data, "미세 조정"

# 상태 저장용 컴포넌트
last_data = gr.State()

piano_roll.change(
    fn=filtered_change_handler,
    inputs=[piano_roll, last_data],
    outputs=[piano_roll, last_data, status_text]
)
```

## 이벤트 데이터 구조

### change 이벤트 데이터

```python
{
    "notes": [...],           # 전체 음표 배열
    "tempo": 120,            # 현재 템포
    "timeSignature": {...},   # 박자표
    "editMode": "select",     # 편집 모드
    "snapSetting": "1/4",     # 스냅 설정
    # ... 기타 피아노롤 데이터
}
```

### input 이벤트 데이터

```python
{
    "noteId": "note_0",      # 음표 고유 ID
    "newLyric": "안녕",      # 새로운 가사
    "oldLyric": "hello",     # 이전 가사 (선택사항)
    "timestamp": 1640995200  # 이벤트 발생 시간 (선택사항)
}
```

### 오디오 이벤트 데이터

```python
{
    "action": "play",        # 액션 타입 ("play", "pause", "stop")
    "position": 0.0,         # 현재 재생 위치 (초)
    "duration": 10.5,        # 전체 재생 길이 (초)
    "timestamp": 1640995200  # 이벤트 발생 시간
}
```

## 이벤트 활용 패턴

### 1. 실시간 검증

```python
def validate_on_change(data):
    """실시간으로 데이터 유효성 검사"""
    errors = []

    for i, note in enumerate(data.get('notes', [])):
        if not (0 <= note.get('pitch', 0) <= 127):
            errors.append(f"음표 {i+1}: 유효하지 않은 음높이")
        if note.get('duration', 0) <= 0:
            errors.append(f"음표 {i+1}: 유효하지 않은 길이")

    if errors:
        return data, "❌ " + ", ".join(errors)
    return data, "✅ 유효한 데이터"
```

### 2. 자동 저장

```python
import json
import time

def auto_save(data):
    """자동으로 데이터 저장"""
    timestamp = int(time.time())
    filename = f"pianoroll_backup_{timestamp}.json"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data, f"💾 자동 저장됨: {filename}"
    except Exception as e:
        return data, f"❌ 저장 실패: {str(e)}"
```

### 3. 실시간 분석

```python
def analyze_harmony(data):
    """실시간 화성 분석"""
    notes = data.get('notes', [])
    if not notes:
        return data, "분석할 음표 없음"

    # 동시에 연주되는 음표들 찾기
    chords = []
    for time_point in range(0, max(n['start'] + n['duration'] for n in notes), 80):
        active_notes = [n for n in notes
                       if n['start'] <= time_point < n['start'] + n['duration']]
        if len(active_notes) >= 2:
            pitches = sorted([n['pitch'] % 12 for n in active_notes])
            chords.append(pitches)

    if chords:
        return data, f"🎼 화음 발견: {len(chords)}개"
    return data, "🎵 멜로디 라인"
```

## 모범 사례

### 1. 성능 최적화

```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_analysis(notes_hash):
    """비용이 큰 분석 작업 캐싱"""
    # 복잡한 분석 로직
    time.sleep(0.1)  # 시뮬레이션
    return "분석 결과"

def optimized_handler(data):
    """최적화된 이벤트 핸들러"""
    notes = data.get('notes', [])
    notes_hash = hash(str(sorted(notes, key=lambda x: x.get('start', 0))))

    result = expensive_analysis(notes_hash)
    return data, f"⚡ 캐시된 분석: {result}"
```

### 2. 에러 처리

```python
def safe_event_handler(data):
    """안전한 이벤트 처리"""
    try:
        # 메인 처리 로직
        result = process_piano_roll_data(data)
        return result, "✅ 처리 완료"

    except ValueError as e:
        return data, f"❌ 데이터 오류: {str(e)}"
    except Exception as e:
        return data, f"⚠️ 예상치 못한 오류: {str(e)}"
```

이벤트 API를 통해 피아노롤과 다양한 상호작용을 구현할 수 있으며, 실시간 처리, 분석, 저장 등의 고급 기능을 제공할 수 있습니다.