// valley_ores.js — /valley ores: puts VANILLA ores into the pre-generated valley.
//
// Geolosys ships a biome modifier (remove_vanilla_ores.json) that strips all thirty vanilla
// ore features from every biome, and the shipped world was pre-generated under that rule, so
// the whole 1040x1040 play area had no iron, coal, copper, gold, redstone, lapis or diamond in
// its stone. Josh: "I like vanilla ores AND modded ones" (2026-09-05). The pack now overrides
// that modifier (kubejs/data/geolosys/forge/biome_modifier/remove_vanilla_ores.json), so every
// NEW chunk generates both. This command back-fills the 4225 chunks that already exist.
//
// How: it replays vanilla's own placement rules (data/minecraft/worldgen/placed_feature/
// ore_*.json, 1.20.1, copied into RULES below) through `/place feature`, so every blob is the
// real configured feature — same size, same stone/deepslate targets, same discard-on-air-
// exposure. The features only ever replace #minecraft:stone_ore_replaceables and
// #minecraft:deepslate_ore_replaceables, so nothing built, placed or planted can be touched.
// Above y 40 inside a registry site box (plus the Works shell and the cellar) no attempt is
// made at all; every structure in the valley sits above y 53.
//
// `/place feature` refuses a position unless the 3x3 chunks around it are loaded (PlaceCommand
// .checkLoaded), and it refuses silently through runCommandSilent. The first version of this
// forceloaded one chunk at a time and lost a third of the deep ore that way. Now it works in
// batches: forceload an 8x8 block of chunks plus a one-chunk margin, wait until the chunk
// source reports every one of them loaded, place, release, next batch. Every command's return
// value is counted, so the log says how many placements the game accepted.
//
// Runs once per world: a persistentData latch stops a second run doubling the ore. Permission
// 0 so it works in singleplayer with cheats off (the server's own command source places the
// features). `/valley ores force` (op) re-runs it — only ever for a rebuilt master world.
//
// Rhino rule (docs/SESSIONS.md): `let`, never `const`, inside functions.

const ORE_Y_CAP = 160        // highest surface in the pregen is y 153; stone above it does not exist
const CHUNK_X0 = -52, CHUNK_X1 = 12, CHUNK_Z0 = -33, CHUNK_Z1 = 31   // Chunky square, r 512 from -310,-6
const BATCH = 8              // chunks per side per batch
const MARGIN = 1             // loaded ring around the batch so every 3x3 is loaded
const CHUNKS_PER_TICK = 2      // 4 on the dedicated master run; 2 keeps a singleplayer client playable
const LOAD_TIMEOUT_TICKS = 200
const BOX_MARGIN = 8

// [configured feature, attempts per chunk (fractional = probability), height provider]
// 'u' = uniform inclusive, 't' = vanilla trapezoid with plateau 0 (sum of two uniforms).
// above_bottom / below_top already resolved against the overworld's -64..319.
const RULES = [
  ['minecraft:ore_coal',           30,    ['u',  136, 319]],   // ore_coal_upper
  ['minecraft:ore_coal_buried',    20,    ['t',    0, 192]],   // ore_coal_lower
  ['minecraft:ore_iron',           90,    ['t',   80, 384]],   // ore_iron_upper (the ridge)
  ['minecraft:ore_iron',           10,    ['t',  -24,  56]],   // ore_iron_middle
  ['minecraft:ore_iron_small',     10,    ['u',  -64,  72]],   // ore_iron_small
  ['minecraft:ore_copper_small',   16,    ['t',  -16, 112]],   // ore_copper
  ['minecraft:ore_gold_buried',     4,    ['t',  -64,  32]],   // ore_gold
  ['minecraft:ore_gold_buried',     0.5,  ['u',  -64, -48]],   // ore_gold_lower (count 0..1)
  ['minecraft:ore_redstone',        4,    ['u',  -64,  15]],   // ore_redstone
  ['minecraft:ore_redstone',        8,    ['t',  -96, -32]],   // ore_redstone_lower
  ['minecraft:ore_lapis',           2,    ['t',  -32,  32]],   // ore_lapis
  ['minecraft:ore_lapis_buried',    4,    ['u',  -64,  64]],   // ore_lapis_buried
  ['minecraft:ore_diamond_small',   7,    ['t', -144,  16]],   // ore_diamond
  ['minecraft:ore_diamond_large',   1 / 9, ['t', -144,  16]],  // ore_diamond_large (rarity 9)
  ['minecraft:ore_diamond_buried',  4,    ['t', -144,  16]]    // ore_diamond_buried
]
// Emerald only where vanilla puts it: the #minecraft:is_mountain biomes.
const MOUNTAIN_RULES = [
  ['minecraft:ore_emerald',       100,    ['t',  -16, 480]]    // ore_emerald
]
const MOUNTAIN_BIOME = /peaks|meadow|grove|slopes|windswept/

