
import gradio as gr
from app import demo as app
import os

_docs = {'PianoRoll': {'description': 'PianoRoll custom Gradio component for MIDI note editing and playback.\n\nThis class manages the state and data for the piano roll, including note timing, audio data,\nand backend/ frontend synchronization. It provides methods for preprocessing and postprocessing\ndata, as well as updating backend audio/curve/segment data.\n\n    width (int): Width of the piano roll component in pixels.\n    height (int): Height of the piano roll component in pixels.\n    value (dict): Current piano roll data (notes, settings, etc.).\n    audio_data (str|None): Backend audio data (base64 or URL).\n    curve_data (dict): Backend curve data (pitch, loudness, etc.).\n    segment_data (list): Backend segment data (timing, etc.).\n    use_backend_audio (bool): Whether to use backend audio engine.', 'members': {'__init__': {'value': {'type': 'dict | None', 'default': 'None', 'description': 'default MIDI notes data to provide in piano roll. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'audio_data': {'type': 'str | None', 'default': 'None', 'description': '백엔드에서 전달받은 오디오 데이터 (base64 인코딩된 오디오 또는 URL)'}, 'curve_data': {'type': 'dict | None', 'default': 'None', 'description': '백엔드에서 전달받은 선형 데이터 (피치 곡선, loudness 곡선 등)'}, 'segment_data': {'type': 'list | None', 'default': 'None', 'description': '백엔드에서 전달받은 구간 데이터 (발음 타이밍 등)'}, 'use_backend_audio': {'type': 'bool', 'default': 'False', 'description': '백엔드 오디오를 사용할지 여부 (True시 프론트엔드 오디오 엔진 비활성화)'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'every': {'type': '"Timer | float | None"', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an editable piano roll; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'width': {'type': 'int | None', 'default': '1000', 'description': 'width of the piano roll component in pixels.'}, 'height': {'type': 'int | None', 'default': '600', 'description': 'height of the piano roll component in pixels.'}}, 'postprocess': {}, 'preprocess': {}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the PianoRoll changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the PianoRoll.'}, 'play': {'type': None, 'default': None, 'description': 'This listener is triggered when the user plays the media in the PianoRoll.'}, 'pause': {'type': None, 'default': None, 'description': 'This listener is triggered when the media in the PianoRoll stops for any reason.'}, 'stop': {'type': None, 'default': None, 'description': 'This listener is triggered when the user reaches the end of the media playing in the PianoRoll.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the PianoRoll using the clear button for the component.'}}}, '__meta__': {'additional_interfaces': {}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_pianoroll`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_pianoroll/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_pianoroll"></a>  
</div>

A PianoRoll Component for Gradio.
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_pianoroll
```

## Usage

```python
import gradio as gr
import numpy as np
import io
import base64
import wave
import tempfile
import os
from gradio_pianoroll import PianoRoll

# Additional imports for F0 analysis
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ librosa available")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa not installed. F0 analysis functionality is limited.")

# Synthesizer settings
SAMPLE_RATE = 44100
MAX_DURATION = 10.0  # Maximum 10 seconds

# User-defined phoneme mapping (global state)
user_phoneme_map = {}

def initialize_phoneme_map():
    \"\"\"Initialize with default Korean phoneme mapping\"\"\"
    global user_phoneme_map
    user_phoneme_map = {
        '가': 'g a',
        '나': 'n a',
        '다': 'd a',
        '라': 'l aa',
        '마': 'm a',
        '바': 'b a',
        '사': 's a',
        '아': 'aa',
        '자': 'j a',
        '차': 'ch a',
        '카': 'k a',
        '타': 't a',
        '파': 'p a',
        '하': 'h a',
        '도': 'd o',
        '레': 'l e',
        '미': 'm i',
        '파': 'p aa',
        '솔': 's o l',
        '라': 'l aa',
        '시': 's i',
        '안녕': 'aa n ny eo ng',
        '하세요': 'h a s e y o',
        '노래': 'n o l ae',
        '사랑': 's a l a ng',
        '행복': 'h ae ng b o k',
        '음악': 'eu m a k',
        '피아노': 'p i a n o'
    }

# Initialize phoneme mapping at program start
initialize_phoneme_map()

def get_phoneme_mapping_list():
    \"\"\"Return current phoneme mapping list (for UI display)\"\"\"
    global user_phoneme_map
    return [{"lyric": k, "phoneme": v} for k, v in user_phoneme_map.items()]

def get_phoneme_mapping_for_dataframe():
    \"\"\"Return phoneme mapping list for DataFrame\"\"\"
    global user_phoneme_map
    return [[k, v] for k, v in user_phoneme_map.items()]

def add_phoneme_mapping(lyric: str, phoneme: str):
    \"\"\"Add new phoneme mapping\"\"\"
    global user_phoneme_map
    user_phoneme_map[lyric.strip()] = phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"'{lyric}' → '{phoneme}' mapping added."

def update_phoneme_mapping(old_lyric: str, new_lyric: str, new_phoneme: str):
    \"\"\"Update existing phoneme mapping\"\"\"
    global user_phoneme_map

    # Delete existing mapping
    if old_lyric in user_phoneme_map:
        del user_phoneme_map[old_lyric]

    # Add new mapping
    user_phoneme_map[new_lyric.strip()] = new_phoneme.strip()
    return get_phoneme_mapping_for_dataframe(), f"Mapping updated to '{new_lyric}' → '{new_phoneme}'."

def delete_phoneme_mapping(lyric: str):
    \"\"\"Delete phoneme mapping\"\"\"
    global user_phoneme_map
    if lyric in user_phoneme_map:
        del user_phoneme_map[lyric]
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' mapping deleted."
    else:
        return get_phoneme_mapping_for_dataframe(), f"'{lyric}' mapping not found."

def reset_phoneme_mapping():
    \"\"\"Reset phoneme mapping to default values\"\"\"
    initialize_phoneme_map()
    return get_phoneme_mapping_for_dataframe(), "Phoneme mapping reset to default values."

def midi_to_frequency(midi_note):
    \"\"\"Convert MIDI note number to frequency (A4 = 440Hz)\"\"\"
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def create_adsr_envelope(attack, decay, sustain, release, duration, sample_rate):
    \"\"\"Generate ADSR envelope\"\"\"
    total_samples = int(duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples

    # Adjust sustain section to avoid negative values
    if sustain_samples < 0:
        sustain_samples = 0
        total_samples = attack_samples + decay_samples + release_samples

    envelope = np.zeros(total_samples)

    # Attack phase
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay phase
    if decay_samples > 0:
        start_idx = attack_samples
        end_idx = attack_samples + decay_samples
        envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)

    # Sustain phase
    if sustain_samples > 0:
        start_idx = attack_samples + decay_samples
        end_idx = start_idx + sustain_samples
        envelope[start_idx:end_idx] = sustain

    # Release phase
    if release_samples > 0:
        start_idx = attack_samples + decay_samples + sustain_samples
        envelope[start_idx:] = np.linspace(sustain, 0, release_samples)

    return envelope

def generate_sine_wave(frequency, duration, sample_rate):
    \"\"\"Generate sine wave\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_sawtooth_wave(frequency, duration, sample_rate):
    \"\"\"Generate sawtooth wave\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    # 2 * (t * frequency - np.floor(0.5 + t * frequency))
    return 2 * (t * frequency % 1) - 1

def generate_square_wave(frequency, duration, sample_rate):
    \"\"\"Generate square wave\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sign(np.sin(2 * np.pi * frequency * t))

def generate_triangle_wave(frequency, duration, sample_rate):
    \"\"\"Generate triangle wave\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1

def generate_harmonic_wave(frequency, duration, sample_rate, harmonics=5):
    \"\"\"Generate complex waveform with harmonics\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    wave = np.zeros_like(t)

    # Fundamental frequency
    wave += np.sin(2 * np.pi * frequency * t)

    # Add harmonics (amplitude decreases by 1/n)
    for n in range(2, harmonics + 1):
        amplitude = 1.0 / n
        wave += amplitude * np.sin(2 * np.pi * frequency * n * t)

    # Normalize
    wave = wave / np.max(np.abs(wave))
    return wave

def generate_fm_wave(frequency, duration, sample_rate, mod_freq=5.0, mod_depth=2.0):
    \"\"\"Generate FM waveform\"\"\"
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # Modulator
    modulator = mod_depth * np.sin(2 * np.pi * mod_freq * t)

    # Carrier with frequency modulation
    carrier = np.sin(2 * np.pi * frequency * t + modulator)

    return carrier

def generate_complex_wave(frequency, duration, sample_rate, wave_type='complex'):
    \"\"\"Generate complex waveform (combination of multiple techniques)\"\"\"
    if wave_type == 'sine':
        return generate_sine_wave(frequency, duration, sample_rate)
    elif wave_type == 'sawtooth':
        return generate_sawtooth_wave(frequency, duration, sample_rate)
    elif wave_type == 'square':
        return generate_square_wave(frequency, duration, sample_rate)
    elif wave_type == 'triangle':
        return generate_triangle_wave(frequency, duration, sample_rate)
    elif wave_type == 'harmonic':
        return generate_harmonic_wave(frequency, duration, sample_rate, harmonics=7)
    elif wave_type == 'fm':
        return generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.1, mod_depth=3.0)
    else:  # 'complex' - combination of multiple waveforms
        # Basic sawtooth + harmonics + some FM
        base = generate_sawtooth_wave(frequency, duration, sample_rate) * 0.6
        harmonic = generate_harmonic_wave(frequency, duration, sample_rate, harmonics=4) * 0.3
        fm = generate_fm_wave(frequency, duration, sample_rate, mod_freq=frequency * 0.05, mod_depth=1.0) * 0.1

        return base + harmonic + fm

def synthesize_audio(piano_roll_data, attack=0.01, decay=0.1, sustain=0.7, release=0.3, wave_type='complex'):
    \"\"\"Synthesize audio from PianoRoll data\"\"\"
    if not piano_roll_data or 'notes' not in piano_roll_data or not piano_roll_data['notes']:
        return None

    notes = piano_roll_data['notes']
    tempo = piano_roll_data.get('tempo', 120)
    pixels_per_beat = piano_roll_data.get('pixelsPerBeat', 80)

    # Calculate total length (up to the end of the last note)
    max_end_time = 0
    for note in notes:
        # Convert pixels to seconds (considering tempo and pixels per beat)
        start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
        duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)
        end_time = start_seconds + duration_seconds
        max_end_time = max(max_end_time, end_time)

    # Limit maximum length
    total_duration = min(max_end_time + 1.0, MAX_DURATION)  # Add 1 second buffer
    total_samples = int(total_duration * SAMPLE_RATE)

    # Final audio buffer
    audio_buffer = np.zeros(total_samples)

    # Process each note
    for i, note in enumerate(notes):
        try:
            # Note properties
            pitch = note['pitch']
            velocity = note.get('velocity', 100)

            # Calculate time
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            # Check range
            if start_seconds >= total_duration:
                continue

            # Adjust duration to not exceed total length
            if start_seconds + duration_seconds > total_duration:
                duration_seconds = total_duration - start_seconds

            if duration_seconds <= 0:
                continue

            # Calculate frequency
            frequency = midi_to_frequency(pitch)

            # Calculate volume (normalize velocity to 0-1)
            volume = velocity / 127.0

            # Use same waveform type for all notes (consistency)
            # Generate complex waveform
            base_wave = generate_complex_wave(frequency, duration_seconds, SAMPLE_RATE, wave_type)

            # Additional effect: Vibrato (frequency modulation)
            t = np.linspace(0, duration_seconds, len(base_wave), False)
            vibrato_freq = 4.5  # 4.5Hz Vibrato
            vibrato_depth = 0.02  # 2% frequency modulation
            vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)

            # Apply vibrato to waveform (simple approximation)
            vibrato_wave = base_wave * vibrato

            # Additional effect: Tremolo (amplitude modulation)
            tremolo_freq = 3.0  # 3Hz Tremolo
            tremolo_depth = 0.1  # 10% amplitude modulation
            tremolo = 1 + tremolo_depth * np.sin(2 * np.pi * tremolo_freq * t)

            # Apply tremolo to waveform
            final_wave = vibrato_wave * tremolo

            # Apply ADSR envelope
            envelope = create_adsr_envelope(attack, decay, sustain, release, duration_seconds, SAMPLE_RATE)

            # Adjust envelope and waveform length
            min_length = min(len(final_wave), len(envelope))
            note_audio = final_wave[:min_length] * envelope[:min_length] * volume * 0.25  # Adjust volume

            # Add to audio buffer
            start_sample = int(start_seconds * SAMPLE_RATE)
            end_sample = start_sample + len(note_audio)

            # Add only within buffer range
            if start_sample < total_samples:
                end_sample = min(end_sample, total_samples)
                audio_length = end_sample - start_sample
                if audio_length > 0:
                    audio_buffer[start_sample:end_sample] += note_audio[:audio_length]

        except Exception as e:
            print(f"Error processing note: {e}")
            continue

    # Prevent clipping (normalize)
    max_amplitude = np.max(np.abs(audio_buffer))
    if max_amplitude > 0:
        audio_buffer = audio_buffer / max_amplitude * 0.9  # Limit to 90%

    return audio_buffer

def audio_to_base64_wav(audio_data, sample_rate):
    \"\"\"Convert audio data to base64 encoded WAV\"\"\"
    if audio_data is None or len(audio_data) == 0:
        return None

    # Convert to 16-bit PCM
    audio_16bit = (audio_data * 32767).astype(np.int16)

    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_16bit.tobytes())

    # base64 encoding
    buffer.seek(0)
    wav_data = buffer.read()
    base64_data = base64.b64encode(wav_data).decode('utf-8')

    return f"data:audio/wav;base64,{base64_data}"

def calculate_waveform_data(audio_data, pixels_per_beat, tempo, target_width=1000):
    \"\"\"Calculate waveform visualization data from audio data\"\"\"
    if audio_data is None or len(audio_data) == 0:
        return None

    # Calculate total audio duration (seconds)
    audio_duration = len(audio_data) / SAMPLE_RATE

    # Calculate total pixel length (based on tempo and pixels per beat)
    total_pixels = (tempo / 60) * pixels_per_beat * audio_duration

    # Calculate samples per pixel
    samples_per_pixel = len(audio_data) / total_pixels

    waveform_points = []

    # Calculate min/max values for each pixel
    for pixel in range(int(total_pixels)):
        start_sample = int(pixel * samples_per_pixel)
        end_sample = int((pixel + 1) * samples_per_pixel)
        end_sample = min(end_sample, len(audio_data))

        if start_sample >= len(audio_data):
            break

        if start_sample < end_sample:
            # Audio data for the pixel range
            pixel_data = audio_data[start_sample:end_sample]

            # Calculate min, max values
            min_val = float(np.min(pixel_data))
            max_val = float(np.max(pixel_data))

            # Time information (pixel position)
            time_position = pixel

            waveform_points.append({
                'x': time_position,
                'min': min_val,
                'max': max_val
            })

    return waveform_points

def convert_basic(piano_roll):
    \"\"\"Basic conversion function (first tab)\"\"\"
    print("=== Basic Convert function called ===")
    print("Received piano_roll:")
    print(piano_roll)
    print("Type:", type(piano_roll))
    return piano_roll

def synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    \"\"\"Synthesize audio and pass it to the piano roll\"\"\"
    print("=== Synthesize function called ===")
    print("Piano roll data:", piano_roll)
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")

    # Synthesize audio
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        print("Audio synthesis failed")
        return piano_roll, "Audio synthesis failed", None

    # Convert to base64 (for piano roll)
    audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)

    # Create WAV file for gradio Audio component
    gradio_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)

    # Add audio data to piano roll data
    updated_piano_roll = piano_roll.copy() if piano_roll else {}
    updated_piano_roll['audio_data'] = audio_base64
    updated_piano_roll['use_backend_audio'] = True

    print(f"🔊 [synthesize_and_play] Setting backend audio data:")
    print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
    print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")
    print(f"   - audio_base64 preview: {audio_base64[:50] + '...' if audio_base64 else 'None'}")

    # Calculate waveform data
    pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)
    tempo = updated_piano_roll.get('tempo', 120)
    waveform_data = calculate_waveform_data(audio_data, pixels_per_beat, tempo)

    # Example curve data (pitch curve + waveform data)
    curve_data = {}

    # Add waveform data
    if waveform_data:
        curve_data['waveform_data'] = waveform_data
        print(f"Waveform data created: {len(waveform_data)} points")

    # Pitch curve data (existing)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        pitch_curve = []
        for note in updated_piano_roll['notes']:
            # Simple example: create curve based on note pitch
            base_pitch = note['pitch']
            # Slightly vibrato effect
            curve_points = [base_pitch + 0.5 * np.sin(i * 0.5) for i in range(10)]
            pitch_curve.extend(curve_points)

        curve_data['pitch_curve'] = pitch_curve[:100]  # Limit to 100 points

    updated_piano_roll['curve_data'] = curve_data

    # Example segment data (phoneme timing)
    if 'notes' in updated_piano_roll and updated_piano_roll['notes']:
        segment_data = []

        for i, note in enumerate(updated_piano_roll['notes']):
            start_seconds = (note['start'] / pixels_per_beat) * (60.0 / tempo)
            duration_seconds = (note['duration'] / pixels_per_beat) * (60.0 / tempo)

            segment_data.append({
                'start': start_seconds,
                'end': start_seconds + duration_seconds,
                'type': 'note',
                'value': note.get('lyric', f"Note_{i+1}"),
                'confidence': 0.95
            })

        updated_piano_roll['segment_data'] = segment_data

    print(f"Audio synthesis completed: {len(audio_data)} samples")
    if waveform_data:
        print(f"Waveform points: {len(waveform_data)}")

    status_message = f"Audio synthesis completed ({wave_type} waveform): {len(audio_data)} samples, duration: {len(audio_data)/SAMPLE_RATE:.2f} seconds"

    return updated_piano_roll, status_message, gradio_audio_path

def create_temp_wav_file(audio_data, sample_rate):
    \"\"\"Create temporary WAV file for gradio Audio component\"\"\"
    if audio_data is None or len(audio_data) == 0:
        return None

    try:
        # Convert to 16-bit PCM
        audio_16bit = (audio_data * 32767).astype(np.int16)

        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())

        # Close file descriptor
        os.close(temp_fd)

        return temp_path
    except Exception as e:
        print(f"Error creating temporary WAV file: {e}")
        return None

def clear_and_regenerate_waveform(piano_roll, attack, decay, sustain, release, wave_type='complex'):
    \"\"\"Clear and regenerate waveform\"\"\"
    print("=== Clear and Regenerate Waveform ===")

    # First clear waveform data
    cleared_piano_roll = piano_roll.copy() if piano_roll else {}
    cleared_piano_roll['curve_data'] = {}  # Initialize curve data
    cleared_piano_roll['audio_data'] = None  # Initialize audio data
    cleared_piano_roll['use_backend_audio'] = False  # Disable backend audio

    # Message for waiting
    yield cleared_piano_roll, "Clearing waveform...", None

    # Then regenerate new waveform
    result_piano_roll, status_message, gradio_audio_path = synthesize_and_play(piano_roll, attack, decay, sustain, release, wave_type)

    yield result_piano_roll, f"Regeneration completed! {status_message}", gradio_audio_path

# G2P (Grapheme-to-Phoneme) function (using custom mapping)
def mock_g2p(text: str) -> str:
    \"\"\"
    Korean G2P function using custom mapping
    \"\"\"
    global user_phoneme_map

    # Convert text to lowercase and remove whitespace
    text = text.strip()

    # Find in custom mapping
    if text in user_phoneme_map:
        return user_phoneme_map[text]

    # If not found, process each character
    result = []
    for char in text:
        if char in user_phoneme_map:
            result.append(user_phoneme_map[char])
        else:
            # Unknown characters are returned as is
            result.append(char)

    return ' '.join(result)

def process_lyric_input(piano_roll, lyric_data):
    \"\"\"
    Process lyric input event and run G2P to create phoneme
    \"\"\"
    print("=== G2P Processing ===")
    print("Piano roll data:", piano_roll)
    print("Lyric data:", lyric_data)

    if not piano_roll or not lyric_data:
        return piano_roll, "Lyric data is missing."

    # Run G2P for new lyric
    new_lyric = lyric_data.get('newLyric', '')
    if new_lyric:
        # Run G2P (using mock function)
        phoneme = mock_g2p(new_lyric)
        print(f"G2P result: '{new_lyric}' -> '{phoneme}'")

        # Update phoneme for the corresponding note
        note_id = lyric_data.get('noteId')
        if note_id and 'notes' in piano_roll:
            notes = piano_roll['notes'].copy()
            for note in notes:
                if note.get('id') == note_id:
                    note['phoneme'] = phoneme
                    print(f"Note {note_id} phoneme updated: {phoneme}")
                    break

            # Return updated piano roll data
            updated_piano_roll = piano_roll.copy()
            updated_piano_roll['notes'] = notes

            return updated_piano_roll, f"G2P completed: '{new_lyric}' -> [{phoneme}]"

    return piano_roll, "G2P processing completed"

def manual_phoneme_update(piano_roll, note_index, phoneme_text):
    \"\"\"
    Manually update phoneme for a specific note
    \"\"\"
    print(f"=== Manual Phoneme Update ===")
    print(f"Note index: {note_index}, Phoneme: '{phoneme_text}'")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "Piano roll data is missing."

    notes = piano_roll['notes'].copy()

    if 0 <= note_index < len(notes):
        notes[note_index]['phoneme'] = phoneme_text

        updated_piano_roll = piano_roll.copy()
        updated_piano_roll['notes'] = notes

        lyric = notes[note_index].get('lyric', '?')
        return updated_piano_roll, f"Note {note_index + 1} ('{lyric}') phoneme set to '{phoneme_text}'"
    else:
        return piano_roll, f"Invalid note index: {note_index}"

def clear_all_phonemes(piano_roll):
    \"\"\"
    Clear all phonemes for all notes
    \"\"\"
    print("=== Clear All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "Piano roll data is missing."

    notes = piano_roll['notes'].copy()

    for note in notes:
        note['phoneme'] = None

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, "All phonemes cleared."

def auto_generate_all_phonemes(piano_roll):
    \"\"\"
    Automatically generate phoneme for all lyrics
    \"\"\"
    print("=== Auto Generate All Phonemes ===")

    if not piano_roll or 'notes' not in piano_roll:
        return piano_roll, "Piano roll data is missing."

    notes = piano_roll['notes'].copy()

    updated_count = 0
    for note in notes:
        lyric = note.get('lyric')
        if lyric:
            phoneme = mock_g2p(lyric)
            note['phoneme'] = phoneme
            updated_count += 1
            print(f"Auto-generated: '{lyric}' -> '{phoneme}'")

    updated_piano_roll = piano_roll.copy()
    updated_piano_roll['notes'] = notes

    return updated_piano_roll, f"{updated_count} notes' phoneme auto-generated"

# Functions for analyzing F0 and audio features
def extract_f0_from_audio(audio_file_path, f0_method="pyin"):
    \"\"\"
    Extract F0 (fundamental frequency) from audio file
    \"\"\"
    if not LIBROSA_AVAILABLE:
        return None, "librosa is not installed, so F0 analysis cannot be performed"

    try:
        print(f"🎵 F0 extraction started: {audio_file_path}")

        # Load audio
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - Sample rate: {sr}Hz")
        print(f"   - Length: {len(y)/sr:.2f} seconds")

        # Select F0 extraction method
        if f0_method == "pyin":
            # Use PYIN algorithm (more accurate but slower)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                sr=sr,
                fmin=librosa.note_to_hz('C2'),  # Approx. 65Hz
                fmax=librosa.note_to_hz('C7')   # Approx. 2093Hz
            )
        else:
            # Fundamental pitch extraction
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            f0 = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                f0.append(pitch if pitch > 0 else np.nan)
            f0 = np.array(f0)

        # Calculate time axis
        hop_length = 512  # librosa default
        frame_times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)

        # Handle NaN values and smoothing
        valid_indices = ~np.isnan(f0)
        if np.sum(valid_indices) == 0:
            return None, "Valid F0 values not found"

        # Use only valid F0 values
        valid_f0 = f0[valid_indices]
        valid_times = frame_times[valid_indices]

        print(f"   - Extracted F0 points: {len(valid_f0)}")
        print(f"   - F0 range: {np.min(valid_f0):.1f}Hz ~ {np.max(valid_f0):.1f}Hz")

        # Return voiced/unvoiced information as well
        result_data = {
            'times': frame_times,  # Full time axis
            'f0_values': f0,  # Full F0 (includes NaN)
            'valid_times': valid_times,  # Only valid times
            'valid_f0_values': valid_f0,  # Only valid F0
            'sample_rate': sr,
            'duration': len(y) / sr,
            'hop_length': hop_length
        }

        # Add voiced information from PYIN
        if f0_method == "pyin" and 'voiced_flag' in locals() and 'voiced_probs' in locals():
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs
        else:
            # For other methods, estimate voiced based on F0 existence
            voiced_flag = ~np.isnan(f0)
            voiced_probs = voiced_flag.astype(float)
            result_data['voiced_flag'] = voiced_flag
            result_data['voiced_probs'] = voiced_probs

        return result_data, "F0 extraction completed"

    except Exception as e:
        print(f"❌ F0 extraction error: {e}")
        return None, f"F0 extraction error: {str(e)}"

def extract_loudness_from_audio(audio_file_path):
    \"\"\"
    Extract loudness (volume) from audio file
    \"\"\"
    if not LIBROSA_AVAILABLE:
        return None, "librosa is not installed, so loudness analysis cannot be performed"

    try:
        print(f"🔊 Loudness extraction started: {audio_file_path}")

        # Load audio
        y, sr = librosa.load(audio_file_path, sr=None)
        print(f"   - Sample rate: {sr}Hz")
        print(f"   - Length: {len(y)/sr:.2f} seconds")

        # Calculate RMS energy
        hop_length = 512
        rms_energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]

        # Calculate time axis
        frame_times = librosa.frames_to_time(np.arange(len(rms_energy)), sr=sr, hop_length=hop_length)

        # Convert to dB (reference value: maximum RMS)
        max_rms = np.max(rms_energy)
        if max_rms > 0:
            loudness_db = 20 * np.log10(rms_energy / max_rms)
            # Below -60dB is treated as silence
            loudness_db = np.maximum(loudness_db, -60)
        else:
            loudness_db = np.full_like(rms_energy, -60)

        # Normalize to 0-1 range (-60dB ~ 0dB -> 0 ~ 1)
        loudness_normalized = (loudness_db + 60) / 60

        print(f"   - Extracted Loudness points: {len(loudness_normalized)}")
        print(f"   - RMS range: {np.min(rms_energy):.6f} ~ {np.max(rms_energy):.6f}")
        print(f"   - dB range: {np.min(loudness_db):.1f}dB ~ {np.max(loudness_db):.1f}dB")

        return {
            'times': frame_times,
            'rms_values': rms_energy,
            'loudness_db': loudness_db,
            'loudness_normalized': loudness_normalized,
            'sample_rate': sr,
            'duration': len(y) / sr,
            'hop_length': hop_length
        }, "Loudness extraction completed"

    except Exception as e:
        print(f"❌ Loudness extraction error: {e}")
        return None, f"Loudness extraction error: {str(e)}"

def extract_voicing_from_audio(audio_file_path, f0_method="pyin"):
    \"\"\"
    Extract voice/unvoice information from audio file
    \"\"\"
    if not LIBROSA_AVAILABLE:
        return None, "librosa is not installed, so voice/unvoice analysis cannot be performed"

    try:
        print(f"🗣️ Voice/Unvoice extraction started: {audio_file_path}")

        # Get voiced information from F0 analysis
        f0_data, f0_status = extract_f0_from_audio(audio_file_path, f0_method)

        if f0_data is None:
            return None, f"F0 analysis failed, so voice/unvoice extraction is not possible: {f0_status}"

        # Extract voiced information
        times = f0_data['times']
        voiced_flag = f0_data['voiced_flag']
        voiced_probs = f0_data['voiced_probs']

        print(f"   - Extracted Voice/Unvoice points: {len(voiced_flag)}")

        # voiced section statistics
        voiced_frames = np.sum(voiced_flag)
        voiced_ratio = voiced_frames / len(voiced_flag) if len(voiced_flag) > 0 else 0
        print(f"   - Voiced section: {voiced_frames} frames ({voiced_ratio:.1%})")
        print(f"   - Unvoiced section: {len(voiced_flag) - voiced_frames} frames ({1-voiced_ratio:.1%})")

        return {
            'times': times,
            'voiced_flag': voiced_flag,
            'voiced_probs': voiced_probs,
            'sample_rate': f0_data['sample_rate'],
            'duration': f0_data['duration'],
            'hop_length': f0_data['hop_length'],
            'voiced_ratio': voiced_ratio
        }, "Voice/Unvoice extraction completed"

    except Exception as e:
        print(f"❌ Voice/Unvoice extraction error: {e}")
        return None, f"Voice/Unvoice extraction error: {str(e)}"

def extract_audio_features(audio_file_path, f0_method="pyin", include_f0=True, include_loudness=True, include_voicing=True):
    \"\"\"
    Extract F0, loudness, and voice/unvoice from audio file
    \"\"\"
    if not LIBROSA_AVAILABLE:
        return None, "librosa is not installed, so audio feature analysis cannot be performed"

    features = {}
    status_messages = []

    try:
        print(f"🎵 Audio feature analysis started: {audio_file_path}")

        # Extract F0
        if include_f0:
            f0_data, f0_status = extract_f0_from_audio(audio_file_path, f0_method)
            if f0_data:
                features['f0'] = f0_data
                status_messages.append(f0_status)
            else:
                status_messages.append(f"F0 extraction failed: {f0_status}")

        # Extract Loudness
        if include_loudness:
            loudness_data, loudness_status = extract_loudness_from_audio(audio_file_path)
            if loudness_data:
                features['loudness'] = loudness_data
                status_messages.append(loudness_status)
            else:
                status_messages.append(f"Loudness extraction failed: {loudness_status}")

        # Extract Voice/Unvoice
        if include_voicing:
            voicing_data, voicing_status = extract_voicing_from_audio(audio_file_path, f0_method)
            if voicing_data:
                features['voicing'] = voicing_data
                status_messages.append(voicing_status)
            else:
                status_messages.append(f"Voice/Unvoice extraction failed: {voicing_status}")

        if features:
            # Add common information
            if 'f0' in features:
                features['duration'] = features['f0']['duration']
                features['sample_rate'] = features['f0']['sample_rate']
            elif 'loudness' in features:
                features['duration'] = features['loudness']['duration']
                features['sample_rate'] = features['loudness']['sample_rate']
            elif 'voicing' in features:
                features['duration'] = features['voicing']['duration']
                features['sample_rate'] = features['voicing']['sample_rate']

            return features, " | ".join(status_messages)
        else:
            return None, "All feature extraction failed"

    except Exception as e:
        print(f"❌ Audio feature analysis error: {e}")
        return None, f"Audio feature analysis error: {str(e)}"

def create_f0_line_data(f0_data, tempo=120, pixelsPerBeat=80):
    \"\"\"
    Convert F0 data to line_data format for LineLayer
    Ensure F0 curve is displayed at the exact pitch positions of the piano roll grid
    \"\"\"
    if not f0_data:
        return None

    try:
        times = f0_data['times']
        f0_values = f0_data['f0_values']

        # Piano roll constants (same as GridComponent)
        NOTE_HEIGHT = 20
        TOTAL_NOTES = 128

        def hz_to_midi(frequency):
            \"\"\"Convert frequency (Hz) to MIDI note number\"\"\"
            if frequency <= 0:
                return 0
            return 69 + 12 * np.log2(frequency / 440.0)

        def midi_to_y_coordinate(midi_note):
            \"\"\"Convert MIDI note number to piano roll Y coordinate (same as GridComponent)\"\"\"
            return (TOTAL_NOTES - 1 - midi_note) * NOTE_HEIGHT + NOTE_HEIGHT/2

        # Create data points (using piano roll coordinate system)
        data_points = []
        valid_f0_values = []

        for time, f0 in zip(times, f0_values):
            if not np.isnan(f0) and f0 > 0:
                # Convert Hz to MIDI
                midi_note = hz_to_midi(f0)

                # Check MIDI range (0-127)
                if 0 <= midi_note <= 127:
                    # Convert time (seconds) to pixel X coordinate
                    x_pixel = time * (tempo / 60) * pixelsPerBeat

                    # Convert MIDI to piano roll Y coordinate
                    y_pixel = midi_to_y_coordinate(midi_note)

                    data_points.append({
                        "x": float(x_pixel),
                        "y": float(y_pixel)
                    })
                    valid_f0_values.append(f0)

        if not data_points:
            print("⚠️ No valid F0 data points")
            return None

        # F0 value range information (for display)
        min_f0 = float(np.min(valid_f0_values))
        max_f0 = float(np.max(valid_f0_values))
        min_midi = hz_to_midi(min_f0)
        max_midi = hz_to_midi(max_f0)

        # Set Y range to full piano roll range
        y_min = 0
        y_max = TOTAL_NOTES * NOTE_HEIGHT

        line_data = {
            "f0_curve": {
                "color": "#FF6B6B",  # Red
                "lineWidth": 3,
                "yMin": y_min,
                "yMax": y_max,
                "position": "overlay",  # Overlay on grid
                "renderMode": "piano_grid",  # F0-specific rendering mode
                "visible": True,
                "opacity": 0.8,
                "data": data_points,
                # Metadata
                "dataType": "f0",
                "unit": "Hz",
                "originalRange": {
                    "minHz": min_f0,
                    "maxHz": max_f0,
                    "minMidi": min_midi,
                    "maxMidi": max_midi
                }
            }
        }

        print(f"📊 F0 LineData created: {len(data_points)} points")
        print(f"   - F0 range: {min_f0:.1f}Hz ~ {max_f0:.1f}Hz")
        print(f"   - MIDI range: {min_midi:.1f} ~ {max_midi:.1f}")
        print(f"   - Rendering mode: Piano roll grid alignment")

        return line_data

    except Exception as e:
        print(f"❌ F0 LineData creation error: {e}")
        return None

def create_loudness_line_data(loudness_data, tempo=120, pixelsPerBeat=80, y_min=None, y_max=None, use_db=True):
    \"\"\"
    Convert Loudness data to line_data format for LineLayer
    Has independent Y range and is displayed separately from the piano roll grid
    \"\"\"
    if not loudness_data:
        return None

    try:
        times = loudness_data['times']

        # Select loudness value to use (dB or normalized)
        if use_db:
            values = loudness_data['loudness_db']
            unit = "dB"
            default_y_min = -60
            default_y_max = 0
        else:
            values = loudness_data['loudness_normalized']
            unit = "normalized"
            default_y_min = 0
            default_y_max = 1

        # Set Y range
        actual_y_min = y_min if y_min is not None else default_y_min
        actual_y_max = y_max if y_max is not None else default_y_max
        y_range = actual_y_max - actual_y_min

        # Create data points
        data_points = []
        for time, value in zip(times, values):
            if not np.isnan(value):
                # Convert time (seconds) to pixel X coordinate
                x_pixel = time * (tempo / 60) * pixelsPerBeat

                # Convert Loudness value to 0-2560 pixel range (using full grid canvas height)
                normalized_value = (value - actual_y_min) / y_range
                y_pixel = normalized_value * 2560  # 0-2560 pixel range (128 notes * 20 pixels height)

                data_points.append({
                    "x": float(x_pixel),
                    "y": float(max(0, min(2560, y_pixel)))  # Range limit
                })

        if not data_points:
            print("⚠️ No valid Loudness data points")
            return None

        # Actual value range
        min_value = float(np.min(values))
        max_value = float(np.max(values))

        line_data = {
            "loudness_curve": {
                "color": "#4ECDC4",  # Cyan
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,  # Full grid canvas height (128 notes * 20 pixels)
                "position": "overlay",  # Display on entire area as overlay
                "renderMode": "independent_range",  # Independent Y range
                "visible": True,
                "opacity": 0.6,
                "data": data_points,
                # Metadata
                "dataType": "loudness",
                "unit": unit,
                "originalRange": {
                    "min": min_value,
                    "max": max_value,
                    "y_min": actual_y_min,
                    "y_max": actual_y_max
                }
            }
        }

        print(f"📊 Loudness LineData created: {len(data_points)} points")
        print(f"   - Loudness range: {min_value:.1f}{unit} ~ {max_value:.1f}{unit}")
        print(f"   - Y range: {actual_y_min} ~ {actual_y_max}")
        print(f"   - Rendering mode: Full grid canvas height (independent_range)")

        return line_data

    except Exception as e:
        print(f"❌ Loudness LineData creation error: {e}")
        return None

def create_voicing_line_data(voicing_data, tempo=120, pixelsPerBeat=80, use_probs=True):
    \"\"\"
    Convert Voice/Unvoice data to line_data format for LineLayer
    Has independent Y range and is displayed as 0(unvoiced) ~ 1(voiced) range
    \"\"\"
    if not voicing_data:
        return None

    try:
        times = voicing_data['times']

        # Select voicing value to use (probability or binary)
        if use_probs and 'voiced_probs' in voicing_data:
            values = voicing_data['voiced_probs']
            unit = "probability"
        else:
            values = voicing_data['voiced_flag'].astype(float)
            unit = "binary"

        # Create data points
        data_points = []
        for time, value in zip(times, values):
            if not np.isnan(value):
                # Convert time (seconds) to pixel X coordinate
                x_pixel = time * (tempo / 60) * pixelsPerBeat

                # Convert Voice/Unvoice value to 0-2560 pixel range (using full grid canvas height)
                y_pixel = value * 2560  # Convert 0-1 range to 0-2560 pixels

                data_points.append({
                    "x": float(x_pixel),
                    "y": float(max(0, min(2560, y_pixel)))  # Range limit
                })

        if not data_points:
            print("⚠️ No valid Voice/Unvoice data points")
            return None

        # Actual value range
        min_value = float(np.min(values))
        max_value = float(np.max(values))
        voiced_ratio = voicing_data.get('voiced_ratio', 0.0)

        line_data = {
            "voicing_curve": {
                "color": "#9B59B6",  # Purple
                "lineWidth": 2,
                "yMin": 0,
                "yMax": 2560,  # Full grid canvas height (128 notes * 20 pixels)
                "position": "overlay",  # Display on entire area as overlay
                "renderMode": "independent_range",  # Independent Y range
                "visible": True,
                "opacity": 0.6,
                "data": data_points,
                # Metadata
                "dataType": "voicing",
                "unit": unit,
                "originalRange": {
                    "min": min_value,
                    "max": max_value,
                    "voiced_ratio": voiced_ratio,
                    "y_min": 0,
                    "y_max": 1
                }
            }
        }

        print(f"📊 Voice/Unvoice LineData created: {len(data_points)} points")
        print(f"   - Voice/Unvoice range: {min_value:.3f} ~ {max_value:.3f} ({unit})")
        print(f"   - Voiced ratio: {voiced_ratio:.1%}")
        print(f"   - Rendering mode: Full grid canvas height (independent_range)")

        return line_data

    except Exception as e:
        print(f"❌ Voice/Unvoice LineData creation error: {e}")
        return None

def create_multi_feature_line_data(features, tempo=120, pixelsPerBeat=80,
                                   loudness_y_min=None, loudness_y_max=None,
                                   loudness_use_db=True, voicing_use_probs=True):
    \"\"\"
    Combine multiple audio features (F0, Loudness, Voice/Unvoice) into a single line_data
    \"\"\"
    combined_line_data = {}

    try:
        # Add F0 curve
        if 'f0' in features:
            f0_line_data = create_f0_line_data(features['f0'], tempo, pixelsPerBeat)
            if f0_line_data:
                combined_line_data.update(f0_line_data)

        # Add Loudness curve
        if 'loudness' in features:
            loudness_line_data = create_loudness_line_data(
                features['loudness'], tempo, pixelsPerBeat,
                loudness_y_min, loudness_y_max, loudness_use_db
            )
            if loudness_line_data:
                combined_line_data.update(loudness_line_data)

        # Add Voice/Unvoice curve
        if 'voicing' in features:
            voicing_line_data = create_voicing_line_data(
                features['voicing'], tempo, pixelsPerBeat, voicing_use_probs
            )
            if voicing_line_data:
                combined_line_data.update(voicing_line_data)

        if combined_line_data:
            print(f"📊 Combined LineData created: {len(combined_line_data)} curves")
            return combined_line_data
        else:
            print("⚠️ No curves data created")
            return None

    except Exception as e:
        print(f"❌ Combined LineData creation error: {e}")
        return None

def synthesize_and_analyze_features(piano_roll, attack, decay, sustain, release, wave_type='complex',
                                  include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin",
                                  loudness_y_min=None, loudness_y_max=None, loudness_use_db=True, voicing_use_probs=True):
    \"\"\"
    Synthesize audio from piano roll, analyze F0, loudness, and voice/unvoice from synthesized audio, and visualize the results
    \"\"\"
    print("=== Synthesize and Analyze Features ===")
    print(f"ADSR: A={attack}, D={decay}, S={sustain}, R={release}")
    print(f"Wave Type: {wave_type}")
    print(f"Include F0: {include_f0}, Include Loudness: {include_loudness}, Include Voicing: {include_voicing}")

    # First synthesize audio
    audio_data = synthesize_audio(piano_roll, attack, decay, sustain, release, wave_type)

    if audio_data is None:
        return piano_roll, "Audio synthesis failed", None

    # Create temporary WAV file
    temp_audio_path = create_temp_wav_file(audio_data, SAMPLE_RATE)
    if temp_audio_path is None:
        return piano_roll, "Failed to create temporary audio file", None

    try:
        # Analyze audio features
        features, analysis_status = extract_audio_features(
            temp_audio_path, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"Audio feature analysis failed: {analysis_status}", temp_audio_path

        # Update piano roll
        updated_piano_roll = piano_roll.copy() if piano_roll else {}

        # Add backend audio data
        audio_base64 = audio_to_base64_wav(audio_data, SAMPLE_RATE)
        updated_piano_roll['audio_data'] = audio_base64
        updated_piano_roll['use_backend_audio'] = True

        # Add tempo and pixels per beat information
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        # Calculate waveform data (for backend audio)
        waveform_data = calculate_waveform_data(audio_data, pixels_per_beat, tempo)

        # Create curve data (audio feature analysis results)
        line_data = create_multi_feature_line_data(
            features, tempo, pixels_per_beat,
            loudness_y_min, loudness_y_max, loudness_use_db, voicing_use_probs
        )

        # Set combined curve data (audio features + waveform)
        curve_data = {}

        # Add audio feature curves
        if line_data:
            curve_data.update(line_data)

        # Add waveform data
        if waveform_data:
            curve_data['waveform_data'] = waveform_data
            print(f"Waveform data created: {len(waveform_data)} points")

        # Set curve data for piano roll
        if curve_data:
            updated_piano_roll['curve_data'] = curve_data

        # Set line_data separately (for LineLayer)
        if line_data:
            updated_piano_roll['line_data'] = line_data

        print(f"🔊 [synthesize_and_analyze_features] Setting backend audio data:")
        print(f"   - audio_data length: {len(audio_base64) if audio_base64 else 0}")
        print(f"   - use_backend_audio: {updated_piano_roll['use_backend_audio']}")
        print(f"   - waveform points: {len(waveform_data) if waveform_data else 0}")
        print(f"   - feature curves: {len(line_data) if line_data else 0}")

        # Create status message
        status_parts = [f"Audio synthesis completed ({wave_type} waveform)", analysis_status]

        if waveform_data:
            status_parts.append(f"Waveform visualization completed ({len(waveform_data)} points)")

        if line_data:
            curve_count = len(line_data)
            status_parts.append(f"{curve_count} feature curves visualization completed")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, temp_audio_path

    except Exception as e:
        error_message = f"Error during feature analysis: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, temp_audio_path
    # Temporary file is cleaned up after use (gradio automatically manages)

def analyze_uploaded_audio_features(piano_roll, audio_file, include_f0=True, include_loudness=True, include_voicing=True,
                                  f0_method="pyin", loudness_y_min=None, loudness_y_max=None,
                                  loudness_use_db=True, voicing_use_probs=True):
    \"\"\"
    Analyze F0, loudness, and voice/unvoice from uploaded audio file and display on piano roll
    \"\"\"
    print("=== Analyze Uploaded Audio Features ===")
    print(f"Audio file: {audio_file}")
    print(f"Include F0: {include_f0}, Include Loudness: {include_loudness}, Include Voicing: {include_voicing}")

    if not audio_file:
        return piano_roll, "Please upload an audio file.", None

    if not LIBROSA_AVAILABLE:
        return piano_roll, "librosa is not installed, so audio feature analysis cannot be performed. Please install it with 'pip install librosa'.", None

    try:
        # Analyze audio features
        features, analysis_status = extract_audio_features(
            audio_file, f0_method, include_f0, include_loudness, include_voicing
        )

        if features is None:
            return piano_roll, f"Audio feature analysis failed: {analysis_status}", audio_file

        # Update piano roll data
        updated_piano_roll = piano_roll.copy() if piano_roll else {
            "notes": [],
            "tempo": 120,
            "timeSignature": {"numerator": 4, "denominator": 4},
            "editMode": "select",
            "snapSetting": "1/4",
            "pixelsPerBeat": 80
        }

        # Create curve data
        tempo = updated_piano_roll.get('tempo', 120)
        pixels_per_beat = updated_piano_roll.get('pixelsPerBeat', 80)

        line_data = create_multi_feature_line_data(
            features, tempo, pixels_per_beat,
            loudness_y_min, loudness_y_max, loudness_use_db, voicing_use_probs
        )

        if line_data:
            updated_piano_roll['line_data'] = line_data

        # Create status message
        status_parts = [analysis_status]

        if line_data:
            curve_count = len(line_data)
            curve_types = list(line_data.keys())
            status_parts.append(f"{curve_count} curves ({', '.join(curve_types)}) visualization completed")

            # Add range information for each feature
            for curve_name, curve_info in line_data.items():
                if 'originalRange' in curve_info:
                    range_info = curve_info['originalRange']
                    if 'minHz' in range_info:  # F0
                        status_parts.append(f"F0: {range_info['minHz']:.1f}~{range_info['maxHz']:.1f}Hz")
                    elif 'min' in range_info and 'voiced_ratio' not in range_info:  # Loudness
                        unit = curve_info.get('unit', '')
                        status_parts.append(f"Loudness: {range_info['min']:.1f}~{range_info['max']:.1f}{unit}")
                    elif 'voiced_ratio' in range_info:  # Voice/Unvoice
                        unit = curve_info.get('unit', '')
                        voiced_ratio = range_info['voiced_ratio']
                        status_parts.append(f"Voicing: {voiced_ratio:.1%} voiced ({unit})")

        duration = features.get('duration', 0)
        status_parts.append(f"⏱️ {duration:.2f} seconds")

        status_message = " | ".join(status_parts)

        return updated_piano_roll, status_message, audio_file

    except Exception as e:
        error_message = f"Error during uploaded audio analysis: {str(e)}"
        print(f"❌ {error_message}")
        return piano_roll, error_message, audio_file

def analyze_audio_f0(piano_roll, audio_file, f0_method="pyin"):
    \"\"\"
    Extract F0 from uploaded audio file and display on piano roll (for backward compatibility)
    \"\"\"
    return analyze_uploaded_audio_features(
        piano_roll, audio_file, include_f0=True, include_loudness=False, include_voicing=False, f0_method=f0_method
    )

def generate_f0_demo_audio():
    \"\"\"
    Create a simple audio for F0 analysis demo
    \"\"\"
    print("🎵 Creating F0 analysis demo audio...")

    # Create a simple sawtooth tone (100Hz to 400Hz)
    duration = 3.0  # 3 seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # Create a sine wave with frequency changing over time (100Hz -> 400Hz)
    start_freq = 100
    end_freq = 400
    instantaneous_freq = start_freq + (end_freq - start_freq) * (t / duration)

    # Create a frequency-modulated sine wave
    phase = 2 * np.pi * np.cumsum(instantaneous_freq) / sample_rate
    audio = 0.3 * np.sin(phase)  # Volume adjustment

    # Save as WAV file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Convert to 16-bit PCM
            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ Demo audio created: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ Failed to create demo audio: {e}")
        return None

def generate_feature_demo_audio():
    \"\"\"
    Create an audio with various features for audio feature analysis demo
    Includes F0 and loudness changes
    \"\"\"
    print("🎵 Creating audio with various features for audio feature analysis demo...")

    duration = 4.0  # 4 seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)

    # Create audio with different features for each section
    audio = np.zeros_like(t)

    # Section 1 (0-1 second): C4 to C5 + volume increase
    mask1 = (t >= 0) & (t < 1)
    t1 = t[mask1]
    f1_start, f1_end = 261.63, 523.25  # C4 to C5
    freq1 = f1_start + (f1_end - f1_start) * (t1 / 1.0)
    phase1 = 2 * np.pi * np.cumsum(freq1) / sample_rate
    vol1 = 0.1 + 0.4 * (t1 / 1.0)  # Increase from 0.1 to 0.5
    audio[mask1] = vol1 * np.sin(phase1)

    # Section 2 (1-2 seconds): C5 to G4 + constant volume
    mask2 = (t >= 1) & (t < 2)
    t2 = t[mask2] - 1
    f2_start, f2_end = 523.25, 392.00  # C5 to G4
    freq2 = f2_start + (f2_end - f2_start) * (t2 / 1.0)
    phase2 = 2 * np.pi * np.cumsum(freq2) / sample_rate
    audio[mask2] = 0.5 * np.sin(phase2)

    # Section 3 (2-3 seconds): A4 fixed + volume decrease (tremolo effect)
    mask3 = (t >= 2) & (t < 3)
    t3 = t[mask3] - 2
    freq3 = 440.0  # A4 fixed
    phase3 = 2 * np.pi * freq3 * t3
    vol3 = 0.5 * (1 - t3 / 1.0) * (1 + 0.3 * np.sin(2 * np.pi * 6 * t3))  # Tremolo
    audio[mask3] = vol3 * np.sin(phase3)

    # Section 4 (3-4 seconds): Complex sound (A4 + E5) + fade out
    mask4 = (t >= 3) & (t < 4)
    t4 = t[mask4] - 3
    freq4a, freq4b = 440.0, 659.25  # A4 + E5
    phase4a = 2 * np.pi * freq4a * t4
    phase4b = 2 * np.pi * freq4b * t4
    vol4 = 0.4 * (1 - t4 / 1.0)  # Fade out
    audio[mask4] = vol4 * (0.6 * np.sin(phase4a) + 0.4 * np.sin(phase4b))

    # Save as WAV file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
    try:
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Convert to 16-bit PCM
            audio_16bit = (audio * 32767).astype(np.int16)
            wav_file.writeframes(audio_16bit.tobytes())

        os.close(temp_fd)
        print(f"✅ Audio feature analysis demo audio generated: {temp_path}")
        return temp_path

    except Exception as e:
        os.close(temp_fd)
        print(f"❌ Failed to generate audio feature analysis demo audio: {e}")
        return None

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")

    with gr.Tabs():
        # First tab: Basic demo
        with gr.TabItem("🎼 Basic Demo"):
            gr.Markdown("## Basic PianoRoll Demo")

            with gr.Row():
                with gr.Column():
                    # Set initial value
                    initial_value_basic = {
                        "notes": [
                            {
                                "start": 80,
                                "duration": 80,
                                "pitch": 60,
                                "velocity": 100,
                                "lyric": "안녕"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 64,
                                "velocity": 90,
                                "lyric": "하세요"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_basic = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_basic,
                        elem_id="piano_roll_basic",  # Unique ID
                        use_backend_audio=False  # Use frontend audio engine
                    )

            with gr.Row():
                with gr.Column():
                    output_json_basic = gr.JSON()

            with gr.Row():
                with gr.Column():
                    btn_basic = gr.Button("🔄 Convert & Debug", variant="primary")

            # Basic tab events
            btn_basic.click(
                fn=convert_basic,
                inputs=piano_roll_basic,
                outputs=output_json_basic,
                show_progress=True
            )

        # Second tab: Synthesizer demo
        with gr.TabItem("🎵 Synthesizer Demo"):
            gr.Markdown("## 🎹 PianoRoll with Synthesizer Demo")
            gr.Markdown("Edit notes and click '🎶 Synthesize Audio' to generate audio and play it!")

            with gr.Row():
                with gr.Column(scale=3):
                    # Synthesizer initial value
                    initial_value_synth = {
                        "notes": [
                            {
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "도"
                            },
                            {
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "레"
                            },
                            {
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "미"
                            },
                            {
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "파"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "curve_data": {},  # Initial empty curve data
                        "use_backend_audio": False  # Initially disable backend audio
                    }
                    piano_roll_synth = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_synth,
                        elem_id="piano_roll_synth",  # Unique ID
                        use_backend_audio=False  # Initially use frontend engine, switch to backend for synthesize
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ ADSR Settings")
                    attack_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.01,
                        step=0.001,
                        label="Attack (seconds)"
                    )
                    decay_slider = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.1,
                        step=0.001,
                        label="Decay (seconds)"
                    )
                    sustain_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.01,
                        label="Sustain (level)"
                    )
                    release_slider = gr.Slider(
                        minimum=0.001,
                        maximum=2.0,
                        value=0.3,
                        step=0.001,
                        label="Release (seconds)"
                    )

                    gr.Markdown("### 🎵 Waveform Settings")
                    wave_type_dropdown = gr.Dropdown(
                        choices=[
                            ("Complex Waveform (Complex)", "complex"),
                            ("Harmonic Synthesis (Harmonic)", "harmonic"),
                            ("FM Synthesis (FM)", "fm"),
                            ("Sawtooth Wave (Sawtooth)", "sawtooth"),
                            ("Square Wave (Square)", "square"),
                            ("Triangle Wave (Triangle)", "triangle"),
                            ("Sine Wave (Sine)", "sine")
                        ],
                        value="complex",
                        label="Waveform Type",
                        info="Each note uses different waveforms cyclically"
                    )

            with gr.Row():
                with gr.Column():
                    btn_synthesize = gr.Button("🎶 Synthesize Audio", variant="primary", size="lg")
                    status_text = gr.Textbox(label="Status", interactive=False)

            with gr.Row():
                with gr.Column():
                    btn_regenerate = gr.Button("🔄 Regenerate Waveform", variant="secondary", size="lg")

            # Add gradio Audio component for comparison
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔊 Gradio Audio Comparison")
                    gradio_audio_output = gr.Audio(
                        label="Backend-generated audio (comparison)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_synth = gr.JSON(label="Result Data")

            # Synthesizer tab events
            btn_synthesize.click(
                fn=synthesize_and_play,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # Waveform regeneration button event
            btn_regenerate.click(
                fn=clear_and_regenerate_waveform,
                inputs=[
                    piano_roll_synth,
                    attack_slider,
                    decay_slider,
                    sustain_slider,
                    release_slider,
                    wave_type_dropdown
                ],
                outputs=[piano_roll_synth, status_text, gradio_audio_output],
                show_progress=True
            )

            # Event listener settings
            def log_play_event(event_data=None):
                print("🎵 Play event triggered:", event_data)
                return f"Play started: {event_data if event_data else 'Playing'}"

            def log_pause_event(event_data=None):
                print("⏸️ Pause event triggered:", event_data)
                return f"Paused: {event_data if event_data else 'Paused'}"

            def log_stop_event(event_data=None):
                print("⏹️ Stop event triggered:", event_data)
                return f"Stopped: {event_data if event_data else 'Stopped'}"

            piano_roll_synth.play(log_play_event, outputs=status_text)
            piano_roll_synth.pause(log_pause_event, outputs=status_text)
            piano_roll_synth.stop(log_stop_event, outputs=status_text)

            # Add input event processing (G2P processing)
            def handle_synth_input(lyric_data):
                print("🎵 Synthesizer tab - Input event triggered:", lyric_data)
                return f"Lyric input detected: {lyric_data if lyric_data else 'Input detected'}"

            piano_roll_synth.input(handle_synth_input, outputs=status_text)

            # Update JSON output when note changes
            piano_roll_synth.change(lambda x: x, inputs=piano_roll_synth, outputs=output_json_synth)

        # Third tab: Phoneme demo
        with gr.TabItem("🗣️ Phoneme Demo"):
            gr.Markdown("## 📢 Phoneme Feature Demo")
            gr.Markdown("When you modify lyrics, G2P (Grapheme-to-Phoneme) is automatically executed to display phonemes. You can also manually edit phonemes.")

            with gr.Row():
                with gr.Column(scale=3):
                    # Phoneme initial value
                    initial_value_phoneme = {
                        "notes": [
                            {
                                "id": "note_0",
                                "start": 0,
                                "duration": 160,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "안녕",
                                "phoneme": "aa n ny eo ng"  # Pre-set phoneme
                            },
                            {
                                "id": "note_1",
                                "start": 160,
                                "duration": 160,
                                "pitch": 62,  # D4
                                "velocity": 100,
                                "lyric": "하세요",
                                "phoneme": "h a s e y o"
                            },
                            {
                                "id": "note_2",
                                "start": 320,
                                "duration": 160,
                                "pitch": 64,  # E4
                                "velocity": 100,
                                "lyric": "음악",
                                "phoneme": "eu m a k"
                            },
                            {
                                "id": "note_3",
                                "start": 480,
                                "duration": 160,
                                "pitch": 65,  # F4
                                "velocity": 100,
                                "lyric": "피아노"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4"
                    }
                    piano_roll_phoneme = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_phoneme,
                        elem_id="piano_roll_phoneme",  # Unique ID
                        use_backend_audio=False  # Use frontend audio engine
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Phoneme Mapping Management")

                    # Display current mapping list
                    phoneme_mapping_dataframe = gr.Dataframe(
                        headers=["Lyric", "Phoneme"],
                        datatype=["str", "str"],
                        value=get_phoneme_mapping_for_dataframe(),
                        label="Current Phoneme Mapping",
                        interactive=True,
                        wrap=True
                    )

                    gr.Markdown("#### ➕ Add New Mapping")
                    with gr.Row():
                        add_lyric_input = gr.Textbox(
                            label="Lyric",
                            placeholder="Example: 라",
                            scale=1
                        )
                        add_phoneme_input = gr.Textbox(
                            label="Phoneme",
                            placeholder="Example: l aa",
                            scale=1
                        )
                    btn_add_mapping = gr.Button("➕ Add Mapping", variant="primary", size="sm")

                    gr.Markdown("### 🔧 Batch Operations")
                    with gr.Row():
                        btn_auto_generate = gr.Button("🤖 Auto-generate All Phonemes", variant="primary")
                        btn_clear_phonemes = gr.Button("🗑️ Clear All Phonemes", variant="secondary")

                    btn_reset_mapping = gr.Button("🔄 Reset Mapping to Default", variant="secondary")

            with gr.Row():
                with gr.Column():
                    phoneme_status_text = gr.Textbox(label="Status", interactive=False)

            with gr.Row():
                with gr.Column():
                    output_json_phoneme = gr.JSON(label="Phoneme Data")

            # Phoneme tab event processing

            # Add mapping
            btn_add_mapping.click(
                fn=add_phoneme_mapping,
                inputs=[add_lyric_input, add_phoneme_input],
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            ).then(
                fn=lambda: ["", ""],  # Reset input fields
                outputs=[add_lyric_input, add_phoneme_input]
            )

            # Reset
            btn_reset_mapping.click(
                fn=reset_phoneme_mapping,
                outputs=[phoneme_mapping_dataframe, phoneme_status_text],
                show_progress=False
            )

            # Automatic G2P processing when lyric is input
            def handle_phoneme_input_event(piano_roll_data):
                \"\"\"Process lyric input event - detect piano roll changes and generate phoneme\"\"\"
                print("🗣️ Phoneme tab - Input event triggered")
                print(f"   - Piano roll data: {type(piano_roll_data)}")

                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "Piano roll data is missing."

                return auto_generate_missing_phonemes(piano_roll_data)

            def auto_generate_missing_phonemes(piano_roll_data):
                \"\"\"Automatically generate phoneme for notes with lyrics but no phoneme\"\"\"
                if not piano_roll_data or 'notes' not in piano_roll_data:
                    return piano_roll_data, "Piano roll data is missing."

                # Copy current notes
                notes = piano_roll_data['notes'].copy()
                updated_notes = []
                changes_made = 0

                for note in notes:
                    note_copy = note.copy()

                    # Process if lyric exists
                    lyric = note.get('lyric', '').strip()
                    current_phoneme = note.get('phoneme', '').strip()

                    if lyric:
                        # Run G2P to create new phoneme
                        new_phoneme = mock_g2p(lyric)

                        # Update if different from existing phoneme or missing
                        if not current_phoneme or current_phoneme != new_phoneme:
                            note_copy['phoneme'] = new_phoneme
                            changes_made += 1
                            print(f"   - G2P applied: '{lyric}' -> '{new_phoneme}'")
                    else:
                        # Remove phoneme if lyric is missing
                        if current_phoneme:
                            note_copy['phoneme'] = None
                            changes_made += 1
                            print(f"   - Phoneme removed (no lyric)")

                    updated_notes.append(note_copy)

                if changes_made > 0:
                    # Return updated piano roll data
                    updated_piano_roll = piano_roll_data.copy()
                    updated_piano_roll['notes'] = updated_notes
                    return updated_piano_roll, f"Automatic G2P completed: {changes_made} notes updated"
                else:
                    return piano_roll_data, "No changes to apply G2P."

            piano_roll_phoneme.input(
                fn=handle_phoneme_input_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # Automatic phoneme generation when note changes
            def handle_phoneme_change_event(piano_roll_data):
                \"\"\"Handle automatic phoneme generation when note changes\"\"\"
                return auto_generate_missing_phonemes(piano_roll_data)

            piano_roll_phoneme.change(
                fn=handle_phoneme_change_event,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # Automatic phoneme generation (manual button)
            btn_auto_generate.click(
                fn=auto_generate_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=True
            )

            # Clear all phonemes
            btn_clear_phonemes.click(
                fn=clear_all_phonemes,
                inputs=[piano_roll_phoneme],
                outputs=[piano_roll_phoneme, phoneme_status_text],
                show_progress=False
            )

            # Update JSON output when note changes (separate from automatic phoneme processing)
            def update_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_phoneme.change(
                fn=update_json_output,
                inputs=[piano_roll_phoneme],
                outputs=[output_json_phoneme],
                show_progress=False
            )

            # Log play event
            def log_phoneme_play_event(event_data=None):
                print("🗣️ Phoneme Play event triggered:", event_data)
                return f"Play started: {event_data if event_data else 'Playing'}"

            def log_phoneme_pause_event(event_data=None):
                print("🗣️ Phoneme Pause event triggered:", event_data)
                return f"Paused: {event_data if event_data else 'Paused'}"

            def log_phoneme_stop_event(event_data=None):
                print("🗣️ Phoneme Stop event triggered:", event_data)
                return f"Stopped: {event_data if event_data else 'Stopped'}"

            piano_roll_phoneme.play(log_phoneme_play_event, outputs=phoneme_status_text)
            piano_roll_phoneme.pause(log_phoneme_pause_event, outputs=phoneme_status_text)
            piano_roll_phoneme.stop(log_phoneme_stop_event, outputs=phoneme_status_text)

        # Fourth tab: F0 analysis demo
        with gr.TabItem("📊 F0 Analysis Demo"):
            gr.Markdown("## 🎵 F0 (Fundamental Frequency) Analysis Demo")
            if LIBROSA_AVAILABLE:
                gr.Markdown("Upload an audio file and extract F0 to visualize in PianoRoll!")
            else:
                gr.Markdown("⚠️ **librosa is not installed**: Run `pip install librosa` to install it.")

            with gr.Row():
                with gr.Column(scale=3):
                    # F0 initial value (empty piano roll)
                    initial_value_f0 = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }
                    piano_roll_f0 = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_f0,
                        elem_id="piano_roll_f0",  # Unique ID
                        use_backend_audio=False  # Use frontend audio engine
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### 🎤 Upload Audio")

                    audio_input = gr.Audio(
                        label="Audio file to analyze",
                        type="filepath",
                        interactive=True
                    )

                    gr.Markdown("### ⚙️ F0 Extraction Settings")
                    f0_method_dropdown = gr.Dropdown(
                        choices=[
                            ("PYIN (accurate, slow)", "pyin"),
                            ("PipTrack (fast, less accurate)", "piptrack")
                        ],
                        value="pyin",
                        label="F0 Extraction Method"
                    )
                    gr.Markdown("💡 **PYIN** is more accurate but takes longer to process.")

                    btn_analyze_f0 = gr.Button(
                        "🔬 Start F0 Analysis",
                        variant="primary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

                    btn_generate_demo = gr.Button(
                        "🎵 Generate Demo Audio",
                        variant="secondary"
                    )
                    gr.Markdown("📄 Generate a test audio with F0 changing over time.")

                    if not LIBROSA_AVAILABLE:
                        gr.Markdown("⚠️ librosa is required")

            with gr.Row():
                with gr.Column():
                    f0_status_text = gr.Textbox(
                        label="Analysis Status",
                        interactive=False,
                        lines=6
                    )

            with gr.Row():
                with gr.Column():
                    # Reference audio playback
                    reference_audio = gr.Audio(
                        label="Original Audio (reference)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_f0 = gr.JSON(label="F0 Analysis Result")

            # F0 tab event processing

            # F0 analysis button
            btn_analyze_f0.click(
                fn=analyze_audio_f0,
                inputs=[piano_roll_f0, audio_input, f0_method_dropdown],
                outputs=[piano_roll_f0, f0_status_text, reference_audio],
                show_progress=True
            )

            # Demo audio generation button
            def create_and_analyze_demo():
                \"\"\"Create demo audio and automatically analyze F0.\"\"\"
                demo_audio_path = generate_f0_demo_audio()
                if demo_audio_path:
                    # Initial piano roll data
                    initial_piano_roll = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }

                    # Perform F0 analysis
                    updated_piano_roll, status, _ = analyze_audio_f0(initial_piano_roll, demo_audio_path, "pyin")

                    return updated_piano_roll, status, demo_audio_path, demo_audio_path
                else:
                    return initial_value_f0, "Failed to generate demo audio.", None, None

            btn_generate_demo.click(
                fn=create_and_analyze_demo,
                outputs=[piano_roll_f0, f0_status_text, audio_input, reference_audio],
                show_progress=True
            )

            # Update JSON output when note changes
            def update_f0_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_f0.change(
                fn=update_f0_json_output,
                inputs=[piano_roll_f0],
                outputs=[output_json_f0],
                show_progress=False
            )

            # Log play event
            def log_f0_play_event(event_data=None):
                print("📊 F0 Play event triggered:", event_data)
                return f"Play started: {event_data if event_data else 'Playing'}"

            def log_f0_pause_event(event_data=None):
                print("📊 F0 Pause event triggered:", event_data)
                return f"Paused: {event_data if event_data else 'Paused'}"

            def log_f0_stop_event(event_data=None):
                print("📊 F0 Stop event triggered:", event_data)
                return f"Stopped: {event_data if event_data else 'Stopped'}"

            piano_roll_f0.play(log_f0_play_event, outputs=f0_status_text)
            piano_roll_f0.pause(log_f0_pause_event, outputs=f0_status_text)
            piano_roll_f0.stop(log_f0_stop_event, outputs=f0_status_text)

        # Fifth tab: Audio feature analysis demo
        with gr.TabItem("🔊 Audio Feature Analysis"):
            gr.Markdown("## 🎵 Audio Feature Analysis Demo")
            if LIBROSA_AVAILABLE:
                gr.Markdown("Create audio from PianoRoll notes and analyze F0 and loudness, or upload your own audio for analysis!")
            else:
                gr.Markdown("⚠️ **librosa is not installed**: Run `pip install librosa` to install it.")

            with gr.Row():
                with gr.Column(scale=3):
                    # Audio feature analysis initial value
                    initial_value_features = {
                        "notes": [
                            {
                                "start": 0,
                                "duration": 320,
                                "pitch": 60,  # C4
                                "velocity": 100,
                                "lyric": "도"
                            },
                            {
                                "start": 320,
                                "duration": 320,
                                "pitch": 64,  # E4
                                "velocity": 90,
                                "lyric": "미"
                            },
                            {
                                "start": 640,
                                "duration": 320,
                                "pitch": 67,  # G4
                                "velocity": 95,
                                "lyric": "솔"
                            }
                        ],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }
                    piano_roll_features = PianoRoll(
                        height=600,
                        width=1000,
                        value=initial_value_features,
                        elem_id="piano_roll_features",  # Unique ID
                        use_backend_audio=True  # Use backend audio engine
                    )
            with gr.Row():
                with gr.Column():
                    btn_analyze_generated = gr.Button(
                        "🎶 Create Audio from Notes & Analyze",
                        variant="primary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

            with gr.Row():
                with gr.Column():
                    btn_analyze_uploaded = gr.Button(
                        "📤 Analyze Uploaded Audio",
                        variant="secondary",
                        size="lg",
                        interactive=LIBROSA_AVAILABLE
                    )

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎛️ Synthesizer Settings")

                    # ADSR settings
                    attack_features = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.01,
                        step=0.001,
                        label="Attack (seconds)"
                    )
                    decay_features = gr.Slider(
                        minimum=0.001,
                        maximum=1.0,
                        value=0.1,
                        step=0.001,
                        label="Decay (seconds)"
                    )
                    sustain_features = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.01,
                        label="Sustain (level)"
                    )
                    release_features = gr.Slider(
                        minimum=0.001,
                        maximum=2.0,
                        value=0.3,
                        step=0.001,
                        label="Release (seconds)"
                    )

                    # Waveform settings
                    wave_type_features = gr.Dropdown(
                        choices=[
                            ("Complex", "complex"),
                            ("Harmonic", "harmonic"),
                            ("FM", "fm"),
                            ("Sawtooth", "sawtooth"),
                            ("Square", "square"),
                            ("Triangle", "triangle"),
                            ("Sine", "sine")
                        ],
                        value="complex",
                        label="Waveform Type"
                    )
                with gr.Column():
                    gr.Markdown("### 📊 Analysis Settings")

                    # Select features to analyze
                    include_f0_features = gr.Checkbox(
                        label="F0 (fundamental frequency) analysis",
                        value=True
                    )
                    include_loudness_features = gr.Checkbox(
                        label="Loudness (loudness) analysis",
                        value=True
                    )
                    include_voicing_features = gr.Checkbox(
                        label="Voice/Unvoice (voiced/unvoiced) analysis",
                        value=True
                    )

                    # F0 analysis method
                    f0_method_features = gr.Dropdown(
                        choices=[
                            ("PYIN (accurate, slow)", "pyin"),
                            ("PipTrack (fast, less accurate)", "piptrack")
                        ],
                        value="pyin",
                        label="F0 Extraction Method"
                    )

                    # Loudness settings
                    loudness_use_db_features = gr.Checkbox(
                        label="Display Loudness in dB",
                        value=True
                    )
                    with gr.Row():
                        loudness_y_min_features = gr.Number(
                            label="Loudness minimum value (auto if empty)",
                            value=None
                        )
                        loudness_y_max_features = gr.Number(
                            label="Loudness maximum value (auto if empty)",
                            value=None
                        )

                    # Voice/Unvoice settings
                    voicing_use_probs_features = gr.Checkbox(
                        label="Display Voice/Unvoice as probabilities",
                        value=True,
                        info="Unchecked: Display as binary (0/1)"
                    )
                with gr.Column():
                    gr.Markdown("### 🎤 Upload Audio")
                    audio_upload_features = gr.Audio(
                        label="Audio file to analyze",
                        type="filepath",
                        interactive=True
                    )

                    btn_generate_feature_demo = gr.Button(
                        "🎵 Generate Demo Audio for Feature Analysis",
                        variant="secondary"
                    )
                    gr.Markdown("📄 Generate a test audio with F0 and loudness changing over time.")

            with gr.Row():
                with gr.Column():
                    features_status_text = gr.Textbox(
                        label="Analysis Status",
                        interactive=False,
                        lines=4
                    )

            with gr.Row():
                with gr.Column():
                    # Reference audio playback
                    reference_audio_features = gr.Audio(
                        label="Analyzed Audio (reference)",
                        type="filepath",
                        interactive=False
                    )

            with gr.Row():
                with gr.Column():
                    output_json_features = gr.JSON(label="Audio Feature Analysis Result")

            # Audio feature analysis tab event processing

            # Analyze generated audio button
            btn_analyze_generated.click(
                fn=synthesize_and_analyze_features,
                inputs=[
                    piano_roll_features,
                    attack_features,
                    decay_features,
                    sustain_features,
                    release_features,
                    wave_type_features,
                    include_f0_features,
                    include_loudness_features,
                    include_voicing_features,
                    f0_method_features,
                    loudness_y_min_features,
                    loudness_y_max_features,
                    loudness_use_db_features,
                    voicing_use_probs_features
                ],
                outputs=[piano_roll_features, features_status_text, reference_audio_features],
                show_progress=True
            )

            # Analyze uploaded audio button
            btn_analyze_uploaded.click(
                fn=analyze_uploaded_audio_features,
                inputs=[
                    piano_roll_features,
                    audio_upload_features,
                    include_f0_features,
                    include_loudness_features,
                    include_voicing_features,
                    f0_method_features,
                    loudness_y_min_features,
                    loudness_y_max_features,
                    loudness_use_db_features,
                    voicing_use_probs_features
                ],
                outputs=[piano_roll_features, features_status_text, reference_audio_features],
                show_progress=True
            )

            # Generate demo audio and analyze button
            def create_and_analyze_feature_demo():
                \"\"\"Generate demo audio for feature analysis and automatically analyze it.\"\"\"
                demo_audio_path = generate_feature_demo_audio()
                if demo_audio_path:
                    # Initial piano roll data
                    initial_piano_roll = {
                        "notes": [],
                        "tempo": 120,
                        "timeSignature": {"numerator": 4, "denominator": 4},
                        "editMode": "select",
                        "snapSetting": "1/4",
                        "pixelsPerBeat": 80
                    }

                    # Perform audio feature analysis (F0, loudness, voice/unvoice)
                    updated_piano_roll, status, _ = analyze_uploaded_audio_features(
                        initial_piano_roll, demo_audio_path,
                        include_f0=True, include_loudness=True, include_voicing=True, f0_method="pyin",
                        loudness_y_min=None, loudness_y_max=None, loudness_use_db=True, voicing_use_probs=True
                    )

                    return updated_piano_roll, status, demo_audio_path, demo_audio_path
                else:
                    return initial_value_features, "Failed to generate demo audio.", None, None

            btn_generate_feature_demo.click(
                fn=create_and_analyze_feature_demo,
                outputs=[piano_roll_features, features_status_text, audio_upload_features, reference_audio_features],
                show_progress=True
            )

            # Update JSON output when note changes
            def update_features_json_output(piano_roll_data):
                return piano_roll_data

            piano_roll_features.change(
                fn=update_features_json_output,
                inputs=[piano_roll_features],
                outputs=[output_json_features],
                show_progress=False
            )

            # Log play event
            def log_features_play_event(event_data=None):
                print("🔊 Features Play event triggered:", event_data)
                return f"Play started: {event_data if event_data else 'Playing'}"

            def log_features_pause_event(event_data=None):
                print("🔊 Features Pause event triggered:", event_data)
                return f"Paused: {event_data if event_data else 'Paused'}"

            def log_features_stop_event(event_data=None):
                print("🔊 Features Stop event triggered:", event_data)
                return f"Stopped: {event_data if event_data else 'Stopped'}"

            piano_roll_features.play(log_features_play_event, outputs=features_status_text)
            piano_roll_features.pause(log_features_pause_event, outputs=features_status_text)
            piano_roll_features.stop(log_features_stop_event, outputs=features_status_text)

            if not LIBROSA_AVAILABLE:
                gr.Markdown("⚠️ librosa is required")

if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `PianoRoll`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["PianoRoll"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["PianoRoll"]["events"], linkify=['Event'])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
