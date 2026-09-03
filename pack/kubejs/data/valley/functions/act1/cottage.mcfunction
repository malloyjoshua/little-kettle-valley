# valley:act1/cottage
# Q2 reward — "Put the Waystone on the Hearthstone."
# Invoked by valley_checks.js on the Q2 waystone placement, positioned at the
# WAYSTONE — that is, at the ruin's hearthstone. It used to run from the quest
# reward at {x} {y} {z}, the claiming player's feet, which since the ruin is now
# actually on the ground would have rebuilt the cottage off-centre and left the
# old walls standing through the new ones.
#
# Every offset below therefore lines up, block for block, with the local
# coordinates of valley:kettle_ruin (see tools/scripts/make_structures.py).
#
# The ruin becomes a cottage shell: four walls, a roof, a doorway, two window
# holes and a wool mat where the bed goes. The player is standing ON the
# hearthstone with the Homestead Waystone they just placed, so NOTHING in this
# file touches the 3x3 column around ~0 ~0 ~0 below head height. Every clear
# either sits above y+2 or is a `replace` on vegetation only.
# All coordinates are ~ offsets from the invocation position (§7 rule 3).

# --- clear the site: vegetation and snow only, so the waystone survives -----
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:grass
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:tall_grass
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:fern
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:large_fern
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:dead_bush
fill ~-6 ~0 ~-6 ~6 ~2 ~6 minecraft:air replace minecraft:snow
# above head height the site is cleared outright, so a tree cannot sit in the roof
fill ~-6 ~3 ~-6 ~6 ~9 ~6 minecraft:air

# --- clear the RUIN's loose interior: the bed frame, the cobwebs, the fallen
#     stone. Named block types only, never a plain box fill, because the
#     Homestead Waystone is standing at ~0 ~0 ~0 and must survive this.
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:oak_fence
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:stripped_oak_log
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:cobweb
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:cobblestone
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:mossy_cobblestone
fill ~-3 ~0 ~-3 ~3 ~2 ~3 minecraft:air replace minecraft:campfire

# --- foundation and floor ---------------------------------------------------
fill ~-5 ~-2 ~-5 ~5 ~-2 ~5 minecraft:cobblestone
fill ~-4 ~-1 ~-4 ~4 ~-1 ~4 minecraft:oak_planks
# the hearthstone stays a hearthstone; the waystone is standing on it
setblock ~0 ~-1 ~0 minecraft:polished_andesite

# --- four walls, three high, on the 9x9 footprint ---------------------------
fill ~-4 ~0 ~-4 ~4 ~2 ~-4 minecraft:oak_planks
fill ~-4 ~0 ~4 ~4 ~2 ~4 minecraft:oak_planks
fill ~-4 ~0 ~-4 ~-4 ~2 ~4 minecraft:oak_planks
fill ~4 ~0 ~-4 ~4 ~2 ~4 minecraft:oak_planks

# --- corner posts -----------------------------------------------------------
fill ~-4 ~0 ~-4 ~-4 ~2 ~-4 minecraft:oak_log
fill ~4 ~0 ~-4 ~4 ~2 ~-4 minecraft:oak_log
fill ~-4 ~0 ~4 ~-4 ~2 ~4 minecraft:oak_log
fill ~4 ~0 ~4 ~4 ~2 ~4 minecraft:oak_log

# --- the doorway, south wall, 1 wide and 2 high (Q3 hangs the door here) ----
fill ~0 ~0 ~4 ~0 ~1 ~4 minecraft:air
setblock ~-1 ~0 ~4 minecraft:oak_log[axis=y]
setblock ~1 ~0 ~4 minecraft:oak_log[axis=y]

# --- two window holes, 1 wide and 2 high, one per side wall ------------------
fill ~-4 ~1 ~-1 ~-4 ~2 ~-1 minecraft:air
fill ~4 ~1 ~-1 ~4 ~2 ~-1 minecraft:air

# --- the hook by the door, for Q3's sconce ----------------------------------
setblock ~1 ~1 ~3 minecraft:oak_fence

# --- roof: a plank deck and two stair tiers ---------------------------------
fill ~-5 ~3 ~-5 ~5 ~3 ~5 minecraft:oak_planks
fill ~-4 ~4 ~-4 ~4 ~4 ~-4 minecraft:oak_stairs[facing=north]
fill ~-4 ~4 ~4 ~4 ~4 ~4 minecraft:oak_stairs[facing=south]
fill ~-4 ~4 ~-3 ~-4 ~4 ~3 minecraft:oak_stairs[facing=west]
fill ~4 ~4 ~-3 ~4 ~4 ~3 minecraft:oak_stairs[facing=east]
fill ~-3 ~4 ~-3 ~3 ~4 ~3 minecraft:oak_planks
fill ~-2 ~5 ~-2 ~2 ~5 ~2 minecraft:oak_planks

