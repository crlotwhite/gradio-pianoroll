/**
 * Mouse Handler Utilities for Piano Roll Grid
 *
 * This module provides mouse event handling logic extracted from GridComponent.
 * It manages note creation, selection, dragging, and resizing operations.
 *
 * @module mouseHandler
 */

import { NOTE_HEIGHT, TOTAL_NOTES, DEFAULT_VELOCITY, DEFAULT_LYRIC } from './constants';
import { getGridSizeFromSnap, getInitialNoteDuration, getMinimumNoteSize, snapDurationToGrid } from './snapUtils';
import { calculateAllTimingData, flicksToPixels, getExactNoteFlicks, pixelsToFlicks } from './flicks';
import { yToPitch, pitchToY, clampPitch, calculateDragPitch } from './coordinateUtils';
import { createLogger } from './logger';
import type { Note } from '../types';

const log = createLogger('MouseHandler');

// ============================================================================
// Types
// ============================================================================

/**
 * Edit modes available in the piano roll.
 */
export type EditMode = 'draw' | 'select' | 'erase';

/**
 * Current interaction state (what action is being performed).
 */
export type InteractionMode = 'none' | 'creating' | 'dragging' | 'resizing';

/**
 * Configuration for mouse handler operations.
 */
export interface MouseHandlerConfig {
  /** Pixels per beat (horizontal zoom level) */
  pixelsPerBeat: number;
  /** Tempo in BPM */
  tempo: number;
  /** Audio sample rate */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
  /** Current snap setting (e.g., "1/4", "1/8", "none") */
  snapSetting: string;
  /** Horizontal scroll offset */
  horizontalScroll: number;
  /** Vertical scroll offset */
  verticalScroll: number;
}

/**
 * State maintained during mouse interactions.
 */
export interface MouseState {
  /** Whether a drag operation is in progress */
  isDragging: boolean;
  /** Whether a resize operation is in progress */
  isResizing: boolean;
  /** Whether a new note is being created */
  isCreatingNote: boolean;
  /** Set of selected note IDs */
  selectedNotes: Set<string>;
  /** X coordinate where drag started */
  dragStartX: number;
  /** Y coordinate where drag started */
  dragStartY: number;
  /** Last recorded mouse X coordinate */
  lastMouseX: number;
  /** Last recorded mouse Y coordinate */
  lastMouseY: number;
  /** ID of note being dragged (null if none) */
  draggedNoteId: string | null;
  /** ID of note being resized (null if none) */
  resizedNoteId: string | null;
  /** Start time (pixels) when creating a note */
  creationStartTime: number;
  /** Pitch when creating a note */
  creationPitch: number;
  /** Offset from mouse to note start X for natural dragging */
  noteOffsetX: number;
  /** Offset from mouse to note start Y for natural dragging */
  noteOffsetY: number;
  /** Whether mouse is near a note edge (for resize cursor) */
  isNearNoteEdge: boolean;
}

/**
 * Result of a mouse down operation.
 */
export interface MouseDownResult {
  /** Updated notes array */
  notes: Note[];
  /** Updated mouse state */
  state: MouseState;
  /** Whether notes were changed */
  notesChanged: boolean;
}

/**
 * Result of a mouse move operation.
 */
export interface MouseMoveResult {
  /** Updated notes array */
  notes: Note[];
  /** Updated mouse state */
  state: MouseState;
  /** Whether notes were changed */
  notesChanged: boolean;
  /** Whether the grid needs to be redrawn */
  needsRedraw: boolean;
}

/**
 * Result of a mouse up operation.
 */
export interface MouseUpResult {
  /** Updated notes array */
  notes: Note[];
  /** Updated mouse state */
  state: MouseState;
  /** Whether notes were changed */
  notesChanged: boolean;
}

/**
 * Callback to find a note at a given position.
 */
export type FindNoteCallback = (x: number, y: number) => Note | null;

/**
 * Callback to snap a value to the grid.
 */
export type SnapToGridCallback = (value: number) => number;

// ============================================================================
// State Factory
// ============================================================================

