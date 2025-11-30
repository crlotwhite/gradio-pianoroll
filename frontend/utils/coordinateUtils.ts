/**
 * Coordinate Utilities for Piano Roll Grid
 *
 * This module provides conversion functions between different coordinate systems:
 * - Pixel coordinates (screen space)
 * - Musical coordinates (measures, beats, ticks)
 * - MIDI pitch values
 *
 * These utilities enable consistent coordinate transformations across the piano roll.
 */

import { NOTE_HEIGHT, TOTAL_NOTES } from './constants';

// ============================================================================
// Types
// ============================================================================

/**
 * Represents a position in musical time (measure, beat, tick).
 */
export interface MeasureInfo {
  /** 1-based measure number */
  measure: number;
  /** 1-based beat number within the measure */
  beat: number;
  /** Tick within the beat (0-based) */
  tick: number;
  /** Human-readable fraction (e.g., "2/4" for 2nd beat in 4/4) */
  measureFraction: string;
}

/**
 * Represents pitch information with both MIDI value and note name.
 */
export interface PitchInfo {
  /** MIDI pitch value (0-127) */
  pitch: number;
  /** Human-readable note name (e.g., "C4", "F#5") */
  noteName: string;
}

/**
 * Configuration required for coordinate calculations.
 */
export interface CoordinateConfig {
  /** Pixels per beat (determines horizontal zoom level) */
  pixelsPerBeat: number;
  /** Beats per measure (from time signature numerator) */
  beatsPerMeasure: number;
  /** Current snap setting (e.g., "1/4", "1/8", "none") */
  snapSetting: string;
}

// ============================================================================
// Note Names
// ============================================================================

/** Standard Western chromatic note names */
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

/**
 * Convert MIDI pitch to note name.
 *
 * @param pitch - MIDI pitch value (0-127)
 * @returns Note name with octave (e.g., "C4", "F#5")
 *
 * @example
 * getMidiNoteName(60) // "C4"
 * getMidiNoteName(69) // "A4"
 */
export function getMidiNoteName(pitch: number): string {
  const noteName = NOTE_NAMES[pitch % 12];
  const octave = Math.floor(pitch / 12) - 1; // MIDI standard: C4 is 60
  return `${noteName}${octave}`;
}

// ============================================================================
// Vertical (Pitch) Coordinate Conversions
// ============================================================================

/**
 * Convert Y coordinate to MIDI pitch.
 *
 * The piano roll displays higher pitches at the top, so the Y coordinate
 * is inverted relative to MIDI pitch values.
 *
 * @param y - Y coordinate in pixels (world coordinates)
 * @returns PitchInfo with MIDI pitch and note name
 *
 * @example
 * yToPitch(0)   // { pitch: 127, noteName: "G9" } (top of piano roll)
 * yToPitch(520) // Lower pitch values
 */
export function yToPitch(y: number): PitchInfo {
  const pitchIndex = Math.floor(y / NOTE_HEIGHT);
  const pitch = TOTAL_NOTES - 1 - pitchIndex;
  const noteName = getMidiNoteName(pitch);

  return { pitch, noteName };
}

/**
 * Convert MIDI pitch to Y coordinate.
 *
 * @param pitch - MIDI pitch value (0-127)
 * @returns Y coordinate in pixels
 *
 * @example
 * pitchToY(60) // Y coordinate for middle C
 * pitchToY(127) // 0 (top of piano roll)
 */
export function pitchToY(pitch: number): number {
  return (TOTAL_NOTES - 1 - pitch) * NOTE_HEIGHT;
}

/**
 * Clamp a pitch value to valid MIDI range.
 *
 * @param pitch - Unclamped pitch value
 * @returns Pitch clamped to 0-127
 */
export function clampPitch(pitch: number): number {
  return Math.max(0, Math.min(127, pitch));
}

/**
 * Convert Y coordinate to clamped pitch.
 * Combines yToPitch and clampPitch for convenience.
 *
 * @param y - Y coordinate in pixels
 * @returns Clamped MIDI pitch value
 */
export function yToClampedPitch(y: number): number {
  const { pitch } = yToPitch(y);
  return clampPitch(pitch);
}

// ============================================================================
// Horizontal (Time) Coordinate Conversions
// ============================================================================

/**
 * Parse snap setting to get division value.
 *
 * @param snapSetting - Snap setting string (e.g., "1/4", "1/8", "none")
 * @returns Division value or 4 as default
 */
function parseSnapDivision(snapSetting: string): number {
  if (snapSetting === 'none') return 4;

  const [numerator, denominator] = snapSetting.split('/');
  if (numerator === '1' && denominator) {
    return parseInt(denominator, 10);
  }
  return 4;
}

/**
 * Convert X coordinate to measure, beat, and tick information.
 *
 * @param x - X coordinate in pixels (world coordinates)
 * @param config - Coordinate configuration
 * @returns MeasureInfo with position details
 *
 * @example
 * xToMeasureInfo(80, { pixelsPerBeat: 80, beatsPerMeasure: 4, snapSetting: '1/4' })
 * // { measure: 1, beat: 2, tick: 0, measureFraction: "2/4" }
 */
