#!/bin/zsh
# Zip the world to server/backups/, keep the newest 20. Safe to run while the server is up
# (it asks the server to flush first if the command pipe exists).
cd "$(dirname "$0")"
FIFO="../scratch/server.in"
if [ -p "$FIFO" ] && pgrep -f 'forge/1.20.1.*unix_args' >/dev/null; then echo "save-all flush" > "$FIFO"; sleep 5; fi
mkdir -p backups
STAMP=$(date +%Y-%m-%d_%H%M)
tar -czf "backups/world-$STAMP.tgz" world 2>/dev/null && echo "backup: backups/world-$STAMP.tgz ($(du -h backups/world-$STAMP.tgz | cut -f1))"
ls -t backups/world-*.tgz | tail -n +21 | xargs rm -f 2>/dev/null
