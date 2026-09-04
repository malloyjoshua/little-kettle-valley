#!/bin/zsh
# Rebuild every friend-facing asset and attach them to the GitHub release "friends"
# (created on first run): the manual-import zip, the macOS disk image, the Windows
# one-click installer (built by CI on a real Windows runner), and the install guide PDF.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"

echo "==> Rebuilding dist/LittleKettleValley.zip"
rm -f dist/LittleKettleValley.zip
# Finder droppings: .DS_Store at the root, in any subfolder, and the __MACOSX sidecar tree
# that some archivers add. Friends import this zip straight into Prism, so it ships clean.
(cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store' -x '*/.DS_Store' -x '__MACOSX/*')

# The Windows installer is built on a GitHub runner, which has no dist/CozyTech -- stage.py falls
# back to this committed zip. So the zip has to be on main BEFORE the workflow is triggered, or the
# .exe gets built around the previous instance.
echo "==> Committing dist/LittleKettleValley.zip (the Windows CI build reads it from main)"
git add dist/LittleKettleValley.zip
if git diff --cached --quiet -- dist/LittleKettleValley.zip; then
  echo "    unchanged"
else
  git commit -m "Refresh dist/LittleKettleValley.zip for the release"
  echo "    committed"
fi
git push origin main

echo "==> Rebuilding dist/LittleKettleValley.dmg"
tools/venv/bin/python installers/macos/build_dmg.py

echo "==> Triggering the Windows installer workflow and waiting for it"
# gh workflow run is fire-and-forget and prints no run id, so we have to find the run it made.
# Take the timestamp first (30s back to absorb clock skew against GitHub) and then pick the
# EARLIEST run created after it -- "most recent run" races with anything already in flight.
SINCE="$(date -u -v-30S +%Y-%m-%dT%H:%M:%SZ)"
gh workflow run installers.yml --ref main
RUN_ID=""
for _ in $(seq 1 36); do
  RUN_ID="$(gh run list --workflow installers.yml --limit 30 \
    --json databaseId,createdAt,status \
    --jq "[.[] | select(.createdAt >= \"$SINCE\")] | sort_by(.createdAt) | .[0].databaseId // empty")"
  if [ -n "$RUN_ID" ]; then break; fi
  sleep 5
done
if [ -z "$RUN_ID" ]; then
  echo "!! no installers.yml run appeared after $SINCE — check https://github.com/malloyjoshua/little-kettle-valley/actions" >&2
  exit 1
fi
echo "    run id: $RUN_ID  (queued after $SINCE)"
gh run watch "$RUN_ID" --exit-status

echo "==> Rebuilding the install guide PDF (new version, dist/v2/ etc. — never overwrite an existing v*/)"
N=1; while [ -d "dist/v$N" ]; do N=$((N + 1)); done
mkdir -p "dist/v$N"
tools/venv/bin/python tools/scripts/install_guide_pdf.py "dist/v$N/Little Kettle Valley - Install Guide.pdf"

echo "==> Uploading zip + dmg + PDF to the release (the .exe was already uploaded by the workflow above)"
gh release view friends >/dev/null 2>&1 || gh release create friends --title "Little Kettle Valley: launcher instance" --notes "Windows: LittleKettleValley-Setup.exe. Mac: LittleKettleValley.dmg. Any launcher: import LittleKettleValley.zip into Prism Launcher. Guide: docs/INSTALL.md" dist/LittleKettleValley.zip
gh release upload friends dist/LittleKettleValley.zip dist/LittleKettleValley.dmg "dist/v$N/Little Kettle Valley - Install Guide.pdf" --clobber
gh release view friends --json url,assets --jq '.url, (.assets[] | "  \(.name)  \(.size) bytes")'
