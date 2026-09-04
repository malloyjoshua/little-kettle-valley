#!/bin/zsh
# Automated playthrough + command audit + client regression. An offline test client joins a temporarily
# offline-mode server on a fresh world; the Town Anchor and Home are set near the player; every quest is
# completed in dependency order; then every command reward, every datapack function line, every finale and
# scene is executed from the console (where feedback is logged) and the log is censused for failures.
# Then two rules that only a live client can prove are exercised: the /valley check look-at rule, and the
# per-TEAM latch, with a SECOND offline client on its own team. online-mode is restored on exit.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; C="$ROOT/tools/scripts/server_ctl.sh"; JAVA="$ROOT/tools/jdk17/Contents/Home/bin/java"
GD="$HOME/Library/Application Support/PrismLauncher/instances/CozyTech/.minecraft"
LOG="$SRV/logs/latest.log"; OUT="${PLAYTHROUGH_OUT:-$ROOT/scratch/night_playthrough}"; mkdir -p "$OUT"; rm -f "$OUT/completed.txt"
GD2="$OUT/gamedir2"
FIFO="$ROOT/scratch/server.in"; P=packtester; P2=packmate; PIDF="$ROOT/scratch/server.pid"

# ---------------------------------------------------------------------------
# One run at a time, enforced rather than remembered.
# server_ctl.sh gives every run the SAME control FIFO, the same pid file and the
# same server.properties. Starting a second run while the previous one is still
# in its `$C stop` (which waits up to two minutes) means that stop's "stop" goes
# down the new run's FIFO into the new run's server: it booted, reported DONE,
# was shut down thirty seconds later, and the client got "Connection refused"
# and span for five minutes before giving up. Refuse instead.
# ---------------------------------------------------------------------------
for pid in $(pgrep -f 'playthrough.sh'); do
  [ "$pid" = "$$" ] && continue
  ps -o command= -p "$pid" | grep -q 'zsh.*playthrough.sh' && {
    echo "REFUSING: another playthrough.sh is running (pid $pid). Let it finish, or kill it."; exit 1; }
