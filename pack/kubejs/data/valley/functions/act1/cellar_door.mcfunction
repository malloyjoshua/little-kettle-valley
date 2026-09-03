# valley:act1/cellar_door
# Q5 reward — "Dig Out the Cellar Stairs."
# Invoked positioned at the player, who is standing at the bottom of the
# cleared stairs, below the cottage floor.
#
# What the quest text promises: "a sealed iron door with no handle, Josie's
# chalk on it, a Cellar Waystone and her tool chest."
# The door is IRON on purpose — no handle, and it stays shut until Act III.

# --- the chamber: a 7x4x7 room of stone brick, hollow ----------------------
fill ~-3 ~-1 ~-3 ~3 ~3 ~3 minecraft:stone_bricks hollow
fill ~-3 ~-1 ~-3 ~3 ~-1 ~3 minecraft:stone_bricks
fill ~-2 ~0 ~-2 ~2 ~2 ~2 minecraft:air
setblock ~0 ~-1 ~0 minecraft:polished_andesite

# --- the frame, north wall -------------------------------------------------
fill ~-2 ~0 ~-3 ~2 ~2 ~-3 minecraft:stone_bricks
setblock ~-1 ~0 ~-3 minecraft:chiseled_stone_bricks
setblock ~-1 ~1 ~-3 minecraft:chiseled_stone_bricks
setblock ~-1 ~2 ~-3 minecraft:chiseled_stone_bricks
setblock ~1 ~0 ~-3 minecraft:chiseled_stone_bricks
setblock ~1 ~1 ~-3 minecraft:chiseled_stone_bricks
setblock ~1 ~2 ~-3 minecraft:chiseled_stone_bricks
setblock ~0 ~2 ~-3 minecraft:stone_brick_slab[type=bottom]

# --- the door itself: iron, shut, no handle --------------------------------
setblock ~0 ~0 ~-3 minecraft:iron_door[facing=north,half=lower,hinge=left,open=false,powered=false]
setblock ~0 ~1 ~-3 minecraft:iron_door[facing=north,half=upper,hinge=left,open=false,powered=false]

# --- Josie's chalk, on the wall beside it ----------------------------------
setblock ~-1 ~1 ~-2 minecraft:oak_wall_sign[facing=south]{front_text:{messages:['{"text":"Not yet."}','{"text":""}','{"text":"- J.K."}','{"text":""}'],color:"gray"}}

# --- her tool chest, and a plinth for the Cellar Waystone the quest gives --
setblock ~2 ~0 ~2 minecraft:chest[facing=west]
setblock ~-2 ~-1 ~2 minecraft:polished_andesite
setblock ~2 ~1 ~-2 minecraft:lantern[hanging=false]
setblock ~-2 ~1 ~-2 minecraft:lantern[hanging=false]
setblock ~0 ~3 ~0 minecraft:lantern[hanging=true]

tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\"Not yet. I'll explain when you have people who can help you carry it.\"","color":"white","italic":true}]
playsound minecraft:block.chain.place master @a[distance=..64] ~ ~ ~ 1 0.7
