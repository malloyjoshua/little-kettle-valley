#!/usr/bin/env python3
"""Compile story/quests/*.json into FTB Quests SNBT.
Usage: compile_quests.py <quests_json_dir> <ftbquests_quests_dir> <ids.json> [--strict]
Input JSON per chapter (see docs/QUEST_FORMAT.md). Output: chapters/<key>.snbt, reward_tables/<key>.snbt,
chapter_groups.snbt, data.snbt. IDs are deterministic (sha1 of key). Layout is automatic by dependency depth.
Validates every item id against ids.json and every dep against known quest keys. Exit 1 on any error."""
import sys, json, hashlib, pathlib, re, collections
src, out, ids_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
strict = '--strict' in sys.argv
IDS = set(json.loads(ids_path.read_text())['items'])
errors, warns = [], []
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
def q(s):  # SNBT string literal
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
def item_ok(item, where):
    if item not in IDS and not item.startswith('#'):
        (errors if strict else warns).append(f"{where}: unknown item {item}")
def snbt_item(item, count=None):
    return q(item)
def task_snbt(t, where, key):
    tid = hid(key + '/t/' + json.dumps(t, sort_keys=True))
    typ = t['type']; parts = [f'id: "{tid}"', f'type: "{typ}"']
    if 'title' in t: parts.append(f'title: {q(t["title"])}')
    if 'icon' in t: parts.append(f'icon: {q(t["icon"])}')
    if typ == 'item':
        item_ok(t['item'], where); parts.append(f'item: {q(t["item"])}'); parts.append(f'count: {int(t.get("count",1))}L')
        if t.get('consume'): parts.append('consume_items: true')
    elif typ == 'checkmark': pass
    elif typ == 'biome': parts.append(f'biome: {q(t["biome"])}')
    elif typ == 'dimension': parts.append(f'dimension: {q(t["dimension"])}')
    elif typ == 'advancement': parts.append(f'advancement: {q(t["advancement"])}'); parts.append(f'criterion: {q(t.get("criterion",""))}')
    elif typ == 'kill': parts.append(f'entity: {q(t["entity"])}'); parts.append(f'value: {int(t.get("count",1))}L')
    elif typ == 'observation':
        parts.append(f'to_observe: {q(t["block"])}'); parts.append(f'observe_type: {int(t.get("observe_type",0))}'); parts.append(f'timer: {int(t.get("timer",0))}L')
    elif typ == 'structure': parts.append(f'structure: {q(t["structure"])}')
    elif typ == 'stage': parts.append(f'stage: {q(t["stage"])}')
    elif typ == 'xp': parts.append(f'value: {int(t.get("levels",1))}L'); parts.append('points: false')
    elif typ == 'stat': parts.append(f'stat: {q(t["stat"])}'); parts.append(f'value: {int(t.get("count",1))}')
    elif typ == 'fluid': parts.append(f'fluid: {q(t["fluid"])}'); parts.append(f'amount: {int(t.get("mb",1000))}L')
    elif typ == 'energy': parts.append(f'value: {int(t.get("fe",1000))}L')
    elif typ == 'location':
        parts.append(f'dimension: {q(t.get("dimension","minecraft:overworld"))}'); parts.append(f'ignore_dimension: {str(t.get("ignore_dimension",False)).lower()}')
        p = t['pos']; parts.append(f'position: [I; {int(p[0])}, {int(p[1])}, {int(p[2])}]'); s = t.get('size',[8,8,8]); parts.append(f'size: [I; {int(s[0])}, {int(s[1])}, {int(s[2])}]')
    else: errors.append(f"{where}: unknown task type {typ}")
    return '{ ' + ', '.join(parts) + ' }'
def reward_snbt(r, where, key, tables):
    rid = hid(key + '/r/' + json.dumps(r, sort_keys=True))
    typ = r['type']; parts = [f'id: "{rid}"', f'type: "{typ}"']
    if 'title' in r: parts.append(f'title: {q(r["title"])}')
    if r.get('team'): parts.append('team_reward: true')
    if r.get('autoclaim'): parts.append(f'auto: {q(r["autoclaim"])}')
    if typ == 'item':
        item_ok(r['item'], where); parts.append(f'item: {q(r["item"])}')
        if int(r.get('count',1)) != 1: parts.append(f'count: {int(r["count"])}')
    elif typ == 'xp_levels': parts.append(f'xp_levels: {int(r.get("levels",1))}')
    elif typ == 'xp': parts.append(f'xp: {int(r.get("points",100))}')
    elif typ == 'command':
        parts.append(f'command: {q(r["command"])}')
        if r.get('elevate', True): parts.append('elevate_perms: true')
        if r.get('silent', True): parts.append('silent: true')
    elif typ == 'loot':
        tk = r['table']
        if tk not in tables: errors.append(f"{where}: unknown reward table {tk}")
        parts.append(f'table_id: {int(hid(tk, "table/"), 16)}L')
    elif typ == 'stage': parts.append(f'stage: {q(r["stage"])}')
    elif typ == 'toast': parts.append(f'description: {q(r.get("description",""))}')
    elif typ == 'advancement': parts.append(f'advancement: {q(r["advancement"])}'); parts.append(f'criterion: {q(r.get("criterion",""))}')
    else: errors.append(f"{where}: unknown reward type {typ}")
    return '{ ' + ', '.join(parts) + ' }'
