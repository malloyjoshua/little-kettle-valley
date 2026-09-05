# Our world edits — a forensic pass on what Little Kettle Valley actually does to the ground

Job R3. Local files only, no web. Everything below was read out of `pack/kubejs/server_scripts/*.js`,
`pack/kubejs/data/valley/functions/**/*.mcfunction`, `pack/kubejs/server_scripts/town_plan.js` and
`tools/scripts/plan_town.py`. Footprints and volumes are computed from the emitted commands, not estimated.

**The one-line finding:** every visible change in this pack is a *swap* — a hard `fill … minecraft:air` over a
rectangle, then a `place template` into the hole — executed synchronously, in one tick, at the exact moment a
quest card is claimed or a block is placed, with **no check anywhere in the pack for whether the box is empty,
whether the player is standing in it, or whether anything in it belongs to the player.** There is exactly one
piece of terrain-aware code in the whole system (`@pad` / `@padfix` in `valley_finales.js`), it was written
late, and the four biggest edits in Act I — the ruin pad, the cottage pad, the plaza and every street — do not
use it.

---

## 1. Every runtime edit, in play order

Column key:
- **Footprint** — the rectangle the edit touches, in columns (x × z), and the vertical span it clears.
- **Kills player blocks?** — whether a player build inside the box is destroyed. `fill` in its default
  (`replace`) mode **does not drop items**, so "yes" means gone, contents included.
- **Player inside?** — whether the player is, in normal play, standing inside the box when it runs.
- **Reads as** — swap (something is deleted and something else appears in its place, in one frame),
  additive (blocks appear, nothing is deleted), offscreen (happens where the player is not).

