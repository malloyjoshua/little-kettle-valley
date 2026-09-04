# Status: 2026-09-04, morning (final)

## Where it stands
Little Kettle Valley is built, boots clean, and was played through end to end three times overnight by an automated client on fresh worlds, with an independent reviewer re-checking every claim on separate worlds. The town got a full visual rebuild from designed structures, a real 3x3 mining hammer was added, the story got a suspense pass, and the friend-facing installers (Windows .exe, Mac .dmg, manual .zip) were built, verified and published. Everything is pushed; the pack served from GitHub is byte-identical to the repo head.

## Launching
1. Open Prism Launcher. The instance is **Little Kettle Valley** (kettle icon). You already signed in.
2. Click **Launch**. The pre-launch step pulls the latest pack from GitHub (a few seconds), then the game starts. About 35 seconds to the title screen.
4. Singleplayer > Create New World (any name). Josie's letter, the deed, and the quest book arrive on first join. Press J for the quest book.
5. When your wife's Air is free: see **"Handing her the DMG"** below.

## What changed overnight
- **The town got rebuilt for real.** Every building is now a real, designed structure (Towns and Towers' Swiss-village set, the Dungeons and Taverns inn, a proper ruin) placed on leveled ground, not the old placeholder boxes. Roads, lamps, market carts, the well, flower boxes — all solved by a planner script so nothing overlaps or floats. 130 automated checks on this pass, 130 pass.
- **A second, independent pass re-checked that work** and added its own new checks the first pass didn't have — 177 total, 163 pass. The 14 that don't are all cosmetic (see "Still open" below), not game-breaking.
- **Bram now hands you a mining hammer in the first hour** (Just Hammers mod, a real 3x3-block-per-swing tool, the same one the inspiration pack uses). Every big dig-out in the game is now a third of the swings. New quest, no changes to anything that already existed.
- **The story got a suspense pass.** Each of the five act-endings now closes on an actual line from a character, not just "the season turns" — Marnie on the cellar door, Halden on the pier, Oda on the ridge fire, Halden reading Josie's real last page. 36 fixes applied and verified, nothing about quest order or dependencies touched.
- **The Windows installer, Mac disk image, and manual-import zip all rebuilt and verified.** The Windows one-click installer passed a real silent-install test on a GitHub-hosted Windows machine, including an install path with spaces and a `#`, and it picks the game's memory from the machine's RAM (3072 MB under 12 GB, 3584 up to 24 GB, 4096 above). Nobody has launched the game itself on Windows yet; the installer, bundled Java and pack download are what CI proves. The Mac side was proven on this Mac at your wife's exact memory setting (3072 MB) — see the memory numbers below.
- **An "everything works together" audit** went through all 127 mods' logs and configs looking for stuff that's individually fine but breaks in combination. Found 23 things; the two that mattered (wheat couldn't grow in the spring acts it's needed in; a common ore was quietly paying out real emeralds) are fixed and verified. The rest are cosmetic or your call — see below.
- **Two real bugs found by the memory test, both now fixed:** the pack's mod list on GitHub was missing the new hammer mod (so your wife's client would have failed to connect), and the settings file (`pack/options.txt`) was missing one line that Minecraft needs to read it at all — without that line, every fresh install silently threw away render distance, the quest-book key, and all the keybind fixes from the audit. Proven with the file's own tests, one line, done.

## Verified tonight (see the session log for detail)
- Server boots clean: 116 server-side jars, KubeJS 2/2 startup + 9/9 server scripts, 0 script errors, all 126 quests loaded.
- Client boots to title in 35 s with 127 client-side jars; loads a world in 40 s; joins the server.
- Automated playthrough (headless client, full replay): all 126 quests sent and acknowledged (0 refused), 321 audited commands, all 5 finales complete with 0 arrival retries giving up, 20 distinct scenes, all 15 residents present and accounted for by name, 0 real `[valley]` errors, 0 KubeJS script errors.
- **Quest ID bug fixed and proven the hard way.** Roughly half the quest and chapter IDs were silently unaddressable — a signed/unsigned overflow bug — which made 14 of 24 auto-completing quests silently no-op and 2 of 3 reward crates unreachable. Traced to the exact line, fixed, and reproduced clean: 0 bad IDs out of 1,194, re-verified again just now before tonight's push.
- Story read-through by three readers: 109 issues found, 133 text fixes applied, 16 progression blockers fixed and independently re-verified.
- Memory test on this Mac at your wife's exact settings (3072 MB heap, render distance 6): 35 s to title, 30 s to join, RSS peaks at 3.85 GB and settles to 3.06 GB after 5 minutes in town, **0 full garbage collections**, worst pause 52 ms. Plenty of headroom under an 8 GB machine's ceiling — this Mac is bigger than her Air, but the game's own memory use is a property of the pack, not the host, so this transfers. Her actual time-to-title will be slower than 35 s (weaker CPU); that's expected and fine.

