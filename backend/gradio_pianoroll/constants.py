"""
Backend constants for the piano roll component.
Centralizes magic numbers to improve maintainability and ensure consistency
between frontend and backend.
"""

# =============================================================================
# Zoom Configuration
# =============================================================================

#: Default pixels per beat (controls initial zoom level)
DEFAULT_PIXELS_PER_BEAT: int = 80

#: Minimum zoom level in pixels per beat
MIN_PIXELS_PER_BEAT: int = 40

#: Maximum zoom level in pixels per beat
MAX_PIXELS_PER_BEAT: int = 200

#: Zoom step size (must be integer to avoid coordinate calculation errors)
ZOOM_STEP: int = 20

# =============================================================================
# Default Audio Settings
# =============================================================================

#: Default tempo in BPM
DEFAULT_TEMPO: int = 120

#: Default audio sample rate in Hz
DEFAULT_SAMPLE_RATE: int = 44100

#: Default MIDI pulses per quarter note (ticks per beat)
DEFAULT_PPQN: int = 480

# =============================================================================
# UI Configuration
# =============================================================================

#: Default keyboard width in pixels
DEFAULT_KEYBOARD_WIDTH: int = 120

#: Default timeline height in pixels
DEFAULT_TIMELINE_HEIGHT: int = 40

#: Default piano roll width in pixels
DEFAULT_PIANOROLL_WIDTH: int = 1000

#: Default piano roll height in pixels
DEFAULT_PIANOROLL_HEIGHT: int = 600

#: Minimum component width in pixels
MIN_COMPONENT_WIDTH: int = 160

# =============================================================================
# Grid and Note Dimensions
# =============================================================================

#: Height of a single note row in pixels (matches white key height)
NOTE_HEIGHT: int = 20

#: Total number of MIDI notes (0-127)
TOTAL_NOTES: int = 128

# =============================================================================
# Default Values
# =============================================================================

#: Default note velocity (0-127)
DEFAULT_VELOCITY: int = 100

#: Default lyric for new notes
DEFAULT_LYRIC: str = "라"

#: Default snap setting
DEFAULT_SNAP_SETTING: str = "1/4"

#: Default edit mode
DEFAULT_EDIT_MODE: str = "select"

# =============================================================================
# Flicks Timing
# =============================================================================

#: Flicks per second (standard Flicks timing unit)
FLICKS_PER_SECOND: int = 705_600_000
