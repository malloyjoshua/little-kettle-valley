// unify.js — Cozy Tech Pack material unification (KubeJS 2001.6.5 / Forge 1.20.1)
// One ingot per metal. Canonical picks:
//   tin / silver / lead / nickel / electrum / netherite nugget -> Thermal
//   zinc                                                        -> Create
//   copper nugget                                               -> Create
//   aluminum / platinum / coal variants                         -> Geolosys (sole provider)
// Evidence for every line is in the audit; nothing here touches worldgen.

// ---------------------------------------------------------------------------
// 1. Canonical map: retired item -> canonical replacement
// ---------------------------------------------------------------------------
const UNIFY = {
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
  'geolosys:copper_nugget': 'create:copper_nugget',
  // Create Crafts & Additions duplicates of Thermal electrum
  'createaddition:electrum_ingot': 'thermal:electrum_ingot',
  'createaddition:electrum_nugget': 'thermal:electrum_nugget',
  'createaddition:electrum_block': 'thermal:electrum_block',
  // Create Deco duplicate of Thermal netherite nugget
  'createdeco:netherite_nugget': 'thermal:netherite_nugget'
}

// Geolosys ore-cluster -> canonical ingot for the vanilla furnace / blast furnace.
// (Thermal only smelts `thermal:raw_*` by item id, so without these the clusters
//  have no furnace path once Geolosys' own recipes are removed.)
const CLUSTER_SMELT = {
  'geolosys:tin_cluster': 'thermal:tin_ingot',
  'geolosys:silver_cluster': 'thermal:silver_ingot',
  'geolosys:lead_cluster': 'thermal:lead_ingot',
  'geolosys:nickel_cluster': 'thermal:nickel_ingot'
  // zinc_cluster intentionally omitted: create:zinc_ingot_from_raw_ore already
  // smelts #forge:raw_materials/zinc, which contains geolosys:zinc_cluster.
}

ServerEvents.recipes(event => {

  // -------------------------------------------------------------------------
  // 2. Delete every recipe that PRODUCES a retired item.
  //    Verified producers (audit): 3 per Geolosys ingot, 1 per Geolosys nugget,
  //    4 Create Crafts & Additions electrum crafting recipes, 2 Create Deco.
  // -------------------------------------------------------------------------
  Object.keys(UNIFY).forEach(retired => {
    event.remove({ output: retired })
  })

  // 2b. Explicit removals of recipes that survive step 2 (their output is a
  //     vanilla item) but would become exact duplicates after unification.
  //     - geolosys copper 3x3: Create already ships an all-tag 3x3
  //       (create:crafting/materials/copper_ingot) with the same result.
  //     - createdeco:netherite_ingot: replaced by cozytech's tag version below.
  event.remove({ id: 'geolosys:crafting/nuggets/copper_nugget_to_copper_ingot' })
  event.remove({ id: 'createdeco:netherite_ingot' })

  // -------------------------------------------------------------------------
  // 3. Anything that still emits a retired item now emits the canonical one.
  //    This is what keeps Create's Crushing Wheels (tuff / ochrum -> electrum
  //    nugget) and the Mixer alloy (gold + silver -> electrum) on the Thermal
  //    item, so Create and Thermal share one electrum.
  // -------------------------------------------------------------------------
  Object.keys(UNIFY).forEach(retired => {
    event.replaceOutput({}, retired, UNIFY[retired])
  })

  // -------------------------------------------------------------------------
  // 4. Anything that CONSUMES a retired item by explicit id now takes the
  //    canonical one. Known case: Create Deco's Netherite Coin pressing.
  // -------------------------------------------------------------------------
  Object.keys(UNIFY).forEach(retired => {
    event.replaceInput({}, retired, UNIFY[retired])
  })

  // -------------------------------------------------------------------------
  // 5. Re-add the furnace / blast-furnace path for Geolosys clusters.
  //    Same xp + cook time Geolosys used (0.7 xp, 200/100 ticks).
  // -------------------------------------------------------------------------
  Object.keys(CLUSTER_SMELT).forEach(cluster => {
    const ingot = CLUSTER_SMELT[cluster]
    const name = cluster.split(':')[1]
    event.smelting(ingot, cluster).xp(0.7).cookingTime(200).id('cozytech:smelting/' + name)
    event.blasting(ingot, cluster).xp(0.7).cookingTime(100).id('cozytech:blasting/' + name)
  })

  // -------------------------------------------------------------------------
  // 6. Dead-end Geolosys drops that no loaded mod can process.
  //    - osmium_cluster: Mekanism absent, nothing smelts it (see config finding)
  //    - uranium_cluster: Bigger Reactors only smelts its own uranium_chunk
  // -------------------------------------------------------------------------
  event.smelting('geolosys:platinum_ingot', 'geolosys:osmium_cluster')
    .xp(0.7).cookingTime(200).id('cozytech:smelting/osmium_cluster')
  event.blasting('geolosys:platinum_ingot', 'geolosys:osmium_cluster')
    .xp(0.7).cookingTime(100).id('cozytech:blasting/osmium_cluster')

  event.smelting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster')
    .xp(0.35).cookingTime(200).id('cozytech:smelting/uranium_cluster')
  event.blasting('biggerreactors:uranium_ingot', 'geolosys:uranium_cluster')
    .xp(0.35).cookingTime(100).id('cozytech:blasting/uranium_cluster')

  // -------------------------------------------------------------------------
  // 7. Netherite nugget loop in the crafting table.
  //    Create Deco's 9<->1 pair is gone (step 2); Thermal only offers the
  //    Press. Give the cozy player a bench recipe on the canonical nugget.
  // -------------------------------------------------------------------------
  event.shapeless('9x thermal:netherite_nugget', ['minecraft:netherite_ingot'])
    .id('cozytech:netherite_nugget_from_ingot')
  event.shaped('minecraft:netherite_ingot', ['NNN', 'NNN', 'NNN'], {
    N: '#forge:nuggets/netherite'
  }).id('cozytech:netherite_ingot_from_nuggets')

  // -------------------------------------------------------------------------
  // 8. Legacy conversion: any retired item already in a chest converts 1:1.
  //    Retired items stay in their forge tags, so they keep working in every
  //    tag-driven Thermal / Create machine recipe either way — this is just so
  //    a player can tidy their inventory into the canonical item.
  // -------------------------------------------------------------------------
  Object.keys(UNIFY).forEach(retired => {
    event.shapeless(UNIFY[retired], [retired])
      .id('cozytech:legacy/' + retired.replace(':', '_'))
  })
})

ServerEvents.tags('item', event => {
  // Leftover Create Deco netherite nuggets are outside #forge:nuggets/netherite
  // (live tag dump: that tag holds only thermal:netherite_nugget), which means
  // they cannot be packed by the Thermal Press or by recipe 7. Add them.
  event.add('forge:nuggets/netherite', 'createdeco:netherite_nugget')

  // Belt-and-braces: every retired item stays tagged as its material so no
  // machine recipe can ever reject a leftover stack.
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
})
