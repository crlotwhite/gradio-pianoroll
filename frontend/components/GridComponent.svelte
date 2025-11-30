<!--
  GridComponent for displaying and editing notes and lyrics.
  This component uses the layer system to render the grid, notes, and lyrics.
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { pixelsToFlicks, flicksToPixels, getExactNoteFlicks, roundFlicks, calculateAllTimingData } from '../utils/flicks';
  import { LayerManager, GridLayer, NotesLayer, WaveformLayer, LineLayer } from '../utils/layers';
  import LayerControlPanel from './LayerControlPanel.svelte';
  import LyricEditor from './LyricEditor.svelte';
  import type { LayerRenderContext, Note, LineLayerConfig, LineDataPoint, CoordinateConfig, MouseHandlerConfig, MouseState, EditMode } from '../types';
  import { AudioEngineManager } from '../utils/audioEngine';
  import { NOTE_HEIGHT, TOTAL_NOTES, DEFAULT_VELOCITY, DEFAULT_LYRIC } from '../utils/constants';
  import { getSubdivisionsFromSnapSetting as getSnapSubdivisions, getGridSizeFromSnap, getInitialNoteDuration, getMinimumNoteSize, snapToGrid as snapValueToGrid, snapDurationToGrid } from '../utils/snapUtils';
  import { createLogger } from '../utils/logger';
  import {
    xToMeasureInfo,
    measureInfoToX,
    yToPitch,
    pitchToY,
    getMidiNoteName,
    beatToPixel,
    pixelToBeat,
    getMousePositionInfo,
    clampPitch,
    calculateDragPitch,
  } from '../utils/coordinateUtils';
  import {
    createInitialMouseState,
    handleMouseDown as mouseHandlerDown,
    handleMouseMove as mouseHandlerMove,
    handleMouseUp as mouseHandlerUp,
  } from '../utils/mouseHandler';

  const log = createLogger('GridComponent');

  // Props
  export let width = 880;  // Width of the grid (total width - keyboard width)
  export let height = 520;  // Height of the grid
  export let notes: Array<{
    id: string,
    start: number,
    duration: number,
    startFlicks?: number,      // Optional for backward compatibility
    durationFlicks?: number,   // Optional for backward compatibility
    startSeconds?: number,     // Optional - seconds timing
    durationSeconds?: number,  // Optional - seconds timing
    endSeconds?: number,       // Optional - end time in seconds
    startBeats?: number,       // Optional - beats timing
    durationBeats?: number,    // Optional - beats timing
    startTicks?: number,       // Optional - MIDI ticks timing
    durationTicks?: number,    // Optional - MIDI ticks timing
    startSample?: number,      // Optional - sample timing
    durationSamples?: number,  // Optional - sample timing
    pitch: number,
    velocity: number,
    lyric?: string,
    phoneme?: string
  }> = [];
  // Tempo is used to calculate timing and note positioning
  export let tempo = 120;  // BPM

  // Calculate pixels per second based on tempo
  $: pixelsPerSecond = (tempo / 60) * pixelsPerBeat;
  export let timeSignature = { numerator: 4, denominator: 4 };
  export let editMode = 'draw';  // Current edit mode
  export let snapSetting = '1/8';  // Snap grid setting (1/1, 1/2, 1/4, 1/8, 1/16, 1/32, none)
  export let horizontalScroll = 0;  // Horizontal scroll position
  export let verticalScroll = 0;  // Vertical scroll position
  export let currentFlicks = 0;  // Current playback position in flicks (added for playhead tracking)
  export let isPlaying = false;  // Whether playback is active

  // Audio metadata
  export let sampleRate = 44100; // Audio sample rate
  export let ppqn = 480;         // MIDI pulses per quarter note
  export let elem_id = '';       // Component ID for audio engine management

  // Backend audio data
  export let audio_data: string | null = null;
  export let curve_data: object | null = null;
  export let line_data: object | null = null;  // Line layer data
  export let use_backend_audio: boolean = false;

  // Sizing and grid constants (NOTE_HEIGHT and TOTAL_NOTES imported from constants)
  export let pixelsPerBeat = 80;  // How many pixels wide a beat is (controls zoom level)

  // Get subdivisions based on time signature denominator
  function getSubdivisionsFromTimeSignature(denominator: number): { count: number, pixelsPerSubdivision: number } {
    // The number of subdivisions per beat depends on the denominator
    switch (denominator) {
      case 2: // Half note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      case 4: // Quarter note gets the beat
        return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
      case 8: // Eighth note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      case 16: // Sixteenth note gets the beat
        return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
      default:
        return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
    }
  }

  // Derived grid constants based on time signature and snap setting
  $: subdivisions = getSnapSubdivisions(snapSetting, pixelsPerBeat);
  $: snapChanged = snapSetting; // Reactive variable to trigger redraw when snap changes

  // State
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;

  // Mouse interaction state (managed by mouseHandler)
  let mouseState: MouseState = createInitialMouseState();

  // Reactive accessors for mouse state (for template and other uses)
  $: selectedNotes = mouseState.selectedNotes;
  $: isNearNoteEdge = mouseState.isNearNoteEdge;
  $: isResizing = mouseState.isResizing;

  // Layer system
  let layerManager: LayerManager;
  let gridLayer: GridLayer;
  let notesLayer: NotesLayer;
  let waveformLayer: WaveformLayer;
  let lineLayers: Map<string, LineLayer> = new Map();  // Dynamic line layers
  let showLayerControl = false;
  let layerControlPanel: LayerControlPanel;

  // Audio engine for waveform data
  $: audioEngine = AudioEngineManager.getInstance(elem_id || 'default');

  // Coordinate configuration for utility functions (reactive)
  $: coordinateConfig: CoordinateConfig = {
    pixelsPerBeat,
    beatsPerMeasure,
    snapSetting,
  };

  // Mouse handler configuration (reactive)
  $: mouseHandlerConfig: MouseHandlerConfig = {
    pixelsPerBeat,
    tempo,
    sampleRate,
    ppqn,
    snapSetting,
    horizontalScroll,
    verticalScroll,
  };

  // Current mouse position info (for position display)
  let currentMousePosition = {
    x: 0,
    y: 0,
    measure: 0,
    beat: 0,
    tick: 0,
    pitch: 0,
    noteName: ''
  }

  // Keep track of the previous zoom level for scaling
  let previousPixelsPerBeat = pixelsPerBeat;

  // Lyric editing state (used by LyricEditor component)
  let lyricEditorState = {
    isEditing: false,
    noteId: null as string | null,
    value: '',
    x: 0,
    y: 0,
    width: 40
  };

  const dispatch = createEventDispatcher();

  // Calculate various dimensions and metrics
  $: totalGridHeight = TOTAL_NOTES * NOTE_HEIGHT;
  $: beatsPerMeasure = timeSignature.numerator;
  $: pixelsPerMeasure = beatsPerMeasure * pixelsPerBeat;

  // Calculate how many measures to show based on width
  $: totalMeasures = 32;  // Adjustable
  $: totalGridWidth = totalMeasures * pixelsPerMeasure;

  // Handle scrolling
  function handleScroll(event: WheelEvent) {
    event.preventDefault();

    // Vertical scrolling with mouse wheel
    if (event.deltaY !== 0) {
      const newVerticalScroll = Math.max(
        0,
        Math.min(
          totalGridHeight - height,
          verticalScroll + event.deltaY
        )
      );

      if (newVerticalScroll !== verticalScroll) {
        verticalScroll = newVerticalScroll;
        log.debug('verticalScroll updated to', verticalScroll);
        dispatch('scroll', { horizontalScroll, verticalScroll });
      }
    }

    // Horizontal scrolling with shift+wheel or trackpad
    if (event.deltaX !== 0 || event.shiftKey) {
      const deltaX = event.deltaX || event.deltaY;
      const newHorizontalScroll = Math.max(
        0,
        Math.min(
          totalGridWidth - width,
          horizontalScroll + deltaX
        )
      );

      if (newHorizontalScroll !== horizontalScroll) {
        horizontalScroll = newHorizontalScroll;
        dispatch('scroll', { horizontalScroll, verticalScroll });
      }
            }

        // Redraw with new scroll positions
        renderLayers();
  }

  // Mouse events for note manipulation
  function handleMouseDown(event: MouseEvent) {
    if (!canvas) return;

    log.debug('Mouse down event triggered');

    // Ensure layers are properly initialized
    ensureLayersReady();

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Delegate to mouseHandler
    const result = mouseHandlerDown(
      x,
      y,
      editMode as EditMode,
      event.shiftKey,
      notes,
      mouseState,
      mouseHandlerConfig,
      findNoteAtPosition,
      snapToGrid
    );

    // Update state
    mouseState = result.state;
    notes = result.notes;

    if (result.notesChanged) {
      dispatch('noteChange', { notes });
    }

    // Redraw
    ensureLayersReady();
  }

  function handleMouseMove(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Update mouse position information
    updateMousePositionInfo(x, y);

    // Delegate to mouseHandler
    const result = mouseHandlerMove(
      x,
      y,
      editMode as EditMode,
      notes,
      mouseState,
      mouseHandlerConfig,
      findNoteAtPosition,
      snapToGrid
    );

    // Update state
    mouseState = result.state;
    notes = result.notes;

    if (result.notesChanged) {
      dispatch('noteChange', { notes });
    }

    if (result.needsRedraw) {
      renderLayers();
    }
  }

  function handleMouseUp() {
    // Delegate to mouseHandler
    const result = mouseHandlerUp(notes, mouseState, mouseHandlerConfig);

    // Update state
    mouseState = result.state;
    notes = result.notes;

    if (result.notesChanged) {
      dispatch('noteChange', { notes });
    }

    // Redraw the grid
    renderLayers();
  }

  // Handle double-click to edit lyrics
  function handleDoubleClick(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Find the note that was double-clicked
    const clickedNote = findNoteAtPosition(x, y);

    if (clickedNote) {
      // Calculate screen position for the input field
      const noteY = pitchToY(clickedNote.pitch) - verticalScroll;

      // Update lyric editor state
      lyricEditorState = {
        isEditing: true,
        noteId: clickedNote.id,
        value: clickedNote.lyric || '',
        x: clickedNote.start - horizontalScroll,
        y: noteY,
        width: Math.max(40, clickedNote.duration) // Minimum width for usability
      };
    }
  }

  // Handle lyric save from LyricEditor component
  function handleLyricSave(event: CustomEvent<{ noteId: string; oldValue: string; newValue: string }>) {
    const { noteId, oldValue, newValue } = event.detail;

    // Update the note with the new lyric
    notes = notes.map(note => {
      if (note.id === noteId) {
        return {
          ...note,
          lyric: newValue
        };
      }
      return note;
    });

    // Dispatch event only if lyric actually changed
    if (oldValue !== newValue) {
      // Dispatch input event first (for G2P execution)
      dispatch('lyricInput', {
        notes,
        lyricData: {
          noteId,
          oldLyric: oldValue,
          newLyric: newValue,
          note: notes.find(note => note.id === noteId)
        }
      });
    } else {
      // Dispatch only note change event if lyric didn't change
      dispatch('noteChange', { notes });
    }

    // Reset editing state
    lyricEditorState = { ...lyricEditorState, isEditing: false, noteId: null };

    // Redraw with updated lyrics
    renderLayers();
  }

  // Handle lyric cancel from LyricEditor component
  function handleLyricCancel() {
    lyricEditorState = { ...lyricEditorState, isEditing: false, noteId: null };
  }

  // Handle global keyboard shortcuts
  function handleKeydown(event: KeyboardEvent) {
    // L key to toggle layer control panel
    if (event.key === 'l' || event.key === 'L') {
      showLayerControl = !showLayerControl;
      event.preventDefault();
    }
  }

  // Dynamic line layer management
  function updateLineLayers() {
    if (!layerManager || !line_data) return;

    log.debug('Updating line layers with data:', line_data);

    // Clear existing line layers
    for (const [name, layer] of lineLayers) {
      layerManager.removeLayer(name);
    }
    lineLayers.clear();

    // Add new line layers based on line_data
    if (typeof line_data === 'object' && line_data !== null) {
      const layerConfigs = line_data as Record<string, any>;

      Object.entries(layerConfigs).forEach(([layerName, layerInfo], index) => {
        try {
          // Default colors for different types of data
          const defaultColors = [
            '#FF6B6B', // Red
            '#4ECDC4', // Teal
            '#45B7D1', // Blue
            '#96CEB4', // Green
            '#FFEAA7', // Yellow
            '#DDA0DD', // Plum
            '#F39C12', // Orange
            '#9B59B6'  // Purple
          ];

          // Determine if this is F0/pitch data that should follow piano grid
          const isF0Data = layerName.toLowerCase().includes('f0') ||
                          layerName.toLowerCase().includes('pitch') ||
                          layerInfo.dataType === 'f0' ||
                          layerInfo.renderMode === 'piano_grid';

          const config: LineLayerConfig = {
            name: layerName,
            color: layerInfo.color || defaultColors[index % defaultColors.length],
            lineWidth: layerInfo.lineWidth || 2,
            yMin: layerInfo.yMin || 0,
            yMax: layerInfo.yMax || 1,
            height: layerInfo.height || (isF0Data ? undefined : height / 3), // F0 uses full height, others use 1/3
            position: isF0Data ? 'overlay' : (layerInfo.position || 'bottom'),
            renderMode: isF0Data ? 'piano_grid' : 'default',
            visible: layerInfo.visible !== false,
            opacity: layerInfo.opacity || (isF0Data ? 0.8 : 1.0),
            dataType: layerInfo.dataType,
            unit: layerInfo.unit,
            originalRange: layerInfo.originalRange
          };

          const lineLayer = new LineLayer(config);

          // Convert data points if necessary
          const dataPoints: LineDataPoint[] = [];
          if (layerInfo.data && Array.isArray(layerInfo.data)) {
            for (const point of layerInfo.data) {
              if (typeof point === 'object' && point !== null) {
                // Support different data formats
                let x: number, y: number;

                if ('x' in point && 'y' in point) {
                  x = point.x;
                  y = point.y;
                } else if ('time' in point && 'value' in point) {
                  // Convert time to pixels
                  x = point.time * pixelsPerBeat * (tempo / 60);
                  y = point.value;
                } else if ('seconds' in point && 'value' in point) {
                  // Convert seconds to pixels
                  x = point.seconds * pixelsPerBeat * (tempo / 60);
                  y = point.value;
                } else {
                  console.warn(`Unknown data point format for layer ${layerName}:`, point);
                  continue;
                }

                dataPoints.push({ x, y });
              }
            }
          }

          lineLayer.setData(dataPoints);
          lineLayers.set(layerName, lineLayer);
          layerManager.addLayer(lineLayer);

          log.debug(`Added line layer: ${layerName} with ${dataPoints.length} points (mode: ${config.renderMode})`);
        } catch (error) {
          console.error(`❌ Failed to create line layer ${layerName}:`, error);
        }
      });
    }

    log.debug(`Line layers updated: ${lineLayers.size} total layers`);
    log.debug(`LayerManager has ${layerManager.getLayerNames().length} layers:`, layerManager.getLayerNames());

    renderLayers();

    // Update layer control panel to show new line layers
    if (layerControlPanel) {
      log.debug('Updating layer control panel');
      layerControlPanel.updateLayers();
    }
  }

  // Layer control event handlers
  function handleLayerChanged() {
    renderLayers();
  }

  // Helper to find a note at a specific position
  // x, y are already world coordinates (screen coordinates + scroll)
  function findNoteAtPosition(x: number, y: number) {
    // console.log('🔍 Finding note at position:', x, y);

    if (notesLayer) {
      // Convert world coordinates back to screen coordinates for the layer function
      const screenX = x - horizontalScroll;
      const screenY = y - verticalScroll;
      const foundNotes = notesLayer.findNotesAtPosition(screenX, screenY, horizontalScroll, verticalScroll);
      // console.log('🎵 Found notes via layer:', foundNotes.length);
      return foundNotes.length > 0 ? foundNotes[0] : null;
    }

    // Fallback to original implementation using world coordinates
    // console.log('⚠️ Using fallback note finding');
    const foundNote = notes.find(note => {
      const noteY = pitchToY(note.pitch);
      return (
        x >= note.start &&
        x <= note.start + note.duration &&
        y >= noteY &&
        y <= noteY + NOTE_HEIGHT
      );
    });
    // console.log('🎵 Found note via fallback:', !!foundNote);
    return foundNote;
  }

  // --- Coordinate conversion wrapper functions ---
  // These functions wrap the imported coordinateUtils with component-local config

  // Update mouse position info using coordinateUtils
  function updateMousePositionInfo(x: number, y: number) {
    const positionInfo = getMousePositionInfo(x, y, coordinateConfig);

    // Update current mouse position
    currentMousePosition = positionInfo;

    // Emit position info event for parent components to use
    dispatch('positionInfo', currentMousePosition);
  }

  // Convert X coordinate to measure info (local wrapper)
  function localXToMeasureInfo(x: number) {
    return xToMeasureInfo(x, coordinateConfig);
  }

  // Convert measure info to X (local wrapper)
  function localMeasureInfoToX(measure: number, beat: number, tick: number, ticksPerBeat: number) {
    return measureInfoToX(measure, beat, tick, ticksPerBeat, coordinateConfig);
  }

  // Convert beat to pixel (local wrapper)
  function localBeatToPixel(beat: number) {
    return beatToPixel(beat, pixelsPerBeat);
  }

  // Snap value to grid based on selected snap setting with higher precision
  function snapToGrid(value: number) {
    // If snap is set to 'none', return the exact value
    if (snapSetting === 'none') {
      return value;
    }

    try {
      // Use the precise note flicks calculation for better accuracy
      const exactNoteFlicks = getExactNoteFlicks(snapSetting, tempo);
      const exactNotePixels = flicksToPixels(exactNoteFlicks, pixelsPerBeat, tempo);

      // Round to nearest grid position
      return Math.round(value / exactNotePixels) * exactNotePixels;
    } catch (error) {
      // Fallback to utility function if snap setting is not recognized
      log.warn(`Unknown snap setting: ${snapSetting}, using fallback calculation`);
      return snapValueToGrid(value, snapSetting, pixelsPerBeat);
    }
  }

  // Render using layer system
  function renderLayers() {
    if (!ctx || !canvas) return;

    // Ensure layer system is initialized
    if (!layerManager) {
      initializeLayers();
      if (!layerManager) return; // Still not initialized
    }

    // Create render context
    const renderContext: LayerRenderContext = {
      canvas,
      ctx,
      width,
      height,
      horizontalScroll,
      verticalScroll,
      pixelsPerBeat,
      tempo,
      currentFlicks,
      isPlaying,
      timeSignature,
      snapSetting
    };

    // Update notes layer with current data
    if (notesLayer) {
      notesLayer.setNotes(notes as Note[]);
      notesLayer.setSelectedNotes(selectedNotes);
    }

    // Render all layers
    layerManager.renderAllLayers(renderContext);
  }

  // Initialize layer system
  function initializeLayers() {
    if (!ctx || !canvas) {
      log.warn('Cannot initialize layers: missing ctx or canvas');
      return;
    }

    // console.log('🎨 Initializing layer system...');

    // Create layer manager
    layerManager = new LayerManager();

    // Create and add layers
    gridLayer = new GridLayer();
    notesLayer = new NotesLayer();
    waveformLayer = new WaveformLayer();

    layerManager.addLayer(gridLayer);
    layerManager.addLayer(waveformLayer);
    layerManager.addLayer(notesLayer);

    // console.log('✅ Layer system initialized with layers:', layerManager.getLayerNames());
    // console.log('Layer info:', layerManager.getLayerInfo());
  }

  // Legacy function name for compatibility
  function drawGrid() {
    renderLayers();
  }

  // Ensure proper initialization and rendering
  function ensureLayersReady() {
    if (!layerManager || !ctx || !canvas) {
      initializeLayers();
    }
    if (layerManager && ctx && canvas) {
      renderLayers();
    }
  }

  // Calculate the initial scroll position to center A3
  function calculateInitialScrollPosition() {
    // MIDI note number for A3 is 57 (9 semitones above C3 which is 48)
    const A3_MIDI_NOTE = 57;

    // Calculate the position of A3 in the grid
    const A3_INDEX = TOTAL_NOTES - 1 - A3_MIDI_NOTE;
    const A3_POSITION = A3_INDEX * NOTE_HEIGHT;

    // Calculate scroll position to center A3 vertically
    // Subtract half the grid height to center it
    const centeredScrollPosition = Math.max(0, A3_POSITION - (height / 2));

    return centeredScrollPosition;
  }

  // Set up the component
  onMount(() => {
    // Get canvas context
    ctx = canvas.getContext('2d');

    // Set up canvas size
    canvas.width = width;
    canvas.height = height;

    // Initialize layer system
    initializeLayers();

    // Set initial scroll position to center C3
    verticalScroll = calculateInitialScrollPosition();

    // Notify parent of scroll position
    dispatch('scroll', { horizontalScroll, verticalScroll });

    // Draw initial grid using layer system
    renderLayers();

    // Set initial mouse position info for the center of the viewport
    const centerX = horizontalScroll + width / 2;
    const centerY = verticalScroll + height / 2;
    updateMousePositionInfo(centerX, centerY);

    // Initial waveform render attempt (when not using backend audio)
    if (!use_backend_audio && waveformLayer) {
      // console.log('🌊 Initial waveform auto-render attempt on mount');
      setTimeout(() => {
        autoRenderFrontendAudio();
      }, 100); // Delay slightly to run after other initialization is complete
    }

    // Expose coordinate conversion utilities to parent components
    // Wrap imported functions with local config for convenience
    dispatch('utilsReady', {
      xToMeasureInfo: (x: number) => xToMeasureInfo(x, coordinateConfig),
      measureInfoToX: (measure: number, beat: number, tick: number, ticksPerBeat: number) =>
        measureInfoToX(measure, beat, tick, ticksPerBeat, coordinateConfig),
      yToPitch,
      pitchToY,
      getMidiNoteName
    });
  });

  // Update waveform layer data when relevant props change
  function updateWaveformLayer() {
    if (!waveformLayer) return;

    // Priority 1: Use pre-calculated waveform data from curve_data
    if (curve_data && (curve_data as any).waveform_data) {
      waveformLayer.setPreCalculatedWaveform((curve_data as any).waveform_data);
      waveformLayer.setUseBackendAudio(true);
      // console.log('🌊 WaveformLayer: Using pre-calculated waveform data');
      return;
    }

    // Priority 2: Backend audio is available and use_backend_audio is true
    if (use_backend_audio && audio_data) {
      // Backend audio needs to be decoded and set separately
      waveformLayer.setUseBackendAudio(true);
      // console.log('🌊 WaveformLayer: Using backend audio mode');
      return;
    }

    // Priority 3: Use frontend audio engine buffer
    const audioBuffer = audioEngine.getRenderedBuffer();
    if (audioBuffer) {
      waveformLayer.setAudioBuffer(audioBuffer);
      waveformLayer.setUseBackendAudio(false);
      // console.log('🌊 WaveformLayer: Using frontend audio buffer');
      return;
    }

    // Priority 4: Try auto-render when not using backend audio and no buffer available
    if (!use_backend_audio && !audioBuffer) {
      // console.log('🌊 WaveformLayer: No buffer available, attempting auto-render');
      autoRenderFrontendAudio();
    }

    // No data available
    waveformLayer.setAudioBuffer(null);
    waveformLayer.setPreCalculatedWaveform(null);
    // console.log('🌊 WaveformLayer: No waveform data available');
  }

  // Function to automatically attempt frontend audio rendering
  async function autoRenderFrontendAudio() {
    try {
      // console.log('🎵 Auto-rendering frontend audio for waveform...');

      // Initialize audio engine (attempt without user interaction)
      audioEngine.initialize();

      // Calculate total length (32 measures)
      const totalLengthInBeats = 32 * 4; // 32 measures * 4 beats per measure (4/4 time)

      // Render notes
      await audioEngine.renderNotes(notes, tempo, totalLengthInBeats, pixelsPerBeat);

      // Update waveform after rendering is complete
      const newAudioBuffer = audioEngine.getRenderedBuffer();
      if (newAudioBuffer && waveformLayer) {
        waveformLayer.setAudioBuffer(newAudioBuffer);
        waveformLayer.setUseBackendAudio(false);
        // console.log('✅ Auto-render completed, waveform updated');
        renderLayers();
      }
    } catch (error: any) {
      log.debug('Auto-render failed (expected if no user interaction):', error.message);
      // Failure is normal behavior (when user interaction is required)
    }
  }

  // Update when props change
  $: {
    if (ctx && canvas) {
      canvas.width = width;
      canvas.height = height;
      if (layerManager) {
        updateWaveformLayer();
        renderLayers();
      } else {
        initializeLayers();
        updateWaveformLayer();
        renderLayers();
      }
    }
  }

  // Re-render grid when playhead position changes during playback
  $: if (isPlaying && currentFlicks && layerManager) {
    renderLayers();
  }

  // Redraw when time signature changes
  $: if (timeSignature && ctx && canvas && layerManager) {
    // This will reactively update when timeSignature.numerator or denominator changes
    renderLayers();
  }

  // Redraw when snap setting changes
  $: if (snapChanged && ctx && canvas && layerManager) {
    // This will reactively update when snapSetting changes
    renderLayers();
  }

  // Redraw and scale notes when zoom level (pixelsPerBeat) changes
  $: {
    if (pixelsPerBeat !== previousPixelsPerBeat) {
      // Scale existing notes when zoom level changes
      scaleNotesForZoom();
      previousPixelsPerBeat = pixelsPerBeat;
    }
    if (layerManager) {
      renderLayers();
    }
  }

  // Re-render grid when notes array changes
  $: if (notes && layerManager) {
    renderLayers();

    // Auto-update waveform when notes change and not using backend audio
    if (!use_backend_audio && waveformLayer && !audioEngine.getRenderedBuffer()) {
      // console.log('🌊 Notes changed, auto-updating waveform');
      setTimeout(() => {
        autoRenderFrontendAudio();
      }, 50);
    }
  }

  // Update waveform layer when audio data changes
  $: if (layerManager && waveformLayer && (audio_data || curve_data || use_backend_audio !== undefined)) {
    updateWaveformLayer();
    renderLayers();
  }

  // Update line layers when line_data changes
  $: if (layerManager && line_data !== undefined) {
    updateLineLayers();
  }

  // Update waveform layer when audio engine renders new audio
  $: if (layerManager && waveformLayer && audioEngine) {
    const audioBuffer = audioEngine.getRenderedBuffer();
    if (audioBuffer && !use_backend_audio) {
      waveformLayer.setAudioBuffer(audioBuffer);
      waveformLayer.setUseBackendAudio(false);
      renderLayers();
    }
  }

  // Scale the position of notes when the zoom level (pixelsPerBeat) changes
  function scaleNotesForZoom() {
    if (notes.length === 0 || !previousPixelsPerBeat) return;

    const scaleFactor = pixelsPerBeat / previousPixelsPerBeat;

    // Scale the start positions of all notes
    notes = notes.map(note => ({
      ...note,
      // Maintain relative position by scaling the start time
      start: note.start * scaleFactor,
      // Scale the duration proportionally
      duration: note.duration * scaleFactor,
      // Update flicks values to match the new pixel positions
      startFlicks: pixelsToFlicks(note.start * scaleFactor, pixelsPerBeat, tempo),
      durationFlicks: pixelsToFlicks(note.duration * scaleFactor, pixelsPerBeat, tempo)
    }));

    // Notify parent of note changes
    dispatch('noteChange', { notes });
  }
