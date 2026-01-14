<script lang="ts">
	import { JsonView } from "@zerodevx/svelte-json-view";

	import type { Gradio } from "@gradio/utils";
	import { Block, Info } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { SelectData } from "@gradio/utils";

	import PianoRoll from "./components/PianoRoll.svelte";
	import { createLogger } from "./utils/logger";

	const log = createLogger('Index');

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;

	export let value = {
		notes: [],
		tempo: 120,
		timeSignature: { numerator: 4, denominator: 4 },
		editMode: 'select',
		snapSetting: '1/4',
		pixelsPerBeat: 80,
		sampleRate: 44100,
		ppqn: 480
	};
	export let container = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		change: never;
		input: never;  // Triggered when lyrics are edited (for G2P execution)
		play: never;   // Triggered when play button is clicked
		pause: never;  // Triggered when pause button is clicked
		stop: never;   // Triggered when stop button is clicked
		clear: never;  // Triggered when clear button is clicked
		select: SelectData;
		clear_status: LoadingStatus;
	}>;

	// Backend data properties
	export let audio_data: string | null = null;
	export let curve_data: object | null = null;
	export let segment_data: Array<any> | null = null;
	export let line_data: object | null = null;  // Line layer data (pitch curves, loudness, etc.)
	export let use_backend_audio: boolean = false;

	export let width = 800;
	export let height = 400;

	// Set default values if value is not initialized or missing required properties
	$: if (!value || typeof value !== 'object') {
		value = {
			notes: [],
			tempo: 120,
			timeSignature: { numerator: 4, denominator: 4 },
			editMode: 'select',
			snapSetting: '1/4',
			pixelsPerBeat: 80,
			sampleRate: 44100,
			ppqn: 480
		};
	} else {
		// Set default values only for missing individual properties
		if (!value.notes) value.notes = [];
		if (!value.tempo) value.tempo = 120;
		if (!value.timeSignature) value.timeSignature = { numerator: 4, denominator: 4 };
		if (!value.editMode) value.editMode = 'select';
		if (!value.snapSetting) value.snapSetting = '1/4';
		if (!value.pixelsPerBeat) value.pixelsPerBeat = 80;
		if (!value.sampleRate) value.sampleRate = 44100;
		if (!value.ppqn) value.ppqn = 480;
	}

	// Extract backend data - Update backend data props whenever value changes
	$: if (value && typeof value === 'object') {
		// Update props if backend data exists in value
		if ('audio_data' in value && value.audio_data !== undefined) {
			log.debug("Audio data updated:", !!value.audio_data);
			audio_data = typeof value.audio_data === 'string' ? value.audio_data : null;
		}
		if ('curve_data' in value && value.curve_data !== undefined) {
			log.debug("Curve data updated:", value.curve_data);
			curve_data = value.curve_data && typeof value.curve_data === 'object' ? value.curve_data : null;
		}
		if ('segment_data' in value && value.segment_data !== undefined) {
			log.debug("Segment data updated:", value.segment_data);
			segment_data = Array.isArray(value.segment_data) ? value.segment_data : null;
		}
		if ('use_backend_audio' in value && value.use_backend_audio !== undefined) {
			use_backend_audio = typeof value.use_backend_audio === 'boolean' ? value.use_backend_audio : false;
		}
		if ('line_data' in value && value.line_data !== undefined) {
			log.debug("Line data updated:", value.line_data);
			line_data = value.line_data && typeof value.line_data === 'object' ? value.line_data : null;
		}
	}

	// Handler called when piano roll data changes (tempo, note info, etc.)
	function handlePianoRollChange(event: CustomEvent) {
		const { notes, tempo, timeSignature, editMode, snapSetting, pixelsPerBeat, sampleRate, ppqn } = event.detail;

		// Update entire value object
		value = {
			notes: notes,
			tempo,
			timeSignature,
			editMode,
			snapSetting,
			pixelsPerBeat,
			sampleRate: sampleRate || 44100,
			ppqn: ppqn || 480
		};

		// Pass changes to Gradio
		gradio.dispatch("change");
	}

	// Handler called when lyrics are edited (input event fires first)
	function handleLyricInput(event: CustomEvent) {
		const { notes, lyricData } = event.detail;

		// Update note info
		value = {
			...value,
			notes: notes
		};

		// Dispatch input event first (for G2P execution)
		gradio.dispatch("input", lyricData);

		// Then dispatch change event
		setTimeout(() => {
			gradio.dispatch("change");
		}, 0);
	}

	// Handler called when only notes change (note changes other than lyrics)
	function handleNotesChange(event: CustomEvent) {
		const { notes } = event.detail;

		// Update only notes
		value = {
			...value,
			notes: notes
		};

		// Send changes to Gradio
		gradio.dispatch("change");
	}

	// Playback control event handlers
	function handlePlay(event: CustomEvent) {
		gradio.dispatch("play", event.detail);
	}

	function handlePause(event: CustomEvent) {
		gradio.dispatch("pause", event.detail);
	}

	function handleStop(event: CustomEvent) {
		gradio.dispatch("stop", event.detail);
	}

	function handleClear(event: CustomEvent) {
		gradio.dispatch("clear", event.detail);
	}
</script>

<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width}>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}

	<!-- PianoRoll Component -->
	<PianoRoll
		width={width}
		height={height}
		notes={value.notes}
		tempo={value.tempo}
		timeSignature={value.timeSignature}
		editMode={value.editMode}
		snapSetting={value.snapSetting}
		pixelsPerBeat={value.pixelsPerBeat || 80}
		sampleRate={value.sampleRate || 44100}
		ppqn={value.ppqn || 480}
		{audio_data}
		{curve_data}
		{line_data}
		{use_backend_audio}
		{elem_id}
		on:dataChange={handlePianoRollChange}
		on:noteChange={handleNotesChange}
		on:lyricInput={handleLyricInput}
		on:play={handlePlay}
		on:pause={handlePause}
		on:stop={handleStop}
		on:clear={handleClear}
	/>
</Block>
