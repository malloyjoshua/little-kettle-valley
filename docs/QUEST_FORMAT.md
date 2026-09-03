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
- any reward may set `"team": true` (claimed once per team) and `"autoclaim": "enabled"|"invisible"`

## Quest fields
`key` (unique across all files), `title`, `subtitle`, `icon`, `description` (list of strings), `deps` (list of keys, may cross chapters),
`optional`, `shape` ("default","circle","square","hexagon","octagon","rsquare","pentagon","gear","diamond","heart"), `size`,
`hide_until_deps_complete` (default true), `hide_details_until_startable` (default true), `can_repeat`, `min_required_deps`, `dependency_requirement` ("all_completed","one_completed","all_started","one_started"), `guide_page`,
`invisible` (the quest is never drawn — used for the Standing: Trusted gate, completed only by KubeJS), `hide_dependency_lines`, `hide_dependent_lines`,
`x` / `y` (explicit board position; overrides the automatic dependency-depth layout)

## Rules
- Every `item` and `icon` must exist in `scratch/ids.json`. The compiler fails on unknown ids in strict mode.
- One entry quest per chapter (a quest with no deps), unless the chapter is a side board.
- Keep descriptions to 2 to 6 short lines. The pinned HUD shows the title, so titles must be the instruction.
