# Create: Astral — Quest Book Structural Inventory

Reference pack: `Create- Astral` (PrismLauncher instance, read-only, never launched or modified). Source of every number below: a full parse of every file in `config/ftbquests/quests/` — `data.snbt`, `chapter_groups.snbt`, `chapters/*.snbt` (13 files, ~25,400 lines total), and `reward_tables/*.snbt` (7 files) — plus `kubejs/assets/createastral/lang/en_us.json` for the actual English text behind the `{ftbquests....}` translation keys the SNBT stores instead of literal strings. Keybind and give-on-join behavior cross-checked against `options.txt` and `kubejs/server_scripts/misc/interaction.js`. Everything here is inventory, not a play-through — see `astral-onboarding.md` for the real-session notification/pacing log.

A small custom SNBT parser was written for this pass (`Parser` class, handles FTB Quests' comma-optional / unquoted-key / typed-literal dialect) — it parsed all 13 chapter files and all 7 reward tables without errors.

## 1. Top-level shape

| | |
|---|---|
| Chapters | **13** files |
| Chapter groups | **1** ("Side Quests", id `31A321D19BB5F68F`) |
| Chapters in that group | **5** — `chapter_25_the_automation_matrix`, `culinary_delights`, `astral_signals`, `astral_storage`, `the_trophy_room` |
| Chapters in the main (ungrouped) tab | **8** |
| Total quests | **851** (851 unique ids — no collisions) |
| Total reward tables (loot crates) | **7** |
| `progression_mode` | `"linear"` |
| `default_quest_shape` | `"circle"` (every chapter's own `default_quest_shape` is `""`, i.e. inherits this) |
| `default_autoclaim_rewards` | `"disabled"` — confirmed pack-wide; grepped every file for `auto_claim`/`autoClaim` and found **zero** per-quest or per-reward overrides, so nothing in the book ever auto-claims. The player must always open the reward screen and click. |
| `lock_message` | `""` (empty — no custom text shown when a locked chapter is clicked) |
| `pause_game` | `false` |
| `title` / icon | "Create: Astral" / `createastral:textures/item/logos_binted.png` |

## 2. Chapter list, in book order

Order is `order_index` **within each group's own namespace** — the main tab and the Side Quests tab each count 0..N independently, which is why two files both show `order=0`.

### Main tab (order_index 0→7)

| # | Title | File | Quests | Deps: 0 / 1 / 2+ | Optional | Reward objects |
|---|---|---|---:|---|---:|---:|
| 0 | Read the Questbook! (FAQ) | `read_the_questbook.snbt` | 23 | 23 / 0 / 0 | 0 | 0 |
| 1 | 0.5) Getting Started | `assorted_goals.snbt` | 45 | 2 / 39 / 4 | 25 | 45 |
| 2 | 1) The Andesite World | `chapter_2.snbt` | 60 | 0 / 56 / 4 | 9 | 80 |
| 3 | 2) Getting Industrial | `chapter_3.snbt` | 84 | 0 / 72 / 12 | 6 | 87 |
| 4 | 3) Remnants of a Lost Civilization | `chapter_4.snbt` | 153 | 0 / 136 / 17 | 19 | 136 |
| 5 | 4) Piglin Peculiarities | `chapter_5.snbt` | 83 | 0 / 69 / 14 | 7 | 76 |
| 6 | 5) Sub-Atomic | `6_raow.snbt` | 67 | 0 / 55 / 12 | 1 | 29 |
| 7 | 6) The End | `6.snbt` | 54 | 0 / 44 / 10 | 0 | 32 |

### Side Quests tab (order_index 0→4)

| # | Title | File | Quests | Deps: 0 / 1 / 2+ | Optional | Reward objects |
|---|---|---|---:|---|---:|---:|
| 0 | The Automation Matrix | `chapter_25_the_automation_matrix.snbt` | 176 | 0 / 152 / 24 | 0 | 8 |
| 1 | Culinary Delights | `culinary_delights.snbt` | 36 | 0 / 24 / 12 | 8 | 28 |
| 2 | &k1.5&r) Astral Signals | `astral_signals.snbt` | 31 | 0 / 19 / 12 | 0 (2 invisible) | 15 |
| 3 | 3.5) Astral Storage | `astral_storage.snbt` | 26 | 0 / 23 / 3 | 1 | 13 |
| 4 | ?) The Trophy Room | `the_trophy_room.snbt` | 13 | 0 / 12 / 1 | 0 | 13 |

