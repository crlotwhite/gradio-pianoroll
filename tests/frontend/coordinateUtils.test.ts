/**
 * Unit tests for coordinateUtils
 */
import { describe, it, expect } from 'vitest';
import {
  getMidiNoteName,
  yToPitch,
  pitchToY,
  clampPitch,
  yToClampedPitch,
  xToMeasureInfo,
  measureInfoToX,
  beatToPixel,
  pixelToBeat,
  getMousePositionInfo,
  calculateDragPitch,
  type CoordinateConfig,
} from '../../frontend/utils/coordinateUtils';

describe('coordinateUtils', () => {
  // Test configuration
  const config: CoordinateConfig = {
    pixelsPerBeat: 80,
    beatsPerMeasure: 4,
    snapSetting: '1/4',
  };

  describe('getMidiNoteName', () => {
    it('should return correct note name for middle C (60)', () => {
      expect(getMidiNoteName(60)).toBe('C4');
    });

    it('should return correct note name for A4 (69)', () => {
      expect(getMidiNoteName(69)).toBe('A4');
    });

    it('should handle sharps correctly', () => {
      expect(getMidiNoteName(61)).toBe('C#4');
      expect(getMidiNoteName(66)).toBe('F#4');
    });

    it('should handle octave boundaries', () => {
      expect(getMidiNoteName(0)).toBe('C-1');
      expect(getMidiNoteName(12)).toBe('C0');
      expect(getMidiNoteName(127)).toBe('G9');
    });
  });

  describe('yToPitch / pitchToY', () => {
    it('should be inverse operations', () => {
      for (let pitch = 0; pitch <= 127; pitch++) {
        const y = pitchToY(pitch);
        const result = yToPitch(y);
        expect(result.pitch).toBe(pitch);
      }
    });

    it('should return correct note names', () => {
      const y = pitchToY(60);
      const result = yToPitch(y);
      expect(result.noteName).toBe('C4');
    });

    it('should handle top of piano roll (high pitch)', () => {
      // Pitch 127 should be at Y = 0
      expect(pitchToY(127)).toBe(0);
    });
  });

  describe('clampPitch', () => {
    it('should clamp values below 0', () => {
      expect(clampPitch(-5)).toBe(0);
      expect(clampPitch(-100)).toBe(0);
    });

    it('should clamp values above 127', () => {
      expect(clampPitch(128)).toBe(127);
      expect(clampPitch(200)).toBe(127);
    });

    it('should not modify values in valid range', () => {
      expect(clampPitch(0)).toBe(0);
      expect(clampPitch(60)).toBe(60);
      expect(clampPitch(127)).toBe(127);
    });
  });

  describe('yToClampedPitch', () => {
    it('should return clamped pitch from Y coordinate', () => {
      const y = pitchToY(60);
      expect(yToClampedPitch(y)).toBe(60);
    });

    it('should clamp extreme Y values', () => {
      // Very negative Y (beyond top) should clamp to 127
      expect(yToClampedPitch(-1000)).toBe(127);
    });
  });

  describe('xToMeasureInfo', () => {
    it('should correctly identify first beat of first measure', () => {
      const result = xToMeasureInfo(0, config);
      expect(result.measure).toBe(1);
      expect(result.beat).toBe(1);
      expect(result.tick).toBe(0);
    });

    it('should correctly identify second beat', () => {
      const result = xToMeasureInfo(80, config);
      expect(result.measure).toBe(1);
      expect(result.beat).toBe(2);
      expect(result.tick).toBe(0);
    });

    it('should correctly identify second measure', () => {
      const result = xToMeasureInfo(320, config); // 4 beats * 80 pixels
      expect(result.measure).toBe(2);
      expect(result.beat).toBe(1);
    });

    it('should correctly calculate ticks within beat', () => {
      // At 1/4 snap, 4 ticks per beat
      const result = xToMeasureInfo(40, config); // Half a beat
      expect(result.tick).toBe(2); // 2 out of 4 ticks
    });

    it('should include measure fraction', () => {
      const result = xToMeasureInfo(0, config);
      expect(result.measureFraction).toBe('1/4');
    });
  });

  describe('measureInfoToX', () => {
    it('should convert first beat of first measure to 0', () => {
      const x = measureInfoToX(1, 1, 0, 4, config);
      expect(x).toBe(0);
    });

    it('should convert second beat to correct position', () => {
      const x = measureInfoToX(1, 2, 0, 4, config);
      expect(x).toBe(80);
    });

    it('should handle ticks correctly', () => {
      const x = measureInfoToX(1, 1, 2, 4, config);
      expect(x).toBe(40); // Half a beat
    });

    it('should be inverse of xToMeasureInfo', () => {
      const x = 200;
      const info = xToMeasureInfo(x, config);
      const backToX = measureInfoToX(info.measure, info.beat, info.tick, 4, config);
      // Should be approximately equal (may have rounding)
      expect(Math.abs(backToX - x)).toBeLessThan(1);
    });
  });

  describe('beatToPixel / pixelToBeat', () => {
    it('should convert beats to pixels correctly', () => {
      expect(beatToPixel(1, 80)).toBe(80);
      expect(beatToPixel(2.5, 80)).toBe(200);
      expect(beatToPixel(0, 80)).toBe(0);
    });

    it('should convert pixels to beats correctly', () => {
      expect(pixelToBeat(80, 80)).toBe(1);
      expect(pixelToBeat(200, 80)).toBe(2.5);
      expect(pixelToBeat(0, 80)).toBe(0);
    });

    it('should be inverse operations', () => {
      const beat = 3.75;
      const pixels = beatToPixel(beat, 80);
      const backToBeat = pixelToBeat(pixels, 80);
      expect(backToBeat).toBe(beat);
    });
  });

  describe('getMousePositionInfo', () => {
    it('should return complete position information', () => {
      const result = getMousePositionInfo(160, pitchToY(60), config);

      expect(result.x).toBe(160);
      expect(result.measure).toBe(1);
      expect(result.beat).toBe(3); // 160 / 80 = 2 full beats, so beat 3
      expect(result.pitch).toBe(60);
      expect(result.noteName).toBe('C4');
    });

    it('should handle origin correctly', () => {
      const result = getMousePositionInfo(0, pitchToY(127), config);

      expect(result.measure).toBe(1);
      expect(result.beat).toBe(1);
      expect(result.tick).toBe(0);
      expect(result.pitch).toBe(127);
    });
  });

  describe('calculateDragPitch', () => {
    it('should calculate pitch from drag position', () => {
      const startPitch = 60;
      const startY = pitchToY(startPitch);
      const offsetY = 0; // No offset

      const result = calculateDragPitch(startY, offsetY);
      expect(result).toBe(startPitch);
    });

    it('should handle offset correctly', () => {
      // Simulate clicking slightly off from note position
      const targetPitch = 60;
      const y = pitchToY(targetPitch);
      const offset = 5; // 5 pixels offset

      // The offset simulates the difference between click position and note position
      const result = calculateDragPitch(y - offset, offset);
      expect(result).toBe(targetPitch);
    });

    it('should clamp result to valid range', () => {
      // Very large Y value should clamp to 0
      const result = calculateDragPitch(10000, 0);
      expect(result).toBe(0);

      // Very negative Y value should clamp to 127
      const resultHigh = calculateDragPitch(-1000, 0);
      expect(resultHigh).toBe(127);
    });
  });

  describe('edge cases', () => {
    it('should handle snap setting "none"', () => {
      const noneConfig: CoordinateConfig = {
        ...config,
        snapSetting: 'none',
      };
      const result = xToMeasureInfo(100, noneConfig);
      expect(result.measure).toBe(1);
      expect(result.beat).toBe(2);
    });

    it('should handle different time signatures', () => {
      const threeQuarterConfig: CoordinateConfig = {
        pixelsPerBeat: 80,
        beatsPerMeasure: 3,
        snapSetting: '1/4',
      };
      // Second measure starts at 3 beats = 240 pixels
      const result = xToMeasureInfo(240, threeQuarterConfig);
      expect(result.measure).toBe(2);
      expect(result.beat).toBe(1);
    });

    it('should handle different pixelsPerBeat values', () => {
      const zoomedConfig: CoordinateConfig = {
        pixelsPerBeat: 160,
        beatsPerMeasure: 4,
        snapSetting: '1/4',
      };
      const result = xToMeasureInfo(160, zoomedConfig);
      expect(result.measure).toBe(1);
      expect(result.beat).toBe(2);
    });
  });
});