</script>

<div class="grid-container">
  <canvas
    bind:this={canvas}
    width={width}
    height={height}
    on:wheel={handleScroll}
    on:mousedown={handleMouseDown}
    on:mousemove={handleMouseMove}
    on:mouseup={handleMouseUp}
    on:mouseleave={handleMouseUp}
    on:dblclick={handleDoubleClick}
    class="grid-canvas
      {editMode === 'select' ? 'select-mode' : ''}
      {editMode === 'draw' ? 'draw-mode' : ''}
      {editMode === 'erase' ? 'erase-mode' : ''}
      {isNearNoteEdge || isResizing ? (editMode !== 'draw' ? 'resize-possible' : '') : ''}"
  ></canvas>

  <!-- Layer Control Panel -->
  {#if layerManager}
    <LayerControlPanel
      bind:this={layerControlPanel}
      {layerManager}
      visible={showLayerControl}
      on:layerChanged={handleLayerChanged}
    />
  {/if}

  <!-- Lyric Editor Component -->
  <LyricEditor
    isEditing={lyricEditorState.isEditing}
    noteId={lyricEditorState.noteId}
    value={lyricEditorState.value}
    x={lyricEditorState.x}
    y={lyricEditorState.y}
    width={lyricEditorState.width}
    on:save={handleLyricSave}
    on:cancel={handleLyricCancel}
  />

  <!-- Position info display -->
  <div class="position-info" aria-live="polite">
    <div class="position-measure">Measure: {currentMousePosition.measure}, Beat: {currentMousePosition.beat}, Tick: {currentMousePosition.tick}</div>
    <div class="position-note">Note: {currentMousePosition.noteName} (MIDI: {currentMousePosition.pitch})</div>
  </div>

  <!-- Layer system status -->
  <div class="layer-info" aria-live="polite">
    <div class="layer-status">
      {#if layerManager}
        🎨 Layers: {layerManager.getLayerNames().length} | Press 'L' for controls
      {:else}
        ⚠️ Layer system not initialized
      {/if}
    </div>
  </div>
</div>

<!-- Add global keydown event handler -->
<svelte:window on:keydown={handleKeydown} />

<style>
  .grid-container {
    position: relative;
    height: 100%;
  }

  .position-info {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'Roboto Mono', monospace, sans-serif;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    pointer-events: none; /* Allow clicks to pass through */
    z-index: 10;
    transition: opacity 0.2s ease;
  }

  .position-measure {
    margin-bottom: 3px;
    opacity: 0.9;
  }

  .position-note {
    font-weight: 500;
    color: #90caf9;
  }

  .layer-info {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background-color: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'Roboto Mono', monospace, sans-serif;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    pointer-events: none;
    z-index: 10;
    transition: opacity 0.2s ease;
  }

  .layer-status {
    color: #90caf9;
    font-weight: 500;
  }

  .grid-canvas {
    display: block;
    cursor: crosshair; /* Default cursor for generic mode */
  }

  /* Cursor styles based on edit mode and interactions */
  .grid-canvas.select-mode {
    cursor: default; /* Normal cursor for select mode */
  }

  .grid-canvas.draw-mode {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M21.1,2.9c-0.8-0.8-2.1-0.8-2.9,0L6.9,15.2l-1.8,5.3l5.3-1.8L22.6,6.5c0.8-0.8,0.8-2.1,0-2.9L21.1,2.9z M6.7,19.3l1-2.9l1.9,1.9L6.7,19.3z'/%3E%3C/svg%3E") 0 24, auto; /* Pencil cursor for draw mode */
  }

  /* Draw mode cursor takes precedence over resize cursor */
  .grid-canvas.draw-mode.resize-possible {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M21.1,2.9c-0.8-0.8-2.1-0.8-2.9,0L6.9,15.2l-1.8,5.3l5.3-1.8L22.6,6.5c0.8-0.8,0.8-2.1,0-2.9L21.1,2.9z M6.7,19.3l1-2.9l1.9,1.9L6.7,19.3z'/%3E%3C/svg%3E") 0 24, auto !important; /* Pencil cursor with higher specificity */
  }

  .grid-canvas.erase-mode {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23ffffff' stroke='%23000000' stroke-width='0.5' d='M18.3,8.3L15.7,5.7c-0.4-0.4-1-0.4-1.4,0L3.7,16.3c-0.4,0.4-0.4,1,0,1.4l2.6,2.6c0.4,0.4,1,0.4,1.4,0L18.3,9.7C18.7,9.3,18.7,8.7,18.3,8.3z M6.3,18.9L5.1,17.7l9.9-9.9l1.2,1.2L6.3,18.9z'/%3E%3C/svg%3E") 0 24, auto; /* Eraser cursor for erase mode */
  }

  .grid-canvas.resize-possible {
    cursor: ew-resize; /* Left-right resize cursor when hovering over note edges */
  }
</style>
