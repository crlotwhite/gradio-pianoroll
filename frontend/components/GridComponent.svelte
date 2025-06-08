<!--
  GridComponent for displaying and editing notes and lyrics.
  This component uses the layer system to render the grid, notes, and lyrics.
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { pixelsToFlicks, flicksToPixels, getExactNoteFlicks, roundFlicks, calculateAllTimingData } from '../utils/flicks';
  import { LayerManager, GridLayer, NotesLayer, WaveformLayer, LineLayer } from '../utils/layers';
  import LayerControlPanel from './LayerControlPanel.svelte';
  import type { LayerRenderContext, Note, LineLayerConfig, LineDataPoint } from '../types/layer';
  import { AudioEngineManager } from '../utils/audioEngine';

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

  // Backend audio data (추가)
  export let audio_data: string | null = null;
  export let curve_data: object | null = null;
  export let line_data: object | null = null;  // Line layer data
  export let use_backend_audio: boolean = false;

  // Constants
  const NOTE_HEIGHT = 20;  // Height of a note row (same as white key height)

  // Sizing and grid constants
  const TOTAL_NOTES = 128;  // Total MIDI notes
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

  // Get subdivisions based on snap setting (음악적 의미에 맞게)
  function getSubdivisionsFromSnapSetting(): { count: number, pixelsPerSubdivision: number } {
    if (snapSetting === 'none') {
      // Default to quarter note subdivisions if snap is 'none'
      return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
    }

    const [numerator, denominator] = snapSetting.split('/');
    if (numerator === '1' && denominator) {
      const divisionValue = parseInt(denominator);

      switch (divisionValue) {
        case 1: // Whole note - 4 beats
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat * 4 };
        case 2: // Half note - 2 beats
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat * 2 };
        case 4: // Quarter note - 1 beat
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
        case 8: // Eighth note - 0.5 beat
          return { count: 2, pixelsPerSubdivision: pixelsPerBeat / 2 };
        case 16: // Sixteenth note - 0.25 beat
          return { count: 4, pixelsPerSubdivision: pixelsPerBeat / 4 };
        case 32: // Thirty-second note - 0.125 beat
          return { count: 8, pixelsPerSubdivision: pixelsPerBeat / 8 };
        default:
          return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
      }
    }

    // Default to quarter note subdivisions
    return { count: 1, pixelsPerSubdivision: pixelsPerBeat };
  }

  // Derived grid constants based on time signature and snap setting
  $: subdivisions = getSubdivisionsFromSnapSetting();
  $: snapChanged = snapSetting; // Reactive variable to trigger redraw when snap changes

  // State
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  let isDragging = false;
  let isResizing = false;
  let isCreatingNote = false;
  let selectedNotes: Set<string> = new Set();
  let dragStartX = 0;
  let dragStartY = 0;
  let lastMouseX = 0;
  let lastMouseY = 0;
  let draggedNoteId: string | null = null;
  let resizedNoteId: string | null = null;
  let creationStartTime = 0;
  let creationPitch = 0;
  let noteOffsetX = 0; // Offset from mouse to note start for natural movement
  let noteOffsetY = 0; // Vertical offset for pitch adjustment

  let isNearNoteEdge = false; // Track if mouse is near a note edge for resize cursor

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

  // Lyric editing state
  let isEditingLyric = false;
  let editedNoteId: string | null = null;
  let lyricInputValue = '';
  let lyricInputPosition = { x: 0, y: 0, width: 0 };

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
        console.log('📊 GridComponent: verticalScroll updated to', verticalScroll);
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

    console.log('🖱️ Mouse down event triggered');

    // Ensure layers are properly initialized
    ensureLayersReady();

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    // Store initial position for drag operations
    dragStartX = x;
    dragStartY = y;
    lastMouseX = x;
    lastMouseY = y;



    // Reset offsets by default
    noteOffsetX = 0;
    noteOffsetY = 0;

    // Check if clicking on a note
    const clickedNote = findNoteAtPosition(x, y);
    console.log('🎯 Clicked note:', clickedNote ? `${clickedNote.id} at ${clickedNote.start}-${clickedNote.start + clickedNote.duration}, pitch ${clickedNote.pitch}` : 'none');

    if (editMode === 'draw' && !clickedNote) {
      // Start note creation process
      const pitch = Math.floor(y / NOTE_HEIGHT);
      const time = snapToGrid(x);

      // Store the starting position and pitch for the new note
      creationStartTime = time;
      creationPitch = TOTAL_NOTES - 1 - pitch;

      // Calculate initial note duration based on snap setting (음악적 의미에 맞게)
      let initialDuration = pixelsPerBeat; // Default: quarter note (1/4)

      // Parse the snap setting to determine initial note duration
      if (snapSetting !== 'none') {
        const [numerator, denominator] = snapSetting.split('/');
        if (numerator === '1' && denominator) {
          const divisionValue = parseInt(denominator);
          // Calculate duration in pixels based on snap setting
          // 음악적 의미에 맞는 duration 계산
          switch (divisionValue) {
            case 1: // Whole note - 4 beats
              initialDuration = pixelsPerBeat * 4;
              break;
            case 2: // Half note - 2 beats
              initialDuration = pixelsPerBeat * 2;
              break;
            case 4: // Quarter note - 1 beat
              initialDuration = pixelsPerBeat;
              break;
            case 8: // Eighth note - 0.5 beat
              initialDuration = pixelsPerBeat / 2;
              break;
            case 16: // Sixteenth note - 0.25 beat
              initialDuration = pixelsPerBeat / 4;
              break;
            case 32: // Thirty-second note - 0.125 beat
              initialDuration = pixelsPerBeat / 8;
              break;
            default:
              initialDuration = pixelsPerBeat; // Quarter note
          }
        }
      } else {
        // When snap is 'none', use a small default size
        initialDuration = pixelsPerBeat / 8;
      }

      // Calculate timing data for start position and duration
      const startTiming = calculateAllTimingData(time, pixelsPerBeat, tempo, sampleRate, ppqn);
      const durationTiming = calculateAllTimingData(initialDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

      // Create a new note with duration based on snap setting
      const newNote = {
        id: `note-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        start: time,
        duration: initialDuration,
        pitch: creationPitch,
        velocity: 100,
        lyric: '라',  // Default lyric is '라'
        startFlicks: startTiming.flicks,
        durationFlicks: durationTiming.flicks,
        startSeconds: startTiming.seconds,
        durationSeconds: durationTiming.seconds,
        endSeconds: startTiming.seconds + durationTiming.seconds,
        startBeats: startTiming.beats,
        durationBeats: durationTiming.beats,
        startTicks: startTiming.ticks,
        durationTicks: durationTiming.ticks,
        startSample: startTiming.samples,
        durationSamples: durationTiming.samples
      };

      // Add note to the collection
      notes = [...notes, newNote];

      // Set note as selected and being resized
      selectedNotes = new Set([newNote.id]);
      resizedNoteId = newNote.id;  // We're resizing, not dragging
      isCreatingNote = true;       // Flag that we're in note creation mode
      isResizing = true;          // Enable resizing mode

      dispatch('noteChange', { notes });
    }
    else if (editMode === 'erase' && clickedNote) {
      // Erase clicked note
      notes = notes.filter(note => note.id !== clickedNote.id);
      selectedNotes.delete(clickedNote.id);

      dispatch('noteChange', { notes });
    }
    else if (editMode === 'select') {
      if (clickedNote) {
        // Check if clicking near the end of the note (for resizing)
        const noteEndX = clickedNote.start + clickedNote.duration;
        // Edge detection threshold scales with zoom level
        const edgeDetectionThreshold = Math.max(5, Math.min(15, pixelsPerBeat / 8));
        if (Math.abs(x - noteEndX) < edgeDetectionThreshold) {
          // Start resizing - similar to draw mode
          isResizing = true;
          resizedNoteId = clickedNote.id;
          // Store the original note start position for absolute resizing calculation
          creationStartTime = clickedNote.start;
        } else {
          // Select and drag note
          if (!event.shiftKey) {
            // If not holding shift, clear previous selection
            if (!selectedNotes.has(clickedNote.id)) {
              selectedNotes = new Set([clickedNote.id]);
              console.log('🔘 Selected note:', clickedNote.id);
            }
          } else {
            // Add to selection with shift key
            selectedNotes.add(clickedNote.id);
            console.log('🔘 Added note to selection:', clickedNote.id, 'Total selected:', selectedNotes.size);
          }

          // Calculate offset from mouse position to note start for natural dragging
          // This maintains the relative position between mouse and note during drag
          noteOffsetX = clickedNote.start - x;
          noteOffsetY = (TOTAL_NOTES - 1 - clickedNote.pitch) * NOTE_HEIGHT - y;

          isDragging = true;
          draggedNoteId = clickedNote.id;
          console.log('🖱️ Started dragging note:', clickedNote.id);
          console.log('📏 Drag offsets:', { noteOffsetX, noteOffsetY });
        }
      } else {
        // Clicked empty space, clear selection unless shift is held
        if (!event.shiftKey) {
          selectedNotes = new Set();
        }
      }
    }

    // Redraw
    ensureLayersReady();
  }

  function handleMouseMove(event: MouseEvent) {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left + horizontalScroll;
    const y = event.clientY - rect.top + verticalScroll;

    const deltaX = x - lastMouseX;
    const deltaY = y - lastMouseY;

    lastMouseX = x;
    lastMouseY = y;

    // Update mouse position information
    updateMousePositionInfo(x, y);

    // Check if mouse is near any note edge for resize cursor
    if (editMode === 'select' && !isDragging && !isResizing) {
      const clickedNote = findNoteAtPosition(x, y);
      if (clickedNote) {
        const noteEndX = clickedNote.start + clickedNote.duration;
        // Edge detection threshold scales with zoom level
        const edgeDetectionThreshold = Math.max(5, Math.min(15, pixelsPerBeat / 8));
        // If mouse is within threshold pixels of the note edge, show resize cursor
        isNearNoteEdge = Math.abs(x - noteEndX) < edgeDetectionThreshold;
      } else {
        isNearNoteEdge = false;
      }
    }

    if (isDragging && draggedNoteId && editMode === 'select') {
      // Move selected notes to snap to grid positions
      notes = notes.map(note => {
        if (selectedNotes.has(note.id)) {
          // Calculate new position based on current mouse position with offset
          // Apply the offset to maintain the original click position relative to the note
          let newStart = x + noteOffsetX;
          let newPitchY = y + noteOffsetY;
          let newPitch = Math.floor(newPitchY / NOTE_HEIGHT);
          newPitch = TOTAL_NOTES - 1 - newPitch;

          // Snap to grid
          newStart = snapToGrid(newStart);

          // Ensure valid ranges
          newStart = Math.max(0, newStart);
          newPitch = Math.max(0, Math.min(127, newPitch));

          // console.log(`📍 Moving note ${note.id} to grid position ${newStart},${newPitch}`);

          // Calculate all timing data for new start position
          const newStartTiming = calculateAllTimingData(newStart, pixelsPerBeat, tempo, sampleRate, ppqn);

          return {
            ...note,
            start: newStart,
            pitch: newPitch,
            startFlicks: newStartTiming.flicks,
            startSeconds: newStartTiming.seconds,
            startBeats: newStartTiming.beats,
            startTicks: newStartTiming.ticks,
            startSample: newStartTiming.samples,
            endSeconds: newStartTiming.seconds + (note.durationSeconds || 0)
          };
        }
        return note;
      });

      dispatch('noteChange', { notes });
      renderLayers();
    }
    else if (isResizing && resizedNoteId) {
      // Resize note
      notes = notes.map(note => {
        if (note.id === resizedNoteId) {
          let newDuration;

          // Get the grid size based on snap setting (음악적 의미에 맞게)
          let gridSize;
          if (snapSetting === 'none') {
            // If snap is off, use a small default size for fine control
            gridSize = pixelsPerBeat / 32; // Very fine control
          } else {
            // Parse the snap setting fraction
            gridSize = pixelsPerBeat; // Default to quarter note (1/4)
            const [numerator, denominator] = snapSetting.split('/');
            if (numerator === '1' && denominator) {
              const divisionValue = parseInt(denominator);

              // 음악적 의미에 맞는 grid size 계산
              switch (divisionValue) {
                case 1: // Whole note - 4 beats
                  gridSize = pixelsPerBeat * 4;
                  break;
                case 2: // Half note - 2 beats
                  gridSize = pixelsPerBeat * 2;
                  break;
                case 4: // Quarter note - 1 beat
                  gridSize = pixelsPerBeat;
                  break;
                case 8: // Eighth note - 0.5 beat
                  gridSize = pixelsPerBeat / 2;
                  break;
                case 16: // Sixteenth note - 0.25 beat
                  gridSize = pixelsPerBeat / 4;
                  break;
                case 32: // Thirty-second note - 0.125 beat
                  gridSize = pixelsPerBeat / 8;
                  break;
                default:
                  gridSize = pixelsPerBeat;
              }
            }
          }

          // Use the same approach for both note creation and resize in select mode
          // Calculate width from the start position to the current mouse position
          const width = Math.max(gridSize, x - creationStartTime);

          // Snap the width to the grid based on current snap setting
          const snappedWidth = snapSetting === 'none'
            ? width
            : Math.round(width / gridSize) * gridSize;

          // Ensure minimum size
          newDuration = Math.max(gridSize, snappedWidth);

          // Calculate all timing data for new duration
          const newDurationTiming = calculateAllTimingData(newDuration, pixelsPerBeat, tempo, sampleRate, ppqn);

          return {
            ...note,
            duration: newDuration,
            durationFlicks: newDurationTiming.flicks,
            durationSeconds: newDurationTiming.seconds,
            durationBeats: newDurationTiming.beats,
            durationTicks: newDurationTiming.ticks,
            durationSamples: newDurationTiming.samples,
            endSeconds: (note.startSeconds || 0) + newDurationTiming.seconds
          };
        }
        return note;
      });

      dispatch('noteChange', { notes });
      renderLayers();
    }
  }

  function handleMouseUp() {
    // Check if we're finalizing note creation
    if (isCreatingNote) {
      // If the note is too small, remove it, but base minimum size on current snap setting
      if (resizedNoteId) {
        const createdNote = notes.find(note => note.id === resizedNoteId);

        // Calculate minimum note size based on snap setting (음악적 의미에 맞게)
        let minimumNoteSize;
        if (snapSetting === 'none') {
          minimumNoteSize = pixelsPerBeat / 32; // Tiny minimum size when snap is off
        } else {
          // Parse the snap setting fraction
          minimumNoteSize = pixelsPerBeat / 2; // Default to half quarter note
          const [numerator, denominator] = snapSetting.split('/');
          if (numerator === '1' && denominator) {
            const divisionValue = parseInt(denominator);

            // 음악적 의미에 맞는 minimum size 계산 (snap grid의 절반)
            switch (divisionValue) {
              case 1: // Whole note - 4 beats
                minimumNoteSize = (pixelsPerBeat * 4) / 2;
                break;
              case 2: // Half note - 2 beats
                minimumNoteSize = (pixelsPerBeat * 2) / 2;
                break;
              case 4: // Quarter note - 1 beat
                minimumNoteSize = pixelsPerBeat / 2;
                break;
              case 8: // Eighth note - 0.5 beat
                minimumNoteSize = (pixelsPerBeat / 2) / 2;
                break;
              case 16: // Sixteenth note - 0.25 beat
                minimumNoteSize = (pixelsPerBeat / 4) / 2;
                break;
              case 32: // Thirty-second note - 0.125 beat
                minimumNoteSize = (pixelsPerBeat / 8) / 2;
                break;
              default:
                minimumNoteSize = pixelsPerBeat / 2;
            }
          }
        }

        // Now check if the note is too small based on the dynamic minimum size
        if (createdNote && createdNote.duration < minimumNoteSize) {
          // Remove notes that are too small (likely accidental clicks)
          notes = notes.filter(note => note.id !== resizedNoteId);
          dispatch('noteChange', { notes });
        }
      }

      // Reset creation state
      isCreatingNote = false;
    }

    // Reset interaction states
    isDragging = false;
    isResizing = false;
    isNearNoteEdge = false; // Reset resize cursor state
    draggedNoteId = null;
    resizedNoteId = null;

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
      // Set up lyric editing state
      editedNoteId = clickedNote.id;
      lyricInputValue = clickedNote.lyric || '';

      // Calculate position for the input field
      const noteY = (TOTAL_NOTES - 1 - clickedNote.pitch) * NOTE_HEIGHT - verticalScroll;

      lyricInputPosition = {
        x: clickedNote.start - horizontalScroll,
        y: noteY,
        width: clickedNote.duration
      };

      isEditingLyric = true;

      // Set a timeout to focus the input element once it's rendered
      setTimeout(() => {
        const input = document.getElementById('lyric-input');
        if (input) {
          input.focus();
        }
      }, 10);
    }
  }

  // Save the edited lyric
  function saveLyric() {
    if (!editedNoteId) return;

    // 이전 가사와 새 가사 저장
    const oldNote = notes.find(note => note.id === editedNoteId);
    const oldLyric = oldNote?.lyric || '';
    const newLyric = lyricInputValue;

    // Update the note with the new lyric
    notes = notes.map(note => {
      if (note.id === editedNoteId) {
        return {
          ...note,
          lyric: newLyric
        };
      }
      return note;
    });

    // 가사가 실제로 변경된 경우에만 이벤트 발생
    if (oldLyric !== newLyric) {
      // 먼저 input 이벤트 발생 (G2P 실행용)
      dispatch('lyricInput', {
        notes,
        lyricData: {
          noteId: editedNoteId,
          oldLyric,
          newLyric,
          note: notes.find(note => note.id === editedNoteId)
        }
      });
    } else {
      // 가사가 변경되지 않은 경우 일반 노트 변경 이벤트만 발생
      dispatch('noteChange', { notes });
    }

    // Reset editing state
    isEditingLyric = false;
    editedNoteId = null;

    // Redraw with updated lyrics
    renderLayers();
  }

  // Handle keydown in the lyric input
  function handleLyricInputKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      saveLyric();
    } else if (event.key === 'Escape') {
      // Cancel editing
      isEditingLyric = false;
      editedNoteId = null;
    }
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

    console.log('📊 Updating line layers with data:', line_data);

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
            height: layerInfo.height || (isF0Data ? undefined : height / 3), // F0는 전체 높이, 나머지는 1/3
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

          console.log(`✅ Added line layer: ${layerName} with ${dataPoints.length} points (mode: ${config.renderMode})`);
        } catch (error) {
          console.error(`❌ Failed to create line layer ${layerName}:`, error);
        }
      });
    }

    console.log(`📊 Line layers updated: ${lineLayers.size} total layers`);
    console.log(`📊 LayerManager has ${layerManager.getLayerNames().length} layers:`, layerManager.getLayerNames());

    renderLayers();

    // Update layer control panel to show new line layers
    if (layerControlPanel) {
      console.log('🎛️ Updating layer control panel');
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
      const noteY = (TOTAL_NOTES - 1 - note.pitch) * NOTE_HEIGHT;
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

  // Coordinate conversion utility functions

  // Convert X coordinate to measure, beat, tick information
  function xToMeasureInfo(x: number) {
    // Calculate measure
    const measureIndex = Math.floor(x / pixelsPerMeasure);

    // Calculate beat within measure
    const xWithinMeasure = x - (measureIndex * pixelsPerMeasure);
    const beatWithinMeasure = Math.floor(xWithinMeasure / pixelsPerBeat);

    // Calculate tick within beat (based on current snap setting)
    let divisionValue = 4; // Default to quarter note (1/4)
    if (snapSetting !== 'none') {
      const [numerator, denominator] = snapSetting.split('/');
      if (numerator === '1' && denominator) {
        divisionValue = parseInt(denominator);
      }
    }

    const ticksPerBeat = divisionValue;
    const xWithinBeat = xWithinMeasure - (beatWithinMeasure * pixelsPerBeat);
    const tickWithinBeat = Math.floor((xWithinBeat / pixelsPerBeat) * ticksPerBeat);

    return {
      measure: measureIndex + 1, // 1-based measure number
      beat: beatWithinMeasure + 1, // 1-based beat number
      tick: tickWithinBeat,
      measureFraction: `${beatWithinMeasure + 1}/${ticksPerBeat}` // e.g. 2/4 for second beat in 4/4
    };
  }

  // Convert measure, beat, tick to X coordinate
  function measureInfoToX(measure: number, beat: number, tick: number, ticksPerBeat: number) {
    // Convert to 0-based indices
    const measureIndex = measure - 1;
    const beatIndex = beat - 1;

    // Calculate x position
    const measureX = measureIndex * pixelsPerMeasure;
    const beatX = beatIndex * pixelsPerBeat;
    const tickX = (tick / ticksPerBeat) * pixelsPerBeat;

    return measureX + beatX + tickX;
  }

  // Convert Y coordinate to MIDI pitch
  function yToPitch(y: number) {
    const pitchIndex = Math.floor(y / NOTE_HEIGHT);
    const pitch = TOTAL_NOTES - 1 - pitchIndex;

    // Convert MIDI pitch to note name (e.g. C4, F#5)
    const noteName = getMidiNoteName(pitch);

    return { pitch, noteName };
  }

  // Convert MIDI pitch to Y coordinate
  function pitchToY(pitch: number) {
    return (TOTAL_NOTES - 1 - pitch) * NOTE_HEIGHT;
  }

  // Get note name from MIDI pitch
  function getMidiNoteName(pitch: number) {
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const noteName = noteNames[pitch % 12];
    const octave = Math.floor(pitch / 12) - 1; // MIDI standard: C4 is 60
    return `${noteName}${octave}`;
  }

  // Update mouse position info
  function updateMousePositionInfo(x: number, y: number) {
    // Get measure, beat, tick info from x coordinate
    const measureInfo = xToMeasureInfo(x);

    // Get pitch info from y coordinate
    const pitchInfo = yToPitch(y);

    // Update current mouse position
    currentMousePosition = {
      x,
      y,
      measure: measureInfo.measure,
      beat: measureInfo.beat,
      tick: measureInfo.tick,
      pitch: pitchInfo.pitch,
      noteName: pitchInfo.noteName
    };

    // Emit position info event for parent components to use
    dispatch('positionInfo', currentMousePosition);
  }

  // Snap value to grid based on selected snap setting with higher precision (음악적 의미에 맞게)
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
      // Fallback to original calculation if snap setting is not recognized
      console.warn(`Unknown snap setting: ${snapSetting}, using fallback calculation`);

      // Parse the snap setting fraction
      let gridSize = pixelsPerBeat; // Default to quarter note (1/4)

      if (snapSetting !== 'none') {
        const [numerator, denominator] = snapSetting.split('/');
        if (numerator === '1' && denominator) {
          const divisionValue = parseInt(denominator);

          // 음악적 의미에 맞는 grid size 계산
          switch (divisionValue) {
            case 1: // Whole note - 4 beats
              gridSize = pixelsPerBeat * 4;
              break;
            case 2: // Half note - 2 beats
              gridSize = pixelsPerBeat * 2;
              break;
            case 4: // Quarter note - 1 beat
              gridSize = pixelsPerBeat;
              break;
            case 8: // Eighth note - 0.5 beat
              gridSize = pixelsPerBeat / 2;
              break;
            case 16: // Sixteenth note - 0.25 beat
              gridSize = pixelsPerBeat / 4;
              break;
            case 32: // Thirty-second note - 0.125 beat
              gridSize = pixelsPerBeat / 8;
              break;
            default:
              gridSize = pixelsPerBeat;
          }
        }
      }

      return Math.round(value / gridSize) * gridSize;
    }
  }

  // Convert beat position to pixel position
  function beatToPixel(beat: number) {
    return beat * pixelsPerBeat;
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
      console.log('⚠️ Cannot initialize layers: missing ctx or canvas');
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

    // 초기 웨이브폼 렌더링 시도 (백엔드 오디오를 사용하지 않는 경우)
    if (!use_backend_audio && waveformLayer) {
      // console.log('🌊 Initial waveform auto-render attempt on mount');
      setTimeout(() => {
        autoRenderFrontendAudio();
      }, 100); // 약간의 지연을 두어 다른 초기화가 완료된 후 실행
    }

    // Expose coordinate conversion utilities to parent components
    dispatch('utilsReady', {
      xToMeasureInfo,
      measureInfoToX,
      yToPitch,
      pitchToY,
      getMidiNoteName
    });
  });

  // Update waveform layer data when relevant props change
  function updateWaveformLayer() {
    if (!waveformLayer) return;

    // 1순위: curve_data에서 미리 계산된 웨이브폼 데이터 사용
    if (curve_data && (curve_data as any).waveform_data) {
      waveformLayer.setPreCalculatedWaveform((curve_data as any).waveform_data);
      waveformLayer.setUseBackendAudio(true);
      // console.log('🌊 WaveformLayer: Using pre-calculated waveform data');
      return;
    }

    // 2순위: 백엔드 오디오가 있고 use_backend_audio가 true인 경우
    if (use_backend_audio && audio_data) {
      // 백엔드 오디오는 별도로 디코딩해서 설정해야 함
      waveformLayer.setUseBackendAudio(true);
      // console.log('🌊 WaveformLayer: Using backend audio mode');
      return;
    }

    // 3순위: 프론트엔드 오디오 엔진 버퍼 사용
    const audioBuffer = audioEngine.getRenderedBuffer();
    if (audioBuffer) {
      waveformLayer.setAudioBuffer(audioBuffer);
      waveformLayer.setUseBackendAudio(false);
      // console.log('🌊 WaveformLayer: Using frontend audio buffer');
      return;
    }

    // 4순위: 백엔드 오디오를 사용하지 않고 버퍼가 없는 경우 자동 렌더링 시도
    if (!use_backend_audio && !audioBuffer) {
      // console.log('🌊 WaveformLayer: No buffer available, attempting auto-render');
      autoRenderFrontendAudio();
    }

    // 데이터가 없는 경우
    waveformLayer.setAudioBuffer(null);
    waveformLayer.setPreCalculatedWaveform(null);
    // console.log('🌊 WaveformLayer: No waveform data available');
  }

  // 자동으로 프론트엔드 오디오 렌더링을 시도하는 함수
  async function autoRenderFrontendAudio() {
    try {
      // console.log('🎵 Auto-rendering frontend audio for waveform...');

      // 오디오 엔진 초기화 (사용자 상호작용 없이 시도)
      audioEngine.initialize();

      // 총 길이 계산 (32 마디)
      const totalLengthInBeats = 32 * 4; // 32 measures * 4 beats per measure (4/4 time)

      // 노트 렌더링
      await audioEngine.renderNotes(notes, tempo, totalLengthInBeats, pixelsPerBeat);

      // 렌더링 완료 후 웨이브폼 업데이트
      const newAudioBuffer = audioEngine.getRenderedBuffer();
      if (newAudioBuffer && waveformLayer) {
        waveformLayer.setAudioBuffer(newAudioBuffer);
        waveformLayer.setUseBackendAudio(false);
        // console.log('✅ Auto-render completed, waveform updated');
        renderLayers();
      }
    } catch (error: any) {
      console.log('⚠️ Auto-render failed (expected if no user interaction):', error.message);
      // 실패는 정상적인 동작 (사용자 상호작용이 필요한 경우)
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

    // 노트가 변경되었고 백엔드 오디오를 사용하지 않는 경우 웨이브폼 자동 업데이트
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

  {#if isEditingLyric}
    <div
      class="lyric-input-container"
      style="
        left: {lyricInputPosition.x}px;
        top: {lyricInputPosition.y}px;
        width: {lyricInputPosition.width}px;
      "
    >
      <input
        id="lyric-input"
        type="text"
        bind:value={lyricInputValue}
        on:keydown={handleLyricInputKeydown}
        on:blur={saveLyric}
        class="lyric-input"
        aria-label="노트 가사 편집"
      />
    </div>
  {/if}

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

  .lyric-input-container {
    position: absolute;
    z-index: 10;
  }

  .lyric-input {
    width: 100%;
    height: 18px;
    background-color: #fff;
    border: 1px solid #1976D2;
    border-radius: 2px;
    font-size: 10px;
    padding: 0 4px;
    color: #333;
    box-sizing: border-box;
  }

  .lyric-input:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.4);
  }
</style>
