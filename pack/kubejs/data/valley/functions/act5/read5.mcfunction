# valley:act5/read5
# The last line, then the world opens.
tellraw @a [{"text":"Halden: ","color":"green"},{"text":"\"If there is more than one set of footprints on my cellar stairs, then I was right to wait, and go and turn it on.\"","color":"white","italic":true}]
playsound minecraft:item.book.put master @a ~ ~ ~ 1 1
worldborder set 59999968
execute in minecraft:the_nether run worldborder set 59999968
tellraw @a {"text":"The valley's fine now. Go see what's past the ridge - and come home for supper.","color":"gold","italic":true}
