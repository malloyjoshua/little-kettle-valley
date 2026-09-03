#!/usr/bin/env python3
"""Little Kettle Valley title-screen panorama, painted by code.
One 4096x1024 strip wraps the horizon and is sliced into faces 0-3, so the seam is
automatic. The cube's equator (true horizon) is row 512. Faces 4 (up) and 5 (down)
match the strip's top and bottom rows.
"""
import json, math, pathlib, random
from PIL import Image, ImageDraw, ImageFilter
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'media' / 'panorama'
PAL = json.loads((ROOT / 'media' / 'palette.json').read_text())['colors']
def C(n):
    h = PAL[n].lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))
def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i]-a[i])*t)) for i in range(3))
W, H, HZ = 4096, 1024, 512
random.seed(7)
NIGHT, SKY, DUSK, CREAM, WOOL = C('night'), C('sky'), C('dusk'), C('cream'), C('wool')
SAGE, SAGED, INK, LAMP, GLOW = C('sage'), C('sage_dark'), C('ink'), C('lamp'), C('lamp_glow')
COP, COPD, WOOD, WOODD = C('copper'), C('copper_dark'), C('wood'), C('wood_dark')
WATER, BLUSH = C('water'), C('blush')
# ---------------------------------------------------------------- sky
img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
for y in range(H):
    if y <= HZ:
        t = y / HZ                               # 0 top .. 1 horizon
        if t < 0.45: col = mix(NIGHT, SKY, t / 0.45)
        elif t < 0.82: col = mix(SKY, mix(DUSK, SKY, 0.35), (t - 0.45) / 0.37)
        else: col = mix(mix(DUSK, SKY, 0.35), DUSK, (t - 0.82) / 0.18)
    else:
        col = mix(DUSK, mix(WOOL, WATER, 0.25), min(1.0, (y - HZ) / 420))
    d.line([(0, y), (W, y)], fill=col)
# stars: strictly in the upper sky, never near the hills
for _ in range(1100):
    x = random.randrange(W); y = random.randrange(0, 340)
    b = random.random()
    if b < 0.72: d.point((x, y), fill=mix(CREAM, SKY, 0.45))
    elif b < 0.95: d.point((x, y), fill=CREAM)
    else:
        d.point((x, y), fill=CREAM)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)): d.point((x+dx, y+dy), fill=mix(CREAM, SKY, 0.6))
# moon with a soft halo
MX, MY, MR = 2680, 150, 34
halo = Image.new('RGB', (W, H), (0,0,0)); hd = ImageDraw.Draw(halo)
hd.ellipse([MX-MR*4, MY-MR*4, MX+MR*4, MY+MR*4], fill=(70, 78, 86))
img = Image.blend(img, Image.blend(img, halo, 0.0), 0.0)
gl = Image.new('RGBA', (W, H), (0,0,0,0)); gd = ImageDraw.Draw(gl)
for r, a in ((MR*4, 26), (MR*2.6, 34), (MR*1.7, 44)):
    gd.ellipse([MX-r, MY-r, MX+r, MY+r], fill=CREAM + (a,))
gl = gl.filter(ImageFilter.GaussianBlur(26))
img = Image.alpha_composite(img.convert('RGBA'), gl).convert('RGB'); d = ImageDraw.Draw(img)
d.ellipse([MX-MR, MY-MR, MX+MR, MY+MR], fill=CREAM)
d.ellipse([MX-MR+9, MY-MR+7, MX-MR+19, MY-MR+17], fill=mix(CREAM, SKY, 0.18))
d.ellipse([MX-MR+22, MY-MR+30, MX-MR+34, MY-MR+42], fill=mix(CREAM, SKY, 0.14))
# ---------------------------------------------------------------- hills (wrap exactly)
def ridge(base, terms):
    ys = []
    for x in range(W + 1):
        v = base
        for f, a, p in terms: v += a * math.sin(2*math.pi*f*x/W + p)
        ys.append(v)
    return ys
LAYERS = [
    (ridge(452, [(3, 26, 0.4), (7, 13, 1.9), (13, 7, 3.1), (21, 4, 0.7)]), mix(SAGE, DUSK, 0.52)),
    (ridge(482, [(2, 34, 2.2), (5, 18, 0.3), (11, 9, 2.6), (17, 5, 1.2)]), mix(SAGE, DUSK, 0.30)),
    (ridge(516, [(4, 30, 1.1), (6, 16, 2.9), (9, 11, 0.6), (19, 6, 2.0)]), SAGE),
    (ridge(556, [(3, 34, 3.0), (5, 20, 1.4), (8, 12, 2.2), (15, 7, 0.9)]), mix(SAGED, INK, 0.22)),
]
for ys, col in LAYERS:
    pts = [(x, ys[x]) for x in range(W + 1)] + [(W, H), (0, H)]
    d.polygon(pts, fill=col)
