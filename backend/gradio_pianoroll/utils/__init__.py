"""
Utility Module for Researchers

This package provides various helper functions and templates
to help researchers use the piano roll component more easily.

All utilities can be imported optionally and operate
independently from the main component.

Module Structure:
    - converters: Data conversion functions (from_notes, from_midi_numbers, etc.)
    - analysis: Analysis tools (analyze_notes, auto_analyze)
    - ui_builders: UI/demo creation (create_pianoroll_with_data, quick_demo)
    - templates: Template generators
    - research: Backward compatibility module (re-exports all functions)

Usage example:
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    # Use researcher convenience functions
    data = research.from_notes([(60, 0, 1), (64, 1, 1)])
    piano_roll = PianoRoll(value=data)

    # Or use specific modules (recommended for new code):
    from gradio_pianoroll.utils import converters
    data = converters.from_notes([(60, 0, 1), (64, 1, 1)])
"""

import sys
from importlib import import_module

# Module names available for lazy loading
__all__ = [
    "research",
    "templates",
    "converters",
    "analysis",
    "ui_builders",
]

# Cache for loaded modules
_loaded_modules = {}


def __getattr__(name: str):
    """Lazy import for utility modules."""
    if name in __all__:
        if name not in _loaded_modules:
            # Use importlib to avoid circular import issues
            module = import_module(f".{name}", __name__)
            _loaded_modules[name] = module
        return _loaded_modules[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
