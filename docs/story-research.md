# Story research — what actually makes a modpack storyline land

**Scope.** Research for *Little Kettle Valley* (Forge 1.20.1, FTB Quests + KubeJS + Easy NPC, two-player household plus friends). Every claim below is tagged:

- **[DOC]** — the exact text exists at the cited URL (questbook text, dev/pack description, wiki, forum post, review, GitHub issue, API response).
- **[INF]** — my inference. No source states it.
- **[UNVERIFIED]** — the claim was made in a source I could not retrieve, or the cited page did not contain the quoted text.

**The most important methodological finding, stated first.** Almost every "this is WHY the pack succeeded" claim in modpack discourse is unsourced. Descriptions of *what a pack does* are abundant and checkable; explanations of *why players liked it* almost never exist as primary evidence. Worse, three of the classic "great story pack" success stories are confounded by Let's Play exposure, not design:

- Agrarian Skies — Yogscast's 99-episode *Hardcore Skyblock* series. [DOC] https://yogscast.fandom.com/wiki/Hardcore_Skyblock_(Agrarian_Skies)
- Journey to the Core — Yogscast's 102-episode *To The Core* series (Nov 2015–Oct 2016). [DOC] https://yogscast.fandom.com/wiki/Minecraft:_To_The_Core
- Crash Landing — ModpackIndex attributes its spike to "several big YouTubers at once" in 2014. [DOC] https://www.modpackindex.com/

**So: do not copy design decisions from download counts.** For a private two-person pack, adoption is irrelevant anyway. What we want is the small set of documented *practices* that make a questbook readable and finishable.

---

## 1. Ranked packs

Ranked by *usefulness to Little Kettle Valley × strength of evidence*, not by popularity.

### 1. Create: Above and Beyond (1.16.5, 2021)
**Device.** The whole quest tree *is* the build path to one physical object stated on the welcome page. Questbook, verbatim: "Your entire factory will be put to the test as final products flow into the Data Centre, programming the Guidance computer of your Spaceship." The CurseForge blurb frames the entire pack the same way — "an epic technological journey toward space travel," "fifty inventions between you and the moon."
**Why it worked.** The destination is named in hour one, countable, and identical in the last chapter. Chapters are legible slices of it (Welcome, Bulletin Board, Market, Shipments, Metallurgy, Lifesavers). [DOC for the text; INF for the causal claim — no dev post or review argues the mechanism.] One review calls it "my favorite modpack of all time."
**What failed.** Nothing documented.
- https://create-above-and-beyond.fandom.com/wiki/Quests
- https://www.curseforge.com/minecraft/modpacks/create-above-and-beyond
- https://mmcreviews.com/all/modpacks/create-above-and-beyond/ (now redirects to https://moddex.gg/)

### 2. Blightfall (Technic, 1.7.10, 2015)
**Device.** Colonist scout dropped into a planet entirely covered in Thaumcraft Taint; the rest of the crew stays in orbit and you earn resource requisitions by completing quests. Hand-built ~3.75km map, HQM quest book, CustomNPCs crew.
**Why it worked.** Two documented things. (a) The antagonist is mechanically real — Taint spreads over time and poisons the player, so the story pressure and the survival pressure are one system. (b) **The quest book is the credited narrative-delivery mechanism**: the contemporary review says HQM is used "not only to give you goals and rewards, but to slowly reveal the story of the planet." [DOC]
**What failed.** The same review calls it "enormous to tackle solo" and grindy in the back half. [DOC]
**Correction worth carrying.** A popular claim that Blightfall's handcrafted biodome "does more narrative work than quest text" is **[UNVERIFIED]** — the quote used to support it does not exist in the review, and the review argues the opposite. The map is atmosphere; the book is the story.
- https://ftb.fandom.com/wiki/Blightfall
- https://airaplaysgames.wordpress.com/2015/08/23/blightfall-minecraft-modpack-a-detailed-compelling-world/
- https://blightfall.fandom.com/wiki/Taint

