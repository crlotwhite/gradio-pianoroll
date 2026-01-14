/**
 * Coordinate Utilities Barrel Export
 *
 * This module re-exports all coordinate-related utility modules.
 */

// Coordinate conversion utilities
export {
  xToMeasureInfo,
  measureInfoToX,
  yToPitch,
  pitchToY,
  getMidiNoteName,
  beatToPixel,
  pixelToBeat,
  getMousePositionInfo,
  clampPitch,
  calculateDragPitch,
  yToClampedPitch,
  getNoteScreenY,
} from './coordinateUtils';

// Keyboard-related utilities
export {
  getKeyboardLayout,
  getKeyForPitch,
  getPitchForKey,
  isBlackKey,
  getKeyColor,
  getKeyboardWidth,
  KEYBOARD_LAYOUT,
} from './keyboardUtils';
