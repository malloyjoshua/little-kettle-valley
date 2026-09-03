# LANTERNWICK — Story Document

## 1. Pack name and tagline

**Candidates**

1. **Lanternwick** — the valley is named for its lamps and the wick that fed them; the whole pack is about relighting things.
2. **Copperkettle Hollow** — warmer, more kitchen-forward, but it undersells the tech lane.
3. **The Long Wick** — evocative, but reads slightly ominous, and "long" implies grind, which is exactly what we're avoiding.

**Chosen: LANTERNWICK**

**Tagline:** *The lamps went out. You showed up with a letter, a shovel, and all the time in the world.*

---

## 2. Premise (what the player is told on first join)

You are handed a letter before you can move. It is from your great-aunt, **Marigold Wick**, who died last autumn at a very great age and left you everything she had, which is: a leaning cottage, a field full of weeds, a rusted lamp-post, and a valley called Lanternwick that used to be full of people. The letter says the valley ran on one thing — the old mill on the river, whose wheel turned a line of lamps called the Wick Line all the way from the water to the town square. When the wheel stopped, the lamps went out. When the lamps went out, people stopped staying. Seven of them stayed anyway, and they are still there, and Marigold's last written wish was that somebody warm the place back up. She left you her journal with her plans in it, only half finished. She was not worried about you. Her exact words: *"You will not have to guess. I wrote it all down. Start with the porch."*

---

## 3. The setting

### The valley

**Lanternwick** is a river valley with a town of about a dozen buildings, half of them dark and boarded. The river runs down from a wooded ridge, through the **Old Mill**, past the **Flooded Dock**, and out into a marsh where the **frog-folk of Marshbottom** (Ribbits) keep to themselves because nobody has come to trade in years. Above the town, on a slope of exposed stone, is **Marigold's homestead**: a cottage, a well, a field, and a lamp-post with no lamp on it.

### What is broken

Three specific, nameable things — not a vague malaise:

1. **The Mill wheel is stopped.** No power. Without it the bakery oven is cold, the pumps are dead, and the lamps are dark.
2. **The Wick Line is dark.** A run of lamp-posts from the mill to the town square. Every act relights a section of it, so progress is literally visible from anywhere in town at night.
3. **The town is mostly empty.** Seven residents remain. Empty, marked lots sit between the occupied houses, waiting.

### What restoring it means

Restoring Lanternwick means three counters going up, and the player can see all three without opening a menu:

- **Lamps lit** on the Wick Line (0 → 40 by the finale).
- **Houses with someone in them** (7 → 14).
- **The wheel turning**, then the machines humming, then the reactor's glow behind the ridge.

Nothing in the pack is a boss fight. Nothing is lost if you fail. Mobs are heavily suppressed near town by Torchmaster lanterns given as early rewards, and death drops a Corpse you can walk back to. The stakes are: *it would be nice if these people had their town back.*

### How a non-creative player stays oriented

This is the single most important design constraint in the pack, so it gets explicit rules:

- **A moving world border.** The world starts at a **1,500-block** border centered on spawn — big enough to never feel like a cage, small enough that "wander until lost" is impossible. Each act finale expands it: 1,500 → 2,500 → 3,500 → 5,000 → 8,000 → unlocked at the Lantern Festival. The border expansion is announced as a story event ("Juniper has walked the north ridge and marked it safe"), not a technical one.
- **Waystones are given, never found.** Every waystone in the story is placed by a quest reward command or handed to the player with a quest that says exactly where to put it. Travel is always: open the waystone list, pick the name, go. Named waystones: Homestead, Town Square, Old Mill, Marshbottom, Flooded Dock, Ridge Cabin, Deep Survey, Reactor Yard.
- **The map is pre-marked.** Xaero's waypoints are pushed as quest rewards at the same moment the quest that needs them unlocks. She is never told "explore"; she is told "there is a marker on your map called *Nan's Bakery*, go there."
- **Explorer's Compass is never open-ended.** Every quest that uses it names the exact structure to search for and gives the compass a target in the quest text: "Open the Explorer's Compass and search for *Ribbits Village*. Click it. Follow the arrow."
- **One chapter, one pin.** The quest book opens on exactly one visible chapter. Inside it, quests unlock in a chain — usually one or two available at a time, never a grid of twelve. There is a permanent pinned **"Today"** objective at the top of the screen with one sentence in it. Chapters for future acts are hidden, not greyed out, so there is no wall to feel behind on.
- **Every quest task is literal.** No quest ever says "build a base" or "make it nice." It says "place a bed, a door, and one window, and put a lantern on the wall." Decoration quests give a checklist of exact block counts, and the reward includes the blocks, so she is arranging, not sourcing.

---

## 4. Cast

Eight residents. Seven living, plus Marigold, who is dead and does all her talking through the journal.

### Marigold Wick — the voice in the book (both lanes)
**Role:** Your great-aunt. Deceased. Speaks only through the Patchouli journal, which gains a chapter at each act finale.
**Want:** For the valley not to end with her.
**Arc:** (1) A capable, funny old woman giving instructions. (2) Slowly you notice the handwriting getting shakier and the plans getting more ambitious, not less. (3) The last chapter is not a plan at all — it's a thank-you note written before there was anything to thank you for.

