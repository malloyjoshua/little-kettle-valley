#!/usr/bin/env python3
"""Little Kettle Valley title logo.
minecraft.png is a 1024x256 file that Minecraft treats as a 256x64 LOGICAL texture
(4 file px = 1 logical px) and blits the top 256x44 logical region. So artwork lives in
file rows 0-175 and the player sees 256x44. We author on an 8-file-px grid, which makes
each art pixel 2 logical px: a chunky, legible read at title-screen size.
Art canvas: 128 x 22 art px  ->  x8  ->  1024 x 176 file px.
"""
import json, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[2]
PAL = json.loads((ROOT / 'media' / 'palette.json').read_text())['colors']
def C(name, a=255):
    h = PAL[name].lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a)
S = 8            # file px per art px
AW, AH = 128, 22 # art canvas
# ---------------------------------------------------------------- chunky 6x9 font
# Every stroke is 2 art px wide, so nothing goes thin at display size.
F = {
 'L': ["##....","##....","##....","##....","##....","##....","##....","######","######"],
 'I': ["##","##","##","##","##","##","##","##","##"],
 'T': ["######","######","..##..","..##..","..##..","..##..","..##..","..##..","..##.."],
 'E': ["######","######","##....","##....","#####.","#####.","##....","######","######"],
 'K': ["##..##","##..##","##.##.","####..","###...","####..","##.##.","##..##","##..##"],
 'V': ["##..##","##..##","##..##","##..##","##..##",".####.",".####.","..##..","..##.."],
 'A': [".####.",".####.","##..##","##..##","######","######","##..##","##..##","##..##"],
 'Y': ["##..##","##..##","##..##",".####.",".####.","..##..","..##..","..##..","..##.."],
}
GAP, SPACE = 1, 4
def text_mask(s):
    w = 0
    for i, ch in enumerate(s):
        if ch == ' ': w += SPACE
        else: w += len(F[ch][0]) + (GAP if i else 0)
    m = set(); x = 0
    for i, ch in enumerate(s):
        if ch == ' ': x += SPACE; continue
        if i: x += GAP
        g = F[ch]
        for y, row in enumerate(g):
            for dx, c in enumerate(row):
                if c == '#': m.add((x + dx, y))
        x += len(g[0])
    return m, w
