# COPPER KETTLE VALLEY — Story Bible (final)
### *A Year in the Valley* · Minecraft Forge 1.20.1 · private modpack
**Status:** build-ready. Spine = *seasons*, with the Lanternwick lamp-line and the Copperbell buried-age grafts folded in. This revision applies three audit passes in full — the non-creative player's advocate (38 findings), the anti-grind audit (blockers, spikes, gather-chains, economy), and the implementation pass (12 corrections, 8 patterns, 11 impossible-mechanic substitutes).

**Quest count: 99** (Q1–Q91 plus eight interleaved cozy beats, numbered `Qna` so no existing dependency edge had to be renumbered). **Authored playtime ≈ 16.4 hours**, down from 21.5 — no build was removed; only grind was.

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
A shallow bowl of meadow, water and low hills — a market road, a stream, a lake, a marsh, and one hillside where the copper seam still shows through the grass. Almost nothing is pre-built. What the story needs is placed by the players, and the game builds around them. (See **The Town Anchor**, below — this is the load-bearing engineering idea of the whole pack.)

**The one exception, and it matters:** the **ruined Kettle farm** is placed at first join, 40–80 blocks from spawn, on a levelled pad. The fiction promises the player a house with a chimney and a cellar; the pack must therefore *have* one before Q2 sends her to it. Everything else still grows from the anchor.

### What is broken
- **The Hearth** — the inn's fireplace, the valley's social centre. Cold since Josie died. Nobody has cooked for anybody in years.
- **The Mill** — Bram's water wheel snapped its axle. No flour, no sawn boards, no power of any kind.
- **The Store** — Oda's shelves are empty because no wagon has come up the road. The bounty board outside has one weathered notice on it.
- **The Lake** — Nella's boat is beached and the docks are rotted.
- **The Lantern Road** — forty lamp posts from the mill to the square to the lake. Josie counted them on her fingers as a child. Every one of them is dark.
- **The Works** — the Kettle copper works, a hole in the hill with a collapsed adit, and a sealed iron door in the cellar under the old farmhouse with Josie's handwriting on it: *"Not yet. — J.K."*
- **The winter** — the real antagonist. Non-lethal, comprehensible without any gaming literacy, and undefeatable by kindness. From November to March the valley cannot grow, light or heat anything. Every year, whoever is left goes.

### What restoring it means
Restoration is measured in **people, and in lamps**. Two counters, both readable without opening a menu — implemented as **bossbars**, not scoreboards (see §12, P6):

- **Residents** — 1 → 8 named neighbours plus four Ribbits plus three new arrivals (15).
- **The Lantern Road** — 0 → 40 lamps, mill to square to lake. Every act lights a stretch. At night, from the homestead window, you can see exactly how far the game has come and how far it hasn't. A lit lamp is physical proof two people cooperated: the cozy lane places the post, the tech lane runs the duct. The fortieth lamp is the second-to-last quest in the pack.

**The counter reconciles exactly, and this is not cosmetic** — the lamp bossbar is the one number a non-menu player reads all game, and if it ever disagrees with itself she stops trusting it. Ledger: Q7 → 2 · Act I finale → 6 · Q34 → 10 · Act II finale → 12 · Act III finale → 22 · Q74 → 39 · Q90 → 40.

### The Town Anchor — the terrain-independence rule
In Act I the players place **two waystones**:
- **Homestead Waystone** — on the hearthstone of the ruined farm, which a compass leads them to.
- **Town Anchor Waystone** — placed with the **Surveyor's Stake** (below), within about 60 blocks of home.

KubeJS records the Town Anchor coordinates on placement. From then on, **every** structure, NPC, market stall, sign, lamp post, greenhouse and festival table in the game is placed at a fixed offset from that anchor by quest-reward commands. The valley grows outward from a spot the players chose. It fits any terrain, and it always looks intentional.

**The Surveyor's Stake.** "Place it on flat-ish ground" is a builder's judgment call, and it is the most consequential placement in the pack — 99 quests offset from it. So the judgment is removed: Q7 hands a **Surveyor's Stake** that tints a 24×24 patch of ground green or red while held and **refuses to place on red**. The task becomes *"walk toward the road until the ground goes green, then right-click."* The anchor can never land on a cliff.

**The levelled-pad rule.** No finale ever calls `/place structure` on a jigsaw onto live terrain — that is the most fragile command in the set and it looks wrong when it half-works. Every structure command chain runs in this order:

1. `/fill` an air box above the pad (clear).
2. `/fill` a stone-and-dirt pad at anchor+offset (level).
3. `/place template valley:<name>` — a hand-built, exported `.nbt`, which **is** deterministic and is the correct tool on a known pad. (The bible's earlier "zero `/place` calls" rule conflated `/place structure` with `/place template`. Only the jigsaw form is banned.)

Coordinates are already solved by the anchor, so this is arithmetic, not pathing. It works on a cliff, in a swamp, on a beach.

### Water, and the seed
Four quests want water that the anchor system cannot conjure: the mill race (Q16), the lake (Q21/Q22/Q26/Q61/Q80), the vine slope (Q24) and Halden's spring (Q41). The pack therefore ships **two belts, both fastened**:

- **A curated seed is a hard ship requirement**, stated in §11 — a verified valley bowl with a stream and a lake inside 400 blocks of spawn. The pack does not offer a "new world" button that bypasses it.
- **And every water feature has an anchor-placed fallback anyway.** The Act I finale cuts the **mill race** at an anchor offset; the Act II finale digs the **dredging shallows** and the **pier**; Halden's **spring** is a placed structure in Q23's reward, not a found one; the vine slope is a marked, pad-filled terrace behind the hedge garden. A re-seeded world degrades in looks, never in function.

### The season rule — stated, not assumed
The acts **are** the seasons, so the calendar cannot be allowed to drift out of phase with the story.

- **Config (corrected).** There is no `season_cycle_length` key. In `serene_seasons/seasons.toml`: `subSeasonDuration = 4`, `startingSubSeason = "EARLY_SPRING"`, `dayDuration = 24000`, `progressSeasonWhileOffline = false`. Same maths as intended — 12 in-game days per season, 48 per year. Short enough that a season is felt in an evening or two; long enough that it isn't a strobe.
- **Every act finale force-sets the season** as the first command in its chain. **The argument is a sub-season, not a season:** `/sereneseasons setseason early_spring|mid_summer|mid_autumn|mid_winter`. This is not optional and it is not implicit. The finale is what turns the calendar.
- **Nothing in the pack ever waits on weather.** If a quest wants snow, the finale before it set winter. No quest text ever says "when winter comes." (And `/weather snow` does not exist — the command is `/weather rain`, which Serene Seasons renders as snow once the season is winter.)

### Keeping a non-creative player oriented
This is the single most important constraint in the pack, so it is written as rules, not intentions.

- **A moving world border, announced as story.** Act I: 1,500. Act II: 3,000. Act III: 6,000. Act IV: 10,000 plus the Nether. Act V: open. Every expansion arrives as a line from a resident — *"Tobin walked the north ridge and came back with a map and a cold. It's safe to the cairn."* — never as a technical notice. (The border is per-dimension and does not auto-scale; the Nether gets its own `worldborder set 1250`.)
- **One chapter visible, one quest visible per lane.** FTB Quests shows exactly one unlocked chapter; completed chapters collapse into **Memories** (read-only); future chapters are **hidden, not greyed**. Every quest is set to *hide until its dependencies complete*, so at any moment each lane shows exactly one available quest. **There is no server-side quest pinning in FTB Quests** — pinning is client-side with no API — so the pack produces the same experience through visibility instead, and every quest reward fires a **toast** naming the next step in plain language. The design never promises a literal pin.
- **Her book is never empty.** Two acts in v1 left the cozy lane with nothing to do for eleven consecutive tech quests. Fixed two ways: **eight interleaved cozy beats** (Q45a, Q48a, Q51a, Q54a in Act III; Q66a, Q68a, Q70a, Q72a in Act IV), and an **always-available side chapter** — *Marnie's Menu Board, Pip's Courier Board, Oda's Standing Orders* — which gates nothing, pays Scrip, and is what the book falls back to whenever a lane is waiting.
- **Every task is literal.** No quest ever says "build a base," "make it nice," or "build a shelter." It says: *"Put the door in the doorway, a window in each hole, the bed on the wool mat, and the lantern on the hook."*
- **Decoration quests ship the blocks AND mark the spots.** The v1 rule solved sourcing and left arranging. Both are solved now: every decorating quest gives an exact checklist, the reward packet contains those exact blocks **delivered by the quest that unlocks it**, and the target surface carries **marked footprints** — a distinct block (weathered copper tiles read well) on every spot an item goes. *"Put one item on each marked tile. Any order is right."* She still gets the arranging pleasure; the empty-lot anxiety is gone.
- **Every shape is pre-built.** Shells, pads, outlines and fence footprints are placed by the finale or the previous quest: the cottage, the inn, the granary, the stilt platform, the pasture outline, the greenhouse, the bathhouse, the guest rooms. The player fits out; she never designs.
- **Waystones are given, never crafted**, and every travel destination has one **standing at the far end before she leaves**. Walking somewhere twice is a design bug.
- **Explorer's Compass is never open-ended.** Every quest that uses it names the structure in the quest text and hands over a compass already set to it. There are exactly **four** named destinations in the whole pack (Q20 Ribbit village, Q67 Wandering Merchant's Tower, Q81 Cairn Chapel and Drowned Lighthouse), each with a pre-placed waystone and, for the chest hunts, a beacon beam on the chest.
- **Torchmaster in Act I, before anything else — and it must be the right item.** A **Megatorch** is what suppresses hostile spawning; a Feral Flare Lantern only places invisible light blocks and stops nothing. The homestead, the coop, the pasture and the Lantern Road get Megatorches. Feral Flares are handed out as pure lighting decor. Nothing spawns where she lives. Ever. Night is atmosphere.
- **Corpse and Lootr are named safety nets.** A death is never a lost run — your stuff waits in a grave you can walk back to. A shared structure is never already-looted — Lootr gives every player their own copy of every chest.
- **No timers, no fail states, no failable festivals.** Every "in one session" and "in one day" clause is deleted — they read as timers, they were never detectable, and §3 forbids them. The festival waits for the players. Missing one is impossible. The pressure is a calendar, not a threat.
- **The deep dark is not in this pack.** Q82's echo sample comes from a scripted, Warden-free echo cave placed at an anchor offset. The pack promises non-lethal and keeps it.
- **Build detection is on the honour system.** FTB Quests cannot verify "you fitted out the bathhouse." Those are Checkmark tasks with a picture in the quest text. This is stated here so nobody wastes a week trying to detect a cottage. Item-delivery, item-craft and KubeJS-observed placement carry the real gating.

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
1. *Summer* — teaches fishing and the lake's moods; gives you your first good rod, and the dredge net before you ever need it.
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
2. *Autumn* — his core samples locate the deep copper, iron, gold and silver, and Bram says "good work" out loud.
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

