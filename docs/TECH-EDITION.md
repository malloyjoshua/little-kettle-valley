# Kettle Tech: the no-story edition

Kettle Tech is Little Kettle Valley with the story taken out and a quest book put in its place. Same 128 mods, same configs, same world generation — but nothing writes to your world, nobody moves in, no recipe is locked behind a letter you haven't been handed yet. You load a fresh world and it is just Minecraft with Create, Thermal, AE2, Bigger Reactors and QuarryPlus in it, plus a book that tells you what to build next.

It exists because the story pack is a story: it wants you to meet people, run errands and unlock the valley in order. That is the wrong shape for an evening when you want to get a water wheel spinning before bed.

**Pack directory:** `pack-tech/` · **Quest sources:** `story-tech/quests/` · **Book:** 9 chapters, 90 quests

---

## How to launch it

The Prism instance already exists: **Kettle Tech**, at

```
~/Library/Application Support/PrismLauncher/instances/KettleTech
```

Open Prism, pick **Kettle Tech**, press Play. Its pre-launch command pulls the pack fresh from GitHub every time, so it self-updates:

```
"$INST_JAVA" -jar packwiz-installer-bootstrap.jar -g -s client \
  "https://raw.githubusercontent.com/malloyjoshua/little-kettle-valley/main/pack-tech/pack.toml"
```

It is a separate instance from **Little Kettle Valley** (the story pack) with its own saves, its own config and its own memory setting — 3584 MB, same as the story instance. Playing one does not touch the other.

To hand it to someone else, point them at the same `pack-tech/pack.toml` URL in a fresh Prism instance on Forge 1.20.1 / 47.4.10.

---

## The first hour

You spawn with nothing but a Quest Book in your inventory and one line of chat telling you it is there. Press **J** to open it.

**Read Me First** is six tiles, no tasks, no rewards — how the book works, that nothing is hidden, that the Side Quests tab is optional, the two keys worth knowing, and how to look a machine up in JEI. Two minutes. Then:

**Start Here** — eight short jobs, roughly an hour.

1. **Craft the Wide Hammer.** Copper and sticks, not diamonds — this pack makes it cheap on purpose. It breaks a 3x3 face in one swing, which is why every tunnel, cellar and reactor pit later in the pack goes four times faster.
2. **Craft a backpack**, twenty-seven slots that follow you.
3. **Sleep a night**, **bake eight bread**.
4. **Place a waystone** (stone bricks and copper — also made cheap here) so home is on your map forever.
5. **Raise a megatorch** (copper and a copper block, instead of the vanilla two diamonds and two gold blocks). Nothing spawns for 64 blocks around it.
6. **Put up a chest or a drawer**, and the book hands you drawers and eight andesite alloy — which is the first ingredient of the next chapter.

That last move is the pattern the whole book follows: **the reward is the next step's ingredient.** You are never sent away to go farm something before you can continue.

After that the board is open. **Create** is the natural next chapter — andesite alloy to a water wheel to brass to a train track, fourteen quests. **Thermal** and **Applied Energistics** run beside it. **The Reactor** and **The Quarry** are the deep end. **Cozy** and **Explore** sit in a separate **Side Quests** tab and block nothing.

Two things worth knowing at the keyboard: **J** opens the book, and holding the **grave key** (the one above Tab) while breaking an ore or a log takes up to 64 blocks of that vein at once, with no enchantment needed. Both are rebindable under Options → Controls.

---

## How it differs from the story pack

### Nothing runs in your world

Every script that built, placed, moved or gave anything is gone. The story pack's login handler did five things — auto-party, a first-join letter and deed and kettle, an objective polling loop, a bossbar, a self-dismissing nudge. Kettle Tech's does one: hand you the book, say one line, never speak again.

Deleted wholesale: `valley_core.js`, `valley_checks.js`, `valley_finales.js`, `valley_greetings.js`, `valley_keepsakes.js`, `valley_gates.js`, `town_plan.js`, `_quest_ids.js`, `valley_items.js` (the 48 `valley:` items), `valley_lore.js`, the `valley` data and asset trees, and the Patchouli journal. There is no structure placement, no teleport, no `/setblock`, no `/fill`, no template pasting anywhere in `pack-tech/kubejs`.

Kept: `unify.js` (ore unification — it is also the only source of `biggerreactors:uranium_ingot` from Geolosys uranium clusters, which the Reactor chapter needs), `seasons_tags.js`, `valley_blocks.js` (its one remaining job is making herbal tea kettles hand-breakable), `hide.js`, and the non-story data fixes — Bountiful pools, the Vinery and Farm & Charm loot-table fixes, forge tags, loot modifiers.

### The anti-grind recipes stayed; every gate went

`tech_recipes.js` keeps the five recipes from `valley_gates.js` that made things *cheaper*, and drops all seven that made things *harder*:

| Recipe | What it does |
|---|---|
| `bountiful:bountyboard` | copper ingot instead of a diamond (vanilla recipe removed) |
| `torchmaster:megatorch` | copper + copper block instead of 2 diamonds + 2 gold blocks (vanilla removed) |
| `waystones:waystone` | stone bricks + copper — **added**, the mod's own recipe still works |
| `justhammers:stone_hammer` | a copper variant — **added**, the mod's own recipe still works |
| `minecraft:bell` | cast from copper. Vanilla ships no bell recipe at all, so this adds a source |

