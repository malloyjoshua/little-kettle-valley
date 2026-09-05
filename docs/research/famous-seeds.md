# Famous seeds — candidate list for the one shipped world

Job W, 2026-09-04. The decision upstream of this file: Little Kettle Valley ships **one hand-built
world**, so the seed is chosen once, by hand, from seeds other people have already looked at and
written up — Josh: *"pull from famous seeds first, not random ones."* A famous seed comes with a
description we can check against, and a name we can say.

**Pre-condition, and it is not optional.** Every description below is a description of *vanilla*
1.20 worldgen. Regions Unexplored is a TerraBlender biome mod: with it installed, the seed we type
in is not the seed anyone wrote about — the biome layer is replaced and the terrain that hangs off
it moves. Regions Unexplored and TerraBlender were removed from the pack before any of these were
generated (`docs/mod-decisions.md`, 2026-09-04). Everything in the verification pass below runs on
stock 1.20.1 worldgen plus the pack's structure mods.

## What the site has to be

From `story/` and `docs/transitions-design.md`, the site needs, inside one ~240x240 window:

- a **gentle rise** for the Kettle farm, with the **lake in view** from the hearth
- a **flat** big enough for the town — the plaza needs a genuinely level 60x60 core
- a **ridge** 12-30 blocks up within ~120 blocks (Tobin walks "the north ridge"; Halden's vines go
  on "the south slope", so a `-z` ridge puts both where the writing already says they are)
- **meadow / plains / cherry grove / flower forest** ground cover; a village nearby is fine
- **not** ocean, jungle, desert, swamp or badlands at spawn, and **nothing snowy** — the pack has a
  season system and a snow spawn reads as the wrong story from block one

## Sources used

Reputable, human-written 1.20-era lists rather than seed-database dumps: PCGamesN, GameSkinny,
Beebom, Sportskeeda, Pro Game Guides, and the Minecraft Wiki's own notable-seed page. Where a list
did not say Java explicitly, the seed is only carried here if the source's page is a Java page —
Bedrock seeds generate different terrain from the same number and are useless to us.

## The eight candidates

| # | Seed | Source's name for it | Claimed spawn / features | Claimed coords | Why it is on this list | Risk going in |
|---|------|---------------------|--------------------------|----------------|------------------------|---------------|
| 1 | `1569845621568838682` | "Cherry Blossom Lake with Island" (Beebom) | Spawns **in a cherry grove**; a "peaceful lake" with an island in it, fishable, cave mouths nearby for early resources | lake at `-9, 120, -10` | The single closest match to the brief: grove **and** lake **at** spawn. Cherry grove is a mountain sub-biome, so a ridge is structurally likely | Cherry grove borders snowy slopes as often as not |
| 2 | `5369984945557223422` | "Beautiful lake and villages" (Sportskeeda, 20 best 1.20 Java) | Spawn is **on the shore of a sizable lake**; multiple villages within easy reach, plus a pillager outpost and ruined portals | not given | Lake literally at the spawn point, and the villages give the valley neighbours | The same write-up mentions **cold ocean ruins** "a short distance" away — ocean may be inside our window |
| 3 | `6139114308887857248` | (GameSkinny, top 1.20.1 seeds — Java, 1.20) | **Cherry grove at spawn** with adjacent **plains villages** | spawn `-9, -4` | Grove + plains + village, the three ground covers the pack's palette is written for | No lake named anywhere in the description |
| 4 | `9067159196951998086` | "What lies beneath" (Sportskeeda, 1.20 Java) | Spawn sits between a **cherry grove biome and a mountain range**, with **a village on either side** | not given | This is the brief's "meadow beside mountains, village nearby" almost word for word | No lake named; "mountain range" may be too tall (we want a 12-30 wall, not an alp) |
| 5 | `4437805342312437912` | "Pleasant village in the valley" (Sportskeeda, 1.20 Java) | Spawn near a **circular mountain range with a village at its centre**; a second village nearby; ancient city at the range's edge | not given | A literal ring-of-hills valley — the shape the whole pack is named after | A closed ring can mean the flat inside is small, and no water is named |
| 6 | `-2032795982907864146` | "Cherry Grove Valley Village" (Beebom) | Spawn biome **cherry grove**; a **plains village merges into the grove**; deep dark below | grove/village `-129, 100, 11` | Village already blended into the grove is exactly the look the town wants | No lake named; deep dark under the site is a mob-spawn nuisance under the plaza |
| 7 | `-4475792576490886961` | "Valley of Patterned Cherry Blossoms" (Beebom) | Spawn biome **sunflower plains**; a **cherry grove plateau circles the whole plains region** | grove ring `-163, 120, 207` | A plains bowl ringed by a raised grove is the cleanest ridge-around-a-flat in the whole list | Ring is described as a plateau, which can read as a wall rather than a slope |
| 8 | `6942710633571786` | "Valley of Cherry Grove Trees" (Beebom) | Spawn biome **meadow**; a cherry grove sitting in a valley; extensive caves | grove `227, 50, -8` | **Meadow spawn** is the brief's first choice, and it is the only meadow spawn on any of the lists that also names a valley | The source calls it a "snowy mountain valley" — snow may be inside the window, which is a hard reject |

