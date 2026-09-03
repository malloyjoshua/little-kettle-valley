// =============================================================================
// valley_checks.js — Copper Kettle Valley: the "checkmark·kjs" auto-completions.
//
// §12.2 P2 — the KubeJS escape hatch. FTB Quests Location tasks are authored
// as fixed coordinates and cannot reference a runtime anchor, so every
// "be at / place / sleep / dig / keep N animals" gate is a CHECKMARK task
// completed by a listener calling /ftbquests change_progress.
//
// Every check in this file:
//   * is latched once per world in server.persistentData, and
//   * removes itself from the poll list the moment it fires.
// Event-driven checks (block placed, item used) cost nothing at all. The poll
// runs once every 20 ticks and, once the pack is finished, has an empty list.
//
// Quest keys follow the naming contract: Q7 -> "q07", Q74 -> "q74".
// =============================================================================

const $CHK_AABB = Java.loadClass('net.minecraft.world.phys.AABB')

const POLL_INTERVAL = 20        // ticks between polls; ~1 second
const V = () => global.valley   // shorthand; valley_core.js defines it

// -----------------------------------------------------------------------------
// Poll registry. Each entry: { key, need(server, player) -> bool }
// `key` is the quest key AND the persistentData latch name.
// -----------------------------------------------------------------------------
const POLLS = []

function poll(key, need) { POLLS.push({ key: key, need: need }) }

function fire(player, key) {
  const v = V()
  // Drop it from the poll list first, so an already-latched check can never
  // sit in the list re-testing forever after a /reload.
  for (let i = POLLS.length - 1; i >= 0; i--) {
    if (POLLS[i].key === key) POLLS.splice(i, 1)
  }
  if (!v.once(key)) return
  v.complete(player, key)
  console.info('[valley] check satisfied: ' + key)
}

