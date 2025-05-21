; filepath: launcher.iss
[Setup]
AppName=App Launcher
AppVersion=1.0
DefaultDirName={autopf}\AppLauncher
DefaultGroupName=App Launcher
OutputBaseFilename=launcher.setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\launcher\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\App Launcher"; Filename: "{app}\launcher.exe"
Name: "{group}\Uninstall App Launcher"; Filename: "{uninstallexe}"