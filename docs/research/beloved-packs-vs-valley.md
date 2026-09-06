# Why the beloved packs are beloved, and why ours still kinda sucks

*2026-09-05, evening. Eleven research and audit agents (six packs, one on design principles, three
audits of this pack through different players' eyes, one critic), 516 page reads and file reads,
then this synthesis. Josh's question, verbatim: "Do a deep dive to why all these packs are so
beloved and why ours still kinda sucks." The six packs are the ones a previous answer recommended:
StoneBlock 3, FTB Evolution, FTB University 1.16, Direwolf20 1.21, All the Mods 10, Enigmatica 9.*

## The short answer

They are beloved because a lot of people have already played them. Every one of the six shipped
broken, in public, and then got fixed in public for months or years: StoneBlock 3 has been
patched from v1.0 to v1.11.6 over four years; Evolution shipped 73 versions in 22 months (with
aluminium ore missing from the world at launch and an Immersive Engineering block that had no
recipe at all); University shipped launch crashes and text left over from the 1.12 version;
Direwolf20 has 36 numbered patches; ATM10 pushes several point releases a day when it has to;
Enigmatica 9 runs a develop branch, a CI formatter and a public tracker. None of them ran a
closed beta. Their polish is the residue of thousands of strangers hitting the bugs first.

Ours has had exactly one tester, and that tester is also the customer. Ninety-seven commits in
four days is what it looks like when the first human play-through and the bug-fixing happen in
the same person at the same time. That is the whole diagnosis. Everything below is detail.

And a correction to the earlier recommendation: "FTB Evolution (1.20.1, chapters walking through
Create, Thermal, Mekanism)" does not exist as described. The real FTB Evolution is a 1.21 tech
and magic pack with airships, custom dimensions and a Pyramid endgame. The pack that most
resembles what was described is our own Kettle Tech fork.

## What the six actually do

**StoneBlock 3.** You spawn sealed in stone with empty hands. The first goal needs no tutorial
because the world is the tutorial: punch stone, get pebbles, make a crook and a hammer. Every
early quest hands you the tool, not the recipe. The map cannot sprawl: biomes generate in rings
around you. Weaknesses players report: guidance drops off after the first stretch, the endgame
is a grind for gear with nothing to use it on.

**FTB Evolution (real one).** One world with a full tech stack and a full magic stack, chapter
per system, named world tiers (Midgard, Asgard) you can feel yourself climbing, a custom Java
companion mod written just so airships don't eat your automation. Ships fast and in public.
Quest text has shipped with wrong item names and stale tool references.

**FTB University 1.16.** The first quest hands you a finished, furnished, stocked house. The
pack's stated promise is to skip the early game so you can learn the mods, and it keeps it in
the first five minutes. 900 quests in 24 chapters, one per mod, no forced order, written in a
first-person joking voice. Vein Miner is pre-bound and explained because it was the most asked
question in every let's play. Typos get filed and fixed by name.

**Direwolf20 Season 14.** No quest book on purpose. Mods at their authors' balance. The let's
play is the tutorial. It is loved by people who already know what they are doing and want the
tools they know; a cold newcomer gets 314 mods and a search bar.

**All the Mods 10.** "Quests are optional. Mods are not gated." A free pre-built base from a
supply camp on minute one. Sixty-six chapters, one per mod, in a joking second-person voice.
One visible endgame, the ATM Star, that every mod feeds. Rewards deliberately generous because
the team optimises for momentum. Weakness: decision paralysis, and the back half of the book
reads as fetch-and-craft busywork.

**Enigmatica 9.** Getting Started is five quests. Quest one is a checkmark that says hello and
hands you a loot crate. Then a fork you choose (Discovery or Learning Mods), and two books: a
pack-written "Modded for Dummies" primer and an Eccentric Tome that morphs into any mod's own
manual. Ninety duplicate ingots hidden by script so JEI shows one copper. Quests reveal
themselves progressively instead of dumping the tree. A CI formatter keeps 1,000 files
consistent, a bot regenerates the modlist, a develop branch precedes every release.