### 3. Material Energy^5: Entity (and ME^4)
**Device.** A distress call from an AI-run station ("Error: Universe not found. Catastrophic failure."), then a series of discrete rooms loaded through an AE spatial system, each with its own resources and quests, all feeding one monument. Dev's own words: "travel from different rooms loaded in an AE system, each distinct and challenging, gathering unique resources and completing quests in order to complete the monument and achieve a final goal." [DOC]
**Why it worked.** This is the cleanest documented *chapter architecture* in the whole survey: bounded areas with their own start and end, all summing to one stated endpoint. ME^4 did the same with 250+ quests, 20+ spatial areas and a 16-"space-time wool" checklist. [DOC]
**Also documented and directly relevant:** ME^5 states its player count on the pack page — "This modpack is balanced around 2 to 3 players on normal difficulty… If you wish to play with more or less players, adjust the difficulty as needed." [DOC] Almost nobody does this. It is free and it sets expectations.
**What failed.** Nothing documented. Note that ME^4's popularity figures (143k) have no baseline to compare against.
- https://www.curseforge.com/minecraft/modpacks/material-energy-5-entity
- https://www.curseforge.com/minecraft/modpacks/material-energy-4
- https://forum.feed-the-beast.com/threads/material-energy-megathread.101335/

### 4. Create: Astral (1.18.2 Fabric, 2022)
**Device.** Chapter per celestial body — Earth → Moon → Mars → Mercury — under an opening line ("Waking up on a planet underneath a shattered moon, discovering the technology of a civilisation long past").
**Why it matters most to us — a source-level finding.** In the pack's repo, individual quest objects in `config/ftbquests/quests/chapters/*.snbt` carry **narrative description text and mechanical task requirements in the same object**. There is no separate "lore quest" type. [DOC — verified in the repo, not just the store page.]
**Its own stated design rule, verbatim:** "Planets tie into the progression of the pack. They are not a goal but a path leading you through exploring." [DOC] This is the opposite of Above and Beyond's single-object framing — both ship, both work, they are different bets.
**What failed.** Community commentary describes the tech tree as growing "much too quickly in the early game," and the pack ships a **separate FAQ chapter and a separate automation-guide chapter** — which implies the narrative chapters alone left players needing help. [DOC for the chapters existing; INF for the implication.]
**Caveat for us.** Fabric, not Forge.
- https://www.curseforge.com/minecraft/modpacks/create-astral
- https://github.com/Laskyyy/Create-Astral
- https://createastral.wiki.gg/wiki/Chapters

### 5. Prominence II RPG: Hasturian Era (1.20.1 Fabric, ongoing, 12.4M downloads)
**Device.** Two campaigns delivered through **"Immersive Dialogues"** (voice-acted, "no AI used", used on campaign/important quests) plus **"Interactive Dialogues"** (a custom screen where the player answers the NPC). [DOC]
**Why it matters.** It is the ceiling of production value, and it shows the split worth stealing: reserve the expensive presentation for story beats so they don't read like every other quest popup. [DOC for the feature split; INF for the effect.]
**What failed / what we can't copy.** The lift. And a hard, concrete blocker for us: the **EasyNPC × FTB Quests Compat** mod — which does exactly "NPC dialogue that changes with quest progress" — has exactly one release, **Minecraft 1.21.1–1.21.11, Fabric only**. Base Easy NPC supports Forge 1.20.1 but ships no FTB Quests integration. [DOC — Modrinth API.] On our loader, quest-conditional NPC lines must be built by hand in KubeJS.
- https://modrinth.com/modpack/prominence-2-fabric
- https://www.curseforge.com/minecraft/modpacks/prominence-2-hasturian-era
- https://modrinth.com/project/tJfPbrsT (EasyNPC × FTB Quests Compat)
- https://modrinth.com/mod/easy-npc

