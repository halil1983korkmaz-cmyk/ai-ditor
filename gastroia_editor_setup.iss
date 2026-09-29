; Inno Setup script for GASTROIA Editor (Windows)
; Build with: iscc gastroia_editor_setup.iss

#define MyAppName "GASTROIA Editor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GASTROIA"
#define MyAppExeName "GastroiaEditor.exe"

[Setup]
AppId={{6F0C2D8A-4B1E-4C57-9A3D-7E5A1B9C2F44}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=GastroiaEditor_Setup
SetupIconFile=icon_gastroia.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
