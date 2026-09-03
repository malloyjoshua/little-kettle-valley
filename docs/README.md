# Copper Kettle Valley

A private Minecraft modpack for Josh, his wife, and friends. Forge 1.20.1, about 125 mods, a five-act Stardew-style story written as FTB Quests chapters, braided with Tekkit-style tech (Create, Thermal, Applied Energistics, Bigger Reactors, QuarryPlus).

**The one-line pitch:** you inherit a cold house in a quiet valley. Forty lamps. Fifteen people. One winter that nobody leaves.

## Folder map
- `pack/` the pack itself (packwiz). `pack.toml`, `mods/*.pw.toml`, `config/`, `defaultconfigs/`, `kubejs/`, `patchouli_books/`, `options.txt`
- `story/` the story document (`story-final.md`), the machine outline, the writer brief, `npcs.json`, and the quest source JSON in `story/quests/`
- `tools/` user-space JDK 17, packwiz, the Python venv, and `scripts/`:
  - `compile_quests.py` turns `story/quests/*.json` into FTB Quests SNBT
  - `validate_quests.py` parses the SNBT and checks item ids and dependencies
  - `make_npc_presets.py` builds Easy NPC presets from `story/npcs.json`
  - `make_structures.py` builds the small structure templates the finales place
  - `server_ctl.sh` start/wait/cmd/stop for the server with a command pipe
  - `playthrough.sh` automated command-layer playthrough of every quest
  - `testclient.py` offline test client (mod-developer style, no account)
- `server/` the Forge server for local play and hosting (`start.sh`, `backup.sh`)
- `docs/` this file, `RUNBOOK.md`, `INSTALL.md`, `QUEST_FORMAT.md`, `NPCS.md`, `JOURNAL.md`, `BOUNTIES.md`, `mod-decisions.md`, `integration-plan.md`, `story-research.md`, `story-gap-analysis.md`

## How the story is wired
- Quests: `story/quests/act1..act5.json` + `oda.json` (Oda's Counter, the scrip shop). Compile with `tools/venv/bin/python tools/scripts/compile_quests.py story/quests pack/config/ftbquests/quests scratch/ids_plus.json --strict`
- Custom items (`valley:` namespace): `pack/kubejs/startup_scripts/valley_items.js`
- Core helpers, team auto-party, first join: `pack/kubejs/server_scripts/valley_core.js`
- Recipe gates and anti-grind recipes: `valley_gates.js`. Auto-completing checks: `valley_checks.js`. The `/valley` command (finales, scenes, standing): `valley_finales.js`
- Datapack: `pack/kubejs/data/valley/` (functions, advancements, loot tables, structures, Easy NPC presets)
- Josie's Journal: `pack/patchouli_books/valley_journal/`
- Materials unification and JEI hiding: `unify.js`, `client_scripts/hide.js`

## Change a quest
1. Edit the JSON in `story/quests/`.
2. Recompile (command above). Errors name the quest key.
3. `cd pack && ../tools/packwiz refresh`
4. Re-sync the server: `cd server && ../tools/jdk17/Contents/Home/bin/java -jar ../tools/packwiz-installer-bootstrap.jar -g -s server ../pack/pack.toml`
5. Commit.

## Rules that hold
- The company NAS never hosts this. See `docs/RUNBOOK.md`.
- Every id in a quest must exist in the game. The compiler enforces it.
- Stage rewards are per player and never team-wide. Quest progress is per team.