### 6. MeatballCraft: Dimensional Ascension (1.12.2)
**Device.** Nine-plus chapters, each with self-contained lore and its own puzzle set woven into progression gates.
**Why it worked — and a correction.** A widely-repeated claim says its rich lore failed to substitute for progression signposting, citing a review titled "Questbook is some kind of joke." Checked: that review is by a 5-hour player, rated 2.0/5, and was voted **0 helpful / 10 not helpful** by the site's own community. The pack's aggregate is **4.7/5 across 52 reviews, ranked #1 modpack on ModDex**, and the long-playtime reviewers praise exactly the thing the claim denies: "a really satisfying progression where you can continually upgrade your crafts… as you go through the chapters" (500 hrs), "the questbook is very helpful at leading me through mods i hadn't touched before" (100 hrs), and "if I didn't know how something worked, there would be a tooltip built into the game to tell you" (1,000 hrs). [DOC]
**The real lesson.** Confusion is **front-loaded**. The unhappy reviews are all short-playtime; the happy ones are long-playtime. Guidance density matters most in the first hours.
**What failed.** One 200-hr reviewer notes the questbook "might also not be everyone's jam" for players wanting more hand-holding. [DOC]
- https://moddex.gg/modpack/meatballcraft
- https://meatballcraft.miraheze.org/wiki/MeatballCraft:_Dimensional_Ascension

### 7. Agrarian Skies / Agrarian Skies 2 (1.6.4 / 1.7.10)
**Device.** Skyblock apocalypse, opened by a strong comic voice: "you are the sole survivor(s) of this devastating tragedy… the omnipotent goddesses, The Jaded One and The Cute One, who chose to abandon you after this final act of mercy with nothing more than a book." [DOC]
**Why it worked.** A 2014 review that explicitly analyses the pack credits **resource scarcity, HQM guided progression, hardcore lives and crafting satisfaction** — and never mentions the writing. [DOC] The memorable thing is the *intro beat*, not a narrator who keeps talking; I found no evidence of sustained narration past the opening. The popularity driver is the Yogscast series.
**What failed / a myth to drop.** AS2 is often cited as having "customizable difficulty to match individual playstyles." Its actual page says: "There are multiple map options ranging from easy to hard. Your game difficulty will determine what you start with for resources." [DOC] That is a **one-time, pre-playthrough, whole-world** choice. It does not help two players of different patience sharing one world.
- https://ftb.fandom.com/wiki/Agrarian_Skies:_Hardcore_Quest
- https://www.curseforge.com/minecraft/modpacks/agrarian-skies-2
- https://whyigame.wordpress.com/2014/09/23/minecraft-agrarian-skies/

### 8. Regrowth (1.7.10)
**Device.** Restore a dead wasteland — the closest historical analogue to a restoration story.
**Why it worked.** A contemporary review credits the **questbook as a teacher**: a "comprehensive HQM quest book that walks you step-wise through unfamiliar mods," producing "a relaxing, growing/farming progression, that gives you sufficient time and space to build however you wish." [DOC]
**What failed / correction.** The claim that Regrowth's restoration premise *is* the mechanic (the way Taint is in Blightfall) is **[UNVERIFIED]** and the review argues against it: the wasteland is motivational framing over ordinary HQM gating through Thaumcraft/Forestry/Blood Magic/Botania. Nothing attacks you for not restoring.
- https://whyigame.wordpress.com/2015/09/26/minecraft-regrowth-first-thoughts/
- https://forum.feed-the-beast.com/threads/makings-of-a-story-driven-hqm-pack.146377/

