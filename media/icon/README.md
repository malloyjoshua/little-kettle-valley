# Icon — Little Kettle Valley

Launcher / server icon: a copper kettle on a cream badge, hand-authored 32x32
pixel art, upscaled with nearest-neighbor (crisp pixels, no blur/antialiasing).

Run `tools/venv/bin/python media/icon/build.py` to rebuild everything in this
folder from scratch.

## What's drawn (32x32 native canvas)
- **Badge**: rounded-square cream (`cream`) background with a 2px sage
  (`sage`) rim, corners cut with a small radius so it reads as a soft badge
  rather than a hard square.
- **Kettle body**: squat copper (`copper`) belly with a copper_dark
  (`copper_dark`) shadow on the lower-right, a copper_light (`copper_light`)
  rim stroke on the upper-left edge, and a small cream (`cream`) highlight
  blob for shine.
- **Lid + knob + handle**: kettle_dark (`kettle_dark`) throughout. The handle
  is a single wide overhead arc with its feet planted low on the body's own
  shoulders (not on the lid) — on purpose, so the lid/knob sit *inside* one
  arch instead of being flanked by two symmetric loops, which at 32px reads
  as a face (learned this the hard way — v1 looked like a bear).
- **Spout**: a short copper wedge jutting up-right from the body with a
  kettle_dark tip.
- **Steam**: two puffs rising diagonally from the spout tip — a plain steam
  (`steam`) puff, and above it a heart-shaped puff in blush (`blush`), per
  spec.

All colors are pulled live from `media/palette.json` — no hardcoded hex in
`build.py`.

## Outputs
| File | Size | Purpose |
|---|---|---|
| `icon_32.png` | 32x32 | launcher tile |
| `icon_64.png` | 64x64 | Forge/Minecraft `server-icon.png` (verified exactly 64x64 RGBA) |
| `icon_128.png` | 128x128 | Prism/MultiMC instance icon |
| `icon_512.png` | 512x512 | store-quality / press-kit size |
| `mark_128.png`, `mark_512.png` | 128 / 512 | kettle mark alone, transparent background (no badge) |
| `_preview_32_at_6x.png` | — | quick art-director contact print, not a deliverable |

`icon.icns` was explicitly out of scope for this pass.

## Method
Unlike the 16x16 icons elsewhere in the pack (rendered through
`tools/scripts/pixel.py`'s row-string DSL), this icon is built with shape
math directly in `build.py`: rounded-rect masks (circular corner cut),
ellipse fills for the body/lid/handle, a manually stepped diagonal wedge for
the spout, and two small hand-drawn bitmaps (`STEAM_PUFF`, `STEAM_HEART`)
stamped in for the steam. Chosen over the DSL because a 32px canvas needs
finer shape control than a 16-character grid gives you, and ellipse/rounded-
rect math is easier to nudge iteratively than re-typing a character grid by
hand. All fills are exact-integer pixel tests (no anti-aliasing), so NEAREST
upscaling stays perfectly crisp at every output size.

## Iteration notes
Went through 4 passes on the top of the kettle (lid + knob + handle) before
it stopped reading as a face — the first version had a big full-ring handle
that boxed the knob into two round "eye" gaps. Fixed by shrinking the knob
to a near-single-pixel dot and widening/lowering the handle's feet onto the
body's shoulders so it's one wide arch, not two flanking loops. Also nudged
the steam puffs inward once, since the top heart puff was clipping the
badge's rounded top-right corner.
