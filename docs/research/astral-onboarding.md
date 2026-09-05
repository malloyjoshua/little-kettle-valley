# Create: Astral — Onboarding & Notification Policy Inventory

Reference pack: `Create- Astral` (PrismLauncher instance, Fabric 1.18.2, read-only, never launched — inventoried from disk + a real play session log only).
Sources: `kubejs/server_scripts/misc/interaction.js`, `config/ftbquests/**`, `kubejs/assets/createastral/lang/en_us.json`, `mods/`, `options.txt`, `config/fancymenu/`, `config/drippyloadingscreen/`, and `logs/latest.log` (an actual join session by `DefNotJosh`, 2026-xx-xx 19:13–19:37).

## What actually happens on join (from `latest.log`)

Timestamps are wall-clock from one real session:

| Time | t+ | Event |
|---|---|---|
| 19:15:18 | 0:00 | `DefNotJosh joined the game` (world/quests finish loading) |
| 19:15:19 | 0:01 | **[CHAT]** `has made the advancement [Welcome to Create]` — vanilla-style advancement toast, top-right, from Create's own root advancement |
| 19:15:19 | 0:01 | **[CHAT]** `Please Read The Quest Book (Hover Over Me!)` — aqua, underlined, custom KubeJS message with a hover tooltip |
| 19:15:28 | 0:10 | **[CHAT]** `JourneyMap: Press [M]` — JourneyMap's own first-use hint |
| 19:22:53 | 7:35 | advancement `[Barrel Booty]` (Create) |
| 19:26:24 | 11:06 | `Respawn point set` + advancement `[Sweet Dreams]` (just past the 10-min mark — first bed) |
| 19:35:41 | 20:23 | goal `[Encyclopedia]` reached |
| 19:37:06 | 21:48 | advancement `[Stone Age]` |

**Message rate: 3 messages in the first 10 seconds, then silence for the next ~7.5 minutes, then 1 more before the 10-minute mark — 4 messages total in 10 minutes (~0.4/min), front-loaded almost entirely into the first 10 seconds.** Nothing repeats, nothing loops, nothing is timer-driven.

## The mechanism behind the one nag message (the part Josh liked)

`kubejs/server_scripts/misc/interaction.js`, `onEvent("player.logged_in", ...)`:

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

- On first login the player is silently given the quest book (gated by a persistent player "stage" flag, `starting_items`, so it's a one-time grant, not a repeat-every-join item drop).
- The reminder chat line only fires while the player's `read_quest` stage is unset.
- The moment the player right-clicks (opens) the book **once**, that stage is permanently set and the reminder never appears again — on this login or any future one.
- Net effect: at most one nudge, ever, per player, and it self-dismisses the instant you take the hinted action. It never becomes a recurring toast, never re-triggers on relog, and never nags someone who already engaged.

The message text itself lives in `kubejs/assets/minecraft/lang/en_us.json` under the vanilla `logging_tip` / `logging_tip.hover` keys:
- `logging_tip`: "Please Read The Quest Book (Hover Over Me!)"
- `logging_tip.hover`: "The Quest Book contains most of the information needed to progress in this modpack - it's your friend! Use the item to prevent this message from appearing."

The hover text itself tells the player how to make it go away — the pack explains its own notification policy inline, in the notification.

## FTB Quests configuration that shapes the whole experience

`config/ftbquests/quests/data.snbt`:
- `progression_mode: "linear"` — quests/chapters gate on prerequisites; you are not shown the whole tree at once.
- `pause_game: false` — opening the quest book (J key, `key_key.ftbquests.quests` in `options.txt`) never freezes the world.
- `disable_gui: false`, `default_autoclaim_rewards: "disabled"`, `grid_scale: 0.5`.

Chapter order (main list, `group: ""`, by `order_index`):
0. **Read the Questbook! (FAQ)** — always visible, 22 short Q&A-style entries (why Tinkers smeltery is disabled, where AE2 patterns went, common lag causes, etc.) — a reference tab, not a task list.
1. **0.5) Getting Started** (`assorted_goals`) — the real first task chapter. First quest titles/subtitles: "A Knight in Shining Copper — Cheap defense," craft Tinkers' Part Builder / Pattern, "combine tool parts... Give it a go!", "Fresh Furnace — A pioneer's first piece of industry..."
2. **1) The Andesite World** (`chapter_2`)
3. **2) Getting Industrial** (`chapter_3`)
4. **3) Remnants of a Lost Civilization** (`chapter_4`)
5. **4) Piglin Peculiarities** (`chapter_5`)
6. **5) Sub-Atomic** (`6_raow`)
7. **6) The End** (`6`)

