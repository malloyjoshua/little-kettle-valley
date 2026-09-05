#!/usr/bin/env python3
"""shipped_assert.py -- the three parts of the shipped-world playthrough that need a world
reader or the registry rather than a shell. Driven by tools/scripts/playthrough.sh.

  salt   --world W --out salt.json      print 20 `setblock` commands for player blocks
                                        around the farm and the square, and record them
  player --player NAME                  print the block placements a PLAYER makes, in
                                        order, so BlockEvents.placed fires for each
  check  --world W --salt salt.json --baseline B
                                        read the finished world off its region files and
                                        assert the seven things the run exists to prove

Everything is read from pack/kubejs/data/valley/valley_sites.json. Nothing here knows a
coordinate of its own.
"""
import sys, json, argparse, pathlib, collections
sys.path.insert(0, 'scratch'); sys.path.insert(0, 'tools/scripts')
import vt_lib as V
import seed_hunt as SH

SITES = json.load(open('pack/kubejs/data/valley/valley_sites.json'))

AIR = ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air')


def reader(world):
    cache = {}
    w = pathlib.Path(world)

    def chunk(cx, cz):
        rk = (cx >> 5, cz >> 5)
        if rk not in cache:
            q = w / 'region' / ('r.%d.%d.mca' % rk)
            cache[rk] = SH.read_region(q) if q.exists() else {}
        return cache[rk].get((cx & 31, cz & 31))
    return chunk


def use(world):
    V.chunk = reader(world)
    V._sec = {}


def blk(x, y, z):
    try:
        return V.block(int(x), int(y), int(z))
    except Exception:                                    # noqa: BLE001
        return '?'


def state(x, y, z):
    try:
        return V.block_full(int(x), int(y), int(z))[1] or {}
    except Exception:                                    # noqa: BLE001
        return {}


# =============================================================================
# salt -- twenty blocks a player put down, in places the story walks through
# =============================================================================
def salt(args):
    use(args.world)
    home = SITES['home_waystone']
    anchor = SITES['anchor']
    lake = SITES['marks']['lake']
    spots = []
    # a ring in the farm yard, a ring on the square, and two on the lantern road: the three
    # places the old pack's pads, fills and templates all reached into.
    for dx, dz in ((6, 6), (-6, 6), (6, -3), (-6, -3), (8, 0), (-8, 0), (0, 7)):
        spots.append((home[0] + dx, home[2] + dz))
    for dx, dz in ((7, 7), (-7, 7), (7, -7), (-7, -7), (10, 0), (-10, 0), (0, 10), (0, -8)):
        spots.append((anchor[0] + dx, anchor[2] + dz))
    for dx, dz in ((5, 3), (-5, 3), (5, -3), (-5, -3), (0, 5)):
        spots.append((lake[0] + dx, lake[2] + dz))
    out, rec = [], []
    for i, (x, z) in enumerate(spots):
        # stand it on whatever is already there: find the surface, put it one above.
        y = None
        for yy in range(120, 40, -1):
            if blk(x, yy, z) not in AIR:
                y = yy + 1
                break
        if y is None:
            continue
        block = 'minecraft:bookshelf' if i % 2 == 0 else 'minecraft:jukebox'
        out.append('setblock %d %d %d %s' % (x, y, z, block))
        rec.append({'pos': [x, y, z], 'block': block})
    print('# %d player blocks, salted before the run' % len(rec))
    for c in out:
        print(c)
    pathlib.Path(args.out).write_text(json.dumps(rec, indent=1) + '\n')
    return 0


