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
