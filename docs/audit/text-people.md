# Audit — people text (greetings, NPC lines, finale speeches)

Slice: `npc_greeting_before` (58) · `npc_greeting_after` (33) · `npc_line` (45) · `finale_speech` (16) = **152 strings**. `scene_line` and `bossbar` are not kinds in `story/text-corpus.json`; the scene beats are filed as `npc_line` and are included below.

Scored against `docs/writing-craft.md` §2, 1–5 per criterion, in the order **Picture / Gap / Shape / Causation / Fit / Question**. Anything under 4 on any criterion is rewritten in `docs/audit/changes-people.json`.

**36 of 152 flagged.**


## Named residents — greetings (`story/npcs.json`)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1007` | 5/5/5/4/5/5 | Fine. |
| `S1008` | 5/5/5/4/5/5 | Fine. |
| `S1009` | 5/5/4/4/5/5 | Fine. |
| `S1010` | 5/5/5/5/5/5 | Fine. |
| `S1011` | 4/5/5/4/5/4 | Fine. |
| `S1012` | 5/5/5/4/5/5 | Fine. |
| `S1013` **↯** | 5/2/4/4/5/4 | Byte-identical to her before-line — the arc closes and she says the same sentence. |
| `S1014` **↯** | 5/2/4/4/5/4 | Byte-identical to her before-line; the loaf never becomes a different loaf. |
| `S1015` **↯** | 5/2/4/4/5/4 | Byte-identical to her before-line; thirty years of one fire, unchanged by the whole pack. |
| `S1016` **↯** | 3/2/4/4/5/3 | Byte-identical to her before-line; no fact moves. |
| `S1017` | 5/5/5/4/5/5 | Fine. |
| `S1018` | 5/5/4/4/5/4 | Fine. |
| `S1019` | 5/5/5/5/5/5 | Fine. |
| `S1020` | 5/5/5/5/5/5 | Fine. |
| `S1021` | 5/5/5/5/5/5 | Fine. |
| `S1022` | 5/5/5/5/5/5 | Fine. |
| `S1023` | 5/5/5/4/5/4 | Fine. |
| `S1024` | 4/5/5/5/5/5 | Fine. |
| `S1025` | 5/5/5/5/5/5 | Fine. |
| `S1026` | 4/5/5/4/5/4 | Fine. |
| `S1027` | 5/5/5/5/5/5 | Fine. |
| `S1028` | 5/5/5/5/5/5 | Fine. |
| `S1029` | 5/5/5/4/5/4 | Fine. |
| `S1030` | 4/5/5/5/5/4 | Fine. |
| `S1031` | 5/5/5/5/5/5 | Fine. |
| `S1032` | 4/5/4/4/5/4 | Fine. |
| `S1033` | 5/5/5/4/5/5 | Fine. |
| `S1034` | 4/5/5/4/5/4 | Fine. |
| `S1035` **↯** | 4/2/4/4/5/4 | Byte-identical to her before-line; the greenhouse never reaches her mouth. |
| `S1036` **↯** | 4/2/4/4/5/4 | Byte-identical to her before-line. |
| `S1037` **↯** | 5/2/4/4/5/4 | Byte-identical to her before-line; still guarding the spot after her arc says she stopped. |
| `S1038` | 4/5/5/4/5/4 | Fine. |
| `S1039` | 5/5/5/5/5/5 | Fine. |
| `S1040` | 5/5/5/5/5/5 | Fine. |
| `S1041` | 5/5/5/5/5/5 | Fine. |
| `S1042` | 5/5/5/4/5/5 | Fine. |
| `S1043` | 4/5/5/5/5/5 | Fine. |
| `S1044` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1045` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line; the hedge is still the cover story after he stops needing one. |
| `S1046` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1047` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1048` | 5/5/5/4/5/5 | Fine. |
| `S1049` **↯** | 4/3/4/4/5/4 | Repeats element 0's 'look at this rock' joke — two of four before-lines are the same beat. |
| `S1050` | 5/5/5/5/5/5 | Fine. |
| `S1051` | 4/5/5/4/5/4 | Fine. |
| `S1052` | 5/5/5/5/5/5 | Fine. |
| `S1053` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line; Bram's 'good work' never reaches the rock. |
| `S1054` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line; the pink marks are still being dismissed after they were proved right. |
| `S1055` | 5/5/5/5/5/5 | Fine. |
| `S1056` **↯** | 3/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1057` | 5/5/5/4/5/5 | Fine. |
| `S1058` | 5/5/5/4/5/4 | Fine. |
| `S1059` | 4/5/5/5/5/5 | Fine. |
| `S1060` | 4/5/5/5/5/5 | Fine. |
| `S1061` **↯** | 4/3/4/4/5/4 | Repeats element 0's purple-mushroom line almost verbatim inside the same pool. |
| `S1062` | 5/5/5/5/5/5 | Fine. |
| `S1063` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line; the two villages never become one in his greetings. |
| `S1064` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line; still admiring the choice after he has made it. |
| `S1065` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1066` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1067` **↯** | 5/4/4/2/5/4 | Canon break: the duck is Biscuit in Q11's summon, its quest text, JOURNEY.md and the rubric's promise map. |
| `S1068` | 5/5/5/4/5/5 | Fine. |
| `S1069` | 5/5/5/5/5/5 | Fine. |
| `S1070` | 4/5/5/5/5/5 | Fine. |
| `S1071` | 5/5/5/4/5/5 | Fine. |
| `S1072` | 5/5/5/5/5/5 | Fine. |
| `S1073` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line; the duck has a name by then and this line does not use it. |
| `S1074` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line; the exact fact his arc inverts is left standing. |
| `S1075` **↯** | 4/2/4/4/5/4 | Byte-identical to his before-line. |
| `S1076` **↯** | 5/2/4/4/5/4 | Byte-identical to his before-line; the bell payoff never lands in his pool. |

