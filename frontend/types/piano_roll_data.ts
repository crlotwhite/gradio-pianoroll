export interface TimeSignature {
  numerator: number;
  denominator: number;
}

export interface Note {
  id: string;
  start: number;
  duration: number;
  startFlicks?: number;
  durationFlicks?: number;
  startSeconds?: number;
  durationSeconds?: number;
  endSeconds?: number;
  startBeats?: number;
  durationBeats?: number;
  startTicks?: number;
  durationTicks?: number;
  startSample?: number;
  durationSamples?: number;
  pitch: number;
  velocity: number;
  lyric?: string;
  phoneme?: string;
}

export interface LineDataPoint {
  x: number;
  y: number;
}

export interface LineLayerConfig {
  color: string;
  lineWidth: number;
  yMin: number;
  yMax: number;
  position?: string;
  renderMode?: string;
  visible?: boolean;
  opacity?: number;
  dataType?: string;
  unit?: string;
  originalRange?: Record<string, any>;
  data: LineDataPoint[];
}

export interface PianoRollData {
  notes: Note[];
  tempo: number;
  timeSignature: TimeSignature;
  editMode: string;
  snapSetting: string;
  pixelsPerBeat?: number;
  sampleRate?: number;
  ppqn?: number;
  audio_data?: string | null;
  curve_data?: Record<string, any> | null;
  segment_data?: Array<Record<string, any>> | null;
  line_data?: Record<string, LineLayerConfig> | null;
  use_backend_audio?: boolean;
  waveform_data?: Array<Record<string, number>> | null;
}
