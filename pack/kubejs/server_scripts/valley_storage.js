// valley_storage.js — one chest, one barrel, and nothing hijacks the ring.
//
// 2026-09-05: the plank ring used to be deleted from minecraft:chest and given to the
// Sophisticated chest instead. That broke nineteen recipes that want a VANILLA chest as an
// ingredient (Storage Drawers, the reactor access port, chest boats, sideboards, jewelry boxes)
// and the feasibility check found all of them uncraftable. So: vanilla keeps its ring and its
// barrel; the Sophisticated chest and barrel are UPGRADES of the vanilla ones (one plank, one
// slab). Both are visible in JEI, neither shape collides with anything.
ServerEvents.recipes(event => {
  event.shapeless('sophisticatedstorage:chest', ['minecraft:chest', '#minecraft:planks'])
    .id('valley:one_chest')
  event.shapeless('sophisticatedstorage:barrel', ['minecraft:barrel', '#minecraft:wooden_slabs'])
    .id('valley:one_barrel')
})