| # | Trigger | Code | Clears | Places | Footprint | Kills player blocks? | Player inside? | Reads as |
|---|---------|------|--------|--------|-----------|----------------------|----------------|----------|
| 1 | **First join** (once per world) | `valley_core.js:1012` `valleyFirstJoin` → `placeRuin` (`:811`) → `valley:setup/place_ruin` | `fill ~-11 ~1 ~-11 ~11 ~16 ~11 air` = **8,464 blocks**; `fill ~-11 ~-6 … ~11 stone` (2,645); `fill … ~-1 dirt`; `fill … ~0 grass_block` | `nova_structures:wild_ruin/wild_ruin_23` (10×11×9) at `~-7 ~-1 ~-6`; hearthstone `polished_andesite`; unlit campfire; 3 yard props; gate post + "KETTLE FARM" sign + 2 lanterns at `~0 ~1 ~8` | **23 × 23 = 529 columns**, cleared 16 up, dug 6 down | N/A (world is new) | No — 48–64 blocks away | **Offscreen**, but the title card `The Old Kettle Farm` and `playsound … bell.resonate` fire **at spawn, immediately** (see §4 item 6) |
| 2 | **First join**, same tick | `valley_core.js:777` `ruinPath` | Per step: `setblock … dirt_path/gravel` at that column's own surface + `setblock … air` one above | 3-wide dirt path + gravel verges; oak-fence post + lantern **both sides** every 6 steps | 48–64 long × 3 wide ≈ **150–200 columns**, +~20 lamp posts | N/A | No | Offscreen |
| 3 | **First join**, same tick | `valley_core.js:915` `spawnSignpost` | 2 blocks | Oak sign + lantern, 3 blocks along the path from spawn | 1 column | N/A | Yes — ~3 blocks from the player | Additive |
| 4 | **Q2 — waystone on the hearthstone** | `valley_checks.js:112` (BlockEvents.placed) | `setblock <the waystone the player just placed> waystones:waystone{WaystoneName:"Home"}` — the placed block is **destroyed and re-created** | Home waystone | 1 block | The player's own waystone | Yes | **Swap**, invisible-but-consequential (§3) |
| 5 | **Q2**, same tick, once per world | `valley_checks.js:149` → `valley:act1/cottage` | `fill ~-11 ~0 ~-14 ~11 ~15 ~11 air` = **9,568 blocks** — the entire ruin, the campfire, the gate sign, the yard fences, *the waystone from #4*, and anything the player put down; then `dirt` at `~-4..~-3`, `coarse_dirt` at `~-2`, `grass_block` at `~-1` (**598 columns forced to one Y**) | `kaisyn:village/meadow_swiss/houses/meadow_small_house_1` (9×10×9) at `~-4 ~-1 ~-4`; hearthstone re-set; Home waystone re-set **again**; wool mat, red carpet, porch cobble, 27 `dirt_path` garden tiles, 23-block pen outline, 2 signs | **23 × 26 = 598 columns**, cleared 16 up, dug 4 down | **YES — worst offender in the pack** | **Yes — the player is standing on the hearthstone** | **Swap.** The building you walked 60 blocks to see is deleted and a different building appears around your head, in one frame |
| 6 | **Q5 — dig out the cellar** | `SCENES.cellar` (`valley_finales.js:~1570`) → `valley:act1/cellar_door` at `home + [0,-6,0]` | `fill ~-3 ~-1 ~-3 ~3 ~3 ~3 stone_bricks hollow` then hollow it out — overwrites whatever is at home.y-7 … home.y-3 | 7×7×5 stone-brick room, iron door, chalk sign, chest, 3 lanterns, waystone plinth | **7 × 7 = 49 columns**, 5 tall, entirely underground | Yes (anything mined/built in that shell) | Yes — the player is at the bottom of the stairs | Swap, but underground and small — this one reads fine |
| 7 | **Q7 — place the Surveyor's Stake** | `valley_checks.js:162`; on refusal `setblock … air` + `give … valley:town_anchor 1` | On refusal: the stake block, silently | Nothing | 1 block | The stake | Yes | Swap — **the stake you just planted disappears** and reappears in your hand, with one red action-bar line |
| 8 | **Q7 reward**, once per world | `SCENES.square_path` → `valley:act1/square_path` at the anchor | `fill ~-3 ~1 ~-3 ~3 ~6 ~3 air`; `fill ~-1 ~1 ~1 ~1 ~6 ~24 air` (3×24×6); `fill … ~0 stone_bricks` — **this overwrites the anchor block itself**, i.e. the stake | 7×7 stone-brick pad, 24-block cobble road south, gravel verges, 2 lit lamp posts, 2 lanterns | **~155 columns**, 6 up, 5 down | Yes | **Yes** | Swap — the stake vanishes under paving |
| 9 | **Q8 — sleep one night**, three scenes in one claim | `SCENES.inn` → `act1_inn`; `SCENES.bram` → `act1_mill`; `SCENES.marnie` → `act1_marnie` | `@pad` clears 20/32/16 blocks up and digs 10 down over each pad | Tavern (`tavern_house_spruce`), windmill + `valley:mill_race`, Marnie's chalet, aprons, lamps, NPC imports | inn **23×21 = 483** (486 cols total); mill **21×22 = 462** (504); marnie **13×13** (172) | Yes, inside any pad | No — 60+ blocks away | **Offscreen**, but each group ends in `title @a` + `playsound … @a`, so **three title cards and three toasts stack on the player in bed** (§4 item 7) |
| 10 | **Q10 — fence the pen** | `SCENES.coop` → `valley:act1/nesting_box` at `home + [4,-1,-9]` | `fill ~-2 ~1 ~-2 ~2 ~4 ~2 air` | 5×5 grass floor, plank centre, 2 `farm_and_charm:chicken_nest`, hay, slab, 2 lamp posts, sign, 2 eggs as items | **5 × 5 = 25 columns**, 4 up | Yes (inside the pen you just fenced) | Usually yes | Swap, small — reads fine |
| 11 | **Q11 — three eggs to Marnie** | `SCENES.pip` → `act1_pip` | `@pad` 16 up, 10 down | `meadow_small_house_1`, apron, duck | **13 × 13 = 169** (172 cols) | Yes | No | Offscreen + title card |
| 12 | **Q19 — "Sweep Oda's Store"** → **Act I finale** | `finaleAct1` (`valley_finales.js:764`): `act1_square` + `act1_streets` + `act1_lamp_pads` + 24 inline setblocks | `act1_square`: `fill ~-12 ~1 ~-12 ~12 ~14 ~12 air` (**8,750 blocks**) + `dirt` y-10..-2 + `stone` y-1 + `cobblestone` y0 — a hard **25×25** slab, no feather. `act1_streets`: **1,174 columns**, each `fill dy1..dy6 air` + `fill dy-5..dy-1 dirt` + one paving `setblock`. `act1_lamp_pads`: 57 columns cleared 5 up | Well (top + bottom), 4 market carts, Town Square waystone, 8 benches, 12 flower boxes, 14 lamps, 6 lit lamp posts; then season/time/weather set, worldborder 3000, loot, 5 NPCs | **plaza 25×25 = 625; streets 74 × 72 bounding box, 1,174 real columns**; ~**3,922 commands in one tick** | **YES, everywhere** | **Yes — this fires wherever the card is claimed; normally in the square** | **Swap, at scale.** One synchronous burst; the server hitches, then 74×72 of the world is different |
| 13 | Act I finale, arrival beat | `finaleAct1` second beat + `act1_tobin` + lake segment | `@pad` 9 up over Tobin's outcrop; `fill ~-4 ~0 ~4 ~4 ~7 ~12 air` + `stone` + `sand` at the lake mark | Tobin's ore + NPC; Nella's boat, campfire, stairs, barrel, lamp | tobin **11×11**; lake beach **9×9** | Yes | No | Offscreen |
| 14 | **Q34 — lamp posts** | `valley_checks.js:295` | The post the player just placed | `setblock … LAMP_DARK` — the placed lamp is destroyed and re-created in a normalised state | 1 block each | The player's own lamp | Yes | Swap, 1 block — reads as "it snapped into place", acceptable |
| 15 | **Q40 — "Fill Oda's Three Notices"** → **Act II finale** | `finaleAct2` (`valley_finales.js:864`) | `fill ~-14 ~1 ~-14 ~14 ~10 ~14 air` (**29×29×10 = 8,410**) + `fill ~-14 ~-2 … ~14 stone` (2 courses) at the Lake mark; then `fill ~-9 ~-4 ~9 ~9 ~-1 ~25 stone` (basin shell), `fill ~-9 ~0 ~10 ~9 ~8 ~25 air`, five `replace water` plugs, `fill ~-8 ~-3 ~10 ~8 ~-1 ~24 water` | `valley:pier`, sandstone beach, 12 lantern rafts, 3 giant + 12 small lily pads, 34 fence rails, 6 candle holders, Pier waystone, fireworks | **29 × 29 = 841 columns** at the lake, cleared 10 up, dug 4 down | **YES** | Yes (the card is claimed anywhere; the build is at the lake) | Swap — a lake is deleted and a different lake is built |
| 16 | Act II finale, same tick | `act2_granary` (15×14 pad), `act2_garden` (14×13 pad), **re-run of `act1_streets`** | `@pad` 20 / 11 up, 10 down; then all 3,682 street commands again | Rustic barn + 12 alcoves; classic small farm | granary **217 cols**, garden **182 cols**, streets **1,174 cols again** | **YES — the streets re-run wipes anything built on or over a road since Act I** | Possibly | Offscreen + swap |
| 17 | Act III–V (out of scope, listed for completeness) | `act3_store` (261 cols), `act3_church` (170), `act3_table` (29), `act4_greenhouse_shell/glaze/heat` (221/117/16), `act4_bathhouse` (179), `act4_works` + shell (225, underground), `act4_works_light` (5), `act4_beds` (6), `act4_bram_chair` (2), `act4_lamp_sweep` (21), `act5_townhall` (361), `act5_tess` (287), `act5_mab` (290), `act5_corin` (259) | pads + air fills as above | 8 more templates + 2 hand-built shells | — | Yes | Mostly no | Offscreen |

