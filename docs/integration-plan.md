# Cozy Tech Pack — Integration Plan

Forge 1.20.1 / Forge 47.4.10 · ~120 mods · two players (a Tekkit-era tech player who hates
grind, and a non-creative cozy player who needs a clear path) · must run on an 8 GB M2 Air
at 3.5 GB allocated.

**Standing constraint:** no heavy new mods. Everything below is a config key, a KubeJS
script, a datapack file, a quest-book edit, or a mod removal.

**Artifacts this plan ships**

| File | What it is |
|---|---|
| `pack/kubejs/server_scripts/unify.js` | materials unification + ore chains (rewritten) |
| `pack/kubejs/client_scripts/hide.js` | JEI hide list (replaces the deleted `unify_jei.js`) |
| `scratch/config_edits.json` | every config key + value to apply under `pack/` |
| `pack/options.txt` | keybinds + the handful of client options that matter |
| `scratch/mod_changes.json` | mod removals the evidence justifies |

**Deploy note that applies to every config item below.** `pack/` is packwiz source;
`server/` is the running world. Nothing in `pack/` reaches the test server until
`packwiz refresh` + a packwiz-installer reinstall (`docs/RUNBOOK.md` lines 43-48).
`grep pack/index.toml` currently shows **no entries** for `config/easy_npc/security.cfg`
or `config/ftbxmodcompat.snbt` even though both files exist on disk — they are not being
shipped. Run `packwiz refresh` before believing any "already fixed" claim.

---

## 1. Power and tech — Create · Thermal · AE2 · Bigger Reactors · QuarryPlus · Geolosys

### PT-01 — Thermal parts tree: **VERIFY FIRST, do not patch blind** — severity: blocker (contested)

**What we do.** This is the one finding where two independent verifications disagree, so
the action is a five-minute in-game check, not a script.

One pass scanned every `data/**.json` in `server/mods/*.jar` and found no recipe producing
`thermal:machine_frame`, `thermal:rf_coil`, `thermal:redstone_servo`, `thermal:energy_cell`,
`thermal:fluid_cell`, `thermal:saw_blade`, `thermal:drill_head` or `thermal:wrench` — which
would make every Thermal Expansion machine, every dynamo and every Innovation tool
uncraftable. The second pass found those exact recipes **inside a jar-in-jar**:
`thermal_foundation-1.20.1-11.0.6.70.jar :: META-INF/jarjar/thermal_core-1.20.1-11.0.6.24.jar`,
whose `mods.toml` declares `modId = "thermal"` (the dependency `thermal_expansion` requires).
A top-level-only jar scan cannot see it.

**Exact change — step 1 (do this before anything else).** In game, JEI-lookup
Machine Frame, RF Coil, Redstone Servo, Energy Cell, Wrench, Satchel.

* **If every one shows a recipe** → PT-01 is a scanning artefact. Close it. Do **not**
  create `thermal_parts.js`; adding a second recipe for an item that already has one is
  exactly the duplicate-JEI-entry mess this pack is trying to avoid.
* **If any shows "no recipe"** → the cause is a runtime override, not a missing recipe.
  `grep -rn "event.remove" pack/kubejs/server_scripts/` for anything matching those ids
  (the rewritten `unify.js` does **not** touch them — every removal there is either an
  explicit id or scoped to a vanilla recipe type). Only if nothing is removing them do
  you add recipes, and then use the parts file from the finding verbatim.

**Exact change — step 2 (do this regardless).** Run a proper orphan sweep before writing
any recipe, because the first scan's method was the bug:

```bash
cd "/Users/joshuamalloy/Desktop/1. Projects/Minecraft/server/mods"
for f in *.jar; do unzip -l "$f" 2>/dev/null | grep -qi jarjar && echo "$f"; done
```

Extract each hit's `META-INF/jarjar/*.jar` and repeat the recipe-result scan across the
extracted content. Only items still unrecipe'd after that are true orphans. Known
candidates for that sweep: all `thermal:device_*`, all `thermal:*_augment`,
`thermal:charge_bench`, `thermal:tinker_bench`, `thermal:xp_crystal`, `thermal:lock`,
`thermal:florb`, rockwool, the beekeeper/diving/hazmat armour sets, plus
`thermal:redprint`, `thermal:laser_diode`, `thermal:detonator`, `thermal:junk_net`,
`thermal:compost`, `thermal:phytogro`, `thermal:phytosoil_tilled` and the
diamond/emerald/lapis/quartz/ruby/sapphire gears. Each genuine orphan gets a recipe or a
JEI hide — never a quest-book reference.

**Do not** chase the "swap Thermal Foundation 11.0.5.x against TE 11.0.1.29" idea. The
CoFH changelog (`github.com/CoFH/Version/blob/main/thermal/changelog.md`) records no
addition or removal of these parts recipes anywhere across 11.0.0 → 11.0.6. This is not
version skew.

**Integration win.** The frame/coil tree is what makes Thermal a real second tech branch
next to Create: Pulverizer → Thermal plates → Create Crafts & Additions rolling mill
(`createaddition:data/createaddition/recipes/rolling/electrum_plate.json` takes
`#forge:plates/electrum`, which Thermal's Press fills). That chain is already wired.

---

### PT-02 / MAT-02 — Crushing wheels destroy platinum, uranium, aluminum, osmium — blocker — **FIXED in `unify.js` step 10**

**Evidence.** Parsed every recipe in `create-1.20.1-6.0.8.jar`.
`create:crushed_raw_platinum` has **zero** consuming recipes.
`create:crushed_raw_uranium` (9), `create:crushed_raw_osmium` (3) and
`create:crushed_raw_aluminum` (6) are all gated on
`{"type":"forge:mod_loaded","modid":"ic2"|"immersiveengineering"|"mekanism"}` — none of
those are in `scratch/modlist.txt`. The *producing* recipes are live because Geolosys and
Bigger Reactors fill the gating tags:
`Geolosys-1.20.1-7.0.14.jar :: data/forge/tags/items/raw_materials/platinum.json` =
`[geolosys:platinum_cluster]`, same for `uranium` and `aluminum`; Bigger Reactors ships
`raw_materials/uranium` = `[biggerreactors:uranium_chunk]`. So a Tekkit player who feeds
raw ore into crushing wheels permanently loses every platinum cluster, every uranium chunk
and every aluminum cluster.

**Exact change.** `unify.js` step 10 gives all four a furnace + blast path to the same
ingot the un-crushed cluster reaches:

```js
'create:crushed_raw_platinum': 'geolosys:platinum_ingot',
'create:crushed_raw_osmium':   'geolosys:platinum_ingot', // no osmium ingot exists in this pack
'create:crushed_raw_aluminum': 'geolosys:aluminum_ingot',
'create:crushed_raw_uranium':  'biggerreactors:uranium_ingot'
```

`.xp(0.1).cookingTime(200)` smelting and `.xp(0.1).cookingTime(100)` blasting, matching
Create's own gated `smelting/ingot_uranium_compat_*.json` numbers.

**We do not delete the osmium crushing recipes.** The earlier draft removed
`create:crushing/osmium_ore` / `raw_osmium` / `raw_osmium_block`. That leaves crushing
behaving differently for one ore than every other, and `geolosys:osmium_cluster` already
routes to `geolosys:platinum_ingot` in `unify.js` step 9. Uniform behaviour beats a
special case.

**Also in `unify.js` (tag event).** Geolosys files `geolosys:platinum_ore` and
`geolosys:deepslate_platinum_ore` into **both** `forge:ores/platinum` and
`forge:ores/osmium` (its own tag files, unconditional and byte-identical), so Create loads
two crushing recipes for the same block. We remove the osmium membership on both the item
and block side. Because it is not certain whether KubeJS tag edits land before Create's
`forge:tag_empty` conditions are evaluated, step 10's smelting fallback stays as the belt
to that braces.

**Integration win.** Crushing wheels become the "ore doubling for everything" answer a
Tekkit player expects, and Create becomes a legitimate front end for the Bigger Reactors
fuel chain instead of a wood-chipper.

---

### MAT-03 — Geolosys autunite → Bigger Reactors — major — **already fixed, do not duplicate**

`geolosys:uranium_cluster` is the autunite drop; Bigger Reactors smelts only
`biggerreactors:uranium_chunk` by literal id
(`biggerreactors:data/biggerreactors/recipes/smelting/uranium_chunk.json`), and ships
compat folders for appliedenergistics and mekanism only. The live tag
`forge:raw_materials/uranium` already contains both items, so the two are declared the same
material and only the recipe was missing.

`unify.js` step 9 carries it, with xp/time copied from Bigger Reactors' own recipe:

```js
event.smelting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster').xp(0.35).cookingTime(200)
event.blasting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster').xp(0.35).cookingTime(100)
```

**Do not add a second copy in another script.** A jar/datapack scan will always report
"zero recipes" for this, because KubeJS-generated recipes are never written as
`data/**/recipes/*.json` files. That scan blind spot is what made this look unfixed twice.

---

### PT-07 — All four Geolosys `[compat]` flags are dead code — major — config

`CompatConfig.class` in `Geolosys-1.20.1-7.0.14.jar` defines `ENABLE_OSMIUM`,
`ENABLE_OSMIUM_EXCLUSIVELY`, `ENABLE_YELLORIUM`, `enableSulfur`, but across all 60 classes
in the jar `CompatConfig` is referenced only by `CommonConfig.class` and itself — no
gameplay class reads it. Confirmed at runtime:
`server/local/kubejs/export/loot_tables/geolosys/blocks/platinum_ore.json` still drops
`geolosys:platinum_cluster` with `enableOsmiumExclusively = true`
(`pack/config/geolosys-common.toml:50`), and `autunite_ore.json` still drops
`geolosys:uranium_cluster` with `enableYellorium = true` (line 52).

**Exact change.** Set all four to `false` in `pack/config/geolosys-common.toml`
(`config_edits.json` entries 1-4). This is documentary — it changes no behaviour. Its
whole job is to stop a future maintainer "fixing" the osmium or uranium dead end by
flipping a switch that does nothing.

---

### PT-09 — AE2 power direction — major — quest design

**Evidence.** `scratch/ids.json` has `ae2:energy_acceptor`, `ae2:cable_energy_acceptor`,
`ae2:energy_cell`, `ae2:dense_energy_cell` — all AE-side.
`server/config/ae2/common.json` `PowerRatios.ForgeEnergy: 0.5` = 2 FE per AE, one way in.
ME cables carry AE only.

**But the earlier framing was wrong and must not reach the book.** "FE never comes back out
of AE2" is false: an **ME P2P Tunnel attuned to Forge Energy** (`ae2:fe_p2p_tunnel`,
attuned by right-clicking with an Energy Acceptor / Energy Cell / Dense Energy Cell — see
`appliedenergistics2-forge-15.4.10.jar :: data/ae2/tags/items/p2p_attunements/fe_p2p_tunnel.json`)
relays real FE across the network for a 2.5% AE tax (`PowerRatios.p2pTunnelEnergyTax`).