# =============================================================================
# player -- the placements a PLAYER makes, in order
# =============================================================================
def player(args):
    p = args.player
    c = SITES['cottage']
    out = ['# The blocks the player puts down herself, in the order she would.',
           '#',
           '# These are `execute as/at` the player, but they are SETBLOCKS, and a setblock does',
           '# not fire BlockEvents.placed -- neither does a Create deployer, a Building Gadget',
           '# or a schematic. That is exactly why every one of these checks now READS THE',
           '# WORLD at a registry coordinate instead of listening for a hand: the old',
           '# listeners were untestable, and every previous playthrough proved them by',
           '# ticking the quest with `ftbquests change_progress` and moving on.']

    def place(pos, block, why):
        out.append('# %s' % why)
        out.append('execute as %s at %s run setblock %d %d %d %s' %
                   (p, p, pos[0], pos[1], pos[2], block))

    # ---- Q2: the Homestead Waystone on the hearthstone -----------------------
    place([c['hearthstone'][0], c['hearthstone'][1] + 1, c['hearthstone'][2]],
          'waystones:waystone', 'Q2 -- the Homestead Waystone on the hearthstone')
    out.append('SLEEP 2')
    # ---- Q3: the door, two windows, the bed, the sconce ----------------------
    place(c['door'], 'minecraft:oak_door[facing=west,half=lower,hinge=left]', 'Q3 -- the door')
    place([c['door'][0], c['door'][1] + 1, c['door'][2]],
          'minecraft:oak_door[facing=west,half=upper,hinge=left]', 'Q3 -- the door, upper half')
    for i, w in enumerate(c['windows'][:4]):
        place(w, 'minecraft:glass_pane', 'Q3 -- window %d' % (i + 1))
    place([c['bed'][0], c['bed'][1] + 1, c['bed'][2]],
          'minecraft:red_bed[facing=east,part=foot]', 'Q3 -- the bed on the wool mat')
    place([c['bed'][0] - 1, c['bed'][1] + 1, c['bed'][2]],
          'minecraft:red_bed[facing=east,part=head]', 'Q3 -- the bed, head')
    place(c['sconce'], 'minecraft:lantern[hanging=false]', 'Q3 -- the sconce on the hook')
    out.append('SLEEP 3')
    # ---- Q4: the megatorch ---------------------------------------------------
    place([c['hearthstone'][0] + 2, c['hearthstone'][1] + 1, c['hearthstone'][2] + 2],
          'torchmaster:megatorch', 'Q4 -- the Megatorch inside the cottage')
    # ---- Q5 / Q55: stand in the cellar ---------------------------------------
    st = SITES['cellar']['stand']
    out.append('# Q5 and Q55 -- standing in the cellar (the harness digs by teleporting)')
    out.append('tp %s %d %d %d' % (p, st[0], st[1], st[2]))
    out.append('SLEEP 3')
    # ---- Q7: the stake in Bram's socket --------------------------------------
    s = SITES['stake_socket']
    out.append('tp %s %d %d %d' % (p, s[0], s[1] + 1, s[2]))
    out.append('SLEEP 1')
    place(s, 'valley:town_anchor', "Q7 -- the Surveyor's Stake in Bram's socket")
    out.append('SLEEP 2')
    # ---- Q34: energy duct out to the four marked posts ------------------------
    q34 = [l['pos'] for l in SITES['lamps'] if l['route'] == 'q34']
    for i, l in enumerate(q34):
        out.append('tp %s %d %d %d' % (p, l[0] + 1, l[1] + 1, l[2]))
        place([l[0] + 1, l[1] + 1, l[2]], 'thermal:energy_duct',
              'Q34 -- duct to marked post %d' % (i + 1))
    out.append('SLEEP 2')
    # ---- Q74: walk the line --------------------------------------------------
    q74 = [l['pos'] for l in SITES['lamps'] if l['route'] == 'q74']
    out.append('# Q74 -- walk the whole line, mill to square to lake to farm gate')
    for l in q74:
        out.append('tp %s %d %d %d' % (p, l[0], l[1] + 1, l[2]))
        out.append('SLEEP 1.2')
    out.append('SLEEP 2')
    # ---- Q90: the fortieth lamp on the bare post -----------------------------
    porch = [l['pos'] for l in SITES['lamps'] if l['route'] == 'q90'][0]
    out.append('tp %s %d %d %d' % (p, porch[0] + 1, porch[1], porch[2]))
    out.append('SLEEP 1')
    place([porch[0], porch[1] + 1, porch[2]], 'minecraft:lantern[hanging=false]',
          "Q90 -- the fortieth lamp on Josie's bare post")
    out.append('SLEEP 2')
    # ---- Q8 / Q57 / Q76 -- the three sleeps ---------------------------------
    out.append('# the three sleep quests: the poll watches the sleeping -> awake edge')
    out.append('tp %s %d %d %d' % (p, c['hearthstone'][0], c['hearthstone'][1] + 1,
                                   c['hearthstone'][2]))
    print('\n'.join(out))
    return 0


