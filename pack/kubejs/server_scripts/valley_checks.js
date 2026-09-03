// =============================================================================
// valley_checks.js — Little Kettle Valley: the "checkmark·kjs" auto-completions.
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
  let v = V()
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
  let v = V()
  if (!v || !global.valleyServer) return
  let b = event.block
  let id = String(b.id)
  let player = event.entity
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
      let p = v.offset(off)
      if (p) v.addLamp(p[0], p[1], p[2])
    })
    // ...and the two that valley:act1/square_path is about to setblock as
    // this quest's own reward. A setblock never fires this listener.
    v.C.LAMPS_Q07.forEach(off => {
      let p = v.offset(off)
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
    let home = v.home()
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
      let home = v.home()
      if (home) {
        let porch = [home[0] + v.C.HOME_PORCH[0], home[1] + v.C.HOME_PORCH[1], home[2] + v.C.HOME_PORCH[2]]
        if (Math.abs(b.x - porch[0]) <= 2 && Math.abs(b.y - porch[1]) <= 2 && Math.abs(b.z - porch[2]) <= 2) {
          v.addLamp(b.x, b.y, b.z)
          global.valleyServer.runCommandSilent('bossbar set valley:lamps value 40')
          v.sayAll('Josie', 'Forty lamps. Fifteen people. One winter that nobody leaves.')
          fire(player, 'q90')
          return
        }
      }
    }

    let anchor = v.anchor()
    if (!anchor) return
    let tol = v.C.LAMP_TOLERANCE
    let matched = null
    let route = null
    let tryRoute = (list, name) => {
      if (matched) return
      for (let i = 0; i < list.length; i++) {
        let p = [anchor[0] + list[i][0], anchor[1] + list[i][1], anchor[2] + list[i][2]]
        if (Math.abs(b.x - p[0]) <= tol && Math.abs(b.y - p[1]) <= tol && Math.abs(b.z - p[2]) <= tol) {
          matched = p; route = name; return
        }
      }
    }
    tryRoute(v.C.LAMPS_Q34, 'q34')
    tryRoute(v.C.LAMPS_Q74, 'q74')
    if (!matched) return

    v.addLamp(b.x, b.y, b.z)
    let total = v.lamps().length
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
  // Q47 — "The Cell on the Wall." Energy Duct within 12 blocks of the inn.
  // (§12.1 C11: this proximity is a QUEST check, never a recipe condition.)
  // ---------------------------------------------------------------------
  if (id === 'thermal:energy_duct' && !v.isDone('q47')) {
    let inn = v.mark('inn')
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
    let board = v.mark('board')
    if (board && Math.abs(b.x - board[0]) <= 10 && Math.abs(b.y - board[1]) <= 6 && Math.abs(b.z - board[2]) <= 10) {
      v.set('valley_crate_pos', b.x + ',' + b.y + ',' + b.z)
      v.say(player, 'Oda', "Crate's beside the board. Fill it and I'll stop asking.")
    }
  }
})

function countOnRoute(v, anchor, route) {
  let lamps = v.lamps()
  let tol = v.C.LAMP_TOLERANCE
  let n = 0
  for (let i = 0; i < route.length; i++) {
    let p = [anchor[0] + route[i][0], anchor[1] + route[i][1], anchor[2] + route[i][2]]
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
  let v = V()
  if (!v || !global.valleyServer) return
  let player = event.player
  if (player.level.isClientSide()) return
  if (v.isDone('q28')) return
  let n = parseInt(v.get('valley_pick_uses', '0'), 10) + 1
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
  let v = V()
  let home = v.home()
  if (!home) return false
  return v.flatDist(player, home) <= 16 && player.y <= home[1] + v.C.HOME_CELLAR_Y
})

// ---- Q55: "Read the Cellar Wall." Deeper, and only after Q54 has revealed it.
poll('q55', (server, player) => {
  let v = V()
  let home = v.home()
  if (!home) return false
  if (!v.hasWorldStage('act3')) return false
  return v.flatDist(player, home) <= 10 && player.y <= home[1] + v.C.HOME_DEEP_Y
})

// ---- Q10: "Three chickens standing inside the finished pen." --------------
poll('q10', (server, player) => {
  let v = V()
  let home = v.home()
  if (!home) return false
  if (v.flatDist(player, home) > 32) return false
  return v.countNear(player.level, home, 12, 'minecraft:chicken') >= 3
})

// ---- Q25: "2 cows and 2 sheep are standing inside the fenced pasture." ----
poll('q25', (server, player) => {
  let v = V()
  let home = v.home()
  if (!home) return false
  if (v.flatDist(player, home) > 40) return false
  return v.countNear(player.level, home, 24, 'minecraft:cow') >= 2 &&
         v.countNear(player.level, home, 24, 'minecraft:sheep') >= 2
})

