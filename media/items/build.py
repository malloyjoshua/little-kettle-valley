#!/usr/bin/env python3
"""Builds media/items/batch1.json — 16x16 item icons for Little Kettle Valley.
Run: tools/venv/bin/python media/items/build.py
Then: tools/venv/bin/python tools/scripts/pixel.py render media/items/batch1.json media/items/png
"""
import json, pathlib, math

def G():
    return [['.' for _ in range(16)] for _ in range(16)]

def st(g, x, y, ch):
    if 0 <= x < 16 and 0 <= y < 16:
        g[y][x] = ch

def rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            st(g, x, y, ch)

def frame(g, x0, y0, x1, y1, ch):
    for x in range(x0, x1 + 1):
        st(g, x, y0, ch); st(g, x, y1, ch)
    for y in range(y0, y1 + 1):
        st(g, x0, y, ch); st(g, x1, y, ch)

def hline(g, x0, x1, y, ch):
    for x in range(x0, x1 + 1):
        st(g, x, y, ch)

def vline(g, x0, y0, y1, ch):
    for y in range(y0, y1 + 1):
        st(g, x0, y, ch)

def disc(g, cx, cy, r, ch, r0=0.0):
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r0 <= d <= r:
                st(g, x, y, ch)

def px(g, pts, ch):
    for (x, y) in pts:
        st(g, x, y, ch)

def rows(g):
    return [''.join(r) for r in g]

icons = []
def add(name, g):
    icons.append({"name": name, "rows": rows(g)})

# ---------------------------------------------------------------- scrip
g = G()
disc(g, 8, 8, 6.3, 'D')
disc(g, 8, 8, 5.6, 'C')
disc(g, 8, 8, 5.6, 'L', r0=4.6)
for (x, y) in [(4,4),(5,4),(4,5),(5,3),(6,3)]:
    st(g, x, y, 'Y')
# tiny kettle glyph
px(g, [(6,9),(7,9),(8,9),(9,9),(7,8),(8,8),(6,10),(7,10),(8,10),(9,10),(5,9),(9,8)], 'k')
st(g, 5, 9, 'k'); st(g, 10, 9, 'D')
add('scrip', g)

# ---------------------------------------------------------------- letter
g = G()
rect(g, 3, 4, 12, 12, 'p')
frame(g, 3, 4, 12, 12, 'i')
# dog-ear fold
px(g, [(10,4),(11,4),(12,4),(11,5),(12,5),(12,6)], 'c')
px(g, [(10,4),(12,6)], 'O')
hline(g, 3, 12, 4, 'i')
# fold shadow line
for i in range(9):
    st(g, 3+i, 8, 'c') if False else None
vline(g, 7, 5, 12, 'O')
vline(g, 8, 5, 12, 'c')
# wax seal
disc(g, 7, 12, 2.4, 'D')
disc(g, 7, 12, 1.9, 'r')
st(g, 6, 11, 'h')
add('letter', g)

# ---------------------------------------------------------------- deed
g = G()
rect(g, 2, 5, 13, 10, 'p')
frame(g, 2, 5, 13, 10, 'O')
vline(g, 2, 4, 11, 'u'); vline(g, 3, 5, 10, 'c')
vline(g, 13, 4, 11, 'u'); vline(g, 12, 5, 10, 'c')
for x in range(4, 12):
    if x % 3 == 0: st(g, x, 7, 'O')
hline(g, 4, 11, 7, 'D')
hline(g, 4, 9, 9, 'D')
# ribbon bow
px(g, [(6,11),(7,11),(8,11),(9,11)], 'r')
px(g, [(7,12),(8,12)], 'D')
px(g, [(6,10),(9,10)], 'G')
add('deed', g)

# ---------------------------------------------------------------- deed_works
g = G()
rect(g, 2, 5, 13, 10, 'p')
frame(g, 2, 5, 13, 10, 'O')
vline(g, 2, 4, 11, 'u'); vline(g, 3, 5, 10, 'c')
vline(g, 13, 4, 11, 'u'); vline(g, 12, 5, 10, 'c')
hline(g, 4, 11, 7, 'D')
hline(g, 4, 9, 9, 'D')
# gear seal
disc(g, 8, 11, 2.4, 'T')
disc(g, 8, 11, 1.3, 't')
for (x, y) in [(6,11),(10,11),(8,9),(8,13),(6.5,9.5),(9.5,9.5),(6.5,12.5),(9.5,12.5)]:
    st(g, round(x), round(y), 'T')
