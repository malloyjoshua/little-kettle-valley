# Oda's Bounty Board (Bountiful 6.0.4)

Bountiful is data-driven: **pools** define the pieces (objectives you can be asked for, rewards you can be paid), **decrees** are a named playlist of pools that a Bounty Board rolls from. None of this is touched by `compile_quests.py` — it's the mod's own JSON, read straight off disk, and it has nothing to do with FTB Quests IDs or stages.

## Where the files live

```
pack/kubejs/data/bountiful/bounty_pools/valley/
  cozy_objectives.json   — what the board can ask for (cozy lane)
  cozy_rewards.json      — what it pays out (cozy lane)
  tech_objectives.json   — what the board can ask for (tech lane)
  tech_rewards.json      — what it pays out (tech lane)

pack/kubejs/data/bountiful/bounty_decrees/valley/
  cozy.json               — { "objectives": ["cozy_objectives"], "rewards": ["cozy_rewards"] }
  tech.json                — { "objectives": ["tech_objectives"], "rewards": ["tech_rewards"] }
```

A decree file just lists pool filenames (no extension) to pull from — you can list more than one pool per decree (vanilla Bountiful stacks 2-3, e.g. a resident-specific pool plus a shared `_all_objs` pool). Ours are single-pool for now; add a second entry to either array to widen the roll without touching the other lane.

## Why this exists in the story

Per `story/story-final.md` §12 (correction C8): **FTB Quests cannot see a Bountiful completion** — it only reads the player's inventory, not the board's internal state. So the story-critical bounty beat, **Q37 "The Bounty Board Fills Up"**, is three hand-authored FTB Quests item tasks (24 wheat / 8 cooked fish / 8 wool), not a real Bountiful roll. Q53 then builds the **Delivery Crate** so every later "bring X to Y" quest is pre-filled from the AE2 network.

