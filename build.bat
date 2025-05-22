@echo off

pyinstaller --noconfirm --windowed --add-data "icons/icon.ico;." --add-data "config.json;." --icon=icons/icon.ico --add-data "icons;icons" launcher.pyw
copy /Y icon.ico dist\launcher\