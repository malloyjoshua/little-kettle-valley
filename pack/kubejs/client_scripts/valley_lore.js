// =============================================================================
// valley_lore.js — Little Kettle Valley: item lore for every custom item.
// KubeJS 2001.6.5 / Forge 1.20.1. MUST live in kubejs/client_scripts/ —
// ItemEvents.tooltip is a client event and does nothing server-side.
// =============================================================================
// The pack registers 48 custom items in startup_scripts/valley_items.js plus
// the Surveyor's Stake block, and until now every one of them was a display
// name and nothing else. This file is the only place item lore lives.
//
// THE RULE (docs/writing-craft.md §4, "Item lore"): two lines, each under 50
// characters, and each line is a fact about the owner or the making — never a
// stat, never what the item does. The worked example is Oda's brass key:
//   "Her initials scratched off. Yours scratched on."
// Line 1 is the object. Line 2 is the turn — the thing the object gives away
// about whoever handled it.
//
// VOICE. Whoever's hand the tag is in writes it, in the register that resident
// uses everywhere else in the pack:
//   Josie   — chalk and paper, states a number or a time of night, dry after
//             the hard sentence, never inside it.
//   Marnie  — feeds you instead of asking how you are.
//   Bram    — laconic; talks about the part, not the feeling.
//   Oda     — ledger hand: counts, dates, files, does not round up.
//   Nella   — undersells, and is already damp.
//   Halden  — unhurried; the kettle is always already on.
//   Tobin   — right about the rock, terrible at saying so.
//   Wisp    — sentences slightly wrong, and warmer for it.
//   Pip     — names things, in capitals.
//
// FORMATTING. Gray italic, matching the one lore line the pack already had —
// the Kettle Farm Compass in server_scripts/valley_core.js:
//   Lore:['{"text":"It points at the hearth.","color":"gray","italic":true}']
// That compass is a vanilla minecraft:compass with display NBT set by command,
// so it is NOT in the table below and must not be: giving it a tooltip here
// would double the line on the one item that already has it.
//
// Rhino: no `const` inside a function body in this pack (KubeJS runs Rhino in a
// mode where a const in a nested scope can be re-entered on a reload and
// throw). Top-level const only; `let` everywhere inside.
//
// Packwiz: kubejs/ is a pack folder and is synced to clients — client_scripts/
// hide.js is already listed in pack/index.toml, so `packwiz refresh` picks this
// file up the same way. Run refresh before any sync.
// =============================================================================

