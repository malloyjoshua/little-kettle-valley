# Quest JSON format (compiled to FTB Quests SNBT by tools/scripts/compile_quests.py)

One file per chapter in `story/quests/<chapter>.json`. Keys are stable slugs; IDs and layout are generated.

Chapters ship in this order: `readme` (Read Me First, order 0) · `start` (Start Here, q01–q08, order 1) ·
`act1`–`act5` (orders 2–6) — all in the **Story** group — and `oda` (Oda's Counter, order 0) in the **Side Quests**
group. A quest id is `sha1(key)`, never the filename, so a quest can be moved between chapter files without
breaking live progress, `/ftbquests`, or `_quest_ids.js`.

```json
{
  "chapter": { "key": "act1", "title": "Act I: The Thaw", "subtitle": ["Spring, Year One"], "icon": "minecraft:oak_sapling", "group": "Story", "order": 2 },
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
  (the five names of `RewardAutoClaim` in ftb-quests 2001.4.22; anything else is written through verbatim and silently ignored by the mod).
  You almost never need it — the compiler picks the right one per reward type; see **One toast per quest** below.
- `"toast": true` forces `"enabled"` on a reward that has earned its own popup (a hero item like Josie's Lantern). Use it once or twice in the whole book.

## Quest fields
`key` (unique across all files), `title`, `subtitle`, `icon`, `description` (list of strings), `deps` (list of keys, may cross chapters),
`optional`, `shape` ("default","circle","square","hexagon","octagon","rsquare","pentagon","gear","diamond","heart"), `size`,
`min_width` (int, px — widen a quest card whose description keeps wrapping; 300 is applied to the eight quests over 500 characters), `icon_scale` (double, 1.0 = normal), `hide_lock_icon` (drop the padlock overlay on a locked quest),
`hide_until_deps_complete` (**default false** — see **Nothing hides** below; set true on a genuine surprise), `hide_details_until_startable` (**default false**, same rule),
`can_repeat`, `min_required_deps` (int — the quest starts once this many of its `deps` are done instead of all of them; used on the act finales so one skipped side branch never walls the act), `dependency_requirement` ("all_completed","one_completed","all_started","one_started"), `guide_page`,
`invisible` (the quest is never drawn — used for the Standing: Trusted gate, completed only by KubeJS), `hide_dependency_lines`, `hide_dependent_lines`,
`x` / `y` (explicit board position; overrides the automatic dependency-depth layout)

## Chapter fields
`key`, `title`, `subtitle` (string or list), `icon`, `group` (chapter-group tab name, default "Story"), `order`,
`always_invisible`, `hide_quest_until_deps_complete`, `hide_quest_details_until_startable` (both default false and are always written, so a chapter can never re-hide the quests the quest emitter drew), `progression_mode`,
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

## Book-wide conventions the compiler applies for you

`compile_quests.py <src> <out> <ids.json> [--strict]`. Two of the Create: Astral conventions from
`docs/research/astral-vs-valley.md` (A1 and A2) are baked into the emitter rather than repeated on every quest,
because they are decisions about the *book*, not about any one quest.

### 1. Nothing hides — a locked quest is greyed, not absent

`hide_until_deps_complete` and `hide_details_until_startable` both default to **false**, and the false is written
explicitly on every quest (plus `hide_quest_until_deps_complete: false` / `hide_quest_details_until_startable: false`
on every chapter) so no chapter-level default can re-hide the board. Opening a chapter shows the whole act as a
connected map: the finished quests filled, the current one lit, the rest greyed with their titles and subtitles
readable. The player can see that an act is twelve steps long and that step nine is a kitchen.

A quest that is a genuine reveal opts back in on itself:

```json
{ "key": "q55", "hide_until_deps_complete": true, "hide_details_until_startable": true }
```

`progression_mode` in `data.snbt` stays `"flexible"`. Astral uses `linear`, but linear is doing Astral's hiding for
it; with a visible board, flexible is the more forgiving of the two and it protects our braided dependencies.

### 2. One toast per quest

`auto` is chosen by reward type, so a finished quest shows the quest-complete toast plus exactly one reward toast —
the `Next:` line — instead of eleven. **Nothing about auto-claiming changes**: every reward still lands in the
inventory the instant the quest ticks (the fix for the lost Homestead Waystone), only the popup volume drops.

| Reward type | `auto` written | Why |
|---|---|---|
| `item`, `xp`, `xp_levels`, `loot` | `no_toast` | the stack arrives silently and is still listed on the quest card |
| `command`, `stage`, `advancement` | `invisible` | machinery — scene commands and KubeJS stages are not gifts, so they are neither toasted nor listed as loot |
| the **first** `toast` reward on the quest | `enabled` | our `Next:` line, the one popup worth reading |
| any **later** `toast` reward on the same quest | `no_toast` | a quest can never fire two |

Overrides, in order of precedence: an explicit `"autoclaim": "..."` on the reward always wins; then `"toast": true`,
which forces `"enabled"`; then the table above.

## Rules
- Every `item` and `icon` must exist in `scratch/ids.json`. The compiler fails on unknown ids in strict mode.
- One entry quest per chapter (a quest with no deps), unless the chapter is a side board or a reference tab.
  `oda` is a side board; `readme` is a reference tab and every one of its nine quests is a root on purpose.
  `validate_quests.py` reports the extra roots as a WARN, not an error.
- Set `icon` to the item the task asks for whenever the quest is "go and get N of X" and X is a real good.
  Keep a machine icon where the quest *is* "use this machine" (q06's kettle, q18's oven), and keep the goods
  icon on Oda's counter, where the task item is currency and twenty identical Scrip icons would read as nothing.
- Keep descriptions to 2 to 6 short lines. The pinned HUD shows the title, so titles must be the instruction.