**Totals:** 26 build groups, **5,641 commands** in `town_plan.js`, plus 5 hand-written `.mcfunction` files and
~15 inline `runSeg` segments in `valley_finales.js`. The Act I finale alone is ~3,922 of those commands, all
issued inside a single server tick with no throttle (`runSeg`, `valley_finales.js:303`, is a plain `forEach`).

---

## 2. The one piece of terrain-aware code, and where it isn't

`@pad` / `@padfix` (`valley_finales.js:242` `padApply`) is genuinely good work: it samples the ring 3 blocks
outside the pad for the surface material the generator actually laid, lays the pad's top course in *that*
material instead of hard-coded grass, and feathers the outer two rings with a deterministic coordinate hash
(50% pad material one in from the edge, 25% on the edge itself), putting snow layers back where the sample
says the site is snowy.

**Every `@pad` in the pack is in `town_plan.js`, and none of the Act I hero moments use it:**

| Edit | Feathered? | Material |
|------|-----------|----------|
| `place_ruin.mcfunction` (the farm) | **No** | Hard `fill … minecraft:grass_block`, 23×23, straight edge |
| `cottage.mcfunction` (your home) | **No** | Hard `fill … minecraft:grass_block`, 23×26, straight edge |
| `square_path.mcfunction` (the stake) | **No** | Hard `fill … stone_bricks` / `cobblestone` |
| `act1_square` (the plaza) | **No** | Hard `fill … cobblestone` + `stone_bricks` + `polished_andesite`, 25×25, gravel border |
| `act1_streets` (1,174 columns) | **No** | `setb … cobblestone / gravel / stone_bricks / dirt_path` per column |
| `act1_lamp_pads` | **No** | Hard `gravel` 3×3 |
| The 15 building groups | **Yes** | `@pad` sampled + feathered |

