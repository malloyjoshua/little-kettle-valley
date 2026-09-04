# Text audit — Act IV, Act V and Oda's Counter

Slice: every `quest_title`, `quest_subtitle`, `quest_description`, `task_text` and `reward_text` string in `story/quests/act4.json`, `story/quests/act5.json` and `story/quests/oda.json` — **461 strings**. Rubric: `docs/writing-craft.md`. Canon: `story/story-final.md` §1–3, §4, §6–7.

Scores are **P / G / Sh / C / F / Q** = Picture · Gap · Shape · Causation · Fit · Question, 1–5 each. Anything scoring **under 4 on any criterion** has a paste-ready rewrite in `docs/audit/changes-act4-5-oda.json`, keyed by the same id. A row that reads `Fine.` needs nothing.

**Counts:** 461 scored · 167 flagged · 294 clean (64%).

## What is actually wrong here

The prose is strong — voice, gaps and causation hold up across all three files, and the character lines are the best-written text in the pack. Three systemic faults account for almost every flag:

1. **Length.** 112 of 461 strings are over their §4 cap, and the overruns cluster in the two places that hurt most: quest titles (30 over 45, up to 68) and tech-lane instruction lines (up to 509 against a 240 cap). Line 5 — *what the player will see happen* — is repeatedly used as a second parts list or a recipe card, so the payoff slot never lands a payoff.
2. **Designer vocabulary leaking into player text.** "Wisp's arc closes", "Nella's chain closes", "Stage big_power", "Stage town_provides", "Vibrant Quartz Glass Unlocked", "The Works Deed is signed (Q86)". Fourteen strings tell the player about the *design* instead of the valley, and every one of them sits in the payoff or toast slot where the image should be.
3. **Oda's Counter repeats itself twenty times.** Twenty of the twenty-three shop lines carry the subtitle `<N> Scrip. Restocks.` — the price is already in the title, so the subtitle adds one word and the chapter reads as a single line pasted twenty times. Three shop lines (`oda_coils`, `oda_cat_garden`, `oda_reactor_internals`) got no second clause at all: "Eighteen Scrip.", "Ten Scrip.", "Thirty-five Scrip."

### Two continuity bugs

- **`S0953` (`oda_coils`, available from Q19, Act I)** — "Tobin brings the silver down from the adit in sample bags." Tobin does not arrive until summer (canon §4), and the adit stays collapsed until **Q65 in Act IV**. The line is readable roughly forty quests before either fact is true.
- **`S0941` (`oda_lampoil`, Act I)** — "Josie bought this exact crate every autumn **for eleven years**." Oda's eleven years are the years no wagon came and the shelves were empty (canon §2; her own Q89 line, `S0878`). Josie cannot have been buying crates off that shelf through them.

A third, softer one: **`S0742` (Q77)** has Nella saying *"I grew a tomato before the snow was off the ridge"* in the set-up line — which spends the Winter Tomato before the quest that delivers it (rubric §5, the February payoff Marnie eats standing up). Fixed to future tense.

### Deliberately left alone

- **The spine line** — `S0721`, `S0885`, `S0887`, `S0897` all read *Forty lamps. Fifteen people. One winter that nobody leaves.* Identical in all four places; §5 rule 5 forbids editing one instance without the others, and none of them needs editing.
- **`Standing: Trusted`** (`S0835`) breaks the no-colon title rule, but the string is a game term echoed in Q86's text and in `/valley check standing`. Renaming it means touching a command and another quest; left as canon.
- **Pip naming the boat Biscuit** (`S0811`) after the duckling (Q11) reads as a second use of the joke rather than an error — Pip names everything, and he names the bell Big Copper eight quests later. Flagging it would cost more than it fixes.
- **Q61/Q80 fish** are Muskellunge/Rainbow Trout and Bluegill/Perch/Catfish, where canon §6 says Northern Pike and a six-fish derby. The shipped set is internally consistent across title, description, tasks and toasts; this is a canon-vs-build delta for Josh to rule on, not a text fault.

### The three worst offenders

1. **`S0584`** — Q62 instruction line, **509 characters against a 240 cap**, containing a parenthetical about what Halden would rather you did and a footnote about plain glass bottles. It is the longest string in the slice and the clearest case of a quest explaining itself instead of instructing.
2. **`S0720`** — Q75, the act's last instruction, **414 characters**, of which the back half is a cross-reference table telling the player which `/valley` command belongs to which *other* quest. Wiki voice at the exact moment the Longest Night is supposed to land.
3. **The `oda_*` subtitle block** — twenty strings (`S0920`…`S0996`) that are the same sentence with a different number in it, in the one chapter the player opens most often. Individually trivial, collectively the most boring text in the pack.

## Act IV — The Longest Night

