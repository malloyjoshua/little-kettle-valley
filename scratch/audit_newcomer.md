# Quest Book Audit — lens: NEWCOMER

**Persona:** Stardew Valley player. Never played Minecraft. MacBook Air, trackpad, no mouse.
Wants a clear path. Quits when confused. Reads the first two lines of anything and skims the rest.

**Route walked:** Read Me First → Start Here → Act I → Farm & Seasons → Cooking & Brewing →
Animals & Fishing → Home & Town.

**Method:** every quest gets a timeline line `key | est minutes | what she is doing`, then findings
appended as I go. Estimates assume a total beginner: no Minecraft muscle memory, trackpad-only,
re-reads the description twice, opens JEI to find recipes.

---
## 1. Read Me First (`story/quests/readme.json`) — 11 quests

### Timeline
```
rm_book       | 1 min  | Reads "chapters are the tabs", clicks the tick.
readme_hands  | 1 min  | Reads left/right-click + 2x2 vs 3x3. Gets a crafting table.
readme_night  | 1 min  | Reads eat/sleep/F3. Tries F3, Mission Control opens instead.
rm_next       | 1 min  | Learns the toast tells her where to go next.
rm_folk       | 1 min  | Learns the eight names. None of them mean anything yet.
rm_lanes      | 1 min  | Learns there are two lanes; told to start in Farm and Seasons.
rm_oda        | 1 min  | Learns Scrip buys the annoying parts.
rm_journal    | 1 min  | Learns the journal and the compass exist.
rm_order      | 1 min  | Learns order barely matters.
rm_notimer    | 1 min  | Learns nothing is timed. This is the line she needed most.
rm_world      | 1 min  | Learns it's one shared valley.
```
**Chapter total: ~11 min.** No felt win — eleven ticks and some XP. That is correct for a
"read me" tab, but see FIND-N04: nothing tells her the ticks are hers to click.

### Findings

**[BLOCKER] `readme_night` — `readme.json` — F3 does not exist on a MacBook Air; pressing it opens Mission Control and the newcomer concludes the book lied to her on page 3.**
On Apple laptops the top row defaults to media keys; the debug screen needs `fn`+`F3`. This is
the first instruction in the book she can physically fail, and it is the instruction that teaches
her how to find her way back — so it fails at the exact moment she is most fragile.
- field: `description`
- old: `["Eat when the drumsticks drop. Sleep in a bed to skip a night.", "", "Press &bF3&r for the XYZ line and write the three numbers down.", "", "The &aMegatorch&r you place at home keeps &cmonsters&r off it for good."]`
- new: `["Eat when the drumsticks drop. Sleep in a bed to skip a night.", "", "Press &bF3&r for the XYZ line and write the three numbers down. On a Mac laptop that is &bfn&r + &bF3&r.", "", "The &aMegatorch&r you place at home keeps &cmonsters&r off it for good."]`
- (same one-clause fix belongs on `tips_f3` in `tips.json` — logged again there)

**[MAJOR] `readme_hands` — `readme.json` — the quest titled "Move, Break, Place, Craft" never says how to move or how to look, and right-click is a two-finger tap she has never been told about.**
A Stardew player moves with arrows or click-to-move and has no mouselook at all. WASD + "the
trackpad turns your head" is the single largest unstated assumption in the book, and this is the
only quest that could carry it. Right-click on a trackpad is a two-finger tap or Ctrl-click.
- field: `description`
- old: `["&bLeft-click&r held breaks a block. &bRight-click&r places what you hold.", "", "Your pack has a 2x2 grid; a &aCrafting Table&r makes it 3x3. Click an item in the search list to see its recipe."]`
- new: `["&bW A S D&r walk. The trackpad turns your head. &bE&r opens your bag.", "", "&bLeft-click&r held breaks a block. &bRight-click&r places what you hold — on a Mac trackpad that is a &btwo-finger tap&r.", "", "Your pack has a 2x2 grid; a &aCrafting Table&r makes it 3x3. Click an item in the search list to see its recipe."]`

**[MAJOR] `rm_lanes` — `readme.json` — sends her to Farm and Seasons on page 6, one page after `rm_book` sent her to Start Here; the one player who most needs a single path is handed two.**
"Wants a clear path, quits when confused" is exactly the player who reads two different
"start here" instructions and stops to work out which one is wrong.
- field: `description`
- old: `["Most of the book is the cozy lane: food, animals, planting, decorating. Start in the &6Farm and Seasons&r chapter.", "", "Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."]`
- new: `["Most of the book is the cozy lane: food, animals, planting, decorating. After &6Start Here&r, the &6Farm and Seasons&r chapter is the one to open.", "", "Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."]`

**[MAJOR] `rm_book` — `readme.json` — never says that the tick is hers to click, so the eleven checkmark quests in this chapter can read as broken.**
Every quest in Read Me First completes on a `checkmark` task. FTB Quests requires her to open
the quest and click the task box. Nothing in the book says so, and this is the first chapter,
where a newcomer decides whether the book works.
- field: `description`
- old: `["Chapters are the &btabs&r down the left edge. This one is the top one.", "", "A quest you cannot start yet stays on the board, greyed, with its title readable.", "", "The story starts one tab down, in &6Start Here&r."]`
- new: `["Chapters are the &btabs&r down the left edge. This one is the top one.", "", "Click a quest to open it. Where a quest ends in a &bbox to tick&r, that box is yours to click when you have done the thing.", "", "A quest you cannot start yet stays on the board, greyed, with its title readable.", "", "The story starts one tab down, in &6Start Here&r."]`

**[MINOR] `rm_book` — `readme.json` — chapter subtitle says "Eleven short pages" and is the only line telling her how long this tab is, but nothing tells her she can leave.**
She will read all eleven before starting, which is ~11 minutes of no play at the front of the
game. One clause turns that into a choice.
- field: chapter `subtitle` (in `readme.json` chapter block)
- old: `["Eleven short pages about the book itself.", "Nothing here locks, and nothing here can be missed."]`
- new: `["Eleven short pages about the book itself. Read the first, skip the rest if you like.", "Nothing here locks, and nothing here can be missed."]`

**[MINOR] `rm_folk` — `readme.json` — eight names with no roles, delivered before she has met anyone, is a list to forget.**
`rm_oda`, `rm_journal` and Act I all lean on knowing who Bram and Marnie are. One noun each
costs nothing and makes the names stick.
- field: `description`
- old: `["Marnie, Bram, Oda, Halden, Tobin, Wisp, Pip and Nella live here. Seven more arrive.", "", "Right-click any of them; what they say changes as the valley moves. The &bbar at the top&r counts them."]`
- new: `["Marnie the innkeeper, Bram the miller, Oda the shopkeeper, Halden the gardener, Tobin the prospector, Wisp of the reeds, Pip the courier and Nella the fisher. Seven more arrive.", "", "Right-click any of them; what they say changes as the valley moves. The &bbar at the top&r counts them."]`

---
## 2. Start Here (`story/quests/start.json`) — q01–q08

### Timeline
```
q01 | 4 min  | Two-finger-taps the letter, pages through 4 screens, then eleven reward
              items land at once and she spends a minute working out what a backpack is.
q02 | 8 min  | Learns WASD + mouselook while walking ~85 blocks south on a trackpad.
              Finds the gate, finds the grey hearthstone, places waystone, types "Home".
q03 | 6 min  | Aims at four holes in a wall with a trackpad. Slow but satisfying — the
              first time the world visibly becomes hers.
q04 | 2 min  | Puts down one tall torch. Easiest quest in the book.
q05 | 7 min  | Digs 40 gravel down a 2-wide shaft. Gravel falls on her; she does not know
              why. Torches the cellar, reads the chalk. Title card. Big moment.
q06 | 20 min | THE WALL. Needs a bowl. Needs a crafting table. Needs planks. Needs a tree.
              Has no axe. Nothing in the text mentions any of it. (~8 min once fixed.)
q07 | 6 min  | Walks ~76 blocks north to the square, finds the socket, drives the stake.
              Title card, two lamps light. Clear win.
q08 | 12 min | Sleeps. If she arrives at the bed in daylight the game refuses and she has
              no instruction at all. Then three scenes fire and the valley opens.
```
**Chapter total: ~65 min as written, ~50 min with FIND-N07 fixed.**

### Findings