So the two places the player spends the entire first act — **the farm and the town square** — are the two
places with the hardest edges in the pack. The feathering only shows up on plots she mostly walks past.

---

## 3. Block by block: what happens when the waystone goes on the hearthstone

The player is standing on the hearthstone, holding the Homestead Waystone. She right-clicks. All of this
happens in **the same tick**, in this order:

**Step 0 — the block lands.** Vanilla/Waystones places `waystones:waystone` at `(hx, hy+1, hz)` — call it
`H`. Waystones' own behaviour on placement is to open the naming screen and register the stone to the
placing player.

**Step 1 — `BlockEvents.placed` fires** (`valley_checks.js:112`). `nearRuinHearth` accepts it (±4 x/z, ±3 y
of the ruin hearthstone). `v.setHome(b.x, b.y, b.z)` records Home.

**Step 2 — the waystone is destroyed and re-created:**
```
setblock <H> waystones:waystone{WaystoneName:"Home"}
```
This is not a rename. `/setblock` removes the block entity and creates a new one. The waystone the player
placed — with whatever UUID Waystones assigned it and whatever name she was typing into the open screen —
is gone; a *different* waystone with the same block state stands in its place. **The naming screen she is
looking at is now editing a block entity that no longer exists.** Any activation she got from placing it
points at a dead UUID.

**Step 3 — `valley:act1/cottage` runs, positioned at `H`** (`valley_checks.js:151`, once per world). Its
first line is:
```
fill ~-11 ~0 ~-14 ~11 ~15 ~11 minecraft:air
```
`~0` is `H`'s own Y. So this is a **23 × 26 × 16 = 9,568-block** air fill whose *bottom layer is the
waystone she just placed*. In one command it deletes, with no drops:

- **The waystone from Step 2** (it is at `~0 ~0 ~0`, inside the box).
- **The entire ruin above the hearthstone** — `wild_ruin_23` occupies `~-7..~2` x, `~-6..~2` z, up to `~+8`.
  The three walls and the chimney the letter promised, the thing she walked 48–64 blocks to find, gone.
- **The cold campfire** at `~-1 ~1 ~0` — the "cold hearth" the title card named 20 minutes earlier.
- **The gate**: the oak post, the "KETTLE FARM / J. Kettle / mind the weeds" sign and its two lanterns at
  `~0 ~1 ~8` / `~±1 ~1 ~8` — the marker that told her she'd arrived.
- **The yard props** — the two oak fences and two mossy cobblestones "four years of nobody keeping the yard".
- **Everything the player put down.** There is no player-block check anywhere in this pack. A torch, a
  crafting table, a furnace, a bed, a shelter thrown up against the ruin wall while it was getting dark, a
  chest with the contents of her first hour in it — all inside the 23×26 box, all inside `~0..~15`, all
  deleted **without dropping**, because `fill` in `replace` mode destroys silently.
- **Two blocks of the lit path**, where it runs into the box on the north side (`~-14` reaches 14 north of
  the waystone, and the path arrives from that direction).

The three lines after it finish the job downward:
```
fill ~-11 ~-4 ~-14 ~11 ~-3 ~11 minecraft:dirt          <- 1,196 blocks, kills any digging
fill ~-11 ~-2 ~-14 ~11 ~-2 ~11 minecraft:coarse_dirt
fill ~-11 ~-1 ~-14 ~11 ~-1 ~11 minecraft:grass_block   <- 598 columns forced to ONE Y
```
That last line also overwrites the hearthstone itself with grass — it is put back four lines later by
`setblock ~0 ~-1 ~0 minecraft:polished_andesite`.

**Step 4 — the cottage materialises.**
```
place template kaisyn:village/meadow_swiss/houses/meadow_small_house_1 ~-4 ~-1 ~-4
```
A 9×10×9 Swiss chalet appears with its interior floor centre exactly on the hearthstone — i.e. **around the
player's body**. She is standing at the centre of the floor, so she is usually inside the room rather than
inside a wall, but nothing in the code checks or moves her; step one block off-centre while clicking and the
template writes solid blocks into her hitbox.