// -----------------------------------------------------------------------------
// The table. [item id without the namespace, [line 1, line 2]]
// Grouped exactly as valley_items.js groups the roster, so the two files can be
// read side by side and a missing item is visible.
// -----------------------------------------------------------------------------
const LORE = [

  // --- Currency and paper ---------------------------------------------------
  ['scrip',                 ['Oda writes the number on by hand.',
                             'She has never once rounded up.']],
  ['letter',                ['Four pages, and the fourth one is a map.',
                             'Written a year early, in case.']],
  ['deed',                  ['The farm, the chimney, eleven feet of porch.',
                             'She left the top line blank for four years.']],
  ['deed_works',            ['Eight names under it. Bram signed as witness.',
                             'The Works belongs to whoever stayed.']],
  ['kettle_deed',           ['Your name on the line she left blank.',
                             'Filed the afternoon Pip rang the bell.']],
  ['bounty_receipt',        ['Torn off the board, ticked at the counter.',
                             'Oda files them. There is a drawer of them.']],

  // --- Gate ingredients -----------------------------------------------------
  ['green_oak_plank',       ['Cut this spring. Still heavy with the wet.',
                             'Bend one and it stays bent, so nobody does.']],
  ['seasoned_oak_board',    ['Two minutes of furnace heat, and it holds.',
                             'Josie was insufferable about the method.']],
  ['lake_sand',             ['Dredged off Nella\'s boat, sixteen a pull.',
                             'She never once let you into the water.']],
  ['washed_silica',         ['Lake sand, washed until it stops squeaking.',
                             'Bram did his first batch four times.']],
  ['spring_water',          ['From the spring above the hedge garden.',
                             'Josie filled her jars here, never for tea.']],
  ['works_power_tap',       ['Comes off the line at the inn\'s back wall.',
                             'Bram ran the duct. Marnie got a fridge.']],
  ['turbine_notes',         ['Forty pages of turbine sums, in her hand.',
                             'The margins argue with the book she bought.']],

  // --- The buried secret ----------------------------------------------------
  ['kettle_plate_a',        ['Copper, scratched over in her shorthand.',
                             'Halden could read it four years ago.']],
  ['kettle_plate_b',        ['The second half. It went out with a trader.',
                             'He could not read a word of it.']],
  ['deep_survey',           ['Tobin read the echo and drew the seam.',
                             'Signed, dated, and right, which he expected.']],

  // --- Deliveries and the order board ---------------------------------------
  ['delivery_crate',        ['It fills itself now, which took a year.',
                             'Oda counts the contents anyway.']],
  ['courier_parcel',        ['Paper, string, and a name in Pip\'s capitals.',
                             'This one says HENRIETTA. He did not explain.']],
  ['feast_crate',           ['One of each dish, packed for Founder\'s Day.',
                             'Marnie set eight aside before anyone ate.']],

  // --- Livestock and smallholding -------------------------------------------
  ['hen_crate',             ['Two hens and a rooster, slats and straw.',
                             'Do not name the rooster. Marnie means it.']],
  ['cow_crate',             ['Came up on the wagon, counted at both ends.',
                             'Oda\'s end and yours. Hers was right.']],
  ['sheep_crate',           ['Slats, straw, and one ewe with a torn ear.',
                             'Nella carried it up from the pier herself.']],
  ['chicken_feed',          ['Marnie\'s mix: barley, grit, crushed shell.',
                             'She mixes it in a chipped bread bowl.']],
  ['dredge_net',            ['Nella\'s net, mended in four colours.',
                             'She had it in the boat the whole time.']],
  ['ice_auger',             ['Nella sharpened it in October, from habit.',
                             'She has no lake from December to March.']],

  // --- Winter and the hearth ------------------------------------------------
  ['firewood_bundle',       ['Split, stacked, and tied in fours.',
                             'Sixteen to a house. Oda counted them out.']],
  ['blanket',               ['Eight wool round one string, on the loom.',
                             'Beds get made before the people arrive.']],
  ['winter_cloak',          ['Marnie\'s, and she is taller than you.',
                             'She had it out of the chest before you asked.']],
  ['winter_tonic',          ['Halden\'s still: a flask, a leaf, one sugar.',
                             'Nobody in the valley got ill that winter.']],
  ['winter_tomato',         ['Grown in February, under Nella\'s glass.',
                             'Marnie ate the first one in the doorway.']],

  // --- Light: the Lantern Road ----------------------------------------------
  ['paper_lantern',         ['Eight sheets of paper round one torch.',
                             'Nella made forty and said nobody would come.']],
  ['josies_lantern',        ['Off the fortieth post, on Josie\'s porch.',
                             'She asked, on the last page, to be on the line.']],
  ['hearthkeepers_lantern', ['Lit the night the valley kept its own lights.',
                             'It has not been out since. Marnie checks.']],

  // --- Trophies, decor and shop stock ---------------------------------------
  ['plushie_token',         ['One token, one shelf, one plushie.',
                             'Pip has spent eleven. Oda wrote each one down.']],
  ['copper_kettle_trophy',  ['Older than Josie, and she was seventy-one.',
                             'It hangs over your hearth now. Put it on.']],
  ['place_setting',         ['A bowl, a brick, an iron and a copper ingot.',
                             'Marnie set twelve. Three chairs stayed empty.']],
  ['oda_broom',             ['Off the store\'s back door, worn to a wedge.',
                             'Eleven years of sweeping an empty shop.']],
  ['odas_ledger',           ['Eleven years of red ink, in one small hand.',
                             'She held it long enough. Now you hold it.']],
  ['framed_town_map',       ['The mill, the square, the lake, forty posts.',
                             'Drawn before the last seventeen went in.']],
  ['catalogue',             ['Oda\'s full stock list, priced in her hand.',
                             'Two pages stayed blank for eleven years.']],

  // --- The eight resident tokens --------------------------------------------
  ['token_marnie',          ['A bread tag off the loaf she carried up.',
                             'It was in her apron the whole walk.']],
  ['token_bram',            ['The Millwright\'s Bolt, out of his palm.',
                             'He would not call it help. He called it holding.']],
  ['token_oda',             ['A ledger page, folded twice, corner initialled.',
                             'She dated it. Oda dates everything.']],
  ['token_nella',           ['A brass ferry chit, green round the edges.',
                             'She handed it over without getting up.']],
  ['token_halden',          ['A sprig of hedge, tied with garden twine.',
                             'He gave it while the kettle was still on.']],
  ['token_tobin',           ['A thumb of copper ore, marked in pink chalk.',
                             'He explained it twice. It got no clearer.']],
  ['token_wisp',            ['A reed ring, woven mid-sentence.',
                             'Is for neighbour. The near kind, not far.']],
  ['token_pip',             ['A duck feather in a folded paper sleeve.',
                             'Biscuit\'s. The sleeve says BISCUIT.']],

  // --- The Surveyor's Stake (the block item from valley_items.js) ------------
  ['town_anchor',           ['Bram\'s stake, wrapped in a rag, chalked K.',
                             'He surveyed that flat twice and never drove it.']]
]

// -----------------------------------------------------------------------------
// Gray italic, one component per line, matching the compass. Text.gray() is
// already used across this pack (valley_finales.js), so nothing new is being
// relied on here.
// -----------------------------------------------------------------------------
ItemEvents.tooltip(event => {
  LORE.forEach(entry => {
    let lines = entry[1].map(line => Text.gray(line).italic(true))
    event.add('valley:' + entry[0], lines)
  })
  console.info('[valley] lore on ' + LORE.length + ' items')
})