st(g, 8, 11, 'i')
add('deed_works', g)

# ---------------------------------------------------------------- kettle_deed
g = G()
rect(g, 2, 5, 13, 10, 'u')
rect(g, 3, 6, 12, 9, 'p')
frame(g, 2, 5, 13, 10, 'O')
vline(g, 2, 4, 11, 'O'); vline(g, 13, 4, 11, 'O')
hline(g, 4, 11, 7, 'D')
hline(g, 4, 9, 8, 'D')
# copper seal
disc(g, 8, 11, 2.6, 'D')
disc(g, 8, 11, 1.7, 'C')
st(g, 7, 10, 'L')
add('kettle_deed', g)

# ---------------------------------------------------------------- bounty_receipt
g = G()
rect(g, 4, 3, 11, 12, 'W')
frame(g, 4, 3, 11, 12, 'i')
for y in range(3, 13):
    if y % 2 == 0:
        st(g, 3, y, 'W'); st(g, 12, y, 'W')
hline(g, 5, 10, 6, 'r')
hline(g, 5, 8, 8, 'T')
hline(g, 5, 9, 10, 'T')
for x in range(5, 11):
    if x % 2 == 0: st(g, x, 4, 'T')
add('bounty_receipt', g)

# ---------------------------------------------------------------- catalogue
g = G()
rect(g, 4, 2, 11, 13, 's')
frame(g, 4, 2, 11, 13, 'S')
vline(g, 4, 2, 13, 'S')
rect(g, 9, 3, 10, 12, 'c')
hline(g, 5, 8, 5, 'S')
hline(g, 5, 8, 7, 'S')
hline(g, 5, 8, 9, 'S')
add('catalogue', g)

# ---------------------------------------------------------------- odas_ledger
g = G()
rect(g, 3, 2, 12, 13, 'O')
frame(g, 3, 2, 12, 13, 'i')
rect(g, 10, 3, 11, 12, 'c')
for y in range(3, 13):
    if y % 2 == 0: st(g, 11, y, 'p')
vline(g, 4, 2, 13, 'D')
# gold clasp
rect(g, 6, 7, 9, 8, 'G')
st(g, 7, 7, 'Y')
add('odas_ledger', g)

# ---------------------------------------------------------------- turbine_notes
g = G()
rect(g, 3, 3, 12, 13, 'b')
frame(g, 3, 3, 12, 13, 'n')
for x in range(4, 12, 2):
    st(g, x, 3, 'T'); st(g, x, 2, 'T')
# gear emblem
disc(g, 8, 9, 3.1, 'V')
disc(g, 8, 9, 1.6, 'e')
for (x, y) in [(5,9),(11,9),(8,6),(8,12),(6,7),(10,7),(6,11),(10,11)]:
    st(g, x, y, 'V')
add('turbine_notes', g)

# ---------------------------------------------------------------- deep_survey
g = G()
# rolled scroll cylinder
rect(g, 3, 6, 12, 10, 'p')
disc(g, 3, 8, 2.3, 'O'); disc(g, 3, 8, 1.5, 'o')
disc(g, 12, 8, 2.3, 'O'); disc(g, 12, 8, 1.5, 'o')
hline(g, 5, 10, 7, 'D')
hline(g, 5, 9, 9, 'D')
vline(g, 7, 6, 10, 'T')
# pick tag
px(g, [(9,3),(10,4),(11,5)], 'T')
px(g, [(11,4),(10,3)], 'O')
st(g, 9, 5, 'i')
add('deep_survey', g)

# ---------------------------------------------------------------- framed_town_map
g = G()
rect(g, 1, 1, 14, 14, 'O')
frame(g, 1, 1, 14, 14, 'i')
rect(g, 3, 3, 12, 12, 'p')
frame(g, 3, 3, 12, 12, 'D')
# roads
hline(g, 4, 11, 8, 'i')
vline(g, 8, 4, 11, 'i')
px(g, [(5,5),(10,5),(5,10),(10,10)], 'r')
px(g, [(3,3),(12,3),(3,12),(12,12)], 'G')
add('framed_town_map', g)