# ---------------------------------------------------------------- the kettle mark
# 15 x 10 art px: body, spout left, handle over the top, lid knob, plus steam.
KETTLE = [
 "........CC..........",
 "........CC..........",
 "......LLLLLL........",
 "......CCCCCC........",
 "...CCCCCCCCCCCC.....",
 "CCCCCCCCCCCCCCCCCC..",
 "CCCLLCCCCCCCCCCCCCCC",
 ".CCCCCCCCCCCCCCCCCC.",
 "..DDDDDDDDDDDDDDDD..",
 "....DDDDDDDDDDDD....",
]
STEAM = []
HEART = []
def build():
    art = Image.new('RGBA', (AW, AH), (0,0,0,0)); px = art.load()
    l1, w1 = text_mask('LITTLE KETTLE')
    l2, w2 = text_mask('VALLEY')
    KW = 20
    x1 = (AW - w1) // 2; y1 = 0
    grp = w2 + 3 + KW                      # VALLEY + gap + kettle
    x2 = (AW - grp) // 2; y2 = 12
    kx = x2 + w2 + 3; ky = y2 - 1
    face = set((x + x1, y + y1) for x, y in l1) | set((x + x2, y + y2) for x, y in l2)
    # --- extrusion: 2 art px down-right, copper, behind the face
    ext, ext_deep = set(), set()
    for (x, y) in face:
        p = (x + 1, y + 1)
        if p not in face: ext.add(p)
    for (x, y) in face:
        p = (x + 2, y + 2)
        if p not in face and p not in ext: ext_deep.add(p)
    # --- kettle pixels by colour letter
    kett = {}
    for y, row in enumerate(KETTLE):
        for x, ch in enumerate(row):
            if ch == '.': continue
            kett[(kx + x, ky + y)] = {'#':'ink','k':'kettle_dark','C':'copper','L':'copper_light','D':'copper_dark'}[ch]
    # --- outline: dilate everything solid by 1, in ink
    solid = face | ext | ext_deep | set(kett)
    outline = set()
    for (x, y) in solid:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                p = (x+dx, y+dy)
                if p not in solid: outline.add(p)
    def put(pt, col):
        x, y = pt
        if 0 <= x < AW and 0 <= y < AH: px[x, y] = col
    for p in outline: put(p, C('ink'))
    for p in ext_deep: put(p, C('copper_dark'))
    for p in ext:      put(p, C('copper'))
    for p in face:    put(p, C('cream'))
    # top-row highlight on every letter face for a little dimension
    for (x, y) in sorted(face, key=lambda t: t[1]):
        if (x, y - 1) not in face: put((x, y), C('paper'))
    for p, name in kett.items(): put(p, C(name))
    for p in STEAM: put((kx + p[0], ky + p[1]), C('wool'))
    for p in HEART: put((kx + p[0], ky + p[1]), C('blush'))
    # --- upscale to the file grid
    logo = Image.new('RGBA', (1024, 256), (0,0,0,0))
    logo.paste(art.resize((AW*S, AH*S), Image.NEAREST), (0, 0))
    assert logo.crop((0,176,1024,256)).getbbox() is None, 'rows 176-255 must be transparent'
    logo.save(ROOT / 'media' / 'logo' / 'minecraft.png')
    # ---------------------------------------------------------------- tagline
    # 512x64 file = 128x16 logical, drawn as the top 128x14. 4 file px per art px.
    T = {'p':["###",'#.#',"###","#..","#.."],'u':["...","#.#","#.#","#.#","###"],'t':[".#.","###",".#.",".#.",".##"],
         'h':["#..","#..","###","#.#","#.#"],'e':["...","###","###","#..","###"],'k':["#.#","#.#","##.","#.#","#.#"],
         'l':["#..","#..","#..","#..","###"],'o':["###","#.#","#.#","#.#","###"],'n':["...","##.","#.#","#.#","#.#"],
         ' ':["...","...","...","...","..."]}
    s = 'put the kettle on'; aw = len(s)*4 - 1
    ed = Image.new('RGBA', (128, 16), (0,0,0,0)); ep = ed.load()
    ox = (128 - aw)//2; oy = 4
    for i, ch in enumerate(s):
        g = T[ch]
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == '#':
                    ep[ox + i*4 + x + 1, oy + y + 1] = C('ink')
    for i, ch in enumerate(s):
        g = T[ch]
        for y, row in enumerate(g):
            for x, c in enumerate(row):
                if c == '#': ep[ox + i*4 + x, oy + y] = C('lamp')
    out = Image.new('RGBA', (512, 64), (0,0,0,0))
    out.paste(ed.resize((512, 64), Image.NEAREST), (0, 0))
    out.save(ROOT / 'media' / 'logo' / 'edition.png')
    # ---------------------------------------------------------------- previews
    lg = logo.crop((0,0,1024,176)).resize((256,44), Image.LANCZOS)
    eg = out.crop((0,0,512,56)).resize((128,14), Image.LANCZOS)
    pv = Image.new('RGBA', (256, 70), (46, 62, 82, 255))
    pv.alpha_composite(lg, (0, 4)); pv.alpha_composite(eg, ((256-128)//2, 50))
    pv.resize((256*4, 70*4), Image.NEAREST).convert('RGB').save(ROOT / 'media' / 'logo' / 'preview.png')
    art.resize((AW*6, AH*6), Image.NEAREST).save(ROOT / 'media' / 'logo' / '_art_zoom.png')
    wm = art.crop(art.getbbox()); wm.resize((wm.width*16, wm.height*16), Image.NEAREST).save(ROOT / 'media' / 'logo' / 'wordmark_2048.png')
    print('logo art bbox', art.getbbox(), '| line widths', w1, w2)
build()
