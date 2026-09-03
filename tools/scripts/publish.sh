#!/bin/zsh
# One-time: create the GitHub repo, enable Pages, push, and print the packwiz URL friends use.
# Run only after Josh approves a public repo. Everything here is reversible (delete the repo).
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
REPO="${1:-copper-kettle-valley}"
gh repo create "$REPO" --public --source=. --remote=origin --push --description "Copper Kettle Valley: a cozy story modpack for Forge 1.20.1 (packwiz)"
# GitHub Pages from the main branch root so pack/pack.toml is served over HTTPS
gh api -X POST "repos/{owner}/$REPO/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || gh api -X PUT "repos/{owner}/$REPO/pages" -f 'source[branch]=main' -f 'source[path]=/' >/dev/null
OWNER=$(gh api user --jq .login)
URL="https://$OWNER.github.io/$REPO/pack/pack.toml"
echo "packwiz URL: $URL"
# point the friend instance at the URL
INST="$HOME/Library/Application Support/PrismLauncher/instances/CozyTech/instance.cfg"
sed -i '' "s|PreLaunchCommand=.*|PreLaunchCommand=\"\$INST_JAVA\" -jar packwiz-installer-bootstrap.jar -g -s client \"$URL\"|" "$INST"
echo "Prism instance now updates from GitHub on every launch. Export it from Prism (right-click > Export) as CozyTech.zip for friends."