**This pool content is for after the story ends.** The Act V finale (Founder's Day) explicitly unlocks "Endless Seasons: repeatable seasonal festivals, rotating Bountiful bounties (this is the only place random bounties appear)…" — that's what these four pools and two decrees are. Before Founder's Day, nobody should be rolling random notices off Oda's board; the story's own bounty beat is the scripted Q37 one.

**Gating note for whoever wires the physical board:** these pool/decree JSON files carry no stage logic — Bountiful has none. Gate access at the block, not the data: either don't place/activate the `bountiful:bountyboard` until `/valley finale act5` runs, or have the Act V finale hand out (or `/give`) the `cozy`/`tech` `bountiful:decree` items for the first time at that point, so there's nothing to slot into the board earlier. `valley_gates.js` already replaces the board's diamond in its crafting recipe per the project brief — do the same "cheap now" treatment for the decree recipe (paper + stick + gold ingot + purple dye) if it should be craftable pre-Act-V for flavor, or leave it as-is if it should stay a `/give` from the finale.

## The two lanes

- **`cozy`** — Marnie/Oda-flavoured chores: crops, wool, fish, cooked meals. Pays seeds, decor (candles, sconces, shelving, plushies), emeralds, honey.
- **`tech`** — ore/alloy/machine-part chores: ingots, dusts, geolosys ore samples, Thermal gears/servos. Pays small Thermal/AE2 parts, redstone, decor.

**Neither decree pays Valley Scrip, and that is the point.** Both pools used to carry four `valley:scrip` entries each (one per rarity tier) at `weightMult` 1.8–2.5, well above every other entry — and the board is repeatable forever and craftable for one copper ingot. Together with Oda's standing order, that made Scrip infinitely printable, and the 350 Scrip Act V asks for (Q85 = 120, Q86 = 80, the Works Deed = 150) stopped being a gate at all. Scrip is now **hand-authored only**: quest rewards, festival baskets, arc closures, and one 8-Scrip standing order. The pools pay goods.

What the board is *for*, then, is the thing Scrip cannot buy: a reason to fish, farm, shear and smelt after the story stops handing out quests, paid in the decor, seeds and parts that make the valley look lived-in. If a future edit wants a repeatable Scrip trickle, it has to come with a sink of the same size — an uncapped faucet on a hand-authored currency is what this removal fixed.

## `valley:bounty_receipt`

Both reward pools include a `valley:bounty_receipt` entry (low `unitWorth`, `weightMult` 1.0, so it shows up reasonably often without crowding out the goods). This exists purely so a future KubeJS `InventoryChanged` or crafting-style listener can count "how many bounties has this team turned in" for an Endless Seasons stat/advancement — the same C8 fix noted in the story doc, since Bountiful completion itself is invisible to everything else. It's already appended to `story/quests/_custom_ids.txt`; register the actual item in `valley_items.js` alongside the rest of the `valley:` namespace before shipping.

## The Bountiful schema, as read from the mod's own data

**Pool file** (`bounty_pools/<namespace>/<pool_name>.json`):
```json
{
  "content": {
    "<entry_id>": {
      "type": "item",
      "rarity": "UNCOMMON",
      "content": "modid:item_id",
      "amount": { "min": 4, "max": 10 },
      "unitWorth": 100,
      "weightMult": 1.3
    }
  }
}
```
- `type` — `item` (a concrete item stack), `item_tag` (an `#modid:tag`, e.g. `minecraft:planks` — needs a `bountiful.entry.<id>` lang key since there's no single item to name it after), `entity` (mob kill count — supports `timeMult` to scale time-to-complete), or `criteria` (an advancement-style trigger with a `conditions` block, e.g. brewing a specific potion). We only used `item` — every entry names a real, single item, so Bountiful can derive its display name automatically and no lang file is needed.
- `rarity` — omit for `Common` (the default), or `UNCOMMON` / `RARE` / `EPIC`. Determines which tier bucket a bounty notice draws the entry from.
- `amount.min` / `amount.max` — random count range for an objective (how many the player must turn in) or a reward (how many they receive).
- `unitWorth` — the value of **one unit** of the item. The board sums an objective's `unitWorth × amount` to hit a tier's target "worth," then fills the reward side to roughly the same worth from the reward pool. Keep worth-per-item roughly proportional to how annoying/rare the item actually is to get — that's the entire balancing lever.
- `weightMult` — multiplies selection likelihood within its rarity tier (default 1.0). Above 1 = picked more often (we use this for scrip); below 1 = picked less often (used here for anything that would otherwise dominate — big machine parts, jackpot plushies).
- `nbt` / `forbids` — optional, for reward items with a real NBT state (e.g. undamaged tools) and to exclude some other pool entry from co-occurring with this one. Unused here; nothing in either lane needs NBT-exact matching.

**Decree file** (`bounty_decrees/<namespace>/<decree_name>.json`):
```json
{ "objectives": ["pool_a", "pool_b"], "rewards": ["pool_c"] }
```
Pool names are looked up by filename (no extension) inside `bounty_pools/<namespace>/`. A decree is obtained as a `bountiful:decree` item (crafted: paper + 2 sticks + gold ingot + purple dye, or `/give`) and placed into a `bountiful:bountyboard` block to make that board roll only from the named decree's pools; a board with no decree slotted rolls from every registered decree.

## How to add a bounty

1. Confirm the item id is real: `jq -r '.items[]' scratch/ids.json | grep <word>` — the compiler (and Bountiful itself, at runtime) will silently no-op or error on an id that isn't actually registered.
2. Add an entry to the matching `_objectives.json` (something to ask for) or `_rewards.json` (something to pay). Pick a `rarity` tier by how much effort the item costs the player, and a `unitWorth` roughly proportional to the other entries at that tier (use the existing entries as your ruler — don't eyeball a fresh scale).
3. Validate: `jq empty pack/kubejs/data/bountiful/bounty_pools/valley/<file>.json`.
4. New objective/reward pool files (a third lane, say) need a matching decree file listing them, or need to be appended to `cozy.json` / `tech.json`'s `objectives`/`rewards` arrays.
5. If you use a brand-new `valley:` custom item as a reward, add it to `valley_items.js` and to `story/quests/_custom_ids.txt` — same rule as quest JSON.
6. In-game: `/reload` (or restart) picks up the new data; break and re-place (or right-click) an existing board to force a re-roll, or wait for its normal refresh.

No lang file is required for anything currently in these four pools — every entry is a concrete `item` type, which the mod names from the item's own translation key.
