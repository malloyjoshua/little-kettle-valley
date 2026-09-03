# Story gap analysis — the research vs. `story/story-final.md`

Read alongside `docs/story-research.md`. Every lesson from that document is checked against the story document. Verdicts: **DOES IT** · **PARTIAL** · **GAP**.

**Headline: the story document already implements most of the verified research, and in several places exceeds it.** The lane braid is a stronger version of Create: Arcane Engineering's late-converging tracks; the reward-precedes-ask rule has no precedent in any pack surveyed; §12.3's impossible-mechanics table is more rigorous than anything published by the packs studied. There are **nine real gaps**, and two of them are bugs against the story document's own stated rules.

---

## Framing and voice

### F1 — Name the destination in quest one, in the words the last quest uses · **GAP**
**Bible today.** The tagline names a year and a winter. The first-join screen says: *"Spring, Year One. COPPER KETTLE VALLEY. Open your Quest Book. There is exactly one thing to do."* Q1's task is "read the letter." Each act has its own one-sentence goal. The lamp counter appears at Q7.

Nowhere in hour one does the player learn **the countable thing the pack ends on**. Create: Above and Beyond names the spaceship on its welcome page and ends on the spaceship; that is the single most-copied device in the survey.

**Change.**
1. **First-join subtitle (§2)** — replace *"There is exactly one thing to do"* with the destination line, and use the identical words in Q1's description, in every act header, on the town noticeboard, and at Q90:
   > **Forty lamps. Fifteen people. One winter that nobody leaves.**
2. **Q1 description** — after Josie's line, one plain sentence: *"By the end of the year there are forty lamps lit on the road and fifteen people in the valley. Right now there are none and there is you."*
3. **Q90's text closes the loop verbatim:** *"Forty lamps. Fifteen people. Nobody left."*

Costs three strings. It is the single highest-value change in this document.

### F2 — Voice and instruction in the same quest object · **GAP**
**Bible today.** Quest text is deliberately literal (*"Put the door in the doorway, a window in each hole…"*) and the voice lives in the Patchouli journal — which unlocks **only at act finales** (§10, five `valley:journal/entry_N` advancements). So between finales, Josie is silent, and the quest book — the thing both players actually read — carries instructions with no character in them.

Create: Astral's quest `.snbt` files put narrative description and mechanical task in the same object. That is the pattern.

**Change.** Every quest description gets a **three-part body, in this order**:
1. **One voice line, ≤25 words**, attributed to a named resident or Josie. (`Marnie: "I baked for nobody again. Take the bread before I pretend I didn't."`)
2. **The literal instruction**, unchanged — this is the story document's best asset and must not be diluted.
3. **One line of consequence** — what this unlocks or who it helps.

The journal stays as the long form. It stops being the only form. This is a writer-brief rule, not a structural change: 99 quests × one line.

### F3 — The questbook is the delivery mechanism, not the terrain · **DOES IT**
The story document never claims the anchor system or the curated seed carries story; §3 is explicitly engineering, §10 is explicitly voice. No change.

### F4 — Found, readable objects in the world · **PARTIAL → small GAP**
**Bible today.** Josie's journal (5 entries), the cellar wall (Q55), the chalked door (Q5), Josie's framed blueprint as a decor block, Pip's drawing, four named destinations with loot chests. That is more environmental storytelling than Homestead has — the reviewer's request in the research is already 70% answered.

What is missing is the cheapest tier: **things you find and read that nobody handed you.**

