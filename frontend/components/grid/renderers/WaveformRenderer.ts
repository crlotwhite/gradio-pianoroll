/**
 * Waveform Renderer for Piano Roll
 *
 * This module handles rendering of audio waveform visualization.
 */

import { createLogger } from '../../../utils/logger';
import type { LayerRenderContext } from '../../../types';
import { flicksToPixels } from '../../../utils/flicks';

const log = createLogger('WaveformRenderer');

/**
 * Waveform renderer configuration.
 */
export interface WaveformRendererConfig {
  /** Waveform color */
  color: string;
  /** Waveform line width */
  lineWidth: number;
  /** Waveform opacity */
  opacity: number;
  /** Waveform padding from top */
  paddingTop: number;
  /** Waveform height */
  height: number;
  /** Amplitude multiplier */
  amplitudeMultiplier: number;
}

/**
 * Default waveform renderer configuration.
 */
const DEFAULT_CONFIG: WaveformRendererConfig = {
  color: '#4a9eff',
  lineWidth: 1.5,
  opacity: 0.8,
  paddingTop: 10,
  height: 60,
  amplitudeMultiplier: 1.0,
};

/**
 * WaveformRenderer class
 *
 * Renders audio waveform visualization on the piano roll.
 */
export class WaveformRenderer {
  private config: WaveformRendererConfig;
  private audioBuffer: AudioBuffer | null = null;
  private waveformData: Float32Array | null = null;
  private useBackendAudio = false;

  constructor(config?: Partial<WaveformRendererConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<WaveformRendererConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Set the audio buffer for rendering.
   */
  setAudioBuffer(buffer: AudioBuffer | null): void {
    this.audioBuffer = buffer;
    this.waveformData = null;
    this.useBackendAudio = false;
  }

  /**
   * Set pre-calculated waveform data.
   */
  setPreCalculatedWaveform(data: Float32Array | null): void {
    this.waveformData = data;
    this.audioBuffer = null;
    this.useBackendAudio = true;
  }

  /**
   * Set backend audio mode.
   */
  setUseBackendAudio(useBackend: boolean): void {
    this.useBackendAudio = useBackend;
  }

  /**
   * Render the waveform.
   */
  render(context: LayerRenderContext): void {
    const { ctx, width, tempo, horizontalScroll, pixelsPerBeat, isPlaying, currentFlicks } = context;

    if (!ctx) return;

    // Get waveform data
    const data = this.getWaveformData();
    if (!data) return;

    // Calculate waveform display parameters
    const samplesPerPixel = this.calculateSamplesPerPixel(context);
    const startX = 0;
    const endX = width;
    const waveformY = this.config.paddingTop + this.config.height / 2;

    // Apply opacity
    ctx.globalAlpha = this.config.opacity;
    ctx.strokeStyle = this.config.color;
    ctx.lineWidth = this.config.lineWidth;
    ctx.beginPath();

    // Render waveform
    let firstPoint = true;
    for (let x = startX; x < endX; x++) {
      const sampleIndex = Math.floor((x + horizontalScroll) / pixelsPerBeat * (tempo / 60) * this.audioBuffer!.sampleRate);

      if (sampleIndex >= 0 && sampleIndex < data.length) {
        const amplitude = data[sampleIndex] * this.config.amplitudeMultiplier * (this.config.height / 2);
        const y = waveformY - amplitude;

        if (firstPoint) {
          ctx.moveTo(x, y);
          firstPoint = false;
        } else {
          ctx.lineTo(x, y);
        }
      }
    }

    ctx.stroke();
    ctx.globalAlpha = 1.0;

    // Draw position indicator if playing
    if (isPlaying && currentFlicks !== undefined) {
      this.drawPositionIndicator(context, waveformY);
    }
  }

  /**
   * Get waveform data from buffer or pre-calculated data.
   */
  private getWaveformData(): Float32Array | null {
    if (this.waveformData) {
      return this.waveformData;
    }

    if (this.audioBuffer) {
      // Generate waveform data from buffer
      const channelData = this.audioBuffer.getChannelData(0);
      return this.downsampleForDisplay(channelData, 2000);
    }

    return null;
  }

  /**
   * Calculate samples per pixel for display.
   */
  private calculateSamplesPerPixel(context: LayerRenderContext): number {
    if (!this.audioBuffer) return 1;

    const { width, tempo, pixelsPerBeat } = context;
    const pixelsPerSecond = (tempo / 60) * pixelsPerBeat;
    const secondsToDisplay = width / pixelsPerSecond;

    return Math.floor(this.audioBuffer.sampleRate * secondsToDisplay / width);
  }

  /**
   * Downsample audio data for waveform display.
   */
  private downsampleForDisplay(data: Float32Array, targetLength: number): Float32Array {
    const result = new Float32Array(targetLength);
    const blockSize = Math.floor(data.length / targetLength);

    for (let i = 0; i < targetLength; i++) {
      const start = i * blockSize;
      let sum = 0;

      // Calculate RMS for each block
      for (let j = 0; j < blockSize && start + j < data.length; j++) {
        sum += Math.abs(data[start + j]);
      }

      result[i] = sum / blockSize;
    }

    return result;
  }

  /**
   * Draw current position indicator on waveform.
   */
  private drawPositionIndicator(context: LayerRenderContext, waveformY: number): void {
    const { ctx, currentFlicks, tempo, horizontalScroll, pixelsPerBeat, width } = context;

    const playheadX = flicksToPixels(currentFlicks, pixelsPerBeat, tempo) - horizontalScroll;

    // Skip if not visible
    if (playheadX < 0 || playheadX > width) return;

    // Draw indicator
    ctx.strokeStyle = '#ff4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, this.config.paddingTop);
    ctx.lineTo(playheadX, this.config.paddingTop + this.config.height);
    ctx.stroke();
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    this.audioBuffer = null;
    this.waveformData = null;
  }
}

/**
 * Create a waveform renderer instance.
 */
export function createWaveformRenderer(config?: Partial<WaveformRendererConfig>): WaveformRenderer {
  return new WaveformRenderer(config);
}
