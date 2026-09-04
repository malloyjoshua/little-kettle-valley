# Text audit — Act I and Act II, letter, chat and title cards

427 strings scored. Slice: every `quest_title`, `quest_subtitle`, `quest_description`, `task_text` and `reward_text` in `story/quests/act1.json` and `story/quests/act2.json`, plus every `letter_page`, `chat_line` and `title_card` in the corpus.

**Score column** is the six rubric criteria in order — **P**icture · **G**ap · **S**hape · **C**ausation · **F**it · **Q**uestion — scored 1-5. Anything under 4 on any criterion has an entry in `changes-act1-2.json`.

**Two scoring calls, stated up front so they can be overruled:**

1. *Fit is measured, not estimated.* A string one character over its §4 cap scores 3 on Fit and gets a trim. That is where most of the 98 changes come from, and most of those trims touch prose that is otherwise excellent — the diagnosis says so when that is the case.
2. *"Chat/tellraw: one sentence" is read as one speaker, one beat, ≤120 characters.* Read literally it would gut lines the rubric itself holds up as models (*"Do not just stand there. Hold this."*). The 120-character cap and the one-speaker rule are enforced strictly; sentence count is not.

---

## Counts

| | |
|---|---|
| Strings scored | **427** |
| Flagged (under 4 on at least one criterion) | **98** |
| Clean, no note | 259 |
| Scored 5 across the board | 70 |
| Failures that are length only | 51 |
| Failures with a content or continuity fault | 47 |

Where the failures live: Act II **55**, Act I **29** (four of those are the shared reward-crate names), building title cards **12**, Josie's letter **1**, the act5 closing function **1**. Act II carries more than twice Act I's fault rate, and almost all of it is one drift: titles, subtitles and toast titles grew into sentences and stopped obeying their caps.

## The three worst offenders

**1. `S0332` — Act II's closing line (`quests[q37].description[6]`).**  
*"...and for the first summer in eleven years, this valley is a place people come back to instead of a place people leave."*  
It summarises the theme, which the rubric bans outright, and it does it in the it's-not-X-it's-Y shape, which the rubric also bans by name. Worse, it is an act-end line: §5 requires those to be a question the player is already holding. Write the question this raises and you get nothing — it has answered itself. Every other act-end beat in the slice lands on an object (six lamps burning, five people in a field that froze in February); this one lands on a moral. Nella spent all of Act II certain nobody would come to her Float, and the line never uses her.

**2. `S0135` and `S0151` — `"Stage: seasoned"` and `"Stage: market_stalls"`.**  
Two reward toasts in Act I show the player a raw KubeJS stage identifier, underscore and all. This is past gaming register and into developer output: it is the name of a variable. They sit directly after two of the warmest beats in the act — Marnie handing over her chair by the oven, and the fair getting its stalls — and the game responds with a config key. Cheapest high-value fix in the slice.

**3. `S0324` — Marnie's eleven-nights line (`quests[q36].rewards[5].command`).**  
The best-written string in Act II and the most broken: 288 characters against a 120-character chat cap, five sentences where the format allows one beat, and it fires immediately after Pip's line with no `/schedule` between them. It is also the load-bearing plant for *"I lit them once. Then I put them out, on purpose"* — so it cannot simply be cut, which is exactly why it needs deciding rather than leaving. The change file trims it to cap and keeps February, eleven nights, the warm soup and *I never asked*; if Josh wants the full line, the right fix is a `/schedule` splitting it into two Marnie tellraws, which is a code change.

*(Runners-up: `S0300`, a 452-character instruction against a 240 cap, and `S0238`, a subtitle that is a word-for-word restatement of its own title.)*

## Continuity findings

**Fixed in the change file:**

