# LineLayer 사용 가이드

LineLayer는 피아노롤에서 시간에 따른 선형 데이터를 시각화하기 위한 범용 레이어입니다. pitch curve, loudness, voice/unvoice 등 다양한 유형의 데이터를 표시할 수 있습니다.

## 기본 사용법

### 1. Backend에서 line_data 전송

#### 새로운 방식 (PianoRollBackendData 사용)

```python
from gradio_pianoroll import PianoRoll, PianoRollBackendData

# 백엔드 데이터 객체 생성
backend_data = PianoRollBackendData()

# 곡선 데이터 추가
backend_data.add_curve("pitch_curve", {
    "color": "#FF6B6B",  # 선 색상
    "lineWidth": 2,      # 선 두께
    "yMin": 50,          # Y축 최소값 (Hz)
    "yMax": 500,         # Y축 최대값 (Hz)
    "position": "top",   # 위치 ("top", "center", "bottom")
    "height": 100,       # 레이어 높이 (픽셀)
    "visible": True,     # 표시 여부
    "opacity": 1.0,      # 투명도 (0.0-1.0)
    "data": [
        {"x": 0, "y": 220},      # 직접 픽셀 좌표
        {"x": 100, "y": 440},
        {"x": 200, "y": 330},
        # ...
    ]
})

backend_data.add_curve("loudness", {
    "color": "#4ECDC4",
    "lineWidth": 3,
    "yMin": -60,         # dB
    "yMax": 0,
    "position": "bottom",
    "data": [
        {"time": 0.0, "value": -20},    # 시간(초) + 값
        {"time": 0.1, "value": -15},
        {"time": 0.2, "value": -25},
        # ...
    ]
})

# 피아노롤에 적용
piano_roll = PianoRoll(backend_data=backend_data)
```

#### 기존 방식 (여전히 지원)

```python
line_data = {
    "pitch_curve": {...},
    "loudness": {...}
}

# Gradio 컴포넌트 업데이트
return gr.update(value={
    "notes": notes,
    "tempo": 120,
    "line_data": line_data,  # LineLayer 데이터
    # ... 기타 데이터
})
```

### 2. 지원하는 데이터 형식

LineLayer는 다양한 데이터 형식을 지원합니다:

#### 직접 픽셀 좌표
```python
"data": [
    {"x": 0, "y": 220},
    {"x": 100, "y": 440},
]
```

#### 시간(초) + 값
```python
"data": [
    {"seconds": 0.0, "value": 220},
    {"seconds": 1.0, "value": 440},
]
```

#### 시간(beats) + 값
```python
"data": [
    {"time": 0.0, "value": 220},  # time은 beats 단위로 해석됨
    {"time": 4.0, "value": 440},
]
```

## 설정 옵션

### 필수 옵션
- `color`: 선 색상 (hex 코드)
- `yMin`: Y축 최소값
- `yMax`: Y축 최대값

### 선택 옵션
- `lineWidth`: 선 두께 (기본값: 2)
- `height`: 레이어 높이 픽셀 (기본값: 캔버스 높이의 1/4)
- `position`: 레이어 위치 - "top", "center", "bottom" (기본값: "center")
- `visible`: 표시 여부 (기본값: true)
- `opacity`: 투명도 0.0-1.0 (기본값: 1.0)

## 실제 사용 예시

### 🎵 F0 분석 데모 (demo/app.py 구현)

**🎯 중요: F0 곡선이 피아노롤 노트와 정확히 정렬됩니다!**

실제로 동작하는 F0 분석 예시가 `demo/app.py`의 "F0 Analysis Demo" 탭에 구현되어 있습니다:

