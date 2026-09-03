# Copper Kettle Valley — Story Bible
### *A Year in the Valley* — Minecraft Forge 1.20.1 private modpack

---

## 1. Pack name and tagline

**Candidates**

1. **Copper Kettle Valley** — warm, domestic, and quietly hints at the copper-and-brass tech spine (Create, Thermal). The valley is named for the Kettle family, who ran the old copper works and the inn.
2. **Hearthfall** — evocative and seasonal, but abstract; a non-gamer partner reads it as vaguely fantasy rather than cozy.
3. **The Long Year at Mossgrove** — good literary flavor, but "long year" reads as a slog, which is exactly the feeling we are designing against.

**Chosen: Copper Kettle Valley.**

**Tagline:** *You inherited a cold house in a quiet valley. Put the kettle on — it takes a year to bring a town back.*

---

## 2. Premise (shown on first join)

You inherited the old Kettle farm from a great-aunt you barely remember — Josie Kettle, who kept the lights on in this valley long after everyone else stopped trying. The letter says the house is "mostly standing." It is: a chimney, three walls, a bed frame, and a copper kettle still hanging over a cold hearth. The valley outside is not empty, exactly. There is an inn with no innkeeper on the road, a mill with a broken wheel, a general store with the shutters down, and a marsh full of frog-folk who have not had a neighbor in years. Josie left a journal on the mantle, and the first page says the same thing on every page after it: *the valley only ever needed one person to start.* You have one spring to make this place a home, one summer to make it worth staying, one autumn to fill the larder, and one winter to prove the valley can keep its own lights on. Then it starts again — warmer.

**First-join screen text (title + tellraw):**
> *Spring, Year One.*
> **Copper Kettle Valley**
> Open your Quest Book. There is exactly one thing to do.

---

## 3. The setting

### The valley
A shallow bowl of meadow, water, and low hills — home to a market road, a stream, a lake, a marsh, and one hillside where the copper seam still shows through the grass. Everything the story needs is placed by the players themselves, so the story never depends on terrain.

### What is broken
- **The Hearth** — the inn's fireplace, the valley's social center. Cold since Josie died. Nobody has cooked for anybody in years.
- **The Mill** — Bram's water wheel snapped its axle. No flour, no sawn boards, no power of any kind.
- **The Store** — Oda's shelves are empty because no wagon has come up the road; the bounty board outside has one weathered notice on it.
- **The Ferry & the lake** — Nella's boat is beached; the docks are rotted.
- **The Works** — the Kettle family copper works, a hole in the hill with a collapsed adit. Josie's real project, unfinished.
- **The winter** — the real antagonist. The valley has no way to grow, light, or heat anything from November to March. Every year, whoever is left leaves. That is the actual reason the town emptied.

### What restoring it means
Restoration is measured in **people, not blocks**. Every act adds residents, and every resident makes a lane easier: Marnie feeds you, Bram powers you, Oda supplies you, Nella moves you, Halden heals you, Wisp forages for you, Tobin surveys for you, Pip delivers to you. The visible scoreboard is the town itself — each act's finale physically builds part of the square in front of the players.

### The Town Rule (terrain independence)
Nothing is pre-built. The players place **two waystones** in Act I:
- **Homestead Waystone** — wherever they want to live.
- **Town Anchor Waystone** — on any flat-ish spot within about 60 blocks of home.

KubeJS records the Town Anchor coordinates. From then on, every structure, NPC, market stall, sign, lamp post, and festival table is placed at a fixed offset from the anchor by quest-reward commands (`/place`, `/fill`, `/setblock`, Easy NPC spawn). The valley grows outward from a spot the players chose, so it always fits their world and always looks intentional.

### Keeping a non-creative player oriented
- **World border, opened by act.** Act I: 1,500 blocks. Act II: 3,000. Act III: 6,000. Act IV: 10,000 (plus the Nether). Act V: fully open. The world is never bigger than the current chapter needs, so "too open" never happens.
- **One chapter visible at a time.** FTB Quests shows a single unlocked chapter; completed chapters collapse into a "Memories" chapter. Future chapters are hidden, not greyed.
- **One pinned objective.** Every quest reward for the cozy lane auto-pins the next quest. The book always opens to a single sentence in plain language.
- **Waystones as bookmarks.** Every named place in the story is a waystone, given already-placed or placed by the quest that introduces it. Fast travel is free between town waystones from Act I.
- **Xaero markers as rewards.** Any quest that says "go find X" hands over the map marker in the same breath, or hands over an Explorer's Compass already told what to look for.
- **Torchmaster from Act I.** The homestead and every pasture get a lantern early. Nothing spawns where the cozy player lives. Ever.
- **No timers, no fail states.** Seasons advance on their own; festivals wait for the players. Missing a festival is impossible.

---

## 4. Cast

Eight residents, placed with Easy NPC, each with a name, a face, a want, and a three-beat arc that resolves across the year. Each is tagged **cozy**, **tech**, or **both** — meaning which lane's quests they hand out and who they talk to.

### Marnie Ashcombe — Innkeeper, keeper of the Hearth — **cozy**
Fifties, flour on her sleeves, talks to you like you already live here. Ran the inn with Josie; has kept the building swept every day since it closed, out of habit.
**Wants:** to serve a meal to a full room again.
1. *Spring* — She comes up the hill because she saw smoke from your chimney for the first time in years, and brings bread she baked for nobody.
2. *Autumn* — She admits she has been cooking for one and throwing half of it away. The Harvest Supper is the first meal she cooks to a real headcount.
3. *Winter* — Her stores run out during the cold snap. She lets you feed *her*, which is the hardest thing she does all year, and afterward stops calling the inn "Josie's place."

### Bram Tolliver — Millwright — **tech**
Sixties, grease-stained apron, keeps every broken part he has ever owned in labeled crates. Gruff for about four minutes.
**Wants:** to see the wheel turn again before he gets too old to fix it.
1. *Spring* — Won't accept help; will accept "hold this." Teaches Create by making you do it while he narrates.
2. *Summer/Autumn* — Hands over Josie's Thermal schematics, which he could never make work, and stops pretending he's the smartest engineer in the valley.
3. *Winter* — Refuses to leave the mill during the cold snap. Has to be carried, essentially, to the reactor lighting — and is the one who pulls the lever.

