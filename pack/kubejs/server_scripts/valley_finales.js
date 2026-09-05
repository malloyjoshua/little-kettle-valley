// =============================================================================
// valley_finales.js — Little Kettle Valley: the /valley command tree and the
// five finale chains.
//
// THE RULE THIS FILE IS BUILT ON: the story only ADDS.
//
// The pack ships one hand-built world (docs/transitions-design.md architecture A). The
// farm, the town, the lantern road, the forty posts, the pier, the sealed Works, the
// greenhouse and bathhouse shells, the cellar and the three empty newcomer houses are all
// standing before the first login. So a finale or a scene may:
//
//     light a lamp        setblock a cage lamp from its dark state to its lit one
//     open a door         flip `open` on a door that is already hanging there
//     set furniture down  ONLY into a cell that is air right now — see put() below
//     bring a resident    easy_npc preset import (same UUID) or a tp to a registry stand
//     turn the year       season / time / weather
//     say something       title, tellraw, playsound, bossbar, advancement, give
//
// ...and may NOT, ever, under any circumstance:
//
//     cut a pad           `@pad` and `@padfix` live in valley_build.js
//     paste a building    `place template` lives in valley_build.js
//     clear a box         `fill … air` lives in valley_build.js
//     re-level anything   the terracing is baked into the world
//
// putSeg() below refuses all four at runtime and logs the line, so the rule is enforced
// where it is broken rather than asserted in a doc. `scratch/shipped_playthrough.sh`
// greps this file for the same four things.
//
// §12.2 P7 — finale idempotency. FTB Quests command rewards fire once per CLAIMING PLAYER,
// so no finale build ever lives in a reward. Every finale reward is exactly one command,
// `/valley finale actN`; this file checks a server.persistentData flag and returns silently
// if it is already set.
//
// §12.2 P3 — there is no vanilla stage command, so `/valley stage` is here too.
//
// ---------------------------------------------------------------------------
// Corrections still in force, verified against the shipped jars:
//
//  1. `sereneseasons setseason X` -> `season set X` (SeasonCommands registers the ROOT
//     literal `season`, then `set`, then a SubSeason argument).
//  2. `easy_npc preset import data <preset> <x> <y> <z>` — a source literal is REQUIRED,
//     and `import` reuses the preset's UUID, so re-running a finale cannot duplicate a
//     resident. `import_new` would.
//  3. `schedule function` -> global.valley.delay(). We ship no datapack functions for this.
//  4. `~` offsets are resolved to ABSOLUTE coordinates here; 1.20.1 has no macros.
//  5. The lamp is `createdeco:yellow_copper_lamp`. CageLampBlock#shouldBeLit is
//     `inverted XOR redstone into the mounting face` and neighborChanged writes that answer
//     back over whatever `lit` a setblock wrote — so a lamp that must STAY lit with no
//     redstone on it is inverted=true,lit=true, and a dark one is inverted=false,lit=false.
//  6. A `/setblock` whose target block AND blockstate already match is a NO-OP that
//     silently drops the NBT tag that came with it. Signs that already exist are written
//     with `data merge block`, never setblock.
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


// =============================================================================
// THE ADDITIVE RUNNER.
//
// Every command a finale or a scene runs goes through here, and four families of command
// are refused rather than run:
//
//   `@pad` / `@padfix`   the levelled, material-sampled, feathered pad
//   `place template`     pasting a building over whatever is standing there
//   `fill … air`         clearing a box, which is how the old pack deleted player builds
//   `fill` of anything   a story beat that needs a fill is a story beat that is building
//
// They are refused HERE, in the runner, not checked in review, because the failure mode
// they cause is silent: a fill in replace mode destroys a chest with its contents and
// returns success. A refusal is one warning in the log and a scene that is missing a prop.
//
// The one `fill` a story is allowed is none. If a beat needs a row of six blocks, it is six
// setblocks, and every one of them goes through put().
// =============================================================================
const BANNED = [
  { re: /^@pad/, why: 'a levelled pad' },
  { re: /^@padfix/, why: 'a pad edge fix' },
  { re: /place template/, why: 'a pasted structure template' },
  { re: /^fill /, why: 'a box fill' },
  { re: /^clone /, why: 'a clone' },
  { re: /^execute .* run fill /, why: 'a box fill' },
  { re: /run function valley:/, why: 'a datapack function that builds' }
]

function refuses(cmd) {
  for (let i = 0; i < BANNED.length; i++) {
    if (BANNED[i].re.test(cmd)) return BANNED[i].why
  }
  return null
}

// Resolve `~dx ~dy ~dz` against an origin. Nothing else in a command line starts with `~`,
// so a single regex pass is exact and leaves NBT and JSON untouched.
const TILDE3 = /(^|\s)~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)(?=[ ]|$)/g

function num(base, d) {
  let v = base + (d === '' || d === '-' ? 0 : parseFloat(d))
  return (v === Math.floor(v)) ? String(Math.floor(v)) : String(v)
}

function resolve(cmd, origin) {
  return cmd.replace(TILDE3, (m, lead, dx, dy, dz) =>
    lead + num(origin[0], dx) + ' ' + num(origin[1], dy) + ' ' + num(origin[2], dz))
}

function runSeg(server, origin, cmds) {
  cmds.forEach(c => {
    if (!c || c.charAt(0) === '#') return
    let full = resolve(c, origin)
    let no = refuses(full)
    if (no) {
      console.error('[valley] REFUSED (' + no + ' is not something the story may do): ' + full)
      return
    }
    try {
      let r = server.runCommandSilent(full)
      if (r === 0 && full.indexOf('setblock') < 0) {
        console.warn('[valley] command returned 0 (no effect / failed): ' + full)
      }
    } catch (err) { console.error('[valley] finale command failed: ' + full + ' :: ' + err) }
  })
}

// -----------------------------------------------------------------------------
// put() — the furniture guard.
//
// A story beat may set a block down ONLY where the cell is air right now. This is the
// whole of "never replace a player-placed block": we do not need to know whether the thing
// in the way is hers, because if anything at all is in the way we do not write.
//
// It is also what makes every scene safely re-runnable. `/valley scene q62` twice used to
// re-stamp the still over whatever the player had since put on those three cells.
//
// Returns true if it wrote.
// -----------------------------------------------------------------------------
const AIRS = { 'minecraft:air': 1, 'minecraft:cave_air': 1, 'minecraft:void_air': 1 }

function isAir(level, p) {
  try { return !!AIRS[String(level.getBlock(p[0], p[1], p[2]).id)] } catch (err) { return false }
}

function put(server, p, block, what) {
  let level = null
  try { level = server.overworld() } catch (err) { level = null }
  if (level && !isAir(level, p)) {
    let held = String(level.getBlock(p[0], p[1], p[2]).id)
    // Already what we were going to put there: the scene has run before, or the world
    // shipped with it. Silent, because that is the normal answer on a re-run.
    if (block.indexOf(held) !== 0) {
      console.info('[valley] left alone: ' + (what || block) + ' at ' + p.join(' ') +
                   ' — ' + held + ' is already there')
    }
    return false
  }
  server.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + block)
  return true
}

// The same guard for a list of [pos, block] pairs, resolved against an origin.
function putAll(server, origin, list) {
  let n = 0
  list.forEach(e => {
    let p = [origin[0] + e[0][0], origin[1] + e[0][1], origin[2] + e[0][2]]
    if (put(server, p, e[1], e[2])) n++
  })
  return n
}

