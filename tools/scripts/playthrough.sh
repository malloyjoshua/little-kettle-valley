#!/bin/zsh
# Automated command-layer playthrough: offline test client joins a temporarily offline-mode server,
# then every quest is completed in dependency order from the console and the log is checked for errors.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; C="$ROOT/tools/scripts/server_ctl.sh"
GD="$HOME/Library/Application Support/PrismLauncher/instances/CozyTech/.minecraft"
LOG="$SRV/logs/latest.log"; OUT="$ROOT/scratch/playthrough"; mkdir -p "$OUT"
cp "$SRV/server.properties" "$OUT/server.properties.bak"
sed -i '' 's/^online-mode=true/online-mode=false/' "$SRV/server.properties"
restore() { cp "$OUT/server.properties.bak" "$SRV/server.properties"; grep -q '^online-mode=true' "$SRV/server.properties" && echo "online-mode restored to true"; }
trap restore EXIT
rm -rf "$SRV/world"   # fresh world every run so first-join and finales are exercised from zero
$C start >/dev/null; $C wait || { echo "SERVER FAILED TO BOOT"; tail -40 "$LOG"; exit 1; }
$C cmd "whitelist add PackTester"; $C cmd "op PackTester"
cd "$ROOT"; tools/venv/bin/python tools/scripts/testclient.py command "$GD" --xmx 3584 --server localhost:25565 > "$OUT/client_cmd.json"
rm -rf "$GD/logs"; ( cd "$GD" && nohup "$ROOT/tools/venv/bin/python" -c "import json,subprocess;subprocess.run(json.load(open('$OUT/client_cmd.json')))" > "$OUT/client.out" 2>&1 & )
for i in $(seq 1 60); do sleep 5; grep -q 'PackTester joined the game' "$LOG" && { echo "CLIENT_JOINED after $((i*5))s"; break; }; [ $i -eq 60 ] && { echo "CLIENT NEVER JOINED"; tail -20 "$GD/logs/latest.log"; exit 1; }; done
sleep 25
MARK=$(wc -l < "$LOG"); echo "log mark $MARK"
$C cmd "valley anchor"; $C cmd "kubejs stages list PackTester"
# place the town anchor and a home waystone near the player so anchor-relative finales have a target
$C cmd 'execute as PackTester at PackTester run setblock ~2 ~ ~2 valley:town_anchor'
$C cmd 'execute as PackTester at PackTester run setblock ~-2 ~ ~-2 waystones:waystone'
sleep 3; $C cmd "valley anchor"
n=0
tools/venv/bin/python tools/scripts/quest_order.py | while IFS=$'\t' read -r key id title ch; do
  n=$((n+1)); echo "$key $id $title" >> "$OUT/completed.txt"
  echo "ftbquests change_progress PackTester complete $id" > "$ROOT/scratch/server.in"; sleep 1.2
  case "$key" in q19|q37|q56|q75|q91) sleep 12;; esac
done
sleep 15
echo "=== SUMMARY"; echo "quests completed: $(wc -l < "$OUT/completed.txt")"
tail -n +"$MARK" "$LOG" > "$OUT/playthrough.log"
echo "errors/warnings of interest:"; grep -nE 'Unknown or incomplete command|Incorrect argument|No such|does not exist|Failed to|Exception|ERROR|\[KubeJS Server\].*(error|Error)|Unknown item|Unknown block|Could not|is not a valid|Expected' "$OUT/playthrough.log" | grep -viE 'ModernFix|Missing texture|datafixer|VersionChecker' | head -80
echo "quest reward commands that ran:"; grep -cE 'valley|easy_npc|place template|function valley' "$OUT/playthrough.log"
$C cmd "valley lamps"; $C cmd "easy_npc list"; sleep 3; grep -E 'Type: easy_npc' "$OUT/../../server/logs/latest.log" | wc -l
$C cmd "save-all"; sleep 5
pkill -f 'cpw.mods.bootstraplauncher'; sleep 3; $C stop