### Carried as reserves, not verified

- `69420018030897796` — PCGamesN, "Cherry Grove Lake": a **large lake village beneath a cherry
  grove**, and on its face the best match here. Held back because PCGamesN's list is written for a
  much later game version, and large-scale terrain is not guaranteed to survive that far back to
  1.20.1. Worth generating if all eight above fail.
- `8907269963032727430` — Beebom, "Canyon with Cherry Grove": **plains** spawn, river canyon
  bordered by cliffs at `-110, 70, 120`. A canyon river is not a lake, so it fails the lantern-raft
  and pier beats on paper — kept only as a shape reference.
- `4459605219549419` — Beebom: plains spawn, grove **adjacent to snowy mountains** at `31, 80, -57`.
  Named snow next to the site; excluded on the same rule as #8's risk.

## How these get judged

`tools/scripts/seed_hunt.py` boots each seed fresh, pregens with Chunky, then reads the region files
offline and scores every 240x240 window whose centre is within 240 of spawn on: surface-height
std-dev, the flattest 60x60 inside it (the plaza floor), tree cover, preferred/forbidden biome
share, a lake of 400-26,000 water cells with an 18x18 patch of open water in it (that test is what
separates a lake from a river), no man-made blocks, no structure bounding boxes, and a 12-45 block
ridge within 120 blocks on at least one side, scored higher when that side is `-z`.

Two notes on the numbers, both of which came out of the earlier stopped run and are kept honest here:

- **The brief's "chunky radius 224" cannot evaluate the brief's own window rule.** A window centre
  240 from spawn reaches 360 for the window itself, and the ridge test looks 120 further out: 480.
  At radius 224 not even a spawn-centred window has its ridge band generated, which is why the first
  hunt returned zero qualifying windows on every seed. Candidates are generated at **480**; the
  shipped master world is still pregenerated at 512 as specified.
- **The brief's "height std-dev 2-5 over 240x240" does not exist in this worldgen.** Measured across
  the first six generated worlds, a 240x240 land window runs 5.5-25. A 240-block square inside ±10
  blocks of level is a pancake, and the same brief also asks for a 12+ ridge, which by itself lifts
  the window's std. So the 2-5 intent is enforced where it actually matters — `CORE_STD`, the
  flattest 60x60, which is the ground the plaza is built on — and the window std becomes a wide
  sanity gate plus a scoring term that peaks on gentle, rolling ground.

Results, renders and the final pick are appended below once the verification pass has run.

---

# Verification pass — what actually happened

All eight were generated on the pack (Regions Unexplored removed) at Chunky radius 480 and scored
offline. Logs: `scratch/seedhunt/famous.log`, `scratch/seedhunt/rank400.json`.

## Round 1: every one of the eight failed, and the scorer was wrong about why

At the brief's own gates, **zero of the eight produced a single qualifying window.** The rejection
counts said `std` and `land` — the windows were too rough, or too wet. That was true, but it hid a
worse problem, which only showed up when the gates were relaxed one rung at a time
(`scratch/seed_rank.py`, a ladder that stops at the first rung a seed clears, so a seed that misses
by a hair is distinguishable from a seed that is an ocean):

| Seed | First rung it cleared | Best window |
|---|---|---|
| `1569845621568838682` | `std<=12` | score 9.03, core60 std 1.96, lake 5,280 |
| `9067159196951998086` | `+pref>=0.35 tree<=0.50` | score 10.64, core60 std 1.39, lake 7,193 |
| the other six | nothing, even at the widest rung | — |

`1569845621568838682` looked like the winner. It is not. `scratch/site_diag.py` — written because
`pick_site()` fails with one line and no reason — reported that **605 of its hearth candidates had a
lake edge within 170 blocks and not one of them had a clear sightline to it.** The reason:

```
lake surface Y = 62.0
hearth Y: min 103 median 110 max 119   (lake 62)
```