NEAR = LAYERS[3][0]
# pines along the near ridge
def pine(x, base, h, col, trunk=True):
    w = max(6, int(h * 0.42))
    for i in range(3):
        yt = base - h + i * h * 0.27; yb = base - h * 0.34 + i * h * 0.27
        ww = w * (0.55 + 0.22 * i)
        d.polygon([(x, yt), (x - ww, yb), (x + ww, yb)], fill=col)
    if trunk: d.rectangle([x - 2, base - h * 0.12, x + 2, base + 3], fill=mix(WOODD, INK, 0.4))
for x in range(40, W, 63):
    xx = x + random.randint(-16, 16)
    pine(xx, NEAR[xx % W] + 6, random.randint(34, 62), mix(SAGED, INK, 0.42))
# ---------------------------------------------------------------- frozen lake
LX0, LX1 = 3180, 3980
lake = Image.new('RGBA', (W, H), (0,0,0,0)); ld = ImageDraw.Draw(lake)
ld.ellipse([LX0, 546, LX1, 690], fill=mix(WATER, CREAM, 0.42) + (255,))
ld.ellipse([LX0+40, 556, LX1-40, 664], fill=mix(WATER, DUSK, 0.34) + (255,))
for i in range(9):
    x0 = random.randint(LX0+70, LX1-160); y0 = random.randint(572, 650)
    ld.line([(x0, y0), (x0 + random.randint(40, 130), y0 + random.randint(-8, 8))], fill=mix(CREAM, WATER, 0.5) + (200,), width=2)
img = Image.alpha_composite(img.convert('RGBA'), lake).convert('RGB'); d = ImageDraw.Draw(img)
d.ellipse([MX-16, 596, MX+16, 616], fill=mix(CREAM, WATER, 0.55)) if LX0 < MX < LX1 else None
# ---------------------------------------------------------------- the town
def window(x, y, w=7, h=9):
    d.rectangle([x, y, x+w, y+h], fill=LAMP)
    d.rectangle([x+1, y+1, x+w-1, y+h-1], fill=GLOW)
def house(x, base, w, h, roof=None, lit=2):
    roof = roof or mix(WOODD, INK, 0.3)
    d.rectangle([x, base-h, x+w, base], fill=mix(CREAM, WOOD, 0.42))
    d.rectangle([x, base-h, x+w, base], outline=mix(WOODD, INK, 0.45), width=2)
    d.polygon([(x-9, base-h), (x+w+9, base-h), (x+w/2, base-h-h*0.62)], fill=roof)
    for i in range(lit):
        window(x + 9 + i * (w - 14) / max(1, lit), base - h + 12)
    cx = x + w * 0.74
    d.rectangle([cx, base-h-h*0.42, cx+9, base-h-h*0.16], fill=mix(WOODD, INK, 0.2))
    for k in range(5):
        r = 4 + k * 2.6; yy = base-h-h*0.42 - 8 - k*13; xx = cx + 4 + math.sin(k*0.9)*7
        d.ellipse([xx-r, yy-r, xx+r, yy+r], fill=mix(WOOL, SKY, 0.25 + k*0.12))
TOWN = 1180
plots = [(0, 92, 74, 2), (104, 70, 58, 2), (186, 110, 86, 3), (300, 78, 62, 2), (378, 96, 78, 2), (476, 66, 54, 1)]
for off, w, h, lit in plots:
    x = TOWN + off; house(x, NEAR[int(x + w/2) % W] + 8, w, h, lit=lit)
# bell tower with a copper roof
tx = TOWN + 232; tb = NEAR[tx % W] + 8
d.rectangle([tx, tb-186, tx+52, tb], fill=mix(CREAM, WOOD, 0.3))
d.rectangle([tx, tb-186, tx+52, tb], outline=mix(WOODD, INK, 0.45), width=2)
d.polygon([(tx-14, tb-186), (tx+66, tb-186), (tx+26, tb-252)], fill=COP)
d.polygon([(tx+26, tb-252), (tx+66, tb-186), (tx+26, tb-186)], fill=COPD)
window(tx+18, tb-168, 16, 22)
d.ellipse([tx+20, tb-96, tx+32, tb-84], fill=LAMP)
# ---------------------------------------------------------------- the road + lamp posts
road = Image.new('RGBA', (W, H), (0,0,0,0)); rd = ImageDraw.Draw(road)
RX = TOWN + 250
pts = []
for i in range(101):
    t = i / 100
    y = NEAR[int(RX) % W] + 10 + t * (H - NEAR[int(RX) % W] - 10)
    x = RX + math.sin(t * 1.9) * 300 * t + t * t * 120
    wdt = 7 + t * t * 150
    pts.append((x, y, wdt))