**Exact change — quest-book page text:**

> Power flows Create → FE → everything. AE2's Energy Acceptor pulls FE **in** to run your ME
> network (2 FE = 1 AE); your network's AE budget can't be turned back into FE. Build your
> grid out of Fluxducts (`thermal:energy_duct`) or Connectors
> (`createaddition:connector`, `createaddition:large_connector`) and hang the Energy
> Acceptor off it as a leaf. Later, if you want power to travel *through* your ME network
> instead of along more cable, attune an ME P2P Tunnel to Forge Energy with an Energy
> Acceptor, feed the input side from a real FE source, and take FE out of any FE-attuned
> output tunnel — into a Reactor Power Tap (`biggerreactors:reactor_power_tap`), a quarry,
> or a Thermal machine.

If you would rather keep the cozy player's mental model simple, cut the P2P paragraph — but
then say "AE2 doesn't reach Bigger Reactors / QuarryPlus / Thermal by the simple path", not
"FE never comes back out". A player who later finds P2P tunnels in JEI or the AE2 guide
book will correctly conclude the book lied.

**Integration win.** A Tekkit player will absolutely try to run power over ME cable. Saying
this once prevents an hour of "the quarry isn't running".

---

### PT-11 — Certus quartz is meteorite-only, and Sparse Structures makes it worse — major — config

AE2 15.4.10 registers **no certus quartz ore block** — `scratch/ids.json` has
`ae2:certus_quartz_crystal`, the budding blocks and `ae2:quartz_cluster`, but no
`ae2:quartz_ore`. Its only worldgen is
`data/ae2/worldgen/structure_set/meteorite.json` (spacing 32, separation 8), and
`worldGen.spawnPressesInMeteorites: true` means the four processor presses are gated on it
too. `pack/config/sparsestructures.json5` sets `"spreadFactor": 1.5` with an empty
`customSpreadFactors`, pushing that to ~48 chunks. The entire AE2 branch is hostage to one
structure roll.

**Exact change.** `config_edits.json` entry 5 — add to `customSpreadFactors`:

```json
{ "structure": "ae2:meteorite", "factor": 1.0 }
```

`factor` **overrides** `spreadFactor`, it does not compound with it, so `1.0` restores exact
vanilla 32/8 spacing. (If you decide certus should be deliberately easier than vanilla for
the no-grind player, use `0.6` and describe it as "more common than vanilla" — not as an
exemption.) Requires a game restart; the file header says so. Keep
`spawnFlawlessOnly: false` in `server/config/ae2/common.json` so damaged budding quartz is
obtainable, and hand out an `ae2:meteorite_compass` as an early quest reward.

---

### PT-12 — QuarryPlus force-loads chunks with no cap — major — config

`pack/config/quarryplus-common.toml:38` `enableChunkLoader = true`, line 30
`chunkDestroyerLimit = -1`, line 47 `adv_quarry = true`, line 33
`flexMarkerMaxDistance = 256`, `maxEnergy = 50000` / `breakBlockBase = 25.0` (lines
104-108). On an 8 GB M2 Air at 3.5 GB this is the most likely single cause of a
death-spiral.

**Exact change.** `config_edits.json` entries 6-7:

* `enableChunkLoader = false` — this is the load-bearing one.
  `QuarryChunkLoadUtil.isChunkLoadDisabled()` gates **every** chunk-load call in the mod:
  the Advanced Quarry's single-chunk self-load *and* the basic Quarry's whole-area ticket
  (`TileQuarry.java:401-407`, `makeChunkLoadedForMining`), which has no config size cap at
  all and is sized purely by marker placement.
* `chunkDestroyerLimit = 128` — bounds only the Advanced Quarry's working-area size
  (`TileAdvQuarry.java:184`). Useful, but it is the area cap, not the chunk-loading fix.

Chunky-1.3.146.jar is already installed for deliberate force-loading. Leave
`removeCommonMaterialsByCD = true` (line 19) — right call for item spam and memory both. If
you want an area cap on the basic Quarry too, this config has none; either accept that
`enableChunkLoader = false` already defangs it, or set `[machines] quarry = false` and push
players to the now-capped `adv_quarry`.

---

### PT-13 / MAT-05 — Two competing ore systems — major — config

`server/config/thermal-common.toml` has every `World.Features.*.Enable = true`
(lines 8-44). Geolosys' biome modifier only strips **vanilla** features —
`Geolosys :: data/geolosys/forge/biome_modifier/remove_vanilla_ores.json` lists
`ore_coal_lower`, `ore_gold`, `ore_lapis`, `ore_redstone` etc. and nothing from Thermal — so
both systems run. Confirmed in the live dump:
`.../forge/ores/tin.json` = `[geolosys:cassiterite_ore, geolosys:deepslate_cassiterite_ore,
geolosys:deepslate_teallite_ore, geolosys:teallite_ore, thermal:deepslate_tin_ore,
thermal:tin_ore]`; `ores/silver` and `ores/lead` both list Geolosys galena plus Thermal's
blocks; `ores/nickel` lists Geolosys limonite plus `thermal:nickel_ore`. Geolosys' deposits
load on top (`scratch/server.out` lines 806-861, the
`[co.oi.ge.Geolosys/]: Preparing to load deposit datafile` block).

Result: two visually different ore blocks per metal, two raw items, and the Prospector's
Pick / ore-sample loop — the pack's actual discovery mechanic — bypassed by veins the player
trips over.

**Exact change.** `config_edits.json` entries 8-11. `pack/config/thermal-common.toml` does
not exist yet:

```bash
cp "server/config/thermal-common.toml" "pack/config/thermal-common.toml"
```

then set `Enable = false` under `[World.Features.Silver]` (14-16), `[World.Features.Lead]`
(18-20), `[World.Features.Nickel]` (22-24), `[World.Features.Tin]` (38-40). **Leave**
Apatite (10-12), Cinnabar (30-32), Sulfur (34-36), Niter (42-44), Oil Sand (8) and
Rubberwood enabled — Geolosys has no equivalent and Thermal's Crystallizer / Insolator
chains depend on them.

