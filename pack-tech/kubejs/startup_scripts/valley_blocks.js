// valley_blocks.js — block tweaks that keep story items from becoming traps.
// The Copper Tea Kettle (Let's Do: HerbalBrews) is handed over on first join and
// is a keepsake the story keeps pointing at. Its block needs a pickaxe to drop,
// so a player who sets it on the hearth and picks it up by hand loses it with no
// message. Hand-breakable, drops itself, every time.
BlockEvents.modification(event => {
  ['herbalbrews:copper_tea_kettle', 'herbalbrews:tea_kettle'].forEach(id => {
    event.modify(id, block => {
      block.requiresTool = false
      // NOT `hardness`. BlockKJS exposes kjs$setDestroySpeed, and `block.hardness`
      // throws "has no public instance field or method named hardness" at startup,
      // which fails the whole startup script and takes the server down with it.
      block.destroySpeed = 0.5
    })
  })
})

// -----------------------------------------------------------------------------
// The other two block traps found by the same sweep are fixed with loot table
// overrides rather than block properties, because the problem is the table, not
// the tool:
//
//   pack/kubejs/data/vinery/loot_tables/blocks/apple_press.json
//     Vinery ships an EMPTY table ({}). A placed Apple Press is destroyed by
//     any tool, silently.
//
//   pack/kubejs/data/farm_and_charm/loot_tables/blocks/chicken_nest.json
//     Farm & Charm drops the nest itself only with Silk Touch; a bare hand gets
//     0-2 wheat and the nest is gone.
//
// Verified on the headless server with `/setblock` + `/loot spawn ... mine ...
// minecraft:air`: every block the quests ask a player to place now drops itself
// into an empty hand. See docs/RUNBOOK.md, "Lost something".
