// =============================================================================
// valley_build.js — Little Kettle Valley: the BUILD-TIME placer.
//
// This file exists so that valley_finales.js does not.
//
// The pack ships ONE hand-built world (docs/transitions-design.md architecture A). Every
// building, every street, the pier, the greenhouse and bathhouse shells, the sealed Works,
// the forty lamp posts and the three empty newcomer houses are already standing when the
// player joins, and the story only ever ADDS to them: a light, an open door, a chair, a
// resident, a season, a title card.
//
// So every piece of machinery that CUTS the world — the levelled pad, `place template`,
// the air fills, the group runner that plays a town-vbPlan group — is here, behind
// `/valley build`, which is run exactly once by whoever makes the master world
// (scratch/master_build.sh) and never in play. valley_finales.js greps clean of `@pad`,
// `place template` and `fill … air` because none of it lives there any more.
//
// Nothing in this file is reachable from a quest reward. `/valley build` needs permission
// level 2 and is not in any quest's command list.
//
// Public surface, for valley_finales.js's `/valley build` subcommand only:
//   global.valleyBuild.group(source, key)   build one town-vbPlan group
//   global.valleyBuild.all(source)          build every group, in VB_BUILD_ORDER
//   global.valleyBuild.order()              the build order, for `/valley build list`
//   global.valleyBuild.seg(server, o, cmds) vbResolve `~` offsets and run a command list
//   global.valleyBuild.vbResolve(cmd, origin) the tilde resolver on its own
// =============================================================================

const VB_POST = 'minecraft:oak_fence'
const VB_LAMP_LIT = 'createdeco:yellow_copper_lamp[facing=up,inverted=true,lit=true]'
const VB_LAMP_DARK = 'createdeco:yellow_copper_lamp[facing=up,inverted=false,lit=false]'

// -----------------------------------------------------------------------------
// Tilde resolution. Every coordinate in the outline is written as a triple of
// tilde offsets from the segment's origin; nothing else in a command line
// starts with `~`, so a single regex pass is exact and leaves NBT and JSON
// untouched.
// -----------------------------------------------------------------------------
const VB_TILDE3 = /(^|\s)~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)[ ]+~(-?[0-9]*\.?[0-9]*)(?=[ ]|$)/g

function vbNum(base, d) {
  let v = base + (d === '' || d === '-' ? 0 : parseFloat(d))
  return (v === Math.floor(v)) ? String(Math.floor(v)) : String(v)
}

function vbResolve(cmd, origin) {
  return cmd.replace(VB_TILDE3, (m, lead, dx, dy, dz) =>
    lead + vbNum(origin[0], dx) + ' ' + vbNum(origin[1], dy) + ' ' + vbNum(origin[2], dz))
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
function vbRunDirective(server, line) {
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

function vbRunSeg(server, origin, cmds) {
  cmds.forEach(c => {
    if (!c || c.charAt(0) === '#') return
    let full = vbResolve(c, origin)
    if (full.charAt(0) === '@') { vbRunDirective(server, full); return }
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
    } catch (err) { console.error('[valley] build command failed: ' + full + ' :: ' + err) }
  })
}
function vbPlan() {
  return (typeof global.valleyTownPlan !== 'undefined') ? global.valleyTownPlan : null
}

function vbGroupOrigin(v, name) {
  if (name === 'anchor') return v.anchor()
  if (name === 'home') return v.home()
  // 'world' means the group's `~` offsets are already ABSOLUTE world coordinates. The
  // day-one groups written by plan_town.py --site use it: a road that follows the real
  // ground has no single origin to hang off, so it carries its own coordinates.
  if (name === 'world') return [0, 0, 0]
  return v.mark(name)
}

// A resident teleport: the one kind of command in a group or a scene that
// silently does nothing when its target is in a chunk the server has been told
// to load and has not loaded yet.
function vbIsNpcTp(c) {
  return typeof c === 'string' && c.indexOf('tp @e[tag=npc_') === 0
}

// `arrive`, when given, is an array a caller collects deferred segments in:
// the group's resident teleports are pulled out and handed back instead of
// being run here, so the caller can retry them the way a finale does.
function vbRunGroup(server, v, key, arrive) {
  let pl = vbPlan()
  if (!pl || !pl.groups || !pl.groups[key]) {
    console.warn('[valley] town vbPlan has no group "' + key + '" - nothing built')
    return false
  }
  let g = pl.groups[key]
  let origin = vbGroupOrigin(v, g.origin)
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
    let later = cmds.filter(vbIsNpcTp)
    if (later.length) {
      cmds = cmds.filter(c => !vbIsNpcTp(c))
      arrive.push({ origin: origin, cmds: later })
    }
  }
  try {
    vbRunSeg(server, origin, cmds)
  } finally {
    v.delay(60, srv => srv.runCommandSilent('forceload remove ' + x0 + ' ' + z0 + ' ' + x1 + ' ' + z1))
  }
  console.info('[valley] built ' + key + ' (' + g.cmds.length + ' commands)')
  return true
}


// =============================================================================
// /valley build <group|all> — the BUILD-TIME command's implementation.
//
// It runs CONSTRUCTION ONLY. Everything a group carries that is not construction is
// stripped: no resident is imported or teleported, no title card, no sound, no chat line,
// no season / time / weather / worldborder. A building group therefore lands as an EMPTY
// building, which is exactly what day one is — the town stands, abandoned, and the story
// moves people into it later.
//
// It reads the anchor and home from wherever they already are, so before the first build
// the operator sets them from valley_sites.json (scratch/master_build.sh does).
// =============================================================================

