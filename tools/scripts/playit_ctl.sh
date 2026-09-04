#!/bin/zsh
# playit.gg tunnel control for Little Kettle Valley.
#   playit_ctl.sh start   - start the playitd daemon (needs tools/playit/playit.secret from a claim)
#   playit_ctl.sh stop    - stop it
#   playit_ctl.sh status  - daemon + tunnel status
#   playit_ctl.sh claim   - print a fresh claim link (first-time setup or after `reset`)
#   playit_ctl.sh log     - tail the daemon log
# Binaries were built from https://github.com/playit-cloud/playit-agent at tag v1.0.10
# (no macOS release asset exists): tools/playit-src -> cargo build --release -p playit-cli -p playitd
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
P="$ROOT/tools/playit"
CLI="$P/playit-cli"; D="$P/playitd"; SECRET="$P/playit.secret"; PIDF="$P/playitd.pid"; LOG="$P/playitd.log"

running() { [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; }

case "${1:-status}" in
  start)
    if running; then echo "playitd already running (pid $(cat "$PIDF"))"; exit 0; fi
    [ -s "$SECRET" ] || { echo "no secret at $SECRET; run: $0 claim"; exit 1; }
    nohup "$D" --secret-path "$SECRET" -l "$LOG" >> "$P/playitd.out" 2>&1 &
    echo $! > "$PIDF"; sleep 2
    running && echo "playitd started (pid $(cat "$PIDF"))" || { echo "failed to start; see $LOG"; exit 1; }
    ;;
  stop)
    running && kill "$(cat "$PIDF")" && echo "stopped" || echo "not running"; rm -f "$PIDF"
    ;;
  status)
    running && echo "playitd: running (pid $(cat "$PIDF"))" || echo "playitd: not running"
    "$CLI" status 2>&1 | head -20 || true
    ;;
  claim)
    CODE="$("$CLI" claim generate | tr -d '[:space:]')"
    echo "Open this link, sign in to playit.gg (free), and approve the agent:"
    "$CLI" claim url --name little-kettle-valley "$CODE"
    echo "Waiting for approval..."
    umask 077
    "$CLI" claim exchange --wait 0 "$CODE" | tee "$SECRET.raw" | grep -E '^[0-9a-fA-F]{32,}$' | tail -1 > "$SECRET.tmp"
    [ -s "$SECRET.tmp" ] && mv "$SECRET.tmp" "$SECRET" || { echo "no secret in the exchange output (see $SECRET.raw)"; exit 1; }
    echo "secret saved to $SECRET"; "$0" start
    ;;
  log) tail -n 40 "$LOG" ;;
  *) echo "usage: $0 start|stop|status|claim|log"; exit 1 ;;
esac
