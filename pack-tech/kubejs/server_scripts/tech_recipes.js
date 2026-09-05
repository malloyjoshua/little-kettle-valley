// =============================================================================
// tech_recipes.js — Kettle Tech: the anti-grind recipe edits, and nothing else.
//
// This file is the no-story descendant of the story pack's valley_gates.js
// (Little Kettle Valley, pack/kubejs/server_scripts/valley_gates.js). That file
// did two jobs at once:
//
//   1. SEVEN INGREDIENT GATES. Each one removed a mod's own recipe and replaced
//      it with a version that ate a quest-granted valley: item — Seasoned Oak
//      Board for the Water Wheel, Washed Silica for the Thermal Machine Frame,
//      the Works Power Tap for Cooking for Blockheads, Spring Water for the AE2
//      Charger, Josie's Turbine Notes for Bigger Reactors, the Works Deed for
//      the QuarryPlus Quarry, and a Cyanite Ingot for the greenhouse glass.
//
//   2. ANTI-GRIND. A handful of recipes that made an early-game thing cheaper,
//      or gave something a source it did not otherwise have.
//
// Kettle Tech keeps (2) and drops (1) entirely. There is no quest that hands
// out a valley: item here — there are no valley: items at all — so every gate
// would have been a hard wall with nothing behind it. Dropping a gate means
// dropping its `event.remove` too, which restores the mod's own recipe exactly
// as the mod ships it: Water Wheel, Machine Frame, Fridge/Sink/Milk Jar,
// Charger, Growth Accelerator, Reactor Casing/Terminal, Quarry and Vibrant
// Quartz Glass are all stock. Nothing here is harder than vanilla+mods.
//
// Also dropped with the gates: the greenhouse-glass TAG narrowing that used to
// live at the bottom of valley_gates.js. Serene Seasons ships
// #sereneseasons:greenhouse_glass containing #forge:glass, i.e. every glass
// block already works as a greenhouse roof. The story pack narrowed that tag to
// one reactor-gated glass. Here the tag is left at its permissive default, so
// any glass roof grows out-of-season crops from day one.
//
// Recipe ids are namespaced `kubejs:kettletech/...` — the kubejs namespace is
// always loaded, so no recipe id depends on a mod namespace this pack does not
// register (the story pack could use `valley:` because valley_items.js
// registered it; nothing registers a namespace here).
//
// Rhino: no `const` inside a function body in this pack.
// =============================================================================

ServerEvents.recipes(event => {

  // ---------------------------------------------------------------------------
  // CHEAPER — the bounty board. Vanilla Bountiful wants a DIAMOND, which is a
  // mining trip before the board that is supposed to give you something to do.
  // Copper instead: it is the first metal you smelt anyway.
  // (from valley_gates.js `valley:cheap/bountyboard`)
  // ---------------------------------------------------------------------------
  event.remove({ output: 'bountiful:bountyboard' })
  event.shaped('bountiful:bountyboard', [
    'PLP',
    'ACA',
    'PLP'
  ], {
    P: 'minecraft:oak_planks',
    L: 'minecraft:oak_log',
    A: 'minecraft:paper',
    C: 'minecraft:copper_ingot'
  }).id('kubejs:kettletech/cheap/bountyboard')

  // ---------------------------------------------------------------------------
  // CHEAPER — the Megatorch. Torchmaster ships it at 2 diamonds + 2 GOLD BLOCKS,
  // which lands somewhere in hour six; the thing it does (stop mobs spawning in
  // your base) is worth having in hour one. Copper ingot + copper block.
  // (from valley_gates.js `valley:cheap/megatorch`)
  // ---------------------------------------------------------------------------
  event.remove({ output: 'torchmaster:megatorch' })
  event.shaped('torchmaster:megatorch', [
    'TTT',
    'CLC',
    'GLG'
  ], {
    T: 'minecraft:torch',
    C: 'minecraft:copper_ingot',
    L: '#minecraft:logs',
    G: 'minecraft:copper_block'
  }).id('kubejs:kettletech/cheap/megatorch')

  // ---------------------------------------------------------------------------
  // CHEAPER — the Waystone. ADD ONLY: Waystones' own recipe is NOT removed, so
  // both paths show in JEI and the mod's is untouched. In the story pack this
  // cheap one existed because waystones were gifted by quests and JEI needed
  // something to point at. Here it is the point: a copper-tier waystone means
  // the second base does not cost a diamond trip.
  // (from valley_gates.js `valley:cheap/waystone`)
  // ---------------------------------------------------------------------------
  event.shaped('waystones:waystone', [
    'SSS',
    'SCS',
    'SSS'
  ], {
    S: 'minecraft:stone_bricks',
    C: 'minecraft:copper_ingot'
  }).id('kubejs:kettletech/cheap/waystone')

  // ---------------------------------------------------------------------------
  // CHEAPER — the first 3x3 hammer. ADD ONLY: Just Hammers' own Stone Hammer
  // (3 stone + 3 sticks) is untouched; this is a second, parallel path in
  // copper. The upgrade ladder above it is left exactly as the mod ships it —
  // justhammers:impact_core still wants a netherite hammer, so nothing past the
  // stone tier is made cheaper here.
  // (from valley_gates.js `valley:cheap/copper_hammer`)
  // ---------------------------------------------------------------------------
  event.shaped('justhammers:stone_hammer', [
    'CSC',
    ' SC',
    ' S '
  ], {
    C: '#forge:ingots/copper',
    S: 'minecraft:stick'
  }).id('kubejs:kettletech/cheap/copper_hammer')

  // ---------------------------------------------------------------------------
  // ADDS A SOURCE — the Bell. Vanilla ships NO recipe for minecraft:bell at
  // all; the only source is a village that already generated one. There is
  // nothing to remove, so this is purely additive: copper, which is what a bell
  // is actually made of.
  // (from valley_gates.js `valley:craft/bell`)
  // ---------------------------------------------------------------------------
  event.shaped('minecraft:bell', [
    ' C ',
    'CBC',
    ' C '
  ], {
    C: 'minecraft:copper_ingot',
    B: 'minecraft:copper_block'
  }).id('kubejs:kettletech/craft/bell')

  // ---------------------------------------------------------------------------
  // NOT CARRIED OVER, and why — so nobody has to diff this against
  // valley_gates.js to find out what happened to each one.
  //
  //  * create:splashing lake sand -> washed silica. There is no silica item in
  //    this pack outside valley:washed_silica (checked against the live
  //    registry export, scratch/ids_plus.json: "silica" matches valley only),
  //    so a sand -> silica splashing recipe has nothing to output. Dropped, not
  //    rewritten.
  //  * The 8 lake sand + bucket -> 4 washed silica batch craft. Same reason:
  //    both the input and the output were story items, and the only consumer
  //    was the Machine Frame gate, which is gone.
  //  * valley:winter_tonic. Its INPUTS survive without the story
  //    (herbalbrews:flask, herbalbrews:green_tea_leaf, minecraft:sugar are all
  //    real), but the OUTPUT does not — valley_items.js is not in this pack —
  //    so there is nothing to craft. Dropped.
  //  * green oak plank, seasoned oak board, firewood bundle, wool blanket,
  //    paper lantern, chicken feed, place setting, delivery crate, courier
  //    parcel, Surveyor's Stake. Every one of these outputs a valley: item.
  //    Dropped with the item registry.
  //  * All seven gates and their `event.remove` calls. See the header.
  // ---------------------------------------------------------------------------

  console.info('[kettletech] anti-grind recipes applied')
})
