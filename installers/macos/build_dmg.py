#!/usr/bin/env python3
"""Build the macOS disk image for Little Kettle Valley.

The image carries three things a friend can see:

  * ``Prism Launcher.app`` — the official, untouched, Developer-ID-signed and
    notarized build, pinned by sha256.  It is copied with ``ditto`` so the
    signature survives, and re-verified with ``codesign``/``spctl`` afterwards.
  * ``Applications`` — a symlink, so step 1 is a drag.
  * ``Little Kettle Valley.zip`` — the Prism instance export, built from
    ``dist/CozyTech`` with the memory settings tuned for an 8 GB MacBook Air.

...and one thing it doesn't: a hand-drawn background PNG showing the three
numbered steps, generated here with Pillow from ``media/palette.json`` and the
title wordmark in ``media/logo``.

The layout is written straight into the image's ``.DS_Store`` by dmgbuild — no
Finder, no AppleScript, nothing takes over the desktop.

Idempotent: run it as many times as you like.  Output is
``dist/LittleKettleValley.dmg`` and its sha256 is printed at the end.

    tools/venv/bin/python installers/macos/build_dmg.py [--verify-only]
"""

from __future__ import annotations

import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --------------------------------------------------------------------------
# Pinned inputs
# --------------------------------------------------------------------------

PRISM_VERSION = "11.1.0"
PRISM_DMG_NAME = f"PrismLauncher-macOS-{PRISM_VERSION}.dmg"
PRISM_DMG_URL = (
    "https://github.com/PrismLauncher/PrismLauncher/releases/download/"
    f"{PRISM_VERSION}/{PRISM_DMG_NAME}"
)
# Computed from the bytes at that URL on 2026-09-03 (see installers/RECON-prism.md).
PRISM_DMG_SHA256 = "dd34e829abdc22b60a713a45f8e013148ab8ef5dee4531fa4030844f14bfac3b"
PRISM_TEAM_ID = "MZM5U2NVNH"

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "installers" / "macos"
BUILD = HERE / "build"
DIST = ROOT / "dist"
OUT_DMG = DIST / "LittleKettleValley.dmg"

VOLUME_NAME = "Little Kettle Valley"
APP_NAME = "Prism Launcher.app"
ZIP_NAME = "Little Kettle Valley.zip"

# Tuned for the target machine: MacBook Air M2, 8 GB unified memory.
# 3 GB heap leaves room for the JVM's own off-heap use plus macOS itself.
# No JavaPath / OverrideJavaLocation: Prism auto-detects, and failing that
# auto-downloads a matching Java 17 (AutomaticJavaDownload defaults on for the
# official macOS build) — see installers/RECON-prism.md §6.
MAX_MEM_MB = 3072
MIN_MEM_MB = 1024

# The pack ships render 8 / simulation 6 (pack/options.txt), which is right for
# Josh's M1 Max and for the Windows exe.  The DMG is the Air's copy, and render
# distance is the single cheapest frame-rate dial there — see the "Air budget"
# section of docs/integration-audit-night.md — so this instance starts at 6/6.
#
# It sticks because `options.txt` is marked `preserve = true` in pack/index.toml:
# packwiz-installer only writes a preserved file when it does not already exist
# ("the file is not overwritten if it already exists, to preserve changes made
# by a user" — packwiz index.toml reference; confirmed in the shipped
# packwiz-installer.jar, DownloadTask.download(): `if (metadata.getPreserve() &&
# dest.getNioPath().toFile().exists()) return`).  We put ours in .minecraft/
# before the first PreLaunchCommand runs, so the installer leaves it alone —
# and so does every later update, along with whatever she changes herself.
AIR_RENDER_DISTANCE = 6
AIR_SIMULATION_DISTANCE = 6
PACK_OPTIONS = ROOT / "pack" / "options.txt"