- **`S0321` — the paper comes from the wrong person.** Q35's payoff (`S0311`) says *Oda's stockroom sends over all 48 sheets of paper and the torches*. Q36, the very next quest, says *Wisp's payout put all 48 sheets and 24 torches in your bag*. Two quests apart, two suppliers. Oda is right; Wisp's quest is only what triggers it.
- **`S0053` — a rag with your name on it.** Josie posted three letters to relatives she could not name, died four years ago, Marnie has not arrived and Bram has not been met. Nobody in the fiction could have written the player's name on that rag. (FTB also has no player-name substitution token, which is why Q11's duckling stopped being *named after you*.) Changed to a chalk K in her hand.
- **`S0060` — *fifteen houses*.** Fifteen is the people number — eight residents, four Ribbits, three arrivals — and it is half the spine line the pack opens and closes on. Spending it on houses in Q7 costs the payoff more than the sentence gains.
- **`S0333` vs the finale title card.** The Act II toast says *The Midsummer Lantern Float*; `valley_finales.js` puts *The Lantern Float* on screen. Matched.
- **`S1493` vs `S1421`.** The same closing sentence exists twice, one with an em dash and one with a hyphen. Matched to the finale.

**Flagged, not changed — these need a decision or a file outside this slice:**

- **The residents counter does not reconcile with the Act I finale.** Toasts in this slice run `Residents 1/15` (Marnie, Q8), `2/15` (Pip, Q11), `3/15` (Bram, Q12) — named residents only, reaching 4 when Oda opens at Q19. The Act I finale sets the bossbar to **5**, and Q19's own payoff says *five people standing in a square* — which counts the player. The three toasts are self-consistent; the finale is the line that disagrees. §3 says this counter is *not cosmetic* for lamps, and the same argument applies here. Needs one ruling: is the player one of the fifteen or not?
- **The lamp ledger reconciles exactly** across this slice: `S0061`/`S0065` 2/40 → Act I finale 6 → `S0299` Oda counting *six lit, thirty-four dark* → `S0301`/`S0305` 10/40 → Act II finale 12. No action.
- **Eleven days vs eleven nights vs December.** Marnie says *eleven nights* and *middle of a February*; the cellar wall says *eleven days* and *February*; the found ledger page (`b1_ledger_page`) dates the run **Dec 2 through Dec 12**. February and December cannot both be true. Marnie and the wall agree, so the ledger page is the odd one out — but it is the physical artifact the player holds in Act I, and it is outside this slice. Worth one look before ship.
- **All seven Act I promises in rubric §5 are planted where canon says they are:** the forty dark lamps and the *put them out on purpose* line in `LETTER_PAGES[2]`, the cellar door as a lock in the same page, Q5's chalk, Q6's kettle on the hook, Q11's Biscuit, Q15's *the furnace is you*, and Q19's frozen February field. Nothing is missing.

## Structural findings (need code, not text)

- **Two speakers fire twice in a row with no `/schedule`.** `q23.rewards[7]` and `[8]` are both Halden; `q28.rewards[6]` and `[7]` are both Tobin. §4 forbids two lines from one speaker back to back unless a `/schedule` separates them. Both pairs are now individually under the 120-character cap in the change file, but the pacing fault survives until a schedule is added — and merging them is not an option, since reward entries cannot be removed.
- **`S0156` (Q18) stays over cap at 389 characters against 240.** Compressed from 633 with no fact lost and the out-of-world *Act III* reference cut. The residue is real anti-stuck information — the give-it-back mechanic, the three numbered slabs, and the pumpkin-is-an-autumn-crop warning. The right fix is structural: move the pumpkin note into `description[4]`.
- **`S0060` sits in `description[4]` where §4 expects the payoff**, with the real payoff pushed to `[6]`. Q7 is not an act opener, so it should not have a sixth line. Trimmed in place; worth restructuring later.
- **`S1534`-`S1537` are paired locators.** Each crate's `title` and `loot_crate.name` hold the same value in the same object and must be edited together. The four entries in the change file are the two halves of two crates, and they are marked LOW PRIORITY — the rename is cosmetic. First cozy crate lands at Q11 and first tech crate at Q14, so Marnie and Bram are both on screen before their names appear on a reward.

---

## Act I — story/quests/act1.json