# ---------------------------------------------------------------- place_setting
g = G()
disc(g, 8, 10, 4.6, 'T')
disc(g, 8, 10, 3.9, 'W')
disc(g, 8, 10, 2.6, 'V', r0=2.2)
# fork left
vline(g, 3, 3, 12, 'V')
px(g, [(2,3),(4,3)], 'V')
px(g, [(2,2),(4,2),(3,2)], 'V')
# cup right
rect(g, 11, 5, 13, 8, 'W')
frame(g, 11, 5, 13, 8, 'T')
st(g, 14, 6, 'V')
st(g, 12, 6, 'u')
add('place_setting', g)

# ---------------------------------------------------------------- green_oak_plank
g = G()
rect(g, 1, 3, 14, 12, 'o')
rect(g, 1, 3, 14, 12, 's')
for y in range(3, 13):
    for x in range(1, 15):
        pass
rect(g, 1, 3, 14, 12, 'o')
for x in range(1, 15):
    if (x) % 4 in (0,):
        vline(g, x, 3, 12, 'O')
for y in (3, 7, 12):
    hline(g, 1, 14, y, 'S' if y != 12 else 'O')
frame(g, 1, 3, 14, 12, 'S')
add('green_oak_plank', g)

# ---------------------------------------------------------------- seasoned_oak_board
g = G()
rect(g, 1, 3, 14, 12, 'O')
for x in range(1, 15):
    if x % 5 == 0:
        vline(g, x, 3, 12, 'D')
hline(g, 1, 14, 3, 'D'); hline(g, 1, 14, 12, 'i')
for x in (3, 8, 11):
    st(g, x, 7, 'D')
frame(g, 1, 3, 14, 12, 'i')
add('seasoned_oak_board', g)

# ---------------------------------------------------------------- lake_sand
g = G()
for y, (x0, x1) in [(11,(2,13)),(10,(2,13)),(9,(3,12)),(8,(4,11)),(7,(5,10)),(6,(6,9))]:
    hline(g, x0, x1, y, 'p')
hline(g, 2, 13, 12, 'D')
for (x, y) in [(4,10),(8,9),(6,8),(10,10),(7,7),(5,11),(9,11)]:
    st(g, x, y, 'c')
for (x, y) in [(3,11),(11,11),(6,10)]:
    st(g, x, y, 'O')
add('lake_sand', g)

# ---------------------------------------------------------------- washed_silica
g = G()
for y, (x0, x1) in [(11,(2,13)),(10,(2,13)),(9,(3,12)),(8,(4,11)),(7,(5,10))]:
    hline(g, x0, x1, y, 'V')
hline(g, 2, 13, 12, 'T')
for (x, y) in [(4,10),(8,9),(11,10),(6,8),(9,11),(5,11)]:
    st(g, x, y, 'w')
for (x, y) in [(7,8),(10,9),(3,11)]:
    st(g, x, y, 'a')
add('washed_silica', g)

# ---------------------------------------------------------------- spring_water
g = G()
vline(g, 7, 2, 4, 'V'); vline(g, 8, 2, 4, 'V')
st(g, 7, 1, 'O')
disc(g, 8, 10, 4.6, 'a')
disc(g, 8, 10, 4.6, 'V', r0=4.0)
rect(g, 5, 5, 10, 9, 'A')
rect(g, 5, 5, 10, 6, (0,0,0,0) and 'A' or 'A')
for x in range(5, 11):
    st(g, x, 5, 'A')
disc(g, 8, 10, 3.7, 'a')
px(g, [(6,8),(7,9)], 'w')
px(g, [(10,6),(9,7)], 'w')
add('spring_water', g)

# ---------------------------------------------------------------- works_power_tap
g = G()
rect(g, 1, 1, 14, 14, 'C')
for x in range(1, 15):
    if x % 4 == 0: vline(g, x, 1, 14, 'D')
for y in range(1, 15):
    if y % 4 == 0: hline(g, 1, 14, y, 'D')
