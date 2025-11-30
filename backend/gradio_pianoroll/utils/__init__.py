"""
Utility Module for Researchers

This package provides various helper functions and templates
to help researchers use the piano roll component more easily.

All utilities can be imported optionally and operate
independently from the main component.

Usage example:
    from gradio_pianoroll import PianoRoll
    from gradio_pianoroll.utils import research

    # Use researcher convenience functions
    data = research.from_notes([(60, 0, 1), (64, 1, 1)])
    piano_roll = PianoRoll(value=data)
"""

# Provide lazy imports for each module
__all__ = []


def __getattr__(name: str):
    """Lazy import for utility modules"""
    if name == "research":
        from . import research

        return research
    elif name == "templates":
        from . import templates

        return templates
    elif name == "converters":
        from . import converters

        return converters
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
