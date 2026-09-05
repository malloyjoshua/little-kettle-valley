#!/usr/bin/env python3
"""render_oblique.py -- a 3/4 view of the valley, so a human can see whether it sits on the land.

The top-down map (scratch/render_map.py) proves WHERE things are. It cannot show a plinth: a
23x23 pad cut five blocks proud of the ground reads as a flat green square from above and as a
grey cliff with a green lid from the side. This draws the side.

  tools/venv/bin/python tools/scripts/render_oblique.py --cx -300 --cz 140 --r 130 \
      --out media/site_oblique.png --dir se --title "Little Kettle Valley"

  --dir  the corner the camera stands in: nw | ne | sw | se (default se, i.e. looking north-west)
  --px   pixels per block along the ground (default 4)
  --vy   pixels per block of height (default 5; raise it to exaggerate relief)

Columns are read from the chunk heightmaps and the top block's id, exactly like render_map.py, so
a 260x260 window renders in seconds. Painter's algorithm, far rows first; every column is drawn as
a top face plus a lit left face and a darker right face, so a vertical cut edge shows as a wall.
"""
import sys, json, math, argparse, pathlib
sys.path.insert(0, 'scratch'); sys.path.insert(0, 'tools/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import vt_lib as V
import seed_hunt as SH

ap = argparse.ArgumentParser()
ap.add_argument('--cx', type=int, required=True)
ap.add_argument('--cz', type=int, required=True)
ap.add_argument('--r', type=int, default=120)
ap.add_argument('--px', type=int, default=4)
ap.add_argument('--vy', type=float, default=5.0)
ap.add_argument('--dir', default='se', choices=['nw', 'ne', 'sw', 'se'])
ap.add_argument('--world', default='server/world')
ap.add_argument('--out', default='media/site_oblique.png')
ap.add_argument('--title', default=None)
ap.add_argument('--mark', action='append', default=[], help='name:x,y,z')
args = ap.parse_args()

WORLD = pathlib.Path(args.world)
_rcache = {}
def _chunk(cx, cz):
    rk = (cx >> 5, cz >> 5)
    if rk not in _rcache:
        q = WORLD / 'region' / ('r.%d.%d.mca' % rk)
        _rcache[rk] = SH.read_region(q) if q.exists() else {}
    return _rcache[rk].get((cx & 31, cz & 31))
V.chunk = _chunk
V._sec = {}

X0, X1 = args.cx - args.r, args.cx + args.r
Z0, Z1 = args.cz - args.r, args.cz + args.r
NX, NZ = X1 - X0 + 1, Z1 - Z0 + 1

hs, _, _ = SH.heights_box(str(WORLD), X0, X1, Z0, Z1, 'WORLD_SURFACE')
of, _, _ = SH.heights_box(str(WORLD), X0, X1, Z0, Z1, 'OCEAN_FLOOR')
mb, _, _ = SH.heights_box(str(WORLD), X0, X1, Z0, Z1, 'MOTION_BLOCKING')

FAM = [
 (('createdeco:', 'lamp', 'lantern', 'torch', 'campfire', 'glowstone', 'sea_lantern', 'shroomlight'), (255, 200, 80)),
 (('water',), (56, 104, 196)),
 (('ice', 'powder_snow', 'snow'), (238, 243, 250)),
 (('glass',), (170, 214, 232)),
 (('leaves', 'azalea'), (60, 118, 50)),
 (('grass_block', 'moss', 'podzol', 'fern', 'grass', 'vine', 'lily', 'sugar_cane', 'wheat',
   'crop', 'carrot', 'potato', 'beetroot', 'melon', 'pumpkin', 'hay', 'bamboo', 'sapling',
   'flower', 'tulip', 'daisy', 'rose', 'orchid', 'cornflower', 'dandelion', 'poppy',
   'allium', 'bluet', 'pink_petals'), (112, 160, 78)),
 (('gravel', 'dirt_path', 'coarse_dirt', 'sand', 'farmland', 'mud', 'clay', 'rooted_dirt', 'dirt'), (184, 161, 122)),
 (('log', 'planks', 'wood', 'fence', 'barrel', 'chest', 'trapdoor', 'door', 'sign', 'ladder',
   'bookshelf', 'crafting', 'loom', 'lectern', 'composter', 'beehive', 'table', 'chair',
   'bed', 'scaffold', 'cherry'), (142, 98, 56)),
 (('cobblestone', 'stone', 'andesite', 'granite', 'diorite', 'brick', 'deepslate', 'tuff',
   'basalt', 'blackstone', 'furnace', 'smoker', 'anvil', 'bell', 'cauldron', 'copper',
   'iron', 'wall', 'slab', 'stairs', 'gate'), (148, 148, 152)),
]
DEF = (108, 104, 100)
def colour(bid):
    b = bid.split('[')[0]
    for keys, c in FAM:
        for k in keys:
            if k in b:
                return c
    return DEF

SKIP = ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'NOCHUNK', 'minecraft:structure_void')

# top block id per column, from the heightmap
top = {}
for ix in range(NX):
    for iz in range(NZ):
        y = int(hs[ix, iz])
        if y < -900:
            continue
        x, z = X0 + ix, Z0 + iz
        got = None
        for yy in range(y, y - 6, -1):
            b = V.block(x, yy, z)
            if b not in SKIP:
                got = (b, yy)
                break
        if got:
            top[(ix, iz)] = got

