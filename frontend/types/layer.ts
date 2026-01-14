/**
 * Piano Roll Layer System Types
 *
 * This module contains types for the layer-based rendering system.
 * Note types are now exported from './notes' for single source of truth.
 */

// Re-export Note from notes.ts for backward compatibility
export type { Note } from './notes';

// Layer rendering context
export interface LayerRenderContext {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  width: number;
  height: number;
  horizontalScroll: number;
  verticalScroll: number;
  pixelsPerBeat: number;
  tempo: number;
  currentFlicks: number;
  isPlaying: boolean;
  timeSignature: { numerator: number; denominator: number };
  snapSetting: string;
  [key: string]: unknown;
}

/**
 * Base properties for all layers.
 */
export interface LayerProps {
  opacity: number;
  visible: boolean;
  zIndex: number;
  name: string;
}

/**
 * Represents a single data point in a line layer (e.g., pitch curve).
 */
export interface LineDataPoint {
  x: number;
  y: number;
}

/**
 * Configuration for a line layer (e.g., pitch contour, loudness).
 */
export interface LineLayerConfig {
  name: string;
  color: string;
  lineWidth: number;
  yMin: number;
  yMax: number;
  height?: number;
  position?: 'top' | 'center' | 'bottom' | 'overlay';
  renderMode?: 'default' | 'piano_grid' | 'independent_range';
  visible?: boolean;
  opacity?: number;
  dataType?: string;
  unit?: string;
  originalRange?: {
    minHz?: number;
    maxHz?: number;
    minMidi?: number;
    maxMidi?: number;
    min?: number;
    max?: number;
    voiced_ratio?: number;
    y_min?: number;
    y_max?: number;
  };
}

/**
 * Layer type enumeration for type checking.
 */
export enum LayerType {
  GRID = 'grid',
  NOTES = 'notes',
  WAVEFORM = 'waveform',
  LINE = 'line',
  PLAYHEAD = 'playhead',
}

/**
 * Base interface for all layer implementations.
 */
export interface Layer {
  /** Get the layer type */
  getType(): LayerType;
  /** Get the layer name */
  getName(): string;
  /** Render the layer */
  render(context: LayerRenderContext): void;
  /** Set layer visibility */
  setVisible(visible: boolean): void;
  /** Check if layer is visible */
  isVisible(): boolean;
  /** Set layer opacity */
  setOpacity(opacity: number): void;
  /** Get current opacity */
  getOpacity(): number;
  /** Dispose of layer resources */
  dispose(): void;
}
