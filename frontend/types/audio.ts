/**
 * Audio engine related types for Piano Roll
 */

/**
 * Callback function for playhead position updates.
 * Called during playback to sync UI with audio position.
 *
 * @param flicks - Current playhead position in flicks
 */
export type PlayheadUpdateCallback = (flicks: number) => void;

/**
 * Audio buffer with metadata.
 */
export interface AudioBufferWithMetadata {
  /** The audio buffer */
  buffer: AudioBuffer;
  /** Sample rate of the audio */
  sampleRate: number;
  /** Duration in seconds */
  duration: number;
  /** Number of channels */
  numberOfChannels: number;
}

/**
 * Audio analysis result from waveform processing.
 */
export interface WaveformAnalysis {
  /** Peak values for visualization */
  peaks: Float32Array;
  /** RMS values for each segment */
  rms: Float32Array;
  /** Duration in seconds */
  duration: number;
  /** Number of segments */
  segmentCount: number;
}

/**
 * Audio format options for export.
 */
export interface AudioExportOptions {
  /** Format: 'wav' | 'mp3' | 'ogg' */
  format: 'wav' | 'mp3' | 'ogg';
  /** Bit depth for WAV export */
  bitDepth?: 16 | 24 | 32;
  /** Audio quality (0-1) for lossy formats */
  quality?: number;
}

/**
 * Audio device information.
 */
export interface AudioDeviceInfo {
  /** Device ID */
  deviceId: string;
  /** Device label */
  label: string;
  /** Number of output channels */
  outputChannels: number;
  /** Whether the device is the default */
  isDefault: boolean;
}

/**
 * Audio context state.
 */
export type AudioContextState = 'running' | 'suspended' | 'closed';