done
pgrep -f 'forge/1.20.1.*unix_args' >/dev/null && { echo "REFUSING: a Forge server is already running. Stop it first."; exit 1; }
pgrep -f 'cpw.mods.bootstraplauncher' >/dev/null && { echo "REFUSING: a Minecraft client is already running."; exit 1; }
ts() { echo "[$(date +%H:%M:%S)] $1"; }
# printf, never echo: zsh's builtin echo expands backslash escapes, and the audit list carries
# quest text with \u escapes in it. One "Tobin\u2019s lanterns" line aborted a whole run with
# "character not in range" partway through the audit.
say() { printf '%s\n' "$1" > "$FIFO"; sleep "${2:-0.5}"; }
# Everything between two marks in the server log, for a phase-local census.
since() { tail -n +"$1" "$LOG"; }
cp "$SRV/server.properties" "$OUT/server.properties.bak"
restore() { cp "$OUT/server.properties.bak" "$SRV/server.properties"; grep -q '^online-mode=true' "$SRV/server.properties" && echo "online-mode restored to true"; }
trap restore EXIT
ts "== sync pack -> server + client"; ( cd "$ROOT/pack" && "$ROOT/tools/packwiz" refresh >/dev/null 2>&1 )
"$ROOT/tools/scripts/sync_server.sh"
( cd "$GD" && "$JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "$ROOT/pack/pack.toml" 2>&1 | tail -1 )
# The audit list is DERIVED, never edited by hand: a stale scratch/audit_cmds.txt silently stops covering
# the quests and functions that changed since it was written, which is the one thing this run exists to catch.
"$ROOT/tools/venv/bin/python" "$ROOT/tools/scripts/command_audit.py" "$P" > "$ROOT/scratch/audit_cmds.txt"
echo "audit list regenerated: $(grep -vc '^#' "$ROOT/scratch/audit_cmds.txt") commands"
sed -i '' 's/^online-mode=true/online-mode=false/' "$SRV/server.properties"
rm -rf "$SRV/world"
$C start >/dev/null; $C wait || { echo "SERVER FAILED TO BOOT"; tail -40 "$LOG"; exit 1; }
# whitelist OFF, not "whitelist add". The server resolves a name it is given against Mojang
# (this Mac is online), so `whitelist add packmate` stored the REAL account Packmate's uuid
# while the offline client connects with the MD5 offline uuid — "You are not white-listed on
# this server!", and the second client never joined. server.properties is restored on exit.
say "whitelist off" 1; say "op $P" 1; say "op $P2" 1
cd "$ROOT"; tools/venv/bin/python tools/scripts/testclient.py command "$GD" --xmx 3584 --server localhost:25565 > "$OUT/client_cmd.json"
rm -rf "$GD/logs"; ( cd "$GD" && nohup "$ROOT/tools/venv/bin/python" -c "import json,subprocess;subprocess.run(json.load(open('$OUT/client_cmd.json')))" > "$OUT/client.out" 2>&1 & )
for i in $(seq 1 60); do sleep 5
  grep -q "$P joined the game" "$LOG" 2>/dev/null && { ts "CLIENT_JOINED after $((i*5))s"; break; }
  # A server that died here is the failure, not the client. Say so at once.
  kill -0 "$(cat "$PIDF" 2>/dev/null)" 2>/dev/null || { echo "SERVER DIED DURING CLIENT JOIN after $((i*5))s"; tail -20 "$ROOT/scratch/server.out"; exit 1; }
  [ $i -eq 60 ] && { echo "CLIENT NEVER JOINED"; exit 1; }
done
sleep 25
MARK=$(wc -l < "$LOG" | tr -d ' '); echo "log mark $MARK"
say "data get entity $P Pos" 2
POS=$(grep 'has the following entity data' "$LOG" | tail -1 | sed -E 's/.*\[(.*)\].*/\1/' | tr -d 'd' | tr ',' ' ')
PX=$(echo $POS | awk '{printf "%d",$1}'); PY=$(echo $POS | awk '{printf "%d",$2}'); PZ=$(echo $POS | awk '{printf "%d",$3}'); echo "player at $PX $PY $PZ"
# The stake has to clear the cottage. town_box is x[-48,63] z[-45,60] grown by
# town_clearance 12, so an anchor within 60 blocks of Home on EITHER axis is
# refused by anchorSetCmd() — and this harness used to put it 14 blocks away,
# which set no anchor at all and left every finale with nothing to measure
# from. 80 clears it on both axes with room to spare.
#
# The two attempts below are also the client-visible half of the clearance
# check: they run `execute as/at` the PLAYER, so the refusal and the
# acceptance are p.tell()'d into the client's own chat log, which is the only
# place either message can be read. The console-side rule (every cardinal,
# per-position) is verify_run.sh + vt_check.py section (11); this is the half
# that needs a real player on the other end of it.
AX=$((PX+80)); AY=$PY; AZ=$((PZ+80))
NX=$((PX+14)); NZ=$((PZ+14))
say "valley home set $PX $PY $PZ" 1
say "execute as $P at $P run valley anchor set $NX $PY $NZ" 1   # too close: must refuse
say "valley anchor" 1                                           # ...and must still be unset
say "execute as $P at $P run valley anchor set $AX $AY $AZ" 1   # 80 out: must be accepted
say "setblock $((PX-2)) $PY $((PZ-2)) waystones:waystone" 1; say "valley anchor" 1
ts "== quests"; n=0
tools/venv/bin/python tools/scripts/quest_order.py | while IFS=$'\t' read -r key id title ch cmdid; do
  echo "$key $id $title" >> "$OUT/completed.txt"; say "ftbquests change_progress $P complete $cmdid" 1.0
  case "$key" in q19|q37|q56|q75|q91) sleep 12;; esac
