#!/usr/bin/env python3
"""Validate FTB Quests SNBT files: parse, check item IDs against a whitelist, check dependency ids exist.
Usage: validate_quests.py <quests_dir> <ids.json>
"""
import sys, json, pathlib, re
import nbtlib
qdir, ids_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
ids = set(json.loads(ids_path.read_text())["items"]) if ids_path.exists() else set()
errors, warnings = [], []
quest_ids = set(); chapter_files = list((qdir / 'chapters').glob('*.snbt'))
parsed = {}
for f in chapter_files + list((qdir / 'reward_tables').glob('*.snbt')) + [p for p in [qdir/'data.snbt', qdir/'chapter_groups.snbt'] if p.exists()]:
    try:
        parsed[f] = nbtlib.parse_nbt(f.read_text())
    except Exception as e:
        errors.append(f"{f.name}: PARSE ERROR {e}")
for f in chapter_files:
    if f not in parsed: continue
    for q in parsed[f].get('quests', []):
        quest_ids.add(str(q.get('id')))
def walk(node, path, fname):
    if isinstance(node, dict):
        if 'item' in node:
            it = node['item']
            item_id = it['id'] if isinstance(it, dict) and 'id' in it else it
            item_id = str(item_id)
            if ids and item_id not in ids and not item_id.startswith('minecraft:'):
                errors.append(f"{fname}: unknown item id {item_id} at {path}")
        for k, v in node.items(): walk(v, f"{path}.{k}", fname)
    elif isinstance(node, list):
        for i, v in enumerate(node): walk(v, f"{path}[{i}]", fname)
for f in chapter_files:
    if f not in parsed: continue
    ch = parsed[f]
    entry = 0
    for q in ch.get('quests', []):
        deps = [str(d) for d in q.get('dependencies', [])]
        if not deps: entry += 1
        for d in deps:
            if d not in quest_ids: errors.append(f"{f.name}: quest {q.get('id')} depends on missing {d}")
        walk(q, f"quest[{q.get('id')}]", f.name)
    if entry > 1: warnings.append(f"{f.name}: {entry} quests have no dependencies (more than one entry point)")
    if entry == 0 and ch.get('quests'): errors.append(f"{f.name}: no entry quest (circular?)")
print(f"files: {len(parsed)}  quests: {len(quest_ids)}  errors: {len(errors)}  warnings: {len(warnings)}")
for e in errors: print("ERROR", e)
for w in warnings: print("WARN", w)
sys.exit(1 if errors else 0)
