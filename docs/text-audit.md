# Text audit — Little Kettle Valley

**What this is.** Every player-visible line in the pack got read and scored against `docs/writing-craft.md`. **364 lines are getting rewritten.** The paste-ready list is `docs/audit/changes-final.json` — id, file, locator, exact old string, exact new string, and why. Nothing in it changes a quest key, a dependency, a task, an item id, a count, a coordinate, a command string or a `{placeholder}`.

Five separate passes produced the raw findings (`docs/audit/text-*.md`); this file is the merged result after I removed the collisions, resolved the facts that disagreed between passes, and rewrote the rewrites that were themselves flat.

---

## The short version: what was boring, and why

**1. Half the pack was over its own length limit.** 217 of the 364 lines were past the cap in the rubric — not by a little. One instruction line was 722 characters. Another was 633. Thirteen "here's what you'll see happen" lines were being used as a second parts list, so the payoff slot never paid anything off. **Long lines don't read as detailed, they read as unread** — the player skims to the bold text and misses the actual instruction sitting in the middle.

**2. Developer strings were being shown to the player as rewards.** Right after two of Act I's warmest moments, the reward toast said `Stage: seasoned` and `Stage: market_stalls`. Underscore and all. Later ones said `Stage: big_power` and `Stage: town_provides`. That is the code talking, in the exact spot where a person should be talking.

**3. The town stopped changing after you fixed it.** Every named resident has a "before" line pool and an "after" line pool — the after pool is supposed to fire once their story closes. **22 of the 33 after-lines were byte-identical to a before-line.** Marnie thanked you for the last time in hour one and then said the same four things for the rest of the game. The whole reason those pools exist is so the town is not scenery, and they were doing nothing.

**4. Some lines told the player what the story meant.** Act II closed on "for the first summer in eleven years, this valley is a place people come back to instead of a place people leave." That's the pack explaining its own theme in the one position that's supposed to leave a question open.

**5. A few facts disagreed with each other.** The found ledger page dated Josie's eleven days in **December**. The cellar wall — canon, verbatim — puts them in **February**. Oda's shop credited Tobin with hauling silver out of a mine shaft that is still collapsed at that point in the story. The paper you count wheat with ran its arithmetic backwards. Details like this are the only thing holding a mystery together; when they slip, the mystery reads as sloppy rather than deep.

**6. Twenty shop lines were the same sentence twenty times.** Oda's board — the screen the player opens more than any other — had twenty subtitles reading `<number> Scrip. Restocks.` The price was already in the title above it, so the subtitle added one word.

---

## The 15 biggest improvements

### 1. Act II's last line stopped explaining itself
`story/quests/act2.json` — q37 · **S0332**
- **Before:** "Then everybody walks down to the water and puts the lanterns on it — and for the first summer in eleven years, this valley is a place people come back to instead of a place people leave."
- **After:** "Then everybody walks down to the water and sets the lanterns on it, and Nella stands at the end of the pier counting the people who came."
- **Why:** Nella spent the whole act certain nobody would come. Putting her on the pier counting heads pays that off without saying it. The old version answered its own question, which is the one thing an act-ending line must never do.

### 2. Five reward toasts stopped printing code
`act1/act4/act5.json` — **S0135, S0151, S0700, S0775, S0869**
- `Stage: seasoned` → **"Dry Boards, in April"**
- `Stage: market_stalls` → **"Four Stalls for the Fair"**
- `Vibrant Quartz Glass Unlocked` → **"Glass That Lights Itself"**
- `Stage: big_power` → **"Power for a Quarry"**
- `Stage: town_provides` → **"Shelves Fill Themselves"**
- **Why:** Cheapest high-value fix in the whole audit. Same trigger, same reward, a line a person wrote.

### 3. The ledger page now agrees with the cellar wall
`b1_ledger_page.json` — **S1179 + S1180** *(must ship together)*
- **Before:** "Nov 28 — lit. 31 out… Dec 7 — held. 40/40. Dec 8 — held. **Eleven days.**"
- **After:** "Feb 1 — lit. 31 out… Feb 10 — held. 40/40. Feb 11 — held. **Eleven days.**"
- **Why:** The cellar wall says *"I stood in the lane at ten o'clock at night in February and every lamp on the road was lit."* The one piece of physical evidence in the pack was dated December — so it contradicted the reveal it exists to prove, and it dropped the February that Entry 4 and the Winter Tomato both hang on. Still exactly eleven days, 40/40 still lands on the tenth, nothing else on the page moved.

