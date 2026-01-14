/**
 * Waveform Generator for Audio Visualization
 *
 * This module provides utilities for generating waveform data
 * from audio buffers for visualization purposes.
 */

import { createLogger } from '../logger';

const log = createLogger('WaveformGenerator');

/**
 * Waveform generation configuration.
 */
export interface WaveformConfig {
  /** Number of samples in the output waveform */
  sampleCount: number;
  /** Whether to use peak mode (max absolute) instead of RMS */
  usePeak: boolean;
  /** Style of waveform rendering */
  style: 'line' | 'bar' | 'mirror';
}

/**
 * Generated waveform data.
 */
export interface WaveformData {
  /** Waveform amplitude values (normalized 0-1) */
  data: Float32Array;
  /** Number of samples used to generate each point */
  samplesPerPoint: number;
  /** Total duration in seconds */
  duration: number;
  /** Sample rate of source audio */
  sampleRate: number;
}

/**
 * WaveformGenerator class
 *
 * Generates optimized waveform data from audio buffers for
 * efficient visualization.
 */
export class WaveformGenerator {
  private config: WaveformConfig;

  constructor(config?: Partial<WaveformConfig>) {
    this.config = {
      sampleCount: 1000,
      usePeak: false,
      style: 'line',
      ...config,
    };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<WaveformConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Generate waveform data from an audio buffer.
   */
  generate(audioBuffer: AudioBuffer): WaveformData {
    const channelData = audioBuffer.getChannelData(0);
    const totalSamples = channelData.length;
    const samplesPerPoint = Math.floor(totalSamples / this.config.sampleCount);
    const data = new Float32Array(this.config.sampleCount);

    for (let i = 0; i < this.config.sampleCount; i++) {
      const start = i * samplesPerPoint;
      const end = Math.min(start + samplesPerPoint, totalSamples);

      if (this.config.usePeak) {
        // Peak mode: use maximum absolute value
        let max = 0;
        for (let j = start; j < end; j++) {
          const abs = Math.abs(channelData[j]);
          if (abs > max) max = abs;
        }
        data[i] = max;
      } else {
        // RMS mode: root mean square
        let sum = 0;
        let count = 0;
        for (let j = start; j < end; j++) {
          sum += channelData[j] * channelData[j];
          count++;
        }
        data[i] = Math.sqrt(sum / count);
      }
    }

    log.debug('Generated waveform data', {
      sampleCount: this.config.sampleCount,
      samplesPerPoint,
      duration: audioBuffer.duration,
    });

    return {
      data,
      samplesPerPoint,
      duration: audioBuffer.duration,
      sampleRate: audioBuffer.sampleRate,
    };
  }

  /**
   * Generate symmetric waveform for mirror-style display.
   */
  generateMirror(audioBuffer: AudioBuffer): { positive: Float32Array; negative: Float32Array } {
    const waveform = this.generate(audioBuffer);
    const negative = new Float32Array(waveform.data.length);

    for (let i = 0; i < waveform.data.length; i++) {
      negative[i] = -waveform.data[i];
    }

    return { positive: waveform.data, negative };
  }

  /**
   * Generate bar-style waveform data.
   */
  generateBars(audioBuffer: AudioBuffer, barWidth: number = 2): Float32Array {
    const channelData = audioBuffer.getChannelData(0);
    const totalSamples = channelData.length;
    const barsCount = Math.floor(totalSamples / barWidth);
    const data = new Float32Array(barsCount);

    for (let i = 0; i < barsCount; i++) {
      const start = i * barWidth;
      const end = start + barWidth;
      let max = 0;

      for (let j = start; j < end; j++) {
        const abs = Math.abs(channelData[j]);
        if (abs > max) max = abs;
      }

      data[i] = max;
    }

    return data;
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    // No persistent resources to clean up
  }
}

/**
 * Create a waveform generator instance.
 */
export function createWaveformGenerator(config?: Partial<WaveformConfig>): WaveformGenerator {
  return new WaveformGenerator(config);
}