### Corwin Ashgrove — the millwright's son (TECH)
**Role:** The only person left who understands the mill. Lives in a shed behind it, not in it.
**Want:** To find out whether it was the machine that failed or him.
**Arc:** (1) *"It's stone and rust, don't waste your afternoon."* He'll take your andesite, but he won't come look. (2) He comes to look. He does not touch anything, he just watches the wheel turn and asks you to do it again. (3) He moves into the mill house and starts leaving you upgrade parts on the doorstep with notes that say things like *"try this on the smelter, I've been thinking about it."*

### Nan Pepperwhistle — the baker (COZY)
**Role:** Keeps the bakery swept and the oven cold. Has not baked for a customer in four years.
**Want:** To bake for a full room again.
**Arc:** (1) Feeds you for free and refuses your payment, which is her way of saying she doesn't expect you to stay. (2) The oven is relit; she starts a menu board and complains about your flour delivery being late, which is the happiest she has been in years. (3) She hands you her recipe tin and asks you to teach whoever moves in next.

### Gus Halloway — the fisherman (COZY, unblocked by TECH)
**Role:** Fishes the shallow end of a dock that is two-thirds underwater since the pumps died.
**Want:** The deep water back. The good fish are out there and he can see them.
**Arc:** (1) Cheerful about it in a way that is obviously a coping strategy. Trades you tackle for cooked meals. (2) The dock is pumped dry; he gets very quiet, then goes and gets his father's rod out of a chest. (3) He runs an ice-fishing day in winter and teaches Pip to cast.

### Juniper Vale — the ranger (BOTH)
**Role:** Maps the ridge, keeps the roads walkable, sleeps in a different place every week.
**Want:** To stop moving. Won't admit it.
**Arc:** (1) Gives you the Explorer's Compass and the good waypoints, then leaves before you can say thanks. (2) Starts leaving supply caches for you, which is a person building a routine. (3) You build her a cabin on the ridge. She argues about it, then puts a doormat down.

### Odette Quill — the archivist (BOTH)
**Role:** Ran the town hall. Now runs a table in the town hall with all the town's paper stacked on it.
**Want:** Someone to hand the archive to before it turns to mulch.
**Arc:** (1) Has Marigold's letters and will only give them to you one at a time, because she has decided that's how you'll stay. (2) You recover the lost **Wick Ledger** from the town hall ruin; she cries, apologizes for crying, and keeps working. (3) She reopens the archive as a library, and it is the building the new residents go to first.

### Dr. Sable Finch — the surveyor (TECH)
**Role:** Geologist. Camped at the edge of town with a prospector's pick and a lot of unfinished charts.
**Want:** To finish the deep survey her mentor abandoned. She needs power and storage she doesn't have.
**Arc:** (1) All business. Will trade you ore locations for materials, no small talk. (2) You wire her camp into the network; she starts eating dinner in town. (3) She names the big vein after her mentor and asks you to come see it, which for Sable is a hug.

### Bramble Tuck — envoy of Marshbottom (COZY)
**Role:** A frog-folk elder from the marsh village downriver. Comes as far as the bridge and no further.
**Want:** For the trade road to be safe and lit again, so his people can come to market.
**Arc:** (1) Accepts a cooked meal at the bridge, politely, and hops home. (2) You build the bridge and light the path; he brings two others with him. (3) A full Marshbottom delegation arrives for the Lantern Festival with gifts, and stays.

### Pip Marrow — the kid (COZY)
**Role:** Eleven. Runs the bounty board because nobody else was doing it. Collects plushies.
**Want:** A pet, and to be genuinely useful to an adult.
**Arc:** (1) Hands you your first bounty and watches to see if you actually do it. (2) You bring her a tamed animal; she names it immediately and badly. (3) She's given the plushie shelf in the rebuilt town hall and appoints herself festival organizer.

---

## 5. The two lanes and how they gate each other

**The Tech Lane (Josh)** — Create → Thermal → Applied Energistics → Bigger Reactors → QuarryPlus, strictly in that order, each unlocked by a KubeJS stage granted at an act finale.

**The Cozy Lane (his wife)** — Farmer's Delight cooking → animals and pets → Aquaculture fishing → Serene Seasons crops → decorating with Supplementaries / Macaw's / Handcrafted → guided exploration with Explorer's Compass.

**The connective tissue: the Wick Ledger.** Odette keeps a ledger of what the town owes and is owed. Mechanically it's a set of KubeJS stages that only flip when *both* lanes have delivered. Neither player can sprint ahead alone, and neither ever has to do the other's work — they have to hand each other things.

### Cross-lane dependencies (concrete)