## Ribbits and newcomers — greetings (`story/npcs.json`)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1077` | 4/5/5/4/5/5 | Fine. |
| `S1078` | 4/5/5/4/5/4 | Fine. |
| `S1079` | 5/5/5/4/5/5 | Fine. |
| `S1080` | 4/5/5/4/5/4 | Fine. |
| `S1081` | 5/5/5/5/5/5 | Fine. |
| `S1082` | 4/5/5/4/5/4 | Fine. |
| `S1083` | 5/5/5/4/5/5 | Fine. |
| `S1084` | 5/5/5/4/5/5 | Fine. |
| `S1085` | 5/5/5/4/5/5 | Fine. |
| `S1086` **↯** | 4/3/4/4/5/4 | Opens with Wisp's Q58 sentence word for word — two frog-folk with one mouth. |
| `S1087` | 5/5/5/5/5/5 | Fine. |
| `S1088` | 4/5/5/5/5/5 | Fine. |
| `S1089` | 5/5/5/5/5/5 | Fine. |
| `S1090` | 4/5/5/5/5/5 | Fine. |
| `S1091` | 4/5/5/5/5/5 | Fine. |
| `S1092` | 5/5/5/5/5/5 | Fine. |
| `S1093` | 5/5/5/5/5/5 | Fine. |
| `S1094` | 5/5/5/5/5/5 | Fine. |
| `S1095` | 4/5/5/5/5/5 | Fine. |
| `S1096` | 5/5/5/5/5/5 | Fine. |
| `S1097` | 5/5/5/5/5/5 | Fine. |

## Finale speeches (`valley_finales.js`)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1397` | 5/5/5/5/4/5 | Fine. |
| `S1398` | 5/5/5/5/4/5 | Fine. |
| `S1400` | 4/5/5/5/5/5 | Fine. |
| `S1401` | 5/5/5/5/4/5 | Fine. |
| `S1405` | 4/5/5/5/5/5 | Fine. |
| `S1407` | 4/5/5/5/5/5 | Fine. |
| `S1408` | 4/5/5/5/5/5 | Fine. |
| `S1409` | 4/5/5/5/5/5 | Fine. |
| `S1410` | 4/5/5/5/5/5 | Fine. |
| `S1411` | 5/5/5/5/5/5 | Fine. |
| `S1412` | 5/5/5/5/4/5 | Fine. |
| `S1416` | 4/5/5/5/5/4 | Fine. |
| `S1417` | 4/5/5/5/4/5 | Fine. |
| `S1418` | 5/5/5/5/5/5 | Fine. |
| `S1419` | 5/5/5/5/5/5 | Fine. |
| `S1420` | 5/5/5/5/4/5 | Fine. |

