// Farm & Charm ships its Serene Seasons tags at data/sereneseasons/blocks|items/
// instead of data/sereneseasons/tags/blocks|items/, so the game never loads them.
// Re-file them here. Values copied from the mod's own (misplaced) files.
ServerEvents.tags('block', event => {
  event.add('sereneseasons:spring_crops', 'farm_and_charm:onion_crop', 'farm_and_charm:strawberry_crop')
  event.add('sereneseasons:summer_crops', 'farm_and_charm:corn_crop', 'farm_and_charm:tomato_crop')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:barley_crop', 'farm_and_charm:lettuce_crop', 'farm_and_charm:oat_crop')
})
ServerEvents.tags('item', event => {
  event.add('sereneseasons:spring_crops', 'farm_and_charm:onion', 'farm_and_charm:strawberry_seeds')
  // corn's seed item is farm_and_charm:kernels (the plantable), not farm_and_charm:corn
  event.add('sereneseasons:summer_crops', 'farm_and_charm:kernels', 'farm_and_charm:tomato_seeds')
  event.add('sereneseasons:autumn_crops', 'farm_and_charm:barley_seeds', 'farm_and_charm:lettuce_seeds', 'farm_and_charm:oat_seeds')
})

// ---------------------------------------------------------------------------
// ACT I SOFT-LOCK FIX (integration sweep 2026-09-04).
//
// Evidence:
//   * server/config/sereneseasons/seasons.toml -> starting_sub_season = 1
//     (= EARLY_SPRING), and valley_finales.js finaleAct1() ends Act I with
//     `season set early_spring`. Act I and Act II are therefore both played
//     in SPRING; the world only reaches summer at the Act II finale
//     (valley_finales.js finaleAct2 -> `season set mid_summer`).
//   * Live tag dump (server/local/kubejs/export/tags/minecraft/{block,item}/
//     sereneseasons/): minecraft:wheat / minecraft:wheat_seeds are in
//     summer_crops and autumn_crops ONLY -- never spring.
//   * story/quests/act1.json q09 "Till and Plant the 3x9 Patch" tells the
//     player to plant "Wheat, carrots, potatoes"; q18 wants 1 bread; q19
//     (Act I finale) CONSUMES 16 create:wheat_flour + 8 minecraft:bread
//     (~40 wheat).
//   * fertility.toml out_of_season_crop_behavior = 1 ("Can't grow"), so the
//     planted wheat simply never advances -- it does not even fail loudly.
//
// Net effect without this: the Act I finale demands ~40 wheat that cannot be
// grown during Act I, and the season cannot be waited out because the script
// pins it to spring. Village farms are the only source.
//
// Smallest fix: make wheat spring-fertile too. Winter still blocks it, so the
// seasonal feel is preserved and no quest key, dependency or reward changes.
// ---------------------------------------------------------------------------
ServerEvents.tags('block', event => {
  event.add('sereneseasons:spring_crops', 'minecraft:wheat')
})
ServerEvents.tags('item', event => {
  event.add('sereneseasons:spring_crops', 'minecraft:wheat_seeds')
})
