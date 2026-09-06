# The quest book, rebuilt the FTB Evolution way (2026-09-06, overnight)

Josh, 2026-09-05 22:00: "I've been playing FTB Evolution and I really like their quest line. You
aren't really this good at making what I want. I am going to let you run all night so I wake up
to a genuinely useful plot, world, etc." This is the spec every writer follows tonight.

## What he likes, measured off his own copy of Evolution (config/ftbquests/quests)

2,072 quests in 40 chapters and 6 groups (Main Questline, Logistics, Resource Automation,
Exploration, Tech Mods, Magic Mods). The Beginning is a short spine of vanilla milestones
(punch a tree, stone, iron, power, first diamond, Nether, blaze, Eyes of Ender, stronghold,
the End, the dragon), and every mod gets its own chapter. Quest text: mean 256 characters,
median 197, one idea each, second person, friendly, tips folded in ("hold ` to Ultimine"),
coloured keywords (&a green for items, &b aqua for concepts, &6 gold for chapter names,
&d for magic, &c red for danger). Every quest rewards XP; most also hand an item or a
loot crate; 349 are "choose one of these". A third of everything is optional. Deps average
1.04 (a chain, not a web). Nothing is hidden. Chapter boards carry 10 to 70 images, almost
all of them the mods' own block and item textures placed as decoration, plus a title banner.
Sizes and shapes mark importance: goals are big hexagons, side quests small rounded squares,
info quests gears. Rules said out loud: "Mods are not gated, so experience progression
however you'd like." Sideways pointers everywhere: "check out the &6Power&r chapter".

## What we keep, exactly

- The world, the residents, the finales, the scenes, Oda's Counter, the letter, the journal.
- **Every existing quest key** (q01–q91, q13a/q13b, the a-suffixed ones, oda_*, rm_*): the KubeJS
  checks poll by key, the scenes and stages fire from reward arrays, `/valley keepsake` and the
  finales assume them. Keys move between files freely (id = sha1(key)). Their `rewards` entries of
  type `command`, `stage`, `loot` are **frozen verbatim**. Their `tasks` are frozen. Their `deps`
  are frozen unless the brief below says otherwise. Titles, subtitles, descriptions, icons,
  shapes, sizes, `optional`, `min_width`, and item/xp rewards may change.
- The compiler and its format (`docs/QUEST_FORMAT.md`): `compile_quests.py story/quests <out> scratch/ids_valid.json --strict`.
- Auto-claim and one toast per quest.

## The new shape

Groups (chapter `group` field) and chapters (`story/quests/<key>.json`), in order:

**The Valley** (main questline; group "The Valley")
- `readme` Read Me First — 6 quests, roots: how the book works; how to Minecraft in two quests
  (move/look/break/place/the 2x2 and 3x3 grid; eat/sleep/the F3 coordinates line); who lives here;
  the truth about the two lanes (the cozy lane is most of the book, five winter quests need the
  reactor, Oda sells every part of it); Oda's Counter is the shortcut.
- `start` Start Here — q01–q08 (keys kept). Backpack (`sophisticatedbackpacks:backpack`) added to q01
  rewards; q03's twelve stacks cut to the five the quest uses.
- `act1`–`act5` — keys kept, text cut to the guide shape, furnishing/dress/fit-out quests flagged
  `optional: true` (they stay in their chains; optional only changes the completion maths and the
  look). Each act chapter gets 6–12 board images and a banner-sized root.
  Sideways pointers added where a system starts: q13 → "&6Create&r chapter", q31 → "&6Thermal&r",
  q50 → "&6Storage Network&r", q70 → "&6The Reactor&r", q09 → "&6Farm & Seasons&r".

**Home & Farm** (group "Home & Farm") — new
- `farm` Farm & Seasons — 14–18 quests. Tilling, seeds, the Serene Seasons calendar and what grows
  when (read `pack/kubejs/server_scripts/seasons_tags.js` and the mod tags), Farmer's Delight
  crops and rich soil, Thermal Cultivation (phytogro, the four Thermal crops), the greenhouse in
  winter. Root free.
