/**
 * Utility functions index
 * Re-exports all utility functions for easy importing
 */

// Backend data management
export {
  BackendDataManager,
  extractBackendData,
  mergeBackendData,
  validateCurveData,
  validateSegmentData
} from './backend-data';

// Timing calculations
export {
  generateNoteId,
  pixelsToFlicks,
  pixelsToSeconds,
  pixelsToBeats,
  pixelsToTicks,
  pixelsToSamples,
  calculateAllTimingData,
  createNoteWithTiming,
  updateNoteTiming,
  updateNotesTiming,
  validateNote,
  createTimingContext,
  formatTimingContext,
  secondsToPixels,
  beatsToPixels,
  ticksToPixels,
  samplesToPixels
} from './timing'; 