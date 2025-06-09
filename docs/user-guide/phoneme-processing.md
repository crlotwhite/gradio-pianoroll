# 음소 처리 (G2P)

한국어 가사를 음소로 변환하는 G2P(Grapheme-to-Phoneme) 기능을 활용해보세요.

## 🗣️ 개요

음소 처리 기능은 한국어 가사를 발음 기호(phoneme)로 자동 변환하여 더 정확한 음성 합성을 가능하게 합니다.

### 주요 기능
- **자동 G2P**: 가사 입력 시 자동으로 음소 생성
- **커스텀 매핑**: 사용자 정의 음소 매핑 관리
- **일괄 처리**: 여러 노트의 음소를 한 번에 생성
- **실시간 업데이트**: 가사 변경 시 즉시 음소 반영

## 🔤 한국어 음성학 기초

### 기본 자음 (19개)

| 한글 | 음소 | 예시 | 설명 |
|------|------|------|------|
| ㄱ | g | **가**락 | 연음 |
| ㄲ | kk | **까**치 | 경음 |
| ㄴ | n | **나**무 | 비음 |
| ㄷ | d | **다**리 | 연음 |
| ㄸ | tt | **따**라 | 경음 |
| ㄹ | r/l | **라**디오 | 유음 |
| ㅁ | m | **마**음 | 비음 |
| ㅂ | b | **바**다 | 연음 |
| ㅃ | pp | **빠**른 | 경음 |
| ㅅ | s | **사**람 | 마찰음 |
| ㅆ | ss | **쌀** | 경음 |
| ㅇ | ng | 하**ㅇ** | 비음 (받침) |
| ㅈ | j | **자**동차 | 파찰음 |
| ㅉ | jj | **짜**장면 | 경음 |
| ㅊ | ch | **차**가운 | 파찰음 |
| ㅋ | k | **카**메라 | 파열음 |
| ㅌ | t | **타**이어 | 파열음 |
| ㅍ | p | **파**일 | 파열음 |
| ㅎ | h | **하**늘 | 마찰음 |

### 기본 모음 (21개)

| 한글 | 음소 | 예시 | 분류 |
|------|------|------|------|
| ㅏ | a | 가**ㅏ** | 저모음, 후설모음 |
| ㅑ | ya | **ㅑ**구 | 이중모음 |
| ㅓ | eo | 가**ㅓ** | 중모음, 후설모음 |
| ㅕ | yeo | **ㅕ**름 | 이중모음 |
| ㅗ | o | 가**ㅗ** | 중고모음, 후설모음 |
| ㅛ | yo | **ㅛ**일 | 이중모음 |
| ㅜ | u | 가**ㅜ** | 고모음, 후설모음 |
| ㅠ | yu | **ㅠ**럽 | 이중모음 |
| ㅡ | eu | 가**ㅡ** | 고모음, 중설모음 |
| ㅣ | i | 가**ㅣ** | 고모음, 전설모음 |
| ㅐ | ae | 가**ㅐ** | 중저모음, 전설모음 |
| ㅒ | yae | **ㅒ** | 이중모음 |
| ㅔ | e | 가**ㅔ** | 중고모음, 전설모음 |
| ㅖ | ye | **ㅖ**쁘다 | 이중모음 |
| ㅘ | wa | 가**ㅘ** | 이중모음 |
| ㅙ | wae | 가**ㅙ** | 삼중모음 |
| ㅚ | oe | 가**ㅚ** | 이중모음 |
| ㅝ | wo | 가**ㅝ** | 이중모음 |
| ㅞ | we | 가**ㅞ** | 삼중모음 |
| ㅟ | wi | 가**ㅟ** | 이중모음 |
| ㅢ | ui | 가**ㅢ** | 이중모음 |

### 받침 자음 (7개 대표음)

| 받침 | 음소 | 예시 | 설명 |
|------|------|------|------|
| ㄱ, ㅋ, ㄲ | k | 악, 밖, 깎 | [k] 음 |
| ㄴ | n | 안, 천 | [n] 음 |
| ㄷ, ㅅ, ㅆ, ㅈ, ㅊ, ㅌ, ㅎ | t | 앞, 옷, 있, 있, 맞, 밭, 놓 | [t] 음 |
| ㄹ | l | 말, 솔 | [l] 음 |
| ㅁ | m | 감, 곰 | [m] 음 |
| ㅂ, ㅍ | p | 밥, 앞 | [p] 음 |
| ㅇ | ng | 강, 공 | [ŋ] 음 |

