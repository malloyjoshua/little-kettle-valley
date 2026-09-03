# valley:act1/nesting_box
# Q10 reward — "Fence the Pen and Open the Three Hen Crates."
#
# Invoked by `/valley scene coop`, positioned at the CENTRE GROUND BLOCK of the
# pen: home + [4, -1, -9]. That is the middle of the 7x7 outline
# cottage.mcfunction marks out at home + [1..7, -1, -12..-6], so this 5x5 lands
# exactly on the pen's interior and nowhere else.
#
# It used to run from the quest reward at `{x} {y} {z}` — the CLAIMING PLAYER'S
# FEET. Claim the card from the doorway, from the mill, or from the bottom of
# the cellar and Marnie's nesting box, her straw and her two lamps were built
# there instead of in the pen, in an empty field or inside a wall. It also read
# ~0 as the ground in some lines and as the standing level in others, so the
# hay and the box floated a block above the floor.
#
# Convention, the same as cottage.mcfunction and place_ruin: the ground is at
# ~0 and everything stands at ~1.
#
# farm_and_charm:chicken_nest is a real block in this pack's registry — it is
# the nesting box, so no chest-and-sign fallback is needed.

# --- a dry floor for the coop, inside the finished fence -------------------
fill ~-2 ~1 ~-2 ~2 ~4 ~2 minecraft:air
fill ~-2 ~0 ~-2 ~2 ~0 ~2 minecraft:grass_block
fill ~-1 ~0 ~-1 ~1 ~0 ~1 minecraft:oak_planks

# --- the nesting box, on a straw bed ---------------------------------------
setblock ~1 ~0 ~1 minecraft:hay_block
setblock ~1 ~1 ~1 farm_and_charm:chicken_nest
setblock ~0 ~1 ~1 farm_and_charm:chicken_nest

# --- the feeding trough side of the coop -----------------------------------
setblock ~-1 ~1 ~1 minecraft:hay_block
setblock ~-1 ~2 ~1 minecraft:oak_slab[type=bottom]

# --- two eggs already in it, so the box is not an empty promise ------------
summon minecraft:item ~0 ~2 ~1 {Item:{id:"minecraft:egg",Count:2b},PickupDelay:20}

# --- a post for the Megatorch, and a lamp so the pen is never dark ---------
setblock ~2 ~1 ~-2 minecraft:oak_fence
setblock ~2 ~2 ~-2 minecraft:lantern[hanging=false]
setblock ~-2 ~1 ~-2 minecraft:oak_fence
setblock ~-2 ~2 ~-2 minecraft:lantern[hanging=false]

# --- a sign, because Pip labelled it ---------------------------------------
setblock ~2 ~1 ~1 minecraft:oak_sign[rotation=8]{front_text:{messages:['{"text":"NESTING BOX"}','{"text":"2 hens"}','{"text":"1 rooster"}','{"text":"- Pip"}']}}

tellraw @a[distance=..64] [{"text":"Marnie: ","color":"gold"},{"text":"\"Two hens and a rooster. Don't name the rooster - you'll get attached, and he is horrible.\"","color":"white","italic":true}]
playsound minecraft:entity.chicken.egg master @a[distance=..64] ~ ~ ~ 1 1