### 4. Pip's duck got its name back
`story/npcs.json` — **S1067**
- **Before:** "I named the duck after you. Do not be weird about it."
- **After:** "The duck is called Biscuit. I decided it in about one second and I am not changing it."
- **Why:** This line was dead. The quest that summons the duck names it **Biscuit** in code, the quest text says Biscuit, and there is no player-name token in FTB — so "after you" could never render as anything. The rubric hangs a three-plant chain on Biscuit that runs to Founder's Day, and the first link was broken.

### 5. Twenty-two after-lines now carry a changed fact
`story/npcs.json` — **S1013–S1076**
- **Marnie, before and after (identical):** "Sit down. You've got that look people get when they've been carrying something heavy up a hill."
- **Marnie, after:** "I called it my inn this morning. Out loud, to Oda. I did not correct myself."
- **Tobin, after:** "Look at this rock. It is the same rock. I keep it in my pocket now, which Bram says is normal."
- **Pip, after:** "I'm the one who rings the bell. Nobody else rings it. That was the deal and everybody heard it."
- **Why:** These fire only after a resident's story closes. Each one now reports the thing that actually changed — Marnie stops calling it Josie's place, Tobin's marks were right, Pip owns the bell rope.

### 6. Oda's "Eleven" speech kept all three elevens
`act5.json` — q89 · **S0878**
- **Before (264 chars, five sentences):** "Eleven. Eleven days she ran it. Eleven years I kept the book of a shop with nothing in it. Eleven feet of porch, she used to say, and never look at more than that at once. I have stopped believing that is a coincidence and I have stopped needing it not to be."
- **After (120):** "Eleven days she ran it, eleven years I kept an empty book, eleven feet of porch — I have stopped calling it chance."
- **Why:** The first pass said cutting this to the chat cap had to cost "eleven feet of porch" — Josie's whole method, and the callback the Act V beat lands on. It doesn't. The triple and the refusal both fit in exactly 120.

### 7. Marnie's eleven nights, 288 characters down to 118
`act2.json` — q36 · **S0324**
- **Before:** "Josie had the road lit like this once. Middle of a February, out of nowhere. I carried soup up the lane and it was warm the whole way. Eleven nights of it. Then it stopped, and she said the boiler had cracked, and I never asked her one question about it. Pass me the string, love."
- **After:** "Josie lit this road one February — eleven nights, soup warm the whole way up the lane — and I never asked why."
- **Why:** Best-written line in Act II and the most broken — 288 against a 120 chat cap, and it fires back-to-back with Pip's line with no `/schedule` between them. It's also the plant for *"I lit them once. Then I put them out, on purpose,"* so it couldn't just go. February, eleven nights, the warm soup and "I never asked" all survive.

### 8. A rag nobody could have labelled
`act1.json` — q06 · **S0053**
- **Before:** "…wrapped in a rag with your name on it"
- **After:** "…wrapped in a rag with a chalk K on it"
- **Why:** At that point Josie is four years dead, Marnie hasn't arrived and Bram hasn't been met. Nobody in the fiction could have written your name on it — and FTB couldn't render it anyway. Her chalk K keeps the object and loses the impossibility.

### 9. The granary count stopped running backwards
`act3.json` — q44 · **S0400**
- **Before:** "Thirty-two cured meat into the granary — **ninety-one days short** now…"
- **After:** "Thirty-two cured meat into the granary — **ninety-one days covered, twenty-one short** — and Oda has stopped saying the number out loud."
- **Why:** Oda's ledger is 112 days needed. You start at 81 covered and the whole act is spent closing the gap. The old line said the granary got emptier the more you filled it, on the one number the player tracks for a full act.

### 10. Oda stopped describing a mine that hasn't opened
`oda.json` — **S0953**
- **Before:** "Eight coils. Silver and redstone, wound. Tobin brings the silver down from the adit in sample bags and pretends it is not a delivery."
- **After:** "Eight coils. Silver and redstone, wound. Josie ordered a dozen, collected eight, and the other four are still on my books."
- **Why:** This line is readable from Act I. **Tobin doesn't arrive until summer and the adit stays collapsed until Act IV** — roughly forty quests after you can first read it. Moved onto Josie and the ledger, both of which are true on day one.

