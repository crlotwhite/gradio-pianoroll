/**
 * WaveformLayer - Displays audio waveform visualization as a layer
 */
import type { Layer, LayerEvent, Viewport, HitResult, AudioData, LayerManager as ILayerManager } from './types';
import { AudioEngineManager } from '../../utils/audioEngine';

export interface WaveformLayerProps {
  id: string;
  name: string;
  elemId?: string;
  audioData?: AudioData;
  useBackendAudio?: boolean;
  visible?: boolean;
  opacity?: number;
  zIndex?: number;
  position?: { top: number }; // Vertical position offset
}

export class WaveformLayer implements Layer {
  readonly id: string;
  readonly name: string;
  visible: boolean;
  opacity: number;
  zIndex: number;

  // Waveform specific properties
  private elemId: string;
  private audioData: AudioData | null = null;
  private useBackendAudio: boolean = false;
  private position: { top: number };

  // Audio processing
  private backendAudioBuffer: AudioBuffer | null = null;
  private audioContextForDecoding: AudioContext | null = null;

  // Visual properties
  private readonly WAVEFORM_COLOR = '#4287f5';
  private readonly BACKEND_WAVEFORM_COLOR = '#4CAF50';
  private readonly BACKGROUND_COLOR = 'rgba(30, 30, 30, 0.4)';

  constructor(props: WaveformLayerProps) {
    this.id = props.id;
    this.name = props.name;
    this.elemId = props.elemId || 'default';
    this.visible = props.visible ?? true;
    this.opacity = props.opacity ?? 0.7;
    this.zIndex = props.zIndex ?? 1;
    this.position = props.position ?? { top: 0 };

    if (props.audioData) {
      this.setAudioData(props.audioData);
    }
    this.useBackendAudio = props.useBackendAudio ?? false;
  }

  // Set audio data
  setAudioData(audioData: AudioData): void {
    this.audioData = audioData;

    if (this.useBackendAudio && audioData.audioUrl) {
      this.decodeBackendAudio(audioData.audioUrl);
    }
  }

  // Set backend audio flag
  setUseBackendAudio(useBackend: boolean): void {
    this.useBackendAudio = useBackend;
    if (useBackend && this.audioData?.audioUrl) {
      this.decodeBackendAudio(this.audioData.audioUrl);
    }
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    const layerHeight = Math.floor(viewport.height / 2);
    const layerTop = this.position.top;

    // Don't clear the layer area to preserve the grid background
    // ctx.clearRect(0, layerTop, viewport.width, layerHeight);

    // Don't draw background to keep it transparent and show the grid
    // ctx.fillStyle = this.BACKGROUND_COLOR;
    // ctx.fillRect(0, layerTop, viewport.width, layerHeight);

    // Draw center line (optional - can be commented out if not needed)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    const centerY = layerTop + layerHeight / 2;
    ctx.moveTo(0, centerY);
    ctx.lineTo(viewport.width, centerY);
    ctx.stroke();

    // 1. 미리 계산된 웨이브폼 데이터 사용
    if (this.audioData?.waveformData) {
      this.drawPreCalculatedWaveform(ctx, viewport, layerTop, layerHeight);
      return;
    }

    // 2. 오디오 버퍼 사용
    let buffer: AudioBuffer | null = null;
    if (this.useBackendAudio && this.backendAudioBuffer) {
      buffer = this.backendAudioBuffer;
    } else if (!this.useBackendAudio) {
      // 프론트엔드 오디오 엔진 사용
      const audioEngine = AudioEngineManager.getInstance(this.elemId);
      buffer = audioEngine.getRenderedBuffer();
    }

    if (buffer) {
      this.drawWaveformFromBuffer(ctx, viewport, layerTop, layerHeight, buffer);
    } else {
      this.drawEmptyWaveform(ctx, viewport, layerTop, layerHeight);
    }
  }

  hitTest(worldX: number, worldY: number, viewport: Viewport): HitResult | null {
    const layerHeight = Math.floor(viewport.height / 2);
    const layerTop = this.position.top;

    // Convert world coordinates to canvas coordinates
    const canvasY = worldY - viewport.verticalScroll;

    // Check if point is within this layer's bounds
    if (canvasY >= layerTop && canvasY <= layerTop + layerHeight) {
      return {
        layerId: this.id,
        elementType: 'waveform',
        cursor: 'default'
      };
    }

    return null;
  }

  handleEvent(event: LayerEvent, viewport: Viewport): boolean {
    // For now, waveform doesn't handle events (read-only)
    // Future: Could handle scrubbing, selection, etc.
    return false;
  }

  onResize(viewport: Viewport): void {
    // Waveform layer doesn't need special resize handling
    // It will be redrawn automatically
  }

