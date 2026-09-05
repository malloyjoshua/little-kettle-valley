# Runbook

Everything lives in `~/Desktop/1. Projects/Minecraft/`. Nothing here touches the NAS.

## The world

**Little Kettle Valley is not generated. It is shipped.** Every friend opens the same valley
Josh built — the same seed, the same terracing, the same forty unlit lamp posts, the same
gravel in the cellar floor. Nobody ever sees "Create New World".

### Where it lives

| Copy | Path | What it is |
| --- | --- | --- |
| **Source of truth** | `world-master/` | The product. 68 files, 55 MB. Everything else is a copy of this. Untracked (it is 55 MB of region files) but zipped beside it as `world-master.zip`. |
| Singleplayer | `pack/saves/Little Kettle Valley/` | The copy that ships. Byte-identical to `world-master/`, minus `level.dat_old`. Tracked in git; packwiz installs it into every friend's `.minecraft/saves/`. |
| Server | `server/world/` | The live copy. Byte-identical to `world-master/` today; it diverges the moment anyone plays on it, and **that divergence is the save.** |

**Never delete `server/world/`.** It is not a build artefact and it is not reproducible —
it is everyone's progress. `.gitignore` keeps it out of git precisely because it is
runtime state, not source. If it ever has to be replaced, back it up first
(`server/backup.sh`) and then restore from `world-master/`, in that order.

`server/backup.sh` covers it: it flushes the running server, tars `server/world` into
`server/backups/world-<stamp>.tgz`, and keeps the newest 20. That is the only thing standing
between a bad afternoon and everybody's winter. Point Time Machine or Backblaze at the
Minecraft folder so those backups leave the machine.

### Why the shipped world does not eat a player's save

Every one of the 68 files under `saves/` is marked `preserve = true` in `pack/index.toml` —
the same flag `options.txt` carries, and for a much sharper reason. packwiz re-hashes every
indexed file on every launch and rewrites anything that no longer matches. A world file stops
matching the moment a player walks anywhere. Without the flag, the second launch would hand
them our copy back: the cottage un-built, the lamps unlit, the chests they filled gone.

`preserve` makes it write-once-if-missing. Verified against the shipped
`packwiz-installer.jar`, both directions:

* install into an empty folder → all 68 files land, byte-identical to `world-master/`;
* edit the local copy, change the file upstream so the index hash moves, relaunch →
  the installer prints `level.dat pending (you should never see this...)` and **leaves the
  player's file alone**, while a control file with the flag stripped is silently overwritten.

The flag has to be re-applied after `packwiz refresh`, which rewrites the `[[files]]` blocks
without inventing keys of its own:

```bash
tools/venv/bin/python tools/scripts/mark_preserve.py            # refresh already run: mark, then re-point pack.toml
tools/venv/bin/python tools/scripts/mark_preserve.py --refresh  # refresh, mark, re-point — the whole invariant
tools/venv/bin/python tools/scripts/mark_preserve.py --check    # release gate; exits 1 if any saves/ entry is bare
```

`release.sh` runs the `--refresh` form, so a release can never ship an unflagged world.

**The consequence, and it is the important one:** *we can no longer patch the world of
somebody who has already started playing.* Fixing a block in `world-master/` and pushing it
reaches fresh installs only. Anyone mid-story keeps the valley they have. That is the right
trade — the alternative deletes their game — but it means the world has to be right before it
ships, not after. Fixes for a live player are commands (`/valley scene …`, `/valley finale …
force`, `/valley keepsake …`), never files.

### How a friend resets their singleplayer copy

Their world is one folder. Deleting it makes packwiz lay a fresh valley down on the next
launch — no reinstall, no re-download of the mods.

1. Quit Minecraft **and** the launcher.
2. Prism: right-click **Little Kettle Valley** → **Minecraft Folder**.
3. Delete `saves/Little Kettle Valley/`. (Rename it to `saves/old-valley/` instead if they
   might want it back — a renamed folder still opens from the world list.)
