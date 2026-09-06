# Quest Book Audit — lens: VETERAN (Tekkit-era tech player, FTB Evolution fan)

Little Kettle Valley, MC 1.20.1 Forge, FTB Quests. Read-only audit of `story/quests/*.json`
against `docs/research/book-redesign.md`. Judging PACING and PLAYABILITY only — feasibility,
numbers, pointers, toasts and coords were already linted (`scratch/book_lint.txt`).

What this lens wants: Thermal, AE2, a reactor and a real world. Evolution's cadence —
every quest gives XP, most give an item or a loot crate, a third are optional, deps ~1.04,
one idea per quest, mods not gated. A grind wall is a count that buys no new mechanic.

Format: `TIMELINE` lines are `key | est minutes | doing`. Findings are numbered `V-nn`.

---

## Chapter: Read Me First (`readme.json`) — 11 quests, all gear/info

TIMELINE
```
rm_book        | 1 | read how tabs work
readme_hands   | 1 | how to Minecraft
readme_night   | 1 | eat/sleep/F3
rm_next        | 1 | toast explainer
rm_folk        | 1 | eight neighbours
rm_lanes       | 1 | cozy lane vs reactor
rm_oda         | 1 | Oda sells the dull half
rm_journal     | 1 | journal + compass
rm_order       | 1 | order barely matters
rm_notimer     | 1 | no timers
rm_world       | 1 | one map
```
Chapter total ~8-11 min of reading. Correctly all-optional, all `gear`, no gates. No pacing
problem — a veteran ticks these in one sitting for the free XP.

### V-01 (minor) — `rm_lanes` / readme.json — the Read Me tells the cozy player where to start and tells the tech player nothing, so a Thermal/AE2 player leaves the intro with no lane to walk.
`rm_lanes` names the cozy lane and points at `&6Farm and Seasons&r`, but the tech half of the
pack (Create/Thermal/Power/Storage Network/Ores/Reactor — six chapters, ~110 quests) is
described only as "&cfive quests in winter&r need the reactor". That reads as a tax, not an
invitation. This is the one page every player reads.

FIX — `rm_lanes.description`, line 3 (currently):
`"Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."`
NEW (replace that one line with two, keeping the blank-line break style):
`"The other lane is machines: start in &6Create&r, then &6Thermal&r, &6Power and Logistics&r and &6Storage Network&r. None of it is gated."`
`""`
`"Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."`

---

## Chapter: Start Here (`start.json`) — 8 quests, q01-q08

TIMELINE
```
q01 |  3 | read the letter, collect the starter kit
q02 |  4 | walk -319 74 32, set the Home waystone
q03 |  2 | hang door/2 windows/bed/sconce
q04 |  1 | place the megatorch
q05 |  4 | dig 40 gravel, find the sealed iron door
q06 |  4 | campfire + kettle + cook one vegetable soup
q07 |  4 | walk to -302 69 -44, drive the stake
q08 |  2 | sleep; Marnie, Bram and the inn open
```
Chapter total ~24 min. Good shape — three walks, three builds, one cook, one sleep, and every
quest hands something forward. q01's reward block is the pack's best (kettle, waystone,
backpack, iron tools, food, megatorch) and is exactly Evolution's "loot dump on quest one".
No findings.

---

## Chapter: Act I — The Thaw (`act1.json`) — 13 quests, q09-q19

TIMELINE
```
q09  |  5 | till + plant 27 marked tiles
q10  |  4 | 23 fence footings, gate, 3 hen crates
q11  |  3 | 3 eggs (feed the hens to skip the wait)
q12  |  3 | walk west to the mill, take Bram's bolt
q13a |  1 | stone hammer + prospector's pick off the bench
q13b |  8 | read hematite samples, dig 15 down, 8 iron clusters  << first real mining
q13  |  2 | craft 8 andesite alloy                              << first Create craft
q14  |  5 | millstone + hand crank, 16 flour                    << FIRST MACHINE
q15  |  6 | smelt 32 green oak planks (10s each)
q16  |  5 | 2 water wheels on the race, belt the millstone      << first automation
q17  |  9 | 22 logs -> 128 planks on the mechanical saw
q18  |  8 | fit the inn kitchen, cook 3 dishes
q19  |  4 | sweep the store, 16 flour + 8 bread — Act I finale
```
Chapter ~63 min. **First machine (hand-cranked millstone): ~1h00 from world join.**
**First self-turning machine (water wheel + belted millstone): ~1h15.**

Act I is the best-paced chapter in the book for this lens: a mine, a craft, a hand-powered
machine, then the same machine driven by water — four beats, each one a new verb, and the
rewards run ahead of the asks (q13 hands a Mechanical Press, q16 hands Saw + Basin + Mixer +
32 alloy). That is Evolution's cadence exactly.

### V-02 (major) — `q18` / act1.json — the Act I finale is locked behind a quest the book labels optional, so a player who trusts the label softlocks the act.
`q18` is `optional: true`, and `q19` (the finale) has `deps: ["q17","q18"]`. FTB Quests still
enforces the dep; the optional flag only changes the icon and the completion maths. A veteran
skips furnishing quests on sight — that is what the flag trains him to do — and then finds the
act's last quest greyed out with no explanation.
This pattern repeats: `q33`→q32/q37, `q39`→q52, `q42`→q43/q47, `q48a`→q51a, `q54a`→q56,
`q66a`→q68a, `q68a`→q70a, `q78`→q79/q89, `q80`→q85. Deps are frozen; the flag is not.

FIX — for every story quest that another quest depends on, drop the optional flag and say so
in the text instead. Concretely for `q18`:
- field `optional`: OLD `true` → NEW: remove the key (or `false`)
- field `shape`: OLD `"rsquare"` → NEW `"square"`
- field `description`, append as a new last line:
  `"Marnie's kitchen is where Act I ends: &6q19&r wants bread off this oven."`
Apply the same three-part change to `q33`, `q39`, `q42`, `q48a`, `q54a`, `q66a`, `q68a`,
`q78`, `q80`. (Leave `q24`, `q61`, `q62`, `q63`, `q70a`, `q72a`, `q84a` optional — nothing
depends on them, so the flag is honest there.)

### V-03 (minor) — `q15` / act1.json — 32 furnace smelts at 10s each is 5m20s of standing in front of one furnace, the only dead stretch in Act I.
No new mechanic, no decision. A veteran builds three more furnaces and the problem is his own
solution, but the quest never suggests it and Act I has no other idle beat.

FIX — `q15.description`, line 3 (currently):
`"Bram cannot build a Water Wheel until these dry, and the furnace is you. The kitchen kit comes with them: see &6Cooking and Brewing&r."`
NEW:
`"Bram cannot build a Water Wheel until these dry. One furnace is five minutes; four furnaces is one. Kitchen kit comes with them: &6Cooking and Brewing&r."`

---

## Chapter: Act II — The Long Days (`act2.json`) — 18 quests, q20-q37

TIMELINE
```
q20  |  6 | walk to the Ribbit village, 4 red toadstools
q21  |  3 | walk to the lake, Nella's token
q22  |  8 | 10 fish (honour box) + 1 cooked cod on a skillet
q23  |  5 | bone-meal 8+8+8 flowers, carry to Halden
q24  |  6 | OPT trellis, 4 grape starts, wait for fruit
q25  |  4 | fence the pasture, 2 cows + 2 sheep
q26  |  5 | 8 dredge pulls -> 128 lake sand (handed straight back)
q27  |  3 | walk to the copper outcrop, Tobin's token
q28  |  5 | 6 prospector readings
q29  |  4 | windmill bearing + 8 sails on the mill roof
q30  |  3 | 16 bench batches -> 64 washed silica
q31  |  3 | first Thermal machine frame
q33  |  6 | 6 drawers + controller + 3 barrels
q32  | 10 | pulverizer + stirling dynamo, 32 iron dust   << FIRST THERMAL MACHINE / FIRST RF
q34  |  6 | energy duct to 4 posts, light 2
q35  |  6 | fit out Wisp's stilt house
q36  |  3 | 24 paper lanterns
q37  | 10 | 24 wheat + 8 cooked cod + 8 white wool — Act II finale
```
Chapter ~96 min. **First Thermal machine and first RF (q32): ~2h10 from world join**
(critical path q19→q21→q22→q26→q30→q31→q33→q32; ~42 min after the Act I finale).

