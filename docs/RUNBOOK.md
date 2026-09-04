# Runbook

Everything lives in `~/Desktop/1. Projects/Minecraft/`. Nothing here touches the NAS.

## Start the server
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" start
```
Wait for `DONE` (about 30 seconds warm, 2 minutes cold):
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" wait
```

## Stop the server
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" stop
```
This saves the world first. Never kill the Java process directly while people are online.

## Send a console command
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" cmd "whitelist add SomePlayer"
```

## Back up the world
```bash
"$HOME/Desktop/1. Projects/Minecraft/server/backup.sh"
```
Backups land in `server/backups/`, newest 20 kept. Point Time Machine or Backblaze Personal at the Minecraft folder so backups leave the machine.

## Restore a backup
1. Stop the server.
2. `mv server/world server/world.broken`
3. `tar -xzf server/backups/world-<stamp>.tgz -C server/`
4. Start the server.

## Add a friend
1. Get their exact Minecraft username.
2. `server_ctl.sh cmd "whitelist add <name>"` (and `op <name>` only if they should run commands)
3. Send them `dist/LittleKettleValley.zip` (or the GitHub release link) plus `docs/INSTALL.md` and the server address.

## Publish a new friend zip
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/release.sh"
```
Rebuilds all four release assets — see [Installers](#installers) for what it does in what order and why. Friends who already installed do not need any of it; the pack itself updates from GitHub on every launch after `git push`.

## Update the pack
1. Edit files under `pack/` (mods via `tools/packwiz`, configs, quests, KubeJS).
2. `cd pack && ../tools/packwiz refresh`
3. Test: `server_ctl.sh start` then `wait`, watch for errors, `stop`.
4. Stage by path — never `git add -A`, `dist/` and `server/` collect large local-only junk that must not land in a commit:
   `git add pack/ story/ docs/ && git commit -m "what changed"` then `git push`. Narrow it further when only some of those changed; `git status --short` before and `git show --stat` after.
5. Friends get the update automatically on their next launch. The server gets it with the sync script, which also clears the quest files the game rewrites on its own so they never shadow an update:
   `"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/sync_server.sh"`

## Roll back a bad update
```bash
git revert HEAD && git push
```
Friends pick up the revert on next launch.

## Logs
- Server: `server/logs/latest.log`
- Crashes: `server/crash-reports/`
- Client (Prism): right-click the instance, "Minecraft Folder", then `logs/latest.log`

## Let friends connect without port forwarding (playit.gg, free)
1. Download the macOS agent from https://github.com/playit-cloud/playit-agent/releases (playit-darwin-arm64), put it in `tools/`, `chmod +x`.
2. Run `tools/playit-darwin-arm64` once. It prints a claim link. Open it, sign in (free account), name the agent.
3. In the playit dashboard add a tunnel: type Minecraft Java, local address `127.0.0.1:25565`. It gives a hostname like `something.playit.gg`. That is the server address friends use.
4. Keep the agent running whenever the server is up (a second terminal, or a launchd job later).

## Automated playthrough (proves every quest reward and finale still works after a change)
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/playthrough.sh"
```
It temporarily sets `online-mode=false`, boots a fresh world, joins the offline test client, completes all quests in order from the console, and prints every command error. It restores `online-mode=true` when it exits. Do not run it while people are playing.

## Fixing the story while people are playing

**Someone is stuck on a quest right now (no files, no restart):**
1. Make yourself op once: `server_ctl.sh cmd "op YourName"`.
2. In the game, open the quest book and run `/ftbquests editing_mode` in chat. Right-click any quest for Complete or Reset. Run the command again to leave edit mode.
3. Missing a stage the story should have given: `/kubejs stages add PlayerName stage_name` (stage names are in `story/quests/*.json`).
4. A finale or scene that did not fire: `/valley finale act2`, `/valley scene q59`. If the town anchor was never set: `/valley anchor set x y z`.
   * Each act is a chain of timed beats and only the last one marks the act done, so re-running a half-finished finale is safe: it skips the beats that already played and runs the ones that did not. If the act is already marked done but a payoff never landed (no spring after the Longest Night, the world border never came off), use `/valley finale act4 force` — same skipping, but it ignores the done flag.
   * The act's ground is force-loaded for the length of the build and released when the last beat ends, so it no longer matters where anybody is standing when the card is claimed.
