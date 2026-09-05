#!/usr/bin/env python3
"""
Stage the Windows one-click installer payload for Little Kettle Valley.

Builds a self-contained tree that Inno Setup packages verbatim:

    <out>/
      prismlauncher.exe + Qt/mingw runtime      (Prism Launcher portable, pinned + hash-checked)
      portable.txt                              (empty -> Prism treats this folder as its data root)
      prismlauncher.cfg                         (pre-seeded: skips every first-run wizard page but Login)
      LittleKettleValley.ico                    (shortcut icon)
      jre/bin/javaw.exe ...                     (Eclipse Temurin 17 JRE, x64, hash-checked from the Adoptium API)
      icons/lkv.png                             (instance icon, resolved by iconKey=lkv)
      instances/Little Kettle Valley/
        instance.cfg                            (rewritten: name, icon, memory, PreLaunchCommand, Java pin)
        mmc-pack.json
        lkv.png
        .minecraft/packwiz-installer-bootstrap.jar

Cross-platform: runs on the GitHub windows-latest runner and on macOS (for verification).
Stdlib only.

Usage:
    python installers/windows/stage.py --out build/stage [--cache .cache] [--java-path <abs path>]

`--java-path` and `--max-mem` are only for local verification. In the real build both values are
left as the placeholder tokens below and Inno Setup's [Code] section substitutes the real ones after
the files are copied: the install path is not knowable until the user picks a destination folder, and
the heap size is not knowable until we can read the target machine's physical RAM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Pinned inputs
# ---------------------------------------------------------------------------

# Prism Launcher 11.1.0, Windows x64, MinGW-w64 *Portable*.
# MinGW (not MSVC) on purpose: per prismlauncher.org/download/windows the MinGW builds
# "do not require the Visual C++ Redistributable to be installed on your system", so the
# installer has zero prerequisites. sha256 recorded in installers/RECON-prism.md, computed
# from the actual bytes at this URL.
PRISM_VERSION = "11.1.0"
PRISM_URL = (
    "https://github.com/PrismLauncher/PrismLauncher/releases/download/"
    f"{PRISM_VERSION}/PrismLauncher-Windows-MinGW-w64-Portable-{PRISM_VERSION}.zip"
)
PRISM_SHA256 = "2bf5e879ea1c3f6a1aaaa43539667ce296308abf3e6a984d5cc4c48bfe3c431c"
PRISM_SIZE = 43_926_838

# Eclipse Temurin JRE 17 (Minecraft 1.20.1 / Forge 47 want Java 17).
# Version floats with Adoptium "latest GA"; the sha256 is taken from the API response for the exact
# asset we then download, and verified before anything is extracted.
ADOPTIUM_ASSETS = (
    "https://api.adoptium.net/v3/assets/latest/17/hotspot"
    "?architecture=x64&image_type=jre&os=windows&vendor=eclipse"
)
# Documented equivalent redirect endpoint (kept for reference; we use the assets API so we get a
# checksum to verify against):
#   https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk

INSTANCE_NAME = "Little Kettle Valley"
PACK_URL = "https://raw.githubusercontent.com/malloyjoshua/little-kettle-valley/main/pack/pack.toml"

# Replaced by the Inno Setup [Code] section at install time with the real absolute path.
JAVA_PATH_TOKEN = "@@JAVA_PATH@@"

# Likewise replaced at install time, with a heap size chosen from the machine's physical RAM
# (GlobalMemoryStatusEx). Baking one number here would hand an 8 GB laptop a 3584 MB heap, which is
# exactly what docs/INSTALL.md tells people not to do. Tiers live in the .iss [Code] section:
#   < 12 GB -> 3072    12-24 GB -> 3584    > 24 GB -> 4096
MAX_MEM_TOKEN = "@@MAX_MEM@@"
MIN_MEM_MB = 1024

# Open the shipped valley instead of the main menu.  The pack carries the world
# (pack/saves/Little Kettle Valley/) and the PreLaunchCommand installs it before the
# JVM starts, so the save is on disk by the time these are read.
#
# PrismLauncher 11.1.0, MinecraftInstance.cpp: createLaunchTask() ignores both keys
# unless JoinServerOnLaunch is true, then prefers JoinServerOnLaunchAddress and only
# falls through to JoinWorldOnLaunch when the address is empty -- so we set the bool
# and write no address key at all.  processMinecraftArgs() turns it into
# `--quickPlaySingleplayer <value>`, gated on the profile trait
# feature:is_quick_play_singleplayer, which 1.20.1's Prism meta carries.
#
# The value is the SAVE FOLDER name (Prism reads WorldList::folderName()), not
# level.dat's LevelName.  Rename the folder and this has to follow it.
#
# Note the INI caveat in instance_cfg()'s docstring applies here too: with no
# ConfigVersion key Prism runs unescape() over every value.  unescape() only eats
# backslashes -- spaces are untouched -- so "Little Kettle Valley" survives intact.
JOIN_WORLD_FOLDER = "Little Kettle Valley"

# Prism's own self-updater. Deliberately NOT shipped: Application::updaterEnabled() (Application.cpp
# 1272-1279) only turns the updater on when this binary sits next to the exe, so omitting it stops
# Prism prompting friends to self-update a launcher we pin and ship ourselves.
PRISM_EXCLUDE = {"prismlauncher_updater.exe"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    print(f"[stage] {msg}", flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, attempts: int = 3) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            log(f"downloading {url} (attempt {attempt})")
            req = urllib.request.Request(url, headers={"User-Agent": "little-kettle-valley-installer"})
            tmp = dest.with_suffix(dest.suffix + ".part")
            with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as out:
                shutil.copyfileobj(resp, out, 1024 * 1024)
            tmp.replace(dest)
            return dest
        except (urllib.error.URLError, TimeoutError, OSError) as exc:  # pragma: no cover
            last = exc
            log(f"  failed: {exc}")
    raise SystemExit(f"could not download {url}: {last}")


def cached_download(url: str, dest: Path, expect_sha: str | None, expect_size: int | None = None) -> Path:
    """Download unless a cached copy already matches the expected digest."""
    if dest.exists() and expect_sha:
        if sha256_file(dest) == expect_sha:
            log(f"cache hit {dest.name}")
            return dest
        log(f"cache miss (digest changed) {dest.name}")
        dest.unlink()
    elif dest.exists() and not expect_sha:
        dest.unlink()

    download(url, dest)

    actual = sha256_file(dest)
    size = dest.stat().st_size
    if expect_sha and actual != expect_sha:
        raise SystemExit(
            f"sha256 mismatch for {url}\n  expected {expect_sha}\n  actual   {actual}\n"
            "Refusing to stage. Re-pin the digest only after confirming upstream republished."
        )
    if expect_size is not None and size != expect_size:
        log(f"WARNING: {dest.name} is {size} B, expected {expect_size} B (digest still matched)")
    log(f"verified {dest.name}  {size} B  sha256={actual}")
    return dest


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "little-kettle-valley-installer"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def unzip(archive: Path, dest: Path, strip_top_level: bool = False, exclude: set[str] | None = None) -> None:
    """Extract `archive` into `dest`. Path-traversal safe; optionally drops the single root folder."""
    exclude = exclude or set()
    dest.mkdir(parents=True, exist_ok=True)
    dest_resolved = dest.resolve()
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        prefix = ""
        if strip_top_level:
            roots = {n.split("/", 1)[0] for n in names if n.strip()}
            if len(roots) != 1:
                raise SystemExit(f"expected exactly one top-level folder in {archive.name}, found {sorted(roots)}")
            prefix = roots.pop() + "/"
        for info in zf.infolist():
            name = info.filename
            if strip_top_level:
                if not name.startswith(prefix):
                    continue
                name = name[len(prefix) :]
            if not name or name in exclude:
                continue
            target = (dest / name).resolve()
            if not str(target).startswith(str(dest_resolved)):
                raise SystemExit(f"refusing unsafe path {info.filename} in {archive.name}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out)


def write_text(path: Path, text: str) -> None:
    """Write CRLF text (these are Windows config files read by Qt's INI parser)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))


def resolve_instance_source(repo_root: Path, workdir: Path) -> Path:
    """
    Locate the source instance tree.

    `dist/CozyTech/` is gitignored, so it only exists on Josh's Mac. `dist/LittleKettleValley.zip`
    -- the exact zip friends already import by hand -- IS committed, so that is what CI unpacks.
    Prefer the live folder when present so a local build reflects unreleased tweaks.
    """
    folder = repo_root / "dist" / "CozyTech"
    if (folder / "instance.cfg").is_file():
        log(f"instance source: {folder}")
        return folder

    zip_path = repo_root / "dist" / "LittleKettleValley.zip"
    if not zip_path.is_file():
        raise SystemExit(f"no instance source: neither {folder} nor {zip_path} exists")
    dest = workdir / "instance-src"
    if dest.exists():
        shutil.rmtree(dest)
    unzip(zip_path, dest)
    if not (dest / "instance.cfg").is_file():
        raise SystemExit(f"{zip_path} does not look like a Prism instance export")
    log(f"instance source: {zip_path} (unpacked to {dest})")
    return dest


def pack_version(repo_root: Path) -> str:
    toml = (repo_root / "pack" / "pack.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', toml, re.MULTILINE)
    if not m:
        raise SystemExit("could not read version from pack/pack.toml")
    return m.group(1)


# ---------------------------------------------------------------------------
# Config file bodies
# ---------------------------------------------------------------------------


def instance_cfg(java_path: str, max_mem: str) -> str:
    """
    Prism reads this through INIFile::loadFile. With no ConfigVersion key present it falls back to
    parseOldFileFormat(), which runs unescape() over every value -- unescape() *eats* backslashes
    (INIFile.cpp 76-99), so a Windows path must be written with forward slashes. Qt resolves
    'C:/.../javaw.exe' fine on Windows.
    """
    return "\n".join(
        [
            "[General]",
            "InstanceType=OneSix",
            f"name={INSTANCE_NAME}",
            "iconKey=lkv",
            # Join-on-launch: see JOIN_WORLD_FOLDER above. No JoinServerOnLaunchAddress
            # key -- an address would win over the world.
            "JoinServerOnLaunch=true",
            f"JoinWorldOnLaunch={JOIN_WORLD_FOLDER}",
            "OverrideMemory=true",
            f"MinMemAlloc={MIN_MEM_MB}",
            f"MaxMemAlloc={max_mem}",
            "OverrideCommands=true",
            # Prism never runs PreLaunchCommand through a shell: it substitutes $INST_JAVA in C++
            # and tokenizes with QProcess::splitCommand(), then execs directly. Same string works
            # on Windows and macOS -- see installers/RECON-instance.md.
            f'PreLaunchCommand="$INST_JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "{PACK_URL}"',
            "OverrideJavaArgs=true",
            "JvmArgs=-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:G1NewSizePercent=20 "
            "-XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
            # Pin the bundled JRE. AutoInstallJava::executeTask() short-circuits when
            # OverrideJavaLocation is true and the JavaPath file exists, so Prism never
            # second-guesses this -- but still auto-downloads a JRE if the folder ever moves.
            "OverrideJavaLocation=true",
            f"JavaPath={java_path}",
            "",
        ]
    )


def launcher_cfg(java_path: str, max_mem: str) -> str:
    """
    Global Prism settings. Every first-run wizard page is skipped except Login (Microsoft sign-in
    cannot be pre-seeded, by design). Conditions verified against Application::createSetupWizard()
    in installers/RECON-prism.md section 4.
    """
    return "\n".join(
        [
            "[General]",
            # Language page: shown when Language is empty.
            "Language=en_US",
            # Theme page: shown when the app/icon theme id is not a valid one.
            "ApplicationTheme=dark",
            "IconTheme=pe_colored",
            # Paste page: shown when PastebinURL is non-empty (legacy migration prompt).
            "PastebinURL=",
            # Java + AutoJava pages: AutomaticJavaDownload=true skips both. Both flags stay on so a
            # broken/moved bundled JRE still self-heals; the instance-level pin takes precedence.
            "AutomaticJavaDownload=true",
            "AutomaticJavaSwitch=true",
            "UserAskedAboutAutomaticJavaDownload=true",
            "IgnoreJavaWizard=true",
            f"JavaPath={java_path}",
            # Launcher-wide defaults for any *new* instance the player makes. The pack instance
            # pins its own values above; these are patched to the same tier for consistency.
            f"MinMemAlloc={MIN_MEM_MB}",
            f"MaxMemAlloc={max_mem}",
            "InstanceDir=instances",
            "IconsDir=icons",
            "ShowConsole=false",
            "ShowConsoleOnError=true",
            "",
        ]
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    here = Path(__file__).resolve().parent
    repo_root = here.parents[1]

    ap = argparse.ArgumentParser(description="Stage the Little Kettle Valley Windows installer payload")
    ap.add_argument("--out", default=str(here / "build" / "stage"), help="output tree (wiped and rebuilt)")
    ap.add_argument("--cache", default=str(here / "build" / "cache"), help="download cache")
    ap.add_argument("--repo-root", default=str(repo_root), help="repo root (holds pack/ and dist/CozyTech)")
    ap.add_argument(
        "--java-path",
        default=JAVA_PATH_TOKEN,
        help="absolute path to javaw.exe to bake in (default: placeholder replaced by the installer)",
    )
    ap.add_argument(
        "--max-mem",
        default=MAX_MEM_TOKEN,
        help="MaxMemAlloc in MB to bake in (default: placeholder replaced by the installer, which "
        "picks 3072/3584/4096 from the machine's physical RAM)",
    )
    args = ap.parse_args()

    out = Path(args.out).resolve()
    cache = Path(args.cache).resolve()
    repo_root = Path(args.repo_root).resolve()

    cache.mkdir(parents=True, exist_ok=True)
    src_instance = resolve_instance_source(repo_root, cache)

    version = pack_version(repo_root)
    log(f"pack version {version}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # 1. Prism Launcher portable ------------------------------------------------
    prism_zip = cached_download(PRISM_URL, cache / Path(PRISM_URL).name, PRISM_SHA256, PRISM_SIZE)
    unzip(prism_zip, out, exclude=PRISM_EXCLUDE)
    if not (out / "prismlauncher.exe").is_file():
        raise SystemExit("prismlauncher.exe missing after extraction")
    log(f"prism extracted ({sum(1 for _ in out.rglob('*') if _.is_file())} files)")

    # portable.txt next to the exe -> the install folder becomes Prism's data root
    # (Application.cpp 405-416; Windows m_rootPath == applicationDirPath()).
    (out / "portable.txt").write_bytes(b"")

    # 2. Temurin 17 JRE ---------------------------------------------------------
    assets = fetch_json(ADOPTIUM_ASSETS)
    if not isinstance(assets, list) or not assets:
        raise SystemExit("unexpected Adoptium API response (empty list)")
    binary = assets[0]["binary"]
    pkg = binary["package"]
    jre_release = assets[0].get("release_name", "unknown")
    if binary.get("os") != "windows" or binary.get("architecture") != "x64" or binary.get("image_type") != "jre":
        raise SystemExit(f"Adoptium returned an unexpected binary: {binary.get('os')}/{binary.get('architecture')}")
    log(f"temurin {jre_release}: {pkg['name']} sha256={pkg['checksum']}")
    jre_zip = cached_download(pkg["link"], cache / pkg["name"], pkg["checksum"], pkg.get("size"))
    unzip(jre_zip, out / "jre", strip_top_level=True)
    javaw = out / "jre" / "bin" / "javaw.exe"
    if not javaw.is_file():
        raise SystemExit("jre/bin/javaw.exe missing after extraction")
    if not (out / "jre" / "bin" / "java.exe").is_file():
        raise SystemExit("jre/bin/java.exe missing after extraction")
    log(f"jre staged ({jre_release})")

    # 3. Instance ---------------------------------------------------------------
    inst = out / "instances" / INSTANCE_NAME
    (inst / ".minecraft").mkdir(parents=True)
    shutil.copy2(src_instance / "mmc-pack.json", inst / "mmc-pack.json")
    shutil.copy2(src_instance / "lkv.png", inst / "lkv.png")
    shutil.copy2(
        src_instance / ".minecraft" / "packwiz-installer-bootstrap.jar",
        inst / ".minecraft" / "packwiz-installer-bootstrap.jar",
    )
    write_text(inst / "instance.cfg", instance_cfg(args.java_path, args.max_mem))

    # 4. Icons + launcher config ------------------------------------------------
    (out / "icons").mkdir(exist_ok=True)
    shutil.copy2(src_instance / "lkv.png", out / "icons" / "lkv.png")
    write_text(out / "prismlauncher.cfg", launcher_cfg(args.java_path, args.max_mem))

    ico = here / "LittleKettleValley.ico"
    if not ico.is_file():
        raise SystemExit(f"missing {ico} -- run installers/windows/make_icon.py first")
    shutil.copy2(ico, out / "LittleKettleValley.ico")

    # 5. Version include for Inno Setup ----------------------------------------
    write_text(here / "version.iss", f'; generated by stage.py -- do not edit\n#define AppVersion "{version}"\n')

    # 6. Sanity: the installer can only substitute tokens it can actually find ---
    for rel, tokens in (
        (f"instances/{INSTANCE_NAME}/instance.cfg", (args.java_path, args.max_mem)),
        ("prismlauncher.cfg", (args.java_path, args.max_mem)),
    ):
        body = (out / rel).read_text(encoding="utf-8")
        for tok in tokens:
            if tok not in body:
                raise SystemExit(f"{rel} does not contain {tok!r} -- the installer would never patch it")
    if args.max_mem == MAX_MEM_TOKEN:
        log("memory left as a token; the installer picks 3072/3584/4096 from the machine's RAM")

    cfg_body = (out / f"instances/{INSTANCE_NAME}/instance.cfg").read_text(encoding="utf-8")
    for needed in ("JoinServerOnLaunch=true", f"JoinWorldOnLaunch={JOIN_WORLD_FOLDER}"):
        if needed not in cfg_body:
            raise SystemExit(f"instance.cfg is missing {needed!r} -- it would open the main menu")
    if "JoinServerOnLaunchAddress" in cfg_body:
        raise SystemExit("instance.cfg sets JoinServerOnLaunchAddress -- that beats the world join")
    log(f"opens {JOIN_WORLD_FOLDER!r} on launch (--quickPlaySingleplayer)")

    # 7. Report -----------------------------------------------------------------
    files = [p for p in out.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    log(f"staged {len(files)} files, {total / 1024 / 1024:.1f} MiB -> {out}")
    for rel in [
        "prismlauncher.exe",
        "portable.txt",
        "prismlauncher.cfg",
        "LittleKettleValley.ico",
        "jre/bin/javaw.exe",
        "icons/lkv.png",
        f"instances/{INSTANCE_NAME}/instance.cfg",
        f"instances/{INSTANCE_NAME}/mmc-pack.json",
        f"instances/{INSTANCE_NAME}/.minecraft/packwiz-installer-bootstrap.jar",
    ]:
        p = out / rel
        status = "ok " if p.is_file() else "MISSING"
        log(f"  {status} {rel}")
        if not p.is_file():
            return 1

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"version={version}\n")
            fh.write(f"jre={jre_release}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