frame(g, 1, 1, 14, 14, 'D')
disc(g, 8, 8, 4.2, 'i')
disc(g, 8, 8, 3.4, 'r')
st(g, 8, 5, 'W'); st(g, 8, 8, 'i')
for (x,y) in [(2,2),(13,2),(2,13),(13,13)]:
    st(g, x, y, 'T')
add('works_power_tap', g)

FONT3x5 = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'B': ['##.', '#.#', '##.', '#.#', '##.'],
}
def nameplate(letter_ch):
    g = G()
    rect(g, 2, 4, 13, 11, 'C')
    frame(g, 2, 4, 13, 11, 'D')
    for (x,y) in [(3,5),(12,5),(3,10),(12,10)]:
        st(g, x, y, 'T')
    glyph = FONT3x5[letter_ch]
    x0, y0 = 6, 5
    for gy, r in enumerate(glyph):
        for gx, c in enumerate(r):
            if c == '#':
                st(g, x0 + gx, y0 + gy, 'k')
    return g

add('kettle_plate_a', nameplate('A'))
add('kettle_plate_b', nameplate('B'))

# ---------------------------------------------------------------- ice_auger
g = G()
hline(g, 3, 12, 3, 'o')
hline(g, 3, 12, 4, 'O')
vline(g, 7, 4, 6, 'T')
vline(g, 8, 4, 6, 'T')
for y in range(6, 13):
    off = (y - 6) % 2
    st(g, 7 + off, y, 'V')
    st(g, 8 - off, y, 't')
px(g, [(7,13),(8,14)], 'i')
add('ice_auger', g)

# ---------------------------------------------------------------- dredge_net
g = G()
vline(g, 10, 5, 13, 'O')
px(g, [(11,13),(12,14)], 'O')
disc(g, 7, 6, 4.4, 'O')
disc(g, 7, 6, 3.6, (0,0,0,0) and '.' or '.')
frame(g, 3, 2, 11, 10, '.')
disc(g, 7, 6, 4.4, 'O')
disc(g, 7, 6, 3.5, '.')
disc(g, 7, 6, 4.4, 'O', r0=3.6)
for (x,y) in [(5,4),(9,4),(5,8),(9,8),(7,3),(7,9),(4,6),(10,6)]:
    st(g, x, y, 'p')
for (x,y) in [(5,4),(7,6),(9,8)]:
    st(g, x, y, 'p')
add('dredge_net', g)

# ---------------------------------------------------------------- oda_broom
g = G()
vline(g, 8, 2, 9, 'o')
vline(g, 9, 2, 9, 'O')
hline(g, 6, 11, 10, 'D')
for x in range(5, 12):
    vline(g, x, 11, 14, 'G' if x % 2 == 0 else 'y')
hline(g, 5, 11, 14, 'O')
add('oda_broom', g)

# ---------------------------------------------------------------- copper_kettle_trophy
g = G()
# body (rounded, outline + fill + upper-left highlight)
for y in range(16):
    for x in range(16):
        dx, dy = x + 0.5 - 8, y + 0.5 - 10.2
        d = math.hypot(dx, dy * 1.05)
        if d <= 5.0:
            ch = 'D' if d > 4.15 else ('L' if (dx < -0.6 and dy < -0.6 and d > 1.8) else 'C')
            st(g, x, y, ch)
# clip body to sit above the base band
rect(g, 0, 14, 15, 15, '.')
hline(g, 3, 12, 13, 'D')
rect(g, 4, 14, 11, 14, 'D')
# lid
rect(g, 5, 4, 10, 5, 'D')
rect(g, 6, 5, 9, 5, 'L')
st(g, 7, 3, 'D'); st(g, 8, 3, 'D'); st(g, 7, 2, 'D')
st(g, 8, 2, 'L')
# handle (open loop on the left)
px(g, [(2,7),(3,6),(4,6)], 'D')
px(g, [(1,8),(1,9)], 'D')
px(g, [(2,11),(3,12),(4,12)], 'D')
# spout (right side, with a visible opening at the tip)
px(g, [(12,7),(13,7),(13,6)], 'C')
px(g, [(12,6),(14,6),(14,7)], 'D')
px(g, [(13,8),(12,8)], 'D')
st(g, 13, 7, 'w')
# sparkle, kept clear of the silhouette
px(g, [(2,2),(13,3)], 'Y')
st(g, 3, 3, 'Y')
add('copper_kettle_trophy', g)

