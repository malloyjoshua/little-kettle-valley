# Transitions: why the valley feels glitchy, and how to fix it

From three research passes in `docs/research/`: `story-pack-worlds.md`, `forge-world-toolbox.md`, `our-world-edits.md`.

---

## 1. Why it feels glitchy

Every visible change in this pack is a **swap** — delete a rectangle with `fill … air`, paste a template into the
hole — run synchronously in one tick, with no check for whether the box is empty, whether it holds anything the
player made, or whether the player is standing in it. When she puts the waystone on the hearthstone, the very first
line of `cottage.mcfunction` is a 23x26x16 air fill (9,568 blocks) that deletes the ruin she walked 60 blocks to
find, the campfire, the KETTLE FARM sign, the waystone she just placed, and anything she'd set down — `fill` in
replace mode destroys silently, so a chest goes with its contents — and then writes a 9x10x9 chalet around her
body. It doesn't sit on the land because the pad is cut to the *highest* of nine probes over a 23x23 block of solid
stone, capped with hard grass and a 46-block dead-straight edge, so on any slope you walk up to a grey plinth with a
green lid — and the one piece of terrain-aware code in the pack (`@pad`, which samples the real surface material and
feathers the outer rings) is used on none of the Act I hero moments.

---

## 2. What the loved packs actually do

- **Nobody destroys a structure the player has already visited.** Packs praised for their world either ship a
  finished hand-built map (Tolkiencraft III, Material Energy) or place structures once at worldgen and never touch
  them again (Homestead — the pack you liked; its docs tell server owners to *protect* the starter village).
- **The one pack that does "the world evolves" well — Prominence II's Kingdom of Vaaz — evolves by unlocking**:
  new dialogue, new services, new areas opening in a city you've been visiting since the start. Never a demolition.
- **Vault Hunters splits persistent home from disposable instance** — the scripted space is somewhere you enter and leave; your own base is never scripted.
- **The only pack found that spawns structures over player builds is The Broken Script — a horror mod**, whose own wiki names that mechanic as the source of unease. It's the mechanic we ship as a cozy beat.
- **Smooth onboarding is always sequential**: the first player action is trivial and the world sits still. We ask her to place the waystone at the exact instant the ground is rewritten.

---

## 3. Three architectures

### A — Ship a hand-built world (one seed for everyone)

The farm, the valley, the town site and the Works are built once, by hand, in a saved world we ship. Story beats only
ever **add**: furnish, light, unlock a door, move a person in. The cottage is either rebuilt by her from a kit
(Stardew-like), or raised overnight while she sleeps.

- **Multiplayer / her Air:** best case by a distance. She joins your server, so she downloads *nothing* — a
  dedicated server just reads whatever `level-name` points at; drop the world folder in before first boot. Zero
  runtime rebuild means no 3,900-command tick, no 74x72 chunk re-send burst to an 8 GB M2 Air at render distance 6.
  Singleplayer friends get it once as a zipped `preserve: true` packwiz entry — shipped once, never overwritten.
- **Quests:** all 126 survive. Gather/craft/deliver tasks don't care. The ~20 scene hooks stop cutting pads and
  become "teleport this NPC, place these six props, open this door." Coordinates become a fixed registry instead of
  runtime anchors — simpler than what's there now.
- **Town planner:** `plan_town.py` becomes a build-time tool — run it once into a scratch world, hand-tune until it looks like a place. The 5,641 commands in `town_plan.js` go away.
- **We lose:** a fresh seed per world, "your valley is unique," and the ability to re-roll if you hate the terrain.
  Everyone's Kettle Valley is the same valley. **Effort:** high (days of hand-building). **Risk:** low, and it's the
  only option with no live world-editing left to go wrong.

### B — Keep procedural terrain, place the designed valley at world creation as a real jigsaw structure

Register the valley as an actual vanilla jigsaw structure with `terrain_adaptation: beard_thin` — the mechanism
villages use to stand on natural ground instead of a cut pad.

