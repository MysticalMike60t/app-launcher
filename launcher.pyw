import shutil
import sys
import os
import json
import subprocess
import keyboard
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QMessageBox, QInputDialog, QMenu, QStatusBar,
    QSystemTrayIcon
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QEvent, QTimer
from PySide6.QtGui import QPalette, QColor, QFont, QIcon, QGuiApplication, QAction, QPainterPath, QRegion, QPainter, QPen

APP_NAME = "AppLauncher"
APPDATA_PATH = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
if not os.path.exists(APPDATA_PATH):
    os.makedirs(APPDATA_PATH)
CONFIG_PATH = os.path.join(APPDATA_PATH, "config.json")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if not os.path.exists(CONFIG_PATH):
    # Copy the default config from the bundled directory
    default_config = resource_path("config.json")
    if os.path.exists(default_config):
        shutil.copy(default_config, CONFIG_PATH)

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
        central.setObjectName("centralWidget")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(15, 10, 15, 10)
        central_layout.setSpacing(10)
        main_layout.addWidget(central, 1)

        # Set a solid background for the central widget
        central.setStyleSheet("""
            QWidget#centralWidget {
                background: transparent;
                border: 1px solid #4b4b4b;
            }
        """)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search apps and folders...")
        self.search_bar.textChanged.connect(self.filter_apps)
        self.search_bar.setStyleSheet("padding: 6px; border-radius: 8px; background: transparent; color: white;")
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
                background: transparent;
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

        # Add tray icon
        self.tray_icon = QSystemTrayIcon(self)
        tray_icon_path = resource_path("icon.ico")
        print("Tray icon path:", tray_icon_path, "Exists:", os.path.exists(tray_icon_path))
        self.tray_icon.setIcon(QIcon(tray_icon_path) if os.path.exists(tray_icon_path) else self.windowIcon())
        self.tray_icon.setToolTip("App Launcher")

        tray_menu = QMenu()
        open_editor_action = QAction("Open Config Editor", self)
        open_editor_action.triggered.connect(self.open_config_editor)
        tray_menu.addAction(open_editor_action)

        show_launcher_action = QAction("Show Launcher", self)
        show_launcher_action.triggered.connect(self.show_launcher_from_tray)
        tray_menu.addAction(show_launcher_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

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
        # Modern dark translucent style with acrylic blur effect (Windows 10/11)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30, 220))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(40, 40, 40, 200))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35, 180))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(50, 100, 180))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)
        self.setFont(QFont("Segoe UI", 10))

        # Windows 10/11 acrylic blur effect
        try:
            import ctypes
            from ctypes import windll, byref, sizeof, c_int

            class ACCENTPOLICY(ctypes.Structure):
                _fields_ = [
                    ("AccentState", c_int),
                    ("AccentFlags", c_int),
                    ("GradientColor", c_int),
                    ("AnimationId", c_int)
                ]

            class WINCOMPATTRDATA(ctypes.Structure):
                _fields_ = [
                    ("Attribute", c_int),
                    ("Data", ctypes.POINTER(ACCENTPOLICY)),
                    ("SizeOfData", c_int)
                ]

            ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # Acrylic effect
            WCA_ACCENT_POLICY = 19

            hwnd = self.winId().__int__()
            accent = ACCENTPOLICY()
            accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
            accent.AccentFlags = 2  # Enable window border
            # GradientColor: 0xAABBGGRR (AA=alpha, BB=blue, GG=green, RR=red)
            # Example: semi-transparent dark (alpha=0xCC, RGB=0x232323)
            accent.GradientColor = 0xCC232323
            data = WINCOMPATTRDATA()
            data.Attribute = WCA_ACCENT_POLICY
            data.Data = ctypes.pointer(accent)
            data.SizeOfData = sizeof(accent)
            windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))
        except Exception as e:
            print("Acrylic effect failed:", e)

    def populate_apps(self):
        self.tree.clear()

        def add_items(parent, entries):
            for entry in entries:
                if isinstance(entry, dict) and "folder" in entry:
                    folder_item = QTreeWidgetItem([entry["folder"]])
                    folder_item.setExpanded(True)
                    folder_item.setToolTip(0, f"Folder: {entry['folder']}")
                    # Set folder icon if present
                    folder_icon_path = entry.get("icon")
                    if folder_icon_path and os.path.exists(folder_icon_path):
                        folder_item.setIcon(0, QIcon(folder_icon_path))
                    add_items(folder_item, entry.get("apps", []))
                    parent.addChild(folder_item)
                elif isinstance(entry, dict):
                    app_name = entry.get("name", str(entry))
                    app_cmd = entry.get("command", app_name)
                    app_item = QTreeWidgetItem([app_name])
                    app_item.setData(0, Qt.UserRole, app_cmd)
                    app_item.setToolTip(0, app_cmd)
                    icon_path = entry.get("icon")
                    if icon_path and os.path.exists(icon_path):
                        app_item.setIcon(0, QIcon(icon_path))
                    parent.addChild(app_item)
                else:
                    app_item = QTreeWidgetItem([str(entry)])
                    app_item.setData(0, Qt.UserRole, str(entry))
                    parent.addChild(app_item)

        root = self.tree.invisibleRootItem()
        add_items(root, self.config.get("apps", []))

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

    def show_launcher_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_launcher_from_tray()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Opaque background (matches your palette or acrylic tint)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 30, 220))  # Use your desired color and alpha
        painter.drawRect(self.rect())
        # Draw border
        border_color = QColor("#4b4b4b")  # Your lighter border color
        border_width = 1
        rect = self.rect().adjusted(border_width//2, border_width//2, -border_width//2, -border_width//2)
        painter.setPen(QPen(border_color, border_width))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)

