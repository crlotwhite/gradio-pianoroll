/**
 * Layer System - Export all layer classes and utilities
 */

// Base layer system
export { BaseLayer, LayerManager, LayerZIndex } from '../LayerSystem';
export type { LayerRenderContext, LayerProps } from '../LayerSystem';

// Specific layer implementations
export { GridLayer } from './GridLayer';
export { NotesLayer } from './NotesLayer';
export { WaveformLayer } from './WaveformLayer';
export { PlayheadLayer } from './PlayheadLayer';

// Note interface for NotesLayer
export type { Note } from './NotesLayer';

// Layer System exports
export * from '../LayerSystem';
export * from './GridLayer';
export * from './NotesLayer';
export * from './PlayheadLayer';
export * from './WaveformLayer';