  dispose(): void {
    if (this.audioContextForDecoding) {
      this.audioContextForDecoding.close();
      this.audioContextForDecoding = null;
    }
    this.backendAudioBuffer = null;
    this.audioData = null;
  }

  // Draw waveform from pre-calculated data
  private drawPreCalculatedWaveform(
    ctx: CanvasRenderingContext2D,
    viewport: Viewport,
    layerTop: number,
    layerHeight: number
  ): void {
    if (!this.audioData?.waveformData || this.audioData.waveformData.length === 0) {
      this.drawEmptyWaveform(ctx, viewport, layerTop, layerHeight);
      return;
    }

    ctx.strokeStyle = this.BACKEND_WAVEFORM_COLOR;
    ctx.lineWidth = 2;
    ctx.beginPath();

    const centerY = layerTop + layerHeight / 2;
    let hasDrawnAnyPoint = false;

    // Sort waveform data by x coordinate
    const sortedData = [...this.audioData.waveformData].sort((a, b) => a.x - b.x);

    for (let screenX = 0; screenX < viewport.width; screenX++) {
      // Find data point considering scroll position
      const dataX = screenX + viewport.horizontalScroll;
      const dataPoint = sortedData.find(point => Math.abs(point.x - dataX) < 1);

      if (dataPoint) {
        // Map sample values to y-coordinates (-1 to 1 range to canvas height)
        const minY = centerY + dataPoint.min * (layerHeight / 2) * 0.9;
        const maxY = centerY + dataPoint.max * (layerHeight / 2) * 0.9;

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

  // Draw waveform from audio buffer
  private drawWaveformFromBuffer(
    ctx: CanvasRenderingContext2D,
    viewport: Viewport,
    layerTop: number,
    layerHeight: number,
    buffer: AudioBuffer
  ): void {
    // Get audio data (use first channel)
    const channelData = buffer.getChannelData(0);
    const bufferLength = channelData.length;

    // Calculate total duration in seconds
    const totalSeconds = buffer.duration;
    // Calculate total length in pixels
    const totalPixels = (viewport.tempo / 60) * viewport.pixelsPerBeat * totalSeconds;
    // Calculate samples per pixel
    const samplesPerPixel = bufferLength / totalPixels;

    // Draw waveform
    ctx.strokeStyle = this.useBackendAudio ? this.BACKEND_WAVEFORM_COLOR : this.WAVEFORM_COLOR;
    ctx.lineWidth = 2;
    ctx.beginPath();

    const centerY = layerTop + layerHeight / 2;
    let lastX = -1;
    let lastMaxY = centerY;
    let lastMinY = centerY;

    for (let x = 0; x < viewport.width; x++) {
      const pixelStartSample = Math.floor((x + viewport.horizontalScroll) * samplesPerPixel);
      const pixelEndSample = Math.floor((x + 1 + viewport.horizontalScroll) * samplesPerPixel);

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
      const minY = centerY + min * (layerHeight / 2) * 0.9;
      const maxY = centerY + max * (layerHeight / 2) * 0.9;

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

  // Draw empty waveform background
  private drawEmptyWaveform(
    ctx: CanvasRenderingContext2D,
    viewport: Viewport,
    layerTop: number,
    layerHeight: number
  ): void {
    // Draw "No waveform" message with transparent background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const centerY = layerTop + layerHeight / 2;
    ctx.fillText('웨이브폼이 없습니다. "Synthesize Audio" 버튼을 클릭하세요.', viewport.width / 2, centerY);
  }

  // Decode backend audio data
  private async decodeBackendAudio(audioData: string): Promise<void> {
    if (!audioData) return;

    try {
      if (!this.audioContextForDecoding) {
        this.audioContextForDecoding = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      let arrayBuffer: ArrayBuffer;

      if (audioData.startsWith('data:')) {
        // Base64 data processing
        const base64Data = audioData.split(',')[1];
        const binaryString = atob(base64Data);
        arrayBuffer = new ArrayBuffer(binaryString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < binaryString.length; i++) {
          uint8Array[i] = binaryString.charCodeAt(i);
        }
      } else {
        // URL processing
        const response = await fetch(audioData);
        arrayBuffer = await response.arrayBuffer();
      }

      this.backendAudioBuffer = await this.audioContextForDecoding.decodeAudioData(arrayBuffer);
    } catch (error) {
      console.error('Error decoding backend audio:', error);
      this.backendAudioBuffer = null;
    }
  }

  // Public method to force redraw (for external calls)
  forceRedraw(): void {
    // This method can be called to trigger a redraw
    // The actual redraw will happen on next render cycle
  }
}