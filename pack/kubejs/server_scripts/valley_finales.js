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
    const full = resolve(c, origin)
    try {
      const r = server.runCommandSilent(full)
      if (r === 0) console.warn('[valley] command returned 0 (no effect / failed): ' + full)
    } catch (err) { console.error('[valley] finale command failed: ' + full + ' :: ' + err) }
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
    // §7 rule 2. The shipped long_table is 9x2x3 with the table row on its
    // own local z=1, so this origin puts the table at ~-2..~-11 and the two
    // bench rows at ~-11 and ~-9 — clear of the Town Square waystone at
    // ~0 ~1 ~0 and of the Act V signpost at ~0 ~1 ~-3, both of which the
    // doc's ~-3 ~1 ~0 would have punched a hole through.
    'place template valley:long_table ~-4 ~1 ~-11',
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
    // Halden lives at the hedge garden all through Act I (docs/NPCS.md).
    // He was never imported by any finale, yet Act II /tp's him by tag.
    npc('halden', '~-14', '~1', '~8'),
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
    // the shipped pier is 3 wide, so ~-1 centres it on the waystone axis
    'place template valley:pier ~-1 ~0 ~0',
    'fill ~-6 ~-1 ~6 ~6 ~-1 ~16 minecraft:sand',
    'fill ~-2 ~2 ~2 ~-2 ~2 ~18 supplementaries:candle_holder',
    'fill ~2 ~2 ~2 ~2 ~2 ~18 supplementaries:candle_holder',
    'setblock ~0 ~1 ~-2 waystones:waystone{WaystoneName:"The Pier"}',
    'bossbar set valley:lamps value 12',
    // Nella and Wisp arrive in Act II and had no import anywhere in the
    // pack. Import BEFORE the /tp block below, or the tp selects nothing.
    npc('nella', '~0', '~1', '~8'),
    npc('wisp', '~-8', '~1', '~12'),
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
    'place template valley:granary_shell ~-14 ~1 ~-4',
    // Tobin walks in off the north ridge in Act II (docs/NPCS.md).
    npc('tobin', '~12', '~1', '~-14')
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
    // Wisp brings three more Ribbits; this is their first appearance, so
    // they are imported, and everyone else is /tp'd (§7 rule 4).
    npc('ribbit_reed', '~2', '~1', '~-12'),
    npc('ribbit_sedge', '~4', '~1', '~-12'),
    npc('ribbit_mudlark', '~6', '~1', '~-12'),
    // Seated positions along valley:long_table. The template's bench rows
    // land at ~-11 and ~-9, so the seats are the row outside each bench.
    'tp @e[tag=npc_marnie,limit=1] ~-4 ~1 ~-8',
    'tp @e[tag=npc_bram,limit=1] ~-2 ~1 ~-8',
    'tp @e[tag=npc_pip,limit=1] ~0 ~1 ~-8',
    'tp @e[tag=npc_halden,limit=1] ~2 ~1 ~-8',
    'tp @e[tag=npc_tobin,limit=1] ~4 ~1 ~-8',
    'tp @e[tag=npc_oda,limit=1] ~-4 ~1 ~-12',
    'tp @e[tag=npc_nella,limit=1] ~-2 ~1 ~-12',
    'tp @e[tag=npc_wisp,limit=1] ~0 ~1 ~-12',
    'summon duckling:duck ~0 ~1 ~-9 {PersistenceRequired:1b,NoAI:1b}',
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
    // Puddle is the fourth Ribbit and arrives here (docs/NPCS.md).
    npc('ribbit_puddle', '~-4', '~1', '~6'),
    'tp @e[tag=npc_pip,limit=1] ~0 ~1 ~4',
    'tp @e[tag=npc_marnie,limit=1] ~-3 ~1 ~4',
    'tp @e[tag=npc_oda,limit=1] ~3 ~1 ~4',
    'tp @e[tag=npc_tobin,limit=1] ~-3 ~1 ~2',
    'tp @e[tag=npc_nella,limit=1] ~-3 ~1 ~6',
    'tp @e[tag=npc_halden,limit=1] ~3 ~1 ~6',
    'tp @e[tag=npc_wisp,limit=1] ~0 ~1 ~6',
    'tp @e[tag=npc_ribbit_reed,limit=1] ~2 ~1 ~6',
    'tp @e[tag=npc_ribbit_sedge,limit=1] ~4 ~1 ~6',
    'tp @e[tag=npc_ribbit_mudlark,limit=1] ~-2 ~1 ~6',
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
    // Clear-fill air -> fill pad -> place template (§7 rule 2). Act V is the
    // one finale the doc wrote without its pads; without them the town hall
    // and the bridge land in whatever the terrain happens to be.
    'fill ~-22 ~1 ~-18 ~-10 ~9 ~-6 minecraft:air',
    'fill ~-22 ~0 ~-18 ~-10 ~0 ~-6 minecraft:stone_bricks',
    'fill ~13 ~1 ~-17 ~19 ~7 ~-5 minecraft:air',
    'fill ~13 ~0 ~-17 ~19 ~0 ~-5 minecraft:stone_bricks',
    // ~-20 ~1 ~-6 put the 11x7x11 hall straight through the granary shell
    // (~-14 ~1 ~-4, 9x6x9) and ~10 ~0 ~-14 put the bridge through the
    // north-east market stall (~8 ~1 ~-10, 5x4x3). Both moved clear.
    'place template valley:town_hall ~-21 ~1 ~-17',
    'place template valley:stone_bridge ~14 ~0 ~-16',
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
    // The fifteen who already live here, on their Founder's Day marks.
    'tp @e[tag=npc_halden,limit=1] ~0 ~1 ~-2',
    'tp @e[tag=npc_pip,limit=1] ~0 ~1 ~2',
    'tp @e[tag=npc_marnie,limit=1] ~-4 ~1 ~2',
    'tp @e[tag=npc_bram,limit=1] ~-2 ~1 ~2',
    'tp @e[tag=npc_wisp,limit=1] ~4 ~1 ~-2',
    'tp @e[tag=npc_oda,limit=1] ~-4 ~1 ~-2',
    'tp @e[tag=npc_nella,limit=1] ~-2 ~1 ~-2',
    'tp @e[tag=npc_tobin,limit=1] ~2 ~1 ~-2',
    'tp @e[tag=npc_ribbit_reed,limit=1] ~6 ~1 ~0',
    'tp @e[tag=npc_ribbit_sedge,limit=1] ~6 ~1 ~2',
    'tp @e[tag=npc_ribbit_mudlark,limit=1] ~6 ~1 ~-2',
    'tp @e[tag=npc_ribbit_puddle,limit=1] ~8 ~1 ~0',
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
    s.runCommandSilent('worldborder set 59999968')
    s.runCommandSilent('execute in minecraft:the_nether run worldborder set 59999968')
    s.runCommandSilent('tellraw @a ' + JSON.stringify({
      text: "The valley's fine now. Go see what's past the ridge — and come home for supper.",
      color: 'gold', italic: true
    }))
    v.addWorldStage('endless_seasons')
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
//   * scenes are NOT latched — a scene is a set change, and re-running one
//     just re-places the same blocks. Only finales are once-per-world (§P7).
// =============================================================================
const SCENES = {

  // Q58 — the four firewood stacks. Wisp lights a lantern path down the
  // frozen river, which is the first thing that happens after the Hearth
  // goes out and the only light between the town and the reed village.
  q58: {
    origin: 'anchor',
    who: ['Wisp', 'Warm inn. Warm soup. I light the way, you walk it. That is a fair trade.'],
    cmds: [
      'setblock ~2 ~1 ~14 candlelight:lamp',
      'setblock ~-2 ~1 ~20 candlelight:lamp',
      'setblock ~2 ~1 ~26 candlelight:lamp',
      'setblock ~-2 ~1 ~32 candlelight:lamp',
      'setblock ~2 ~2 ~14 minecraft:lantern[hanging=false]',
      'setblock ~-2 ~2 ~20 minecraft:lantern[hanging=false]',
      'setblock ~2 ~2 ~26 minecraft:lantern[hanging=false]',
      'setblock ~-2 ~2 ~32 minecraft:lantern[hanging=false]',
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
    cmds: [
      'easy_npc preset import data valley:easy_npc/preset/ribbit_reed.npc.snbt ~-10 ~1 ~4',
      'easy_npc preset import data valley:easy_npc/preset/ribbit_sedge.npc.snbt ~-10 ~1 ~6',
      'easy_npc preset import data valley:easy_npc/preset/ribbit_mudlark.npc.snbt ~-12 ~1 ~4',
      'easy_npc preset import data valley:easy_npc/preset/ribbit_puddle.npc.snbt ~-12 ~1 ~6',
      'setblock ~-11 ~1 ~5 minecraft:campfire[lit=true]',
      'setblock ~-13 ~1 ~5 candlelight:lamp',
      'bossbar set valley:folk value 15',
      'playsound minecraft:entity.frog.long_jump master @a ~0 ~1 ~0 1 1'
    ]
  },

  // Q60 — soup for a full room. The Hearth relights, and the greenhouse SHELL
  // goes up on the square: six empty window frames, a doorway and a bare
  // bench. Q64 is what glazes it.
  q60: {
    origin: 'greenhouse',
    who: ['Marnie', "I have fed this room for thirty years, and tonight I'm sitting down at it. Don't make a thing of it."],
    cmds: [
      'fill ~-4 ~0 ~-3 ~4 ~6 ~3 minecraft:air',
      'fill ~-4 ~-1 ~-3 ~4 ~-1 ~3 minecraft:stone_bricks',
      'fill ~-4 ~0 ~-3 ~4 ~3 ~-3 minecraft:oak_planks',
      'fill ~-4 ~0 ~3 ~4 ~3 ~3 minecraft:oak_planks',
      'fill ~-4 ~0 ~-3 ~-4 ~3 ~3 minecraft:oak_planks',
      'fill ~4 ~0 ~-3 ~4 ~3 ~3 minecraft:oak_planks',
      // the six frames Q64 puts a window in
      'fill ~-3 ~1 ~-3 ~-2 ~2 ~-3 minecraft:air',
      'fill ~0 ~1 ~-3 ~1 ~2 ~-3 minecraft:air',
      'fill ~2 ~1 ~-3 ~3 ~2 ~-3 minecraft:air',
      'fill ~-3 ~1 ~3 ~-2 ~2 ~3 minecraft:air',
      'fill ~1 ~1 ~3 ~2 ~2 ~3 minecraft:air',
      'fill ~3 ~1 ~3 ~3 ~2 ~3 minecraft:air',
      // the doorway
      'fill ~-1 ~0 ~3 ~-1 ~1 ~3 minecraft:air',
      // an open rafter roof, glazed later
      'fill ~-4 ~4 ~-3 ~4 ~4 ~3 minecraft:oak_fence',
      // the marked bench for Q64's eight planters
      'fill ~-3 ~0 ~0 ~3 ~0 ~0 minecraft:oak_slab[type=top]',
      'setblock ~-4 ~1 ~0 candlelight:lamp',
      'setblock ~4 ~1 ~0 candlelight:lamp'
    ],
    also: {
      origin: 'inn',
      cmds: [
        // the Hearth relights — the whole point of the quest
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
    cmds: [
      'setblock ~-16 ~1 ~10 minecraft:brewing_stand',
      'setblock ~-17 ~1 ~10 handcrafted:oak_cupboard',
      'setblock ~-15 ~1 ~10 minecraft:water_cauldron[level=3]',
      'setblock ~-16 ~2 ~10 minecraft:lantern[hanging=false]',
      'effect give @a minecraft:regeneration 20 0 true',
      'particle minecraft:happy_villager ~0 ~2 ~0 6 2 6 0.01 120 force @a',
      'playsound minecraft:block.brewing_stand.brew master @a ~0 ~1 ~0 2 1'
    ]
  },

  // Q64 — the cold frame. Six windows, a door, eight planters on the bench.
  q64: {
    origin: 'greenhouse',
    who: ['Nella', "Nothing grows in it yet. I'll sit in it anyway - it's the only quiet room in town."],
    cmds: [
      'fill ~-3 ~1 ~-3 ~-2 ~2 ~-3 mcwwindows:oak_window',
      'fill ~0 ~1 ~-3 ~1 ~2 ~-3 mcwwindows:oak_window',
      'fill ~2 ~1 ~-3 ~3 ~2 ~-3 mcwwindows:oak_window',
      'fill ~-3 ~1 ~3 ~-2 ~2 ~3 mcwwindows:oak_window',
      'fill ~1 ~1 ~3 ~2 ~2 ~3 mcwwindows:oak_window',
      'fill ~3 ~1 ~3 ~3 ~2 ~3 mcwwindows:oak_window',
      'setblock ~-1 ~0 ~3 mcwdoors:oak_cottage_door[half=lower,facing=north,hinge=left,open=false]',
      'setblock ~-1 ~1 ~3 mcwdoors:oak_cottage_door[half=upper,facing=north,hinge=left,open=false]',
      // the eight planters on the marked bench
      'fill ~-3 ~1 ~0 ~3 ~1 ~0 minecraft:flower_pot',
      'setblock ~0 ~1 ~1 farmersdelight:organic_compost',
      'setblock ~-2 ~1 ~1 handcrafted:oak_table',
      'fill ~-4 ~4 ~-3 ~4 ~4 ~3 minecraft:glass',
      'playsound minecraft:block.glass.place master @a ~0 ~1 ~0 2 1'
    ]
  },

  // Q65 — open the Works. The interior lights, and there is a saddled horse
  // in the stable (the quest's reward line, made literally true).
  q65: {
    origin: 'works',
    who: ['Tobin', 'Ninety blocks of fallen adit, I counted twice, and behind it is the entire works, and I have not slept.'],
    cmds: [
      'fill ~-5 ~0 ~-5 ~5 ~4 ~5 minecraft:air replace minecraft:cobblestone',
      'setblock ~-4 ~3 ~-4 minecraft:lantern[hanging=true]',
      'setblock ~4 ~3 ~-4 minecraft:lantern[hanging=true]',
      'setblock ~-4 ~3 ~4 minecraft:lantern[hanging=true]',
      'setblock ~4 ~3 ~4 minecraft:lantern[hanging=true]',
      'setblock ~0 ~3 ~0 minecraft:lantern[hanging=true]',
      'setblock ~-3 ~0 ~-3 minecraft:smithing_table',
      'setblock ~3 ~0 ~-3 minecraft:barrel[facing=up]',
      'setblock ~0 ~0 ~-5 minecraft:polished_andesite',
      'fill ~5 ~0 ~5 ~7 ~0 ~7 minecraft:hay_block',
      'summon minecraft:horse ~6 ~1 ~6 {Tame:1b,PersistenceRequired:1b,SaddleItem:{id:"minecraft:saddle",Count:1b}}',
      'playsound minecraft:block.beacon.power_select master @a ~0 ~1 ~0 2 0.8'
    ]
  },

  // Q66 — the grid. Duct from the mill to the Works, two cells at this end.
  q66: {
    origin: 'works',
    who: ['Bram', "Mill makes it, Works needs it, duct in between. That's the whole job."],
    cmds: [
      'setblock ~-2 ~0 ~-4 thermal:energy_cell',
      'setblock ~2 ~0 ~-4 thermal:energy_cell',
      'fill ~-1 ~0 ~-4 ~1 ~0 ~-4 thermal:energy_duct',
      'setblock ~0 ~1 ~-4 minecraft:redstone_lamp[lit=true]',
      'particle minecraft:electric_spark ~0 ~1 ~-4 0.6 0.6 0.6 0.02 60 force @a',
      'playsound minecraft:block.beacon.activate master @a ~0 ~1 ~0 1 1.4'
    ]
  },

  // Q70a — the wool line. Four blankets, four beds, four empty houses that
  // will not be empty in spring.
  q70a: {
    origin: 'inn',
    who: ['Marnie', 'Four empty houses, four beds, four blankets. People arrive in spring, and beds should be made before they get here.'],
    cmds: [
      'setblock ~4 ~0 ~2 minecraft:white_bed[facing=south,part=foot]',
      'setblock ~4 ~0 ~3 minecraft:white_bed[facing=south,part=head]',
      'setblock ~6 ~0 ~2 minecraft:white_bed[facing=south,part=foot]',
      'setblock ~6 ~0 ~3 minecraft:white_bed[facing=south,part=head]',
      'setblock ~8 ~0 ~2 minecraft:white_bed[facing=south,part=foot]',
      'setblock ~8 ~0 ~3 minecraft:white_bed[facing=south,part=head]',
      'setblock ~10 ~0 ~2 minecraft:white_bed[facing=south,part=foot]',
      'setblock ~10 ~0 ~3 minecraft:white_bed[facing=south,part=head]',
      'setblock ~5 ~0 ~2 minecraft:white_carpet',
      'setblock ~7 ~0 ~2 minecraft:light_gray_carpet',
      'setblock ~9 ~0 ~2 minecraft:brown_carpet',
      'setblock ~11 ~0 ~2 minecraft:orange_carpet',
      'playsound minecraft:block.wool.place master @a ~0 ~1 ~0 2 1'
    ]
  },

  // Q71 — the turbine holds 1,800 RPM. The lever goes live: it is placed
  // UNPOWERED here, because pulling it is the Act IV finale.
  q71: {
    origin: 'works',
    who: ['Bram', "Crate's got what it's got - blades, coils, casing. Eighteen hundred RPM under load, and hold it there."],
    cmds: [
      'setblock ~0 ~1 ~0 minecraft:polished_andesite',
      'setblock ~0 ~2 ~0 minecraft:lever[face=wall,facing=south,powered=false]',
      'setblock ~-1 ~2 ~0 minecraft:copper_block',
      'setblock ~1 ~2 ~0 minecraft:copper_block',
      'setblock ~0 ~3 ~0 minecraft:oak_wall_sign[facing=south]{front_text:{messages:[\'{"text":"1800 RPM"}\',\'{"text":"under load"}\',\'{"text":"- J.K."}\',\'{"text":""}\']}}',
      'playsound minecraft:block.note_block.bit master @a ~0 ~1 ~0 2 1.6'
    ]
  },

  // Q72 — the coolant loop. Josie's rule: the waste heat goes to the town.
  // Six heaters under the greenhouse, and the bathhouse starts steaming.
  q72: {
    origin: 'greenhouse',
    who: ['Josie', 'The waste heat goes to the town, not the sky. Anything else is a fire you paid for twice.'],
    cmds: [
      'fill ~-3 ~-1 ~-2 ~3 ~-1 ~-2 thermal:fluid_duct',
      'setblock ~-3 ~0 ~-2 minecraft:magma_block',
      'setblock ~-1 ~0 ~-2 minecraft:magma_block',
      'setblock ~1 ~0 ~-2 minecraft:magma_block',
      'setblock ~3 ~0 ~-2 minecraft:magma_block',
      'setblock ~-2 ~0 ~2 minecraft:magma_block',
      'setblock ~2 ~0 ~2 minecraft:magma_block',
      'particle minecraft:cloud ~0 ~2 ~0 3 1 2 0.01 120 force @a',
      'playsound minecraft:block.lava.ambient master @a ~0 ~1 ~0 1 1.4'
    ],
    also: {
      origin: 'bathhouse',
      cmds: [
        'fill ~-2 ~0 ~-2 ~2 ~0 ~2 minecraft:water[level=0]',
        'setblock ~0 ~-1 ~0 minecraft:magma_block',
        'setblock ~-3 ~1 ~-3 candlelight:lamp',
        'setblock ~3 ~1 ~3 candlelight:lamp',
        'particle minecraft:cloud ~0 ~2 ~0 2 1 2 0.02 200 force @a',
        'playsound minecraft:block.bubble_column.upwards_ambient master @a ~0 ~1 ~0 2 0.8'
      ]
    }
  },

  // Q73 — bring Bram. He says no. You bring him anyway.
  q73: {
    origin: 'inn',
    who: ['Bram', "The mill needs me at midnight in January, is the thing. ... Fine. One cocoa."],
    cmds: [
      'tp @e[tag=npc_bram,limit=1] ~2 ~1 ~1',
      'setblock ~2 ~1 ~2 handcrafted:oak_chair',
      'setblock ~1 ~1 ~1 handcrafted:oak_table',
      'particle minecraft:campfire_cosy_smoke ~2 ~2 ~1 0.2 0.4 0.2 0.01 30 force @a',
      'playsound minecraft:entity.villager.yes master @a ~0 ~1 ~0 1 0.8'
    ]
  },

  // Q74 — the second stretch. Runs the duct along every post already stored
  // in persistentData.lamps[], which is why this one is a `run` and not a
  // command list: the coordinates only exist at runtime.
  q74: {
    origin: 'anchor',
    who: ['Josie', 'Forty posts, mill to square to lake. I counted them on my fingers before I could count to forty.'],
    run: function (server, v) {
      const lamps = v.lamps()
      lamps.forEach(p => {
        server.runCommandSilent('particle minecraft:end_rod ' +
          p[0] + ' ' + (p[1] + 2) + ' ' + p[2] + ' 0.2 0.4 0.2 0.01 6 force @a')
      })
      server.runCommandSilent('bossbar set valley:lamps value ' + Math.min(Math.max(lamps.length, 39), 40))
      const home = v.home()
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

function runScene(source, key) {
  const v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }

  const scene = SCENES[key]
  if (!scene) {
    msg(source, Text.gray('[valley] no scene "' + key + '". Known scenes: ' +
      Object.keys(SCENES).join(' ')))
    return 0
  }
  if (!v.anchor()) {
    msg(source, Text.red(
      'No Town Anchor is set, so a scene has nothing to measure from. Place the Surveyor\'s Stake first (Q7).'))
    return 0
  }

  const server = source.server
  try {
    if (scene.cmds) {
      const origin = scene.origin === 'anchor' ? v.anchor() : v.mark(scene.origin)
      if (origin) runSeg(server, origin, scene.cmds)
      else console.warn('[valley] scene ' + key + ': no mark "' + scene.origin + '"')
    }
    if (scene.also) {
      const o2 = scene.also.origin === 'anchor' ? v.anchor() : v.mark(scene.also.origin)
      if (o2) runSeg(server, o2, scene.also.cmds)
    }
    if (scene.run) scene.run(server, v)
    if (scene.who) v.sayAll(scene.who[0], scene.who[1])
  } catch (err) {
    // A scene is set dressing. It must never take a reward down with it.
    console.error('[valley] scene ' + key + ' failed: ' + err)
    msg(source, Text.gray('[valley] scene ' + key + ' hit a snag; see the log.'))
    return 0
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
  const p = srcPlayer(source)
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

      // --- /valley standing <key> [team] (§5 Standing: Trusted) -----------
      // Called by a silent, elevated command reward on each of the eight
      // chain-closing quests:
      //     /valley standing q59 {long_team_id}
      // CommandReward#claim substitutes {long_team_id} with the CLAIMING
      // player's FTB team UUID, so the ledger this writes is per team. The
      // team argument is optional: run by hand, it resolves from the caller.
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
      .then(Commands.literal('anchor').then(Commands.literal('set').requires(src => src.hasPermission(2))
        .then(Commands.argument('x', Arguments.INTEGER.create(event)).then(Commands.argument('y', Arguments.INTEGER.create(event)).then(Commands.argument('z', Arguments.INTEGER.create(event)).executes(ctx => {
          const x = Arguments.INTEGER.getResult(ctx, 'x'), y = Arguments.INTEGER.getResult(ctx, 'y'), z = Arguments.INTEGER.getResult(ctx, 'z')
          global.valley.setAnchor(x, y, z)
          msg(ctx.source, Text.gold('Town Anchor set to ' + x + ' ' + y + ' ' + z))
          return 1
        }))))))
      .then(Commands.literal('home').then(Commands.literal('set').requires(src => src.hasPermission(2))
        .then(Commands.argument('x', Arguments.INTEGER.create(event)).then(Commands.argument('y', Arguments.INTEGER.create(event)).then(Commands.argument('z', Arguments.INTEGER.create(event)).executes(ctx => {
          const x = Arguments.INTEGER.getResult(ctx, 'x'), y = Arguments.INTEGER.getResult(ctx, 'y'), z = Arguments.INTEGER.getResult(ctx, 'z')
          global.valley.setHome(x, y, z)
          msg(ctx.source, Text.gold('Home set to ' + x + ' ' + y + ' ' + z))
          return 1
        }))))))
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
  const player = srcPlayer(source)
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
// /valley check standing — reports Q86's second condition. Read-only.
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

function checkStanding(source) {
  const v = global.valley
  if (!v) { msg(source, Text.red('[valley] core script not loaded.')); return 0 }
  const player = srcPlayer(source)
  if (!player) { msg(source, Text.red('Run this as a player.')); return 0 }

  const team = v.teamId(player)
  const api = v.standingApiClosed(player)
  if (api) api.forEach(k => v.recordStanding(team, k))

  const closed = v.standingClosed(team)
  const done = {}
  closed.forEach(k => { done[k] = true })

  msg(source, Text.gold('Standing: ' + closed.length + ' of 8 chains closed. Six are needed.'))
  const line = v.standingChains().map(k =>
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
  const v = global.valley
  if (!v) return 0
  const key = event.arguments.WORD.getResult(ctx, 'key')
  const player = srcPlayer(ctx.source)
  const team = teamArgName ? event.arguments.WORD.getResult(ctx, teamArgName) : v.teamId(player)

  if (v.standingChains().indexOf(key) === -1) {
    msg(ctx.source, Text.red('Not a chain-closing quest: ' + key +
      '. Expected one of ' + v.standingChains().join(' ') + '.'))
    return 0
  }

  const fresh = v.recordStanding(team, key)
  const closed = v.standingClosed(team)
  if (fresh && player) {
    v.say(player, 'Oda', (STANDING_WHO[key] || 'That') + "'s story is closed. That's " +
      closed.length + ' of eight in my book.')
  }
  console.info('[valley] /valley standing ' + key + ' ' + team +
               ' -> ' + closed.length + '/8' + (fresh ? '' : ' (already recorded)'))
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
  const player = srcPlayer(ctx.source)
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