**Change.** Add five `written_book` items as decor, each two paragraphs, each placed by an existing reward — zero new mechanics, zero new quests:
- **Q5 (cellar)** — a ledger page in Josie's hand listing the eleven days the Works ran, dated, with no explanation. Plants the Act III reveal in Act I.
- **Q12 (Bram's crates)** — one crate label, in Bram's father's handwriting, that Bram has never thrown away.
- **Q19 (the store)** — the weathered notice already on Oda's bounty board, made readable: someone advertising for help, eleven years ago, never answered.
- **Q39 (the granary)** — Oda's old stock ledger with her initials scratched off. (The story document already gives the scales; give the book too.)
- **Q65 (the Works)** — Josie's abandoned turbine notebook, with one page torn out. The torn page is what Q67 brings back.

### F5 — Reserve a different register for story beats · **DOES IT**
§7's finales are `tellraw` scenes paced by `/schedule function`, with fireworks, sound cues and NPC teleports — categorically different presentation from ordinary quest text. No change.

### F6 — Quest-reactive NPC dialogue has no off-the-shelf solution on Forge 1.20.1 · **GAP (documentation, not design)**
**Bible today.** §4 says Easy NPC dialog "swaps by KubeJS stage," which is correct and is the right approach. But nothing in §11 or §12.3 records **why** — and the next person to build this will spend an afternoon looking for the compat mod.

**Change.** Add a row to §12.3 (*Impossible mechanics and the substitute that shipped*):

| v1 wanted | Why it can't | What ships instead |
|---|---|---|
| NPC dialogue that reacts to quest state | **EasyNPC × FTB Quests Compat is 1.21.1 Fabric-only** (single release, no Forge, no 1.20.1). Base Easy NPC on Forge 1.20.1 has no FTB Quests integration. | KubeJS reads FTB Quests completion, then swaps the Easy NPC dialog preset on stage grant — the §4 approach, made explicit. Budget it in the custom-code bill. |

And add it to §11's custom-code bill as its own line item, sized alongside the 24 dialog presets.

---

## Pacing and guidance

### P1 — Bounded chapters, own start and end, all summing to one goal · **DOES IT**
Five acts, five finales, five journal entries, per-act one-sentence goals, per-act lamp ledger, per-act border. This is ME^5's architecture with a warmer skin. No change.

### P2 — Confusion is front-loaded · **DOES IT**
Act I is 19 quests in ~120 minutes with: a compass to the house, a pre-placed ruin, a Surveyor's Stake that refuses bad ground, marked tiles for every placement, Megatorches before the first night, exact-count material grants, and no mining. This is the most heavily scaffolded opening in anything surveyed. No change.

### P3 — Long chains want more, smaller quests; not more story · **DOES IT**
The eight interleaved `Qna` beats and the always-available side chapter (Marnie's Menu Board / Pip's Courier Board / Oda's Standing Orders) were added for exactly this. No change.

### P4 — The book must be a complete guide, not a showcase · **DOES IT**
§3's "every task is literal" rule and §12.4's per-quest task/reward table are the opposite of a showcase book. No change.

### P5 — Don't design from download counts · **N/A**
Private pack, no audience. Noted only so nobody later imports "popular pack does X" reasoning.

### P5b — The goal must be re-readable without opening the book · **GAP**
**Bible today.** Two bossbars (lamps, residents) are always visible — excellent. But the **current act's one-sentence goal exists only inside FTB Quests**, and the town noticeboard is not templated until the Act III finale (Q38's reward; §7 Act III lists the noticeboard in the harvest dressing).

The research's control-group packs win on exactly one thing: the answer to "what do I do next" is never more than a glance away.

**Change.** Move the **noticeboard to the Act I finale** (§7, Thaw Fair chain — it is already doing a clear/pad/template pass on the square). Right-clicking it `tellraw`s three lines:
1. The act's one-sentence goal, verbatim from §6.
2. The destination line from F1.
3. *"Kitchen: <current cozy quest title>. Workshop: <current tech quest title>."* — a KubeJS lookup of each lane's lowest incomplete quest.

That last line is the closest we can get to the quest pin §12.3 correctly says we cannot have, and it works for the player who has closed the book and forgotten.

---

## Gating

### G1 — Mechanical gating works without narrative · **DOES IT**
§5's six ingredient gates function whether or not anyone reads the story. No change.

### G2 — Quest count is not story · **DOES IT**
99 quests / 16.4 hours, deliberately cut from 21.5 by deleting grind not content. The pack is not padded. No change.

### G3 — Teach the gate's solution in the book · **GAP, and it is a bug against the story document's own rule**
**Bible today.** §8's constraint #2 is *"The tool always precedes the ask,"* and §8 proudly lists six v1 violations that were fixed. **Two remain, in the two hardest quests in the pack:**

- **Q71 (The Turbine)** — *"A problem, not a recipe… build a turbine that holds 1,800 RPM under load."* Its reward includes **"a tuning page in the journal with Josie's own numbers pencilled in the margin."** The tuning page is the reference material for the puzzle it pays out *after*.
- **Q83 (Reactor, Scaled)** — *"Hit the town's stated winter power budget… without exceeding the fuel burn Tobin signed off on."* Its reward includes **"live energy readout in the journal."** The readout is how you'd know whether you hit the target — delivered after you hit it.

This is Crash Landing's failure mode exactly: a real, learnable gate whose solution is not in the book at the moment it is needed. Two engineers on a Discord call is our version of a 25-page forum thread.

**Change (two-line fix).**
- Move the **tuning page** to **Q70's reward** ("Build the Vessel"). Q71 keeps `reactor_ready` and the lever.
- Move the **live energy readout** to **Q75's reward** (the Act IV finale, which already hands both lanes the next act's opening bill of materials — §7 rule 7). Q83 keeps `big_power` and the augment set.
- Q72 ("route the waste heat to two live consumers") is safe: the six heaters and the bathhouse tank are pre-placed and marked, so the problem is routing, not discovery. No change.

