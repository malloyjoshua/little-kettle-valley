#!/usr/bin/env python3
"""plan_town.py - lay out Little Kettle Valley from real structure templates.

Reads the installed template NBTs (Towns and Towers / Dungeons and Taverns /
vanilla) straight out of the mod jars, solves a collision-free village plan
around the Town Anchor, and writes:

    media/town_plan.json                        the plan, human readable
    pack/kubejs/server_scripts/town_plan.js     global.valleyTownPlan (OFF marks,
                                                anchor/works-relative command
                                                groups, verification probes)
    pack/kubejs/data/valley/functions/setup/place_ruin.mcfunction
    pack/kubejs/data/valley/functions/act1/cottage.mcfunction
    pack/kubejs/data/valley/functions/act1/square_path.mcfunction

Every pad rectangle, apron, street and probe below is COMPUTED from the
template's own measured footprint - there are no hand-typed building
rectangles anywhere in the pack after this runs.

Run:  tools/venv/bin/python tools/scripts/plan_town.py
"""
import io, gzip, json, math, os, pathlib, re, sys, zipfile, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.chdir(ROOT)

JARS = {
    'kaisyn': 'server/mods/Towns-and-Towers-1.12-Fabric+Forge.jar',
    'nova_structures': 'server/mods/dungeons-and-taverns-3.0.3.f.jar',
    'minecraft': ('server/libraries/net/minecraft/server/1.20.1-20230612.114412/'
                  'server-1.20.1-20230612.114412-extra.jar'),
}
import nbtlib  # noqa: E402  (tools/venv)

# =============================================================================
# 1. Template loading
# =============================================================================
_zips, _cache = {}, {}


def template(tid):
    """-> {'size':[x,y,z], 'blocks':{(x,y,z):(name, props)}}"""
    if tid in _cache:
        return _cache[tid]
    ns, path = tid.split(':', 1)
    if ns in JARS:
        jar = JARS[ns]
        if jar not in _zips:
            _zips[jar] = zipfile.ZipFile(jar)
        raw = _zips[jar].read('data/%s/structures/%s.nbt' % (ns, path))
    else:
        # the pack's own datapack structures (valley:pier, valley:noticeboard,
        # valley:mill_race). They are placed by the groups, so the write-set
        # replay in section 11 has to be able to size them too.
        raw = pathlib.Path('pack/kubejs/data/%s/structures/%s.nbt' % (ns, path)).read_bytes()
    f = nbtlib.File.parse(io.BytesIO(gzip.decompress(raw)))
    root = f if 'blocks' in f else f['']
    pal = []
    for p in root['palette']:
        props = {k: str(v) for k, v in dict(p['Properties']).items()} if 'Properties' in p else {}
        pal.append((str(p['Name']), props))
    g = {}
    for b in root['blocks']:
        g[tuple(int(v) for v in b['pos'])] = pal[int(b['state'])]
    out = {'size': [int(v) for v in root['size']], 'blocks': g}
    _cache[tid] = out
    return out


# =============================================================================
# 2. Rotation maths.  Mirrors vanilla StructureTemplate.calculateRelativePosition
#    with pivot (0,0,0), which is what /place template uses.
# =============================================================================
ROTS = ['none', 'clockwise_90', '180', 'counterclockwise_90']


def rot_pos(p, r):
    x, y, z = p
    if r == 0:
        return (x, y, z)
    if r == 1:
        return (-z, y, x)          # CLOCKWISE_90
    if r == 2:
        return (-x, y, -z)         # 180
    return (z, y, -x)              # COUNTERCLOCKWISE_90


_DIRS = ['north', 'east', 'south', 'west']


def rot_dir(d, r):
    if d not in _DIRS:
        return d
    return _DIRS[(_DIRS.index(d) + r) % 4]


def footprint(size, r):
    sx, _, sz = size
    return (sz, sx) if r in (1, 3) else (sx, sz)


def origin_offset(size, r):
    """origin = minCorner - offset, where offset is the min rotated coord."""
    sx, _, sz = size
    xs, zs = [], []
    for a in (0, sx - 1):
        for b in (0, sz - 1):
            p = rot_pos((a, 0, b), r)
            xs.append(p[0]); zs.append(p[2])
    return (min(xs), min(zs))


_STEP = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}


class Placed(object):
    """A template pinned to an anchor-relative min corner."""

    def __init__(self, name, tid, r, minx, minz, y_base=0, margin=2):
        self.name, self.tid, self.r = name, tid, r
        t = template(tid)
        self.size = t['size']
        self.grid = t['blocks']
        self.y_base = y_base
        self.margin = margin
        self.fw, self.fd = footprint(self.size, r)
        self.x0, self.z0 = minx, minz
        self.x1, self.z1 = minx + self.fw - 1, minz + self.fd - 1
        ox, oz = origin_offset(self.size, r)
        self.ox, self.oz = minx - ox, minz - oz
        # The pad's OWN level, as a dy off the anchor. Filled in by section 6.5 from the
        # median surface under this footprint; 0 until then, and 0 forever when the
        # planner is run without a world to read (`--site`/`--world` absent).
        self.dy = 0
        self.oy = -y_base
        self.y0, self.y1 = -y_base, -y_base + self.size[1] - 1

    def abs(self, lp):
        """local (x,y,z) -> anchor-relative (dx,dy,dz)"""
        rx, ry, rz = rot_pos(lp, self.r)
        return (self.ox + rx, self.oy + ry, self.oz + rz)

    def pad(self):
        m = self.margin
        return (self.x0 - m, self.z0 - m, self.x1 + m, self.z1 + m)

    def find(self, pred):
        return [(lp, b) for lp, b in sorted(self.grid.items()) if pred(b)]

    # Blocks you can stand in or walk through: they do not stop a doorway from
    # being a way out.  A door's own two halves are in here because the cell a
    # door stands in IS the cell you walk through.
    WALK_THROUGH = ('door', 'carpet', 'torch', 'sign', 'button', 'pressure_plate',
                    'banner', 'flower', 'grass', 'fern', 'sapling', 'bush', 'snow',
                    'ladder', 'rail', 'vine', 'candle', 'chain', 'light', 'jigsaw',
                    'void', 'lantern', 'string', 'lily', 'wheat', 'seagrass')

    def _blocked_cols(self, y):
        """anchor-relative (dx,dz) columns this template WALLS OFF at y..y+1."""
        out = set()
        for lp, b in self.grid.items():
            a = self.abs(lp)
            if a[1] != y and a[1] != y + 1:
                continue
            if b[0] in AIRY or any(k in b[0] for k in Placed.WALK_THROUGH):
                continue
            out.add((a[0], a[2]))
        return out

    def door_out(self, d, blocked=None):
        """(steps, direction, first cell OUTSIDE the footprint) for a door.

        A vanilla door's `facing` is the way it SWINGS, not the way out: a door
        in a west wall placed from the yard reads facing=east, and Towns and
        Towers' templates use both conventions. apron_cmds() used to trust it,
        walked three steps INTO the house, and then ran its L-leg back out
        through the far wall - which is why eight of eleven front doors ended
        up with a dotted line of cobble laid through the building instead of a
        path to the road.

        So the way out is measured instead: step from the door cell in each of
        the four directions and keep the ones that leave the footprint without
        passing through a column the template has a wall in. An interior door
        (five of the tavern's six) has no such direction and returns None.
        """
        if blocked is None:
            blocked = self._blocked_cols(d['pos'][1])
        best = None
        for dirn in _DIRS:
            sx, sz = _STEP[dirn]
            x, z = d['pos'][0], d['pos'][2]
            n, ok = 0, False
            while True:
                x += sx
                z += sz
                n += 1
                if not (self.x0 <= x <= self.x1 and self.z0 <= z <= self.z1):
                    ok = True
                    break
                if (x, z) in blocked or n > 48:
                    break
            if ok and (best is None or (n, dirn) < (best[0], best[1])):
                best = (n, dirn, (x, z))
        return best

    def doors(self):
        out = []
        for lp, b in self.find(lambda b: b[0].endswith('_door') and b[1].get('half') == 'lower'):
            a = self.abs(lp)
            out.append({'pos': list(a), 'facing': rot_dir(b[1].get('facing', 'north'), self.r),
                        'block': b[0], 'local': list(lp)})
        gy = min([d['pos'][1] for d in out], default=0)
        out = [d for d in out if d['pos'][1] <= gy + 1]
        cache = {}
        for d in out:
            y = d['pos'][1]
            if y not in cache:
                cache[y] = self._blocked_cols(y)
            b = self.door_out(d, cache[y])
            d['outward'] = b[1] if b else None
            d['exit'] = list(b[2]) if b else None
            d['steps_out'] = b[0] if b else None

        # The FRONT door is a door you can actually walk out of, and of those,
        # the one whose doorstep is nearest the paving the town already has.
        # Sorting on "the facing points at the anchor" gave the tavern an
        # upstairs bedroom door as its front, and the apron then had nothing to
        # connect: the planned door was not reachable from the street at all.
        def rank(d):
            if not d['exit']:
                return (1, 10 ** 6, 0, tuple(d['pos']))
            if street_cells:
                near = min((d['exit'][0] - c[0]) ** 2 + (d['exit'][1] - c[1]) ** 2
                           for c in street_cells)
            else:
                near = d['exit'][0] ** 2 + d['exit'][1] ** 2
            return (0, near, d['steps_out'], tuple(d['pos']))
        out.sort(key=rank)
        return out

    FRAGILE = ('carpet', 'sign', 'torch', 'button', 'pressure_plate', 'rail', 'ladder',
               'vine', 'water', 'lava', 'snow', 'door', 'lantern', 'candle', 'pot',
               'jigsaw', 'concrete', 'air', 'sapling', 'flower', 'grass', 'bush',
               'wheat', 'farmland', 'bed', 'banner', 'painting', 'chain', 'lily',
               'minecraft:dirt', 'podzol', 'gravel')

    def _probe_pool(self):
        return [(lp, b) for lp, b in sorted(self.grid.items())
                if not any(k in b[0] for k in Placed.FRAGILE)]

    def probes(self):
        """Two blocks that must exist once this template is on the ground."""
        pool = self._probe_pool()
        if not pool:
            return []
        top = max(lp[1] for lp, _ in pool)
        lows = [t for t in pool if 1 <= t[0][1] <= 2] or [t for t in pool if t[0][1] <= 2]
        highs = [t for t in pool if t[0][1] >= top - 1]
        out, used = [], set()
        for cand, tag in ((lows, 'low'), (highs, 'high')):
            if not cand:
                continue
            lp, b = cand[len(cand) // 2]
            if tuple(self.abs(lp)) in used:
                lp, b = cand[0]
            used.add(tuple(self.abs(lp)))
            out.append({'label': '%s_%s' % (self.name, tag), 'pos': list(self.abs(lp)),
                        'block': b[0], 'origin': 'anchor'})
        return out


# =============================================================================
# 3. Town geometry
# =============================================================================
PLAZA = 12                       # plaza is dx/dz -12..12
PAD_DEEP = 10                    # dirt subgrade depth under a pad
ROAD_DEEP = 5

LAMPS = {
    'finale': [[-12, 1, 0], [12, 1, 0], [0, 1, -12], [0, 1, 12]],
    'q07': [[-2, 1, 8], [2, 1, 16]],
    'q34': [[-16, 1, 2], [-20, 1, 3], [-24, 1, 4], [-8, 1, 1]],
    'q74': [[4, 1, 6], [8, 1, 10], [12, 1, 14], [16, 1, 18], [20, 1, 22], [24, 1, 26],
            [-4, 1, 8], [-8, 1, 12], [-12, 1, 16], [-16, 1, 20], [-20, 1, 24],
            [6, 1, -8], [10, 1, -12], [14, 1, -16], [-6, 1, -8], [-10, 1, -12], [-14, 1, -16]],
}

# Streets: centre polylines.  Each lamp route above sits on a verge two blocks
# off the centre of the street named beside it, so the posts stand at the kerb.
STREETS = [
    ('high_street',      [(0, 13), (0, 31)]),
    ('mill_lane',        [(-13, 3), (-16, 4), (-20, 5), (-24, 6)]),
    # The four diagonals start OUTSIDE the plaza. Fanning them in from radius 7
    # filled all four corners of the square with street verge and left nowhere
    # for a market cart to stand; inside x/z +-12 the plaza is the road.
    ('lake_road',        [(6, 10), (10, 14), (14, 18), (18, 22), (22, 26), (24, 28)]),
    ('green_lane',       [(-6, 12), (-10, 16), (-14, 20), (-18, 24), (-20, 26)]),
    # The bathhouse stood on open snow with no way in. This spur leaves the
    # Lake Road at (12,16) and runs east to its front.
    ('bath_lane',        [(12, 16), (16, 16), (20, 16)]),
    # The two north lanes used to stop dead at +-13,-17, three plots short of
    # the store, the bell tower and the town hall - the whole north cluster
    # fronted nothing but snow. They are carried on to it.
    # ...and they start at the plaza's own edge rather than four blocks inside
    # it. Beginning at +-6,-10 put a two-block road clear across x +-4..+-8,
    # z -12..-8, which is the north half of the square: the Harvest Supper's
    # own bench rows are in there, and so was the only ground a market cart
    # could stand on. The square pays for its own paving; the lane does not
    # need to reach in and take it.
    ('north_east_lane',  [(8, -12), (10, -14), (13, -17), (13, -22), (10, -26)]),
    ('north_west_lane',  [(-8, -12), (-10, -14), (-13, -17), (-15, -21),
                          (-19, -24), (-24, -27)]),
    # East Lane. Marnie's cottage had a road; Pip's house, four plots further
    # east, was eighteen blocks from the nearest paving and the newcomer's
    # house at the far end was twenty-nine, which is a house in a field. This
    # runs along the north side of the inn's plot and out to the east end of
    # the town. It crosses the ground the Works is under - six blocks over its
    # ceiling - and that is fine: every street is laid in Act I and re-laid in
    # Act II, both of them long before act4_works seals the shell.
    ('east_lane',        [(13, -12), (22, -12), (32, -12), (45, -12)]),
    # The cart track up to Tobin's copper outcrop, off the east end of the East
    # Lane. Gravel and cobble like every other road, because the town works
    # that rock all winter.
    ('outcrop_road',     [(45, -14), (45, -30), (41, -36)]),
]
ROAD_BRUSH = 1                   # 1 -> three blocks wide (plus a gravel verge)
ROAD_CLEAR = 2                   # keep-clear half width for the solver

# =============================================================================
# The Works: the one thing in the plan that lives entirely underground, and the
# one thing a purely 2-D solver cannot see.
#
# OFF.works is anchor + [34,-6,-20] and valley_finales.js WORKS_SHELL seals
# works + [-6..8, -1..4, -6..8] - anchor-relative x 28..42, y -7..-2,
# z -26..-12. Act V's newcomer pad ran `fill ~42 ~-10 ~-26 ~57 ~-2 ~-11 dirt`
# straight along the east wall and punched ninety cells out of it, six blocks
# under a house nobody would ever dig up to find out why the room was flooded.
#
# So the box below is a THREE-DIMENSIONAL reservation:
#   * every build solved at or after Act IV keeps its pad out of the box's
#     x/z shadow (a pad digs to dy-10, which is under the shell's ceiling, so
#     for a pad the shadow IS the box), and
#   * section 11 replays every group's write set in the order the pack runs
#     them and fails the generator if one cell of the shell is written after
#     act4_works builds it.
# Groups that run BEFORE act4_works may write here freely: the shell goes up
# over whatever they left.
# =============================================================================
WORKS_OFF = [34, -6, -20]        # y is re-measured in 6.5: see WORKS_COVER
WORKS_COVER = 5                  # blocks of real rock that must lie over the shell's ceiling
WORKS_SHELL = {'x': [-6, 8], 'y': [-1, 4], 'z': [-6, 8]}
WORKS_RESERVE_MARGIN = 2


def works_box(margin=0):
    """The Works shell as an anchor-relative (x0,y0,z0,x1,y1,z1) box."""
    return (WORKS_OFF[0] + WORKS_SHELL['x'][0] - margin,
            WORKS_OFF[1] + WORKS_SHELL['y'][0] - margin,
            WORKS_OFF[2] + WORKS_SHELL['z'][0] - margin,
            WORKS_OFF[0] + WORKS_SHELL['x'][1] + margin,
            WORKS_OFF[1] + WORKS_SHELL['y'][1] + margin,
            WORKS_OFF[2] + WORKS_SHELL['z'][1] + margin)


# Rectangles nothing may be built on (dx0, dz0, dx1, dz1).
RESERVED = [
    ('plaza',       -PLAZA, -PLAZA, PLAZA, PLAZA),
    ('lake_works',  -15, 18, 15, 50),      # finaleAct2 levels lake+[-14..14]
    # Open ground immediately west of the square. Halden's still and the
    # Ribbit camp both stand on the plaza's own paving now (SCENES.q62 and
    # q59), and this keeps the approach to them clear of buildings.
    ('west_approach', -17, 3, -10, 8),
    ('river_lamps',  -4, 13, 4, 34),       # SCENES.q58 posts at x = +-2
]

# name, template, rotation, bearing (deg: 0=east, 90=south), min radius,
# margin, act, y_base, label, blurb
BUILDINGS = [
    # name, template, rotation, preferred min corner (dx,dz), margin, act, y_base,
    # arrival title, arrival subtitle
    ('inn',        'nova_structures:tavern/tavern_house_spruce',                   1, (15, -9), 2, 'act1', 0,
     'The Hearth',        'Marnie keeps the fire in the middle.'),
    ('mill',       'kaisyn:village/sunflower_plains_farm/side/sunflower_plains_windmill_1', 1, (-46, -4), 2, 'act1', 0,
     'The Broken Mill',   'Sixty years looking at a snapped axle.'),
    ('marnie_house', 'kaisyn:village/meadow_swiss/houses/meadow_small_house_2',    0, (16, -25), 2, 'act1', 0,
     "Marnie's Cottage",  'Four years of watching a cold chimney.'),
    ('pip_house',  'kaisyn:village/meadow_swiss/houses/meadow_small_house_1',      0, (29, -25), 2, 'act1', 0,
     "Pip's Place",       'He is being extremely useful.'),
    ('granary',    'kaisyn:village/exclusives/rustic/houses/rustic_barn_professions_1', 0, (-36, 18), 2, 'act2', 1,
     'The Granary',       'Twelve alcoves, one winter to fill them.'),
    ('garden',     'kaisyn:village/exclusives/classic/houses/classic_small_farm_1', 0, (-12, -40), 2, 'act2', 0,
     'The Hedge Garden',  "Halden's rows. The quiet corner of town."),
    ('store',      'kaisyn:village/meadow_swiss/houses/meadow_butcher_and_mason_1', 0, (6, -36), 2, 'act3', 0,
     "Oda's Store",       'Eleven years of ledger, no stock.'),
    ('church',     'kaisyn:village/exclusives/classic/houses/classic_church_1',    0, (-5, -24), 2, 'act3', 0,
     'The Bell Tower',    'Pip gets to ring it. Marnie said.'),
    ('town_hall',  'kaisyn:village/meadow_swiss/houses/meadow_large_house_1',      0, (-30, -28), 2, 'act5', 0,
     'The Town Hall',     'Fifteen people, arguing in the warm.'),
    ('newcomer_tess',  'kaisyn:village/meadow_swiss/houses/meadow_medium_house_2', 0, (20, 30), 2, 'act5', 0,
     "Tess's House",      'Empty until spring. Not empty now.'),
    ('newcomer_mab',   'kaisyn:village/meadow_swiss/houses/meadow_medium_house_3', 0, (-30, 34), 2, 'act5', 0,
     "Mab's House",       'Beds made before they got here.'),
    ('newcomer_corin', 'kaisyn:village/meadow_swiss/houses/meadow_medium_house_4', 0, (50, -24), 2, 'act5', 0,
     "Corin's House",     'The last of the three empty houses.'),
]

# Custom (no template exists in any installed pack) - footprints are declared
# here and the shells are generated block by block further down.
CUSTOM = [
    # name, width, depth, preferred min corner, act, label, blurb
    ('greenhouse', 13, 9, (-27, -10), 'act4', 'The Greenhouse', 'Warm glass in February.'),
    ('bathhouse',   9, 9, (23, 12),   'act4', 'The Bathhouse',  'Waste heat, into the town not the sky.'),
]

MARKET_CARTS = [
    'nova_structures:tavern/tavern_event_trader_car_farmer_spruce',
    'nova_structures:tavern/tavern_event_trader_car_butcher_spruce',
    'nova_structures:tavern/tavern_event_trader_car_fisher_spruce',
    # There is no `_spruce` cartographer car in dungeons-and-taverns 3.0.3.f.
    # The cartographer is the one trade car the mod ships bare, and it is the
    # same 5x4x5 / 100-block piece as the other three. `place template` on a
    # missing id is a silent no-op, so three carts stood on the square and the
    # fourth quarter was an empty patch of paving. Section 11 now asserts that
    # every template id this file emits exists in the installed jars.
    'nova_structures:tavern/tavern_event_trader_car_cartographer',
]
WELL_TOP = 'kaisyn:village/exclusives/classic/town_centers/classic_meeting_point_1/well_top'
WELL_BOTTOM = 'kaisyn:village/exclusives/classic/town_centers/classic_meeting_point_1/well_bottom'
RUIN = 'nova_structures:wild_ruin/wild_ruin_23'
COTTAGE = 'kaisyn:village/meadow_swiss/houses/meadow_small_house_1'

POST = 'minecraft:oak_fence'
LAMP_LIT = 'createdeco:yellow_copper_lamp[facing=up,inverted=true,lit=true]'
LAMP_DARK = 'createdeco:yellow_copper_lamp[facing=up,inverted=false,lit=false]'

# =============================================================================
# 4. Occupancy solver
# =============================================================================
occupied = {}            # (dx,dz) -> owner name
street_cells = set()     # paving, for apron routing


def claim(cells, owner, hard=True):
    for c in cells:
        if hard and c in occupied and occupied[c] != owner:
            raise SystemExit('collision: %s wants %s, held by %s' % (owner, c, occupied[c]))
        occupied[c] = owner


def rect_cells(x0, z0, x1, z1):
    return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)]


