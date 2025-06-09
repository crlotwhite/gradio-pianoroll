"""
Audio utility functions for the PianoRoll component.

This module provides conversion utilities between audio frequencies, time values,
and piano roll pixel coordinates. Supports various data formats including numpy arrays,
lists, and scalar values for ease of use by AI/ML practitioners.

Functions:
    - hz_to_pixels: Convert frequency (Hz) to piano roll Y coordinates (pixels)
    - time_to_pixels: Convert time (seconds) to piano roll X coordinates (pixels)
    - hz_and_time_to_pixels: Convert frequency and time arrays to pixel coordinates
    - create_pitch_curve_data: Create complete pitch curve data for piano roll
    - create_loudness_curve_data: Create complete loudness curve data for piano roll
    - audio_array_to_base64_wav: Convert numpy audio array to base64 WAV string
"""

import numpy as np
import io
import base64
import wave
from typing import Union, Tuple, List, Dict, Any, Optional

# Piano roll constants
NOTE_HEIGHT = 20
TOTAL_NOTES = 128
PIANO_ROLL_HEIGHT = TOTAL_NOTES * NOTE_HEIGHT  # 2560 pixels

def hz_to_midi(frequency: Union[float, np.ndarray, List[float]]) -> Union[float, np.ndarray]:
    """
    Convert frequency (Hz) to MIDI note number.
    
    Args:
        frequency: Frequency in Hz (scalar, numpy array, or list)
        
    Returns:
        MIDI note number(s) (same type as input)
    """
    frequency = np.asarray(frequency)
    
    # Handle zero or negative frequencies
    valid_mask = frequency > 0
    result = np.zeros_like(frequency, dtype=float)
    
    if np.any(valid_mask):
        result[valid_mask] = 69 + 12 * np.log2(frequency[valid_mask] / 440.0)
    
    # Return scalar if input was scalar
    if np.isscalar(frequency) or (hasattr(frequency, 'shape') and frequency.shape == ()):
        return float(result)
    
    return result

def midi_to_y_pixels(midi_note: Union[float, np.ndarray, List[float]]) -> Union[float, np.ndarray]:
    """
    Convert MIDI note number to piano roll Y coordinate (pixels).
    
    Args:
        midi_note: MIDI note number (scalar, numpy array, or list)
        
    Returns:
        Y coordinate in pixels (same type as input)
    """
    midi_note = np.asarray(midi_note)
    
    # Clamp MIDI values to valid range (0-127)
    clamped_midi = np.clip(midi_note, 0, 127)
    
    # Convert to Y coordinate (inverted, with note center)
    y_pixels = (TOTAL_NOTES - 1 - clamped_midi) * NOTE_HEIGHT + NOTE_HEIGHT / 2
    
    # Return scalar if input was scalar
    if np.isscalar(midi_note) or (hasattr(midi_note, 'shape') and midi_note.shape == ()):
        return float(y_pixels)
    
    return y_pixels

def hz_to_pixels(frequency: Union[float, np.ndarray, List[float]]) -> Union[float, np.ndarray]:
    """
    Convert frequency (Hz) directly to piano roll Y coordinate (pixels).
    
    Args:
        frequency: Frequency in Hz (scalar, numpy array, or list)
        
    Returns:
        Y coordinate in pixels (same type as input)
        
    Example:
        >>> hz_to_pixels(440.0)  # A4
        1290.0
        >>> hz_to_pixels([440.0, 523.25])  # A4, C5
        array([1290. , 1230.])
        >>> hz_to_pixels(np.array([440.0, 523.25]))
        array([1290. , 1230.])
    """
    midi_notes = hz_to_midi(frequency)
    return midi_to_y_pixels(midi_notes)

