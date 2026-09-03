# valley:act1/marnie_arrives
# Q8 reward — "Sleep One Night in Your Bed." Marnie sees the chimney.
# Invoked positioned at the player, i.e. at the cottage. She arrives AT YOUR
# DOOR, which is the beat the quest text describes; the Act I finale re-imports
# her at the anchor for the Fair. Both are the same NPC — every preset carries
# a deterministic UUID, so `preset import data` updates in place (docs/NPCS.md).

# --- a spot to stand on, just outside the south door -----------------------
# COBBLESTONE, not dirt_path. Q9 sends the player to "the 3x9 patch behind the
# house - every tile is marked in path blocks", and cottage.mcfunction now
# marks exactly 27 dirt_path tiles north of the house. A 5x3 dirt_path pad
# south of the DOOR was the first path-block rectangle anyone would find, on
# the wrong side of the house and 15 tiles instead of 27. There is now exactly
# one patch of path blocks on this farm and it is the one Q9 means.
fill ~-2 ~0 ~6 ~2 ~0 ~8 minecraft:cobblestone
setblock ~-2 ~1 ~7 minecraft:oak_fence
setblock ~-2 ~2 ~7 createdeco:yellow_copper_lamp[facing=up,inverted=true,lit=true]

# --- Marnie herself --------------------------------------------------------
easy_npc preset import data valley:easy_npc/preset/marnie.npc.snbt ~0 ~1 ~7

# --- the bread she is not carrying home ------------------------------------
setblock ~1 ~1 ~7 minecraft:barrel[facing=up]
setblock ~-1 ~1 ~7 handcrafted:oak_table

tellraw @a[distance=..64] [{"text":"Marnie: ","color":"gold"},{"text":"\"Four years I've looked at that chimney, and last night there was smoke. I've brought bread and I am not carrying it home.\"","color":"white","italic":true}]
playsound minecraft:entity.villager.yes master @a[distance=..64] ~ ~ ~ 1 1