## Numbers
| Thing | Count |
|---|---|
| Mods in pack | 127 |
| Quests | 126 across 6 chapters (5 acts + Oda's Counter) |
| Custom items | 49 (`valley:` namespace) |
| NPC presets | 15 (8 residents, 4 Ribbits, 3 arrivals) |
| Custom structure templates | 3 (the town's buildings are now the mods' own designed structures, not stand-ins) |
| Datapack functions | 12 |
| Journal entries | 19 (6 journal, 8 field notes, 5 found books) |
| Client memory | ~3.0 GB resident joined to the server, ~4.5 GB in singleplayer, at a 3.5 GB heap on this Mac. Your wife's Air: 3072 MB heap, joined to your server — do not raise it, there's no shortage of headroom at that number |

## First server start
The whitelist is on and empty, and nobody is op. Start the server, then add and op yourself (exact Minecraft username):
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" cmd "whitelist add YourMinecraftName"
```
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" cmd "op YourMinecraftName"
```
Then in the game: Multiplayer > Direct Connect > `localhost`.

## Handing her the DMG (exact steps)
1. Send her `LittleKettleValley.dmg` from the [release page](https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends) (or AirDrop it) and have her open it. Three steps are drawn right on the disk image: drag Prism Launcher into Applications, open it and sign in with her Microsoft account (the one that owns Minecraft — that's the only sign-in), then drag the kettle zip onto Prism's window.
2. First time opening Prism, macOS asks *"are you sure you want to open this?"* — she clicks **Open**. One-time, won't ask again.
3. She clicks **Little Kettle Valley > Play**. First launch pulls ~125 mods (a few minutes); after that it's fast and self-updating — she'll never need to redownload anything.

Memory is already baked into the DMG at 3072 MB and it starts at render distance 6 — nothing for her to configure. Player settings are write-once: the pack never overwrites `options.txt` after the first launch, so her own changes stick (and a keybind change in the pack only reaches fresh installs; see `docs/RUNBOOK.md`). Full written version with screenshots-in-words is `docs/INSTALL.md` if she wants it in front of her.

**Before you send it:** she needs to be on your server's whitelist first (see "First server start" above) — get her exact Minecraft username before she tries to join.

## Still open (needs you)
- **Fixed since the first draft of this report:** the Act IV greenhouse-glass wording (now names Vibrant Quartz Glass, the real recipe), the turbine/reactor command line in Act IV, and all 14 town-polish items: every front door now has paved road to it (11/11 doors, zero grass to cross), all four market carts match their templates 100%, the Ribbit camp, the still and the harvest props are solved against every piece of square furniture, resident teleports in scenes now forceload and retry like the finales, and the Surveyor's Stake refuses to stand where the town would swallow your cottage (the command form too; ops can add `force`). Independent re-check: 244 checks, 0 failures, on two fresh worlds. A third full client playthrough after those changes: 126/126 quests, 0 errors, hammer quest and anchor refusal exercised live.
- **Lower-priority stuff from the "everything works together" audit** — none of it blocks play, all of it is a judgment call: two ores (galena/limonite) each drop two different metals but machines only pay for one depending on recipe order (a balance call, not a bug); a couple of Act I/III quest items are only obtainable by foraging rather than farming in-season (works today, just not via farming); Carry On can pick up and carry off reactor/turbine blocks (recoverable — just re-place it and the multiblock re-forms, but worth locking down before she builds the reactor room). Full table in `docs/integration-audit-night.md`.
- **The Air test used this Mac, not her actual 8 GB M2 Air.** The numbers above are simulated at her exact settings and should transfer (memory use is the pack's, not the host's), but nobody has launched it on her physical machine yet.
- **playit.gg tunnel** for friends without port forwarding, still not set up. Steps in `docs/RUNBOOK.md`; needs your browser sign-in to claim the agent.
- **Your wife's cute picks.** Placeholder cozy set is in (Farmer's Delight, Let's Do, Handcrafted, Macaw's, plushies, Ribbits, ducks, pets). Swap in her three things when she names them.

## Branding (done)
Chunky cream-and-copper title logo with the kettle, the "put the kettle on" tagline, an illustrated dusk panorama of the valley behind the title screen, a kettle launcher icon and server-list icon, and hand-drawn 16 px textures for all 49 valley items. Sources and build scripts in `media/`; in-game capture at `media/title_screen_in_game.png`. The Supplementaries "Amendments" popup is suppressed for every client.

## Known rough edges
- The 26 per-player stage flags granted by quests are milestone markers with no consumer. Harmless. Documented in `docs/integration-plan.md`.
- Forge's update checker logs a JSON warning for Canary's remote version file at startup. Cosmetic.
- Torchmaster logs a missing model for its invisible light block at client start. Known upstream, cosmetic.
- Embeddium is flagged as "tainted" by a Supplementaries mixin (both mods wanted, no clean fix) — if she ever sees a fluid-rendering glitch, that's the first thing to suspect.

## If something breaks
`docs/RUNBOOK.md` covers start, stop, backup, restore, add a friend, update, roll back. The automated playthrough is `tools/scripts/playthrough.sh` and takes about 10 minutes.
