/**
 * NoteRenderer - Utility for rendering individual piano roll notes
 *
 * This module provides functions for rendering notes on a canvas context.
 * It separates note rendering logic from the layer system for better reusability
 * and testability.
 *
 * @module noteRenderer
 */

import { NOTE_HEIGHT, TOTAL_NOTES } from './constants';

// ============================================================================
// Types
// ============================================================================

/**
 * Note data required for rendering.
 */
export interface RenderableNote {
  id: string;
  start: number;
  duration: number;
  pitch: number;
  velocity: number;
  lyric?: string;
  phoneme?: string;
}

/**
 * Configuration for note rendering appearance.
 */
export interface NoteRenderConfig {
  /** Fill color for unselected notes */
  noteColor: string;
  /** Fill color for selected notes */
  selectedColor: string;
  /** Text color for lyrics */
  lyricColor: string;
  /** Border color for notes */
  borderColor: string;
  /** Border line width */
  borderWidth: number;
  /** Font for lyrics */
  lyricFont: string;
  /** Whether to show velocity indicator */
  showVelocity: boolean;
  /** Minimum note width to display lyrics */
  minLyricWidth: number;
}

/**
 * Context for rendering notes (scroll and viewport info).
 */
export interface NoteRenderContext {
  /** Canvas 2D rendering context */
  ctx: CanvasRenderingContext2D;
  /** Viewport width */
  width: number;
  /** Viewport height */
  height: number;
  /** Horizontal scroll offset */
  horizontalScroll: number;
  /** Vertical scroll offset */
  verticalScroll: number;
}

// ============================================================================
// Default Configuration
// ============================================================================

/**
 * Default note rendering configuration.
 */
export const DEFAULT_NOTE_CONFIG: NoteRenderConfig = {
  noteColor: '#2196F3',
  selectedColor: '#03A9F4',
  lyricColor: '#FFFFFF',
  borderColor: '#1a1a1a',
  borderWidth: 1,
  lyricFont: '10px Arial',
  showVelocity: true,
  minLyricWidth: 20,
};

// ============================================================================
// Coordinate Calculations
// ============================================================================

/**
 * Calculate the Y position for a note based on its pitch.
 *
 * @param pitch - MIDI pitch value (0-127)
 * @returns Y coordinate in world space
 */
export function calculateNoteY(pitch: number): number {
  return (TOTAL_NOTES - 1 - pitch) * NOTE_HEIGHT;
}

/**
 * Calculate screen position for a note.
 *
 * @param note - The note to position
 * @param horizontalScroll - Horizontal scroll offset
 * @param verticalScroll - Vertical scroll offset
 * @returns Screen coordinates { x, y }
 */
export function calculateNoteScreenPosition(
  note: RenderableNote,
  horizontalScroll: number,
  verticalScroll: number
): { x: number; y: number } {
  return {
    x: note.start - horizontalScroll,
    y: calculateNoteY(note.pitch) - verticalScroll,
  };
}

/**
 * Check if a note is visible in the viewport.
 *
 * @param note - The note to check
 * @param context - Render context with viewport info
 * @returns True if the note is at least partially visible
 */
export function isNoteVisible(
  note: RenderableNote,
  context: NoteRenderContext
): boolean {
  const { x, y } = calculateNoteScreenPosition(
    note,
    context.horizontalScroll,
    context.verticalScroll
  );

  return !(
    x + note.duration < 0 ||
    x > context.width ||
    y + NOTE_HEIGHT < 0 ||
    y > context.height
  );
}

// ============================================================================
// Rendering Functions
// ============================================================================

/**
 * Render a single note on the canvas.
 *
 * @param note - The note to render
 * @param context - Render context
 * @param isSelected - Whether the note is selected
 * @param config - Render configuration (optional, uses defaults)
 */
export function renderNote(
  note: RenderableNote,
  context: NoteRenderContext,
  isSelected: boolean,
  config: NoteRenderConfig = DEFAULT_NOTE_CONFIG
): void {
  const { ctx } = context;
  const { x, y } = calculateNoteScreenPosition(
    note,
    context.horizontalScroll,
    context.verticalScroll
  );

  // Draw note rectangle
  ctx.fillStyle = isSelected ? config.selectedColor : config.noteColor;
  ctx.fillRect(x, y, note.duration, NOTE_HEIGHT);

  // Draw border
  ctx.strokeStyle = config.borderColor;
  ctx.lineWidth = config.borderWidth;
  ctx.strokeRect(x, y, note.duration, NOTE_HEIGHT);

  // Draw velocity indicator
  if (config.showVelocity) {
    renderVelocityIndicator(note, x, y, ctx);
  }

  // Draw lyric text
  if (note.lyric && note.duration > config.minLyricWidth) {
    renderLyricText(note, x, y, ctx, config);
  }
}

