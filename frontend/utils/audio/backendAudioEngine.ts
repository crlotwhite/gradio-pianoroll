/**
 * Backend Audio Adapter
 *
 * This module handles audio playback from backend-provided audio data
 * (e.g., base64 encoded audio strings).
 */

import { createLogger } from '../logger';

const log = createLogger('BackendAudioAdapter');

/**
 * Backend audio configuration.
 */
export interface BackendAudioConfig {
  /** Base64 encoded audio data */
  audioData: string | null;
  /** Whether to use backend audio */
  enabled: boolean;
}

/**
 * Backend audio state.
 */
export interface BackendAudioState {
  isInitialized: boolean;
  isDecoded: boolean;
  isPlaying: boolean;
  isPaused: boolean;
  duration: number;
  currentTime: number;
}

/**
 * Backend audio playback callbacks.
 */
export interface BackendAudioCallbacks {
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onEnded: () => void;
  onTimeUpdate: (currentTime: number) => void;
  onError: (error: Error) => void;
}

/**
 * BackendAudioAdapter class
 *
 * Manages audio playback from backend-provided audio sources.
 */
export class BackendAudioAdapter {
  private config: BackendAudioConfig;
  private callbacks: BackendAudioCallbacks;
  private state: BackendAudioState;
  private audioContext: AudioContext | null = null;
  private audioBuffer: AudioBuffer | null = null;
  private sourceNode: AudioBufferSourceNode | null = null;
  private startTime = 0;
  private pausedAt = 0;
  private animationFrameId: number | null = null;

  constructor(config: BackendAudioConfig, callbacks: BackendAudioCallbacks) {
    this.config = config;
    this.callbacks = callbacks;
    this.state = {
      isInitialized: false,
      isDecoded: false,
      isPlaying: false,
      isPaused: false,
      duration: 0,
      currentTime: 0,
    };
  }

  /**
   * Initialize the audio context.
   */
  async initialize(): Promise<void> {
    if (this.state.isInitialized) return;

    try {
      this.audioContext = new (window.AudioContext || (window as unknown).webkitAudioContext)();
      this.state.isInitialized = true;
      log.debug('Backend audio context initialized');
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to create audio context');
      log.error('Failed to initialize audio context:', err);
      this.callbacks.onError(err);
      throw err;
    }
  }

  /**
   * Decode backend audio data.
   */
  async decodeAudio(): Promise<AudioBuffer | null> {
    if (!this.config.audioData || !this.audioContext) {
      log.warn('Cannot decode: no audio data or context');
      return null;
    }

    try {
      // Convert base64 to array buffer
      const base64Data = this.config.audioData.split(',')[1] || this.config.audioData;
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const arrayBuffer = bytes.buffer;

      // Decode audio data
      this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.state.isDecoded = true;
      this.state.duration = this.audioBuffer.duration;

      log.debug('Backend audio decoded', { duration: this.state.duration });

      return this.audioBuffer;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to decode audio');
      log.error('Failed to decode audio:', err);
      this.callbacks.onError(err);
      return null;
    }
  }

  /**
   * Start playback.
   */
  play(offset: number = 0): void {
    if (!this.audioContext || !this.audioBuffer || this.state.isPlaying) return;

    // Resume context if suspended
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }

    // Create source node
    this.sourceNode = this.audioContext.createBufferSource();
    this.sourceNode.buffer = this.audioBuffer;
    this.sourceNode.connect(this.audioContext.destination);

    // Calculate start time
    this.startTime = this.audioContext.currentTime - offset;

    // Start playback
    this.sourceNode.start(0, offset);
    this.state.isPlaying = true;
    this.state.isPaused = false;

    // Start time update loop
    this.startTimeUpdates();

    // Handle playback end
    this.sourceNode.onended = () => {
      if (this.state.isPlaying) {
        this.state.isPlaying = false;
        this.state.currentTime = 0;
        this.stopTimeUpdates();
        this.callbacks.onEnded();
      }
    };

    log.debug('Started backend audio playback', { offset, duration: this.state.duration });
    this.callbacks.onPlay();
  }

  /**
   * Pause playback.
   */
  pause(): void {
    if (!this.state.isPlaying || !this.audioContext) return;

    // Calculate current position
    this.pausedAt = this.audioContext.currentTime - this.startTime;

    // Stop source
    if (this.sourceNode) {
      this.sourceNode.stop();
      this.sourceNode = null;
    }

    this.state.isPlaying = false;
    this.state.isPaused = true;
    this.state.currentTime = this.pausedAt;

    this.stopTimeUpdates();

    log.debug('Paused backend audio playback', { position: this.pausedAt });
    this.callbacks.onPause();
  }

  /**
   * Stop playback and reset.
   */
  stop(): void {
    if (this.sourceNode) {
      this.sourceNode.stop();
      this.sourceNode = null;
    }

    this.state.isPlaying = false;
    this.state.isPaused = false;
    this.state.currentTime = 0;
    this.pausedAt = 0;

    this.stopTimeUpdates();

    log.debug('Stopped backend audio playback');
    this.callbacks.onStop();
  }

  /**
   * Seek to a specific position.
   */
  seek(time: number): void {
    const wasPlaying = this.state.isPlaying;

    if (wasPlaying) {
      this.stop();
    }

    this.pausedAt = Math.max(0, Math.min(time, this.state.duration));
    this.state.currentTime = this.pausedAt;

    if (wasPlaying) {
      this.play(this.pausedAt);
    }

    log.debug('Seeked to position', { time: this.pausedAt });
  }

  /**
   * Get current playback position in seconds.
   */
  getCurrentTime(): number {
    if (this.state.isPlaying && this.audioContext) {
      return this.audioContext.currentTime - this.startTime;
    }
    return this.state.currentTime;
  }

  /**
   * Get audio duration in seconds.
   */
  getDuration(): number {
    return this.state.duration;
  }

  /**
   * Get current state.
   */
  getState(): Readonly<BackendAudioState> {
    return this.state;
  }

  /**
   * Update configuration.
   */
  updateConfig(config: Partial<BackendAudioConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Start time update loop.
   */
  private startTimeUpdates(): void {
    const update = () => {
      if (!this.state.isPlaying) return;

      this.state.currentTime = this.getCurrentTime();
      this.callbacks.onTimeUpdate(this.state.currentTime);

      this.animationFrameId = requestAnimationFrame(update);
    };

    this.animationFrameId = requestAnimationFrame(update);
  }

  /**
   * Stop time update loop.
   */
  private stopTimeUpdates(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Clean up resources.
   */
  dispose(): void {
    this.stop();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.audioBuffer = null;
    this.state = {
      isInitialized: false,
      isDecoded: false,
      isPlaying: false,
      isPaused: false,
      duration: 0,
      currentTime: 0,
    };
  }
}

/**
 * Create a backend audio adapter instance.
 */
export function createBackendAudioAdapter(
  config: BackendAudioConfig,
  callbacks: BackendAudioCallbacks
): BackendAudioAdapter {
  return new BackendAudioAdapter(config, callbacks);
}
