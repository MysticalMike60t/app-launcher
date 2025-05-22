from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QAbstractItemView, QMessageBox, QInputDialog, QMenu, QStatusBar,
    QSystemTrayIcon
)
from PySide6.QtCore import Qt, QFileSystemWatcher, QEvent, QTimer, QSize
from PySide6.QtGui import QPalette, QColor, QFont, QIcon, QGuiApplication, QAction, QPainterPath, QRegion, QPainter, QPen, QCursor
from config import load_config, save_config

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