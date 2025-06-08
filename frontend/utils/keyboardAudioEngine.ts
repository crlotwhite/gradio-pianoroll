// Utility for managing audio context and previewing notes in the keyboard
import { midiToFrequency } from './keyboardUtils';

export class KeyboardAudioEngine {
  private audioContext: AudioContext | null = null;
  private canPlay = false;

  get context() {
    return this.audioContext;
  }

  get isReady() {
    return this.canPlay && !!this.audioContext;
  }

  init() {
    if (!this.audioContext) {
      try {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        this.canPlay = true;
      } catch (e) {
        console.error('Web Audio API is not supported in this browser', e);
        this.canPlay = false;
      }
    }
  }

  dispose() {
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
      this.canPlay = false;
    }
  }

  playNote(midiNote: number) {
    if (!this.audioContext || !this.canPlay) return;
    const attackTime = 0.01;
    const releaseTime = 0.5;
    const frequency = midiToFrequency(midiNote);
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;
    gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + attackTime);
    gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + attackTime + releaseTime);
    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    oscillator.start();
    oscillator.stop(this.audioContext.currentTime + attackTime + releaseTime);
  }
}

export {};
