# 개발자 예제

실제 프로젝트에서 활용할 수 있는 Gradio PianoRoll 컴포넌트의 다양한 예제들을 제공합니다.

## 🎹 기본 예제

### 1. 간단한 MIDI 에디터

```python
import gradio as gr
from gradio_pianoroll import PianoRoll

def save_midi_data(piano_roll_data):
    """MIDI 데이터를 파일로 저장"""
    notes = piano_roll_data.get("notes", [])
    tempo = piano_roll_data.get("tempo", 120)
    
    # MIDI 파일 생성 로직 (python-midi 등 사용)
    filename = f"composition_{len(notes)}_notes.mid"
    
    return f"✅ {filename}에 {len(notes)}개 노트가 저장되었습니다."

with gr.Blocks(title="MIDI 작곡 도구") as demo:
    with gr.Row():
        piano_roll = PianoRoll(
            label="🎼 MIDI 에디터",
            height=500,
            width=1200
        )
    
    with gr.Row():
        save_btn = gr.Button("💾 MIDI 저장", variant="primary")
        clear_btn = gr.Button("🗑️ 초기화", variant="secondary")
    
    status_text = gr.Textbox(label="상태", interactive=False)
    
    save_btn.click(
        fn=save_midi_data,
        inputs=[piano_roll],
        outputs=[status_text]
    )

demo.launch()
```

### 2. 실시간 음악 분석기

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
import librosa
import numpy as np

def analyze_composition(piano_roll_data):
    """작곡된 음악의 특성 분석"""
    notes = piano_roll_data.get("notes", [])
    tempo = piano_roll_data.get("tempo", 120)
    
    if not notes:
        return {"분석": "노트가 없습니다."}
    
    # 음정 분석
    pitches = [note["pitch"] for note in notes]
    pitch_range = max(pitches) - min(pitches)
    avg_pitch = np.mean(pitches)
    
    # 리듬 분석
    durations = [note["durationSeconds"] for note in notes]
    avg_duration = np.mean(durations)
    
    # 조성 추정 (간단한 버전)
    pitch_classes = [pitch % 12 for pitch in pitches]
    most_common_key = max(set(pitch_classes), key=pitch_classes.count)
    
    analysis = {
        "총 노트 수": len(notes),
        "음역대": f"{pitch_range} 반음",
        "평균 음높이": f"MIDI {avg_pitch:.1f}",
        "평균 노트 길이": f"{avg_duration:.2f}초",
        "추정 조성": f"Key of {most_common_key}",
        "템포": f"{tempo} BPM"
    }
    
    return analysis

with gr.Blocks() as demo:
    piano_roll = PianoRoll(height=400)
    
    with gr.Row():
        analyze_btn = gr.Button("🔍 음악 분석")
        analysis_output = gr.JSON(label="분석 결과")
    
    analyze_btn.click(
        fn=analyze_composition,
        inputs=[piano_roll],
        outputs=[analysis_output]
    )
    
    # 실시간 분석 (노트 변경시마다)
    piano_roll.change(
        fn=analyze_composition,
        inputs=[piano_roll],
        outputs=[analysis_output]
    )

demo.launch()
```

## 🎤 음성 합성 예제

### 3. 한국어 가사 TTS 시스템

```python
from gradio_pianoroll import PianoRoll
import gradio as gr

def text_to_phoneme(text):
    """한국어 텍스트를 음소로 변환 (간단한 예제)"""
    # 실제로는 G2P 라이브러리 사용
    phoneme_map = {
        "안녕": "ㅇㅏㄴㄴㅕㅇ",
        "하세요": "ㅎㅏㅅㅔㅇㅛ",
        "감사": "ㄱㅏㅁㅅㅏ",
        "합니다": "ㅎㅏㅁㄴㅣㄷㅏ"
    }
    return phoneme_map.get(text, text)

def process_lyrics_input(piano_roll_data, lyrics_text):
    """가사 입력을 처리하여 노트에 할당"""
    notes = piano_roll_data.get("notes", [])
    lyrics_list = lyrics_text.strip().split()
    
    # 가사를 노트에 순서대로 할당
    for i, note in enumerate(notes):
        if i < len(lyrics_list):
            note["lyric"] = lyrics_list[i]
            # 음소 변환도 함께 저장
            note["phoneme"] = text_to_phoneme(lyrics_list[i])
    
    return piano_roll_data

