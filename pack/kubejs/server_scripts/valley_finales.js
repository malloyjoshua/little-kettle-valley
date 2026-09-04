// =============================================================================
// valley_finales.js — Little Kettle Valley: the /valley command tree and the
// five finale chains.
//
// §12.2 P7 — finale idempotency. FTB Quests command rewards fire once per
// CLAIMING PLAYER, so no finale build ever lives in a reward. Every finale
// reward is exactly one command, `/valley finale actN`; this file checks a
// server.persistentData flag and returns silently if it is already set. That
// single guard is what makes the one-per-world rule in §9-C work.
//
// §12.2 P3 — there is no vanilla stage command, so `/valley stage` is here too.
//
// ---------------------------------------------------------------------------
// Corrections applied to the outline's finale.commands, all verified against
// the shipped jars. Do not revert these.
//
//  1. `sereneseasons setseason X`  ->  `season set X`
//     SereneSeasons 9.1.0.3 registers the ROOT literal `season`, then `set`,
//     then a SubSeason argument (sereneseasons/command/SeasonCommands.class,
//     CommandSetSeason.class). The sub-season enum values are unchanged.
//  2. `easy_npc preset import_new valley:<name> ...`
//     ->  `easy_npc preset import data <preset> <x> <y> <z>`
//     PresetImportCommand exposes import / import_new / import_with_owner and
//     REQUIRES a source literal (custom | data | default | local | world).
//     `import` reuses the preset's UUID, so re-running a finale cannot
//     duplicate a resident; `import_new` would.
//  3. `schedule function valley:actN/...` -> global.valley.delay(). We ship no
//     datapack functions; the delay queue in valley_core.js does the pacing.
//  4. `valley stage add world actN` -> handled in-process (still available as
//     a real command for quest command rewards).
//  5. `supplementaries:lantern_post` / `lantern_post_lit` DO NOT EXIST in this
//     mod list. A lamp post is minecraft:oak_fence with
//     createdeco:yellow_copper_lamp on top of it (valley_core.js
//     VALLEY.LAMP_POST / LAMP_BLOCK); the Act IV "everything lights at once"
//     moment re-sets every stored lamp into its lit state, from the Works
//     outward, one post per tick.
//     This used to be `candlelight:lamp` with a lantern dropped on top at
//     y+1. candlelight:lamp has no lit state — its blockstate carries only
//     `hanging` — so the forty lamps could not be turned on at all, and the
//     lantern the lever placed went one block ABOVE the lamp, in the air.
//  6. `~` offsets are resolved to ABSOLUTE coordinates here, because 1.20.1
//     has no macro functions and we are not shipping mcfunctions (§12.1 C6).
//  7. The Act II Float floats on water this file DIGS. Nothing at the Lake
//     Waystone is lake: finaleAct2's own fills level y-2..y-1 to stone across
//     29x29. And a `fill <pos> <pos> supplementaries:candle_holder` writes the
//     block's default state, which is lit=FALSE — the candle holders on the
//     pier are set one at a time with lit=true, standing on fence posts. The
//     basin is sealed by five `replace minecraft:water` plugs, so a lakeside
//     or coastal anchor cannot drain it.
// ---------------------------------------------------------------------------
// =============================================================================

const FIN_ACTS = ['act1', 'act2', 'act3', 'act4', 'act5']

// -----------------------------------------------------------------------------
// The lamp post, mirrored from valley_core.js VALLEY.LAMP_*. These are baked
// into the command arrays below at script load, before global.valley is
// guaranteed to exist, so they cannot be read off v.C there. Change both files.
//
//   POST      the fence the lamp stands on, at the offset's own y
//   LAMP_LIT  burning and staying burning (inverted=true beats shouldBeLit)
//   LAMP_DARK dark and staying dark, until the Act IV lever
// -----------------------------------------------------------------------------
// Every post below is written out as two literal setblock lines — the fence at
// ~1 and the lamp at ~2 — rather than built by a helper, because resolve() is
// the only thing in this file allowed to do arithmetic on a tilde.
const POST = 'minecraft:oak_fence'
const LAMP_LIT = 'createdeco:yellow_copper_lamp[facing=up,inverted=true,lit=true]'
const LAMP_DARK = 'createdeco:yellow_copper_lamp[facing=up,inverted=false,lit=false]'

// Easy NPC preset addressing. DataPresetDataFiles scans the folder constant
// "easy_npc/preset" in every namespace, so a preset shipped at
//   pack/kubejs/data/valley/easy_npc/preset/<name>.npc.snbt
// is addressed as valley:easy_npc/preset/<name>.npc.snbt.
// One constant, so a single edit fixes every finale if the NPC author lands
// the files somewhere else.
const PRESET_PREFIX = 'valley:easy_npc/preset/'
const PRESET_SUFFIX = '.npc.snbt'

function npc(name, x, y, z) {
  return 'easy_npc preset import data ' + PRESET_PREFIX + name + PRESET_SUFFIX +
         ' ' + x + ' ' + y + ' ' + z
}

// -----------------------------------------------------------------------------
// Tilde resolution. Every coordinate in the outline is written as a triple of
// tilde offsets from the segment's origin; nothing else in a command line
// starts with `~`, so a single regex pass is exact and leaves NBT and JSON
// untouched.
// -----------------------------------------------------------------------------
const TILDE3 = /(^|\s)~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)(?=[ ]|$)/g

function num(base, d) {
  let v = base + (d === '' || d === '-' ? 0 : parseFloat(d))
  return (v === Math.floor(v)) ? String(Math.floor(v)) : String(v)
}

function resolve(cmd, origin) {
  return cmd.replace(TILDE3, (m, lead, dx, dy, dz) =>
    lead + num(origin[0], dx) + ' ' + num(origin[1], dy) + ' ' + num(origin[2], dz))
}


// =============================================================================
// Build-time directives — the pad that knows what it is standing in.
//
// A line that begins with `@` is not a command. It is a job whose answer
// depends on the world the generator actually made, so plan_town.py cannot
// decide it and bake it into town_plan.js; it has to be decided here, with the
// level in hand, at the moment the group runs.
//
// There is one directive family: `@pad` and `@padfix`, the levelled pad under
// a building. Every pad in the valley used to end in
// `fill <rect> minecraft:grass_block`, which is why twelve plots read as hard
// green rectangles stamped into snow — a lawn with a straight edge, in a
// biome that has no lawns. `@pad` samples the ring three blocks outside the
// pad for the surface the terrain is actually made of, lays the pad's top
// course in THAT material, and feathers the outermost two rings: one in from
// the edge keeps the ground it already had half the time, the edge itself
// three times in four. A plot fades into the hillside instead of ending on a
// line, and where the sample says the site is under snow the feathered cells
// get their snow layer back on top.
//
// Two rules hold this together:
//   * the feather only ever touches the pad's two-block MARGIN, so the course
//     under a footprint is always solid, always level, always one material; and
//   * the scatter is a hash of the cell's own coordinates, never Math.random,
//     because `/valley finale actN force` has to lay the same pad down twice.
// =============================================================================
const PAD_FALLBACK = 'minecraft:grass_block'
const PAD_SAMPLE_RING = 3

// "Sky" for the purpose of finding the ground: air, and the things that stand
// on the ground rather than being it.
const PAD_SKY = {
  'minecraft:air': 1, 'minecraft:cave_air': 1, 'minecraft:void_air': 1,
  'minecraft:grass': 1, 'minecraft:tall_grass': 1, 'minecraft:fern': 1,
  'minecraft:large_fern': 1, 'minecraft:dead_bush': 1, 'minecraft:vine': 1,
  'minecraft:sugar_cane': 1, 'minecraft:sweet_berry_bush': 1, 'minecraft:seagrass': 1
}

// The only things a pad is allowed to be made of. Anything else the sampler
// finds — a road, an older pad, bare stone, water — is not a surface material
// and is ignored, so a plot beside the High Street does not come out cobbled.
const PAD_SURFACES = {
  'minecraft:grass_block': 1, 'minecraft:snow_block': 1, 'minecraft:podzol': 1,
  'minecraft:coarse_dirt': 1, 'minecraft:sand': 1, 'minecraft:red_sand': 1,
  'minecraft:dirt': 1, 'minecraft:rooted_dirt': 1, 'minecraft:moss_block': 1,
  'minecraft:mycelium': 1
}
// Deliberately NOT gravel. Gravel is a natural surface, but in this valley it
// is overwhelmingly the verge of a road: an Act III or Act V plot whose sample
// ring clips the East Lane would otherwise be paved in road verge and read as
// a car park. Street cells are excluded from the check in scratch/vt_check.py
// for the same reason.

const PAD_CACHE = {}
let padLevelWarned = false

function padLevel(server) {
  try { if (server.overworld) return server.overworld() } catch (err) { /* fall through */ }
  try { if (server.getLevel) return server.getLevel('minecraft:overworld') } catch (err) { /* fall through */ }
  return null
}

// Distance from (x,z) to the nearest edge of the rectangle. 0 is the edge ring,
// 1 the ring inside it; everything else is the solid core.
function padRing(x, z, x0, z0, x1, z1) {
  return Math.min(Math.min(x - x0, x1 - x), Math.min(z - z0, z1 - z))
}

// A stable 0..99 for a cell.
function padHash(x, z) {
  let h = (x * 73856093) ^ (z * 19349663)
  h = h ^ (h >>> 13)
  h = (h * 1274126177) & 0x7fffffff
  return h % 100
}

// The surface of one column: the top block that is not sky, foliage or
// treetop, and whether snow was lying on it. Starts 40 above the pad rather
// than at the build limit, because a pad is cut at the anchor's own height.
function padColumn(level, x, ytop, z) {
  let snow = false
  for (let y = ytop; y > ytop - 72; y--) {
    let id
    try { id = String(level.getBlock(x, y, z).id) } catch (err) { return null }
    if (id === 'minecraft:snow' || id === 'minecraft:powder_snow') { snow = true; continue }
    if (PAD_SKY[id]) continue
    if (id.indexOf('leaves') >= 0 || id.indexOf('_log') >= 0 ||
        id.indexOf('_wood') >= 0 || id.indexOf('mushroom_block') >= 0) continue
    return { id: id, snow: snow }
  }
  return null
}

// Sampled once per pad rectangle and cached, so `@padfix` puts back exactly
// the material `@pad` chose.
function padSample(server, x0, y, z0, x1, z1) {
  let key = x0 + ':' + y + ':' + z0 + ':' + x1 + ':' + z1
  if (PAD_CACHE[key]) return PAD_CACHE[key]
  let out = { mat: PAD_FALLBACK, snowy: false, native: {} }
  let level = padLevel(server)
  if (!level) {
    if (!padLevelWarned) {
      padLevelWarned = true
      console.warn('[valley] no overworld handle for the pad sampler; pads fall back to ' + PAD_FALLBACK)
    }
    PAD_CACHE[key] = out
    return out
  }
  let r = PAD_SAMPLE_RING
  let ax0 = x0 - r, az0 = z0 - r, ax1 = x1 + r, az1 = z1 + r
  let tally = {}, seen = 0, snowy = 0
  for (let x = ax0; x <= ax1; x++) {
    for (let z = az0; z <= az1; z++) {
      if (x !== ax0 && x !== ax1 && z !== az0 && z !== az1) continue
      let c = padColumn(level, x, y + 40, z)
      if (!c) continue
      seen++
      if (c.snow) snowy++
      if (PAD_SURFACES[c.id]) tally[c.id] = (tally[c.id] || 0) + 1
    }
  }
  let best = null, bn = 0
  for (let k in tally) { if (tally[k] > bn) { bn = tally[k]; best = k } }
  out.mat = best || PAD_FALLBACK
  out.snowy = (seen > 0 && snowy * 2 >= seen)
  // The ground each feathered cell already has, read BEFORE anything is
  // written into the pad. Read afterwards it would be the pad.
  for (let x = x0; x <= x1; x++) {
    for (let z = z0; z <= z1; z++) {
      if (padRing(x, z, x0, z0, x1, z1) > 1) continue
      let c = padColumn(level, x, y + 40, z)
      out.native[x + ',' + z] = (c && PAD_SURFACES[c.id]) ? c.id : out.mat
    }
  }
  PAD_CACHE[key] = out
  return out
}

function padApply(server, x0, y, z0, x1, z1, height, deep) {
  if (x0 > x1) { let t0 = x0; x0 = x1; x1 = t0 }
  if (z0 > z1) { let t1 = z0; z0 = z1; z1 = t1 }
  let s = padSample(server, x0, y, z0, x1, z1)
  server.runCommandSilent('fill ' + x0 + ' ' + (y + 1) + ' ' + z0 + ' ' +
                          x1 + ' ' + (y + height) + ' ' + z1 + ' minecraft:air')
  server.runCommandSilent('fill ' + x0 + ' ' + (y - deep) + ' ' + z0 + ' ' +
                          x1 + ' ' + (y - 2) + ' ' + z1 + ' minecraft:dirt')
  server.runCommandSilent('fill ' + x0 + ' ' + (y - 1) + ' ' + z0 + ' ' +
                          x1 + ' ' + (y - 1) + ' ' + z1 + ' minecraft:coarse_dirt')
  let cx0 = x0 + 2, cx1 = x1 - 2, cz0 = z0 + 2, cz1 = z1 - 2
  if (cx0 > cx1 || cz0 > cz1) {
    // too small to feather; a solid course is the safe answer
    server.runCommandSilent('fill ' + x0 + ' ' + y + ' ' + z0 + ' ' +
                            x1 + ' ' + y + ' ' + z1 + ' ' + s.mat)
    return
  }
  server.runCommandSilent('fill ' + cx0 + ' ' + y + ' ' + cz0 + ' ' +
                          cx1 + ' ' + y + ' ' + cz1 + ' ' + s.mat)
  for (let x = x0; x <= x1; x++) {
    for (let z = z0; z <= z1; z++) {
      let ring = padRing(x, z, x0, z0, x1, z1)
      if (ring > 1) continue
      // ring 1 is half the pad's own material, the edge ring a quarter of it
      let usePad = padHash(x, z) < (ring === 1 ? 50 : 25)
      let blk = usePad ? s.mat : (s.native[x + ',' + z] || s.mat)
      server.runCommandSilent('setblock ' + x + ' ' + y + ' ' + z + ' ' + blk)
      if (s.snowy && !usePad) {
        server.runCommandSilent('setblock ' + x + ' ' + (y + 1) + ' ' + z +
          ' minecraft:snow[layers=' + (1 + (padHash(x + 7, z - 3) % 3)) + ']')
      }
    }
  }
}

function padFix(server, x0, y, z0, x1, z1) {
  if (x0 > x1) { let t0 = x0; x0 = x1; x1 = t0 }
  if (z0 > z1) { let t1 = z0; z0 = z1; z1 = t1 }
  let s = padSample(server, x0, y, z0, x1, z1)
  server.runCommandSilent('fill ' + x0 + ' ' + y + ' ' + z0 + ' ' + x1 + ' ' + y + ' ' +
                          z1 + ' ' + s.mat + ' replace minecraft:air')
}

// `@pad x0 y z0 x1 y z1 <clear height> <dig depth> <fallback top>`
// `@padfix x0 y z0 x1 y z1 <fallback top>`
function runDirective(server, line) {
  let a = line.split(' ')
  if (a[0] === '@pad' && a.length >= 10) {
    padApply(server, parseInt(a[1]), parseInt(a[2]), parseInt(a[3]),
             parseInt(a[4]), parseInt(a[6]), parseInt(a[7]), parseInt(a[8]))
    return true
  }
  if (a[0] === '@padfix' && a.length >= 8) {
    padFix(server, parseInt(a[1]), parseInt(a[2]), parseInt(a[3]),
           parseInt(a[4]), parseInt(a[6]))
    return true
  }
  console.warn('[valley] unknown build directive, skipped: ' + line)
  return false
}

