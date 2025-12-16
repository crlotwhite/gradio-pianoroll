"""
Helper function library for researchers.

This module enables researchers to easily use the piano roll component
by processing complex tasks through simple function calls.

.. deprecated::
    This module is kept for backward compatibility.
    For new code, use the specific submodules:
    - ``gradio_pianoroll.utils.converters`` for data conversion functions
    - ``gradio_pianoroll.utils.analysis`` for analysis tools
    - ``gradio_pianoroll.utils.ui_builders`` for UI/demo creation
"""

from __future__ import annotations

# Re-export all public functions for backward compatibility
# =============================================================================
# Converters (data creation/conversion)
# =============================================================================
from .converters import (
    from_frequencies,
    from_midi_generation,
    from_midi_numbers,
    from_notes,
    from_tts_output,
)

# =============================================================================
# Analysis tools
# =============================================================================
from .analysis import analyze_notes, auto_analyze

# =============================================================================
# UI builders
# =============================================================================
from .ui_builders import create_pianoroll_with_data, quick_demo

# =============================================================================
# Internal (re-exported for compatibility, but marked as private)
# =============================================================================
from ._internal import _create_f0_line_data

__all__ = [
    # Converters
    "from_notes",
    "from_midi_numbers",
    "from_frequencies",
    "from_tts_output",
    "from_midi_generation",
    # Analysis
    "analyze_notes",
    "auto_analyze",
    # UI builders
    "create_pianoroll_with_data",
    "quick_demo",
    # Internal (for backward compatibility)
    "_create_f0_line_data",
]
