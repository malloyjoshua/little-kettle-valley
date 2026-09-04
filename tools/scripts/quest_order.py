#!/usr/bin/env python3
"""Print quests in dependency order as: key<TAB>id<TAB>title<TAB>chapter<TAB>cmd_id.
Uses story/quests/*.json and the compiler's id scheme. cmd_id is the same id written the way
FTB Quests' command argument can actually parse it — see cmd_id() below."""
import json, pathlib, hashlib, sys, collections
root = pathlib.Path(__file__).resolve().parents[2]
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
def cmd_id(h):
    """FTB Quests parses /ftbquests' object argument with Long.parseLong(s, 16), which is
    SIGNED: an id with the top bit set overflows, is swallowed, and comes back as 0, so the
    command answers "Invalid Object ID". 66 of this pack's 126 ids are in that half. The same
    long written as a negative hex literal parses, and '-' is legal unquoted in Brigadier.
    valley_core.js#cmdId does exactly this at runtime; keep the two in step."""
    v = int(h, 16)
    return h if v < 2**63 else '-%X' % (2**64 - v)
quests = {}
for f in sorted((root / 'story/quests').glob('*.json')):
    d = json.loads(f.read_text())
    for q in d['quests']: quests[q['key']] = (q, d['chapter']['key'])
indeg = {k: 0 for k in quests}; out = collections.defaultdict(list)
for k, (q, ch) in quests.items():
    for dep in q.get('deps', []):
        if dep in quests: indeg[k] += 1; out[dep].append(k)
ready = sorted([k for k, n in indeg.items() if n == 0]); order = []
while ready:
    k = ready.pop(0); order.append(k)
    for n in out[k]:
        indeg[n] -= 1
        if indeg[n] == 0: ready.append(n); ready.sort()
if len(order) != len(quests): print('CYCLE or missing deps', file=sys.stderr)
for k in order:
    q, ch = quests[k]; print(f"{k}\t{hid(k)}\t{q['title']}\t{ch}\t{cmd_id(hid(k))}")
