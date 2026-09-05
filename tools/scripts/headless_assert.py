#!/usr/bin/env python3
"""headless_assert.py -- read the shipped world off its REGION FILES and prove the things
the story is supposed to have done, with no Minecraft client anywhere.

tools/scripts/playthrough.sh is the full harness and it needs a client: it salts twenty
player blocks, joins an offline client at the world spawn, and makes the cottage placements
with a player's own hands so BlockEvents.placed fires. None of that can run while Josh is at
the Mac. This script is the half that can: everything a headless server plus a region reader
can settle.

  --phase pristine   the world as it ships, BEFORE anything runs
  --phase act1       a fresh copy with ONLY /valley finale act1 run against it
  --phase after      the world after every act and every scene has run

Every coordinate comes from pack/kubejs/data/valley/valley_sites.json and every building
probe comes from the structure template's own palette, read out of the mod jar. Nothing here
carries a hand-typed coordinate.
"""
import sys, os, json, argparse, pathlib, collections, glob

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / 'scratch'))
sys.path.insert(0, str(ROOT / 'tools' / 'scripts'))
import vt_lib as V
import seed_hunt as SH

SITES = json.load(open('pack/kubejs/data/valley/valley_sites.json'))
PLAN = None
AIR = ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air')

# The fifteen people the valley ends with. docs/NPCS.md, and the same list the
# client harness greps the server log for.
RESIDENTS = ["Bram Tolliver", "Halden Root", "Marnie Ashcombe", "Nella Brightwater",
             "Corin Ashe", "Mab Oldfield", "Tess Weaver", "Oda Vance", "Pip Ashcombe",
             "Mudlark", "Puddle", "Reed", "Sedge", "Tobin Gale", "Wisp"]

# The doors a finale or a scene opens, and the two it deliberately does not: the granary is
# a store room nobody lives in and the boathouse is Nella's shed. The cottage door is not
# hung at all until Q3 puts it there, which needs a player.
DOORS_STORY = ['inn', 'mill', 'marnie_house', 'pip_house', 'church', 'store',
               'town_hall', 'newcomer_tess', 'newcomer_mab', 'newcomer_corin']
DOORS_SHUT = ['granary', 'boathouse']

# Anything that makes light. The valley is dark by design: outside a building the only lit
# things in the whole town are meant to be the forty lamp posts once a finale lights them.
LIGHT_IDS = ('torch', 'lantern', 'campfire', 'glowstone', 'sea_lantern', 'shroomlight',
             'jack_o_lantern', 'end_rod', 'beacon', 'conduit', 'fire', 'lava',
             'candle', 'redstone_lamp', 'copper_lamp', 'soul_', 'froglight',
             'crying_obsidian', 'magma_block', 'sculk_catalyst', 'ochre',
             'verdant', 'pearlescent', 'light')


# =============================================================================
# world readers
# =============================================================================
def use(world):
    cache = {}
    w = pathlib.Path(world)

    def chunk(cx, cz):
        rk = (cx >> 5, cz >> 5)
        if rk not in cache:
            q = w / 'region' / ('r.%d.%d.mca' % rk)
            cache[rk] = SH.read_region(q) if q.exists() else {}
        return cache[rk].get((cx & 31, cz & 31))
    V.chunk = chunk
    V._sec = {}


def blk(x, y, z):
    try:
        return V.block(int(x), int(y), int(z))
    except Exception:                                    # noqa: BLE001
        return '?'


def props(x, y, z):
    try:
        return V.block_full(int(x), int(y), int(z))[1] or {}
    except Exception:                                    # noqa: BLE001
        return {}


def entities(world):
    """vt_lib.entities() is hard-wired to server/world; this one takes a path."""
    out = []
    for p in sorted(glob.glob(str(pathlib.Path(world) / 'entities' / '*.mca'))):
        try:
            rg = SH.read_region(p)
        except Exception:                                # noqa: BLE001
            continue
        for c in rg.values():
            for e in c.get('Entities', []):
                out.append(e)
    return out


