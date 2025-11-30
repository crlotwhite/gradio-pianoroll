/**
 * NotesLayer - Renders piano roll notes with their properties
 *
 * This layer uses noteRenderer utilities for the actual note drawing,
 * managing the notes collection and selection state.
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext, Note } from '../../types';
import {
  renderNotes,
  findNotesAtPosition as findNotesAtPos,
  DEFAULT_NOTE_CONFIG,
  type NoteRenderConfig,
  type NoteRenderContext,
} from '../noteRenderer';

export class NotesLayer extends BaseLayer {
  private notes: Note[] = [];
  private selectedNotes: Set<string> = new Set();
  private config: NoteRenderConfig = DEFAULT_NOTE_CONFIG;

  constructor() {
    super('notes', LayerZIndex.NOTES);
  }

  /**
   * Update the notes data.
   */
  setNotes(notes: Note[]): void {
    this.notes = notes;
  }

  /**
   * Update selected notes.
   */
  setSelectedNotes(selectedNotes: Set<string>): void {
    this.selectedNotes = selectedNotes;
  }

  /**
   * Update render configuration.
   */
  setConfig(config: Partial<NoteRenderConfig>): void {
    this.config = { ...this.config, ...config };
  }

  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, verticalScroll } = context;

    // Create render context for noteRenderer
    const renderContext: NoteRenderContext = {
      ctx,
      width,
      height,
      horizontalScroll,
      verticalScroll,
    };

    // Delegate to noteRenderer utility
    renderNotes(this.notes, renderContext, this.selectedNotes, this.config);
  }

  /**
   * Find notes at a screen position.
   */
  findNotesAtPosition(
    x: number,
    y: number,
    horizontalScroll: number,
    verticalScroll: number
  ): Note[] {
    return findNotesAtPos(this.notes, x, y, horizontalScroll, verticalScroll);
  }

  /**
   * Get all notes.
   */
  getNotes(): Note[] {
    return this.notes;
  }

  /**
   * Get selected notes.
   */
  getSelectedNotes(): Set<string> {
    return this.selectedNotes;
  }
}