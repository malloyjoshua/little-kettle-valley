# valley:act4/lever
# The Longest Night, four seconds after the gathering (§12.5).
# Invoked positioned at the Works.
#
# Bram pulls the lever, which means: the lever is setblock and Bram's line is
# tellraw. NPCs cannot interact with blocks; he is narration, and it reads
# perfectly (§7 rule 5).
#
# The one thing this file CANNOT do is the lamp sweep — lighting all 39 posts
# needs persistentData.lamps[], which is KubeJS state. valley_finales.js
# finaleAct4 owns that loop and calls the rest of this chain inline. This file
# is the datapack-side equivalent for the parts that are pure commands.

setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=true]
particle minecraft:cloud ~2 ~3 ~2 1 1 1 0.02 60 force @a
playsound minecraft:block.beacon.activate master @a ~ ~ ~ 3 0.7
playsound minecraft:block.conduit.activate master @a ~ ~ ~ 2 1
tellraw @a [{"text":"Bram: ","color":"dark_aqua"},{"text":"\"Well.\"","color":"white","italic":true}]
