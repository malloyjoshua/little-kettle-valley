# Little Kettle Valley — quest book audit, lens: **CO-OP (two players, one FTB Teams party)**

Scope: the owner and his wife on one LAN server, both on the auto-created "Cozy" party
(valley_core.js §9-A). Everything below is judged as "what actually happens when the second
player is online", not as a numbers/pointer lint (that is scratch/book_lint.txt).

Sources read: `pack/kubejs/server_scripts/valley_core.js`, `valley_checks.js`,
`valley_finales.js`, `valley_gates.js`, `tools/scripts/compile_quests.py`,
`docs/integration-plan.md` §STORY-06, `story/quests/*.json`, `scratch/quest_hooks.txt`.

**Engine facts this audit rests on** (all verified in-repo, not assumed):

* `compile_quests.py:93` — `team_reward: true` is emitted **only** when the source JSON
  reward carries `"team": true`. Absent = `false`.
* `docs/integration-plan.md:691` (STORY-06, the pack's own verified note) — *"`team_reward:
  true` means exactly one team member receives the reward."* Therefore `team_reward: false`
  (the default) = **the reward is delivered once per team member**, and an auto-claim reward
  is delivered to every ONLINE member at completion time.
* `compile_quests.py:100-101` — command/stage/advancement rewards get `auto: "invisible"`,
  which is an automated claim. So an un-teamed command reward **executes once per online
  player**.
* `valley_finales.js:1652 runScene()` — has **no** `once()` latch. (The comment at line
  ~1621 in `sceneArrival` asserts "runScene has already taken the scene's own once() latch";
  it has not. Grep: the only `v.once` in the file is the per-beat finale latch at line 350
  and `/valley check` at line 2075.)
* `valley_finales.js:350 beat()` / `endAct()` — finales ARE latched per beat, world-level.
* `valley_checks.js:71 fire()` — `v.once(key, team)` then `v.complete(player, key)`; FTB
  Quests progress is team-wide, so one player satisfying a polled check ticks it for both.
  This half is correct and is the pack's strongest co-op mechanism.

---

## BLOCKER-adjacent structural finding (one issue, 68 quests)

### C1 — blocker — every quest from `q13a` onward — `story/quests/act1..act5,oda,start.json`

**Issue:** 68 quests carry command rewards with no `"team": true`, so with two players
online every one of them runs **twice** — every `tellraw @a` line prints twice to both
players, every `playsound ... @a` fires twice, and every `/valley scene <key>` plays its
whole segment twice (titles, sounds, `sayAll`, lamp particles), because `runScene()` has no
idempotency latch.

`start.json` and the first four Act I quests were fixed (12 rewards carry `"team": true` —
`q05, q07, q08, q10, q11, q12, q15`); the pass stopped there. Everything after `q13a` is
un-teamed.

**What the wife actually sees**, from Act II (q20) to the end of the pack: every resident
speaks each line twice in a row, every act card chimes twice, and the Act IV lamp sweep
plays 17 doubled particle+`block.copper.place` bursts. It reads as a broken mod, not a
cozy pack, and it starts the moment the second player joins.

**Exact fix** (this touches a field the brief marks frozen — `command` rewards — so flagging
rather than silently assuming): on each reward object listed below, add the key
`"team": true` alongside the existing `"type": "command"` / `"command": ...`. The command
string itself is unchanged. Old: `{"type": "command", "command": "..."}`; new:
`{"type": "command", "command": "...", "team": true}`.

Apply to **every command reward whose command is a `/valley scene`, a `/valley finale`, a
`tellraw @a`, a `tellraw @p`, or a `playsound ... @a`** in:

```
act1.json  q13a q19
act2.json  q20 q21 q23 q24 q25 q26 q27 q28 q29 q30 q32 q34 q35 q36 q37
act3.json  q38 q39 q41 q43 q44 q45 q47 q48 q49 q50 q53 q54 q54a q55 q56
act4.json  q58 q59 q60 q62 q64 q65 q66 q67 q70a q71 q72 q73 q74 q75
act5.json  q76 q77 q78 q79 q81 q82 q83 q86 q87 q88 q89 q90 q91
oda.json   oda_open
start.json q02 q05 q07   (the `playsound` rewards only — their scenes are already teamed)
```

**Do NOT add `"team": true`** to these, which are correct un-teamed (one copy per player is
the desired behaviour): every `title @p ...` reward (each player should get their own title
card), `give @p ...` (q01 q18 q28 q38 q40 q42 q52 q54 q55 — each player wants the pickaxe /
guide book), `recipe give @p *` (q18), `advancement grant @a` (idempotent), `bossbar set`
(idempotent), and `/valley standing <key> {team}` (idempotent by design).

**Cheapest partial fix if the frozen-field rule holds:** add the latch to `runScene()`
instead — one line, `if (!v.once('scene_' + key, v.teamId(source.player))) return 1` after
the SCENES lookup — which kills the doubled scenes and finales but leaves the ~40 doubled
`tellraw @a` resident lines. Not sufficient on its own.

---

## The scrip economy under two players

### C2 — major — `q36 q38 q45a q48a q49 q51a q53 q54 q54a q59 q60 q62 q63 q66a q68a q70a q72a q73 q75 q77 q80 q84a q85 q86a q88 mining_beryl oda_open oda_standing_order` — `story/quests/act2..act5, mining.json, oda.json`

**Issue:** all 28 `valley:scrip` **item rewards** are un-teamed, so with two players the valley
mints **1,286 scrip instead of 643** — while the mandatory spend is unchanged at 200
(`q85` 120 + `q86` 80). Oda's counter, which `rm_folk`/`rm_oda` bill as "the shortcut you pay
for", becomes free money from Act III on, and `q85` "Pay 120 Valley Scrip at Oda's Counter" —
the climax of her whole arc — is already affordable twice over by the end of Act IV.

**Compounding it:** every Oda shop line is `can_repeat: true` with `consume: true` on the
scrip *task* and un-teamed *goods*. One purchase takes 25 scrip from one player and hands
**both** players the goods. Combined with 2× income that is an effective **4× shop**:
`oda_frames` = 4 machine frames for 25 scrip, repeatable.

**Exact fix** — item rewards are explicitly in scope. On **every reward object of the form
`{"type": "item", "item": "valley:scrip", "count": N}`** in the 28 quests listed, add
`"team": true`:

```
old: {"type": "item", "item": "valley:scrip", "count": 60}
new: {"type": "item", "item": "valley:scrip", "count": 60, "team": true}
```

That keeps solo income at exactly 643 and makes the team purse a single purse, which is what
"pay Oda" means. Do this **before** touching any count — the numbers are already balanced for
one player and only break because they are paid twice.

**Second half of the fix** — the same key on the **goods** of every repeatable Oda line, so a
purchase delivers one lot: `oda_casings, oda_alloy, oda_gearing, oda_seedbox, oda_pantry,
oda_lampoil, oda_servos, oda_frames, oda_coils, oda_fluxduct, oda_cat_furniture,
oda_cat_windows, oda_cat_garden, oda_cat_lights, oda_livestock, oda_rare_seeds,
oda_reactor_casings, oda_reactor_internals, oda_ae_bundle, oda_plushie, oda_works_deed` —
add `"team": true` to each `{"type": "item", ...}` reward on those 21 quests.

### C3 — minor — `oda_open` — `story/quests/oda.json`

**Issue:** the chapter never tells two players that scrip is one purse and the counter is one
counter, so they will each try to hoard and neither will hit 120 for `q85` until late.

**Exact fix** — field `description`, append one line to the existing array:

```
old (last line): "One warning: keep two hundred Scrip back. The winter debt is a hundred and twenty, the Works Deed is eighty, and I do not get talked down."
new: add after it -> "&7Two players:&r Scrip is one purse. Pile it into one pack before you buy — and before Oda asks for the hundred and twenty."
```

---

## First join, the letter and the book for player two

### C4 — no defect — `valley_core.js valleyFirstJoin`

Verified working. `valleyFirstJoin` is gated on the **per-player** `first_join` stage, so the
second player gets her own written `Josie's Letter`, `ftbquests:book`, `valley:deed`,
`herbalbrews:copper_tea_kettle` and a lodestone `Kettle Farm Compass`, whenever she joins.
`facePathSettled` turns her three times, and `global.valley.once('world_opened')` is
world-level so the border and the two bossbars are not reset by her arrival. `objectiveState`
reads the **team** latch, so a wife joining in Act III is correctly told nothing rather than
being told to place a waystone that has been standing for ten hours. This is the best-behaved
co-op mechanism in the pack.

### C5 — major — `q01` and every quest completed while player two is offline — all chapters

**Issue:** FTB Quests auto-claim runs for **online team members only** at the moment of
completion. If the owner plays an evening alone, his wife's copies of every item/xp reward in
that evening are never delivered. They stay claimable in her book, but nothing in the book or
the readme says so, and `auto: "no_toast"` means she gets no popup pointing at them — a
completed quest looks finished.

This is the single most likely real failure for this couple: one plays ahead, the other logs
in the next day short a backpack, an iron pickaxe, a Megatorch and 16 cooked beef.

**Exact fix** — field `description` on `rm_world` (`story/quests/readme.json`), append to the
existing array:

```
old (2 lines): ["There is one valley and everybody plays in it. Lamps lit, houses opened, people moved in: the same for everyone logged in.", "", "Quest progress is shared across your party."]
new: [... same three ..., "", "&7If one of you plays ahead:&r rewards only land in the bags of whoever is &blogged in&r at the time. Open the book, scroll back over the green quests and click any reward still sitting there. Nothing is lost."]
```

### C6 — major — `rm_world` — `story/quests/readme.json`

**Issue:** `valley_core.js:829 valleyJoinParty` races. Both players are auto-partied only if
the FIRST one through has already had `pdPut('valley_team', ...)` land — a two-tick window.
Two clients connecting to a LAN world in the same second both find `stored == null`, both run
`ftbteams party create Cozy`, and end up on **two different parties both displayed as
"Cozy"**. Every command is `runCommandSilent` and the only symptom is a console line
(`"They keep their own quest book"`), so the couple would play for an hour before noticing
their books disagree. `valley_checks.js` latches per team, so the polled checks re-arm for
the second party and the *world* checks would re-tick — but nothing else would, and the
merge loses the item/craft quests.

**Exact fix** — field `description` on `rm_world`, add the check-and-repair as the first
thing a second player reads. Combine with C5's line:

```
new lines to append to rm_world description:
"",
"&7Before your first quest, both of you type &b/ftbteams party info&7. If it does not name the same party, the second player types &b/ftbteams party join Cozy&7 and it does from then on."
```

Also worth the owner's attention outside the book: have the second player wait until the host
is fully in the world before joining, the first time only.

---

## Item tasks, `consume`, and who has to be holding what

### C7 — major — `q26` — `story/quests/act2.json`

**Issue:** FTB Quests item tasks **do not pool across a team** — the count is read from the
submitting player's own inventory. `q26` needs `valley:lake_sand ×128, consume: true`, and
`q22` hands a `valley:dredge_net` to **each** player (un-teamed item reward), so both will
naturally take turns at the boat. `dredgePull` gives 16 to whoever clicked; alternating eight
pulls leaves 64 in each pack and the quest at 50%. Nella's own counter
(`valley_dredge_pulls`) is world-level, so she says *"that's the eight — a hundred and
twenty-eight"* while neither player can hand it in.

**Exact fix** — field `description`, append one line to the existing array:

```
old (last line): "Lake Sand is the only road to Washed Silica, and Bram's workshop is waiting on it."
new: add after it -> "&7Two players:&r the net fills whoever pulled it. Eight pulls between you, then pile all 128 into one pack before you hand it over."
```

Do **not** lower `tasks[0].count` from 128 — the eight-pull beat is the quest, and 128 is
still eight pulls for one person.

### C8 — minor — `q17 q30 q69 q70 q88 q48 q85 q86 q50 q32 q15` — `act1–act5.json`

**Issue:** same non-pooling rule on every large item task: `q88` 1,024 cobblestone, `q17` 128
oak planks, `q30` 64 washed silica, `q69` 64 uranium, `q70` 64 reactor casing, `q48` 64 track,
`q85` 120 scrip, `q86` 80 scrip. All fit one inventory (1,024 cobble = 16 slots, 120 scrip = 2
slots at the 64-stack in `valley_items.js:22`), so nothing is unwinnable — but a couple who
split the mining will each sit at half and read it as a bug.

**Exact fix** — one line in the readme rather than eleven quest edits. Field `description` on
`rm_order` (`story/quests/readme.json`), append:

```
new final line: "&7Two players:&r a quest counts what &bone&r of you is carrying, not both. Split the gathering, then pile it into one pack to hand in."
```

### C9 — minor — `q22` — `story/quests/act2.json`

**Issue:** the fish baseline in `valley_checks.js:q22` is keyed
`valley_fish_base_<playername>` — per player, not per team — so five fish each never
auto-ticks. The task title already says *"tick this yourself — honour system"*, so it cannot
wall, but the subtitle/description do not say the ten are per person.

**Exact fix** — field `tasks[0].title`:

```
old: "Ten fish caught (tick this yourself — honour system)"
new: "Ten fish caught between you (tick this yourself — honour system)"
```

---

## Duplicated one-of-a-kind props

### C10 — major — `q06` — `story/quests/start.json`

**Issue:** `q06` pays `{"type": "item", "item": "valley:town_anchor"}` un-teamed, so **both
players are handed a Surveyor's Stake** and there is exactly one socket. Once either drives
it, `valley_checks.js` (the `id === 'valley:town_anchor'` branch in `BlockEvents.placed`) has
**no `isDone('q07')` guard**: every subsequent placement anywhere in the world is
`setblock ... air`-ed, given back, and answered with Josie's *"Not there. Bram cut a socket
for it…"*. The second player is left holding an item that can never be put down anywhere,
being nagged about it, for the rest of the pack.

**Exact fix** — field `rewards`, on the `valley:town_anchor` entry:

```
old: {"type": "item", "item": "valley:town_anchor"}
new: {"type": "item", "item": "valley:town_anchor", "team": true}
```

One stake, one socket. Leave every other `q06` reward un-teamed — the skillet, knife and
seeds are correctly one each.

### C11 — minor — `q13a` — `story/quests/act1.json`

**Issue:** `justhammers:stone_hammer` and `geolosys:prospectors_pick` are un-teamed, so both
players get a prospector's pick. `valley_checks.js` counts pick uses in
`valley_pick_uses_<team>` — **pooled per team**, which is right — so two picks means `q28`'s
"all 6 marked spots" can be finished with three swings each. That is fine and arguably the
point of co-op; flagging only because the quest card says *"the 6 spots he marked"* and a
player who strikes three and sees it tick will assume it is broken.

**Exact fix** — field `description`, append one line:

```
old (last line): "The &aProspector's Pick&r hangs beside it: right-click bare stone underground and it names the nearest ore and how far. More in &6Ores and Mining&r."
new: add after it -> "&7Two players:&r you each get a pick, and the six strikes in Q28 are counted between you — not six each."
```

---

## Sleep, beds and where the second player wakes up

### C12 — major — `q08` — `story/quests/start.json`

**Issue:** `valley_core.js:737` sets `gamerule playersSleepingPercentage 1`, so the **first**
player into a bed passes the night for everybody. `valley_checks.js checkSleep` credits `q08`
on that player's sleep→awake edge and completes it for the team. Correct, and `q57`/`q76`
behave the same way in Acts IV and V.

The co-op consequence is the one the quest text does not cover: the second player **never has
to get into a bed**, so vanilla never runs `startSleepInBed` for her and **her respawn point
is never set**. She dies in the mine in Act II and wakes at world spawn `-324 75 116`, ~84
blocks up the road from the farm, with no explanation. `q02` already hands **each** player a
`minecraft:red_bed` (un-teamed, correctly), so the bed exists — nothing tells her to use it.

**Exact fix** — field `description` on `q08`, append one line to the existing array:

```
old (last line): "Marnie opens the inn she has kept with no guests in it, Bram opens the mill, and she leaves you her seed sack, 32 &aGreen Oak Planks&r and a flint and steel."
new: add after it -> "&7Two players:&r one sleeper passes the night for both. Put &adown a second bed&r and sleep in it once anyway — that is what sets where you wake up if you die."
```

Do **not** team `q02`'s `minecraft:red_bed` reward — two beds is exactly what this needs.

### C13 — minor — `q57` and `q76` — `story/quests/act4.json`, `act5.json`

**Issue:** same mechanism, later. Both are checkmark quests polled by `checkSleep`, both gated
on a world stage (`act4`, `act5`), and both tick for the team off one sleeper. Working as
intended; the only co-op wrinkle is that whichever player is *not* asleep gets no title card
and no `say` line — `v.say(player, 'Pip', ...)` and `v.say(player, 'Marnie', ...)` in
`checkSleep` target the sleeper only, so the other player's morning is silent and she will not
know the act turned.

**Exact fix** — field `subtitle` on each, so the card itself carries the beat for the player
who did not sleep:

```
q57  old subtitle: "The Hearth has gone out."
     new subtitle: "The Hearth has gone out. One of you sleeping is enough."
q76  old subtitle: "Year two, and the noticeboard is longer."
     new subtitle: "Year two. One of you sleeping is enough."
```

(Both "old" strings are verbatim from the files.)

---

## Scenes, finales, bossbars and toasts — verdicts

### C14 — blocker (mechanism half of C1) — 14 quests — `act3.json act4.json act5.json`

**Issue:** `runScene()` (`valley_finales.js:1652`) takes **no latch**, and **all 21 scenes
carry a `who:` line** that is broadcast with `v.sayAll()` (a `tellraw @a`). The seven scenes
reached from `start.json`/`act1.json` are protected by `"team": true` on their command
rewards; the other 14 are not:

```
q54  q58  q59  q60  q62  q64  q65  q66  q70a  q71  q72  q73  q74  q76
```

With two players each of those plays **twice in the same tick**: the resident's line prints
twice to both, the `playsound` fires twice, and `q74`'s scene runs `lightLamps` over 17 posts
twice, so the road lights with 17 doubled `block.copper.place` bursts and a doubled end-rod
burst per post. `putAll` is self-guarding ("the rest were already occupied") and the NPC
teleports are idempotent, so nothing is *broken* — it simply reads as a stuttering pack for
the entire back half of the story.

**Exact fix** — the same one-key edit as C1, on the `/valley scene <key>` command reward of
each of those 14 quests: add `"team": true`.

### C15 — no defect — finales — `valley_finales.js:349`

Verified safe under double-fire. `runFinale` is entered twice (once per online player) but
every one of `finaleAct1..5` is wrapped in `beat(v, act, 0)` from its first statement, and
each later payoff takes its own world-level `once()`. The second invocation costs one
redundant `forceHold` and returns. `markFinale` lives only in the last beat. No change needed
— and note that adding `"team": true` per C1 makes this moot anyway.

### C16 — no defect — bossbars — `valley_core.js:723-728, 804`

Verified working for two players. `bossbar set valley:lamps players @a` and
`valley:folk players @a` are re-issued on every `ServerEvents.loaded` **and** on every
`PlayerEvents.loggedIn`, so the second player picks up both bars the moment she joins, at
their current values. The values themselves are world-level (`valley_lamps_lit` in
`persistentData`), which is right for one shared valley. The `bossbar set ... value N` command
rewards are absolute and idempotent, so running them twice is harmless — they are correctly
left off the C1 fix list.

### C17 — no defect — the "Next:" toasts — `compile_quests.py:100, 129`

Verified working for two players, **and this is the one place the un-teamed default is
exactly right**. `lead_toast` gives the first `toast` reward on each quest `auto: "enabled"`,
and with `team_reward: false` FTB Quests delivers it to **every online team member** — so both
players get the same "Next:" popup at the same moment, which is what `rm_next` promises
("one popup slides in at the top right"). **Do not add `"team": true` to any toast reward**;
that would silence one of the two players for the whole pack.

Caveat inherited from C5: a player who is offline at completion never sees that quest's toast,
and there is no backlog. The `rm_world` line in C5 is the only mitigation available in-book.

---

## The 23 polled checkmarks, one by one (`valley_checks.js`)

Every one of these calls `fire(player, key)` → `v.once(key, teamId)` → `v.complete(player, key)`,
and FTB Quests progress is team-wide, so **one player satisfying it ticks it for both**. The
per-team latch (not the old per-world one) is correct and is the reason two players do not
break each other. Verdicts:

| key | mechanism | two players |
|---|---|---|
| `q01` | right-click the written letter | ✓ either reads; both still get their own copy on first join |
| `q02` | hearth cell holds a waystone | ✓ either places |
| `q03` | cottage door/windows/bed/sconce cells, poller within 24 of home | ✓ either can be the one standing there |
| `q04` | megatorch within a 13×7×13 box of home | ✓ |
| `q05` | poller inside `CELLAR_BOX` | ✓ only one has to go down |
| `q07` | socket cell holds `valley:town_anchor` | ✓ — but see **C10**, the spare stake |
| `q08` `q57` `q76` | sleep→awake edge | ✓ one sleeper; see **C12**, **C13** |
| `q10` | ≥3 chickens within 12 of home | ✓ pooled by proximity, not by player |
| `q22` | **per-player** `valley_fish_base_<name>` | ✗ does not pool — **C9** |
| `q25` | 2 cows + 2 sheep within 24 of home | ✓ |
| `q28` | **per-team** `valley_pick_uses_<team>` | ✓ pools — **C11** |
| `q34` | duct within 6 of ≥2 of the four q34 posts | ✓ |
| `q47` | duct within 12 of the inn, poller within 48 | ✓ |
| `q53` | the recorded barrel is non-empty | ⚠ **C18** below |
| `q55` | cellar box + world stage `act3` | ✓ |
| `q59` | ≥2 `ribbits:` within 8 of the poller | ✓ |
| `q65` | poller inside `works.shell` | ✓ |
| `q74` / `q74p<i>` | **per-team flag per post** | ✓ **best co-op design in the pack** — they can walk the road from opposite ends and the flags merge |
| `q82` | poller inside the echo cave box | ✓ |
| `q90` | a light on the porch post | ✓ |

### C18 — minor — `q53` — `story/quests/act3.json`

**Issue:** `valley_checks.js` records the Delivery Crate in `valley_crate_pos`, a **world-level**
`persistentData` key with no team scoping, and the `BlockEvents.placed` branch rewrites it for
**every** `minecraft:barrel` placed within ±10/±6/±10 of the board while `q53` is unfinished.
Two players dressing the square (which `q78` later asks for) will overwrite each other: player A
places and fills the crate, player B sets a decorative barrel beside the board, the pointer moves
to B's empty barrel and the poll stops passing with no explanation. Oda even says *"Crate's beside
the board"* a second time, which reads as confirmation.

**Exact fix** — field `tasks[0].title`, so the failure is self-diagnosing:

```
old: "Crate beside the board, export bus feeding it"
new: "Crate beside the board, export bus feeding it — only ONE barrel by the board"
```

(Task title is text; if the current string differs, keep it and append the em-dash clause.)

---

## Pacing: is there enough for two people to do at once?

**Verdict: yes, comfortably — this is the pack's strongest pacing property and it should be
said out loud in the book.** Walking the six story chapters in order and counting quests whose
dependencies are all satisfied, the non-Story frontier never drops below **27** and averages
**~29** from `q02` to `q90`. The Story lane is a single chain (one player drives it), and the
release valve is 22 side chapters totalling ~200 quests across four groups:

```
Home and Farm       62   Animals and Fishing 14 · Cooking and Brewing 16 · Farm and Seasons 18 · Home and Town 14
Tech               113   Create 25 · Storage Network 22 · Thermal 21 · Ores and Mining 16 · The Reactor and the Quarry 16 · Power and Logistics 13
The Valley Beyond   40   Places 16 · Getting Around 12 · The Wild 12
Side Quests         37   Oda's Counter 23 · Useful Items and Tips 14
```

That is a natural two-player split — one on the cozy lane, one on tech — and it is exactly the
shape `rm_lanes` already describes for a solo player. It just never says it to a couple.

### C19 — minor — `rm_lanes` — `story/quests/readme.json`

**Issue:** the readme explains the two lanes but never tells two players that the lanes are the
co-op split, so the likely first-session behaviour is both of them following the same Story
quest around and one of them idling.

**Exact fix** — field `description`, append to the existing array:

```
old (last line): "Only &cfive quests in winter&r need the reactor, and Oda sells every part of it over her counter."
new: add after it -> "&7Two players:&r that is your split. One takes the cozy lane, one takes &6Create&r and &6Thermal&r, and the story quests get done by whoever is nearest. About thirty side quests are open at any moment."
```

### C20 — minor — pacing, no single quest — the back half shortens

Because item/xp rewards are per player and the Story chain is one chain, a two-player team moves
through the spine at roughly the same quest count but with double the materials, double the
scrip (**C2**) and double the tools (**C10, C11**). Acts IV and V — which are the gear-gated
ones (reactor, AE2, quarry) — will land noticeably early. Fixing **C2** (team the scrip) removes
the largest single contributor; the rest is inherent to co-op and is not worth flattening, since
the counts are already tuned for one player and lowering them would punish the solo run.

**No change recommended.** Recorded so the owner is not surprised when Act IV arrives an evening
early.

---

## Priority order for the fix pass

1. **C1 + C14** (blocker) — add `"team": true` to the `/valley scene`, `/valley finale`,
   `tellraw @a`, `tellraw @p` and `playsound … @a` command rewards on the 68 listed quests.
   This is one mechanical pass and it removes every doubled line, sound and scene in the pack.
   *Touches a field the brief marks frozen — owner's call, but nothing else fixes it.*
2. **C2** (major) — `"team": true` on the 28 `valley:scrip` item rewards and on the goods of the
   21 repeatable Oda lines. Restores the whole economy to its tuned numbers.
3. **C5 + C6** (major) — two new lines in `rm_world`: unclaimed rewards for the player who was
   offline, and the party sanity-check before the first quest.
4. **C10** (major) — `"team": true` on `q06`'s `valley:town_anchor`, so there is one stake.
5. **C12** (major) — the second-bed line on `q08`.
6. **C7** (major) — the dredge-net line on `q26`.
7. Minors: **C3, C8, C9, C11, C13, C18, C19**.
8. No action: **C4, C15, C16, C17, C20** — verified correct or accepted.

**Nothing in this lens is unwinnable.** No co-op mechanism hard-locks a quest: every polled check
completes for the team, every honour-system checkmark is tickable by hand, the recipe gates in
`valley_gates.js` are ingredient-based and world-level (no `.stage()` anywhere, verified), and no
stage reward carries `team_reward: true` (STORY-06 respected across all 27 of them). The blocker
rating on C1/C14 is for *experience*, not progression: from Act II to the end, both players read
every resident's line twice.