def crate(extra=None):
    g = G()
    rect(g, 2, 5, 13, 13, 'o')
    frame(g, 2, 5, 13, 13, 'O')
    vline(g, 2, 5, 13, 'O'); vline(g, 13, 5, 13, 'O')
    hline(g, 2, 13, 9, 'O')
    for x in (2,13):
        st(g, x, 5, 'D'); st(g, x, 13, 'D')
    rect(g, 4, 10, 11, 12, 'p')
    frame(g, 4, 10, 11, 12, 'D')
    return g

g = crate()
add('delivery_crate', g)

# ---------------------------------------------------------------- courier_parcel
g = G()
rect(g, 3, 4, 12, 12, 'W')
frame(g, 3, 4, 12, 12, 'T')
vline(g, 7, 4, 12, 'O')
vline(g, 8, 4, 12, 'O')
hline(g, 3, 12, 7, 'O')
hline(g, 3, 12, 8, 'O')
rect(g, 6, 6, 9, 10, 'W')
disc(g, 7, 4, 1.4, 'D')
add('courier_parcel', g)

# ---------------------------------------------------------------- feast_crate
g = crate()
# bread loaf peeking (rounded dome, scored top)
for y, (x0, x1) in [(4,(5,7)),(3,(5,7)),(5,(4,8))]:
    hline(g, x0, x1, y, 'o')
px(g, [(5,3),(7,3),(5,4),(7,4)], 'O')
hline(g, 4, 8, 6, 'D')
# apple peeking
disc(g, 11, 5, 2.1, 'r')
st(g, 11, 3, 'g')
st(g, 10, 4, 'h')
add('feast_crate', g)

# ---------------------------------------------------------------- hen_crate
g = crate()
disc(g, 8, 5, 3.1, 'W')
disc(g, 8, 5, 3.1, 'p', r0=2.6)
px(g, [(7,1),(8,1),(9,2),(7,2)], 'r')
px(g, [(11,5),(11,6),(12,5)], 'y')
st(g, 6, 5, 'i')
add('hen_crate', g)

# ---------------------------------------------------------------- cow_crate
g = crate()
disc(g, 8, 5, 3.4, 'W')
px(g, [(5,2),(5,3),(11,2),(11,3)], 'W')
px(g, [(4,2),(12,2)], 'T')
px(g, [(6,3),(7,3)], 'i')
px(g, [(10,6),(10,7)], 'i')
st(g, 6, 5, 'i'); st(g, 10, 5, 'i')
rect(g, 6, 7, 10, 8, 'h')
st(g, 7, 8, 'i'); st(g, 9, 8, 'i')
add('cow_crate', g)

# ---------------------------------------------------------------- sheep_crate
g = crate()
disc(g, 8, 5, 3.6, 'W')
px(g, [(8,1),(4,4),(12,4),(5,2),(11,2),(6,8),(10,8),(3,6),(13,6)], 'W')
rect(g, 6, 5, 10, 7, 't')
st(g, 7, 6, 'i'); st(g, 9, 6, 'i')
add('sheep_crate', g)

# ---------------------------------------------------------------- chicken_feed
g = G()
px(g, [(6,4),(7,3),(9,3),(10,4)], 'O')
rect(g, 5, 5, 11, 12, 'o')
frame(g, 5, 5, 11, 12, 'O')
hline(g, 5, 11, 12, 'D')
px(g, [(7,7),(8,6),(9,7),(8,8)], 'y')
px(g, [(7,9),(9,9),(8,10)], 'G')
add('chicken_feed', g)

# ---------------------------------------------------------------- firewood_bundle
g = G()
for y0 in (2, 6, 10):
    rect(g, 3, y0, 12, y0 + 2, 'o')
    frame(g, 3, y0, 12, y0 + 2, 'O')
    # end-grain caps
    vline(g, 3, y0, y0 + 2, 'D'); st(g, 4, y0 + 1, 'c')
    vline(g, 12, y0, y0 + 2, 'D'); st(g, 11, y0 + 1, 'c')
# rope straps crossing the stack
for x in (6, 10):
    vline(g, x, 1, 13, 'i')
    st(g, x - 1, 1, 'T'); st(g, x + 1, 13, 'T')