def layout(quests):
    by = {qq['key']: qq for qq in quests}
    depth = {}
    def d(k, seen=()):
        if k in depth: return depth[k]
        if k in seen: errors.append(f"dependency cycle at {k}"); return 0
        qq = by[k]; deps = [x for x in qq.get('deps', []) if x in by]
        depth[k] = 0 if not deps else 1 + max(d(x, seen + (k,)) for x in deps)
        return depth[k]
    for qq in quests: d(qq['key'])
    cols = collections.defaultdict(list)
    for qq in quests: cols[depth[qq['key']]].append(qq)
    for col, items in cols.items():
        n = len(items)
        for i, qq in enumerate(items):
            qq['_x'] = col * 2.0; qq['_y'] = (i - (n - 1) / 2.0) * 1.5
    # Explicit x/y win over the automatic layout. Used by side boards like
    # Oda's Counter, where every quest sits at the same dependency depth and
    # the tiers are only legible if they are laid out as columns by hand.
    for qq in quests:
        if 'x' in qq: qq['_x'] = float(qq['x'])
        if 'y' in qq: qq['_y'] = float(qq['y'])
    return depth
(out / 'chapters').mkdir(parents=True, exist_ok=True); (out / 'reward_tables').mkdir(parents=True, exist_ok=True)
files = sorted(src.glob('*.json'))
all_keys = {}
chapters = []
tables = {}
for f in files:
    data = json.loads(f.read_text())
    for t in data.get('reward_tables', []): tables[t['key']] = t
    for qq in data['quests']:
        if qq['key'] in all_keys: errors.append(f"{f.name}: duplicate quest key {qq['key']}")
        all_keys[qq['key']] = f.name
    chapters.append((f, data))
groups = collections.OrderedDict()
for f, data in chapters:
    ch = data['chapter']; groups.setdefault(ch.get('group', 'Story'), hid(ch.get('group', 'Story'), 'group/'))
    quests = data['quests']; layout(quests)
    lines = []
    for qq in quests:
        where = f"{f.name}:{qq['key']}"
        deps = qq.get('deps', [])
        for dk in deps:
            if dk not in all_keys: errors.append(f"{where}: unknown dependency {dk}")
        parts = []
        parts.append(f'id: "{hid(qq["key"])}"')
        parts.append(f'title: {q(qq["title"])}')
        if qq.get('subtitle'): parts.append(f'subtitle: {q(qq["subtitle"])}')
        if qq.get('icon'): item_ok(qq['icon'], where + ' icon'); parts.append(f'icon: {q(qq["icon"])}')
        desc = qq.get('description', [])
        if isinstance(desc, str): desc = desc.split('\n')
        parts.append('description: [' + ', '.join(q(x) for x in desc) + ']')
        parts.append(f'x: {qq["_x"]:.1f}d'); parts.append(f'y: {qq["_y"]:.1f}d')
        if deps: parts.append('dependencies: [' + ', '.join(f'"{hid(dk)}"' for dk in deps) + ']')
        if qq.get('optional'): parts.append('optional: true')
        if qq.get('shape'): parts.append(f'shape: {q(qq["shape"])}')
        if qq.get('size'): parts.append(f'size: {float(qq["size"])}d')
        if qq.get('hide_until_deps_complete', True) and deps: parts.append('hide_until_deps_complete: true')
        if qq.get('hide_details_until_startable', True): parts.append('hide_details_until_startable: true')
        if qq.get('can_repeat'): parts.append('can_repeat: true')
        if qq.get('invisible'): parts.append('invisible: true')
        if qq.get('hide_dependency_lines'): parts.append('hide_dependency_lines: true')
        if qq.get('hide_dependent_lines'): parts.append('hide_dependent_lines: true')
        if qq.get('min_required_deps'): parts.append(f'min_required_dependencies: {int(qq["min_required_deps"])}')
        if qq.get('dependency_requirement'): parts.append(f'dependency_requirement: {q(qq["dependency_requirement"])}')
        if qq.get('guide_page'): parts.append(f'guide_page: {q(qq["guide_page"])}')
        parts.append('tasks: [' + ', '.join(task_snbt(t, where, qq['key']) for t in qq.get('tasks', [])) + ']')
        parts.append('rewards: [' + ', '.join(reward_snbt(r, where, qq['key'], tables) for r in qq.get('rewards', [])) + ']')
        lines.append('\t\t{\n\t\t\t' + '\n\t\t\t'.join(parts) + '\n\t\t}')
    sub = ch.get('subtitle', [])
    if isinstance(sub, str): sub = [sub]
    body = ['{', '\tdefault_hide_dependency_lines: false', '\tdefault_quest_shape: ""', f'\tfilename: {q(ch["key"])}',
            f'\tgroup: "{groups[ch.get("group","Story")]}"', f'\ticon: {q(ch.get("icon","minecraft:book"))}', f'\tid: "{hid(ch["key"], "chapter/")}"',
            f'\torder_index: {int(ch.get("order",0))}', '\tquest_links: [ ]']
    if sub: body.append('\tsubtitle: [' + ', '.join(q(x) for x in sub) + ']')
    if ch.get('always_invisible'): body.append('\talways_invisible: true')
    if ch.get('hide_quest_until_deps_complete', False): body.append('\thide_quest_until_deps_complete: true')
    if ch.get('progression_mode'): body.append(f'\tprogression_mode: {q(ch["progression_mode"])}')
    body.append('\tquests: [\n' + '\n'.join(lines) + '\n\t]')
    body.append(f'\ttitle: {q(ch["title"])}'); body.append('}')
    (out / 'chapters' / f'{ch["key"]}.snbt').write_text('\n'.join(body) + '\n')