## What they have in common

1. **The first real thing you do is obvious and fast, and it is a thing, not a reading.** A
   stone to punch, a house to place, a crate to open. Enigmatica's first quest is one click and
   a reward. StoneBlock's is a fist.
2. **The book is a guide before it is a story.** Voice is welcome; volume is not. The packs that
   write well write short: one idea, one joke, one task.
3. **Nothing important is gated on something the player cannot see.** Either mods are ungated
   (ATM10, Direwolf20), or gates are named (Evolution's tiers), or the whole tree is visible and
   greyed. And nothing is gated on a mechanic the pack itself broke.
4. **Duplicates and conflicts are removed by script before players see them.** Enigmatica's
   unification pass exists because a player wrote "there were multiple versions of the same
   ingot". Our JEI hides and our unify.js are the same idea; our chest ring giving a crate and
   our paper matching a notice board are the failures it exists to prevent.
5. **Rewards make momentum.** ATM10's team answers "the free Dragon Egg breaks progression" with
   "in a kitchen sink that is fine". Hand the player the machine.
6. **They fix in public, fast, and forever.** Public tracker, visible labels, changelogs that
   name the player's bug. The pack gets less broken because it is played, not because it was
   tested.
7. **Nobody edits the world under the player, and nobody resets saves without warning.** FTB's
   version numbers exist to signal "this one needs a new world".

## Why ours still kinda sucks

**The root cause, which all three audits found independently:** every quality gate we have
proves the artifact and none proves the experience. The playthrough harness puts a creative-mode
bot at spawn and force-completes all 136 quests by command in dependency order. It has never
crafted, mined, cooked, slept or read a line. The terrain probes read region files. The text
audit counts characters. All of it is real and all of it is good, and none of it requires a
person to do anything. So the bugs that survive are exactly the ones a person hits in the first
hour: a sentence that omits an ingredient, a hint for a key that isn't bound, a trap item, a
quest that needs iron before the quest that teaches iron, a world whose ores were deleted by a
mod default nobody mined for ten minutes to notice.

**The proof:** the shipped world's clock was frozen. `doDaylightCycle=false`, permanent morning,
in every copy we ship. The bed refuses outside night. "Sleep One Night in Your Bed" is the sole
gate on all of Act I. It survived two "135 of 135, zero errors" playthroughs because the bot
never tried to sleep. It was found tonight by the critic reading `level.dat`, verified, and
fixed (commit 7b69ced, with a self-heal on every server load for copies already downloaded).
Your own copy progressed past it only because it was downloaded before the rebuild that froze
it.

**The gaps that matter most, in order.** Severity is "fatal" if it would make the target player
quit, "major" if it frustrates, "minor" if it is polish. Evidence is where it lives.

| # | Gap | Sev | Evidence | Fix |
|---|---|---|---|---|
| 1 | No human has played hour one before a customer did. The harness force-completes. | fatal | `tools/scripts/playthrough.sh:150,168-172`; `docs/STATUS.md` says so in its own words | A survival-mode run of q01–q19 with real hands, mine and me, before her. Add `hour_one.sh` that force-completes nothing. |
| 2 | Frozen clock, sleep impossible, Act I gated | fatal | `level.dat` ×3, q08 → q09/q12/q15 | Fixed tonight (7b69ced) |
| 3 | Two players both had to sleep to pass a night (`playersSleepingPercentage=100`) | fatal for co-op | `level.dat` | Fixed tonight: 1 sleeper passes the night, plus the load-time guard |
| 4 | Quest sentences that disagree with the recipe or the graph: soup named three vegetables, recipe wants four; Bram's toast pointed at the old next quest after this afternoon's reorder; "Stage market_stalls:" in player text | fatal (soup) | `start.json` q06, `act1.json` q12, q17 | Fixed tonight. Add a compiler check: a "Next:" toast must name a quest that actually follows; a quest naming ingredients must name every one the recipe wants. |
| 5 | The quest book renders at FTB Quests' stock theme: eight icons over the live world, chapter panel collapsed, no background. Every legibility fix landed in the data and none reaches the eye. | fatal (newcomer) | `media/look/NOTES.md` #7, no `ftbquests-client` config in the repo | Ship a client config with the chapter panel pinned open and an opaque background; one chapter image. Screenshot it. |
| 6 | Nothing teaches Minecraft itself. `tutorialStep:none` copies Astral, which assumes a Minecraft player. She has never crafted. | fatal (newcomer) | `pack/options.txt`; readme.json | Three checkmark quests at the top of Read Me First: move and look, break a block and the 2×2 vs 3×3 grid, eat and sleep. |
| 7 | The first hour hands her eleven stacks in q01 and twelve in q03 with no backpack, and the pack is dark, normal difficulty, no keepInventory, phantoms on. | major | `start.json` rewards; `level.dat`; `server.properties` | Backpack in q01; cut q03 to what it needs. Decision for Josh: peaceful + keepInventory for her copy. Exactly one quest in 136 needs a mob drop, and it is shearable wool. |
| 8 | Read Me First promises "either lane on its own is a way through". The graph says 84 of 136 quests are required, 16 of them hard tech. `PITCH.md` says the opposite. | major | `readme.json` rm_lanes; dependency walk from q91 | Rewrite one sentence to the truth. |
| 9 | Silent world border at 1,500 blocks on first join, centred on the origin, no message. The veteran audit calls this fatal for the player who wants to explore. | major | `valley_core.js:1131` | Start at 6,000 and say so in Read Me First; keep the per-act growth. |
| 10 | Every tech quest is a one-and-done checkbox with parts and ore location supplied. There is no shortage that forces the next machine. No multiblock build guide anywhere; the reactor and turbine are asked for without a picture. | major (veteran) | item census over `story/quests`; `guide_page` used 0 times | Give the Act IV heat loop a number a Stirling dynamo cannot meet. Add `patchouli:multiblock` pages to the two field notes that exist (book JSON only). |
| 11 | Zero quests send anyone anywhere. 156 item tasks, 64 checkmarks, 1 stage task, no structure, biome or dimension task. | major (veteran) | task census | One optional chapter of five exploration quests; the compiler already supports the task types. |
| 12 | Optional flags: 8 of 113 story quests, none in the first three chapters. The board reads as all-homework. | major | `grep optional story/quests` | Flag the furnish and dress quests optional. One key each. |
| 13 | Descriptions average 380–480 characters, five lines each, on every quest including "Craft 8 Andesite Alloy". Astral averages 244. | major/minor (the lenses disagree) | measured | Two lines for the ~38 pure craft quests; keep every quest where a resident speaks. |
| 14 | The shipped world is write-once, so world fixes never reach existing installs unless there is a command (`/valley ores`, `/valley fixfloors`). | major | `pack/index.toml` preserve flags | Stamp a world revision in persistentData; on login, run the idempotent repairs when behind. |
| 15 | Commands whose result is never read. The doors that stayed shut through two clean runs (3edc0b2) were this. | major | `runCommandSilent` call sites | A wrapper that warns on a zero result; a harness assert that every registry door is open after Act V. |
| 16 | The valley reads as machine output from the ridge (contour steps), the counters don't reconcile (residents 4/15 then bossbar 5), a rendering taint (Supplementaries into Embeddium's fluid renderer) is documented and unnamed in the runbook. | minor | `STATUS.md`, `text-audit.md`, `integration-audit-night.md` N6 | Named in the docs already; do them in order. |