5. **Bram is not at the mill** (Q12 wants his token and there is nobody to take it from): `/valley scene bram`. It also cuts the mill race Q16 needs. It is latched once per world, so if it already ran and he is still missing, `/data remove` is not the answer — re-run the import by hand: `easy_npc preset import data valley:easy_npc/preset/bram.npc.snbt <x> <y> <z>`.
6. **Q1 will not tick after reading the letter** (the book opened, the quest stayed grey): Q1's task is a checkmark — open the quest book and click the box. The right-click listener is a convenience, not a gate. The letter itself is a vanilla written book titled *Josie's Letter*; a replacement is `give PlayerName written_book{title:"Josie's Letter",author:"Josie Kettle"}` plus a re-read, or just tick the box.
7. **The ruined Kettle farm is not there** (Q2 has nowhere to put the waystone): `/valley anchor` prints Home when it is set; the ruin's own hearthstone is in `world/kubejs_persistent_data.nbt` under `valley_ruin`. To rebuild it: `execute positioned <x> <y> <z> run function valley:setup/place_ruin`, where `<x> <y> <z>` is where you want the waystone to go. It is placed once per world on the first player's first join.

**Change text, tasks, rewards, or dependencies (permanent):**
1. Edit `story/quests/act*.json` (or `oda.json`). The format is `docs/QUEST_FORMAT.md`.
2. Compile: `tools/venv/bin/python tools/scripts/compile_quests.py story/quests pack/config/ftbquests/quests scratch/ids_plus.json --strict`. It refuses unknown item ids.
3. `cd pack && ../tools/packwiz refresh`, then stage by path (not `-A`): `git add story/quests pack/config/ftbquests && git commit -m "..." && git push`.
4. On the running server, without restarting: run `tools/scripts/sync_server.sh`, then in the console `ftbquests reload`. Everyone online sees the new quests immediately; quest text comes from the server.
5. KubeJS recipe or script edits: same install, then `kubejs reload server_scripts`. Datapack functions: `reload`.
   * `kubejs reload server_scripts` does NOT rebuild the command tree: `/valley` keeps running the functions from the last full server start. If you changed anything inside `/valley finale`, `/valley scene`, `/valley check` or `/valley standing`, restart the server or the reload will look like it did nothing.

**One rule:** in-game edit mode writes to the server's quest files, and the compiler overwrites those from the JSON. Use edit mode to unstick people, use the JSON for anything you want to keep.

## Installers

