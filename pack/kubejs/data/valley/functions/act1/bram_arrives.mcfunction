# valley:act1/bram_arrives
# Q8 reward — "Sleep One Night in Your Bed." Marnie sees the chimney; Bram is
# already down at the mill, and Q12 sends the player to him.
#
# Invoked by /valley scene bram, positioned at the MILL mark
# (VALLEY.OFF.mill = anchor + [-26, 0, 4]) — the same origin valley_finales.js
# used for the mill race, so the race, this shell and the Act V mill_roof at
# anchor + [-24, 4, 2] all line up.
#
# Why this file exists: Q12's only task is handing in valley:token_bram, the
# token's only source is Bram's ON_INTERACTION action, and Bram's only import
# in the pack was inside finaleAct1 — which runs from Q19's reward, seven
# quests AFTER Q12. Act I could not be finished. He arrives here instead.
#
# The mill race moved here for the same reason: Q16 says "the race is cut" and
# asks for two Water Wheels in it, and the race was not cut until the finale.
# §7 rule 2 all the way down: clear air, fill the pad, then place the template.

# --- clear and level the mill plot -----------------------------------------
fill ~-6 ~1 ~-6 ~13 ~12 ~9 minecraft:air
fill ~-6 ~-3 ~-6 ~13 ~-1 ~9 minecraft:dirt
fill ~-6 ~0 ~-6 ~13 ~0 ~9 minecraft:grass_block
fill ~-1 ~0 ~-3 ~11 ~0 ~7 minecraft:cobblestone

# --- the mill house: a shell with no wheel and no axle ---------------------
fill ~2 ~1 ~-2 ~10 ~3 ~6 minecraft:oak_planks hollow
fill ~3 ~1 ~-1 ~9 ~3 ~5 minecraft:air
fill ~2 ~1 ~-2 ~2 ~3 ~-2 minecraft:oak_log[axis=y]
fill ~10 ~1 ~-2 ~10 ~3 ~-2 minecraft:oak_log[axis=y]
fill ~2 ~1 ~6 ~2 ~3 ~6 minecraft:oak_log[axis=y]
fill ~10 ~1 ~6 ~10 ~3 ~6 minecraft:oak_log[axis=y]
# the door, east side
fill ~10 ~1 ~2 ~10 ~2 ~2 minecraft:air
# two windows
fill ~6 ~2 ~-2 ~7 ~2 ~-2 minecraft:air
fill ~6 ~2 ~6 ~7 ~2 ~6 minecraft:air

# --- the race, cut through the west end. The template overwrites the wall
#     where it crosses, which is exactly the opening the water needs. -------
place template valley:mill_race ~0 ~0 ~0

# --- cap both ends of the channel. valley:mill_race ships seven source blocks
#     in an open-ended trough, so left as the template lands it the water
#     walks out of both ends and floods the mill floor and the doorway. The
#     drain-and-refill below makes the result the same whichever tick the
#     fluid updates land on.
setblock ~-1 ~1 ~1 minecraft:stone_bricks
setblock ~7 ~1 ~1 minecraft:stone_bricks
setblock ~-1 ~2 ~1 minecraft:stone_brick_slab[type=bottom]
setblock ~7 ~2 ~1 minecraft:stone_brick_slab[type=bottom]
fill ~-6 ~1 ~-6 ~13 ~6 ~9 minecraft:air replace minecraft:water
fill ~0 ~1 ~1 ~6 ~1 ~1 minecraft:water[level=0]

# --- the snapped axle, on the floor where it fell --------------------------
setblock ~4 ~1 ~4 minecraft:stripped_oak_log[axis=x]
setblock ~5 ~1 ~4 minecraft:stripped_oak_log[axis=x]
setblock ~6 ~1 ~4 minecraft:oak_log[axis=x]
setblock ~7 ~1 ~5 minecraft:stripped_oak_log[axis=z]

# --- his labelled crates. Q12's text: "Bram opens his labelled crates." ----
setblock ~8 ~1 ~-1 minecraft:barrel[facing=up]
setblock ~8 ~1 ~1 minecraft:barrel[facing=up]
setblock ~9 ~1 ~1 handcrafted:oak_table
setblock ~9 ~1 ~3 minecraft:crafting_table

# --- light, and a sign so the mill plot on the map is unmistakable ---------
setblock ~12 ~1 ~0 minecraft:oak_fence
setblock ~12 ~2 ~0 minecraft:lantern[hanging=false]
setblock ~12 ~1 ~4 minecraft:oak_fence
setblock ~12 ~2 ~4 minecraft:lantern[hanging=false]
setblock ~12 ~1 ~2 minecraft:oak_fence
setblock ~12 ~2 ~2 minecraft:oak_sign[rotation=12]{front_text:{messages:['{"text":"THE MILL"}','{"text":""}','{"text":"B. Tolliver"}','{"text":"millwright"}'],color:"gray"}}

# --- Bram, outside the door, where the player walks up to him --------------
easy_npc preset import data valley:easy_npc/preset/bram.npc.snbt ~11 ~1 ~2

tellraw @a[distance=..96] [{"text":"Bram: ","color":"dark_aqua"},{"text":"\"Axle's snapped. Sixty years I've looked at it. Come here and hold something.\"","color":"white","italic":true}]
playsound minecraft:block.wood.break master @a[distance=..96] ~ ~ ~ 1 0.7
