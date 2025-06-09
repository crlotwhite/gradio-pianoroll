# ⚡ 성능 최적화

대용량 데이터와 실시간 처리를 위한 성능 최적화 가이드입니다.

## 🎯 최적화 목표

- **메모리 사용량 감소**: 대용량 오디오 데이터 처리
- **CPU 성능 향상**: 실시간 분석 및 합성
- **UI 반응성 개선**: 부드러운 사용자 경험
- **네트워크 효율성**: 데이터 전송 최적화

## 💾 메모리 최적화

### 1. 오디오 데이터 관리

```python
import numpy as np
from gradio_pianoroll import PianoRoll

def optimize_audio_memory():
    """메모리 효율적인 오디오 데이터 처리"""
    
    # 샘플레이트 최적화 (44100 -> 22050)
    sr = 22050  # 음성 분석에는 충분
    
    # 데이터 타입 최적화
    audio_data = np.array(audio_data, dtype=np.float32)  # float64 대신
    
    # 청크 단위 처리
    chunk_size = 1024
    processed_chunks = []
    
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i+chunk_size]
        # 처리...
        processed_chunks.append(process_chunk(chunk))
        
        # 메모리 정리
        del chunk
    
    return np.concatenate(processed_chunks)

# 불필요한 데이터 제거
def cleanup_piano_roll_data(piano_roll_data):
    """불필요한 데이터 제거로 메모리 절약"""
    cleaned_data = piano_roll_data.copy()
    
    # 빈 curve_data, segment_data 제거
    if not cleaned_data.get('curve_data'):
        cleaned_data['curve_data'] = {}
    
    if not cleaned_data.get('segment_data'):
        cleaned_data['segment_data'] = []
    
    # 불필요한 노트 속성 제거
    for note in cleaned_data.get('notes', []):
        # 빈 lyric 제거
        if note.get('lyric') == '':
            note.pop('lyric', None)
        
        # 빈 phoneme 제거
        if note.get('phoneme') == '':
            note.pop('phoneme', None)
    
    return cleaned_data
```

### 2. 대용량 노트 처리

```python
def optimize_large_note_count(notes_data):
    """1000개 이상의 노트 최적화"""
    
    # 노트 개수 제한
    MAX_NOTES = 2000
    if len(notes_data.get('notes', [])) > MAX_NOTES:
        print(f"⚠️ 노트가 {len(notes_data['notes'])}개입니다. 성능 저하 가능")
        
        # 가장 중요한 노트만 선택 (예: 음량 기준)
        notes = sorted(
            notes_data['notes'], 
            key=lambda x: x.get('velocity', 0), 
            reverse=True
        )[:MAX_NOTES]
        
        notes_data['notes'] = notes
        print(f"✅ 상위 {MAX_NOTES}개 노트만 유지")
    
    return notes_data

# 가상화된 렌더링 (큰 데이터셋용)
def create_virtualized_pianoroll():
    """가상화를 통한 대용량 데이터 렌더링"""
    
    # 뷰포트 기반 렌더링 설정
    viewport_config = {
        "virtualScrolling": True,
        "bufferSize": 100,  # 화면 밖 노트 버퍼
        "renderThreshold": 500  # 이 개수 이상일 때 가상화 활성화
    }
    
    return PianoRoll(
        height=600,
        width=1000,
        value={"viewport_config": viewport_config}
    )
```

## 🚀 CPU 성능 최적화

### 1. librosa 가속화

```python
import os
import librosa
import numba

# numba 설치 및 설정
# pip install numba

# 멀티스레딩 설정
os.environ['NUMBA_NUM_THREADS'] = '4'  # CPU 코어 수에 맞게

# 캐시 활성화
os.environ['LIBROSA_CACHE_DIR'] = '/tmp/librosa_cache'

@numba.jit(nopython=True)
def fast_f0_analysis(y, sr=22050):
    """numba로 가속화된 F0 분석"""
    
    # 사전 필터링으로 성능 향상
    hop_length = 512
    frame_length = 2048
    
    # 고성능 F0 추출
    f0 = librosa.pyin(
        y, 
        fmin=50, 
        fmax=800,
        sr=sr,
        hop_length=hop_length,
        frame_length=frame_length,
        center=True,
        pad_mode='constant'
    )[0]
    
    return f0

# 배치 처리로 성능 향상
def batch_process_audio(audio_files, batch_size=4):
    """여러 오디오 파일을 배치로 처리"""
    results = []
    
    for i in range(0, len(audio_files), batch_size):
        batch = audio_files[i:i+batch_size]
        
        # 병렬 처리
        with multiprocessing.Pool(processes=batch_size) as pool:
            batch_results = pool.map(fast_f0_analysis, batch)
        
        results.extend(batch_results)
    
    return results
```