add('firewood_bundle', g)

# ---------------------------------------------------------------- blanket
g = G()
rect(g, 2, 6, 13, 12, 'W')
frame(g, 2, 6, 13, 12, 'T')
for y in (7, 9, 11):
    hline(g, 2, 13, y, 's')
hline(g, 2, 13, 6, 'c')
add('blanket', g)

# ---------------------------------------------------------------- winter_cloak
g = G()
disc(g, 8, 4, 3.0, 'S')
rect(g, 4, 6, 11, 14, 'S')
for y in range(6, 15):
    w = max(0, (y - 6))
    pass
# taper cloak shape
for y, (x0, x1) in [(6,(6,9)),(7,(5,10)),(8,(5,10)),(9,(4,11)),(10,(4,11)),(11,(3,12)),(12,(3,12)),(13,(3,12)),(14,(3,12))]:
    hline(g, x0, x1, y, 's')
frame(g, 3, 6, 12, 14, 'S')
disc(g, 8, 5, 2.4, 'n')
disc(g, 8, 5, 1.6, 's')
st(g, 8, 8, 'C')
add('winter_cloak', g)

# ---------------------------------------------------------------- winter_tonic
g = G()
vline(g, 7, 1, 3, 'O')
vline(g, 8, 1, 3, 'o')
rect(g, 6, 4, 9, 6, 'V')
for y, (x0, x1) in [(7,(5,10)),(8,(4,11)),(9,(4,11)),(10,(4,11)),(11,(4,11)),(12,(4,11)),(13,(4,11))]:
    hline(g, x0, x1, y, 'u')
frame(g, 4, 7, 11, 13, 'D')
hline(g, 4, 11, 8, 'w')
st(g, 6, 9, 'Y')
add('winter_tonic', g)

# ---------------------------------------------------------------- winter_tomato
g = G()
disc(g, 8, 9, 5.4, 'D')
disc(g, 8, 9, 4.7, 'r')
disc(g, 8, 9, 4.7, 'u', r0=3.6)
px(g, [(6,4),(8,3),(10,4),(7,5),(9,5)], 'g')
st(g, 8, 5, 'S')
px(g, [(5,7),(6,6)], 'u')
add('winter_tomato', g)

# ---------------------------------------------------------------- paper_lantern
g = G()
rect(g, 6, 2, 9, 3, 'O')
disc(g, 8, 9, 5.4, 'T')
disc(g, 8, 9, 4.7, 'W')
disc(g, 8, 9, 3.0, 'Y')
for x in (6, 8, 10):
    vline(g, x, 5, 13, 'c')
rect(g, 6, 13, 9, 14, 'O')
st(g, 8, 1, 'O')
add('paper_lantern', g)

# ---------------------------------------------------------------- josies_lantern
g = G()
px(g, [(6,2),(7,1),(8,1),(9,2)], 'D')
rect(g, 5, 3, 10, 4, 'D')
rect(g, 5, 5, 10, 12, 'C')
rect(g, 6, 6, 9, 11, 'y')
rect(g, 6, 6, 9, 8, 'Y')
vline(g, 5, 5, 12, 'D'); vline(g, 10, 5, 12, 'D')
hline(g, 5, 10, 8, 'D')
rect(g, 4, 12, 11, 13, 'D')
rect(g, 5, 13, 10, 14, 'C')
add('josies_lantern', g)

# ---------------------------------------------------------------- hearthkeepers_lantern
g = G()
st(g, 8, 1, 'G')
px(g, [(6,2),(7,1),(8,0) if False else (8,1),(9,2)], 'G')
rect(g, 5, 3, 10, 4, 'G')
rect(g, 5, 5, 10, 12, 'D')
rect(g, 6, 6, 9, 11, 'Y')
rect(g, 6, 6, 9, 8, 'w')
vline(g, 5, 5, 12, 'G'); vline(g, 10, 5, 12, 'G')
hline(g, 5, 8, 8, 'G')
rect(g, 4, 12, 11, 13, 'G')
rect(g, 5, 13, 10, 14, 'D')
px(g, [(3,4),(12,4),(2,8),(13,8)], 'Y')
add('hearthkeepers_lantern', g)