/**
 * Create initial mouse state.
 *
 * @returns A fresh MouseState object with default values
 */
export function createInitialMouseState(): MouseState {
  return {
    isDragging: false,
    isResizing: false,
    isCreatingNote: false,
    selectedNotes: new Set(),
    dragStartX: 0,
    dragStartY: 0,
    lastMouseX: 0,
    lastMouseY: 0,
    draggedNoteId: null,
    resizedNoteId: null,
    creationStartTime: 0,
    creationPitch: 0,
    noteOffsetX: 0,
    noteOffsetY: 0,
    isNearNoteEdge: false,
  };
}

// ============================================================================
// Edge Detection
// ============================================================================

/**
 * Calculate the edge detection threshold based on zoom level.
 *
 * @param pixelsPerBeat - Current pixels per beat
 * @returns Threshold in pixels for detecting note edges
 */
export function getEdgeDetectionThreshold(pixelsPerBeat: number): number {
  return Math.max(5, Math.min(15, pixelsPerBeat / 8));
}

/**
 * Check if a position is near the edge of a note (for resize detection).
 *
 * @param x - X coordinate in world space
 * @param note - The note to check against
 * @param pixelsPerBeat - Current pixels per beat
 * @returns True if x is near the right edge of the note
 */
export function isNearNoteEdge(x: number, note: Note, pixelsPerBeat: number): boolean {
  const noteEndX = note.start + note.duration;
  const threshold = getEdgeDetectionThreshold(pixelsPerBeat);
  return Math.abs(x - noteEndX) < threshold;
}

// ============================================================================
// Note Creation
// ============================================================================

/**
 * Create a new note at the specified position.
 *
 * @param time - Start time in pixels
 * @param pitch - MIDI pitch (0-127)
 * @param config - Mouse handler configuration
 * @returns A new Note object with all timing data calculated
 */