## 🎯 기본 사용법

### 1. 기본 설정

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

# 기본 음소 매핑 시스템
user_phoneme_map = {
    '가': 'g a',
    '나': 'n a',
    '다': 'd a',
    '라': 'l aa',
    '마': 'm a',
    '바': 'b a',
    '사': 's a',
    '아': 'aa',
    '자': 'j a',
    '차': 'ch a',
    '카': 'k a',
    '타': 't a',
    '파': 'p a',
    '하': 'h a',
    '안녕': 'aa n ny eo ng',
    '하세요': 'h a s e y o',
    '음악': 'eu m a k',
    '피아노': 'p i a n o'
}

def mock_g2p(text: str) -> str:
    """한국어 G2P 함수"""
    text = text.strip()
    
    # 사용자 정의 매핑에서 찾기
    if text in user_phoneme_map:
        return user_phoneme_map[text]
    
    # 글자별 처리
    result = []
    for char in text:
        if char in user_phoneme_map:
            result.append(user_phoneme_map[char])
        else:
            result.append(char)  # 알 수 없는 글자는 그대로
    
    return ' '.join(result)
```

### 2. 피아노롤 설정

```python
# 음소가 포함된 노트 데이터
initial_notes = {
    "notes": [
        {
            "id": "note_0",
            "start": 0,
            "duration": 160,
            "pitch": 60,
            "velocity": 100,
            "lyric": "안녕",
            "phoneme": "aa n ny eo ng"
        },
        {
            "id": "note_1",
            "start": 160,
            "duration": 160,
            "pitch": 62,
            "velocity": 100,
            "lyric": "하세요",
            "phoneme": "h a s e y o"
        }
    ],
    "tempo": 120,
    "timeSignature": {"numerator": 4, "denominator": 4},
    "editMode": "select",
    "snapSetting": "1/4"
}

piano_roll = PianoRoll(
    height=600,
    width=1000,
    value=initial_notes
)
```

## 🔄 자동 G2P 처리

### 실시간 음소 생성

가사 입력 시 자동으로 음소가 생성되도록 설정:

```python
def auto_generate_missing_phonemes(piano_roll_data):
    """가사가 있지만 phoneme이 없는 노트들에 대해 자동 음소 생성"""
    if not piano_roll_data or 'notes' not in piano_roll_data:
        return piano_roll_data, "피아노롤 데이터가 없습니다."

    notes = piano_roll_data['notes'].copy()
    updated_notes = []
    changes_made = 0

    for note in notes:
        note_copy = note.copy()
        lyric = note.get('lyric', '').strip()
        current_phoneme = note.get('phoneme', '').strip()

        if lyric:
            # G2P 실행
            new_phoneme = mock_g2p(lyric)
            
            # 기존 phoneme과 다르거나 없으면 업데이트
            if not current_phoneme or current_phoneme != new_phoneme:
                note_copy['phoneme'] = new_phoneme
                changes_made += 1
                print(f"G2P 적용: '{lyric}' -> '{new_phoneme}'")
        else:
            # 가사가 없으면 phoneme도 제거
            if current_phoneme:
                note_copy['phoneme'] = None
                changes_made += 1

        updated_notes.append(note_copy)

    if changes_made > 0:
        updated_piano_roll = piano_roll_data.copy()
        updated_piano_roll['notes'] = updated_notes
        return updated_piano_roll, f"자동 G2P 완료: {changes_made}개 노트 업데이트"
    else:
        return piano_roll_data, "G2P 적용할 변경사항이 없습니다."

# 이벤트 연결
piano_roll.input(
    fn=auto_generate_missing_phonemes,
    inputs=[piano_roll],
    outputs=[piano_roll, status_text]
)
```

### 일괄 음소 생성

모든 노트에 대해 한 번에 음소 생성:

```python
def auto_generate_all_phonemes(piano_roll_data):
    """모든 노트의 가사에 대해 자동으로 phoneme 생성"""
    if not piano_roll_data or 'notes' not in piano_roll_data:
        return piano_roll_data, "피아노롤 데이터가 없습니다."

    notes = piano_roll_data['notes'].copy()
    updated_count = 0

    for note in notes:
        lyric = note.get('lyric')
        if lyric:
            phoneme = mock_g2p(lyric)
            note['phoneme'] = phoneme
            updated_count += 1
            print(f"자동 생성: '{lyric}' -> '{phoneme}'")

    updated_piano_roll = piano_roll_data.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, f"{updated_count}개 노트의 phoneme이 자동 생성되었습니다."

