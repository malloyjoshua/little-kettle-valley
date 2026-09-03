// =============================================================================
// unify.js - Cozy Tech Pack materials unification
// KubeJS 2001.6.5 / Forge 1.20.1 / Minecraft 1.20.1
// =============================================================================
// GOAL: one item per material, one furnace path per ore, no dead-end drops.
//
// CANONICAL PICKS (evidence: live tag dump at
//   server/local/kubejs/export/tags/minecraft/item/forge/*):
//   tin / silver / lead / nickel / electrum / netherite nugget -> Thermal
//   zinc, copper nugget                                        -> Create
//   aluminum / platinum / uranium / coal tiers                 -> Geolosys (sole provider)
//
// SAFETY RULE THIS FILE FOLLOWS (learned the hard way, see docs/integration-plan.md
// "Refuted ideas" #1): a blanket `event.remove({ output: X })` also deletes
// non-vanilla machine recipes that happen to emit X - it wiped Create's Mixer
// electrum recipe (create:mixing, createaddition:recipes/mixing/electrum.json).
// Every removal below is therefore either an explicit recipe id, or an
// output-filter SCOPED TO A VANILLA RECIPE TYPE. Machine recipes are never
// removed by accident.
//
// SECOND RULE: never hide an item in JEI whose producer we did not actually
// remove. A machine that spits out an item JEI refuses to explain is worse
// than a duplicate. See pack/kubejs/client_scripts/hide.js - it only hides the
// HARD_RETIRE set below.
// =============================================================================

// -----------------------------------------------------------------------------
// 1. HARD_RETIRE - duplicates whose ONLY producers are vanilla-type recipes
//    (crafting / smelting / blasting). These can be removed cleanly, replaced
//    everywhere, and hidden from JEI without orphaning a machine.
//    Geolosys ships only smelting/, blasting/ and crafting/ folders - verified.
// -----------------------------------------------------------------------------
const HARD_RETIRE = {
  // Geolosys duplicates of Thermal metals
  'geolosys:tin_ingot': 'thermal:tin_ingot',
  'geolosys:tin_nugget': 'thermal:tin_nugget',
  'geolosys:silver_ingot': 'thermal:silver_ingot',
  'geolosys:silver_nugget': 'thermal:silver_nugget',
  'geolosys:lead_ingot': 'thermal:lead_ingot',
  'geolosys:lead_nugget': 'thermal:lead_nugget',
  'geolosys:nickel_ingot': 'thermal:nickel_ingot',
  'geolosys:nickel_nugget': 'thermal:nickel_nugget',
  // Geolosys duplicates of Create zinc
  'geolosys:zinc_ingot': 'create:zinc_ingot',
  'geolosys:zinc_nugget': 'create:zinc_nugget',
  // Geolosys duplicate of Create copper nugget
  'geolosys:copper_nugget': 'create:copper_nugget'
}

// -----------------------------------------------------------------------------
// 2. SOFT_UNIFY - duplicates that a MACHINE still produces.
//    createaddition:electrum_ingot comes out of Create's Mixer
//    (createaddition:recipes/mixing/electrum.json, type create:mixing) and
//    electrum_nugget is a Crushing Wheel byproduct on tuff/ochrum.
//    We do NOT delete those recipes and we do NOT hide these items.
//    Instead: keep them in the forge tags (so every tag-driven Thermal/Create
//    recipe treats them as the same metal - this is the unification that
//    actually matters), attempt a replaceOutput retarget, and give the player a
//    1:1 bench conversion so a chest full of them tidies into the canonical item.
// -----------------------------------------------------------------------------
const SOFT_UNIFY = {
  'createaddition:electrum_ingot': 'thermal:electrum_ingot',
  'createaddition:electrum_nugget': 'thermal:electrum_nugget',
  'createaddition:electrum_block': 'thermal:electrum_block',
  // createdeco:netherite_nugget is the ONLY legal input to Create Deco's
  // Netherite Coin press (createdeco:recipes/pressing/coins/netherite_coin.json,
  // type create:pressing, matched by item id). Deleting its producer bricks the
  // coin. Keep it craftable; just tag it so the Thermal Press accepts it too.
  'createdeco:netherite_nugget': 'thermal:netherite_nugget'
}

