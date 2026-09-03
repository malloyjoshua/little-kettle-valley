// =============================================================================
// valley_core.js — Copper Kettle Valley: the spine.
//
// Owns:
//   * global.valley           the helper API every other valley script uses
//   * server.persistentData   anchor, home, lamps[], world stages, finale flags
//   * the FTB Teams auto-party (§9-A "the couple's team")
//   * the first-join handler (§2 premise, §12.5 first-join command block)
//   * the animal-crate / chicken-feed right-click handlers (§8 worked ex. 2)
//
// Engine notes verified against kubejs-forge-2001.6.5-build.26.jar:
//   * PlayerEvents has NO wakeUp/sleep event in this build. Sleep detection
//     lives in valley_checks.js as a slow-tick poll.
//   * There is no player.username. Use player.profile.name.
//   * server.persistentData is a CompoundTag (MinecraftServerMixin implements
//     WithPersistentData). Everything below stores FLAT primitive keys, because
//     nested CompoundTags returned by getCompound() are not reliably attached.
//   * There is no exposed scheduler binding, so delays are a tick queue here.
// =============================================================================

// -----------------------------------------------------------------------------
// 0. Tunables. Every anchor-relative offset in the pack lives here so the
//    checks and the finales can never disagree. [dx, dy, dz] from the Town
//    Anchor unless the name says HOME_.
// -----------------------------------------------------------------------------
const VALLEY = {
  // --- Named marks, anchor-relative ---------------------------------------
  OFF: {
    square:      [0, 1, 0],      // the Town Square waystone (act1 finale)
    board:       [0, 1, -5],     // Oda's noticeboard (act3 finale)
    inn:         [-14, 1, 4],
    mill:        [-26, 0, 4],    // the mill race (act1 finale)
    granary:     [-14, 1, -4],   // (act2 finale)
    lake:        [0, 1, 34],     // the Pier waystone
    works:       [34, -6, -20],
    greenhouse:  [-20, 1, 14],
    bathhouse:   [-18, 1, 10],
    echo_cave:   [34, -30, -20]
  },

  // --- Box sizes for "is the player standing in X" checks, in blocks -------
  BOX: {
    works:     [10, 6, 10],
    echo_cave: [8, 6, 8],
    cellar:    [7, 4, 7]
  },

  // Q5 wants "below the ruin floor"; Q55 wants "in the cellar, at the wall".
  HOME_CELLAR_Y: -3,          // Q5  : player.y <= home.y - 3
  HOME_DEEP_Y:   -6,          // Q55 : player.y <= home.y - 6
  HOME_PORCH:    [3, 0, 0],   // Q90 : the bare fortieth post

  // --- The Lantern Road. Anchor-relative post positions. -------------------
  // Act I's finale places LAMPS_FINALE itself. Q34 whitelists LAMPS_Q34, Q74
  // the rest. Everything actually placed is stored absolute in persistentData
  // and re-lit, all at once, by the Act IV lever.
  LAMP_BLOCK: 'candlelight:lamp',
  LAMP_TOLERANCE: 2,
  LAMPS_FINALE: [[-12,1,0],[12,1,0],[0,1,-12],[0,1,12]],
  LAMPS_Q34: [[-16,1,2],[-20,1,3],[-24,1,4],[-8,1,1]],
  LAMPS_Q74: [
    [4,1,6],[8,1,10],[12,1,14],[16,1,18],[20,1,22],[24,1,26],
    [-4,1,8],[-8,1,12],[-12,1,16],[-16,1,20],[-20,1,24],
    [6,1,-8],[10,1,-12],[14,1,-16],[-6,1,-8],[-10,1,-12],[-14,1,-16]
  ],

  // --- Resident chat colours (§writer-brief rule 10) -----------------------
  VOICE: {
    Josie:  'gray',
    Marnie: 'gold',
    Bram:   'dark_aqua',
    Oda:    'yellow',
    Nella:  'aqua',
    Halden: 'green',
    Tobin:  'gold',
    Wisp:   'light_purple',
    Pip:    'red'
  },

  // --- The eight chain-closing quests, for Standing: Trusted (§5) ----------
  STANDING_CHAINS: ['q59', 'q60', 'q62', 'q63', 'q73', 'q75', 'q77', 'q85'],

  // --- Custom item ids used by the runtime handlers ------------------------
  ITEM: {
    letter: 'valley:letter',
    deed:   'valley:deed',
    kettle: 'herbalbrews:copper_tea_kettle'   // the Copper Kettle over the hearth
  }
}