function runSeg(server, origin, cmds) {
  cmds.forEach(c => {
    if (!c || c.charAt(0) === '#') return
    let full = resolve(c, origin)
    if (full.charAt(0) === '@') { runDirective(server, full); return }
    try {
      let r = server.runCommandSilent(full)
      // A `fill ... replace <block>` returns the number of blocks it matched, so 0 means
      // "there was nothing of that block here" — which is the NORMAL answer for the
      // marker_cleanup() pass the town planner emits (it sweeps every plot in 4-wide
      // stripes looking for Towns-and-Towers' cyan_concrete street markers and jigsaw
      // blocks, and most stripes have none). Warning on those buried the signal: one
      // run logged 5047 of these, 3440 fills and 1563 setblocks, and a genuine failure
      // would have been one line in five thousand. The return code carries no
      // information for that form, so it is not reported for it.
      if (r === 0 && full.indexOf(' replace ') < 0) {
        console.warn('[valley] command returned 0 (no effect / failed): ' + full)
      }
    } catch (err) { console.error('[valley] finale command failed: ' + full + ' :: ' + err) }
  })
}

// =============================================================================
// Beats.
//
// Every finale is a chain of BEATS: one synchronous opening and then one or
// more v.delay() payoffs. The act used to be latched done in runFinale before
// the first beat ran, which meant a reload, a crash or a /stop anywhere inside
// a delay window burned the act permanently — the queue in valley_core.js is
// in memory and is cleared on load. Act III's delay(120) is the only thing
// that grants stage act4; Act IV's delay(80) is the lever, the lamp sweep and
// stages act5 + greenhouse_warm; Act IV's delay(200) is spring; Act V's last
// delay is the world border. Losing the act4 window also strands Q76 forever,
// because valley_checks.js gates it on hasWorldStage('act5').
//
// So: each beat carries its own world-level once() latch, and only the LAST
// beat of a chain calls markFinale. A re-run therefore skips what already
// happened and finishes what did not, and `/valley finale <act> force` is the
// backstop for an act that latched before this file changed.
// =============================================================================
// Opens a beat. false means it already ran in this world and the caller must
// return without doing anything.
function beat(v, act, n) {
  if (v.once('fin_' + act + '_b' + n)) return true
  console.info('[valley] finale ' + act + ' beat ' + n + ' already ran; skipped')
  return false
}

// Called at the END of a chain's LAST beat, and nowhere else. Latching the act
// and dropping its forceload are the same event, so an act that never finished
// keeps its chunks and an act that finished cannot leak them.
function endAct(v, act) {
  v.markFinale(act)
  let s = v.server()
  if (s) forceRelease(s, act)
  console.info('[valley] finale ' + act + ' complete')
}

// -----------------------------------------------------------------------------
// Forceload.
//
// Every command below runs as the SERVER, from 0 0 0, via runCommandSilent —
// so a setblock, fill or place into a chunk nobody is standing in is refused,
// and runSeg turns the whole refusal into a console warning. server.properties
// ships view-distance=8, and a finale card can be claimed from the Nether, the
// ridge, or a mineshaft. The result was an act that "ran", latched, and built
// nothing.
//
// The ground each act builds on is forceloaded before the chain starts and
// released after its last beat. FORCE_R is a radius in blocks around each mark
// the act touches; 40 covers every fill and template in that act, and the Act
// IV lamp sweep, whose furthest post is anchor + [24, 1, 26].
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// THE ARRIVAL BEAT.
//
// runFinale forceloads the act's ground and then calls the chain IN THE SAME
// TICK — and `forceload add` is ASYNCHRONOUS. The chunk is queued, not
// present. A `tp @e[tag=npc_marnie,limit=1]` issued before it lands matches
// NOTHING, because @e only ever sees loaded entities: the command returns 0,
// runSeg logs one warning nobody reads, and the whole town fails to turn up to
// its own festival. Measured on the pinned seed: with the twelve residents
// standing in the Works — whose chunks Act IV's own forceRelease let go of
// thirty seconds earlier — `execute if entity @e[tag=npc_halden]` matches
// nothing, and matches after a forceload plus three seconds.
//
// So every act is split. Beat 0 builds the ground; the people arrive in a beat
// of their own, two ticks later. And that beat does not trust one go: it
// counts the `tp @e[tag=npc_*]` lines that reported no effect and, if any did,
// runs the whole segment again a second later, up to ARRIVE_TRIES times. Two
// ticks is enough for a chunk already on the heap and is not enough for one
// coming off disk, and nothing in this file can know which it is looking at.
//
// Every command in an arrival segment is idempotent — an `easy_npc preset
// import` reuses the preset's own UUID (see correction 2 at the top of this
// file) and a tp is a tp — so a retry can never duplicate a resident.
//
// The beat's once() latch is taken on the FIRST attempt, like every other
// beat; the retries are in-memory. `done` runs after the last attempt, which
// is where the act's stage grant and endAct live, so the act is never latched
// complete before its people have had every chance to arrive.
// -----------------------------------------------------------------------------
const ARRIVE_FIRST = 2          // ticks after beat 0
const ARRIVE_GAP = 20           // ticks between retries
const ARRIVE_TRIES = 8

// Like runSeg, but returns how many RESIDENT TELEPORTS did nothing. Only tps
// are counted: a `fill` that finds the ground already the way it wants it also
// returns 0, and that is success, not a missing chunk.
function runSegArrive(server, origin, cmds) {
  let missed = 0
  cmds.forEach(c => {
    if (!c || c.charAt(0) === '#') return
    let full = resolve(c, origin)
    if (full.charAt(0) === '@') { runDirective(server, full); return }
    let counts = (full.indexOf('tp @e[tag=npc_') === 0)
    try {
      let r = server.runCommandSilent(full)
      if (r === 0) {
        if (counts) missed++
        else console.warn('[valley] command returned 0 (no effect / failed): ' + full)
      }
    } catch (err) {
      if (counts) missed++
      console.error('[valley] finale command failed: ' + full + ' :: ' + err)
    }
  })
  return missed
}

function arrival(v, act, run, done) {
  let tries = 0
  let step = s => {
    if (tries === 0 && !beat(v, act, '0n')) return
    tries++
    let missed = run(s)
    if (missed > 0 && tries < ARRIVE_TRIES) {
      console.info('[valley] ' + act + ' arrival: ' + missed +
                   ' resident(s) not in a loaded chunk yet; going round again (' +
                   tries + '/' + (ARRIVE_TRIES - 1) + ')')
      v.delay(ARRIVE_GAP, step)
      return
    }
    if (missed > 0) {
      console.warn('[valley] ' + act + ' arrival gave up with ' + missed +
                   ' resident(s) unmoved. /valley finale ' + act + ' force replays it.')
    }
    if (done) done(s)
  }
  v.delay(ARRIVE_FIRST, step)
}

const FORCE_R = 40

const FINALE_MARKS = {
  act1: ['anchor', 'lake'],
  act2: ['anchor', 'lake'],
  act3: ['anchor'],
  act4: ['anchor', 'works', 'inn', 'bathhouse'],
  act5: ['anchor']
}

// Comfortably past each chain's last beat: act3 turns at 120, act4 at 200,
// act5's fifth journal line at 100 + 5*100.
// act1 and act2 were 60 (three seconds). The arrival beat can now spend up to
// ARRIVE_FIRST + 7*ARRIVE_GAP = 142 ticks waiting for a chunk, and dropping
// the forceload out from under it mid-retry would be the same bug wearing a
// different hat.
const FINALE_RELEASE = { act1: 240, act2: 240, act3: 240, act4: 300, act5: 720 }

// Squared horizontal distance from a stored lamp to a mark. Used only to order
// the Act IV sweep, so the square root would be waste.
function lampSort(p, mark) {
  if (!mark) return 0
  let dx = p[0] - mark[0], dz = p[2] - mark[2]
  return dx * dx + dz * dz
}

function forceRegions(v, act) {
  let out = []
  let names = FINALE_MARKS[act] || ['anchor']
  names.forEach(name => {
    let p = name === 'anchor' ? v.anchor() : v.mark(name)
    if (p) out.push(p)
  })
  return out
}

function forceload(server, regions, op) {
  regions.forEach(p => {
    server.runCommandSilent('forceload ' + op + ' ' +
      (p[0] - FORCE_R) + ' ' + (p[2] - FORCE_R) + ' ' +
      (p[0] + FORCE_R) + ' ' + (p[2] + FORCE_R))
  })
}

// What each act is currently holding. Re-seeded by every runFinale, so a
// restart mid-act cannot orphan the release: the re-run that finishes the act
// is the thing that lets the chunks go.
const FORCE_HELD = {}

function forceHold(server, v, act) {
  let regions = forceRegions(v, act)
  FORCE_HELD[act] = regions
  forceload(server, regions, 'add')
  return regions
}

function forceRelease(server, act) {
  let regions = FORCE_HELD[act]
  if (!regions || regions.length === 0) return
  FORCE_HELD[act] = null
  forceload(server, regions, 'remove')
}

// -----------------------------------------------------------------------------
// The Works is a HOLE, and nothing in the pack was digging it.
//
// VALLEY.OFF.works is anchor + [34, -6, -20]: six blocks under the surface, in
// undisturbed stone. Act IV's opening beat tp's all eleven residents to
// works + [~0..~±4, ~1, ~2..~6] and its second beat setblocks the lever at
// works + [0, 2, 0] — every one of those coordinates was inside solid rock, so
// The Longest Night played with the whole town suffocating in the wall and the
// lever buried where nobody could see it. The only clear anywhere in the pack
// was SCENES.q65's `fill ... air replace minecraft:cobblestone`, and cobblestone
// does not generate naturally, so it cleared nothing.
//
// This digs the chamber: a stone-brick floor at ~-1, four blocks of headroom
// (~0..~3), and a stone-brick ceiling at ~4 so q65's five `lantern[hanging=true]`
// have something to hang from. It runs east/south to +8 so the stable pad q65
// lays at ~5..~7 and its saddled horse at ~6 ~1 ~6 are in the room too.
//
// It is latched once per world rather than filtered, because it has to be safe
// to call from BOTH ends: q65 normally opens the Works, but `/valley finale act4`
// on a world where q65 never played must still not entomb anybody — and an
// unfiltered re-fill at finale time would delete the lanterns, smithing table,
// barrel, hay and horse q65 put there. First caller digs; the other is a no-op.
// -----------------------------------------------------------------------------
// THE BOX HAD NO WALLS. The dig was a floor at ~-1, a ceiling at ~4 and an
// air fill between them — open on all four sides. Six blocks down, on an
// anchor anywhere near the lake, a river, an aquifer or a flooded cave, the
// surrounding stone is holding water back; the moment the air fill ran, that
// water flowed in and filled the room. Water washes a lever off its wall, so
// the Act IV finale set the lever, the water took it, and The Longest Night
// ended with the town standing in a flooded adit and nothing to pull.
//
// So the shell goes up FIRST — floor, ceiling and four one-block walls at the
// edge of the box — and only then is the interior inside that shell dug out.
// Nothing can flow in while the room is being cleared, because by then the
// room is already sealed.
//
// The box is unchanged from the outside (works + [-6..8] on x and z, ~-1
// floor, ~4 ceiling); the walls take the outer ring, so the ROOM is
// works + [-5..7, 0..3, -5..7]. Everything that lives in here still fits:
// q65's lanterns at [±4, 3, ±4], its stable pad at [5..7, 0, 5..7] and its
// horse at [6, 1, 6]; q66's cells and duct at [±2, 0, -4]; q71 and the Act IV
// finale's lever at [0, 2, 0]; and the eleven residents Act IV tp's to
// [0..±4, 1, 2..6].
const WORKS_SHELL = [
  // 1. Seal the box before a single block of stone is taken out of it.
  'fill ~-6 ~-1 ~-6 ~8 ~-1 ~8 minecraft:stone_bricks',
  'fill ~-6 ~4 ~-6 ~8 ~4 ~8 minecraft:stone_bricks',
  'fill ~-6 ~0 ~-6 ~-6 ~3 ~8 minecraft:stone_bricks',
  'fill ~8 ~0 ~-6 ~8 ~3 ~8 minecraft:stone_bricks',
  'fill ~-6 ~0 ~-6 ~8 ~3 ~-6 minecraft:stone_bricks',
  'fill ~-6 ~0 ~8 ~8 ~3 ~8 minecraft:stone_bricks',
  // 2. Now the room. Water first — a `replace minecraft:water` pass takes out
  //    source blocks and flowing blocks by state, before the general air fill
  //    gives anything left a fresh set of neighbours to spread into.
  'fill ~-5 ~0 ~-5 ~7 ~3 ~7 minecraft:air replace minecraft:water',
  'fill ~-5 ~0 ~-5 ~7 ~3 ~7 minecraft:air'
]

// The same water sweep on its own. Run AFTER a scene or a finale has put
// fixtures in the room: a lantern, a duct or a lever placed into a cell that
// still held water leaves that water behind it, and one more pass is cheaper
// than a drowned lever.
function dryWorks(server, v) {
  let works = v.mark('works')
  if (!works) return
  runSeg(server, works, ['fill ~-5 ~0 ~-5 ~7 ~3 ~7 minecraft:air replace minecraft:water'])
}

function excavateWorks(server, v) {
  if (!v.once('works_excavated')) return
  let works = v.mark('works')
  if (!works) { console.warn('[valley] excavateWorks: no "works" mark'); return }
  runSeg(server, works, WORKS_SHELL)
  // The room is a room now: Dungeons and Taverns bunker pieces, fitted INSIDE
  // the shell (the plan asserts every piece stays within works + [-6..8] on x
  // and z, so nothing breaches the seal), with the link corridor and the three
  // doorways cut afterwards. The shell fills are repeated at the end of that
  // group, so the seal survives whatever a bunker piece wrote at its edge.
  runGroup(server, v, 'act4_works')
  runSeg(server, works, ['fill ~-5 ~0 ~-5 ~7 ~3 ~7 minecraft:air replace minecraft:water'])
  console.info('[valley] Works chamber excavated, sealed and fitted out at ' + works.join(' '))
}


// -----------------------------------------------------------------------------
// THE TOWN PLAN.
//
// Every building in the valley is now a real structure template placed on a
// levelled pad, and both the pad and the placement are computed by
// tools/scripts/plan_town.py from the template's own measured footprint. That
// script writes town_plan.js, which KubeJS loads before this file, so the
// finales and the scenes below never carry a hand-typed building rectangle:
// they name a group and this runs it.
//
// A group also carries its own `bounds` - the bounding box of every `~` triple
// in it - because a finale runs as the SERVER from 0 0 0 and a fill into a
// chunk nobody is standing in is silently refused. FORCE_R around the mark is
// not enough any more: the town reaches 55 blocks east and 47 south.
// -----------------------------------------------------------------------------
function plan() {
  return (typeof global.valleyTownPlan !== 'undefined') ? global.valleyTownPlan : null
}

function groupOrigin(v, name) {
  if (name === 'anchor') return v.anchor()
  if (name === 'home') return v.home()
  return v.mark(name)
}

// A resident teleport: the one kind of command in a group or a scene that
// silently does nothing when its target is in a chunk the server has been told
// to load and has not loaded yet.
function isNpcTp(c) {
  return typeof c === 'string' && c.indexOf('tp @e[tag=npc_') === 0
}