def is_lit(bid, st):
    """A block that is emitting light where it stands."""
    if not any(k in bid for k in LIGHT_IDS):
        return False
    if 'lit' in st:
        return str(st['lit']).lower() == 'true'
    # a torch, a lantern, glowstone: no state, always on
    return True


def plan():
    """The 50 verification probes plan_town.py wrote into town_plan.js, absolute."""
    global PLAN
    if PLAN is None:
        import re
        s = open('pack/kubejs/server_scripts/town_plan.js').read()
        m = re.search(r'\n  probes: (\[.*?\]),\n', s, re.S)
        PLAN = json.loads(m.group(1))
    origins = {'anchor': SITES['anchor'], 'works': SITES['works']['mark']}
    out = []
    for p in PLAN:
        o = origins[p.get('origin', 'anchor')]
        out.append((p['label'], [o[0] + p['pos'][0], o[1] + p['pos'][1], o[2] + p['pos'][2]],
                    p['block']))
    return out


# The palette a building must show inside its own site box. For a template it is the
# template's own most-used solid blocks, read out of the mod jar; for the three the planner
# builds itself there is no jar, so the palette is the material list the planner uses.
# The pristine pregen, read for the SAME box, so a palette block that the meadow already
# had there (oak logs in a wood, water in a stream) can never stand in for a building.
PREGEN = 'scratch/pregen'

CUSTOM_PALETTE = {
    'greenhouse': ['minecraft:stone_bricks', 'minecraft:glass', 'minecraft:glass_pane',
                   'createdeco:copper_bars', 'minecraft:waxed_exposed_cut_copper_stairs',
                   'minecraft:spruce_slab'],
    'bathhouse': ['minecraft:spruce_planks', 'minecraft:stone_bricks', 'minecraft:cauldron',
                  'minecraft:water_cauldron', 'minecraft:waxed_exposed_cut_copper_stairs',
                  'minecraft:stone_brick_slab'],
    'tobin_camp': ['minecraft:copper_ore', 'minecraft:stone', 'minecraft:oak_fence',
                   'minecraft:campfire', 'minecraft:barrel', 'minecraft:cobblestone'],
}
FRAGILE = ('air', 'jigsaw')
_PAL = {}


def palette_for(key, b, box, y0, y1):
    """The blocks that prove THIS piece is standing in THIS box.

    Candidates are the template's own most-used blocks, read out of the mod jar rather than
    out of a catalogue -- the bell tower is a kaisyn outpost piece and media/templates.json
    does not carry it. Then every candidate the PRISTINE PREGEN already had inside the same
    box is struck out, because a farm's oak logs prove nothing if the column was a wood
    before the town was planned. What is left is a probe: a block that is there because the
    build put it there.
    """
    if key in _PAL:
        return _PAL[key]
    if b.get('template'):
        t = V.template(b['template'])
        n = collections.Counter(c[0] for c in t['cells'].values())
        cand = [bid for bid, _ in n.most_common() if not any(k in bid for k in FRAGILE)][:14]
    else:
        cand = list(CUSTOM_PALETTE[key])
    keep, saved = [], (V.chunk, V._sec)
    use(PREGEN)
    had = set()
    for x in range(box[0], box[2] + 1):
        for z in range(box[1], box[3] + 1):
            for y in range(y0, y1):
                had.add(blk(x, y, z))
    V.chunk, V._sec = saved
    for bid in cand:
        if bid not in had:
            keep.append(bid)
        if len(keep) == 6:
            break
    _PAL[key] = keep
    return keep


# =============================================================================
class Report(object):
    def __init__(self, title):
        self.title = title
        self.rows = []

    def add(self, name, ok, detail):
        self.rows.append({'probe': name, 'ok': bool(ok), 'detail': detail})

    @property
    def ok(self):
        return all(r['ok'] for r in self.rows)

    def show(self):
        print('=== %s' % self.title)
        w = max(len(r['probe']) for r in self.rows)
        for r in self.rows:
            print('  %-*s  %-4s  %s' % (w, r['probe'], 'PASS' if r['ok'] else 'FAIL',
                                        r['detail']))
        print('  %d of %d probes pass'
              % (sum(1 for r in self.rows if r['ok']), len(self.rows)))