// -----------------------------------------------------------------------------
// 3. Geolosys ore-cluster -> canonical ingot, vanilla furnace + blast furnace.
//    Thermal only smelts `thermal:raw_*` by literal item id, so without these
//    the clusters have no furnace path once Geolosys' own recipes are removed.
//    (zinc_cluster is intentionally absent: create:zinc_ingot_from_raw_ore
//     already smelts #forge:raw_materials/zinc, which contains it.)
// -----------------------------------------------------------------------------
const CLUSTER_SMELT = {
  'geolosys:tin_cluster': 'thermal:tin_ingot',
  'geolosys:silver_cluster': 'thermal:silver_ingot',
  'geolosys:lead_cluster': 'thermal:lead_ingot',
  'geolosys:nickel_cluster': 'thermal:nickel_ingot'
}

// Vanilla recipe types only. Scoping removals to these is what keeps
// create:mixing / create:crushing / create:pressing / thermal:* alive.
const VANILLA_TYPES = [
  'minecraft:crafting_shaped',
  'minecraft:crafting_shapeless',
  'minecraft:smelting',
  'minecraft:blasting'
]

ServerEvents.recipes(event => {

  // ===========================================================================
  // 4. Remove the vanilla-type producers of every HARD_RETIRE item.
  // ===========================================================================
  Object.keys(HARD_RETIRE).forEach(retired => {
    VANILLA_TYPES.forEach(type => {
      event.remove({ output: retired, type: type })
    })
  })

  // 4b. Named removals that survive step 4 because their OUTPUT is a vanilla
  //     item, but which become exact duplicates after unification.
  //     - Geolosys' copper 3x3 takes the literal geolosys nugget; Create already
  //       ships an all-tag 3x3 (create:crafting/materials/copper_ingot).
  //     - Create Deco's netherite 9-nugget craft is replaced by the tag version
  //       in step 8, which accepts BOTH nuggets.
  event.remove({ id: 'geolosys:crafting/nuggets/copper_nugget_to_copper_ingot' })
  event.remove({ id: 'createdeco:netherite_ingot' })

  // 4c. Supplementaries flax is disabled in config (see config_edits.json,
  //     MAT-07) so this Create milling recipe would try to resolve a
  //     deregistered ingredient every reload. Remove it explicitly.
  event.remove({ id: 'create:milling/compat/supplementaries/flax' })

  // ===========================================================================
  // 5. Retarget. Anything still EMITTING a retired item emits the canonical one.
  //    On vanilla-type recipes this is guaranteed. On Create's custom types it
  //    is best-effort: if it does not take, the SOFT_UNIFY items simply remain
  //    craftable and tag-identical, which is why they are not JEI-hidden.
  // ===========================================================================
  Object.keys(HARD_RETIRE).forEach(r => event.replaceOutput({}, r, HARD_RETIRE[r]))
  Object.keys(SOFT_UNIFY).forEach(r => event.replaceOutput({}, r, SOFT_UNIFY[r]))

  // ===========================================================================
  // 6. Anything CONSUMING a retired item by literal id now takes the canonical
  //    one. HARD_RETIRE only - SOFT_UNIFY inputs are deliberately left alone so
  //    the Netherite Coin press keeps its ingredient.
  // ===========================================================================
  Object.keys(HARD_RETIRE).forEach(r => event.replaceInput({}, r, HARD_RETIRE[r]))

  // ===========================================================================
  // 7. Furnace / blast path for Geolosys clusters.
  //    xp + cook time copied from Geolosys' own cluster recipes (0.7 / 200 / 100).
  // ===========================================================================
  Object.keys(CLUSTER_SMELT).forEach(cluster => {
    const ingot = CLUSTER_SMELT[cluster]
    const name = cluster.split(':')[1]
    event.smelting(ingot, cluster).xp(0.7).cookingTime(200).id('cozytech:smelting/' + name)
    event.blasting(ingot, cluster).xp(0.7).cookingTime(100).id('cozytech:blasting/' + name)
  })

  // ===========================================================================
  // 8. Netherite nugget loop on the bench, tag-driven so BOTH nuggets work.
  //    Create Deco's own 9->1 was removed in 4b; Thermal only offers the Press.
  // ===========================================================================
  event.shapeless('9x thermal:netherite_nugget', ['minecraft:netherite_ingot'])
    .id('cozytech:netherite_nugget_from_ingot')
  event.shaped('minecraft:netherite_ingot', ['NNN', 'NNN', 'NNN'], {
    N: '#forge:nuggets/netherite'
  }).id('cozytech:netherite_ingot_from_nuggets')

  // ===========================================================================
  // 9. DEAD-END DROPS - Geolosys clusters no loaded mod can process.
  //
  //    osmium_cluster: Mekanism is not in this pack. Geolosys' platinum ore is
  //      filed into forge:ores/osmium as well as forge:ores/platinum (its own
  //      tag files, unconditional), so osmium clusters really do drop. Route
  //      them to platinum - same metal, one destination.
  //    uranium_cluster: Bigger Reactors smelts only its own uranium_chunk by
  //      literal id (biggerreactors:recipes/smelting/uranium_chunk.json).
  //      xp/time copied from that recipe so the two paths match exactly.
  // ===========================================================================
  event.smelting('geolosys:platinum_ingot', 'geolosys:osmium_cluster')
    .xp(0.7).cookingTime(200).id('cozytech:smelting/osmium_cluster')
  event.blasting('geolosys:platinum_ingot', 'geolosys:osmium_cluster')
    .xp(0.7).cookingTime(100).id('cozytech:blasting/osmium_cluster')

  event.smelting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster')
    .xp(0.35).cookingTime(200).id('cozytech:smelting/uranium_cluster')
  event.blasting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster')
    .xp(0.35).cookingTime(100).id('cozytech:blasting/uranium_cluster')

  // ===========================================================================
  // 10. CRUSHING WHEEL SAFETY NET.
  //     Create's crushed_raw_* items for platinum / uranium / aluminum / osmium
  //     have NO active consumer in this pack - every smelting recipe for them is
  //     gated on forge:mod_loaded mekanism / immersiveengineering / ic2, none of
  //     which are installed. The PRODUCING crushing recipes are live because
  //     Geolosys and Bigger Reactors fill the gating tags. Net effect without
  //     this block: crushing wheels silently destroy every platinum cluster,
  //     every uranium chunk and every aluminum cluster.
  //     Give all four a furnace path to the same ingot the un-crushed cluster
  //     reaches, so crushing is uniformly a doubling step, never a shredder.
  // ===========================================================================
  const CRUSHED = {
    'create:crushed_raw_platinum': 'geolosys:platinum_ingot',
    'create:crushed_raw_osmium': 'geolosys:platinum_ingot', // no osmium ingot exists in this pack
    'create:crushed_raw_aluminum': 'geolosys:aluminum_ingot',
    'create:crushed_raw_uranium': 'biggerreactors:uranium_ingot'
  }
  Object.keys(CRUSHED).forEach(crushed => {
    const ingot = CRUSHED[crushed]
    const name = crushed.split(':')[1]
    event.smelting(ingot, crushed).xp(0.1).cookingTime(200).id('cozytech:smelting/' + name)
    event.blasting(ingot, crushed).xp(0.1).cookingTime(100).id('cozytech:blasting/' + name)
  })

  // ===========================================================================
  // 11. Geolosys coal tiers -> Thermal Pyrolyzer.
  //     bituminous_coal_coke and lignite_coal_coke are producible ONLY by
  //     Geolosys' Immersive Engineering compat recipes, and IE is not installed,
  //     so both are unobtainable. Thermal's own pyrolyzer_coal.json takes the
  //     literal item minecraft:coal, and Geolosys' coals are only in the
  //     minecraft:coals tag - so they have no Thermal path either.
  //     JSON shape copied verbatim from thermal's pyrolyzer_coal.json.
  // ===========================================================================
  event.custom({
    type: 'thermal:pyrolyzer',
    ingredient: { item: 'geolosys:lignite_coal' },
    result: [
      { item: 'geolosys:lignite_coal_coke' },
      { fluid: 'thermal:creosote', amount: 150 }
    ],
    experience: 0.1
  }).id('cozytech:pyrolyzer/lignite')

  event.custom({
    type: 'thermal:pyrolyzer',
    ingredient: { item: 'geolosys:bituminous_coal' },
    result: [
      { item: 'geolosys:bituminous_coal_coke' },
      { item: 'thermal:tar', chance: 0.35 },
      { fluid: 'thermal:creosote', amount: 250 }
    ],
    experience: 0.15
  }).id('cozytech:pyrolyzer/bituminous')

  event.custom({
    type: 'thermal:pyrolyzer',
    ingredient: { item: 'geolosys:anthracite_coal' },
    result: [
      { item: 'thermal:coal_coke', count: 2 },
      { item: 'thermal:tar', chance: 0.5 },
      { fluid: 'thermal:creosote', amount: 350 }
    ],
    experience: 0.2
  }).id('cozytech:pyrolyzer/anthracite')

  // ===========================================================================
  // 12. Legacy 1:1 bench conversions so nothing already in a chest is stranded.
  //     Retired items keep their forge tags (see the tag event below), so they
  //     already work in every tag-driven machine recipe - this is purely for
  //     tidying inventories into the canonical item.
  // ===========================================================================
  const legacy = id => 'cozytech:legacy/' + id.replace(':', '_')
  Object.keys(HARD_RETIRE).forEach(r => {
    event.shapeless(HARD_RETIRE[r], [r]).id(legacy(r))
  })
  Object.keys(SOFT_UNIFY).forEach(r => {
    event.shapeless(SOFT_UNIFY[r], [r]).id(legacy(r))
  })
})

