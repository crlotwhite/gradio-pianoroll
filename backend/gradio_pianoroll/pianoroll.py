from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from gradio.components.base import Component
from gradio.events import Events
from gradio.i18n import I18nData

from .backend_data import PianoRollBackendData
from .note import Note

if TYPE_CHECKING:
    from gradio.components import Timer

class PianoRoll(Component):
    """
    PianoRoll custom Gradio component for MIDI note editing and playback.

    This class manages the state and data for the piano roll, including note timing, audio data,
    and backend/ frontend synchronization. It provides methods for preprocessing and postprocessing
    data, as well as updating backend audio/curve/segment data.

    Attributes:
        width (int): Width of the piano roll component in pixels.
        height (int): Height of the piano roll component in pixels.
        value (dict): Current piano roll data (notes, settings, etc.).
        audio_data (str|None): Backend audio data (base64 or URL).
        curve_data (dict): Backend curve data (pitch, loudness, etc.).
        segment_data (list): Backend segment data (timing, etc.).
        use_backend_audio (bool): Whether to use backend audio engine.
    """

    EVENTS = [
        Events.change,
        Events.input,
        Events.play,
        Events.pause,
        Events.stop,
        Events.clear,
    ]

    def __init__(
        self,
        value: dict | None = None,
        *,
        backend_data: PianoRollBackendData | None = None,
        label: str | I18nData | None = None,
        every: "Timer | float | None" = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        width: int | None = 1000,
        height: int | None = 600,
    ):
        """
        Parameters:
            value: default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            backend_data: PianoRollBackendData instance containing audio, curve, and segment data for backend processing
            label: the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: if True, will display label.
            scale: relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            width: width of the piano roll component in pixels.
            height: height of the piano roll component in pixels.
        """
        self.width = width
        self.height = height
        
        # Default settings
        self._default_pixels_per_beat = 80
        self._default_tempo = 120
        self._default_sample_rate = 44100
        self._default_ppqn = 480

        # Initialize backend data
        self.backend_data = backend_data or PianoRollBackendData()

        # Initialize value with default notes if not provided
        if value is None:
            self.value = self._create_default_value()
        else:
            self.value = self._normalize_value(value)

        self._attrs = {
            "width": width,
            "height": height,
            "value": self.value,
        }

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )
    
    def _create_default_value(self) -> Dict[str, Any]:
        """Create default piano roll value with sample notes."""
        default_notes = [
            Note(
                pitch=60, velocity=100, lyric="안녕",
                start_pixels=80, duration_pixels=80,
                pixels_per_beat=self._default_pixels_per_beat,
                tempo=self._default_tempo,
                sample_rate=self._default_sample_rate,
                ppqn=self._default_ppqn
            ).to_dict(),
            Note(
                pitch=64, velocity=90, lyric="하세요",
                start_pixels=160, duration_pixels=160,
                pixels_per_beat=self._default_pixels_per_beat,
                tempo=self._default_tempo,
                sample_rate=self._default_sample_rate,
                ppqn=self._default_ppqn
            ).to_dict(),
            Note(
                pitch=67, velocity=95, lyric="반가워요",
                start_pixels=320, duration_pixels=80,
                pixels_per_beat=self._default_pixels_per_beat,
                tempo=self._default_tempo,
                sample_rate=self._default_sample_rate,
                ppqn=self._default_ppqn
            ).to_dict()
        ]
        
        return {
            "notes": default_notes,
            "tempo": self._default_tempo,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": self._default_pixels_per_beat,
            "sampleRate": self._default_sample_rate,
            "ppqn": self._default_ppqn
        }
    
    def _normalize_value(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize input value, ensuring all notes have complete timing data."""
        if not value:
            return self._create_default_value()
        
        # Get context values
        pixels_per_beat = value.get("pixelsPerBeat", self._default_pixels_per_beat)
        tempo = value.get("tempo", self._default_tempo)
        sample_rate = value.get("sampleRate", self._default_sample_rate)
        ppqn = value.get("ppqn", self._default_ppqn)
        
        # Normalize notes
        if "notes" in value and value["notes"]:
            normalized_notes = []
            for note_data in value["notes"]:
                # Convert to Note object to ensure complete timing data
                note = Note.from_dict(note_data, pixels_per_beat, tempo, sample_rate, ppqn)
                normalized_notes.append(note.to_dict())
            value["notes"] = normalized_notes
        
        return value

    def preprocess(self, payload):
        """
        Preprocess incoming MIDI notes data from the frontend before passing to user function.
        Args:
            payload: The MIDI notes data to preprocess.
        Returns:
            The preprocessed data (passed through).
        """
        return payload

    def postprocess(self, value):
        """
        Postprocess outgoing MIDI notes data from the user function before sending to the frontend.
        Ensures all notes have complete timing data and attaches backend data if available.
        Args:
            value: The MIDI notes data to postprocess.
        Returns:
            The postprocessed data (with all required fields).
        """
        if not value:
            value = self._create_default_value()
        
        # Normalize the value to ensure complete timing data
        value = self._normalize_value(value)
        
        # Attach backend data if available
        if self.backend_data.has_data():
            backend_dict = self.backend_data.to_dict()
            value.update(backend_dict)
            
            print(f"🔊 [postprocess] Backend data attached:")
            print(f"   - audio_data: {bool(backend_dict.get('audio_data'))}")
            print(f"   - curve_data: {bool(backend_dict.get('curve_data'))}")
            print(f"   - segment_data: {bool(backend_dict.get('segment_data'))}")
            print(f"   - use_backend_audio: {backend_dict.get('use_backend_audio', False)}")

        return value

    def example_payload(self):
        """
        Example payload for the piano roll component (for documentation/testing).
        Returns:
            dict: Example piano roll data.
        """
        note = Note(
            pitch=60, velocity=100, lyric="안녕",
            start_pixels=80, duration_pixels=80,
            pixels_per_beat=80, tempo=120,
            sample_rate=44100, ppqn=480
        )

        return {
            "notes": [note.to_dict()],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80,
            "sampleRate": 44100,
            "ppqn": 480
        }

    def example_value(self):
        """
        Example value for the piano roll component (for documentation/testing).
        Returns:
            dict: Example piano roll data.
        """
        notes = [
            Note(
                pitch=60, velocity=100, lyric="안녕",
                start_pixels=80, duration_pixels=80,
                pixels_per_beat=80, tempo=120,
                sample_rate=44100, ppqn=480
            ).to_dict(),
            Note(
                pitch=64, velocity=90, lyric="하세요",
                start_pixels=160, duration_pixels=160,
                pixels_per_beat=80, tempo=120,
                sample_rate=44100, ppqn=480
            ).to_dict()
        ]

        return {
            "notes": notes,
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80,
            "sampleRate": 44100,
            "ppqn": 480
        }

    def api_info(self):
        """
        Returns OpenAPI-style schema for the piano roll data object.
        Returns:
            dict: API schema for the piano roll component.
        """
        return {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "start": {"type": "number", "description": "Start position in pixels"},
                            "duration": {"type": "number", "description": "Duration in pixels"},
                            "startFlicks": {"type": "number", "description": "Start position in flicks (precise timing)"},
                            "durationFlicks": {"type": "number", "description": "Duration in flicks (precise timing)"},
                            "startSeconds": {"type": "number", "description": "Start time in seconds (for audio processing)"},
                            "durationSeconds": {"type": "number", "description": "Duration in seconds (for audio processing)"},
                            "endSeconds": {"type": "number", "description": "End time in seconds (startSeconds + durationSeconds)"},
                            "startBeats": {"type": "number", "description": "Start position in musical beats"},
                            "durationBeats": {"type": "number", "description": "Duration in musical beats"},
                            "startTicks": {"type": "integer", "description": "Start position in MIDI ticks"},
                            "durationTicks": {"type": "integer", "description": "Duration in MIDI ticks"},
                            "startSample": {"type": "integer", "description": "Start position in audio samples"},
                            "durationSamples": {"type": "integer", "description": "Duration in audio samples"},
                            "pitch": {"type": "number", "description": "MIDI pitch (0-127)"},
                            "velocity": {"type": "number", "description": "MIDI velocity (0-127)"},
                            "lyric": {"type": "string", "description": "Optional lyric text"}
                        },
                        "required": ["id", "start", "duration", "startFlicks", "durationFlicks",
                                   "startSeconds", "durationSeconds", "endSeconds", "startBeats", "durationBeats",
                                   "startTicks", "durationTicks", "startSample", "durationSamples", "pitch", "velocity"]
                    }
                },
                "tempo": {
                    "type": "number",
                    "description": "BPM tempo"
                },
                "timeSignature": {
                    "type": "object",
                    "properties": {
                        "numerator": {"type": "number"},
                        "denominator": {"type": "number"}
                    },
                    "required": ["numerator", "denominator"]
                },
                "editMode": {
                    "type": "string",
                    "description": "Current edit mode"
                },
                "snapSetting": {
                    "type": "string",
                    "description": "Note snap setting"
                },
                "pixelsPerBeat": {
                    "type": "number",
                    "description": "Zoom level in pixels per beat"
                },
                "sampleRate": {
                    "type": "integer",
                    "description": "Audio sample rate (Hz) for sample-based timing calculations",
                    "default": 44100
                },
                "ppqn": {
                    "type": "integer",
                    "description": "Pulses Per Quarter Note for MIDI tick calculations",
                    "default": 480
                },
                # Backend data attributes for passing
                "audio_data": {
                    "type": "string",
                    "description": "Backend audio data (base64 encoded audio or URL)",
                    "nullable": True
                },
                "curve_data": {
                    "type": "object",
                    "description": "Linear curve data (pitch curves, loudness curves, etc.)",
                    "properties": {
                        "pitch_curve": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Pitch curve data points"
                        },
                        "loudness_curve": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Loudness curve data points"
                        },
                        "formant_curves": {
                            "type": "object",
                            "description": "Formant frequency curves",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        }
                    },
                    "additionalProperties": True,
                    "nullable": True
                },
                "segment_data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "number", "description": "Segment start time (seconds)"},
                            "end": {"type": "number", "description": "Segment end time (seconds)"},
                            "type": {"type": "string", "description": "Segment type (phoneme, syllable, word, etc.)"},
                            "value": {"type": "string", "description": "Segment value/text"},
                            "confidence": {"type": "number", "description": "Confidence score (0-1)", "minimum": 0, "maximum": 1}
                        },
                        "required": ["start", "end", "type", "value"]
                    },
                    "description": "Segmentation data (pronunciation timing, etc.)",
                    "nullable": True
                },
                "use_backend_audio": {
                    "type": "boolean",
                    "description": "Whether to use backend audio (disables frontend audio engine when true)",
                    "default": False
                }
            },
            "required": ["notes", "tempo", "timeSignature", "editMode", "snapSetting"],
            "description": "Piano roll data object containing notes array, settings, and optional backend data"
        }

    # Clean backend data management methods
    def set_audio_data(self, audio_data: str) -> None:
        """Set backend audio data."""
        self.backend_data.set_audio(audio_data)

    def add_curve_data(self, name: str, curve_data: Dict[str, Any]) -> None:
        """Add or update a curve dataset."""
        self.backend_data.add_curve(name, curve_data)

    def remove_curve_data(self, name: str) -> None:
        """Remove a curve dataset."""
        self.backend_data.remove_curve(name)

    def add_segment_data(self, segment: Dict[str, Any]) -> None:
        """Add a segment data entry."""
        self.backend_data.add_segment(segment)

    def clear_segment_data(self) -> None:
        """Clear all segment data."""
        self.backend_data.clear_segments()

    def enable_backend_audio(self, enable: bool = True) -> None:
        """Enable or disable backend audio engine."""
        self.backend_data.enable_backend_audio(enable)
    
    def get_backend_data(self) -> PianoRollBackendData:
        """Get the backend data object."""
        return self.backend_data
    
    # Convenience methods for working with notes
    def add_note(self, pitch: int, start_pixels: float, duration_pixels: float, 
                 velocity: int = 100, lyric: str = "") -> str:
        """Add a new note to the piano roll and return its ID."""
        pixels_per_beat = self.value.get("pixelsPerBeat", self._default_pixels_per_beat)
        tempo = self.value.get("tempo", self._default_tempo)
        sample_rate = self.value.get("sampleRate", self._default_sample_rate)
        ppqn = self.value.get("ppqn", self._default_ppqn)
        
        note = Note(
            pitch=pitch, velocity=velocity, lyric=lyric,
            start_pixels=start_pixels, duration_pixels=duration_pixels,
            pixels_per_beat=pixels_per_beat, tempo=tempo,
            sample_rate=sample_rate, ppqn=ppqn
        )
        
        if "notes" not in self.value:
            self.value["notes"] = []
        
        self.value["notes"].append(note.to_dict())
        return note.id
    
    def remove_note(self, note_id: str) -> bool:
        """Remove a note by ID. Returns True if found and removed."""
        if "notes" not in self.value:
            return False
        
        original_count = len(self.value["notes"])
        self.value["notes"] = [note for note in self.value["notes"] if note.get("id") != note_id]
        return len(self.value["notes"]) < original_count