### 9. Farming Valley (1.10.2/1.12.2, 3.09M downloads)
**Device.** An explicit Stardew/Harvest Moon pastiche with a **named guiding NPC as the first objective**: "Your first goal will be to spawn in a Goddess, who will explain how to progress in the pack." [DOC] Four seasons with season-specific crops, NPC shops, an achievement book.
**Why it matters.** It is the only pack in the survey whose *first quest is a character*, which is structurally what our Q8/Q12 do.
**What failed — and this is a real operational warning.** (a) The base pack was under-quested enough that a community fork, *Farming Valley Expanded*, exists specifically to add "hundreds of quests" and "clear, non-intrusive guidance… explained through quests, guides, NPCs, and item descriptions" to "minimize wiki-searching." [DOC] (b) At least one player reported that **an important NPC failed to spawn** — an NPC-gated onboarding step is a single point of failure. [DOC, community report]
- https://www.curseforge.com/minecraft/modpacks/farming-valley
- https://www.minecraftforum.net/forums/mapping-and-modding-java-edition/minecraft-mods/mod-packs/3060564-farming-valley-expanded-a-major-revamp-of-an-old

### 10. Craft to Exile 2 (1.20.1, 2.68M downloads)
**Device.** Borrowed ARPG grammar: "Prologue Chapter… followed by the Main Campaign Acts," with side objectives that pay build power rather than lore. [DOC]
**Why it matters.** Acts are a structure players already know, so the pack spends no words teaching its own shape. Note the honest caveat: the Act framing is inherited from the Mine & Slash mod's Path-of-Exile styling, not an original authorial choice, and its ModDex score is 3.2/5 from only 5 ratings — far too thin to prove anything.
- https://www.curseforge.com/minecraft/modpacks/craft-to-exile-2
- https://github.com/mahjerion/Craft-to-Exile-2/wiki/Mine-&-Slash
- https://moddex.gg/modpack/craft-to-exile-2

### 11. FTB Inferno / FTB Genesis / FTB Skies (official FTB, 2023–2025)
**Device.** One paragraph of premise plus environmental staging, over a near-interchangeable tier-progression questbook. Inferno: "A rite gone wrong, trapped in a dimension of fire and torment… bend this world to your will… or be lost to the INFERNO." Genesis: "Suspended in a corrupt simulation, your people need you to restore Elyria's habitat." Skies: floating island, no land. [DOC]
**Why it matters.** This is the *cheapest* viable story tool: a single strong hook plus a spawn condition that matches it. The world state sells the fiction; the quests underneath do not have to.
**Correction.** These are often cited as "genre-borrowing" (Matrix, Fallout). On the packs' own text they are original tropes, not borrowed franchises — the borrowed-premise pattern only genuinely appears in *The Suspect's Journey* (Among Us: "The Skeld," "defeat the Imposter"), a 6,948-download pack with no reception data at all. [DOC]
- https://www.curseforge.com/minecraft/modpacks/ftb-inferno
- https://www.curseforge.com/minecraft/modpacks/ftb-genesis
- https://www.feed-the-beast.com/modpacks/103-ftb-skies
- https://www.curseforge.com/minecraft/modpacks/the-suspects-journey

### 12. Homestead (CozyStudios, 1.20.1, 2025, 656k downloads)
**Device.** Theme-grouped chapters (Heart of the Homestead, Whispers of the Wilds, Embers Beneath, Deep Dark Secrets, Echoes of the Void — 22 chapters), tamable companion mobs, and a stated pacing philosophy: **"Custom Quests: A full questline that guides you without limiting your freedom"** and "Peaceful Progression" / "No Forced Path — explore at your own pace, in your own way." [DOC]
**Why it matters — this is our closest neighbour and our clearest opening.** A 4/5 review of it says, verbatim: the world "feels like it is missing a stronger story behind it… we have not discovered much substantial lore explaining the world, its locations, or why certain things exist," and prescribes exactly what we already plan: "Small environmental stories, books, hidden locations, quest descriptions, NPC stories, or scattered pieces of information could add another layer to the experience." [DOC]
**Honesty about that evidence.** It is one reviewer at one general-gaming outlet, and the lore gap is one of *three* co-equal suggestions (the others: transportation and difficulty) inside a positive score. It is not proof the pack was "marked down" for it. Treat it as a well-phrased request, not a verdict.
- https://cozystudios.org/homestead/intro/
- https://gaminghq.eu/2026/08/08/homestead-cozy-minecraft-modpack-review/
- https://www.curseforge.com/minecraft/modpacks/homestead-cozy