# Open the shipped valley instead of the Minecraft main menu.
#
# The pack carries the world itself (pack/saves/Little Kettle Valley/, every file
# marked preserve = true), so by the time the game starts the save is already on
# disk -- the PreLaunchCommand that installs it runs before the JVM does.  These
# two keys are what make Prism walk her into it rather than leaving her at
# Singleplayer > pick one.
#
# Read out of PrismLauncher 11.1.0 (the version this dmg bundles):
#   * MinecraftInstance::loadSpecificSettings registers JoinServerOnLaunch (bool),
#     JoinServerOnLaunchAddress (string) and JoinWorldOnLaunch (string), with no
#     global override -- they are instance.cfg keys and nothing else.
#   * createLaunchTask() only looks at any of them when JoinServerOnLaunch is
#     true; it then takes the ADDRESS if it is non-empty and the WORLD otherwise.
#     So the world path needs the boolean on and the address key absent.
#   * processMinecraftArgs() emits `--quickPlaySingleplayer <JoinWorldOnLaunch>`
#     if the profile has the trait feature:is_quick_play_singleplayer.
#     meta.prismlauncher.org's net.minecraft/1.20.1.json carries that trait.
#   * MinecraftTarget::parse(s, useWorld=true) returns s verbatim -- no splitting,
#     no trimming -- so the space in the folder name is safe.
#
# The value is the SAVE FOLDER name (Prism fills the box from
# WorldList::folderName()), not level.dat's LevelName.  They are the same string
# here; if the folder is ever renamed, this must follow it, not the display name.
#
# Worst case is benign: if the world is missing or the arg is wrong, Minecraft
# falls back to the main menu.  It cannot fail the launch.
JOIN_WORLD_FOLDER = "Little Kettle Valley"

# --------------------------------------------------------------------------
# Window / background layout — one source of truth, shared by the PNG we draw
# and the icon positions dmgbuild writes into the .DS_Store.
# --------------------------------------------------------------------------

WIN_W, WIN_H = 900, 660
ICON_SIZE = 96
LABEL_SIZE = 13

SHELF_W, SHELF_H = 220, 165
SHELF_ICON_DY = 62  # icon centre, measured down from the shelf's top edge

APP_SHELF = (160, 250)        # top-left of the "Prism Launcher" shelf
APPS_SHELF = (520, 250)       # top-left of the "Applications" shelf
ZIP_SHELF = (645, 480)        # top-left of the kettle-zip shelf


def shelf_icon_centre(shelf: tuple[int, int]) -> tuple[int, int]:
    return (shelf[0] + SHELF_W // 2, shelf[1] + SHELF_ICON_DY)


ICON_LOCATIONS = {
    APP_NAME: shelf_icon_centre(APP_SHELF),
    "Applications": shelf_icon_centre(APPS_SHELF),
    ZIP_NAME: shelf_icon_centre(ZIP_SHELF),
}

STEPS = [
    # (badge centre, title, subtitle)
    ((76, 210), "Drag Prism Launcher into Applications",
     "Drop it on the folder. Leave this window open for step 3."),
    ((76, 452), "Open Prism Launcher, sign in with Microsoft",
     "It fetches Java by itself. Let it — that's normal."),
    ((76, 522), "Drag the kettle zip onto Prism's window",
     "Or: Add Instance > Import. First launch installs the pack."),
]

TAGLINE = "Put the kettle on. Three steps and you're in the valley."

# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def say(msg: str) -> None:
    print(f"  {msg}", flush=True)


def palette() -> dict[str, str]:
    with open(ROOT / "media" / "palette.json") as fh:
        return json.load(fh)["colors"]


def rgb(hexstr: str, alpha: int | None = None):
    hexstr = hexstr.lstrip("#")
    t = tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))
    return t if alpha is None else t + (alpha,)


# --------------------------------------------------------------------------
# 1. The official Prism Launcher.app
# --------------------------------------------------------------------------


def fetch_prism_dmg() -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    dmg = BUILD / PRISM_DMG_NAME
    if dmg.exists() and sha256_of(dmg) == PRISM_DMG_SHA256:
        say(f"{PRISM_DMG_NAME} already present, sha256 matches the pin")
        return dmg
    if dmg.exists():
        say("cached copy does not match the pinned sha256 — re-downloading")
        dmg.unlink()
    say(f"downloading {PRISM_DMG_URL}")
    with urllib.request.urlopen(PRISM_DMG_URL) as resp, open(dmg, "wb") as out:
        shutil.copyfileobj(resp, out)
    got = sha256_of(dmg)
    if got != PRISM_DMG_SHA256:
        dmg.unlink()
        raise SystemExit(
            f"FATAL: {PRISM_DMG_NAME} sha256 mismatch.\n"
            f"  expected {PRISM_DMG_SHA256}\n  got      {got}\n"
            "Upstream republished the release, or the download was tampered with. "
            "Re-run the recon before changing the pin."
        )
    say(f"downloaded, sha256 {got} matches the pin")
    return dmg