**[BLOCKER] `q06` — `start.json` — Vegetable Soup needs a Bowl, a Bowl needs a 3x3 grid, and Start Here has given her no crafting table, no planks, and no axe.**
Farmer's Delight cooking uses a bowl as the container (`farmersdelight/cooking/vegetable_soup.json`
declares none, so it defaults to `minecraft:bowl`); `minecraft/bowl.json` is a 3-wide shaped
recipe, so her 2x2 inventory grid cannot make one. The only crafting table in the book is the
reward on `readme_hands`, an **optional gear quest in a different chapter**. q03's toast routes her
q03 → q04 → q06 and skips q05, so she does not even have the iron axe when she gets here. A
Minecraft player punches a tree without thinking; this player stares at "Three planks make four
bowls" with no planks, no table and no idea trees are a resource. This is the quest where she quits.
- field: `q03.rewards` (append two entries)
- old: `[cooking_pot, campfire, cabbage x4, carrot x4, potato x4, beetroot x4, xp_levels 1, toast]`
- new: same list plus `{"type": "item", "item": "minecraft:crafting_table"}` and `{"type": "item", "item": "minecraft:bowl", "count": 4}` inserted after the campfire entry
- and field: `q06.description`
- old: `["Josie: \"Kettle on the hook, soup in the pot. That is the entire ceremony.\"", "", "Set the &acampfire&r down outside your door, hang the &aCopper Kettle&r over it, and cook one &aVegetable Soup&r in the Cooking Pot: cabbage, carrot, potato, beetroot and a bowl. Three planks make four bowls.", "", "Bram's Surveyor's Stake is in the vegetable basket, in a rag with a chalk K on it. Ovens and kettles: &6Cooking and Brewing&r."]`
- new: `["Josie: \"Kettle on the hook, soup in the pot. That is the entire ceremony.\"", "", "Set the &acampfire&r down outside your door and stand the &aCooking Pot&r on top of it — the fire under it is what cooks.", "", "Drop cabbage, carrot, potato and beetroot in, with a &abowl&r in the slot on the right. Four bowls and a &aCrafting Table&r came with the pot.", "", "Bram's Surveyor's Stake is in the vegetable basket, in a rag with a chalk K on it. Ovens and kettles: &6Cooking and Brewing&r."]`

**[MAJOR] `q08` — `start.json` — "Sleep one night" with no word about what to do when it is noon; the game refuses her and the book has no answer.**
She arrives at the bed whenever she arrives. Minecraft answers "You can only sleep at night",
which reads as the quest being broken. This is the last quest of the tutorial chapter and the one
that fires three scenes, so it is the worst possible place for a dead stop.
- field: `description`
- old: `["Marnie: \"Four years I've looked at that chimney, and last night there was smoke. I've brought bread and I am not carrying it home.\"", "", "Sleep one night in the &aRed Bed&r in your cottage.", "", "Marnie opens the inn she has kept with no guests in it, Bram opens the mill, and she leaves you her seed sack, 32 &aGreen Oak Planks&r and a flint and steel."]`
- new: `["Marnie: \"Four years I've looked at that chimney, and last night there was smoke. I've brought bread and I am not carrying it home.\"", "", "Sleep one night in the &aRed Bed&r in your cottage. Beds only work after dusk — if the sun is up, go and dig the cellar stairs and come back.", "", "Marnie opens the inn she has kept with no guests in it, Bram opens the mill, and she leaves you her seed sack, 32 &aGreen Oak Planks&r and a flint and steel."]`

**[MAJOR] `q05` — `start.json` — forty blocks of gravel dug downward will bury her, and the text treats it as a shovelling job.**
Gravel falls. In a 2-wide shaft a newcomer digs the block under her own feet, rides the column
down and takes suffocation damage in the dark with no idea what happened. She has never seen a
falling block. One sentence removes the whole failure.
- field: `description`
- old: `["Josie: \"There's a door down there I'm not going to explain yet. Dig anyway; I know you.\"", "", "Dig out the two-wide patch of &agravel&r in the kitchen floor — forty marked blocks — down to the stone stair she cut herself. The &airon shovel&r is in your bag.", "", "At the bottom: a sealed iron door with no handle, four words in her chalk — Not yet. — J.K. — and a plinth for the &aCellar Waystone&r."]`
- new: `["Josie: \"There's a door down there I'm not going to explain yet. Dig anyway; I know you.\"", "", "Dig out the two-wide patch of &agravel&r in the kitchen floor — forty marked blocks — down to the stone stair she cut herself. The &airon shovel&r is in your bag.", "", "&cGravel falls.&r Stand on solid floor and dig the block in front of you, never the one under your feet. Put a torch down when it gets dark.", "", "At the bottom: a sealed iron door with no handle, four words in her chalk — Not yet. — J.K. — and a plinth for the &aCellar Waystone&r."]`

**[MAJOR] `q02` — `start.json` — the walk to the farm is the longest unguided stretch in the game and the quest text gives her a coordinate she cannot read.**
`-319 74 32` is only useful with the F3 screen, which on her laptop needs `fn`. The world does
solve this — first join turns her to face the road and hands her a Kettle Farm Compass — but the
quest text never mentions the compass, so any player who dies, relogs, or wanders off has only
the number. Name the compass and the number becomes a backup instead of the whole plan.
- field: `description`
- old: `["Josie: \"The hearthstone is the one thing in that house I never had to fix. Start from the part that held.\"", "", "Follow the road to the old farm (&b-319 74 32&r): signposted gate, standing chimney, no door on the house. Put the &aHomestead Waystone&r on the flat grey hearthstone, type Home, click the tick.", "", "Nothing is rebuilt and nothing is moved. It is your house from that moment. Scrolls and maps: &6Getting Around&r."]`
- new: `["Josie: \"The hearthstone is the one thing in that house I never had to fix. Start from the part that held.\"", "", "Hold the &aKettle Farm Compass&r and walk the way its needle points. The road is signposted and ends at her gate (&b-319 74 32&r): standing chimney, no door on the house.", "", "Put the &aHomestead Waystone&r on the flat grey hearthstone in the kitchen floor, type Home, click the tick.", "", "Nothing is rebuilt and nothing is moved. It is your house from that moment. Scrolls and maps: &6Getting Around&r."]`

**[MINOR] `q01` — `start.json` — eleven reward items arrive in one burst on the first quest of the game, and the description does not tell her a single one of them is coming.**
Backpack, kettle, waystone, shovel, pickaxe, megatorch, 16 beef, 16 torches, journal. She cannot
tell which are tools, which are quest items, and which are food. One line naming the three that
matter turns a dump into a kit.
- field: `description`
- old line 5: `"Forty lamp posts stand along that road and not one is lit. New here? Read the &6Read Me First&r chapter."`
- new (append one line after it): `"Her kit comes with the letter: a &abackpack&r, a &ashovel&r and &apick&r, food, torches, and the &aJournal&r you can right-click any time."`

**[MINOR] `q05` — `start.json` — she is given a second Waystone and shown a plinth, and never told to put one on the other.**
The description ends on "a plinth for the &aCellar Waystone&r" and the rewards hand her a
`waystones:waystone`, but nothing joins them up. She either works it out or leaves a waystone in
her bag for four acts.
- field: `description` (final line, on top of the FIND-N09 rewrite)
- old: `"At the bottom: a sealed iron door with no handle, four words in her chalk — Not yet. — J.K. — and a plinth for the &aCellar Waystone&r."`
- new: `"At the bottom: a sealed iron door with no handle and four words in her chalk — Not yet. — J.K. Stand the spare &aWaystone&r on the empty plinth beside it and you can hop home from anywhere."`

**[MINOR] `q06` — `start.json` — the Copper Kettle instruction has no tick against it and sends her hunting for a mechanic that is not part of the quest.**
The tasks are the Cooking Pot and the soup. "Hang the Copper Kettle over it" is scenery, but she
reads it as step one and spends five minutes trying to hang a kettle on a campfire. Covered by
the FIND-N07 rewrite, which drops the kettle from the instruction and leaves it to
&6Cooking and Brewing&r.

### Cadence verdict for the first hour
Good, with one hole. q02 (title card "Home"), q05 (title card "Josie's Cellar"), q07 (title card
plus lamps 2/40) and q08 (three scenes, first neighbour) land a real felt win roughly every 8–10
minutes. **q06 is the hole**: it is the longest quest in the chapter, it is the one that can stop
her dead, and it is the only one with no title card, no scene and no bossbar move — its payoff is
deferred to q07. Fixing FIND-N07 shortens it enough that the deferral stops mattering.