# 일괄 생성 버튼
btn_auto_generate = gr.Button("🤖 모든 Phoneme 자동 생성")
btn_auto_generate.click(
    fn=auto_generate_all_phonemes,
    inputs=[piano_roll],
    outputs=[piano_roll, status_text]
)
```

## 📝 음소 매핑 관리

### 매핑 테이블 표시

현재 음소 매핑을 테이블로 관리:

```python
def get_phoneme_mapping_for_dataframe():
    """Dataframe용 phoneme 매핑 리스트 반환"""
    global user_phoneme_map
    return [[k, v] for k, v in user_phoneme_map.items()]

# Gradio Dataframe으로 매핑 테이블 표시
phoneme_mapping_dataframe = gr.Dataframe(
    headers=["가사", "Phoneme"],
    datatype=["str", "str"],
    value=get_phoneme_mapping_for_dataframe(),
    label="현재 Phoneme 매핑",
    interactive=True,
    wrap=True
)
```

### 새 매핑 추가

```python
def add_phoneme_mapping(lyric: str, phoneme: str):
    """새로운 phoneme 매핑 추가"""
    global user_phoneme_map
    user_phoneme_map[lyric.strip()] = phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"'{lyric}' → '{phoneme}' 매핑이 추가되었습니다."

def update_phoneme_mapping(old_lyric: str, new_lyric: str, new_phoneme: str):
    """기존 phoneme 매핑 수정"""
    global user_phoneme_map
    
    # 기존 매핑 삭제
    if old_lyric in user_phoneme_map:
        del user_phoneme_map[old_lyric]
    
    # 새 매핑 추가
    user_phoneme_map[new_lyric.strip()] = new_phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"매핑이 '{new_lyric}' → '{new_phoneme}'로 수정되었습니다."

def delete_phoneme_mapping(lyric: str):
    """phoneme 매핑 삭제"""
    global user_phoneme_map
    if lyric in user_phoneme_map:
        del user_phoneme_map[lyric]
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑이 삭제되었습니다."
    else:
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' 매핑을 찾을 수 없습니다."

# UI 컴포넌트
with gr.Row():
    add_lyric_input = gr.Textbox(label="가사", placeholder="예: 라")
    add_phoneme_input = gr.Textbox(label="Phoneme", placeholder="예: l aa")

btn_add_mapping = gr.Button("➕ 매핑 추가", variant="primary")
btn_add_mapping.click(
    fn=add_phoneme_mapping,
    inputs=[add_lyric_input, add_phoneme_input],
    outputs=[phoneme_mapping_dataframe, status_text]
)
```

### 매핑 초기화

```python
def initialize_phoneme_map():
    """기본 한국어 phoneme 매핑으로 초기화"""
    global user_phoneme_map
    user_phoneme_map = {
        # 기본 자음/모음
        '가': 'g a', '나': 'n a', '다': 'd a', '라': 'l aa', '마': 'm a',
        '바': 'b a', '사': 's a', '아': 'aa', '자': 'j a', '차': 'ch a',
        '카': 'k a', '타': 't a', '파': 'p a', '하': 'h a',
        
        # 음계
        '도': 'd o', '레': 'l e', '미': 'm i', '파': 'p aa',
        '솔': 's o l', '라': 'l aa', '시': 's i',
        
        # 일반적인 단어
        '안녕': 'aa n ny eo ng',
        '하세요': 'h a s e y o',
        '노래': 'n o l ae',
        '사랑': 's a l a ng',
        '행복': 'h ae ng b o k',
        '음악': 'eu m a k',
        '피아노': 'p i a n o'
    }

def reset_phoneme_mapping():
    """phoneme 매핑을 기본값으로 리셋"""
    initialize_phoneme_map()
    return get_phoneme_mapping_for_dataframe(), "Phoneme 매핑이 기본값으로 리셋되었습니다."

