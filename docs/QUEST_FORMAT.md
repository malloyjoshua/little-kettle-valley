# Quest JSON format (compiled to FTB Quests SNBT by tools/scripts/compile_quests.py)

One file per chapter in `story/quests/<act>.json`. Keys are stable slugs; IDs and layout are generated.

```json
{
  "chapter": { "key": "act1", "title": "Act I: The Thaw", "subtitle": ["Spring, Year One"], "icon": "minecraft:oak_sapling", "group": "Story", "order": 0 },
  "reward_tables": [
    { "key": "cozy_crate", "title": "Cozy Crate", "loot_size": 1,
      "loot_crate": { "id": "cozy_crate", "name": "Cozy Crate", "color": 16755200, "glow": false },
      "rewards": [ { "item": "farmersdelight:cabbage_seeds", "count": 4, "weight": 3 }, { "item": "perfectplushies:cat_plushie", "weight": 1 } ] }
  ],
  "quests": [
    { "key": "a1_letter", "title": "The Letter and the Kettle", "subtitle": "Read it twice.", "icon": "minecraft:paper",
      "description": ["Line one of story text.", "", "Line three. Blank strings are paragraph breaks."],
      "deps": [], "optional": false, "shape": "hexagon", "size": 1.5,
      "tasks": [ { "type": "item", "item": "minecraft:oak_log", "count": 16 } ],
      "rewards": [ { "type": "item", "item": "minecraft:bread", "count": 8 }, { "type": "xp_levels", "levels": 2 } ] }
  ]
}
```

## Task types
- `item`: `item`, `count` (default 1), `consume` (true = items are taken)
- `checkmark`: honour system, optional `title`
- `biome`: `biome` id. `dimension`: `dimension` id. `structure`: `structure` id or `#tag`
- `advancement`: `advancement`, optional `criterion`
- `kill`: `entity`, `count`
- `observation`: `block` id to look at, optional `timer` ticks
- `stage`: `stage` (KubeJS stage the team must have)
- `xp`: `levels`. `stat`: `stat`, `count`. `fluid`: `fluid`, `mb`. `energy`: `fe`
- `location`: `pos` [x,y,z], `size` [w,h,d], `dimension`, `ignore_dimension`

## Reward types
- `item`: `item`, `count`
- `xp_levels`: `levels`. `xp`: `points`
- `command`: `command` (leading slash ok), `player` (false = run as server; `@p` is the claiming player), `elevate` (default true), `silent` (default true)
- `loot`: `table` = a reward table key
- `stage`: `stage` (grants a KubeJS stage)
- `toast`: `title`, `description`
- `advancement`: `advancement`
- any reward may set `"team": true` (claimed once per team) and `"autoclaim": "default"|"disabled"|"enabled"|"no_toast"|"invisible"`
  (the five names of `RewardAutoClaim` in ftb-quests 2001.4.22; anything else is written through verbatim and silently ignored by the mod)
- `"toast": true` only matters under `--astral`: it keeps the claim popup on a reward worth interrupting for (see below)

## Quest fields
`key` (unique across all files), `title`, `subtitle`, `icon`, `description` (list of strings), `deps` (list of keys, may cross chapters),
`optional`, `shape` ("default","circle","square","hexagon","octagon","rsquare","pentagon","gear","diamond","heart"), `size`,
`min_width` (int, px — widen a quest card whose description keeps wrapping), `icon_scale` (double, 1.0 = normal), `hide_lock_icon` (drop the padlock overlay on a locked quest),
`hide_until_deps_complete` (default true, `--astral` false), `hide_details_until_startable` (default true, `--astral` false), `can_repeat`, `min_required_deps`, `dependency_requirement` ("all_completed","one_completed","all_started","one_started"), `guide_page`,
`invisible` (the quest is never drawn — used for the Standing: Trusted gate, completed only by KubeJS), `hide_dependency_lines`, `hide_dependent_lines`,
`x` / `y` (explicit board position; overrides the automatic dependency-depth layout)

## Chapter fields
`key`, `title`, `subtitle` (string or list), `icon`, `group` (chapter-group tab name, default "Story"), `order`,
`always_invisible`, `hide_quest_until_deps_complete`, `hide_quest_details_until_startable` (both only written under `--astral` unless set), `progression_mode`,
`images` — decorations drawn on the chapter board behind the quests:

```json
"images": [
  { "x": 0, "y": -4, "width": 6, "height": 2, "image": "kubejs:textures/gui/act1_banner.png",
    "hover": ["Start here", "then work right"], "order": -1 }
]
```

Image fields: `x`, `y`, `width`, `height` (board units, doubles — `width`/`height` default 1), `image` (required, a texture path),
`rotation` (degrees, default 0), `alpha` (0-255, default 255), `order` (draw order, negative = behind the quests), `hover` (string or list of tooltip lines),
`click` (URL, or a quest id to jump to), `color` (packed int tint), `corner` (pin to the screen corner instead of the board), `dev` (only visible in the quest editor),
`dependency` (a quest key — the image stays hidden until that quest is complete).
`images` is only written when a chapter declares it, so chapters without it are unaffected.

## `--astral` mode
`compile_quests.py <src> <out> <ids.json> [--strict] [--astral]`. Without the flag the output is unchanged, byte for byte
(regression-checked by compiling `story/quests` to a temp dir and diffing against `pack/config/ftbquests/quests`).
`--astral` applies the two Create: Astral quest-book conventions from `docs/research/astral-questbook.md` that a *tech* pack wants and a *story* pack does not:

1. **Nothing is hidden, only greyed.** `hide_until_deps_complete` and `hide_details_until_startable` default to **false**, and the false is written
   explicitly on every quest (plus `hide_quest_until_deps_complete: false` / `hide_quest_details_until_startable: false` on the chapter) so no chapter-level
   default can re-hide the board. The player can read a whole chapter on day one and plan toward it. A quest that genuinely must stay dark still sets
   `"hide_until_deps_complete": true` on itself and wins.
2. **Rewards auto-claim silently.** Every reward's `auto` defaults to `"no_toast"` instead of `"enabled"` — the items still land in the inventory the moment
   the quest ticks, but the screen stops filling with popups. A reward worth an interruption sets `"toast": true` and gets `"enabled"`.
   An explicit `"autoclaim"` on a reward always wins over both.

## Rules
- Every `item` and `icon` must exist in `scratch/ids.json`. The compiler fails on unknown ids in strict mode.
- One entry quest per chapter (a quest with no deps), unless the chapter is a side board.
- Keep descriptions to 2 to 6 short lines. The pinned HUD shows the title, so titles must be the instruction.