**What the critic says the research cannot answer, and it is right.** None of the six packs
ships a hand-built world, none is a cozy narrative NPC pack, none was examined for two-player
co-op or for updating a save safely. The peers on our actual axes (Create: Astral, Prominence II,
Farming Valley, Cottage Witch, Blightfall) were not in the set. So the comparison above is
strongest on onboarding, quest shape and process, and weakest on exactly the choices that make
this pack this pack. A second research round on those five is the obvious next study.

## What we do better than any of the six

These are real, and they are the reason the pack is worth finishing rather than replacing.

- **The writing.** There is a scoring rubric, a banned-phrase list, a per-format length table, and
  an audit that scored 1,647 strings and rewrote 364. No big pack has that. The letter is good.
- **The "Next:" line.** 105 of 126 quests end by naming what to do next, where, and with whom.
  Astral's answer to "what now" is "open the book".
- **Nothing scripted can eat your build.** `runSeg()` refuses every world-editing verb, and the
  harness greps the runtime scripts and exits before it will boot. The failure that made the
  first version glitchy stopped existing instead of getting rarer.
- **Oda's Counter.** An anti-grind valve with a thought-out economy. No beloved tech pack ships one.
- **Auto-claim, one toast per quest.** Better than Astral's click-to-claim for a newcomer, and
  it fixed the missing-waystone bug.