class Mounted:
    """hdiutil attach -nobrowse (never touches Finder), detached on exit."""

    def __init__(self, dmg: Path, readonly: bool = True):
        self.dmg = dmg
        self.readonly = readonly
        self.point: Path | None = None
        self._tmp: str | None = None

    def __enter__(self) -> Path:
        self._tmp = tempfile.mkdtemp(prefix="lkv-mnt-")
        cmd = ["hdiutil", "attach", str(self.dmg), "-nobrowse", "-noautoopen",
               "-noverify", "-mountpoint", self._tmp]
        if self.readonly:
            cmd.append("-readonly")
        run(cmd)
        self.point = Path(self._tmp)
        return self.point

    def __exit__(self, *exc):
        if self.point is not None:
            for _ in range(12):
                try:
                    run(["hdiutil", "detach", str(self.point)])
                    break
                except subprocess.CalledProcessError:
                    import time
                    time.sleep(1)
            else:
                run(["hdiutil", "detach", str(self.point), "-force"])
        if self._tmp and os.path.isdir(self._tmp):
            try:
                os.rmdir(self._tmp)
            except OSError:
                pass
        return False


def verify_app_signature(app: Path, label: str) -> None:
    cs = subprocess.run(["codesign", "--verify", "--deep", "--strict",
                         "--verbose=2", str(app)],
                        text=True, capture_output=True)
    if cs.returncode != 0:
        raise SystemExit(f"FATAL: codesign --verify failed on {label}:\n{cs.stderr}")
    info = subprocess.run(["codesign", "-dv", "--verbose=2", str(app)],
                          text=True, capture_output=True).stderr
    if f"TeamIdentifier={PRISM_TEAM_ID}" not in info:
        raise SystemExit(
            f"FATAL: {label} is not signed by the expected Prism team "
            f"{PRISM_TEAM_ID}:\n{info}"
        )
    if "Notarization Ticket=stapled" not in info:
        raise SystemExit(f"FATAL: {label} has no stapled notarization ticket:\n{info}")
    sp = subprocess.run(["spctl", "-a", "-vv", "-t", "exec", str(app)],
                        text=True, capture_output=True)
    combined = sp.stdout + sp.stderr
    if sp.returncode != 0 or "accepted" not in combined:
        raise SystemExit(f"FATAL: spctl rejected {label}:\n{combined}")
    src = "Notarized Developer ID" if "Notarized Developer ID" in combined else "?"
    say(f"{label}: codesign OK, team {PRISM_TEAM_ID}, ticket stapled, "
        f"spctl accepted (source={src})")


def stage_prism_app() -> Path:
    dmg = fetch_prism_dmg()
    staged = BUILD / "stage"
    app = staged / APP_NAME
    if app.exists():
        shutil.rmtree(app)
    staged.mkdir(parents=True, exist_ok=True)
    with Mounted(dmg) as point:
        src = point / APP_NAME
        if not src.is_dir():
            raise SystemExit(f"FATAL: {APP_NAME} not found in {PRISM_DMG_NAME}")
        verify_app_signature(src, "app inside the upstream dmg")
        # ditto, not cp: keeps xattrs, ACLs and symlinks intact so the
        # code signature stays valid.
        run(["ditto", str(src), str(app)])
    verify_app_signature(app, "staged copy")
    return app


# --------------------------------------------------------------------------
# 2. The instance zip, tuned for the Air
# --------------------------------------------------------------------------


def tune_instance_cfg(text: str) -> str:
    out, seen = [], set()
    for line in text.splitlines():
        key = line.split("=", 1)[0].strip() if "=" in line else None
        if key in ("JavaPath", "OverrideJavaLocation"):
            # Deliberately dropped: let Prism auto-detect or auto-download Java.
            continue
        if key == "MaxMemAlloc":
            line = f"MaxMemAlloc={MAX_MEM_MB}"
            seen.add(key)
        elif key == "MinMemAlloc":
            line = f"MinMemAlloc={MIN_MEM_MB}"
            seen.add(key)
        out.append(line)
    missing = {"MaxMemAlloc", "MinMemAlloc"} - seen
    if missing:
        raise SystemExit(f"FATAL: dist/CozyTech/instance.cfg has no {sorted(missing)}")
    # Join-the-world keys: normally inherited from dist/CozyTech/instance.cfg, but
    # written here if that file has drifted, so the dmg can never ship an instance
    # that drops her at the main menu.  An explicit JoinServerOnLaunchAddress would
    # win over the world (createLaunchTask checks the address first), so drop it.
    out = [l for l in out if (l.split("=", 1)[0].strip() if "=" in l else None)
           not in ("JoinServerOnLaunch", "JoinWorldOnLaunch", "JoinServerOnLaunchAddress")]
    head = out.index("[General]") + 1
    out[head:head] = ["JoinServerOnLaunch=true", f"JoinWorldOnLaunch={JOIN_WORLD_FOLDER}"]
    return "\n".join(out) + "\n"