---
## 3. Act I: The Thaw (`story/quests/act1.json`) — q09–q19

### Timeline
```
q09  | 12 min | Tills 27 marked tiles. Needs a hoe the quest never names and she may not
                own. Plants 27 crops, then discovers the hand-in wants 9 seeds she just
                buried.
q10  |  8 min | Places 23 fences and a gate on a trackpad, opens three crates. Chickens.
q11  |  1 min | Instant — q10's reward already put three eggs in her bag. Duckling appears.
q12  |  8 min | Walks "west to the mill" with no coordinate. Finds Bram eventually.
q13a |  3 min | Ticks a box; hammer and prospector's pick arrive.
q13b | 14 min | Walks west, finds hematite on the grass, digs STRAIGHT DOWN 15 blocks,
                mines 8 clusters in the dark, climbs back out.
q13  |  6 min | Makes iron nuggets, crafts 8 andesite alloy in a 2x2 checker.
q14  | 25 min | THE SECOND WALL. Millstone needs an Andesite Casing, which is not a
                crafting recipe at all — it is right-clicking a placed stripped log with an
                alloy. Then ~2 min of holding a two-finger tap to crank 16 flour.
q15  | 12 min | Crafts a furnace she was never given, then watches it for 5 min 20 s.
q16  | 10 min | Crafts 2 water wheels, sets them in the race. Tries to belt the millstone.
q17  | 20 min | Chops ~32 oak logs, powers the saw, cuts 128 planks. Long, but honest work.
q18  | 18 min | Three kitchen blocks, bread, soup, and a pumpkin pie whose sugar has no
                source anywhere in the act. Marked OPTIONAL but gates the finale.
q19  |  6 min | Sweeps cobwebs, hands over flour and bread. Fair, fireworks, Act II opens.
```
**Chapter total: ~2 h 23 m as written, ~1 h 45 m with the fixes below.**

### Findings

**[BLOCKER] `q14` — `act1.json` — the Millstone needs an Andesite Casing, and Andesite Casing has no crafting-grid recipe at all; it is a Create "item application" and nothing in the story says so.**
`create/item_application/andesite_casing_from_log.json`: the only way to get one is to strip a
log with an axe, place the stripped log in the world, and right-click it holding an Andesite
Alloy. JEI shows this as a category a Stardew player cannot read. She has eight alloys, eight
cogwheels, a pickaxe, and no possible way to work out the missing step. Act I stops here.
(The same wording problem is in `create.json` → `create_casing`, whose title says "Craft".)
- field: `description`
- old: `["Bram: \"Hand crank first. You should know exactly what the water is doing for you before it starts doing it.\"", "", "Build a &aMillstone&r, put a &aHand Crank&r on top of it, and grind &a16 Wheat Flour&r for Marnie. Bram's 32 wheat covers this and Oda's order at the end of the act.", "", "The reward is the whole parts list for the Mechanical Saw, two quests from here."]`
- new: `["Bram: \"Hand crank first. You should know exactly what the water is doing for you before it starts doing it.\"", "", "A Millstone is a cogwheel, a stone block and an &aAndesite Casing&r. Casing is not made in a grid: strip a log with your axe, put the stripped log down, and &bright-click it holding an Andesite Alloy&r.", "", "Put a &aHand Crank&r on top of the Millstone and hold right-click to turn it. Grind &a16 Wheat Flour&r for Marnie; Bram's 32 wheat covers this and Oda's order at the end of the act.", "", "The reward is the whole parts list for the Mechanical Saw, two quests from here."]`
- and field: `q13.rewards` — insert `{"type": "item", "item": "create:andesite_casing", "count": 2}` before the cogwheel entry, so a player who still cannot follow the trick is not stopped by it

**[BLOCKER] `q09` — `act1.json` — she is told to plant nine wheat seeds and to hand in holding nine wheat seeds, and Marnie's sack contains exactly nine.**
q08 gives `wheat_seeds` 9, `carrot` 9, `potato` 9 — exactly the 27 the patch takes and not one
spare. Read literally, the quest is impossible; in practice she must tick the item task before
planting the last bed, which nothing tells her. A newcomer plants all 27, sees `0/9 Wheat Seeds`,
and has no idea that grass and grown wheat are seed sources.
- field: `q08.rewards` — change the wheat seed entry
- old: `{"type": "item", "item": "minecraft:wheat_seeds", "count": 9}`
- new: `{"type": "item", "item": "minecraft:wheat_seeds", "count": 18}`
- and field: `q09.description`
- old: `"Till the 3x9 patch behind the house — every tile is marked in path blocks — then plant the &a9 carrots&r, &a9 potatoes&r and &a9 wheat seeds&r from Marnie's sack. Hand in holding the seeds; the book counts them and never takes them."`
- new: `"Take the &ahoe&r from your bag and right-click each of the 27 marked tiles behind the house, then plant &a9 carrots&r, &a9 potatoes&r and &a9 wheat seeds&r. Marnie packed a spare nine seeds for the hand-in; the book counts them and never takes them."`

**[BLOCKER] `q18` — `act1.json` — flagged `optional: true`, but `q19`, the Act I finale, depends on it; a player who trusts the word "optional" locks herself out of the act ending with no explanation on screen.**
This is the worst instance of a pattern that runs through the whole book — eleven quests are
marked optional while a required quest depends on them (see the systemic finding at the end).
For the newcomer it is fatal here, because q18 is also the quest that hands her Oda's Broom,
without which q19's first task cannot be done.
- field: `optional`
- old: `true`
- new: `false`
- and field: `shape` / `size` (to match the rest of the required chain)
- old: `"rsquare"` / `1.0`
- new: `"square"` / `1.0`

**[MAJOR] `q15` — `act1.json` — "in any furnace" assumes she has a furnace; nothing in the game has given her one or mentioned that they exist, and this quest gates both water wheels.**
No `minecraft:furnace` appears in any reward in `start.json` or `act1.json`. She has an iron
pickaxe, so eight cobblestone is reachable — but only if she knows a furnace is a thing you build.
- field: `description`
- old: `["Marnie: \"Green planks want heat and time. Josie dried every board in this valley in a furnace and was insufferable about it.\"", "", "Smelt the 32 &aGreen Oak Planks&r in any furnace — ten seconds a plank — and hold 32 &aSeasoned Oak Boards&r. Marnie's charcoal is in the barrel by the door.", "", "Bram cannot build a Water Wheel until these dry, and the furnace is you. The kitchen kit comes with them: see &6Cooking and Brewing&r."]`
- new: `["Marnie: \"Green planks want heat and time. Josie dried every board in this valley in a furnace and was insufferable about it.\"", "", "Eight cobblestone in a ring makes a &aFurnace&r. Marnie's charcoal is in the barrel by the door.", "", "Smelt the 32 &aGreen Oak Planks&r into 32 &aSeasoned Oak Boards&r. That is five minutes of burning, so light it and go and see Bram at the mill while it works.", "", "Bram cannot build a Water Wheel until these dry. The kitchen kit comes with them: see &6Cooking and Brewing&r."]`
- and field: `q08.rewards` — insert `{"type": "item", "item": "minecraft:furnace", "count": 2}` after the flint and steel

**[MAJOR] `q05` — `start.json` — nothing in the toast chain ever points at the cellar, and the cellar is where the axe, the hoe and the shears live.**
q03's toast routes her q03 → q04 → q06 and skips q05 entirely. q04 and q05 both end with no
"Next:" line, so the "one popup per quest, pointing forward" promise of `rm_next` breaks twice in
the tutorial chapter. Downstream, q09 wants a hoe and q17 wants an axe — both are q05 rewards.
- field: `q04.rewards` — append `{"type": "toast", "title": "It Never Goes Out", "description": "Next: the gravel patch in the kitchen floor. Josie's shovel is in your bag and there are stairs under it."}`
- field: `q05.rewards` — append `{"type": "toast", "title": "Josie's Cellar", "description": "Next: an axe, a hoe and shears came up those stairs with you. Set the campfire down and cook one soup."}`