- **A real two-player braid.** 34% of quests have two or more dependencies, and the couplings are
  real (the boards for the water wheel exist because someone dried oak).
- **Integration by decompilation, not assumption.** Keybind collisions found in bytecode; the
  energy chain verified by scanning every jar.
- **World-integrity testing.** Twenty salted blocks survive the whole story, diffed off disk.
  No published pack has an equivalent.
- **The install.** One file, auto-updating, tuned for her machine, measured at her settings.

## What to do, in order

1. **A person plays hour one.** Me first with a survival harness that force-completes nothing
   (q01–q19 from the recipes and the world that actually ship), then Josh, then her. Every bug
   found tonight would have fallen out of that in twenty minutes.
2. **Freeze it for her.** Beloved packs patch daily because they have millions of players. An
   audience of one gets a version that stops moving the day she starts. Hotfix only what blocks.
3. **The three newcomer fatals:** the book theme, the three "how to Minecraft" quests, the
   backpack and the trimmed first crate. Half a day.
4. **Josh's calls, each one line:** peaceful and keepInventory for her copy; world border 6,000
   with a sentence; the optional flags; the Read Me First lane sentence.
5. **The veteran's two:** a heat number the dynamo cannot meet, and multiblock pages for the
   reactor and turbine.
6. **Process:** the compiler checks for "Next:" toasts and ingredient sentences; the
   runCommandSilent wrapper; the world-revision stamp with repairs on login.
7. **Round two of this study** on the five peers that actually resemble us.

## Method and caveats

Six pack researchers (sonnet, web), one principles researcher, three audits of this repository
(opus; newcomer, veteran, QA), one critic (opus). Reddit was unreachable to the researchers, so
player sentiment leans on forums, GitHub trackers, blogs and changelogs; "beloved" was never
measured with numbers beyond download counts, and several single-source claims are flagged in
the critic's notes. The audits did not launch the game; their first-hour narratives are
reconstructions from files, which is itself the point of finding #1.

## Sources read by the researchers


**FTB StoneBlock 3**

- https://www.curseforge.com/minecraft/modpacks/ftb-stoneblock-3
- https://www.feed-the-beast.com/modpacks/100-ftb-stoneblock-3
- https://feed-the-beast.com/modpacks/100/changelog/2280
- https://www.curseforge.com/minecraft/modpacks/ftb-stoneblock-3/files/5735554
- https://cursedquail.com/blog/2023-01.stoneblock3-review/
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/2544
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/1889
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/2731
- https://forum.feed-the-beast.com/threads/stoneblock-3-quests.306912/
- https://github.com/FTBTeam/FTB-StoneBlock-Companion/blob/main/README.md
- https://orian34.github.io/travelogues/posts/stoneblock3/
- https://borg286.github.io/stoneblock/
- https://github.com/FTBTeam/FTB-Modpack-Issues (issue-tracker pattern search: StoneBlock 3 tagged issues)

**IMPORTANT DISCREPANCY: The task briefed "FTB Evolution" as M**

