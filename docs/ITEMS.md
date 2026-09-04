# Item lore — the 48 custom items

Every custom item in the pack now carries two lines of gray italic lore. They are
authored in one file, `pack/kubejs/client_scripts/valley_lore.js`, and delivered
through `ItemEvents.tooltip`. Nothing else about the items changed: no display
name, no id, no stack size, no rarity.

## The rule these were written to

`docs/writing-craft.md` §4, row **Item lore**: *2 lines × 50 characters. A fact
about the owner or the making, never the stats.* The worked example is Oda's
brass key — **"Her initials scratched off. Yours scratched on."**

So every entry below is shaped the same way:

- **Line 1 is the object.** What it is, what it is made of, whose hand it came
  out of. A concrete noun the player can see (criterion 1, Picture).
- **Line 2 is the turn.** The thing the object gives away about whoever handled
  it — a number, a date, a habit, a refusal. Never a feeling named out loud
  (criterion 2, Gap).

Measured: 49 entries, 98 lines, longest line **48 characters**, none over the
50-character cap, none over two lines, no line duplicated, no line verbatim from
the quest JSON, `story/npcs.json` or `story-final.md`, zero banned-list hits.

## Whose hand each tag is in

| Voice | How it sounds here |
|---|---|
| **Josie** | chalk and paper; a number or a time of night, and the dry half after the hard sentence — *"Older than Josie, and she was seventy-one."* |
| **Marnie** | feeds you instead of asking; her tags are about who is coming and what is already baked |
| **Bram** | the part, not the feeling — *"He would not call it help. He called it holding."* |
| **Oda** | ledger hand: counts, dates, files, does not round up |
| **Nella** | undersells, and is already damp |
| **Halden** | unhurried; the kettle is always already on |
| **Tobin** | right about the rock, terrible at saying so |
| **Wisp** | sentences slightly wrong, and warmer for it |
| **Pip** | names things, in capitals |

## The table

### Currency and paper

| Item | id | Lore |
|---|---|---|
| Valley Scrip | `scrip` | Oda writes the number on by hand. · She has never once rounded up. |
| Josie's Letter | `letter` | Four pages, and the fourth one is a map. · Written a year early, in case. |
| The Kettle Farm Deed | `deed` | The farm, the chimney, eleven feet of porch. · She left the top line blank for four years. |
| The Works Deed | `deed_works` | Eight names under it. Bram signed as witness. · The Works belongs to whoever stayed. |
| Kettle Family Deed | `kettle_deed` | Your name on the line she left blank. · Filed the afternoon Pip rang the bell. |
| Bounty Receipt | `bounty_receipt` | Torn off the board, ticked at the counter. · Oda files them. There is a drawer of them. |

### Gate ingredients

| Item | id | Lore |
|---|---|---|
| Green Oak Plank | `green_oak_plank` | Cut this spring. Still heavy with the wet. · Bend one and it stays bent, so nobody does. |
| Seasoned Oak Board | `seasoned_oak_board` | Two minutes of furnace heat, and it holds. · Josie was insufferable about the method. |
| Lake Sand | `lake_sand` | Dredged off Nella's boat, sixteen a pull. · She never once let you into the water. |
| Washed Silica | `washed_silica` | Lake sand, washed until it stops squeaking. · Bram did his first batch four times. |
| Spring Water | `spring_water` | From the spring above the hedge garden. · Josie filled her jars here, never for tea. |
| Works Power Tap | `works_power_tap` | Comes off the line at the inn's back wall. · Bram ran the duct. Marnie got a fridge. |
| Josie's Turbine Notes | `turbine_notes` | Forty pages of turbine sums, in her hand. · The margins argue with the book she bought. |

### The buried secret

| Item | id | Lore |
|---|---|---|
| Kettle Plate A | `kettle_plate_a` | Copper, scratched over in her shorthand. · Halden could read it four years ago. |
| Kettle Plate B | `kettle_plate_b` | The second half. It went out with a trader. · He could not read a word of it. |
| Tobin's Deep Survey | `deep_survey` | Tobin read the echo and drew the seam. · Signed, dated, and right, which he expected. |

### Deliveries and the order board

| Item | id | Lore |
|---|---|---|
| Delivery Crate | `delivery_crate` | It fills itself now, which took a year. · Oda counts the contents anyway. |
| Courier Parcel | `courier_parcel` | Paper, string, and a name in Pip's capitals. · This one says HENRIETTA. He did not explain. |
| Feast Crate | `feast_crate` | One of each dish, packed for Founder's Day. · Marnie set eight aside before anyone ate. |

### Livestock and smallholding

| Item | id | Lore |
|---|---|---|
| Hen Crate | `hen_crate` | Two hens and a rooster, slats and straw. · Do not name the rooster. Marnie means it. |
| Cow Crate | `cow_crate` | Came up on the wagon, counted at both ends. · Oda's end and yours. Hers was right. |
| Sheep Crate | `sheep_crate` | Slats, straw, and one ewe with a torn ear. · Nella carried it up from the pier herself. |
| Chicken Feed | `chicken_feed` | Marnie's mix: barley, grit, crushed shell. · She mixes it in a chipped bread bowl. |
| Dredge Net | `dredge_net` | Nella's net, mended in four colours. · She had it in the boat the whole time. |
| Ice Auger | `ice_auger` | Nella sharpened it in October, from habit. · She has no lake from December to March. |