Nothing breaks: every Thermal machine recipe for these metals is tag-driven
(`forge:raw_materials/tin`, `forge:ingots/tin`) and `unify.js` step 7 already routes the
Geolosys clusters to `thermal:*_ingot`. Once this ships, `hide.js` hides `thermal:raw_tin`,
`raw_lead`, `raw_silver`, `raw_nickel` (they become unobtainable). **Do not** strip vanilla
ore gen with a datapack — that risks an oreless world and is not recoverable per-seed.

**Integration win.** Geolosys becomes *the* ore system — one prospecting loop, one raw item
per metal — and Thermal keeps only what it uniquely owns. Say so in the book: "Geolosys
deposits are big and rich; vanilla veins are the backup."

---

### PT-14 — Aluminum and the two coal cokes are dead ends — minor — **FIXED in `unify.js` steps 10-11**

`geolosys:bauxite_ore` generates (`scratch/server.out` lines 838-839) and drops
`geolosys:aluminum_cluster` → `geolosys:aluminum_ingot`, but no mod in `modlist.txt`
consumes `#forge:ingots/aluminum` outside Immersive-Engineering-gated recipes.
`geolosys:bituminous_coal_coke` and `lignite_coal_coke` are producible **only** by Geolosys'
IE compat recipes (`data/geolosys/recipes/compat/immersiveengineering/*.json`), and IE is
not installed. Thermal's Pyrolyzer cannot help: `pyrolyzer_coal.json` takes the literal item
`minecraft:coal`, and Geolosys' coals are only in the `minecraft:coals` tag.

**Exact change.** `unify.js` step 11 adds three `thermal:pyrolyzer` recipes (lignite →
lignite coke + creosote; bituminous → bituminous coke + tar + creosote; anthracite → 2×
`thermal:coal_coke` + tar + creosote). JSON shape copied verbatim from Thermal's own
`pyrolyzer_coal.json` (`type` / `ingredient` / `result` / `experience`). Aluminum gets its
sink from step 10's `crushed_raw_aluminum` path plus its existing AE2 matter-cannon ammo.

**Refuted alternatives are recorded below** — do not add an aluminum→bronze or
platinum→netherite Induction Smelter recipe.

---

### PT-15 — QuarryPlus Book Mover — minor — quest design

`pack/config/quarryplus-common.toml:48` `book_mover = false`, line 57 `mover = true`, line
168 allows `[efficiency, unbreaking, fortune, silk_touch]` on the quarry.

**Exact change: leave `book_mover = false`** (it already matches the mod's shipped default;
`diff` against `server/config/quarryplus-common.toml` is clean). Its real recipe
(`AdditionalEnchantedMiner-1.20.1-1201.1.136.jar :: data/quarryplus/recipes/book_mover.json`)
costs 2× beacon + 4× `quarryplus:mover` + 64 bookshelves + 16 diamonds + 500,000 FE — a
grind escalation this pack explicitly rejects, and it needs Movers built first anyway.

Ship the quest step instead. No `.snbt` under `server/config/ftbquests` mentions quarryplus
today, so this content genuinely has to be written:

> Enchant a pickaxe with Fortune III or Silk Touch, then use the Enchantment Mover
> (`quarryplus:mover`) to transfer it into the Quarry (`quarryplus:quarry`).

**Integration win.** Silk Touch on a quarry is the whole point of pairing QuarryPlus with
Geolosys — silk-touched ore blocks feed Create's crushing wheels and Thermal's Pulverizer
for doubling.

---

### PT-16 / MAT-08 — Two blocks both called "Cinnabar" — minor/polish — datapack lang

`scratch/dupes.json` lists `cinnabar_ore` for `[geolosys, thermal]` and they are genuinely
different materials. `server/local/kubejs/export/loot_tables/geolosys/blocks/cinnabar_ore.json`
drops 4-5 `minecraft:redstone` — this is the pack's **only** redstone supply, since
Geolosys' `remove_vanilla_ores` biome modifier strips `ore_redstone` and
`ore_redstone_lower`. `thermal:cinnabar_ore` drops `thermal:cinnabar`, the raw gem Thermal's
Pulverizer/Crystallizer chain produces and consumes downstream. Geolosys' block is not in
`forge:ores/cinnabar` (Thermal ships that tag with only its own two blocks), so Thermal
recipes correctly never accept it — right behaviour, confusing naming. Both must stay
enabled.

**Exact change.** Create `pack/kubejs/assets/geolosys/lang/en_us.json` (KubeJS assets
override mod jars):

```json
{
  "block.geolosys.cinnabar_ore": "Redstone Cinnabar",
  "block.geolosys.deepslate_cinnabar_ore": "Deepslate Redstone Cinnabar",
  "block.geolosys.cinnabar_ore_sample": "Redstone Cinnabar Sample"
}
```

Display text only — no recipe or tag change. Same class of collision, lower stakes and left
alone: `geolosys:quartz_ore` → quartz, `geolosys:kimberlite_ore` → diamond,
`geolosys:beryl_ore` → emerald.

---

### PT-18 — Vein Mining misses platinum — polish — config

`pack/config/veinmining-server.toml` `groupsList` includes `"#forge:ores/osmium"` but not
`"#forge:ores/platinum"`. Platinum ore vein-mines today only because Geolosys puts it in
both tags — and `unify.js` removes that aliasing. Without this edit, platinum becomes the
one ore that does not vein-mine.

**Exact change.** Replace `"#forge:ores/osmium"` with `"#forge:ores/platinum"` in
`pack/config/veinmining-server.toml`, and apply the identical edit to
`server/config/veinmining-server.toml` for the existing test world.

---

## 2. Materials unification

The full script is `pack/kubejs/server_scripts/unify.js`; its JEI counterpart is
`pack/kubejs/client_scripts/hide.js`. The old `pack/kubejs/client_scripts/unify_jei.js`
has been **deleted** — keeping both would have hidden items the new script deliberately
leaves visible.

**Canonical picks** (from the live tag dump, not the jars):

| Material | Canonical | Retired |
|---|---|---|
| tin, silver, lead, nickel | `thermal:*_ingot` / `*_nugget` | `geolosys:*` |
| zinc | `create:zinc_ingot` / `zinc_nugget` | `geolosys:*` |
| copper nugget | `create:copper_nugget` | `geolosys:copper_nugget` |
| electrum | `thermal:electrum_*` | `createaddition:electrum_*` (soft — see below) |
| netherite nugget | `thermal:netherite_nugget` | none (soft — see below) |
| aluminum, platinum, uranium, coal tiers | Geolosys / Bigger Reactors (sole provider) | — |

### Two rules the script follows, and why

**Rule 1 — never `event.remove({ output: X })` unscoped.** An output filter matches by
output item across *every* recipe type. The previous draft's blanket removal deleted
Create's Mixer electrum recipe
(`createaddition :: data/createaddition/recipes/mixing/electrum.json`, type
`create:mixing`, gold + silver → 2× electrum ingot) outright rather than retargeting it, and
deleted `createdeco:netherite_nugget_from_netherite_ingot`, orphaning the Netherite Coin
press (`createdeco :: data/createdeco/recipes/pressing/coins/netherite_coin.json`, type
`create:pressing`, ingredient matched by literal item id) and making the coin uncraftable.
Every removal in the shipped script is now either an explicit recipe id or scoped to
`minecraft:crafting_shaped` / `crafting_shapeless` / `smelting` / `blasting`.

**Rule 2 — never hide an item whose producer we did not remove.** It is contested whether
KubeJS 2001.6.5 can edit Create's custom recipe types at all in this pack (no
Create↔KubeJS compat addon is installed; `kubejs-forge-2001.6.5-build.26.jar` ships schemas
only for vanilla types, though its generic `JsonRecipeJS` fallback may still match by
output). So the script splits duplicates in two:

* **HARD_RETIRE** — all producers are vanilla-type recipes (Geolosys ships only
  `smelting/`, `blasting/` and `crafting/`). Removed, replaced, and hidden in JEI.
* **SOFT_UNIFY** — a machine still produces them (`createaddition:electrum_*` from the
  Mixer and Crushing Wheels; `createdeco:netherite_nugget` as the coin press's only legal
  input). **Not** removed, **not** hidden. They are kept in the forge tags — which is where
  unification actually matters, because every Thermal and Create machine recipe consumes
  tags, not item ids — plus a best-effort `replaceOutput` and a 1:1 bench conversion for
  tidying.