// -----------------------------------------------------------------------------
// openDoor() — the other half of "the story only adds".
//
// Every door in the valley is hanging in the world already, shut. Opening one is a beat in
// four different acts, and it cannot be a setblock with a typed blockstate: the properties
// that matter (facing, hinge) came out of the structure template and differ per building,
// and `/setblock` fills unspecified properties with DEFAULTS — so a typed door would spin
// the door to face north and swap its hinge.
//
// So the door is read out of the world and written back with the same properties and
// `open` flipped. Both halves, because a door is two blocks and the halves must agree.
// -----------------------------------------------------------------------------
function doorState(level, p, open) {
  let b = level.getBlock(p[0], p[1], p[2])
  let id = String(b.id)
  if (id.indexOf('_door') < 0) return null
  let props = null
  try { props = b.properties } catch (err) { props = null }
  if (!props) return null
  let out = []
  let keys = null
  try { keys = props.keySet ? props.keySet().toArray() : Object.keys(props) } catch (err) { keys = null }
  if (!keys) return null
  for (let i = 0; i < keys.length; i++) {
    let k = String(keys[i])
    let val = String(props.get ? props.get(keys[i]) : props[k])
    if (k === 'open') val = open ? 'true' : 'false'
    if (k === 'powered') val = 'false'
    out.push(k + '=' + val)
  }
  return id + '[' + out.join(',') + ']'
}

// A DOOR WILL NOT TAKE AN `open` FLIP FROM A BARE SETBLOCK. Measured on this pack,
// 2026-09-05, on the shipped world, with the server console:
//
//   setblock -342 68 -39 minecraft:spruce_door[facing=east,half=lower,hinge=right,\
//                                              open=true,powered=false]
//   -> "Could not set the block"                       (the door stayed shut)
//
// and the same command differing in `hinge` instead, or in `powered` instead, both come
// back "Changed the block". So it is not the command, the coordinate, the chunk or the
// permission: it is the `open` property specifically, and only while the door's OTHER HALF
// is standing. A door half's updateShape copies FACING, OPEN, HINGE and POWERED from its
// partner in BOTH directions, so a write that touches one half alone is put straight back
// to what the other half says, the write ends up equal to the state already there, and
// vanilla reports it as no change. A trapdoor and a fence gate -- single blocks -- take the
// same open-only flip without complaint, which is the control.
//
// This is why the store, the church, the mill, the inn, the two cottages, the Town Hall and
// all three newcomer houses were still shut at the end of a full playthrough: every one of
// them is opened by this function, and every one of those setblocks was refused, silently,
// because runCommandSilent's 0 was never read.
//
// So: clear BOTH halves to air first, then write both back with the new `open`. Clearing
// the upper half takes the lower with it (updateShape returns AIR when the partner is
// gone), which is why the second air setblock usually reports no change and why the lower
// is written FIRST on the way back -- the upper cannot survive without it. `setblock air`
// drops nothing (only `destroy` mode does), so the door is not turned into an item, and the
// net effect on the world is still the one block the story is entitled to: the same door,
// same facing, same hinge, open.
function openDoor(server, p, open) {
  let level = null
  try { level = server.overworld() } catch (err) { level = null }
  if (!level) return false
  let lower = doorState(level, p, open)
  if (!lower) {
    console.warn('[valley] no door at ' + p.join(' ') + ' to open')
    return false
  }
  let upper = doorState(level, [p[0], p[1] + 1, p[2]], open)
  if (upper) {
    server.runCommandSilent('setblock ' + p[0] + ' ' + (p[1] + 1) + ' ' + p[2] +
                            ' minecraft:air')
  }
  server.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' minecraft:air')
  let r = server.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + lower)
  if (r === 0) {
    console.error('[valley] door at ' + p.join(' ') + ' could not be put back: ' + lower)
  }
  if (upper) {
    server.runCommandSilent('setblock ' + p[0] + ' ' + (p[1] + 1) + ' ' + p[2] + ' ' + upper)
  }
  server.runCommandSilent('playsound minecraft:block.wooden_door.open master @a ' +
                          p[0] + ' ' + p[1] + ' ' + p[2] + ' 1 1')
  return true
}

// A lantern on the doorstep, so an opened house reads as lived-in from the road.
//
// There is no cell near a door that every one of the twelve templates leaves clear — door +
// [0,2,0] is the lintel, and on the three newcomer houses that is a bone block, on the Town
// Hall a dark oak stair. So this TRIES a ring: the four cells the doorstep opens onto, then
// the two above the doorway, and takes the first that is air with something solid under it.
// If every one of them is occupied it places nothing and says so once, which is the correct
// answer for a porch somebody has already decorated.
const PORCH_TRIES = [[1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1],
                     [1, 1, 0], [-1, 1, 0], [0, 1, 1], [0, 1, -1],
                     [0, 2, 0]]

function porchLight(server, key, door) {
  let level = null
  try { level = server.overworld() } catch (err) { level = null }
  for (let i = 0; i < PORCH_TRIES.length; i++) {
    let o = PORCH_TRIES[i]
    let p = [door[0] + o[0], door[1] + o[1], door[2] + o[2]]
    if (!level) break
    if (!isAir(level, p)) continue
    // a lantern needs a floor under it or a ceiling over it; the doorstep ring has floors.
    if (isAir(level, [p[0], p[1] - 1, p[2]])) continue
    server.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] +
                            ' minecraft:lantern[hanging=false]')
    return true
  }
  console.info('[valley] ' + key + ': no free cell on the doorstep for a lantern; left as is')
  return false
}

// Open a building's front door by its registry key, and put a light on its doorstep.
function moveIn(server, v, key, light) {
  let door = v.site('doors.' + key)
  if (!door) { console.warn('[valley] no registry door for ' + key); return false }
  openDoor(server, door, true)
  if (light !== false) porchLight(server, key, door)
  return true
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
    let no = refuses(full)
    if (no) {
      console.error('[valley] REFUSED (' + no + ' is not something the story may do): ' + full)
      return
    }
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
// act5's sixth journal line at 100 + 6*100 = 700.
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
// The Works is a room in the world.
//
// WHAT USED TO BE HERE: WORKS_SHELL, excavateWorks() and dryWorks() — a runtime dig that
// sealed a fourteen-block box six blocks under the north-east shoulder of the town, cleared
// it, pasted three bunker templates into it and then swept it for water three more times,
// all triggered from a quest reward, because the coordinates the Act IV finale teleported
// eleven residents to were inside undisturbed stone.
//
// The chamber, its bunker rooms, its ceiling lanterns, the andesite panel the lever hangs
// on and the marked plinth the Works Waystone stands on are all built into the shipped
// world (valley_build.js groups act4_works, act4_works_light and day1_adit). The only way
// in is Tobin's fallen adit — forty blocks of cobblestone in a lined shaft off the East
// Lane verge — and mining those forty blocks IS Q65. Nothing here digs anything.
// -----------------------------------------------------------------------------

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

// WHAT USED TO BE HERE: groupOrigin() and runGroup(), which played a town-plan group —
// pads, templates, fills and all — from inside a finale or a scene. Both live in
// valley_build.js now and are reachable only from `/valley build`, which needs permission
// level 2 and is in no quest's reward list. What the finales still read out of the plan is
// where a PERSON stands: the plaza cells, the supper seats and the bunker floor cells, all
// of which are measurements of a world that is already built.

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
// Small helpers the five chains share.
// -----------------------------------------------------------------------------

// The thirty-nine posts on the road and in the town, in lighting order. The fortieth —
// Josie's porch — is deliberately not in here: it ships bare and Q90 is its lamp.
function roadLamps(v) {
  let out = []
  let all = v.C.LAMPS_ALL
  let porch = v.C.LAMPS_Q90
  for (let i = 0; i < all.length; i++) {
    let skip = false
    for (let j = 0; j < porch.length; j++) {
      if (all[i][0] === porch[j][0] && all[i][1] === porch[j][1] && all[i][2] === porch[j][2]) skip = true
    }
    if (!skip) out.push(all[i])
  }
  return out
}

// A fixture that is already standing, changed to a different STATE of itself — a candle
// holder lit, a campfire lit, a lamp burning. Not a build and not a replacement: the guard
// is that the block that is there has to be the block we expect, so a player who has taken
// the campfire out and put a chest in its place keeps the chest.
function swap(server, p, expect, state, what) {
  let level = null
  try { level = server.overworld() } catch (err) { level = null }
  if (level) {
    let held = String(level.getBlock(p[0], p[1], p[2]).id)
    if (held !== expect) {
      console.info('[valley] left alone: ' + (what || expect) + ' at ' + p.join(' ') +
                   ' — ' + held + ' is there instead')
      return false
    }
  }
  server.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + state)
  return true
}

