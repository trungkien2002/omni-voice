[Setup]
AppId={{6B0C6F64-41B4-4DC3-AE98-6CA25CB9B8B0}
AppName=Omni Voice
AppVersion=1.0.0
AppPublisher=Omni Voice
DefaultDirName={localappdata}\Programs\Omni Voice
DefaultGroupName=Omni Voice
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename=OmniVoice-Setup-1.0.0
UninstallDisplayIcon={app}\OmniVoice.exe
WizardStyle=modern
Compression=zip/6
SolidCompression=no
DiskSpanning=yes
DiskSliceSize=max
LZMANumBlockThreads=4
CloseApplications=yes
RestartApplications=no
SetupIconFile=omni.ico
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng Omni Voice trên Desktop"; Flags: checkedonce

[Files]
Source: "stage\OmniVoice\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Omni Voice"; Filename: "{app}\OmniVoice.exe"
Name: "{autodesktop}\Omni Voice"; Filename: "{app}\OmniVoice.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\OmniVoice.exe"; Description: "Mở Omni Voice"; Flags: nowait postinstall skipifsilent