A second tab, the **Side Quests** chapter group, holds `1.5) Astral Signals`, `3.5) Astral Storage`, `The Automation Matrix`, `Culinary Delights`, and `?) The Trophy Room` — optional/bonus content is structurally kept off the main line rather than interleaved into it, so the primary path a new player sees stays short and linear.

From the FAQ itself (`read_the_questbook.quests2`): "By default, the only chapters displayed in the quest book are those which have been unlocked... More chapters are unlocked when you complete the quests that are shaped like a gear at the end of every chapter." — so the book progressively reveals itself; a brand-new player never sees Chapter 6 content while still in Chapter 1.

## How it points to "next goal" without nagging

- The **quest book itself** (opened with `J`) is the single source of "what's next" — no HUD overlay, no repeating chat spam, no boss-bar timer.
- The one-time chat nudge above is the *only* push notification the pack sends; everything else is pull (the player opens the book when they want direction).
- Standard FTB Quests reward toasts exist under the hood (`ftbquests:display_completion_toast`, `display_reward_toast`, `display_item_reward_toast` — registered client packet handlers seen in the log at world join) but only fire on actual quest completion, i.e. only after the player does something.
- `RoughlyEnoughItems` (REI, not JEI) is integrated directly with FTB Quests (`FTBQuestsREIIntegration` plugin, confirmed in the log) — hovering a recipe in REI can show the quest that unlocks it, so item lookup and quest guidance are the same UI instead of two competing systems.
- `ponderjs` + `ponder_overrides` give animated in-world tutorials (Create-style "Ponder," right-click a block/item) for pack-specific multiblocks — `kubejs/client_scripts/ponder.js` registers a custom "Create: Astral" ponder tag over machines like the Electrolyzer, Shimmer Refinery, and Stone Growth Chamber. This is opt-in (you have to Ponder the item) — it never plays itself.

## Schematics as build guides (`[AstralExamples]` in `schematics/`)

Four `.nbt` structure schematics ship in `schematics/`:
- `[AstralExamples] Shimmer Refinery.nbt`
- `[AstralExamples] Electrolyzer.nbt`
- `[AstralExamples] Stone Growth Chamber.nbt`
- `[AstralExamples] Distillery.nbt`

These are complimentary example builds for the pack's custom multiblock machines, distributed as **quest rewards**, not as something you have to look up externally. Quote from `chapter_3.quests75.description0`: *"Complimentary schematic included with all purchases! You can also Ponder this block to see more info!"* — the same reward node hands the player both a placeable structure-block outline (spatial "build it like this" guide) and a pointer to the animated Ponder tutorial (mechanical "here's why it works" guide). `chapter_5.quests41.description4` confirms the same pattern for a Chapter 3 structure: *"Using the complementary schematic obtained as a reward from the previous quest, you can place an outline of a structure to use as a baseline when building it."* Schematics are handed out exactly when a player unlocks something complex enough to need one — not gathered as a pre-made "starter pack."

## Everything else that shapes the first minute

