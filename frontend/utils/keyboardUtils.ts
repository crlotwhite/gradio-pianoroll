// Piano keyboard utility functions and constants

export const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
export const TOTAL_KEYS = 128;
export const WHITE_KEY_HEIGHT = 20;
export const BLACK_KEY_HEIGHT = 12;
export function getBlackKeyWidth(keyboardWidth: number) {
  return keyboardWidth * 0.6;
}

export function midiToFrequency(midiNote: number): number {
  return 440 * Math.pow(2, (midiNote - 69) / 12);
}

export function calculateKeyPositions(keyboardWidth: number) {
  const keyPositions: Array<{
    note: string;
    octave: number;
    isBlack: boolean;
    y: number;
  }> = [];
  for (let midiNote = TOTAL_KEYS - 1; midiNote >= 0; midiNote--) {
    const octave = Math.floor(midiNote / 12) - 1;
    const noteIndex = midiNote % 12;
    const note = NOTES[noteIndex];
    const isBlack = note.includes('#');
    const y = (TOTAL_KEYS - 1 - midiNote) * WHITE_KEY_HEIGHT;
    keyPositions.push({ note, octave, isBlack, y });
  }
  return keyPositions;
}

export function playPreviewNote(audioContext: AudioContext, midiNote: number) {
  const attackTime = 0.01;
  const releaseTime = 0.5;
  const frequency = midiToFrequency(midiNote);
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();
  oscillator.type = 'sine';
  oscillator.frequency.value = frequency;
  gainNode.gain.setValueAtTime(0, audioContext.currentTime);
  gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + attackTime);
  gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + attackTime + releaseTime);
  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + attackTime + releaseTime);
}

export {};
