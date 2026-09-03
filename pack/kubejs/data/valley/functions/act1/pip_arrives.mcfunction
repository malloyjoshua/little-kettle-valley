# valley:act1/pip_arrives
# Q11 reward — "Take Three Eggs to Marnie." Pip moves in with a duckling.
# Invoked positioned at the player, at the inn / cottage. The Act I finale
# re-imports Pip at the anchor for the Fair; same UUID, so he is moved, not
# duplicated (docs/NPCS.md, "Importing and re-importing").

fill ~-2 ~0 ~2 ~2 ~0 ~4 minecraft:dirt_path
setblock ~2 ~1 ~3 minecraft:oak_fence
setblock ~2 ~2 ~3 createdeco:yellow_copper_lamp[facing=up,inverted=true,lit=true]

# --- Pip, and the duck he was promised for being extremely useful ----------
easy_npc preset import data valley:easy_npc/preset/pip.npc.snbt ~0 ~1 ~3
summon duckling:duck ~0 ~1 ~4 {PersistenceRequired:1b,NoAI:1b}

# --- his courier board -----------------------------------------------------
setblock ~-2 ~1 ~3 minecraft:oak_fence
setblock ~-2 ~2 ~3 minecraft:oak_wall_sign[facing=south]{front_text:{messages:['{"text":"PIPS DELIVERYS"}','{"text":"fast"}','{"text":"very fast"}','{"text":"ask me"}']}}
setblock ~-1 ~1 ~3 domesticationinnovation:pet_bed_yellow

tellraw @a[distance=..64] [{"text":"Pip: ","color":"red"},{"text":"\"Is that an egg? Aunt Marnie says I get a duck if I'm useful, so I am being extremely useful.\"","color":"white","italic":true}]
playsound minecraft:entity.chicken.ambient master @a[distance=..64] ~ ~ ~ 1 1.6