- **Multiplayer / her Air:** fine at runtime; the cost moves to world generation (Life in the Village 3's recurring complaint is map-gen stalls once big structure mods land) — a one-time long first load.
- **Quests:** the coordinate problem gets *harder*, not easier — every site is seed-dependent, so the whole
  registry stays dynamic, as today.
- **Town planner:** becomes template pools and jigsaw JSON. Real work, and a 48x48x48 cap per piece means the town
  must be decomposed into pieces regardless.
- **We lose:** control over where the valley lands relative to spawn — research finding: `structure_set` has **no**
  `spawn_override` field; you tune spacing/separation/salt for *likelihood*, not a guarantee. **Effort:** high, and
  it's the least-understood path (a real engineering project, not a mod install). **Risk:** medium-high.

### C — Keep the current runtime approach, make every edit additive, offscreen and small

Write a KubeJS block-by-block placer that reads structure NBT and skips any position that doesn't match a stored
baseline; fire it on the sleeping→awake edge the pack already detects; delete every `fill … air`.

- **Multiplayer / her Air:** better than today, but the placer still runs while she's connected, and she can be awake when someone else sleeps. Needs throttling across ticks.
- **Quests:** unchanged — this is the smallest-diff option.
- **Town planner:** unchanged, but every one of its 26 groups needs re-emitting as additive, and `@pad` (or better)
  needs applying to the ruin, cottage, plaza and all 1,174 street columns that don't have it.
- **We lose:** nothing structurally — but we keep the thing every loved pack avoids: a world that edits itself
  around a player. **Effort:** medium. **Risk:** medium — bespoke code that can only be proven by testing, forever.

---

## 4. Recommendation

**Do A: ship one hand-built world.** It's the only option where the failure mode stops existing rather than getting
managed — no pad-cutting, no fills, no template written around anyone's body, so nothing is left to be glitchy. It's
also what the pack you liked does: Homestead's world is simply *there*, static and protected. The multiplayer story is the clincher — she plays on your
server, so a shipped world costs her exactly nothing to download and removes the single biggest hitch source from a
3 GB heap on an 8 GB Air. It kills the most code (5,641 planner commands, five mcfunctions, ~15 inline segments),
keeps all 126 quests, and turns the town planner into what it should always have been: a first-draft generator for a
human to hand-tune. The price — one seed for everyone, no re-rolls — is one the shipped-map packs (Tolkiencraft, Material Energy, Blightfall) all pay happily, and it buys back the hand-authored feel people fall in love with.

### Implementation plan

1. **Freeze the seed; generate and pre-explore the master world headless.** Pick the seed, run Chunky over the
   valley footprint, boot the server on it. *Verified:* server log shows clean boot on the frozen seed; region-file
   read confirms every chunk in the footprint exists.
2. **Convert `plan_town.py` from command emitter to world writer.** Same layout maths, output written directly into
   the master world (offline NBT write or a one-time creative pass), never at runtime. *Verified:* region read
   asserts each of the 26 build groups is present at its planned coordinates.
3. **Hand-tune every site — no rectangles.** Farm, cottage plot, plaza, streets, lakefront, the Works. Slopes
   feathered by hand, plinths removed, materials matched to the biome, a real path from homestead to town.
   *Verified:* a scripted probe reads the surface Y and block id along each site's perimeter and fails on any
   straight run longer than 8 blocks at one height, or any exposed `stone` face over 2 tall.
4. **Publish a fixed site registry** (`valley_sites.json`: hearth, plot corners, every NPC home, every door). Rip
   out runtime anchoring, `ruinSiteOk`, `townWouldSwallow` and the Surveyor's Stake gate. *Verified:* headless probe
   `/execute` at every registry coordinate returns the expected block.
5. **Build the additive beat kit** — one KubeJS helper that only ever writes into air or into a block matching a
   stored baseline, throttled to ≤200 blocks per tick, plus an overnight scheduler on the existing
   sleeping→awake edge, plus announce-before / acknowledge-after helpers. *Verified:* unit-style scenario — place
   junk in a beat's footprint, run the beat, assert every junk block still stands and nothing dropped.
6. **Rebuild the cottage beat.** The ruin is shipped as a habitable shelter she can sleep in from night one. The
   waystone only *registers* home (no `setblock` over her own block, no naming screen orphaned). The rebuild is a
   kit + a night: she stocks the materials, sleeps, and wakes to the cottage. *Verified:* scripted walk-through
   places a chest and a torch on the plot, sleeps, and asserts both survive and the cottage exists.
7. **Retire the finales' terrain work.** Acts II–V keep their beats but only unlock, dress, light and populate —
   the pads, plaza, street re-runs and lake re-level are deleted. *Verified:* grep asserts zero `fill … air` and
   zero `place template` remain in runtime scripts.
8. **Re-point the 126 quests** to the registry, and split every "meaningful action" beat from its world change by
   at least one night. *Verified:* full headless playthrough — all 126 sent and acknowledged, 0 refused.
9. **Ship it.** World folder into the server's `level-name` before boot; zipped `preserve: true` packwiz entry for
   singleplayer friends; her DMG unchanged. *Verified:* fresh-install test on a clean machine, plus a second client
   joining the server.
10. **Prove it end to end.** Region-file diff of the whole footprint before and after a full playthrough with player
    blocks salted throughout. *Verified:* zero player-placed blocks changed; no server tick over 50 ms during any
    beat.

### The rules every transition follows

1. **Never replace a player-placed block.** Not to normalise it, not to re-key it, not to make room.
2. **Nothing changes inside her view while she watches** — unless it's a reveal she triggered and is meant to see.
3. **Changes land overnight, or behind a door.** Sleep-edge or first-open, never mid-stride.
4. **Announce before, acknowledge after.** She hears it's coming; the next morning something tells her it's done.
   No title card fires for a building she can't see.
5. **Terrain is never cut into rectangles.** Sample the real surface, feather the edges, follow the slope — or
   don't touch the ground at all.


---

## 6. Where the plan actually got to (2026-09-05)

Steps 1-4, 7, 8 and 10 are done and the harness proves them on every run. What follows is the
honest state of each, and the two places the plan changed shape when it met the world.

| step | state | how it is proved |
|---|---|---|
| 1 freeze the seed, pre-explore | **done** | `scratch/master_build.sh pregen`; the pristine pregen is snapshotted to `scratch/pregen/` and every later phase reads it |
| 2 planner writes the world | **done** | `/valley build all` from `valley_build.js`; 35 groups, 14,614 commands, into the master save, never at runtime |
| 3 no rectangles | **done** | `scratch/nature_check.py --world world-master --baseline scratch/pregen` — 8/8 |
| 4 fixed registry, runtime anchoring gone | **done** | `valley_sites.json` + generated `valley_sites.js`; `ruinSiteOk`, `ruinPath`, `placeRuin`, `spawnSignpost`, `townWouldSwallow`, `townBox` and the whole Q7 stake guide are deleted |
| 5 additive beat kit | **changed shape — see below** | `put()` / `swap()` / `openDoor()` in `valley_finales.js` |
| 6 the cottage beat | **changed shape — see below** | the cottage is shipped standing; Q2 registers Home and changes nothing |
| 7 retire the finales' terrain work | **done** | `runSeg()` refuses `@pad`, `place template`, `fill`, `clone` and `run function valley:`; `playthrough.sh` greps all seven runtime scripts before it boots |
| 8 re-point the quests | **done** | every check reads a registry coordinate; a full run completes all 135 |
| 9 ship it | unchanged | `tools/scripts/release.sh` |
| 10 prove it end to end | **done** | `playthrough.sh` salts 20 player blocks, runs the whole story, then reads the region files with the server stopped |

**Step 5 changed shape.** The plan asked for a helper that writes into air *or into a block
matching a stored baseline*, throttled to 200 blocks a tick, with an overnight scheduler. The
baseline half turned out to be unnecessary and the throttle turned out to be unreachable: once
the world ships finished, no beat writes more than about a dozen blocks, so there is nothing to
throttle, and there is no baseline to compare against because there is no rebuild — the only
question a beat ever has to ask is "is this cell empty". That is `put()`. Its sibling `swap()`
handles the other half of the vocabulary the story actually needs: a fixture that is already
standing, changed to a different *state* of itself (a candle lit, a campfire lit, a lamp
burning), guarded by "the block that is there has to be the block I expect".

**Step 6 changed shape.** The plan had the cottage rebuilt from a kit over a night. It is
simpler than that now: the cottage is standing when the player arrives, cold and empty and with
no door on it, and Q3 hands her the door, the windows, the bed and the sconce for holes that
are already in the walls. Nothing is raised overnight because nothing needs raising. The one
thing she genuinely digs is the cellar — forty blocks of gravel in the kitchen floor over a
stone flight and a sealed iron door — and the one thing she genuinely mines is Tobin's fallen
adit into the Works, forty blocks of it.

**What the world gained on day one to make that true:** the cellar (`day1_cellar`), the adit
(`day1_adit`), the noticeboard and the Surveyor's Stake socket (`day1_board`), the whole
lakefront — basin, beach, pier, rails, rafts (`day1_lakefront`), and Wisp's four posts down the
frozen river (`day1_wisp_posts`). Every one of those was previously cut at runtime, in front of
the player, by a finale or a scene.
