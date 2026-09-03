#!/usr/bin/env python3
"""Extract item/block registry IDs from mod jars using lang keys AND model filenames.
Usage: extract_ids.py <mods_dir> <out.json>"""
import sys, json, zipfile, re, pathlib
mods_dir, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
items, blocks, by_mod = set(), set(), {}
langpat = re.compile(r'^(item|block)\.([a-z0-9_]+)\.([a-z0-9_/]+)$')
modelpat = re.compile(r'^assets/([a-z0-9_]+)/models/(item|block)/([a-z0-9_/]+)\.json$')
def add(kind, ns, name):
    rid = f"{ns}:{name}"
    d = by_mod.setdefault(ns, {"items": set(), "blocks": set()})
    if kind == 'item': items.add(rid); d["items"].add(rid)
    else: blocks.add(rid); d["blocks"].add(rid)
for jar in sorted(mods_dir.glob('*.jar')):
    try: z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile: continue
    for n in z.namelist():
        m = modelpat.match(n)
        if m:
            ns, kind, name = m.groups()
            if kind == 'item' and '/' not in name: add('item', ns, name)
            elif kind == 'block' and '/' not in name and not re.search(r'_(top|bottom|side|inventory|on|off|open|closed|lit|active|inner|outer|post|wall|stage\d+|age\d+|\d+)$', name):
                add('block', ns, name)
            continue
        if n.startswith('assets/') and n.endswith('/lang/en_us.json'):
            try: data = json.loads(z.read(n).decode('utf-8', 'ignore'))
            except Exception: continue
            for key in data:
                m = langpat.match(key)
                if m:
                    kind, ns, name = m.groups()
                    if '.' not in name and '/' not in name: add(kind, ns, name)
all_items = items | blocks
res = {"items": sorted(all_items), "blocks": sorted(blocks),
       "by_mod": {k: {"items": sorted(v["items"] | v["blocks"]), "blocks": sorted(v["blocks"])} for k, v in by_mod.items()}}
out.write_text(json.dumps(res, indent=1))
print(f"{len(all_items)} item ids, {len(blocks)} block ids, {len(by_mod)} namespaces -> {out}")
