# Prism Launcher recon — for the CozyTech installer build

All facts below were established today (2026-09-03) directly against Prism Launcher release
**11.1.0** (published 2026-09-03T09:23:15Z, stable, not a pre-release) — either by downloading
and hashing the actual release assets, running `codesign`/`spctl` on the real signed app, or by
reading the source at git tag `11.1.0` (commit `ea87ffcfbc22c3bb37c75b97160fe836aeb130be`,
cloned read-only into a scratch dir, not into this repo).

Source repo: https://github.com/PrismLauncher/PrismLauncher
Release: https://github.com/PrismLauncher/PrismLauncher/releases/tag/11.1.0
Download page (asset descriptions): https://prismlauncher.org/download/windows

---

## 1. Release assets — tag, names, sha256

Tag: **`11.1.0`**. Confirmed via GitHub Releases API (`prerelease: false`, `draft: false`).

### Windows x64 — MinGW vs MSVC (which needs no VC++ Redistributable)

The official download page (https://prismlauncher.org/download/windows) states outright, under
"Advanced Windows Install Options → MinGW":

> "These builds are built with MinGW and do not require the Visual C++ Redistributable to be
> installed on your system. They require Windows 10/11 64bit. **These builds are less tested
> than the MSVC builds.**"

That sentence only exists for the MinGW builds — the MSVC builds (the page's default/primary
recommendation, red "Installer" button) carry no such disclaimer, meaning they *do* need the
redistributable (standard for MSVC-linked Qt/C++ binaries; this is also just how every MSVC-built
Windows app behaves). **For a zero-prerequisite double-click experience, ship the MinGW-w64
build.**

| Asset | Purpose | Size | sha256 (computed locally after download) |
|---|---|---|---|
| `PrismLauncher-Windows-MinGW-w64-Portable-11.1.0.zip` | **No VC++ Redist needed.** Portable x64 zip. | 43,926,838 B | `2bf5e879ea1c3f6a1aaaa43539667ce296308abf3e6a984d5cc4c48bfe3c431c` |
| `PrismLauncher-Windows-MinGW-w64-Setup-11.1.0.exe` | Same, installer form | 44,742,088 B | not downloaded (portable zip is what CozyTech ships) |
| `PrismLauncher-Windows-MSVC-Portable-11.1.0.zip` | Needs VC++ Redist. Portable x64 zip (site's primary/default build). | 20,395,945 B | `4902ef9e8f980068e91e7bedea99474bce795d677beb152555b35fe955490fd4` |
| `PrismLauncher-Windows-MSVC-Setup-11.1.0.exe` | Needs VC++ Redist. Installer form | 23,964,776 B | not downloaded |

GitHub does **not** publish an official `sha256sums.txt` for this release (checked the full
21-asset list — none present). The hashes above are what I computed myself, right after
downloading straight from the `github.com/.../releases/download/11.1.0/...` URLs, so they're an
exact record of the specific bytes at that URL today, not a third-party-attested checksum. If the
release script re-downloads at build time it should compute+compare against these same values
(or re-pin fresh ones if PrismLauncher ever republishes the tag's assets).

### macOS dmg

| Asset | Size | sha256 |
|---|---|---|
| `PrismLauncher-macOS-11.1.0.dmg` | 42,831,961 B | `dd34e829abdc22b60a713a45f8e013148ab8ef5dee4531fa4030844f14bfac3b` |

This is a **universal** dmg (see §2 — Mach-O has both `x86_64` and `arm64` slices), so there's no
separate arm64-only asset to choose between.

---

## 2. macOS dmg — signing & notarization (verified by actually mounting it)

```
$ hdiutil attach -nobrowse -readonly PrismLauncher-macOS-11.1.0.dmg
...mounted at /Volumes/Prism Launcher ea87ffc

$ codesign -dv --verbose=2 "/Volumes/Prism Launcher ea87ffc/Prism Launcher.app"
Executable=.../Prism Launcher.app/Contents/MacOS/prismlauncher
Identifier=org.prismlauncher.PrismLauncher
Format=app bundle with Mach-O universal (x86_64 arm64)
CodeDirectory v=20500 size=32651 flags=0x10000(runtime) hashes=1009+7 location=embedded
Authority=Developer ID Application: Sefa Eyeoglu (MZM5U2NVNH)
Authority=Developer ID Certification Authority
Authority=Apple Root CA
Timestamp=Sep 3, 2026 at 2:12:29 AM
Notarization Ticket=stapled
TeamIdentifier=MZM5U2NVNH
Runtime Version=26.5.0

$ spctl -a -vv -t exec "/Volumes/Prism Launcher ea87ffc/Prism Launcher.app"
/Volumes/Prism Launcher ea87ffc/Prism Launcher.app: accepted
source=Notarized Developer ID
origin=Developer ID Application: Sefa Eyeoglu (MZM5U2NVNH)

$ hdiutil detach "/Volumes/Prism Launcher ea87ffc"
"disk4" ejected.
```

**Answer: yes on both counts.** Developer ID Application signed (team `MZM5U2NVNH`, Sefa Eyeoglu
— the Prism Launcher project lead), hardened runtime on, and the notarization ticket is stapled
to the app bundle itself — Gatekeeper accepts it offline with no network check needed. A user
just double-clicks it; no "unidentified developer" warning, no right-click-Open workaround
needed. Universal binary, so this single dmg covers both Intel and Apple Silicon Macs — no
arm64-only variant to worry about. Dmg was detached cleanly after the check; nothing left mounted.

---

## 3. Windows portable mode — where it looks for `portable.txt`, and what that does

Source: `launcher/Application.cpp`, inside `Application::Application()`, lines ~362–416
(https://github.com/PrismLauncher/PrismLauncher/blob/11.1.0/launcher/Application.cpp#L362-L416):

```cpp
QString binPath = applicationDirPath();
{
    // Root path is used for updates and portable data
#if defined(Q_OS_LINUX) || defined(Q_OS_FREEBSD) || defined(Q_OS_OPENBSD)
    QDir foo(FS::PathCombine(binPath, ".."));
    m_rootPath = foo.absolutePath();
#elif defined(Q_OS_WIN32)
    m_rootPath = binPath;                      // <-- Windows: root = the exe's own folder
#elif defined(Q_OS_MAC)
    QDir foo(FS::PathCombine(binPath, "../.."));
    m_rootPath = foo.absolutePath();
#endif
}
...
#ifndef Q_OS_MACOS
    if (auto portableUserData = FS::PathCombine(m_rootPath, "UserData"); QDir(portableUserData).exists()) {
        dataPath = portableUserData;
        adjustedBy = "Portable user data path";
        m_portable = true;
    } else if (QFile::exists(FS::PathCombine(m_rootPath, "portable.txt"))) {
        dataPath = m_rootPath;
        adjustedBy = "Portable data path";
        m_portable = true;
    }
#endif
```

Facts this gives us, exactly:

- On Windows, `m_rootPath` is simply the folder the .exe lives in (`applicationDirPath()`,
  no `..`). That's also where it looks for `portable.txt`.
- Two portable triggers, checked in this order:
  1. A **`UserData` subfolder** next to the exe — if that exists, it's used *as* the data dir
     (instances/, accounts.json, prismlauncher.cfg all go inside `UserData\`), portable mode on.
  2. Otherwise, a bare **`portable.txt`** file next to the exe — if that exists, the data dir
     becomes the **exe's own folder itself** (not a subfolder): `instances\`, `icons\`,
     `prismlauncher.cfg`, `accounts.json` etc. all sit right alongside `PrismLauncher.exe`.
  3. If neither exists, it falls back to the normal per-user AppData location and is **not**
     portable.
- This `#ifndef Q_OS_MACOS` guard means the exact same portable.txt/UserData logic also applies
  on **Linux**, not just Windows — macOS is the one platform that never goes portable.
- Right after this, the code does `QDir::setCurrent(dataPath)` (line ~430) — so once portable
  mode is picked, the launcher's **current working directory becomes the data dir** for the rest
  of the run. That matters for §6 (relative `JavaPath` values resolve against this).

**For CozyTech's Windows portable zip: ship an empty `portable.txt` file next to
`prismlauncher.exe`** (or ship a pre-populated `UserData\` folder directly — equivalent, and lets
you drop `instances/`, `prismlauncher.cfg`, etc. straight into `UserData\` instead of the zip
root). Either way, `instances/`, `icons/`, and `prismlauncher.cfg` all resolve relative to that
same root, confirmed by the same code path (`m_dataPath = dataPath` is the one path everything
else — instance manager, settings, icon loader — reads from).

---

## 4. First-run setup wizard — exact skip conditions

Source: `Application::createSetupWizard()`, `launcher/Application.cpp` lines 1197–1267
(https://github.com/PrismLauncher/PrismLauncher/blob/11.1.0/launcher/Application.cpp#L1197-L1267),
plus the individual page files in `launcher/ui/setupwizard/`.

The wizard only appears at all if `wizardRequired` (the OR of every page's own "is this needed"
flag) is true. Pages are added to the `QWizard` in this fixed order, each independently gated:

| # | Page (source file) | Shown when… (exact condition from source) | Settings key(s) to pre-seed in `prismlauncher.cfg` to force-skip it |
|---|---|---|---|
| 1 | **Language** — `LanguageWizardPage` | `settings()->get("Language").toString().isEmpty()` | `Language=en_US` (any non-empty valid locale id) |
| 2 | **Java** (manual picker) — `JavaWizardPage` | `javaRequired` is true. `javaRequired` is computed as: **false** if `AutomaticJavaDownload=true` (and the build has the Java-downloader compiled in, which it does — see below); else **false** if `IgnoreJavaWizard=true`; else **false** only if `QHostInfo::localHostName()` still equals the stored `LastHostname` *and* the stored `JavaPath` resolves to a real executable (`FS::ResolveExecutable`) — otherwise **true**. | Simplest: `AutomaticJavaDownload=true` (see row 3 too — this one flag skips *both* Java pages). Alternative: `IgnoreJavaWizard=true`. |
| 3 | **Auto-Java prompt** — `AutoJavaWizardPage` | Only considered if page 2 was *not* required. Shown when: build has Java-downloader compiled in AND `AutomaticJavaDownload=false` AND `AutomaticJavaSwitch=false` AND `UserAskedAboutAutomaticJavaDownload=false`. | `AutomaticJavaDownload=true` (also satisfies row 2), or `UserAskedAboutAutomaticJavaDownload=true`. |
| 4 | **Paste-service intervention** — `PasteWizardPage` | `settings()->get("PastebinURL") != ""` — i.e. shown when a **non-empty** legacy `PastebinURL` value is present (this page exists to migrate users off an old built-in pastebin default). | `PastebinURL=` (empty string) |
| 5 | **Theme** — `ThemeWizardPage` | `!ThemeManager::isValidApplicationTheme(ApplicationTheme)` OR `!ThemeManager::isValidIconTheme(IconTheme)`. Valid app-theme ids always include the built-ins `"dark"` and `"bright"` (platform-independent — see `DarkTheme::id()`/`BrightTheme::id()`) plus per-platform Qt style names. Valid icon-theme ids are the built-in set `{pe_colored, pe_light, pe_dark, pe_blue, breeze_light, breeze_dark, OSX, iOS, flat, flat_white, multimc}` (`ThemeManager.h`, `builtinIcons`). | `ApplicationTheme=dark` (or `bright` — both are guaranteed valid on every platform) and `IconTheme=pe_colored` |
| 6 | **Login (MSA)** — `LoginWizardPage` | `!accounts->anyAccountIsValid() && (capabilities() & Application::SupportsMSA)` | **Cannot be skipped by config alone.** It only goes away once a real, valid Microsoft account exists in `accounts.json` — there's no settings flag to suppress it, by design (Prism won't let you silently pre-seed someone's Microsoft login). Every fresh CozyTech user will see this page once, the first time they launch, until they sign in. Plan the onboarding doc around that. |

Practical `prismlauncher.cfg` block that skips every page *except* the unavoidable login page:

```ini
Language=en_US
AutomaticJavaDownload=true
UserAskedAboutAutomaticJavaDownload=true
PastebinURL=
ApplicationTheme=dark
IconTheme=pe_colored
```

Note on row 2/3: `AutomaticJavaDownload` **defaults to `true` already** on a totally fresh config
(`Application.cpp` line ~751: `auto defaultEnableAutoJava = m_settings->get("JavaPath").toString().isEmpty();` then
`registerSetting("AutomaticJavaDownload", defaultEnableAutoJava)` — i.e. if you don't pre-set a
`JavaPath`, it's auto-true out of the box). Setting it explicitly is just belt-and-suspenders and
makes the intent obvious in the shipped cfg. This also means the Java-downloader must be compiled
into the binary for that shortcut to work — see §6, it is on both the Windows and macOS official
builds (only Linux/BSD packages ship it off by default, per `CMakeLists.txt` line 231:
`if(UNIX AND NOT APPLE) set(Launcher_ENABLE_JAVA_DOWNLOADER_DEFAULT OFF) endif()`).

---

## 5. CLI: `-l/--launch`, `-I/--import`, and what happens with no account

Source: `launcher/Application.cpp` lines 313–352 (option table + parsing) and
`LaunchController::decideAccount()` (`launcher/LaunchController.cpp` lines 79–127).

Confirmed option table (exact flags):

```cpp
parser.addOptions(
    { { { "d", "dir" }, "Use a custom path as application root (use '.' for current directory)", "directory" },
      { { "l", "launch" }, "Launch the specified instance (by instance ID)", "instance" },
      { { "s", "server" }, "Join the specified server on launch (only valid in combination with --launch)", "address" },
      { { "w", "world" }, "Join the specified world on launch (only valid in combination with --launch)", "world" },
      { { "a", "profile" }, "Use the account specified by its profile name (only valid in combination with --launch)", "profile" },
      { { "o", "offline" }, "Launch offline, with given player name (only valid in combination with --launch)", "offline" },
      { "alive", "Write a small 'PrismLauncher_alive.txt' file after the launcher starts" },
      { "show-window", "Show the main launcher window (useful in combination with --launch)" },
      { { "I", "import" }, "Import instance or resource from specified local path or URL", "url" },
      { "show", "Opens the window for the specified instance (by instance ID)", "show" } });
parser.addPositionalArgument("URL", "Import the resource(s) at the given URL(s) (same as -I / --import)", "[URL...]");
```

So yes to both:
- `-l/--launch <instance id>` — launches that instance by its **id** (the instance folder name,
  not its display name — confirmed by `instances()->getInstanceById(m_instanceIdToLaunch)` at
  line 1326). Combine with `--show-window` if you want the main window visible during launch
  (otherwise it launches headless-ish, straight to the Minecraft process).
- `-I/--import <path-or-url>` — and bare positional args are treated identically (line 350-352:
  `for (auto url : parser.positionalArguments()) m_urlsToImport.append(normalizeImportUrl(url));`),
  so `prismlauncher.exe C:\path\to\SomeInstance.zip` works exactly like
  `prismlauncher.exe --import C:\path\to\SomeInstance.zip`.

**`--launch` with no account logged in:** it does **not** silently fail or silently launch
offline. `LaunchController::decideAccount()` (lines 95-111) checks
`accounts->anyAccountIsValid()`; if false, it pops a **blocking modal dialog**:

> "No Accounts" — "In order to play Minecraft, you must have at least one Microsoft account which
> owns Minecraft logged in. Would you like to open the account manager to add an account now?"
> [Yes] [No]

Yes opens the account-manager settings page; No just aborts that launch attempt (`return;` at
line 109, no account selected). Either way this needs a human at the keyboard — **`--launch`
cannot be used for a fully unattended/scripted launch on a machine with zero accounts
configured.** Relevant for the release script only if it ever tries to smoke-test the built
instance via CLI — it'll need at least one account (even an Offline/cracked-style account counts,
per `AccountType::Offline` checks lower in the same file) present in `accounts.json` first, or
expect a modal to appear.

---

## 6. Instance-level Java pin, and Prism's auto-download-Java

Source: `launcher/minecraft/MinecraftInstance.cpp`, `loadSpecificSettings()`, lines 180-201
(https://github.com/PrismLauncher/PrismLauncher/blob/11.1.0/launcher/minecraft/MinecraftInstance.cpp#L180-L201):

```cpp
auto locationOverride = m_settings->registerSetting("OverrideJavaLocation", false);
...
m_settings->registerOverride(global_settings->getSetting("JavaPath"), locationOverride);
```

- **`instance.cfg` key: `OverrideJavaLocation=true`** turns on the per-instance override.
- **`instance.cfg` key: `JavaPath=<path>`** is then the actual Java binary path used for that
  instance (it "overrides" the global `JavaPath` setting only when `OverrideJavaLocation=true` is
  also set — without that flag, the instance just inherits whatever Java the global settings /
  auto-download picked).
- **Does `JavaPath` need to be absolute?** Not strictly enforced by the resolver — `ResolveExecutable()`
  (`launcher/FileSystem.cpp` lines 790-803):
  ```cpp
  QString ResolveExecutable(QString path) {
      if (path.isEmpty()) return QString();
      if (!path.contains('/')) {
          path = QStandardPaths::findExecutable(path);   // bare "java" -> looked up on PATH
      }
      QFileInfo pathInfo(path);
      if (!pathInfo.exists() || !pathInfo.isExecutable()) return QString();
      return pathInfo.absoluteFilePath();
  }
  ```
  A path containing a `/` is used as-is and resolved via `QFileInfo` against the **current
  working directory** — and recall from §3 that in portable mode the CWD is set to the data dir
  right at startup. So a relative `JavaPath` *can* work in the portable build, but it's fragile
  (depends on nobody launching the exe from a different CWD, e.g. via some odd shortcut or when
  invoked with `-l` from a script in a different directory). **Recommendation for the release
  script: always write an absolute `JavaPath`** — don't rely on the relative-path CWD behavior.

- **Does Prism 8+ auto-download Java if none is configured?** Yes — this is the
  `AutomaticJavaDownload` setting (global, `launcher/Application.cpp` line 753) plus
  `AutoInstallJava` task (`launcher/minecraft/launch/AutoInstallJava.cpp` line 71:
  `if (!APPLICATION->settings()->get("AutomaticJavaDownload").toBool()) { ... }` — the task
  no-ops/skips when the flag is off, i.e. runs and fetches a matching Java runtime automatically
  when it's on). It's compiled in (`Launcher_ENABLE_JAVA_DOWNLOADER`, `CMakeLists.txt` line 227,
  `ON` by default) on **both Windows and macOS official builds** — only Linux/BSD distro packages
  default it off (line 231-233, because they can't guarantee ABI compatibility of a downloaded
  JRE across every distro). Combined with the default-true behavior noted in §4, a totally fresh
  CozyTech instance with no `JavaPath` set and no `instance.cfg` override will just download the
  right Java automatically the first time someone hits Launch — no manual "install Java first"
  step needed for the friends' build.

---

## 7. Drag-and-drop import onto the main window (all platforms, incl. macOS)

Source: `launcher/ui/instanceview/InstanceView.cpp` `dropEvent()`, lines 625-669
(https://github.com/PrismLauncher/PrismLauncher/blob/11.1.0/launcher/ui/instanceview/InstanceView.cpp#L625-L669):

```cpp
void InstanceView::dropEvent(QDropEvent* event) {
    ...
    // files dropped from outside?
    if (mimedata->hasUrls()) {
        auto urls = mimedata->urls();
        event->accept();
        emit droppedURLs(urls);
    }
}
```

`droppedURLs` is wired in `launcher/ui/MainWindow.cpp` line 323:
`connect(view, &InstanceView::droppedURLs, this, &MainWindow::processURLs, Qt::QueuedConnection);`
— `MainWindow::processURLs` (line 930) is the same code path that handles `--import`/positional
CLI args and OS "open with" file events, so it understands instance zips, modpack zips, .mrpack,
etc.

`InstanceView` is the shared Qt widget used for the main instance grid on every platform Prism
ships for (it's not platform-gated code) — **so yes, dragging an instance zip onto the main
window works identically on macOS.** No macOS-specific drag-drop path exists or is needed; it's
the same `InstanceView`/`MainWindow` pair as Windows/Linux.

---

## 8. macOS data directory

Source: `launcher/Application.cpp` line 399 (the non-portable data-path branch, which on macOS is
the *only* branch — see §3, the portable-mode block is wrapped in `#ifndef Q_OS_MACOS`):

```cpp
foo = QDir(FS::PathCombine(QStandardPaths::writableLocation(QStandardPaths::AppDataLocation), ".."));
dataPath = foo.absolutePath();
```

with `setOrganizationName(BuildConfig.LAUNCHER_NAME)` / `setApplicationName(BuildConfig.LAUNCHER_NAME)`
both set to `"PrismLauncher"` (`Application.cpp` lines 297-299) — org and app name are the same
string. Qt's `AppDataLocation` on macOS resolves to
`~/Library/Application Support/<OrganizationName>/<ApplicationName>`, i.e.
`~/Library/Application Support/PrismLauncher/PrismLauncher`; stepping one level up (the `".."` in
the code above) lands on:

**`~/Library/Application Support/PrismLauncher/`**

That's where `instances/`, `accounts.json`, `prismlauncher.cfg`, `icons/`, etc. all live on
macOS. (Corroborating evidence for the "AppDataLocation is two levels nested" read: the same file,
line 585, computes a **PolyMC** migration path as
`PathCombine(AppDataLocation, "../../PolyMC")` — i.e. two levels up from `AppDataLocation` plus a
sibling app name, which only makes sense if `AppDataLocation` itself already sits two directories
below `~/Library/Application Support`, matching the Org/App-name nesting above.)

Drag-and-drop import (§7) works the same way on macOS as everywhere else — no macOS-only gap.

---

## 10-line summary

1. Latest **stable** Prism Launcher tag: **`11.1.0`** (published 2026-09-03, verified via GitHub API, not a pre-release).
2. Windows: ship the **MinGW-w64 Portable** build — official download page states MinGW needs no VC++ Redistributable; MSVC (the site's default) does. sha256 of both zips computed locally and recorded above.
3. macOS dmg (`PrismLauncher-macOS-11.1.0.dmg`, universal x86_64+arm64) is **Developer ID signed** (team `MZM5U2NVNH`) **and notarized with a stapled ticket** — `spctl` accepts it offline, no Gatekeeper prompt for users.
4. Windows portable mode = a `portable.txt` file (or `UserData\` folder) next to `prismlauncher.exe`; when present, the exe's own folder becomes the data root for `instances/`, `icons/`, `prismlauncher.cfg` (confirmed in `Application.cpp`); same logic also applies on Linux, never on macOS.
5. First-run wizard pages and their exact skip flags: `Language` (non-empty `Language`), Java pages (`AutomaticJavaDownload=true`, already the default), paste-migration page (`PastebinURL=`), theme page (`ApplicationTheme=dark`+`IconTheme=pe_colored`) — a 6-line pre-seeded `prismlauncher.cfg` skips every page except Login.
6. The **Login/MSA page cannot be pre-seeded away** — no settings flag suppresses it; every new user sees it once until they sign into a Microsoft account.
7. CLI confirmed: `-l/--launch <instance-id>` and `-I/--import <path-or-url>` (bare positional args act as `--import` too); `--launch` with zero configured accounts pops a blocking "No Accounts" modal dialog rather than failing silently — not safe for unattended/scripted smoke tests without a pre-seeded account.
8. Per-instance Java pin: `instance.cfg` keys `OverrideJavaLocation=true` + `JavaPath=<path>`; relative paths technically resolve (CWD = data dir in portable mode) but ship absolute paths to be safe.
9. Prism auto-downloads a matching Java runtime when `AutomaticJavaDownload=true` (the fresh-install default) — compiled in and on by default for official Windows/macOS builds (off by default only for Linux/BSD distro packages).
10. Drag-and-drop of an instance zip onto the main window is handled by shared cross-platform code (`InstanceView`→`MainWindow::processURLs`) — works identically on macOS; macOS data dir is `~/Library/Application Support/PrismLauncher/`.
