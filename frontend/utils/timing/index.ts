/**
 * Timing Utilities Barrel Export
 *
 * This module re-exports all timing-related utility modules.
 */

// Flicks timing utilities
export {
  FLICKS_PER_SECOND,
  secondsToFlicks,
  flicksToSeconds,
  beatsToFlicks,
  flicksToBeats,
  pixelsToFlicks,
  flicksToPixels,
  pixelsToBeats,
  beatsToPixels,
  noteDurationToFlicks,
  snapToFlicks,
  roundFlicks,
  formatFlicks,
  getExactNoteFlicks,
  pixelsToSeconds,
  secondsToPixels,
  pixelsToTicks,
  ticksToPixels,
  pixelsToSamples,
  samplesToPixels,
  calculateAllTimingData,
} from './flicks';

// Snap utilities
export {
  getSubdivisionsFromSnapSetting,
  getGridSizeFromSnap,
  getInitialNoteDuration,
  getMinimumNoteSize,
  snapToGrid,
  snapDurationToGrid,
  getSnapSubdivisions,
  getGridSizeFromSnap as snapUtilsGetGridSize,
} from './snapUtils';
