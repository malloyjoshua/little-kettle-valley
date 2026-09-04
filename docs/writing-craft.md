# The Little Kettle Valley writing rubric

How every line in this pack gets written and how an auditor checks it. Research behind it: `docs/research/writing-sentence.md`, `writing-structure.md`, `writing-game.md`. Canon behind it: `story/story-final.md`, `docs/JOURNEY.md`. Where this file and canon disagree, canon wins.

Hard rules that override everything below: a quest description's first instruction sentence stays an instruction; book pages stay under ~230 characters; chat and tellraw lines stay one sentence; quest keys, deps, tasks, item ids, counts, coordinates, command strings and `{x} {y} {z} {team}` placeholders never change; no death, no timers, no fail states.

---

## 1. The voice of the valley

**Josie Kettle** — dead, chalk and paper, grey. Writes to one named person at a time and knows she is being read after her death, which is why she is funny about it. Practical imperatives, one dry joke per page placed *after* the hard sentence, never inside it. She states costs plainly ("I was seventy-one. If I'd died in the spring — and I nearly did"). She never names a feeling; she names a number, an object, or a time of night. Test: could this sentence be a to-do list item written by someone who loves you? If not, it isn't Josie.

**The residents** — each has one obsession and answers sideways from it. Marnie feeds you instead of asking how you are. Bram talks about the shaft. Oda talks about the book. Halden changes the subject. Tobin explains the rock badly. Wisp's sentences are slightly wrong. Pip names things. Nella undersells. Nobody says what they want; they say what they are holding. Test: strip the name off the line — can you still tell who said it?

**The narrator in quest text** — has no personality and no opinions. It says what to do, where, with which item, and what will visibly happen. It never comments on the story, never says "now that you've", never congratulates. Warmth in quest text comes from the character line above the instruction and the rendered payoff below it, never from the narrator's tone.

**Register for all three:** short concrete nouns, present tense, second person, contractions, British-inflected plain speech. Tension comes from what is withheld and from the calendar. Never from danger.

---

## 2. The scoring card

Six criteria. Score each line 0 (fails), 1 (passes), 2 (does real work). **Ship at 9/12 with no zeros.** Any zero is a rewrite, not a note.

| # | Criterion | The one-line test |
|---|---|---|
| 1 | **Picture** | Does the line contain one concrete noun the player can see in the world — a kettle, a shaft, a loaf, the third lamp post? "Things," "stuff," "the house," "the situation" score 0. |
| 2 | **Gap** | Is there something unsaid — a feeling and an action that don't match, or an answer to a different question than the one asked? If the line states its own emotion, score 0. |
| 3 | **Shape** | Does the quest's first sentence tell me exactly what to do, and the last sentence make me want to? For non-quest text: does it open on a fact and close on an image? |
| 4 | **Causation** | Can you put "but" or "therefore" between this line and the next? If only "and then" fits, score 0. |
| 5 | **Fit** | Is it inside its format's cap in §4, and does it read aloud in one breath per sentence? Count the characters; don't estimate. |
| 6 | **Question** | Does it end on an image or an open question rather than a summary? For an act-end line: can you write the question it raises in one sentence? If not, score 0. |

**Audit sweep, in this order:** (a) run the character counts; (b) grep the banned list; (c) read every act-end line aloud and write its question in the margin; (d) check every NPC's before/after pair changes a *fact*, not just a mood; (e) walk §5 and confirm each plant is still in the file it claims to be in.

---

## 3. Banned

**Phrases.** "A testament to." "A reminder that." "Little did you know." "Now more than ever." "The heart of the valley." "Together, you can." "It's not about X, it's about Y." "Something magical." "The true meaning of." "Warmth filled the room." Any sentence containing "community" or "resilience."

**Patterns.**
- *Explaining the feeling.* "Marnie was moved." Show the plate she sets down twice.
- *Summarising the theme.* Any line that tells the player what the act meant. The act meant it already.
- *Triplets of adjectives.* "cold, dark and empty." Two, or one, or a list of nouns.
- *Even rhythm.* Four sentences of the same length in a row. Read aloud; if it thumps, break one.
- *Everything wrapped up.* A page that answers every question it raises. Leave one door shut.
- *And-then chains.* Beats connected by sequence instead of cause.
- *Adverbs on verbs.* "said quietly," "walked slowly." Fix the verb.
- *Decorated dialogue tags.* "exclaimed," "interjected," any exclamation mark outside Pip's mouth.
- *Filler openers.* "Well," "So," "Ah," "Of course," "You know," "Indeed."
- *Second-person emotional instructions.* "Take a moment to appreciate." Never tell the player how to feel about a thing she is looking at.
- *Confusion sold as mystery.* If the player can't name what is being withheld, it isn't a hook.
- *Threat language.* "before it's too late," "running out of time," "if you fail." No line in this pack implies a deadline or a loss.
- *Gaming register.* "unlock," "tier," "progression," "grind," "OP," "endgame" in any player-facing text.

**Names.** Any name that would work unchanged in another story. "The Farm," "The Reactor," "The Festival." Ours are load-bearing: the Kettle farm, the cellar door, forty lamps, the Lantern Road, the Thaw Fair, the Longest Night.

---

## 4. Rules and caps by text kind

Counts are characters unless stated. Caps are ceilings, not targets.

