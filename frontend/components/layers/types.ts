/**
 * Layer system types and interfaces
 */

// Viewport represents the current visible area and zoom level
export interface Viewport {
  width: number;
  height: number;
  horizontalScroll: number;
  verticalScroll: number;
  pixelsPerBeat: number;
  tempo: number;
  totalGridWidth?: number;
  totalGridHeight?: number;
}

// Hit test result
export interface HitResult {
  layerId: string;
  elementId?: string;
  elementType?: string;
  data?: any;
  cursor?: string;
}

// Layer event types
export type LayerEventType =
  | 'mousedown'
  | 'mousemove'
  | 'mouseup'
  | 'mouseleave'
  | 'click'
  | 'dblclick'
  | 'wheel';

// Layer event interface
export interface LayerEvent {
  type: LayerEventType;
  x: number;        // Canvas coordinates
  y: number;        // Canvas coordinates
  worldX: number;   // World coordinates (considering scroll)
  worldY: number;   // World coordinates (considering scroll)
  originalEvent: MouseEvent | WheelEvent;
  shiftKey?: boolean;
  ctrlKey?: boolean;
  altKey?: boolean;
  button?: number;
  deltaX?: number;  // For wheel events
  deltaY?: number;  // For wheel events
}

// Base layer interface
export interface Layer {
  readonly id: string;
  readonly name: string;
  visible: boolean;
  opacity: number;
  zIndex: number;

  // Rendering
  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void;

  // Hit testing - return null if no hit
  hitTest(worldX: number, worldY: number, viewport: Viewport): HitResult | null;

  // Event handling - return true if event was handled
  handleEvent(event: LayerEvent, viewport: Viewport): boolean;

  // Lifecycle methods
  onAdd?(layerManager: LayerManager): void;
  onRemove?(layerManager: LayerManager): void;
  onResize?(viewport: Viewport): void;

  // Update method for animations or data changes
  update?(deltaTime: number): void;

  // Cleanup resources
  dispose?(): void;
}

// Layer manager interface
export interface LayerManager {
  addLayer(layer: Layer): void;
  removeLayer(layerId: string): void;
  getLayer(layerId: string): Layer | null;
  getAllLayers(): Layer[];
  setLayerVisibility(layerId: string, visible: boolean): void;
  setLayerOpacity(layerId: string, opacity: number): void;
  setLayerZIndex(layerId: string, zIndex: number): void;
  clear(): void;
  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void;
  handleEvent(event: LayerEvent, viewport: Viewport): boolean;
}

// Common layer properties
export interface LayerProps {
  id: string;
  name: string;
  visible?: boolean;
  opacity?: number;
  zIndex?: number;
}

// Audio data interface for layers that need audio information
export interface AudioData {
  buffer?: AudioBuffer;
  waveformData?: Array<{x: number, min: number, max: number}>;
  audioUrl?: string;
  isBackendAudio?: boolean;
}

// Note interface for note layer
export interface Note {
  id: string;
  start: number;
  duration: number;
  startFlicks?: number;
  durationFlicks?: number;
  startSeconds?: number;
  durationSeconds?: number;
  endSeconds?: number;
  startBeats?: number;
  durationBeats?: number;
  startTicks?: number;
  durationTicks?: number;
  startSample?: number;
  durationSamples?: number;
  pitch: number;
  velocity: number;
  lyric?: string;
  phoneme?: string;
}