# The world

Little Kettle Valley ships **one hand-built world**. There is no world generation on a
friend's machine, no seed to type and no Create New World screen: the valley — the town, the
forty unlit lamp posts, the letter on the cold hearth — is committed into the pack and
handed over whole. Everything below is what is standing in it, where, and why that piece and
not another.

Seed **5369984945557223422**. Town anchor **-302 69 -44**. Spawn **-324 75 116**, yaw
**-180** (she wakes on the road, facing the farm, looking up the lantern road toward the
town). Every coordinate in this file, in the story scripts and in every probe comes from one
generated registry, `pack/kubejs/data/valley/valley_sites.json`, written by
`tools/scripts/plan_town.py --site`. Nothing is hand-typed anywhere else, which is why a
building can be moved without hunting for its coordinate in nine files.

---

## What stands where

`level` is the terrace the pad was cut to — every piece stands on the **median surface under
its own footprint**, which is why the town sits in the meadow instead of on a plinth. Site
box (`x0..x1 / z0..z1`) is the registry rectangle the build is allowed to touch and the
probe reads. Act is the act the building belongs to in the story, not when it was built:
**everything in this table is standing, finished and shut before the player's first login.**

| Building | Piece | Rotation | Act | Level | Site box (x / z) | Front door |
|---|---|---|---|---|---|---|
| **The Hearth** | `nova_structures:tavern/tavern_house_spruce` | clockwise_90 | Act 1 | 67 | -286..-268 / -51..-35 | -279 68 -48 |
| **Marnie's Cottage** | `kaisyn:village/meadow_swiss/houses/meadow_medium_house_5` | none | Act 1 | 65 | -282..-272 / -78..-68 | -280 66 -73 |
| **The Broken Mill** | `kaisyn:village/sunflower_plains_farm/side/sunflower_plains_windmill_1` | clockwise_90 | Act 1 | 67 | -348..-332 / -48..-31 | -342 68 -39 |
| **Pip's Place** | `kaisyn:village/meadow_swiss/houses/meadow_medium_house_1` | none | Act 1 | 67 | -267..-259 / -80..-68 | -265 68 -74 |
| **The Copper Outcrop** | *planner-built* | — | Act 1 | 66 | -264..-256 / -94..-86 | — |
| **The Boathouse** | `kaisyn:village/meadow_swiss/houses/meadow_fisher_1` | none | Act 2 | 69 | -284..-274 / -11..0 | -282 70 -7 |
| **The Hedge Garden** | `kaisyn:village/exclusives/classic/houses/classic_small_farm_1` | none | Act 2 | 64 | -314..-305 / -91..-83 | — |
| **The Granary** | `kaisyn:village/exclusives/rustic/houses/rustic_barn_professions_1` | none | Act 2 | 66 | -338..-328 / -26..-17 | -337 67 -22 |
| **The Bell Tower** | `kaisyn:outpost/towers/meadow/base_plate` | none | Act 3 | 66 | -308..-296 / -77..-65 | -302 66 -68 |
| **Oda's Store** | `kaisyn:village/meadow_swiss/houses/meadow_butcher_and_mason_1` | none | Act 3 | 65 | -296..-286 / -95..-83 | -290 66 -87 |
| **The Bathhouse** | *planner-built* | — | Act 4 | 67 | -275..-267 / -30..-22 | — |
| **The Greenhouse** | *planner-built* | — | Act 4 | 65 | -337..-325 / -61..-53 | — |
| **Corin's House** | `kaisyn:village/meadow_swiss/houses/meadow_medium_house_4` | none | Act 5 | 65 | -256..-245 / -48..-37 | -254 66 -44 |
| **Mab's House** | `kaisyn:village/meadow_swiss/houses/meadow_medium_house_3` | none | Act 5 | 66 | -332..-321 / -10..1 | -330 67 -6 |
| **Tess's House** | `kaisyn:village/meadow_swiss/houses/meadow_medium_house_2` | none | Act 5 | 67 | -269..-258 / -14..-2 | -265 68 -10 |
| **The Town Hall** | `kaisyn:village/meadow_swiss/houses/meadow_large_house_1` | none | Act 5 | 63 | -350..-334 / -78..-66 | -346 64 -72 |

### Why that piece

- **The Bell Tower** — the only structure in any installed jar with **both a real
  `minecraft:bell` and a door**, out of 2,505 enumerated across Towns and Towers and
  Dungeons and Taverns. The tudor tower is taller and ships zero doors; `meadow_temple_1`
  has a door and no bell; the oriental piece has neither. It is placed with `y_base 6` so
  its ragged rock plinth is buried and its threshold lands on the doorstep — 31 courses
  stand, and the bell hangs at **-302 87 -71**, over the plaza, where Act III rings it.
- **The Hearth** — kept as `tavern_house_spruce` rather than swapped for the cherry variant
  that also fits. It is the best-reading building in the pack, and the hearthstone, the
  chalk tiles, the bed and the wall-run are all *derived* from that template's own geometry.
- **The meadow houses** — one palette for the whole town, so the valley reads as one place.
  Marnie's is the medium house with a balcony door; Pip's is the long-plan chalet next door.
- **The Broken Mill** — the sunflower-plains windmill is the only piece in the catalogue
  with a real wheel and a real axle, and the story's first job is that the axle is snapped.
- **The Greenhouse, the Bathhouse and the Copper Outcrop** are planner-built: no jar in the
  pack has a greenhouse or a bathhouse, and the outcrop is a copper seam, not a building.
