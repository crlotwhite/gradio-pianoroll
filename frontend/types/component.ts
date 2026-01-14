/**
 * Component props types for Piano Roll
 *
 * This module contains TypeScript interfaces for Svelte component props.
 * These define the public API for each component.
 */

import type { Note, TimeSignature } from './notes';
import type { LineLayerConfig } from './layer';

/**
 * Props for the main PianoRoll component.
 */
export interface PianoRollProps {
  /** Total width of the component */
  width?: number;
  /** Total height of the component */
  height?: number;
  /** Width of the keyboard sidebar */
  keyboardWidth?: number;
  /** Height of the timeline */
  timelineHeight?: number;
  /** Unique element ID */
  elem_id?: string;
  /** Base64 encoded audio data from backend */
  audio_data?: string | null;
  /** Pre-calculated curve data */
  curve_data?: Record<string, unknown> | null;
  /** Segment data for audio regions */
  segment_data?: Array<unknown> | null;
  /** Line layer configuration data */
  line_data?: Record<string, LineLayerConfig> | null;
  /** Whether to use backend audio */
  use_backend_audio?: boolean;
  /** Array of notes to display */
  notes?: Note[];
}

/**
 * Props for the Toolbar component.
 */
export interface ToolbarProps {
  /** Current tempo in BPM */
  tempo?: number;
  /** Current time signature */
  timeSignature?: TimeSignature;
  /** Current edit mode */
  editMode?: string;
  /** Current snap setting */
  snapSetting?: string;
  /** Whether audio is currently playing */
  isPlaying?: boolean;
  /** Whether audio is currently rendering */
  isRendering?: boolean;
}

/**
 * Props for the LayerControlPanel component.
 */
export interface LayerControlPanelProps {
  /** Layer manager instance */
  layerManager?: unknown;
  /** Whether the panel is visible */
  visible?: boolean;
}

/**
 * Props for the DebugComponent.
 */
export interface DebugComponentProps {
  /** Current playhead position in flicks */
  currentFlicks?: number;
  /** Current tempo in BPM */
  tempo?: number;
  /** Array of notes for debugging */
  notes?: Note[];
  /** Whether audio is playing */
  isPlaying?: boolean;
  /** Whether audio is rendering */
  isRendering?: boolean;
}

/**
 * Props for the Keyboard component.
 */
export interface KeyboardProps {
  /** Width of the keyboard */
  width: number;
  /** Height of the keyboard */
  height: number;
  /** Current vertical scroll position */
  verticalScroll: number;
  /** Number of octaves to display */
  octaves?: number;
  /** Starting MIDI note number */
  startNote?: number;
}

/**
 * Props for the Timeline component.
 */
export interface TimelineProps {
  /** Width of the timeline */
  width: number;
  /** Height of the timeline */
  height: number;
  /** Current time signature */
  timeSignature: TimeSignature;
  /** Current snap setting */
  snapSetting: string;
  /** Current horizontal scroll position */
  horizontalScroll: number;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Current tempo in BPM */
  tempo: number;
}

/**
 * Props for the Playhead component.
 */
export interface PlayheadProps {
  /** Width of the playhead area */
  width: number;
  /** Height of the playhead area */
  height: number;
  /** Current horizontal scroll position */
  horizontalScroll: number;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Current tempo in BPM */
  tempo: number;
  /** Current playhead position in flicks */
  currentFlicks: number;
  /** Whether audio is playing */
  isPlaying: boolean;
}

/**
 * Props for the Grid component.
 */
export interface GridProps {
  /** Width of the grid */
  width: number;
  /** Height of the grid */
  height: number;
  /** Array of notes to display */
  notes: Note[];
  /** Current tempo in BPM */
  tempo: number;
  /** Current time signature */
  timeSignature: TimeSignature;
  /** Current edit mode */
  editMode: string;
  /** Current snap setting */
  snapSetting: string;
  /** Current horizontal scroll position */
  horizontalScroll: number;
  /** Current vertical scroll position */
  verticalScroll: number;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Current playhead position in flicks */
  currentFlicks: number;
  /** Whether audio is playing */
  isPlaying: boolean;
  /** Audio sample rate */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
  /** Component element ID */
  elem_id: string;
  /** Base64 encoded audio data */
  audio_data: string | null;
  /** Pre-calculated curve data */
  curve_data: object | null;
  /** Line layer data */
  line_data: object | null;
  /** Whether to use backend audio */
  use_backend_audio: boolean;
}

/**
 * Props for the LyricEditor component.
 */
export interface LyricEditorProps {
  /** Whether the editor is in editing mode */
  isEditing: boolean;
  /** ID of the note being edited */
  noteId: string | null;
  /** Current lyric value */
  value: string;
  /** X position on screen */
  x: number;
  /** Y position on screen */
  y: number;
  /** Width of the editor */
  width: number;
}

/**
 * Props for the Waveform component.
 */
export interface WaveformProps {
  /** Audio buffer to display */
  audioBuffer: AudioBuffer | null;
  /** Width of the component */
  width: number;
  /** Height of the component */
  height: number;
  /** Current horizontal scroll position */
  horizontalScroll: number;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Current tempo in BPM */
  tempo: number;
  /** Whether to use backend audio */
  useBackendAudio: boolean;
  /** Pre-calculated waveform data */
  waveformData: Float32Array | null;
}