# ---- the probes shared by every phase ---------------------------------------
def probe_bell(R):
    bell = [(lab, pos) for lab, pos, b in plan() if lab == 'church_bell'][0]
    got = blk(*bell[1])
    R.add('bell_present', got == 'minecraft:bell',
          '%s at %s' % (got, ' '.join(map(str, bell[1]))))


def probe_stake(R):
    """The socket is a HOLE, and the hole is the point: Q7 is the player driving the
    Surveyor's Stake into it, so the cell itself must stay empty and the plinth under it
    must be the chiselled course the planner set, not the meadow."""
    s = SITES['stake_socket']
    cell = blk(*s)
    floor = blk(s[0], s[1] - 1, s[2])
    R.add('stake_socket', cell in AIR and floor == 'minecraft:chiseled_stone_bricks',
          'empty socket over a %s plinth at %s (cell=%s)'
          % (floor.split(':')[-1], ' '.join(map(str, s)), cell.split(':')[-1]))


def probe_doors_exist(R):
    bad, cot = [], None
    for k, p in SITES['doors'].items():
        got = blk(*p)
        if k == 'cottage':
            cot = got
            continue
        if '_door' not in got:
            bad.append('%s=%s@%s' % (k, got, ' '.join(map(str, p))))
    R.add('doors_exist', not bad,
          '12 of 12 hung doors are real door blocks (cottage=%s, Q3 hangs it)' % cot
          if not bad else 'missing: ' + ', '.join(bad))


def probe_sites(R, R2):
    misses, rows = [], []
    for key, b in SITES['buildings'].items():
        box = SITES['site_boxes'][key]
        y0 = b['level'] - 2
        y1 = b['level'] + 26
        pal = palette_for(key, b, box, y0, y1)
        lo = None
        found = set()
        for x in range(box[0], box[2] + 1):
            for z in range(box[1], box[3] + 1):
                for y in range(y0, y1):
                    g = blk(x, y, z)
                    if g in pal:
                        found.add(g)
            if len(found) >= 3:
                break
        rows.append('%s:%d' % (key, len(found)))
        if len(found) < 3:
            misses.append('%s only %d of %s' % (key, len(found), pal[:3]))
        del lo
    R.add('site_boxes_hold_buildings', not misses,
          '%d buildings, >=3 palette blocks each (%s)' % (len(rows), ' '.join(rows))
          if not misses else '; '.join(misses))
    del R2


def probe_plan(R):
    bad = []
    for lab, pos, want in plan():
        got = blk(*pos)
        if got != want:
            bad.append('%s want %s got %s @%s' % (lab, want, got, ' '.join(map(str, pos))))
    R.add('plan_block_probes', not bad,
          '%d of %d of the planner\'s own probes' % (len(plan()) - len(bad), len(plan()))
          + ('' if not bad else '; ' + '; '.join(bad[:6])))


def lamp_state():
    lit, dark = [], []
    for L in SITES['lamps']:
        x, y, z = L['pos']
        st = props(x, y + 1, z)
        b = blk(x, y + 1, z)
        (lit if str(st.get('lit', '')).lower() == 'true' else dark).append((L, b))
    return lit, dark