### Oda Vance — Storekeeper, bounty board — **both**
Forties, ledger under one arm, opinions about everything. Reopened the store on the strength of a rumor that someone moved into the Kettle place.
**Wants:** a reason to reorder stock — i.e., customers.
1. *Spring* — Sells you almost nothing because she has almost nothing; posts the first bounty out of embarrassment.
2. *Summer* — The trade wagon (a Steam 'n' Rails line, later) reaches town and her shelves fill. She starts special-ordering for individual residents by name.
3. *Winter/Spring* — Becomes the valley's quartermaster during the crisis and, at Founder's Day, hands the ledger to the players: the town's books balance for the first time.

### Nella Brightwater — Fisher and ferryman — **cozy**
Thirties, permanently damp, unbothered. Lives on the lake in a boat she keeps meaning to repair.
**Wants:** the docks rebuilt so the lake is a place people go, not a place she hides.
1. *Spring/Summer* — Teaches fishing (Aquaculture) and the lake's moods; gives you your first good rod.
2. *Summer* — The Lantern Float is her idea, and she is visibly terrified nobody will come.
3. *Winter* — The lake freezes and she loses her livelihood for a season; the greenhouse gives her a job, and she discovers she likes growing things.

### Halden Root — Herbalist and brewer — **both**
Quiet, ancient-seeming, probably fifty. Keeps a hedge garden and a still. Knew Josie best.
**Wants:** to finish the recipe book Josie and he started.
1. *Spring* — Trades tea for stories; gives the players the herbal starts and the first Let's Do HerbalBrews kit.
2. *Autumn* — Reveals what Josie was actually building in the Works, and gives you the second half of the journal.
3. *Winter* — Keeps the whole valley from getting sick during the cold snap; admits he stayed because Josie asked him to, and that he's glad he did.

### Tobin Gale — Prospector — **tech**
Twenty-three, over-caffeinated, unreasonably delighted by rocks. Showed up chasing a Geolosys survey report and never left.
**Wants:** to be taken seriously by someone who owns a pickaxe.
1. *Spring/Summer* — Nobody believes his survey. He is right about everything and terrible at explaining it.
2. *Autumn* — His sample cores locate the deep copper and iron clusters; Bram finally says "good work" out loud.
3. *Spring, Year Two* — He calls in the quarry rig. It is the biggest thing he has ever been responsible for and he is very calm about it, which fools no one.

### Wisp — Ribbit forager — **cozy**
A frog-person from the reed village downstream. Speaks in short, cheerful, slightly wrong sentences. Carries too much.
**Wants:** the marsh village and the town to be one place instead of two.
1. *Spring* — First contact; brings a basket of things you cannot identify, all of which are delicious.
2. *Summer* — Moves into a stilt house at the edge of town, which the town builds for them.
3. *Winter* — Brings the entire reed village to shelter in the inn; the two settlements merge for good.

### Pip Ashcombe — Marnie's nephew, age nine — **cozy**
Runs everywhere. Names everything. Has a duckling by the end of Act I and it is the pack's mascot.
**Wants:** a pet, and then a job.
1. *Spring* — Gets the duckling. Names it after you, or after a food.
2. *Summer/Autumn* — Appoints himself the town's courier; his delivery quests are the pack's short, sweet filler between big beats.
3. *Winter* — Is the one who notices the Hearth has gone out, and the one who rings the bell. Gets a plushie of his duck at Founder's Day.

---

## 5. The two lanes and how they gate each other