// =============================================================================
// EVENT-DRIVEN CHECKS
// =============================================================================
BlockEvents.placed(event => {
  const v = V()
  if (!v || !global.valleyServer) return
  const b = event.block
  const id = String(b.id)
  const player = event.entity
  if (!player || !player.isPlayer()) return

  // ---------------------------------------------------------------------
  // Q2 — "Put the Waystone on the Hearthstone."
  // The FIRST waystone placed in the world is Home. That position becomes
  // the reference for Q4, Q5, Q10, Q25, Q55 and Q90.
  // ---------------------------------------------------------------------
  if (id === 'waystones:waystone' && !v.isDone('q02')) {
    v.setHome(b.x, b.y, b.z)
    global.valleyServer.runCommandSilent(
      'setblock ' + b.x + ' ' + b.y + ' ' + b.z + ' waystones:waystone{WaystoneName:"Home"}')
    v.say(player, 'Josie', 'That is where the hearth was. Good.')
    fire(player, 'q02')
    return
  }

  // ---------------------------------------------------------------------
  // Q7 — "Place the Surveyor's Stake North of Your Gate."
  // THE anchor listener. Everything anchor-relative in the pack — every
  // finale, every mark, every lamp — depends on this one block placement.
  // ---------------------------------------------------------------------
  if (id === 'valley:town_anchor') {
    v.setAnchor(b.x, b.y, b.z)
    global.valleyServer.runCommandSilent(
      'tellraw @a ' + JSON.stringify({
        text: 'Town Anchor set at ' + b.x + ' ' + b.y + ' ' + b.z + '. This is where the town will be.',
        color: 'gold'
      }))
    // Record the lamp posts the Act I finale is about to place, so the Act IV
    // lever relights the whole road and not just the stretches she built.
    v.C.LAMPS_FINALE.forEach(off => {
      const p = v.offset(off)
      if (p) v.addLamp(p[0], p[1], p[2])
    })
    fire(player, 'q07')
    return
  }

  // ---------------------------------------------------------------------
  // Q4 — "Place the Megatorch Inside the Cottage."
  // Within 32 of Home (§12.4: "megatorch within 32 of Home").
  // ---------------------------------------------------------------------
  if (id === 'torchmaster:megatorch' && !v.isDone('q04')) {
    const home = v.home()
    if (home && Math.abs(b.x - home[0]) <= 32 && Math.abs(b.z - home[2]) <= 32) {
      fire(player, 'q04')
    }
    return
  }

  // ---------------------------------------------------------------------
  // Q34 and Q74 — the Lantern Road.
  // A post counts when it lands within LAMP_TOLERANCE of a whitelisted
  // anchor-relative mark. Every accepted post is pushed to
  // persistentData.lamps[]; the Act IV finale iterates that list.
  // ---------------------------------------------------------------------
  if (id === v.C.LAMP_BLOCK) {
    // -------------------------------------------------------------------
    // Q90 — "The Last Lamp." One known coordinate: the bare post on
    // Josie's porch, HOME_PORCH blocks from the Homestead waystone.
    // Checked FIRST, and only for the lamp block: it is Home-relative, not
    // anchor-relative, so it has to run before the anchor bail-out below.
    // -------------------------------------------------------------------
    if (!v.isDone('q90')) {
      const home = v.home()
      if (home) {
        const porch = [home[0] + v.C.HOME_PORCH[0], home[1] + v.C.HOME_PORCH[1], home[2] + v.C.HOME_PORCH[2]]
        if (Math.abs(b.x - porch[0]) <= 2 && Math.abs(b.y - porch[1]) <= 2 && Math.abs(b.z - porch[2]) <= 2) {
          v.addLamp(b.x, b.y, b.z)
          global.valleyServer.runCommandSilent('bossbar set valley:lamps value 40')
          v.sayAll('Josie', 'Forty lamps. Fifteen people. One winter that nobody leaves.')
          fire(player, 'q90')
          return
        }
      }
    }

    const anchor = v.anchor()
    if (!anchor) return
    const tol = v.C.LAMP_TOLERANCE
    let matched = null
    let route = null
    const tryRoute = (list, name) => {
      if (matched) return
      for (let i = 0; i < list.length; i++) {
        const p = [anchor[0] + list[i][0], anchor[1] + list[i][1], anchor[2] + list[i][2]]
        if (Math.abs(b.x - p[0]) <= tol && Math.abs(b.y - p[1]) <= tol && Math.abs(b.z - p[2]) <= tol) {
          matched = p; route = name; return
        }
      }
    }
    tryRoute(v.C.LAMPS_Q34, 'q34')
    tryRoute(v.C.LAMPS_Q74, 'q74')
    if (!matched) return

    v.addLamp(b.x, b.y, b.z)
    const total = v.lamps().length
    global.valleyServer.runCommandSilent('bossbar set valley:lamps value ' + Math.min(total, 40))

    if (route === 'q34' && !v.isDone('q34') && countOnRoute(v, anchor, v.C.LAMPS_Q34) >= v.C.LAMPS_Q34.length) {
      fire(player, 'q34')
    }
    if (route === 'q74' && !v.isDone('q74') && countOnRoute(v, anchor, v.C.LAMPS_Q74) >= v.C.LAMPS_Q74.length) {
      fire(player, 'q74')
    }
    return
  }

  // ---------------------------------------------------------------------
  // Q47 — "The Cell on the Wall." Fluxduct within 12 blocks of the inn.
  // (§12.1 C11: this proximity is a QUEST check, never a recipe condition.)
  // ---------------------------------------------------------------------
  if (id === 'thermal:energy_duct' && !v.isDone('q47')) {
    const inn = v.mark('inn')
    if (inn && Math.abs(b.x - inn[0]) <= 12 && Math.abs(b.y - inn[1]) <= 12 && Math.abs(b.z - inn[2]) <= 12) {
      fire(player, 'q47')
    }
    return
  }

  // ---------------------------------------------------------------------
  // Q53 — "The Order Board." A barrel beside Oda's board is the Delivery
  // Crate. Placement arms it; the poll below waits until it is actually fed.
  // (§12.3: FTB Quests reads inventory only, and querying an AE2 grid means
  //  touching AE2's internal API — so the crate is the interface.)
  // ---------------------------------------------------------------------
  if (id === 'minecraft:barrel' && !v.isDone('q53')) {
    const board = v.mark('board')
    if (board && Math.abs(b.x - board[0]) <= 10 && Math.abs(b.y - board[1]) <= 6 && Math.abs(b.z - board[2]) <= 10) {
      v.set('valley_crate_pos', b.x + ',' + b.y + ',' + b.z)
      v.say(player, 'Oda', "Crate's beside the board. Fill it and I'll stop asking.")
    }
  }
})

