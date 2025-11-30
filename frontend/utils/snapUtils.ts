/**
 * Snap and grid utility functions for the piano roll.
 * Consolidates repeated snap calculation logic into reusable functions.
 */

import { FINE_CONTROL_DIVISION } from './constants';

/**
 * Snap setting division values and their corresponding beat multipliers.
 * Maps the denominator of a snap setting (e.g., "1/8" -> 8) to the
 * number of beats that division represents.
 */
const SNAP_DIVISION_TO_BEATS: Record<number, number> = {
  1: 4,    // Whole note = 4 beats
  2: 2,    // Half note = 2 beats
  4: 1,    // Quarter note = 1 beat
  8: 0.5,  // Eighth note = 0.5 beat
  16: 0.25, // Sixteenth note = 0.25 beat
  32: 0.125, // Thirty-second note = 0.125 beat
};

/**
 * Parse a snap setting string (e.g., "1/8") and return the division value.
 * @param snapSetting - The snap setting string (e.g., "1/4", "1/8", "none")
 * @returns The division value (e.g., 4 for "1/4", 8 for "1/8") or null for "none"
 */
export function parseSnapSetting(snapSetting: string): number | null {
  if (snapSetting === 'none') {
    return null;
  }

  const parts = snapSetting.split('/');
  if (parts.length === 2 && parts[0] === '1') {
    const divisionValue = parseInt(parts[1], 10);
    if (!isNaN(divisionValue) && divisionValue in SNAP_DIVISION_TO_BEATS) {
      return divisionValue;
    }
  }

  return null;
}

/**
 * Get the grid size in pixels based on snap setting.
 * This is the main function to calculate how many pixels correspond to one grid unit.
 *
 * @param snapSetting - The snap setting string (e.g., "1/4", "1/8", "none")
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns Grid size in pixels
 *
 * @example
 * // Quarter note at 80 pixels per beat
 * getGridSizeFromSnap("1/4", 80) // returns 80
 *
 * // Eighth note at 80 pixels per beat
 * getGridSizeFromSnap("1/8", 80) // returns 40
 */
export function getGridSizeFromSnap(snapSetting: string, pixelsPerBeat: number): number {
  const divisionValue = parseSnapSetting(snapSetting);

  if (divisionValue === null) {
    // When snap is off, use very fine control
    return pixelsPerBeat / FINE_CONTROL_DIVISION;
  }

  const beatsPerDivision = SNAP_DIVISION_TO_BEATS[divisionValue] ?? 1;
  return pixelsPerBeat * beatsPerDivision;
}

/**
 * Get the initial duration for a new note based on snap setting.
 * Same as grid size but with different semantics (duration vs position).
 *
 * @param snapSetting - The snap setting string
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns Initial note duration in pixels
 */
export function getInitialNoteDuration(snapSetting: string, pixelsPerBeat: number): number {
  if (snapSetting === 'none') {
    // When snap is off, use a small default size
    return pixelsPerBeat / 8;
  }
  return getGridSizeFromSnap(snapSetting, pixelsPerBeat);
}

/**
 * Get the minimum note size based on snap setting.
 * This is typically half of the grid size to allow for some flexibility.
 *
 * @param snapSetting - The snap setting string
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns Minimum note size in pixels
 */
export function getMinimumNoteSize(snapSetting: string, pixelsPerBeat: number): number {
  if (snapSetting === 'none') {
    return pixelsPerBeat / FINE_CONTROL_DIVISION;
  }
  return getGridSizeFromSnap(snapSetting, pixelsPerBeat) / 2;
}

/**
 * Snap a value to the nearest grid position.
 *
 * @param value - The value to snap (in pixels)
 * @param snapSetting - The snap setting string
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns The snapped value in pixels
 *
 * @example
 * snapToGrid(45, "1/4", 80) // returns 40 (nearest quarter note)
 * snapToGrid(45, "1/8", 80) // returns 40 (nearest eighth note)
 * snapToGrid(45, "none", 80) // returns 45 (no snapping, returns original value)
 */
export function snapToGrid(value: number, snapSetting: string, pixelsPerBeat: number): number {
  if (snapSetting === 'none') {
    return value;
  }

  const gridSize = getGridSizeFromSnap(snapSetting, pixelsPerBeat);
  return Math.round(value / gridSize) * gridSize;
}

/**
 * Snap a duration (width) to the grid, ensuring minimum size.
 *
 * @param duration - The duration to snap (in pixels)
 * @param snapSetting - The snap setting string
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns The snapped duration in pixels (at least one grid unit)
 */
export function snapDurationToGrid(
  duration: number,
  snapSetting: string,
  pixelsPerBeat: number
): number {
  const gridSize = getGridSizeFromSnap(snapSetting, pixelsPerBeat);

  if (snapSetting === 'none') {
    return Math.max(gridSize, duration);
  }

  const snappedDuration = Math.round(duration / gridSize) * gridSize;
  return Math.max(gridSize, snappedDuration);
}

/**
 * Get subdivisions info for grid rendering based on snap setting.
 * Returns the count and pixel size of subdivisions within a beat.
 *
 * @param snapSetting - The snap setting string
 * @param pixelsPerBeat - Current zoom level in pixels per beat
 * @returns Object with count and pixelsPerSubdivision
 */
export function getSubdivisionsFromSnapSetting(
  snapSetting: string,
  pixelsPerBeat: number
): { count: number; pixelsPerSubdivision: number } {
  const divisionValue = parseSnapSetting(snapSetting);

  if (divisionValue === null) {
    // Default to quarter note subdivisions if snap is 'none'
    return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
  }

  switch (divisionValue) {
    case 1: // Whole note - 4 beats
      return { count: 1, pixelsPerSubdivision: pixelsPerBeat * 4 };
    case 2: // Half note - 2 beats
      return { count: 1, pixelsPerSubdivision: pixelsPerBeat * 2 };
    case 4: // Quarter note - 1 beat
      return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
    case 8: // Eighth note - 0.5 beat
      return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
    case 16: // Sixteenth note - 0.25 beat
      return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
    case 32: // Thirty-second note - 0.125 beat
      return { count: 8, pixelsPerSubdivision: pixelsPerBeat / 8 };
    default:
      return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
  }
}