## In-world lines (`valley_core.js`, `valley_checks.js`)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1373` **↯** | 3/3/4/4/5/4 | Reuses her own greeting's opening three words and holds nothing but 'the gate'. |
| `S1374` **↯** | 3/2/4/4/5/3 | A notice, not a person: no verb, nothing withheld, could be any game's error string. |
| `S1375` | 5/5/5/5/5/4 | Fine. |
| `S1376` | 4/5/5/5/5/5 | Fine. |
| `S1377` | 5/5/5/5/5/5 | Fine. |
| `S1379` | 5/4/5/5/5/4 | Fine. |
| `S1380` | 5/5/5/5/5/5 | Fine. |
| `S1382` **↯** | 4/4/5/4/2/4 | 188 chars against a 120-char chat cap, and 'fifteen houses' misreads the counter — fifteen is the population. |
| `S1385` | 5/5/5/5/5/5 | Fine. |
| `S1386` | 5/5/5/5/5/5 | Fine. |
| `S1387` | 5/5/5/5/5/5 | Fine. |
| `S1388` | 5/5/5/5/5/5 | Fine. |
| `S1389` | 5/5/5/5/5/5 | Fine. |
| `S1390` | 4/5/5/4/5/5 | Fine. |
| `S1391` | 4/5/5/5/4/5 | Fine. |
| `S1392` **↯** | 4/4/5/4/2/4 | 163 chars against the cap and repeats the same 'fifteen houses' miscount. |
| `S1393` **↯** | 3/4/5/4/5/3 | 'Level is the whole requirement' is spec-sheet register in a dead woman's mouth. |
| `S1394` | 5/5/5/5/5/4 | Fine. |

## Scene lines (`valley_finales.js` SCENES)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1422` | 5/5/5/5/5/5 | Fine. |
| `S1423` | 5/5/5/5/5/5 | Fine. |
| `S1424` | 5/5/5/5/5/5 | Fine. |
| `S1425` | 4/5/5/5/5/5 | Fine. |
| `S1426` | 5/5/5/5/5/5 | Fine. |
| `S1427` | 5/5/5/4/5/5 | Fine. |
| `S1428` | 5/5/5/5/5/5 | Fine. |
| `S1429` **↯** | 5/4/4/4/5/3 | Triplet then a rule stated instead of shown — 'beds should be made before they get here' explains itself. |
| `S1430` **↯** | 3/3/4/4/3/4 | 127 chars over the cap, and 'exactly as they were' withholds something the player cannot name. |
| `S1431` | 5/5/5/5/5/5 | Fine. |
| `S1432` | 5/5/5/5/5/5 | Fine. |
| `S1433` | 5/5/5/5/5/5 | Fine. |
| `S1434` | 5/5/5/5/5/5 | Fine. |
| `S1436` **↯** | 3/4/4/4/5/3 | 'Story is closed' is author-voice about the player's progress, not Oda's noun. |

## `tellraw` lines (mcfunctions, `town_plan.js`)

| id | P/G/S/C/F/Q | diagnosis |
|---|---|---|
| `S1475` | 4/5/5/5/5/5 | Fine. |
| `S1477` **↯** | 4/3/4/4/5/2 | Banned pattern: 'That is a house. What you do next makes it a home' is the it's-not-X-it's-Y theme summary, and it would fit any game. |
| `S1480` | 5/5/5/5/5/5 | Fine. |
| `S1482` **↯** | 4/3/4/3/5/3 | Repeats the Bram-surveyed-it-twice fact from seconds earlier, then summarises the theme. |
| `S1483` | 4/5/5/5/5/5 | Fine. |
| `S1484` | 5/5/5/5/5/5 | Fine. |
| `S1488` | 5/5/5/5/5/5 | Fine. |
| `S1489` | 5/5/5/5/4/5 | Fine. |
| `S1490` | 5/5/5/5/5/5 | Fine. |
| `S1491` | 5/5/5/5/5/5 | Fine. |
| `S1492` | 5/5/5/5/4/5 | Fine. |
| `S1526` | 5/5/5/5/4/5 | Fine. |
| `S1527` | 5/5/5/5/5/5 | Fine. |

