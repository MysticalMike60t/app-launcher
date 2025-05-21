@echo off

pyinstaller --noconfirm --windowed --add-data "config.json;." --icon=icon.ico --add-data "icons;icons" launcher.pyw