done
echo "client RSS MB after quests: $(ps -o rss= -p $(pgrep -f cpw.mods.bootstraplauncher | head -1) 2>/dev/null | awk '{print int($1/1024)}')"
sleep 10; echo "quests completed: $(wc -l < "$OUT/completed.txt" | tr -d ' ')"
ts "== command audit ($(grep -vc '^#' "$ROOT/scratch/audit_cmds.txt") commands)"; AMARK=$(wc -l < "$LOG" | tr -d ' ')
grep -v '^#' "$ROOT/scratch/audit_cmds.txt" | grep -v '^\s*$' | while IFS= read -r cmd; do say "$cmd" 0.35; done
sleep 5
ts "== finales + scenes"; FMARK=$(wc -l < "$LOG" | tr -d ' ')
for a in 1 2 3 4 5; do say "valley finale act$a" 8; done
for s in q58 q59 q60 q62 q64 q65 q66 q70a q71 q72 q73 q74; do say "valley scene $s" 2; done
sleep 10
# Counted over the WHOLE run, not from FMARK: each act's own quest reward is
# `/valley finale actN`, so all five have usually already run during the command audit and
# the explicit pass below only re-runs beats that were skipped. A window that starts here
# reports "0 acts complete" on a perfectly good run.
echo "finales complete: $(grep -oE 'finale act[0-9] complete' "$LOG" | sort -u | tr '\n' ' ')"
echo "arrival retries that gave up: $(grep -c 'gave up' "$LOG")"
echo "distinct scenes run: $(grep -oE 'valley\] scene [a-z0-9_]+' "$LOG" | sort -u | wc -l | tr -d ' ')"
echo "client RSS MB after finales: $(ps -o rss= -p $(pgrep -f cpw.mods.bootstraplauncher | head -1) 2>/dev/null | awk '{print int($1/1024)}')"

# -----------------------------------------------------------------------------
# The four things this run was re-opened for. Driven from newbits_probe.py so the
# camp cells and the chair offset are READ OUT of the town plan rather than typed
# here: the planner solves square.scenes.ribbit_camp against the four market
# carts, and a copy in this file would go stale the first time it re-solves.
#   1. the 3x3 hammer: the quest's reward item and the cheap copper recipe
#   2. Q59's Ribbits stand on open ground, not inside the fisher's cart
#   3. Bram's Act IV chair teleport, cold
# (the anchor clearance rule is #4 and ran up in the setup, before the town
#  existed; its verdict is read off the client chat log at the end.)
# -----------------------------------------------------------------------------
ts "== new bits: hammer / Q59 camp / Q73 chair"
NBMARK=$(wc -l < "$LOG" | tr -d ' ')
tools/venv/bin/python tools/scripts/newbits_probe.py cmds $AX $AY $AZ | while IFS= read -r cmd; do
  case "$cmd" in
    "valley scene q59"|"valley scene q73") say "$cmd" 10;;
    say\ NB_*SETTLE) say "$cmd" 6;;
    *) say "$cmd" 0.6;;
  esac
done
sleep 3
tail -n +"$NBMARK" "$LOG" > "$OUT/newbits.log"

