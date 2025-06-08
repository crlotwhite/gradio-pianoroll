/**
 * NotesLayer - Renders piano roll notes with their properties
 */

import { BaseLayer, LayerZIndex } from '../LayerSystem';
import type { LayerRenderContext } from '../../types/layer';
import type { Note } from '../../types/layer';

export class NotesLayer extends BaseLayer {
  // Note colors and styling
  private readonly NOTE_COLOR = '#2196F3';
  private readonly NOTE_SELECTED_COLOR = '#03A9F4';
  private readonly LYRIC_COLOR = '#FFFFFF';

  private notes: Note[] = [];
  private selectedNotes: Set<string> = new Set();

  constructor() {
    super('notes', LayerZIndex.NOTES);
  }

  // Update the notes data
  setNotes(notes: Note[]): void {
    this.notes = notes;
  }

  // Update selected notes
  setSelectedNotes(selectedNotes: Set<string>): void {
    this.selectedNotes = selectedNotes;
  }

  render(context: LayerRenderContext): void {
    const { ctx, width, height, horizontalScroll, verticalScroll } = context;
    const NOTE_HEIGHT = 20;
    const TOTAL_NOTES = 128;

    // Draw notes
    for (const note of this.notes) {
      const noteX = note.start - horizontalScroll;
      const noteY = (TOTAL_NOTES - 1 - note.pitch) * NOTE_HEIGHT - verticalScroll;

      // Skip notes outside of visible area
      if (
        noteX + note.duration < 0 ||
        noteX > width ||
        noteY + NOTE_HEIGHT < 0 ||
        noteY > height
      ) {
        continue;
      }

      // Draw note rectangle
      ctx.fillStyle = this.selectedNotes.has(note.id) ? this.NOTE_SELECTED_COLOR : this.NOTE_COLOR;
      ctx.fillRect(noteX, noteY, note.duration, NOTE_HEIGHT);

      // Draw border
      ctx.strokeStyle = '#1a1a1a';
      ctx.lineWidth = 1;
      ctx.strokeRect(noteX, noteY, note.duration, NOTE_HEIGHT);

      // Draw velocity indicator (brightness of note)
      const velocityHeight = (NOTE_HEIGHT - 4) * (note.velocity / 127);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.fillRect(noteX + 2, noteY + 2 + (NOTE_HEIGHT - 4 - velocityHeight), note.duration - 4, velocityHeight);

      // Draw lyric text if present and note is wide enough
      if (note.lyric && note.duration > 20) {
        ctx.fillStyle = this.LYRIC_COLOR;
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Create text that fits within note width
        let text = note.lyric;

        // Add phoneme if available
        if (note.phoneme) {
          text += ` [${note.phoneme}]`;
        }

        const maxWidth = note.duration - 6;
        let textWidth = ctx.measureText(text).width;

        if (textWidth > maxWidth) {
          // Try to fit as much text as possible
          if (note.phoneme && text.length > note.lyric.length) {
            // If phoneme makes it too long, try without phoneme
            text = note.lyric;
            textWidth = ctx.measureText(text).width;

            if (textWidth > maxWidth) {
              text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
            }
          } else {
            text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
          }
        }

        ctx.fillText(text, noteX + note.duration / 2, noteY + NOTE_HEIGHT / 2);
      }
    }
  }

  // Helper method to find notes at a position
  findNotesAtPosition(x: number, y: number, horizontalScroll: number, verticalScroll: number): Note[] {
    const NOTE_HEIGHT = 20;
    const TOTAL_NOTES = 128;

    // Convert screen coordinates to world coordinates
    const worldX = x + horizontalScroll;
    const worldY = y + verticalScroll;

    return this.notes.filter(note => {
      const noteY = (TOTAL_NOTES - 1 - note.pitch) * NOTE_HEIGHT;
      return (
        worldX >= note.start &&
        worldX <= note.start + note.duration &&
        worldY >= noteY &&
        worldY <= noteY + NOTE_HEIGHT
      );
    });
  }

  // Helper method to get all notes
  getNotes(): Note[] {
    return this.notes;
  }

  // Helper method to get selected notes
  getSelectedNotes(): Set<string> {
    return this.selectedNotes;
  }
}