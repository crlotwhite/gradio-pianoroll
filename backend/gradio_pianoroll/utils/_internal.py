"""
Internal helper functions for the utils module.

These functions are not part of the public API and should not be
imported directly by users.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np


def _create_f0_line_data(
    f0_values: List[float], total_duration: float, tempo: int, pixels_per_beat: int
) -> Dict:
    """
    Convert F0 data to LineLayer format.

    Args:
        f0_values: List of F0 (fundamental frequency) values.
        total_duration: Total duration in seconds.
        tempo: BPM.
        pixels_per_beat: Pixels per beat for coordinate conversion.

    Returns:
        Dictionary containing line data for F0 curve visualization.
    """
    data_points = []

    for i, f0 in enumerate(f0_values):
        if f0 > 0:  # Valid F0 only
            time_sec = (i / len(f0_values)) * total_duration
            x_pixel = time_sec * (tempo / 60) * pixels_per_beat

            # Convert F0 to MIDI note, then to Y coordinate
            midi_note = 69 + 12 * np.log2(f0 / 440)
            y_pixel = (127 - midi_note) * 20  # 20 is NOTE_HEIGHT

            data_points.append({"x": x_pixel, "y": y_pixel})

    return {
        "f0_curve": {
            "color": "#FF6B6B",
            "lineWidth": 2,
            "yMin": 0,
            "yMax": 2560,
            "position": "overlay",
            "renderMode": "piano_grid",
            "data": data_points,
        }
    }
