// =============================================================================
// valley_finales.js — Copper Kettle Valley: the /valley command tree and the
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
//     mod list. The lamp post is `candlelight:lamp` (see valley_core.js
//     VALLEY.LAMP_BLOCK); the Act IV "everything lights at once" moment sets
//     a lantern on top of every stored post.
//  6. `~` offsets are resolved to ABSOLUTE coordinates here, because 1.20.1
//     has no macro functions and we are not shipping mcfunctions (§12.1 C6).
// ---------------------------------------------------------------------------
// =============================================================================

const FIN_ACTS = ['act1', 'act2', 'act3', 'act4', 'act5']

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
  const v = base + (d === '' || d === '-' ? 0 : parseFloat(d))
  return (v === Math.floor(v)) ? String(Math.floor(v)) : String(v)
}

function resolve(cmd, origin) {
  return cmd.replace(TILDE3, (m, lead, dx, dy, dz) =>
    lead + num(origin[0], dx) + ' ' + num(origin[1], dy) + ' ' + num(origin[2], dz))
}

function runSeg(server, origin, cmds) {
  cmds.forEach(c => {
    if (!c || c.charAt(0) === '#') return
    try { server.runCommandSilent(resolve(c, origin)) }
    catch (err) { console.error('[valley] finale command failed: ' + c + ' :: ' + err) }
  })
}

// =============================================================================
// The five chains. Each is a list of segments; a segment names its origin mark
// (a key in VALLEY.OFF, or 'anchor') and its commands, with `~` offsets from
// that origin. Written out rather than read from outline.json so the six
// corrections above are visible in the file that runs them.
// =============================================================================
function finaleAct1(server, v) {
  runSeg(server, v.anchor(), [
    'season set early_spring',
    'time set day',
    'weather clear',
    // levelled pad, then templates (§7 rule 2) — never /place structure
    'fill ~-18 ~1 ~-18 ~18 ~14 ~18 minecraft:air',
    'fill ~-18 ~-3 ~-18 ~18 ~-2 ~18 minecraft:dirt',
    'fill ~-18 ~-1 ~-18 ~18 ~-1 ~18 minecraft:stone',
    'fill ~-18 ~0 ~-18 ~18 ~0 ~18 minecraft:cobblestone',
    'fill ~-7 ~0 ~-7 ~7 ~0 ~7 minecraft:stone_bricks',
    'place template valley:market_stall ~-10 ~1 ~-10',
    'place template valley:market_stall ~8 ~1 ~-10',
    'place template valley:market_stall ~-10 ~1 ~8',
    'place template valley:market_stall ~8 ~1 ~8',
    'place template valley:long_table ~-3 ~1 ~0',
    // the mill race is cut here so Q16's water wheels have water on any terrain
    'place template valley:mill_race ~-26 ~0 ~4',
    'setblock ~0 ~1 ~0 waystones:waystone{WaystoneName:"Town Square"}',
    'setblock ~-12 ~1 ~0 candlelight:lamp',
    'setblock ~12 ~1 ~0 candlelight:lamp',
    'setblock ~0 ~1 ~-12 candlelight:lamp',
    'setblock ~0 ~1 ~12 candlelight:lamp',
    'bossbar set valley:lamps value 6',
    'bossbar set valley:folk value 5',
    npc('marnie', '~-4', '~1', '~-2'),
    npc('bram', '~4', '~1', '~-2'),
    npc('oda', '~-4', '~1', '~2'),
    npc('pip', '~4', '~1', '~2'),
    'summon duckling:duck ~4 ~1 ~3 {PersistenceRequired:1b,NoAI:1b}',
    'title @a times 15 70 25',
    'title @a subtitle {"text":"Spring, Year One.","color":"gray"}',
    'title @a title {"text":"The Thaw Fair","color":"gold"}',
    'playsound minecraft:block.bell.use master @a ~0 ~1 ~0 1 1',
    'loot give @a loot valley:rewards/fair_basket',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_2',
    'worldborder set 3000 10'
  ])
  v.sayAll('Tobin', "Walked the north ridge. It's fine to the cairn. Also I found a rock, but that's a separate conversation.")
  v.addWorldStage('act2')
}

