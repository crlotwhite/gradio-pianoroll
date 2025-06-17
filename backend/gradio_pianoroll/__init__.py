from .pianoroll import PianoRoll
from .data_models import (
    TimeSignatureData,
    NoteData,
    LineDataPointData,
    LineLayerConfigData,
    PianoRollDataClass,
)

# Core component is always available
__all__ = [
    "PianoRoll",
    "TimeSignatureData",
    "NoteData",
    "LineDataPointData",
    "LineLayerConfigData",
    "PianoRollDataClass",
]

# Optional utilities - users can import explicitly if needed
# Example usage:
# from gradio_pianoroll import PianoRoll  # Basic component
# from gradio_pianoroll import utils      # Research utilities (optional)

# Provide easy access to utils if needed
try:
    from . import utils

    __all__.append("utils")
except ImportError:
    # utils might not be available in minimal installations
    pass
