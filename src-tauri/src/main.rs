// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{AppHandle, Manager, Runtime, WebviewWindowBuilder};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri_plugin_global_shortcut::{Builder as ShortcutPluginBuilder, GlobalShortcutExt};

#[derive(Serialize, Deserialize, Clone)]
struct Config {
    folders: Vec<Folder>,
}
#[derive(Serialize, Deserialize, Clone)]
struct Folder {
    name: String,
    apps: Vec<App>,
}
#[derive(Serialize, Deserialize, Clone)]
struct App {
    name: String,
    icon: String,
    path: String,
}

// Get config.json path (project root)
fn config_path() -> PathBuf {
    std::env::current_dir().unwrap().join("config.json")
}

// Read config.json
#[tauri::command]
fn read_config() -> Result<Config, String> {
    let path = config_path();
    let data = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    serde_json::from_str(&data).map_err(|e| e.to_string())
}

// Write config.json
#[tauri::command]
fn write_config(config: Config) -> Result<(), String> {
    let path = config_path();
    let data = serde_json::to_string_pretty(&config).map_err(|e| e.to_string())?;
    fs::write(&path, data).map_err(|e| e.to_string())
}

// Launch app using shell
#[tauri::command]
fn launch_app(path: String) -> Result<(), String> {
    std::process::Command::new("cmd")
        .args(["/C", &path])
        .spawn()
        .map(|_| ())
        .map_err(|e| e.to_string())
}

// Show settings window (create if not exists)
#[tauri::command]
fn show_settings_window<R: Runtime>(app: AppHandle<R>) {
    if app.get_webview_window("settings").is_none() {
        WebviewWindowBuilder::new(&app, "settings", tauri::WebviewUrl::App("settings".into()))
            .title("Settings")
            .inner_size(600.0, 500.0)
            .resizable(true)
            .build()
            .unwrap();
    } else if let Some(win) = app.get_webview_window("settings") {
        win.show().unwrap();
        win.set_focus().unwrap();
    }
}

// Toggle main window visibility
#[tauri::command]
fn toggle_main_window<R: Runtime>(app: AppHandle<R>) {
    let win = app.get_webview_window("main").unwrap();
    if win.is_visible().unwrap() {
        win.hide().unwrap();
    } else {
        win.show().unwrap();
        win.set_focus().unwrap();
    }
}

// main.rs
fn main() {
    tauri::Builder::default()
        .plugin(ShortcutPluginBuilder::new().build())
        .invoke_handler(tauri::generate_handler![
            read_config,
            write_config,
            launch_app,
            show_settings_window,
            toggle_main_window
        ])
        .setup(|app| {
            let shortcut = "Ctrl+Space";
            app.handle().global_shortcut().register(shortcut)?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
