@echo off

pyinstaller --noconfirm --windowed --add-data "icon.ico;." --add-data "config.json;." --icon=icon.ico --add-data "icons;icons" launcher.pyw
copy /Y icon.ico dist\launcher\