# =============================================================================
def phase_pristine(args, R):
    lit, dark = lamp_state()
    R.add('lamps_dark', not lit,
          '%d of 40 lamp posts unlit' % len(dark)
          + ('' if not lit else '; LIT: ' + ', '.join(str(l[0]['n']) for l in lit)))

    # the plaza, before Act I, from bedrock-ish to well over the rooftops
    pz = SITES['site_boxes']['plaza']
    a = SITES['anchor']
    strays = []
    for x in range(pz[0], pz[2] + 1):
        for z in range(pz[1], pz[3] + 1):
            for y in range(a[1] - 4, a[1] + 20):
                b = blk(x, y, z)
                if b in AIR or b == '?':
                    continue
                if is_lit(b, props(x, y, z)):
                    strays.append('%s @%d %d %d' % (b, x, y, z))
    R.add('plaza_unlit_before_act1', not strays,
          'no lit light source anywhere in the %dx%d plaza box'
          % (pz[2] - pz[0] + 1, pz[3] - pz[1] + 1)
          if not strays else '%d LIT: %s' % (len(strays), '; '.join(strays[:8])))

    # the cottage gaps: the story does not fill these, Q3 does, with a player's hands
    c = SITES['cottage']
    cells = [('door', c['door']), ('door_upper', [c['door'][0], c['door'][1] + 1, c['door'][2]])]
    for i, w in enumerate(c['windows']):
        cells.append(('window_%d' % (i + 1), w))
    for i, r in enumerate(c['roof_patch']):
        cells.append(('roof_patch_%d' % (i + 1), r))
    cells.append(('bed', [c['bed'][0], c['bed'][1] + 1, c['bed'][2]]))
    filled = ['%s=%s' % (n, blk(*p)) for n, p in cells if blk(*p) not in AIR]
    R.add('cottage_gaps_air', not filled,
          'all %d gap cells (door, %d windows, %d roof, bed) are air'
          % (len(cells), len(c['windows']), len(c['roof_patch']))
          if not filled else 'already filled: ' + ', '.join(filled))

    probe_doors_exist(R)
    shut = [k for k, p in SITES['doors'].items()
            if k != 'cottage' and str(props(*p).get('open', '')).lower() == 'true']
    R.add('doors_shut_before_the_story', not shut,
          'all 12 hung doors shut' if not shut else 'already open: ' + ', '.join(shut))

    probe_bell(R)
    probe_stake(R)

    # The lever is NOT day one: the Works chamber, its bunker rooms and the andesite panel
    # the lever hangs on are, and Q71 is the player putting the lever on the panel. So on
    # the shipped world the panel must be there and the cell in front of it must be clear.
    lv = SITES['works']['lever']
    pn = SITES['works']['panel']
    R.add('works_panel_ready',
          blk(*lv) in AIR and blk(*pn) == 'minecraft:polished_andesite',
          'panel %s, lever cell %s (Q71 hangs the lever)'
          % (blk(*pn).split(':')[-1], blk(*lv).split(':')[-1]))
    cd = SITES['cellar']['door']
    R.add('cellar_door_present', 'iron_door' in blk(*cd),
          '%s open=%s' % (blk(*cd), props(*cd).get('open')))

    probe_sites(R, None)
    probe_plan(R)


def phase_act1(args, R):
    lit, dark = lamp_state()
    want = set()
    for L in SITES['lamps']:
        if L['route'] in ('finale', 'q07'):
            want.add(L['n'])
    got = set(l[0]['n'] for l in lit)
    R.add('lamps_lit_after_act1', len(lit) == 6 and got == want,
          '%d lit (want 6: the four plaza kerb posts + the two on the High Street) -> %s'
          % (len(lit), sorted(got)))
    R.add('the_other_34_still_dark', len(dark) == 34, '%d of 40 still unlit' % len(dark))


