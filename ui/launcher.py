import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QMessageBox, QInputDialog, QMenu, QStatusBar,
    QSystemTrayIcon
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QEvent, QTimer, QSize
from PySide6.QtGui import QPalette, QColor, QFont, QIcon, QGuiApplication, QAction, QPainterPath, QRegion, QPainter, QPen, QCursor
from config import load_config, save_config, CONFIG_PATH
from utils import resource_path, launch_app
from ui.config_editor import ConfigEditor

class HoverIconButton(QPushButton):
    def __init__(self, normal_icon, hover_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normal_icon = QIcon(normal_icon)
        self.hover_icon = QIcon(hover_icon)
        self.setIcon(self.normal_icon)
        self.setIconSize(QSize(24, 24))

    def enterEvent(self, event):
        self.setIcon(self.hover_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.normal_icon)
        super().leaveEvent(event)

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
        settings_icon_path = resource_path("icons/settings.png")
        settings_icon_dark_path = resource_path("icons/settings-dark.png")

        self.config_btn = HoverIconButton(settings_icon_path, settings_icon_dark_path)
        self.config_btn.setFixedSize(32, 32)
        self.config_btn.setToolTip("Open Config Editor")
        self.config_btn.clicked.connect(self.open_config_editor)
        self.config_btn.setCursor(QCursor(Qt.PointingHandCursor))
        search_layout.addWidget(self.config_btn)

        # Set stylesheet for hover effect
        settings_icon_path_css = settings_icon_path.replace("\\", "/")
        settings_icon_dark_path_css = settings_icon_dark_path.replace("\\", "/")
        self.config_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0,0,0,0);
                border-radius: 8px;
                border: none;
                qproperty-icon: url("{settings_icon_path_css}");
            }}
            QPushButton:hover {{
                qproperty-icon: url("{settings_icon_dark_path_css}");
            }}
        """)
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
        tray_icon_path = resource_path("icons/icon.ico")
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