# ---------------------------------------------------------------- plushie_token
g = G()
vline(g, 8, 1, 3, 'O')
disc(g, 8, 9, 5.5, 'D')
disc(g, 8, 9, 4.7, 'C')
disc(g, 8, 9, 4.7, 'L', r0=3.6)
st(g, 5, 6, 'C'); st(g, 4, 5, 'D')
px(g, [(11,8),(12,7),(13,7)], 'C')
disc(g, 7, 8, 0.8, 'i'); disc(g, 10, 8, 0.8, 'i')
hline(g, 7, 9, 11, 'i')
add('plushie_token', g)

# ---------------------------------------------------------------- tokens
def token(fill, ring, glyph_fn):
    g = G()
    disc(g, 8, 8, 5.6, ring)
    disc(g, 8, 8, 4.7, fill)
    disc(g, 8, 8, 4.7, 'w', r0=4.1)
    glyph_fn(g)
    return g

def gl_bread(g):
    for y, (x0, x1) in [(9,(6,10)),(8,(6,10)),(7,(6,10)),(6,(7,9))]:
        hline(g, x0, x1, y, 'O')
    st(g, 8, 8, 'i')

def gl_gear(g):
    disc(g, 8, 8, 2.6, 'i')
    disc(g, 8, 8, 1.4, 't')
    for (x,y) in [(6,8),(10,8),(8,6),(8,10)]:
        st(g, x, y, 'i')

def gl_coin(g):
    disc(g, 8, 8, 2.6, 'D')
    disc(g, 8, 8, 1.7, 'G')

def gl_fish(g):
    px(g, [(6,8),(7,7),(8,7),(9,7),(10,8),(9,9),(8,9),(7,9)], 'i')
    px(g, [(5,7),(5,9)], 'i')
    st(g, 8, 8, 'w')

def gl_leaf(g):
    for (x, y) in [(8,5),(7,6),(8,6),(9,6),(6,7),(7,7),(8,7),(9,7),(10,7),
                   (7,8),(8,8),(9,8),(8,9),(8,10)]:
        st(g, x, y, 'i')
    vline(g, 8, 6, 10, 'S')

def gl_pick(g):
    px(g, [(5,10),(6,9),(7,8),(8,7),(9,6),(10,5)], 'i')
    px(g, [(6,6),(7,7),(9,5),(10,6)], 'i')

def gl_lily(g):
    disc(g, 8, 8, 2.7, 'S')
    px(g, [(8,8),(10,7),(11,6)], 'w')

def gl_egg(g):
    for y, (x0,x1) in [(6,(7,9)),(7,(6,10)),(8,(6,10)),(9,(6,10)),(10,(7,9))]:
        hline(g, x0, x1, y, 'W')
    frame(g, 6, 6, 10, 10, 'i')

add('token_marnie', token('h', 'D', gl_bread))
add('token_bram', token('t', 'T', gl_gear))
add('token_oda', token('G', 'D', gl_coin))
add('token_nella', token('a', 'A', gl_fish))
add('token_halden', token('g', 'S', gl_leaf))
add('token_tobin', token('C', 'D', gl_pick))
add('token_wisp', token('s', 'S', gl_lily))
add('token_pip', token('r', 'D', gl_egg))

# ---------------------------------------------------------------- town_anchor (block)
g = G()
rect(g, 0, 0, 15, 15, 't')
for y in range(0, 16, 4):
    hline(g, 0, 15, y, 'T')
for row, offset in enumerate(range(0, 16, 4)):
    shift = 4 if (row % 2 == 0) else 0
    for x in range(-4 + shift, 16, 8):
        vline(g, x, offset, offset + 3, 'T')
disc(g, 8, 8, 4.4, 'D')
disc(g, 8, 8, 3.6, 'C')
px(g, [(6,8),(7,8),(8,8),(9,8),(7,7),(8,7),(6,9),(7,9),(8,9),(9,9),(5,8),(9,7)], 'k')
st(g, 5, 8, 'k'); st(g, 10, 8, 'D')
add('town_anchor', g)

out = pathlib.Path(__file__).parent / 'batch1.json'
out.write_text(json.dumps(icons, indent=1))
print(f"wrote {len(icons)} icons -> {out}")