// ---- Q22: "Catch 10 fish — Nella starts your count at zero." --------------
// The vanilla fish stat is cumulative (§12.4), so the baseline is taken the
// first time this check sees the player, which is the moment the quest opens.
poll('q22', (server, player) => {
  let v = V()
  if (!v.hasWorldStage('act2')) return false
  let name = v.pname(player)
  let key = 'valley_fish_base_' + name
  let now = player.stats.fishCaught
  let base = v.get(key, null)
  if (base === null) { v.set(key, now); return false }
  return (now - parseInt(base, 10)) >= 10
})

// ---- Q59: "The Reed Village Comes In." Walk the Ribbits home. -------------
// Satisfied when the player is standing with at least two Ribbits.
poll('q59', (server, player) => {
  let v = V()
  if (!v.hasWorldStage('act4')) return false
  let here = [player.x, player.y, player.z]
  return v.countNear(player.level, here, 8, 'ribbits:') >= 2
})

// ---- Q65: "Open the Works." Player inside the Works box. ------------------
poll('q65', (server, player) => {
  let v = V()
  return v.inBox(player, v.mark('works'), v.C.BOX.works)
})

// ---- Q82: "Deeper and Darker." Player inside the echo cave. ---------------
poll('q82', (server, player) => {
  let v = V()
  return v.inBox(player, v.mark('echo_cave'), v.C.BOX.echo_cave)
})

// ---- Q53: the Delivery Crate is placed AND fed. ---------------------------
poll('q53', (server, player) => {
  let v = V()
  let raw = v.get('valley_crate_pos', null)
  if (!raw) return false
  let parts = String(raw).split(',')
  let b = player.level.getBlock(
    parseInt(parts[0], 10), parseInt(parts[1], 10), parseInt(parts[2], 10))
  if (String(b.id) !== 'minecraft:barrel') return false
  let inv = b.inventory
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
  let v = V()
  let name = v.pname(player)
  let now = !!player.isSleeping()
  let was = !!sleeping[name]
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

// =============================================================================
// Standing: Trusted — q86_standing (§5, §12.3).
//
// "Six of eight neighbours' stories closed" is not expressible as an FTB Quests
// dependency (dependency_requirement is only ALL / ONE), so q86_standing is an
// INVISIBLE checkmark quest and this is the listener that ticks it. q86 then
// depends on it normally.
//
// The count is per TEAM and comes from the ledger in valley_core.js, which is
// written by a silent command reward on each of the eight closing quests:
//     /valley standing <key> {team}   (the FTB Teams short team name)
// That is deterministic and needs no quest API. Before counting we also ask the
// FTB XMod Compat KubeJS binding which of the eight FTB Quests itself considers
// complete, and fold any extras into the ledger — so a chain closed before this
// shipped still counts. When the binding is absent that call returns null and
// nothing changes.
//
// Runs every STANDING_INTERVAL ticks, per online player, and costs one
// persistentData read per chain once a team is already Trusted.
// =============================================================================
const STANDING_INTERVAL = 200          // ticks; ~10 seconds

function checkStanding(server, player) {
  let v = V()
  let team = v.teamId(player)
  if (v.standingGranted(team)) return

  // Top-up pass: whatever FTB Quests already knows goes into the ledger.
  let api = v.standingApiClosed(player)
  if (api) api.forEach(k => v.recordStanding(team, k))

  let closed = v.standingClosed(team)
  if (closed.length < v.STANDING_REQUIRED) return

  v.markStandingGranted(team)
  console.info('[valley] Standing: Trusted for team ' + team +
               ' (' + closed.length + '/8: ' + closed.join(' ') + ')')

  // Per team, not per world: complete for every online member of THIS team,
  // so a second party in the same world still has to earn its own Standing.
  server.players.forEach(p => {
    if (v.teamId(p) !== team) return
    v.complete(p, 'q86_standing')
  })
  v.say(player, 'Oda', 'Six of eight. I have written it down, which is the only vote that has ever mattered in this valley.')
}

// -----------------------------------------------------------------------------
// The tick handler. One modulo, one length check, then at most POLLS.length
// cheap predicates per online player. POLLS shrinks as the pack is played.
// -----------------------------------------------------------------------------
ServerEvents.tick(event => {
  if (global.valleyTick % POLL_INTERVAL !== 0) return
  let v = V()
  if (!v || !global.valleyServer) return
  if (!prunedOnce) pruneFinished()
  let players = event.server.players
  if (players.length === 0) return

  let slow = (global.valleyTick % STANDING_INTERVAL === 0)

  players.forEach(player => {
    checkSleep(event.server, player)
    if (slow) {
      try { checkStanding(event.server, player) }
      catch (err) { console.error('[valley] standing check failed: ' + err) }
    }
    for (let i = POLLS.length - 1; i >= 0; i--) {
      let c = POLLS[i]
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
  let v = V()
  for (let i = POLLS.length - 1; i >= 0; i--) {
    if (v.isDone(POLLS[i].key)) POLLS.splice(i, 1)
  }
  prunedOnce = true
  console.info('[valley] checks armed: ' + POLLS.map(c => c.key).join(' ') + ' (+ sleep, + block/use listeners)')
}

ServerEvents.unloaded(event => { prunedOnce = false })
