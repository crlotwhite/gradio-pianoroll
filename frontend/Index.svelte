<script lang="ts">
	import { JsonView } from "@zerodevx/svelte-json-view";

	import type { Gradio } from "@gradio/utils";
	import { Block, Info } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { SelectData } from "@gradio/utils";

	import PianoRoll from "./components/PianoRoll.svelte";

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
		select: SelectData;
		input: never;
		clear_status: LoadingStatus;
	}>;

	export let width = 800;
	export let height = 400;

	// value가 초기화되지 않았거나 필수 속성이 누락된 경우 기본값 설정
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
		// 개별 속성이 없는 경우에만 기본값 설정
		if (!value.notes) value.notes = [];
		if (!value.tempo) value.tempo = 120;
		if (!value.timeSignature) value.timeSignature = { numerator: 4, denominator: 4 };
		if (!value.editMode) value.editMode = 'select';
		if (!value.snapSetting) value.snapSetting = '1/4';
		if (!value.pixelsPerBeat) value.pixelsPerBeat = 80;
		if (!value.sampleRate) value.sampleRate = 44100;
		if (!value.ppqn) value.ppqn = 480;
	}

	// 피아노롤에서 데이터 변경 시 호출되는 핸들러
	function handlePianoRollChange(event: CustomEvent) {
		const { notes, tempo, timeSignature, editMode, snapSetting, pixelsPerBeat, sampleRate, ppqn } = event.detail;

		// value 전체 업데이트
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

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
		gradio.dispatch("input");
	}

	// 노트만 변경되었을 때 호출되는 핸들러
	function handleNotesChange(event: CustomEvent) {
		const { notes } = event.detail;

		// 노트만 업데이트
		value = {
			...value,
			notes: notes
		};

		// Gradio로 변경사항 전달
		gradio.dispatch("change");
		gradio.dispatch("input");
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

	<!-- 피아노롤 컴포넌트 -->
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
		on:dataChange={handlePianoRollChange}
		on:noteChange={handleNotesChange}
	/>
</Block>
