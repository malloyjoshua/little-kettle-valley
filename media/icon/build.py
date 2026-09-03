#!/usr/bin/env python3
"""Little Kettle Valley - launcher/server icon builder.

Hand-authored 32x32 pixel art (a copper kettle on a cream badge) built with
shape math (rounded-rect masks, ellipses, a hand-drawn heart bitmap for the
top steam puff) rather than the 16x16 DSL grid in pixel.py, since this icon
needs a 32px canvas. Colors are still pulled straight from media/palette.json
so the icon stays on-palette with the rest of the pack.

Outputs (in this folder):
  icon_32.png    32x32   launcher tile
  icon_64.png    64x64   Forge/Minecraft server-icon.png size
  icon_128.png   128x128 Prism/MultiMC instance icon
  icon_512.png   512x512 store-quality / press-kit size
  mark_128.png / mark_512.png   kettle mark alone, transparent background

Run: tools/venv/bin/python media/icon/build.py
"""
import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
PAL = json.loads((ROOT / "media" / "palette.json").read_text())


def hexrgba(name, alpha=255):
    h = PAL["colors"][name].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


N = 32  # native canvas size


def blank():
    return Image.new("RGBA", (N, N), (0, 0, 0, 0))


def set_px(px, x, y, color):
    if 0 <= x < N and 0 <= y < N:
        px[x, y] = color


def rounded_rect_mask(x0, y0, x1, y1, r):
    """Return a function(x,y) -> bool for a filled rounded rect, corners cut
    with a simple circular test (crisp, no anti-aliasing -> stays pixel art)."""
    def inside(x, y):
        if x < x0 or x > x1 or y < y0 or y > y1:
            return False
        # which corner zone (if any)?
        cx = None
        cy = None
        if x < x0 + r:
            cx = x0 + r
        elif x > x1 - r:
            cx = x1 - r
        if y < y0 + r:
            cy = y0 + r
        elif y > y1 - r:
            cy = y1 - r
        if cx is None or cy is None:
            return True
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy <= r * r + r * 0.15
    return inside


def ellipse_mask(cx, cy, rx, ry):
    def inside(x, y):
        dx = (x - cx) / rx
        dy = (y - cy) / ry
        return dx * dx + dy * dy <= 1.0
    return inside


def stamp(px, bitmap, ox, oy, color, alpha=255):
    """bitmap: list of strings, 'X' = filled pixel, offset at (ox, oy)."""
    c = (color[0], color[1], color[2], alpha)
    for j, row in enumerate(bitmap):
        for i, ch in enumerate(row):
            if ch == "X":
                set_px(px, ox + i, oy + j, c)


# --- hand-drawn steam bitmaps -------------------------------------------
STEAM_PUFF = [
    ".XXX.",
    "XXXXX",
    "XXXXX",
    "XXXXX",
    ".XXX.",
]

STEAM_HEART = [
    ".X.X.",
    "XXXXX",
    "XXXXX",
    ".XXX.",
    "..X..",
]


def build_badge():
    """Cream rounded-square badge with a sage rim (background layer)."""
    im = blank()
    px = im.load()
    cream = hexrgba("cream")
    sage = hexrgba("sage")
    outer = rounded_rect_mask(1, 1, 30, 30, 7)
    inner = rounded_rect_mask(3, 3, 28, 28, 6)
    for y in range(N):
        for x in range(N):
            if inner(x, y):
                set_px(px, x, y, cream)
            elif outer(x, y):
                set_px(px, x, y, sage)
    return im


