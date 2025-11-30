/**
 * Unit tests for flicks utility module.
 *
 * Tests cover:
 * - FLICKS_PER_SECOND constant
 * - secondsToFlicks: Convert seconds to flicks
 * - flicksToSeconds: Convert flicks to seconds
 * - beatsToFlicks: Convert beats to flicks (tempo-dependent)
 * - flicksToBeats: Convert flicks to beats (tempo-dependent)
 * - pixelsToFlicks: Convert pixels to flicks
 * - flicksToPixels: Convert flicks to pixels
 * - pixelsToBeats: Convert pixels to beats
 * - beatsToPixels: Convert beats to pixels
 * - noteDurationToFlicks: Convert note duration to flicks
 */

import { describe, it, expect } from 'vitest';
import {
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
} from '../../frontend/utils/flicks';

// =============================================================================
// Constants
// =============================================================================

describe('FLICKS_PER_SECOND constant', () => {
  it('should be 705600000', () => {
    expect(FLICKS_PER_SECOND).toBe(705600000);
  });
});

// =============================================================================
// Tests for secondsToFlicks
// =============================================================================

describe('secondsToFlicks', () => {
  it('should return 0 for 0 seconds', () => {
    expect(secondsToFlicks(0)).toBe(0);
  });

  it('should return FLICKS_PER_SECOND for 1 second', () => {
    expect(secondsToFlicks(1)).toBe(FLICKS_PER_SECOND);
  });

  it('should return half FLICKS_PER_SECOND for 0.5 seconds', () => {
    expect(secondsToFlicks(0.5)).toBe(FLICKS_PER_SECOND / 2);
  });

  it('should handle small fractions', () => {
    const result = secondsToFlicks(0.001); // 1 millisecond
    expect(result).toBe(FLICKS_PER_SECOND / 1000);
  });
});

// =============================================================================
// Tests for flicksToSeconds
// =============================================================================

describe('flicksToSeconds', () => {
  it('should return 0 for 0 flicks', () => {
    expect(flicksToSeconds(0)).toBe(0);
  });

  it('should return 1 second for FLICKS_PER_SECOND flicks', () => {
    expect(flicksToSeconds(FLICKS_PER_SECOND)).toBe(1);
  });

  it('should be inverse of secondsToFlicks', () => {
    const seconds = 2.5;
    const flicks = secondsToFlicks(seconds);
    expect(flicksToSeconds(flicks)).toBeCloseTo(seconds, 10);
  });
});

// =============================================================================
// Tests for beatsToFlicks
// =============================================================================

describe('beatsToFlicks', () => {
  it('should return 0 for 0 beats', () => {
    expect(beatsToFlicks(0, 120)).toBe(0);
  });

  it('should return correct flicks for 1 beat at 60 BPM (1 second)', () => {
    // At 60 BPM, 1 beat = 1 second
    const result = beatsToFlicks(1, 60);
    expect(result).toBeCloseTo(FLICKS_PER_SECOND, 0);
  });

  it('should return correct flicks for 1 beat at 120 BPM (0.5 seconds)', () => {
    // At 120 BPM, 1 beat = 0.5 seconds
    const result = beatsToFlicks(1, 120);
    expect(result).toBeCloseTo(FLICKS_PER_SECOND / 2, 0);
  });

  it('should scale linearly with beats', () => {
    const tempo = 120;
    const onebeat = beatsToFlicks(1, tempo);
    const fourBeats = beatsToFlicks(4, tempo);
    expect(fourBeats).toBeCloseTo(onebeat * 4, 0);
  });

  it('should scale inversely with tempo', () => {
    const beats = 2;
    const at60 = beatsToFlicks(beats, 60);
    const at120 = beatsToFlicks(beats, 120);
    expect(at60).toBeCloseTo(at120 * 2, 0);
  });
});

// =============================================================================
// Tests for flicksToBeats
// =============================================================================

describe('flicksToBeats', () => {
  it('should return 0 for 0 flicks', () => {
    expect(flicksToBeats(0, 120)).toBe(0);
  });

  it('should be inverse of beatsToFlicks', () => {
    const beats = 3.5;
    const tempo = 90;
    const flicks = beatsToFlicks(beats, tempo);
    expect(flicksToBeats(flicks, tempo)).toBeCloseTo(beats, 10);
  });

  it('should return 1 beat for half-second flicks at 120 BPM', () => {
    const halfSecondFlicks = FLICKS_PER_SECOND / 2;
    const result = flicksToBeats(halfSecondFlicks, 120);
    expect(result).toBeCloseTo(1, 10);
  });
});