if not top:
    raise SystemExit('nothing generated in that window')

ys = [v[1] for v in top.values()]
YMIN, YMAX = min(ys), max(ys)

# Camera. The far corner is drawn first. `dir` names where the camera stands, so from 'se'
# we look toward -x/-z and the far corner is (X0, Z0).
flip_x = args.dir in ('sw', 'nw')   # camera on the -x side -> +x is "near" in screen terms
flip_z = args.dir in ('ne', 'nw')

PX, VY = args.px, args.vy
def proj(ix, iz, y):
    a = (NX - 1 - ix) if flip_x else ix
    b = (NZ - 1 - iz) if flip_z else iz
    sx = (a - b) * PX
    sy = (a + b) * PX * 0.5 - (y - YMIN) * VY
    return sx, sy

corners = [proj(i, j, y) for i in (0, NX - 1) for j in (0, NZ - 1) for y in (YMIN, YMAX)]
MINX = min(c[0] for c in corners); MAXX = max(c[0] for c in corners)
MINY = min(c[1] for c in corners); MAXY = max(c[1] for c in corners)
PAD = 40
W = int(MAXX - MINX) + 2 * PAD
H = int(MAXY - MINY) + 2 * PAD + 46
img = Image.new('RGB', (W, H), (17, 19, 24))
d = ImageDraw.Draw(img)

def screen(ix, iz, y):
    sx, sy = proj(ix, iz, y)
    return sx - MINX + PAD, sy - MINY + PAD + 40

def shade(c, f):
    return tuple(min(255, max(0, int(v * f))) for v in c)

# Painter's order: far rows first == small (a+b).
order = sorted(top.keys(), key=lambda k: ((NX - 1 - k[0]) if flip_x else k[0]) +
                                          ((NZ - 1 - k[1]) if flip_z else k[1]))
SIDE = 3     # how many blocks of side wall to draw under each column top
for (ix, iz) in order:
    bid, y = top[(ix, iz)]
    c = colour(bid)
    # neighbour toward the camera, so a drop shows a wall
    nx_ = ix + (-1 if flip_x else 1)
    nz_ = iz + (-1 if flip_z else 1)
    yn = min(top.get((nx_, iz), (None, y))[1], top.get((ix, nz_), (None, y))[1])
    drop = max(0, min(SIDE + 6, y - yn))
    x0s, y0s = screen(ix, iz, y)
    # top face: a diamond one block across
    p1 = screen(ix, iz, y)
    p2 = screen(ix + 1, iz, y)
    p3 = screen(ix + 1, iz + 1, y)
    p4 = screen(ix, iz + 1, y)
    if drop:
        # left wall (toward -screen-x) and right wall, both from y down to y-drop
        wl = [p1, p4, (p4[0], p4[1] + drop * VY), (p1[0], p1[1] + drop * VY)]
        wr = [p4, p3, (p3[0], p3[1] + drop * VY), (p4[0], p4[1] + drop * VY)]
        d.polygon(wl, fill=shade(c, 0.60))
        d.polygon(wr, fill=shade(c, 0.44))
    f = 1.0 + (y - (YMIN + YMAX) / 2.0) * 0.006
    d.polygon([p1, p2, p3, p4], fill=shade(c, max(0.7, min(1.25, f))))

def font(sz):
    for p in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial.ttf'):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()
F12, F16 = font(13), font(17)

for m in args.mark:
    nm, rest = m.split(':', 1)
    p = [int(v) for v in rest.split(',')]
    mx, my, mz = (p + [0, 0, 0])[:3]
    ix, iz = mx - X0, mz - Z0
    if not (0 <= ix < NX and 0 <= iz < NZ):
        continue
    yy = top.get((ix, iz), (None, my))[1]
    sx, sy = screen(ix, iz, yy)
    d.line([(sx, sy - 26), (sx, sy)], fill=(255, 90, 80), width=2)
    d.ellipse([sx - 5, sy - 32, sx + 5, sy - 22], fill=(255, 120, 90), outline=(20, 20, 20))
    bb = d.textbbox((0, 0), nm, font=F12)
    d.rectangle([sx - (bb[2] - bb[0]) // 2 - 4, sy - 52, sx + (bb[2] - bb[0]) // 2 + 4, sy - 34], fill=(14, 14, 16))
    d.text((sx - (bb[2] - bb[0]) // 2, sy - 50), nm, fill=(255, 200, 180), font=F12)

ttl = args.title or ('oblique from the %s -- centre %d,%d  +-%d blocks  Y %d..%d'
                     % (args.dir.upper(), args.cx, args.cz, args.r, YMIN, YMAX))
d.text((12, 10), ttl, fill=(255, 255, 255), font=F16)
d.text((12, 30), 'looking toward the %s; vertical exaggeration %.1fx; walls drawn where a column '
                 'drops toward the camera' % ({'se': 'north-west', 'sw': 'north-east',
                                               'ne': 'south-west', 'nw': 'south-east'}[args.dir], VY / PX),
       fill=(190, 190, 190), font=F12)
pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
img.save(args.out)
print('wrote %s %s  (%d columns, Y %d..%d)' % (args.out, img.size, len(top), YMIN, YMAX))
