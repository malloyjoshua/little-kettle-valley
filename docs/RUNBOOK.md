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