function rnd(n) { return Math.floor(Math.random() * n) }

function sampleY(h) {
  let a = h[1], b = h[2]
  if (h[0] === 'u') return a + rnd(b - a + 1)
  // net.minecraft.world.level.levelgen.heightproviders.TrapezoidHeight, plateau 0
  let k = b - a, l = Math.floor(k / 2), m = k - l
  return a + rnd(m + 1) + rnd(l + 1)
}

function attempts(c) {
  let whole = Math.floor(c)
  return whole + (Math.random() < c - whole ? 1 : 0)
}

// Site boxes (x0, z0, x1, z1) from the registry, plus the Works shell and the cellar,
// each grown by BOX_MARGIN. Built once, lazily, so a missing registry cannot break load.
let boxes = null
function siteBoxes() {
  if (boxes) return boxes
  boxes = []
  let s = global.valleySites || {}
  let sb = s.site_boxes || {}
  Object.keys(sb).forEach(k => {
    let b = sb[k]
    boxes.push([Math.min(b[0], b[2]) - BOX_MARGIN, Math.min(b[1], b[3]) - BOX_MARGIN,
                Math.max(b[0], b[2]) + BOX_MARGIN, Math.max(b[1], b[3]) + BOX_MARGIN])
  })
  if (s.works && s.works.shell) {
    let w = s.works.shell
    boxes.push([w[0] - BOX_MARGIN, w[2] - BOX_MARGIN, w[3] + BOX_MARGIN, w[5] + BOX_MARGIN])
  }
  if (s.cellar && s.cellar.box) {
    let c = s.cellar.box
    boxes.push([c[0] - BOX_MARGIN, c[2] - BOX_MARGIN, c[3] + BOX_MARGIN, c[5] + BOX_MARGIN])
  }
  return boxes
}

function inSiteBox(x, z) {
  let bs = siteBoxes()
  for (let i = 0; i < bs.length; i++) {
    let b = bs[i]
    if (x >= b[0] && x <= b[2] && z >= b[1] && z <= b[3]) return true
  }
  return false
}

function isMountain(level, x, z) {
  try {
    return MOUNTAIN_BIOME.test(String(level.getBlock(x, 64, z).biomeId))
  } catch (err) { return false }
}

function doChunk(server, level, cx, cz, job) {
  let rules = isMountain(level, cx * 16 + 8, cz * 16 + 8) ? RULES.concat(MOUNTAIN_RULES) : RULES
  for (let r = 0; r < rules.length; r++) {
    let rule = rules[r]
    let n = attempts(rule[1])
    for (let k = 0; k < n; k++) {
      let y = sampleY(rule[2])
      if (y < -64 || y > ORE_Y_CAP) continue
      let x = cx * 16 + rnd(16), z = cz * 16 + rnd(16)
      if (y > 40 && inSiteBox(x, z)) continue
      let res = server.runCommandSilent('place feature ' + rule[0] + ' ' + x + ' ' + y + ' ' + z)
      if (res > 0) job.ok++; else job.fail++
    }
  }
}