### G4 — Ingredient-visible gating · **DOES IT**
§5: *"the original recipe is removed… a replacement is added that consumes the gate item. JEI/EMI then shows the true path and nobody has to guess."* Better than anything in the survey. No change.

### G5 — A world-level difficulty dial does not solve mismatched co-op · **DOES IT**
The story document never offers one. The lane system plus per-team quest state is the answer, and §9-A's single first-join question (*"the kitchen, or the workshop?"*) is a better version of the idea than Agrarian Skies 2's map-difficulty select. No change.

---

## Rewards

### R1 — Endgame power needs a stated sink · **DOES IT, with an optional strengthener**
Q83 targets *"the town's stated winter power budget"* — a named number, not a bigger number. Q88's `town_provides` makes the quarry restock Oda's store permanently. This is already the fix StoneBlock 3's dev declined to make.

**Optional (§7, Act V finale — Endless Seasons list).** Add one bullet: *"**a rising town load** — every new resident who arrives adds to the winter power budget shown in the journal."* One line, and the reactor never becomes a trophy.

### R2 — Claimable structures for the non-builder · **DOES IT**
§3: *"Every shape is pre-built… The player fits out; she never designs."* Fifteen pre-built shells and pads. Stronger than Cottage Witch's prefab list, because ours are placed in situ rather than chosen from a menu. No change.

### R3 — Permanently available low-stakes activity · **DOES IT**
The always-available side chapter, plus eight interleaved cozy beats in the two acts that had dead zones. No change.

### R4 — "Reward is the shortcut, not the trophy" is ours, unsourced · **NOTE ONLY**
No pack in the survey documents a reward-pacing philosophy. §8 is original work and is the strongest section of the story document. Do not weaken it to match anything found in research; there is nothing to match it to.

---

## Co-op and non-gamer partners

### C1 — State the player count on the tin · **GAP (one sentence)**
**Bible today.** §9 is thorough about teams, second teams, late joiners and absentees, but nothing the player *sees* says what the pack is balanced for. ME^5 does it in one line on its front page.

**Change.** Add to the pack description and to the Q1 quest text footer:
> *Balanced for one or two players. Friends can join at any point in the year — Oda will catch them up.*

That second clause is doing real work: it tells a friend, in advance, that arriving in Act IV is a supported thing (§9-D), not a spoiler.

### C2 — Braided lanes beat late-converging tracks · **DOES IT (exceeds)**
Create: Arcane Engineering's tracks converge once at the end. Ours trade material every third quest, and §8's worked examples 3–5 make the tech lane visibly serve the cozy lane three separate times. No change.

### C3 — An NPC-gated step is a single point of failure · **GAP**
**Bible today.** Pattern P1 (§12.2) makes "talk to X" a token handshake used by **Q12, Q21, Q23, Q27, Q38, Q54, Q73, and both onboarding chapters** — eight blocking quests plus the entire late-joiner path. Residents are `/tp`'d or summoned by finales and carry tags (`npc_marnie`, …). If an NPC despawns, is killed, falls into water, or fails to summon, **there is no documented recovery** — and Farming Valley has a recorded case of exactly this.