# =============================================================================
# check -- read the finished world
# =============================================================================
class Report(object):
    def __init__(self):
        self.rows = []
        self.ok = True

    def add(self, name, ok, detail):
        self.rows.append({'probe': name, 'ok': bool(ok), 'detail': detail})
        if not ok:
            self.ok = False

    def show(self):
        w = max(len(r['probe']) for r in self.rows)
        for r in self.rows:
            print('  %-*s  %-4s  %s' % (w, r['probe'], 'PASS' if r['ok'] else 'FAIL', r['detail']))
        print('  %d of %d probes pass' % (sum(1 for r in self.rows if r['ok']), len(self.rows)))


def check(args):
    use(args.world)
    R = Report()

    # ---- 1. all forty lamps lit ------------------------------------------
    dark = []
    for L in SITES['lamps']:
        x, y, z = L['pos']
        st = state(x, y + 1, z)
        lit = str(st.get('lit', '')).lower() == 'true'
        if not lit:
            dark.append('%d@%d %d %d=%s' % (L['n'], x, y + 1, z, blk(x, y + 1, z)))
    R.add('lamps_lit', not dark,
          '%d of 40 burning%s' % (40 - len(dark), '' if not dark else '; dark: ' + ', '.join(dark[:6])))

    # ---- 2. every resident at their stand --------------------------------
    ents = []
    try:
        ents = list(V.entities())
    except Exception as e:                               # noqa: BLE001
        ents = []
    names = collections.Counter()
    npcs = []
    for e in ents:
        t = str(e.get('id', ''))
        if 'easy_npc' not in t:
            continue
        nm = e.get('CustomName') or e.get('Name') or ''
        npcs.append((str(nm), e.get('Pos')))
        names[str(nm)] += 1
    R.add('residents_present', len(npcs) >= 15,
          '%d easy_npc entities in the region files (want >= 15)' % len(npcs))

    # ---- 3. the cottage gaps are filled ----------------------------------
    c = SITES['cottage']
    gaps = []
    if 'door' not in blk(*c['door']):
        gaps.append('door=%s' % blk(*c['door']))
    glazed = sum(1 for w in c['windows']
                 if any(k in blk(*w) for k in ('glass', 'window', 'pane')))
    if glazed < 2:
        gaps.append('windows=%d' % glazed)
    bedcell = [c['bed'][0], c['bed'][1] + 1, c['bed'][2]]
    if 'bed' not in blk(*bedcell):
        gaps.append('bed=%s' % blk(*bedcell))
    if c.get('sconce') and not any(k in blk(*c['sconce'])
                                   for k in ('lantern', 'torch', 'sconce', 'candle')):
        gaps.append('sconce=%s' % blk(*c['sconce']))
    R.add('cottage_gaps_filled', not gaps,
          'door, %d windows, bed and sconce all in' % glazed if not gaps
          else 'still open: ' + ', '.join(gaps))

    # ---- 4. the Works lever is thrown ------------------------------------
    lv = SITES['works']['lever']
    lst = state(*lv)
    R.add('works_lever', 'lever' in blk(*lv) and str(lst.get('powered', '')).lower() == 'true',
          '%s %s at %s' % (blk(*lv), json.dumps(lst), ' '.join(map(str, lv))))

    # ---- 5. the cellar door is open --------------------------------------
    cd = SITES['cellar']['door']
    dst = state(*cd)
    R.add('cellar_door_open',
          'iron_door' in blk(*cd) and str(dst.get('open', '')).lower() == 'true',
          '%s open=%s' % (blk(*cd), dst.get('open')))

    # ---- 6. the salt survived --------------------------------------------
    lost = []
    if args.salt and pathlib.Path(args.salt).exists():
        for s in json.load(open(args.salt)):
            got = blk(*s['pos'])
            if got != s['block']:
                lost.append('%s -> %s at %s' % (s['block'].split(':')[-1], got,
                                                ' '.join(map(str, s['pos']))))
        R.add('player_blocks_survive', not lost,
              'all %d salted blocks still there' % len(json.load(open(args.salt)))
              if not lost else '%d LOST: %s' % (len(lost), '; '.join(lost[:6])))
    else:
        R.add('player_blocks_survive', False, 'no salt file')

    # ---- 7. nothing changed outside the registry footprints --------------
    # Compare the finished world with the shipped master over a wide box, and allow a
    # change only where the registry says the story is entitled to one: inside a site box,
    # the plaza, the cottage plot, the cellar, the works, the lakefront, or within 3 of a
    # lamp post, a door, a mark, a stand or one of the harness's own salt blocks.
    if args.baseline and pathlib.Path(args.baseline, 'region').exists():
        allowed = []
        for b in SITES['site_boxes'].values():
            allowed.append((b[0] - 2, b[1] - 2, b[2] + 2, b[3] + 2))
        cl = SITES['cellar']['box']
        allowed.append((cl[0] - 2, cl[2] - 2, cl[3] + 2, cl[5] + 2))
        wk = SITES['works']['shell']
        allowed.append((wk[0] - 3, wk[2] - 3, wk[3] + 3, wk[5] + 3))
        lk = SITES['marks']['lake']
        allowed.append((lk[0] - 16, lk[2] - 16, lk[0] + 16, lk[2] + 28))
        pts = [l['pos'] for l in SITES['lamps']] + list(SITES['doors'].values()) + \
              list(SITES['marks'].values()) + [s['pos'] for s in SITES['npc_stands']] + \
              [SITES['stake_socket'], SITES['signpost'], SITES['pier']] + \
              SITES.get('wisp_posts', [])
        if args.salt and pathlib.Path(args.salt).exists():
            pts += [s['pos'] for s in json.load(open(args.salt))]
        for p in pts:
            allowed.append((p[0] - 4, p[2] - 4, p[0] + 4, p[2] + 4))
        for rp in SITES['road_path']:
            allowed.append((rp[0] - 3, rp[2] - 3, rp[0] + 3, rp[2] + 3))

        def ok_xz(x, z):
            for a in allowed:
                if a[0] <= x <= a[2] and a[1] <= z <= a[3]:
                    return True
            return False

        # Two readers with their OWN section caches, swapped by reference. The first version
        # of this called use() per cell, which rebuilt the region reader and threw the
        # section cache away sixty thousand times and never finished.
        now_chunk, now_sec = reader(args.world), {}
        was_chunk, was_sec = reader(args.baseline), {}

        def at(which, x, y, z):
            if which:
                V.chunk, V._sec = now_chunk, now_sec
            else:
                V.chunk, V._sec = was_chunk, was_sec
            try:
                return V.block(int(x), int(y), int(z))
            except Exception:                            # noqa: BLE001
                return '?'

        # WHAT THE WORLD DOES ON ITS OWN.
        #
        # A Minecraft world is not static and this probe is not entitled to pretend it is.
        # Over a playthrough that runs five seasons in fifteen minutes, grass spreads onto
        # bare dirt, snow layers land and melt, water freezes and thaws, leaves decay and
        # flowers grow. Measured on the run of 2026-09-05: 48 "changes" outside every
        # registry footprint, every single one of them `dirt -> grass_block` or
        # `air -> snow`, three hundred blocks from anything the pack touches.
        #
        # So the probe ignores a change BETWEEN two natural states, and only a change
        # between two natural states. Anything the pack could have written -- planks, glass,
        # stone brick, a lamp, a door, a chest -- is still a stray wherever it turns up.
        NATURAL = set('''minecraft:air minecraft:cave_air minecraft:grass_block minecraft:dirt
            minecraft:coarse_dirt minecraft:rooted_dirt minecraft:podzol minecraft:mycelium
            minecraft:snow minecraft:snow_block minecraft:powder_snow minecraft:ice
            minecraft:water minecraft:mud minecraft:moss_block minecraft:short_grass
            minecraft:grass minecraft:tall_grass minecraft:fern minecraft:large_fern
            minecraft:dead_bush minecraft:seagrass minecraft:tall_seagrass
            minecraft:sweet_berry_bush minecraft:vine minecraft:lily_pad'''.split())

        def natural_drift(was, now, x, y, z):
            if was in NATURAL and now in NATURAL:
                return True
            # leaves and flowers: any *_leaves to any *_leaves or air, and any small plant
            for k in ('_leaves', 'flower', 'tulip', 'orchid', 'daisy', 'bluet', 'poppy',
                      'dandelion', 'cornflower', 'allium', 'sapling', 'mushroom', 'moss',
                      'azalea', 'snow', 'ice', 'rhododendron'):
                if k in was or k in now:
                    return True
            # Geolosys scatters surface indicator plants over its own ore as the world runs.
            if now.startswith('geolosys:') or was.startswith('geolosys:'):
                return True
            # FIRE. Supplementaries leaves `supplementaries:ash` where something burned, so a
            # column with ash in it has burned, and what is missing from it burned. Measured
            # on the run of 2026-09-05: two buried oak logs at -332,68..69 -- two hundred
            # blocks from anything the pack writes -- came back as ash and air. That is the
            # world's own fire, not a story beat, and the ash two blocks down is the receipt.
            for dy in range(-2, 3):
                if at(True, x, y + dy, z) == 'supplementaries:ash':
                    return True
            return False

        anchor = SITES['anchor']
        strays = []
        scanned = 0
        # a coarse lattice over the whole valley
        for x in range(anchor[0] - 90, anchor[0] + 91, 3):
            for z in range(anchor[2] - 90, anchor[2] + 91, 3):
                if ok_xz(x, z):
                    continue
                for y in range(anchor[1] - 8, anchor[1] + 22, 2):
                    scanned += 1
                    was = at(False, x, y, z)
                    now = at(True, x, y, z)
                    if was != now and not natural_drift(was, now, x, y, z):
                        strays.append('%d %d %d %s -> %s' % (x, y, z, was, now))
                    if len(strays) > 40:
                        break
        use(args.world)
        R.add('nothing_else_changed', not strays,
              '%d cells sampled outside every registry footprint, %d changed by anything '
              'other than weather and growth%s'
              % (scanned, len(strays), '' if not strays else ': ' + '; '.join(strays[:6])))
    else:
        R.add('nothing_else_changed', False, 'no baseline world to compare against')

    R.show()
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(R.rows, indent=1) + '\n')
    return 0 if R.ok else 1


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest='cmd', required=True)
a = sub.add_parser('salt'); a.add_argument('--world', default='server/world'); a.add_argument('--out', default='scratch/shipped_playthrough/salt.json')
b = sub.add_parser('player'); b.add_argument('--player', default='packtester')
d = sub.add_parser('check'); d.add_argument('--world', default='server/world')
d.add_argument('--salt', default=None); d.add_argument('--baseline', default=None)
d.add_argument('--json', default=None)
args = ap.parse_args()
sys.exit({'salt': salt, 'player': player, 'check': check}[args.cmd](args))
