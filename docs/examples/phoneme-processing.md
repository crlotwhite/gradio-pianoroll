# 한국어 음성학적 처리 (Phoneme Processing)

한국어 가사를 음소(phoneme)로 변환하고 PianoRoll 컴포넌트에서 활용하는 방법을 설명합니다.

## 개요

gradio-pianoroll은 한국어 텍스트를 국제음성기호(IPA) 또는 X-SAMPA 형식의 음소로 변환하여 음성 합성에 활용할 수 있습니다.

## 기본 예제

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

# 기본 한국어 음소 매핑
korean_phonemes = {
    '안녕': 'aa n ny eo ng',
    '하세요': 'h a s e y o',
    '음악': 'eu m a k',
    '노래': 'n o l ae',
    '피아노': 'p i a n o'
}

def process_korean_text(text):
    """한국어 텍스트를 음소로 변환"""
    phonemes = []
    for char in text:
        if char in korean_phonemes:
            phonemes.append(korean_phonemes[char])
        else:
            phonemes.append(char)
    return ' '.join(phonemes)

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            korean_input = gr.Textbox(
                label="한국어 입력",
                value="안녕하세요",
                placeholder="한국어 텍스트를 입력하세요"
            )
            phoneme_output = gr.Textbox(
                label="음소 변환 결과",
                interactive=False
            )

        with gr.Column():
            piano_roll = PianoRoll(
                label="피아노롤",
                height=400,
                width=800
            )

    korean_input.change(
        fn=process_korean_text,
        inputs=korean_input,
        outputs=phoneme_output
    )

if __name__ == "__main__":
    demo.launch()
```

## 고급 음소 매핑

### 자모 단위 분해

```python
def decompose_hangul(text):
    """한글 자모 단위로 분해하여 음소 변환"""
    # 초성, 중성, 종성 분해 로직
    cho = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    jung = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    jong = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    result = []
    for char in text:
        if '가' <= char <= '힣':
            char_code = ord(char) - ord('가')
            cho_idx = char_code // (21 * 28)
            jung_idx = (char_code % (21 * 28)) // 28
            jong_idx = char_code % 28

            result.append(cho[cho_idx])
            result.append(jung[jung_idx])
            if jong_idx > 0:
                result.append(jong[jong_idx])

    return result
```

### IPA 표기법 활용

```python
# 한국어 자모-IPA 매핑
korean_to_ipa = {
    'ㄱ': 'k', 'ㄴ': 'n', 'ㄷ': 't', 'ㄹ': 'l', 'ㅁ': 'm',
    'ㅂ': 'p', 'ㅅ': 's', 'ㅇ': 'ŋ', 'ㅈ': 'tʃ', 'ㅊ': 'tʃʰ',
    'ㅋ': 'kʰ', 'ㅌ': 'tʰ', 'ㅍ': 'pʰ', 'ㅎ': 'h',
    'ㅏ': 'a', 'ㅓ': 'ʌ', 'ㅗ': 'o', 'ㅜ': 'u', 'ㅡ': 'ɯ', 'ㅣ': 'i'
}

def korean_to_ipa_conversion(jamo_list):
    """자모 리스트를 IPA로 변환"""
    return [korean_to_ipa.get(jamo, jamo) for jamo in jamo_list]
```

## 피아노롤과 연동

### 음소별 노트 생성

```python
def create_phoneme_notes(phoneme_text, start_time=0):
    """음소 문자열을 노트로 변환"""
    phonemes = phoneme_text.split()
    notes = []
    current_time = start_time

    for i, phoneme in enumerate(phonemes):
        # 기본 피치 (C4 = 60)
        pitch = 60 + (i % 12)  # 옥타브 내에서 순환

        note = {
            'pitch': pitch,
            'start_pixels': current_time * 80,  # 80 pixels per beat
            'duration_pixels': 80,  # 1 beat duration
            'velocity': 100,
            'lyric': phoneme
        }
        notes.append(note)
        current_time += 1

    return notes
```

### 멜로디와 음소 결합

```python
def combine_melody_and_phonemes(melody, phonemes):
    """기존 멜로디에 음소 가사 추가"""
    phoneme_list = phonemes.split()

    for i, note in enumerate(melody):
        if i < len(phoneme_list):
            note['lyric'] = phoneme_list[i]
        else:
            note['lyric'] = ''

    return melody
```

## 실제 활용 사례

### 1. 동요 "나비야" 예제

```python
lyrics = "나비야 나비야 이리 날아오너라"
phonemes = "n a b i y a n a b i y a i l i n a l a o n eo l a"

melody = [
    {'pitch': 60, 'start_pixels': 0, 'duration_pixels': 80, 'velocity': 100},
    {'pitch': 62, 'start_pixels': 80, 'duration_pixels': 80, 'velocity': 100},
    {'pitch': 64, 'start_pixels': 160, 'duration_pixels': 80, 'velocity': 100},
    # ... 더 많은 노트들
]

notes_with_lyrics = combine_melody_and_phonemes(melody, phonemes)
```

### 2. 실시간 음소 변환

```python
def real_time_phoneme_conversion(text):
    """실시간으로 한국어를 음소로 변환하여 피아노롤 업데이트"""
    phonemes = process_korean_text(text)
    notes = create_phoneme_notes(phonemes)
    return notes
```

## 참고 자료

- [한국어 음성학 기초](../user-guide/phoneme-processing.md)
- [피아노롤 기본 사용법](basic-usage.md)
- [음성 합성 예제](synthesizer.md)

## 다음 단계

- [F0 분석과 연동](f0-analysis.md)
- [오디오 특성 분석](audio-features.md)
- [고급 음성 합성 기법](../user-guide/synthesizer.md)