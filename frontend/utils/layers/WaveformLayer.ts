/**
 * WaveformLayer - Renders audio waveform visualization
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext } from '../LayerSystem';

export class WaveformLayer extends BaseLayer {
  // Waveform colors
  private readonly WAVEFORM_COLOR = '#4287f5';
  private readonly BACKEND_WAVEFORM_COLOR = '#4CAF50';
  private readonly BACKGROUND_COLOR = 'rgba(20, 20, 20, 0.05)'; // 매우 투명한 배경으로 변경

  private audioBuffer: AudioBuffer | null = null;
  private preCalculatedWaveform: Array<{x: number, min: number, max: number}> | null = null;
  private useBackendAudio: boolean = false;

  constructor() {
    super('waveform', LayerZIndex.WAVEFORM);
  }

  // Set audio buffer for rendering
  setAudioBuffer(buffer: AudioBuffer | null): void {
    this.audioBuffer = buffer;
    this.preCalculatedWaveform = null; // Clear pre-calculated when setting new buffer
  }

  // Set pre-calculated waveform data
  setPreCalculatedWaveform(data: Array<{x: number, min: number, max: number}> | null): void {
    this.preCalculatedWaveform = data;
  }

  // Set whether to use backend audio styling
  setUseBackendAudio(useBackend: boolean): void {
    this.useBackendAudio = useBackend;
  }

  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, pixelsPerBeat, tempo } = context;

    // Calculate waveform position and size (lower half of the grid)
    const waveformHeight = height / 3; // Use 1/3 of total height
    const waveformTop = height - waveformHeight - 50; // Position in lower area

    // Save current context state
    ctx.save();

    // Set clipping region for waveform
    ctx.beginPath();
    ctx.rect(0, waveformTop, width, waveformHeight);
    ctx.clip();

    // Don't clear or draw background - keep it transparent

    // Draw center line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    const centerY = waveformTop + waveformHeight / 2;
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();

    // Render waveform data if available
    if (this.preCalculatedWaveform) {
      this.drawPreCalculatedWaveform(ctx, width, waveformHeight, waveformTop, horizontalScroll);
    } else if (this.audioBuffer) {
      this.drawAudioBufferWaveform(ctx, width, waveformHeight, waveformTop, horizontalScroll, pixelsPerBeat, tempo);
    } else {
      this.drawEmptyWaveform(ctx, width, waveformHeight, waveformTop);
    }

    // Restore context state
    ctx.restore();
  }

    private drawPreCalculatedWaveform(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    top: number,
    horizontalScroll: number
  ): void {
    if (!this.preCalculatedWaveform || this.preCalculatedWaveform.length === 0) {
      this.drawEmptyWaveform(ctx, width, height, top);
      return;
    }

    // Draw waveform from pre-calculated data
    ctx.strokeStyle = this.BACKEND_WAVEFORM_COLOR;
    ctx.lineWidth = 1.5;
    ctx.beginPath();

    const centerY = top + height / 2;
    let hasDrawnAnyPoint = false;

    // Sort waveform data by x coordinate
    const sortedData = [...this.preCalculatedWaveform].sort((a, b) => a.x - b.x);

    for (let screenX = 0; screenX < width; screenX++) {
      // Find data point considering scroll position
      const dataX = screenX + horizontalScroll;

      // Find closest waveform data point
      const dataPoint = sortedData.find(point => Math.abs(point.x - dataX) < 1);

      if (dataPoint) {
        // Map sample values to y-coordinates (-1 to 1 range to canvas height)
        const minY = centerY + dataPoint.min * (height / 2) * 0.9;
        const maxY = centerY + dataPoint.max * (height / 2) * 0.9;

        if (!hasDrawnAnyPoint) {
          ctx.moveTo(screenX, minY);
          hasDrawnAnyPoint = true;
        }

        // Draw vertical line from min to max
        ctx.lineTo(screenX, minY);
        ctx.lineTo(screenX, maxY);
      }
    }

    if (hasDrawnAnyPoint) {
      ctx.stroke();
    }
  }

  private drawAudioBufferWaveform(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    top: number,
    horizontalScroll: number,
    pixelsPerBeat: number,
    tempo: number
  ): void {
    if (!this.audioBuffer) return;

    // Get audio data (use first channel)
    const channelData = this.audioBuffer.getChannelData(0);
    const bufferLength = channelData.length;

    // Calculate total duration in seconds
    const totalSeconds = this.audioBuffer.duration;
    // Calculate total length in pixels
    const totalPixels = (tempo / 60) * pixelsPerBeat * totalSeconds;
    // Calculate samples per pixel
    const samplesPerPixel = bufferLength / totalPixels;

    // Draw waveform
    ctx.strokeStyle = this.useBackendAudio ? this.BACKEND_WAVEFORM_COLOR : this.WAVEFORM_COLOR;
    ctx.lineWidth = 1.5;
    ctx.beginPath();

    // Map audio samples to canvas coordinates
    const centerY = top + height / 2;
    let lastX = -1;
    let lastMaxY = centerY;
    let lastMinY = centerY;

    for (let x = 0; x < width; x++) {
      const pixelStartSample = Math.floor((x + horizontalScroll) * samplesPerPixel);
      const pixelEndSample = Math.floor((x + 1 + horizontalScroll) * samplesPerPixel);

      // Find min and max sample values in this pixel column
      let min = 0;
      let max = 0;

      for (let i = pixelStartSample; i < pixelEndSample && i < bufferLength; i++) {
        if (i < 0) continue;

        const sample = channelData[i];
        if (sample < min) min = sample;
        if (sample > max) max = sample;
      }

      // Map sample values to y-coordinates
      const minY = centerY + min * (height / 2) * 0.9;
      const maxY = centerY + max * (height / 2) * 0.9;

      // Only draw if different from last pixel to optimize performance
      if (x === 0 || lastX !== x - 1 || lastMinY !== minY || lastMaxY !== maxY) {
        if (x === 0 || lastX !== x - 1) {
          ctx.moveTo(x, minY);
        }

        // Draw vertical line from min to max
        ctx.lineTo(x, minY);
        ctx.lineTo(x, maxY);

        lastX = x;
        lastMinY = minY;
        lastMaxY = maxY;
      }
    }

    ctx.stroke();
  }

  private drawEmptyWaveform(ctx: CanvasRenderingContext2D, width: number, height: number, top: number): void {
    // Draw "No waveform" message
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('웨이브폼이 없습니다. "Synthesize Audio" 버튼을 클릭하세요.', width / 2, top + height / 2);
  }

  // Helper methods
  hasWaveformData(): boolean {
    return this.audioBuffer !== null || (this.preCalculatedWaveform !== null && this.preCalculatedWaveform.length > 0);
  }
}