### 11. Oda's board stopped repeating itself twenty times
`oda.json` — **S0920–S0996**
- **Before, twenty times:** "6 Scrip. Restocks." · "15 Scrip. Restocks." · "40 Scrip. Restocks."
- **After:** "Restocks. The crate Josie bought every autumn." · "Restocks. Bram asks for these by name." · "Restocks. Page eleven, carried since the Supper."
- **Why:** The price is already in the title directly above. Each subtitle now carries one fact you can't get anywhere else, and "Restocks." stays.

### 12. An advancement named the wrong man
`advancements/journal/found_2.json` — **S1253**
- **Before:** "Bram labels everything. Twice."
- **After:** "The hand is not his. He kept it anyway."
- **Why:** The whole point of that crate label is that the handwriting **isn't Bram's** — it's rounder, older, pressed harder into the wood, and Entry 5 confirms it was his father's. The old line named the wrong man and spent the reveal before the page opened. Four sibling advancements also said "Field Note:" while sending the player to a chapter called "Things You Found"; those now say "Found:".

### 13. Four instruction lines came back under the cap
**S0359** (722 → 233) · **S0688** (494 → 230) · **S0584** (509 → 221) · **S0720** (414 → 233)
- **S0720 before, in the Act IV finale:** "…This one is Tobin's signature, not a command: you tick it yourself. `/valley check turbine` belongs to the Turbine Terminal back in Q71, and `/valley check power` to the Reactor Terminal in Act V, once there are two turbines on it."
- **After:** "…then tell Tobin the numbers are good and hand Bram the lever. No command for this one: you tick it yourself."
- **Why:** That was a cross-reference table explaining which command belongs to which *other* quest — wiki voice in the last instruction of the act. Every part, count and command that a player actually needs survived the cuts; I checked each one against the quest it belongs to.

### 14. "Fifteen" went back to being people
`act1.json` q07 + `valley_checks.js` — **S0060, S1382, S1392**
- **Before:** "**Fifteen houses**, a square, a mill and a lakefront go in around this stake…"
- **After:** "Walk until the cottage chimney is small behind you. Stake it in your own dooryard and the square and the mill land on top of the farm."
- **Why:** Fifteen is the population — it's on the bossbar, it's on the Act V signpost, and it's half the spine line the pack opens and closes on. Three separate lines were spending it on buildings before the player ever heard it mean people.

### 15. "Grow her something out of season"
`act5.json` — q77 · **S0743**
- **Before:** "Glaze Nella's cold frame with 16 panes and grow her something out of season."
- **After:** "Glaze Nella's cold frame with 16 Vibrant Quartz Glass, then grow a Tomato, a Strawberry, a Bell Pepper and a Corn under it."
- **Why:** "Something" is the word the rubric scores zero. This is Nella's whole arc closing and the instruction didn't name a single crop. Also fixed alongside it: Nella's set-up line said "I grew a tomato before the snow was off the ridge" in the past tense — spending the Winter Tomato in the quest that's about to deliver it. Now future tense.

---

## Counts

| | |
|---|---|
| Strings in the corpus | 1,545 |
| Scored (five passes; `oda.json` audited twice) | 1,647 |
| Rewrites proposed by the passes | 384 |
| **Rewrites in `changes-final.json`** | **364** |
| Duplicate ids resolved (both passes hit `oda.json`) | 21 |
| Rewrites rejected outright | 1 |
| Rewrites I rewrote again before shipping | 30 |
| New rewrites added by the merge | 2 |
| Characters cut from player-facing text | 8,548 |
| Lines that were over cap before | 217 |
| Lines over cap after | 1 (documented) |
| Entries carrying an apply note | 41 |

**By kind:** quest description 119 · reward text 68 · quest subtitle 53 · quest title 41 · NPC after-greeting 22 · task text 16 · title card 12 · NPC line 10 · advancement 8 · NPC before-greeting 4 · found book 3 · journal 2 · chapter title 2 · sign 2 · letter page 1 · chat line 1.

**By file:** act5 67 · act4 56 · act2 55 · oda 48 · act3 43 · act1 30 · npcs.json 26 · town_plan.js 11 · the rest across `valley_core.js`, `valley_checks.js`, `valley_finales.js`, the Patchouli book, five advancements and three mcfunctions.

