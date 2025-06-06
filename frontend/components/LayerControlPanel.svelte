<!--
  LayerControlPanel.svelte
  UI component for controlling layer visibility, opacity, and order
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { LayerManager } from '../utils/layers';

  // Props
  export let layerManager: LayerManager | null = null;
  export let visible = false;

  const dispatch = createEventDispatcher();

  // Layer information
  $: layerInfo = layerManager ? layerManager.getLayerInfo() : [];

  function toggleLayerVisibility(layerName: string) {
    if (!layerManager) return;
    
    const layer = layerManager.getLayer(layerName);
    if (layer) {
      layerManager.setLayerVisible(layerName, !layer.isVisible());
      dispatch('layerChanged');
    }
  }

  function updateLayerOpacity(layerName: string, opacity: number) {
    if (!layerManager) return;
    
    layerManager.setLayerOpacity(layerName, opacity);
    dispatch('layerChanged');
  }

  function moveLayerUp(layerName: string) {
    console.log('📈 Moving layer up:', layerName);
    if (!layerManager) return;
    
    const layer = layerManager.getLayer(layerName);
    if (!layer) return;

    // Get current z-index and increment it
    const currentZ = layer.getZIndex();
    console.log('Current Z:', currentZ, 'Moving to Z:', currentZ + 1);
    
    layerManager.setLayerZIndex(layerName, currentZ + 1);
    dispatch('layerChanged');
  }

  function moveLayerDown(layerName: string) {
    console.log('📉 Moving layer down:', layerName);
    if (!layerManager) return;
    
    const layer = layerManager.getLayer(layerName);
    if (!layer) return;

    // Get current z-index and decrement it
    const currentZ = layer.getZIndex();
    console.log('Current Z:', currentZ, 'Moving to Z:', currentZ - 1);
    
    layerManager.setLayerZIndex(layerName, currentZ - 1);
    dispatch('layerChanged');
  }

  function togglePanel() {
    visible = !visible;
  }
</script>

<div class="layer-control-panel" class:visible>
  <div class="panel-header">
    <button class="toggle-button" on:click={togglePanel}>
      <span class="icon">{visible ? '🔽' : '📋'}</span>
      <span class="label">Layers</span>
    </button>
  </div>

  {#if visible}
    <div class="panel-content">
      {#if layerInfo.length === 0}
        <div class="no-layers">No layers available</div>
      {:else}
        <div class="layers-list">
          {#each layerInfo.sort((a, b) => b.zIndex - a.zIndex) as layer (layer.name)}
            <div class="layer-item" class:disabled={!layer.visible}>
              <div class="layer-header">
                <button 
                  class="visibility-toggle"
                  class:hidden={!layer.visible}
                  on:click={() => toggleLayerVisibility(layer.name)}
                  title={layer.visible ? 'Hide layer' : 'Show layer'}
                >
                  {layer.visible ? '👁️' : '👁️‍🗨️'}
                </button>
                
                <span class="layer-name">{layer.name}</span>
                
                <div class="layer-controls">
                  <button 
                    class="move-button" 
                    on:click={() => moveLayerUp(layer.name)}
                    title="Move up"
                  >
                    ⬆️
                  </button>
                  <button 
                    class="move-button" 
                    on:click={() => moveLayerDown(layer.name)}
                    title="Move down"
                  >
                    ⬇️
                  </button>
                </div>
              </div>

              <div class="layer-properties">
                <div class="opacity-control">
                  <label for="opacity-{layer.name}">Opacity:</label>
                  <input
                    id="opacity-{layer.name}"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={layer.opacity}
                    on:input={(e) => updateLayerOpacity(layer.name, parseFloat(e.target.value))}
                  />
                  <span class="opacity-value">{Math.round(layer.opacity * 100)}%</span>
                </div>

                <div class="z-index-display">
                  Z-Index: {layer.zIndex}
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .layer-control-panel {
    position: fixed;
    top: 60px;
    right: 20px;
    background-color: rgba(40, 40, 40, 0.95);
    border: 1px solid #555;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #fff;
    min-width: 250px;
    max-width: 300px;
  }

  .panel-header {
    padding: 8px;
  }

  .toggle-button {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    color: #fff;
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .toggle-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .icon {
    margin-right: 6px;
  }

  .panel-content {
    border-top: 1px solid #555;
    max-height: 400px;
    overflow-y: auto;
  }

  .no-layers {
    padding: 16px;
    text-align: center;
    color: #999;
    font-style: italic;
  }

  .layers-list {
    padding: 8px;
  }

  .layer-item {
    border: 1px solid #666;
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 8px;
    background-color: rgba(50, 50, 50, 0.5);
    transition: opacity 0.3s;
  }

  .layer-item.disabled {
    opacity: 0.5;
  }

  .layer-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }

  .visibility-toggle {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    margin-right: 8px;
    transition: opacity 0.2s;
  }

  .visibility-toggle:hover {
    opacity: 0.7;
  }

  .visibility-toggle.hidden {
    opacity: 0.3;
  }

  .layer-name {
    flex: 1;
    font-weight: 600;
    text-transform: capitalize;
  }

  .layer-controls {
    display: flex;
    gap: 4px;
  }

  .move-button {
    background: none;
    border: 1px solid #777;
    border-radius: 3px;
    color: #fff;
    cursor: pointer;
    font-size: 12px;
    padding: 2px 6px;
    transition: background-color 0.2s;
  }

  .move-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .layer-properties {
    font-size: 12px;
  }

  .opacity-control {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
  }

  .opacity-control label {
    margin-right: 8px;
    min-width: 50px;
  }

  .opacity-control input[type="range"] {
    flex: 1;
    margin-right: 8px;
  }

  .opacity-value {
    min-width: 30px;
    text-align: right;
    color: #ccc;
  }

  .z-index-display {
    color: #999;
    font-size: 11px;
  }

  /* Scrollbar styling */
  .panel-content::-webkit-scrollbar {
    width: 6px;
  }

  .panel-content::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
  }

  .panel-content::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
  }

  .panel-content::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
  }
</style> 