// `arrive`, when given, is an array a caller collects deferred segments in:
// the group's resident teleports are pulled out and handed back instead of
// being run here, so the caller can retry them the way a finale does.
function runGroup(server, v, key, arrive) {
  let pl = plan()
  if (!pl || !pl.groups || !pl.groups[key]) {
    console.warn('[valley] town plan has no group "' + key + '" - nothing built')
    return false
  }
  let g = pl.groups[key]
  let origin = groupOrigin(v, g.origin)
  if (!origin) {
    console.warn('[valley] group "' + key + '" has no origin "' + g.origin + '" yet')
    return false
  }
  let b = g.bounds || [0, 0, 0, 0]
  let x0 = origin[0] + b[0] - 16, z0 = origin[2] + b[1] - 16
  let x1 = origin[0] + b[2] + 16, z1 = origin[2] + b[3] + 16
  server.runCommandSilent('forceload add ' + x0 + ' ' + z0 + ' ' + x1 + ' ' + z1)
  let cmds = g.cmds
  if (arrive) {
    let later = cmds.filter(isNpcTp)
    if (later.length) {
      cmds = cmds.filter(c => !isNpcTp(c))
      arrive.push({ origin: origin, cmds: later })
    }
  }
  try {
    runSeg(server, origin, cmds)
  } finally {
    v.delay(60, srv => srv.runCommandSilent('forceload remove ' + x0 + ' ' + z0 + ' ' + x1 + ' ' + z1))
  }
  console.info('[valley] built ' + key + ' (' + g.cmds.length + ' commands)')
  return true
}

// A plaza stand from the plan: a square cell that is not the well, a market
// cart, the supper table, the road or the noticeboard.
function stand(v, i) {
  let pl = plan()
  let list = (pl && pl.square && pl.square.stands) ? pl.square.stands : []
  return list.length ? list[i % list.length] : [0, 1, 0]
}

function seat(v, i) {
  let pl = plan()
  let list = (pl && pl.square && pl.square.supper_seats) ? pl.square.supper_seats : []
  return list.length ? list[i % list.length] : [0, 1, -8]
}

function at(p) { return '~' + p[0] + ' ~' + p[1] + ' ~' + p[2] }

// A works-relative floor cell inside the bunker rooms, spread out so eleven
// residents are not standing on each other. Read off the placed templates by
// tools/scripts/plan_town.py, never guessed.
function wstand(i) {
  let pl = plan()
  let list = (pl && pl.works && pl.works.stands) ? pl.works.stands : []
  if (!list.length) return [0, 1, 2]
  let step = Math.max(1, Math.floor(list.length / 12))
  return list[(i * step) % list.length]
}

function npcAt(name, p) { return npc(name, '~' + p[0], '~' + p[1], '~' + p[2]) }

function tpTo(tag, p) { return 'tp @e[tag=npc_' + tag + ',limit=1] ' + at(p) }

// -----------------------------------------------------------------------------
// The three scenes that stand ON the square: Q59's Ribbit camp, Q62's still and
// the Act III harvest.
//
// Their coordinates used to be typed into this file, next to a comment that
// described the square as it was two rewrites ago ("the four market carts (the
// +-11..+-7 corners)"). The planner then pulled the square's furniture inward
// and solved the carts to new cells - and the hand-typed scenes did not move
// with them. Cart 2 came to rest on x -10..-6, z 3..7, which is where the camp
// was: four Ribbits stood inside the fisher's cart, Sedge in its oak fence with
// a lit lantern in his head, and a lit campfire burned under its wooden canopy.
// Two of the four harvest props landed in carts as well.
//
// So the planner solves these cells too, against the well, the four carts, the
// supper table, the flower boxes, the bench garden, the streets and every
// whitelisted lamp post, and exports them as square.scenes. Nothing in this
// file knows where the carts are any more, which is the point.
// -----------------------------------------------------------------------------
const SQ_SCENE_FALLBACK = {
  ribbit_camp: { stands: [[-8, 1, 4], [-8, 1, 6], [-10, 1, 4], [-10, 1, 6]],
                 campfire: [-9, 1, 5], post: [-11, 1, 5] },
  still: { cupboard: [-9, 1, 7], brewing_stand: [-8, 1, 7], cauldron: [-7, 1, 7],
           post: [-8, 1, 6] },
  harvest: { hay: [[-6, 1, -6], [6, 1, -6]], pumpkins: [[-6, 1, 6], [6, 1, 6]] }
}

function sqScene(key) {
  let pl = plan()
  let sc = (pl && pl.square && pl.square.scenes) ? pl.square.scenes[key] : null
  if (sc) return sc
  console.warn('[valley] town_plan.js carries no square.scenes.' + key +
               ' - re-run tools/scripts/plan_town.py. Falling back to the ' +
               'pre-solve cells, which may be under a market cart.')
  return SQ_SCENE_FALLBACK[key]
}

// =============================================================================
// The five chains. Each is a list of segments; a segment names its origin mark
// (a key in VALLEY.OFF, or 'anchor') and its commands, with `~` offsets from
// that origin. Written out rather than read from outline.json so the six
// corrections above are visible in the file that runs them.
// =============================================================================
// -----------------------------------------------------------------------------
// THE ARRIVAL BEAT.
//
// runFinale forceloads the act's ground and then calls the chain IN THE SAME
// TICK. A chunk that has just been handed to `forceload add` is not in the
// world yet when the next command runs, so:
//
//   * `tp @e[tag=npc_marnie,limit=1] ...` matches NOTHING and returns 0 - the
//     entity it is looking for is in a chunk the server has been told to load
//     and has not loaded, so every resident stayed where the last act left
//     them and the festival was a party for the player alone; and
//   * `easy_npc preset import data ... x y z` into that same chunk drops its
//     NPC into a chunk that is about to be replaced by the one off disk.
//
// So every act is split: beat 0 builds the ground, and a second beat two ticks
// later brings the people to it. Two ticks, not one, because the forceload is
// processed at the end of the tick it was issued in and the chunk is there on
// the next. The arrival beat carries its own once() latch like any other, so a
// reload between the two finishes the half that never ran.
// -----------------------------------------------------------------------------
function finaleAct1(server, v) {
  if (beat(v, 'act1', 0)) {
  // The square, the six streets, the classic well and the four market carts
  // all come out of the town plan. The plaza is ONE clean rectangle now, not
  // the seven cut around the inn and the mill this used to need: the plan's
  // solver keeps every building outside x/z +-12 in the first place, so there
  // is nothing inside the square to cut around.
  runGroup(server, v, 'act1_square')
  runGroup(server, v, 'act1_streets')
  // The lamp pads clear the post cells themselves - on snowy highland the
  // whitelisted Q34/Q74 sites are powder snow over a slope - so they run once,
  // here, immediately before the first six posts go down. act1_streets does
  // NOT clear a post cell, which is what lets finaleAct2 re-lay the roads.
  runGroup(server, v, 'act1_lamp_pads')

  runSeg(server, v.anchor(), [
    'season set early_spring',
    'time set day',
    'weather clear',
    // Four posts on the square. With square_path's two that is the "six lamps
    // burning" the quest text promises and the 6 the bossbar reads, so these
    // are LIT - Act II's Oda counts exactly these six. Every post placed after
    // this one lands dark and waits for the lever. Fence at ~1, lamp at ~2.
    'setblock ~-12 ~1 ~0 ' + POST,
    'setblock ~-12 ~2 ~0 ' + LAMP_LIT,
    'setblock ~12 ~1 ~0 ' + POST,
    'setblock ~12 ~2 ~0 ' + LAMP_LIT,
    'setblock ~0 ~1 ~-12 ' + POST,
    'setblock ~0 ~2 ~-12 ' + LAMP_LIT,
    'setblock ~0 ~1 ~12 ' + POST,
    'setblock ~0 ~2 ~12 ' + LAMP_LIT,
    // ...and the OTHER two of the six: LAMPS_Q07, the pair
    // valley:act1/square_path put down at Q7. The plaza pad deletes them, so
    // they go back, LIT, after it. Same two coordinates as VALLEY.LAMPS_Q07.
    'setblock ~-2 ~1 ~8 ' + POST,
    'setblock ~-2 ~2 ~8 ' + LAMP_LIT,
    'setblock ~2 ~1 ~16 ' + POST,
    'setblock ~2 ~2 ~16 ' + LAMP_LIT,
    'bossbar set valley:lamps value 6',
    'bossbar set valley:folk value 5',
    'title @a times 15 70 25',
    'title @a subtitle {"text":"Spring, Year One.","color":"gray"}',
    'title @a title {"text":"The Thaw Fair","color":"gold"}',
    'playsound minecraft:block.bell.use master @a ~0 ~1 ~0 1 1',
    'loot give @a loot valley:rewards/fair_basket',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_2',
    'worldborder set 3000 10'
  ])
  }

  // The arrival beat.
  arrival(v, 'act1', s => runSegArrive(s, v.anchor(), [
    npcAt('marnie', stand(v, 0)),
    npcAt('bram', stand(v, 3)),
    npcAt('oda', stand(v, 6)),
    npcAt('pip', stand(v, 9)),
    // Halden lives at the hedge garden all through Act I (docs/NPCS.md), and
    // comes up to the square for the Fair.
    npcAt('halden', stand(v, 12)),
    'summon duckling:duck ' + at(stand(v, 10)) + ' {PersistenceRequired:1b,NoAI:1b}'
  ]), s => {
  // Q21 and Q27 both hang off this finale and both hand in a resident's token,
  // so Nella and Tobin arrive HERE, at the two places their own quest text
  // names, and not at the Act II finale sixteen quests later.
  runGroup(s, v, 'act1_tobin')
  runSeg(s, v.mark('lake'), [
    // Nella, at the beached boat. A small pad only - Act II's finale is what
    // builds the beach and the pier here.
    'fill ~-4 ~0 ~4 ~4 ~7 ~12 minecraft:air',
    'fill ~-4 ~-2 ~4 ~4 ~-2 ~12 minecraft:stone',
    'fill ~-4 ~-1 ~4 ~4 ~-1 ~12 minecraft:sand',
    'summon minecraft:boat ~1 ~0 ~7 {Type:"oak"}',
    'setblock ~-2 ~0 ~6 minecraft:oak_stairs[facing=east,half=bottom]',
    'setblock ~-2 ~0 ~7 minecraft:oak_stairs[facing=east,half=bottom]',
    'setblock ~-2 ~0 ~8 minecraft:oak_planks',
    'setblock ~-3 ~0 ~7 minecraft:campfire[lit=true]',
    'setblock ~3 ~0 ~9 minecraft:barrel[facing=up]',
    'setblock ~3 ~0 ~6 minecraft:oak_fence',
    'setblock ~3 ~1 ~6 minecraft:lantern[hanging=false]',
    npc('nella', '~0', '~0', '~8')
  ])
  v.sayAll('Tobin', "Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation.")
  // The act whose stated beat is "there is a door in your cellar you cannot
  // open" used to end on the rock joke. This sits inside the arrival beat's
  // second callback, which can run as late as tick 142 (ARRIVE_FIRST + 7 *
  // ARRIVE_GAP); 142 + 80 = 222 against FINALE_RELEASE.act1 = 240, and it is a
  // tellraw, so even overrunning the forceload costs nothing.
  v.delay(80, s2 => v.sayAll('Marnie',
    "That door in her cellar. You've found it, then. Everybody who has ever lived in that house has found it. Nobody has ever seen it open."))
  v.addWorldStage('act2')
  endAct(v, 'act1')
  })
}

