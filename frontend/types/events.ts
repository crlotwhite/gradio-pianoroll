/**
 * Event type definitions for Piano Roll
 *
 * This module contains all custom event types used across
 * the piano roll components.
 */

import type { Note } from './notes';
import type { TimeSignature } from './notes';
import type { MousePositionInfo } from '../utils/coordinateUtils';

/**
 * Base interface for all piano roll events.
 */
export interface PianoRollEvent<T = never> {
  /** The type of event */
  type: string;
  /** Event payload data */
  detail: T;
}

/**
 * Event fired when note data changes.
 */
export interface NoteChangeEvent {
  /** Array of all notes */
  notes: Note[];
}

/**
 * Event fired when lyrics are edited.
 */
export interface LyricInputEvent {
  /** Array of all notes (updated) */
  notes: Note[];
  /** Lyric-specific data */
  lyricData: {
    /** ID of the note that was edited */
    noteId: string;
    /** Previous lyric value */
    oldLyric: string;
    /** New lyric value */
    newLyric: string;
    /** The full note object */
    note?: Note;
  };
}

/**
 * Event fired when general data changes.
 */
export interface DataChangeEvent {
  /** Array of all notes */
  notes: Note[];
  /** Tempo in BPM */
  tempo: number;
  /** Time signature */
  timeSignature: TimeSignature;
  /** Current edit mode */
  editMode: string;
  /** Snap setting */
  snapSetting: string;
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Audio sample rate */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
}

/**
 * Event fired during playback.
 */
export interface PlaybackEvent {
  /** Current playback position in flicks */
  currentPosition: number;
  /** Array of all notes */
  notes: Note[];
  /** Tempo in BPM */
  tempo: number;
  /** Whether using backend audio */
  useBackendAudio: boolean;
}

/**
 * Event fired when scroll position changes.
 */
export interface ScrollEvent {
  /** Horizontal scroll position in pixels */
  horizontalScroll: number;
  /** Vertical scroll position in pixels */
  verticalScroll: number;
}

/**
 * Event fired when position info changes (e.g., mouse hover).
 */
export interface PositionInfoEvent {
  /** Position information */
  positionInfo: MousePositionInfo;
}

/**
 * Event fired when utilities are ready.
 */
export interface UtilsReadyEvent {
  /** Convert X to measure info */
  xToMeasureInfo: (x: number) => {
    measure: number;
    beat: number;
    tick: number;
    measureFraction: string;
  };
  /** Convert measure info to X */
  measureInfoToX: (
    measure: number,
    beat: number,
    tick: number,
    ticksPerBeat: number
  ) => number;
  /** Convert Y to pitch */
  yToPitch: (y: number) => { pitch: number; noteName: string };
  /** Convert pitch to Y */
  pitchToY: (pitch: number) => number;
  /** Get MIDI note name */
  getMidiNoteName: (pitch: number) => string;
}

/**
 * Event for layer system changes.
 */
export interface LayerChangedEvent {
  /** Name of the changed layer */
  layerName: string;
  /** New visibility state */
  visible: boolean;
  /** New opacity value */
  opacity: number;
}

/**
 * Grid scroll wheel event with modifier keys.
 */
export interface GridScrollEvent {
  /** Delta X (horizontal scroll) */
  deltaX: number;
  /** Delta Y (vertical scroll) */
  deltaY: number;
  /** Whether shift key is pressed */
  shiftKey: boolean;
  /** Whether ctrl/cmd key is pressed */
  ctrlKey: boolean;
}

/**
 * Edit mode change event payload.
 */
export interface EditModeChangePayload {
  /** New edit mode */
  editMode: 'select' | 'draw' | 'erase';
}

/**
 * Tempo change event payload.
 */
export interface TempoChangePayload {
  /** New tempo value */
  tempo: number;
}

/**
 * Time signature change event payload.
 */
export interface TimeSignatureChangePayload {
  /** New time signature */
  timeSignature: TimeSignature;
}

/**
 * Snap setting change event payload.
 */
export interface SnapChangePayload {
  /** New snap setting */
  snapSetting: string;
}

/**
 * Zoom change event payload.
 */
export interface ZoomChangePayload {
  /** Zoom action type */
  action: 'zoom-in' | 'zoom-out';
  /** New pixels per beat value (optional, calculated if not provided) */
  pixelsPerBeat?: number;
}

/**
 * Position change event payload (from timeline).
 */
export interface PositionChangePayload {
  /** New position in flicks */
  flicks: number;
}

/**
 * Toolbar event payloads.
 */
export interface ToolbarEventMap {
  tempoChange: TempoChangePayload;
  timeSignatureChange: TimeSignatureChangePayload;
  editModeChange: EditModeChangePayload;
  snapChange: SnapChangePayload;
  zoomChange: ZoomChangePayload;
  play: never;
  pause: never;
  stop: never;
  togglePlay: never;
  downloadAudio: never;
}

/**
 * Grid event payloads.
 */
export interface GridEventMap {
  scroll: ScrollEvent;
  noteChange: NoteChangeEvent;
  lyricInput: LyricInputEvent;
  positionInfo: PositionInfoEvent;
  utilsReady: UtilsReadyEvent;
}
