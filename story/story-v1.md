# COPPER KETTLE VALLEY — Story Document v1
### *A Year in the Valley* · Minecraft Forge 1.20.1 · private modpack
**Status:** final synthesis. Winner spine = *seasons*. Grafts from *inheritance* (Lanternwick) and *buried-age* (Copperbell Hollow) marked inline where they matter.

---

## 1. Pack name and tagline

**Candidates considered**

1. **Copper Kettle Valley** — warm and domestic on the title screen, and quietly names the tech spine. The valley is named for the Kettle family, who ran the copper works and the inn. A kettle is a cozy object and a pressure vessel.
2. **Hearthfall** — evocative, but a non-gamer reads it as generic fantasy.
3. **The Long Year at Mossgrove** — good prose, wrong promise. "Long" reads as slog.

**Chosen: COPPER KETTLE VALLEY.**

**Tagline:** *You inherited a cold house in a quiet valley. Put the kettle on — you have one year, and one winter, to prove this place can keep its own lights on.*

The tagline is doing a job. The player this pack is built for bounces off open worlds because nothing ever says *when*. So the tagline states the clock in the first sentence. There is no "take your time." There is a year, there are five parties, and the last one has a date.

---

## 2. Premise (shown on first join)

You inherited the old Kettle farm from a great-aunt you barely remember — **Josie Kettle**, who kept the lights on in this valley long after everyone else stopped trying. The letter says the house is "mostly standing." It is: a chimney, three walls, a bed frame, and a copper kettle still hanging over a cold hearth.

The valley outside is not empty, exactly. There is an inn with no innkeeper, a mill with a snapped axle, a general store with the shutters down, and a marsh full of frog-folk who have not had a neighbour in years. Every February for a decade, somebody has packed up and left, and nobody has ever come back in April.

Josie left a journal on the mantle. The first page says the same thing every page after it says: *the valley only ever needed one person to start.*

You have one spring to make this place livable, one summer to make it worth staying, one autumn to fill the larder, and one winter to prove the valley can keep its own lights on. Then it starts again, warmer.

**First-join screen (title + subtitle + tellraw):**

> *Spring, Year One.*
> **COPPER KETTLE VALLEY**
> Open your Quest Book. There is exactly one thing to do.

**Second letter (multiplayer, see §9).** Josie wrote to more than one relative. She was not a woman who put all her eggs in one nephew. Any second team's first-join gives them their own copy of the letter, in her hand, dated the same day.

---

## 3. The setting

### The valley
A shallow bowl of meadow, water and low hills — a market road, a stream, a lake, a marsh, and one hillside where the copper seam still shows through the grass. Nothing is pre-built. Everything the story needs is placed by the players, and the game builds around them. (See **The Town Anchor**, below — this is the load-bearing engineering idea of the whole pack.)

### What is broken
- **The Hearth** — the inn's fireplace, the valley's social centre. Cold since Josie died. Nobody has cooked for anybody in years.
- **The Mill** — Bram's water wheel snapped its axle. No flour, no sawn boards, no power of any kind.
- **The Store** — Oda's shelves are empty because no wagon has come up the road. The bounty board outside has one weathered notice on it.
- **The Lake** — Nella's boat is beached and the docks are rotted.
- **The Lantern Road** — forty lamp posts from the mill to the square to the lake. Josie counted them on her fingers as a child. Every one of them is dark.
- **The Works** — the Kettle copper works, a hole in the hill with a collapsed adit, and a sealed iron door in the cellar under your own house with Josie's handwriting on it: *"Not yet. — J.K."*
- **The winter** — the real antagonist. Non-lethal, comprehensible without any gaming literacy, and undefeatable by kindness. From November to March the valley cannot grow, light or heat anything. Every year, whoever is left goes.

### What restoring it means
Restoration is measured in **people, and in lamps**. Two counters, both readable without opening a menu:

