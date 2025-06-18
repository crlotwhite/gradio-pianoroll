from __future__ import annotations

import logging
import os

from .pianoroll import PianoRoll
from .data_models import (
    TimeSignatureData,
    NoteData,
    LineDataPointData,
    LineLayerConfigData,
    PianoRollDataClass as PianoRollData,
)

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

level_str = os.environ.get("GRADIO_PIANOROLL_LOG_LEVEL", "WARNING").upper()
logger.setLevel(getattr(logging, level_str, logging.WARNING))

# Core component is always available
__all__ = [
    "PianoRoll",
    "TimeSignatureData",
    "NoteData",
    "LineDataPointData",
    "LineLayerConfigData",
    "PianoRollData",
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
