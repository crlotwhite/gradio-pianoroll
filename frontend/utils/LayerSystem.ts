import type { LayerRenderContext, LayerProps } from '../types/layer';

/**
 * Layer System for Piano Roll Canvas Rendering
 *
 * This system allows different visual elements (notes, waveforms, grid, playhead)
 * to be rendered as separate layers with independent properties like opacity,
 * visibility, and z-order.
 */

export abstract class BaseLayer {
  protected props: LayerProps;

  constructor(name: string, zIndex: number = 0) {
    this.props = {
      opacity: 1.0,
      visible: true,
      zIndex,
      name
    };
  }

  // Abstract method that each layer must implement
  abstract render(context: LayerRenderContext): void;

  // Layer property management
  setOpacity(opacity: number): void {
    this.props.opacity = Math.max(0, Math.min(1, opacity));
  }

  getOpacity(): number {
    return this.props.opacity;
  }

  setVisible(visible: boolean): void {
    this.props.visible = visible;
  }

  isVisible(): boolean {
    return this.props.visible;
  }

  setZIndex(zIndex: number): void {
    this.props.zIndex = zIndex;
  }

  getZIndex(): number {
    return this.props.zIndex;
  }

  getName(): string {
    return this.props.name;
  }

  // Called before rendering (setup phase)
  onBeforeRender(context: LayerRenderContext): void {
    // Default implementation - can be overridden
    if (context.ctx && this.props.opacity < 1.0) {
      context.ctx.save();
      context.ctx.globalAlpha = this.props.opacity;
    }
  }

  // Called after rendering (cleanup phase)
  onAfterRender(context: LayerRenderContext): void {
    // Default implementation - can be overridden
    if (context.ctx && this.props.opacity < 1.0) {
      context.ctx.restore();
    }
  }
}

export class LayerManager {
  private layers: Map<string, BaseLayer> = new Map();
  private renderOrder: string[] = [];

  // Add a layer to the system
  addLayer(layer: BaseLayer): void {
    this.layers.set(layer.getName(), layer);
    this.updateRenderOrder();
  }

  // Remove a layer from the system
  removeLayer(name: string): void {
    this.layers.delete(name);
    this.updateRenderOrder();
  }

  // Get a layer by name
  getLayer(name: string): BaseLayer | undefined {
    return this.layers.get(name);
  }

  // Get all layer names
  getLayerNames(): string[] {
    return Array.from(this.layers.keys());
  }

  // Update the rendering order based on z-index
  private updateRenderOrder(): void {
    this.renderOrder = Array.from(this.layers.keys()).sort((a, b) => {
      const layerA = this.layers.get(a)!;
      const layerB = this.layers.get(b)!;
      return layerA.getZIndex() - layerB.getZIndex();
    });
  }

  // Clear the canvas and render all visible layers
  renderAllLayers(context: LayerRenderContext): void {
    // Clear the canvas first
    context.ctx.clearRect(0, 0, context.width, context.height);

    // Render layers in z-index order
    for (const layerName of this.renderOrder) {
      const layer = this.layers.get(layerName);
      if (layer && layer.isVisible()) {
        layer.onBeforeRender(context);
        layer.render(context);
        layer.onAfterRender(context);
      }
    }
  }

  // Render a specific layer (useful for testing or partial updates)
  renderLayer(name: string, context: LayerRenderContext): void {
    const layer = this.layers.get(name);
    if (layer && layer.isVisible()) {
      layer.onBeforeRender(context);
      layer.render(context);
      layer.onAfterRender(context);
    }
  }

  // Enable/disable a layer
  setLayerVisible(name: string, visible: boolean): void {
    const layer = this.layers.get(name);
    if (layer) {
      layer.setVisible(visible);
    }
  }

  // Set layer opacity
  setLayerOpacity(name: string, opacity: number): void {
    const layer = this.layers.get(name);
    if (layer) {
      layer.setOpacity(opacity);
    }
  }

  // Set layer z-index and update render order
  setLayerZIndex(name: string, zIndex: number): void {
    const layer = this.layers.get(name);
    if (layer) {
      layer.setZIndex(zIndex);
      this.updateRenderOrder();
    }
  }

  // Get layer information for debugging
  getLayerInfo(): Array<{name: string, visible: boolean, opacity: number, zIndex: number}> {
    return Array.from(this.layers.values()).map(layer => ({
      name: layer.getName(),
      visible: layer.isVisible(),
      opacity: layer.getOpacity(),
      zIndex: layer.getZIndex()
    }));
  }

  // Clear all layers
  clear(): void {
    this.layers.clear();
    this.renderOrder = [];
  }
}

// Layer Z-index constants for consistent layer ordering
export const LayerZIndex = {
  BACKGROUND: 0,
  GRID: 10,
  WAVEFORM: 20,
  LINES: 25,        // Line data layers (pitch curves, loudness, etc.)
  NOTES: 30,
  SELECTION: 40,
  PLAYHEAD: 50,
  UI_OVERLAY: 60
} as const;

export type { LayerRenderContext, LayerProps };