| Kind | Cap | Rules |
|---|---|---|
| **Quest title** | 45 | Imperative naming the real object: *Put the Waystone on the Hearthstone*. No colons, no articles-only titles, never a mod name. |
| **Quest subtitle** | 50 | One clause that adds a fact the title doesn't have: *The last page is a map.* Never restate the title's verb. This line is protected on all 126 quests — it is the first thing to die at quest 90 and the last thing allowed to. |
| **Quest description** | 5 lines, fixed | Line 1: `Name: "one or two sentences"` ≤ 140, in character, with a gap in it. Line 2: blank. Line 3: the instruction — verb first, second person, every item and place named, ≤ 240. Line 4: blank. Line 5: what the player will see happen, ≤ 140. Act openers may carry the spine line as a sixth. Never invert lines 1 and 3. |
| **Task text** | 60 | A noun phrase describing the finished state, not an order: *Door, two windows, bed and sconce placed.* |
| **Reward toast** | title 24 · body 160 | Body starts "Next:" and holds at most three short clauses, each one new fact. Read it in one breath or cut a clause. |
| **Chat / tellraw** | 120 | One sentence. One speaker per line. Colour from the §4 palette in canon. Never two lines from the same speaker back to back unless a `/schedule` separates them. |
| **Title card** | title 22 · subtitle 40 | Title is a name (*The Longest Night*), subtitle is a time or a fact (*Spring, Year One.*). No verbs, no punctuation beyond a full stop. |
| **Book page** | 230 · ≤ 2 blank lines | One idea per page. A page ends on an image or a hook, never mid-list. Bold at most one phrase. |
| **Journal entry** | 3–6 pages | Opens on a scene, not a topic. Contains exactly one joke, placed after the hardest sentence. Handwriting gets shakier and plans get *more* ambitious. Ends on an instruction or an image; never on "and that's why." |
| **NPC greeting (before)** | 140 | Written as one half of a pair. States the obsession sideways. Element 0 of the pool is the headline line. |
| **NPC greeting (after)** | 140 | Same voice, same cadence, **a changed fact** — Bram before: *"Do not just stand there. Hold this."* After: *"Wheel is turning. Sixty years I waited."* If only the mood changed, it fails. Named residents carry 5; Ribbits and newcomers 2–3. |
| **Finale speech** | ≤ 5 lines | One sentence each, one speaker each, `/schedule`d apart. Line 1 names what just happened; the last line points at the next act as a question or an arrival, never as a summary. |
| **Item lore** | 2 lines × 50 | A fact about the owner or the making, never the stats: *Her initials scratched off. Yours scratched on.* |
| **Noticeboard / signpost** | 4 lines × 15 | Reads as something a resident wrote and nailed up. Counts and names only. |

---

## 5. The journey map — promises and where they land

Act I makes seven promises. Every one is countable or physical, and every one pays off on screen. An auditor's job is to confirm each row's plants still exist in the files named in canon.

| Promise (Act I) | Plant 2 | Plant 3 | Payoff |
|---|---|---|---|
| **"Forty lamp posts stand along the road and not one is lit."** (letter p3) | The lamp bossbar reconciles: 2 → 6 → 10 → 12 → 22 | Q74 lights 39 and leaves **one post bare on purpose** | Q90, the fortieth on Josie's own porch; Entry 5's P.S. read aloud at Founder's Day |
| **"There is a door in the cellar… It is not a riddle. It is a lock."** (letter p3) | Q5's chalk: *"Not yet. — J.K."* | Act I ends on Marnie: *"Nobody has ever seen it open."* | Q54 the door turns a quarter; Q55 the wall |
| **"I lit them once. Then I put them out, on purpose."** (letter p3) | Entry 3: *"I bought a book about turbines."* | Act II ends on Halden: *"I laughed at her. I would very much like that back."* | Q55: eleven days, and why she stopped |
| **"The valley only ever needed one person to start."** (Entry 1) | The braid — Q15's boards unblock Q16 before anyone has mined | Q52's second terminal, Q53's Delivery Crate: his build shortens her chores | Q55 inverts it: *"A machine that one person can run is not infrastructure. It's a hostage."* → *"I waited for two of you."* |
| **"Every February for a decade, somebody has packed up and left."** (premise) | Entry 4: *"People leave in February and they do not come back in April."* | Act III ends on Oda: *"That's the last warm night. Let's not lose anybody this year."* | Q77's Winter Tomato, in February, which Marnie eats standing up; then Tess, Mab and Corin walking up the High Street |
| **"Put the kettle on."** (letter p4) | Q6 hangs the copper kettle over the first fire | Act IV ends on Oda: *"Nobody has walked IN to this valley in eleven years. Put the kettle on."* | The Copper Kettle trophy over the player's own hearth, Act V |
| **Pip names a duckling Biscuit** (Q11) | Q57: Pip is the one who notices the Hearth has gone out | Entry 5: *"Put a bell there, and ring it when supper's ready."* | Q89 Pip casts and rings the bell; Founder's Day line four lands on it |

**Rules this map enforces.**
1. Every major reveal carries **three plants before its payoff**, in three different acts and at least two different text kinds (a page and an NPC line, never two notes).
2. Nothing is ever carried by a note alone — every found text is paired with an object (the Kettle Plate, the chalk, the bare post) or a resident who will mention it later.
3. Each act closes one small deduction on its own, so the whole picture only assembles in the player's head at Founder's Day.
4. Each act-end line is a **question the player is already holding**, never a threat. Write the question in the margin; if you can't, the hook isn't sharp.
5. The last words echo the first: the pack opens on a copper kettle over a cold hearth and closes on forty lit lamps and Josie telling you to go and meet the next stranger. The spine line — *Forty lamps. Fifteen people. One winter that nobody leaves* — is said as a promise in Act I and lands as a fact in Act V, same words, opposite weight. Never edit one instance of it without the other.

**Seeding check before any act ships:** for each promise above, name the file and line of all three plants. A missing plant is a bug of the same severity as a broken dependency.