const $AABB = Java.loadClass('net.minecraft.world.phys.AABB')

// -----------------------------------------------------------------------------
// 1. persistentData. Flat keys only — see the header note.
// -----------------------------------------------------------------------------
function pdata() {
  const s = global.valleyServer
  return s ? s.persistentData : null
}

function pdGet(key, fallback) {
  const d = pdata()
  if (!d || !d.contains(key)) return fallback
  return d.getString(key)
}

function pdPut(key, value) {
  const d = pdata()
  if (d) d.putString(key, String(value))
}

function pdFlag(key) {
  const d = pdata()
  return !!(d && d.contains(key))
}

function pdSetFlag(key) {
  const d = pdata()
  if (d) d.putString(key, '1')
}

function posToStr(p) { return p[0] + ',' + p[1] + ',' + p[2] }

function strToPos(s) {
  if (!s) return null
  const parts = String(s).split(',')
  if (parts.length !== 3) return null
  const x = parseInt(parts[0], 10), y = parseInt(parts[1], 10), z = parseInt(parts[2], 10)
  if (isNaN(x) || isNaN(y) || isNaN(z)) return null
  return [x, y, z]
}

// -----------------------------------------------------------------------------
// 2. The delay queue. Replaces `/schedule function`, which needs a datapack
//    function we do not ship. Drained by the tick handler at the bottom; the
//    array is empty except during a finale, so the cost is one length check.
// -----------------------------------------------------------------------------
const valleyPending = []

function valleyDelay(ticks, fn) {
  valleyPending.push({ at: global.valleyTick + ticks, fn: fn })
}

