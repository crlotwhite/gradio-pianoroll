"""
Backend data management for PianoRoll component.

This module provides a clean interface for managing audio, curve, and segment data
separately from the main component value structure.
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class PianoRollBackendData:
    """
    Manages backend data for PianoRoll component in a clean, structured way.
    
    Attributes:
        audio_data: Base64 encoded audio or URL
        curve_data: Dictionary containing curve data (pitch, loudness, etc.)
        segment_data: List of segmentation data (phonemes, timing, etc.)
        use_backend_audio: Whether to use backend audio engine
    """
    audio_data: Optional[str] = None
    curve_data: Dict[str, Any] = field(default_factory=dict)
    segment_data: List[Dict[str, Any]] = field(default_factory=list)
    use_backend_audio: bool = False
    
    def set_audio(self, audio_data: str) -> None:
        """Set backend audio data."""
        self.audio_data = audio_data
    
    def add_curve(self, name: str, curve_data: Dict[str, Any]) -> None:
        """Add or update a curve dataset."""
        self.curve_data[name] = curve_data
    
    def remove_curve(self, name: str) -> None:
        """Remove a curve dataset."""
        self.curve_data.pop(name, None)
    
    def add_segment(self, segment: Dict[str, Any]) -> None:
        """Add a segment data entry."""
        self.segment_data.append(segment)
    
    def clear_segments(self) -> None:
        """Clear all segment data."""
        self.segment_data.clear()
    
    def enable_backend_audio(self, enable: bool = True) -> None:
        """Enable or disable backend audio engine."""
        self.use_backend_audio = enable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "audio_data": self.audio_data,
            "curve_data": self.curve_data,
            "segment_data": self.segment_data,
            "use_backend_audio": self.use_backend_audio
        }
    
    def has_data(self) -> bool:
        """Check if any backend data is present."""
        return (
            self.audio_data is not None or
            bool(self.curve_data) or
            bool(self.segment_data)
        ) 