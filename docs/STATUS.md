# Status: 2026-09-03, midday

## Where it stands
Little Kettle Valley is built, boots, and has been played through end to end by an automated harness. Everything below was verified by running the real thing, not by reading code.

## Launching
1. Open Prism Launcher. The instance is **Little Kettle Valley** (kettle icon). You already signed in.
2. Click **Launch**. The pre-launch step pulls the latest pack from GitHub (a few seconds), then the game starts. About 40 seconds to the title screen.
4. Singleplayer > Create New World (any name). Josie's letter, the deed, and the quest book arrive on first join. Press J for the quest book.
5. When your wife's Air is free: install Prism there, sign in, and import the instance (see `docs/INSTALL.md`). Set memory to 3072 MB.

## Verified tonight (see the session log for detail)
- Server boots clean: 116 server-side jars, KubeJS 2/2 startup + 8/8 server scripts, 0 script errors, 65 recipes added / 37 gated with 0 failures, all 125 quests loaded.
- Client boots to title in 35 s with 126 client-side jars; loads a world in 40 s; joins the server.
- Automated playthrough (4 runs, last one clean): offline test client joined, all 125 quests completed in order, 231 command rewards and function lines executed from the console with 0 errors, all 5 finales and 12 scenes ran, all 15 residents present in the world afterwards.
- Story read-through by three readers (non-creative partner, Tekkit veteran, continuity editor): 109 issues, 133 text fixes applied, then 16 progression blockers fixed with data changes and independently re-verified (one refuted and repaired: Lake Sand had no source).
- Integration audit: 75 findings, 26 verified fixes applied (duplicate metals unified, Farm & Charm season tags restored, Vein Mining bound to grave key, quarry chunkloader off, Waystones inventory button on, Dynamic Lights removed as a per-tick datapack).

## Numbers
| Thing | Count |
|---|---|
| Mods in pack | 126 |
| Quests | 125 across 6 chapters (5 acts + Oda's Counter) |
| Custom items | 49 (`valley:` namespace) |
| NPC presets | 15 (8 residents, 4 Ribbits, 3 arrivals) |
| Structure templates | 10 |
| Datapack functions | 13 |
| Journal entries | 19 (6 journal, 8 field notes, 5 found books) |
| Client memory | ~3.0 GB resident joined to the server, ~4.5 GB in singleplayer (integrated server), at a 3.5 GB heap. Air guidance: 3072 MB heap, play on Josh's server rather than singleplayer |

## First server start
The whitelist is on and empty, and nobody is op. Start the server, then add and op yourself (exact Minecraft username):
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" cmd "whitelist add YourMinecraftName"
```
```bash
"$HOME/Desktop/1. Projects/Minecraft/tools/scripts/server_ctl.sh" cmd "op YourMinecraftName"
```
Then in the game: Multiplayer > Direct Connect > `localhost`.

## Still open (needs you)
- **The Air test.** Not on the network tonight. Expect it to work at 3072 MB with render distance 6; if it stutters, the cut list is in `docs/integration-plan.md` and starts with Regions Unexplored.
- **GitHub: done.** Public repo https://github.com/malloyjoshua/little-kettle-valley, pack served at https://raw.githubusercontent.com/malloyjoshua/little-kettle-valley/main/pack/pack.toml, your Prism instance and the friend zip (`dist/LittleKettleValley.zip`, also attached to the GitHub release) both update from it on every launch.
- **playit.gg tunnel** for friends without port forwarding. Steps in `docs/RUNBOOK.md`; needs your browser sign-in to claim the agent.
- **Your wife's cute picks.** Placeholder cozy set is in (Farmer's Delight, Let's Do, Handcrafted, Macaw's, plushies, Ribbits, ducks, pets). Swap in her three things when she names them.

## Branding (done)
Chunky cream-and-copper title logo with the kettle, the "put the kettle on" tagline, an illustrated dusk panorama of the valley behind the title screen, a kettle launcher icon and server-list icon, and hand-drawn 16 px textures for all 49 valley items. Sources and build scripts in `media/`; in-game capture at `media/title_screen_in_game.png`. The Supplementaries "Amendments" popup is suppressed for every client.


## Gameplay redteam (2026-09-03 afternoon)
Five adversarial agents (the non-creative partner, the Tekkit veteran, a late-joining friend, the game engine on a headless server, a taste critic) attacked the shipped pack. 54 attacks, 49 kept: 7 critical, 14 high. Verdict before fixes: do not ship. All 21 critical and high items were then fixed and independently re-verified on fresh worlds, including one with the town on an island so the Works sat underwater. Highlights of what changed:
- Act I no longer deadlocks at q12 (Bram arrives the night you first sleep).
- Progress is shared for real (one party, recorded by its real name) and every auto-check latches per team, so a second player is never stuck.
- The ruined Kettle farm exists at first join with a lit path to it; the cottage rebuilds around its hearthstone; the letter has four pages.
- Finales run as re-entrant beats, forceload their region, and survive restarts, reloads, and being claimed from far away.
- The forty lamps light (copper lamps on posts, swept by the Act IV lever). The reactor climax needs the real terminal in view.
- Turbine bill has both bearings, the greenhouse glass passes light, scrip is capped (738 earnable against 350 of gates), the Works is excavated and sealed, the beach holds, the Lantern Float floats, the noticeboard carries the destination line.
Still unverified without a real player: the reactor look-at rule and the two-player latches. Run `tools/scripts/playthrough.sh` when the Mac is free (it launches the game window).

Next: the beauty pass. The town, the starting ruin and the Works get rebuilt from the pack's own designed structure templates (Towns and Towers, Dungeons and Taverns) in one consistent style, with staged arrival moments for discovery.

## Known rough edges
- The 26 per-player stage flags granted by quests are milestone markers with no consumer. Harmless. Documented in `docs/integration-plan.md`.
- Forge's update checker logs a JSON warning for Canary's remote version file at startup. Cosmetic.
- Torchmaster logs a missing model for its invisible light block at client start. Known upstream, cosmetic.

## If something breaks
`docs/RUNBOOK.md` covers start, stop, backup, restore, add a friend, update, roll back. The automated playthrough is `tools/scripts/playthrough.sh` and takes about 10 minutes.