// -----------------------------------------------------------------------------
// 3. The public API. Everything in valley_gates / valley_checks /
//    valley_finales, and every act writer's KubeJS-facing assumption, goes
//    through this object.
// -----------------------------------------------------------------------------
global.valley = {

  C: VALLEY,

  // ---- server handle ------------------------------------------------------
  server: function () { return global.valleyServer },

  // ---- Town Anchor (Q7). Returns [x,y,z] or null. -------------------------
  anchor: function () { return strToPos(pdGet('valley_anchor', null)) },

  setAnchor: function (x, y, z) {
    pdPut('valley_anchor', posToStr([x, y, z]))
    console.info('[valley] Town Anchor set to ' + x + ' ' + y + ' ' + z)
  },

  // ---- The Homestead waystone (Q2). Returns [x,y,z] or null. --------------
  home: function () { return strToPos(pdGet('valley_home', null)) },

  setHome: function (x, y, z) {
    pdPut('valley_home', posToStr([x, y, z]))
    console.info('[valley] Home set to ' + x + ' ' + y + ' ' + z)
  },

  // ---- anchor + offset -> absolute [x,y,z]. Null if no anchor. ------------
  offset: function (off) {
    const a = global.valley.anchor()
    if (!a) return null
    return [a[0] + off[0], a[1] + off[1], a[2] + off[2]]
  },

  // ---- Named mark by key from VALLEY.OFF ---------------------------------
  mark: function (name) {
    const off = VALLEY.OFF[name]
    return off ? global.valley.offset(off) : null
  },

  // ---- Complete a quest for the player's TEAM (§P2). ---------------------
  // key is an outline key: 'q07'. Silently no-ops if the compiler has not
  // emitted that key into _quest_ids.js yet, so a half-built pack still runs.
  complete: function (player, key) {
    const ids = global.valleyQuestIds || {}
    const id = ids[key]
    if (!id) {
      if (!global.valleyMissingWarned) global.valleyMissingWarned = {}
      if (!global.valleyMissingWarned[key]) {
        global.valleyMissingWarned[key] = true
        console.warn('[valley] no quest id for "' + key + '" in _quest_ids.js — skipping completion')
      }
      return false
    }
    const s = global.valleyServer
    if (!s) return false
    s.runCommandSilent('ftbquests change_progress ' + global.valley.pname(player) + ' complete ' + id)
    return true
  },

  // ---- The player's login name. There is no player.username in 2001.6.5. --
  pname: function (player) { return player.profile.name },

  // ---- Give a KubeJS stage to every ONLINE member of a team. -------------
  // Stages are per player (§naming contract), so a team-wide grant is a loop.
  // `team` may be an FTB team object, or null for "everyone online".
  stageAll: function (team, stage) {
    const s = global.valleyServer
    if (!s) return
    s.players.forEach(p => {
      if (team) {
        // p.team only exists when the FTB Teams integration is present; if the
        // lookup fails for any reason we fall back to "everyone online", which
        // is correct for a one-team world and harmless for two.
        try { if (p.team && String(p.team.id) !== String(team.id)) return } catch (err) { /* ignore */ }
      }
      if (!p.stages.has(stage)) p.stages.add(stage)
    })
  },

  // ---- One resident line, in that resident's colour (§writer-brief 10). ---
  // Built as tellraw JSON so nothing depends on a Component builder overload.
  say: function (player, who, text) {
    const colour = VALLEY.VOICE[who] || 'white'
    const json = [
      { text: who + ': ', color: colour, bold: false },
      { text: text, color: 'white', italic: true }
    ]
    const s = global.valleyServer
    if (!s) return
    s.runCommandSilent('tellraw ' + global.valley.pname(player) + ' ' + JSON.stringify(json))
  },

  // ---- Same line, to everyone. Used by the finales. ----------------------
  sayAll: function (who, text) {
    const colour = VALLEY.VOICE[who] || 'white'
    const json = [
      { text: who + ': ', color: colour },
      { text: text, color: 'white', italic: true }
    ]
    const s = global.valleyServer
    if (s) s.runCommandSilent('tellraw @a ' + JSON.stringify(json))
  },

  // ---- World stages. There is no GameStages mod; a world stage is a flag in
  //      persistentData (§9-F "world stages vs team stages"). -------------
  hasWorldStage: function (id) { return pdFlag('valley_ws_' + id) },
  addWorldStage: function (id) {
    if (!pdFlag('valley_ws_' + id)) {
      pdSetFlag('valley_ws_' + id)
      console.info('[valley] world stage granted: ' + id)
    }
  },

  // ---- The Lantern Road list. Absolute coords, CSV in persistentData. ----
  lamps: function () {
    const raw = pdGet('valley_lamps', '')
    if (!raw) return []
    return String(raw).split(';').filter(s => s.length > 0).map(strToPos).filter(p => p)
  },

  addLamp: function (x, y, z) {
    const list = global.valley.lamps()
    for (let i = 0; i < list.length; i++) {
      if (list[i][0] === x && list[i][1] === y && list[i][2] === z) return false
    }
    const raw = pdGet('valley_lamps', '')
    pdPut('valley_lamps', raw ? raw + ';' + posToStr([x, y, z]) : posToStr([x, y, z]))
    return true
  },

  // ---- Finale idempotency (§P7). ----------------------------------------
  finaleDone: function (act) { return pdFlag('valley_finale_' + act) },
  markFinale: function (act) { pdSetFlag('valley_finale_' + act) },

  // ---- Generic once-per-world latch, used by the checks. -----------------
  once: function (key) {
    if (pdFlag('valley_once_' + key)) return false
    pdSetFlag('valley_once_' + key)
    return true
  },
  isDone: function (key) { return pdFlag('valley_once_' + key) },

  // ---- Delay, in ticks. ---------------------------------------------------
  delay: valleyDelay,

  // ---- Raw persistent storage, for the checks' per-player baselines. ------
  get: function (key, fallback) { return pdGet(key, fallback) },
  set: function (key, value) { pdPut(key, value) },

  // ---- Entities of a type inside a box centred on [x,y,z]. ---------------
  countNear: function (level, pos, radius, typePrefix) {
    const box = new $AABB(
      pos[0] - radius, pos[1] - radius, pos[2] - radius,
      pos[0] + radius, pos[1] + radius, pos[2] + radius
    )
    let n = 0
    level.getEntitiesWithin(box).forEach(e => {
      if (String(e.type).indexOf(typePrefix) === 0) n++
    })
    return n
  },

  // ---- Is this player inside the box [centre, size]? ---------------------
  inBox: function (player, centre, size) {
    if (!centre) return false
    return Math.abs(player.x - centre[0]) <= size[0] &&
           Math.abs(player.y - centre[1]) <= size[1] &&
           Math.abs(player.z - centre[2]) <= size[2]
  },

  // ---- Horizontal distance, for "within N of Home" checks. ---------------
  flatDist: function (player, pos) {
    const dx = player.x - pos[0], dz = player.z - pos[2]
    return Math.sqrt(dx * dx + dz * dz)
  }
}