function finaleAct2(server, v) {
  // Positioned at the Lake Waystone, not the anchor.
  runSeg(server, v.mark('lake'), [
    'season set mid_summer',
    'time set 18000',
    'weather clear',
    'fill ~-14 ~1 ~-14 ~14 ~10 ~14 minecraft:air',
    'fill ~-14 ~-1 ~-14 ~14 ~-1 ~14 minecraft:stone',
    'place template valley:pier ~-3 ~0 ~0',
    'fill ~-6 ~-1 ~6 ~6 ~-1 ~16 minecraft:sand',
    'fill ~-2 ~2 ~2 ~-2 ~2 ~18 supplementaries:candle_holder',
    'fill ~2 ~2 ~2 ~2 ~2 ~18 supplementaries:candle_holder',
    'setblock ~0 ~1 ~-2 waystones:waystone{WaystoneName:"The Pier"}',
    'bossbar set valley:lamps value 12',
    // residents are teleported, never pathed (§7 rule 4)
    'tp @e[tag=npc_marnie,limit=1] ~-2 ~1 ~4',
    'tp @e[tag=npc_bram,limit=1] ~2 ~1 ~4',
    'tp @e[tag=npc_oda,limit=1] ~-2 ~1 ~6',
    'tp @e[tag=npc_nella,limit=1] ~0 ~1 ~10',
    'tp @e[tag=npc_halden,limit=1] ~2 ~1 ~6',
    'tp @e[tag=npc_pip,limit=1] ~0 ~1 ~4',
    'title @a times 15 70 25',
    'title @a title {"text":"The Lantern Float","color":"aqua"}',
    'summon firework_rocket ~0 ~4 ~12 {LifeTime:18,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:1b,Colors:[I;16766720],FadeColors:[I;16777215]}]}}}}',
    'summon firework_rocket ~4 ~4 ~14 {LifeTime:22,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Explosions:[{Type:4b,Colors:[I;3847130]}]}}}}',
    'playsound minecraft:entity.firework_rocket.launch master @a ~0 ~2 ~0 2 1',
    'give @a supplementaries:candle_holder 1',
    'give @a perfectplushies:frog_plushie 1',
    // the visible "the next tier is already in your hands" moment
    'give @a thermal:energy_cell 1',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_3',
    'worldborder set 6000 10'
  ])
  // The empty granary shell goes up at the anchor, so Q39 is twelve drawers
  // into twelve marked alcoves and not a build.
  runSeg(server, v.anchor(), [
    'place template valley:granary_shell ~-14 ~1 ~-4'
  ])
  v.sayAll('Nella', 'You all came. Right.')
  v.addWorldStage('act3')
}

function finaleAct3(server, v) {
  runSeg(server, v.anchor(), [
    'season set mid_autumn',
    'time set 13000',
    'weather clear',
    'setblock ~-6 ~1 ~-6 minecraft:hay_block',
    'setblock ~6 ~1 ~-6 minecraft:hay_block',
    'setblock ~-6 ~1 ~6 minecraft:carved_pumpkin[facing=south]',
    'setblock ~6 ~1 ~6 minecraft:carved_pumpkin[facing=south]',
    'place template valley:granary_facade ~-14 ~1 ~-4',
    'place template valley:noticeboard ~0 ~1 ~-5',
    'bossbar set valley:lamps value 22',
    'bossbar set valley:folk value 11',
    'title @a times 20 90 30',
    'title @a title {"text":"The Harvest Supper","color":"gold"}',
    'loot give @a loot valley:rewards/harvest_gifts',
    'give @a valley:scrip 25',
    'advancement grant @a only valley:journal/entry_4'
  ])

  // The turn, six seconds later (§7: /schedule function valley:act3/turn 6s).
  v.delay(120, s => {
    runSeg(s, v.anchor(), [
      'season set early_winter',
      'weather rain',                                  // §12.1 C10: /weather snow does not exist
      'playsound minecraft:block.snow.place master @a ~0 ~1 ~0 1 0.6',
      'worldborder set 10000 10',
      'execute in minecraft:the_nether run worldborder set 1250 10'   // §12.1 C9: per dimension
    ])
    v.sayAll('Oda', "That's the last warm night. Let's not lose anybody this year.")
    v.addWorldStage('act4')
  })
}

