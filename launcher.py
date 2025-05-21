import json
import os
import subprocess
import sys
import threading

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTextEdit, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import keyboard

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

class AppLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Launcher")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        scroll = QScrollArea()
        container = QWidget()
        self.grid = QVBoxLayout()
        container.setLayout(self.grid)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.setLayout(layout)
        self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        for folder in config.get("folders", []):
            folder_label = QLabel(f"📁 {folder['name']}")
            folder_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            self.grid.addWidget(folder_label)

            grid = QGridLayout()
            row = col = 0
            for app in folder.get("apps", []):
                btn = QPushButton(app['name'])
                icon_path = app.get("icon")
                if icon_path and os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                btn.clicked.connect(lambda _, path=app['path']: self.launch_app(path))
                grid.addWidget(btn, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1
            self.grid.addLayout(grid)

    def launch_app(self, path):
        try:
            subprocess.Popen(path, shell=True)
        except Exception as e:
            print(f"Failed to launch {path}: {e}")

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.raise_()


class ConfigEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Editor")
        self.setGeometry(200, 200, 600, 500)

        layout = QVBoxLayout()
        self.editor = QTextEdit()
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(save_btn)

        open_btn = QPushButton("Open Config File")
        open_btn.clicked.connect(self.open_config_file)
        btn_layout.addWidget(open_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                self.editor.setText(f.read())

    def save_config(self):
        try:
            with open(CONFIG_PATH, 'w') as f:
                f.write(self.editor.toPlainText())
        except Exception as e:
            print(f"Error saving config: {e}")

    def open_config_file(self):
        os.startfile(CONFIG_PATH)

def hotkey_listener(launcher):
    keyboard.add_hotkey("ctrl+space", lambda: launcher.show() if not launcher.isVisible() else launcher.hide())

def main():
    app = QApplication(sys.argv)
    launcher = AppLauncher()
    editor = ConfigEditor()

    # Show on launch for now
    launcher.show()

    # Register hotkeys (non-blocking)
    keyboard.add_hotkey("ctrl+space", launcher.toggle)
    keyboard.add_hotkey("ctrl+shift+e", editor.show)

    print("Launcher running. Press Ctrl+Space.")
    sys.exit(app.exec())


main()