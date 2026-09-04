# Game Writing Specifics — Research for Little Kettle Valley

Scope: how acclaimed games and modpacks actually deliver text at the sentence and paragraph level — quest lines, item lore, letters, NPC barks, UI copy, humor, and naming — with a before/after in Little Kettle Valley's own register for each principle. "Before" examples are illustrative wiki-speak, not pulled from the pack; the pack's real voice (Josie's letter, Act I quest text) is the "after" target throughout.

---

## 1. Quest text reads as story, not a wiki

**Principle:** the first sentence of a quest is always the instruction — what to do, in plain verbs — and everything else (character voice, stakes, flavor) is built around it, never in front of it. E.M. Welsh's guide to writing a first game quest treats a quest like a short story with a clear start and end, built collaboratively between writer and designer, but the player-facing text still has to function as a set of steps first.

**Why it works:** a quest is read at the exact moment a player wants to know what to do next — under-communicating the objective breaks flow and drives players to a wiki, which permanently exits the story register. Voice and lore have to ride on top of clarity, not replace it. This is also why Blightfall's fans single out its writing: the pack's quests "assist the player in progressing by learning about the various mods included" — function first — while the framing narrative (colonists, a Taint-covered planet) is the thing readers remember afterward.

**Before (wiki-speak, hypothetical):**
> This quest requires you to construct a waystone and configure it at the designated hearthstone location in order to establish your home base.

**After (Little Kettle Valley's actual register — Act I, q02):**
> Josie: "The hearthstone is the one thing in that house I never had to fix. Start from the part that held."
>
> Follow the lit path from where you woke up to the old farm — the chimney is still standing. Place the Homestead Waystone on the flat grey hearthstone beside it, type Home in the box, click the tick.
>
> The roof and the walls go back up around you, with a doorway, two window holes and a wool mat where the bed goes.

Note the shape: character line for hook and subtext, blank line, then the instruction in second person with concrete verbs, blank line, then a payoff sentence that describes what the player will see happen. The instruction is never buried after the lore.

**Source:** E.M. Welsh, ["How to Write Your First Video Game Quest"](https://www.emwelsh.com/blog/video-game-writing-guide); "Blightfall," [Official Feed The Beast Wiki](https://ftb.fandom.com/wiki/Blightfall).

---

## 2. Found text as environmental storytelling — reward curiosity, don't force exposition

**Principle:** an item description or note should never be the only way to understand the plot; it should be a reward for a player who was already curious. Dark Souls tells almost its entire history through item flavor text and lets players "become a researcher-cum-author" by piecing fragments together rather than being told directly. FromSoftware's method places items by relevance to their location so a sickle in a graveyard, or a trapped chest, means something without a caption explaining it.

**Why it works:** exposition a player finds themselves feels earned and is remembered; exposition delivered to them feels like homework. Gone Home is the inverse proof of the same rule: its critical weakness, according to narrative-design analysis, is when a designer under-supplies fragments and forces a note to "convey dramatic elements" alone instead of alongside an object — notes work best paired with a physical thing, not standing in for it.

**Concrete technique (from Dark Souls analysis):** items reach a character by one of five routes — personal property, theft, foraging, food, or bodily byproduct — and each route implies a different fact about the owner. A locked chest means the owner wanted to protect something valuable, hide something dangerous, or hide that they owned it at all. Any one of those three readings is enough; the text doesn't need to pick for the player.

**Before (over-explained, hypothetical cellar-wall carving):**
> This was carved by Josie during the blackout the winter the reactor shut down, to remind herself she chose to stop it.

**After (in-pack register, cellar wall — implies without stating):**
> ELEVEN DAYS. I COUNTED. I STOPPED IT ON PURPOSE.

The carving gives a fact (eleven days), an action (counted), and a claim (on purpose) — and lets the player supply the "why," which they already partly know from Josie's letter. Nothing here says "reactor" or "blackout"; the found books and NPC dialogue elsewhere carry that.

**Source:** Lokey Lore, ["Environmental Storytelling"](https://lokeysouls.com/2020/11/16/environmental-storytelling/); Steve Gaynor via Game Developer, ["Gone Home and Its Hidden Objects"](https://www.gamedeveloper.com/design/gone-home-and-its-hidden-objects).

---

## 3. Letters: intimate, dated, and written for one person

**Principle:** an in-game letter should read like it was written by someone who knows exactly who's receiving it, with a length and format short enough to read in one sitting on a piece of UI. Animal Crossing gates its own tutorial around writing an actual, plausible letter — the game checks for real capitalization, punctuation, and word-length patterns before it treats the text as legible mail, because the entire mechanic depends on villagers appearing to write and receive real correspondence rather than placeholder text. Stardew Valley ties letters to relationship thresholds and gives major NPCs (the Wizard, Krobus, Sandy) their own visual letterhead so the letter is recognizably theirs before you read a word.

**Why it works:** a letter is the one text object in a game that structurally implies a relationship — someone chose to write to you specifically. That framing lets a few sentences carry more emotional weight than the same information delivered as a quest log entry, because the "why tell me this" question is already answered by the format.

**Before (generic, hypothetical):**
> Dear Player, Welcome to the valley. Please repair the farm and help the town of fifteen people survive winter. Good luck.

**After (in-pack register — Josie's Letter, page 1 style, matching q01's actual line):**
> If you're reading this I'm dead and the valley is cold. Only one of those is your problem.

One sentence, addressed to a specific "you," carries voice (dark humor undercutting the stakes), tells the reader their situation, and ends on a hook — the exact shape Stardew and Animal Crossing letters use to earn an emotional response in three lines or fewer.

**Source:** Set Side B, ["The Letter-Writing System in Gamecube Animal Crossing"](https://setsideb.com/the-letter-writing-system-in-gamecube-animal-crossing/); Stardew Valley Wiki, ["Letters"](https://stardewvalleywiki.com/Letters).

---

## 4. NPC barks carry subtext, and they have to change

**Principle:** a bark (a line an NPC says without being talked to, or a greeting) needs a surface meaning and a second meaning underneath, and it has to be one of many — the same line heard twice in a row breaks the illusion that anyone is home. Hades' writer Greg Kasavin built the entire dialogue system to solve exactly this: "I felt it was important for players to not quickly run into that moment of characters having repeating dialogue... so the only real solution was to give our characters lots of stuff to say." The system holds a pool of lines per situation, weighted by priority and gameplay state, and won't repeat a line until the whole pool for that context is exhausted — which can take tens of hours.

**Why it works, and what makes it feel alive rather than just large:** Hades doesn't just avoid repeats, it reacts specifically — a line about *how* you just died, delivered by the character who'd care about that detail — so "it feels like the game really sees you." Disco Elysium gets subtext a different way: its skills are voices that argue with each other and the player in the margins of ordinary dialogue, so even a mundane bark carries a second conversation underneath the literal one.

**Practical rule for a small pack (can't afford 21,000 lines):** don't try to out-volume Hades — use *change over time* instead of volume. A greeting said before a milestone and the same NPC's greeting said after it should be recognizably the same voice saying a different thing, so five or six hand-written variants per NPC, gated on story progress, do more work than fifty ungated random ones.

**Before (static bark, hypothetical, said forever):**
> Josie: "Welcome to the farm! Let me know if you need anything."

**After (progress-gated, same character, before/after the cellar reveal):**
> Early: Josie: "Forty lamps. That's not a number I picked for luck."
> Late: Josie: "Forty lamps lit. I never thought I'd count that high and mean it."

Same cadence, same obsession (the lamp count), but the second line only fires after the player has learned what the lamps mean — the change is the payoff, not a bigger line pool.

**Source:** Christi Kerr, ["How the Dialogue System in Hades Rewards Failure"](https://www.christi-kerr.com/post/how-the-dialogue-system-in-hades-rewards-failure); Cultured Vultures, ["Supergiant's Hades Contains More Words Than The Iliad and Odyssey Combined"](https://culturedvultures.com/supergiant-hades-word-count-dialogue/); Game Developer, ["Understanding the meaningless, micro-reactive, and marvellous writing of Disco Elysium"](https://www.gamedeveloper.com/business/understanding-the-meaningless-micro-reactive-and-marvellous-writing-of-i-disco-elysium-i-).

---

## 5. UI text length is a hard budget, not a suggestion

**Principle:** the format dictates the length before the content does. A toast is read in under two seconds at the corner of the screen; a chat/tellraw line is read while something else is happening (a mob spawning, a boss appearing); a book page is read while the player is standing still and can afford one paragraph but not a page. Screen real estate and reading context set the ceiling, and good UI text designs *within* that ceiling rather than fighting it with smaller fonts — text needs "legible borders and colors that match the overall design," implying the words themselves have to fit the space, not be shrunk to fit.

**Why it works:** a toast that takes longer to read than it's on screen fails at its only job. A tellraw line that runs past one sentence turns a bossfight beat into a subtitle player have to pause combat to finish reading — precisely the kind of friction Little Kettle Valley's own rules (chat/tellraw = one sentence, book pages ≤ ~230 characters) already guard against.

**Before (toast, hypothetical, too long):**
> Journal Entry 1: You should now proceed to follow the illuminated pathway that begins at your starting location, which will lead you directly to the old, abandoned Kettle family farm, where you will need to locate the waystone and place it correctly.

**After (in-pack register — q01's actual toast, same information):**
> Next: follow the lit path from where you woke up. It ends at the old Kettle farm. Put the waystone on the flat grey hearthstone by the chimney.

Three short clauses, each one new piece of information, each readable inside a toast's on-screen window — this is the pack's existing standard and it's already correct by the research.

**Source:** Indieklem, ["Accessibility, typographic hierarchy, emotions... the basics of typography in game interface"](https://indieklem.com/13-the-basics-of-typography-in-game-interface/); project house rules (`CLAUDE.md`): book pages ≤ ~230 chars, chat/tellraw = one sentence.

---

## 6. Humor is relief, placed right after the tight moment, never during it

**Principle:** comic relief works as "a pressure valve, providing a momentary release of tension," and its timing is the whole craft — it belongs immediately *after* a period of heightened drama, not inside it and not as constant background noise. The Last of Us's writers use Ellie's jokes specifically as banter *between* survival-horror beats, not layered on top of them.

**Why it works:** a joke inside a tense beat undercuts the beat; the same joke placed one line later, once the tension has landed, gives the player somewhere to exhale — and makes them trust the writing enough to feel the next tense beat fully, because they know relief is coming. Games "without comic relief tend to burn the player out" on unbroken seriousness — which matters directly for a pack explicitly built to never feel unsafe.

**Before (joke mid-tension, hypothetical, undercuts the beat):**
> Josie: "The reactor's core temperature is climbing and I'm the only one who— ha, you should see your face right now."

**After (joke placed as release, immediately after the beat resolves):**
> Josie: "The core's steady. Eleven days and it held." [beat] Josie: "...and yes, I did name it. Don't ask."

The tension is allowed to land clean first; the joke arrives as the exhale, one line later, which is what keeps a genuinely tense story moment (a power plant, a woman alone, a decision to shut it down) from ever tipping into something that reads as unsafe.

**Source:** StudioBinder, ["What is Comic Relief — Exploring the Importance of Humor"](https://www.studiobinder.com/blog/what-is-comic-relief-definition/).

---

## 7. Names are the cheapest, highest-leverage storytelling a pack has

**Principle:** a name is memorable when it's specific to *this* story and would make no sense in any other one, and a character or place name should say something about who or what it is without spelling it out. "Making coves and lagoons unique to your story makes them more memorable, especially when the name wouldn't make sense in just any story" — the same logic that makes "the Thaw Fair" a better act-title beat than "the Spring Festival," because Thaw implies the winter that came before it, which is the actual plot.

**Why it works:** players encounter a name hundreds of times over a playthrough — far more repetition than any single piece of dialogue gets — so a name that's doing story work compounds, while a generic one is dead weight every single time it's read. Uniqueness itself drives memorability: "we are biologically wired to pay attention to what is different."

**Before (generic, hypothetical):**
> The Farm. The Reactor. The Storage Room.

**After (in-pack register — from the project's actual canon):**
> The Kettle farm. The cellar door. Forty lamps.

Every one of these names is load-bearing: "Kettle" is a family name that makes the farm someone's specifically, "cellar door" is doing quiet foreshadowing work (a door implies a room implies a secret), and "forty lamps" turns an abstract goal (revive the town) into a countable, visualizable, unique-to-this-story image.

**Source:** Ignited Ink Writing, ["Naming Places: How to Give Your Fictional Settings Significant Names"](https://www.ignitedinkwriting.com/ignite-your-ink-blog-for-writers/naming-places-how-to-give-your-fictional-settings-significant-names/2021); Writers in the Storm, ["The Name Game: Tips for Naming Your Characters"](https://writersinthestormblog.com/2024/03/the-name-game-tips-for-naming-your-characters/).

---

## 8. What acclaimed Minecraft story modpacks get right — and where they bore players

**Principle:** the modpacks players remember as "written" (Blightfall above all) are the ones where quest text serves a mod-progression tech tree *and* a running narrative frame at the same time, so the player never has to context-switch between "learning a mod" and "following a story." Blightfall's quests exist to teach the player the included mods, but the wrapper — colonists who can't survive a Taint-choked planet — is what reviewers actually remember and praise years later, calling it "a whole world, a lore that has been created," not a quest list.

**Where the format usually breaks down — the pattern across the genre, not just one pack:** FTB Quests-style packs default to a screen of "Craft X to unlock Y" tech-tree captions with zero voice, because the tool is built for progression-gating, not prose, and most pack authors never overwrite the template text. Even beloved packs aren't immune to their own tedium: Blightfall itself is criticized for "a slow endgame" once the story wrapper thins out and only the grind is left, and Age of Engineering — a classic, well-regarded expert pack — draws the same complaint in a harsher key: reviewers note "the tedium can be a lot both early on, and after you set up UU matter replication," i.e. once the quest text stops being a story and reverts to being a checklist, players feel it immediately.

**The lesson for Little Kettle Valley specifically:** the risk isn't the early acts, where Josie's letter and the found-book fragments carry real voice — it's the back half of any long tech-tree pack, where quest volume naturally outpaces how much voice a writer can sustain per quest. The house rule that every quest's first sentence stays an instruction is what keeps even a "just craft this" quest from reading as pure tech-tree filler — but the *subtitle* line and the character-voice opener are what keep it from reading as *only* a tech-tree quest, and those are the two lines most likely to get skipped when a pack author runs out of steam at quest 90 of 126.

**Source:** "Blightfall," [TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/Blightfall) and [Official FTB Wiki](https://ftb.fandom.com/wiki/Blightfall); "Blightfall reviews," [Modded Minecraft Reviews](https://mmcreviews.com/all/modpacks/blightfall/?reviews-page=2); "Age of Engineering reviews," [Modded Minecraft Reviews](https://mmcreviews.com/all/modpacks/age-of-engineering/).

---

## The 10 rules

1. **Instruction first, always.** The first sentence of any quest is the verb-first action the player takes right now. Voice, stakes, and lore build around that sentence — never in front of it.
2. **Never make a note the only carrier of a fact.** Pair every found text with a physical thing (an object, a location, an NPC who'll reference it later) so the note rewards a curious player instead of being the one required reading.
3. **Give found text three readings, not one.** A carving, a letter fragment, or a cellar-wall line should let the player land on any of two or three plausible interpretations. If it only supports one reading, it's exposition, not lore.
4. **A letter is written to one specific person.** Before writing any in-game letter, name who wrote it and who they think they're writing to — that relationship, not the plot info, is what makes three sentences land emotionally.
5. **No bark fires the same way twice in a row.** Gate barks and greetings on story progress instead of trying to out-volume repetition — five hand-written, progress-gated variants beat fifty flat ones for a small pack.
6. **A returning NPC's line has to have changed.** If a greeting reads identically before and after a major beat, it's a missed beat. Write the "before" and "after" version together, not the "after" as an afterthought.
7. **Respect the format's reading window.** A toast gets one breath, a tellraw line gets one sentence, a book page gets one paragraph. Write to the space, don't shrink the words to fit it.
8. **Put the joke after the tight moment, never inside it.** Let tension land clean, then release it one line later. A joke that undercuts its own beat costs you the beat.
9. **Make every name load-bearing.** A name should imply a fact, a history, or a question ("the cellar door," "forty lamps") — if it would work unchanged in any other story, replace it.
10. **Budget voice across the whole quest count, not just the first act.** Decide up front how much character-voice text 126 quests can actually sustain, and protect the subtitle + opening line on every single one — those two lines are what keep the back half from reading as a tech tree once the writer's energy is lowest.

---

### All sources cited above

- E.M. Welsh — [How to Write Your First Video Game Quest](https://www.emwelsh.com/blog/video-game-writing-guide)
- Feed The Beast Wiki — [Blightfall](https://ftb.fandom.com/wiki/Blightfall)
- Lokey Lore — [Environmental Storytelling](https://lokeysouls.com/2020/11/16/environmental-storytelling/)
- Game Developer / Steve Gaynor — [Gone Home and Its Hidden Objects](https://www.gamedeveloper.com/design/gone-home-and-its-hidden-objects)
- Set Side B — [The Letter-Writing System in Gamecube Animal Crossing](https://setsideb.com/the-letter-writing-system-in-gamecube-animal-crossing/)
- Stardew Valley Wiki — [Letters](https://stardewvalleywiki.com/Letters)
- Christi Kerr — [How the Dialogue System in Hades Rewards Failure](https://www.christi-kerr.com/post/how-the-dialogue-system-in-hades-rewards-failure)
- Cultured Vultures — [Supergiant's Hades Contains More Words Than The Iliad and Odyssey Combined](https://culturedvultures.com/supergiant-hades-word-count-dialogue/)
- Game Developer — [Understanding the meaningless, micro-reactive, and marvellous writing of Disco Elysium](https://www.gamedeveloper.com/business/understanding-the-meaningless-micro-reactive-and-marvellous-writing-of-i-disco-elysium-i-)
- Indieklem — [The basics of typography in game interface](https://indieklem.com/13-the-basics-of-typography-in-game-interface/)
- StudioBinder — [What is Comic Relief](https://www.studiobinder.com/blog/what-is-comic-relief-definition/)
- Ignited Ink Writing — [Naming Places: How to Give Your Fictional Settings Significant Names](https://www.ignitedinkwriting.com/ignite-your-ink-blog-for-writers/naming-places-how-to-give-your-fictional-settings-significant-names/2021)
- Writers in the Storm — [The Name Game: Tips for Naming Your Characters](https://writersinthestormblog.com/2024/03/the-name-game-tips-for-naming-your-characters/)
- TV Tropes — [Blightfall](https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/Blightfall)
- Modded Minecraft Reviews — [Blightfall reviews](https://mmcreviews.com/all/modpacks/blightfall/?reviews-page=2)
- Modded Minecraft Reviews — [Age of Engineering reviews](https://mmcreviews.com/all/modpacks/age-of-engineering/)