### V-04 (major) — `q33` / act2.json — the pack's first Thermal machine sits behind a shelving-and-barrels quest that the book flags optional.
`q32` ("Run 32 Iron Ore Through a Pulverizer" — the first Thermal machine, the first dynamo,
the first RF in the pack) has `deps: ["q33"]`, and `q33` is `optional: true`. So the single
most important tech beat in the first two acts is reachable only through a decorating quest
that the UI tells the player to skip. `q33` also gates the Act II finale `q37`.

FIX — same shape as V-02, applied to `q33`:
- field `optional`: OLD `true` → NEW: remove the key
- field `shape`: OLD `"rsquare"` → NEW `"square"`
- field `subtitle`: OLD `"Six drawers, a controller, three barrels."`
  NEW `"The bench before the machines. Not skippable."`
- field `description`, last line: OLD
  `"One controller makes six drawers one inventory. More of that in &6Power and Logistics&r."`
  NEW `"One controller makes six drawers one inventory. The Pulverizer goes in this room next — more in &6Power and Logistics&r."`

### V-05 (major) — `q37` / act2.json — 8 cooked cod as an act-finale gate is a fishing grind wall, because Aquaculture dilutes the loot pool so vanilla cod is one catch in dozens.
`q22` asks for one cooked cod and that is fine as a lesson. `q37` asks for eight more of the
same specific vanilla fish with Aquaculture's species table in play — 30-60 casts of nothing
new. It is the last bar in front of the Lantern Float and it teaches nothing q22 did not.

FIX — `q37.tasks[1].count`: OLD `8` → NEW `4`, and
`q37.description` line 2: OLD
`"Take 24 wheat off your fields, 8 &acooked cod&r off Nella's lake and 8 &awhite wool&r off Cloud and Also Cloud, and hand all three notices in at the board outside the store."`
NEW `"Take 24 wheat off your fields, 4 &acooked cod&r off Nella's lake and 8 &awhite wool&r off Cloud and Also Cloud, and hand all three notices in at the board outside the store."`
(If the count must stay at 8, the alternative is to say where cod is dense: add a line
`"Cod bite in open deep water, not the shallows. Worms on the hook double the rate."`)

### V-06 (minor) — `q34` / act2.json — the quest warns the player off a Redstone Furnace he has not been given and no quest has mentioned.
`"The &cRedstone Furnace&r eats power; leave it off this line."` is a warning about a machine
that first appears in the Thermal chapter. A veteran reads it as "you already made a mistake".

FIX — `q34.description`, line 2, replace the final sentence:
OLD `"The &cRedstone Furnace&r eats power; leave it off this line."`
NEW `"One Stirling Dynamo runs two lamps and no more — a second dynamo comes with the next reward."`

### V-07 (minor) — act2.json — nine straight quests between the Act I finale and the windmill with no machine in them; the tech player's first dead stretch.
q20-q28 is toadstools, a token, fishing, flowers, fences, a token and six pick readings. The
story earns it, but the book never tells a machines-first player that he can walk away and
come back. The chapter subtitle promises "power the workshop" and then withholds it for ~40 min.

FIX — `q20.description`, append one line (this is the first quest of the act):
`"Machines can run ahead of this: the &6Create&r and &6Thermal&r chapters need nothing from Act II. Come back for the lake when you want the silica."`

---

## Chapter: Act III — The Harvest Debt (`act3.json`) — 23 quests, q38-q56

TIMELINE
```
q38  |  2 | Oda's token, the winter count
q39  |  6 | 12 oak full drawers into the granary alcoves
q40  |  4 | sow pumpkin / beetroot / oat / barley
q41  |  4 | 3 spring water bottles + Josie's 16 certus
q42  | 10 | 4 apple pies, 4 berry jams, 4 pickle jars (taiga trip for berries)
q43  |  8 | 4 bread, 2 chocolate pies, 2 cakes (cocoa = trader or jungle)
q45a |  3 | 3 courier parcels
q44  |  6 | smoke + hang 8 hams
q48a |  4 | fit out two guest rooms
q51a |  5 | 12 rice panicles to Wisp
q54a |  8 | 8 cooked fillets into the granary
q45  |  8 | dig ~90 blocks of Tobin's adit, open the Lootr chest
q46  |  6 | induction smelter, 16 bronze + 16 electrum        << 2nd Thermal machine
q47  |  6 | energy cell + duct to the inn                     << first RF distribution
q48  |  8 | station + 64 track, mill to square                << Steam 'n' Rails
q49  |  2 | unload Oda's wagon
q50  | 20 | grow 32 certus in spring water                    << AE2 starts
q51  |  8 | ME drive + 2x 4k cell + terminal                  << FIRST ME TERMINAL
q52  |  6 | storage bus the granary, wireless terminal
q53  |  5 | export bus into the order-board crate
q54  |  3 | the Kettle Plate to Halden
q55  |  3 | read the cellar wall
q56  |  6 | long table, 12 place settings — Act III finale
```
Chapter ~137 min. **First ME terminal (q51): ~4h10 from world join** playing the book in order
(critical path q38→q40→q41→q42→q45→q46→q47→q50→q51 ≈ 68 min after the Act II finale).
This is the chapter the veteran came for and it delivers: smelter, RF grid, a train, and a
storage network in one act.

### V-08 (major) — `q56` / act3.json — the Act III finale is the only story-act finale with no item and no loot crate; it pays 3 XP for the longest act in the book.
Rewards are `command` + `stage:act4` + `xp_levels 3` + toast. Compare q19 (story_crate +
Explorer's Compass + XP3), q37 (story_crate + Bountiful Decree + XP3), q75 and q91 (two crates
each). Twenty-three quests, ~2h15, and the payoff is a level bar and a popup. In Evolution
terms this is the one place the cadence breaks outright.

FIX — `q56.rewards`, insert item rewards before the `xp_levels` entry (do not touch the
`command`/`stage` entries):
```
{ "type": "item", "item": "handcrafted:oak_table", "count": 2 },
{ "type": "item", "item": "supplementaries:candle_holder", "count": 4 },
{ "type": "item", "item": "thermal:energy_cell", "count": 1 },
{ "type": "item", "item": "ae2:item_storage_cell_16k", "count": 1 },
{ "type": "item", "item": "valley:scrip", "count": 40 }
```
and `xp_levels`: OLD `3` → NEW `3` (unchanged; the act finales already sit at the cap).

### V-09 (major) — `q42` / act3.json — running the first RF line into town is gated behind four apple pies, four jams and four jars of pickles.
`q47` ("Run Energy Duct to the Inn") has `deps: ["q46","q42"]`. `q42` is a cozy preserving
quest, flagged `optional: true`, that also needs a taiga trip for out-of-season berries. A
machines-first player is stopped mid-grid by jam. The dep is frozen, so the honest fix is to
stop calling it optional and to warn about the berries in the quest that needs it.

FIX (two parts):
1. `q42.optional`: OLD `true` → NEW: remove the key; `q42.shape`: OLD `"rsquare"` → NEW `"square"`.
2. `q47.description`, line 2, append: `"The preserves quest feeds this one — Marnie will not open the inn wall until her shelves are up."`

### V-10 (major) — `q51` / act3.json — the story spine builds an ME Drive and Terminal without ever saying how to power an AE2 network.
`q50` hands a Charger and four Growth Accelerators, `q51` asks for a Drive, two 4k cells and a
Terminal. Neither quest mentions the &aEnergy Acceptor&r — the only quest in the pack that does
is `ae_power` in the Storage Network chapter. A player walking the story alone places the drive,
sees a red idle network, and has nothing in the book to search for. This is the pack's clearest
missing engineering instruction.

FIX — `q51.description`, replace line 3:
OLD `"Four more cells and the full bus set come back. The granary is twelve drawers and one screen away."`
NEW `"Power it with an &aEnergy Acceptor&r on the network and your energy duct into that — nothing lights up without one. Four more cells and the full bus set come back."`
and add to `q51.rewards` (before `xp_levels`):
`{ "type": "item", "item": "ae2:energy_acceptor", "count": 2 }`