// The groups that make the world. Order matters: the road and the plot are laid before
// anything stands on them, the Works shell is sealed before the streets that cross over its
// ceiling are re-laid, the cellar is cut out from under the finished cottage, the adit is
// driven through the sealed Works shell, and the lamps go last so nothing pads over a post.
const VB_BUILD_ORDER = [
  'day1_road', 'day1_cottage', 'day1_signpost',
  'act1_inn', 'act1_mill', 'act1_marnie', 'act1_pip',
  'act1_square', 'act1_streets', 'act1_lamp_pads', 'act1_tobin',
  'act2_granary', 'act2_garden', 'act2_boathouse',
  'act3_store', 'act3_church', 'act3_table',
  'act4_greenhouse_shell', 'act4_greenhouse_glaze', 'act4_greenhouse_heat',
  'act4_bathhouse',
  'act4_works', 'act4_works_light', 'act4_beds', 'act4_bram_chair',
  'act4_lamp_sweep',
  'act5_townhall', 'act5_tess', 'act5_mab', 'act5_corin',
  // the four things the story used to build at runtime and now never does:
  // the cellar under the kitchen (Q5 digs it out), the fallen adit into the Works
  // (Q65 mines it), the noticeboard and the Surveyor's Stake socket on the square.
  'day1_cellar', 'day1_adit', 'day1_board', 'day1_lakefront', 'day1_wisp_posts',
  'day1_lamps',
  // ...and the planting LAST: eight trees, five fenced plots and the orchard behind the
  // farm stand on ground every other group has finished moving.
  'day1_planting',
]

// A command that dresses, announces or populates rather than builds.
function vbIsBuildCmd(c) {
  if (typeof c !== 'string' || !c.length) return false
  if (c.charAt(0) === '#') return false
  if (c.charAt(0) === '@') return true                      // @pad / @padfix ARE construction
  let h = c.split(' ')[0]
  if (h === 'title' || h === 'playsound' || h === 'tellraw' || h === 'stopsound') return false
  if (h === 'season' || h === 'time' || h === 'weather' || h === 'worldborder') return false
  if (h === 'gamerule' || h === 'difficulty' || h === 'give' || h === 'advancement') return false
  if (h === 'summon' || h === 'kill') return false
  if (c.indexOf('easy_npc') === 0) return false             // no residents on day one
  if (c.indexOf('tp @e[tag=npc_') === 0) return false
  if (c.indexOf('execute') === 0 && (c.indexOf(' playsound') >= 0 || c.indexOf(' tellraw') >= 0)) return false
  return true
}

// A lamp that a build must leave DARK. Q34, Q74 and the Act I finale each light a route;
// on day one every post in the valley is unlit, so a lit lamp in a group's own commands is
// swapped for the dark state rather than dropped -- the post still stands.
function vbDarkenLamps(c) {
  return (c.indexOf(VB_LAMP_LIT) < 0) ? c : c.split(VB_LAMP_LIT).join(VB_LAMP_DARK)
}

function vbBuildGroup(source, key) {
  let v = global.valley
  let pl = vbPlan()
  if (!pl || !pl.groups || !pl.groups[key]) {
    vbMsg(source, Text.red('No build group "' + key + '".'))
    return 0
  }
  let g = pl.groups[key]
  let origin = vbGroupOrigin(v, g.origin)
  if (!origin) {
    vbMsg(source, Text.red('Group "' + key + '" needs origin "' + g.origin +
        '", which is not set. Set the anchor and home from valley_sites.json first.'))
    return 0
  }
  let server = source.getServer()
  let cmds = g.cmds.filter(vbIsBuildCmd).map(vbDarkenLamps)
  let b = g.bounds || [0, 0, 0, 0]
  let x0 = origin[0] + b[0] - 16, z0 = origin[2] + b[1] - 16
  let x1 = origin[0] + b[2] + 16, z1 = origin[2] + b[3] + 16
  server.runCommandSilent('forceload add ' + x0 + ' ' + z0 + ' ' + x1 + ' ' + z1)
  try {
    vbRunSeg(server, origin, cmds)
  } finally {
    server.runCommandSilent('forceload remove ' + x0 + ' ' + z0 + ' ' + x1 + ' ' + z1)
  }
  vbMsg(source, Text.gold('built ' + key + '  (' + cmds.length + ' of ' + g.cmds.length +
      ' commands; ' + (g.cmds.length - cmds.length) + ' skipped as dressing)'))
  console.info('[valley] BUILD ' + key + ': ' + cmds.length + '/' + g.cmds.length)
  return 1
}

function vbBuildAll(source) {
  let n = 0
  VB_BUILD_ORDER.forEach(k => { n += vbBuildGroup(source, k) })
  let server = source.getServer()
  server.runCommandSilent('save-all flush')
  vbMsg(source, Text.gold('BUILD COMPLETE: ' + n + ' of ' + VB_BUILD_ORDER.length + ' groups.'))
  return n
}


// -----------------------------------------------------------------------------
// Command feedback. 1.20 changed CommandSourceStack.sendSuccess to take a
// Supplier<Component>, which is a trap for a script, so everything talks to the
// player directly and falls back to the console.
// -----------------------------------------------------------------------------
function vbMsg(source, component) {
  let p = null
  try { p = source.player || null } catch (err) { p = null }
  if (p) p.tell(component)
  else console.info('[valley/build] ' + component.getString())
}

global.valleyBuild = {
  group: vbBuildGroup,
  all: vbBuildAll,
  order: function () { return VB_BUILD_ORDER.slice(0) },
  seg: vbRunSeg,
  runGroup: vbRunGroup,
  resolve: vbResolve
}

console.info('[valley] valley_build.js ok -- ' + VB_BUILD_ORDER.length + ' groups in the build order')
