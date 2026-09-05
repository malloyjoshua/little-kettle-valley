#!/usr/bin/env python3
"""Validate a quest-source folder before compiling it.

Usage: check_quests.py <quests_json_dir> <ids.json>

Asserts, with no side effects and no writes:
  * every file is valid JSON with a chapter object and a quests list
  * every quest key is unique across all files
  * every dep names a known quest key, and no dep cycles exist
  * every item id (task items, reward items, quest icons, chapter icons,
    reward-table items) is present in ids.json
  * every structure task is either a "#tag" or a namespaced id
  * writing caps: title <= 45, subtitle <= 50, description <= 2 lines and
    <= 180 characters (warnings, not errors)
  * no gaming-register words in player-facing text (warning)
Exit 1 if any error was found.
"""
import sys, json, pathlib, collections, re

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)

src = pathlib.Path(sys.argv[1])
IDS = set(json.loads(pathlib.Path(sys.argv[2]).read_text())['items'])

errors, warns = [], []
# Gaming register, per docs/writing-craft.md §3. 'grind' is not listed: a Millstone
# and a Pulverizer literally grind, so only the player-facing noun forms are banned.
BANNED = ('unlock', 'unlocks', 'unlocked', 'tier', 'tiers', 'grindy',
          'the grind', 'progression', 'endgame')


def item_ok(item, where):
    if not isinstance(item, str):
        errors.append(f"{where}: item is not a string: {item!r}")
    elif not item.startswith('#') and item not in IDS:
        errors.append(f"{where}: unknown item id {item}")


def text_checks(qq, where):
    t = qq.get('title', '')
    if len(t) > 45:
        warns.append(f"{where}: title {len(t)} chars (cap 45): {t}")
    s = qq.get('subtitle', '')
    if len(s) > 50:
        warns.append(f"{where}: subtitle {len(s)} chars (cap 50): {s}")
    d = qq.get('description', [])
    if isinstance(d, str):
        d = d.split('\n')
    body = [x for x in d if x.strip()]
    if len(body) > 2:
        warns.append(f"{where}: description {len(body)} lines (cap 2)")
    n = sum(len(x) for x in d)
    # A multiblock build quest has to name its exact block counts, which is worth
    # more than the cap. Those quests opt out with "long_description": true.
    cap = 300 if qq.get('long_description') else 180
    if n > cap:
        warns.append(f"{where}: description {n} chars (cap {cap})")
    blob = ' '.join([t, s] + list(d)).lower()
    for b in BANNED:
        if re.search(r'\b' + re.escape(b.strip()) + r'\b', blob):
            warns.append(f"{where}: banned word {b.strip()!r}")


quests = {}
chapters = []
tables = {}
for f in sorted(src.glob('*.json')):
    try:
        data = json.loads(f.read_text())
    except Exception as e:
        errors.append(f"{f.name}: invalid JSON: {e}")
        continue
    ch = data.get('chapter')
    if not isinstance(ch, dict) or 'key' not in ch or 'title' not in ch:
        errors.append(f"{f.name}: missing or malformed chapter object")
        continue
    chapters.append((f.name, ch))
    if ch.get('icon'):
        item_ok(ch['icon'], f"{f.name}: chapter icon")
    for t in data.get('reward_tables', []):
        tables[t['key']] = t
        for r in t.get('rewards', []):
            item_ok(r['item'], f"{f.name}: table {t['key']}")
    for qq in data.get('quests', []):
        key = qq.get('key')
        where = f"{f.name}:{key}"
        if not key:
            errors.append(f"{f.name}: quest with no key")
            continue
        if key in quests:
            errors.append(f"{where}: duplicate quest key (also in {quests[key][0]})")
        quests[key] = (f.name, qq)
        if qq.get('icon'):
            item_ok(qq['icon'], where + ' icon')
        if not qq.get('tasks'):
            errors.append(f"{where}: no tasks")
        for t in qq.get('tasks', []):
            typ = t.get('type')
            if typ == 'item':
                item_ok(t.get('item'), where + ' task')
            elif typ == 'structure':
                s = t.get('structure', '')
                if not (s.startswith('#') or ':' in s):
                    errors.append(f"{where}: structure {s!r} is not a tag or a namespaced id")
            elif typ in ('biome', 'dimension'):
                if ':' not in t.get(typ, ''):
                    errors.append(f"{where}: {typ} {t.get(typ)!r} is not namespaced")
            elif typ == 'advancement':
                if ':' not in t.get('advancement', ''):
                    errors.append(f"{where}: advancement not namespaced")
            elif typ not in ('checkmark', 'kill', 'observation', 'stage', 'xp',
                             'stat', 'fluid', 'energy', 'location'):
                errors.append(f"{where}: unknown task type {typ}")
        for r in qq.get('rewards', []):
            if r.get('type') == 'item':
                item_ok(r.get('item'), where + ' reward')
            if r.get('type') == 'loot' and r.get('table') not in tables:
                errors.append(f"{where}: reward table {r.get('table')} not defined")
            a = r.get('autoclaim')
            if a is not None and a not in ('default', 'disabled', 'enabled', 'no_toast', 'invisible'):
                errors.append(f"{where}: bad autoclaim {a!r}")
        text_checks(qq, where)

for key, (fn, qq) in quests.items():
    for dk in qq.get('deps', []):
        if dk not in quests:
            errors.append(f"{fn}:{key}: unknown dependency {dk}")

# cycle detection
state = {}
def walk(k, stack):
    if state.get(k) == 'done':
        return
    if state.get(k) == 'open':
        errors.append(f"dependency cycle: {' -> '.join(stack + [k])}")
        return
    state[k] = 'open'
    for dk in quests[k][1].get('deps', []):
        if dk in quests:
            walk(dk, stack + [k])
    state[k] = 'done'
for k in quests:
    walk(k, [])

# one entry quest per chapter
by_chapter = collections.defaultdict(list)
for key, (fn, qq) in quests.items():
    by_chapter[fn].append(qq)
for fn, qs in sorted(by_chapter.items()):
    roots = [q['key'] for q in qs if not q.get('deps')]
    if not roots:
        errors.append(f"{fn}: no entry quest (every quest has a dependency)")
    elif len(roots) > 1 and fn != 'readme.json':
        warns.append(f"{fn}: {len(roots)} entry quests: {', '.join(roots)}")

orders = [(ch['order'], ch['key'], fn) for fn, ch in chapters if 'order' in ch]
dupes = [o for o, c in collections.Counter(o for o, _, _ in orders).items() if c > 1]
if dupes:
    errors.append(f"duplicate chapter order values: {dupes}")

print(f"files: {len(chapters)}  quests: {len(quests)}  errors: {len(errors)}  warnings: {len(warns)}")
for fn, ch in chapters:
    n = len(by_chapter[fn])
    print(f"  {ch['order']:>2}  {ch['group']:<12} {ch['title']:<24} {n:>3} quests  ({fn})")
for e in errors:
    print("ERROR", e)
for w in warns:
    print("WARN ", w)
sys.exit(1 if errors else 0)
