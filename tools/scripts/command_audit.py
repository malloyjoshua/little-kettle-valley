#!/usr/bin/env python3
"""Emit every quest command reward and every datapack function line as console commands with test substitutions.
Usage: command_audit.py <player> > cmds.txt"""
import json, pathlib, re, sys, hashlib
root = pathlib.Path(__file__).resolve().parents[2]; player = sys.argv[1] if len(sys.argv) > 1 else 'packtester'
def hid(key, salt=''): return hashlib.sha1((salt + key).encode()).hexdigest()[:16].upper()
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
for f in sorted((root / 'pack/kubejs/data/valley/functions').rglob('*.mcfunction')):
    rel = f.relative_to(root / 'pack/kubejs/data/valley/functions').with_suffix('')
    for ln in f.read_text().split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        out.append(f'# fn {rel}\nexecute as {player} at {player} positioned ~8 ~ ~8 run {ln}')
print('\n'.join(out))
