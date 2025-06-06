/**
 * Layer system exports
 */

// Types and interfaces
export type {
  Layer,
  LayerManager as ILayerManager,
  LayerEvent,
  LayerEventType,
  Viewport,
  HitResult,
  LayerProps,
  AudioData,
  Note
} from './types';

// Layer Manager
export { LayerManager } from './LayerManager';

// Layers
export { WaveformLayer } from './WaveformLayer';
export type { WaveformLayerProps } from './WaveformLayer';
export { NoteLayer } from './NoteLayer';
export type { NoteLayerProps } from './NoteLayer';

// Utility functions for layer events
import type { LayerEventType, Viewport, LayerEvent } from './types';

export function createLayerEvent(
  type: LayerEventType,
  originalEvent: MouseEvent | WheelEvent,
  canvasRect: DOMRect,
  viewport: Viewport
): LayerEvent {
  const x = (originalEvent as MouseEvent).clientX - canvasRect.left;
  const y = (originalEvent as MouseEvent).clientY - canvasRect.top;

  return {
    type,
    x,
    y,
    worldX: x + viewport.horizontalScroll,
    worldY: y + viewport.verticalScroll,
    originalEvent,
    shiftKey: originalEvent.shiftKey,
    ctrlKey: originalEvent.ctrlKey,
    altKey: originalEvent.altKey,
    button: (originalEvent as MouseEvent).button,
    deltaX: (originalEvent as WheelEvent).deltaX,
    deltaY: (originalEvent as WheelEvent).deltaY,
  };
}