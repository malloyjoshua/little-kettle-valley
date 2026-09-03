#!/usr/bin/env python3
"""Pixel-art DSL renderer for Little Kettle Valley.
Usage:
  pixel.py render <icons.json> <out_dir>        # each icon: {"name": ..., "rows": [16 strings of 16 chars]}
  pixel.py sheet <png_dir> <out.png> [scale]     # contact sheet with labels
  pixel.py check <png_dir>                        # verify every png is 16x16 RGBA
Palette letters are defined in media/palette.json ("dsl" maps a letter to a color name).
"""
import sys, json, pathlib
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[2]
PAL = json.loads((ROOT / 'media' / 'palette.json').read_text())
def hex2rgba(h): h = h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), 255)
LETTERS = {k: (hex2rgba(PAL['colors'][v]) if v else (0,0,0,0)) for k, v in PAL['dsl'].items()}
def render(spec, out_dir):
    out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); n = 0; errs = []
    for icon in spec:
        rows = icon['rows']
        if len(rows) != 16 or any(len(r) != 16 for r in rows): errs.append(f"{icon['name']}: must be 16 rows of 16 chars"); continue
        im = Image.new('RGBA', (16, 16), (0,0,0,0)); px = im.load()
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch not in LETTERS: errs.append(f"{icon['name']}: unknown letter {ch!r} at {x},{y}"); ch = '.'
                px[x, y] = LETTERS[ch]
        im.save(out_dir / f"{icon['name']}.png"); n += 1
    print(f"rendered {n} icons -> {out_dir}"); [print('ERROR', e) for e in errs]; return 1 if errs else 0
def sheet(png_dir, out, scale=8):
    files = sorted(pathlib.Path(png_dir).glob('*.png')); cols = 8; cell = 16*scale + 8; lab = 14
    rows = (len(files) + cols - 1) // cols
    im = Image.new('RGBA', (cols*cell, rows*(cell+lab)), (40, 36, 32, 255)); d = ImageDraw.Draw(im)
    for i, f in enumerate(files):
        ic = Image.open(f).convert('RGBA').resize((16*scale, 16*scale), Image.NEAREST)
        x = (i % cols) * cell + 4; y = (i // cols) * (cell + lab) + 4
        d.rectangle([x-1, y-1, x+16*scale, y+16*scale], fill=(60, 56, 50, 255))
        im.alpha_composite(ic, (x, y)); d.text((x, y + 16*scale + 2), f.stem[:18], fill=(230, 220, 200, 255))
    im.save(out); print(f"sheet {len(files)} icons -> {out}")
def check(png_dir):
    bad = 0
    for f in sorted(pathlib.Path(png_dir).glob('*.png')):
        im = Image.open(f)
        if im.size != (16, 16) or im.mode != 'RGBA': print('BAD', f.name, im.size, im.mode); bad += 1
    print('checked', len(list(pathlib.Path(png_dir).glob('*.png'))), 'bad', bad); return 1 if bad else 0
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render': sys.exit(render(json.loads(pathlib.Path(sys.argv[2]).read_text()), sys.argv[3]))
    if cmd == 'sheet': sheet(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 8)
    if cmd == 'check': sys.exit(check(sys.argv[2]))