// =============================================================================
// Tests for pixelsToFlicks
// =============================================================================

describe('pixelsToFlicks', () => {
  it('should return 0 for 0 pixels', () => {
    expect(pixelsToFlicks(0, 80, 120)).toBe(0);
  });

  it('should return correct flicks for 1 beat worth of pixels', () => {
    const pixelsPerBeat = 80;
    const tempo = 120;
    const pixels = 80; // 1 beat

    const result = pixelsToFlicks(pixels, pixelsPerBeat, tempo);
    const expected = beatsToFlicks(1, tempo);

    expect(result).toBeCloseTo(expected, 0);
  });

  it('should scale with zoom level', () => {
    const tempo = 120;

    // At pixelsPerBeat = 80, 80 pixels = 1 beat
    const at80 = pixelsToFlicks(80, 80, tempo);

    // At pixelsPerBeat = 160, 80 pixels = 0.5 beats
    const at160 = pixelsToFlicks(80, 160, tempo);

    expect(at80).toBeCloseTo(at160 * 2, 0);
  });
});

// =============================================================================
// Tests for flicksToPixels
// =============================================================================

describe('flicksToPixels', () => {
  it('should return 0 for 0 flicks', () => {
    expect(flicksToPixels(0, 80, 120)).toBe(0);
  });

  it('should be inverse of pixelsToFlicks', () => {
    const pixels = 160;
    const pixelsPerBeat = 80;
    const tempo = 120;

    const flicks = pixelsToFlicks(pixels, pixelsPerBeat, tempo);
    const result = flicksToPixels(flicks, pixelsPerBeat, tempo);

    expect(result).toBeCloseTo(pixels, 10);
  });
});

// =============================================================================
// Tests for pixelsToBeats
// =============================================================================

describe('pixelsToBeats', () => {
  it('should return 0 for 0 pixels', () => {
    expect(pixelsToBeats(0, 80)).toBe(0);
  });

  it('should return 1 for pixelsPerBeat pixels', () => {
    expect(pixelsToBeats(80, 80)).toBe(1);
  });

  it('should return correct fractional beats', () => {
    expect(pixelsToBeats(40, 80)).toBe(0.5);
    expect(pixelsToBeats(20, 80)).toBe(0.25);
  });

  it('should scale with zoom level', () => {
    // Same pixels, different zoom = different beats
    expect(pixelsToBeats(80, 40)).toBe(2);
    expect(pixelsToBeats(80, 160)).toBe(0.5);
  });
});

// =============================================================================
// Tests for beatsToPixels
// =============================================================================

describe('beatsToPixels', () => {
  it('should return 0 for 0 beats', () => {
    expect(beatsToPixels(0, 80)).toBe(0);
  });

  it('should return pixelsPerBeat for 1 beat', () => {
    expect(beatsToPixels(1, 80)).toBe(80);
  });

  it('should be inverse of pixelsToBeats', () => {
    const beats = 3.5;
    const pixelsPerBeat = 80;

    const pixels = beatsToPixels(beats, pixelsPerBeat);
    const result = pixelsToBeats(pixels, pixelsPerBeat);

    expect(result).toBeCloseTo(beats, 10);
  });
});

// =============================================================================
// Tests for noteDurationToFlicks
// =============================================================================

describe('noteDurationToFlicks', () => {
  it('should return 0 for 0 duration', () => {
    expect(noteDurationToFlicks(0, 120)).toBe(0);
  });

  it('should be equivalent to beatsToFlicks', () => {
    const duration = 2;
    const tempo = 120;

    const result = noteDurationToFlicks(duration, tempo);
    const expected = beatsToFlicks(duration, tempo);

    expect(result).toBeCloseTo(expected, 0);
  });

  it('should correctly calculate quarter note at 120 BPM', () => {
    // Quarter note = 1 beat = 0.5 seconds at 120 BPM
    const result = noteDurationToFlicks(1, 120);
    const expected = FLICKS_PER_SECOND / 2;

    expect(result).toBeCloseTo(expected, 0);
  });
});