Everything that was gated is back to exactly what its mod ships: Create's Water Wheel, Thermal's Machine Frame, the Cooking for Blockheads Fridge / Sink / Milk Jar, AE2's Charger and Growth Accelerator, Bigger Reactors' Casing and Terminal, QuarryPlus's Quarry, AE2's Vibrant Quartz Glass. **Nothing in Kettle Tech is harder than the mods as shipped.**

One behaviour change rather than a removal: the story pack narrowed `sereneseasons:greenhouse_glass` so only reactor-gated glass grew out-of-season crops. Kettle Tech drops that narrowing, so the tag sits at Serene Seasons' permissive default — **any glass roof** grows out-of-season crops from day one.

### The book is built the Astral way

The story pack's book unfolds as you earn it. This one is open from the first minute, following the adoption list in `docs/research/astral-vs-valley.md`:

- **Nothing hides.** All 90 quests write `hide_details_until_startable: false` explicitly, all 76 quests that have a dependency write `hide_until_deps_complete: false` (the other 14 have no dependency to hide behind), and both chapter-level equivalents are false on all 9 chapters. A quest you cannot start yet is drawn greyed with its title and subtitle readable, so you can plan.
- **One toast per quest.** All 244 item rewards auto-claim silently (`no_toast`); only each chapter's final quest fires a visible "Next:" toast. Six toasts across the whole book.
- **Progression is `flexible`,** and there is no lock message.
- **Every title is an instruction** — "Stand a Water Wheel in Running Water", not "The Water Wheel".
- **The icon is the deliverable** on all 90 quests.
- **Optional means optional.** Cozy and Explore are flagged optional *and* moved into their own **Side Quests** chapter group, so the main tab is only the machine line.

Multiblock quests name exact block counts, read out of Bigger Reactors' own validation strings rather than guessed: a 3x3x3 reactor is 22 plain casing + terminal + access port + power tap + control rod, with one fuel rod inside; a 5x5x4 turbine is 76 casing + 2 rotor bearings + terminal + 2 fluid ports + 1 power tap, with 2 shafts, 4 blades and 4 copper blocks inside.

### Quiet by default

`options.txt` carries `tutorialStep:none`, `hideBundleTutorial:true` and `joinedFirstServer:true`. Toast Control is configured to suppress advancement, recipe, system and tutorial toasts while **leaving FTB Quests toasts on**, so the book can still talk. Simple Voice Chat ships `onboarding_finished=true` so it does not open its setup panel on first join.

---

## How to update it

The mod list and configs are **shared with the story pack** — `pack-tech` is a fork of `pack`, not an independent pack. When the story pack's mods or configs change, re-mirror them:

```bash
cd "~/Desktop/1. Projects/Minecraft"
rsync -a --delete pack/mods/ pack-tech/mods/
rsync -a pack/config/ pack-tech/config/ \
  --exclude 'ftbquests/quests' --exclude 'toastcontrol-client.toml'
cp pack/options.txt pack-tech/options.txt
(cd pack-tech && ../tools/packwiz refresh)
```

Mind the two excludes — `config/ftbquests/quests` is Kettle Tech's own book, and `toastcontrol-client.toml` differs on purpose (Kettle Tech suppresses advancement toasts; the story pack keeps them, because its advancements are how the story speaks). `pack-tech/config/voicechat/voicechat-client.properties` is Kettle Tech-only and has no counterpart to overwrite.

To change the quest book, edit `story-tech/quests/*.json` and recompile:

```bash
tools/venv/bin/python tools/scripts/check_quests.py story-tech/quests scratch/ids_plus.json
tools/venv/bin/python tools/scripts/compile_quests.py \
  story-tech/quests pack-tech/config/ftbquests/quests scratch/ids_plus.json --strict --astral
(cd pack-tech && ../tools/packwiz refresh)
```

`--astral` is what applies the nothing-hides and one-toast-per-quest conventions; without it you get the story pack's defaults. `check_quests.py` validates keys, dependency cycles, item ids, structure tags and the writing caps in `docs/writing-craft.md` before you compile. The compiler will not overwrite `pack-tech/config/ftbquests/quests/data.snbt`, so the pack title stays "Kettle Tech".

The compiler writes its KubeJS quest-id map into the pack it just compiled for, derived from the output directory, and only when a script in that pack actually reads `global.valleyQuestIds`. Kettle Tech has no such script, so it gets no id map — and compiling the tech book can no longer overwrite the story pack's.

To test a change before Josh plays it, sync it to the headless server:

```bash
tools/scripts/sync_server.sh "$PWD/pack-tech/pack.toml"   # absolute path — the script cds into server/
tools/scripts/server_ctl.sh start && tools/scripts/server_ctl.sh wait
tools/scripts/server_ctl.sh stop
tools/scripts/sync_server.sh                              # leave the server on the story pack
```

Only one server at a time (`pgrep -f "forge/1.20.1.*unix_args"`), and `sync_server.sh` does not prune files the previous pack left behind — clear `server/kubejs`, `server/patchouli_books` and `server/config/ftbquests` by hand when switching packs, or the story pack's scripts will still be sitting there.

Finally, the launcher pulls from `main` on GitHub, so a change is not live for Josh until it is committed and pushed.
