/**
 * TypeScript type definitions for backend data classes
 * These types mirror the Python classes in the backend
 */

// PianoRollBackendData 클래스에 대응하는 타입
export interface PianoRollBackendData {
  audio_data?: string | null;
  curve_data?: Record<string, CurveData>;
  segment_data?: SegmentData[];
  use_backend_audio?: boolean;
}

// Note 클래스에 대응하는 완전한 타입 (모든 타이밍 필드 포함)
export interface Note {
  // 기본 노트 속성
  id: string;
  pitch: number;  // MIDI pitch (0-127)
  velocity: number;  // MIDI velocity (0-127)
  lyric?: string;  // 가사 텍스트
  
  // 픽셀 좌표 (기본 좌표계)
  start: number;  // 시작 위치 (픽셀)
  duration: number;  // 지속 시간 (픽셀)
  
  // 자동 계산되는 타이밍 값들
  startFlicks: number;  // Flicks 단위 시작 시간 (정밀한 타이밍)
  durationFlicks: number;  // Flicks 단위 지속 시간
  startSeconds: number;  // 초 단위 시작 시간 (오디오 처리용)
  durationSeconds: number;  // 초 단위 지속 시간
  endSeconds: number;  // 초 단위 종료 시간 (startSeconds + durationSeconds)
  startBeats: number;  // 박자 단위 시작 위치
  durationBeats: number;  // 박자 단위 지속 시간
  startTicks: number;  // MIDI 틱 단위 시작 위치
  durationTicks: number;  // MIDI 틱 단위 지속 시간
  startSample: number;  // 샘플 단위 시작 위치 (오디오 처리용)
  durationSamples: number;  // 샘플 단위 지속 시간
  
  // 음성학 관련 (선택적)
  phoneme?: string;
}

// 곡선 데이터 타입 (F0, loudness 등)
export interface CurveData {
  color: string;
  lineWidth: number;
  yMin: number;
  yMax: number;
  position: string;  // "overlay", "background" 등
  renderMode: string;  // "piano_grid", "independent_range" 등
  visible: boolean;
  opacity: number;
  data: CurvePoint[];
  dataType: string;  // "f0", "loudness" 등
  unit: string;  // "Hz", "dB", "normalized" 등
  originalRange?: {
    minHz?: number;
    maxHz?: number;
    minMidi?: number;
    maxMidi?: number;
    min?: number;
    max?: number;
    y_min?: number;
    y_max?: number;
  };
}

// 곡선 데이터 포인트
export interface CurvePoint {
  x: number;  // X 좌표 (픽셀)
  y: number;  // Y 좌표 (픽셀)
}

// 세그먼트 데이터 타입 (음소, 단어 등의 타이밍 정보)
export interface SegmentData {
  start: number;  // 시작 시간 (초)
  end: number;    // 종료 시간 (초)
  type: string;   // 세그먼트 타입 ("phoneme", "syllable", "word" 등)
  value: string;  // 세그먼트 값/텍스트
  confidence?: number;  // 신뢰도 점수 (0-1)
}

// 피아노롤 전체 데이터 구조
export interface PianoRollData {
  notes: Note[];
  tempo: number;
  timeSignature: {
    numerator: number;
    denominator: number;
  };
  editMode: string;
  snapSetting: string;
  pixelsPerBeat: number;
  sampleRate: number;
  ppqn: number;
  
  // 백엔드 데이터 (선택적으로 포함됨)
  audio_data?: string | null;
  curve_data?: Record<string, CurveData>;
  segment_data?: SegmentData[];
  use_backend_audio?: boolean;
}

// 오디오 유틸리티 관련 타입들
export interface AudioProcessingOptions {
  sampleRate?: number;
  normalize?: boolean;
}

export interface TimingContext {
  pixels_per_beat: number;
  tempo: number;
  sample_rate: number;
  ppqn: number;
}

// API 응답 타입들
export interface CreateNoteResponse {
  note_id: string;
  note: Note;
}

export interface TimingCalculationResult {
  flicks: number;
  seconds: number;
  beats: number;
  ticks: number;
  samples: number;
} 