for (x, y, wdt) in pts:
    rd.ellipse([x-wdt, y-wdt*0.22, x+wdt, y+wdt*0.22], fill=mix(WOOL, WOOD, 0.30) + (255,))
for (x, y, wdt) in pts[::7]:
    rd.ellipse([x-wdt*0.86, y-wdt*0.17, x+wdt*0.86, y+wdt*0.17], fill=mix(WOOL, DUSK, 0.16) + (255,))
img = Image.alpha_composite(img.convert('RGBA'), road).convert('RGB'); d = ImageDraw.Draw(img)
glowl = Image.new('RGBA', (W, H), (0,0,0,0)); gd = ImageDraw.Draw(glowl)
posts = []
for i in range(6, 101, 15):
    x, y, wdt = pts[i]; side = -1 if (i // 15) % 2 == 0 else 1
    px = x + side * (wdt + 16); ph = 44 + (i / 100) * 150
    posts.append((px, y, ph))
    gd.ellipse([px-ph*0.9, y-ph*1.5, px+ph*0.9, y+ph*0.25], fill=GLOW + (40,))
glowl = glowl.filter(ImageFilter.GaussianBlur(28))
img = Image.alpha_composite(img.convert('RGBA'), glowl).convert('RGB'); d = ImageDraw.Draw(img)
for (px, y, ph) in posts:
    d.rectangle([px-3, y-ph, px+3, y], fill=mix(INK, WOODD, 0.3))
    d.rectangle([px-11, y-ph-16, px+11, y-ph], fill=mix(INK, COPD, 0.35))
    d.rectangle([px-8, y-ph-13, px+8, y-ph-3], fill=LAMP)
    d.rectangle([px-6, y-ph-11, px+6, y-ph-5], fill=GLOW)
    d.polygon([(px-14, y-ph-16), (px+14, y-ph-16), (px, y-ph-30)], fill=COP)
# ---------------------------------------------------------------- foreground
# a fence that wraps the whole strip, sitting low so it frames without blocking
for x in range(0, W, 34):
    fy = H - 96 + int(math.sin(x / 260) * 12)
    d.rectangle([x, fy, x+7, fy+70], fill=mix(WOODD, INK, 0.25))
for x in range(0, W, 4):
    fy = H - 96 + int(math.sin(x / 260) * 12)
    d.rectangle([x, fy+16, x+4, fy+24], fill=mix(WOOD, INK, 0.3))
    d.rectangle([x, fy+40, x+4, fy+48], fill=mix(WOOD, INK, 0.34))
# two close pines framing one face, and a mailbox by the road
for (fx, fh) in ((520, 300), (600, 226), (2210, 268)):
    pine(fx, H - 40, fh, mix(SAGED, INK, 0.62))
mb = pts[-22]
d.rectangle([mb[0]-70, mb[1]-96, mb[0]-62, mb[1]-10], fill=mix(WOODD, INK, 0.3))
d.rounded_rectangle([mb[0]-94, mb[1]-126, mb[0]-42, mb[1]-94], 9, fill=COP, outline=COPD, width=2)
# snow speckle on the near ground
for _ in range(2600):
    x = random.randrange(W); y = random.randrange(HZ + 60, H)
    d.point((x, y), fill=mix(WOOL, CREAM, random.random()))
# ---------------------------------------------------------------- slice + caps
img.save(OUT / '_strip.png')
for i in range(4):
    img.crop((i*1024, 0, (i+1)*1024, 1024)).save(OUT / f'panorama_{i}.png')
top_col = img.getpixel((0, 0)); bot_col = img.getpixel((0, H-1))
up = Image.new('RGB', (1024, 1024), top_col); ud = ImageDraw.Draw(up)
for _ in range(700):
    x, y = random.randrange(1024), random.randrange(1024)
    dist = math.hypot(x-512, y-512) / 724
    if random.random() > dist * 0.7: ud.point((x, y), fill=mix(top_col, CREAM, random.uniform(0.35, 1.0)))
up.save(OUT / 'panorama_4.png')
dn = Image.new('RGB', (1024, 1024), bot_col); dd = ImageDraw.Draw(dn)
for _ in range(2200):
    x, y = random.randrange(1024), random.randrange(1024)
    dd.point((x, y), fill=mix(bot_col, CREAM, random.uniform(0.2, 0.9)))
dn.save(OUT / 'panorama_5.png')
# previews
img.resize((1400, 350), Image.LANCZOS).save(OUT / '_preview_strip.png')
f3 = Image.open(OUT / 'panorama_3.png'); f0 = Image.open(OUT / 'panorama_0.png')
seam = Image.new('RGB', (160, 1024)); seam.paste(f3.crop((944, 0, 1024, 1024)), (0, 0)); seam.paste(f0.crop((0, 0, 80, 1024)), (80, 0))
seam.resize((480, 1024)).save(OUT / 'seam_check.png')
print('panorama built. horizon row', HZ)