def time_to_pixels(time_seconds: Union[float, np.ndarray, List[float]], 
                  tempo: float = 120, 
                  pixels_per_beat: float = 80) -> Union[float, np.ndarray]:
    """
    Convert time (seconds) to piano roll X coordinate (pixels).
    
    Args:
        time_seconds: Time in seconds (scalar, numpy array, or list)
        tempo: Tempo in BPM (default: 120)
        pixels_per_beat: Pixels per beat zoom level (default: 80)
        
    Returns:
        X coordinate in pixels (same type as input)
        
    Example:
        >>> time_to_pixels(1.0)  # 1 second at 120 BPM
        160.0
        >>> time_to_pixels([0.5, 1.0, 1.5])
        array([ 80., 160., 240.])
    """
    time_seconds = np.asarray(time_seconds)
    
    # Convert seconds to pixels: time * (tempo/60) * pixels_per_beat
    x_pixels = time_seconds * (tempo / 60.0) * pixels_per_beat
    
    # Return scalar if input was scalar
    if np.isscalar(time_seconds) or (hasattr(time_seconds, 'shape') and time_seconds.shape == ()):
        return float(x_pixels)
    
    return x_pixels

def hz_and_time_to_pixels(frequency: Union[np.ndarray, List[float]], 
                         time_seconds: Union[np.ndarray, List[float]],
                         tempo: float = 120,
                         pixels_per_beat: float = 80) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert frequency and time arrays to piano roll pixel coordinates.
    
    Args:
        frequency: Frequency values in Hz (numpy array or list)
        time_seconds: Time values in seconds (numpy array or list)
        tempo: Tempo in BPM (default: 120)
        pixels_per_beat: Pixels per beat zoom level (default: 80)
        
    Returns:
        Tuple of (x_pixels, y_pixels) as numpy arrays
        
    Example:
        >>> freqs = [440.0, 523.25, 659.25]  # A4, C5, E5
        >>> times = [0.5, 1.0, 1.5]
        >>> x_coords, y_coords = hz_and_time_to_pixels(freqs, times)
        >>> print(f"X: {x_coords}, Y: {y_coords}")
        X: [ 80. 160. 240.], Y: [1290. 1230. 1170.]
    """
    frequency = np.asarray(frequency)
    time_seconds = np.asarray(time_seconds)
    
    if frequency.shape != time_seconds.shape:
        raise ValueError(f"Frequency and time arrays must have the same shape. "
                        f"Got {frequency.shape} and {time_seconds.shape}")
    
    x_pixels = time_to_pixels(time_seconds, tempo, pixels_per_beat)
    y_pixels = hz_to_pixels(frequency)
    
    return x_pixels, y_pixels

def create_pitch_curve_data(frequency: Union[np.ndarray, List[float]], 
                           time_seconds: Union[np.ndarray, List[float]],
                           tempo: float = 120,
                           pixels_per_beat: float = 80,
                           color: str = "#FF6B6B",
                           line_width: int = 3,
                           opacity: float = 0.8) -> Dict[str, Any]:
    """
    Create complete pitch curve data for piano roll LineLayer.
    
    Args:
        frequency: Frequency values in Hz (numpy array or list)
        time_seconds: Time values in seconds (numpy array or list)
        tempo: Tempo in BPM (default: 120)
        pixels_per_beat: Pixels per beat zoom level (default: 80)
        color: Curve color (default: "#FF6B6B" - red)
        line_width: Line width in pixels (default: 3)
        opacity: Line opacity 0-1 (default: 0.8)
        
    Returns:
        Dictionary containing complete F0 curve data for piano roll
        
    Example:
        >>> freqs = librosa.pyin(audio, sr=sr)[0]  # Extract F0 using librosa
        >>> times = librosa.frames_to_time(np.arange(len(freqs)), sr=sr)
        >>> curve_data = create_pitch_curve_data(freqs, times)
        >>> piano_roll.set_curve_data({"f0_curve": curve_data})
    """
    frequency = np.asarray(frequency)
    time_seconds = np.asarray(time_seconds)
    
    # Filter out invalid frequencies (NaN, zero, negative)
    valid_mask = np.isfinite(frequency) & (frequency > 0)
    valid_freqs = frequency[valid_mask]
    valid_times = time_seconds[valid_mask]
    
    if len(valid_freqs) == 0:
        raise ValueError("No valid frequency data found (all values are NaN, zero, or negative)")
    
    # Convert to pixel coordinates
    x_pixels, y_pixels = hz_and_time_to_pixels(valid_freqs, valid_times, tempo, pixels_per_beat)
    
    # Create data points for LineLayer
    data_points = [
        {"x": float(x), "y": float(y)} 
        for x, y in zip(x_pixels, y_pixels)
    ]
    
    # Calculate metadata
    min_hz = float(np.min(valid_freqs))
    max_hz = float(np.max(valid_freqs))
    min_midi = hz_to_midi(min_hz)
    max_midi = hz_to_midi(max_hz)
    
    return {
        "color": color,
        "lineWidth": line_width,
        "yMin": 0,
        "yMax": PIANO_ROLL_HEIGHT,
        "position": "overlay",
        "renderMode": "piano_grid",
        "visible": True,
        "opacity": opacity,
        "data": data_points,
        "dataType": "f0",
        "unit": "Hz",
        "originalRange": {
            "minHz": min_hz,
            "maxHz": max_hz,
            "minMidi": float(min_midi),
            "maxMidi": float(max_midi)
        }
    }

def create_loudness_curve_data(loudness: Union[np.ndarray, List[float]], 
                              time_seconds: Union[np.ndarray, List[float]],
                              tempo: float = 120,
                              pixels_per_beat: float = 80,
                              use_db: bool = True,
                              y_min: Optional[float] = None,
                              y_max: Optional[float] = None,
                              color: str = "#4ECDC4",
                              line_width: int = 2,
                              opacity: float = 0.6) -> Dict[str, Any]:
    """
    Create complete loudness curve data for piano roll LineLayer.
    
    Args:
        loudness: Loudness values (RMS, dB, or normalized)
        time_seconds: Time values in seconds (numpy array or list)
        tempo: Tempo in BPM (default: 120)
        pixels_per_beat: Pixels per beat zoom level (default: 80)
        use_db: Whether loudness values are in dB (default: True)
        y_min: Minimum value for normalization (auto if None)
        y_max: Maximum value for normalization (auto if None)
        color: Curve color (default: "#4ECDC4" - cyan)
        line_width: Line width in pixels (default: 2)
        opacity: Line opacity 0-1 (default: 0.6)
        
    Returns:
        Dictionary containing complete loudness curve data for piano roll
        
    Example:
        >>> rms = librosa.feature.rms(y=audio)[0]  # Extract RMS using librosa
        >>> times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
        >>> curve_data = create_loudness_curve_data(rms, times, use_db=False)
        >>> piano_roll.set_curve_data({"loudness_curve": curve_data})
    """
    loudness = np.asarray(loudness)
    time_seconds = np.asarray(time_seconds)
    
    if loudness.shape != time_seconds.shape:
        raise ValueError(f"Loudness and time arrays must have the same shape. "
                        f"Got {loudness.shape} and {time_seconds.shape}")
    
    # Filter out invalid values
    valid_mask = np.isfinite(loudness)
    valid_loudness = loudness[valid_mask]
    valid_times = time_seconds[valid_mask]
    
    if len(valid_loudness) == 0:
        raise ValueError("No valid loudness data found (all values are NaN)")
    
    # Convert time to X coordinates
    x_pixels = time_to_pixels(valid_times, tempo, pixels_per_beat)
    
    # Normalize loudness to 0-1 range
    if y_min is None:
        y_min = float(np.min(valid_loudness))
    if y_max is None:
        y_max = float(np.max(valid_loudness))
    
    if y_max == y_min:
        normalized_loudness = np.ones_like(valid_loudness) * 0.5
    else:
        normalized_loudness = (valid_loudness - y_min) / (y_max - y_min)
    
    # Convert to Y coordinates (full piano roll height)
    y_pixels = normalized_loudness * PIANO_ROLL_HEIGHT
    
    # Create data points for LineLayer
    data_points = [
        {"x": float(x), "y": float(y)} 
        for x, y in zip(x_pixels, y_pixels)
    ]
    
    return {
        "color": color,
        "lineWidth": line_width,
        "yMin": 0,
        "yMax": PIANO_ROLL_HEIGHT,
        "position": "overlay",
        "renderMode": "independent_range",
        "visible": True,
        "opacity": opacity,
        "data": data_points,
        "dataType": "loudness",
        "unit": "dB" if use_db else "normalized",
        "originalRange": {
            "min": float(np.min(valid_loudness)),
            "max": float(np.max(valid_loudness)),
            "y_min": y_min,
            "y_max": y_max
        }
    }

def audio_array_to_base64_wav(audio_data: np.ndarray, 
                             sample_rate: int = 44100,
                             normalize: bool = True) -> str:
    """
    Convert numpy audio array to base64 encoded WAV string.
    
    Args:
        audio_data: Audio data as numpy array (float32 or float64)
        sample_rate: Sample rate in Hz (default: 44100)
        normalize: Whether to normalize audio to prevent clipping (default: True)
        
    Returns:
        Base64 encoded WAV data string (data:audio/wav;base64,...)
        
    Example:
        >>> import numpy as np
        >>> audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))  # 1s sine wave
        >>> audio_base64 = audio_array_to_base64_wav(audio)
        >>> piano_roll.set_audio_data(audio_base64)
    """
    audio_data = np.asarray(audio_data, dtype=np.float64)
    
    if normalize:
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude > 0:
            audio_data = audio_data / max_amplitude * 0.9  # 90% to prevent clipping
    
    # Convert to 16-bit PCM
    audio_16bit = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())
    
    # Encode to base64
    buffer.seek(0)
    wav_data = buffer.read()
    base64_data = base64.b64encode(wav_data).decode('utf-8')
    
    return f"data:audio/wav;base64,{base64_data}"

# Convenience functions for common use cases
def librosa_f0_to_pixels(f0_values: np.ndarray, 
                        sr: int = 22050, 
                        hop_length: int = 512,
                        tempo: float = 120,
                        pixels_per_beat: float = 80) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert librosa F0 extraction results to piano roll pixel coordinates.
    
    Args:
        f0_values: F0 values from librosa.pyin() or similar
        sr: Sample rate used for F0 extraction
        hop_length: Hop length used for F0 extraction
        tempo: Piano roll tempo in BPM
        pixels_per_beat: Piano roll pixels per beat
        
    Returns:
        Tuple of (x_pixels, y_pixels) for valid F0 points
    """
    # Calculate time axis
    times = np.arange(len(f0_values)) * hop_length / sr
    
    # Filter valid F0 values
    valid_mask = np.isfinite(f0_values) & (f0_values > 0)
    valid_f0 = f0_values[valid_mask]
    valid_times = times[valid_mask]
    
    if len(valid_f0) == 0:
        return np.array([]), np.array([])
    
    return hz_and_time_to_pixels(valid_f0, valid_times, tempo, pixels_per_beat)

