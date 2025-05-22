@echo off

pyinstaller launcher.spec

REM Ensure icons folder is in dist\launcher
xcopy /E /I /Y icons dist\launcher\icons

copy /Y icon.ico dist\launcher\