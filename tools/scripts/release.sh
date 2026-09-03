#!/bin/zsh
# Rebuild the friend zip and attach it to the GitHub release "friends" (created on first run).
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
rm -f dist/LittleKettleValley.zip; (cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store')
gh release view friends >/dev/null 2>&1 || gh release create friends --title "Little Kettle Valley: launcher instance" --notes "Import this zip into Prism Launcher (Add Instance > Import). It installs the pack and keeps it updated. Guide: docs/INSTALL.md" dist/LittleKettleValley.zip
gh release upload friends dist/LittleKettleValley.zip --clobber
gh release view friends --json url --jq .url
