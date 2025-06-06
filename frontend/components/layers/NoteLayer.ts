/**
 * NoteLayer - Handles note rendering and interaction
 */
import type { Layer, LayerEvent, Viewport, HitResult, LayerManager as ILayerManager, Note } from './types';
import { calculateAllTimingData, pixelsToFlicks, getExactNoteFlicks } from '../../utils/flicks';

export interface NoteLayerProps {
  id: string;
  name: string;
  notes?: Note[];
  tempo?: number;
  timeSignature?: { numerator: number; denominator: number };
  editMode?: string;
  snapSetting?: string;
  pixelsPerBeat?: number;
  sampleRate?: number;
  ppqn?: number;
  visible?: boolean;
  opacity?: number;
  zIndex?: number;
}

export class NoteLayer implements Layer {
  readonly id: string;
  readonly name: string;
  visible: boolean;
  opacity: number;
  zIndex: number;

  // Note-specific properties
  private notes: Note[] = [];
  private selectedNotes: Set<string> = new Set();
  private tempo: number = 120;
  private timeSignature = { numerator: 4, denominator: 4 };
  private editMode: string = 'select';
  private snapSetting: string = '1/4';
  private pixelsPerBeat: number = 80;
  private sampleRate: number = 44100;
  private ppqn: number = 480;

  // Interaction state
  private isDragging = false;
  private isResizing = false;
  private isCreatingNote = false;
  private draggedNoteId: string | null = null;
  private resizedNoteId: string | null = null;
  private creationStartTime = 0;
  private lastMouseX = 0;
  private lastMouseY = 0;
  private accumulatedDeltaX = 0;
  private accumulatedDeltaY = 0;

  // Visual constants
  private readonly NOTE_HEIGHT = 20;
  private readonly TOTAL_NOTES = 128;
  private readonly NOTE_COLOR = '#2196F3';
  private readonly NOTE_SELECTED_COLOR = '#03A9F4';
  private readonly LYRIC_COLOR = '#FFFFFF';

  // Event callbacks
  private onNotesChange?: (notes: Note[]) => void;
  private onLyricEdit?: (noteId: string, oldLyric: string, newLyric: string) => void;

  constructor(props: NoteLayerProps) {
    this.id = props.id;
    this.name = props.name;
    this.visible = props.visible ?? true;
    this.opacity = props.opacity ?? 1.0;
    this.zIndex = props.zIndex ?? 2;

    if (props.notes) this.notes = [...props.notes];
    if (props.tempo) this.tempo = props.tempo;
    if (props.timeSignature) this.timeSignature = props.timeSignature;
    if (props.editMode) this.editMode = props.editMode;
    if (props.snapSetting) this.snapSetting = props.snapSetting;
    if (props.pixelsPerBeat) this.pixelsPerBeat = props.pixelsPerBeat;
    if (props.sampleRate) this.sampleRate = props.sampleRate;
    if (props.ppqn) this.ppqn = props.ppqn;
  }

  // Update methods
  setNotes(notes: Note[]): void {
    console.log(`🎵 NoteLayer setNotes called with ${notes.length} notes`);
    this.notes = [...notes];

    // Log first few notes for debugging
    if (notes.length > 0) {
      console.log('🎵 First note:', notes[0]);
    }
  }

  setTempo(tempo: number): void {
    this.tempo = tempo;
  }

  setTimeSignature(timeSignature: { numerator: number; denominator: number }): void {
    this.timeSignature = timeSignature;
  }

  setEditMode(editMode: string): void {
    this.editMode = editMode;
    this.resetInteractionState();
  }

  setSnapSetting(snapSetting: string): void {
    this.snapSetting = snapSetting;
  }

  setPixelsPerBeat(pixelsPerBeat: number): void {
    this.pixelsPerBeat = pixelsPerBeat;
  }

  setSelectedNotes(selectedNotes: Set<string>): void {
    this.selectedNotes = new Set(selectedNotes);
  }

  getSelectedNotes(): Set<string> {
    return new Set(this.selectedNotes);
  }

  getNotes(): Note[] {
    return [...this.notes];
  }

  // Event callbacks
  setOnNotesChange(callback: (notes: Note[]) => void): void {
    this.onNotesChange = callback;
  }

  setOnLyricEdit(callback: (noteId: string, oldLyric: string, newLyric: string) => void): void {
    this.onLyricEdit = callback;
  }

