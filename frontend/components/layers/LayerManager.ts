/**
 * LayerManager - Central manager for handling multiple canvas layers
 */
import type { Layer, LayerManager as ILayerManager, LayerEvent, Viewport, HitResult } from './types';

export class LayerManager implements ILayerManager {
  private layers: Map<string, Layer> = new Map();
  private layersArray: Layer[] = [];
  private needsSort = false;

  constructor() {}

  addLayer(layer: Layer): void {
    if (this.layers.has(layer.id)) {
      console.warn(`Layer with id '${layer.id}' already exists`);
      return;
    }

    this.layers.set(layer.id, layer);
    this.layersArray.push(layer);
    this.needsSort = true;

    // Call lifecycle method
    if (layer.onAdd) {
      layer.onAdd(this);
    }
  }

  removeLayer(layerId: string): void {
    const layer = this.layers.get(layerId);
    if (!layer) {
      console.warn(`Layer with id '${layerId}' not found`);
      return;
    }

    // Call lifecycle method
    if (layer.onRemove) {
      layer.onRemove(this);
    }

    // Cleanup resources
    if (layer.dispose) {
      layer.dispose();
    }

    this.layers.delete(layerId);
    this.layersArray = this.layersArray.filter(l => l.id !== layerId);
  }

  getLayer(layerId: string): Layer | null {
    return this.layers.get(layerId) || null;
  }

  getAllLayers(): Layer[] {
    this.sortLayersIfNeeded();
    return [...this.layersArray];
  }

  setLayerVisibility(layerId: string, visible: boolean): void {
    const layer = this.layers.get(layerId);
    if (layer) {
      layer.visible = visible;
    }
  }

  setLayerOpacity(layerId: string, opacity: number): void {
    const layer = this.layers.get(layerId);
    if (layer) {
      layer.opacity = Math.max(0, Math.min(1, opacity));
    }
  }

  setLayerZIndex(layerId: string, zIndex: number): void {
    const layer = this.layers.get(layerId);
    if (layer) {
      layer.zIndex = zIndex;
      this.needsSort = true;
    }
  }

  clear(): void {
    // Dispose all layers
    for (const layer of this.layersArray) {
      if (layer.onRemove) {
        layer.onRemove(this);
      }
      if (layer.dispose) {
        layer.dispose();
      }
    }

    this.layers.clear();
    this.layersArray = [];
    this.needsSort = false;
  }

  render(ctx: CanvasRenderingContext2D, viewport: Viewport): void {
    this.sortLayersIfNeeded();

    // Only log when layers change, not every frame
    if (this.needsSort || this.layersArray.length === 0) {
      console.log(`🎨 LayerManager rendering ${this.layersArray.length} layers`);
    }

    // Save context state
    ctx.save();

    // Render layers in z-index order (lowest to highest)
    for (const layer of this.layersArray) {
      if (!layer.visible) {
        continue;
      }

      // Save context for each layer
      ctx.save();

      // Apply layer opacity
      if (layer.opacity < 1) {
        ctx.globalAlpha = layer.opacity;
      }

      try {
        layer.render(ctx, viewport);
      } catch (error) {
        console.error(`Error rendering layer '${layer.id}':`, error);
      }

      // Restore context after each layer
      ctx.restore();
    }

    // Restore main context state
    ctx.restore();
  }

  handleEvent(event: LayerEvent, viewport: Viewport): boolean {
    this.sortLayersIfNeeded();

    console.log(`🎨 LayerManager handling ${event.type} event at (${event.worldX}, ${event.worldY}) with ${this.layersArray.length} layers`);

    // Process layers in reverse z-index order (highest to lowest)
    // This ensures top layers get first chance to handle events
    for (let i = this.layersArray.length - 1; i >= 0; i--) {
      const layer = this.layersArray[i];

      if (!layer.visible) {
        console.log(`🎨 Skipping invisible layer '${layer.id}'`);
        continue;
      }

      try {
        // First check if the event hits this layer
        const hitResult = layer.hitTest(event.worldX, event.worldY, viewport);
        if (!hitResult) {
          console.log(`🎨 Layer '${layer.id}' hit test failed`);
          continue;
        }

        console.log(`🎨 Layer '${layer.id}' hit test passed, attempting to handle event`);

        // If hit, let the layer handle the event
        const handled = layer.handleEvent(event, viewport);
        if (handled) {
          console.log(`🎨 Event handled by layer '${layer.id}'`);
          return true; // Event consumed
        } else {
          console.log(`🎨 Layer '${layer.id}' did not handle the event`);
        }
      } catch (error) {
        console.error(`Error handling event in layer '${layer.id}':`, error);
      }
    }

    console.log('🎨 No layer handled the event');
    return false; // Event not handled by any layer
  }

  // Hit test against all layers to find cursor changes
  getHitResult(worldX: number, worldY: number, viewport: Viewport): HitResult | null {
    this.sortLayersIfNeeded();

    // Check layers in reverse z-index order (highest to lowest)
    for (let i = this.layersArray.length - 1; i >= 0; i--) {
      const layer = this.layersArray[i];

      if (!layer.visible) continue;

      try {
        const hitResult = layer.hitTest(worldX, worldY, viewport);
        if (hitResult) {
          return hitResult;
        }
      } catch (error) {
        console.error(`Error in hit test for layer '${layer.id}':`, error);
      }
    }

    return null;
  }

  // Update all layers (for animations)
  update(deltaTime: number): void {
    for (const layer of this.layersArray) {
      if (layer.update) {
        try {
          layer.update(deltaTime);
        } catch (error) {
          console.error(`Error updating layer '${layer.id}':`, error);
        }
      }
    }
  }

  // Notify all layers of viewport resize
  onResize(viewport: Viewport): void {
    for (const layer of this.layersArray) {
      if (layer.onResize) {
        try {
          layer.onResize(viewport);
        } catch (error) {
          console.error(`Error in resize for layer '${layer.id}':`, error);
        }
      }
    }
  }

  private sortLayersIfNeeded(): void {
    if (!this.needsSort) return;

    this.layersArray.sort((a, b) => {
      // Sort by z-index (ascending)
      if (a.zIndex !== b.zIndex) {
        return a.zIndex - b.zIndex;
      }
      // If z-index is same, maintain original order
      return 0;
    });

    this.needsSort = false;
  }

  // Dispose the layer manager
  dispose(): void {
    this.clear();
  }
}