def librosa_rms_to_pixels(rms_values: np.ndarray,
                         sr: int = 22050,
                         hop_length: int = 512,
                         tempo: float = 120,
                         pixels_per_beat: float = 80,
                         to_db: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert librosa RMS extraction results to piano roll pixel coordinates.
    
    Args:
        rms_values: RMS values from librosa.feature.rms()
        sr: Sample rate used for RMS extraction
        hop_length: Hop length used for RMS extraction
        tempo: Piano roll tempo in BPM
        pixels_per_beat: Piano roll pixels per beat
        to_db: Whether to convert RMS to dB scale
        
    Returns:
        Tuple of (x_pixels, y_pixels) for loudness curve
    """
    # Calculate time axis
    times = np.arange(len(rms_values)) * hop_length / sr
    
    # Convert to dB if requested
    if to_db:
        # Convert to dB relative to max
        max_rms = np.max(rms_values)
        if max_rms > 0:
            loudness_values = 20 * np.log10(np.maximum(rms_values / max_rms, 1e-6))
            loudness_values = np.maximum(loudness_values, -60)  # Floor at -60dB
        else:
            loudness_values = np.full_like(rms_values, -60)
    else:
        loudness_values = rms_values
    
    # Convert time to X coordinates
    x_pixels = time_to_pixels(times, tempo, pixels_per_beat)
    
    # Normalize and convert to Y coordinates
    if to_db:
        # Normalize -60dB to 0dB -> 0 to 1
        normalized = (loudness_values + 60) / 60
    else:
        # Normalize 0 to max -> 0 to 1
        max_val = np.max(loudness_values)
        normalized = loudness_values / max_val if max_val > 0 else np.zeros_like(loudness_values)
    
    y_pixels = normalized * PIANO_ROLL_HEIGHT
    
    return x_pixels, y_pixels 