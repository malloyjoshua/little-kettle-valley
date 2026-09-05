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

// `heavy` marks a check that READS A BOX of blocks rather than one cell. Those run on the
// slow tick (every HEAVY_INTERVAL) instead of every second: Q47's is a 25x13x25 read, and
// at 1 Hz per player that is eight thousand block lookups a second for a quest nobody has
// opened yet.
function poll(key, need, heavy) { POLLS.push({ key: key, need: need, heavy: !!heavy }) }

const HEAVY_INTERVAL = 100      // ticks; ~5 seconds

// -----------------------------------------------------------------------------
// The registry. Every coordinate this file tests against is a constant in
// pack/kubejs/data/valley/valley_sites.json, loaded by valley_sites.js.
//
// WHAT USED TO BE HERE: townBox(), hearthXZ() and townWouldSwallow() — a clearance rule
// that grew the whole town's footprint out of town_plan.js and refused a Surveyor's Stake
// driven anywhere inside it, because Q7 was "walk north until the ground is flat and drive
// the stake, and the entire valley will be measured from wherever you stopped". There is
// nothing left to measure: the square is paved, the stake's socket is chiselled into it,
// and Q7 is "put the stake in the socket". The rule, its 30..140-block window, its
// side-max, its per-poll pad probe and its green-sparks guide all go with it.
// -----------------------------------------------------------------------------
function site(path) {
  let v = V()
  return v ? v.site(path) : null
}

// Is [x,y,z] within `r` of the registry point at `path`?
function atSite(pos, path, r) {
  let t = site(path)
  if (!t) return false
  return Math.abs(pos[0] - t[0]) <= r && Math.abs(pos[1] - t[1]) <= r && Math.abs(pos[2] - t[2]) <= r
}