### V-11 (minor) — `q53` / act3.json — the instruction says an Export Bus takes "patterns"; it takes a filter, and a veteran will hunt for a pattern slot that does not exist.
OLD (description line 2):
`"Place a &aDelivery Crate&r beside Oda's bounty board in the square and point an ME Export Bus at it with the town's standing orders patterned in."`
NEW:
`"Place a &aDelivery Crate&r beside Oda's bounty board in the square and point an ME Export Bus at it. Put bread, planks and lamp oil in the bus's filter slots — nine slots with the upgrade card, one without."`

### V-12 (minor) — `q43` / act3.json — two chocolate pies put a wandering-trader RNG roll or a jungle expedition on the story's critical path.
`q43` gates `q45a`→`q44`→`q48a`→`q51a`→`q54a`→`q56`, i.e. the whole back half of the act. The
quest says where cocoa comes from but not that it may take a while, and gives no fallback.

FIX — `q43.description` line 2, replace the last clause:
OLD `"...cocoa is the one thing this valley does not grow, so it comes off a wandering trader or a jungle pod."`
NEW `"...cocoa is the one thing this valley does not grow. Oda keeps a tin behind the counter — see the &6Oda's Counter&r chapter — or take the jungle pods off a trip east."`

### V-13 (minor) — `q50` / act3.json — twenty minutes of watching quartz grow is the longest idle block in the story and the quest does not say to go and do something else.
Certus growth is AE2's own pacing and stays, but this is the one place the book should push the
player at a parallel chapter.

FIX — `q50.description`, append a line:
`"Growth is slow even accelerated. Set it going and spend the wait in &6Ores and Mining&r or on Oda's board — the crystals keep."`

---

## Chapter: Act IV — The Longest Night (`act4.json`) — 23 quests, q57-q75

TIMELINE
```
q57  |  3 | sleep, walk to the inn, the Hearth is out
q58  |  3 | 4x16 firewood bundles into the stacks (pure hand-back)
q59  |  8 | walk the frozen river, bring four Ribbits home
q60  |  6 | 12 vegetable soup for the long table
q61  | 10 | OPT ice-auger 4 muskellunge + 4 rainbow trout
q62  |  5 | OPT 8 winter tonics at Halden's still
q63  |  4 | OPT 5 courier parcels
q64  |  5 | glaze the greenhouse, 8 planters
q66a |  4 | OPT dress the inn's 12 solstice tiles
q68a |  3 | OPT bake 4 bread with Pip
q70a |  4 | OPT shear + 3 blankets
q72a |  4 | OPT furnish the bathhouse
q65  |  6 | mine 40 blocks, drop into Josie's Works, place the waystone
q66  |  6 | duct mill -> Works, 2 energy cells
q67  |  8 | compass to the Merchant's Tower, the second Kettle Plate  << reactor gate opens
q68  |  6 | molecular assembler + 4k crafting storage   << AE2 autocraft
q69  | 18 | mine + smelt 64 uranium
q70  | 12 | assemble the 78-block vessel, read valid
q71  | 20 | build and tune the turbine to 1,800 RPM     << REACTOR ENGINEERING
q72  | 10 | fluid + energy duct, 6 greenhouse heaters + bathhouse tank
q73  |  3 | walk Bram down with a hot cocoa
q74  | 12 | 29 lamp posts, mill -> square -> lake
q75  |  4 | read the three numbers, hand over the lever — Act IV finale
```
Chapter ~164 min. **Reactor lit (q75): ~7h30 from world join** (critical path
q57→q58→q59→q60→q64→[q65→q66→q67→q68→q69→q70→q71]→q72→q73→q74→q75 ≈ 130 min after the
Harvest Supper). The tech branch hangs off `q55`, so a veteran can run q65-q71 in parallel
with the cozy winter chain — that is the single best structural decision in the book.

### V-14 (blocker) — `q71` / act4.json — the turbine quest lists the parts bill and never explains how RPM is controlled, which is the one step in the pack a player cannot brute-force.
`"Hold 1,800 RPM under load without going over"` is the whole instruction. Bigger Reactors RPM
is set by steam flow rate on the Turbine Terminal (a slider in mB/t), and the coils must be
disengaged while spinning up and engaged once the rotor is near speed — engage them early and
the rotor never reaches 1,800; overshoot and the rotor tears. Nothing in the quest, its
subtitle, or its rewards says any of that, and it is the last bar before the act finale. A
veteran will get there eventually; a first-timer stalls indefinitely on a checkmark he cannot
tick. (Spec calls for a `guide_page` to the journal field notes f6/f7 — the reactor chapter has
them; this quest does not point at them.)

FIX — `q71.description`, replace line 3 (wording taken from `rx_turbine`, which already states
the real model — do not invent a different one):
OLD `"Hold 1,800 RPM under load without going over. The lever goes live."`
NEW three lines (blank string between as elsewhere):
`"RPM is a balance, not a switch: &bmore steam speeds it, more blades or more coil blocks slow it&r. Open the flow a little at a time."`
`""`
`"Press &bT&r and type &b/valley check turbine&r to read RPM, steam in and power out. It settles in about three passes. Josie's field notes f6 and f7 are in the &aValley Journal&r, and &6The Reactor and the Quarry&r chapter builds one from scratch."`

### V-15 (major) — `q69` / act4.json — 64 uranium mined and smelted one-for-one is the pack's largest single-resource ask and buys no new mechanic.
64 ore blocks + 64 furnace smelts, mid-winter, on the critical path to the reactor. The vessel
(`q70`) needs 8 fuel rods, not 64 ingots of fuel; the count is inventory theatre. This is the
one place a Tekkit-era player will put the book down.

FIX — `q69.tasks[0].count`: OLD `64` → NEW `32`, and
`q69.description` line 2: OLD
`"Follow Josie's map from the Works Waystone and mine 64 &aUranium&r. Every block drops a cluster and every cluster smelts one for one. \"Yellorium\" is her shorthand."`
NEW `"Follow Josie's map from the Works Waystone and mine 32 &aUranium&r. Every block drops a cluster and every cluster smelts one for one — a Redstone Furnace or Induction Smelter clears the lot in a minute. \"Yellorium\" is her shorthand."`
(If the 64 must stay, add the same second sentence about running it through a machine — the
grind is the furnace, not the pickaxe.)

### V-16 (minor) — `q58` / act4.json — four tasks of 16 firewood bundles, handed to you 64 at a time in the previous quest's rewards, is a click with no verb in it.
`q57` rewards `valley:firewood_bundle x64`; `q58` asks for 4x16 of the same item. It is a
two-second hand-back dressed as a quest, immediately after the act's opening beat.

FIX — `q58.description`, replace line 2:
OLD `"Put 16 &aFirewood Bundles&r into each of the four marked stacks in the inn's back room. Any order is right."`
NEW `"Put 16 &aFirewood Bundles&r into each of the four marked stacks in the inn's back room. Sixty-four is what Oda gave you and sixty-four is what winter costs — burn any of it and you are cutting more."`
(Leaves the counts alone; makes the hand-back read as a ledger beat rather than a filler quest.)

### V-17 (minor) — `q70` / act4.json — the vessel quest names seven block types and never says the one thing that makes a multiblock valid or invalid.
`"Build it square"` is the only shape guidance for a 78-block assembly whose failure mode is a
terminal that just says invalid. The parts are all given; the geometry is not.

FIX — `q70.description`, replace line 3:
OLD `"Bram's turbine crate comes back — the whole bill for the next quest. For the rest, see &6The Reactor and the Quarry&r."`
NEW `"A hollow box of casing with the ports in the walls, fuel rods standing floor to ceiling inside and a control rod on top of each column. The &bReactor Terminal&r tells you what is wrong. Bram's turbine crate comes back with it — see &6The Reactor and the Quarry&r."`

---

## Chapter: Act V — Second Spring (`act5.json`) — 19 quests, q76-q91