function finaleAct2(server, v) {
  // Beat 0 builds the lakefront; beat '0n' brings the town down to it two
  // ticks later. See THE ARRIVAL BEAT above finaleAct1.
  if (beat(v, 'act2', 0)) {
  // Positioned at the Lake Waystone, not the anchor.
  runSeg(server, v.mark('lake'), [
    'season set mid_summer',
    'time set 18000',
    'weather clear',
    'fill ~-14 ~1 ~-14 ~14 ~10 ~14 minecraft:air',
    // TWO courses, not one. The beach below is laid into the same ~-1 layer as
    // the floor, so a single course meant the whole 13x11 patch was falling
    // sand with nothing under it — and Oda (~-2 ~1 ~6), Halden (~2 ~1 ~6) and
    // Nella (~0 ~1 ~9) are all tp'd onto it. The Float opened with three
    // residents dropping through the floor of their own festival.
    'fill ~-14 ~-2 ~-14 ~14 ~-1 ~14 minecraft:stone',
    // the shipped pier is 3 wide, so ~-1 centres it on the waystone axis
    'place template valley:pier ~-1 ~0 ~0',
    // sandstone, not sand: it reads the same from standing height and it is
    // not affected by gravity, so the beach cannot fall again if anything
    // later opens the course beneath it.
    'fill ~-6 ~-1 ~6 ~6 ~-1 ~16 minecraft:sandstone',
    // --- The Lantern Float has to float. ----------------------------------
    // What stood here: two fills of bare `supplementaries:candle_holder` at
    // x=±2, y=+2, z=2..18. Wrong three ways at once. A fill writes the
    // block's DEFAULT state and CandleHolderBlock's is lit=false, so all
    // thirty-four were unlit. x=±2 is off BOTH sides of the pier — the
    // template is 3x3x9 placed at ~-1, so its deck is x -1..1 — and y=+2 is
    // the rail course, one above the deck, so every one of them had air
    // underneath; a floor-mounted candle holder fails canSurvive there and
    // pops on the first neighbour update. And z ran to 18, ten blocks past
    // the end of a 9-long pier. Thirty-four unlit candlesticks hanging over
    // nothing, at a festival called the Lantern Float.
    //
    // There was also nothing to float ON. The two fills above level y-2..y-1
    // to stone across the whole 29x29 and clear y1..y10 to air, so the lake
    // at the Lake Waystone is a stone yard. The basin is DUG here rather than
    // trusted to the seed, and sealed rather than trusted to the water table:
    //
    //   1  stone shell, y-4..y-1, one block proud of the water on all four
    //      sides (x=±9, z=9, z=25) and under it (y-4).
    //   2  everything above cleared to y+8. This starts at z=10, and the two
    //      lines after it clear z=9 in halves — because finaleAct1 sets
    //      Nella's barrel at ~3 ~0 ~9 and a player may have put something in
    //      it between the two festivals.
    //   3  five 1-thick `replace minecraft:water` plugs, one per face of a
    //      box just outside the shell. They touch nothing but water, so on a
    //      dry anchor they are no-ops and on a lakeside or coastal one they
    //      are the reason the basin does not simply drain into the map.
    //   4  three courses of source water, top face at y+0 — flush with the
    //      beach, two below the pier deck, so the pier reads as a pier.
    //
    // This is also the only open water in the valley, which is what Q26's
    // Dredge Net looks for (valley_core.js dredgePull: water within two
    // blocks horizontally, dy +1..-4). The shore lip at z=9 is inside that.
    'fill ~-9 ~-4 ~9 ~9 ~-1 ~25 minecraft:stone',
    'fill ~-9 ~0 ~10 ~9 ~8 ~25 minecraft:air',
    'fill ~-9 ~0 ~9 ~2 ~0 ~9 minecraft:air',
    'fill ~4 ~0 ~9 ~9 ~0 ~9 minecraft:air',
    'fill ~-10 ~-5 ~8 ~-10 ~3 ~26 minecraft:stone replace minecraft:water',
    'fill ~10 ~-5 ~8 ~10 ~3 ~26 minecraft:stone replace minecraft:water',
    'fill ~-10 ~-5 ~8 ~10 ~3 ~8 minecraft:stone replace minecraft:water',
    'fill ~-10 ~-5 ~26 ~10 ~3 ~26 minecraft:stone replace minecraft:water',
    'fill ~-10 ~-5 ~8 ~10 ~-5 ~26 minecraft:stone replace minecraft:water',
    'fill ~-8 ~-3 ~10 ~8 ~-1 ~24 minecraft:water[level=0]',
    // the shore lip the shell just paved over, back in beach sandstone so the
    // water's edge reads as an edge and not as a kerb
    'fill ~-6 ~-1 ~9 ~6 ~-1 ~9 minecraft:sandstone',

    // Twelve rafts, each a lantern on a waterlogged TOP slab. A top slab's
    // upper face IS the block boundary, so it sits flush with the water and
    // still supports the lantern; a bottom slab's up-face shape is empty at
    // that boundary and the lantern would pop straight back off.
    'setblock ~-6 ~-1 ~13 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~-6 ~0 ~13 minecraft:lantern[hanging=false]',
    'setblock ~-2 ~-1 ~12 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~-2 ~0 ~12 minecraft:lantern[hanging=false]',
    'setblock ~2 ~-1 ~14 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~2 ~0 ~14 minecraft:lantern[hanging=false]',
    'setblock ~6 ~-1 ~12 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~6 ~0 ~12 minecraft:lantern[hanging=false]',
    'setblock ~-7 ~-1 ~18 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~-7 ~0 ~18 minecraft:lantern[hanging=false]',
    'setblock ~-3 ~-1 ~17 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~-3 ~0 ~17 minecraft:lantern[hanging=false]',
    'setblock ~1 ~-1 ~19 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~1 ~0 ~19 minecraft:lantern[hanging=false]',
    'setblock ~5 ~-1 ~17 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~5 ~0 ~17 minecraft:lantern[hanging=false]',
    'setblock ~-5 ~-1 ~22 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~-5 ~0 ~22 minecraft:lantern[hanging=false]',
    'setblock ~0 ~-1 ~23 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~0 ~0 ~23 minecraft:lantern[hanging=false]',
    'setblock ~4 ~-1 ~21 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~4 ~0 ~21 minecraft:lantern[hanging=false]',
    'setblock ~7 ~-1 ~23 minecraft:oak_slab[type=top,waterlogged=true]',
    'setblock ~7 ~0 ~23 minecraft:lantern[hanging=false]',
    // Three big pads and a scatter of small ones. Both are WaterlilyBlock:
    // they need a water SOURCE directly below and no fluid in their own
    // block, which is exactly y+0 over this basin.
    'setblock ~-8 ~0 ~15 ribbits:giant_lilypad',
    'setblock ~8 ~0 ~19 ribbits:giant_lilypad',
    'setblock ~-1 ~0 ~21 ribbits:giant_lilypad',
    'setblock ~-4 ~0 ~11 minecraft:lily_pad',
    'setblock ~0 ~0 ~11 minecraft:lily_pad',
    'setblock ~4 ~0 ~11 minecraft:lily_pad',
    'setblock ~-8 ~0 ~13 minecraft:lily_pad',
    'setblock ~8 ~0 ~14 minecraft:lily_pad',
    'setblock ~-5 ~0 ~16 minecraft:lily_pad',
    'setblock ~3 ~0 ~16 minecraft:lily_pad',
    'setblock ~-1 ~0 ~15 minecraft:lily_pad',
    'setblock ~6 ~0 ~20 minecraft:lily_pad',
    'setblock ~-7 ~0 ~21 minecraft:lily_pad',
    'setblock ~2 ~0 ~24 minecraft:lily_pad',
    'setblock ~-3 ~0 ~24 minecraft:lily_pad',

    // The pier template posts its rail only at z=0, 4 and 8, so six of the
    // deck's nine blocks are open on both long sides — with a basin under
    // them now, that is a two-block drop into cold water at a party. Close
    // the rail, then stand a LIT candle holder on every other post:
    // floor-mounted on a fence top, which does support it, at y+3 so the
    // walkway down the middle of the deck stays clear.
    'fill ~-1 ~2 ~1 ~-1 ~2 ~7 minecraft:oak_fence',
    'fill ~1 ~2 ~1 ~1 ~2 ~7 minecraft:oak_fence',
    'setblock ~-1 ~3 ~2 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~-1 ~3 ~4 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~-1 ~3 ~6 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~1 ~3 ~2 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~1 ~3 ~4 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~1 ~3 ~6 supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
    'setblock ~0 ~1 ~-2 waystones:waystone{WaystoneName:"The Pier"}',
    'bossbar set valley:lamps value 12',
    'title @a times 15 70 25',
    'title @a title {"text":"The Lantern Float","color":"aqua"}',
    'summon firework_rocket ~0 ~4 ~12 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1b,Colors:[I;16766720],FadeColors:[I;16777215]}]}}}}',
    'summon firework_rocket ~4 ~4 ~14 {LifeTime:22,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:4b,Colors:[I;3847130]}]}}}}',
    'playsound minecraft:entity.firework_rocket.launch master @a ~0 ~2 ~0 2 1',
    // the float itself, over the water: one drifting sheet of end_rod motes
    // above the lanterns. `force` so it renders regardless of the viewer's
    // particle setting.
    'particle minecraft:end_rod ~0 ~2 ~17 8 1 6 0.005 200 force @a',
    'give @a supplementaries:candle_holder 1',
    'give @a perfectplushies:frog_plushie 1',
    // the visible "the next tier is already in your hands" moment
    'give @a thermal:energy_cell 1',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_3',
    'worldborder set 6000 10'
  ])
  // The granary and the hedge garden. The granary is a real barn now
  // (Towns and Towers rustic barn) with twelve andesite alcoves marked out on
  // its own floor, so Q39 is still twelve drawers into twelve marked alcoves
  // and not a build; the hedge garden is the classic small farm.
  runGroup(server, v, 'act2_granary')
  runGroup(server, v, 'act2_garden')
  // The Float levels lake + [-14..14] to stone, which crosses the bottom of
  // the High Street and the last stretch of the Green Lane. Re-laying the
  // streets is idempotent (same fills, same paving) and is the only thing
  // that puts those two roads back over the new lakefront.
  runGroup(server, v, 'act1_streets')
  }

  // The arrival beat.
  arrival(v, 'act2', s => runSegArrive(s, v.mark('lake'), [
      // Nella already arrived with the Act I finale (Q21 needs her token).
      // This re-import is the same UUID, so it MOVES her to the Float rather
      // than duplicating her. Wisp arrives here for the first time. Both must
      // be imported BEFORE the /tp block below, or the tp selects nothing.
      npc('nella', '~0', '~1', '~8'),
      // Wisp used to arrive at ~-8 ~1 ~12 and Nella was tp'd to ~0 ~1 ~10.
      // Both are open water now, so both came to the Float by falling into it.
      // They stand on the sandstone shore lip at z=9 instead, at the water's
      // edge with the lanterns.
      npc('wisp', '~-5', '~1', '~9'),
      // residents are teleported, never pathed (§7 rule 4)
      'tp @e[tag=npc_marnie,limit=1] ~-2 ~1 ~4',
      'tp @e[tag=npc_bram,limit=1] ~2 ~1 ~4',
      'tp @e[tag=npc_oda,limit=1] ~-2 ~1 ~6',
      'tp @e[tag=npc_nella,limit=1] ~0 ~1 ~9',
      'tp @e[tag=npc_halden,limit=1] ~2 ~1 ~6',
      'tp @e[tag=npc_pip,limit=1] ~0 ~1 ~4'
    ]), s => {
    runSeg(s, v.anchor(), [
      // Tobin came down to the outcrop with the Act I finale (Q27 needs his
      // token). Same UUID, so this moves him into the square for the Float.
      npcAt('tobin', stand(v, 15))
    ])
    v.sayAll('Nella', 'You all came. Right.')
    // Act II is the act with no threat and no mystery in it, and it used to end
    // pointing at nothing. Entry 3 — unlocked in this same finale — closes on
    // "I bought a book about turbines", so she reads the page and then hears
    // the one person alive who was there flinch at it. Q54 pays it in Act III.
    // Pure tellraw, so endAct dropping the forceload on the next line is
    // irrelevant.
    v.delay(80, s2 => v.sayAll('Halden',
      "Josie stood on this pier the last summer she had and told me she'd bought a book about turbines. I laughed at her. I would very much like that back."))
    v.addWorldStage('act3')
    endAct(v, 'act2')
  })
}

function finaleAct3(server, v) {
  let HARVEST = sqScene('harvest')
  if (beat(v, 'act3', 0)) {
  // Oda's store and the bell tower open on the square, and the Supper table
  // is real Handcrafted furniture rather than a nine-block plank template.
  runGroup(server, v, 'act3_store')
  runGroup(server, v, 'act3_church')
  runGroup(server, v, 'act3_table')
  runSeg(server, v.anchor(), [
    'season set mid_autumn',
    'time set 13000',
    'weather clear',
    // The harvest itself: two bales and two lanterns-in-all-but-name, on the
    // four cells the planner solved for them (square.scenes.harvest). They
    // used to be the four (+-6, +-6) corners, and two of those corners are
    // inside market carts now.
    'setblock ' + at(HARVEST.hay[0]) + ' minecraft:hay_block',
    'setblock ' + at(HARVEST.hay[1]) + ' minecraft:hay_block',
    'setblock ' + at(HARVEST.pumpkins[0]) + ' minecraft:carved_pumpkin[facing=south]',
    'setblock ' + at(HARVEST.pumpkins[1]) + ' minecraft:carved_pumpkin[facing=south]',
    'place template valley:noticeboard ~0 ~1 ~-5',
    // The board template carries an oak_sign at its local [1,3,0]; writing it
    // here is the only place in the pack the destination line is actually
    // ON the noticeboard rule 3 says it is on.
    //
    // DATA MERGE, NOT SETBLOCK. valley:noticeboard has already placed
    // minecraft:oak_sign[rotation=8] at this exact position, and a /setblock
    // whose target block AND blockstate are identical to what is already there
    // is a no-op: 1.20.1's SetBlockCommand compares the new BlockState to the
    // old one, returns "Could not set the block" and NEVER applies the NBT tag
    // that came with it. The four lines were dropped on the floor every time,
    // and `data get block <pos> front_text` on a finished world came back with
    // four empty messages. `data merge block` writes the block entity that is
    // already standing there, so the destination line lands.
    'data merge block ~1 ~4 ~-5 {front_text:{messages:[\'{"text":"Forty lamps."}\',\'{"text":"Fifteen people."}\',\'{"text":"One winter that"}\',\'{"text":"nobody leaves."}\'],has_glowing_text:0b,color:"black"}}',
    'tellraw @a {"text":"On the noticeboard, in Oda\\u0027s hand: Forty lamps. Fifteen people. One winter that nobody leaves.","color":"gold"}',
    'bossbar set valley:lamps value 22',
    'bossbar set valley:folk value 11',
    'title @a times 20 90 30',
    'title @a title {"text":"The Harvest Supper","color":"gold"}',
    'loot give @a loot valley:rewards/harvest_gifts',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_4'
  ])
  }

  // The arrival beat: eleven people sitting down, two ticks after the table
  // and the chairs exist and the forceload has actually landed.
  arrival(v, 'act3', s => runSegArrive(s, v.anchor(), [
      // Wisp brings three more Ribbits; this is their first appearance, so
      // they are imported, and everyone else is /tp'd (§7 rule 4).
      npcAt('ribbit_reed', seat(v, 7)),
      npcAt('ribbit_sedge', seat(v, 8)),
      npcAt('ribbit_mudlark', seat(v, 9)),
      // Seated positions along the Harvest Supper table. act3_table lays real
      // Handcrafted tables and chairs at x -4..4, z -11..-9, so the seats are
      // the two rows outside each bench: z = -12 and z = -8. Twelve cells are
      // solved in plan_town.py against the lamps, the carts, the well and the
      // streets, and they are all DISTINCT - seat 2 used to be the north
      // corner lamp post and seat 10 (Wisp) used to wrap round onto seat 0.
      tpTo('marnie', seat(v, 5)),
      tpTo('bram', seat(v, 6)),
      tpTo('pip', seat(v, 0)),
      tpTo('halden', seat(v, 1)),
      tpTo('tobin', seat(v, 2)),
      tpTo('oda', seat(v, 3)),
      tpTo('nella', seat(v, 4)),
      tpTo('wisp', seat(v, 10)),
      'summon duckling:duck ~0 ~1 ~-13 {PersistenceRequired:1b,NoAI:1b}'
  ]))

  // The turn, six seconds later (§7: /schedule function valley:act3/turn 6s).
  // LAST BEAT: this is the only thing in the pack that grants stage act4, so
  // it is the thing act3 is latched on.
  v.delay(120, s => {
    if (!beat(v, 'act3', 1)) return
    runSeg(s, v.anchor(), [
      'season set early_winter',
      'weather rain',                                  // §12.1 C10: /weather snow does not exist
      'playsound minecraft:block.snow.place master @a ~0 ~1 ~0 1 0.6',
      'worldborder set 10000 10',
      'execute in minecraft:the_nether run worldborder set 1250 10'   // §12.1 C9: per dimension
    ])
    v.sayAll('Oda', "That's the last warm night. Let's not lose anybody this year.")
    v.addWorldStage('act4')
    endAct(v, 'act3')
  })
}