**[MAJOR] `q13b` — `act1.json` — "dig straight down" is the one instruction that can kill a first-time Minecraft player, and it is given without a word of caution.**
Fifteen blocks down through unlit stone, with caves and lava under the valley. She has 16 torches
and no idea she should be placing them. She will fall into a cavern in the dark, lose the iron
pickaxe and the backpack, and stop playing.
- field: `description`
- old: `["Bram: \"The weight of the iron sits in beds. And every bed throws its rubbish onto the grass above it.\"", "", "Walk out the west side of the cottage, fifteen paces past the fence, and look down: rust-brown &ahematite samples&r on the grass. From the nearest one, walk seven paces north and dig straight down.", "", "Fifteen blocks down the stone turns red and stays red for twenty more. Hematite breaks into &airon clusters&r; bring back 8."]`
- new: `["Bram: \"The weight of the iron sits in beds. And every bed throws its rubbish onto the grass above it.\"", "", "Walk out the west side of the cottage, fifteen paces past the fence, and look down: rust-brown &ahematite samples&r on the grass. From the nearest one, walk seven paces north and dig down.", "", "&cNever dig the block under your own feet.&r Dig a two-wide staircase down instead, and put a torch every few steps.", "", "Fifteen blocks down the stone turns red and stays red for twenty more. Hematite breaks into &airon clusters&r; bring back 8. Your grave keeps your things — see the &6The Wild&r chapter."]`

**[MAJOR] `q12` — `act1.json` — "the mill plot marked on your map" is the only destination in the first two chapters given without a coordinate, and she has no map.**
q02 gives `-319 74 32`, q07 gives `-302 69 -44`. q12 gives a mod feature she has never opened.
The subtitle says "Walk west" but subtitles are one grey line she will skim past.
- field: `description`
- old: `"Walk to the mill plot marked on your map, talk to &bBram&r, and bring back the Millwright's Bolt he puts in your hand."`
- new: `"Walk west down the river from the square until you find the mill with the snapped axle. Talk to &bBram&r and bring back the Millwright's Bolt he puts in your hand."`
- (if a mill coordinate exists in `valley_sites.json`, put it in `&b…&r` here the way q02 and q07 do)

**[MAJOR] `q11` — `act1.json` — the chicken branch dead-ends: nothing depends on q11, and it is the only quest in Act I with no "Next:" toast, so a player following the popups stops here.**
She has just been given a duckling and a cozy crate — the best felt win in the act — and then the
book goes silent. This is the moment she puts the game down.
- field: `rewards` — append `{"type": "toast", "title": "His Name Is Biscuit", "description": "Next: Bram is at the broken mill west of the square, and Marnie's green planks want a furnace. Ducks and pets have their own chapter: Animals and Fishing."}`

**[MINOR] `q11` — `act1.json` — she already holds three eggs when this opens, so the quest completes itself and the text about waiting for hens reads as nonsense.**
`q10.rewards` includes `minecraft:egg` ×3 and rewards auto-claim. The free win is fine; the
instruction should just admit it.
- field: `description`
- old: `"Collect &a3 eggs&r from the nesting box behind your house and hand them in. Right-click a hen with &achicken feed&r if you would rather not wait for her."`
- new: `"Marnie's three eggs are already in your bag — walk them up to the inn. For the next lot, watch the nesting box, or right-click a hen with &achicken feed&r rather than wait."`

**[MINOR] `q18` — `act1.json` — Pumpkin Pie needs sugar, and no sugar, sugar cane or pumpkin appears in any reward or instruction in the first three chapters.**
"The pumpkin is wild" covers half of it. The sugar half sends her looking for a plant she has
never been told about, in the one quest that gates the Act I finale.
- field: `q15.rewards` — insert `{"type": "item", "item": "minecraft:pumpkin", "count": 2}` and `{"type": "item", "item": "minecraft:sugar_cane", "count": 4}` after the oven
- and field: `q18.description`
- old: `"Hold the Counter, Sink and Oven at hand-in; the book gives them back. Set them on the inn's three grey slabs, 1, 2, 3, then cook &aBread&r, &aPumpkin Pie&r and &aVegetable Soup&r. The pumpkin is wild."`
- new: `"Hold the Counter, Sink and Oven at hand-in; the book gives them back. Set them on the inn's three grey slabs, 1, 2, 3, then cook &aBread&r, &aPumpkin Pie&r and &aVegetable Soup&r. Marnie sent the pumpkins and the cane — cane makes the sugar."`