Accepted consequence: JEI may show two electrum ingots. They are fully interchangeable in
every machine. If an in-game check shows `replaceOutput` **did** retarget
`create:mixing/electrum`, move `createaddition:electrum_*` from `SOFT_UNIFY` to
`HARD_RETIRE` and add them to `hide.js`. That is a one-line promotion, not a rewrite.

### Tag work that is genuinely required (not defensive)

* `forge:nuggets/netherite` holds only `thermal:netherite_nugget` in the live dump, so
  Create Deco's nugget cannot be packed by the Thermal Press. `unify.js` adds it, and
  step 8 replaces Create Deco's own 9→1 craft with a tag-based one that accepts both.
* `forge:ores/osmium` membership is removed from `geolosys:platinum_ore` and
  `deepslate_platinum_ore` on both item and block sides (see PT-02 above).

### MAT-07 — Two flax crops — minor — config + one removal

`scratch/dupes.json` lists `flax_block` for `[supplementaries, thermal]`; `ids.json` has
`supplementaries:flax / flax_seeds / flax_block / wild_flax` **and** `thermal:flax /
flax_seeds / flax_block`. The live tag `forge:crops/flax` = `[supplementaries:flax,
thermal:flax]` — the game already agrees they are one material — and both craft to
`minecraft:string`. Both generate wild patches, so the player farms two identical crops with
two seeds that are not interchangeable in the ground.

**Exact change.** Keep Thermal's (wired into the Phytogenic Insolator via
`thermal/recipes/machines/insolator/insolator_flax.json` and the Press packing recipes;
Supplementaries' is bench-only). `cp server/config/supplementaries-common.toml
pack/config/supplementaries-common.toml`, then lines 222-224:

```toml
[functional.flax]
	enabled = false
	wild_flax = false