function finaleAct4(server, v) {
  if (beat(v, 'act4', 0)) {
    // Before a single tp: dig the room out. No-op if Q65 already opened it.
    excavateWorks(server, v)
    runSeg(server, v.mark('works'), [
      'season set mid_winter',
      'time set 18000',
      'weather rain',
      'title @a times 20 100 30',
      'title @a title {"text":"The Longest Night","color":"white"}',
      'playsound minecraft:block.bell.use master @a ~0 ~1 ~0 1 1.4'
    ])
    v.sayAll('Pip', 'I get to ring it. Marnie said. RING IT.')
  }

  // The arrival beat. The Works is six blocks under the north-east shoulder of
  // the town and nobody has ever stood in it, so its chunks are the coldest in
  // the act - which is exactly the case where a tp in the forceload's own tick
  // finds nothing at all.
  arrival(v, 'act4', s => runSegArrive(s, v.mark('works'), [
      // Eleven residents, on floor cells the plan read off the bunker rooms
      // themselves - works.stands. The old literal ~0..~+-4 ~1 ~2..~6 grid was
      // fine in an empty stone box and is not fine now there are walls in here.
      tpTo('bram', wstand(0)),
      // Puddle is the fourth Ribbit and arrives here (docs/NPCS.md).
      npcAt('ribbit_puddle', wstand(1)),
      tpTo('pip', wstand(2)),
      tpTo('marnie', wstand(3)),
      tpTo('oda', wstand(4)),
      tpTo('tobin', wstand(5)),
      tpTo('nella', wstand(6)),
      tpTo('halden', wstand(7)),
      tpTo('wisp', wstand(8)),
      tpTo('ribbit_reed', wstand(9)),
      tpTo('ribbit_sedge', wstand(10)),
      tpTo('ribbit_mudlark', wstand(11))
  ]))

  // Four seconds later, the instant. Bram pulls the lever: NPCs cannot
  // interact with blocks, so the lever is setblock and Bram is narration.
  v.delay(80, s => {
    if (!beat(v, 'act4', 1)) return
    let works = v.mark('works')
    // The chamber is sealed (see WORKS_SHELL), but the lever is the one block
    // in the pack that a single flowing water block deletes, and it is the
    // whole of this beat. Drain the room, place the panel and the lever, then
    // drain it again: a fixture set into a cell that still held water can
    // leave water behind it, and a lever with water in its cell is a lever
    // on the floor as an item.
    dryWorks(s, v)
    runSeg(s, works, [
      // A wall lever needs a wall. The chamber is open air now, so the panel
      // the lever hangs on is placed first or the lever pops off the next
      // time anything updates the block beside it.
      'setblock ~0 ~2 ~-1 minecraft:polished_andesite',
      'setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=true]',
      'particle minecraft:cloud ~2 ~3 ~2 1 1 1 0.02 60 force @a'
    ])
    dryWorks(s, v)

    // The world changes: every stored lamp post lights, nearest the Works
    // first, one post per tick, so from the doorway it reads as a wave going
    // down the road instead of forty blocks changing in the same frame.
    //
    // Each stored coordinate IS the lamp (valley_checks.js stores the lamp,
    // not the fence it stands on), so this sets the block in place — the old
    // `p[1] + 1` dropped a plain lantern in the air one block above a
    // candlelight lamp that had no lit state to begin with.
    let lamps = v.lamps().slice()
    lamps.sort((a, b) => lampSort(a, works) - lampSort(b, works))

    // THE FALSE START. The six nearest posts come up, hold, and go out again:
    // a cold coolant line, nothing more. Nobody is in danger, nothing can
    // fail, and no input is asked for. The point is two seconds of held
    // breath so Bram's "Well." lands on the far side of a silence. Tobin and
    // Bram both name it as mechanical hesitation before the player has time to
    // read it as a threat.
    lamps.slice(0, 6).forEach((p, i) => {
      v.delay(i * 2, srv => {
        srv.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_LIT)
        srv.runCommandSilent('playsound minecraft:block.copper.place master @a ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' 0.6 1.6')
      })
    })
    v.delay(16, srv => {
      lamps.slice(0, 6).forEach(p => srv.runCommandSilent(
        'setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_DARK))
      runSeg(srv, works, ['playsound minecraft:block.beacon.deactivate master @a ~0 ~1 ~0 2 0.8'])
      v.sayAll('Tobin', 'Cold line. That is all that is. It is only cold.')
    })
    v.delay(30, srv => v.sayAll('Bram', 'Give it a second.'))

    // Stage B, at +56: the real sweep, the two chords the lever used to play,
    // and the Hearth and the bathhouse, so the whole world turns on together.
    // Beat 2 is v.delay(200, ...) from finale start, i.e. 120 ticks after this
    // beat's own delay(80); +56 plus a sweep of at most 39 ticks ends by +95,
    // leaving 25 ticks of margin. valleyDelay schedules on global.valleyTick +
    // ticks, so a nested delay is relative to when it is called.
    v.delay(56, srv => {
      runSeg(srv, works, [
        'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 3 0.7',
        'playsound minecraft:block.conduit.activate master @a ~0 ~1 ~0 2 1'
      ])
      lamps.forEach((p, i) => {
        v.delay(i, s2 => {
          s2.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_LIT)
          s2.runCommandSilent('particle minecraft:end_rod ' + p[0] + ' ' + (p[1] + 1) + ' ' + p[2] + ' 0.2 0.2 0.2 0.01 8 force @a')
          s2.runCommandSilent('playsound minecraft:block.copper.place master @a ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' 0.6 1.6')
        })
      })
      srv.runCommandSilent('bossbar set valley:lamps value ' + Math.max(lamps.length, 39))
      // The Hearth relights, and the bathhouse starts steaming.
      let inn = v.mark('inn')
      if (inn) srv.runCommandSilent('setblock ' + inn[0] + ' ' + inn[1] + ' ' + inn[2] + ' minecraft:campfire[lit=true]')
      let bath = v.mark('bathhouse')
      if (bath) srv.runCommandSilent('particle minecraft:cloud ' + bath[0] + ' ' + (bath[1] + 2) + ' ' + bath[2] + ' 2 1 2 0.02 120 force @a')
    })

    // Q75 pays the Hearthkeeper's Lantern, the Plushie Token and 75 Scrip on
    // its own card, so the biggest build in the pack shows its payout before
    // the player claims it. This adds the town's own 25 on top.
    runSeg(s, works, [
      'summon firework_rocket ~0 ~6 ~0 {LifeTime:26,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;16766720,3847130],FadeColors:[I;16777215]}]}}}}',
      'summon firework_rocket ~-5 ~5 ~4 {LifeTime:32,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:4b,Colors:[I;16766720]}]}}}}',
      'summon firework_rocket ~5 ~5 ~-4 {LifeTime:38,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;3847130],FadeColors:[I;16766720]}]}}}}',
      'playsound minecraft:entity.firework_rocket.launch master @a ~0 ~2 ~0 3 1'
    ])
    s.runCommandSilent('give @a valley:scrip 25')
    s.runCommandSilent('advancement grant @a only valley:journal/entry_5')
    v.delay(62, srv => v.sayAll('Bram', 'Well.'))
    v.addWorldStage('greenhouse_warm')
    v.addWorldStage('act5')
  })

  // The turn, six seconds after the lever, the way Act III turns after the
  // Supper. Without this nothing sets spring until Q91 and the whole of Act V
  // — Nella's tomato, Marnie's walk round the square — plays in mid-winter.
  // LAST BEAT.
  v.delay(200, s => {
    if (!beat(v, 'act4', 2)) return
    runSeg(s, v.mark('works'), [
      'season set early_spring',
      'weather clear',
      'particle minecraft:falling_water ~0 ~5 ~0 8 3 8 0.01 160 force @a',
      'playsound minecraft:block.amethyst_block.chime master @a ~0 ~1 ~0 2 1.2'
    ])
    // Backstop for the sweep. The one-post-per-tick wave above is scheduled on
    // the in-memory queue, so a /stop two seconds after the lever would leave
    // the far end of the road dark with beat 1 already latched. This is the
    // same setblocks with no particles and no sound: by now they are either a
    // no-op or the only thing that lit those posts.
    v.lamps().forEach(p => {
      s.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_LIT)
    })
    v.sayAll('Marnie', "Snow's off the ridge by morning. It always turns the night after the longest one.")
    // Act V's premise is that people start arriving on their own, and its
    // finale walks Tess, Mab and Corin up the High Street with nothing in Act
    // IV pointing at them. Warm, not ominous: Oda names it as a traveller in
    // the same breath and ends on the kettle. Beat 2 fires at tick 200, so this
    // is 260 against FINALE_RELEASE.act4 = 300 — and it is a tellraw anyway.
    v.delay(60, s2 => v.sayAll('Oda',
      "There's a fire on the ridge road tonight. Three miles out, well off the tree line — somebody is walking in. Nobody has walked IN to this valley in eleven years. Put the kettle on."))
    endAct(v, 'act4')
  })
}

function finaleAct5(server, v) {
  if (beat(v, 'act5', 0)) {
  runGroup(server, v, 'act5_townhall')
  runGroup(server, v, 'act5_tess')
  runGroup(server, v, 'act5_mab')
  runGroup(server, v, 'act5_corin')
  runSeg(server, v.anchor(), [
    'season set early_spring',
    'time set noon',
    'weather clear',
    // The Town Hall and the three houses that will not be empty in spring are
    // real Towns and Towers meadow_swiss buildings on solved pads (see
    // town_plan.js); they are placed by the runGroup calls below this segment.
    // The signpost. Two fixes:
    //   * the valley is LITTLE KETTLE VALLEY. "COPPER KETTLE" was the working
    //     title and survived here alone; the ITEM valley:copper_kettle_trophy
    //     ("The Copper Kettle") and the Kettle family name are correct and stay.
    //   * air first, then the sign with its NBT. Nothing is meant to be
    //     standing at anchor + [0,1,-3], but if anything ever is - a re-run,
    //     a player's block, a stray fill - /setblock onto an identical
    //     blockstate silently drops the tag, exactly like the noticeboard did.
    'setblock ~0 ~1 ~-3 minecraft:air',
    'setblock ~0 ~1 ~-3 minecraft:oak_sign{front_text:{messages:[\'{"text":"LITTLE KETTLE"}\',\'{"text":"VALLEY"}\',\'{"text":"pop. 15"}\',\'{"text":"est. again"}\']}}',
    'bossbar set valley:lamps value 40',
    'bossbar set valley:folk value 15',
    'title @a times 20 110 40',
    'title @a subtitle {"text":"Spring, Year Two.","color":"gray"}',
    'title @a title {"text":"Founder\'s Day","color":"gold","bold":true}',
    'give @a valley:kettle_deed 1',
    'give @a valley:copper_kettle_trophy 1',
    'loot give @a loot valley:rewards/founders',
    'summon firework_rocket ~0 ~5 ~0 {LifeTime:25,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;16766720,3847130],FadeColors:[I;16777215]}]}}}}',
    'playsound minecraft:ui.toast.challenge_complete master @a ~0 ~1 ~0 2 1'
  ])
  }

  // The arrival beat. Act V lays four new pads before anyone moves, so this is
  // also the act where the forceload has the most work to do in the tick the
  // chain starts in.
  arrival(v, 'act5', s => runSegArrive(s, v.anchor(), [
      // three new arrivals, walking up the High Street the plan paved at Q19 -
      // a short approach, because long-distance pathing does not work (§12.3)
      npc('newcomer_tess', '~0', '~1', '~24'),
      npc('newcomer_mab', '~2', '~1', '~26'),
      npc('newcomer_corin', '~-2', '~1', '~26'),
      // The fifteen who already live here, on their Founder's Day marks - plaza
      // cells from the plan, so nobody is standing in the well.
      tpTo('halden', stand(v, 0)),
      tpTo('pip', stand(v, 2)),
      tpTo('marnie', stand(v, 4)),
      tpTo('bram', stand(v, 6)),
      tpTo('wisp', stand(v, 8)),
      tpTo('oda', stand(v, 10)),
      tpTo('nella', stand(v, 12)),
      tpTo('tobin', stand(v, 14)),
      tpTo('ribbit_reed', stand(v, 16)),
      tpTo('ribbit_sedge', stand(v, 18)),
      tpTo('ribbit_mudlark', stand(v, 20)),
      tpTo('ribbit_puddle', stand(v, 22))
  ]))

  // Halden reads the last page of Josie's journal: five lines, each five
  // seconds after the last. (§7: `function valley:act5/read1` .. read5.)
  //
  // These five lines ARE Entry 5 (journal/entry_5_the_last_page.json). What
  // used to be here was the Act III cellar wall read back word for word — text
  // the player read six hours earlier and which is already permanently in the
  // journal — and it closed the pack on "go and turn it on", an instruction to
  // do the thing she did in the previous act. Five lines in, five lines out,
  // so every beat(v,'act5', 1+i) index and the 1 + page.length final latch are
  // byte-identical. Line 4 lands on the bell Pip hung at q89; line 5 lands on
  // Tess, Mab and Corin, already standing on the road 24 blocks away.
  let page = [
    "Last one. The writing's gone shaky, so I'll be brief, which Marnie will tell you is a first.",
    "If the lights are on out there — if you're reading this warm, in the dark half of the year — then it worked, and it was not me who did it, and that is exactly right. I only ever got this valley to hold on. You got it to stay.",
    "So: the wheel goes counter-clockwise, the third lamp post leans and always has, and Marnie takes her tea far too strong.",
    "Don't turn this into a monument. Don't put my name on the square. Put a bell there, and ring it when supper's ready.",
    "And when somebody new comes up the road next spring — and they will, they always do when there's smoke — go out and meet them. Bring bread. Pretend you were passing."
  ]
  page.forEach((line, i) => {
    v.delay(100 + i * 100, s => {
      if (!beat(v, 'act5', 1 + i)) return
      v.sayAll('Halden', line)
    })
  })

  // LAST BEAT: the world border comes off here and nowhere else, so this is
  // the thing act5 is latched on. Thirty seconds after the card is claimed.
  v.delay(100 + page.length * 100, s => {
    if (!beat(v, 'act5', 1 + page.length)) return
    s.runCommandSilent('worldborder set 59999968')
    s.runCommandSilent('execute in minecraft:the_nether run worldborder set 59999968')
    s.runCommandSilent('tellraw @a ' + JSON.stringify({
      text: "The valley's fine now. Go see what's past the ridge — and come home for supper.",
      color: 'gold', italic: true
    }))
    v.addWorldStage('endless_seasons')
    endAct(v, 'act5')
  })
}

// =============================================================================
// /valley scene <key> — the Act IV set changes (§11 "every reward calls it").
//
// Twelve Act IV rewards call `/valley scene qNN`. There was no `scene`
// subcommand, so every one of them was a red error in the log and a quest that
// paid out with nothing visibly happening. Each key below is the smallest
// visible change the quest text actually promises, run at an anchor-relative
// mark, plus one line in the right resident's register.
//
// Rules, same as the finales:
//   * `origin` names a key in VALLEY.OFF (or 'anchor'); every command is a `~`
//     offset from it and resolve() turns those into absolute coordinates.
//   * `run` is for the two scenes that need runtime state (the lamp list).
//   * an unknown key is a friendly message, never an exception (§P3).
//   * scenes are NOT latched by default — a scene is a set change, and
//     re-running one just re-places the same blocks. Only finales are
//     once-per-world (§P7). A scene that puts a TEMPLATE down sets
//     `once: true`, because re-pasting a template over what the player has
//     since built in it is destructive, not idempotent.
// =============================================================================
const SCENES = {

  // Q8's reward — Marnie arrives at the door, Bram is down at the mill.
  //
  // Q12 ("Talk to Bram at the Broken Mill") consumes valley:token_bram; the
  // token's only source is Bram's ON_INTERACTION action in
  // data/valley/easy_npc/preset/bram.npc.snbt; and Bram's only import used to
  // be inside finaleAct1, which runs from Q19's reward — six quests past the
  // quest that needs him (Q19 <- Q17 <- Q16 <- Q14 <- Q13 <- Q12). Act I could
  // not be completed by anybody. He is imported here instead, at the mill plot
  // Q12's text sends the player to, and the mill race comes with him so Q16's
  // "the race is cut" is true when Q16 says it.
  //
  // Latched: it places valley:mill_race, and Q16 puts two Water Wheels in it.
  bram: {
    origin: 'mill',
    once: true,
    groups: ['act1_mill']
  },

  // Q8's other reward — the inn.
  //
  // Q8's payoff line is "Marnie moves in, the inn shell goes up at the Town
  // Anchor" and Q18 puts a Counter, a Sink and an Oven "on the three marked
  // spots along the inn's back wall". No inn was ever built: story-final.md
  // P8 lists inn_shell among the required structures and it was never made,
  // so Q18's three chalked spots existed on no wall in the world and the
  // Hearth that Act IV puts out and Q60 relights was a campfire in a field.
  //
  // Latched: Q18 sets three blocks down inside it and Q70a makes three beds
  // in it, and a second run would fill the room back in over both.
  inn: {
    origin: 'inn',
    once: true,
    groups: ['act1_inn']
  },

  // Q10's reward — the coop, built inside the pen the player has just fenced.
  //
  // cottage.mcfunction marks the pen out at home + [1..7, -1, -12..-6], so its
  // interior centre is home + [4, -1, -9] and that is where this positions the
  // nesting box. The reward used to be
  // `execute positioned {x} {y} {z} run function valley:act1/nesting_box` —
  // the CLAIMING PLAYER'S FEET — so Marnie's nesting box, her straw and her
  // two lamps were built wherever the card happened to be claimed from.
  coop: {
    origin: 'home',
    cmds: ['execute positioned ~4 ~-1 ~-9 run function valley:act1/nesting_box']
  },

  // ---------------------------------------------------------------------
  // Q5, Q7, Q8 and Q11 — the four Act I builds that used to run AT THE
  // CLAIMING PLAYER'S FEET.
  //
  // Every one of them was an FTB Quests command reward reading
  //   execute positioned {x} {y} {z} run function valley:act1/<name>
  // and CommandReward#claim substitutes {x} {y} {z} with the position of the
  // PLAYER WHO CLICKED THE CARD. A card can be claimed from the ridge, from
  // the Nether, from a mineshaft, from the inn — so:
  //
  //   * square_path.mcfunction, whose own header says "this function is
  //     invoked positioned at the anchor", laid the pad, the twenty-four
  //     block road and the first two lamp posts wherever the claim happened.
  //     valley_checks.js had already recorded those two lamps at
  //     anchor + LAMPS_Q07 the moment the stake went down, so the Act IV
  //     lever lit two posts that did not exist and left the two that did.
  //   * cellar_door.mcfunction built Josie's sealed iron door, her chalk and
  //     her tool chest in a 7x4x7 stone-brick box in mid-air, or inside a
  //     hill, or in the sea.
  //   * marnie_arrives and pip_arrives dropped two residents, a courier
  //     board, a barrel and two lamp posts in the same arbitrary spot.
  //
  // They are scenes now, each measured from a mark, and each latched
  // once:true — which is `v.once('scene_<key>')` with NO team argument, i.e.
  // world-level. That is deliberate and it is the rule for every shared town
  // structure in this file: the square, the cellar, the inn's neighbours and
  // the road are built once per WORLD. A per-team latch would build a second
  // road through the first one the moment a second team claimed the card.
  // ---------------------------------------------------------------------

  // Q7's reward. AT THE ANCHOR, which is the only position this function has
  // ever been correct at: it is the stake, the pad around it, the road south
  // and LAMPS_Q07's two posts.
  square_path: {
    origin: 'anchor',
    once: true,
    cmds: ['execute positioned ~0 ~0 ~0 run function valley:act1/square_path']
  },

  // Q5's reward — the cellar under the Kettle hearthstone.
  //
  // Two things make this one different from every other scene here.
  //
  // 1. NO ANCHOR YET. Q5 is two quests before Q7, so the Surveyor's Stake has
  //    not been driven and v.anchor() is null. runScene refuses a scene with
  //    no anchor because a scene has nothing to measure from — but this one
  //    measures from the HOUSE, not the town, so it carries noAnchor.
  // 2. DEPTH. The function builds a 7x4x7 room whose shell runs from its
  //    origin's y-1 to y+3, with the walkable floor at y-1 and the air at
  //    y..y+2. Home is the Homestead Waystone block (valley_checks.js sets it
  //    where the player places it, on the ruin hearthstone), the cottage's
  //    plank floor is home.y-1 and its cobblestone subfloor is home.y-2. So
  //    the origin is home + [0,-6,0]: the room's stone-brick ceiling lands at
  //    home.y-3, directly under that subfloor, and a player standing on the
  //    cellar floor has their feet at home.y-6 — which satisfies BOTH gates
  //    valley_checks.js puts on this room, Q5's `y <= home.y + HOME_CELLAR_Y`
  //    (-3) and Q55's `y <= home.y + HOME_DEEP_Y` (-6).
  cellar: {
    origin: 'home',
    once: true,
    noAnchor: true,
    // Home is set by Q2. If a world somehow reaches Q5 without it, fall back
    // to the ruin hearthstone placeRuin() dropped at first join, and only
    // then to the claiming player — the old behaviour, but said out loud in
    // the log instead of happening silently every single time.
    fallback: function (v, source) {
      let r = v.ruin()
      if (r) {
        console.warn('[valley] scene cellar: no Home set; building under the Kettle ruin hearthstone at ' + r.join(' '))
        return r
      }
      let p = srcPlayer(source)
      if (p) {
        let q = [Math.floor(p.x), Math.floor(p.y), Math.floor(p.z)]
        console.warn('[valley] scene cellar: no Home and no ruin hearthstone. ' +
                     'Building at the claiming player, ' + q.join(' ') + ' — the cellar will be wherever this card was clicked.')
        return q
      }
      return null
    },
    cmds: ['execute positioned ~0 ~-6 ~0 run function valley:act1/cellar_door']
  },

  // Q8's third reward — Marnie arrives. AT THE INN, which is the building
  // Q8's own payoff line says she moves into.
  //
  // The inn mark is the Hearth: the floor is inn.y-1 and everything stands at
  // inn.y, so the function (which expects to be positioned at ground level,
  // the way a player's feet are) is run at inn + [0,-1,0]. Its own footprint
  // is then anchor + [-10..-6, 0..2, 18..20] — three blocks clear of the inn's
  // south eave (z 17) and, more importantly, OUTSIDE every rectangle the Act I
  // finale bulldozes eleven quests later. That finale air-fills y 1..14 over
  // z <= 6, over z = 18, and over z 7..17 either side of the inn; the only
  // ground near the inn that survives it is z >= 19, which is exactly where
  // Marnie's post, her barrel and her table stand. The pad row at z = 18 is
  // at y 0 and is simply repaved in the same cobblestone.
  //
  // The three fills are §7 rule 2 — subgrade, clear, then build — because
  // this is the first thing ever built south of the inn and nothing else has
  // levelled that strip.
  marnie: {
    origin: 'anchor',
    once: true,
    groups: ['act1_marnie']
  },

  // Q11's reward - Pip moves in, with the duck. His own meadow_swiss chalet,
  // next door to his aunt, on its own solved pad. Same rule as marnie above:
  // the group is anchor-relative and the plan guarantees the pad clears every
  // other building, every street and every whitelisted lamp post.
  pip: {
    origin: 'anchor',
    once: true,
    groups: ['act1_pip']
  },

  // Q58 — the four firewood stacks. Wisp lights a lantern path down the
  // frozen river, which is the first thing that happens after the Hearth
  // goes out and the only light between the town and the reed village.
  q58: {
    origin: 'anchor',
    who: ['Wisp', 'Warm inn. Warm soup. I light the way, you walk it. That is a fair trade.'],
    cmds: [
      // Four posts down the frozen river, lit on the spot — this is Wisp
      // lighting the way, so they do not wait for the lever. They are not on
      // any LAMPS_* route, so they never enter the count. The lanterns that
      // used to sit at ~2 are gone: ~2 is where the lamp itself now goes.
      'setblock ~2 ~1 ~14 ' + POST,
      'setblock ~2 ~2 ~14 ' + LAMP_LIT,
      'setblock ~-2 ~1 ~20 ' + POST,
      'setblock ~-2 ~2 ~20 ' + LAMP_LIT,
      'setblock ~2 ~1 ~26 ' + POST,
      'setblock ~2 ~2 ~26 ' + LAMP_LIT,
      'setblock ~-2 ~1 ~32 ' + POST,
      'setblock ~-2 ~2 ~32 ' + LAMP_LIT,
      'particle minecraft:end_rod ~0 ~3 ~24 1 1 8 0.01 80 force @a',
      'playsound minecraft:block.amethyst_block.chime master @a ~0 ~1 ~0 2 1.2'
    ]
  },

  // Q59 — the reed village comes in. Four Ribbits move into town for good;
  // Puddle's first appearance is here rather than at the Act IV finale, which
  // re-imports the same UUID and therefore just moves him.
  q59: {
    origin: 'anchor',
    who: ['Wisp', 'The reeds is all ice now, and we are eleven with no roof. Can we be your neighbours nearer?'],
    // On the square's own paving. The camp used to stand at anchor x -13..-10,
    // which is outside the plaza and therefore on raw terrain - four Ribbits
    // and a campfire in a hedge - and then at x -10..-8, which a market cart
    // was solved on top of. The cells come from square.scenes.ribbit_camp now:
    // four stands, a fire between them and the lamp post at the end.
    cmds: function () {
      let c = sqScene('ribbit_camp')
      let out = []
      let who = ['ribbit_reed', 'ribbit_sedge', 'ribbit_mudlark', 'ribbit_puddle']
      who.forEach((n, i) => out.push(npcAt(n, c.stands[i % c.stands.length])))
      out.push('setblock ' + at(c.campfire) + ' minecraft:campfire[lit=true]')
      out.push('setblock ' + at(c.post) + ' ' + POST)
      out.push('setblock ' + at([c.post[0], c.post[1] + 1, c.post[2]]) + ' ' + LAMP_LIT)
      // Eight named + four Ribbits = twelve. The last three are the Act V
      // arrivals, and the bar does not count the player.
      out.push('bossbar set valley:folk value 12')
      out.push('playsound minecraft:entity.frog.long_jump master @a ~0 ~1 ~0 1 1')
      return out
    }
  },

  // Q60 — soup for a full room. The Hearth relights, and the greenhouse SHELL
  // goes up on the square: six empty window frames, a doorway and a bare
  // bench. Q64 is what glazes it.
  q60: {
    origin: 'anchor',
    who: ['Marnie', "I have fed this room for thirty years, and tonight I'm sitting down at it. Don't make a thing of it."],
    // The greenhouse is a real building on a levelled pad now: spruce frame,
    // six empty window openings, a doorway, a rafter roof and a planting bench
    // down the middle. Q64 is what glazes it.
    groups: ['act4_greenhouse_shell'],
    also: {
      origin: 'inn',
      cmds: [
        // the Hearth relights - the whole point of the quest. `inn` is the
        // tavern's own campfire, so this is the fire in the middle of the room.
        'setblock ~0 ~0 ~0 minecraft:campfire[lit=true]',
        'particle minecraft:campfire_cosy_smoke ~0 ~2 ~0 0.3 0.3 0.3 0.01 40 force @a',
        'playsound minecraft:block.campfire.crackle master @a ~0 ~1 ~0 2 1'
      ]
    }
  },

  // Q62 — Halden's rounds. Eight tonics, eight houses, nobody gets sick.
  q62: {
    origin: 'anchor',
    who: ['Halden', 'Eight people, eight bottles. I would go round myself, but they talk to you more than they talk to me.'],
    // THE STILL USED TO BE INSIDE BRAM'S MILL, and then on raw terrain west of
    // the old square. It stands on the square's own paving now - but not on
    // paving this file picks. The comment that used to live here described a
    // square that no longer exists ("the well (x 2..7, z -3..2), the four
    // market carts (the +-11..+-7 corners)"): both were re-solved inward, the
    // still's three cells ended up inside the fisher's cart, and nothing in
    // this file could have known. square.scenes.still is solved against the
    // square as it actually is, every time the planner runs.
    cmds: function () {
      let c = sqScene('still')
      return [
        'setblock ' + at(c.cupboard) + ' handcrafted:oak_cupboard',
        'setblock ' + at(c.brewing_stand) + ' minecraft:brewing_stand',
        'setblock ' + at(c.cauldron) + ' minecraft:water_cauldron[level=3]',
        // The lantern used to sit directly on top of the brewing stand, which
        // has no sturdy top face to hang a lantern from. It stands on its own
        // fence post instead, the same post-and-light the rest of the pack uses.
        'setblock ' + at(c.post) + ' minecraft:oak_fence',
        'setblock ' + at([c.post[0], c.post[1] + 1, c.post[2]]) + ' minecraft:lantern[hanging=false]',
        'effect give @a minecraft:regeneration 20 0 true',
        'particle minecraft:happy_villager ~0 ~2 ~0 6 2 6 0.01 120 force @a',
        'playsound minecraft:block.brewing_stand.brew master @a ~0 ~1 ~0 2 1'
      ]
    }
  },

  // Q64 — the cold frame. Six windows, a door, eight planters on the bench.
  q64: {
    origin: 'anchor',
    who: ['Nella', "Nothing grows in it yet. I'll sit in it anyway - it's the only quiet room in town."],
    // Six windows into the six openings the shell left, the cottage door, the
    // glass roof and the planters on the bench. All computed against the shell
    // the plan actually built, so a window can never land in a wall.
    groups: ['act4_greenhouse_glaze']
  },

  // Q65 — open the Works. The interior lights, and there is a saddled horse
  // in the stable (the quest's reward line, made literally true).
  q65: {
    origin: 'works',
    // The chamber itself. This used to be a `fill ... air replace
    // minecraft:cobblestone` in the cmds below, which cleared nothing, because
    // the Works is six blocks down in natural stone and cobblestone does not
    // generate. Everything below this line decorates a room that now exists.
    pre: excavateWorks,
    who: ['Tobin', 'Forty blocks of fallen adit, I paced it twice, and behind forty blocks is the entire works, and I have not slept.'],
    // The five hanging lanterns moved off works + [+-4, 3, +-4]: x = +-4 is
    // now the bunker hall's own east wall, and a lantern setblock there would
    // punch a hole through it. The plan picks ceiling cells inside the room
    // (works.lanterns) and act4_works_light places them.
    groups: ['act4_works_light'],
    cmds: [
      'setblock ~-3 ~0 ~-3 minecraft:smithing_table',
      'setblock ~3 ~0 ~-3 minecraft:barrel[facing=up]',
      'setblock ~0 ~0 ~-5 minecraft:polished_andesite',
      'fill ~5 ~0 ~5 ~7 ~0 ~7 minecraft:hay_block',
      'summon minecraft:horse ~6 ~1 ~6 {Tame:1b,PersistenceRequired:1b,SaddleItem:{id:"minecraft:saddle",Count:1b}}',
      'playsound minecraft:block.beacon.power_select master @a ~0 ~1 ~0 2 0.8'
    ],
    // One more water sweep, after the fixtures. runScene calls `run` last.
    run: dryWorks
  },

  // Q66 — the grid. Duct from the mill to the Works, two cells at this end.
  q66: {
    origin: 'works',
    // Q66's cells and duct sit at works + [~±2, ~0, ~-4]; if a player somehow
    // reaches the grid before the Works is opened, they go in rock too.
    pre: excavateWorks,
    who: ['Bram', "Mill makes it, Works needs it, duct in between. That's the whole job."],
    cmds: [
      'setblock ~-2 ~0 ~-4 thermal:energy_cell',
      'setblock ~2 ~0 ~-4 thermal:energy_cell',
      'fill ~-1 ~0 ~-4 ~1 ~0 ~-4 thermal:energy_duct',
      'setblock ~0 ~1 ~-4 minecraft:redstone_lamp[lit=true]',
      'particle minecraft:electric_spark ~0 ~1 ~-4 0.6 0.6 0.6 0.02 60 force @a',
      'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 1 1.4'
    ],
    run: dryWorks
  },

  // Q70a — the wool line. Three blankets, three beds, three empty houses
  // that will not be empty in spring: Tess, Mab and Corin arrive in Act V.
  q70a: {
    origin: 'anchor',
    who: ['Marnie', 'Three empty houses, three beds, three blankets. People arrive in spring, and beds should be made before they get here.'],
    // Three beds in the inn's common room. The old ~-3 ~0 ~-3..~2 row was
    // measured against a 9x9 plank box that no longer exists; the plan pairs
    // adjacent floor cells it read off the tavern piece itself, so the beds
    // are on the floor, indoors, and clear of Q18's three chalked spots.
    groups: ['act4_beds']
  },

  // Q76 — year two. Oda rewrites the noticeboard, and the destination line
  // stays word for word, because rule 3 says it is never paraphrased.
  q76: {
    origin: 'anchor',
    who: ['Oda', "Year two on the board, and it is a longer list than last spring. I have written the bottom four lines out exactly as they were."],
    cmds: [
      // Same trap as finaleAct3, same fix: the sign is already standing on
      // the noticeboard in this exact blockstate, so /setblock refuses and
      // throws the NBT away. Write the block entity instead.
      'data merge block ~1 ~4 ~-5 {front_text:{messages:[\'{"text":"Forty lamps."}\',\'{"text":"Fifteen people."}\',\'{"text":"One winter that"}\',\'{"text":"nobody leaves."}\'],has_glowing_text:0b,color:"black"}}',
      'tellraw @a {"text":"On the noticeboard, in Oda\\u0027s hand: Forty lamps. Fifteen people. One winter that nobody leaves.","color":"gold"}',
      'playsound minecraft:block.wood.place master @a ~0 ~1 ~-5 1 1.2'
    ]
  },

  // Q71 — the turbine holds 1,800 RPM. The lever goes live: it is placed
  // UNPOWERED here, because pulling it is the Act IV finale.
  q71: {
    origin: 'works',
    // Same room, same lever cell as the Act IV finale — so the same two
    // guards. `pre` digs and seals the chamber if q65 has not (latched, so
    // it is a no-op when it has), and the andesite panel at ~0 ~2 ~-1 is the
    // wall a `face=wall` lever hangs on: without it the lever has no support
    // and pops off as an item the first time a neighbour updates.
    pre: excavateWorks,
    who: ['Bram', "Crate's got what it's got - blades, coils, casing. Eighteen hundred RPM under load, and hold it there."],
    cmds: [
      'setblock ~0 ~1 ~0 minecraft:polished_andesite',
      'setblock ~0 ~2 ~-1 minecraft:polished_andesite',
      'setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=false]',
      'setblock ~-1 ~2 ~0 minecraft:copper_block',
      'setblock ~1 ~2 ~0 minecraft:copper_block',
      'setblock ~0 ~3 ~0 minecraft:oak_wall_sign[facing=south]{front_text:{messages:[\'{"text":"1800 RPM"}\',\'{"text":"under load"}\',\'{"text":"- J.K."}\',\'{"text":""}\']}}',
      'playsound minecraft:block.note_block.bit master @a ~0 ~1 ~0 2 1.6'
    ],
    run: dryWorks
  },

  // Q72 — the coolant loop. Josie's rule: the waste heat goes to the town.
  // Six heaters under the greenhouse, and the bathhouse starts steaming.
  q72: {
    origin: 'anchor',
    who: ['Josie', 'The waste heat goes to the town, not the sky. Anything else is a fire you paid for twice.'],
    // Six magma heaters and the fluid duct under the greenhouse bench, and the
    // bathhouse itself: a real stone-and-spruce building with a sunken tank,
    // a roof and two lamps, instead of a bare pool of water in a field.
    groups: ['act4_greenhouse_heat', 'act4_bathhouse'],
    cmds: [
      'particle minecraft:cloud ~0 ~2 ~0 3 1 2 0.01 120 force @a',
      'playsound minecraft:block.lava.ambient master @a ~0 ~1 ~0 1 1.4'
    ]
  },

  // Q73 — bring Bram. He says no. You bring him anyway.
  q73: {
    origin: 'anchor',
    who: ['Bram', "The mill needs me at midnight in January, is the thing. ... Fine. One cocoa."],
    // Bram, a chair and a table, on floor cells inside the tavern's common
    // room - not on the ~1 layer of air the old inn-relative offsets used.
    groups: ['act4_bram_chair']
  },

  // Q74 — the second stretch. Runs the duct along every post already stored
  // in persistentData.lamps[], which is why this one is a `run` and not a
  // command list: the coordinates only exist at runtime.
  q74: {
    origin: 'anchor',
    // `home` asks runScene to forceload the homestead too: the bare fortieth
    // post goes down at home + HOME_PORCH, which is nowhere near the anchor.
    home: true,
    who: ['Josie', 'Forty posts, mill to square to lake. I counted them on my fingers before I could count to forty.'],
    // Q74 opens in mid-winter. The seventeen whitelisted sites have had three
    // months of snow on them and neither snow_block nor powder_snow can be
    // replaced by placing a post, so the scene sweeps them clear first.
    groups: ['act4_lamp_sweep'],
    run: function (server, v) {
      let lamps = v.lamps()
      lamps.forEach(p => {
        // p IS the lamp, so the spark sits one block over its head.
        server.runCommandSilent('particle minecraft:end_rod ' +
          p[0] + ' ' + (p[1] + 1) + ' ' + p[2] + ' 0.2 0.4 0.2 0.01 6 force @a')
      })
      server.runCommandSilent('bossbar set valley:lamps value ' + Math.min(Math.max(lamps.length, 39), 40))
      let home = v.home()
      if (home) {
        // the fortieth post stays bare on purpose: Josie's porch, Q90.
        server.runCommandSilent('setblock ' +
          (home[0] + v.C.HOME_PORCH[0]) + ' ' +
          (home[1] + v.C.HOME_PORCH[1]) + ' ' +
          (home[2] + v.C.HOME_PORCH[2]) + ' minecraft:oak_fence')
      }
      server.runCommandSilent('playsound minecraft:block.chain.place master @a ~ ~ ~ 1 1')
    }
  }
}

// A scene's origin. 'anchor' is the Town Anchor, 'home' is the Homestead
// waystone on the Kettle hearthstone (Q2) — the only two fixed points that are
// not anchor offsets — and anything else is a key in VALLEY.OFF. 'home' exists
// so `coop` can build inside the pen cottage.mcfunction marked out behind the
// house without measuring from the claiming player's feet.
function originPos(v, name) {
  if (name === 'anchor') return v.anchor()
  if (name === 'home') return v.home()
  return v.mark(name)
}

// Where a scene actually builds. Normally that is its own mark; a scene that
// can legitimately run before its mark exists carries a `fallback(v, source)`
// which returns a position or null. SCENES.cellar is the only one: Q5 is two
// quests before the Surveyor's Stake.
function sceneOrigin(v, scene, source) {
  let p = originPos(v, scene.origin)
  if (p) return p
  if (scene.fallback) return scene.fallback(v, source)
  return null
}

// Run a scene segment now, except for the resident teleports, which are handed
// to `pending` for the arrival loop.
function runSegSplit(server, origin, cmds, pending) {
  let now = [], later = []
  cmds.forEach(c => { (isNpcTp(c) ? later : now).push(c) })
  runSeg(server, origin, now)
  if (later.length) pending.push({ origin: origin, cmds: later })
}

// The finales' arrival beat, for scenes. Same shape as arrival(): try, count
// the teleports that reported no effect, and go round again a second later up
// to ARRIVE_TRIES times. Two differences, both because a scene is not an act:
// there is no world-level latch to take (runScene has already taken the
// scene's own once() latch, and a re-run of a scene re-runs these teleports
// harmlessly - a tp is a tp), and the loop holds the forceload itself, since
// runGroup drops its own after sixty ticks.
function sceneArrival(v, key, regions, segs) {
  let tries = 0
  let step = s => {
    tries++
    forceload(s, regions, 'add')
    let missed = 0
    segs.forEach(seg => { missed += runSegArrive(s, seg.origin, seg.cmds) })
    if (missed > 0 && tries < ARRIVE_TRIES) {
      console.info('[valley] scene ' + key + ' arrival: ' + missed +
                   ' resident(s) not in a loaded chunk yet; going round again (' +
                   tries + '/' + (ARRIVE_TRIES - 1) + ')')
      v.delay(ARRIVE_GAP, step)
      return
    }
    if (missed > 0) {
      console.warn('[valley] scene ' + key + ' arrival gave up with ' + missed +
                   ' resident(s) unmoved. /valley scene ' + key + ' replays it.')
    }
    // The six-second hold a scene has always taken, counted from the last
    // attempt rather than from the scene: letting the chunks go two ticks
    // after the people arrive would be a shorter hold than the code this
    // replaces, not a longer one.
    v.delay(120, srv => forceload(srv, regions, 'remove'))
  }
  v.delay(ARRIVE_FIRST, step)
}

function runScene(source, key) {
  let v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }

  let scene = SCENES[key]
  if (!scene) {
    msg(source, Text.gray('[valley] no scene "' + key + '". Known scenes: ' +
      Object.keys(SCENES).join(' ')))
    return 0
  }
  // Almost every scene is anchor-relative, so no anchor means nothing to
  // measure from. `noAnchor` is the exception for a scene measured from the
  // homestead instead — see SCENES.cellar, which is a Q5 reward and therefore
  // fires two quests BEFORE the stake is driven.
  if (!scene.noAnchor && !v.anchor()) {
    msg(source, Text.red(
      'No Town Anchor is set, so a scene has nothing to measure from. Place the Surveyor\'s Stake first (Q7).'))
    return 0
  }

  // Resolve the origin BEFORE the once() latch is burned: a scene that could
  // not find anywhere to build has not played, and must stay re-runnable.
  let origin = sceneOrigin(v, scene, source)
  if (!origin) {
    console.warn('[valley] scene ' + key + ': no origin "' + scene.origin + '" and no usable fallback; nothing built')
    msg(source, Text.gray('[valley] scene ' + key + ' has nothing to measure from yet.'))
    return 0
  }

  if (scene.once && !v.once('scene_' + key)) {
    console.info('[valley] scene ' + key + ' already played in this world')
    return 1
  }

  let server = source.server

  // Same trap as a finale, and worse for `bram`: a scene reward claimed from
  // anywhere the origin's chunk is not loaded refuses every setblock, logs
  // "scene played", and never builds. `bram` carries once:true and is the only
  // thing that puts Bram at the mill, so a claim from 200 blocks away used to
  // make Q12 unwinnable for good. Hold the chunks for six seconds.
  let sr = [origin]
  let a = v.anchor()
  if (a) sr.push(a)
  if (scene.also) { let p2 = originPos(v, scene.also.origin); if (p2) sr.push(p2) }
  if (scene.home) { let h = v.home(); if (h) sr.push(h) }
  sr = sr.filter(p => p)
  forceload(server, sr, 'add')

  // Resident teleports are collected here rather than run in this tick. See
  // sceneArrival(): the forceload above is asynchronous, so a `tp @e[tag=npc_*]`
  // issued now matches nothing and returns 0, and a scene - unlike a finale -
  // had no retry. Measured: SCENES.q73 builds act4_bram_chair, whose group ends
  // in `tp @e[tag=npc_bram,limit=1] ~23 ~1 ~-7`, and on a replay from the
  // console that teleport returned 0 and Bram never sat down.
  let pending = []
  try {
    // A scene may need the ground prepared before its own commands land.
    if (scene.pre) scene.pre(server, v)
    // Town-plan groups first: they build the room the cmds below dress.
    if (scene.groups) scene.groups.forEach(g => runGroup(server, v, g, pending))
    // `cmds` may be a function: the three scenes that stand on the square read
    // their cells out of the town plan at run time rather than carrying a copy.
    let cl = (typeof scene.cmds === 'function') ? scene.cmds(v) : scene.cmds
    if (cl) runSegSplit(server, origin, cl, pending)
    if (scene.also) {
      let o2 = originPos(v, scene.also.origin)
      if (o2) {
        let al = (typeof scene.also.cmds === 'function') ? scene.also.cmds(v) : scene.also.cmds
        if (al) runSegSplit(server, o2, al, pending)
      }
    }
    if (scene.run) scene.run(server, v)
    if (scene.who) v.sayAll(scene.who[0], scene.who[1])
  } catch (err) {
    // A scene is set dressing. It must never take a reward down with it.
    console.error('[valley] scene ' + key + ' failed: ' + err)
    msg(source, Text.gray('[valley] scene ' + key + ' hit a snag; see the log.'))
    v.delay(120, s => forceload(s, sr, 'remove'))
    return 0
  }
  if (pending.length) {
    // The arrival loop owns the forceload from here: it can spend up to
    // ARRIVE_FIRST + 7*ARRIVE_GAP ticks waiting for a chunk, which is longer
    // than the 120 a scene used to hold for, and runGroup lets its own
    // forceload go after 60.
    pending.forEach(seg => { if (seg.origin) sr.push(seg.origin) })
    sceneArrival(v, key, sr, pending)
  } else {
    v.delay(120, s => forceload(s, sr, 'remove'))
  }
  console.info('[valley] scene ' + key + ' played')
  return 1
}