TIMELINE
```
q76           |  3 | sleep, walk the square with Marnie
q77           | 12 | 16 vibrant quartz glass + 4 Thermal crops
q78           |  8 | OPT dress the square's 30 copper tiles
q80           | 10 | OPT bluegill, perch, night catfish + 3 mounts
q83           | 25 | build a SECOND turbine, 25,000 RF on <=60 fuel
q84           |  8 | 2x16k crafting storage, 2 access points, 4 boosters
q84a          |  8 | OPT 8 patterns + pattern providers + level emitters
q86a          |  8 | level the 9x9 rig pad, run the power lane, type the box
q79           | 20 | eight residents' favourite dishes
q81           | 12 | boat to the Cairn and the Drowned Lighthouse
q82           |  8 | echo cave under the Works, one echo shard
q85           |  5 | pay 120 scrip
q86_standing  |  0 | ticks itself at six closed resident chains
q86           |  3 | buy the Works Deed, 80 scrip           << quarry gate
q87           |  6 | quarry on the marker, switch it on
q88           | 10 | 1,024 cobblestone into the granary
q89           |  4 | cast and hang the copper bell
q90           |  3 | the fortieth lamp on Josie's post
q91           |  6 | eight dishes, bank the hearth — Act V finale
```
Chapter ~159 min. **Whole story spine (Start Here + Acts I-V, optionals included): ~10h45.**

### V-18 (major) — `q83` / act5.json — "Build the Second Turbine" is written as a repeat and is actually a 64-casing craft with no parts given and no bill stated.
`q70` supplied exactly one turbine's worth of parts. `q71` returned 16 blades, 4 shafts and a
computer port. `q83`'s only task is the checkmark `"Both turbines at 25,000+ on 60 or less
fuel"` and its description says only `"Build a second turbine off the reactor you already
have"`. The real cost is another 64 Turbine Casing, 16 Turbine Glass, 2 Rotor Bearings, 2 Fluid
Ports and a Terminal, all hand-crafted, and the quest is available the moment Act V opens. A
veteran budgets five minutes and loses forty.

FIX — `q83.description`, replace line 2:
OLD `"Build a second turbine off the reactor you already have, then stand at the terminal, press &bT&r and type &b/valley check power&r."`
NEW `"Build a second turbine off the reactor you already have: another 64 &aTurbine Casing&r, 16 Glass, 2 Rotor Bearings, 2 Fluid Ports and a Terminal, none of it in the crate. Then stand at the terminal, press &bT&r and type &b/valley check power&r."`
and add to `q83.rewards` (before `xp_levels`):
`{ "type": "item", "item": "biggerreactors:turbine_rotor_bearing", "count": 2 },`
`{ "type": "item", "item": "biggerreactors:turbine_fluid_port", "count": 2 }`
(the two parts that are pure iron-and-time and add nothing to the lesson).