### 13. Cottage Witch (1.18.2/1.19.2, 610k downloads)
**Device.** No plot. A lifestyle premise plus a questbook whose stated purpose is teaching: "Learn mods ingame by following custom quests instead of consulting a wiki," and "It intends to mostly preserve the vanilla progression." [DOC]
**Why it matters for the non-builder partner.** Prefab structures — a wizard tower, mansion, hobbit hole, campsite — are **claimed out of the quest book**, framed explicitly: "Don't worry if you're not much of a builder though or just want to get straight into exploring… Grab your favorite from the quest book and place it wherever you decide to call home." [DOC] Also documented: it is "cozy and fun to play with a partner," and "you can spend HOURS just decorating your cottage" without progressing the quests. [DOC]
**What failed / corrections.** Two widely-circulated quotes about this pack — that its quests are "optional scaffolding" for mixed player types, and a reviewer line about "stay-at-home types" — are **[UNVERIFIED]**; neither appears in the cited sources. The pack has no tech-mod content, so it says nothing about tech-lane gating.
- https://www.curseforge.com/minecraft/modpacks/cottage-witch
- https://gamingcompanion.substack.com/p/8-things-to-do-in-cottage-witch
- https://moddex.gg/modpack/cottage-witch
- https://www.akliz.net/blog/posts/getting-cozy-with-cottage-witch

### 14. The Ferret Business (1.7.10, WIP 2015–2021)
**Device.** A corporation teleports you into a strange dimension and keeps talking to you: "We can communicate with you, and send items back and forth through your handy, dandy QUEST Tablet." [DOC] 500+ quests, a quest-driven contract economy rather than pure unlock gating.
**Why it matters.** It is the only pack in the survey with a *persistent* narrator device baked into a mechanic.
**What failed.** It never reached 1.0. Releases ran v0.0.2 (Jul 2015) → v0.4.2a (Jan 2021) with a 19-month gap; players asked on the forum whether it was abandoned and got no reply; version numbering skips 0.3.x entirely. [DOC] The cause is undocumented — it is a solo creator's project, not a "team that outran its scope," and calling it a failure overstates it (152k downloads, 266-page thread). The honest lesson: **unexplained multi-month gaps erode trust; a pack can ship real content for six years and still never end.**
- https://forum.feed-the-beast.com/threads/1-7-10-the-ferret-business-wip-bq-hqm-500-quests-v-0-2-6.64930/
- https://www.curseforge.com/minecraft/modpacks/the-ferret-business/files/all

### 15. Overgrown — the failure case
**Device.** A story-oriented progression pack.
**What failed.** Its own listing: "no longer under development and will remain as is, unfinished… playable but still has some bugs and unfinished quests," at roughly 80% completion. [DOC] This is the single clearest documented case of a modpack story stopping mid-arc, and it is the one lesson in this entire research pass that survived verification unqualified.
- https://www.curseforge.com/minecraft/modpacks/overgrown