/**
 * Render the velocity indicator on a note.
 *
 * @param note - The note
 * @param x - Screen X position
 * @param y - Screen Y position
 * @param ctx - Canvas context
 */
function renderVelocityIndicator(
  note: RenderableNote,
  x: number,
  y: number,
  ctx: CanvasRenderingContext2D
): void {
  const velocityHeight = (NOTE_HEIGHT - 4) * (note.velocity / 127);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
  ctx.fillRect(
    x + 2,
    y + 2 + (NOTE_HEIGHT - 4 - velocityHeight),
    note.duration - 4,
    velocityHeight
  );
}

/**
 * Render the lyric text on a note.
 *
 * @param note - The note
 * @param x - Screen X position
 * @param y - Screen Y position
 * @param ctx - Canvas context
 * @param config - Render configuration
 */
function renderLyricText(
  note: RenderableNote,
  x: number,
  y: number,
  ctx: CanvasRenderingContext2D,
  config: NoteRenderConfig
): void {
  ctx.fillStyle = config.lyricColor;
  ctx.font = config.lyricFont;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  // Build text with optional phoneme
  let text = note.lyric || '';
  if (note.phoneme) {
    text += ` [${note.phoneme}]`;
  }

  // Truncate text to fit within note width
  const maxWidth = note.duration - 6;
  text = truncateText(ctx, text, maxWidth, note.lyric || '');

  ctx.fillText(text, x + note.duration / 2, y + NOTE_HEIGHT / 2);
}

/**
 * Truncate text to fit within a maximum width.
 *
 * @param ctx - Canvas context for measuring text
 * @param text - Full text to display
 * @param maxWidth - Maximum width in pixels
 * @param fallbackText - Fallback text if phoneme makes it too long
 * @returns Truncated text with ellipsis if needed
 */
function truncateText(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
  fallbackText: string
): string {
  let textWidth = ctx.measureText(text).width;

  if (textWidth <= maxWidth) {
    return text;
  }

  // If text includes phoneme and is too long, try without phoneme
  if (text.length > fallbackText.length) {
    text = fallbackText;
    textWidth = ctx.measureText(text).width;

    if (textWidth <= maxWidth) {
      return text;
    }
  }

  // Truncate with ellipsis
  const ratio = maxWidth / textWidth;
  const truncatedLength = Math.floor(text.length * ratio) - 3;
  if (truncatedLength > 0) {
    return text.substring(0, truncatedLength) + '...';
  }

  return '...';
}

/**
 * Render multiple notes on the canvas.
 *
 * @param notes - Array of notes to render
 * @param context - Render context
 * @param selectedNotes - Set of selected note IDs
 * @param config - Render configuration (optional)
 */
export function renderNotes(
  notes: RenderableNote[],
  context: NoteRenderContext,
  selectedNotes: Set<string>,
  config: NoteRenderConfig = DEFAULT_NOTE_CONFIG
): void {
  for (const note of notes) {
    // Skip notes outside visible area
    if (!isNoteVisible(note, context)) {
      continue;
    }

    const isSelected = selectedNotes.has(note.id);
    renderNote(note, context, isSelected, config);
  }
}

// ============================================================================
// Hit Testing
// ============================================================================

/**
 * Find notes at a specific screen position.
 *
 * @param notes - Array of notes to search
 * @param screenX - Screen X coordinate
 * @param screenY - Screen Y coordinate
 * @param horizontalScroll - Horizontal scroll offset
 * @param verticalScroll - Vertical scroll offset
 * @returns Array of notes at the position
 */
export function findNotesAtPosition(
  notes: RenderableNote[],
  screenX: number,
  screenY: number,
  horizontalScroll: number,
  verticalScroll: number
): RenderableNote[] {
  // Convert screen coordinates to world coordinates
  const worldX = screenX + horizontalScroll;
  const worldY = screenY + verticalScroll;

  return notes.filter((note) => {
    const noteY = calculateNoteY(note.pitch);
    return (
      worldX >= note.start &&
      worldX <= note.start + note.duration &&
      worldY >= noteY &&
      worldY <= noteY + NOTE_HEIGHT
    );
  });
}

/**
 * Check if a point is inside a note.
 *
 * @param note - The note to check
 * @param worldX - World X coordinate
 * @param worldY - World Y coordinate
 * @returns True if the point is inside the note
 */
export function isPointInNote(
  note: RenderableNote,
  worldX: number,
  worldY: number
): boolean {
  const noteY = calculateNoteY(note.pitch);
  return (
    worldX >= note.start &&
    worldX <= note.start + note.duration &&
    worldY >= noteY &&
    worldY <= noteY + NOTE_HEIGHT
  );
}
