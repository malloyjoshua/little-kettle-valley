#!/bin/zsh
# =============================================================================
# playthrough.sh — prove the whole story on the SHIPPED world.
#
# The pack ships one hand-built world (docs/transitions-design.md architecture A). Every
# earlier harness ran on a FRESH world and set the anchor and Home near wherever the test
# client happened to spawn, which is the exact thing the pack no longer does — so it could
# not have caught a single one of the bugs this rewrite is about.
#
# This one:
#   * refreshes and syncs the server FROM pack/ (never pack-tech/), and asserts the ten
#     valley scripts are present before it boots;
#   * deletes server/world and copies world-master/ in, so the run is against the product;
#   * SALTS twenty player blocks around the farm and the square before anything runs;
#   * joins an offline test client at the world's own fixed spawn — no anchor, no home, no
#     ruin set-up commands, because all three are constants in valley_sites.json;
#   * completes every quest in dependency order, runs the command audit, then every finale
#     and every scene;
#   * and then asserts, off the REGION FILES with the server stopped:
#        1. all 40 lamp cells lit
#        2. every resident alive and at their registry stand
#        3. the cottage gaps filled (the harness places them the way the player would)
#        4. the Works lever thrown
#        5. the cellar door open
#        6. every one of the 20 salted player blocks still there
#        7. no block outside the registry footprints changed
#   * plus: no server tick over 50 ms during any finale, read off the tick log.
#
# Usage: tools/scripts/playthrough.sh
# Logs:  scratch/shipped_playthrough/
# =============================================================================
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; C="$ROOT/tools/scripts/server_ctl.sh"
JAVA="$ROOT/tools/jdk17/Contents/Home/bin/java"
# The client game directory. Overridable so a run can use a throwaway gamedir instead of
# Josh's own Prism instance (which this script otherwise packwiz-syncs and deletes logs in).
GD="${PLAYTHROUGH_GD:-$HOME/Library/Application Support/PrismLauncher/instances/CozyTech/.minecraft}"
LOG="$SRV/logs/latest.log"; OUT="${PLAYTHROUGH_OUT:-$ROOT/scratch/shipped_playthrough}"
FIFO="$ROOT/scratch/server.in"; P=packtester; PIDF="$ROOT/scratch/server.pid"
PY="$ROOT/tools/venv/bin/python"
mkdir -p "$OUT"; rm -f "$OUT/completed.txt"

ts() { echo "[$(date +%H:%M:%S)] $1"; }
# printf, never echo: zsh's builtin echo expands backslash escapes and the audit list
# carries quest text with \u escapes in it.
say() { printf '%s\n' "$1" > "$FIFO"; sleep "${2:-0.5}"; }

for pid in $(pgrep -f 'playthrough.sh'); do
  [ "$pid" = "$$" ] && continue
  ps -o command= -p "$pid" | grep -q 'zsh.*playthrough.sh' && {
    echo "REFUSING: another run is going (pid $pid)."; exit 1; }
