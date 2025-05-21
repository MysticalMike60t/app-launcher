import { invoke } from '@tauri-apps/api/tauri';

// Opens the settings window via backend
export function openSettings() {
	invoke('show_settings_window');
}
