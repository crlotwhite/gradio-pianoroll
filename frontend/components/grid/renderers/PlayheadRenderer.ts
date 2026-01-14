/**
 * Playhead Renderer for Piano Roll
 *
 * This module handles rendering of the playhead position indicator.
 */

import { createLogger } from '../../../utils/logger';
import type { LayerRenderContext } from '../../../types';
import { flicksToPixels } from '../../../utils/flicks';

const log = createLogger('PlayheadRenderer');

/**
 * Playhead renderer configuration.
 */
export interface PlayheadRendererConfig {
  /** Playhead line color */
  lineColor: string;
  /** Playhead line width */
  lineWidth: number;
  /** Playhead handle color */
  handleColor: string;
  /** Playhead handle size */
  handleSize: number;
  /** Playhead glow color */
  glowColor: string;
  /** Playhead glow intensity */
  glowIntensity: number;
}

/**
 * Default playhead renderer configuration.
 */
const DEFAULT_CONFIG: PlayheadRendererConfig = {
  lineColor: '#ff4444',
  lineWidth: 2,
  handleColor: '#ff6666',
  handleSize: 10,
  glowColor: '#ff4444',
  glowIntensity: 0.3,
};

/**
 * PlayheadRenderer class
 *
 * Renders the playhead position indicator on the piano roll.
 */
export class PlayheadRenderer {
  private config: PlayheadRendererConfig;

  constructor(config?: Partial<PlayheadRendererConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<PlayheadRendererConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Render the playhead.
   */
  render(context: LayerRenderContext): void {
    const { ctx, width, height, currentFlicks, tempo, horizontalScroll, pixelsPerBeat } = context;

    if (!ctx) return;

    // Calculate playhead position
    const playheadX = flicksToPixels(currentFlicks, pixelsPerBeat, tempo) - horizontalScroll;

    // Skip if not visible
    if (playheadX < 0 || playheadX > width) return;

    // Draw glow effect
    this.drawGlow(ctx, playheadX, height);

    // Draw playhead line
    this.drawLine(ctx, playheadX, height);

    // Draw playhead handle
    this.drawHandle(ctx, playheadX, height);
  }

  /**
   * Draw glow effect around playhead.
   */
  private drawGlow(ctx: CanvasRenderingContext2D, x: number, height: number): void {
    ctx.save();
    ctx.shadowColor = this.config.glowColor;
    ctx.shadowBlur = this.config.glowIntensity * 20;
    ctx.strokeStyle = this.config.glowColor;
    ctx.lineWidth = this.config.lineWidth + 4;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
    ctx.restore();
  }

  /**
   * Draw playhead line.
   */
  private drawLine(ctx: CanvasRenderingContext2D, x: number, height: number): void {
    ctx.strokeStyle = this.config.lineColor;
    ctx.lineWidth = this.config.lineWidth;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }

  /**
   * Draw playhead handle at top.
   */
  private drawHandle(ctx: CanvasRenderingContext2D, x: number, _height: number): void {
    const size = this.config.handleSize;

    ctx.fillStyle = this.config.handleColor;
    ctx.beginPath();
    ctx.moveTo(x - size / 2, 0);
    ctx.lineTo(x + size / 2, 0);
    ctx.lineTo(x, size);
    ctx.closePath();
    ctx.fill();
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    // No persistent resources to clean up
  }
}

/**
 * Create a playhead renderer instance.
 */
export function createPlayheadRenderer(config?: Partial<PlayheadRendererConfig>): PlayheadRenderer {
  return new PlayheadRenderer(config);
}
