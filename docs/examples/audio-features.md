# 오디오 특성 종합 분석

F0, 음량, 음성 감지 등 다양한 오디오 특성을 분석하고 PianoRoll에서 시각화하는 방법을 설명합니다.

## 개요

gradio-pianoroll은 librosa를 활용하여 오디오의 다양한 특성을 추출하고 이를 피아노롤에서 종합적으로 시각화할 수 있습니다.

## 기본 오디오 특성 분석

```python
import gradio as gr
import librosa
import numpy as np
from gradio_pianoroll import PianoRoll
from gradio_pianoroll.audio_utils import (
    librosa_f0_to_pixels,
    librosa_rms_to_pixels,
    create_loudness_curve_data
)

def comprehensive_audio_analysis(audio_file):
    """오디오 파일의 종합적 특성 분석"""
    if audio_file is None:
        return None, "오디오 파일을 업로드하세요."

    try:
        # 오디오 로드
        y, sr = librosa.load(audio_file, sr=22050)

        # 1. F0 (기본 주파수) 분석
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
        )

        # 2. RMS (음량) 분석
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]

        # 3. 스펙트럴 센트로이드 (음색 밝기)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

        # 4. 영크로싱률 (음성/비음성 구분)
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # 5. 멜 주파수 켑스트럴 계수 (음색 특성)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # 피아노롤용 곡선 데이터 생성
        curves = {}

        # F0 곡선
        if np.any(~np.isnan(f0)):
            curves['f0'] = librosa_f0_to_pixels(f0, sr=sr)

        # 음량 곡선
        curves['loudness'] = librosa_rms_to_pixels(rms, sr=sr)

        # 음성 확률 곡선
        if voiced_probs is not None:
            curves['voicing'] = librosa_rms_to_pixels(voiced_probs, sr=sr)

        # 분석 결과 요약
        analysis_summary = create_analysis_summary(
            f0, rms, spectral_centroids, zcr, mfccs, sr
        )

        return curves, analysis_summary

    except Exception as e:
        return None, f"오류 발생: {str(e)}"

def create_analysis_summary(f0, rms, spectral_centroids, zcr, mfccs, sr):
    """분석 결과 요약 생성"""
    # 유효한 F0 값들
    valid_f0 = f0[~np.isnan(f0)]

    summary = f"""
    🎵 오디오 특성 분석 결과:

    📊 기본 주파수 (F0):
    - 평균: {np.mean(valid_f0):.2f} Hz
    - 범위: {np.min(valid_f0):.2f} - {np.max(valid_f0):.2f} Hz
    - 표준편차: {np.std(valid_f0):.2f} Hz

    🔊 음량 (RMS):
    - 평균: {np.mean(rms):.4f}
    - 최대: {np.max(rms):.4f}
    - 동적 범위: {20 * np.log10(np.max(rms) / np.mean(rms)):.2f} dB

    🎶 음색 특성:
    - 스펙트럴 센트로이드 평균: {np.mean(spectral_centroids):.2f} Hz
    - 영크로싱률 평균: {np.mean(zcr):.4f}
    - MFCC 첫 번째 계수: {np.mean(mfccs[0]):.2f}

    📈 오디오 길이: {len(f0) * 512 / sr:.2f}초
    """

    return summary

with gr.Blocks() as demo:
    gr.Markdown("# 오디오 특성 종합 분석")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="분석할 오디오 파일",
                type="filepath"
            )
            analyze_btn = gr.Button("종합 분석 시작", variant="primary")

        with gr.Column():
            analysis_result = gr.Textbox(
                label="분석 결과 요약",
                lines=15,
                interactive=False
            )

    piano_roll = PianoRoll(
        label="오디오 특성 시각화",
        height=500,
        width=1000
    )

    analyze_btn.click(
        fn=comprehensive_audio_analysis,
        inputs=audio_input,
        outputs=[piano_roll, analysis_result]
    )

if __name__ == "__main__":
    demo.launch()
```

## 고급 특성 분석

### 하모닉-퍼커시브 분리