def air_options_txt() -> bytes:
    """pack/options.txt with the two distance dials turned down for the Air.

    Every other line — the 12 de-collided keybinds, maxFps, entityDistanceScaling
    — is carried through byte for byte, in the pack's own order, so the DMG never
    silently drifts from the pack it installs.
    """
    if not PACK_OPTIONS.is_file():
        raise SystemExit(f"FATAL: {PACK_OPTIONS} missing — nothing to tune")
    wanted = {
        "renderDistance": AIR_RENDER_DISTANCE,
        "simulationDistance": AIR_SIMULATION_DISTANCE,
    }
    out, seen = [], set()
    for line in PACK_OPTIONS.read_text(encoding="utf-8").splitlines():
        key = line.split(":", 1)[0] if ":" in line else None
        if key in wanted:
            line = f"{key}:{wanted[key]}"
            seen.add(key)
        out.append(line)
    missing = set(wanted) - seen
    if missing:
        raise SystemExit(f"FATAL: pack/options.txt has no {sorted(missing)}")
    if not out or not out[0].startswith("version:"):
        raise SystemExit("FATAL: pack/options.txt does not start with a version: line")
    return ("\n".join(out) + "\n").encode("utf-8")


def build_instance_zip() -> Path:
    src = DIST / "CozyTech"
    if not (src / "instance.cfg").is_file():
        raise SystemExit(f"FATAL: {src}/instance.cfg missing — nothing to package")
    out = BUILD / ZIP_NAME
    if out.exists():
        out.unlink()

    members: list[tuple[str, bytes]] = []
    for path in sorted(src.rglob("*")):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        arc = path.relative_to(src).as_posix()
        data = path.read_bytes()
        if arc == "instance.cfg":
            data = tune_instance_cfg(data.decode("utf-8")).encode("utf-8")
        members.append((arc, data))

    # Synthesised, not copied: dist/CozyTech has no options.txt, and adding one
    # there would make the pack's own copy and the Air's copy two files to keep
    # in step.  This is generated from pack/options.txt on every build instead.
    opts = ".minecraft/options.txt"
    if any(a == opts for a, _ in members):
        raise SystemExit(f"FATAL: dist/CozyTech already ships {opts}")
    members.append((opts, air_options_txt()))
    members.sort(key=lambda m: m[0])

    # Fixed timestamps so re-running produces byte-identical output.
    stamp = (2026, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arc, data in members:
            info = zipfile.ZipInfo(arc, date_time=stamp)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)

    cfg = next(d for a, d in members if a == "instance.cfg").decode()
    assert f"MaxMemAlloc={MAX_MEM_MB}" in cfg and f"MinMemAlloc={MIN_MEM_MB}" in cfg
    assert "JavaPath" not in cfg and "OverrideJavaLocation" not in cfg
    assert "JoinServerOnLaunch=true" in cfg, "instance would open the main menu, not the valley"
    assert f"JoinWorldOnLaunch={JOIN_WORLD_FOLDER}" in cfg
    assert "JoinServerOnLaunchAddress" not in cfg, "an address key would beat the world"
    opt = next(d for a, d in members if a == ".minecraft/options.txt").decode()
    assert opt.splitlines()[0].startswith("version:")
    assert f"renderDistance:{AIR_RENDER_DISTANCE}" in opt
    assert f"simulationDistance:{AIR_SIMULATION_DISTANCE}" in opt
    say(f"{ZIP_NAME}: {len(members)} entries, "
        f"MaxMemAlloc={MAX_MEM_MB} MinMemAlloc={MIN_MEM_MB}, no Java pin")
    say(f"  opens {JOIN_WORLD_FOLDER!r} on launch (--quickPlaySingleplayer)")
    say(f"  .minecraft/options.txt: {len(opt.splitlines())} lines, "
        f"renderDistance={AIR_RENDER_DISTANCE} "
        f"simulationDistance={AIR_SIMULATION_DISTANCE} "
        "(preserve=true keeps packwiz off it)")
    return out


