# valley:act3/turn
# The Harvest Supper's turn, six seconds after the Supper (§7, §12.5).
# Invoked positioned at the Town Anchor.
#
# Two corrections from the story document are already applied here, and match
# valley_finales.js line for line — do not revert either:
#   * `sereneseasons setseason X` -> `season set X`  (SereneSeasons 9.1.0.3
#     registers the root literal `season`, then `set`, then a SubSeason arg)
#   * `/weather snow` does not exist; winter + `/weather rain` renders as snow
#
# valley_finales.js finaleAct3 runs this same chain through global.valley.delay
# rather than /schedule, because the delay queue is what the pack ships. This
# file is the datapack-side equivalent, kept in step so `/schedule function
# valley:act3/turn 6s` and the KubeJS path do exactly the same thing.

season set early_winter
weather rain
playsound minecraft:block.snow.place master @a ~ ~ ~ 1 0.6
tellraw @a [{"text":"Oda: ","color":"yellow"},{"text":"\"That's the last warm night. Let's not lose anybody this year.\"","color":"white","italic":true}]
worldborder set 10000 10
execute in minecraft:the_nether run worldborder set 1250 10
particle minecraft:snowflake ~ ~4 ~ 12 4 12 0.01 400 force @a