| id | kind | score | diagnosis |
|---|---|---|---|
| `S0005` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0006` | quest_subtitle | `5 5 5 5 5 5` | Excellent. |
| `S0007` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0008` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0009` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0010` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0011` | reward_text | `4 3 4 4 5 3` | Toast title is a system label, not an image — 'Journal Entry 1' could be any mod. |
| `S0012` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0013` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0014` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0015` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0016` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0017` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0018` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0019` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0020` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0021` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0022` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0023` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0024` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0025` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0026` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0027` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0028` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0029` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0030` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0031` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0032` | quest_subtitle | `3 3 4 4 5 3` | 'One problem solved' is an abstraction; subtitle must add a fact the title lacks. |
| `S0033` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0034` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0035` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0036` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0037` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0038` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0039` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0040` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0041` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0042` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0043` | quest_description | `5 5 5 5 3 5` | Fine line, 16 over the 140 payoff cap. |
| `S0044` | task_text | `4 4 4 4 5 4` | Second person rather than a pure noun phrase, but it is the clearest way to say 'you are below the floor'. |
| `S0045` | reward_text | `5 4 4 4 3 4` | Title subtitle is 55 against a 40 cap. |
| `S0046` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0047` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0048` | reward_text | `4 4 3 4 3 4` | Body does not open on 'Next:' and runs 3 over 160. |
| `S0049` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0050` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0051` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0052` | quest_description | `4 4 4 4 2 4` | Instruction is 313 against a 240 cap. |
| `S0053` | quest_description | `4 3 4 4 3 4` | Continuity: nobody could have written your name on that rag. |
| `S0054` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0055` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0056` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0057` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0058` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0059` | quest_description | `4 4 4 4 3 4` | 'every building in the pack' breaks the fiction; 280 against a 240 cap. |
| `S0060` | quest_description | `4 4 3 4 2 4` | 'Fifteen houses' collides with the fifteen-people spine; 256 against 140. |
| `S0061` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0062` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0063` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0064` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0065` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0066` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0067` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0068` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0069` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0070` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0071` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0072` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0073` | reward_text | `4 4 4 4 5 4` | Residents 1/15 counts named residents only; the Act I finale sets the bossbar to 5, which includes the player. Self-consistent inside the slice — flagged so the finale ledger can be checked against it. |
| `S0074` | reward_text | `4 4 4 4 3 4` | 183 against the 160 toast cap; parenthesis buries Bram. |
| `S0075` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0076` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0077` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0078` | quest_description | `4 4 4 4 2 4` | Instruction is 335 against a 240 cap. |
| `S0079` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0080` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0081` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0082` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0083` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0084` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0085` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0086` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0087` | quest_description | `4 4 4 4 3 4` | 154 against the 140 payoff cap. |
| `S0088` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0089` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0090` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0091` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0092` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0093` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0094` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0095` | quest_description | `5 4 4 4 3 4` | 180 against 140 — best image in Act I is over cap. |
| `S0096` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0097` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0098` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0099` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0100` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0101` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0102` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0103` | quest_description | `4 4 4 4 3 4` | 142 against 140. |
| `S0104` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0105` | reward_text | `4 4 3 4 5 4` | Toast body does not open on 'Next:'. |
| `S0106` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0107` | quest_subtitle | `4 4 4 4 3 4` | 57 against the 50 subtitle cap. |
| `S0108` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0109` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0110` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0111` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0112` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0113` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0114` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0115` | quest_description | `5 5 5 5 3 5` | Best buried plant in Act I, 181 against a 140 character-line cap. |
| `S0116` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0117` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0118` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0119` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0120` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0121` | reward_text | `4 4 4 4 5 4` | Toast body does not open on 'Next:' — allowed here: Q13a is a leaf quest with no next step. |
| `S0122` | quest_title | `4 4 4 4 3 4` | 48 against the 45 title cap. |
| `S0123` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0124` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0125` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0126` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0127` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0128` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0129` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0130` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0131` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0132` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0133` | quest_description | `5 4 4 5 2 4` | 212 against 140; 'that gate is the furnace' is mod-config register. |
| `S0134` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0135` | reward_text | `2 2 3 3 5 2` | 'Stage: seasoned' is a datapack identifier shown to the player. |
| `S0136` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0137` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0138` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0139` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0140` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0141` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0142` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0143` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0144` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0145` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0146` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0147` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0148` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0149` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0150` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0151` | reward_text | `2 2 3 3 5 2` | 'Stage: market_stalls' is a datapack identifier shown to the player. |
| `S0152` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0153` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0154` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0155` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0156` | quest_description | `4 4 4 4 1 4` | 633 against a 240 cap — the longest instruction in Act I or II by 2.6x. |
| `S0157` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0158` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0159` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0160` | quest_title | `4 4 4 4 3 4` | 52 against the 45 title cap. |
| `S0161` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0162` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0163` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0164` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0165` | quest_description | `5 5 5 5 3 5` | Act I payoff, 169 against 140. |
| `S0166` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0167` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0168` | reward_text | `4 4 3 4 2 4` | 269 against 160, and three clauses of compass UI walkthrough. |
| `S1534` | reward_text | `3 3 4 4 5 3` | 'Cozy Crate' is a name that would work unchanged in any modpack. |
| `S1535` | reward_text | `3 3 4 4 5 3` | Duplicate of S1534 — must change together. |
| `S1536` | reward_text | `3 3 4 4 5 3` | 'Tech Crate' is a name that would work unchanged in any modpack, and 'Tech' is out-of-world. |
| `S1537` | reward_text | `3 3 4 4 5 3` | Duplicate of S1536 — must change together. |
| `S1538` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S1539` | reward_text | `4 4 4 4 5 4` | Fine. |