btn_reset_mapping = gr.Button("🔄 매핑 기본값으로 리셋")
btn_reset_mapping.click(
    fn=reset_phoneme_mapping,
    outputs=[phoneme_mapping_dataframe, status_text]
)
```

## 🎵 실제 활용 예제

### 완전한 음소 처리 시스템

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

class PhonemeMappingSystem:
    def __init__(self):
        self.phoneme_map = {
            # 기본 매핑들...
            '가': 'g a', '나': 'n a', '다': 'd a',
            # ... (위의 initialize_phoneme_map 내용)
        }
    
    def g2p(self, text: str) -> str:
        """G2P 변환"""
        text = text.strip()
        if text in self.phoneme_map:
            return self.phoneme_map[text]
        
        # 글자별 처리
        result = []
        for char in text:
            if char in self.phoneme_map:
                result.append(self.phoneme_map[char])
            else:
                result.append(char)
        return ' '.join(result)
    
    def add_mapping(self, lyric: str, phoneme: str):
        """매핑 추가"""
        self.phoneme_map[lyric.strip()] = phoneme.strip()
    
    def get_mappings(self):
        """현재 매핑 리스트 반환"""
        return [[k, v] for k, v in self.phoneme_map.items()]

# 전역 인스턴스
phoneme_system = PhonemeMappingSystem()

def create_phoneme_demo():
    """음소 처리 데모 생성"""
    initial_data = {
        "notes": [
            {
                "id": "note_0",
                "start": 0,
                "duration": 160,
                "pitch": 60,
                "velocity": 100,
                "lyric": "안녕",
                "phoneme": phoneme_system.g2p("안녕")
            },
            {
                "id": "note_1", 
                "start": 160,
                "duration": 160,
                "pitch": 64,
                "velocity": 100,
                "lyric": "음악"
            }  # 의도적으로 phoneme 없음
        ],
        "tempo": 120,
        "timeSignature": {"numerator": 4, "denominator": 4},
        "editMode": "select",
        "snapSetting": "1/4"
    }
    
    return initial_data

def process_lyric_changes(piano_roll_data):
    """가사 변경 시 자동 음소 처리"""
    notes = piano_roll_data.get('notes', [])
    changes = 0
    
    for note in notes:
        lyric = note.get('lyric', '').strip()
        if lyric and not note.get('phoneme'):
            note['phoneme'] = phoneme_system.g2p(lyric)
            changes += 1
    
    return piano_roll_data, f"자동 G2P 처리: {changes}개 노트"

def clear_all_phonemes(piano_roll_data):
    """모든 phoneme 지우기"""
    notes = piano_roll_data.get('notes', [])
    for note in notes:
        note['phoneme'] = None
    
    return piano_roll_data, "모든 phoneme이 지워졌습니다."

# Gradio 인터페이스
with gr.Blocks() as demo:
    gr.Markdown("# 🗣️ 음소 처리 시스템")
    
    with gr.Row():
        with gr.Column(scale=3):
            piano_roll = PianoRoll(
                height=600,
                width=1000,
                value=create_phoneme_demo()
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 음소 매핑 관리")
            
            phoneme_table = gr.Dataframe(
                headers=["가사", "Phoneme"],
                value=phoneme_system.get_mappings(),
                label="현재 매핑"
            )
            
            with gr.Row():
                new_lyric = gr.Textbox(label="가사")
                new_phoneme = gr.Textbox(label="Phoneme")
            
            btn_add = gr.Button("추가")
            
            with gr.Row():
                btn_auto = gr.Button("🤖 자동 생성")
                btn_clear = gr.Button("🗑️ 모두 지우기")
    
    status = gr.Textbox(label="상태")
    
    # 이벤트 연결
    piano_roll.input(process_lyric_changes, 
                    inputs=piano_roll, 
                    outputs=[piano_roll, status])
    
    btn_add.click(
        lambda l, p: (phoneme_system.add_mapping(l, p), 
                     phoneme_system.get_mappings(),
                     f"'{l}' → '{p}' 추가됨")[1:],
        inputs=[new_lyric, new_phoneme],
        outputs=[phoneme_table, status]
    )
    
    btn_auto.click(process_lyric_changes, 
                  inputs=piano_roll, 
                  outputs=[piano_roll, status])
    
    btn_clear.click(clear_all_phonemes,
                   inputs=piano_roll,
                   outputs=[piano_roll, status])

demo.launch()
```

## 🎯 고급 음소 처리

### 복합 단어 처리