- https://www.curseforge.com/minecraft/modpacks/ftb-evolution
- https://www.curseforge.com/minecraft/modpacks/ftb-evolution/files/all
- https://www.curseforge.com/minecraft/modpacks/ftb-evolution/files/all?page=4
- https://www.curseforge.com/minecraft/modpacks/ftb-evolution/files/8279842/dependencies
- https://www.curseforge.com/minecraft/mc-mods/ftb-evolution-companion
- https://www.feed-the-beast.com/modpacks/125-ftb-evolution
- https://www.feed-the-beast.com/blog/p/ftb-evolution
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/6055
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/6447
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/13266
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/6523
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/6154
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/6059
- https://forum.feed-the-beast.com/ (confirmed archived/read-only, discussion moved to Discord)

**FTB University 1.16**

- https://www.feed-the-beast.com/modpacks/90-ftb-university-116
- https://github.com/FTBTeam/FTB-University
- https://raw.githubusercontent.com/FTBTeam/FTB-University/main/resources/ftbuniversity/lang/en_us.lang
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/3109
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/3094
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/3101
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/3141
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/3140
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/290
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues/1150
- https://api.github.com/repos/FTBTeam/FTB-Modpack-Issues/issues?labels=FTB%20University%201.16
- https://www.youtube.com/watch?v=1DiespWEZbA
- https://forum.feed-the-beast.com/threads/ftb-university-wont-launch.303398/
- https://www.9minecraft.net/ftb-university-modpack/
- https://api.github.com/repos/FTBTeam/FTB-University/contributors
- https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge

**FTB Presents: Direwolf20 – Season 14**

- https://www.curseforge.com/minecraft/modpacks/ftb-presents-direwolf20-s14
- https://www.feed-the-beast.com/modpacks/126-ftb-presents-direwolf20-121
- https://feed-the-beast.com/modpacks/126-modpack/versions
- https://www.curseforge.com/minecraft/modpacks/ftb-presents-direwolf20-s14/files/7982629
- https://www.curseforge.com/minecraft/modpacks/ftb-presents-direwolf20-s14/files/7431790
- https://www.curseforge.com/minecraft/modpacks/ftb-presents-direwolf20-s14/files/5734567
- https://gdlauncher.com/modpacks/curseforge/ftb-presents-direwolf20-s14
- https://forum.craftersland.net/topic/59074-update-ftb-direwolf20-120-server-to-direwolf20-121-version-vote-here/
- https://github.com/FTBTeam/FTB-Modpack-Issues/issues?q=is%3Aissue+direwolf20+1.21+in%3Atitle
- https://www.thetvdb.com/series/direwolf20s-lets-play/seasons/official/14
- https://www.9minecraft.net/ftb-presents-direwolf20-modpack/ (via search synthesis)
- https://feed-the-beast.fandom.com/wiki/Direwolf20_Pack (via search synthesis; direct fetch blocked by paywall)
- https://www.modpackindex.com/modpack/90586/ftb-presents-direwolf20-season-14 (via search synthesis; direct fetch blocked/403)

**All the Mods 10**

- https://www.curseforge.com/minecraft/modpacks/all-the-mods-10
- https://github.com/AllTheMods/ATM-10
- https://github.com/AllTheMods/ATM-10-a
- https://github.com/AllTheMods/ATM-10/issues/3293
- https://github.com/AllTheMods/ATM-10/discussions/3539
- https://github.com/AllTheMods/ATM-10/blob/main/CHANGELOG.md
- https://github.com/AllTheMods/ATM-10/blob/main/MOD_ISSUES.md
- https://github.com/AllTheMods/ATM-10/tree/main/config/ftbquests/quests/chapters
- https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/lang/en_us/chapters/welcome.snbt
- https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/lang/en_us/chapters/mainquestline_part_1.snbt
- https://raw.githubusercontent.com/AllTheMods/ATM-10/main/config/ftbquests/quests/lang/en_us/chapters/chapter_2_the_star.snbt
- https://allthemods.github.io/alltheguides/atm10/
- https://all-themods.com/beginner-guide/
- https://all-themods.com/mod-list/
- https://www.akliz.net/blog/posts/exploring-all-the-mods-10
- https://mineyourmind.net/forum/threads/all-the-mods-10.36726/

