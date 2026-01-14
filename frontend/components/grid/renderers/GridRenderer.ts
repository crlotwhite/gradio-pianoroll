/**
 * Grid Renderer for Piano Roll
 *
 * This module handles rendering of the piano roll grid including
 * measure lines, beat lines, and subdivision lines.
 */

import { createLogger } from '../../../utils/logger';
import type { LayerRenderContext, TimeSignature } from '../../../types';

const log = createLogger('GridRenderer');

/**
 * Grid renderer configuration.
 */
export interface GridRendererConfig {
  /** Pixels per beat */
  pixelsPerBeat: number;
  /** Time signature */
  timeSignature: TimeSignature;
  /** Background color for grid */
  backgroundColor: string;
  /** Measure line color */
  measureLineColor: string;
  /** Beat line color */
  beatLineColor: string;
  /** Subdivision line color */
  subdivisionLineColor: string;
  /** Subdivision lines per beat */
  subdivisionsPerBeat: number;
}

/**
 * Default grid renderer configuration.
 */
const DEFAULT_CONFIG: GridRendererConfig = {
  pixelsPerBeat: 80,
  timeSignature: { numerator: 4, denominator: 4 },
  backgroundColor: '#1e1e1e',
  measureLineColor: '#666666',
  beatLineColor: '#444444',
  subdivisionLineColor: '#2a2a2a',
  subdivisionsPerBeat: 4,
};

/**
 * GridRenderer class
 *
 * Renders the piano roll grid including measure lines, beat lines,
 * and subdivision lines based on the current time signature.
 */
export class GridRenderer {
  private config: GridRendererConfig;

  constructor(config?: Partial<GridRendererConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<GridRendererConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Render the grid.
   */
  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, pixelsPerBeat, timeSignature } = context;

    if (!ctx) return;

    // Update config from context
    this.config.pixelsPerBeat = pixelsPerBeat;
    this.config.timeSignature = timeSignature;

    // Draw background
    ctx.fillStyle = this.config.backgroundColor;
    ctx.fillRect(0, 0, width, height);

    // Calculate visible range
    const startX = horizontalScroll;
    const endX = horizontalScroll + width;

    // Calculate beats per measure
    const beatsPerMeasure = timeSignature.numerator;

    // Render subdivision lines (finest grid)
    this.renderSubdivisionLines(ctx, startX, endX, pixelsPerBeat);

    // Render beat lines
    this.renderBeatLines(ctx, startX, endX, pixelsPerBeat);

    // Render measure lines (coarsest grid)
    this.renderMeasureLines(ctx, startX, endX, beatsPerMeasure * pixelsPerBeat);
  }

  /**
   * Render subdivision lines.
   */
  private renderSubdivisionLines(
    ctx: CanvasRenderingContext2D,
    startX: number,
    endX: number,
    pixelsPerBeat: number
  ): void {
    const pixelsPerSubdivision = pixelsPerBeat / this.config.subdivisionsPerBeat;

    ctx.strokeStyle = this.config.subdivisionLineColor;
    ctx.lineWidth = 0.5;

    ctx.beginPath();

    const startSubdivision = Math.floor(startX / pixelsPerSubdivision);
    const endSubdivision = Math.ceil(endX / pixelsPerSubdivision);

    for (let i = startSubdivision; i <= endSubdivision; i++) {
      const x = i * pixelsPerSubdivision;
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 2560); // Grid total height
    }

    ctx.stroke();
  }

  /**
   * Render beat lines.
   */
  private renderBeatLines(
    ctx: CanvasRenderingContext2D,
    startX: number,
    endX: number,
    pixelsPerBeat: number
  ): void {
    ctx.strokeStyle = this.config.beatLineColor;
    ctx.lineWidth = 1;

    ctx.beginPath();

    const startBeat = Math.floor(startX / pixelsPerBeat);
    const endBeat = Math.ceil(endX / pixelsPerBeat);

    for (let i = startBeat; i <= endBeat; i++) {
      const x = i * pixelsPerBeat;
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 2560);
    }

    ctx.stroke();
  }

  /**
   * Render measure lines.
   */
  private renderMeasureLines(
    ctx: CanvasRenderingContext2D,
    startX: number,
    endX: number,
    pixelsPerMeasure: number
  ): void {
    ctx.strokeStyle = this.config.measureLineColor;
    ctx.lineWidth = 2;

    ctx.beginPath();

    const startMeasure = Math.floor(startX / pixelsPerMeasure);
    const endMeasure = Math.ceil(endX / pixelsPerMeasure);

    for (let i = startMeasure; i <= endMeasure; i++) {
      const x = i * pixelsPerMeasure;
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 2560);
    }

    ctx.stroke();
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    // No persistent resources to clean up
  }
}

/**
 * Create a grid renderer instance.
 */
export function createGridRenderer(config?: Partial<GridRendererConfig>): GridRenderer {
  return new GridRenderer(config);
}