- **The square** is planner-built too. The mod's own street pieces (`crossroad_04`,
  `classic/crossroad_03`) carry 129 cyan-concrete jigsaw markers and nothing else — they are
  connectors, not places. The **fountain** is `meadow_meeting_point_1`, whose bell was
  swapped for a quartz slab: there is one bell in this valley and it is in the tower.

### The rest of the valley

| Thing | Where | Note |
|---|---|---|
| Town anchor / waystone | -302 69 -44 / -302 70 -44 | the datum every `~` offset in the story hangs off |
| Plaza | -314..-290 / -56..-32 | rings and spokes, weathered off `cell_hash`; **no light source in it until Act I** |
| Fountain | -296..-292 / -41..-37 | smooth-quartz basin, 4-block jet |
| Surveyor's stake socket | -302 70 -46 | an **empty** cell over a chiselled-stone-brick plinth: Q7 is the player driving the stake in |
| Noticeboard / signpost | -302 70 -49 / -322 76 112 | the signpost lantern is the one lit thing on the road |
| The Works | shell -274..-260 / -70..-56, mark -268 54 -64 | lever **-268 56 -64** on the andesite panel at -268 56 -65; the lever itself is Q71's |
| Josie's cellar | box -321..-314 / 13..21, stand -318 64 17 | iron door **-318 64 13**, sealed; 40 blocks of gravel to dig |
| The cottage | plot -330..-308 / 18..43, hearthstone -319 74 32 | ships with **no door, no glass, no bed and a hole in the roof** — that is Q3 |
| Lake / pier | lake mark -302 71 -10, pier -302 71 -10 | Act II's Lantern Float |
| Lantern road | 164 columns, spawn → farm gate → square | **40 posts**, all `createdeco:yellow_copper_lamp`, all `lit=false` at ship |

**The valley is dark on purpose.** Outside a building the only light is the forty posts and
the signpost lantern, and the posts ship unlit. Every template that arrives carrying
lanterns, torches, candles or a lit campfire has them blown out or removed at build time
(`douse()` in `plan_town.py`) — the bell tower alone would otherwise stand over the square as
a lighthouse, and Act I's payoff (six lamps come on) would have nothing to be a payoff
against. Lit windows *inside* a house are allowed and kept: that is the warmest thing in the
pack.

---

## How a player gets this world

**A friend installing for the first time** gets it automatically: packwiz downloads the
55 MB world with the rest of the pack, and the game opens in the valley. Nothing to do.

**A friend who already has the pack** does *not* get it. Every shipped world file is marked
`preserve = true` in `pack/index.toml`, which is what stops packwiz handing our copy back
over the top of theirs on every launch — a fix to the *world* only reaches people who have
not started yet. To take this world instead of theirs: quit the game and the launcher,
right-click the instance → **Minecraft Folder**, delete `saves/Little Kettle Valley`, and
launch. (Rename it to `saves/old valley` instead to keep the old one in the world list.)
Account, mods, keybinds and video settings are untouched either way.

**The server** is replaced by hand, because a server world is never downloaded:

```
tools/scripts/server_ctl.sh stop          # if it is up
rm -rf server/world
cp -R world-master server/world
rm -f server/world/session.lock
```

`world-master/` is the master copy and the only source of truth. `server/world` and
`pack/saves/Little Kettle Valley/` are both copies of it — the packaged copy drops
`level.dat_old`, `playerdata/`, `session.lock` and nothing else. To rebuild the master from
the pristine terrain: `scratch/master_build.sh build` (it restores `scratch/pregen/`, boots,
runs `/valley build all`, snapshots to `world-master/`, and re-packages into `pack/saves/`).
Re-run the planner first — `scratch/master_build.sh plan` — if anything in `plan_town.py`
changed.

---

## Proving it

Two harnesses, and they cover different halves.

**`tools/scripts/headless_playthrough.sh` — no client, safe to run any time.** Installs
`world-master/` into `server/world` twice, runs Act I alone on the first copy and every act
plus all 21 scenes on the second, then reads the verdict off the region files with the
server stopped (`tools/scripts/headless_assert.py`). It proves: the world ships dark, shut
and unbuilt; Act I lights exactly six posts and no more; the acts and scenes run clean; 39
posts burn; 15 residents stand where the registry put them; ten doors open, the Works lever
is thrown and the cellar door is open; and all 16 buildings and all 50 planner probes are
still standing at the end.

**`tools/scripts/playthrough.sh` — needs a Minecraft client, so it runs when Josh is away
from the Mac.** Everything above plus the half a console cannot reach:

- the **Q3 cottage placements** (door, two windows, bed, sconce) and the **Q7 stake** — these
  are `BlockEvents.placed` checks, and only a player's own hands fire that event;
- the **fortieth lamp**: Josie's porch post is lit by Q90's block-placed check and by nothing
  else. Act IV's sweep deliberately skips it and the Q74 scene says so out loud, so **39 of
  40 is the headless maximum** and 40 of 40 is a client-only result;
- the twenty **salted player blocks** — proof that nothing the story runs writes over a
  block a player put down;
- the **quest tree**: every quest completed in dependency order, and the full command audit;
- **tick times**: each finale wrapped in `debug start` / `debug stop`, which is the only
  measured claim that no tick in a finale went over its 50 ms budget;
- the **client log**: mixin failures, missing models and textures, FATAL lines. Nothing
  server-side can see any of them.

Terrain is checked separately and independently of both:
`scratch/nature_check.py --world world-master --baseline scratch/pregen` — 9 probes on cut
edges, bare stone faces, pad materials, doors, lamps, road steps, road banks, plaza drainage
and the sightline to the lake.