## Act II — story/quests/act2.json

| id | kind | score | diagnosis |
|---|---|---|---|
| `S0173` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0174` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0175` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0176` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0177` | quest_description | `3 3 3 4 5 3` | 'This is how you meet Wisp' is the narrator commenting on the story. |
| `S0178` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0179` | reward_text | `4 4 4 4 3 4` | Title subtitle 52 against a 40 cap. |
| `S0180` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0181` | reward_text | `3 4 3 4 2 3` | Toast title is a sentence at 30 against a 24 cap; Act I used names. |
| `S0182` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0183` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0184` | quest_subtitle | `3 2 2 4 5 2` | Subtitle repeats the first five words of the instruction verbatim. |
| `S0185` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0186` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0187` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0188` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0189` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0190` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0191` | reward_text | `3 4 3 4 3 3` | Status sentence at 27 against a 24 cap. |
| `S0192` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0193` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0194` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0195` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0196` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0197` | quest_description | `5 5 4 4 3 5` | 187 against 140; the joke is worth keeping. |
| `S0198` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0199` | task_text | `4 4 4 4 5 4` | Fine. |
| `S0200` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0201` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0202` | quest_title | `4 4 4 4 3 4` | 54 against the 45 title cap. |
| `S0203` | quest_subtitle | `3 2 3 4 3 3` | Subtitle restates the title's counts and adds nothing. |
| `S0204` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0205` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0206` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0207` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0208` | reward_text | `5 5 5 5 2 5` | 168 against a 120 chat cap, and Halden speaks twice back to back. |
| `S0209` | reward_text | `3 4 3 4 3 3` | Status sentence at 29 against a 24 cap. |
| `S0210` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0211` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0212` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0213` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0214` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0215` | quest_description | `3 3 3 4 5 3` | 'the wine line' is pipeline jargon and 'Act III' is out-of-world. |
| `S0216` | task_text | `4 4 3 4 3 4` | 62 against the 60 task cap; reads as a sentence, not a finished state. |
| `S0217` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0218` | reward_text | `3 4 3 4 3 3` | Status sentence at 26 against a 24 cap. |
| `S0219` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0220` | quest_title | `4 4 4 4 3 4` | 48 against the 45 title cap. |
| `S0221` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0222` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0223` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0224` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0225` | task_text | `4 4 3 4 2 4` | 73 against the 60 task cap; reads as prose. |
| `S0226` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0227` | reward_text | `4 5 3 4 3 4` | 30 against a 24 cap; the sheep names are the joke. |
| `S0228` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0229` | quest_title | `4 4 4 4 3 4` | 49 against the 45 title cap. |
| `S0230` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0231` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0232` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0233` | quest_description | `4 4 4 4 3 4` | 152 against 140. |
| `S0234` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0235` | reward_text | `4 4 3 4 3 4` | 25 against a 24 cap. |
| `S0236` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0237` | quest_title | `4 4 4 4 3 4` | 51 against the 45 title cap. |
| `S0238` | quest_subtitle | `2 1 1 4 5 1` | Subtitle is a verbatim restatement of the title — zero new information. |
| `S0239` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0240` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0241` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0242` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0243` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0244` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0245` | reward_text | `3 4 3 4 2 3` | Status sentence at 32 against a 24 cap. |
| `S0246` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0247` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0248` | quest_subtitle | `3 2 3 4 5 3` | Subtitle restates the title's count and Tobin's name. |
| `S0249` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0250` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0251` | quest_description | `4 4 4 4 3 4` | 201 against 140. |
| `S0252` | task_text | `4 4 3 4 2 4` | 73 against the 60 task cap. |
| `S0253` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0254` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0255` | reward_text | `5 5 5 5 2 5` | 198 against a 120 chat cap, and Tobin's second line back to back with his first. |
| `S0256` | reward_text | `4 4 3 4 3 4` | 31 against a 24 cap. |
| `S0257` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0258` | quest_title | `4 4 4 4 3 4` | 53 against the 45 title cap. |
| `S0259` | quest_subtitle | `3 2 3 4 5 3` | Subtitle is a near-verbatim copy of the instruction's last sentence. |
| `S0260` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0261` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0262` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0263` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0264` | reward_text | `3 4 3 4 3 3` | Status sentence at 25 against a 24 cap. |
| `S0265` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0266` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0267` | quest_subtitle | `3 1 3 4 5 3` | Subtitle is a word-for-word duplicate of the character line directly under it. |
| `S0268` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0269` | quest_description | `4 4 4 4 3 4` | 251 against a 240 cap. |
| `S0270` | quest_description | `3 3 4 4 3 3` | 'Same result, more fun' is the narrator having an opinion; 160 against 140. |
| `S0271` | quest_description | `4 4 4 4 3 4` | 153 against 140; 'gate item' is recipe-authoring jargon. |
| `S0272` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0273` | reward_text | `4 4 3 4 3 4` | 29 against a 24 cap. |
| `S0274` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0275` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0276` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0277` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0278` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0279` | quest_description | `4 4 4 4 2 4` | 290 against the 140 payoff cap. |
| `S0280` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0281` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0282` | quest_title | `4 4 4 4 2 4` | 59 against the 45 title cap — longest title in the slice. |
| `S0283` | quest_subtitle | `3 2 3 4 5 3` | Subtitle repeats the instruction's closing phrase verbatim. |
| `S0284` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0285` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0286` | quest_description | `3 3 3 4 5 3` | Designer voice — the line explains its own quest ordering to the player. |
| `S0287` | reward_text | `3 4 3 4 3 3` | Status sentence at 25 against a 24 cap. |
| `S0288` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0289` | quest_title | `4 4 4 4 3 4` | 49 against the 45 title cap. |
| `S0290` | quest_subtitle | `3 1 3 4 5 3` | Subtitle is a word-for-word duplicate of Bram's line beneath it. |
| `S0291` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0292` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0293` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0294` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0295` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0296` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0297` | quest_title | `4 4 4 4 3 4` | 53 against the 45 title cap. |
| `S0298` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0299` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0300` | quest_description | `4 4 4 4 1 4` | 452 against a 240 cap — the longest instruction in Act II. |
| `S0301` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0302` | task_text | `4 4 3 4 2 4` | 77 against the 60 task cap. |
| `S0303` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0304` | reward_text | `5 5 5 5 2 5` | 158 against a 120 chat cap. |
| `S0305` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0306` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0307` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0308` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0309` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0310` | quest_description | `4 4 4 4 3 4` | 289 against a 240 cap. |
| `S0311` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0312` | task_text | `4 4 3 4 2 4` | 71 against the 60 task cap. |
| `S0313` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0314` | reward_text | `4 4 4 4 3 4` | Title subtitle 45 against a 40 cap. |
| `S0315` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0316` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0317` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0318` | quest_title | `4 4 4 4 5 4` | Fine. |
| `S0319` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0320` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0321` | quest_description | `4 4 4 4 5 3` | Continuity: credits the paper to Wisp; Q35's own payoff credits Oda's stockroom. |
| `S0322` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0323` | reward_text | `5 5 5 5 5 5` | Excellent. |
| `S0324` | reward_text | `5 5 5 5 1 5` | The best line in Act II, at 288 against a 120 chat cap. |
| `S0325` | reward_text | `3 4 3 4 2 3` | Sentence at 34 against a 24 cap. |
| `S0326` | reward_text | `4 4 4 4 5 4` | Fine. |
| `S0327` | quest_title | `3 4 4 4 2 4` | 57 against a 45 cap, and a colon, which §4 forbids in titles. |
| `S0328` | quest_subtitle | `4 4 4 4 5 4` | Fine. |
| `S0329` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0330` | quest_description | `4 4 4 4 5 4` | Fine. |
| `S0331` | quest_description | `5 5 5 5 5 5` | Excellent. |
| `S0332` | quest_description | `3 2 2 4 3 1` | Act II's closing line summarises the theme instead of ending on an image. |
| `S0333` | reward_text | `4 4 3 4 3 4` | 27 against a 24 cap; disagrees with its own title card. |
| `S0334` | reward_text | `4 4 4 4 5 4` | Fine. |

## Josie's letter, first join and world text — valley_core.js / valley_checks.js

| id | kind | score | diagnosis |
|---|---|---|---|
| `S1364` | letter_page | `5 5 5 5 5 5` | Excellent. |
| `S1365` | letter_page | `5 5 5 5 3 5` | Letter page 234 against a 230 cap. |
| `S1366` | letter_page | `5 5 5 5 5 5` | Excellent. |
| `S1367` | letter_page | `5 5 5 5 5 5` | Excellent. |
| `S1368` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1369` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1370` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1371` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1372` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1378` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1381` | title_card | `4 4 4 4 5 4` | 64 chars, but this renders on the actionbar, not as a title subtitle — the 40-char cap does not apply. |
| `S1383` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1384` | chat_line | `4 4 4 4 5 4` | Fine. |