function finaleAct4(server, v) {
  runSeg(server, v.mark('works'), [
    'season set mid_winter',
    'time set 18000',
    'weather rain',
    'title @a times 20 100 30',
    'title @a title {"text":"The Longest Night","color":"white"}',
    'tp @e[tag=npc_bram,limit=1] ~0 ~1 ~2',
    'playsound minecraft:block.bell.use master @a ~0 ~1 ~0 1 1.4'
  ])
  v.sayAll('Pip', 'I get to ring it. Marnie said. RING IT.')

  // Four seconds later, the instant. Bram pulls the lever: NPCs cannot
  // interact with blocks, so the lever is setblock and Bram is narration.
  v.delay(80, s => {
    const works = v.mark('works')
    runSeg(s, works, [
      'setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=true]',
      'particle minecraft:cloud ~2 ~3 ~2 1 1 1 0.02 60 force @a',
      'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 3 0.7',
      'playsound minecraft:block.conduit.activate master @a ~0 ~1 ~0 2 1'
    ])

    // The world changes in one instant: every stored lamp post lights at once.
    const lamps = v.lamps()
    lamps.forEach(p => {
      s.runCommandSilent('setblock ' + p[0] + ' ' + (p[1] + 1) + ' ' + p[2] + ' minecraft:lantern')
      s.runCommandSilent('particle minecraft:end_rod ' + p[0] + ' ' + (p[1] + 2) + ' ' + p[2] + ' 0.2 0.2 0.2 0.01 8 force @a')
    })
    s.runCommandSilent('bossbar set valley:lamps value ' + Math.max(lamps.length, 39))

    // The Hearth relights, and the bathhouse starts steaming.
    const inn = v.mark('inn')
    if (inn) s.runCommandSilent('setblock ' + inn[0] + ' ' + inn[1] + ' ' + inn[2] + ' minecraft:campfire[lit=true]')
    const bath = v.mark('bathhouse')
    if (bath) s.runCommandSilent('particle minecraft:cloud ' + bath[0] + ' ' + (bath[1] + 2) + ' ' + bath[2] + ' 2 1 2 0.02 120 force @a')

    s.runCommandSilent('give @a valley:hearthkeepers_lantern 1')
    s.runCommandSilent('give @a valley:plushie_token 1')
    s.runCommandSilent('give @a valley:scrip 25')
    s.runCommandSilent('advancement grant @a only valley:journal/entry_5')
    v.sayAll('Bram', 'Well.')
    v.addWorldStage('greenhouse_warm')
    v.addWorldStage('act5')
  })
}

function finaleAct5(server, v) {
  runSeg(server, v.anchor(), [
    'season set early_spring',
    'time set noon',
    'weather clear',
    'place template valley:town_hall ~-20 ~1 ~-6',
    'place template valley:stone_bridge ~10 ~0 ~-14',
    'place template valley:mill_roof ~-24 ~4 ~2',
    'setblock ~0 ~1 ~-3 minecraft:oak_sign{front_text:{messages:[\'{"text":"COPPER KETTLE"}\',\'{"text":"VALLEY"}\',\'{"text":"pop. 15"}\',\'{"text":"est. again"}\']}}',
    'bossbar set valley:lamps value 40',
    'bossbar set valley:folk value 15',
    // three new arrivals, 24 blocks out on a pre-filled path — a short
    // approach, because long-distance pathing does not work (§12.3)
    'fill ~-2 ~0 ~10 ~2 ~0 ~28 minecraft:dirt_path',
    npc('newcomer_tess', '~0', '~1', '~24'),
    npc('newcomer_mab', '~2', '~1', '~26'),
    npc('newcomer_corin', '~-2', '~1', '~26'),
    'title @a times 20 110 40',
    'title @a subtitle {"text":"Spring, Year Two.","color":"gray"}',
    'title @a title {"text":"Founder\'s Day","color":"gold","bold":true}',
    'give @a valley:kettle_deed 1',
    'give @a valley:copper_kettle_trophy 1',
    'loot give @a loot valley:rewards/founders',
    'summon firework_rocket ~0 ~5 ~0 {LifeTime:25,FireworksItem:{id:"minecraft:firework_rocket",Count:1b,tag:{Fireworks:{Flight:2b,Explosions:[{Type:1b,Colors:[I;16766720,3847130],FadeColors:[I;16777215]}]}}}}',
    'playsound minecraft:ui.toast.challenge_complete master @a ~0 ~1 ~0 2 1'
  ])

  // Halden reads the last page of Josie's journal: five lines, each five
  // seconds after the last. (§7: `function valley:act5/read1` .. read5.)
  const page = [
    'The Works ran. For eleven days, in the winter Old Dell left.',
    'The greenhouse was warm and the bakery had flour and I stood in the lane at ten at night in February, and every lamp on the road was lit.',
    'A machine that one person can run is not infrastructure. It is a hostage.',
    'So I shut it off, and I waited for two of you.',
    'If there is more than one set of footprints on my cellar stairs, then I was right to wait, and go and turn it on.'
  ]
  page.forEach((line, i) => {
    v.delay(100 + i * 100, s => v.sayAll('Halden', line))
  })

  v.delay(100 + page.length * 100, s => {
    s.runCommandSilent('worldborder set 60000000')
    s.runCommandSilent('execute in minecraft:the_nether run worldborder set 60000000')
    s.runCommandSilent('tellraw @a ' + JSON.stringify({
      text: "The valley's fine now. Go see what's past the ridge — and come home for supper.",
      color: 'gold', italic: true
    }))
    v.addWorldStage('endless_seasons')
  })
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
  let p = null
  try { p = source.player } catch (err) { p = null }
  if (p) p.tell(component)
  else console.info('[valley] ' + component.getString())
}

