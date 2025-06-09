# 🔄 Migration Guide

기존 gradio-pianoroll 코드를 새로운 구조로 마이그레이션하는 가이드입니다.

## 📋 주요 변경사항

### 0. TypedDict 타입 안전성 추가 (v2.x 신규)

**새로 추가된 타입 시스템**:
```python
from gradio_pianoroll.data_models import PianoRollData, Note, TimeSignature

# ✅ 타입 안전한 데이터 구조
data: PianoRollData = {
    "notes": [
        {
            "id": "note_1",
            "start": 0,
            "duration": 160,
            "pitch": 60,
            "velocity": 100,
            "lyric": "안녕"
        }
    ],
    "tempo": 120,
    "timeSignature": {"numerator": 4, "denominator": 4},
    "editMode": "select",
    "snapSetting": "1/4"
}

# IDE 자동완성과 타입 검사 지원
piano_roll = PianoRoll(value=data)
```

**기존 dict 방식도 완전 호환**:
```python
# ✅ 기존 방식도 그대로 동작 (하위 호환성 보장)
old_data = {
    "notes": [{"pitch": 60, "start": 0, "duration": 160}],
    "tempo": 120
}
piano_roll = PianoRoll(value=old_data)  # 자동으로 유효성 검사 및 변환
```

**자동 유효성 검사**:
```python
# ❌ 잘못된 데이터 입력 시
bad_data = {
    "notes": [{"pitch": 999}],  # 범위 초과 (0-127)
    "tempo": -50               # 음수 템포
}

# ✅ 자동으로 경고 출력하고 기본값으로 안전하게 대체
piano_roll = PianoRoll(value=bad_data)
# UserWarning: Initial piano roll value validation failed:
#   - Note 0: 'pitch' must be between 0 and 127
#   - 'tempo' must be a positive number
```

### 1. 모듈 구조 변경

**이전 구조**:
```
backend/gradio_pianoroll/
  ├── pianoroll.py (클래스 메서드 포함)
  └── research_helpers.py (헬퍼 함수들)
```

**새로운 구조**:
```
backend/gradio_pianoroll/
  ├── pianoroll.py (순수 컴포넌트)
  └── utils/
      ├── __init__.py (lazy import)
      ├── research.py (연구자용 헬퍼 함수)
      └── templates.py (분야별 템플릿)
```

### 2. API 변경사항

#### PianoRoll 클래스 메서드 제거

**❌ 이전 방식 (deprecated)**:
```python
from gradio_pianoroll import PianoRoll

# 클래스 메서드 사용 (더 이상 지원되지 않음)
data = PianoRoll.from_notes(notes)
data = PianoRoll.from_midi_numbers(midi_notes)
data = PianoRoll.from_frequencies(frequencies)
demo = PianoRoll.quick_demo(notes)
```

**✅ 새로운 방식**:
```python
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research

# 단계별 접근
data = research.from_notes(notes)
piano_roll = PianoRoll(value=data)

# 또는
data = research.from_midi_numbers(midi_notes)
data = research.from_frequencies(frequencies)
demo = research.quick_demo(notes)
```

## 🔧 단계별 마이그레이션

### Step 1: Import 문 변경

**Before**:
```python
from gradio_pianoroll import PianoRoll
# research_helpers를 직접 import했다면:
from gradio_pianoroll.research_helpers import from_notes
```

**After**:
```python
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.utils import research
```

### Step 2: 함수 호출 변경

#### 노트에서 피아노롤 생성

**Before**:
```python
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
data = PianoRoll.from_notes(notes)
piano_roll = PianoRoll(value=data)
```

**After**:
```python
notes = [(60, 0, 1), (64, 1, 1), (67, 2, 1)]
data = research.from_notes(notes)
piano_roll = PianoRoll(value=data)
```

#### MIDI 번호에서 피아노롤 생성

**Before**:
```python
midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
data = PianoRoll.from_midi_numbers(midi_notes)
```

**After**:
```python
midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]
data = research.from_midi_numbers(midi_notes)
```

#### 주파수에서 피아노롤 생성

**Before**:
```python
frequencies = [440, 493.88, 523.25]
data = PianoRoll.from_frequencies(frequencies)
```