## Finale title cards, closing lines and /valley operator text — valley_finales.js

| id | kind | score | diagnosis |
|---|---|---|---|
| `S1395` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1396` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1399` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1403` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1404` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1406` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1413` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1414` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1421` | chat_line | `5 5 5 5 5 5` | Excellent. |
| `S1437` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1438` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1439` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1440` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1441` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1442` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1443` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1444` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1445` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1446` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1447` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1448` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1449` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1450` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1451` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1452` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1453` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1454` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1455` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1456` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1457` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1458` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1459` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1460` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1461` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1462` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1463` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1464` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1465` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1466` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1467` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1468` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1469` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1470` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1471` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1472` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1473` | chat_line | `4 4 4 4 5 4` | Fine. |
| `S1474` | chat_line | `4 4 4 4 5 4` | Fine. |

## Building title cards — town_plan.js

| id | kind | score | diagnosis |
|---|---|---|---|
| `S1494` | title_card | `4 5 4 4 3 4` | 48 against a 40 cap. |
| `S1495` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1496` | title_card | `5 5 4 4 3 4` | 41 against a 40 cap. |
| `S1497` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1498` | title_card | `5 5 4 4 3 4` | 46 against a 40 cap. |
| `S1499` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1500` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1501` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1502` | title_card | `4 4 4 4 3 4` | 42 against a 40 cap. |
| `S1503` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1504` | title_card | `5 5 4 4 3 4` | 42 against a 40 cap. |
| `S1505` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1506` | title_card | `4 5 4 4 3 4` | 49 against a 40 cap. |
| `S1507` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1508` | title_card | `5 5 4 4 3 4` | 41 against a 40 cap. |
| `S1509` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1510` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1511` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1512` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1513` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1514` | title_card | `4 4 4 4 3 4` | 41 against a 40 cap. |
| `S1515` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1516` | title_card | `5 5 4 4 3 4` | 50 against a 40 cap. |
| `S1517` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1518` | title_card | `4 4 4 4 3 4` | 51 against a 40 cap. |
| `S1519` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1520` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1521` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1522` | title_card | `4 5 4 4 3 4` | 42 against a 40 cap. |
| `S1523` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1524` | title_card | `4 4 4 4 5 4` | Fine. |
| `S1525` | title_card | `4 4 4 4 5 4` | Fine. |

## Placed-ruin and act5 function text

| id | kind | score | diagnosis |
|---|---|---|---|
| `S1485` | title_card | `5 5 4 4 3 4` | 41 against the 40 title-subtitle cap. |
| `S1486` | title_card | `5 5 5 5 5 5` | Excellent. |
| `S1493` | chat_line | `4 4 4 4 4 4` | Duplicate of the Act V closing tellraw but with a hyphen where the other has an em dash. |

