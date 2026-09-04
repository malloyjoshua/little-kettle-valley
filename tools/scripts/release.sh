#!/bin/zsh
# Rebuild every friend-facing asset and attach them to the GitHub release "friends"
# (created on first run): the manual-import zip, the macOS disk image, the Windows
# one-click installer (built by CI on a real Windows runner), and the install guide PDF.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"

echo "==> Rebuilding dist/LittleKettleValley.zip"
rm -f dist/LittleKettleValley.zip; (cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store')

echo "==> Rebuilding dist/LittleKettleValley.dmg"
tools/venv/bin/python installers/macos/build_dmg.py

echo "==> Triggering the Windows installer workflow and waiting for it"
gh workflow run installers.yml
# gh workflow run is fire-and-forget; give the run a moment to be scheduled, then find it.
sleep 5
RUN_ID="$(gh run list --workflow installers.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
echo "    run id: $RUN_ID"
gh run watch "$RUN_ID" --exit-status

echo "==> Rebuilding the install guide PDF (new version, dist/v2/ etc. — never overwrite an existing v*/)"
N=1; while [ -d "dist/v$N" ]; do N=$((N + 1)); done
mkdir -p "dist/v$N"
tools/venv/bin/python tools/scripts/install_guide_pdf.py "dist/v$N/Little Kettle Valley - Install Guide.pdf"

echo "==> Uploading zip + dmg + PDF to the release (the .exe was already uploaded by the workflow above)"
gh release view friends >/dev/null 2>&1 || gh release create friends --title "Little Kettle Valley: launcher instance" --notes "Windows: LittleKettleValley-Setup.exe. Mac: LittleKettleValley.dmg. Any launcher: import LittleKettleValley.zip into Prism Launcher. Guide: docs/INSTALL.md" dist/LittleKettleValley.zip
gh release upload friends dist/LittleKettleValley.zip dist/LittleKettleValley.dmg "dist/v$N/Little Kettle Valley - Install Guide.pdf" --clobber
gh release view friends --json url,assets --jq '.url, (.assets[] | "  \(.name)  \(.size) bytes")'