# -----------------------------------------------------------------------------
# The look-at rule on /valley check (valley_finales.js CHECK_BLOCK).
# Both halves, because only the refusal half can fail quietly: a broken rayTrace
# binding logs and falls through to the 16-block box, which is exactly the
# loophole the rule exists to close, and nothing else in this run would notice.
# The rig is a floating platform at the Works' x/z so no terrain can block the ray.
# -----------------------------------------------------------------------------
ts "== reactor look-at rule"
WX=$((AX+34)); WZ=$((AZ-20)); RY=$((AY+40)); LMARK=$(wc -l < "$LOG" | tr -d ' ')
# Creative for the rig phases only: a survival test player who suffocates in the Works shell or
# falls off the floating platform respawns at world spawn and the probe measures nothing.
say "gamemode creative $P" 1
say "forceload add $((WX-8)) $((WZ-8)) $((WX+8)) $((WZ+8))" 1
say "fill $((WX-2)) $((RY-1)) $((WZ-2)) $((WX+2)) $((RY+3)) $((WZ+4)) air" 1
say "fill $((WX-1)) $((RY-1)) $((WZ-1)) $((WX+1)) $((RY-1)) $((WZ+3)) stone" 1
say "setblock $WX $((RY+1)) $WZ biggerreactors:turbine_terminal" 1
# feet at RY, eyes at RY+1.62, facing north (yaw 180) at the block spanning RY+1..RY+2
say "tp $P $WX $RY $((WZ+2)) 0 0" 1          # facing SOUTH: the terminal is behind him
say "execute as $P at $P run valley check turbine" 2
say "tp $P $WX $RY $((WZ+2)) 180 0" 1        # facing NORTH: the terminal is in the crosshair
say "execute as $P at $P run valley check turbine" 2
say "setblock $WX $((RY+1)) $WZ biggerreactors:reactor_terminal" 1
say "execute as $P at $P run valley check power" 2
say "tp $P $((WX+60)) $RY $((WZ+60)) 180 0" 1  # 60 blocks out: the distance half must refuse
say "execute as $P at $P run valley check power" 2
since $LMARK > "$OUT/lookat.log"
# checkAt() answers with msg(), which is p.tell() — it goes to the PLAYER, not the console.
# The only place the refusal and the pass are both visible is the CLIENT's chat log, so the
# census for this phase runs down with the client-log census at the end of the run.
echo "look-at rig built; verdict is read off the client chat log below"

# -----------------------------------------------------------------------------
# The per-TEAM latch, with a second client on its own FTB Teams party.
# q65 is the probe: "player inside the Works box", no stage gate, no items. If the
# latch were world-level (the bug the header of valley_checks.js describes) the
# second player's team would never see "check satisfied" for a key the first
# team already took.
# -----------------------------------------------------------------------------
ts "== second client / per-team latch"
rm -rf "$GD2"; cp -Rc "$GD" "$GD2" 2>/dev/null || cp -R "$GD" "$GD2"; rm -rf "$GD2/logs" "$GD2/saves"
tools/venv/bin/python tools/scripts/testclient.py command "$GD2" --xmx 3072 --user "$P2" --server localhost:25565 > "$OUT/client2_cmd.json"
( cd "$GD2" && nohup "$ROOT/tools/venv/bin/python" -c "import json,subprocess;subprocess.run(json.load(open('$OUT/client2_cmd.json')))" > "$OUT/client2.out" 2>&1 & )
JOINED2=no
for i in $(seq 1 60); do sleep 5; grep -q "$P2 joined the game" "$LOG" && { echo "CLIENT2_JOINED after $((i*5))s"; JOINED2=yes; break; }; done
if [ "$JOINED2" = no ]; then
  echo "SECOND CLIENT NEVER JOINED — per-team latch NOT exercised"
else
  sleep 20
  TMARK=$(wc -l < "$LOG" | tr -d ' ')
  WY=$((AY-6))
  say "gamemode creative $P2" 1
  say "forceload add $((WX-8)) $((WZ-8)) $((WX+8)) $((WZ+8))" 1
  say "tp $P $WX $((WY+1)) $WZ" 4      # team A stands in the Works box
  say "tp $P2 $WX $((WY+1)) $WZ" 6     # team B stands in the same box
  sleep 6
  say "execute as $P run valley check standing" 2
  say "execute as $P2 run valley check standing" 2
  since $TMARK > "$OUT/teams.log"
  TEAMS=$(grep -oE 'check satisfied: q65 \(team [^)]+\)' "$OUT/teams.log" | sed -E 's/.*team //;s/\)//' | sort -u)
  echo "q65 fired for teams: $(echo $TEAMS | tr '\n' ' ')  distinct=$(echo "$TEAMS" | grep -c . )"
