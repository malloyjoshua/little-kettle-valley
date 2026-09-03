# The residents — Easy NPC presets

Fifteen Easy NPC presets: the **eight residents** of the cast, the **four Ribbits** who follow Wisp
in, and the **three Act V arrivals** (8 + 4 + 3 = the "pop. 15" on the Founder's Day signpost).
Josie Kettle is dead and speaks only through the Patchouli journal — she has no NPC.

**Source of truth:** `story/npcs.json`
**Generator:** `tools/scripts/make_npc_presets.py`
**Output:** `pack/kubejs/data/valley/easy_npc/preset/<key>.npc.snbt`

Never hand-edit the `.npc.snbt` files. Edit `story/npcs.json` and re-run:

```
tools/venv/bin/python tools/scripts/make_npc_presets.py story/npcs.json pack
tools/venv/bin/python tools/scripts/make_npc_presets.py story/npcs.json pack --check   # validate only
```

The generator is deterministic — a re-run with unchanged input produces byte-identical files.

---

## Three engine facts that shape every preset

All three were read out of the jars (`server/mods/easy_npc-forge-1.20.1-7.11.0.jar`,
`server/mods/ftb-quests-forge-2001.4.22.jar`) with `javap`. Two of them contradict what the
build brief assumed, so they are written down here in full.

### 1. The preset path is `easy_npc/preset/`, not `preset/`

`de.markusbordihn.easynpc.security.PresetSecurity#isAllowedDataPresetPath` accepts a **data**
preset only when its resource path starts with `easy_npc/preset/` or `easy_npc/api/preset/`
(or, for the `easy_npc` namespace itself, `preset/` / `api/preset/`). Anything else is refused with
*"Rejected data preset …, because it is not below the expected … folder."*

* ❌ `valley:preset/marnie.npc.snbt` — rejected.
* ✅ `valley:easy_npc/preset/marnie.npc.snbt` — works.

The generator also drops an identical **inert compat copy** at
`pack/kubejs/data/valley/preset/<key>.npc.snbt` because the build brief named that path. Nothing
should reference it; Easy NPC will not load a data preset from there.

### 2. `access:"INTERNAL"` cannot be imported by command

`PresetAccess#isUsableByCommand` returns false for `INTERNAL`. The jar's base template
(`data/easy_npc/api/preset/base/humanoid.npc.snbt`) ships as `INTERNAL`, so every valley preset sets
`access:"PUBLIC"`. Copying the base template verbatim would produce presets that silently refuse to import.

### 3. `ftbquests open_book` takes no player argument

`dev.ftb.mods.ftbquests.command.FTBQuestsCommands` registers `open_book` with one optional
`quest_object` string and **no** player argument; it opens the book for the *source* player.
`ftbquests open_book @initiator` is a syntax error. The book action is therefore:

```
{Cmd:"/ftbquests open_book", ExecAsUser:1b, PermLevel:0, Type:"COMMAND"}
```

which is exactly what `pack/config/easy_npc/security.cfg` already provisions:
`executeAsUserCommandAllowList.ALL=ftbquests,trigger,me`.

---

## What each NPC is made of

```
ON_INTERACTION:
  1. /info_message <greeting>        ExecAsUser:0b  PermLevel:2   condition: <objective> LESS_THAN 1
  2. /info_message <greeting_after>  ExecAsUser:0b  PermLevel:2   condition: <objective> >= 1
  3. /ftbquests open_book            ExecAsUser:1b  PermLevel:0   (never conditional)
```

Plus: `CustomName` (a JSON component in the resident's colour), `CustomNameVisible:1b`,
`PersistenceRequired:1b`, `Invulnerable:1b`, `SkinData Type:"DEFAULT"` with a `VariantType` from
the jar's own enum, `ObjectiveData` = `LOOK_AT_PLAYER` + `LOOK_AT_RESET` only (they turn to face
you and never wander), vanilla `Tags` for the finale selectors, and a deterministic `data.UUID`.

**Why `PermLevel:2` on the greeting.** `/info_message` is an Easy NPC macro
(`ActionUtils.MACRO_INFO_MESSAGE`) that expands to
`/title @initiator title {"text":"…","color":"aqua"}`. Vanilla `/title` needs permission level 2.
`PresetSanitizer` clamps each entry to `min(PermLevel, actor level)`; a server/console import gets
`serverTrustedCommandLevel=ADMINS` (3), so 2 survives. **Always run the imports from a function,
KubeJS, or an op console** — a survival player importing by hand is clamped to 0 and the greeting
would silently do nothing.

**Why the greetings are short.** They render as a screen *title*, not a chat line. The generator
errors above 120 characters and rejects any double quote in the command (it would break the
`/info_message` JSON).

---

## The arc gate — how the second line turns on

Each resident's chain closes at a named quest (§5 Standing). One dummy scoreboard objective per
resident flips the greeting.

`valley_core.js` **must create these on server load, before any resident is imported:**

```
scoreboard objectives add valley_arc_marnie dummy
scoreboard objectives add valley_arc_bram   dummy
scoreboard objectives add valley_arc_oda    dummy
scoreboard objectives add valley_arc_nella  dummy
scoreboard objectives add valley_arc_halden dummy
scoreboard objectives add valley_arc_tobin  dummy
scoreboard objectives add valley_arc_wisp   dummy
scoreboard objectives add valley_arc_pip    dummy
```

If an objective is missing, `ScoreboardCondition` logs *"Scoreboard objective … does not exist,
every dialog and action using it stays hidden"* and **both** greeting lines are suppressed — the NPC
still opens the book but says nothing. This is the one failure mode worth watching for.

The arc-closing quest adds a command reward:

```json
{"type":"command","command":"/scoreboard players set @p valley_arc_marnie 1","elevate":true,"silent":true}
```

Quest progress is per team, but rewards are claimed per player, so each player's greeting flips
when *they* claim the closing quest.

| Resident | Chain closes at | Quest | Objective |
|---|---|---|---|
| Wisp | Q59 | The Reed Village Comes In | `valley_arc_wisp` |
| Marnie | Q60 | Soup for a Full Room | `valley_arc_marnie` |
| Halden | Q62 | Halden's Rounds | `valley_arc_halden` |
| Pip | Q63 | Pip's Winter Job | `valley_arc_pip` |
| Bram | Q73 | Bring Bram | `valley_arc_bram` |
| Tobin | Q75 | Tobin's Numbers | `valley_arc_tobin` |
| Nella | Q77 | Glaze the Cold Frame… | `valley_arc_nella` |
| Oda | Q85 | Pay 120 Valley Scrip at Oda's Counter | `valley_arc_oda` |

**Why scoreboard and not a player tag.** `PlayerTagCondition#evaluate` is a bare
`player.getTags().contains(name)` — it ignores the `Operation` field completely, so a tag can only
express *"the arc is closed"*, never *"not yet"*. `ScoreboardCondition` honours
`ConditionOperationType`, so one objective gives both halves of the pair.

---

## The cast

| Key | Name | Role | Lane | Entity | Skin | Colour | Tag |
|---|---|---|---|---|---|---|---|
| `marnie` | Marnie Ashcombe | Innkeeper, keeper of the Hearth | cozy | humanoid | `MAKENA` | `#E0A15A` | `npc_marnie` |
| `bram` | Bram Tolliver | Millwright | tech | humanoid | `EFE` | `#A8825C` | `npc_bram` |
| `oda` | Oda Vance | Storekeeper, bounty board, quartermaster | both | humanoid_slim | `NOOR` | `#C9A227` | `npc_oda` |
| `nella` | Nella Brightwater | Fisher and ferryman | cozy | humanoid_slim | `KAI` | `#4FA3D1` | `npc_nella` |
| `halden` | Halden Root | Herbalist and brewer | both | humanoid | `PROFESSOR_01` | `#5E8C61` | `npc_halden` |
| `tobin` | Tobin Gale | Prospector | tech | humanoid | `ARI` | `#D9613C` | `npc_tobin` |
| `wisp` | Wisp | Ribbit forager | cozy | humanoid_slim | `KAWORRU` | `#8FD14F` | `npc_wisp` |
| `pip` | Pip Ashcombe | Marnie's nephew, nine, courier | cozy | humanoid_slim | `SUNNY` | `#E8A2C8` | `npc_pip` |
| `ribbit_reed` | Reed | Ribbit of the reed village | cozy | humanoid_slim | `EFE` | `#7FB25A` | `npc_ribbit_reed` |
| `ribbit_sedge` | Sedge | Ribbit of the reed village | cozy | humanoid_slim | `MAKENA` | `#7FB25A` | `npc_ribbit_sedge` |
| `ribbit_mudlark` | Mudlark | Ribbit of the reed village | cozy | humanoid_slim | `NOOR` | `#7FB25A` | `npc_ribbit_mudlark` |
| `ribbit_puddle` | Puddle | Ribbit of the reed village | cozy | humanoid_slim | `ZURI` | `#7FB25A` | `npc_ribbit_puddle` |
| `newcomer_tess` | Tess Weaver | Act V arrival, weaver | cozy | humanoid_slim | `ARI` | `#B98AC9` | `npc_newcomer_tess` |
| `newcomer_corin` | Corin Ashe | Act V arrival, roofer | tech | humanoid | `KAI` | `#8FA9C9` | `npc_newcomer_corin` |
| `newcomer_mab` | Mab Oldfield | Act V arrival, came home | both | humanoid_slim | `STEVE` | `#C7B8A1` | `npc_newcomer_mab` |

Every NPC also carries the tag `valley_npc`; the Ribbits also carry `ribbit`, the arrivals `newcomer`.

**Invented names.** The story document does not name the four Ribbits or the three Act V arrivals.
Those seven names are the author's and are flagged `"invented": true` in `story/npcs.json` — rename
them freely, the keys and tags travel with the name.

**Skins.** All are `SkinData Type:"DEFAULT"` with a `VariantType` from the jar's own enums
(`HumanoidSkinVariant`: ALEX ARI EFE KAI MAKENA NOOR STEVE SUNNY ZURI JAYJASONBO PROFESSOR_01
SECURITY_01 KNIGHT_01 KNIGHT_02 · `HumanoidSlimSkinVariant`: the first nine plus KAWORRU). No
`PLAYER_SKIN` and no remote URL: both need a network round trip, and `security.cfg` gates
`URL_RESOURCE` behind `CREATIVE_PLAYER`. Wisp and the Ribbits are humanoids in the frog-green
name colour — Easy NPC has no Ribbit body. If a frog silhouette is wanted later, that is a
`RESOURCE_LOCATION` skin plus a `ModelData` scale, and it changes nothing else here.

---

## The lines

| Key | Before the arc closes | After |
|---|---|---|
| `marnie` | There you are. Kettle is on and I baked too much bread again. | Full room tonight. Sit down before I give your chair away. |
| `bram` | Do not just stand there. Hold this, and do not let it slip. | Wheel is turning. Sixty years I waited. Come and look at it. |
| `oda` | Shelves are thin and my ledger is thinner. What do you need. | Books balance. Eleven years. Here, take the ledger. I mean it. |
| `nella` | Lake is in a mood. So am I. Bring a rod anyway. | Turns out I like growing things. Do not make it strange. |
| `halden` | Sit a while. Tea first, then whatever it is you came to ask. | The cellar door is open and I am not carrying it alone now. |
| `tobin` | You own a pickaxe. Good. Look at this rock. No, really look. | Bram said good work. Out loud. I have not stopped hearing it. |
| `wisp` | You are come! I bring basket. Eat the purple one first, yes. | Two villages, one place now. My people sleep warm at the inn. |
| `pip` | I named the duck after you. Do not be weird about it. | I have a real job now. The duck supervises. Mostly badly. |
| `ribbit_reed` | Wisp says you are the new one. You are less tall than said. | — |
| `ribbit_sedge` | I carry too much. Is fine. Is what I am for, mostly. | — |
| `ribbit_mudlark` | The mud here is good mud. You should be proud of this. | — |
| `ribbit_puddle` | Warm inn. Warm soup. We stay now, I think. Yes. We stay. | — |
| `newcomer_tess` | Saw your noticeboard from the ridge road. Is there a room? | — |
| `newcomer_corin` | I mend roofs. Heard this valley has roofs again. Here I am. | — |
| `newcomer_mab` | I left here in the bad winter. I am not leaving twice. | — |

---

## Where the finales put them

All offsets are `~` offsets, used inside a function invoked as
`/execute positioned <ax> <ay> <az> run function valley:actN/<name>` (§7 rule 3). Rows marked
**doc** are fixed by `story/story-final.md` §12.5; rows marked *proposed* are this file's suggestion
because the story document specifies the beat but no coordinates — the finale author should treat
them as a starting point, not a contract.

### Act I — The Thaw Fair · origin: **Town Anchor**

| NPC | Offset | Source |
|---|---|---|
| `marnie` | `~-4 ~1 ~-2` | doc |
| `bram` | `~4 ~1 ~-2` | doc |
| `oda` | `~-4 ~1 ~2` | doc |
| `pip` | `~4 ~1 ~2` | doc (his duckling is summoned at `~4 ~1 ~3`) |

`halden` is placed earlier in Act I at the hedge garden, *proposed* `~-14 ~1 ~8`; `wisp` is first
met at the Ribbit village waystone (Q20), *proposed* `~0 ~1 ~3` from that waystone.

### Act II — The Midsummer Lantern Float · origin: **Lake Waystone**

All six are `/tp`'d, not re-imported.

| NPC | Offset | Source |
|---|---|---|
| `marnie` | `~-2 ~1 ~4` | doc |
| `bram` | `~2 ~1 ~4` | doc |
| `oda` | `~-2 ~1 ~6` | doc |
| `nella` | `~0 ~1 ~10` | doc |
| `halden` | `~2 ~1 ~6` | doc |
| `pip` | `~0 ~1 ~4` | doc |

`nella` is first imported earlier in Act II, *proposed* `~0 ~1 ~8` from the Lake Waystone.
`tobin` arrives in Act II on the north-ridge side of the square, *proposed* `~12 ~1 ~-14` from the
Town Anchor. `wisp` moves into the stilt house, *proposed* `~-8 ~1 ~12` from the Lake Waystone.

### Act III — The Harvest Supper · origin: **Town Anchor**

The doc says "seated positions" and gives no coordinates. The Act I finale places
`valley:long_table` at `~-3 ~1 ~0`, so these seats *(all proposed)* run along it:

`marnie ~-4 ~1 ~-1` · `bram ~-2 ~1 ~-1` · `pip ~0 ~1 ~-1` · `halden ~2 ~1 ~-1` · `tobin ~4 ~1 ~-1`
· `oda ~-4 ~1 ~1` · `nella ~-2 ~1 ~1` · `wisp ~0 ~1 ~2` · `ribbit_reed ~2 ~1 ~2`
· `ribbit_sedge ~4 ~1 ~2` · `ribbit_mudlark ~6 ~1 ~2`

The three extra Ribbits are **imported** here (their first appearance); everyone else is `/tp`'d.

### Act IV — The Longest Night · origin: **the Works**

| NPC | Offset | Source |
|---|---|---|
| `bram` | `~0 ~1 ~2` | doc — he faces the lever the finale sets at `~0 ~2 ~0` |
| `pip` | `~0 ~1 ~4` | proposed (he rings the hand bell; the `playsound` is on `@a`, so any mark works) |
| `marnie` | `~-3 ~1 ~4` | proposed |
| `oda` | `~3 ~1 ~4` | proposed |
| `tobin` | `~-3 ~1 ~2` | proposed |
| `nella` | `~-3 ~1 ~6` | proposed |
| `halden` | `~3 ~1 ~6` | proposed |
| `wisp` | `~0 ~1 ~6` | proposed |
| `ribbit_reed` / `_sedge` / `_mudlark` | `~2 ~1 ~6` · `~4 ~1 ~6` · `~-2 ~1 ~6` | proposed |
| `ribbit_puddle` | `~-4 ~1 ~6` | proposed — **imported** here, the fourth Ribbit |

`tobin` is also `/tp`'d into the Q82 echo cave, *proposed* `~0 ~1 ~4` from the cave entrance
waystone ("Tobin already inside, talking", §12.7).

### Act V — Founder's Day · origin: **Town Anchor**

| NPC | Offset | Source |
|---|---|---|
| `newcomer_tess` (`newcomer_a`) | `~0 ~1 ~24` | doc |
| `newcomer_corin` (`newcomer_b`) | `~2 ~1 ~26` | doc |
| `newcomer_mab` (`newcomer_c`) | `~-2 ~1 ~26` | doc |
| `halden` | `~0 ~1 ~-2` | he reads Josie's last page; the finale sets the signpost at `~0 ~1 ~-3` |
| `pip` | `~0 ~1 ~2` | proposed — he rings the bell at the end |
| `marnie` · `bram` · `wisp` | `~-4 ~1 ~2` · `~-2 ~1 ~2` · `~4 ~1 ~-2` | proposed |
| `oda` · `nella` · `tobin` | `~-4 ~1 ~-2` · `~-2 ~1 ~-2` · `~2 ~1 ~-2` | proposed |
| `ribbit_reed` · `_sedge` · `_mudlark` · `_puddle` | `~6 ~1 ~0` · `~6 ~1 ~2` · `~6 ~1 ~-2` · `~8 ~1 ~0` | proposed |

The doc also asks for the three arrivals to walk the last stretch in with a `follow_player`
objective. That is a runtime change on top of the preset — the presets ship with
`LOOK_AT_PLAYER` + `LOOK_AT_RESET` only. Add the objective after import, or accept a static
tableau; either reads fine at 24 blocks.

---

## Importing and re-importing

```
/easy_npc preset import data valley:easy_npc/preset/<key>.npc.snbt <x> <y> <z>
```

Every preset carries a deterministic `data.UUID` (`uuid5` of `copperkettle://npc/<key>`).
`PresetHandler#importPresetData` branches on it: if an entity with that UUID already exists it is
**updated in place**, otherwise it is **created**. So the command above is idempotent — running it
twice does not give you two Marnies, and re-running it after regenerating the presets is how you
push edited dialogue into a live world.

* **Re-import one resident after editing her lines** — regenerate, then run the import command again
  at any coordinates. Existing NPC, new dialogue.
* **Deliberately want a second copy** — use `import_new` instead of `import`; it forces a fresh UUID.
  Only `valley:easy_npc/preset/…` paths are accepted either way.
* **Move a resident** — `/tp @e[tag=npc_<key>,limit=1] <x> <y> <z>`. Never re-import to move; the
  finales all `/tp` for exactly this reason (pathing across arbitrary terrain does not work).
* **Tags went missing** (a future Easy NPC build could stop round-tripping vanilla `Tags`) —
  `/tag @e[type=easy_npc:humanoid,limit=1,sort=nearest] add npc_<key>` and the same for `valley_npc`.
  Everything downstream selects on the tag, so this is the one thing worth spot-checking on first run.
* **Nothing happens when you click a resident** — check the log for
  *"Scoreboard objective … does not exist"* (the objectives were never created) or
  *"Command levels were reduced"* / *"Command actions were removed"* (the import ran as a
  non-op player and `PresetSanitizer` clamped it).

## Deliberately not used

* **Dialog trees.** `DialogData` / `DialogDataSet` is fully expressible and the jar ships worked
  examples, but Easy NPC dialog is click-driven and cannot be sequenced, and §7 rule 5 puts all
  paced finale dialogue in `tellraw`. Two `/info_message` lines and the quest book is the whole
  contract.
* **Trading.** §5: the Valley Scrip shop is an FTB Quests chapter, not a merchant UI. Easy NPC may
  get two or three flavour trades on Oda later; the preset ships with none, and the base template's
  `OPEN_TRADING_SCREEN` interaction is removed.
* **`MESSAGE` actions.** They render as chat rather than a title and support MiniMessage colour,
  which would arguably read better than `/info_message`. Left alone so the greeting matches the
  build brief exactly; switching is a one-line change in the generator if you want chat lines.