**Step 5 — the Home waystone is re-created a *second* time:**
```
setblock ~0 ~-1 ~0 minecraft:polished_andesite
setblock ~0 ~0 ~0  waystones:waystone{WaystoneName:"Home"}
```
So within one tick the waystone block entity is created three times (player place → setblock → fill-air
delete → setblock) and destroyed twice.

**Step 6 — the yard is chalked out**: 27 `dirt_path` tiles for Q9, a 23-block cobblestone pen outline for
Q10, two instructional signs, the wool mat and red carpet for Q3's bed, the porch cobble for Q90.

**Step 7 — the flavour line and sound**, `tellraw @a[distance=..64]` + `playsound … block.wood.place`.

### So: what "everything that's there breaks"?

| Thing | What happens |
|-------|--------------|
| The ruin (3 walls + chimney) | Deleted. The whole reason she walked here. |
| The campfire | Deleted. |
| The gate, sign, lanterns | Deleted. |
| The yard fences / mossy cobble | Deleted. |
| **Anything the player placed** | **Deleted, no drops, chest contents included.** |
| **Anything the player mined** | Backfilled with dirt, 4 layers down. |
| The waystone she just placed | Destroyed and re-created twice; naming screen orphaned; activation invalidated. |
| The lit path where it enters the yard | Overwritten with grass. |
| The player | Not moved, not warned, not protected; a template is written around her body. |

Every one of those is a `fill`/`setblock` with no precondition. Nothing here is a bug in the sense of a typo —
the code does exactly what it says. The design is "delete the rectangle, paste the new rectangle," and the
player is standing in the rectangle.

---

## 4. Why the home "does not feel naturally on land"

Five separate causes, all visible in the same frame.

**(a) The 23×23 pad is cut to the *highest* point of the site, not the ground under it.**
`ruinSiteOk` (`valley_core.js:758`) samples 9 columns — centre and 8 probes at ±8 — rejects the site if any
probe differs from the centre by more than 5, and then **returns `top`, the maximum**:
```js
let top = c
for (…) { if (Math.abs(h - c) > 5) return -1; if (h > top) top = h }
return top
```
The comment says this on purpose ("Proud of a slope beats buried in it"). The cost is that on any site with
even 3 blocks of relief — which is most overworld terrain — the pad is cut at the high corner and the whole
23×23 platform stands **up to 5 blocks proud of the ground on the downhill side.**

**(b) Underneath that platform is a solid block of stone with vertical sides.**
```
fill ~-11 ~-6 ~-11 ~11 ~-2 ~11 minecraft:stone     <- 23 × 23 × 5 = 2,645 blocks
fill ~-11 ~-1 ~-11 ~11 ~-1 ~11 minecraft:dirt
fill ~-11 ~0  ~-11 ~11 ~0  ~11 minecraft:grass_block
```
On the downhill side that stone is *exposed* — a grey, perfectly rectangular cliff face up to 5 blocks high,
capped with a 1-block dirt band and a grass lid. That is the visual signature of a creative-mode plinth, and
it is the first thing she sees walking up the lit path.

**(c) The grass cap is a hard rectangle with a straight edge and no transition.**
`fill … minecraft:grass_block` over the full 23×23, always grass, regardless of biome. In a snowy highland,
a taiga, a savanna or a badlands the farm is a green lawn in a biome with no lawns — the exact complaint the
`@pad` handler was written to fix, on the one pad that never got it. There is no feather, no material
sampling, no snow restoration. The boundary is a 46-block-long dead-straight line at every edge.

**(d) The cottage pad then *extends* that rectangle asymmetrically and re-does it in a different shape.**
`cottage.mcfunction` levels `~-11..~11` x by `~-14..~11` z — **23 × 26**, not 23 × 23. It is offset 3 blocks
north (to make room for the garden and pen), so after Q2 the farm sits on an L-shaped compound of two
overlapping rectangles at two slightly different treatments: the ruin pad's grass over stone, and the cottage
pad's grass over coarse dirt over dirt. Where they don't overlap you get a visible seam.

**(e) The pad is cut at the *hearthstone's* Y, and the cottage at the *waystone's* Y (one higher).**
`place_ruin` treats `~0` as the ground; `cottage` treats `~-1` as the ground because it is positioned at the
waystone. That is internally consistent, but it means the finished house floor sits at the hearthstone level
while the surrounding yard grass is also at that level — so the chalet has no stoop, no step, no threshold.
It reads like a model dropped on a board.

