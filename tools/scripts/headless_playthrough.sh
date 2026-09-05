#!/bin/zsh
# =============================================================================
# headless_playthrough.sh — run the whole story on the shipped world with NO CLIENT.
#
# tools/scripts/playthrough.sh is the full harness and it needs a Minecraft client: it
# joins an offline player at the world spawn and makes the cottage placements with a
# player's own hands, because BlockEvents.placed is what half the checks listen for. That
# run cannot happen while Josh is at the Mac.
#
# This one is the half that can. Everything here is issued by the SERVER CONSOLE, which is
# the same source every finale and every scene already runs its own commands from — so the
# acts, the scenes, the arrivals, the lamp sweep, the doors, the lever and the residents are
# all exercised for real. What it cannot do:
#
#   * the Q3 cottage placements (door, windows, bed, sconce) and the Q7 stake — those are
#     BlockEvents.placed, and only a player fires it;
#   * the FORTIETH lamp: Josie's porch post is lit by Q90's block-placed check and by
#     nothing else, so 39 of 40 is the headless maximum and 39 is a PASS here;
#   * anything the client renders. Mixins, models and textures need the client log.
#
# It runs TWICE, on two fresh copies of world-master/:
#   pass 1  act1 only        -> exactly six lamps come on, and the other 34 stay dark
#   pass 2  every act, then every scene, in story order
#
# Usage: tools/scripts/headless_playthrough.sh
# Logs:  scratch/headless_playthrough/
# =============================================================================
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; C="$ROOT/tools/scripts/server_ctl.sh"
LOG="$SRV/logs/latest.log"; OUT="$ROOT/scratch/headless_playthrough"
FIFO="$ROOT/scratch/server.in"; PY="$ROOT/tools/venv/bin/python"
mkdir -p "$OUT"

ts() { echo "[$(date +%H:%M:%S)] $1"; }
say() { printf '%s\n' "$1" > "$FIFO"; sleep "${2:-0.5}"; }

