#!/usr/bin/env python3
"""The four things the client regression added, driven and then read back.

  cmds  <ax> <ay> <az>          -> the console commands to run, one per line
  check <ax> <ay> <az> <log>    -> reads the log slice those commands wrote and
                                   prints one PASS/FAIL line per assertion

The four:
  1. the 3x3 hammer   — the quest's reward item resolves in the live registry and
                        the cheap copper recipe is in the server's RecipeManager,
                        which is the registry JEI mirrors on the client.
  2. anchor clearance — driven in playthrough.sh itself (it has to run before the
                        town is built); read back here off the CLIENT chat log.
  3. Q59's Ribbit camp— the four stands are open ground: feet and head air, floor
                        solid, and the four Ribbits actually standing on them.
                        A cart would put fence/barrel/canopy in exactly those cells.
  4. Bram's Act IV chair — the scene's `tp @e[tag=npc_bram]` lands, cold, on a
                        chunk the scene had to forceload first.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLAN = json.loads((ROOT / 'media' / 'town_plan.json').read_text())
CAMP = PLAN['square']['scenes']['ribbit_camp']
CARTS = PLAN['square']['market_carts']
RIBBITS = ['ribbit_reed', 'ribbit_sedge', 'ribbit_mudlark', 'ribbit_puddle']
BRAM_OFF = [23, 1, -7]          # act4_bram_chair: tp @e[tag=npc_bram,limit=1] ~23 ~1 ~-7
HAMMER = 'justhammers:stone_hammer'
CHEAP = 'valley:cheap/copper_hammer'


def abs3(a, off):
    return [a[0] + off[0], a[1] + off[1], a[2] + off[2]]


def cmds(a):
    P = 'packtester'
    out = ['say NB_BEGIN']

    # ---- 1. the hammer -----------------------------------------------------
    # `give` is NOT a safe probe here: this runs after 321 audit commands have
    # emptied every `give` reward into the player, his inventory is full, and a
    # full inventory sends the hammer to the GROUND — so the bag count reads
    # zero and a perfectly good item id looks broken. `item replace` writes a
    # named slot whether the bag is full or not, and SelectedItem reads that
    # exact slot back with its id in it.
    out += ['say NB_HAMMER',
            f'item replace entity {P} weapon.mainhand with {HAMMER} 1',
            f'data get entity {P} SelectedItem',
            # The RecipeManager validates this argument, so an id that is not
            # registered fails the PARSE with "Unknown recipe" and never runs.
            f'recipe take {P} {CHEAP}',
            f'recipe give {P} {CHEAP}',
            f'recipe take {P} {HAMMER}',
            f'recipe give {P} {HAMMER}']

    # ---- 3. Q59's Ribbit camp ---------------------------------------------
    stands = [abs3(a, s) for s in CAMP['stands']]
    lo = [min(p[i] for p in stands) - 10 for i in (0, 2)]
    hi = [max(p[i] for p in stands) + 10 for i in (0, 2)]
    out += ['say NB_Q59',
            f'forceload add {lo[0]} {lo[1]} {hi[0]} {hi[1]}',
            'valley scene q59']
    out += ['say NB_Q59_SETTLE']
    for i, p in enumerate(stands):
        x, y, z = p
        out += [f'execute if block {x} {y} {z} minecraft:air run say NB_Q59_FEET{i}_AIR',
                f'execute if block {x} {y+1} {z} minecraft:air run say NB_Q59_HEAD{i}_AIR',
                f'execute unless block {x} {y-1} {z} minecraft:air run say NB_Q59_FLOOR{i}_SOLID']
    cf = abs3(a, CAMP['campfire'])
    out += [f'execute if block {cf[0]} {cf[1]} {cf[2]} minecraft:campfire[lit=true] '
            'run say NB_Q59_CAMPFIRE_LIT']
    for n in RIBBITS:
        out += [f'say NB_Q59_POS_{n}',
                f'data get entity @e[tag=npc_{n},limit=1] Pos']

    # ---- 4. Bram's Act IV chair, cold -------------------------------------
    b = abs3(a, BRAM_OFF)
    out += ['say NB_Q73',
            f'forceload add {b[0]-16} {b[2]-16} {b[0]+16} {b[2]+16}',
            'valley scene q73']
    # the scene lets its own forceload go a few seconds after the arrival, and
    # `forceload remove <area>` is not reference counted, so re-assert before
    # reading or `@e[tag=npc_bram]` matches nothing and measures nothing.
    out += ['say NB_Q73_SETTLE',
            f'forceload add {b[0]-16} {b[2]-16} {b[0]+16} {b[2]+16}',
            'say NB_Q73_POS',
            'data get entity @e[tag=npc_bram,limit=1] Pos']
    out += ['say NB_END']
    return out


POS_RE = re.compile(r'has the following entity data: \[([-0-9.]+)d, ([-0-9.]+)d, ([-0-9.]+)d\]')


def check(a, logpath):
    txt = pathlib.Path(logpath).read_text(errors='replace')
    lines = txt.splitlines()
    # the slice this probe wrote
    try:
        i0 = max(i for i, l in enumerate(lines) if 'NB_BEGIN' in l)
    except ValueError:
        print('FAIL  probe never ran (no NB_BEGIN in the log)')
        return 1
    sl = lines[i0:]
    blob = '\n'.join(sl)
    res = []

    def ok(cond, name, extra=''):
        res.append((bool(cond), name, extra))

    # ---- 1. hammer ---------------------------------------------------------
    # `clear <p> <item> 0` counts without removing. An empty bag answers
    # "No items were found on player X", NOT "Found 0 matching items", so both
    # forms have to be read, in order, or the before-count goes missing and the
    # assertion fails on a perfectly good give.
    hs = blob[blob.find('NB_HAMMER'):blob.find('NB_Q59')]
    # Two independent reads, either of which proves the point: the item NBT in
    # the player's hand, and the command's own answer (an id that is not in the
    # registry fails `item replace` at the PARSE, with "Unknown item", so a
    # success line cannot be produced by a broken id).
    held = re.search(r'id: "([a-z0-9_.:/-]+)"', hs)
    repl = re.search(r'[Rr]eplaced? .*?slot.*?with \d+ ([a-z0-9_.:/-]+)', hs)
    got = (held.group(1) if held else None) or (repl.group(1) if repl else None)
    ok(got == HAMMER,
       'the hammer the quest rewards resolves in the live item registry',
       f'read back = {got or "nothing"}'
       + (' (from the player NBT)' if held else ' (from the command answer)' if repl else ''))
    ok('Unknown recipe' not in blob, 'no "Unknown recipe" — both hammer recipes are registered')
    unlocked = len(re.findall(r'nlocked \d+ recipe', blob))
    ok(unlocked >= 2, 'recipe give accepted for both the cheap copper hammer and the mod hammer',
       f'unlock lines={unlocked}')

    # ---- 3. Q59 ------------------------------------------------------------
    for i in range(len(CAMP['stands'])):
        ok(f'NB_Q59_FEET{i}_AIR' in blob, f'Q59 stand {i}: feet cell is open air')
        ok(f'NB_Q59_HEAD{i}_AIR' in blob, f'Q59 stand {i}: head cell is open air (no cart canopy)')
        ok(f'NB_Q59_FLOOR{i}_SOLID' in blob, f'Q59 stand {i}: floor below is solid')
    ok('NB_Q59_CAMPFIRE_LIT' in blob, 'Q59 campfire is lit on its own cell')

    stands = [abs3(a, s) for s in CAMP['stands']]
    # cart footprints, for a distance number rather than a bare assertion
    cart_cells = [abs3(a, c['min']) for c in CARTS]
    for n in RIBBITS:
        j = next((k for k, l in enumerate(sl) if f'NB_Q59_POS_{n}' in l), None)
        m = None
        if j is not None:
            for l in sl[j:j + 6]:
                m = POS_RE.search(l)
                if m:
                    break
        if not m:
            ok(False, f'Q59 {n}: position read back', 'no data-get answer')
            continue
        p = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
        d = min(max(abs(p[0] - s[0] - .5), abs(p[1] - s[1]), abs(p[2] - s[2] - .5)) for s in stands)
        dc = min(max(abs(p[0] - c[0]), abs(p[2] - c[2])) for c in cart_cells)
        ok(d <= 1.5, f'Q59 {n}: standing on a camp cell',
           f'{d:.2f} blocks off the nearest stand; nearest cart corner {dc:.1f} away')

    # ---- 4. Bram -----------------------------------------------------------
    b = abs3(a, BRAM_OFF)
    j = next((k for k, l in enumerate(sl) if 'NB_Q73_POS' in l), None)
    m = None
    if j is not None:
        for l in sl[j:j + 6]:
            m = POS_RE.search(l)
            if m:
                break
    if not m:
        ok(False, "Bram's Act IV chair teleport", 'no data-get answer')
    else:
        p = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
        d = max(abs(p[0] - b[0] - .5), abs(p[1] - b[1]), abs(p[2] - b[2] - .5))
        ok(d <= 1.5, "Bram's Act IV chair teleport landed, cold",
           f'{d:.2f} blocks off {b}; he is at {p}')
    # A `tp @e[tag=npc_*]` that matches nothing is NOT logged as "command
    # returned 0" — runGroup counts it into the arrival retry (missed++), and
    # only a retry that runs out of attempts says anything. That line is the
    # signal that the chair teleport was dropped on the floor.
    tail = blob[blob.find('NB_Q73'):]
    ok('arrival gave up' not in tail,
       "the q73 arrival retry never gave up on a resident")

    npass = sum(1 for c, _, _ in res if c)
    for c, name, extra in res:
        print(('PASS  ' if c else 'FAIL  ') + name + (f'   [{extra}]' if extra else ''))
    print(f'--- new-bits probe: {npass}/{len(res)} pass, {len(res)-npass} fail')
    return 0 if npass == len(res) else 1


if __name__ == '__main__':
    mode = sys.argv[1]
    a = [int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])]
    if mode == 'cmds':
        print('\n'.join(cmds(a)))
    else:
        sys.exit(check(a, sys.argv[5]))