    render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    // Draw notes
    for (const note of this.notes) {
      const noteX = note.start - viewport.horizontalScroll;
      const noteY = (this.TOTAL_NOTES - 1 - note.pitch) * this.NOTE_HEIGHT - viewport.verticalScroll;

      // Skip notes outside of visible area
      if (
        noteX + note.duration < 0 ||
        noteX > viewport.width ||
        noteY + this.NOTE_HEIGHT < 0 ||
        noteY > viewport.height
      ) {
        continue;
      }

      // Draw note rectangle
      ctx.fillStyle = this.selectedNotes.has(note.id) ? this.NOTE_SELECTED_COLOR : this.NOTE_COLOR;
      ctx.fillRect(noteX, noteY, note.duration, this.NOTE_HEIGHT);

      // Draw border
      ctx.strokeStyle = '#1a1a1a';
      ctx.lineWidth = 1;
      ctx.strokeRect(noteX, noteY, note.duration, this.NOTE_HEIGHT);

      // Draw velocity indicator
      const velocityHeight = (this.NOTE_HEIGHT - 4) * (note.velocity / 127);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.fillRect(noteX + 2, noteY + 2 + (this.NOTE_HEIGHT - 4 - velocityHeight), note.duration - 4, velocityHeight);

      // Draw lyric text if present and note is wide enough
      if (note.lyric && note.duration > 20) {
        ctx.fillStyle = this.LYRIC_COLOR;
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        let text = note.lyric;
        if (note.phoneme) {
          text += ` [${note.phoneme}]`;
        }

        const maxWidth = note.duration - 6;
        let textWidth = ctx.measureText(text).width;

        if (textWidth > maxWidth) {
          if (note.phoneme && text.length > note.lyric.length) {
            text = note.lyric;
            textWidth = ctx.measureText(text).width;
            if (textWidth > maxWidth) {
              text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
            }
          } else {
            text = text.substring(0, Math.floor(text.length * (maxWidth / textWidth))) + '...';
          }
        }

        ctx.fillText(text, noteX + note.duration / 2, noteY + this.NOTE_HEIGHT / 2);
      }
    }
  }

  hitTest(worldX: number, worldY: number, viewport: Viewport): HitResult | null {
    const note = this.findNoteAtPosition(worldX, worldY);
    if (note) {
      const noteEndX = note.start + note.duration;
      const edgeDetectionThreshold = Math.max(5, Math.min(15, this.pixelsPerBeat / 8));
      const isNearEdge = Math.abs(worldX - noteEndX) < edgeDetectionThreshold;

      console.log(`🎵 NoteLayer hit test success - note ${note.id} at (${worldX}, ${worldY}), isNearEdge: ${isNearEdge}`);

      return {
        layerId: this.id,
        elementId: note.id,
        elementType: isNearEdge ? 'note-edge' : 'note',
        data: note,
        cursor: isNearEdge && this.editMode === 'select' ? 'ew-resize' : 'default'
      };
    }

    console.log(`🎵 NoteLayer hit test failed at (${worldX}, ${worldY}) - no note found`);
    return null;
  }

  handleEvent(event: LayerEvent, viewport: Viewport): boolean {
    console.log(`🎵 NoteLayer handling ${event.type} event at (${event.worldX}, ${event.worldY})`);

    switch (event.type) {
      case 'mousedown':
        return this.handleMouseDown(event, viewport);
      case 'mousemove':
        return this.handleMouseMove(event, viewport);
      case 'mouseup':
        return this.handleMouseUp(event, viewport);
      case 'dblclick':
        return this.handleDoubleClick(event, viewport);
      default:
        return false;
    }
  }

  private handleMouseDown(event: LayerEvent, viewport: Viewport): boolean {
    const x = event.worldX;
    const y = event.worldY;

    console.log(`🎵 NoteLayer mousedown at (${x}, ${y}) in edit mode: ${this.editMode}`);

    this.lastMouseX = x;
    this.lastMouseY = y;
    this.accumulatedDeltaX = 0;
    this.accumulatedDeltaY = 0;

    const clickedNote = this.findNoteAtPosition(x, y);
    console.log(`🎵 Clicked note: ${clickedNote ? clickedNote.id : 'none'}`);

    if (this.editMode === 'draw' && !clickedNote) {
      console.log('🎵 Creating new note');
      return this.createNewNote(x, y);
    } else if (this.editMode === 'erase' && clickedNote) {
      console.log('🎵 Erasing note');
      return this.eraseNote(clickedNote);
    } else if (this.editMode === 'select' && clickedNote) {
      console.log('🎵 Selecting note');
      return this.selectNote(clickedNote, x, event.shiftKey || false);
    } else if (this.editMode === 'select' && !clickedNote) {
      console.log('🎵 Clearing selection');
      if (!event.shiftKey) {
        this.selectedNotes.clear();
      }
      return true;
    }

    console.log('🎵 No action taken');
    return false;
  }

  private handleMouseMove(event: LayerEvent, viewport: Viewport): boolean {
    const x = event.worldX;
    const y = event.worldY;
    const deltaX = x - this.lastMouseX;
    const deltaY = y - this.lastMouseY;

    this.lastMouseX = x;
    this.lastMouseY = y;

    if (this.isDragging && this.draggedNoteId) {
      return this.dragNote(deltaX, deltaY);
    } else if (this.isResizing && this.resizedNoteId) {
      return this.resizeNote(x);
    }

    return false;
  }

  private handleMouseUp(event: LayerEvent, viewport: Viewport): boolean {
    if (this.isCreatingNote && this.resizedNoteId) {
      this.finalizeNoteCreation();
    }

    this.resetInteractionState();
    return true;
  }

  private handleDoubleClick(event: LayerEvent, viewport: Viewport): boolean {
    const clickedNote = this.findNoteAtPosition(event.worldX, event.worldY);
    if (clickedNote && this.onLyricEdit) {
      const oldLyric = clickedNote.lyric || '';
      this.onLyricEdit(clickedNote.id, oldLyric, oldLyric);
      return true;
    }
    return false;
  }

  private createNewNote(x: number, y: number): boolean {
    const pitch = Math.floor(y / this.NOTE_HEIGHT);
    const time = this.snapToGrid(x);
    const creationPitch = this.TOTAL_NOTES - 1 - pitch;

    let initialDuration = this.pixelsPerBeat / 4;
    if (this.snapSetting !== 'none') {
      const [numerator, denominator] = this.snapSetting.split('/');
      if (numerator === '1' && denominator) {
        const divisionValue = parseInt(denominator);
        initialDuration = this.pixelsPerBeat / divisionValue;
      }
    } else {
      initialDuration = this.pixelsPerBeat / 8;
    }

    const startTiming = calculateAllTimingData(time, this.pixelsPerBeat, this.tempo, this.sampleRate, this.ppqn);
    const durationTiming = calculateAllTimingData(initialDuration, this.pixelsPerBeat, this.tempo, this.sampleRate, this.ppqn);

    const newNote: Note = {
      id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
      start: time,
      duration: initialDuration,
      pitch: creationPitch,
      velocity: 100,
      lyric: '라',
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
      durationSamples: durationTiming.samples
    };

    this.notes.push(newNote);
    this.selectedNotes = new Set([newNote.id]);
    this.resizedNoteId = newNote.id;
    this.isCreatingNote = true;
    this.isResizing = true;
    this.creationStartTime = time;

    this.notifyNotesChange();
    return true;
  }

  private eraseNote(note: Note): boolean {
    this.notes = this.notes.filter(n => n.id !== note.id);
    this.selectedNotes.delete(note.id);
    this.notifyNotesChange();
    return true;
  }

  private selectNote(note: Note, x: number, shiftKey: boolean): boolean {
    const noteEndX = note.start + note.duration;
    const edgeDetectionThreshold = Math.max(5, Math.min(15, this.pixelsPerBeat / 8));

    if (Math.abs(x - noteEndX) < edgeDetectionThreshold) {
      this.isResizing = true;
      this.resizedNoteId = note.id;
      this.creationStartTime = note.start;
    } else {
      if (!shiftKey) {
        if (!this.selectedNotes.has(note.id)) {
          this.selectedNotes = new Set([note.id]);
        }
      } else {
        this.selectedNotes.add(note.id);
      }
      this.isDragging = true;
      this.draggedNoteId = note.id;
    }
    return true;
  }

  private dragNote(deltaX: number, deltaY: number): boolean {
    let gridSize = this.pixelsPerBeat / 4;
    if (this.snapSetting !== 'none') {
      const [numerator, denominator] = this.snapSetting.split('/');
      if (numerator === '1' && denominator) {
        const divisionValue = parseInt(denominator);
        gridSize = this.pixelsPerBeat / divisionValue;
      }
    } else {
      gridSize = this.pixelsPerBeat / 32;
    }

    this.accumulatedDeltaX += deltaX;
    this.accumulatedDeltaY += deltaY;

    const gridMovementX = Math.floor(Math.abs(this.accumulatedDeltaX) / gridSize) * Math.sign(this.accumulatedDeltaX);
    const gridMovementY = Math.floor(Math.abs(this.accumulatedDeltaY) / this.NOTE_HEIGHT) * Math.sign(this.accumulatedDeltaY);

    if (gridMovementX !== 0 || gridMovementY !== 0) {
      this.notes = this.notes.map(note => {
        if (this.selectedNotes.has(note.id)) {
          const newStart = Math.max(0, note.start + (gridMovementX * gridSize));
          const newPitch = Math.max(0, Math.min(127, note.pitch - gridMovementY));

          const newStartTiming = calculateAllTimingData(newStart, this.pixelsPerBeat, this.tempo, this.sampleRate, this.ppqn);

          return {
            ...note,
            start: newStart,
            pitch: newPitch,
            startFlicks: newStartTiming.flicks,
            startSeconds: newStartTiming.seconds,
            startBeats: newStartTiming.beats,
            startTicks: newStartTiming.ticks,
            startSample: newStartTiming.samples,
            endSeconds: newStartTiming.seconds + (note.durationSeconds || 0)
          };
        }
        return note;
      });

      this.accumulatedDeltaX -= gridMovementX * gridSize;
      this.accumulatedDeltaY -= gridMovementY * this.NOTE_HEIGHT;

      this.notifyNotesChange();
    }

    return true;
  }

  private resizeNote(x: number): boolean {
    if (!this.resizedNoteId) return false;

    let gridSize = this.pixelsPerBeat / 4;
    if (this.snapSetting !== 'none') {
      const [numerator, denominator] = this.snapSetting.split('/');
      if (numerator === '1' && denominator) {
        const divisionValue = parseInt(denominator);
        gridSize = this.pixelsPerBeat / divisionValue;
      }
    } else {
      gridSize = this.pixelsPerBeat / 32;
    }

    this.notes = this.notes.map(note => {
      if (note.id === this.resizedNoteId) {
        const width = Math.max(gridSize, x - this.creationStartTime);
        const snappedWidth = this.snapSetting === 'none' ? width : Math.round(width / gridSize) * gridSize;
        const newDuration = Math.max(gridSize, snappedWidth);

        const newDurationTiming = calculateAllTimingData(newDuration, this.pixelsPerBeat, this.tempo, this.sampleRate, this.ppqn);

        return {
          ...note,
          duration: newDuration,
          durationFlicks: newDurationTiming.flicks,
          durationSeconds: newDurationTiming.seconds,
          durationBeats: newDurationTiming.beats,
          durationTicks: newDurationTiming.ticks,
          durationSamples: newDurationTiming.samples,
          endSeconds: (note.startSeconds || 0) + newDurationTiming.seconds
        };
      }
      return note;
    });

    this.notifyNotesChange();
    return true;
  }

  private finalizeNoteCreation(): void {
    if (!this.resizedNoteId) return;

    const createdNote = this.notes.find(note => note.id === this.resizedNoteId);
    if (createdNote) {
      let minimumNoteSize = this.pixelsPerBeat / 32;
      if (this.snapSetting !== 'none') {
        const [numerator, denominator] = this.snapSetting.split('/');
        if (numerator === '1' && denominator) {
          const divisionValue = parseInt(denominator);
          minimumNoteSize = (this.pixelsPerBeat / divisionValue) / 2;
        }
      }

      if (createdNote.duration < minimumNoteSize) {
        this.notes = this.notes.filter(note => note.id !== this.resizedNoteId);
        this.notifyNotesChange();
      }
    }

    this.isCreatingNote = false;
  }

  private resetInteractionState(): void {
    this.isDragging = false;
    this.isResizing = false;
    this.draggedNoteId = null;
    this.resizedNoteId = null;
    this.accumulatedDeltaX = 0;
    this.accumulatedDeltaY = 0;
  }

  private findNoteAtPosition(x: number, y: number): Note | null {
    const pitch = this.TOTAL_NOTES - 1 - Math.floor(y / this.NOTE_HEIGHT);

    return this.notes.find(note => {
      const noteY = (this.TOTAL_NOTES - 1 - note.pitch) * this.NOTE_HEIGHT;
      return (
        x >= note.start &&
        x <= note.start + note.duration &&
        y >= noteY &&
        y <= noteY + this.NOTE_HEIGHT
      );
    }) || null;
  }

  private snapToGrid(value: number): number {
    if (this.snapSetting === 'none') {
      return value;
    }

    try {
      const exactNoteFlicks = getExactNoteFlicks(this.snapSetting, this.tempo);
      const exactNotePixels = (exactNoteFlicks * this.pixelsPerBeat * this.tempo) / (60 * 705600000);
      return Math.round(value / exactNotePixels) * exactNotePixels;
    } catch (error) {
      console.warn(`Unknown snap setting: ${this.snapSetting}, using fallback calculation`);
      let divisionValue = 4;
      if (this.snapSetting !== 'none') {
        const [numerator, denominator] = this.snapSetting.split('/');
        if (numerator === '1' && denominator) {
          divisionValue = parseInt(denominator);
        }
      }
      const gridSize = this.pixelsPerBeat / divisionValue;
      return Math.round(value / gridSize) * gridSize;
    }
  }

  private notifyNotesChange(): void {
    if (this.onNotesChange) {
      this.onNotesChange([...this.notes]);
    }
  }

  dispose(): void {
    this.notes = [];
    this.selectedNotes.clear();
    this.resetInteractionState();
  }
}