### 2. 실시간 처리 최적화

```python
import threading
import queue

class RealtimeProcessor:
    """실시간 오디오 처리를 위한 최적화된 클래스"""
    
    def __init__(self, buffer_size=1024):
        self.buffer_size = buffer_size
        self.input_queue = queue.Queue(maxsize=10)
        self.output_queue = queue.Queue(maxsize=10)
        self.processing = False
        
    def start_processing(self):
        """백그라운드 처리 시작"""
        self.processing = True
        self.worker_thread = threading.Thread(target=self._process_worker)
        self.worker_thread.start()
    
    def _process_worker(self):
        """백그라운드 워커 스레드"""
        while self.processing:
            try:
                # 논블로킹으로 데이터 가져오기
                data = self.input_queue.get(timeout=0.1)
                
                # 실시간 처리 (가벼운 연산만)
                result = self._lightweight_process(data)
                
                # 결과 저장
                self.output_queue.put(result)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"처리 오류: {e}")
    
    def _lightweight_process(self, data):
        """가벼운 실시간 처리"""
        # 복잡한 분석은 별도 스레드에서
        # 여기서는 기본적인 처리만
        return {
            'processed_at': time.time(),
            'data_length': len(data),
            'peak_level': np.max(np.abs(data)) if len(data) > 0 else 0
        }

# 사용 예제
processor = RealtimeProcessor()
processor.start_processing()
```

## 🖥️ UI 반응성 최적화

### 1. 비동기 처리

```python
import asyncio
import gradio as gr

async def async_audio_analysis(audio_data):
    """비동기 오디오 분석"""
    
    # CPU 집약적 작업을 별도 스레드에서
    loop = asyncio.get_event_loop()
    
    # F0 분석 (별도 스레드)
    f0_task = loop.run_in_executor(None, extract_f0, audio_data)
    
    # Loudness 분석 (별도 스레드)
    loudness_task = loop.run_in_executor(None, extract_loudness, audio_data)
    
    # 병렬 실행
    f0_result, loudness_result = await asyncio.gather(f0_task, loudness_task)
    
    return {
        'f0': f0_result,
        'loudness': loudness_result
    }

# Gradio 비동기 인터페이스
def create_async_interface():
    """비동기 처리를 사용하는 인터페이스"""
    
    with gr.Blocks() as demo:
        piano_roll = PianoRoll()
        
        # 비동기 이벤트 핸들러
        async def handle_change(data):
            # 무거운 처리는 백그라운드에서
            result = await async_audio_analysis(data)
            return result
        
        piano_roll.change(
            fn=handle_change,
            inputs=piano_roll,
            outputs=piano_roll
        )
    
    return demo
```

### 2. 프론트엔드 최적화

```python
def optimize_frontend_data(piano_roll_data):
    """프론트엔드 전송 데이터 최적화"""
    
    # 정밀도 조정 (소수점 3자리로 제한)
    def round_numbers(obj):
        if isinstance(obj, float):
            return round(obj, 3)
        elif isinstance(obj, dict):
            return {k: round_numbers(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [round_numbers(item) for item in obj]
        return obj
    
    # 데이터 압축
    optimized_data = round_numbers(piano_roll_data)
    
    # 불필요한 필드 제거
    for note in optimized_data.get('notes', []):
        # 기본값과 같은 필드 제거
        if note.get('velocity') == 100:
            note.pop('velocity', None)
        
        # 빈 문자열 제거
        if note.get('lyric') == '':
            note.pop('lyric', None)
    
    return optimized_data
```

## 📊 성능 모니터링

### 1. 메모리 사용량 추적

```python
import psutil
import tracemalloc

def monitor_memory_usage():
    """메모리 사용량 모니터링"""
    
    # 메모리 추적 시작
    tracemalloc.start()
    
    def get_memory_info():
        # 현재 프로세스 메모리
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Python 메모리 추적
        current, peak = tracemalloc.get_traced_memory()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # MB
            'vms_mb': memory_info.vms / 1024 / 1024,  # MB
            'python_current_mb': current / 1024 / 1024,
            'python_peak_mb': peak / 1024 / 1024
        }
    
    return get_memory_info

# 사용 예제
memory_monitor = monitor_memory_usage()

def process_with_monitoring(data):
    """메모리 모니터링과 함께 처리"""
    
    before = memory_monitor()
    print(f"처리 전 메모리: {before['rss_mb']:.1f}MB")
    
    # 실제 처리
    result = heavy_processing(data)
    
    after = memory_monitor()
    print(f"처리 후 메모리: {after['rss_mb']:.1f}MB")
    print(f"메모리 증가: {after['rss_mb'] - before['rss_mb']:.1f}MB")
    
    return result
```