### Also checked, lower value
- **Journey to the Core** — bounded descent, dimension by dimension: "You begin your trip in a small cave on the overworld and slowly move further down dimension by dimension." [DOC] But it is a self-described *hardcore* pack, the one documented player reaction is someone struggling with restricted-inventory HQM, and its popularity is Yogscast-driven. https://forum.feed-the-beast.com/threads/1-7-10-journey-to-the-core-hardcore-hqm.62313/
- **Crash Landing** — often listed as a story pack; its entire story is one sentence ("You've managed to crash land on a dry, dusty planet. No water, no food, no real supplies… Try not to dehydrate"). The famous "venting" thread is actually 25 pages of players *sharing water-production solutions* — the gate was learnable, it just wasn't taught in-book. ~2.5/5 aggregate. https://www.curseforge.com/minecraft/modpacks/crash-landing · https://forum.feed-the-beast.com/threads/crash-landing-help-venting-and-discussion.50255/
- **TerraFirmaPunk** — its changelog notes "The questbook has been fully rewritten to be more compact as well as fit better into the world of TFC" [DOC], but the only substantive review credits its mechanics and never mentions the writing. https://www.curseforge.com/minecraft/modpacks/terrafirmapunk · https://whyigame.wordpress.com/2017/01/21/minecraft-terrafirmapunk/
- **Monumental Experience** — the author's own page says "the quest book serves as a showcase, not a full tutorial or progression guide." [DOC] Useful only as a named anti-pattern; no reviews exist on the aggregator that supposedly criticised it. https://www.curseforge.com/minecraft/modpacks/monumental-experience
- **Create: Arcane Engineering** — parallel magic/tech tracks that fuse late. Real structure, but cross-dependency starts well before the end, and 3.5/5 from 3 ratings supports nothing. https://www.curseforge.com/minecraft/modpacks/create-arcane-engineering
- **Life in the Village 3** — Minecolonies attachment through named citizens; 877k downloads. Note the common description of it as "deliberately low-tech, no machines" is wrong — its own page advertises "an in-depth tech tree… sprawling factories" and Create. https://www.curseforge.com/minecraft/modpacks/life-in-the-village-3
- **Vault Hunters** — commonly cited as the story-committed FTB Quests exemplar; it is not FTB-Quests-driven, it runs a custom Vault mod. Iskall85's stated design direction is worth one line though: "easier to understand for everyone… less grind, more fun… casual playstyle is an option." https://vaulthunters.gg/ · https://x.com/iskall85/status/1547592680997150720

---

## 2. The verified lessons

Only lessons with a real source are listed. Where the standard version of a lesson failed verification, the failure is stated so nobody re-imports it.

### Framing and voice

**F1. Name the destination in the first quest, in words you will reuse in the last quest.** [DOC that packs do it; INF that it causes anything] Create: Above and Beyond names the spaceship on the welcome page and ends on the spaceship. FTB Inferno/Genesis/Skies each spend one paragraph and then let the spawn condition carry the fiction. The cheap version costs one sentence.

**F2. Put the voice and the instruction in the same quest object.** [DOC] Create: Astral's quest source files carry narrative description and mechanical task in one object; there is no separate lore-quest track. Corollary: a story that lives only in a companion book is a story your partner may never open.

**F3. The questbook is the narrative delivery mechanism — not the terrain, not the aesthetic.** [DOC] Blightfall's own reviewer credits HQM with "slowly reveal[ing] the story of the planet." The oft-repeated claim that a handcrafted starting area outperforms quest text is **unsupported and contradicted by its own source**. Build the biodome for atmosphere; write the book for story.

**F4. Atmosphere alone reads as missing something.** [DOC, single reviewer] A 4/5 cozy pack was told, in writing, that it needed "environmental stories, books, hidden locations, quest descriptions, NPC stories." Weak evidence, but it is a request from exactly our audience for exactly our plan.

**F5. Reserve expensive presentation for story beats.** [DOC] Prominence II separates voice-acted "Immersive Dialogues" (campaign beats) from ordinary quest text. We can't voice-act, but the principle transfers: the finale scenes should not be delivered in the same register as "craft 8 alloys."

**F6. Hard platform fact.** Quest-state-reactive NPC dialogue has no off-the-shelf solution on Forge 1.20.1. EasyNPC × FTB Quests Compat is 1.21.1 Fabric only. [DOC] Budget KubeJS time for it.

### Pacing and guidance

**P1. Bounded chapters with their own start and end, all summing to one stated goal.** [DOC] ME^5's dev describes exactly this ("each distinct… in order to complete the monument and achieve a final goal"); Astral runs chapter-per-planet; ME^4 ran 20+ areas into a 16-item checklist.