def polyline_cells(pts, brush):
    out = set()
    for i in range(len(pts) - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        n = max(abs(bx - ax), abs(bz - az))
        for s in range(n + 1):
            x = int(round(ax + (bx - ax) * s / float(n)))
            z = int(round(az + (bz - az) * s / float(n)))
            for dx in range(-brush, brush + 1):
                for dz in range(-brush, brush + 1):
                    out.add((x + dx, z + dz))
    return out


def seed_occupancy():
    for name, x0, z0, x1, z1 in RESERVED:
        for c in rect_cells(x0, z0, x1, z1):
            occupied[c] = name
    for name, pts in STREETS:
        for c in polyline_cells(pts, ROAD_CLEAR):
            occupied[c] = name
        street_cells.update(polyline_cells(pts, ROAD_BRUSH))
    for c in rect_cells(-PLAZA, -PLAZA, PLAZA, PLAZA):
        street_cells.add(c)
    # every whitelisted lamp post, plus a one-block skirt, must stay open ground
    for route, posts in LAMPS.items():
        for p in posts:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    occupied[(p[0] + dx, p[2] + dz)] = 'lamp_' + route


def _spiral():
    """Offsets from a preferred corner, nearest first. Deterministic."""
    out = [(0, 0)]
    for rad in range(1, 25):
        ring = []
        for dx in range(-rad, rad + 1):
            for dz in range(-rad, rad + 1):
                if max(abs(dx), abs(dz)) == rad:
                    ring.append((dx, dz))
        ring.sort(key=lambda c: (c[0] * c[0] + c[1] * c[1], c))
        out += ring
    return out


SPIRAL = _spiral()


# The x/z shadow of the Works reservation. A pad digs from dy-1 down to
# dy-10, which is below the shell's ceiling at dy-2, so any pad that overlaps
# the shadow overlaps the box - there is no "build above it" for a pad.
# Consulted ONLY for builds that go up at or after Act IV; Act I's marnie_house
# and pip_house sit right over the Works and are perfectly safe there, because
# the shell is dug and sealed long after their pads were cut.
WORKS_SHADOW = set(rect_cells(works_box(WORKS_RESERVE_MARGIN)[0],
                              works_box(WORKS_RESERVE_MARGIN)[2],
                              works_box(WORKS_RESERVE_MARGIN)[3],
                              works_box(WORKS_RESERVE_MARGIN)[5]))


def _fits(x0, z0, fw, fd, margin, extra=None):
    cells = rect_cells(x0 - margin, z0 - margin, x0 + fw - 1 + margin, z0 + fd - 1 + margin)
    if any(c in occupied for c in cells):
        return None
    if extra and any(c in extra for c in cells):
        return None
    return cells


def solve(name, tid, r, want, margin, late=False):
    """Place at the designed corner, or the nearest clear corner to it."""
    fw, fd = footprint(template(tid)['size'], r)
    extra = WORKS_SHADOW if late else None
    for dx, dz in SPIRAL:
        x0, z0 = want[0] + dx, want[1] + dz
        cells = _fits(x0, z0, fw, fd, margin, extra)
        if cells is not None:
            claim(cells, name)
            if (dx, dz) != (0, 0):
                print('  nudged %-16s by %+d,%+d' % (name, dx, dz))
            return Placed(name, tid, r, x0, z0, margin=margin)
    raise SystemExit('no room for ' + name)


def solve_custom(name, fw, fd, want, margin=2, late=False):
    extra = WORKS_SHADOW if late else None
    for dx, dz in SPIRAL:
        x0, z0 = want[0] + dx, want[1] + dz
        cells = _fits(x0, z0, fw, fd, margin, extra)
        if cells is not None:
            claim(cells, name)
            if (dx, dz) != (0, 0):
                print('  nudged %-16s by %+d,%+d' % (name, dx, dz))
            return (x0, z0, x0 + fw - 1, z0 + fd - 1)
    raise SystemExit('no room for ' + name)


# =============================================================================
# 5. Command emitters.  Everything is a `~` offset from the group's origin.
# =============================================================================
def t(v):
    return '~%d' % v


# Every `~a ~b ~c` triple in a command, so a whole group can be lifted onto its pad's own
# level in one pass. `fill` carries two triples and they both move; `tellraw` and `title`
# carry none. This is how terracing stays a five-line change to a 3,000-line generator
# instead of a Y argument threaded through every one of its emitters: a building's pad, its
# template, its furniture, its signs and its NPC stand are all written relative to the
# building's own ground, so they all move together.
_TRIPLE = re.compile(r'~(-?\d+) ~(-?\d+) ~(-?\d+)')


def shift_y(cmds, dy):
    if not dy:
        return list(cmds)
    out = []
    for c in cmds:
        if not c or c.startswith('#'):
            out.append(c)
            continue
        out.append(_TRIPLE.sub(
            lambda m: '~%s ~%d ~%s' % (m.group(1), int(m.group(2)) + dy, m.group(3)), c))
    return out


def fill(x0, y0, z0, x1, y1, z1, block, extra=''):
    return 'fill %s %s %s %s %s %s %s%s' % (t(x0), t(y0), t(z0), t(x1), t(y1), t(z1), block, extra)


def setb(x, y, z, block):
    return 'setblock %s %s %s %s' % (t(x), t(y), t(z), block)


def pad_cmds(x0, z0, x1, z1, height, top='minecraft:grass_block', y=0):
    """A pad, laid in the material the terrain around it is actually made of.

    This used to be four static fills ending in `fill ... minecraft:grass_block`,
    and that is why every plot in the valley was a hard green rectangle stamped
    into snow: a pad in a snowy highland is a lawn with a straight edge, and
    twelve of them read as a minigame lobby rather than a village.

    A `@pad` line is not a command. valley_finales.js runSeg() dispatches any
    line beginning with `@` to a directive handler, which is the only place in
    the pack allowed to LOOK at the world before it writes to it: it samples
    the ring three blocks outside the pad for the surface the generator
    actually laid down, lays the pad's top course in the majority material, and
    then feathers the outermost two rings - a deterministic ~50% scatter one in
    from the edge and ~25% on the edge itself - between that material and the
    ground each of those cells already had. The two feathered rings are inside
    the pad's MARGIN, never under a footprint, so every building still stands
    on a solid, level course.

    Argument order is fixed by the directive parser:
        @pad ~x0 ~0 ~z0 ~x1 ~0 ~z1 <clear height> <dig depth> <fallback top>
    The two tilde triples are what group() reads to compute the group's
    forceload bounds, so they have to stay tilde triples."""
    return ['@pad %s %s %s %s %s %s %d %d %s'
            % (t(x0), t(y), t(z0), t(x1), t(y), t(z1), height, PAD_DEEP, top)]


def marker_cleanup(p):
    """Jigsaw blocks and Towns-and-Towers' cyan_concrete street markers are
    processed away by the mod's own worldgen processors; /place template does
    not run them, so they are cleaned up here.  cyan_concrete becomes the same
    gravel / stone-brick mix street_meadow.json produces."""
    out = [fill(p.x0, p.y0, p.z0, p.x1, p.y1, p.z1, 'minecraft:air',
                ' replace minecraft:jigsaw')]
    for x in range(p.x0, p.x1 + 1, 4):
        out.append(fill(x, p.y0, p.z0, min(x + 1, p.x1), p.y1, p.z1,
                        'minecraft:stone_bricks', ' replace minecraft:cyan_concrete'))
    out.append(fill(p.x0, p.y0, p.z0, p.x1, p.y1, p.z1, 'minecraft:gravel',
                    ' replace minecraft:cyan_concrete'))
    return out


def build_cmds(p, top='minecraft:grass_block'):
    # The LEVELLED rectangle stops ONE COLUMN INSIDE the site's registry box. That last ring
    # -- and the two beyond it -- is the feathered edge: sometimes the terrace, sometimes the
    # hillside, decided per column by edge_holds(). A pad levelled all the way to its own box
    # has a box edge that is a straight line at one height for its whole length, which is
    # exactly what `cut_edge` measures and what the eye reads as a plinth in a field.
    px0, pz0, px1, pz1 = p.pad()
    out = pad_cmds(px0 + 1, pz0 + 1, px1 - 1, pz1 - 1, p.size[1] + 6, top)
    out.append('place template %s %s %s %s %s' % (p.tid, t(p.ox), t(p.oy), t(p.oz), ROTS[p.r]))
    out += marker_cleanup(p)
    # Anything the template wrote as air at ground level goes back to ground,
    # so the pad never reads as a trench around the building. `@padfix` rather
    # than a fill because it has to put back the same material `@pad` chose:
    # the handler caches the sample per pad rectangle, so the two agree.
    out.append('@padfix %s %s %s %s %s %s %s'
               % (t(px0), t(0), t(pz0), t(px1), t(0), t(pz1), top))
    return out


# Every (dx,dz) column that a placed template has a wall standing in. An apron
# routed through one of these would delete the wall: the apron writes air at
# dy1 and paving at dy0, which is exactly a doorway-shaped hole plus a ripped-up
# floor. Filled in by build_cmds() as each building goes down.
WALL_CELLS = set()


def note_walls(p):
    for (lx, ly, lz), b in p.grid.items():
        if ly - p.y_base < 1 or ly - p.y_base > 3:
            continue
        if b[0] in AIRY or b[0] == 'minecraft:jigsaw':
            continue
        a = p.abs((lx, ly, lz))
        WALL_CELLS.add((a[0], a[2]))


# Everything an apron may NOT pave or route through, and the cells it may
# always finish on. Built once, the first time an apron is laid: by then every
# building, every custom shell and every piece of the square's own furniture
# has been solved, which is the whole reason the old L-leg could not see them.
APRON_BLOCK = set()
APRON_PAVED = set()          # every cell the aprons actually pave
_APRON_READY = []


def square_furniture_cells():
    """The square's solved furniture: the well, the four carts, the flower
    boxes, the bench garden, the supper table and the three scene props."""
    out = set()
    out |= set(rect_cells(WELL_X, WELL_Z, WELL_X + 5, WELL_Z + 5))
    for (cx, cz) in CART_POS:
        out |= set(rect_cells(cx, cz, cx + 4, cz + 4))
    for (fx, fz) in FLOWER_POS:
        out.add((fx, fz))
        out.add((fx + 1, fz))
    for b in SQ_BENCH:
        out.add((b[0], b[1]))
    for c in SQ_PLANTER + SQ_POST:
        out.add(c)
    out |= set(rect_cells(SUPPER['x'][0] - 1, SUPPER['z'][0] - 1,
                          SUPPER['x'][1] + 1, SUPPER['z'][1] + 1))
    out |= set(SCENE_CELLS)
    out |= set(rect_cells(-2, -7, 2, -2))          # signpost + noticeboard
    out |= set(rect_cells(-1, -1, 1, 1))           # the Town Square waystone
    return out


def apron_setup():
    if _APRON_READY:
        return
    _APRON_READY.append(True)
    # Every placed template's own wall columns, for ALL buildings, not just the
    # ones emitted so far: an apron laid in Act I must already know where the
    # Act V town hall is going to stand.
    for _p in P.values():
        note_walls(_p)
    for _p in P.values():
        APRON_BLOCK.update(rect_cells(_p.x0, _p.z0, _p.x1, _p.z1))
    for _r in CX.values():
        APRON_BLOCK.update(rect_cells(_r[0], _r[1], _r[2], _r[3]))
    APRON_BLOCK.update(WALL_CELLS)
    APRON_BLOCK.update(square_furniture_cells())
    APRON_BLOCK.update(PIER_CELLS)
    for _route, _posts in LAMPS.items():
        for _q in _posts:
            APRON_BLOCK.add((_q[0], _q[2]))
    # The reservations, except the plaza itself - the plaza IS the destination.
    for _n, _x0, _z0, _x1, _z1 in RESERVED:
        if _n == 'plaza':
            continue
        APRON_BLOCK.update(rect_cells(_x0, _z0, _x1, _z1))


def apron_free(c):
    """Paving already planned is always walkable; everything else has to be
    clear of buildings, furniture, lamp posts and reservations."""
    return c in street_cells or c not in APRON_BLOCK


def apron_route(start):
    """Shortest 4-connected path from `start` to the nearest planned paving.

    A real grid path, not an L. The L took the perpendicular leg first and hoped
    - which works in an empty field and walks through the granary otherwise."""
    if start in street_cells:
        return [start]
    seen = {start: None}
    q = collections.deque([start])
    while q:
        c = q.popleft()
        for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nc = (c[0] + dx, c[1] + dz)
            if nc in seen or max(abs(nc[0]), abs(nc[1])) > 140:
                continue
            if not apron_free(nc):
                continue
            seen[nc] = c
            if nc in street_cells:
                path = [nc]
                while path[-1] != start:
                    path.append(seen[path[-1]])
                path.reverse()
                return path
            q.append(nc)
    return None


def apron_widen(path):
    """A 3-wide corridor: every path cell plus its two neighbours PERPENDICULAR
    to the direction of travel there, so a corner widens both ways. Returns
    (cell, index-of-the-path-cell-it-came-from) so the widened corridor can take the
    ramp's level at that point rather than one level for the whole apron."""
    out = []
    for i, c in enumerate(path):
        steps = set()
        if i + 1 < len(path):
            steps.add((path[i + 1][0] - c[0], path[i + 1][1] - c[1]))
        if i:
            steps.add((c[0] - path[i - 1][0], c[1] - path[i - 1][1]))
        if not steps:
            steps.add((1, 0))
        for (sx, _sz) in sorted(steps):
            px, pz = (0, 1) if sx else (1, 0)
            for k in (-1, 0, 1):
                cc = (c[0] + px * k, c[1] + pz * k)
                if cc not in [q[0] for q in out]:
                    out.append((cc, i))
    return out


def apron_cmds(door, name, lamp=True):
    """A cobbled apron from the door to the nearest paving, plus a lantern.

    Walk OUT of the door - along the direction that actually leaves the
    footprint (Placed.door_out), not the door's swing - to the first cell
    outside the building, then take a breadth-first grid path from there to the
    nearest street or plaza cell, over ground that is not inside a footprint,
    not the square's furniture, not a lamp post and not a reservation. The
    corridor is paved three wide, dug and cleared exactly like a street so it
    is level ground you can walk rather than a slab lying on a hillside.

    Cells INSIDE the footprint - a set-back door's own stoop - are paved at
    dy0 and never cleared above: the building is standing there.
    """
    apron_setup()
    out = []
    b = None
    if door.get('outward'):
        b = (door.get('steps_out') or 1, door['outward'], tuple(door['exit']))
    elif name in P:
        b = P[name].door_out(door)
    else:
        # A custom shell (the bathhouse) whose doorway is cut in its own wall
        # by the group above: the caller knows which way it faces and the cell
        # one step that way is already outside the rectangle.
        _sx, _sz = _STEP[door['facing']]
        b = (1, door['facing'], (door['pos'][0] + _sx, door['pos'][2] + _sz))
    if not b:
        print('  WARNING: %s has no way out of its front door; no apron' % name)
        return out
    steps, dirn, exit_cell = b
    sx, sz = _STEP[dirn]
    stoop, x, z = [], door['pos'][0], door['pos'][2]
    for _i in range(steps):
        x += sx
        z += sz
        stoop.append((x, z))
    inside = set(stoop[:-1])                       # the set-back part, if any
    route = apron_route(exit_cell)
    if route is None:
        print('  WARNING: no apron route from %s door to any paving' % name)
        route = [exit_cell]
    path = stoop[:-1] + route
    # The apron is the RAMP between the building's own level and the street's. Its two ends
    # are pinned -- the doorstep at the pad's level, the last cell at whatever the paving it
    # joins was given -- and ramp() spreads the difference over the run, one block at a
    # time, as evenly as the run allows.
    ay0 = PAD_DY.get(name, 0)
    ay1 = lev(path[-1][0], path[-1][1]) if path else ay0
    prof = ramp(len(path), ay0, ay1)
    if os.environ.get('APRON_DEBUG'):
        print('  APRON %-14s n=%2d from %+d to %+d  last=%s in_level=%s'
              % (name, len(path), ay0, ay1, path[-1] if path else None,
                 (path[-1] in LEVEL) if path else None))
    if prof and abs(prof[-1] - ay1) > 0:
        print('  WARNING: %s apron is %d cells for a %d-block change of level'
              % (name, len(path), ay1 - ay0))
    for (c0, c1) in zip(prof, prof[1:]):
        if abs(c1 - c0) > 1:
            print('  WARNING: %s apron steps %d blocks at once' % (name, c1 - c0))
    cells = apron_widen(path)
    for i, ((cx, cz), pi) in enumerate(cells):
        ay = prof[pi] if prof else 0
        if (cx, cz) in inside:
            # The set-back part of the doorway - the church, the town hall and
            # the tavern all have one. Lay the stoop and NOTHING else: no air
            # clear and no dig, because the building is standing here. The
            # WALL_CELLS guard is deliberately not applied to these cells; it
            # counts any block at dy1..3, which includes the eave over a porch,
            # and skipping the stoop is how the doorway ended up with paving
            # that started three blocks away from it.
            out.append(setb(cx, ay, cz, 'minecraft:cobblestone'))
            APRON_PAVED.add((cx, cz))
            LEVEL.setdefault((cx, cz), ay)
            continue
        if (cx, cz) in street_cells or (cx, cz) in PROTECTED:
            continue
        if (cx, cz) in WALL_CELLS or (cx, cz) in APRON_BLOCK:
            continue
        out.append(fill(cx, ay + 1, cz, cx, ay + 6, cz, 'minecraft:air'))
        out.append(fill(cx, ay - ROAD_DEEP, cz, cx, ay - 1, cz, 'minecraft:dirt'))
        out.append(setb(cx, ay, cz, 'minecraft:cobblestone' if i % 3 else 'minecraft:gravel'))
        APRON_PAVED.add((cx, cz))
        LEVEL.setdefault((cx, cz), ay)
    if lamp:
        # Beside the doorstep and OFF the corridor: a fence post standing in a
        # three-wide path is a three-wide path you cannot walk down the middle
        # of, and section (8) of the harness reads it as unwalkable ground.
        px, pz = (0, 1) if sx else (1, 0)
        for k in (2, -2):
            lx, lz = exit_cell[0] + px * k, exit_cell[1] + pz * k
            if (lx, lz) in WALL_CELLS or (lx, lz) in street_cells:
                continue
            if (lx, lz) in APRON_BLOCK or (lx, lz) in PROTECTED:
                continue
            if (lx, lz) in APRON_PAVED:
                continue
            ly = prof[-1] if prof else 0
            out.append(fill(lx, ly + 1, lz, lx, ly + 4, lz, 'minecraft:air'))
            out.append(setb(lx, ly, lz, 'minecraft:cobblestone'))
            out.append(setb(lx, ly + 1, lz, POST))
            out.append(setb(lx, ly + 2, lz, 'minecraft:lantern[hanging=false]'))
            LEVEL.setdefault((lx, lz), ly)
            break
    return out


def assert_doors_reach_plaza():
    """Every planned front door has a paved route to the plaza. BFS over the
    PAVING ONLY - streets, plaza and aprons - so a door that is one block of
    grass short of the road fails here rather than in the world."""
    paved = set(street_cells) | APRON_PAVED
    seen = {(0, 0)}
    q = collections.deque([(0, 0)])
    while q:
        c = q.popleft()
        for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nc = (c[0] + dx, c[1] + dz)
            if nc in seen or nc not in paved:
                continue
            seen.add(nc)
            q.append(nc)
    bad = []
    for nm, pp in sorted(P.items()):
        ds = pp.doors()
        if not ds:
            continue
        d = ds[0]
        nb = [(d['pos'][0] + a, d['pos'][2] + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if not any(c in seen for c in nb):
            bad.append('%s door %s (outward %s)' % (nm, d['pos'], d['outward']))
    if bad:
        raise SystemExit('doors with no paved route to the plaza: ' + '; '.join(bad))
    print('  aprons: %d paved cells, all %d planned doors reach the plaza over paving'
          % (len(APRON_PAVED), len([n for n in P if P[n].doors()])))


# Cells whose AIR COLUMN is untouchable. A street or a lamp pad may pave the
# ground at dy0 under them, but must never `fill dy1..6 air` there:
#   * a whitelisted lamp post is a post at dy1 and a lamp at dy2,
#   * the Pier waystone stands at lake + [0,1,-2] and the pier deck runs south
#     of it, both inside the High Street's own verge.
# This is what makes act1_streets safe to re-run, which finaleAct2 does after
# the Float levels the lakefront over the bottom of the High Street.
PROTECTED = set()
for _r, _ps in LAMPS.items():
    for _p in _ps:
        PROTECTED.add((_p[0], _p[2]))
PIER_CELLS = set(rect_cells(-1, 32, 1, 43))
PROTECTED |= PIER_CELLS


def street_cmds(pts):
    """A three-block carriageway with a one-block gravel verge either side, laid at the
    level the street was GIVEN in section 6.5 -- its own staircase down the hillside, one
    block of climb per ROAD_RUN blocks of run -- rather than flat at the anchor's Y.
    The verge matters: every whitelisted lamp post sits two blocks off the centre line,
    i.e. ON the verge, and a post needs paved ground under it."""
    out = []
    centre = set(centre_line(pts))
    road = polyline_cells(pts, ROAD_BRUSH)
    verge = polyline_cells(pts, ROAD_BRUSH + 1) - road
    for (x, z) in sorted(road | verge):
        if (x, z) in PIER_CELLS:
            continue
        y = lev(x, z)
        if (x, z) not in PROTECTED:
            out.append(fill(x, y + 1, z, x, y + 6, z, 'minecraft:air'))
        out.append(fill(x, y - ROAD_DEEP, z, x, y - 1, z, 'minecraft:dirt'))
        if (x, z) in verge:
            block = 'minecraft:gravel'
        elif (x, z) in centre:
            block = 'minecraft:cobblestone'
        elif (x + z) % 5 == 0:
            block = 'minecraft:stone_bricks'
        else:
            block = 'minecraft:dirt_path'
        out.append(setb(x, y, z, block))
    return out


def lamp_pad_cmds():
    """A levelled, cleared 3x3 under every whitelisted lamp post that no street
    and not the plaza already paves. Q34 and Q74 ask the player to PLACE these
    posts, and a post needs solid ground with nothing in the cell above it: on
    raw snowy highland the site is powder snow over a hillside.

    This clears the post cells themselves, unlike street_cmds - it runs once,
    inside the Act I finale, immediately before the finale sets the first six
    posts down, and is never re-run."""
    done = set(street_cells)
    out = []
    for route in ('finale', 'q07', 'q34', 'q74'):
        for pst in LAMPS[route]:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    c = (pst[0] + dx, pst[2] + dz)
                    if c in done:
                        continue
                    done.add(c)
                    y = lev(c[0], c[1])
                    out.append(fill(c[0], y + 1, c[1], c[0], y + 5, c[1], 'minecraft:air'))
                    out.append(fill(c[0], y - ROAD_DEEP, c[1], c[0], y - 1, c[1],
                                    'minecraft:dirt'))
                    out.append(setb(c[0], y, c[1], 'minecraft:gravel'))
    return out



# =============================================================================
# 5.5  THE LAND.
#
# Terracing. Until this section existed every pad in the valley was cut at ONE Y --
# `anchor.y` -- over a footprint of 136 x 130 columns, and `docs/research/famous-seeds.md`
# ends with the measurement that kills that idea outright: over the whole 1024x1024 pregen
# of the chosen seed there are 53,478 town-sized boxes lying entirely on land and the
# FLATTEST of them has 22 blocks of relief. There is no patch of 1.20 overworld this size
# that a single-level town fits on. So the town stops pretending: the plaza keeps one level,
# every building pad takes the MEDIAN SURFACE UNDER ITS OWN FOOTPRINT, and the streets,
# aprons and the lantern road ramp between those levels at no more than one block per three
# blocks of run.
#
# Everything here reads the PRISTINE PREGEN -- the world as the generator made it, before
# `/valley build all` writes a single block into it (`scratch/master_build.sh pregen`).
# Read a built world instead and the planner terraces the town onto its own last pads.
#
# The design surface is one field, LEVEL: an anchor-relative dy for every column the plan
# touches. It is filled in four passes, and later passes never overwrite earlier ones:
#
#   1. FLAT      the plaza, and every pad (footprint grown by one). One dy each.
#   2. STREETS   each street's centre line, pinned to the plaza at its plaza end and
#                otherwise following the terrain through a 1-in-3 staircase; the whole
#                cross-section takes its centre column's level.
#   3. APRONS    door level -> street level, same staircase, over the routed path.
#   4. SKIRT     everything else within reach: a multi-source relaxation outwards from the
#                built cells that walks back to the natural surface one block per ring and
#                stops the moment it gets there. This is what feathers a pad into the
#                hillside instead of ending it on a 46-block straight line, and it is what
#                makes `stone_face` pass: no two adjacent columns anywhere in a site's
#                skirt differ by more than one.
# =============================================================================
SKIRT_RINGS = 10                 # how far a pad may reach out to find the natural surface
ROAD_RUN = 3                     # one block of climb per this many blocks of road

SITE = None
_site_arg = None
WORLD_DIR = 'server/world'
for _i, _a in enumerate(sys.argv):
    if _a == '--site' and _i + 1 < len(sys.argv):
        _site_arg = sys.argv[_i + 1]
    if _a == '--world' and _i + 1 < len(sys.argv):
        WORLD_DIR = sys.argv[_i + 1]
if _site_arg:
    SITE = json.load(open(_site_arg))

TERRAIN = SITE is not None
ANCHOR_W = HEARTH_W = SPAWN_W = None

if TERRAIN:
    import numpy as _np
    sys.path.insert(0, 'tools/scripts')
    import seed_hunt as _SH

    HEARTH_W = list(SITE['hearth'])
    ANCHOR_W = list(SITE['anchor'])
    SPAWN_W = list(SITE['spawn'])

    _cx = [HEARTH_W[0], ANCHOR_W[0], SPAWN_W[0]]
    _cz = [HEARTH_W[2], ANCHOR_W[2], SPAWN_W[2]]
    _GX0, _GX1 = min(_cx) - 150, max(_cx) + 150
    _GZ0, _GZ1 = min(_cz) - 150, max(_cz) + 150
    # OCEAN_FLOOR is the top block that is not a fluid -- the LAND. MOTION_BLOCKING counts
    # the fluid too, so the difference is the depth of water standing on that column, which
    # is the only way an offline heightmap read can tell a lake from a lake bed.
    _OF, _, _ = _SH.heights_box(WORLD_DIR, _GX0, _GX1, _GZ0, _GZ1, 'OCEAN_FLOOR')
    _MB, _, _ = _SH.heights_box(WORLD_DIR, _GX0, _GX1, _GZ0, _GZ1, 'MOTION_BLOCKING')

    def surface(x, z):
        """Top non-fluid motion-blocking Y in the PREGEN. None off-grid or ungenerated."""
        ix, iz = x - _GX0, z - _GZ0
        if ix < 0 or iz < 0 or ix >= _OF.shape[0] or iz >= _OF.shape[1]:
            return None
        y = int(_OF[ix, iz])
        return None if y < -900 else y

    def water_depth(x, z):
        ix, iz = x - _GX0, z - _GZ0
        if ix < 0 or iz < 0 or ix >= _OF.shape[0] or iz >= _OF.shape[1]:
            return 0
        a, b = int(_OF[ix, iz]), int(_MB[ix, iz])
        if a < -900 or b < -900:
            return 0
        return max(0, b - a)

    # --- the natural surface MATERIAL, read block by block off the same pregen ----------
    # `@pad` samples this at run time for the pads it lays; the skirt cannot, because a
    # skirt cell is a different height from its neighbour and `@pad` lays one rectangle at
    # one Y. So the skirt reads the block the generator actually put on top of that column
    # and puts the same thing back.
    _MATC = {}
    _VT = None

    def _vt():
        global _VT
        if _VT is None:
            sys.path.insert(0, 'scratch')
            import vt_lib as _v
            _rc = {}

            def _chunk(cx, cz):
                rk = (cx >> 5, cz >> 5)
                if rk not in _rc:
                    q = pathlib.Path(WORLD_DIR) / 'region' / ('r.%d.%d.mca' % rk)
                    _rc[rk] = _SH.read_region(q) if q.exists() else {}
                return _rc[rk].get((cx & 31, cz & 31))
            _v.chunk = _chunk
            _v._sec = {}
            _VT = _v
        return _VT

    SKIRT_TOPS = ('grass_block', 'podzol', 'coarse_dirt', 'moss_block', 'dirt',
                  'rooted_dirt', 'sand', 'red_sand', 'gravel', 'snow_block', 'mycelium',
                  'clay', 'mud', 'stone', 'terracotta')

    def surf_mat(x, z):
        """The block on top of that column in the pregen, or grass_block if unreadable."""
        k = (x, z)
        if k in _MATC:
            return _MATC[k]
        out = 'minecraft:grass_block'
        y = surface(x, z)
        if y is not None:
            try:
                b = _vt().block(x, y, z).split('[')[0]
                if b.split(':')[-1] in SKIRT_TOPS:
                    out = b
            except Exception:                                     # noqa: BLE001
                pass
        _MATC[k] = out
        return out
else:
    def surface(x, z):
        return None

    def water_depth(x, z):
        return 0

    def surf_mat(x, z):
        return 'minecraft:grass_block'


def nat(dx, dz):
    """The natural surface at an anchor-relative column, as a dy. 0 with no world loaded."""
    if not TERRAIN:
        return 0
    y = surface(ANCHOR_W[0] + dx, ANCHOR_W[2] + dz)
    return 0 if y is None else y - ANCHOR_W[1]


def wet(dx, dz):
    return TERRAIN and water_depth(ANCHOR_W[0] + dx, ANCHOR_W[2] + dz) > 0


LEVEL = {}          # (dx,dz) -> dy   the DESIGN surface for every column the plan touches
FLAT_OF = {}        # (dx,dz) -> name of the flat region that owns it
PAD_DY = {}         # site name -> its own level, as a dy


def median_dy(x0, z0, x1, z1):
    """The median natural surface under a footprint, as a dy. Water columns are left out:
    a pad that clips the shore should take the level of the LAND it stands on."""
    if not TERRAIN:
        return 0
    vals = [nat(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)
            if not wet(x, z)]
    if not vals:
        return 0
    vals.sort()
    return int(vals[len(vals) // 2])


def flat(x0, z0, x1, z1, dy, name):
    """Register a rectangle that is levelled to one dy. First writer wins."""
    for c in rect_cells(x0, z0, x1, z1):
        if c not in LEVEL:
            LEVEL[c] = dy
            FLAT_OF[c] = name


def cell_hash(x, z):
    """A stable 0..99 for a column. The same shape as padHash() in valley_finales.js and for
    the same reason: a build that has to be reproducible cannot roll dice."""
    h = (x * 73856093) ^ (z * 19349663)
    h ^= (h >> 13)
    return ((h * 1274126177) & 0x7fffffff) % 100


HOLD_BLOCK = 3                   # how long a run of edge keeps the same width


def hold_depth(x, z):
    """How many rings beyond the levelled rectangle keep the terrace's own level here: 0, 1
    or 2. This is the feathering, and it is the difference between a terrace and a plinth.

    The first version of this dithered PER COLUMN, and it did nothing, because the probe
    (and the eye) reads the ground through a 9x9 morphological opening -- and an opening
    deletes single-column bumps by construction. A one-block hold in a field of steps is
    exactly such a bump. So the hold is COHERENT: it is drawn from a hash of the column's
    HOLD_BLOCK-sized cell, so the terrace's edge holds its width for six columns at a time
    and then moves in or out by up to two. That is a boundary that wanders in PLAN, at a
    scale bigger than the kernel, which is what both the probe and a person actually see."""
    return cell_hash((x // HOLD_BLOCK) * HOLD_BLOCK, (z // HOLD_BLOCK) * HOLD_BLOCK) % 4


def lev(dx, dz):
    """The design surface: the plan's own level where it has one, the land otherwise."""
    c = (dx, dz)
    return LEVEL[c] if c in LEVEL else nat(dx, dz)


def staircase(target, pin0=None):
    """A walkable profile through `target`: at most one block of climb, and at least
    ROAD_RUN flat blocks between two climbs. This is the whole of the road rule, and it is
    one-directional on purpose -- a road is walked, and a staircase that changes its mind
    to meet the terrain behind it is a road with a cliff in it."""
    if not target:
        return []
    out = [target[0] if pin0 is None else pin0]
    last = -(ROAD_RUN + 1)
    for i in range(1, len(target)):
        y = out[-1]
        # ROAD_RUN + 1, not ROAD_RUN: "a block per three blocks of run" is three FLAT
        # columns between two steps, so the step lands on the fourth. Stepping on the third
        # leaves two flat columns and nature_check's road_steps counts them.
        if i - last >= ROAD_RUN + 1 and target[i] != y:
            y += 1 if target[i] > y else -1
            last = i
        out.append(y)
    return out


def ramp(n, y0, y1):
    """n columns from y0 to y1, one block of change at a time, the changes spread as
    evenly over the run as the run allows. A five-cell apron closing three blocks steps on
    cells 2, 3 and 4; a fifteen-cell one steps on 5, 10 and 15. Where the run is shorter
    than the change, every cell steps and the caller is told."""
    if n <= 0:
        return []
    if n == 1:
        return [y1]
    d = y1 - y0
    if d == 0:
        return [y0] * n
    sgn = 1 if d > 0 else -1
    k = min(abs(d), n - 1)
    at = set(int(round((j + 1) * (n - 1) / float(k))) for j in range(k))
    # A ramp whose steps land on consecutive columns is a staircase with no landings. Where
    # the run allows it, push the first step off the first column so the spacing is even.
    if k and (n - 1) // k >= 2 and 0 in at:
        at.discard(0)
        at.add(1)
    out, y = [], y0
    for i in range(n):
        if i in at:
            y += sgn
        out.append(y)
    return out


def centre_line(pts):
    """The ordered centre columns of a polyline, no repeats."""
    out = []
    for i in range(len(pts) - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        n = max(abs(bx - ax), abs(bz - az))
        for st in range(n + 1):
            c = (int(round(ax + (bx - ax) * st / float(n))),
                 int(round(az + (bz - az) * st / float(n))))
            if not out or out[-1] != c:
                out.append(c)
    return out


# =============================================================================
# 6. Solve the town
# =============================================================================
seed_occupancy()
P = {}
META = {}
CX = {}
EARLY = ('inn', 'mill', 'marnie_house', 'pip_house')
for name, tid, r, want, margin, act, ybase, label, blurb in BUILDINGS:
    if name not in EARLY:
        continue
    p = solve(name, tid, r, want, margin)
    p.y_base = ybase
    p.oy = -ybase
    p.y0, p.y1 = -ybase, -ybase + p.size[1] - 1
    P[name] = p
    META[name] = {'act': act, 'label': label, 'blurb': blurb}
for name, fw, fd, want, act, label, blurb in CUSTOM:
    # both customs are Act IV, i.e. they go up after the Works is sealed
    CX[name] = solve_custom(name, fw, fd, want, late=True)
    META[name] = {'act': act, 'label': label, 'blurb': blurb}
for name, tid, r, want, margin, act, ybase, label, blurb in BUILDINGS:
    if name in EARLY:
        continue
    p = solve(name, tid, r, want, margin, late=(act in ('act4', 'act5')))
    p.y_base = ybase
    p.oy = -ybase
    p.y0, p.y1 = -ybase, -ybase + p.size[1] - 1
    P[name] = p
    META[name] = {'act': act, 'label': label, 'blurb': blurb}


# The two custom shells are solid buildings too, so no later apron may route
# through them either.
for _n, _r in CX.items():
    for _c in rect_cells(_r[0], _r[1], _r[2], _r[3]):
        WALL_CELLS.add(_c)


# =============================================================================
# 6.5  The design surface, pass 1 and 2: the pads, then the streets.
#
# The plaza is the datum and keeps one level. Every other pad takes the median natural
# surface under its OWN footprint -- median, not maximum, because the maximum is what cut
# the inn's doorstep to Y 63 with the ground outside it at 74. The streets are then laid as
# staircases: pinned to the plaza where they leave it, following the land everywhere else,
# and never climbing more than a block per ROAD_RUN blocks of run.
# =============================================================================
if TERRAIN:
    _pz = median_dy(-PLAZA, -PLAZA, PLAZA, PLAZA)
    if _pz:
        # site_chosen.json's anchor.y was the median over the whole town box, which is a
        # level the plaza itself is not at. The anchor is a datum, and the datum belongs on
        # the square: move it, and every anchor-relative constant in this file goes on
        # meaning what it says. master_build.sh's `valley anchor set` follows this number.
        ANCHOR_W[1] += _pz
        print('  anchor datum moved to the plaza median: y %d (was %d)'
              % (ANCHOR_W[1], ANCHOR_W[1] - _pz))
    flat(-PLAZA, -PLAZA, PLAZA, PLAZA, 0, 'plaza')

    for _n, _p in sorted(P.items()):
        PAD_DY[_n] = median_dy(_p.x0, _p.z0, _p.x1, _p.z1)
        _p.dy = PAD_DY[_n]
        _pp = _p.pad()
        flat(_pp[0] + 1, _pp[1] + 1, _pp[2] - 1, _pp[3] - 1, PAD_DY[_n], _n)
    for _n, _r in sorted(CX.items()):
        PAD_DY[_n] = median_dy(_r[0], _r[1], _r[2], _r[3])
        flat(_r[0] - 1, _r[1] - 1, _r[2] + 1, _r[3] + 1, PAD_DY[_n], _n)

    # The cottage yard, sixty blocks up the lantern road. It is home-relative in the
    # mcfunction and anchor-relative here, because there is only one design surface.
    COT_OX = HEARTH_W[0] - ANCHOR_W[0]
    COT_OZ = HEARTH_W[2] - ANCHOR_W[2]
    COT_DY = HEARTH_W[1] - ANCHOR_W[1]
    COT_FLAT = (-10, -13, 10, 10)        # home-relative; the registry box is one ring wider
    flat(COT_OX + COT_FLAT[0], COT_OZ + COT_FLAT[1],
         COT_OX + COT_FLAT[2], COT_OZ + COT_FLAT[3], COT_DY, 'cottage_plot')

    # ---- no terrace may be further from its neighbour than the ground between them can
    # ---- climb. Measured on the built world before this existed: the town hall's pad at
    # ---- Y 63 and the greenhouse's at Y 69 with FOUR free columns between them, i.e. a
    # ---- six-block wall of cut dirt down the side of the greenhouse. A pad taking the
    # ---- median under its own footprint is right; two of them ignoring each other is not.
    _rects = {}
    for _n, _p in P.items():
        _pp = _p.pad()
        _rects[_n] = (_pp[0] + 1, _pp[1] + 1, _pp[2] - 1, _pp[3] - 1)
    for _n, _r in CX.items():
        _rects[_n] = (_r[0] - 1, _r[1] - 1, _r[2] + 1, _r[3] + 1)

    def _sep(a, b):
        dx = max(a[0] - b[2] - 1, b[0] - a[2] - 1, 0)
        dz = max(a[1] - b[3] - 1, b[1] - a[3] - 1, 0)
        return max(dx, dz)

    _names = sorted(_rects)
    _pairs = [(a, b, _sep(_rects[a], _rects[b])) for i, a in enumerate(_names)
              for b in _names[i + 1:] if _sep(_rects[a], _rects[b]) <= 10]
    for _it in range(40):
        _moved = 0
        for _a, _b, _g in _pairs:
            _lim = max(1, _g)
            _d = PAD_DY[_a] - PAD_DY[_b]
            if abs(_d) <= _lim:
                continue
            _ex = abs(_d) - _lim
            _s = 1 if _d > 0 else -1
            PAD_DY[_a] -= _s * ((_ex + 1) // 2)
            PAD_DY[_b] += _s * (_ex // 2)
            _moved += 1
        if not _moved:
            break
    for _n, _p in P.items():
        _p.dy = PAD_DY[_n]
    # re-stamp the flats at the settled levels
    for _c in list(LEVEL):
        if FLAT_OF.get(_c) in PAD_DY:
            LEVEL[_c] = PAD_DY[FLAT_OF[_c]]
    _worst = max(((_g, _a, _b, abs(PAD_DY[_a] - PAD_DY[_b])) for _a, _b, _g in _pairs),
                 key=lambda q: q[3] - max(1, q[0]), default=None)
    if _worst:
        print('  closest terraces: %s/%s %d columns apart, %d blocks of level between them'
              % (_worst[1], _worst[2], _worst[0], _worst[3]))

    def _pin_start(c):
        """The level a street LEAVES FROM: the nearest column that already has one.

        Every street in STREETS is written plaza-end first, and most of them start one or
        two columns OUTSIDE the plaza rectangle -- high_street at (0,13), mill_lane at
        (-13,3), east_lane at (13,-12). Reading lev() there returns the raw hillside, and
        the raw hillside at the square's kerb is Y 77 against a plaza at 69. Mill Lane was
        therefore laid as a cobbled embankment eight blocks in the air, walking out of the
        square over a wall, and the mill's apron then ramped 45 columns up to meet it."""
        for r in range(0, 4):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) != r:
                        continue
                    q = (c[0] + dx, c[1] + dz)
                    if q in LEVEL:
                        return LEVEL[q]
        return None

    for _sn, _spts in STREETS:
        _cl = centre_line(_spts)
        _tg = [lev(c[0], c[1]) for c in _cl]
        _p0 = _pin_start(_cl[0])
        _sy = staircase(_tg, _tg[0] if _p0 is None else _p0)
        for _i, _c in enumerate(_cl):
            for _ddx in range(-(ROAD_BRUSH + 1), ROAD_BRUSH + 2):
                for _ddz in range(-(ROAD_BRUSH + 1), ROAD_BRUSH + 2):
                    LEVEL.setdefault((_c[0] + _ddx, _c[1] + _ddz), _sy[_i])
    # The Works is a sealed room in undisturbed rock, and "six blocks under the anchor" is
    # only under the ground while the anchor happens to BE the ground. Moving the datum onto
    # the plaza lifted the ceiling to within nothing of the meadow over it (measured: -3 to
    # 0 blocks of cover, i.e. the roof of the bunker sticking out of a field). So the depth
    # is measured rather than assumed: drop the mark until the thinnest cover anywhere over
    # the ceiling is WORKS_COVER blocks, which also puts it below anything a street digs.
    _wb0 = works_box(0)
    _wfloor = min(nat(x, z) for x in range(_wb0[0], _wb0[3] + 1)
                  for z in range(_wb0[2], _wb0[5] + 1))
    WORKS_OFF[1] = _wfloor - WORKS_COVER - WORKS_SHELL['y'][1]
    print('  works mark dropped to dy %d: ceiling %+d, %d blocks of cover under the '
          'thinnest ground over it (%+d)'
          % (WORKS_OFF[1], WORKS_OFF[1] + WORKS_SHELL['y'][1], WORKS_COVER, _wfloor))

    print('  levels: plaza 0, pads %+d..%+d, cottage yard %+d'
          % (min(PAD_DY.values()), max(PAD_DY.values()), COT_DY))
    for _n in sorted(PAD_DY):
        print('    %-16s %+d' % (_n, PAD_DY[_n]))

# --- the square's own furniture, solved against the streets ----------------
# The four corners this used to hard-code put a market cart under the Lake
# Road's verge, and the street clear (dy1..6 air) took the cart with it. The
# square is a busy place: the well, four carts, eight flower boxes, the supper
# table, the noticeboard, the signpost, the waystone and the road out of the
# south side all have to fit around each other, so they are solved here.
SUPPER = {'x': (-4, 4), 'z': (-11, -9)}
_sq_blocked = set()
for _n, _pts in STREETS:
    _sq_blocked |= polyline_cells(_pts, ROAD_BRUSH + 1)
_sq_blocked |= set(rect_cells(SUPPER['x'][0] - 1, SUPPER['z'][0] - 1,
                              SUPPER['x'][1] + 1, SUPPER['z'][1] + 1))
_sq_blocked |= set(rect_cells(-2, 1, 2, PLAZA))        # the road out of the square
_sq_blocked |= set(rect_cells(-2, -7, 2, -2))          # signpost + noticeboard
_sq_blocked |= set(rect_cells(-1, -1, 1, 1))           # the Town Square waystone
# --- the bench garden: the second cluster, round the waystone ---------------
# The middle of the square was bare paving. The waystone stood on it alone,
# the well and the four carts were solved out to the kerb, and between the
# signpost and the road there was nothing for the eye to land on. This is the
# town's own furniture, at Chebyshev radius 3: two benched wings facing in, a
# flower box between each pair of benches, a lantern post on each of the four
# ends. It is laid out before anything else is solved, so the well, the carts,
# the flower boxes, the plaza stands and the supper seats all route round it;
# and radius 3 clears the waystone cell, the four corner lamp posts at +-12,
# the noticeboard/signpost strip (x -2..2, z -7..-2) and the road out of the
# south side (x -2..2, z 1..12) by construction.
SQ_BENCH, SQ_PLANTER, SQ_POST = [], [], []
for _sx, _face in ((-3, 'east'), (3, 'west')):
    for _bz in (-2, 0, 2):
        SQ_BENCH.append((_sx, _bz, _face))
    for _bz in (-1, 1):
        SQ_PLANTER.append((_sx, _bz))
    for _bz in (-3, 3):
        SQ_POST.append((_sx, _bz))
for _c in [(b[0], b[1]) for b in SQ_BENCH] + SQ_PLANTER + SQ_POST:
    _sq_blocked.add(_c)
for _r, _ps in LAMPS.items():
    for _p in _ps:
        for _dx in (-1, 0, 1):
            for _dz in (-1, 0, 1):
                _sq_blocked.add((_p[0] + _dx, _p[2] + _dz))
PLAZA_CELLS = set(rect_cells(-PLAZA, -PLAZA, PLAZA, PLAZA))


def sq_fit(w, d, want):
    """Nearest w x d patch to `want` that is inside the plaza and free."""
    for dx, dz in SPIRAL:
        x0, z0 = want[0] + dx, want[1] + dz
        cells = rect_cells(x0, z0, x0 + w - 1, z0 + d - 1)
        if all(c in PLAZA_CELLS and c not in _sq_blocked for c in cells):
            _sq_blocked.update(cells)
            return (x0, z0)
    for _z in range(-PLAZA, PLAZA + 1):
        print('%4d %s' % (_z, ''.join('.' if (_x, _z) in _sq_blocked else '#'
                                      for _x in range(-PLAZA, PLAZA + 1))))
    raise SystemExit('no room on the square for a %dx%d near %s' % (w, d, str(want)))


if os.environ.get('PLAN_DEBUG_SQUARE'):
    for _z in range(-PLAZA, PLAZA + 1):
        print('%4d %s' % (_z, ''.join('.' if (_x, _z) in _sq_blocked else '#'
                                      for _x in range(-PLAZA, PLAZA + 1))))
# The well and the four carts used to be wanted at the kerb - one cart's
# preferred corner was (-10,-10), i.e. two blocks off the plaza's own edge -
# so the square read as a ring of furniture round an empty middle. Every want
# below is pulled in towards the waystone; sq_fit still spirals out from it,
# so a want that lands on a street verge or the bench garden simply steps to
# the nearest free patch instead of failing.
WELL_X, WELL_Z = sq_fit(6, 6, (-10, -6))        # well_top min corner (6x6)
CART_POS = [sq_fit(5, 5, c) for c in ((4, -4), (8, -9), (-10, 3), (6, 3))]
FLOWER_POS = [sq_fit(2, 1, c) for c in
              ((-6, 0), (5, 1), (-6, 2), (9, -3), (-4, -7), (3, -7), (-5, 5), (4, 2))]

# --- the three scenes that stand on the square, solved like everything else --
# valley_finales.js used to hand-type these. Q59's Ribbit camp went in at
# anchor x -10..-8, z 4..6, Q62's still at x -9..-7, z 6..7, and finaleAct3's
# hay and pumpkins at the four (+-6, +-6) corners - all of them written when
# the well and the carts were out at the kerb. Pulling the furniture inward
# moved a market cart onto x -10..-6, z 3..7, and the scenes did not move with
# it: four Ribbits ended up standing in the fisher's cart, Sedge inside its
# oak fence with a lit lantern in his head, and a lit campfire under its wooden
# canopy. They are solved against every occupant of the square here instead,
# exported in the plan, and read back by the scenes at run time - so the next
# person who nudges a cart cannot put a camp fire under it.
RIBBIT_CAMP_MIN = sq_fit(5, 3, (-11, 4))
RIBBIT_STANDS = [[RIBBIT_CAMP_MIN[0] + 1, 1, RIBBIT_CAMP_MIN[1]],
                 [RIBBIT_CAMP_MIN[0] + 1, 1, RIBBIT_CAMP_MIN[1] + 2],
                 [RIBBIT_CAMP_MIN[0] + 3, 1, RIBBIT_CAMP_MIN[1]],
                 [RIBBIT_CAMP_MIN[0] + 3, 1, RIBBIT_CAMP_MIN[1] + 2]]
RIBBIT_FIRE = [RIBBIT_CAMP_MIN[0] + 2, 1, RIBBIT_CAMP_MIN[1] + 1]
RIBBIT_POST = [RIBBIT_CAMP_MIN[0], 1, RIBBIT_CAMP_MIN[1] + 1]
STILL_MIN = sq_fit(3, 2, (-9, 8))
STILL = {'cupboard': [STILL_MIN[0], 1, STILL_MIN[1] + 1],
         'brewing_stand': [STILL_MIN[0] + 1, 1, STILL_MIN[1] + 1],
         'cauldron': [STILL_MIN[0] + 2, 1, STILL_MIN[1] + 1],
         'post': [STILL_MIN[0] + 1, 1, STILL_MIN[1]]}
HARVEST_HAY = [[c[0], 1, c[1]] for c in (sq_fit(1, 1, (-6, -6)), sq_fit(1, 1, (6, -6)))]
HARVEST_PUMPKIN = [[c[0], 1, c[1]] for c in (sq_fit(1, 1, (-6, 6)), sq_fit(1, 1, (6, 6)))]
SCENE_CELLS = ([(c[0], c[2]) for c in RIBBIT_STANDS] +
               [(RIBBIT_FIRE[0], RIBBIT_FIRE[2]), (RIBBIT_POST[0], RIBBIT_POST[2])] +
               [(c[0], c[2]) for c in STILL.values()] +
               [(c[0], c[2]) for c in HARVEST_HAY + HARVEST_PUMPKIN])

# --- where a resident can stand on the square without being inside the well,
#     a market cart, the supper table, the road or the noticeboard ------------
_blocked = set(_sq_blocked)
_cand = [c for c in rect_cells(-8, -8, 8, 8)
         if c not in _blocked and 3 <= max(abs(c[0]), abs(c[1])) <= 8]
_cand.sort(key=lambda c: (math.atan2(c[1], c[0]), max(abs(c[0]), abs(c[1]))))
_step = max(1, len(_cand) // 24)
PLAZA_STANDS = [[x, 1, z] for (x, z) in _cand[::_step]][:24]

# --- the seats at the Harvest Supper ----------------------------------------
# This used to be `[[x,1,z] for z in (-12,-8) for x in range(-4,5,2)]`. Ten
# cells, and two things wrong with them: [0,1,-12] IS the north corner lamp
# post (LAMPS.finale[2]), so whoever got seat 2 was standing inside a fence
# and a lit lamp; and finaleAct3 seats ELEVEN - seat(v,10) is Wisp - so the
# eleventh index wrapped round to 0 and sat her on top of Pip.
#
# Twelve distinct cells are solved here instead, out of the two rows behind
# the benches (z -12 and z -8) and, if a row runs out, the rows behind those,
# alternating sides and working outwards from the middle of the table so the
# party fills the seats nearest the food first. Every lamp post, cart, flower
# box, well cell, bench-garden cell, street verge and the table's own
# furniture is excluded.
_seat_blocked = set()
for _n, _pts in STREETS:
    _seat_blocked |= polyline_cells(_pts, ROAD_BRUSH + 1)
for _r, _ps in LAMPS.items():
    for _p in _ps:
        _seat_blocked.add((_p[0], _p[2]))
_seat_blocked |= set(rect_cells(WELL_X, WELL_Z, WELL_X + 5, WELL_Z + 5))
for (_cx, _cz) in CART_POS:
    _seat_blocked |= set(rect_cells(_cx, _cz, _cx + 4, _cz + 4))
for (_fx, _fz) in FLOWER_POS:
    _seat_blocked.add((_fx, _fz)); _seat_blocked.add((_fx + 1, _fz))
for _c in [(b[0], b[1]) for b in SQ_BENCH] + SQ_PLANTER + SQ_POST:
    _seat_blocked.add(_c)
_seat_blocked |= set(rect_cells(-4, -11, 4, -9))        # tables and both chair rows
_seat_blocked.add((-6, -10)); _seat_blocked.add((6, -10))   # the table's lantern posts
_seat_blocked |= set(rect_cells(-2, 1, 2, PLAZA))       # the road out of the square
_seat_blocked |= set(rect_cells(-2, -7, 2, -2))         # signpost + noticeboard
_seat_blocked |= set(rect_cells(-1, -1, 1, 1))          # the waystone
_seat_blocked |= set(SCENE_CELLS)                      # camp, still, hay and pumpkins

_seat_x = [0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6, -7, 7]
_seat_cand = []
for _rows in ((-12, -8), (-13, -7)):
    for _sx in _seat_x:
        for _sz in _rows:
            _seat_cand.append((_sx, _sz))
SUPPER_SEATS = []
for _c in _seat_cand:
    if len(SUPPER_SEATS) >= 12:
        break
    if _c in _seat_blocked:
        continue
    if max(abs(_c[0]), abs(_c[1])) > PLAZA:
        continue
    _seat_blocked.add(_c)
    SUPPER_SEATS.append([_c[0], 1, _c[1]])
if len(SUPPER_SEATS) < 12:
    raise SystemExit('only %d supper seats solved; the table has eleven sitters'
                     % len(SUPPER_SEATS))

# =============================================================================
# 7. Derived marks
# =============================================================================
inn = P['inn']
# The Hearth: the tavern's own campfire.
hearth = None
for lp, b in sorted(inn.grid.items()):
    if b[0] == 'minecraft:campfire':
        hearth = inn.abs(lp)
        break
if hearth is None:
    raise SystemExit('tavern has no campfire to use as the Hearth')

mill = P['mill']
gran = P['granary']
gh = CX['greenhouse']
bh = CX['bathhouse']

# Every mark a finale measures from stands on the terrace of the thing it names: `v.mark('inn')`
# is the inn's hearthstone, and the inn is two blocks below the square now. A mark left at the
# anchor's level is a scene played two blocks in the air, or two blocks inside a floor.
def _mk(pos, site):
    return [pos[0], pos[1] + PAD_DY.get(site, 0), pos[2]]


OFF = {
    'square':     [0, 1, 0],
    'board':      [0, 1, -5],
    'inn':        _mk(list(hearth), 'inn'),
    'mill':       _mk([mill.x1 + 3, 0, mill.z0 + (mill.fd // 2)], 'mill'),
    'granary':    _mk([gran.x0, 1, gran.z0], 'granary'),
    'lake':       [0, lev(0, 34) + 1, 34],
    'works':      list(WORKS_OFF),
    'greenhouse': _mk([gh[0] + (gh[2] - gh[0]) // 2, 1, gh[1] + (gh[3] - gh[1]) // 2],
                      'greenhouse'),
    'bathhouse':  _mk([bh[0] + (bh[2] - bh[0]) // 2, 1, bh[1] + (bh[3] - bh[1]) // 2],
                      'bathhouse'),
    'echo_cave':  [34, WORKS_OFF[1] - 24, -20],
}

# =============================================================================
# 8. Interior analysis - every NPC stand, chalk mark and bed below is read off
#    the template's own blocks, never guessed.
# =============================================================================
AIRY = ('minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void')


def _air(g, p):
    b = g.get(p)
    return b is None or b[0] in AIRY


def _solid(g, p):
    b = g.get(p)
    if b is None:
        return False
    n = b[0]
    if n in AIRY or n == 'minecraft:jigsaw':
        return False
    return not any(k in n for k in ('_door', 'carpet', 'torch', 'lantern', 'sign', 'flower',
                                    'grass', 'bush', 'sapling', 'water', 'candle', 'pot',
                                    'fence', '_wall', 'pane', '_bars', 'chain', 'ladder',
                                    'lever', 'button', 'vine', 'leaves', 'snow', 'rail'))


def indoor_stands(p, grid=None, size=None, roofed=True):
    """Anchor-relative positions where a person can stand inside the building."""
    g = grid if grid is not None else p.grid
    sz = size if size is not None else p.size
    out = []
    for (x, y, z), b in g.items():
        if not _solid(g, (x, y, z)):
            continue
        if not (_air(g, (x, y + 1, z)) and _air(g, (x, y + 2, z))):
            continue
        if roofed and not any(_solid(g, (x, yy, z)) for yy in range(y + 3, min(y + 9, sz[1]))):
            continue
        out.append((x, y + 1, z))
    out.sort()
    if p is None:
        return out
    return [p.abs(o) for o in out]


def wall_run(p, length=3):
    """A run of `length` interior floor tiles with a solid wall behind them.
    Returns (tiles, signs, facing) in anchor-relative coordinates."""
    g = p.grid
    sz = p.size
    stands = set()
    for (x, y, z), b in g.items():
        if not (_solid(g, (x, y, z)) and _air(g, (x, y + 1, z)) and _air(g, (x, y + 2, z))):
            continue
        # indoors only: a chalked spot on the kitchen wall is not the garden fence
        if not any(_solid(g, (x, yy, z)) for yy in range(y + 3, min(y + 9, sz[1]))):
            continue
        stands.add((x, y, z))
    for axis in (0, 1):
        for back in (-1, 1):
            for (x, y, z) in sorted(s for s in stands if s[1] <= 2):
                run = []
                for i in range(length):
                    c = (x + (i if axis == 0 else 0), y, z + (0 if axis == 0 else i))
                    w = (c[0] + (0 if axis == 0 else back), y + 1, c[2] + (back if axis == 0 else 0))
                    if c in stands and _solid(g, w) and _air(g, (c[0], y + 1, c[2])):
                        run.append(c)
                    else:
                        break
                if len(run) == length:
                    d = ('south' if back == 1 else 'north') if axis == 0 else \
                        ('east' if back == 1 else 'west')
                    # the sign hangs in the open cell, facing away from the wall
                    # d and face are LOCAL directions; the sign is placed in the
                    # world, so both have to come through the same rotation the
                    # template did.
                    face = {'south': 'north', 'north': 'south', 'east': 'west', 'west': 'east'}[d]
                    face = rot_dir(face, p.r)
                    tiles = [p.abs(c) for c in run]
                    signs = [p.abs((c[0], c[1] + 1, c[2])) for c in run]
                    return tiles, signs, face
    raise SystemExit('no wall run found in ' + p.name)


# =============================================================================
# 9. Groups
# =============================================================================
GROUPS = collections.OrderedDict()
PROBES = []


TIL3 = re.compile(r'(?:^|\s)~(-?\d+)\s+~(-?\d+)\s+~(-?\d+)(?=\s|$)')


def group(key, origin, cmds):
    # The bounding box of every `~` triple in the group.  runGroup() in
    # valley_finales.js forceloads exactly this, because a finale runs as the
    # server from 0 0 0 and a fill into an unloaded chunk is silently refused.
    xs, zs = [], []
    for c in cmds:
        for m in TIL3.finditer(c):
            xs.append(int(m.group(1))); zs.append(int(m.group(3)))
    b = [min(xs), min(zs), max(xs), max(zs)] if xs else [0, 0, 0, 0]
    GROUPS[key] = {'origin': origin, 'cmds': cmds, 'bounds': b}


def probe(label, pos, block, origin='anchor', dy=0):
    """A block that must exist once the build has run. `dy` lifts the probe onto the same
    terrace as the thing it is checking -- a probe left at the anchor's level after the pad
    under it moved is a probe that reads a hillside."""
    PROBES.append({'label': label, 'pos': [pos[0], pos[1] + dy, pos[2]],
                   'block': block, 'origin': origin})


def npc(name, pos):
    return 'easy_npc preset import data valley:easy_npc/preset/%s.npc.snbt %s %s %s' % (
        name, t(pos[0]), t(pos[1]), t(pos[2]))


def arrival(label, blurb, sound='minecraft:ui.toast.challenge_complete'):
    return [
        'title @a times 10 60 20',
        'title @a subtitle ' + json.dumps({'text': blurb, 'color': 'gray', 'italic': True}),
        'title @a title ' + json.dumps({'text': label, 'color': 'gold'}),
        'playsound %s master @a ~0 ~1 ~0 1 1' % sound,
    ]


def building_group(key, name, dressing=None, npc_at=None, top='minecraft:grass_block'):
    """The pad, the template and everything standing on it, lifted onto the building's own
    level -- and the apron, which is NOT lifted, because the apron is the ramp between that
    level and the road's."""
    p = P[name]
    note_walls(p)
    dy = PAD_DY.get(name, 0)
    body = build_cmds(p, top)
    if dressing:
        body += dressing
    if npc_at:
        body += npc_at
    cmds = shift_y(body, dy)
    for d in p.doors()[:1]:
        cmds += apron_cmds(d, name)
    cmds += arrival(META[name]['label'], META[name]['blurb'])
    group(key, 'anchor', cmds)
    for pr in p.probes():
        pr['pos'][1] += dy
        PROBES.append(pr)
    return p


# --- Act I -------------------------------------------------------------------
inn_tiles, inn_signs, inn_face = wall_run(inn, 3)
inn_stands = indoor_stands(inn)
inn_hall = [s for s in inn_stands if abs(s[1] - 1) <= 1]

dress_inn = []
for i, (tile, sg) in enumerate(zip(inn_tiles, inn_signs)):
    dress_inn.append(setb(tile[0], tile[1], tile[2], 'minecraft:polished_andesite'))
    label = ['COUNTER', 'SINK', 'OVEN'][i]
    dress_inn.append(
        'setblock %s %s %s minecraft:oak_wall_sign[facing=%s]{front_text:{messages:['
        '\'{"text":"%d"}\',\'{"text":"%s"}\',\'{"text":""}\',\'{"text":"- M."}\'],color:"gray"}}'
        % (t(sg[0]), t(sg[1]), t(sg[2]), inn_face, i + 1, label))
CRATE = ('minecraft:barrel[facing=up]{Items:[{Slot:0b,id:"minecraft:wheat",Count:24b},'
         '{Slot:1b,id:"minecraft:pumpkin",Count:4b},{Slot:2b,id:"minecraft:sugar",Count:4b},'
         '{Slot:3b,id:"minecraft:egg",Count:4b},{Slot:4b,id:"minecraft:carrot",Count:4b},'
         '{Slot:5b,id:"minecraft:potato",Count:4b},{Slot:6b,id:"farmersdelight:cabbage",Count:4b},'
         '{Slot:7b,id:"minecraft:bowl",Count:4b},{Slot:8b,id:"minecraft:charcoal",Count:16b}]}')
crate_spot = [s for s in inn_hall if s not in inn_tiles][0]
dress_inn.append(setb(crate_spot[0], crate_spot[1], crate_spot[2], CRATE))
dress_inn.append(setb(hearth[0], hearth[1], hearth[2], 'minecraft:campfire[lit=true]'))
innd = inn.doors()[0]
# A standing sign on its own post beside the door: a wall sign hung off a door
# has no support and pops the first time a neighbour updates.
_isx, _isz = _STEP[innd['facing']]
_ipx, _ipz = innd['pos'][0] + _isx * 2 + (2 if _isz else 0), innd['pos'][2] + _isz * 2 + (2 if _isx else 0)
dress_inn += [
    setb(_ipx, innd['pos'][1] - 1, _ipz, 'minecraft:cobblestone'),
    setb(_ipx, innd['pos'][1], _ipz, POST),
    'setblock %s %s %s minecraft:oak_sign[rotation=%d]{front_text:{messages:['
    '\'{"text":"THE INN"}\',\'{"text":""}\',\'{"text":"kept by"}\',\'{"text":"M. Ashcombe"}\'],'
    'color:"gray"}}' % (t(_ipx), t(innd['pos'][1] + 1), t(_ipz),
                        {'north': 8, 'south': 0, 'east': 12, 'west': 4}[innd['facing']]),
]
building_group('act1_inn', 'inn', dressing=dress_inn)
probe('inn_hearth', hearth, 'minecraft:campfire', dy=PAD_DY.get('inn', 0))
probe('inn_chalk_1', inn_tiles[0], 'minecraft:polished_andesite', dy=PAD_DY.get('inn', 0))

# --- the mill ----------------------------------------------------------------
mill_yard = OFF['mill']
# The yard and the race sit NORTH of Mill Lane. The lane's last leg runs along
# anchor z 5..7 at x -25..-23, so anything the mill scene puts down at z >= 5
# there is inside the street the Act I finale cuts eleven quests later - which
# is exactly what happened to the race the first time: `fill x 1..6 z air`
# emptied the channel and the paving took the water with it.
race = [mill_yard[0] - 1, 0, mill_yard[2] - 6]
_yx0, _yz0 = mill_yard[0] - 2, mill_yard[2] - 7
_yx1, _yz1 = mill_yard[0] + 6, mill_yard[2] - 3
dress_mill = [
    fill(_yx0, 1, _yz0, _yx1, 8, _yz1, 'minecraft:air'),
    fill(_yx0, -6, _yz0, _yx1, -1, _yz1, 'minecraft:dirt'),
    fill(_yx0, 0, _yz0, _yx1, 0, _yz1, 'minecraft:cobblestone'),
    # the race Q16 sets two Water Wheels in
    'place template valley:mill_race %s %s %s' % (t(race[0]), t(race[1]), t(race[2])),
    # The template is an open-ended trough. Capped at both ends AND walled down
    # both long sides: the yard around it is open ground now, so an unwalled
    # channel simply empties itself across the mill plot and down Mill Lane.
    fill(race[0] - 1, 1, race[2], race[0] + 7, 1, race[2], 'minecraft:stone_bricks'),
    fill(race[0] - 1, 1, race[2] + 2, race[0] + 7, 1, race[2] + 2, 'minecraft:stone_bricks'),
    setb(race[0] - 1, 1, race[2] + 1, 'minecraft:stone_bricks'),
    setb(race[0] + 7, 1, race[2] + 1, 'minecraft:stone_bricks'),
    fill(race[0] - 1, 1, race[2] - 1, race[0] + 7, 5, race[2] + 3, 'minecraft:air',
         ' replace minecraft:water'),
    fill(race[0], 1, race[2] + 1, race[0] + 6, 1, race[2] + 1, 'minecraft:water[level=0]'),
    # the snapped axle, on the stones where it fell
    setb(mill_yard[0] + 1, 1, mill_yard[2] - 7, 'minecraft:stripped_oak_log[axis=x]'),
    setb(mill_yard[0] + 2, 1, mill_yard[2] - 7, 'minecraft:stripped_oak_log[axis=x]'),
    setb(mill_yard[0] + 3, 1, mill_yard[2] - 7, 'minecraft:oak_log[axis=x]'),
    setb(mill_yard[0] + 4, 1, mill_yard[2] - 7, 'minecraft:stripped_oak_log[axis=z]'),
    # Bram's labelled crates
    setb(mill_yard[0] + 5, 1, mill_yard[2] - 7, 'minecraft:barrel[facing=up]'),
    setb(mill_yard[0] + 5, 1, mill_yard[2] - 4, 'handcrafted:oak_table'),
    setb(mill_yard[0] + 6, 1, mill_yard[2] - 4, 'minecraft:crafting_table'),
    setb(mill_yard[0] + 6, 1, mill_yard[2] - 3, POST),
    setb(mill_yard[0] + 6, 2, mill_yard[2] - 3,
         'minecraft:oak_sign[rotation=12]{front_text:{messages:[\'{"text":"THE MILL"}\','
         '\'{"text":""}\',\'{"text":"B. Tolliver"}\',\'{"text":"millwright"}\'],color:"gray"}}'),
    npc('bram', [mill_yard[0] + 2, 1, mill_yard[2] - 3]),
]
MILL_YARD = (_yx0, _yz0, _yx1, _yz1)
building_group('act1_mill', 'mill', dressing=dress_mill)
probe('mill_race_water', [race[0] + 3, 1, race[2] + 1], 'minecraft:water',
      dy=PAD_DY.get('mill', 0))

# --- Marnie and Pip ----------------------------------------------------------
def resident_house(key, name, who, lines, extra=None):
    p = P[name]
    d = p.doors()[0]
    sx, sz = _STEP[d['facing']]
    stand = [d['pos'][0] + sx * 2, d['pos'][1], d['pos'][2] + sz * 2]
    dress = [
        setb(stand[0] + (1 if sz else 0), stand[1] - 1, stand[2] + (1 if sx else 0),
             'handcrafted:oak_table'),
        setb(stand[0] - (1 if sz else 0), stand[1] - 1, stand[2] - (1 if sx else 0),
             'minecraft:barrel[facing=up]'),
    ]
    if extra:
        dress += extra
    dress.append(npc(who, stand))
    dress.append('tellraw @a[distance=..96] ' + json.dumps(
        [{'text': lines[0] + ': ', 'color': lines[2]},
         {'text': lines[1], 'color': 'white', 'italic': True}]))
    building_group(key, name, dressing=dress)
    return stand


marnie_stand = resident_house(
    'act1_marnie', 'marnie_house', 'marnie',
    ['Marnie', '"Four years I\'ve looked at that chimney, and last night there was smoke. '
     'I\'ve brought bread and I am not carrying it home."', 'gold'])
pip_stand = resident_house(
    'act1_pip', 'pip_house', 'pip',
    ['Pip', '"Is that an egg? Aunt Marnie says I get a duck if I\'m useful, so I am being '
     'extremely useful."', 'red'],
    extra=None)
GROUPS['act1_pip']['cmds'].insert(
    -4, 'summon duckling:duck %s %s %s {PersistenceRequired:1b,NoAI:1b}'
        % (t(pip_stand[0]), t(pip_stand[1]), t(pip_stand[2] + 1)))

# --- the Town Square ---------------------------------------------------------
sq = []
sq += [
    fill(-PLAZA, 1, -PLAZA, PLAZA, 14, PLAZA, 'minecraft:air'),
    fill(-PLAZA, -PAD_DEEP, -PLAZA, PLAZA, -2, PLAZA, 'minecraft:dirt'),
    fill(-PLAZA, -1, -PLAZA, PLAZA, -1, PLAZA, 'minecraft:stone'),
    fill(-PLAZA, 0, -PLAZA, PLAZA, 0, PLAZA, 'minecraft:cobblestone'),
    fill(-7, 0, -7, 7, 0, 7, 'minecraft:stone_bricks'),
    fill(-4, 0, -4, 4, 0, 4, 'minecraft:polished_andesite'),
]
# a gravel kerb ring, so the plaza reads as a paved square and not a slab
for k in (PLAZA - 1, -(PLAZA - 1)):
    sq.append(fill(-(PLAZA - 1), 0, k, PLAZA - 1, 0, k, 'minecraft:gravel'))
    sq.append(fill(k, 0, -(PLAZA - 1), k, 0, PLAZA - 1, 'minecraft:gravel'))
# the well: shaft first, then the wellhead on top of it
sq += [
    'place template %s %s %s %s' % (WELL_BOTTOM, t(WELL_X + 1), t(-10), t(WELL_Z + 1)),
    'place template %s %s %s %s' % (WELL_TOP, t(WELL_X), t(0), t(WELL_Z)),
    fill(WELL_X, 0, WELL_Z, WELL_X + 5, 5, WELL_Z + 5, 'minecraft:air', ' replace minecraft:jigsaw'),
    fill(WELL_X + 1, -10, WELL_Z + 1, WELL_X + 4, -1, WELL_Z + 4, 'minecraft:air',
         ' replace minecraft:jigsaw'),
]
probe('well_rim', [WELL_X + 1, 2, WELL_Z + 1], 'minecraft:cobblestone')
probe('well_roof', [WELL_X + 1, 5, WELL_Z + 1], 'minecraft:cobblestone')
# four market carts, one per quarter of the square
for i, (cx, cz) in enumerate(CART_POS):
    tid = MARKET_CARTS[i]
    sq.append('place template %s %s %s %s' % (tid, t(cx), t(1), t(cz)))
    sq.append(fill(cx, 1, cz, cx + 4, 5, cz + 4, 'minecraft:air', ' replace minecraft:jigsaw'))
_cart = Placed('market_cart', MARKET_CARTS[0], 0, CART_POS[0][0], CART_POS[0][1], y_base=-1)
for _pr in _cart.probes():
    PROBES.append(_pr)
# flower boxes and lanterns along the kerb
for i, (fx, fz) in enumerate(FLOWER_POS):
    sq.append(setb(fx, 1, fz, POST))
    sq.append(setb(fx, 2, fz, 'minecraft:lantern[hanging=false]'))
    sq.append(setb(fx + 1, 1, fz, 'supplementaries:flower_box'))
# the bench garden either side of the waystone (see SQ_BENCH above)
for (bx, bz, face) in SQ_BENCH:
    sq.append(setb(bx, 1, bz, 'handcrafted:oak_bench[facing=%s]' % face))
for (bx, bz) in SQ_PLANTER:
    sq.append(setb(bx, 1, bz, 'supplementaries:flower_box'))
for (bx, bz) in SQ_POST:
    sq.append(setb(bx, 1, bz, POST))
    sq.append(setb(bx, 2, bz, 'minecraft:lantern[hanging=false]'))
sq.append('setblock ~0 ~1 ~0 waystones:waystone{WaystoneName:"Town Square"}')
sq += arrival('The Town Square', 'A well, four lamps, somewhere to stand.',
              'minecraft:block.bell.resonate')
group('act1_square', 'anchor', sq)
probe('square_waystone', [0, 1, 0], 'waystones:waystone')

# --- the streets -------------------------------------------------------------
st = []
for name, pts in STREETS:
    st += street_cmds(pts)
group('act1_streets', 'anchor', st)
# Separate group: the pads DO clear their post cells, so this one must run
# exactly once (finaleAct1, just before the six lit posts go down) while
# act1_streets stays safe to re-lay after the Float paves the lakefront.
_pads = lamp_pad_cmds()
group('act1_lamp_pads', 'anchor', _pads)

# Q74 opens in mid-winter and asks the player to stand seventeen posts along
# roads that have had three months of snow on them. Snow blocks and powder snow
# are not replaceable by a block placement, so the sites are swept first: this
# is Josie's "forty posts, mill to square to lake" scene clearing its own way.
_sweep = []
for _pst in LAMPS['q34'] + LAMPS['q74']:
    _py = lev(_pst[0], _pst[2]) + 1
    for _blk in ('minecraft:snow', 'minecraft:snow_block', 'minecraft:powder_snow',
                 'minecraft:ice'):
        _sweep.append(fill(_pst[0], _py, _pst[2], _pst[0], _py + 1, _pst[2],
                           'minecraft:air', ' replace ' + _blk))
group('act4_lamp_sweep', 'anchor', _sweep)
probe('high_street', [0, lev(0, 20), 20], 'minecraft:cobblestone')
probe('mill_lane', [-20, lev(-20, 5), 5], 'minecraft:cobblestone')
# One of the whitelisted post sites that neither a street nor the plaza paves:
# proof that lamp_pad_cmds() levelled the raw hillside under it.
_padcell = next((pst for pst in LAMPS['q34'] + LAMPS['q74']
                 if (pst[0], pst[2]) not in street_cells), None)
if _padcell:
    probe('lamp_pad', [_padcell[0], lev(_padcell[0], _padcell[2]), _padcell[2]],
          'minecraft:gravel')

# --- Act II: the granary and the hedge garden -------------------------------
gp = P['granary']
alcoves = indoor_stands(gp)[:12]
dress_gran = []
for a in alcoves:
    dress_gran.append(setb(a[0], a[1] - 1, a[2], 'minecraft:polished_andesite'))
if alcoves:
    dress_gran.append(
        'setblock %s %s %s minecraft:oak_sign[rotation=8]{front_text:{messages:['
        '\'{"text":"THE GRANARY"}\',\'{"text":"twelve alcoves"}\',\'{"text":"twelve drawers"}\','
        '\'{"text":"- Oda"}\'],color:"gray"}}'
        % (t(gp.x0 - 1), t(1), t(gp.z0 - 1)))
building_group('act2_granary', 'granary', dressing=dress_gran)
if alcoves:
    probe('granary_alcove', [alcoves[0][0], alcoves[0][1] - 1, alcoves[0][2]],
          'minecraft:polished_andesite')
building_group('act2_garden', 'garden', top='minecraft:grass_block')

# --- Act III: the store, the bell tower, the supper table -------------------
store = P['store']
store_stand = indoor_stands(store)
dress_store = [npc('oda', list(store_stand[0]))] if store_stand else []
building_group('act3_store', 'store', dressing=dress_store)

church = P['church']
top_solid = max(lp[1] for lp, b in church.grid.items() if _solid(church.grid, lp))
bell_local = None
for lp, b in sorted(church.grid.items()):
    if lp[1] == top_solid - 1 and _solid(church.grid, lp):
        bell_local = lp
        break
bell = church.abs((bell_local[0], bell_local[1] + 1, bell_local[2])) if bell_local else None
dress_church = []
if bell:
    dress_church.append(setb(bell[0], bell[1], bell[2],
                             'minecraft:bell[attachment=floor,facing=south]'))
building_group('act3_church', 'church', dressing=dress_church)
if bell:
    probe('church_bell', bell, 'minecraft:bell')

# the Harvest Supper table: real furniture on the square, not a template box
tbl = []
for x in range(-4, 5):
    tbl.append(setb(x, 1, -10, 'handcrafted:oak_table'))
    tbl.append(setb(x, 1, -11, 'handcrafted:oak_chair[facing=south]'))
    tbl.append(setb(x, 1, -9, 'handcrafted:oak_chair[facing=north]'))
for x in (-4, 0, 4):
    tbl.append(setb(x, 2, -10, 'supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]'))
tbl += [
    setb(-6, 1, -10, POST), setb(-6, 2, -10, 'minecraft:lantern[hanging=false]'),
    setb(6, 1, -10, POST), setb(6, 2, -10, 'minecraft:lantern[hanging=false]'),
]
group('act3_table', 'anchor', tbl)
probe('supper_table', [0, 1, -10], 'handcrafted:oak_table')

# --- Act IV: the greenhouse ---------------------------------------------------
gx0, gz0, gx1, gz1 = gh
gm = OFF['greenhouse']
shell = pad_cmds(gx0 - 2, gz0 - 2, gx1 + 2, gz1 + 2, 10)
shell += [
    fill(gx0, 0, gz0, gx1, 0, gz1, 'minecraft:stone_bricks'),
    fill(gx0 + 1, 0, gz0 + 1, gx1 - 1, 0, gz1 - 1, 'minecraft:podzol'),
    fill(gx0, 1, gz0, gx1, 3, gz1, 'minecraft:spruce_planks', ' hollow'),
    fill(gx0 + 1, 1, gz0 + 1, gx1 - 1, 3, gz1 - 1, 'minecraft:air'),
]
for cx, cz in ((gx0, gz0), (gx1, gz0), (gx0, gz1), (gx1, gz1)):
    shell.append(fill(cx, 1, cz, cx, 3, cz, 'minecraft:spruce_log[axis=y]'))
GH_WINDOWS = []
for x in range(gx0 + 2, gx1 - 1, 3):
    GH_WINDOWS.append((x, gz0)); GH_WINDOWS.append((x, gz1))
for (wx, wz) in GH_WINDOWS:
    shell.append(fill(wx, 2, wz, wx + 1, 3, wz, 'minecraft:air'))
GH_DOOR = (gx0 + (gx1 - gx0) // 2, gz1)
shell.append(fill(GH_DOOR[0], 1, GH_DOOR[1], GH_DOOR[0], 2, GH_DOOR[1], 'minecraft:air'))
# The roof line. It used to be one flat course of fence at y 4, glazed flat at y 4, and
# from anywhere outside the valley it read as a pale blue slab lying in a field -- a glass
# box, not a greenhouse. It is a gable now: the ridge runs along x down the middle of the
# span, the pitch falls one block per two blocks of depth to the eaves, the risers between
# courses are closed so there are no holes to see sky through, and the two ends are filled
# in as proper gable walls in the same spruce as the rest of the shell.
def _gh_ry(z):
    d = min(z - gz0, gz1 - z)
    return 4 + (d + 1) // 2


GH_ROOF, GH_GABLE = [], []
_prev = None
for _z in range(gz0, gz1 + 1):
    _ry = _gh_ry(_z)
    GH_ROOF.append((_ry, _z))
    if _prev is not None and _ry > _prev:
        GH_ROOF.append((_ry - 1, _z))
    _prev = _ry
    for _y in range(4, _ry):
        GH_GABLE += [(gx0, _y, _z), (gx1, _y, _z)]

for (_ry, _z) in GH_ROOF:
    shell.append(fill(gx0, _ry, _z, gx1, _ry, _z, 'minecraft:spruce_fence'))
for (_gx, _gy, _gz) in GH_GABLE:
    shell.append(setb(_gx, _gy, _gz, 'minecraft:spruce_planks'))
shell += [
    fill(gx0 + 1, 1, gm[2], gx1 - 1, 1, gm[2], 'minecraft:spruce_slab[type=top]'),
    setb(gx0, 2, gm[2], LAMP_LIT),
    setb(gx1, 2, gm[2], LAMP_LIT),
]
shell += arrival(META['greenhouse']['label'], META['greenhouse']['blurb'])
GH_DY = PAD_DY.get('greenhouse', 0)
group('act4_greenhouse_shell', 'anchor', shift_y(shell, GH_DY))
probe('greenhouse_wall', [gx0, 1, gz0 + 1], 'minecraft:spruce_planks', dy=GH_DY)

glaze = []
for (wx, wz) in GH_WINDOWS:
    glaze.append(fill(wx, 2, wz, wx + 1, 3, wz, 'mcwwindows:spruce_window'))
glaze += [
    'setblock %s %s %s mcwdoors:oak_cottage_door[half=lower,facing=north,hinge=left,open=false]'
    % (t(GH_DOOR[0]), t(1), t(GH_DOOR[1])),
    'setblock %s %s %s mcwdoors:oak_cottage_door[half=upper,facing=north,hinge=left,open=false]'
    % (t(GH_DOOR[0]), t(2), t(GH_DOOR[1])),
]
for (_ry, _z) in GH_ROOF:
    glaze.append(fill(gx0, _ry, _z, gx1, _ry, _z, 'minecraft:glass'))
glaze += [
    # the eaves, so the roof has a line instead of an edge
    fill(gx0, 4, gz0, gx1, 4, gz0, 'minecraft:spruce_stairs[facing=north]'),
    fill(gx0, 4, gz1, gx1, 4, gz1, 'minecraft:spruce_stairs[facing=south]'),
]
for x in range(gx0 + 2, gx1 - 1, 2):
    glaze.append(setb(x, 2, gm[2], 'minecraft:flower_pot'))
glaze += [
    setb(gx0 + 2, 1, gm[2] - 2, 'farmersdelight:organic_compost'),
    setb(gx1 - 2, 1, gm[2] - 2, 'handcrafted:oak_table'),
    'playsound minecraft:block.glass.place master @a ~0 ~1 ~0 2 1',
]
group('act4_greenhouse_glaze', 'anchor', shift_y(glaze, GH_DY))
probe('greenhouse_glass', [gm[0], _gh_ry(gm[2]), gm[2]], 'minecraft:glass', dy=GH_DY)

heat = []
for x in range(gx0 + 2, gx1 - 1, 2):
    heat.append(setb(x, 0, gz0 + 1, 'minecraft:magma_block'))
heat.append(fill(gx0 + 1, 0, gz1 - 1, gx1 - 1, 0, gz1 - 1, 'thermal:fluid_duct'))
group('act4_greenhouse_heat', 'anchor', shift_y(heat, GH_DY))

# --- Act IV: the bathhouse ----------------------------------------------------
bx0, bz0, bx1, bz1 = bh
bm = OFF['bathhouse']
bath = pad_cmds(bx0 - 2, bz0 - 2, bx1 + 2, bz1 + 2, 10)
bath += [
    fill(bx0, 0, bz0, bx1, 0, bz1, 'minecraft:stone_bricks'),
    fill(bx0, 1, bz0, bx1, 3, bz1, 'minecraft:stone_bricks', ' hollow'),
    fill(bx0 + 1, 1, bz0 + 1, bx1 - 1, 3, bz1 - 1, 'minecraft:air'),
    fill(bx0 + 1, 4, bz0 + 1, bx1 - 1, 4, bz1 - 1, 'minecraft:spruce_planks'),
    fill(bx0, 4, bz0, bx1, 4, bz0, 'minecraft:spruce_stairs[facing=north]'),
    fill(bx0, 4, bz1, bx1, 4, bz1, 'minecraft:spruce_stairs[facing=south]'),
    fill(bx0, 4, bz0 + 1, bx0, 4, bz1 - 1, 'minecraft:spruce_stairs[facing=west]'),
    fill(bx1, 4, bz0 + 1, bx1, 4, bz1 - 1, 'minecraft:spruce_stairs[facing=east]'),
    # the door, facing the town
    fill(bm[0], 1, bz0, bm[0], 2, bz0, 'minecraft:air'),
    # two window bands
    fill(bx0, 2, bz0 + 2, bx0, 2, bz1 - 2, 'minecraft:glass_pane'),
    fill(bx1, 2, bz0 + 2, bx1, 2, bz1 - 2, 'minecraft:glass_pane'),
    # the tank
    fill(bx0 + 2, 0, bz0 + 2, bx1 - 2, 0, bz1 - 2, 'minecraft:water[level=0]'),
    setb(bm[0], -1, bm[2], 'minecraft:magma_block'),
    setb(bx0 + 1, 1, bz0 + 1, 'minecraft:cauldron'),
    setb(bx1 - 1, 1, bz1 - 1, 'handcrafted:oak_bench'),
    setb(bx0 + 1, 1, bz1 - 1, POST), setb(bx0 + 1, 2, bz1 - 1, LAMP_LIT),
    setb(bx1 - 1, 1, bz0 + 1, POST), setb(bx1 - 1, 2, bz0 + 1, LAMP_LIT),
    'particle minecraft:cloud %s %s %s 2 1 2 0.02 200 force @a' % (t(bm[0]), t(bm[1] + 2), t(bm[2])),
    'playsound minecraft:block.bubble_column.upwards_ambient master @a ~0 ~1 ~0 2 0.8',
]
BH_DY = PAD_DY.get('bathhouse', 0)
bath = shift_y(bath, BH_DY)
bath += apron_cmds({'pos': [bm[0], 1 + BH_DY, bz0], 'facing': 'north'}, 'bathhouse')
bath += arrival(META['bathhouse']['label'], META['bathhouse']['blurb'])
group('act4_bathhouse', 'anchor', bath)
probe('bathhouse_wall', [bx0, 2, bz0 + 1], 'minecraft:stone_bricks', dy=BH_DY)
probe('bathhouse_water', [bm[0], 0, bm[2] + 1], 'minecraft:water', dy=BH_DY)

# --- Act IV: the Works interior, bunker pieces inside the sealed shell -------
# The shell (valley_finales.js WORKS_SHELL) is works + [-6..8, -1..4, -6..8]:
# stone-brick floor at -1, ceiling at +4, four one-block walls.  Every bunker
# piece below is 6 blocks tall with its own floor at local y=0, so placing it
# at works.y-1 lands its floor on the shell floor and its ceiling on the shell
# ceiling - the exterior never breaches the shell.
WORKS_PIECES = [
    ('works_hall',  'nova_structures:bunker/bunker_underground_room_largest_1', 0, -6, -6),
    ('works_north', 'nova_structures:bunker/bunker_underground_room_medium_1',  0,  4, -6),
    ('works_south', 'nova_structures:bunker/bunker_underground_room_medium_2',  0,  4,  3),
]
works_grid = {}
wcmds = []
for name, tid, r, mx, mz in WORKS_PIECES:
    wp = Placed(name, tid, r, mx, mz, y_base=1, margin=0)
    if wp.x0 < -6 or wp.x1 > 8 or wp.z0 < -6 or wp.z1 > 8:
        raise SystemExit('%s breaches the Works shell: x %d..%d z %d..%d'
                         % (name, wp.x0, wp.x1, wp.z0, wp.z1))
    wcmds.append('place template %s %s %s %s %s'
                 % (tid, t(wp.ox), t(wp.oy), t(wp.oz), ROTS[r]))
    for lp, b in wp.grid.items():
        works_grid[wp.abs(lp)] = b
# the link corridor between the two east bays, and the doorways
wcmds += [
    fill(5, -1, 0, 8, -1, 2, 'minecraft:stone_bricks'),
    fill(5, 4, 0, 8, 4, 2, 'minecraft:stone_bricks'),
    fill(5, 0, 0, 7, 3, 2, 'minecraft:air'),
    fill(6, 0, -1, 6, 2, -1, 'minecraft:air'),
    fill(6, 0, 3, 6, 2, 3, 'minecraft:air'),
    fill(4, 0, 1, 4, 2, 1, 'minecraft:air'),
    fill(4, 0, -3, 4, 2, -3, 'minecraft:air'),
    fill(4, 0, 5, 4, 2, 5, 'minecraft:air'),
    fill(-6, -1, -6, 8, 4, 8, 'minecraft:air', ' replace minecraft:jigsaw'),
    # the shell is the only thing between this room and the water table
    fill(-6, -1, -6, 8, -1, 8, 'minecraft:stone_bricks'),
    fill(-6, 4, -6, 8, 4, 8, 'minecraft:stone_bricks'),
    fill(-6, 0, -6, -6, 3, 8, 'minecraft:stone_bricks'),
    fill(8, 0, -6, 8, 3, 8, 'minecraft:stone_bricks'),
    fill(-6, 0, -6, 8, 3, -6, 'minecraft:stone_bricks'),
    fill(-6, 0, 8, 8, 3, 8, 'minecraft:stone_bricks'),
    fill(-5, 0, -5, 7, 3, 7, 'minecraft:air', ' replace minecraft:water'),
]
group('act4_works', 'works', wcmds)

works_stands = []
for (x, y, z), b in sorted(works_grid.items()):
    if not _solid(works_grid, (x, y, z)):
        continue
    if _air(works_grid, (x, y + 1, z)) and _air(works_grid, (x, y + 2, z)) and y + 1 <= 2:
        works_stands.append([x, y + 1, z])
# the lever cell and the panel behind it must stay reachable and unbuilt
LEVER = [0, 2, 0]
PANEL = [0, 2, -1]
works_stands = [s for s in works_stands if not (abs(s[0]) <= 1 and abs(s[2]) <= 1)]
probe('works_floor', [0, -1, 0], 'minecraft:stone_bricks', origin='works')
probe('works_ceiling', [0, 4, 0], 'minecraft:stone_bricks', origin='works')
probe('works_bunker_wall', [4, 1, 0], 'minecraft:stone_bricks', origin='works')

# the five hanging lanterns and the stable, recomputed against the bunker rooms
lantern_spots = []
for (x, z) in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 0)):
    if works_grid.get((x, 4, z)) and _solid(works_grid, (x, 4, z)):
        lantern_spots.append([x, 3, z])
    elif (x, 4, z) not in works_grid:
        lantern_spots.append([x, 3, z])
group('act4_works_light', 'works',
      [setb(p[0], p[1], p[2], 'minecraft:lantern[hanging=true]') for p in lantern_spots])

# --- the inn's furniture, computed against the room that is actually there ----
def _pairs(stands, avoid, want):
    st = set(tuple(a) for a in stands)
    av = set(tuple(a) for a in avoid)
    out, used = [], set()
    for c in sorted(st):
        if len(out) >= want:
            break
        d = (c[0], c[1], c[2] + 1)
        if c in used or d in used or c in av or d in av or d not in st:
            continue
        out.append((c, d))
        used.add(c); used.add(d)
    return out


hall = [tuple(sitem) for sitem in inn_stands if sitem[1] == hearth[1]]
avoid = [tuple(x) for x in inn_tiles] + [tuple(hearth), tuple(crate_spot)]
bed_pairs = _pairs(hall, avoid, 3)
beds = []
for i, (a, b) in enumerate(bed_pairs):
    beds.append(setb(a[0], a[1], a[2], 'minecraft:white_bed[facing=south,part=foot]'))
    beds.append(setb(b[0], b[1], b[2], 'minecraft:white_bed[facing=south,part=head]'))
beds.append('playsound minecraft:block.wool.place master @a ~0 ~1 ~0 2 1')
group('act4_beds', 'anchor', shift_y(beds, PAD_DY.get('inn', 0)))
if bed_pairs:
    probe('inn_bed', list(bed_pairs[0][0]), 'minecraft:white_bed', dy=PAD_DY.get('inn', 0))

free = [c for c in hall if c not in avoid and
        all(c not in pr for pr in bed_pairs)]
chair = []
if len(free) >= 2:
    chair = [
        'tp @e[tag=npc_bram,limit=1] %s %s %s' % (t(free[0][0]), t(free[0][1]), t(free[0][2])),
        setb(free[1][0], free[1][1], free[1][2], 'handcrafted:oak_chair'),
        setb(free[-1][0], free[-1][1], free[-1][2], 'handcrafted:oak_table'),
        'particle minecraft:campfire_cosy_smoke %s %s %s 0.2 0.4 0.2 0.01 30 force @a'
        % (t(hearth[0]), t(hearth[1] + 1), t(hearth[2])),
        'playsound minecraft:entity.villager.yes master @a ~0 ~1 ~0 1 0.8',
    ]
group('act4_bram_chair', 'anchor', shift_y(chair, PAD_DY.get('inn', 0)))

# --- Tobin's copper outcrop --------------------------------------------------
TOB = solve_custom('tobin_camp', 9, 9, (28, -38))
tx0, tz0, tx1, tz1 = TOB
PAD_DY['tobin_camp'] = median_dy(tx0, tz0, tx1, tz1)
flat(tx0 - 2, tz0 - 2, tx1 + 2, tz1 + 2, PAD_DY['tobin_camp'], 'tobin_camp')
tob = pad_cmds(tx0 - 1, tz0 - 1, tx1 + 1, tz1 + 1, 9)
tob += [
    # the outcrop itself, in the north half of the clearing
    fill(tx0 + 2, 1, tz0 + 2, tx1 - 2, 3, tz0 + 6, 'minecraft:stone'),
    setb(tx0 + 3, 2, tz0 + 3, 'minecraft:copper_ore'),
    setb(tx0 + 4, 2, tz0 + 4, 'minecraft:copper_ore'),
    setb(tx0 + 3, 3, tz0 + 4, 'minecraft:copper_ore'),
    setb(tx0 + 5, 1, tz0 + 3, 'minecraft:copper_ore'),
    setb(tx1, 1, tz0 + 3, 'minecraft:raw_copper_block'),
    # his camp, in the south half: tent, fire, barrel, a light
    fill(tx0, 1, tz1 - 2, tx0 + 1, 2, tz1 - 1, 'minecraft:brown_wool'),
    setb(tx0 + 3, 1, tz1, 'minecraft:campfire[lit=true]'),
    setb(tx0 + 2, 1, tz1, 'minecraft:barrel[facing=up]'),
    setb(tx0 + 5, 1, tz1, POST),
    setb(tx0 + 5, 2, tz1, 'minecraft:lantern[hanging=false]'),
    npc('tobin', [tx0 + 4, 1, tz1 - 1]),
]
tob += arrival('The Copper Outcrop', 'Tobin\'s rock. A separate conversation.')
group('act1_tobin', 'anchor', shift_y(tob, PAD_DY['tobin_camp']))
probe('tobin_ore', [tx0 + 3, 2, tz0 + 3], 'minecraft:copper_ore', dy=PAD_DY['tobin_camp'])
META['tobin_camp'] = {'act': 'act1', 'label': 'The Copper Outcrop', 'blurb': 'Tobin found a rock.'}
CX['tobin_camp'] = TOB

# --- Act V --------------------------------------------------------------------
building_group('act5_townhall', 'town_hall')
for who in ('tess', 'mab', 'corin'):
    building_group('act5_' + who, 'newcomer_' + who)

# =============================================================================
# 10. The Kettle ruin and the cottage that replaces it
# =============================================================================
rt = template(RUIN)
rg, rsz = rt['blocks'], rt['size']
furnace = [lp for lp, b in sorted(rg.items()) if b[0] in ('minecraft:furnace', 'minecraft:campfire')]


def ruin_floor_cells():
    out = []
    for (x, y, z), b in rg.items():
        if y > 2 or not _solid(rg, (x, y, z)):
            continue
        if _air(rg, (x, y + 1, z)) and _air(rg, (x, y + 2, z)):
            out.append((x, y, z))
    return sorted(out)


cells = ruin_floor_cells()
if not cells:
    raise SystemExit('no floor found in ' + RUIN)
if furnace:
    fx, fy, fz = furnace[0]
    cells.sort(key=lambda c: (abs(c[0] - fx) + abs(c[2] - fz), abs(c[1] - fy), c))
else:
    cx, cz = rsz[0] // 2, rsz[2] // 2
    cells.sort(key=lambda c: (abs(c[0] - cx) + abs(c[2] - cz), c))
HEARTH_LOCAL = cells[0]
RUIN_MIN = [-HEARTH_LOCAL[0], -HEARTH_LOCAL[1], -HEARTH_LOCAL[2]]
RUIN_MAX = [RUIN_MIN[i] + rsz[i] - 1 for i in range(3)]

ruin_lines = [
    '# valley:setup/place_ruin  -- GENERATED by tools/scripts/plan_town.py, do not hand-edit.',
    '# Invoked positioned at the HEARTHSTONE (valley_core.js placeRuin).',
    '# The ruin is %s; its hearthstone is local %s.' % (RUIN, list(HEARTH_LOCAL)),
    '',
    'fill ~-11 ~1 ~-11 ~11 ~16 ~11 minecraft:air',
    'fill ~-11 ~-6 ~-11 ~11 ~-2 ~11 minecraft:stone',
    'fill ~-11 ~-1 ~-11 ~11 ~-1 ~11 minecraft:dirt',
    'fill ~-11 ~0 ~-11 ~11 ~0 ~11 minecraft:grass_block',
    'place template %s ~%d ~%d ~%d' % (RUIN, RUIN_MIN[0], RUIN_MIN[1], RUIN_MIN[2]),
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air replace minecraft:jigsaw'
    % (RUIN_MIN[0], RUIN_MIN[1], RUIN_MIN[2], RUIN_MAX[0], RUIN_MAX[1], RUIN_MAX[2]),
    'fill ~-11 ~0 ~-11 ~11 ~0 ~11 minecraft:grass_block replace minecraft:air',
    '# the flat grey hearthstone Q2 sends her to, and two blocks of air over it',
    'setblock ~0 ~0 ~0 minecraft:polished_andesite',
    'setblock ~0 ~1 ~0 minecraft:air',
    'setblock ~0 ~2 ~0 minecraft:air',
    'setblock ~-1 ~1 ~0 minecraft:campfire[lit=false]',
    '# four years of nobody keeping the yard',
    'setblock ~-7 ~1 ~6 minecraft:oak_fence',
    'setblock ~-6 ~1 ~7 minecraft:oak_fence',
    'setblock ~7 ~1 ~-6 minecraft:mossy_cobblestone',
    'setblock ~-8 ~1 ~-7 minecraft:mossy_cobblestone',
    'setblock ~6 ~1 ~7 minecraft:oak_fence',
    '# the gate, so the end of the lit path is unmistakably the place',
    'setblock ~0 ~1 ~8 minecraft:oak_fence',
    'setblock ~0 ~2 ~8 minecraft:oak_sign[rotation=8]{front_text:{messages:[\'{"text":"KETTLE FARM"}\',\'{"text":""}\',\'{"text":"J. Kettle"}\',\'{"text":"mind the weeds"}\'],color:"gray"}}',
    'setblock ~-1 ~1 ~8 minecraft:lantern[hanging=false]',
    'setblock ~1 ~1 ~8 minecraft:lantern[hanging=false]',
    'title @a times 10 70 20',
    'title @a subtitle {"text":"Three walls, a chimney, a cold hearth.","color":"gray","italic":true}',
    'title @a title {"text":"The Old Kettle Farm","color":"gold"}',
    'execute at @a run playsound minecraft:block.bell.resonate master @a ~ ~ ~ 1 0.9',
]

# --- the cottage --------------------------------------------------------------
ct = template(COTTAGE)
cg, csz = ct['blocks'], ct['size']
# the meadow chalet's interior floor centre - the hearthstone has to end up here
cstands = []
for (x, y, z), b in cg.items():
    if _solid(cg, (x, y, z)) and _air(cg, (x, y + 1, z)) and _air(cg, (x, y + 2, z)) \
            and any(_solid(cg, (x, yy, z)) for yy in range(y + 3, csz[1])):
        cstands.append((x, y, z))
if not cstands:
    raise SystemExit('no indoor floor in ' + COTTAGE)
cxs = sorted(cstands)
COT_HEARTH = cxs[len(cxs) // 2]
# home is the waystone, one block above the hearthstone
COT_MIN = [-COT_HEARTH[0], -1 - COT_HEARTH[1], -COT_HEARTH[2]]
COT_MAX = [COT_MIN[i] + csz[i] - 1 for i in range(3)]

cot_lines = [
    '# valley:act1/cottage  -- GENERATED by tools/scripts/plan_town.py, do not hand-edit.',
    '# Invoked positioned at the HOME waystone (valley_checks.js, Q2).',
    '# Home is the waystone; the hearthstone is home + [0,-1,0]; the ruin comes down',
    '# and %s goes up around it, so the hearthstone ends up on the cottage floor.' % COTTAGE,
    '',
    '# 1. clear the ruin, and level the yard Q9 and Q10 are marked out on',
    'fill ~-11 ~0 ~-14 ~11 ~15 ~11 minecraft:air',
    'fill ~-11 ~-4 ~-14 ~11 ~-3 ~11 minecraft:dirt',
    'fill ~-11 ~-2 ~-14 ~11 ~-2 ~11 minecraft:coarse_dirt',
    'fill ~-11 ~-1 ~-14 ~11 ~-1 ~11 minecraft:grass_block',
    '',
    '# 2. the cottage, placed so its interior floor centre IS the hearthstone',
    'place template %s ~%d ~%d ~%d' % (COTTAGE, COT_MIN[0], COT_MIN[1], COT_MIN[2]),
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air replace minecraft:jigsaw'
    % (COT_MIN[0], COT_MIN[1], COT_MIN[2], COT_MAX[0], COT_MAX[1], COT_MAX[2]),
]
for x in range(COT_MIN[0], COT_MAX[0] + 1, 4):
    cot_lines.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone_bricks replace minecraft:cyan_concrete'
                     % (x, COT_MIN[1], COT_MIN[2], min(x + 1, COT_MAX[0]), COT_MAX[1], COT_MAX[2]))
cot_lines += [
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:gravel replace minecraft:cyan_concrete'
    % (COT_MIN[0], COT_MIN[1], COT_MIN[2], COT_MAX[0], COT_MAX[1], COT_MAX[2]),
    'fill ~-11 ~-1 ~-14 ~11 ~-1 ~11 minecraft:grass_block replace minecraft:air',
    '',
    '# 3. Q3 hangs the door, the two windows, the bed and the sconce herself, so the',
    '#    template\'s own door, glass and bed come out and leave the holes behind.',
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air replace minecraft:dark_oak_door'
    % (COT_MIN[0], COT_MIN[1], COT_MIN[2], COT_MAX[0], COT_MAX[1], COT_MAX[2]),
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air replace minecraft:white_stained_glass_pane'
    % (COT_MIN[0], COT_MIN[1], COT_MIN[2], COT_MAX[0], COT_MAX[1], COT_MAX[2]),
    'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air replace minecraft:green_bed'
    % (COT_MIN[0], COT_MIN[1], COT_MIN[2], COT_MAX[0], COT_MAX[1], COT_MAX[2]),
    '',
    '# 4. the hearthstone stays a hearthstone, and Home stands on it',
    'setblock ~0 ~-1 ~0 minecraft:polished_andesite',
    'setblock ~0 ~0 ~0 waystones:waystone{WaystoneName:"Home"}',
    '# the wool mat Q3 puts the Red Bed on, and the hook for the sconce',
    'setblock ~-1 ~-1 ~-1 minecraft:white_wool',
    'setblock ~-1 ~-1 ~0 minecraft:white_wool',
    'setblock ~-2 ~-1 ~-1 minecraft:red_carpet',
    'setblock ~1 ~0 ~1 minecraft:oak_fence',
    '',
    '# 5. HOME_PORCH: the bare fortieth post lands at home + [3,0,0] (Q90), so that',
    '#    cell is kept clear with solid ground under it.',
    'setblock ~3 ~-1 ~0 minecraft:cobblestone',
    'setblock ~3 ~0 ~0 minecraft:air',
    'setblock ~3 ~1 ~0 minecraft:air',
    'fill ~1 ~-1 ~1 ~4 ~-1 ~3 minecraft:cobblestone',
    '',
    '# 6. Q9: the 3x9 patch behind the house. 27 dirt_path tiles, one per seed.',
    'fill ~-8 ~-1 ~-8 ~0 ~-1 ~-6 minecraft:dirt_path',
    'setblock ~-4 ~-1 ~-10 minecraft:water',
    '# Q10: the pen. 23 cobblestone footings and one polished andesite gate slot.',
    'fill ~1 ~-1 ~-12 ~7 ~-1 ~-12 minecraft:cobblestone',
    'fill ~1 ~-1 ~-6 ~7 ~-1 ~-6 minecraft:cobblestone',
    'fill ~1 ~-1 ~-11 ~1 ~-1 ~-7 minecraft:cobblestone',
    'fill ~7 ~-1 ~-11 ~7 ~-1 ~-7 minecraft:cobblestone',
    'setblock ~4 ~-1 ~-6 minecraft:polished_andesite',
    'setblock ~-4 ~0 ~-5 minecraft:oak_sign[rotation=8]{front_text:{messages:[\'{"text":"3 x 9"}\',\'{"text":"wheat"}\',\'{"text":"carrots"}\',\'{"text":"potatoes"}\'],color:"gray"}}',
    'setblock ~4 ~0 ~-5 minecraft:oak_sign[rotation=8]{front_text:{messages:[\'{"text":"THE PEN"}\',\'{"text":"fence the stone"}\',\'{"text":"gate on grey"}\',\'{"text":""}\'],color:"gray"}}',
    '',
    'tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\\"Four walls and a door. The mat is where my bed was; that corner stays warm until about four in the morning.\\"","color":"white","italic":true}]',
    'playsound minecraft:block.wood.place master @a[distance=..64] ~ ~ ~ 1 0.9',
]

# --- Q7's road head -----------------------------------------------------------
sp_lines = [
    '# valley:act1/square_path  -- GENERATED by tools/scripts/plan_town.py.',
    '# Q7 reward, invoked positioned at the Town Anchor.',
    '# The stake pad is on the plaza, which is the datum; the twenty-four blocks of High',
    '# Street south of it are laid COLUMN BY COLUMN at the level act1_streets gave them,',
    '# because the street is a staircase down the hill now and a flat re-lay would cut a',
    '# trench through it at Q7.',
    'fill ~-3 ~1 ~-3 ~3 ~6 ~3 minecraft:air',
    'fill ~-3 ~-5 ~-3 ~3 ~-1 ~3 minecraft:dirt',
    'fill ~-3 ~0 ~-3 ~3 ~0 ~3 minecraft:stone_bricks',
    'setblock ~0 ~0 ~0 minecraft:polished_andesite',
]
for _sz in range(1, 25):
    for _sx in (-2, -1, 0, 1, 2):
        _sy = lev(_sx, _sz)
        if abs(_sx) == 2 and not (4 <= _sz <= 20):
            continue
        sp_lines.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                        % (_sx, _sy + 1, _sz, _sx, _sy + 6, _sz))
        sp_lines.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:dirt'
                        % (_sx, _sy - 5, _sz, _sx, _sy - 1, _sz))
        sp_lines.append('setblock ~%d ~%d ~%d %s'
                        % (_sx, _sy, _sz,
                           'minecraft:gravel' if abs(_sx) == 2 else
                           'minecraft:polished_andesite' if _sx == 0 else
                           'minecraft:cobblestone'))
sp_lines += [
    '# the first two lamp posts: 2 of 40 (valley_core.js LAMPS_Q07).',
    'setblock ~-2 ~%d ~8 %s' % (lev(-2, 8) + 1, POST),
    'setblock ~-2 ~%d ~8 %s' % (lev(-2, 8) + 2, LAMP_LIT),
    'setblock ~2 ~%d ~16 %s' % (lev(2, 16) + 1, POST),
    'setblock ~2 ~%d ~16 %s' % (lev(2, 16) + 2, LAMP_LIT),
    'setblock ~-2 ~%d ~2 minecraft:oak_fence' % (lev(-2, 2) + 1),
    'setblock ~2 ~%d ~2 minecraft:oak_fence' % (lev(2, 2) + 1),
    'setblock ~-2 ~%d ~2 minecraft:lantern[hanging=false]' % (lev(-2, 2) + 2),
    'setblock ~2 ~%d ~2 minecraft:lantern[hanging=false]' % (lev(2, 2) + 2),
    'tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\\"Stake\'s in. Bram will tell you he chose the spot. Let him.\\"","color":"white","italic":true}]',
    'playsound minecraft:block.stone.place master @a[distance=..64] ~ ~ ~ 1 0.8',
]

# =============================================================================
# 11. Sanity checks
# =============================================================================
# The aprons connect. Asserted over the PAVING the plan actually emits, so a
# door that is one block of grass short of the road stops the generator here
# rather than shipping.
assert_doors_reach_plaza()

errors = []
allb = {}
for n, p in P.items():
    allb[n] = (p.x0, p.z0, p.x1, p.z1, p.pad())
for n, (x0, z0, x1, z1, pd) in list(allb.items()):
    for m, (a0, b0, a1, b1, pd2) in allb.items():
        if m <= n:
            continue
        if not (x1 < a0 or a1 < x0 or z1 < b0 or b1 < z0):
            errors.append('footprint overlap: %s and %s' % (n, m))
for name, rect in CX.items():
    for n, (x0, z0, x1, z1, pd) in allb.items():
        if not (rect[2] < x0 or x1 < rect[0] or rect[3] < z0 or z1 < rect[1]):
            errors.append('footprint overlap: %s and %s' % (name, n))
lamp_cells = set()
for route, posts in LAMPS.items():
    for p in posts:
        lamp_cells.add((p[0], p[2]))
for n, (x0, z0, x1, z1, pd) in allb.items():
    for c in lamp_cells:
        if pd[0] <= c[0] <= pd[2] and pd[1] <= c[1] <= pd[3]:
            errors.append('lamp %s inside pad of %s' % (str(c), n))
for name, rect in CX.items():
    for c in lamp_cells:
        if rect[0] - 2 <= c[0] <= rect[2] + 2 and rect[1] - 2 <= c[1] <= rect[3] + 2:
            errors.append('lamp %s inside pad of %s' % (str(c), name))
for n, (x0, z0, x1, z1, pd) in allb.items():
    if not (pd[2] < -PLAZA or pd[0] > PLAZA or pd[3] < -PLAZA or pd[1] > PLAZA):
        errors.append('%s pad reaches into the plaza' % n)
# The mill yard holds an open water channel; a street clearing dy1..6 through it
# empties the race across the plot.
_streetcells = set()
for _n, _pts in STREETS:
    _streetcells |= polyline_cells(_pts, ROAD_BRUSH + 1)
for _c in rect_cells(*MILL_YARD):
    if _c in _streetcells:
        errors.append('mill yard cell %s is inside a street' % str(_c))

# Nothing the plan builds may stand in a whitelisted lamp post's cell: Q34 and
# Q74 ask the player to PLACE those posts, and a cell with a mill axle or a
# flower box in it silently refuses the placement forever.
# The post's cell is one block above the ground it stands on, and the ground under a
# whitelisted post is now whatever level the street beside it was terraced to -- not the
# anchor's Y. Reading LAMPS[..][1] literally made this check fire on every street that
# climbs, because the paving at its own level and the post's old fixed dy 1 collide.
_lampcells = set()
for _r, _ps in LAMPS.items():
    for _p in _ps:
        _ly = lev(_p[0], _p[2])
        _lampcells.add((_p[0], _ly + 1, _p[2]))
        _lampcells.add((_p[0], _ly + 2, _p[2]))
_setre = re.compile(r'^setblock ~(-?\d+) ~(-?\d+) ~(-?\d+) (\S+)')
for _k, _g in GROUPS.items():
    if _g['origin'] != 'anchor':
        continue
    for _c in _g['cmds']:
        _m = _setre.match(_c)
        if not _m:
            continue
        _pos = (int(_m.group(1)), int(_m.group(2)), int(_m.group(3)))
        if _pos in _lampcells and 'air' not in _m.group(4) and 'copper_lamp' not in _m.group(4):
            errors.append('%s writes %s into lamp-post cell %s' % (_k, _m.group(4), str(_pos)))

# -----------------------------------------------------------------------------
# Every template id this file emits has to EXIST.
#
# `place template <id>` on an id no installed jar carries is a SILENT no-op:
# the command returns 0, runSeg logs one warning nobody reads, and the build is
# simply absent. That is how the fourth market cart came to be a blank patch of
# paving for the whole game - the plan asked for
# nova_structures:tavern/tavern_event_trader_car_cartographer_SPRUCE and
# dungeons-and-taverns ships the cartographer car bare.
# -----------------------------------------------------------------------------
def jar_template_index():
    idx = set()
    for ns, jar in JARS.items():
        try:
            z = zipfile.ZipFile(jar)
        except Exception as exc:                       # noqa: BLE001
            errors.append('cannot open %s for the template index (%s)' % (jar, exc))
            continue
        for nm in z.namelist():
            m = re.match(r'data/([^/]+)/structures/(.+)\.nbt$', nm)
            if m:
                idx.add(m.group(1) + ':' + m.group(2))
    for nm in pathlib.Path('pack/kubejs/data').rglob('*.nbt'):
        m = re.search(r'/data/([^/]+)/structures/(.+)\.nbt$', '/' + nm.as_posix())
        if m:
            idx.add(m.group(1) + ':' + m.group(2))
    return idx


_placere = re.compile(r'place template (\S+)')
TEMPLATE_IDS = set()
for _g in GROUPS.values():
    for _c in _g['cmds']:
        _m = _placere.search(_c)
        if _m:
            TEMPLATE_IDS.add(_m.group(1))
for _lines in (ruin_lines, cot_lines, sp_lines):
    for _c in _lines:
        _m = _placere.search(_c)
        if _m:
            TEMPLATE_IDS.add(_m.group(1))
TEMPLATE_IDS |= {RUIN, COTTAGE, WELL_TOP, WELL_BOTTOM} | set(MARKET_CARTS)
TEMPLATE_IDS |= {b[1] for b in BUILDINGS} | {w[1] for w in WORKS_PIECES}
_index = jar_template_index()
for _tid in sorted(TEMPLATE_IDS):
    if _tid not in _index:
        near = [i for i in _index if i.split('/')[-1].startswith(_tid.split('/')[-1][:14])]
        errors.append('template does not exist: %s%s'
                      % (_tid, ('  (did you mean %s?)' % near[0]) if near else ''))

# -----------------------------------------------------------------------------
# The 3-D write-set replay.
#
# Section 6's solver thinks in x/z. The Works does not: it is a sealed room six
# blocks under the north-east shoulder of the town, and Act V's newcomer pad
# ran `fill ~42 ~-10 ~-26 ~57 ~-2 ~-11 dirt` right down its east wall - ninety
# cells - because in x/z that pad and that room are simply two different
# things at two different heights and nothing in the plan ever compared them.
#
# So every group's commands are turned back into the BOXES they write, shifted
# into anchor-relative space, and replayed in the order the pack actually runs
# them (RUN_ORDER below, which is checked against GROUPS so it cannot go
# stale). After act4_works has built the shell:
#   * no group whose origin is not the Works may write one cell INSIDE it, and
#   * no group whose origin IS the Works may write one cell OUTSIDE it.
# Before act4_works, anything goes: the shell is laid over whatever is there.
# -----------------------------------------------------------------------------
RUN_ORDER = [
    'act1_inn', 'act1_mill', 'act1_marnie', 'act1_pip',            # Act I scenes
    'act1_square', 'act1_streets', 'act1_lamp_pads', 'act1_tobin',  # finaleAct1
    'act2_granary', 'act2_garden',                                  # finaleAct2
    'act3_store', 'act3_church', 'act3_table',                      # finaleAct3
    'act4_greenhouse_shell',                                        # scene q60
    'act4_greenhouse_glaze',                                        # scene q64
    'act4_works',                                                   # q65 pre: excavateWorks
    'act4_works_light',                                             # scene q65
    'act4_beds',                                                    # scene q70a
    'act4_greenhouse_heat', 'act4_bathhouse',                       # scene q72
    'act4_bram_chair',                                              # scene q73
    'act4_lamp_sweep',                                              # scene q74
    'act5_townhall', 'act5_tess', 'act5_mab', 'act5_corin',         # finaleAct5
]
if set(RUN_ORDER) != set(GROUPS.keys()):
    errors.append('RUN_ORDER is stale: missing %s, unknown %s'
                  % (sorted(set(GROUPS) - set(RUN_ORDER)), sorted(set(RUN_ORDER) - set(GROUPS))))

_FILLRE = re.compile(r'^fill ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+)\s')
_SETRE = re.compile(r'^setblock ~(-?\d+) ~(-?\d+) ~(-?\d+)\s')
_PLCRE = re.compile(r'^place template (\S+) ~(-?\d+) ~(-?\d+) ~(-?\d+)(?:\s+(\S+))?')
_PADRE = re.compile(r'^@pad ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) (\d+) (\d+)')
_PFXRE = re.compile(r'^@padfix ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+) ~(-?\d+)')


def write_boxes(cmd):
    """The (x0,y0,z0,x1,y1,z1) boxes a command writes, in its group's frame."""
    m = _FILLRE.match(cmd)
    if m:
        a = [int(v) for v in m.groups()]
        return [(min(a[0], a[3]), min(a[1], a[4]), min(a[2], a[5]),
                 max(a[0], a[3]), max(a[1], a[4]), max(a[2], a[5]))]
    m = _SETRE.match(cmd)
    if m:
        x, y, z = (int(v) for v in m.groups())
        return [(x, y, z, x, y, z)]
    m = _PADRE.match(cmd)
    if m:
        a = [int(v) for v in m.groups()]
        x0, x1 = sorted((a[0], a[3]))
        z0, z1 = sorted((a[2], a[5]))
        return [(x0, a[1] - a[7], z0, x1, a[1] + a[6], z1)]
    m = _PFXRE.match(cmd)
    if m:
        a = [int(v) for v in m.groups()]
        x0, x1 = sorted((a[0], a[3]))
        z0, z1 = sorted((a[2], a[5]))
        return [(x0, a[1], z0, x1, a[1], z1)]
    m = _PLCRE.match(cmd)
    if m:
        tid = m.group(1)
        ox, oy, oz = int(m.group(2)), int(m.group(3)), int(m.group(4))
        rot = m.group(5) if m.group(5) in ROTS else 'none'
        try:
            sz = template(tid)['size']
        except Exception:                              # noqa: BLE001
            return []                                  # the existence check above owns this
        r = ROTS.index(rot)
        fw, fd = footprint(sz, r)
        mx, mz = origin_offset(sz, r)
        return [(ox + mx, oy, oz + mz, ox + mx + fw - 1, oy + sz[1] - 1, oz + mz + fd - 1)]
    return []


def overlap_cells(a, b):
    lo = [max(a[i], b[i]) for i in range(3)]
    hi = [min(a[3 + i], b[3 + i]) for i in range(3)]
    if any(lo[i] > hi[i] for i in range(3)):
        return 0
    return (hi[0] - lo[0] + 1) * (hi[1] - lo[1] + 1) * (hi[2] - lo[2] + 1)


WORKS_BOX = works_box(0)
_seal_at = RUN_ORDER.index('act4_works') if 'act4_works' in RUN_ORDER else 0
_earlier_hits = 0
for _i, _k in enumerate(RUN_ORDER):
    if _k not in GROUPS:
        continue
    _g = GROUPS[_k]
    _shift = OFF.get(_g['origin'], [0, 0, 0]) if _g['origin'] != 'anchor' else [0, 0, 0]
    _own = (_g['origin'] == 'works')
    for _c in _g['cmds']:
        for _b in write_boxes(_c):
            _wb = (_b[0] + _shift[0], _b[1] + _shift[1], _b[2] + _shift[2],
                   _b[3] + _shift[0], _b[4] + _shift[1], _b[5] + _shift[2])
            _in = overlap_cells(_wb, WORKS_BOX)
            if _own:
                _tot = ((_wb[3] - _wb[0] + 1) * (_wb[4] - _wb[1] + 1) * (_wb[5] - _wb[2] + 1))
                if _tot > _in:
                    errors.append('%s writes %d cell(s) OUTSIDE the Works shell: %s'
                                  % (_k, _tot - _in, _c[:96]))
                continue
            if not _in:
                continue
            if _i < _seal_at:
                _earlier_hits += _in
            else:
                errors.append('%s writes %d cell(s) of the sealed Works shell (%s): %s'
                              % (_k, _in, str(WORKS_BOX), _c[:96]))

# -----------------------------------------------------------------------------
# The town's own footprint, for the Q7 stake handler (valley_checks.js). Every
# pad, the plaza, every street verge, every whitelisted lamp post, the lakefront
# the Act II Float levels and digs, and the Works. Grown by `town_clearance`
# this is the box a homestead has to be OUTSIDE of before a stake is accepted.
# -----------------------------------------------------------------------------
_bx = [-PLAZA, PLAZA]
_bz = [-PLAZA, PLAZA]


def _grow(x, z):
    _bx[0] = min(_bx[0], x); _bx[1] = max(_bx[1], x)
    _bz[0] = min(_bz[0], z); _bz[1] = max(_bz[1], z)


for _n, _p in P.items():
    _pd = _p.pad()
    _grow(_pd[0], _pd[1]); _grow(_pd[2], _pd[3])
for _n, _r in CX.items():
    _grow(_r[0] - 2, _r[1] - 2); _grow(_r[2] + 2, _r[3] + 2)
for _n, _pts in STREETS:
    for _c in polyline_cells(_pts, ROAD_BRUSH + 1):
        _grow(_c[0], _c[1])
for _r, _ps in LAMPS.items():
    for _p2 in _ps:
        _grow(_p2[0] - 1, _p2[2] - 1); _grow(_p2[0] + 1, _p2[2] + 1)
_lk = OFF['lake']
_grow(_lk[0] - 14, _lk[2] - 14)                 # the Float levels lake +-14
_grow(_lk[0] + 14, _lk[2] + 26)                 # ...and digs the basin to +26
_grow(WORKS_BOX[0], WORKS_BOX[2])
_grow(WORKS_BOX[3], WORKS_BOX[5])
TOWN_BOX = {'x': list(_bx), 'z': list(_bz)}
TOWN_CLEARANCE = 12

# -----------------------------------------------------------------------------
# What valley:act1/cottage deliberately does to the template AFTER placing it.
#
# Q3 hangs the door, the glass and the bed herself, so the template's own come
# straight back out; the hearthstone, the Home waystone, the wool mat, the
# porch, Q9's seed bed and Q10's pen are all written over the template's floor
# and yard. Those cells are MEANT to differ from the NBT, so the independent
# verifier's cottage check needs to know which they are rather than being
# calibrated with a percentage.
#   overwrites   home-relative boxes written after the `place template` line
#   removed_ids  template block ids taken out by a `... replace <id>` fill
# -----------------------------------------------------------------------------
COT_OVERWRITES, COT_REMOVED = [], set()
_seen_place = False
for _c in cot_lines:
    if _c.startswith('place template'):
        _seen_place = True
        continue
    if not _seen_place or _c.startswith('#'):
        continue
    _m = re.search(r' replace (\S+)$', _c)
    if _m:
        COT_REMOVED.add(_m.group(1))
        continue
    COT_OVERWRITES += [list(b) for b in write_boxes(_c)]

if errors:
    for e in errors:
        print('ERROR ' + e)
    raise SystemExit(1)
print('  works shell: %s; %d cell(s) written into it before act4_works seals it (fine)'
      % (str(WORKS_BOX), _earlier_hits))
print('  town box (anchor-relative): x %d..%d  z %d..%d, clearance %d'
      % (TOWN_BOX['x'][0], TOWN_BOX['x'][1], TOWN_BOX['z'][0], TOWN_BOX['z'][1], TOWN_CLEARANCE))

NPC_SPOTS = []
_npcre = re.compile(r'easy_npc preset import data \S+ ~(-?\d+) ~(-?\d+) ~(-?\d+)')
for _k, _g in GROUPS.items():
    for _c in _g['cmds']:
        _m = _npcre.search(_c)
        if _m:
            NPC_SPOTS.append({'group': _k, 'origin': _g['origin'],
                              'pos': [int(_m.group(1)), int(_m.group(2)), int(_m.group(3))]})

# =============================================================================
# 11.5  DAY ONE: the world as she finds it.
#
# The pack no longer rebuilds the valley around the player (docs/transitions-design.md,
# architecture A). Everything below is written into the MASTER WORLD once, at build time,
# by `/valley build all`, and never runs again. This section computes it.
#
# It only runs when a chosen site is on disk (`--site <json>`, written by
# tools/scripts/seed_hunt.py site). Without one, plan_town.py behaves exactly as before,
# so the file stays runnable on its own.
#
# What day one looks like, and why:
#   - The COTTAGE STANDS, with visible gaps. No door, two empty window holes, a 2x2 hole
#     in the roof, no bed. Q3 hands her the pieces that fill exactly those gaps, so the
#     first act is "finish the house you are living in" rather than "watch your house be
#     replaced" (§5 rule 1: never replace a player-placed block; §1: no swaps).
#   - The TOWN STANDS, abandoned: every building present, every lamp UNLIT, the mill
#     without its water wheel, the inn empty, the store shuttered. Lighting a lamp is a
#     setblock on a block the town planner already put there.
#   - The LANTERN ROAD is one continuous road, spawn -> farm gate -> town square, laid at
#     each column's own surface with steps cut, never a dotted line of floating path
#     blocks (the ruinPath failure named in docs/research/our-world-edits.md §4).
# =============================================================================
DAY1 = {}
SITES_JSON = None

if SITE:
    def dsurf(x, z):
        """The DESIGN surface: what the finished valley's ground is at this column --
        the plan's own level where it has one, the pregen's land everywhere else."""
        return ANCHOR_W[1] + lev(x - ANCHOR_W[0], z - ANCHOR_W[2])

    # =========================================================================
    # The lantern road: spawn -> farm gate -> town square, ONE road.
    #
    # Route: three legs joined end to end, each a straight run between fixed points,
    # walked one column at a time. The centre line is laid at that column's OWN surface
    # (never at a single anchored Y -- the "town one block proud of the world" failure),
    # and where consecutive columns differ by more than one the intervening column is
    # stepped so the road is walkable rather than a broken dotted line.
    # =========================================================================
    GATE_W = [HEARTH_W[0], 0, HEARTH_W[2] + 8]                 # the KETTLE FARM gate post
    # The road TURNS IN at the gate rather than making straight for it. A straight run from
    # spawn to the gate post clips the cottage's east wall -- the built world had the road's
    # last columns going through the house, which is where nature_check's "step of 8 at
    # -316,28" came from: the probe was reading the roof. The bend is due east of the gate,
    # eight blocks south of the hearthstone, so the final approach runs along the bottom of
    # the yard and arrives at the gate from outside it.
    BEND_W = [HEARTH_W[0] + 14, 0, HEARTH_W[2] + 8]

    def _leg(a, b):
        """Integer columns from a to b inclusive of a, exclusive of b (Bresenham-ish)."""
        ax, az = a[0], a[2]
        bx, bz = b[0], b[2]
        n = max(abs(bx - ax), abs(bz - az))
        out = []
        for i in range(n):
            f = i / float(n) if n else 0.0
            out.append((int(round(ax + (bx - ax) * f)), int(round(az + (bz - az) * f))))
        return out

    # One road, walked once: the square's doorstep (spawn stands 14 blocks off the anchor,
    # at the town's mouth) out to the farm gate. The old route ran spawn -> gate -> back to
    # the plaza's south kerb, which laid a second carriageway ten blocks from the first all
    # the way down the valley and then had to be pinned twice.
    ROAD_CENTRE = []
    for _a, _b in ((SPAWN_W, BEND_W), (BEND_W, GATE_W)):
        for _c in _leg(_a, _b):
            if not ROAD_CENTRE or ROAD_CENTRE[-1] != _c:
                ROAD_CENTRE.append(_c)
    ROAD_CENTRE.append((GATE_W[0], GATE_W[2]))

    # The road's own Y. Read off the DESIGN surface, not the raw land: where the road runs
    # into the plaza or the cottage yard it has to arrive at the level those were terraced
    # to, and everywhere else the design surface IS the land.
    _ry = []
    for _x, _z in ROAD_CENTRE:
        _ry.append(dsurf(_x, _z))
    # Where the road runs INTO a pad, it has to arrive at the pad's level. The cottage yard
    # is levelled to the hearthstone and the plaza to the anchor, both at build time; a road
    # laid at the natural surface through them meets the finished pad at a cliff. The first
    # built world had an 8-block step at -316,28 for exactly this reason -- the road's own
    # Y there was the hillside's, and day1_cottage then cut the yard out from under it.
    # Pinning those columns before the smoothing pass lets the ramp be spread over the run
    # into the yard instead of appearing as one step at its edge.
    def _pin(x, z):
        """The two levelled places the road runs through, which it must ARRIVE at rather
        than meet at a cliff. Everything between them is terrain."""
        if (HEARTH_W[0] + COT_FLAT[0] <= x <= HEARTH_W[0] + COT_FLAT[2]) and \
           (HEARTH_W[2] + COT_FLAT[1] <= z <= HEARTH_W[2] + COT_FLAT[3]):
            return HEARTH_W[1]
        if (ANCHOR_W[0]-PLAZA <= x <= ANCHOR_W[0]+PLAZA) and (ANCHOR_W[2]-PLAZA <= z <= ANCHOR_W[2]+PLAZA):
            return ANCHOR_W[1]
        return None

    # A STAIRCASE, not a smoothing pass. The old code clamped the profile to one block of
    # climb per COLUMN, which is a 45-degree road, and nature_check's `road_steps` fails it
    # on the second half of the rule: a step of 1 needs ROAD_RUN flat blocks in front of it.
    # The road is walked from the square out to the farm, so the profile is built in that
    # direction, pinned at the square, and the pins in between are hit by re-running the
    # staircase from each pin to the next.
    _pins = [(_i, _pin(_x, _z)) for _i, (_x, _z) in enumerate(ROAD_CENTRE)]
    _pins = [(i, v) for i, v in _pins if v is not None]
    _segs = []
    _cut = [0]
    if _pins:
        # the run of columns that are inside a pinned rectangle keeps that rectangle's level
        _first, _last = _pins[0][0], _pins[-1][0]
    ROAD_Y = list(_ry)
    _i = 0
    while _i < len(ROAD_CENTRE):
        _pv = _pin(*ROAD_CENTRE[_i])
        if _pv is not None:
            ROAD_Y[_i] = _pv
            _i += 1
            continue
        _j = _i
        while _j < len(ROAD_CENTRE) and _pin(*ROAD_CENTRE[_j]) is None:
            _j += 1
        # free run [_i, _j): pinned to the level behind it, and it has to land on the level
        # in front of it, so it is a ramp rather than an open staircase.
        _y0 = ROAD_Y[_i - 1] if _i else _ry[_i]
        _y1 = ROAD_Y[_j] if _j < len(ROAD_CENTRE) else _ry[_j - 1]
        _free = _j - _i
        _prof = staircase([_ry[_k] for _k in range(_i, _j)], _y0)
        # Close the last few columns onto the level in front -- but only when there IS a
        # level in front. A run that ends at the end of the road has nothing to meet, and
        # forcing it onto the raw terrain height of its last column is what put three
        # one-block steps on consecutive columns at the plaza kerb.
        _tail = 0
        if _free and _j < len(ROAD_CENTRE):
            _tail = min(_free, max(4, abs(_y1 - _prof[-1]) * (ROAD_RUN + 1) + 1))
        if _tail:
            _prof[_free - _tail:] = ramp(_tail, _prof[_free - _tail], _y1)
        for _k in range(_i, _j):
            ROAD_Y[_k] = _prof[_k - _i]
        _i = _j
    _bad = [(i, ROAD_Y[i] - ROAD_Y[i - 1]) for i in range(1, len(ROAD_Y))
            if abs(ROAD_Y[i] - ROAD_Y[i - 1]) > 1]
    if _bad:
        print('  WARNING: lantern road steps more than a block at %s' % _bad[:6])

    ROAD_CMDS = ['# the lantern road: spawn -> farm gate -> town square, %d columns.'
                 % len(ROAD_CENTRE)]
    ROAD_CELLS = set()
    for _i, (_x, _z) in enumerate(ROAD_CENTRE):
        _y = ROAD_Y[_i]
        # local direction, so the 3-wide brush is always across the road
        _j = min(_i + 1, len(ROAD_CENTRE) - 1)
        _k = max(_i - 1, 0)
        _dx = ROAD_CENTRE[_j][0] - ROAD_CENTRE[_k][0]
        _dz = ROAD_CENTRE[_j][1] - ROAD_CENTRE[_k][1]
        _px, _pz = (0, 1) if abs(_dx) >= abs(_dz) else (1, 0)
        for _o in (-1, 0, 1):
            _cx, _cz = _x + _px * _o, _z + _pz * _o
            ROAD_CELLS.add((_cx, _cz))
            # the road IS part of the design surface: the skirt in 11.6 grades the meadow
            # up to its shoulders instead of leaving it standing on an embankment.
            LEVEL.setdefault((_cx - ANCHOR_W[0], _cz - ANCHOR_W[2]), _y - ANCHOR_W[1])
            # Sixteen, not five. `road_steps` reads the road's own surface, and the surface
            # of a column with a spruce standing over it is the spruce: the built road had a
            # "6-block step" at -305,36 that was a tree the five-block clear had cut off at
            # the ankles and left hanging.
            ROAD_CMDS.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                             % (_cx, _y + 1, _cz, _cx, _y + 16, _cz))
            ROAD_CMDS.append('setblock ~%d ~%d ~%d %s'
                             % (_cx, _y, _cz,
                                'minecraft:dirt_path' if _o == 0 else 'minecraft:gravel'))
            # backfill: never leave the road hanging over a hole it just stepped down to
            ROAD_CMDS.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:dirt replace minecraft:air'
                             % (_cx, _y - 4, _cz, _cx, _y - 1, _cz))

    # ---- lamp posts on the road, every 6 blocks, BOTH sides -----------------
    ROAD_LAMPS = []
    for _i in range(6, len(ROAD_CENTRE) - 4, 6):
        _x, _z = ROAD_CENTRE[_i]
        _y = ROAD_Y[_i]
        _j = min(_i + 1, len(ROAD_CENTRE) - 1)
        _dx = ROAD_CENTRE[_j][0] - ROAD_CENTRE[_i - 1][0]
        _dz = ROAD_CENTRE[_j][1] - ROAD_CENTRE[_i - 1][1]
        _px, _pz = (0, 1) if abs(_dx) >= abs(_dz) else (1, 0)
        for _side in (-2, 2):
            _cx, _cz = _x + _px * _side, _z + _pz * _side
            _cy = dsurf(_cx, _cz)
            if abs(_cy - _y) > 2:
                _cy = _y
            ROAD_LAMPS.append([_cx, _cy + 1, _cz])

    # =========================================================================
    # The forty lamp posts.
    #
    # The brief asks for two things that do not both fit: "unlit lamp posts every 6 blocks
    # both sides" of a road that is ~160 columns long (that is 52 posts by itself), and
    # "exactly forty lamp posts total across road and streets". Forty is the number the
    # story counts -- `/valley lamps` says "of 40", Q34 and Q74 light routes out of it, and
    # Q90's fortieth post is the one on Josie's own porch -- so forty wins, and the road's
    # spacing is what gives. The road gets EIGHT stations, posts on BOTH sides of each, laid
    # out evenly along the whole route; the town keeps its plaza corners, its High Street
    # head and its street verges. 4 + 2 + 16 + 18 = 40, and every post that exists is one a
    # quest can light.
    # =========================================================================
    ROAD_STATIONS = 8
    ROAD_LAMPS = []
    _lo, _hi = 8, len(ROAD_CENTRE) - 10
    for _s in range(ROAD_STATIONS):
        _i = int(round(_lo + (_hi - _lo) * (_s + 0.5) / ROAD_STATIONS))
        _i = max(1, min(len(ROAD_CENTRE) - 2, _i))
        _x, _z = ROAD_CENTRE[_i]
        _dx = ROAD_CENTRE[_i + 1][0] - ROAD_CENTRE[_i - 1][0]
        _dz = ROAD_CENTRE[_i + 1][1] - ROAD_CENTRE[_i - 1][1]
        _px, _pz = (0, 1) if abs(_dx) >= abs(_dz) else (1, 0)
        for _side in (-2, 2):
            _cx, _cz = _x + _px * _side, _z + _pz * _side
            _cy = dsurf(_cx, _cz)
            if abs(_cy - ROAD_Y[_i]) > 2:
                _cy = ROAD_Y[_i]
            ROAD_LAMPS.append([_cx, _cy + 1, _cz])
            LEVEL.setdefault((_cx - ANCHOR_W[0], _cz - ANCHOR_W[2]), _cy - ANCHOR_W[1])

    # street posts, anchor-relative -> absolute, trimmed to 18
    _street_rel = (LAMPS['q34'] + LAMPS['q74'])[:18]
    STREET_LAMPS = []
    for _p in _street_rel:
        _cx, _cz = ANCHOR_W[0] + _p[0], ANCHOR_W[2] + _p[2]
        STREET_LAMPS.append([_cx, dsurf(_cx, _cz) + 1, _cz])
    PLAZA_LAMPS = [[ANCHOR_W[0] + p[0], dsurf(ANCHOR_W[0] + p[0], ANCHOR_W[2] + p[2]) + 1,
                    ANCHOR_W[2] + p[2]] for p in LAMPS['finale']]
    Q07_LAMPS = [[ANCHOR_W[0] + p[0], dsurf(ANCHOR_W[0] + p[0], ANCHOR_W[2] + p[2]) + 1,
                  ANCHOR_W[2] + p[2]] for p in LAMPS['q07']]

    # lighting order 1..40: the plaza she is standing in, the road head, out along the
    # lantern road toward home, then the streets.
    LAMPS_40 = PLAZA_LAMPS + Q07_LAMPS + ROAD_LAMPS + STREET_LAMPS
    assert len(LAMPS_40) == 40, 'lamp registry is %d, not 40' % len(LAMPS_40)

    LAMP_CMDS = ['# forty unlit lamp posts. `setblock <LAMP_LIT>` is the whole of lighting one.']
    for _i, _p in enumerate(LAMPS_40):
        LAMP_CMDS.append('setblock ~%d ~%d ~%d minecraft:cobblestone' % (_p[0], _p[1] - 1, _p[2]))
        LAMP_CMDS.append('setblock ~%d ~%d ~%d %s' % (_p[0], _p[1], _p[2], POST))
        LAMP_CMDS.append('setblock ~%d ~%d ~%d %s' % (_p[0], _p[1] + 1, _p[2], LAMP_DARK))

    # =========================================================================
    # The spawn signpost. Three blocks along the road from where she stands, so the
    # first thing in frame is a direction, not a quest card.
    # =========================================================================
    # Three blocks along, but OUTSIDE the plaza: spawn is 14 blocks from the anchor, so a
    # naive "index 3" put the signpost inside the square, where act1_square's paving and the
    # Handcrafted furniture then stood on top of it (the built world had a chair there and no
    # sign). Walk out along the road until the column is clear of both pads.
    _sp_i = None
    for _i in range(3, len(ROAD_CENTRE) - 6):
        _x, _z = ROAD_CENTRE[_i]
        if _pin(_x, _z) is None:
            _sp_i = _i
            break
    if _sp_i is None:
        _sp_i = min(3, len(ROAD_CENTRE) - 1)
    _sx, _sz = ROAD_CENTRE[_sp_i]
    SIGNPOST = [_sx + 2, dsurf(_sx + 2, _sz) + 1, _sz]
    SIGN_CMDS = [
        'setblock ~%d ~%d ~%d minecraft:cobblestone' % (SIGNPOST[0], SIGNPOST[1] - 1, SIGNPOST[2]),
        'setblock ~%d ~%d ~%d %s' % (SIGNPOST[0], SIGNPOST[1], SIGNPOST[2], POST),
        'setblock ~%d ~%d ~%d minecraft:oak_sign[rotation=8]{front_text:{messages:['
        '\'{"text":"KETTLE FARM"}\',\'{"text":"follow the road"}\',\'{"text":""}\','
        '\'{"text":"LITTLE KETTLE"}\'],color:"gray"}}'
        % (SIGNPOST[0], SIGNPOST[1] + 1, SIGNPOST[2]),
        'setblock ~%d ~%d ~%d minecraft:lantern[hanging=false]'
        % (SIGNPOST[0] - 1, SIGNPOST[1], SIGNPOST[2]),
    ]

    # =========================================================================
    # The cottage, standing, with the gaps Q3 fills.
    #
    # cot_lines already takes the template's own door, glass panes and bed back out (Q3
    # hangs them). Day one adds: a 2x2 hole in the roof, a COLD campfire on the hearth,
    # and no waystone -- Q2 still places that herself on the bare hearthstone, which is the
    # one meaningful first action the pack has, and it now changes nothing but the block
    # she is holding.
    #
    # The roof patch is READ OFF the template: the highest solid cells over the interior,
    # kept clear of the chimney column so the chimney still stands.
    # =========================================================================
    _roof = [(x, y, z) for (x, y, z), b in cg.items()
             if b[0] not in ('minecraft:air',) and y >= csz[1] - 3]
    _chim = None
    for (x, y, z), b in cg.items():
        if 'brick' in b[0] or 'cobblestone' in b[0]:
            if _chim is None or y > _chim[1]:
                _chim = (x, y, z)
    _cands = sorted(_roof, key=lambda p: (-p[1],
                    -((p[0] - _chim[0]) ** 2 + (p[2] - _chim[2]) ** 2) if _chim else 0))
    ROOF_PATCH = None
    for (rx, ry, rz) in _cands:
        cells = [(rx + a, ry, rz + b) for a in (0, 1) for b in (0, 1)]
        if all(c in cg and cg[c][0] != 'minecraft:air' for c in cells):
            if _chim and min(abs(c[0] - _chim[0]) + abs(c[2] - _chim[2]) for c in cells) < 2:
                continue
            ROOF_PATCH = (rx, ry, rz)
            break
    if ROOF_PATCH is None:
        ROOF_PATCH = (_cands[0][0], _cands[0][1], _cands[0][2])

    # template-local -> home-relative
    def _c2h(p):
        return (COT_MIN[0] + p[0], COT_MIN[1] + p[1], COT_MIN[2] + p[2])

    _rp = _c2h(ROOF_PATCH)
    ROOF_HOLE_HOME = [_rp[0], _rp[1], _rp[2]]

    # the day-one cottage group: cot_lines minus the waystone, minus the flavour line,
    # with the hard level replaced by @pad (feathered, material-sampled) and the roof
    # patch and cold campfire added.
    DAY1_COTTAGE = []
    for _c in cot_lines:
        if _c.startswith('#') or _c == '':
            DAY1_COTTAGE.append(_c); continue
        if 'waystones:waystone' in _c:
            DAY1_COTTAGE.append('# (no waystone: Q2 places Home on the bare hearthstone herself)')
            continue
        if _c.startswith('tellraw') or _c.startswith('playsound') or _c.startswith('title'):
            continue
        if _c.startswith('fill ~-11 ~0 ~-14') or _c.startswith('fill ~-11 ~-4 ~-14') \
                or _c.startswith('fill ~-11 ~-2 ~-14') or _c.startswith('fill ~-11 ~-1 ~-14 ~11 ~-1 ~11 minecraft:grass_block'):
            continue
        DAY1_COTTAGE.append(_c)
    DAY1_COTTAGE = ([
        '# The cottage yard. The LEVELLED part is the house, the seed bed, the pen, the porch',
        '# and the gate, and nothing else. The old pad was the whole 23 x 26 registry box at',
        '# one Y -- the 26-block straight cut edge nature_check kept failing on. Everything',
        '# outside it is skirt, graded back to the meadow a block a ring by day1_grade_farm,',
        '# so the yard ends where the hillside catches up with it and not on a line.',
        '@pad ~%d ~-1 ~%d ~%d ~-1 ~%d 16 4 minecraft:grass_block'
        % (COT_FLAT[0], COT_FLAT[1], COT_FLAT[2], COT_FLAT[3]),
    ] + DAY1_COTTAGE + [
        '',
        '# the gaps Q3 fills. The door, the two window panes and the bed are already out',
        '# (the `replace` fills above); this is the hole in the roof.',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
        % (ROOF_HOLE_HOME[0], ROOF_HOLE_HOME[1], ROOF_HOLE_HOME[2],
           ROOF_HOLE_HOME[0] + 1, ROOF_HOLE_HOME[1], ROOF_HOLE_HOME[2] + 1),
        '# a cold hearth, and the hearthstone bare for Q2',
        'setblock ~0 ~-1 ~0 minecraft:polished_andesite',
        'setblock ~0 ~0 ~0 minecraft:air',
        'setblock ~-1 ~0 ~0 minecraft:campfire[lit=false]',
        '# the gate at the end of the road, unchanged from the ruin: this is still the',
        '# marker that says you have arrived.',
        '# ...beside the road, not in it. The lantern road arrives along z = home+8 and its',
        '# three-block brush covers z = home+7..9, so a post anywhere on that line is a',
        '# two-block step at the very end of the road. It stands one clear of the verge.',
        'setblock ~0 ~0 ~10 minecraft:oak_fence',
        'setblock ~0 ~1 ~10 minecraft:oak_sign[rotation=8]{front_text:{messages:['
        '\'{"text":"KETTLE FARM"}\',\'{"text":""}\',\'{"text":"J. Kettle"}\','
        '\'{"text":"mind the weeds"}\'],color:"gray"}}',
    ])

    group('day1_cottage', 'home', DAY1_COTTAGE)
    group('day1_lamps', 'world', LAMP_CMDS)
    group('day1_signpost', 'world', SIGN_CMDS)

    # =========================================================================
    # 11.6  THE SKIRT.  Walking the design surface back to the land.
    #
    # Everything above decided a level for the columns the plan BUILDS on: the plaza, the
    # pads, the streets, the aprons, the lantern road, the cottage yard. This is what
    # happens at their edges. A multi-source flood outward from every built column; each
    # ring may move one block toward the natural surface, and a column STOPS the moment it
    # reaches it. Two things fall out of that and they are the whole point:
    #
    #   * no two adjacent columns anywhere in a skirt differ by more than one block, so
    #     there is no exposed face to cover -- `stone_face` has nothing to find; and
    #   * the outer boundary of the skirt is wherever the hillside happened to catch up,
    #     which is a different distance on every column. It cannot be a straight line,
    #     because nothing draws it.
    #
    # Columns standing in water are left alone: the lake keeps its shore.
    # =========================================================================
    _NB8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def build_skirt():
        """The skirt, solved rather than swept.

        The first two attempts were single outward passes, and both of them left cliffs:
        stop the flood where the land catches up and the natural step behind it never gets
        seen (the mill's six-block face); let it carry on and a column that has already met
        the land three rings away becomes a NEIGHBOUR of the ramp coming off a pad, drags it
        straight down to the ground in one step, and you get the church standing on a
        seven-block wall. Both are the same mistake: a single pass decides a column's level
        from whichever neighbour happened to be visited first.

        So it is relaxed to a fixed point instead. Every column within SKIRT_RINGS of
        anything the plan builds on starts at the natural surface; the built columns are
        pinned; and then the whole field is swept until no column is more than one block
        from any of its eight neighbours. The result is the flattest surface that (a) holds
        every terrace exactly, (b) never steps more than a block anywhere, and (c) is the
        natural ground wherever it can be -- which is most of it: the sweep touches forty
        thousand columns and writes about two thousand.
        """
        pinned = dict(LEVEL)
        field = dict(LEVEL)
        # everything within reach of the plan
        frontier = set(LEVEL)
        for _ring in range(SKIRT_RINGS):
            nxt = set()
            for (x, z) in frontier:
                for dx, dz in _NB8:
                    c = (x + dx, z + dz)
                    if c in field:
                        continue
                    if wet(c[0], c[1]):
                        continue
                    w = surface(ANCHOR_W[0] + c[0], ANCHOR_W[2] + c[1])
                    if w is None:
                        continue
                    field[c] = w - ANCHOR_W[1]
                    nxt.add(c)
            frontier = nxt
            if not frontier:
                break
        free = [c for c in field if c not in pinned]
        nat_of = {c: field[c] for c in free}
        order = sorted(free)
        for _sweep in range(60):
            moved = 0
            seq = order if _sweep % 2 == 0 else order[::-1]
            for c in seq:
                nb = [field[q] for q in ((c[0] + dx, c[1] + dz) for dx, dz in _NB8)
                      if q in field]
                if not nb:
                    continue
                lo = max(nb) - 1
                hi = min(nb) + 1
                n = nat_of[c]
                # A column may hold its terrace's level for a ring or two before it starts
                # down: that is the feathering, and it is what stops the edge of a pad being
                # a straight line in plan. It is a floor on the level, never a ceiling, so it
                # can never make a step taller.
                if hold_depth(c[0], c[1]) and max(nb) > n:
                    n = min(max(nb), n + hold_depth(c[0], c[1]))
                y = n if lo <= hi else (lo + hi) // 2
                y = max(lo, min(hi, y)) if lo <= hi else y
                if y != field[c]:
                    field[c] = y
                    moved += 1
            if not moved:
                break
        return {c: field[c] for c in free if field[c] != nat_of[c]}

    SKIRT = build_skirt()

    def grade_cmds(cells):
        """Row runs, in world coordinates. One `fill` per run of columns at the same level
        in the same material rather than three commands a column: the skirt is thousands of
        columns and town_plan.js is read by KubeJS on every server start."""
        rows = {}
        for (x, z), y in cells.items():
            rows.setdefault(z, {})[x] = y
        out = []
        for z in sorted(rows):
            row = rows[z]
            xs = sorted(row)
            i = 0
            while i < len(xs):
                y = row[xs[i]]
                mat = surf_mat(ANCHOR_W[0] + xs[i], ANCHOR_W[2] + z)
                j = i
                while (j + 1 < len(xs) and xs[j + 1] == xs[j] + 1 and row[xs[j + 1]] == y
                       and surf_mat(ANCHOR_W[0] + xs[j + 1], ANCHOR_W[2] + z) == mat):
                    j += 1
                x0, x1 = xs[i], xs[j]
                lo = min(nat(x, z) for x in range(x0, x1 + 1))
                hi = max(nat(x, z) for x in range(x0, x1 + 1))
                WX0, WX1 = ANCHOR_W[0] + x0, ANCHOR_W[0] + x1
                WZ, WY = ANCHOR_W[2] + z, ANCHOR_W[1] + y
                out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                           % (WX0, WY + 1, WZ, WX1, max(WY + 4, ANCHOR_W[1] + hi + 10), WZ))
                out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d %s'
                           % (WX0, WY, WZ, WX1, WY, WZ, mat))
                if y - 1 >= lo:
                    out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:dirt replace minecraft:air'
                               % (WX0, ANCHOR_W[1] + lo, WZ, WX1, WY - 1, WZ))
                i = j + 1
        return out

    # The grading ships INSIDE day1_road, ahead of the paving. Two reasons, and the second
    # is the one that decided it:
    #
    #   * it is the same job. The road is the valley's ground floor: the columns it lays and
    #     the columns that walk back from it to the meadow are one continuous surface, and
    #     splitting them into two groups only means two forceloads over the same chunks.
    #   * `/valley build all` runs BUILD_ORDER, a list in valley_finales.js. A new group key
    #     is not in it, is not built, and says nothing about it -- which is exactly what
    #     happened the first time this ran: 29 of 29 groups built, every grading band
    #     silently skipped, and the probes reported a world with no skirt on it. Folding the
    #     grading into a key BUILD_ORDER already carries means the shipped world cannot be
    #     rebuilt without it.
    #
    # It goes first inside the group because the road's own columns are excluded from the
    # skirt by construction (every built column is in LEVEL), so nothing here can touch the
    # paving, and putting it in front keeps the sequence readable: ground, then road.
    GRADE_CMDS = (['# the skirt: %d columns walked back from the plan to the land.' % len(SKIRT)]
                  + grade_cmds(SKIRT))
    group('day1_road', 'world', GRADE_CMDS + ROAD_CMDS)
    print('  skirt: %d columns graded back to the land, %d commands, inside day1_road'
          % (len(SKIRT), len(GRADE_CMDS)))

    RUN_ORDER[:0] = ['day1_road', 'day1_cottage', 'day1_signpost']
    RUN_ORDER.append('day1_lamps')

    # =========================================================================
    # valley_sites.json -- THE fixed registry.
    #
    # Step 4 of docs/transitions-design.md: "Publish a fixed site registry ... rip out
    # runtime anchoring". Everything the pack used to derive at runtime from a stake the
    # player planted is a constant in here, in world coordinates, computed once from the
    # master world. Read it, never re-derive it.
    # =========================================================================
    def W(off, base):
        return [base[0] + off[0], base[1] + off[1], base[2] + off[2]]

    _buildings, _doors, _site_boxes = {}, {}, {}
    for _n, _p in P.items():
        _d = _p.doors()
        _pdy = PAD_DY.get(_n, 0)
        _rec = {
            'template': _p.tid, 'rotation': ROTS[_p.r], 'act': META[_n]['act'],
            'label': META[_n]['label'],
            # `level` is the terrace this building stands on: the median natural surface
            # under its own footprint, in world Y. Everything else in the record is
            # measured from it.
            'level': ANCHOR_W[1] + _pdy,
            'origin': W([_p.ox, _p.oy + _pdy, _p.oz], ANCHOR_W),
            'footprint': {'x': [ANCHOR_W[0] + _p.x0, ANCHOR_W[0] + _p.x1],
                          'z': [ANCHOR_W[2] + _p.z0, ANCHOR_W[2] + _p.z1]},
            'pad': [ANCHOR_W[0] + _p.pad()[0], ANCHOR_W[2] + _p.pad()[1],
                    ANCHOR_W[0] + _p.pad()[2], ANCHOR_W[2] + _p.pad()[3]],
        }
        if _d:
            _rec['door'] = W([_d[0]['pos'][0], _d[0]['pos'][1] + _pdy, _d[0]['pos'][2]],
                             ANCHOR_W)
            _rec['door_facing'] = _d[0]['facing']
            _doors[_n] = _rec['door']
        _buildings[_n] = _rec
        _site_boxes[_n] = _rec['pad']
    for _n, _r in CX.items():
        _buildings[_n] = {
            'custom': True, 'act': META[_n]['act'], 'label': META[_n]['label'],
            'level': ANCHOR_W[1] + PAD_DY.get(_n, 0),
            'footprint': {'x': [ANCHOR_W[0] + _r[0], ANCHOR_W[0] + _r[2]],
                          'z': [ANCHOR_W[2] + _r[1], ANCHOR_W[2] + _r[3]]},
        }
        _site_boxes[_n] = [ANCHOR_W[0] + _r[0], ANCHOR_W[2] + _r[1],
                           ANCHOR_W[0] + _r[2], ANCHOR_W[2] + _r[3]]
    _site_boxes['plaza'] = [ANCHOR_W[0] - PLAZA, ANCHOR_W[2] - PLAZA,
                            ANCHOR_W[0] + PLAZA, ANCHOR_W[2] + PLAZA]
    _site_boxes['cottage_plot'] = [HEARTH_W[0] - 11, HEARTH_W[2] - 14,
                                   HEARTH_W[0] + 11, HEARTH_W[2] + 11]
    _doors['cottage'] = None

    # She stands on the road, and the road is a staircase now: read the level the plan
    # actually gave that column rather than trusting the number the site solver guessed.
    SPAWN_W[1] = dsurf(SPAWN_W[0], SPAWN_W[2]) + 1

    HOME_W = [HEARTH_W[0], HEARTH_W[1] + 1, HEARTH_W[2]]

    # ---- the Works, re-verified against the groups section 11 could not see ------------
    # Section 11's replay runs before day one exists, and its shift arithmetic only knows
    # anchor- and works-relative groups. The grading bands, the road, the lamps and the
    # cottage are 'world'- and 'home'-relative, they dig, and the East Lane runs six blocks
    # over the Works ceiling. So they get their own pass, in world coordinates.
    _WBW = (ANCHOR_W[0] + WORKS_BOX[0], ANCHOR_W[1] + WORKS_BOX[1], ANCHOR_W[2] + WORKS_BOX[2],
            ANCHOR_W[0] + WORKS_BOX[3], ANCHOR_W[1] + WORKS_BOX[4], ANCHOR_W[2] + WORKS_BOX[5])
    _seal_i = RUN_ORDER.index('act4_works')
    _day1_hits = 0
    for _i2, _k2 in enumerate(RUN_ORDER):
        _g2 = GROUPS.get(_k2)
        if not _g2 or _g2['origin'] not in ('world', 'home'):
            continue
        _base = [0, 0, 0] if _g2['origin'] == 'world' else HOME_W
        for _c2 in _g2['cmds']:
            for _b2 in write_boxes(_c2):
                _wb2 = (_b2[0] + _base[0], _b2[1] + _base[1], _b2[2] + _base[2],
                        _b2[3] + _base[0], _b2[4] + _base[1], _b2[5] + _base[2])
                _n2 = overlap_cells(_wb2, _WBW)
                if not _n2:
                    continue
                if _i2 < _seal_i:
                    _day1_hits += _n2
                else:
                    errors.append('%s writes %d cell(s) of the sealed Works shell: %s'
                                  % (_k2, _n2, _c2[:96]))
    # The shell has to be UNDER GROUND with a roof of real rock on it, not a stone-brick
    # ceiling flush with a meadow.
    _cover = []
    for _wx in range(_WBW[0], _WBW[3] + 1):
        for _wz in range(_WBW[2], _WBW[5] + 1):
            _cover.append(dsurf(_wx, _wz) - _WBW[4])
    print('  works shell y %d..%d, cover above the ceiling: %d..%d blocks (day-one groups '
          'wrote %d cell(s) into it before act4_works seals it, which is fine)'
          % (_WBW[1], _WBW[4], min(_cover), max(_cover), _day1_hits))
    if min(_cover) < 1:
        errors.append('the Works ceiling breaks the surface: only %d block(s) of cover'
                      % min(_cover))
    _cot_door = None
    for (x, y, z), b in cg.items():
        if b[0].endswith('_door') and b[1] and b[1].get('half') == 'lower':
            _cot_door = _c2h((x, y, z)); break
    _cot_win = []
    for (x, y, z), b in sorted(cg.items()):
        if 'glass_pane' in b[0]:
            _cot_win.append(_c2h((x, y, z)))
    if _cot_door:
        _doors['cottage'] = W(_cot_door, HOME_W)

    SITES_JSON = {
        '_read_me': (
            'Little Kettle Valley -- THE fixed site registry. GENERATED by '
            'tools/scripts/plan_town.py --site, from the chosen seed\'s master world. Every '
            'coordinate is ABSOLUTE and never changes: the world is shipped, so there is '
            'nothing left to derive at runtime. See docs/transitions-design.md step 4.'),
        'seed': SITE['seed'],
        'spawn': SPAWN_W,
        'hearth': HEARTH_W,
        'home_waystone': HOME_W,
        'anchor': ANCHOR_W,
        'cottage': {
            'template': COTTAGE,
            'place_origin': W(COT_MIN, HOME_W),
            'hearthstone': HEARTH_W,
            'door': _doors.get('cottage'),
            'windows': [W(p, HOME_W) for p in _cot_win],
            'roof_patch': [W(ROOF_HOLE_HOME, HOME_W),
                           W([ROOF_HOLE_HOME[0] + 1, ROOF_HOLE_HOME[1], ROOF_HOLE_HOME[2] + 1], HOME_W)],
            'bed': W([-1, -1, -1], HOME_W),
            'gate_sign': W([0, 1, 10], HOME_W),
            'porch': W([3, 0, 0], HOME_W),
        },
        'plaza': _site_boxes['plaza'],
        'site_boxes': _site_boxes,
        'buildings': _buildings,
        'doors': {k: v for k, v in _doors.items() if v},
        'lamps': [{'n': i + 1, 'pos': p,
                   'route': ('finale' if i < 4 else 'q07' if i < 6 else
                             'q34' if i < 22 else 'q74')}
                  for i, p in enumerate(LAMPS_40)],
        # The road's own columns, MINUS the ones inside the square. The lantern road is laid
        # from spawn to the farm gate and it crosses the plaza on the way, but inside the
        # plaza the ground is the plaza: it is paved by act1_square, and the well, the four
        # market carts, the flower boxes and the noticeboard all stand on it. Calling those
        # columns "road" makes the square's own furniture read as steps in a road, which is
        # what the first terraced build reported. Both ends of the gap are plaza kerb at the
        # same level, so the path stays continuous where it matters.
        'road_path': [[x, ROAD_Y[i], z] for i, (x, z) in enumerate(ROAD_CENTRE)
                      if not (ANCHOR_W[0] - PLAZA <= x <= ANCHOR_W[0] + PLAZA
                              and ANCHOR_W[2] - PLAZA <= z <= ANCHOR_W[2] + PLAZA)],
        'signpost': SIGNPOST,
        'pier': W(OFF['lake'], ANCHOR_W),
        'lake_centre': [SITE['lake_centre'][0], SITE.get('lake_surface_y', HEARTH_W[1]),
                        SITE['lake_centre'][1]],
        'works': {
            'mark': W(OFF['works'], ANCHOR_W),
            'lever': W(plan_lever, ANCHOR_W) if False else None,
        },
        'marks': {k: W(v, ANCHOR_W) for k, v in OFF.items()},
        'npc_homes': {},
        'npc_stands': [],
    }
    _wm = SITES_JSON['marks']['works']
    SITES_JSON['works']['lever'] = W(LEVER, _wm)
    SITES_JSON['works']['panel'] = W(PANEL, _wm)
    SITES_JSON['works']['door'] = W([0, 1, -6], _wm)
    SITES_JSON['works']['shell'] = [
        _wm[0] + WORKS_SHELL['x'][0], _wm[1] + WORKS_SHELL['y'][0], _wm[2] + WORKS_SHELL['z'][0],
        _wm[0] + WORKS_SHELL['x'][1], _wm[1] + WORKS_SHELL['y'][1], _wm[2] + WORKS_SHELL['z'][1]]
    SITES_JSON['cellar_door'] = [HOME_W[0], HOME_W[1] - 6, HOME_W[2]]
    for _sp in NPC_SPOTS:
        _base = ANCHOR_W if _sp['origin'] == 'anchor' else (
            HOME_W if _sp['origin'] == 'home' else W(OFF.get(_sp['origin'], [0, 0, 0]), ANCHOR_W))
        SITES_JSON['npc_stands'].append({'group': _sp['group'], 'pos': W(_sp['pos'], _base)})
    for _n, _rec in _buildings.items():
        if 'door' in _rec:
            SITES_JSON['npc_homes'][_n] = _rec['door']


# =============================================================================
# 12. Output
# =============================================================================
def jrec(name, p):
    d = p.doors()
    return {
        'template': p.tid, 'rotation': ROTS[p.r], 'size': p.size,
        'footprint': {'x': [p.x0, p.x1], 'z': [p.z0, p.z1], 'y': [p.y0, p.y1]},
        'pad': list(p.pad()), 'place_origin': [p.ox, p.oy, p.oz],
        'door': d[0] if d else None, 'act': META[name]['act'],
        'label': META[name]['label'], 'blurb': META[name]['blurb'],
    }


plan = {
    '_read_me': (
        'Little Kettle Valley town plan. Anchor-relative [dx,dy,dz]; dy=0 is the levelled '
        'pad top course and everything stands at dy=1. GENERATED by tools/scripts/plan_town.py '
        'from the installed template NBTs - re-run it, never hand-edit, and re-run it after '
        'any change to BUILDINGS/STREETS/RESERVED in that script. The same run writes '
        'pack/kubejs/server_scripts/town_plan.js, which is the file the pack actually reads.'),
    'style': {
        'primary_set': 'Towns and Towers - meadow_swiss (kaisyn)',
        'fallbacks': 'Towns and Towers - exclusives/classic (church, library, well, farms)',
        'inn': 'Dungeons and Taverns - tavern/tavern_house_spruce (the only standalone tavern piece)',
        'starting_ruin': 'Dungeons and Taverns - wild_ruin/wild_ruin_23 (self-contained, has a furnace)',
        'works_interior': 'Dungeons and Taverns - bunker/* inside the sealed Works shell',
        'cross_set_borrows_needing_sign_off': [
            {'slot': 'mill', 'template': BUILDINGS[1][1],
             'why': 'the only real windmill in any installed pack; sunflower_plains_farm set, '
                    'oak/spruce palette, reads rustic-Swiss',
             'in_style_alternate': 'kaisyn:village/meadow_swiss/houses/meadow_farmer_1'},
            {'slot': 'granary', 'template': BUILDINGS[4][1],
             'why': 'neither meadow_swiss nor classic has a barn; rustic is spruce + brick trim',
             'in_style_alternate': 'kaisyn:village/meadow_swiss/houses/meadow_shepherd_1'},
        ],
        'custom_builds': ['greenhouse', 'bathhouse',
                          'the Town Square paving, kerb and streets',
                          'the Harvest Supper table (Handcrafted furniture, not a template)'],
    },
    'ground_rules': {
        'pad': 'clear dy1..h air, dirt dy-%d..-2, coarse_dirt dy-1, top course dy0' % PAD_DEEP,
        'template_y': 'every chosen template has its walkable floor at local y=y_base, so the '
                      'place origin is dy = -y_base and the floor lands on the pad top course',
        'markers': 'jigsaw blocks are cleared; Towns-and-Towers cyan_concrete street markers are '
                   'replaced with the gravel/stone_brick mix kaisyn:village/street_meadow produces',
        'apron': 'every door gets a 3-wide cobble/gravel apron routed to the nearest paving, '
                 'and a lantern on a post beside it',
    },
    'square': {
        'plaza': [-PLAZA, -PLAZA, PLAZA, PLAZA],
        'waystone': [0, 1, 0], 'noticeboard': [0, 1, -5], 'signpost': [0, 1, -3],
        'well_top': [WELL_X, 0, WELL_Z], 'well_bottom': [WELL_X + 1, -10, WELL_Z + 1],
        'market_carts': [{'template': MARKET_CARTS[i], 'min': [c[0], 1, c[1]]}
                         for i, c in enumerate(CART_POS)],
        'supper_table': {'x': [-4, 4], 'z': [-11, -9]},
        'stands': PLAZA_STANDS[:24],
        'supper_seats': SUPPER_SEATS,
        # The cells the three square scenes stand on, solved against every
        # occupant above. valley_finales.js reads these rather than carrying
        # its own copy of where the carts used to be.
        'scenes': {
            'ribbit_camp': {'stands': RIBBIT_STANDS, 'campfire': RIBBIT_FIRE,
                            'post': RIBBIT_POST},
            'still': STILL,
            'harvest': {'hay': HARVEST_HAY, 'pumpkins': HARVEST_PUMPKIN},
        },
    },
    'streets': [{'name': n, 'centre': [list(p) for p in pts], 'width': 2 * ROAD_BRUSH + 1}
                for n, pts in STREETS],
    'buildings': {n: jrec(n, p) for n, p in P.items()},
    'custom': {n: {'footprint': {'x': [r[0], r[2]], 'z': [r[1], r[3]]},
                   'act': META[n]['act'], 'label': META[n]['label'], 'blurb': META[n]['blurb']}
               for n, r in CX.items()},
    'works': {
        'mark': OFF['works'],
        'shell': {'x': [-6, 8], 'y': [-1, 4], 'z': [-6, 8]},
        'pieces': [{'name': n, 'template': tid, 'min': [mx, -1, mz]}
                   for n, tid, r, mx, mz in WORKS_PIECES],
        'lever': LEVER, 'panel': PANEL,
        'stands': works_stands,
        'lanterns': lantern_spots,
    },
    'ruin': {'template': RUIN, 'hearthstone_local': list(HEARTH_LOCAL),
             'place_offset_from_hearthstone': RUIN_MIN},
    'cottage': {'template': COTTAGE, 'hearthstone_local': list(COT_HEARTH),
                'place_offset_from_home': COT_MIN,
                'home_porch': [3, 0, 0],
                'overwrites': COT_OVERWRITES,
                'removed_ids': sorted(COT_REMOVED)},
    'marks_OFF': OFF,
    'lamp_routes': LAMPS,
    'probes': PROBES,
    'npc_spots': NPC_SPOTS,
    # The whole town, anchor-relative, and how far a homestead has to be from
    # it. valley_checks.js reads these two in the Q7 stake handler.
    'town_box': TOWN_BOX,
    'town_clearance': TOWN_CLEARANCE,
    # 3-D reservations and the group that seals each one. Everything after that
    # group in run_order must leave the box alone; the generator asserts it and
    # so does scratch/vt_check.py, off this file.
    'reservations_3d': [
        {'name': 'works_shell', 'sealed_by': 'act4_works', 'origin': 'works',
         'box': list(WORKS_BOX),
         'why': 'the Works is a sealed dry room six blocks down; a pad that digs '
                'to dy-10 through its wall floods it and washes the lever off'}],
    'run_order': RUN_ORDER,
    # cmds included so the write-set replay can be re-run independently
    'command_groups': {k: {'origin': g['origin'], 'bounds': g['bounds'],
                           'count': len(g['cmds']), 'cmds': g['cmds']}
                       for k, g in GROUPS.items()},
}
pathlib.Path('media/town_plan.json').write_text(json.dumps(plan, indent=1) + '\n')

# --- the JS the pack reads ----------------------------------------------------
js = [
    # KubeJS reads this header. It is load-bearing, and it is the reason the Works spent
    # three builds standing in a field: valley_core.js takes VALLEY.OFF from
    # global.valleyTownPlan when it exists and from a hand-typed fallback when it does not,
    # the comment above that fallback says town_plan.js is loaded first because "'t' sorts
    # before 'v'", and the server log says otherwise -- valley_core.js at 00:15:02.929,
    # town_plan.js at 00:15:02.953. Every mark in the pack was therefore coming from the
    # fallback. It agreed with the plan by luck until terracing moved the Works down nine
    # blocks to bury it, at which point act4_works built a fifteen-block stone-brick room
    # at the fallback's depth, breaking the surface under Pip's house. A priority is a
    # promise the loader keeps; alphabetical order is not.
    '// priority: 1000',
    '// town_plan.js -- GENERATED by tools/scripts/plan_town.py. DO NOT HAND-EDIT.',
    '//',
    '// The Little Kettle Valley town plan: every mark, every levelled pad, every',
    '// `place template` and every verification probe, computed from the installed',
    '// structure NBTs. The human-readable copy is media/town_plan.json.',
    '//',
    '// Loaded before every valley_*.js (KubeJS loads server_scripts alphabetically and',
    "// 't' sorts before 'v'), so valley_core.js can read VALLEY.OFF straight out of it.",
    '//',
    '// Command groups are lists of `~` offsets from the group\'s origin mark; runSeg()',
    '// in valley_finales.js resolves them against v.anchor() / v.mark(origin).',
    '',
    'global.valleyTownPlan = {',
    '  version: %d,' % 3,
    '  OFF: ' + json.dumps(OFF) + ',',
    '  square: ' + json.dumps(plan['square']) + ',',
    '  town_box: ' + json.dumps(TOWN_BOX) + ',',
    '  town_clearance: %d,' % TOWN_CLEARANCE,
    '  works: ' + json.dumps({k: plan['works'][k] for k in
                             ('shell', 'lever', 'panel', 'stands', 'lanterns')}) + ',',
    '  probes: ' + json.dumps(PROBES) + ',',
    '  npc_spots: ' + json.dumps(NPC_SPOTS) + ',',
    '  groups: {',
]
for k, g in GROUPS.items():
    js.append('    %s: { origin: %s, bounds: %s, cmds: [' % (k, json.dumps(g['origin']), json.dumps(g['bounds'])))
    for c in g['cmds']:
        js.append('      ' + json.dumps(c) + ',')
    js.append('    ] },')
js += ['  }', '}', '',
       "console.info('[valley] town_plan.js ok -- ' + Object.keys(global.valleyTownPlan.groups).length + ' build groups')",
       '']
pathlib.Path('pack/kubejs/server_scripts/town_plan.js').write_text('\n'.join(js))

fn = pathlib.Path('pack/kubejs/data/valley/functions')
(fn / 'setup').mkdir(parents=True, exist_ok=True)
(fn / 'act1').mkdir(parents=True, exist_ok=True)
(fn / 'setup' / 'place_ruin.mcfunction').write_text('\n'.join(ruin_lines) + '\n')
(fn / 'act1' / 'cottage.mcfunction').write_text('\n'.join(cot_lines) + '\n')
(fn / 'act1' / 'square_path.mcfunction').write_text('\n'.join(sp_lines) + '\n')

if SITES_JSON is not None:
    _sp = pathlib.Path('pack/kubejs/data/valley/valley_sites.json')
    _sp.parent.mkdir(parents=True, exist_ok=True)
    _sp.write_text(json.dumps(SITES_JSON, indent=1) + '\n')
    print('  valley_sites.json: seed %s, spawn %s, hearth %s, anchor %s, %d lamps, %d doors'
          % (SITES_JSON['seed'], SITES_JSON['spawn'], SITES_JSON['hearth'],
             SITES_JSON['anchor'], len(SITES_JSON['lamps']), len(SITES_JSON['doors'])))

if errors:
    # Section 11 raises on what it can see before day one is built. Everything the day-one
    # section adds -- the grading bands, the road, the re-measured Works -- reports here.
    for e in errors:
        print('ERROR ' + e)
    raise SystemExit(1)

total = sum(len(g['cmds']) for g in GROUPS.values())
print('town plan ok: %d buildings, %d custom, %d groups, %d commands, %d probes'
      % (len(P), len(CX), len(GROUPS), total, len(PROBES)))
for n, p in sorted(P.items()):
    print('  %-16s %-62s x %4d..%-4d z %4d..%-4d  %s'
          % (n, p.tid.split(':')[1], p.x0, p.x1, p.z0, p.z1, ROTS[p.r]))
for n, r in sorted(CX.items()):
    print('  %-16s %-62s x %4d..%-4d z %4d..%-4d' % (n, '(custom)', r[0], r[2], r[1], r[3]))
print('  marks: ' + json.dumps(OFF))
print('  inn chalk tiles: %s facing %s' % (inn_tiles, inn_face))
print('  inn door: %s' % inn.doors()[0])