// Is the player standing inside a registry box [x0,y0,z0,x1,y1,z1]? Half a block of slack
// on every face, because a player's feet sit at the box's floor, not in it.
function inSiteBox(player, box) {
  if (!box) return false
  return player.x >= box[0] - 0.5 && player.x <= box[3] + 1.5 &&
         player.y >= box[1] - 0.5 && player.y <= box[4] + 1.5 &&
         player.z >= box[2] - 0.5 && player.z <= box[5] + 1.5
}

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
    // The hearthstone is a registry constant: the flat grey block in the middle of a
    // cottage that has been standing there since before she logged in. Off the mark, she
    // is told where the mark is instead of being silently failed.
    let hearth = v.hearth()
    if (hearth && !nearHearth(b, hearth)) {
      v.say(player, 'Josie', 'Not there. The flat grey hearthstone in the middle of the floor, at ' +
        hearth[0] + ' ' + hearth[1] + ' ' + hearth[2] + '.')
      return
    }
    // Home is one place per world, and after this it is the waystone cell rather than the
    // stone under it. Nothing is built, nothing is replaced: the farm stands as found, and
    // Q3 hands the door, the windows, the bed and the sconce for the player to hang.
    if (!v.homeSet()) v.setHome(b.x, b.y, b.z)
    v.say(player, 'Josie', 'That is where the hearth was. Good.')
    fire(player, 'q02')
    return
  }

  // ---------------------------------------------------------------------
  // Q7 — "Drive the Surveyor's Stake into the Socket on the Square."
  //
  // The socket is a chiselled stone-brick cell in the middle of the square, two north of
  // the town waystone, with Bram's sign beside it (day1_board). It has been there since
  // before she arrived. This used to be the single most consequential decision in the
  // pack — every pad, street, lamp and the Works were measured off wherever the stake
  // landed — and it is now what it always read like in the text: forty years of nearly,
  // and somebody finally drives it in.
  // ---------------------------------------------------------------------
  if (id === 'valley:town_anchor') {
    let socket = site('stake_socket')
    if (socket && !(Math.abs(b.x - socket[0]) <= 1 && Math.abs(b.y - socket[1]) <= 1 &&
                    Math.abs(b.z - socket[2]) <= 1)) {
      let srv = global.valleyServer
      srv.runCommandSilent('setblock ' + b.x + ' ' + b.y + ' ' + b.z + ' minecraft:air')
      srv.runCommandSilent('give ' + v.pname(player) + ' valley:town_anchor 1')
      srv.runCommandSilent('title ' + v.pname(player) + ' actionbar ' + JSON.stringify({
        text: 'The socket is on the square, at ' + socket.join(' ') + '.', color: 'red' }))
      v.say(player, 'Josie',
        'Not there. Bram cut a socket for it in the middle of the square and then never drove it. Use his socket.')
      return
    }
    if (v.once('q07_driven')) {
      global.valleyServer.runCommandSilent('tellraw @a ' + JSON.stringify({
        text: 'The Surveyor\'s Stake is in. Forty years of nearly, and the square has a town in it.',
        color: 'gold' }))
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
  // Q90 — "The Last Lamp."
  //
  // The fortieth post is a bare oak fence on Josie's porch: thirty-nine posts ship with a
  // dark cage lamp on them and this one ships with nothing, which is the whole of the
  // payoff §5 row 1 names. Any light the player hangs on it counts — the quest hands her a
  // Lantern and Josie's Lantern, and refusing one because it was the wrong one of the two
  // would be a cruel way to end the pack.
  // ---------------------------------------------------------------------
  if (!v.isDone('q90', team) &&
      (id === v.C.LAMP_BLOCK || id === 'minecraft:lantern' || id === 'valley:josies_lantern')) {
    let porch = v.C.LAMPS_Q90 && v.C.LAMPS_Q90.length ? v.C.LAMPS_Q90[0] : null
    if (porch && Math.abs(b.x - porch[0]) <= 1 && Math.abs(b.y - porch[1]) <= 1 &&
        Math.abs(b.z - porch[2]) <= 1) {
      // It lights on the spot: every other post on the road has been burning since Bram
      // pulled the lever, and this one is the line closing.
      global.valleyServer.runCommandSilent(
        'setblock ' + porch[0] + ' ' + porch[1] + ' ' + porch[2] + ' ' + v.C.LAMP_LIT)
      v.setLampsLit(40)
      v.sayAll('Josie', 'Forty lamps. Fifteen people. One winter that nobody leaves.')
      fire(player, 'q90')
      return
    }
  }

  // ---------------------------------------------------------------------
  // Q34 and Q74 — running the line.
  //
  // The forty posts are IN THE WORLD, dark, from the first second, so neither of these is
  // "place a lamp post" any more. Q34 is the duct from the Stirling Dynamo out to the four
  // marked posts between the mill and the square; Q74 is walking the whole line, mill to
  // square to lake to farm, which is what its own text has always said the duct does
  // ("the duct runs itself along the line as you go"). Both are satisfied against the
  // registry's own lamp cells, and the scene that pays each one is what LIGHTS them.
  // ---------------------------------------------------------------------
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

// Q2's mark. The hearthstone is one block, but she is placing a waystone by hand on a 9x9
// floor, so the accept box is generous horizontally and tight vertically: anywhere in the
// cottage's front room counts, the yard does not.
function nearHearth(b, hearth) {
  return Math.abs(b.x - hearth[0]) <= 4 &&
         Math.abs(b.z - hearth[2]) <= 4 &&
         Math.abs(b.y - hearth[1]) <= 3
}

// How much slack a length of Energy Duct gets against a lamp post's own cell (Q34).
const DUCT_REACH = 6
const Q34_NEED = 2          // "run duct to the nearest two" — the other two light with them

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
// A5 -- the kill switch for the login nudge.
// valley_core.js sends one aqua "right-click the Quest Book" line on every login
// while the player lacks the read_quest stage. Opening the book once sets that
// stage permanently, so the nudge is gone from that moment on, for this login and
// every future one. This is Create: Astral's exact mechanism (its interaction.js
// gates the same line on the same stage name).
//
// Not a quest gate: nothing in the book depends on read_quest, so a right-click
// that never reaches the server costs the player a chat line and nothing else.
// -----------------------------------------------------------------------------
ItemEvents.rightClicked('ftbquests:book', event => {
  let player = event.player
  if (!player || player.level.isClientSide()) return
  if (!player.stages.has('read_quest')) player.stages.add('read_quest')
})

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
// SLOW POLLS — one pass every SLOW_INTERVAL ticks, and they READ THE WORLD.
//
// Every "did she put X down at Y" check in this pack used to be a BlockEvents.placed
// listener and nothing else. Two things are wrong with that, and the second one is why
// this section exists:
//
//   1. `/setblock` does not fire BlockEvents.placed. Neither does a block placed by a
//      Create deployer, a Building Gadget, a schematic, or anything else that is not a
//      hand. So a player who builds with a mod the pack ships could not finish Q3.
//   2. It is untestable. The harness cannot press a mouse button, so the whole class of
//      "she placed it" checks was proved by nothing at all — every previous playthrough
//      ticked those quests with `ftbquests change_progress` and moved on.
//
// The registry made the fix cheap: every one of these has a KNOWN CELL now, so the check
// is a block read at a constant coordinate rather than a search. The event listeners above
// stay, because they are what says "not there, the hearthstone is at ..." in the second a
// player gets it wrong; these are the authority.
// =============================================================================
const SLOW_INTERVAL = 40        // ticks; ~2 seconds

// Does any cell within `r` of `centre` hold a block whose id contains `needle`? Bounded and
// only ever called for a check the team has not finished.
function nearBlock(level, centre, r, ry, needle) {
  for (let dx = -r; dx <= r; dx++) {
    for (let dz = -r; dz <= r; dz++) {
      for (let dy = -ry; dy <= ry; dy++) {
        if (String(level.getBlock(centre[0] + dx, centre[1] + dy, centre[2] + dz).id)
              .indexOf(needle) >= 0) return true
      }
    }
  }
  return false
}

// ---- Q2: the Homestead Waystone is standing on the hearthstone. -----------
poll('q02', (server, player) => {
  let v = V()
  let h = v.hearth()
  if (!h) return false
  let cell = [h[0], h[1] + 1, h[2]]
  if (String(player.level.getBlock(cell[0], cell[1], cell[2]).id).indexOf('waystone') < 0) return false
  if (!v.homeSet()) v.setHome(cell[0], cell[1], cell[2])
  return true
})

// ---- Q4: the Megatorch is inside the cottage. -----------------------------
// A 13x7x13 read, twice a second at most, and only until the first team ticks it.
poll('q04', (server, player) => {
  let v = V()
  let home = v.home()
  if (!home) return false
  if (v.flatDist(player, home) > 32) return false
  return nearBlock(player.level, home, 6, 3, 'megatorch')
}, true)

// ---- Q7: the Surveyor's Stake is in Bram's socket. ------------------------
poll('q07', (server, player) => {
  let v = V()
  let s = site('stake_socket')
  if (!s) return false
  return String(player.level.getBlock(s[0], s[1], s[2]).id) === 'valley:town_anchor'
})

// ---- Q47: an Energy Duct within 12 of the inn's own hearth. ---------------
poll('q47', (server, player) => {
  let v = V()
  if (!v.hasWorldStage('act3')) return false
  let inn = v.mark('inn')
  if (!inn) return false
  if (v.flatDist(player, inn) > 48) return false
  return nearBlock(player.level, inn, 12, 6, 'energy_duct')
}, true)

// ---- Q34: the duct has reached at least two of the four marked posts. -----
poll('q34', (server, player) => {
  let v = V()
  let posts = v.lampsOnRoute('q34')
  if (!posts.length) return false
  let n = 0
  for (let i = 0; i < posts.length; i++) {
    if (nearBlock(player.level, posts[i], DUCT_REACH, DUCT_REACH, 'energy_duct')) n++
  }
  if (n > 0 && n < Q34_NEED) {
    global.valleyServer.runCommandSilent('title ' + v.pname(player) + ' actionbar ' +
      JSON.stringify({ text: 'Duct run to ' + n + ' of ' + posts.length + ' posts.', color: 'gold' }))
  }
  return n >= Q34_NEED
}, true)

// ---- Q90: a light is on Josie's bare post. --------------------------------
poll('q90', (server, player) => {
  let v = V()
  let porch = v.C.LAMPS_Q90 && v.C.LAMPS_Q90.length ? v.C.LAMPS_Q90[0] : null
  if (!porch) return false
  let id = String(player.level.getBlock(porch[0], porch[1], porch[2]).id)
  if (id.indexOf('lamp') < 0 && id.indexOf('lantern') < 0) return false
  global.valleyServer.runCommandSilent(
    'setblock ' + porch[0] + ' ' + porch[1] + ' ' + porch[2] + ' ' + v.C.LAMP_LIT)
  v.setLampsLit(40)
  v.sayAll('Josie', 'Forty lamps. Fifteen people. One winter that nobody leaves.')
  return true
})

// =============================================================================
// POLLED CHECKS — one pass every POLL_INTERVAL ticks
// =============================================================================

// ---- Q3: "Hang the Door, Windows, Bed and Sconce." ------------------------
// The cottage ships with the holes in it: the planner pulls the template's own door, its
// window panes and its bed out at build time and leaves the openings, the wool mat and the
// hook. So this reads the registry's own gap cells and asks whether the player has filled
// them. Deliberately generous about WHICH door and WHICH window: the quest hands her an Oak
// Cottage Door and two Oak Windows, but any door in the doorway and any pane or window in a
// window hole is a house with the weather kept out, which is the point of the quest.
poll('q03', (server, player) => {
  let v = V()
  let c = site('cottage')
  if (!c) return false
  if (v.flatDist(player, v.home()) > 24) return false
  let level = player.level
  let at = p2 => String(level.getBlock(p2[0], p2[1], p2[2]).id)

  if (c.door && at(c.door).indexOf('door') < 0) return false

  let glazed = 0
  let wins = c.windows || []
  for (let i = 0; i < wins.length; i++) {
    let id = at(wins[i])
    if (id.indexOf('glass') >= 0 || id.indexOf('window') >= 0 || id.indexOf('pane') >= 0) glazed++
  }
  if (glazed < 2) return false

  // the bed goes ON the wool mat, so the cell that has to hold it is one up
  if (c.bed && at([c.bed[0], c.bed[1] + 1, c.bed[2]]).indexOf('bed') < 0) return false

  // the sconce goes on the hook: the oak fence post the planner leaves standing by the door
  if (c.sconce) {
    let id = at(c.sconce)
    if (id.indexOf('sconce') < 0 && id.indexOf('lantern') < 0 && id.indexOf('torch') < 0 &&
        id.indexOf('candle') < 0) return false
  }
  return true
})

// ---- Q5: "Dig Out the Cellar Stairs." -------------------------------------
// Forty blocks of gravel over a real stone-brick flight, and at the bottom a room with a
// sealed iron door in it. Both are in the world from the first second (day1_cellar), so
// this is simply "you are in the room", against the registry's own shell box. It used to
// be "your feet are three blocks below the waystone", which the cottage's own floor
// satisfies from the far side of a wall.
poll('q05', (server, player) => {
  let v = V()
  return inSiteBox(player, v.C.CELLAR_BOX)
})

// ---- Q55: "Read the Cellar Wall." The same room, after Act III opened the door.
poll('q55', (server, player) => {
  let v = V()
  if (!v.hasWorldStage('act3')) return false
  return inSiteBox(player, v.C.CELLAR_BOX)
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

// ---- Q65: "Open the Works." Player inside the Works chamber. --------------
// The chamber is sealed rock on six sides and the only way in is the fallen adit — forty
// blocks of cobblestone in a lined shaft off the East Lane verge (day1_adit). Standing in
// the room means the fall is mined, which is the whole task.
poll('q65', (server, player) => {
  let v = V()
  return inSiteBox(player, site('works.shell'))
})

// ---- Q74: "Run the Line, Mill to Square to Lake." -------------------------
// The posts are already standing. The duct lays itself along the line as she walks it
// (which is what Q74's own text has always said), so the check is that she has actually
// been to every one of them. One flag per post per team; the last one fires the quest and
// the scene lights the whole stretch.
poll('q74', (server, player) => {
  let v = V()
  // NOT gated on stage act4. The posts have stood there since the first second, so a player
  // who has already walked the road end to end has already done the thing this asks for, and
  // the quest should tick the moment it opens rather than sending her back down a road she
  // just came up. FTB Quests' own dependency chain is what makes it unavailable before then.
  let posts = v.lampsOnRoute('q74')
  if (!posts.length) return false
  let team = v.teamId(player)
  let done = 0
  let justHit = -1
  for (let i = 0; i < posts.length; i++) {
    if (v.isDone('q74p' + i, team)) { done++; continue }
    if (Math.abs(player.x - posts[i][0]) <= 6 && Math.abs(player.z - posts[i][2]) <= 6 &&
        Math.abs(player.y - posts[i][1]) <= 8) {
      v.once('q74p' + i, team)
      done++
      justHit = i
    }
  }
  if (justHit >= 0 && done < posts.length) {
    global.valleyServer.runCommandSilent('title ' + v.pname(player) + ' actionbar ' +
      JSON.stringify({ text: 'The line is run to ' + done + ' of ' + posts.length + ' posts.',
                       color: 'gold' }))
  }
  return done >= posts.length
})

// ---- Q82: "Deeper and Darker." Player inside the echo cave. ---------------
poll('q82', (server, player) => {
  let v = V()
  return v.inBox(player, v.mark('echo_cave'), [8, 6, 8])
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
// Q7's green sparks are gone, and so is everything they were guiding.
//
// What stood here: a per-poll 5x5 flatness probe, a north-of-home window, a side-max, a
// nudge counter and a ring of happy_villager particles that came up round the player's feet
// wherever the ground would hold a town — because Q7 used to be a judgement call ("walk
// north until the ground turns green") that decided where all ninety-nine remaining quests
// would be measured from.
//
// The valley is built. Bram's socket is chiselled into the middle of the square with his
// own sign beside it, and Q7 is "put the stake in the socket" — which needs no guide,
// cannot be got wrong, and is what the quest's own line always meant: "Bram surveyed that
// flat by the road twice and never drove the stake."
// -----------------------------------------------------------------------------

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
  let heavyTick = (global.valleyTick % HEAVY_INTERVAL === 0)

  players.forEach(player => {
    checkSleep(event.server, player)
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
      if (c.heavy && !heavyTick) continue
      let ok = false
      // A predicate that throws is logged and SKIPPED for this tick only.
      // This used to POLLS.splice(i, 1), which is world-level surgery in a
      // per-player loop: one bad tick — a null level, a player mid-dimension-
      // change — disarmed that check for EVERY team in the world, permanently,
      // and the quest it feeds could never fire again. Same bug as the old
      // splice in fire(); same fix. Nothing is ever removed from POLLS.
      try { ok = c.need(event.server, player) } catch (err) {
        console.error('[valley] check ' + c.key + ' failed (left armed): ' + err)
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
