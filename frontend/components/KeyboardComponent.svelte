<!--
  KeyboardComponent.svelte
  Renders a vertical piano keyboard using canvas, allows users to preview notes by clicking keys.
  - Props:
    - keyboardWidth: number (width of the keyboard in px)
    - height: number (height of the keyboard in px)
    - verticalScroll: number (vertical scroll offset)
  - Emits:
    - (none by default, but can be extended)
  - Usage:
    <KeyboardComponent keyboardWidth={120} height={560} verticalScroll={0} />
-->

<!--
  KeyboardComponent that renders piano keys using canvas and allows users to preview sounds.
-->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import {
    NOTES,
    TOTAL_KEYS,
    calculateKeyPositions,
    WHITE_KEY_HEIGHT,
    BLACK_KEY_HEIGHT,
    getBlackKeyWidth
  } from '../utils/keyboardUtils';
  import { KeyboardAudioEngine } from '../utils/keyboardAudioEngine';

  // Props
  export let keyboardWidth = 120;
  export let height = 560;
  export let verticalScroll = 0;

  // Constants
  const BLACK_KEY_WIDTH = getBlackKeyWidth(keyboardWidth);

  // Key positions (computed)
  let keyPositions = calculateKeyPositions(keyboardWidth);

  // Audio engine instance
  const audioEngine = new KeyboardAudioEngine();

  // DOM References
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;

  const dispatch = createEventDispatcher();

  // Play a preview note
  function playNote(midiNote: number) {
    audioEngine.playNote(midiNote);
  }

  // Draw the piano keyboard
  function drawKeyboard() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const startIndex = Math.floor(verticalScroll / WHITE_KEY_HEIGHT);
    const visibleKeysCount = Math.ceil(height / WHITE_KEY_HEIGHT) + 1;
    for (let i = startIndex; i < Math.min(startIndex + visibleKeysCount, keyPositions.length); i++) {
      const key = keyPositions[i];
      if (!key.isBlack) {
        const y = key.y - verticalScroll;
        drawWhiteKey(key.note, key.octave, y);
      }
    }
    for (let i = startIndex; i < Math.min(startIndex + visibleKeysCount, keyPositions.length); i++) {
      const key = keyPositions[i];
      if (key.isBlack) {
        const y = key.y - verticalScroll;
        drawBlackKey(key.note, key.octave, y);
      }
    }
  }

  function drawWhiteKey(note: string, octave: number, y: number) {
    if (!ctx) return;
    ctx.fillStyle = '#ffffff';
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    ctx.fillRect(0, y, keyboardWidth, WHITE_KEY_HEIGHT);
    ctx.strokeRect(0, y, keyboardWidth, WHITE_KEY_HEIGHT);
    ctx.fillStyle = '#333333';
    ctx.font = '10px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${note}${octave}`, keyboardWidth - 6, y + WHITE_KEY_HEIGHT / 2);
  }

  function drawBlackKey(note: string, octave: number, y: number) {
    if (!ctx) return;
    ctx.fillStyle = '#333333';
    ctx.fillRect(0, y, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT);
    ctx.fillStyle = '#ffffff';
    ctx.font = '8px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${note}${octave}`, BLACK_KEY_WIDTH - 6, y + BLACK_KEY_HEIGHT / 2);
  }

  function handleMouseDown(event: MouseEvent) {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top + verticalScroll;
    for (let i = 0; i < keyPositions.length; i++) {
      const key = keyPositions[i];
      const keyHeight = key.isBlack ? BLACK_KEY_HEIGHT : WHITE_KEY_HEIGHT;
      const keyWidth = key.isBlack ? BLACK_KEY_WIDTH : keyboardWidth;
      if (y >= key.y && y < key.y + keyHeight && x <= keyWidth) {
        const midiNote = TOTAL_KEYS - 1 - i;
        playNote(midiNote);
        break;
      }
    }
  }

  onMount(() => {
    ctx = canvas.getContext('2d');
    canvas.width = keyboardWidth;
    canvas.height = height;
    keyPositions = calculateKeyPositions(keyboardWidth);
    drawKeyboard();
    audioEngine.init();
  });

  onDestroy(() => {
    audioEngine.dispose();
  });

  $: {
    if (ctx && canvas) {
      drawKeyboard();
    }
  }
  $: if (verticalScroll !== undefined && ctx && canvas) {
    drawKeyboard();
  }
</script>

<canvas
  bind:this={canvas}
  width={keyboardWidth}
  height={height}
  on:mousedown={handleMouseDown}
  class="keyboard-canvas"
></canvas>

<style>
  .keyboard-canvas {
    display: block;
    background-color: #f8f8f8;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  }
</style>