function countOnRoute(v, anchor, route) {
  const lamps = v.lamps()
  const tol = v.C.LAMP_TOLERANCE
  let n = 0
  for (let i = 0; i < route.length; i++) {
    const p = [anchor[0] + route[i][0], anchor[1] + route[i][1], anchor[2] + route[i][2]]
    for (let j = 0; j < lamps.length; j++) {
      if (Math.abs(lamps[j][0] - p[0]) <= tol &&
          Math.abs(lamps[j][1] - p[1]) <= tol &&
          Math.abs(lamps[j][2] - p[2]) <= tol) { n++; break }
    }
  }
  return n
}

// -----------------------------------------------------------------------------
// Q28 — "Read the Rock." Six uses of Tobin's prospector pick.
// Counted per world in persistentData, which is what the quest text promises
// ("the 6 spots he marked"), rather than off the cumulative vanilla stat.
// -----------------------------------------------------------------------------
ItemEvents.rightClicked('geolosys:prospectors_pick', event => {
  const v = V()
  if (!v || !global.valleyServer) return
  const player = event.player
  if (player.level.isClientSide()) return
  if (v.isDone('q28')) return
  const n = parseInt(v.get('valley_pick_uses', '0'), 10) + 1
  v.set('valley_pick_uses', n)
  if (n >= 6) {
    v.say(player, 'Tobin', "That's the six. Copper's under the third one, which — anyway. Copper.")
    fire(player, 'q28')
  }
})

// =============================================================================
// POLLED CHECKS — one pass every POLL_INTERVAL ticks
// =============================================================================

// ---- Q5: "Dig Out the Cellar Stairs." Player below the ruin floor. ---------
poll('q05', (server, player) => {
  const v = V()
  const home = v.home()
  if (!home) return false
  return v.flatDist(player, home) <= 16 && player.y <= home[1] + v.C.HOME_CELLAR_Y
})

// ---- Q55: "Read the Cellar Wall." Deeper, and only after Q54 has revealed it.
poll('q55', (server, player) => {
  const v = V()
  const home = v.home()
  if (!home) return false
  if (!v.hasWorldStage('act3')) return false
  return v.flatDist(player, home) <= 10 && player.y <= home[1] + v.C.HOME_DEEP_Y
})

// ---- Q10: "Three chickens standing inside the finished pen." --------------
poll('q10', (server, player) => {
  const v = V()
  const home = v.home()
  if (!home) return false
  if (v.flatDist(player, home) > 32) return false
  return v.countNear(player.level, home, 12, 'minecraft:chicken') >= 3
})

// ---- Q25: "2 cows and 2 sheep are standing inside the fenced pasture." ----
poll('q25', (server, player) => {
  const v = V()
  const home = v.home()
  if (!home) return false
  if (v.flatDist(player, home) > 40) return false
  return v.countNear(player.level, home, 24, 'minecraft:cow') >= 2 &&
         v.countNear(player.level, home, 24, 'minecraft:sheep') >= 2
})

// ---- Q22: "Catch 10 fish — Nella starts your count at zero." --------------
// The vanilla fish stat is cumulative (§12.4), so the baseline is taken the
// first time this check sees the player, which is the moment the quest opens.
poll('q22', (server, player) => {
  const v = V()
  if (!v.hasWorldStage('act2')) return false
  const name = v.pname(player)
  const key = 'valley_fish_base_' + name
  const now = player.stats.fishCaught
  const base = v.get(key, null)
  if (base === null) { v.set(key, now); return false }
  return (now - parseInt(base, 10)) >= 10
})

