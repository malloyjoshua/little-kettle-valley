# Items — batch 1

49 handmade 16x16 item textures (plus one block face) for **Little Kettle Valley**, drawn in the
project pixel DSL and rendered with `tools/scripts/pixel.py`.

## Files
- `build.py` — generator script. Builds every icon out of small pixel-drawing helpers
  (`disc`, `rect`, `frame`, `hline`/`vline`, `px`) rather than hand-typed row strings, so it's
  easy to re-run and tweak. Writes `batch1.json`.
- `batch1.json` — the 16x16 DSL rows consumed by `pixel.py render`.
- `png/` — one 16x16 RGBA PNG per icon, named after the item.
- `sheet_batch1.png` — 10x contact sheet (all 49 icons, labeled) for art-directing at a glance.

Regenerate with:
```
tools/venv/bin/python media/items/build.py
tools/venv/bin/python tools/scripts/pixel.py render media/items/batch1.json media/items/png
tools/venv/bin/python tools/scripts/pixel.py check media/items/png
tools/venv/bin/python tools/scripts/pixel.py sheet media/items/png media/items/sheet_batch1.png 10
```

## What's in the batch
- **Documents**: `scrip`, `letter`, `deed`, `deed_works`, `kettle_deed`, `bounty_receipt`,
  `catalogue`, `odas_ledger`, `turbine_notes`, `deep_survey`, `framed_town_map`, `place_setting`
- **Raw materials**: `green_oak_plank`, `seasoned_oak_board`, `lake_sand`, `washed_silica`,
  `spring_water`
- **Works machine parts**: `works_power_tap`, `kettle_plate_a`, `kettle_plate_b`
- **Tools**: `ice_auger`, `dredge_net`, `oda_broom`
- **Hero item**: `copper_kettle_trophy` — a proper teapot silhouette (looped handle, lidded
  body with knob, spouted opening) so it reads distinctly from the plainer `scrip` coin.
- **Crates & parcels**: `delivery_crate`, `courier_parcel`, `feast_crate`, `hen_crate`,
  `cow_crate`, `sheep_crate`, `chicken_feed`, `firewood_bundle`
- **Cozy/comfort**: `blanket`, `winter_cloak`, `winter_tonic`, `winter_tomato`, `paper_lantern`,
  `josies_lantern`, `hearthkeepers_lantern`, `plushie_token`
- **Resident tokens**: `token_marnie` (blush/bread), `token_bram` (stone/gear), `token_oda`
  (gold/coin), `token_nella` (water blue/fish), `token_halden` (green/leaf), `token_tobin`
  (copper/pick), `token_wisp` (sage/lily pad), `token_pip` (red/egg) — same round wax-seal
  template (dark ring, notched outer edge, small glyph), recolored per resident.
- **Block**: `town_anchor` — Surveyor's Stake, a tileable-ish stone-brick plinth face with a
  copper kettle stamped in the center.

## Style notes
- Every icon keeps a 1-2px transparent margin and a darker one-step outline, vanilla-MC style.
- Crate items (`delivery_crate`, `feast_crate`, the three animal crates) share one `crate()`
  base shape with a paper label band, so the set reads as a family.
- The two nameplates use a hand-drawn 3x5 pixel font (`FONT3x5` in `build.py`) for a legible
  stamped "A" / "B" at this scale — freehand letterforms didn't read at 16px.
- Iterated once on a first full render: reworked the kettle trophy (was an unclear blob),
  the three animal-crate faces, the firewood bundle (was reading as a fence/grate), the
  feast-crate bread, and a few token glyphs (fish, pick, gear) for legibility.
