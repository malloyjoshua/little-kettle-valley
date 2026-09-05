# Mod decisions

Log of every swap, cut, or pin, with the reason. Newest at the bottom.

| Date | Mod | Decision | Why |
|---|---|---|---|
| 2026-09-02 | Modern Industrialization, Tech Reborn | Not included | Pack moved from Fabric to Forge so Thermal Expansion could be the backbone. |
| 2026-09-02 | Geocluster | Replaced by Geolosys | Geocluster is the Fabric clone; Geolosys is the Forge original. |
| 2026-09-02 | Sodium / Lithium / Krypton | Replaced by Embeddium / Canary; Krypton dropped | Fabric-only; Forge ports used where they exist. |
| 2026-09-02 | Universal Graves | Replaced by Corpse | Fabric-only. Corpse does the same on Forge. |
| 2026-09-02 | Friends For Life | Replaced by Domestication Innovation | Fabric-only, every version. Domestication Innovation adds pet upgrades on Forge. |
| 2026-09-02 | Fancy Beds | Dropped | Not a real mod on either platform; only a resource pack by that name. Beds come from Macaw's and Handcrafted anyway. |
| 2026-09-02 | Bigger Reactors, FTB Quests, FTB Teams, FTB Library, FTB XMod Compat | Sourced from CurseForge | Not on Modrinth. packwiz pulls them with its built-in CurseForge key. |
| 2026-09-02 | Oculus / any shader mod | Not included | Visuals don't matter and the 8 GB Air needs the headroom. |
| 2026-09-02 | Phosphophyllite | Sourced from CurseForge, not the Modrinth "phos" project | Modrinth's "Phosphophyllite" is a different mod by a different author. Bigger Reactors needs BiggerSeries' library, which is CurseForge-only. |
| 2026-09-02 | Quartz | Added from CurseForge | Second required library for Bigger Reactors 0.6.0-beta.10. |
| 2026-09-02 | Duckling, ImmediatelyFast | Pinned to 3.0.0 and 1.2.4+1.20.1 | packwiz's non-interactive picker grabbed NeoForge 1.20.4 and 1.20.2 builds. Both mislabel game versions on Modrinth. |
| 2026-09-02 | EMI | Replaced by JEI | Thermal, Create, AE2, Bigger Reactors and Farmer's Delight all ship JEI plugins natively; EMI would have needed a JEI bridge to show their recipes. One recipe viewer, full coverage. |
| 2026-09-02 | Create Crafts & Additions | Added | Bridges Create rotational power and Thermal/AE2 RF with an alternator and motor. Without it the two power systems never touch. |
| 2026-09-02 | Jade Addons | Added (client) | Hover info for Create and Thermal machines, so "what is this doing" is answered on screen. |
| 2026-09-02 | Dynamic Lights (dynamic-torches) | Removed | It is a bundled datapack that runs a per-tick fill/clear loop of light blocks around every glowing entity, not a client renderer. Real TPS risk on a 3.5 GB client. Torchmaster's Feral Flare Lantern is the pack's carry-light. |
| 2026-09-03 | Just Hammers 2.0.3+mc1.20.1 (Modrinth `just-hammers` / `edU0NbZZ`, version `JafXa7hr`) | Added, pinned, `side = "both"` | The 3x3 mining tool the pack was missing. It is the mod Homestead itself ships for this role, its only dependency is Architectury API (already in the pack), it respects vanilla harvest tiers (a Stone Hammer cannot break iron/diamond-gated blocks), it drops through `Block.getDrops` so Fortune and Silk Touch behave, and it never fully breaks — it bottoms out at 1 durability and goes to an anvil. Rejected: Only Hammers / Only Hammers and Excavators (3x1 line, not a 3x3 grid), Hammer (client-only, `server_side: unsupported` — wrong shape for the headless server), HammerLib (a library, not a hammer), Thermal Innovation (whole Thermal multitool chain for one AoE augment), TFC: Hammer Time (needs TerraFirmaCraft). Upstream has moved to NeoForge-only, so 2.0.3 is the last 1.20.1-Forge build — fine for a pinned pack, just expect no bugfixes. |
| 2026-09-03 | Just Hammers recipes | Mod recipes left alone; ONE parallel copper craft added (`valley:cheap/copper_hammer`) | The shipped Stone Hammer is already 3 stone + 3 sticks and the Iron Hammer 3 iron + 3 sticks (read out of `data/justhammers/recipes/*.json` in the 2.0.3 jar), so nothing was expensive enough to need a §5 ingredient gate and nothing was removed. What was added in `valley_gates.js` is a second path to `justhammers:stone_hammer` in copper — the same 3-2-1 shape, `#forge:ingots/copper` + sticks — so the first hammer reads as something the kettle town made, in the metal every other hour-one recipe here already uses (bounty board, megatorch, waystone, bell, surveyor's stake). The upgrade ladder is untouched: its first core (`justhammers:impact_core`) eats a NETHERITE hammer plus iron and gold blocks, so 3x3x3 and larger already sit far past the end of the story on the mod's own terms. |

| 2026-09-04 | Regions Unexplored 0.5.6 + TerraBlender 3.0.1.10 | **Removed both** | The pack now ships ONE hand-built world on a famous vanilla seed, and a TerraBlender biome mod rewrites what that seed produces — every "famous" spawn description on the wiki/press lists is a vanilla-generation description, so with RU installed the seed we pick is not the seed anyone wrote about. Checked before pulling: zero references to `regions_unexplored` in `story/`, `pack/kubejs/` or `pack/config/` (the only two hits in the whole repo are prose in `docs/integration-plan.md` and `docs/integration-audit-night.md`), and a scan of every `META-INF/mods.toml` in `server/mods` found exactly one mod declaring a `terrablender` dependency — Regions Unexplored itself. So TerraBlender had no other dependent and went with it. Net effect: worldgen is stock 1.20.1, seeds behave as documented, and a chunk of biome-blend worldgen cost comes off the 8 GB Air's first load. |
| 2026-09-04 | Toast Control 8.0.3 (Modrinth `toast-control` / `CnOG2wlS`, version `q8jNIVj8`), `side = "client"` | Added, plus Placebo 8.6.3 (`tCkE8p2N` / `6SkuAGoz`) as its required library, forced to `side = "client"` | The onboarding problem this pack has is noise: a Forge pack of this size fires a wall of recipe-unlock toasts in the first ten minutes, on top of vanilla tutorial and system toasts, and the story's own beats have to compete with them. Toast Control is the only 1.20.1-Forge mod on Modrinth for the job and it is `client_side: required / server_side: unsupported`, so it never touches the headless server. Placebo is its only dependency; nothing else in the pack needs Placebo, so it is pinned to the client side too rather than the `both` packwiz copied off Modrinth — the server mod list is unchanged by this addition. |
| 2026-09-04 | Toast Control config (`pack/config/toastcontrol-client.toml`) | recipes / tutorial / system **blocked**; advancements **left visible** | Read the config spec straight out of `dev/shadowsoffire/toastcontrol/ToastConfig.class` in the 8.0.3 jar. The blockable knobs are exactly: `advancements`, `recipes`, `system`, `tutorial`, `global_vanilla`, `global_modded`, `global`, and `blocked_classes` (a list of *Java toast class names*, not registry ids). **There is no per-advancement-id filter** — the mod cannot allow `valley:` advancements while blocking vanilla ones, because it never sees the advancement id, only the toast object's class. The pack's journal beats are advancement toasts (`pack/kubejs/data/valley/advancements/journal/*.json`, all `show_toast: true`, `announce_to_chat: false`), so `advancements = true` would silence the story to mute Minecraft. Blocking recipes + tutorial + system removes the actual first-hour noise and costs nothing the story uses; the leftover vanilla advancement toasts are rare enough in this pack's play pattern to be worth the trade. If they ever need to go, the only route is a datapack overriding each vanilla advancement's `show_toast` — not a config change. |
| 2026-09-04 | Inventory Sorter (Configurable) 23.1.9 | **Removed** (`packwiz remove inventory-sorter-configurable`) | Superseded by Inventory Profiles Next (below), which draws its own on-screen Sort/Move-All buttons directly on every container and player-inventory screen — the visible button Josh asked for, which the old mod never had (it was middle-click-only, keybind-driven). Its stale `key_key.inventorysorter.sort:key.mouse.middle` line was also removed from `pack/options.txt`. Mouse Tweaks stays — it does click-drag stack transfer/splitting across slots, a different job that IPN does not touch. |
| 2026-09-04 | Inventory Profiles Next 1.10.20 (Modrinth `inventory-profiles-next` / `O7RBXm3n`, version `CrtAI3P9`) + libIPN 4.0.2 (`libipn` / `onSQdWhM`, version `pdAXmKcS`) | Added, both `side = "client"` (packwiz auto-detected this from Modrinth's `client_side: required` / `server_side: unsupported` metadata, matching how `mouse-tweaks.pw.toml` is already pinned) | Picked over Quark (not present in this pack, and pulling all of Quark for its sort buttons alone would be a large, unrelated feature surface) and over doing nothing (the old sorter had no visible button at all). IPN needs Kotlin for Forge >= 4.3 (`mods.toml`: `loaderVersion="[4.3,)"`) and libIPN `[4.0.2,5)` exactly — Kotlin for Forge 4.12.0 is already in the pack for other mods, so libIPN 4.0.2 (the only 1.20.1-Forge build on Modrinth) was the only version that could satisfy both. Compatibility checked by decompiling the 1.10.20 jar rather than guessing: `assets/inventoryprofilesnext/config/ModIntegrationHintsNG.json` ships 133 built-in per-mod container hints, including explicit entries for `sophisticatedbackpacks`, `sophisticatedstorage`, `create`, `thermal`, `waystones`, `supplementaries` and `quark` — i.e. IPN already knows how to read/sort the exact storage mods this pack ships. No entry exists for `storagedrawers` or `curios`, but neither is a generic sortable container (drawers are per-block-type slots; Curios is equipment), so that's expected, not a gap. IPN's own doc site (`inventory-profiles-next.github.io/known-issues/`) lists no reported conflicts with any of those mods either. |
| 2026-09-04 | `pack/config/inventoryprofilesnext/inventoryprofiles.json` | Wrote one override: unbind IPN's `SORT_INVENTORY` hotkey | See "IPN sort button + JEI recipe transfer" below — IPN ships with `SORT_INVENTORY` hard-coded to bare `R`, which is the same physical key (GLFW 82) JEI uses for "Show Recipes" while hovering an item in a container GUI. Everything Josh actually asked for (the visible Sort/Move-All buttons) is `true` by default in the compiled jar and needed no config at all; this file only removes the one real keybind collision. |

## IPN sort button + JEI recipe transfer (verified 2026-09-04)

**The on-screen buttons need no config.** Disassembled `org/anti_ad/mc/ipnext/config/GuiSettings.class`
from the 1.10.20 jar with the project's own bundled JDK 17 (`tools/jdk17`) and read the
static initializer's literal arguments rather than guessing: `ENABLE_INVENTORY_BUTTONS`,
`SHOW_REGULAR_SORT_BUTTON`, `SHOW_SORT_IN_COLUMNS_BUTTON`, `SHOW_SORT_IN_ROWS_BUTTON` and
`SHOW_MOVE_ALL_BUTTON` all compile to `true`. IPN draws its Sort/Move-All icons on chests,
the player inventory, and every container GUI it has a hint for, the moment the jar is
added — nothing in `pack/config/` was required to "turn the button on."

**One real keybind collision, found the same way.** `org/anti_ad/mc/ipnext/config/Hotkeys.class`'s
static initializer was walked instruction-by-instruction (`javap -c -p -constants`) to
recover every default hotkey string next to its `KeybindSettings` context:

| IPN hotkey | Default | Context |
|---|---|---|
| `SORT_INVENTORY` | **`R`** | GUI (only while a container screen is open) |
| `OPEN_CONFIG_MENU` | `R,C` (sequence) | in-game |
| `RELOAD_CUSTOM_CONFIGS` | `R,Y` (sequence) | any |
| `MOVE_ALL_ITEMS` | `R,T` (sequence) | GUI |
| `THROW_ALL_ITEMS` | `R,M` (sequence) | GUI |
| `SORT_INVENTORY_IN_COLUMNS` / `_IN_ROWS` | *(unbound)* | GUI |

JEI's own jar (`server/mods/jei-1.20.1-forge-15.56.0.205.jar`, class
`mezz/jei/gui/config/InternalKeyMappings`) was decompiled the same way: `showRecipe` is
hard-coded to `buildKeyboardKey(82)` (GLFW 82 = `R`) and `showUses` to `buildKeyboardKey(85)`
(GLFW 85 = `U`), both scoped to `JeiKeyConflictContext.JEI_GUI_HOVER` — i.e. "while hovering
an item in any open container/inventory GUI," which is the exact same trigger IPN's bare-`R`
`SORT_INVENTORY` uses. That is a genuine, same-key, same-context collision, and it is exactly
the case the brief said to avoid. The `R,C` / `R,Y` / `R,T` / `R,M` *sequences* are lower risk
(they need a specific second key within IPN's chord window, not a bare tap) and were left
alone — `OPEN_CONFIG_MENU` and `MOVE_ALL_ITEMS` also both have on-screen buttons already
(`ENABLE_INVENTORY_EDITOR_BUTTON` / `SHOW_MOVE_ALL_BUTTON`, both default `true`), so the
keyboard shortcut is a convenience, not the only way in.

**The fix.** `pack/config/inventoryprofilesnext/inventoryprofiles.json` sets
`sort_inventory.main.keys` to an empty string, unbinding it — matching how
`SORT_INVENTORY_IN_COLUMNS`/`_IN_ROWS` already ship unbound by default, rather than
picking a new letter that might turn out to collide with something else in a 130-mod
pack. Sorting stays available via the always-on-screen button either way. The exact
on-disk schema (`{"<lowercased_property_name>": {"main": {"keys": "..."}}}`) was reverse
engineered from `ConfigSaveLoadManager`, `CategorizedMultiConfig`,
`IKeybind$DefaultImpls` and `ConfigOptionDelegateProvider$1` in `libIPN-forge-1.20-4.0.2.jar`
(the property name is lower-cased via `Locale.ROOT` before being used as the JSON key, and
`ConfigSaveLoadManager.load()` wraps parsing in try/catch for `IOException` /
`SerializationException` / generic `Exception` and only logs — it never crashes — so a
schema mistake here fails safe back to the (colliding) default, not to a broken client).
**This was not launch-tested** (the brief asked for the server/client to stay untouched);
if the override doesn't take, the same fix is 10 seconds in-game: open IPN's settings
(gear icon on the player inventory screen, or the `R,C` chord) and clear the Sort
Inventory hotkey.

**JEI recipe transfer was not touched and did not need to be.** No `pack/config/jei/`
or `jei-client.toml` exists anywhere in the repo (JEI generates it from compiled
defaults on first client launch, and nothing in this pack pre-seeds one), and
`mezz/jei/common/config/IClientConfig` in the 15.56.0.205 jar has no
"disable recipe transfer" toggle at all — transfer is wired into the recipe-category
system itself (`RecipeTransferManager`, `RecipeTransferButton`), not a config flag, so
it cannot have been switched off by a stray config. With a crafting table (or another
compatible station) open and a recipe pulled up in the JEI recipes GUI, the **+** button
moves what it can from the player's inventory into the grid; **shift-click on +** crafts
and pulls enough for a full stack in one go. Cheat Mode is a runtime toggle
(`key.jei.toggleCheatMode`, unbound by default in this pack, off until explicitly
turned on) — confirmed off, not a modpack config setting to flip.

## Just Hammers vs Vein Mining (verified 2026-09-03, both stay usable)

Both mods hook block-breaking, and the Just Hammers README lists "Vein miner like
mods can be used in conjunction with the hammers" as an open issue, so the two were
read against each other in the actual 1.20.1 jars before the mod was kept:

- **They fire off different events.** Vein Mining listens to Forge's
  `BlockEvent$BreakEvent` (`ForgeCommonEventsListener.blockBreak`). Just Hammers
  breaks its extra blocks with `Level.destroyBlock(pos, false, entity)` and announces
  them on Architectury's `BlockEvent.BREAK`, which on Forge is a one-way bridge
  (`EventHandlerImplCommon` only converts Forge -> Architectury, never back). So the
  hammer's other 8 blocks never re-enter Vein Mining: no cascade, no dupe.
- **Vein Mining is re-entrancy-latched anyway.** `VeinMiningEvents.blockBreak` returns
  early when `VeinMiningPlayers.isVeinMining(player)` is already true.
- **They do not collide on the source block either.** Vein Mining only runs while its
  activation key is held (bound to the grave accent in `pack/options.txt`) *and* the
  tool carries the Vein Mining enchantment; the hammer's own AoE is disabled while
  sneaking (`causeAoe` returns on `LivingEntity.isCrouching()`). When both do run on the
  same swing they work on disjoint blocks — the vein-mined ore is already air, and the
  hammer's `canDestroy` skips anything with destroy speed 0.
- **The enchantment applies to hammers.** `veinmining-common.toml` allows `is:tool`,
  which `ForgePlatform.buildEnchantableItems()` resolves to a Forge `ToolActions`
  predicate. `HammerItem extends PickaxeItem` and does not override `canPerformAction`,
  so every hammer is enchantable and one tool can do both jobs.
- **Blocks with a block entity are never smashed** — `canDestroy` bails on
  `Level.getBlockEntity(pos) != null` — and the mod ships a `justhammers:hammer_no_smashy`
  block tag if anything in the valley ever needs explicit protection.
- **No keybinds added.** The jar registers no `KeyMapping` (its only client event is
  `RenderLevelStageEvent`, and its lang file has no `key.*` entries), so
  `pack/options.txt` is untouched and nothing collides with the existing Vein Mining,
  FTB Quests, backpack, Carry, sorter or push-to-talk bindings.

---

## 2026-09-05 — KubeJS script load order is not alphabetical, and the pack was relying on it

Not a mod swap, but it belongs in this log because it is a fact about a dependency the pack
had assumed rather than checked.

`valley_core.js` builds `VALLEY.OFF` — every mark the finales and scenes measure from — like
this:

```js
OFF: (typeof global.valleyTownPlan !== 'undefined' && global.valleyTownPlan.OFF)
  ? global.valleyTownPlan.OFF
  : { square: [0,1,0], ... works: [34,-6,-20], ... }      // hand-typed fallback
```

with a comment above it saying town_plan.js is loaded first because "'t' sorts before 'v'".
It is not. Measured, from `server/logs/latest.log` on 2026-09-05:

```
00:15:02.929  valley_core.js#1213: [valley] valley_core.js ok
00:15:02.953  town_plan.js#9974:  [valley] town_plan.js ok -- 30 build groups
```

So `global.valleyTownPlan` was undefined at the moment `OFF` was evaluated, and **every mark
in the pack was coming from the hand-typed fallback**, not from the generated plan. It went
unnoticed for as long as the two happened to agree. They stopped agreeing the moment the
terracing pass moved the Works down nine blocks to keep it buried: `act4_works` then built a
15 x 6 x 15 stone-brick room at the fallback's depth, which put its ceiling one block under
the meadow and its floor through the pad of Pip's house.

**Decision:** `plan_town.py` now emits `// priority: 1000` as the first line of the generated
`town_plan.js`. KubeJS reads that header and loads the file before anything without one, so
the plan is in `global` before `valley_core.js` asks for it. The fallback stays where it is —
it is a sensible thing to have — but nothing normal should ever reach it again.

Worth knowing for anything else added to `pack/kubejs/server_scripts/`: if a script reads a
global another script sets, say so with a priority. Filenames are not a contract.