**Cozy lane (the wife's spine):** food, animals, fishing, seasonal crops, decorating, meeting people. Every quest names an item and a place. Rewards are things you can look at or hug.

**Tech lane (Josh's spine):** Create → Thermal → Applied Energistics → Bigger Reactors → QuarryPlus, in that order, with no early grind — every tier hands over the awkward middle materials and asks for the interesting one.

They are **not parallel tracks**. They are a braid: roughly every third quest in each lane needs something the other lane produced. A solo player can do both (the story assumes it); a couple splits it naturally; a friend can pick up either.

### Cross-lane dependencies

1. **Seasoned boards → the first water wheel.** Create's Water Wheel recipe is stage-gated behind *Seasoned Oak Boards*, which only exist if someone fires Marnie's bread oven and dries green planks in it overnight (cozy: A1Q13). Bram literally cannot start until the inn's oven is lit.
2. **Dredged lake sand → the first Thermal machine frame.** Machine Frames are gated behind *Washed Silica*, made from sand only obtainable by dredging the lake with Nella (cozy: A2Q6) and washing it in a Create fan. No fishing trip, no Pulverizer.
3. **Powered kitchen → Cooking for Blockheads.** The full Cooking for Blockheads kitchen (fridge, sink, counters) is gated behind a Thermal Energy Cell within 12 blocks (tech: A3). The cozy player's dream kitchen is the tech player's first "look what I did for you" moment, and the fridge unlocks the entire preserved-food branch that Act IV depends on.
4. **Certus seeds → spring water.** Applied Energistics certus quartz seeds only grow in water drawn from Halden's spring, which requires the cozy herbal-garden line (A3Q4). AE2 does not start until the herbalist likes you.
5. **Reactor heat → winter crops.** In Act IV the greenhouse's Serene Seasons override (grow anything, any season) is a KubeJS stage lit only when the Bigger Reactors reactor is producing and Fluxducts reach the greenhouse heaters. The cozy player's winter farm exists because the tech player built a reactor. This is the pack's thesis.
6. **Town approval → the quarry deed.** QuarryPlus is stage-locked behind *Founder's Day Standing*: six of eight residents at max friendship, which is earned almost entirely with cozy-lane gifts, meals, and errands. Josh's biggest toy is unlocked by his wife's relationships. (He is told this on day one, cheerfully.)
7. **Trains → the store.** Oda's full stock list (and therefore the cozy lane's decor catalogue: Macaw's, Handcrafted, Supplementaries variants) unlocks when the Steam 'n' Rails line reaches town in Act III — a tech build.
8. **Bounties → tech shortcuts.** Bountiful board bounties are turned in by the cozy lane for *Valley Scrip*, and Scrip is the only way to buy the tech lane's skip-tokens: pre-made Andesite Casings, a crate of Redstone Servos, a spare Machine Frame. Cozy work literally deletes tech grind.

---

## 6. The five acts

Format: `Qn. Title | lane | task | reward | depends on`
Lanes: **C** = cozy, **T** = tech, **B** = both.
Every task is written the way the quest text will read: plain words, an item named the way it appears in the player's inventory, and a place.

---

## ACT I — SPRING: *The Thaw*

**Story beat.** You arrive at a cold house in a valley that used to be a town. One neighbor sees your chimney smoke, comes up the hill, and decides you're staying. By the end of spring there are five people in the valley instead of one, and the mill turns.

**Goal, in one sentence:** *"Make the old Kettle farm livable and wake the town up in time for the Thaw Fair."*

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | Somebody Left the Kettle On | B | Take the Homestead Waystone out of your starting bag and place it anywhere you'd like to live. | Josie's Journal (Patchouli), Copper Kettle, bed, 64 oak planks, cooked food ×16, a Torchmaster Feral Flare Lantern | — |
| Q2 | Four Walls and a Door | C | Build any small shelter around your waystone, put a Macaw's cottage door on it, and sleep one night. | Handcrafted table + 2 chairs, 4 Macaw's windows, wool rug, "homestead" stage | Q1 |
| Q3 | Put the Kettle On | C | Hang the Copper Kettle over a campfire and cook one Farmer's Delight meal in a Cooking Pot. | Cooking Pot, Skillet, Farmer's Delight knife, 3 sacks of assorted seeds | Q2 |
| Q4 | Where the Square Goes | B | Place the Town Anchor Waystone on flat ground within 60 blocks of home. This is where the town will be. | Town Anchor set (KubeJS records it), a stone path laid from your door to the anchor, 2 Supplementaries lamp posts placed | Q3 |
| Q5 | Chimney Smoke | C | Sleep one night after placing the Town Anchor. | **Marnie arrives** at the inn plot; her tent + sign placed; loaf of Marnie's Bread ×8; inn waystone | Q4 |
| Q6 | Three Beds of Dirt | C | Till a 3×9 patch near your house and plant the wheat, carrots and potatoes from Marnie's seed sack. | Farmer's Delight watering can, bone meal ×16, straw hat | Q5 |
| Q7 | Two Hens and a Rooster | C | Lead 2 chickens home with seeds and build them a fenced pen with a Macaw's gate. | Chicken feed, a nesting box, "the coop is warm" — Torchmaster lantern placed over the pen | Q6 |
| Q8 | Pip and the Egg | C | Bring 6 eggs to Marnie at the inn. | **Pip arrives**; you are given a Duckling to name and keep; Pip's courier board unlocks | Q7 |
| Q9 | The Man at the Broken Mill | T | Walk to the mill plot marked on your map and talk to Bram. | **Bram arrives** at the mill; Create wrench, goggles, iron ingots ×12, andesite ×24 | Q4 |
| Q10 | Eight Alloys, No More | T | Make 8 Andesite Alloy using the iron and andesite Bram gave you. | Mechanical Press (pre-made), Cogwheel ×8, Shaft ×8 | Q9 |
| Q11 | Turn It By Hand | T | Build a Millstone, attach a Hand Crank, and mill 16 wheat into flour for Marnie. | Millstone recipe unlocked at half cost; Encased Fan; 3 more Andesite Alloy | Q10 |
| Q12 | The Green Boards | C | Fire the inn's bread oven for Marnie, then leave 32 oak planks inside overnight. | **Seasoned Oak Boards ×32**; "seasoned" stage (this unlocks Water Wheels) | Q5, Q11 |
| Q13 | Water Finds a Way | T | Build 2 Water Wheels on the stream with the Seasoned Oak Boards and connect them to the Millstone with shafts. | Create Saw (pre-made), Basin, Mechanical Mixer, Bram's crate: 32 Andesite Alloy | Q12 |
| Q14 | Sawdust and Shingles | T | Use the Saw to cut 128 boards, then hand Bram 64 of them for the market stalls. | Macaw's roof kit ×3, Supplementaries planter ×4, "market_stalls" stage | Q13 |
| Q15 | Marnie's Kitchen | C | Build a Cooking for Blockheads Kitchen Counter, Sink and Oven in the inn, then cook 3 different Farmer's Delight dishes. | Cookbook, Fruit Basket, 5 recipes learned automatically, Handcrafted cupboard set | Q12 |
| Q16 | Frogs in the Reeds | C | Take the Explorer's Compass Marnie gives you (already set to Ribbit Village), follow it, and trade with the frog folk. | **Wisp befriended**; basket of marsh produce; Sophisticated Backpack (upgraded once) | Q15 |
| Q17 | The Store Reopens | B | Sweep out the general store and bring Oda 16 flour, 8 eggs and 8 wool. | **Oda arrives**; store + bounty board placed; Valley Scrip ×10; store waystone | Q14, Q15 |

### Act I finale — **The Thaw Fair**
Triggered by completing Q17. In sequence, run as quest reward commands:
- `/time set day`, `/weather clear`, a soft playsound and a title card: *"The Thaw Fair — Spring, Year One."*
- `/place` the market stall structures at the recorded Town Anchor offsets; `/fill` a stone-and-flower square between them; place bunting (Supplementaries flags), lamp posts, and a Handcrafted long table.
- Summon Marnie, Bram, Oda, Pip and Wisp at their fair positions with festive dialog; Pip's duckling follows him.
- Give every player a **Fair Basket**: festival food, a plushie of their choice, a Supplementaries sconce set, and 25 Valley Scrip.
- Unlock KubeJS stage `act2`, expand the world border to 3,000, and set the **Town Square Waystone** in the middle of the square.
- Journal entry 2 unlocks in the Patchouli book.

---

## ACT II — SUMMER: *The Long Days*

**Story beat.** The town is awake and it is immediately too small. Summer is abundance you can't store, water you can't move, and light you don't have. Nella comes back to the lake, Halden opens the hedge garden, and the mill stops being a mill and starts being a workshop.

**Goal, in one sentence:** *"Make summer's abundance actually usable — power the workshop, work the lake, and throw the town a party on the water."*

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | The Beached Boat | C | Follow the map marker to the lake and talk to the woman fixing a boat that doesn't need fixing. | **Nella arrives**; Aquaculture Iron Fishing Rod; lake waystone; tackle box | A1 finale |
| Q2 | Something With Fins | C | Catch 10 fish of any kind with Nella and cook one in the Skillet. | Neptunium-grade bait ×16, Fish Bag, 2 recipes learned, Nella's hat | Q1 |
| Q3 | The Hedge and the Still | C | Bring Halden 8 flowers of three different colors from around the valley. | **Halden arrives**; herbal garden placed; HerbalBrews starter kit; tea set | A1 finale |
| Q4 | Vines on the South Slope | C | Plant a grape trellis from the Let's Do Vinery kit and water it twice. | 12 grape starts, wine press, "vinery" stage, Handcrafted wine rack | Q3 |
| Q5 | Bees, Cows, and a Sheep Named Later | C | Build a pasture with a fence, a trough and a Torchmaster lantern, and move in 2 cows and 2 sheep. | Milk churn, shears, wool bundle ×16, pasture waystone, sheep plushie | Q1 |
| Q6 | Dredging the Shallows | C | Ride out with Nella and gather 3 stacks of sand from the lake bed. | Nella's oar (faster swim), **3 stacks of Lake Sand**, "dredged" stage | Q2 |
| Q7 | The Rock Kid | T | Talk to the young man camped by the copper outcrop with too many notebooks. | **Tobin arrives**; Geolosys prospector's pick; survey map ×3 already marked | A1 finale |
| Q8 | Read the Rock | T | Use Tobin's prospector's pick on 6 spots he has marked to find the copper cluster. | Copper cluster location marked on your map; copper ingots ×32; Vein Mining unlocked | Q7 |
| Q9 | A Wheel That Doesn't Freeze | T | Build a Windmill Bearing with 8 sails on the mill roof so the workshop keeps running when the stream is low. | Gearbox ×6, Clutch, Gearshift, Mechanical Crafter ×3 | A1Q13 |
| Q10 | Wash the Sand | T | Wash the Lake Sand under an Encased Fan over water to make **Washed Silica**. | Washed Silica ×64, "silica" stage (unlocks Thermal machine frames), Create Deployer ×2 | Q6, Q9 |
| Q11 | Josie's First Schematic | T | Take Bram's crate of Josie's papers and craft your first Machine Frame. | Machine Frame ×2 pre-made as spares, Thermal Redstone Furnace (given), Fluxduct ×32 | Q10 |
| Q12 | The Pulverizer | T | Build a Thermal Pulverizer and run 64 iron ore through it. | Double iron output, Thermal Sawmill (given), 8 Redstone Servos, Dynamo (Stirling) | Q11 |
| Q13 | The Long Bench | T | Build a proper workshop room at the mill: 6 Storage Drawers, a drawer controller, and 3 Sophisticated Storage barrels. | Drawer upgrades ×6, Storage controller remote, Backpack upgrade tier 2 for every player | Q12 |
| Q14 | Lights on the Road | B | Place 8 Supplementaries lanterns along the road between the homestead and the square, and hook 2 of them to a Redstone Furnace via Fluxduct. | Dynamic Lights torch, "the road is safe" — hostile spawn suppression stage around town | Q12, A1Q17 |
| Q15 | A House on Stilts | C | Build Wisp a stilt house at the water's edge with Macaw's fences and a Handcrafted bed. | **Wisp moves to town**; marsh trade unlocked (rare seeds, frog-village decor); Ribbit plushie | Q5, A1Q16 |
| Q16 | Two Hundred Lanterns | C | Craft 24 paper lanterns with Marnie and Pip for the float. | Lantern crate, festival clothes, 20 Valley Scrip | Q15 |
| Q17 | The Bounty Board Fills Up | B | Complete any 3 bounties from Oda's Bountiful board. | 40 Valley Scrip; Oda's catalogue tier 2 (Macaw's + Handcrafted decor sets purchasable) | Q13, Q16 |

### Act II finale — **The Midsummer Lantern Float**
Triggered by Q17 at night.
- `/time set midnight`, `/weather clear`, title: *"Midsummer — The Lantern Float."*
- `/place` a pier + dock structure onto the lake at an offset from the lake waystone the player set; `/fill` a line of lit lanterns and Supplementaries candles along it.
- Summon all seven current residents on the pier; Nella's dialog is the toast. Pip's duckling is placed in the water.
- Firework rockets fired via `/summon`; a soft `/playsound`; every player receives a **Floating Lantern** decor item and a **Frog Plushie**.
- Give the tech lane a **Thermal Energy Cell** (empty) and Josie's second schematic packet — this is the visible "next tier is already in your hands" moment.
- Unlock stage `act3`, world border to 6,000, place the **Pier Waystone**.
- Journal entry 3 unlocks.

---

## ACT III — AUTUMN: *The Harvest Debt*

**Story beat.** The valley is finally producing more than it eats — and Oda opens the ledger and shows everyone the truth: at the current rate, the town runs out of food and fuel in February. Autumn is the act where cozy work becomes *preservation* and tech work becomes *storage and logistics*. Halden gives you the rest of Josie's journal, and you learn what the Works was actually for.

**Goal, in one sentence:** *"Fill the granary and finish Josie's storage system before winter — and feed the whole town at the Harvest Supper."*

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | Oda Opens the Ledger | B | Talk to Oda at the store. She counts the town's stores out loud. | Winter checklist (in-book), 30 Valley Scrip, Granary blueprint | A2 finale |
| Q2 | The Granary | C | Build a granary at the square: 12 Storage Drawers on a Handcrafted frame with a Macaw's roof. | Drawers pre-filled with the town's current stock; granary waystone; "granary" stage | Q1 |
| Q3 | Autumn Sowing | C | Plant the autumn seed pack (pumpkin, beetroot, squash, cranberry) — Serene Seasons will only grow these now. | Seasonal almanac (in-book: what grows when), scarecrow, 3 Farmer's Delight recipes | Q1 |
| Q4 | Halden's Spring | C | Follow Halden to the spring above the hedge garden and fill 3 bottles of **Spring Water**. | Spring Water ×3, "springwater" stage (unlocks AE2 certus seeds), herbal tea set, Halden's friendship tier 2 | Q3 |
| Q5 | Preserves and Pickles | C | Make 12 preserved foods: pies, pickled vegetables, and jam from the Let's Do Bakery and Farm & Charm kits. | Preserving crock ×4, pie safe, Cooking for Blockheads Fridge **blueprint** (needs power — see Q10) | Q3 |
| Q6 | The Bakery Line | C | Bake 8 loaves, 4 pies and 4 cakes in one session in the inn kitchen. | Bakery set (display cases, trays), Marnie's friendship tier 2, apron, cake plushie | Q5 |
| Q7 | Smoked, Salted, Hung | C | Build a smokehouse with a Nether's Delight hoglin-style rack and smoke 16 meat. | Cured meat ×32, smokehouse decor, "larder" stage | Q5 |
| Q8 | What Tobin Found | T | Take Tobin's 3 core samples to the marked hillside and open the copper adit. | Deep copper + iron cluster revealed (Geolosys), Vein Mining tier 2, Artifact from the adit chest (Lootr) | A2Q8 |
| Q9 | Induction | T | Build a Thermal Induction Smelter and alloy 32 bronze and 32 electrum. | Alloy stock ×64 pre-made, Thermal Centrifugal Separator (given), Fluxduct ×64 | Q8 |
| Q10 | The Cell on the Wall | T | Charge a Thermal Energy Cell from your dynamos and run Fluxduct to the inn. | **Kitchen power stage** — Cooking for Blockheads Fridge, Sink and Milk Jar now craftable; Energy Cell ×1 spare | Q9, Q5 |
| Q11 | Rails to the Road | T | Lay a Steam 'n' Rails line from the mill to the square with a Create train station. | Train assembly kit (pre-made engine + 2 cars), station bell, "trainline" stage | Q9 |
| Q12 | Oda's Wagon Comes In | B | Run the train to the square and unload Oda's first proper delivery. | **Oda's catalogue tier 3** — full Macaw's/Handcrafted/Supplementaries decor, seeds, animals purchasable with Scrip | Q11 |
| Q13 | Quartz in Water | T | Plant Certus Quartz Seeds in Halden's Spring Water and wait for them to grow. | Certus quartz ×32, AE2 Inscriber (given), Meteorite compass already pointing | Q4, Q10 |
| Q14 | The First Terminal | T | Build an ME Drive with 2 storage cells and an ME Terminal in the mill workshop. | 4 more storage cells, ME Import/Export bus set, "ae_basic" stage | Q13 |
| Q15 | Everything In One Place | T | Link the granary's drawers to the ME network with a Storage Bus so the whole town's stock shows on one screen. | Wireless Terminal + charger (given), Oda's ledger now auto-updates in-book | Q14, Q2 |
| Q16 | Josie's Real Plan | B | Bring Halden the finished journal and let him read the last pages. | **Journal Part Two** (Patchouli chapter 2) — the Works was going to be a power plant; Bigger Reactors recipes revealed but not yet craftable | Q15, Q6 |
| Q17 | Setting the Table | C | Place a 12-seat Handcrafted long table in the square with a place setting for every resident. | Table settings, centerpiece, everyone's favorite dish revealed in-book, 40 Valley Scrip | Q6, Q7, Q12 |

### Act III finale — **The Harvest Supper**
Triggered by Q17.
- `/time set 13000` (golden hour), title: *"The Harvest Supper — Autumn, Year One."*
- `/fill` the square with harvest decor: pumpkins, hay, Supplementaries candle holders, hanging lanterns; `/place` the granary's finished façade and a town noticeboard.
- Summon all eight residents seated at the table, each with a dialog line about the year so far. Pip's duckling is at the table. Wisp brings three more Ribbits.
- Every player receives a **Harvest Gift** from each resident: Marnie's pie, Bram's brass toolbox, Oda's ledger page, Nella's smoked trout, Halden's tonic, Tobin's copper nugget, Wisp's basket, Pip's drawing (a written book).
- **The turn:** at the end of the meal, snow starts (`/weather` + Serene Seasons winter). Oda says the line the act was built on: *"That's the last warm night. Let's not lose anybody this year."*
- Unlock stage `act4`, world border to 10,000, Nether access opens (Nether's Delight, reactor fuel line).
- Journal entry 4 unlocks.

---

## ACT IV — WINTER: *The Longest Night*

**Story beat.** The crisis, played warm and never grim. Nothing kills anybody. What happens is that the valley gets *cold and dark and boring* — crops stop, the lake freezes, Nella loses her work, Marnie's stores run down, the Ribbits can't stay in the marsh, and the town crowds into one building. The fix is the thing Josie never finished: the Works becomes a reactor, the reactor heats a greenhouse, and the valley grows food in January for the first time in its history.

**Goal, in one sentence:** *"Keep everyone warm and fed through winter, and finish Josie's power plant so the valley never has to go dark again."*

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | The Hearth Goes Out | C | Sleep one night after the Harvest Supper, then follow Pip to the inn. | Everyone gathers at the inn; the Winter chapter opens; firewood ×64, warm cloak, hot cocoa recipe | A3 finale |
| Q2 | Firewood for Eight Houses | C | Deliver 16 firewood bundles to each of Marnie, Halden, Nella and Oda. | Each gives a gift back (blanket, tonic, smoked fish, lamp oil); friendship +1 each; sleigh bells | Q1 |
| Q3 | The Reed Village Comes In | C | Take Wisp's boat downstream and bring the Ribbits back to the inn. | **4 Ribbit residents added** to town; frog village decor set; Wisp friendship max | Q2 |
| Q4 | Soup for a Full Room | C | Cook one Farmer's Delight stew large enough to feed twelve and serve it at the inn. | Marnie's friendship max; her recipe book (10 recipes); the Hearth relights (block change) | Q3 |
| Q5 | Ice Fishing | C | Cut a hole in the frozen lake and catch 8 winter fish with Aquaculture. | Nella's friendship tier 3; ice auger; winter tackle; the "Nella needs work" beat opens | Q3 |
| Q6 | The Cold Frame | C | Build a small greenhouse shell at the square: glass, Macaw's windows, a Handcrafted door, and 8 planters. | Greenhouse shell registered; planters placed; **but nothing grows yet — it's too cold** | Q4 |
| Q7 | Halden's Rounds | C | Brew 8 winter tonics with HerbalBrews and deliver one to every resident. | Halden's friendship max; his half of Josie's recipe book; medicine cabinet; "healthy" stage | Q2 |
| Q8 | Pip's Winter Job | C | Complete 5 of Pip's courier deliveries around town in one day. | Pip's friendship max; his duckling grows up; **Duck Plushie**; courier satchel (speed boost in town) | Q2 |
| Q9 | Open the Works | T | Clear the collapsed adit at the Kettle copper works and set a waystone inside. | Works waystone; Josie's tool chest (steel tools); Artifact from the deep chest; drilling stage | A3Q16 |
| Q10 | The Grid | T | Run Fluxducts from the mill to the Works and install 2 more Thermal Energy Cells. | Energy Cell ×2 pre-made, Thermal Dynamics servo/filter set, "grid" stage | Q9 |
| Q11 | Autocrafting | T | Set up 8 AE2 Crafting Patterns and a Molecular Assembler so the network builds parts for you. | Crafting CPU (pre-made, 32k), pattern set for every reactor component, ME Interface ×4 | Q10, A3Q15 |
| Q12 | Yellorium | T | Mine the yellorium the deep survey found and process 64 ore through the Pulverizer and Smelter. | Yellorium ingots ×128, reactor casing ×64 (auto-crafted via Q11), radiation-free confirmation in-book | Q11 |
| Q13 | Build the Vessel | T | Assemble a Bigger Reactors reactor: casing, controller, fuel rods, control rods, and an access port. | Reactor computer port, redstone port, Josie's original blueprint framed as a decor item | Q12 |
| Q14 | The Turbine | T | Add a Bigger Reactors turbine and connect it to the grid through the Energy Cells. | Turbine housing kit (pre-made), coils, "reactor_ready" stage — the lever is now live | Q13 |
| Q15 | Wire the Greenhouse | B | Run Fluxduct from the Energy Cells to 6 Thermal heaters inside the cold frame. | Heaters placed; greenhouse registered; **waiting on power** | Q14, Q6 |
| Q16 | Bring Bram | C | Go get Bram from the mill. He will say no. Bring him anyway (give him hot cocoa). | Bram's friendship max; his father's wrench; the lever quest unlocks | Q4, Q14 |
| Q17 | Tobin's Numbers | T | Let Tobin run the safety check: verify fuel, coolant and control rod insertion in the reactor UI. | Tobin's friendship max; his survey rig; "the numbers are good" — finale unlocked | Q16, Q14 |

### Act IV finale — **The Longest Night**
Triggered by Q17. The pack's centerpiece.
- `/time set midnight`, heavy snow, title: *"The Longest Night — Winter, Year One."*
- Summon every resident (all eight plus the four Ribbits) outside the Works, each with one line. Pip rings the bell (`/playsound`).
- The player hands Bram the lever. Bram pulls it (quest completion runs the commands).
- **The world changes:** `/fill` places lit lanterns and glowstone-backed lamp posts down every street and around the square in one instant; the greenhouse heaters activate; `/setblock` lights the inn's Hearth; snow-covered lamps glow. A long, warm chord (`/playsound`).
- Unlock stage `greenhouse_warm` — Serene Seasons growth override inside the registered greenhouse. Give the cozy player a **Winter Seed Pack** (every crop, any season) and a Watering Can that never empties.
- Give the tech lane the **QuarryPlus schematic** (recipe revealed, not yet craftable — it needs Founder's Day Standing).
- Give every player a **Hearthkeeper's Lantern** (Dynamic Lights, permanent) and a plushie of their choice.
- World border stays at 10,000 for now. Journal entry 5 unlocks — the last thing Josie wrote.

---

## ACT V — SECOND SPRING: *Founder's Day*

**Story beat.** The valley survived a winter for the first time in a decade, and people start arriving on their own. Act V is the victory lap with teeth: the town formally re-founds itself, the deed to the Works is signed over to the players, and the quarry finally goes in — not as a strip mine, but as the town's public works. Every resident's arc closes.

**Goal, in one sentence:** *"Re-found the town: finish the square, earn the valley's trust, and sink the quarry that pays for the next hundred years."*

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | Thaw, Again | C | Sleep one night after the Longest Night and walk the square with Marnie. | Spring seed pack, flower crates, "year_two" stage, town noticeboard updated | A4 finale |
| Q2 | The Greenhouse Full | C | Grow one of every Serene Seasons crop inside the warm greenhouse at the same time. | Master gardener's kit; Nella hired as gardener (her arc closes); rare seed set from Wisp | Q1, A4Q15 |
| Q3 | Paint the Town | C | Decorate the square: 12 Supplementaries planters, 6 Macaw's awnings, 4 Handcrafted benches, and 8 flower boxes. | Full decor catalogue unlocked at Oda's for free; "square_finished" stage; Xaero town map art | Q1 |
| Q4 | Eight Favorite Meals | C | Cook and deliver each resident's favorite dish (the book lists them). | Every resident +1 friendship; the Feast recipe; commemorative dish set | Q3 |
| Q5 | The Fishing Derby | C | Catch one of every Aquaculture fish species found in the valley and mount three on the inn wall. | Trophy mounts, Nella's rod (top tier), Fisher's plushie, 50 Valley Scrip | Q2 |
| Q6 | The Last Bounties | B | Clear the entire Bountiful board — 8 bounties in one week. | 150 Valley Scrip; Oda's arc closes (she hands you the ledger); quartermaster's chest | Q4 |
| Q7 | Out Past the Ridge | C | Take the Explorer's Compass to two structures you've never visited and bring back one Artifact from each. | 2 Artifacts, Lootr chest luck upgrade, travel journal pages, Waystone ×2 to place | Q3 |
| Q8 | Deeper and Darker | B | With Tobin, descend to the deep dark layer once and come back with an echo sample. | Deep survey data (needed for the quarry site), Corpse-recovery insurance token, warding lamp | Q7, A4Q17 |
| Q9 | Reactor, Scaled | T | Expand the reactor to a 7×7×7 core and add a second turbine. | Doubled output; "big_power" stage; Thermal augment set; energy readout added to the in-book HUD | A4 finale |
| Q10 | Everything, Everywhere | T | Build a full AE2 setup: 4 storage cells of drives, 2 Crafting CPUs, and wireless access across the whole town. | Wireless booster set; every player gets a wireless terminal; Oda's stock syncs to the network | Q9, A4Q11 |
| Q11 | Founder's Day Standing | B | Reach maximum friendship with six of the eight residents. | **"founders_standing" stage — the QuarryPlus deed is now craftable**; town key; a portrait of the town (framed map) | Q4, Q6, Q8 |
| Q12 | The Deed | B | Craft the Works Deed at the square with the town watching. | Deed item; the residents vote (dialog sequence); Bram signs as witness — his arc closes | Q11 |
| Q13 | Sink the Shaft | T | Place the QuarryPlus machine and its marker at the site Tobin surveyed, and power it from the reactor. | Quarry running; Pump + Filler modules; enchanted quarry upgrade; Tobin's arc closes | Q12, Q9, Q8 |
| Q14 | The First Load | T | Route the quarry's output into the ME network and let it run one full cycle. | Auto-sorting complete; "town_provides" stage — Oda's store restocks itself from the network | Q13, Q10 |
| Q15 | A Bell for the Square | C | Craft and hang a bell in the finished square and ring it once. | Bell placed; every resident comes out; Pip becomes the bell-ringer — his arc closes | Q3, Q14 |
| Q16 | The Feast | C | Cook the Feast — one long table, one dish from every resident, and the Hearth lit. | Feast placed on the table; festival clothes for every player; Marnie's arc closes | Q4, Q15 |

### Act V finale — **Founder's Day**
Triggered by Q16.
- `/time set noon`, clear weather, title: *"Founder's Day — Spring, Year Two."*
- `/place` the finished town: town hall façade, a signpost with every resident's name, a stone bridge, the rebuilt mill roof, banners. `/fill` flower beds and a paved square.
- Summon all residents plus **three new arrivals** (unnamed villagers with Easy NPC skins) walking in on the road — the visible proof the valley is alive again.
- Halden reads the last page of Josie's journal aloud (tellraw sequence).
- Every player receives: the **Kettle Family Deed**, a **Founder's Plaque** (a decor block with their name), a full plushie set, the top-tier backpack, and a **Copper Kettle** trophy to hang over their own hearth.
- Fireworks; a long playsound; the world border opens fully (`/worldborder set 60000000`) with the line: *"The valley's fine now. Go see what's past the ridge — and come home for supper."*
- Unlock the **Endless Seasons** chapter: repeatable festivals, seasonal bounties, new-resident requests, and open building. The story ends; the world doesn't.

---

## 7. Reward philosophy applied

**The rule:** a reward is not a trophy, it is a *shortcut for the next quest*. Nothing in this pack is ever gathered twice, and no quest ever says "collect 64 of X" without the previous quest having handed you 48 of them.

**Example 1 — Act I, Q9 → Q10 → Q11.**
Bram's introduction hands over exactly *12 iron ingots and 24 andesite* — precisely the input for the next quest, "Eight Alloys, No More." Completing that quest awards a **pre-made Mechanical Press plus 8 cogwheels and 8 shafts**, which is the entire bill of materials for the Millstone quest after it. The tech lane's first hour has zero mining in it. Josh goes from "talk to a guy" to "powered millstone" without opening a mineshaft once, which is the specific thing he used to cheat past.

**Example 2 — Act II, Q10 → Q11 → Q12.**
Washing the lake sand awards **64 Washed Silica**, and the very next quest is "craft your first Machine Frame," which consumes silica. Completing *that* quest awards **2 spare Machine Frames and a free Redstone Furnace** — so the Pulverizer quest (Q12) is one craft away instead of a full Thermal bootstrap. The Pulverizer then doubles ore output for everything in Act III, meaning the ore Josh mines in autumn goes twice as far as the ore he mined in summer. Every tier makes the previous grind retroactively cheaper.

**Example 3 — cozy lane, Act III Q5 → Q10 → Act IV Q4.**
"Preserves and Pickles" awards the **Cooking for Blockheads Fridge blueprint** — deliberately unusable until the tech lane powers the kitchen two quests later. When power arrives, the fridge is a single free craft, and the fridge instantly unlocks the entire preserved-food branch. Come Act IV's "Soup for a Full Room" — the quest that needs twelve portions at once — the fridge and the smokehouse mean the ingredients are already in the larder. The wife never does a gathering run for the act's biggest cozy beat; she does the *cooking*, which is the part she actually enjoys.

**Supporting rules baked in everywhere:**
- Any quest that says "go find" comes with the map marker or a pre-set Explorer's Compass in the same reward packet.
- Any quest that needs a tool gives the tool one quest earlier.
- Backpack and storage upgrades land *before* the acts that produce a lot of items, never after.
- Valley Scrip is a grind-delete currency: cozy work buys tech intermediates outright at Oda's.
- Waystones are given liberally. Walking somewhere twice is a design bug.

---

## 8. Multiplayer: second teams and late joiners

**Teams.** FTB Teams with quest progress shared per team. Two supported shapes:

**A. The couple's team (default).** Josh and his wife are one team. Quest completions are shared, so she never sees a tech quest blocking her chapter and he never has to cook. The FTB Quests book is filtered by lane tag on first join: each player picks "I want the cozy path" or "I want the workshop path" once, and the book pins accordingly. Both can see everything; only one lane is pinned. Chapters unlock when *the team* finishes an act, so nobody waits alone.

**B. A friend's own team.** A second team plays the same story from its own homestead. Concretely:
- The friend places their **own Homestead Waystone** anywhere in the valley (the border is shared).
- They do **not** place a second Town Anchor. Instead, their Act I is a compressed 6-quest chapter, *"New Neighbor"*: place your homestead, build a shelter, meet Marnie, plant a plot, get a pet, and **register at the town noticeboard** — which links their team to the existing town anchor.
- All town-wide unlocks (residents present, square built, reactor running, greenhouse warm, store catalogue tier) are **world stages**, not team stages. A second team inherits the town as it currently stands and never re-does the finales.
- The second team's own quests are the *personal* half: their farm, their workshop, their friendships, their house. Friendship is tracked per team, so they get their own arcs with the same residents.
- The lore fits: they are a family who heard the valley had people in it again. Which is exactly what happens in Act V.

**Late joiner catch-up.** A player joining in Act IV should not play three months of spring. KubeJS first-join event checks the current world act stage and grants a **Newcomer's Satchel** scaled to it:
- Act II joiner: Create basics kit + a starter farm crate.
- Act III joiner: the above, plus a Thermal starter set, a backpack, and 100 Valley Scrip.
- Act IV/V joiner: the above, plus AE2 basics, wireless terminal access to the town network, and every town waystone pre-discovered.
Their quest book opens on the *current* chapter with a 4-quest onboarding prelude ("get a bed, meet three people, get a pet, pick a lane"), then merges into the live act. No back-catalog, no wall of options. The completed acts appear in the "Memories" chapter as read-only story, so they can catch up on the narrative in the Patchouli book instead of the quest log.

**Solo continuity.** If a friend leaves, nothing breaks: their homestead becomes a house in town, and a one-line noticeboard quest lets the remaining team adopt any structures or animals they left. Nothing in the story ever requires a specific player to be online.

---

## 9. Journal — Josie Kettle's book (Patchouli)

Five entries, one unlocked per act, each in the same hand and the same voice: practical, warm, a little wry, never sad for long.

---

**Entry 1 — found on the mantle, Act I**

> *If you're reading this you got the letter, and the letter lied a little. The house is not "mostly standing." The house has a chimney and opinions.*
>
> *Here is everything I know about this valley, which took me forty years to learn and will take you one line to read: it doesn't need saving. It needs somebody to be visibly, stubbornly here. Light the fire. Let the smoke go up. Marnie will see it from the inn and she will come up the hill with bread and pretend she was passing.*
>
> *She wasn't passing. Nobody passes here. That's the whole problem and it's also the whole fix.*
>
> *The kettle's copper. It's older than me. Put it on.*

---

**Entry 2 — unlocked at the Thaw Fair, Act I finale**

> *I forgot how loud five people are.*
>
> *We had the Fair today, first one in — I want to say nine years, but Oda would correct me and she'd be right, she always is, she keeps the book. There were four stalls and one of them was a plank on two barrels and Pip sold flowers he picked out of my own garden and charged me for them.*
>
> *Bram got the wheel turning at noon. He stood there with his hands on his hips and said "well." That's the most emotional I have ever seen that man.*
>
> *Write this down somewhere you'll find it in November, when it's dark and you're tired and you're wondering why you're doing this: it's this. It was always going to be this.*

---

**Entry 3 — unlocked at the Lantern Float, Act II finale**

> *Nella was sure nobody would come. She spent all week telling me it was a silly idea, and then she spent all week making lanterns, which is how you know somebody means it.*
>
> *Everyone came. Wisp brought the whole reed village and they sang something in frog that I think was about soup. Halden cried and said it was the smoke.*
>
> *A thing I've noticed about summer here: it gives you more than you can hold. Fish, fruit, light, hours. And every single year we let most of it rot because we had nowhere to put it. That's not a farming problem. That's an engineering problem, and I have been calling it a farming problem for thirty years because I was afraid of the other kind.*
>
> *I'm going to stop doing that. I bought a book about turbines.*

---

**Entry 4 — Halden gives you the second half, Act III**

> *Halden, if you're the one reading this to somebody: yes, tell them. I don't mind anymore.*
>
> *The Works was never going to be a mine. I was going to build a power plant. Copper, then brass, then a boiler, then something a great deal past a boiler, and the point of it — the entire point, the only point — was that this valley loses people every winter. Not to anything dramatic. To cold rooms and empty larders and four months of nothing to do. People leave in February and they don't come back in April.*
>
> *You cannot fix that with kindness. I tried. I was extremely kind for three decades and Old Dell still left.*
>
> *You fix it with heat and light in January. That's it. That's the whole design document.*
>
> *I got about halfway and then I got old. The plans are in the crate under the bench, and Bram will tell you they don't work, and Bram is wrong, he's just never had enough hands. You have hands. Go on.*

---

**Entry 5 — the last page, unlocked at the Longest Night, Act IV finale**

> *Last one. The writing's gone shaky so I'll be brief, which Marnie will tell you is a first.*
>
> *If the lights are on out there — if you're reading this warm, in the dark half of the year, with the greenhouse going and somebody's kid asleep by the fire — then it worked, and it wasn't me who did it, and that's exactly right. I only ever got the valley to hold on. You got it to stay.*
>
> *Don't turn it into a monument. Don't put my name on the square. Put a bell there. Ring it when supper's ready.*
>
> *And when somebody new comes up the road next spring — and they will, they always do when there's smoke — go out and meet them. Bring bread. Pretend you were passing.*
>
> *— J.K.*