**Bonus, same family:** the lit path that brings her here is drawn one column at a time at each column's own
surface (`ruinPath`, `valley_core.js:777`) and **skips any column where `ruinSurface` returns -1** — which
includes water, ice and lava. So a path crossing a stream simply has a hole in it, and a path up a steep
slope becomes a broken dotted line of `dirt_path` blocks at different heights with no steps cut between
them: you can see it, and you can't walk it.

**And the town has the same problem one level up:** the Town Anchor is the *stake block*, which the player
places standing on the ground — so `anchor.y = surface + 1`. Every pad, plaza and street course is laid at
`~0` = `anchor.y`. That puts the entire 74×72 town **one block proud of the terrain it was staked into**, with
a kerb all the way round; and `street_cmds` clears only 6 blocks up and digs only 5 down, so anywhere the
terrain deviates from the anchor's height by more than that, the High Street is either a dirt ledge floating
over a slope or a trench with a ragged ceiling of untouched hillside over it.

---

## 5. The ten worst glitch moments a first-time player hits in Act I and II

Ranked by how badly each one breaks the fiction, not by how hard it is to fix.

1. **Placing the waystone deletes the farm you just walked to.** — `cottage.mcfunction` line 1,
   `fill ~-11 ~0 ~-14 ~11 ~15 ~11 minecraft:air`, 9,568 blocks, same tick as the placement.
2. **Everything you own inside that box goes with it, without dropping.** — `fill` runs in `replace` mode,
   which destroys silently; there is no player-block check anywhere in the pack, so a chest and its contents
   are simply gone.
3. **Your waystone is destroyed and re-created twice in one tick.** — `valley_checks.js:143` setblocks over
   it, the cottage's air fill deletes it, `cottage.mcfunction` step 4 setblocks it again; the naming screen
   you have open is orphaned and the activation you just earned points at a dead block entity.
4. **A house is written around your body with no safety check.** — `place template … ~-4 ~-1 ~-4` runs while
   you stand on the hearthstone; nothing moves the player or verifies the space is clear.
5. **The farm arrives on a rectangular stone plinth.** — `ruinSiteOk` returns the *highest* of 9 probes and
   `place_ruin` fills stone y-6..y-2 over a hard 23×23, so on any slope you approach a grey cliff with a
   green lid and a 46-block straight edge.
6. **"The Old Kettle Farm" title card plays at spawn, before you have taken a step.** —
   `place_ruin.mcfunction` ends in `title @a` + `execute at @a run playsound`, and `placeRuin` is called from
   `valleyFirstJoin`; the arrival beat fires 56 blocks before the arrival.
7. **Sleeping one night stacks three title cards and three toasts for three buildings you cannot see.** — Q8
   claims `scene inn`, `scene bram` and `scene marnie` in one tick; each group ends in
   `title @a times 10 60 20` + `playsound … @a`, so the three overwrite each other and the sounds pile up
   while you are in bed 60+ blocks away.
8. **The Act I finale runs ~3,900 commands in one server tick while you are standing in the box.** —
   `runSeg` (`valley_finales.js:303`) is an unthrottled `forEach`; `act1_square` (8,750-block air fill) +
   `act1_streets` (1,174 columns × 3 commands) + `act1_lamp_pads` land together. The game hitches, then
   74 × 72 blocks of world are different.
9. **The Surveyor's Stake disappears the instant you plant it.** — `square_path.mcfunction`'s
   `fill ~-3 ~0 ~-3 ~3 ~0 ~3 minecraft:stone_bricks` is at the anchor block's own Y, so it paves over the
   stake; and on a *rejected* placement `valley_checks.js:170` setblocks the stake to air and hands it back
   with a single red action-bar line.
10. **Q7 silently demands you walk 58–76 blocks from the cottage, and only tells you "walk up until the
    chimney is small behind you."** — `townWouldSwallow` tests the hearth against `town_box` `x [-48, 63]`,
    `z [-45, 60]` grown by `town_clearance: 12`, so the stake is refused unless the anchor is more than 60
    blocks west / 75 east / 57 north / 72 south of Home. There is no in-world indicator of the boundary, so
    this is trial-and-error with an error message.

**Runners-up** (real, slightly less visible): the Act II finale re-levels 29 × 29 of lakefront to stone and
**re-runs all 3,682 street commands**, wiping anything built on a road since Act I; every finale yanks
`season set`, `time set` and `weather` out from under whatever the player was doing; the town platform sits
one block proud of the world with a kerb all the way round; and **no paving ever connects the homestead to
the town** — the High Street runs `anchor + z13..z31` and the cottage is 60+ blocks away across raw terrain.
