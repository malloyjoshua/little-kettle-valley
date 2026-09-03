#!/usr/bin/env python3
"""Builder for Little Kettle Valley batch3 item icons (16x16 DSL grids).
Run: tools/venv/bin/python media/items/build_batch3.py
Writes media/items/batch3.json, then use tools/scripts/pixel.py to render/check/sheet.
NOTE: filename is batch3-specific (not build.py) because other concurrent
batches share this items/ directory and each writes its own build script.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "media" / "items" / "batch3.json"

def new_grid():
    return [['.' for _ in range(16)] for _ in range(16)]

def set_(g, x, y, ch):
    if 0 <= x < 16 and 0 <= y < 16:
        g[y][x] = ch

def rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            set_(g, x, y, ch)

def border(g, x0, y0, x1, y1, ch):
    for x in range(x0, x1 + 1):
        set_(g, x, y0, ch); set_(g, x, y1, ch)
    for y in range(y0, y1 + 1):
        set_(g, x0, y, ch); set_(g, x1, y, ch)

def hline(g, x0, x1, y, ch):
    for x in range(x0, x1 + 1):
        set_(g, x, y, ch)

def vline(g, x0, y0, y1, ch):
    for y in range(y0, y1 + 1):
        set_(g, x0, y, ch)

def rows(g):
    return [''.join(r) for r in g]

icons = []

def add(name, g):
    icons.append({"name": name, "rows": rows(g)})

# ---------- shared crate base ----------
def crate_base(open_top=False, top_y=6):
    g = new_grid()
    x0, y0, x1, y1 = 2, 6, 13, 13
    if open_top:
        y0 = top_y
    rect(g, x0, y0, x1, y1, 'o')
    border(g, x0, y0, x1, y1, 'O')
    hline(g, x0, x1, (y0 + y1) // 2 + 1, 'O')  # plank seam
    for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        set_(g, cx, cy, 'C'); set_(g, cx + dx, cy, 'C'); set_(g, cx, cy + dy, 'C')
    return g, x0, y0, x1, y1

# ---------- 1. delivery_crate ----------
g, x0, y0, x1, y1 = crate_base()
rect(g, 5, 9, 10, 11, 'p')
border(g, 5, 9, 10, 11, 'D')
hline(g, 6, 9, 10, 'i')
add('delivery_crate', g)

# ---------- 2. courier_parcel ----------
g = new_grid()
x0, y0, x1, y1 = 3, 5, 12, 12
rect(g, x0, y0, x1, y1, 'p')
border(g, x0, y0, x1, y1, 'D')
vline(g, 7, y0, y1, 'o'); vline(g, 8, y0, y1, 'o')   # twine, vertical
hline(g, x0, x1, 8, 'o'); hline(g, x0, x1, 9, 'o')    # twine, horizontal
# bow loops sitting on the top edge
rect(g, 5, 3, 6, 4, 'o'); rect(g, 9, 3, 10, 4, 'o')
border(g, 5, 3, 6, 4, 'D'); border(g, 9, 3, 10, 4, 'D')
rect(g, 7, 4, 8, 4, 'D')  # knot
# wax seal centered on the twine cross
rect(g, 6, 7, 9, 10, 'C')
border(g, 6, 7, 9, 10, 'D')
set_(g, 7, 8, 'L')
add('courier_parcel', g)

# ---------- 3. feast_crate ----------
g, x0, y0, x1, y1 = crate_base(open_top=True, top_y=9)
# bread loaf peeking (rounded dome via inset top rows)
rect(g, 4, 6, 9, 8, 'L')
hline(g, 5, 8, 5, 'L')
border(g, 4, 6, 9, 8, 'D')
set_(g, 5, 5, 'D'); set_(g, 8, 5, 'D')
hline(g, 5, 8, 7, 'D')  # score line
# apple peeking, off to the right
rect(g, 10, 6, 13, 9, 'r')
border(g, 10, 6, 13, 9, 'D')
set_(g, 11, 5, 'g'); set_(g, 12, 4, 'g')
set_(g, 11, 7, 'u')  # highlight
add('feast_crate', g)

# ---------- 4. hen_crate ----------
g, x0, y0, x1, y1 = crate_base(open_top=True, top_y=9)
rect(g, 6, 4, 9, 9, 'c')     # hen head (cream/white)
border(g, 6, 4, 9, 9, 'D')
# zig-zag comb
hline(g, 6, 9, 3, 'r')
set_(g, 6, 2, 'r'); set_(g, 9, 2, 'r'); set_(g, 7, 2, 'i')
# beak + wattle
rect(g, 9, 6, 10, 7, 'y')
set_(g, 8, 8, 'r')
set_(g, 7, 6, 'i')  # eye
add('hen_crate', g)

# ---------- 5. cow_crate ----------
g, x0, y0, x1, y1 = crate_base(open_top=True, top_y=9)
rect(g, 5, 4, 10, 9, 'W')    # cow head white
border(g, 5, 4, 10, 9, 'D')
set_(g, 6, 3, 'c'); set_(g, 9, 3, 'c')  # small horn nubs
rect(g, 5, 4, 6, 5, 'i')     # patch (top-left, off-center)
rect(g, 9, 8, 10, 9, 'i')    # patch (bottom-right, off-center)
hline(g, 6, 9, 8, 'h')       # muzzle blush
set_(g, 6, 7, 'i'); set_(g, 9, 7, 'i')  # eyes, clear of patches
set_(g, 7, 8, 'i'); set_(g, 8, 8, 'i')  # nostrils
add('cow_crate', g)

# ---------- 6. sheep_crate ----------
g, x0, y0, x1, y1 = crate_base(open_top=True, top_y=9)
rect(g, 5, 3, 10, 8, 'W')    # wool fluff
border(g, 5, 3, 10, 8, 'D')
set_(g, 4, 5, 'W'); set_(g, 11, 5, 'W')  # fluff bumps
set_(g, 4, 4, 'W'); set_(g, 11, 4, 'W')
rect(g, 7, 6, 8, 8, 'h')     # face
set_(g, 7, 7, 'i'); set_(g, 8, 7, 'i')
add('sheep_crate', g)

# ---------- 7. chicken_feed ----------
g = new_grid()
sack = [
    (7,4),(8,4),
    (6,5),(9,5),
    (5,6),(10,6),
    (5,7),(10,7),
    (4,8),(11,8),
    (4,9),(11,9),
    (4,10),(11,10),
    (5,11),(10,11),
    (6,12),(9,12),
    (7,13),(8,13),
]
xs = {}
for x, y in sack:
    xs.setdefault(y, []).append(x)
for y, xlist in xs.items():
    lo, hi = min(xlist), max(xlist)
    hline(g, lo, hi, y, 'o')
for x, y in sack:
    set_(g, x, y, 'O')
# neck tie
rect(g, 6, 3, 9, 4, 'O')
set_(g, 7, 2, 'D'); set_(g, 8, 2, 'D')
# grain, tight cluster right above the tie
set_(g, 7, 1, 'y'); set_(g, 8, 1, 'G')
set_(g, 6, 2, 'G'); set_(g, 9, 2, 'y')
add('chicken_feed', g)

# ---------- 8. firewood_bundle ----------
g = new_grid()
def log(g, x0, y0, length, ch_bark, ch_end):
    rect(g, x0, y0, x0 + length - 1, y0 + 2, ch_bark)
    vline(g, x0, y0, y0 + 2, ch_end)
    set_(g, x0, y0 + 1, ch_end)
log(g, 3, 4, 11, 'o', 'O')
log(g, 3, 7, 11, 'L', 'D')
log(g, 3, 10, 11, 'o', 'O')
# rope ties
vline(g, 5, 3, 13, 'D')
vline(g, 10, 3, 13, 'D')
add('firewood_bundle', g)

# ---------- 9. blanket ----------
g = new_grid()
rect(g, 2, 5, 13, 13, 'W')
border(g, 2, 5, 13, 13, 'O')
hline(g, 2, 13, 8, 's')
hline(g, 2, 13, 11, 'r')
# folded-back corner (bottom right), like a peeled blanket corner
for (x, y) in [(11,12),(12,12),(13,12),(12,13),(13,13),(13,11)]:
    set_(g, x, y, 'S')
set_(g, 13, 13, 'T')
add('blanket', g)

# ---------- 10. winter_cloak ----------
g = new_grid()
rect(g, 6, 2, 9, 4, 's')
border(g, 6, 2, 9, 4, 'S')
rect(g, 7, 3, 8, 3, 'i')
body = {5:(6,9), 6:(5,10), 7:(5,10), 8:(4,11), 9:(4,11), 10:(3,12), 11:(3,12), 12:(3,12), 13:(2,13)}
for y,(lo,hi) in body.items():
    hline(g, lo, hi, y, 's')
for y,(lo,hi) in body.items():
    set_(g, lo, y, 'S'); set_(g, hi, y, 'S')
set_(g, 7, 5, 'C'); set_(g, 8, 5, 'C')
add('winter_cloak', g)

# ---------- 11. winter_tonic ----------
g = new_grid()
rect(g, 7, 2, 8, 3, 'o')
border(g, 7, 2, 8, 3, 'O')
rect(g, 7, 4, 8, 5, 'V')
rect(g, 5, 6, 10, 12, 'V')
border(g, 5, 6, 10, 12, 'T')
rect(g, 6, 8, 9, 11, 'y')
hline(g, 6, 9, 8, 'L')
set_(g, 6, 7, 'w')
add('winter_tonic', g)

# ---------- 12. winter_tomato ----------
g = new_grid()
rect(g, 4, 6, 11, 12, 'r')
border(g, 4, 6, 11, 12, 'D')
for (x,y) in [(4,6),(11,6),(4,12),(11,12)]:
    set_(g, x, y, '.')
set_(g, 5,6,'D'); set_(g, 10,6,'D'); set_(g, 5,12,'D'); set_(g, 10,12,'D')
set_(g, 4,7,'D'); set_(g, 11,7,'D'); set_(g, 4,11,'D'); set_(g, 11,11,'D')
rect(g, 6, 7, 7, 8, 'u')  # highlight
# jagged calyx (stem + notched leaf points)
set_(g, 7, 3, 'g'); set_(g, 8, 3, 'g')
set_(g, 6, 4, 'g'); set_(g, 9, 4, 'g')
hline(g, 5, 10, 5, 'g')
add('winter_tomato', g)

OUT.write_text(json.dumps(icons, indent=2))
print(f"wrote {len(icons)} icons -> {OUT}")