// ---- Q59: "The Reed Village Comes In." Walk the Ribbits home. -------------
// Satisfied when the player is standing with at least two Ribbits.
poll('q59', (server, player) => {
  const v = V()
  if (!v.hasWorldStage('act4')) return false
  const here = [player.x, player.y, player.z]
  return v.countNear(player.level, here, 8, 'ribbits:') >= 2
})

// ---- Q65: "Open the Works." Player inside the Works box. ------------------
poll('q65', (server, player) => {
  const v = V()
  return v.inBox(player, v.mark('works'), v.C.BOX.works)
})

// ---- Q82: "Deeper and Darker." Player inside the echo cave. ---------------
poll('q82', (server, player) => {
  const v = V()
  return v.inBox(player, v.mark('echo_cave'), v.C.BOX.echo_cave)
})

// ---- Q53: the Delivery Crate is placed AND fed. ---------------------------
poll('q53', (server, player) => {
  const v = V()
  const raw = v.get('valley_crate_pos', null)
  if (!raw) return false
  const parts = String(raw).split(',')
  const b = player.level.getBlock(
    parseInt(parts[0], 10), parseInt(parts[1], 10), parseInt(parts[2], 10))
  if (String(b.id) !== 'minecraft:barrel') return false
  const inv = b.inventory
  if (!inv) return false
  return !inv.isEmpty()
})

// -----------------------------------------------------------------------------
// Sleep — Q8, Q57, Q76.
// PlayerEvents has NO wakeUp/sleep event in KubeJS 2001.6.5 (verified against
// the jar). §12.4 also forbids the cumulative sleep_in_bed Stat task. So sleep
// is a two-state poll: we watch for sleeping -> awake and credit whichever
// sleep quest the world stage says is open.
// -----------------------------------------------------------------------------
const sleeping = {}

function checkSleep(server, player) {
  const v = V()
  const name = v.pname(player)
  const now = !!player.isSleeping()
  const was = !!sleeping[name]
  sleeping[name] = now
  if (!(was && !now)) return          // only the sleeping -> awake edge counts

  if (!v.isDone('q08')) { fire(player, 'q08'); return }
  if (v.hasWorldStage('act4') && !v.isDone('q57')) {
    v.say(player, 'Pip', "The hearth's out. Marnie says come down. She said it twice.")
    fire(player, 'q57'); return
  }
  if (v.hasWorldStage('act5') && !v.isDone('q76')) {
    v.say(player, 'Marnie', "Walk the square with me. It looks different in the light.")
    fire(player, 'q76')
  }
}

// -----------------------------------------------------------------------------
// The tick handler. One modulo, one length check, then at most POLLS.length
// cheap predicates per online player. POLLS shrinks as the pack is played.
// -----------------------------------------------------------------------------
ServerEvents.tick(event => {
  if (global.valleyTick % POLL_INTERVAL !== 0) return
  const v = V()
  if (!v || !global.valleyServer) return
  if (!prunedOnce) pruneFinished()
  const players = event.server.players
  if (players.length === 0) return

  players.forEach(player => {
    checkSleep(event.server, player)
    for (let i = POLLS.length - 1; i >= 0; i--) {
      const c = POLLS[i]
      let ok = false
      try { ok = c.need(event.server, player) } catch (err) {
        console.error('[valley] check ' + c.key + ' failed: ' + err)
        POLLS.splice(i, 1)
        continue
      }
      if (ok) fire(player, c.key)
    }
  })
})

// Drop checks that are already satisfied in this world, so a mid-game /reload
// does not re-poll finished work. Done lazily on the first poll rather than in
// ServerEvents.loaded, because server scripts load alphabetically and this file
// is registered before valley_core.js defines global.valley.
let prunedOnce = false

function pruneFinished() {
  const v = V()
  for (let i = POLLS.length - 1; i >= 0; i--) {
    if (v.isDone(POLLS[i].key)) POLLS.splice(i, 1)
  }
  prunedOnce = true
  console.info('[valley] checks armed: ' + POLLS.map(c => c.key).join(' ') + ' (+ sleep, + block/use listeners)')
}

ServerEvents.unloaded(event => { prunedOnce = false })
