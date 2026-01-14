/**
 * Selection Manager for Piano Roll
 *
 * This module manages note selection state and selection operations.
 */

import { createLogger } from '../../../utils/logger';
import type { Note } from '../../../types';

const log = createLogger('SelectionManager');

/**
 * Selection state.
 */
export interface SelectionState {
  selectedNotes: Set<string>;
  anchorNoteId: string | null;
  selectionBox: SelectionBox | null;
}

/**
 * Selection box for marquee selection.
 */
export interface SelectionBox {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

/**
 * Selection options.
 */
export interface SelectionOptions {
  /** Whether to add to existing selection with shift key */
  addToSelection: boolean;
  /** Whether selection is exclusive (clear others) */
  exclusive: boolean;
}

/**
 * Selection result.
 */
export interface SelectionResult {
  selectedNoteIds: Set<string>;
  notesChanged: boolean;
}

/**
 * SelectionManager class
 *
 * Manages note selection state and provides methods for
 * selecting, deselecting, and querying selection state.
 */
export class SelectionManager {
  private state: SelectionState;

  constructor() {
    this.state = {
      selectedNotes: new Set(),
      anchorNoteId: null,
      selectionBox: null,
    };
  }

  /**
   * Get current selection state.
   */
  getState(): Readonly<SelectionState> {
    return this.state;
  }

  /**
   * Get set of selected note IDs.
   */
  getSelectedIds(): ReadonlySet<string> {
    return this.state.selectedNotes;
  }

  /**
   * Check if a note is selected.
   */
  isSelected(noteId: string): boolean {
    return this.state.selectedNotes.has(noteId);
  }

  /**
   * Check if any notes are selected.
   */
  hasSelection(): boolean {
    return this.state.selectedNotes.size > 0;
  }

  /**
   * Get the number of selected notes.
   */
  getSelectionCount(): number {
    return this.state.selectedNotes.size;
  }

  /**
   * Select a single note.
   */
  selectNote(noteId: string, options?: Partial<SelectionOptions>): SelectionResult {
    const opts: SelectionOptions = {
      addToSelection: false,
      exclusive: true,
      ...options,
    };

    const notesChanged = !this.state.selectedNotes.has(noteId);

    if (opts.exclusive && !opts.addToSelection) {
      this.state.selectedNotes = new Set([noteId]);
    } else {
      this.state.selectedNotes.add(noteId);
    }

    this.state.anchorNoteId = noteId;

    return {
      selectedNoteIds: this.state.selectedNotes,
      notesChanged,
    };
  }

  /**
   * Select multiple notes.
   */
  selectNotes(noteIds: string[], options?: Partial<SelectionOptions>): SelectionResult {
    const opts: SelectionOptions = {
      addToSelection: false,
      exclusive: true,
      ...options,
    };

    if (!opts.addToSelection && opts.exclusive) {
      this.state.selectedNotes = new Set(noteIds);
    } else {
      noteIds.forEach((id) => this.state.selectedNotes.add(id));
    }

    const notesChanged = noteIds.length > 0;

    if (noteIds.length > 0) {
      this.state.anchorNoteId = noteIds[0];
    }

    return {
      selectedNoteIds: this.state.selectedNotes,
      notesChanged,
    };
  }

  /**
   * Deselect a single note.
   */
  deselectNote(noteId: string): SelectionResult {
    const wasSelected = this.state.selectedNotes.has(noteId);
    this.state.selectedNotes.delete(noteId);

    if (this.state.anchorNoteId === noteId) {
      this.state.anchorNoteId = null;
    }

    return {
      selectedNoteIds: this.state.selectedNotes,
      notesChanged: wasSelected,
    };
  }

  /**
   * Deselect all notes.
   */
  deselectAll(): SelectionResult {
    const hadSelection = this.state.selectedNotes.size > 0;
    this.state.selectedNotes = new Set();
    this.state.anchorNoteId = null;
    this.state.selectionBox = null;

    return {
      selectedNoteIds: this.state.selectedNotes,
      notesChanged: hadSelection,
    };
  }

  /**
   * Toggle selection of a note.
   */
  toggleSelection(noteId: string): SelectionResult {
    if (this.state.selectedNotes.has(noteId)) {
      return this.deselectNote(noteId);
    } else {
      return this.selectNote(noteId, { addToSelection: true, exclusive: false });
    }
  }

  /**
   * Select notes within a rectangular region.
   */
  selectInBox(notes: Note[], box: SelectionBox): SelectionResult {
    const selectedIds = new Set<string>();

    notes.forEach((note) => {
      const noteTop = pitchToY(note.pitch);
      const noteBottom = noteTop + 20; // NOTE_HEIGHT

      // Check if note intersects with selection box
      if (
        note.start < box.endX &&
        note.start + note.duration > box.startX &&
        noteTop < box.endY &&
        noteBottom > box.startY
      ) {
        selectedIds.add(note.id);
      }
    });

    const notesChanged = selectedIds.size !== this.state.selectedNotes.size ||
      ![...selectedIds].every((id) => this.state.selectedNotes.has(id));

    this.state.selectedNotes = selectedIds;
    this.state.selectionBox = box;

    return {
      selectedNoteIds: this.state.selectedNotes,
      notesChanged,
    };
  }

  /**
   * Set the selection box (for marquee selection).
   */
  setSelectionBox(box: SelectionBox | null): void {
    this.state.selectionBox = box;
  }

  /**
   * Get the current selection box.
   */
  getSelectionBox(): SelectionBox | null {
    return this.state.selectionBox;
  }

  /**
   * Get selected notes from a list of all notes.
   */
  getSelectedNotes(notes: Note[]): Note[] {
    return notes.filter((note) => this.state.selectedNotes.has(note.id));
  }

  /**
   * Restore selection from saved state.
   */
  restoreSelection(savedState: SelectionState): void {
    this.state = {
      selectedNotes: new Set(savedState.selectedNotes),
      anchorNoteId: savedState.anchorNoteId,
      selectionBox: savedState.selectionBox ? { ...savedState.selectionBox } : null,
    };
  }

  /**
   * Get selection state for saving.
   */
  getSavedState(): SelectionState {
    return {
      selectedNotes: new Set(this.state.selectedNotes),
      anchorNoteId: this.state.anchorNoteId,
      selectionBox: this.state.selectionBox ? { ...this.state.selectionBox } : null,
    };
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    this.state.selectedNotes.clear();
    this.state.anchorNoteId = null;
    this.state.selectionBox = null;
  }
}

// Helper function for selection
function pitchToY(pitch: number): number {
  return (127 - pitch) * 20; // NOTE_HEIGHT = 20
}

/**
 * Create a selection manager instance.
 */
export function createSelectionManager(): SelectionManager {
  return new SelectionManager();
}