**Enigmatica 9**

- https://www.curseforge.com/minecraft/modpacks/enigmatica9
- https://github.com/EnigmaticaModpacks/Enigmatica9
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/changelogs/CHANGELOG.md
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/MODLIST.md
- https://github.com/EnigmaticaModpacks/Enigmatica9/issues
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/config/ftbquests/quests/chapters/getting_started.snbt
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/config/ftbquests/quests/chapters/adventure.snbt
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/config/ftbquests/quests/chapters/mekanism.snbt
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/config/ftbquests/quests/data.snbt
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/kubejs/client_scripts/base/emi_material_unification.js
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/.github/workflows/modlist.yml
- https://github.com/EnigmaticaModpacks/Enigmatica9/blob/master/.github/workflows/support.yml
- https://github.com/EnigmaticaModpacks/Enigmatica9/pull/440
- https://api.github.com/repos/EnigmaticaModpacks/Enigmatica9/contributors
- https://api.github.com/repos/EnigmaticaModpacks/Enigmatica9/releases
- https://wiki.enigmatica.net/enigmatica-9
- https://blog.enigmatica.net/
- https://web.archive.org/web/20251229195043/https://mmcreviews.com/all/modpacks/enigmatica-9-e9-1-19-2/
- https://moddex.gg/modpack/enigmatica9

**Design principles**

- forum.feed-the-beast.com/threads/ftb-interactions-turd.300471/
- forum.feed-the-beast.com/threads/what-makes-a-good-modpack.167847/
- forum.feed-the-beast.com — 'Survey - Future Quest Based Modpacks' thread, page 3 (forum.feed-the-beast.com/threads/survey-future-quest-based-modpacks.270903/page-3)
- forum.feed-the-beast.com/threads/a-whiny-rant.140596/page-2
- forum.feed-the-beast.com/threads/is-there-way-to-detect-recipe-conflict.101568/
- blog.curseforge.com/author-workshop-designing-your-modpack/ (Vazkii)
- blog.curseforge.com/best-minecraft-quests-mods/
- blog.curseforge.com/10-questions-with-vazkii/
- GDC 2016 — Celia Hodent, 'The Gamer's Brain, Part 2: UX of Onboarding and Player Engagement' (gdcvault.com/play/1023231 ; celiahodent.com/gamers-brain-ux-onboarding/)
- modrinth.com/mod/disableannounceadvancement
- moddex.gg/modpack/create-astral (Create: Astral reviews)
- SkyFactory 4 official page — minecraft.net/en-us/article/sky-factory-4
- Vault Hunters wiki/FAQ — wiki.vaulthunters.gg ; blog.curseforge.com/minecraft-vault-hunters-modpack-frequently-asked-questions/
- Enigmatica 2: Expert wiki — e2e.fandom.com/wiki/Enigmatica_2:_Expert
- SevTech: Ages summaries — mmcreviews.com/all/modpacks/sevtech-ages/ ; sevtechages.fandom.com
- Prominence II coverage — modrinth.com/modpack/prominence-2-fabric ; space-node.net/blog/prominence-2-rpg-modpack-server-guide-2026 ; 9minecraft.net/prominence-ii-modpack/
- All The Mods Expert (ATM3E) — curseforge.com/minecraft/modpacks/all-the-mods-3-expert ; modpackindex.com/modpack/5527/all-the-mods-3-expert-atm3e
- GGServers blog — ggservers.com/blog/how-to-make-your-mixed-minecraft-modpack-cohesive-balanced-and-built-to-last/
- Countly player retention benchmarks — countly.com/blog/player-retention-analytics-the-metrics-that-predict-long-term-game-success
- Cross-genre backlash analogy — Valheim terrain-generation/Ashlands update coverage (community discussion summaries)
- Cross-community modpack-author burnout analogy — itch.io developer post-mortem on discontinuing a Risk of Rain 2 modpack