**[MINOR] `q19` — `act1.json` — asks for 8 Bread, which she already has (Marnie's loaves from q08), but the text does not say so, so she thinks she has to farm 24 more wheat.**
Her patch holds nine wheat plants. Working out that she needs three harvests to bake eight loaves
is a two-in-game-week detour she does not actually have to take.
- field: `description`
- old: `"Sweep the marked cobwebs out of the store with &aOda's Broom&r, then hand &a16 Wheat Flour&r and &a8 Bread&r across the counter."`
- new: `"Sweep the marked cobwebs out of the store with &aOda's Broom&r, then hand &a16 Wheat Flour&r and &a8 Bread&r across the counter. The eight loaves are the ones Marnie brought up the hill — you have been carrying them since spring."`

**[MINOR] `q13b` — `act1.json` — the toast says "press eight Andesite Alloy" but q13 says craft them in a 2x2 checker, and the Mechanical Press does not arrive until after q13.**
Two different verbs for the same step, one of which names a machine she does not own.
- field: `rewards` toast `description`
- old: `"Next: smelt the clusters and press eight Andesite Alloy. Copper, gold and lead sit in beds too."`
- new: `"Next: eight Andesite Alloy, two andesite and two iron nuggets at a time. Copper, gold and lead sit in beds too."`

**[MINOR] `q16` — `act1.json` — "belt the Millstone off them" asks for a Create belt she has no parts for and no task checks.**
The task is two water wheels. The belting sentence sends her into JEI hunting dried kelp. Say it
is optional or point at the chapter that teaches it.
- field: `description`
- old: `"Craft &a2 Water Wheels&r: Bram's way is the Seasoned Oak Boards, Create's own recipe (planks round a shaft) works too. Set them in the mill race beside the mill and belt the Millstone off them so it turns without you."`
- new: `"Craft &a2 Water Wheels&r: Bram's way is the Seasoned Oak Boards, Create's own recipe (planks round a shaft) works too. Set them in the mill race beside the mill — that is the whole quest.", "", "Running a shaft from them to the Millstone so it turns without you is worth doing next; the &6Create&r chapter walks it."`

### Cadence verdict for Act I
The felt-win rhythm is genuinely good in the first half — q10 (coop scene), q11 (a duck lands on
her boot), q12 (third resident, journal entry), q13a (a hammer that breaks 3x3). Then it collapses:
**q14 → q15 → q16 → q17 is roughly 67 minutes with one loot crate and no scene, no title card, no
new neighbour and no bossbar movement.** That is the longest joyless stretch anywhere on this
route, it lands right after the two hardest walls in the game, and it is where a Stardew player
decides this is not the game she was promised. The fixes above cut it to ~45 minutes; if one more
thing can be added, a `cozy_crate` on `q15` would buy back the middle of it.

---
## 4. Farm and Seasons (`story/quests/farm.json`) — 18 quests

`rm_lanes` sends her here as "the cozy lane", so this is the chapter that has to feel like Stardew.

### Timeline
```
farm_ground        |  4 min | Crafts a stone hoe, tills a strip by the lake. Good root.
farm_wheat         | 45 min | Two crop cycles for 32 wheat. Mostly waiting. No filler offered.
farm_calendar      |  5 min | Crafts a calendar, reads spring. The best quest in the chapter.
farm_spring        | 60 min | Carrots and potatoes she has; strawberries she has to find wild
                             with no hint where.
farm_summer        | GATED  | Cannot start for ~5 real hours. Board gives no sign of that.
farm_autumn        | GATED  | Cannot start for ~10 real hours.
farm_winter_rule   |  1 min | The single most reassuring line in the chapter, marked optional.
farm_compost       |  8 min | Near-instant — q09 already gave her 16 bone meal.
farm_delight       | 35 min | Three of the four seeds are already in her bag from q06. Onion
                             is a genuine hunt with no location given.
farm_silo          |  5 min | Nine planks. Easy win.
farm_thermal_crops | 50 min | Told to "craft the seeds". There is no seed recipe.
farm_berries       | 20 min | Berry bushes and cabbage. Pleasant.
farm_rich          | 12 min | Needs a cutting board she does not have and is not pointed at.
farm_phytogro      | 25 min | Mining apatite and niter. A tech quest wearing a farm hat.
farm_rice          | 20 min | Shallow water at the lake edge. Clear and findable.
farm_bees          | 15 min | Campfire under the nest. The danger warning is correctly loud.
farm_insolator     | 40 min+| A Thermal machine frame and lumium gears, required, in the cozy
                             chapter she was told avoids all of that.
farm_winter_crop   | GATED  | Winter is ~15 real hours from her first spring morning.
```
**Active work ≈ 5 h 30 m. Wall-clock to finish the chapter ≈ one in-game year.**

### Findings

**[BLOCKER] chapter-wide — `farm.json` — a season here is 27 in-game days and the book never says so, so the three seasonal quests read as broken rather than long.**
`pack/config/sereneseasons/seasons.toml`: `sub_season_duration = 9`, three sub-seasons per season,
`day_duration = 24000`. That is 27 Minecraft days per season — roughly 5 real hours with nightly
sleeping, ~9 without — and a full year before `farm_winter_crop` can even be attempted. A newcomer
opens `farm_summer` in spring, plants melon, watches nothing happen for twenty minutes and
concludes the pack is broken. She has been told "nothing here is timed", which she will now read
as a lie. This needs to be said once, loudly, on the quest that hands her the calendar.
- field: `farm_calendar.description`
- old: `["Hold the &aCalendar&r to read the season and the day. Every crop here is tagged to a season, and out of season it does not grow one stage.", "", "&bSpring&r: carrot, potato, strawberry. &bSummer&r: melon, tomato, corn. &bAutumn&r: pumpkin, beetroot, amaranth."]`
- new: `["Hold the &aCalendar&r to read the season and the day. Every crop here is tagged to a season, and out of season it does not grow one stage. &cIt is not broken — it is waiting.&r", "", "A season is &b27 days&r long, so the three quests below are a year-long thread. Leave them running and play the rest of the valley around them.", "", "&bSpring&r: carrot, potato, strawberry. &bSummer&r: melon, tomato, corn. &bAutumn&r: pumpkin, beetroot, amaranth."]`

**[MAJOR] `farm_thermal_crops` — `farm.json` — "Craft the seeds" for barley, spinach, sadiroot and bell pepper; none of the four has a crafting recipe.**
The only exported recipes touching `thermal:*_seeds` are insolator recipes that *consume* them.
The real source is the wild Thermal crops that generate in the world. She will type "barley seeds"
into JEI, get nothing, and stop.
- field: `description`
- old: `["Craft the seeds for &abarley&r, &aspinach&r, &asadiroot&r and &abell pepper&r, plant them, and harvest sixteen of each.", "", "The first three keep growing outdoors in December. Bell pepper stops at the frost."]`
- new: `["These four grow wild. Walk the meadows and the field edges until you find &abarley&r, &aspinach&r, &asadiroot&r and &abell pepper&r standing in the grass, break them for seed, then plant and harvest sixteen of each.", "", "The first three keep growing outdoors in December. Bell pepper stops at the frost."]`

**[MAJOR] `farm_insolator` + `farm_winter_crop` — `farm.json` — the required spine of the cozy chapter ends in a Thermal machine frame and lumium gears, which is exactly what `rm_lanes` promised her she could skip.**
`rm_lanes`: "Most of the book is the cozy lane: food, animals, planting, decorating." Then the
farming chapter cannot be completed without the tech chapter. Either move them out of the required
spine or stop calling this the cozy lane. Marking both optional is the smaller change and keeps the
chapter honest; they stay in the chain and still carry the chapter's "Next:" toast.
- field: `farm_insolator.optional` — old `false`, new `true`; `shape` old `"hexagon"` new `"rsquare"`, `size` old `1.5` new `1.0`
- field: `farm_winter_crop.optional` — old `false`, new `true`; `shape` old `"hexagon"` new `"rsquare"`, `size` old `1.5` new `1.0`
- and field: `farm_insolator.description` (first line)
- old: `"The &aInsolator&r takes seeds, water and phytogro and hands back the crop. It is a machine, so no season touches it."`
- new: `"The stretch goal of this chapter, and the only one that needs the tech lane. The &aInsolator&r takes seeds, water and phytogro and hands back the crop, and no season touches it."`

**[MAJOR] `farm_wheat` — `farm.json` — "leave them until the stalks go gold" is the first real crop wait in the book and the quest offers her nothing to do for forty minutes.**
Two cycles of wheat with nothing beside it. Every other long quest in this chapter has a sibling
she could be doing; the text should say so, once, here, where the habit is formed.
- field: `description`
- old: `["Plant &awheat seeds&r on wet farmland and leave them until the stalks go gold before you cut.", "", "Act I, step 8 wants sixteen flour and eight bread off this patch."]`
- new: `["Plant &awheat seeds&r on wet farmland and leave them until the stalks go gold before you cut.", "", "Crops grow while you are elsewhere. Put the composter in, hunt the wild crops, or go and see Bram — do not stand and watch the rows.", "", "Act I, step 8 wants sixteen flour and eight bread off this patch."]`

**[MAJOR] `farm_winter_rule` — `farm.json` — "It is not broken" is the one line that stops a confused player quitting, and it is buried on an optional gear quest about winter.**
The same rule applies in every season to every out-of-season crop, from her first day. Covered by
the `farm_calendar` rewrite above; this quest should then narrow to what winter specifically stops.
- field: `optional`
- old: `true`
- new: `false`  *(it is the rule that makes the seasonal trio legible; it should not be skippable)*

**[MAJOR] `farm_delight` — `farm.json` — three of the four "wild crops" are already in her bag and the fourth has no location, so she goes hunting for all four.**
q06 in `start.json` rewards `farmersdelight:cabbage_seeds` ×8, `farmersdelight:tomato_seeds` ×8 and
`farmersdelight:rice` ×8. Only onion is a real hunt, and the description locates only cabbage.
- field: `description`
- old: `["Marnie: \"Cabbage grows wild along the treeline. I have walked past it for ten years because I like the walk.\"", "", "Take a start of cabbage, tomato, onion and rice from the wild patches, replant them at home, and harvest eight of each."]`
- new: `["Marnie: \"Cabbage grows wild along the treeline. I have walked past it for ten years because I like the walk.\"", "", "Josie's seed tin already holds cabbage, tomato and rice — plant those at home. Only the &aonion&r is still out there, in the long grass on the forest edge.", "", "Harvest eight of each."]`

**[MINOR] `farm_spring` — `farm.json` — strawberries are the only spring crop she cannot get from her own bag, and the quest does not say where they grow.**
Carrots and potatoes came from Marnie's sack in q08. `thermal:strawberry_seeds` has no recipe; the
plant generates wild.
- field: `description`
- old: `["Plant &acarrots&r, &apotatoes&r and &astrawberries&r on the first spring page and bring in sixteen of each.", "", "Wheat is spring-fertile in this pack on purpose, so Act I is not waiting on July."]`
- new: `["Carrots and potatoes came out of Marnie's sack. &aStrawberries&r grow wild in the meadow — break the plants for seed, then plant all three and bring in sixteen of each.", "", "Wheat is spring-fertile in this pack on purpose, so Act I is not waiting on July."]`

**[MINOR] `farm_rich` — `farm.json` — "Straw and bark both come off a cutting board" names a block she does not own and does not point at the chapter that gives it.**
Every other cross-system mention in this chapter carries a `&6chapter&r` pointer. This one does not.
- field: `description`
- old: `"&aOrganic Compost&r is straw, tree bark, bone meal and one dirt on the grid. Straw and bark both come off a cutting board."`
- new: `"&aOrganic Compost&r is straw, tree bark, bone meal and one dirt on the grid. Straw and bark both come off a &aCutting Board&r — that is the first quest in &6Cooking and Brewing&r."`

**[MINOR] `farm_ground` — `farm.json` — the chapter root gives 16 seeds and one XP level, the thinnest root reward in the book, on the chapter a new player is told to open first.**
Every other chapter root lands harder. This one is where she decides whether the cozy lane is worth
her evening.
- field: `rewards` — append `{"type": "loot", "table": "farm_crate"}`

---
## 5. Cooking and Brewing (`story/quests/kitchen.json`) — 16 quests

The best-written chapter on this route. Mechanics are actually explained ("put an item on the
Cutting Board and right-click it with a knife", "connected blocks share one inventory"), which is
exactly what the newcomer needs and mostly does not get elsewhere.

### Timeline
```
kitchen_pot     |  1 min | Instant — q03 already gave her a Cooking Pot. 16 bowls, 8 onions.
kitchen_board   |  8 min | Cutting board + iron knife. Clear, teaches a real mechanic.
kitchen_skillet | 12 min | Bacon needs the cutting board from the sibling quest. Not said.
kitchen_kettle  | 25 min | Finds wild tea bushes (no location), then waits on daylight drying.
kitchen_grapes  | 30 min | Pot, lattice, wait for the vine, pick 16 bunches.
kitchen_stove   | 10 min | Easy, satisfying, optional.
kitchen_nether  | 60 min+| A trip to the Nether, in the cozy chapter, with no on-ramp at all.
kitchen_counter | 12 min | She already holds all three from q15. Free milestone.
kitchen_fridge  | 15 min | Fridge + toaster. Good.
kitchen_bakery  | 20 min | Baker station, dough, four loaves. Needs sugar and a bucket.
kitchen_cake    | 20 min | Two cakes. The only quest that tells her where strawberries grow.
kitchen_candle  | 15 min | Pan, table set, bolognese.
kitchen_teas    | 45 min | Black, hibiscus, coffee — coffee means finding a jungle.
kitchen_press   | 20 min | Apple press, mash, ferment, two juices.
kitchen_wine    | 25 min | Barrel, sugar, bottle, a wait of unstated length.
kitchen_feast   | 25 min | Four dishes off four stations. Correct capstone.
```
**Chapter total: ~5 h 40 m.**

### Findings

**[MAJOR] `kitchen_skillet` — `kitchen.json` — Bacon and Eggs cannot be made without the cutting board taught in the sibling quest, and this one only depends on the pot.**
Raw `farmersdelight:bacon` has no crafting recipe; it comes off a cutting board from a porkchop.
`farmersdelight/bacon_and_eggs.json` is also a **shapeless crafting recipe**, not a skillet recipe —
so "Cook Bacon and Eggs on it" is wrong twice. She will hold the skillet over the fire with a raw
porkchop and get nothing.
- field: `description`
- old: `["Pip: \"You can hit things with it while it's still hot. Aunt Marnie says not to.\"", "", "Craft a &aSkillet&r, hold it over a fire and fry one item at a time. Cook &aBacon and Eggs&r on it.", "", "Fastest breakfast in the valley."]`
- new: `["Pip: \"You can hit things with it while it's still hot. Aunt Marnie says not to.\"", "", "Craft a &aSkillet&r, hold it over a fire and fry one item at a time.", "", "Slice a porkchop into &abacon&r on the &aCutting Board&r first — that is the quest beside this one — then fry the bacon and two eggs and put the plate together on the grid.", "", "Fastest breakfast in the valley."]`

**[MAJOR] `kitchen_nether` — `kitchen.json` — sends her to a different dimension out of a cooking chapter, with no word on how to get there and no pointer to the chapter that covers it.**
`wild.json` has `wild_nether` and `wild_fortress`; this quest should hand her over to them.
As written the only preparation offered is "take a machete, take water too", which reads as a
picnic list. She has never built a portal and does not know obsidian exists.
- field: `description`
- old: `["Craft an &aIron Machete&r, which cuts a fungus colony down in one swing, then grill &a2 Nether Skewers&r over a blackstone stove.", "", "&cHoglins hit hard&r and striders burn nothing but your patience."]`
- new: `["This one is a trip. The fungus grows in the &cNether&r, through a portal you have to build first — the &6The Wild&r chapter walks you in and back out.", "", "Craft an &aIron Machete&r, which cuts a fungus colony down in one swing, then grill &a2 Nether Skewers&r over a blackstone stove.", "", "&cHoglins hit hard&r and striders burn nothing but your patience."]`

**[MAJOR] `kitchen_kettle` — `kitchen.json` — two unlocated things and one silent real-time wait in a single quest.**
"pick 8 Green Tea Leaves off the wild bushes" — which bushes, where? "Dry the leaf blocks in
daylight" — for how long? This is the pattern the whole book repeats: a wait she cannot plan
around. `kitchen_cake` proves the chapter knows how to do this ("Wild strawberries grow in the
meadow above the mill"); this quest should match it.
- field: `description`
- old: `["Halden: \"Green leaves want a week of sun before they want a kettle. Everything here waits.\"", "", "Craft a &aTea Kettle&r and pick &a8 Green Tea Leaves&r off the wild bushes. Dry the leaf blocks in daylight, then brew dried leaf with a glass bottle over heat.", "", "A brewed cup carries a small effect for half an hour."]`
- new: `["Halden: \"Green leaves want a week of sun before they want a kettle. Everything here waits.\"", "", "Craft a &aTea Kettle&r and pick &a8 Green Tea Leaves&r off the low bushes along the lake path below Halden's hedge.", "", "Lay the leaf blocks somewhere the sun reaches and leave them a full day — go and cook something. Then brew dried leaf with a glass bottle over heat.", "", "A brewed cup carries a small effect for half an hour."]`

**[MINOR] `kitchen_teas` — `kitchen.json` — "Coffee beans grow wild on jungle trunks" is a biome expedition dropped in as a closing aside, with no way to find a jungle.**
`travel.json` has Nature's Compass. One pointer turns an open-ended search into an errand.
- field: `description`
- old: `"Coffee beans grow wild on jungle trunks."`
- new: `"Coffee beans grow wild on jungle trunks. Find the nearest jungle with &aNature's Compass&r — see the &6Getting Around&r chapter."`

**[MINOR] `kitchen_press` and `kitchen_wine` — `kitchen.json` — both hinge on a fermentation wait whose length is never given, in a chapter that otherwise gives real numbers.**
"leave the mash in the press to ferment" and "leave it alone until it reads as Apple Wine". She
will stand and watch. One clause each fixes it.
- field: `kitchen_press.description`
- old: `"Build an &aApple Press&r. Drop apples in for &aApple Mash&r, leave the mash in the press to ferment, and draw off &a2 Apple Juice&r."`
- new: `"Build an &aApple Press&r. Drop apples in for &aApple Mash&r, then leave the mash in the press — it works on its own and takes minutes, not seconds. Come back and draw off &a2 Apple Juice&r."`
- field: `kitchen_wine.description`
- old: `"Build a &aFermentation Barrel&r. Pour in apple juice with sugar and an empty &aWine Bottle&r, then leave it alone until it reads as &aApple Wine&r."`
- new: `"Build a &aFermentation Barrel&r. Pour in apple juice with sugar and an empty &aWine Bottle&r, then walk away — it ferments on its own clock. It reads as &aApple Wine&r when it is done."`

**[MINOR] cross-chapter — `kitchen_pot` hands her eight onions on a root quest she completes instantly, while `farm_delight` sends her hunting for wild onion.**
The two chapters do not know about each other. `farm_delight` should say so (folded into the
`farm_delight` fix above; the exact clause to add is below).
- field: `farm_delight.description` — append to the FIND rewrite
- add: `"Marnie hands eight onions across the counter on the first quest of &6Cooking and Brewing&r if you would rather not walk the treeline."`

**[MINOR] `kitchen_grapes` — `kitchen.json` — never says where Red Grape Seeds come from, and it is a required quest gating `kitchen_press`.**
The rewards give her eight seeds *after* she has grown sixteen grapes.
- field: `description`
- old: `"Plant &aRed Grape Seeds&r in a &aGrapevine Pot&r with a lattice standing over it and the vine climbs on its own. Pick the bunches by hand once they redden."`
- new: `"Wild grapes hang on the sunny slope behind Halden's hedge — pick one for seed. Plant &aRed Grape Seeds&r in a &aGrapevine Pot&r with a lattice standing over it and the vine climbs on its own. Pick the bunches by hand once they redden."`

---
## 6. Animals and Fishing (`story/quests/animals.json`) — 14 quests

### Timeline
```
an_pen      | 25 min | Crafts 24 fences in a minute, then hunts a slimeball for the leads.
an_cows     | 15 min | Finds cows, breeds them with wheat, fills a milk bucket.
an_sheep    | 10 min | Shears sixteen wool. Clean, quick, the shears came from q05.
an_coop     | 40 min | Sixteen eggs off three hens. Almost entirely waiting.
an_ducks    | 20 min | Duck eggs in the reeds. Charming.
an_bees     | 15 min | Near-duplicate of farm_bees; free progress.
an_tame     | 20 min | Finds a wolf, crafts a collar tag (chain + copper), beds it.
an_pet_kit  | 15 min | Drum and wayward lantern.
an_rod      | 10 min | Iron rod. String from the cobwebs she swept out of Oda's store.
an_worms    | 10 min | Worm farm, eight worms.
an_catch    | 45 min | Four species of fish, on RNG, reeling with a two-finger tap.
an_fillet   | 15 min | Fillet knife, eight cooked fillets.
an_mount    | 10 min | Two fish mounts on the inn wall. Lovely payoff.
an_ribbits  | 20 min | Walks downstream to the frogs. No coordinate given.
```
**Chapter total: ~4 h 30 m.**

### Findings

**[BLOCKER] `an_pen` — `animals.json` — the root of the cozy animals chapter demands 2 Leads, and a Lead needs a slimeball; every other quest in the chapter chains off this one.**
`minecraft/lead.json`: 4 string + 1 **slime ball** → 2 leads. Slimeballs come from slimes, which
mean a swamp at night or a slime chunk deep underground — a hostile-mob expedition standing between
a Stardew player and "fence a pen and lead two animals in". Worse, the description already offers
her the alternative ("or hold &aWheat&r and walk slowly") while the task still demands the leads,
so the quest contradicts itself.
- field: `q11.rewards` (Act I, already the animals beat and already points at this chapter) — append `{"type": "item", "item": "minecraft:slime_ball", "count": 4}`
- and field: `an_pen.description`
- old: `["Marnie: \"Anything that eats will follow you. That is not affection, it is arithmetic.\"", "", "Fence a square behind the barn, then bring in two animals on a &aLead&r, or hold &aWheat&r and walk slowly.", "", "Two animals in a pen is a herd by autumn."]`
- new: `["Marnie: \"Anything that eats will follow you. That is not affection, it is arithmetic.\"", "", "Fence a square behind the barn and walk two animals into it holding &aWheat&r — they follow the food.", "", "Make the two &aLeads&r as well: four string and one of Pip's slimeballs makes a pair, and a led animal does not wander off mid-hill.", "", "Two animals in a pen is a herd by autumn."]`

**[MAJOR] `an_coop` — `animals.json` — sixteen eggs off three hens is roughly forty minutes of standing near a box, and the quest is required.**
Three hens lay one egg each every five to ten minutes. The line "Hens lay whether you watch or not"
is the right instinct but stops one clause short of telling her to leave.
- field: `description`
- old: `["Pip: \"They lay in the box if the box is dark. I checked. Forty times.\"", "", "Keep three hens penned and pick up the &aEgg&r each one drops. &aWheat Seeds&r in your hand walk them anywhere.", "", "Marnie took the first three: Act I, step 3."]`
- new: `["Pip: \"They lay in the box if the box is dark. I checked. Forty times.\"", "", "Keep three hens penned and pick up the &aEgg&r each one drops. &aWheat Seeds&r in your hand walk them anywhere.", "", "Sixteen eggs is most of an afternoon of hen time. Go fishing and come back to a full box — they lay whether you are there or not.", "", "Marnie took the first three: Act I, step 3."]`

**[MAJOR] `an_catch` — `animals.json` — four named species on random rolls, and nothing tells her that fishing has a timing input she has to hit.**
Aquaculture rolls the species per catch; four specific fish is a long tail. On top of that she has
never fished: the bobber dips, and she has a fraction of a second to right-click — a two-finger tap
on a trackpad. The quest explains bait and depth, which is good, and says nothing about the moment
that actually decides whether she catches anything.
- field: `description`
- old: `["Nella: \"Four is not a competition. Six is a competition. We will get to six.\"", "", "Cast off the pier for &aBluegill&r and &aPerch&r. &aCatfish&r and &aCarp&r sit on the bottom, so hook a worm first.", "", "Three of them go on the inn wall in Act V."]`
- new: `["Nella: \"Four is not a competition. Six is a competition. We will get to six.\"", "", "Right-click to cast. When the float dips and you hear the splash, right-click again — that is the whole skill.", "", "Cast off the pier for &aBluegill&r and &aPerch&r. &aCatfish&r and &aCarp&r sit on the bottom, so hook a worm first. Which fish comes up is luck; keep casting.", "", "Three of them go on the inn wall in Act V."]`

**[MINOR] `an_tame` — `animals.json` — a required milestone that starts with "tame a wolf", which is the first hostile-adjacent errand in the cozy group, with no note that a wolf can turn on her.**
Feeding bones to a wolf is safe; failing to feed it enough and hitting it is not. She also needs a
chain and a copper ingot for the collar tag, neither of which is mentioned.
- field: `description`
- old: `"Tame a wolf with bones or a cat with raw fish, then put a &aCollar Tag&r on it to name it and set its collar colour."`
- new: `"Feed &abones&r to a wolf in the woods until hearts pop — keep feeding, never hit it — or a cat with raw fish. Then put a &aCollar Tag&r on it (a chain and a copper ingot) to name it and set its collar colour."`

**[MINOR] `an_ribbits` — `animals.json` — "walk downstream to the reed village" is the only destination in the chapter and it has no coordinate.**
Every other place in the book she has been sent to carries `&b…&r` numbers or a landmark.
- field: `description`
- old: `"Walk downstream to the reed village and trade for &aRed&r and &aBrown Toadstools&r. They grow in the boardwalk planters too."`
- new: `"Follow the river down from the mill to the reed village on the shallows — the one you first walked into at Act II, step 1 — and trade for &aRed&r and &aBrown Toadstools&r. They grow in the boardwalk planters too."`

**[MINOR] `an_bees` — `animals.json` — near-identical to `farm_bees` in `farm.json` (beehive plus a hive product), so one of them completes itself the moment she finishes the other.**
Harmless as free progress, but the chapter looks padded to a player reading both boards. If one
should go, this is the one — `farm_bees` earns its place next to the crops.
- field: `optional` — already `true`, no change needed; consider retitling to make the difference visible
- old title: `"Hive the Bees and Take Three Combs"`
- new title: `"Wax the Hive and Bottle the Honey"`

---
## 7. Home and Town (`story/quests/home.json`) — 14 quests

### Timeline
```
home_root        |  8 min | Crafts a second cottage door (hers is already hung). Home crate.
home_windows     | 10 min | Sand, furnace, glass, two windows and two shutters.
home_roof        |  8 min | Twelve roof blocks, four ridge pieces. Visible instantly.
home_fence       |  6 min | Picket fence and a gate round the patch.
home_comforts    | 10 min | Sleeping bag and hammock. The sleeping bag is a real quality-of-life
                            unlock and she will not know that until she uses it.
home_carryon     |  3 min | An info gear. Teaches sneak + empty hand — but not that sneak is Shift.
home_chairs      |  6 min | Table and two chairs by the fire. Home crate.
home_lights      |  8 min | Six sconces, two lanterns.
home_flowers     |  6 min | Flower boxes — she already has the planters from q17.
home_wardrobe    |  6 min | Wardrobe and two drawers.
home_handcrafted |  8 min | Bench, shelves, cups.
home_jars        |  8 min | Four jars on two item shelves.
home_signs       |  6 min | Sign posts and a notice board.
home_megatorch   |  2 min | Instant — she has two spare megatorches from q04.
```
**Chapter total: ~1 h 35 m.**

### Verdict
**This is the best-paced chapter on the whole route for this player, and nothing points her at it
early enough.** Every quest is 6–10 minutes, ends in a visible change to her own house, needs no
season, no RNG, no unfindable item and no machine. It is the Stardew decorating loop, and it is
sitting behind the farm chapter that opens with a forty-minute wheat wait. If one structural
change is made for the newcomer, it is telling her this chapter exists on day one.

### Findings

**[MAJOR] `rm_lanes` — `readme.json` — the "cozy lane" pointer sends her only to Farm and Seasons, the chapter with the longest waits, and never mentions Home and Town, the chapter with none.**
Refinement of the earlier `rm_lanes` fix; this is the version to use.
- field: `description`
- old: `["Most of the book is the cozy lane: food, animals, planting, decorating. Start in the &6Farm and Seasons&r chapter.", "", "Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."]`
- new: `["Most of the book is the cozy lane: food, animals, planting, decorating.", "", "After &6Start Here&r, plant something in &6Farm and Seasons&r and then go and build in &6Home and Town&r while it grows. Crops take days; a door takes a minute.", "", "Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."]`

**[MINOR] chapter subtitle — `home.json` — "None of it is required" is not true; five of the fourteen are `optional: false`.**
Small, but this is the one player who reads the reassurance and then trusts it.
- field: chapter `subtitle`
- old: `["Doors that shut, chairs that face the fire, and a light on the porch.", "None of it is required. All of it is why anybody stays."]`
- new: `["Doors that shut, chairs that face the fire, and a light on the porch.", "Nothing here blocks the story. All of it is why anybody stays."]`

**[MINOR] `home_carryon` — `home.json` — "Sneak and use an empty hand on it" never says which key sneak is, in the chapter's only keyboard instruction.**
Same defect as `readme_hands`. She has no reason to know Shift crouches.
- field: `description`
- old: `["&bCarry On&r picks up a chest, a barrel or a machine with everything still inside it.", "", "Sneak and use an empty hand on it. You walk slow until you set it down."]`
- new: `["&bCarry On&r picks up a chest, a barrel or a machine with everything still inside it.", "", "Hold &bShift&r to sneak and right-click it with an empty hand. You walk slow until you set it down."]`

**[MINOR] `home_megatorch` — `home.json` — the chapter's `hexagon 1.5` capstone completes itself, because q04 already gave her two spare megatorches.**
A capstone that ticks the moment she opens the tab reads as the chapter being finished for her.
Asking for the second one she actually stands in the yard keeps the milestone.
- field: `tasks[0].count`
- old: `1`
- new: `2`

**[MINOR] `home_comforts` — `home.json` — the sleeping bag is the answer to the daytime-sleep problem from q08, and neither quest knows about the other.**
`comforts:sleeping_bag_red` lets her pass a night anywhere without moving her spawn. That is the
single most useful thing in this chapter for a new player and it is described as a convenience.
- field: `description`
- old: `["A &aSleeping Bag&r passes the night and leaves your spawn where it is. A &aHammock&r needs two Rope and Nail.", "", "Craft one of each and keep the bag on you."]`
- new: `["A &aSleeping Bag&r passes the night anywhere and leaves your spawn where it is — roll it out on the road instead of walking home in the dark. A &aHammock&r needs two Rope and Nail.", "", "Craft one of each and keep the bag on you."]`

---

## 8. Appendix — the MacBook Air problem, outside my route

Two more quests in `tips.json` name keys that do not exist as single keys on her laptop. Same
defect class as `readme_night`; listing them so the fix lands everywhere at once.

**[MAJOR] `tips_f3` — `tips.json` — "Press &bF3&r" opens Mission Control on a MacBook.**
- field: `description`
- old: `"Press &bF3&r. The XYZ line top left is where you stand; the line under it is the way you face."`
- new: `"Press &bF3&r — on a Mac laptop, &bfn&r + &bF3&r. The XYZ line top left is where you stand; the line under it is the way you face."`

**[MAJOR] `tips_keys` — `tips.json` — "&bHome&r lists where you died" names a key a MacBook Air does not have.**
The quest calls these "the four keys that matter", so one of the four is unusable on her machine.
- field: `description`
- old: `["&bJ&r opens this book. &bB&r opens your backpack. &bC&r picks a chest up with everything still in it.", "", "&bHome&r lists where you died. All four move under Options - Controls."]`
- new: `["&bJ&r opens this book. &bB&r opens your backpack. &bC&r picks a chest up with everything still in it.", "", "&bHome&r lists where you died — a Mac laptop has no Home key, so use &bfn&r + &bleft arrow&r, or bind it to something else.", "", "All four move under Options - Controls."]`

---

## 9. Systemic findings (whole book)

**[BLOCKER] eleven quests are flagged `optional: true` while a required quest depends on them.**
FTB Quests draws optional quests differently and leaves them out of chapter completion, so "optional"
reads to a new player as "skippable". Every one of these silently locks a required quest, and the
board gives no reason why. Full list, from a dependency scan of all 22 chapters:

| optional quest | file | blocks (required) |
|---|---|---|
| `q18` Fit the Kitchen and Cook Three Dishes | act1.json | `q19` (Act I finale) |
| `q33` Fit the Workshop With Drawers and Barrels | act2.json | `q32`, `q37` (Act II finale) |
| `q39` Fill the Granary's Twelve Alcoves | act3.json | `q52` |
| `q42` Put Up Twelve Preserves | act3.json | `q43`, `q47` |
| `q48a` Fit Out the Two Guest Rooms | act3.json | `q51a` |
| `q54a` Salt Eight Fillets into the Granary | act3.json | `q56` (Act III finale) |
| `q78` Dress the Square's 30 Copper Tiles | act5.json | `q79`, `q89` |
| `q80` Catch Three Named Fish for the Inn Wall | act5.json | `q85` |
| `travel_map` Open the Map and Mark the Mill | travel.json | `travel_nature` |

- fix: set `optional: false` on all nine, and `shape` `"rsquare"` → `"square"` to match. Optional
  should mean "nothing waits on this". The spec's own rule — "optional only changes the completion
  maths and the look" — is only true when nothing depends on them.
- (three of the four story finales are behind one of these. `q18` and `q54a` are the worst: both
  gate an act ending.)

**[MAJOR] three story quests end with no "Next:" toast, and all three are dead ends.**
`rm_next` promises "one popup per quest, pointing forward". It breaks at `q04` and `q05` (the
tutorial chapter) and at `q11` (the end of the Act I chicken branch, right after the best emotional
beat in the act). `q24`, `q61`, `q62`, `q63`, `q70a`, `q72a` and `q84a` are the same shape later on,
but those are all optional side branches where a silent finish is defensible. The three on this
route are not: `q05` carries the axe, hoe and shears the next four quests need.
- fix: the three `rewards` toast additions given under Act I and Start Here above.

**[MAJOR] the book never teaches a single control, and it is written for a player who has none.**
Across `readme.json`, `start.json` and `act1.json` the instructions assume, without ever stating:
WASD to walk, the mouse to look, `E` to open the inventory, `Shift` to sneak, right-click as a
distinct action, and that holding right-click is how you turn a crank. `readme_hands` is the one
quest with the job of saying this and it says only left-click and right-click. On a trackpad, four
of those six need explaining before she can follow the second quest in the game.
- fix: the `readme_hands` rewrite above, plus the `home_carryon` and `q14` clauses.

**[MINOR] waits are never named.** Twelve quests on this route hinge on a wait with no length and no
suggestion of what to do meanwhile: `farm_wheat`, `farm_spring/summer/autumn`, `farm_winter_crop`,
`q15` (5 min 20 s of smelting), `an_coop` (~40 min of hens), `kitchen_kettle`, `kitchen_press`,
`kitchen_wine`, `q08` (waiting for dusk). The book has exactly the right instinct in `rm_notimer`
("Crops keep. Neighbours wait.") and then never applies it to a specific quest. The pattern fix is
one clause per quest: say how long, and name one thing to go and do.

---

## 10. Totals

| Segment | As written | With the fixes above |
|---|---|---|
| Read Me First | 11 min | 11 min |
| Start Here (q01–q08) | ~65 min | ~50 min |
| Act I (q09–q19) | ~2 h 23 m | ~1 h 45 m |
| **Start Here + Act I** | **~3 h 30 m** | **~2 h 35 m** |

Beyond the assigned route, for context: Farm and Seasons ~5 h 30 m of work spread over an in-game
year, Cooking and Brewing ~5 h 40 m, Animals and Fishing ~4 h 30 m, Home and Town ~1 h 35 m.

### Does the first hour give a felt win every 5–10 minutes?
**Yes, up to q08 — then no.** Minutes 0–65 land four title cards and the first neighbour, which is
the right rhythm. From q13b to q17 (roughly minutes 95–160) there is one loot crate, no scene, no
title card, no new resident and no bossbar movement, and it contains both hard walls (`q14`'s
andesite casing, `q06`'s bowl if she got past it). That stretch is where a Stardew player who has
been promised a cozy game puts it down. It is fixable with text: the three blockers above account
for most of the dead time, and a `cozy_crate` on `q15` covers the rest.