**Change.** Two additions:
1. **A self-heal in the `/valley` command tree.** On every P1 quest becoming visible, KubeJS counts entities with that NPC's tag; if zero, or if the nearest is >64 blocks from its mark, re-summon from the stored preset at the mark. Same listener shape as the ~25 already budgeted in §11.
2. **A player-facing escape hatch.** Add `/valley find <resident>` to the command tree — `tellraw`s the resident's coordinates and re-summons if missing. Document it once, in the Q1 quest text footer, in one sentence: *"If you ever can't find somebody, type /valley find and their name."*

### C4 — "Non-gamers only need prettiness" is refuted · **NOTE ONLY**
No change. The story document's premise — that the non-creative player needs a *clear path and cute payoffs* — is the correct read, and the research contains no evidence for the opposite claim.

---

## Endings

### E1 — Scope to what you can finish · **PARTIAL → the most important GAP**
**Bible today.** §11's custom-code bill is nine build steps: the anchor listener, the `/valley` command tree, ~15 custom items and six recipe gates, ~25 KubeJS listeners, **11 hand-built structure NBTs** (§12.2 P8 actually lists 16), ~24 Easy NPC presets, five finale functions, five journal advancements, five Patchouli entries, a Bountiful edit, five Global Loot Modifiers, and 99 quest JSONs. §11 is honest that the NBTs are "the long pole."

Overgrown is the one lesson in the entire research pass that survived verification unqualified: it shipped at ~80% and stopped. Ferret Business shipped for six years and never reached 1.0. Nothing in the story document currently prevents Copper Kettle Valley from becoming either of them.

**Change — add a §11 subsection, "Ship gates":**

1. **Every act finale must read as an ending if the pack stops there.** Add it to §7's universal finale rules as rule 8. It is nearly true already — each finale turns the season, stages a communal scene, pays a journal entry and expands the world — but it must be a stated authoring constraint, not an accident. Concretely: **every finale's last `tellraw` is a line that would work as a last line.** The Act II Float already has one (Nella's *"You all came. Right."*). Act I and Act III need one written deliberately.
2. **Acts I–II ship as v1.0.** No work starts on Act III content until Acts I–II are playable end to end on a fresh world, twice. That is 37 quests, ~285 minutes, two finales, and roughly half the structure NBTs — a complete, satisfying, giftable pack on its own, ending at the Lantern Float with a lit pier and six residents.
3. **A named cut list, written before the build starts.** Order of things to drop if time runs out, decided cold rather than in a panic: (a) the second team / Second Letter chapter, (b) Q81's two named destinations, (c) the Endless Seasons chapter, (d) Act V's three new arrivals. Never cut: a finale, a journal entry, or the fortieth lamp.

### E2 — End on the object you named at the start · **DOES IT, once F1 lands**
Q90 (the fortieth lamp) and Q91 (the Feast) are the destination made physical, and Q90 is deliberately the second-to-last quest. This is Above and Beyond's structure. It only fully works once F1 puts the same words in hour one.

### E3 — A resource ceiling is not an ending · **DOES IT**
The pack ends on a bell, a lamp and eight dishes on a table, not on a tech tier. Endless Seasons explicitly continues *after* the story ends. No change.

### E4 — Silence erodes trust · **N/A**
Two players in one house.

---

## The nine gaps, in build order

| # | Gap | Where | Size |
|---|---|---|---|
| 1 | Destination not named in hour one | §2 first-join, Q1, Q90 | 3 strings |
| 2 | No voice line in quest descriptions | all 99 quests | writer-brief rule |
| 3 | Reward-precedes-ask violated | Q71 → Q70, Q83 → Q75 | 2 line moves |
| 4 | No NPC self-heal / `/valley find` | §12.2 P1, `/valley` tree | 1 listener + 1 command |
| 5 | Every finale must read as an ending | §7 rule 8; Act I + Act III last lines | 1 rule + 2 lines |
| 6 | No Acts I–II ship gate or cut list | §11 new subsection | planning only |
| 7 | Goal not re-readable outside the book | noticeboard → Act I finale | 1 template move + 1 listener |
| 8 | No found readable objects | Q5, Q12, Q19, Q39, Q65 | 5 written books |
| 9 | Easy NPC / FTB Quests compat gap undocumented; player count unstated | §12.3 row, §11 bill, Q1 footer | 3 strings |

Gaps 1, 3 and 5 are the ones that change how the pack plays. Everything else is polish or insurance.