# --------------------------------------------------------------------------
# 3. The background, drawn with Pillow
# --------------------------------------------------------------------------


def font(index: int, size: int):
    for path in ("/System/Library/Fonts/Avenir Next.ttc",
                 "/System/Library/Fonts/HelveticaNeue.ttc",
                 "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except OSError:
                continue
    return ImageFont.load_default()


FONT_TITLE, FONT_SUB, FONT_TAG = 2, 7, 5  # Avenir Next Demi Bold / Regular / Medium


def pixel_grid(draw: ImageDraw.ImageDraw, grid, ox: int, oy: int, unit: int,
               fill, outline) -> None:
    """Blit a '#'/'.' bitmap as chunky pixels, with a one-cell outline.

    Same idiom as media/logo/build.py: author at native resolution, scale by
    an integer factor, so nothing ever gets blurred.
    """
    h, w = len(grid), len(grid[0])
    solid = {(x, y) for y in range(h) for x in range(w) if grid[y][x] == "#"}
    edge = set()
    for (x, y) in solid:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if p not in solid:
                    edge.add(p)
    for (x, y), colour in [(p, outline) for p in edge] + [(p, fill) for p in solid]:
        draw.rectangle([ox + x * unit, oy + y * unit,
                        ox + (x + 1) * unit - 1, oy + (y + 1) * unit - 1],
                       fill=colour)


DIGITS = {
    1: ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    2: [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    3: [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
}


def badge_grid(n: int) -> list[str]:
    size, r = 15, 7.4
    cells = [["." for _ in range(size)] for _ in range(size)]
    for y in range(size):
        for x in range(size):
            if (x - 7) ** 2 + (y - 7) ** 2 <= r * r:
                cells[y][x] = "#"
    glyph = DIGITS[n]
    gx, gy = (size - 5) // 2, (size - 7) // 2
    for y, row in enumerate(glyph):
        for x, ch in enumerate(row):
            if ch == "#":
                cells[gy + y][gx + x] = "o"   # punched out of the disc
    return ["".join(row) for row in cells]


def arrow_grid(length: int) -> list[str]:
    """Chunky right-pointing arrow: shaft plus a stepped triangular head."""
    h = 11
    head = 8
    w = length
    cells = [["." for _ in range(w)] for _ in range(h)]
    for x in range(0, w - head + 1):
        for y in (4, 5, 6):
            cells[y][x] = "#"
    for i in range(head):
        x = w - head + i
        k = round((head - 1 - i) * 5 / (head - 1))
        for y in range(5 - k, 5 + k + 1):
            if 0 <= y < h:
                cells[y][x] = "#"
    return ["".join(row) for row in cells]


def draw_shelf(base: Image.Image, xy: tuple[int, int], s: int, c: dict) -> None:
    """A mid-tone 'shelf' the Finder icon sits on.

    This is doing real work, not decoration.  Finder draws icon labels in the
    system label colour: near-black in light mode, white in dark mode.  On a
    cream background one of those two is unreadable.  sage_dark sits at
    relative luminance ~0.17 — near the exact midpoint where white and black
    both clear 4.4:1 — so the labels read either way.
    """
    x, y = xy[0] * s, xy[1] * s
    w, h = SHELF_W * s, SHELF_H * s
    r = 14 * s

    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x + 3 * s, y + 4 * s, x + w + 3 * s, y + h + 4 * s], r,
        fill=rgb(c["copper_dark"], 46))
    base.alpha_composite(shadow)

    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x, y, x + w, y + h], r,
                        fill=rgb(c["sage_dark"], 255),
                        outline=rgb(c["copper_dark"], 255), width=3 * s)
    d.rounded_rectangle([x + 5 * s, y + 5 * s, x + w - 5 * s, y + h - 5 * s],
                        r - 3 * s, outline=rgb(c["sage"], 90), width=max(1, s))


