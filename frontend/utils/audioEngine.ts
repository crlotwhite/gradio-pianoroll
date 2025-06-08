/**
 * Audio Engine for rendering and playing notes.
 *
 * This module provides the AudioEngine class, which uses the Web Audio API to synthesize
 * and play back notes based on piano roll data. It supports rendering notes to an AudioBuffer,
 * playback control (play, pause, stop), waveform analysis, and playhead updates.
 *
 * Functions:
 *   - midiToFreq: Convert MIDI note number to frequency (Hz)
 *
 * Classes:
 *   - AudioEngine: Main audio engine for note synthesis and playback
 */
import {beatsToFlicks, flicksToSeconds, pixelsToFlicks, secondsToFlicks} from './flicks';

/**
 * Convert a MIDI note number to its frequency in Hz.
 * @param midi MIDI note number (0-127)
 * @returns Frequency in Hz
 */
function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

/**
 * AudioEngine class for managing audio synthesis, rendering, and playback.
 *
 * Usage:
 *   const engine = new AudioEngine('my-component');
 *   engine.initialize();
 *   await engine.renderNotes(...);
 *   engine.play();
 *   engine.pause();
 *   engine.stop();
 *
 * Methods:
 *   - initialize(): Set up the audio context and nodes
 *   - dispose(): Clean up resources
 *   - renderNotes(...): Render notes to an AudioBuffer
 *   - play(): Start playback
 *   - pause(): Pause playback
 *   - stop(): Stop playback
 *   - setPlayheadUpdateCallback(cb): Set callback for playhead updates
 *   - getRenderedBuffer(): Get the current rendered AudioBuffer
 *   - downloadAudio(filename): Download rendered audio as WAV
 */
class AudioEngine {
  private audioContext: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private analyserNode: AnalyserNode | null = null;
  private renderBuffer: AudioBuffer | null = null;
  private renderSource: AudioBufferSourceNode | null = null;
  private isPlaying = false;
  private startTime = 0;
  private playbackStartFlicks = 0;
  private currentPlaybackFlicks = 0;
  private onPlayheadUpdate: ((flicks: number) => void) | null = null;
  private rafId: number | null = null;
  private componentId: string;

  constructor(componentId: string = 'default') {
    this.componentId = componentId;
  }

  // Initialize the audio context
  initialize(): void {
    if (this.audioContext) return;

    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.gainNode = this.audioContext.createGain();
    this.analyserNode = this.audioContext.createAnalyser();

    // Configure analyzer for waveform visualization
    this.analyserNode.fftSize = 2048;

    // Connect nodes
    this.gainNode.connect(this.analyserNode);
    this.analyserNode.connect(this.audioContext.destination);

    // Set initial volume
    this.gainNode.gain.value = 0.7;
  }