**Tech lane (Josh's spine):** Create → Thermal → Applied Energistics 2 → Bigger Reactors → QuarryPlus, in that order, each gated by an **ingredient** granted at an act finale or a key quest, and each tier handing over the boring middle materials while asking for the interesting one.

They are **braided, not parallel**. Roughly every third quest in each lane consumes something the other lane produced. A solo player does both. A couple splits naturally. A friend picks either.

### How gating actually works (this changed)
There is **no GameStages, no Recipe Stages, no CraftTweaker and no LootJS** in this pack. Per-player recipe locking is therefore not available at all. **Every recipe gate in the pack is world-level and ingredient-based**: the original recipe is removed in `ServerEvents.recipes` and a replacement is added that consumes the gate item. JEI/EMI then shows the true path and nobody has to guess. v1 did this for three of six gates; all six now work the same way, which is both simpler and consistent with the one-per-world rule in §9.

### The gates, concretely

1. **Seasoned Oak Boards → the first water wheel.** *(Hour one.)* Create's Water Wheel recipe consumes **Seasoned Oak Boards**, which exist only if somebody fires Marnie's bread oven and dries green planks in it overnight (Q15). **Q15 depends on Q8 alone** — she can light the oven the moment Marnie arrives, and Bram's Q16 is gated on the boards. The stated fiction is now true: she unblocks him before he has mined anything.
2. **Washed Silica → the first Thermal Machine Frame.** Machine Frames consume **Washed Silica**, made from lake sand only obtainable by dredging with Nella (Q26) and washing it under a Create fan. No fishing trip, no Pulverizer.
3. **The Works Power Tap → Cooking for Blockheads.** "An energy cell within 12 blocks of the inn" is not expressible as a recipe condition. So Q47 pays out a **Works Power Tap** — an ingredient in the Fridge, Sink and Milk Jar recipes — and the 12-block proximity is checked by the *quest*, never by the recipe. Her dream kitchen is still his first *look what I did for you*, and the fridge still opens the preserved-food branch Act IV depends on.
4. **Spring Water → certus quartz.** AE2 certus seeds consume water drawn from Halden's spring, which requires the cozy herbal line (Q41). AE2 does not start until the herbalist likes you. Q41 also hands over **16 certus crystals from Josie's jar on Halden's shelf**, which makes the first Crystal Growth Accelerator buildable immediately — otherwise Q50 is twenty minutes of watching a bucket.
5. **Josie's Turbine Notes → Bigger Reactors.** Reactor casings consume **Turbine Notes**, granted by Q67. The recipes are visible from Q54 and craftable from Q67 — revealed, then earned.
6. **Reactor heat → winter crops.** The greenhouse grows out of season because the reactor's coolant loop feeds its heaters (Q72), which **enables Serene Seasons' own Greenhouse Glass recipe world-wide**. Not a bespoke growth override — the mod already ships the mechanism, so the reactor unlocks a *recipe*, not a hack. This is the pack's thesis: **the reactor is the reason food exists in January, which is the reason nobody leaves in February.**
7. **Waste heat → the bathhouse.** The coolant loop's other outlet is a bathhouse behind the inn. The endgame machine is domestically useful, not just numerically bigger — and she furnishes it in Q72a, so his heat becomes her room.
8. **The Delivery Crate → the bounty board.** *(This is the anti-grind centrepiece, and its implementation changed.)* FTB Quests reads the player's inventory only; it cannot pull from an AE2 grid, and querying the grid from KubeJS means touching AE2's internal API — real mod development, not scripting. So **Q53 builds a Delivery Crate**: a tagged barrel beside Oda's board, fed by an AE2 export bus with the town's standing orders patterned in. Every delivery quest from Q53 onward completes from that crate via a KubeJS container listener. From her side it is exactly what was promised — walk up, it's already full. Q63 is deliberately placed after it so the first thing she notices about his network is that her own chores got shorter.
9. **The spare wireless terminal.** Q52 hands the cozy player a second wireless terminal — one act before the decorating marathon. She types "lantern" instead of rummaging through fourteen chests.
10. **Valley Scrip → tech skip-tokens.** Bounties, deliveries and closing a resident's arc pay **Valley Scrip**. Scrip's only use is Oda's counter, and her counter sells: pre-made Andesite Casings, crates of Redstone Servos, spare Machine Frames, reactor casing bundles, and — in Act V — **the Works Deed that unlocks QuarryPlus**. Cozy labour deletes tech grind continuously, as a standing supply chain rather than three well-chosen rewards.
11. **Trains → the decor catalogue.** Oda's full stock (Macaw's, Handcrafted, Supplementaries variants; animals; rare seeds) unlocks in tiers when the Steam 'n' Rails line reaches town in Act III — a tech build.
12. **The Lantern Road.** Every stretch needs the cozy lane to place the posts and the tech lane to run the duct. Forty lamps, both hands.

### Oda's counter is a quest chapter, not a villager trade
Easy NPC trade offers are a single MerchantOffers list, shown identically to every player, capped at the villager UI's slot count. It cannot hold the decor catalogue and cannot vary by team. So **the Valley Scrip shop lives in FTB Quests**: a repeatable *Oda's Counter* chapter, one quest per stock line (task: Scrip, consume → item reward), with tiers unlocked by dependency on Q19 / Q49 / Q86. Unlimited stock lines, per-team correctly, zero custom UI. Easy NPC keeps two or three flavour trades so she still feels like a shopkeeper.

### The Scrip economy, with the arithmetic done
v1 asked for 350 Scrip against ~285 of stated income, and closed the gap with an undirected *go grind the board* wall. Fixed on both sides:

- **Income.** Festival baskets 25 × 5 = **125** · Q36 **20** · Q38 **30** · Q53 **60** · Q80 **50** · **eight resident chains × 25 = 200** (Q59, Q60, Q62, Q63, Q73, Q75, Q77, Q85) · side-chapter and interleave beats **15** each · **bounties 15 each**, board refreshing three notices per in-game week.
- **Costs.** Q85 **120**. Q86 **80**. Total **200**.

Standing and Scrip are now earned by the *same* act, so Q86's two conditions stop being independent chores. The real sink is Oda's counter, which is optional by design — the endgame is reachable in normal play, and Scrip beyond it buys the tech lane its skip-tokens.

### Standing — how the deed gate actually works
The *seasons* draft gated QuarryPlus behind "max friendship with six of eight residents." There is no reputation mod here and Easy NPC has dialog, not relationships.

**Standing is simply *how many named resident quest chains your team has completed.*** A count of completed quest IDs — FTB Quests already tracks that.

FTB Quests' `dependency_requirement` supports only ALL / ONE completed-or-started, so "six of eight" is authored as a **hidden checkmark quest, "Standing: Trusted"**, completed by a KubeJS listener that counts the eight chain-closing IDs and, at ≥6, runs `/ftbquests change_progress <player> complete <standing_quest_id>`. Q86 then depends on it normally. About twenty lines.

- Marnie closes at Q60 · Wisp Q59 · Halden Q62 · Pip Q63 · Bram Q73 · Tobin Q75 · Nella Q77 · Oda Q85.
- **The Works Deed (Q86)** costs **80 Valley Scrip** and requires **Standing: Trusted**. Both conditions are visible in the player's own book, and the Scrip half means the tech player can buy his way toward it himself.

---

## 6. The five acts

Format: `Qn. Title | lane | task | reward | depends on`
Lanes: **C** cozy · **T** tech · **B** both.
**Counts:** Act I = 19 · Act II = 18 · Act III = 23 · Act IV = 23 · Act V = 16. **Total = 99.**
Eight beats are numbered `Qna` — they are new quests inserted into dead zones, numbered this way so no existing dependency edge had to be rewritten. Three v1 reorders are enforced by **dependency**, not renumbering: Q32 now depends on Q33, Q79 on Q84, and the Act V cozy lane runs Q76 → Q77 → Q78 → Q80 → Q79 → Q81.

---

## ACT I — SPRING: *The Thaw*
**Beat.** You arrive at a cold house in a valley that used to be a town. One neighbour sees your chimney smoke, comes up the hill, and decides you're staying. By the end of spring there are five people in the valley instead of one, the mill turns, and there is a door in your cellar you cannot open.

