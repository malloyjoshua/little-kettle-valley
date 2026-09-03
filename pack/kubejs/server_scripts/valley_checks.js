// =============================================================================
// valley_checks.js — Little Kettle Valley: the "checkmark·kjs" auto-completions.
//
// §12.2 P2 — the KubeJS escape hatch. FTB Quests Location tasks are authored
// as fixed coordinates and cannot reference a runtime anchor, so every
// "be at / place / sleep / dig / keep N animals" gate is a CHECKMARK task
// completed by a listener calling /ftbquests change_progress.
//
// Every check in this file is latched once per TEAM in server.persistentData.
// It used to be once per WORLD, and the check then removed itself from the poll
// list on the first fire — which meant the first party to reach a quest turned
// the check off for everybody, and a second party was hard-stuck from Q2 on.
// Nothing is spliced out of POLLS any more; the per-team latch is the guard,
// and the poll loop skips a check for any player whose team has already
// satisfied it, so a finished pack still costs one flag read per check.
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
  let team = v.teamId(player)
  // Per TEAM. The check stays in POLLS for everyone else — see the header.
  if (!v.once(key, team)) return
  v.complete(player, key)
  console.info('[valley] check satisfied: ' + key + ' (team ' + team + ')')
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
  let team = v.teamId(player)

  // ---------------------------------------------------------------------
  // Q2 — "Put the Waystone on the Hearthstone."
  // Home is the waystone that lands ON the Kettle ruin's hearthstone — never
  // "the first waystone anywhere in the world", which is what this was and
  // which let a crafted waystone dropped at spawn become the reference point
  // for Q4, Q5, Q10, Q25, Q55 and Q90.
  // ---------------------------------------------------------------------
  if (id === 'waystones:waystone' && !v.isDone('q02', team)) {
    // Where the ruin is known, the waystone has to land ON the hearthstone —
    // that is the whole instruction, and accepting it anywhere left the ruin
    // unvisited and the cellar under open field. Off the mark, she is told
    // where the mark is instead of being silently failed.
    let ruin = v.ruin()
    if (ruin && !nearRuinHearth(b, ruin)) {
      v.say(player, 'Josie', 'Not there. The flat grey hearthstone by the chimney, at ' +
        ruin[0] + ' ' + ruin[1] + ' ' + ruin[2] + '.')
      return
    }
    // placeRuin() is wrapped in a try/catch, so valley_ruin CAN be missing —
    // and then the gate above is skipped and this waystone silently becomes
    // Home wherever it is. Accept it (refusing would hard-stop the pack at Q2)
    // but never do it silently: the op has to know the cottage, the cellar and
    // the porch lamp are all now measured from here.
    if (!ruin && !v.home()) {
      console.warn('[valley] no Kettle ruin recorded; Home is being set from a ' +
                   'waystone at ' + b.x + ' ' + b.y + ' ' + b.z + ' instead of the hearthstone.')
      global.valleyServer.runCommandSilent(
        'tellraw @a ' + JSON.stringify({
          text: 'No ruin was recorded for this world, so Home is being set here (' +
                b.x + ' ' + b.y + ' ' + b.z + '). An op can move it with /valley home set.',
          color: 'gold'
        }))
    }
    // Home itself is one place per world (the cellar, Q5, Q55 and Q90 all
    // measure from it), so only the first party sets it; a later party still
    // gets the tick for putting their waystone on the same hearth.
    if (!v.home()) v.setHome(b.x, b.y, b.z)
    global.valleyServer.runCommandSilent(
      'setblock ' + b.x + ' ' + b.y + ' ' + b.z + ' waystones:waystone{WaystoneName:"Home"}')
    v.say(player, 'Josie', 'That is where the hearth was. Good.')
    // The repair is centred on the HEARTHSTONE, not on wherever the player is
    // standing when they claim. Once per world: a second party's waystone must
    // not re-fill the walls and delete the door, windows and bed the first
    // party hung. (This was q02's command reward until the ruin existed.)
    if (v.once('cottage_built')) {
      global.valleyServer.runCommandSilent(
        'execute positioned ' + b.x + ' ' + b.y + ' ' + b.z + ' run function valley:act1/cottage')
    }
    fire(player, 'q02')
    return
  }

  // ---------------------------------------------------------------------
  // Q7 — "Place the Surveyor's Stake North of Your Gate."
  // THE anchor listener. Everything anchor-relative in the pack — every
  // finale, every mark, every lamp — depends on this one block placement.
  // ---------------------------------------------------------------------
  if (id === 'valley:town_anchor') {
    // There is exactly ONE town, so only the first stake in the world moves
    // the anchor. A second party driving a stake still gets Q7 ticked; the
    // valley does not relocate around them.
    let setAnchorAt = v.anchor()
    if (setAnchorAt && (setAnchorAt[0] !== b.x || setAnchorAt[1] !== b.y || setAnchorAt[2] !== b.z)) {
      // A stake is a plain Q6 reward and is craftable from 1 copper + 6 stone
      // bricks, so a second one WILL get placed — by a friend tidying up, or by
      // whoever finds the spare in a chest in Act IV. Say so out loud instead of
      // leaving them to wonder why the town did not move.
      global.valleyServer.runCommandSilent(
        'tellraw ' + v.pname(player) + ' ' + JSON.stringify({
          text: 'The Town Anchor is already set at ' + setAnchorAt.join(' ') +
                ' — an op can move it with /valley anchor set.',
          color: 'gold'
        }))
    }
    if (!setAnchorAt) {
      v.setAnchor(b.x, b.y, b.z)
      global.valleyServer.runCommandSilent(
        'tellraw @a ' + JSON.stringify({
          text: 'Town Anchor set at ' + b.x + ' ' + b.y + ' ' + b.z + '. This is where the town will be.',
          color: 'gold'
        }))
      // Record the lamp posts the Act I finale is about to place, so the Act IV
      // lever relights the whole road and not just the stretches she built.
      // A LAMPS_* offset is the POST's y; the lamp itself sits LAMP_HEAD above
      // it, and the lamp is what the Act IV sweep sets, so that is what goes in
      // the list.
      v.C.LAMPS_FINALE.forEach(off => {
        let p = v.offset(off)
        if (p) v.addLamp(p[0], p[1] + v.C.LAMP_HEAD, p[2])
      })
      // ...and the two that valley:act1/square_path is about to setblock as
      // this quest's own reward. A setblock never fires this listener.
      v.C.LAMPS_Q07.forEach(off => {
        let p = v.offset(off)
        if (p) v.addLamp(p[0], p[1] + v.C.LAMP_HEAD, p[2])
      })
    }
    fire(player, 'q07')
    return
  }

  // ---------------------------------------------------------------------
  // Q4 — "Place the Megatorch Inside the Cottage."
  // Within 32 of Home (§12.4: "megatorch within 32 of Home").
  // ---------------------------------------------------------------------
  if (id === 'torchmaster:megatorch' && !v.isDone('q04', team)) {
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
    if (!v.isDone('q90', team)) {
      let home = v.home()
      if (home) {
        let porch = [home[0] + v.C.HOME_PORCH[0], home[1] + v.C.HOME_PORCH[1], home[2] + v.C.HOME_PORCH[2]]
        if (Math.abs(b.x - porch[0]) <= 2 && Math.abs(b.y - porch[1]) <= 2 && Math.abs(b.z - porch[2]) <= 2) {
          v.addLamp(b.x, b.y, b.z)
          // The fortieth. Every other post on the road has been burning since
          // Bram pulled the lever, so this one lights the moment it lands —
          // and it is force-set, because a cage lamp placed by hand comes down
          // dark and facing whatever face the player clicked.
          global.valleyServer.runCommandSilent(
            'setblock ' + b.x + ' ' + b.y + ' ' + b.z + ' ' + v.C.LAMP_LIT)
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
    // Normalise the post the moment it lands. CageLampBlock's placement state
    // takes `facing` from the face the player clicked, so a post set against a
    // wall or the underside of a slab ends up a sconce; and it comes down with
    // inverted=false, which shouldBeLit reads as dark. Both are what we want
    // for a road post — it stays dark until Bram pulls the lever — but only if
    // the state is written down rather than left to how she happened to click.
    global.valleyServer.runCommandSilent(
      'setblock ' + b.x + ' ' + b.y + ' ' + b.z + ' ' + v.C.LAMP_DARK)
    let total = v.lamps().length
    global.valleyServer.runCommandSilent('bossbar set valley:lamps value ' + Math.min(total, 40))

    if (route === 'q34' && !v.isDone('q34', team) && countOnRoute(v, anchor, v.C.LAMPS_Q34) >= v.C.LAMPS_Q34.length) {
      fire(player, 'q34')
    }
    if (route === 'q74' && !v.isDone('q74', team) && countOnRoute(v, anchor, v.C.LAMPS_Q74) >= v.C.LAMPS_Q74.length) {
      fire(player, 'q74')
    }
    return
  }

  // ---------------------------------------------------------------------
  // Q47 — "The Cell on the Wall." Energy Duct within 12 blocks of the inn.
  // (§12.1 C11: this proximity is a QUEST check, never a recipe condition.)
  // ---------------------------------------------------------------------
  if (id === 'thermal:energy_duct' && !v.isDone('q47', team)) {
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
  if (id === 'minecraft:barrel' && !v.isDone('q53', team)) {
    let board = v.mark('board')
    if (board && Math.abs(b.x - board[0]) <= 10 && Math.abs(b.y - board[1]) <= 6 && Math.abs(b.z - board[2]) <= 10) {
      v.set('valley_crate_pos', b.x + ',' + b.y + ',' + b.z)
      v.say(player, 'Oda', "Crate's beside the board. Fill it and I'll stop asking.")
    }
  }
})

// Q2's mark. The hearthstone is one block, but she is placing a waystone by
// hand on a 9x9 floor, so the accept box is generous horizontally and tight
// vertically: anywhere in the ruin's front room counts, the yard does not.
function nearRuinHearth(b, ruin) {
  return Math.abs(b.x - ruin[0]) <= 4 &&
         Math.abs(b.z - ruin[2]) <= 4 &&
         Math.abs(b.y - ruin[1]) <= 3
}

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
// Q1 — "Read Josie's Letter."
// The letter is a vanilla written_book built in valley_core.js, so clicking it
// opens the real four-page book screen. THAT is what ticks Q1. The task used to
// be "hold valley:letter", which the first-join gift satisfied before she had
// read a word — the quest was green on the title screen.
//
// Q1's task is a CHECKMARK, so this listener is a convenience, not a gate: if
// right-click ever fails to reach the server, the box is still tickable by hand
// in the quest book and quest 1 cannot wall.
// -----------------------------------------------------------------------------
function letterRead(player) {
  let v = V()
  if (!v || !global.valleyServer) return
  if (!player || player.level.isClientSide()) return
  if (v.isDone('q01', v.teamId(player))) return
  v.say(player, 'Josie', 'Four pages and a chimney. Go and look at it.')
  fire(player, 'q01')
}

ItemEvents.rightClicked('minecraft:written_book', event => {
  try {
    let stack = event.item
    let nbt = stack ? stack.nbt : null
    if (!nbt || String(nbt.getString('title')) !== "Josie's Letter") return
  } catch (err) {
    return
  }
  letterRead(event.player)
})

// The keepsake copy. valley:letter is still registered and is still Q1's icon,
// and it is what josieLetter() falls back to, so it reads the same way.
ItemEvents.rightClicked('valley:letter', event => letterRead(event.player))

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
  let team = v.teamId(player)
  if (v.isDone('q28', team)) return
  // Per team, or the second party inherits the first party's six strikes and
  // Q28 completes on their very first swing.
  let slot = 'valley_pick_uses_' + String(team).replace(/[^A-Za-z0-9]/g, '')
  let n = parseInt(v.get(slot, '0'), 10) + 1
  v.set(slot, n)
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

  let team = v.teamId(player)
  if (!v.isDone('q08', team)) { fire(player, 'q08'); return }
  if (v.hasWorldStage('act4') && !v.isDone('q57', team)) {
    v.say(player, 'Pip', "The hearth's out. Marnie says come down. She said it twice.")
    fire(player, 'q57'); return
  }
  if (v.hasWorldStage('act5') && !v.isDone('q76', team)) {
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
// Q7 — the ground that goes green.
//
// Q7 told her to "walk until the ground under your feet turns green" and
// nothing in the pack turned any ground any colour. The anchor listener above
// fires on PLACEMENT only, there is no zone test, and Q7's own reward is the
// road — so the walk that decides where all ninety-nine remaining quests get
// measured from had zero feedback, and the one judgement call in Act I was the
// one she is least equipped to make.
//
// This is the signal the text promises. While the world has no anchor and she
// is holding the Surveyor's Stake, a ring of green sparks comes up around her
// feet whenever she is standing far enough north of Home on a level 5x5 pad
// with headroom. Josie says it once, and once more with a way out if the
// terrain up there never offers a flat spot.
//
// It is help, never a gate: the anchor listener still accepts a stake placed
// anywhere, so a player who ignores the sparks loses nothing.
// -----------------------------------------------------------------------------
const STAKE_ITEM      = 'valley:town_anchor'
const STAKE_NORTH_MIN = 30     // blocks north of Home: past the garden
const STAKE_NORTH_MAX = 96     // and still this valley
const STAKE_SIDE_MAX  = 48     // "up the road", not over the ridge
const STAKE_PAD       = 2      // a 5x5 pad, level, two blocks of headroom
const STAKE_NUDGE_AT  = 30     // polls (~30s) in range with no green

let stakeGuideOff = false      // one thrown error disables it for the session
const stakeSearching = {}      // team -> consecutive in-range polls with no pad

// Mojang names both getters exactly once, and they do not match each other:
// getMainHandItem() / getOffhandItem() (server-1.20.1 mappings, lines 1924 and
// 1928), so the bean properties are `mainHandItem` and `offhandItem`.
//
// A wrong property name here would return undefined and read as "not holding
// it", which is a signal that silently never fires — the exact failure this
// whole fix exists to remove. So an unreadable hand is NOT a no: if neither
// hand can be read at all, the guide falls back to "the world has no anchor and
// she is standing in the right place", which is still the right thing to show.
function holdingStake(player) {
  let m = player.mainHandItem
  let o = player.offhandItem
  if (m === undefined && o === undefined) return true    // API mismatch: don't gate
  if (m && !m.isEmpty() && String(m.id) === STAKE_ITEM) return true
  return !!(o && !o.isEmpty() && String(o.id) === STAKE_ITEM)
}

// Level, solid, walkable, clear overhead. Deliberately loose: a 5x5 of
// same-height non-fluid ground with two open blocks above it. Blocks are read
// by id rather than isAir(), which is the idiom the rest of this pack already
// uses against this KubeJS build (valley_core.js ruinSurface, dredgePull).
const AIR = 'minecraft:air'

function padIsFlat(level, x, y, z) {
  for (let dx = -STAKE_PAD; dx <= STAKE_PAD; dx++) {
    for (let dz = -STAKE_PAD; dz <= STAKE_PAD; dz++) {
      let gid = String(level.getBlock(x + dx, y - 1, z + dz).id)
      if (gid === AIR) return false
      if (gid.indexOf('water') >= 0 || gid.indexOf('lava') >= 0) return false
      if (String(level.getBlock(x + dx, y, z + dz).id) !== AIR) return false
      if (String(level.getBlock(x + dx, y + 1, z + dz).id) !== AIR) return false
    }
  }
  return true
}

function stakeGuide(server, player) {
  if (stakeGuideOff) return
  let v = V()
  if (v.anchor()) return
  if (!holdingStake(player)) return
  let home = v.home()
  if (!home) return

  let x = Math.floor(player.x), y = Math.floor(player.y), z = Math.floor(player.z)
  let north = home[2] - z
  if (north < STAKE_NORTH_MIN || north > STAKE_NORTH_MAX) return
  if (Math.abs(x - home[0]) > STAKE_SIDE_MAX) return

  let team = v.teamId(player)
  if (!padIsFlat(player.level, x, y, z)) {
    // She is in the right part of the valley and the ground keeps saying no.
    // Rather than let her walk to the world border, tell her the pad is the
    // only requirement and that she is allowed to make one.
    stakeSearching[team] = (stakeSearching[team] || 0) + 1
    if (stakeSearching[team] === STAKE_NUDGE_AT && v.once('q07_nudge', team)) {
      v.say(player, 'Josie',
        'Nothing flat up here? Then flatten a five-by-five and stake that. Level is the whole requirement.')
    }
    return
  }

  server.runCommandSilent(
    'particle minecraft:happy_villager ' + (x + 0.5) + ' ' + (y + 0.1) + ' ' + (z + 0.5) +
    ' 2.4 0.1 2.4 0 40 force ' + v.pname(player))
  if (v.once('q07_green', team)) {
    v.say(player, 'Josie',
      'That is the flat Bram surveyed twice and never staked. Green means yes — put it down.')
  }
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
    // Pre-Q7 only: bails on one flag read the moment the anchor exists.
    try { stakeGuide(event.server, player) }
    catch (err) {
      stakeGuideOff = true
      console.error('[valley] Q7 stake guide disabled after: ' + err)
    }
    if (slow) {
      try { checkStanding(event.server, player) }
      catch (err) { console.error('[valley] standing check failed: ' + err) }
    }
    let team = v.teamId(player)
    for (let i = POLLS.length - 1; i >= 0; i--) {
      let c = POLLS[i]
      // One flag read, per player, for work this player's team has finished.
      // This is what replaces the old splice: the check stays armed for every
      // OTHER team in the world.
      if (v.isDone(c.key, team)) continue
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

// One line in the log saying what is armed. This used to DROP every check the
// world had already seen, which is the same bug as the splice in fire(): a
// second party's checks were pruned away before they ever ran one. Nothing is
// removed here any more — the per-team latch read in the poll loop is what
// keeps a finished check cheap. Done lazily on the first poll rather than in
// ServerEvents.loaded, because server scripts load alphabetically and this file
// is registered before valley_core.js defines global.valley.
let prunedOnce = false

function pruneFinished() {
  prunedOnce = true
  console.info('[valley] checks armed: ' + POLLS.map(c => c.key).join(' ') + ' (+ sleep, + block/use listeners)')
}

ServerEvents.unloaded(event => { prunedOnce = false })