| id | where | chars/cap | P/G/Sh/C/F/Q | diagnosis |
|---|---|---|---|---|
| `S0538` | q57 · title | 43/45 | 5/5/5/5/5/5 | Fine. |
| `S0539` | q57 · subtitle | 24/50 | 5/5/5/5/5/5 | Fine. |
| `S0540` | q57 · desc L1 | 134/140 | 5/5/5/5/5/5 | Fine. |
| `S0541` **⚑** | q57 · desc L3 | 267/240 | 5/5/5/5/2/5 | Over the 240 cap for an instruction line (267). Trimmed the repetitions, kept the instruction verb-first and the closing 'nobody can tell you why'. |
| `S0542` | q57 · desc L5 | 91/140 | 5/5/5/5/5/5 | Fine. |
| `S0543` **⚑** | q57 · task | 39/60 | 5/5/2/5/5/5 | Task text is an order, not a noun phrase describing the finished state (rubric §4). |
| `S0544` | q57 · toast title | 21/24 | 5/4/5/5/5/5 | Fine. |
| `S0545` | q57 · toast body | 64/160 | 5/5/5/5/5/5 | Fine. |
| `S0546` **⚑** | q58 · title | 51/45 | 5/5/5/5/2/5 | Title 51 > 45. Same imperative, same object, same count, six characters under. |
| `S0547` | q58 · subtitle | 38/50 | 5/5/5/5/5/5 | Fine. |
| `S0548` | q58 · desc L1 | 131/140 | 5/5/5/5/5/5 | Fine. |
| `S0549` | q58 · desc L3 | 142/240 | 5/5/5/5/5/5 | Fine. |
| `S0550` | q58 · desc L5 | 88/140 | 5/5/5/5/5/5 | Fine. |
| `S0551` | q58 · task | 36/60 | 5/4/5/5/5/4 | Fine. |
| `S0552` | q58 · task | 36/60 | 5/4/5/5/5/4 | Fine. |
| `S0553` | q58 · task | 35/60 | 5/4/5/5/5/4 | Fine. |
| `S0554` | q58 · task | 33/60 | 5/4/5/5/5/4 | Fine. |
| `S0555` | q58 · toast title | 18/24 | 5/4/5/5/5/5 | Fine. |
| `S0556` | q58 · toast body | 75/160 | 5/5/5/5/5/5 | Fine. |
| `S0557` **⚑** | q59 · title | 48/45 | 5/5/5/5/3/5 | Title 48 > 45. |
| `S0558` | q59 · subtitle | 43/50 | 5/5/5/5/5/5 | Fine. |
| `S0559` | q59 · desc L1 | 97/140 | 5/5/5/5/5/5 | Fine. |
| `S0560` | q59 · desc L3 | 232/240 | 5/5/5/5/5/5 | Fine. |
| `S0561` **⚑** | q59 · desc L5 | 91/140 | 2/5/5/5/5/3 | 'Wisp's arc closes' is designer vocabulary in the line that is supposed to say what the player will SEE. |
| `S0562` | q59 · task | 59/60 | 5/4/5/5/5/4 | Fine. |
| `S0563` | q59 · card sub | 30/40 | 5/5/5/5/5/5 | Fine. |
| `S0564` | q59 · card title | 16/22 | 5/5/5/5/5/5 | Fine. |
| `S0565` **⚑** | q59 · toast title | 25/24 | 5/5/5/5/3/5 | Toast title 25 > 24, and it named the place rather than the change. |
| `S0566` | q59 · toast body | 130/160 | 5/5/5/5/5/5 | Fine. |
| `S0567` | q60 · title | 41/45 | 5/5/5/5/5/5 | Fine. |
| `S0568` | q60 · subtitle | 24/50 | 5/5/5/5/5/5 | Fine. |
| `S0569` | q60 · desc L1 | 119/140 | 5/5/5/5/5/5 | Fine. |
| `S0570` | q60 · desc L3 | 114/240 | 5/5/5/5/5/5 | Fine. |
| `S0571` **⚑** | q60 · desc L5 | 181/140 | 2/5/5/5/2/3 | 181 > 140 and 'Marnie's arc closes' is meta. The image (Marnie sitting down) is the thing that actually happens. |
| `S0572` | q60 · toast title | 23/24 | 5/4/5/5/5/5 | Fine. |
| `S0573` | q60 · toast body | 115/160 | 5/5/5/5/5/5 | Fine. |
| `S0574` **⚑** | q61 · title | 55/45 | 5/5/5/5/2/5 | Title 55 > 45. Counts stay in the subtitle, description and task, which is where the player checks them. |
| `S0575` | q61 · subtitle | 34/50 | 5/5/5/5/5/5 | Fine. |
| `S0576` | q61 · desc L1 | 105/140 | 5/5/5/5/5/5 | Fine. |
| `S0577` **⚑** | q61 · desc L3 | 342/240 | 5/5/5/5/2/5 | 342 > 240. Every fact kept (auger, counts, deep water past the pier, dark ice, worm); |
| `S0578` | q61 · desc L5 | 98/140 | 5/5/5/5/5/5 | Fine. |
| `S0579` **⚑** | q61 · toast title | 28/24 | 5/5/5/5/2/5 | Toast title 28 > 24. |
| `S0580` | q61 · toast body | 68/160 | 5/5/5/5/5/5 | Fine. |
| `S0581` | q62 · title | 44/45 | 5/5/5/5/5/5 | Fine. |
| `S0582` | q62 · subtitle | 38/50 | 5/5/5/5/5/5 | Fine. |
| `S0583` | q62 · desc L1 | 119/140 | 5/5/5/5/5/5 | Fine. |
| `S0584` **⚑** | q62 · desc L3 | 509/240 | 5/5/5/5/1/5 | 509 > 240 — the worst Fit failure in the slice, and the back half was a paragraph of parenthetical hedging. |
| `S0585` **⚑** | q62 · desc L5 | 68/140 | 2/5/5/5/5/3 | 'Halden's arc closes' is meta; his arc closing in-fiction is that he is no longer the only one carrying it (canon §4). |
| `S0586` **⚑** | q62 · toast title | 28/24 | 5/2/5/5/2/5 | Toast title 28 > 24, and the old one stated the outcome instead of showing it. |
| `S0587` | q62 · toast body | 63/160 | 5/5/5/5/5/5 | Fine. |
| `S0588` | q63 · title | 45/45 | 5/5/5/5/5/5 | Fine. |
| `S0589` | q63 · subtitle | 38/50 | 5/5/5/5/5/5 | Fine. |
| `S0590` | q63 · desc L1 | 87/140 | 5/5/5/5/5/5 | Fine. |
| `S0591` | q63 · desc L3 | 132/240 | 5/5/5/5/5/5 | Fine. |
| `S0592` **⚑** | q63 · desc L5 | 90/140 | 2/5/5/5/5/3 | 'Pip's arc closes' is meta in the line that says what the player will see. |
| `S0593` | q63 · toast title | 18/24 | 5/4/5/5/5/5 | Fine. |
| `S0594` | q63 · toast body | 93/160 | 5/5/5/5/5/5 | Fine. |
| `S0595` **⚑** | q64 · title | 57/45 | 5/5/2/5/2/5 | Title 57 > 45 and contained a colon, which §4 forbids in quest titles. |
| `S0596` **⚑** | q64 · subtitle | 66/50 | 5/5/5/5/2/5 | Subtitle 66 > 50. |
| `S0597` | q64 · desc L1 | 91/140 | 5/5/5/5/5/5 | Fine. |
| `S0598` | q64 · desc L3 | 219/240 | 5/5/5/5/5/5 | Fine. |
| `S0599` **⚑** | q64 · desc L5 | 212/140 | 5/5/5/5/1/5 | 212 > 140. The itemised solstice list is repeated verbatim in Q66a's own description, so it is redundant here. |
| `S0600` | q64 · task | 54/60 | 5/4/5/5/5/4 | Fine. |
| `S0601` | q64 · toast title | 24/24 | 5/4/5/5/5/5 | Fine. |
| `S0602` | q64 · toast body | 66/160 | 5/5/5/5/5/5 | Fine. |
| `S0603` **⚑** | q66a · title | 52/45 | 5/5/5/5/2/5 | Title 52 > 45. |
| `S0604` **⚑** | q66a · subtitle | 76/50 | 5/5/5/5/1/5 | Subtitle 76 > 50. |
| `S0605` | q66a · desc L1 | 92/140 | 5/5/5/5/5/5 | Fine. |
| `S0606` | q66a · desc L3 | 194/240 | 5/5/5/5/5/5 | Fine. |
| `S0607` **⚑** | q66a · desc L5 | 75/140 | 2/3/5/5/5/2 | The payoff line described a restock, which is no image at all in the slot reserved for one. |
| `S0608` | q66a · task | 38/60 | 5/4/5/5/5/4 | Fine. |
| `S0609` | q66a · toast title | 18/24 | 5/4/5/5/5/5 | Fine. |
| `S0610` | q66a · toast body | 41/160 | 5/5/5/5/5/5 | Fine. |
| `S0611` | q68a · title | 37/45 | 5/5/5/5/5/5 | Fine. |
| `S0612` | q68a · subtitle | 39/50 | 5/5/5/5/5/5 | Fine. |
| `S0613` | q68a · desc L1 | 98/140 | 5/5/5/5/5/5 | Fine. |
| `S0614` | q68a · desc L3 | 64/240 | 5/5/5/5/5/5 | Fine. |
| `S0615` **⚑** | q68a · desc L5 | 165/140 | 5/5/5/5/2/5 | 165 > 140. The loom and wool are named in Q70a's own instruction line, so cutting them here loses nothing and saves the joke's landing. |
| `S0616` | q68a · toast title | 14/24 | 5/4/5/5/5/5 | Fine. |
| `S0617` | q68a · toast body | 120/160 | 5/5/5/5/5/5 | Fine. |
| `S0618` | q70a · title | 35/45 | 5/5/5/5/5/5 | Fine. |
| `S0619` | q70a · subtitle | 28/50 | 5/5/5/5/5/5 | Fine. |
| `S0620` | q70a · desc L1 | 128/140 | 5/5/5/5/5/5 | Fine. |
| `S0621` | q70a · desc L3 | 183/240 | 5/5/5/5/5/5 | Fine. |
| `S0622` | q70a · desc L5 | 109/140 | 5/5/5/5/5/5 | Fine. |
| `S0623` | q70a · toast title | 15/24 | 5/4/5/5/5/5 | Fine. |
| `S0624` **⚑** | q70a · toast body | 221/160 | 5/5/2/5/2/5 | 221 > 160 and did not open with 'Next:' — the one thing a toast body is for. |
| `S0625` **⚑** | q72a · title | 57/45 | 5/5/5/5/2/5 | Title 57 > 45. |
| `S0626` | q72a · subtitle | 35/50 | 5/5/5/5/5/5 | Fine. |
| `S0627` | q72a · desc L1 | 67/140 | 5/5/5/5/5/5 | Fine. |
| `S0628` | q72a · desc L3 | 204/240 | 5/5/5/5/5/5 | Fine. |
| `S0629` | q72a · desc L5 | 117/140 | 5/5/5/5/5/5 | Fine. |
| `S0630` | q72a · task | 44/60 | 5/4/5/5/5/4 | Fine. |
| `S0631` | q72a · toast title | 19/24 | 5/4/5/5/5/5 | Fine. |
| `S0632` | q72a · toast body | 66/160 | 5/5/5/5/5/5 | Fine. |
| `S0633` | q65 · title | 14/45 | 5/5/5/5/5/5 | Fine. |
| `S0634` **⚑** | q65 · subtitle | 66/50 | 5/5/5/5/2/5 | Subtitle 66 > 50. |
| `S0635` | q65 · desc L1 | 131/140 | 5/5/5/5/5/5 | Fine. |
| `S0636` | q65 · desc L3 | 163/240 | 5/5/5/5/5/5 | Fine. |
| `S0637` | q65 · desc L5 | 132/140 | 5/5/5/5/5/5 | Fine. |
| `S0638` | q65 · task | 49/60 | 5/4/5/5/5/4 | Fine. |
| `S0639` **⚑** | q65 · chat | 224/120 | 5/5/5/5/1/5 | Chat line 224 > 120 and four sentences where §4 allows one. |
| `S0640` **⚑** | q65 · chat | 231/120 | 5/5/5/5/1/5 | Chat line 231 > 120, four sentences. Keeps the deduction, the eleven years and his need for credit. |
| `S0641` **⚑** | q65 · card sub | 46/40 | 5/5/2/5/2/5 | Title-card subtitle 46 > 40 and carried a colon (§4: no punctuation beyond a full stop). |
| `S0642` | q65 · card title | 9/22 | 5/5/5/5/5/5 | Fine. |
| `S0643` | q65 · toast title | 17/24 | 5/4/5/5/5/5 | Fine. |
| `S0644` | q65 · toast body | 149/160 | 5/5/5/5/5/5 | Fine. |
| `S0645` **⚑** | q66 · title | 51/45 | 5/5/5/5/2/5 | Title 51 > 45. |
| `S0646` **⚑** | q66 · subtitle | 53/50 | 5/5/2/5/3/5 | Subtitle 53 > 50, and it restated the title's verb instead of adding a fact. |
| `S0647` | q66 · desc L1 | 88/140 | 5/5/5/5/5/5 | Fine. |
| `S0648` | q66 · desc L3 | 109/240 | 5/5/5/5/5/5 | Fine. |
| `S0649` **⚑** | q66 · desc L5 | 219/140 | 5/5/5/5/1/5 | 219 > 140. The 'six of eight' arithmetic is Q86's own quest text and lands harder there. |
| `S0650` | q66 · task | 42/60 | 5/4/5/5/5/4 | Fine. |
| `S0651` | q66 · toast title | 19/24 | 5/4/5/5/5/5 | Fine. |
| `S0652` | q66 · toast body | 92/160 | 5/5/5/5/5/5 | Fine. |
| `S0653` **⚑** | q67 · title | 60/45 | 5/5/5/5/2/5 | Title 60 > 45. |
| `S0654` | q67 · subtitle | 39/50 | 5/5/5/5/5/5 | Fine. |
| `S0655` | q67 · desc L1 | 118/140 | 5/5/5/5/5/5 | Fine. |
| `S0656` | q67 · desc L3 | 200/240 | 5/5/5/5/5/5 | Fine. |
| `S0657` | q67 · desc L5 | 82/140 | 5/5/5/5/5/5 | Fine. |
| `S0658` **⚑** | q67 · task | 65/60 | 5/5/5/5/3/5 | Task text 65 > 60 and phrased as a past-tense order rather than a finished state. |
| `S0659` **⚑** | q67 · card sub | 52/40 | 5/5/5/5/2/5 | Title-card subtitle 52 > 40. The compression is the point of the reveal. |
| `S0660` | q67 · card title | 20/22 | 5/5/5/5/5/5 | Fine. |
| `S0661` | q67 · toast title | 21/24 | 5/4/5/5/5/5 | Fine. |
| `S0662` | q67 · toast body | 83/160 | 5/5/5/5/5/5 | Fine. |
| `S0663` **⚑** | q68 · title | 53/45 | 5/5/5/5/2/5 | Title 53 > 45. |
| `S0664` | q68 · subtitle | 33/50 | 5/5/5/5/5/5 | Fine. |
| `S0665` **⚑** | q68 · desc L1 | 141/140 | 5/5/5/5/3/5 | 141 > 140. |
| `S0666` | q68 · desc L3 | 100/240 | 5/5/5/5/5/5 | Fine. |
| `S0667` **⚑** | q68 · desc L5 | 152/140 | 5/5/5/5/3/5 | 152 > 140. The 'thirty-two sticks of powder for the pocket' is an item-reward detail the player reads off the payout. |
| `S0668` **⚑** | q68 · toast title | 26/24 | 5/5/5/5/3/5 | Toast title 26 > 24. |
| `S0669` | q68 · toast body | 98/160 | 5/5/5/5/5/5 | Fine. |
| `S0670` **⚑** | q69 · title | 48/45 | 5/5/5/5/3/5 | Title 48 > 45. |
| `S0671` | q69 · subtitle | 47/50 | 5/5/5/5/5/5 | Fine. |
| `S0672` | q69 · desc L1 | 114/140 | 5/5/5/5/5/5 | Fine. |
| `S0673` **⚑** | q69 · desc L3 | 310/240 | 5/5/5/5/2/5 | 310 > 240. All three facts kept: route, the one-for-one smelt, and Josie's word for it. |
| `S0674` | q69 · desc L5 | 68/140 | 5/5/5/5/5/5 | Fine. |
| `S0675` | q69 · toast title | 24/24 | 5/4/5/5/5/5 | Fine. |
| `S0676` | q69 · toast body | 114/160 | 5/5/5/5/5/5 | Fine. |
| `S0677` | q70 · title | 16/45 | 5/5/5/5/5/5 | Fine. |
| `S0678` **⚑** | q70 · subtitle | 84/50 | 5/5/5/5/1/5 | Subtitle 84 > 50 and it was a parts list, which is line 3's job, not the subtitle's. |
| `S0679` **⚑** | q70 · desc L1 | 143/140 | 5/5/5/5/3/5 | 143 > 140. |
| `S0680` **⚑** | q70 · desc L3 | 382/240 | 5/5/5/5/1/5 | 382 > 240. Every item, count and geometry fact preserved; |
| `S0681` **⚑** | q70 · desc L5 | 326/140 | 5/5/5/5/1/5 | 326 > 140. The crate's contents are itemised again in Q71's instruction line; |
| `S0682` | q70 · task | 50/60 | 5/4/5/5/5/4 | Fine. |
| `S0683` | q70 · toast title | 20/24 | 5/4/5/5/5/5 | Fine. |
| `S0684` | q70 · toast body | 72/160 | 5/5/5/5/5/5 | Fine. |
| `S0685` | q71 · title | 40/45 | 5/5/5/5/5/5 | Fine. |
| `S0686` **⚑** | q71 · subtitle | 58/50 | 5/5/5/5/2/5 | Subtitle 58 > 50; command string unchanged. |
| `S0687` | q71 · desc L1 | 119/140 | 5/5/5/5/5/5 | Fine. |
| `S0688` **⚑** | q71 · desc L3 | 494/240 | 5/5/5/5/1/5 | 494 > 240. Every part, count and the RPM figure kept; the paragraph explaining how to open a chat box moves to the subtitle and the task, which both carry /valley check tur... |
| `S0689` | q71 · desc L5 | 80/140 | 5/5/5/5/5/5 | Fine. |
| `S0690` **⚑** | q71 · task | 71/60 | 5/5/5/5/2/5 | Task text 71 > 60; command string unchanged. |
| `S0691` | q71 · toast title | 15/24 | 5/4/5/5/5/5 | Fine. |
| `S0692` | q71 · toast body | 78/160 | 5/5/5/5/5/5 | Fine. |
| `S0693` **⚑** | q72 · title | 57/45 | 5/5/5/5/2/5 | Title 57 > 45, and 'to the town' is Josie's rule, which is the point of the quest. |
| `S0694` | q72 · subtitle | 40/50 | 5/5/5/5/5/5 | Fine. |
| `S0695` | q72 · desc L1 | 122/140 | 5/5/5/5/5/5 | Fine. |
| `S0696` | q72 · desc L3 | 132/240 | 5/5/5/5/5/5 | Fine. |
| `S0697` **⚑** | q72 · desc L5 | 393/140 | 5/5/5/5/1/5 | 393 > 140 — a recipe card in the payoff slot. The recipe is repeated in Q77's own description, where the player needs it. |
| `S0698` | q72 · task | 46/60 | 5/4/5/5/5/4 | Fine. |
| `S0699` | q72 · task | 37/60 | 5/4/5/5/5/4 | Fine. |
| `S0700` **⚑** | q72 · toast title | 29/24 | 5/5/2/5/2/5 | Toast title 29 > 24 and 'Unlocked' is on §3's banned gaming-register list. |
| `S0701` | q72 · toast body | 130/160 | 5/5/5/5/5/5 | Fine. |
| `S0702` | q73 · title | 38/45 | 5/5/5/5/5/5 | Fine. |
| `S0703` **⚑** | q73 · subtitle | 57/50 | 5/5/5/5/2/5 | Subtitle 57 > 50. |
| `S0704` | q73 · desc L1 | 120/140 | 5/5/5/5/5/5 | Fine. |
| `S0705` | q73 · desc L3 | 145/240 | 5/5/5/5/5/5 | Fine. |
| `S0706` **⚑** | q73 · desc L5 | 75/140 | 2/5/5/5/5/3 | 'Bram's arc closes' and 'the lever quest opens' are both designer vocabulary in the payoff line. |
| `S0707` | q73 · toast title | 14/24 | 5/4/5/5/5/5 | Fine. |
| `S0708` | q73 · toast body | 59/160 | 5/5/5/5/5/5 | Fine. |
| `S0709` **⚑** | q74 · title | 52/45 | 5/5/5/5/2/5 | Title 52 > 45; the route is in the instruction line and the task. |
| `S0710` | q74 · subtitle | 36/50 | 5/5/5/5/5/5 | Fine. |
| `S0711` | q74 · desc L1 | 117/140 | 5/5/5/5/5/5 | Fine. |
| `S0712` | q74 · desc L3 | 195/240 | 5/5/5/5/5/5 | Fine. |
| `S0713` | q74 · desc L5 | 62/140 | 5/5/5/5/5/5 | Fine. |
| `S0714` | q74 · task | 55/60 | 5/4/5/5/5/4 | Fine. |
| `S0715` | q74 · toast title | 13/24 | 5/4/5/5/5/5 | Fine. |
| `S0716` | q74 · toast body | 78/160 | 5/5/5/5/5/5 | Fine. |
| `S0717` **⚑** | q75 · title | 51/45 | 5/5/5/5/2/5 | Title 51 > 45. |
| `S0718` | q75 · subtitle | 34/50 | 5/5/5/5/5/5 | Fine. |
| `S0719` | q75 · desc L1 | 130/140 | 5/5/5/5/5/5 | Fine. |
| `S0720` **⚑** | q75 · desc L3 | 414/240 | 2/5/5/5/1/3 | 414 > 240, and the back half was a cross-reference table explaining which /valley command belongs to which other quest — pure wiki voice in the act's last instruction. |
| `S0721` | q75 · desc L5 | 59/140 | 5/5/5/5/5/5 | Fine. |
| `S0722` | q75 · desc L7 | 109/140 | 5/5/5/5/5/5 | Fine. |
| `S0723` **⚑** | q75 · task | 68/60 | 5/5/5/5/2/5 | Task text 68 > 60. |
| `S0724` | q75 · chat | 117/120 | 5/5/5/5/5/5 | Fine. |
| `S0725` | q75 · toast title | 17/24 | 5/4/5/5/5/5 | Fine. |
| `S0726` **⚑** | q75 · toast body | 199/160 | 5/5/2/5/2/5 | 199 > 160 and did not open with 'Next:'. The Scrip and the lantern are item rewards the player already sees. |