def build_background(scale: int, c: dict) -> Image.Image:
    s = scale
    W, H = WIN_W * s, WIN_H * s
    img = Image.new("RGBA", (W, H), rgb(c["cream"], 255))
    d = ImageDraw.Draw(img)

    # Ground: a slow cream -> paper wash, so the window has some depth.
    top, bot = rgb(c["cream"]), rgb(c["paper"])
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,))

    # Steam curling up behind the wordmark.
    steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for cx, cy, rx, ry, a in ((250, 92, 120, 62, 42), (640, 84, 140, 66, 38),
                              (450, 60, 190, 54, 30)):
        sd.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s],
                   fill=rgb(c["steam"], a))
    steam = steam.filter(ImageFilter.GaussianBlur(18 * s))
    img.alpha_composite(steam)

    # Hills along the bottom-left, sage, kept faint.
    hills = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hills)
    ridge = [(0, 660), (0, 630), (90, 606), (190, 626), (300, 602),
             (420, 628), (520, 612), (640, 636), (760, 614), (900, 632),
             (900, 660)]
    hd.polygon([(x * s, y * s) for x, y in ridge], fill=rgb(c["sage"], 70))
    img.alpha_composite(hills)

    # Wordmark: native art is 87x22; 5x at 1x, 10x at 2x — always integer,
    # always NEAREST, so the pixels stay square.
    mark = Image.open(ROOT / "media" / "logo" / "wordmark_2048.png").convert("RGBA")
    native = mark.resize((87, 22), Image.NEAREST)
    factor = 5 * s
    mark = native.resize((87 * factor, 22 * factor), Image.NEAREST)
    img.alpha_composite(mark, ((W - mark.width) // 2, 24 * s))

    # Tagline + divider.
    d.text((W // 2, 152 * s), TAGLINE, font=font(FONT_TAG, 15 * s),
           fill=rgb(c["copper_dark"], 255), anchor="mm")
    for x in range(56 * s, 844 * s, 12 * s):
        d.rectangle([x, 176 * s, x + 6 * s, 176 * s + max(1, 2 * s) - 1],
                    fill=rgb(c["copper"], 120))

    # Shelves first, so the arrows and text land on top of nothing important.
    for shelf in (APP_SHELF, APPS_SHELF, ZIP_SHELF):
        draw_shelf(img, shelf, s, c)

    # Numbered steps.
    f_title, f_sub = font(FONT_TITLE, 19 * s), font(FONT_SUB, 13 * s)
    for i, ((bx, by), title, sub) in enumerate(STEPS, start=1):
        grid = badge_grid(i)
        unit = 3 * s
        px = bx * s - (len(grid[0]) * unit) // 2
        py = by * s - (len(grid) * unit) // 2
        disc = [row.replace("o", "#") for row in grid]
        pixel_grid(d, disc, px, py, unit,
                   rgb(c["copper"], 255), rgb(c["copper_dark"], 255))
        for gy, row in enumerate(grid):          # punch the digit back out
            for gx, ch in enumerate(row):
                if ch == "o":
                    d.rectangle([px + gx * unit, py + gy * unit,
                                 px + (gx + 1) * unit - 1, py + (gy + 1) * unit - 1],
                                fill=rgb(c["cream"], 255))
        tx = 112 * s
        d.text((tx, by * s - 7 * s), title, font=f_title,
               fill=rgb(c["ink"], 255), anchor="lm")
        d.text((tx, by * s + 16 * s), sub, font=f_sub,
               fill=rgb(c["kettle_dark"], 235), anchor="lm")

        # Nothing may run into a shelf; fail the build rather than ship it ugly.
        right = max(tx + d.textlength(title, font=f_title),
                    tx + d.textlength(sub, font=f_sub))
        for shelf in (APP_SHELF, APPS_SHELF, ZIP_SHELF):
            sx0, sy0 = shelf[0] * s, shelf[1] * s
            sy1 = sy0 + SHELF_H * s
            if sy0 - 8 * s <= by * s <= sy1 + 8 * s and right > sx0 - 12 * s:
                raise SystemExit(
                    f"FATAL: step {i} text (right edge {right / s:.0f}pt) collides "
                    f"with the shelf at x={shelf[0]}pt. Shorten the copy."
                )

    # Arrow: Prism Launcher -> Applications.
    big = arrow_grid(24)
    unit = 5 * s
    ax = (APP_SHELF[0] + SHELF_W + 10) * s
    ay = (APP_SHELF[1] + SHELF_ICON_DY) * s - (len(big) * unit) // 2
    pixel_grid(d, big, ax, ay, unit, rgb(c["copper"], 255), rgb(c["copper_dark"], 255))

    # Arrow: step 3's sentence -> the kettle zip.
    small = arrow_grid(14)
    unit = 4 * s
    sx = 584 * s
    sy = STEPS[2][0][1] * s - (len(small) * unit) // 2
    pixel_grid(d, small, sx, sy, unit, rgb(c["copper"], 255), rgb(c["copper_dark"], 255))

    return img


def write_backgrounds() -> Path:
    c = palette()
    BUILD.mkdir(parents=True, exist_ok=True)
    one = BUILD / "background.png"
    two = BUILD / "background@2x.png"
    build_background(1, c).convert("RGB").save(one, "PNG")
    build_background(2, c).convert("RGB").save(two, "PNG")
    say(f"background.png {WIN_W}x{WIN_H} + @2x {WIN_W * 2}x{WIN_H * 2} "
        "(dmgbuild folds them into one HiDPI .background.tiff)")
    return one


# --------------------------------------------------------------------------
# 4. Volume icon
# --------------------------------------------------------------------------


def build_volume_icon() -> Path | None:
    src = DIST / "CozyTech" / "lkv.png"
    if not src.is_file():
        return None
    iconset = BUILD / "lkv.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    art = Image.open(src).convert("RGBA")          # 128x128 pixel art
    for px, name in ((16, "icon_16x16.png"), (32, "icon_16x16@2x.png"),
                     (32, "icon_32x32.png"), (64, "icon_32x32@2x.png"),
                     (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
                     (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"),
                     (512, "icon_512x512.png"), (1024, "icon_512x512@2x.png")):
        art.resize((px, px), Image.NEAREST).save(iconset / name, "PNG")
    icns = BUILD / "lkv.icns"
    if icns.exists():
        icns.unlink()
    try:
        run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)])
    except subprocess.CalledProcessError as exc:
        say(f"iconutil failed, shipping without a volume icon: {exc.stderr.strip()}")
        return None
    return icns


# --------------------------------------------------------------------------
# 5. Assemble
# --------------------------------------------------------------------------


def build(app: Path, zip_path: Path, background: Path, icns: Path | None) -> None:
    import dmgbuild

    DIST.mkdir(parents=True, exist_ok=True)
    if OUT_DMG.exists():
        OUT_DMG.unlink()

    settings = {
        "format": "UDZO",
        "filesystem": "HFS+",
        "files": [str(app), str(zip_path)],
        "symlinks": {"Applications": "/Applications"},
        "icon": str(icns) if icns else None,
        "background": str(background),
        "window_rect": ((140, 120), (WIN_W, WIN_H)),
        "default_view": "icon-view",
        "show_status_bar": False,
        "show_tab_view": False,
        "show_toolbar": False,
        "show_pathbar": False,
        "show_sidebar": False,
        "show_icon_preview": False,
        "include_icon_view_settings": True,
        "include_list_view_settings": False,
        "arrange_by": None,
        "grid_offset": (0, 0),
        "grid_spacing": 110,
        "scroll_position": (0, 0),
        "label_pos": "bottom",
        "text_size": LABEL_SIZE,
        "icon_size": ICON_SIZE,
        "icon_locations": {k: v for k, v in ICON_LOCATIONS.items()},
        "hide_extension": [],
    }
    dmgbuild.build_dmg(str(OUT_DMG), VOLUME_NAME, settings=settings)


# --------------------------------------------------------------------------
# 6. Verify — headless, no Finder, nothing opens
# --------------------------------------------------------------------------


def verify() -> None:
    print("\nVERIFY  (hdiutil attach -nobrowse -readonly; nothing opens on screen)")
    with Mounted(OUT_DMG) as point:
        listing = run(["ls", "-la", str(point)]).stdout
        print(listing.rstrip())

        names = set(os.listdir(point))
        problems = []
        for want in (APP_NAME, ZIP_NAME, "Applications"):
            if want not in names:
                problems.append(f"missing {want!r} on the volume")
        if "Applications" in names and not os.path.islink(point / "Applications"):
            problems.append("'Applications' is not a symlink")
        elif "Applications" in names:
            say(f"Applications -> {os.readlink(point / 'Applications')}")

        bg = [n for n in names if n.startswith(".background")]
        if not bg:
            problems.append("no .background image on the volume")
        else:
            size = (point / bg[0]).stat().st_size
            say(f"background present: {bg[0]} ({size:,} bytes) "
                "— .tiff because the 1x PNG and its @2x sibling were folded "
                "into one HiDPI image")
        if ".DS_Store" not in names:
            problems.append("no .DS_Store — the window layout would not stick")
        else:
            say(f".DS_Store present ({(point / '.DS_Store').stat().st_size:,} bytes)"
                " — icon positions and background are baked in")
        if ".VolumeIcon.icns" in names:
            say(".VolumeIcon.icns present (kettle volume icon)")

        verify_app_signature(point / APP_NAME, "app on the built volume")
        plist = plistlib.loads((point / APP_NAME / "Contents" / "Info.plist").read_bytes())
        say(f"app version: {plist.get('CFBundleShortVersionString')} "
            f"({plist.get('CFBundleIdentifier')})")

        with zipfile.ZipFile(point / ZIP_NAME) as zf:
            print("\n  unzip -l equivalent for " + ZIP_NAME + ":")
            for info in zf.infolist():
                print(f"    {info.file_size:>9,}  {info.filename}")
            cfg = zf.read("instance.cfg").decode()
            names_in_zip = set(zf.namelist())
            opt = (zf.read(".minecraft/options.txt").decode()
                   if ".minecraft/options.txt" in names_in_zip else None)
        if opt is None:
            problems.append("the instance zip carries no .minecraft/options.txt")
        else:
            # version:3465 is 1.20.1's options format, and it is asserted
            # literally on purpose: the pack is pinned to 1.20.1, and a
            # missing/wrong version line is the exact bug that once made every
            # fresh install silently discard render distance and all 12 keybinds
            # (docs/STATUS.md).  Cheap guard, and it fails loudly if it ever
            # regresses.
            lines = opt.splitlines()
            print(f"\n  .minecraft/options.txt ({len(lines)} lines):")
            for line in lines[:5]:
                print(f"    {line}")
            print("    ...")
            if not lines or lines[0] != "version:3465":
                problems.append("options.txt line 1 is not 'version:3465' "
                                f"(got {lines[0] if lines else '<empty>'!r})")
            if f"renderDistance:{AIR_RENDER_DISTANCE}" not in lines:
                problems.append(f"options.txt is not renderDistance:{AIR_RENDER_DISTANCE}")
            if f"simulationDistance:{AIR_SIMULATION_DISTANCE}" not in lines:
                problems.append(
                    f"options.txt is not simulationDistance:{AIR_SIMULATION_DISTANCE}")
        print("\n  instance.cfg:")
        for line in cfg.splitlines():
            print(f"    {line}")
        if f"MaxMemAlloc={MAX_MEM_MB}" not in cfg:
            problems.append(f"instance.cfg is not MaxMemAlloc={MAX_MEM_MB}")
        if f"MinMemAlloc={MIN_MEM_MB}" not in cfg:
            problems.append(f"instance.cfg is not MinMemAlloc={MIN_MEM_MB}")
        if "JavaPath" in cfg or "OverrideJavaLocation" in cfg:
            problems.append("instance.cfg still pins Java")

    if not (BUILD / "background.png").is_file():
        problems.append("installers/macos/build/background.png was not written")

    if problems:
        raise SystemExit("\nFAILED:\n" + "\n".join(f"  - {p}" for p in problems))
    print("\n  all checks passed")


# --------------------------------------------------------------------------


def main() -> None:
    verify_only = "--verify-only" in sys.argv
    if not verify_only:
        print("BUILD  Little Kettle Valley.dmg")
        app = stage_prism_app()
        zip_path = build_instance_zip()
        background = write_backgrounds()
        icns = build_volume_icon()
        build(app, zip_path, background, icns)
    if not OUT_DMG.is_file():
        raise SystemExit(f"FATAL: {OUT_DMG} does not exist")

    verify()

    size = OUT_DMG.stat().st_size
    digest = sha256_of(OUT_DMG)
    print("\n" + "-" * 72)
    print(f"  {OUT_DMG}")
    print(f"  size    {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
    print(f"  sha256  {digest}")
    print("-" * 72)


if __name__ == "__main__":
    main()
