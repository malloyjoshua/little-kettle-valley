# Act III + Oda's Counter + chapter titles — text audit

Rubric: `docs/writing-craft.md` §2 (Picture, Gap, Shape, Causation, Fit, Question), scored 1–5 each, 30 max. **Under 4 on any criterion = a rewrite**, and every one of those is in `docs/audit/changes-act3.json` with paste-ready replacement text.

**Slice:** every `quest_title` / `quest_subtitle` / `quest_description` / `task_text` / `reward_text` in `story/quests/act3.json`, all of `story/quests/oda.json` (the bounty-board / standing-order chapter — the Bountiful pool and decree JSON under `pack/kubejs/data/bountiful/` carries no prose at all, only item ids, so there is nothing there to score), and every `chapter_title` in the corpus.

**Scored: 327 strings. Flagged: 68. Fine: 259.**

## Reading the caps

`Fit` is measured, not estimated. Caps applied per `docs/writing-craft.md` §4: title 45 · subtitle 50 · description line 1 = 140, line 3 = 240, line 5 = 140 · task 60 · toast title 24 / body 160 · tellraw 120 · title card title 22 / subtitle 40. Two judgement calls, stated so they can be overruled:

1. **A sixth description line** (`description[6]`) is capped at 140, the same as line 5. §4 only defines the sixth line for act openers carrying the spine line; four quests in this slice use one for extra fact.
2. **The one-sentence tellraw rule.** All 16 reward tellraws in this slice are two or three sentences, and several of them (S0402, S0452, S0510) are the best writing in the act *because* of the second sentence — fact, then cost. A rule that 100% of the shipped corpus breaks is more likely a length rule than a sentence-count rule, so `Fit` here was scored as ≤120 characters, one speaker. If the literal reading is meant, that is a separate 16-line pass and it will make some of those lines worse.

## Applying the changes

`changes-act3.json` uses the corpus's own `id` / `file` / `locator`, and `old` is byte-identical to the shipped string in every case except the two `.command` tellraws (S0370, S0520), where the corpus concatenates the coloured speaker component with the italic message component. For those two, replace **only the italic text component** and leave `{"text":"Halden: ","color":"green"}` / `{"text":"Josie, on the wall: ","color":"gold"}` alone. Every quest key, dependency, task, item id, count, coordinate, command shape and placeholder is unchanged; every instruction line still opens on a verb; every replacement was measured against its cap, not estimated.

## Three worst offenders

1. **S0475** (`quests[q50].description[4]`) — 362 characters in a 140-character payoff line. It is an entire second quest briefing (meteorite, four named presses, nether quartz, certus arithmetic) filed under "what you will see happen."
2. **S0359** (`quests[q40].description[2]`) — 722 characters in a 240-character instruction line: the order, the mod disambiguation, the shop price and a paragraph of Serene Seasons agronomy, stacked. It is the single longest string in the slice and the one a non-gamer is most likely to bounce off.
3. **S0400** (`quests[q44].description[4]`) — the only *continuity* break in the slice. Oda's ledger runs 112 days needed / 81 covered (S0341) → 12 jars = 4 days (S0378) → the hams should take it to **91 covered, 21 short**. The line says "ninety-one days short," which means the granary gets emptier the more you put in it, and it is the one number in Act III the player is tracking.

## Continuity checks that passed

- **Ledger arithmetic**, apart from S0400: 112 − 81 = 31 (S0341) ✓.
- **Nine people** at the Harvest Supper (S0341) against twelve settings and three empty chairs (S0530): the Ribbits join in Q59 and Tess/Mab/Corin arrive in Act V, so 9 + 3 = 12 is exact, and the three chairs are a legitimate third plant for the February payoff.
- **"The key's brass. My initials are scratched off it and yours are scratched on"** (S0353) — `story-final.md` calls the Q39 reward brass weighing scales, but the shipped reward is `storagedrawers:drawer_key`, so the text is right and the story document is the stale one. No change made.
- **Halden's four years** (S0367 / S0473 / S0507) is consistent across all three, and S0370's "snow never sat on that slope" is a real plant for the Works, so it survives the length cut.
- **The bare fortieth post, forty lamps, eleven years, the cellar door** — all instances in this slice agree with canon and with each other.
- **S0529**, the spine line, is untouched: §5 forbids editing one instance without Act I and Act V.

