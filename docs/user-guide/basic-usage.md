# 기본 사용법

피아노롤의 모든 편집 기능과 조작법을 자세히 알아봅시다.

## 🎼 인터페이스 개요

### 메인 컴포넌트

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

piano_roll = PianoRoll(
    height=600,           # 캔버스 높이
    width=1000,          # 캔버스 너비
    value=initial_data,  # 초기 노트 데이터
    interactive=True     # 편집 가능 여부
)
```

### 화면 구성

- **상단 툴바**: 편집 모드, 템포, 박자, 스냅 설정
- **왼쪽 피아노**: MIDI 노트 (C0~G10, 128개 키)
- **메인 그리드**: 노트 편집 영역
- **하단 컨트롤**: 재생, 일시정지, 정지, 볼륨
- **우측 패널**: 레이어 제어 (L키로 토글)

## 🎯 편집 모드

### 1. 선택 모드 (Select) 🎯

**활성화**: 툴바의 화살표 아이콘 클릭 또는 `S` 키

기본 조작:
- **단일 선택**: 노트 클릭
- **다중 선택**: `Ctrl` + 클릭 또는 드래그로 영역 선택
- **전체 선택**: `Ctrl` + `A`
- **선택 해제**: 빈 공간 클릭

노트 조작:
- **이동**: 선택된 노트를 드래그
- **크기 조절**: 노트의 오른쪽 가장자리를 드래그
- **복사**: `Ctrl` + `C` 후 `Ctrl` + `V`
- **삭제**: `Delete` 키 또는 지우개 모드로 전환 후 클릭

```python
# 선택 모드 예제
def handle_selection(notes_data):
    """선택된 노트 정보 처리"""
    notes = notes_data.get('notes', [])
    selected_notes = [note for note in notes if note.get('selected', False)]
    
    print(f"선택된 노트: {len(selected_notes)}개")
    for note in selected_notes:
        print(f"- {note.get('lyric', '?')} (피치: {note['pitch']})")
    
    return notes_data

piano_roll.change(handle_selection, inputs=piano_roll, outputs=piano_roll)
```

### 2. 그리기 모드 (Draw) ✏️

**활성화**: 툴바의 연필 아이콘 클릭 또는 `D` 키

노트 생성:
- **기본 그리기**: 클릭하고 드래그하여 노트 생성
- **빠른 생성**: 그리드에 단순 클릭 (기본 길이로 생성)
- **정밀 조절**: 드래그 중 `Shift` 키로 스냅 무시

```python
# 그리기 모드에서 자동 가사 생성
def auto_assign_lyrics(notes_data):
    """새로 생성된 노트에 자동 가사 할당"""
    lyrics_sequence = ["도", "레", "미", "파", "솔", "라", "시"]
    notes = notes_data.get('notes', [])
    
    for i, note in enumerate(notes):
        if not note.get('lyric'):
            note['lyric'] = lyrics_sequence[i % len(lyrics_sequence)]
    
    return notes_data
```

### 3. 지우기 모드 (Erase) 🗑️

**활성화**: 툴바의 지우개 아이콘 클릭 또는 `E` 키

삭제 방법:
- **개별 삭제**: 삭제할 노트 클릭
- **드래그 삭제**: 드래그하여 지나가는 모든 노트 삭제
- **영역 삭제**: 영역을 드래그하여 포함된 노트들 삭제

## ⚙️ 스냅 설정

노트가 그리드에 맞춰지는 정밀도를 설정합니다.

### 지원하는 스냅 값

```python
snap_settings = {
    "1/1": "온음표 (4비트)",
    "1/2": "2분음표 (2비트)",
    "1/4": "4분음표 (1비트)",
    "1/8": "8분음표 (0.5비트)",
    "1/16": "16분음표 (0.25비트)",
    "1/32": "32분음표 (0.125비트)"
}
```

### 스냅 무시

정밀한 편집을 위해 스냅을 일시적으로 무시할 수 있습니다:
- **임시 무시**: 편집 중 `Shift` 키 유지
- **완전 무시**: 스냅 설정을 "off"로 변경

## 🎹 노트 편집

### 가사 편집

**방법 1: 더블클릭**
1. 노트를 더블클릭
2. 입력 모달에서 가사 입력
3. Enter로 확인 또는 ESC로 취소

**방법 2: 프로그래밍 방식**
```python
def batch_edit_lyrics(notes_data, lyric_mapping):
    """여러 노트의 가사를 일괄 편집"""
    notes = notes_data.get('notes', [])
    
    for note in notes:
        pitch = note.get('pitch')
        if pitch in lyric_mapping:
            note['lyric'] = lyric_mapping[pitch]
    
    return notes_data

