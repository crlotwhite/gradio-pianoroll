/**
 * Audio Manager for Piano Roll
 *
 * This module manages audio rendering and playback using the Web Audio API.
 * It handles both frontend synthesis and backend audio sources.
 *
 * Separated from PianoRoll.svelte for better maintainability.
 */

import { createLogger } from '../../utils/logger';
import {
  secondsToFlicks,
  flicksToSeconds,
  beatsToFlicks,
} from '../../utils/flicks';
import type { Note, PlayheadUpdateCallback } from '../../types';

const log = createLogger('AudioManager');

/**
 * Audio source type.
 */
export type AudioSourceType = 'frontend' | 'backend';

/**
 * Audio manager configuration.
 */
export interface AudioManagerConfig {
  /** Audio sample rate */
  sampleRate: number;
  /** MIDI pulses per quarter note */
  ppqn: number;
  /** Component element ID for engine instances */
  elemId: string;
}

/**
 * Audio rendering result.
 */
export interface RenderResult {
  /** The rendered audio buffer */
  buffer: AudioBuffer | null;
  /** Whether rendering succeeded */
  success: boolean;
  /** Error message if failed */
  error?: string;
}

/**
 * Audio playback state.
 */
export interface AudioPlaybackState {
  isPlaying: boolean;
  isRendering: boolean;
  currentPosition: number;
  duration: number;
}

/**
 * AudioManager class
 *
 * Manages audio context, rendering, and playback for the piano roll.
 */
export class AudioManager {
  private config: AudioManagerConfig;
  private audioContext: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private renderBuffer: AudioBuffer | null = null;
  private isPlaying = false;
  private currentPosition = 0;
  private onPlayheadUpdate: PlayheadUpdateCallback | null = null;
  private animationFrameId: number | null = null;

  constructor(config: AudioManagerConfig) {
    this.config = config;
  }

  /**
   * Initialize the audio context.
   */
  initialize(): void {
    if (this.audioContext) return;

    this.audioContext = new (window.AudioContext || (window as unknown).webkitAudioContext)();
    this.gainNode = this.audioContext.createGain();
    this.analyserNode = this.audioContext.createAnalyser();

    // Configure analyzer for waveform visualization
    this.analyserNode.fftSize = 2048;

    // Connect nodes
    this.gainNode.connect(this.analyserNode);
    this.analyserNode.connect(this.audioContext.destination);

    // Set initial volume
    this.gainNode.gain.value = 0.7;

    log.debug('Audio context initialized');
  }

  /**
   * Get the audio context.
   */
  getContext(): AudioContext | null {
    return this.audioContext;
  }

  /**
   * Get the analyser node for visualization.
   */
  getAnalyser(): AnalyserNode | null {
    return this.analyserNode;
  }

  /**
   * Set callback for playhead position updates.
   */
  setPlayheadUpdateCallback(callback: PlayheadUpdateCallback): void {
    this.onPlayheadUpdate = callback;
  }

  /**
   * Render notes to an audio buffer.
   */
  async renderNotes(
    notes: Note[],
    tempo: number,
    totalLengthInBeats: number
  ): Promise<RenderResult> {
    this.initialize();
    if (!this.audioContext) {
      return { success: false, buffer: null, error: 'Audio context not initialized' };
    }

    try {
      // Calculate total duration in seconds
      const totalDurationFlicks = beatsToFlicks(totalLengthInBeats, tempo);
      const totalDuration = flicksToSeconds(totalDurationFlicks);

      // Create offline context for rendering
      const offlineCtx = new OfflineAudioContext(
        2, // stereo
        this.audioContext.sampleRate * totalDuration,
        this.audioContext.sampleRate
      );

      // Create gain node for mixing
      const offlineGain = offlineCtx.createGain();
      offlineGain.connect(offlineCtx.destination);

      // Render each note
      notes.forEach((note) => {
        this.createNoteTone(
          offlineCtx,
          note.startFlicks ? flicksToSeconds(note.startFlicks) : 0,
          note.durationFlicks ? flicksToSeconds(note.durationFlicks) : 0.5,
          this.midiToFreq(note.pitch),
          note.velocity,
          offlineGain
        );
      });

      // Render the audio
      const renderedBuffer = await offlineCtx.startRendering();
      this.renderBuffer = renderedBuffer;

      log.debug('Audio rendering completed', {
        duration: renderedBuffer.duration,
        numberOfChannels: renderedBuffer.numberOfChannels,
      });

      return { success: true, buffer: renderedBuffer };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      log.error('Audio rendering failed:', error);
      return { success: false, buffer: null, error: errorMessage };
    }
  }

