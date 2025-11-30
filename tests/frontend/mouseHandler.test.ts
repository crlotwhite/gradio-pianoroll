/**
 * Tests for mouseHandler utility functions.
 *
 * These tests verify the mouse event handling logic extracted from GridComponent,
 * including note creation, selection, dragging, and resizing operations.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  createInitialMouseState,
  getEdgeDetectionThreshold,
  isNearNoteEdge,
  createNote,
  handleMouseDown,
  handleMouseMove,
  handleMouseUp,
  type MouseState,
  type MouseHandlerConfig,
  type EditMode,
} from '../../frontend/utils/mouseHandler';
import type { Note } from '../../frontend/types';

// ============================================================================
// Test Fixtures
// ============================================================================

function createTestConfig(overrides: Partial<MouseHandlerConfig> = {}): MouseHandlerConfig {
  return {
    pixelsPerBeat: 80,
    tempo: 120,
    sampleRate: 44100,
    ppqn: 480,
    snapSetting: '1/8',
    horizontalScroll: 0,
    verticalScroll: 0,
    ...overrides,
  };
}

function createTestNote(overrides: Partial<Note> = {}): Note {
  return {
    id: 'test-note-1',
    start: 100,
    duration: 40,
    pitch: 60,
    velocity: 100,
    lyric: '라',
    ...overrides,
  };
}

// Stub find note function
function createFindNoteStub(noteToReturn: Note | null = null) {
  return (_x: number, _y: number) => noteToReturn;
}

// Stub snap to grid function (snaps to 10px grid)
function createSnapStub(gridSize: number = 10) {
  return (value: number) => Math.round(value / gridSize) * gridSize;
}

// ============================================================================
// createInitialMouseState Tests
// ============================================================================

describe('createInitialMouseState', () => {
  it('returns a fresh state with default values', () => {
    const state = createInitialMouseState();

    expect(state.isDragging).toBe(false);
    expect(state.isResizing).toBe(false);
    expect(state.isCreatingNote).toBe(false);
    expect(state.selectedNotes.size).toBe(0);
    expect(state.dragStartX).toBe(0);
    expect(state.dragStartY).toBe(0);
    expect(state.lastMouseX).toBe(0);
    expect(state.lastMouseY).toBe(0);
    expect(state.draggedNoteId).toBeNull();
    expect(state.resizedNoteId).toBeNull();
    expect(state.creationStartTime).toBe(0);
    expect(state.creationPitch).toBe(0);
    expect(state.noteOffsetX).toBe(0);
    expect(state.noteOffsetY).toBe(0);
    expect(state.isNearNoteEdge).toBe(false);
  });

  it('returns independent state objects', () => {
    const state1 = createInitialMouseState();
    const state2 = createInitialMouseState();

    state1.isDragging = true;
    state1.selectedNotes.add('note-1');

    expect(state2.isDragging).toBe(false);
    expect(state2.selectedNotes.size).toBe(0);
  });
});

// ============================================================================
// getEdgeDetectionThreshold Tests
// ============================================================================

describe('getEdgeDetectionThreshold', () => {
  it('returns minimum threshold for low zoom levels', () => {
    expect(getEdgeDetectionThreshold(20)).toBe(5); // 20/8 = 2.5, clamped to 5
  });

  it('returns maximum threshold for high zoom levels', () => {
    expect(getEdgeDetectionThreshold(200)).toBe(15); // 200/8 = 25, clamped to 15
  });

  it('returns proportional threshold for medium zoom levels', () => {
    expect(getEdgeDetectionThreshold(80)).toBe(10); // 80/8 = 10
  });
});

// ============================================================================
// isNearNoteEdge Tests
// ============================================================================

describe('isNearNoteEdge', () => {
  const note = createTestNote({ start: 100, duration: 40 }); // end = 140

  it('returns true when x is at note edge', () => {
    expect(isNearNoteEdge(140, note, 80)).toBe(true); // exactly at edge
  });

  it('returns true when x is within threshold of edge', () => {
    const threshold = getEdgeDetectionThreshold(80); // 10
    expect(isNearNoteEdge(135, note, 80)).toBe(true); // 5px before edge
    expect(isNearNoteEdge(145, note, 80)).toBe(true); // 5px after edge
  });

  it('returns false when x is far from edge', () => {
    expect(isNearNoteEdge(100, note, 80)).toBe(false); // at start
    expect(isNearNoteEdge(120, note, 80)).toBe(false); // in middle
    expect(isNearNoteEdge(160, note, 80)).toBe(false); // too far after
  });
});

// ============================================================================
// createNote Tests
// ============================================================================

describe('createNote', () => {
  const config = createTestConfig();

  it('creates note with correct basic properties', () => {
    const note = createNote(100, 60, config);

    expect(note.start).toBe(100);
    expect(note.pitch).toBe(60);
    expect(note.velocity).toBe(100);
    expect(note.lyric).toBe('라');
  });

  it('generates unique IDs', () => {
    const note1 = createNote(100, 60, config);
    const note2 = createNote(100, 60, config);

    expect(note1.id).not.toBe(note2.id);
  });

  it('calculates timing data', () => {
    const note = createNote(100, 60, config);

    expect(note.startFlicks).toBeDefined();
    expect(note.durationFlicks).toBeDefined();
    expect(note.startSeconds).toBeDefined();
    expect(note.durationSeconds).toBeDefined();
  });

  it('clamps pitch to valid MIDI range', () => {
    const highNote = createNote(100, 150, config);
    const lowNote = createNote(100, -10, config);

    expect(highNote.pitch).toBeLessThanOrEqual(127);
    expect(lowNote.pitch).toBeGreaterThanOrEqual(0);
  });
});

// ============================================================================
// handleMouseDown Tests
// ============================================================================

describe('handleMouseDown', () => {
  let config: MouseHandlerConfig;
  let state: MouseState;
  let snapToGrid: (value: number) => number;

  beforeEach(() => {
    config = createTestConfig();
    state = createInitialMouseState();
    snapToGrid = createSnapStub(10);
  });

  describe('draw mode', () => {
    it('creates new note when clicking empty space', () => {
      const findNote = createFindNoteStub(null);

      const result = handleMouseDown(
        100, 100,
        'draw',
        false,
        [],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.notes.length).toBe(1);
      expect(result.notesChanged).toBe(true);
      expect(result.state.isCreatingNote).toBe(true);
      expect(result.state.isResizing).toBe(true);
    });

    it('does not create note when clicking existing note', () => {
      const existingNote = createTestNote();
      const findNote = createFindNoteStub(existingNote);

      const result = handleMouseDown(
        110, 100,
        'draw',
        false,
        [existingNote],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.notes.length).toBe(1);
      expect(result.notesChanged).toBe(false);
    });
  });

  describe('erase mode', () => {
    it('removes note when clicking on it', () => {
      const existingNote = createTestNote();
      const findNote = createFindNoteStub(existingNote);

      const result = handleMouseDown(
        110, 100,
        'erase',
        false,
        [existingNote],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.notes.length).toBe(0);
      expect(result.notesChanged).toBe(true);
    });

    it('does nothing when clicking empty space', () => {
      const findNote = createFindNoteStub(null);

      const result = handleMouseDown(
        100, 100,
        'erase',
        false,
        [],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.notes.length).toBe(0);
      expect(result.notesChanged).toBe(false);
    });
  });

  describe('select mode', () => {
    it('starts dragging when clicking note body', () => {
      const existingNote = createTestNote({ start: 100, duration: 40 });
      const findNote = createFindNoteStub(existingNote);

      const result = handleMouseDown(
        110, 100, // in the middle of the note, not near edge
        'select',
        false,
        [existingNote],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.state.isDragging).toBe(true);
      expect(result.state.draggedNoteId).toBe(existingNote.id);
      expect(result.state.selectedNotes.has(existingNote.id)).toBe(true);
    });

    it('starts resizing when clicking near note edge', () => {
      const existingNote = createTestNote({ start: 100, duration: 40 }); // edge at 140
      const findNote = createFindNoteStub(existingNote);

      const result = handleMouseDown(
        138, 100, // near the edge (140 - 138 = 2px, within threshold)
        'select',
        false,
        [existingNote],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.state.isResizing).toBe(true);
      expect(result.state.resizedNoteId).toBe(existingNote.id);
    });

    it('clears selection when clicking empty space without shift', () => {
      state.selectedNotes.add('some-note');
      const findNote = createFindNoteStub(null);

      const result = handleMouseDown(
        100, 100,
        'select',
        false,
        [],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.state.selectedNotes.size).toBe(0);
    });

    it('keeps selection when clicking empty space with shift', () => {
      state.selectedNotes.add('some-note');
      const findNote = createFindNoteStub(null);

      const result = handleMouseDown(
        100, 100,
        'select',
        true, // shift key
        [],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.state.selectedNotes.has('some-note')).toBe(true);
    });

    it('adds to selection when clicking note with shift', () => {
      const note1 = createTestNote({ id: 'note-1' });
      const note2 = createTestNote({ id: 'note-2', start: 200 });
      state.selectedNotes.add('note-1');
      const findNote = createFindNoteStub(note2);

      const result = handleMouseDown(
        210, 100,
        'select',
        true,
        [note1, note2],
        state,
        config,
        findNote,
        snapToGrid
      );

      expect(result.state.selectedNotes.has('note-1')).toBe(true);
      expect(result.state.selectedNotes.has('note-2')).toBe(true);
    });
  });
});

// ============================================================================
// handleMouseMove Tests
// ============================================================================

describe('handleMouseMove', () => {
  let config: MouseHandlerConfig;
  let snapToGrid: (value: number) => number;

  beforeEach(() => {
    config = createTestConfig();
    snapToGrid = createSnapStub(10);
  });

  it('updates isNearNoteEdge when hovering near edge in select mode', () => {
    const note = createTestNote({ start: 100, duration: 40 }); // edge at 140
    const findNote = createFindNoteStub(note);
    const state = createInitialMouseState();

    const result = handleMouseMove(
      138, 100, // near edge
      'select',
      [note],
      state,
      config,
      findNote,
      snapToGrid
    );

    expect(result.state.isNearNoteEdge).toBe(true);
    expect(result.needsRedraw).toBe(true);
  });

  it('moves selected notes when dragging', () => {
    const note = createTestNote({ id: 'note-1', start: 100, duration: 40 });
    const findNote = createFindNoteStub(null);
    const state: MouseState = {
      ...createInitialMouseState(),
      isDragging: true,
      draggedNoteId: 'note-1',
      selectedNotes: new Set(['note-1']),
      noteOffsetX: -10, // clicked 10px into the note
      noteOffsetY: 0,
    };

    const result = handleMouseMove(
      160, 100, // new position
      'select',
      [note],
      state,
      config,
      findNote,
      snapToGrid
    );

    expect(result.notesChanged).toBe(true);
    expect(result.notes[0].start).toBe(150); // 160 + (-10) = 150, snapped
  });

  it('resizes note when in resize mode', () => {
    const note = createTestNote({ id: 'note-1', start: 100, duration: 40 });
    const findNote = createFindNoteStub(null);
    const state: MouseState = {
      ...createInitialMouseState(),
      isResizing: true,
      resizedNoteId: 'note-1',
      creationStartTime: 100,
    };

    const result = handleMouseMove(
      200, 100, // new end position
      'select',
      [note],
      state,
      config,
      findNote,
      snapToGrid
    );

    expect(result.notesChanged).toBe(true);
    expect(result.notes[0].duration).toBeGreaterThan(40);
  });
});

// ============================================================================
// handleMouseUp Tests
// ============================================================================

describe('handleMouseUp', () => {
  let config: MouseHandlerConfig;

  beforeEach(() => {
    config = createTestConfig();
  });

  it('resets all interaction states', () => {
    const state: MouseState = {
      ...createInitialMouseState(),
      isDragging: true,
      isResizing: true,
      isNearNoteEdge: true,
      isCreatingNote: true,
      draggedNoteId: 'note-1',
      resizedNoteId: 'note-2',
    };

    const result = handleMouseUp([], state, config);

    expect(result.state.isDragging).toBe(false);
    expect(result.state.isResizing).toBe(false);
    expect(result.state.isNearNoteEdge).toBe(false);
    expect(result.state.isCreatingNote).toBe(false);
    expect(result.state.draggedNoteId).toBeNull();
    expect(result.state.resizedNoteId).toBeNull();
  });

  it('removes too-small notes created by accidental clicks', () => {
    const tinyNote = createTestNote({
      id: 'tiny-note',
      start: 100,
      duration: 2, // very small
    });

    const state: MouseState = {
      ...createInitialMouseState(),
      isCreatingNote: true,
      resizedNoteId: 'tiny-note',
    };

    const result = handleMouseUp([tinyNote], state, config);

    expect(result.notes.length).toBe(0);
    expect(result.notesChanged).toBe(true);
  });

  it('keeps normally-sized created notes', () => {
    const normalNote = createTestNote({
      id: 'normal-note',
      start: 100,
      duration: 40, // normal size
    });

    const state: MouseState = {
      ...createInitialMouseState(),
      isCreatingNote: true,
      resizedNoteId: 'normal-note',
    };

    const result = handleMouseUp([normalNote], state, config);

    expect(result.notes.length).toBe(1);
    expect(result.notesChanged).toBe(false);
  });
});
