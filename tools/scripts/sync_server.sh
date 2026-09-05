#!/bin/zsh
# Sync the server folder from the pack. Removes the files the game itself rewrites (quest SNBT, KubeJS copies)
# first, so a pack update is never shadowed by the server's own re-saved copy.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
rm -rf "$ROOT/server/config/ftbquests/quests" "$ROOT/server/kubejs/server_scripts" "$ROOT/server/kubejs/startup_scripts" "$ROOT/server/kubejs/data/valley" "$ROOT/server/packwiz.json"
cd "$ROOT/server" && "$ROOT/tools/jdk17/Contents/Home/bin/java" -jar "$ROOT/tools/packwiz-installer-bootstrap.jar" -g -s server "${1:-$ROOT/pack/pack.toml}" 2>&1 | tail -1
ls "$ROOT/server/config/ftbquests/quests/chapters" | wc -l | xargs echo "quest chapters:"

# The shipped singleplayer world (pack/saves/Little Kettle Valley/, 55 MB) is indexed as plain
# files, and packwiz's index has no per-file `side` -- only metafiles carry one -- so `-s server`
# installs it here too. The server's world is server/world/; a copy under server/saves/ is dead
# weight and, worse, looks like a second world to anyone reading the folder. Drop it.
rm -rf "$ROOT/server/saves"

# ---------------------------------------------------------------------------
# ORPHAN SWEEP. This script deletes server/packwiz.json above -- that file is the
# installer's record of what IT put there, and without it the installer cannot remove
# anything, so a jar that leaves the pack stays in server/mods forever.
#
# One did: inventorysorter-1.20.1-23.1.9.jar, left behind by an older index. It registers a
# network channel, the client (which correctly did not have it) was handed a mod list it
# could not match, and every join was refused with "mismatched mod channel list" -- the
# server log's own words -- before a single quest ran.
#
# So: anything in server/mods that the index does not name is moved aside, not deleted, and
# printed. Moved rather than deleted because a jar somebody put there on purpose is a
# decision, and this script is not entitled to make it.
# ---------------------------------------------------------------------------
"$ROOT/tools/venv/bin/python" - "$ROOT" <<'PY'
import pathlib, sys, tomllib, shutil, time
root = pathlib.Path(sys.argv[1])
idx = tomllib.loads((root / 'pack' / 'index.toml').read_text())
want = set()
for f in idx['files']:
    p = f['file']
    if not p.startswith('mods/'):
        continue
    if p.endswith('.pw.toml'):
        want.add(tomllib.loads((root / 'pack' / p).read_text())['filename'])
    else:
        want.add(p.split('/')[-1])
have = sorted(p for p in (root / 'server' / 'mods').glob('*.jar'))
orphans = [p for p in have if p.name not in want]
if orphans:
    away = root / 'scratch' / ('orphan_mods_%s' % time.strftime('%Y%m%d_%H%M%S'))
    away.mkdir(parents=True, exist_ok=True)
    for p in orphans:
        shutil.move(str(p), str(away / p.name))
    print('orphan mods moved out of server/mods -> %s: %s'
          % (away, ', '.join(p.name for p in orphans)))
else:
    print('server/mods: no orphans (%d jars, all named by the index)' % len(have))
PY