```

`unify.js` step 4c removes `create:milling/compat/supplementaries/flax`, which would
otherwise try to resolve a deregistered ingredient every reload.

**Integration win.** One flax, one seed, one Insolator recipe — the cozy player plants a
crop the tech player's machine can automate.

---

## 3. Cozy — food, farming, decor, seasons

### Farm & Charm's Serene Seasons tags are dead (wrong path) — major — datapack

`letsdo-farm_and_charm-forge-1.0.14.jar` ships its season data at
`data/sereneseasons/blocks/*.json` and `data/sereneseasons/items/*.json` — **no `tags/`
segment**. Minecraft's loader only reads `data/<ns>/tags/<registry>/...`, so the files are
unreachable. Contrast: Farmer's Delight, Supplementaries, Thermal Cultivation and Serene
Seasons itself all correctly use `data/sereneseasons/tags/{blocks,items}/*.json`. Seven
crops therefore ignore the pack's tuned 9-day sub-seasons.
`server/config/sereneseasons/fertility.toml` has `seasonal_crops = true`,
`out_of_season_crop_behavior = 0` (grow slowly, not break) and `crop_tooltips = true`.

**Exact change.** Add `pack/kubejs/server_scripts/seasons_tags.js` (KubeJS
`ServerEvents.tags` is already proven in this pack — `unify.js` uses it):

```js
// Farm & Charm ships its Serene Seasons tags at data/sereneseasons/blocks|items/
// instead of data/sereneseasons/tags/blocks|items/, so the game never loads them.
// Re-file them by hand. Values copied from the mod's own (misplaced) files.
ServerEvents.tags('block', event => {
  event.add('sereneseasons:spring_crops', 'farm_and_charm:onion_crop', 'farm_and_charm:strawberry_crop')
  event.add('sereneseasons:summer_crops', 'farm_and_charm:corn_crop', 'farm_and_charm:tomato_crop')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:barley_crop', 'farm_and_charm:lettuce_crop')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:oat_crop')
})
ServerEvents.tags('item', event => {
  event.add('sereneseasons:spring_crops', 'farm_and_charm:onion', 'farm_and_charm:strawberry_seeds')
  // corn's seed item is farm_and_charm:kernels, NOT farm_and_charm:corn -
  // kernels is the unconditional loot-table drop and the item you plant.
  event.add('sereneseasons:summer_crops', 'farm_and_charm:kernels', 'farm_and_charm:tomato_seeds')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:barley_seeds', 'farm_and_charm:lettuce_seeds')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:oat_seeds')
})
```

Two traps this version avoids: **corn's seed is `farm_and_charm:kernels`**, not
`farm_and_charm:corn` (the mod's own misplaced `items/summer_crops.json` says so; `corn` is
only the max-age food drop, so tagging it puts the season tooltip on the wrong item), and
**Farm & Charm ships no winter-fertile crop at all** (both winter tag files are empty
arrays) — making oat winter-fertile would be an invented design change, not a restoration,
so oat is filed with autumn here. Onion correctly uses the food item as its own seed (no
`onion_seeds` exists).

`farm_and_charm:onion_crop` also appears in Farm & Charm's misplaced
`unbreakable_infertile_crops.json`; with `out_of_season_crop_behavior = 0` that tag has no
visible effect, so it is not restored.

---

## 4. Worldgen and exploration

### wg-01 — Waystones and VillagersPlus never reach Towns & Towers villages — major — config

`waystones-common.toml` sets `spawnInVillages = true`, but Waystones' injection is
data-driven: `unzip -l waystones-forge-1.20.1-14.1.20.jar` shows three data namespaces
(`minecraft`, `repurposed_structures`, `waystones`) and its pool additions live only under
`data/repurposed_structures/pool_additions/villages/<biome>/houses.json` plus vanilla
`minecraft:village/*` pools. Grepping every Waystones json for `towns_and_towers`, `kaisyn`
or `villagesandpillages` returns nothing. VillagersPlus injects profession-house weights via
a mixin (`com/lion/villagersplus/util/StructurePoolAddition.class`) hardcoded to vanilla
pools. Towns & Towers registers its villages as a wholly separate structure set
(`data/towns_and_towers/worldgen/structure_set/towns.json`), as does Villages & Pillages
(`village_witch.json`). Neither hook system ever touches them.

There is no datapack hook to extend a hardcoded mixin, so full parity needs a Java mod — out
of scope.

**Exact change (config, not KubeJS).** Make T&T towns the special find rather than the norm,
so most villages the players stumble into *do* get waystones and profession houses. In
`pack/config/sparsestructures.json5` **and** `server/config/sparsestructures.json5` (the
latter is what the running server reads):

```json
{ "structure": "towns_and_towers:towns", "factor": 4 }
```

**Do not** attempt the `exclusion_zone.other_set: "#tag"` idea — see Refuted #6.

### wg-03 — Regions Unexplored biome coverage — polish — no action

Largely a non-issue: RU merges its biomes into the **vanilla** `data/minecraft/tags/
worldgen/biome/is_forest|is_taiga|is_jungle|is_savanna|is_mountain` tags, which is exactly
what YUNG's Better Strongholds and Better Dungeons check as required entries. Residual gap
is ~6 biomes (`cold_deciduous_forest`, `tropics`, `cold_boreal_taiga`, `frozen_pine_taiga`,
`pine_slopes`, `ashen_woodland`), not "dozens". Not worth a datapack, and a bare tag entry
pointing at a nonexistent id can hard-fail datapack load — note that
`regions_unexplored:smouldering_woodland` does **not** exist (the biome is `ashen_woodland`).

---

## 5. Client and QoL

### Remove `dynamic-torches-5.3.jar` — blocker — mod removal

See `scratch/mod_changes.json`. Short version: it is not a client light renderer, it is a
bundled datapack (`data/dt/functions/*.mcfunction`) whose `tick.mcfunction` runs every tick,
spawning marker entities that `fill` and clear real light blocks in the world, for an
uncapped trigger set (`config.mcfunction` defaults: players, held items, blazes, glow
squids, lit creepers, fire, mob-held items, arrows, fireballs, magma cubes — all `1`, with
no override shipped in `server/config` or `server/world/serverconfig`). Unthrottled
per-tick entity churn plus block writes on a 3.5 GB heap.

Replacement is already installed and already capped: TorchMaster's Feral Flare Lantern
(`server/config/torchmaster.toml` — `feralFlareRadius=16`, `feralFlareTickRate=5`,
`feralFlareLanternLightCountHardcap=255`) becomes the pack's one sanctioned carry-light.
Zero dependents on `mr_dynamic_torches` across all mods and KubeJS, so removal is clean.
Note it in the pack README so it is not re-added.

Caveat on the framing: do **not** claim it reproduces TorchMaster's documented radius-based
"badly compressed packet" corruption — the mechanisms differ (dynamic-torches has no
radius, one block per lit entity). The evidenced risk is TPS and entity churn, which is
enough.

### `pack/options.txt` — polish — ship it

Only the lines that matter; packwiz merges on first install. Two things worth stating:

* The Vein Mining activation mapping is named **`key.veinmining.activate.desc`**, not
  `key.veinmining.activate` — `VeinMiningKey.class` registers the `.desc` string and
  `assets/veinmining/lang/en_us.json` has no bare `activate` key. An `options.txt` line
  using the wrong name binds nothing silently.
* This is a convenience, not a rescue. `pack/config/veinmining-server.toml:6-8` sets
  `maxBlocksBase = 64` — "the maximum number of blocks to vein mine **without the
  enchantment**" — and the client-side activation default for the un-enchanted mode is
  `STANDING`, i.e. it already fires with no keypress. The key drives the enchanted
  bonus-range mode.

Xaero's Minimap and World Map sharing `M` is intentional Xaero behaviour, not a collision.

---

## 6. Story engine and multiplayer

### STORY-01 — Two players get separate quest progress — blocker — KubeJS

FTB Quests keys progress to a **team**
(`FTBQuestsKubeJSWrapper.class` → `getTeamForPlayerID` → `getOrCreateTeamData`), and FTB
Teams gives every player a singleton `player` team on first join
(`server/world/ftbteams/{party,server,player}`). Nothing in the pack creates a party — there
is no ftbteams config anywhere and `pack/kubejs/server_scripts/init.js` is a one-line stub.
Joining a party **later abandons the joiner's progress**, so this must happen on session
one.

**Exact change.** Create `pack/kubejs/server_scripts/story_team.js`:

```js
// Cozy Tech Pack - one shared party so quest progress is shared.
const PARTY = 'Cozy'

PlayerEvents.loggedIn(event => {
  const p = event.player
  if (p.stages.has('cozy_party')) return   // run once per player, ever
  const n = p.username
  // Player 2+ : join. Fails harmlessly ("not invited") if the party isn't there yet.
  server.runCommandSilent(`execute as ${n} at ${n} run ftbteams party join ${PARTY}`)
  // Player 1 : create. Fails harmlessly ("already in a party") if the join above worked.
  server.runCommandSilent(`execute as ${n} at ${n} run ftbteams party create ${PARTY}`)
  server.runCommandSilent(`execute as ${n} at ${n} run ftbteams party settings free_to_join true`)
  p.stages.add('cozy_party')
})
```

Use the **global `server` binding** — it is in scope for every `server_scripts` file
(`BuiltinKubeJSPlugin.registerBindings`); do not assign `event.server` to a local first.
`PlayerEvents.loggedIn`, `server.runCommandSilent` and `player.stages` are all verified in
`kubejs-forge-2001.6.5-build.26.jar`; the command literals (`party`, `create`, `invite`,
`join`, `accept`, `settings`) are verified in `FTBTeamsCommands.class`.

Verify on first boot that `ftbteams party settings free_to_join true` tab-completes; the
property is real (`ftbteamsconfig.ftbteams.free_to_join` in lang) but the subcommand shape
was not confirmed statically. If it doesn't, drop that line and use invite/accept.

Manual fallback (run as an op — `ops.json` is currently empty): Player A
`/ftbteams party create Cozy` then `/ftbteams party invite <PlayerB>`; Player B
`/ftbteams party accept`. The automated path is unaffected by op status because
`runCommandSilent` uses the server's own elevated source.

**Test:** both log in, one completes a quest, the other opens the book and sees it checked.

### STORY-02 — `minecraft:village` is a tag, not a structure key — major — quest design

`StructureTask.class` stores `Either<ResourceKey<Structure>, TagKey<Structure>>` and
branches on a leading `#`. The real vanilla keys are `minecraft:village_plains`,
`village_desert`, `village_savanna`, `village_snowy`, `village_taiga` — there is no
`minecraft:village` structure, only the tag. An unresolvable key is stored as-is and only
fails at check time, which is why the smoke test reported zero errors.

**Exact change.**

```
{ id: "397E18D087A24BA3", type: "structure", structure: "#minecraft:village" }
```

Strictly better for this pack: Towns & Towers appends 26 of its own villages to that same
tag, so one task covers vanilla *and* modded. For non-tag tasks use verified keys —
`minecraft:village_plains`, `towns_and_towers:village_meadow`. **`nova_structures:hamlet`
appears in an earlier draft; that namespace ships inside `dungeons-and-taverns-3.0.3.f.jar`
(modId `mr_dungeons_andtaverns`) and `hamlet.json` does exist, but prefer the two verified
ids above.**

Housekeeping: this is the only `structure`-type task in the tree and it sits in
`ztest.snbt` — chapter title "Compiler Test", subtitle "delete me". Its JSON source is
already gone from the compile pipeline, and `compile_quests.py` purges stale compiled
chapters under `pack/config/...` — but it never touches `server/config/...`, which is the
running world's save data. **Manually delete
`server/config/ftbquests/quests/chapters/ztest.snbt` before shipping.** A chapter subtitled
"delete me" is visible in the book right now, which is precisely the wrong first impression
for the cozy player.

### STORY-06 — Never set `team_reward: true` on a stage reward — major — quest design (hard rule)

Stages are per-player (`KubeJSStageProvider.class` → `Stages.get(Player).add(String)` +
`sync(ServerPlayer)`); quest progress is team-wide. `team_reward: true` means exactly one
team member receives the reward, so a stage reward with it silently locks the other player
out of every stage-gated recipe. Stage rewards already default to invisible auto-claim
(`StageReward` constructor sets `RewardAutoClaim.INVISIBLE`), so both players get them
without clicking.

```
{ id: "...", type: "stage", stage: "cozy_smelting", remove: false }
```

`stage` and `remove` are the only keys `StageReward.writeData` emits. Reserve
`team_reward: true` for bulky one-off item rewards. Repair a desync with
`/kubejs stages add <player> <stage>`.

**Registry-id caveat, unresolved:** one verification pass read the registered id for both
the reward and task type as `"gamestage"`, not `"stage"` (from the string literal preceding
the `StageReward` constructor reference in `RewardTypes.class`). The current
`ztest.snbt` uses `type: "stage"`. Before authoring stage rewards at scale, add one to a
chapter, reload, and check it appears in the book — if it silently doesn't register, switch
to `"gamestage"`. Getting this wrong means a permanently-locked recipe with no visible way
to unlock it, which is worse than not gating at all.

### STORY-09 — `player_command` is a dead key — minor — quest design

`CommandReward.class` reads exactly three fields — `command`, `elevate_perms`, `silent`
(plus `DEFAULT_COMMAND = "/say Hi, @p!"`). `player_command` was the 1.16/1.18 spelling;
unknown SNBT keys are dropped without warning.

```
{ id: "7F0D92FD2208D776", type: "command", command: "/say compiled reward", elevate_perms: true, silent: true }
```

Substitutions available in the command string: vanilla selectors, `{x} {y} {z}`, `{quest}`,
`{chapter}`, `{team}`. **`{team}` is the one to use in a two-player pack** — e.g.
`"/say {team} finished the smelting line"`. Both `pack/` and `server/` copies of
`ztest.snbt` are already clean (commit `8ba6204`); do not re-apply.

### STORY-10 / STORY-11 — Easy NPC as the quest-book handoff — minor — datapack

Ship story NPCs as datapack presets at `data/<ns>/preset/*.npc.snbt`
(`DataPresetDataFiles.class` concatenates the resource paths `easy_npc/preset` and
`preset`). Author in game — the dialog editor writes the UUID-keyed `DialogDataSet`
correctly, and hand-writing is fragile because `DialogDataEntry` derives its id via
`UUID.nameUUIDFromBytes(label)`.

1. `/easy_npc preset export custom @e[type=easy_npc:villager,limit=1,sort=nearest] mayor`
2. copy `server/easy_npc/preset/<skin_model>/mayor.npc.snbt` →
   `pack/kubejs/data/cozytech/preset/mayor.npc.snbt`
3. spawn from a quest command reward (`elevate_perms: true`):
   `/easy_npc preset import data cozytech:preset/mayor.npc.snbt 120 65 -40`
   — use `import`, not `import_new`, so re-running is idempotent.

Ship `.npc.snbt` (or `.npc.nbt`). **Not `.npc.json`** — `PresetExportFormat` recognises it
but `PresetFileHandler.load()` refuses it ("JSON preset format is not supported yet").

**Action macros.** Use `@initiator`, never `@p` — `@p` resolves against the command source,
which for an NPC action is the NPC's own position, so in a two-player pack it can resolve
to whoever is standing closer rather than whoever clicked. Macro set from
`ActionUtils.class`: `@initiator`, `@initiator-uuid`, `@npc`, `@npc-uuid`, plus
`/success_message`, `/info_message`, `/warn_message`, `/error_message` (these are rewritten
internally into `/title @initiator ...`, so no selector is needed).

The quest-book button is the exception — `open_book` takes **no arguments**
(`FTBQuestsCommands.class` has no argument child for it), so match the pack's own working
pattern in `pack/kubejs/data/valley/easy_npc/preset/tobin.npc.snbt`:

```
{ Type: "COMMAND", Cmd: "/ftbquests open_book", ExecAsUser: 1b, PermLevel: 0 }
{ Type: "COMMAND", Cmd: "give @initiator bountiful:decree 1", ExecAsUser: 0b, PermLevel: 2 }
```

`ExecAsUser: 1b` runs it as the interacting player, so the player *is* the sender and no
selector is required. NBT tag names (`Cmd`, `ExecAsUser`, `PermLevel`, `Type`) are verified
in `ActionDataEntry.class`.

**Gating dialogs.** `ConditionType` values: `ADVANCEMENT`, `HAS_ITEM_IN_INVENTORY`,
`HAS_ITEM_IN_HAND`, `PLAYER_TAG`, `SCOREBOARD`, `TEAM`, `EXPERIENCE_LEVEL`,
`EXECUTION_LIMIT`, `CHANCE`, `TIME_OF_DAY`, `WEATHER`, `RELATIONSHIP`. **KubeJS stages are
not on that list** — bridge with a scoreboard: add a second quest reward
`{ type: "command", command: "/scoreboard players set {p} cozy_stage 1", elevate_perms: true, silent: true }`
and condition the button on `SCOREBOARD`. (`{p}` is FTB Quests' own player placeholder —
deterministic, unlike `@p`.) `EXECUTION_LIMIT` is what makes a story NPC feel authored: a
button that fires once.

**Security.** The relevant cap for a quest-reward-triggered import is
`maxAdminImportedCommandLevel` in `server/config/easy_npc/security.cfg`, not
`serverTrustedCommandLevel` (that one applies to imports with no player context). Both are
`ADMINS` today, so behaviour is unchanged — but tune the former if this is ever split.

**Integration win.** The quest book stops being a keybind the cozy player has to remember
and becomes a person in the world who hands it to them.

### STORY-13 — Quest file settings — minor — config

Only two of the seven proposed keys are real changes; the rest restate compiled-in defaults
(`detection_delay` 20, `default_reward_team` false, `drop_book_on_death` false,
`drop_loot_crates` false, `grid_scale` 0.5). Add to
`pack/config/ftbquests/quests/data.snbt`:

* `progression_mode: "flexible"` — `BaseQuestFile` initialises `LINEAR`, so the book is
  currently in strict mode where a quest must be **fully completed** before a dependent one
  can be started. Wrong default for a player who hates grind.
* `lock_message: "Not yet. Finish the quest before this one."` — defaults to empty, so a
  locked quest currently says nothing.

Note `default_hide_dependency_lines` (already in the file) is a **Chapter**-level key, not a
file-level one; sitting in `data.snbt` it is silently ignored. Harmless, but don't cite it
as evidence of anything.

### STORY-15 — Chunky won't resume after a restart — polish — config

`server/config/chunky/config.json` has `"continueOnRestart": false`. Pre-generation is the
single biggest lever for keeping an 8 GB M2 Air smooth, and a meaningful-radius pre-gen
outlasts at least one restart. Ship `pack/config/chunky/config.json` with
`continueOnRestart: true` (full file in `config_edits.json` entry 16), mirror to
`server/config/`, `packwiz refresh`, then run once before the pair starts:
`/chunky world minecraft:overworld` · `/chunky center 0 0` · `/chunky radius 3000` ·
`/chunky start`.

### STORY-18 — Voice chat config isn't shipped — minor — config

`server/config/voicechat/voicechat-server.properties` sets `port=24454` on a **separate UDP
socket** (the file itself warns against reusing the game port), and `ls pack/config` shows no
`voicechat` directory — none of it is reproducible from the pack. Copy the file across
unchanged and `packwiz refresh`. Then confirm UDP 24454 is reachable: this is the single most
common "Unable to connect" cause and it is invisible in game. On a tunnel that forwards one
port only, set `port=-1` or `voice_host=<hostname>:24454`. Keep `enable_groups=true` — with
48-block proximity audio, groups are what keeps the two of them talking when one is mining
and the other is farming.

---

## Checked and fine — do not re-open

**Power and tech**

* **SU↔FE conversion works.** `server/config/createaddition-common.toml`: `max_stress=16384`
  (36), `fe_at_max_rpm=480` (39); alternator `generator_efficiency=0.75` (107),
  `capacity/max_output=5000` (110/113); electric motor `capacity=5000` (56),
  `min_consumption=8` (59), `max_input=5000` (62), `rpm_range=256` (65); wires
  small 1000 in/out (6, 9), large 5000 (21, 26), lengths 16/32 (18, 15),
  `connector_allow_passive_io=true` (23), `connector_ignore_face_check=true` (28).
  Alternator will not spin below 32 RPM. Use these numbers verbatim in the quest book.
* **Thermal RF *is* Forge Energy.** `server/world/serverconfig/thermal-server.toml:80`
  `"Standalone Redstone Flux" = false`. QuarryPlus implements `IEnergyStorage` directly
  (`com/yogpc/qp/machines/PowerTile.class`). Reactor/Turbine Power Tap → Fluxduct → Quarry
  works; Alternator → Connector → Fluxduct → Thermal machine works.
  `thermal:energy_duct` is craftable independent of the disputed parts tree
  (`thermal_dynamics :: data/thermal/recipes/energy_duct_4.json` = 6 redstone + 2 lead + 1
  glass → 4).
* **Every tech-mod version range is satisfied** and the server boots clean.
  biggerreactors 0.6.0-beta.10.5 ↔ phosphophyllite 0.7.0-alpha.0.2 ↔ quartz
  0.2.0-alpha.0.1 (exact); ae2 15.4.10 ↔ guideme 20.1.15 ↔ jei 15.56.0.205;
  thermal_expansion 11.0.1.29 ↔ cofh_core 11.0.2.56 ↔ thermal 11.0.6.70;
  createaddition 1.3.3 / Steam 'n' Rails 1.7.3 / Create Deco 2.0.3 all satisfied by
  create 6.0.8; quarryplus ↔ forge 47.4.10. `scratch/server.out` ends "Reloaded with no
  KubeJS errors!".
* **Ore gen for Create zinc, Thermal ores and BR uranium is intact**, and AE2↔BR and
  Thermal↔BR cross-recipes already ship
  (`data/biggerreactors/recipes/compat/appliedenergistics/*` ×5,
  `data/thermal/recipes/machine/biggerreactors/pulverizer_mod_*.json` ×6).
* **JEI is the only recipe viewer** — no REI, no EMI. `server/config/ae2/client.json` has
  `search.useExternalSearch: false` with `syncWithExternalSearch: true`, so AE2 terminals
  and JEI stay in sync.

**Materials**

* **`forge:ingots/<metal>` already unifies.** Every mod writes with merge semantics
  (`replace: false` or omitted). Live: `forge/ingots/tin` = `[geolosys:tin_ingot,
  thermal:tin_ingot]`; `forge/raw_materials/tin` = `[geolosys:tin_cluster, thermal:raw_tin]`.
  Thermal's machine recipes consume the tag, so a Geolosys tin cluster already works in the
  Induction Smelter *before* any of this work. Same for silver, lead, nickel, and for
  `plates/electrum` = `[createaddition:electrum_sheet, thermal:electrum_plate]`. The tag
  block in `unify.js` is defensive, not load-bearing.
* **coal / gold / lapis / quartz "duplicates" are not conflicts.** Geolosys' 
  `remove_vanilla_ores.json` deliberately strips the vanilla features, and its loot tables
  name the `minecraft:` result explicitly. `ae2:quartz_block` is Certus — a different
  mineral, false positive on registry path.
* **Copper nugget triple-registration is tag-unified.** Live
  `forge/nuggets/copper` = `[create, geolosys, thermal]` — CoFH registers Thermal's at
  runtime even though its jar ships no tag file. Only JEI clutter remained, and `unify.js`
  retires the Geolosys one.

**Cozy**

* **Aquaculture 2 fish already work in Farmer's Delight cooking.** FD's
  `cooking/fish_stew.json` keys on `forge:raw_fishes`; Aquaculture ships that tag with 28
  species, `replace: false` on both sides.
* **Create / Farmer's Delight / Let's Do flour, dough and milk tags are already bridged**
  — all `replace: false`, all merging. Cabbage has no duplicate anywhere in `ids.json`.
* **Cooking for Blockheads is item-agnostic** — no per-mod allowlist in its config, no
  compat files in its jar. It already sees FD and Let's Do foods.
* **Farm & Charm's dead `unbreakable_infertile_crops` entry has no visible effect**
  under `out_of_season_crop_behavior = 0`.
* **Ribbits / Duckling / Domestication Innovation / Perfect Plushies / Comforts** deps all
  satisfied (yungsapi 4.0.6, geckolib 4.8.4, citadel 2.6.3).

**Worldgen**

* **TerraBlender weighting already gives "RU common, vanilla still exists".**
  `vanilla_overworld_region_weight = 10` vs RU 11+8+1 = 20 → 2:1. Nether 14 vs 10 → ~1.4:1.
  Matches the stated goal; leave it.
* **Lootr's chest conversion is unrestricted** — every blacklist in `pack/config/lootr-common.toml`
  is empty, and Deeper and Darker / Dungeons and Taverns / When Dungeons Arise all ship
  vanilla chest blocks. Zero per-mod entries needed.
* **Explorer's Compass has an empty blacklist** and builds its list from the structure
  registry, so every structure mod surfaces automatically.

**Client / QoL**

* **JEI plugin coverage is intact** for Create, Create Crafts & Additions, AE2, Farmer's
  Delight, Bigger Reactors and the whole Thermal Series (via
  `cofh_core :: CoreJeiPlugin.class`, which the sub-mods ride on). Create Deco has no
  plugin but uses vanilla shaped recipes, which JEI surfaces anyway.
* **Client-only mods are correctly excluded from the server** (Embeddium, Entity Culling,
  ImmediatelyFast, Xaero ×2, Sound Physics), and the both-sides perf mods correctly are not
  (Canary, FerriteCore, ModernFix, Memory Leak Fix, JEI).
* **Xaero Minimap + World Map sharing `M` is intentional**, not a collision.
* **ImmediatelyFast / Embeddium / Sound Physics have no conflict surface here** — their
  known 1.20.1 Forge issues are Iris/Oculus-specific and no shader mod is installed
  (`grep -iE 'iris|oculus|shader' scratch/pack_manifest.tsv` → 0).
* **`pack_manifest.tsv` mislabels the four FTB mods "(NeoForge)"** — the jars are
  `ftb-*-forge-*.jar` and load fine on Forge 47.4.10. Display-label bug in the manifest
  generator, not a loader mismatch.

**Story**

* **The FTB Quests stage plumbing already resolves to KubeJS with no extra mods.**
  `server/config/ftbxmodcompat.snbt` `stage_selector: "default"`; `StagesSetup.class`
  prefers KubeJS → Game Stages → vanilla; `mods.json` (128 entries) has `kubejs` 2001.6.5
  and neither `gamestages` nor `recipestages`. The GameStages mod is **not** required. One
  caveat: without it there is no scriptable stage-changed event.
* **Reward-table linkage, chapter group, task types and Lootr break settings all check out.**
  Chapter group `B00129D2A12C0DC3` matches `chapter_groups.snbt`;
  `table_id: 4525898250150043917L` == `0x3ECF387AB1C1610D` == the reward table's `id`;
  `observe_type: 0` = `BLOCK`; a leading `/` on a command reward is fine. Lootr's
  `disable_break=false` + `enable_break=false` means normal breaking — what the cozy player
  expects. Corpse `force_time = -1` means a non-empty corpse never despawns. FTB XMod
  Compat's ftbchunks / ftbranks / itemfilters / ftbfiltersystem branches are inert and cost
  nothing on the heap.
* **Bountiful already has pack-specific bounties and a copper-cost board.**
  `pack/kubejs/data/bountiful/bounty_pools/valley/{tech,cozy}_{objectives,rewards}.json`
  and `bounty_decrees/valley/{tech,cozy}.json` exist and are tuned to this pack's items;
  `pack/kubejs/server_scripts/valley_gates.js:206-220` already removes the diamond board
  recipe and re-adds it with copper (`valley:cheap/bountyboard`). `server/config/bountiful/`
  being empty is the mod's default-extraction folder, not where pack content lives.
* **The pack already has an external Patchouli book** at
  `pack/patchouli_books/valley_journal/book.json` ("Josie's Journal"), with an empty
  `en_us/entries/field_notes/` folder waiting for exactly the mechanical pages a second book
  would have duplicated. It is not yet packwiz-tracked (`grep -c patchouli_books
  pack/index.toml` → 0) — that is the real open item, not authoring a new book.
* **`tools/scripts/compile_quests.py` and `validate_quests.py` already validate quest item
  ids and dependencies** against `ids.json`, with `story/quests/_custom_ids.txt`
  whitelisting the 48 `valley:*` items registered in
  `pack/kubejs/startup_scripts/valley_items.js`. No third validator is needed.

---

## Refuted ideas — do not re-propose

Each of these was investigated, found wrong or already done, and is recorded so nobody
spends the afternoon again.

1. **"Blanket `event.remove({ output: retired })` in unify.js is safe."** It is not. An
   output filter matches across every recipe type, including `create:mixing`. It deleted
   Create's Mixer electrum recipe outright instead of retargeting it, and orphaned Create
   Deco's Netherite Coin press by removing the only producer of
   `createdeco:netherite_nugget`. Removals must be by explicit id or scoped to vanilla
   types. **Fixed in the shipped script.**

2. **"Add a `thermal:pulverizer` recovery recipe for uranium / a second smelting recipe for
   `geolosys:uranium_cluster`" (PT-03).** Already present at `unify.js` step 9 with
   identical input, output, xp and cook time. Adding it again registers duplicate furnace
   and blast entries and JEI shows both. Also: the pulverizer draft used an `energy: 4000`
   key that does not exist in this Thermal version — real pulverizer recipes use
   `energy_mod` (a multiplier). A jar/datapack scan will always report "0 recipes" for a
   KubeJS-added recipe; that is a scan blind spot, not a missing fix.

3. **"Geolosys `enableOsmium = false` unbricks platinum" (MAT-02 as originally framed).**
   The flags are dead code (PT-07) — flipping them fixes nothing. The real fix is the
   `forge:ores/osmium` tag removal plus the crushed/cluster smelting fallbacks now in
   `unify.js`.

4. **"`geolosys:osmium_cluster` and `create:crushed_raw_osmium` are orphans — hide them in
   JEI" (PT-06).** `osmium_cluster` has had a smelting and blasting recipe in `unify.js`
   since before the audit, and `crushed_raw_osmium` is *actively produced* by crushing
   Geolosys platinum ore (both `forge:ores/osmium` crushing recipes are live because the tag
   is non-empty). Hiding an item a machine emits, while its producing recipe stays visible
   in JEI's Crushing category, is the exact disconnected experience the brief forbids. Only
   `create:crushed_raw_quicksilver` is genuinely unreachable, and `hide.js` hides that one.
   Also: `event.hide()` takes one ingredient — there is no array overload on
   `HideJEIEventJS` in this build.

5. **"Retire `thermal:copper_nugget`/`createdeco:netherite_nugget` and hide them" (PT-08).**
   `forge:nuggets/copper` is populated by Create and Geolosys only in the jars; Thermal's is
   registered at runtime by CoFH (live dump confirms all three). Choosing Thermal's as
   canonical while replacing every tag-matched output would have made
   `geolosys:copper_nugget` unobtainable *and* left the survivor unable to round-trip to an
   ingot — a dead end that did not exist before. `forge:nuggets/netherite` is shipped by no
   mod at all; the fix is the explicit `event.add` in `unify.js`, not an output rewrite.

6. **"Give Towns & Towers / Villages & Pillages an `exclusion_zone` pointing at a `#tag`"
   (wg-02).** Vanilla's `minecraft:random_spread` `exclusion_zone.other_set` is a single
   structure-set reference codec — `#` is not a legal ResourceLocation character, so the
   structure set would fail to parse. The `#tag` pattern cited as precedent is Repurposed
   Structures' *own* custom `repurposed_structures:advanced_random_spread` placement type
   with a differently-named `super_exclusion_zone` field. Villages & Pillages'
   `village_witch.json` also uses `yungsapi:enhanced_random_spread`, whose field is
   `enhanced_exclusion_zone` — an `exclusion_zone` block there is a silent no-op, because
   Mojang's codecs ignore unrecognised keys. Use `customSpreadFactors` instead (wg-01).

7. **"Regions Unexplored biomes are excluded from YUNG's structures" (wg-03).** RU merges
   into the *vanilla* `minecraft:is_forest/is_taiga/is_jungle/is_savanna/is_mountain` tags,
   which is what those mods check as required entries. Residual gap ≈6 biomes. Also
   `regions_unexplored:smouldering_woodland` does not exist — the biome is `ashen_woodland`,
   and a bare tag entry naming a nonexistent id can hard-fail datapack load.

8. **"Remove Thermal Cultivation to fix the tomato/onion/strawberry/barley/rice
   duplication."** It resolves only rice. Strawberry also comes from `letsdo-bakery` and
   `farm_and_charm`; barley also from `regions_unexplored`; tomato from `candlelight`,
   `farm_and_charm` and `farmersdelight`. Thermal Cultivation also hard-depends on
   `thermal` and ships its **own** Serene Seasons tags — it is better integrated than
   `letsdo-candlelight`, which ships none.

9. **"Handcrafted vs Macaw's Furniture overlap."** ~193 combined chair/table entries, but
   different namespaces, different tags, different recipes — additive JEI clutter, no
   functional conflict. And the justification for keeping both was mostly fabricated:
   Handcrafted has **no** cabinets (Macaw's has 62), and **neither** mod has drying racks or
   cuckoo clocks. Cushions are genuinely Handcrafted-only (16 vs 0). Keep both; change
   nothing.

10. **"Flip ModernFix `mixin.perf.dynamic_resources=true` for the RAM win."** The author
    disables it by default precisely because it is not universally safe, and this exact
    build's `modernfix.mixins.json` compiles compat patches only for `ctm`, `ldlib` and
    `supermartijncore` — while the mod's own lang file names an `ae2` compat patch that this
    version does not ship, and AE2 *is* installed. Create + addons and three Macaw's mods
    are in the same nonstandard-model-API risk class. The quoted 55% figure comes from a
    different pack. Not worth the "crash on startup or missing textures" risk against the
    explicit "not glitchy" requirement.

11. **"`options.txt` is required because Vein Mining's flagship feature is invisible."**
    The core anti-grind mechanic is `maxBlocksBase = 64` — up to 64 blocks with **no**
    enchantment and, at the mod's default client `activationState = STANDING`, no keypress
    at all. The unbound key drives the enchanted bonus-range mode only. We still ship
    `options.txt` (it is a genuine convenience) but with the correct mapping name
    `key.veinmining.activate.desc` and a deliberately small set of lines, because a
    packwiz-tracked `options.txt` re-syncs on every pack update and will stomp personal
    render-distance and graphics tweaks.

12. **"Corpse is owner-only, so neither player can help the other" (STORY-16).** The live
    world config `server/world/serverconfig/corpse-server.toml` already has
    `only_owner = false`. Forge seeds `defaultconfigs` into a world's `serverconfig` only at
    world creation and never re-syncs, so editing `pack/defaultconfigs/corpse-server.toml`
    changes nothing for this world.

13. **"`ftbxmodcompat.snbt` / `easy_npc/security.cfg` are missing from the pack"
    (STORY-03, STORY-07, STORY-08).** Both exist in `pack/config/` and already carry the
    correct values (`stage_selector: "kubejs"`,
    `executeAsUserCommandAllowList.ALL=ftbquests,trigger,me`). The `server/config/` copies
    are the stale ones. **Copying server → pack would regress the fix.** The genuine open
    action is `packwiz refresh`, since `pack/index.toml` has no entries for either file.

14. **"Patchouli books in `kubejs/data` never register, so author a new Cozy Tech
    Handbook" (STORY-04).** The registration mechanism claim is correct — Patchouli
    enumerates mod containers plus the external `patchouli_books/` folder, not the datapack
    manager — but the pack already has `pack/patchouli_books/valley_journal/book.json` with
    a "Field Notes" category built for exactly this content. A second book with a different
    voice and no cross-links is a disconnected experience by construction. Populate
    `valley_journal` and `packwiz refresh` it.

15. **"`/place structure minecraft:village` fails from console because the console source
    has no position" (STORY-05).** The diagnosis of the *symptom* is right —
    `minecraft:village` is a tag, not a structure — but the mechanism is invented:
    `MinecraftServer.createCommandSourceStack()` always supplies a position (world spawn).
    Also, no `/place` command exists anywhere in this pack; the only real occurrence of
    `minecraft:village` is the FTB Quests structure **task** (STORY-02).

16. **"Chapters can depend on other chapters, so a finished chapter reveals the next"
    (STORY-14).** `Chapter.class` has no dependency list at all — only `Quest.class` does.
    `hide_quest_until_deps_visible` / `_complete` on a chapter are per-chapter **defaults**
    for the per-quest fields, not chapter-visibility gates. It is also dead in this pack:
    every dependent quest in `act1`–`act5` pins `hide_until_deps_complete: true`
    explicitly, and `Quest.isVisible()` returns from that branch before it ever reads the
    visibility Tristate. The good news — sequential reveal already works, via the existing
    cross-act gate quests plus `Chapter.isVisible()` returning false when nothing inside is
    visible.

17. **"Add a `thermal:smelter` sink for aluminum (→ bronze) and platinum (→ netherite)"
    (MAT-06).** The dead-end diagnosis is correct (no live consumer of
    `#forge:ingots/platinum`; all three aluminum consumers are Immersive-Engineering-gated),
    but the proposed recipes break the economy: the platinum one yields 2 netherite ingots
    from 4 scrap where Thermal's own `smelter_alloy_netherite.json` yields 1 from 4 — a
    2× netherite duplication path — and the aluminum one makes bronze at 400 RF/ingot
    against Thermal's 1600, bypassing tin entirely. Both also add a second competing recipe
    for an item that already has one. Aluminum's sink is the crushed-ore path in `unify.js`
    step 10 plus AE2 matter-cannon ammo; platinum's is the same plus the Geolosys ingot line.

18. **"Add a quest-id validator script" (STORY-17).** Run verbatim against the live repo it
    exits 1 with 97 false positives — every `valley:*` custom item, because `scratch/ids.json`
    is a server registry export that predates that namespace. It also duplicates
    `tools/scripts/compile_quests.py --strict` and `tools/scripts/validate_quests.py`, scans
    the compiled `.snbt` rather than the `story/quests/*.json` source of truth, and hardcodes
    three structure ids instead of checking the real registry — so it would not catch the next
    occurrence of the bug it exists to prevent. One of its three hardcoded entries
    (`minecraft:ruined_portal`) is also wrong: that *is* a registered standalone structure as
    well as a tag, and "fixing" a task to `#minecraft:ruined_portal` would silently widen it
    from one portal to seven.

---

## Apply order

1. `packwiz refresh` — nothing in `pack/` is live until this runs, and two already-authored
   fixes are currently unshipped.
2. Remove `dynamic-torches-5.3.jar` + its `.pw.toml` entry (`mod_changes.json`).
3. Apply `scratch/config_edits.json`, including the three `cp server/config/... pack/config/...`
   steps (thermal, supplementaries, voicechat) and the two mirrored `server/config/` edits
   (sparsestructures, veinmining).
4. Deploy `unify.js` + `hide.js`; confirm `server/kubejs/server_scripts/` actually receives
   them — it is a separate directory from `pack/kubejs/`, not a symlink.
5. Delete `server/config/ftbquests/quests/chapters/ztest.snbt`.
6. Add `story_team.js`, `seasons_tags.js`, and the Geolosys cinnabar lang file.
7. Boot, then run the PT-01 JEI check (Machine Frame / RF Coil / Redstone Servo / Energy Cell
   / Wrench / Satchel) before writing any Thermal parts recipes.
8. Chunky pre-gen, radius 3000, before the two of them start.
