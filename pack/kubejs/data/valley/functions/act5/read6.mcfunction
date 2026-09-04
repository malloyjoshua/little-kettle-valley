# valley:act5/read6
# The P.S., then the world opens.
tellraw @a [{"text":"Halden: ","color":"green"},{"text":"There's a lamp post on my porch with nothing on it. I'd like to be on the line.","color":"white","italic":true}]
playsound minecraft:item.book.put master @a ~ ~ ~ 1 1
worldborder set 59999968
execute in minecraft:the_nether run worldborder set 59999968
tellraw @a {"text":"The valley's fine now. Go see what's past the ridge — and come home for supper.","color":"gold","italic":true}