fi
say "valley lamps" 1; say "easy_npc list" 3
# easy_npc list truncates its listing at ten entries, so counting "Type: easy_npc" lines
# reports 10 on a world with all fifteen residents. "Total NPCs:" is the real number, and
# the roll-call below is by display name, which is the thing the quest text actually promises.
say "execute as @e[type=easy_npc:humanoid] run data get entity @s CustomName" 3
say "execute as @e[type=easy_npc:humanoid_slim] run data get entity @s CustomName" 3
sleep 5
say "save-all flush" 8
tail -n +"$MARK" "$LOG" > "$OUT/playthrough.log"; tail -n +"$AMARK" "$LOG" > "$OUT/audit.log"
cp "$LOG" "$OUT/server_full.log" 2>/dev/null
echo "=== SUMMARY"
echo "quests completed (console): $(wc -l < "$OUT/completed.txt" | tr -d ' ')"
echo "quest completions acked by FTBQuests: $(grep -c 'Progress has been changed' "$OUT/playthrough.log")"
echo "NPCs alive: $(grep -oE 'Total NPCs: [0-9]+' "$OUT/playthrough.log" | tail -1 | awk '{print $3}') (want 15)"
MISSING=0
for npc in "Bram Tolliver" "Halden Root" "Marnie Ashcombe" "Nella Brightwater" "Corin Ashe" \
           "Mab Oldfield" "Tess Weaver" "Oda Vance" "Pip Ashcombe" "Mudlark" "Puddle" "Reed" \
           "Sedge" "Tobin Gale" "Wisp"; do
  grep -qF "$npc" "$OUT/playthrough.log" || { echo "  MISSING RESIDENT: $npc"; MISSING=$((MISSING+1)); }
done
echo "residents named in the world: $((15-MISSING))/15"
# "command returned 0" is NOT an error for a block write. fill and setblock both return 0
# when every cell in the box already holds the target block, which is the normal answer for
# an idempotent pad-levelling pass over ground that already matches and for the audit phase
# replaying function lines the finales already ran. Counting them as [valley] errors put
# 4545 false positives on the summary line and buried the two classes that DO mean something:
# a thrown command (finale command failed) and a non-block command that did nothing.
NOOP=$(grep -ca 'command returned 0' "$OUT/playthrough.log")
echo "[valley] real errors: $(grep -caE '\[valley\] (finale command failed|unknown build directive)|\[valley\].*(ReferenceError|TypeError)' "$OUT/playthrough.log")"
echo "[valley] idempotent block writes (fill/setblock already correct — not failures): $NOOP"
grep -oaE 'command returned 0 \(no effect / failed\): [a-z_]+' "$OUT/playthrough.log" | awk '{print "    " $NF}' | sort | uniq -c | sort -rn | head -6
echo "KubeJS script errors: $(grep -cE 'Error in .ServerEvents|ReferenceError|TypeError|Rhino|kubejs.*ERROR' "$OUT/playthrough.log")"
echo "quest ids the command parser refused: $(grep -c 'Invalid Object ID' "$OUT/playthrough.log")"
# Kept short on purpose: one long alternation tripped ugrep's complexity limit and the
# census silently printed an error instead of the counts.
echo "error census (whole run, idempotent block writes excluded):"
for pat in 'Invalid Object ID' 'No quest object found' 'Invalid chat component' \
           'Unknown or incomplete command' 'Incorrect argument for command' \
           'No player was found' 'No entity was found' 'That position is not loaded' \
           'Failed to place' 'Unknown item' 'Unknown block' 'Unknown function' \
           'Unknown loot table' 'Unknown entity' 'Unknown effect' 'Could not set' \
           'Could not find' 'Could not parse' 'finale command failed' \
           'Error in .ServerEvents' 'TypeError' 'ReferenceError' 'Expected .* at position'; do
  n=$(grep -ca "$pat" "$OUT/playthrough.log")
  [ "$n" -gt 0 ] && echo "  $n  $pat"
done
echo "  (nothing listed above = zero command errors in the whole run)"

