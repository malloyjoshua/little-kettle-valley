#!/bin/zsh
# Feed a file of console commands into the server FIFO in 30-line chunks, so a
# large batch can never leave a half-written pipe behind if the caller is
# interrupted.
ROOT="/Users/joshuamalloy/Desktop/1. Projects/Minecraft"
FIFO="$ROOT/scratch/server.in"
TMP=$(mktemp -d)
split -l 30 "$1" "$TMP/chunk."
for f in "$TMP"/chunk.*; do cat "$f" > "$FIFO"; sleep 0.7; done
rm -rf "$TMP"
sleep 2
echo "sent $(wc -l < "$1") lines"
