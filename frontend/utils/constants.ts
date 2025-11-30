/**
 * Frontend constants for the piano roll component.
 * Centralizes magic numbers to improve maintainability.
 */

// =============================================================================
// Grid and Note Dimensions
// =============================================================================

/** Height of a single note row in pixels (matches white key height) */
export const NOTE_HEIGHT = 20;

/** Total number of MIDI notes (0-127) */
export const TOTAL_NOTES = 128;

/** Total height of the piano roll grid in pixels */
export const GRID_TOTAL_HEIGHT = NOTE_HEIGHT * TOTAL_NOTES;

// =============================================================================
// Zoom Configuration
// =============================================================================

/** Default pixels per beat (controls initial zoom level) */
export const DEFAULT_PIXELS_PER_BEAT = 80;

/** Minimum zoom level in pixels per beat */
export const MIN_PIXELS_PER_BEAT = 40;

/** Maximum zoom level in pixels per beat */
export const MAX_PIXELS_PER_BEAT = 200;

/** Zoom step size (must be integer to avoid coordinate calculation errors) */
export const ZOOM_STEP = 20;

// =============================================================================
// Default Audio Settings
// =============================================================================

/** Default tempo in BPM */
export const DEFAULT_TEMPO = 120;

/** Default audio sample rate in Hz */
export const DEFAULT_SAMPLE_RATE = 44100;

/** Default MIDI pulses per quarter note (ticks per beat) */
export const DEFAULT_PPQN = 480;

// =============================================================================
// UI Configuration
// =============================================================================

/** Default keyboard width in pixels */
export const DEFAULT_KEYBOARD_WIDTH = 120;

/** Default timeline height in pixels */
export const DEFAULT_TIMELINE_HEIGHT = 40;

/** Default piano roll width in pixels */
export const DEFAULT_PIANOROLL_WIDTH = 1000;

/** Default piano roll height in pixels */
export const DEFAULT_PIANOROLL_HEIGHT = 600;

// =============================================================================
// Interaction Thresholds
// =============================================================================

/** Minimum edge detection threshold for note resize (pixels) */
export const MIN_EDGE_DETECTION_THRESHOLD = 5;

/** Maximum edge detection threshold for note resize (pixels) */
export const MAX_EDGE_DETECTION_THRESHOLD = 15;

/** Fine control grid division when snap is off */
export const FINE_CONTROL_DIVISION = 32;

// =============================================================================
// Default Values
// =============================================================================

/** Default note velocity (0-127) */
export const DEFAULT_VELOCITY = 100;

/** Default lyric for new notes (Korean syllable 'ra') */
export const DEFAULT_LYRIC = '라';

/** Default snap setting */
export const DEFAULT_SNAP_SETTING = '1/4';

/** Default edit mode */
export const DEFAULT_EDIT_MODE = 'select';
