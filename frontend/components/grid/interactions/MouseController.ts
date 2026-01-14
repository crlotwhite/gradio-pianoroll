/**
 * Mouse Controller for Piano Roll Grid
 *
 * This module handles all mouse interaction logic for the piano roll grid
 * including clicking, dragging, and resizing notes.
 */

import { createLogger } from '../../../utils/logger';
import { NOTE_HEIGHT, TOTAL_NOTES, DEFAULT_VELOCITY, DEFAULT_LYRIC } from '../../../utils/constants';
import { yToPitch, clampPitch, pitchToY } from '../../../utils/coordinateUtils';
import { calculateAllTimingData, getExactNoteFlicks, flicksToPixels, pixelsToFlicks } from '../../../utils/flicks';
import type { Note, EditMode, MouseHandlerConfig, MouseState } from '../../../types';

const log = createLogger('MouseController');

/**
 * Mouse event result.
 */
export interface MouseEventResult {
  notes: Note[];
  state: MouseState;
  notesChanged: boolean;
  needsRedraw: boolean;
}

/**
 * Mouse controller configuration.
 */
export interface MouseControllerConfig {
  /** Pixels per beat (zoom level) */
  pixelsPerBeat: number;
  /** Tempo in BPM */
  tempo: number;
  /** Audio sample rate */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
  /** Current snap setting */
  snapSetting: string;
  /** Horizontal scroll offset */
  horizontalScroll: number;
  /** Vertical scroll offset */
  verticalScroll: number;
}

/**
 * Edge detection result.
 */
export interface EdgeDetectionResult {
  isNearEdge: boolean;
  edgePosition: number;
  threshold: number;
}

/**
 * MouseController class
 *
 * Handles all mouse interactions on the piano roll grid including
 * note selection, creation, dragging, resizing, and deletion.
 */
export class MouseController {
  private config: MouseControllerConfig;
  private editMode: EditMode = 'select';
  private shiftKey = false;

  constructor(config: MouseControllerConfig) {
    this.config = config;
  }

