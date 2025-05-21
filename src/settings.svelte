<script>
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/tauri';

	let jsonText = '';
	let error = '';

	async function loadConfig() {
		const config = await invoke('read_config');
		jsonText = JSON.stringify(config, null, 2);
	}

	async function saveConfig() {
		try {
			const parsed = JSON.parse(jsonText);
			await invoke('write_config', { config: parsed });
			error = '';
			// Optionally notify main window to reload config
			window.tauri?.emit('reload-config');
			alert('Config saved!');
		} catch (e) {
			error = 'Invalid JSON: ' + e.message;
		}
	}

	onMount(loadConfig);
</script>

<div class="editor">
	<h1>Edit config.json</h1>
	{#if error}
		<div class="error">{error}</div>
	{/if}
	<textarea bind:value={jsonText}></textarea>
	<button on:click={saveConfig}>Save</button>
</div>

<style>
	.editor {
		display: flex;
		flex-direction: column;
		padding: 2rem;
		min-width: 500px;
	}
	textarea {
		width: 100%;
		height: 300px;
		font-family: monospace;
		font-size: 1rem;
		margin-bottom: 1rem;
	}
	.error {
		color: red;
		margin-bottom: 1rem;
	}
</div>
