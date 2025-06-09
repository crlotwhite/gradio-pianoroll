// Svelte component props types

import type { Note, PianoRollData, PianoRollBackendData, CurveData, SegmentData } from './backend';

export interface PianoRollProps {
  width?: number;
  height?: number;
  keyboardWidth?: number;
  timelineHeight?: number;
  elem_id?: string;
  
  // 백엔드 데이터 속성들 (새로운 API 구조에 맞춤)
  audio_data?: string | null;
  curve_data?: Record<string, CurveData> | null;
  segment_data?: SegmentData[] | null;
  line_data?: Record<string, CurveData> | null;  // 곡선 데이터의 다른 이름
  use_backend_audio?: boolean;
  
  // 노트 데이터 (완전한 타이밍 정보 포함)
  notes?: Note[];
  
  // 피아노롤 설정
  tempo?: number;
  timeSignature?: { numerator: number; denominator: number };
  editMode?: string;
  snapSetting?: string;
  pixelsPerBeat?: number;
  sampleRate?: number;
  ppqn?: number;
}

export interface ToolbarProps {
  tempo?: number;
  timeSignature?: { numerator: number; denominator: number };
  editMode?: string;
  snapSetting?: string;
  isPlaying?: boolean;
  isRendering?: boolean;
}

export interface LayerControlPanelProps {
  layerManager?: any;
  visible?: boolean;
}

export interface DebugComponentProps {
  currentFlicks?: number;
  tempo?: number;
  notes?: Note[];  // 완전한 Note 타입 사용
  isPlaying?: boolean;
  isRendering?: boolean;
}

// 이벤트 데이터 타입들
export interface PianoRollChangeEvent {
  notes: Note[];
  tempo: number;
  timeSignature: { numerator: number; denominator: number };
  editMode: string;
  snapSetting: string;
  pixelsPerBeat: number;
  sampleRate: number;
  ppqn: number;
}

export interface LyricInputEvent {
  notes: Note[];
  lyricData: {
    noteId: string;
    lyric: string;
    phoneme?: string;
  };
}

export interface NotesChangeEvent {
  notes: Note[];
}

export interface PlaybackEvent {
  currentTime?: number;
  isPlaying?: boolean;
  notes?: Note[];
}

// 백엔드 데이터 관리 관련 타입들
export interface BackendDataManager {
  data: PianoRollBackendData;
  setAudio(audioData: string): void;
  addCurve(name: string, curveData: CurveData): void;
  removeCurve(name: string): void;
  addSegment(segment: SegmentData): void;
  clearSegments(): void;
  enableBackendAudio(enable: boolean): void;
  hasData(): boolean;
}

// 노트 생성/편집 관련 타입들
export interface NoteCreationParams {
  pitch: number;
  startPixels: number;
  durationPixels: number;
  velocity?: number;
  lyric?: string;
  phoneme?: string;
}

export interface NoteEditParams {
  noteId: string;
  updates: Partial<Note>;
}

// 타이밍 계산 관련 타입들
export interface TimingCalculatorOptions {
  pixelsPerBeat: number;
  tempo: number;
  sampleRate: number;
  ppqn: number;
}

// 오디오 처리 관련 타입들
export interface AudioAnalysisResult {
  f0?: number[];  // 기본 주파수
  loudness?: number[];  // 음량
  times?: number[];  // 시간 축
  sampleRate?: number;
}

