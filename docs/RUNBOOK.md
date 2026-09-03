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
Rebuilds `dist/LittleKettleValley.zip` and uploads it to the GitHub release. Friends who already installed do not need it; the pack itself updates from GitHub on every launch after `git push`.

## Update the pack
1. Edit files under `pack/` (mods via `tools/packwiz`, configs, quests, KubeJS).
2. `cd pack && ../tools/packwiz refresh`
3. Test: `server_ctl.sh start` then `wait`, watch for errors, `stop`.
4. `git add -A && git commit -m "what changed"` then `git push`.
5. Friends get the update automatically on their next launch. The server gets it by re-running the installer:
   `cd server && ../tools/jdk17/Contents/Home/bin/java -jar ../tools/packwiz-installer-bootstrap.jar -g -s server ../pack/pack.toml`

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
3. `cd pack && ../tools/packwiz refresh`, then `git add -A && git commit -m "..." && git push`.
4. On the running server, without restarting: re-run the installer (`cd server && ../tools/jdk17/Contents/Home/bin/java -jar ../tools/packwiz-installer-bootstrap.jar -g -s server ../pack/pack.toml`), then in the console `ftbquests reload`. Everyone online sees the new quests immediately; quest text comes from the server.
5. KubeJS recipe or script edits: same install, then `kubejs reload server_scripts`. Datapack functions: `reload`.
   * `kubejs reload server_scripts` does NOT rebuild the command tree: `/valley` keeps running the functions from the last full server start. If you changed anything inside `/valley finale`, `/valley scene`, `/valley check` or `/valley standing`, restart the server or the reload will look like it did nothing.

**One rule:** in-game edit mode writes to the server's quest files, and the compiler overwrites those from the JSON. Use edit mode to unstick people, use the JSON for anything you want to keep.
