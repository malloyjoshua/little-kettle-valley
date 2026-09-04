; Little Kettle Valley - Windows one-click installer
; ---------------------------------------------------
; Packages the tree produced by installers/windows/stage.py:
;   Prism Launcher 11.1.0 (MinGW-w64 portable, needs no VC++ Redistributable)
;   + portable.txt          -> the install folder is Prism's whole data root
;   + jre/                  -> Eclipse Temurin 17 JRE, so no "install Java first" step
;   + instances/Little Kettle Valley  -> the pack instance, self-updating via packwiz on every launch
;   + prismlauncher.cfg     -> pre-seeded so no first-run wizard page appears except Microsoft login
;
; Two values in those config files cannot be known until install time, so stage.py leaves tokens
; and the [Code] section below substitutes them:
;   @@JAVA_PATH@@ -> the absolute path of the bundled JRE (the user picks the install folder)
;   @@MAX_MEM@@   -> a heap size read off this machine's physical RAM, 3072 / 3584 / 4096 MB
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
  MaxMemToken = '@@MAX_MEM@@';

  { Heap sizes in MB, by physical RAM. These are the numbers docs/INSTALL.md quotes, and they
    exist because the game needs roughly 1 GB on top of whatever is allocated: hand an 8 GB
    laptop the 3584 that a 16 GB desktop wants and it swaps. MinMemAlloc stays 1024 everywhere. }
  HeapSmallMB = 3072;   { under 12 GB }
  HeapMediumMB = 3584;  { 12-24 GB }
  HeapLargeMB = 4096;   { over 24 GB }

  { sizeof(MEMORYSTATUSEX): 4 + 4 + 7*8. Hard-coded because Pascal Script has no SizeOf() for
    records. Getting it wrong makes GlobalMemoryStatusEx fail outright rather than lie, and the
    CI smoke test would then see the fallback tier instead of the runner's real one. }
  MemoryStatusExSize = 64;

type
  { MEMORYSTATUSEX, winbase.h. Two DWORDs then seven DWORDLONGs. 4 + 4 already leaves the first
    64-bit field on an 8-byte boundary, so the C struct has no interior padding -- which means it
    matches Pascal Script's packed record layout byte for byte, at 64 bytes. Do not reorder. }
  TMemoryStatusEx = record
    dwLength: Cardinal;
    dwMemoryLoad: Cardinal;
    ullTotalPhys: Int64;
    ullAvailPhys: Int64;
    ullTotalPageFile: Int64;
    ullAvailPageFile: Int64;
    ullTotalVirtual: Int64;
    ullAvailVirtual: Int64;
    ullAvailExtendedVirtual: Int64;
  end;

{ Returns 0 on failure. Declared with an Integer result rather than Boolean: the Win32 BOOL is a
  4-byte int and reading it as a 1-byte Pascal Boolean is a needless gamble. }
function GlobalMemoryStatusEx(var lpBuffer: TMemoryStatusEx): Integer;
  external 'GlobalMemoryStatusEx@kernel32.dll stdcall';

var
  CachedMaxMemMB: Integer;  { 0 = not worked out yet }

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
  { parseOldFileFormat() also truncates a value at the first unescaped '#' (it treats it as a
    comment) and unescape() turns '\#' back into '#'. Windows does allow '#' in a user name, so
    escape it rather than silently handing Prism a truncated path. }
  StringChangeEx(P, '#', '\#', True);
  Result := P;
end;

{ Physical RAM in whole GB, rounded up; 0 if it cannot be read.

  Rounding up is deliberate. Windows reports what is left after the firmware takes its cut, so a
  16 GB machine says about 15.9 GB and an 8 GB one about 7.9 -- rounding up recovers the number
  printed on the box, which is what the tier boundaries are written in terms of. }
function PhysicalRamGB(): Integer;
var
  Status: TMemoryStatusEx;
  MB: Int64;
begin
  Result := 0;
  try
    Status.dwLength := MemoryStatusExSize;
    if GlobalMemoryStatusEx(Status) = 0 then
    begin
      Log('PhysicalRamGB: GlobalMemoryStatusEx returned FALSE');
      Exit;
    end;
    MB := Status.ullTotalPhys div 1048576;
    { A wrong record layout would show up here as a wild number rather than a crash, so refuse
      anything outside "half a gigabyte to four terabytes" and fall back instead of acting on it. }
    if (MB < 512) or (MB > 4194304) then
    begin
      Log('PhysicalRamGB: implausible ullTotalPhys (' + IntToStr(MB) + ' MB) -- ignoring');
      Exit;
    end;
    Result := (MB + 1023) div 1024;
    Log('PhysicalRamGB: ' + IntToStr(MB) + ' MB physical -> ' + IntToStr(Result) + ' GB');
  except
    Log('PhysicalRamGB: exception while calling GlobalMemoryStatusEx');
    Result := 0;
  end;
end;

{ MaxMemAlloc for this machine. Worked out once and remembered, so both config files agree. }
function ChosenMaxMemMB(): Integer;
var
  GB: Integer;
begin
  if CachedMaxMemMB > 0 then
  begin
    Result := CachedMaxMemMB;
    Exit;
  end;

  { /LKVRAMGB=<n> pretends the machine has n GB. It exists so CI can exercise the 3072 and 4096
    branches on a 16 GB runner; it is not documented for players. }
  GB := StrToIntDef(ExpandConstant('{param:LKVRAMGB|0}'), 0);
  if GB > 0 then
    Log('ChosenMaxMemMB: /LKVRAMGB override, pretending ' + IntToStr(GB) + ' GB')
  else
    GB := PhysicalRamGB();

  if GB <= 0 then
  begin
    { Could not read the RAM at all. Fall back to the middle tier -- the value this installer
      baked in unconditionally before it learned to ask. }
    Log('ChosenMaxMemMB: RAM unknown, falling back to ' + IntToStr(HeapMediumMB) + ' MB');
    CachedMaxMemMB := HeapMediumMB;
  end
  else
  begin
    if GB < 12 then
      CachedMaxMemMB := HeapSmallMB
    else if GB <= 24 then
      CachedMaxMemMB := HeapMediumMB
    else
      CachedMaxMemMB := HeapLargeMB;
    Log('ChosenMaxMemMB: ' + IntToStr(GB) + ' GB -> MaxMemAlloc=' + IntToStr(CachedMaxMemMB));
  end;

  Result := CachedMaxMemMB;
end;

{ Replace the placeholder tokens in one config file, preserving every other line verbatim.
  Written back as UTF-8 without a BOM: Prism reads these as UTF-8, and a BOM would end up glued to
  the first key name. The install path can contain non-ASCII characters (a friend's user name), so
  an ANSI write would corrupt it. }
function PatchConfig(const FileName: String): Boolean;
var
  Lines: TArrayOfString;
  I: Integer;
  JavaPath, MaxMem: String;
  Changed: Boolean;
begin
  Result := False;
  if not FileExists(FileName) then
  begin
    Log('PatchConfig: missing ' + FileName);
    Exit;
  end;
  if not LoadStringsFromFile(FileName, Lines) then
  begin
    Log('PatchConfig: could not read ' + FileName);
    Exit;
  end;

  JavaPath := BundledJavaPath();
  MaxMem := IntToStr(ChosenMaxMemMB());

  Changed := False;
  for I := 0 to GetArrayLength(Lines) - 1 do
  begin
    if Pos(JavaPathToken, Lines[I]) > 0 then
    begin
      StringChangeEx(Lines[I], JavaPathToken, JavaPath, True);
      Changed := True;
    end;
    if Pos(MaxMemToken, Lines[I]) > 0 then
    begin
      StringChangeEx(Lines[I], MaxMemToken, MaxMem, True);
      Changed := True;
    end;
  end;

  if not Changed then
  begin
    Log('PatchConfig: no tokens found in ' + FileName + ' (already patched?)');
    Result := True;
    Exit;
  end;

  Result := SaveStringsToUTF8FileWithoutBOM(FileName, Lines, False);
  if not Result then
    Log('PatchConfig: could not write ' + FileName);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  InstanceCfg, LauncherCfg: String;
begin
  if CurStep = ssPostInstall then
  begin
    InstanceCfg := ExpandConstant('{app}\instances\Little Kettle Valley\instance.cfg');
    LauncherCfg := ExpandConstant('{app}\prismlauncher.cfg');

    if not PatchConfig(InstanceCfg) then
      MsgBox('Could not finish setting up Java and memory for the game instance.' + #13#10 +
             'Little Kettle Valley will still run -- the launcher will download its own copy of ' +
             'Java the first time you press Play. If the game runs out of memory, set it by hand: ' +
             'select the instance, Edit, Settings, Memory.', mbInformation, MB_OK);

    { The launcher-wide defaults matter less (the instance pin wins), so a failure here is silent. }
    PatchConfig(LauncherCfg);
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
