#define MyAppVersion "1.0.3"

[Setup]
AppName=App Launcher
SetupIconFile=icon.ico
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\AppLauncher
DefaultGroupName=App Launcher
OutputBaseFilename=launcher.{#MyAppVersion}.setup
Compression=lzma
SolidCompression=yes
AppPublisher=Caden Finkelstein
AppPublisherURL=https://github.com/MysticalMike60t/app-launcher
AppSupportURL=https://github.com/MysticalMike60t/app-launcher/issues
AppUpdatesURL=https://github.com/mysticalmike60t/app-launcher/releases

[Files]
Source: "dist\launcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\launcher\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\App Launcher"; Filename: "{app}\launcher.exe"
Name: "{group}\Uninstall App Launcher"; Filename: "{uninstallexe}"
Name: "{commondesktop}\App Launcher"; Filename: "{app}\launcher.exe"; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\launcher.exe"; Description: "Launch App Launcher"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Registry]
Root: HKCU; Subkey: "Software\AppLauncher"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Code]
function GetRemoteVersion(): String;
var
  WinHttp: Variant;
  Response: String;
begin
  try
    WinHttp := CreateOleObject('WinHttp.WinHttpRequest.5.1');
    WinHttp.Open('GET', 'https://raw.githubusercontent.com/MysticalMike60t/app-launcher/refs/heads/main/update-info.txt', False);
    WinHttp.Send;
    Response := WinHttp.ResponseText;
    Result := Trim(Response);
  except
    Result := '';
  end;
end;

function InitializeSetup(): Boolean;
var
  RemoteVer: string;
begin
  RemoteVer := GetRemoteVersion();
  if RemoteVer = '' then begin
    MsgBox('Could not check for updates.', mbInformation, MB_OK);
  end else if CompareStr(RemoteVer, '{#MyAppVersion}') > 0 then begin
    if MsgBox('A newer version (' + RemoteVer + ') is available. Continue installing this version?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False
    else
      Result := True;
  end else
    Result := True;
end;