## Act V — Founder's Day

| id | where | chars/cap | P/G/Sh/C/F/Q | diagnosis |
|---|---|---|---|---|
| `S0731` **⚑** | q76 · title | 49/45 | 5/5/5/5/3/5 | Title 49 > 45. |
| `S0732` **⚑** | q76 · subtitle | 58/50 | 5/5/2/5/2/5 | Subtitle 58 > 50 and it restated the title's verbs instead of adding a fact. |
| `S0733` | q76 · desc L1 | 112/140 | 5/5/5/5/5/5 | Fine. |
| `S0734` | q76 · desc L3 | 90/240 | 5/5/5/5/5/5 | Fine. |
| `S0735` **⚑** | q76 · desc L5 | 150/140 | 5/5/5/5/3/5 | 150 > 140. |
| `S0736` **⚑** | q76 · task | 75/60 | 5/5/5/5/2/5 | Task text 75 > 60. |
| `S0737` | q76 · chat | 87/120 | 5/5/5/5/5/5 | Fine. |
| `S0738` **⚑** | q76 · toast title | 8/24 | 2/3/5/5/5/2 | 'Year two' has no concrete noun in it and is the only lower-case toast title in the act. |
| `S0739` **⚑** | q76 · toast body | 162/160 | 5/5/5/5/3/5 | 162 > 160. |
| `S0740` **⚑** | q77 · title | 54/45 | 5/5/5/5/2/5 | Title 54 > 45. |
| `S0741` **⚑** | q77 · subtitle | 21/50 | 2/3/5/5/5/2 | 'Nella's chain closes' is designer vocabulary, states no world fact, and gives the player no picture. |
| `S0742` **⚑** | q77 · desc L1 | 104/140 | 5/5/5/2/5/5 | Continuity: the old line has Nella already having grown the tomato, which pre-empts the Winter Tomato payoff the quest is built to deliver (canon §5, Act V). |
| `S0743` **⚑** | q77 · desc L3 | 76/240 | 1/5/5/5/5/5 | The instruction line said 'grow her something out of season' — 'something' scores 0 on Picture and §4 requires every item named in line 3. |
| `S0744` **⚑** | q77 · desc L5 | 258/140 | 5/5/5/5/1/5 | 258 > 140. |
| `S0745` **⚑** | q77 · desc L7 | 157/140 | 5/5/5/5/2/5 | 157 > 140; the crop list moved to the instruction line where it belongs. |
| `S0746` **⚑** | q77 · desc L9 | 132/140 | 2/5/5/5/5/3 | 'her chain closes' is meta and sits directly in front of the best image in the act. |
| `S0747` | q77 · task | 46/60 | 5/4/5/5/5/4 | Fine. |
| `S0748` | q77 · chat | 65/120 | 5/5/5/5/5/5 | Fine. |
| `S0749` **⚑** | q77 · toast title | 20/24 | 2/5/5/5/5/3 | Toast title was designer vocabulary ('chain closes') rather than a thing that happened. |
| `S0750` | q77 · toast body | 44/160 | 5/5/5/5/5/5 | Fine. |
| `S0751` **⚑** | q78 · title | 50/45 | 5/5/5/5/2/5 | Title 50 > 45. |
| `S0752` **⚑** | q78 · subtitle | 48/50 | 5/5/2/5/5/5 | With the shorter title, the old subtitle restated the title's own count; |
| `S0753` | q78 · desc L1 | 73/140 | 5/5/5/5/5/5 | Fine. |
| `S0754` | q78 · desc L3 | 196/240 | 5/5/5/5/5/5 | Fine. |
| `S0755` | q78 · desc L5 | 74/140 | 5/5/5/5/5/5 | Fine. |
| `S0756` **⚑** | q78 · task | 63/60 | 5/5/5/5/3/5 | Task text 63 > 60. |
| `S0757` | q78 · chat | 66/120 | 5/5/5/5/5/5 | Fine. |
| `S0758` | q78 · toast title | 22/24 | 5/4/5/5/5/5 | Fine. |
| `S0759` | q78 · toast body | 74/160 | 5/5/5/5/5/5 | Fine. |
| `S0760` **⚑** | q80 · title | 60/45 | 5/5/5/5/2/5 | Title 60 > 45. |
| `S0761` **⚑** | q80 · subtitle | 18/50 | 2/3/5/5/5/2 | 'The Fishing Derby.' is a label, not a fact the title lacks — no picture, nothing withheld. |
| `S0762` | q80 · desc L1 | 107/140 | 5/5/5/5/5/5 | Fine. |
| `S0763` **⚑** | q80 · desc L3 | 389/240 | 5/5/5/5/1/5 | 389 > 240. Species, counts, times of day, bait and the fallback spot all kept. |
| `S0764` **⚑** | q80 · desc L5 | 51/140 | 2/3/5/5/5/2 | Payoff line was a payment notice with no image — the one line in the quest that could be in any game. |
| `S0765` | q80 · task | 42/60 | 5/4/5/5/5/4 | Fine. |
| `S0766` | q80 · toast title | 17/24 | 5/4/5/5/5/5 | Fine. |
| `S0767` | q80 · toast body | 85/160 | 5/5/5/5/5/5 | Fine. |
| `S0768` | q83 · title | 24/45 | 5/5/5/5/5/5 | Fine. |
| `S0769` | q83 · subtitle | 41/50 | 5/5/5/5/5/5 | Fine. |
| `S0770` | q83 · desc L1 | 139/140 | 5/5/5/5/5/5 | Fine. |
| `S0771` **⚑** | q83 · desc L3 | 472/240 | 5/5/5/5/1/5 | 472 > 240. Both numbers, the command string and the terminal are unchanged; |
| `S0772` **⚑** | q83 · desc L5 | 64/140 | 2/5/5/5/5/3 | 'Stage big_power' prints a raw stage id at the player — wiki voice, and §3 bans that register. |
| `S0773` **⚑** | q83 · task | 78/60 | 5/5/5/5/2/5 | Task text 78 > 60. |
| `S0774` | q83 · chat | 107/120 | 5/5/5/5/5/5 | Fine. |
| `S0775` **⚑** | q83 · toast title | 16/24 | 2/5/5/5/5/3 | Toast title was a raw stage id. |
| `S0776` | q83 · toast body | 59/160 | 5/5/5/5/5/5 | Fine. |
| `S0777` **⚑** | q84 · title | 68/45 | 5/5/5/5/1/5 | Title 68 > 45 — the longest title in the slice, and it was a parts list. |
| `S0778` **⚑** | q84 · subtitle | 23/50 | 2/3/5/5/5/2 | 'Everything, everywhere.' names nothing and would fit any game in the genre. |
| `S0779` | q84 · desc L1 | 35/140 | 5/5/5/5/5/5 | Fine. |
| `S0780` | q84 · desc L3 | 104/240 | 5/5/5/5/5/5 | Fine. |
| `S0781` **⚑** | q84 · desc L5 | 145/140 | 5/5/5/5/3/5 | 145 > 140; the pantry subnet is Q84a's own payoff line. |
| `S0782` **⚑** | q84 · toast title | 26/24 | 5/5/5/5/3/5 | Toast title 26 > 24; also lands Bram's line from the same quest. |
| `S0783` | q84 · toast body | 102/160 | 5/5/5/5/5/5 | Fine. |
| `S0784` **⚑** | q84a · title | 60/45 | 5/5/5/5/2/5 | Title 60 > 45. |
| `S0785` | q84a · subtitle | 33/50 | 5/5/5/5/5/5 | Fine. |
| `S0786` | q84a · desc L1 | 97/140 | 5/5/5/5/5/5 | Fine. |
| `S0787` | q84a · desc L3 | 210/240 | 5/5/5/5/5/5 | Fine. |
| `S0788` | q84a · desc L5 | 96/140 | 5/5/5/5/5/5 | Fine. |
| `S0789` | q84a · task | 48/60 | 5/4/5/5/5/4 | Fine. |
| `S0790` | q84a · toast title | 23/24 | 5/4/5/5/5/5 | Fine. |
| `S0791` **⚑** | q84a · toast body | 168/160 | 5/5/2/5/3/5 | 168 > 160 and did not open with 'Next:'. |
| `S0792` **⚑** | q86a · title | 54/45 | 5/5/5/5/2/5 | Title 54 > 45. |
| `S0793` | q86a · subtitle | 37/50 | 5/5/5/5/5/5 | Fine. |
| `S0794` **⚑** | q86a · desc L1 | 142/140 | 5/5/5/5/3/5 | 142 > 140. |
| `S0795` | q86a · desc L3 | 222/240 | 5/5/5/5/5/5 | Fine. |
| `S0796` | q86a · desc L5 | 135/140 | 5/5/5/5/5/5 | Fine. |
| `S0797` | q86a · task | 33/60 | 5/4/5/5/5/4 | Fine. |
| `S0798` | q86a · task | 48/60 | 5/4/5/5/5/4 | Fine. |
| `S0799` | q86a · toast title | 14/24 | 5/4/5/5/5/5 | Fine. |
| `S0800` | q86a · toast body | 109/160 | 5/5/5/5/5/5 | Fine. |
| `S0801` **⚑** | q79 · title | 47/45 | 5/5/5/5/3/5 | Title 47 > 45. |
| `S0802` | q79 · subtitle | 27/50 | 5/5/5/5/5/5 | Fine. |
| `S0803` | q79 · desc L1 | 125/140 | 5/5/5/5/5/5 | Fine. |
| `S0804` **⚑** | q79 · desc L3 | 378/240 | 5/5/5/5/1/5 | 378 > 240. All eight dishes and all eight names kept, plus the hand-in condition. |
| `S0805` | q79 · desc L5 | 67/140 | 5/5/5/5/5/5 | Fine. |
| `S0806` | q79 · chat | 80/120 | 5/5/5/5/5/5 | Fine. |
| `S0807` | q79 · toast title | 18/24 | 5/4/5/5/5/5 | Fine. |
| `S0808` | q79 · toast body | 105/160 | 5/5/5/5/5/5 | Fine. |
| `S0809` **⚑** | q81 · title | 51/45 | 5/5/5/5/2/5 | Title 51 > 45; both load-bearing names kept. |
| `S0810` | q81 · subtitle | 19/50 | 5/5/5/5/5/5 | Fine. |
| `S0811` | q81 · desc L1 | 103/140 | 5/5/5/5/5/5 | Fine. |
| `S0812` **⚑** | q81 · desc L3 | 293/240 | 5/5/5/5/2/5 | 293 > 240. |
| `S0813` | q81 · desc L5 | 71/140 | 5/5/5/5/5/5 | Fine. |
| `S0814` **⚑** | q81 · card sub | 43/40 | 5/5/5/5/3/5 | Title-card subtitle 43 > 40. |
| `S0815` | q81 · card title | 16/22 | 5/5/5/5/5/5 | Fine. |
| `S0816` | q81 · toast title | 20/24 | 5/4/5/5/5/5 | Fine. |
| `S0817` | q81 · toast body | 45/160 | 5/5/5/5/5/5 | Fine. |
| `S0818` **⚑** | q82 · title | 56/45 | 5/5/5/5/2/5 | Title 56 > 45; Tobin's lanterns are in the subtitle and the instruction. |
| `S0819` **⚑** | q82 · subtitle | 60/50 | 5/5/5/5/2/5 | Subtitle 60 > 50. |
| `S0820` | q82 · desc L1 | 116/140 | 5/5/5/5/5/5 | Fine. |
| `S0821` | q82 · desc L3 | 170/240 | 5/5/5/5/5/5 | Fine. |
| `S0822` **⚑** | q82 · desc L5 | 46/140 | 2/5/5/5/5/3 | 'The deep survey data is what sites the quarry' is a design note in wiki voice, not something the player watches happen. |
| `S0823` | q82 · task | 37/60 | 5/4/5/5/5/4 | Fine. |
| `S0824` **⚑** | q82 · card sub | 49/40 | 5/5/5/5/2/5 | Title-card subtitle 49 > 40. |
| `S0825` | q82 · card title | 17/22 | 5/5/5/5/5/5 | Fine. |
| `S0826` | q82 · toast title | 21/24 | 5/4/5/5/5/5 | Fine. |
| `S0827` | q82 · toast body | 86/160 | 5/5/5/5/5/5 | Fine. |
| `S0828` | q85 · title | 37/45 | 5/5/5/5/5/5 | Fine. |
| `S0829` **⚑** | q85 · subtitle | 19/50 | 2/5/5/5/5/3 | 'Oda's chain closes' is designer vocabulary and adds no fact the title lacks. |
| `S0830` | q85 · desc L1 | 78/140 | 5/5/5/5/5/5 | Fine. |
| `S0831` | q85 · desc L3 | 75/240 | 5/5/5/5/5/5 | Fine. |
| `S0832` **⚑** | q85 · desc L5 | 109/140 | 2/5/5/5/5/3 | 'Oda's chain closes' is designer vocabulary in the payoff line — the balancing books already are the closing. |
| `S0833` | q85 · toast title | 17/24 | 5/4/5/5/5/5 | Fine. |
| `S0834` | q85 · toast body | 57/160 | 5/5/5/5/5/5 | Fine. |
| `S0835` | q86_standing · title | 17/45 | 5/5/5/5/5/5 | Fine. |
| `S0836` | q86_standing · subtitle | 40/50 | 5/5/5/5/5/5 | Fine. |
| `S0837` | q86_standing · desc L1 | 113/140 | 5/5/5/5/5/5 | Fine. |
| `S0838` | q86_standing · desc L3 | 227/240 | 5/5/5/5/5/5 | Fine. |
| `S0839` **⚑** | q86_standing · desc L5 | 183/140 | 5/5/5/5/2/5 | 183 > 140. |
| `S0840` | q86_standing · task | 39/60 | 5/4/5/5/5/4 | Fine. |
| `S0841` | q86_standing · toast title | 17/24 | 5/4/5/5/5/5 | Fine. |
| `S0842` **⚑** | q86_standing · toast body | 150/160 | 5/5/2/5/5/5 | Toast body did not open with 'Next:'; command string unchanged. |
| `S0843` **⚑** | q86 · title | 57/45 | 5/5/5/5/2/5 | Title 57 > 45; the price and the Standing condition are in the subtitle and the instruction line. |
| `S0844` **⚑** | q86 · subtitle | 27/50 | 2/5/5/5/5/3 | 'chains' is designer vocabulary; the price is the fact the shortened title now lacks. |
| `S0845` | q86 · desc L1 | 102/140 | 5/5/5/5/5/5 | Fine. |
| `S0846` | q86 · desc L3 | 174/240 | 5/5/5/5/5/5 | Fine. |
| `S0847` **⚑** | q86 · desc L5 | 228/140 | 5/5/5/5/1/5 | 228 > 140 — an eight-item recap in the slot reserved for what the player will see. |
| `S0848` | q86 · desc L7 | 95/140 | 5/5/5/5/5/5 | Fine. |
| `S0849` | q86 · chat | 75/120 | 5/5/5/5/5/5 | Fine. |
| `S0850` **⚑** | q86 · chat | 220/120 | 5/5/5/5/1/5 | Chat line 220 > 120 and four sentences. Keeps the cellar-wall quote and the deed's real payoff. |
| `S0851` **⚑** | q86 · chat | 183/120 | 5/5/5/5/1/5 | Chat line 183 > 120. |
| `S0852` | q86 · toast title | 14/24 | 5/4/5/5/5/5 | Fine. |
| `S0853` | q86 · toast body | 52/160 | 5/5/5/5/5/5 | Fine. |
| `S0854` | q87 · title | 45/45 | 5/5/5/5/5/5 | Fine. |
| `S0855` **⚑** | q87 · subtitle | 19/50 | 2/5/5/5/5/3 | 'Tobin's arc closes' is designer vocabulary; this is the fact that stops the player mis-placing the rig. |
| `S0856` | q87 · desc L1 | 138/140 | 5/5/5/5/5/5 | Fine. |
| `S0857` | q87 · desc L3 | 172/240 | 5/5/5/5/5/5 | Fine. |
| `S0858` **⚑** | q87 · desc L5 | 122/140 | 2/2/5/5/5/3 | 'his arc closes here' is meta, and the old line explained his state instead of showing it (§3, explaining the feeling). |
| `S0859` **⚑** | q87 · task | 62/60 | 5/5/5/5/3/5 | Task text 62 > 60. |
| `S0860` | q87 · chat | 68/120 | 5/5/5/5/5/5 | Fine. |
| `S0861` **⚑** | q87 · toast title | 18/24 | 2/5/5/5/5/3 | Toast title was designer vocabulary, and it double-books Tobin's closing with Q75's. |
| `S0862` | q87 · toast body | 58/160 | 5/5/5/5/5/5 | Fine. |
| `S0863` **⚑** | q88 · title | 59/45 | 5/5/5/5/2/5 | Title 59 > 45. |
| `S0864` | q88 · subtitle | 15/50 | 5/5/5/5/5/5 | Fine. |
| `S0865` | q88 · desc L1 | 93/140 | 5/5/5/5/5/5 | Fine. |
| `S0866` **⚑** | q88 · desc L3 | 314/240 | 5/5/5/5/2/5 | 314 > 240; every routing rule and the count preserved. |
| `S0867` **⚑** | q88 · desc L5 | 97/140 | 2/5/5/5/5/3 | 'Stage town_provides:' prints a raw stage id at the player. |
| `S0868` | q88 · chat | 98/120 | 5/5/5/5/5/5 | Fine. |
| `S0869` **⚑** | q88 · toast title | 20/24 | 2/5/5/5/5/3 | Toast title was a raw stage id. |
| `S0870` | q88 · toast body | 47/160 | 5/5/5/5/5/5 | Fine. |
| `S0871` **⚑** | q89 · title | 46/45 | 5/5/5/5/3/5 | Title 46 > 45. |
| `S0872` **⚑** | q89 · subtitle | 58/50 | 5/5/5/5/2/5 | Subtitle 58 > 50; the casting instruction is line 3's job. |
| `S0873` | q89 · desc L1 | 72/140 | 5/5/5/5/5/5 | Fine. |
| `S0874` | q89 · desc L3 | 158/240 | 5/5/5/5/5/5 | Fine. |
| `S0875` **⚑** | q89 · desc L5 | 153/140 | 5/5/5/5/3/5 | 153 > 140. |
| `S0876` | q89 · task | 42/60 | 5/4/5/5/5/4 | Fine. |
| `S0877` | q89 · chat | 44/120 | 5/5/5/5/5/5 | Fine. |
| `S0878` **⚑** | q89 · chat | 264/120 | 5/5/5/5/1/5 | Chat line 264 > 120 and five sentences where §4 allows one. |
| `S0879` | q89 · toast title | 14/24 | 5/4/5/5/5/5 | Fine. |
| `S0880` | q89 · toast body | 59/160 | 5/5/5/5/5/5 | Fine. |
| `S0881` **⚑** | q90 · title | 55/45 | 5/5/5/5/2/5 | Title 55 > 45; Josie's porch is in the instruction line and the task. |
| `S0882` | q90 · subtitle | 14/50 | 5/5/5/5/5/5 | Fine. |
| `S0883` | q90 · desc L1 | 106/140 | 5/5/5/5/5/5 | Fine. |
| `S0884` | q90 · desc L3 | 168/240 | 5/5/5/5/5/5 | Fine. |
| `S0885` | q90 · desc L5 | 59/140 | 5/5/5/5/5/5 | Fine. |
| `S0886` | q90 · task | 54/60 | 5/4/5/5/5/4 | Fine. |
| `S0887` | q90 · chat | 59/120 | 5/5/5/5/5/5 | Fine. |
| `S0888` | q90 · chat | 77/120 | 5/5/5/5/5/5 | Fine. |
| `S0889` **⚑** | q90 · card sub | 51/40 | 5/5/5/5/2/5 | Title-card subtitle 51 > 40. |
| `S0890` | q90 · card title | 13/22 | 5/5/5/5/5/5 | Fine. |
| `S0891` | q90 · toast title | 11/24 | 5/4/5/5/5/5 | Fine. |
| `S0892` | q90 · toast body | 79/160 | 5/5/5/5/5/5 | Fine. |
| `S0893` **⚑** | q91 · title | 64/45 | 5/5/5/5/2/5 | Title 64 > 45. |
| `S0894` | q91 · subtitle | 29/50 | 5/5/5/5/5/5 | Fine. |
| `S0895` | q91 · desc L1 | 99/140 | 5/5/5/5/5/5 | Fine. |
| `S0896` **⚑** | q91 · desc L3 | 345/240 | 5/5/5/5/2/5 | 345 > 240. The instruction, the crate, the table and the borrowed trick all kept; |
| `S0897` | q91 · desc L5 | 59/140 | 5/5/5/5/5/5 | Fine. |
| `S0898` | q91 · desc L7 | 40/140 | 5/5/5/5/5/5 | Fine. |
| `S0899` | q91 · toast title | 13/24 | 5/4/5/5/5/5 | Fine. |
| `S0900` | q91 · toast body | 96/160 | 5/5/5/5/5/5 | Fine. |