4. Launch. The pre-launch step re-downloads the 55 MB world and the instance opens straight
   into a brand-new day one.

Quest progress is separate and does **not** reset: FTB Quests keeps it in the world folder, so
deleting the folder does clear it — that is the point — but their *account*, mods and settings
are untouched. `options.txt` is preserved too, so their keybinds and video settings survive.

### How the instance opens it by itself

Neither installer leaves anybody at the main menu. The Prism instance carries two keys:

```ini
JoinServerOnLaunch=true
JoinWorldOnLaunch=Little Kettle Valley
```

Prism 11.1.0 ignores both unless `JoinServerOnLaunch` is true; it then prefers
`JoinServerOnLaunchAddress` and only falls through to the world when that key is absent — so
the address key must **not** be written. It becomes `--quickPlaySingleplayer "Little Kettle
Valley"` on the game's command line, gated on the profile trait
`feature:is_quick_play_singleplayer`, which 1.20.1 carries.

The value is the **save folder name**, not `level.dat`'s `LevelName`. They are the same string
today. Rename the folder and this has to follow the folder, not the display name.

It is set in three places that must agree, and two of them assert it at build time:
`dist/CozyTech/instance.cfg` (the friend zip, and what the Windows CI reads),
`installers/macos/build_dmg.py` (`JOIN_WORLD_FOLDER`, re-written into the tuned cfg and
asserted into the built zip), and `installers/windows/stage.py` (`JOIN_WORLD_FOLDER`, checked
before the payload is handed to Inno Setup).

Failure is benign by design: a missing world or a wrong name drops the player at the main menu
with the world still sitting in the list. It cannot fail a launch.

### Rebuilding the world from the planner

Only ever needed when the town layout itself changes. It replaces the world, so it is a
before-anyone-plays operation.

```bash
scratch/master_build.sh all      # pregen, plan, build  (about an hour, supervised)
```

Three phases, and the order is not optional:

1. `pregen` — a fresh world on seed `5369984945557223422`, Chunky radius 512, world spawn set,
   saved and snapshotted to `scratch/pregen/`. Pristine terrain, nothing of the valley in it.
2. `plan` — `tools/scripts/plan_town.py` reads the template NBTs out of the installed mod jars
   and solves the layout **against `scratch/pregen/`**, writing `media/town_plan.json`,
   `pack/kubejs/server_scripts/town_plan.js` and `pack/kubejs/data/valley/valley_sites.json`.
   It must read the pregen, not a built world: it terraces each pad onto the median surface
   under its own footprint, so run against a built world it terraces the town onto its own
   previous pads.
3. `build` — restores the pregen into `server/world`, boots, runs `/valley build all`, saves,
   stops, and snapshots to `world-master/` and `world-master.zip`.

Then, in order:

```bash
scratch/nature_check.py --world world-master --baseline scratch/pregen   # 9/9 required
tools/scripts/playthrough.sh                                             # 135 quests, 15 residents, 7 world asserts
rsync -a --exclude playerdata --exclude stats --exclude advancements \
      --exclude session.lock --exclude level.dat_old \
      world-master/ "pack/saves/Little Kettle Valley/"
tools/venv/bin/python tools/scripts/mark_preserve.py --refresh
```

and commit `pack/saves/`, `pack/index.toml`, `pack/pack.toml` and the two generated planner
files together. Never hand-edit `town_plan.js` or `valley_sites.json`.

> ⚠️ `scratch/` is gitignored, so `master_build.sh` and `nature_check.py` are **not in the
> repo** — they live only on this Mac. `plan_town.py` and `playthrough.sh` are tracked.
> Moving the two drivers into `tools/scripts/` is an open job.

A handful of the shipped world's details were applied to `world-master/` directly rather than
through the planner (the farm-yard scatter, the bare-earth patches, the hostile sweep) — see
`media/look/NOTES.md`. **Those are not in `plan_town.py` and a rebuild loses them.**

