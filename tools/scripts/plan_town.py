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

# Cells a template ships that the town has to open, keyed by template id and given in the
# template's own LOCAL coordinates: {(x, y, z): the block that replaces it}.
#
# The meadow watchtower's two ground-floor doors each open into a small fenced forecourt
# that its own builder closed off with a fence at the far end -- fine for an outpost
# standing alone on a hill, and the reason `Placed.door_out` reported that the tallest
# building in the valley had no way out of either door and got no apron at all. The two
# closing rails become garden gates, standing open. They are taken out of the grid the
# door analysis reads AND replaced in the world, so the plan and the build agree.
TEMPLATE_OPEN = {
    'kaisyn:outpost/towers/meadow/base_plate': {
        (6, 6, 1): 'minecraft:oak_fence_gate[facing=north,open=true]',
        (6, 6, 11): 'minecraft:oak_fence_gate[facing=south,open=true]',
    },
}


class Placed(object):
    """A template pinned to an anchor-relative min corner."""

    def __init__(self, name, tid, r, minx, minz, y_base=0, margin=2):
        self.name, self.tid, self.r = name, tid, r
        t = template(tid)
        self.size = t['size']
        self.open_local = TEMPLATE_OPEN.get(tid, {})
        if self.open_local:
            self.grid = {k: v for k, v in t['blocks'].items() if k not in self.open_local}
        else:
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
        # A door BELOW the pad's top course is a door under the ground. The bell tower is
        # a 37-block outpost piece whose walkable floor is at local y6 -- it is placed with
        # y_base 6 so its threshold lands on the doorstep, which buries the service door
        # its rock plinth carries at local y4. Sorting on the lowest door found put the
        # front door two blocks under the lawn and the apron then paved a trench to it.
        # Doors at dy < 0 are dropped first; the ground-floor filter runs on what is left.
        above = [d for d in out if d['pos'][1] >= 0]
        if above:
            out = above
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
    #
    # 2026-09-05: both lanes are swung four blocks further out between z -16 and z -29.
    # They used to converge on +-13,-17 and pinch the north cluster to a corridor eleven
    # columns wide at its narrowest -- which is why the tallest piece in any installed jar
    # could not be put where the town's bell tower belongs: a 13x13 tower with its two-block
    # margin needs seventeen. Both routes still leave the plaza at +-8,-12 and still end
    # where they ended, and every whitelisted lamp post on them (+-10,-12 and +-14,-16)
    # still stands on the widened verge -- checked, not assumed: `lamps` in nature_check.py
    # walks all forty.
    ('north_east_lane',  [(8, -12), (12, -16), (15, -20), (15, -25), (12, -29)]),
    ('north_west_lane',  [(-8, -12), (-12, -16), (-17, -20), (-19, -24),
                          (-23, -27), (-27, -30)]),
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
    # 2026-09-05: swung out to x 58. It used to run at x 45, four columns off the east
    # end of the town, and with Marnie and Pip in real houses instead of the two 9x9
    # sheds there was no plot left between the North East Lane and this cart track.
    ('outcrop_road',     [(45, -12), (56, -22), (56, -40), (52, -46)]),
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
    # Marnie and Pip used to have the two 9x9 `meadow_small_house` boxes - the plainest
    # pieces in the whole set, a gable and two windows each, and the two buildings a
    # player meets FIRST. medium_house_5 carries a balcony (its second door is at local
    # y5) and a stone-brick plinth; medium_house_1 is the long-plan chalet with twelve
    # panes of window and a porch. Same neighbourhood, same palette, +2 and +4 blocks of
    # footprint, and both read as somebody's home rather than as a shed.
    ('marnie_house', 'kaisyn:village/meadow_swiss/houses/meadow_medium_house_5',   0, (20, -34), 2, 'act1', 0,
     "Marnie's Cottage",  'Four years of watching a cold chimney.'),
    ('pip_house',  'kaisyn:village/meadow_swiss/houses/meadow_medium_house_1',     0, (35, -36), 2, 'act1', 0,
     "Pip's Place",       'He is being extremely useful.'),
    ('granary',    'kaisyn:village/exclusives/rustic/houses/rustic_barn_professions_1', 0, (-36, 18), 2, 'act2', 1,
     'The Granary',       'Twelve alcoves, one winter to fill them.'),
    ('garden',     'kaisyn:village/exclusives/classic/houses/classic_small_farm_1', 0, (-12, -40), 2, 'act2', 0,
     'The Hedge Garden',  "Halden's rows. The quiet corner of town."),
    ('store',      'kaisyn:village/meadow_swiss/houses/meadow_butcher_and_mason_1', 0, (6, -36), 2, 'act3', 0,
     "Oda's Store",       'Eleven years of ledger, no stock.'),
    # THE BELL TOWER. classic_church_1 is a 10x12x7 cobblestone box with a ladder in it,
    # no bell, no glass and no roof - "the crudest thing in the town, and it is called The
    # Bell Tower" (media/look/NOTES.md item 5). Towns and Towers' meadow watchtower is the
    # tallest piece in any installed jar that has BOTH a real bell block and a door: 37
    # courses, a mossy-cobble plinth, a jettied timber body, a stone belfry with the bell
    # at local y27 and a flag over it. y_base 6 buries the plinth's ragged lower six
    # courses in the pad, which is what puts the door on the doorstep; what is left
    # standing is 31 blocks, and the bell ends up 21 blocks over the square.
    ('church',     'kaisyn:outpost/towers/meadow/base_plate',                      0, (-6, -31), 3, 'act3', 6,
     'The Bell Tower',    'Pip gets to ring it. Marnie said.'),
    # The Boathouse. meadow_fisher_1 is the meadow set's own dock building - a chalet with
    # a jetty off its south side - and it stands on the east shore looking at the pier.
    ('boathouse',  'kaisyn:village/meadow_swiss/houses/meadow_fisher_1',           0, (18, 29), 2, 'act2', 0,
     'The Boathouse',     'Nella wants her nets under a roof.'),
    ('town_hall',  'kaisyn:village/meadow_swiss/houses/meadow_large_house_1',      0, (-30, -28), 2, 'act5', 0,
     'The Town Hall',     'Fifteen people, arguing in the warm.'),
    ('newcomer_tess',  'kaisyn:village/meadow_swiss/houses/meadow_medium_house_2', 0, (20, 30), 2, 'act5', 0,
     "Tess's House",      'Empty until spring. Not empty now.'),
    ('newcomer_mab',   'kaisyn:village/meadow_swiss/houses/meadow_medium_house_3', 0, (-30, 34), 2, 'act5', 0,
     "Mab's House",       'Beds made before they got here.'),
    ('newcomer_corin', 'kaisyn:village/meadow_swiss/houses/meadow_medium_house_4', 0, (46, -4), 2, 'act5', 0,
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
# The meadow set's own town centre. Its 11x11 box is 68 cells of cyan_concrete street
# marker and 15 jigsaws round ONE real thing: a 5x5 smooth-quartz basin with a
# four-block jet standing in it. That real thing is the fountain on the square.
FOUNTAIN_TID = 'kaisyn:village/meadow_swiss/town_centers/meadow_meeting_point_1'
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


# DARK SQUARE FIX, the general case. The valley is dark by design: outside a building the
# only light in it is the forty copper lamp posts, and they ship `lit=false`. A structure
# template does not know that. The meadow watchtower alone carries twelve lanterns, eight
# torches and two campfires, and it is a 31-block landmark standing over the square -- lit,
# it is a lighthouse, and Act I's payoff (six posts come on) has nothing to be a payoff
# against. douse() blows out every light a template carries, in place, and ONLY the ones it
# actually carries: the fills are generated from the piece's own palette, so there are no
# dead commands and nothing outside the piece is touched.
#
# It is deliberately NOT applied to the houses. A lit window with a chair behind it is the
# warmest thing in the pack (media/look/NOTES.md, shot 11) and it is INSIDE a building,
# which is where the rule says light is allowed.
DOUSE = {
    'minecraft:torch': 'minecraft:air',
    'minecraft:wall_torch': 'minecraft:air',
    'minecraft:soul_torch': 'minecraft:air',
    'minecraft:soul_wall_torch': 'minecraft:air',
    'minecraft:lantern': 'minecraft:air',
    'minecraft:soul_lantern': 'minecraft:air',
    'minecraft:glowstone': 'minecraft:bone_block',
    'minecraft:shroomlight': 'minecraft:bone_block',
    'minecraft:sea_lantern': 'minecraft:smooth_quartz',
    'minecraft:jack_o_lantern': 'minecraft:carved_pumpkin',
    'minecraft:campfire': 'minecraft:campfire[lit=false]',
    'minecraft:soul_campfire': 'minecraft:soul_campfire[lit=false]',
    'minecraft:redstone_lamp': 'minecraft:redstone_lamp[lit=false]',
}
_CANDLES = ['minecraft:candle'] + ['minecraft:%s_candle' % c for c in (
    'white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
    'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black')]


def douse(p, box=None):
    """Every light this template ships, blown out where it stands."""
    if box is None:
        box = (p.x0, p.y0, p.z0, p.x1, p.y1, p.z1)
    have = set(b[0] for b in p.grid.values())
    out = []
    for src in sorted(have & set(DOUSE)):
        out.append(fill(box[0], box[1], box[2], box[3], box[4], box[5],
                        DOUSE[src], ' replace ' + src))
    # A candle keeps its count: `candle[lit=true]` as a filter matches all four counts, so
    # one fill per count, and only for the counts the piece actually has.
    for src in sorted(have & set(_CANDLES)):
        counts = sorted(set(int(b[1].get('candles', '1')) for b in p.grid.values()
                            if b[0] == src and b[1].get('lit') == 'true'))
        for n in counts:
            out.append(fill(box[0], box[1], box[2], box[3], box[4], box[5],
                            '%s[candles=%d,lit=false]' % (src, n),
                            ' replace %s[candles=%d,lit=true]' % (src, n)))
    return out


def ring(x0, y0, z0, x1, y1, z1, block):
    """The four walls of a box, and nothing inside it.

    NOT `fill ... hollow`. Vanilla's hollow flag fills the whole outer SHELL -- including
    the top and bottom faces -- so on a box one or two blocks tall the "shell" is the
    entire box, and the building comes out solid. That is exactly what happened to the
    rebuilt greenhouse and bathhouse on their first build: both of them shipped as a solid
    block of stone with a roof on it, and the section through the bathhouse showed no
    interior at all. Four explicit wall fills cannot do that at any height.
    """
    return [fill(x0, y0, z0, x1, y1, z0, block),
            fill(x0, y0, z1, x1, y1, z1, block),
            fill(x0, y0, z0 + 1, x0, y1, z1 - 1, block),
            fill(x1, y0, z0 + 1, x1, y1, z1 - 1, block)]


# SHUT DOORS, the general case (2026-09-05, job B). A structure template may ship its own
# front door standing OPEN, and eleven of the twelve houses in this valley ship shut. The
# twelfth -- kaisyn meadow_medium_house_4, Corin's -- ships open, which is wrong twice over:
# an empty, unlit house standing wide open reads as a break-in for the whole of Acts I to
# IV, and Act V's moveIn() then "opens" a door that is already open, so one of the three
# newcomers' arrivals has no visible beat at all.
#
# Every door the piece carries is written back WHERE IT STANDS with open=false and nothing
# else touched -- same block, same half, same facing, same hinge -- so this can never spin a
# door round the way a typed `setblock` with default properties would (see openDoor() in
# valley_finales.js for the same trap on the runtime side). Emitted straight after the
# `place template`, so anything the dressing puts on top of it still wins.
def shut_doors(p):
    """Every door this template ships open, shut where it stands.

    NOT a single setblock per half. A door will not take an `open` flip from a bare
    setblock while its other half is standing -- both halves copy FACING/OPEN/HINGE/POWERED
    off each other in updateShape, so the write is put straight back and vanilla answers
    "Could not set the block". That is exactly what the first version of this did, on this
    door, and the build log recorded both halves as `command returned 0` while the door
    stayed open. Measured and reproduced on the console 2026-09-05; the same fix is in
    openDoor() in valley_finales.js, with the full measurement written up there.

    So: air the upper half (which takes the lower with it), air the lower for the case where
    it did not, then write the lower back and the upper on top of it. `setblock air` drops
    nothing, and every property except `open` is the template's own.
    """
    out = []
    for lp, b in sorted(p.grid.items()):
        if not b[0].endswith('_door') or not b[1]:
            continue
        if b[1].get('half') != 'lower' or b[1].get('open') != 'true':
            continue
        up = p.grid.get((lp[0], lp[1] + 1, lp[2]))
        a = p.abs(lp)
        au = p.abs((lp[0], lp[1] + 1, lp[2]))

        def shut(b2):
            pr = dict(b2[1])
            pr['open'] = 'false'
            return '%s[%s]' % (b2[0], ','.join('%s=%s' % (k, pr[k]) for k in sorted(pr)))

        if up and up[0].endswith('_door'):
            out.append(setb(au[0], au[1], au[2], 'minecraft:air'))
        out.append(setb(a[0], a[1], a[2], 'minecraft:air'))
        out.append(setb(a[0], a[1], a[2], shut(b)))
        if up and up[0].endswith('_door'):
            out.append(setb(au[0], au[1], au[2], shut(up)))
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
    # TEMPLATE_OPEN: the cells the plan took out of the grid it reasons over have to come
    # out of the world too, or the front door the apron was routed to is still behind a
    # fence. Written immediately after the place, before anything else stands on them.
    for _lp, _blk in sorted(p.open_local.items()):
        _a = p.abs(_lp)
        out.append(setb(_a[0], _a[1], _a[2], _blk))
    out += marker_cleanup(p)
    # Anything the template wrote as air at ground level goes back to ground,
    # so the pad never reads as a trench around the building. `@padfix` rather
    # than a fill because it has to put back the same material `@pad` chose:
    # the handler caches the sample per pad rectangle, so the two agree.
    #
    # OVER THE SAME RECTANGLE `@pad` LEVELLED, inset one from the registry box. It used to
    # run over the whole box, and the ring it added is the one ring the design surface says
    # is meadow: padfix filled the air at pad level there, the built kerb came out a block
    # over the plan, and the skirt -- which had walked that column down to the hillside --
    # left a two-block lip. Measured on the 2026-09-05 build: eleven columns of it down the
    # inn's east side, `cut_edge` 11 against a limit of 8. The template never reaches that
    # ring anyway; it stands inside its own footprint, several columns in.
    out.append('@padfix %s %s %s %s %s %s %s'
               % (t(px0 + 1), t(0), t(pz0 + 1), t(px1 - 1), t(0), t(pz1 - 1), top))
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
    out |= set(rect_cells(FOUNTAIN[0], FOUNTAIN[1], FOUNTAIN[0] + 4, FOUNTAIN[1] + 4))
    for (bx, bz) in SQ_TREE + SQ_BED:
        out |= set(rect_cells(bx, bz, bx + 2, bz + 2))
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


def apron_cmds(door, name, lamp=True, sign=None):
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
        # THE DOORPOST. Beside the doorstep and OFF the corridor: a fence post standing in
        # a three-wide path is a three-wide path you cannot walk down the middle of, and
        # section (8) of the harness reads it as unwalkable ground.
        #
        # It used to carry a LIT minecraft:lantern -- one at every front door in the
        # valley, thirteen of them, every one of them a light source standing outdoors in
        # a town whose entire story is that nothing outdoors is lit until she lights it
        # (media/look/NOTES.md item 10: the unlit valley is not dark). The lantern is gone.
        # What hangs off the post instead is the building's NAME, on a proper gibbet: post,
        # post, an arm out over the doorstep and a hanging sign under the arm. Every
        # building in the town is named at its own door now, which is the other half of the
        # same fix -- there was nothing anywhere to tell you what you were standing in
        # front of.
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
            out.append(setb(lx, ly + 2, lz, POST))
            if sign:
                # the arm reaches back toward the door, and the sign hangs under it
                ax, az = lx - px * (1 if k > 0 else -1), lz - pz * (1 if k > 0 else -1)
                out.append(setb(lx, ly + 3, lz, POST))
                out.append(setb(ax, ly + 3, az, POST))
                out.append('setblock %s %s %s minecraft:oak_hanging_sign'
                           '[attached=false,rotation=%d,waterlogged=false]'
                           '{front_text:{messages:[%s],color:"gray"},is_waxed:1b}'
                           % (t(ax), t(ly + 2), t(az), 4 if pz else 0,
                              ','.join(json.dumps(json.dumps({'text': m})) for m in sign)))
            else:
                out.append(setb(lx, ly + 3, lz, POST))
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


LAMP_PAD_SAMPLE = []


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
                    # A cell of gravel this actually laid that is NOT a post's own cell:
                    # day1_lamps sets cobblestone under every post, so the old probe --
                    # which read the post's own column -- has never been able to pass.
                    if (dx, dz) != (0, 0) and not LAMP_PAD_SAMPLE:
                        LAMP_PAD_SAMPLE.append((c[0], y, c[1]))
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
SKIRT_RINGS = 14                 # how far a pad may reach out to find the natural surface
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
    # ...and the same grid with the leaves taken off, which is the cheap half of the walk
    # below: it drops the reader straight under the canopy so only the trunk has to be
    # stepped through block by block.
    _NL, _, _ = _SH.heights_box(WORLD_DIR, _GX0, _GX1, _GZ0, _GZ1, 'MOTION_BLOCKING_NO_LEAVES')

    def canopy(x, z):
        """Top non-fluid motion-blocking Y in the PREGEN -- INCLUDING whatever grew on the
        column. None off-grid or ungenerated."""
        ix, iz = x - _GX0, z - _GZ0
        if ix < 0 or iz < 0 or ix >= _OF.shape[0] or iz >= _OF.shape[1]:
            return None
        y = int(_OF[ix, iz])
        return None if y < -900 else y

    # A TREE IS NOT THE GROUND, and for the first three builds of this world the planner
    # thought it was.
    #
    # OCEAN_FLOOR is "the top block that blocks motion, ignoring fluids", and leaves and
    # logs block motion -- so on a wooded column the surface it reports is the CANOPY,
    # eleven or twelve blocks over the land. Measured on this seed: 38% of the columns
    # within ten blocks of the lantern road are leaf-covered in the pregen, and every one of
    # them handed the planner a natural surface up to twelve blocks too high.
    #
    # That is where the trench came from, and it came from it twice over. The skirt starts
    # every free column at its "natural" surface and then relaxes the field until no column
    # is more than a block from its neighbours -- so a tree column got dragged down eleven
    # blocks to meet the road, which counts as a REGRADE, and regrading a column means
    # clearing the air over it. Measured on the shipped world: 38% leaf cover in the pregen
    # against 2% in the built world over the same 2768 columns. The lantern road was a
    # twenty-block-wide clear-cut with bare graded steps in it, which is exactly what the
    # first-join screenshots show.
    #
    # So the surface is the LAND: start under the leaves and walk down through anything
    # that GREW there. Everything else -- pad medians, the road's profile, the skirt --
    # reads this, and the trees stay standing because nothing needs to move them.
    _GREW = ('_log', '_wood', 'leaves', 'mushroom_block', 'mushroom_stem', 'bamboo',
             'cactus', 'sugar_cane', 'vine', 'shroomlight', 'bee_nest', 'beehive',
             'nether_wart_block', 'moss_carpet', 'azalea', 'hanging_roots', 'cocoa',
             'stem', 'log', 'wood', 'branch', 'trunk')
    _LAND = {}

    def surface(x, z):
        """The LAND at this column in the PREGEN: the top block that grew there is walked
        past, so a spruce is not a hill. None off-grid or ungenerated."""
        k = (x, z)
        if k in _LAND:
            return _LAND[k]
        y = canopy(x, z)
        if y is None:
            _LAND[k] = None
            return None
        ix, iz = x - _GX0, z - _GZ0
        nl = int(_NL[ix, iz])
        if -900 < nl < y:
            y = nl
        low = y - 40
        try:
            v = _vt()
            while y > low:
                b = v.block(x, y, z).split('[')[0]
                if not any(t in b for t in _GREW):
                    break
                y -= 1
        except Exception:                                         # noqa: BLE001
            y = canopy(x, z)
        _LAND[k] = y
        return y

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

    def canopy(x, z):
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
# The bell tower is solved with the Act I pieces even though it goes up in Act III:
# it is the tallest thing in the valley and the only piece with a bell, and a landmark
# that gets whatever corner is left over after eleven houses is not a landmark. It
# claims the ground between the two north lanes first and the north cluster arranges
# itself around it.
EARLY = ('inn', 'mill', 'marnie_house', 'pip_house', 'church')
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

    STREET_PATHS = {}          # name -> [(dx, dy, dz)], anchor-relative, for the registry
    for _sn, _spts in STREETS:
        _cl = centre_line(_spts)
        _tg = [lev(c[0], c[1]) for c in _cl]
        _p0 = _pin_start(_cl[0])
        _sy = staircase(_tg, _tg[0] if _p0 is None else _p0)
        for _i, _c in enumerate(_cl):
            for _ddx in range(-(ROAD_BRUSH + 1), ROAD_BRUSH + 2):
                for _ddz in range(-(ROAD_BRUSH + 1), ROAD_BRUSH + 2):
                    LEVEL.setdefault((_c[0] + _ddx, _c[1] + _ddz), _sy[_i])
        # ...and record the level the street ACTUALLY got, which is not always the one its
        # own staircase asked for: LEVEL is first-writer-wins, so where a street runs into
        # the plaza or over a pad the terrace it meets keeps its level. Writing the
        # staircase's number into the registry instead made `road_banks` measure a verge
        # against a carriageway that is not there.
        STREET_PATHS[_sn] = [(_c[0], LEVEL.get((_c[0], _c[1]), _sy[_i]), _c[1])
                             for _i, _c in enumerate(_cl)]
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
# THE FOUNTAIN. Solved before the carts so it gets the middle of the east half rather than
# whatever is left. It is the meadow set's OWN town-centre piece: a quartz basin five
# across with a four-block jet in it. Its 11x11 bounding box is otherwise nothing but
# cyan_concrete street markers and jigsaws, which is why the piece is placed offset -- the
# only blocks it really has are the 5x5x4 fountain, and this is where they land.
# Three market carts, not four, and the fountain in the quarter the fourth used to stand
# in. A dying town of eleven people does not run four market stalls, and the square is a
# 25x25 that already carries a well, a waystone, a noticeboard, a signpost, a supper table,
# a bench garden and the road out of the south side: something had to give for the town to
# get a centrepiece, and a fourth trader's cart is the thing it can spare.
CART_POS = [sq_fit(5, 5, c) for c in ((4, -4), (8, -9), (-10, 3))]
FOUNTAIN = sq_fit(5, 5, (6, 3))

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

# Two trees and a flower bed, so there is something alive on the square. Three-block beds:
# a stone-brick wall kerb round a soil middle, exactly like a planted bed in a real square,
# and never in a road, a cart, the well or the bench garden because sq_fit spirals off
# anything already claimed. Solved AFTER the carts: a market cart that cannot stand where
# the town wants it is a fault, a tree that stands a block off its preferred corner is not.
SQ_TREE = [sq_fit(3, 3, c) for c in ((-11, -9), (-11, 8))]
SQ_BED = [sq_fit(3, 3, c) for c in ((9, -3),)]
# The window boxes on their kerb posts, cut from eight to four. Eight of them, plus the
# well, four carts, the bench garden, the supper table and now a fountain and three planted
# beds, is a square you cannot cross without walking round something -- and the square's
# own complaint in media/look/NOTES.md is that it is furnished like a waiting room.
FLOWER_POS = [sq_fit(2, 1, c) for c in ((-6, 0), (5, 1), (-4, -7), (4, 2))]

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
_seat_blocked |= set(rect_cells(FOUNTAIN[0], FOUNTAIN[1], FOUNTAIN[0] + 4, FOUNTAIN[1] + 4))
for _bb in SQ_TREE + SQ_BED:
    _seat_blocked |= set(rect_cells(_bb[0], _bb[1], _bb[0] + 2, _bb[1] + 2))

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


# The three houses Act V opens are DELIBERATELY unnamed: they are the empty houses, and a
# house with somebody's name already on the door is not empty.
UNNAMED = ('newcomer_tess', 'newcomer_mab', 'newcomer_corin')


def door_sign_lines(name):
    """The building's own label, wrapped to fit a hanging sign (four lines, ~11 wide)."""
    if name in UNNAMED or name not in META:
        return None
    words, lines, cur = META[name]['label'].split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > 11:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines[:4]


def window_boxes(p, want=6):
    """A flower box on the sill of up to `want` of this template's own windows.

    Read off the piece, never guessed: a candidate is a glass pane (or a Macaw window) in
    an exterior wall with a SOLID course under it and open air on the outside, which is
    exactly where a window box hangs. The box goes in that air cell, at the level of the
    course under the pane, facing out -- supported by the wall behind it, so it cannot pop
    the first time a neighbour updates. Windows on the ground course are skipped: a box at
    knee height beside a front door is something to trip over.

    kaisyn's meadow chalets already carry boxes on their south faces; this dresses the
    faces they left bare, and stops after `want` so a house does not read as a florist.
    """
    ag = {}
    for lp, b in p.grid.items():
        ag[tuple(p.abs(lp))] = b
    panes = []
    for a, b in sorted(ag.items()):
        if 'glass_pane' not in b[0] and 'window' not in b[0]:
            continue
        if not (3 <= a[1] <= 8):
            continue                          # ground-floor sills trip people; a belfry
        panes.append(a)                       # window twenty blocks up is not a window box
    out, used = [], set()
    for (x, y, z) in panes:
        if len(out) >= want:
            break
        for dirn, (dx, dz) in sorted(_STEP.items()):
            ox, oz = x + dx, z + dz
            if (ox, oz) in used:
                continue
            if not _solid(ag, (x, y - 1, z)):
                continue
            # open air outside: the template's own grid carries explicit air cells, so
            # "not in the dict" is not the test -- `_air` is
            if not all(_air(ag, (ox, y + k, oz)) for k in (-1, 0, 1)):
                continue
            if (ox, oz) in APRON_PAVED or (ox, oz) in street_cells:
                continue
            used.add((ox, oz))
            out.append(setb(ox, y - 1, oz,
                            'supplementaries:flower_box[face=wall,facing=%s]' % dirn))
            break
    return out


def building_group(key, name, dressing=None, npc_at=None, top='minecraft:grass_block'):
    """The pad, the template and everything standing on it, lifted onto the building's own
    level -- and the apron, which is NOT lifted, because the apron is the ramp between that
    level and the road's."""
    p = P[name]
    note_walls(p)
    dy = PAD_DY.get(name, 0)
    body = build_cmds(p, top)
    body += shut_doors(p)
    body += window_boxes(p)
    if dressing:
        body += dressing
    if npc_at:
        body += npc_at
    cmds = shift_y(body, dy)
    for d in p.doors()[:1]:
        cmds += apron_cmds(d, name, sign=door_sign_lines(name))
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
#
# THE RACE, rebuilt 2026-09-05. It used to be `place template valley:mill_race` -- a 7x3x3
# trough with SEVEN water cells in it, which media/look/NOTES.md item 8 correctly calls a
# seven-block puddle: "no race, no wheel, no flow". This is a real one:
#
#   a head basin at the east end of the yard, three across and full to the brim
#   a stone-lined channel three wide and ten long, kerbed both sides, running west
#   a plank footbridge over the middle of it, with rails
#   a WHEEL PIT at the mill's own east wall, cut three blocks deeper, so the channel
#     pours into it -- that fall is the flow, and it is where Q16 sets the two Water
#     Wheels; the pit is walled on all four sides and floored, so it cannot drain into
#     the mill's pad
MX, MZ = mill_yard[0], mill_yard[2]
RACE_X0, RACE_X1 = MX - 2, MX + 5          # the channel, west (pit) to east (head)
RACE_Z0, RACE_Z1 = MZ - 7, MZ - 5          # three wide
PIT_X0, PIT_X1 = MX - 2, MX
BRIDGE_X = MX + 1
_yx0, _yz0 = MX - 2, MZ - 8
_yx1, _yz1 = MX + 6, MZ - 3
dress_mill = [
    fill(_yx0, 1, _yz0, _yx1, 8, _yz1, 'minecraft:air'),
    fill(_yx0, -6, _yz0, _yx1, -1, _yz1, 'minecraft:dirt'),
    fill(_yx0, 0, _yz0, _yx1, 0, _yz1, 'minecraft:cobblestone'),
    # the channel: a stone-brick invert one block down, walls to either side, and the
    # water standing in it flush with the yard
    fill(RACE_X0, -1, RACE_Z0, RACE_X1 + 1, -1, RACE_Z1, 'minecraft:stone_bricks'),
    fill(RACE_X0, 0, RACE_Z0 - 1, RACE_X1 + 1, 0, RACE_Z0 - 1, 'minecraft:stone_bricks'),
    fill(RACE_X0, 0, RACE_Z1 + 1, RACE_X1 + 1, 0, RACE_Z1 + 1, 'minecraft:stone_bricks'),
    setb(RACE_X1 + 1, 0, RACE_Z0, 'minecraft:stone_bricks'),
    setb(RACE_X1 + 1, 0, RACE_Z0 + 1, 'minecraft:stone_bricks'),
    setb(RACE_X1 + 1, 0, RACE_Z1, 'minecraft:stone_bricks'),
    # the wheel pit, three deeper, sealed on every face that is not the channel
    fill(PIT_X0 - 1, -4, RACE_Z0 - 1, PIT_X1, -1, RACE_Z1 + 1, 'minecraft:stone_bricks'),
    fill(PIT_X0, -3, RACE_Z0, PIT_X1, 0, RACE_Z1, 'minecraft:air'),
    fill(PIT_X0, -3, RACE_Z0, PIT_X1, -1, RACE_Z1, 'minecraft:water[level=0]'),
    # the channel's own water, laid last so the walls are already standing
    fill(PIT_X1 + 1, 0, RACE_Z0, RACE_X1, 0, RACE_Z1, 'minecraft:water[level=0]'),
    # the footbridge over it
    fill(BRIDGE_X, 1, RACE_Z0 - 1, BRIDGE_X + 1, 1, RACE_Z1 + 1, 'minecraft:oak_planks'),
    fill(BRIDGE_X, 2, RACE_Z0 - 1, BRIDGE_X + 1, 2, RACE_Z0 - 1, 'minecraft:oak_fence'),
    fill(BRIDGE_X, 2, RACE_Z1 + 1, BRIDGE_X + 1, 2, RACE_Z1 + 1, 'minecraft:oak_fence'),
    # the snapped axle, on the stones where it fell
    setb(MX + 1, 1, MZ - 8, 'minecraft:stripped_oak_log[axis=x]'),
    setb(MX + 2, 1, MZ - 8, 'minecraft:stripped_oak_log[axis=x]'),
    setb(MX + 3, 1, MZ - 8, 'minecraft:oak_log[axis=x]'),
    setb(MX + 4, 1, MZ - 8, 'minecraft:stripped_oak_log[axis=z]'),
    # Bram's labelled crates, all of them on the SOUTH kerb now: the two that used to
    # stand at z = MZ-4 are in the channel since it went from one water cell wide to three
    setb(MX + 5, 1, MZ - 8, 'minecraft:barrel[facing=up]'),
    setb(MX + 4, 1, MZ - 3, 'handcrafted:oak_table'),
    setb(MX + 5, 1, MZ - 3, 'minecraft:crafting_table'),
    setb(MX + 6, 1, MZ - 3, POST),
    setb(MX + 6, 2, MZ - 3,
         'minecraft:oak_sign[rotation=12]{front_text:{messages:[\'{"text":"THE MILL"}\','
         '\'{"text":""}\',\'{"text":"B. Tolliver"}\',\'{"text":"millwright"}\'],color:"gray"}}'),
    npc('bram', [MX + 3, 1, MZ - 3]),
]
MILL_YARD = (_yx0, _yz0, _yx1, _yz1)
# NO APRON MAY CROSS THE RACE. An apron paves at dy0 and clears dy1..6 over every cell it
# takes, so a route across an open water channel is a cobbled lid on the channel -- which
# is exactly what the first build of this did: seven cells of the mill's own front path
# were laid straight over the wheel pit and the head of the race, and `pad_material` caught
# it as "pad edge cobblestone vs surround grass_block". The channel, its two kerbs and the
# pit are hard-blocked here, before act1_mill lays its own apron, so the path goes round.
apron_setup()
MILL_RACE_CELLS = set(rect_cells(RACE_X0 - 1, RACE_Z0 - 1, RACE_X1 + 1, RACE_Z1 + 1))
APRON_BLOCK.update(MILL_RACE_CELLS)
PROTECTED.update(MILL_RACE_CELLS)
building_group('act1_mill', 'mill', dressing=dress_mill)
probe('mill_race_water', [MX + 3, 0, MZ - 6], 'minecraft:water',
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
]

# ---------------------------------------------------------------------------
# THE PAVING. It used to be three concentric squares -- cobblestone, then a
# 15x15 of stone_bricks, then a 9x9 of polished_andesite, then a one-block
# gravel kerb -- and from inside the square that is what media/look/NOTES.md
# calls "one unbroken grid of pale tiles": four flat rectangles, every joint
# dead straight, every cell the same block as the ninety around it.
#
# This is laid the way a town lays a square: RINGS, not rectangles, so the
# geometry is round and the eye has a centre to find; four spokes running out
# to the four corner lamp posts; and a deterministic weathering scatter --
# mossy and cracked brick in the middle, gravel and coarse dirt at the kerb --
# off cell_hash(), so it is reproducible to the block and still reads as stone
# that has been walked on for sixty years. Only the cells that differ from the
# cobblestone base above are written.
# ---------------------------------------------------------------------------
PAVE = {}
for _px in range(-PLAZA, PLAZA + 1):
    for _pz in range(-PLAZA, PLAZA + 1):
        _r = math.hypot(_px, _pz)
        _h = cell_hash(_px, _pz)
        # a spoke is a cell within half a block of one of the two diagonals
        _spoke = abs(abs(_px) - abs(_pz)) <= 1 and 4.0 <= _r <= 11.0
        if _r < 2.6:                                  # the waystone dais
            _b = 'minecraft:polished_andesite'
        elif _r < 3.6:                                # its kerb ring
            _b = 'minecraft:chiseled_stone_bricks' if _h < 55 else 'minecraft:stone_bricks'
        elif _spoke:
            _b = 'minecraft:polished_andesite' if _h < 70 else 'minecraft:andesite'
        elif _r < 8.2:                                # the swept middle
            _b = ('minecraft:mossy_stone_bricks' if _h < 20 else
                  'minecraft:cracked_stone_bricks' if _h < 30 else
                  'minecraft:cobblestone' if _h < 38 else 'minecraft:stone_bricks')
        elif _r < 11.4:                               # the working half
            _b = ('minecraft:mossy_cobblestone' if _h < 22 else
                  'minecraft:gravel' if _h < 34 else
                  'minecraft:andesite' if _h < 42 else
                  'minecraft:stone_bricks' if _h < 50 else 'minecraft:cobblestone')
        else:                                         # the kerb, dissolving out
            _b = ('minecraft:coarse_dirt' if _h < 22 else
                  'minecraft:cobblestone' if _h < 34 else 'minecraft:gravel')
        if _b != 'minecraft:cobblestone':
            PAVE[(_px, _pz)] = _b
for (_px, _pz), _b in sorted(PAVE.items()):
    sq.append(setb(_px, 0, _pz, _b))

# ---------------------------------------------------------------------------
# THE FOUNTAIN. kaisyn's own meadow_swiss town centre, placed so its 5x5 quartz
# basin lands on the solved patch: the piece's real content is local x3..7,
# y1..4, z3..7 and everything else in its 11x11 box is street marker. The
# markers are cleared straight afterwards (marker_cleanup only runs for
# BUILDINGS, and this is furniture on the square), and its bell comes out --
# there is exactly one bell in this valley and it hangs in the tower.
# ---------------------------------------------------------------------------
FOUNTAIN_BOX = [FOUNTAIN[0], FOUNTAIN[1], FOUNTAIN[0] + 4, FOUNTAIN[1] + 4]
_fo = (FOUNTAIN[0] - 3, FOUNTAIN[1] - 3)
sq += [
    'place template %s %s %s %s' % (FOUNTAIN_TID, t(_fo[0]), t(0), t(_fo[1])),
    fill(_fo[0], 0, _fo[1], _fo[0] + 10, 4, _fo[1] + 10, 'minecraft:air',
         ' replace minecraft:jigsaw'),
    fill(_fo[0], 0, _fo[1], _fo[0] + 10, 4, _fo[1] + 10, 'minecraft:air',
         ' replace minecraft:cyan_concrete'),
    fill(FOUNTAIN_BOX[0], 1, FOUNTAIN_BOX[1], FOUNTAIN_BOX[2], 4, FOUNTAIN_BOX[3],
         'minecraft:smooth_quartz_slab[type=top]', ' replace minecraft:bell'),
]
# the paving the markers took back out, and the basin's own floor
for _px in range(_fo[0], _fo[0] + 11):
    for _pz in range(_fo[1], _fo[1] + 11):
        if max(abs(_px), abs(_pz)) <= PLAZA:
            sq.append(setb(_px, 0, _pz, PAVE.get((_px, _pz), 'minecraft:cobblestone')))
probe('square_fountain', [FOUNTAIN[0] + 2, 4, FOUNTAIN[1] + 2], 'minecraft:water')

# ---------------------------------------------------------------------------
# Two trees and two flower beds. A square with nothing growing on it is a car
# park; these are the only living things between the four corner lamp posts.
# Each is a 3x3: a stone-brick wall kerb round eight sides, soil in the middle,
# and either a birch that clears the awnings or a bed of the same flowers the
# window boxes carry.
# ---------------------------------------------------------------------------
for _bi, (_bx, _bz) in enumerate(SQ_TREE + SQ_BED):
    _cx, _cz = _bx + 1, _bz + 1
    for _dx in (-1, 0, 1):
        for _dz in (-1, 0, 1):
            if (_dx, _dz) == (0, 0):
                continue
            # a tree gets a full eight-block guard; a flower bed only four corner posts,
            # so the flowers in it are visible from the paving rather than behind a kerb
            if _bi < 2 or (_dx and _dz):
                sq.append(setb(_cx + _dx, 1, _cz + _dz, 'minecraft:stone_brick_wall'))
    sq.append(setb(_cx, 1, _cz, 'minecraft:podzol' if _bi < 2 else 'minecraft:grass_block'))
    if _bi < 2:
        # a birch: five of trunk, then a 5x5 crown at 6..7 and a cap at 8. It starts at
        # dy2, so the crown's lowest leaf is four blocks over the tallest market cart.
        for _ty in range(2, 7):
            sq.append(setb(_cx, _ty, _cz, 'minecraft:birch_log[axis=y]'))
        for _ty, _rad in ((6, 2), (7, 2), (8, 1)):
            for _dx in range(-_rad, _rad + 1):
                for _dz in range(-_rad, _rad + 1):
                    if _dx == 0 and _dz == 0 and _ty < 8:
                        continue
                    if abs(_dx) == _rad and abs(_dz) == _rad:
                        continue
                    sq.append(setb(_cx + _dx, _ty, _cz + _dz,
                                   'minecraft:birch_leaves[persistent=true]'))
    else:
        for _dx, _dz, _fl in ((0, 0, 'minecraft:peony'), (-1, 0, 'minecraft:red_tulip'),
                              (1, 0, 'minecraft:oxeye_daisy'), (0, -1, 'minecraft:cornflower'),
                              (0, 1, 'minecraft:allium')):
            sq.append(setb(_cx + _dx, 1, _cz + _dz, 'minecraft:grass_block'))
            sq.append(setb(_cx + _dx, 2, _cz + _dz, _fl))
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
    # DARK SQUARE FIX (2026-09-05): the cart templates carry LIT candles under their
    # awnings. The square has to be dark until Act I lights the six copper lamps, so the
    # candles are blown out where they stand -- the cart still reads as a dressed cart,
    # it just stops being a light source. The four in this valley are all candles=3.
    sq.append(fill(cx, 1, cz, cx + 4, 5, cz + 4,
                   'minecraft:candle[candles=3,lit=false]', ' replace minecraft:candle[lit=true]'))
_cart = Placed('market_cart', MARKET_CARTS[0], 0, CART_POS[0][0], CART_POS[0][1], y_base=-1)
for _pr in _cart.probes():
    PROBES.append(_pr)
# flower boxes along the kerb.
# DARK SQUARE FIX (2026-09-05): these posts used to carry a LIT minecraft:lantern, and
# with fourteen of them plus the supper table's candles the square read fully at midnight
# -- so the story's payoff (forty dark copper lamps, six lit at the end of Act I, all
# forty by Act V) had no before and no after. The lantern is gone; the POST stays,
# because the flower box beside it is wall-mounted ON the post and pops off as an item
# the moment the post does.
for i, (fx, fz) in enumerate(FLOWER_POS):
    sq.append(setb(fx, 1, fz, POST))
    sq.append(setb(fx + 1, 1, fz, 'supplementaries:flower_box'))
# the bench garden either side of the waystone (see SQ_BENCH above)
for (bx, bz, face) in SQ_BENCH:
    sq.append(setb(bx, 1, bz, 'handcrafted:oak_bench[facing=%s]' % face))
for (bx, bz) in SQ_PLANTER:
    sq.append(setb(bx, 1, bz, 'supplementaries:flower_box'))
# DARK SQUARE FIX (2026-09-05): the four bench-garden ends carried a post and a LIT
# lantern each. Nothing is mounted on these four, so post and lantern both go -- which
# also takes four of the forty-seven fence posts out of the middle of the square.
# SQ_POST itself stays: it is part of _sq_blocked, and the solver routes the well, the
# carts and the flower boxes around those four cells. Only the emission is gone.
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
if LAMP_PAD_SAMPLE:
    probe('lamp_pad', list(LAMP_PAD_SAMPLE[0]), 'minecraft:gravel')

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
    # ...on the granary's OWN terrace. This probe (and church_bell below) were written
    # before the town was terraced and never got the `dy=` every other probe carries, so
    # both of them have been reading three blocks above the block they name since the day
    # the pads got their own levels: the shipped world scored 44/47, not 47/47.
    probe('granary_alcove', [alcoves[0][0], alcoves[0][1] - 1, alcoves[0][2]],
          'minecraft:polished_andesite', dy=PAD_DY.get('granary', 0))
building_group('act2_garden', 'garden', top='minecraft:grass_block')

# The Boathouse, on the east shore looking at the pier. Nella's nets, her spare oars and a
# boat on the shingle; the covered slip out over the water is part of day1_lakefront.
boat_p = P['boathouse']
_bd = boat_p.doors()[0]
_bsx, _bsz = _STEP[_bd['facing']]
dress_boat = [
    setb(boat_p.x0 + 1, 1, boat_p.z1 - 1, 'minecraft:barrel[facing=up]'),
    setb(boat_p.x1 - 1, 1, boat_p.z1 - 1, 'handcrafted:oak_table'),
    setb(boat_p.x0 + 2, 1, boat_p.z1 - 1, 'minecraft:composter'),
]
building_group('act2_boathouse', 'boathouse', dressing=dress_boat)

# --- Act III: the store, the bell tower, the supper table -------------------
store = P['store']
store_stand = indoor_stands(store)
dress_store = [npc('oda', list(store_stand[0]))] if store_stand else []
building_group('act3_store', 'store', dressing=dress_store)

church = P['church']
# The bell. classic_church_1 had none, so this used to stack one on the highest solid
# block it could find - which on a piece with a flagpole is the top of the flagpole. The
# watchtower ships a real bell in its belfry, hung the way the mod's own builder hung it,
# so it is READ rather than added: the registry's bell position is the template's, and
# Act III's quest rings a bell that is part of the building instead of an ornament resting
# on its roof. The fallback is kept for any future piece that has no bell of its own.
bell, dress_church = None, []
_bell_own = [lp for lp, b in sorted(church.grid.items()) if b[0] == 'minecraft:bell']
if _bell_own:
    bell = church.abs(_bell_own[0])
else:
    top_solid = max(lp[1] for lp, b in church.grid.items() if _solid(church.grid, lp))
    bell_local = None
    for lp, b in sorted(church.grid.items()):
        if lp[1] == top_solid - 1 and _solid(church.grid, lp):
            bell_local = lp
            break
    if bell_local:
        bell = church.abs((bell_local[0], bell_local[1] + 1, bell_local[2]))
        dress_church.append(setb(bell[0], bell[1], bell[2],
                                 'minecraft:bell[attachment=floor,facing=south]'))
dress_church += douse(church)
building_group('act3_church', 'church', dressing=dress_church)
if bell:
    probe('church_bell', bell, 'minecraft:bell', dy=PAD_DY.get('church', 0))
    print('  bell tower: %s, %d courses, bell at dy %+d (%d over the plaza)'
          % (church.tid.split('/')[-1], church.size[1], bell[1],
             bell[1] + PAD_DY.get('church', 0)))

# The Harvest Supper table: real furniture on the square, not a template box.
#
# It used to be nine tables between two ranks of NINE INDIVIDUAL CHAIRS each -- eighteen
# `handcrafted:oak_chair` in two dead-straight lines down the middle of the square, which
# is the single thing media/look/NOTES.md item 3 names when it calls the square "furnished
# like a waiting room". The chairs are gone. What stands here now is a trestle: seven
# tables with a CONTINUOUS BENCH down each side -- handcrafted's benches join up into one
# long seat rather than reading as fourteen separate objects -- and one chair at each end,
# for whoever is carving. Eleven people still sit down at it; `SUPPER_SEATS` above solves
# where they stand, and it is unchanged.
tbl = []
for x in range(-3, 4):
    tbl.append(setb(x, 1, -10, 'handcrafted:oak_table'))
    tbl.append(setb(x, 1, -11, 'handcrafted:oak_bench[facing=south]'))
    tbl.append(setb(x, 1, -9, 'handcrafted:oak_bench[facing=north]'))
tbl.append(setb(-4, 1, -10, 'handcrafted:oak_chair[facing=east]'))
tbl.append(setb(4, 1, -10, 'handcrafted:oak_chair[facing=west]'))
# DARK SQUARE FIX (2026-09-05): the three candle holders were lit=true and the two
# table ends carried a post with a LIT lantern on it. The supper table keeps its candle
# holders -- unlit -- and loses the two lantern posts, so nothing on this square emits
# light until finaleAct1 lights the first six copper lamps.
for x in (-2, 0, 2):
    tbl.append(setb(x, 2, -10, 'supplementaries:candle_holder[lit=false,face=floor,facing=north,candles=3]'))
group('act3_table', 'anchor', tbl)
probe('supper_table', [0, 1, -10], 'handcrafted:oak_table')

# --- Act IV: the greenhouse ---------------------------------------------------
# REBUILT 2026-09-05. What stood here was a spruce-plank box with panes stuck on it at four
# different heights (media/look/NOTES.md item 6: "a blank wall with glass stuck on it"),
# and no template in any installed jar is a greenhouse, so this is a real parametric
# building instead:
#
#   dy0   a stone-brick raft, with the beds and the walkway cut into it
#   dy1   the BASE COURSE -- stone brick all round, the thing every glasshouse stands on
#   dy2-4 the frame: stone-brick corner piers, copper-bar mullions every third column,
#         and glass between them (the glass is in the GLAZE group, because Q64 is the
#         player glazing six empty frames herself and the shell has to ship empty)
#   dy5-8 an ARCH, not a gable: the roof height falls as a cosine off the ridge, so the
#         span reads as a barrel vault of glass with copper eaves, and both end walls are
#         arched glass gables
#   the chimney for Q72's heaters, up the east end and three courses over the ridge
#
# Everything is computed off the solved rectangle, so the building follows the site.
gx0, gz0, gx1, gz1 = gh
gm = OFF['greenhouse']
GH_ZC = (gz0 + gz1) // 2
GH_EAVE, GH_RISE = 5, 3
GH_MULLION = [gx0 + 3, gx0 + 6, gx0 + 9]
GH_DOOR = (gx0 + (gx1 - gx0) // 2, gz1)


def _gh_ry(z):
    """The arch: eaves at the two long walls, ridge down the middle."""
    half = max(1.0, (gz1 - gz0) / 2.0)
    return GH_EAVE + int(round(GH_RISE * math.cos(math.pi / 2 * abs(z - GH_ZC) / half)))


shell = pad_cmds(gx0 - 2, gz0 - 2, gx1 + 2, gz1 + 2, 14)
shell += [
    # the raft and the plinth
    fill(gx0, 0, gz0, gx1, 0, gz1, 'minecraft:stone_bricks'),
    fill(gx0, 1, gz0, gx1, 3, gz1, 'minecraft:air'),
]
shell += ring(gx0, 1, gz0, gx1, 1, gz1, 'minecraft:stone_bricks')
# the beds, the walkway and the potting bench, cut into the raft
for _z in range(gz0 + 1, gz1):
    if _z == GH_ZC or _z == gz1 - 1:
        continue                                   # walkway
    if _z == gz0 + 1:
        continue                                   # the bench sits on the raft
    shell.append(fill(gx0 + 1, 0, _z, gx1 - 1, 0, _z, 'minecraft:podzol'))
shell += [
    fill(gx0 + 1, 1, gz0 + 1, gx1 - 1, 1, gz0 + 1, 'minecraft:spruce_slab[type=top]'),
    setb(gx0 + 1, 1, gz1 - 1, 'farmersdelight:organic_compost'),
    setb(gx1 - 1, 1, gz1 - 1, 'handcrafted:oak_table'),
]
# the frame: four stone piers, copper-bar mullions, an open frame everywhere else
for _cx, _cz in ((gx0, gz0), (gx1, gz0), (gx0, gz1), (gx1, gz1)):
    shell.append(fill(_cx, 2, _cz, _cx, 4, _cz, 'minecraft:stone_bricks'))
GH_FRAME = []
for _mx in GH_MULLION:
    GH_FRAME += [(_mx, gz0), (_mx, gz1)]
GH_FRAME += [(gx0, GH_ZC), (gx1, GH_ZC)]
for (_fx, _fz) in GH_FRAME:
    shell.append(fill(_fx, 2, _fz, _fx, 4, _fz, 'createdeco:copper_bars'))
# the arch's ribs and its copper eaves. The glass between them is the glaze.
GH_ROOF, GH_GABLE = [], []
_prev = None
for _z in range(gz0, gz1 + 1):
    _ry = _gh_ry(_z)
    GH_ROOF.append((_ry, _z))
    if _prev is not None and _ry > _prev:
        GH_ROOF.append((_ry - 1, _z))               # close the riser
    _prev = _ry
    for _y in range(GH_EAVE, _ry):
        GH_GABLE += [(gx0, _y, _z), (gx1, _y, _z)]
shell += [
    fill(gx0, GH_EAVE, gz0, gx1, GH_EAVE, gz0,
         'minecraft:waxed_exposed_cut_copper_stairs[facing=north]'),
    fill(gx0, GH_EAVE, gz1, gx1, GH_EAVE, gz1,
         'minecraft:waxed_exposed_cut_copper_stairs[facing=south]'),
]
for _mx in [gx0] + GH_MULLION + [gx1]:
    for (_ry, _z) in GH_ROOF:
        if _z in (gz0, gz1):
            continue
        shell.append(setb(_mx, _ry, _z, 'createdeco:copper_bars'))
# the doorway, left empty for Q64
shell.append(fill(GH_DOOR[0], 1, GH_DOOR[1], GH_DOOR[0], 3, GH_DOOR[1], 'minecraft:air'))
# the chimney for the heaters: up the east gable, three courses over the ridge
GH_FLUE = (gx1, gz0 + 2)
shell += [
    fill(GH_FLUE[0], 1, GH_FLUE[1], GH_FLUE[0], 10, GH_FLUE[1], 'minecraft:stone_bricks'),
    fill(GH_FLUE[0], 8, GH_FLUE[1], GH_FLUE[0], 10, GH_FLUE[1], 'minecraft:bricks'),
    setb(GH_FLUE[0], 11, GH_FLUE[1], 'minecraft:brick_slab'),
    # DARK SQUARE FIX: these two used to be LAMP_LIT, i.e. two lit copper lamps standing
    # outside a building in a valley whose whole story is that nothing outside is lit.
    setb(gx0, 2, gm[2], LAMP_DARK),
    setb(gx1, 2, gm[2], LAMP_DARK),
]
shell += arrival(META['greenhouse']['label'], META['greenhouse']['blurb'])
GH_DY = PAD_DY.get('greenhouse', 0)
shell = shift_y(shell, GH_DY)
# ...and a way in. The greenhouse is the one building in the valley that never had an
# apron: its door opened onto the raw skirt of its own pad.
shell += apron_cmds({'pos': [GH_DOOR[0], 1 + GH_DY, GH_DOOR[1]], 'facing': 'south'},
                    'greenhouse', sign=door_sign_lines('greenhouse'))
group('act4_greenhouse_shell', 'anchor', shell)
probe('greenhouse_wall', [gx0, 1, gz0 + 1], 'minecraft:stone_bricks', dy=GH_DY)

glaze = []
# the walls: every frame bay that is not a pier, a mullion or the doorway
for _z in (gz0, gz1):
    for _x in range(gx0 + 1, gx1):
        if (_x, _z) in GH_FRAME or (_x, _z) == GH_DOOR:
            continue
        glaze.append(fill(_x, 2, _z, _x, 4, _z, 'minecraft:glass_pane'))
for _x in (gx0, gx1):
    for _z in range(gz0 + 1, gz1):
        if (_x, _z) in GH_FRAME or (_x, _z) == GH_FLUE:
            continue
        glaze.append(fill(_x, 2, _z, _x, 4, _z, 'minecraft:glass_pane'))
# the arched gable ends, in pane so the ribs read through them
for (_gx2, _gy, _gz2) in GH_GABLE:
    if (_gx2, _gz2) == GH_FLUE:
        continue
    glaze.append(setb(_gx2, _gy, _gz2, 'minecraft:glass_pane'))
# the vault
for (_ry, _z) in GH_ROOF:
    for _x in range(gx0, gx1 + 1):
        if _x in [gx0] + GH_MULLION + [gx1] and _z not in (gz0, gz1):
            continue
        if _z in (gz0, gz1):
            continue
        if (_x, _z) == GH_FLUE:
            continue
        glaze.append(setb(_x, _ry, _z, 'minecraft:glass'))
glaze += [
    'setblock %s %s %s mcwdoors:oak_cottage_door[half=lower,facing=north,hinge=left,open=false]'
    % (t(GH_DOOR[0]), t(1), t(GH_DOOR[1])),
    'setblock %s %s %s mcwdoors:oak_cottage_door[half=upper,facing=north,hinge=left,open=false]'
    % (t(GH_DOOR[0]), t(2), t(GH_DOOR[1])),
]
# eight planters on the marked bench (Q64 hands these over), and what is growing in the beds
for _x in range(gx0 + 2, gx1 - 1, 2):
    glaze.append(setb(_x, 2, gz0 + 1, 'minecraft:flower_pot'))
for _z in range(gz0 + 1, gz1):
    if _z in (GH_ZC, gz1 - 1, gz0 + 1):
        continue
    for _x in range(gx0 + 1, gx1):
        _h = cell_hash(_x, _z)
        glaze.append(setb(_x, 1, _z,
                          'minecraft:sweet_berry_bush[age=2]' if _h < 22 else
                          'minecraft:fern' if _h < 50 else
                          'minecraft:grass' if _h < 72 else 'minecraft:air'))
glaze.append('playsound minecraft:block.glass.place master @a ~0 ~1 ~0 2 1')
group('act4_greenhouse_glaze', 'anchor', shift_y(glaze, GH_DY))
# one column OFF the centre: the centre line of the vault is a copper rib
probe('greenhouse_glass', [gm[0] + 1, _gh_ry(GH_ZC), GH_ZC], 'minecraft:glass', dy=GH_DY)

heat = []
for x in range(gx0 + 2, gx1 - 1, 2):
    heat.append(setb(x, 0, gz0 + 1, 'minecraft:magma_block'))
heat.append(fill(gx0 + 1, 0, gz1 - 1, gx1 - 1, 0, gz1 - 1, 'thermal:fluid_duct'))
group('act4_greenhouse_heat', 'anchor', shift_y(heat, GH_DY))

# --- Act IV: the bathhouse ----------------------------------------------------
# REBUILT 2026-09-05. It was a stone box with a flat spruce lid and a puddle in it. This is
# a bathhouse: stone brick to the sill, spruce boarding above it, four sunk cauldron tubs
# round a warm tank, benches along two walls, and a COPPER HIP ROOF -- five stepped rings
# of waxed exposed cut copper, which is the one roof in the valley with a colour in it --
# with a stone flue up the north-west corner for the steam. Nothing in it is lit: the tank
# is warm because Q72 plumbs the Works' waste heat into it, and that is a story beat, not
# a light source.
bx0, bz0, bx1, bz1 = bh
bm = OFF['bathhouse']
BH_DOOR = (bm[0], bz0)
bath = pad_cmds(bx0 - 2, bz0 - 2, bx1 + 2, bz1 + 2, 14)
bath += [
    fill(bx0, 0, bz0, bx1, 0, bz1, 'minecraft:stone_bricks'),
    fill(bx0, 1, bz0, bx1, 3, bz1, 'minecraft:air'),
]
# stone to the sill, spruce boarding above it
bath += ring(bx0, 1, bz0, bx1, 1, bz1, 'minecraft:stone_bricks')
bath += ring(bx0, 2, bz0, bx1, 3, bz1, 'minecraft:spruce_planks')
for _cx, _cz in ((bx0, bz0), (bx1, bz0), (bx0, bz1), (bx1, bz1)):
    bath.append(fill(_cx, 1, _cz, _cx, 3, _cz, 'minecraft:stripped_spruce_log[axis=y]'))
bath += [
    # the doorway, facing the town
    fill(BH_DOOR[0], 1, BH_DOOR[1], BH_DOOR[0], 2, BH_DOOR[1], 'minecraft:air'),
    # two window bands, in the boarding rather than punched through the stone
    fill(bx0, 2, bz0 + 2, bx0, 2, bz1 - 2, 'minecraft:glass_pane'),
    fill(bx1, 2, bz0 + 2, bx1, 2, bz1 - 2, 'minecraft:glass_pane'),
    fill(bx0 + 2, 2, bz1, bx1 - 2, 2, bz1, 'minecraft:glass_pane'),
]
# the copper hip roof: five stepped rings, each a solid course with a stair skin, so there
# is no diagonal gap to see sky through.
BH_RINGS = min((bx1 - bx0) // 2, (bz1 - bz0) // 2) + 1
for _k in range(BH_RINGS):
    _y = 4 + _k
    _a, _b, _c, _d = bx0 + _k, bz0 + _k, bx1 - _k, bz1 - _k
    bath.append(fill(_a, _y, _b, _c, _y, _d, 'minecraft:waxed_exposed_cut_copper'))
    if _a < _c:
        bath.append(fill(_a, _y, _b, _c, _y, _b,
                         'minecraft:waxed_exposed_cut_copper_stairs[facing=north]'))
        bath.append(fill(_a, _y, _d, _c, _y, _d,
                         'minecraft:waxed_exposed_cut_copper_stairs[facing=south]'))
        bath.append(fill(_a, _y, _b + 1, _a, _y, _d - 1,
                         'minecraft:waxed_exposed_cut_copper_stairs[facing=west]'))
        bath.append(fill(_c, _y, _b + 1, _c, _y, _d - 1,
                         'minecraft:waxed_exposed_cut_copper_stairs[facing=east]'))
    else:
        bath.append(setb(_a, _y, _b, 'minecraft:waxed_exposed_cut_copper_slab'))
# the flue, up the north-west corner and clear of the ridge
BH_FLUE = (bx0 + 1, bz0 + 1)
bath += [
    fill(BH_FLUE[0], 1, BH_FLUE[1], BH_FLUE[0], 4 + BH_RINGS + 1, BH_FLUE[1],
         'minecraft:stone_bricks'),
    setb(BH_FLUE[0], 4 + BH_RINGS + 2, BH_FLUE[1], 'minecraft:stone_brick_slab'),
    # the tank: sunk into the raft, rimmed in stone brick, warm since Q72
    fill(bx0 + 2, 0, bz0 + 2, bx1 - 2, 0, bz1 - 2, 'minecraft:water[level=0]'),
    setb(bm[0], -1, bm[2], 'minecraft:magma_block'),
]
# four cauldron tubs in the corners, two benches, two unlit lamps
for _tx, _tz in ((bx0 + 1, bz1 - 1), (bx1 - 1, bz0 + 1), (bx1 - 1, bz1 - 1)):
    bath.append(setb(_tx, 1, _tz, 'minecraft:water_cauldron[level=3]'))
bath += [
    setb(bx0 + 1, 1, bm[2], 'handcrafted:spruce_bench[facing=east]'),
    setb(bx1 - 1, 1, bm[2], 'handcrafted:spruce_bench[facing=west]'),
    setb(bx0 + 2, 2, bz0, LAMP_DARK),
    setb(bx1 - 2, 2, bz0, LAMP_DARK),
    'playsound minecraft:block.bubble_column.upwards_ambient master @a ~0 ~1 ~0 2 0.8',
]
BH_DY = PAD_DY.get('bathhouse', 0)
bath = shift_y(bath, BH_DY)
bath += apron_cmds({'pos': [BH_DOOR[0], 1 + BH_DY, BH_DOOR[1]], 'facing': 'north'}, 'bathhouse',
                   sign=door_sign_lines('bathhouse'))
bath += arrival(META['bathhouse']['label'], META['bathhouse']['blurb'])
group('act4_bathhouse', 'anchor', bath)
probe('bathhouse_wall', [bx0, 2, bz0 + 1], 'minecraft:spruce_planks', dy=BH_DY)
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
TOB = solve_custom('tobin_camp', 9, 9, (38, -50))
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
    '# The wool mat Q3 puts the Red Bed on, and the hook the Sconce goes on. Both are',
    '# CLEARED ABOVE, which the old pair were not: the template stands a length of',
    '# stripped dark oak on one mat cell and a cold campfire is on the other, so the bed',
    '# had nowhere to go, and the hook at [1,0,1] had the loft LADDER in the cell the',
    '# sconce hangs in. Two cells for the bed, running west along z = home-1, and the',
    '# hook moved to the wall on the other side of the hearth.',
    'setblock ~-1 ~-1 ~-1 minecraft:white_wool',
    'setblock ~-2 ~-1 ~-1 minecraft:white_wool',
    'setblock ~-1 ~0 ~-1 minecraft:air',
    'setblock ~-2 ~0 ~-1 minecraft:air',
    'setblock ~-1 ~1 ~-1 minecraft:air',
    'setblock ~-2 ~1 ~-1 minecraft:air',
    'setblock ~-1 ~-1 ~0 minecraft:white_wool',
    'setblock ~-1 ~0 ~1 minecraft:oak_fence',
    'setblock ~-1 ~1 ~1 minecraft:air',
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
    'act2_granary', 'act2_garden', 'act2_boathouse',                # finaleAct2
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

    # The town's mouth: the column the site solver picked, fourteen blocks off the anchor,
    # on the square's doorstep. It USED to be where the player spawned, and that was the
    # arrival bug: spawn sat NORTH of the plaza and the farm is SOUTH of it, so "follow the
    # road south to the farm" walked her straight across the finished square before Q1 --
    # a wall of plaza benches on the first frame and the whole town spent in ten seconds.
    # It is now just the road's town end; she arrives here on foot from the farm.
    TOWN_HEAD_W = list(SPAWN_W)

    # =====================================================================
    # WHERE SHE ACTUALLY STARTS.
    #
    # The far side of the farm, so the road reads in the order the story does:
    #   spawn -> the farm gate -> past the farm -> the square.
    # Solved, not typed. Walk a fan of bearings out of the gate on the side AWAY from the
    # town, SPAWN_MIN..SPAWN_MAX road columns, and keep the one that
    #   * never crosses water and stays on generated land;
    #   * lands the road's own staircase ON the natural surface at the far end;
    #   * cuts and fills the least along the way; and, the point of the whole thing,
    #   * cannot see the plaza -- the sightline from her eye at spawn to the town waystone
    #     has to run into ground first, and on this seed it runs into the farm's own rise.
    # =====================================================================
    SPAWN_MIN, SPAWN_MAX = 70, 90

    def _hidden(sx, sz, sy):
        """Is the town waystone out of sight from her eye at spawn? Tested against the
        LAND, so a wood is not counted as cover -- the fix has to hold in winter."""
        tx, tz, ty = ANCHOR_W[0], ANCHOR_W[2], ANCHOR_W[1] + 1
        dist = math.hypot(tx - sx, tz - sz)
        eye = sy + 2
        for s in range(3, int(dist)):
            f = s / dist
            px = int(round(sx + (tx - sx) * f))
            pz = int(round(sz + (tz - sz) * f))
            g = surface(px, pz)
            if g is None:
                continue
            if g > eye + (ty - eye) * f + 1.5:
                return (px, pz, g)
        return None

    _ax = GATE_W[0] - ANCHOR_W[0]
    _az = GATE_W[2] - ANCHOR_W[2]
    _al = math.hypot(_ax, _az) or 1.0
    _ax, _az = _ax / _al, _az / _al                # anchor -> gate, i.e. AWAY from the town
    _cands = []
    for _deg in range(-40, 41, 4):
        _a = math.radians(_deg)
        _ux = _ax * math.cos(_a) - _az * math.sin(_a)
        _uz = _ax * math.sin(_a) + _az * math.cos(_a)
        for _d in range(SPAWN_MIN, SPAWN_MAX + 1, 2):
            _cx = int(round(GATE_W[0] + _ux * _d))
            _cz = int(round(GATE_W[2] + _uz * _d))
            _pts = _leg(GATE_W, [_cx, 0, _cz]) + [(_cx, _cz)]
            if any(wet(_p[0] - ANCHOR_W[0], _p[1] - ANCHOR_W[2]) or
                   surface(_p[0], _p[1]) is None for _p in _pts):
                continue
            # the leg's own staircase, pinned to the cottage yard where it starts inside it
            _tgt = [dsurf(_p[0], _p[1]) for _p in _pts]
            _prof = staircase(_tgt, _tgt[0])
            _cut = [abs(_prof[_k] - _tgt[_k]) for _k in range(len(_tgt))]
            _sy = _prof[-1]
            _blk = _hidden(_cx, _cz, _sy)
            if _blk is None:
                continue
            _cands.append((_cut[-1], max(_cut), abs(len(_pts) - 1 - 76), _deg, _d,
                           _cx, _cz, _sy, _blk))
    if not _cands:
        raise SystemExit('plan_town: no spawn candidate on the far side of the farm hides '
                         'the town -- widen the fan or the distance band')
    _cands.sort()
    _c = _cands[0]
    SPAWN_W = [_c[5], _c[7] + 1, _c[6]]
    SPAWN_HIDDEN = _c[8]
    SPAWN_RUN = int(max(abs(SPAWN_W[0] - GATE_W[0]), abs(SPAWN_W[2] - GATE_W[2])))
    print('  spawn moved to the far side of the farm: %s, %d road blocks from the gate '
          '(bearing %+d deg off the away-line), cut %d/%d'
          % (str(SPAWN_W), SPAWN_RUN, _c[3], _c[0], _c[1]))
    print('    the town is hidden: the sightline to the waystone runs into ground at '
          '%d,%d (y %d)' % (SPAWN_HIDDEN[0], SPAWN_HIDDEN[1], SPAWN_HIDDEN[2]))

    # One road, walked once, town end first: the square's doorstep -> the bend at the
    # bottom of the cottage yard -> the farm gate -> on past the farm to where she wakes
    # up. The old route ran spawn -> gate -> back to the plaza's south kerb, which laid a
    # second carriageway ten blocks from the first all the way down the valley and then had
    # to be pinned twice. The order matters twice over: the profile is a staircase and it is
    # pinned at the square, and the forty lamps are numbered along it, so lighting the road
    # runs from the square outward toward home exactly as the quests say.
    ROAD_CENTRE = []
    for _a, _b in ((TOWN_HEAD_W, BEND_W), (BEND_W, GATE_W), (GATE_W, SPAWN_W)):
        for _c2 in _leg(_a, _b):
            if not ROAD_CENTRE or ROAD_CENTRE[-1] != _c2:
                ROAD_CENTRE.append(_c2)
    ROAD_CENTRE.append((SPAWN_W[0], SPAWN_W[2]))

    # The road's own Y. Read off the DESIGN surface, not the raw land: where the road runs
    # into the plaza or the cottage yard it has to arrive at the level those were terraced
    # to, and everywhere else the design surface IS the land.
    # The lakefront's own footprint, in world coordinates: the levelled yard is the lake
    # mark +-LAKE_R, and the basin runs on to +LAKE_FAR. Everything in it is finished at
    # lake.y-1, so it is a terrace like the plaza and the cottage yard and the design
    # surface has to say so BEFORE the skirt and the road are solved against it.
    LAKE_W = [ANCHOR_W[0] + OFF['lake'][0], ANCHOR_W[1] + OFF['lake'][1],
              ANCHOR_W[2] + OFF['lake'][2]]
    # ...and it is not a square. The first attempt registered the bounding box, 29 x 41, and
    # that is a plate cut into a hillside forty blocks from the water -- exactly the "grey
    # plinth with a green lid" the terracing pass exists to stop. The footprint is the three
    # rectangles the group actually writes: the pier yard, the beach and the basin.
    # ...and it is entirely EAST of the lantern road. Centred on the lake mark, as the Act
    # II finale had it, the basin's west half sat on top of the road: measured on the first
    # shipped-world build, fifteen consecutive road columns came out under three courses of
    # water, and `road_steps` reported a 3-block drop at the water's edge. The road runs
    # along the yard's western kerb now and the water starts two blocks east of it.
    LAKE_RECTS = ((-2, -6, 16, 8),       # the yard, including the road's crossing of it
                  (2, 6, 14, 16),        # the beach
                  (1, 9, 17, 25))        # the basin and its rim

    def in_lake(x, z):
        dx, dz = x - LAKE_W[0], z - LAKE_W[2]
        for r in LAKE_RECTS:
            if r[0] <= dx <= r[2] and r[1] <= dz <= r[3]:
                return True
        return False

    for _r in LAKE_RECTS:
        for _lx in range(LAKE_W[0] + _r[0], LAKE_W[0] + _r[2] + 1):
            for _lz in range(LAKE_W[2] + _r[1], LAKE_W[2] + _r[3] + 1):
                LEVEL[(_lx - ANCHOR_W[0], _lz - ANCHOR_W[2])] = LAKE_W[1] - 1 - ANCHOR_W[1]

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
        # ...and the lakefront, which is the third. The pier, its basin and its beach used
        # to be dug by the Act II finale, at runtime, into whatever the road had left there
        # -- so the plan never had to know about them. They are day one now (group
        # day1_lakefront), they level a 29x29 yard to lake.y-1, and the lantern road runs
        # straight through the middle of it. Measured on the first shipped-world build: a
        # 3-block road step and an 8-block bare face, both at the lakefront's own edge.
        if in_lake(x, z):
            return LAKE_W[1] - 1
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

    # =========================================================================
    # THE SHOULDERS.  A road is never a trench.
    #
    # The three-block carriageway used to be the whole of the road: everything outside it
    # was skirt, and the skirt is allowed to climb a block a ring. So wherever the road ran
    # a block or two below the meadow -- which is most of a staircase laid across a hillside
    # -- the very first column off the gravel was already a step up, the next one another,
    # and the road came out as a slot with bare dirt sides. Measured on the shipped world:
    # the first column outside the paving stood two blocks over the road surface, and the
    # first-join screenshots show the result.
    #
    # So the road carries its own shoulder: SHOULDER_MIN..SHOULDER_MAX columns either side,
    # held at the carriageway's OWN level (or one below it, where the ground is already
    # falling away -- a shoulder may drop, it may never rise). Two things come out of that:
    #
    #   * the column next to the paving, and the one next to THAT, are never more than a
    #     block over the road -- which is the whole of `road_banks` in nature_check.py; and
    #   * the bank that does remain starts at the shoulder's outer edge, so the skirt's
    #     one-block-a-ring climb reads as a grass slope three to five blocks deep rather
    #     than a wall at the kerb.
    #
    # The shoulder's WIDTH is drawn from the same coherent hash as the pad feathering, in
    # HOLD_BLOCK-sized cells, so the edge of the cut wanders in plan instead of running dead
    # straight beside the road for a hundred and ninety columns. That is the difference
    # between a verge and a kerbstone.
    # =========================================================================
    SHOULDER_MIN, SHOULDER_MAX = 2, 4
    ROAD_SHOULDER = {}                       # (x,z) -> (distance from centre, world Y)
    for _i, (_x, _z) in enumerate(ROAD_CENTRE):
        _y = ROAD_Y[_i]
        _j = min(_i + 1, len(ROAD_CENTRE) - 1)
        _k = max(_i - 1, 0)
        _dx = ROAD_CENTRE[_j][0] - ROAD_CENTRE[_k][0]
        _dz = ROAD_CENTRE[_j][1] - ROAD_CENTRE[_k][1]
        _px, _pz = (0, 1) if abs(_dx) >= abs(_dz) else (1, 0)
        for _side in (-1, 1):
            _w = SHOULDER_MIN + cell_hash((_x + 40 * _side) // HOLD_BLOCK * HOLD_BLOCK,
                                          (_z + 40 * _side) // HOLD_BLOCK * HOLD_BLOCK) \
                % (SHOULDER_MAX - SHOULDER_MIN + 1)
            for _o in range(2, _w + 1):
                _cx, _cz = _x + _px * _side * _o, _z + _pz * _side * _o
                _rel = (_cx - ANCHOR_W[0], _cz - ANCHOR_W[2])
                if (_cx, _cz) in ROAD_CELLS or _rel in LEVEL:
                    continue                 # the plaza, a pad or a street already owns it
                if wet(_rel[0], _rel[1]):
                    continue                 # the lake keeps its shore
                _n = surface(_cx, _cz)
                if _n is None:
                    continue
                # never above the road; never more than a block below it either, so the
                # shoulder is a verge and not the top of a fill.
                _sy = max(_y - 1, min(_y, _n))
                _have = ROAD_SHOULDER.get((_cx, _cz))
                if _have is None or (_o, _sy) < _have:
                    ROAD_SHOULDER[(_cx, _cz)] = (_o, _sy)
    # ---- the ROAD HEAD: a landing, not a lip -------------------------------------------
    # The road stops at her feet on purpose -- it is where she wakes up -- but the first
    # build with the arrival moved measured what that costs: the world put her down on the
    # last column of the carriageway and the harness read her back a block later, a block
    # lower, having stepped off the end of it. So the ground the road stops on is part of
    # the arrival. The three columns beyond the last one, five wide, are held at the
    # carriageway's own level: she wakes on a level patch of meadow with the road under her
    # feet and the meadow walking away from it a block a ring, like everywhere else.
    ROAD_HEAD = 3
    _hx, _hz = ROAD_CENTRE[-1]
    _hdx = _hx - ROAD_CENTRE[-2][0]
    _hdz = _hz - ROAD_CENTRE[-2][1]
    _hpx, _hpz = (0, 1) if abs(_hdx) >= abs(_hdz) else (1, 0)
    _hy = ROAD_Y[-1]
    for _st in range(1, ROAD_HEAD + 1):
        for _o in range(-2, 3):
            _cx = _hx + _hdx * _st + _hpx * _o
            _cz = _hz + _hdz * _st + _hpz * _o
            _rel = (_cx - ANCHOR_W[0], _cz - ANCHOR_W[2])
            if (_cx, _cz) in ROAD_CELLS or _rel in LEVEL or (_cx, _cz) in ROAD_SHOULDER:
                continue
            if wet(_rel[0], _rel[1]) or surface(_cx, _cz) is None:
                continue
            ROAD_SHOULDER[(_cx, _cz)] = (2, _hy)
            LEVEL.setdefault(_rel, _hy - ANCHOR_W[1])

    for (_cx, _cz), (_o, _sy) in ROAD_SHOULDER.items():
        LEVEL.setdefault((_cx - ANCHOR_W[0], _cz - ANCHOR_W[2]), _sy - ANCHOR_W[1])
        _top = max(_sy + 3, canopy(_cx, _cz) or _sy)
        ROAD_CMDS.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                         % (_cx, _sy + 1, _cz, _cx, _top, _cz))
        ROAD_CMDS.append('setblock ~%d ~%d ~%d %s'
                         % (_cx, _sy, _cz, surf_mat(_cx, _cz)))
        ROAD_CMDS.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:dirt replace minecraft:air'
                         % (_cx, _sy - 4, _cz, _cx, _sy - 1, _cz))
    print('  road shoulders: %d columns held at the carriageway\'s level, %d..%d wide'
          % (len(ROAD_SHOULDER), SHOULDER_MIN, SHOULDER_MAX))

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
    # ...and the band they are spread over runs almost to the far end now. The road used to
    # STOP where she stood, so the last station had to hold back from the end; the road runs
    # on past her arrival instead, and the two posts at its last station are the two she can
    # see from the moment the world loads.
    _lo, _hi = 8, len(ROAD_CENTRE) - 6
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

    # ---- the three cells on the square a lamp post may not stand on ---------------------
    # Measured on the 2026-09-05 build: ROAD_LAMPS' first station lands on the anchor
    # itself, so day1_lamps (which runs LAST, so nothing pads over a post) wrote an oak
    # fence straight over the town waystone act1_square had just set at anchor + [0,1,0].
    # The square came out with a lamp post in the middle of it and no waystone at all.
    # These are the cells the square owns: the waystone, the Surveyor's Stake socket, and
    # the noticeboard. A post that lands on one is nudged along until it is clear.
    RESERVED_XZ = {(ANCHOR_W[0], ANCHOR_W[2]),                 # the town waystone
                   (ANCHOR_W[0], ANCHOR_W[2] - 2),             # the stake socket
                   (ANCHOR_W[0], ANCHOR_W[2] - 5)}             # the noticeboard
    _taken = set()
    for _i, _p in enumerate(LAMPS_40):
        _k = (_p[0], _p[2])
        _n = 0
        while (_k in RESERVED_XZ or _k in _taken) and _n < 8:
            _n += 1
            _k = (_p[0] + 2 * _n, _p[2])
            if _k in RESERVED_XZ or _k in _taken:
                _k = (_p[0] - 2 * _n, _p[2])
        if _k != (_p[0], _p[2]):
            print('  lamp %d moved off a reserved square cell: %s -> %s'
                  % (_i + 1, (_p[0], _p[2]), _k))
            _p[0], _p[2] = _k[0], _k[1]
            _p[1] = dsurf(_p[0], _p[2]) + 1
        _taken.add(_k)

    # ---- the FORTIETH post is Josie's own, and it ships BARE ----------------------------
    # Every number in the pack says so: Q74 is "lamps 39 of 40, one post stays bare on
    # purpose: Josie's porch", and Q90 is the lantern that goes on it. The registry had
    # forty town-and-road posts AND a porch post the Q74 scene set down at runtime, which is
    # forty-one lights and a runtime build. So the last street post is dropped and the porch
    # takes its place: thirty-nine posts ship with a dark cage lamp on them, the fortieth
    # ships as a bare fence, and Q90 is the only thing that ever puts a light on it.
    LAMP_BARE = len(LAMPS_40) - 1
    LAMPS_40[LAMP_BARE] = [HEARTH_W[0] + 3, HEARTH_W[1] + 1, HEARTH_W[2]]
    print('  lamp 40 is the bare post on Josie\'s porch at %s (Q90)' % LAMPS_40[LAMP_BARE])

    LAMP_CMDS = ['# Forty lamp posts, standing from the first second and every one of them',
                 '# dark. `setblock <LAMP_LIT>` on the head is the whole of lighting one, and',
                 '# that is the only thing the story ever does to them. The fortieth -- the',
                 '# last entry, on Josie\'s porch -- ships as a BARE post: Q90 is its lamp.']
    for _i, _p in enumerate(LAMPS_40):
        LAMP_CMDS.append('setblock ~%d ~%d ~%d minecraft:cobblestone' % (_p[0], _p[1] - 1, _p[2]))
        LAMP_CMDS.append('setblock ~%d ~%d ~%d %s' % (_p[0], _p[1], _p[2], POST))
        if _i == LAMP_BARE:
            LAMP_CMDS.append('setblock ~%d ~%d ~%d minecraft:air' % (_p[0], _p[1] + 1, _p[2]))
            continue
        LAMP_CMDS.append('setblock ~%d ~%d ~%d %s' % (_p[0], _p[1] + 1, _p[2], LAMP_DARK))

    # =========================================================================
    # The spawn signpost. Four blocks along the road from where she stands, beside it, and
    # TURNED TO FACE HER, so the first thing in frame is a direction rather than a quest
    # card. It used to be four blocks along the road from the town end -- which is where
    # she used to wake up -- so with the arrival moved to the far side of the farm it moves
    # with her: the road's last four columns are the ones she is standing on.
    #
    # Which way it faces is computed, not typed. `rotation` counts sixteen steps clockwise
    # from SOUTH, so the facing vector back down the road toward her is turned into a step
    # here; the old hard-coded `rotation=8` was north because the old road ran north, and it
    # would have shown her the blank back of the sign on any other bearing.
    _sp_i = max(0, len(ROAD_CENTRE) - 5)
    while _sp_i < len(ROAD_CENTRE) - 1 and _pin(*ROAD_CENTRE[_sp_i]) is not None:
        _sp_i += 1
    _sx, _sz = ROAD_CENTRE[_sp_i]
    _bx, _bz = ROAD_CENTRE[min(_sp_i + 1, len(ROAD_CENTRE) - 1)]
    _fx, _fz = _bx - _sx, _bz - _sz            # points from the sign toward spawn
    _spx, _spz = (0, 1) if abs(_fx) >= abs(_fz) else (1, 0)
    _SIGN_ROT = int(round(math.atan2(-_fx, _fz) / (2 * math.pi) * 16)) % 16
    SIGNPOST = None
    for _side in (1, -1):
        _cx, _cz = _sx + _spx * 2 * _side, _sz + _spz * 2 * _side
        if (_cx, _cz) not in ROAD_CELLS:
            SIGNPOST = [_cx, dsurf(_cx, _cz) + 1, _cz]
            break
    if SIGNPOST is None:
        SIGNPOST = [_sx + 2, dsurf(_sx + 2, _sz) + 1, _sz]
    SIGN_CMDS = [
        'setblock ~%d ~%d ~%d minecraft:cobblestone' % (SIGNPOST[0], SIGNPOST[1] - 1, SIGNPOST[2]),
        'setblock ~%d ~%d ~%d %s' % (SIGNPOST[0], SIGNPOST[1], SIGNPOST[2], POST),
        'setblock ~%d ~%d ~%d minecraft:oak_sign[rotation=%d]{front_text:{messages:['
        '\'{"text":"KETTLE FARM"}\',\'{"text":"follow the road"}\',\'{"text":""}\','
        '\'{"text":"LITTLE KETTLE"}\'],color:"gray"}}'
        % (SIGNPOST[0], SIGNPOST[1] + 1, SIGNPOST[2], _SIGN_ROT),
    ]
    # the lantern stands on the ground beside the post, one step further off the road:
    # on top of the post it would be sitting on the sign, which is not something a lantern
    # can stand on, and it drops the moment the chunk ticks.
    _lx = SIGNPOST[0] + (SIGNPOST[0] - _sx and (1 if SIGNPOST[0] > _sx else -1))
    _lz = SIGNPOST[2] + (SIGNPOST[2] - _sz and (1 if SIGNPOST[2] > _sz else -1))
    SIGN_CMDS.append('setblock ~%d ~%d ~%d minecraft:lantern[hanging=false]'
                     % (_lx, dsurf(_lx, _lz) + 1, _lz))
    print('  signpost at %s, %d blocks from spawn, facing rotation %d (back down the road)'
          % (str(SIGNPOST), int(round(math.hypot(SIGNPOST[0] - SPAWN_W[0],
                                                 SIGNPOST[2] - SPAWN_W[2]))), _SIGN_ROT))

    # =========================================================================
    # THE ARRIVAL, measured rather than hoped for.
    #
    # Four things the first frame has to be, all of them checked here so a re-run on a new
    # site cannot quietly lose them:
    #   1. she is facing along the road, toward the farm;
    #   2. nothing the plan builds stands within SPAWN_CLEAR blocks of her except the road,
    #      its shoulder and the signpost -- the old spawn opened on a wall of plaza benches;
    #   3. the town is out of sight (solved above, re-stated here for the record); and
    #   4. two lamp posts ARE in sight, so the road reads as the lantern road from the
    #      first second.
    # =========================================================================
    SPAWN_CLEAR = 8
    _sdx = ROAD_CENTRE[-2][0] - ROAD_CENTRE[-1][0]
    _sdz = ROAD_CENTRE[-2][1] - ROAD_CENTRE[-1][1]
    SPAWN_YAW = round(-math.degrees(math.atan2(_sdx, _sdz)), 1)

    _near = []
    for _k2, _g2 in GROUPS.items():
        _o2 = OFF.get(_g2['origin'], [0, 0, 0])
        _base = {'world': [0, 0, 0],
                 'home': [HEARTH_W[0], HEARTH_W[1] + 1, HEARTH_W[2]]}.get(
            _g2['origin'], [ANCHOR_W[0] + _o2[0], ANCHOR_W[1] + _o2[1],
                            ANCHOR_W[2] + _o2[2]])
        for _c3 in _g2['cmds']:
            for _b3 in write_boxes(_c3):
                if (max(_b3[0], _b3[3]) + _base[0] >= SPAWN_W[0] - SPAWN_CLEAR and
                        min(_b3[0], _b3[3]) + _base[0] <= SPAWN_W[0] + SPAWN_CLEAR and
                        max(_b3[2], _b3[5]) + _base[2] >= SPAWN_W[2] - SPAWN_CLEAR and
                        min(_b3[2], _b3[5]) + _base[2] <= SPAWN_W[2] + SPAWN_CLEAR):
                    _near.append('%s: %s' % (_k2, _c3[:70]))
    if _near:
        raise SystemExit('plan_town: %d thing(s) stand within %d blocks of spawn: %s'
                         % (len(_near), SPAWN_CLEAR, '; '.join(_near[:4])))

    _allnear = [_p for _p in LAMPS_40
                if max(abs(_p[0] - SPAWN_W[0]), abs(_p[2] - SPAWN_W[2])) <= SPAWN_CLEAR]
    if _allnear:
        raise SystemExit('plan_town: %d lamp post(s) inside the %d-block clear at spawn: %s'
                         % (len(_allnear), SPAWN_CLEAR, str(_allnear[:3])))
    _lampd = sorted((math.hypot(_p[0] - SPAWN_W[0], _p[2] - SPAWN_W[2]), _p)
                    for _p in ROAD_LAMPS)
    if len(_lampd) < 2:
        raise SystemExit('plan_town: the lantern road has fewer than two posts on it')

    def _sees(a, b):
        """Straight sightline over the DESIGN surface between two eye-height points."""
        dist = math.hypot(b[0] - a[0], b[2] - a[2])
        if dist < 2:
            return True
        for _s in range(2, int(dist)):
            _f = _s / dist
            _px = int(round(a[0] + (b[0] - a[0]) * _f))
            _pz = int(round(a[2] + (b[2] - a[2]) * _f))
            if dsurf(_px, _pz) > (a[1] + 1) + ((b[1] + 1) - (a[1] + 1)) * _f + 1.0:
                return False
        return True

    SPAWN_LAMPS = []
    for _d3, _p3 in _lampd[:4]:
        if _sees(SPAWN_W, _p3):
            SPAWN_LAMPS.append((round(_d3, 1), list(_p3)))
        if len(SPAWN_LAMPS) == 2:
            break
    if len(SPAWN_LAMPS) < 2:
        raise SystemExit('plan_town: fewer than two lantern-road posts are visible from '
                         'spawn (nearest four at %s)'
                         % str([round(_d3, 1) for _d3, _ in _lampd[:4]]))
    if SPAWN_LAMPS[1][0] > 40:
        raise SystemExit('plan_town: the second visible post is %.0f blocks from spawn'
                         % SPAWN_LAMPS[1][0])
    print('  arrival: yaw %.1f toward the farm, nothing built within %d blocks, first two '
          'road posts in sight at %.0f and %.0f blocks (%s, %s)'
          % (SPAWN_YAW, SPAWN_CLEAR, SPAWN_LAMPS[0][0], SPAWN_LAMPS[1][0],
             str(SPAWN_LAMPS[0][1]), str(SPAWN_LAMPS[1][1])))

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

    # ---- where the gate post stands -----------------------------------------------------
    # Home-relative, solved against the finished road. Candidates run outward from the old
    # spot along the road's own cross direction; the first one whose column is neither
    # paving nor shoulder wins, so the sign is always two clear of the carriageway however
    # the road happens to leave the gate.
    GATE_POST = (0, 10)
    for _gc in ((0, 10), (3, 10), (-3, 10), (3, 12), (-3, 12), (0, 13), (5, 10), (-5, 10)):
        _gw = (HEARTH_W[0] + _gc[0], HEARTH_W[2] + _gc[1])
        if _gw not in ROAD_CELLS and _gw not in ROAD_SHOULDER:
            GATE_POST = _gc
            break
    # face the sign back down the road she came up, the same arithmetic as the signpost.
    _gi = min(range(len(ROAD_CENTRE)),
              key=lambda i: (ROAD_CENTRE[i][0] - GATE_W[0]) ** 2
              + (ROAD_CENTRE[i][1] - GATE_W[2]) ** 2)
    _gj = min(_gi + 2, len(ROAD_CENTRE) - 1)
    GATE_ROT = int(round(math.atan2(-(ROAD_CENTRE[_gj][0] - ROAD_CENTRE[_gi][0]),
                                    ROAD_CENTRE[_gj][1] - ROAD_CENTRE[_gi][1])
                         / (2 * math.pi) * 16)) % 16
    print('  farm gate post at home + %s (rotation %d); the road runs through the gate now'
          % (str(GATE_POST), GATE_ROT))

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
        '# the gate: the marker that says you have arrived.',
        '# ...beside the road, not in it. It used to sit at home + [0,0,10] because the road',
        '# only ever ARRIVED at the gate along z = home+8 and stopped. The road runs THROUGH',
        '# the gate now -- she comes up it from the far side of the farm and carries on past',
        '# the yard to the town -- so home + [0,0,10] is under the carriageway. The post is',
        '# solved against the road it stands beside instead of typed: the first candidate',
        '# clear of the paving AND of its shoulder, so it is never a step at the kerb.',
        'setblock ~%d ~0 ~%d minecraft:oak_fence' % (GATE_POST[0], GATE_POST[1]),
        'setblock ~%d ~1 ~%d minecraft:oak_sign[rotation=%d]{front_text:{messages:['
        '\'{"text":"KETTLE FARM"}\',\'{"text":""}\',\'{"text":"J. Kettle"}\','
        '\'{"text":"mind the weeds"}\'],color:"gray"}}'
        % (GATE_POST[0], GATE_POST[1], GATE_ROT),
    ])

    group('day1_cottage', 'home', DAY1_COTTAGE)

    # =========================================================================
    # 11.5b  THE CELLAR.  The one room in the pack the player DIGS.
    #
    # Q5's own text has always described a shipped world: "There is a trapdoor under the
    # ash in the old kitchen ... Dig the gravel out of the stairs beneath it -- about 40
    # marked blocks ... At the bottom: a sealed iron door, no handle, four words in her
    # chalk." Nothing built it. `/valley scene cellar` ran a 7x4x7 stone-brick box out of a
    # datapack function AT THE CLAIMING PLAYER, which is the exact class of runtime edit
    # this whole rewrite exists to delete -- and on the shipped world the ground under the
    # cottage is solid stone from y-5 down, so there was no cellar at all.
    #
    # So it is here, on day one, and the story only opens the door.
    #
    #   * a real stone-brick flight, ten treads, descending north out of the kitchen;
    #   * forty blocks of gravel filling the void ABOVE the treads -- two wide, two tall,
    #     ten steps, and the top course is flush with the kitchen floor, so the gravel
    #     patch in the floorboards IS the mark the quest text promises;
    #   * a room at the bottom with her chalk, her tool chest, the marked plinth the
    #     Cellar Waystone goes on, and a sealed iron door in the north wall with nothing
    #     but rock behind it. Q55 opens the door; it is a state change, not a build.
    #
    # Everything is HOME-relative: home is the waystone cell, the kitchen floor is home-1.
    # =========================================================================
    CELLAR_STEPS = 10
    CELLAR_W = (1, 2)              # the flight is x = home+1 .. home+2
    # step i: tread at y home-3-i, z home-2-i; the two cells of headroom above it are the
    # gravel. 2 wide x 2 tall x 10 steps = 40.
    CELLAR_ROOM = {                # all home-relative
        'shell': (-2, -13, -19, 5, -8, -11),
        'floor_y': -12,
        'stand': (1, -11, -15),
        'door': (1, -11, -19),
        # THE LOCK. One block of rock buried behind the door, out of sight, which Q54 turns
        # into a redstone block. An IRON door cannot be held open by a setblock: vanilla's
        # DoorBlock#neighborChanged recomputes OPEN from the redstone signal for any door
        # that cannot be opened by hand, so a door set open with nothing powering it snaps
        # shut on the next block update beside it. Measured: `/valley scene q54` reported
        # played, wrote both halves open, and the region file came back `open=false`.
        # Josie's door has no handle. It has a lock, and this is the lock.
        'lock': (1, -11, -20),
        'chalk': (0, -10, -18),
        'chest': (4, -11, -17),
        'plinth': (-1, -12, -17),
    }
    _cs = CELLAR_ROOM['shell']
    DAY1_CELLAR = [
        '# The cellar. GENERATED by tools/scripts/plan_town.py. Home-relative.',
        '# Ten treads, forty blocks of gravel on top of them, and a sealed iron door at the',
        '# bottom. The story never builds this -- Q5 digs it out and Q55 opens the door.',
        '# 1. ROCK for the flight to be cut out of -- plain stone, not dressed brick, and',
        '#    topping out at home-2, one course under the yard.',
        '#    Two measurements, both on the cottage plot:',
        '#      * filled to home-1 it broke the surface as a 4x12 patch of stone in the',
        '#        middle of the seed bed;',
        '#      * filled with STONE BRICK it stayed buried and still failed, because seven',
        '#        courses of dressed stone under one course of turf is not something the',
        '#        terrain probe will read as land (paving counts as ground only two courses',
        '#        deep), and it reported a 12-block face where there is a garden.',
        '#    Rock is what she cut the stair out of anyway. Only the ROOM is dressed.',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone'
        % (CELLAR_W[0] - 1, -3 - CELLAR_STEPS - 1, -2 - CELLAR_STEPS - 1,
           CELLAR_W[1] + 1, -2, -1),
        '# 2. the room at the bottom: shell, then hollow, then a stone floor',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone_bricks' % _cs,
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
        % (_cs[0] + 1, _cs[1] + 1, _cs[2] + 1, _cs[3] - 1, _cs[4] - 1, _cs[5] - 1),
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone_bricks'
        % (_cs[0] + 1, _cs[1], _cs[2] + 1, _cs[3] - 1, _cs[1], _cs[5] - 1),
    ]
    for _i in range(CELLAR_STEPS):
        _ty, _tz = -3 - _i, -2 - _i
        DAY1_CELLAR += [
            # the tread, and solid rock under it so the flight cannot be undermined
            'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone_bricks'
            % (CELLAR_W[0], _cs[1], _tz, CELLAR_W[1], _ty, _tz),
            'setblock ~%d ~%d ~%d minecraft:stone_brick_stairs[facing=north,half=bottom]'
            % (CELLAR_W[0], _ty, _tz),
            'setblock ~%d ~%d ~%d minecraft:stone_brick_stairs[facing=north,half=bottom]'
            % (CELLAR_W[1], _ty, _tz),
            # the two cells of headroom, filled: THIS is the forty blocks of gravel
            'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:gravel'
            % (CELLAR_W[0], _ty + 1, _tz, CELLAR_W[1], _ty + 2, _tz),
        ]
    DAY1_CELLAR += [
        '# 3. the sealed iron door. No handle: nothing in the world can open it until Q55.',
        'setblock ~%d ~%d ~%d minecraft:stone_bricks'
        % (CELLAR_ROOM['door'][0], CELLAR_ROOM['door'][1] + 2, CELLAR_ROOM['door'][2]),
        'setblock ~%d ~%d ~%d minecraft:chiseled_stone_bricks'
        % (CELLAR_ROOM['door'][0] - 1, CELLAR_ROOM['door'][1], CELLAR_ROOM['door'][2]),
        'setblock ~%d ~%d ~%d minecraft:chiseled_stone_bricks'
        % (CELLAR_ROOM['door'][0] + 1, CELLAR_ROOM['door'][1], CELLAR_ROOM['door'][2]),
        'setblock ~%d ~%d ~%d minecraft:iron_door[facing=north,half=lower,hinge=left,open=false,powered=false]'
        % CELLAR_ROOM['door'],
        'setblock ~%d ~%d ~%d minecraft:iron_door[facing=north,half=upper,hinge=left,open=false,powered=false]'
        % (CELLAR_ROOM['door'][0], CELLAR_ROOM['door'][1] + 1, CELLAR_ROOM['door'][2]),
        '# ...and the lock: one block of rock behind it, buried, that Q54 turns to redstone.',
        'setblock ~%d ~%d ~%d minecraft:stone' % CELLAR_ROOM['lock'],
        'setblock ~%d ~%d ~%d minecraft:stone'
        % (CELLAR_ROOM['lock'][0], CELLAR_ROOM['lock'][1] + 1, CELLAR_ROOM['lock'][2]),
        '# 4. her chalk, her tool chest, and the plinth the Cellar Waystone goes on',
        'setblock ~%d ~%d ~%d minecraft:oak_wall_sign[facing=south]{front_text:{messages:['
        '\'{"text":"Not yet."}\',\'{"text":""}\',\'{"text":"- J.K."}\',\'{"text":""}\'],color:"gray"}}'
        % CELLAR_ROOM['chalk'],
        'setblock ~%d ~%d ~%d minecraft:chest[facing=west]' % CELLAR_ROOM['chest'],
        'setblock ~%d ~%d ~%d minecraft:polished_andesite' % CELLAR_ROOM['plinth'],
        'setblock ~%d ~%d ~%d minecraft:lantern[hanging=false]'
        % (_cs[0] + 1, _cs[1] + 1, _cs[2] + 1),
        'setblock ~%d ~%d ~%d minecraft:lantern[hanging=false]'
        % (_cs[3] - 1, _cs[1] + 1, _cs[2] + 1),
        'setblock ~%d ~%d ~%d minecraft:lantern[hanging=true]'
        % (CELLAR_ROOM['stand'][0], _cs[4] - 1, CELLAR_ROOM['stand'][2]),
    ]
    group('day1_cellar', 'home', DAY1_CELLAR)
    print('  cellar: %d treads, %d blocks of gravel, sealed iron door at home + %s'
          % (CELLAR_STEPS, CELLAR_STEPS * 4, str(CELLAR_ROOM['door'])))

    # =========================================================================
    # 11.5c  THE ADIT.  Q65's forty marked blocks of fall.
    #
    # "Mine the 40 marked blocks out of the fallen adit into Josie's Works, then place the
    # Waystone on the marked plinth inside." The Works chamber is sealed on all six sides
    # and there was no way in at all: the only opening anything ever made was
    # excavateWorks(), a runtime fill. So the adit is here, on day one -- an open mouth on
    # the verge beside the East Lane, a lined shaft, and forty blocks of cobblestone fall
    # in it. Nothing in the story digs it; the player does, with the Works Pick.
    #
    # Works-relative. The mark is the chamber floor's centre; the shell runs y-1..+4.
    # =========================================================================
    ADIT_XZ = ((0, 6), (1, 6), (0, 7), (1, 7))       # a 2x2 shaft, works-relative x/z
    ADIT_TOP = 11                                    # works + 11 is the meadow surface
    ADIT_FALL = (0, 10)                              # ten courses of cobblestone: 40 blocks
    DAY1_ADIT = [
        '# The fallen adit into the Works. GENERATED by plan_town.py. Works-relative.',
        '# Forty blocks of cobblestone in a lined shaft, and a mouth on the verge.',
    ]
    for _dx, _dz in ADIT_XZ:
        # line every column the shaft passes through, so it never opens into dirt or a cave
        for _lx in (-1, 0, 1):
            for _lz in (-1, 0, 1):
                if (_dx + _lx, _dz + _lz) in ADIT_XZ:
                    continue
                # ...and it stops ONE COURSE SHORT of the surface. Lined all the way up,
                # the mouth is a stone-brick collar twelve courses deep standing where the
                # verge was, and both the terrain probe and a person read that as a wall:
                # nature_check scored a 14-block bare face on it. Under the top course the
                # lining is invisible; at the top course the ground is the ground, with a
                # two-by-two hole in it. And the lining is plain STONE, not dressed brick:
                # a fallen adit through a hillside is a hole in rock, and eleven courses of
                # stone brick read to the terrain probe as a wall with no land under it.
                DAY1_ADIT.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:stone'
                                 % (_dx + _lx, 0, _dz + _lz, _dx + _lx, ADIT_TOP - 1, _dz + _lz))
    DAY1_ADIT += [
        '# the shaft itself: open from the mouth down to the top of the fall',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
        % (ADIT_XZ[0][0], ADIT_FALL[1] + 1, ADIT_XZ[0][1],
           ADIT_XZ[3][0], ADIT_TOP, ADIT_XZ[3][1]),
        '# THE FALL. Forty blocks. This is Q65.',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:cobblestone'
        % (ADIT_XZ[0][0], ADIT_FALL[0] + 1, ADIT_XZ[0][1],
           ADIT_XZ[3][0], ADIT_FALL[1], ADIT_XZ[3][1]),
        '# ...and the chamber floor under it stays open, so the last block drops you in',
        'fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
        % (ADIT_XZ[0][0], 0, ADIT_XZ[0][1], ADIT_XZ[3][0], 0, ADIT_XZ[3][1]),
        '# the mouth, on the verge: a stone-brick rim, a post and Tobin\'s sign',
        'setblock ~%d ~%d ~%d minecraft:oak_fence' % (ADIT_XZ[0][0] - 1, ADIT_TOP, ADIT_XZ[0][1] - 1),
        'setblock ~%d ~%d ~%d minecraft:lantern[hanging=false]'
        % (ADIT_XZ[0][0] - 1, ADIT_TOP + 1, ADIT_XZ[0][1] - 1),
        'setblock ~%d ~%d ~%d minecraft:oak_sign[rotation=8]{front_text:{messages:['
        '\'{"text":"THE WORKS"}\',\'{"text":"adit - fallen"}\',\'{"text":"40 blocks"}\','
        '\'{"text":"- T. Gale"}\'],color:"gray"}}'
        % (ADIT_XZ[1][0] + 1, ADIT_TOP, ADIT_XZ[1][1] - 1),
        '# the marked plinth Q65 stands the Works Waystone on, and the andesite panel the',
        '# Act IV lever hangs off. Both are fixtures of the room; neither is a build.',
        'setblock ~0 ~0 ~-5 minecraft:polished_andesite',
        'setblock ~%d ~%d ~%d minecraft:polished_andesite' % tuple(PANEL),
    ]
    group('day1_adit', 'works', DAY1_ADIT)
    print('  adit: %d blocks of fall, mouth at works + [%d, %d, %d]'
          % ((ADIT_FALL[1] - ADIT_FALL[0]) * 4, ADIT_XZ[0][0], ADIT_TOP, ADIT_XZ[0][1]))

    # =========================================================================
    # 11.5d  The noticeboard and the Surveyor's Stake socket, on the square.
    # Both used to be built at runtime -- the board by finaleAct3's `place template`, the
    # socket by nothing at all, because Q7 used to accept a stake anywhere in the valley.
    # =========================================================================
    DAY1_BOARD = [
        '# The noticeboard, and the socket the Surveyor\'s Stake goes into. Anchor-relative.',
        'place template valley:noticeboard ~0 ~1 ~-5',
        '# the socket: chiselled, two blocks north of the town waystone, with the sign that',
        '# says what it is for. Q7 is "put the stake in the socket" now, not "find flat ground".',
        'setblock ~0 ~0 ~-2 minecraft:chiseled_stone_bricks',
        'setblock ~0 ~1 ~-2 minecraft:air',
        'setblock ~-1 ~0 ~-2 minecraft:polished_andesite',
        'setblock ~1 ~0 ~-2 minecraft:polished_andesite',
        'setblock ~-1 ~1 ~-2 minecraft:oak_sign[rotation=12]{front_text:{messages:['
        '\'{"text":"THE SQUARE"}\',\'{"text":"stake goes here"}\',\'{"text":""}\','
        '\'{"text":"- B. Tolliver"}\'],color:"gray"}}',
    ]
    group('day1_board', 'anchor', DAY1_BOARD)

    # =========================================================================
    # 11.5e  THE LAKEFRONT.  The pier, the basin and the Lantern Float's water.
    #
    # There is no lake at the Lake Waystone. The seed's water is four hundred blocks away;
    # what the pack calls "the lake" is a basin the Act II finale DUG -- 29x29 levelled to
    # stone, eight courses cleared to air, five `replace minecraft:water` plugs and three
    # courses of source water poured back in -- with a pier template pasted into the middle
    # of it, at the moment twelve people were standing on the spot for a festival.
    #
    # All of it is day one now. The basin, the beach, the pier, the rails, the candle
    # holders, the twelve lantern rafts and the lily pads are standing before anybody logs
    # in; Act II lights the candles, brings the town down to the water and hands out the
    # fireworks. The pier is a pier from the first walk down the road, which is also the
    # only reason Q22's fishing and Q26's Dredge Net have any water to work in before Act II.
    #
    # Lake-mark-relative, exactly as finaleAct2 had it.
    # =========================================================================
    DAY1_LAKE = [
        '# The lakefront. GENERATED by plan_town.py. Lake-mark-relative, and all of it EAST',
        '# of the lantern road, which runs down the yard\'s western kerb.',
        '# 1. the yard: two courses of stone under it, everything above cleared.',
        'fill ~-2 ~1 ~-6 ~16 ~10 ~8 minecraft:air',
        'fill ~-2 ~-2 ~-6 ~16 ~-1 ~8 minecraft:stone',
        '# 2. the beach, laid BEFORE the basin is dug (the basin takes back z 9..16 of it)',
        'fill ~2 ~-1 ~6 ~14 ~-1 ~16 minecraft:sandstone',
        '# 3. the basin: a sealed stone shell, one block proud of the water on all four',
        '#    sides and under it, so a spring, an aquifer or a flooded cave cannot drain it.',
        'fill ~1 ~-4 ~9 ~17 ~-1 ~25 minecraft:stone',
        'fill ~1 ~0 ~10 ~17 ~8 ~25 minecraft:air',
        'fill ~1 ~0 ~9 ~17 ~0 ~9 minecraft:air',
        'fill ~0 ~-5 ~8 ~0 ~3 ~26 minecraft:stone replace minecraft:water',
        'fill ~18 ~-5 ~8 ~18 ~3 ~26 minecraft:stone replace minecraft:water',
        'fill ~0 ~-5 ~8 ~18 ~3 ~8 minecraft:stone replace minecraft:water',
        'fill ~0 ~-5 ~26 ~18 ~3 ~26 minecraft:stone replace minecraft:water',
        'fill ~0 ~-5 ~8 ~18 ~-5 ~26 minecraft:stone replace minecraft:water',
        'fill ~2 ~-3 ~10 ~16 ~-1 ~24 minecraft:water[level=0]',
        '# 4. the shore lip the shell paved over, back in beach sandstone, so the water\'s',
        '#    edge reads as an edge and not as a kerb',
        'fill ~2 ~-1 ~9 ~14 ~-1 ~9 minecraft:sandstone',
        '# 5. the pier, out over the water rather than nine blocks up the middle of the',
        '#    road. Rails closed on both sides -- the template posts its rail only every',
        '#    fourth block, and with a basin under it that is a two-block drop into cold',
        '#    water at a party.',
        'place template valley:pier ~7 ~0 ~6',
        'fill ~7 ~2 ~7 ~7 ~2 ~13 minecraft:oak_fence',
        'fill ~9 ~2 ~7 ~9 ~2 ~13 minecraft:oak_fence',
        'setblock ~8 ~0 ~4 waystones:waystone{WaystoneName:"The Pier"}',
        '# 6. Nella\'s beached boat and her cold fire, at the head of the shingle',
        'setblock ~3 ~0 ~6 minecraft:oak_stairs[facing=east,half=bottom]',
        'setblock ~3 ~0 ~7 minecraft:oak_stairs[facing=east,half=bottom]',
        'setblock ~3 ~0 ~8 minecraft:oak_planks',
        'setblock ~4 ~0 ~7 minecraft:campfire[lit=false]',
        'setblock ~5 ~0 ~8 minecraft:barrel[facing=up]',
        'setblock ~11 ~0 ~6 minecraft:oak_fence',
        'setblock ~11 ~1 ~6 minecraft:lantern[hanging=false]',
    ]
    # =====================================================================
    # THE BOAT SLIP -- a spruce shed on piles over the water, beside the pier.
    #
    # The brief for the lakefront was "a boathouse", and there are two of them: the
    # meadow set's own fisher chalet stands on the shore (act2_boathouse) and this is
    # the covered slip it works out of -- four courses of pile driven into the basin
    # floor, a U of decking round an open bay, a spruce gable over it and a boat
    # floating in the bay with its bow to the lake. It is lake-mark-relative like
    # everything else here, it is west of the pier and east of the lantern road's own
    # kerb, and it is written AFTER the basin, so the water is already standing when
    # the piles go into it.
    # =====================================================================
    SLIP = (2, 6, 11, 17)                       # x0, x1, z0, z1, lake-relative
    _sxc = (SLIP[0] + SLIP[1]) // 2
    DAY1_LAKE.append('# 7. the covered boat slip, west of the pier')
    for _px, _pz in [(SLIP[0], _z) for _z in range(SLIP[2], SLIP[3] + 1)] + \
                    [(SLIP[1], _z) for _z in range(SLIP[2], SLIP[3] + 1)] + \
                    [(_x, SLIP[2]) for _x in range(SLIP[0] + 1, SLIP[1])]:
        DAY1_LAKE.append('fill ~%d ~-3 ~%d ~%d ~-1 ~%d minecraft:spruce_log[axis=y]'
                         % (_px, _pz, _px, _pz))
        DAY1_LAKE.append('setblock ~%d ~0 ~%d minecraft:spruce_planks' % (_px, _pz))
    # the bay: the water the boat sits in, kept clear of deck
    DAY1_LAKE.append('fill ~%d ~0 ~%d ~%d ~5 ~%d minecraft:air'
                     % (SLIP[0] + 1, SLIP[2] + 1, SLIP[1] - 1, SLIP[3]))
    # the back wall, the two side walls and the open front
    DAY1_LAKE.append('fill ~%d ~1 ~%d ~%d ~2 ~%d minecraft:spruce_planks'
                     % (SLIP[0], SLIP[2], SLIP[1], SLIP[2]))
    for _wx in (SLIP[0], SLIP[1]):
        DAY1_LAKE.append('fill ~%d ~1 ~%d ~%d ~1 ~%d minecraft:spruce_planks'
                         % (_wx, SLIP[2] + 1, _wx, SLIP[3] - 1))
        DAY1_LAKE.append('fill ~%d ~2 ~%d ~%d ~2 ~%d minecraft:spruce_fence'
                         % (_wx, SLIP[2] + 1, _wx, SLIP[3] - 1))
        DAY1_LAKE.append('fill ~%d ~1 ~%d ~%d ~2 ~%d minecraft:stripped_spruce_log[axis=y]'
                         % (_wx, SLIP[3], _wx, SLIP[3]))
    # a spruce gable, ridge running down the slip
    for _dx in range(-(SLIP[1] - _sxc), SLIP[1] - _sxc + 1):
        _ry = 5 - abs(_dx)
        _blk = ('minecraft:spruce_slab[type=bottom]' if _dx == 0 else
                'minecraft:spruce_stairs[facing=%s]' % ('west' if _dx < 0 else 'east'))
        DAY1_LAKE.append('fill ~%d ~%d ~%d ~%d ~%d ~%d %s'
                         % (_sxc + _dx, _ry, SLIP[2], _sxc + _dx, _ry, SLIP[3], _blk))
        if _dx:
            DAY1_LAKE.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:spruce_planks'
                             % (_sxc + _dx, _ry + 1, SLIP[2], _sxc + _dx, _ry + 1, SLIP[2]))
    # her nets, her oars, and the boat itself
    DAY1_LAKE += [
        'setblock ~%d ~1 ~%d minecraft:barrel[facing=up]' % (SLIP[0] + 1, SLIP[2]),
        'setblock ~%d ~1 ~%d minecraft:stripped_spruce_log[axis=x]' % (SLIP[1] - 1, SLIP[2]),
        # ...and the boat in the bay. Built, not summoned: valley_build filters `summon`
        # out of a day-one build, so a boat entity here would simply never exist. Four
        # waterlogged pieces sitting in the water surface read as a hull from the pier.
        'setblock ~%d ~-1 ~%d minecraft:oak_stairs[facing=north,half=top,waterlogged=true]'
        % (_sxc, SLIP[3] - 4),
        'setblock ~%d ~-1 ~%d minecraft:oak_slab[type=top,waterlogged=true]'
        % (_sxc, SLIP[3] - 3),
        'setblock ~%d ~-1 ~%d minecraft:oak_slab[type=top,waterlogged=true]'
        % (_sxc, SLIP[3] - 2),
        'setblock ~%d ~-1 ~%d minecraft:oak_stairs[facing=south,half=top,waterlogged=true]'
        % (_sxc, SLIP[3] - 1),
    ]
    SLIP_CELLS = set((x, z) for x in range(SLIP[0], SLIP[1] + 1)
                     for z in range(SLIP[2], SLIP[3] + 1))

    # the twelve rafts: a lantern on a waterlogged TOP slab, whose upper face IS the block
    # boundary, so it sits flush with the water and still supports the lantern.
    # Anything the slip is standing on is dropped: a lantern raft under a boathouse floor
    # is a lantern in a joist.
    for _rx, _rz in ((3, 13), (7, 12), (11, 14), (15, 12), (2, 18), (6, 17), (10, 19),
                     (14, 17), (4, 22), (9, 23), (13, 21), (16, 23)):
        if (_rx, _rz) in SLIP_CELLS:
            continue
        DAY1_LAKE.append('setblock ~%d ~-1 ~%d minecraft:oak_slab[type=top,waterlogged=true]'
                         % (_rx, _rz))
        DAY1_LAKE.append('setblock ~%d ~0 ~%d minecraft:lantern[hanging=false]' % (_rx, _rz))
    for _gx, _gz in ((3, 15), (16, 19), (8, 21)):
        if (_gx, _gz) in SLIP_CELLS:
            continue
        DAY1_LAKE.append('setblock ~%d ~0 ~%d ribbits:giant_lilypad' % (_gx, _gz))
    for _lx2, _lz2 in ((5, 11), (9, 11), (13, 11), (3, 13), (16, 14), (4, 16), (12, 16),
                       (8, 15), (15, 20), (2, 21), (11, 24), (6, 24)):
        if (_lx2, _lz2) in SLIP_CELLS:
            continue
        DAY1_LAKE.append('setblock ~%d ~0 ~%d minecraft:lily_pad' % (_lx2, _lz2))
    for _cz in (8, 10, 12):
        for _cx in (7, 9):
            DAY1_LAKE.append('setblock ~%d ~3 ~%d supplementaries:candle_holder'
                             '[lit=false,face=floor,facing=north,candles=3]' % (_cx, _cz))
    group('day1_lakefront', 'lake', DAY1_LAKE)

    # =========================================================================
    # 11.5f  Wisp's four posts down the frozen river (Q58).
    # Four more posts, outside the forty, standing dark like everything else. Q58 lights
    # them; it used to set them down.
    # =========================================================================
    DAY1_WISP = ['# Wisp\'s lantern path down the frozen river (Q58 lights these).']
    for _wx, _wz in ((2, 14), (-2, 20), (2, 26), (-2, 32)):
        DAY1_WISP.append('setblock ~%d ~0 ~%d minecraft:cobblestone' % (_wx, _wz))
        DAY1_WISP.append('setblock ~%d ~1 ~%d %s' % (_wx, _wz, POST))
        DAY1_WISP.append('setblock ~%d ~2 ~%d %s' % (_wx, _wz, LAMP_DARK))
    group('day1_wisp_posts', 'anchor', DAY1_WISP)

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

        # ---- THE ENVELOPE, and why the sweep it replaces could not build a ramp ---------
        #
        # The sweep relaxed each column to `clamp(natural, max(nb) - 1, min(nb) + 1)` in
        # place, and where those two bounds crossed it split the difference. That is a fixed
        # point, but it is the wrong one, and beside a terrace it is reliably wrong: the
        # first free column outside a pad is pulled UP by the pad (max(nb) - 1) and pulled
        # DOWN by the meadow behind it (min(nb) + 1), the bounds cross on the first sweep,
        # and it settles halfway. Measured on the 2026-09-05 build: the cottage yard sat at
        # 74, the column outside it at 72, and the same two-block lip ran twenty-six columns
        # down the plot's west side -- `cut_edge` 20 against a limit of 8. Nothing further
        # out was wrong; the ramp simply never started.
        #
        # A ramp is not a local condition, so it is not solved locally. Two Lipschitz
        # envelopes are propagated from the PINNED columns instead:
        #
        #   LO(c) = max over pinned p of (level(p) - chebyshev(c, p))
        #   HI(c) = min over pinned p of (level(p) + chebyshev(c, p))
        #
        # LO is the lowest a column may be without leaving a step down to some terrace; HI
        # the highest without leaving a step up to one. Both are 1-Lipschitz by
        # construction, so a column pinned between them is one ring of a proper staircase,
        # and a column that is already at the natural surface inside them is left alone --
        # which is still most of the field.
        INF = 10 ** 6
        LO = {c: -INF for c in free}
        HI = {c: INF for c in free}
        for _it in range(SKIRT_RINGS + 4):
            moved = 0
            seq = order if _it % 2 == 0 else order[::-1]
            for c in seq:
                nl, nh = -INF, INF
                for dx, dz in _NB8:
                    q = (c[0] + dx, c[1] + dz)
                    if q in pinned:
                        v = pinned[q]
                        if v > nl:
                            nl = v
                        if v < nh:
                            nh = v
                    elif q in LO:
                        if LO[q] > nl:
                            nl = LO[q]
                        if HI[q] < nh:
                            nh = HI[q]
                nl = -INF if nl <= -INF else nl - 1
                nh = INF if nh >= INF else nh + 1
                if nl > LO[c]:
                    LO[c] = nl
                    moved += 1
                if nh < HI[c]:
                    HI[c] = nh
                    moved += 1
            if not moved:
                break

        for c in free:
            n = nat_of[c]
            # A column may hold its terrace's level for a ring or two before it starts down:
            # that is the feathering, and it is what stops the edge of a pad being a straight
            # line in plan. It is a floor on the level, never a ceiling, and the capping pass
            # below takes back anything it turned into a step.
            h = hold_depth(c[0], c[1])
            if h and LO[c] > n:
                n = min(LO[c] + h, n + h)
            y = n
            if LO[c] > -INF:
                y = max(y, LO[c])
            if HI[c] < INF:
                y = min(y, HI[c])
            if LO[c] > -INF and HI[c] < INF and LO[c] > HI[c]:
                y = (LO[c] + HI[c]) // 2       # two terraces too close to ramp between
            field[c] = y

        # ---- and cap: no free column may stand more than a block over its lowest
        # neighbour. Downward only, so it cannot break LO (every neighbour is at least
        # LO[c] - 1, so the cap can never push a column under its own envelope) and it
        # cannot make a step; all it does is take back the feathering wherever the hash
        # raised a column its neighbours could not follow.
        for _it in range(SKIRT_RINGS + 4):
            moved = 0
            seq = order if _it % 2 == 0 else order[::-1]
            for c in seq:
                nb = [pinned[q] if q in pinned else field[q]
                      for q in ((c[0] + dx, c[1] + dz) for dx, dz in _NB8)
                      if q in field or q in pinned]
                if not nb:
                    continue
                cap = min(nb) + 1
                if field[c] > cap:
                    field[c] = cap
                    moved += 1
            if not moved:
                break

        # ---- and say so. The skirt's whole promise is "no step taller than one anywhere
        # the plan regraded", and the only honest way to make that claim is to measure it.
        worst = 0
        for c in free:
            for dx, dz in _NB8:
                q = (c[0] + dx, c[1] + dz)
                v = pinned.get(q, field.get(q))
                if v is None:
                    continue
                if c in nat_of and q in nat_of and field[c] == nat_of[c] \
                        and field[q] == nat_of[q]:
                    continue                    # two untouched columns: that is the land
                worst = max(worst, abs(field[c] - v))
        print('  skirt: worst step between a regraded column and any neighbour: %d' % worst)
        return {c: field[c] for c in free if field[c] != nat_of[c]}

    SKIRT = build_skirt()

    # --- and the meadow put back on top of it ---------------------------------------
    # A graded column is bare. Nine hundred of them in a row beside the road is a cutting,
    # whatever its cross-section, because the eye reads "mown" as "man-made". So every
    # column the plan regrades to grass gets its ground cover back: short grass and ferns
    # mostly, a flower here and there, drawn from the same reproducible per-column hash the
    # rest of the file uses so a rebuild lays down the same meadow. None of it blocks
    # motion, so it changes no heightmap and no probe reads it as ground.
    MEADOW = ('minecraft:grass', 'minecraft:grass', 'minecraft:grass', 'minecraft:fern',
              'minecraft:poppy', 'minecraft:dandelion', 'minecraft:oxeye_daisy',
              'minecraft:cornflower', 'minecraft:azure_bluet', 'minecraft:allium')

    def meadow_cmds(x0, x1, z, wy, mat):
        """Ground cover for one graded row run, or nothing if the run is not turf."""
        if not mat.endswith('grass_block'):
            return []
        out = []
        for xx in range(x0, x1 + 1):
            wx = ANCHOR_W[0] + xx
            h = cell_hash(wx, ANCHOR_W[2] + z)
            if h >= 34:
                continue
            out.append('setblock ~%d ~%d ~%d %s'
                       % (wx, wy + 1, ANCHOR_W[2] + z, MEADOW[h % len(MEADOW)]))
        return out

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
                # TWO blocks of clearance over the new ground, not ten.
                #
                # This line used to read `max(WY + 4, hi + 10)`, i.e. every graded column
                # had a ten-block column of air punched over it -- and a graded column is
                # not a lonely thing: an oak's canopy is five columns wide, so clearing the
                # sky over ONE column at its edge takes the whole crown off a tree whose
                # trunk was never touched. That is the multiplier that turned a road with
                # some cut-and-fill into a twenty-block clear-cut: 1044 of the 2768 columns
                # within ten blocks of the road are wooded in the pregen and 57 survived.
                # Two blocks is enough to lift the old ground off the new one and no more;
                # the columns that really do carry a trunk are cleared one by one below.
                top = max(WY + 2, ANCHOR_W[1] + hi)
                out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                           % (WX0, WY + 1, WZ, WX1, top, WZ))
                for xx in range(x0, x1 + 1):
                    cy = canopy(ANCHOR_W[0] + xx, WZ)
                    if cy is not None and cy > top:
                        out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:air'
                                   % (ANCHOR_W[0] + xx, top + 1, WZ,
                                      ANCHOR_W[0] + xx, cy, WZ))
                out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d %s'
                           % (WX0, WY, WZ, WX1, WY, WZ, mat))
                if y - 1 >= lo:
                    out.append('fill ~%d ~%d ~%d ~%d ~%d ~%d minecraft:dirt replace minecraft:air'
                               % (WX0, ANCHOR_W[1] + lo, WZ, WX1, WY - 1, WZ))
                out += meadow_cmds(x0, x1, z, WY, mat)
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

    # =========================================================================
    # 11.7  THE PLANTING.  Trees, gardens, pens and the orchard.
    #
    # media/look/NOTES.md says the valley reads as a machine's output from the air: "the
    # buildings sit apart from each other on lawns". A town is not a set of buildings on
    # mown grass -- it is buildings with STUFF ROUND THEM: a tree that was there before the
    # house, a fence somebody put up, a run of vegetables, a pen with birds in it. None of
    # that can be a template (no installed jar has a standalone garden that is not a whole
    # villager plot), so it is solved here, against everything the plan already knows:
    #
    #   * never on a built column -- LEVEL holds every pad, street, plaza, apron and road
    #     column the plan pinned, and this refuses all of them
    #   * never on ground the solver reserved -- `occupied` is every pad plus its margin,
    #     every street with its keep-clear, every lamp post and every reservation
    #   * never within three columns of a front door, so nothing here can block a doorway
    #   * only on ground the plan did not regrade steeply, and never in water
    #
    # It runs LAST, after the skirt has walked the ground back to the land, so a tree is
    # planted on the height the finished world actually has under it.
    # =========================================================================
    def _ground(x, z):
        """The finished ground at an anchor-relative column: the skirt's level where it
        moved one, the design surface everywhere else."""
        return SKIRT.get((x, z), lev(x, z))

    DOOR_CELLS = set()
    for _n5, _p5 in P.items():
        for _d5 in _p5.doors()[:1]:
            for _ddx in range(-3, 4):
                for _ddz in range(-3, 4):
                    DOOR_CELLS.add((_d5['pos'][0] + _ddx, _d5['pos'][2] + _ddz))

    def plant_free(x, z, flat=1):
        if (x, z) in LEVEL or (x, z) in occupied or (x, z) in APRON_PAVED:
            return False
        if (x, z) in street_cells or (x, z) in PROTECTED or (x, z) in DOOR_CELLS:
            return False
        if (x, z) in PIER_CELLS or wet(x, z):
            return False
        g = _ground(x, z)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if wet(x + dx, z + dz):
                    return False
                if abs(_ground(x + dx, z + dz) - g) > flat:
                    return False
        return True

    PLANT_CMDS = ['# the planting: trees, gardens, pens and the orchard. GENERATED.']
    PLANTED = set()

    def _claim(cells):
        for c in cells:
            PLANTED.add(c)

    def tree_at(x, z, kind=None):
        """One small tree, anchor-relative, standing on the finished ground."""
        y = _ground(x, z)
        h = cell_hash(x, z)
        wood = kind or ('oak' if h < 40 else 'birch' if h < 75 else 'spruce')
        trunk = 4 + (h % 3)
        out = ['fill %s %s %s %s %s %s minecraft:air'
               % (t(x - 2), t(y + 1), t(z - 2), t(x + 2), t(y + trunk + 3), t(z + 2)),
               setb(x, y, z, 'minecraft:dirt')]
        for _ty in range(1, trunk + 1):
            out.append(setb(x, y + _ty, z, 'minecraft:%s_log[axis=y]' % wood))
        _leaf = 'minecraft:%s_leaves[persistent=true]' % wood
        if wood == 'spruce':
            _shape = [(trunk - 2, 2), (trunk - 1, 1), (trunk, 1), (trunk + 1, 0), (trunk + 2, 0)]
        else:
            _shape = [(trunk - 1, 2), (trunk, 2), (trunk + 1, 1), (trunk + 2, 0)]
        for _dy, _rad in _shape:
            for _dx in range(-_rad, _rad + 1):
                for _dz in range(-_rad, _rad + 1):
                    if _rad and abs(_dx) == _rad and abs(_dz) == _rad:
                        continue
                    if _dx == 0 and _dz == 0 and _dy <= trunk:
                        continue
                    out.append(setb(x + _dx, y + _dy, z + _dz, _leaf))
        return out

    # ---- eight trees, near the buildings, never in front of a door ----------------
    TREE_SPOTS = []
    for _n5, _p5 in sorted(P.items()):
        if len(TREE_SPOTS) >= 8:
            break
        _pd5 = _p5.pad()
        _ring = []
        for _rx in range(_pd5[0] - 4, _pd5[2] + 5):
            for _rz in range(_pd5[1] - 4, _pd5[3] + 5):
                if _pd5[0] - 1 <= _rx <= _pd5[2] + 1 and _pd5[1] - 1 <= _rz <= _pd5[3] + 1:
                    continue
                _ring.append((_rx, _rz))
        _ring.sort(key=lambda c: (cell_hash(c[0], c[1]), c))
        for _c5 in _ring:
            if not plant_free(*_c5):
                continue
            if any(max(abs(_c5[0] - q[0]), abs(_c5[1] - q[1])) < 7 for q in TREE_SPOTS):
                continue
            if any(max(abs(_c5[0] - q[0]), abs(_c5[1] - q[1])) <= 2 for q in PLANTED):
                continue
            TREE_SPOTS.append(_c5)
            _claim([(_c5[0] + a, _c5[1] + b) for a in (-2, -1, 0, 1, 2)
                    for b in (-2, -1, 0, 1, 2)])
            break
    for _c5 in TREE_SPOTS:
        PLANT_CMDS += tree_at(*_c5)

    # ---- five fenced plots: three gardens, a hen run and a stock pen --------------
    # Each is a rectangle of free ground beside its building, fenced with a gate facing the
    # building's own side, and filled with what the story says is in it. The hens are canon
    # -- Q10's pen at the farm is the player's -- so this is the TOWN's flock, at Oda's.
    YARD_PLOTS = [
        ('granary',    7, 5, 'pen'),
        ('store',      6, 5, 'hens'),
        ('marnie_house', 6, 5, 'garden'),
        ('town_hall',  7, 5, 'garden'),
        ('boathouse',  5, 5, 'garden'),
    ]
    YARDS = []
    for _yn, _yw, _yd, _ykind in YARD_PLOTS:
        if _yn not in P:
            continue
        _pd5 = P[_yn].pad()
        _best = None
        for _sx in range(_pd5[0] - _yw - 3, _pd5[2] + 5):
            for _sz in range(_pd5[1] - _yd - 3, _pd5[3] + 5):
                _cells = [(a, b) for a in range(_sx, _sx + _yw) for b in range(_sz, _sz + _yd)]
                if any(c in PLANTED for c in _cells):
                    continue
                if not all(plant_free(a, b) for a, b in _cells):
                    continue
                _d5 = ((_sx + _yw // 2) - (_pd5[0] + _pd5[2]) // 2,
                       (_sz + _yd // 2) - (_pd5[1] + _pd5[3]) // 2)
                _score = _d5[0] * _d5[0] + _d5[1] * _d5[1]
                if _best is None or _score < _best[0]:
                    _best = (_score, _sx, _sz, _cells)
        if _best is None:
            print('  no room for the %s at %s' % (_ykind, _yn))
            continue
        _, _sx, _sz, _cells = _best
        _claim(_cells)
        YARDS.append((_yn, _ykind, _sx, _sz, _yw, _yd))
        _y5 = _ground(_sx + _yw // 2, _sz + _yd // 2)
        _gate = (_sx + _yw // 2, _sz)
        PLANT_CMDS.append(fill(_sx, _y5 + 1, _sz, _sx + _yw - 1, _y5 + 3, _sz + _yd - 1,
                               'minecraft:air'))
        for (_a, _b) in _cells:
            _edge = _a in (_sx, _sx + _yw - 1) or _b in (_sz, _sz + _yd - 1)
            _yy = _ground(_a, _b)
            if _edge:
                if (_a, _b) == _gate:
                    PLANT_CMDS.append(setb(_a, _yy + 1, _b,
                                           'minecraft:oak_fence_gate[facing=north,open=false]'))
                else:
                    PLANT_CMDS.append(setb(_a, _yy + 1, _b, 'minecraft:oak_fence'))
                continue
            _h5 = cell_hash(_a, _b)
            if _ykind == 'garden':
                PLANT_CMDS.append(setb(_a, _yy, _b, 'minecraft:farmland[moisture=7]'))
                PLANT_CMDS.append(setb(_a, _yy + 1, _b,
                                       'minecraft:carrots[age=7]' if _h5 < 33 else
                                       'minecraft:potatoes[age=7]' if _h5 < 66 else
                                       'minecraft:beetroots[age=3]'))
            elif _ykind == 'hens':
                PLANT_CMDS.append(setb(_a, _yy, _b,
                                       'minecraft:coarse_dirt' if _h5 < 50 else
                                       'minecraft:grass_block'))
                if _h5 < 18:
                    PLANT_CMDS.append(setb(_a, _yy + 1, _b, 'minecraft:hay_block'))
            else:
                PLANT_CMDS.append(setb(_a, _yy, _b, 'minecraft:grass_block'))
                if _h5 < 22:
                    PLANT_CMDS.append(setb(_a, _yy + 1, _b, 'minecraft:grass'))
        if _ykind == 'hens':
            # A coop in the corner of the run. The BIRDS are not summoned here: valley_build
            # deliberately filters `summon` out of a day-one build ("no residents on day
            # one"), so a summon in this group would be a line that never runs, and the one
            # thing the shipped world does not need is more entities baked into its region
            # files (media/look/NOTES.md item 12: 73 hostiles were saved into it).
            PLANT_CMDS += [
                fill(_sx + 1, _y5 + 1, _sz + 1, _sx + 2, _y5 + 2, _sz + 2,
                     'minecraft:spruce_planks'),
                fill(_sx + 1, _y5 + 1, _sz + 1, _sx + 1, _y5 + 1, _sz + 1, 'minecraft:air'),
                fill(_sx + 1, _y5 + 3, _sz + 1, _sx + 2, _y5 + 3, _sz + 2,
                     'minecraft:spruce_slab'),
                setb(_sx + 2, _y5 + 1, _sz + 3, 'minecraft:hay_block'),
                setb(_sx + 3, _y5 + 1, _sz + 2, 'minecraft:composter'),
            ]
    print('  planting: %d trees, %d fenced plots (%s)'
          % (len(TREE_SPOTS), len(YARDS), ', '.join('%s/%s' % (y[0], y[1]) for y in YARDS)))

    # ---- the orchard behind the farm ---------------------------------------------
    # Home-relative, north of the cottage and clear of the yard, the gate and the road.
    ORCHARD = []
    _cot_ox = HEARTH_W[0] - ANCHOR_W[0]
    _cot_oz = HEARTH_W[2] - ANCHOR_W[2]
    for _ox5 in range(-13, 9, 3):
        for _oz5 in range(-24, -11, 3):
            if len(ORCHARD) >= 7:
                break
            _c5 = (_cot_ox + _ox5, _cot_oz + _oz5)
            if not plant_free(_c5[0], _c5[1], flat=2):
                continue
            if any(max(abs(_c5[0] - q[0]), abs(_c5[1] - q[1])) <= 2 for q in PLANTED):
                continue
            _claim([(_c5[0] + a, _c5[1] + b) for a in (-2, -1, 0, 1, 2)
                    for b in (-2, -1, 0, 1, 2)])
            ORCHARD.append(_c5)
            PLANT_CMDS += tree_at(_c5[0], _c5[1], kind='oak')
    print('  orchard: %d trees behind the farm' % len(ORCHARD))
    group('day1_planting', 'anchor', PLANT_CMDS)

    RUN_ORDER[:0] = ['day1_road', 'day1_cottage', 'day1_signpost']
    # The cellar, the adit, the noticeboard and the stake socket all go in AFTER the
    # buildings they sit under or on: the cellar is cut out from under the cottage, the
    # adit pierces the Works shell act4_works seals, and the board and the socket stand on
    # the square act1_square paves.
    RUN_ORDER += ['day1_cellar', 'day1_adit', 'day1_board', 'day1_lakefront',
                  'day1_wisp_posts', 'day1_lamps', 'day1_planting']

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
            'gate_sign': W([GATE_POST[0], 1, GATE_POST[1]], HOME_W),
            'porch': W([3, 0, 0], HOME_W),
        },
        'plaza': _site_boxes['plaza'],
        'site_boxes': _site_boxes,
        'buildings': _buildings,
        'doors': {k: v for k, v in _doors.items() if v},
        # Lighting ORDER, 1..40, and which quest lights each one. The last is the bare
        # post on Josie's porch (Q90); everything before it ships with a dark cage lamp
        # on top, at pos + [0,1,0].
        'lamps': [{'n': i + 1, 'pos': p, 'bare': (i == LAMP_BARE),
                   'route': ('q90' if i == LAMP_BARE else
                             'finale' if i < 4 else 'q07' if i < 6 else
                             'q34' if i < 10 else 'q74')}
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
        # The streets' own centre lines, at the level the terracing gave them. The lantern
        # road is not the only thing in the valley with a verge, and `road_banks` in
        # nature_check.py walks these for the same reason it walks the road: a street cut
        # into the hillside with a two-block bank at the kerb is the same defect indoors.
        'streets': {_sn: [[ANCHOR_W[0] + _c[0], ANCHOR_W[1] + _c[1], ANCHOR_W[2] + _c[2]]
                          for _c in _sp] for _sn, _sp in STREET_PATHS.items()},
        'signpost': SIGNPOST,
        # Which way she is facing when the world puts her down: along the road, toward the
        # farm. `setworldspawn <x> <y> <z> <yaw>` takes it, and the yaw is computed from the
        # road's first step rather than typed, so it follows the arrival wherever it moves.
        'spawn_yaw': SPAWN_YAW,
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
    SITES_JSON['works']['plinth'] = W([0, 0, -5], _wm)
    SITES_JSON['works']['adit'] = {
        'mouth': W([ADIT_XZ[0][0], ADIT_TOP, ADIT_XZ[0][1]], _wm),
        'fall': [_wm[0] + ADIT_XZ[0][0], _wm[1] + ADIT_FALL[0] + 1, _wm[2] + ADIT_XZ[0][1],
                 _wm[0] + ADIT_XZ[3][0], _wm[1] + ADIT_FALL[1], _wm[2] + ADIT_XZ[3][1]],
        'blocks': (ADIT_FALL[1] - ADIT_FALL[0]) * 4,
    }
    SITES_JSON['cellar'] = {
        'stand': W(CELLAR_ROOM['stand'], HOME_W),
        'box': [HOME_W[0] + _cs[0], HOME_W[1] + _cs[1], HOME_W[2] + _cs[2],
                HOME_W[0] + _cs[3], HOME_W[1] + _cs[4], HOME_W[2] + _cs[5]],
        'door': W(CELLAR_ROOM['door'], HOME_W),
        'chalk': W(CELLAR_ROOM['chalk'], HOME_W),
        'chest': W(CELLAR_ROOM['chest'], HOME_W),
        'plinth': W(CELLAR_ROOM['plinth'], HOME_W),
        'lock': W(CELLAR_ROOM['lock'], HOME_W),
        'gravel': [HOME_W[0] + CELLAR_W[0], HOME_W[1] - 2 - CELLAR_STEPS,
                   HOME_W[2] - 1 - CELLAR_STEPS,
                   HOME_W[0] + CELLAR_W[1], HOME_W[1] - 1, HOME_W[2] - 2],
        'blocks': CELLAR_STEPS * 4,
    }
    SITES_JSON['cellar_door'] = SITES_JSON['cellar']['door']
    # The fountain's own footprint, in world coordinates. `plaza_dry` in
    # scratch/nature_check.py reads it and skips those five columns: the square is
    # meant to be dry everywhere else, and this is the one place it is meant to be wet.
    SITES_JSON['fountain'] = [ANCHOR_W[0] + FOUNTAIN_BOX[0], ANCHOR_W[2] + FOUNTAIN_BOX[1],
                              ANCHOR_W[0] + FOUNTAIN_BOX[2], ANCHOR_W[2] + FOUNTAIN_BOX[3]]
    SITES_JSON['stake_socket'] = [ANCHOR_W[0], ANCHOR_W[1] + 1, ANCHOR_W[2] - 2]
    SITES_JSON['lakefront'] = {
        'pier_waystone': W([8, 0, 4], W(OFF['lake'], ANCHOR_W)),
        'candles': [W([_c[0], 3, _c[1]], W(OFF['lake'], ANCHOR_W))
                    for _c in ((7, 8), (9, 8), (7, 10), (9, 10), (7, 12), (9, 12))],
        'campfire': W([4, 0, 7], W(OFF['lake'], ANCHOR_W)),
        'boat': W([3, 0, 10], W(OFF['lake'], ANCHOR_W)),
        'water': [W([2, -3, 10], W(OFF['lake'], ANCHOR_W)),
                  W([16, -1, 24], W(OFF['lake'], ANCHOR_W))],
    }
    SITES_JSON['wisp_posts'] = [W([_w[0], 2, _w[1]], ANCHOR_W)
                                for _w in ((2, 14), (-2, 20), (2, 26), (-2, 32))]
    SITES_JSON['town_waystone'] = [ANCHOR_W[0], ANCHOR_W[1] + 1, ANCHOR_W[2]]
    SITES_JSON['noticeboard'] = {
        'origin': W([0, 1, -5], ANCHOR_W),
        'sign': W([1, 4, -5], ANCHOR_W),
    }
    SITES_JSON['cottage']['sconce'] = W([-1, 1, 1], HOME_W)
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

# The two mcfunctions the pack still ships. They are DERIVATIONS, not runtime code:
# `day1_cottage` and Q7's road are built from the same `cot_lines` / `sp_lines` this writes
# out, and having them on disk in a readable form is how the cottage and the road are
# reviewed. Nothing calls them -- valley_finales.js REFUSES `run function valley:`, and no
# quest reward names one.
#
# valley:setup/place_ruin is NOT written any more. It cut a 23x26 pad and pasted a ruin onto
# it at the first player's first join, which is the single thing this whole architecture
# exists to delete: the farm is in the shipped world, standing, before anybody logs in.
fn = pathlib.Path('pack/kubejs/data/valley/functions')
(fn / 'act1').mkdir(parents=True, exist_ok=True)
_dead = fn / 'setup' / 'place_ruin.mcfunction'
if _dead.exists():
    _dead.unlink()
    try:
        (fn / 'setup').rmdir()
    except OSError:
        pass
    print('  removed the dead valley:setup/place_ruin')
(fn / 'act1' / 'cottage.mcfunction').write_text('\n'.join(cot_lines) + '\n')
(fn / 'act1' / 'square_path.mcfunction').write_text('\n'.join(sp_lines) + '\n')

if SITES_JSON is not None:
    _sp = pathlib.Path('pack/kubejs/data/valley/valley_sites.json')
    _sp.parent.mkdir(parents=True, exist_ok=True)
    _sp.write_text(json.dumps(SITES_JSON, indent=1) + '\n')
    print('  valley_sites.json: seed %s, spawn %s, hearth %s, anchor %s, %d lamps, %d doors'
          % (SITES_JSON['seed'], SITES_JSON['spawn'], SITES_JSON['hearth'],
             SITES_JSON['anchor'], len(SITES_JSON['lamps']), len(SITES_JSON['doors'])))

    # ---- ...and the same registry as a KubeJS global ---------------------------------
    # valley_core.js, valley_checks.js and valley_finales.js all read their coordinates
    # out of the registry now, and a server script cannot open a file. So the JSON is
    # emitted a second time as a script that does nothing but assign it, with a priority
    # comment that puts it ahead of every valley_*.js AND ahead of town_plan.js.
    #
    # KubeJS sorts server_scripts by `// priority:` DESC and only then by filename, and
    # the ordering matters: valley_core.js reads global.valleySites at load time to build
    # its constants, and a file that loads after it would be invisible. This was already a
    # live bug for town_plan.js -- the log shows valley_core.js at 00:15:02.929 and
    # town_plan.js at 00:15:02.953, i.e. the plan loaded SECOND and every mark in the pack
    # came out of valley_core's hand-typed fallback. See docs/mod-decisions.md.
    _js = pathlib.Path('pack/kubejs/server_scripts/valley_sites.js')
    _js.write_text(
        '// priority: 2000\n'
        '// valley_sites.js -- GENERATED by tools/scripts/plan_town.py. DO NOT HAND-EDIT.\n'
        '//\n'
        '// The fixed site registry, verbatim from pack/kubejs/data/valley/valley_sites.json,\n'
        '// as a KubeJS global. The world is shipped, so every coordinate in the pack is a\n'
        '// constant and this is where all three valley scripts read them from.\n'
        '//\n'
        '// priority 2000 loads it before town_plan.js (1000) and before every valley_*.js.\n'
        '\n'
        'global.valleySites = ' + json.dumps(SITES_JSON, indent=1) + '\n'
        '\n'
        "console.info('[valley] valley_sites.js ok -- seed " + str(SITES_JSON['seed']) +
        ", anchor " + ' '.join(str(v) for v in SITES_JSON['anchor']) +
        ", ' + global.valleySites.lamps.length + ' lamps, ' +\n"
        "             Object.keys(global.valleySites.buildings).length + ' buildings')\n")
    print('  valley_sites.js: %d bytes' % _js.stat().st_size)

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