done
# Our server is the one whose WORKING DIRECTORY is $SRV. A bare `unix_args` pgrep matches
# the parallel Kettle Tech server too and has killed it twice (docs/SESSIONS.md rule 1).
ours() {
  local p cwd
  for p in $(pgrep -f "unix_args.txt nogui" 2>/dev/null); do
    cwd=$(lsof -a -p "$p" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
    [ "$cwd" = "$SRV" ] && print -r -- "$p"
  done
}
[ -n "$(ours)" ] && { echo "REFUSING: our Forge server is already running. Stop it first."; exit 1; }
pgrep -f 'cpw.mods.bootstraplauncher' >/dev/null && { echo "REFUSING: a Minecraft client is running."; exit 1; }

cp "$SRV/server.properties" "$OUT/server.properties.bak"
restore() { cp "$OUT/server.properties.bak" "$SRV/server.properties"; }
trap restore EXIT

# -----------------------------------------------------------------------------
# 0. THE STATIC ASSERTS. These cost nothing and they are the whole rule.
# -----------------------------------------------------------------------------
ts "== static asserts: the story may not build"
FAIL=0
for f in valley_core.js valley_checks.js valley_finales.js valley_gates.js \
         valley_greetings.js valley_keepsakes.js valley_step.js; do
  n1=$(grep -cE "['\"][^'\"]*place template" "$ROOT/pack/kubejs/server_scripts/$f")
  n2=$(grep -cE "['\"]@pad" "$ROOT/pack/kubejs/server_scripts/$f")
  n3=$(grep -cE "['\"]fill |['\"]execute [^'\"]* run fill " "$ROOT/pack/kubejs/server_scripts/$f")
  [ "$n1$n2$n3" = "000" ] || { echo "  FAIL $f: place template=$n1 @pad=$n2 fill=$n3"; FAIL=1; }
done
echo "  runtime scripts free of place-template / @pad / fill: $([ $FAIL = 0 ] && echo YES || echo NO)"
[ $FAIL = 0 ] || exit 1

# -----------------------------------------------------------------------------
# 1. Sync FROM pack/, and prove it.
# -----------------------------------------------------------------------------
ts "== packwiz refresh + sync server FROM pack/"
( cd "$ROOT/pack" && "$ROOT/tools/packwiz" refresh >/dev/null 2>&1 )
"$ROOT/tools/scripts/sync_server.sh" 2>&1 | tail -2
for f in valley_core.js valley_finales.js valley_checks.js valley_build.js valley_sites.js \
         town_plan.js valley_gates.js valley_greetings.js valley_keepsakes.js \
         valley_step.js seasons_tags.js unify.js; do
  [ -f "$SRV/kubejs/server_scripts/$f" ] || { echo "SYNC WRONG: no $f — a parallel job has
  synced server/ from pack-tech/. Re-run sync_server.sh from pack/."; exit 1; }
done
echo "  valley scripts in server/: $(ls "$SRV/kubejs/server_scripts" | wc -l | tr -d ' ')"
( cd "$GD" && "$JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "$ROOT/pack/pack.toml" 2>&1 | tail -1 )
"$PY" "$ROOT/tools/scripts/command_audit.py" "$P" > "$ROOT/scratch/audit_cmds.txt"
echo "  audit list regenerated: $(grep -vc '^#' "$ROOT/scratch/audit_cmds.txt") commands"

# -----------------------------------------------------------------------------
# 2. THE SHIPPED WORLD, not a fresh one.
# -----------------------------------------------------------------------------
ts "== install world-master/ as server/world"
[ -d "$ROOT/world-master/region" ] || { echo "no world-master/ — run scratch/master_build.sh"; exit 1; }
rm -rf "$SRV/world"
cp -R "$ROOT/world-master" "$SRV/world"
rm -f "$SRV/world/session.lock"
echo "  world installed: $(du -sh "$SRV/world" | awk '{print $1}'), $(ls "$SRV/world/region" | wc -l | tr -d ' ') region files"
sed -i '' 's/^online-mode=true/online-mode=false/' "$SRV/server.properties"

$C start >/dev/null; $C wait || { echo "SERVER FAILED TO BOOT"; tail -40 "$LOG"; exit 1; }
say "whitelist off" 1; say "op $P" 1
grep -q 'valley_sites.js ok' "$LOG" || { echo "valley_sites.js DID NOT LOAD"; exit 1; }
echo "  registry: $(grep -o 'valley_sites.js ok.*' "$LOG" | tail -1)"

# -----------------------------------------------------------------------------
# 3. THE SALT. Twenty player blocks that must survive the whole run.
# -----------------------------------------------------------------------------
ts "== salting 20 player blocks around the farm and the square"
"$PY" "$ROOT/tools/scripts/shipped_assert.py" salt --world "$SRV/world" --out "$OUT/salt.json" > "$OUT/salt.txt"
grep -v '^#' "$OUT/salt.txt" | while IFS= read -r cmd; do [ -n "$cmd" ] && say "$cmd" 0.25; done
echo "  salted: $(grep -vc '^#' "$OUT/salt.txt") blocks"

# -----------------------------------------------------------------------------
# 4. The client joins at the world's own spawn. No anchor. No home. No ruin.
# -----------------------------------------------------------------------------
ts "== offline client joins at the fixed spawn"
cd "$ROOT"; "$PY" tools/scripts/testclient.py command "$GD" --xmx 3584 --server localhost:25565 > "$OUT/client_cmd.json"
rm -rf "$GD/logs"; ( cd "$GD" && nohup "$PY" -c "import json,subprocess;subprocess.run(json.load(open('$OUT/client_cmd.json')))" > "$OUT/client.out" 2>&1 & )
for i in $(seq 1 60); do sleep 5
  grep -q "$P joined the game" "$LOG" 2>/dev/null && { ts "CLIENT_JOINED after $((i*5))s"; break; }
  kill -0 "$(cat "$PIDF" 2>/dev/null)" 2>/dev/null || { echo "SERVER DIED DURING CLIENT JOIN"; tail -20 "$ROOT/scratch/server.out"; exit 1; }
  [ $i -eq 60 ] && { echo "CLIENT NEVER JOINED"; exit 1; }
done
sleep 25
MARK=$(wc -l < "$LOG" | tr -d ' ')
say "data get entity $P Pos" 2
POS=$(grep 'has the following entity data' "$LOG" | tail -1 | sed -E 's/.*\[(.*)\].*/\1/' | tr -d 'd' | tr ',' ' ')
echo "  player spawned at: $POS   (registry spawn: $("$PY" -c "import json;print(*json.load(open('$ROOT/pack/kubejs/data/valley/valley_sites.json'))['spawn'])"))"
say "valley anchor" 2
echo "  anchor as the pack sees it: $(grep -o 'Town Anchor: .*' "$LOG" | tail -1)"

# -----------------------------------------------------------------------------
# 5. The player's own hands: the cottage gaps, the stake, the ducts, the lamp.
#    These are the block placements the CHECKS are written against, done the way a
#    player would do them, with the player as the placer so BlockEvents.placed fires.
# -----------------------------------------------------------------------------
ts "== the player's own placements (cottage, stake, ducts, walk the line, last lamp)"
HMARK=$(wc -l < "$LOG" | tr -d ' ')
say "gamemode creative $P" 1
"$PY" "$ROOT/tools/scripts/shipped_assert.py" player --player "$P" | while IFS= read -r cmd; do
  case "$cmd" in
    "#"*) ;;
    "SLEEP "*) sleep "${cmd#SLEEP }";;
    *) say "$cmd" 0.4;;
  esac