```python
def harmonic_percussive_analysis(audio_file):
    """하모닉과 퍼커시브 성분 분리 분석"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 하모닉-퍼커시브 분리
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # 각 성분별 특성 분석
    harmonic_features = {
        'f0': librosa.pyin(y_harmonic, fmin=80, fmax=400)[0],
        'rms': librosa.feature.rms(y=y_harmonic)[0],
        'spectral_centroid': librosa.feature.spectral_centroid(y=y_harmonic, sr=sr)[0]
    }

    percussive_features = {
        'rms': librosa.feature.rms(y=y_percussive)[0],
        'zcr': librosa.feature.zero_crossing_rate(y_percussive)[0],
        'tempo': librosa.beat.tempo(y=y_percussive, sr=sr)
    }

    return harmonic_features, percussive_features
```

### 음성 활동 감지

```python
def voice_activity_detection(audio_file, threshold=0.02):
    """음성 활동 구간 감지"""
    y, sr = librosa.load(audio_file, sr=22050)

    # RMS 에너지 계산
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]

    # 임계값 기반 음성 활동 감지
    voice_activity = rms > threshold

    # 연속된 음성 구간 찾기
    voice_segments = []
    in_voice = False
    start_frame = 0

    for i, is_voice in enumerate(voice_activity):
        if is_voice and not in_voice:
            # 음성 시작
            start_frame = i
            in_voice = True
        elif not is_voice and in_voice:
            # 음성 종료
            end_frame = i
            start_time = start_frame * 512 / sr
            end_time = end_frame * 512 / sr
            voice_segments.append((start_time, end_time))
            in_voice = False

    # 마지막 구간 처리
    if in_voice:
        end_time = len(voice_activity) * 512 / sr
        start_time = start_frame * 512 / sr
        voice_segments.append((start_time, end_time))

    return voice_segments, voice_activity
```

### 멜로디 추출

```python
def extract_melody_line(audio_file):
    """주 멜로디 라인 추출"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 하모닉 성분 추출
    y_harmonic, _ = librosa.effects.hpss(y)

    # F0 추출
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y_harmonic,
        fmin=librosa.note_to_hz('C3'),
        fmax=librosa.note_to_hz('C6'),
        threshold=0.1
    )

    # 멜로디 스무딩
    from scipy import ndimage
    smoothed_f0 = np.copy(f0)
    valid_indices = ~np.isnan(f0)
    smoothed_f0[valid_indices] = ndimage.gaussian_filter1d(
        f0[valid_indices], sigma=2
    )

    # 노트 세그멘테이션
    melody_notes = []
    current_pitch = None
    current_start = None
    pitch_tolerance = 50  # Hz

    for i, freq in enumerate(smoothed_f0):
        if np.isnan(freq):
            # 무음 구간
            if current_pitch is not None:
                # 현재 노트 종료
                duration = (i - current_start) * 512 / sr
                melody_notes.append({
                    'pitch': librosa.hz_to_midi(current_pitch),
                    'start': current_start * 512 / sr,
                    'duration': duration,
                    'frequency': current_pitch
                })
                current_pitch = None
        else:
            if current_pitch is None:
                # 새 노트 시작
                current_pitch = freq
                current_start = i
            else:
                # 피치 변화 확인
                if abs(freq - current_pitch) > pitch_tolerance:
                    # 피치가 크게 변했으므로 새 노트
                    duration = (i - current_start) * 512 / sr
                    melody_notes.append({
                        'pitch': librosa.hz_to_midi(current_pitch),
                        'start': current_start * 512 / sr,
                        'duration': duration,
                        'frequency': current_pitch
                    })
                    current_pitch = freq
                    current_start = i

    return melody_notes, smoothed_f0
```

## 실시간 특성 분석

### 스트리밍 오디오 분석

