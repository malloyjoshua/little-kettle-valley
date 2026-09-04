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
