#!/usr/bin/env python3
"""Print quests in dependency order as: key<TAB>id<TAB>title<TAB>chapter. Uses story/quests/*.json and the compiler's id scheme."""
import json, pathlib, hashlib, sys, collections
root = pathlib.Path(__file__).resolve().parents[2]
def hid(key, salt=''): return hashlib.sha1((salt + key).encode()).hexdigest()[:16].upper()
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
    q, ch = quests[k]; print(f"{k}\t{hid(k)}\t{q['title']}\t{ch}")
