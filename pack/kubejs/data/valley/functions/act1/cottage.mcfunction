# valley:act1/cottage
# Q2 reward — "Put the Waystone on the Hearthstone."
# Invoked as: execute positioned <player x> <player y> <player z> run function valley:act1/cottage
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

# --- foundation and floor ---------------------------------------------------
fill ~-5 ~-2 ~-5 ~5 ~-2 ~5 minecraft:cobblestone
fill ~-4 ~-1 ~-4 ~4 ~-1 ~4 minecraft:oak_planks

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

tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\"Four walls and a door. That is a house. What you do next makes it a home.\"","color":"white","italic":true}]
playsound minecraft:block.wood.place master @a[distance=..64] ~ ~ ~ 1 0.9
