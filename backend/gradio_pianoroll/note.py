"""
Note data structure with integrated timing calculations.

This module provides a clean Note class that encapsulates all timing calculations
and provides a more intuitive interface for working with piano roll notes.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .timing_utils import (
    generate_note_id,
    pixels_to_flicks,
    pixels_to_seconds,
    pixels_to_beats,
    pixels_to_ticks,
    pixels_to_samples
)


@dataclass
class Note:
    """
    Represents a single note in the piano roll with automatic timing calculations.
    
    All timing values are automatically calculated from pixel values based on
    the provided musical context (tempo, pixels_per_beat, etc.).
    """
    # Core note properties
    pitch: int  # MIDI pitch (0-127)
    velocity: int = 100  # MIDI velocity (0-127)
    lyric: str = ""  # Optional lyric text
    
    # Position and duration in pixels (primary coordinates)
    start_pixels: float = 0.0
    duration_pixels: float = 80.0
    
    # Musical context for timing calculations
    pixels_per_beat: float = 80.0
    tempo: float = 120.0
    sample_rate: int = 44100
    ppqn: int = 480
    
    # Unique identifier
    id: Optional[str] = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if self.id is None:
            self.id = generate_note_id()
    
    # Properties for automatic timing calculations
    @property
    def start_flicks(self) -> float:
        """Start position in flicks (precise timing unit)."""
        return pixels_to_flicks(self.start_pixels, self.pixels_per_beat, self.tempo)
    
    @property
    def duration_flicks(self) -> float:
        """Duration in flicks (precise timing unit)."""
        return pixels_to_flicks(self.duration_pixels, self.pixels_per_beat, self.tempo)
    
    @property
    def start_seconds(self) -> float:
        """Start time in seconds (for audio processing)."""
        return pixels_to_seconds(self.start_pixels, self.pixels_per_beat, self.tempo)
    
    @property
    def duration_seconds(self) -> float:
        """Duration in seconds (for audio processing)."""
        return pixels_to_seconds(self.duration_pixels, self.pixels_per_beat, self.tempo)
    
    @property
    def end_seconds(self) -> float:
        """End time in seconds (start + duration)."""
        return self.start_seconds + self.duration_seconds
    
    @property
    def start_beats(self) -> float:
        """Start position in musical beats."""
        return pixels_to_beats(self.start_pixels, self.pixels_per_beat)
    
    @property
    def duration_beats(self) -> float:
        """Duration in musical beats."""
        return pixels_to_beats(self.duration_pixels, self.pixels_per_beat)
    
    @property
    def start_ticks(self) -> int:
        """Start position in MIDI ticks."""
        return pixels_to_ticks(self.start_pixels, self.pixels_per_beat, self.ppqn)
    
    @property
    def duration_ticks(self) -> int:
        """Duration in MIDI ticks."""
        return pixels_to_ticks(self.duration_pixels, self.pixels_per_beat, self.ppqn)
    
    @property
    def start_samples(self) -> int:
        """Start position in audio samples."""
        return pixels_to_samples(self.start_pixels, self.pixels_per_beat, self.tempo, self.sample_rate)
    
    @property
    def duration_samples(self) -> int:
        """Duration in audio samples."""
        return pixels_to_samples(self.duration_pixels, self.pixels_per_beat, self.tempo, self.sample_rate)
    
    def update_context(self, pixels_per_beat: float = None, tempo: float = None, 
                      sample_rate: int = None, ppqn: int = None) -> None:
        """Update musical context for timing calculations."""
        if pixels_per_beat is not None:
            self.pixels_per_beat = pixels_per_beat
        if tempo is not None:
            self.tempo = tempo
        if sample_rate is not None:
            self.sample_rate = sample_rate
        if ppqn is not None:
            self.ppqn = ppqn
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with frontend."""
        return {
            "id": self.id,
            "start": self.start_pixels,
            "duration": self.duration_pixels,
            "startFlicks": self.start_flicks,
            "durationFlicks": self.duration_flicks,
            "startSeconds": self.start_seconds,
            "durationSeconds": self.duration_seconds,
            "endSeconds": self.end_seconds,
            "startBeats": self.start_beats,
            "durationBeats": self.duration_beats,
            "startTicks": self.start_ticks,
            "durationTicks": self.duration_ticks,
            "startSample": self.start_samples,
            "durationSamples": self.duration_samples,
            "pitch": self.pitch,
            "velocity": self.velocity,
            "lyric": self.lyric
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], pixels_per_beat: float = 80.0, 
                  tempo: float = 120.0, sample_rate: int = 44100, ppqn: int = 480) -> 'Note':
        """Create Note from dictionary data."""
        return cls(
            id=data.get("id"),
            start_pixels=data["start"],
            duration_pixels=data["duration"],
            pitch=data["pitch"],
            velocity=data.get("velocity", 100),
            lyric=data.get("lyric", ""),
            pixels_per_beat=pixels_per_beat,
            tempo=tempo,
            sample_rate=sample_rate,
            ppqn=ppqn
        )
    
    def move_to(self, start_pixels: float) -> None:
        """Move note to new start position."""
        self.start_pixels = start_pixels
    
    def resize(self, duration_pixels: float) -> None:
        """Change note duration."""
        self.duration_pixels = duration_pixels
    
    def transpose(self, semitones: int) -> None:
        """Transpose note by semitones."""
        self.pitch = max(0, min(127, self.pitch + semitones)) 