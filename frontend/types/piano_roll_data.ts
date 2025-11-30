// Import canonical types from layer.ts
import type { Note, LineDataPoint, LineLayerConfig } from './layer';

// Re-export for backward compatibility
export type { Note, LineDataPoint, LineLayerConfig };

export interface TimeSignature {
  numerator: number;
  denominator: number;
}

/**
 * Extended LineLayerConfig for PianoRollData
 * Includes the data array for the line points
 */
export interface LineLayerConfigWithData extends LineLayerConfig {
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
  line_data?: Record<string, LineLayerConfigWithData> | null;
  use_backend_audio?: boolean;
  waveform_data?: Array<Record<string, number>> | null;
}
