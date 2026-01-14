/**
 * Piano roll data types
 *
 * This module contains the main data structures used throughout
 * the piano roll application.
 */

import type { Note, TimeSignature } from './notes';
import type { LineDataPoint } from './layer';

// Re-export for convenience
export type { Note, TimeSignature } from './notes';

/**
 * Extended LineLayerConfig for PianoRollData
 * Includes the data array for the line points
 */
export interface LineLayerConfigWithData {
  data: LineDataPoint[];
  color?: string;
  lineWidth?: number;
  yMin?: number;
  yMax?: number;
  height?: number;
  position?: 'top' | 'center' | 'bottom' | 'overlay';
  renderMode?: 'default' | 'piano_grid' | 'independent_range';
  visible?: boolean;
  opacity?: number;
  dataType?: string;
  unit?: string;
  originalRange?: {
    minHz?: number;
    maxHz?: number;
    minMidi?: number;
    maxMidi?: number;
    min?: number;
    max?: number;
    voiced_ratio?: number;
    y_min?: number;
    y_max?: number;
  };
}

/**
 * Complete piano roll data structure.
 * This is the main data format used for serialization and state management.
 */
export interface PianoRollData {
  /** Array of notes */
  notes: Note[];
  /** Tempo in BPM */
  tempo: number;
  /** Time signature */
  timeSignature: TimeSignature;
  /** Current edit mode ('select', 'draw', 'erase') */
  editMode: string;
  /** Snap setting (e.g., '1/4', '1/8', 'none') */
  snapSetting: string;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat?: number;
  /** Audio sample rate in Hz */
  sampleRate?: number;
  /** MIDI pulses per quarter note */
  ppqn?: number;
  /** Base64 encoded audio data from backend */
  audio_data?: string | null;
  /** Pre-calculated curve data (e.g., waveform, pitch contour) */
  curve_data?: Record<string, unknown> | null;
  /** Segment data for structured audio regions */
  segment_data?: Array<Record<string, unknown>> | null;
  /** Line layer data (e.g., pitch curves, loudness) */
  line_data?: Record<string, LineLayerConfigWithData> | null;
  /** Whether to use backend audio instead of frontend synthesis */
  use_backend_audio?: boolean;
  /** Pre-calculated waveform data points */
  waveform_data?: Array<Record<string, number>> | null;
}

/**
 * Piano roll settings (non-data properties).
 */
export interface PianoRollSettings {
  /** Default zoom level */
  defaultPixelsPerBeat: number;
  /** Minimum zoom level */
  minPixelsPerBeat: number;
  /** Maximum zoom level */
  maxPixelsPerBeat: number;
  /** Zoom step size */
  zoomStep: number;
  /** Default tempo */
  defaultTempo: number;
  /** Default time signature */
  defaultTimeSignature: TimeSignature;
  /** Default snap setting */
  defaultSnapSetting: string;
  /** Default edit mode */
  defaultEditMode: string;
}

/**
 * Validation result for piano roll data.
 */
export interface PianoRollValidationResult {
  /** Whether the data is valid */
  isValid: boolean;
  /** List of validation errors */
  errors: string[];
  /** List of warnings */
  warnings: string[];
  /** Sanitized data (if corrections were applied) */
  sanitizedData?: PianoRollData;
}