### Cheats are off

`level.dat` ships `allowCommands = 0`, so a singleplayer friend is permission level 0. That is
deliberate and it costs nothing that matters: everything in the "Lost something" section below
— `/valley keepsake`, `/valley book`, `/valley intro`, `/valley letter` — is registered at
`hasPermission(0)` and works for them. Only the op-level repairs (`/valley finale`,
`/valley scene`, `/valley anchor set`, `/ftbquests editing_mode`) need cheats, and those are
Josh's tools on the server. A friend who genuinely needs one can **Open to LAN → Allow
Cheats → Start LAN World** for that session.

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
2. `cd pack && ../tools/packwiz refresh` — or, if you touched anything under `pack/saves/`,
   `tools/venv/bin/python tools/scripts/mark_preserve.py --refresh` instead, which refreshes,
   re-applies `preserve = true` to the world files and re-points `pack.toml`. A bare refresh
   leaves the world unflagged and the next update would overwrite every player's save.
3. Test: `server_ctl.sh start` then `wait`, watch for errors, `stop`.
4. Stage by path — never `git add -A`, `dist/` and `server/` collect large local-only junk that must not land in a commit:
   `git add pack/ story/ docs/ && git commit -m "what changed"` then `git push`. `pack/` includes
   the 55 MB shipped world under `pack/saves/`; it only shows up in a diff when the world itself
   changed, but check `git show --stat` if a commit is unexpectedly large. Narrow it further when only some of those changed; `git status --short` before and `git show --stat` after.
5. Friends get the update automatically on their next launch. The server gets it with the sync script, which also clears the quest files the game rewrites on its own so they never shadow an update:
   `"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/sync_server.sh"`