```python
def analyze_audio_f0(piano_roll, audio_file, f0_method="pyin"):
    """오디오 파일에서 F0를 추출하고 LineLayer로 시각화"""

    # 1. librosa로 F0 추출
    y, sr = librosa.load(audio_file, sr=None)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),  # 65Hz
        fmax=librosa.note_to_hz('C7')   # 2093Hz
    )

    # 2. Hz를 MIDI 노트 번호로 변환하여 피아노롤과 정렬
    def hz_to_midi(frequency):
        return 69 + 12 * np.log2(frequency / 440.0)

    NOTE_HEIGHT = 20
    TOTAL_NOTES = 128

    # 3. LineLayer 데이터 형식으로 변환 (피아노롤 좌표계 사용)
    line_data = {
        "f0_curve": {
            "color": "#FF6B6B",  # 빨간색
            "lineWidth": 3,
            "yMin": 0,  # 전체 피아노롤 범위
            "yMax": TOTAL_NOTES * NOTE_HEIGHT,
            "position": "overlay",  # 그리드 위에 오버레이
            "renderMode": "piano_grid",  # 🔥 피아노롤 정렬 모드
            "visible": True,
            "opacity": 0.8,
            "dataType": "f0",
            "unit": "Hz",
            "data": [
                {
                    "x": float(time * (tempo/60) * pixelsPerBeat),  # 시간을 픽셀로
                    "y": float((TOTAL_NOTES-1-hz_to_midi(f0_val))*NOTE_HEIGHT + NOTE_HEIGHT/2)  # 피아노롤 Y 좌표
                }
                for time, f0_val in zip(frame_times, f0)
                if not np.isnan(f0_val) and f0_val > 0 and 0 <= hz_to_midi(f0_val) <= 127
            ],
            "originalRange": {
                "minHz": float(np.min(f0[~np.isnan(f0)])),
                "maxHz": float(np.max(f0[~np.isnan(f0)])),
                "minMidi": hz_to_midi(np.min(f0[~np.isnan(f0)])),
                "maxMidi": hz_to_midi(np.max(f0[~np.isnan(f0)]))
            }
        }
    }

    # 3. 피아노롤에 적용
    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['line_data'] = line_data

    return updated_piano_roll, "F0 분석 완료!", audio_file
```

**데모 사용법:**
1. `demo/app.py` 실행
2. "F0 Analysis Demo" 탭 선택
3. 오디오 파일 업로드 또는 "데모 오디오 생성" 클릭
4. "F0 분석 시작" 버튼 클릭
5. 피아노롤에서 빨간색 F0 곡선 확인

### F0 (피치) 모델 개발자
```python
def update_f0_display(f0_curve):
    line_data = {
        "f0": {
            "color": "#FF4081",
            "lineWidth": 2,
            "yMin": 80,    # 인간 음성 범위
            "yMax": 400,
            "position": "top",
            "height": 120,
            "data": [
                {"seconds": t, "value": f0}
                for t, f0 in enumerate(f0_curve)
            ]
        }
    }
    return gr.update(value={"line_data": line_data})
```

### Loudness + Voice/Unvoice 분석 연구자
```python
def update_multi_layer_display(loudness, voice_flags):
    line_data = {
        "loudness": {
            "color": "#4CAF50",
            "lineWidth": 2,
            "yMin": -60,   # dB 범위
            "yMax": 0,
            "position": "center",
            "height": 80,
            "data": [
                {"seconds": i * 0.01, "value": db}
                for i, db in enumerate(loudness)
            ]
        },
        "voice_unvoice": {
            "color": "#FF9800",
            "lineWidth": 3,
            "yMin": 0,     # 0 = unvoice, 1 = voice
            "yMax": 1,
            "position": "bottom",
            "height": 60,
            "data": [
                {"seconds": i * 0.01, "value": flag}
                for i, flag in enumerate(voice_flags)
            ]
        }
    }
    return gr.update(value={"line_data": line_data})
```

### 복합 음성 특성 분석
```python
def update_comprehensive_display(features):
    # 기본 색상 팔레트
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

    line_data = {}
    for i, (feature_name, values) in enumerate(features.items()):
        line_data[feature_name] = {
            "color": colors[i % len(colors)],
            "lineWidth": 2,
            "yMin": min(values),
            "yMax": max(values),
            "position": "center",
            "data": [
                {"seconds": j * 0.01, "value": val}
                for j, val in enumerate(values)
            ]
        }

    return gr.update(value={"line_data": line_data})
```

## 레이어 제어

사용자는 UI에서 다음과 같은 제어가 가능합니다:

1. **표시/숨김**: 각 레이어를 개별적으로 표시하거나 숨김
2. **투명도 조절**: 슬라이더로 레이어 투명도 조절
3. **레이어 순서**: 레이어를 앞뒤로 이동하여 겹침 순서 조절
4. **레이어 정보**: 데이터 범위, 위치, 포인트 수 등 정보 표시

## 성능 최적화

- 화면에 보이지 않는 데이터 포인트는 자동으로 렌더링에서 제외
- 대량의 데이터 포인트도 효율적으로 처리
- 레이어별 독립적인 렌더링으로 부분 업데이트 지원

## 주의사항

1. Y값은 설정된 `yMin`, `yMax` 범위 내에서만 올바르게 표시됩니다
2. 각 레이어는 고유한 이름을 가져야 합니다
3. 데이터 포인트는 X좌표 순으로 정렬되어 렌더링됩니다
4. 메모리 사용량을 고려하여 적절한 데이터 샘플링을 권장합니다