for tk, t in tables.items():
    rs = []
    for r in t['rewards']:
        item_ok(r['item'], f'table {tk}')
        rs.append('\t\t{ item: ' + q(r['item']) + (f', count: {int(r["count"])}' if int(r.get('count',1)) != 1 else '') + f', weight: {float(r.get("weight",1))}f }}')
    body = ['{', f'\tempty_weight: {float(t.get("empty_weight",0))}f', f'\tid: "{hid(tk, "table/")}"', f'\tloot_size: {int(t.get("loot_size",1))}', f'\torder_index: {int(t.get("order",0))}',
            f'\ttitle: {q(t["title"])}', '\tuse_title: true', '\trewards: [\n' + '\n'.join(rs) + '\n\t]']
    if t.get('loot_crate'):
        lc = t['loot_crate']; body.append('\tloot_crate: { string_id: ' + q(lc.get('id', tk)) + f', item_name: {q(lc.get("name", t["title"]))}, color: {int(lc.get("color", 0xFFAA00))}, glow: {str(lc.get("glow", False)).lower()}, drops: {{ passive: 0, monster: 0, boss: 0 }} }}')
    body.append('}')
    (out / 'reward_tables' / f'{tk}.snbt').write_text('\n'.join(body) + '\n')
(out / 'chapter_groups.snbt').write_text('{\n\tchapter_groups: [\n' + '\n'.join(f'\t\t{{ id: "{gid}", title: {q(g)} }}' for g, gid in groups.items()) + '\n\t]\n}\n')
data_file = out / 'data.snbt'
if not data_file.exists():
    data_file.write_text('{\n\tdefault_hide_dependency_lines: false\n\tdefault_quest_shape: ""\n\tfilename: "cozytech"\n\tlock_message: "Not yet. Finish the quest before this one."\n\tprogression_mode: "flexible"\n\ttitle: "Little Kettle Valley"\n\tversion: 13\n}\n')
# purge stale chapter/table files not produced this run
keep_ch = {ch['key'] for _, d in chapters for ch in [d['chapter']]}
for p in (out / 'chapters').glob('*.snbt'):
    if p.stem not in keep_ch: p.unlink(); print(f"removed stale chapter {p.name}")
for p in (out / 'reward_tables').glob('*.snbt'):
    if p.stem not in tables: p.unlink(); print(f"removed stale table {p.name}")
idmap = pathlib.Path('pack/kubejs/server_scripts/_quest_ids.js')
idmap.parent.mkdir(parents=True, exist_ok=True)
idmap.write_text('// GENERATED by compile_quests.py. Do not edit. Quest key -> FTB Quests id.\nglobal.valleyQuestIds = ' + json.dumps({k: hid(k) for k in all_keys}, indent=1) + '\nglobal.valleyChapterIds = ' + json.dumps({d['chapter']['key']: hid(d['chapter']['key'], 'chapter/') for _, d in chapters}, indent=1) + '\n')
print(f"chapters: {len(chapters)}  quests: {len(all_keys)}  tables: {len(tables)}  errors: {len(errors)}  warnings: {len(warns)}")
for e in errors: print("ERROR", e)
for w in warns[:40]: print("WARN", w)
sys.exit(1 if errors else 0)
