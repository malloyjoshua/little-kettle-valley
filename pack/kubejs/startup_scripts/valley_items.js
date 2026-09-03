// =============================================================================
// valley_items.js — Copper Kettle Valley: every custom item, plus the Town
// Anchor block. Runs at registry time (startup_scripts), KubeJS 2001.6.5.
//
// Textures: every item below ships a 16x16 PNG at
//   pack/kubejs/assets/valley/textures/item/<name>.png
// KubeJS' generated item model uses layer0 = valley:item/<name> by default, so
// no .texture() call is needed and nothing can point at a missing path.
// Display names are also mirrored in pack/kubejs/assets/valley/lang/en_us.json.
//
// Naming contract: every id registered here is also listed, one per line, in
//   story/quests/_custom_ids.txt
// so the quest compiler's strict id check accepts it.
// =============================================================================

// -----------------------------------------------------------------------------
// The roster. [id, display name, max stack]
// Grouped by the job each item does in the story.
// -----------------------------------------------------------------------------
const VALLEY_ITEMS = [
  // --- Currency and paper (Q1, Q19, Q85, Q86, §5.10 Scrip economy) ----------
  ['scrip',                 'Valley Scrip',            64],
  ['letter',                "Josie's Letter",           1],
  ['deed',                  'The Kettle Farm Deed',     1],  // first join
  ['deed_works',            'The Works Deed',           1],  // Q86 -> QuarryPlus gate
  ['kettle_deed',           'Kettle Family Deed',       1],  // Act V finale
  ['bounty_receipt',        'Bounty Receipt',          64],  // Bountiful pools, Endless Seasons

  // --- Gate ingredients (§5 "The gates, concretely") ------------------------
  ['green_oak_plank',       'Green Oak Plank',         64],  // Q15 input
  ['seasoned_oak_board',    'Seasoned Oak Board',      64],  // gate 1 -> water wheel
  ['lake_sand',             'Lake Sand',               64],  // Q26 dredging
  ['washed_silica',         'Washed Silica',           64],  // gate 2 -> machine frame
  ['spring_water',          "Spring Water",            16],  // gate 4 -> AE2
  ['works_power_tap',       'Works Power Tap',         16],  // gate 3 -> CfB kitchen
  ['turbine_notes',         "Josie's Turbine Notes",    1],  // gate 5 -> Bigger Reactors

  // --- The buried secret (Q45, Q54, Q55, Q67) -------------------------------
  ['kettle_plate_a',        'Kettle Plate A',           1],
  ['kettle_plate_b',        'Kettle Plate B',           1],
  ['deep_survey',           "Tobin's Deep Survey",      1],

  // --- Deliveries and the order board (Q45a, Q49, Q53, Q63) -----------------
  ['delivery_crate',        'Delivery Crate',          16],
  ['courier_parcel',        'Courier Parcel',          16],
  ['feast_crate',           'Feast Crate',             16],

  // --- Livestock and smallholding (Q10, Q25, Q26, §8 worked example 2) ------
  ['hen_crate',             'Hen Crate',               16],
  ['cow_crate',             'Cow Crate',               16],
  ['sheep_crate',           'Sheep Crate',             16],
  ['chicken_feed',          'Chicken Feed',            64],
  ['dredge_net',            'Dredge Net',               1],
  ['ice_auger',             'Ice Auger',                1],

  // --- Winter and the hearth (Act IV) ---------------------------------------
  ['firewood_bundle',       'Firewood Bundle',         16],
  ['blanket',               'Wool Blanket',            16],
  ['winter_cloak',          'Winter Cloak',             1],
  ['winter_tonic',          'Winter Tonic',            16],
  ['winter_tomato',         'Winter Tomato',           64],

  // --- Light: the Lantern Road (Q34, Q36, Q74, Q90, Act IV finale) ----------
  ['paper_lantern',         'Paper Lantern',           64],
  ['josies_lantern',        "Josie's Lantern",          1],
  ['hearthkeepers_lantern', "Hearthkeeper's Lantern",   1],

  // --- Trophies, decor and shop stock (Act III/V, Oda's Counter) ------------
  ['plushie_token',         'Plushie Token',           16],
  ['copper_kettle_trophy',  'The Copper Kettle',        1],
  ['place_setting',         'Place Setting',           16],
  ['oda_broom',             "Oda's Broom",              1],
  ['odas_ledger',           "Oda's Ledger",             1],
  ['framed_town_map',       'Framed Town Map',         16],

  // --- P1 NPC token handshake: one token per resident -----------------------
  ['token_marnie',          "Marnie's Word",           16],
  ['token_bram',            "Bram's Word",             16],
  ['token_oda',             "Oda's Word",              16],
  ['token_nella',           "Nella's Word",            16],
  ['token_halden',          "Halden's Word",           16],
  ['token_tobin',           "Tobin's Word",            16],
  ['token_wisp',            "Wisp's Word",             16],
  ['token_pip',             "Pip's Word",              16]
]

// Items that read as documents / one-offs get the uncommon rarity tint so they
// are findable in a full inventory. Purely cosmetic.
const UNCOMMON = [
  'letter', 'deed', 'deed_works', 'kettle_deed', 'turbine_notes',
  'kettle_plate_a', 'kettle_plate_b', 'deep_survey', 'josies_lantern',
  'hearthkeepers_lantern', 'copper_kettle_trophy', 'odas_ledger'
]

StartupEvents.registry('item', event => {
  VALLEY_ITEMS.forEach(entry => {
    const id = entry[0]
    const name = entry[1]
    const stack = entry[2]
    const b = event.create('valley:' + id).displayName(name).maxStackSize(stack)
    if (UNCOMMON.indexOf(id) !== -1) b.rarity('uncommon')
  })
  console.info('[valley] registered ' + VALLEY_ITEMS.length + ' custom items')
})

// -----------------------------------------------------------------------------
// valley:town_anchor — Q7. A decorative stone marker. Placing it is what sets
// the Town Anchor (see valley_checks.js, BlockEvents.placed). Quest text calls
// it "Bram's old Surveyor's Stake", so that is its display name.
// Texture is a vanilla block texture reference, which is guaranteed present on
// every client; no block PNG is shipped.
// -----------------------------------------------------------------------------
StartupEvents.registry('block', event => {
  event.create('valley:town_anchor')
    .displayName("Surveyor's Stake")
    .textureAll('minecraft:block/chiseled_stone_bricks')
    .stoneSoundType()
    .hardness(1.5)
    .resistance(6.0)
    .requiresTool(false)
    .tagBlock('minecraft:mineable/pickaxe')
  console.info('[valley] registered valley:town_anchor')
})