## Oda's Counter

| id | where | chars/cap | P/G/Sh/C/F/Q | diagnosis |
|---|---|---|---|---|
| `S0905` | oda_open · title | 31/45 | 5/5/5/5/5/5 | Fine. |
| `S0906` | oda_open · subtitle | 36/50 | 5/5/5/5/5/5 | Fine. |
| `S0907` | oda_open · desc L1 | 133/140 | 5/5/5/5/5/5 | Fine. |
| `S0908` **⚑** | oda_open · desc L3 | 221/240 | 5/5/2/5/5/5 | Line 3 must be the instruction, verb first. It was Oda still talking, unquoted, so the point of view slides between line 1 and line 3. |
| `S0909` | oda_open · desc L5 | 78/140 | 5/5/5/5/5/5 | Fine. |
| `S0910` **⚑** | oda_open · desc L7 | 317/140 | 5/5/5/5/1/5 | 317 > 140. |
| `S0911` | oda_open · task | 38/60 | 5/4/5/5/5/4 | Fine. |
| `S0912` | oda_open · chat | 91/120 | 5/5/5/5/5/5 | Fine. |
| `S0913` | oda_open · toast title | 21/24 | 5/4/5/5/5/5 | Fine. |
| `S0914` | oda_open · toast body | 137/160 | 5/5/5/5/5/5 | Fine. |
| `S0915` | oda_standing_order · title | 44/45 | 5/5/5/5/5/5 | Fine. |
| `S0916` | oda_standing_order · subtitle | 14/50 | 5/5/5/5/5/5 | Fine. |
| `S0917` | oda_standing_order · desc L1 | 130/140 | 5/5/5/5/5/5 | Fine. |
| `S0918` **⚑** | oda_standing_order · desc L3 | 161/240 | 5/5/2/5/5/5 | Line 3 was not an instruction; verb-first now, same numbers. |
| `S0919` | oda_casings · title | 33/45 | 5/5/5/5/5/5 | Fine. |
| `S0920` **⚑** | oda_casings · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0921` | oda_casings · desc L1 | 95/140 | 5/5/5/5/5/5 | Fine. |
| `S0922` | oda_casings · desc L3 | 90/240 | 5/5/5/5/5/5 | Fine. |
| `S0923` | oda_alloy · title | 31/45 | 5/5/5/5/5/5 | Fine. |
| `S0924` **⚑** | oda_alloy · subtitle | 18/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0925` **⚑** | oda_alloy · desc L1 | 141/140 | 5/5/5/5/3/5 | 141 > 140. |
| `S0926` | oda_alloy · desc L3 | 69/240 | 5/5/5/5/5/5 | Fine. |
| `S0927` | oda_gearing · title | 31/45 | 5/5/5/5/5/5 | Fine. |
| `S0928` **⚑** | oda_gearing · subtitle | 18/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0929` **⚑** | oda_gearing · desc L1 | 144/140 | 5/5/5/5/3/5 | 144 > 140. |
| `S0930` | oda_gearing · desc L3 | 93/240 | 5/5/5/5/5/5 | Fine. |
| `S0931` | oda_seedbox · title | 26/45 | 5/5/5/5/5/5 | Fine. |
| `S0932` **⚑** | oda_seedbox · subtitle | 18/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0933` | oda_seedbox · desc L1 | 134/140 | 5/5/5/5/5/5 | Fine. |
| `S0934` | oda_seedbox · desc L3 | 71/240 | 5/5/5/5/5/5 | Fine. |
| `S0935` | oda_pantry · title | 31/45 | 5/5/5/5/5/5 | Fine. |
| `S0936` **⚑** | oda_pantry · subtitle | 18/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0937` | oda_pantry · desc L1 | 138/140 | 5/5/5/5/5/5 | Fine. |
| `S0938` | oda_pantry · desc L3 | 60/240 | 5/5/5/5/5/5 | Fine. |
| `S0939` | oda_lampoil · title | 32/45 | 5/5/5/5/5/5 | Fine. |
| `S0940` **⚑** | oda_lampoil · subtitle | 18/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0941` **⚑** | oda_lampoil · desc L1 | 166/140 | 5/5/5/2/2/5 | Continuity plus 166 > 140: the old line has Josie buying from this shop 'every autumn for eleven years', but Oda's own eleven years are the years the wagon stopped coming a... |
| `S0942` | oda_lampoil · desc L3 | 103/240 | 5/5/5/5/5/5 | Fine. |
| `S0943` | oda_servos · title | 44/45 | 5/5/5/5/5/5 | Fine. |
| `S0944` **⚑** | oda_servos · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0945` **⚑** | oda_servos · desc L1 | 173/140 | 5/5/5/5/2/5 | 173 > 140. |
| `S0946` | oda_servos · desc L3 | 103/240 | 5/5/5/5/5/5 | Fine. |
| `S0947` | oda_frames · title | 37/45 | 5/5/5/5/5/5 | Fine. |
| `S0948` **⚑** | oda_frames · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0949` **⚑** | oda_frames · desc L1 | 142/140 | 5/5/5/5/3/5 | 142 > 140. |
| `S0950` | oda_frames · desc L3 | 106/240 | 5/5/5/5/5/5 | Fine. |
| `S0951` | oda_coils · title | 25/45 | 5/5/5/5/5/5 | Fine. |
| `S0952` **⚑** | oda_coils · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0953` **⚑** | oda_coils · desc L1 | 140/140 | 5/5/5/2/5/5 | Continuity: this line is available from Q19 in Act I, but it credits Tobin (who does not arrive until summer) with carrying silver out of the adit (which stays collapsed un... |
| `S0954` **⚑** | oda_coils · desc L3 | 15/240 | 2/3/5/5/5/2 | Bare price line — no noun to see, nothing withheld, no reason to read it. |
| `S0955` **⚑** | oda_fluxduct · title | 46/45 | 5/5/5/5/3/5 | Title 46 > 45; price kept, since every other line on the board carries its price in the title. |
| `S0956` **⚑** | oda_fluxduct · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0957` | oda_fluxduct · desc L1 | 131/140 | 5/5/5/5/5/5 | Fine. |
| `S0958` | oda_fluxduct · desc L3 | 49/240 | 5/5/5/5/5/5 | Fine. |
| `S0959` | oda_cat_furniture · title | 33/45 | 5/5/5/5/5/5 | Fine. |
| `S0960` **⚑** | oda_cat_furniture · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0961` **⚑** | oda_cat_furniture · desc L1 | 155/140 | 5/5/5/5/2/5 | 155 > 140. |
| `S0962` | oda_cat_furniture · desc L3 | 62/240 | 5/5/5/5/5/5 | Fine. |
| `S0963` | oda_cat_windows · title | 43/45 | 5/5/5/5/5/5 | Fine. |
| `S0964` **⚑** | oda_cat_windows · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0965` **⚑** | oda_cat_windows · desc L1 | 155/140 | 5/5/5/5/2/5 | 155 > 140. |
| `S0966` | oda_cat_windows · desc L3 | 54/240 | 5/5/5/5/5/5 | Fine. |
| `S0967` | oda_cat_garden · title | 30/45 | 5/5/5/5/5/5 | Fine. |
| `S0968` **⚑** | oda_cat_garden · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0969` **⚑** | oda_cat_garden · desc L1 | 161/140 | 5/5/5/5/2/5 | 161 > 140. |
| `S0970` **⚑** | oda_cat_garden · desc L3 | 10/240 | 2/3/5/5/5/2 | Bare price line — nothing to see and nothing withheld. |
| `S0971` | oda_cat_lights · title | 32/45 | 5/5/5/5/5/5 | Fine. |
| `S0972` **⚑** | oda_cat_lights · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0973` **⚑** | oda_cat_lights · desc L1 | 157/140 | 5/5/5/5/2/5 | 157 > 140. |
| `S0974` | oda_cat_lights · desc L3 | 85/240 | 5/5/5/5/5/5 | Fine. |
| `S0975` | oda_livestock · title | 34/45 | 5/5/5/5/5/5 | Fine. |
| `S0976` **⚑** | oda_livestock · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0977` | oda_livestock · desc L1 | 133/140 | 5/5/5/5/5/5 | Fine. |
| `S0978` | oda_livestock · desc L3 | 65/240 | 5/5/5/5/5/5 | Fine. |
| `S0979` | oda_rare_seeds · title | 33/45 | 5/5/5/5/5/5 | Fine. |
| `S0980` **⚑** | oda_rare_seeds · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0981` **⚑** | oda_rare_seeds · desc L1 | 167/140 | 5/5/5/5/2/5 | 167 > 140. |
| `S0982` | oda_rare_seeds · desc L3 | 66/240 | 5/5/5/5/5/5 | Fine. |
| `S0983` | oda_reactor_casings · title | 38/45 | 5/5/5/5/5/5 | Fine. |
| `S0984` **⚑** | oda_reactor_casings · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0985` **⚑** | oda_reactor_casings · desc L1 | 216/140 | 5/5/5/5/1/5 | 216 > 140. The 'notes came home from the tower' clause is the dependency talking, and the quest is already gated on Q67. |
| `S0986` | oda_reactor_casings · desc L3 | 124/240 | 5/5/5/5/5/5 | Fine. |
| `S0987` | oda_reactor_internals · title | 43/45 | 5/5/5/5/5/5 | Fine. |
| `S0988` **⚑** | oda_reactor_internals · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0989` **⚑** | oda_reactor_internals · desc L1 | 167/140 | 5/5/5/5/2/5 | 167 > 140. |
| `S0990` **⚑** | oda_reactor_internals · desc L3 | 18/240 | 2/3/5/5/5/2 | Bare price line — no image, no gap, nothing to make the player read the next one. |
| `S0991` | oda_ae_bundle · title | 33/45 | 5/5/5/5/5/5 | Fine. |
| `S0992` **⚑** | oda_ae_bundle · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0993` **⚑** | oda_ae_bundle · desc L1 | 154/140 | 5/5/5/5/3/5 | 154 > 140. |
| `S0994` | oda_ae_bundle · desc L3 | 62/240 | 5/5/5/5/5/5 | Fine. |
| `S0995` | oda_plushie · title | 30/45 | 5/5/5/5/5/5 | Fine. |
| `S0996` **⚑** | oda_plushie · subtitle | 19/50 | 2/3/5/5/5/2 | Twenty shop subtitles are the same sentence with a different number in it, and the price is already in the title, so the subtitle names nothing the player cannot see. |
| `S0997` | oda_plushie · desc L1 | 128/140 | 5/5/5/5/5/5 | Fine. |
| `S0998` | oda_plushie · desc L3 | 44/240 | 5/5/5/5/5/5 | Fine. |
| `S0999` **⚑** | oda_works_deed · title | 46/45 | 5/5/5/5/3/5 | Title 46 > 45; the 150 Scrip is in the subtitle and the instruction line. |
| `S1000` | oda_works_deed · subtitle | 39/50 | 5/5/5/5/5/5 | Fine. |
| `S1001` **⚑** | oda_works_deed · desc L1 | 159/140 | 5/5/5/5/2/5 | 159 > 140. |
| `S1002` | oda_works_deed · desc L3 | 73/240 | 5/5/5/5/5/5 | Fine. |
| `S1003` | oda_works_deed · desc L5 | 134/140 | 5/5/5/5/5/5 | Fine. |
| `S1004` **⚑** | oda_works_deed · task | 30/60 | 2/5/5/5/5/3 | Task text printed a quest id ('(Q86)') at the player — wiki voice in the one line she reads to know what she is waiting on. |
| `S1005` | oda_works_deed · toast title | 19/24 | 5/4/5/5/5/5 | Fine. |
| `S1006` | oda_works_deed · toast body | 66/160 | 5/5/5/5/5/5 | Fine. |