**P2. Confusion is front-loaded — thicken guidance in the first hours, not the last.** [DOC] On the #1-ranked expert pack, every negative "the questbook is useless" review is from a sub-20-hour player and was downvoted by the community; every 100–3,000-hour reviewer describes the chapters as clear progression. The people who bounce, bounce early.

**P3. Where a pack's signposting thins, the documented request is "more quests," not "more story."** [DOC] The StoneBlock 3 review asks for "a few more quests" because "certain resources have a very long production chain" and the player couldn't tell if they were on the right path. Splitting a long chain into more, smaller quests is the fix.

**P4. A questbook explicitly scoped as a "showcase, not a full tutorial" is a real design choice with a real cost.** [DOC] Monumental Experience says so on its own page. Ours must be complete.

**P5. Beware the discovery confound.** [DOC] Three canonical "story packs" got their audience from Let's Plays. Sprawl does not prevent adoption either — DawnCraft (10.4M downloads) is described as overwhelming, its "curated" alternative NightfallCraft has ~1.5–2M. Adoption is not a design signal. For us the only metric that matters is: did two people finish it.

### Gating

**G1. Mechanical gating with zero narrative is a proven, popular pattern.** [DOC] SevTech: Ages hides ore, items and recipes based on progress and drives everything off vanilla advancements, with no story, no NPCs and no chapters — 7.1M downloads. Gating does not need a story to function. (The corollary claim that gating "carries narrative weight" is **unsupported**; and the widely-quoted 4.2/5 reception score for SevTech has no findable source.)

**G2. Quest count is not story.** [DOC] GT New Horizons' own site frames its ~3,900-quest book as "technical progression rather than story-driven." The largest questbook in modding is explicitly not a narrative.

**G3. Teach the gate's solution in the book, or it gets solved on a forum.** [DOC for the forum thread; INF for the prescription] Crash Landing's water gate had a real solution — 25 pages of veterans explaining it to newcomers. The failure was discoverability, not difficulty.

**G4. Ingredient-visible gating beats hidden gating for legibility.** [INF] No source states this; it is the structural argument that a gate whose ingredient appears in EMI is self-explaining. Included because it is already our design and it survives the "don't make them look it up" test.

**G5. A one-time, world-level difficulty choice does not solve mismatched co-op.** [DOC] Agrarian Skies 2's "multiple map options ranging from easy to hard" is chosen before the world starts and applies to everyone in it.

### Rewards

**R1. Endgame power needs a stated sink.** [DOC] A StoneBlock 3 player filed "Stoneblock 3 NEEDS a better ending quest"; an FTB team member replied "The ending of the pack is to have infinity armor and be the most powerful you can be" and closed it. The player's complaint — top-tier gear with nothing to use it on — is a real, recorded reaction to a pack that ends at a resource ceiling.
https://github.com/FTBTeam/FTB-Modpack-Issues/issues/2544

**R2. Give the non-builder a claimable structure, not an empty lot.** [DOC] Cottage Witch hands out prefab homes from the quest book with an explicit "Don't worry if you're not much of a builder."

**R3. Keep a low-stakes activity permanently available.** [DOC] Cottage Witch players "can spend HOURS just decorating"; Homestead advertises "objectives without obligations." Both are pack-description claims, not measured effects, but they are the shape of the cozy genre.

**R4. "Rewards should be the shortcut for the next quest, not a trophy" has no source.** [INF] I found no dev post, review or forum thread anywhere in this survey arguing reward-pacing philosophy. Our reward rule is our own invention. It is a good one; it is not borrowed.

### Co-op and non-gamer partners

**C1. State the player count on the tin.** [DOC] ME^5 does it in one sentence. Nearly nobody else does.