# 사용 예제
lyric_map = {
    60: "도",  # C4
    62: "레",  # D4
    64: "미",  # E4
    65: "파",  # F4
    67: "솔", # G4
    69: "라",  # A4
    71: "시"   # B4
}

piano_roll.change(
    lambda data: batch_edit_lyrics(data, lyric_map),
    inputs=piano_roll,
    outputs=piano_roll
)
```

### 벨로시티 편집

MIDI 벨로시티(음량)를 조절할 수 있습니다:

```python
def adjust_velocity(notes_data, velocity_curve="linear"):
    """벨로시티 곡선 적용"""
    notes = notes_data.get('notes', [])
    
    for i, note in enumerate(notes):
        if velocity_curve == "linear":
            # 선형 증가
            note['velocity'] = int(50 + (i / len(notes)) * 77)
        elif velocity_curve == "crescendo":
            # 점진적 증가
            note['velocity'] = int(60 + (i / len(notes)) * 67)
        elif velocity_curve == "random":
            # 랜덤 변화
            import random
            note['velocity'] = random.randint(60, 127)
    
    return notes_data
```

## 🎵 템포와 박자

### 템포 설정

```python
def change_tempo(notes_data, new_tempo):
    """템포 변경"""
    notes_data['tempo'] = new_tempo
    return notes_data

def get_tempo_presets():
    """일반적인 템포 프리셋"""
    return {
        "라르고": 60,
        "안단테": 76,
        "모데라토": 108,
        "알레그로": 132,
        "프레스토": 168
    }
```

### 박자 설정

```python
def change_time_signature(notes_data, numerator, denominator):
    """박자 변경"""
    notes_data['timeSignature'] = {
        "numerator": numerator,
        "denominator": denominator
    }
    return notes_data

# 일반적인 박자
common_time_signatures = [
    (4, 4),  # 4/4 박자 (일반적)
    (3, 4),  # 3/4 박자 (왈츠)
    (2, 4),  # 2/4 박자 (행진곡)
    (6, 8),  # 6/8 박자 (컴파운드)
    (5, 4),  # 5/4 박자 (비정규)
]
```

## 🎮 키보드 단축키

### 편집 모드
- `D`: 그리기 모드
- `S`: 선택 모드
- `E`: 지우기 모드

### 재생 제어
- `Space`: 재생/일시정지 토글
- `Enter`: 재생 시작
- `Esc`: 정지

### 편집 작업
- `Ctrl + A`: 전체 선택
- `Ctrl + C`: 복사
- `Ctrl + V`: 붙여넣기
- `Delete`: 선택된 노트 삭제
- `Ctrl + Z`: 실행 취소 (향후 지원 예정)

### 뷰 제어
- `L`: 레이어 패널 토글
- `+/-`: 수평 줌 인/아웃
- `Shift + +/-`: 수직 줌 인/아웃

## 🖱️ 마우스 조작

### 기본 조작
- **좌클릭**: 선택/그리기
- **우클릭**: 컨텍스트 메뉴 (향후 지원)
- **드래그**: 영역 선택 또는 노트 이동
- **휠**: 수평 스크롤
- **Shift + 휠**: 수직 스크롤

### 고급 조작
- **Ctrl + 드래그**: 복사하면서 이동
- **Alt + 드래그**: 스냅 무시하고 이동
- **Shift + 클릭**: 다중 선택에 추가

## 📐 정밀 편집

### 픽셀 단위 조정

```python
def fine_tune_positions(notes_data, offset_pixels):
    """노트 위치를 픽셀 단위로 미세 조정"""
    notes = notes_data.get('notes', [])
    
    for note in notes:
        if note.get('selected', False):
            note['start'] += offset_pixels
            # 음수 위치 방지
            note['start'] = max(0, note['start'])
    
    return notes_data

