# RECON — cross-platform readiness audit of the shipped Prism instance

Scope: `dist/CozyTech/**`, `dist/LittleKettleValley.zip`, `tools/scripts/release.sh`, `docs/INSTALL.md`, `tools/scripts/install_guide_pdf.py`, `media/` (read-only), plus upstream source for Prism Launcher (PreLaunchCommand execution, icon import) and packwiz-installer-bootstrap/packwiz-installer (Java/Kotlin, CLI args, side handling). Sourced from the actual PrismLauncher, packwiz-installer-bootstrap, and packwiz-installer GitHub repos via `gh api`/`gh pr diff`, not from memory.

## 1. What's actually in the shipped instance

```
dist/CozyTech/
├── instance.cfg
├── mmc-pack.json
├── lkv.png                              (128×128 RGBA icon)
└── .minecraft/
    └── packwiz-installer-bootstrap.jar  (98,989 bytes)
```

`dist/LittleKettleValley.zip` (built by `release.sh` via `cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store'`) contains exactly those 5 entries, flat at the zip root (no wrapping folder) — this matches Prism's MultiMC-format import expectations (it locates the instance by finding `instance.cfg`).

**instance.cfg**
```ini
[General]
InstanceType=OneSix
name=Little Kettle Valley
iconKey=lkv
OverrideMemory=true
MinMemAlloc=1024
MaxMemAlloc=3584
OverrideCommands=true
PreLaunchCommand="$INST_JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "https://raw.githubusercontent.com/malloyjoshua/little-kettle-valley/main/pack/pack.toml"
OverrideJavaArgs=true
JvmArgs=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M
```

**mmc-pack.json** — `net.minecraft 1.20.1` + `net.minecraftforge 47.4.10`. No local/absolute paths, nothing OS-specific.

No junk found: `find dist -iname .DS_Store` → empty, `find dist/CozyTech -type l` → no symlinks, no `packwiz.json` or `options.txt` bundled (both are correctly *absent* — see §5).

## 2. PreLaunchCommand — verified against Prism's actual source, not assumption

This was the highest-risk item on the list, and the answer is good news: **it is safe as written, no change needed.**

Traced `launcher/launch/steps/PreLaunchCommand.cpp` (PrismLauncher/PrismLauncher, current main):

```cpp
void PreLaunchCommand::executeTask()
{
    auto cmd = m_parent->substituteVariables(m_command);
    auto args = QProcess::splitCommand(cmd);
    const QString program = args.takeFirst();
    m_process.start(program, args);
}
```

- **`$INST_JAVA` is substituted by Prism itself**, in Qt/C++, before any tokenizing happens. From `MinecraftInstance.cpp`: `out.insert("INST_JAVA", QDir::toNativeSeparators(QDir(settings()->get("JavaPath").toString()).absolutePath()));` — it becomes the absolute, native-separator path to the Java binary Prism picked for the instance (backslashes on Windows). The shell/cmd string `$VAR` syntax is irrelevant — Prism does the substitution itself, not a shell.
- **No shell is ever invoked.** `QProcess::splitCommand()` is Qt's own cross-platform tokenizer (handles the `"..."` quoting the same way on Windows/macOS/Linux); the result is exec'd directly via `QProcess::start(program, args)`, which calls `CreateProcess` on Windows and `fork`/`exec` on POSIX — **not** `cmd.exe /C ...` and not `/bin/sh -c ...`. So `"$INST_JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "URL"` is parsed once, uniformly, on every OS.
- This exact pattern (`"$INST_JAVA" -jar packwiz-installer-bootstrap.jar link`) is Prism's own test fixture in `tests/INIFile_test.cpp` — it's the documented, supported form.
- Working directory: `MinecraftInstance.cpp` sets `step->setWorkingDirectory(gameRoot())` for the pre-launch step, i.e. the instance's `.minecraft/` folder — so the bare relative path `packwiz-installer-bootstrap.jar` (no `./` or path prefix) resolves correctly on every OS, matching where the jar actually sits in the shipped tree.

**Verdict: no quoting/path change needed for Windows.** This is the one item I'd have guessed was broken and it isn't — confirmed from source, not assumed.

## 3. Icon (`iconKey=lkv`, `lkv.png`) — also verified fine, with one version floor to be aware of

Traced `launcher/icons/IconUtils.cpp` + `InstanceImportTask.cpp` (`processMultiMC()`):

