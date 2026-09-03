# valley:act5/read1
# Founder's Day — Halden reads the last page of Josie's journal aloud.
# Five tellraw lines, each scheduling the next five seconds later (§12.5).
# The words are the cellar wall from §7, which is what Halden is reading:
# the reveal, said out loud, in front of the whole town.
#
# valley_finales.js finaleAct5 paces the same five lines through
# global.valley.delay(). Only ONE of the two should ever run — the shipped
# finale uses the delay queue, so this chain is the datapack-side equivalent
# for a manual `/function valley:act5/read1`.

tellraw @a [{"text":"Halden: ","color":"green"},{"text":"\"The Works ran. For eleven days, in the winter Old Dell left.\"","color":"white","italic":true}]
playsound minecraft:item.book.page_turn master @a ~ ~ ~ 1 0.9
schedule function valley:act5/read2 5s