export function createNote(
  time: number,
  pitch: number,
  config: MouseHandlerConfig
): Note {
  const { pixelsPerBeat, tempo, sampleRate, ppqn, snapSetting } = config;

  // Calculate initial note duration based on snap setting
  const initialDuration = getInitialNoteDuration(snapSetting, pixelsPerBeat);

  // Calculate timing data for start position and duration
  const startTiming = calculateAllTimingData(time, pixelsPerBeat, tempo, sampleRate, ppqn);
  const durationTiming = calculateAllTimingData(initialDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

  return {
    id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
    start: time,
    duration: initialDuration,
    pitch: clampPitch(pitch),
    velocity: DEFAULT_VELOCITY,
    lyric: DEFAULT_LYRIC,
    startFlicks: startTiming.flicks,
    durationFlicks: durationTiming.flicks,
    startSeconds: startTiming.seconds,
    durationSeconds: durationTiming.seconds,
    endSeconds: startTiming.seconds + durationTiming.seconds,
    startBeats: startTiming.beats,
    durationBeats: durationTiming.beats,
    startTicks: startTiming.ticks,
    durationTicks: durationTiming.ticks,
    startSample: startTiming.samples,
    durationSamples: durationTiming.samples,
  };
}

// ============================================================================
// Mouse Down Handler
// ============================================================================

/**
 * Handle mouse down event on the piano roll grid.
 *
 * @param x - X coordinate in world space (screen + scroll)
 * @param y - Y coordinate in world space (screen + scroll)
 * @param editMode - Current edit mode
 * @param shiftKey - Whether shift key is pressed
 * @param notes - Current notes array
 * @param state - Current mouse state
 * @param config - Mouse handler configuration
 * @param findNote - Callback to find note at position
 * @param snapToGrid - Callback to snap value to grid
 * @returns Result containing updated notes and state
 */
export function handleMouseDown(
  x: number,
  y: number,
  editMode: EditMode,
  shiftKey: boolean,
  notes: Note[],
  state: MouseState,
  config: MouseHandlerConfig,
  findNote: FindNoteCallback,
  snapToGrid: SnapToGridCallback
): MouseDownResult {
  log.debug('Mouse down at', x, y, 'mode:', editMode);

  // Clone state to avoid mutation
  const newState: MouseState = {
    ...state,
    dragStartX: x,
    dragStartY: y,
    lastMouseX: x,
    lastMouseY: y,
    noteOffsetX: 0,
    noteOffsetY: 0,
  };

  let newNotes = [...notes];
  let notesChanged = false;

  // Find note at click position
  const clickedNote = findNote(x, y);
  log.debug('Clicked note:', clickedNote?.id ?? 'none');

  if (editMode === 'draw' && !clickedNote) {
    // Create new note in draw mode
    const time = snapToGrid(x);
    const { pitch: clickedPitch } = yToPitch(y);

    newState.creationStartTime = time;
    newState.creationPitch = clampPitch(clickedPitch);

    const newNote = createNote(time, newState.creationPitch, config);
    newNotes = [...newNotes, newNote];

    newState.selectedNotes = new Set([newNote.id]);
    newState.resizedNoteId = newNote.id;
    newState.isCreatingNote = true;
    newState.isResizing = true;
    notesChanged = true;

    log.debug('Created new note:', newNote.id);
  } else if (editMode === 'erase' && clickedNote) {
    // Erase note
    newNotes = newNotes.filter((n) => n.id !== clickedNote.id);
    newState.selectedNotes = new Set(state.selectedNotes);
    newState.selectedNotes.delete(clickedNote.id);
    notesChanged = true;

    log.debug('Erased note:', clickedNote.id);
  } else if (editMode === 'select') {
    if (clickedNote) {
      // Check if clicking near edge for resize
      if (isNearNoteEdge(x, clickedNote, config.pixelsPerBeat)) {
        newState.isResizing = true;
        newState.resizedNoteId = clickedNote.id;
        newState.creationStartTime = clickedNote.start;
        log.debug('Started resizing note:', clickedNote.id);
      } else {
        // Select and drag
        if (!shiftKey) {
          if (!state.selectedNotes.has(clickedNote.id)) {
            newState.selectedNotes = new Set([clickedNote.id]);
          } else {
            newState.selectedNotes = new Set(state.selectedNotes);
          }
        } else {
          newState.selectedNotes = new Set(state.selectedNotes);
          newState.selectedNotes.add(clickedNote.id);
        }

        // Calculate offset for natural dragging
        newState.noteOffsetX = clickedNote.start - x;
        newState.noteOffsetY = pitchToY(clickedNote.pitch) - y;

        newState.isDragging = true;
        newState.draggedNoteId = clickedNote.id;
        log.debug('Started dragging note:', clickedNote.id);
      }
    } else {
      // Clicked empty space
      if (!shiftKey) {
        newState.selectedNotes = new Set();
      } else {
        newState.selectedNotes = new Set(state.selectedNotes);
      }
    }
  }

  return { notes: newNotes, state: newState, notesChanged };
}

// ============================================================================
// Mouse Move Handler
// ============================================================================

/**
 * Handle mouse move event on the piano roll grid.
 *
 * @param x - X coordinate in world space
 * @param y - Y coordinate in world space
 * @param editMode - Current edit mode
 * @param notes - Current notes array
 * @param state - Current mouse state
 * @param config - Mouse handler configuration
 * @param findNote - Callback to find note at position
 * @param snapToGrid - Callback to snap value to grid
 * @returns Result containing updated notes and state
 */
export function handleMouseMove(
  x: number,
  y: number,
  editMode: EditMode,
  notes: Note[],
  state: MouseState,
  config: MouseHandlerConfig,
  findNote: FindNoteCallback,
  snapToGrid: SnapToGridCallback
): MouseMoveResult {
  const { pixelsPerBeat, tempo, sampleRate, ppqn, snapSetting } = config;

  // Clone state
  const newState: MouseState = {
    ...state,
    lastMouseX: x,
    lastMouseY: y,
    selectedNotes: new Set(state.selectedNotes),
  };

  let newNotes = notes;
  let notesChanged = false;
  let needsRedraw = false;

  // Check for resize cursor in select mode when not dragging/resizing
  if (editMode === 'select' && !state.isDragging && !state.isResizing) {
    const hoveredNote = findNote(x, y);
    if (hoveredNote) {
      newState.isNearNoteEdge = isNearNoteEdge(x, hoveredNote, pixelsPerBeat);
    } else {
      newState.isNearNoteEdge = false;
    }
    if (newState.isNearNoteEdge !== state.isNearNoteEdge) {
      needsRedraw = true;
    }
  }

  // Handle dragging
  if (state.isDragging && state.draggedNoteId && editMode === 'select') {
    newNotes = notes.map((note) => {
      if (newState.selectedNotes.has(note.id)) {
        // Calculate new position with offset
        let newStart = x + state.noteOffsetX;
        let newPitch = calculateDragPitch(y, state.noteOffsetY);

        // Snap to grid
        newStart = snapToGrid(newStart);
        newStart = Math.max(0, newStart);

        // Calculate all timing data for new start
        const newStartTiming = calculateAllTimingData(newStart, pixelsPerBeat, tempo, sampleRate, ppqn);

        return {
          ...note,
          start: newStart,
          pitch: newPitch,
          startFlicks: newStartTiming.flicks,
          startSeconds: newStartTiming.seconds,
          startBeats: newStartTiming.beats,
          startTicks: newStartTiming.ticks,
          startSample: newStartTiming.samples,
          endSeconds: newStartTiming.seconds + (note.durationSeconds || 0),
        };
      }
      return note;
    });
    notesChanged = true;
    needsRedraw = true;
  }

  // Handle resizing
  if (state.isResizing && state.resizedNoteId) {
    newNotes = notes.map((note) => {
      if (note.id === state.resizedNoteId) {
        const gridSize = getGridSizeFromSnap(snapSetting, pixelsPerBeat);
        const width = Math.max(gridSize, x - state.creationStartTime);
        const newDuration = snapDurationToGrid(width, snapSetting, pixelsPerBeat);

        const newDurationTiming = calculateAllTimingData(newDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

        return {
          ...note,
          duration: newDuration,
          durationFlicks: newDurationTiming.flicks,
          durationSeconds: newDurationTiming.seconds,
          durationBeats: newDurationTiming.beats,
          durationTicks: newDurationTiming.ticks,
          durationSamples: newDurationTiming.samples,
          endSeconds: (note.startSeconds || 0) + newDurationTiming.seconds,
        };
      }
      return note;
    });
    notesChanged = true;
    needsRedraw = true;
  }

  return { notes: newNotes, state: newState, notesChanged, needsRedraw };
}

// ============================================================================
// Mouse Up Handler
// ============================================================================

/**
 * Handle mouse up event on the piano roll grid.
 *
 * @param notes - Current notes array
 * @param state - Current mouse state
 * @param config - Mouse handler configuration
 * @returns Result containing updated notes and state
 */
export function handleMouseUp(
  notes: Note[],
  state: MouseState,
  config: MouseHandlerConfig
): MouseUpResult {
  const { snapSetting, pixelsPerBeat } = config;

  let newNotes = [...notes];
  let notesChanged = false;

  // Clone state
  const newState: MouseState = {
    ...state,
    selectedNotes: new Set(state.selectedNotes),
  };

  // Validate created note size
  if (state.isCreatingNote && state.resizedNoteId) {
    const createdNote = newNotes.find((n) => n.id === state.resizedNoteId);
    const minimumNoteSize = getMinimumNoteSize(snapSetting, pixelsPerBeat);

    if (createdNote && createdNote.duration < minimumNoteSize) {
      // Remove note that is too small (accidental click)
      newNotes = newNotes.filter((n) => n.id !== state.resizedNoteId);
      notesChanged = true;
      log.debug('Removed note that was too small:', state.resizedNoteId);
    }
  }

  // Reset interaction states
  newState.isDragging = false;
  newState.isResizing = false;
  newState.isNearNoteEdge = false;
  newState.isCreatingNote = false;
  newState.draggedNoteId = null;
  newState.resizedNoteId = null;

  return { notes: newNotes, state: newState, notesChanged };
}
