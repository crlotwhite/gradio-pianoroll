/**
 * Note-related type definitions for Piano Roll
 *
 * This module contains all types related to musical notes including
 * timing data, pitch, velocity, and lyrical information.
 */

/**
 * Represents a single note in the piano roll.
 * Contains comprehensive timing data in multiple formats for flexibility.
 */
export interface Note {
  /** Unique identifier for the note */
  id: string;
  /** Start position in pixels (primary coordinate) */
  start: number;
  /** Duration in pixels */
  duration: number;
  /** Start time in flicks (Facebook's high-precision time unit) */
  startFlicks?: number;
  /** Duration in flicks */
  durationFlicks?: number;
  /** Start time in seconds */
  startSeconds?: number;
  /** Duration in seconds */
  durationSeconds?: number;
  /** End time in seconds (calculated) */
  endSeconds?: number;
  /** Start position in beats */
  startBeats?: number;
  /** Duration in beats */
  durationBeats?: number;
  /** Start position in MIDI ticks */
  startTicks?: number;
  /** Duration in MIDI ticks */
  durationTicks?: number;
  /** Start position in audio samples */
  startSample?: number;
  /** Duration in audio samples */
  durationSamples?: number;
  /** MIDI pitch value (0-127) */
  pitch: number;
  /** MIDI velocity (0-127) */
  velocity: number;
  /** Lyric text associated with the note (for singing synthesis) */
  lyric?: string;
  /** Phoneme representation of the lyric */
  phoneme?: string;
}

/**
 * Complete timing data for a note position.
 * Used internally for consistent timing calculations.
 */
export interface NoteTimingData {
  /** Time in seconds */
  seconds: number;
  /** Position in beats */
  beats: number;
  /** Position in flicks */
  flicks: number;
  /** Position in MIDI ticks */
  ticks: number;
  /** Position in audio samples */
  samples: number;
}

/**
 * Time signature definition.
 */
export interface TimeSignature {
  /** Number of beats per measure */
  numerator: number;
  /** Note value that receives the beat */
  denominator: number;
}

/**
 * Configuration for note rendering.
 */
export interface NoteRenderConfig {
  /** Height of each note row in pixels */
  noteHeight: number;
  /** Default color for notes */
  defaultColor: string;
  /** Color for selected notes */
  selectedColor: string;
  /** Corner radius for note rectangles */
  cornerRadius: number;
}

/**
 * Extended note information for rendering.
 */
export interface RenderableNote extends Note {
  /** Screen X position */
  screenX: number;
  /** Screen Y position */
  screenY: number;
  /** Whether the note is selected */
  isSelected: boolean;
  /** Whether the mouse is near the note edge */
  isNearEdge: boolean;
}

/**
 * Quantization settings for note snapping.
 */
export interface QuantizationSettings {
  /** Current snap setting (e.g., "1/4", "1/8", "none") */
  snapSetting: string;
  /** Whether quantization is enabled */
  enabled: boolean;
  /** Grid subdivision count */
  subdivisions: number;
}
