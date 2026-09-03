#!/usr/bin/env python3
"""Extract every item and block registry ID from the lang files inside mod jars.
Usage: extract_ids.py <mods_dir> <out.json>
Output: {"items": [...], "blocks": [...], "by_mod": {modid: {"items": [...], "blocks": [...]}}}
"""
import sys, json, zipfile, re, pathlib
mods_dir, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
items, blocks, by_mod = set(), set(), {}
pat = re.compile(r'^(item|block)\.([a-z0-9_]+)\.([a-z0-9_./]+)$')
for jar in sorted(mods_dir.glob('*.jar')):
    try:
        z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile:
        continue
    for n in z.namelist():
        if n.startswith('assets/') and n.endswith('/lang/en_us.json'):
            try:
                data = json.loads(z.read(n).decode('utf-8', 'ignore'))
            except Exception:
                continue
            for key in data:
                m = pat.match(key)
                if not m:
                    continue
                kind, modid, name = m.groups()
                # skip tooltip/desc sub keys like item.x.y.desc
                if '.' in name:
                    continue
                rid = f"{modid}:{name}"
                by_mod.setdefault(modid, {"items": set(), "blocks": set()})
                if kind == 'item':
                    items.add(rid); by_mod[modid]["items"].add(rid)
                else:
                    blocks.add(rid); by_mod[modid]["blocks"].add(rid)
# blocks are almost always also items (block items)
all_items = items | blocks
res = {"items": sorted(all_items), "blocks": sorted(blocks),
       "by_mod": {k: {"items": sorted(v["items"] | v["blocks"]), "blocks": sorted(v["blocks"])} for k, v in by_mod.items()}}
out.write_text(json.dumps(res, indent=1))
print(f"{len(all_items)} item ids, {len(blocks)} block ids, {len(by_mod)} mods -> {out}")