// =============================================================================
// 4. Server lifecycle
// =============================================================================
global.valleyTick = 0

ServerEvents.loaded(event => {
  global.valleyServer = event.server
  global.valleyTick = 0
  valleyPending.length = 0

  // §P6 — the two counters are bossbars. Re-issued on every load; `add` on an
  // existing bar is a harmless failure.
  const s = event.server
  s.runCommandSilent('bossbar add valley:lamps {"text":"Lantern Road","color":"gold"}')
  s.runCommandSilent('bossbar set valley:lamps max 40')
  s.runCommandSilent('bossbar set valley:lamps players @a')
  s.runCommandSilent('bossbar add valley:folk {"text":"Residents","color":"green"}')
  s.runCommandSilent('bossbar set valley:folk max 15')
  s.runCommandSilent('bossbar set valley:folk players @a')

  const a = global.valley.anchor()
  console.info('[valley] core loaded. Anchor: ' + (a ? a.join(' ') : 'not set yet'))
})

ServerEvents.unloaded(event => {
  global.valleyServer = null
  valleyPending.length = 0
})

// The one shared tick handler for the delay queue. valley_checks.js keeps its
// own slow-tick poll; this one only drains scheduled finale steps.
ServerEvents.tick(event => {
  global.valleyTick++
  if (valleyPending.length === 0) return
  for (let i = valleyPending.length - 1; i >= 0; i--) {
    if (valleyPending[i].at <= global.valleyTick) {
      const job = valleyPending.splice(i, 1)[0]
      try { job.fn(event.server) } catch (err) { console.error('[valley] delayed step failed: ' + err) }
    }
  }
})

// =============================================================================
// 5. Login: the FTB Teams auto-party, then the first-join handler.
// =============================================================================
PlayerEvents.loggedIn(event => {
  const player = event.entity
  const server = global.valleyServer || player.level.server
  if (!server) return
  const name = global.valley.pname(player)

  // ---- §9-A: everybody lands on one party called Cozy. Guarded by the
  // per-player stage cozy_party; skipped entirely for anyone holding
  // solo_team (§9-B, the second letter / a player who wants their own book).
  if (!player.stages.has('cozy_party') && !player.stages.has('solo_team')) {
    player.stages.add('cozy_party')
    // join first: if Cozy exists this succeeds and create/settings are no-ops.
    server.runCommandSilent('execute as ' + name + ' run ftbteams party join Cozy')
    server.runCommandSilent('execute as ' + name + ' run ftbteams party create Cozy')
    server.runCommandSilent('execute as ' + name + ' run ftbteams party settings free_to_join true')
  }

  // ---- §12.5 first-join block. Per player, once.
  if (!player.stages.has('first_join')) {
    player.stages.add('first_join')
    valleyFirstJoin(server, player, name)
  }

  // Re-attach the bossbars for this player.
  server.runCommandSilent('bossbar set valley:lamps players @a')
  server.runCommandSilent('bossbar set valley:folk players @a')
})