### Apply order
1. **`story/npcs.json` first**, then regenerate `valley_greetings.js` and the easy_npc presets — the JSON is the source, the JS is generated.
2. Quest JSON, then recompile: `tools/venv/bin/python tools/scripts/compile_quests.py story/quests pack/config/ftbquests/quests scratch/ids_plus.json --strict`
3. **Paired edits that must land together:** S1179+S1180 (the ledger page), S1534+S1535 and S1536+S1537 (crate name and crate title are the same string in one object).
4. **Eight tellraw entries** flatten "Speaker: body" in the corpus but are two components in the file — replace the body component only, leave the colour and italic keys alone. They're marked `apply_note` in the JSON.

---

## What I deliberately left alone

**Needs your call — I'm not guessing:**

- **The residents counter doesn't reconcile.** Toasts run Residents 1/15 (Marnie), 2/15 (Pip), 3/15 (Bram), reaching 4 at Oda — but the Act I finale sets the bossbar to 5 and Q19's payoff says "five people standing in a square". One ruling needed: **is the player one of the fifteen?** Everything downstream follows from that; I didn't want to bake in an answer.
- **The fish don't match canon.** Q61 uses Muskellunge and Rainbow Trout, Q80 uses Bluegill, Perch and Catfish. Canon says Northern Pike and a six-fish derby. The shipped version is internally consistent across title, subtitle, description, tasks and toasts — so this is a canon-vs-build delta, not a text bug, and changing it touches item ids.
- **`act5/read1..read5.mcfunction`** is the Act III cellar wall read aloud at Founder's Day — the beat canon explicitly removed, because it closes the pack on "go and turn it on", an instruction to do the thing you did last act. The prose is fine; **the fix is deleting the file**, which isn't a rewrite. (One punctuation fix in there is in the list and is harmless either way.)
- **Wisp says "we are eleven"** while the bossbar reads 12 residents after Act IV. Canon-compatible depending on who's counted; same question as the counter above.

**Structure, not words — can't fix in a text pass:**

- **45 of the 90 journal pages are over the 230-char limit.** The journal entries and the cellar wall are canon verbatim and canon beats the rubric; the field notes have their page numbers frozen by their `constraints` field. The real fix is splitting pages, which changes JSON structure and the hard rules forbid it. Flagged, not patched.
- **Nothing in the pack has item lore.** 49 items in `valley_items.js` have a name and a stack size and nothing else. Josie's Letter, the Turbine Notes, the Kettle Plates, the Copper Kettle, the eight tokens — every one of her objects reaches the player's hand with no hand on it. **This is the biggest unwritten surface in the pack**, and it's new writing, not an audit fix.
- **Two pairs of same-speaker tellraws fire back to back** (q23 rewards 7+8, both Halden; q28 rewards 6+7, both Tobin). The rubric forbids it without a `/schedule`. Both are trimmed to cap in the list, but the pacing fault survives until someone adds the schedule.
- **Bram has 4 before-lines and 2 after-lines; Oda has 4 and 2.** Canon says five per named resident. The two people a tech player talks to most have two after-lines between them. Adding lines is out of scope for a rewrite pass.
- **The inn sign** reads "THE INN / kept by / M. Ashcombe" from Act I. Marnie's Act IV beat is that she stops calling it Josie's place — an Act I sign in her hand reading "Josie's place" would pay that off perfectly, but nothing swaps the sign later, so the plant would still be standing uncorrected at Founder's Day. Needs a swap command.

**Protected on purpose:**

- **The spine line** — *"Forty lamps. Fifteen people. One winter that nobody leaves."* — appears in four places, identical. Untouched. The rubric forbids editing one instance without the others, and it's the sentence the whole pack rhymes with.
- **The six finale speeches quoted verbatim in canon** and the five lines locked to Entry 5. All sixteen finale speeches scored clean anyway.
- **"Standing: Trusted"** breaks the no-colon rule but it's a game term echoed in `/valley check standing`; renaming it touches a command.
- **Item display names** like Kettle Plate A/B and Plushie Token — referenced from quest text in other acts.
- **`docs/BOUNTIES.md` and the Bountiful pools** contain no prose at all — pure item data, no lang keys. There was nothing to audit there; the standing-order writing lives in `oda.json`, which is covered.

---

## One judgement call worth knowing about

The rubric says chat and tellraw lines are **one sentence**. Read literally that would gut lines the rubric itself holds up as models — including Oda's "Eleven" speech above. All three quest passes read it as **one speaker, one beat, ≤120 characters**, and I kept that reading in the merge. If you want it literal, that's a separate ~20-line pass and some of those lines will get worse.