```cpp
QString findBestIconIn(const QString& folder, const QString& iconKey) {
    // iterates files in `folder` (non-recursive), returns the file whose
    // completeBaseName() == iconKey (case-sensitive) and whose suffix is
    // one of: svg png ico gif jpg jpeg webp
}
```
`processMultiMC()` calls `installIcon(instance.instanceRoot(), instance.iconKey())`, which uses exactly that lookup against the instance's root folder and installs the match into Prism's global icon store under the iconKey name.

- `iconKey=lkv` + a file literally named `lkv.png` sitting at the instance root (not inside `.minecraft/`) is exactly the pattern this looks for. `completeBaseName()` on `lkv.png` is `lkv` — exact match, valid suffix. **This will auto-import correctly.**
- **Caveat: this auto-import only exists as of PR [#3752](https://github.com/PrismLauncher/PrismLauncher/pull/3752) ("feat: search for pack icon in the actual file", fixes #876), merged 2025-05-10, shipped in Prism **10.0.0** (released 2026-01-06).** Before that, Prism silently ignored a bundled icon and fell back to the default dirt-block icon — no error, just the wrong picture. `docs/INSTALL.md` step 1 sends friends to `prismlauncher.org/download` for a fresh install, and current latest is **11.1.0** (released today), so anyone following the guide today is well past the fix. This is a soft floor worth knowing about, not a bug to fix — no action needed unless a friend is somehow on a Prism build older than 10.0.0.
- Minor, low-priority edge case (not platform-specific): `installIcon()` does `if (iconList->iconFileExists(instIcon)) iconList->deleteIcon(instIcon);` before installing — if a friend already happens to have an icon named exactly `lkv` installed in their Prism (e.g. from an unrelated pack), the import silently overwrites it. Not worth guarding against; flagging only for completeness.
- The zip does include the icon (confirmed in the `unzip -l` listing above) — nothing to add there.

## 4. packwiz-installer-bootstrap.jar and packwiz-installer — verified plain JVM code, no OS branches

Pulled the actual source (`gh api .../git/blobs`, not docs):

- **Language confirmed via GitHub API (`.language` field): Java** for `packwiz-installer-bootstrap` (98,989-byte jar matches). The chainloaded `packwiz-installer` itself is Kotlin, also JVM bytecode.
- `Main.java` → `Bootstrap.init(args)` → `parseOptions()` (Apache Commons CLI) → `doUpdate()` (checks GitHub Releases API for a newer `packwiz-installer.jar`, downloads via `java.net.URL`/`java.nio.file.Files.copy`) → `LoadJAR.start(args, jarPath)`.
- **`LoadJAR.java` loads the real installer via `URLClassLoader` + reflection, in the same JVM process** — no `ProcessBuilder`, no subprocess spawn, no shelling out. There is nothing in this bootstrap that could behave differently by OS beyond what the JVM itself already normalizes (file paths via `java.nio.file.Paths`, HTTP via `java.net.URL`). No platform-specific code paths found.
- **Arg handling confirmed, matches our exact command line:**
  - `-g` → Bootstrap's own `"g"/"no-gui"` option, disables the Swing UI (`useGUI = false`) so no window pops up on any OS during launch — this also gets forwarded through to the chainloaded installer, which independently checks `no-gui` too (`Main.kt`: `guiEnabled = !GraphicsEnvironment.isHeadless()`, then overridden by `-g`). Passing `-g` explicitly is the right call regardless of platform's default headless-ness.
  - `-s client` and the trailing pack-URL are **not** bootstrap options at all — `Bootstrap`'s `filterArgs()` strips only its own known flags from what it feeds its own Commons-CLI parser, but passes the **full original `args` array** through to the chainloaded installer. In `packwiz-installer`'s `Main.kt`, `-s`/`--side` maps to `Side.from(it)`, and `"client"` is a recognized value (`Side.CLIENT`) — confirmed by reading the actual parser, not the docs page (which loaded as JS chrome with no body text via WebFetch).
  - The pack URL is matched against `^https?://` and parsed as an `HttpUrlPath` via OkHttp — a plain HTTPS GET, nothing Windows/macOS-specific (no `file://` UNC-path handling invoked since our URL is `https://raw.githubusercontent.com/...`).
- **Verdict: no platform-specific code paths in either the bootstrap or the installer for the flags we use. Safe on Windows as-is.**

## 5. Things that are correctly *absent* (don't add them)

- **No `packwiz.json`** shipped — that's the installer's own state/manifest file, generated on first run in `.minecraft/`. Shipping one baked from Josh's Mac would just get overwritten (harmless) but could theoretically confuse the diffing logic on first run if it referenced stale hashes; better it doesn't exist yet.
- **No `options.txt`** shipped — correct. `options.txt` can carry keybinds using OS/keyboard-layout-specific scancodes (`key_key.forward:key.keyboard.w` is fine, but raw scancode-only bindings on some peripherals or non-QWERTY layouts don't round-trip identically across OSes). Not shipping one means every friend gets Minecraft's own per-OS defaults on first launch instead of inheriting Josh's Mac keybinds. Correct call — leave it out.
- **No symlinks, no `.DS_Store`** currently present anywhere under `dist/CozyTech` (confirmed via `find`).

## 6. One real, if currently dormant, gap: `release.sh`'s `.DS_Store` exclude is fragile

```sh
(cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store')
```

`zip -x PATTERN` without a wildcard only excludes an entry whose *relative path from the zip root* literally equals `.DS_Store` — i.e. one sitting directly in `dist/CozyTech/`. It will **not** catch a `.DS_Store` that Finder drops inside `dist/CozyTech/.minecraft/` (or any future subfolder) — that would match `-x '.minecraft/.DS_Store'`, not `-x '.DS_Store'`, and would ship silently. Right now there are none anywhere in the tree, so nothing is currently leaking — but the exclude pattern doesn't actually protect the nested case it's presumably meant to guard against.

**Fix for `installers/` tooling to apply:** change the exclude to also catch nested Finder junk, e.g. `-x '.DS_Store' -x '*/.DS_Store' -x '__MACOSX/*'` (the last guards against a future `zip`/`unzip -x` combo on a different Mac leaving a resource-fork sidecar). Low priority since it's dormant, but cheap to fix while touching `release.sh`.

## 7. Summary — concrete changes for the installers work

| Area | Finding | Action needed |
|---|---|---|
| `PreLaunchCommand` quoting/`$INST_JAVA` | Verified safe on Windows from Prism source — no shell involved, Prism substitutes the var itself, `QProcess::start` execs directly | **None.** Do not "fix" this — it's already correct. |
| `iconKey=lkv` / `lkv.png` | Verified auto-imports correctly on Prism ≥10.0.0 (May 2025 fix); current download is 11.1.0 | **None**, informational only — note the 10.0.0 floor in case a friend is on a very old Prism build. |
| `packwiz-installer-bootstrap.jar` / chainloaded installer | Confirmed plain JVM (Java bootstrap, Kotlin installer), in-process `URLClassLoader`, no subprocess/OS branching; `-g -s client <url>` all confirmed to parse and route correctly | **None.** |
| Junk files / symlinks in `dist/CozyTech` | None present currently | **None** — just don't introduce any. |
| `packwiz.json` / `options.txt` | Correctly not shipped | **None** — keep it that way; don't let a future build step accidentally bundle a generated `packwiz.json` or a Mac `options.txt`. |
| `release.sh` `.DS_Store` exclude | `-x '.DS_Store'` only matches a root-level file, won't catch nested ones (currently dormant, no live leak) | **Recommended:** broaden to `-x '.DS_Store' -x '*/.DS_Store' -x '__MACOSX/*'` when `release.sh` is next touched. |
| Memory settings (`MinMemAlloc=1024`/`MaxMemAlloc=3584`) | Portable ints, no OS issue, but numerically inconsistent with `docs/INSTALL.md`'s guidance to raise to 3072/3584/4096 by RAM tier | Not a cross-platform bug — flagging only since it's adjacent; no change required by this audit's scope. |

**Bottom line:** the instance itself was already built correctly for cross-platform (specifically Windows) import — the PreLaunchCommand quoting, the `$INST_JAVA` substitution path, the icon pickup, and the bootstrap jar's argument handling all check out against the real upstream source, not just plausible-sounding assumptions. The only actionable item from this recon is the `release.sh` `.DS_Store` exclude pattern, which is a minor robustness fix, not a fire to put out. The installers work (`installers/`, packaging, docs) can proceed without needing to touch `dist/CozyTech`'s file contents.
