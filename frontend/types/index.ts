/**
 * Centralized type definitions for the piano roll frontend
 *
 * This module re-exports all types from their respective source files
 * to provide a single import point for type definitions.
 */

// Layer system types (canonical source for Note, LineDataPoint, LineLayerConfig)
export type {
  LayerRenderContext,
  LayerProps,
  Note,
  LineDataPoint,
  LineLayerConfig,
} from './layer';

// Piano roll data types
export type { TimeSignature, PianoRollData, LineLayerConfigWithData } from './piano_roll_data';

// Component props types
export type {
  PianoRollProps,
  ToolbarProps,
  LayerControlPanelProps,
  DebugComponentProps,
} from './component';

// Audio engine types
export type { PlayheadUpdateCallback } from './audio';

// Coordinate utility types (re-export from utils)
export type {
  MeasureInfo,
  PitchInfo,
  CoordinateConfig,
  MousePositionInfo,
} from '../utils/coordinateUtils';
