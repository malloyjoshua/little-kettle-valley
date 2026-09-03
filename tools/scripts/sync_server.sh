#!/bin/zsh
# Sync the server folder from the pack. Removes the files the game itself rewrites (quest SNBT, KubeJS copies)
# first, so a pack update is never shadowed by the server's own re-saved copy.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
rm -rf "$ROOT/server/config/ftbquests/quests" "$ROOT/server/kubejs/server_scripts" "$ROOT/server/kubejs/startup_scripts" "$ROOT/server/kubejs/data/valley" "$ROOT/server/packwiz.json"
cd "$ROOT/server" && "$ROOT/tools/jdk17/Contents/Home/bin/java" -jar "$ROOT/tools/packwiz-installer-bootstrap.jar" -g -s server "${1:-$ROOT/pack/pack.toml}" 2>&1 | tail -1
ls "$ROOT/server/config/ftbquests/quests/chapters" | wc -l | xargs echo "quest chapters:"