def synthesize_speech(piano_roll_data):
    """음성 합성 수행"""
    notes = piano_roll_data.get("notes", [])
    
    if not notes:
        return piano_roll_data, "노트가 없습니다."
    
    # 각 노트의 가사와 음높이를 이용해 음성 합성
    synthesis_info = []
    
    for note in notes:
        lyric = note.get("lyric", "")
        phoneme = note.get("phoneme", "")
        pitch = note.get("pitch", 60)
        duration = note.get("durationSeconds", 1.0)
        
        if lyric:
            synthesis_info.append(f"'{lyric}' ({phoneme}) - {pitch} MIDI, {duration:.2f}초")
    
    # 실제 음성 합성 로직은 여기에 구현
    # piano_roll_data["audio_data"] = synthesized_audio_base64
    piano_roll_data["use_backend_audio"] = True
    
    status = f"✅ {len(synthesis_info)}개 노트의 음성을 합성했습니다:\n" + "\n".join(synthesis_info)
    
    return piano_roll_data, status

with gr.Blocks(title="한국어 TTS 시스템") as demo:
    gr.Markdown("## 🎤 한국어 가사 음성 합성")
    
    with gr.Row():
        with gr.Column(scale=3):
            piano_roll = PianoRoll(
                height=400,
                use_backend_audio=True
            )
        
        with gr.Column(scale=1):
            lyrics_input = gr.Textbox(
                label="🎵 가사 입력",
                placeholder="안녕 하세요 감사 합니다",
                lines=5
            )
            
            process_lyrics_btn = gr.Button("📝 가사 적용")
            synthesize_btn = gr.Button("🎤 음성 합성", variant="primary")
    
    status_output = gr.Textbox(label="합성 상태", lines=6, interactive=False)
    
    process_lyrics_btn.click(
        fn=process_lyrics_input,
        inputs=[piano_roll, lyrics_input],
        outputs=[piano_roll]
    )
    
    synthesize_btn.click(
        fn=synthesize_speech,
        inputs=[piano_roll],
        outputs=[piano_roll, status_output]
    )

demo.launch()
```

## 🔊 오디오 분석 예제

### 4. 음성 분석 도구

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
import librosa
import numpy as np

def extract_pitch_curve(audio_file):
    """오디오에서 피치 곡선 추출"""
    if not audio_file:
        return None
    
    # 오디오 로드
    y, sr = librosa.load(audio_file)
    
    # F0 추출 (PYIN)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
    )
    
    # 시간축 생성
    times = librosa.frames_to_time(np.arange(len(f0)), sr=sr)
    
    return f0, times, voiced_probs

def create_pitch_visualization(f0_data, times, tempo=120, pixels_per_beat=80):
    """F0 데이터를 피아노롤 시각화 형태로 변환"""
    line_points = []
    
    for i, (f0_val, time_val) in enumerate(zip(f0_data, times)):
        if not np.isnan(f0_val) and f0_val > 0:
            # 시간을 픽셀로 변환
            x_pixel = time_val * (tempo / 60) * pixels_per_beat
            
            # 주파수를 MIDI 노트로 변환
            midi_note = librosa.hz_to_midi(f0_val)
            y_pixel = (127 - midi_note) * 10  # 피아노롤 Y 좌표
            
            line_points.append({"x": x_pixel, "y": y_pixel})
    
    return {
        "f0_curve": {
            "type": "line",
            "points": line_points,
            "color": "#ff6b6b",
            "lineWidth": 2
        }
    }

def analyze_uploaded_audio(piano_roll_data, audio_file):
    """업로드된 오디오 분석"""
    if not audio_file:
        return piano_roll_data, "오디오 파일을 업로드해주세요."
    
    try:
        # 피치 추출
        f0_data, times, voiced_probs = extract_pitch_curve(audio_file)
        
        # 시각화 데이터 생성
        curve_data = create_pitch_visualization(f0_data, times)
        
        # 피아노롤에 적용
        piano_roll_data["curve_data"] = curve_data
        
        # 통계 정보
        valid_f0 = f0_data[~np.isnan(f0_data) & (f0_data > 0)]
        if len(valid_f0) > 0:
            status = f"""
✅ 피치 분석 완료
• 총 프레임: {len(f0_data)}
• 유성음 프레임: {len(valid_f0)} ({len(valid_f0)/len(f0_data)*100:.1f}%)
• 평균 F0: {np.mean(valid_f0):.1f} Hz
• F0 범위: {np.min(valid_f0):.1f} - {np.max(valid_f0):.1f} Hz
• 평균 유성음 확률: {np.mean(voiced_probs):.2f}
            """
        else:
            status = "❌ 유효한 피치를 찾을 수 없습니다."
        
        return piano_roll_data, status.strip()
        
    except Exception as e:
        return piano_roll_data, f"❌ 분석 실패: {str(e)}"

with gr.Blocks(title="음성 분석 도구") as demo:
    gr.Markdown("## 🔍 음성 피치 분석 도구")
    
    with gr.Row():
        with gr.Column(scale=2):
            audio_input = gr.Audio(
                label="🎵 분석할 오디오 업로드",
                type="filepath"
            )
            analyze_btn = gr.Button("🔬 피치 분석 시작", variant="primary")
        
        with gr.Column(scale=1):
            analysis_status = gr.Textbox(
                label="분석 상태",
                lines=8,
                interactive=False
            )
    
    piano_roll = PianoRoll(
        label="📊 피치 곡선 시각화",
        height=500,
        width=1200
    )
    
    analyze_btn.click(
        fn=analyze_uploaded_audio,
        inputs=[piano_roll, audio_input],
        outputs=[piano_roll, analysis_status]
    )

demo.launch()
```

