# Josie's Journal — Patchouli book

Book id: **`patchouli:valley_journal`** (external book; Patchouli gives every folder under
`patchouli_books/` the `patchouli` namespace, so the folder name *is* the book id).

## Give command

```
/give @p patchouli:guide_book{"patchouli:book":"patchouli:valley_journal"}
```

The compiler's `item` reward (see `docs/QUEST_FORMAT.md`) takes `item` and `count` only —
no NBT — so **Q1 hands the book with a command reward**, not an item reward:

```json
{ "type": "command",
  "command": "/give @p patchouli:guide_book{\"patchouli:book\":\"patchouli:valley_journal\"}",
  "elevate": true, "silent": true }
```

(`@p` is the claiming player. If the compiler ever grows an `nbt` key on item rewards, switch
to that so the reward shows the book's icon in the quest panel.)

Q1's reward hands the book. Nothing else in the pack needs to give it again — Patchouli
remembers the book per player, and `"show_toasts": true` pops a toast when a new entry unlocks.

## File map

```
pack/patchouli_books/valley_journal/
├── book.json                                  name / landing_text / model / colours
└── en_us/
    ├── categories/
    │   ├── journal.json                       "Josie's Hand"        sortnum 0
    │   ├── field_notes.json                   "Field Notes"         sortnum 1
    │   └── found_books.json                   "Things You Found"    sortnum 2
    └── entries/
        ├── journal/            (6 entries)
        │   ├── entry_1_the_porch.json         no advancement — readable from Q1
        │   ├── entry_2_the_fair.json          valley:journal/entry_2
        │   ├── entry_3_the_float.json         valley:journal/entry_3
        │   ├── entry_4_the_works.json         valley:journal/entry_4
        │   ├── entry_5_the_last_page.json     valley:journal/entry_5
        │   └── cellar_wall.json               valley:journal/cellar_wall
        ├── field_notes/        (8 entries — ungated, see below)
        │   ├── f1_andesite_and_the_wheel.json water wheel SU, andesite alloy, board gate
        │   ├── f2_the_windmill.json           sails, 16 RPM ceiling, wool count
        │   ├── f3_silica_and_frame.json       washed silica -> machine frame, Thermal grid
        │   ├── f4_cells_and_ducts.json        energy cell, fluxduct, Works Power Tap, 12 blocks
        │   ├── f5_the_network.json            AE2 controller basics, channels, AE/FE, cells
        │   ├── f6_the_vessel.json             reactor shell arithmetic, casing counts
        │   ├── f7_the_turbine.json            1,800 RPM, the three dials, 5x5x4 minimum
        │   └── f8_quarry_and_markers.json     marker layout, 256 cap, Works Deed gate
        └── found_books/        (5 entries)
            ├── b1_ledger_page.json            valley:journal/found_1   (Q5, the cellar)
            ├── b2_crate_label.json            valley:journal/found_2   (Q12, Bram's crates)
            ├── b3_weathered_notice.json       valley:journal/found_3   (Q19, the store)
            ├── b4_stock_ledger.json           valley:journal/found_4   (Q39, the granary)
            └── b5_turbine_notebook.json       valley:journal/found_5   (Q65, the Works)
```

**19 entries, 3 categories, 23 JSON files.** All validate under `jq`.

## Advancements this book expects

Patchouli has no read-state API and unlocks entries **only** by advancement, so the datapack
must ship these eleven, all as invisible, criterion-free advancements under `valley:journal/`:

| Advancement | Granted by | Unlocks |
|---|---|---|
| `valley:journal/entry_2` | Act I finale (Q19) | Entry Two — The Thaw Fair |
| `valley:journal/entry_3` | Act II finale (Q37) | Entry Three — The Lantern Float |
| `valley:journal/entry_4` | Q54 (Halden hands over the second half) | Entry Four — What the Works Was For |
| `valley:journal/cellar_wall` | Q55 (player inside the cellar box) | The Cellar Wall |
| `valley:journal/entry_5` | Act IV finale (Q75) | Entry Five — The Last Page |
| `valley:journal/found_1` | Q5 reward | The Ledger Page |
| `valley:journal/found_2` | Q12 reward | The Crate Label |
| `valley:journal/found_3` | Q19 reward | The Weathered Notice |
| `valley:journal/found_4` | Q39 reward | Oda's Old Stock Ledger |
| `valley:journal/found_5` | Q65 reward | The Turbine Notebook |
| *(none)* | — | Entry One and all eight Field Notes are always readable |

Grant them from the finale function / quest command reward exactly as §10 specifies:

```
advancement grant @a only valley:journal/entry_2
```

A locked Patchouli entry is **hidden**, not greyed, which matches the pack's
"future chapters are hidden, not greyed" rule. If an advancement is missing at runtime the
entry simply never appears — it will not error — so a missing advancement is a silent bug.
Check all ten after the datapack lands.

**Field Notes are deliberately ungated.** Writer-brief rule 6 says reference material ships
*before* the quest that needs it and rule 14 forbids sending the player to a wiki, so the
numbers must never be behind a gate the player is currently stuck on. Nothing in Field Notes
spoils a plot beat; it is arithmetic.

## Where the numbers came from (do not "correct" these from memory)

Every figure in Field Notes was read out of the shipped jars in `server/mods`, not recalled:

- **Water Wheel 32 su per RPM, 8 RPM** — `create-1.20.1-6.0.8.jar`, stress defaults in
  `AllBlocks` (`water_wheel` -> 32.0; `large_water_wheel` -> 128.0) and
  `WaterWheelBlockEntity.getGeneratedSpeed` (bipush 8). Machine impacts from the same table:
  millstone 4, saw 4, press 8, mixer 4, encased fan 2, mechanical crafter 2, deployer 4.
- **Windmill: 2 RPM per sail, ceiling 16** — `WindmillBearingBlockEntity.getGeneratedSpeed`
  (float 2.0, cap 16). Eight sails is both the assembly minimum and the ceiling.
- **AE2 controller / channels / energy** — `appliedenergistics2-forge-15.4.10.jar`, the mod's
  own guide: `assets/ae2/ae2guide/items-blocks-machines/controller.md` (32 channels per face,
  6 AE/t, 8,000 AE per block, 7x7x7, one-axis rule) and
  `assets/ae2/ae2guide/ae2-mechanics/energy.md` (2 FE = 1 AE, 25 AE per part, energy cell
  200k, dense 1.6M) and `channels.md` (8 per cable/full block, 32 dense, ad-hoc max 8).
- **Reactor / turbine minimums and ceilings** — `server/config/biggerreactors-server.toml`
  (reactor min 3, max 128x128x192; turbine min 5x5x4, max 32x32x192).
- **Quarry marker cap 256, chunk loading on** — `pack/config/quarryplus-common.toml`
  (`flexMarkerMaxDistance = 256`, `enableChunkLoader = true`).
- **Quest counts** (8 alloys, 32 boards, 96 lake sand, 64 washed silica, 32 certus, 64 ore ->
  128 ingots -> 64 casings, 1,800 RPM, 1,024 cobblestone, 80 Scrip for the deed) —
  `story/outline.json` and `story/story-final.md` §5, §12.4.
- **Reactor shell arithmetic** — computed, not looked up: shell = LWH minus (L-2)(W-2)(H-2).
  3x3x3 = 26, 4x4x4 = 56, 5x5x5 = 98. The 64 casings Q69 pays out build the 4x4x4.

## Crafting pages — which recipe ids are safe

Every `patchouli:crafting` page in the book points at a recipe json that **exists in a shipped
jar and is not one of the six §12.4-P4 gated recipes**. Verified present:

```
create:crafting/materials/andesite_alloy
create:crafting/kinetics/millstone
create:crafting/kinetics/windmill_bearing
thermal:machine_pulverizer
ae2:network/blocks/storage_drive
ae2:network/blocks/controller
ae2:network/blocks/energy_energy_cell
biggerreactors:crafting/reactor/reactor_fuel_rod
biggerreactors:crafting/reactor/reactor_control_rod
biggerreactors:crafting/reactor/reactor_access_port
biggerreactors:crafting/turbine/turbine_rotor_blade
quarryplus:flex_marker
```

**Never add a crafting page for these** — `valley_gates.js` removes and replaces them, and a
Patchouli crafting page on a removed recipe renders as a blank grid:

- `create:water_wheel` (gated on Seasoned Oak Boards)
- `thermal:machine_frame` (gated on Washed Silica)
- AE2 certus seeds (gated on Spring Water)
- CookingForBlockheads Fridge / Sink / Milk Jar (gated on Works Power Tap)
- `biggerreactors:reactor_casing` (gated on Turbine Notes)
- `quarryplus:quarry` (gated on the Works Deed — and it is a `quarryplus:workbench_recipe`,
  which Patchouli's crafting page cannot render regardless)

Those six are described in **text** instead, naming the gate item and who holds it, per
writer-brief rule 9.

If the KubeJS writer wants those replacement recipes shown in the book, give the replacement
a stable id in `valley_gates.js` (e.g. `kubejs:valley/water_wheel`) and add a crafting page
here pointing at it. Until then, text.

## Style rules this book is written to

- Josie is wry, practical, never sad for long, and never present.
- Residents keep their register: Bram short and technical, Tobin fast and over-explaining,
  Oda counting things.
- Field Notes name the item, the count and the place. No "gather some", no timers, no fail
  states, no "before it's too late".
- The destination line is the book's `landing_text` and is never paraphrased:
  **"Forty lamps. Fifteen people. One winter that nobody leaves."**
- ASCII only in page text — no em dashes, no smart quotes — so nothing renders as a box.

## Editing

Page text uses Patchouli's default macros only: `$(br)`, `$(br2)`, `$(bold)`, `$(italic)`,
`$(item)`, `$(li)`, and `$()` to reset. Nothing custom, so no `macros` block in `book.json`.

After any edit:

```
find "pack/patchouli_books/valley_journal" -name "*.json" -exec jq -e . {} \; > /dev/null
```
