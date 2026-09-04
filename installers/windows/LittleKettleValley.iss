; Little Kettle Valley - Windows one-click installer
; ---------------------------------------------------
; Packages the tree produced by installers/windows/stage.py:
;   Prism Launcher 11.1.0 (MinGW-w64 portable, needs no VC++ Redistributable)
;   + portable.txt          -> the install folder is Prism's whole data root
;   + jre/                  -> Eclipse Temurin 17 JRE, so no "install Java first" step
;   + instances/Little Kettle Valley  -> the pack instance, self-updating via packwiz on every launch
;   + prismlauncher.cfg     -> pre-seeded so no first-run wizard page appears except Microsoft login
;
; Build:  ISCC.exe installers\windows\LittleKettleValley.iss
; (run stage.py first -- it also regenerates version.iss from pack/pack.toml)

#include "version.iss"

#define AppName "Little Kettle Valley"
#define AppPublisher "Josh Malloy"
#define AppURL "https://github.com/malloyjoshua/little-kettle-valley"
#define ExeName "prismlauncher.exe"

[Setup]
AppId={{935DBAC7-AAAF-43F8-B23F-03004DC69E82}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases

; No UAC prompt, ever: everything lands in the user's own profile. Deliberately no
; PrivilegesRequiredOverridesAllowed -- that would add an "install for all users?" dialog whose
; other branch triggers UAC.
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Little Kettle Valley
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableWelcomePage=yes
DisableReadyPage=yes
UsePreviousAppDir=yes

; Prism Launcher requires 64-bit Windows 10 or newer; so does the bundled x64 JRE.
MinVersion=10.0
ArchitecturesAllowed=x64compatible

OutputDir=build\out
OutputBaseFilename=LittleKettleValley-Setup
SetupIconFile=LittleKettleValley.ico
UninstallDisplayIcon={app}\LittleKettleValley.ico
UninstallDisplayName={#AppName}
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "build\stage\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Plain shortcut, no -l/--launch: with zero Microsoft accounts configured, --launch pops a blocking
; "No Accounts" modal and then aborts the launch (LaunchController::decideAccount) rather than
; walking the user into sign-in. Opening the launcher window is the graceful first run.
Name: "{group}\{#AppName}"; Filename: "{app}\{#ExeName}"; IconFilename: "{app}\LittleKettleValley.ico"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExeName}"; IconFilename: "{app}\LittleKettleValley.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "Launch {#AppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[Code]

const
  JavaPathToken = '@@JAVA_PATH@@';

{ Absolute path to the bundled JRE, written with forward slashes.

  Forward slashes are load-bearing: Prism reads these files through INIFile::loadFile, which -- for
  a file with no ConfigVersion key -- falls back to parseOldFileFormat() and runs unescape() over
  every value. unescape() (INIFile.cpp 76-99) drops any backslash that is not \n, \t or \#, so
  "C:\Users\..." would arrive as "C:Users...". Qt resolves the forward-slash form natively on
  Windows. }
function BundledJavaPath(): String;
var
  P: String;
begin
  P := ExpandConstant('{app}') + '\jre\bin\javaw.exe';
  StringChangeEx(P, '\', '/', True);
  Result := P;
end;

{ Replace the placeholder token in one config file, preserving every other line verbatim.
  Written back as UTF-8 without a BOM: Prism reads these as UTF-8, and a BOM would end up glued to
  the first key name. The install path can contain non-ASCII characters (a friend's user name), so
  an ANSI write would corrupt it. }
function PatchJavaPath(const FileName: String): Boolean;
var
  Lines: TArrayOfString;
  I: Integer;
  Changed: Boolean;
begin
  Result := False;
  if not FileExists(FileName) then
  begin
    Log('PatchJavaPath: missing ' + FileName);
    Exit;
  end;
  if not LoadStringsFromFile(FileName, Lines) then
  begin
    Log('PatchJavaPath: could not read ' + FileName);
    Exit;
  end;

  Changed := False;
  for I := 0 to GetArrayLength(Lines) - 1 do
  begin
    if Pos(JavaPathToken, Lines[I]) > 0 then
    begin
      StringChangeEx(Lines[I], JavaPathToken, BundledJavaPath(), True);
      Changed := True;
    end;
  end;

  if not Changed then
  begin
    Log('PatchJavaPath: no token found in ' + FileName + ' (already patched?)');
    Result := True;
    Exit;
  end;

  Result := SaveStringsToUTF8FileWithoutBOM(FileName, Lines, False);
  if not Result then
    Log('PatchJavaPath: could not write ' + FileName);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InstanceCfg, LauncherCfg: String;
begin
  if CurStep = ssPostInstall then
  begin
    InstanceCfg := ExpandConstant('{app}\instances\Little Kettle Valley\instance.cfg');
    LauncherCfg := ExpandConstant('{app}\prismlauncher.cfg');

    if not PatchJavaPath(InstanceCfg) then
      MsgBox('Could not finish setting up Java for the game instance.' + #13#10 +
             'Little Kettle Valley will still run -- the launcher will download its own copy of ' +
             'Java the first time you press Play.', mbInformation, MB_OK);

    { The launcher-wide default matters less (the instance pin wins), so a failure here is silent. }
    PatchJavaPath(LauncherCfg);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Instances: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    Instances := ExpandConstant('{app}\instances');
    if DirExists(Instances) then
    begin
      { SuppressibleMsgBox, not MsgBox: a /SILENT uninstall must not block on a dialog, and the
        safe default there is IDNO -- never destroy someone's worlds without them saying so. }
      if SuppressibleMsgBox('Also delete your Little Kettle Valley worlds, mods and downloaded game files?' + #13#10 + #13#10 +
                'Yes  -  remove everything in' + #13#10 + '      ' + ExpandConstant('{app}') + #13#10 + #13#10 +
                'No  -  leave that folder alone (several GB), so reinstalling later picks up right ' +
                'where you left off.',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2, IDNO) = IDYES then
        DelTree(ExpandConstant('{app}'), True, True, True);
    end;
  end;
end;