const FINALES = {
  act1: finaleAct1, act2: finaleAct2, act3: finaleAct3,
  act4: finaleAct4, act5: finaleAct5
}


// -----------------------------------------------------------------------------
// Command feedback.
// 1.20 changed CommandSourceStack.sendSuccess to take a Supplier<Component>,
// which is a trap for a script. Everything here talks to the player directly
// instead, and falls back to the console when the source is not a player.
// -----------------------------------------------------------------------------
function msg(source, component) {
  let p = srcPlayer(source)
  if (p) p.tell(component)
  else console.info('[valley] ' + component.getString())
}

// CommandSourceStack#getPlayer THROWS when the source is not a player (a
// command block, the console, or a reward claimed in an odd context), so every
// read of it goes through here.
function srcPlayer(source) {
  try { return source.player || null } catch (err) { return null }
}

// -----------------------------------------------------------------------------
// The P7 guard. One entry point, one flag, one refusal message.
// -----------------------------------------------------------------------------
function runFinale(source, act, force) {
  let v = global.valley
  let server = source.server
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }

  if (!v.anchor()) {
    msg(source, Text.red(
      'No Town Anchor is set. Place the Surveyor\'s Stake first (Q7), then run this again.'))
    return 0
  }
  if (v.finaleDone(act) && !force) {
    msg(source, Text.gray('[valley] ' + act + ' finale has already run in this world.'))
    msg(source, Text.gray('If a payoff never landed, /valley finale ' + act +
      ' force replays only the beats that never fired.'))
    return 1
  }

  // The act is NOT latched here. See the Beats block above: markFinale lives
  // in the last beat of each chain, so a reload inside a delay window leaves
  // the act re-runnable and the re-run picks up where the queue was lost.
  //
  // Forceload first. Every command in this file runs as the server, from
  // 0 0 0, so a chunk nobody is standing in refuses all of them and runSeg
  // swallows the whole act into console warnings.
  let regions = forceHold(server, v, act)
  console.info('[valley] running finale ' + act + (force ? ' (forced)' : '') +
               ', ' + regions.length + ' region(s) forceloaded')
  try {
    FINALES[act](server, v)
  } catch (err) {
    console.error('[valley] finale ' + act + ' threw: ' + err)
    msg(source, Text.gray('[valley] ' + act + ' hit a snag; see the log. ' +
      '/valley finale ' + act + ' force picks it up again.'))
  }
  // Belt and braces. endAct releases as soon as the chain finishes; this
  // catches a forced re-run whose beats were all done already, and it is a
  // no-op when endAct got there first.
  v.delay(FINALE_RELEASE[act] || 60, s => forceRelease(s, act))
  return 1
}