  /**
   * Update controller configuration.
   */
  updateConfig(config: Partial<MouseControllerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Set edit mode.
   */
  setEditMode(mode: EditMode): void {
    this.editMode = mode;
  }

  /**
   * Set shift key state.
   */
  setShiftKey(pressed: boolean): void {
    this.shiftKey = pressed;
  }

  /**
   * Handle mouse down event.
   */
  handleMouseDown(
    x: number,
    y: number,
    notes: Note[],
    state: MouseState,
    findNote: (x: number, y: number) => Note | null,
    snapToGrid: (value: number) => number
  ): MouseEventResult {
    const newState = { ...state };
    newState.dragStartX = x;
    newState.dragStartY = y;
    newState.lastMouseX = x;
    newState.lastMouseY = y;

    let newNotes = [...notes];
    let notesChanged = false;

    const clickedNote = findNote(x, y);

    if (this.editMode === 'draw' && !clickedNote) {
      // Create new note
      const snappedX = snapToGrid(x);
      const { pitch: clickedPitch } = yToPitch(y);

      newState.creationStartTime = snappedX;
      newState.creationPitch = clampPitch(clickedPitch);

      const newNote = this.createNote(snappedX, newState.creationPitch);
      newNotes = [...newNotes, newNote];

      newState.selectedNotes = new Set([newNote.id]);
      newState.resizedNoteId = newNote.id;
      newState.isCreatingNote = true;
      newState.isResizing = true;
      notesChanged = true;

      log.debug('Created new note:', newNote.id);
    } else if (this.editMode === 'erase' && clickedNote) {
      // Delete note
      newNotes = newNotes.filter((n) => n.id !== clickedNote.id);
      newState.selectedNotes = new Set(state.selectedNotes);
      newState.selectedNotes.delete(clickedNote.id);
      notesChanged = true;

      log.debug('Deleted note:', clickedNote.id);
    } else if (this.editMode === 'select') {
      if (clickedNote) {
        // Check if near edge for resize
        const edgeResult = this.detectEdge(x, y, clickedNote);
        if (edgeResult.isNearEdge) {
          newState.isResizing = true;
          newState.resizedNoteId = clickedNote.id;
          newState.creationStartTime = clickedNote.start;
          log.debug('Started resizing note:', clickedNote.id);
        } else {
          // Select and prepare for drag
          if (!this.shiftKey) {
            newState.selectedNotes = new Set([clickedNote.id]);
          } else {
            newState.selectedNotes = new Set(state.selectedNotes);
            newState.selectedNotes.add(clickedNote.id);
          }

          newState.noteOffsetX = clickedNote.start - x;
          newState.noteOffsetY = pitchToY(clickedNote.pitch) - y;
          newState.isDragging = true;
          newState.draggedNoteId = clickedNote.id;
          log.debug('Started dragging note:', clickedNote.id);
        }
      } else {
        // Clicked empty space - deselect
        if (!this.shiftKey) {
          newState.selectedNotes = new Set();
        }
      }
    }

    return { notes: newNotes, state: newState, notesChanged, needsRedraw: true };
  }

  /**
   * Handle mouse move event.
   */
  handleMouseMove(
    x: number,
    y: number,
    notes: Note[],
    state: MouseState,
    findNote: (x: number, y: number) => Note | null,
    snapToGrid: (value: number) => number
  ): MouseEventResult {
    const newState = { ...state };
    newState.lastMouseX = x;
    newState.lastMouseY = y;
    newState.selectedNotes = new Set(state.selectedNotes);

    let newNotes = notes;
    let notesChanged = false;
    let needsRedraw = false;

    // Check for resize cursor in select mode
    if (this.editMode === 'select' && !state.isDragging && !state.isResizing) {
      const hoveredNote = findNote(x, y);
      const edgeResult = hoveredNote ? this.detectEdge(x, y, hoveredNote) : null;
      newState.isNearNoteEdge = edgeResult?.isNearEdge ?? false;
      needsRedraw = true;
    }

    // Handle dragging
    if (state.isDragging && state.draggedNoteId) {
      newNotes = notes.map((note) => {
        if (newState.selectedNotes.has(note.id)) {
          let newStart = x + state.noteOffsetX;
          const newPitch = clampPitch(yToPitch(y).pitch);

          newStart = snapToGrid(newStart);
          newStart = Math.max(0, newStart);

          const timing = calculateAllTimingData(newStart, this.config.pixelsPerBeat, this.config.tempo, this.config.sampleRate, this.config.ppqn);

          return {
            ...note,
            start: newStart,
            pitch: newPitch,
            startFlicks: timing.flicks,
            startSeconds: timing.seconds,
            startBeats: timing.beats,
            startTicks: timing.ticks,
            startSample: timing.samples,
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
          const width = Math.max(this.config.pixelsPerBeat / 4, x - state.creationStartTime);
          const snappedDuration = snapToGrid(width);

          const timing = calculateAllTimingData(snappedDuration, this.config.pixelsPerBeat, this.config.tempo, this.config.sampleRate, this.config.ppqn);

          return {
            ...note,
            duration: snappedDuration,
            durationFlicks: timing.flicks,
            durationSeconds: timing.seconds,
            durationBeats: timing.beats,
            durationTicks: timing.ticks,
            durationSamples: timing.samples,
          };
        }
        return note;
      });
      notesChanged = true;
      needsRedraw = true;
    }

    return { notes: newNotes, state: newState, notesChanged, needsRedraw };
  }

  /**
   * Handle mouse up event.
   */
  handleMouseUp(
    notes: Note[],
    state: MouseState
  ): MouseEventResult {
    const newState = { ...state };
    newState.selectedNotes = new Set(state.selectedNotes);

    let newNotes = [...notes];
    let notesChanged = false;

    // Validate created note size
    if (state.isCreatingNote && state.resizedNoteId) {
      const createdNote = newNotes.find((n) => n.id === state.resizedNoteId);
      const minimumSize = this.config.pixelsPerBeat / 4;

      if (createdNote && createdNote.duration < minimumSize) {
        newNotes = newNotes.filter((n) => n.id !== state.resizedNoteId);
        notesChanged = true;
        log.debug('Removed note that was too small');
      }
    }

    // Reset states
    newState.isDragging = false;
    newState.isResizing = false;
    newState.isNearNoteEdge = false;
    newState.isCreatingNote = false;
    newState.draggedNoteId = null;
    newState.resizedNoteId = null;

    return { notes: newNotes, state: newState, notesChanged, needsRedraw: true };
  }

  /**
   * Create a new note at the specified position.
   */
  private createNote(time: number, pitch: number): Note {
    const noteFlicks = getExactNoteFlicks(this.config.snapSetting, this.config.tempo);
    const notePixels = flicksToPixels(noteFlicks, this.config.pixelsPerBeat, this.config.tempo);

    const startTiming = calculateAllTimingData(time, this.config.pixelsPerBeat, this.config.tempo, this.config.sampleRate, this.config.ppqn);
    const durationTiming = calculateAllTimingData(notePixels, this.config.pixelsPerBeat, this.config.tempo, this.config.sampleRate, this.config.ppqn);

    return {
      id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
      start: time,
      duration: notePixels,
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

  /**
   * Detect if mouse is near a note's edge.
   */
  private detectEdge(x: number, y: number, note: Note): EdgeDetectionResult {
    const threshold = Math.max(5, Math.min(15, this.config.pixelsPerBeat / 8));
    const noteEndX = note.start + note.duration;
    const isNearEdge = Math.abs(x - noteEndX) < threshold;

    return {
      isNearEdge,
      edgePosition: noteEndX,
      threshold,
    };
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    // No persistent resources to clean up
  }
}

/**
 * Create a mouse controller instance.
 */
export function createMouseController(config: MouseControllerConfig): MouseController {
  return new MouseController(config);
}
