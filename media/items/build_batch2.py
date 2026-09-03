#!/usr/bin/env python3
"""Builder for batch2 items — Little Kettle Valley.
Generates 16x16 pixel grids programmatically (instead of hand-typing DSL
strings) and writes media/items/batch2.json for tools/scripts/pixel.py to
render. Re-run this file, then:
  venv/bin/python tools/scripts/pixel.py render media/items/batch2.json media/items/png
  venv/bin/python tools/scripts/pixel.py check media/items/png
  venv/bin/python tools/scripts/pixel.py sheet media/items/png media/items/sheet_batch2.png 10
"""
import json, pathlib, math

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "media" / "items" / "batch2.json"

N = 16

def new_grid():
    return [['.' for _ in range(N)] for _ in range(N)]

def setpx(g, x, y, ch):
    if 0 <= x < N and 0 <= y < N:
        g[y][x] = ch

def get(g, x, y):
    if 0 <= x < N and 0 <= y < N:
        return g[y][x]
    return '.'

def rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            setpx(g, x, y, ch)

def rect_border(g, x0, y0, x1, y1, ch):
    for x in range(x0, x1 + 1):
        setpx(g, x, y0, ch); setpx(g, x, y1, ch)
    for y in range(y0, y1 + 1):
        setpx(g, x0, y, ch); setpx(g, x1, y, ch)

def hline(g, x0, x1, y, ch):
    rect(g, x0, y, x1, y, ch)

def vline(g, x, y0, y1, ch):
    rect(g, x, y0, x, y1, ch)

def dot(g, x, y, ch):
    setpx(g, x, y, ch)

def filled_circle(g, cx, cy, r, ch, skip_existing=False):
    for y in range(N):
        for x in range(N):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                if skip_existing and get(g, x, y) != '.':
                    continue
                setpx(g, x, y, ch)

def ring(g, cx, cy, r_out, r_in, ch):
    for y in range(N):
        for x in range(N):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if r_in * r_in <= d2 <= r_out * r_out:
                setpx(g, x, y, ch)

def outline(g, ch, diag=False):
    """Paint a 1px outline into transparent cells touching a filled cell."""
    cells = [(x, y) for y in range(N) for x in range(N) if g[y][x] == '.']
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diag:
        neigh += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    to_set = []
    for x, y in cells:
        for dx, dy in neigh:
            if get(g, x + dx, y + dy) != '.':
                to_set.append((x, y))
                break
    for x, y in to_set:
        g[y][x] = ch

def rows(g):
    return [''.join(row) for row in g]