// A resident stand out of the registry, by the group name plan_town.py solved it under.
function standAt(v, group) {
  let list = v.site('npc_stands') || []
  for (let i = 0; i < list.length; i++) if (list[i].group === group) return list[i].pos
  return null
}

// `easy_npc preset import` at an ABSOLUTE position.
function npcHere(name, p) {
  return npc(name, String(p[0]), String(p[1]), String(p[2]))
}

// =============================================================================
// The five chains. Each is a synchronous opening beat, an arrival beat two ticks later
// (see THE ARRIVAL BEAT above), and one or more delayed payoffs.
//
// Not one of them builds anything. Read the command lists: seasons, titles, sounds,
// bossbars, gives, tellraws, `setblock` of a lamp from dark to lit, `setblock` of a prop
// into a cell that put() has checked is air, and `easy_npc`/`tp` for the people.
// =============================================================================

// -----------------------------------------------------------------------------
// ACT I — The Thaw Fair. The square fills up and six lamps come on.
//
// The square, the six streets, the well, the four market carts, the inn, the mill and the
// two cottages have all been standing there, empty and dark, since before she logged in.
// The Fair is the first time anybody is IN them.
// -----------------------------------------------------------------------------
function finaleAct1(server, v) {
  if (beat(v, 'act1', 0)) {
    runSeg(server, v.anchor(), [
      'season set early_spring',
      'time set day',
      'weather clear',
      'title @a times 15 70 25',
      'title @a subtitle {"text":"Spring, Year One.","color":"gray"}',
      'title @a title {"text":"The Thaw Fair","color":"gold"}',
      'playsound minecraft:block.bell.use master @a ~0 ~1 ~0 1 1',
      'loot give @a loot valley:rewards/fair_basket',
      'give @a valley:scrip 25',
      'advancement grant @a only valley:journal/entry_2',
      'bossbar set valley:folk value 5',
      'worldborder set 3000 10'
    ])
    // The six lamps the quest text promises: the four on the plaza kerb, and the two at
    // the head of the High Street that Q7's own reward lit when the stake went in. Both
    // lists are registry routes, so the posts are the posts that are actually standing.
    v.lightLamps(v.C.LAMPS_FINALE, true)
    v.lightLamps(v.C.LAMPS_Q07, true)
    v.setLampsLit(6)
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
    // Q21 and Q27 both hang off this finale and both hand in a resident's token, so Nella
    // and Tobin arrive HERE, at the two places their own quest text names.
    let tobin = standAt(v, 'act1_tobin')
    if (tobin) runSeg(s, tobin, [npc('tobin', '~0', '~0', '~0')])
    let lake = v.mark('lake')
    if (lake) {
      // Nella, at the beached boat on the shingle. The boat, the fire, the barrel and the
      // pier itself are day-one; this lights her fire and sits her by it.
      let fire = v.site('lakefront.campfire')
      if (fire) swap(s, fire, 'minecraft:campfire',
                     'minecraft:campfire[lit=true]', "Nella's fire")
      runSeg(s, lake, [
        'summon minecraft:boat ~3 ~0 ~10 {Type:"oak"}',
        npc('nella', '~5', '~0', '~7')
      ])
    }
    v.sayAll('Tobin', "Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation.")
    v.delay(80, s2 => {
      v.sayAll('Marnie', "That door in her cellar. You've found it, then.")
      v.delay(40, s3 => v.sayAll('Marnie',
        "Everybody who has ever lived in that house has found it. Nobody has ever seen it open."))
    })
    v.addWorldStage('act2')
    endAct(v, 'act1')
  })
}

// -----------------------------------------------------------------------------
// ACT II — The Lantern Float. The pier fills up and the candles come on.
//
// The basin, the beach, the pier, its rails, its six candle holders, the twelve lantern
// rafts and the lily pads are all day one (valley_build.js, group day1_lakefront). This
// finale lights six candles and brings eight people down to the water.
// -----------------------------------------------------------------------------
function finaleAct2(server, v) {
  if (beat(v, 'act2', 0)) {
    let lake = v.mark('lake')
    runSeg(server, lake, [
      'season set mid_summer',
      'time set 18000',
      'weather clear',
      'title @a times 15 70 25',
      'title @a title {"text":"The Lantern Float","color":"aqua"}',
      'summon firework_rocket ~9 ~4 ~14 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1b,Colors:[I;16766720],FadeColors:[I;16777215]}]}}}}',
      'summon firework_rocket ~13 ~4 ~16 {LifeTime:22,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:4b,Colors:[I;3847130]}]}}}}',
      'playsound minecraft:entity.firework_rocket.launch master @a ~0 ~2 ~0 2 1',
      // the float itself: one drifting sheet of end_rod motes over the water, `force` so
      // it renders regardless of the viewer's particle setting.
      'particle minecraft:end_rod ~9 ~2 ~17 8 1 6 0.005 200 force @a',
      'give @a supplementaries:candle_holder 1',
      'give @a perfectplushies:frog_plushie 1',
      // the visible "the next tier is already in your hands" moment
      'give @a thermal:energy_cell 1',
      'give @a valley:scrip 25',
      'advancement grant @a only valley:journal/entry_3',
      'worldborder set 6000 10'
    ])
    // The six candle holders standing on the pier rail, lit. A `fill` of candle holders
    // writes the block's DEFAULT state, which is lit=false — which is how all thirty-four
    // of the originals ended up unlit at a festival called the Lantern Float.
    let candles = v.site('lakefront.candles') || []
    candles.forEach(c => swap(server, c, 'supplementaries:candle_holder',
      'supplementaries:candle_holder[lit=true,face=floor,facing=north,candles=3]',
      'pier candle'))
    runSeg(server, lake, [
      'playsound minecraft:block.candle.ambient master @a ~8 ~3 ~10 1 1.2'
    ])
  }

  // The arrival beat.
  arrival(v, 'act2', s => runSegArrive(s, v.mark('lake'), [
    // Nella already arrived with the Act I finale (Q21 needs her token). This re-import is
    // the same UUID, so it MOVES her to the Float rather than duplicating her. Wisp arrives
    // here for the first time. Both must be imported BEFORE the /tp block, or the tp
    // selects nothing.
    npc('nella', '~8', '~0', '~8'),
    npc('wisp', '~12', '~0', '~8'),
    // residents are teleported, never pathed (§7 rule 4)
    // y is ~0, not ~1: the lakefront's top course is lake.y-1, so a player standing on it
    // has their feet at lake.y. The old ~1 dropped six residents a block onto their own
    // festival.
    'tp @e[tag=npc_marnie,limit=1] ~4 ~0 ~6',
    'tp @e[tag=npc_bram,limit=1] ~6 ~0 ~6',
    'tp @e[tag=npc_oda,limit=1] ~4 ~0 ~8',
    'tp @e[tag=npc_nella,limit=1] ~8 ~0 ~8',
    'tp @e[tag=npc_halden,limit=1] ~6 ~0 ~8',
    'tp @e[tag=npc_pip,limit=1] ~10 ~0 ~7'
  ]), s => {
    // Tobin came down to the outcrop with the Act I finale (Q27 needs his token). Same
    // UUID, so this moves him into the square for the Float.
    runSeg(s, v.anchor(), [npcAt('tobin', stand(v, 15))])
    v.sayAll('Nella', 'You all came. Right.')
    v.delay(80, s2 => {
      v.sayAll('Halden',
        "Josie stood on this pier the last summer she had and told me she'd bought a book about turbines.")
      v.delay(40, s3 => v.sayAll('Halden',
        'I laughed at her. I would very much like that back.'))
    })
    v.addWorldStage('act3')
    endAct(v, 'act2')
  })
}

