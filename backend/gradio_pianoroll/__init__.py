from .pianoroll import PianoRoll

# Core component is always available
__all__ = ["PianoRoll"]

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