**Goal, one sentence:** *"Make the old Kettle farm livable and wake the town up in time for the Thaw Fair."*
**Border:** 1,500. **Tech tier:** Create, andesite through sawmill. **Lamps:** 0 → 6. **≈ 120 min.**

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q1 | The Letter and the Kettle | B | Take Josie's Letter out of your bag and read it. The last page is a map. | Josie's Journal (Patchouli), the Copper Kettle, the **Kettle Farm Compass**, the Homestead Waystone, **an iron shovel and pick**, 16 cooked food, 16 torches, a **Megatorch**, Journal Entry 1 | — |
| Q2 | Somebody Left the Kettle On | B | Follow the compass to the old Kettle farm — the chimney's still standing. Put the waystone on the hearthstone. A box will pop up: type **Home** and click the tick. | The cottage is re-roofed and re-walled around you, with a doorway, two window holes and a wool mat where the bed goes. A door, 4 Macaw's windows, a bed and a wall lantern | Q1 |
| Q3 | Four Walls and a Door | C | Put the door in the doorway, a window in each hole, the bed on the wool mat, and the lantern on the hook by the door. All four are in your bag. | Handcrafted table + 2 chairs, wool rug, 2 flower boxes, **a Cooking Pot, a campfire, 16 bricks and a bag of soup vegetables** | Q2 |
| Q4 | Nothing Gets In | B | Place the Megatorch inside your cottage. | Nothing hostile spawns near home from now on. 2 spare Megatorches for the pens, 2 Feral Flare Lanterns for lighting | Q3 |
| Q5 | The Door Under the House | B | There's a trapdoor under the ash in the old kitchen — it's glowing. Dig the gravel out of the stairs (about 75 blocks; the shovel's in your bag). | You find a sealed iron door with no handle, and Josie's handwriting chalked on it: *"Not yet. — J.K."* Cellar Waystone, Josie's tool chest | Q2 |
| Q6 | Put the Kettle On | C | Put the campfire down outside your door, hang the Copper Kettle on the hook above it, and cook one Vegetable Soup in the Cooking Pot. Everything's in the basket. | Skillet, Farmer's Delight knife, 3 sacks of assorted seeds | Q3 |
| Q7 | Where the Square Goes | B | Bram's old **Surveyor's Stake**. Walk toward the road north of your gate until the ground under you goes green, then right-click. This is where the town will be. | Anchor recorded. A stone path is laid from your door to the anchor and **the first two lamp posts go up (2/40)** | Q6 |
| Q8 | Chimney Smoke | C | Sleep one night. | **Marnie arrives.** The inn shell is built at the anchor. 8 loaves of Marnie's Bread, the Inn Waystone, **32 Green Oak Planks and a flint and steel** | Q7 |
| Q9 | Three Beds of Dirt | C | Till the 3×9 patch behind the house — it's marked in path blocks — and plant the wheat, carrots and potatoes from Marnie's sack. | Watering can, 16 bone meal, straw hat, scarecrow, **4 fence sections, a gate and a trough**, **three Hen Crates** | Q8 |
| Q10 | Two Hens and a Rooster | C | Put a fence section on each marked block behind the house, hang the gate, then right-click the three Hen Crates inside the pen. | Nesting box placed with 2 eggs already in it, **chicken feed (right-click a hen and she lays)**, a Megatorch over the coop, 3 eggs | Q9 |
| Q11 | Pip and the Egg | C | Collect 3 eggs from the nesting box and take them to Marnie. | **Pip arrives.** You are given a **Duckling** to name and keep. Pip's courier board unlocks. **16 wool from Marnie's carding basket** — she's been carding it for nobody for four years | Q10 |
| Q12 | The Man at the Broken Mill | T | Walk to the mill plot marked on your map and talk to Bram. | **Bram arrives.** Create wrench, goggles, **12 iron ingots and 24 andesite** | Q8 |
| Q13 | Eight Alloys, No More | T | Make 8 Andesite Alloy from exactly what Bram gave you. | **Mechanical Press (pre-made)**, 8 cogwheels, 8 shafts, **32 wheat** — Bram's winter store, he's sick of porridge | Q12 |
| Q14 | Turn It By Hand | T | Build a Millstone, attach a Hand Crank, and grind 16 wheat into flour for Marnie. | Encased Fan, 3 Andesite Alloy, saw-blade parts | Q13 |
| Q15 | The Green Boards | C | Put the 32 Green Oak Planks in the inn's oven, light it with the flint and steel, then go to bed. They'll be dry when you wake up. | The boards go straight into Bram's crate. **You** get the inn's spare tea set, the pantry key, a chair by the oven that is now understood to be yours, and **a pre-made Kitchen Counter, Sink and Oven**. Stage `seasoned` | Q8 |
| Q16 | Water Finds a Way | T | Build 2 Water Wheels on the mill race and drive the Millstone off them. | **Mechanical Saw (pre-made)**, Basin, Mechanical Mixer, Bram's crate: 32 Andesite Alloy **and 16 wool for the sails** | Q14, Q15 |
| Q17 | Sawdust and Shingles | T | Cut 128 boards on the Saw and hand Bram 64 of them for the market stalls. | Macaw's roof kit ×3, 4 planters, stage `market_stalls` | Q16 |
| Q18 | Marnie's Kitchen | C | Put the Counter, Sink and Oven on the three marked spots along the inn's back wall, then cook **Bread, Pumpkin Pie and Vegetable Soup**. Everything's in the crate by the counter. | Cookbook, fruit basket, 5 recipes learned automatically, Handcrafted cupboard set | Q15 |
| Q19 | **The Store Reopens** | B | Sweep the cobwebs out of the store with Oda's broom — they're marked — then bring her 16 flour and 8 loaves of bread. | *Act finale* | Q17, Q18 |

---

## ACT II — SUMMER: *The Long Days*
**Beat.** The town is awake and immediately too small. Summer is abundance you can't store, water you can't move, and light you don't have. Nella comes back to the lake, Halden opens the hedge garden, and the mill stops being a mill and starts being a workshop.

**Goal, one sentence:** *"Make summer's abundance usable — power the workshop, work the lake, and throw the town a party on the water."*
**Border:** 3,000. **Tech tier:** Create advanced → first Thermal. **Lamps:** 6 → 12. **≈ 165 min.**

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q20 | Frogs in the Reeds | C | Marnie's Explorer's Compass is **already set to the Ribbit village** — four minutes past the reeds, and Wisp walked over and set a waystone there so you don't have to walk back. Follow it and trade with the frog folk. | **Wisp befriended**, basket of marsh produce, Sophisticated Backpack, Ribbit Village Waystone, **three flower seed packets and bone meal** | Q19 |
| Q21 | The Beached Boat | C | Follow the marker to the lake and talk to the woman fixing a boat that doesn't need fixing. | **Nella arrives.** Aquaculture Iron Rod, tackle box, Lake Waystone. **A pasture outline is drawn in path blocks behind the barn, with a fence kit, a Cow Crate and a Sheep Crate** | Q19 |
| Q22 | Something With Fins | C | Catch 10 fish of any kind and cook one in the Skillet. | 16 bait, Fish Bag, 2 recipes, Nella's hat, **Nella's Dredge Net and a diving cap** | Q21 |
| Q23 | The Hedge and the Still | C | Halden wants **poppies, dandelions and cornflowers**. Plant the three seed packets in your window boxes, bone-meal them, and bring him 8 of each. | **Halden arrives**, herb garden and **the spring above it** placed, HerbalBrews starter kit, tea set, **a trellis kit, 4 grape starts and a filled watering can** | Q19, Q20 |
| Q24 | Vines on the South Slope | C | Place the trellis on the marked terrace behind Halden's hedge, plant the 4 starts, water them twice. | 12 more grape starts, wine press, Handcrafted wine rack, stage `vinery` | Q23 |
| Q25 | Bees, Cows, and a Sheep Named Later | C | Put a fence section on every marked block behind the barn, hang the gate, then right-click the Cow Crate and the Sheep Crate inside. | Milk churn, shears, 16 wool, Pasture Waystone, sheep plushie, Megatorch | Q21 |
| Q26 | Dredging the Shallows | C | Sit in Nella's boat and pull the dredge net six times. You never get in the water. | 96 more Lake Sand (192 total), Nella's oar, stage `dredged` | Q22 |
| Q27 | The Rock Kid | T | Talk to the young man camped by the copper outcrop with too many notebooks. | **Tobin arrives**, Geolosys prospector's pick, 3 survey maps already marked | Q19 |
| Q28 | Read the Rock | T | Use Tobin's pick on the 6 spots he marked and find the copper cluster. | Copper **and the tin deposit** marked as map waypoints, 32 copper ingots, **32 raw iron (Tobin's sample bags)**, **Vein Mining I** | Q27 |
| Q29 | A Wheel That Doesn't Freeze | T | Build a Windmill Bearing with 8 sails on the mill roof so the workshop runs when the stream is low. The wool is in Bram's crate. | 6 gearboxes, clutch, gearshift, 3 Mechanical Crafters | Q16 |
| Q30 | Wash the Sand | T | Wash Lake Sand under an Encased Fan over water to make 64 **Washed Silica**. | 64 more Washed Silica, stage `silica`, 2 Deployers | Q26, Q29 |
| Q31 | Josie's First Schematic | T | Take Bram's crate of Josie's papers and craft your first Machine Frame. | **2 spare Machine Frames**, Redstone Furnace, 32 Fluxduct, **a Stirling Dynamo** | Q30 |
| Q33 | The Long Bench | T | Build a proper workshop room at the mill: 6 Storage Drawers, a controller, 3 Sophisticated barrels. *(Deliberately before the Pulverizer — its storage is what makes the ore trip short.)* | 6 drawer upgrades, controller remote, **Backpack tier 2 for every player** | Q31 |
| Q32 | The Pulverizer | T | Build a Thermal Pulverizer and run 32 iron ore through it. | Doubled ore forever, Thermal Sawmill (given), 8 Redstone Servos, a second Stirling Dynamo | Q33 |
| Q34 | The Lantern Road, First Stretch | B | Place 4 lamp posts on the marked spots from the mill to the square, and power two of them from the Redstone Furnace with Fluxduct. All posts and duct supplied. | **Lamps 10/40.** Hostile spawns suppressed along the whole road | Q32, Q19 |
| Q35 | A House on Stilts | C | Wisp's platform is already out over the shallows. Put a post on each of the six marks, then the bed, the door, the windows and the three lanterns where they're marked. | **Wisp moves to town.** Marsh trade opens, Ribbit plushie, **24 paper and 24 torches from Oda's stockroom** | Q20, Q25 |
| Q36 | Two Hundred Lanterns | C | Craft 24 paper lanterns with Marnie and Pip from the paper and torches in the crate. | Lantern crate, festival clothes, 20 Valley Scrip | Q35 |
| Q37 | **The Bounty Board Fills Up** | B | Fill Oda's three notices: **24 wheat, 8 cooked fish, 8 wool.** *(Hand-authored. Random bounties appear only in Endless Seasons, after the story ends.)* | *Act finale* | Q33, Q36 |

---

## ACT III — AUTUMN: *The Harvest Debt*
**Beat.** The valley finally produces more than it eats — and Oda opens the ledger and shows everyone the truth: at this rate the town runs out of food and fuel in February. Autumn is where cozy work becomes *preservation* and tech work becomes *storage and logistics*. And Halden finally reads what is written on the Kettle Plate, and opens the door under your house.

