# valley:setup/place_ruin
# First join, once per world (story-final.md §3 "The one exception, and it
# matters", §12.1 C5, §12.5). Invoked by valley_core.js as:
#     execute positioned <hx> <hy> <hz> run function valley:setup/place_ruin
# where <hx hy hz> is the HEARTHSTONE: the block the player will stand on to
# place the Homestead Waystone in Q2, one above the levelled pad.
#
# The premise, Q1's map and Q2's instruction all describe this house. Nothing
# in the pack built it — the only chimney in the files was the one Q2's own
# reward puts up — so Q2 sent the player to look for a building that did not
# exist. This is that building.
#
# §7 rule 2, the levelled-pad rule: clear air above, fill the pad, then
# /place template. Never /place structure onto live terrain.

# --- clear everything standing on the site ---------------------------------
fill ~-9 ~0 ~-9 ~9 ~14 ~9 minecraft:air

# --- the pad: rock, then soil, then the yard she walks on at ~-1 -----------
fill ~-9 ~-5 ~-9 ~9 ~-3 ~9 minecraft:stone
fill ~-9 ~-2 ~-9 ~9 ~-2 ~9 minecraft:dirt
fill ~-9 ~-1 ~-9 ~9 ~-1 ~9 minecraft:grass_block

# --- the ruin. Local (5,2,5) is the hearthstone, so the template's
#     north-west-bottom corner is (-5,-2,-5) from here. -------------------
place template valley:kettle_ruin ~-5 ~-2 ~-5

# --- the yard: four years of nobody keeping it ------------------------------
setblock ~-7 ~0 ~6 minecraft:oak_fence
setblock ~-6 ~0 ~7 minecraft:oak_fence
setblock ~7 ~0 ~-6 minecraft:mossy_cobblestone
setblock ~-8 ~0 ~-7 minecraft:mossy_cobblestone
setblock ~6 ~0 ~7 minecraft:oak_fence

# --- the gate sign, so the end of the path is unmistakably the place -------
setblock ~0 ~0 ~7 minecraft:oak_fence
setblock ~0 ~1 ~7 minecraft:oak_sign[rotation=8]{front_text:{messages:['{"text":"KETTLE FARM"}','{"text":""}','{"text":"J. Kettle"}','{"text":"est. long ago"}'],color:"gray"}}
setblock ~-1 ~0 ~7 minecraft:lantern[hanging=false]
setblock ~1 ~0 ~7 minecraft:lantern[hanging=false]