class ConfigEditor(QWidget):
    def __init__(self, launcher=None):
        super().__init__()
        self.launcher = launcher
        self.setWindowTitle("Launcher Config Editor")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tree to show structure
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Command/Folder", "Icon"])
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        layout.addWidget(self.tree)

        # Edit fields
        form_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Name")
        form_layout.addWidget(self.name_edit)
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("Command (leave blank for folder)")
        form_layout.addWidget(self.command_edit)
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("Icon path (optional)")
        form_layout.addWidget(self.icon_edit)
        icon_btn = QPushButton("Choose Icon")
        icon_btn.clicked.connect(self.choose_icon)
        form_layout.addWidget(icon_btn)
        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        add_app_btn = QPushButton("Add App")
        add_app_btn.clicked.connect(self.add_app)
        btn_layout.addWidget(add_app_btn)
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_folder_btn)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(remove_btn)
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        reload_btn = QPushButton("Reload Config")
        reload_btn.clicked.connect(self.reload_from_disk)
        btn_layout.addWidget(reload_btn)
        layout.addLayout(btn_layout)

        self.config = load_config()
        self.reload_tree()

    def choose_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Icon", "", "Images (*.png *.ico *.jpg *.bmp)")
        if path:
            self.icon_edit.setText(path)

    def reload_tree(self):
        self.tree.clear()
        def add_items(parent, entries):
            for entry in entries:
                if isinstance(entry, dict) and "folder" in entry:
                    folder_item = QTreeWidgetItem([entry["folder"], "", entry.get("icon", "")])
                    folder_item.setData(0, Qt.UserRole, entry)
                    add_items(folder_item, entry.get("apps", []))
                    parent.addChild(folder_item)
                elif isinstance(entry, dict):
                    app_item = QTreeWidgetItem([entry.get("name", ""), entry.get("command", ""), entry.get("icon", "")])
                    app_item.setData(0, Qt.UserRole, entry)
                    parent.addChild(app_item)
                else:
                    app_item = QTreeWidgetItem([str(entry), "", ""])
                    app_item.setData(0, Qt.UserRole, entry)
                    parent.addChild(app_item)
        root = self.tree.invisibleRootItem()
        add_items(root, self.config.get("apps", []))
        self.name_edit.clear()
        self.command_edit.clear()
        self.icon_edit.clear()

    def on_tree_item_clicked(self, item):
        data = item.data(0, Qt.UserRole)
        if isinstance(data, dict):
            self.name_edit.setText(data.get("name", data.get("folder", "")))
            self.command_edit.setText(data.get("command", ""))
            self.icon_edit.setText(data.get("icon", ""))
        else:
            self.name_edit.setText(str(data))
            self.command_edit.clear()
            self.icon_edit.clear()

    def add_app(self):
        name = self.name_edit.text().strip()
        command = self.command_edit.text().strip()
        icon = self.icon_edit.text().strip()
        if not name or not command:
            QMessageBox.warning(self, "Input Error", "App name and command required.")
            return
        app = {"name": name, "command": command}
        if icon:
            app["icon"] = icon
        selected = self.tree.currentItem()
        if selected:
            data = selected.data(0, Qt.UserRole)
            if isinstance(data, dict) and "folder" in data:
                self._add_app_recursive(self.config["apps"], data["folder"], app)
                self.reload_tree()
                self._select_folder_by_name(data["folder"])
                return
        self.config.setdefault("apps", []).append(app)
        self.reload_tree()

    def _add_app_recursive(self, entries, folder_name, app):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("folder") == folder_name:
                entry.setdefault("apps", []).append(app)
                return True
            if isinstance(entry, dict) and "apps" in entry:
                if self._add_app_recursive(entry["apps"], folder_name, app):
                    return True
        return False

    def add_folder(self):
        name = self.name_edit.text().strip()
        icon = self.icon_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Folder name required.")
            return
        selected = self.tree.currentItem()
        folder = {"folder": name, "apps": []}
        if icon:
            folder["icon"] = icon

        if selected:
            data = selected.data(0, Qt.UserRole)
            if isinstance(data, dict) and "folder" in data:
                # Prevent duplicate subfolder
                if self._folder_exists_recursive(data.get("apps", []), name):
                    QMessageBox.warning(self, "Input Error", "Folder already exists in this location.")
                    return
                # Recursively add folder to the correct subfolder
                if self._add_folder_recursive(self.config["apps"], data["folder"], folder):
                    self.reload_tree()
                    self._select_folder_by_name(name)
                    return

        # Prevent duplicate top-level folder
        if self._folder_exists_recursive(self.config["apps"], name):
            QMessageBox.warning(self, "Input Error", "Folder already exists.")
            return
        self.config.setdefault("apps", []).append(folder)
        self.reload_tree()
        self._select_folder_by_name(name)

    def _add_folder_recursive(self, entries, parent_folder_name, folder_to_add):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("folder") == parent_folder_name:
                entry.setdefault("apps", []).append(folder_to_add)
                return True
            if isinstance(entry, dict) and "apps" in entry:
                if self._add_folder_recursive(entry["apps"], parent_folder_name, folder_to_add):
                    return True
        return False

    def _folder_exists_recursive(self, entries, name):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("folder") == name:
                return True
            if isinstance(entry, dict) and "apps" in entry:
                if self._folder_exists_recursive(entry["apps"], name):
                    return True
        return False

    def _select_folder_by_name(self, name):
        def search(item):
            for i in range(item.childCount()):
                child = item.child(i)
                data = child.data(0, Qt.UserRole)
                if isinstance(data, dict) and data.get("folder") == name:
                    self.tree.setCurrentItem(child)
                    return True
                if search(child):
                    return True
            return False
        search(self.tree.invisibleRootItem())

    def remove_selected(self):
        selected = self.tree.currentItem()
        if not selected:
            return
        parent = selected.parent()
        if parent:
            # Remove app from folder
            folder_name = parent.text(0)
            app_name = selected.text(0)
            for entry in self.config["apps"]:
                if isinstance(entry, dict) and entry.get("folder") == folder_name:
                    entry["apps"] = [a for a in entry.get("apps", []) if a.get("name") != app_name]
                    break
        else:
            # Remove top-level app or folder
            name = selected.text(0)
            to_remove = None
            for entry in self.config["apps"]:
                if (isinstance(entry, dict) and (entry.get("name") == name or entry.get("folder") == name)) or entry == name:
                    to_remove = entry
                    break
            if to_remove:
                self.config["apps"].remove(to_remove)
        self.reload_tree()

    def save(self):
        try:
            save_config(self.config)
            QMessageBox.information(self, "Success", "Config saved!")
            if self.launcher:
                self.launcher.on_config_changed()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save config:\n{e}")

    def reload_from_disk(self):
        self.config = load_config()
        self.reload_tree()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.clearMask()

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