**Goal, one sentence:** *"Fill the granary and finish Josie's storage system before winter — and feed the whole town at the Harvest Supper."*
**Border:** 6,000. **Tech tier:** Thermal full → AE2 basic. **Lamps:** 12 → 22. **≈ 205 min.**

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q38 | Oda Opens the Ledger | B | Talk to Oda at the store. She counts the town's stores out loud. | The winter checklist (in-book), 30 Valley Scrip, granary blueprint | Q37 |
| Q39 | The Granary | C | The shell went up at the Lantern Float. Put a drawer in each of the twelve marked alcoves. | Drawers arrive pre-filled with the town's current stock, Granary Waystone, stage `granary`, **Oda's brass weighing scales, her initials scratched off and yours scratched on** | Q38 |
| Q40 | Autumn Sowing | C | Plant the autumn seed pack — pumpkin, beetroot, squash, cranberry — in the marked beds. These are the only things that grow now. | Seasonal almanac (what grows when), second scarecrow, 3 recipes, **the larder crate: 32 eggs, 32 sugar, 12 milk, 32 raw meat, 16 apples, 12 empty jars** | Q38 |
| Q41 | Halden's Spring | C | Follow Halden up to the spring above the hedge garden and fill 3 bottles of **Spring Water**. | Spring Water ×3, stage `springwater`, herbal tea set, **16 certus quartz crystals from Josie's jar on Halden's shelf** | Q40 |
| Q42 | Preserves and Pickles | C | Make **4 Apple Pies, 4 Jars of Pickles and 4 Jars of Jam**. The recipes are on pages 3–5 of your cookbook and everything you need is in the crate by the counter. | 4 preserving crocks, pie safe, Marnie's pickling notes, **a drying rack Halden found in Josie's shed**. *(Quest text: Bram left a fridge blueprint on the counter. Says it needs power and he's "working on it," which from him is a promise.)* | Q40 |
| Q43 | The Bakery Line | C | Bake 4 loaves, 2 pies and 2 cakes in the inn kitchen. | Bakery display set, apron, cake plushie, Marnie's autumn beat | Q42 |
| **Q45a** | **Pip's First Run** | C | Run 3 of Pip's courier parcels. | Courier satchel, a drawing of you that is mostly hat, 15 Scrip | Q43 |
| Q44 | Smoked, Salted, Hung | C | Hang 8 raw meat on the drying rack in the shed behind the inn. *(No Nether needed — the Nether doesn't open until the end of this act.)* | 32 cured meat, smokehouse decor, stage `larder` | Q45a |
| **Q48a** | **Guest Rooms** | C | Fit out the inn's two upstairs bedrooms — a bed, a rug, a lantern and a chest on each marked spot. Everything's in the packet. | Two rooms Marnie can rent, the first arrival's letter, 15 Scrip | Q44 |
| **Q51a** | **Wisp's Marsh Harvest** | C | Gather 12 marsh crops from the marked plants downstream with Wisp. | Rare marsh seeds, frog-village decor set, 15 Scrip | Q48a |
| **Q54a** | **Nella's Autumn Catch** | C | Catch 8 fish before the lake turns and salt them into the granary. | Salt barrel, Nella's autumn beat, 15 Scrip | Q51a |
| Q45 | What Tobin Found | T | Take Tobin's 3 core samples to the marked hillside and dig out the adit (about 90 marked blocks). | Deep copper, iron, **gold and silver** clusters revealed as waypoints, **Vein Mining II**, **64 pre-made bronze and electrum stock**, and in the Lootr chest: an Artifact and **the Kettle Plate** | Q28 |
| Q46 | Induction | T | Build a Thermal Induction Smelter and alloy 8 bronze and 8 electrum. | Centrifugal Separator (given), 64 Fluxduct, 2 more Machine Frames | Q45 |
| Q47 | The Cell on the Wall | T | Charge a Thermal Energy Cell off your dynamos and run Fluxduct to the inn. | **The Works Power Tap** — Fridge, Sink and Milk Jar now craftable. One spare Energy Cell | Q46, Q42 |
| Q48 | Rails to the Road | T | Lay a Steam 'n' Rails line from the mill to the square with a Create train station. 64 rails and 32 track are in the packet. | **Train kit: engine and 2 cars, pre-made.** Station bell, stage `trainline` | Q46 |
| Q49 | Oda's Wagon Comes In | B | Unload Oda's first proper delivery crate from the station. | **Oda's catalogue tier 3** — the full Macaw's / Handcrafted / Supplementaries decor list, seeds and animals, purchasable with Scrip | Q48 |
| Q50 | Quartz in Water | T | Plant Certus Quartz Seeds in Halden's Spring Water and grow 32 certus. Josie's jar gets the first accelerator running immediately. | AE2 Inscriber (given), meteorite compass already pointing, Crystal Growth Accelerator parts | Q41, Q47 |
| Q51 | The First Terminal | T | Build an ME Drive with 2 storage cells and a terminal in the mill workshop. | 4 more cells, import/export bus set, stage `ae_basic` | Q50 |
| Q52 | Everything In One Place | T | Storage-bus the granary's drawers onto the network so the whole town's stock shows on one screen. | Wireless Terminal + charger, **a second wireless terminal to hand your partner**, Oda's ledger now auto-updates in-book | Q51, Q39 |
| Q53 | The Order Board | T | Put a **Delivery Crate** beside Oda's bounty board and point an export bus at it with the town's standing orders patterned in. | **Every delivery and "bring X to Y" quest from here on is already filled when you walk up.** 60 Scrip | Q52 |
| Q54 | The Plate in the Door | B | Take the Kettle Plate from the adit to Halden. He has been able to read Josie's shorthand for four years and has been avoiding it. | The cellar door turns one quarter and stops. **Journal Part Two.** Bigger Reactors recipes *revealed* — casings still need Josie's Turbine Notes | Q45, Q43 |
| Q55 | What Josie Actually Built | B | Go down into the cellar and read the wall. | **The reveal** (see §7). Works Waystone, Josie's steel tool chest, her original reactor blueprint framed as a decor block | Q54 |
| Q56 | **Setting the Table** | C | Put a **Place Setting** on each of the twelve marked spots on the long table, and the centrepiece in the middle. | *Act finale* | Q43, Q44, Q54a, Q55 |

---

## ACT IV — WINTER: *The Longest Night*
**Beat.** The crisis, played warm and never grim. Nothing kills anybody. What happens is that the valley gets **cold and dark and boring** — the crops stop, the lake freezes, Nella loses her work, Marnie's stores run down, the Ribbits can't stay in the marsh, and the whole town crowds into one building. The fix is the thing Josie shut down: the Works becomes a reactor, the reactor heats a greenhouse and a bathhouse, and the valley grows food in January for the first time in its history.

**Goal, one sentence:** *"Keep everyone warm and fed through winter, and finish Josie's power plant so the valley never has to go dark again."*
**Border:** 10,000 + Nether (1,250). **Tech tier:** AE2 autocrafting → Bigger Reactors. **Lamps:** 22 → 39. **≈ 270 min.**

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q57 | The Hearth Goes Out | C | Sleep one night after the Supper, then follow Pip down to the inn. | Everyone gathers. The Winter chapter opens. **64 Firewood Bundles**, a warm cloak, the cocoa recipe | Q56 |
| Q58 | Firewood for Eight Houses | C | Give **16 Firewood Bundles each** to Marnie, Halden, Nella and Oda. | Each gives something back — blanket, tonic, smoked trout, lamp oil. Sleigh bells. **Wisp's lantern path is lit down the frozen river** | Q57 |
| Q59 | The Reed Village Comes In | C | The river's ice now — you can walk it. Follow Wisp's lanterns downstream and bring the Ribbits home. | **4 Ribbit residents added to town**, frog-village decor set, **Nella's ice auger**, **Wisp's chain closes**, 25 Scrip | Q58 |
| Q60 | Soup for a Full Room | C | Cook one stew big enough for twelve and serve it at the inn. | **Marnie's chain closes.** Her recipe book (10 recipes). The Hearth relights. **The greenhouse shell goes up at the square.** 25 Scrip | Q59 |
| Q61 | Ice Fishing | C | Use Nella's auger on the lake ice, then catch **4 Northern Pike and 4 Rainbow Trout**. | Winter tackle, 2 trophies, Nella's winter beat | Q59 |
| Q62 | Halden's Rounds | C | Brew 8 winter tonics and take one each to **Marnie, Bram, Oda, Nella, Tobin, Wisp, Pip and Halden**. | **Halden's chain closes.** His half of Josie's recipe book, medicine cabinet, stage `healthy`, 25 Scrip | Q58 |
| Q63 | Pip's Winter Job | C | Run 5 of Pip's courier deliveries. *(One click each now — the Delivery Crate fills them.)* | **Pip's chain closes.** The duckling grows up. **Duck Plushie.** Courier satchel, 25 Scrip | Q58, Q53 |
| Q64 | The Cold Frame | C | Put a window in each of the six frames of the greenhouse shell, hang the door, and set the 8 planters on the marked bench. | A potting bench, a rack of seed trays, and Nella starts coming down to sit in it in the evenings because it's the only quiet room in town. *(Nella's dialog, not the reward, is the one who says nothing grows yet.)* | Q60 |
| **Q66a** | **Winter Windows** | C | Dress the inn for the solstice — a wreath, a garland and a candle on each of the twelve marked spots. | Solstice decor set, Marnie's mulled cider recipe, 15 Scrip | Q64 |
| **Q68a** | **Teaching Pip to Bake** | C | Bake 4 loaves with Pip standing on a stool. | Pip's own apron, one genuinely bad loaf you can keep forever, 15 Scrip | Q66a |
| **Q70a** | **The Wool Line** | C | Shear the flock, spin the wool and make 4 blankets — one for each empty house. | Loom set, the four blankets placed on four beds, 15 Scrip | Q68a |
| **Q72a** | **The Bathhouse Fit-Out** | C | He built it and left it bare. Benches, towel racks and lanterns on the marked spots. | Bathhouse decor set, hot-spring plushie, 15 Scrip | Q72 |
| Q65 | Open the Works | T | Clear the collapsed adit into Josie's works (about 90 marked blocks) and set a waystone inside. | Works interior lit, Josie's steel tools, a Lootr Artifact, stage `drilling`, **a saddled horse in the Works stable** | Q55 |
| Q66 | The Grid | T | Run Fluxduct from the mill to the Works and install 2 more Energy Cells. | 2 pre-made cells, Thermal servo/filter set, stage `grid` | Q65 |
| Q67 | The Second Plate | B | Explorer's Compass, **already set to the Wandering Merchant's Tower**. A waystone is standing at its gate — click it and walk in. Bring back the last Kettle Plate from the vault chest. | **Josie's Turbine Notes ×16: Bigger Reactors casings now craftable.** 2 Artifacts | Q65 |
| Q68 | Autocrafting | T | Build a Crafting CPU and a Molecular Assembler so the network builds the boring parts for you. | CPU housing and 4 co-processors, 4 ME Interfaces | Q66, Q51 |
| Q69 | Yellorium | T | Follow the deep survey to Josie's yellorite pocket — a guaranteed cluster at a fixed offset from the Works waystone — and process 64 ore. | 128 yellorium ingots; **64 reactor casings auto-crafted by your own network** while you walk back | Q68, Q67 |
| Q70 | Build the Vessel | T | Assemble the reactor: casing shell, controller, fuel rods, control rods, access port. | Reactor computer port, redstone port, Josie's blueprint framed | Q69 |
| Q71 | The Turbine | T | **A problem, not a recipe.** Bram's crate contains a fixed budget of rotor blades, coils and casing. Build a turbine that holds 1,800 RPM under load without exceeding it. | `reactor_ready` — the lever is live. A tuning page in the journal with Josie's own numbers pencilled in the margin | Q70 |
| Q72 | The Coolant Loop Goes Somewhere | B | **Josie's rule: the waste heat goes to the town, not the sky.** Run fluid and Fluxduct from the reactor to 6 greenhouse heaters and the bathhouse tank behind the inn. | Heaters live, bathhouse built and steaming, **Greenhouse Glass recipe enabled** | Q71, Q64 |
| Q73 | Bring Bram | C | Go and get Bram from the mill. He will say no. Bring him anyway. Bring cocoa. | **Bram's chain closes.** His father's wrench. The lever quest unlocks. 25 Scrip | Q60, Q71 |
| Q74 | The Lantern Road, Second Stretch | B | Place the last 17 posts on the marked spots, mill to square to lake. When the last post goes down the duct runs itself along the line. | **Lamps 39/40.** One post is left bare on purpose: Josie's porch | Q66, Q34 |
| Q75 | **Tobin's Numbers** | T | Let Tobin run the safety check: verify fuel, coolant flow and control-rod insertion in the reactor UI. | *Act finale* — **Tobin's chain closes**, 25 Scrip | Q73, Q72, Q74 |

---

## ACT V — SECOND SPRING: *Founder's Day*
**Beat.** The valley survived a winter for the first time in a decade, and people start arriving on their own. The victory lap has teeth: the town formally re-founds itself, the deed to the Works is bought and signed over, and the quarry goes in — not as a strip mine, as the town's public works. Every arc closes on screen.

**Goal, one sentence:** *"Re-found the town: finish the square, balance the books, and sink the quarry that pays for the next hundred years."*
**Border:** open at the finale. **Tech tier:** reactor scale-up, full AE2, QuarryPlus. **Lamps:** 39 → 40. **≈ 220 min.**

| # | Title | Lane | Task | Reward | Depends on |
|---|---|---|---|---|---|
| Q76 | Thaw, Again | C | Sleep one night after the Longest Night and walk the square with Marnie. | Spring seed pack, flower crates, stage `year_two`, the noticeboard updates | Q75 |
| Q77 | Greenhouse Glass | C | Glaze the cold frame with Greenhouse Glass and grow 4 out-of-season crops in it at once. | **Nella's chain closes** — she takes the gardener's job. Rare seeds from Wisp, master gardener's kit, **Nella's top-tier rod and 32 of each bait**, 25 Scrip, and **the Winter Tomato**: the first tomato of the year, in February, which Marnie eats standing up in the doorway and does not comment on | Q76, Q72 |
| Q78 | Paint the Town | C | Put one item on each of the **30 marked copper tiles** in the square. Any order is right — Oda has opinions but she's wrong. Every block is in this quest's opening packet. | Oda's full catalogue goes free, stage `square_finished`, a framed map of the town for your wall | Q76 |
| Q80 | The Fishing Derby | C | Nella wants six for the wall: **Bluegill, Perch, Trout, Pike, Catfish and Carp**. Trout and Pike are in the cold water off the pier; the rest are anywhere. Worm bait for the bottom feeders. Mount 3 on the inn wall. | Trophy mounts, fisher plushie, 50 Scrip | Q77 |
| Q83 | Reactor, Scaled | T | **A problem, not a recipe.** Hit the town's stated winter power budget with a second turbine, without exceeding the fuel burn Tobin signed off on. | `big_power`, Thermal augment set, live energy readout in the journal | Q75 |
| Q84 | Everything, Everywhere | T | Full network: 2 Crafting CPUs, wireless access across the whole town, and a subnet that keeps Marnie's pantry stocked forever. | Wireless boosters, a terminal for every player, Oda's stock syncs to the network | Q83, Q68 |
| Q79 | Eight Favourite Meals | C | Cook and deliver each resident's favourite dish. The book lists all eight — and the network has already crafted every ingredient into the Delivery Crate. | Commemorative dish set, a warm line from each of them, and the **Feast Crate**: one of each of the eight, kept for Founder's Day | Q78, Q84 |
| Q81 | Out Past the Ridge | B | Take the boat out with Nella and Pip to the **Cairn Chapel** and the **Drowned Lighthouse**. Waystones are standing at both; the chest in each is under a beacon beam. | 2 Artifacts, a Lootr luck upgrade, travel journal pages, the **Warding Lamp** | Q79 |
| Q82 | Deeper and Darker | B | Follow Tobin's lanterns down into the echo cave under the Works and bring back an echo sample. *(No ancient city, no Warden. The sculk down here is dead, and Tobin is already talking.)* | Deep survey data — this is what sites the quarry. Corpse-recovery token | Q81 |
| Q85 | The Ledger Balanced | B | Pay off the town's winter debt at Oda's counter: **120 Valley Scrip.** | **Oda's chain closes.** She hands you the ledger. Quartermaster's chest, 25 Scrip | Q79, Q80 |
| Q86 | The Works Deed | B | Buy the deed at Oda's counter: **80 Valley Scrip**, and **Standing: Trusted** — six of eight resident chains closed. | **The Deed — QuarryPlus is now craftable.** The residents vote; Bram signs as witness | Q85, Q82 |
| Q87 | Sink the Shaft | T | Place the QuarryPlus rig and its markers on the site Tobin surveyed, and power it from the reactor. | Quarry running. Pump and filler modules. **Tobin's arc closes** | Q86, Q83 |
| Q88 | The First Load | T | Route the quarry's output into the ME network, then deliver **1,024 cobblestone** from network stock to the granary. *(A bounded first cycle — the quarry keeps running after.)* | `town_provides` — Oda's store now restocks itself from your network, permanently | Q87, Q84 |
| Q89 | A Bell for the Square | C | Cast a bell from the quarry's own copper and hang it on the marked post in the finished square. | Bell placed. Every resident comes out. **Pip becomes the bell-ringer — his arc closes** | Q78, Q88 |
| Q90 | The Last Lamp | C | Walk up to Josie's porch and put the fortieth lamp on the bare post. | **Lamps 40/40.** Josie's Lantern (never burns out), a memorial bench, **Journal Entry 5** | Q89, Q74 |
| Q91 | **The Feast** | C | Set the eight dishes from the Feast Crate on the long table and light the Hearth. | *Act finale* | Q79, Q90 |

---

## 7. Finale events

**Universal rules for every finale chain**
1. **First command is always the season**, and the argument is a **sub-season**: `/sereneseasons setseason early_spring`. The finale turns the calendar; the calendar never turns on its own between acts.
2. **Levelled pad, then template.** Clear-fill air → fill pad → `/place template`. All at Town Anchor offsets. **No `/place structure` (jigsaw) anywhere in the pack.**
3. **Anchor offsets are `~` offsets.** 1.20.1 has no datapack macro functions, so a finale is invoked as `/execute positioned <ax> <ay> <az> run function valley:actN/<name>` and every command inside uses `~` only. This is the entire anchor system, solved with one `/execute`.
4. **Residents are despawned and re-summoned (or `/tp`'d)** at their new positions with new Easy NPC dialog, rather than pathed. Pathing across arbitrary terrain does not work; teleporting does. Every NPC carries a tag (`valley_npc`, `npc_marnie`, …) because every later move depends on it.
5. **All finale dialogue is `tellraw`, paced with `/schedule function`.** Easy NPC dialog is click-driven and cannot be sequenced.
6. **One per world.** FTB Quests command rewards fire once per *claiming player*, so no finale build ever lives in a reward. Every finale reward is exactly one command — `/valley finale actN` — and KubeJS checks a `server.persistentData` flag and returns silently if it is already set. This single guard is what makes the one-per-world rule in §9 work.
7. **Every finale hands both lanes the entire opening bill of materials for the next act.** Nobody starts an act by gathering.

---

### Act I finale — **The Thaw Fair** *(triggered by Q19)*
- `/sereneseasons setseason early_spring` · `/time set day` · `/weather clear`
- Clear/pad/template the market square at the anchor: four stalls, a stone-and-flower plaza, bunting, a Handcrafted long table — **and the mill race is cut**, so Q16's water wheels have water on any terrain.
- Lamp posts **3 through 6** → `bossbar set valley:lamps value 6`. Residents bossbar → 5.
- Summon Marnie, Bram, Oda and Pip at fair positions with festival dialog. Pip's duckling is placed at his feet.
- Every player gets a **Fair Basket** (loot table): festival food, a plushie token, a sconce set, and **25 Valley Scrip**.
- **Town Square Waystone** set in the middle of the square.
- `worldborder set 3000 10`, announced by Tobin: *"Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation."*
- `advancement grant @a only valley:journal/entry_2` — **Journal Entry 2**. World stage `act2`.

### Act II finale — **The Midsummer Lantern Float** *(triggered by Q37)*
- `/sereneseasons setseason mid_summer` · `/time set 18000` · `/weather clear`
- Positioned at the **Lake Waystone**: clear/pad, `/place template valley:pier`, **dig the dredging shallows**, and fill two runs of candle holders down the pier. Lamp posts **11 and 12** → `bossbar 12`.
- **Also pad-and-templates the empty granary shell** at the anchor, so Q39 is twelve drawers into twelve marked alcoves and not a build.
- `/tp` all six residents onto the pier. Nella's toast is `tellraw`, four words, clearly rehearsed: *"You all came. Right."*
- Fireworks via `/summon firework_rocket` with explicit `FireworksItem` NBT. Every player gets a Floating Lantern and a Frog Plushie.
- The tech lane receives an empty **Thermal Energy Cell** and Josie's second schematic packet — the visible "the next tier is already in your hands" moment.
- `worldborder set 6000 10`. **Pier Waystone** set. **Journal Entry 3.** Stage `act3`.

### Act III finale — **The Harvest Supper** *(triggered by Q56)*
- `/sereneseasons setseason mid_autumn` · `/time set 13000` (golden hour) · `/weather clear`
- Fill the square with harvest dressing: pumpkins, hay bales, candle holders, hanging lanterns; template the granary façade and the town noticeboard; lamp posts **13 through 22** → `bossbar 22`. Residents → 11.
- `/tp` all eight residents to seated positions, each with one `tellraw` line about the year so far. Wisp brings three more Ribbits. Pip's duckling is at the table and is served first.
- Every player receives a **Harvest Gift** loot roll: Marnie's pie, Bram's brass toolbox, Oda's ledger page, Nella's smoked trout, Halden's tonic, Tobin's copper nugget, Wisp's basket, and Pip's drawing (a written book, badly spelled, framed).
- **The turn**, paced with `/schedule function valley:act3/turn 6s`: `/sereneseasons setseason early_winter`, `/weather rain` (renders as snow), and Oda says the line the whole act was built on: *"That's the last warm night. Let's not lose anybody this year."*
- `worldborder set 10000 10` **and** `execute in minecraft:the_nether run worldborder set 1250 10` — the border is per-dimension and does not scale itself.
- **Journal Entry 4.** Stage `act4`.

### Act IV finale — **The Longest Night** *(triggered by Q75)*
The centrepiece of the pack.
- `/sereneseasons setseason mid_winter` · `/time set 18000` · `/weather rain`
- `/tp` every resident — eight plus four Ribbits — to marks outside the Works, each with one `tellraw` line. Pip rings the hand bell (`playsound`, pitch 1.4).
- The player hands Bram the lever. **Bram pulls it** — which means: quest completion runs `/schedule function valley:act4/lever 4s`, the lever is `setblock` to `powered=true`, and Bram's line is `tellraw`. NPCs cannot interact with blocks; he is narration, and it reads perfectly.
- **The world changes in one instant:** KubeJS iterates `persistentData.lamps[]` and emits one `setblock` per stored lamp coordinate, lighting all 39 posts down every street at once; the greenhouse heaters come on; the bathhouse starts steaming; a `setblock` relights the inn's Hearth as a lit campfire. `playsound block.beacon.activate` + `block.conduit.activate`. One long warm chord.
- **Greenhouse Glass recipe enabled world-wide.** The cozy player gets a Winter Seed Pack and a watering can that never empties.
- The tech lane gets the **Works Deed** listed at Oda's counter — revealed, priced, not yet owned.
- Every player receives a **Hearthkeeper's Lantern** (`dynamic-torches` held light) and a plushie token.
- Border stays at 10,000. **Journal Entry 5** — the last thing Josie wrote.

### Act V finale — **Founder's Day** *(triggered by Q91)*
- `/sereneseasons setseason early_spring` · `/time set noon` · `/weather clear`
- Clear/pad/template the finished town: the town hall façade, a signpost carrying every resident's name (`oak_sign` with `front_text`, reading *COPPER KETTLE / VALLEY / pop. 15 / est. again*), a stone bridge, the rebuilt mill roof, banners, paved square, flower beds.
- `bossbar valley:lamps 40` · `bossbar valley:folk 15`.
- Summon all residents **plus three new arrivals** on the road 24 blocks out, on a pre-filled path, with a `follow_player` objective so they walk the last stretch in. Visible proof the valley is alive again — and it is a short approach, not a journey, because long-distance pathing does not work.
- Halden reads the last page of Josie's journal aloud: five `tellraw` lines, each scheduling the next 5 seconds later.
- Every player receives: the **Kettle Family Deed**, a **Founder's Plaque** decor block with their own name on it, the plushie set, a top-tier backpack, and a **Copper Kettle** trophy to hang over their own hearth.
- Fireworks. `playsound ui.toast.challenge_complete`. Simple Voice Chat is the actual payoff here — twelve people standing around a table in proximity chat is the emotional beat the whole pack is built toward, and it needs no code at all.
- `worldborder set 60000000` (overworld and Nether) with the line: *"The valley's fine now. Go see what's past the ridge — and come home for supper."*
- Unlocks the **Endless Seasons** chapter: repeatable seasonal festivals, **rotating Bountiful bounties (this is the only place random bounties appear)**, Oda's ore contracts for the tech lane, Marnie's menu challenges for the cozy lane, and new-resident requests. The story ends. The world doesn't.

---

### The buried secret and its reveal *(Act III, Q54–Q55)*
The one thing the winning spine genuinely lacked was a mystery with a real payoff. Here it is, and it is deliberately warm rather than spooky, because the mystery belongs to **both** players — she found the door in hour one, he opens it in autumn.

**Setup.** Act I Q5: a sealed iron door in the cellar of the farmhouse she just moved into, chalked *"Not yet. — J.K."* It cannot be opened, and no quest asks you to try. It sits there for two acts. Halden changes the subject whenever it comes up.

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

**Three hard constraints:**

1. **No quest ever asks for 64 of X unless the previous quest handed you 48 of them.**
2. **The tool always precedes the ask.** v1 broke this six times — the Cooking Pot paid for the quest that required a Cooking Pot, the dynamo paid for the machine that needed power, the oar paid for the dive, the auger paid for the ice, the rod paid for the derby, the warding lamp paid for the dark. All six are moved one quest earlier. Every remaining reward was walked against the next task in its lane.
3. **Pre-made is for intermediates, never for the machine that is the point of the quest.** Casings, servos, alloys, cogs, patterns and spare frames arrive assembled. The Pulverizer, the reactor, the turbine, the network and the quarry are always built by hand. Grind deleted; building never deleted. Three quests are explicitly **problems, not recipes** — Q71 (turbine inside a parts budget), Q83 (power target inside a fuel budget), Q72 (route the waste heat to two live consumers). These are the ones where the pack expects him to actually think, and they are the only long quests left in the tech lane on purpose.

**Two blockers that would have shipped, and did not.** Q6 asked her to cook in a Cooking Pot and paid her the Cooking Pot — un-completable in hour one, in a pack whose entire claim is that hour one has no mining in it. Q32 asked him to run a Pulverizer and paid him the generator. Both are one-line moves; both would have ended a first session.

**Worked example 1 — the first hour has no mining in it.**
Q12 hands over *exactly* 12 iron and 24 andesite. Q13 consumes exactly that and pays a **pre-made Mechanical Press plus 8 cogwheels, 8 shafts and 32 wheat** — the entire bill for Q14's Millstone *and* its grind. Josh goes from "talk to a guy" to "powered millstone" without opening a mineshaft once. That is the specific thing he used to cheat past, deleted by design rather than by console.

**Worked example 2 — the egg economy, which nearly ate an evening.**
v1's Act I asked for 14 eggs from 2 vanilla hens (30–50 minutes of lay timers) and 8 wool from sheep that don't arrive until Act II. Now: three hens arrive in crates, the nesting box is placed with two eggs already in it, **chicken feed is a KubeJS item that makes a hen lay on use**, the ask drops to 3 eggs, and the 8 wool becomes 16 wool out of Marnie's carding basket in Q11 — with another 16 in Bram's crate for Q29's sails. Nobody waits on a chicken.

**Worked example 3 — the tech lane's biggest build is the cozy lane's biggest convenience, twice, in the same act.**
Q52 finishes the wireless terminal and hands **a second one to the partner** — one act before the decorating marathon, so she types "lantern" instead of opening fourteen chests. Q53 builds the **Delivery Crate**, and from that moment every delivery quest in the pack is already filled when she walks up to the board. Pip's five-delivery winter quest (Q63) is deliberately placed *after* it, so the first thing she notices about his network is that her own chores got shorter. He gets to watch that land.

**Worked example 4 — the network arrives before the quest it solves.**
v1 put Q84 (the subnet that keeps Marnie's pantry stocked forever) *after* Q79 (cook and deliver eight distinct dishes with unstated ingredients). Q79 now depends on Q84. Thirty-two minutes of shopping becomes twelve minutes of assembly, the tech lane visibly serves the cozy lane one last time, and Q79's reward carries the **Feast Crate** so Q91 is setting a table rather than cooking the same eight dishes twice.

**Worked example 5 — Valley Scrip is the standing supply chain.**
Bounties, deliveries and closing a resident's arc pay Scrip. Scrip buys, at Oda's counter: pre-made Andesite Casings, crates of Redstone Servos, spare Machine Frames, reactor casing bundles, and finally the **Works Deed**. Her play converts directly into his skip-tokens, every session, permanently. And because closing an arc pays 25, Standing and Scrip are the same economy — Q86's two conditions are one act, not two chores.

**Standing rules baked in everywhere**
- Any quest that says *go find* ships the marker, a pre-set Explorer's Compass, **and a waystone already standing at the destination**.
- Any decoration quest ships its own checklist of blocks *and* marks every spot they go.
- Any quest that needs a shape gets the shape pre-built by the previous quest or the previous finale.
- Backpack and storage upgrades land **before** the acts that produce a lot of items.
- Waystones are given, never crafted.
- Megatorches arrive with the first structure that needs one, not after the first bad night.
- Lootr means arriving second to a structure costs nothing. Corpse means a death is never a lost run. Both are named here so the design never has to add a difficulty apology.

---

## 9. Multiplayer

**Shape.** FTB Teams, progress shared per team. FTB Quests tracks progress **per team, not per player** — so "personal" quests are authored as team quests with per-lane visibility, and anyone who genuinely wants their own book becomes their own team. This is stated up front because it silently breaks any design that assumes per-player quest state.

### A. The couple's team (default)
Josh and his wife are one team, **Kettle**. Completions are shared: she never sees a tech quest blocking her chapter, he never has to cook. On first join each player answers one question — *"the kitchen, or the workshop?"* — which sets which lane the book shows first. Both can see everything; each lane shows exactly one available quest. Chapters unlock when **the team** finishes an act, so nobody waits alone.

### B. A second team — **The Second Letter**
Josie wrote to more than one relative. She was not a woman who put all her eggs in one nephew. A new team's first-join grants every member a **Second Letter** in her hand, dated the same day as yours, and opens a short private chapter.

- They place **their own Homestead Waystone**. They do **not** place a second Town Anchor — there is one town.
- Their lots are on the **far side of the square** from the first team's, so the town visibly grows from two directions rather than one team's suburb absorbing another's.
- Their Act I is a compressed six-quest chapter, **New Neighbour**: place your homestead, fit out a shelter, meet Marnie, plant a plot, get a pet, register at the town noticeboard.

### C. The one-per-world rule
**Town-state quests are one per world.** The mill wheel, the granary, the greenhouse shell, the reactor, the bell — the town only needs restoring once. If another team already did it:

> The quest **auto-completes** for the arriving team, with a line of flavour — *"The mill was already turning when you got here. Bram says you should go and meet whoever did it."* — **and still pays the full reward.**

**Because the reward is the shortcut, not the trophy.** A team that arrives in Act IV still gets the pre-made frames, the charged cell, the backpack upgrades and the Scrip, because those are the things that let them play. Withholding them to protect somebody's sense of achievement would only make the game worse for the person who showed up late.

The *personal* half always runs fresh: your farm, your kitchen, your workshop, your animals, your house, your friendships. Every team gets its own cozy build-out and its own arcs with the same residents.

**Implementation note that makes this true:** because all recipe gating is world-level and ingredient-based (§5), and every finale is guarded by a world flag (§7 rule 6), a second team can never re-fire a finale and can never be locked out of a recipe the world has already unlocked. The two rules are the same rule.

### D. Late joiners — **"You Missed the Weather"**
A six-quest onboarding chapter, granted automatically on first join at any point in the story. A player joining in Act IV does not play three months of spring.

1. Read the Second Letter.
2. Follow the compass to your lot, place your own waystone, name it.
3. See Oda — she gives you **every waystone the town has already activated**, the journal chapters written so far, and a Newcomer's Satchel scaled to the current world act (Act II: Create basics + farm crate · Act III: + Thermal starter, backpack, 100 Scrip · Act IV/V: + AE2 basics, wireless access to the town network, 200 Scrip).
4. See Marnie — she feeds you and gives you a food stack for the current season.
5. **See Bram, or see Pip.** The quest asks which one you'd rather go and visit. **That single choice sets your lane**, invisibly, with no menu and no explanation.
6. Claim a lot in town.

On completion, KubeJS grants **every world stage already unlocked** and opens the current act's chapter. They are never behind and nobody walks them through four acts of backfill. In fiction: their letter got wet. Pip is extremely sorry about the letter.

### E. Somebody stops logging in
Nothing breaks. Their homestead becomes a house in town, and a one-line noticeboard quest lets the remaining team adopt any structures and animals they left behind — the animals get fed, the lamps stay lit, and the quest text is kind about it. Nothing in the story ever requires a specific player to be online.

### F. World stages vs team stages — the authoring split
- **World stages** (one per world, never re-run): every act finale, every structure the anchor system builds, every resident's arrival, the reactor, the greenhouse, the quarry, the Lantern Road count, every ingredient-gated recipe.
- **Team stages** (per team, run fresh): lane choice, personal building, cooking, animals, fishing, resident chains, Standing, Valley Scrip balance, backpack and network access.

If a stage would ever be granted twice for the same world change, it is a world stage. That single rule prevents every duplicate-finale bug.

---

## 10. Journal — Josie Kettle's book

Patchouli, five chapters, one per act finale, plus the cellar wall in Act III. Same hand throughout — practical, warm, a bit wry, never sad for long — and the art direction is that the handwriting gets shakier and the plans get **more** ambitious, not less.

**Implementation constraint that shapes this section:** Patchouli exposes no read-state API, and entries unlock **only by advancement**. So each entry has a datapack advancement (`valley:journal/entry_N`) and each finale ends with `advancement grant @a only valley:journal/entry_N`. Q1 cannot detect "read all four pages" — the task is holding the Letter, and the text does the rest.

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

**Mod-list check.** The live manifest at `/Users/joshuamalloy/Desktop/1. Projects/Minecraft/pack/mods` (124 entries) was verified three times against this bible. Everything the story depends on is present: `create`, `create-steam-n-rails`, `geolosys`, `vein-mining`, `torchmaster`, `additional-enchanted-miner` (this is QuarryPlus — the mod's actual id), `biggerreactors`, `ae2`, all four Thermal jars plus Cultivation and Innovation, `serene-seasons`, `aquaculture`, `easy-npc`, `kubejs`, `ftb-quests-forge`, `ftb-teams-forge`, `patchouli`, `lootr`, `corpse`, `bountiful`, `waystones`, `duckling`, `ribbits`, `perfect-plushies`, `simple-voice-chat`, `dynamic-torches`. Extras now used: `domestication-innovation` (Pip's duck), `supplementaries` (lantern posts, candle holders), `create-deco`.

**The absences that shaped the design, stated plainly:** there is **no GameStages, no Recipe Stages, no CraftTweaker and no LootJS.** Every consequence of that is already folded into §5 (ingredient gating), §7 (finale guards), §9 (world vs team) and §12 (Global Loot Modifiers instead of LootJS). Do not design against a per-player recipe lock; it does not exist here.

**Curated seed — a hard ship requirement.** The pack ships one verified seed: valley bowl, stream and lake inside 400 blocks of spawn, a hillside for the Works, a marsh downstream. The launcher does not offer a world-creation screen that bypasses it. The anchor fallbacks (§3) mean a re-seeded world still functions, but it will not look like the screenshots.

**Custom-code bill, in build order.** (Full detail in §12.)
1. **Town Anchor listener** + `offset()` helper + `persistentData` (anchor coords, `lamps[]`, finale flags). Nothing else works without it.
2. **The `/valley` command tree** — `stage`, `finale`, `check`, `deliver`. Every reward calls it.
3. **Custom items and the six ingredient gates** — Seasoned Oak Boards, Washed Silica, Spring Water, Kettle Plate A/B, Works Power Tap, Turbine Notes, Works Deed, Valley Scrip, Firewood Bundle, Place Setting, Surveyor's Stake, Hen/Cow/Sheep Crates, Dredge Net, chicken feed. **Each removed recipe ships with its replacement**, never a deletion, or EMI desyncs and nobody can find the path.
4. **~25 KubeJS completion listeners** (the `change_progress` pattern) — bulk mechanical work, all the same shape.
5. **11 hand-built structure NBTs** — the long pole. Start in parallel with 1–4.
6. **Easy NPC presets** — 8 residents × ~3 dialog states ≈ 24 presets, exported from in-game, never hand-written NBT.
7. **5 finale functions + 5 journal advancements + 5 Patchouli entries.**
8. **Bountiful reward-pool edit + 5 Global Loot Modifiers** (Q45, Q67, Q81 ×2, Q82).
9. **Quest JSON, all 99**, last — it depends on everything above.

**Season config.** `subSeasonDuration = 4`, `startingSubSeason = "EARLY_SPRING"`, `progressSeasonWhileOffline = false`. Every act finale force-sets the sub-season as its first command. Do not ship without this.

**Honour-system tasks.** Every fit-out and shell quest is an FTB Quests Checkmark task with a screenshot in the quest text. Item delivery, item crafting and KubeJS-observed placement carry the real gating. This is a deliberate choice, not an oversight — FTB Quests has no build detection and faking one is not worth a week.

**The three real risks, ranked.**
1. **Bigger Reactors block-entity reads** (Q70/Q71/Q83). RPM and fuel figures may live in non-serialized runtime fields. Author as `/valley check turbine`, which either completes the quest or prints the current numbers — and ship a plain Checkmark fallback behind a config flag so the pack is never blocked by a mod update.
2. **The 11 structure NBTs.** Pure hours, no cleverness. Nothing else is blocked by them until step 7.
3. **Command-string spellings that must be verified in the first hour of testing:** the Easy NPC preset-import subcommand, the Explorer's Compass NBT key, the Waystone name tag, and the Xaero waypoint chat format. All four have safe fallbacks (`/summon` with exported NBT; naming the structure in quest text plus `/locate`; a `tellraw` of the coordinates; a handed waystone).

---

## 12. Implementation notes

*Everything the next stage needs to write SNBT directly. Reward types are FTB Quests native: **item · xp · xp_levels · loot · command · toast**. Task types are: **item** (with `consume` true/false) · **checkmark** · **checkmark·kjs** (a checkmark completed by a KubeJS listener calling `/ftbquests change_progress`) · **stat**.*

### 12.1 Corrections applied to v1 (do not re-introduce)

| # | v1 said | Reality | Applied fix |
|---|---|---|---|
| C1 | `setseason spring` | The argument is a **sub-season** enum | `early_spring`, `mid_summer`, `mid_autumn`, `early_winter`, `mid_winter` |
| C2 | `season_cycle_length = 48` | Not a real key | `subSeasonDuration = 4`, `startingSubSeason`, `progressSeasonWhileOffline = false` |
| C3 | Feral Flare = no spawns | Feral Flare only places light blocks | **Megatorch** for suppression; Feral Flare is decor lighting |
| C4 | "Zero `/place` calls" | Conflates two commands | `/place structure` (jigsaw) banned; **`/place template` is the tool** |
| C5 | Cellar is "under the Kettle house" | Nothing was pre-built, so there was no house | The **ruin is placed at first join**; Q2's reward repairs it into the cottage shell |
| C6 | `.mcfunction` with absolute anchor coords | 1.20.1 has **no macro functions** | `/execute positioned <ax> <ay> <az> run function valley:actN/x`, `~` offsets inside |
| C7 | "in one session" / "in one day" | Not detectable, and reads as a timer | Clauses deleted from Q43 and Q63 |
| C8 | "complete any 3 bounties" | FTB Quests cannot see a Bountiful completion | Q37 is three hand-authored notices; `valley:bounty_receipt` added to Bountiful reward pools for Endless Seasons |
| C9 | "10,000 plus the Nether" | Border is per-dimension | `worldborder set 10000` **and** `execute in minecraft:the_nether run worldborder set 1250` |
| C10 | "heavy snow" | `/weather snow` does not exist | `/weather rain` after the season is winter |
| C11 | Fridge gated on "cell within 12 blocks" | Not expressible as a recipe condition | Ingredient gate `valley:works_power_tap`; the 12-block check is a **quest** check |
| C12 | "Vein Mining unlocked" as a stage | Vein Mining is an **enchantment** | Reward = enchanted book, level I (Q28) / II (Q45) |

### 12.2 The eight patterns every quest cites

- **P1 — NPC token handshake.** "Talk to X" is not a task type. Easy NPC dialog button → Action (COMMAND) → `/give @initiator valley:token_<npc>_<n>` → the quest task is **item, consume: true, count 1**. Needs `easy_npc-common.toml` action permission level 2. More robust than Observation, because every Easy NPC shares one entity type. Used by Q12, Q21, Q23, Q27, Q38, Q54, Q73, and the New Neighbour and late-joiner chapters.
- **P2 — KubeJS escape hatch.** Location tasks are authored as fixed coordinates and cannot reference a runtime anchor. Every "be at / place / sleep / dig / break N" gate is a **checkmark** completed by a listener calling `/ftbquests change_progress <player> complete <questId>`. ~25 listeners.
- **P3 — Stages.** No GameStages mod. A stage is `player.stages.add(id)`, a key in `server.persistentData`, or FTB Teams data. There is no vanilla command, so register `/valley stage <add|remove> <world|team|player> <id>` in `ServerEvents.commandRegistry` and call it from a **command** reward.
- **P4 — All recipe gating is world-level and ingredient-based.** Remove the original in `ServerEvents.recipes`, add a replacement consuming the gate item. Six gates: Water Wheel ← Seasoned Oak Boards · Machine Frame ← Washed Silica · certus seeds ← Spring Water · CfB Fridge/Sink/Milk Jar ← Works Power Tap · reactor casings ← Turbine Notes · QuarryPlus ← Works Deed. A seventh is an *enable*, not a gate: Greenhouse Glass, switched on world-wide by Q72.
- **P5 — "Marked on your map."** `tellraw @a {"text":"xaero-waypoint:Mill:M:<x>:<y>:<z>:6:false:0:Internal-overworld"}`. Verify the format against the installed Xaero build; fallback is a handed waystone plus coordinates in the quest text.
- **P6 — The two counters are bossbars.** `bossbar add valley:lamps {"text":"Lantern Road","color":"gold"}` / `max 40`; `bossbar add valley:folk {"text":"Residents"}` / `max 15`; `bossbar set … players @a`. Readable with no menu open.
- **P7 — Finale idempotency.** Every finale reward is exactly one command, `/valley finale actN`. KubeJS checks `server.persistentData.finales.actN`, returns silently if set, otherwise runs the chain and sets the flag. Never put a world build in a reward — rewards fire once per claiming player.
- **P8 — Structures are hand-built `.nbt`.** Build once in a creative flat world with structure blocks, export to `data/valley/structures/*.nbt`, then clear-fill air → fill pad → `/place template`. **Required:** `kettle_ruin`, `kettle_cottage_shell`, `inn_shell`, `market_stall`, `granary_shell`, `granary_facade`, `stilt_platform`, `greenhouse_shell`, `bathhouse`, `guest_rooms`, `town_hall`, `mill_roof`, `train_station`, `pier`, `noticeboard`, `echo_cave`. Writing these as raw `/fill` chains is thousands of lines per act and will not survive editing.

### 12.3 Impossible mechanics and the substitute that shipped

| v1 wanted | Why it can't | What ships instead |
|---|---|---|
| Auto-pin the next quest | Pinning is client-side, no server API | Hide-until-dependencies-complete (one visible quest per lane) + a **toast** reward naming the next step |
| Bounties auto-fill from ME stock, one click | FTB Quests reads inventory only; grid queries need AE2's internal API | **Delivery Crate** (tagged barrel + export bus, Q53) + a KubeJS container listener. Same experience, ~30 lines |
| Verify a built shelter / pen / shell | No build detection exists | Checkmark + screenshot in quest text; item tasks carry the gating |
| Read turbine RPM / fuel burn (Q70/71/83) | Figures may be non-serialized runtime fields | `/valley check turbine` and `/valley check power`, with a Checkmark fallback behind a config flag |
| "Six of eight chains closed" (Q86) | `dependency_requirement` is only ALL/ONE | Hidden checkmark quest **"Standing: Trusted"**, completed by a KubeJS count of eight quest IDs |
| Per-player recipe gating | No GameStages / Recipe Stages / CraftTweaker | P4 ingredient gates, world-level — which is also what §9-C needs |
| Patchouli "read all four pages" | No read-state API; entries unlock by advancement only | Task = hold the Letter; five `valley:journal/entry_N` advancements granted by finales |
| "A plushie of their choosing" | No choice reward type | `valley:plushie_token` + a repeatable **Josie's Shelf** chapter, one token per plushie |
| Residents walk into town | Long-distance pathing fails | `/tp` to the mark; for Act V's arrivals, spawn 24 blocks out on a pre-filled path with `follow_player` |
| Geolosys clusters "marked on your map" | The pick prints to chat only | P5 waypoints; also set `generate_samples = true` so Tobin's six spots are real surface samples |
| Give an item to an NPC | No give-to-NPC hook exists | Every "bring X to Y" is an FTB Quests consume-item task |
| Oda's tiered decor catalogue as trades | MerchantOffers is one list, slot-capped, identical for everyone | The **Oda's Counter** repeatable quest chapter (§5) |
| Loot injection | No LootJS | Forge **Global Loot Modifier** JSONs on the specific chest loot tables (Q45, Q67, Q81 ×2, Q82) |

### 12.4 Per-quest task type / reward type

**Act I** — Q1 item(hold)/item+command+toast · Q2 checkmark·kjs(waystone placed)/command+item · Q3 checkmark/item · Q4 checkmark·kjs(megatorch within 32 of Home)/item · Q5 checkmark·kjs(player below ruin floor)/command+item · Q6 item(cooking pot, hold)+item(cooked meal)/item · Q7 checkmark·kjs(**anchor listener — build first**)/command · Q8 checkmark·kjs(`PlayerEvents.wakeUp`; **never a Stat task, `sleep_in_bed` is cumulative**)/command+item · Q9 item(seeds, hold)+checkmark/item · Q10 checkmark·kjs(3 chickens within 12 of Home)/command+item · Q11 item(egg ×3, consume)/command+item · Q12 item(token, consume)/item · Q13 item(andesite alloy ×8, hold)/item · Q14 item(wheat flour ×16, consume)/item · Q15 item(seasoned board ×32, hold)/command+item · Q16 item(water wheel ×2, hold)/item · Q17 item(planks ×128 hold + ×64 consume)/item+command · Q18 item(3 CfB blocks, hold)+item(3 named dishes)/item+command · Q19 item(flour ×16 + bread ×8, consume)+checkmark/**command `/valley finale act1`**

**Act II** — Q20 item(Ribbit trade good, hold)/item+command · Q21 item(token)/item+command · Q22 stat or checkmark·kjs(**from-zero counter — the vanilla fish stat is cumulative**)+item(cooked fish)/item · Q23 item(3 flowers ×8, consume)/command+item · Q24 item(grape, hold)+checkmark/item+command · Q25 checkmark·kjs(2 cows + 2 sheep in the pasture box)/item+command · Q26 item(`valley:lake_sand` ×96, consume)/item+command · Q27 item(token)/item · Q28 checkmark·kjs(6 prospector-pick uses)/item+command · Q29 item(windmill bearing + 8 sails, hold)/item · Q30 item(washed silica ×64)/item+command · Q31 item(machine frame, hold)/item · Q33 item(6 drawers + controller + 3 barrels, hold)/item · Q32 item(pulverizer, hold)+item(iron dust ×32)/item · Q34 checkmark·kjs(4 posts on whitelisted anchor-relative coords; **push each coord to `persistentData.lamps[]` — the Act IV finale iterates this list**)/command+item · Q35 checkmark/command+item · Q36 item(paper lantern ×24)/item · Q37 item(wheat 24 + cooked fish 8 + wool 8, consume)/**command `/valley finale act2`**

**Act III** — Q38 item(token)/item+command · Q39 item(12 drawers, consume)+checkmark/command+item · Q40 item(4 autumn seeds, hold)/item · Q41 item(spring water ×3)/item+command · Q42 item(4 pies + 4 pickles + 4 jam)/item · Q43 item(4 bread + 2 pies + 2 cakes)/item · **Q45a** item(courier parcel ×3, consume)/item · Q44 item(smoked meat ×8)+checkmark/item+command · **Q48a** checkmark/item · **Q51a** item(marsh crop ×12, consume)/item · **Q54a** item(salted fish ×8, consume)/item · Q45 item(`valley:kettle_plate_a`, hold — **injected by GLM into the adit's Lootr chest**)/item+loot+command · Q46 item(bronze ×8 + electrum ×8)/item · Q47 item(energy cell, hold)+checkmark·kjs(duct within 12 of inn)/item+command · Q48 item(track station + tracks ×64, hold)/item+command · Q49 item(`valley:delivery_crate`, consume — spawned in the station chest by Q48's reward, because "arrive by train" is not detectable)/command · Q50 item(certus ×32)/item+command · Q51 item(drive + 2 cells + terminal, hold)/item+command · Q52 item(wireless terminal, hold)+checkmark/item ×2 · Q53 checkmark·kjs(Delivery Crate placed + fed)/item+command · Q54 item(kettle plate A, consume, via P1 handoff)/command+item · Q55 checkmark·kjs(player inside the cellar box)/command+item+loot · Q56 item(table + 12 place settings, consume)+checkmark/**command `/valley finale act3`**

**Act IV** — Q57 checkmark·kjs(wakeUp)/item · Q58 item(`valley:firewood_bundle` ×16 ×4, consume — four consume-tasks, because **an NPC cannot accept an item**)/item+command · Q59 checkmark·kjs/command+item · Q60 item(great stew ×12, consume)/command+item · Q61 item(4 Northern Pike + 4 Rainbow Trout — **named real species; Aquaculture has no "winter fish"**)/item · Q62 item(8 tonics, consume)/item+command · Q63 item(courier parcel ×5, consume)/item · Q64 checkmark/item+command · **Q66a** checkmark/item · **Q68a** item(bread ×4)/item · **Q70a** item(blanket ×4, consume)/item+command · **Q72a** checkmark/item · Q65 checkmark·kjs(player inside the Works box)/command+loot+item · Q66 item(2 energy cells, hold)+checkmark/item+command · Q67 item(`valley:kettle_plate_b`, hold — GLM on the named structure's loot table)/item+loot · Q68 item(molecular assembler + crafting storage, hold — **never task on encoded patterns, NBT matching is fragile**)/item · Q69 item(yellorium ingot ×128)/item · Q70 item(5 reactor parts, hold)+checkmark/item · Q71 checkmark + `/valley check turbine`/command · Q72 checkmark ×2/command+item · Q73 item(token)+item(cocoa, consume)/item+command · Q74 checkmark·kjs(remaining coords from `persistentData.lamps[]`)/command+item · Q75 checkmark/**command `/valley finale act4`**

**Act V** — Q76 checkmark·kjs(wakeUp)/item+command · Q77 item(4 out-of-season crops, hold)+checkmark/item+command · Q78 checkmark(30 marked tiles, honour)/command+item · Q80 item(6 named species)+item(3 mounts)/item · Q83 checkmark + `/valley check power`/command+item · Q84 item(2 crafting storage 16k + boosters, hold)/item · Q79 item(8 named dishes, consume)/item · Q81 item(2 GLM artifacts, one per named structure)/loot+item · Q82 item(echo shard) + biome(`minecraft:deep_dark`) **or**, if the biome task type is absent in this FTB Quests build, checkmark·kjs on the scripted echo cave/item · Q85 item(`valley:scrip` ×120, consume)/item+toast · Q86 item(`valley:scrip` ×80, consume)+checkmark(**hidden "Standing: Trusted" quest**)/item+command · Q87 item(quarry, hold)+checkmark/item · Q88 item(cobblestone ×1024, consume)/command · Q89 item(bell, consume)+checkmark/command+item · Q90 checkmark·kjs(block placed at the one known porch coord)/command+item · Q91 item(8 feast dishes, consume)/**command `/valley finale act5`**

**Chain-closing quest IDs for the Standing counter:** Q59, Q60, Q62, Q63, Q73, Q75, Q77, Q85. Each also pays 25 Scrip.

### 12.5 Finale command chains

Invoked only through the P7 guard:
```js
server.runCommandSilent(`execute positioned ${a.x} ${a.y} ${a.z} run function valley:act1/fair`)
```

**First join** (`PlayerEvents.loggedIn`, first-time flag):
```
title @s times 20 90 30
title @s subtitle {"text":"Spring, Year One.","color":"gray","italic":true}
title @s title {"text":"COPPER KETTLE VALLEY","color":"gold","bold":true}
playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 0.8
tellraw @s [{"text":"Open your Quest Book. There is exactly one thing to do.","color":"white"}]
give @s valley:letter
worldborder set 1500
function valley:setup/place_ruin
bossbar add valley:lamps {"text":"Lantern Road","color":"gold"}
bossbar set valley:lamps max 40
bossbar set valley:lamps players @a
bossbar add valley:folk {"text":"Residents"}
bossbar set valley:folk max 15
bossbar set valley:folk players @a
bossbar set valley:folk value 1
```

**`valley:act1/fair`** — The Thaw Fair
```
sereneseasons setseason early_spring
time set day
weather clear
fill ~-18 ~1 ~-18 ~18 ~14 ~18 minecraft:air
fill ~-18 ~-3 ~-18 ~18 ~-2 ~18 minecraft:dirt
fill ~-18 ~-1 ~-18 ~18 ~-1 ~18 minecraft:stone
fill ~-18 ~0 ~-18 ~18 ~0 ~18 minecraft:cobblestone
fill ~-7 ~0 ~-7 ~7 ~0 ~7 minecraft:stone_bricks
place template valley:market_stall ~-10 ~1 ~-10
place template valley:market_stall ~8 ~1 ~-10
place template valley:market_stall ~-10 ~1 ~8
place template valley:market_stall ~8 ~1 ~8
place template valley:long_table ~-3 ~1 ~0
place template valley:mill_race ~-26 ~0 ~4
setblock ~0 ~1 ~0 waystones:waystone{WaystoneName:"Town Square"}
setblock ~-12 ~1 ~0 supplementaries:lantern_post
setblock ~12 ~1 ~0 supplementaries:lantern_post
setblock ~0 ~1 ~-12 supplementaries:lantern_post
setblock ~0 ~1 ~12 supplementaries:lantern_post
bossbar set valley:lamps value 6
bossbar set valley:folk value 5
easy_npc preset import_new valley:marnie_fair ~-4 ~1 ~-2
easy_npc preset import_new valley:bram_fair ~4 ~1 ~-2
easy_npc preset import_new valley:oda_fair ~-4 ~1 ~2
easy_npc preset import_new valley:pip_fair ~4 ~1 ~2
summon duckling:duck ~4 ~1 ~3 {PersistenceRequired:1b,NoAI:1b}
title @a times 15 70 25
title @a subtitle {"text":"Spring, Year One.","color":"gray"}
title @a title {"text":"The Thaw Fair","color":"gold"}
playsound minecraft:block.bell.use master @a ~ ~ ~ 1 1
loot give @a loot valley:rewards/fair_basket
give @a valley:scrip 25
advancement grant @a only valley:journal/entry_2
worldborder set 3000 10
tellraw @a [{"text":"Tobin: ","color":"gold"},{"text":"\"Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation.\"","color":"white","italic":true}]
```
Then, outside the function: `/valley stage add world act2`.

**`valley:act2/float`** — The Lantern Float *(positioned at the Lake Waystone)*
```
sereneseasons setseason mid_summer
time set 18000
weather clear
fill ~-14 ~1 ~-14 ~14 ~10 ~14 minecraft:air
fill ~-14 ~-1 ~-14 ~14 ~-1 ~14 minecraft:stone
place template valley:pier ~-3 ~0 ~0
fill ~-6 ~-1 ~6 ~6 ~-1 ~16 minecraft:sand
fill ~-2 ~2 ~2 ~-2 ~2 ~18 supplementaries:candle_holder
fill ~2 ~2 ~2 ~2 ~2 ~18 supplementaries:candle_holder
setblock ~0 ~1 ~-2 waystones:waystone{WaystoneName:"The Pier"}
bossbar set valley:lamps value 12
tp @e[tag=npc_marnie,limit=1] ~-2 ~1 ~4
tp @e[tag=npc_bram,limit=1] ~2 ~1 ~4
tp @e[tag=npc_oda,limit=1] ~-2 ~1 ~6
tp @e[tag=npc_nella,limit=1] ~0 ~1 ~10
tp @e[tag=npc_halden,limit=1] ~2 ~1 ~6
tp @e[tag=npc_pip,limit=1] ~0 ~1 ~4
title @a title {"text":"The Lantern Float","color":"aqua"}
tellraw @a [{"text":"Nella: ","color":"aqua"},{"text":"\"You all came. Right.\"","italic":true}]
summon firework_rocket ~ ~4 ~12 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1b,Colors:[I;16766720],FadeColors:[I;16777215]}]}}}}
summon firework_rocket ~4 ~4 ~14 {LifeTime:22,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:4b,Colors:[I;3847130]}]}}}}
playsound minecraft:entity.firework_rocket.launch master @a ~ ~ ~ 2 1
give @a supplementaries:candle_holder 1
give @a perfectplushies:frog_plushie 1
give @a thermal:energy_cell 1
give @a valley:scrip 25
advancement grant @a only valley:journal/entry_3
worldborder set 6000 10
```
Plus, positioned at the anchor: `place template valley:granary_shell ~-14 ~1 ~-4`.

**`valley:act3/supper`** — The Harvest Supper
```
sereneseasons setseason mid_autumn
time set 13000
weather clear
setblock ~-6 ~1 ~-6 minecraft:hay_block
setblock ~6 ~1 ~-6 minecraft:hay_block
setblock ~-6 ~1 ~6 minecraft:carved_pumpkin[facing=south]
setblock ~6 ~1 ~6 minecraft:carved_pumpkin[facing=south]
place template valley:granary_facade ~-14 ~1 ~-4
place template valley:noticeboard ~0 ~1 ~-5
bossbar set valley:lamps value 22
bossbar set valley:folk value 11
title @a title {"text":"The Harvest Supper","color":"gold"}
loot give @a loot valley:rewards/harvest_gifts
give @a valley:scrip 25
advancement grant @a only valley:journal/entry_4
schedule function valley:act3/turn 6s
```
**`valley:act3/turn`** — the turn:
```
sereneseasons setseason early_winter
weather rain
tellraw @a [{"text":"Oda: ","color":"gold"},{"text":"\"That's the last warm night. Let's not lose anybody this year.\"","italic":true}]
playsound minecraft:block.snow.place master @a ~ ~ ~ 1 0.6
worldborder set 10000 10
execute in minecraft:the_nether run worldborder set 1250 10
```

**`valley:act4/night`** — The Longest Night
```
sereneseasons setseason mid_winter
time set 18000
weather rain
title @a times 20 100 30
title @a title {"text":"The Longest Night","color":"white"}
tp @e[tag=npc_bram,limit=1] ~0 ~1 ~2
playsound minecraft:block.bell.use master @a ~ ~ ~ 1 1.4
schedule function valley:act4/lever 4s
```
**`valley:act4/lever`** — the instant:
```
setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=true]
# KubeJS then iterates persistentData.lamps[] and emits one setblock per stored coord:
#   setblock <x> <y> <z> supplementaries:lantern_post_lit
particle minecraft:cloud ~2 ~3 ~2 1 1 1 0.02 60 force @a
playsound minecraft:block.beacon.activate master @a ~ ~ ~ 3 0.7
playsound minecraft:block.conduit.activate master @a ~ ~ ~ 2 1
bossbar set valley:lamps value 39
give @a valley:hearthkeepers_lantern 1
give @a valley:plushie_token 1
advancement grant @a only valley:journal/entry_5
```
Plus separate positioned calls: at the inn `setblock ~ ~ ~ minecraft:campfire[lit=true]`; at the bathhouse a steam source plus `particle minecraft:cloud`; and the KubeJS enable of the Greenhouse Glass recipe.

**`valley:act5/founders`** — Founder's Day
```
sereneseasons setseason early_spring
time set noon
weather clear
place template valley:town_hall ~-20 ~1 ~-6
place template valley:stone_bridge ~10 ~0 ~-14
place template valley:mill_roof ~-24 ~4 ~2
setblock ~0 ~1 ~-3 minecraft:oak_sign{front_text:{messages:['{"text":"COPPER KETTLE"}','{"text":"VALLEY"}','{"text":"pop. 15"}','{"text":"est. again"}']}}
bossbar set valley:lamps value 40
bossbar set valley:folk value 15
easy_npc preset import_new valley:newcomer_a ~0 ~1 ~24
easy_npc preset import_new valley:newcomer_b ~2 ~1 ~26
easy_npc preset import_new valley:newcomer_c ~-2 ~1 ~26
title @a times 20 110 40
title @a subtitle {"text":"Spring, Year Two.","color":"gray"}
title @a title {"text":"Founder's Day","color":"gold","bold":true}
give @a valley:kettle_deed 1
give @a valley:copper_kettle_trophy 1
loot give @a loot valley:rewards/founders
summon firework_rocket ~ ~5 ~ {LifeTime:25,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;16766720,3847130],FadeColors:[I;16777215]}]}}}}
playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 2 1
function valley:act5/read1
```
**`valley:act5/read1` … `read5`** — Halden reads the last page, each line scheduling the next 5 seconds later, ending with:
```
worldborder set 60000000
execute in minecraft:the_nether run worldborder set 60000000
tellraw @a {"text":"The valley's fine now. Go see what's past the ridge — and come home for supper.","color":"gold","italic":true}
```

### 12.6 Geolosys and worldgen prerequisites

Four metals were demanded by quests and never surfaced by the survey system, in a pack with a prospector NPC whose whole arc is finding them. All four are one config or KubeJS line, and all four are now made true by a reward:

| Metal | Demanded by | Made findable by |
|---|---|---|
| Tin | Q31 (Machine Frame) | Cassiterite deposit in the Act II band; **Q28's reward marks it** |
| Silver | Q46 (electrum) | Deposit in the Act III band; **Q45's reveal extended to gold + silver** |
| Gold | Q46, Q51 | Same reveal as silver |
| Yellorite | Q69 | **A guaranteed 128-ore cluster placed at a fixed offset from the Works waystone** — reusing the anchor system, which makes "follow the deep survey" mechanically true and drops Q69 from ~28 min to ~10 |

Also set Geolosys `generate_samples = true`, or Tobin's six marked spots in Q28 are not real surface samples and the prospector's entire gimmick is cosmetic.

### 12.7 Named destinations (there are exactly four)

Every one is hard-named in quest text, has a waystone standing at it **before** the player leaves, and — where a chest is involved — a beacon beam on the chest and a Global Loot Modifier injecting the quest item.

1. **Ribbit Village** (Q20) — vanilla `ribbits` structure, waystone set by the Act I finale.
2. **The Wandering Merchant's Tower** (Q67) — pick a concrete structure from the installed set (`when-dungeons-arise`, `dungeons-and-taverns`, `yungsbetterstrongholds`, `towns-and-towers`) and write the GLM against that structure's own loot table. "Any ruin" cannot be authored.
3. **The Cairn Chapel** (Q81) — as above.
4. **The Drowned Lighthouse** (Q81) — as above.

Q82's echo cave is not a hunt: it is a `valley:echo_cave` template placed at an anchor offset, deepslate and dead sculk, no ancient city, no Warden, one Lootr chest, a waystone at the entrance and Tobin already inside, talking.

---

*End of bible. Next: FTB Quests chapter SNBT (99 quests, per §12.4), the KubeJS anchor/stage/listener scripts, the 16 structure NBTs, Easy NPC presets, the five finale functions, and Josie's Patchouli book.*