# 미세 조정 버튼들
with gr.Row():
    btn_left = gr.Button("← 1px")
    btn_right = gr.Button("1px →")

btn_left.click(lambda data: fine_tune_positions(data, -1), 
               inputs=piano_roll, outputs=piano_roll)
btn_right.click(lambda data: fine_tune_positions(data, 1), 
                inputs=piano_roll, outputs=piano_roll)
```

### 그리드 스냅 계산

```python
def calculate_snap_position(pixel_position, pixels_per_beat, snap_setting):
    """스냅 설정에 따른 위치 계산"""
    snap_fractions = {
        "1/1": 1.0,
        "1/2": 0.5,
        "1/4": 0.25,
        "1/8": 0.125,
        "1/16": 0.0625,
        "1/32": 0.03125
    }
    
    snap_size = pixels_per_beat * snap_fractions.get(snap_setting, 0.25)
    snapped_position = round(pixel_position / snap_size) * snap_size
    
    return snapped_position
```

## 🎯 고급 기능

### 노트 필터링

```python
def filter_notes_by_criteria(notes_data, criteria):
    """특정 조건으로 노트 필터링"""
    notes = notes_data.get('notes', [])
    
    filtered_notes = []
    for note in notes:
        if criteria.get('min_pitch', 0) <= note['pitch'] <= criteria.get('max_pitch', 127):
            if criteria.get('min_velocity', 0) <= note['velocity'] <= criteria.get('max_velocity', 127):
                if not criteria.get('require_lyric') or note.get('lyric'):
                    filtered_notes.append(note)
    
    notes_data['notes'] = filtered_notes
    return notes_data

# 사용 예제: 고음역대 노트만 표시
high_notes_criteria = {
    'min_pitch': 72,  # C5 이상
    'max_pitch': 127,
    'min_velocity': 50,
    'max_velocity': 127
}
```

### 노트 정렬

```python
def sort_notes(notes_data, sort_by="start"):
    """노트 정렬"""
    notes = notes_data.get('notes', [])
    
    if sort_by == "start":
        notes.sort(key=lambda n: n['start'])
    elif sort_by == "pitch":
        notes.sort(key=lambda n: n['pitch'])
    elif sort_by == "velocity":
        notes.sort(key=lambda n: n['velocity'], reverse=True)
    elif sort_by == "duration":
        notes.sort(key=lambda n: n['duration'], reverse=True)
    
    notes_data['notes'] = notes
    return notes_data
```

## 📊 데이터 분석

### 통계 정보

```python
def analyze_notes(notes_data):
    """노트 데이터 분석"""
    notes = notes_data.get('notes', [])
    
    if not notes:
        return "노트가 없습니다."
    
    # 기본 통계
    pitches = [n['pitch'] for n in notes]
    velocities = [n['velocity'] for n in notes]
    durations = [n['duration'] for n in notes]
    
    stats = {
        "노트 개수": len(notes),
        "음역대": f"{min(pitches)} ~ {max(pitches)}",
        "평균 피치": round(sum(pitches) / len(pitches), 1),
        "평균 벨로시티": round(sum(velocities) / len(velocities), 1),
        "평균 길이": round(sum(durations) / len(durations), 1),
        "총 길이": max(n['start'] + n['duration'] for n in notes) if notes else 0
    }
    
    return stats
```

## 🔄 데이터 입출력

### JSON 형식으로 저장

```python
import json

def save_to_json(notes_data, filename):
    """노트 데이터를 JSON 파일로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(notes_data, f, ensure_ascii=False, indent=2)

def load_from_json(filename):
    """JSON 파일에서 노트 데이터 로드"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# Gradio 인터페이스에서 사용
def export_data(notes_data):
    save_to_json(notes_data, "exported_notes.json")
    return "데이터가 exported_notes.json으로 저장되었습니다."

btn_export = gr.Button("📤 데이터 내보내기")
btn_export.click(export_data, inputs=piano_roll, outputs=status_text)
```

---

이제 피아노롤의 모든 기본 기능을 마스터했습니다! 🎉

**다음 단계**: [신디사이저](synthesizer.md)에서 실제 오디오 생성 방법을 알아보세요! 