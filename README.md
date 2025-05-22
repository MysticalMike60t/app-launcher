# App Launcher

**App Launcher** is a modern, visual application and folder launcher for Windows.

More tailored towards developers, being simple with full control over how it works.

## How is this different from [Flow Launcher](https://www.flowlauncher.com/)?

While Flow Launcher is primarily a search-based tool, **App Launcher** presents your apps in a folder-like view. You can organize, launch, and manage your shortcuts with a simple interface.

## Features

- Visual, folder-like layout for your apps and folders
- Always-on-top, borderless, and translucent window
- Global hotkey (default: <kbd>Ctrl</kbd>+<kbd>Space</kbd>) to show/hide the launcher
- Easy configuration via a built-in editor
- System tray integration
- Custom icons for each shortcut
- Lightweight and fast

## Getting Started

1. **Install requirements:**

   ```shell
   pip install -r requirements.txt
   ```

2. **Run the launcher:**

   ```shell
   python main.pyw
   ```

3. **Configure your shortcuts:**

- Click the settings (gear) icon or right-click for the context menu and choose "Open Editor".
- Add, edit, or remove apps and folders as needed.

## Configuration

- The configuration is stored in `config.json` in your app data directory.
- You can edit it directly or use the built-in config editor.

## Building

To package as a standalone executable, use [PyInstaller](https://pyinstaller.org/):

```shell
./build.bat
```

## Version

See [`update-info.txt`](update-info.txt) for the current version.

---

_Inspired by the need for a simple, visual app launcher for Windows power users._