# tiny 3x5 bitmap font (rows top->bottom, '#'=on) for stamping single letters
FONT3x5 = {
    'A': ["###", "#.#", "###", "#.#", "#.#"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
}

def stamp_letter(g, letter, x0, y0, ch):
    pat = FONT3x5[letter]
    for dy, row in enumerate(pat):
        for dx, c in enumerate(row):
            if c == '#':
                dot(g, x0 + dx, y0 + dy, ch)

icons = []

def add(name, g):
    icons.append({"name": name, "rows": rows(g)})

# ---------------------------------------------------------------- planks --
def plank_texture(base, band, grain, seam, knot=None):
    g = new_grid()
    rect(g, 0, 0, 15, 15, base)
    # sparse single-row bands (subtle, not a checkerboard)
    for y in (3, 8, 12):
        hline(g, 0, 15, y, band)
    # short grain streaks, varied length, within each board
    for (x0, x1, y) in [(1, 4, 1), (7, 9, 2), (11, 14, 1), (1, 3, 6),
                          (7, 10, 5), (12, 14, 6), (1, 4, 10), (7, 9, 11),
                          (12, 15, 10), (2, 4, 14), (8, 10, 13), (12, 14, 14)]:
        hline(g, x0, x1, y, grain)
    # plank seams (vertical board separators)
    vline(g, 5, 0, 15, seam)
    vline(g, 11, 0, 15, seam)
    if knot:
        for x, y in [(2, 5), (8, 9), (13, 3)]:
            dot(g, x, y, knot)
    return g

add("green_oak_plank", plank_texture('c', 's', 'S', 'o', knot='p'))
add("seasoned_oak_board", plank_texture('o', 'O', 'D', 'i', knot='L'))

# -------------------------------------------------------------- sand/silica --
def pile(base, base2, speck, outline_ch):
    g = new_grid()
    # heaping mound silhouette
    spans = {2: (6, 9), 3: (5, 10), 4: (4, 11), 5: (3, 12), 6: (2, 13),
              7: (1, 14), 8: (1, 14), 9: (1, 14), 10: (2, 13), 11: (3, 12)}
    for y, (x0, x1) in spans.items():
        hline(g, x0, x1, y, base)
    # shade underside
    for y in (9, 10, 11):
        x0, x1 = spans[y]
        hline(g, x0, x1, y, base2)
    hline(g, 3, 12, 5, base2)
    # speckle highlight/texture
    for x, y in [(4, 4), (7, 3), (10, 4), (5, 7), (9, 7), (12, 6), (3, 8),
                  (6, 9), (11, 9), (8, 5)]:
        dot(g, x, y, speck)
    outline(g, outline_ch)
    return g

add("lake_sand", pile('c', 'u', 'p', 'D'))
add("washed_silica", pile('V', 'a', 'w', 'A'))

# -------------------------------------------------------------- spring water --
def spring_water():
    g = new_grid()
    # flask: round bulb + neck
    filled_circle(g, 7.5, 10.5, 4.4, 'a')
    rect(g, 6, 3, 9, 7, 'a')
    # glass outline
    outline(g, 'A')
    rect_border(g, 6, 2, 9, 3, 'A')
    # water shading
    filled_circle(g, 8.5, 11.5, 3.6, 'A', skip_existing=False)
    filled_circle(g, 6.5, 9.5, 1.6, 'w')  # highlight
    # cork/stopper
    rect(g, 6, 1, 9, 2, 'O')
    hline(g, 6, 9, 1, 'o')
    # sparkle
    dot(g, 11, 6, 'w'); dot(g, 4, 8, 'w')
    return g

add("spring_water", spring_water())

# -------------------------------------------------------------- works power tap --
def works_power_tap():
    g = new_grid()
    rect(g, 1, 1, 14, 14, 'C')
    rect(g, 1, 1, 14, 2, 'L')
    rect(g, 1, 13, 14, 14, 'D')
    # rivets
    for x, y in [(2, 2), (13, 2), (2, 13), (13, 13)]:
        dot(g, x, y, 'D')
    # dial plate
    filled_circle(g, 7.5, 7.5, 4.2, 'T')
    ring(g, 7.5, 7.5, 4.2, 3.4, 'D')
    filled_circle(g, 7.5, 7.5, 3.0, 't')
    dot(g, 7, 7, 'r'); dot(g, 8, 7, 'r'); dot(g, 7, 8, 'r'); dot(g, 8, 8, 'r')
    # needle
    dot(g, 9, 5, 'r'); dot(g, 10, 4, 'r')
    outline(g, 'D')
    return g

add("works_power_tap", works_power_tap())

# -------------------------------------------------------------- kettle plates --
def kettle_plate(letter_glyph):
    g = new_grid()
    rect(g, 2, 4, 13, 11, 'C')
    rect(g, 2, 4, 13, 5, 'L')
    rect(g, 2, 10, 13, 11, 'D')
    rect_border(g, 2, 4, 13, 11, 'D')
    for x, y in [(3, 5), (12, 5), (3, 10), (12, 10)]:
        dot(g, x, y, 'D')
    stamp_letter(g, letter_glyph, 6, 6, 'k')
    outline(g, 'D')
    return g

add("kettle_plate_a", kettle_plate('A'))
add("kettle_plate_b", kettle_plate('B'))

# -------------------------------------------------------------- ice auger --
def ice_auger():
    g = new_grid()
    # T-handle at top-left
    hline(g, 1, 6, 2, 'o')
    hline(g, 1, 6, 3, 'O')
    vline(g, 3, 3, 5, 'o')
    vline(g, 4, 3, 5, 'O')
    # diagonal shaft (two parallel rows = a solid rod)
    for i in range(9):
        x = 4 + i
        y = 5 + i
        dot(g, x, y, 't')
        dot(g, x + 1, y, 'V')
    # spiral thread flanges crossing the rod
    for i in range(0, 9, 2):
        x = 4 + i
        y = 5 + i
        dot(g, x - 1, y + 1, 'T')
        dot(g, x + 2, y - 1, 'V')
    # pointed tip
    dot(g, 13, 13, 'T'); dot(g, 14, 14, 'T'); dot(g, 14, 13, 'i')
    outline(g, 'T')
    return g

add("ice_auger", ice_auger())

# -------------------------------------------------------------- dredge net --
def dredge_net():
    g = new_grid()
    # pole diagonal
    for i in range(12):
        x = 2 + i
        y = 14 - i
        dot(g, x, y, 'o')
    dot(g, 1, 15, 'O'); dot(g, 2, 15, 'O')
    # net hoop (circle outline) near top
    ring(g, 9.5, 5.5, 4.6, 3.7, 't')
    # mesh lines inside hoop
    for (x0, y0, x1, y1) in [(7, 4, 12, 7), (7, 7, 12, 4), (6, 5, 13, 6), (9, 2, 9, 9)]:
        # simple bresenham-ish
        steps = 8
        for s in range(steps + 1):
            xx = round(x0 + (x1 - x0) * s / steps)
            yy = round(y0 + (y1 - y0) * s / steps)
            d2 = (xx - 9.5) ** 2 + (yy - 5.5) ** 2
            if d2 <= 3.6 * 3.6:
                if get(g, xx, yy) == '.':
                    dot(g, xx, yy, 'T')
    outline(g, 'T')
    return g

add("dredge_net", dredge_net())

# -------------------------------------------------------------- oda broom --
def oda_broom():
    g = new_grid()
    # handle diagonal, bottom-left to top-right
    for i in range(9):
        x = 4 + i
        y = 11 - i
        dot(g, x, y, 'o')
        dot(g, x + 1, y, 'O')
    # binding where bristles meet handle
    dot(g, 3, 11, 'D'); dot(g, 4, 12, 'D'); dot(g, 3, 12, 'D')
    # bristle fan, flush against the handle base, flaring down-left
    bristles = [
        (0, 14), (1, 14), (2, 14), (3, 14),
        (0, 15), (1, 15), (2, 15), (3, 15), (4, 15),
        (1, 13), (2, 13), (3, 13),
        (0, 13), (2, 12), (3, 12),
    ]
    for x, y in bristles:
        dot(g, x, y, 'y')
    for x, y in [(0, 15), (1, 15), (0, 14), (2, 15), (4, 15)]:
        dot(g, x, y, 'G')
    outline(g, 'O')
    return g

add("oda_broom", oda_broom())

# -------------------------------------------------------------- copper kettle trophy --
def copper_kettle_trophy():
    g = new_grid()
    # body
    filled_circle(g, 7.5, 10, 5.0, 'C')
    rect(g, 3, 7, 12, 10, 'C')
    # shading
    for x in range(3, 13):
        setpx(g, x, 13, 'D') if (x-7.5)**2 <= 5.0*5.0 - 9 else None
    filled_circle(g, 9, 12, 3.2, 'D', skip_existing=False)
    filled_circle(g, 6, 8, 1.6, 'L')
    outline(g, 'D')
    # neck + lid
    rect(g, 6, 4, 9, 6, 'L')
    rect_border(g, 6, 4, 9, 6, 'D')
    filled_circle(g, 7.5, 3, 1.3, 'G')
    # spout
    for i in range(3):
        dot(g, 12 + i, 6 - i, 'L')
        dot(g, 13 + i, 7 - i, 'D')
    # handle
    for (x, y) in [(1,7),(1,8),(1,9),(1,10),(2,6),(2,11),(3,6),(3,11)]:
        dot(g, x, y, 'D')
    # sparkle
    dot(g, 5, 8, 'w'); dot(g, 4, 9, 'Y')
    return g

add("copper_kettle_trophy", copper_kettle_trophy())

# ================================================================= paper goods
def paper_base(w=11, h=13, x0=3, y0=1, base='p', edge='O'):
    g = new_grid()
    rect(g, x0, y0, x0 + w - 1, y0 + h - 1, base)
    outline(g, edge)
    return g

def scrip():
    g = new_grid()
    filled_circle(g, 7.5, 7.5, 6.3, 'C')
    ring(g, 7.5, 7.5, 6.3, 5.3, 'L')
    filled_circle(g, 7.5, 7.5, 5.2, 'C')
    ring(g, 7.5, 7.5, 5.2, 4.6, 'D')
    # tiny kettle stamp: body + spout + handle
    filled_circle(g, 7.5, 8.5, 2.6, 'D')
    dot(g, 10, 7, 'D'); dot(g, 11, 6, 'D')
    dot(g, 5, 6, 'D'); dot(g, 5, 7, 'D')
    dot(g, 7, 5, 'D'); dot(g, 8, 5, 'D')
    outline(g, 'D')
    return g

add("scrip", scrip())

def letter():
    g = paper_base(w=11, h=8, x0=2, y0=4, base='p', edge='O')
    # folded flap lines
    for i in range(6):
        dot(g, 3 + i, 5 + i, 'c')
        dot(g, 12 - i, 5 + i, 'c')
    hline(g, 3, 12, 4, 'c')
    # wax seal
    filled_circle(g, 7.5, 8.5, 2.1, 'r')
    ring(g, 7.5, 8.5, 2.1, 1.5, 'D')
    dot(g, 7, 8, 'D'); dot(g, 8, 8, 'D')
    return g

add("letter", letter())

def deed(seal='ribbon', paper_ch='p', seal_ch='r'):
    g = new_grid()
    rect(g, 2, 1, 12, 13, paper_ch)
    # torn/rolled top+bottom edge notches
    for x in (2, 4, 6, 8, 10, 12):
        setpx(g, x, 1, 'c')
    outline(g, 'O')
    # a few text lines
    for y in (4, 6, 8):
        hline(g, 4, 10, y, 'O')
    if seal == 'ribbon':
        vline(g, 6, 1, 13, seal_ch)
        vline(g, 8, 1, 13, seal_ch)
        rect(g, 5, 9, 9, 11, seal_ch)
        outline(g, 'D' if seal_ch == 'r' else 'D')
    elif seal == 'gear':
        filled_circle(g, 7.5, 10, 2.6, 't')
        for ang in range(0, 360, 45):
            dx = round(2.9 * math.cos(math.radians(ang)))
            dy = round(2.9 * math.sin(math.radians(ang)))
            dot(g, 7 + dx, 10 + dy, 'T')
        filled_circle(g, 7.5, 10, 1.2, 'T')
    elif seal == 'copper':
        filled_circle(g, 7.5, 10, 2.6, 'C')
        ring(g, 7.5, 10, 2.6, 1.9, 'D')
    return g

add("deed", deed(seal='ribbon', paper_ch='p', seal_ch='s'))
add("deed_works", deed(seal='gear', paper_ch='p'))
add("kettle_deed", deed(seal='copper', paper_ch='u'))

def bounty_receipt():
    g = new_grid()
    rect(g, 3, 3, 12, 11, 'c')
    # torn zigzag right edge
    for i, y in enumerate(range(3, 12)):
        setpx(g, 12 + (i % 2), y, 'c')
    outline(g, 'O')
    hline(g, 5, 10, 5, 'r')
    for y in (7, 9):
        hline(g, 5, 10, y, 'O')
    dot(g, 10, 5, 'r'); dot(g, 9, 5, 'r')
    return g

add("bounty_receipt", bounty_receipt())

def catalogue():
    g = new_grid()
    rect(g, 3, 2, 11, 13, 's')
    rect(g, 3, 2, 11, 3, 'S')
    vline(g, 3, 2, 13, 'S')
    rect(g, 10, 3, 11, 13, 'c')  # page edges
    outline(g, 'S')
    rect(g, 5, 6, 9, 6, 'c')
    rect(g, 5, 8, 9, 8, 'c')
    filled_circle(g, 7, 5, 1.1, 'y')
    return g

add("catalogue", catalogue())

def odas_ledger():
    g = new_grid()
    rect(g, 2, 2, 12, 13, 'O')
    rect(g, 2, 2, 12, 3, 'o')
    rect(g, 11, 3, 12, 13, 'c')
    for y in range(4, 13, 2):
        dot(g, 11, y, 'p')
    outline(g, 'i')
    vline(g, 2, 2, 13, 'i')
    dot(g, 6, 7, 'C'); dot(g, 7, 7, 'C'); dot(g, 6, 8, 'C'); dot(g, 7, 8, 'C')
    return g

add("odas_ledger", odas_ledger())

def turbine_notes():
    g = new_grid()
    rect(g, 3, 2, 12, 13, 's')
    rect(g, 11, 2, 12, 13, 'c')
    for y in range(3, 13, 2):
        dot(g, 11, y, 'S')
    outline(g, 'S')
    # gear icon on cover
    filled_circle(g, 6.5, 7, 2.6, 'T')
    for ang in range(0, 360, 45):
        dx = round(2.9 * math.cos(math.radians(ang)))
        dy = round(2.9 * math.sin(math.radians(ang)))
        dot(g, 6 + dx, 7 + dy, 'T')
    filled_circle(g, 6.5, 7, 1.1, 't')
    return g

add("turbine_notes", turbine_notes())

def deep_survey():
    g = new_grid()
    # rolled scroll: cylinder viewed from the side
    rect(g, 2, 3, 13, 12, 'p')
    filled_circle(g, 2.5, 7.5, 2.6, 'c')
    filled_circle(g, 13.5, 7.5, 2.6, 'c')
    outline(g, 'O')
    for y in (5, 7, 9):
        hline(g, 5, 11, y, 'O')
    # pick mark
    dot(g, 8, 10, 'T'); dot(g, 9, 9, 'T'); dot(g, 7, 9, 'T'); dot(g, 8, 8, 'T')
    return g

add("deep_survey", deep_survey())

def framed_town_map():
    g = new_grid()
    rect(g, 1, 1, 14, 14, 'O')
    rect(g, 2, 2, 13, 13, 'o')
    rect(g, 3, 3, 12, 12, 'p')
    outline(g, 'i')
    # map lines: roads + water
    hline(g, 4, 11, 6, 'O')
    vline(g, 7, 4, 11, 'O')
    for x, y in [(5, 8), (6, 9), (9, 5), (10, 4)]:
        dot(g, x, y, 'a')
    dot(g, 8, 8, 'r')
    return g

add("framed_town_map", framed_town_map())

def place_setting():
    g = new_grid()
    # plate: flat top-down dish, centered low
    filled_circle(g, 8, 11, 4.6, 'W')
    ring(g, 8, 11, 4.6, 3.6, 't')
    filled_circle(g, 8, 11, 2.6, 'W')
    outline(g, 'T')
    # fork, standing at left edge of the plate
    for x in (2, 4):
        vline(g, x, 1, 4, 'V')
    vline(g, 3, 1, 4, 'V')
    vline(g, 3, 4, 9, 'V')
    # cup/mug, standing at right edge of the plate (small, with handle)
    rect(g, 11, 2, 13, 6, 'C')
    hline(g, 11, 13, 2, 'L')
    hline(g, 11, 13, 6, 'D')
    dot(g, 14, 3, 'D'); dot(g, 14, 4, 'D'); dot(g, 14, 5, 'D')
    return g

add("place_setting", place_setting())

# ================================================================= crates
def crate(face_extra=None, wood='o', wood_dark='O'):
    g = new_grid()
    rect(g, 1, 3, 14, 14, wood)
    # cross-brace X
    for i in range(12):
        dot(g, 2 + i, 4 + i * 10 // 12, wood_dark)
        dot(g, 2 + i, 13 - i * 10 // 12, wood_dark)
    rect_border(g, 1, 3, 14, 14, wood_dark)
    hline(g, 1, 14, 3, wood_dark)
    outline(g, 'i')
    if face_extra:
        face_extra(g)
    return g

def delivery_crate_extra(g):
    rect(g, 4, 6, 11, 10, 'c')
    rect_border(g, 4, 6, 11, 10, 'O')
    hline(g, 5, 10, 8, 'r')

add("delivery_crate", crate(delivery_crate_extra))

def courier_parcel():
    g = new_grid()
    rect(g, 3, 3, 12, 12, 'p')
    outline(g, 'O')
    # string cross
    hline(g, 3, 12, 7, 'O')
    vline(g, 7, 3, 12, 'O')
    rect(g, 6, 6, 8, 8, 'c')
    filled_circle(g, 7, 7, 0.9, 'r')
    return g

add("courier_parcel", courier_parcel())

def feast_crate_extra(g):
    # apples poking up
    filled_circle(g, 5, 4, 2.0, 'r')
    dot(g, 5, 2, 'g')
    filled_circle(g, 11, 3, 1.8, 'r')
    dot(g, 11, 1, 'g')
    # bread loaf
    filled_circle(g, 8, 4, 2.2, 'u')
    hline(g, 6, 10, 3, 'o')

add("feast_crate", crate(feast_crate_extra))

def animal_crate_extra(kind):
    def fn(g):
        if kind == 'hen':
            filled_circle(g, 8, 3.5, 3.0, 'W')
            dot(g, 8, 1, 'r'); dot(g, 9, 0, 'r')
            dot(g, 6, 3, 'G')
            dot(g, 9, 4, 'i')
        elif kind == 'cow':
            filled_circle(g, 8, 3.5, 3.2, 'W')
            dot(g, 6, 2, 'i'); dot(g, 10, 4, 'i'); dot(g, 8, 1, 'i')
            dot(g, 6, 4, 'h'); dot(g, 10, 3, 'h')
            dot(g, 7, 4, 'i'); dot(g, 9, 4, 'i')
        else:  # sheep
            filled_circle(g, 8, 3.5, 3.2, 'W')
            filled_circle(g, 8, 4, 1.6, 'c')
            dot(g, 6, 4, 'i'); dot(g, 10, 4, 'i')
    return fn

add("hen_crate", crate(animal_crate_extra('hen')))
add("cow_crate", crate(animal_crate_extra('cow')))
add("sheep_crate", crate(animal_crate_extra('sheep')))

def chicken_feed():
    g = new_grid()
    # sack silhouette: round bulging body, pinched neck near the top
    filled_circle(g, 7.5, 10.5, 4.8, 'u')
    rect(g, 4, 6, 11, 10, 'u')
    rect(g, 5, 4, 10, 6, 'u')
    filled_circle(g, 7.5, 4, 1.6, 'u')
    outline(g, 'O')
    # tie at the neck
    hline(g, 5, 10, 5, 'O')
    dot(g, 6, 2, 'O'); dot(g, 9, 2, 'O'); dot(g, 7, 2, 'o'); dot(g, 8, 2, 'o')
    # grain spilling
    for x, y in [(3, 12), (4, 13), (11, 12), (12, 13), (2, 13), (13, 12)]:
        dot(g, x, y, 'G')
    return g

add("chicken_feed", chicken_feed())

def firewood_bundle():
    g = new_grid()
    for i, y0 in enumerate((2, 6, 10)):
        rect(g, 1, y0, 14, y0 + 3, 'O' if i % 2 else 'o')
        filled_circle(g, 2.5, y0 + 1.5, 1.4, 'p')
        filled_circle(g, 13.5, y0 + 1.5, 1.4, 'p')
        ring(g, 2.5, y0 + 1.5, 1.4, 0.7, 'D')
        ring(g, 13.5, y0 + 1.5, 1.4, 0.7, 'D')
    outline(g, 'i')
    # rope ties
    vline(g, 5, 1, 14, 'C')
    vline(g, 10, 1, 14, 'C')
    return g

add("firewood_bundle", firewood_bundle())

# ================================================================= textiles
def blanket():
    g = new_grid()
    rect(g, 1, 4, 14, 12, 'W')
    for y in (6, 9):
        hline(g, 1, 14, y, 'r')
    for y in (5, 10):
        hline(g, 1, 14, y, 's')
    outline(g, 'T')
    # folded edge shading
    rect(g, 1, 4, 14, 4, 'w')
    return g

add("blanket", blanket())

def winter_cloak():
    g = new_grid()
    # hood triangle
    filled_circle(g, 8, 3, 3.0, 's')
    # body
    for y in range(5, 15):
        w = 3 + (y - 5) // 2
        hline(g, 8 - w, 8 + w, y, 's')
    # fold shading
    vline(g, 8, 5, 14, 'S')
    for y in range(6, 14, 2):
        w = 3 + (y - 5) // 2
        dot(g, 8 - w + 1, y, 'S')
        dot(g, 8 + w - 1, y, 'S')
    outline(g, 'S')
    # clasp
    dot(g, 7, 6, 'C'); dot(g, 8, 6, 'C')
    return g

add("winter_cloak", winter_cloak())

# ================================================================= consumables
def winter_tonic():
    g = new_grid()
    filled_circle(g, 7.5, 11, 4.0, 'G')
    rect(g, 6, 5, 9, 11, 'G')
    outline(g, 'D')
    rect_border(g, 6, 5, 9, 11, 'D')
    filled_circle(g, 6.3, 9, 1.3, 'Y')
    # cork
    rect(g, 6, 2, 9, 4, 'o')
    hline(g, 6, 9, 2, 'O')
    return g

add("winter_tonic", winter_tonic())

def winter_tomato():
    g = new_grid()
    filled_circle(g, 7.5, 9, 5.6, 'r')
    outline(g, 'D')
    filled_circle(g, 5.5, 6.5, 1.7, 'u')
    # stem + leaves
    dot(g, 7, 2, 'g'); dot(g, 8, 2, 'g')
    for x, y in [(5, 3), (10, 3), (6, 2), (9, 2), (7, 1), (8, 1)]:
        dot(g, x, y, 'g')
    return g

add("winter_tomato", winter_tomato())

# ================================================================= lanterns
def lantern(frame, glow_outer, glow_inner, ornate=False):
    g = new_grid()
    # hanging loop
    vline(g, 7, 0, 1, frame); vline(g, 8, 0, 1, frame)
    rect(g, 6, 1, 9, 2, frame)
    # cage top/bottom
    rect(g, 4, 3, 11, 4, frame)
    rect(g, 4, 11, 11, 12, frame)
    rect(g, 5, 13, 10, 14, frame)
    # body glow
    rect(g, 5, 5, 10, 10, glow_outer)
    rect(g, 6, 6, 9, 9, glow_inner)
    # frame ribs
    vline(g, 4, 3, 12, frame)
    vline(g, 11, 3, 12, frame)
    if ornate:
        vline(g, 7, 5, 10, frame)
        vline(g, 8, 5, 10, frame)
        dot(g, 3, 7, frame); dot(g, 12, 7, frame)
    outline(g, 'i' if not ornate else 'D')
    return g

add("paper_lantern", lantern('w', 'Y', 'w'))
add("josies_lantern", lantern('C', 'y', 'Y'))
add("hearthkeepers_lantern", lantern('G', 'Y', 'w', ornate=True))

# ================================================================= plushie / tokens
def plushie_token():
    g = new_grid()
    # tag string
    dot(g, 7, 1, 'T'); dot(g, 8, 1, 'T')
    dot(g, 6, 2, 'T'); dot(g, 9, 2, 'T')
    # tiny plush kettle face (round, cute)
    filled_circle(g, 7.5, 9, 5.2, 'C')
    ring(g, 7.5, 9, 5.2, 4.3, 'L')
    outline(g, 'D')
    # spout + handle nubs
    dot(g, 12, 7, 'D'); dot(g, 13, 6, 'D')
    dot(g, 2, 7, 'D'); dot(g, 1, 8, 'D')
    # cute face
    filled_circle(g, 5.5, 8.5, 1.0, 'i')
    filled_circle(g, 9.5, 8.5, 1.0, 'i')
    dot(g, 5, 8, 'w'); dot(g, 9, 8, 'w')
    for x, y in [(6, 11), (7, 12), (8, 12), (9, 11)]:
        dot(g, x, y, 'D')
    return g

add("plushie_token", plushie_token())

TOKEN_RESIDENTS = {
    'marnie': ('h', 'D', 'bread'),
    'bram':   ('t', 'T', 'gear'),
    'oda':    ('G', 'D', 'coin'),
    'nella':  ('a', 'A', 'fish'),
    'halden': ('g', 'S', 'leaf'),
    'tobin':  ('C', 'D', 'pick'),
    'wisp':   ('s', 'S', 'lily'),
    'pip':    ('r', 'D', 'egg'),
}

def token(color, edge, glyph):
    g = new_grid()
    filled_circle(g, 7.5, 7.5, 6.4, edge)
    filled_circle(g, 7.5, 7.5, 5.3, color)
    ring(g, 7.5, 7.5, 5.3, 4.6, edge)
    outline(g, edge)
    if glyph == 'bread':
        filled_circle(g, 7.5, 8, 2.6, 'u')
        hline(g, 5, 10, 7, 'O')
        hline(g, 6, 9, 6, 'O')
    elif glyph == 'gear':
        filled_circle(g, 7.5, 7.5, 2.6, 't')
        for ang in range(0, 360, 45):
            dx = round(2.9 * math.cos(math.radians(ang)))
            dy = round(2.9 * math.sin(math.radians(ang)))
            dot(g, 7 + dx, 7 + dy, 'T')
        filled_circle(g, 7.5, 7.5, 1.1, 'T')
    elif glyph == 'coin':
        filled_circle(g, 7.5, 7.5, 2.6, 'G')
        ring(g, 7.5, 7.5, 2.6, 1.9, 'D')
    elif glyph == 'fish':
        filled_circle(g, 6.3, 7.5, 2.4, 'w')
        # tail fin (triangle)
        for x, y in [(9, 5), (10, 6), (9, 6), (10, 8), (9, 8), (9, 9), (10, 9)]:
            dot(g, x, y, 'w')
        dot(g, 5, 7, 'i')
        dot(g, 5, 9, 'A')
    elif glyph == 'leaf':
        filled_circle(g, 7.5, 7.5, 2.8, 'S')
        vline(g, 7, 5, 10, 'O')
        dot(g, 6, 6, 'S'); dot(g, 9, 9, 'S')
    elif glyph == 'pick':
        # handle: diagonal from lower-left to center
        for i in range(5):
            dot(g, 5 + i, 10 - i, 'T')
        # head: shallow V-shaped chevron pick-head above the handle
        for i in range(4):
            dot(g, 6 + i, 4 + i, 'T')
            dot(g, 10 - i, 4 + i, 'T')
        dot(g, 7, 4, 't'); dot(g, 8, 4, 't'); dot(g, 9, 4, 't')
    elif glyph == 'lily':
        # round pad with a wedge notch (classic lily-pad silhouette)
        filled_circle(g, 7.5, 7.5, 2.9, 'g')
        for x, y in [(8, 5), (9, 5), (9, 6), (9, 7), (8, 6)]:
            setpx(g, x, y, edge)
        dot(g, 6, 7, 'S'); dot(g, 7, 8, 'S')
    elif glyph == 'egg':
        filled_circle(g, 7.5, 8, 2.4, 'w')
        rect(g, 6, 6, 9, 7, 'w')
        dot(g, 7, 7, 'u'); dot(g, 8, 8, 'u')
    return g

for name, (color, edge, glyph) in TOKEN_RESIDENTS.items():
    add(f"token_{name}", token(color, edge, glyph))

# ================================================================= town anchor block
def town_anchor():
    g = new_grid()
    rect(g, 0, 0, 15, 15, 't')
    # brick courses
    for y in (3, 7, 11, 15):
        hline(g, 0, 15, y, 'T')
    for x in (4, 12):
        vline(g, x, 0, 3, 'T')
    for x in (0, 8):
        vline(g, x, 4, 7, 'T')
    for x in (4, 12):
        vline(g, x, 8, 11, 'T')
    for x in (0, 8):
        vline(g, x, 12, 15, 'T')
    # copper kettle stamp, centered
    filled_circle(g, 7.5, 8, 4.6, 'C')
    ring(g, 7.5, 8, 4.6, 3.8, 'D')
    filled_circle(g, 7.5, 8.5, 2.4, 'D')
    dot(g, 10, 7, 'D'); dot(g, 11, 6, 'D')
    dot(g, 5, 6, 'D')
    dot(g, 6, 5, 'D'); dot(g, 8, 5, 'D')
    dot(g, 6, 7, 'L')
    return g

add("town_anchor", town_anchor())

json_out = json.dumps(icons, indent=1)
OUT.write_text(json_out)
print(f"wrote {len(icons)} icons -> {OUT}")