// -----------------------------------------------------------------------------
// /valley anchor set — the SAME clearance rule the Surveyor's Stake obeys.
//
// The refusal used to live in one place only: BlockEvents.placed in
// valley_checks.js, behind `if (!player || !player.isPlayer()) return`. So the
// rule covered the block a player puts down and nothing else, and the command
// path — the one an op uses, the one a headless test can reach, and the one
// `scratch/verify_run.sh` drives the whole town from — set the anchor
// unconditionally. Proved live: with Home at -780 92 -783,
// `/valley anchor set -770 92 -773` (fourteen blocks away) answered
// "Town Anchor set to -770 92 -773" and the town was then laid over the
// cottage.
//
// townWouldSwallow() and townBox() live in valley_checks.js, which KubeJS
// loads first ('c' sorts before 'f') into the same scope; the typeof guard is
// for the case where that file failed to load, where refusing every anchor
// would be worse than the bug.
//
// `force` is the op override, and it says so in the refusal.
// -----------------------------------------------------------------------------
function anchorHearth() {
  let v = global.valley
  if (!v) return null
  // The team's home mark, else the Kettle ruin's hearthstone — the same two
  // points, in the same order, that hearthXZ() uses for the stake.
  return v.home() || v.ruin()
}

function anchorSetCmd(source, x, y, z, force) {
  let v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }
  let h = anchorHearth()
  if (!force && h) {
    if (typeof townWouldSwallow !== 'function') {
      console.warn('[valley] valley_checks.js is not loaded, so /valley anchor set ' +
                   'cannot check the town clearance. Setting it anyway.')
    } else if (townWouldSwallow(x, z, h[0], h[2])) {
      msg(source, Text.red('Too close to the cottage — the town would be built on top of it.'))
      v.sayAll('Josie',
        'Not there. Fifteen houses, a square and a mill go in around that stake, and I ' +
        'will not have them in your dooryard. Walk on up the road until the chimney is ' +
        'small behind you, then drive it.')
      msg(source, Text.gray('Home is at ' + h.join(' ') + '. ' +
        '/valley anchor set ' + x + ' ' + y + ' ' + z + ' force sets it anyway.'))
      return 0
    }
  }
  v.setAnchor(x, y, z)
  msg(source, Text.gold('Town Anchor set to ' + x + ' ' + y + ' ' + z + (force ? ' (forced)' : '')))
  return 1
}