- `kitchen` Cooking & Brewing — 12–16. Cooking pot, skillet, cutting board, the Cooking for
  Blockheads kitchen (counter/sink/oven/fridge/toaster), Bakery, Candlelight, Herbal Brews (the
  kettle and teas), Vinery (grapes, press, wine), Nether's Delight. Root free.
- `animals` Animals & Fishing — 10–14. Chickens, ducks, cows, sheep, Domestication Innovation
  (taming, pet upgrades), Aquaculture rods, fish, fish mounts, Ribbits. Root free.
- `home` Home & Town — 10–14, mostly optional. Macaw's doors/windows/roofs/furniture/fences,
  Handcrafted, Supplementaries (signs, jars, lanterns), Comforts (sleeping bags, hammocks),
  Perfect Plushies, Torchmaster megatorch, Carry On. Root free.

**Tech** (group "Tech") — new
- `create` Create — 20–26. Andesite alloy, shafts/cogs, water wheel, millstone, hand crank,
  mechanical press, mixer, encased fans, belts, deployer, saw, mechanical crafting, Steam 'n'
  Rails (track, station, the trainline), Create Deco lamps. Root free (q13 stays the story's
  own first alloy; the chapter's own alloy quest may ALSO exist).
- `thermal` Thermal — 16–22. Redstone flux in one paragraph, the dynamos (stirling, compression,
  magmatic), machine frame (both roads: the mod recipe and Bram's washed-silica one), pulverizer,
  induction smelter, sawmill, centrifuge, augments, energy cells, fluxducts/itemducts, Thermal
  Innovation tools. Root free.
- `power` Power & Logistics — 10–14. What RF is, cells, ducts, Create Addition (alternator, motor,
  rolling mill), Storage Drawers + controller, Sophisticated Storage chests/barrels upgrades,
  item ducts/servos. Root free.
- `ae2` Storage Network — 16–22. The meteorite (a `structure` task on `ae2:meteorite`, nearest
  at x -216 z 72, 110 blocks east of the farm), certus, charger (mod recipe AND Halden's
  spring-water road), inscriber and the presses, ME drive, cells, terminal, crafting terminal,
  molecular assembler, patterns, wireless. Root free.
- `mining` Ores & Mining — 12–16. Vanilla ores are back and Geolosys beds too: samples on the
  grass, the Prospector's Pick, the beds' depths (hematite y 32–60 etc. from the mod's deposit
  files), hammers, vein mining (the held key), Thermal ore processing, the AE2 meteorite as a
  dig. Root free.
- `reactor` The Reactor & the Quarry — 12–16. Bigger Reactors: uranium, casing, the vessel
  (`guide_page` to `valley:journal` field notes f6/f7), fuel rods, control rods, coolant,
  the turbine at 1,800 RPM, the second turbine, QuarryPlus. Root depends on `q67` (Josie's
  turbine notes are the story's reveal and stay so); the quarry quest depends on `q86`.

**The Valley Beyond** (group "The Valley Beyond") — new
- `explore` Places — 12–16. Real places from `scratch/structures_near_spawn.json`, each a
  `structure` task (id from that file) or a `location` task with the coordinates and a 32-block
  box, plus a sentence about what is there: the small dungeon at -424 8, the underground house
  at -344 120, the AE2 meteorite -216 72, the mineshaft -312 248, the illager camp -520 216,
  the bathhouse -600 24, the plague asylum 168 24, the savanna village -328 -504, the ancient
  city -568 -552, the taverns, the shipwrecks, the ruined portals. Loot crates as rewards.
- `travel` Getting Around — 8–12. Waystones (the home one, the town one, warp scrolls),
  Xaero's map and minimap keys, Nature's Compass, Explorer's Compass, Carry On, sleeping bag,
  artifacts.
- `wild` The Wild — 8–12. Friends & Foes, Ribbits, Deeper and Darker (the echo shard is q82's),
  Nether's Delight, YUNG's dungeons and strongholds, When Dungeons Arise, Lootr (per-player
  chests), Corpse (your grave keeps your things).

**Side Quests** (group "Side Quests")
- `oda` Oda's Counter — unchanged.
- `tips` Useful Items & Tips — 10–14, all optional, all `shape: "gear"`: JEI search (and `@mod`),
  the vein-mining key, hammers, backpacks, Jade, Inventory Profiles Next sort key, the sound
  muffler, Toast Control, `/valley keepsake`, `/valley ores`, the F3 line, the seasons HUD,
  voice chat.

## Writing rules (every quest)

- Title = the instruction, ≤ 45 characters. Subtitle ≤ 50, optional, a wry half-line.
- Description: 2–5 short lines, ≤ 320 characters in system chapters, ≤ 450 on a story beat
  that carries one resident line. One idea. Verb first. Blank string = paragraph break.
- Colour codes: `&a` the item you make, `&b` a concept or a key, `&6` another chapter's name,
  `&c` a danger, `&r` to reset. Never more than four coloured runs per quest. Titles may carry
  one colour (e.g. "Build a &aWater Wheel&r").
- Sideways pointers: "For more, see the &6Create&r chapter." on the first quest of any system
  a story quest touches, and back-pointers from system chapters to the story quest that uses
  the thing ("Bram wants two of these on the mill race: Act I, step 8.").
- Residents may speak in Home & Farm and story chapters (one line, then the instruction).
  Tech chapters use the plain friendly guide voice, with a resident aside at most once per chapter.
- Rewards: every quest `xp_levels` 1–3. Most quests also give a useful item (the next
  ingredient, a spare part, a stack of the thing) or a `loot` crate. Each new chapter declares
  ONE reward table (its own crate, named for a resident: "Bram's Crate", "Tobin's Sack",
  "Marnie's Basket" already exists in act1 as `cozy_crate`; `tech_crate` and `story_crate`
  exist too and may be referenced). No `toast` rewards in system chapters except one "Next:"
  on the chapter's last quest pointing at where the story picks the thing up.
- Optional: ≥ 30% of a system chapter; every side branch; every furnishing quest.
- Shapes and sizes: chapter root `hexagon` 2.0; milestone `hexagon` 1.5; normal `square` 1.0;
  optional `rsquare` 1.0; info/tips `gear` 1.0.
- Tasks: `item` with the real count; `structure`/`location`/`dimension`/`kill`/`advancement`
  where the thing is a place or a deed; `checkmark` only for things no task type can see.
- Every item id in `scratch/ids_valid.json`. Every task item must be obtainable: a recipe
  result in `scratch/craftable_ids.json`, or a vanilla natural source (ore, crop, drop, fish,
  structure loot) that you can name. Never ask for a `regions_unexplored:` item (mod removed).
- Board images: 4–10 per chapter from `scratch/textures.txt` only (e.g. `create:block/water_wheel`,
  `minecraft:item/diamond`), sizes 1.5–3, `order: -1`, spread across the board's x range
  (x -6..30, y -6..8); one `hover` per image is nice.
- Deps: within the chapter, a chain or a short tree (mean ≤ 1.3 deps). Cross-chapter deps only
  to story keys (q01–q91) or the chapter's own keys. Never to another new chapter.
- Gates that remain: the reactor (`q67`), the quarry (`q86`). Everything else is parallel now
  (`valley_gates.js` keeps the mods' recipes): say so where it matters ("Bram's road or the
  mod's own recipe, either works").

## Verification (in order)

1. `check_quests.py story/quests scratch/ids_valid.json` warnings only.
2. `compile_quests.py ... --strict` 0 errors.
3. Feasibility: every task item craftable or naturally sourced (tools/scripts/feasibility.py).
4. Headless boot: 0 KubeJS errors, quest count printed.
5. `headless_playthrough.sh`: finales and scenes still fire.
6. Real client (Josh is away): screenshots of every chapter board and the first ten minutes.