## Patterns worth fixing at the source

- **Length is the dominant failure: 51 of 327 strings are over their cap**, and the character line of almost every Oda shop quest is 140–216 when the cap is 140. It is systematic, not incidental.
- **Banned gaming register survives in five places**: "tier"/"tiers" (S0467, S0469, S0904), "grind" (S0903), "gate" (S0367).
- **Quest numbers leak into player-facing text** (S0366 "Q23", S1004 "(Q86)"). Nobody playing this reads quest ids.
- **Subtitles that restate** the title or the line beneath them (S0406, S0421, S0447, S0495) — §4 calls the subtitle the last thing allowed to die, and these four were already dead.
- **Bare prices as payoff lines** (S0954, S0970, S0990) — three lines that are a number and a full stop.

## The table

`P` Picture · `G` Gap · `S` Shape · `C` Causation · `F` Fit · `Q` Question. **Bold** = flagged, rewrite in `changes-act3.json`.

| ID | Kind | Locator | P | G | S | C | F | Q | Σ | Diagnosis |
|---|---|---|---|---|---|---|---|---|---|---|
| S0001 | chapter title | `chapter[act1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0002 | chapter title | `chapter[act1].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0003 | chapter title | `chapter[act1].subtitle[1]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0004 | chapter title | `chapter[act1].subtitle[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0169 | chapter title | `chapter[act2].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0170 | chapter title | `chapter[act2].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0171 | chapter title | `chapter[act2].subtitle[1]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0172 | chapter title | `chapter[act2].subtitle[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0335 | chapter title | `chapter[act3].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0336 | chapter title | `chapter[act3].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0337 | chapter title | `chapter[act3].subtitle[1]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0338 | chapter title | `chapter[act3].subtitle[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0339 | quest title | `quests[q38].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0340 | quest subtitle | `quests[q38].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0341 | quest description | `quests[q38].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0342 | quest description | `quests[q38].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — but the instruction repeats the subtitle word for word. |
| **S0343** | quest description | `quests[q38].description[4]` | 3 | 3 | 4 | 4 | 5 | 2 | 21 | Menu summary, no picture — 'both lanes of autumn work' is wiki voice. |
| S0344 | reward text | `quests[q38].rewards[3].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0345 | reward text | `quests[q38].rewards[4].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0346 | reward text | `quests[q38].rewards[4].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0347 | quest title | `quests[q39].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0348 | quest subtitle | `quests[q39].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0349 | quest description | `quests[q39].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0350 | quest description | `quests[q39].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0351 | quest description | `quests[q39].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0352 | task text | `quests[q39].tasks[1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0353 | reward text | `quests[q39].rewards[5].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0354 | reward text | `quests[q39].rewards[7].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0355 | reward text | `quests[q39].rewards[7].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0356 | quest title | `quests[q40].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0357 | quest subtitle | `quests[q40].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0358 | quest description | `quests[q40].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0359** | quest description | `quests[q40].description[2]` | 4 | 3 | 3 | 3 | 1 | 3 | 17 | 722 chars in a 240-char instruction line; four separate topics stacked. |
| **S0360** | quest description | `quests[q40].description[4]` | 4 | 3 | 4 | 4 | 5 | 2 | 22 | Ends on 'which is everything the preserving work needs' — a summary, not an image. |
| S0361 | reward text | `quests[q40].rewards[9].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0362 | reward text | `quests[q40].rewards[9].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0363 | quest title | `quests[q41].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0364 | quest subtitle | `quests[q41].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0365 | quest description | `quests[q41].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0366** | quest description | `quests[q41].description[2]` | 3 | 4 | 4 | 4 | 4 | 4 | 23 | 'the 3 bottles Q23 left you' — a quest number in player-facing text. |
| **S0367** | quest description | `quests[q41].description[4]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 157 > 140; 'the tech lane's next gate' is gaming register. |
| S0368 | task text | `quests[q41].tasks[1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0369 | reward text | `quests[q41].rewards[5].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0370** | reward text | `quests[q41].rewards[6].command` | 5 | 5 | 4 | 4 | 1 | 5 | 24 | 180 > 120 on a tellraw; the reveal plant is buried behind a second clause. |
| S0371 | reward text | `quests[q41].rewards[7].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0372 | reward text | `quests[q41].rewards[7].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0373 | quest title | `quests[q42].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0374 | quest subtitle | `quests[q42].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0375 | quest description | `quests[q42].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0376 | quest description | `quests[q42].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0377** | quest description | `quests[q42].description[4]` | 4 | 4 | 3 | 4 | 1 | 3 | 19 | 263 > 140; sourcing advice sitting in the payoff line. |
| **S0378** | quest description | `quests[q42].description[6]` | 5 | 4 | 4 | 4 | 2 | 5 | 24 | 195 > 140. |
| S0379 | reward text | `quests[q42].rewards[5].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0380 | reward text | `quests[q42].rewards[5].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0381 | quest title | `quests[q43].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0382 | quest subtitle | `quests[q43].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0383 | quest description | `quests[q43].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0384 | quest description | `quests[q43].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0385 | quest description | `quests[q43].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0386 | reward text | `quests[q43].rewards[5].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0387 | reward text | `quests[q43].rewards[6].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0388 | reward text | `quests[q43].rewards[6].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0389 | quest title | `quests[q45a].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0390 | quest subtitle | `quests[q45a].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0391 | quest description | `quests[q45a].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0392 | quest description | `quests[q45a].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0393 | quest description | `quests[q45a].description[4]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0394 | reward text | `quests[q45a].rewards[3].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0395 | reward text | `quests[q45a].rewards[3].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0396 | quest title | `quests[q44].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0397 | quest subtitle | `quests[q44].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0398 | quest description | `quests[q44].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0399 | quest description | `quests[q44].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0400** | quest description | `quests[q44].description[4]` | 4 | 4 | 4 | 2 | 2 | 4 | 20 | 177 > 140, and 'ninety-one days short' contradicts the ledger. |
| S0401 | task text | `quests[q44].tasks[1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0402 | reward text | `quests[q44].rewards[5].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0403 | reward text | `quests[q44].rewards[6].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0404 | reward text | `quests[q44].rewards[6].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0405 | quest title | `quests[q48a].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0406** | quest subtitle | `quests[q48a].subtitle` | 2 | 2 | 4 | 4 | 5 | 2 | 19 | Verbatim echo of the last sentence of the character line above it. |
| S0407 | quest description | `quests[q48a].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0408 | quest description | `quests[q48a].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0409 | quest description | `quests[q48a].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0410** | task text | `quests[q48a].tasks[0].title` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 71 > 60, and it opens with 'Both rooms furnished:' — a status, not the state. |
| S0411 | reward text | `quests[q48a].rewards[5].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0412** | reward text | `quests[q48a].rewards[5].toast.description` | 4 | 4 | 3 | 4 | 2 | 4 | 21 | 170 > 160 and the body does not start 'Next:'. |
| S0413 | quest title | `quests[q51a].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0414 | quest subtitle | `quests[q51a].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0415** | quest description | `quests[q51a].description[0]` | 5 | 5 | 4 | 4 | 3 | 5 | 26 | Exclamation mark — banned outside Pip's mouth. |
| S0416 | quest description | `quests[q51a].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0417 | quest description | `quests[q51a].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0418 | reward text | `quests[q51a].rewards[6].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0419 | reward text | `quests[q51a].rewards[6].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0420 | quest title | `quests[q54a].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0421** | quest subtitle | `quests[q54a].subtitle` | 3 | 2 | 3 | 4 | 2 | 3 | 17 | 51 > 50 and it restates the title's nouns and verb. |
| S0422 | quest description | `quests[q54a].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0423 | quest description | `quests[q54a].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0424** | quest description | `quests[q54a].description[4]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 197 > 140. |
| S0425 | reward text | `quests[q54a].rewards[8].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0426 | reward text | `quests[q54a].rewards[9].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0427 | reward text | `quests[q54a].rewards[9].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0428 | quest title | `quests[q45].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0429 | quest subtitle | `quests[q45].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0430 | quest description | `quests[q45].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0431 | quest description | `quests[q45].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0432** | quest description | `quests[q45].description[4]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 212 > 140. |
| S0433 | task text | `quests[q45].tasks[0].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0434 | reward text | `quests[q45].rewards[7].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — 'iron' vs the tin in S0432 is canon (the clusters include iron). |
| **S0435** | reward text | `quests[q45].rewards[9].command` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 53 > 40 on a title card subtitle. |
| S0436 | reward text | `quests[q45].rewards[10].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0437 | reward text | `quests[q45].rewards[12].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0438 | reward text | `quests[q45].rewards[12].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0439 | quest title | `quests[q46].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0440 | quest subtitle | `quests[q46].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0441** | quest description | `quests[q46].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 187 > 140, and both alloy ratios are repeated verbatim in line 3 below. |
| **S0442** | quest description | `quests[q46].description[2]` | 4 | 4 | 5 | 4 | 3 | 4 | 24 | 241 > 240 by one character. |
| S0443 | quest description | `quests[q46].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0444 | reward text | `quests[q46].rewards[4].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0445** | reward text | `quests[q46].rewards[4].toast.description` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 206 > 160 and four clauses in a three-clause toast. |
| S0446 | quest title | `quests[q47].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0447** | quest subtitle | `quests[q47].subtitle` | 3 | 2 | 3 | 4 | 5 | 3 | 20 | Near-verbatim echo of Bram's line directly beneath it. |
| S0448 | quest description | `quests[q47].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0449** | quest description | `quests[q47].description[2]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 289 > 240. |
| **S0450** | quest description | `quests[q47].description[4]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 182 > 140. |
| S0451 | task text | `quests[q47].tasks[1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0452 | reward text | `quests[q47].rewards[6].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0453 | reward text | `quests[q47].rewards[7].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0454 | reward text | `quests[q47].rewards[7].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0455 | quest title | `quests[q48].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0456 | quest subtitle | `quests[q48].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0457** | quest description | `quests[q48].description[0]` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 143 > 140, and the count is said twice in one sentence. |
| S0458 | quest description | `quests[q48].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0459 | quest description | `quests[q48].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0460 | reward text | `quests[q48].rewards[5].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0461 | reward text | `quests[q48].rewards[6].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0462 | reward text | `quests[q48].rewards[6].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0463 | quest title | `quests[q49].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0464 | quest subtitle | `quests[q49].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0465 | quest description | `quests[q49].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0466 | quest description | `quests[q49].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0467** | quest description | `quests[q49].description[4]` | 3 | 4 | 4 | 4 | 2 | 3 | 20 | 'catalogue tier three' — 'tier' is on the banned gaming-register list. |
| S0468 | reward text | `quests[q49].rewards[1].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0469** | reward text | `quests[q49].rewards[2].toast.title` | 3 | 4 | 4 | 4 | 2 | 3 | 20 | 25 > 24, and 'tier three' again. |
| S0470 | reward text | `quests[q49].rewards[2].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0471 | quest title | `quests[q50].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0472 | quest subtitle | `quests[q50].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0473 | quest description | `quests[q50].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0474 | quest description | `quests[q50].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0475** | quest description | `quests[q50].description[4]` | 4 | 4 | 3 | 3 | 1 | 4 | 19 | 362 > 140 — a whole second quest briefing inside a payoff line. |
| S0476 | reward text | `quests[q50].rewards[4].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0477 | reward text | `quests[q50].rewards[5].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0478 | reward text | `quests[q50].rewards[5].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0479 | quest title | `quests[q51].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0480 | quest subtitle | `quests[q51].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0481 | quest description | `quests[q51].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0482 | quest description | `quests[q51].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0483** | quest description | `quests[q51].description[4]` | 3 | 3 | 4 | 4 | 5 | 2 | 21 | Ends by restating the next quest; no picture. |
| S0484 | reward text | `quests[q51].rewards[6].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0485 | reward text | `quests[q51].rewards[6].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0486 | quest title | `quests[q52].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0487 | quest subtitle | `quests[q52].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0488 | quest description | `quests[q52].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0489** | quest description | `quests[q52].description[2]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 291 > 240. |
| S0490 | quest description | `quests[q52].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0491 | task text | `quests[q52].tasks[1].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0492 | reward text | `quests[q52].rewards[4].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0493 | reward text | `quests[q52].rewards[4].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0494 | quest title | `quests[q53].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0495** | quest subtitle | `quests[q53].subtitle` | 3 | 3 | 4 | 4 | 2 | 3 | 19 | 51 > 50 and it restates the title's objects. |
| S0496 | quest description | `quests[q53].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0497 | quest description | `quests[q53].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0498** | quest description | `quests[q53].description[4]` | 2 | 3 | 4 | 4 | 5 | 3 | 21 | 'every "bring X to Y" quest' — placeholder letters in player-facing prose. |
| **S0499** | task text | `quests[q53].tasks[0].title` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 65 > 60 and it reads as a report, not a state. |
| S0500 | reward text | `quests[q53].rewards[3].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S0501** | reward text | `quests[q53].rewards[5].command` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 46 > 40 on a title card subtitle. |
| S0502 | reward text | `quests[q53].rewards[6].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0503 | reward text | `quests[q53].rewards[8].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0504 | reward text | `quests[q53].rewards[8].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0505 | quest title | `quests[q54].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0506 | quest subtitle | `quests[q54].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0507** | quest description | `quests[q54].description[0]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 151 > 140. |
| S0508 | quest description | `quests[q54].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0509** | quest description | `quests[q54].description[4]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 168 > 140. |
| S0510 | reward text | `quests[q54].rewards[2].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0511 | reward text | `quests[q54].rewards[3].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0512 | reward text | `quests[q54].rewards[3].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0513 | quest title | `quests[q55].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0514 | quest subtitle | `quests[q55].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0515** | quest description | `quests[q55].description[0]` | 5 | 5 | 4 | 4 | 1 | 5 | 24 | 219 > 140 — the best character line in the act is 79 chars over. |
| S0516 | quest description | `quests[q55].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0517** | quest description | `quests[q55].description[4]` | 4 | 4 | 4 | 4 | 1 | 4 | 21 | 261 > 140. |
| S0518 | task text | `quests[q55].tasks[0].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0519 | reward text | `quests[q55].rewards[3].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0520** | reward text | `quests[q55].rewards[6].command` | 5 | 5 | 5 | 5 | 2 | 5 | 27 | 128 > 120 on the reveal line. |
| **S0521** | reward text | `quests[q55].rewards[9].command` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 47 > 40 on a title card subtitle. |
| S0522 | reward text | `quests[q55].rewards[10].command` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0523** | reward text | `quests[q55].rewards[12].toast.title` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 27 > 24. |
| **S0524** | reward text | `quests[q55].rewards[12].toast.description` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 203 > 160. |
| S0525 | quest title | `quests[q56].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0526** | quest subtitle | `quests[q56].subtitle` | 3 | 3 | 4 | 4 | 2 | 3 | 19 | 53 > 50, and it breaks the finale-subtitle pattern the other four acts use. |
| S0527 | quest description | `quests[q56].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0528 | quest description | `quests[q56].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0529 | quest description | `quests[q56].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — protected spine line; do not edit this instance without Act I and Act V. |
| **S0530** | quest description | `quests[q56].description[6]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 166 > 140. |
| S0531 | task text | `quests[q56].tasks[3].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0532 | reward text | `quests[q56].rewards[2].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0533 | reward text | `quests[q56].rewards[2].toast.description` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0534 | chapter title | `chapter[act4].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0535 | chapter title | `chapter[act4].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0536 | chapter title | `chapter[act4].subtitle[1]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0537 | chapter title | `chapter[act4].subtitle[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0727 | chapter title | `chapter[act5].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0728 | chapter title | `chapter[act5].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0729 | chapter title | `chapter[act5].subtitle[1]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0730 | chapter title | `chapter[act5].subtitle[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0901 | chapter title | `chapter[oda].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0902 | chapter title | `chapter[oda].subtitle[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0903** | chapter title | `chapter[oda].subtitle[1]` | 3 | 4 | 4 | 4 | 2 | 3 | 20 | 'grind' is on the banned gaming-register list. |
| **S0904** | chapter title | `chapter[oda].subtitle[2]` | 3 | 4 | 4 | 4 | 2 | 3 | 20 | 'tiers' twice — banned register, and it says nothing she can see. |
| S0905 | quest title | `quests[oda_open].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0906 | quest subtitle | `quests[oda_open].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0907 | quest description | `quests[oda_open].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0908 | quest description | `quests[oda_open].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0909 | quest description | `quests[oda_open].description[4]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0910** | quest description | `quests[oda_open].description[6]` | 4 | 4 | 4 | 4 | 1 | 4 | 21 | 317 > 140. |
| S0911 | task text | `quests[oda_open].tasks[0].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0912 | reward text | `quests[oda_open].rewards[2].command` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0913 | reward text | `quests[oda_open].rewards[3].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0914** | reward text | `quests[oda_open].rewards[3].toast.description` | 4 | 4 | 3 | 4 | 5 | 4 | 24 | Toast body does not start 'Next:'. |
| S0915 | quest title | `quests[oda_standing_order].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0916 | quest subtitle | `quests[oda_standing_order].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0917 | quest description | `quests[oda_standing_order].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0918 | quest description | `quests[oda_standing_order].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — shop line 3 states a price, not a verb-first order; the title carries the imperative. |
| S0919 | quest title | `quests[oda_casings].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0920 | quest subtitle | `quests[oda_casings].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0921 | quest description | `quests[oda_casings].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0922 | quest description | `quests[oda_casings].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0923 | quest title | `quests[oda_alloy].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0924 | quest subtitle | `quests[oda_alloy].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0925** | quest description | `quests[oda_alloy].description[0]` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 141 > 140 by one character. |
| S0926 | quest description | `quests[oda_alloy].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0927 | quest title | `quests[oda_gearing].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0928 | quest subtitle | `quests[oda_gearing].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0929** | quest description | `quests[oda_gearing].description[0]` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 144 > 140. |
| S0930 | quest description | `quests[oda_gearing].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — brushes the banned 'not X, but Y' shape but earns it. |
| S0931 | quest title | `quests[oda_seedbox].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0932 | quest subtitle | `quests[oda_seedbox].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0933 | quest description | `quests[oda_seedbox].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0934 | quest description | `quests[oda_seedbox].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0935 | quest title | `quests[oda_pantry].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0936 | quest subtitle | `quests[oda_pantry].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0937 | quest description | `quests[oda_pantry].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0938 | quest description | `quests[oda_pantry].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0939 | quest title | `quests[oda_lampoil].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0940 | quest subtitle | `quests[oda_lampoil].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0941** | quest description | `quests[oda_lampoil].description[0]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 166 > 140. |
| **S0942** | quest description | `quests[oda_lampoil].description[2]` | 3 | 2 | 3 | 4 | 5 | 2 | 19 | 'Light is not decoration, it is the thing that keeps...' — banned 'not X, it is Y' shape, and it preaches. |
| S0943 | quest title | `quests[oda_servos].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0944 | quest subtitle | `quests[oda_servos].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0945** | quest description | `quests[oda_servos].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 173 > 140. |
| S0946 | quest description | `quests[oda_servos].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0947 | quest title | `quests[oda_frames].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0948 | quest subtitle | `quests[oda_frames].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0949** | quest description | `quests[oda_frames].description[0]` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 142 > 140. |
| S0950 | quest description | `quests[oda_frames].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0951 | quest title | `quests[oda_coils].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0952 | quest subtitle | `quests[oda_coils].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0953 | quest description | `quests[oda_coils].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0954** | quest description | `quests[oda_coils].description[2]` | 1 | 2 | 3 | 3 | 5 | 1 | 15 | 'Eighteen Scrip.' — a price with nothing attached. |
| **S0955** | quest title | `quests[oda_fluxduct].title` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 46 > 45. |
| S0956 | quest subtitle | `quests[oda_fluxduct].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0957 | quest description | `quests[oda_fluxduct].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0958 | quest description | `quests[oda_fluxduct].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0959 | quest title | `quests[oda_cat_furniture].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0960 | quest subtitle | `quests[oda_cat_furniture].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0961** | quest description | `quests[oda_cat_furniture].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 155 > 140. |
| S0962 | quest description | `quests[oda_cat_furniture].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0963 | quest title | `quests[oda_cat_windows].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0964 | quest subtitle | `quests[oda_cat_windows].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0965** | quest description | `quests[oda_cat_windows].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 155 > 140. |
| S0966 | quest description | `quests[oda_cat_windows].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0967 | quest title | `quests[oda_cat_garden].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0968 | quest subtitle | `quests[oda_cat_garden].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0969** | quest description | `quests[oda_cat_garden].description[0]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 161 > 140. |
| **S0970** | quest description | `quests[oda_cat_garden].description[2]` | 1 | 2 | 3 | 3 | 5 | 1 | 15 | 'Ten Scrip.' — a price with nothing attached. |
| S0971 | quest title | `quests[oda_cat_lights].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0972 | quest subtitle | `quests[oda_cat_lights].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0973** | quest description | `quests[oda_cat_lights].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 157 > 140. |
| S0974 | quest description | `quests[oda_cat_lights].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0975 | quest title | `quests[oda_livestock].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0976 | quest subtitle | `quests[oda_livestock].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0977 | quest description | `quests[oda_livestock].description[0]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0978 | quest description | `quests[oda_livestock].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0979 | quest title | `quests[oda_rare_seeds].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0980 | quest subtitle | `quests[oda_rare_seeds].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0981** | quest description | `quests[oda_rare_seeds].description[0]` | 5 | 5 | 4 | 4 | 2 | 5 | 25 | 167 > 140. |
| S0982 | quest description | `quests[oda_rare_seeds].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0983 | quest title | `quests[oda_reactor_casings].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0984 | quest subtitle | `quests[oda_reactor_casings].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0985** | quest description | `quests[oda_reactor_casings].description[0]` | 4 | 4 | 4 | 4 | 1 | 4 | 21 | 216 > 140. |
| S0986 | quest description | `quests[oda_reactor_casings].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0987 | quest title | `quests[oda_reactor_internals].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0988 | quest subtitle | `quests[oda_reactor_internals].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0989** | quest description | `quests[oda_reactor_internals].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 167 > 140. |
| **S0990** | quest description | `quests[oda_reactor_internals].description[2]` | 1 | 2 | 3 | 3 | 5 | 1 | 15 | 'Thirty-five Scrip.' — a price with nothing attached. |
| S0991 | quest title | `quests[oda_ae_bundle].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0992 | quest subtitle | `quests[oda_ae_bundle].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0993** | quest description | `quests[oda_ae_bundle].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 154 > 140. |
| S0994 | quest description | `quests[oda_ae_bundle].description[2]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0995 | quest title | `quests[oda_plushie].title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0996 | quest subtitle | `quests[oda_plushie].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S0997 | quest description | `quests[oda_plushie].description[0]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S0998 | quest description | `quests[oda_plushie].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S0999** | quest title | `quests[oda_works_deed].title` | 4 | 4 | 4 | 4 | 3 | 4 | 23 | 46 > 45. |
| S1000 | quest subtitle | `quests[oda_works_deed].subtitle` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| **S1001** | quest description | `quests[oda_works_deed].description[0]` | 4 | 4 | 4 | 4 | 2 | 4 | 22 | 159 > 140. |
| S1002 | quest description | `quests[oda_works_deed].description[2]` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine — shop line 3 exception, as above. |
| S1003 | quest description | `quests[oda_works_deed].description[4]` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| **S1004** | task text | `quests[oda_works_deed].tasks[0].title` | 3 | 4 | 4 | 4 | 3 | 3 | 21 | '(Q86)' — a quest number in player-facing text. |
| S1005 | reward text | `quests[oda_works_deed].rewards[3].toast.title` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1006 | reward text | `quests[oda_works_deed].rewards[3].toast.description` | 5 | 5 | 5 | 5 | 5 | 5 | 30 | Fine. |
| S1540 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1541 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1542 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1543 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1544 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
| S1545 | chapter title | `chapter.group` | 4 | 4 | 4 | 4 | 5 | 4 | 25 | Fine. |