// =============================================================================
// 13. TAG WORK - this is where unification is actually enforced.
//     Every Thermal / Create machine recipe consumes forge tags, not item ids,
//     so a correct tag means a Geolosys cluster works in an Induction Smelter
//     with zero recipe edits. These adds are defensive: they guarantee that a
//     leftover retired item can never be rejected by a machine.
// =============================================================================
ServerEvents.tags('item', event => {

  // Create Deco's netherite nugget sits outside #forge:nuggets/netherite (live
  // tag dump: that tag holds only thermal:netherite_nugget), which means the
  // Thermal Press and recipe 8 cannot see it. Add it.
  event.add('forge:nuggets/netherite', 'createdeco:netherite_nugget')

  // Retired items stay tagged as their material.
  event.add('forge:ingots/tin', 'geolosys:tin_ingot')
  event.add('forge:nuggets/tin', 'geolosys:tin_nugget')
  event.add('forge:ingots/silver', 'geolosys:silver_ingot')
  event.add('forge:nuggets/silver', 'geolosys:silver_nugget')
  event.add('forge:ingots/lead', 'geolosys:lead_ingot')
  event.add('forge:nuggets/lead', 'geolosys:lead_nugget')
  event.add('forge:ingots/nickel', 'geolosys:nickel_ingot')
  event.add('forge:nuggets/nickel', 'geolosys:nickel_nugget')
  event.add('forge:ingots/zinc', 'geolosys:zinc_ingot')
  event.add('forge:nuggets/zinc', 'geolosys:zinc_nugget')
  event.add('forge:nuggets/copper', 'geolosys:copper_nugget')
  event.add('forge:ingots/electrum', 'createaddition:electrum_ingot')
  event.add('forge:nuggets/electrum', 'createaddition:electrum_nugget')
  event.add('forge:storage_blocks/electrum', 'createaddition:electrum_block')

  // Platinum ore is filed into forge:ores/osmium AND forge:ores/platinum by
  // Geolosys itself, which makes Create load TWO crushing recipes for the same
  // block. Drop the osmium membership so only the platinum recipe applies.
  // (Step 10 still gives crushed_raw_osmium a furnace path, in case tag removal
  //  lands after Create's forge:tag_empty condition is evaluated.)
  event.remove('forge:ores/osmium', 'geolosys:platinum_ore')
  event.remove('forge:ores/osmium', 'geolosys:deepslate_platinum_ore')
})

ServerEvents.tags('block', event => {
  // Same osmium de-aliasing on the block side, so mining/vein-mining tools and
  // JEI both stop treating platinum ore as an osmium source.
  event.remove('forge:ores/osmium', 'geolosys:platinum_ore')
  event.remove('forge:ores/osmium', 'geolosys:deepslate_platinum_ore')
})