# -----------------------------------------------------------------------------
# The CLIENT log. The server never sees a missing model, a failed mixin or a
# recipe the client refused to sync, so none of the above would catch them.
# -----------------------------------------------------------------------------
pkill -f 'cpw.mods.bootstraplauncher'; sleep 5
cp "$GD/logs/latest.log" "$OUT/client.log" 2>/dev/null
cp "$GD2/logs/latest.log" "$OUT/client2.log" 2>/dev/null
echo "=== CLIENT LOG"
for f in "$OUT/client.log" "$OUT/client2.log"; do
  [ -f "$f" ] || continue
  echo "-- $(basename $f) ($(wc -l < "$f" | tr -d ' ') lines)"
  echo "   mixin failures:      $(grep -cE 'Mixin apply failed|MixinApplyError|MixinTransformerError|Critical injection failure|mixin.*could not be applied' "$f")"
  echo "   missing models:      $(grep -cE 'Unable to load model|Exception loading blockstate|Missing textures in model' "$f")"
  echo "   missing textures:    $(grep -cE 'Using missing texture|Failed to load texture|File .* does not exist.*textures' "$f")"
  # The pack's OWN assets are the ones that matter. Upstream mods ship a handful of
  # missing-texture models in every 1.20.1 pack and they are not this pack's problem.
  echo "   valley: asset gaps:  $(grep -cE '(Unable to load model|Using missing texture|Failed to load texture|Missing textures in model)[^\n]*valley' "$f")"
  echo "   recipe conflicts:    $(grep -cE 'Duplicate recipe|recipe .* conflict|Parsing error loading recipe|Failed to parse recipe' "$f")"
  echo "   ERROR lines:         $(grep -c '/ERROR\]' "$f")"
  echo "   FATAL lines:         $(grep -c '/FATAL\]' "$f")"
done
echo "=== NEW BITS"
tools/venv/bin/python tools/scripts/newbits_probe.py check $AX $AY $AZ "$OUT/newbits.log" || true
echo "  quest reward declares the hammer: $(grep -c 'item: \"justhammers:stone_hammer\"' "$ROOT/pack/config/ftbquests/quests/chapters/act1.snbt") (want 1)"
# JEI builds its registry from the recipes the SERVER syncs to the client, so the
# sync landing is the link between "/recipe give accepted the id" and "JEI can see it".
echo "  server->client recipe sync:          $(grep -ca 'recipe sync for player' "$OUT/playthrough.log") (want >=1)"
  # Forge prints the level BEFORE the logger name, so "jei.*ERROR" never matches
  # a JEI error line. Match the logger, and the phrases JEI uses when a recipe
  # will not go into its registry, independently.
  echo "  JEI loaded its recipe registry:      $(grep -cE 'mezz\.jei.*(Registering recipes|Building recipe registry|Starting JEI)' "$OUT/client.log" 2>/dev/null)"
  echo "  JEI errors / broken recipes:         $(grep -cE '(ERROR|WARN).*mezz\.jei|broken recipe|Failed to register recipe' "$OUT/client.log" 2>/dev/null)"
echo "=== ANCHOR CLEARANCE (player-visible, read off the client's chat log)"
if [ -f "$OUT/client.log" ]; then
  echo "  refused, too close to the cottage: $(grep -c 'Too close to the cottage' "$OUT/client.log") (want 1)"
  echo "  Josie says why:                    $(grep -c 'will not have them in your dooryard' "$OUT/client.log") (want 1)"
  echo "  accepted 80 blocks out:            $(grep -c 'Town Anchor set to' "$OUT/client.log") (want 1)"
  echo "  forced overrides needed:           $(grep -c '(forced)' "$OUT/client.log") (want 0)"
fi
echo "=== LOOK-AT RULE (read off the client's chat log)"
LC="$OUT/client.log"
if [ -f "$LC" ]; then
  echo "  refused, not looking at it: $(grep -c 'Look at the Turbine Terminal' "$LC") (want 1)"
  echo "  passed, terminal in view:   $(grep -cE 'Turbine holding 1,800 RPM|25,000 FE/t sustained' "$LC") (want 2)"
  echo "  refused, too far from Works:$(grep -c 'Stand at the Works and run this again' "$LC") (want 1)"
  echo "  rayTrace fallbacks:         $(grep -c 'rayTrace unavailable' "$OUT/playthrough.log") (want 0)"
else
  echo "  NO CLIENT LOG — look-at rule NOT verified"
fi
$C stop
