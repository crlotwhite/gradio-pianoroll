/**
 * Unit tests for snapUtils module.
 *
 * Tests cover:
 * - parseSnapSetting: Parse snap setting strings
 * - getGridSizeFromSnap: Calculate grid size in pixels
 * - snapToGrid: Snap values to grid
 * - getInitialNoteDuration: Get default note duration
 * - getMinimumNoteSize: Get minimum note size
 * - snapDurationToGrid: Snap duration values to grid
 * - getSubdivisionsFromSnapSetting: Get subdivision info for grid rendering
 */

import { describe, it, expect } from 'vitest';
import {
  parseSnapSetting,
  getGridSizeFromSnap,
  snapToGrid,
  getInitialNoteDuration,
  getMinimumNoteSize,
  snapDurationToGrid,
  getSubdivisionsFromSnapSetting,
} from '../../frontend/utils/snapUtils';

// =============================================================================
// Tests for parseSnapSetting
// =============================================================================

describe('parseSnapSetting', () => {
  it('should return null for "none"', () => {
    expect(parseSnapSetting('none')).toBeNull();
  });

  it('should parse "1/4" as 4', () => {
    expect(parseSnapSetting('1/4')).toBe(4);
  });

  it('should parse "1/8" as 8', () => {
    expect(parseSnapSetting('1/8')).toBe(8);
  });

  it('should parse "1/16" as 16', () => {
    expect(parseSnapSetting('1/16')).toBe(16);
  });

  it('should parse "1/32" as 32', () => {
    expect(parseSnapSetting('1/32')).toBe(32);
  });

  it('should parse "1/1" as 1 (whole note)', () => {
    expect(parseSnapSetting('1/1')).toBe(1);
  });

  it('should parse "1/2" as 2 (half note)', () => {
    expect(parseSnapSetting('1/2')).toBe(2);
  });

  it('should return null for invalid format', () => {
    expect(parseSnapSetting('invalid')).toBeNull();
    expect(parseSnapSetting('2/4')).toBeNull();
    expect(parseSnapSetting('')).toBeNull();
  });
});

// =============================================================================
// Tests for getGridSizeFromSnap
// =============================================================================

describe('getGridSizeFromSnap', () => {
  const pixelsPerBeat = 80;

  it('should return 1 pixel for "none" (fine control)', () => {
    const result = getGridSizeFromSnap('none', pixelsPerBeat);
    // For "none", returns pixelsPerBeat / FINE_CONTROL_DIVISION
    expect(result).toBeLessThan(pixelsPerBeat);
  });

  it('should return correct size for quarter note (1/4)', () => {
    // 1/4 note = 1 beat = pixelsPerBeat
    expect(getGridSizeFromSnap('1/4', pixelsPerBeat)).toBe(80);
  });

  it('should return correct size for eighth note (1/8)', () => {
    // 1/8 note = 0.5 beat = pixelsPerBeat * 0.5
    expect(getGridSizeFromSnap('1/8', pixelsPerBeat)).toBe(40);
  });

  it('should return correct size for sixteenth note (1/16)', () => {
    // 1/16 note = 0.25 beat = pixelsPerBeat * 0.25
    expect(getGridSizeFromSnap('1/16', pixelsPerBeat)).toBe(20);
  });

  it('should return correct size for whole note (1/1)', () => {
    // 1/1 note = 4 beats = pixelsPerBeat * 4
    expect(getGridSizeFromSnap('1/1', pixelsPerBeat)).toBe(320);
  });

  it('should return correct size for half note (1/2)', () => {
    // 1/2 note = 2 beats = pixelsPerBeat * 2
    expect(getGridSizeFromSnap('1/2', pixelsPerBeat)).toBe(160);
  });

  it('should scale with different pixelsPerBeat values', () => {
    expect(getGridSizeFromSnap('1/4', 40)).toBe(40);
    expect(getGridSizeFromSnap('1/4', 160)).toBe(160);
    expect(getGridSizeFromSnap('1/8', 160)).toBe(80);
  });
});

// =============================================================================
// Tests for snapToGrid
// =============================================================================