### 5. 실시간 오디오 모니터링

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
import numpy as np

class AudioMonitor:
    def __init__(self):
        self.is_monitoring = False
        self.audio_buffer = []
    
    def start_monitoring(self):
        self.is_monitoring = True
        return "🔴 모니터링 시작됨"
    
    def stop_monitoring(self):
        self.is_monitoring = False
        return "⏹️ 모니터링 중지됨"
    
    def process_audio_chunk(self, audio_chunk):
        """실시간 오디오 청크 처리"""
        if not self.is_monitoring:
            return None
        
        # 간단한 피치 분석 (실제로는 더 복잡한 알고리즘 사용)
        # 여기서는 데모용 랜덤 데이터 생성
        mock_f0 = 200 + 100 * np.sin(len(self.audio_buffer) * 0.1)
        
        self.audio_buffer.append({
            "time": len(self.audio_buffer) * 0.1,
            "f0": mock_f0,
            "amplitude": np.random.random()
        })
        
        # 최근 100개 샘플만 유지
        if len(self.audio_buffer) > 100:
            self.audio_buffer = self.audio_buffer[-100:]
        
        return self.create_realtime_visualization()
    
    def create_realtime_visualization(self):
        """실시간 시각화 데이터 생성"""
        if not self.audio_buffer:
            return {}
        
        line_points = []
        for i, sample in enumerate(self.audio_buffer):
            x_pixel = i * 10  # 10픽셀 간격
            midi_note = librosa.hz_to_midi(sample["f0"])
            y_pixel = (127 - midi_note) * 10
            
            line_points.append({"x": x_pixel, "y": y_pixel})
        
        return {
            "realtime_f0": {
                "type": "line",
                "points": line_points,
                "color": "#00ff00",
                "lineWidth": 3
            }
        }

monitor = AudioMonitor()

def update_monitoring_display(piano_roll_data):
    """모니터링 디스플레이 업데이트"""
    # 실시간 오디오 처리 시뮬레이션
    visualization = monitor.process_audio_chunk(None)
    
    if visualization:
        piano_roll_data["curve_data"] = visualization
    
    return piano_roll_data

with gr.Blocks(title="실시간 오디오 모니터") as demo:
    gr.Markdown("## 🎙️ 실시간 오디오 피치 모니터링")
    
    with gr.Row():
        start_btn = gr.Button("🔴 모니터링 시작", variant="primary")
        stop_btn = gr.Button("⏹️ 모니터링 중지", variant="secondary")
        status_text = gr.Textbox(label="상태", interactive=False)
    
    piano_roll = PianoRoll(
        label="📊 실시간 피치 모니터",
        height=400,
        width=1000
    )
    
    # 실시간 업데이트 (0.1초마다)
    timer = gr.Timer(0.1)
    
    start_btn.click(
        fn=monitor.start_monitoring,
        outputs=[status_text]
    )
    
    stop_btn.click(
        fn=monitor.stop_monitoring,
        outputs=[status_text]
    )
    
    timer.tick(
        fn=update_monitoring_display,
        inputs=[piano_roll],
        outputs=[piano_roll]
    )

demo.launch()
```

## 🎛️ 고급 활용 예제

### 6. 음악 교육 도구

```python
import gradio as gr
from gradio_pianoroll import PianoRoll
import random

class MusicTeacher:
    def __init__(self):
        self.scales = {
            "C Major": [60, 62, 64, 65, 67, 69, 71],
            "A Minor": [57, 59, 60, 62, 64, 65, 67],
            "G Major": [67, 69, 71, 72, 74, 76, 78],
            "E Minor": [64, 66, 67, 69, 71, 72, 74]
        }
        self.current_exercise = None
    
    def generate_scale_exercise(self, scale_name):
        """스케일 연습 문제 생성"""
        if scale_name not in self.scales:
            return None
        
        notes = []
        scale_notes = self.scales[scale_name]
        
        for i, pitch in enumerate(scale_notes):
            note = {
                "id": f"scale-note-{i}",
                "start": i * 160,  # 160픽셀 간격
                "duration": 120,
                "pitch": pitch,
                "velocity": 100,
                "lyric": f"도레미파솔라시"[i] if i < 7 else ""
            }
            notes.append(note)
        
        self.current_exercise = {
            "type": "scale",
            "scale": scale_name,
            "notes": notes
        }
        
        return {
            "notes": notes,
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80
        }
    
    def generate_interval_exercise(self, interval_type):
        """음정 연습 문제 생성"""
        intervals = {
            "Perfect 5th": 7,
            "Major 3rd": 4,
            "Minor 3rd": 3,
            "Octave": 12
        }
        
        if interval_type not in intervals:
            return None
        
        root_note = random.randint(60, 72)
        interval_semitones = intervals[interval_type]
        
        notes = [
            {
                "id": "interval-root",
                "start": 0,
                "duration": 160,
                "pitch": root_note,
                "velocity": 100,
                "lyric": "Root"
            },
            {
                "id": "interval-target",
                "start": 200,
                "duration": 160,
                "pitch": root_note + interval_semitones,
                "velocity": 100,
                "lyric": interval_type
            }
        ]
        
        return {
            "notes": notes,
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80
        }

