#!/usr/bin/env python3
"""Little Kettle Valley - title screen logo + edition strip builder.

Hand-authored pixel-art wordmark (no vanilla Minecraft artwork reused -
this is an original blocky font drawn glyph-by-glyph for just the letters
the two lines need) plus the kettle mark from media/icon/build.py used as
a small crest above the title.

Outputs (in this folder):
  minecraft.png  1024x256 RGBA  title-screen logo (game draws rows 0-175
                  as a 274x44 logo; rows 176-255 stay fully transparent)
  edition.png    512x64  RGBA  small "FORGE 1.20.1" strip under the logo
                  (game draws rows 0-54 as a 128x14 strip)

Run: tools/venv/bin/python media/logo/build.py
"""
import importlib.util
import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
PAL = json.loads((ROOT / "media" / "palette.json").read_text())


def hexrgba(name, alpha=255):
    h = PAL["colors"][name].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


# --- load the kettle mark from media/icon/build.py (reuse the brand mark) --
_spec = importlib.util.spec_from_file_location("_icon_build", ROOT / "media" / "icon" / "build.py")
_icon = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_icon)


# --- an original 7x9 blocky pixel font, hand-drawn per glyph --------------
GW, GH = 7, 9
FONT = {
    "L": ["#......", "#......", "#......", "#......", "#......", "#......", "#......", "#......", "#######"],
    "I": ["#######", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "#######"],
    "T": ["#######", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "...#...", "...#..."],
    "E": ["#######", "#......", "#......", "#......", "#####..", "#......", "#......", "#......", "#######"],
    "K": ["#.....#", "#....#.", "#...#..", "#..#...", "##.....", "#..#...", "#...#..", "#....#.", "#.....#"],
    "V": ["#.....#", "#.....#", ".#...#.", ".#...#.", "..#.#..", "..#.#..", "...#...", "...#...", "...#..."],
    "A": ["..###..", ".#...#.", "#.....#", "#.....#", "#######", "#.....#", "#.....#", "#.....#", "#.....#"],
    "Y": ["#.....#", ".#...#.", "..#.#..", "...#...", "...#...", "...#...", "...#...", "...#...", "...#..."],
    "F": ["#######", "#......", "#......", "#......", "#####..", "#......", "#......", "#......", "#......"],
    "O": [".#####.", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", "#.....#", ".#####."],
    "R": ["#####..", "#....#.", "#....#.", "#####..", "#..#...", "#...#..", "#....#.", "#....#.", "#.....#"],
    "G": [".#####.", "#.....#", "#......", "#......", "#..####", "#.....#", "#.....#", "#.....#", ".#####."],
    "0": [".#####.", "#.....#", "#....##", "#...#.#", "#..#..#", "#.#...#", "##....#", "#.....#", ".#####."],
    "1": ["..##...", ".###...", "..#....", "..#....", "..#....", "..#....", "..#....", "..#....", "#######"],
    "2": [".#####.", "#.....#", "......#", ".....#.", "....#..", "...#...", "..#....", ".#.....", "#######"],
    ".": [".......", ".......", ".......", ".......", ".......", ".......", ".......", "..##...", "..##..."],
    " ": None,
}
SPACE_W = 4


def text_mask(s):
    """Native-resolution (1 font-px = 1 array-px) boolean grid for a string."""
    cols = []
    for ch in s:
        g = FONT[ch]
        cols.append(GW if g else SPACE_W)
    width = sum(cols) + (len(s) - 1)  # 1px gap between glyphs
    grid = [[False] * width for _ in range(GH)]
    x = 0
    for ch, w in zip(s, cols):
        g = FONT[ch]
        if g:
            for y, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == "#":
                        grid[y][x + i] = True
        x += w + 1
    return grid, width, GH


def render_wordmark(text, scale, fill, shadow, outline, highlight, shadow_off=1):
    """Build an RGBA image of `text` at native res then scale NEAREST.
    Layers (native res, back to front): outline (dilated ink), drop shadow
    (offset down-right), flat fill, top/left bevel highlight edge."""
    grid, w, h = text_mask(text)
    pad = 2
    W, H = w + pad * 2 + shadow_off, h + pad * 2 + shadow_off
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()

    def on(x, y):
        gx, gy = x - pad, y - pad
        return 0 <= gx < w and 0 <= gy < h and grid[gy][gx]

    # outline: any transparent px 4-adjacent to a filled px (own layer + shadow layer)
    for y in range(H):
        for x in range(W):
            if on(x, y) or on(x - shadow_off, y - shadow_off):
                continue
            near = any(on(x + dx, y + dy) or on(x - shadow_off + dx, y - shadow_off + dy)
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if near:
                px[x, y] = outline

    # drop shadow
    for y in range(H):
        for x in range(W):
            if on(x - shadow_off, y - shadow_off):
                px[x, y] = shadow

    # flat fill + bevel highlight (top/left edge of each glyph pixel)
    for y in range(H):
        for x in range(W):
            if on(x, y):
                edge = not on(x - 1, y) or not on(x, y - 1)
                px[x, y] = highlight if edge else fill

    return im.resize((W * scale, H * scale), Image.NEAREST)


def outline_rgba(im, color, size=1):
    """Return a same-size RGBA with `color` filled 1px around im's alpha,
    for pasting *behind* im (contrast against a busy background)."""
    W, H = im.size
    src = im.load()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dst = out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3] > 20:
                continue
            near = False
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy < H and src[xx, yy][3] > 20:
                        near = True
                        break
                if near:
                    break
            if near:
                dst[x, y] = color
    return out


def build_minecraft_png():
    canvas = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))

    copper = hexrgba("copper")
    copper_light = hexrgba("copper_light")
    copper_dark = hexrgba("copper_dark")
    ink = hexrgba("ink")

    title = render_wordmark(
        "LITTLE KETTLE VALLEY", scale=5,
        fill=copper, shadow=copper_dark, outline=ink, highlight=copper_light,
    )

    # kettle crest, reused from the icon mark, with its own ink halo so it
    # stays legible over any panorama tile behind it
    CREST = 64
    mark = _icon.build_mark().resize((CREST, CREST), Image.NEAREST)
    halo = outline_rgba(mark, ink, size=2)

    tx = (1024 - title.width) // 2
    mx = (1024 - CREST) // 2
    my = 8
    ty = my + CREST + 14

    canvas.alpha_composite(halo, (mx - 2, my - 2))
    canvas.alpha_composite(mark, (mx, my))
    canvas.alpha_composite(title, (tx, ty))

    assert ty + title.height <= 176, f"title bottom {ty + title.height} exceeds row 175 budget"
    canvas.save(OUT / "minecraft.png")

    # verify rows 176-255 are fully transparent, per the media brief
    px = canvas.load()
    for y in range(176, 256):
        for x in range(0, 1024, 8):
            assert px[x, y][3] == 0, f"row {y} not transparent at x={x}"
    print(f"minecraft.png -> {canvas.size}, title {title.size} @ ({tx},{ty}), crest @ ({mx},{my})")