// -----------------------------------------------------------------------------
// ACT III — The Harvest Supper. Oda's door and the bell tower door come open.
//
// The store, the church and the long table have stood empty on the square since day one.
// The beat is that two of them are UNLOCKED, and eleven people sit down at the third.
// -----------------------------------------------------------------------------
function finaleAct3(server, v) {
  let HARVEST = sqScene('harvest')
  if (beat(v, 'act3', 0)) {
    // Oda opens her shop and Pip's bell tower is unlocked. Both doors are hanging in the
    // world already; openDoor reads their own facing and hinge back out of it.
    moveIn(server, v, 'store')
    moveIn(server, v, 'church')

    let a = v.anchor()
    // The harvest itself: two bales and two carved pumpkins, on the four cells the planner
    // solved for them, and ONLY where those cells are air.
    putAll(server, a, [
      [HARVEST.hay[0], 'minecraft:hay_block', 'harvest bale'],
      [HARVEST.hay[1], 'minecraft:hay_block', 'harvest bale'],
      [HARVEST.pumpkins[0], 'minecraft:carved_pumpkin[facing=south]', 'harvest pumpkin'],
      [HARVEST.pumpkins[1], 'minecraft:carved_pumpkin[facing=south]', 'harvest pumpkin']
    ])

    // The noticeboard is day one (group day1_board) and its sign is already standing in
    // this exact blockstate — so a /setblock is a NO-OP that silently throws the NBT away,
    // which is how four empty messages ended up on a finished world. `data merge block`
    // writes the block entity that is there.
    let bs = v.site('noticeboard.sign')
    if (bs) {
      server.runCommandSilent('data merge block ' + bs[0] + ' ' + bs[1] + ' ' + bs[2] +
        ' {front_text:{messages:[\'{"text":"Forty lamps."}\',\'{"text":"Fifteen people."}\',' +
        '\'{"text":"One winter that"}\',\'{"text":"nobody leaves."}\'],has_glowing_text:0b,color:"black"}}')
    }
    runSeg(server, a, [
      'season set mid_autumn',
      'time set 13000',
      'weather clear',
      'tellraw @a {"text":"On the noticeboard, in Oda\\u0027s hand: Forty lamps. Fifteen people. One winter that nobody leaves.","color":"gold"}',
      'bossbar set valley:folk value 11',
      'title @a times 20 90 30',
      'title @a title {"text":"The Harvest Supper","color":"gold"}',
      'playsound minecraft:block.note_block.bell master @a ~0 ~1 ~0 1 1.1',
      'loot give @a loot valley:rewards/harvest_gifts',
      'give @a valley:scrip 25',
      'advancement grant @a only valley:journal/entry_4'
    ])
  }

  // The arrival beat: eleven people sitting down, two ticks after the forceload has
  // actually landed.
  arrival(v, 'act3', s => runSegArrive(s, v.anchor(), [
    // Wisp brings three more Ribbits; this is their first appearance, so they are
    // imported, and everyone else is /tp'd (§7 rule 4).
    npcAt('ribbit_reed', seat(v, 7)),
    npcAt('ribbit_sedge', seat(v, 8)),
    npcAt('ribbit_mudlark', seat(v, 9)),
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

  // The turn, six seconds later. LAST BEAT: this is the only thing in the pack that grants
  // stage act4, so it is the thing act3 is latched on.
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

// -----------------------------------------------------------------------------
// ACT IV — The Longest Night. Bram pulls the lever and the road comes on.
//
// The Works chamber, its bunker rooms, its ceiling lanterns and the andesite panel the
// lever hangs on are all day one. Q65 mined the forty blocks of fall to get in and Q71 put
// the lever on the panel; this pulls it, and thirty-nine posts light in lighting order,
// one per tick, so from the doorway it reads as a wave going down the road.
// -----------------------------------------------------------------------------
function finaleAct4(server, v) {
  if (beat(v, 'act4', 0)) {
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

  // The arrival beat. The Works is fifteen blocks under the north-east shoulder of the
  // town, so its chunks are the coldest in the act — exactly the case where a tp in the
  // forceload's own tick finds nothing at all.
  arrival(v, 'act4', s => runSegArrive(s, v.mark('works'), [
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

  // Four seconds later, the instant. NPCs cannot interact with blocks, so the lever is a
  // setblock and Bram is narration.
  v.delay(80, s => {
    if (!beat(v, 'act4', 1)) return
    let works = v.mark('works')
    let lever = v.site('works.lever')
    if (lever) {
      // Q71 set this lever down unpowered on the andesite panel the world shipped with. If
      // it is there, this throws it; if the player has taken it, put() leaves the cell
      // alone and the sweep below happens anyway, because the story does not stop for a
      // missing lever.
      swap(s, lever, 'minecraft:lever',
           'minecraft:lever[face=wall,facing=south,powered=true]', 'the Works lever')
      put(s, lever, 'minecraft:lever[face=wall,facing=south,powered=true]', 'the Works lever')
    }
    runSeg(s, works, ['particle minecraft:cloud ~2 ~3 ~2 1 1 1 0.02 60 force @a'])

    let lamps = roadLamps(v)

    // THE FALSE START. The six nearest posts come up, hold, and go out again: a cold
    // coolant line, nothing more. Nobody is in danger, nothing can fail, and no input is
    // asked for. The point is two seconds of held breath so Bram's "Well." lands on the
    // far side of a silence.
    let six = lamps.slice(0, 6)
    v.lightLamps(six, true)
    v.delay(16, srv => {
      six.forEach(p => srv.runCommandSilent(
        'setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_DARK))
      runSeg(srv, works, ['playsound minecraft:block.beacon.deactivate master @a ~0 ~1 ~0 2 0.8'])
      v.sayAll('Tobin', 'Cold line. That is all that is. It is only cold.')
    })
    v.delay(30, srv => v.sayAll('Bram', 'Give it a second.'))

    // Stage B, at +56: the real sweep. Beat 2 is v.delay(200) from the finale's start, i.e.
    // 120 ticks after this beat's own delay(80); +56 plus a sweep of at most 39 ticks ends
    // by +95, leaving 25 ticks of margin.
    v.delay(56, srv => {
      runSeg(srv, works, [
        'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 3 0.7',
        'playsound minecraft:block.conduit.activate master @a ~0 ~1 ~0 2 1'
      ])
      v.lightLamps(lamps, true)
      v.setLampsLit(lamps.length)
      // The Hearth relights, and the bathhouse starts steaming.
      let inn = v.mark('inn')
      if (inn) swap(srv, inn, 'minecraft:campfire', 'minecraft:campfire[lit=true]', 'the Hearth')
      let bath = v.mark('bathhouse')
      if (bath) srv.runCommandSilent('particle minecraft:cloud ' + bath[0] + ' ' + (bath[1] + 2) + ' ' + bath[2] + ' 2 1 2 0.02 120 force @a')
    })

    runSeg(s, works, [
      'summon firework_rocket ~0 ~6 ~0 {LifeTime:26,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;16766720,3847130],FadeColors:[I;16777215]}]}}}}',
      'summon firework_rocket ~-5 ~5 ~4 {LifeTime:32,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:4b,Colors:[I;16766720]}]}}}}',
      'summon firework_rocket ~5 ~5 ~-4 {LifeTime:38,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;3847130],FadeColors:[I;16766720]}]}}}}',
      'playsound minecraft:entity.firework_rocket.launch master @a ~0 ~2 ~0 3 1',
      'give @a valley:scrip 25',
      'advancement grant @a only valley:journal/entry_5'
    ])
    v.delay(62, srv => v.sayAll('Bram', 'Well.'))
    v.addWorldStage('greenhouse_warm')
    v.addWorldStage('act5')
  })

  // The turn, six seconds after the lever, the way Act III turns after the Supper. Without
  // this nothing sets spring until Q91 and the whole of Act V plays in mid-winter.
  // LAST BEAT.
  v.delay(200, s => {
    if (!beat(v, 'act4', 2)) return
    runSeg(s, v.mark('works'), [
      'season set early_spring',
      'weather clear',
      'particle minecraft:falling_water ~0 ~5 ~0 8 3 8 0.01 160 force @a',
      'playsound minecraft:block.amethyst_block.chime master @a ~0 ~1 ~0 2 1.2'
    ])
    // Backstop for the sweep. The one-post-per-tick wave above is scheduled on the
    // in-memory queue, so a /stop two seconds after the lever would leave the far end of
    // the road dark with beat 1 already latched. Same setblocks, no particles, no sound.
    roadLamps(v).forEach(p => {
      s.runCommandSilent('setblock ' + p[0] + ' ' + p[1] + ' ' + p[2] + ' ' + LAMP_LIT)
    })
    v.setLampsLit(39)
    v.sayAll('Marnie', "Snow's off the ridge by morning. It always turns the night after the longest one.")
    v.delay(60, s2 => {
      v.sayAll('Oda',
        "There's a fire on the ridge road tonight — three miles out, well off the tree line, and somebody is walking in.")
      v.delay(40, s3 => v.sayAll('Oda',
        'Nobody has walked IN to this valley in eleven years. Put the kettle on.'))
    })
    endAct(v, 'act4')
  })
}

// -----------------------------------------------------------------------------
// ACT V — Founder's Day. Three people walk up the road and move into three houses
// that have been standing empty since the first second.
//
// The Town Hall and Tess's, Mab's and Corin's houses are all day one, finished, shut and
// dark. This act opens four doors, puts a light in three windows and walks three people
// through them, which is the entire difference between an empty valley and a town.
// -----------------------------------------------------------------------------
function finaleAct5(server, v) {
  if (beat(v, 'act5', 0)) {
    let a = v.anchor()
    // The Town Hall, unlocked at last.
    moveIn(server, v, 'town_hall')
    // The signpost at the head of the square. `put` rather than `setblock`, so a re-run —
    // or a player who has put her own sign there — is left alone.
    put(server, [a[0], a[1] + 1, a[2] - 3],
        'minecraft:oak_sign{front_text:{messages:[\'{"text":"LITTLE KETTLE"}\',' +
        '\'{"text":"VALLEY"}\',\'{"text":"pop. 15"}\',\'{"text":"est. again"}\']}}',
        'the valley signpost')
    runSeg(server, a, [
      'season set early_spring',
      'time set noon',
      'weather clear',
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
    v.setLampsLit(40)
  }

  // The arrival beat: the three newcomers come up the High Street the town paved at Q19 —
  // a short approach, because long-distance pathing does not work (§12.3) — and the fifteen
  // who already live here stand on their Founder's Day marks.
  arrival(v, 'act5', s => runSegArrive(s, v.anchor(), [
    npc('newcomer_tess', '~0', '~1', '~24'),
    npc('newcomer_mab', '~2', '~1', '~26'),
    npc('newcomer_corin', '~-2', '~1', '~26'),
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
  ]), s => {
    // ...and then they move in. Three doors that have been shut since the first second come
    // open, three lanterns go up over three doorsteps, and the three of them are standing
    // on their own steps forty ticks later. Nothing is built: the houses were finished
    // before the player had a name.
    v.delay(40, srv => {
      if (!beat(v, 'act5', 'in')) return
      let names = [['newcomer_tess', 'tess'], ['newcomer_mab', 'mab'], ['newcomer_corin', 'corin']]
      names.forEach((n, i) => {
        v.delay(i * 20, s2 => {
          let door = v.site('doors.' + n[0])
          if (!door) return
          moveIn(s2, v, n[0])
          s2.runCommandSilent('tp @e[tag=npc_' + n[0] + ',limit=1] ' +
            door[0] + ' ' + door[1] + ' ' + (door[2] + 1))
        })
      })
      v.delay(80, s2 => v.sayAll('Marnie',
        'Three doors that have not been opened in eleven years, all in one afternoon. I need to sit down.'))
    })
  })

  // Halden reads the last page of Josie's journal: six lines, each five seconds after the
  // last. Line i fires at 100 + i*100 under beat(v,'act5', 1+i), and the final latch is
  // 1 + page.length at 100 + page.length*100 — six lines end at tick 700, inside
  // FINALE_RELEASE.act5 = 720. Do not add a seventh without moving that release.
  let page = [
    "Last one. The writing's gone shaky, so I'll be brief, which Marnie will tell you is a first.",
    "If the lights are on out there, it worked and it wasn't me. I only ever got this valley to hold on. You got it to stay.",
    "So: the wheel goes counter-clockwise, the third lamp post leans and always has, and Marnie takes her tea far too strong.",
    "Don't turn this into a monument. Don't put my name on the square. Put a bell there, and ring it when supper's ready.",
    "Somebody always comes up the road when there's smoke. Go and meet the next one. Bring bread. Pretend you were passing.",
    "There's a lamp post on my porch with nothing on it. I'd like to be on the line."
  ]
  page.forEach((line, i) => {
    v.delay(100 + i * 100, s => {
      if (!beat(v, 'act5', 1 + i)) return
      v.sayAll('Halden', line)
    })
  })

  // LAST BEAT: the world border comes off here and nowhere else.
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
// /valley scene <key> — the set changes (§11 "every reward calls it").
//
// A scene is the smallest visible change a quest's own text promises, and — like a finale —
// it may only ADD. Every building these used to raise is in the shipped world:
//
//   bram / inn / marnie / pip   act1_mill, act1_inn, act1_marnie, act1_pip: standing, shut
//   cellar                      day1_cellar: forty blocks of gravel and a sealed iron door
//   square_path                 day1_board and day1_road: the socket, the square, the road
//   q60 / q64                   act4_greenhouse_shell and _glaze: a shell with six frames
//   q65                         act4_works + day1_adit: a chamber, and forty blocks of fall
//   q72                         act4_bathhouse: a stone-and-spruce building with a tank
//   q70a / q73                  act4_beds, act4_bram_chair: beds and a chair in the inn
//
// So what is left in here is what a scene should always have been: a door opened, a light
// lit, a person moved, four or five props set down into cells that put() has checked are
// empty, and one line in the right resident's register.
//
// Rules:
//   * `origin` names a mark, or 'anchor' / 'home'; every command is a `~` offset from it.
//   * `put` is a list of [offset, block, label] the guard runs — never a fill, never a
//     template.
//   * `doors` is a list of registry door keys to open.
//   * `lamps` is a lamp ROUTE name to light.
//   * `run` is for the two scenes that need runtime state.
//   * an unknown key is a friendly message, never an exception (§P3).
//   * scenes are NOT latched: put() makes a re-run harmless, which is what once:true was
//     protecting against when a scene pasted a template over a room the player had filled.
// =============================================================================
const SCENES = {

  // Q8's reward — Bram is at the mill. The mill, its snapped axle and its race have been
  // standing there since day one; Q12 sends the player to him and Bram's own
  // ON_INTERACTION is the only source of valley:token_bram.
  bram: {
    origin: 'mill',
    who: ['Bram', "Axle's snapped. It's been snapped four years. You'll want to see it."],
    run: function (server, v) {
      let stand = standAt(v, 'act1_mill')
      if (stand) runSeg(server, stand, [npc('bram', '~0', '~0', '~0')])
      moveIn(server, v, 'mill')
    }
  },

  // Q8's other reward — the inn opens. Marnie's Hearth is the tavern's own campfire and it
  // has been cold since Josie died; this is the first time it is lit.
  inn: {
    origin: 'inn',
    who: ['Marnie', "Room's been made up for eleven years. Somebody may as well be in it."],
    doors: ['inn'],
    run: function (server, v) {
      let inn = v.mark('inn')
      if (inn) swap(server, inn, 'minecraft:campfire', 'minecraft:campfire[lit=true]', 'the Hearth')
    }
  },

  // Q10's reward — the coop, inside the pen the cottage yard already has marked out in
  // cobblestone footings. Four props, and only where the cells are empty.
  coop: {
    origin: 'home',
    who: ['Marnie', "Straw in the box, water by the gate, and don't name them. You'll name them."],
    put: [
      [[4, -1, -9], 'minecraft:hay_block', 'nesting box'],
      [[4, 0, -9], 'handcrafted:oak_nightstand', 'nesting box'],
      [[3, 0, -9], 'minecraft:oak_fence', 'coop post'],
      [[3, 1, -9], 'minecraft:lantern[hanging=false]', 'coop lamp'],
      [[5, 0, -9], 'minecraft:composter', 'coop composter']
    ]
  },

  // Q7's reward — the stake is in Bram's socket, and the two posts at the head of the High
  // Street come on. Nothing is paved: the square, the road and the socket are day one.
  square_path: {
    origin: 'anchor',
    lamps: 'q07',
    who: ['Josie', 'That is the flat Bram surveyed twice and never staked. It is a town now, whether or not anybody lives in it.'],
    run: function (server, v) {
      v.setLampsLit(2)
      server.runCommandSilent('particle minecraft:happy_villager ' +
        v.anchor().join(' ') + ' 3 1 3 0.01 80 force @a')
    }
  },

  // Q5's reward — the cellar. The room, the flight, the forty blocks of gravel, the chalk,
  // the tool chest and the sealed iron door are ALL day one (valley_build.js, day1_cellar);
  // digging the gravel out is the quest. This lights the room she has just broken into.
  cellar: {
    origin: 'home',
    noAnchor: true,
    who: ['Josie', "Not yet. I'll explain when you have people who can help you carry it."],
    run: function (server, v) {
      let c = v.site('cellar')
      if (!c) return
      server.runCommandSilent('particle minecraft:end_rod ' + c.stand[0] + ' ' +
        (c.stand[1] + 1) + ' ' + c.stand[2] + ' 1 1 1 0.01 60 force @a')
      server.runCommandSilent('playsound minecraft:block.chain.place master @a ' +
        c.stand.join(' ') + ' 1 0.7')
    }
  },

  // Q8's third reward — Marnie moves into the inn she has kept with no guests.
  marnie: {
    origin: 'anchor',
    who: ['Marnie', "You lit a fire in that chimney. I saw it from my own window and I have not seen it in eleven years."],
    run: function (server, v) {
      let stand = standAt(v, 'act1_marnie')
      if (stand) runSeg(server, stand, [npc('marnie', '~0', '~0', '~0')])
      moveIn(server, v, 'marnie_house')
    }
  },

  // Q11's reward — Pip moves in next door to his aunt, with the duck.
  pip: {
    origin: 'anchor',
    who: ['Pip', "That's MY house. That one. With the door. I get a door."],
    run: function (server, v) {
      let stand = standAt(v, 'act1_pip')
      if (stand) {
        runSeg(server, stand, [
          npc('pip', '~0', '~0', '~0'),
          'summon duckling:duck ~1 ~0 ~0 {PersistenceRequired:1b,NoAI:1b}'
        ])
      }
      moveIn(server, v, 'pip_house')
    }
  },

  // Q58 — the four firewood stacks. Wisp lights the way down the frozen river: four posts
  // that have stood dark on the bank since day one (group day1_wisp_posts), lit here.
  q58: {
    origin: 'anchor',
    who: ['Wisp', 'Warm inn. Warm soup. I light the way, you walk it. That is a fair trade.'],
    run: function (server, v) {
      let posts = v.site('wisp_posts') || []
      v.lightLamps(posts, true)
      runSeg(server, v.anchor(), [
        'particle minecraft:end_rod ~0 ~3 ~24 1 1 8 0.01 80 force @a',
        'playsound minecraft:block.amethyst_block.chime master @a ~0 ~1 ~0 2 1.2'
      ])
    }
  },

  // Q59 — the reed village comes in. Four Ribbits move into town for good; Puddle's first
  // appearance is here rather than at the Act IV finale, which re-imports the same UUID
  // and therefore just moves him.
  q59: {
    origin: 'anchor',
    who: ['Wisp', 'The reeds is all ice now, and we are four with no roof. Can we be your neighbours nearer?'],
    cmds: function () {
      let c = sqScene('ribbit_camp')
      let out = []
      let who = ['ribbit_reed', 'ribbit_sedge', 'ribbit_mudlark', 'ribbit_puddle']
      who.forEach((n, i) => out.push(npcAt(n, c.stands[i % c.stands.length])))
      out.push('bossbar set valley:folk value 12')
      out.push('playsound minecraft:entity.frog.long_jump master @a ~0 ~1 ~0 1 1')
      return out
    },
    putFn: function () {
      let c = sqScene('ribbit_camp')
      return [
        [c.campfire, 'minecraft:campfire[lit=true]', 'the camp fire'],
        [c.post, 'minecraft:oak_fence', 'the camp post'],
        [[c.post[0], c.post[1] + 1, c.post[2]], LAMP_LIT, 'the camp lamp']
      ]
    }
  },

  // Q60 — soup for a full room. The Hearth relights and the greenhouse is unlocked: its
  // shell, its six empty frames and its bench have stood on the square since day one, and
  // Q64 is what glazes them, with the glass this quest hands over.
  q60: {
    origin: 'anchor',
    who: ['Marnie', "I have fed this room for thirty years, and tonight I'm sitting down at it. Don't make a thing of it."],
    run: function (server, v) {
      let inn = v.mark('inn')
      if (inn) {
        swap(server, inn, 'minecraft:campfire', 'minecraft:campfire[lit=true]', 'the Hearth')
        runSeg(server, inn, [
          'particle minecraft:campfire_cosy_smoke ~0 ~2 ~0 0.3 0.3 0.3 0.01 40 force @a',
          'playsound minecraft:block.campfire.crackle master @a ~0 ~1 ~0 2 1'
        ])
      }
      let gh = v.mark('greenhouse')
      if (gh) {
        put(server, [gh[0], gh[1] + 1, gh[2]], 'minecraft:lantern[hanging=false]', 'greenhouse lamp')
        server.runCommandSilent('particle minecraft:happy_villager ' + gh.join(' ') +
                                ' 4 2 4 0.01 80 force @a')
      }
    }
  },

  // Q62 — Halden's rounds. Eight tonics, eight houses, nobody gets sick. The still stands
  // on the square's own paving, on cells the planner solved against the well, the four
  // market carts, the supper table, the streets and every lamp post.
  q62: {
    origin: 'anchor',
    who: ['Halden', 'Eight people, eight bottles. I would go round myself, but they talk to you more than they talk to me.'],
    putFn: function () {
      let c = sqScene('still')
      return [
        [c.cupboard, 'handcrafted:oak_cupboard', "Halden's cupboard"],
        [c.brewing_stand, 'minecraft:brewing_stand', 'the brewing stand'],
        [c.cauldron, 'minecraft:water_cauldron[level=3]', 'the cauldron'],
        [c.post, 'minecraft:oak_fence', 'the still post'],
        [[c.post[0], c.post[1] + 1, c.post[2]], 'minecraft:lantern[hanging=false]', 'the still lamp']
      ]
    },
    cmds: [
      'effect give @a minecraft:regeneration 20 0 true',
      'particle minecraft:happy_villager ~0 ~2 ~0 6 2 6 0.01 120 force @a',
      'playsound minecraft:block.brewing_stand.brew master @a ~0 ~1 ~0 2 1'
    ]
  },

  // Q64 — the cold frame. The player has just glazed the shell herself: six windows into
  // six frames, the cottage door on its hinges, eight planters on the marked bench. This is
  // the room warming up.
  q64: {
    origin: 'greenhouse',
    who: ['Nella', "Nothing grows in it yet. I'll sit in it anyway — it's the only quiet room in town."],
    cmds: [
      'particle minecraft:happy_villager ~0 ~2 ~0 4 2 4 0.01 120 force @a',
      'playsound minecraft:block.glass.place master @a ~0 ~1 ~0 2 1.2'
    ]
  },

  // Q65 — open the Works. The player has just mined forty blocks of fall out of Tobin's
  // adit and put the Waystone on the marked plinth. The room lights, and there is a saddled
  // horse in the stable — the quest's own reward line, made literally true.
  q65: {
    origin: 'works',
    who: ['Tobin', 'Forty blocks of fallen adit. I paced it twice. Behind it is the entire works, and I have not slept.'],
    put: [
      [[-3, 0, -3], 'minecraft:smithing_table', "Josie's bench"],
      [[3, 0, -3], 'minecraft:barrel[facing=up]', "Josie's barrel"],
      [[5, 0, 5], 'minecraft:hay_block', 'the stable'],
      [[6, 0, 5], 'minecraft:hay_block', 'the stable'],
      [[5, 0, 6], 'minecraft:hay_block', 'the stable'],
      [[6, 0, 6], 'minecraft:hay_block', 'the stable']
    ],
    cmds: [
      'summon minecraft:horse ~6 ~1 ~6 {Tame:1b,PersistenceRequired:1b,SaddleItem:{id:"minecraft:saddle",Count:1b}}',
      'playsound minecraft:block.beacon.power_select master @a ~0 ~1 ~0 2 0.8'
    ],
    run: function (server, v) {
      // the five ceiling lanterns act4_works_light hung are already burning; this is the
      // moment the room is seen, so the sparks go where the player is standing.
      let w = v.mark('works')
      if (w) server.runCommandSilent('particle minecraft:end_rod ' + w[0] + ' ' + (w[1] + 2) +
                                     ' ' + w[2] + ' 5 2 5 0.01 200 force @a')
    }
  },

  // Q66 — the grid. Duct from the mill to the Works, two cells at this end.
  q66: {
    origin: 'works',
    who: ['Bram', "Mill makes it, Works needs it, duct in between. That's the whole job."],
    put: [
      [[-2, 0, -4], 'thermal:energy_cell', 'the west cell'],
      [[2, 0, -4], 'thermal:energy_cell', 'the east cell'],
      [[-1, 0, -4], 'thermal:energy_duct', 'the duct'],
      [[0, 0, -4], 'thermal:energy_duct', 'the duct'],
      [[1, 0, -4], 'thermal:energy_duct', 'the duct'],
      [[0, 1, -4], 'minecraft:redstone_lamp[lit=true]', 'the grid lamp']
    ],
    cmds: [
      'particle minecraft:electric_spark ~0 ~1 ~-4 0.6 0.6 0.6 0.02 60 force @a',
      'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 1 1.4'
    ]
  },

  // Q70a — the wool line. Three blankets, three beds, three empty houses that will not be
  // empty in spring: Tess, Mab and Corin arrive in Act V. The beds are in the inn's common
  // room already (act4_beds); this is Marnie turning them down.
  q70a: {
    origin: 'inn',
    who: ['Marnie', 'Three empty houses, three beds, three blankets. I want them turned down before anybody gets to the top of the road.'],
    cmds: [
      'particle minecraft:happy_villager ~0 ~2 ~0 4 1 4 0.01 60 force @a',
      'playsound minecraft:block.wool.place master @a ~0 ~1 ~0 1 1.1'
    ]
  },

  // Q54 — the Kettle Plate is in Halden's hands, and the iron door in the cellar comes
  // open. This is the one door in the pack that is meant to be a lock: it has been shut
  // since before the player arrived, nothing in the world can open it, and this is the
  // only thing that ever does. Halden reads the hand; the door turns.
  q54: {
    origin: 'home',
    noAnchor: true,
    who: ['Halden', "It's a parts list. It has always been a parts list. She wasn't digging a mine."],
    run: function (server, v) {
      let c = v.site('cellar')
      if (!c || !c.door) { console.warn('[valley] scene q54: no cellar door in the registry'); return }
      // Turn the lock FIRST. An iron door cannot be held open by a setblock — vanilla
      // recomputes OPEN from the redstone signal for any door that cannot be opened by hand
      // — so the block that holds this one open is a buried redstone block behind it, which
      // the world shipped as a block of rock for exactly this moment.
      if (c.lock) {
        swap(server, c.lock, 'minecraft:stone', 'minecraft:redstone_block', "Josie's lock")
        swap(server, [c.lock[0], c.lock[1] + 1, c.lock[2]], 'minecraft:stone',
             'minecraft:redstone_block', "Josie's lock")
      }
      openDoor(server, c.door, true)
      server.runCommandSilent('playsound minecraft:block.iron_door.open master @a ' +
                              c.door.join(' ') + ' 2 0.7')
      server.runCommandSilent('particle minecraft:end_rod ' + c.door[0] + ' ' +
                              (c.door[1] + 1) + ' ' + c.door[2] + ' 0.3 0.6 0.3 0.01 40 force @a')
    }
  },

  // Q76 — year two. Oda rewrites the noticeboard, and the destination line stays word for
  // word, because rule 3 says it is never paraphrased.
  q76: {
    origin: 'anchor',
    who: ['Oda', "Year two on the board. Longer list than last spring, and the bottom four lines are still in Josie's hand."],
    run: function (server, v) {
      // Same trap as finaleAct3: the sign is already standing in this exact blockstate, so
      // /setblock refuses and throws the NBT away. Write the block entity instead.
      let bs = v.site('noticeboard.sign')
      if (bs) {
        server.runCommandSilent('data merge block ' + bs[0] + ' ' + bs[1] + ' ' + bs[2] +
          ' {front_text:{messages:[\'{"text":"Forty lamps."}\',\'{"text":"Fifteen people."}\',' +
          '\'{"text":"One winter that"}\',\'{"text":"nobody leaves."}\'],has_glowing_text:0b,color:"black"}}')
        server.runCommandSilent('playsound minecraft:block.wood.place master @a ' +
                                bs.join(' ') + ' 1 1.2')
      }
      server.runCommandSilent('tellraw @a {"text":"On the noticeboard, in Oda\\u0027s hand: Forty lamps. Fifteen people. One winter that nobody leaves.","color":"gold"}')
    }
  },

  // Q71 — the turbine holds 1,800 RPM. The lever goes onto the andesite panel the Works
  // shipped with, UNPOWERED: pulling it is the Act IV finale.
  q71: {
    origin: 'works',
    who: ['Bram', "Crate's got what it's got — blades, coils, casing. Eighteen hundred RPM under load, and hold it there."],
    put: [
      [[0, 2, 0], 'minecraft:lever[face=wall,facing=south,powered=false]', 'the Works lever'],
      [[-1, 2, 0], 'minecraft:copper_block', 'the lever housing'],
      [[1, 2, 0], 'minecraft:copper_block', 'the lever housing'],
      // A STANDING sign on the copper block, not a wall sign at [0,3,0]: works + [0,3,0] is
      // one of the five ceiling lanterns act4_works_light hung, so the note was landing on a
      // lit lantern and being left alone by the guard every single time.
      [[-1, 3, 0], 'minecraft:oak_sign[rotation=8]{front_text:{messages:[\'{"text":"1800 RPM"}\',\'{"text":"under load"}\',\'{"text":"- J.K."}\',\'{"text":""}\']}}', "Josie's note"]
    ],
    cmds: ['playsound minecraft:block.note_block.bit master @a ~0 ~1 ~0 2 1.6']
  },

  // Q72 — the coolant loop. Josie's rule: the waste heat goes to the town. The greenhouse
  // heaters and the bathhouse tank are plumbed in the shipped world; this is the moment
  // they come up warm.
  q72: {
    origin: 'anchor',
    who: ['Josie', 'The waste heat goes to the town, not the sky. Anything else is a fire you paid for twice.'],
    run: function (server, v) {
      let gh = v.mark('greenhouse')
      let bh = v.mark('bathhouse')
      if (gh) server.runCommandSilent('particle minecraft:cloud ' + gh[0] + ' ' + (gh[1] + 2) +
                                      ' ' + gh[2] + ' 3 1 2 0.01 120 force @a')
      if (bh) {
        server.runCommandSilent('particle minecraft:cloud ' + bh[0] + ' ' + (bh[1] + 2) +
                                ' ' + bh[2] + ' 2 1 2 0.02 160 force @a')
        put(server, [bh[0], bh[1], bh[2]], 'minecraft:lantern[hanging=false]', 'bathhouse lamp')
      }
      server.runCommandSilent('playsound minecraft:block.lava.ambient master @a ' +
                              v.anchor().join(' ') + ' 1 1.4')
    }
  },

  // Q73 — bring Bram. He says no. You bring him anyway. The chair and the table are in the
  // inn already (act4_bram_chair); this puts him in the chair.
  q73: {
    origin: 'inn',
    who: ['Bram', "The mill needs me at midnight in January, is the thing. ... Fine. One cocoa."],
    cmds: ['tp @e[tag=npc_bram,limit=1] ~0 ~1 ~-3',
           'playsound minecraft:entity.villager.yes master @a ~0 ~1 ~0 1 0.9']
  },

  // Q74 — the second stretch. The player has walked the whole line, mill to square to lake
  // to farm, and the duct has run itself along it. This is the duct arriving: the posts stay
  // DARK, because nothing on this road lights until Bram pulls the lever.
  q74: {
    origin: 'anchor',
    home: true,
    who: ['Josie', 'Forty posts, mill to square to lake. I counted them on my fingers before I could count to forty.'],
    run: function (server, v) {
      v.lampsOnRoute('q74').forEach(p => {
        server.runCommandSilent('particle minecraft:electric_spark ' +
          p[0] + ' ' + (p[1] + 1) + ' ' + p[2] + ' 0.2 0.4 0.2 0.01 6 force @a')
      })
      // The fortieth post is bare and stays bare: it is on Josie's porch and Q90 is its
      // lamp. This is the only place in the pack that says so out loud.
      let porch = v.C.LAMPS_Q90[0]
      if (porch) {
        server.runCommandSilent('particle minecraft:end_rod ' + porch[0] + ' ' + porch[1] +
                                ' ' + porch[2] + ' 0.2 0.4 0.2 0.01 20 force @a')
      }
      server.runCommandSilent('playsound minecraft:block.chain.place master @a ' +
                              v.anchor().join(' ') + ' 1 1')
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

// A resident teleport: the one kind of command in a scene that silently does nothing when
// its target is in a chunk the server has been told to load and has not loaded yet. (Each
// KubeJS server script has its OWN scope — proved by this file's own log, which spent a
// whole run throwing `ReferenceError: "isNpcTp" is not defined` into eight scenes after the
// group runner moved to valley_build.js — so a copy over there is not a copy here.)
function isNpcTp(c) {
  return typeof c === 'string' && c.indexOf('tp @e[tag=npc_') === 0
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

  // Every mark is a registry constant, so `origin` can only fail if valley_sites.js did
  // not load — in which case nothing in the pack works and the log already says so.
  let origin = originPos(v, scene.origin)
  if (!origin) {
    console.warn('[valley] scene ' + key + ': no origin "' + scene.origin + '"; nothing played')
    msg(source, Text.gray('[valley] scene ' + key + ' has nothing to measure from.'))
    return 0
  }

  let server = source.server

  // Hold the chunks. Every command below runs as the SERVER, from 0 0 0, so a setblock into
  // a chunk nobody is standing in is refused and the scene "plays" and does nothing. Proved
  // live: SCENES.q73's `tp @e[tag=npc_bram]` returned 0 from a console replay and Bram
  // never sat down.
  let sr = [origin]
  let a = v.anchor()
  if (a) sr.push(a)
  if (scene.home) { let h = v.home(); if (h) sr.push(h) }
  sr = sr.filter(p => p)
  forceload(server, sr, 'add')

  // Resident teleports are collected rather than run in this tick: the forceload above is
  // asynchronous, so a `tp @e[tag=npc_*]` issued now matches nothing and returns 0.
  let pending = []
  try {
    // 1. doors. Every one of them is hanging in the world; this flips `open`.
    if (scene.doors) scene.doors.forEach(d => moveIn(server, v, d))

    // 2. furniture, through the air guard. `put` is a fixed list; `putFn` is for the three
    //    scenes whose cells the planner solves against the square's own furniture.
    let plist = scene.put || null
    if (!plist && scene.putFn) plist = scene.putFn(v)
    if (plist) {
      let n = putAll(server, origin, plist)
      console.info('[valley] scene ' + key + ': ' + n + ' of ' + plist.length +
                   ' props set down (the rest were already occupied)')
    }

    // 3. a lamp route, lit.
    if (scene.lamps) v.lightLamps(v.lampsOnRoute(scene.lamps), true)

    // 4. the rest: titles, sounds, particles, gives, NPC imports and teleports.
    let cl = (typeof scene.cmds === 'function') ? scene.cmds(v) : scene.cmds
    if (cl) runSegSplit(server, origin, cl, pending)

    // 5. whatever needs runtime state.
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
// /valley anchor set — the op override, and nothing else.
//
// WHAT USED TO BE HERE: anchorHearth() and a clearance rule that refused any anchor whose
// town footprint would land on the homestead, because the anchor was a decision the player
// made with a stake in Act I and the whole valley was measured off it. The anchor is a
// constant in valley_sites.json now. This command writes a persistentData override that
// v.anchor() reads FIRST, which is how a broken world gets nudged by hand; it is not
// reachable from any quest and it needs permission level 2.
// -----------------------------------------------------------------------------
function anchorSetCmd(source, x, y, z, force) {
  let v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }
  let reg = v.site('anchor')
  v.setAnchor(x, y, z)
  msg(source, Text.gold('Town Anchor set to ' + x + ' ' + y + ' ' + z +
      (reg ? '  (the registry says ' + reg.join(' ') + ')' : '')))
  return 1
}

// =============================================================================
// /valley build <group|all> — BUILD TIME ONLY, and it lives somewhere else.
//
// The pads, the templates, the fills and the group runner are all in valley_build.js, which
// is the only file in the pack allowed to cut the world. This is the command that calls it;
// it needs permission level 2 and is in no quest's reward list. scratch/master_build.sh
// runs `/valley build all` exactly once, into the master save, and it is never run in play.
// =============================================================================
function buildBridge() {
  return (typeof global.valleyBuild !== 'undefined') ? global.valleyBuild : null
}

function buildGroup(source, key) {
  let b = buildBridge()
  if (!b) { msg(source, Text.red('valley_build.js is not loaded.')); return 0 }
  return b.group(source, key)
}

function buildAll(source) {
  let b = buildBridge()
  if (!b) { msg(source, Text.red('valley_build.js is not loaded.')); return 0 }
  return b.all(source)
}

function buildOrder() {
  let b = buildBridge()
  return b ? b.order() : []
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

      // --- /valley build <group|all> --------------------------------------
      // Build-time only. See the BUILD_ORDER block above.
      .then(Commands.literal('build').requires(src => src.hasPermission(2))
        .then(Commands.literal('all').executes(ctx => buildAll(ctx.source)))
        .then(Commands.literal('list').executes(ctx => {
          let bo = buildOrder()
          msg(ctx.source, Text.gold('build order (' + bo.length + '): ' + bo.join(', ')))
          return 1
        }))
        .then(Commands.argument('group', Arguments.WORD.create(event))
          .executes(ctx => buildGroup(ctx.source,
            Arguments.WORD.getResult(ctx, 'group')))))

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
      // --- /valley intro: face the path, the title card, the compass again ---
      .then(Commands.literal('intro').executes(ctx => {
        let pl = ctx.source.player
        if (!pl) { ctx.source.sendFailure(Component.literal('Only a player can be turned around.')); return 0 }
        global.valley.orient(ctx.source.server, pl)
        return 1
      }))
      // --- /valley book: the Quest Book item, for a lost bag or an unbound key --
      .then(Commands.literal('book').executes(ctx => {
        let pl = ctx.source.player
        if (!pl) { ctx.source.sendFailure(Component.literal('Only a player can be handed a book.')); return 0 }
        pl.give(Item.of('ftbquests:book'))
        ctx.source.sendSuccess(Component.literal('The Quest Book is in your bag. Right-click it.'), false)
        return 1
      }))
      // --- /valley letter: a fresh copy of Josie's letter for whoever asks ----
      .then(Commands.literal('letter').executes(ctx => {
        let pl = ctx.source.player
        if (!pl) { ctx.source.sendFailure(Component.literal('Only a player can be handed a letter.')); return 0 }
        pl.give(global.valley.letter())
        ctx.source.sendSuccess(Component.literal('Josie\'s letter is in your bag.'), false)
        return 1
      }))

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
    v.say(player, 'Oda', (STANDING_WHO[key] || 'That') + "'s account is closed. That's " +
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