1. **Nan's oven needs Corwin's power; Corwin's mill needs Nan's grain.** Act 2 ends only when the tech lane delivers a precision mechanism to the mill *and* the cozy lane delivers a cake baked in a real oven. The mill has nothing to grind without a farm; the farm has no flour without the millstone.
2. **Gus's deep dock needs Thermal pumps.** The cozy lane's best fishing content (rare Aquaculture species, the fish mounts, Gus's whole arc beat 2 and 3) is physically underwater until the tech lane builds fluid ducts and pumps out the dock in Act 3. Cozy player is *unblocked by* tech, and visibly so — the water level drops.
3. **Sable's ore survey needs Juniper's map work.** The Geolosys deep vein in Act 4 can only be marked after the cozy lane has used the Explorer's Compass to find and clear three surface structures that Sable needs as survey anchors. Tech player literally cannot start the big vein until cozy player has gone exploring.
4. **The AE2 network needs a stocked pantry to justify itself — and the pantry needs the network.** Act 4 requires an ME export bus that keeps Nan's bakery pantry topped up with 64 flour at all times. The tech lane builds the automation; the cozy lane has to have six different Farmer's Delight dishes on the menu board first, or Nan has no pantry to stock.
5. **The reactor's coolant loop needs the cozy lane's winter.** In Act 5 the reactor build requires ice and snow blocks harvested during Serene Seasons winter, which is a cozy-lane task with its own greenhouse quests attached. Tech player waits on a season; cozy player gets a whole winter chapter out of it.
6. **The QuarryPlus site needs a waystone the cozy lane places.** The quarry can only be started at the Deep Survey waystone, which is a reward for the cozy lane's Act 4 exploration chain. The tech lane's biggest toy is unlocked by his wife's fieldwork.
7. **Every cute thing is a tech reward, and every ore is a cozy reward.** Deliberate crossover: tech-lane quest rewards include plushies, pets, and decor blocks that go straight into her hands; cozy-lane quest rewards include ore bundles, coal, and machine casings that go straight into his. Neither player can hoard their own lane's payoff.
8. **The Wick Line itself.** Every act's finale lamp section needs the tech lane to run the power and the cozy lane to place and decorate the posts. A lit lamp is the visible proof that two people cooperated.

---

## 6. The five acts

Quest format: `Qn. Title | lane | task | reward | depends on`
Quest counts: Act 1 = 16, Act 2 = 17, Act 3 = 19, Act 4 = 18, Act 5 = 19. **Total: 89.**

---

### ACT 1 — "A Letter, a Lantern, a Lot of Weeds"

**Beat:** You arrive with nothing but instructions. Marigold's voice is warm and specific. Two people in town notice you, and neither expects you to still be here next week.

**Goal, in one sentence:** *Claim Aunt Marigold's homestead and get the first lamp on the post lit.*

**Quests**

Q1. The Letter | both | Right-click the letter in your inventory and read all four pages. | Marigold's Journal (Patchouli), 8 bread, 16 torches, a stone pickaxe | —
Q2. Set Down Roots | both | Place the Homestead Waystone anywhere you like the look of. Name it "Homestead." | 3 more waystones for later, a bed, a Xaero waypoint on your position | Q1
Q3. Sweep the Porch | cozy | Clear away 30 blocks of grass, vines, and leaves within sight of the waystone. | Handcrafted table and 2 chairs, a Supplementaries flower box, a bundle of dirt and grass | Q2
Q4. A Roof That Holds | cozy | Build any shelter with a door, one window, and a bed inside. | Macaw's door + 6 windows + a roof kit, 4 lanterns | Q2
Q5. The First Furrow | cozy | Till 9 blocks of ground and plant wheat in all of them. | Farmer's Delight knife, watering can, 3 kinds of seeds, a scarecrow | Q4
Q6. Something to Feed | cozy | Lead 2 chickens back to your farm with seeds and fence them in. | Handcrafted coop decor, a nest box, 1 duck egg | Q5
Q7. The Cold Oven | cozy | Walk the road east to the Town Square and talk to Nan Pepperwhistle. | Town Square waystone unlocked, 8 cookies, Nan's map marker | Q2
Q8. Bread for One | cozy | Cook any meal in a Farmer's Delight cooking pot over a campfire. | Cooking for Blockheads cookbook + kitchen counter + sink | Q7
Q9. Stone in the Hand | tech | Mine 32 cobblestone and 8 coal from the outcrop below the homestead. | **Vein Mining unlocked**, iron pickaxe, 16 iron | Q2
Q10. Andesite Alley | tech | Take 16 andesite to Corwin Ashgrove at the shed behind the mill. | Old Mill waystone unlocked, Create starter: hand crank, 8 cogwheels, 8 shafts | Q9
Q11. The Millwright's Crank | tech | Build a Create millstone, crank it by hand, and grind 8 wheat into flour. | Create gearbox and belt kit, Corwin's first real sentence | Q10, Q5
Q12. Nothing Gets In | both | Place a Torchmaster lantern in the middle of your homestead. | Peaceful nights near home, 2 spare lanterns for the town | Q4
Q13. Pip's Board | cozy | Meet Pip Marrow at the bounty board in the square and finish one bounty. | First plushie, 12 emeralds, Bountiful board unlocked at home | Q7
Q14. Juniper's Compass | both | Meet Juniper Vale on the north road. Open the Explorer's Compass she gives you and search for "Village." | Explorer's Compass, Nature's Compass, 3 map waypoints | Q7
Q15. Carry More | both | Craft a Sophisticated Backpack. | Two backpack upgrades, a Storage Drawers starter set | Q9
Q16. **The Lamp on the Post** | both | Bring 1 flour to Corwin and 1 fresh loaf to Nan, then place the lamp on the empty post in the town square. | *Act finale* | Q11, Q8, Q13

**Finale event — "The First Lamp"**
On completion, a command chain runs at the Town Square waystone: a small lit arch is built with `fill` and `setblock` (fence posts, lanterns, a hanging sign reading *Lanternwick*) on a flattened pad, so it works on any terrain. Night is set with `/time`, a bell plays, and a title card reads **"The first lamp is lit."** Easy NPC **Odette Quill** is summoned at the town hall steps carrying the archive crate and greets both players by name. The KubeJS stage `act2` unlocks the Create chapter. The world border expands 1,500 → 2,500 with a tellraw from Juniper: *"North ridge is walked and marked. It's safe as far as the cairn."* Both players are given a Journal chapter unlock and, for the cozy player, a cat.

---

### ACT 2 — "Wheels and Wheat"

**Beat:** Corwin stops pretending he doesn't care. The mill's water wheel turns for the first time in four years, and the sound of it brings Nan out of the bakery.

**Goal, in one sentence:** *Get the old mill turning and the fields feeding the town.*

**Quests**

Q17. The Millwright's Confession | tech | Talk to Corwin inside the mill. Read the blueprint page he gives you. | Mill blueprint (journal page), 32 andesite alloy | Q16
Q18. Water Wheel | tech | Build a Create large water wheel on the river beside the mill. | 16 shafts, 8 gearboxes, 32 belts | Q17
Q19. Belts and Boxes | tech | Move an item at least 8 blocks along belts and drop it into a chest. | Storage Drawers expansion, a drawer controller | Q18
Q20. Saw It Yourself | tech | Build a mechanical saw and cut 64 logs into planks with it. | Macaw's roofs + fences pack, 2 stacks of planks | Q19
Q21. Press and Basin | tech | Build a mechanical press and make 16 iron sheets. | Zinc ore bundle, a Create mixer recipe page | Q20
Q22. The Brass Age | tech | Build a mechanical mixer and a heated basin, and make 16 brass ingots. | Brass casing kit, 8 gold | Q21
Q23. First Precision | tech | Craft a precision mechanism. | Deployer, mechanical crafter set, Corwin arc beat 2 dialog | Q22
Q24. Flour Forever | tech | Automate wheat into flour on belts and deliver 32 flour to Nan's counter. | Nan's oven part, 3 plushies (hand these to your partner), 16 iron | Q23, Q11
Q25. Nan's Oven Relit | cozy | Build a Cooking for Blockheads kitchen with an oven, a fridge, and a counter, then bake one cake in it. | **Bakery recipes unlocked**, bakery shopfront kit, Nan arc beat 2 | Q24
Q26. The Four Seasons | cozy | Read the Almanac page, then plant one crop that suits the season you're in right now. | Serene Seasons Almanac, greenhouse glass x64, 4 seed packets | Q16
Q27. Cows and Comfort | cozy | Bring home 2 cows and 2 sheep and fence them in a pen at least 9x9. | Handcrafted barn set, milk churn, a Farm & Charm trough | Q26
Q28. The Duck Pond | cozy | Dig a 5x5 pond, fill it with water, and settle 2 ducks on it. | Duckling plushie, lily decor, 3 more ducks | Q27
Q29. First Cast | cozy | Craft an Aquaculture fishing rod and catch 5 fish with it. | Tackle box, fish mount, 2 better hooks | Q26
Q30. Gus at the Flooded Dock | cozy | Take 3 cooked fish to Gus Halloway at the dock south of town. | Flooded Dock waystone, boat, dock decor bundle, Gus arc beat 1 | Q29
Q31. Bramble at the Bridge | cozy | Open the Explorer's Compass, search "Ribbits Village," follow it, and give Bramble Tuck one cooked meal. | Marshbottom waystone, lily pad decor, a frog friend, Bramble arc beat 1 | Q29
Q32. Vinery Row | cozy | Plant 9 grape vines and build a Let's Do Vinery press. | Wine barrels, 6 bottles, a cellar rack set | Q26
Q33. Herb Beds | cozy | Plant 6 herbs and build one HerbalBrews teapot station. | Teapot, 3 tea leaves, a cozy tea-cart | Q32
**Q34. The Wheel Turns** | both | Deliver 1 precision mechanism to Corwin and 1 cake plus 32 flour to Nan. | *Act finale* | Q23, Q25

**Finale event — "The Wheel Turns"**
A command chain builds the mill house shell around Corwin's water wheel: a `fill` stone pad, plank walls, and a `setblock` water wheel and shafts, plus two lit lamp-posts extending the Wick Line out of the mill. Easy NPC Corwin is despawned from the shed and re-summoned inside the mill house with new dialog. A **Mill waystone** is set. Sound: a low creak, then a bell. Title: **"The wheel turns."** KubeJS unlocks stage `thermal`, and the Thermal chapter appears. Josh receives a Thermal starter (redstone furnace parts, a dynamo, a Thermal manual). The cozy player receives a horse, a second plushie set, and a bundle of Macaw's and Handcrafted furniture. World border 2,500 → 3,500. Journal chapter 2 unlocks.

---

### ACT 3 — "Heat, Hearth, and the Wick Line"

**Beat:** The valley stops being a place you're fixing and starts being a place you live. Real machines, real meals, real neighbours. Three new people move in because there is somewhere to move into.

**Goal, in one sentence:** *Power the town with real machines and fill the empty houses.*

**Quests**

Q35. Sable Finch Arrives | tech | Meet Dr. Sable Finch at her camp east of the square. | Geolosys prospector's pick, sample kit, Sable's map markers | Q34
Q36. Read the Rock | tech | Use the prospector's pick until you find a copper cluster, then mine 64 copper from it. | Waypoint on the cluster, 32 tin, 16 lead | Q35
Q37. Redstone Furnace | tech | Build a Thermal redstone furnace. | Thermal manual, 4 machine frames | Q36
Q38. Something to Burn | tech | Build a dynamo and run the furnace off it. | Energy cell frame parts, 32 coal | Q37
Q39. The First Cell | tech | Craft an energy cell and charge it to full. | Charging pad, a portable charger, 8 signalum parts | Q38
Q40. Pulverize It | tech | Build a pulverizer and double 64 ore with it. | 2 augments, 32 iron | Q39
Q41. Induction Heat | tech | Build an induction smelter and make 32 alloy ingots. | Thermal upgrade kit, machine speed augments | Q40
Q42. Fluid Lines | tech | Build a Thermal fluid duct run and move water 16 blocks into a tank. | Pump parts, 16 more ducts | Q41
Q43. Drain the Dock | tech | Place 3 pumps at the markers Gus gives you and pump the flooded dock dry. | **Deep fishing unlocked**, Gus arc beat 2, a Thermal fisher | Q42, Q30
Q44. The Wick Line Cable | tech | Run energy ducts from the mill to the town square and power 3 lamp blocks. | 12 lamp blocks, 32 ducts, 2 charged cells | Q39
Q45. Nan's Bakery Opens | cozy | Cook 6 different Farmer's Delight or Bakery dishes and put one of each on the bakery menu shelf. | Nan arc beat 3, recipe tin, 6 shopfront decor pieces | Q25
Q46. The Tavern Table | cozy | Build a Candlelight counter with 4 seats and a lit candle on each table. | Candlelight set, 4 stools, NPCs start visiting | Q45
Q47. Tea for Everyone | cozy | Brew 3 different teas and give one to Odette, one to Juniper, one to Pip. | Cozy buffs, 3 teacups, friendship dialog with all three | Q33
Q48. Odette's Archive | cozy | Open the Explorer's Compass, search for a library structure, and bring Odette 5 books and 16 paper. | Odette arc beat 2, Journal chapter 3, bookshelf set | Q35
Q49. A House for Someone | cozy | Build a 7x7 cottage on the marked empty lot: bed, door, 2 windows, a light, a table, a chair. | A new resident moves in (Easy NPC summoned), housewarming basket | Q46
Q50. Pip's Pet | cozy | Tame a cat, a dog, or a parrot and bring it to Pip in the square. | Pip arc beat 2, full plushie set of 6, a pet bed | Q49
Q51. Ruins on the Map | cozy | Open the Explorer's Compass, search "Tavern," travel there, and open 3 Lootr chests. | An Artifact, a waystone to place there, 2 map waypoints | Q48
Q52. The Deep Dock Catch | cozy | Catch 3 rare fish from the drained deep end of the dock. | Gus arc beat 3, 2 fish trophies, a fishing hut kit | Q43
Q53. Winter Beds | cozy | Build a 7x7 greenhouse out of glass and keep 3 crops alive through a season change. | Serene Seasons greenhouse upgrade, 6 seed packets | Q26
**Q54. Light the Wick Line** | both | Deliver 1 fully charged energy cell to Corwin and place 12 lamp posts along the marked path from the mill to the square. | *Act finale* | Q44, Q49

**Finale event — "The Wick Line"**
A `fill` command lays a lit lamp run along a fixed axis from the Town Square waystone on a levelled pad, so no specific terrain is required. `/time set night`, a long bell, fireworks summoned along the line, title: **"The Wick Line is lit."** Three Easy NPCs are summoned as new residents outside the new cottage and walk into town. Stage `ae2` unlocks the Applied Energistics chapter and Josh gets a starter (certus seeds, inscriber parts, 8 fluix). The cozy player gets a wardrobe bundle of Supplementaries, Macaw's and Handcrafted decor plus two pets. **Deep Survey waystone** is granted as a placeable item to the cozy player. World border 3,500 → 5,000. Journal chapter 3 unlocks.

---

### ACT 4 — "The Deep Ledger"

**Beat:** The town works. Now it needs a memory. Odette's lost ledger turns up, Sable finally gets her survey, and the network learns to keep track of everything so nobody has to.

**Goal, in one sentence:** *Build a storage network that remembers everything, and open the deep survey.*

**Quests**

Q55. Certus Seeds | tech | Grow 32 certus quartz crystals in water. | 16 fluix, a growth accelerator, 32 nether quartz | Q54
Q56. The Inscriber | tech | Build an inscriber and make 8 logic processors. | 2 more inscribers, press set | Q55
Q57. First Drive | tech | Build an ME drive, a controller, and a terminal, and store 1,000 items in it. | 4 storage cells, a cell workbench | Q56
Q58. Crafting Terminal | tech | Upgrade to a crafting terminal and craft anything through it. | Pattern provider, 8 patterns | Q57
Q59. Autocraft It | tech | Set an autocrafting pattern so the network can make iron gears on demand. | Molecular assembler set, 8 crafting co-processors | Q58
Q60. Wireless | tech | Craft a wireless terminal and an access point, and use the terminal 32 blocks from the network. | Wireless booster, a spare terminal for your partner | Q59
Q61. The Bakery Subnet | tech | Run an ME export bus that keeps Nan's pantry stocked with 64 flour at all times. | Nan's standing order, 3 plushies, a pantry decor set | Q60, Q45
Q62. Sable's Anchors | tech | Place 4 Geolosys survey markers at the 4 points Sable marks on your map. | Survey charts, 32 lead, Sable arc beat 2 | Q35
Q63. The Big Vein | tech | Follow Sable's charts to the deep deposit and mine 256 ore from it. | Sable arc beat 3, a named vein, ore bundles for both players | Q62, Q68
Q64. Torch the Mine Road | both | Place 4 Torchmaster lanterns along the road from town to the vein. | Safe road, 8 lanterns, a mine cart track kit | Q63
Q65. Deeper and Darker | both | Open the Explorer's Compass, search for an Ancient City, travel there, and bring back one relic. | An Artifact, a warden-safe charm, Journal chapter 4 | Q64
Q66. The Lost Ledger | cozy | Search the ruined town hall for the Wick Ledger and bring it to Odette. | Odette arc beat 3, library kit, town hall restored as a build site | Q48
Q67. The Town Square | cozy | Build the square: a fountain, 4 benches, 4 lamps, 2 flower beds, and a signpost. | Supplementaries fountain kit, benches, 64 flowers, 8 lamps | Q66
Q68. Market Day | cozy | Fill 6 barrels with 6 different foods and set them out under the market awning. | Market stall kit, awnings, NPC shoppers arrive, a market waypoint | Q67
Q69. Bramble's Bridge | cozy | Build a path and a bridge from the square to Marshbottom and place a waystone at the far end. | Bramble arc beat 2, 2 frog-folk visitors, marsh decor set | Q31, Q67
Q70. Juniper's Cabin | cozy | Build Juniper a 9x9 cabin on the ridge: bed, fireplace, table, 2 chairs, a map on the wall. | Juniper arc beat 3, Ridge Cabin waystone, a doormat | Q51
Q71. Pip's Menagerie | cozy | Bring 5 different tamed animals to the square and pen them. | Pip arc beat 3, 8 plushies, a menagerie sign | Q50
Q72. The Empty Lots | cozy | Build 2 more cottages on the 2 marked lots, each with a bed, door, window, light, and table. | 2 new residents move in, 2 housewarming baskets | Q67
**Q73. The Ledger Balanced** | both | Deliver a wireless terminal to Sable and one full market barrel to Nan. | *Act finale* | Q60, Q68, Q66

**Finale event — "The Deep Ledger"**
A `fill`/`setblock` chain raises a timber headframe and a lit shaft entrance over the deep vein, on a levelled pad at the **Deep Survey waystone** the cozy player placed. Easy NPC Juniper is despawned and re-summoned inside her new ridge cabin with new dialog; Easy NPC Bramble is re-summoned in the town square with two companions. Odette is given the Ledger book item on a lectern in the restored hall. Title: **"The Deep Ledger opens."** Stages `reactors` and `quarry` unlock. Josh gets a Bigger Reactors starter (yellorium bundle, casing parts, the reactor manual) and a QuarryPlus frame kit. The cozy player gets the Festival Tent kit, a mount, and a full plushie set. World border 5,000 → 8,000. Journal chapter 4 unlocks.

---

### ACT 5 — "The Long Winter Lights"

**Beat:** Winter comes and the valley is warm for the first time in years. The reactor lights behind the ridge, the quarry hums, the tables are full, and everyone Marigold wrote about is standing in the square.

**Goal, in one sentence:** *Build the reactor, open the quarry, and hold the Lantern Festival.*

**Quests**

Q74. Yellorite Hunt | tech | Follow Sable's charts to the yellorite deposit and mine 128 of it. | Yellorium ingots, a Geiger charm, 32 graphite | Q73
Q75. Reactor Casings | tech | Build 64 reactor casings and 8 control rods. | Reactor manual page, 16 more casings | Q74
Q76. The Core | tech | Build a working Bigger Reactors reactor at least 5x5x5 and start it. | Reactor Yard waystone, reactor computer port | Q75
Q77. Steam and Spin | tech | Build a turbine and feed it from the reactor. | Turbine blades, 4 coils, a control panel kit | Q76
Q78. The Cell Bank | tech | Charge 4 energy cells to full from the reactor. | 4 more cells, a bank frame, a lamp array | Q77
Q79. Coolant | tech | Take 128 ice or snow blocks that your partner harvested this winter and run the reactor's coolant loop. | Reactor efficiency upgrade, a cold room decor kit | Q78, Q83
Q80. Quarry Frame | tech | Build a QuarryPlus machine and its markers at the Deep Survey waystone. | Quarry upgrades, a pump module | Q73
Q81. Mark the Ground | tech | Set the quarry markers to a square no larger than 64x64, well clear of town. | A "good neighbour" note from Odette, 32 lapis | Q80
Q82. Quarry Online | tech | Power the quarry from the reactor and run it until it clears one layer. | Fortune module, silk module, ore bundles for both players | Q81, Q78
Q83. The Cold Months | cozy | When winter arrives, keep 3 crops alive in the greenhouse and harvest 128 ice or snow blocks. | Winter seed packets, a snow decor set, ice for the reactor | Q53
Q84. Warm Coats | cozy | Cook 3 winter dishes and hand one each to Nan, Gus, and Corwin. | 3 friendship dialogs, a coat rack, 6 warm meals | Q83
Q85. Gus's Ice Fishing | cozy | Cut a hole in the frozen river and catch 3 winter fish. | Gus's ice hut kit, 2 trophies, Pip learns to cast | Q83, Q52
Q86. Bramble's Delegation | cozy | Take 3 gifts down the lit road to Marshbottom and invite the village to the festival. | Bramble arc beat 3, marsh lanterns, 4 frog-folk guests | Q69
Q87. The Last House | cozy | Build the final cottage on the last empty lot: bed, door, 2 windows, fireplace, table, 2 chairs. | Final resident moves in, the housewarming feast basket | Q72
Q88. Pip's Plushie Shelf | cozy | Place 8 plushies on the shelf in the restored town hall. | Pip's thank-you note, 4 rare plushies, a toy chest | Q71, Q66
Q89. Nan's Banquet | cozy | Cook 9 different dishes and set them on the long table in the square. | Nan's recipe tin (all recipes unlocked), banquet decor, 9 place settings | Q84, Q45
Q90. Marigold's Porch | cozy | Read the last journal chapter, then place Marigold's lantern on the empty post at her old cottage. | Journal chapter 5, Marigold's lantern, a memorial bench | Q88
Q91. String the Lights | both | Place 40 lanterns along the paths between the mill, the square, the dock, and Marshbottom. | 64 spare lanterns, bunting, festival banners | Q87, Q86
**Q92. The Lantern Festival** | both | Deliver 1 charged reactor cell to the Wick Line panel and light the banquet table. | *Act finale* | Q78, Q89, Q91

**Finale event — "The Lantern Festival"**
`/time set night`. Every lamp block on the Wick Line is lit with a `fill` pass. Fireworks are summoned in a timed sequence over the square. All eight Easy NPCs — Corwin, Nan, Gus, Juniper, Odette, Sable, Bramble, Pip — plus the six new residents and the Marshbottom delegation are summoned or teleported around the long table, each with new festival dialog. A `fill`/`setblock` chain raises a lantern arch and Marigold's memorial post beside the fountain. Title: **"Lanternwick."** Subtitle: *"Forty lamps. Fourteen houses. One valley."* Both players are given a Festival Lantern item that never burns out, and a copy of the completed journal.

The stage `open_valley` unlocks a permanent post-game chapter: seasonal festival quests that repeat each Serene Seasons year, an endless Bountiful board through Pip, Sable's rotating ore contracts for the tech lane, and Nan's rotating menu challenges for the cozy lane. The world border is lifted with one last tellraw from Juniper: *"Go on then. It's all walked."*

---

## 7. Reward philosophy applied

**The rule:** no reward is a trophy. Every reward is a tool that makes the next quest shorter, and it arrives *one quest before* it's needed, so the player never notices they were about to have a bad time.

**Example 1 — Vein Mining arrives before the first real mining.**
Q9 ("Stone in the Hand") asks for 32 cobblestone and 8 coal, which is a two-minute job, and pays out with the **Vein Mining stage unlocked** plus an iron pickaxe. The very next mining quest is Q36 ("Read the Rock"), which asks for 64 copper from a Geolosys cluster — a number that would be a twenty-minute grind with a stone pick and one block per swing, and is about three minutes with vein mining and iron. The grind never happens because the tool that deletes it was the reward for the tutorial version of the same task.

**Example 2 — The energy cell arrives before the pumps.**
Q39 ("The First Cell") pays a charged energy cell and a portable charger. The next tech objective, Q42–Q43, is running fluid ducts and pumping the flooded dock dry — a task that in a normal pack means babysitting a furnace generator with coal for twenty minutes. With the cell already charged and in hand, the player places pumps, plugs in the cell, and watches the water drop. The reward converted a fuel-logistics chore into a placement puzzle. It also immediately unblocks his wife's fishing content, so the payoff lands twice.

**Example 3 — The ME network arrives before the decorating marathon.**
Q57–Q60 build the ME drive, crafting terminal, and wireless terminal, finishing with a **spare wireless terminal handed to the cozy player**. The very next chapter is Act 4's build block: the town square, the market stalls, Juniper's cabin, and two cottages — hundreds of decor blocks that would otherwise mean rummaging through fourteen chests. Instead she opens one wireless terminal, types "lantern," and takes what she needs from anywhere in town. The tech lane's biggest abstraction becomes the cozy lane's biggest quality-of-life jump, in the same act.

**Bonus, cozy side —** Q29 ("First Cast") pays a tackle box and two better hooks; Q52 ("The Deep Dock Catch") asks for 3 rare fish, which is a coin-flip with a plain rod and near-certain with the hooks. And every waystone in the pack is a reward, never a craft, so travel time to the *next* objective shrinks the moment you finish the current one.

---

## 8. Multiplayer

**Teams.** FTB Teams runs three shapes without any story rewrite:

- **The Wick Family** — Josh and his wife share one team, one homestead, one quest book progression. Spine quests complete for the team; lane quests are still authored per-lane so each of them has their own pinned objective at all times.
- **The Newcomers** — a friend or a pair of friends form a second team. They are not a second copy of the story; they are the second wave of settlers Marigold's letter mentions.
- **Solo drop-in** — a friend who joins the couple's team, gets the current chapter, and picks up whatever isn't pinned.

**How a second team enters.** Odette Quill has a second letter. When a new team is created, a KubeJS join event gives every member a **Letter of Invitation** and opens a short private chapter called **"The Second Letter."** In it, Marigold wrote to more than one relative — she wrote to the whole family, because she was not a woman who put all her eggs in one nephew. The second team is told the same thing the first was: pick a spot, place a waystone, start with the porch. They get their own homestead and their own farm, and their lots in town are on the *other* side of the square, so the town visibly grows from two directions.

**How a late joiner catches up.** A six-quest onboarding chapter, **"You Missed the Weather,"** granted automatically on first join at any point in the story:

1. Read the Letter of Invitation.
2. Place your own waystone and name it.
3. Go see Odette, who gives you every waystone the town has already unlocked, the current Xaero waypoint set, and the journal chapters written so far.
4. Go see Nan, who feeds you and gives you a starter food stack scaled to the current act.
5. Go see Corwin or Pip — tech-leaning joiners get Corwin and a machine starter kit for the current tier; cozy-leaning joiners get Pip, a plushie, a pet, and a decor bundle. The quest asks which one you'd rather visit; that single choice sets their lane.
6. Claim a lot in town.

On completion, KubeJS grants the joiner **every stage the host team has already unlocked** and drops them straight into the current act's chapter, at the current pinned objective. They are never behind, they never have to be walked through four acts of backfill, and the fiction covers it: they are a relative who got the letter late and came anyway.

**Team-safe quest design.** Spine quests (the finale deliveries, the stage unlocks) are team-completion, so nobody blocks anybody. Personal quests (Pip's bounty board, Nan's menu challenges, Sable's ore contracts) are per-player and repeatable, so any number of people always have something to do. Every act finale event runs once per world, and the tellraw addresses everyone present by name — including anybody who joined this morning.

---

## 9. Journal — five entries from Marigold Wick

*(Patchouli book, one chapter unlocked per act finale. Handwriting gets shakier in the later chapters; the art direction is a note that gets scratchier and warmer at the same time.)*

---

**Entry 1 — Chapter One, "Start with the Porch"**

> If you're reading this you've either inherited the place or you're being nosy, and either way, hello.
>
> Here is the only advice I'll give you all at once, so don't skip it: do not look at the whole valley. It will flatten you. I looked at the whole valley once, in about my sixtieth year, and I sat down on the step and did not get up for a day and a half.
>
> Look at the porch. It is eleven feet of porch and it has weeds on it. Pull the weeds. Then look up and see if you feel like looking at anything bigger.
>
> That's it. That's the whole trick. I have used it on a broken wheel, a dead orchard, and one very bad winter, and it has not failed me yet.

---

**Entry 2 — Chapter Two, "On Corwin"**

> The boy who won't come out of the shed behind the mill is Corwin, and he is not a boy anymore, he's forty-one and he still won't come out of the shed.
>
> His father ran that mill and Corwin ran it after him, and when the wheel finally seized it was nobody's fault and everybody's, and Corwin has spent four years deciding it was only his.
>
> Don't argue with him about it. I tried arguing with him about it for two years and got a lot of exercise. What you do is you turn the wheel where he can hear it. That's all. He will come out on his own or he won't, and if he does it will be because he wanted to, which is the only reason anybody ever comes out of a shed.

---

**Entry 3 — Chapter Three, "The Wick Line"**

> Forty lamps, mill to square. I counted them on my hands when I was small and my mother told me to stop pointing.
>
> People think I want the lamps back for the light. There is plenty of light. It's a valley, the sun comes up.
>
> I want them back because when the lamps were lit you could see, from your own window, that other people were still awake. That's the whole thing. That's what a town is. Not the buildings. The knowledge, at ten at night in February, that you are not the only one with a lamp on.
>
> Nan Pepperwhistle has kept her bakery swept every single day for four years and has not baked one loaf for a customer. Think about that until it makes you angry. Then go and bring her some flour.

---

**Entry 4 — Chapter Four, "What I Got Wrong"**

> I've been at this a long time and I want to put down, honestly, the mistake, in case you're about to make it.
>
> I thought I had to do it myself. I thought if I asked, I'd be admitting the valley was too much for me, and if the valley was too much for me then I had no business being the one who stayed.
>
> That was vanity dressed up as duty and it cost me about fifteen years.
>
> Sable Finch has charts I could never have read. Juniper knows roads I never walked. Odette has kept every piece of paper this town ever produced in a stack on her desk because nobody asked her for it. Bramble's people would have come back at any point in the last four years if somebody had simply gone down to the bridge and said please.
>
> Ask. I'm asking you, so I suppose I've finally learned.

---

**Entry 5 — Chapter Five, "The Last Page"**

> I'm going to be honest, I don't expect this to work.
>
> I'm writing plans for a mill I won't see turn, for a lamp line I won't see lit, to be read by somebody whose name I don't know yet and who has, let's be fair, no particular reason to care about a valley they've never been to.
>
> But I keep writing them. And I've thought about why, and here it is.
>
> Everything I know how to do, somebody taught me on a bad afternoon when they had better things to do. My mother taught me the porch trick. Corwin's father taught me to read a wheel. A woman whose name I have genuinely forgotten taught me to bank an oven so it holds overnight, in about ninety seconds, in the rain, because I looked cold.
>
> None of them saw what I did with it. That's normal. That's the arrangement.
>
> So: the wheel goes counter-clockwise, the third lamp post leans and always has, and Nan takes her tea far too strong.
>
> Thank you for coming. I mean it. Put a lamp on my porch when you get a minute — I'd like to be on the line.
>
> — M.W.

---

*End of story document. Next step: convert to FTB Quests chapter files, KubeJS stage gates, Easy NPC spawn commands, and the Patchouli book JSON.*