// -----------------------------------------------------------------------------
// The P7 guard. One entry point, one flag, one refusal message.
// -----------------------------------------------------------------------------
function runFinale(source, act) {
  const v = global.valley
  const server = source.server
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }

  if (!v.anchor()) {
    msg(source, Text.red(
      'No Town Anchor is set. Place the Surveyor\'s Stake first (Q7), then run this again.'))
    return 0
  }
  if (v.finaleDone(act)) {
    msg(source, Text.gray('[valley] ' + act + ' finale has already run in this world.'))
    return 1
  }
  v.markFinale(act)
  console.info('[valley] running finale ' + act)
  FINALES[act](server, v)
  return 1
}

// =============================================================================
// /valley — the command tree (§11 "the /valley command tree — every reward
// calls it").
// =============================================================================
ServerEvents.commandRegistry(event => {
  const Commands = event.commands
  const Arguments = event.arguments

  event.register(
    Commands.literal('valley')
      .requires(src => src.hasPermission(0))

      // --- /valley finale act1 .. act5 -----------------------------------
      .then(FIN_ACTS.reduce((node, act) =>
        node.then(Commands.literal(act).executes(ctx => runFinale(ctx.source, act))),
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
        .then(Commands.literal('standing').executes(ctx => checkStanding(ctx.source))))

      // --- /valley anchor -------------------------------------------------
      .then(Commands.literal('anchor').executes(ctx => {
        const v = global.valley
        const a = v ? v.anchor() : null
        const h = v ? v.home() : null
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
        const v = global.valley
        const n = v ? v.lamps().length : 0
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
function checkAt(source, key, ok, hint) {
  const v = global.valley
  const player = source.player
  if (!v || !player) { msg(source, Text.red('Run this as a player, standing at the Works.')); return 0 }
  const works = v.mark('works')
  if (!works) { msg(source, Text.red('No Town Anchor set, so the Works has no position yet.')); return 0 }
  const d = Math.max(Math.abs(player.x - works[0]), Math.abs(player.z - works[2]))
  if (d > 48) {
    msg(source, Text.gray('Stand at the Works and run this again.'))
    msg(source, Text.gray(hint))
    return 0
  }
  msg(source, Text.gold(ok))
  v.complete(player, key)
  v.once(key)
  return 1
}

// -----------------------------------------------------------------------------
// /valley check standing — Q86's second condition.
// §5: Standing is a count of completed resident chains. Reading FTB Quests'
// completion state needs its internal API, which is out of scope for a script,
// so this prints the eight chains and grants the world stage once the player
// says the count is met. The quest task itself stays an honour-system
// checkmark, exactly like every other fit-out quest in the pack (§11).
// -----------------------------------------------------------------------------
function checkStanding(source) {
  const v = global.valley
  if (!v) return 0
  msg(source, Text.gold('Standing: Trusted needs six of these eight closed —'))
  msg(source, Text.gray('Wisp Q59 · Marnie Q60 · Halden Q62 · Pip Q63 · Bram Q73 · Tobin Q75 · Nella Q77 · Oda Q85'))
  v.addWorldStage('standing_trusted')
  return 1
}

// -----------------------------------------------------------------------------
// /valley stage ...
// -----------------------------------------------------------------------------
function stageCmd(ctx, event, op, scope) {
  const v = global.valley
  const id = event.arguments.WORD.getResult(ctx, 'id')
  if (!v) return 0
  if (scope === 'world') {
    v.addWorldStage(id)
    msg(ctx.source, Text.gray('World stage ' + id + ' granted.'))
    return 1
  }
  const player = ctx.source.player
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