teacher = MusicTeacher()

def load_scale_exercise(scale_name):
    """스케일 연습 로드"""
    exercise_data = teacher.generate_scale_exercise(scale_name)
    if exercise_data:
        return exercise_data, f"✅ {scale_name} 스케일 연습이 로드되었습니다."
    else:
        return None, "❌ 스케일을 찾을 수 없습니다."

def load_interval_exercise(interval_type):
    """음정 연습 로드"""
    exercise_data = teacher.generate_interval_exercise(interval_type)
    if exercise_data:
        return exercise_data, f"✅ {interval_type} 음정 연습이 로드되었습니다."
    else:
        return None, "❌ 음정을 찾을 수 없습니다."

def check_student_answer(piano_roll_data):
    """학생 답안 검사"""
    if not teacher.current_exercise:
        return "연습 문제를 먼저 로드해주세요."
    
    student_notes = piano_roll_data.get("notes", [])
    correct_notes = teacher.current_exercise["notes"]
    
    if len(student_notes) != len(correct_notes):
        return f"❌ 노트 개수가 틀렸습니다. (정답: {len(correct_notes)}개, 입력: {len(student_notes)}개)"
    
    correct_count = 0
    for i, (student, correct) in enumerate(zip(student_notes, correct_notes)):
        if abs(student.get("pitch", 0) - correct["pitch"]) == 0:
            correct_count += 1
    
    accuracy = correct_count / len(correct_notes) * 100
    
    if accuracy == 100:
        return f"🎉 완벽합니다! {accuracy:.0f}% 정확도"
    elif accuracy >= 80:
        return f"👍 좋습니다! {accuracy:.0f}% 정확도 ({correct_count}/{len(correct_notes)})"
    else:
        return f"💪 더 연습해보세요. {accuracy:.0f}% 정확도 ({correct_count}/{len(correct_notes)})"

with gr.Blocks(title="음악 교육 도구") as demo:
    gr.Markdown("## 🎼 음악 이론 학습 도구")
    
    with gr.Tabs():
        with gr.TabItem("스케일 연습"):
            with gr.Row():
                scale_dropdown = gr.Dropdown(
                    choices=list(teacher.scales.keys()),
                    label="스케일 선택",
                    value="C Major"
                )
                load_scale_btn = gr.Button("📚 스케일 로드")
            
            piano_roll_scale = PianoRoll(height=300)
            scale_status = gr.Textbox(label="스케일 연습 상태", interactive=False)
            
            load_scale_btn.click(
                fn=load_scale_exercise,
                inputs=[scale_dropdown],
                outputs=[piano_roll_scale, scale_status]
            )
        
        with gr.TabItem("음정 연습"):
            with gr.Row():
                interval_dropdown = gr.Dropdown(
                    choices=["Perfect 5th", "Major 3rd", "Minor 3rd", "Octave"],
                    label="음정 선택",
                    value="Perfect 5th"
                )
                load_interval_btn = gr.Button("📚 음정 로드")
            
            piano_roll_interval = PianoRoll(height=300)
            interval_status = gr.Textbox(label="음정 연습 상태", interactive=False)
            
            load_interval_btn.click(
                fn=load_interval_exercise,
                inputs=[interval_dropdown],
                outputs=[piano_roll_interval, interval_status]
            )
    
    with gr.Row():
        check_btn = gr.Button("✅ 답안 검사", variant="primary")
        result_text = gr.Textbox(label="검사 결과", interactive=False)
    
    # 현재 활성 탭에 따라 검사 (간단화를 위해 스케일만)
    check_btn.click(
        fn=check_student_answer,
        inputs=[piano_roll_scale],
        outputs=[result_text]
    )

demo.launch()
```

이 예제들은 Gradio PianoRoll 컴포넌트의 다양한 활용 방법을 보여줍니다. 각 예제를 참고하여 음악 교육, 작곡 도구, 음성 분석 등 다양한 목적에 맞는 애플리케이션을 개발할 수 있습니다. 