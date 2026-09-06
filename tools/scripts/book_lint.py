#!/usr/bin/env python3
"""book_lint.py — mechanical proof-reading of the quest book (numbers, pointers, toasts, coordinates, keys).

Usage: book_lint.py <story/quests dir> [--sites pack/kubejs/data/valley/valley_sites.json] [--structures scratch/structures_near_spawn.json] [--options pack/options.txt]
Prints one line per finding; exit 1 if any ERROR.
"""
import sys, json, glob, re, os, argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('--sites', default='pack/kubejs/data/valley/valley_sites.json')
ap.add_argument('--structures', default='scratch/structures_near_spawn.json'); ap.add_argument('--options', default='pack/options.txt'); a = ap.parse_args()
Q = {}; CH = {}
for f in sorted(glob.glob(f'{a.src}/*.json')):
    d = json.load(open(f)); CH[d['chapter']['key']] = d['chapter']
    for q in d['quests']: q['_file'] = os.path.basename(f); Q[q['key']] = q
titles = {c['title'] for c in CH.values()}
dependents = collections.defaultdict(list)
for k, q in Q.items():
    for dep in q.get('deps', []): dependents[dep].append(k)
sites = json.load(open(a.sites)); structs = json.load(open(a.structures)) if os.path.exists(a.structures) else {}
coords = set()
def harvest(o):
    if isinstance(o, list) and len(o) in (2, 3, 6) and all(isinstance(x, (int, float)) for x in o):
        coords.add(tuple(int(x) for x in o))
        if len(o) == 6: coords.add((int(o[0]), int(o[1]), int(o[2]))); coords.add((int(o[3]), int(o[4]), int(o[5])))
    elif isinstance(o, dict):
        for v in o.values(): harvest(v)
    elif isinstance(o, list):
        for v in o: harvest(v)
harvest(sites)
for sid, lst in structs.items():
    for x, z, bb in lst: coords.add((x, z)); coords.add((x, 0, z))
xz = {(c[0], c[-1]) for c in coords} | {(c[0], c[2]) for c in coords if len(c) == 3}
opts = open(a.options).read() if os.path.exists(a.options) else ''
keybinds = dict(re.findall(r'^key_([\w.:]+):key\.keyboard\.(\w+)$', opts, re.M))
errors = warns = 0
def err(msg):
    global errors; errors += 1; print('ERROR', msg)
def warn(msg):
    global warns; warns += 1; print('WARN ', msg)
WORDNUM = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'twelve':12,'sixteen':16,'twenty':20,'twenty-four':24,'thirty-two':32,'sixty-four':64}
for k, q in Q.items():
    text = ' '.join([q.get('title', ''), q.get('subtitle', '')] + q.get('description', []) + [r.get('description', '') + ' ' + r.get('title', '') for r in q.get('rewards', []) if r.get('type') == 'toast'])
    # 1. bare ampersand / dev strings
    if re.search(r'\S & \S', text): err(f'{k} ({q["_file"]}): bare "&" in text')
    dm = re.search(r'\bStage [a-z_]+:|TODO|\bq\d{2}[a-z]?\b', text)
    if dm: warn(f'{k}: developer string in player text: {dm.group(0)}')
    # 2. chapter pointers
    for m in re.finditer(r'&6([^&]+?)&r', text):
        name = m.group(1).strip()
        if name not in titles and name not in ('Create', 'Thermal') and not any(name == t or name in t for t in titles):
            err(f'{k}: pointer to unknown chapter "{name}"')
    # 3. Next: toasts name a dependent
    for r in q.get('rewards', []):
        if r.get('type') == 'toast' and r.get('description', '').startswith('Next:'):
            deps_titles = [Q[d]['title'] for d in dependents.get(k, []) if d in Q]
            body = r['description'].lower()
            if dependents.get(k) and not any(any(w.lower() in body for w in t.split() if len(w) > 4) for t in deps_titles):
                warn(f'{k}: Next toast may not name a dependent ({", ".join(dependents[k])}): "{r["description"][:70]}"')
            if not dependents.get(k): warn(f'{k}: Next toast but nothing depends on this quest')
    # 4. coordinates in text exist
    for m in re.finditer(r'(-?\d{2,4})[ ,]+(-?\d{1,3})[ ,]+(-?\d{2,4})\b', text):
        x, y, z = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if (x, y, z) not in coords and (x, z) not in xz:
            near = any(abs(x - cx) <= 3 and abs(z - cz) <= 3 for cx, cz in xz)
            (warn if near else err)(f'{k}: coordinate {x} {y} {z} not in registry/structures')
    for m in re.finditer(r'\b(-?\d{3,4}),? (-?\d{2,4})\b(?![ ,]-?\d)', text):
        x, z = int(m.group(1)), int(m.group(2))
        if (x, z) not in xz and not any(abs(x - cx) <= 3 and abs(z - cz) <= 3 for cx, cz in xz): warn(f'{k}: 2D coordinate {x} {z} not in registry/structures')
    # 5. numbers in title vs task counts
    counts = {t.get('count', 1) for t in q.get('tasks', []) if t.get('type') == 'item'}
    for m in re.finditer(r'\b(\d{1,4})\b', q.get('title', '')):
        n = int(m.group(1))
        if counts and n not in counts and n not in (2, 3) and not re.search(r'\b(Act|Year|RPM|x)\b', q['title']):
            warn(f'{k}: title number {n} vs task counts {sorted(counts)}: "{q["title"]}"')
    # 6. keybind claims
    for m in re.finditer(r'[Pp]ress (?:&b)?([A-Z]|`)(?:&r)?', text):
        key = m.group(1)
        bound = key.lower() in ''.join(keybinds.values())
        if not bound: warn(f'{k}: claims key "{key}" which options.txt does not bind (mod default?)')
    # 7. structure tasks exist in the world scan
    for t in q.get('tasks', []):
        if t.get('type') == 'structure' and structs and not t['structure'].startswith('#') and t['structure'] not in structs:
            warn(f'{k}: structure task {t["structure"]} not in the world scan')
        if t.get('type') == 'location':
            x, y, z = t['pos']
            if not (-832 <= x <= 207 and -528 <= z <= 511): err(f'{k}: location task outside the pregen box: {t["pos"]}')
    if q.get('min_required_deps') and q['min_required_deps'] > len(q.get('deps', [])): err(f'{k}: min_required_deps > deps')
# 8. duplicate item tasks across chapters
seen = collections.defaultdict(list)
for k, q in Q.items():
    for t in q.get('tasks', []):
        if t.get('type') == 'item': seen[(t['item'], t.get('count', 1))].append(k)
for (it, n), ks in seen.items():
    files = {Q[k]['_file'] for k in ks}
    if len(files) > 1: warn(f'same task {n}x {it} in {", ".join(ks)}')
print(f'{errors} errors, {warns} warnings over {len(Q)} quests')
sys.exit(1 if errors else 0)
