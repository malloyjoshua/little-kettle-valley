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
2. `server_ctl.sh cmd "whitelist add <name>"`
3. Send them `docs/INSTALL.md` and the server address.

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
