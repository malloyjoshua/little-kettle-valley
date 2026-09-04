# Integration audit — Little Kettle Valley

**Date:** 2026-09-04 (overnight autonomous sweep)
**Scope:** "everything works together, all mods work together, period" — 127 mods, Forge 47.4.10 / MC 1.20.1.
**Sources:** `server/logs/latest.log` + `debug.log` (boots 00:40 and 01:01), `server/logs/kubejs/{startup,server}.log`,
`scratch/night_playthrough/run1_client.log` + `run1_server.log`, the live KubeJS tag/recipe/loot/registry dump under
`server/local/kubejs/export/`, `pack/config/`, `pack/kubejs/server_scripts/`, `pack/mods/*.pw.toml`, and the mod jars themselves.

Every finding below is reproduced from a named log line or file, not inferred.

---

## The table

| # | Lens | Severity | Finding | Evidence | Fix | Status |
|---|---|---|---|---|---|---|
| **A1** | (d) seasons | **HIGH** | Wheat is not spring-fertile, but Acts I–II are scripted to spring and need ~80 wheat. Act I finale is soft-locked. | `seasons.toml starting_sub_season=1` (EARLY_SPRING); `valley_finales.js` `finaleAct1 -> season set early_spring`, `finaleAct2 -> season set mid_summer`; tag dump has `minecraft:wheat` in summer+autumn only; act1 q14 (16 flour), q19 (16 flour + 8 bread, consumed), act2 q37 (24 wheat) | Add `minecraft:wheat` / `minecraft:wheat_seeds` to `sereneseasons:spring_crops` | ✅ **applied** — `seasons_tags.js` |
| **A2** | (b) duplicates | **HIGH** | `geolosys:teallite_ore` is in `forge:ores/emerald` but its loot table drops only `tin_cluster`. Thermal Pulverizer pays 2.5 emeralds avg from a common early tin ore. | Geolosys jar `data/forge/tags/{items,blocks}/ores/emerald.json`; `loot_tables/geolosys/blocks/teallite_ore.json`; `recipes/thermal/machines/pulverizer/pulverizer_emerald_ore.json` (`minecraft:emerald` chance 2.5) | Remove teallite + deepslate variant from `forge:ores/emerald`, both sides — same de-aliasing unify.js already does for osmium | ✅ **applied** — `unify.js` §14 |
| **N1** | (a) content | **HIGH** | **Stale quest text.** Act IV q72 tells the player the greenhouse glazing is **Tinted Glass** from "two amethyst shards, one glass and one Cyanite Ingot". Neither that item nor that recipe exists any more. Following it builds a light-blocking, non-greenhouse room → Act V q77 hard-blocks. Act V **q77 already carries the corrected wording**, so this is one-file drift, not a design choice. | `story/quests/act4.json` q72 vs `valley_gates.js:217-226` (`ae2:quartz_vibrant_glass` = 2× glowstone dust + 2× `ae2:quartz_glass` + 1× cyanite ingot) and `:422-424` (tag holds only vibrant quartz glass). q77 text: *"The glass is Vibrant Quartz Glass — 2 glowstone dust, 2 Quartz Glass and 1 Cyanite Ingot makes two panes"* — already right. | Copy q77's wording into q72, then recompile quests | ⚠️ **not applied** — story surface + needs a full quest recompile; wants your eye |
| **A9** | (packaging) | **HIGH** | **`pack/index.toml` was stale and the packwiz installer refused to run** — `story_crate.snbt: Hash invalid!`, `tech_crate.snbt`, `_quest_ids.js`, the six act chapters and 15 Easy NPC presets, none of which I had edited. The installer aborts with `Update cancelled by user!` and leaves a **partial install**. I hit this for real: `sync_server.sh` deletes the quest/script folders *before* calling packwiz, so the cancel left the server with 0 quest chapters until I repaired it. A player installing the pack in that state gets the same broken result. Nothing in the release path regenerates the index: `tools/scripts/release.sh` never calls packwiz, and `.github/workflows/installers.yml:203` smoke-tests with the very command that fails. | live `packwiz-installer-bootstrap` run; `git status` (the stale entries are other workflows' in-flight edits); `grep packwiz tools/scripts/release.sh` → no refresh | Ran `tools/packwiz refresh` — index regenerated, sync then succeeded, server restored (6 chapters, 9 scripts). **Durable fix still needed:** `packwiz refresh` must run in `release.sh` before packaging. | ✅ **index refreshed** / ⚠️ **process gap not fixed** — `release.sh` and `.github/` belong to the concurrent workflow; hand this to them |
| **A3** | (e) keybinds | MED | `B` is a four-way collision: backpack / Xaero waypoint / CoFH mode-down / Deeper Darker boost — all IN_GAME. | `scratch/options.backup` (156 real client binds) vs `pack/options.txt` | Backpack keeps `B`; moved waypoint→`O`, CoFH down→`,`, DD boost→`;` | ✅ **applied** — `pack/options.txt` |
| **A4** | (e) keybinds | MED | `G` three-way: Curios / GuideMe / voice-chat group. Curios matters — `vinery:winemaker_apron` is a quest reward. | same | Curios keeps `G`; GuideMe→`-`, voice group→`=` | ✅ **applied** |
| **A5** | (e) keybinds | MED | `V` four-way (voice chat / CoFH mode-up / DD transmit / quiver) and `M` two-way (Xaero map vs **mute microphone** — bad for two people on voice). | same | Voice chat keeps `V`, Xaero keeps `M`; CoFH up→`.`, DD transmit→`'`, quiver→`\`, mute mic→`K` | ✅ **applied** |
| **A6** | (e) keybinds | MED | `C` (Carry On) also held Sophisticated Backpacks' inventory_interaction; `U` held Xaero waypoints + Corpse history; middle-click fired **two** sort mods at once. | same | Carry keeps `C`, Xaero keeps `U`, Inventory Sorter keeps middle-click; SB interaction→`I`, Corpse→`Home`, `sophisticatedcore.sort`→unbound (its on-screen sort button remains) | ✅ **applied** |
| **A7** | (a) logs | LOW-MED | Nether's Delight machete chopping bonus for leather and string never loads — 1.18-era loot condition name. | `latest.log`: `Could not decode GlobalLootModifier ... nethersdelight:chopping_leather - error: Unknown type 'minecraft:alternatives'` (and `chopping_string` / `'minecraft:alternative'`) | Datapack override with `minecraft:any_of` | ✅ **applied** — `pack/kubejs/data/nethersdelight/loot_modifiers/` |
| **A8** | (a) logs | LOW | Domestication Innovation's Blazing enchanted book never generates in nether-fortress chests — the mod's index asks for `blazing_enchanted_book`, the jar ships `blazed_enchanted_book.json`. | `latest.log`: `Could not decode GlobalLootModifier ... blazing_enchanted_book - error: Not a JSON object: null`; jar listing confirms the name mismatch | Supply the missing id as a datapack file | ✅ **applied** — `pack/kubejs/data/domesticationinnovation/loot_modifiers/` |
| **N2** | (b) duplicates | MED | `galena_ore` (lead+silver) and `limonite_ore` (iron+nickel) sit in two `forge:ores/*` tags each. Hand-mining drops both clusters; Create/Thermal machine-processing matches two recipes and pays only one metal, chosen by recipe iteration order. | tag dump `forge:ores/{lead,silver,iron,nickel}`; `loot_tables/geolosys/blocks/{galena,limonite}_ore.json`; `recipes/create/crushing/{lead,silver,nickel}_ore.json`, `recipes/thermal/machines/{pulverizer,smelter}/*` | Pick a canonical tag per block and hand-write a two-output machine recipe for the byproduct | ⚠️ **not applied** — changes machine yields; a balance call, not a bug |
| **N3** | (d) seasons | MED | Act I (spring) q18 wants `pumpkin_pie`; `pumpkin_stem` is autumn-only. Farming it is impossible; foraging a naturally-generated pumpkin works. | act1 q18; tag dump autumn_crops | Either forage (works today) or add pumpkin to spring | ⚠️ **not applied** — one pumpkin, obtainable |
| **N4** | (d) seasons | MED | Act III (summer) q42 wants 4× `handcrafted:berry_jam_jar`; `sweet_berry_bush` is spring+winter. | act3 q42; tag dump | Forage taiga bushes, or stockpile in Act II | ⚠️ **not applied** — obtainable |
| **N5** | (d) seasons | LOW | q40 is titled "Sow the Four Autumn Crops" but runs in **summer**; pumpkin/beetroot/barley won't grow. After the Act III finale flips to autumn, `thermal:barley` (spring+winter) still won't. Tasks only require *possessing* the seeds, so nothing blocks. | act3 q40 (`type: item` only); `finaleAct3 -> season set mid_autumn` | Cosmetic; or add barley to autumn | ⚠️ **not applied** — no task blocked |
| **N6** | (g) client | MED | Embeddium is **tainted**: Supplementaries mixes into its `FluidRenderer`. Embeddium disclaims support; fluid rendering is the thing to suspect first if she sees glitches. | `run1_client.log`: `Embeddium-MixinTaintDetector ... Mod(s) [supplementaries] are modifying ... FluidRenderer` | No clean fix — both mods are wanted | ⚠️ **not applied** — documented risk |
| **N7** | (a) logs | LOW | Canary and ModernFix ship the same Paper chunk-ticket patch; Canary's is skipped. | `latest.log`: `Method overwrite conflict for removeIf in canary.mixins.json:world.chunk_tickets.SortedArraySetMixin, previously written by ... modernfix ...` | ModernFix wins and works; can be silenced in `canary.properties` | ⚠️ **not applied** — cosmetic |
| **N8** | (b) duplicates | LOW | Create sheets vs Thermal plates (copper/gold/iron/electrum), `createaddition:diamond_grit` vs `thermal:diamond_dust`, `ae2:ender_dust` vs `thermal:ender_pearl_dust` are tag-unified but have no 1:1 bench conversion like unify.js gives its other pairs. | tag dump `forge:plates/*`, `forge:dusts/*` | Optional convenience recipes | ⚠️ **not applied** — machines already accept either |
| **N13** | (a) mod interaction | LOW-MED | Carry On's stock blacklist blocks `bigreactors:*` — the **1.12 Big Reactors id**. This pack ships `biggerreactors:*`, so reactor and turbine multiblock parts are freely carryable, as are Thermal, AE2, Sophisticated Storage, Storage Drawers and QuarryPlus blocks. The usual tag guard does not help: `forge:relocation_not_supported` holds only Railways (334) + 1 Create block, and `forge:immovable` does not exist. `create:*`, `cookingforblockheads:*`, `ftbquests:*`, `waystones:*` and `easy_npc:*` **are** correctly blocked — the story NPCs cannot be carried off. | `server/config/carryon-common.toml` `[blacklist] forbiddenTiles`; block-tag dump of `forge/relocation_not_supported` | Add `"biggerreactors:*"` (and optionally `"quarryplus:*"`) to `forbiddenTiles` | ⚠️ **not applied** — would mean shipping a whole new `pack/config/carryon-common.toml` and pinning Carry On's defaults; failure mode is recoverable (re-place the block and the multiblock re-forms). Your call. |
| **N11** | (b) duplicates | LOW | Four tomatoes exist (`candlelight:`, `farm_and_charm:`, `farmersdelight:`, `thermal:`) and q77 accepts only `thermal:tomato`. Same shape for onion (3), cabbage/lettuce (4), corn, rice. Cooking recipes are fine — they consume `forge:crops/*`, which unifies all of them — but **quest item tasks match literal ids**. q40 shows the author already handles this ("the Barley Seeds are Thermal's, spelled exactly like that"); q77 does not name a namespace. | tag dump `forge:crops/{tomato,onion,cabbage,corn,rice}`; act5 q77 tasks | Name the namespace in q77's text, as q40 does | ⚠️ **not applied** — story wording; low risk since the seeds come from quest rewards |
| **N9** | (a) logs | INFO | 9× `Failed to parse recipe 'deeperdarker:resonarium_*_smithing'` — upstream ships an empty smithing template. KubeJS falls back to vanilla, so the recipes still work. | `kubejs/server.log` | none | upstream noise |
| **N14** | (b) duplicates | INFO | `hide.js` §3 carries a stale warning — *"leave these commented until that config edit ships, otherwise you hide items the world is still generating"* — but the code is live **and that is correct**: the config did ship. Verified `thermal-common.toml` has Tin/Lead/Silver/Nickel `Enable = false`, and the only surviving producers of `thermal:raw_*` are the circular block↔item pack/unpack recipes, which have no entry point. Only the comment is wrong. | `pack/config/thermal-common.toml:14-40`; `export/recipes/thermal/{storage,machines/press/unpacking}`; `hide.js:49-66` | Delete the stale NOTE so nobody comments out working code | ⚠️ **not applied** — comment-only |
| **N12** | (a) logs | INFO | One gameplay-time error during the run2 playthrough: `Allay: No key selector in MapLike[{event_delay:0,...}]` — vanilla 1.20.1 mis-serialises the Allay's vibration-listener memory. Logged once, the Allay keeps working. | `server/logs/latest.log` (run2 boot) | none | upstream vanilla |
| **N10** | (a) logs | INFO | `patchouli: Invalid icon item stack: Unknown item ID: thermal:lumium_rail` — Thermal Foundation's **own** guide book, not the valley journal. | `run1_client.log`; string found only in `thermal_foundation-1.20.1-11.0.6.70.jar` | none | upstream cosmetic |

---

## Checked and clean

| Lens | What was verified | Evidence |
|---|---|---|
| (c) power bridges | **The FE chain is genuinely unified.** Every link references `net/minecraftforge/energy/IEnergyStorage`: Thermal Dynamics 13, Bigger Reactors 2, QuarryPlus 3, Create Crafts & Additions 65, AE2 20. All bridge blocks exist in the registry (alternator, electric motor, connectors, energy/fluid duct, AE2 energy acceptor, reactor + turbine power taps, quarries). | class-level `strings` scan of the jars + `export/registries/item.json` |
| (c) power bridges | AE2 `PowerRatios.ForgeEnergy = 0.5` (stock 2 FE→1 AE). Createaddition large connector caps at 5000 FE/t — a throttle on reactor output, not a break. | `config/ae2/common.json`, `config/createaddition-common.toml` |
| (f) structures | **No quest has a structure or location task at all** — the 125 quests use only `item` (155), `checkmark` (55) and `stage` (1). The "find a X within 1500 blocks" risk does not exist in this pack. | task-type census over `story/quests/*.json` |
| (f) structures | `bakery:oat_seeds` (act3 q40) looked structure-locked (`bakery:oat_field` at 3264 blocks effective) but is **craftable**: 2× wheat seeds + 2× bone meal → 2. | `letsdo-bakery` jar `data/bakery/recipes/oat_seeds.json` |
| (f) structures | Sparse Structures `spreadFactor 1.5`, `towns_and_towers:towns` at 4. T&T ships **no** `data/minecraft/worldgen/structure_set/` override, so vanilla `minecraft:villages` keeps stock 34/8 → ≈816-block spacing after the global factor; T&T's own 27-town set carries an `exclusion_zone` against `minecraft:villages` and, at factor 4, lands ≈3072 blocks apart. Villages — the practical fallback source for wheat, bread and seeds — stay common. Nothing the story needs is gated behind a rare structure. | `pack/config/sparsestructures.json5`; `Towns-and-Towers-1.12-Fabric+Forge.jar` listing + `towns.json` placement; spacing extracted from every mod jar's `worldgen/structure_set/*.json` |
| (d) seasons | `out_of_season_crop_behavior = 1` = "Can't grow" — out-of-season crops **stall, they do not break**. No silent crop loss. | `config/sereneseasons/fertility.toml` |
| (d) seasons | Farmer's Delight (cabbage, onion, rice, tomato) and Let's Do / Farm & Charm crops all resolve; Vinery grapes and Bakery oats are untagged, i.e. fertile year-round. `seasons_tags.js` correctly re-files Farm & Charm's misplaced tags. | tag dump + `seasons_tags.js` |
| (b) duplicates | Metal unification holds: tin/silver/lead/nickel/zinc/copper/electrum/netherite each resolve to one canonical item with the retired ones still tag-valid. Flax is single-sourced (Supplementaries' is `enabled = false`). | `forge:ingots/*`, `nuggets/*`, `storage_blocks/*` dumps; `supplementaries-common.toml` |
| (b) duplicates | Crop/food duplication across Farmer's Delight, Let's Do (Candlelight/Bakery/Vinery), Farm & Charm and Thermal is **already tag-unified by the mods themselves** — `forge:crops/{tomato,onion,cabbage,corn,rice,flax}` and `forge:seeds/*` hold every variant, so Cooking Pot / Cutting Board / Thermal recipes accept any of them. No unify.js work needed. | tag dump `forge/crops`, `forge/seeds` |
| (g) client | Bigger Reactors' scary `Initializing OpenCL, may cause native level crash` **degrades cleanly** on Apple silicon: `Failed to load LWJGL OpenCL Classes` → `OpenCL acceleration not available`. No crash risk. | `run1_client.log` |
| (g) client | Flywheel falls back `indirect → instancing` on macOS OpenGL 4.1 Metal. Expected and correct on any Mac. | `run1_client.log` ×10 |
| (a) logs | FTB Teams `Local player id ... not found in the known players list` is a **harness artifact** — the test client logs in as `packtester` with an offline (v3) UUID against `online-mode=true`. Confirmed by `valley_core.js#692: FTB Teams did not report a party for packtester`. | `run1_client.log`, `server.properties`, `kubejs/server.log` |
| (hygiene) | **No pack↔server config drift.** All 19 configs the pack ships are byte-identical to what the server ran, except `sereneseasons/seasons.toml`, where the diff is Serene Seasons re-ordering keys inside `[[season_properties]]` — every value matches, and the pack copy carries the `starting_sub_season = 1` / `sub_season_duration = 9` that finding A1 rests on. The FTB Quests SNBT, `ftbxmodcompat.snbt` and `easy_npc/security.cfg` diffs are runtime-rewritten files that `sync_server.sh` deletes before syncing. Everything else in `server/config/` is a regenerated mod default and will regenerate identically on her machine — so the audited behaviour is what ships. | `diff pack/config ↔ server/config` |
| (a) Easy NPC / Patchouli / FTB | **Zero load warnings from any of the three story mods.** Easy NPC 7.11.0 loads all 15 `.npc.snbt` presets with no errors, creates its storage folder and saves NPCs on schedule; its only WARN is the mod turning its own debug log level down. Patchouli reloads and sends its client packet. FTB Quests/Teams/Library register cleanly. | `latest.log`; `pack/kubejs/data/valley/easy_npc/preset/*` |
| (co-op) | Simple Voice Chat is configured sanely for two people: `max_voice_distance 48`, `whisper 24`, `enable_groups true`, `force_voice_chat false`. **Practical gotcha for hosting: it needs UDP 24454 open in addition to the Minecraft TCP port.** Forward only 25565 and voice fails silently. Groups let them talk across the map once building spreads past 48 blocks. | `pack/config/voicechat/voicechat-server.properties` |
| (a) logs | Server boots carry exactly **one** ERROR line (`RuntimeDistCleaner ... MultiPlayerGameMode for invalid dist DEDICATED_SERVER`) — the standard Forge client-class guard. No mixin apply failures, no missing registry entries, no "Unknown recipe", no tag errors, no datapack function errors. KubeJS: **10/10 scripts, 0 errors, 0 warnings.** | `latest.log`, `debug.log`, `kubejs/*.log` |

---

## (g) The Air budget — cut order

Measured on Josh's **M1 Max**: 33.9 s to start, 41.9 s to world, `--xmx 3584`. An M-series Air will be meaningfully worse.
`pack/options.txt` is already conservative (render 8, simulation 6, entityDistanceScaling 0.75, maxFps 60).

**Dial before you cut:** render distance 8 → 6 is the single cheapest win and costs nothing structurally.

Cut in this order. Story-coupling was checked by grepping `story/`, `pack/patchouli_books/` and the server scripts for each mod.

| Order | Mod | Side | Story refs | Safe to remove mid-game? | Why |
|---|---|---|---|---|---|
| 1 | `particle-rain` | client | 0 | ✅ yes | Per-particle weather. Pure cosmetic, highest cost-to-value ratio. |
| 2 | `sound-physics-remastered` | client | 0 | ✅ yes | Raytraces every sound occlusion/reverb — the heaviest CPU client mod in the set. |
| 3 | `ambientsounds` | client | 0 | ✅ yes | Continuous biome-scan ambience. |
| 4 | `xaeros-world-map` | client | 0 | ✅ yes | The **world map** only. Waypoints belong to `xaeros-minimap` — keep that one (see below). Saves background chunk caching and disk churn. |
| 5 | `extreme_sound_muffler` | client | 0 | ✅ yes | Light; cut only if she never uses muffling. |
| 6 | `regions_unexplored` | **both** | 0 (and 0 uses in `town_plan.js`) | ❌ **no — before world creation only** | Biggest single worldgen/render win, but it is a TerraBlender biome mod: pulling it from an existing save voids RU chunks and shifts biome regions. Decide this before she starts. |

**Do not cut**

- `xaeros-minimap` — **story-load-bearing.** Quests hand out waypoints via the `xaero-waypoint:Mill:M:<x>:<y>:<z>:...` chat format (4 references across `story/` and the scripts). Removing it silently drops the navigation the quest text promises.
- `embeddium`, `entityculling`, `immediatelyfast`, `ferrite-core`, `memoryleakfix`, `modernfix`, `canary`, `clumps` — these *are* the performance budget.
- `jade` / `jade-addons` — quest-reading QoL.

**Memory:** the test used 3584 MB. That is about right for an 8 GB Air; give it 4–6 GB on 16 GB. (Installer defaults live in `installers/`, which another workflow owns — not touched here.)

---

## Files changed

| File | Change |
|---|---|
| `pack/kubejs/server_scripts/seasons_tags.js` | A1 — wheat into `sereneseasons:spring_crops` (block + item), with the full evidence trail in the comment |
| `pack/kubejs/server_scripts/unify.js` | A2 — new §14, teallite de-aliased out of `forge:ores/emerald` (block + item) |
| `pack/options.txt` | A3–A6 — 12 keybind lines appended |
| `pack/kubejs/data/nethersdelight/loot_modifiers/chopping_leather.json` | A7 — new, `minecraft:any_of` |
| `pack/kubejs/data/nethersdelight/loot_modifiers/chopping_string.json` | A7 — new, `minecraft:any_of` |
| `pack/kubejs/data/domesticationinnovation/loot_modifiers/blazing_enchanted_book.json` | A8 — new |
| `pack/index.toml` | A9 — regenerated by `tools/packwiz refresh`; hashes for my 6 files **and** for the quest SNBT / Easy NPC presets other workflows have in flight. Idempotent — re-run it after any further `pack/` edit. |

Backups of the three edited files are in the session scratchpad (`seasons_tags.js.bak`, `unify.js.bak`, `options.txt.bak`).

No quest key, dependency, reward, latch, beat, forceload, lamp array or noticeboard text was touched.
`installers/`, `.github/`, `dist/`, `docs/INSTALL.md`, `tools/scripts/release.sh`, `tools/scripts/install_guide_pdf.py`
and `docs/RUNBOOK.md` were not touched.

---

## Verification

The playthrough workflow's **run2** synced `pack/` → `server/` at 01:01:06, *after* the A1/A2 script edits, so its live boot
already exercised them:

```
[01:01:22] Loaded 9/9 KubeJS server scripts in 0.067 s with 0 errors and 0 warnings
[01:01:23] [minecraft:block] Found 779 tags, added 10 objects, removed 7 objects
[01:01:23] [minecraft:item]  Found 1617 tags, added 23 objects, removed 4 objects
```

versus the 00:40 boot before the edits (`block: added 9, removed 5` / `item: added 22, removed 2`) — exactly
**+1 added and +2 removed on each side**, which is wheat in and the two teallite entries out, per side. The arithmetic
confirms both tag fixes landed.

### Dedicated verification boots (01:19 and 01:23)

With the playthrough finished and **no other server running**, I refreshed the packwiz index (A9), re-synced, and booted
twice. The world was fresh, so the first boot generated `world/serverconfig/` for 13 mods — 797 one-time
`ForgeConfigSpec: Incorrect key … was corrected from null to its default` warnings. The second boot proves those do not recur.

| | boot 1 (fresh world) | boot 2 (world initialised) |
|---|---|---|
| ERROR lines | 1 | **1** — only the benign Forge `RuntimeDistCleaner` dist guard |
| WARN lines | 887 | **80** |
| `corrected from null` | 797 (one-time) | **0** |
| **LootModifier failures** | **0** | **0** — was 5 before the fix |
| KubeJS scripts | 9/9, 0 errors, 0 warnings | 9/9, 0 errors, 0 warnings |
| tag deltas | block +10/−7, item +23/−4 | block +10/−7, item +23/−4 |

Then `kubejs export` for a definitive tag dump — all six assertions pass:

```
A1  block spring_crops -> ['minecraft:wheat']          PASS
A1  item  spring_crops -> ['minecraft:wheat_seeds']    PASS
A2  block forge:ores/emerald -> teallite absent        PASS   (beryl_ore retained as the emerald ore)
A2  item  forge:ores/emerald -> teallite absent        PASS
A2  block forge:ores/tin -> teallite still present     PASS   (tin path preserved, no collateral damage)
A2  item  forge:ores/tin -> teallite still present     PASS
```

Server stopped cleanly afterwards; nothing left running.