### Winter and the hearth

| Item | id | Lore |
|---|---|---|
| Firewood Bundle | `firewood_bundle` | Split, stacked, and tied in fours. · Sixteen to a house. Oda counted them out. |
| Wool Blanket | `blanket` | Eight wool round one string, on the loom. · Beds get made before the people arrive. |
| Winter Cloak | `winter_cloak` | Marnie's, and she is taller than you. · She had it out of the chest before you asked. |
| Winter Tonic | `winter_tonic` | Halden's still: a flask, a leaf, one sugar. · Nobody in the valley got ill that winter. |
| Winter Tomato | `winter_tomato` | Grown in February, under Nella's glass. · Marnie ate the first one in the doorway. |

### Light: the Lantern Road

| Item | id | Lore |
|---|---|---|
| Paper Lantern | `paper_lantern` | Eight sheets of paper round one torch. · Nella made forty and said nobody would come. |
| Josie's Lantern | `josies_lantern` | Off the fortieth post, on Josie's porch. · She asked, on the last page, to be on the line. |
| Hearthkeeper's Lantern | `hearthkeepers_lantern` | Lit the night the valley kept its own lights. · It has not been out since. Marnie checks. |

### Trophies, decor and shop stock

| Item | id | Lore |
|---|---|---|
| Plushie Token | `plushie_token` | One token, one shelf, one plushie. · Pip has spent eleven. Oda wrote each one down. |
| The Copper Kettle | `copper_kettle_trophy` | Older than Josie, and she was seventy-one. · It hangs over your hearth now. Put it on. |
| Place Setting | `place_setting` | A bowl, a brick, an iron and a copper ingot. · Marnie set twelve. Three chairs stayed empty. |
| Oda's Broom | `oda_broom` | Off the store's back door, worn to a wedge. · Eleven years of sweeping an empty shop. |
| Oda's Ledger | `odas_ledger` | Eleven years of red ink, in one small hand. · She held it long enough. Now you hold it. |
| Framed Town Map | `framed_town_map` | The mill, the square, the lake, forty posts. · Drawn before the last seventeen went in. |
| Oda's Catalogue | `catalogue` | Oda's full stock list, priced in her hand. · Two pages stayed blank for eleven years. |

### The eight resident tokens

Each token is the physical thing that resident put in your hand when their chain
opened, so each one is a different object rather than eight copies of a coin.

| Item | id | Lore |
|---|---|---|
| Marnie's Word | `token_marnie` | A bread tag off the loaf she carried up. · It was in her apron the whole walk. |
| Bram's Word | `token_bram` | The Millwright's Bolt, out of his palm. · He would not call it help. He called it holding. |
| Oda's Word | `token_oda` | A ledger page, folded twice, corner initialled. · She dated it. Oda dates everything. |
| Nella's Word | `token_nella` | A brass ferry chit, green round the edges. · She handed it over without getting up. |
| Halden's Word | `token_halden` | A sprig of hedge, tied with garden twine. · He gave it while the kettle was still on. |
| Tobin's Word | `token_tobin` | A thumb of copper ore, marked in pink chalk. · He explained it twice. It got no clearer. |
| Wisp's Word | `token_wisp` | A reed ring, woven mid-sentence. · Is for neighbour. The near kind, not far. |
| Pip's Word | `token_pip` | A duck feather in a folded paper sleeve. · Biscuit's. The sleeve says BISCUIT. |

### The block item

| Item | id | Lore |
|---|---|---|
| Surveyor's Stake | `town_anchor` | Bram's stake, wrapped in a rag, chalked K. · He surveyed that flat twice and never drove it. |

## Two items deliberately left alone

- **The Kettle Farm Compass** is a vanilla `minecraft:compass` whose display name
  and `Lore` are set by NBT in `pack/kubejs/server_scripts/valley_core.js`
  (*"It points at the hearth."*). It is not registered in `valley_items.js`, and
  it is **not** in the lore table — a tooltip entry would print a second line
  underneath the one it already has. Its formatting is the model everything here
  copies: `"color":"gray","italic":true`.
- **Every display name is unchanged.** The naming rule in §3 bans names that
  would work unchanged in another story; the roster passes it already (the
  load-bearing nouns — Kettle, the Works, the Lantern Road, Josie, Oda — are in
  the names that matter, and the rest are plain material and tool names doing a
  mechanical job). So `pack/kubejs/assets/valley/lang/en_us.json` was not
  touched, and neither were the ids in `story/quests/_custom_ids.txt`.

## Where it runs

`ItemEvents.tooltip` is client-only — it does not exist server-side and throws on
load in `server_scripts/`, which is the same reason `hide.js` lives where it
does. `kubejs/` is a pack folder synced to clients, and `kubejs/client_scripts/hide.js`
is already listed in `pack/index.toml`, so **`packwiz refresh` picks this file up
the same way**. Run refresh before any `tools/scripts/sync_server.sh`, or the
file never reaches a client.
