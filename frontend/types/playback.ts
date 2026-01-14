/**
 * Playback-related type definitions for Piano Roll
 *
 * This module contains types for audio playback, playhead management,
 * and audio rendering.
 */

import type { PlayheadUpdateCallback } from './audio';

/**
 * Playback state for the piano roll.
 */
export interface PlaybackState {
  /** Whether audio is currently playing */
  isPlaying: boolean;
  /** Whether audio is currently rendering */
  isRendering: boolean;
  /** Current playhead position in flicks */
  currentFlicks: number;
}

/**
 * Audio source type.
 */
export type AudioSourceType = 'frontend' | 'backend';

/**
 * Playback control events.
 */
export type PlaybackEventType = 'play' | 'pause' | 'stop' | 'seek';

/**
 * Payload for playback control events.
 */
export interface PlaybackEventPayload {
  /** Current position in flicks */
  currentPosition: number;
  /** Target position for seek events (in flicks) */
  targetPosition?: number;
  /** Source type of the audio */
  audioSourceType: AudioSourceType;
}

/**
 * Audio rendering configuration.
 */
export interface AudioRenderConfig {
  /** Tempo in BPM */
  tempo: number;
  /** Audio sample rate in Hz */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
  /** Total length in beats to render */
  totalLengthInBeats: number;
  /** Pixels per beat (for visualization alignment) */
  pixelsPerBeat: number;
}

/**
 * Audio rendering result.
 */
export interface AudioRenderResult {
  /** The rendered audio buffer */
  buffer: AudioBuffer;
  /** Duration of the rendered audio in seconds */
  duration: number;
  /** Whether rendering was successful */
  success: boolean;
  /** Error message if rendering failed */
  error?: string;
}

/**
 * Audio playback engine interface.
 */
export interface AudioEngine {
  /** Initialize the audio context */
  initialize(): void;
  /** Render notes to an audio buffer */
  renderNotes(
    notes: import('./notes').Note[],
    tempo: number,
    totalLengthInBeats: number,
    pixelsPerBeat: number
  ): Promise<AudioBuffer>;
  /** Start playback */
  play(startPositionInFlicks?: number): void;
  /** Pause playback */
  pause(): void;
  /** Stop playback and reset */
  stop(): void;
  /** Seek to a specific position */
  seekToFlicks(flicks: number): void;
  /** Set callback for playhead updates */
  setPlayheadUpdateCallback(callback: PlayheadUpdateCallback): void;
  /** Get the rendered audio buffer */
  getRenderedBuffer(): AudioBuffer | null;
  /** Download audio as WAV file */
  downloadAudio(filename: string): void;
  /** Clean up resources */
  dispose(): void;
}

/**
 * Backend audio configuration.
 */
export interface BackendAudioConfig {
  /** Base64 encoded audio data */
  audioData: string | null;
  /** Whether to use backend audio */
  useBackendAudio: boolean;
}

/**
 * Waveform display configuration.
 */
export interface WaveformConfig {
  /** Waveform color */
  color: string;
  /** Waveform line width */
  lineWidth: number;
  /** Waveform opacity */
  opacity: number;
  /** Number of samples to display */
  sampleCount: number;
}