`&k` in "Astral Signals" is a vanilla obfuscated-text formatting code — the chapter tab literally displays as scrambled/glitching text in-game until you're near it.

**The Automation Matrix (176 quests) is the single largest chapter — bigger than three main-tab chapters combined** — and **The Trophy Room (13 quests) is the smallest.**

## 3. Dependency shape — a branching chain, not a strict line and not a wide tree

Across all 851 quests:

| Dependency count | Quests | % |
|---|---:|---:|
| 0 (chapter/branch roots) | 25 | 2.9% |
| 1 | 701 | 82.4% |
| 2 | 91 | |
| 3 | 25 | |
| 4 | 6 | |
| 6 | 1 | |
| 7 | 1 | |
| 12 | 1 | |
| **2+ total** | **125** | **14.7%** |

So the shape is overwhelmingly **single-parent chains** (82% of quests unlock from exactly one prior quest) with periodic **convergence nodes** where 2–12 prior quests must complete before a "chapter capstone" style quest unlocks (`min_required_dependencies` is used on 22 of those, `dependency_requirement` overrides — `one_completed`/`one_started`/`all_started` — appear on 19 quests, letting a node fire from *any one* of several branches instead of requiring all of them).

Looking at it from the other direction (out-degree = how many quests list *this* quest as a dependency):

- **355 quests (42%) are dead ends** — nothing depends on them; they're optional side-branches or terminal rewards.
- **315 quests have exactly 1 child**, continuing the chain.
- Fan-out drops off fast after that (80 have 2 children, 38 have 3, …).
- **One quest is a genuine hub: "What Is This?" in The Automation Matrix has 55 direct children** — the entire 176-quest side chapter fans out from that single intro quest, making it structurally a hub-and-spoke tree rather than a chain like every other chapter.
- Runner-up hubs: "Astral Singularity" (17 children, chapter 6), "Welcome to The Moon!" (13, chapter 4), "The Basis of Automation" (12, chapter 3), "Power the World!" (11, chapter 4).

Net picture: **each main-line chapter is a long single-file chain with a handful of optional side-branches that dead-end**, while **The Automation Matrix is the one deliberately tree-shaped chapter** — a checklist of automation goals radiating from one root instead of a story path.

## 4. Optional / invisible / repeat / hide flags

| Flag | Count | Notes |
|---|---:|---|
| `optional: true` | 76 (8.9%) | Concentrated in "Getting Started" (25 of 45 quests — more than half!) and "Remnants" (19). Side-branch/luxury content, not required to progress. |
| `invisible: true` | 2 | Both in Astral Signals — permanently hidden from the map regardless of dependency state (used for secret/lore quests). |
| `can_repeat: true` | 0 | **Nothing in the entire book is repeatable.** Every quest is a one-time checkbox. |
| `hide: true` / `hide: false` | 35 / 25 (60 quests set it explicitly) | A per-quest "hide the icon" toggle, independent of `invisible`. Frequently paired with `hide_dependency_lines: true` on the same quest — e.g. a hidden Nether-portal-reveal quest in Chapter 6 hides both itself and the line pointing to it until unlocked, for a "surprise" pop-in effect. |
| `hide_dependency_lines: true` | 123 | Purely visual — declutters the connector-line web on dense chapters (Piglin Peculiarities, Remnants) without hiding the quest icon itself. |
| `hide_text_until_complete: true` | 2 | Spoiler-blocks the description text (not the whole quest) until done. |
| `hide_quest_details_until_startable: true` | 1 (chapter-level, not per-quest) | Set on the **Astral Signals** chapter root — every quest in that chapter defaults to hiding its details until startable, overriding the pack's normal per-quest default of `false`. |
| `min_required_tasks` set | 54 | "Complete N of M tasks" quests (not all tasks required). |
| `min_required_dependencies` set | 22 | "Unlock once N of M prerequisite quests are done" — paired with the branching convergence nodes from §3. |

## 5. Per-quest fields actually used (of 851 quests)