export function xToMeasureInfo(x: number, config: CoordinateConfig): MeasureInfo {
  const { pixelsPerBeat, beatsPerMeasure, snapSetting } = config;
  const pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;

  // Calculate measure (1-based)
  const measureIndex = Math.floor(x / pixelsPerMeasure);

  // Calculate beat within measure (1-based)
  const xWithinMeasure = x - measureIndex * pixelsPerMeasure;
  const beatWithinMeasure = Math.floor(xWithinMeasure / pixelsPerBeat);

  // Calculate tick within beat based on snap setting
  const ticksPerBeat = parseSnapDivision(snapSetting);
  const xWithinBeat = xWithinMeasure - beatWithinMeasure * pixelsPerBeat;
  const tickWithinBeat = Math.floor((xWithinBeat / pixelsPerBeat) * ticksPerBeat);

  return {
    measure: measureIndex + 1,
    beat: beatWithinMeasure + 1,
    tick: tickWithinBeat,
    measureFraction: `${beatWithinMeasure + 1}/${ticksPerBeat}`,
  };
}

/**
 * Convert measure, beat, tick to X coordinate.
 *
 * @param measure - 1-based measure number
 * @param beat - 1-based beat number within measure
 * @param tick - Tick within beat (0-based)
 * @param ticksPerBeat - Number of ticks per beat
 * @param config - Coordinate configuration (only needs pixelsPerBeat and beatsPerMeasure)
 * @returns X coordinate in pixels
 *
 * @example
 * measureInfoToX(1, 2, 0, 4, { pixelsPerBeat: 80, beatsPerMeasure: 4 })
 * // 80 (start of beat 2 in measure 1)
 */
export function measureInfoToX(
  measure: number,
  beat: number,
  tick: number,
  ticksPerBeat: number,
  config: Pick<CoordinateConfig, 'pixelsPerBeat' | 'beatsPerMeasure'>
): number {
  const { pixelsPerBeat, beatsPerMeasure } = config;
  const pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;

  // Convert to 0-based indices
  const measureIndex = measure - 1;
  const beatIndex = beat - 1;

  // Calculate x position
  const measureX = measureIndex * pixelsPerMeasure;
  const beatX = beatIndex * pixelsPerBeat;
  const tickX = (tick / ticksPerBeat) * pixelsPerBeat;

  return measureX + beatX + tickX;
}

/**
 * Convert beat position to pixel position.
 *
 * @param beat - Beat number (can be fractional)
 * @param pixelsPerBeat - Pixels per beat
 * @returns X coordinate in pixels
 */
export function beatToPixel(beat: number, pixelsPerBeat: number): number {
  return beat * pixelsPerBeat;
}

/**
 * Convert pixel position to beat number.
 *
 * @param x - X coordinate in pixels
 * @param pixelsPerBeat - Pixels per beat
 * @returns Beat number (can be fractional)
 */
export function pixelToBeat(x: number, pixelsPerBeat: number): number {
  return x / pixelsPerBeat;
}

// ============================================================================
// Mouse Position Utilities
// ============================================================================

/**
 * Combined mouse position information for display and interaction.
 */
export interface MousePositionInfo {
  /** Raw X coordinate */
  x: number;
  /** Raw Y coordinate */
  y: number;
  /** Measure number (1-based) */
  measure: number;
  /** Beat within measure (1-based) */
  beat: number;
  /** Tick within beat */
  tick: number;
  /** MIDI pitch value */
  pitch: number;
  /** Human-readable note name */
  noteName: string;
}

/**
 * Calculate complete mouse position information from coordinates.
 *
 * @param x - X coordinate in pixels (world coordinates)
 * @param y - Y coordinate in pixels (world coordinates)
 * @param config - Coordinate configuration
 * @returns Complete position info including musical position and pitch
 *
 * @example
 * getMousePositionInfo(160, 520, { pixelsPerBeat: 80, beatsPerMeasure: 4, snapSetting: '1/4' })
 * // { x: 160, y: 520, measure: 1, beat: 3, tick: 0, pitch: 60, noteName: "C4" }
 */
export function getMousePositionInfo(
  x: number,
  y: number,
  config: CoordinateConfig
): MousePositionInfo {
  const measureInfo = xToMeasureInfo(x, config);
  const pitchInfo = yToPitch(y);

  return {
    x,
    y,
    measure: measureInfo.measure,
    beat: measureInfo.beat,
    tick: measureInfo.tick,
    pitch: pitchInfo.pitch,
    noteName: pitchInfo.noteName,
  };
}

// ============================================================================
// Note Position Calculations
// ============================================================================

/**
 * Calculate the Y coordinate for a note's position on the piano roll.
 *
 * @param pitch - MIDI pitch value
 * @param verticalScroll - Current vertical scroll offset
 * @returns Screen Y coordinate for the note
 */
export function getNoteScreenY(pitch: number, verticalScroll: number): number {
  return pitchToY(pitch) - verticalScroll;
}

/**
 * Calculate pitch from mouse Y position during drag operations.
 * Used when moving notes vertically.
 *
 * @param y - World Y coordinate (includes scroll offset)
 * @param offsetY - Offset from initial click position to note position
 * @returns Clamped MIDI pitch value
 */
export function calculateDragPitch(y: number, offsetY: number): number {
  const newPitchY = y + offsetY;
  const newPitchIndex = Math.floor(newPitchY / NOTE_HEIGHT);
  const newPitch = TOTAL_NOTES - 1 - newPitchIndex;
  return clampPitch(newPitch);
}
