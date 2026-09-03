# valley:act1/nesting_box
# Q10 reward — "Fence the Pen and Open the Three Hen Crates."
# Invoked positioned at the player, inside the finished pen behind the house.
# The quest text promises: a nesting box with two eggs already in it, and a
# Megatorch over the coop (the Megatorch itself is an item reward, so the
# player places that one; this puts the box and the light down).
#
# farm_and_charm:chicken_nest is a real block in this pack's registry — it is
# the nesting box, so no chest-and-sign fallback is needed.

# --- a dry corner for the coop ---------------------------------------------
fill ~-2 ~0 ~-2 ~2 ~0 ~2 minecraft:oak_planks replace minecraft:grass_block
fill ~-2 ~1 ~-2 ~2 ~3 ~2 minecraft:air replace minecraft:grass
fill ~-2 ~1 ~-2 ~2 ~3 ~2 minecraft:air replace minecraft:tall_grass

# --- the nesting box, on a straw bed ---------------------------------------
setblock ~1 ~0 ~1 minecraft:hay_block
setblock ~1 ~1 ~1 farm_and_charm:chicken_nest
setblock ~0 ~1 ~1 farm_and_charm:chicken_nest

# --- the feeding trough side of the coop -----------------------------------
setblock ~-1 ~1 ~1 minecraft:hay_block
setblock ~-1 ~2 ~1 minecraft:oak_slab[type=bottom]

# --- a post for the Megatorch, and a lamp so the pen is never dark ---------
setblock ~2 ~1 ~-2 minecraft:oak_fence
setblock ~2 ~2 ~-2 minecraft:lantern[hanging=false]
setblock ~-2 ~1 ~-2 minecraft:oak_fence
setblock ~-2 ~2 ~-2 minecraft:lantern[hanging=false]

# --- a sign, because Pip labelled it ---------------------------------------
setblock ~2 ~1 ~1 minecraft:oak_sign[rotation=8]{front_text:{messages:['{"text":"NESTING BOX"}','{"text":"2 hens"}','{"text":"1 rooster"}','{"text":"- Pip"}']}}

tellraw @a[distance=..64] [{"text":"Marnie: ","color":"gold"},{"text":"\"Two hens and a rooster. Don't name the rooster - you'll get attached, and he is horrible.\"","color":"white","italic":true}]
playsound minecraft:entity.chicken.egg master @a[distance=..64] ~ ~ ~ 1 1
