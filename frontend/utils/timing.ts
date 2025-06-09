/**
 * Timing calculation utilities
 * Mirrors the timing_utils.py functionality from the backend
 */

import type { Note, TimingCalculationResult, TimingContext } from '../types/backend';

// Constants
const FLICKS_PER_SECOND = 705600000;

/**
 * Generate a unique note ID using the same algorithm as the frontend
 */
export function generateNoteId(): string {
  const timestamp = Date.now();  // Milliseconds
  const randomChars = Math.random().toString(36).substring(2, 7);
  return `note-${timestamp}-${randomChars}`;
}

/**
 * Convert pixels to flicks for accurate timing calculation
 */
export function pixelsToFlicks(pixels: number, pixelsPerBeat: number, tempo: number): number {
  return (pixels * 60 * FLICKS_PER_SECOND) / (pixelsPerBeat * tempo);
}

/**
 * Convert pixels to seconds for direct audio processing
 */
export function pixelsToSeconds(pixels: number, pixelsPerBeat: number, tempo: number): number {
  return (pixels * 60) / (pixelsPerBeat * tempo);
}

/**
 * Convert pixels to beats for musical accuracy
 */
export function pixelsToBeats(pixels: number, pixelsPerBeat: number): number {
  return pixels / pixelsPerBeat;
}

/**
 * Convert pixels to MIDI ticks for MIDI compatibility
 */
export function pixelsToTicks(pixels: number, pixelsPerBeat: number, ppqn: number = 480): number {
  const beats = pixelsToBeats(pixels, pixelsPerBeat);
  return Math.round(beats * ppqn);
}

/**
 * Convert pixels to audio samples for precise digital audio processing
 */
export function pixelsToSamples(pixels: number, pixelsPerBeat: number, tempo: number, sampleRate: number = 44100): number {
  const seconds = pixelsToSeconds(pixels, pixelsPerBeat, tempo);
  return Math.round(seconds * sampleRate);
}

/**
 * Calculate all timing representations for a given pixel value
 */
export function calculateAllTimingData(
  pixels: number, 
  pixelsPerBeat: number, 
  tempo: number,
  sampleRate: number = 44100, 
  ppqn: number = 480
): TimingCalculationResult {
  return {
    seconds: pixelsToSeconds(pixels, pixelsPerBeat, tempo),
    beats: pixelsToBeats(pixels, pixelsPerBeat),
    flicks: pixelsToFlicks(pixels, pixelsPerBeat, tempo),
    ticks: pixelsToTicks(pixels, pixelsPerBeat, ppqn),
    samples: pixelsToSamples(pixels, pixelsPerBeat, tempo, sampleRate)
  };
}

/**
 * Create a note with all timing data calculated from pixel values
 */
export function createNoteWithTiming(
  noteId: string,
  startPixels: number,
  durationPixels: number,
  pitch: number,
  velocity: number = 100,
  lyric: string = "",
  context: TimingContext = {
    pixels_per_beat: 80,
    tempo: 120,
    sample_rate: 44100,
    ppqn: 480
  }
): Note {
  const startTiming = calculateAllTimingData(startPixels, context.pixels_per_beat, context.tempo, context.sample_rate, context.ppqn);
  const durationTiming = calculateAllTimingData(durationPixels, context.pixels_per_beat, context.tempo, context.sample_rate, context.ppqn);

  return {
    id: noteId,
    start: startPixels,
    duration: durationPixels,
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
    pitch: pitch,
    velocity: velocity,
    lyric: lyric
  };
}

/**
 * Update note timing data when context changes
 */
export function updateNoteTiming(note: Note, context: TimingContext): Note {
  return createNoteWithTiming(
    note.id,
    note.start,
    note.duration,
    note.pitch,
    note.velocity,
    note.lyric || "",
    context
  );
}

/**
 * Batch update multiple notes' timing data
 */
export function updateNotesTiming(notes: Note[], context: TimingContext): Note[] {
  return notes.map(note => updateNoteTiming(note, context));
}

/**
 * Validate note data structure
 */
export function validateNote(note: any): note is Note {
  return (
    note &&
    typeof note === 'object' &&
    typeof note.id === 'string' &&
    typeof note.start === 'number' &&
    typeof note.duration === 'number' &&
    typeof note.pitch === 'number' &&
    typeof note.velocity === 'number'
  );
}

/**
 * Create a timing context from piano roll data
 */
export function createTimingContext(
  pixelsPerBeat: number = 80,
  tempo: number = 120,
  sampleRate: number = 44100,
  ppqn: number = 480
): TimingContext {
  return {
    pixels_per_beat: pixelsPerBeat,
    tempo: tempo,
    sample_rate: sampleRate,
    ppqn: ppqn
  };
}

/**
 * Convert timing context to display string
 */
export function formatTimingContext(context: TimingContext): string {
  return `${context.tempo}BPM, ${context.pixels_per_beat}px/beat, ${context.sample_rate}Hz, ${context.ppqn}PPQ`;
}

// Reverse conversion functions (from time units back to pixels)

/**
 * Convert seconds to pixels
 */
export function secondsToPixels(seconds: number, pixelsPerBeat: number, tempo: number): number {
  return (seconds * pixelsPerBeat * tempo) / 60;
}

/**
 * Convert beats to pixels
 */
export function beatsToPixels(beats: number, pixelsPerBeat: number): number {
  return beats * pixelsPerBeat;
}

/**
 * Convert MIDI ticks to pixels
 */
export function ticksToPixels(ticks: number, pixelsPerBeat: number, ppqn: number = 480): number {
  const beats = ticks / ppqn;
  return beatsToPixels(beats, pixelsPerBeat);
}

/**
 * Convert audio samples to pixels
 */
export function samplesToPixels(samples: number, pixelsPerBeat: number, tempo: number, sampleRate: number = 44100): number {
  const seconds = samples / sampleRate;
  return secondsToPixels(seconds, pixelsPerBeat, tempo);
} 