def draw_kettle(px, ox=0, oy=0):
    """Draws the kettle mark. (ox, oy) shifts the whole mark (used to nudge
    it for the badge vs. the standalone transparent mark)."""
    copper = hexrgba("copper")
    copper_light = hexrgba("copper_light")
    copper_dark = hexrgba("copper_dark")
    kdark = hexrgba("kettle_dark")
    cream = hexrgba("cream")
    steam_c = hexrgba("steam", 235)
    blush = hexrgba("blush", 235)

    cx, cy = 14 + ox, 21 + oy  # body center, left of canvas center (steam rises to the right)

    # body: a squat rounded belly, wider than tall
    body = ellipse_mask(cx, cy, 7, 5)
    # shading split: darker lower-right, lighter upper-left highlight zone
    shade = ellipse_mask(cx + 2, cy + 2, 7, 5)
    highlight = ellipse_mask(cx - 3, cy - 2, 2.6, 1.8)
    for y in range(cy - 6, cy + 7):
        for x in range(cx - 8, cx + 9):
            if not body(x, y):
                continue
            if highlight(x, y):
                set_px(px, x, y, cream)
            elif shade(x, y):
                set_px(px, x, y, copper_dark)
            else:
                set_px(px, x, y, copper)

    # thin copper_light rim stroke along the very top-left edge of the body
    for y in range(cy - 6, cy + 7):
        for x in range(cx - 8, cx + 9):
            if body(x, y) and not ellipse_mask(cx, cy, 6.1, 4.1)(x, y) and not shade(x, y):
                set_px(px, x, y, copper_light)

    # base foot (kettle sits on a short dark ring)
    for x in range(cx - 5, cx + 6):
        set_px(px, x, cy + 5, kdark)
        set_px(px, x, cy + 6, kdark)

    # lid: a slim flat band sitting right on the body's apex (short, so it
    # reads as one vessel rather than a separate blob stacked on top)
    lid_top = cy - 7
    for y in range(lid_top, cy - 5):
        for x in range(cx - 2, cx + 3):
            set_px(px, x, y, kdark)

    # knob: a tiny single-pixel-wide cap, kept small on purpose (a bigger
    # round knob plus the handle's two feet reads as a face at this size)
    set_px(px, cx - 1, lid_top - 1, kdark)
    set_px(px, cx, lid_top - 1, kdark)
    set_px(px, cx, lid_top - 2, kdark)

    # handle: one thin overhead arc, feet planted low on the body's own
    # shoulders (not on the lid) so it forms a single wide arch over the
    # whole lid+knob rather than two tight symmetric loops either side
    foot_y = cy - 3
    handle_outer = ellipse_mask(cx, foot_y, 6.2, 6.2)
    handle_inner = ellipse_mask(cx, foot_y, 5.0, 5.0)
    for y in range(foot_y - 6, foot_y + 1):
        for x in range(cx - 7, cx + 8):
            if handle_outer(x, y) and not handle_inner(x, y):
                set_px(px, x, y, kdark)

    # spout: diagonal wedge jutting up-right from the body, dark tip
    spout_root = (cx + 6, cy - 1)
    spout_tip = (cx + 8, cy - 5)
    steps = 7
    for i in range(steps):
        t = i / (steps - 1)
        sx = round(spout_root[0] + t * (spout_tip[0] - spout_root[0]))
        sy = round(spout_root[1] + t * (spout_tip[1] - spout_root[1]))
        w = max(1, 2 - i // 4)
        color = kdark if i >= steps - 2 else copper
        for dy in range(-w, w + 1):
            set_px(px, sx, sy + dy, color)
    # small dark spout hole at the very tip
    set_px(px, spout_tip[0] - 1, spout_tip[1], kdark)
    set_px(px, spout_tip[0], spout_tip[1], kdark)

    # steam: two puffs rising diagonally up-right from the spout tip, bottom
    # plain, top puff heart-shaped in blush pink
    puff_x, puff_y = spout_tip[0] - 2, spout_tip[1] - 6
    stamp(px, STEAM_PUFF, puff_x, puff_y, steam_c[:3], alpha=235)
    heart_x, heart_y = puff_x + 2, puff_y - 5
    stamp(px, STEAM_HEART, heart_x, heart_y, blush[:3], alpha=235)


def build_icon():
    im = build_badge()
    px = im.load()
    draw_kettle(px)
    return im


def build_mark():
    im = blank()
    px = im.load()
    draw_kettle(px)
    return im


def save_scaled(im, size, path):
    im.resize((size, size), Image.NEAREST).save(path)


def main():
    icon = build_icon()
    mark = build_mark()

    save_scaled(icon, 32, OUT / "icon_32.png")
    save_scaled(icon, 64, OUT / "icon_64.png")
    save_scaled(icon, 128, OUT / "icon_128.png")
    save_scaled(icon, 512, OUT / "icon_512.png")

    save_scaled(mark, 128, OUT / "mark_128.png")
    save_scaled(mark, 512, OUT / "mark_512.png")

    # sanity checks: server icon must be exactly 64x64 RGBA
    with Image.open(OUT / "icon_64.png") as check:
        assert check.size == (64, 64) and check.mode == "RGBA", "icon_64.png must be 64x64 RGBA"

    # a flat contact-sheet preview for quick art-director review
    preview = Image.new("RGBA", (32 * 6 + 40, 32 * 6 + 20), hexrgba("night"))
    preview.alpha_composite(icon.resize((32 * 6, 32 * 6), Image.NEAREST), (10, 10))
    preview.save(OUT / "_preview_32_at_6x.png")

    print("built icon_32/64/128/512.png + mark_128/512.png ->", OUT)


if __name__ == "__main__":
    main()
