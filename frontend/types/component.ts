// Svelte component props types
import type { PianoRollData, Note, LineLayerConfig, TimeSignature } from './piano_roll_data';

export interface PianoRollProps {
  width?: number;
  height?: number;
  keyboardWidth?: number;
  timelineHeight?: number;
  elem_id?: string;
  audio_data?: string | null;
  curve_data?: Record<string, any> | null;
  segment_data?: Array<any> | null;
  line_data?: Record<string, LineLayerConfig> | null;
  use_backend_audio?: boolean;
  notes?: Note[];
}

export interface ToolbarProps {
  tempo?: number;
  timeSignature?: TimeSignature;
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
  notes?: Note[];
  isPlaying?: boolean;
  isRendering?: boolean;
}