# --- the chimney Josie said was the one thing she never had to fix ----------
fill ~-5 ~-1 ~-2 ~-5 ~6 ~-2 minecraft:bricks
setblock ~-5 ~7 ~-2 minecraft:campfire[lit=true]

# --- the wool mat where the bed goes (Q3 puts the Red Bed on it) ------------
setblock ~-3 ~-1 ~-3 minecraft:white_wool
setblock ~-3 ~-1 ~-2 minecraft:white_wool
setblock ~-2 ~-1 ~-3 minecraft:red_carpet
setblock ~-2 ~-1 ~-2 minecraft:red_carpet

# --- light and a place to put things ---------------------------------------
setblock ~3 ~-1 ~-3 minecraft:barrel[facing=up]
setblock ~2 ~2 ~-2 minecraft:lantern[hanging=true]

# ===========================================================================
# THE BACK YARD: the marks Q9 and Q10 are written against.
#
# Q9 says "every tile is marked in path blocks" and Q10 says "put a fence
# section on each marked block behind the house". Nothing in the pack marked
# anything: cottage.mcfunction stopped at its own 9x9, and marnie_arrives laid
# a 5x3 dirt_path pad SOUTH of the door — 15 tiles, the wrong side of the
# house, and the wrong count — which is the only thing a player looking for
# "the 3x9 patch behind the house" could have found.
#
# The marks go HERE, at Q2, because this function is the only one in Act I
# invoked at a fixed point: valley_checks.js runs it positioned at the
# HEARTHSTONE (the Q2 waystone). marnie_arrives and nesting_box run at
# `{x} {y} {z}` — the claiming player's feet — so anything measured out there
# lands wherever the card happened to be claimed.
#
# Convention, the same as place_ruin: the ground the player walks on is at
# ~-1 and everything stands at ~0. "Behind the house" is north, -z.
# ===========================================================================

# --- level the back yard out to z-13. place_ruin's pad only reaches +/-9. ---
fill ~-9 ~0 ~-13 ~9 ~12 ~-6 minecraft:air
fill ~-9 ~-3 ~-13 ~9 ~-2 ~-6 minecraft:dirt
fill ~-9 ~-1 ~-13 ~9 ~-1 ~-6 minecraft:grass_block

# --- Q9: the 3x9 patch. 9 wide, 3 deep, 27 tiles, one per seed she hands
#     over (9 wheat, 9 carrots, 9 potatoes). dirt_path is in HoeItem's
#     TILLABLES, so every marked tile takes a hoe straight to farmland. -----
fill ~-8 ~-1 ~-8 ~0 ~-1 ~-6 minecraft:dirt_path

# --- the well. Farmland is hydrated from water within 4 blocks at its own
#     level, so one source at the head of the patch keeps all 27 tiles wet:
#     x -8..0 is 4 either side of -4, and z -8..-6 is 2 to 4 north of -10.
#     All four neighbours and the block under it are solid, so it never
#     spreads. Without this the beds dry out and she waters by hand forever.
setblock ~-4 ~-1 ~-10 minecraft:water

# --- Q10: the pen. A 7x7 outline behind the house, 24 marked blocks:
#     23 cobblestone footings for Marnie's fence sections and one polished
#     andesite slot for the gate, in the middle of the side facing the house.
#     Cobblestone, not dirt_path, so the pen marks and the garden marks can
#     never be read as the same instruction. ---------------------------------
fill ~1 ~-1 ~-12 ~7 ~-1 ~-12 minecraft:cobblestone
fill ~1 ~-1 ~-6 ~7 ~-1 ~-6 minecraft:cobblestone
fill ~1 ~-1 ~-11 ~1 ~-1 ~-7 minecraft:cobblestone
fill ~7 ~-1 ~-11 ~7 ~-1 ~-7 minecraft:cobblestone
setblock ~4 ~-1 ~-6 minecraft:polished_andesite

# --- two signs, so neither plot is a judgement call (writer brief rule 8) --
setblock ~-4 ~0 ~-5 minecraft:oak_sign[rotation=8]{front_text:{messages:['{"text":"3 x 9"}','{"text":"wheat"}','{"text":"carrots"}','{"text":"potatoes"}'],color:"gray"}}
setblock ~4 ~0 ~-5 minecraft:oak_sign[rotation=8]{front_text:{messages:['{"text":"THE PEN"}','{"text":"fence the stone"}','{"text":"gate on the grey"}','{"text":""}'],color:"gray"}}

tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\"Four walls and a door. That is a house. What you do next makes it a home.\"","color":"white","italic":true}]
playsound minecraft:block.wood.place master @a[distance=..64] ~ ~ ~ 1 0.9
