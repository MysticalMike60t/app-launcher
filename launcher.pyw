import sys
import os
import json
import subprocess
import keyboard
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QMessageBox, QInputDialog, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QEvent, QTimer
from PySide6.QtGui import QPalette, QColor, QFont, QIcon, QGuiApplication

CONFIG_PATH = "config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    # Default config with folders and apps
    return {
        "apps": [
            {"name": "Notepad", "command": "notepad.exe"},
            {"name": "Calculator", "command": "calc.exe"},
            {
                "folder": "Utilities",
                "apps": [
                    {"name": "Command Prompt", "command": "cmd.exe"}
                ]
            }
        ]
    }

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save config: {e}")

def launch_app(command):
    # Launch app with subprocess for better control
    try:
        # Use start to open exe or file with default app on Windows
        subprocess.Popen(f'start "" "{command}"', shell=True)
    except Exception as e:
        QMessageBox.warning(None, "Launch Error", f"Failed to launch {command}:\n{e}")

class AppLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern App Launcher")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyle()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Central widget layout
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(15, 10, 15, 10)
        central_layout.setSpacing(10)
        main_layout.addWidget(central, 1)

        # Set a solid background for the central widget
        central.setStyleSheet("background: #232323; border-radius: 12px;")

        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search apps and folders...")
        self.search_bar.textChanged.connect(self.filter_apps)
        self.search_bar.setStyleSheet("padding: 6px; border-radius: 8px; background: #232323; color: white;")
        search_layout.addWidget(self.search_bar)

        # Config editor button
        self.config_btn = QPushButton("⚙")
        self.config_btn.setFixedSize(32, 32)
        self.config_btn.setStyleSheet("background: #232323; color: white; border-radius: 8px; font-size: 18px;")
        self.config_btn.setToolTip("Open Config Editor")
        self.config_btn.clicked.connect(self.open_config_editor)
        search_layout.addWidget(self.config_btn)
        central_layout.addLayout(search_layout)

        # Tree widget to show folders/apps
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.itemDoubleClicked.connect(self.launch_item)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #232323;
                color: white;
                border-radius: 8px;
                font-size: 14px;
            }
            QTreeWidget::item:selected {
                background: #3256a8;
                color: white;
            }
            QTreeWidget::item:hover {
                background: #2a2a2a;
            }
        """)
        self.tree.setContextMenuPolicy(Qt.NoContextMenu)
        self.tree.setDragDropMode(QAbstractItemView.NoDragDrop)
        central_layout.addWidget(self.tree, 1)

        # Custom status label inside central widget for rounded corners
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaa; font-size: 12px; padding: 4px 0 0 4px;")
        central_layout.addWidget(self.status_label)

        self.config = load_config()
        self.populate_apps()

        self.watcher = QFileSystemWatcher([CONFIG_PATH])
        self.watcher.fileChanged.connect(self.on_config_changed)

    def showEvent(self, event):
        # Position the window just above the taskbar, centered
        screen = QGuiApplication.primaryScreen().geometry()
        taskbar_height = 48  # Typical Windows taskbar height; adjust if needed
        x = screen.x() + (screen.width() - self.width()) // 2
        y = screen.y() + screen.height() - self.height() - taskbar_height + 8
        self.move(x, y)
        super().showEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def setStyle(self):
        # Modern dark translucent style with blur effect
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30, 240))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(40, 40, 40, 220))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35, 200))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(50, 100, 180))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        self.setFont(QFont("Segoe UI", 10))

        # Optional: add blur effect (Windows 10+ only)
        try:
            from ctypes import windll, byref, sizeof, c_int
            hwnd = self.winId().__int__()
            class ACCENTPOLICY(ctypes.Structure):
                _fields_ = [("AccentState", c_int),
                            ("AccentFlags", c_int),
                            ("GradientColor", c_int),
                            ("AnimationId", c_int)]
            class WINCOMPATTRDATA(ctypes.Structure):
                _fields_ = [("Attribute", c_int),
                            ("Data", ctypes.POINTER(ACCENTPOLICY)),
                            ("SizeOfData", c_int)]
            ACCENT_ENABLE_BLURBEHIND = 3
            accent = ACCENTPOLICY()
            accent.AccentState = ACCENT_ENABLE_BLURBEHIND
            accent.GradientColor = 0x99000000  # semi-transparent black
            data = WINCOMPATTRDATA()
            data.Attribute = 19  # WCA_ACCENT_POLICY
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = sizeof(accent)
            windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))
        except Exception:
            pass

    def populate_apps(self):
        self.tree.clear()
        for entry in self.config.get("apps", []):
            if isinstance(entry, dict):
                if "folder" in entry:
                    folder_item = QTreeWidgetItem([entry["folder"]])
                    folder_item.setExpanded(True)
                    folder_item.setToolTip(0, f"Folder: {entry['folder']}")
                    # Set folder icon if present
                    folder_icon_path = entry.get("icon")
                    if folder_icon_path and os.path.exists(folder_icon_path):
                        folder_item.setIcon(0, QIcon(folder_icon_path))
                    for app in entry.get("apps", []):
                        if isinstance(app, dict):
                            app_item = QTreeWidgetItem([app.get("name", "Unnamed")])
                            app_item.setData(0, Qt.UserRole, app.get("command", app.get("name", "")))
                            app_item.setToolTip(0, app.get("command", ""))
                            # Set app icon if present
                            icon_path = app.get("icon")
                            if icon_path and os.path.exists(icon_path):
                                app_item.setIcon(0, QIcon(icon_path))
                            folder_item.addChild(app_item)
                        else:
                            app_item = QTreeWidgetItem([str(app)])
                            app_item.setData(0, Qt.UserRole, str(app))
                            folder_item.addChild(app_item)
                    self.tree.addTopLevelItem(folder_item)
                else:
                    app_name = entry.get("name", str(entry))
                    app_cmd = entry.get("command", app_name)
                    app_item = QTreeWidgetItem([app_name])
                    app_item.setData(0, Qt.UserRole, app_cmd)
                    app_item.setToolTip(0, app_cmd)
                    # Set app icon if present
                    icon_path = entry.get("icon")
                    if icon_path and os.path.exists(icon_path):
                        app_item.setIcon(0, QIcon(icon_path))
                    self.tree.addTopLevelItem(app_item)
            else:
                app_item = QTreeWidgetItem([str(entry)])
                app_item.setData(0, Qt.UserRole, str(entry))
                self.tree.addTopLevelItem(app_item)

    def filter_apps(self, text):
        text = text.lower()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            top_item = root.child(i)
            visible = False
            if top_item.childCount() > 0:
                # Folder: check children
                for j in range(top_item.childCount()):
                    child = top_item.child(j)
                    match = text in child.text(0).lower()
                    child.setHidden(not match)
                    if match:
                        visible = True
                top_item.setHidden(not visible)
            else:
                # Single app
                match = text in top_item.text(0).lower()
                top_item.setHidden(not match)

    def launch_item(self, item, column):
        command = item.data(0, Qt.UserRole)
        if command:
            launch_app(command)
            self.show_status(f"Launched: {item.text(0)}", 2000)

    def on_config_changed(self):
        self.config = load_config()
        self.populate_apps()
        self.show_status("Config reloaded", 2000)

    def open_config_editor(self):
        if not hasattr(self, 'editor') or self.editor is None:
            self.editor = ConfigEditor(self)
        self.editor.show()
        self.editor.raise_()
        self.editor.activateWindow()

    def show_status(self, msg, timeout=2000):
        self.status_label.setText(msg)
        if timeout:
            QTimer.singleShot(timeout, lambda: self.status_label.setText(""))

class ConfigEditor(QWidget):
    def __init__(self, launcher=None):
        super().__init__()
        self.launcher = launcher
        self.setWindowTitle("Launcher Config Editor")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.editor = QTextEdit()
        self.editor.setText(json.dumps(load_config(), indent=4))
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)

        reload_btn = QPushButton("Reload Config")
        reload_btn.clicked.connect(self.reload)
        btn_layout.addWidget(reload_btn)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def save(self):
        try:
            config = json.loads(self.editor.toPlainText())
            save_config(config)
            QMessageBox.information(self, "Success", "Config saved!")
            if self.launcher:
                self.launcher.on_config_changed()
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON!")

    def reload(self):
        self.editor.setText(json.dumps(load_config(), indent=4))

def main():
    app = QApplication(sys.argv)
    launcher = AppLauncher()
    editor = launcher.open_config_editor  # Not used directly, but keeps reference

    launcher.show()

    # Hotkey toggles launcher visibility
    keyboard.add_hotkey("ctrl+space", lambda: launcher.setVisible(not launcher.isVisible()))

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
