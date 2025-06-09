import gradio as gr
from gradio_pianoroll import PianoRoll

from common_utils import (
    get_phoneme_mapping_for_dataframe,
    add_phoneme_mapping,
    reset_phoneme_mapping,
    auto_generate_all_phonemes,
    mock_g2p,
    clear_all_phonemes,
)

# Gradio interface
with gr.Blocks(title="PianoRoll with Synthesizer Demo") as demo:
    gr.Markdown("# 🎹 Gradio PianoRoll with Synthesizer")
    gr.Markdown("Test PianoRoll component and synthesizer functionality!")
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
        """Process lyric input event - detect piano roll changes and generate phoneme"""
        print("🗣️ Phoneme tab - Input event triggered")
        print(f"   - Piano roll data: {type(piano_roll_data)}")

        if not piano_roll_data or 'notes' not in piano_roll_data:
            return piano_roll_data, "Piano roll data is missing."

        return auto_generate_missing_phonemes(piano_roll_data)

    def auto_generate_missing_phonemes(piano_roll_data):
        """Automatically generate phoneme for notes with lyrics but no phoneme"""
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
        """Handle automatic phoneme generation when note changes"""
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

if __name__ == "__main__":
    demo.launch()