**After**:
```python
frequencies = [440, 493.88, 523.25]
data = research.from_frequencies(frequencies)
```

#### 빠른 데모 생성

**Before**:
```python
demo = PianoRoll.quick_demo(notes, "내 모델 결과")
```

**After**:
```python
demo = research.quick_demo(notes, "내 모델 결과")
```

### Step 3: TTS/MIDI 모델 출력 변환

**Before**:
```python
# 이전에 research_helpers에서 import
from gradio_pianoroll.research_helpers import from_tts_output, from_midi_generation
```

**After**:
```python
from gradio_pianoroll.utils import research

# TTS 출력 변환
data = research.from_tts_output(text, alignment, f0_data)

# MIDI 생성 모델 출력 변환
data = research.from_midi_generation(generated_sequence)
```

## 🎯 일반적인 마이그레이션 패턴

### 패턴 1: 기본 사용
```python
# Before
data = PianoRoll.from_notes(notes)

# After
from gradio_pianoroll.utils import research
data = research.from_notes(notes)
```

### 패턴 2: 템플릿 사용
```python
# Before (해당 기능 없었음)

# After (새로 추가됨)
from gradio_pianoroll.utils import templates
demo = templates.create_tts_template()
```

### 패턴 3: 분석 도구
```python
# Before (해당 기능 없었음)

# After (새로 추가됨)
from gradio_pianoroll.utils import research
stats = research.analyze_notes(piano_roll_data)
```

## 🚫 제거된 기능들

다음 기능들은 더 이상 지원되지 않습니다:

1. `PianoRoll.from_notes()` - `research.from_notes()` 사용
2. `PianoRoll.from_midi_numbers()` - `research.from_midi_numbers()` 사용
3. `PianoRoll.from_frequencies()` - `research.from_frequencies()` 사용
4. `PianoRoll.quick_demo()` - `research.quick_demo()` 사용
5. `research_helpers.py` 모듈 - `utils.research` 모듈 사용

## ✨ 새로 추가된 기능들

### 1. 템플릿 시스템
```python
from gradio_pianoroll.utils import templates

# 분야별 템플릿
demo = templates.create_tts_template()
demo = templates.create_midi_generation_template()
demo = templates.create_audio_analysis_template()
```

### 2. 분석 도구
```python
from gradio_pianoroll.utils import research

# 노트 통계 분석
stats = research.analyze_notes(piano_roll_data)

# 자동 모델 출력 분석
data = research.auto_analyze(model_output)
```

### 3. Lazy Import
```python
# 필요한 모듈만 로드
from gradio_pianoroll.utils import research  # 연구자용 기능만
from gradio_pianoroll.utils import templates  # 템플릿만
```

## 🔍 호환성 확인

마이그레이션 후 다음을 확인하세요:

1. **Import 에러**: 모든 import문이 새로운 구조를 사용하는지 확인
2. **함수 호출**: 클래스 메서드 대신 모듈 함수를 사용하는지 확인
3. **기능 동등성**: 기존 기능이 새로운 방식으로 동일하게 작동하는지 확인

## 💡 마이그레이션 도움말

### 자동 변환 스크립트 (참고용)

```python
# 기존 코드를 새 구조로 변환하는 예시
import re

def migrate_code(old_code: str) -> str:
    """기존 코드를 새 구조로 변환 (참고용)"""

    # PianoRoll 클래스 메서드를 research 모듈 함수로 변경
    new_code = re.sub(
        r'PianoRoll\.(from_notes|from_midi_numbers|from_frequencies|quick_demo)',
        r'research.\1',
        old_code
    )

    # research_helpers import를 utils.research로 변경
    new_code = re.sub(
        r'from gradio_pianoroll\.research_helpers import',
        r'from gradio_pianoroll.utils import research\n# 이제 research.',
        new_code
    )

    return new_code
```

## 📞 도움이 필요하다면

- [API 문서](../api/components.md) - 새로운 API 전체 문서
- [사용자 가이드](../user-guide/basic-usage.md) - 기본 사용법
- [예제 모음](../examples/) - 새로운 구조를 사용한 예제들

마이그레이션 과정에서 문제가 있다면 GitHub Issues로 문의해주세요!