// =============================================================================
// /valley — the command tree (§11 "the /valley command tree — every reward
// calls it").
// =============================================================================
ServerEvents.commandRegistry(event => {
  let Commands = event.commands
  let Arguments = event.arguments

  event.register(
    Commands.literal('valley')
      .requires(src => src.hasPermission(0))

      // --- /valley finale act1 .. act5 [force] ----------------------------
      // `force` is the backstop for an act latched done by an older build, or
      // by a crash between markFinale and the payoff: it skips the done check
      // and lets each beat's own latch decide what still has to run.
      .then(FIN_ACTS.reduce((node, act) =>
        node.then(Commands.literal(act)
          .executes(ctx => runFinale(ctx.source, act, false))
          .then(Commands.literal('force')
            .executes(ctx => runFinale(ctx.source, act, true)))),
        Commands.literal('finale').requires(src => src.hasPermission(2))))

      // --- /valley check power | turbine ---------------------------------
      // §12.3: Bigger Reactors RPM and fuel figures may live in non-serialized
      // runtime fields, so these are the shipped Checkmark fallback: standing
      // at the Works with the machine built is the honour-system verification,
      // and the numbers the quest asks for are printed here, not scraped.
      .then(Commands.literal('check')
        .then(Commands.literal('turbine').executes(ctx => checkAt(ctx.source, 'q71',
          'Turbine holding 1,800 RPM under load.',
          'Bram: read the tachometer on the Turbine Terminal. 1,800 RPM under load is the number.')))
        .then(Commands.literal('power').executes(ctx => checkAt(ctx.source, 'q83',
          '25,000 FE/t sustained at 60 mB/t of fuel or under.',
          'Tobin: 25,000 FE/t across both turbines, 60 mB/t of fuel or under. Reactor Terminal, top two rows.')))
        .then(Commands.literal('standing').executes(ctx => standingReport(ctx.source))))

      // --- /valley greet <key> <before|after> <player> ---------------------
      // Run by every resident's ON_INTERACTION (see story/npcs.json). Easy NPC
      // replaces the literal @initiator with the interacting player's name
      // before dispatch — ActionUtils#parseMacros, the same macro Bram's
      // token give already relies on — so the third argument arrives here as a
      // plain name. Never throws: an unknown key or a name that no longer
      // resolves is a no-op, because this runs on a right-click.
      .then(Commands.literal('greet')
        .then(Commands.argument('key', Arguments.WORD.create(event))
          .then(Commands.argument('phase', Arguments.WORD.create(event))
            .then(Commands.argument('player', Arguments.WORD.create(event))
              .executes(ctx => {
                let v = global.valley
                if (!v || !v.greet) return 0
                v.greet(Arguments.WORD.getResult(ctx, 'player'),
                        Arguments.WORD.getResult(ctx, 'key'),
                        Arguments.WORD.getResult(ctx, 'phase'))
                return 1
              })))))

      // --- /valley standing <key> [team] (§5 Standing: Trusted) -----------
      // Called by a silent, elevated command reward on each of the eight
      // chain-closing quests:
      //     /valley standing q59 {team}
      // CommandReward#claim substitutes only @p, {x} {y} {z}, {team}, {quest}
      // and {chapter} — {long_team_id} is NOT one of them and used to arrive
      // at this command as the literal eleven characters. {team} is the FTB
      // Teams short team name, a plain string, and that string is the ledger
      // key. The argument stays optional: run by hand it resolves from the
      // caller, and standingCmd records both spellings so the two halves of
      // the ledger can never drift apart.
      .then(Commands.literal('standing').requires(src => src.hasPermission(2))
        .then(Commands.argument('key', Arguments.WORD.create(event))
          .executes(ctx => standingCmd(ctx, event, null))
          .then(Commands.argument('team', Arguments.WORD.create(event))
            .executes(ctx => standingCmd(ctx, event, 'team')))))

      // --- /valley scene <key> --------------------------------------------
      // Act IV's twelve set changes. Any word is accepted; an unknown key
      // prints the list instead of throwing (§P3).
      .then(Commands.literal('scene')
        .then(Commands.argument('key', Arguments.WORD.create(event))
          .executes(ctx => runScene(ctx.source, event.arguments.WORD.getResult(ctx, 'key')))))

      // --- /valley anchor -------------------------------------------------
      // `set` obeys the same clearance rule as the stake; `set ... force` is
      // the op override. See anchorSetCmd().
      .then(Commands.literal('anchor').then(Commands.literal('set').requires(src => src.hasPermission(2))
        .then(Commands.argument('x', Arguments.INTEGER.create(event)).then(Commands.argument('y', Arguments.INTEGER.create(event)).then(Commands.argument('z', Arguments.INTEGER.create(event))
          .executes(ctx => anchorSetCmd(ctx.source,
            Arguments.INTEGER.getResult(ctx, 'x'), Arguments.INTEGER.getResult(ctx, 'y'),
            Arguments.INTEGER.getResult(ctx, 'z'), false))
          .then(Commands.literal('force').executes(ctx => anchorSetCmd(ctx.source,
            Arguments.INTEGER.getResult(ctx, 'x'), Arguments.INTEGER.getResult(ctx, 'y'),
            Arguments.INTEGER.getResult(ctx, 'z'), true))))))))
      .then(Commands.literal('home').then(Commands.literal('set').requires(src => src.hasPermission(2))
        .then(Commands.argument('x', Arguments.INTEGER.create(event)).then(Commands.argument('y', Arguments.INTEGER.create(event)).then(Commands.argument('z', Arguments.INTEGER.create(event)).executes(ctx => {
          let x = Arguments.INTEGER.getResult(ctx, 'x'), y = Arguments.INTEGER.getResult(ctx, 'y'), z = Arguments.INTEGER.getResult(ctx, 'z')
          global.valley.setHome(x, y, z)
          msg(ctx.source, Text.gold('Home set to ' + x + ' ' + y + ' ' + z))
          return 1
        }))))))
      .then(Commands.literal('anchor').executes(ctx => {
        let v = global.valley
        let a = v ? v.anchor() : null
        let h = v ? v.home() : null
        if (!a) {
          msg(ctx.source, Text.gray('No Town Anchor set yet. Place the Surveyor\'s Stake (Q7).'))
        } else {
          msg(ctx.source, Text.gold('Town Anchor: ' + a.join(' ')))
        }
        if (h) msg(ctx.source, Text.gray('Home: ' + h.join(' ')))
        return 1
      }))

      // --- /valley lamps --------------------------------------------------
      .then(Commands.literal('lamps').executes(ctx => {
        let v = global.valley
        let n = v ? v.lamps().length : 0
        msg(ctx.source, Text.gold('Lantern Road: ' + n + ' posts recorded of 40.'))
        return 1
      }))

      // --- /valley stage <add|remove> <world|team|player> <id> (§P3) -------
      .then(Commands.literal('stage').requires(src => src.hasPermission(2))
        .then(Commands.literal('add')
          .then(Commands.literal('world')
            .then(Commands.argument('id', Arguments.WORD.create(event))
              .executes(ctx => stageCmd(ctx, event, 'add', 'world'))))
          .then(Commands.literal('team')
            .then(Commands.argument('id', Arguments.WORD.create(event))
              .executes(ctx => stageCmd(ctx, event, 'add', 'team'))))
          .then(Commands.literal('player')
            .then(Commands.argument('id', Arguments.WORD.create(event))
              .executes(ctx => stageCmd(ctx, event, 'add', 'player')))))
        .then(Commands.literal('remove')
          .then(Commands.literal('player')
            .then(Commands.argument('id', Arguments.WORD.create(event))
              .executes(ctx => stageCmd(ctx, event, 'remove', 'player'))))))
  )
})

// -----------------------------------------------------------------------------
// /valley check <x> — completes the quest if the player is actually at the
// Works, and prints the number the quest asked for either way.
// -----------------------------------------------------------------------------
// The block each check has to be looking at, and its name in the quest text.
// Q70's rewards hand the player biggerreactors:turbine_terminal, and Q70's own
// task consumes a biggerreactors:reactor_terminal into the vessel, so both of
// these are standing in the Works before the quest that checks them opens.
const CHECK_BLOCK = {
  q71: ['biggerreactors:turbine_terminal', 'Turbine Terminal'],
  q83: ['biggerreactors:reactor_terminal', 'Reactor Terminal']
}

function checkAt(source, key, ok, hint) {
  let v = global.valley
  let player = srcPlayer(source)
  if (!v || !player) { msg(source, Text.red('Run this as a player, standing at the Works.')); return 0 }
  let works = v.mark('works')
  if (!works) { msg(source, Text.red('No Town Anchor set, so the Works has no position yet.')); return 0 }
  // 16, not 48. `check` sits under the root's hasPermission(0) — unlike
  // `finale` and `standing`, which both demand 2 — because Q71's own text
  // tells the player to type it. That is fine; a 96-block-wide box around town
  // in which typing one line finishes the reactor is not.
  let d = Math.max(Math.abs(player.x - works[0]), Math.abs(player.z - works[2]))
  if (d > 16) {
    msg(source, Text.gray('Stand at the Works and run this again.'))
    msg(source, Text.gray(hint))
    return 0
  }
  // §12.3's honour system is "the player reads the number off the terminal",
  // and both quest cards say so in as many words: "on the Turbine Terminal
  // that came with it", "at the reactor terminal". So the terminal has to be
  // in the crosshair. Without this, q71 handed out stage reactor_ready (which
  // opens q72, q73 and q75) and q83 handed out big_power (the only gate on
  // the quarry) with no machine built at all.
  let want = CHECK_BLOCK[key]
  if (want) {
    let look = null
    let traced = true
    try {
      look = player.rayTrace(6)
    } catch (err) {
      // A clean miss refuses. A BROKEN BINDING does not: an unwinnable climax
      // is worse than a loophole in a two-player pack, so if rayTrace itself
      // ever goes away this falls back to the 16-block check and says so in
      // the log rather than locking Q71 and Q83 shut.
      traced = false
      console.error('[valley] rayTrace unavailable, /valley check ' + key +
                    ' fell back to distance only: ' + err)
    }
    if (traced && (!look || !look.block || String(look.block.id) !== want[0])) {
      msg(source, Text.gray('Look at the ' + want[1] + ' and run this again.'))
      msg(source, Text.gray(hint))
      return 0
    }
  }
  msg(source, Text.gold(ok))
  v.complete(player, key)
  v.once(key, v.teamId(player))
  return 1
}

// -----------------------------------------------------------------------------
// /valley check standing — reports Q86's second condition. Read-only.
//
// NOT named checkStanding. KubeJS loads every server script into ONE shared
// scope, and valley_checks.js already has a function of that name — the slow
// tick that actually evaluates Standing and grants Trusted. Scripts load
// alphabetically, so this file loaded last and its declaration won: the tick
// called THIS function with (server, player), got a non-player source, and
// printed "[valley] Run this as a player." every 200 ticks forever while the
// real six-of-eight evaluation never ran once. Nothing threw, so nothing in
// the pack noticed. Keep every top-level name in this folder unique.
//
// §5: Standing is a count of completed resident chains. The count itself lives
// in the ledger in valley_core.js (written by /valley standing below) and is
// evaluated by the slow-tick check in valley_checks.js — this command only
// prints it, so nothing here can hand out Standing that was not earned.
// -----------------------------------------------------------------------------
const STANDING_WHO = {
  q59: 'Wisp', q60: 'Marnie', q62: 'Halden', q63: 'Pip',
  q73: 'Bram', q75: 'Tobin', q77: 'Nella', q85: 'Oda'
}

function standingReport(source) {
  let v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }
  let player = srcPlayer(source)
  if (!player) { msg(source, Text.red('Run this as a player.')); return 0 }

  let team = v.teamId(player)
  let api = v.standingApiClosed(player)
  if (api) api.forEach(k => v.recordStanding(team, k))

  let closed = v.standingClosed(team)
  let done = {}
  closed.forEach(k => { done[k] = true })

  msg(source, Text.gold('Standing: ' + closed.length + ' of 8 chains closed. Six are needed.'))
  let line = v.standingChains().map(k =>
    (done[k] ? '✓ ' : '· ') + STANDING_WHO[k] + ' ' + k.toUpperCase()).join('   ')
  msg(source, Text.gray(line))
  if (v.standingGranted(team)) {
    msg(source, Text.gold('Standing: Trusted is already granted for this team.'))
  } else if (closed.length >= v.STANDING_REQUIRED) {
    msg(source, Text.gray('Trusted lands within ten seconds — the listener ticks every 200 ticks.'))
  }
  return 1
}

// -----------------------------------------------------------------------------
// /valley standing <key> [team] — record ONE closed chain against a team.
//
// This is the deterministic half of Standing. It is idempotent (the ledger flag
// is set once), it validates the key against the eight chains in valley_core,
// and it never completes anything itself — valley_checks.js owns that, so there
// is exactly one place where "six of eight" is decided.
// -----------------------------------------------------------------------------
function standingCmd(ctx, event, teamArgName) {
  let v = global.valley
  if (!v) return 0
  let key = event.arguments.WORD.getResult(ctx, 'key')
  let player = srcPlayer(ctx.source)

  if (v.standingChains().indexOf(key) === -1) {
    msg(ctx.source, Text.red('Not a chain-closing quest: ' + key +
      '. Expected one of ' + v.standingChains().join(' ') + '.'))
    return 0
  }

  // `self` is what every READER of the ledger uses (valley_checks.js and
  // /valley check standing both call teamId), so it is always recorded. The
  // argument is the {team} string FTB Quests substituted; it is recorded too,
  // so a team whose short name the API spells differently cannot strand a
  // closed chain in a slot nothing ever reads.
  let self = v.teamId(player)
  let keys = [self]
  if (teamArgName) {
    let arg = event.arguments.WORD.getResult(ctx, teamArgName)
    if (arg) {
      arg = String(arg)
      if (keys.indexOf(arg) === -1) keys.push(arg)
    }
  }

  let fresh = false
  keys.forEach(t => { if (v.recordStanding(t, key)) fresh = true })

  let closed = v.standingClosed(self)
  if (fresh && player) {
    v.say(player, 'Oda', (STANDING_WHO[key] || 'That') + "'s story is closed. That's " +
      closed.length + ' of eight in my book.')
  }
  console.info('[valley] /valley standing ' + key + ' [' + keys.join(', ') + ']' +
               ' -> ' + closed.length + '/8' + (fresh ? '' : ' (already recorded)'))
  return 1
}

// -----------------------------------------------------------------------------
// /valley stage ...
// -----------------------------------------------------------------------------
function stageCmd(ctx, event, op, scope) {
  let v = global.valley
  let id = event.arguments.WORD.getResult(ctx, 'id')
  if (!v) return 0
  if (scope === 'world') {
    v.addWorldStage(id)
    msg(ctx.source, Text.gray('World stage ' + id + ' granted.'))
    return 1
  }
  let player = srcPlayer(ctx.source)
  if (!player) { msg(ctx.source, Text.red('Run this as a player.')); return 0 }
  if (scope === 'team') {
    v.stageAll(null, id)
    msg(ctx.source, Text.gray('Stage ' + id + ' granted to everyone online.'))
    return 1
  }
  if (op === 'add') player.stages.add(id); else player.stages.remove(id)
  msg(ctx.source, Text.gray('Stage ' + id + ' ' + op + 'ed for ' + v.pname(player) + '.'))
  return 1
}

console.info('[valley] valley_finales.js ok')