| Field | Quests using it | % |
|---|---:|---:|
| `x`, `y`, `id`, `tasks` | 851 | 100% (mandatory) |
| `dependencies` | 826 | 97% |
| `description` | 609 | 72% |
| `subtitle` | 584 | 69% |
| `title` | 466 | 55% (**the other 45% fall back to the icon/first-task item's display name** — e.g. a quest whose only task is "obtain a Furnace" and has no explicit title just shows "Furnace") |
| `rewards` | 402 | 47% |
| `icon` | 292 | 34% (the rest fall back to the first task's item icon) |
| `shape` | 191 | 22% — overrides the pack's global `circle` default. Distribution: diamond 55, square 27, gear 24, pentagon 23, rsquare 22, hexagon 17, octagon 8, heart 8, circle (explicit) 7 |
| `size` | 130 | 15% — values range 0.75d–5.0d, clustering at 1.5d (51 quests) and 2.0d (33) |
| `hide_dependency_lines` | 123 | 14% |
| `optional` | 76 | 9% |
| `hide` | 60 | 7% |
| `min_required_tasks` | 54 | 6% |
| `min_required_dependencies` | 22 | 3% |
| `dependency_requirement` | 19 | 2% |
| `min_width` | 7 | <1% — 6 quests forced to 300px wide, 1 to 1px (near-invisible connector node) |
| `invisible` | 2 | <1% |
| `hide_text_until_complete` | 2 | <1% |

Icon breakdown: **273 quests** use a vanilla/modded item icon directly, **19** use a fully custom PNG (`ftbquests:custom_icon` wrapping a texture path — used for lore quests, e.g. a villager portrait or a painting texture), and **559 (66%)** have no icon field at all and inherit their first task's item icon.

### Description length

- 609 of 851 quests have any description text.
- **Average: 244 characters / 3.9 lines.**
- **Longest: 1,476 characters / 29 lines** — "Moving BLOCKS like a Pro" in Astral Storage, a full tutorial on AE2 Spatial Storage (Spatial Cells + Pylons) written as in-book prose.
- Shortest non-empty descriptions are single-line quips (e.g. "Gone!" style one-liners in the FAQ chapter).
- **6 quests** reference an image filename directly inside their description text (as opposed to a chapter-canvas `images` object) — these are inline `.png` callouts embedded in the prose itself.

## 6. Task types (1,432 task objects total)

| Type | Count | What it checks |
|---|---:|---|
| `item` | 1,126 | Hold/have N of an item (by far the dominant mechanic) |
| `checkmark` | 242 | Manual "I did this" click — used for read-only lore/FAQ entries and for things FTB Quests can't detect (e.g. "you understood the mechanic") |
| `questsadditions:break` | 18 | Break N blocks of a specific type (from the FTB Quests Additions add-on) — used for ore-gathering tutorials in "Getting Started" and a couple of later ore quests |
| `advancement` | 13 | Vanilla/mod advancement completed (e.g. `tconstruct:tools/make_part`) |
| `dimension` | 12 | Visit a specific dimension (Nether, Moon, etc.) |
| `observation` | 8 | "Look at this block/item" detection, all in Chapter 6 (The End) |
| `biome` | 7 | Enter a specific biome |
| `structure` | 4 | Enter/generate near a structure |
| `kill` | 1 | Kill 1 `minecraft:ender_dragon` — the single kill-task in the whole book, unsurprisingly the End chapter's capstone |
| `xp` | 1 | Bank a set amount of XP |

## 7. Reward types (571 reward objects total) and auto-claim

| Type | Count | Behavior |
|---|---:|---|
| `item` | 395 | Standard claimable item stack |
| `loot` | 134 | Rolls from a chapter loot-crate reward table (see §8); always carries `exclude_from_claim_all: true`, so these can never be swept up by a "claim all" button — the player must open each one individually |
| `xp` | 32 | Flat XP grant |
| `random` | 1 | Same loot-table mechanism as `loot` (also `exclude_from_claim_all: true`) — appears exactly once, in Sub-Atomic |

**Nothing auto-claims.** Confirmed both at the global level (`default_autoclaim_rewards: "disabled"`, no per-quest override anywhere) and by the presence of `exclude_from_claim_all` specifically on every loot/random reward, which additionally blocks those from bulk-claim even if a player used the book's "claim all" convenience.

## 8. Reward tables (loot crates)

7 tables exist. FTB Quests reward tables carry a hex `id` (like a quest id), but the `table_id` a reward references is that same hex string reinterpreted as a signed 64-bit integer — confirmed by converting each table's hex id and matching it against every `table_id` used in the chapters:

| Table file | Hex id | Signed-long `table_id` | Loot pool size | Referenced by |
|---|---|---:|---|---|
| `chapter_05.snbt` ("Chapter 0.5") | `65F4E9F0B48DCF6C` | 7346754112178737004 | 31 items | **nobody — orphaned.** No quest anywhere in the book references this table. It exists (basic-materials pool: oak log, stone, diorite, granite, andesite…) but is dead content. |
| `chapter_1.snbt` ("Chapter 1") | `4EEDB842C7C4CB3B` | 5687404501397719867 | 75 items | Andesite World (×8), Remnants (×1 bonus), Astral Signals (×4) |
| `chapter_2.snbt` ("Chapter 2") | `1C7F90CDCD2C8C74` | 2053519168689179764 | 80 items | Getting Industrial (×4), Remnants (×11 bonus), Astral Signals (×2), Automation Matrix (×7 — this side chapter's only reward type at all) |
| `chapter_3.snbt` ("Chapter 3") | `48E82776955518FB` | 5253492355592689915 | 97 items | Remnants (×36, its main crate), Getting Industrial (×1), Piglin Peculiarities (×3 bonus) |
| `chapter_35.snbt` ("Loot Crate: AE2") | `170876D9D871D1C5` | 1659707140697346501 | 30 items | Astral Storage (×12 — its only loot source, all AE2-flavored) |
| `chapter_4.snbt` ("Loot Crate: Chapter 4") | `2671EF8763519011` | 2770258610575478801 | 73 items | Piglin Peculiarities (×34, its main crate) |
| `chapter_5.snbt` ("Loot Crate: Chapter 5-6") | `184075C9E8247561` | 1747526165463332193 | 73 items | Sub-Atomic (×10, main + the one `random` reward), Astral Signals (×1) |

Pattern: each numbered main-tab chapter mostly grants **the loot crate matching its own tier**, with a sprinkling of the previous tier's crate as bonus/early loot in a few quests — the book slightly overlaps reward tiers rather than hard-cutting them. Culinary Delights, The Trophy Room, and The End use **zero** loot-crate rewards — every reward in those three chapters is a specific, named item, not a randomized crate.

## 9. Chapter canvas images (72 total, decorative — not counting quest icons)

| Chapter | Images | What they are |
|---|---:|---|
| Read the Questbook | 1 | A single portal texture, background flavor |
| Getting Started | 1 | The pack's own logo |
| Astral Signals | 7 | Standard Galactic Alphabet (Minecraft enchanting-table glyph) particle textures spelling a word letter-by-letter across the canvas |
| The Andesite World | 5 | Earth sky texture + 4 SGA glyphs |
| Astral Storage | 3 | Two decal blocks + the Phobos sky texture |
| Getting Industrial | 11 | Moon-quest icon, Sun painting, and 9 SGA glyphs spelling two words |
| Remnants | 1 | Moon painting |
| The Trophy Room | **23** | The largest canvas by far: a hexagon outline, the Milky Way, Earth/Moon/Mars/Mercury sky textures arranged as a mini solar-system map, a map-background texture, and 17 SGA glyphs spelling two words across two rows |
| Piglin Peculiarities | 9 | Mars-coolant icon, Mercury painting, Glacio sky texture, 6 SGA glyphs |
| Sub-Atomic | 10 | Mercury sky + painting, three metal-ingot icons, three star-particle textures, the Milky Way painting, and a gradient banner texture |
| The End | 1 | Milky Way sky texture |
| Culinary Delights, Automation Matrix | 0 | No canvas decoration — pure quest grids |

The **Standard Galactic Alphabet glyph-spelling technique** (individual letter textures placed as tiny 1×1 canvas images) is used repeatedly across 6 different chapters to spell out chapter-flavor words directly onto the quest map background — a recognizable, reusable visual signature for the pack rather than a one-off. **The Trophy Room is deliberately staged as a literal solar-system map** (real planet textures at roughly their orbital order left-to-right/up-down around a central hexagon), visually tying the "trophy" endgame chapter to the pack's planet-hopping progression.

## 10. Quest book delivery: does the player actually get a book?

Yes — but it's **not** FTB Quests' own built-in "give book on first join" setting; it's hand-rolled in KubeJS. From `kubejs/server_scripts/misc/interaction.js`:

```js
onEvent("player.logged_in", (event) => {
  if (!event.player.stages.has("starting_items")) {
    event.player.stages.add("starting_items");
    event.player.give("ftbquests:book");
  }
  if (!event.player.stages.has("read_quest")) {
    event.player.tell(
      Text.aqua(Component.translate("logging_tip")).underlined().hover(Component.translate("logging_tip.hover"))
    );
  }
});
onEvent("item.right_click", (event) => {
  if (event.item.id == "ftbquests:book") {
    event.player.stages.add("read_quest");
  }
});
```

- On first login, gated by the `starting_items` player-stage flag, the player is given exactly one `ftbquests:book` item — never re-given on later logins.
- Until the player has ever right-clicked (opened) that book — tracked by a separate `read_quest` stage — every login shows one chat nudge: an aqua, underlined "Please Read The Quest Book (Hover Over Me!)" with a hover tooltip explaining the book and how to dismiss the message (open it once).
- The moment the book is opened, `read_quest` is set permanently and the nudge never appears again, on any future login.

**Keybind:** `options.txt` shows `key_key.ftbquests.quests: key.keyboard.j` — the quest book opens on **J** in this instance. (This is this player's live keybind file, not necessarily the mod's unmodified default — no separate "default keybind" definition file exists to compare against.)

**Client-side FTB Quests settings (pinned/HUD/toasts):** no standalone client-config file for FTB Quests exists anywhere in the instance (`ftbquestsclient.snbt` or equivalent was searched for and not found — FTB Quests apparently doesn't persist HUD/toast toggles to a config file here, only through the in-game GUI). What **is** confirmed, from the live save's per-player progress file (`saves/New World/ftbquests/3b00d9d6-c758-4bc6-9f9f-e068a9eb490d.snbt`, read-only, belongs to player "DefNotJosh"):
- `auto_pin: false` — quests are not automatically pinned to a HUD tracker as they unlock.
- `chapter_pinned: false` — no chapter is pinned either.
- `can_edit: false`, `lock: false`, `rewards_blocked: false`.
- That save already has 8 tasks in progress, 19 quests started, and 15 completed — meaning a real play session has already happened on this instance (worth knowing if you want a "why did this quest feel good" answer straight from lived data rather than only static analysis).

## 11. `data.snbt` settings, verbatim

```
version: 13
title: "Create: Astral"
default_reward_team: false
default_consume_items: false
default_autoclaim_rewards: "disabled"
default_quest_shape: "circle"
default_quest_disable_jei: false
emergency_items_cooldown: 300
drop_loot_crates: false
loot_crate_no_drop: { passive: 4000, monster: 600, boss: 0 }
disable_gui: false
grid_scale: 0.5d
pause_game: false
lock_message: ""
progression_mode: "linear"
```

Note: `config/ftbquests/data.snbt` (one directory up from `quests/`) is a **different, unused default/template copy** — it has `title: "{quest.main_title}"` (an unresolved translation key) and `chapter_groups: [ ]` (no Side Quests group). The live, in-use files are the ones inside `config/ftbquests/quests/`, documented above.

## 12. The first chapter, transcribed in full: "Read the Questbook! (FAQ)"

This is literally chapter `order_index: 0` in the main tab — the first thing a player sees on opening the book. It has **zero dependencies on any quest** (all 23 are independent, no chain), **zero rewards** (every single quest gives nothing), and is built almost entirely from `checkmark` tasks — it is a pure reference/FAQ tab, not a task chapter. Order below follows file order (top to bottom as authored):

| # | Title | Subtitle | First line | Task(s) | Reward |
|---|---|---|---|---|---|
| 1 | Vanilla Tools | Use the Hephaestus tools for early-game instead! | Regular Stone/Wooden tools can still be obtained through the fallback recipe by stonecutting Andesite Alloy. | checkmark | none |
| 2 | Project Tables! | And how to fix quests not registering | Tinker Crafting Stations are not recommended for crafting as they do NOT register quests when taking items from them. Please use Erdragh's "Project Tables" implementation instead. | checkmark + item (`projecttable:projecttable`) | none |
| 3 | Hidden Chapters | Your issues might be solved in later, hidden chapters! | By default, the only chapters displayed in the quest book are those which have been unlocked. | checkmark | none |
| 4 | Common Server Lag Causes | MSPT = MilliSeconds Per Tick. More MSPT, more server lag. | "> Brass Funnels or Smart Chutes" (9-line list of lag culprits) | checkmark | none |
| 5 | Villager FAQ | Massive inhumane trading halls are back, baby! | As of v2.1, villagers have now been reworked. Old progression skips are fixed... | checkmark | none |
| 6 | The Smeltery is disabled! | Alloying is done in a different way! | Hephaestus alloys are made in Create's Mixing Basin. | checkmark | none |
| 7 | Patterns? | Finally, we can use AE2 to its full potential | As of v2.1, AE2 patterns are now ENABLED and craftable. | checkmark | none |
| 8 | Item Transport | So many methods! | To begin with, you'll be using Create's Belts to move items short-range... | checkmark | none |
| 9 | How do I input to storage units? | Crude Storage Unit my beloved | By default, Tech Reborn storage units don't allow automatic inputting nor outputting. | checkmark | none |
| 10 | Brass Info | No filtering options? | In Create: Astral, progression follows a different order than that which you may be familiar with. | checkmark | none |
| 11 | Superheating FAQ | *(none)* | In Create: Astral, progression follows a different order than that which you may be familiar with. | checkmark | none |
| 12 | Where are my portals? | Say farewell to the Nether! | Attempting to construct a Nether Portal will leave you as disappointed as placing Water into a Glowstone portal frame... | `dimension` (overworld) + checkmark | none |
| 13 | Getting to The Moon without rockets? | Moon Portals! | Create: Astral delves into methods of reaching The Moon some would consider 'unconventional'. | checkmark | none |
| 14 | Computercraft / Turtle Chunk Saving! | Computercraft in 1.18.2 has a chunk saving issue! | Wait on the pause menu for around 10 seconds in singleplayer... This bug is not present on dedicated servers. | checkmark | none |
| 15 | Repairing my Space Suit! | Low on durability? | Each Space Suit tier uses vanilla Minecraft mechanics for repairing and enchanting... | checkmark | none |
| 16 | Common FAQ! | We're building an FAQ ingame! ... | As the pack evolves, new knowledge must be shared. | item (`ftbquests:book`) | none |
| 17 | Early-game filtering | No Brass? | Drawers from Extended Drawers in conjunction with Chutes/Andesite Funnels from Create are good replacements for Brass logistics. | checkmark | none |
| 18 | *(untitled → shows sword icon)* | Toggle Combat Music | We heard your request!! Combat music has been turned down and a config option has been added. | checkmark | none |
| 19 | *(untitled → custom "logomusic" icon)* | *(none)* | The custom music you will hear throughout the pack is licensed so that you may use it wherever you wish! | checkmark | none |
| 20 | Create Big Cannon changes | *(none)* | The progression of Big Cannons is slightly modified. | checkmark | none |
| 21 | 10k Fluid Infinite Pools? | Gone! | 10k Infinite Fluid Pools from Create have been disabled in favour of more traditional automation... Check REI for these recipes. | checkmark (labeled "Understood!") | none |
| 22 | How to FTBQuests | First time using a quest book? | Close this quest and hover your mouse to the left of the screen to open the chapter browser :) | checkmark (labeled "Wow thanks!") | none |
| 23 | The Death Penalty | [Experimental Feature!] | A new mod, called "The Death Penalty" has been added in 2.1.5. This mod applies various penalties for dying: respawning with less hunger and increased XP loss. | checkmark (labeled "The Death Penalty") | none |

**Takeaway for our own onboarding:** Astral's actual "first chapter" isn't a tutorial quest line at all — it's a flat, no-stakes FAQ tab (no deps, no rewards, no gating) that exists purely so troubleshooting answers live *inside the book itself* rather than requiring a wiki/Discord lookup. The real onboarding quest chain doesn't start until chapter 2 (`0.5) Getting Started`).

### Bonus: "0.5) Getting Started" — the actual first gameplay chapter

Since the FAQ chapter above has no rewards or dependency chain to speak of, here's the chapter that actually functions as a tutorial (45 quests, 2 roots, 39 single-dependency, 4 convergence, 25 of 45 optional, all 45 give item rewards): it opens on two parallel roots — "Copper Utilities" (leads into Copper armor/tools, the spyglass-zoom-key tip, and Storage Upgrades) and an unnamed Tinkers' Construct Part Builder quest (leads into Tinker Station → first Tinkers tool → the Encyclopedia). It converges seven side "Gather! 32/64 [crop]" quests into one "I'd Rather be Tractor!" reward (an actual drivable Automobility tractor, requiring only 2 of 7 completed), and gates the entire next chapter behind a single "Essential Materials — Chapter 1 Unlock" quest that needs Tin + Copper + Iron + Andesite + Clay in hand simultaneously.

## Files parsed

- `config/ftbquests/quests/data.snbt`, `chapter_groups.snbt`
- `config/ftbquests/quests/chapters/*.snbt` (13 files)
- `config/ftbquests/quests/reward_tables/*.snbt` (7 files)
- `kubejs/assets/createastral/lang/en_us.json` (2,661 quest-related translation keys)
- `kubejs/server_scripts/misc/interaction.js`
- `options.txt`
- `saves/New World/ftbquests/3b00d9d6-c758-4bc6-9f9f-e068a9eb490d.snbt` (read-only, for the pinned/HUD facts in §10)