// Batches: an 8x8 block of chunks, walked in rows across the pregen square.
function batchCount() {
  let w = Math.ceil((CHUNK_X1 - CHUNK_X0 + 1) / BATCH), h = Math.ceil((CHUNK_Z1 - CHUNK_Z0 + 1) / BATCH)
  return w * h
}
function batchAt(i) {
  let w = Math.ceil((CHUNK_X1 - CHUNK_X0 + 1) / BATCH)
  let bx = CHUNK_X0 + (i % w) * BATCH, bz = CHUNK_Z0 + Math.floor(i / w) * BATCH
  return { x0: bx, z0: bz, x1: Math.min(bx + BATCH - 1, CHUNK_X1), z1: Math.min(bz + BATCH - 1, CHUNK_Z1) }
}
function batchLoaded(level, b) {
  let cs = level.getChunkSource()
  for (let cx = b.x0 - MARGIN; cx <= b.x1 + MARGIN; cx++)
    for (let cz = b.z0 - MARGIN; cz <= b.z1 + MARGIN; cz++)
      if (!cs.hasChunk(cx, cz)) return false
  return true
}
function forceBatch(server, b, add) {
  server.runCommandSilent('forceload ' + (add ? 'add ' : 'remove ') +
    ((b.x0 - MARGIN) * 16) + ' ' + ((b.z0 - MARGIN) * 16) + ' ' +
    ((b.x1 + MARGIN) * 16 + 15) + ' ' + ((b.z1 + MARGIN) * 16 + 15))
}

function say(server, text) {
  server.runCommandSilent('tellraw @a ' + JSON.stringify({ text: text, color: 'gray', italic: true }))
}

function startOres(ctx, force) {
  let server = ctx.source.server
  if (global.valleyOresJob) {
    ctx.source.sendSuccess(Component.literal('Already reading the stone. Give it a minute.'), false)
    return 0
  }
  let pd = server.persistentData
  if (!force && pd.getInt('valley_ores_done') === 1) {
    ctx.source.sendSuccess(Component.literal('The stone under the valley has already been read: the ores are in. Nothing to do.'), false)
    return 0
  }
  global.valleyOresJob = { batch: 0, batches: batchCount(), phase: 'load', wait: 0, cx: 0, cz: 0,
                           chunks: 0, ok: 0, fail: 0, lastPct: -1 }
  say(server, 'Reading the stone under the valley: iron, coal, copper, gold, redstone, lapis, diamond. Three or four minutes, and the game will stutter while it works. Keep playing.')
  console.info('[valley] ores: start, ' + global.valleyOresJob.batches + ' batches of ' + BATCH + 'x' + BATCH + ' chunks, force=' + force)
  return 1
}

function finish(server, job) {
  server.persistentData.putInt('valley_ores_done', 1)
  say(server, 'Done. The stone under the valley reads like anywhere else now: ore where you dig for it, and the beds where Bram said.')
  console.info('[valley] ORES COMPLETE chunks=' + job.chunks + ' accepted=' + job.ok + ' refused=' + job.fail)
  global.valleyOresJob = null
}

ServerEvents.tick(event => {
  let job = global.valleyOresJob
  if (!job) return
  let server = event.server
  let level = server.overworld()
  if (job.batch >= job.batches) { finish(server, job); return }
  let b = batchAt(job.batch)
  if (job.phase === 'load') {
    if (job.wait === 0) forceBatch(server, b, true)
    job.wait++
    let ready = false
    try { ready = batchLoaded(level, b) } catch (err) { ready = job.wait >= 40 }
    if (!ready && job.wait < LOAD_TIMEOUT_TICKS) return
    if (!ready) console.warn('[valley] ores: batch ' + job.batch + ' not fully loaded after ' + job.wait + ' ticks, placing anyway')
    job.phase = 'work'; job.cx = b.x0; job.cz = b.z0
    return
  }
  // work: CHUNKS_PER_TICK chunks of this batch per tick
  for (let n = 0; n < CHUNKS_PER_TICK; n++) {
    doChunk(server, level, job.cx, job.cz, job)
    job.chunks++
    job.cx++
    if (job.cx > b.x1) { job.cx = b.x0; job.cz++ }
    if (job.cz > b.z1) {
      forceBatch(server, b, false)
      job.batch++; job.phase = 'load'; job.wait = 0
      break
    }
  }
  let pct = Math.floor(job.batch * 20 / job.batches) * 5
  if (pct !== job.lastPct) {
    job.lastPct = pct
    server.runCommandSilent('title @a actionbar ' + JSON.stringify({ text: 'Reading the stone: ' + pct + '%', color: 'gray' }))
  }
})

ServerEvents.commandRegistry(event => {
  let Commands = event.commands
  event.register(
    Commands.literal('valley')
      .then(Commands.literal('ores')
        .requires(src => src.hasPermission(0))
        .executes(ctx => startOres(ctx, false))
        .then(Commands.literal('force')
          .requires(src => src.hasPermission(2))
          .executes(ctx => startOres(ctx, true)))))
})
