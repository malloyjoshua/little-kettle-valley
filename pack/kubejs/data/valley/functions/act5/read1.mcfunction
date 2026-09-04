# valley:act5/read1
# Founder's Day - Halden reads the last page of Josie's journal aloud.
# Six tellraw lines, each scheduling the next five seconds later (§12.5).
# The words are Entry 5 (journal/entry_5_the_last_page.json), and the last of
# them is the P.S.: the fortieth lamp post is on Josie's own porch, and this is
# where the town hears her ask for it.
#
# These six lines are the SAME six, in the same order, as the `page` array in
# valley_finales.js finaleAct5, which paces them through global.valley.delay().
# Only ONE of the two should ever run - the shipped finale uses the delay
# queue, so this chain is the datapack-side equivalent for a manual
# `/function valley:act5/read1`. If you edit one, edit the other.

tellraw @a [{"text":"Halden: ","color":"green"},{"text":"Last one. The writing's gone shaky, so I'll be brief, which Marnie will tell you is a first.","color":"white","italic":true}]
playsound minecraft:item.book.page_turn master @a ~ ~ ~ 1 0.9
schedule function valley:act5/read2 5s
