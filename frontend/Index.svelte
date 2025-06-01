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
	export let value = false;
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

	// Sample notes data
	const sampleNotes = [
    {
      id: 'note-1',
      start: 80, // 1st beat of measure 1
      duration: 80, // Quarter note
      pitch: 60, // Middle C
      velocity: 100,
      lyric: '안녕'
    },
    {
      id: 'note-2',
      start: 160, // 1st beat of measure 2
      duration: 160, // Half note
      pitch: 64, // E
      velocity: 90,
      lyric: '하세요'
    },
    {
      id: 'note-3',
      start: 320, // 1st beat of measure 3
      duration: 80, // Quarter note
      pitch: 67, // G
      velocity: 95,
      lyric: '반가워요'
    }
  ];
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

	<JsonView json={value} />
	<PianoRoll width={1000} height={600} notes={sampleNotes} />
</Block>
