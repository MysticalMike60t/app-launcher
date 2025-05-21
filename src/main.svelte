<script>
	// @ts-nocheck
	import { onMount } from 'svelte';
	import { listen } from '@tauri-apps/api/event';
	import { invoke } from '@tauri-apps/api/tauri';
	import { openSettings } from './utils.js';

	/** @type {{folders: {name: string, apps: {name: string, icon: string, path: string}[]}[]} } */
	let config = { folders: [] };

	// Load config.json from backend
	async function loadConfig() {
		config = await invoke('read_config');
	}

	// Launch app via backend
	async function launchApp(app) {
		await invoke('launch_app', { path: app.path });
	}

	onMount(() => {
		loadConfig();

		// Listen for config reload (optional, e.g. after settings save)
		window.addEventListener('reload-config', loadConfig);

		// Listen for global shortcut event from Tauri v2 plugin
		listen('tauri://global-shortcut', (event) => {
			if (event.payload === 'Ctrl+Space') {
				invoke('toggle_main_window');
			}
		});
	});
</script>

<div class="launcher">
	<button class="settings-btn" title="Settings" on:click={openSettings}>⚙️</button>
	{#each config.folders as folder}
		<h2>{folder.name}</h2>
		<div class="app-grid">
			{#each folder.apps as app}
				<div class="app" on:click={() => launchApp(app)}>
					<img src={app.icon} alt={app.name} />
					<span>{app.name}</span>
				</div>
			{/each}
		</div>
	{/each}
</div>

<style>
	.launcher {
		padding: 2rem;
		min-width: 400px;
	}
	h2 {
		margin-top: 1.5rem;
	}
	.app-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}
	.app {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 80px;
		cursor: pointer;
		transition: background 0.2s;
		border-radius: 8px;
		padding: 0.5rem;
	}
	.app:hover {
		background: #f0f0f0;
	}
	.app img {
		width: 48px;
		height: 48px;
		margin-bottom: 0.5rem;
	}
	.settings-btn {
		position: absolute;
		top: 1rem;
		right: 1rem;
		cursor: pointer;
		font-size: 1.2rem;
		background: none;
		border: none;
	}
</style>