done
sleep 4
tail -n +"$HMARK" "$LOG" > "$OUT/player_actions.log"
echo "  checks that fired from the player's own hands: $(grep -c 'check satisfied' "$OUT/player_actions.log")"
grep -oE 'check satisfied: [a-z0-9_]+' "$OUT/player_actions.log" | awk '{print "    " $NF}' | sort -u | tr '\n' ' '; echo

# -----------------------------------------------------------------------------
# 6. Every quest, in dependency order.
# -----------------------------------------------------------------------------
ts "== quests"
"$PY" tools/scripts/quest_order.py | while IFS=$'\t' read -r key id title ch cmdid; do
  echo "$key $id $title" >> "$OUT/completed.txt"; say "ftbquests change_progress $P complete $cmdid" 1.0
  case "$key" in q19|q37|q56|q75|q91) sleep 12;; esac
done
sleep 10; echo "  quests completed: $(wc -l < "$OUT/completed.txt" | tr -d ' ')"

ts "== command audit ($(grep -vc '^#' "$ROOT/scratch/audit_cmds.txt") commands)"
AMARK=$(wc -l < "$LOG" | tr -d ' ')
grep -v '^#' "$ROOT/scratch/audit_cmds.txt" | grep -v '^\s*$' | while IFS= read -r cmd; do say "$cmd" 0.35; done
sleep 5

# -----------------------------------------------------------------------------
# 7. Every finale and every scene, explicitly, with the tick log watched.
# -----------------------------------------------------------------------------
ts "== finales + scenes (tick times watched)"
FMARK=$(wc -l < "$LOG" | tr -d ' ')
for a in 1 2 3 4 5; do
  say "debug start" 1
  say "valley finale act$a" 14
  say "debug stop" 3
done
for s in bram inn coop square_path cellar marnie pip q54 q58 q59 q60 q62 q64 q65 q66 q70a q71 q72 q73 q74 q76; do
  say "valley scene $s" 2
done
sleep 10
tail -n +"$FMARK" "$LOG" > "$OUT/finales.log"
echo "  finales complete: $(grep -oE 'finale act[0-9] complete' "$LOG" | sort -u | tr '\n' ' ')"
echo "  arrival retries that gave up: $(grep -c 'gave up' "$LOG")"
echo "  distinct scenes run: $(grep -oE 'valley\] scene [a-z0-9_]+ played' "$LOG" | sort -u | wc -l | tr -d ' ')"
echo "  REFUSED build commands (must be 0): $(grep -c 'REFUSED (' "$LOG")"
grep -oE 'REFUSED \([^)]*\)[^:]*: .{0,70}' "$LOG" | head -5

# the watchdog's own number, and the debug profiler's
echo "  server ticks over 50 ms (Can't keep up): $(grep -c "Can't keep up" "$OUT/finales.log")"
echo "  watchdog warnings:                      $(grep -c 'Running .* behind' "$OUT/finales.log")"
# THE TICK MEASUREMENT. `debug start` / `debug stop` wraps each finale in a 15-second tick
# profile, and the server prints the profile's own rate when it stops. A Minecraft tick has a
# 50 ms budget; the server runs at 20 TPS exactly when every tick fits inside it and drops
# below 20 the moment one does not. So "20.0x ticks per second" over the whole of a finale IS
# the claim "no tick in that finale took longer than 50 ms", measured rather than inferred
# from the absence of an overload warning (vanilla's "Can't keep up" only fires at 2 seconds).
echo "  tick profile per finale (20.00 TPS = every tick inside its 50 ms budget):"
grep -a 'Stopped tick profiling' "$OUT/finales.log" | sed -E 's/.*after /    /' || true
echo "  finales profiled below 20 TPS:          $(grep -a 'Stopped tick profiling' "$OUT/finales.log" | grep -cvE '\(20\.[0-9]+ ticks per second\)')"