# Our server is the one whose WORKING DIRECTORY is $SRV: a bare `unix_args` pgrep matches
# the parallel Kettle Tech server too (docs/SESSIONS.md rule 1).
ours() {
  local p cwd
  for p in $(pgrep -f "unix_args.txt nogui" 2>/dev/null); do
    cwd=$(lsof -a -p "$p" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
    [ "$cwd" = "$SRV" ] && print -r -- "$p"
  done
}
[ -n "$(ours)" ] && { echo "REFUSING: our Forge server is already running."; exit 1; }
pgrep -f 'cpw.mods.bootstraplauncher' >/dev/null && { echo "REFUSING: a Minecraft client is running."; exit 1; }
[ -d "$ROOT/world-master/region" ] || { echo "no world-master/ — run scratch/master_build.sh"; exit 1; }

# -----------------------------------------------------------------------------
# 0. the static asserts: the runtime story may not build
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
# 1. sync FROM pack/, and prove it
# -----------------------------------------------------------------------------
ts "== packwiz refresh + sync server FROM pack/"
( cd "$ROOT/pack" && "$ROOT/tools/packwiz" refresh >/dev/null 2>&1 )
"$ROOT/tools/scripts/sync_server.sh" 2>&1 | tail -2
for f in valley_core.js valley_finales.js valley_checks.js valley_build.js valley_sites.js \
         town_plan.js valley_gates.js valley_greetings.js valley_keepsakes.js \
         valley_step.js seasons_tags.js unify.js; do
  [ -f "$SRV/kubejs/server_scripts/$f" ] || { echo "SYNC WRONG: no $f — a parallel job has synced server/ from pack-tech/."; exit 1; }
done
echo "  valley scripts in server/: $(ls "$SRV/kubejs/server_scripts" | wc -l | tr -d ' ')"

install_world() {
  rm -rf "$SRV/world"
  cp -R "$ROOT/world-master" "$SRV/world"
  rm -f "$SRV/world/session.lock"
}

# Every finale forceloads its own ground and drops it again at endAct. A scene does not, and
# a console command into an unloaded chunk is refused silently. So the whole valley is held
# open for the length of the run and released at the end.
forceload_valley() {
  say "forceload add -370 -110 -230 30" 1
  say "forceload add -350 90 -290 140" 1
  say "forceload query" 1
}

boot() {
  $C start >/dev/null; $C wait || { echo "SERVER FAILED TO BOOT"; tail -40 "$LOG"; exit 1; }
  grep -q 'valley_sites.js ok' "$LOG" || { echo "valley_sites.js DID NOT LOAD"; exit 1; }
  echo "  registry: $(grep -o 'valley_sites.js ok.*' "$LOG" | tail -1)"
}

# -----------------------------------------------------------------------------
# PASS 1 — Act I on its own. Six lamps, and no more.
# -----------------------------------------------------------------------------
ts "== PASS 1: a fresh world, Act I only"
install_world
boot
forceload_valley
MARK1=$(wc -l < "$LOG" | tr -d ' ')
say "valley anchor" 1
say "valley lamps" 1
say "valley finale act1" 20
say "valley lamps" 2
say "save-all flush" 12
tail -n +"$MARK1" "$LOG" > "$OUT/act1.log"
echo "  act1 chains complete: $(grep -c 'finale act1 complete' "$OUT/act1.log")"
say "forceload remove all" 1
$C stop >/dev/null
rm -rf "$OUT/world_act1"; cp -R "$SRV/world" "$OUT/world_act1"; rm -f "$OUT/world_act1/session.lock"

# -----------------------------------------------------------------------------
# PASS 2 — the whole story, on another fresh world.
# -----------------------------------------------------------------------------
ts "== PASS 2: a fresh world, every act and every scene"
install_world
boot
forceload_valley
MARK2=$(wc -l < "$LOG" | tr -d ' ')

ts "== the Start Here beats a console can run"
say "valley anchor" 1
say "valley lamps" 1
say "valley check standing" 1
say "valley build list" 2

ts "== finales, in order"
# Waits are each chain's own last beat plus its FINALE_RELEASE: act1/act2 have an arrival
# that may retry for 142 ticks, act3 turns at 120, act4's last beat is at 200 plus a 60/40
# tail, act5's sixth journal line lands at tick 700 (FINALE_RELEASE 720 = 36 s).
for a in "act1 20" "act2 20" "act3 20" "act4 26" "act5 48"; do
  set -- ${=a}
  ts "   /valley finale $1"
  say "valley finale $1" "$2"
done
say "valley lamps" 2

ts "== scenes, in quest order"
for s in bram inn coop square_path cellar marnie pip q54 q58 q59 q60 q62 q64 q65 q66 \
         q70a q71 q72 q73 q74 q76; do
  say "valley scene $s" 2.5
done
sleep 8

say "valley lamps" 1
say "valley check standing" 1
say "easy_npc list" 3
say "execute as @e[type=easy_npc:humanoid] run data get entity @s CustomName" 3
say "execute as @e[type=easy_npc:humanoid_slim] run data get entity @s CustomName" 3
sleep 3
say "forceload remove all" 1
say "save-all flush" 14
tail -n +"$MARK2" "$LOG" > "$OUT/story.log"
cp "$LOG" "$OUT/server_full.log" 2>/dev/null
$C stop >/dev/null
rm -rf "$OUT/world_story"; cp -R "$SRV/world" "$OUT/world_story"; rm -f "$OUT/world_story/session.lock"

# -----------------------------------------------------------------------------
# THE LOG'S OWN VERDICT
# -----------------------------------------------------------------------------
echo "=== SERVER LOG (pass 2)"
echo "finales complete:                 $(grep -oE 'finale act[0-9] complete' "$OUT/story.log" | sort -u | tr '\n' ' ')"
echo "distinct scenes played:           $(grep -oE 'scene [a-z0-9_]+ played' "$OUT/story.log" | sort -u | wc -l | tr -d ' ') of 21"
echo "arrival retries that gave up:     $(grep -c 'arrival gave up' "$OUT/story.log")"
echo "REFUSED build commands (must be 0): $(grep -c 'REFUSED (' "$OUT/story.log")"
grep -oE 'REFUSED \([^)]*\)' "$OUT/story.log" | sort | uniq -c | head -5
echo "doors that could not be put back: $(grep -c 'could not be put back' "$OUT/story.log")"
echo "[valley] real errors:             $(grep -caE '\[valley\] (finale command failed|build command failed|unknown build directive)|\[valley\].*(ReferenceError|TypeError)' "$OUT/story.log")"
echo "KubeJS script errors:             $(grep -caE 'Error in .ServerEvents|ReferenceError|TypeError|kubejs.*ERROR' "$OUT/story.log")"
echo "unknown / bad commands:"
for pat in 'Unknown or incomplete command' 'Incorrect argument for command' \
           'That position is not loaded' 'Failed to place' 'Unknown item' 'Unknown block' \
           'No entity was found' 'Could not parse' 'Invalid chat component'; do
  n=$(grep -ca "$pat" "$OUT/story.log")
  [ "$n" -gt 0 ] && echo "  $n  $pat"
done
echo "  (nothing listed above = zero command errors in the whole run)"
echo "commands that returned 0 (no effect), by shape:"
grep -a 'command returned 0' "$OUT/story.log" | sed -E 's/.*failed\): ([a-z_]+).*/  \1/' | sort | uniq -c | sort -rn | head -8

# -----------------------------------------------------------------------------
# THE WORLD'S OWN VERDICT
# -----------------------------------------------------------------------------
RC=0
echo
"$PY" "$ROOT/tools/scripts/headless_assert.py" --world "$ROOT/world-master" --phase pristine \
      --json "$OUT/pristine.json" || RC=1
echo
"$PY" "$ROOT/tools/scripts/headless_assert.py" --world "$OUT/world_act1" --phase act1 \
      --json "$OUT/act1.json" || RC=1
echo
"$PY" "$ROOT/tools/scripts/headless_assert.py" --world "$OUT/world_story" --phase after \
      --json "$OUT/after.json" || RC=1
echo
echo "=== exit $RC"
exit $RC