  /**
   * Create a synth tone for a note.
   */
  private createNoteTone(
    ctx: BaseAudioContext,
    time: number,
    duration: number,
    frequency: number,
    velocity: number,
    destination: AudioNode
  ): void {
    const oscillator = ctx.createOscillator();
    const noteGain = ctx.createGain();

    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;

    const velocityGain = velocity / 127;
    noteGain.gain.value = 0;

    // ADSR envelope
    noteGain.gain.setValueAtTime(0, time);
    noteGain.gain.linearRampToValueAtTime(velocityGain, time + 0.02);
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + 0.05);
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + duration - 0.05);
    noteGain.gain.linearRampToValueAtTime(0, time + duration);

    oscillator.connect(noteGain);
    noteGain.connect(destination);
    oscillator.start(time);
    oscillator.stop(time + duration);
  }

  /**
   * Convert MIDI note to frequency.
   */
  private midiToFreq(midi: number): number {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  /**
   * Start playback of rendered audio.
   */
  play(startPositionInFlicks?: number): void {
    if (!this.audioContext || !this.renderBuffer || this.isPlaying) return;

    // Resume audio context if suspended
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }

    const startPosition = startPositionInFlicks ?? this.currentPosition;
    const startPositionInSeconds = flicksToSeconds(startPosition);

    // Create source node
    const source = this.audioContext.createBufferSource();
    source.buffer = this.renderBuffer;
    source.connect(this.gainNode!);

    // Start playback
    source.start(this.audioContext.currentTime, startPositionInSeconds);
    this.isPlaying = true;

    // Start playhead updates
    this.startPlayheadUpdates(source);

    source.onended = () => {
      this.isPlaying = false;
      this.stopPlayheadUpdates();
    };
  }

  /**
   * Start playhead position updates during playback.
   */
  private startPlayheadUpdates(source: AudioBufferSourceNode): void {
    const update = () => {
      if (!this.isPlaying || !this.audioContext || !this.onPlayheadUpdate) {
        this.stopPlayheadUpdates();
        return;
      }

      if (this.audioContext.state === 'running') {
        // Calculate current position based on playback time
        // This is simplified; actual implementation would track start time
        this.onPlayheadUpdate(this.currentPosition);
      }

      this.animationFrameId = requestAnimationFrame(update);
    };

    this.animationFrameId = requestAnimationFrame(update);
  }

  /**
   * Stop playhead position updates.
   */
  private stopPlayheadUpdates(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * Pause playback.
   */
  pause(): void {
    if (!this.isPlaying) return;

    // Store current position
    this.currentPosition = this.getCurrentPositionInFlicks();
    this.isPlaying = false;
    this.stopPlayheadUpdates();
  }

  /**
   * Stop playback and reset.
   */
  stop(): void {
    this.isPlaying = false;
    this.currentPosition = 0;
    this.stopPlayheadUpdates();

    if (this.onPlayheadUpdate) {
      this.onPlayheadUpdate(0);
    }
  }

  /**
   * Get current position in flicks.
   */
  getCurrentPositionInFlicks(): number {
    return this.currentPosition;
  }

  /**
   * Seek to a specific position in flicks.
   */
  seekToFlicks(flicks: number): void {
    const clampedFlicks = Math.max(0, flicks);

    if (this.renderBuffer) {
      const bufferDurationFlicks = secondsToFlicks(this.renderBuffer.duration);
      this.currentPosition = Math.min(clampedFlicks, bufferDurationFlicks);
    } else {
      this.currentPosition = clampedFlicks;
    }

    if (this.onPlayheadUpdate) {
      this.onPlayheadUpdate(this.currentPosition);
    }
  }

  /**
   * Get the rendered audio buffer.
   */
  getRenderedBuffer(): AudioBuffer | null {
    return this.renderBuffer;
  }

  /**
   * Download rendered audio as WAV file.
   */
  downloadAudio(filename: string = 'piano_roll_audio.wav'): void {
    if (!this.renderBuffer) {
      log.warn('No rendered audio buffer available');
      return;
    }

    const wavBlob = this.audioBufferToWav(this.renderBuffer);
    const url = URL.createObjectURL(wavBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);

    log.debug('Audio download initiated:', filename);
  }

  /**
   * Convert AudioBuffer to WAV blob.
   */
  private audioBufferToWav(buffer: AudioBuffer): Blob {
    const length = buffer.length;
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const bitsPerSample = 16;
    const bytesPerSample = bitsPerSample / 8;
    const blockAlign = numberOfChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = length * blockAlign;
    const bufferSize = 44 + dataSize;

    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);

    // RIFF header
    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, bufferSize - 8, true);
    this.writeString(view, 8, 'WAVE');

    // fmt chunk
    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    // data chunk
    this.writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    // Write audio data
    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numberOfChannels; channel++) {
        const channelData = buffer.getChannelData(channel);
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        view.setInt16(offset, intSample, true);
        offset += 2;
      }
    }

    return new Blob([arrayBuffer], { type: 'audio/wav' });
  }

  /**
   * Write string to DataView.
   */
  private writeString(view: DataView, offset: number, string: string): void {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
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
    this.gainNode = null;
    this.analyserNode = null;
    this.renderBuffer = null;
  }
}

/**
 * Create a new audio manager instance.
 */
export function createAudioManager(config: AudioManagerConfig): AudioManager {
  return new AudioManager(config);
}
