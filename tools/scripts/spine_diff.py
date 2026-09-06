#!/usr/bin/env python3
"""spine_diff.py — prove a rewritten story chapter kept everything the engine depends on.

Usage: spine_diff.py <before_dir> <after_dir> [chapter keys...]
For every quest key present before: it must still exist (in ANY file after), with identical
"tasks", "deps", and every reward of type command/stage/loot identical and in the same order.
Exit 1 on any breach; prints each one.
"""
import sys, json, glob, os
before, after = sys.argv[1], sys.argv[2]
def load(d):
    out = {}
    for f in glob.glob(f'{d}/*.json'):
        for q in json.load(open(f))['quests']:
            out[q['key']] = (os.path.basename(f), q)
    return out
B, A = load(before), load(after)
FROZEN_REWARDS = ('command', 'stage', 'loot')
def frozen(q):
    return [r for r in q.get('rewards', []) if r.get('type') in FROZEN_REWARDS]
bad = 0
for k, (bf, bq) in B.items():
    if k not in A:
        print(f'MISSING   {k} (was in {bf})'); bad += 1; continue
    af, aq = A[k]
    for field in ('tasks', 'deps'):
        if json.dumps(bq.get(field, []), sort_keys=True) != json.dumps(aq.get(field, []), sort_keys=True):
            print(f'CHANGED   {k}.{field}  {bf} -> {af}\n   before {json.dumps(bq.get(field, []))[:200]}\n   after  {json.dumps(aq.get(field, []))[:200]}'); bad += 1
    if json.dumps(frozen(bq), sort_keys=True) != json.dumps(frozen(aq), sort_keys=True):
        print(f'CHANGED   {k}.rewards(command/stage/loot)  {bf} -> {af}'); bad += 1
    for field in ('min_required_deps', 'invisible', 'dependency_requirement', 'can_repeat'):
        if bq.get(field) != aq.get(field):
            print(f'CHANGED   {k}.{field}: {bq.get(field)} -> {aq.get(field)}'); bad += 1
    toasts = [r for r in aq.get('rewards', []) if r.get('type') == 'toast']
    if len(toasts) > 1: print(f'WARN      {k} has {len(toasts)} toast rewards'); 
print(f'{len(B)} keys checked, {bad} breaches')
sys.exit(1 if bad else 0)