def build_edition_png():
    canvas = Image.new("RGBA", (512, 64), (0, 0, 0, 0))
    sage = hexrgba("sage")
    sage_dark = hexrgba("sage_dark")
    ink = hexrgba("ink")
    cream = hexrgba("cream")

    strip = render_wordmark(
        "FORGE 1.20.1", scale=3,
        fill=sage, shadow=sage_dark, outline=ink, highlight=cream,
    )
    x = (512 - strip.width) // 2
    y = (54 - strip.height) // 2
    canvas.alpha_composite(strip, (x, y))
    assert y + strip.height <= 54
    canvas.save(OUT / "edition.png")
    print(f"edition.png -> {canvas.size}, strip {strip.size} @ ({x},{y})")


def main():
    build_minecraft_png()
    build_edition_png()

    with Image.open(OUT / "minecraft.png") as im:
        assert im.size == (1024, 256) and im.mode == "RGBA"
    with Image.open(OUT / "edition.png") as im:
        assert im.size == (512, 64) and im.mode == "RGBA"

    # quick contact preview for art-direction review
    prev = Image.new("RGBA", (1024, 256 + 64 + 20), hexrgba("night"))
    prev.alpha_composite(Image.open(OUT / "minecraft.png"), (0, 0))
    prev.alpha_composite(Image.open(OUT / "edition.png"), (256, 276))
    prev.save(OUT / "_preview.png")
    print("built minecraft.png + edition.png ->", OUT)


if __name__ == "__main__":
    main()