function valleyFirstJoin(server, player, name) {
  // The letter, the deed and the kettle. Q1's task is holding the letter.
  player.give(Item.of(VALLEY.ITEM.letter))
  player.give(Item.of(VALLEY.ITEM.deed))
  player.give(Item.of(VALLEY.ITEM.kettle))

  // Title card. Exactly the words in §2.
  server.runCommandSilent('title ' + name + ' times 20 90 30')
  server.runCommandSilent('title ' + name + ' subtitle ' +
    JSON.stringify({ text: 'Spring, Year One.', color: 'gray', italic: true }))
  server.runCommandSilent('title ' + name + ' title ' +
    JSON.stringify({ text: 'COPPER KETTLE VALLEY', color: 'gold', bold: true }))
  server.runCommandSilent('playsound minecraft:block.note_block.chime master ' + name + ' ~ ~ ~ 1 0.8')

  // The premise, then the destination line, verbatim (writer-brief rule 3).
  const lines = [
    [{ text: 'You inherited the old Kettle farm from a great-aunt you barely remember — ', color: 'white' },
     { text: 'Josie Kettle', color: 'gold' },
     { text: ', who kept the lights on in this valley long after everyone else stopped trying.', color: 'white' }],
    [{ text: 'A chimney, three walls, a bed frame, and a copper kettle over a cold hearth. Outside: an inn with no innkeeper, a mill with a snapped axle, a store with the shutters down, and forty dark lamp posts.', color: 'white' }],
    [{ text: 'Forty lamps. Fifteen people. One winter that nobody leaves.', color: 'gold', bold: true }],
    [{ text: 'Open your Quest Book. There is exactly one thing to do.', color: 'white' }]
  ]
  lines.forEach((l, i) => {
    valleyDelay(20 + i * 20, s => s.runCommandSilent('tellraw ' + name + ' ' + JSON.stringify(l)))
  })

  // The world border and the two counters start where §12.5 says they do.
  if (global.valley.once('world_opened')) {
    server.runCommandSilent('worldborder set 1500')
    server.runCommandSilent('bossbar set valley:folk value 1')
    server.runCommandSilent('bossbar set valley:lamps value 0')
  }
  console.info('[valley] first join handled for ' + name)
}

// =============================================================================
// 6. Handheld helpers the quests hand out.
//    §8 worked example 2: nobody waits on a chicken; the animals arrive in
//    crates and the feed makes a hen lay on use.
// =============================================================================
const CRATE_SPAWN = {
  'valley:hen_crate':   'minecraft:chicken',
  'valley:cow_crate':   'minecraft:cow',
  'valley:sheep_crate': 'minecraft:sheep'
}

// Q10 (three Hen Crates) and Q25 (Cow Crate + Sheep Crate).
Object.keys(CRATE_SPAWN).forEach(crateId => {
  ItemEvents.rightClicked(crateId, event => {
    const player = event.player
    if (player.level.isClientSide()) return
    const entityId = CRATE_SPAWN[crateId]
    const e = player.level.createEntity(entityId)
    if (!e) return
    e.setPosition(player.x, player.y, player.z)
    e.spawn()
    if (!player.isCreative()) event.item.count = event.item.count - 1
    global.valley.say(player, 'Marnie', 'There you are. Mind the gate.')
  })
})

// Chicken feed: the nearest hen within 8 blocks lays immediately.
ItemEvents.rightClicked('valley:chicken_feed', event => {
  const player = event.player
  if (player.level.isClientSide()) return
  const box = new $AABB(player.x - 8, player.y - 4, player.z - 8, player.x + 8, player.y + 4, player.z + 8)
  let laid = 0
  player.level.getEntitiesWithin(box).forEach(e => {
    if (laid > 0) return
    if (String(e.type) !== 'minecraft:chicken') return
    const b = player.level.getBlock(Math.floor(e.x), Math.floor(e.y), Math.floor(e.z))
    b.popItem(Item.of('minecraft:egg'))
    laid++
  })
  if (laid > 0 && !player.isCreative()) event.item.count = event.item.count - 1
  if (laid === 0) global.valley.say(player, 'Marnie', 'No hen close enough. Stand in the pen.')
})

console.info('[valley] valley_core.js ok')
