#!/bin/zsh
# Automated playthrough + command audit. Offline test client joins a temporarily offline-mode server on a fresh
# world; the Town Anchor and Home are set near the player; every quest is completed in dependency order; then
# every command reward, every datapack function line, every finale and scene is executed from the console
# (where feedback is logged) and the log is censused for failures. online-mode is restored on exit.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; C="$ROOT/tools/scripts/server_ctl.sh"; JAVA="$ROOT/tools/jdk17/Contents/Home/bin/java"
GD="$HOME/Library/Application Support/PrismLauncher/instances/CozyTech/.minecraft"
LOG="$SRV/logs/latest.log"; OUT="$ROOT/scratch/playthrough"; mkdir -p "$OUT"; rm -f "$OUT/completed.txt"
FIFO="$ROOT/scratch/server.in"; P=packtester
say() { echo "$1" > "$FIFO"; sleep "${2:-0.5}"; }
cp "$SRV/server.properties" "$OUT/server.properties.bak"
restore() { cp "$OUT/server.properties.bak" "$SRV/server.properties"; grep -q '^online-mode=true' "$SRV/server.properties" && echo "online-mode restored to true"; }
trap restore EXIT
echo "== sync pack -> server + client"; ( cd "$ROOT/pack" && "$ROOT/tools/packwiz" refresh >/dev/null 2>&1 )
"$ROOT/tools/scripts/sync_server.sh"
( cd "$GD" && "$JAVA" -jar packwiz-installer-bootstrap.jar -g -s client "$ROOT/pack/pack.toml" 2>&1 | tail -1 )
sed -i '' 's/^online-mode=true/online-mode=false/' "$SRV/server.properties"
rm -rf "$SRV/world"
$C start >/dev/null; $C wait || { echo "SERVER FAILED TO BOOT"; tail -40 "$LOG"; exit 1; }
say "whitelist add $P" 1; say "op $P" 1
cd "$ROOT"; tools/venv/bin/python tools/scripts/testclient.py command "$GD" --xmx 3584 --server localhost:25565 > "$OUT/client_cmd.json"
rm -rf "$GD/logs"; ( cd "$GD" && nohup "$ROOT/tools/venv/bin/python" -c "import json,subprocess;subprocess.run(json.load(open('$OUT/client_cmd.json')))" > "$OUT/client.out" 2>&1 & )
for i in $(seq 1 60); do sleep 5; grep -q "$P joined the game" "$LOG" && { echo "CLIENT_JOINED after $((i*5))s"; break; }; [ $i -eq 60 ] && { echo "CLIENT NEVER JOINED"; exit 1; }; done
sleep 25
MARK=$(wc -l < "$LOG" | tr -d ' '); echo "log mark $MARK"
say "data get entity $P Pos" 2
POS=$(grep 'has the following entity data' "$LOG" | tail -1 | sed -E 's/.*\[(.*)\].*/\1/' | tr -d 'd' | tr ',' ' ')
PX=$(echo $POS | awk '{printf "%d",$1}'); PY=$(echo $POS | awk '{printf "%d",$2}'); PZ=$(echo $POS | awk '{printf "%d",$3}'); echo "player at $PX $PY $PZ"
say "valley home set $PX $PY $PZ" 1; say "valley anchor set $((PX+14)) $PY $((PZ+14))" 1; say "setblock $((PX-2)) $PY $((PZ-2)) waystones:waystone" 1; say "valley anchor" 1
echo "== quests"; n=0
tools/venv/bin/python tools/scripts/quest_order.py | while IFS=$'\t' read -r key id title ch; do
  echo "$key $id $title" >> "$OUT/completed.txt"; say "ftbquests change_progress $P complete $id" 1.0
  case "$key" in q19|q37|q56|q75|q91) sleep 12;; esac
done
echo "client RSS MB after quests: $(ps -o rss= -p $(pgrep -f cpw.mods.bootstraplauncher | head -1) 2>/dev/null | awk '{print int($1/1024)}')"
sleep 10; echo "quests completed: $(wc -l < "$OUT/completed.txt" | tr -d ' ')"
echo "== command audit ($(grep -c '^[^#]' "$ROOT/scratch/audit_cmds.txt") commands)"; AMARK=$(wc -l < "$LOG" | tr -d ' ')
grep -v '^#' "$ROOT/scratch/audit_cmds.txt" | grep -v '^\s*$' | while IFS= read -r cmd; do say "$cmd" 0.35; done
sleep 5
echo "== finales + scenes"; for a in 1 2 3 4 5; do say "valley finale act$a" 8; done
for s in q58 q59 q60 q62 q64 q65 q66 q70a q71 q72 q73 q74; do say "valley scene $s" 2; done
echo "client RSS MB after finales: $(ps -o rss= -p $(pgrep -f cpw.mods.bootstraplauncher | head -1) 2>/dev/null | awk '{print int($1/1024)}')"
say "valley lamps" 1; say "easy_npc list" 2; sleep 5
tail -n +"$MARK" "$LOG" > "$OUT/playthrough.log"; tail -n +"$AMARK" "$LOG" > "$OUT/audit.log"
echo "=== SUMMARY"
echo "NPCs alive: $(grep -c 'Type: easy_npc' "$OUT/playthrough.log")"
echo "error census (whole run):"; grep -oE 'Unknown or incomplete command|Incorrect argument for command|No player was found|No entity was found|That position is not loaded|Failed to place|Unknown (item|block|advancement|loot table|function|structure|entity|dimension|effect)|There is no [a-z ]+|Could not (set|find|parse) [a-z ]*|command returned 0[^\n]{0,120}|finale command failed[^\n]{0,120}|Error in .ServerEvents[^\n]{0,80}|TypeError[^\n]{0,80}|ReferenceError[^\n]{0,80}|Cannot [a-z ]+ property[^\n]{0,60}|Expected [a-z]+ at position' "$OUT/playthrough.log" | sort | uniq -c | sort -rn | head -40
say "save-all" 5
pkill -f 'cpw.mods.bootstraplauncher'; sleep 3; $C stop