> **`pack/options.txt` and the 68 files of the shipped world are what an update does not push.** It is marked `preserve = true` in `pack/index.toml`, so packwiz writes it only when it is missing — see *Video settings* under Installers below. Change a keybind there and existing players keep the old one; only fresh installs get it. Tell them the new binding, or have them delete their `options.txt` and relaunch. The same is true, and matters far more, for `pack/saves/Little Kettle Valley/` — see [The world](#the-world).

## Roll back a bad update
```bash
git revert HEAD && git push
```
Friends pick up the revert on next launch — mods, configs, quests and scripts, all of it. The one thing a revert cannot reach is the world of somebody already playing: those files are `preserve = true`, so reverting a world change fixes fresh installs only. See [The world](#the-world).

## Logs
- Server: `server/logs/latest.log`
- Crashes: `server/crash-reports/`
- Client (Prism): right-click the instance, "Minecraft Folder", then `logs/latest.log`

## Let friends connect without port forwarding (playit.gg, free)
playit publishes no macOS binary, so the agent is built from source once (`tools/playit-src`, tag v1.0.10) into `tools/playit/` (gitignored, as is the secret).

1. First time only, claim the agent: `tools/scripts/playit_ctl.sh claim` prints a link. Open it in a browser, sign in to playit.gg (free account), approve. The script saves the secret and starts the daemon.
2. In the playit dashboard (https://playit.gg/account/agents) add a tunnel to that agent: type **Minecraft Java**, local address `127.0.0.1:25565`. It gives a hostname like `something.joinmc.link`. That is the server address friends use. Add it to `docs/INSTALL.md`.
3. Every time you play: `tools/scripts/playit_ctl.sh start` before or after the server; `status` shows the tunnel, `stop` ends it. The daemon only forwards while it runs.
Current public address (set up 2026-09-04): **`cynthia-mfc.tun.ply.gg`** (SRV record points at port 35925; agent `little-kettle-valley`, tunnel "Little Kettle Valley", local `127.0.0.1:25565`, stored in `tools/playit/public_address.txt`).
Testing note: the tunnel only forwards connections that send a Minecraft handshake naming the hostname (playit's "no raw IP" setting), so a plain TCP or netcat test times out even when everything is fine. Test with the game, or with the handshake probe in `tools/scripts/playit_probe.py`. Never run two copies of `playitd` with the same secret: they kick each other's session every second.

4. To move the agent to another machine or start over: `tools/playit/playit-cli reset`, then `claim` again.

## Automated playthrough (proves every quest reward and finale still works after a change)
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/playthrough.sh"
```
It temporarily sets `online-mode=false`, boots a fresh world, joins the offline test client, completes all quests in order from the console, and prints every command error. It restores `online-mode=true` when it exits. Do not run it while people are playing.

## Lost something

The story hands out a lot of one-of-a-kind things and none of them can be crafted. If one goes in lava, goes down with a bag nobody got back to, or gets left in a chest in a chunk nobody walks to again, **any player** can ask for it back — no op, no edit mode, no restart:

```
/valley keepsake              lists every keepsake and its short name
/valley keepsake <name>       hands that one back
```

The names tab-complete. They are:

| name | what you get back |
| --- | --- |
| `letter` | Josie's Letter — the four pages you start with (a fresh written book, re-readable for Q1) |
| `book` | The Quest Book (same as `/valley book`; also the fix for an unbound J key) |
| `journal` | Josie's Journal, the Patchouli book |
| `kettle` | The Copper Tea Kettle off the hearth |
| `deed` | The Kettle Farm Deed |
| `works_deed` | The Works Deed |
| `kettle_deed` | The Kettle Family Deed |
| `compass` | Marnie's Explorer's Compass |
| `hammer` | Bram's stone hammer |
| `stake` | The Surveyor's Stake (`valley:town_anchor`) |
| `waystone` | A Waystone — Home, or the cellar one |
| `plate_a` / `plate_b` | The two Kettle Plates |
| `survey` | Tobin's Deep Survey |
| `notes` | Josie's Turbine Notes |
| `lantern` / `hearth_lantern` | Josie's Lantern / the Hearthkeeper's Lantern |
| `trophy` | The Copper Kettle (the Act V trophy) |
| `ledger` / `catalogue` / `broom` | Oda's Ledger, Catalogue, Broom |
| `net` / `auger` | The Dredge Net, the Ice Auger |

It hands out a second copy without asking. Nothing in the pack breaks on a duplicate: every quest check reads "hold one", never "hold exactly one", and none of these is a currency. Placing the stake or the waystone a second time is handled too — the town and Home are one-per-world and the pack says so in chat instead of moving them.

Lives in `pack/kubejs/server_scripts/valley_keepsakes.js`. It registers a second `Commands.literal('valley')` root, which Brigadier merges into the tree `valley_finales.js` owns — so adding a keepsake never means touching the finale file. Adding one is a line in the `KEEPSAKES` table at the top; then `sync_server.sh` and a **full server restart** (`kubejs reload server_scripts` does not rebuild the command tree).

**Blocks that used to eat what you placed.** A story keepsake you *place* used to be a second way to lose it, because a block only gives its item back if its loot table says so:

* **The two HerbalBrews kettles** needed a pickaxe; set the Copper Tea Kettle on the hearth and take it back by hand and it was gone. Fixed in `pack/kubejs/startup_scripts/valley_blocks.js` (`requiresTool = false` — note the KubeJS property for hardness is `destroySpeed`, `block.hardness` throws at startup and takes the server down).
* **Vinery's Apple Press** ships an empty loot table and is destroyed by *any* tool. **Farm & Charm's Chicken Nest** gives the nest back only with Silk Touch — a bare hand gets wheat. Both are quest rewards. Both are overridden under `pack/kubejs/data/<mod>/loot_tables/blocks/`.

Everything else the quests ask you to place — the Waystone, the Surveyor's Stake, the Megatorch, all forty cage lamps, the Delivery Crate barrel, the energy duct, the bell, the noticeboard, the whole Create / Thermal / AE2 / Bigger Reactors / QuarryPlus set, the drawers, the beds and the furniture — was checked and already drops itself into an empty hand.

**To re-check after a mod update**, with the server up and nobody on it:

```bash
tools/scripts/server_ctl.sh cmd "setblock 0 199 0 minecraft:bedrock"
tools/scripts/server_ctl.sh cmd "setblock 0 200 0 <block>"
tools/scripts/server_ctl.sh cmd "loot spawn 0 205 0 mine 0 200 0 minecraft:air"
```

`minecraft:air` is the empty hand. The console prints `Dropped 1 [<Item>] from loot table <mod>:blocks/<block>` if it is safe, and `Dropped 0 items` / a different item if it is a trap. Two-block blocks (beds) must be tested with `[part=head]` or they read as a false positive.

## Fixing the story while people are playing

**Someone is stuck on a quest right now (no files, no restart):**
1. Make yourself op once: `server_ctl.sh cmd "op YourName"`.
2. In the game, open the quest book and run `/ftbquests editing_mode` in chat. Right-click any quest for Complete or Reset. Run the command again to leave edit mode.
3. Missing a stage the story should have given: `/kubejs stages add PlayerName stage_name` (stage names are in `story/quests/*.json`).
4. A finale or scene that did not fire: `/valley finale act2`, `/valley scene q59`. There is nothing to set up first — the anchor, Home, the hearthstone, every mark, all forty lamp posts and the cellar are constants in `pack/kubejs/data/valley/valley_sites.json` and the world is shipped with all of them in it. `/valley anchor` prints what the pack is using; `/valley anchor set x y z` writes an op override for a world that has somehow gone wrong, and is the only way any of those coordinates can move.
   * Each act is a chain of timed beats and only the last one marks the act done, so re-running a half-finished finale is safe: it skips the beats that already played and runs the ones that did not. If the act is already marked done but a payoff never landed (no spring after the Longest Night, the world border never came off), use `/valley finale act4 force` — same skipping, but it ignores the done flag.
   * The act's ground is force-loaded for the length of the build and released when the last beat ends, so it no longer matters where anybody is standing when the card is claimed.
5. **Bram is not at the mill** (Q12 wants his token and there is nobody to take it from): `/valley scene bram`. It also cuts the mill race Q16 needs. It is latched once per world, so if it already ran and he is still missing, `/data remove` is not the answer — re-run the import by hand: `easy_npc preset import data valley:easy_npc/preset/bram.npc.snbt <x> <y> <z>`.
6. **Q1 will not tick after reading the letter** (the book opened, the quest stayed grey): Q1's task is a checkmark — open the quest book and click the box. The right-click listener is a convenience, not a gate. The letter itself is a vanilla written book titled *Josie's Letter*; a replacement is `give PlayerName written_book{title:"Josie's Letter",author:"Josie Kettle"}` plus a re-read, or just tick the box.
7. **The Kettle farm is not there** — it cannot not be there. The cottage, the road, the signpost, the gate, the cellar under the kitchen and the flat grey hearthstone are all built into the shipped world, so if any of them is missing, the world is the wrong world: check `level-name` and reinstall `world-master/`. On a friend's singleplayer copy the fix is to delete `saves/Little Kettle Valley/` and relaunch — see [The world](#the-world). `/valley intro` re-points a lost player (it faces them at the hearth, hands them a fresh Kettle Farm Compass and repeats the destination); `/valley letter` hands over another copy of the letter.
8. **The cellar stairs are solid rock** (Q5 has nothing to dig): the flight is forty blocks of gravel in a two-wide patch in the kitchen floor, at the registry's `cellar.gravel` box. If it is not there, the world is wrong — same answer as 7.
9. **The iron door in the cellar never opened** (Q55 is unreachable): `/valley scene q54`. That is the only thing in the pack that opens it, and it fires from Q54's reward when the Kettle Plate goes into Halden's hands.
10. **The Works is sealed and the adit is not there** (Q65): the forty blocks of cobblestone fall are in the registry at `works.adit.fall`, in a lined shaft off the East Lane verge, with a fence, a lantern and Tobin's sign at the mouth. Same answer as 7 if the mouth is missing.

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
In order: rebuilds the zip → refreshes the index **through `mark_preserve.py --refresh`**, not a bare `packwiz refresh` (see [The world](#the-world) — a bare refresh strips the flag that stops an update deleting people's saves), commits `pack/index.toml`, `pack/pack.toml` and `pack/saves/` together, and refuses to go on if any world file is still uncommitted → **commits and pushes the zip** (CI builds the `.exe` from the copy on `main`, so this has to happen first) → rebuilds the dmg → triggers the Windows `installers.yml` workflow on GitHub Actions and waits for it (that job builds the `.exe` on a real Windows runner, silent-installs it four ways, and uploads it to the release itself) → rebuilds the install guide PDF into a new `dist/vN/` folder → uploads the zip + dmg + PDF (the `.exe` is already on the release by that point). Takes several minutes end to end because of the Windows CI run.

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

### Video settings, and why keybind changes only reach fresh installs

`pack/options.txt` carries render distance, `maxFps`, `entityDistanceScaling` and the 12 de-collided keybinds from the night audit. Its entry in `pack/index.toml` is marked:

```toml
[[files]]
file = "options.txt"
hash = "..."
preserve = true
```

`preserve = true` means **write-once-if-missing, never overwrite** — packwiz's own reference puts it as "the file is not overwritten if it already exists, to preserve changes made by a user", and the shipped `packwiz-installer.jar` implements exactly that: `DownloadTask.download()` returns early, before any hashing or writing, when `metadata.getPreserve()` is true and the destination file exists. The hash in the index is still refreshed on every `packwiz refresh`; it is simply never acted on for a file that is already there.

Two consequences, both deliberate:

- **Good:** a player's own video settings, sensitivity, sound levels and rebinds survive every update. Without the flag, every launch would silently stamp them back to ours.
- **The cost:** a keybind fix we make in `pack/options.txt` reaches **only fresh installs**. Existing players keep whatever their file says. If a future audit re-shuffles a binding, either announce the new key or tell them to delete `.minecraft/options.txt` and relaunch — packwiz will then lay down the current copy.

The flag is also what makes the Mac image's lower render distance stick. `installers/macos/build_dmg.py` synthesises `.minecraft/options.txt` into the instance zip from `pack/options.txt`, with `renderDistance` and `simulationDistance` both forced to **6** (`AIR_RENDER_DISTANCE` / `AIR_SIMULATION_DISTANCE` near the top of the file) — every other line, keybinds included, is copied through byte for byte in the pack's own order. Because that file exists before the first `PreLaunchCommand` runs, the packwiz installer leaves it alone, on that launch and every one after.

So there are two different render distances on purpose: **8** in `pack/options.txt` (Josh's Mac, the Windows `.exe`, the tracked `dist/LittleKettleValley.zip`) and **6** in the DMG instance (the 8 GB Air). Render distance is the cheapest frame-rate dial in the pack — see the Air budget table in `docs/integration-audit-night.md`. Changing the Air's number means editing the two constants in `build_dmg.py` and rebuilding the image; changing everyone else's means editing `pack/options.txt`, and only fresh installs will see it.

### Where they live

- `pack/saves/Little Kettle Valley/` — **the shipped world, tracked in git**: 68 files, 55 MB, the largest single file 8.6 MB. It is a release asset in the sense that matters — every friend downloads it through packwiz on first launch — but it is not attached to the GitHub release; it travels in the pack. Both installers point their instance at it with `JoinWorldOnLaunch`.
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
