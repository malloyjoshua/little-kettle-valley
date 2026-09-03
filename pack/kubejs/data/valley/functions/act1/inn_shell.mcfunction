# valley:act1/inn_shell
# Q8 reward — "Sleep One Night in Your Bed."
#
# Q8's payoff line is "Marnie moves in, the inn shell goes up at the Town
# Anchor", and Q18 asks the player to "set them on the three marked spots along
# the inn's back wall: counter, sink, oven, in that order". Nothing in the pack
# built an inn. story-final.md P8 lists `inn_shell` as a required structure and
# it was never made, so the Hearth that Act IV puts out and Q60 relights was a
# campfire standing in an open field, and Q18's three chalked spots did not
# exist on any wall anywhere.
#
# This is that building. It is /fill'd rather than a template because there is
# no inn_shell.nbt to place and the shell is nine walls' worth of blocks, not
# thousands.
#
# Invoked by `/valley scene inn`, positioned at the INN MARK — the Hearth
# itself (VALLEY.OFF.inn). Every offset below is inn-local:
#   the ground and the floor are at ~-1, everything stands at ~0,
#   the walls run ~0..~3, the roof deck is ~4.
# The 9x9 footprint is centred on the Hearth, so the room reads as an old hall
# with a fire in the middle of it — which is what Act IV keeps calling "the
# Hearth" and putting out.
#
# WHY THE MARK MOVED. VALLEY.OFF.inn used to be anchor + [-14, 1, 4], which is
# the exact south-west corner block of the granary shell finaleAct2 places at
# anchor + [-14, 1, -4] (9x6x9, so x -14..-6, z -4..4). Any inn built on the
# old mark had the granary driven through its north wall and its Hearth six
# quests later. The mark is now anchor + [-8, 1, 12]: a 9x9 with a 1-block
# eave clears the granary (z <= 4), the mill plot (x <= -13), the town square
# paving (x >= -7 only above z 7), the bathhouse and its Q72 posts (x <= -15),
# the Act V town hall (z <= -7) and the Act V approach path (x -2..2).
# Everything anchored to `inn` — Q47's duct check, Q60's relight, Q70a's beds,
# Q73's chair, the Act IV hearth — moves with it, because they all address the
# mark and never a literal coordinate.

# ---------------------------------------------------------------------------
# The site. §7 rule 2: clear the air, fill the pad, then build.
# ---------------------------------------------------------------------------
fill ~-6 ~0 ~-6 ~6 ~14 ~6 minecraft:air
fill ~-6 ~-3 ~-6 ~6 ~-2 ~6 minecraft:dirt
fill ~-6 ~-1 ~-6 ~6 ~-1 ~6 minecraft:grass_block
# the apron under the eaves, laid in the same cobblestone the Act I finale
# paves the square with, so the two never meet at a seam of bare grass
fill ~-5 ~-1 ~-5 ~5 ~-1 ~5 minecraft:cobblestone

# ---------------------------------------------------------------------------
# Floor, walls, corner posts.
# ---------------------------------------------------------------------------
fill ~-4 ~-2 ~-4 ~4 ~-2 ~4 minecraft:cobblestone
fill ~-4 ~-1 ~-4 ~4 ~-1 ~4 minecraft:oak_planks

fill ~-4 ~0 ~-4 ~4 ~3 ~-4 minecraft:oak_planks
fill ~-4 ~0 ~4 ~4 ~3 ~4 minecraft:oak_planks
fill ~-4 ~0 ~-4 ~-4 ~3 ~4 minecraft:oak_planks
fill ~4 ~0 ~-4 ~4 ~3 ~4 minecraft:oak_planks
fill ~-3 ~0 ~-3 ~3 ~3 ~3 minecraft:air

fill ~-4 ~0 ~-4 ~-4 ~3 ~-4 minecraft:oak_log[axis=y]
fill ~4 ~0 ~-4 ~4 ~3 ~-4 minecraft:oak_log[axis=y]
fill ~-4 ~0 ~4 ~-4 ~3 ~4 minecraft:oak_log[axis=y]
fill ~4 ~0 ~4 ~4 ~3 ~4 minecraft:oak_log[axis=y]

# --- the door, north wall, facing the town square --------------------------
fill ~0 ~0 ~-4 ~0 ~1 ~-4 minecraft:air
setblock ~-1 ~0 ~-4 minecraft:oak_log[axis=y]
setblock ~1 ~0 ~-4 minecraft:oak_log[axis=y]

# --- four windows, two per side wall ---------------------------------------
fill ~-4 ~1 ~-2 ~-4 ~2 ~-2 minecraft:air
fill ~-4 ~1 ~2 ~-4 ~2 ~2 minecraft:air
fill ~4 ~1 ~-2 ~4 ~2 ~-2 minecraft:air
fill ~4 ~1 ~2 ~4 ~2 ~2 minecraft:air

