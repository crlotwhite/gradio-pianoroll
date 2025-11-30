<!--
  Main PianoRoll component that integrates all subcomponents.
  This component serves as the container for the entire piano roll interface.
  Now with playback functionality using Flicks timing, waveform visualization, and playhead.
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Toolbar from './Toolbar.svelte';
  import KeyboardComponent from './KeyboardComponent.svelte';
  import GridComponent from './GridComponent.svelte';
  import TimeLineComponent from './TimeLineComponent.svelte';
  import PlayheadComponent from './PlayheadComponent.svelte';
  import DebugComponent from './DebugComponent.svelte';
  import { AudioEngineManager } from '../utils/audioEngine';
  import { BackendAudioEngine } from '../utils/backendAudioEngine';
  import { beatsToFlicks, flicksToBeats, formatFlicks } from '../utils/flicks';
  import { createEventDispatcher } from 'svelte';
  import {
    DEFAULT_PIXELS_PER_BEAT,
    MIN_PIXELS_PER_BEAT,
    MAX_PIXELS_PER_BEAT,
    ZOOM_STEP,
    DEFAULT_KEYBOARD_WIDTH,
    DEFAULT_TIMELINE_HEIGHT,
    DEFAULT_PIANOROLL_WIDTH,
    DEFAULT_PIANOROLL_HEIGHT,
    DEFAULT_TEMPO,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_PPQN,
    DEFAULT_SNAP_SETTING,
    DEFAULT_EDIT_MODE
  } from '../utils/constants';
  import { createLogger } from '../utils/logger';

  const log = createLogger('PianoRoll');

  /**
   * @typedef {import('../../types/component').PianoRollProps} PianoRollProps
   */

  // Create event dispatcher
  const dispatch = createEventDispatcher();

  // Props (values injected from parent)
  /** @type {number} */
  export let width = DEFAULT_PIANOROLL_WIDTH;  // Total width of the piano roll
  /** @type {number} */
  export let height = DEFAULT_PIANOROLL_HEIGHT;  // Total height of the piano roll
  /** @type {number} */
  export let keyboardWidth = DEFAULT_KEYBOARD_WIDTH; // Width of the keyboard component
  /** @type {number} */
  export let timelineHeight = DEFAULT_TIMELINE_HEIGHT; // Height of the timeline component
  /** @type {string} */
  export let elem_id = '';  // Component unique ID

  /** @type {string | null} */
  export let audio_data: string | null = null;
  /** @type {object | null} */
  export let curve_data: object | null = null;
  /** @type {object | null} */
  export let line_data: object | null = null;  // Line layer data
  /** @type {boolean} */
  export let use_backend_audio: boolean = false;

  /** @type {Array<PianoRollProps['notes'][0]>} */
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

  // Settings
  /** @type {number} */
  export let tempo = DEFAULT_TEMPO;
  /** @type {{ numerator: number, denominator: number }} */
  export let timeSignature = { numerator: 4, denominator: 4 };
  /** @type {string} */
  export let editMode = DEFAULT_EDIT_MODE; // 'select', 'draw', 'erase', etc.
  /** @type {string} */
  export let snapSetting = DEFAULT_SNAP_SETTING; // Default snap setting: 1/4

  // Audio metadata
  /** @type {number} */
  export let sampleRate = DEFAULT_SAMPLE_RATE; // Audio sample rate
  /** @type {number} */
  export let ppqn = DEFAULT_PPQN;         // MIDI pulses per quarter note

  // Zoom level (pixels per beat) - now controlled from parent
  /** @type {number} */
  export let pixelsPerBeat = DEFAULT_PIXELS_PER_BEAT;

  // Zoom in function
  /**
   * Zoom in the piano roll by increasing pixelsPerBeat.
   * Dispatches a data change event if zoom is possible.
   */
  function zoomIn() {
    if (pixelsPerBeat < MAX_PIXELS_PER_BEAT) {
      pixelsPerBeat += ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // Zoom out function
  /**
   * Zoom out the piano roll by decreasing pixelsPerBeat.
   * Dispatches a data change event if zoom is possible.
   */
  function zoomOut() {
    if (pixelsPerBeat > MIN_PIXELS_PER_BEAT) {
      pixelsPerBeat -= ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // State variables (internal state)
  // Playback state
  let isPlaying = false;
  let isRendering = false;
  let currentFlicks = 0;

  // Scroll positions
  let horizontalScroll = 0;
  let verticalScroll = 0;

  // References to DOM elements
  let containerElement: HTMLDivElement;

  // Per-component audio engine instance
  $: audioEngine = AudioEngineManager.getInstance(elem_id || 'default');
  // Backend audio engine instance
  const backendAudioEngine = new BackendAudioEngine();

  // Dispatch data change event
  /**
   * Dispatch a 'dataChange' event with the current piano roll state.
   */
  function dispatchDataChange() {
    dispatch('dataChange', {
      notes,
      tempo,
      timeSignature,
      editMode,
      snapSetting,
      pixelsPerBeat,
      sampleRate,
      ppqn
    });
  }

  /**
   * Dispatch a 'noteChange' event with the current notes array.
   */
  function dispatchNoteChange() {
    dispatch('noteChange', {
      notes
    });
  }

  // Sync scroll handlers
  /**
   * Handle scroll events from the grid and update scroll positions.
   * @param event CustomEvent<{horizontalScroll: number, verticalScroll: number}>
   */
  function handleGridScroll(event: CustomEvent) {
    horizontalScroll = event.detail.horizontalScroll;
    verticalScroll = event.detail.verticalScroll;
    log.debug('scroll received, verticalScroll =', verticalScroll);
    // The scroll values are now reactively bound to the other components
    // and will trigger updates when they change
  }

  // Settings handlers
  /**
   * Handle time signature change events from the toolbar.
   * @param event CustomEvent<{numerator: number, denominator: number}>
   */
  function handleTimeSignatureChange(event: CustomEvent) {
    timeSignature = event.detail;
    dispatchDataChange();
  }

  /**
   * Handle edit mode change events from the toolbar.
   * @param event CustomEvent<string>
   */
  function handleEditModeChange(event: CustomEvent) {
    editMode = event.detail;
    dispatchDataChange();
  }

  /**
   * Handle snap setting change events from the toolbar.
   * @param event CustomEvent<string>
   */
  function handleSnapChange(event: CustomEvent) {
    snapSetting = event.detail;
    dispatchDataChange();
  }

  /**
   * Handle zoom in/out actions from the toolbar.
   * @param event CustomEvent<{action: 'zoom-in' | 'zoom-out'}>
   */
  function handleZoomChange(event: CustomEvent) {
    const { action } = event.detail;
    if (action === 'zoom-in') {
      zoomIn();
    } else if (action === 'zoom-out') {
      zoomOut();
    }
  }

  // Calculate total length in beats
  $: totalLengthInBeats = 32 * timeSignature.numerator; // 32 measures

  // Playback control functions
  /**
   * Render audio for the current notes and settings (frontend only).
   * Skips rendering if backend audio is enabled.
   */
  async function renderAudio() {
    // Skip rendering when using backend audio
    if (use_backend_audio) {
      console.log("🎵 Backend audio enabled - skipping frontend rendering");
      return;
    }

    // console.log("🎵 Frontend audio rendering started");
    isRendering = true;
    try {
      // Initialize component-specific audio engine
      audioEngine.initialize();

      // Render the notes to an audio buffer
      // Pass pixelsPerBeat to ensure proper alignment between waveform and notes
      await audioEngine.renderNotes(notes, tempo, totalLengthInBeats, pixelsPerBeat);

      // console.log("✅ Frontend audio rendering completed");
      // Waveform is now updated through layer system automatically
    } catch (error) {
      console.error('Error rendering audio:', error);
    } finally {
      isRendering = false;
    }
  }

  // Removed existing backendAudioContext, backendAudioBuffer, backendAudioSource, backendPlayStartTime, backendPlayheadInterval states

  // Removed existing initBackendAudio, decodeBackendAudio, startBackendAudioPlayback, pauseBackendAudio, stopBackendAudio, updateBackendPlayhead, downloadBackendAudio functions

  // Replacement functions
  async function handleBackendAudioInit() {
    if (audio_data) {
      await backendAudioEngine.initBackendAudio();
      await backendAudioEngine.decodeBackendAudio(audio_data);
    }
  }

  function handleBackendAudioPlay() {
    // Create reference objects for playhead updates
    const isPlayingRef = { value: isPlaying };
    const currentFlicksRef = { value: currentFlicks };
    
    backendAudioEngine.startBackendAudioPlayback(currentFlicks, () => {
      isPlaying = false;
      // Stop playhead updates
      if (backendAudioEngine.backendPlayheadInterval) {
        clearInterval(backendAudioEngine.backendPlayheadInterval);
        backendAudioEngine.backendPlayheadInterval = null;
      }
    });
    
    // Update playback state
    isPlaying = true;
    
    // Start playhead updates
    backendAudioEngine.updateBackendPlayhead(
      isPlayingRef,
      currentFlicksRef,
      () => {
        // Callback on playback completion
        isPlaying = false;
        currentFlicks = 0;
      }
    );
    
    // Additional interval for real-time playhead updates
    const playheadUpdateInterval = setInterval(() => {
      if (isPlaying && backendAudioEngine.backendAudioContext && backendAudioEngine.backendAudioBuffer) {
        const elapsedTime = backendAudioEngine.backendAudioContext.currentTime - backendAudioEngine.backendPlayStartTime;
        const newFlicks = Math.round(elapsedTime * 705600000);
        
        // Update currentFlicks in real-time
        currentFlicks = newFlicks;
        
        // Check if playback has ended
        if (elapsedTime >= backendAudioEngine.backendAudioBuffer.duration) {
          isPlaying = false;
          currentFlicks = 0;
          clearInterval(playheadUpdateInterval);
        }
      } else if (!isPlaying) {
        // Clean up interval when playback stops
        clearInterval(playheadUpdateInterval);
      }
    }, 16); // Update at 60fps
  }

  function handleBackendAudioPause() {
    // Pass current position as reference object
    const currentFlicksRef = { value: currentFlicks };
    backendAudioEngine.pauseBackendAudio(currentFlicksRef);
    
    // Reflect updated position
    currentFlicks = currentFlicksRef.value;
    isPlaying = false;
  }

  function handleBackendAudioStop() {
    // Pass current position as reference object
    const currentFlicksRef = { value: currentFlicks };
    backendAudioEngine.stopBackendAudio(currentFlicksRef);
    
    // Reset position to 0
    isPlaying = false;
    currentFlicks = 0;
  }

  async function handleBackendAudioDownload() {
    if (audio_data) {
      await backendAudioEngine.downloadBackendAudio(audio_data);
    }
  }

  // Dispatch data change event when zoom level changes
  $: if (pixelsPerBeat) {
    dispatchDataChange();
  }

  // Playback control functions
  /**
   * Play the piano roll audio (frontend or backend).
   * Handles switching between frontend and backend audio engines.
   */
  async function play() {
    if (isPlaying) {
      log.debug('Already playing, ignoring play request');
      return;
    }

    log.debug('Play function called');
    log.debug('- use_backend_audio:', use_backend_audio);
    log.debug('- audio_data present:', !!audio_data);
    log.debug('- elem_id:', elem_id);

    // Dispatch play event
    dispatch('play', {
      currentPosition: currentFlicks,
      notes,
      tempo,
      use_backend_audio
    });

    if (use_backend_audio && audio_data) {
      log.debug('Using backend audio for playback');
      // Play backend audio
      handleBackendAudioInit().then(() => {
        handleBackendAudioPlay();
      }).catch((error) => {
        log.error('Backend audio initialization failed:', error);
        fallbackToFrontendAudio();
      });
      return;
    }

    log.debug('Using frontend audio engine');
    if (!audioEngine.getRenderedBuffer()) {
      log.debug('No rendered buffer, rendering first...');
      // Render audio first if not already rendered
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      log.debug('Rendered buffer ready, starting playback');
      startPlayback();
    }
  }

  function fallbackToFrontendAudio() {
    log.debug('Falling back to frontend audio engine');
    use_backend_audio = false;
    if (!audioEngine.getRenderedBuffer()) {
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      startPlayback();
    }
  }

  function startPlayback() {
    if (use_backend_audio) {
      log.warn('startPlayback called but use_backend_audio is true - should not happen');
      return; // Skip when using backend audio
    }

    log.debug('Starting frontend audio playback');
    audioEngine.play();
    isPlaying = true;
  }

  /**
   * Pause the piano roll audio (frontend or backend).
   */
  function pause() {
    log.debug('Pause function called');
    log.debug('- use_backend_audio:', use_backend_audio);

    // Dispatch pause event
    dispatch('pause', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      handleBackendAudioPause();
      return;
    }

    log.debug('Pausing frontend audio');
    audioEngine.pause();
    isPlaying = false;
  }

  /**
   * Stop the piano roll audio (frontend or backend) and reset playhead.
   */
  function stop() {
    log.debug('Stop function called');
    log.debug('- use_backend_audio:', use_backend_audio);

    // Dispatch stop event
    dispatch('stop', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      handleBackendAudioStop();
      return;
    }

    log.debug('Stopping frontend audio');
    audioEngine.stop();
    isPlaying = false;
    currentFlicks = 0;
    // Also reset the audio engine's internal position
    audioEngine.seekToFlicks(0);
  }

  // Audio download function
  /**
   * Download the rendered audio (frontend or backend).
   */
  async function downloadAudio() {
    log.debug('Download audio function called');
    log.debug('- use_backend_audio:', use_backend_audio);
    log.debug('- audio_data present:', !!audio_data);

    if (use_backend_audio && audio_data) {
      // Download backend audio
      isRendering = true;
      try {
        await handleBackendAudioDownload();
      } finally {
        isRendering = false;
      }
    } else {
      // Download frontend audio
      await downloadFrontendAudio();
    }
  }

  /**
   * Download the rendered frontend audio as a WAV file.
   */
  async function downloadFrontendAudio() {
    log.debug('Downloading frontend audio...');

    try {
      // Render audio first if not already rendered
      if (!audioEngine.getRenderedBuffer()) {
        log.debug('No rendered buffer, rendering audio first...');
        isRendering = true;
        await renderAudio();
        isRendering = false;
      }

      // Check if rendered audio is available
      if (!audioEngine.getRenderedBuffer()) {
        log.error('Failed to render audio for download');
        return;
      }

      // Generate filename (with current timestamp)
      const now = new Date();
      const timestamp = now.toISOString().slice(0, 19).replace(/[T:]/g, '_');
      const filename = `piano_roll_${timestamp}.wav`;

      // Execute download
      audioEngine.downloadAudio(filename);

      log.info('Frontend audio download initiated:', filename);
    } catch (error) {
      log.error('Error downloading frontend audio:', error);
    } finally {
      isRendering = false;
    }
  }

  /**
   * Toggle playback between play and pause.
   */
  function togglePlayback() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  /**
   * Update the playhead position and auto-scroll if needed.
   * @param flicks Current playhead position in flicks
   */
  function updatePlayheadPosition(flicks: number) {
    currentFlicks = flicks;

    // Check if playhead is out of view and scroll to keep it visible
    const positionInBeats = flicksToBeats(flicks, tempo);
    const positionInPixels = positionInBeats * pixelsPerBeat;

    // Auto-scroll if playhead is near the edge of the view
    const bufferPixels = 100; // Buffer to start scrolling before edge
    if (positionInPixels > horizontalScroll + width - bufferPixels) {
      horizontalScroll = Math.max(0, positionInPixels - width / 2);
    } else if (positionInPixels < horizontalScroll + bufferPixels) {
      horizontalScroll = Math.max(0, positionInPixels - bufferPixels);
    }
  }

  /**
   * Handle note changes from the grid and trigger audio re-rendering.
   * @param event CustomEvent<{notes: Array<...>}>  // See PianoRollProps
   */
  function handleNoteChange(event: CustomEvent) {
    notes = event.detail.notes;
    // Re-render audio when notes change
    renderAudio();
    // Dispatch note change event
    dispatchNoteChange();
  }

  /**
   * Handle tempo changes from the toolbar and trigger audio re-rendering.
   * @param event CustomEvent<number>
   */
  function handleTempoChange(event: CustomEvent) {
    tempo = event.detail;
    // Re-render audio when tempo changes
    renderAudio();
    // Dispatch data change event
    dispatchDataChange();
  }

  /**
   * Handle position changes from the timeline (seek playhead).
   * @param event CustomEvent<{flicks: number}>
   */
  function handlePositionChange(event: CustomEvent) {
    const { flicks } = event.detail;
    currentFlicks = flicks;

    // Seek audio engine to new position
    audioEngine.seekToFlicks(flicks);
  }

  /**
   * Handle lyric input events from the grid and dispatch upward.
   * @param event CustomEvent<any>
   */
  function handleLyricInput(event: CustomEvent) {
    dispatch('lyricInput', event.detail);
  }

  onMount(() => {
    // Set up playhead position update callback
    audioEngine.setPlayheadUpdateCallback(updatePlayheadPosition);

    // Initial audio render - always render when not using backend audio
    if (!use_backend_audio) {
      console.log("🎵 Initial frontend audio rendering on mount");
      renderAudio();
    }
  });

  onDestroy(() => {
    // Clean up backend audio
    // backendAudioEngine.dispose(); // Clean up backend audio engine

    // Clean up component-specific audio engine resources
    if (elem_id) {
      AudioEngineManager.disposeInstance(elem_id);
    } else {
      audioEngine.dispose();
    }
  });

  // Reactive statement to decode backend audio when audio_data changes
  $: if (audio_data && use_backend_audio) {
    console.log("🔄 Audio data or backend flag changed, initializing...");
    console.log("- audio_data present:", !!audio_data);
    console.log("- use_backend_audio:", use_backend_audio);

    handleBackendAudioInit().catch((error) => {
      console.error("❌ Failed to initialize backend audio:", error);
    });
  }

  // Reactive statement to start frontend rendering when switching from backend to frontend
  $: if (!use_backend_audio && audioEngine) {
    console.log("🔄 Switched to frontend audio - starting automatic rendering");
    renderAudio();
  }
</script>

<div
  class="piano-roll-container"
  bind:this={containerElement}
  style="width: {width}px; height: {height}px;"
>
  <Toolbar
    {tempo}
    {timeSignature}
    {editMode}
    {snapSetting}
    {isPlaying}
    {isRendering}
    on:tempoChange={handleTempoChange}
    on:timeSignatureChange={handleTimeSignatureChange}
    on:editModeChange={handleEditModeChange}
    on:snapChange={handleSnapChange}
    on:zoomChange={handleZoomChange}
    on:play={play}
    on:pause={pause}
    on:stop={stop}
    on:togglePlay={togglePlayback}
    on:downloadAudio={downloadAudio}
  />

  <div class="piano-roll-main" style="height: {height - 40}px;">
    <!-- Timeline positioned at the top -->
    <div class="timeline-container" style="margin-left: {keyboardWidth}px;">
      <TimeLineComponent
        width={width - keyboardWidth}
        {timelineHeight}
        {timeSignature}
        {snapSetting}
        {horizontalScroll}
        {pixelsPerBeat}
        {tempo}
        on:zoomChange={handleZoomChange}
        on:positionChange={handlePositionChange}
      />
    </div>

    <!-- Main content area with keyboard and grid aligned -->
    <div class="content-container">
      <KeyboardComponent
        {keyboardWidth}
        height={height - 40 - timelineHeight}
        {verticalScroll}
      />

      <div class="grid-container" style="position: relative;">
        <!-- Waveform is now handled by the layer system in GridComponent -->
        <!-- <WaveformComponent> has been integrated into WaveformLayer -->

        <!-- Grid component containing notes and grid lines -->
        <GridComponent
          width={width - keyboardWidth}
          height={height - 40 - timelineHeight}
          {notes}
          {tempo}
          {timeSignature}
          {editMode}
          {snapSetting}
          {horizontalScroll}
          {verticalScroll}
          {pixelsPerBeat}
          {currentFlicks}
          {isPlaying}
          {sampleRate}
          {ppqn}
          {elem_id}
          {audio_data}
          {curve_data}
          {line_data}
          {use_backend_audio}
          on:scroll={handleGridScroll}
          on:noteChange={handleNoteChange}
          on:lyricInput={handleLyricInput}
        />

        <!-- Playhead position indicator -->
        <PlayheadComponent
          width={width - keyboardWidth}
          height={height - 40 - timelineHeight}
          {horizontalScroll}
          {pixelsPerBeat}
          {tempo}
          {currentFlicks}
          {isPlaying}
        />
      </div>
    </div>
  </div>
</div>

<!-- Debug component for Flicks timing information -->
<DebugComponent
  {currentFlicks}
  {tempo}
  {notes}
  {isPlaying}
  {isRendering}
/>

<style>
  .piano-roll-container {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: #2c2c2c;
    border-radius: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }

  .piano-roll-main {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .timeline-container {
    display: flex;
    height: var(--timeline-height, 40px);
  }

  .content-container {
    display: flex;
    flex-direction: row;
    flex: 1;
  }
</style>