```python
def advanced_g2p(text: str, phoneme_map: dict) -> str:
    """고급 G2P 처리 - 복합 단어 우선 처리"""
    text = text.strip()
    
    # 1. 전체 단어로 먼저 매핑 시도
    if text in phoneme_map:
        return phoneme_map[text]
    
    # 2. 부분 단어 매핑 (긴 것부터)
    for length in range(len(text), 0, -1):
        for start in range(len(text) - length + 1):
            substr = text[start:start + length]
            if substr in phoneme_map:
                before = text[:start]
                after = text[start + length:]
                
                before_phoneme = advanced_g2p(before, phoneme_map) if before else ""
                after_phoneme = advanced_g2p(after, phoneme_map) if after else ""
                
                parts = [p for p in [before_phoneme, phoneme_map[substr], after_phoneme] if p]
                return ' '.join(parts)
    
    # 3. 글자별 처리
    result = []
    for char in text:
        if char in phoneme_map:
            result.append(phoneme_map[char])
        else:
            result.append(char)
    
    return ' '.join(result)
```

### 음소 검증

```python
def validate_phoneme(phoneme: str) -> bool:
    """음소 형식 검증"""
    if not phoneme:
        return False
    
    # 기본적인 음소 패턴 체크
    valid_phonemes = {
        # 자음
        'g', 'n', 'd', 'l', 'm', 'b', 's', 'j', 'ch', 'k', 't', 'p', 'h',
        'gg', 'nn', 'dd', 'll', 'mm', 'bb', 'ss', 'jj',
        # 모음
        'a', 'aa', 'e', 'eo', 'i', 'o', 'u', 'eu', 'ui', 'ae', 'oe', 'wi',
        'ya', 'yaa', 'ye', 'yeo', 'yo', 'yu', 'yae'
    }
    
    parts = phoneme.split()
    for part in parts:
        if part not in valid_phonemes:
            return False
    
    return True

def validate_and_correct_phoneme(lyric: str, phoneme: str) -> tuple[str, str]:
    """음소 검증 및 자동 수정"""
    if validate_phoneme(phoneme):
        return phoneme, "유효한 음소입니다."
    else:
        # 자동 수정 시도
        corrected = phoneme.replace('r', 'l').replace('f', 'p')
        if validate_phoneme(corrected):
            return corrected, f"음소가 자동 수정되었습니다: '{phoneme}' → '{corrected}'"
        else:
            return phoneme, f"⚠️ 유효하지 않은 음소: '{phoneme}'"
```

## 📊 음소 분석

### 음소 통계

```python
def analyze_phonemes(piano_roll_data):
    """음소 사용 통계 분석"""
    notes = piano_roll_data.get('notes', [])
    
    phoneme_count = {}
    lyric_count = {}
    
    for note in notes:
        lyric = note.get('lyric', '')
        phoneme = note.get('phoneme', '')
        
        if lyric:
            lyric_count[lyric] = lyric_count.get(lyric, 0) + 1
        
        if phoneme:
            for p in phoneme.split():
                phoneme_count[p] = phoneme_count.get(p, 0) + 1
    
    analysis = {
        '총 노트 수': len(notes),
        '가사가 있는 노트': len([n for n in notes if n.get('lyric')]),
        '음소가 있는 노트': len([n for n in notes if n.get('phoneme')]),
        '사용된 가사 종류': len(lyric_count),
        '사용된 음소 종류': len(phoneme_count),
        '가장 많이 사용된 가사': max(lyric_count.items(), key=lambda x: x[1]) if lyric_count else None,
        '가장 많이 사용된 음소': max(phoneme_count.items(), key=lambda x: x[1]) if phoneme_count else None
    }
    
    return analysis
```

## 💾 매핑 데이터 관리

### 매핑 저장/로드

```python
import json

def save_phoneme_mapping(phoneme_map: dict, filename: str):
    """음소 매핑을 파일로 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(phoneme_map, f, ensure_ascii=False, indent=2)

def load_phoneme_mapping(filename: str) -> dict:
    """파일에서 음소 매핑 로드"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def export_phoneme_mapping():
    """현재 매핑을 파일로 내보내기"""
    global user_phoneme_map
    save_phoneme_mapping(user_phoneme_map, "phoneme_mapping.json")
    return "매핑이 phoneme_mapping.json으로 저장되었습니다."

def import_phoneme_mapping():
    """파일에서 매핑 가져오기"""
    global user_phoneme_map
    imported_map = load_phoneme_mapping("phoneme_mapping.json")
    if imported_map:
        user_phoneme_map.update(imported_map)
        return "매핑을 성공적으로 가져왔습니다."
    else:
        return "매핑 파일을 찾을 수 없습니다."
```

---

음소 처리 시스템을 통해 한국어 가사의 정확한 발음을 관리할 수 있습니다! 🗣️

**다음 단계**: [오디오 분석](audio-analysis.md)에서 F0와 음성 특성 분석을 알아보세요! 