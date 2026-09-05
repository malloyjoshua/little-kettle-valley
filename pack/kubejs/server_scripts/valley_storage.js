// valley_storage.js — one Chest, one Barrel. Josh (2026-09-05): "crafting recipes
// seem to collide, look at the chest." The pack shipped two items called Chest
// with the same face: vanilla's and Sophisticated Storage's upgradeable one (the
// "bigger chests" ask). JEI showed both, and the mod's shapeless vanilla->
// upgradeable conversion looked like a colliding recipe. Now the ordinary eight-
// planks ring makes the upgradeable Chest and three planks over slabs make the
// upgradeable Barrel; the vanilla recipes are retired (vanilla chests still exist
// in the world and loot, and still convert 1:1 in the grid).
ServerEvents.recipes(event => {
  event.remove({ output: 'minecraft:chest', type: 'minecraft:crafting_shaped' })
  event.remove({ output: 'minecraft:barrel', type: 'minecraft:crafting_shaped' })
  event.shaped('sophisticatedstorage:chest', ['PPP', 'P P', 'PPP'], { P: '#minecraft:planks' })
    .id('valley:one_chest')
  event.shaped('sophisticatedstorage:barrel', ['PSP', 'P P', 'PSP'], { P: '#minecraft:planks', S: '#minecraft:wooden_slabs' })
    .id('valley:one_barrel')
})
