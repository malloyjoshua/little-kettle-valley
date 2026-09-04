// =============================================================================
// valley_keepsakes.js — /valley keepsake <name>
//
// The story hands out a lot of one-of-a-kind things: Josie's letter, the deed,
// the Copper Kettle off the hearth, her journal, Marnie's compass, the two
// kettle plates, Tobin's survey, the turbine notes. Every one of them is a
// max-stack-1 item that can be dropped in lava, left in a chest in a chunk
// nobody goes back to, placed as a block that does not drop itself, or lost
// with the bag on a death nobody got back to in time.
//
// None of them can be crafted. Losing one used to be permanent, and the pack
// said nothing about it. This is the counter you walk back up to.
//
// Deliberately open to every player (hasPermission(0)): the person who loses
// the kettle is the person playing, not the op, and a single-player world has
// no op to ask. Nothing here can be lost by handing out a second copy — the
// quest checks all read "hold one", never "hold exactly one", and none of
// these items is a currency.
//
// Brigadier merges literal roots, so registering a SECOND Commands.literal
// ('valley') here adds `keepsake` to the tree valley_finales.js already owns
// without either file having to know about the other. Both roots declare the
// same .requires, which is what lets the merge keep the permission it has.
//
// Rhino: no `const` inside a function body in this pack (KubeJS 2001.6.5 runs
// Rhino in a mode where a const in a nested scope can be re-entered on a
// reload and throw). Top-level const only; `let` everywhere inside.
// =============================================================================

// -----------------------------------------------------------------------------
// The roster. [command name, item id or 'letter'/'journal' special, what it is]
// The name is what a player types. Keep them short and lower-case: they are
// Brigadier literals, so they tab-complete.
// -----------------------------------------------------------------------------
const KEEPSAKES = [
  ['letter',       'letter',                          "Josie's Letter (the four pages you start with)"],
  ['book',         'ftbquests:book',                  'The Quest Book'],
  ['journal',      'journal',                         "Josie's Journal (the Patchouli book)"],
  ['kettle',       'herbalbrews:copper_tea_kettle',   'The Copper Tea Kettle off the hearth'],
  ['deed',         'valley:deed',                     'The Kettle Farm Deed'],
  ['works_deed',   'valley:deed_works',               'The Works Deed'],
  ['kettle_deed',  'valley:kettle_deed',              'The Kettle Family Deed'],
  ['compass',      'explorerscompass:explorerscompass', "Marnie's Explorer's Compass"],
  ['hammer',       'justhammers:stone_hammer',        "Bram's stone hammer"],
  ['stake',        'valley:town_anchor',              "The Surveyor's Stake"],
  ['waystone',     'waystones:waystone',              'A Waystone (Home, or the cellar)'],
  ['plate_a',      'valley:kettle_plate_a',           'Kettle Plate A'],
  ['plate_b',      'valley:kettle_plate_b',           'Kettle Plate B'],
  ['survey',       'valley:deep_survey',              "Tobin's Deep Survey"],
  ['notes',        'valley:turbine_notes',            "Josie's Turbine Notes"],
  ['lantern',      'valley:josies_lantern',           "Josie's Lantern"],
  ['hearth_lantern', 'valley:hearthkeepers_lantern',  "The Hearthkeeper's Lantern"],
  ['trophy',       'valley:copper_kettle_trophy',     'The Copper Kettle (the trophy)'],
  ['ledger',       'valley:odas_ledger',              "Oda's Ledger"],
  ['catalogue',    'valley:catalogue',                "Oda's Catalogue"],
  ['broom',        'valley:oda_broom',                "Oda's Broom"],
  ['net',          'valley:dredge_net',               'The Dredge Net'],
  ['auger',        'valley:ice_auger',                'The Ice Auger']
]

// The Patchouli book is handed over by the same `give` the quest rewards use
// (story/quests/act1.json Q?? and five act3 quests), rather than by building
// the NBT here: that command is already proven on this pack, and a guide_book
// with the wrong book tag opens to Patchouli's landing page instead of hers.
const JOURNAL_GIVE = "give %s patchouli:guide_book{'patchouli:book':'patchouli:valley_journal'}"

// -----------------------------------------------------------------------------
// Hand one over. Returns a chat-safe string, or null if it could not be built —
// a keepsake is never allowed to throw out of a command a player just typed.
// -----------------------------------------------------------------------------
function giveKeepsake(source, entry) {
  let player = source.player
  if (!player) {
    source.sendFailure(Component.literal('Only a player can be handed a keepsake.'))
    return 0
  }
  let id = entry[1]
  let label = entry[2]

  try {
    if (id === 'letter') {
      // valley_core.js builds a fresh written_book per call; an ItemStack handed
      // to two people is one stack, so this must never be cached.
      if (global.valley && global.valley.letter) {
        player.give(global.valley.letter())
      } else {
        player.give(Item.of('valley:letter'))
      }
    } else if (id === 'journal') {
      let name = player.profile.name
      source.server.runCommandSilent(JOURNAL_GIVE.replace('%s', name))
    } else {
      player.give(Item.of(id))
    }
  } catch (err) {
    console.error('[valley] could not hand over keepsake ' + entry[0] + ': ' + err)
    source.sendFailure(Component.literal(
      'That keepsake could not be built. Tell an op: /give ' + id))
    return 0
  }

  source.sendSuccess(Component.literal(label + ' is in your bag.'), false)
  console.info('[valley] keepsake ' + entry[0] + ' handed to ' + player.profile.name)
  return 1
}

// -----------------------------------------------------------------------------
// `/valley keepsake` with nothing after it. Prints the list rather than
// failing: somebody who has lost something does not know the short name yet.
// -----------------------------------------------------------------------------
function listKeepsakes(source) {
  source.sendSuccess(Component.literal(
    'Lost something? /valley keepsake <name> hands back any story keepsake:'), false)
  KEEPSAKES.forEach(entry => {
    source.sendSuccess(Component.literal('  ' + entry[0] + '  —  ' + entry[2]), false)
  })
  return KEEPSAKES.length
}

// =============================================================================
// The command. A second Commands.literal('valley') root; Brigadier merges it
// into the tree valley_finales.js registers.
// =============================================================================
ServerEvents.commandRegistry(event => {
  let Commands = event.commands

  event.register(
    Commands.literal('valley')
      .requires(src => src.hasPermission(0))
      .then(KEEPSAKES.reduce((node, entry) =>
        node.then(Commands.literal(entry[0])
          .executes(ctx => giveKeepsake(ctx.source, entry))),
        Commands.literal('keepsake')
          .requires(src => src.hasPermission(0))
          .executes(ctx => listKeepsakes(ctx.source))))
  )

  console.info('[valley] /valley keepsake registered with ' + KEEPSAKES.length + ' keepsakes')
})
