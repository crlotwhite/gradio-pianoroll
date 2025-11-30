<!--
  LyricEditor Component for editing note lyrics inline.
  
  This component displays an input field positioned over a note
  for editing lyrics with keyboard navigation (Enter to save, Escape to cancel).
-->
<script lang="ts">
  import { createEventDispatcher, onMount, tick } from 'svelte';

  // ============================================================================
  // Props
  // ============================================================================

  /** Whether the editor is currently visible/active */
  export let isEditing: boolean = false;

  /** ID of the note being edited */
  export let noteId: string | null = null;

  /** Current lyric value being edited */
  export let value: string = '';

  /** X position in pixels (relative to container) */
  export let x: number = 0;

  /** Y position in pixels (relative to container) */
  export let y: number = 0;

  /** Width of the input field in pixels */
  export let width: number = 40;

  // ============================================================================
  // Internal State
  // ============================================================================

  let inputElement: HTMLInputElement;
  let internalValue: string = '';

  // Sync internal value with prop
  $: internalValue = value;

  // ============================================================================
  // Events
  // ============================================================================

  const dispatch = createEventDispatcher<{
    /** Emitted when lyric is saved (Enter pressed or blur) */
    save: { noteId: string; oldValue: string; newValue: string };
    /** Emitted when editing is cancelled (Escape pressed) */
    cancel: { noteId: string };
  }>();

  // ============================================================================
  // Lifecycle
  // ============================================================================

  // Focus input when editing starts
  $: if (isEditing && inputElement) {
    tick().then(() => {
      inputElement?.focus();
      inputElement?.select();
    });
  }

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle keydown events in the input field.
   * Enter saves the lyric, Escape cancels editing.
   */
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      save();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      cancel();
    }
  }

  /**
   * Handle blur event (clicking outside the input).
   * Saves the lyric automatically.
   */
  function handleBlur() {
    if (isEditing) {
      save();
    }
  }

  /**
   * Save the edited lyric and emit save event.
   */
  function save() {
    if (!noteId) return;

    dispatch('save', {
      noteId,
      oldValue: value,
      newValue: internalValue,
    });
  }

  /**
   * Cancel editing and emit cancel event.
   */
  function cancel() {
    if (!noteId) return;

    // Reset internal value to original
    internalValue = value;

    dispatch('cancel', {
      noteId,
    });
  }
</script>

{#if isEditing}
  <div
    class="lyric-editor-container"
    style="
      left: {x}px;
      top: {y}px;
      width: {width}px;
    "
  >
    <input
      bind:this={inputElement}
      type="text"
      bind:value={internalValue}
      on:keydown={handleKeydown}
      on:blur={handleBlur}
      class="lyric-input"
      aria-label="Edit note lyrics"
      placeholder="♪"
    />
  </div>
{/if}

<style>
  .lyric-editor-container {
    position: absolute;
    z-index: 20;
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

  .lyric-input::placeholder {
    color: #aaa;
    font-style: italic;
  }
</style>