describe('snapToGrid', () => {
  const pixelsPerBeat = 80;

  it('should snap value to nearest grid position for quarter notes', () => {
    expect(snapToGrid(0, '1/4', pixelsPerBeat)).toBe(0);
    expect(snapToGrid(39, '1/4', pixelsPerBeat)).toBe(0);
    expect(snapToGrid(40, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapToGrid(79, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapToGrid(80, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapToGrid(120, '1/4', pixelsPerBeat)).toBe(160);
  });

  it('should work with eighth note snap', () => {
    expect(snapToGrid(0, '1/8', pixelsPerBeat)).toBe(0);
    expect(snapToGrid(19, '1/8', pixelsPerBeat)).toBe(0);
    expect(snapToGrid(20, '1/8', pixelsPerBeat)).toBe(40);
    expect(snapToGrid(50, '1/8', pixelsPerBeat)).toBe(40);
    expect(snapToGrid(60, '1/8', pixelsPerBeat)).toBe(80);
  });

  it('should return original value when snap is "none"', () => {
    expect(snapToGrid(45, 'none', pixelsPerBeat)).toBe(45);
    expect(snapToGrid(123, 'none', pixelsPerBeat)).toBe(123);
  });

  it('should handle negative values', () => {
    // Note: Math.round(-0.5) returns -0 in JavaScript
    // -40/80 = -0.5, Math.round(-0.5) = -0, -0 * 80 = -0
    // We check the value is functionally zero
    const result = snapToGrid(-40, '1/4', pixelsPerBeat);
    expect(result === 0 || Object.is(result, -0)).toBe(true);
    expect(snapToGrid(-41, '1/4', pixelsPerBeat)).toBe(-80);
    expect(snapToGrid(-80, '1/4', pixelsPerBeat)).toBe(-80);
  });
});

// =============================================================================
// Tests for getInitialNoteDuration
// =============================================================================

describe('getInitialNoteDuration', () => {
  const pixelsPerBeat = 80;

  it('should return grid size for snap settings', () => {
    expect(getInitialNoteDuration('1/4', pixelsPerBeat)).toBe(80);
    expect(getInitialNoteDuration('1/8', pixelsPerBeat)).toBe(40);
    expect(getInitialNoteDuration('1/16', pixelsPerBeat)).toBe(20);
  });

  it('should return small default for "none"', () => {
    const result = getInitialNoteDuration('none', pixelsPerBeat);
    expect(result).toBe(pixelsPerBeat / 8);
  });
});

// =============================================================================
// Tests for getMinimumNoteSize
// =============================================================================

describe('getMinimumNoteSize', () => {
  const pixelsPerBeat = 80;

  it('should return half of grid size', () => {
    expect(getMinimumNoteSize('1/4', pixelsPerBeat)).toBe(40);
    expect(getMinimumNoteSize('1/8', pixelsPerBeat)).toBe(20);
  });

  it('should return fine control size for "none"', () => {
    const result = getMinimumNoteSize('none', pixelsPerBeat);
    expect(result).toBeLessThan(pixelsPerBeat);
    expect(result).toBeGreaterThan(0);
  });
});

// =============================================================================
// Tests for snapDurationToGrid
// =============================================================================

describe('snapDurationToGrid', () => {
  const pixelsPerBeat = 80;

  it('should snap duration to grid', () => {
    expect(snapDurationToGrid(50, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapDurationToGrid(100, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapDurationToGrid(140, '1/4', pixelsPerBeat)).toBe(160);
  });

  it('should enforce minimum size of one grid unit', () => {
    expect(snapDurationToGrid(10, '1/4', pixelsPerBeat)).toBe(80);
    expect(snapDurationToGrid(1, '1/8', pixelsPerBeat)).toBe(40);
  });
});

// =============================================================================
// Tests for getSubdivisionsFromSnapSetting
// =============================================================================

describe('getSubdivisionsFromSnapSetting', () => {
  const pixelsPerBeat = 80;

  it('should return correct subdivisions for quarter notes', () => {
    const result = getSubdivisionsFromSnapSetting('1/4', pixelsPerBeat);
    expect(result.count).toBe(1);
    expect(result.pixelsPerSubdivision).toBe(80);
  });

  it('should return correct subdivisions for eighth notes', () => {
    const result = getSubdivisionsFromSnapSetting('1/8', pixelsPerBeat);
    expect(result.count).toBe(2);
    expect(result.pixelsPerSubdivision).toBe(40);
  });

  it('should return correct subdivisions for sixteenth notes', () => {
    const result = getSubdivisionsFromSnapSetting('1/16', pixelsPerBeat);
    expect(result.count).toBe(4);
    expect(result.pixelsPerSubdivision).toBe(20);
  });

  it('should return default for "none"', () => {
    const result = getSubdivisionsFromSnapSetting('none', pixelsPerBeat);
    expect(result.count).toBe(1);
    expect(result.pixelsPerSubdivision).toBe(pixelsPerBeat);
  });
});