### 2. 성능 벤치마킹

```python
import time
import functools

def benchmark(func):
    """함수 성능 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} 실행 시간: {end_time - start_time:.3f}초")
        return result
    return wrapper

@benchmark
def benchmark_f0_extraction(audio_data):
    """F0 추출 성능 측정"""
    return librosa.pyin(audio_data, fmin=50, fmax=800)

@benchmark
def benchmark_note_processing(notes_data):
    """노트 처리 성능 측정"""
    return process_piano_roll_notes(notes_data)

# 전체 파이프라인 벤치마크
def run_performance_benchmark():
    """성능 벤치마크 실행"""
    
    print("🚀 성능 벤치마크 시작...")
    
    # 테스트 데이터 생성
    test_audio = np.random.randn(22050 * 5)  # 5초 오디오
    test_notes = generate_test_notes(1000)   # 1000개 노트
    
    # 각 기능별 성능 측정
    benchmark_f0_extraction(test_audio)
    benchmark_note_processing(test_notes)
    
    print("✅ 벤치마크 완료")
```

## 🔧 실용적인 최적화 팁

### 1. 개발 vs 프로덕션 설정

```python
import os

# 환경별 설정
if os.getenv('ENVIRONMENT') == 'production':
    # 프로덕션: 안정성 우선
    SAMPLE_RATE = 22050
    MAX_NOTES = 1000
    ENABLE_CACHE = True
    LOG_LEVEL = 'WARNING'
else:
    # 개발: 기능 우선
    SAMPLE_RATE = 44100
    MAX_NOTES = 5000
    ENABLE_CACHE = False
    LOG_LEVEL = 'DEBUG'

def get_optimized_config():
    """환경에 맞는 최적화 설정"""
    return {
        'sample_rate': SAMPLE_RATE,
        'max_notes': MAX_NOTES,
        'enable_cache': ENABLE_CACHE,
        'chunk_size': 1024 if SAMPLE_RATE == 22050 else 2048
    }
```

### 2. 점진적 로딩

```python
def create_progressive_piano_roll():
    """점진적 로딩이 가능한 피아노롤"""
    
    # 기본 데이터만 먼저 로드
    basic_data = {
        'notes': [],  # 빈 상태로 시작
        'tempo': 120,
        'editMode': 'select'
    }
    
    piano_roll = PianoRoll(value=basic_data)
    
    # 실제 데이터는 백그라운드에서 로드
    def load_notes_progressively():
        import threading
        
        def load_worker():
            # 무거운 데이터 로드
            full_notes = load_full_note_data()
            
            # UI 업데이트
            piano_roll.update(value={
                **basic_data,
                'notes': full_notes
            })
        
        threading.Thread(target=load_worker).start()
    
    # 초기화 후 실제 데이터 로드
    load_notes_progressively()
    
    return piano_roll
```

## 📈 성능 체크리스트

### ✅ 메모리 최적화
- [ ] 오디오 샘플레이트 적절히 설정 (22050Hz 권장)
- [ ] 데이터 타입 최적화 (float32 사용)
- [ ] 불필요한 데이터 정리
- [ ] 청크 단위 처리 구현

### ✅ CPU 최적화
- [ ] numba 설치 및 활용
- [ ] 멀티스레딩 설정
- [ ] 배치 처리 구현
- [ ] 캐시 활성화

### ✅ UI 반응성
- [ ] 비동기 처리 구현
- [ ] 백그라운드 작업 분리
- [ ] 프론트엔드 데이터 최적화
- [ ] 점진적 로딩 구현

### ✅ 모니터링
- [ ] 메모리 사용량 추적
- [ ] 성능 벤치마크 설정
- [ ] 로그 수준 조정
- [ ] 환경별 설정 분리

---

**더 자세한 최적화 방법이 필요하시면** [GitHub Issues](https://github.com/crlotwhite/gradio-pianoroll/issues)에서 문의해주세요! 🚀 