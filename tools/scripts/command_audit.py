#!/usr/bin/env python3
"""Emit every quest command reward and every datapack function line as console commands with test substitutions.
Usage: command_audit.py <player> > cmds.txt"""
import json, pathlib, re, sys, hashlib
root = pathlib.Path(__file__).resolve().parents[2]; player = sys.argv[1] if len(sys.argv) > 1 else 'packtester'
def hid(key, salt=''):
    # Bit 63 is cleared on purpose. FTB Quests reads every object id with
    # QuestObjectBase.parseCodeString, which is Long.parseLong(s, 16) -- SIGNED. An id
    # whose top hex digit is 8-F overflows, the NumberFormatException is swallowed, the
    # id comes back as 0, and the quest file is then loaded with a FRESH RANDOM id in its
    # place. 622 of this pack's 1193 object ids were in that half of the space, so 66 of
    # the 126 quests had a different id every time the file was regenerated: /ftbquests
    # could not address them, fourteen of the twenty-four KubeJS auto-completions
    # silently did nothing, and their progress reset on every pack update.
    # Masking only touches ids that were already unstable -- every id that worked before
    # has its top bit clear already and comes out byte-identical -- so no live progress
    # is lost by this change.
    v = int(hashlib.sha1((salt + key).encode()).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF
    return '%016X' % (v or 1)
out = []
for f in sorted((root / 'story/quests').glob('*.json')):
    d = json.loads(f.read_text()); ch = d['chapter']['key']
    for q in d['quests']:
        for r in q.get('rewards', []):
            if r.get('type') != 'command': continue
            c = r['command'].strip(); c = c[1:] if c.startswith('/') else c
            c = c.replace('@p', player).replace('{team}', 'Cozy').replace('{quest}', hid(q['key'])).replace('{chapter}', hid(ch, 'chapter/'))
            if '{x}' in c: c = 'execute as %s at %s run ' % (player, player) + c.replace('{x}', '~').replace('{y}', '~').replace('{z}', '~')
            elif '~' in c: c = 'execute as %s at %s run ' % (player, player) + c
            out.append(f'# {q["key"]}\n{c}')
# THE DATAPACK FUNCTIONS ARE NOT AUDITED, AND MUST NOT BE.
#
# This used to replay every line of every .mcfunction in the pack as
#     execute as <player> at <player> positioned ~8 ~ ~8 run <line>
# which was reasonable when the functions were live code invoked at a runtime anchor. They
# are not any more: `valley:act1/cottage` and `valley:act1/square_path` are DERIVATIONS that
# tools/scripts/plan_town.py writes out so the cottage and the road can be read by a human,
# nothing in the pack calls them, and valley_finales.js REFUSES `run function valley:`.
#
# Replaying them is actively destructive, and it was measured being so. On the shipped-world
# playthrough of 2026-09-05, the audit ran while the test player was standing at the farm and
# the first line of cottage.mcfunction --
#     fill ~-11 ~0 ~-14 ~11 ~15 ~11 minecraft:air
# -- took the cottage, the gate sign, the porch post and four lamp posts off the map, then
# the next three re-laid a pad over the hole. The world asserts caught it (the hearthstone
# read `coarse_dirt`), which is what they are for, but the audit had no business running it.
#
# If a function ever becomes live again, audit it by CALLING it at the position it documents,
# not by replaying its body at whatever coordinate the player happens to be standing on.
print('\n'.join(out))
