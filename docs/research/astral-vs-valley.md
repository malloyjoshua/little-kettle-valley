# Create: Astral vs Little Kettle Valley — what makes goals feel easy, and what we adopt

Josh, on the reference pack: *"I really liked how easy Create: Astral walked you through the goals. Very useful and not super annoying."*

This file answers two questions with numbers first: **what is Astral actually doing**, and **which of it applies to us**. Sources: `docs/research/astral-questbook.md`, `docs/research/astral-onboarding.md` (both full-disk inventories of the read-only PrismLauncher instance), and a fresh parse of our own `story/quests/*.json`, `tools/scripts/compile_quests.py`, `pack/config/ftbquests/quests/data.snbt`, `pack/kubejs/server_scripts/valley_core.js`, `docs/JOURNEY.md`, `docs/writing-craft.md`, plus the field names actually present in our shipped `ftb-quests-forge-2001.4.22.jar` and `create-1.20.1-6.0.8.jar`.

Nothing in the pack was edited. Stage 2 applies this.

---

## 1. Side by side

| | Create: Astral | Little Kettle Valley | Note |
|---|---:|---:|---|
| Quests | 851 | **126** | Ours is 15% the size — a different job, not a smaller version of the same job |
| Chapters | 13 (8 main + 5 side) | **6** (5 acts + Oda's Counter) | |
| Chapter groups (tabs) | 2 — main line + "Side Quests" | **1** — "Story", everything in it | Oda's 23 repeatables sit in the same tab as the story |
| Largest / smallest chapter | 176 / 13 | **23 / 18** | Ours are all one size; no "quick tab" and no "big optional tab" |
| Quests visible when you open the book | Whole unlocked chapter, locked ones greyed with a lock icon (only 35 of 851, 4%, hide themselves) | **One.** 125 of 126 emit `hide_until_deps_complete: true`, and all 126 emit `hide_details_until_startable: true` | The single biggest legibility gap. Astral shows you the road; we show you one dot |
| Chapters visible at the start | Chapter 0 (FAQ) + Chapter 0.5, later ones hidden until a gear-shaped unlock quest | 1 (Act I); acts II–V hidden by cross-chapter deps | Same shape — we already do the good thing here |
| A "start here" tab | Yes — Chapter 0 "Read the Questbook!", 23 no-stakes FAQ entries, no deps, no rewards | **No** | |
| Description length | 244 chars / 3.9 lines avg; 72% of quests have one | **376 chars / 4.87 lines avg; 100% have one** | Ours are 54% longer, on every single quest |
| Quests with an explicit title | 55% (rest inherit the task item's name) | **100%** | |
| Deps per quest | 82% have exactly 1; 15% have 2+; 3% have none | **65% have 1; 34% have 2+; 1 root** | Ours braids harder — deliberate (cozy lane feeds tech lane) |
| Dead-end quests (nothing depends on them) | 42% | **27%** | Ours is tighter; less to wander off into |
| `optional: true` | 76 quests (8.9%), 25 of them inside the tutorial chapter | **0 of 126** | Nothing in our book is marked skippable, so everything reads as mandatory |
| Repeatable quests | 0 | **21** (Oda's Counter) | Ours has an anti-grind valve Astral doesn't |
| Quest icons | 34% explicit, 66% inherit the task item | **100% explicit** — but 41 of the 91 item-task quests use a *tool* icon, not the item asked for | |
| Chapter canvas images | 72 across 11 chapters (solar-system map, glyph words, pack logo) | **0** | |
| Rewards per quest | 0.67 (571 objects / 851) | **6.7** (850 / 126) — 4.0 of them item stacks; 41 quests hand over 5+ stacks | 10x Astral's per-quest reward volume |
| Reward claim policy | `default_autoclaim_rewards: "disabled"` pack-wide, zero overrides; loot rewards additionally `exclude_from_claim_all` | **`auto: "enabled"` on all 850**, written unconditionally by the compiler | Ours is right for a cozy player — it fixed the lost Homestead Waystone — but it means every stack fires its own toast |
| Toasts on finishing quest 1 | 1 (the quest-complete toast; rewards wait to be clicked) | **~11** — 10 auto-claimed rewards + an advancement grant, all at once | |
| Messages in the first 10 seconds | 3 (Create advancement, one chat nudge, JourneyMap's "Press [M]") | **5** — title card, three chat lines, a second title card at 4.5s — plus a persistent actionbar line | |
| Messages in the first 10 minutes | 4 total (~0.4/min), then silence for 7.5 min | Above, plus ~11 toasts the moment Q1 ticks | |
| Repeating nags | None. One login nudge, gated by a stage, permanently killed the first time the book is right-clicked | None repeating — our actionbar prints once per *state change*, not on a timer (already fixed) | We match Astral here |
| "Next goal" mechanism | The book, opened on `J`. Nothing pushes | The book, **plus** a `Next:` toast on 105 of 126 quests, **plus** a 3-state actionbar for the first two quests | Ours pushes more, which is good for her — but the toast is competing with 6 reward toasts fired in the same tick |
| `pause_game` | false | *(not set — FTB default false)* | Same effect |
| `progression_mode` | `linear` | `flexible` | Astral's linear does the job our hide-flags do; with a visible board, flexible is the friendlier of the two |
| Build guides | 4 `[AstralExamples] *.nbt` Create schematics, handed out **as the reward of the quest that unlocks the machine**, paired in the same text with "you can also Ponder this block" | **None.** 8 Patchouli field notes exist (`f1`–`f8`) but no quest links to one, and `guide_page` is used 0 times | The one Astral mechanism we have zero of |
| Book delivery | KubeJS `player.logged_in`, one-time `starting_items` stage | KubeJS `PlayerEvents.loggedIn`, one-time `first_join` stage | Identical pattern, arrived at independently |

---

## 2. What Astral is actually doing (mechanisms, not adjectives)

Each of these is a mechanism you can point at in a file. The adjective "easy" is the output; these are the inputs.

**1. The whole chapter is on screen, and locked quests are still drawn.** Only 4% of Astral's quests hide themselves. Opening a chapter shows a connected map of circles running left to right, with the finished ones filled, the current one lit, and everything after it greyed under a lock icon. You can *see* that the chapter is fourteen steps long and that step nine involves a furnace. Legibility comes from the map, not from the text.

**2. One chapter at a time, in a numbered line.** The main tab is exactly 8 chapters, titled `0.5)`, `1)`, `2)` … `6)`. Later chapters are hidden until you clear the gear-shaped unlock quest at the end of the current one — and the FAQ tab tells you that this is how it works, in writing, before you wonder. You are never looking at a book of 851 quests; you are looking at 45.

**3. A "read me first" tab that isn't a task list.** Chapter 0 is 23 FAQ entries — no dependencies, no rewards, no gating, mostly checkmark tasks. Why the Smeltery is off. What Project Tables are for. *"First time using a quest book? Close this quest and hover your mouse to the left of the screen to open the chapter browser :)"*. The troubleshooting lives inside the book instead of on a wiki, and the last entry teaches the book's own UI.

**4. Optional content is flagged and structurally separated.** 76 quests carry `optional: true` — 25 of them inside the tutorial chapter, i.e. more than half of "Getting Started" is explicitly skippable. Everything genuinely off-line (Automation Matrix, Culinary Delights, Trophy Room) lives in a second tab called "Side Quests", so the main line stays short.

**5. The icon is the item.** Two thirds of quests don't set an icon at all — FTB Quests falls back to the first task's item, and 45% don't set a title either, so the quest is literally named and pictured as the thing you have to hold. The board reads like a shopping list.

**6. Short descriptions with the object named.** 244 characters, 3.9 lines. 28% of quests have no description at all — the title *is* the instruction. Long prose is rationed to the few quests that genuinely need a tutorial (the one 1,476-character monster is an AE2 Spatial Storage explainer).

**7. Convergence nodes make progress feel earned without gating hard.** 82% single-parent chain, then a capstone that wants 2–12 prior quests — 22 of which set `min_required_dependencies` and 19 set `dependency_requirement: one_completed`, so a node can fire from *any one* of several branches. You collect several loose threads into one visible payoff, and you're never blocked because you skipped a branch.

**8. Pictures on the canvas.** 72 decorative images across 11 chapters — the Trophy Room is laid out as a literal solar-system map, six chapters spell words in enchanting-table glyphs across the background. The board is a place, not a spreadsheet.

**9. Rewards are the next ingredient, and a schematic when the build is hard.** Four `.nbt` Create schematics ship in the instance's `schematics/` folder and are handed over as the reward of the quest that unlocks the matching multiblock: *"Complimentary schematic included with all purchases! You can also Ponder this block to see more info!"* A spatial guide (place the outline, fill it in) and a mechanical guide (the animated Ponder) delivered in the same breath, at the exact moment they're needed.

**10. Nothing auto-claims, so nothing pops.** `default_autoclaim_rewards: "disabled"` pack-wide with zero overrides, and every loot reward also carries `exclude_from_claim_all`. Quiet by construction — a completed quest produces one toast, not eight.

**11. Exactly one push notification exists, and it kills itself.** One chat line on login, gated by a `read_quest` player stage that is set permanently the first time the book is right-clicked. Its own hover tooltip explains how to make it stop. 4 messages in 10 minutes of real play.

**12. Onboarding starts before spawn, and vanilla's tutorial is switched off.** FancyMenu re-skins the title screen; `tutorialStep:none` in `options.txt` kills vanilla's "how to break a block" hints so the whole teaching budget is spent on pack-specific things.

---

## 3. Adoption list for Little Kettle Valley

Ranked by impact **on Josh's wife** — a player who wants to know what to do next, wants to see where this is going, and does not want to be shouted at. Each item names the file it lands in. Every FTB Quests field named below was verified present in our shipped `ftb-quests-forge-2001.4.22.jar` (`Quest.class` / `Chapter.class` / `BaseQuestFile.class` string tables), not assumed from a wiki.

### A1 — Draw the road ahead. Stop hiding every quest.
**Impact: highest.** Right now she opens the book to a board with one dot on it. She cannot see that Act I is twenty steps, that a chicken pen is coming, or that the thing she's doing leads anywhere. Astral's "this feels easy" is 90% this.

* `tools/scripts/compile_quests.py` — flip two defaults:
  * `hide_until_deps_complete` from `True` to `False` (line: `if qq.get('hide_until_deps_complete', True) and deps`). Keep it as an opt-in per quest for the handful of genuine surprises (the cellar door reveal, the Act IV coolant beat).
  * `hide_details_until_startable` from `True` to `False`. A locked quest should show its title and its subtitle — that's the preview. Keep it opt-in for spoiler quests, and add `hide_text_until_complete` (verified present) as the finer tool for hiding *only* a description while the icon and title stay readable.
* Keep `progression_mode: "flexible"` in `pack/config/ftbquests/quests/data.snbt`. Astral uses `linear`, but its job there is exactly what our hide-flags were doing; with a visible board, flexible is the more forgiving of the two and it protects our braided deps (34% of our quests have 2+ parents).
* Add chapter-level `default_min_width` and `default_quest_size` to the chapter emitter while you're in there — both verified, both cheap.
* **Check after:** open the book on a fresh world; Act I should read as a connected map with q01 lit, q02–q19 greyed and titled.

### A2 — Kill the toast avalanche.
**Impact: very high.** Finishing quest 1 currently fires about eleven toasts in one tick: ten auto-claimed rewards plus an advancement. The one toast that matters — our `Next:` line, which is the best thing in our book — is buried in the middle of it.

* `tools/scripts/compile_quests.py`, `reward_snbt()` — the autoclaim value is hard-written as `enabled`. FTB Quests 2001.4.22 supports `default`, `disabled`, `enabled`, **`no_toast`**, `invisible` (verified in `RewardAutoClaim.class`). Default item/xp/loot rewards to `no_toast`, and leave `enabled` on exactly one reward per quest — the `toast` reward that says what's next. Auto-claim behaviour is unchanged (nothing is lost, the Waystone bug stays fixed); only the popup volume drops from ~7 to 1.
* `story/quests/*.json` — no edits needed if the compiler default changes; per-reward `"autoclaim": "enabled"` stays available for the two or three hero items (Josie's Lantern, the Copper Kettle trophy) that deserve their own pop.
* **Check after:** complete q01 on a test world and count toasts. Target: 2 (quest complete + `Next:`).

### A3 — Split Act I into a "Start Here" chapter of eight tiny quests.
**Impact: very high.** Act I is currently 20 quests and about two hours behind one tab. Astral's first hour is its own chapter, and its FAQ tab is another. Our first eight quests are already 1–6 minutes each and end on the first person arriving — they just need to be their own tab so the first thing she sees is a short, obviously finishable list.

* New file `story/quests/start.json` — chapter key `start`, title **"Start Here"**, order 0, subtitle *"Spring, Year One."*, icon `valley:letter`. Move q01–q08 into it verbatim:
  q01 read the letter · q02 waystone on the hearthstone · q03 door/windows/bed/sconce · q04 megatorch · q05 cellar stairs · q06 vegetable soup · q07 surveyor's stake · q08 sleep one night (→ Marnie arrives).
* `story/quests/act1.json` — chapter becomes q09–q19 (11 quests), `order: 2`, keeps the title "Act I: The Thaw"; q09 and q12 and q15 keep their existing deps on q08 as cross-chapter deps, which the compiler already supports (act2–act5 all do this today).
* Renumber `order` on act1–act5 and oda (+2 for the two new chapters ahead of them).
* **Quest ids do not change** — `hid()` hashes the quest *key*, not the file — so nothing about moving them breaks live progress or the KubeJS `_quest_ids.js` map. Only the two new chapter ids are new.
* **Check after:** `tools/scripts/compile_quests.py` runs clean, and `pack/kubejs/server_scripts/_quest_ids.js` diff shows only added chapter entries, zero changed quest ids.

### A4 — Add the "Read Me First" chapter (our version of Astral's Chapter 0).
**Impact: high**, and it's the cheapest thing on this list — it's writing, not code.

* New file `story/quests/readme.json` — chapter key `readme`, title **"Read Me First"**, order 0 (ahead of Start Here), icon `minecraft:book`. 8–12 checkmark quests, no deps, no rewards, exactly like Astral's: how the book works and where the chapter list is; the pack never has a timer, a fail state or a death penalty; what the `Next:` toast is; Oda's Counter is the shortcut when a machine part is annoying; you cannot break the story by doing things out of order; where the journal is and what the compass points at; who the eight residents are; "the tech lane and the cozy lane both count as playing."
* Every quest here is a `checkmark` with a friendly task label (`"Understood."`), zero rewards — matching Astral's no-stakes reference tab exactly.
* Written to `docs/writing-craft.md` §1's **narrator** voice (no personality, no opinions), not Josie's.

### A5 — Cut the first-minute message count to Astral's shape.
**Impact: high.** We fire five messages in the first five seconds before she has done anything; Astral fires three in ten. Our actionbar-per-state-change is already right and stays.

* `pack/kubejs/server_scripts/valley_core.js`, `valleyFirstJoin()`:
  * Keep the title card. Drop to **two** chat lines (letter + destination-with-coordinates); the third — "Right-click the Quest Book (or press J)" — moves to the login-nudge below so it can repeat *only* if she never opens the book.
  * Keep `tellWhere()`'s second title card but push it later or fold it into the actionbar; two title cards 4.5s apart is one too many.
* Add Astral's self-dismissing nudge to `PlayerEvents.loggedIn`: if the player lacks a `read_quest` stage, send **one** aqua line — *"Your Quest Book is in your bag. Right-click it, or press J."* — with a hover that says how to stop it. `pack/kubejs/server_scripts/valley_checks.js` already ticks q01 off the letter right-click, so hook the same event to `player.stages.add('read_quest')` on `ftbquests:book`.
* `pack/options.txt` — set `tutorialStep:none` (Astral does; vanilla's "how to move" hints are noise on top of ours) and confirm the quest-book keybind is a key we name in text (Astral uses `J`; our chat already says J).
* **Check after:** count push messages in a fresh join. Target: title card + 2 chat + 1 actionbar in the first 10 seconds, then nothing until she acts.

### A6 — Mark the optional quests optional.
**Impact: high**, near-zero cost. Zero of our 126 quests are flagged, so a cozy player reads the fishing quest and the grape quest as homework. Astral flags 9% of its book, and more than half of its tutorial chapter.

* `story/quests/*.json` — set `"optional": true` on the side-branch cozy quests (the ones `docs/JOURNEY.md` describes as flavour rather than spine) and on all 21 of Oda's repeatables. The compiler already emits `optional` — no code change.
* `story/quests/oda.json` — additionally move Oda's Counter into its own chapter group: `"group": "Side Quests"` on the chapter object. The compiler already builds groups from that field; today everything says `"Story"`, so 23 repeatable bounties sit in the same tab as the story acts. This is Astral's structural separation, one string.

### A7 — Build guides for the reactor, the turbine and the greenhouse.
**Impact: high for the tech lane** (Josh, or her on a tech night) — this is the one Astral mechanism we have literally none of. The pack asks for a Bigger Reactors vessel, a turbine held at 1,800 RPM and a heated greenhouse, and hands over parts with no picture of the finished thing.

* **Do it with Patchouli, not Create schematics.** We already ship `patchouli:valley_journal` with eight field notes (`f6_the_vessel`, `f7_the_turbine`, `f8_quarry_and_markers`) that currently use only `patchouli:text` and `patchouli:crafting` pages. Add `patchouli:multiblock` pages: they render a rotating 3D preview in the book *and* project a ghost outline into the world, and they need nothing but book JSON. Files: `pack/patchouli_books/valley_journal/en_us/entries/field_notes/f6_the_vessel.json`, `f7_the_turbine.json`, and a new `f9_the_greenhouse.json`.
* **Pair it the way Astral does** — the guide arrives *as the reward of the quest that unlocks the machine*, not as a thing to go and look up. Add to those quests a reward that opens/points at the entry, and a description line naming it. `guide_page` exists as a compiler field and as a `Quest` field in our jar, but its behaviour in 2001.4.22 is unverified — **verify it opens the Patchouli entry before relying on it**; the fallback is a `command` reward (`/patchouli open`) plus the entry named in the text.
* **Create schematics are the optional extra, and they have a catch.** Create 6.0.8 ships the full pipeline (`SchematicItem` with `File`/`Anchor`/`Bounds`/`Deployed`, `ServerSchematicLoader`, the Schematic Table upload). Astral's convention is a literal filename prefix — `[AstralExamples] Shimmer Refinery.nbt` in the instance's `schematics/` folder — so ours would be `[Valley] Reactor Vessel.nbt`, `[Valley] Turbine 5x5x4.nbt`, `[Valley] Greenhouse.nbt`. The catch: the `.nbt` must be in the **client's** `schematics/` folder, and on a server it must additionally be uploaded through a Schematic Table before a Schematicannon can print it. Since she plays on Josh's server, ship them only if the installer can drop files into the client instance folder, and never make a quest depend on one.

### A8 — Put a picture on the board.
**Impact: medium-high.** Astral's chapters are places (a solar-system map, glyph words). Ours are grids. `ChapterImage` is verified present in our jar with fields `x, y, width, height, rotation, image, hover, click, color, alpha, corner, dev, order`.

* `tools/scripts/compile_quests.py` — emit a chapter-level `images: [ ... ]` list from an `"images"` array on the chapter JSON object. About fifteen lines next to the existing `subtitle` emitter.
* `docs/QUEST_FORMAT.md` — document the new chapter field.
* First uses, in order of payoff: `media/town_map.png` faint behind the act boards (she can see the valley she's building); the pack logo on **Start Here**; a lamp-post texture repeated along the bottom of each act board as a progress frieze (2 → 6 → 10 → 22 → 39 → 40, the pack's own spine). Textures must be shipped under `pack/kubejs/assets/valley/textures/` to be addressable.

### A9 — Make the icon the thing she has to get.
**Impact: medium**, near-zero cost. 41 of our 91 item-task quests use a tool icon instead of the item the task asks for (q14 shows a Millstone but wants 16 flour; q19 shows bread but wants flour first). Astral leans the other way — two thirds of its quests inherit the task item — and the board reads like a shopping list because of it.

* `story/quests/*.json` — set `icon` to the first task's item wherever the quest is "go and get N of X". Keep the tool icon only where the quest genuinely is "use this machine" (q06's kettle, q18's oven).

### A10 — Rubric: a two-line description for tech quests, five lines for story quests.
**Impact: medium.** Our descriptions average 376 characters on every one of 126 quests. Astral averages 244 and skips them entirely 28% of the time. The five-line format is *right* for a story beat — Josie's line, the instruction, the render — and heavy on "craft 8 andesite alloy."

* `docs/writing-craft.md` §4 — split the **Quest description** row into two:
  * **Story quest** (any quest that moves a person, opens a place, or lands a promise from §5): unchanged 5-line format, cap unchanged. This is the pack's voice and it does not get trimmed.
  * **Tech quest** (a craft/gather/build step with no story beat, ~38 quests by icon and task item): **2 lines, ≤ 180 characters total.** Line 1 is the instruction — verb first, every item named. Line 2 is what she'll see. No character line, no blank-line padding. If a resident has something to say about a machine, it belongs in the `Next:` toast of the quest before it, or in the journal, not in a shopping list.
  * Add a note under the table: *a quest whose title already is the instruction may ship with no description at all* — Astral's most common shape and the fastest thing in its book to read.
* §2 scoring card is unaffected: a two-line tech description still has to pass Picture, Shape and Fit.

### A11 — `min_width` on the long ones.
**Impact: low-medium**, five minutes of work. Astral uses it on 7 quests (six forced to 300px). Our longest descriptions are 605 characters in a default-width tooltip.

* `tools/scripts/compile_quests.py` — emit `min_width` from a quest field (verified present in `Quest.class`), alongside the existing `size`/`shape` emitters. Also worth exposing while you're there: `icon_scale` and `hide_lock_icon`.
* Apply to the ~10 quests over 500 characters, and to `oda_open` (563 chars, the board everyone reads first).

### A12 — Convergence nodes, sparingly.
**Impact: low** — we already have the shape (34% of our quests have 2+ parents vs Astral's 15%), and our compiler already supports `min_required_deps` and `dependency_requirement`. Neither is used anywhere in the book today.

* `story/quests/*.json` — on the act finales (q19, q37, q56, q75, q90), consider `min_required_deps` so a finale fires when *most* of its act is done rather than all of it. This is the "never blocked because you skipped a branch" property, and it's the safety net that makes A6's optional flags honest.

---

## 4. What NOT to copy

**Astral is a tech pack with no story. Most of its book is a checklist; ours is a novel with chores in it.** Specifically:

* **Do not copy the reward policy.** Astral's `default_autoclaim_rewards: "disabled"` is right for a player who is *shopping* through 851 quests and wants to choose when to take a crate. It cost us the Homestead Waystone on Josh's first play (Q1 ticked, nothing arrived, Q2 asked for a block she didn't have). A2 changes the *toast*, never the auto-claim.
* **Do not copy the quest volume or the fan-out.** One hub with 55 children works for an automation checklist. Our spine is a five-act story; 42% dead-end leaves would read as an unfinished map.
* **Do not copy the FAQ chapter's content.** Astral's Chapter 0 is troubleshooting for a pack that fights you (why the Smeltery is disabled, common lag causes, chunk-saving bugs). Ours (A4) is reassurance for a player who is worried she'll do it wrong — different job, same structural slot.
* **Do not drop titles or descriptions to hit Astral's averages.** 45% of Astral's quests have no title because the item name is enough; our titles are imperatives that carry the voice (`Put the Waystone on the Hearthstone`) and `docs/writing-craft.md` §4 protects the subtitle on all 126 as "the last thing allowed to die." A10 shortens *tech* prose only.
* **Do not adopt `progression_mode: "linear"`.** It's doing Astral's hiding for it. With A1's visible board, linear would only add refusals.
* **Do not adopt the obfuscated/glitch chapter titles, the hidden `invisible` lore quests, or the Standard Galactic Alphabet decoration.** They're a sci-fi pack's signature. Ours is a valley; A8's images should be the town map and the lamps.
* **Do not build a HUD tracker.** Astral has none (its live save shows `auto_pin: false`), and our `Next:` toast plus the first-two-quest actionbar already does the job with less screen furniture. Note that FTB Quests 2001.4.22 does carry a pinned-quest HUD (`pinned_quests_pos` in `FTBQuestsClientConfig`) if we ever want it — it is a client setting, so it cannot be shipped server-side and should not be depended on.
* **Do not copy the pre-spawn work yet.** FancyMenu title-screen re-skinning is real polish, but it's a separate mod and a separate job from the quest book.

---

## 5. Order of work for stage 2

1. **A1 + A2 together** (both in `compile_quests.py`) — recompile, open the book, count toasts. These two alone are most of what Josh liked about Astral.
2. **A3 + A4** (`story/quests/start.json`, `readme.json`, renumber orders) — the first ten minutes stop being a wall.
3. **A5 + A6** (`valley_core.js`, `optional` flags, Oda into "Side Quests").
4. **A9 + A10 + A11** (icons, rubric split, `min_width`) — a text-and-data pass, no risk.
5. **A7 + A8** (Patchouli multiblock pages, chapter images) — the two that need new assets.
6. **A12** last, as a tuning pass once the board is visible enough to see what it does.

Written 2026-09-04. No pack files were edited by this pass.