  // Clean up resources
  dispose(): void {
    this.stop();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
      this.gainNode = null;
      this.analyserNode = null;
      this.renderBuffer = null;
    }
  }

  // Create a basic synth tone for a note
  private createNoteTone(
    ctx: BaseAudioContext, // Changed from AudioContext to BaseAudioContext to work with both regular and offline contexts
    time: number,
    duration: number,
    frequency: number,
    velocity: number,
    destination: AudioNode
  ): void {
    // Create oscillator and gain nodes
    const oscillator = ctx.createOscillator();
    const noteGain = ctx.createGain();

    // Configure oscillator
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;

    // Configure envelope
    const velocityGain = velocity / 127; // MIDI velocity is 0-127
    noteGain.gain.value = 0;

    // Attack
    noteGain.gain.setValueAtTime(0, time);
    noteGain.gain.linearRampToValueAtTime(velocityGain, time + 0.02);

    // Decay and sustain
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + 0.05);

    // Release
    noteGain.gain.linearRampToValueAtTime(velocityGain * 0.7, time + duration - 0.05);
    noteGain.gain.linearRampToValueAtTime(0, time + duration);

    // Connect nodes
    oscillator.connect(noteGain);
    noteGain.connect(destination);

    // Schedule note
    oscillator.start(time);
    oscillator.stop(time + duration);
  }

  // Render notes to an audio buffer
  async renderNotes(
    notes: Array<{
      id: string;
      start: number;
      duration: number;
      startFlicks?: number;      // Optional flicks values for higher precision
      durationFlicks?: number;   // Optional flicks values for higher precision
      pitch: number;
      velocity: number;
    }>,
    tempo: number,
    totalLengthInBeats: number,
    pixelsPerBeat: number = 80 // Add pixelsPerBeat parameter with default value
  ): Promise<AudioBuffer> {
    this.initialize();
    if (!this.audioContext) throw new Error('Audio context not initialized');

    // Calculate total duration in seconds
    const totalDurationFlicks = beatsToFlicks(totalLengthInBeats, tempo);
    const totalDuration = flicksToSeconds(totalDurationFlicks);

    // Create an offline audio context for rendering
    const offlineCtx = new OfflineAudioContext(
      2, // stereo
      this.audioContext.sampleRate * totalDuration,
      this.audioContext.sampleRate
    );

    // Create a gain node in the offline context
    const offlineGain = offlineCtx.createGain();
    offlineGain.connect(offlineCtx.destination);

    // Render each note
    notes.forEach(note => {
      // Use flicks values if available, otherwise convert from pixels
      let noteStartFlicks: number;
      let noteDurationFlicks: number;

      if (note.startFlicks !== undefined && note.durationFlicks !== undefined) {
        // Use precise flicks values if available
        noteStartFlicks = note.startFlicks;
        noteDurationFlicks = note.durationFlicks;
      } else {
        // Fallback to pixel-to-flicks conversion for backward compatibility
        noteStartFlicks = pixelsToFlicks(note.start, pixelsPerBeat, tempo);
        noteDurationFlicks = pixelsToFlicks(note.duration, pixelsPerBeat, tempo);
      }

      const noteStartTime = flicksToSeconds(noteStartFlicks);
      const noteDuration = flicksToSeconds(noteDurationFlicks);

      // Create the note tone
      this.createNoteTone(
        offlineCtx,
        noteStartTime,
        noteDuration,
        midiToFreq(note.pitch),
        note.velocity,
        offlineGain
      );
    });

    // Render the audio
    const renderedBuffer = await offlineCtx.startRendering();
    this.renderBuffer = renderedBuffer;

    return renderedBuffer;
  }

  // Play the rendered audio buffer from current position or specified position
  play(startPositionInFlicks?: number): void {
    if (!this.audioContext || !this.renderBuffer || this.isPlaying) return;

    // Resume audio context if suspended
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }

    // Create a new source for the audio buffer
    this.renderSource = this.audioContext.createBufferSource();
    this.renderSource.buffer = this.renderBuffer;
    this.renderSource.connect(this.gainNode!);

    // Calculate start position in seconds
    const startPositionInSeconds = flicksToSeconds(startPositionInFlicks || this.currentPlaybackFlicks);
    const currentTime = this.audioContext.currentTime;

    // Start playback
    this.renderSource.start(currentTime, startPositionInSeconds);
    this.startTime = currentTime - startPositionInSeconds;
    this.playbackStartFlicks = startPositionInFlicks || this.currentPlaybackFlicks;
    this.isPlaying = true;

    // Start updating playhead position
    this.updatePlayhead();

    // Set up ended event
    this.renderSource.onended = () => {
      this.isPlaying = false;
      this.renderSource = null;
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
    };
  }

  // Stop playback
  stop(): void {
    if (!this.isPlaying || !this.renderSource) return;

    this.renderSource.stop();
    this.renderSource = null;
    this.isPlaying = false;

    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  // Pause playback
  pause(): void {
    if (!this.isPlaying) return;

    // Store current position
    this.currentPlaybackFlicks = this.getCurrentPositionInFlicks();
    this.stop();
  }

  // Resume playback from paused position
  resume(): void {
    if (this.isPlaying) return;
    this.play();
  }

  // Toggle play/pause
  togglePlayback(): void {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.resume();
    }
  }

  // Get current playback position in flicks
  getCurrentPositionInFlicks(): number {
    if (!this.audioContext || !this.isPlaying) {
      return this.currentPlaybackFlicks;
    }

    const elapsedSeconds = this.audioContext.currentTime - this.startTime;
    return this.playbackStartFlicks + secondsToFlicks(elapsedSeconds);
  }

  // Seek to a specific position in flicks
  seekToFlicks(flicks: number): void {
    // Clamp the position to valid range (0 to buffer duration)
    const clampedFlicks = Math.max(0, flicks);

    if (this.renderBuffer) {
      const bufferDurationFlicks = secondsToFlicks(this.renderBuffer.duration);
      const finalFlicks = Math.min(clampedFlicks, bufferDurationFlicks);

      if (this.isPlaying) {
        // If currently playing, stop and restart from new position
        this.stop();
        this.currentPlaybackFlicks = finalFlicks;
        this.play();
      } else {
        // If not playing, just update the position
        this.currentPlaybackFlicks = finalFlicks;

        // Update playhead immediately
        if (this.onPlayheadUpdate) {
          this.onPlayheadUpdate(finalFlicks);
        }
      }
    } else {
      // No buffer yet, just store the position
      this.currentPlaybackFlicks = clampedFlicks;

      // Update playhead immediately
      if (this.onPlayheadUpdate) {
        this.onPlayheadUpdate(clampedFlicks);
      }
    }
  }

  // Update playhead position
  private updatePlayhead(): void {
    if (!this.isPlaying || !this.onPlayheadUpdate) {
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
      return;
    }

    const currentFlicks = this.getCurrentPositionInFlicks();
    this.onPlayheadUpdate(currentFlicks);

    this.rafId = requestAnimationFrame(() => this.updatePlayhead());
  }

  // Set callback for playhead updates
  setPlayheadUpdateCallback(callback: (flicks: number) => void): void {
    this.onPlayheadUpdate = callback;
  }

  // Get analyzer node for waveform visualization
  getAnalyserNode(): AnalyserNode | null {
    return this.analyserNode;
  }

  // Get current waveform data
  getWaveformData(): Float32Array | null {
    if (!this.analyserNode) return null;

    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);
    this.analyserNode.getFloatTimeDomainData(dataArray);

    return dataArray;
  }

  // Check if currently playing
  isCurrentlyPlaying(): boolean {
    return this.isPlaying;
  }

  // Get rendered buffer
  getRenderedBuffer(): AudioBuffer | null {
    return this.renderBuffer;
  }

  // WAV 파일로 내보내기
  exportToWav(): Blob | null {
    if (!this.renderBuffer) {
      console.warn('No rendered audio buffer available for export');
      return null;
    }

    return this.audioBufferToWav(this.renderBuffer);
  }

  // 오디오 다운로드
  downloadAudio(filename: string = 'piano_roll_audio.wav'): void {
    const wavBlob = this.exportToWav();
    if (!wavBlob) {
      console.error('Failed to export audio');
      return;
    }

    // 다운로드 링크 생성
    const url = URL.createObjectURL(wavBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    // 임시로 DOM에 추가하고 클릭하여 다운로드 시작
    document.body.appendChild(link);
    link.click();

    // 정리
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // AudioBuffer를 WAV Blob으로 변환
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

    // WAV 헤더 생성
    const arrayBuffer = new ArrayBuffer(bufferSize);
    const view = new DataView(arrayBuffer);

    // RIFF chunk descriptor
    this.writeString(view, 0, 'RIFF');
    view.setUint32(4, bufferSize - 8, true);
    this.writeString(view, 8, 'WAVE');

    // FMT sub-chunk
    this.writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Sub-chunk size (16 for PCM)
    view.setUint16(20, 1, true); // Audio format (1 for PCM)
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    // Data sub-chunk
    this.writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    // 오디오 데이터 쓰기
    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numberOfChannels; channel++) {
        const channelData = buffer.getChannelData(channel);
        // 부동소수점을 16비트 정수로 변환
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        view.setInt16(offset, intSample, true);
        offset += 2;
      }
    }

    return new Blob([arrayBuffer], { type: 'audio/wav' });
  }

  // 문자열을 DataView에 쓰기
  private writeString(view: DataView, offset: number, string: string): void {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }
}

// AudioEngine 인스턴스 관리자
class AudioEngineManager {
  private static instances: Map<string, AudioEngine> = new Map();

  static getInstance(componentId: string): AudioEngine {
    if (!this.instances.has(componentId)) {
      this.instances.set(componentId, new AudioEngine(componentId));
    }
    return this.instances.get(componentId)!;
  }

  static disposeInstance(componentId: string): void {
    const instance = this.instances.get(componentId);
    if (instance) {
      instance.dispose();
      this.instances.delete(componentId);
    }
  }

  static disposeAll(): void {
    this.instances.forEach(instance => instance.dispose());
    this.instances.clear();
  }
}

// 기본 인스턴스 (하위 호환성을 위해)
export const audioEngine = AudioEngineManager.getInstance('default');

// 인스턴스 관리자 내보내기
export { AudioEngineManager };
