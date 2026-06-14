; Advanced Audio Converter OldWin - Inno Setup 5.x UNIFIED installer
; Version 0.13.6c pre-stable
; One installer for XP x86 and Win7/8/10/11 x86/x64.
; Runtime is 32-bit OldWin/XP-compatible and runs on x64 Windows through WOW64.
; Use Inno Setup 5.6.1.
;
; Output:
; - installer_output_oldwin_unified\setup.exe
; - installer_output_oldwin_unified\setup-1.bin
;
; Keep setup.exe and setup-1.bin together.

#define MyAppName "Advanced Audio Converter OldWin"
#define MyAppVersion "0.13.6c pre-stable"
#define MyInstallerRevision "0.13.6c-prestable-unified"
#define MyAppPublisher "unliked1280"
#define MyAppExeName "Advanced_Audio_Converter_OldWin.exe"

[Setup]
AppId={{7B5E7E4D-0E1B-4E7E-AACF-00000001351}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyInstallerRevision}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\Advanced Audio Converter OldWin
DefaultGroupName=Advanced Audio Converter OldWin
DisableProgramGroupPage=yes
OutputDir=installer_output_oldwin_unified
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=0,5.1sp3
Uninstallable=yes
CreateUninstallRegKey=yes
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallFilesDir={app}
SetupIconFile=icon.ico
LicenseFile=dist\Advanced_Audio_Converter_OldWin\licenses\INSTALL_LICENSE_ACCEPTANCE.txt
InfoBeforeFile=dist\Advanced_Audio_Converter_OldWin\INSTALL_MINIMUM_REQUIREMENTS.txt
VersionInfoVersion=0.13.6.3
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Unified OldWin Setup + Data Installer
VersionInfoTextVersion={#MyInstallerRevision}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion=0.13.6.3

DiskSpanning=yes
DiskSliceSize=max
SlicesPerDisk=1

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\Advanced_Audio_Converter_OldWin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Advanced Audio Converter OldWin"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Minimum System Requirements"; Filename: "{app}\INSTALL_MINIMUM_REQUIREMENTS.txt"
Name: "{group}\License Acceptance"; Filename: "{app}\licenses\INSTALL_LICENSE_ACCEPTANCE.txt"
Name: "{group}\MIT License"; Filename: "{app}\licenses\LICENSE_MIT.txt"
Name: "{group}\Third-Party Notices"; Filename: "{app}\licenses\THIRD_PARTY_NOTICES.txt"
Name: "{group}\Uninstall Advanced Audio Converter OldWin"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Advanced Audio Converter OldWin"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Advanced Audio Converter OldWin"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\AdvancedAudioConverter_OldWin"
Type: filesandordirs; Name: "{userappdata}\AdvancedAudioConverter_OldWin_PyQt4"
Type: filesandordirs; Name: "{userappdata}\AdvancedAudioConverter_XP"
Type: filesandordirs; Name: "{userappdata}\AdvancedAudioConverter_XP_PyQt4"
Type: filesandordirs; Name: "{userappdata}\AdvancedAudioConverter_XP_Tk"

[Code]
function InitializeUninstall(): Boolean;
begin
  Result := True;
end;
