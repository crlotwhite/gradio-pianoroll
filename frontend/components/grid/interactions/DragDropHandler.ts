/**
 * Drag and Drop Handler for Piano Roll
 *
 * This module handles drag and drop operations for notes including
 * moving, copying, and snapping to grid.
 */

import { createLogger } from '../../../utils/logger';
import { calculateAllTimingData } from '../../../utils/flicks';
import { clampPitch } from '../../../utils/coordinateUtils';
import type { Note, MouseHandlerConfig } from '../../../types';

const log = createLogger('DragDropHandler');

/**
 * Drag operation state.
 */
export interface DragState {
  isDragging: boolean;
  draggedNoteId: string | null;
  dragStartX: number;
  dragStartY: number;
  noteOffsetX: number;
  noteOffsetY: number;
  originalNote: Note | null;
}

/**
 * Drag operation result.
 */
export interface DragResult {
  notes: Note[];
  state: DragState;
  notesChanged: boolean;
}

/**
 * Drag options.
 */
export interface DragOptions {
  /** Whether to snap notes to grid during drag */
  snapToGrid: boolean;
  /** Whether to constrain to horizontal movement only */
  horizontalOnly: boolean;
  /** Whether to constrain to vertical movement only */
  verticalOnly: boolean;
  /** Whether this is a copy operation (not move) */
  isCopy: boolean;
}

/**
 * DragDropHandler class
 *
 * Handles drag and drop operations for notes with support for
 * grid snapping, pitch constraints, and copy operations.
 */
export class DragDropHandler {
  private config: MouseHandlerConfig;
  private state: DragState;
  private options: DragOptions;

  constructor(config: MouseHandlerConfig) {
    this.config = config;
    this.state = {
      isDragging: false,
      draggedNoteId: null,
      dragStartX: 0,
      dragStartY: 0,
      noteOffsetX: 0,
      noteOffsetY: 0,
      originalNote: null,
    };
    this.options = {
      snapToGrid: true,
      horizontalOnly: false,
      verticalOnly: false,
      isCopy: false,
    };
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<MouseHandlerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Update options.
   */
  updateOptions(options: Partial<DragOptions>): void {
    this.options = { ...this.options, ...options };
  }

  /**
   * Start a drag operation.
   */
  startDrag(note: Note, x: number, y: number): DragState {
    const state: DragState = {
      isDragging: true,
      draggedNoteId: note.id,
      dragStartX: x,
      dragStartY: y,
      noteOffsetX: note.start - x,
      noteOffsetY: (127 - note.pitch) * 20 - y,
      originalNote: { ...note },
    };

    this.state = state;
    log.debug('Started dragging note:', note.id);

    return state;
  }

  /**
   * Update drag position.
   */
  updateDrag(x: number, y: number, notes: Note[]): DragResult {
    if (!this.state.isDragging || !this.state.draggedNoteId) {
      return { notes, state: this.state, notesChanged: false };
    }

    let newX = x;
    let newY = y;

    // Apply constraints
    if (this.options.horizontalOnly) {
      newY = this.state.dragStartY;
    } else if (this.options.verticalOnly) {
      newX = this.state.dragStartX;
    }

    // Calculate new position
    let newStart = newX + this.state.noteOffsetX;
    let newPitch = clampPitch(127 - Math.floor((newY + this.state.noteOffsetY) / 20));

    // Apply grid snapping
    if (this.options.snapToGrid) {
      newStart = this.snapToGrid(newStart);
    }

    newStart = Math.max(0, newStart);

    // Calculate timing data
    const timing = calculateAllTimingData(
      newStart,
      this.config.pixelsPerBeat,
      this.config.tempo,
      this.config.sampleRate,
      this.config.ppqn
    );

    // Update notes
    const newNotes = notes.map((note) => {
      if (note.id === this.state.draggedNoteId) {
        return {
          ...note,
          start: newStart,
          pitch: newPitch,
          startFlicks: timing.flicks,
          startSeconds: timing.seconds,
          startBeats: timing.beats,
          startTicks: timing.ticks,
          startSample: timing.samples,
          endSeconds: timing.seconds + (note.durationSeconds || 0),
        };
      }
      return note;
    });

    log.debug('Dragging note to:', { start: newStart, pitch: newPitch });

    return { notes: newNotes, state: this.state, notesChanged: true };
  }

  /**
   * End drag operation.
   */
  endDrag(notes: Note[]): DragResult {
    const wasDragging = this.state.isDragging;

    // Reset state
    this.state = {
      isDragging: false,
      draggedNoteId: null,
      dragStartX: 0,
      dragStartY: 0,
      noteOffsetX: 0,
      noteOffsetY: 0,
      originalNote: null,
    };

    if (wasDragging) {
      log.debug('Ended drag operation');
    }

    return { notes, state: this.state, notesChanged: wasDragging };
  }

  /**
   * Cancel drag operation and restore original note position.
   */
  cancelDrag(notes: Note[]): { notes: Note[]; state: DragState; notesChanged: boolean } {
    if (!this.state.isDragging || !this.state.originalNote) {
      return { notes, state: this.state, notesChanged: false };
    }

    const restoredNotes = notes.map((note) => {
      if (note.id === this.state.draggedNoteId) {
        return { ...this.state.originalNote! };
      }
      return note;
    });

    const notesChanged = true;

    // Reset state
    this.state = {
      isDragging: false,
      draggedNoteId: null,
      dragStartX: 0,
      dragStartY: 0,
      noteOffsetX: 0,
      noteOffsetY: 0,
      originalNote: null,
    };

    log.debug('Cancelled drag operation, restored original note');

    return { notes: restoredNotes, state: this.state, notesChanged };
  }

  /**
   * Get current drag state.
   */
  getState(): Readonly<DragState> {
    return this.state;
  }

  /**
   * Check if currently dragging.
   */
  isDragging(): boolean {
    return this.state.isDragging;
  }

  /**
   * Get the ID of the note being dragged.
   */
  getDraggedNoteId(): string | null {
    return this.state.draggedNoteId;
  }

  /**
   * Snap a value to grid based on snap setting.
   */
  private snapToGrid(value: number): number {
    if (this.config.snapSetting === 'none') {
      return value;
    }

    const [_, denominator] = this.config.snapSetting.split('/').map(Number);
    const beatsPerSnap = 1 / denominator;
    const pixelsPerSnap = beatsPerSnap * this.config.pixelsPerBeat;

    return Math.round(value / pixelsPerSnap) * pixelsPerSnap;
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    this.state = {
      isDragging: false,
      draggedNoteId: null,
      dragStartX: 0,
      dragStartY: 0,
      noteOffsetX: 0,
      noteOffsetY: 0,
      originalNote: null,
    };
  }
}

/**
 * Create a drag and drop handler instance.
 */
export function createDragDropHandler(config: MouseHandlerConfig): DragDropHandler {
  return new DragDropHandler(config);
}
