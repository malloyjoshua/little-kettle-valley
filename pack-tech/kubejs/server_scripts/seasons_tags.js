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
// SPRING WHEAT (carried over from the story pack, and it matters more here).
//
// Evidence:
//   * config/sereneseasons/seasons.toml -> starting_sub_season = 1, i.e. every
//     new world opens in EARLY SPRING.
//   * Live tag dump: minecraft:wheat / minecraft:wheat_seeds ship in
//     sereneseasons summer_crops and autumn_crops ONLY -- never spring.
//   * fertility.toml out_of_season_crop_behavior = 1 ("Can't grow"), so wheat
//     planted in spring does not advance and does not say why.
//
// Net effect without this: a fresh world cannot grow its own wheat -- no
// bread, no Create wheat flour, no hay -- until summer arrives on its own.
// Village farms are the only source. In the story pack a script pinned the
// season to spring for two acts and made that a hard stop; here nothing pins
// anything, but the first in-game month is still a food desert for no reason.
//
// Smallest fix: make wheat spring-fertile too. Winter still blocks it, so the
// seasonal feel is preserved.
// ---------------------------------------------------------------------------
ServerEvents.tags('block', event => {
  event.add('sereneseasons:spring_crops', 'minecraft:wheat')
})
ServerEvents.tags('item', event => {
  event.add('sereneseasons:spring_crops', 'minecraft:wheat_seeds')
})