# ---------------------------------------------------------------------------
# Roof, and the chimney over the Hearth.
# ---------------------------------------------------------------------------
fill ~-5 ~4 ~-5 ~5 ~4 ~5 minecraft:oak_planks
fill ~-4 ~5 ~-4 ~4 ~5 ~-4 minecraft:oak_stairs[facing=north]
fill ~-4 ~5 ~4 ~4 ~5 ~4 minecraft:oak_stairs[facing=south]
fill ~-4 ~5 ~-3 ~-4 ~5 ~3 minecraft:oak_stairs[facing=west]
fill ~4 ~5 ~-3 ~4 ~5 ~3 minecraft:oak_stairs[facing=east]
fill ~-3 ~5 ~-3 ~3 ~5 ~3 minecraft:oak_planks
fill ~-2 ~6 ~-2 ~2 ~6 ~2 minecraft:oak_planks
# a 3x3 brick stack from the roof deck up, then the flue punched through it,
# so the Hearth's smoke has somewhere to go and the roof has a hole for it
fill ~-1 ~4 ~-1 ~1 ~8 ~1 minecraft:bricks
fill ~0 ~4 ~0 ~0 ~9 ~0 minecraft:air

# ---------------------------------------------------------------------------
# The Hearth. Act IV puts this out and Q60 relights it; it is lit from the
# night Marnie moves in, which is what Q8 is about.
# ---------------------------------------------------------------------------
fill ~-1 ~-1 ~-1 ~1 ~-1 ~1 minecraft:stone_bricks
setblock ~0 ~0 ~0 minecraft:campfire[lit=true]

# ---------------------------------------------------------------------------
# Q18 — "Counter, sink, oven, along the back wall in that order. I've had the
# spots chalked for four years."
#
# The back wall is the south wall, opposite the door. Three floor tiles are
# swapped for polished andesite — the same block the pack uses for the
# hearthstone and the centre of the road when it means THIS EXACT SPOT — and
# each one has its own sign on the wall above it, west to east, in Marnie's
# order. The player stands in the doorway, reads three words, and puts three
# blocks down. Nothing to judge.
# ---------------------------------------------------------------------------
setblock ~-1 ~-1 ~3 minecraft:polished_andesite
setblock ~0 ~-1 ~3 minecraft:polished_andesite
setblock ~1 ~-1 ~3 minecraft:polished_andesite
setblock ~-1 ~1 ~3 minecraft:oak_wall_sign[facing=north]{front_text:{messages:['{"text":"1"}','{"text":"COUNTER"}','{"text":""}','{"text":"- M."}'],color:"gray"}}
setblock ~0 ~1 ~3 minecraft:oak_wall_sign[facing=north]{front_text:{messages:['{"text":"2"}','{"text":"SINK"}','{"text":""}','{"text":"- M."}'],color:"gray"}}
setblock ~1 ~1 ~3 minecraft:oak_wall_sign[facing=north]{front_text:{messages:['{"text":"3"}','{"text":"OVEN"}','{"text":""}','{"text":"- M."}'],color:"gray"}}

# --- "everything is in the crate by the counter" (Q18's own last line) -----
setblock ~-3 ~0 ~3 minecraft:barrel[facing=up]{Items:[{Slot:0b,id:"minecraft:wheat",Count:24b},{Slot:1b,id:"minecraft:pumpkin",Count:4b},{Slot:2b,id:"minecraft:sugar",Count:4b},{Slot:3b,id:"minecraft:egg",Count:4b},{Slot:4b,id:"minecraft:carrot",Count:4b},{Slot:5b,id:"minecraft:potato",Count:4b},{Slot:6b,id:"farmersdelight:cabbage",Count:4b},{Slot:7b,id:"minecraft:bowl",Count:4b},{Slot:8b,id:"minecraft:charcoal",Count:16b}]}

# --- the room itself: benches, a counter, light ----------------------------
setblock ~3 ~0 ~-2 handcrafted:oak_table
setblock ~3 ~0 ~-1 handcrafted:oak_chair
setblock ~3 ~0 ~2 handcrafted:oak_counter
setblock ~3 ~0 ~3 minecraft:barrel[facing=up]
setblock ~-2 ~3 ~-2 minecraft:lantern[hanging=true]
setblock ~2 ~3 ~-2 minecraft:lantern[hanging=true]
setblock ~-2 ~3 ~2 minecraft:lantern[hanging=true]
setblock ~2 ~3 ~2 minecraft:lantern[hanging=true]

# --- two lanterns either side of the door, and the sign over it ------------
setblock ~-2 ~0 ~-5 minecraft:oak_fence
setblock ~-2 ~1 ~-5 minecraft:lantern[hanging=false]
setblock ~2 ~0 ~-5 minecraft:oak_fence
setblock ~2 ~1 ~-5 minecraft:lantern[hanging=false]
setblock ~0 ~2 ~-5 minecraft:oak_wall_sign[facing=north]{front_text:{messages:['{"text":"THE INN"}','{"text":""}','{"text":"kept by"}','{"text":"M. Ashcombe"}'],color:"gray"}}

playsound minecraft:block.wood.place master @a[distance=..96] ~ ~ ~ 1 0.8
