#define MyAppName "POP PUNK GUITAR LIBRARY MANAGER"
#define MyAppVersion "3.0.0-dev9"
#define MyAppPublisher "L3XTOWN"
#define MyAppExeName "POP_PUNK_GUITAR_LIBRARY_MANAGER.exe"

[Setup]
AppId={{A16A7E54-7A3B-4F7D-9E2A-300000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist\installer
OutputBaseFilename=POP-PUNK-GUITAR-LIBRARY-MANAGER-Setup-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные значки:"; Flags: unchecked

[Files]
Source: "dist\POP_PUNK_GUITAR_LIBRARY_MANAGER\*"; DestDir: "{app}"; Excludes: "portable.mode;UserData\*"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\POP PUNK GUITAR Library Manager"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\POP PUNK GUITAR Library Manager"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить POP PUNK GUITAR Library Manager"; Flags: postinstall nowait skipifsilent