- **Mod stack for onboarding**: FTB Quests + FTB Library + FTB Teams + FTB Chunks (claims/quests), BetterAdvancements (reskins the vanilla advancement toast), RoughlyEnoughItems (REI — this pack uses REI, not JEI, not EMI), PonderJS + Ponder-Overrides (Create's animated tutorials, retargeted at pack machines), Jade + JadeAddons (hover-tooltip block/entity info, a WAILA successor), JourneyMap (minimap, sends its own one-time "Press [M]" chat hint), QuestsAdditions. No Patchouli, no dedicated "Toast Control" mod — toast behavior is entirely vanilla-advancement-toast + FTB Quests' own reward toasts, no third-party toast manager in the stack.
- **`options.txt`**: `tutorialStep:none` (vanilla's own "how to move/break blocks" hints are pre-disabled — the pack assumes basic Minecraft literacy and only teaches pack-specific things), `narrator:0`, `key_key.ftbquests.quests:key.keyboard.j` (J opens the quest book), `key_key.advancements:key.keyboard.l` (vanilla L still opens the vanilla advancement screen separately).
- **Before the player even joins a world**: FancyMenu (`config/fancymenu/`) fully re-skins the title screen, disconnect screen, and pack-selection screen with custom hover animations (`singleplayerhover.gif`, `multiplayerhover.gif`, `notification.gif`, a `create_astral.png` logo) and a looping theme (`npc_theme.ogg`); DrippyLoadingScreen (`config/drippyloadingscreen/customization/createastral.dllayout`) replaces the vanilla loading screen. Onboarding starts at the main menu, not at spawn.
- `addServer.enterIp` / `multiplayer.title` are reflavored to "Discover whole new Astral Realms." — even boilerplate vanilla UI strings are reworded to match the pack's ancient-civilization theme (also visible in the FAQ chapter's Standard Galactic Alphabet decoration and "ancient schematic from a lost civilization" tooltips on blueprint items).

## 12 facts

1. On join, the player gets exactly 3 messages in the first 10 seconds: a "Welcome to Create" advancement toast, a custom chat nudge toward the quest book, and JourneyMap's own "Press [M]" hint — then nothing for roughly 7.5 minutes.
2. In a real 10-minute play session captured in `logs/latest.log`, only 4 total messages/toasts fired — about 0.4 per minute, almost entirely front-loaded into the first 10 seconds.
3. The quest-book reminder is sent by `kubejs/server_scripts/misc/interaction.js` on `player.logged_in`, gated by a player "stage" flag (`read_quest`) that gets permanently set the instant the player right-clicks the book — the nag can fire at most once per player, ever.
4. The same login handler also grants the FTB Quests book itself, gated by a separate one-time stage flag (`starting_items`), so it's given once and never re-granted on relog.
5. The reminder text's own hover tooltip tells the player how to dismiss it ("Use the item to prevent this message from appearing") — the pack explains its notification policy inside the notification.
6. FTB Quests runs in `progression_mode: "linear"` with `pause_game: false` — quests unlock progressively and the book never freezes the world when opened (bound to the `J` key).
7. The main chapter line is exactly 8 chapters long (FAQ, 0.5, 1–6) in `order_index` order; bonus/optional content (Astral Signals, Astral Storage, Automation Matrix, Culinary Delights, Trophy Room) is segregated into a separate "Side Quests" chapter group so it never clutters the primary path.
8. Chapter 0 is explicitly an FAQ/reference tab ("Read the Questbook! (FAQ)", 22 entries covering things like why the Tinkers' Smeltery is disabled or common server-lag causes) — the real first task chapter is "0.5) Getting Started."
9. The FAQ itself documents the reveal mechanic: later chapters stay hidden until a player completes the gear-shaped "unlock" quest at the end of the current chapter.
10. Four `[AstralExamples]` `.nbt` schematics (Shimmer Refinery, Electrolyzer, Stone Growth Chamber, Distillery) are handed out as quest rewards exactly when a player unlocks the matching multiblock — paired in the same quest text with a pointer to that block's animated Ponder tutorial, giving a spatial guide and a mechanical guide together instead of a separate lookup step.
11. There is no dedicated toast-suppression/"Toast Control" mod in the pack — all toast behavior comes from vanilla's own advancement-toast system (reskinned cosmetically by BetterAdvancements) plus FTB Quests' native completion/reward toast packets, which only fire on player action.
12. Onboarding starts before spawn: FancyMenu fully re-skins the title/loading/disconnect screens with pack-themed hover art and music, and vanilla's own tutorial hints are pre-disabled (`tutorialStep:none` in `options.txt`) so the in-game teaching budget is spent entirely on pack-specific mechanics, not "how to break a block."

Written: 2026-09-04.
