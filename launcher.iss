[Setup]
AppName=App Launcher
AppVersion=1.0
DefaultDirName={autopf}\AppLauncher
DefaultGroupName=App Launcher
OutputBaseFilename=launcher.setup
Compression=lzma
SolidCompression=yes
AppPublisher=Caden Finkelstein
AppPublisherURL=https://yourwebsite.com
AppSupportURL=https://yourwebsite.com/support
AppUpdatesURL=https://yourwebsite.com/updates

[Files]
Source: "dist\launcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\App Launcher"; Filename: "{app}\launcher.exe"
Name: "{group}\Uninstall App Launcher"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\launcher.exe"; Description: "Launch App Launcher"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Registry]
Root: HKCU; Subkey: "Software\AppLauncher"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