**C2. Parallel tracks that converge late are a shipped structure, unproven as a fix.** [DOC for the structure — Create: Arcane Engineering's magic and tech lines; **unsupported** for the "answer to mixed-interest households" claim, which no source makes.] Our braided lanes are a stronger version anyway: theirs converge once at the end, ours trade material every third quest.

**C3. A named guiding NPC as the first objective is a shipped device — with a documented single point of failure.** [DOC] Farming Valley's Goddess "will explain how to progress"; a player also reported an important NPC failing to spawn. Any NPC-gated step needs a self-heal.

**C4. "Non-gamer partners just need performance + prettiness, not systems" is refuted.** The couples-marketed, quest-free pack offered as evidence has **498 total downloads** and no reviews; the other pack cited actually ships a full quest system. There is no evidence base for the claim.

### Endings

**E1. Scope to what you can finish. This is the only lesson that survived verification unqualified.** [DOC] Overgrown shipped at ~80% and stopped: "unfinished… still has some bugs and unfinished quests." Ferret Business ran six years of releases and never reached 1.0.

**E2. Make the ending the object you named at the start.** [DOC for the practice] Above and Beyond ends on the spaceship from the welcome page; ME^5 ends on the monument named in the pack description.

**E3. A resource ceiling is not an ending.** [DOC] See R1.

**E4. Silence is what erodes trust, not slow progress.** [DOC] Ferret Business's forum shows players asking "is this abandoned?" and receiving no reply, across a 19-month release gap.

---

## 3. The counterexamples — why goals-without-story packs still get finished

These packs have no narrative at all and are finished by large numbers of people. They are the control group, and they define the floor our story must not sink below.

| Pack | Narrative | What carries it | Evidence |
|---|---|---|---|
| **SevTech: Ages** | none | Dynamic hiding of ore/items/recipes by progress; vanilla advancements as the signpost. 7.1M downloads. | https://sevtechages.fandom.com/wiki/SevTech:_Ages · https://www.curseforge.com/minecraft/modpacks/sevtech-ages |
| **GT New Horizons** | explicitly "technical progression rather than story-driven" | ~3,900 quests that inform you what's required to progress; "making learning part of the fun"; one stated endpoint (Stargate). | https://www.gtnewhorizons.com/ |
| **All the Mods 9** | none — "does not follow a specific thematic focus apart from vanilla Minecraft" | Breadth (400+ mods), a checklist questbook reused release to release, and a built-in endgame. | https://www.curseforge.com/minecraft/modpacks/all-the-mods-9 |
| **StoneBlock 3** | none | Tiered resource unlocks; praised for "goals and progression, making it easy to know what to do next." | https://cursedquail.com/blog/2023-01.stoneblock3-review/ |
| **Nomifactory** | none | A questbook framed as "an encyclopedia of useful knowledge"; explicitly "no complicated magic systems… only factories." | https://www.curseforge.com/minecraft/modpacks/nomifactory |
| **Cottage Witch** | none | Quests as tutorials replacing wiki lookups, plus permanently-available cozy activity. | https://www.curseforge.com/minecraft/modpacks/cottage-witch |

**Why they work, stated plainly:**

1. **The book always answers "what do I do next," at every moment, without ambiguity.** That is the entire product. Narrative is optional; the answer is not.
2. **The reward is capability, and capability is legible.** A doubled ore yield or a new dimension needs no framing to feel like a payoff.
3. **They carry no narrative debt.** Nothing is promised, so nothing can be left unresolved. Overgrown's failure mode is unavailable to them.
4. **Progression is its own signpost.** SevTech's hidden recipes mean the game itself tells you what tier you're on; you cannot get lost in the tech tree the way you can get lost in a plot.

**And the honest counter-counterexample:** none of this produces the thing our brief actually asks for. A checklist cannot deliver a cute payoff, a person who is glad to see you, or a reason the fortieth lamp matters more than the first. StoneBlock 3's recorded complaint is precisely the shape of what a plotless pack cannot give: *"nothing to use it on."*

**The synthesis, which is the actual design rule:**

> Story is the reason to care. The checklist is the reason to keep playing. If our story ever costs the player a clear answer to "what do I do next," we have traded the thing that works for the thing that is nice.