Three friend-facing assets plus a PDF guide, all attached to the GitHub release tagged `friends`. One command rebuilds and re-uploads everything:
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/release.sh"
```
In order: rebuilds the zip → **commits and pushes it** (CI builds the `.exe` from the copy on `main`, so this has to happen first) → rebuilds the dmg → triggers the Windows `installers.yml` workflow on GitHub Actions and waits for it (that job builds the `.exe` on a real Windows runner, silent-installs it four ways, and uploads it to the release itself) → rebuilds the install guide PDF into a new `dist/vN/` folder → uploads the zip + dmg + PDF (the `.exe` is already on the release by that point). Takes several minutes end to end because of the Windows CI run.

### Rebuild one asset at a time

- **Zip** (manual/any-launcher import): `rm -f dist/LittleKettleValley.zip && (cd dist/CozyTech && zip -qr ../LittleKettleValley.zip . -x '.DS_Store' -x '*/.DS_Store' -x '__MACOSX/*')` — same line `release.sh` runs. Then `git add dist/LittleKettleValley.zip && git commit && git push`, because the Windows build reads it from `main`.
- **macOS disk image**: `tools/venv/bin/python installers/macos/build_dmg.py` → `dist/LittleKettleValley.dmg`. Add `--verify-only` to re-check an already-built image (codesign/notarization/hashes) without rebuilding it.
- **Windows installer**: `gh workflow run installers.yml --ref main` (or push a tag matching `installer-*`), then `gh run watch <run-id> --exit-status`. It stages the payload with `installers/windows/stage.py`, compiles `installers/windows/LittleKettleValley.iss` with Inno Setup on the runner, silent-installs + silent-uninstalls it as a smoke test, and uploads the `.exe` to both the workflow artifact and the `friends` release. There is no macOS-side build for this one — Inno Setup only runs on Windows, which is why CI does it.
  **The runner has no `dist/CozyTech/`**, so `stage.py` builds the instance out of the committed `dist/LittleKettleValley.zip`. Rebuilding the zip locally and *not* pushing it means CI silently ships the previous instance — `release.sh` commits and pushes the zip before it triggers the workflow for exactly this reason.
- **Install guide PDF**: `tools/venv/bin/python tools/scripts/install_guide_pdf.py "dist/vN/Little Kettle Valley - Install Guide.pdf"` — pick the next unused `vN` (never overwrite an existing version; the whole `dist/v*/` prefix is gitignored, so these live locally and on the release only). Render a quick visual check before shipping: `pdftoppm -png -r 150 "dist/vN/Little Kettle Valley - Install Guide.pdf" /tmp/page` then look at the PNGs — reportlab gives no warning when text or a numbered-step circle collides with something else on the page.

### How much memory the installer gives the game

`MinMemAlloc` is always 1024. `MaxMemAlloc` is not baked in — `stage.py` writes an `@@MAX_MEM@@` token and the `.iss` `[Code]` section replaces it at install time, after reading physical RAM with `GlobalMemoryStatusEx`:

| Physical RAM | `MaxMemAlloc` |
| --- | --- |
| under 12 GB | 3072 |
| 12–24 GB | 3584 |
| over 24 GB | 4096 |

Windows reports slightly less RAM than the sticker (firmware takes a cut), so the reading is rounded up to whole GB before the table is applied — a 16 GB machine reports ~15.9 GB and still lands on 3584. If the reading fails for any reason the installer falls back to 3584 and says so in `/LOG`. The same tiers are what `docs/INSTALL.md` tells manual-import users to set by hand.

`/LKVRAMGB=<n>` makes the installer pretend the machine has *n* GB. It exists so CI can prove all three branches on one 16 GB runner (8 → 3072, 16 → 3584, 32 → 4096, plus an unforced install checked against the runner's real RAM); it is not documented for players.

The **Mac disk image is a separate number**: `MAX_MEM_MB = 3072` near the top of `installers/macos/build_dmg.py`, baked into the instance because a dmg has no install-time code to run. It is set for an 8 GB Air; on a bigger Mac raise it in Prism (Edit → Settings → Memory). The tracked `dist/LittleKettleValley.zip` carries 3584, matching the middle tier.

### Where they live
- `dist/LittleKettleValley.zip` — **tracked in git, on purpose.** It is both a release asset and the build input CI uses to make the `.exe` (see above), so it has to be on `main`. `release.sh` commits and pushes it; if you rebuild it by hand, commit it by hand: `git add dist/LittleKettleValley.zip`.
- `dist/LittleKettleValley.dmg` — gitignored (47 MB of Prism Launcher). Local build output, re-uploaded with `--clobber` each release.
- `dist/vN/Little Kettle Valley - Install Guide.pdf` — the `dist/v*/` prefix is gitignored; a version only reaches the repo if it is force-added, and `dist/v2/…` is the one in git today while the release currently serves `dist/v3/…`. Every version uploads under the same asset name, so the release always serves the newest guide — but do not assume the tracked PDF is the one that shipped. `installers/RELEASE-NOTES.md` records which is which.
- `installers/windows/build/out/LittleKettleValley-Setup.exe` — CI-only output; `installers/windows/build/` is gitignored and `dist/*.exe` is too. The release asset is the copy CI uploads. Its size and sha256 for each release are recorded in `installers/RELEASE-NOTES.md`.
- `installers/RECON-prism.md`, `installers/RECON-instance.md` — the source-level audits of Prism Launcher and of the shipped instance that every non-obvious decision in the `.iss` and in `stage.py` cites. Read these before changing either.
- Release page: `gh release view friends --web` or https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends

### When Prism or Java releases move

- **Prism Launcher version**: pinned by URL + sha256 in *two* places that need to move together — `PRISM_DMG_URL`/`PRISM_DMG_SHA256` near the top of `installers/macos/build_dmg.py`, and the portable-zip URL/hash near the top of `installers/windows/stage.py`. Update both to the new version, then just run the builds — each one aborts loudly on a sha256 mismatch rather than shipping unverified bytes, so a bad copy-paste fails fast instead of shipping quietly. After bumping the Mac side, `build_dmg.py` re-verifies the new `.app`'s codesign/notarization itself as part of the build.
- **Java on Windows**: `installers/windows/stage.py` always pulls Adoptium's "latest GA" Temurin 17 build via their API and verifies the download's own checksum before extracting — no pin to maintain, but it does mean a rebuild next month can bundle a newer 17.x point release than today's. Say the word if that should be pinned instead.
- **Java on Mac**: not bundled at all — Prism's `AutomaticJavaDownload`/`AutomaticJavaSwitch` are left on in the shipped instance config, so Prism fetches its own JRE on first launch. Nothing to update here when Java moves.