## Structural findings (not per-string, no rewrite in the changes file)

1. **22 of the 33 `greetings_after` lines are byte-identical to a `greetings` line.** Marnie 4, Nella 3, Halden 4, Tobin 3, Wisp 4, Pip 4. `docs/writing-craft.md` §4 makes a changed *fact* the whole definition of an after-line, and §4 of `story-final.md` says the pools exist so the town stops being scenery once you have clicked everyone. Element 0 does the work in every pool; elements 1–4 are the same spring lines the player has read since hour one. All 22 are rewritten.
2. **Pool sizes are inconsistent.** `story-final.md` §4 promises five lines per named resident (headline + four). Actual: Marnie 5/5, Bram **4/2**, Oda **4/2**, Nella 5/**4**, Halden 5/5, Tobin **4**/5, Wisp 5/5, Pip 5/5. Bram and Oda — the two residents the tech player talks to most — carry two after-lines between them. Adding lines is outside a rewrite pass; flagged for Josh.
3. **`npcs.json` is the source; `pack/kubejs/server_scripts/valley_greetings.js` is generated from it** by `tools/scripts/make_npc_presets.py` / the greetings generator. `S1067`'s "I named the duck after you" is live in `valley_greetings.js:120`. Apply the changes to `story/npcs.json`, then regenerate.
4. **`pack/kubejs/data/valley/functions/act5/read1..read5.mcfunction` (`S1488`–`S1492`) is dead text that contradicts a design decision.** The corpus already notes nothing invokes it. Worse than orphaned: it is the Act III cellar wall read aloud at Founder's Day, which `story-final.md` §7 explicitly removed because it closed the pack on *"go and turn it on"* — an instruction to do the thing the player did in the previous act. The prose is good; the fix is deletion, not a rewrite, so it is not in the changes file.
5. **Two "stake too close" lines say the same thing in different words** (`S1382` in `valley_checks.js:176`, `S1392` at `:675`). Both are over the chat cap and both say **"fifteen houses"**, which collides with the one number the player reads all game: fifteen is the *population* on the `valley:folk` bossbar, not a building count. Both rewritten; the wording stays deliberately different because they are different code paths.
6. **Wisp's `S1423` says the reed village is "eleven"** while the residents bossbar reads 12 after Act IV (8 named + 4 Ribbits) and 15 at Founder's Day. Canon allows it — only four Ribbits move in — but it is a fourth distinct "eleven" in a pack where eleven days and eleven years are load-bearing. Left alone; raised here so Josh can decide.
7. **Finale speeches are the strongest text in the slice.** All 16 pass. `S1397`, `S1398`, `S1400`, `S1401`, `S1405`, `S1412` are quoted verbatim in `story-final.md` §7 and `S1416`–`S1420` are byte-locked to `journal/entry_5_the_last_page.json`; none were touched. A few run past the 120-char chat cap (`S1412` at 179, `S1417` at 225) — canon wins over the cap, and they read in one breath per sentence.

## Promise-map spot check (`writing-craft.md` §5)

| Promise | Plant in this slice | Status |
|---|---|---|
| The cellar door | `S1398` Marnie, *"Nobody has ever seen it open."* | present, Act I finale |
| Eleven days, then she put them out | `S1401` Halden, the turbines book | present, Act II finale |
| February and leaving | `S1405` Oda, *"Let's not lose anybody this year."* · `S1095`/`S1097` Mab | present |
| Put the kettle on | `S1412` Oda, Act IV close | present |
| Pip names a duckling Biscuit | `S1067` said the duck was named after the player | **broken — fixed** |
| The bell at Q89 | nothing in Pip's after-pool reached it | **missing — added at `S1076`** |
| Forty lamps | `S1385`, `S1434`, `S1085`, `S1096` | present |

