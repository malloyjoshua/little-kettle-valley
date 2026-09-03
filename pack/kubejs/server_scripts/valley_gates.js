// =============================================================================
// valley_gates.js — Copper Kettle Valley: the six ingredient gates, plus the
// anti-grind recipe edits named in §8.
//
// The rule (§5 "How gating actually works", §12.2 P4):
//   There is no GameStages / Recipe Stages / CraftTweaker in this pack, so
//   per-player recipe locking does not exist. EVERY gate is world-level and
//   ingredient-based: remove the original recipe, add a replacement that
//   consumes the gate item. JEI then shows the true path and nobody opens
//   a wiki. A removed recipe ALWAYS ships with its replacement.
//
// KubeJS 2001.6.5 note: .stage() exists on event.shaped()/event.shapeless()
// but it is deliberately NOT used anywhere here — it is per player, and §9-C
// (the one-per-world rule) needs these to be world-level.
//
// Every item id below was checked against scratch/ids.json.
// =============================================================================

ServerEvents.recipes(event => {

  // ===========================================================================
  // GATE 1 — Seasoned Oak Boards -> the first Water Wheel.  (Q15 -> Q16)
  // "Bram can't build the wheel until the boards are dry — that's the oven,
  //  and that's you." Q15 depends on Q8 alone, so she unblocks him in hour one.
  // Original: 8 planks + 1 shaft (create:crafting/kinetics/water_wheel).
  // ===========================================================================
  event.remove({ output: 'create:water_wheel' })
  event.shaped('create:water_wheel', [
    'SBS',
    'BCB',
    'SBS'
  ], {
    S: '#minecraft:planks',
    B: 'valley:seasoned_oak_board',
    C: 'create:shaft'
  }).id('valley:gate/water_wheel')

  // The Large Water Wheel eats a Water Wheel, so it inherits the gate. Its own
  // recipe is left alone on purpose — gating it twice would read as a wall.

  // ===========================================================================
  // GATE 2 — Washed Silica -> the first Thermal Machine Frame.  (Q26/Q30 -> Q31)
  // Lake sand from Nella's dredging, washed under a Create fan. No fishing
  // trip, no Pulverizer. Thermal generates the frame recipe in code rather
  // than shipping a json, so remove-by-output is the only handle; the
  // replacement below is the recipe JEI will show from now on.
  // ===========================================================================
  event.remove({ output: 'thermal:machine_frame' })
  event.shaped('thermal:machine_frame', [
    'TGT',
    'GSG',
    'TGT'
  ], {
    T: '#forge:ingots/tin',
    G: 'minecraft:glass',
    S: 'valley:washed_silica'
  }).id('valley:gate/machine_frame')

  // ===========================================================================
  // GATE 3 — the Works Power Tap -> Cooking for Blockheads.  (Q47)
  // "An energy cell within 12 blocks of the inn" is not expressible as a
  // recipe condition (§12.1 C11), so Q47 pays out valley:works_power_tap and
  // the 12-block proximity is checked by the QUEST (valley_checks.js, q47).
  // Fridge / Sink / Milk Jar each consume the tap.
  // ===========================================================================
  event.remove({ output: 'cookingforblockheads:fridge' })
  event.shapeless('cookingforblockheads:fridge', [
    '#balm:wooden_chests', 'minecraft:iron_door', 'valley:works_power_tap'
  ]).id('valley:gate/cfb_fridge')

  event.remove({ output: 'cookingforblockheads:sink' })
  event.shaped('cookingforblockheads:sink', [
    'III',
    'CBC',
    'CPC'
  ], {
    I: '#forge:ingots/iron',
    C: 'minecraft:terracotta',
    B: 'minecraft:water_bucket',
    P: 'valley:works_power_tap'
  }).id('valley:gate/cfb_sink')

  event.remove({ output: 'cookingforblockheads:milk_jar' })
  event.shaped('cookingforblockheads:milk_jar', [
    'GPG',
    'GMG',
    'GTG'
  ], {
    G: 'minecraft:glass',
    P: '#minecraft:planks',
    M: 'minecraft:milk_bucket',
    T: 'valley:works_power_tap'
  }).id('valley:gate/cfb_milk_jar')

  // ===========================================================================
  // GATE 4 — Spring Water -> the certus quartz path.  (Q41 -> Q50)
  // AE2 15.4.10 has NO crystal-seed items (verified against the item registry:
  // certus growth is budding-block + Charger only). The chokepoint that still
  // means "AE2 does not start until the herbalist likes you" is the CHARGER,
  // which is the only route to charged certus and therefore to fluix and to
  // every AE2 machine. The Crystal Growth Accelerator is gated with it so the
  // whole crystal line sits behind Halden's spring.
  // ===========================================================================
  event.remove({ output: 'ae2:charger' })
  event.shaped('ae2:charger', [
    'aWa',
    'a b',
    'aba'
  ], {
    a: '#forge:ingots/iron',
    b: '#forge:ingots/copper',
    W: 'valley:spring_water'
  }).id('valley:gate/ae2_charger')

  event.remove({ output: 'ae2:growth_accelerator' })
  event.shaped('ae2:growth_accelerator', [
    'QSQ',
    'FWF',
    'QSQ'
  ], {
    Q: 'ae2:quartz_glass',
    S: 'ae2:certus_quartz_crystal',
    F: 'ae2:fluix_crystal',
    W: 'valley:spring_water'
  }).id('valley:gate/ae2_growth_accelerator')

  // ===========================================================================
  // GATE 5 — Josie's Turbine Notes -> Bigger Reactors.  (Q54 reveals, Q67 earns)
  // Casings AND the terminal both consume the notes, so the reactor is
  // visible in JEI from Q54 and craftable from Q67 — revealed, then earned.
  // Note: a KubeJS stage is deliberately not used here (see the header).
  // ===========================================================================
  event.remove({ output: 'biggerreactors:reactor_casing' })
  event.shaped('4x biggerreactors:reactor_casing', [
    'IGI',
    'GYG',
    'INI'
  ], {
    I: 'minecraft:iron_ingot',
    G: '#forge:ingots/graphite',
    Y: '#forge:ingots/uranium',
    N: 'valley:turbine_notes'
  }).id('valley:gate/reactor_casing')

  event.remove({ output: 'biggerreactors:reactor_terminal' })
  event.shaped('biggerreactors:reactor_terminal', [
    'C C',
    'YDY',
    'CNC'
  ], {
    C: 'biggerreactors:reactor_casing',
    Y: '#forge:ingots/uranium',
    D: 'minecraft:diamond',
    N: 'valley:turbine_notes'
  }).id('valley:gate/reactor_terminal')

  // ===========================================================================
  // GATE 6 — The Works Deed -> QuarryPlus.  (Q86 -> Q87)
  // quarryplus:quarry is a `quarryplus:workbench_recipe`, not a bench recipe,
  // so the replacement is re-emitted as the same custom type with the deed
  // added to the ingredient list. The Workbench stays the way you build a
  // quarry; the deed is simply one more thing on the list.
  // ===========================================================================
  event.remove({ output: 'quarryplus:quarry' })
  event.custom({
    type: 'quarryplus:workbench_recipe',
    energy: 320000.0,
    ingredients: [
      { count: 32, tag: 'forge:gems/diamond' },
      { count: 32, tag: 'forge:ingots/gold' },
      { count: 64, tag: 'forge:ingots/iron' },
      { count: 16, tag: 'forge:dusts/redstone' },
      { count: 4, tag: 'forge:ender_pearls' },
      { count: 1, item: 'valley:deed_works' }
    ],
    result: { count: 1, item: 'quarryplus:quarry' },
    showInJEI: true,
    subType: 'default'
  }).id('valley:gate/quarry')

  // ===========================================================================
  // GATE 7 (an ENABLE, not a gate) — reactor heat -> winter crops.  (Q72)
  // Serene Seasons 9.1.0.3 does not ship a Greenhouse Glass ITEM: greenhouse
  // glass is the BLOCK TAG sereneseasons:greenhouse_glass, which by default
  // contains #forge:glass — i.e. every glass block already works, and a tag
  // cannot be flipped at runtime.
  // Substitute, same shape as every other gate: the tag is narrowed to
  // minecraft:tinted_glass (see ServerEvents.tags below) and tinted glass is
  // re-cut so it consumes a Cyanite Ingot, which only exists once a reactor
  // has actually run. The reactor is still literally the reason food exists
  // in January, and it is one ingredient in JEI instead of a hidden hook.
  // ===========================================================================
  event.remove({ output: 'minecraft:tinted_glass' })
  event.shaped('2x minecraft:tinted_glass', [
    ' A ',
    'AGA',
    ' C '
  ], {
    A: 'minecraft:amethyst_shard',
    G: 'minecraft:glass',
    C: 'biggerreactors:cyanite_ingot'
  }).id('valley:gate/greenhouse_glass')

  // ===========================================================================
  // ANTI-GRIND — §8 "Standing rules baked in everywhere"
  // ===========================================================================

  // The bounty board. Vanilla Bountiful wants a diamond in hour two of a pack
  // whose whole claim is that hour one has no mining in it. Copper instead.
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
  }).id('valley:cheap/bountyboard')

  // "Megatorches arrive with the first structure that needs one, not after the
  // first bad night." Q4 hands one over in hour one, so the craft has to be
  // reachable in hour one too: 2 diamonds + 2 gold blocks becomes copper.
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
  }).id('valley:cheap/megatorch')

  // Waystones are given, never crafted (§8) — but leaving no recipe at all
  // desyncs JEI, so a cheap one stands behind the gift.
  event.shaped('waystones:waystone', [
    'SSS',
    'SCS',
    'SSS'
  ], {
    S: 'minecraft:stone_bricks',
    C: 'minecraft:copper_ingot'
  }).id('valley:cheap/waystone')

  // ===========================================================================
  // The custom items that have to be craftable, so JEI never shows a dead end.
  // Everything else (Scrip, tokens, plates, notes, deeds) is quest-granted on
  // purpose and has no recipe by design.
  // ===========================================================================

  // Green Oak Plank -> the thing Q15 dries in Marnie's oven.
  event.shapeless('4x valley:green_oak_plank', ['minecraft:oak_log'])
    .id('valley:craft/green_oak_plank')

  // Q15: the oven does the drying. A furnace recipe is the readable stand-in
  // so the path is visible in JEI from the moment she has a log.
  event.smelting('valley:seasoned_oak_board', 'valley:green_oak_plank')
    .xp(0.1).cookingTime(200).id('valley:craft/seasoned_oak_board')

  // Q26 -> Q30: lake sand washes into silica. Handed as a bench recipe so the
  // Create fan setup is a choice, not a requirement.
  event.shapeless('valley:washed_silica', [
    'valley:lake_sand', 'valley:lake_sand', 'minecraft:water_bucket'
  ]).id('valley:craft/washed_silica')

  // Firewood, blankets and lanterns are chores, not puzzles.
  event.shapeless('valley:firewood_bundle', [
    '#minecraft:logs', '#minecraft:logs', 'minecraft:string'
  ]).id('valley:craft/firewood_bundle')

  event.shaped('valley:blanket', [
    'WWW',
    'WSW',
    'WWW'
  ], { W: '#minecraft:wool', S: 'minecraft:string' })
    .id('valley:craft/blanket')

  event.shaped('4x valley:paper_lantern', [
    'PPP',
    'PTP',
    'PPP'
  ], { P: 'minecraft:paper', T: 'minecraft:torch' })
    .id('valley:craft/paper_lantern')

  event.shapeless('4x valley:chicken_feed', [
    'minecraft:wheat_seeds', 'minecraft:wheat', 'minecraft:bone_meal'
  ]).id('valley:craft/chicken_feed')

  event.shaped('valley:place_setting', [
    ' B ',
    'SPK'
  ], {
    B: 'minecraft:bowl',
    S: '#forge:ingots/iron',
    P: 'minecraft:brick',
    K: '#forge:ingots/copper'
  }).id('valley:craft/place_setting')

  event.shaped('valley:delivery_crate', [
    'BBB',
    'B B',
    'BBB'
  ], { B: '#minecraft:planks' })
    .id('valley:craft/delivery_crate')

  event.shaped('valley:courier_parcel', [
    'PPP',
    'PBP',
    'PPP'
  ], { P: 'minecraft:paper', B: 'minecraft:string' })
    .id('valley:craft/courier_parcel')

  // The Surveyor's Stake (Q7). One per world in practice, but craftable so a
  // re-anchored world is never stuck.
  event.shaped('valley:town_anchor', [
    ' C ',
    'SSS',
    'SSS'
  ], { C: 'minecraft:copper_ingot', S: 'minecraft:stone_bricks' })
    .id('valley:craft/town_anchor')

  console.info('[valley] gates + anti-grind recipes applied')
})

// =============================================================================
// The greenhouse-glass tag narrowing that GATE 7 depends on.
// Default: #forge:glass + #c:glass_blocks (i.e. all glass). Narrowed to tinted
// glass so the reactor-gated recipe above is the only way to build a
// greenhouse that grows out of season.
// =============================================================================
ServerEvents.tags('block', event => {
  event.removeAll('sereneseasons:greenhouse_glass')
  event.add('sereneseasons:greenhouse_glass', 'minecraft:tinted_glass')
})
