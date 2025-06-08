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
  /**
   * @typedef {import('../../types/component').PianoRollProps} PianoRollProps
   */

  // 이벤트 디스패처 생성
  const dispatch = createEventDispatcher();

  // Props (외부에서 주입되는 값)
  /** @type {number} */
  export let width = 1000;  // Total width of the piano roll
  /** @type {number} */
  export let height = 600;  // Total height of the piano roll
  /** @type {number} */
  export let keyboardWidth = 120; // Width of the keyboard component
  /** @type {number} */
  export let timelineHeight = 40; // Height of the timeline component
  /** @type {string} */
  export let elem_id = '';  // 컴포넌트 고유 ID

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
  export let tempo = 120;
  /** @type {{ numerator: number, denominator: number }} */
  export let timeSignature = { numerator: 4, denominator: 4 };
  /** @type {string} */
  export let editMode = 'select'; // 'select', 'draw', 'erase', etc.
  /** @type {string} */
  export let snapSetting = '1/4'; // Default snap setting: 1/4

  // Audio metadata
  /** @type {number} */
  export let sampleRate = 44100; // Audio sample rate
  /** @type {number} */
  export let ppqn = 480;         // MIDI pulses per quarter note

  // Zoom level (pixels per beat) - now controlled from parent
  /** @type {number} */
  export let pixelsPerBeat = 80;
  const MIN_PIXELS_PER_BEAT = 40; // Minimum zoom level
  const MAX_PIXELS_PER_BEAT = 200; // Maximum zoom level
  const ZOOM_STEP = 20; // Zoom step size (must be integer to avoid coordinate calculation errors)

  // Zoom in function
  function zoomIn() {
    if (pixelsPerBeat < MAX_PIXELS_PER_BEAT) {
      pixelsPerBeat += ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // Zoom out function
  function zoomOut() {
    if (pixelsPerBeat > MIN_PIXELS_PER_BEAT) {
      pixelsPerBeat -= ZOOM_STEP;
      dispatchDataChange();
    }
  }

  // State variables (내부 상태)
  // Playback state
  let isPlaying = false;
  let isRendering = false;
  let currentFlicks = 0;

  // Scroll positions
  let horizontalScroll = 0;
  let verticalScroll = 0;

  // References to DOM elements
  let containerElement: HTMLDivElement;

  // 컴포넌트별 오디오 엔진 인스턴스
  $: audioEngine = AudioEngineManager.getInstance(elem_id || 'default');
  // Backend audio engine 인스턴스
  const backendAudioEngine = new BackendAudioEngine();

  // 전체 데이터 변경 이벤트 발생
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

  // 노트만 변경 이벤트 발생
  function dispatchNoteChange() {
    dispatch('noteChange', {
      notes
    });
  }

  // Sync scroll handlers
  function handleGridScroll(event: CustomEvent) {
    horizontalScroll = event.detail.horizontalScroll;
    verticalScroll = event.detail.verticalScroll;
    console.log('🎨 PianoRoll: scroll received, verticalScroll =', verticalScroll);
    // The scroll values are now reactively bound to the other components
    // and will trigger updates when they change
  }

  // Settings handlers
  function handleTimeSignatureChange(event: CustomEvent) {
    timeSignature = event.detail;
    dispatchDataChange();
  }

  function handleEditModeChange(event: CustomEvent) {
    editMode = event.detail;
    dispatchDataChange();
  }

  function handleSnapChange(event: CustomEvent) {
    snapSetting = event.detail;
    dispatchDataChange();
  }

  // Handle zoom changes from toolbar
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
  async function renderAudio() {
    // 백엔드 오디오를 사용하는 경우 렌더링하지 않음
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

  // 기존 backendAudioContext, backendAudioBuffer, backendAudioSource, backendPlayStartTime, backendPlayheadInterval 등 상태 제거

  // 기존 initBackendAudio, decodeBackendAudio, startBackendAudioPlayback, pauseBackendAudio, stopBackendAudio, updateBackendPlayhead, downloadBackendAudio 함수 제거

  // 기존 함수 대체
  async function handleBackendAudioInit() {
    if (audio_data) {
      await backendAudioEngine.initBackendAudio();
      await backendAudioEngine.decodeBackendAudio(audio_data);
    }
  }

  function handleBackendAudioPlay() {
    backendAudioEngine.startBackendAudioPlayback(currentFlicks, () => {
      isPlaying = false;
    });
  }

  function handleBackendAudioPause() {
    backendAudioEngine.pauseBackendAudio({ value: currentFlicks });
    isPlaying = false;
  }

  function handleBackendAudioStop() {
    backendAudioEngine.stopBackendAudio({ value: currentFlicks });
    isPlaying = false;
    currentFlicks = 0;
  }

  async function handleBackendAudioDownload() {
    if (audio_data) {
      await backendAudioEngine.downloadBackendAudio(audio_data);
    }
  }

  // Zoom level 변경 시 전체 데이터 변경 이벤트 발생
  $: if (pixelsPerBeat) {
    dispatchDataChange();
  }

  // Playback control functions
  async function play() {
    if (isPlaying) {
      console.log("⚠️ Already playing, ignoring play request");
      return;
    }

    console.log("▶️ Play function called");
    console.log("- use_backend_audio:", use_backend_audio);
    console.log("- audio_data present:", !!audio_data);
    console.log("- elem_id:", elem_id);

    // 재생 이벤트 발생
    dispatch('play', {
      currentPosition: currentFlicks,
      notes,
      tempo,
      use_backend_audio
    });

    if (use_backend_audio && audio_data) {
      console.log("🎵 Using backend audio for playback");
      // 백엔드 오디오 재생
      handleBackendAudioInit().then(() => {
        handleBackendAudioPlay();
      }).catch((error) => {
        console.error("❌ Backend audio initialization failed:", error);
        fallbackToFrontendAudio();
      });
      return;
    }

    console.log("🎵 Using frontend audio engine");
    if (!audioEngine.getRenderedBuffer()) {
      console.log("🔄 No rendered buffer, rendering first...");
      // Render audio first if not already rendered
      renderAudio().then(() => {
        startPlayback();
      });
    } else {
      console.log("✅ Rendered buffer ready, starting playback");
      startPlayback();
    }
  }

  function fallbackToFrontendAudio() {
    console.log("🔄 Falling back to frontend audio engine");
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
      console.log("⚠️ startPlayback called but use_backend_audio is true - should not happen");
      return; // 백엔드 오디오 사용 시 건너뛰기
    }

    console.log("▶️ Starting frontend audio playback");
    audioEngine.play();
    isPlaying = true;
  }

  function pause() {
    console.log("⏸️ Pause function called");
    console.log("- use_backend_audio:", use_backend_audio);

    // 일시정지 이벤트 발생
    dispatch('pause', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      handleBackendAudioPause();
      return;
    }

    console.log("⏸️ Pausing frontend audio");
    audioEngine.pause();
    isPlaying = false;
  }

  function stop() {
    console.log("⏹️ Stop function called");
    console.log("- use_backend_audio:", use_backend_audio);

    // 정지 이벤트 발생
    dispatch('stop', {
      currentPosition: currentFlicks,
      use_backend_audio
    });

    if (use_backend_audio) {
      handleBackendAudioStop();
      return;
    }

    console.log("⏹️ Stopping frontend audio");
    audioEngine.stop();
    isPlaying = false;
    currentFlicks = 0;
    // Also reset the audio engine's internal position
    audioEngine.seekToFlicks(0);
  }

  // 오디오 다운로드 함수
  async function downloadAudio() {
    console.log("💾 Download audio function called");
    console.log("- use_backend_audio:", use_backend_audio);
    console.log("- audio_data present:", !!audio_data);

    if (use_backend_audio && audio_data) {
      // 백엔드 오디오 다운로드
      isRendering = true;
      try {
        await handleBackendAudioDownload();
      } finally {
        isRendering = false;
      }
    } else {
      // 프론트엔드 오디오 다운로드
      await downloadFrontendAudio();
    }
  }

  // 프론트엔드 오디오 다운로드 (렌더링 후 WAV로 변환)
  async function downloadFrontendAudio() {
    console.log("💾 Downloading frontend audio...");

    try {
      // 오디오가 렌더링되지 않았다면 먼저 렌더링
      if (!audioEngine.getRenderedBuffer()) {
        console.log("🔄 No rendered buffer, rendering audio first...");
        isRendering = true;
        await renderAudio();
        isRendering = false;
      }

      // 렌더링된 오디오가 있는지 확인
      if (!audioEngine.getRenderedBuffer()) {
        console.error("❌ Failed to render audio for download");
        return;
      }

      // 파일명 생성 (현재 시간 포함)
      const now = new Date();
      const timestamp = now.toISOString().slice(0, 19).replace(/[T:]/g, '_');
      const filename = `piano_roll_${timestamp}.wav`;

      // 다운로드 실행
      audioEngine.downloadAudio(filename);

      console.log("✅ Frontend audio download initiated:", filename);
    } catch (error) {
      console.error("❌ Error downloading frontend audio:", error);
    } finally {
      isRendering = false;
    }
  }

  function togglePlayback() {
    if (isPlaying) {
      pause();
    } else {
      play();
    }
  }

  // Handle position updates from audio engine
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

  // Handle note changes to re-render audio
  function handleNoteChange(event: CustomEvent) {
    notes = event.detail.notes;
    // Re-render audio when notes change
    renderAudio();
    // 노트 변경 이벤트 발생
    dispatchNoteChange();
  }

  // Handle tempo changes
  function handleTempoChange(event: CustomEvent) {
    tempo = event.detail;
    // Re-render audio when tempo changes
    renderAudio();
    // 전체 데이터 변경 이벤트 발생
    dispatchDataChange();
  }

  // Handle position change from timeline click
  function handlePositionChange(event: CustomEvent) {
    const { flicks } = event.detail;
    currentFlicks = flicks;

    // Seek audio engine to new position
    audioEngine.seekToFlicks(flicks);
  }

  // 가사 입력 이벤트 발생 (GridComponent에서 전달받은 것을 상위로 전달)
  function handleLyricInput(event: CustomEvent) {
    dispatch('lyricInput', event.detail);
  }

  onMount(() => {
    // Set up playhead position update callback
    audioEngine.setPlayheadUpdateCallback(updatePlayheadPosition);

    // Initial audio render - 백엔드 오디오를 사용하지 않는 경우 항상 렌더링
    if (!use_backend_audio) {
      console.log("🎵 Initial frontend audio rendering on mount");
      renderAudio();
    }
  });

  onDestroy(() => {
    // Clean up backend audio
    // backendAudioEngine.dispose(); // 백엔드 오디오 엔진 정리

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
