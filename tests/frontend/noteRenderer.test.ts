/**
 * Tests for noteRenderer utility functions.
 *
 * These tests verify the note rendering logic extracted from NotesLayer,
 * including coordinate calculations, visibility checks, and hit testing.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  calculateNoteY,
  calculateNoteScreenPosition,
  isNoteVisible,
  findNotesAtPosition,
  isPointInNote,
  DEFAULT_NOTE_CONFIG,
  type RenderableNote,
  type NoteRenderContext,
} from '../../frontend/utils/noteRenderer';
import { NOTE_HEIGHT, TOTAL_NOTES } from '../../frontend/utils/constants';

// ============================================================================
// Test Fixtures
// ============================================================================

function createTestNote(overrides: Partial<RenderableNote> = {}): RenderableNote {
  return {
    id: 'test-note-1',
    start: 100,
    duration: 40,
    pitch: 60, // Middle C
    velocity: 100,
    lyric: '라',
    ...overrides,
  };
}

function createMockContext(): CanvasRenderingContext2D {
  return {
    fillStyle: '',
    strokeStyle: '',
    lineWidth: 0,
    font: '',
    textAlign: 'left',
    textBaseline: 'top',
    fillRect: vi.fn(),
    strokeRect: vi.fn(),
    fillText: vi.fn(),
    measureText: vi.fn((text: string) => ({ width: text.length * 6 })),
  } as unknown as CanvasRenderingContext2D;
}

function createTestRenderContext(
  overrides: Partial<NoteRenderContext> = {}
): NoteRenderContext {
  // Default verticalScroll to show middle C (pitch 60) in viewport
  // Y for pitch 60 = (128 - 1 - 60) * 20 = 1340
  // We want this visible in a 600px height viewport
  const defaultVerticalScroll = calculateNoteY(60) - 300; // Center pitch 60

  return {
    ctx: createMockContext(),
    width: 800,
    height: 600,
    horizontalScroll: 0,
    verticalScroll: defaultVerticalScroll,
    ...overrides,
  };
}

// ============================================================================
// calculateNoteY Tests
// ============================================================================

describe('calculateNoteY', () => {
  it('calculates correct Y for middle C (pitch 60)', () => {
    const y = calculateNoteY(60);
    // (128 - 1 - 60) * 20 = 67 * 20 = 1340
    expect(y).toBe((TOTAL_NOTES - 1 - 60) * NOTE_HEIGHT);
  });

  it('returns 0 for highest pitch (127)', () => {
    const y = calculateNoteY(127);
    expect(y).toBe(0);
  });

  it('returns maximum Y for lowest pitch (0)', () => {
    const y = calculateNoteY(0);
    expect(y).toBe((TOTAL_NOTES - 1) * NOTE_HEIGHT);
  });

  it('handles edge case pitches', () => {
    expect(calculateNoteY(1)).toBe((TOTAL_NOTES - 2) * NOTE_HEIGHT);
    expect(calculateNoteY(126)).toBe(NOTE_HEIGHT);
  });
});

// ============================================================================
// calculateNoteScreenPosition Tests
// ============================================================================

describe('calculateNoteScreenPosition', () => {
  it('calculates position without scroll', () => {
    const note = createTestNote({ start: 100, pitch: 60 });
    const pos = calculateNoteScreenPosition(note, 0, 0);

    expect(pos.x).toBe(100);
    expect(pos.y).toBe(calculateNoteY(60));
  });

  it('applies horizontal scroll offset', () => {
    const note = createTestNote({ start: 100 });
    const pos = calculateNoteScreenPosition(note, 50, 0);

    expect(pos.x).toBe(50); // 100 - 50
  });

  it('applies vertical scroll offset', () => {
    const note = createTestNote({ pitch: 60 });
    const pos = calculateNoteScreenPosition(note, 0, 100);

    expect(pos.y).toBe(calculateNoteY(60) - 100);
  });

  it('applies both scroll offsets', () => {
    const note = createTestNote({ start: 200, pitch: 64 });
    const pos = calculateNoteScreenPosition(note, 50, 100);

    expect(pos.x).toBe(150);
    expect(pos.y).toBe(calculateNoteY(64) - 100);
  });
});

// ============================================================================
// isNoteVisible Tests
// ============================================================================

describe('isNoteVisible', () => {
  it('returns true for note fully inside viewport', () => {
    const note = createTestNote({ start: 100, duration: 40 });
    const context = createTestRenderContext();

    expect(isNoteVisible(note, context)).toBe(true);
  });

  it('returns true for note partially visible on left', () => {
    const note = createTestNote({ start: -20, duration: 40 });
    const context = createTestRenderContext();

    expect(isNoteVisible(note, context)).toBe(true);
  });

  it('returns false for note completely left of viewport', () => {
    const note = createTestNote({ start: -100, duration: 40 });
    const context = createTestRenderContext();

    expect(isNoteVisible(note, context)).toBe(false);
  });

  it('returns true for note partially visible on right', () => {
    const note = createTestNote({ start: 780, duration: 40 });
    const context = createTestRenderContext({ width: 800 });

    expect(isNoteVisible(note, context)).toBe(true);
  });

  it('returns false for note completely right of viewport', () => {
    const note = createTestNote({ start: 850 });
    const context = createTestRenderContext({ width: 800 });

    expect(isNoteVisible(note, context)).toBe(false);
  });

  it('considers scroll position', () => {
    const note = createTestNote({ start: 500 });
    const context = createTestRenderContext({
      width: 800,
      horizontalScroll: 600, // Note at 500 is now at -100 (off screen left)
    });

    expect(isNoteVisible(note, context)).toBe(false);
  });
});

// ============================================================================
// findNotesAtPosition Tests
// ============================================================================

describe('findNotesAtPosition', () => {
  const notes: RenderableNote[] = [
    createTestNote({ id: 'note-1', start: 100, duration: 40, pitch: 60 }),
    createTestNote({ id: 'note-2', start: 200, duration: 40, pitch: 62 }),
    createTestNote({ id: 'note-3', start: 100, duration: 40, pitch: 64 }), // Same X, different pitch
  ];

  it('finds note at exact position', () => {
    const found = findNotesAtPosition(notes, 110, calculateNoteY(60) + 5, 0, 0);
    expect(found).toHaveLength(1);
    expect(found[0].id).toBe('note-1');
  });

  it('returns empty array for position with no notes', () => {
    const found = findNotesAtPosition(notes, 300, 300, 0, 0);
    expect(found).toHaveLength(0);
  });

  it('handles scroll offsets correctly', () => {
    // With scroll of 50, screen X of 60 becomes world X of 110 (inside note-1)
    const found = findNotesAtPosition(notes, 60, calculateNoteY(60) + 5, 50, 0);
    expect(found).toHaveLength(1);
    expect(found[0].id).toBe('note-1');
  });

  it('finds multiple overlapping notes if they exist', () => {
    const overlappingNotes: RenderableNote[] = [
      createTestNote({ id: 'note-a', start: 100, duration: 40, pitch: 60 }),
      createTestNote({ id: 'note-b', start: 100, duration: 40, pitch: 60 }), // Same position
    ];

    const found = findNotesAtPosition(overlappingNotes, 110, calculateNoteY(60) + 5, 0, 0);
    expect(found).toHaveLength(2);
  });
});

// ============================================================================
// isPointInNote Tests
// ============================================================================

describe('isPointInNote', () => {
  const note = createTestNote({ start: 100, duration: 40, pitch: 60 });
  const noteY = calculateNoteY(60);

  it('returns true for point inside note', () => {
    expect(isPointInNote(note, 120, noteY + 10)).toBe(true);
  });

  it('returns true for point at note start edge', () => {
    expect(isPointInNote(note, 100, noteY)).toBe(true);
  });

  it('returns true for point at note end edge', () => {
    expect(isPointInNote(note, 140, noteY + NOTE_HEIGHT - 1)).toBe(true);
  });

  it('returns false for point left of note', () => {
    expect(isPointInNote(note, 99, noteY + 10)).toBe(false);
  });

  it('returns false for point right of note', () => {
    expect(isPointInNote(note, 141, noteY + 10)).toBe(false);
  });

  it('returns false for point above note', () => {
    expect(isPointInNote(note, 120, noteY - 1)).toBe(false);
  });

  it('returns false for point below note', () => {
    expect(isPointInNote(note, 120, noteY + NOTE_HEIGHT + 1)).toBe(false);
  });
});

// ============================================================================
// DEFAULT_NOTE_CONFIG Tests
// ============================================================================

describe('DEFAULT_NOTE_CONFIG', () => {
  it('has expected default values', () => {
    expect(DEFAULT_NOTE_CONFIG.noteColor).toBe('#2196F3');
    expect(DEFAULT_NOTE_CONFIG.selectedColor).toBe('#03A9F4');
    expect(DEFAULT_NOTE_CONFIG.lyricColor).toBe('#FFFFFF');
    expect(DEFAULT_NOTE_CONFIG.borderColor).toBe('#1a1a1a');
    expect(DEFAULT_NOTE_CONFIG.borderWidth).toBe(1);
    expect(DEFAULT_NOTE_CONFIG.showVelocity).toBe(true);
    expect(DEFAULT_NOTE_CONFIG.minLyricWidth).toBe(20);
  });
});
