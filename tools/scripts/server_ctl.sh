#!/bin/zsh
# Usage: server_ctl.sh start|stop|cmd "<command>"|wait|status
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; SRV="$ROOT/server"; FIFO="$ROOT/scratch/server.in"; PIDF="$ROOT/scratch/server.pid"
case "$1" in
  start)
    rm -f "$FIFO"; mkfifo "$FIFO"; cd "$SRV"; rm -rf logs crash-reports
    ( tail -f "$FIFO" | ./start.sh > "$ROOT/scratch/server.out" 2>&1 ) & disown
    for i in $(seq 1 15); do sleep 2; pgrep -f 'forge/1.20.1.*unix_args' | head -1 > "$PIDF"; [ -s "$PIDF" ] && break; done
    echo "started pid $(cat $PIDF)";;
  wait)
    for i in $(seq 1 120); do sleep 5
      grep -q 'Done (' "$SRV/logs/latest.log" 2>/dev/null && { echo "DONE after $((i*5))s"; exit 0; }
      [ -d "$SRV/crash-reports" ] && [ -n "$(ls -A $SRV/crash-reports 2>/dev/null)" ] && { echo "CRASH after $((i*5))s"; exit 1; }
      [ -s "$PIDF" ] || pgrep -f 'forge/1.20.1.*unix_args' | head -1 > "$PIDF"
      [ -s "$PIDF" ] && ! kill -0 "$(cat $PIDF)" 2>/dev/null && { echo "EXITED after $((i*5))s"; exit 1; }
    done; echo TIMEOUT; exit 1;;
  cmd) echo "$2" > "$FIFO"; sleep 2;;
  stop) echo "stop" > "$FIFO"; for i in $(seq 1 24); do sleep 5; kill -0 "$(cat $PIDF)" 2>/dev/null || { echo "stopped after $((i*5))s"; pkill -f "tail -f $FIFO"; exit 0; }; done; echo "force kill"; kill -9 "$(cat $PIDF)"; pkill -f "tail -f $FIFO";;
  status) kill -0 "$(cat $PIDF)" 2>/dev/null && echo running || echo stopped;;
esac
