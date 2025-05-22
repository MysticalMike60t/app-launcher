import sys
import os
import subprocess
from PySide6.QtWidgets import QMessageBox

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def launch_app(command):
    try:
        subprocess.Popen(f'start "" "{command}"', shell=True)
    except Exception as e:
        QMessageBox.warning(None, "Launch Error", f"Failed to launch {command}:\n{e}")