The window is a plateau. Its "lake" is forty-five blocks down a canyon. **The scorer's lake tests
were all horizontal** — size, openness, not-an-ocean, distance to the window edge — so a seed could
score full marks for water the player can never be shown. Fixed: `LAKE_DROP_MAX = 14` in
`tools/scripts/seed_hunt.py`, and a window now reports `lake_y` and `lake_drop`.

## Round 2: with the height test, and with the search ring widened

`SEARCH_R` was also made a knob and widened to 400. The justification is in the code: the shipped
world sets its own spawn with `/setworldspawn`, so the valley does not have to sit on whatever the
seed dropped the player on — what a famous seed buys is a known, describable world, not a fixed
arrival point.

| Seed | Rung | Score | Window | std | core60 | tree | pref | lake | ridge | lake drop |
|---|---|---|---|---|---|---|---|---|---|---|
| **`5369984945557223422`** | **brief, no relaxation** | **11.81** | -376, 32 | **4.62** | **0.58** | 15% | 92% | 21,774 | +22 **-z** | **3** |
| `4437805342312437912` | brief, no relaxation | 11.02 | -360, 392 | 4.97 | 1.13 | 9% | 86% | 11,576 | +36 -z | 8 |
| `-4475792576490886961` | +land / forb | 9.28 | -344, -344 | 6.48 | 0.77 | 13% | 89% | 2,832 | +45 +z | 4 |
| the other five | nothing | — | | | | | | | | |

## The pick: `5369984945557223422`

Sportskeeda's 1.20 Java list calls it *"you spawn on the shores of a sizable lake with multiple
villages to easily loot"*. On our pack it is the only candidate that clears **every gate the brief
asked for with no relaxation at all**, and it clears them well:

- window height std **4.62** — inside the brief's own 2–5 band, which the previous run had measured
  as unreachable and downgraded to a scoring term
- flattest 60×60 std **0.58** — the plaza floor is essentially level
- tree cover **15%**, exactly the target; preferred biome **92%** (sunflower plains / plains /
  flower forest — no snow, no desert, no jungle, no ocean in the window)
- a 21,774-cell lake whose surface sits **3 blocks** below the site, not 45
- a **-z** ridge of +22 — a valley wall, not an alp, and on the side the writing already calls
  "the north ridge"

Site solved inside it: hearth `-319, 74, 32` on a 2.5-block rise, town anchor `-302, 67, -44`,
world spawn `-299, 70, -58` — 92 blocks down the lantern road from the farm gate, 14 blocks clear
of the plaza edge so she arrives at the town's mouth rather than inside it.

---

# The finding that outranks the seed choice

The site solver was picking an anchor by measuring a **61x61** box around it and calling that flat.
The town the planner lays down is `town_box` grown by its clearance: **136 x 130 columns**, every pad
in it cut at one Y (`anchor.y`). Measuring a fifth of the area and building on all of it is how the
first built master world came out with the inn's doorstep at Y 63 and the ground outside it at Y 74,
the mill's at 63 with the hill behind it at 81, and a 17-block bare rock face on the mill's pad.

That is now fixed in `tools/scripts/seed_hunt.py` — the anchor test covers the real footprint — and
fixing it produced the more important number. Over the entire 1024x1024 pregen of the chosen seed
there are **53,478 town-sized boxes lying entirely on land, and the flattest of them has 22 blocks of
relief**; the 1st percentile is 25 and the median is 45.

**There is no patch of 1.20 overworld this size that a single-level town fits on.** Not on this seed,
and on this evidence not on any seed. `TOWN_RELIEF_MAX` is therefore set to 24 — it picks the
flattest ground that exists rather than pretending flatter ground is out there — and the residual
relief is a **town-plan** problem, not a seed problem.

The fix is terracing: the plaza keeps one level, and each building's pad takes its own local Y with
a step or a ramp between neighbours, exactly as `docs/transitions-design.md` rule 5 already says
("Sample the real surface, feather the edges, follow the slope"). `@pad` already samples the real
surface material; what it does not do is choose its own height. Until it does, the `cut_edge`,
`stone_face` and `doors` probes in `scratch/nature_check.py` will keep failing on any seed.

---

# Terracing: what the residual relief turned into

Job T, 2026-09-05. The finding above — *"there is no patch of 1.20 overworld this size that a
single-level town fits on; the flattest town-sized box on this seed has 22 blocks of relief"* —
was left as a town-plan problem. This is what the town plan did with it.

## The rule

The plaza keeps one level and is the datum. **Every other pad takes the median natural surface
under its own footprint**, read off the pristine pregen before a block is built. Median, not
maximum: the maximum is what cut the inn's doorstep to Y 63 with the ground outside it at 74.

Two constraints sit on top of that:

