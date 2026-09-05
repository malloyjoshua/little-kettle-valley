# Little Kettle Valley — the look pass

2026-09-05, 05:00–06:00. Offline client, `scratch/lookclient/.minecraft`, 3584 MB, render
distance 8 (the pack's own default), against `world-master/` installed as `server/world`.
Twenty screenshots in this folder, read one at a time. Nothing here is inferred from the
registry: every claim is either something visible in a numbered shot or a count taken off
the region files, and the counts are given so they can be re-run.

---

## The short version

The valley is **better than its arrival and worse than its aerial**. Standing inside it —
on the road by the pond (08), in front of the inn (11), in the cellar (07), at the square
after dark (19) — it reads as a place people live in: smoke off a chimney, lily pads,
lanterns on posts, a cow in the road, moss on a roof. Two hundred feet up (17) it reads as
a machine's output: the ground is scored with parallel contour steps for the whole width of
the bowl, and the buildings sit apart from each other on lawns.

The single worst thing was the first four seconds, and it was a one-line bug rather than a
design problem. It is fixed.

---

## What was wrong on arrival, and what it was

**She woke up facing the wrong way.** Measured, not guessed: `level.dat` carried
`SpawnAngle -180.0` and the player's `Rotation` on first join was `[0.0f, 0.0f]` — due
south, 180° from the road, the signpost and both lamp posts the arrival was solved around.
The old `01_first_join.png` was a featureless meadow with a dirt bank in it.

The cause is in vanilla, not in the plan. `setworldspawn <pos> <yaw>` writes `SpawnAngle`,
and `SpawnAngle` is used for **respawn**. A player who has never played is placed by
`ServerPlayer#fudgeSpawnLocation`, which calls `moveTo(..., 0.0F, 0.0F)` — yaw zero, every
time, whatever `SpawnAngle` says. So the world cannot set which way she looks; only a
command can. `valley_core.js` did already call `facePath` on first join, but at **tick 5**,
while the client is still on "Loading terrain", and it aimed at the *hearthstone* rather
than along the road.

Fixed in `pack/kubejs/server_scripts/valley_core.js`:

* `facePath` now uses the registry's own `spawn_yaw` when the player is within 6 blocks of
  `spawn` (the bearing `plan_town.py` solved the arrival on), and falls back to the hearth
  bearing anywhere else — the road bends before it reaches the hearth, so a bee-line is the
  wrong angle to hand her.
* the turn is made three times, at ticks 5, 40 and 100 (`facePathSettled`), so the last one
  lands after the client has the world on screen. It is idempotent, so a player who has
  already turned to look at something loses at most the first two seconds.

Verified end to end by joining as a player who had never played: `Rotation [-180.0f, 8.0f]`,
`Pos [-323.5, 74.0, 116.5]` — dead centre of the road head. A capture 3 s after
`joined the game` (`scratch/z_join_t3.png`) is still "Loading terrain…", so **the turn
completes before the first frame she ever sees**; there is no visible snap.

`01_first_join.png` is now the title card over the road, with the KETTLE FARM signpost and
its lit lantern on the right and the oaks framing. That is the opening frame the arrival was
designed for, and until this morning nobody had ever seen it.

---

## Reads as a place

* **08 road to town.** The best frame in the set. Road beside a lily-padded channel,
  lantern posts standing in the water, a long railed boardwalk, the bell tower behind, a cow
  in the way. Nothing here reads as placed.
* **11 the inn.** Timber frame, moss on the roof, smoke off the chimney, a lit window with a
  chair visible inside, tulips at the door.
* **07 the cellar.** Stone brick, iron door between two chiselled sockets, a hanging lantern
  and a floor lantern, one chest, one plinth. The most deliberate room in the pack.
* **16 Tess's house.** Chalet, flower boxes, tulips, a cobble path to the door, birch, lake
  behind.
* **19 the square after dark.** Warm, populated, legible.
* **05 the cottage** — after this morning's fix (below); the building itself was always good.

## Reads as generated

Ranked by how loudly.

1. **The valley floor is terraced.** From the ridge (17) the ground is scored with long
   parallel steps running the width of the bowl, well beyond anything built. Measured over
   `x -350..-260, z -90..60` (13,500 columns), built against the pristine pregen and
   ignoring vegetation: **41.6 % of columns regraded, mean 2.86 blocks, max 26**. The
   built terrain also *steps more often than nature did* — 3,971 risers against the pregen's
   3,086 over the same window, **+29 % steps per block travelled**.
   This is not a bug. It is `build_skirt()` working exactly as documented: the skirt is
   relaxed to a fixed point where *no column differs from any of its eight neighbours by
   more than one block*. A Lipschitz-1 surface cut into a hillside **is** a staircase. Every
   probe agrees it is fine — `cut_edge`, `stone_face`, `road_banks` all pass, and
   `road_banks` reports "worst verge rise 1 of 1134 tested (limit 1)". The geometry the
   probes are built to guarantee is the geometry that looks wrong.
2. **The road steps three blocks in front of her face.** In `02_after_title.png` the road
   runs four blocks and ends in what reads as a wall: two grey gravel side faces and a bare
   dirt centre. It is really the 1-block rise at `z=113` (road y74 → y75) seen head-on with
   the riser's top edge just *above* eye level, plus the same 1-block lip in the ground on
   both sides. A step in a road is fine; a step at the exact centre of the first frame,
   four blocks from the camera, is not.
3. **The square is furnished like a waiting room.** 24 seating blocks (18 `oak_chair`) in
   two dead-straight ranks down both sides of the plaza, plus 16 copper lamps and 47 fence
   posts inside 31×31. The floor is one unbroken grid of pale tiles.
4. **Grass islands with raw dirt sides, sitting in the paving** (14, and at every plaza
   edge). Rectangular blocks of turf standing a block proud of a grey plain, dirt showing on
   every vertical face. They look like pallets of turf nobody laid.
5. **The church is a cobblestone box** (15). No bell, no door, no glass, no roof — a grey
   rectangle with a taller grey rectangle on it. The crudest thing in the town, and it is
   called The Bell Tower.
6. **The greenhouse is a blank wall with glass stuck on it** (13). Panes at four different
   heights in no pattern, several apparently floating on the plank face.
7. **The quest book has no book** (20). `/ftbquests open_book` opens onto eight small icons
   drawn straight over the live world — chapter panel collapsed to a 6-pixel arrow, no
   chapter title, no subtitle, no background. The chapter *has* a title and a subtitle
   ("Spring, Year One. / Eight small things…") and neither is on screen. This is the pack's
   primary interface.
8. **"The mill by the water" is a seven-block puddle.** Exactly 7 water cells near the mill,
   `x -330..-324, z -44`, in a stone gutter. No race, no wheel, no flow.
9. **Bare earth where the pregen had none.** Surface columns whose top block is
   dirt/coarse dirt/gravel/stone in the bowl: **27 in the pregen (0.2 %), 1,073 in the built
   world (7.9 %)**. 879 of those are on designed road/plaza/pad cells and are meant; **194
   were scars**, and 61 of them were green in the pregen.
10. **The "unlit" valley is not dark.** All 40 lamps ship `lit=false` and act 1 lights 6 of
    them — verified off the region files, 0 lit → 6 lit. But compare `18_square_night_unlit`
    with `19`: the lighting is indistinguishable. `yellow_copper_lamp` renders warm orange
    unlit, other lanterns around the square are already lit, and the pale plaza floor reads
    fully at midnight. The act-1 payoff — the thing the pack is named after — has no visible
    before and after from the middle of the square.
11. **Render distance 8.** `pack/options.txt` ships `renderDistance:8`. From anywhere with a
    view (17) the world ends in a hard fog dome about 128 blocks out; from the square you
    cannot see the farm. See the memory numbers before raising it.
12. **The shipped world came with a mob population baked in.** Before this pass: 16 zombies,
    16 skeletons, **35 creepers** and 6 spiders inside 256 blocks of spawn, saved in the
    region files — there on the player's very first load of a cozy pack.
13. **The residents bunch up.** In 19 they are shoulder to shoulder at the waystone with
    nameplates overlapping.

---

## Fixed this pass

All world edits were applied to a **pristine** copy of `world-master` (the played world had
act 1 run on it and had to be thrown away — it carried `world/ftbquests`, world stage
`act2`, six lit lamps and the spawned residents; that would have shipped a world starting at
act 2). 252 `setblock`s, 0 errors, 0 "could not set", 0 unloaded.

| # | Fix | Before | After |
|---|-----|--------|-------|
| 1 | **Arrival facing** (`valley_core.js`) | `Rotation [0.0f, 0.0f]`, facing an empty meadow | `[-180.0f, 8.0f]`, down the road at the signpost — and it lands before the first frame |
| 2 | **The farm yard is neglected again.** The build group is commented "four years of nobody keeping the yard" and placed five blocks to say so. | 217 of 340 yard columns plain mown grass; sign reads "mind the weeds"; no weeds | 163 plants over 598 columns — 79 grass, 36 fern, 28 tall grass, 12 berry bushes, 8 flowers, deterministic by `cell_hash` so it is reproducible |
| 3 | **Bare-earth scars re-greened** — only columns that were green in the pregen, and only outside every designed surface and >1 block from every pinned registry coordinate | 61 columns of exposed stone/dirt/gravel, incl. the trench along the cottage foundation visible in the old 06 | grass |
| 4 | **Hostiles cleared from the shipped snapshot** | 73 hostiles inside 256 blocks of spawn, 35 of them creepers | 441 hostiles and loose items killed across the valley before the final save |
| 5 | **`LevelName`** | `"world"` | `"Little Kettle Valley"` |
| 6 | `playthrough.sh` gamedir | hardcoded to Josh's own Prism instance, which it packwiz-synced into and deleted logs from | `PLAYTHROUGH_GD` env override, default unchanged |

`nature_check.py --world world-master --baseline scratch/pregen`: **9/9 pass** after the
edits.

Screenshots 01, 02, 04, 05 are re-shot on the fixed world; the rest are as first found.

---

## What I did NOT fix, and why

**The terracing (#1) and the step in front of the arrival (#2) are planner changes and I did
not make them.** Both live in `plan_town.py`, both need `master_build.sh plan build`, and a
rebuild regenerates the world from the pregen — which would discard the 252 cosmetic blocks
above and require the whole 135-quest harness again. More importantly, the planner *solves*
the arrival by search: adding a constraint can change which candidate wins, and that moves
registry coordinates in a world that is already shipped. That is a decision to make awake.

The two changes I would make, in order:

1. **Hold the arrival leg flat.** `staircase()` currently puts a step at `z=113`, three
   blocks from her eye. Pin the first ~10 road columns out of spawn to one level, the way
   the plaza end is already pinned, and the opening frame runs clean to the signpost.
2. **Stop the skirt reading as a staircase.** The Lipschitz-1 fixed point is the right
   *safety* property and the wrong *appearance*. Either shrink its reach (`SKIRT_RINGS = 14`
   — it is regrading 42 % of the bowl to protect a road), or break the risers up in plan the
   way `hold_depth()` already breaks up the pad edges, so the steps wander instead of
   running parallel for eighty blocks. Whichever, re-run `nature_check` — `stone_face` and
   `cut_edge` are exactly what the current constraint buys.

**The church, the greenhouse and the mill race** are template/decoration work, not something
a handful of `setblock`s should fake at 5 a.m.

**The quest book** is a client-side FTB Quests theme question (pin the chapter panel open,
give the book a background). One config file, but it wants somebody to look at it in the
game and agree.

**Render distance** — the numbers are below; the call is Josh's.

**Anything applied by command lives only in `world-master`, not in the planner.** Fixes 2, 3
and 4 will vanish the next time `master_build.sh` runs. The yard scatter in particular
belongs in `plan_town.py`, in the group that already says "four years of nobody keeping the
yard".

---

## Memory and startup

MacBook, offline client against the local dedicated server, world-master installed, walked
spawn → farm gate → the bend → the square by `/tp`, then held at the square. RSS is the
whole JVM (`ps -o rss=`), so it includes the ~700–950 MB of non-heap the renderer needs on
top of `-Xmx`; the heap figure underneath it is what G1 actually reported live.

### 3072 MB, render distance 6 — the specified run

| phase | RSS min | mean | peak |
|---|---|---|---|
| join + world load | 3748 | 3895 | **3933 MB** |
| tp traverse to the square | 3644 | 3883 | **3945 MB** |
| steady at the square | 3025 | **3191** | 3656 MB |

* **GC: 232 young collections, 0 full.** Mean pause 9.3 ms, median 7.8, p95 25.8,
  **max 47.4 ms — not one pause over 50 ms.** 1.44 s of the 389 s run spent in GC (0.37 %).
* **Heap live after the last young GC: 1746 MB of 3072 MB committed.** The pack is not heap
  bound at this setting; it has about 1.3 GB of headroom.
* **Time to title: 29.5 s. Time to join: 31.8 s** (server saw the join). First frame in the
  world 37.6 s (ModernFix's own "Game took 37.578 seconds to start").

Verdict: comfortable. Nothing here is close to a stall — no full GC, no pause a player could
feel, and a third of the heap spare.

### 3584 MB, render distance 12 — measured because the fog dome is a real complaint

| phase | RSS min | mean | peak |
|---|---|---|---|
| join + world load | 4276 | 4456 | 4501 MB |
| tp traverse to the square | 4387 | 4496 | **4539 MB** |
| steady at the square | 2894 | **3326** | 4378 MB |

* GC: 178 young, 0 full. Mean 10.0 ms, p95 28.9, max 49.9 ms, again **none over 50 ms**.
* Heap live after the last young GC: **1781 MB of 3584 MB** — 35 MB more than at render
  distance 6.
* Time to title 26.6 s, join 28.8 s, first frame 34.3 s.

**Doubling the render distance cost 35 MB of live heap and ~600 MB of RSS, and changed
nothing about GC.** The cost is process footprint, not heap pressure: a machine that can
spare ~4.6 GB for the client can run render distance 12 with no other change. Raising
`pack/options.txt` from `renderDistance:8` to 10 or 12 is a cheap, large improvement to a
world built to be looked across — but it raises the pack's floor from ~4 GB to ~4.6 GB of
free RAM, so it is a call about who the pack is for, and I have left the shipped value at 8.

---

## Files

* `01`–`20` — the tour, in the order a player meets it. 01, 02, 04, 05 are on the fixed
  world; the rest are as first found.
* `scratch/z_join_t3.png` — 3 s after the join packet: still "Loading terrain". This is the
  proof the arrival turn lands before the player's first frame.
* `scratch/look_playthrough/` — the full harness run against this world-master:
  135/135 quests, 15/15 residents, 7/7 world asserts, 0 command errors, all five finales
  profiled at 20.06 TPS.
* `scratch/lookclient/rss_3072_rd6.tsv`, `gc_3072_rd6.log`, `rss_3584_rd12.tsv`, `gc12.log`
  — the raw memory samples behind the tables above.
