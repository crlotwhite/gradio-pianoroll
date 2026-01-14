/**
 * Playback Controller for Piano Roll
 *
 * This module handles all playback-related logic including
 * play, pause, stop, seek operations for both frontend and backend audio.
 *
 * Separated from PianoRoll.svelte for better maintainability.
 */

import { createLogger } from '../../utils/logger';
import type { Note } from '../../types';

const log = createLogger('PlaybackController');

/**
 * Audio source type.
 */
export type AudioSourceType = 'frontend' | 'backend';

/**
 * Playback state interface.
 */
export interface PlaybackState {
  isPlaying: boolean;
  isRendering: boolean;
  currentFlicks: number;
  useBackendAudio: boolean;
}

/**
 * Playback options.
 */
export interface PlaybackOptions {
  /** Tempo in BPM */
  tempo: number;
  /** Audio data from backend (base64) */
  audioData: string | null;
  /** Whether to use backend audio */
  useBackendAudio: boolean;
  /** Component element ID */
  elemId: string;
}

/**
 * Playback callback definitions.
 */
export interface PlaybackCallbacks {
  /** Called when play starts */
  onPlay: (payload: PlaybackEventPayload) => void;
  /** Called when playback pauses */
  onPause: (payload: PlaybackEventPayload) => void;
  /** Called when playback stops */
  onStop: (payload: PlaybackEventPayload) => void;
  /** Called when playhead position updates */
  onPositionUpdate: (flicks: number) => void;
}

/**
 * Payload for playback events.
 */
export interface PlaybackEventPayload {
  currentPosition: number;
  notes: Note[];
  tempo: number;
  useBackendAudio: boolean;
}

/**
 * PlaybackController class
 *
 * Manages playback state and coordinates between frontend and backend audio sources.
 */
export class PlaybackController {
  private state: PlaybackState;
  private options: PlaybackOptions;
  private callbacks: PlaybackCallbacks;
  private animationFrameId: number | null = null;
  private lastUpdateTime: number = 0;

  constructor(options: PlaybackOptions, callbacks: PlaybackCallbacks) {
    this.options = options;
    this.callbacks = callbacks;
    this.state = {
      isPlaying: false,
      isRendering: false,
      currentFlicks: 0,
      useBackendAudio: options.useBackendAudio,
    };
  }

  /**
   * Get current playback state.
   */
  getState(): Readonly<PlaybackState> {
    return this.state;
  }

  /**
   * Get current position in flicks.
   */
  getCurrentPosition(): number {
    return this.state.currentFlicks;
  }

  /**
   * Set current position in flicks.
   */
  setPosition(flicks: number): void {
    this.state.currentFlicks = Math.max(0, flicks);
    this.callbacks.onPositionUpdate(this.state.currentFlicks);
  }

  /**
   * Update options (e.g., when props change).
   */
  updateOptions(options: Partial<PlaybackOptions>): void {
    this.options = { ...this.options, ...options };
  }

  /**
   * Start playback.
   */
  play(notes: Note[]): void {
    if (this.state.isPlaying) {
      log.debug('Already playing, ignoring play request');
      return;
    }

    log.debug('Play requested', {
      useBackendAudio: this.options.useBackendAudio,
      hasAudioData: !!this.options.audioData,
    });

    const payload: PlaybackEventPayload = {
      currentPosition: this.state.currentFlicks,
      notes,
      tempo: this.options.tempo,
      useBackendAudio: this.options.useBackendAudio,
    };

    this.callbacks.onPlay(payload);
    this.state.isPlaying = true;
  }

  /**
   * Pause playback.
   */
  pause(): void {
    if (!this.state.isPlaying) {
      return;
    }

    log.debug('Pause requested');

    const payload: PlaybackEventPayload = {
      currentPosition: this.state.currentFlicks,
      notes: [],
      tempo: this.options.tempo,
      useBackendAudio: this.state.useBackendAudio,
    };

    this.callbacks.onPause(payload);
    this.state.isPlaying = false;
    this.stopAnimation();
  }

  /**
   * Stop playback and reset position.
   */
  stop(): void {
    log.debug('Stop requested');

    const payload: PlaybackEventPayload = {
      currentPosition: 0,
      notes: [],
      tempo: this.options.tempo,
      useBackendAudio: this.state.useBackendAudio,
    };

    this.callbacks.onStop(payload);
    this.state.isPlaying = false;
    this.state.currentFlicks = 0;
    this.stopAnimation();
    this.callbacks.onPositionUpdate(0);
  }

  /**
   * Toggle between play and pause.
   */
  toggle(notes: Note[]): void {
    if (this.state.isPlaying) {
      this.pause();
    } else {
      this.play(notes);
    }
  }

  /**
   * Seek to a specific position.
   */
  seek(flicks: number): void {
    this.state.currentFlicks = Math.max(0, flicks);
    this.callbacks.onPositionUpdate(this.state.currentFlicks);
  }

  /**
   * Start animation loop for playhead updates.
   */
  startAnimation(updateCallback: (flicks: number) => void): void {
    this.stopAnimation();

    const animate = (timestamp: number) => {
      if (!this.state.isPlaying) {
        return;
      }

      // Throttle updates to ~60fps
      if (timestamp - this.lastUpdateTime >= 16) {
        this.lastUpdateTime = timestamp;
        updateCallback(this.state.currentFlicks);
      }

      this.animationFrameId = requestAnimationFrame(animate);
    };

    this.animationFrameId = requestAnimationFrame(animate);
  }

  /**
   * Stop animation loop.
   */
  stopAnimation(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Set rendering state.
   */
  setRendering(isRendering: boolean): void {
    this.state.isRendering = isRendering;
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    this.stop();
    this.stopAnimation();
    this.state = {
      isPlaying: false,
      isRendering: false,
      currentFlicks: 0,
      useBackendAudio: false,
    };
  }
}

/**
 * Create a default playback controller instance.
 */
export function createPlaybackController(
  options: PlaybackOptions,
  callbacks: PlaybackCallbacks
): PlaybackController {
  return new PlaybackController(options, callbacks);
}