1. **No terrace may be further from its neighbour than the ground between them can climb.**
   The first run gave the town hall Y 63 and the greenhouse Y 69 with four free columns
   between them — a six-block wall of cut dirt down the greenhouse's side. Pads are now
   relaxed pairwise until `|Δlevel| ≤ (free columns between them)`, which pulled the spread
   from −6..+3 down to −4..+1 and cost nothing anyone will see.
2. **Everything that connects them ramps.** Streets, aprons and the lantern road are laid as
   staircases: one block of climb, then at least three flat columns, then the next. Streets
   are pinned to the level of the paving they leave — which is where the worst bug of the
   pass was hiding: `mill_lane` starts at (−13, 3), one column *outside* the plaza rectangle,
   so it took its starting level from the raw hillside at Y 77 while the square it leaves is
   at 69, and was built as a cobbled embankment eight blocks in the air with the mill's apron
   ramping forty-five columns up to meet it.

## The levels, as built

| site | Y |
|---|---|
| `bathhouse` | 67 |
| `church` | 70 |
| `garden` | 65 |
| `granary` | 69 |
| `greenhouse` | 67 |
| `inn` | 67 |
| `marnie_house` | 65 |
| `mill` | 67 |
| `newcomer_corin` | 66 |
| `newcomer_mab` | 66 |
| `newcomer_tess` | 69 |
| `pip_house` | 67 |
| `store` | 67 |
| `tobin_camp` | 66 |
| `town_hall` | 65 |

Plaza and datum: **69** (the median natural surface over the plaza rectangle — `anchor.y` was
67, the median over the whole town box, which is a level the square itself is not at). Cottage
yard: **74**. Works shell: **53–58**, re-measured each run so the thinnest cover over its
ceiling is five blocks of real rock rather than "six below the anchor", which stopped being
underground the moment the datum moved.

## The skirt

Between a terrace and the land there is no lip: a slope-limited relaxation. Every column within
ten blocks of anything the plan builds on starts at the natural surface, the built columns are
pinned, and the field is swept until no column is more than one block from any of its eight
neighbours. It touches ~40,000 columns and writes ~6,400 — the rest of the valley is already
within a block of where it needs to be and is left alone.

Two earlier versions of that pass are worth recording because both looked right and were not.
A single outward flood that **stops** where the land catches up leaves the step behind that
column unseen (the mill kept a six-block face three columns off its pad). A single outward
flood that **carries on** lets a column which met the land three rings away become a neighbour
of the ramp coming off a pad and drag it to the ground in one step (the church ended up on a
seven-block wall). Both are the same mistake — deciding a column's level from whichever
neighbour was visited first — and only relaxing to a fixed point fixes it.

The edge is feathered on top of that: a column may hold its terrace's level for a ring or two
before it starts down, chosen from a hash of its own coordinates, so a pad's edge wanders in
plan by a block or two instead of ending on a line. It is a floor on the level and never a
ceiling, so it can never make a step taller than the relaxation allows.

## Probe results, before and after

`scratch/nature_check.py --world world-master --baseline scratch/pregen`

| probe | before (flat pads) | after (terraced) | note |
|---|---|---|---|
| cut_edge | 26 (limit 8) | **8** | pass |
| stone_face | 7 (limit 2) | **5** (land itself: 6) | pass |
| pad_material | pass | **pass** | |
| doors | 4 bad of 12 | **12 at the surface** | |
| lamps | pass | **pass** | 40 posts on solid ground |
| road_steps | 8-block step | **1** | 1 per 3 blocks held |
| plaza_dry | pass | **pass** | |
| lake_view | pass | **pass** | 175 blocks, clear |

Three of those numbers moved because the probe was wrong, and it is worth being exact about
which. `nature_check.py`'s TERRAIN grid was a 9x9 morphological opening of the surface —
a workaround for "remove the trees and the buildings" that cannot remove a building wider than
its kernel, erases exactly the feathering the brief asks for, and **fails ground nobody has
touched**: run the old probe against the pristine pregen and `cut_edge` reports 10 and
`stone_face` reports 3, against limits of 8 and 2. TERRAIN is now read per column — walk down
from the surface to the first block that is ground or paving — which removes walls, roofs and
trees at any size and leaves the real steps in the land; `doors` measures the ground outside
the building's own footprint rather than the four columns next to a set-back door, all four of
which are indoors; `cut_edge` counts a run only where the step off the edge is two blocks or
more, because a one-block step is what a graded ramp between two terraces looks like and the
untouched pregen scores 2 under that rule instead of failing at 10; and `stone_face` is scored
against the same measurement on the pregen, because holding the build to a two-block face while
the meadow it sits in has a six-block one is a test of the seed, not of the build.
