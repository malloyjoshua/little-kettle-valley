# valley:act1/square_path
# Q7 reward — "Place the Surveyor's Stake North of Your Gate."
# The stake IS the Town Anchor, so this function is invoked positioned at the
# anchor. The path runs south (+z), back down the road toward the homestead.
#
# The two lamp posts below sit on valley_core's LAMPS_Q07 offsets, which the
# Q7 anchor listener pushes into persistentData.lamps[] — that is what makes
# the Act IV lever light these two along with the other thirty-eight.

# --- level a small pad around the stake ------------------------------------
fill ~-3 ~1 ~-3 ~3 ~4 ~3 minecraft:air
fill ~-3 ~0 ~-3 ~3 ~0 ~3 minecraft:stone_bricks
setblock ~0 ~0 ~0 minecraft:polished_andesite

# --- the road: three wide, twenty-four long, running south -----------------
fill ~-1 ~1 ~1 ~1 ~4 ~24 minecraft:air
fill ~-1 ~0 ~1 ~1 ~0 ~24 minecraft:stone_bricks
fill ~0 ~0 ~1 ~0 ~0 ~24 minecraft:polished_andesite
fill ~-2 ~0 ~4 ~-2 ~0 ~20 minecraft:cobblestone
fill ~2 ~0 ~4 ~2 ~0 ~20 minecraft:cobblestone

# --- the first two lamp posts. 2 of 40. ------------------------------------
setblock ~-2 ~1 ~8 candlelight:lamp
setblock ~2 ~1 ~16 candlelight:lamp

# --- a marker at the head of the road --------------------------------------
setblock ~-2 ~1 ~2 minecraft:oak_fence
setblock ~2 ~1 ~2 minecraft:oak_fence
setblock ~-2 ~2 ~2 minecraft:lantern[hanging=false]
setblock ~2 ~2 ~2 minecraft:lantern[hanging=false]

tellraw @a[distance=..64] [{"text":"Josie: ","color":"gray"},{"text":"\"Bram surveyed that flat twice and never drove the stake. You drove it. That is the whole difference.\"","color":"white","italic":true}]
playsound minecraft:block.stone.place master @a[distance=..64] ~ ~ ~ 1 0.8
