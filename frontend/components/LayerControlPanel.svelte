<!--
  LayerControlPanel.svelte
  UI panel for controlling visibility, opacity, and order of piano roll layers.
  - Props:
    - layerManager: LayerManager | null (manages layers)
    - visible: boolean (panel visibility)
  - Emits:
    - (none by default, but can be extended)
  - Usage:
    <LayerControlPanel layerManager={layerManager} visible={true} />
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { LayerManager, LineLayer } from '../utils/layers';
  /** @type {import('../../types/component').LayerControlPanelProps} */

  // Props
  export let layerManager: LayerManager | null = null;
  export let visible = false;

  const dispatch = createEventDispatcher();

  // Layer information - reactive with force update trigger
  let forceUpdate = 0;
  $: layerInfo = layerManager && forceUpdate >= 0 ? layerManager.getLayerInfo() : [];

  // Watch for layerManager changes and update automatically
  $: if (layerManager) {
    // Force reactive update when layerManager instance changes
    triggerUpdate();
  }

  // Force reactive update
  function triggerUpdate() {
    forceUpdate++;
  }

  // Export function to allow external updates
  export function updateLayers() {
    triggerUpdate();
  }

  function toggleLayerVisibility(layerName: string) {
    if (!layerManager) return;

    const layer = layerManager.getLayer(layerName);
    if (layer) {
      layerManager.setLayerVisible(layerName, !layer.isVisible());
      triggerUpdate();
      dispatch('layerChanged');
    }
  }

  function updateLayerOpacity(layerName: string, opacity: number) {
    if (!layerManager) return;

    layerManager.setLayerOpacity(layerName, opacity);
    triggerUpdate();
    dispatch('layerChanged');
  }

  function moveLayerUp(layerName: string) {
    console.log('📈 Moving layer up:', layerName);
    if (!layerManager) return;

    const allLayers = layerManager.getLayerInfo().sort((a, b) => a.zIndex - b.zIndex);
    const currentIndex = allLayers.findIndex(layer => layer.name === layerName);

    if (currentIndex === -1 || currentIndex >= allLayers.length - 1) {
      console.log('⚠️ Cannot move layer up - already at top or not found');
      return;
    }

    // 현재 레이어와 위의 레이어의 z-index를 교환
    const currentLayer = allLayers[currentIndex];
    const upperLayer = allLayers[currentIndex + 1];

    console.log(`🔄 Swapping layers: ${currentLayer.name} (${currentLayer.zIndex}) ↔ ${upperLayer.name} (${upperLayer.zIndex})`);

    layerManager.setLayerZIndex(currentLayer.name, upperLayer.zIndex);
    layerManager.setLayerZIndex(upperLayer.name, currentLayer.zIndex);

    // 즉시 UI 업데이트
    triggerUpdate();
    dispatch('layerChanged');
  }

  function moveLayerDown(layerName: string) {
    console.log('📉 Moving layer down:', layerName);
    if (!layerManager) return;

    const allLayers = layerManager.getLayerInfo().sort((a, b) => a.zIndex - b.zIndex);
    const currentIndex = allLayers.findIndex(layer => layer.name === layerName);

    if (currentIndex === -1 || currentIndex <= 0) {
      console.log('⚠️ Cannot move layer down - already at bottom or not found');
      return;
    }

    // 현재 레이어와 아래의 레이어의 z-index를 교환
    const currentLayer = allLayers[currentIndex];
    const lowerLayer = allLayers[currentIndex - 1];

    console.log(`🔄 Swapping layers: ${currentLayer.name} (${currentLayer.zIndex}) ↔ ${lowerLayer.name} (${lowerLayer.zIndex})`);

    layerManager.setLayerZIndex(currentLayer.name, lowerLayer.zIndex);
    layerManager.setLayerZIndex(lowerLayer.name, currentLayer.zIndex);

    // 즉시 UI 업데이트
    triggerUpdate();
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
          {#each layerInfo.sort((a, b) => b.zIndex - a.zIndex) as layer, index (layer.name + layer.zIndex)}
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
                    class:disabled={index === 0}
                    on:click={() => moveLayerUp(layer.name)}
                    title="Move forward (above other layers)"
                    disabled={index === 0}
                  >
                    🔼
                  </button>
                  <button
                    class="move-button"
                    class:disabled={index === layerInfo.length - 1}
                    on:click={() => moveLayerDown(layer.name)}
                    title="Move backward (below other layers)"
                    disabled={index === layerInfo.length - 1}
                  >
                    🔽
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
                    on:input={(e) => updateLayerOpacity(layer.name, parseFloat(e.currentTarget.value))}
                  />
                  <span class="opacity-value">{Math.round(layer.opacity * 100)}%</span>
                </div>

                <div class="z-index-display">
                  Z-Index: <span class="z-index-value">{layer.zIndex}</span>
                </div>

                <!-- Line layer specific controls -->
                {#if layerManager}
                  {@const layerInstance = layerManager.getLayer(layer.name)}
                  {#if layerInstance instanceof LineLayer}
                    {@const lineLayer = layerInstance}
                    {@const config = lineLayer.getConfig()}
                    <div class="line-layer-controls">
                      <div class="line-info">
                        <span class="line-label">Range:</span>
                        <span class="line-range">{config.yMin.toFixed(1)} ~ {config.yMax.toFixed(1)}</span>
                      </div>
                      <div class="line-info">
                        <span class="line-label">Position:</span>
                        <span class="line-position">{config.position}</span>
                      </div>
                      <div class="line-info">
                        <span class="line-label">Mode:</span>
                        <span class="line-mode">{config.renderMode === 'piano_grid' ? 'Piano Grid Aligned' : 'Fixed Position'}</span>
                      </div>
                      {#if config.dataType}
                        <div class="line-info">
                          <span class="line-label">Type:</span>
                          <span class="line-type">{config.dataType} ({config.unit || ''})</span>
                        </div>
                      {/if}
                      {#if lineLayer.hasData()}
                        <div class="line-info">
                          <span class="line-label">Points:</span>
                          <span class="line-data-count">{lineLayer.getData().length}</span>
                        </div>
                      {/if}
                    </div>
                  {/if}
                {/if}
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

  .move-button:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .move-button:disabled,
  .move-button.disabled {
    opacity: 0.3;
    cursor: not-allowed;
    pointer-events: none;
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

  .z-index-value {
    color: #4CAF50;
    font-weight: bold;
    font-family: 'Roboto Mono', monospace;
  }

  /* Line layer specific styles */
  .line-layer-controls {
    margin-top: 6px;
    padding: 6px;
    background-color: rgba(60, 60, 60, 0.3);
    border-radius: 3px;
    border-left: 3px solid #FF6B6B;
  }

  .line-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 2px;
    font-size: 10px;
  }

  .line-label {
    color: #aaa;
    font-weight: 500;
  }

  .line-range, .line-position, .line-data-count, .line-mode, .line-type {
    color: #ddd;
    font-family: 'Roboto Mono', monospace;
  }

  .line-range {
    color: #66BB6A;
  }

  .line-position {
    color: #42A5F5;
    text-transform: capitalize;
  }

  .line-data-count {
    color: #FFA726;
  }

  .line-mode {
    color: #E91E63;
    font-weight: 600;
  }

  .line-type {
    color: #9C27B0;
    text-transform: uppercase;
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