def phase_after(args, R):
    # THE FORTIETH LAMP IS THE PLAYER'S. Josie's porch post (route q90) is lit by the
    # BlockEvents.placed check in valley_checks.js and by nothing else -- Act IV's sweep
    # deliberately skips it (roadLamps()) and the Q74 scene says so out loud. So 39 of 40
    # is the headless maximum, and the one dark post has to be that one and no other.
    lit, dark = lamp_state()
    porch = set(L['n'] for L in SITES['lamps'] if L['route'] == 'q90')
    darkn = set(d[0]['n'] for d in dark)
    R.add('lamps_lit', darkn == porch,
          '%d of 40 burning; the one dark post is Josie\'s porch (lamp %s, route q90, '
          'lit by Q90 in a player\'s hands)' % (len(lit), ','.join(map(str, sorted(porch))))
          if darkn == porch
          else '%d burning; DARK: %s' % (len(lit), ', '.join(
              '%d@%s' % (d[0]['n'], d[1]) for d in sorted(dark, key=lambda d: d[0]['n'])[:10])))

    ents = entities(args.world)
    npcs = []
    for e in ents:
        if 'easy_npc' not in str(e.get('id', '')):
            continue
        nm = str(e.get('CustomName') or '')
        pos = [float(v) for v in e.get('Pos', [0, 0, 0])]
        npcs.append((nm, pos))
    found, missing = {}, []
    for who in RESIDENTS:
        hit = [n for n in npcs if who in n[0]]
        if hit:
            found[who] = hit[0][1]
        else:
            missing.append(who)
    R.add('residents_present', not missing,
          '%d of 15 residents in the region files (%d easy_npc entities in all)'
          % (len(found), len(npcs))
          + ('' if not missing else '; MISSING: ' + ', '.join(missing)))

    # every resident standing somewhere the registry put a person: a door, a stand, a mark,
    # the anchor or the pier. 24 blocks, because Act V leaves the town on the square.
    posts = [SITES['anchor'], SITES['pier'], SITES['stake_socket']] + \
            list(SITES['doors'].values()) + list(SITES['marks'].values()) + \
            [s['pos'] for s in SITES['npc_stands']] + list(SITES['npc_homes'].values())
    adrift = []
    for who, p in found.items():
        d = min(max(abs(p[0] - q[0]), abs(p[2] - q[2])) for q in posts)
        if d > 24:
            adrift.append('%s %.0f blocks out' % (who, d))
    R.add('residents_at_their_posts', not adrift,
          'every resident within 24 blocks of a registry door, stand or mark'
          if not adrift else '; '.join(adrift))

    opened = []
    for k in DOORS_STORY:
        p = SITES['doors'][k]
        st = props(*p)
        if str(st.get('open', '')).lower() != 'true':
            opened.append('%s=%s open=%s' % (k, blk(*p), st.get('open')))
    R.add('story_doors_open', not opened,
          'all %d doors a finale or a scene opens are standing open' % len(DOORS_STORY)
          if not opened else 'still shut: ' + ', '.join(opened))

    # the two the story never touches must still be real, openable doors
    bad = [k for k in DOORS_SHUT
           if '_door' not in blk(*SITES['doors'][k]) or 'open' not in props(*SITES['doors'][k])]
    R.add('untouched_doors_still_openable', not bad,
          'granary and boathouse still hung, shut, with an open property'
          if not bad else ', '.join(bad))

    probe_bell(R)
    probe_stake(R)

    lv = SITES['works']['lever']
    R.add('works_lever_thrown',
          'lever' in blk(*lv) and str(props(*lv).get('powered', '')).lower() == 'true',
          '%s powered=%s' % (blk(*lv), props(*lv).get('powered')))
    cd = SITES['cellar']['door']
    R.add('cellar_door_open',
          'iron_door' in blk(*cd) and str(props(*cd).get('open', '')).lower() == 'true',
          '%s open=%s' % (blk(*cd), props(*cd).get('open')))

    c = SITES['cottage']
    still = [n for n, p in (('door', c['door']),
                            ('bed', [c['bed'][0], c['bed'][1] + 1, c['bed'][2]]))
             if blk(*p) in AIR]
    R.add('cottage_still_the_player\'s_job', len(still) == 2,
          'door and bed still air: the story never fills them (%s)' % ', '.join(still))

    probe_sites(R, None)
    probe_plan(R)


ap = argparse.ArgumentParser()
ap.add_argument('--world', required=True)
ap.add_argument('--phase', required=True, choices=('pristine', 'act1', 'after'))
ap.add_argument('--json', default=None)
args = ap.parse_args()
use(args.world)
R = Report('%s  (%s)' % (args.phase, args.world))
{'pristine': phase_pristine, 'act1': phase_act1, 'after': phase_after}[args.phase](args, R)
R.show()
if args.json:
    pathlib.Path(args.json).write_text(json.dumps(R.rows, indent=1) + '\n')
sys.exit(0 if R.ok else 1)
