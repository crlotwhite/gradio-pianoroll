/**
 * Note Renderer for Piano Roll
 *
 * This module handles rendering of notes on the piano roll grid.
 */

import { createLogger } from '../../../utils/logger';
import type { LayerRenderContext, Note } from '../../../types';
import { pitchToY, NOTE_HEIGHT } from '../../../utils/constants';

const log = createLogger('NoteRenderer');

/**
 * Note renderer configuration.
 */
export interface NoteRendererConfig {
  /** Default note color */
  defaultColor: string;
  /** Selected note color */
  selectedColor: string;
  /** Near edge note color */
  nearEdgeColor: string;
  /** Note corner radius */
  cornerRadius: number;
  /** Note height in pixels */
  noteHeight: number;
  /** Lyric text color */
  lyricColor: string;
  /** Lyric font size */
  lyricFontSize: number;
}

/**
 * Default note renderer configuration.
 */
const DEFAULT_CONFIG: NoteRendererConfig = {
  defaultColor: '#4a9eff',
  selectedColor: '#7eb8ff',
  nearEdgeColor: '#5aafff',
  cornerRadius: 4,
  noteHeight: NOTE_HEIGHT,
  lyricColor: '#ffffff',
  lyricFontSize: 11,
};

/**
 * Selection state for notes.
 */
export interface NoteSelectionState {
  selectedNotes: Set<string>;
  nearEdgeNoteId: string | null;
}

/**
 * NoteRenderer class
 *
 * Renders notes on the piano roll with support for selection,
 * resizing indicators, and lyric display.
 */
export class NoteRenderer {
  private config: NoteRendererConfig;

  constructor(config?: Partial<NoteRendererConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<NoteRendererConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Render notes.
   */
  render(context: LayerRenderContext, notes: Note[], selection?: NoteSelectionState): void {
    const { ctx, horizontalScroll, verticalScroll, pixelsPerBeat, isPlaying, currentFlicks } = context;

    if (!ctx) return;

    // Render each note
    notes.forEach((note) => {
      this.renderNote(ctx, note, horizontalScroll, verticalScroll, pixelsPerBeat, selection);
    });

    // Draw playhead position indicator if playing
    if (isPlaying && currentFlicks !== undefined) {
      this.renderPlayheadIndicator(ctx, currentFlicks, horizontalScroll, pixelsPerBeat);
    }
  }

  /**
   * Render a single note.
   */
  private renderNote(
    ctx: CanvasRenderingContext2D,
    note: Note,
    horizontalScroll: number,
    verticalScroll: number,
    pixelsPerBeat: number,
    selection?: NoteSelectionState
  ): void {
    const screenX = note.start - horizontalScroll;
    const screenY = pitchToY(note.pitch) - verticalScroll;

    // Determine note color based on selection state
    const isSelected = selection?.selectedNotes.has(note.id) ?? false;
    const isNearEdge = selection?.nearEdgeNoteId === note.id;

    let fillColor = this.config.defaultColor;
    if (isSelected) {
      fillColor = this.config.selectedColor;
    } else if (isNearEdge) {
      fillColor = this.config.nearEdgeColor;
    }

    // Draw note rectangle
    ctx.fillStyle = fillColor;
    this.drawRoundedRect(
      ctx,
      screenX,
      screenY,
      note.duration,
      this.config.noteHeight - 1,
      this.config.cornerRadius
    );
    ctx.fill();

    // Draw lyric if present
    if (note.lyric) {
      this.renderLyric(ctx, note.lyric, screenX, screenY, note.duration);
    }

    // Draw resize handle indicator if selected
    if (isSelected) {
      this.drawResizeHandle(ctx, screenX + note.duration - 8, screenY, 8, this.config.noteHeight - 1);
    }
  }

  /**
   * Draw a rounded rectangle.
   */
  private drawRoundedRect(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    radius: number
  ): void {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  /**
   * Draw resize handle.
   */
  private drawResizeHandle(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number
  ): void {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillRect(x, y, width, height);
  }

  /**
   * Render lyric text on a note.
   */
  private renderLyric(
    ctx: CanvasRenderingContext2D,
    lyric: string,
    x: number,
    y: number,
    width: number
  ): void {
    ctx.fillStyle = this.config.lyricColor;
    ctx.font = `${this.config.lyricFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Truncate if too long
    const maxWidth = width - 4;
    let displayText = lyric;
    if (ctx.measureText(displayText).width > maxWidth) {
      while (ctx.measureText(displayText + '...').width > maxWidth && displayText.length > 0) {
        displayText = displayText.slice(0, -1);
      }
      displayText += '...';
    }

    ctx.fillText(displayText, x + width / 2, y + this.config.noteHeight / 2);
  }

  /**
   * Render playhead position indicator.
   */
  private renderPlayheadIndicator(
    ctx: CanvasRenderingContext2D,
    currentFlicks: number,
    horizontalScroll: number,
    pixelsPerBeat: number
  ): void {
    // Convert flicks to pixels
    const beats = currentFlicks / (705600000 * 60 / 120); // Simplified conversion
    const x = beats * pixelsPerBeat - horizontalScroll;

    // Draw playhead line
    ctx.strokeStyle = '#ff4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 2560);
    ctx.stroke();

    // Draw playhead handle
    ctx.fillStyle = '#ff4444';
    ctx.beginPath();
    ctx.moveTo(x - 6, 0);
    ctx.lineTo(x + 6, 0);
    ctx.lineTo(x, 12);
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
 * Create a note renderer instance.
 */
export function createNoteRenderer(config?: Partial<NoteRendererConfig>): NoteRenderer {
  return new NoteRenderer(config);
}