```python
class RealTimeAudioAnalyzer:
    def __init__(self, sr=22050, hop_length=512):
        self.sr = sr
        self.hop_length = hop_length
        self.buffer = []
        self.features_history = []

    def process_chunk(self, audio_chunk):
        """오디오 청크 처리"""
        self.buffer.extend(audio_chunk)

        # 충분한 데이터가 모이면 분석
        if len(self.buffer) >= 2048:
            y = np.array(self.buffer[-2048:])

            # 실시간 특성 추출
            features = self.extract_features(y)
            self.features_history.append(features)

            # 히스토리 크기 제한
            if len(self.features_history) > 100:
                self.features_history = self.features_history[-100:]

            return features

    def extract_features(self, y):
        """오디오 특성 추출"""
        features = {}

        # RMS 에너지
        rms = np.sqrt(np.mean(y**2))
        features['rms'] = rms

        # 영크로싱률
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        features['zcr'] = zcr

        # 스펙트럴 센트로이드
        if len(y) > 512:
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=y, sr=self.sr)
            )
            features['spectral_centroid'] = spectral_centroid

        return features
```

### 적응형 분석 파라미터

```python
def adaptive_analysis_parameters(audio_file):
    """오디오 특성에 따라 분석 파라미터 자동 조정"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 기본 특성 분석
    rms = librosa.feature.rms(y=y)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]

    # 오디오 타입 추정
    avg_rms = np.mean(rms)
    avg_zcr = np.mean(zcr)

    if avg_zcr > 0.1:
        # 노이즈가 많은 신호 - 더 엄격한 임계값
        audio_type = "noisy"
        f0_threshold = 0.3
        fmin, fmax = 80, 400
    elif avg_rms < 0.01:
        # 조용한 신호 - 민감한 임계값
        audio_type = "quiet"
        f0_threshold = 0.05
        fmin, fmax = 50, 800
    else:
        # 일반적인 신호
        audio_type = "normal"
        f0_threshold = 0.1
        fmin, fmax = librosa.note_to_hz('C2'), librosa.note_to_hz('C7')

    # 적응형 F0 분석
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=fmin, fmax=fmax, threshold=f0_threshold
    )

    return f0, audio_type, {
        'threshold': f0_threshold,
        'fmin': fmin,
        'fmax': fmax
    }
```

## 다중 곡선 시각화

### 여러 특성을 동시에 표시

```python
def multi_feature_visualization(audio_file):
    """여러 오디오 특성을 하나의 피아노롤에 시각화"""
    y, sr = librosa.load(audio_file, sr=22050)

    # 다양한 특성 추출
    f0, _, voiced_probs = librosa.pyin(y, fmin=80, fmax=400)
    rms = librosa.feature.rms(y=y)[0]
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    # 정규화 (0-1 범위로)
    def normalize_feature(feature):
        valid_values = feature[~np.isnan(feature)]
        if len(valid_values) == 0:
            return feature
        min_val, max_val = np.min(valid_values), np.max(valid_values)
        normalized = (feature - min_val) / (max_val - min_val)
        return normalized

    # 피아노롤용 곡선 데이터 생성
    curves = {}

    # F0 곡선 (파란색)
    if np.any(~np.isnan(f0)):
        curves['pitch'] = librosa_f0_to_pixels(f0, sr=sr)

    # 음량 곡선 (빨간색) - 낮은 위치에 표시
    normalized_rms = normalize_feature(rms) * 200 + 100  # 하단 영역
    curves['loudness'] = create_loudness_curve_data(normalized_rms, sr=sr)

    # 음색 밝기 곡선 (초록색) - 중간 위치에 표시
    normalized_centroid = normalize_feature(spectral_centroid) * 200 + 800  # 중간 영역
    curves['brightness'] = create_loudness_curve_data(normalized_centroid, sr=sr)

    return curves
```

## 참고 자료

- [Librosa 특성 추출 문서](https://librosa.org/doc/main/feature.html)
- [F0 분석 상세 가이드](f0-analysis.md)
- [피아노롤 기본 사용법](basic-usage.md)

## 다음 단계

- [실시간 오디오 처리](../user-guide/audio-analysis.md)
- [음성 합성 연동](synthesizer.md)
- [고급 신호 처리](../advanced/performance.md)