- **Residents** — 1 → 8 named neighbours plus four Ribbits plus three new arrivals. Each one makes a lane easier: Marnie feeds you, Bram powers you, Oda supplies you, Nella moves you, Halden heals you, Wisp forages for you, Tobin surveys for you, Pip delivers for you.
- **The Lantern Road** — 0 → 40 lamps, mill to square to lake. *(Grafted from Lanternwick's Wick Line, which was the best ambient scoreboard in the batch and the thing this spine was missing.)* Every act lights a stretch. At night, from the homestead window, you can see exactly how far the game has come and how far it hasn't. A lit lamp is physical proof two people cooperated: the cozy lane places the post, the tech lane runs the duct. The fortieth lamp is the second-to-last quest in the pack.

### The Town Anchor — the terrain-independence rule
In Act I the players place **two waystones**:
- **Homestead Waystone** — wherever they want to live.
- **Town Anchor Waystone** — any flat-ish spot within about 60 blocks of home.

KubeJS records the Town Anchor coordinates on placement. From then on, **every** structure, NPC, market stall, sign, lamp post, greenhouse and festival table in the game is placed at a fixed offset from that anchor by quest-reward commands. The valley grows outward from a spot the players chose. It fits any seed, and it always looks intentional.

**The levelled-pad rule** *(grafted from Lanternwick).* No finale ever calls `/place` on a jigsaw structure onto live terrain — that is the most fragile command in the set and it looks wrong when it half-works. Every structure command chain runs in this order:

1. `/fill` an air box above the pad (clear).
2. `/fill` a stone-and-dirt pad at anchor+offset (level).
3. `/fill` walls and `/setblock` the details on top of the known pad.

Coordinates are already solved by the anchor, so this is arithmetic, not pathing. It works on a cliff, in a swamp, on a beach.

### The season rule — stated, not assumed
The acts **are** the seasons, so the calendar cannot be allowed to drift out of phase with the story.

- **Config:** Serene Seasons `season_cycle_length` is set to **48** (12 in-game days per season, 4 per sub-season). Short enough that a season is felt in an evening or two of play; long enough that it isn't a strobe.
- **Every act finale force-sets the season** as the first command in its chain: `/sereneseasons setseason <spring|summer|autumn|winter|spring>`. This is not optional and it is not implicit. The finale is what turns the calendar.
- **Nothing in the pack ever waits on weather.** If a quest wants snow, the finale before it set winter. No quest text ever says "when winter comes."

### Keeping a non-creative player oriented
This is the single most important constraint in the pack, so it is written as rules, not intentions.

- **A moving world border, announced as story.** Act I: 1,500. Act II: 3,000. Act III: 6,000. Act IV: 10,000 plus the Nether. Act V: open. Every expansion arrives as a line from a resident — *"Tobin walked the north ridge and came back with a map and a cold. It's safe to the cairn."* — never as a technical notice.
- **One chapter visible.** FTB Quests shows exactly one unlocked chapter. Completed chapters collapse into **Memories** (read-only). Future chapters are **hidden, not greyed**, so there is never a wall to feel behind on.
- **One pinned objective.** Every quest reward auto-pins the next quest in that lane. The book opens to one sentence in plain language. (Two pins when a team has more than one member — one per lane.)
- **Every task is literal.** No quest ever says "build a base" or "make it nice." It says: *"Place a bed, a door, two windows and a wall lantern."*
- **Decoration quests ship the blocks** *(grafted from Lanternwick — the single best accommodation written in any draft).* Every decorating quest gives an exact checklist AND the reward packet contains those exact blocks, **delivered by the quest that unlocks it, before the task**. She is arranging, never sourcing. This is the rule that prevents the "here is an empty lot, make it nice" moment that makes non-builders quit.
- **Waystones are given, never crafted.** Every named place is a waystone, handed over or placed by the quest that introduces it. Walking somewhere twice is a design bug.
- **Explorer's Compass is never open-ended.** Every quest that uses it names the structure in the quest text and hands over a compass already set to it. There are exactly **three** structure hunts in the whole pack (Q67, Q81 twice) and each one is a named destination, never "pick any ruin."
- **Torchmaster in Act I, before anything else.** The homestead, the coop and the pasture each get a Feral Flare Lantern as a quest reward. Nothing spawns where she lives. Ever. Night is atmosphere.
- **Corpse and Lootr are named safety nets.** A death is never a lost run — your stuff waits in a grave you can walk back to. A shared structure is never already-looted — Lootr gives every player their own copy of every chest.
- **No timers, no fail states, no failable festivals.** The festival waits for the players. Missing one is impossible. The pressure is a calendar, not a threat.
- **Build detection is on the honour system.** FTB Quests cannot verify "you built a shelter." Those are Checkmark tasks with a picture in the quest text. This is stated here so nobody wastes a week trying to detect a cottage. Item-delivery and item-craft tasks carry the real gating.

---

## 4. Cast

Eight residents plus Josie, who is dead and does all her talking through the journal. Every NPC is Easy NPC: a name, a skin, and dialog that swaps by KubeJS stage. Each has a **three-beat arc that closes on screen**, and each arc is a *named quest chain* — which is also how Standing works (see §5).

### Josie Kettle — the voice in the book — **both**
Your great-aunt. Deceased. Speaks only through the Patchouli journal, which gains a chapter at each act finale.
**Wants:** for the valley not to end with her.
**Arc:** (1) A capable, funny old woman leaving instructions. (2) The handwriting gets shakier and the plans get *more* ambitious, not less. (3) The reveal — see §7, Act III — and then a last page that is not a plan at all.

### Marnie Ashcombe — innkeeper, keeper of the Hearth — **cozy**
Fifties, flour on her sleeves, talks to you like you already live here. Ran the inn with Josie and has swept the building every day since it closed, out of habit.
**Wants:** to serve a meal to a full room again.
1. *Spring* — comes up the hill because she saw smoke from your chimney for the first time in years, and brings bread she baked for nobody.
2. *Autumn* — admits she has been cooking for one and throwing half of it away. The Harvest Supper is the first meal she cooks to a real headcount.
3. *Winter* — her stores run out during the cold snap and she lets you feed **her**, which is the hardest thing she does all year. Afterwards she stops calling the inn "Josie's place."

### Bram Tolliver — millwright — **tech**
Sixties, grease-stained apron, keeps every broken part he has ever owned in labelled crates. Gruff for about four minutes.
**Wants:** to see the wheel turn again before he gets too old to fix it.
1. *Spring* — won't accept help, will accept "hold this." Teaches Create by making you do it while he narrates.
2. *Autumn* — hands over Josie's schematics, which he could never make work, and stops pretending he's the smartest engineer in the valley.
3. *Winter* — refuses to leave the mill during the cold snap. Has to be fetched, with cocoa, essentially against his will — and is the one who pulls the lever.

### Oda Vance — storekeeper, bounty board, quartermaster — **both**
Forties, ledger under one arm, opinions about everything. Reopened the store on the strength of a rumour that somebody moved into the Kettle place.
**Wants:** a reason to reorder stock. Customers.
1. *Spring* — sells you almost nothing because she has almost nothing, and posts the first bounty out of embarrassment.
2. *Autumn* — the rail line reaches town and her shelves fill; she starts special-ordering for individual residents by name.
3. *Second spring* — the books balance for the first time in eleven years and she hands you the ledger, which for Oda is a hug.

### Nella Brightwater — fisher and ferryman — **cozy**
Thirties, permanently damp, unbothered. Lives on a boat she keeps meaning to repair.
**Wants:** the docks rebuilt so the lake is a place people go, not a place she hides.
1. *Summer* — teaches fishing and the lake's moods; gives you your first good rod.
2. *Summer* — the Lantern Float is her idea and she is visibly terrified nobody will come.
3. *Winter → spring* — the lake freezes and she loses her livelihood for a season. The greenhouse gives her work, and she discovers she likes growing things more than she has ever admitted to liking anything.

### Halden Root — herbalist and brewer — **both**
Quiet, ancient-seeming, probably fifty. Hedge garden and a still. Knew Josie best, and knows what is behind the cellar door.
**Wants:** to finish the book he and Josie started, and to stop being the only person carrying her secret.
1. *Spring* — trades tea for stories; gives you the herbal starts.
2. *Autumn* — reads Josie's shorthand off the Kettle Plate and opens the cellar door. He has been dreading this for four years and does it anyway.
3. *Winter* — keeps the whole valley from getting sick during the cold snap; admits he stayed because Josie asked him to, and that he's glad.

### Tobin Gale — prospector — **tech**
Twenty-three, over-caffeinated, unreasonably delighted by rocks. Showed up chasing a survey report and never left.
**Wants:** to be taken seriously by somebody who owns a pickaxe.
1. *Summer* — nobody believes his survey. He is right about everything and terrible at explaining it.
2. *Autumn* — his core samples locate the deep copper and iron, and Bram says "good work" out loud.
3. *Second spring* — he calls in the quarry rig. It is the biggest thing he has ever been responsible for and he is very calm about it, which fools nobody.

### Wisp — Ribbit forager — **cozy**
A frog-person from the reed village downstream. Short, cheerful, slightly wrong sentences. Carries too much.
**Wants:** the marsh village and the town to be one place instead of two.
1. *Spring* — first contact; brings a basket of things you cannot identify, all of which are delicious.
2. *Summer* — moves into a stilt house at the water's edge, which the town builds for them.
3. *Winter* — brings the entire reed village in to shelter at the inn. The two settlements never separate again.

### Pip Ashcombe — Marnie's nephew, nine — **cozy**
Runs everywhere. Names everything. Has a duckling by the end of Act I and it is the pack's mascot.
**Wants:** a pet, then a job.
1. *Spring* — gets the duckling and names it after you, or after a food.
2. *Autumn* — appoints himself the town's courier; his delivery quests are the short, sweet filler between big beats.
3. *Winter → spring* — is the one who notices the Hearth has gone out, and the one who rings the bell at the end. Gets a plushie of his duck.

---

## 5. The two lanes and how they gate each other

**Cozy lane (his wife's spine):** cook → feed → keep animals → fish → plant by season → decorate → meet people → celebrate. Every quest names an item and a place. Every reward is something you can look at, eat, or hug.

**Tech lane (Josh's spine):** Create → Thermal → Applied Energistics 2 → Bigger Reactors → QuarryPlus, in that order, each gated by a KubeJS stage granted at an act finale, and each tier handing over the boring middle materials while asking for the interesting one.

They are **braided, not parallel**. Roughly every third quest in each lane consumes something the other lane produced. A solo player does both. A couple splits naturally. A friend picks either.

### The gates, concretely

1. **Seasoned Oak Boards → the first water wheel.** *(Hour one.)* Create's Water Wheel recipe is stage-gated behind **Seasoned Oak Boards**, which exist only if somebody fires Marnie's bread oven and dries green planks in it overnight (Q15). Bram literally cannot start until the inn's oven is lit. She unblocks him before he has mined anything.
2. **Washed Silica → the first Thermal Machine Frame.** Machine Frames are gated behind **Washed Silica**, made from lake sand only obtainable by dredging with Nella (Q26) and washing it under a Create fan. No fishing trip, no Pulverizer.
3. **Powered kitchen → Cooking for Blockheads.** The Fridge, Sink and Milk Jar are gated behind a charged Thermal Energy Cell within 12 blocks of the inn (Q47). Her dream kitchen is his first *look what I did for you*, and the fridge opens the whole preserved-food branch Act IV depends on.
4. **Spring Water → certus quartz.** AE2 certus seeds only grow in water drawn from Halden's spring, which requires the cozy herbal line (Q41). AE2 does not start until the herbalist likes you.
5. **Reactor heat → winter crops.** The greenhouse grows out of season because the reactor's coolant loop feeds its heaters (Q72), which unlocks Serene Seasons' own **Greenhouse Glass** recipe. Not a bespoke growth override — the mod already ships the mechanism, so the reactor unlocks a *recipe*, not a hack. This is the pack's thesis: **the reactor is the reason food exists in January, which is the reason nobody leaves in February.**
6. **Waste heat → the bathhouse.** *(Grafted from Copperbell.)* The coolant loop's other outlet is a bathhouse behind the inn. The endgame machine is domestically useful, not just numerically bigger.
7. **The AE2 terminal → the bounty board.** *(Grafted from Copperbell — the best single anti-grind idea in the batch.)* Q53 links an ME terminal to Oda's board. From that quest onward, every delivery bounty and every "bring X to Y" quest auto-fills from network stock and becomes **one click**. His most abstract build becomes her biggest quality-of-life jump, in the same act, and he gets to watch it happen.
8. **The spare wireless terminal.** *(Grafted from Lanternwick.)* Q52 hands the cozy player a second wireless terminal — one act before the decorating marathon. She types "lantern" instead of rummaging through fourteen chests.
9. **Valley Scrip → tech skip-tokens.** Bounties and deliveries pay **Valley Scrip**. Scrip's only use is Oda's counter, and her counter sells: pre-made Andesite Casings, crates of Redstone Servos, spare Machine Frames, reactor casing bundles, and — in Act V — **the Works Deed that unlocks QuarryPlus**. Cozy labour deletes tech grind continuously, as a standing supply chain rather than three well-chosen rewards.
10. **Trains → the decor catalogue.** Oda's full stock (Macaw's, Handcrafted, Supplementaries variants; animals; rare seeds) unlocks in tiers when the Steam 'n' Rails line reaches town in Act III — a tech build.
11. **The Lantern Road.** Every stretch needs the cozy lane to place the posts and the tech lane to run the duct. Forty lamps, both hands.

### Standing — how the deed gate actually works
The *seasons* draft gated QuarryPlus behind "max friendship with six of eight residents." There is no reputation mod in this pack and Easy NPC has dialog, not relationships. Building a friendship system with tiers, gifts and persistent per-team data is the largest custom build anyone proposed, and it would have gated Josh's biggest toy behind a buggy counter.

**Replaced.** **Standing** is simply *how many named resident quest chains your team has completed.* It is a count of completed quest IDs — FTB Quests already tracks that, KubeJS just reads it. No scoreboard, no UI, no gift mechanic, no persistence layer.

- Marnie's chain closes at Q60. Wisp at Q59. Halden at Q62. Pip at Q63. Bram at Q73. Tobin at Q75. Nella at Q77. Oda at Q85.
- **The Works Deed (Q86)** costs **150 Valley Scrip** at Oda's counter and requires **six of eight chains closed**. Both conditions are things a player can see in their own quest book, and the Scrip half means the tech player can buy his way toward it himself if he wants to. The braid survives; the code does not.

---

## 6. The five acts

Format: `Qn. Title | lane | task | reward | depends on`
Lanes: **C** cozy · **T** tech · **B** both.
**Counts:** Act I = 19, Act II = 18, Act III = 19, Act IV = 19, Act V = 16. **Total = 91**, numbered flat Q1–Q91, dependencies walked.

---

## ACT I — SPRING: *The Thaw*
**Beat.** You arrive at a cold house in a valley that used to be a town. One neighbour sees your chimney smoke, comes up the hill, and decides you're staying. By the end of spring there are five people in the valley instead of one, the mill turns, and there is a door in your cellar you cannot open.

**Goal, one sentence:** *"Make the old Kettle farm livable and wake the town up in time for the Thaw Fair."*
**Border:** 1,500. **Tech tier:** Create, andesite through sawmill. **Lamps:** 0 → 6.

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | The Letter and the Kettle | B | Right-click the Letter in your inventory and read all four pages. | Josie's Journal (Patchouli), the Copper Kettle, Homestead Waystone, 16 cooked food, 16 torches, a Torchmaster Feral Flare Lantern | — |
| Q2 | Somebody Left the Kettle On | B | Take the Homestead Waystone out of your bag and place it anywhere you'd like to live. Name it **Home**. | Bed, 64 oak planks, a Macaw's cottage door, 4 Macaw's windows, waystone registered to your map | Q1 |
| Q3 | Four Walls and a Door | C | Build a shelter around your waystone: **1 door, 2 windows, 1 bed, 1 wall lantern.** All four items are in your bag already. | Handcrafted table + 2 chairs, wool rug, 2 flower boxes | Q2 |
| Q4 | Nothing Gets In | B | Place the Feral Flare Lantern inside your shelter. | Nothing hostile spawns near home from now on. 2 spare lanterns for later pens | Q3 |
| Q5 | The Door Under the House | B | Dig out the collapsed cellar under the Kettle house (the floor hatch is marked). | You find a sealed iron door with no handle, and Josie's handwriting chalked on it: *"Not yet. — J.K."* Cellar Waystone, a crate of Josie's tools, **Journal Entry 1** | Q2 |
| Q6 | Put the Kettle On | C | Hang the Copper Kettle over a campfire and cook one meal in a Cooking Pot. | Cooking Pot, Skillet, Farmer's Delight knife, 3 sacks of assorted seeds | Q3 |
| Q7 | Where the Square Goes | B | Place the Town Anchor Waystone on flat-ish ground within 60 blocks of home. This is where the town will be. | Anchor recorded. A stone path is laid from your door to the anchor and **the first two lamp posts go up (2/40)** | Q6 |
| Q8 | Chimney Smoke | C | Sleep one night after placing the Town Anchor. | **Marnie arrives.** The inn shell is built at the anchor. 8 loaves of Marnie's Bread, the Inn Waystone | Q7 |
| Q9 | Three Beds of Dirt | C | Till a 3×9 patch near your house and plant the wheat, carrots and potatoes from Marnie's sack. | Watering can, 16 bone meal, straw hat, scarecrow | Q8 |
| Q10 | Two Hens and a Rooster | C | Lead 2 chickens home with seeds and pen them. **Fence, gate and trough are in the reward packet from Q9.** | Chicken feed, nesting box, a Feral Flare Lantern placed over the coop | Q9 |
| Q11 | Pip and the Egg | C | Bring 6 eggs to Marnie at the inn. | **Pip arrives.** You are given a **Duckling** to name and keep. Pip's courier board unlocks | Q10 |
| Q12 | The Man at the Broken Mill | T | Walk to the mill plot marked on your map and talk to Bram. | **Bram arrives.** Create wrench, goggles, **12 iron ingots and 24 andesite** | Q8 |
| Q13 | Eight Alloys, No More | T | Make 8 Andesite Alloy from exactly what Bram gave you. | **Mechanical Press (pre-made)**, 8 cogwheels, 8 shafts | Q12 |
| Q14 | Turn It By Hand | T | Build a Millstone, attach a Hand Crank, and grind 16 wheat into flour for Marnie. | Encased Fan, 3 Andesite Alloy, saw-blade parts | Q13 |
| Q15 | The Green Boards | C | Fire the inn's bread oven for Marnie, then leave 32 oak planks inside overnight. | **Seasoned Oak Boards ×32** and the `seasoned` stage — this is what unlocks Water Wheels | Q8, Q14 |
| Q16 | Water Finds a Way | T | Build 2 Water Wheels on the stream with the Seasoned Boards and drive the Millstone off them. | **Mechanical Saw (pre-made)**, Basin, Mechanical Mixer, Bram's crate: 32 Andesite Alloy | Q15 |
| Q17 | Sawdust and Shingles | T | Cut 128 boards on the Saw and hand Bram 64 of them for the market stalls. | Macaw's roof kit ×3, 4 planters, the `market_stalls` stage | Q16 |
| Q18 | Marnie's Kitchen | C | Build a Cooking for Blockheads Kitchen Counter, Sink and Oven in the inn, then cook 3 different dishes. | Cookbook, fruit basket, 5 recipes learned automatically, Handcrafted cupboard set | Q15 |
| Q19 | **The Store Reopens** | B | Sweep out the general store and bring Oda 16 flour, 8 eggs and 8 wool. | *Act finale* | Q17, Q18 |

---

## ACT II — SUMMER: *The Long Days*
**Beat.** The town is awake and immediately too small. Summer is abundance you can't store, water you can't move, and light you don't have. Nella comes back to the lake, Halden opens the hedge garden, and the mill stops being a mill and starts being a workshop.

**Goal, one sentence:** *"Make summer's abundance usable — power the workshop, work the lake, and throw the town a party on the water."*
**Border:** 3,000. **Tech tier:** Create advanced → first Thermal. **Lamps:** 6 → 12.

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q20 | Frogs in the Reeds | C | Take the Explorer's Compass Marnie gives you — it is **already set to Ribbit Village** — follow it, and trade with the frog folk. | **Wisp befriended**, basket of marsh produce, Sophisticated Backpack (one upgrade) | Q19 |
| Q21 | The Beached Boat | C | Follow the marker to the lake and talk to the woman fixing a boat that doesn't need fixing. | **Nella arrives.** Aquaculture Iron Rod, tackle box, Lake Waystone | Q19 |
| Q22 | Something With Fins | C | Catch 10 fish of any kind and cook one in the Skillet. | 16 bait, Fish Bag, 2 recipes, Nella's hat | Q21 |
| Q23 | The Hedge and the Still | C | Bring Halden 8 flowers of three different colours from around the valley. | **Halden arrives**, herb garden placed, HerbalBrews starter kit, tea set | Q19 |
| Q24 | Vines on the South Slope | C | Plant a Vinery grape trellis and water it twice. | 12 grape starts, wine press, Handcrafted wine rack, `vinery` stage | Q23 |
| Q25 | Bees, Cows, and a Sheep Named Later | C | Build a pasture and move in 2 cows and 2 sheep. **Fence, gate, trough and lantern supplied.** | Milk churn, shears, 16 wool, Pasture Waystone, sheep plushie | Q21 |
| Q26 | Dredging the Shallows | C | Ride out with Nella and gather 3 stacks of sand from the lake bed. | Nella's oar (swim speed), **192 Lake Sand**, `dredged` stage | Q22 |
| Q27 | The Rock Kid | T | Talk to the young man camped by the copper outcrop with too many notebooks. | **Tobin arrives**, Geolosys prospector's pick, 3 survey maps already marked | Q19 |
| Q28 | Read the Rock | T | Use Tobin's pick on the 6 spots he marked and find the copper cluster. | Cluster marked on your map, 32 copper ingots, **Vein Mining unlocked** | Q27 |
| Q29 | A Wheel That Doesn't Freeze | T | Build a Windmill Bearing with 8 sails on the mill roof so the workshop keeps running when the stream runs low. | 6 gearboxes, clutch, gearshift, 3 Mechanical Crafters | Q16 |
| Q30 | Wash the Sand | T | Wash the Lake Sand under an Encased Fan over water to make **Washed Silica**. | Washed Silica ×64, `silica` stage (unlocks Thermal Machine Frames), 2 Deployers | Q26, Q29 |
| Q31 | Josie's First Schematic | T | Take Bram's crate of Josie's papers and craft your first Machine Frame. | **2 spare Machine Frames**, Redstone Furnace (given), 32 Fluxduct | Q30 |
| Q32 | The Pulverizer | T | Build a Thermal Pulverizer and run 64 iron ore through it. | Doubled ore forever, Thermal Sawmill (given), 8 Redstone Servos, Stirling Dynamo | Q31 |
| Q33 | The Long Bench | T | Build a proper workshop room at the mill: 6 Storage Drawers, a controller, 3 Sophisticated barrels. | 6 drawer upgrades, controller remote, **Backpack tier 2 for every player** | Q32 |
| Q34 | The Lantern Road, First Stretch | B | Place 10 lamp posts along the marked line from the mill to the square, and power two of them from the Redstone Furnace with Fluxduct. **All posts and duct supplied.** | **Lamps 12/40.** Hostile spawns suppressed along the whole road | Q32, Q19 |
| Q35 | A House on Stilts | C | Build Wisp a stilt house at the water's edge: **6 Macaw's fence sections, a Handcrafted bed, a door, 2 windows, 3 lanterns — all supplied.** | **Wisp moves to town.** Marsh trade opens (rare seeds, frog-village decor), Ribbit plushie | Q20, Q25 |
| Q36 | Two Hundred Lanterns | C | Craft 24 paper lanterns with Marnie and Pip for the float. | Lantern crate, festival clothes, 20 Valley Scrip | Q35 |
| Q37 | **The Bounty Board Fills Up** | B | Complete any 3 bounties from Oda's board. | *Act finale* | Q33, Q36 |

---

## ACT III — AUTUMN: *The Harvest Debt*
**Beat.** The valley finally produces more than it eats — and Oda opens the ledger and shows everyone the truth: at this rate the town runs out of food and fuel in February. Autumn is where cozy work becomes *preservation* and tech work becomes *storage and logistics*. And Halden finally reads what is written on the Kettle Plate, and opens the door under your house.

**Goal, one sentence:** *"Fill the granary and finish Josie's storage system before winter — and feed the whole town at the Harvest Supper."*
**Border:** 6,000. **Tech tier:** Thermal full → AE2 basic. **Lamps:** 12 → 22.

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q38 | Oda Opens the Ledger | B | Talk to Oda at the store. She counts the town's stores out loud. | The winter checklist (in-book), 30 Valley Scrip, granary blueprint | Q37 |
| Q39 | The Granary | C | Build the granary at the square: **12 Storage Drawers on a Handcrafted frame under a Macaw's roof — every block supplied.** | Drawers arrive pre-filled with the town's current stock, Granary Waystone, `granary` stage | Q38 |
| Q40 | Autumn Sowing | C | Plant the autumn seed pack — pumpkin, beetroot, squash, cranberry. These are the only things that grow now. | Seasonal almanac (in-book: what grows when), second scarecrow, 3 recipes | Q38 |
| Q41 | Halden's Spring | C | Follow Halden up to the spring above the hedge garden and fill 3 bottles of **Spring Water**. | Spring Water ×3, `springwater` stage (unlocks AE2 certus seeds), herbal tea set | Q40 |
| Q42 | Preserves and Pickles | C | Make 12 preserved foods: pies, pickles and jam from the Bakery and Farm & Charm kits. | 4 preserving crocks, pie safe, **Cooking for Blockheads Fridge blueprint** — deliberately unusable until there's power | Q40 |
| Q43 | The Bakery Line | C | Bake 8 loaves, 4 pies and 4 cakes in one session in the inn kitchen. | Bakery display set, apron, cake plushie, Marnie's autumn beat | Q42 |
| Q44 | Smoked, Salted, Hung | C | Build a smokehouse with a Nether's Delight rack and smoke 16 meat. | 32 cured meat, smokehouse decor, `larder` stage | Q42 |
| Q45 | What Tobin Found | T | Take Tobin's 3 core samples to the marked hillside and open the copper adit. | Deep copper + iron clusters revealed, Vein Mining tier 2, and in the Lootr chest: an Artifact and **the Kettle Plate** | Q28 |
| Q46 | Induction | T | Build a Thermal Induction Smelter and alloy 32 bronze and 32 electrum. | 64 alloy stock pre-made, Centrifugal Separator (given), 64 Fluxduct | Q45 |
| Q47 | The Cell on the Wall | T | Charge a Thermal Energy Cell off your dynamos and run Fluxduct to the inn. | **Kitchen power stage** — Fridge, Sink and Milk Jar now craftable. One spare Energy Cell | Q46, Q42 |
| Q48 | Rails to the Road | T | Lay a Steam 'n' Rails line from the mill to the square with a Create train station. | **Train kit: engine and 2 cars, pre-made.** Station bell, `trainline` stage | Q46 |
| Q49 | Oda's Wagon Comes In | B | Run the train to the square and unload Oda's first proper delivery. | **Oda's catalogue tier 3** — the full Macaw's / Handcrafted / Supplementaries decor list, seeds and animals, purchasable with Scrip | Q48 |
| Q50 | Quartz in Water | T | Plant Certus Quartz Seeds in Halden's Spring Water and let them grow. | 32 certus, AE2 Inscriber (given), meteorite compass already pointing | Q41, Q47 |
| Q51 | The First Terminal | T | Build an ME Drive with 2 storage cells and a terminal in the mill workshop. | 4 more cells, import/export bus set, `ae_basic` stage | Q50 |
| Q52 | Everything In One Place | T | Storage-bus the granary's drawers onto the network so the whole town's stock shows on one screen. | Wireless Terminal + charger, **a second wireless terminal to hand your partner**, Oda's ledger now auto-updates in-book | Q51, Q39 |
| Q53 | The Order Board | T | Put an ME terminal beside Oda's bounty board and pattern-link it to the network. | **Every delivery bounty and "bring X to Y" quest from here on auto-fills from network stock — one click.** 60 Scrip | Q52 |
| Q54 | The Plate in the Door | B | Take the Kettle Plate from the adit to Halden. He has been able to read Josie's shorthand for four years and has been avoiding it. | The cellar door turns one quarter and stops. **Journal Part Two.** Bigger Reactors recipes *revealed but not craftable* | Q45, Q43 |
| Q55 | What Josie Actually Built | B | Go down into the cellar and read the wall. | **The reveal** (see §7). Works Waystone, Josie's steel tool chest, her original reactor blueprint framed as a decor block | Q54 |
| Q56 | **Setting the Table** | C | Place a 12-seat Handcrafted long table in the square with a place setting for every resident. **Table, settings and centrepiece supplied.** | *Act finale* | Q43, Q44, Q49, Q55 |

---

## ACT IV — WINTER: *The Longest Night*
**Beat.** The crisis, played warm and never grim. Nothing kills anybody. What happens is that the valley gets **cold and dark and boring** — the crops stop, the lake freezes, Nella loses her work, Marnie's stores run down, the Ribbits can't stay in the marsh, and the whole town crowds into one building. The fix is the thing Josie shut down: the Works becomes a reactor, the reactor heats a greenhouse and a bathhouse, and the valley grows food in January for the first time in its history.

**Goal, one sentence:** *"Keep everyone warm and fed through winter, and finish Josie's power plant so the valley never has to go dark again."*
**Border:** 10,000 + Nether. **Tech tier:** AE2 autocrafting → Bigger Reactors. **Lamps:** 22 → 39.

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q57 | The Hearth Goes Out | C | Sleep one night after the Supper, then follow Pip down to the inn. | Everyone gathers. The Winter chapter opens. 64 firewood, a warm cloak, the cocoa recipe | Q56 |
| Q58 | Firewood for Eight Houses | C | Deliver 16 firewood bundles each to Marnie, Halden, Nella and Oda. | Each gives something back — blanket, tonic, smoked trout, lamp oil. Sleigh bells | Q57 |
| Q59 | The Reed Village Comes In | C | Take Wisp's boat downstream and bring the Ribbits back to the inn. | **4 Ribbit residents added to town**, frog-village decor set, **Wisp's chain closes** | Q58 |
| Q60 | Soup for a Full Room | C | Cook one stew big enough for twelve and serve it at the inn. | **Marnie's chain closes.** Her recipe book (10 recipes). The Hearth relights | Q59 |
| Q61 | Ice Fishing | C | Cut a hole in the frozen lake and catch 8 winter fish. | Ice auger, winter tackle, 2 trophies, Nella's winter beat | Q59 |
| Q62 | Halden's Rounds | C | Brew 8 winter tonics and deliver one to every resident. | **Halden's chain closes.** His half of Josie's recipe book, medicine cabinet, `healthy` stage | Q58 |
| Q63 | Pip's Winter Job | C | Complete 5 of Pip's courier deliveries in one day. *(One click each now — the order board fills them.)* | **Pip's chain closes.** The duckling grows up. **Duck Plushie.** Courier satchel | Q58, Q53 |
| Q64 | The Cold Frame | C | Build the greenhouse shell at the square: **glass, 6 Macaw's windows, a Handcrafted door, 8 planters — supplied.** | Shell registered at the anchor. **Nothing grows yet. It's too cold.** | Q60 |
| Q65 | Open the Works | T | Clear the collapsed adit into Josie's works and set a waystone inside. | Works interior lit, Josie's steel tools, a Lootr Artifact, `drilling` stage | Q55 |
| Q66 | The Grid | T | Run Fluxduct from the mill to the Works and install 2 more Energy Cells. | 2 pre-made cells, Thermal servo/filter set, `grid` stage | Q65 |
| Q67 | The Second Plate | B | Explorer's Compass — **already set to a named structure** — go, open the vault chest, bring back the last Kettle Plate. *(This is the second and final plate hunt in the pack.)* | Josie's turbine notes: **Bigger Reactors recipes now craftable.** 2 Artifacts, a waystone to place at the site | Q65 |
| Q68 | Autocrafting | T | Set up 8 AE2 crafting patterns and a Molecular Assembler so the network builds the boring parts for you. | Crafting CPU housing and 4 co-processors — **you build the CPU, the network builds everything else.** 4 ME Interfaces | Q66, Q51 |
| Q69 | Yellorium | T | Follow the deep survey to the yellorite and process 64 ore through the Pulverizer and Smelter. | 128 yellorium ingots; **64 reactor casings auto-crafted by your own network** while you walk back | Q68, Q67 |
| Q70 | Build the Vessel | T | Assemble the reactor: casing shell, controller, fuel rods, control rods, access port. | Reactor computer port, redstone port, Josie's blueprint framed | Q69 |
| Q71 | The Turbine | T | **A problem, not a recipe.** Bram's crate contains a fixed budget of rotor blades, coils and casing. Build a turbine that holds 1,800 RPM under load without exceeding it. | `reactor_ready` — the lever is live. A tuning page in the journal with Josie's own numbers pencilled in the margin | Q70 |
| Q72 | The Coolant Loop Goes Somewhere | B | **Josie's rule: the waste heat goes to the town, not the sky.** Run fluid and Fluxduct from the reactor to 6 greenhouse heaters and the bathhouse tank behind the inn. | Heaters live, bathhouse built and steaming, **Serene Seasons Greenhouse Glass recipe unlocked** | Q71, Q64 |
| Q73 | Bring Bram | C | Go and get Bram from the mill. He will say no. Bring him anyway. Bring cocoa. | **Bram's chain closes.** His father's wrench. The lever quest unlocks | Q60, Q71 |
| Q74 | The Lantern Road, Second Stretch | B | Place the rest of the posts — mill to square to lake — and wire them to the grid. **Every post and every duct supplied.** | **Lamps 39/40.** One post is left bare on purpose: Josie's porch | Q66, Q34 |
| Q75 | **Tobin's Numbers** | T | Let Tobin run the safety check: verify fuel, coolant flow and control-rod insertion in the reactor UI. | *Act finale* — **Tobin's chain closes** | Q73, Q72, Q74 |

---

## ACT V — SECOND SPRING: *Founder's Day*
**Beat.** The valley survived a winter for the first time in a decade, and people start arriving on their own. The victory lap has teeth: the town formally re-founds itself, the deed to the Works is bought and signed over, and the quarry goes in — not as a strip mine, as the town's public works. Every arc closes on screen.

**Goal, one sentence:** *"Re-found the town: finish the square, balance the books, and sink the quarry that pays for the next hundred years."*
**Border:** open at the finale. **Tech tier:** reactor scale-up, full AE2, QuarryPlus. **Lamps:** 39 → 40.

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q76 | Thaw, Again | C | Sleep one night after the Longest Night and walk the square with Marnie. | Spring seed pack, flower crates, `year_two` stage, the noticeboard updates | Q75 |
| Q77 | Greenhouse Glass | C | Glaze the cold frame with Greenhouse Glass and grow 4 out-of-season crops in it at once. | **Nella's chain closes** — she takes the gardener's job. Rare seeds from Wisp, master gardener's kit | Q76, Q72 |
| Q78 | Paint the Town | C | Decorate the square: 12 planters, 6 awnings, 4 benches, 8 flower boxes. **Every block is in this quest's opening packet — nothing to gather.** | Oda's full catalogue goes free, `square_finished`, a framed map of the town for your wall | Q76 |
| Q79 | Eight Favourite Meals | C | Cook and deliver each resident's favourite dish. The book lists all eight. | Commemorative dish set, the Feast recipe, a warm line from each of them | Q78 |
| Q80 | The Fishing Derby | C | Catch 6 different Aquaculture species and mount 3 of them on the inn wall. | Trophy mounts, Nella's top-tier rod, fisher plushie, 50 Scrip | Q77 |
| Q81 | Out Past the Ridge | C | Explorer's Compass, **two named destinations**, one Artifact from each. | 2 Artifacts, a Lootr luck upgrade, 2 waystones to place, travel journal pages | Q78 |
| Q82 | Deeper and Darker | B | Go down with Tobin, once, into the deep dark, and come back with an echo sample. | Deep survey data — this is what sites the quarry. Warding lamp, Corpse-recovery token | Q81 |
| Q83 | Reactor, Scaled | T | **A problem, not a recipe.** Hit the town's stated winter power budget with a second turbine, without exceeding the fuel burn Tobin signed off on. | `big_power`, Thermal augment set, live energy readout in the journal | Q75 |
| Q84 | Everything, Everywhere | T | Full network: 2 Crafting CPUs, wireless access across the whole town, and a subnet that keeps Marnie's pantry stocked forever. | Wireless boosters, a terminal for every player, Oda's stock syncs to the network | Q83, Q68 |
| Q85 | The Ledger Balanced | B | Pay off the town's winter debt at Oda's counter: **200 Valley Scrip.** | **Oda's chain closes.** She hands you the ledger. Quartermaster's chest | Q79, Q80 |
| Q86 | The Works Deed | B | Buy the deed at Oda's counter: **150 Valley Scrip and six of eight resident chains closed.** | **The Deed — QuarryPlus is now craftable.** The residents vote; Bram signs as witness | Q85, Q82 |
| Q87 | Sink the Shaft | T | Place the QuarryPlus rig and its markers on the site Tobin surveyed, and power it from the reactor. | Quarry running. Pump and filler modules. **Tobin's arc closes** | Q86, Q83 |
| Q88 | The First Load | T | Route the quarry's output into the ME network and let it run one full cycle. | `town_provides` — Oda's store now restocks itself from your network, permanently | Q87, Q84 |
| Q89 | A Bell for the Square | C | Cast a bell from the quarry's own copper and hang it in the finished square. | Bell placed. Every resident comes out. **Pip becomes the bell-ringer — his arc closes** | Q78, Q88 |
| Q90 | The Last Lamp | C | Walk up to Josie's porch and put the fortieth lamp on the bare post. | **Lamps 40/40.** Josie's Lantern (never burns out), a memorial bench, **Journal Entry 5** | Q89, Q74 |
| Q91 | **The Feast** | C | Cook the Feast: one dish from every resident, on the long table, with the Hearth lit. | *Act finale* | Q79, Q90 |

---

## 7. Finale events

**Universal rules for every finale chain**
1. **First command is always the season.** `/sereneseasons setseason <season>`. The finale turns the calendar; the calendar never turns on its own between acts.
2. **Levelled pad, then build.** Clear-fill air → fill pad → fill walls → setblock details. All at Town Anchor offsets. **Zero `/place` calls anywhere in the pack.**
3. **Residents are despawned and re-summoned** at their new positions with new Easy NPC dialog, rather than pathed. Pathing across arbitrary terrain does not work; teleporting does.
4. **One per world.** Finales are world stages, not team stages. A second team never re-runs them (see §9).
5. **Every finale hands both lanes the entire opening bill of materials for the next act.** Nobody starts an act by gathering.

---

### Act I finale — **The Thaw Fair** *(triggered by Q19)*
- `/sereneseasons setseason spring` · `/time set day` · `/weather clear`
- Title: **"The Thaw Fair"** / subtitle: *"Spring, Year One."* Soft playsound, one bell.
- Pad-and-fill the market square at the anchor: four stalls, a stone-and-flower plaza, Supplementaries bunting, lamp posts **3 through 6**, and a Handcrafted long table.
- Summon Marnie, Bram, Oda and Pip at fair positions with festival dialog. Pip's duckling follows him.
- Every player gets a **Fair Basket**: festival food, a plushie of their choosing, a Supplementaries sconce set, and 25 Valley Scrip.
- Set the **Town Square Waystone** in the middle of the square.
- Stage `act2`. Border → 3,000, announced by Tobin: *"Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation."*
- **Journal Entry 2** unlocks.

### Act II finale — **The Midsummer Lantern Float** *(triggered by Q37)*
- `/sereneseasons setseason summer` · `/time set midnight` · `/weather clear`
- Title: **"The Lantern Float."**
- Pad-and-fill a pier and dock at an offset from the Lake Waystone; fill a run of lit lanterns and Supplementaries candles down it; lamp posts **7 through 12** complete the road's first stretch.
- Summon all six current residents on the pier. Nella's dialog is the toast, and it is four words long, and she has clearly rehearsed it. The duckling is placed on the water.
- Fireworks via `/summon`. Every player receives a **Floating Lantern** decor item and a **Frog Plushie**.
- The tech lane receives an empty **Thermal Energy Cell** and Josie's second schematic packet — the visible "the next tier is already in your hands" moment.
- Stage `act3`. Border → 6,000. **Pier Waystone** set.
- **Journal Entry 3** unlocks.

### Act III finale — **The Harvest Supper** *(triggered by Q56)*
- `/sereneseasons setseason autumn` · `/time set 13000` (golden hour)
- Title: **"The Harvest Supper."**
- Fill the square with harvest dressing: pumpkins, hay bales, candle holders, hanging lanterns; raise the granary façade and the town noticeboard; lamp posts **13 through 22**.
- Summon all eight residents seated, each with one line about the year so far. Wisp brings three more Ribbits. Pip's duckling is at the table and is served first.
- Every player receives a **Harvest Gift** from each resident: Marnie's pie, Bram's brass toolbox, Oda's ledger page, Nella's smoked trout, Halden's tonic, Tobin's copper nugget, Wisp's basket, and Pip's drawing (a written book, badly spelled, framed).
- **The turn.** At the end of the meal the season command fires *forward*: `/sereneseasons setseason winter`, snow starts, and Oda says the line the whole act was built on: *"That's the last warm night. Let's not lose anybody this year."*
- Stage `act4`. Border → 10,000. Nether access opens.
- **Journal Entry 4** unlocks — Josie's argument that kindness is not the fix.

### Act IV finale — **The Longest Night** *(triggered by Q75)*
The centrepiece of the pack.
- `/sereneseasons setseason winter` · `/time set midnight` · heavy snow.
- Title: **"The Longest Night."**
- Summon every resident — eight plus four Ribbits — outside the Works, each with one line. Pip rings the hand bell.
- The player hands Bram the lever. **Bram pulls it.** (Quest completion runs the chain.)
- **The world changes in one instant:** a fill pass lights all 39 lamp posts down every street at once; the greenhouse heaters come on; the bathhouse starts steaming; a setblock relights the inn's Hearth; snow-covered lamps glow. One long warm chord.
- Stage `greenhouse_warm` → **Serene Seasons Greenhouse Glass** recipe unlocked. The cozy player gets a Winter Seed Pack and a watering can that never empties.
- The tech lane gets the **Works Deed blueprint** — revealed at Oda's counter, priced, not yet owned.
- Every player receives a **Hearthkeeper's Lantern** (permanent held light) and a plushie of their choice.
- Border stays at 10,000. **Journal Entry 5** unlocks — the last thing Josie wrote.

### Act V finale — **Founder's Day** *(triggered by Q91)*
- `/sereneseasons setseason spring` · `/time set noon` · clear.
- Title: **"Founder's Day"** / subtitle: *"Spring, Year Two."*
- Pad-and-fill the finished town: the town hall façade, a signpost carrying every resident's name, a stone bridge, the rebuilt mill roof, banners, paved square, flower beds.
- Summon all residents **plus three new arrivals** walking in along the road — unnamed Easy NPCs with new skins. Visible proof the valley is alive again.
- Halden reads the last page of Josie's journal aloud (tellraw sequence, one line at a time, paced).
- Every player receives: the **Kettle Family Deed**, a **Founder's Plaque** decor block with their own name on it, the full plushie set, top-tier backpack, and a **Copper Kettle** trophy to hang over their own hearth.
- Fireworks. Long playsound. Simple Voice Chat is the actual payoff here — twelve people standing around a table in proximity chat is the emotional beat the whole pack is built toward, and it needs no code at all.
- `/worldborder set 60000000` with the line: *"The valley's fine now. Go see what's past the ridge — and come home for supper."*
- Unlocks the **Endless Seasons** chapter: repeatable seasonal festivals, rotating Bountiful bounties, Oda's ore contracts for the tech lane, Marnie's menu challenges for the cozy lane, and new-resident requests. The story ends. The world doesn't.

---

### The buried secret and its reveal *(Act III, Q54–Q55)*
The one thing the winning spine genuinely lacked was a mystery with a real payoff. Here it is, and it is deliberately warm rather than spooky, because the mystery belongs to **both** players — she found the door in hour one, he opens it in autumn.

**Setup.** Act I Q5: a sealed iron door in your own cellar, chalked *"Not yet. — J.K."* It cannot be opened, and no quest asks you to try. It sits there for two acts. Halden changes the subject whenever it comes up.

**The turn.** Q54: the Kettle Plate from the adit is Josie's own shorthand. Halden can read it. He has been able to read it for four years.

**The reveal.** Q55, written on the cellar wall in Josie's hand:

> The Works ran. For eleven days, in the winter Old Dell left. The greenhouse was warm and the bakery had flour and I stood in the lane at ten o'clock at night in February and every lamp on the road was lit and I have never been happier in my life.
>
> Then I shut it down, and I sealed the door, and I told everybody the boiler cracked.
>
> Here is why, and I want it in writing so nobody has to guess. **A machine that one person can run is not infrastructure. It's a hostage.** I was seventy-one. If I'd died in the spring — and I nearly did — this valley would have spent one warm winter and then frozen with the answer sitting under my kitchen, and they'd have blamed themselves for not being clever enough, which is the cruellest thing I could possibly have left them.
>
> So I shut it off and I waited for two of you.
>
> If you're reading this and there is more than one set of footprints on my cellar stairs, then I was right to wait, and I'm sorry it took so long, and go and turn it on.

This does four jobs at once: it explains why the reactor is buried instead of built, it makes the pack's *two-player* structure the literal solution to the plot, it gives Josh a mystery that pays out in his own lane, and it justifies the Standing gate on the deed — the town has to be able to run this without you, or it's a hostage again.

---

## 8. Reward philosophy

**The rule, stated once:** a reward is never a trophy. It is the shortcut for the next quest, and it arrives **one quest before** it is needed, so the player never notices they were about to have a bad time.

**The hard constraint:** no quest ever asks for 64 of X unless the previous quest handed you 48 of them.

**The second hard constraint** *(this one is for Josh):* **pre-made is for intermediates, never for the machine that is the point of the quest.** Casings, servos, alloys, cogs, patterns and spare frames arrive assembled. The Pulverizer, the reactor, the turbine, the network and the quarry are always built by hand. Grind deleted; building never deleted. Three quests in the pack are explicitly **problems, not recipes** — Q71 (turbine inside a parts budget), Q83 (power target inside a fuel budget), and Q72 (route the waste heat to two live consumers). These are the ones where the pack expects him to actually think.

**Worked example 1 — the first hour has no mining in it.**
Q12 hands over *exactly* 12 iron and 24 andesite. Q13 consumes exactly that and pays a **pre-made Mechanical Press plus 8 cogwheels and 8 shafts** — the entire bill for Q14's Millstone. Josh goes from "talk to a guy" to "powered millstone" without opening a mineshaft once. That is the specific thing he used to cheat past, deleted by design rather than by console.

**Worked example 2 — the tool always precedes the ask.**
Q28 unlocks **Vein Mining** as the reward for prospecting six marked spots — a three-minute job. The next real mining ask is Q45's copper adit and Q69's yellorite, both of which would be twenty-minute swings-per-block chores and are now about three minutes each. The grind never happens because the thing that deletes it was the reward for the tutorial version of the same task.

**Worked example 3 — the tech lane's biggest build is the cozy lane's biggest convenience, twice, in the same act.**
Q52 finishes the wireless terminal and hands **a second one to the partner** — one act before the decorating marathon, so she types "lantern" instead of opening fourteen chests. Q53 links an ME terminal to Oda's board, and from that moment **every delivery quest in the pack auto-fills from network stock and becomes one click.** Pip's five-delivery winter quest (Q63) is deliberately placed *after* it, so the first thing she notices about his network is that her own chores got shorter. He gets to watch that land.

**Worked example 4 — Valley Scrip is the standing supply chain.**
Bounties and deliveries pay Scrip. Scrip buys, at Oda's counter: pre-made Andesite Casings, crates of Redstone Servos, spare Machine Frames, reactor casing bundles, and finally the **Works Deed** itself. Her play converts directly into his skip-tokens, every session, permanently. It is not a themed reward — it is the pack's answer to "she plays her lane, I play mine."

**Standing rules baked in everywhere**
- Any quest that says *go find* ships the marker or a pre-set Explorer's Compass in the same reward packet.
- Any decoration quest ships its own checklist of blocks, delivered before the task.
- Backpack and storage upgrades land **before** the acts that produce a lot of items.
- Waystones are given, never crafted.
- Torchmaster lanterns arrive with the first structure that needs one, not after the first bad night.
- Lootr means arriving second to a structure costs nothing. Corpse means a death is never a lost run. Both are named here so the design never has to add a difficulty apology.

---

## 9. Multiplayer

**Shape.** FTB Teams, progress shared per team. FTB Quests tracks progress **per team, not per player** — so "personal" quests are authored as team quests with per-lane pins, and anyone who genuinely wants their own book becomes their own team. This is stated up front because it silently breaks any design that assumes per-player quest state.

### A. The couple's team (default)
Josh and his wife are one team, **Kettle**. Completions are shared: she never sees a tech quest blocking her chapter, he never has to cook. On first join each player answers one question — *"the kitchen, or the workshop?"* — which sets which lane the book pins. Both can see everything; only one lane is ever pinned. Chapters unlock when **the team** finishes an act, so nobody waits alone.

### B. A second team — **The Second Letter** *(framing grafted from Lanternwick)*
Josie wrote to more than one relative. She was not a woman who put all her eggs in one nephew. A new team's first-join grants every member a **Second Letter** in her hand, dated the same day as yours, and opens a short private chapter.

- They place **their own Homestead Waystone**. They do **not** place a second Town Anchor — there is one town.
- Their lots are on the **far side of the square** from the first team's, so the town visibly grows from two directions rather than one team's suburb absorbing another's.
- Their Act I is a compressed six-quest chapter, **New Neighbour**: place your homestead, build a shelter, meet Marnie, plant a plot, get a pet, register at the town noticeboard.

### C. The one-per-world rule *(grafted verbatim from Copperbell — the single best multiplayer sentence anyone wrote)*
**Town-state quests are one per world.** The mill wheel, the granary, the greenhouse shell, the reactor, the bell — the town only needs restoring once. If another team already did it:

> The quest **auto-completes** for the arriving team, with a line of flavour — *"The mill was already turning when you got here. Bram says you should go and meet whoever did it."* — **and still pays the full reward.**

**Because the reward is the shortcut, not the trophy.** A team that arrives in Act IV still gets the pre-made frames, the charged cell, the backpack upgrades and the Scrip, because those are the things that let them play. Withholding them to protect somebody's sense of achievement would only make the game worse for the person who showed up late.

The *personal* half always runs fresh: your farm, your kitchen, your workshop, your animals, your house, your friendships. Every team gets its own cozy build-out and its own arcs with the same residents.

### D. Late joiners — **"You Missed the Weather"** *(structure grafted from Lanternwick)*
A six-quest onboarding chapter, granted automatically on first join at any point in the story. A player joining in Act IV does not play three months of spring.

1. Read the Second Letter.
2. Place your own waystone and name it.
3. See Oda — she gives you **every waystone the town has already activated**, the journal chapters written so far, and a Newcomer's Satchel scaled to the current world act (Act II: Create basics + farm crate · Act III: + Thermal starter, backpack, 100 Scrip · Act IV/V: + AE2 basics, wireless access to the town network, 200 Scrip).
4. See Marnie — she feeds you and gives you a food stack for the current season.
5. **See Bram, or see Pip.** The quest asks which one you'd rather go and visit. **That single choice sets your lane**, invisibly, with no menu and no explanation.
6. Claim a lot in town.

On completion, KubeJS grants **every world stage already unlocked** and drops them onto the current act's pinned objective. They are never behind and nobody walks them through four acts of backfill. In fiction: their letter got wet. Pip is extremely sorry about the letter.

### E. Somebody stops logging in
Nothing breaks. Their homestead becomes a house in town, and a one-line noticeboard quest lets the remaining team adopt any structures and animals they left behind — the animals get fed, the lamps stay lit, and the quest text is kind about it. Nothing in the story ever requires a specific player to be online.

### F. World stages vs team stages — the authoring split
- **World stages** (one per world, never re-run): every act finale, every structure the anchor system builds, every resident's arrival, the reactor, the greenhouse, the quarry, the Lantern Road count.
- **Team stages** (per team, run fresh): lane choice, personal building, cooking, animals, fishing, resident chains, Standing, Valley Scrip balance, backpack and network access.

If a stage would ever be granted twice for the same world change, it is a world stage. That single rule prevents every duplicate-finale bug.

---

## 10. Journal — Josie Kettle's book

Patchouli, five chapters, one per act finale, plus the cellar wall in Act III. Same hand throughout — practical, warm, a bit wry, never sad for long — and the art direction is that the handwriting gets shakier and the plans get **more** ambitious, not less.

---

**Entry 1 — found on the mantle, Act I**

> If you're reading this you got the letter, and the letter lied a little. The house is not "mostly standing." The house has a chimney and opinions.
>
> Here is the only advice I'll give you all at once, so don't skip it: **do not look at the whole valley.** It will flatten you. I looked at the whole valley once, in about my sixtieth year, and I sat down on the step and did not get up for a day and a half.
>
> Look at the porch. It is eleven feet of porch and it has weeds on it. Pull the weeds. Then look up and see whether you feel like looking at anything bigger.
>
> That's it. That's the whole trick. I have used it on a broken wheel, a dead orchard and one genuinely terrible winter, and it has not failed me yet.
>
> The kettle's copper. It's older than me. Put it on.

---

**Entry 2 — unlocked at the Thaw Fair, Act I finale**

> I forgot how loud five people are.
>
> We had the Fair today, first one in — I want to say nine years, but Oda would correct me and she'd be right, she always is, she keeps the book. Four stalls, and one of them was a plank on two barrels, and Pip sold flowers he had picked out of my own garden and charged me for them.
>
> Bram got the wheel turning at noon. He stood there with his hands on his hips and said "well." That is the most emotional I have ever seen that man.
>
> Write this down somewhere you'll find it in November, when it's dark and you're tired and you're wondering why you're bothering: **it's this.** It was always going to be this.

---

**Entry 3 — unlocked at the Lantern Float, Act II finale**

> Nella was certain nobody would come. She spent all week telling me it was a silly idea, and she spent all week making lanterns, which is how you know somebody means it.
>
> Everyone came. Wisp brought the whole reed village and they sang something in frog that I believe was about soup. Halden cried and said it was the smoke.
>
> A thing I've noticed about summer here: it gives you more than you can hold. Fish, fruit, light, hours. And every single year we let most of it rot, because we had nowhere to put it. That is not a farming problem. That is an engineering problem, and I have been calling it a farming problem for thirty years because I was frightened of the other kind.
>
> I'm going to stop doing that. I bought a book about turbines.

---

**Entry 4 — Halden hands you the second half, Act III**

> Halden — if you're the one reading this out loud to somebody: yes. Tell them. I don't mind any more.
>
> The Works was never going to be a mine. I was building a power plant. Copper, then brass, then a boiler, then a good deal past a boiler, and the point of it — the entire point, the only point — is that this valley loses people every winter. Not to anything dramatic. To cold rooms and empty larders and four months of nothing to do. People leave in February and they do not come back in April.
>
> **You cannot fix that with kindness. I tried. I was extremely kind for three decades and Old Dell still left.**
>
> You fix it with heat and light in January. That's it. That's the whole design document.
>
> People think I want the lamps back for the light. There's plenty of light — it's a valley, the sun comes up. I want them back because when the road was lit you could see, from your own window, at ten o'clock at night in February, that somebody else was still awake. That's what a town is. Not the buildings. That.
>
> The plans are in the crate under the bench. Bram will tell you they don't work. Bram is wrong; he has simply never had enough hands. You have hands. Go on.

---

**The cellar wall — Act III, Q55.** *(See §7. Not a journal entry; it is chalk on stone, and it is the reveal.)*

---

**Entry 5 — the last page, unlocked at the Longest Night, Act IV finale**

> Last one. The writing's gone shaky, so I'll be brief, which Marnie will tell you is a first.
>
> If the lights are on out there — if you're reading this warm, in the dark half of the year, with the greenhouse going and somebody's kid asleep by the fire — then it worked, and it wasn't me who did it, and that is exactly right. I only ever got this valley to hold on. You got it to stay.
>
> Everything I know how to do, somebody taught me on a bad afternoon when they had better things to be doing. My mother taught me the porch trick. Bram's father taught me to read a wheel. A woman whose name I have genuinely forgotten taught me to bank an oven so it holds overnight, in about ninety seconds, in the rain, because I looked cold. None of them saw what I did with it. That's normal. That's the arrangement.
>
> So: the wheel goes counter-clockwise, the third lamp post leans and always has, and Marnie takes her tea far too strong.
>
> Don't turn this into a monument. Don't put my name on the square. Put a bell there, and ring it when supper's ready.
>
> And when somebody new comes up the road next spring — and they will, they always do when there's smoke — go out and meet them. Bring bread. Pretend you were passing.
>
> — J.K.
>
> *(P.S. There's a lamp post on my porch with nothing on it. I'd like to be on the line.)*

---

## 11. Build notes

**Mod-list check.** The live manifest at `/Users/joshuamalloy/Desktop/1. Projects/Minecraft/pack/mods` (124 entries) was verified against this story document. Everything this story depends on is present: `create`, `create-steam-n-rails`, `geolosys`, `vein-mining`, `torchmaster`, `additional-enchanted-miner` (this is QuarryPlus — the mod's actual id), `biggerreactors`, `ae2`, all four Thermal jars plus Cultivation and Innovation, `serene-seasons`, `aquaculture`, `easy-npc`, `kubejs`, `ftb-quests-forge`, `ftb-teams-forge`, `patchouli`, `lootr`, `corpse`, `bountiful`, `waystones`, `duckling`, `ribbits`, `perfect-plushies`, `simple-voice-chat`. **A prior feasibility flag claiming Create, Geolosys, QuarryPlus, Torchmaster, Steam 'n' Rails and vein-mining were absent is incorrect** — the flag appears to have searched for `quarryplus` rather than `additional-enchanted-miner`. No blocker. `dynamic-torches` provides the held-light behaviour in place of Dynamic Lights; the Hearthkeeper's Lantern is authored against it.

**Custom-code bill, in build order.**
1. **Town Anchor** — one KubeJS block-place listener, one persistent coord, one `offset(x,y,z)` helper. Everything else in the pack calls it. Build this first; nothing else works without it.
2. **Custom intermediates** — Seasoned Oak Boards, Washed Silica, Spring Water, the two Kettle Plates, Valley Scrip. Five KubeJS items. Recipe removal on Create's Water Wheel and Thermal's Machine Frame will desync EMI, so **each removed recipe gets a replacement recipe pointing at the gated intermediate**, not a deletion — EMI then shows the real path and nobody has to guess.
3. **Valley Scrip shop** — Easy NPC trades on Oda, with the catalogue swapped by stage. Three tiers. No custom UI.
4. **Standing** — a count of completed quest IDs. Roughly twenty lines.
5. **Finale chains** — fill/setblock at anchor offsets. Volume work, not difficulty.

**Season config.** `season_cycle_length = 48`. Every act finale force-sets the season as its first command. Do not ship without this.

**Honour-system tasks.** Every "build a shelter / pen / greenhouse shell" quest is an FTB Quests Checkmark task with a screenshot in the quest text. Item delivery and item crafting carry the real gating. This is a deliberate choice, not an oversight — FTB Quests has no build detection and faking one is not worth a week.

*End of story document. Next: FTB Quests chapter JSON (Q1–Q91), the KubeJS stage and anchor scripts, Easy NPC spawn commands, and Josie's Patchouli book.*
