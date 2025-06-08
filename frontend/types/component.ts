// Svelte component props types

export interface PianoRollProps {
  width?: number;
  height?: number;
  keyboardWidth?: number;
  timelineHeight?: number;
  elem_id?: string;
  audio_data?: string | null;
  curve_data?: object | null;
  segment_data?: Array<any> | null;
  line_data?: object | null;
  use_backend_audio?: boolean;
  notes?: Array<{
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
  }>;
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
  notes?: Array<{
    id: string;
    start: number;
    duration: number;
    pitch: number;
    velocity: number;
    lyric?: string;
    phoneme?: string;
  }>;
  isPlaying?: boolean;
  isRendering?: boolean;
}