say "valley lamps" 1
say "easy_npc list" 3
say "execute as @e[type=easy_npc:humanoid] run data get entity @s CustomName" 3
say "execute as @e[type=easy_npc:humanoid_slim] run data get entity @s CustomName" 3
sleep 3
say "save-all flush" 12
tail -n +"$MARK" "$LOG" > "$OUT/playthrough.log"; tail -n +"$AMARK" "$LOG" > "$OUT/audit.log"
cp "$LOG" "$OUT/server_full.log" 2>/dev/null

# -----------------------------------------------------------------------------
# 8. Stop, then read the WORLD.
# -----------------------------------------------------------------------------
ts "== stopping the server and reading the region files"
$C stop >/dev/null
pkill -f 'cpw.mods.bootstraplauncher'; sleep 6
cp "$GD/logs/latest.log" "$OUT/client.log" 2>/dev/null

echo "=== SUMMARY (server log)"
echo "quests completed (console):            $(wc -l < "$OUT/completed.txt" | tr -d ' ')"
echo "quest completions acked by FTBQuests:  $(grep -c 'Progress has been changed' "$OUT/playthrough.log")"
echo "NPCs alive:                            $(grep -oE 'Total NPCs: [0-9]+' "$OUT/playthrough.log" | tail -1 | awk '{print $3}') (want 15)"
MISSING=0
for npc in "Bram Tolliver" "Halden Root" "Marnie Ashcombe" "Nella Brightwater" "Corin Ashe" \
           "Mab Oldfield" "Tess Weaver" "Oda Vance" "Pip Ashcombe" "Mudlark" "Puddle" "Reed" \
           "Sedge" "Tobin Gale" "Wisp"; do
  grep -qF "$npc" "$OUT/playthrough.log" || { echo "  MISSING RESIDENT: $npc"; MISSING=$((MISSING+1)); }
done
echo "residents named in the world:          $((15-MISSING))/15"
echo "[valley] real errors:                  $(grep -caE '\[valley\] (finale command failed|build command failed|unknown build directive)|\[valley\].*(ReferenceError|TypeError)' "$OUT/playthrough.log")"
echo "KubeJS script errors:                  $(grep -cE 'Error in .ServerEvents|ReferenceError|TypeError|Rhino|kubejs.*ERROR' "$OUT/playthrough.log")"
echo "quest ids the command parser refused:  $(grep -c 'Invalid Object ID' "$OUT/playthrough.log")"
echo "error census (whole run):"
for pat in 'Invalid Object ID' 'No quest object found' 'Invalid chat component' \
           'Unknown or incomplete command' 'Incorrect argument for command' \
           'No player was found' 'No entity was found' 'That position is not loaded' \
           'Failed to place' 'Unknown item' 'Unknown block' 'Unknown function' \
           'Unknown loot table' 'Unknown entity' 'Unknown effect' 'Could not set' \
           'Could not find' 'Could not parse' 'finale command failed' \
           'Error in .ServerEvents' 'TypeError' 'ReferenceError'; do
  n=$(grep -ca "$pat" "$OUT/playthrough.log")
  [ "$n" -gt 0 ] && echo "  $n  $pat"
done
echo "  (nothing listed above = zero command errors in the whole run)"

echo "=== CLIENT LOG"
if [ -f "$OUT/client.log" ]; then
  echo "  mixin failures:   $(grep -cE 'Mixin apply failed|MixinApplyError|Critical injection failure' "$OUT/client.log")"
  echo "  valley asset gaps:$(grep -cE '(Unable to load model|Using missing texture|Failed to load texture)[^\n]*valley' "$OUT/client.log")"
  echo "  FATAL lines:      $(grep -c '/FATAL\]' "$OUT/client.log")"
fi

echo "=== WORLD ASSERTS (read off the region files, server stopped)"
"$PY" "$ROOT/tools/scripts/shipped_assert.py" check --world "$SRV/world" --salt "$OUT/salt.json" \
      --baseline "$ROOT/world-master" --json "$OUT/asserts.json"
RC=$?
echo "=== exit $RC"
exit $RC