### V-19 (major) — `q86_standing` / act5.json — the quarry, the pack's last tech goal, is gated on six closed resident chains, and no tech quest ever says so.
`q86` needs `q86_standing`, which needs six of eight neighbour chains finished — that is the
cozy lane, in bulk. The gate is legitimate and the spec keeps it. The problem is disclosure:
`rm_lanes` tells the player the lanes are separate ("only five quests in winter need the
reactor") and nothing anywhere tells him the traffic runs the other way too. A machines-first
player reaches Act V with the reactor lit and finds the quarry behind eight people's laundry.
It is also the only milestone-shaped quest in the book with no item reward at all.

FIX (two parts):
1. `q86_standing.rewards`, add before `xp_levels`:
   `{ "type": "item", "item": "valley:scrip", "count": 40 },`
   `{ "type": "item", "item": "sophisticatedbackpacks:gold_backpack", "count": 1 }`
2. `rm_lanes.description`, append a line (this pairs with V-01):
   `"It runs both ways: the &6quarry&r at the end wants six neighbours' stories closed, so the cooking is not optional forever."`

### V-20 (minor) — `q91` / act5.json — the last quest in the pack pays less than the one that lit the reactor.
`q75` pays XP 25, two loot crates, the Hearthkeeper's Lantern, a plushie token and 75 Scrip.
`q91` — Founder's Day, the end of the story — pays a netherite backpack, one plushie, one
story crate and XP 3. The curve falls off at the finish line.

FIX — `q91.rewards`: `xp_levels` OLD `3` → NEW `10`, and add before it:
`{ "type": "item", "item": "valley:scrip", "count": 100 },`
`{ "type": "item", "item": "artifacts:lucky_scarf", "count": 1 },`
`{ "type": "item", "item": "handcrafted:blue_plate", "count": 8 }`

### V-21 (minor) — `q88` / act5.json — 1,024 cobblestone is 16 stacks to carry to a hand-in, and the quest does not say the wireless terminal solves that.
The quarry produces it in minutes, so the count is fine; the friction is inventory. The player
has a Wireless Terminal from `q84` and no reason to connect the two.

FIX — `q88.description`, line 2, append:
`"Hand it in off the &aWireless Terminal&r — you do not have to carry sixteen stacks anywhere."`

---

# TECH GROUP

## Chapter: Create (`create.json`) — 25 quests, root `create_alloy` free

TIMELINE
```
create_alloy      |  3 | 8 andesite alloy (chapter root, no deps)
create_shafts     |  2 | 8 shafts + 4 cogwheels
create_crank      |  1 | OPT hand crank
create_wheel      |  4 | water wheel in a stream
create_casing     |  2 | 8 andesite casing
create_millstone  |  5 | millstone + 16 flour
create_press      |  5 | press + 8 iron sheets
create_belt       |  2 | belt between two shafts
create_windmill   |  4 | OPT bearing + 8 sails
create_fan        |  3 | encased fan
create_saw        |  3 | mechanical saw
create_mixer      |  3 | basin + mixer
create_washing    |  5 | OPT wash 16 crushed iron
create_burner     | 25 | NETHER TRIP: empty blaze burner, light it off a blaze
create_brass      |  8 | 16 brass ingots in a heated basin
create_brasscasing|  3 | 8 brass casing
create_goggles    |  2 | OPT engineer's goggles
create_deployer   |  3 | OPT deployer on a depot
create_lamps      |  3 | OPT 8 brass lamps
create_crafters   |  6 | 8 mechanical crafters
create_precision  |  4 | precision mechanism
create_arm        |  4 | OPT mechanical arm
create_track      |  4 | 16 track
create_station    |  5 | station + bogey + seat
create_schedule   |  6 | OPT schedule + conductor's whistle
```
Chapter ~106 min. Structurally the best system chapter in the book: 32% optional, one item
reward on every quest, four `create_crate` drops, a clean chain, XP escalating 2→5 as the
recipes get heavier. This is Evolution's Tech Mods chapter done right.

### V-22 (major) — `create_burner` / create.json — a Nether fortress sits in the middle of the Create chain, gates the eleven quests after it, and the book never tells the player how to reach the Nether or where a portal is.
`create_burner` → `create_brass` → `create_brasscasing` → `create_crafters` → `create_precision`
→ `create_track` → `create_station` → `create_schedule`, plus the goggles/deployer/lamps/arm
branches: 11 of 25 quests behind one blaze. No quest in the book has a `dimension` task, none
mentions obsidian or a portal, and the two ruined portals in the world (-728 232, -600 -408)
are only named in `ex_portal`, in a different group. The quest jumps from "set a mixer over a
basin" to "take it to a nether fortress" in one line.

FIX — `create_burner.description`, add a line between the two existing paragraphs:
`"No portal yet? There is a ruined one in the pines at &b-728, 232&r — see &6Places&r. Ten obsidian and a flint and steel is the other road."`
and `create_burner.subtitle`: OLD `"Heat turns mixing into alloying."`
NEW `"Heat turns mixing into alloying. One trip to the Nether."`

### V-23 (minor) — `create_millstone`, `create_press`, `create_saw`, `create_mixer`, `create_fan` / create.json — the acts hand these machines out as rewards, so a story-first player ticks five chapter quests without building anything.
`q13` gives the Mechanical Press, `q16` gives the Saw, Basin and Mixer, `q14` and `q29` give
Encased Fans. Their chapter quests are `item` tasks on the same block, so they auto-complete on
open. Not a defect — it is a fair reward for having done the story — but the chapter reads as
free ticks and the player never runs the machine the text describes.

FIX — add the run to the task line in the text so a story-first player still learns the verb.
`create_saw.description` line 1: OLD
`"Build a &aMechanical Saw&r, lay it flat and feed it logs off a belt. Stood upright it fells the whole tree."`
NEW `"Already have one from Bram? Lay it flat and feed it logs off a belt anyway — stood upright it fells the whole tree instead."`
Same treatment for `create_press`, `create_mixer`, `create_fan`, `create_millstone`.

---

## Chapter: Thermal (`thermal.json`) — 21 quests, root `thermal_servo` free

TIMELINE
```
thermal_servo      | 3 | 8 redstone servos (root)
thermal_coil       | 3 | 4 RF coils + the RF paragraph
thermal_frame      | 4 | 4 machine frames, both roads
thermal_dynamo     | 4 | stirling dynamo              << first RF generation
thermal_furnace    | 4 | redstone furnace
thermal_wrench     | 2 | OPT wrench
thermal_cell       | 4 | energy cell
thermal_compression| 4 | OPT compression dynamo
thermal_pulverizer | 4 | pulverizer
thermal_sawmill    | 3 | OPT sawmill
thermal_magmatic   | 6 | OPT magmatic dynamo (lava run)
thermal_duct       | 3 | 16 energy duct
thermal_augment    | 3 | OPT speed augment
thermal_capacitor  | 3 | OPT flux capacitor
thermal_smelter    | 4 | induction smelter
thermal_fluid      | 3 | OPT 16 fluid duct + fluid cell
thermal_upgrade    | 4 | OPT hardened upgrade
thermal_innovation | 5 | OPT flux drill + flux saw
thermal_alloys     | 8 | 16 invar + 16 constantan       << the one real production quest
thermal_centrifuge | 4 | centrifuge
thermal_insolator  | 6 | OPT insolator + 16 phytogro
```
Chapter ~80 min. 43% optional, four `flux_crate` drops, an item reward on every quest — the
cadence is right and the writing is the clearest in the book ("a dynamo makes it, a cell holds
it, a duct carries it, a machine spends it").

### V-24 (major) — thermal.json — nineteen of the twenty-one quests tick the moment the block is crafted, so a player can "finish Thermal" without ever powering a single machine.
Only `thermal_alloys` (16 invar + 16 constantan) and `thermal_insolator` (16 phytogro) ask for
something a machine produced. `thermal_pulverizer`, `thermal_furnace`, `thermal_smelter`,
`thermal_centrifuge`, `thermal_sawmill`, all three dynamos and the energy cell complete on the
craft. Compare the Create chapter next door, which asks for 16 flour, 8 iron sheets, 16 brass
and 16 washed crushed iron. A Tekkit-era player finishes this chapter with a shelf of unpowered
boxes and no proof the grid works. (Adding output tasks is outside the frozen scope; the
reachable fix is to make the text demand the run and to raise the two production counts so the
chapter has real weight at its end.)

FIX — three parts:
1. `thermal_pulverizer.description`, replace line 2:
   OLD `"Bram sets you on thirty-two iron in Act II. This is that machine."`
   NEW `"Wire it to the dynamo before you tick this — an unpowered Pulverizer looks exactly like a powered one. Bram sets you on thirty-two iron in Act II on this machine."`
2. `thermal_alloys.tasks[0].count`: OLD `16` → NEW `24`;
   `thermal_alloys.tasks[1].count`: OLD `16` → NEW `24`; and
   `thermal_alloys.subtitle`: OLD `"Two iron and a nickel. Copper and a nickel."`
   NEW `"Twenty-four each. The smelter has to actually run."`
3. `thermal_smelter.description`, append a line:
   `"Run sixteen ore through it with sand in the second slot before you move on — the yield jump is the point, and you cannot see it from the recipe."`

### V-25 (minor) — `thermal_magmatic` / thermal.json — second unheralded Nether requirement ("a fluid duct off a nether pool") in a chapter that never mentions a portal.
Pairs with V-22. The quest is optional, so it is a smaller problem, but it is the same gap.

FIX — `thermal_magmatic.description`, line 2, append:
`"Buckets from the overworld lava lakes work too, and the ruined portal in the pines at &b-728, 232&r is the short way to a pool — see &6Places&r."`

### V-26 (minor) — thermal.json — the chapter never covers itemducts or servos-on-a-duct, so nothing in Thermal ever moves an item on its own.
The spec assigns `fluxducts/itemducts` to Thermal; `thermal_duct` covers energy only and
`thermal_fluid` covers liquid. Item routing lands entirely in `power.json`. A veteran finishes
Thermal still hand-carrying ore to the pulverizer.

FIX — `thermal_duct.description`, append a line:
`"The same craft in itemduct form moves ore into a machine and dust back out. Servos, filters and the rest of the routing are the &6Power and Logistics&r chapter."`

---

## Chapter: Power and Logistics (`power.json`) — 13 quests, root `power_coil` free

TIMELINE
```
power_coil       | 3 | 4 RF coils + the RF paragraph (root)
power_cell       | 3 | energy cell
power_duct       | 3 | 32 energy ducts
power_servo      | 2 | OPT 2 servo attachments
power_mill       | 5 | rolling mill off a shaft
power_wire       | 5 | 16 copper wire + a spool
power_alternator | 6 | alternator on the crafters   << rotation -> RF
power_motor      | 4 | electric motor               << RF -> rotation
power_connector  | 3 | OPT 6 connectors, wire across a gap
power_drawers    | 5 | 4 drawers + controller
power_upgrade    | 3 | OPT 2 iron storage upgrades
power_barrel     | 4 | OPT stack-upgraded barrel
power_link       | 4 | OPT storage controller + 2 links
```
Chapter ~50 min. The Create Addition run (mill → wire → alternator → motor) is the best
four-quest sequence in the pack for this lens: rotation to RF and back, stated as a trade.

### V-27 (major) — power.json (and thermal.json) — the pack never teaches item transport; there is no itemduct, hopper-chain, funnel-routing or servo-on-an-itemduct quest anywhere in 367 quests.
`thermal:item_duct` appears zero times in the whole book — not a task, not a reward, not an
icon, not in any description. `power_servo` is a *Servo Attachment on an energy duct*. The only
item movement the book ever teaches is AE2's import/export buses in Act III. So the progression
is: carry it by hand for six hours, then jump straight to a full ME network. For a Tekkit-era
player that is the missing middle of the entire pack, and `q66` hands out eight
`thermal:filter_attachment` as a reward for a quest that never mentions filters.

FIX — repurpose the existing optional servo quest to cover both duct kinds (task and key stay):
- `power_servo.title`: OLD `"Cap a Duct With a Servo"` → NEW `"Cap a Duct With a Servo"` (unchanged)
- `power_servo.subtitle`: OLD `"It decides which end is the outlet."`
  NEW `"Power ducts and item ducts, same attachment."`
- `power_servo.description`: OLD line 1
  `"Craft two &aServo Attachments&r and put one on the duct face touching the machine you want fed. A bare duct shares power out evenly; a servo makes that end push."`
  NEW (three lines, blank strings between):
  `"Craft two &aServo Attachments&r and put one on the duct face touching the machine you want fed. A bare duct shares power out evenly; a servo makes that end push."`
  `""`
  `"The same attachment goes on an &aItem Duct&r — the item-carrying twin of the energy duct, four to a craft off lead and glass. Servo on the chest end, bare duct on the machine end, and ore walks itself into the Pulverizer."`
  `""`
  `"A &aFilter Attachment&r on the same face picks which items travel. Eight of them come with the Works grid in Act IV."`

### V-28 (minor) — power.json — the chapter's first three quests are a verbatim re-run of the Thermal chapter's first three, so a veteran who did Thermal opens Power to four free ticks.
`power_coil` = `thermal_coil` (4 RF coils), `power_cell` = `thermal_cell`, `power_duct` =
`thermal_duct` (32 vs 16), `power_drawers` overlaps `q33`. Nine of thirteen quests carry new
material. The redundancy is deliberate (either chapter can be an entry point) but nothing says
so, so it reads as padding.

FIX — `power_coil.description`, append a line:
`"Done these in &6Thermal&r already? They tick on sight — this chapter is really the four Create Addition quests and the shelving. Skip down."`

### V-29 (minor) — `power_alternator` / power.json — the chapter's milestone quest pays a loot crate and nothing else, in a chapter where every other quest hands an item.
`power_alternator` rewards are `LOOT power_crate` + XP3. It is the hexagon 1.5 milestone and
the one quest that requires eight Mechanical Crafters from another chapter.

FIX — `power_alternator.rewards`, add before `xp_levels`:
`{ "type": "item", "item": "createaddition:alternator", "count": 1 },`
`{ "type": "item", "item": "createaddition:capacitor", "count": 2 }`

---

## Chapter: Storage Network (`ae2.json`) — 22 quests, root `ae_certus` free

TIMELINE
```
ae_certus     | 10 | 16 certus quartz (root)
ae_silicon    |  4 | 8 silicon
ae_tools      |  2 | OPT certus knife + wrench
ae_charger    |  4 | charger, mod recipe or Halden's spring water
ae_charged    |  5 | 8 charged certus
ae_fluix      |  6 | 16 fluix in standing water
ae_growth     |  4 | OPT 4 growth accelerators
ae_meteorite  | 10 | compass to the crater at -216, 72
ae_skystone   |  5 | OPT 16 smooth sky stone + a chest
ae_presses    |  5 | the four inscriber presses
ae_inscriber  |  3 | inscriber
ae_processors | 25 | 8 logic + 8 calculation + 8 engineering   << the chapter's grind
ae_controller |  5 | ME controller + 16 glass cable
ae_channels   |  1 | OPT gear: channels explained
ae_power      |  4 | energy acceptor + AE energy cell
ae_drive      |  5 | ME drive + 1k cell
ae_cells      |  4 | OPT 4k + 16k
ae_terminal   |  4 | ME terminal                                << FIRST ME TERMINAL (chapter route)
ae_buses      |  4 | OPT import/export/storage bus
ae_wireless   |  5 | OPT access point + wireless terminal
ae_cpu        |  8 | crafting CPU + molecular assembler
ae_patterns   |  8 | pattern terminal + 2 providers + 8 patterns
```
Chapter ~131 min. **First ME terminal by the chapter route: ~1h30 of AE2 work** (root to
`ae_terminal` ≈ 90 min), versus **~4h10 by the story route** (see Act III). Both roads work,
which is exactly what the spec asked for, and the chapter is the best-taught AE2 introduction
in the book — channels, bytes-not-stacks, "two controller blocks touching are one machine".

### V-30 (major) — `ae_processors` / ae2.json — twenty-four processors is roughly seventy-two hand-fed Inscriber operations, placed before the network exists to automate it.
Each processor is print-silicon, print-circuit, then press the pair with redstone. Eight of
each means 24 prints of silicon, 24 of the circuit and 24 assemblies, all by hand, because the
controller, the drive and any bus are still three quests away. It is the longest continuous
click-loop in the pack and it lands one quest before the payoff.

FIX — reduce the counts and promote the automation hint out of the last line:
- `ae_processors.tasks[0].count`: OLD `8` → NEW `4`
- `ae_processors.tasks[1].count`: OLD `8` → NEW `4`
- `ae_processors.tasks[2].count`: OLD `8` → NEW `4`
- `ae_processors.title`: OLD `"Print Eight of Each Processor"` → NEW `"Print Four of Each Processor"`
- `ae_processors.description` line 1: OLD
  `"Inscribe &aPrinted Silicon&r and a printed circuit, then run the pair through again with redstone between them."`
  NEW `"Build three Inscribers and belt them in a row before you start — one prints silicon, one prints the circuit, the third presses the pair with redstone between them. Doing it by hand is seventy-two clicks."`
- `ae_processors.description` line 2: OLD
  `"Eight logic, eight calculation, eight engineering. A belt feeding the &aInscriber&r does all of it for you."`
  NEW `"Four logic, four calculation, four engineering is the controller, the drive, a terminal and a cell. Print more the moment the network can craft them for you."`

### V-31 (minor) — `ae_channels` / ae2.json — channels are explained one quest *after* the controller goes down, which is one quest too late.
`ae_channels` deps `ae_controller`, is optional, and is a gear/info quest. Channel exhaustion is
the single most common AE2 first-network failure, and the book's explanation sits behind the
quest where it first matters.

FIX — `ae_controller.description`, append a line:
`"Every device on it eats a &bchannel&r: eight to a glass cable, thirty-two to a dense one. Read the next quest before you wire eight things off one strand."`

### V-32 (minor) — `ae_certus`, `ae_silicon`, `ae_charger`, `ae_inscriber` / ae2.json — four consecutive quests pay a small stack of the same material and no XP escalation, in the run-up to the chapter's biggest ask.
`ae_certus` XP2, `ae_silicon` XP1, `ae_tools` XP1, `ae_charger` XP2, `ae_charged` XP2 — the
curve is flat through the fifty minutes before the crater. Compare Create, which climbs 2→5.

FIX — `ae_silicon.rewards` `xp_levels`: OLD `1` → NEW `2`;
`ae_fluix.rewards` `xp_levels`: OLD `2` → NEW `3`;
`ae_meteorite.rewards`, add before `xp_levels`:
`{ "type": "item", "item": "ae2:certus_quartz_crystal", "count": 16 }`
(the crater walk is a ten-minute expedition that currently pays sky stone alone).

---

## Chapter: Ores and Mining (`mining.json`) — 16 quests, root `mining_root` free

TIMELINE
```
mining_root           |  2 | stone hammer (root; q13a hands one free)
mining_light          |  3 | 64 torches + 16 ladders
mining_vein           |  6 | the grave key, 32 coal in one seam
mining_samples        |  8 | 12 iron clusters off surface samples
mining_propick        |  2 | prospector's pick
mining_hematite       | 12 | 32 iron, y32-60 dike
mining_hammer_iron    |  2 | OPT iron hammer
mining_beryl          | 10 | OPT 4 emeralds, y-56 to 19
mining_autunite       | 10 | OPT 8 uranium clusters, y8-33
mining_malachite      | 14 | 32 copper clusters, y-16 to 90
mining_tin_lead       | 12 | 8 tin + 8 lead
mining_silver         |  5 | OPT 6 silver out of the same galena
mining_kimberlite     | 15 | 6 diamonds below y10
mining_hammer_diamond |  2 | OPT diamond hammer
mining_meteorite      |  8 | OPT 12 sky stone at -216, 72
mining_pulverizer     |  6 | pulverizer + 16 iron dust
```
Chapter ~117 min. The strongest chapter in the book on pure information density — every bed's
depth, the dike-versus-blanket distinction, "follow it up and down, not sideways", sneak-swing
for single blocks, and the one line a veteran actually wants ("Efficiency before Fortune.
Speed is what a hammer is for"). Five `mining_crate` drops and 38% optional.

### V-33 (minor) — `mining_pulverizer` / mining.json — ore doubling is the last quest in the mining chapter and sits behind six diamonds.
`mining_pulverizer` → `mining_kimberlite` → `mining_tin_lead` → `mining_malachite` →
`mining_hematite` → `mining_propick`: six quests and a diamond hunt before the chapter about
ore tells you ore can be doubled. A Tekkit-era player wants that on hour two, and the Thermal
chapter offers it four quests deep, but nothing here says so.

FIX — `mining_hematite.description`, append a line:
`"Do not smelt a second bed by hand. The &6Thermal&r chapter reaches a Pulverizer in four quests and every ore after that is worth two."`

### V-34 (minor) — `mining_malachite` / mining.json — 32 copper clusters is the chapter's biggest count and the only one that buys nothing new.
Hematite (32 iron) teaches the dike. Tin/lead teaches two beds in one hole. Silver teaches the
by-product. Malachite's 32 is the same swing thirty-two times in the widest, easiest bed in the
game, and it gates tin/lead, kimberlite and everything after.

FIX — `mining_malachite.tasks[0].count`: OLD `32` → NEW `24`, and
`mining_malachite.title`: OLD `"Follow Malachite Down for Copper"` (unchanged), and
`mining_malachite.description` line 2, append:
`"Vein-mine it with the grave key and the bed comes up in a handful of swings."`

### V-35 (minor) — mining.json — nothing in the chapter points at powered mining, so the veteran finishes it still swinging a hammer.
The Flux Drill exists (`thermal_innovation`, and `q65` hands one out charged), never wears out,
and is the natural end of this chapter's argument. No mining quest mentions it.

FIX — `mining_hammer_diamond.description`, append a line:
`"After this the upgrade is not another hammer — it is the &aFlux Drill&r off stored power, in the &6Thermal&r chapter. It never wears out at all."`

---

## Chapter: The Reactor and the Quarry (`reactor.json`) — 16 quests, root `rx_uranium` free, `rx_notes` gated on q67, `rx_quarry` on q86

TIMELINE
```
rx_uranium  | 15 | 16 uranium ingots off autunite (root, ungated)
rx_notes    |  1 | hold Josie's turbine notes            << q67 gate
rx_graphite |  4 | 16 graphite ingots
rx_casing   |  6 | 22 reactor casings
rx_core     |  4 | terminal, port, tap, fuel rod, control rod
rx_vessel   | 10 | 3x3x3 hollow, light it                << REACTOR LIT (chapter route)
rx_glass    |  3 | OPT 12 reactor glass
rx_cyanite  |  6 | OPT cyanite reprocessor -> blutonium
rx_coolant  |  4 | swap the tap for two coolant ports
rx_frame    | 12 | 76 turbine casings + the six specials
rx_rotor    |  4 | 2 shafts, 4 blades, 4 copper blocks
rx_turbine  | 15 | hold 1,800 RPM
rx_second   | 12 | OPT second turbine off the same steam line
rx_quarry   | 12 | workbench plus, quarry, markers        << q86 gate
rx_pump     |  4 | OPT advanced pump
rx_filler   |  4 | OPT filler
```
Chapter ~116 min. **Reactor lit by the chapter route: ~40 min from `rx_notes`** (rx_graphite →
rx_casing → rx_core → rx_vessel), versus **~7h30 by the story route**. Seven `reactor_crate`
drops over sixteen quests — the most generous chapter in the book, and rightly so.

This chapter is the best engineering writing in the pack. `rx_vessel` gives the geometry
("hollow 3x3x3: one Fuel Rod in the middle, a Control Rod on the lid directly above it"),
`rx_coolant` gives the rule that trips everyone ("a vessel has taps or coolant ports, never
both"), and `rx_turbine` gives the actual model ("more blades or more coils slow it; more steam
speeds it... it settles in about three passes"). Every one of those lines is missing from the
story quests that ask for the same builds — see V-14 and V-17.

### V-36 (major) — `rx_uranium` / reactor.json — the chapter root is open, the other fifteen quests are behind a story key the root never names, so a veteran opens the reactor chapter, mines uranium, and hits a wall with no explanation.
`rx_notes` deps `["rx_uranium","q67"]`, and everything downstream chains off `rx_notes`. `q67`
("Fetch the Second Kettle Plate") is roughly 6-7 hours into the story, in Act IV. The root
quest's text says nothing about it: it ends "for bed depths, see the Ores and Mining chapter".

FIX — `rx_uranium.description`, replace line 2:
OLD `"The sample block on the grass sits over the pocket, so dig where the sample is. Sixteen ingots runs a small vessel a long time. For bed depths, see the &6Ores and Mining&r chapter."`
NEW two lines:
`"The sample block on the grass sits over the pocket, so dig where the sample is. Sixteen ingots runs a small vessel a long time. For bed depths, see the &6Ores and Mining&r chapter."`
`""`
`"&cThe rest of this chapter waits on one thing:&r a casing recipe needs a page of Josie's Turbine Notes, and those come out of the Merchant's Tower in Act IV, step 67. Mine the uranium now; it keeps."`

### V-37 (major) — `q71` vs `rx_turbine` / act4.json + reactor.json — the story and the chapter describe two different turbines and neither acknowledges the other, so a player who reads both builds the wrong one.
`rx_rotor`/`rx_turbine` specify a 5x5x4: 2 rotor shafts, 4 blades, 4 copper coil blocks, 76
plain casings. `q71` specifies 64 casing, 16 glass, 2 bearings, **6 shafts, 16 blades and 16
copper blocks**. Those are different machines, and per the chapter's own rule ("more blades or
more coils slow it") a 16-blade rotor needs far more steam to reach 1,800 than the 4-blade one.
The story build is presumably the larger one Bram's crate pays for, but nothing says so, and a
veteran who does the chapter first will size his second turbine off the small numbers.

FIX — `q71.description` line 2, append one sentence:
OLD `"Build the turbine from that crate: 64 &aTurbine Casing&r, 16 Glass, 2 Rotor Bearings one at each end, 6 Shafts, 16 Blades, 2 Fluid Ports and 16 copper blocks for the coil ring."`
NEW `"Build the turbine from that crate: 64 &aTurbine Casing&r, 16 Glass, 2 Rotor Bearings one at each end, 6 Shafts, 16 Blades, 2 Fluid Ports and 16 copper blocks for the coil ring. Bram's crate builds the big one; the &6Reactor&r chapter builds the small 5x5x4 on four blades, and the two are not interchangeable."`

### V-38 (minor) — `rx_uranium` / reactor.json — the chapter's hexagon-2.0 root pays 32 coal for fifteen minutes of uranium mining.
Every other chapter root pays the material forward: `create_alloy` gives 16 alloy + 8 iron,
`thermal_servo` gives 8 servos + 32 redstone, `mining_root` gives 32 torches + 4 iron.

FIX — `rx_uranium.rewards`, add before `xp_levels`:
`{ "type": "item", "item": "biggerreactors:uranium_ingot", "count": 8 },`
`{ "type": "item", "item": "biggerreactors:graphite_ingot", "count": 8 }`
and `xp_levels`: OLD `2` → NEW `3`.

---

# THE VALLEY BEYOND

## Chapter: Places (`explore.json`) — 16 quests, root `ex_pack` free

TIMELINE
```
ex_pack       |  2 | 32 torches + 8 bread (root)
ex_dungeon    | 10 | small dungeon, -424 8
ex_mineshaft  | 12 | oak mineshaft, -312 248
ex_underhouse |  8 | OPT underground house, -344 120
ex_meteorite  | 10 | sky stone crater, -216 72          << AE2 presses
ex_wreck      |  8 | shipwreck, -120 376
ex_treasure   |  8 | OPT buried treasure, -472 248
ex_ruins      |  8 | OPT cold ocean ruin, 72 184
ex_camp       | 12 | illager camp, -520 216
ex_bathhouse  | 10 | dungeons_arise bathhouse, -600 24
ex_asylum     | 15 | OPT plague asylum, 168 24
ex_village    | 12 | savanna village + 8 emeralds, -328 -504
ex_tavern     | 15 | OPT both taverns, -616 -488 and -808 472
ex_dens       | 20 | OPT three dens + 16 skeletons
ex_portal     |  8 | OPT ruined portal, -728 232         << the only Nether door
ex_city       | 25 | ancient city, -568 -552
```
Chapter ~180 min. Eleven `explore_crate` drops over sixteen quests, real coordinates on every
card, one danger line each in `&c` red. This is a faithful copy of Evolution's Exploration
chapter and needs almost nothing.

### V-39 (major) — `ex_portal` and `ex_meteorite` / explore.json — the chapter's own subtitle tells the player nothing here is on the way to anything, and two of these quests gate the Create and AE2 chapters.
Subtitle: `"Nothing here is on the way to anything. That is the point."` But `ex_portal` at
-728, 232 is the only route to the Nether the book ever names, and eleven Create quests need a
blaze (V-22); `ex_meteorite` at -216, 72 holds the four Inscriber Presses without which AE2
does not exist. `ex_portal` is also flagged `optional: true`. A machines-first player reads the
subtitle, skips the whole chapter, and loses both.

FIX — three parts:
1. `chapter.subtitle` line 2: OLD `"Nothing here is on the way to anything. That is the point."`
   NEW `"Most of it is not on the way to anything. Two of them are: the crater and the ruined portal."`
2. `ex_portal.optional`: OLD `true` → NEW: remove the key; `ex_portal.shape`: OLD `"rsquare"` → NEW `"square"`.
3. `ex_portal.description` line 2: OLD
   `"Patch the frame with &aObsidian&r if you want the Nether early."`
   NEW `"Patch the frame with &aObsidian&r — six comes with this quest. The &6Create&r chapter cannot pass the Blaze Burner without a trip through it, and &6Thermal&r wants a lava pool."`

### V-40 (minor) — `ex_city` / explore.json — the Ancient City, the most dangerous trip in the pack, pays one loot crate and 3 XP.
`ex_camp` (an illager camp) pays 6 emeralds and XP3. `ex_asylum` pays a crate and XP3. The
Warden run pays the same as the asylum. Meanwhile the story's equivalent (`q82`, one echo
shard) pays a Totem of Undying, a deep survey and a prospector's pick.

FIX — `ex_city.rewards`, add before `xp_levels`:
`{ "type": "item", "item": "minecraft:echo_shard", "count": 4 },`
`{ "type": "item", "item": "minecraft:experience_bottle", "count": 16 }`
and `xp_levels`: OLD `3` → NEW `5`.

---

# SIDE QUESTS (checked, not walked in full — the tech shortcut only)

## Chapter: Oda's Counter (`oda.json`) — 23 quests, 22 optional, root `oda_open` gated on q19

Verified working as designed: every buy line carries `can_repeat: true`, so the shop really does
restock as `oda_open` promises. Scrip income is 643 from quest rewards plus 4x25 from the finale
scripts (`valley_finales.js`) = ~743, against 200 of mandatory sinks (q85 120 + q86 80) and ~307
to buy one of every shop line except the 150-scrip vanity deed. **The economy balances.** The
tech-relevant lines (casings, alloy, gearing, servos, frames, coils, fluxduct, reactor casings,
reactor internals, AE bundle) total 199 scrip and are all affordable by mid Act IV.

`oda_alloy`'s line — "Deliberately cheap: nobody's evening should be a press" — is the single
best sentence in the book for this lens.

### V-41 (minor) — `rm_oda` / readme.json + `oda_open` / oda.json — the book sells Oda as the escape hatch from grind, and the counter does not open until the Act I finale, by which time the grindiest quests are already behind you.
`rm_oda` (read in the first five minutes) says "If a step is annoying, buy it." `oda_open` deps
`q19`. Scrip income through the whole of Act II is 38 (q36's 20 + oda_open's 10 + the one-shot
standing order's 8). The counter is genuinely useful from Act III, when income reaches ~233.
The Act I quests a veteran would most like to buy out of — 128 planks, 32 furnace smelts,
8 andesite alloy — are all before it exists.

FIX — `rm_oda.description`, replace line 2:
OLD `"Her counter sells casings, alloys, ducts, seeds and furniture. If a step is annoying, buy it: see the &6Oda's Counter&r chapter."`
NEW `"Her counter sells casings, alloys, ducts, seeds and furniture. If a step is annoying, buy it: see the &6Oda's Counter&r chapter."`
`""`
`"It opens at the end of Act I and the money is real from Act III. Before then, the only shortcut is a neighbour handing you the thing."`

### V-42 (minor) — oda.json — all 23 quests pay zero XP, the only chapter in the book where that is true.
The spec exempts this chapter ("Oda's Counter — unchanged"), and a shop tick arguably should not
level you. Recording it only because it is the one place the stated rule ("every quest
`xp_levels` 1-3") is broken across a whole chapter, and 23 quests is 6% of the book.

FIX (optional, low priority) — add `{ "type": "xp_levels", "levels": 1 }` to `oda_open` only,
so the chapter's entry point is consistent with every other chapter root. Leave the 22 buy
lines at zero — they are purchases, not achievements.

---

# SUMMARY — the veteran's read

## Time to the milestones (playing the book in order, unhurried)

| Milestone | Story route | Chapter (beeline) route |
|---|---|---|
| First machine (hand-cranked millstone, `q14`) | **~1h00** | ~35 min via `create_millstone` |
| First self-turning machine (water wheel, `q16`) | **~1h15** | ~25 min via `create_wheel` |
| First Thermal machine + first RF (`q32`) | **~2h10** | **~45 min** via `thermal_dynamo`→`thermal_pulverizer` |
| First ME terminal (`q51`) | **~4h10** | **~2h30** via `ae_terminal` (crater + 24 processors dominate) |
| Reactor lit (`q75`) | **~7h30** | ~7h30 — `rx_notes` is gated on `q67`, so there is no faster road |
| Quarry turning (`q87`) | **~9h30** | same, gated on `q86` + six closed resident chains |
| Whole story spine (Start Here + Acts I-V) | **~10h45** | — |
| Every chapter, optionals included | **~26-30h** | — |

## What the book gets right for this lens

- **Parallel structure.** Every tech chapter has a free root and no cross-chapter deps. A
  machines-first player can open Create, Thermal, Power, Storage Network or Ores and Mining on
  day one and never touch a chicken. Only the reactor (`q67`) and the quarry (`q86`) gate, which
  is exactly what the spec promised.
- **The Act IV branch.** `q65`-`q71` hangs off `q55`, so the whole reactor build runs in
  parallel with the cozy winter chain instead of behind it. Best structural call in the book.
- **Reward cadence.** 335 of 367 quests hand an item or a loot crate; every quest gives XP;
  Create escalates 2→5; `q13`/`q16`/`q31`/`q70` hand the *next* quest's parts list, which is
  the Evolution move. Chapter crates (`create_crate`, `flux_crate`, `power_crate`, `ae_crate`,
  `mining_crate`, `reactor_crate`, `explore_crate`) are all declared and used 2-11 times each.
- **The engineering writing in `reactor.json` and `mining.json`.** Depths, dike-vs-blanket,
  "a vessel has taps or coolant ports, never both", "more blades or more coils slow it".
  Nothing else in the pack teaches this well — which is exactly the problem in V-14 and V-37.
- **Oda's Counter.** A working, repeatable, balanced scrip shop that lets you buy out of the
  dull half. This is the feature Evolution does not have and should.

## The five things to fix first

1. **V-14 (blocker)** `q71` — the turbine quest has no method in it. Borrow `rx_turbine`'s text.
2. **V-02 / V-04 / V-09 (major)** — nine story quests are flagged `optional` while another
   quest hard-depends on them, including the pack's first Thermal machine (`q33`→`q32`) and the
   first RF line into town (`q42`→`q47`). Drop the flag on the nine that gate something.
3. **V-27 (major)** — no itemduct, anywhere, in 367 quests. The pack goes from hand-carrying to
   a full ME network with nothing in between. Fold it into `power_servo`.
4. **V-22 / V-39 (major)** — a Nether fortress sits in the middle of the Create chain and the
   only portal quest in the book is optional, in another group, under a subtitle that says
   nothing here matters.
5. **V-10 (major)** — the story builds an ME network and never says how to power it. Two lines
   in `q51` and an Energy Acceptor in its rewards.

## Grind walls, ranked (count that buys no new mechanic)

1. `q69` 64 uranium mined and smelted one at a time — V-15
2. `ae_processors` 24 processors by hand, pre-network — V-30
3. `q83` a whole second turbine described as a repeat — V-18
4. `q37` 8 cooked cod out of an Aquaculture loot pool — V-05
5. `mining_malachite` 32 copper clusters in the easiest bed in the game — V-34
6. `q15` 32 furnace smelts at ten seconds each — V-03

## Dead stretches (no new mechanic for a long run)

- `q20`-`q28`: nine quests, ~40 min, between the Act I finale and the windmill — V-07
- `q50`: ~20 min of watching certus grow with no parallel suggested — V-13
- `thermal.json` as a whole: nineteen of twenty-one quests complete on the craft, so the
  chapter passes without a single machine being powered — V-24

## One-and-done machines

The acts hand out a Mechanical Press (`q13`), Mixer and Basin (`q16`), Encased Fans (`q14`,
`q29`), a Thermal Sawmill (`q32`), a Centrifuge (`q46`) and a Redstone Furnace (`q31`), and no
act quest ever asks the player to use any of them. Their system-chapter quests are `item` tasks
on the same block, so they auto-tick. Not broken — but the machine is never run. See V-23.

## Scope of this lens

Walked in full: `readme`, `start`, `act1`-`act5`, `create`, `thermal`, `power`, `ae2`,
`mining`, `reactor`, `explore`. Checked for the tech shortcut and the scrip economy only: `oda`.
**Not covered by this lens** (they belong to the cozy/exploration reads): `farm`, `kitchen`,
`animals`, `home`, `travel`, `wild`, `tips` — 100 quests. Cross-chapter facts established here
that those reads may want: nine story quests carry a misleading `optional` flag (V-02); the
quarry needs six closed resident chains and no tech quest says so (V-19); the scrip economy
balances at ~743 income against ~507 of spend.

Numbers verified against the files, not estimated: quest counts, optional ratios, mean deps,
reward composition per chapter, the XP distribution (72x1, 159x2, 104x3, 5x4, 3x5, 1x25), the
scrip ledger, `can_repeat` on Oda's lines, chapter roots and cross-chapter deps, and the
complete absence of `thermal:item_duct` from all 22 files. Minute estimates are judgement.
