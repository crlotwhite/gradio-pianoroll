# ❓ 자주 묻는 질문 (FAQ)

## 📦 설치 관련

### Q1. librosa 설치 시 오류가 발생합니다.

**A:** librosa는 오디오 처리 라이브러리로 시스템 의존성이 필요할 수 있습니다.

=== "Windows"
    ```bash
    # Microsoft Visual C++ 빌드 도구 설치 후
    pip install librosa
    
    # 또는 conda 사용
    conda install -c conda-forge librosa
    ```

=== "macOS"
    ```bash
    # Homebrew로 시스템 의존성 설치
    brew install libsndfile
    pip install librosa
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    # 시스템 패키지 설치
    sudo apt-get install libsndfile1-dev
    pip install librosa
    ```

### Q2. "No module named 'gradio_pianoroll'" 오류가 발생합니다.

**A:** 다음 순서로 확인해보세요:

1. 정확한 패키지 이름 확인:
   ```bash
   pip list | grep gradio
   ```

2. 가상환경 활성화 확인:
   ```bash
   which python
   which pip
   ```

3. 재설치:
   ```bash
   pip uninstall gradio-pianoroll
   pip install gradio-pianoroll
   ```

### Q3. 프론트엔드 빌드 오류가 발생합니다.

**A:** Node.js 버전을 확인하고 의존성을 재설치하세요:

```bash
node --version  # v16 이상 권장
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 🎹 사용법 관련

### Q4. 한국어 가사가 제대로 표시되지 않습니다.

**A:** 브라우저의 인코딩 설정을 확인하고, 한국어 폰트가 설치되어 있는지 확인하세요:

```python
# 가사 설정 예제
note = {
    "lyric": "안녕하세요",  # UTF-8 인코딩 확인
    "start": 80,
    "duration": 80,
    "pitch": 60,
    "velocity": 100
}
```

### Q5. 노트를 그릴 수 없습니다.

**A:** 편집 모드가 올바르게 설정되어 있는지 확인하세요:

```python
value = {
    "editMode": "draw",  # "select", "draw", "erase" 중 하나
    "snapSetting": "1/4",
    # ... 기타 설정
}
```

### Q6. 오디오가 재생되지 않습니다.

**A:** 브라우저의 오디오 권한과 오디오 컨텍스트를 확인하세요:

1. 브라우저에서 사이트의 오디오 권한 허용
2. 사용자 상호작용 후 오디오 재생 (브라우저 정책)
3. HTTPS 환경에서 테스트 (로컬에서는 HTTP도 가능)

## 🔧 기술적 문제

### Q7. 성능이 느립니다.

**A:** 다음 최적화 방법을 시도해보세요:

1. **numba 설치** (librosa 가속화):
   ```bash
   pip install numba
   ```

2. **멀티스레딩 설정**:
   ```python
   import os
   os.environ['NUMBA_NUM_THREADS'] = '4'
   ```

3. **노트 개수 제한**:
   ```python
   # 1000개 이상의 노트는 성능에 영향을 줄 수 있음
   if len(notes) > 1000:
       print("노트가 너무 많습니다. 성능 저하 가능")
   ```

### Q8. F0 분석 결과가 부정확합니다.

**A:** 분석 파라미터를 조정해보세요:

```python
import librosa

# 파라미터 조정
f0, voiced_flag, voiced_probs = librosa.pyin(
    y,
    fmin=50,        # 최소 주파수 (남성: 50-80, 여성: 100-150)
    fmax=800,       # 최대 주파수 (남성: 400-600, 여성: 600-800)
    sr=sr,
    threshold=0.2,  # 임계값 조정 (0.1-0.5)
    resolution=0.1  # 해상도 조정
)
```

### Q9. 메모리 사용량이 너무 큽니다.

**A:** 다음 방법으로 메모리를 절약할 수 있습니다:

1. **오디오 샘플레이트 낮추기**:
   ```python
   sr = 22050  # 대신 44100
   ```

2. **불필요한 데이터 정리**:
   ```python
   # 사용하지 않는 curve_data, segment_data 제거
   piano_roll.update_backend_data(
       curve_data={},
       segment_data=[]
   )
   ```

3. **배치 처리**:
   ```python
   # 큰 데이터를 작은 청크로 나누어 처리
   chunk_size = 1024
   for i in range(0, len(audio_data), chunk_size):
       chunk = audio_data[i:i+chunk_size]
       # 처리...
   ```

## 🎵 음악 이론 관련

### Q10. MIDI 피치 번호를 음이름으로 변환하려면?

**A:** 다음 함수를 사용하세요:

```python
def midi_to_note_name(midi_pitch):
    """MIDI 피치를 음이름으로 변환"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_pitch // 12) - 1
    note = notes[midi_pitch % 12]
    return f"{note}{octave}"

# 예제
print(midi_to_note_name(60))  # C4
print(midi_to_note_name(69))  # A4 (440Hz)
```

### Q11. 템포와 픽셀 위치를 시간으로 변환하려면?

**A:** timing_utils 모듈을 사용하세요:

```python
from gradio_pianoroll.timing_utils import pixels_to_seconds

# 픽셀을 초로 변환
seconds = pixels_to_seconds(
    pixels=320,         # 픽셀 위치
    pixels_per_beat=80, # 줌 레벨
    tempo=120           # BPM
)
print(f"{seconds:.2f}초")  # 2.00초
```

## 🔍 디버깅

### Q12. 개발자 도구에서 오류를 확인하는 방법?

**A:** 브라우저 개발자 도구를 활용하세요:

1. **F12** 키로 개발자 도구 열기
2. **Console** 탭에서 JavaScript 오류 확인
3. **Network** 탭에서 통신 오류 확인
4. **Application** 탭에서 저장된 데이터 확인

### Q13. 백엔드 로그를 확인하려면?

**A:** Python 로깅을 활성화하세요:

```python
import logging

# 디버그 로그 활성화
logging.basicConfig(level=logging.DEBUG)

# 또는 환경 변수 설정
import os
os.environ['GRADIO_PIANOROLL_LOG_LEVEL'] = 'DEBUG'
```

## 📞 추가 지원

### 해결되지 않는 문제가 있나요?

1. **GitHub Issues**: [새 이슈 생성](https://github.com/crlotwhite/gradio-pianoroll/issues/new)
2. **토론 참여**: [GitHub Discussions](https://github.com/crlotwhite/gradio-pianoroll/discussions)
3. **버그 리포트**: 재현 가능한 최소 예제와 함께 신고
4. **기능 제안**: 사용 사례와 함께 제안

### 버그 리포트 템플릿

```
**문제 설명**
간단명료한 문제 설명

**재현 방법**
1. ...
2. ...
3. ...

**예상 동작**
원래 어떻게 동작해야 하는지

**실제 동작**
실제로 어떻게 동작하는지

**환경 정보**
- OS: [예: Windows 10]
- Python 버전: [예: 3.10.0]
- gradio-pianoroll 버전: [예: 0.1.0]
- 브라우저: [예: Chrome 91.0]

**추가 정보**
기타 관련 정보나 스크린샷
```

---

**다른 질문이 있으신가요?** [GitHub Issues](https://github.com/crlotwhite/gradio-pianoroll/issues)에서 질문해주세요! 🙋‍♀️ 