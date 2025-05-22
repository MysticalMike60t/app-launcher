import sys
import keyboard
from PySide6.QtWidgets import QApplication
from ui.launcher import AppLauncher

def main():
    app = QApplication(sys.argv)
    launcher = AppLauncher()
    launcher.show()

    # Add global hotkey to toggle launcher visibility
    keyboard.add_hotkey("ctrl+space", lambda: launcher.setVisible(not launcher.isVisible()))

    sys.exit(app.exec())

if __name__ == "__main__":
    main()