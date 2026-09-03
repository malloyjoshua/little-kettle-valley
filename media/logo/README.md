# Logo — Little Kettle Valley

Title-screen wordmark + edition strip, built entirely from an original
hand-drawn pixel font (no vanilla Minecraft artwork reused).

Run `tools/venv/bin/python media/logo/build.py` to rebuild everything in
this folder from scratch.

## Outputs
| File | Size | Purpose |
|---|---|---|
| `minecraft.png` | 1024x256 RGBA | title-screen logo. Game draws rows 0-175 as a 274x44 logo; rows 176-255 are fully transparent (verified by the build script). |
| `edition.png` | 512x64 RGBA | small strip under the logo. Game draws rows 0-54 as a 128x14 strip. |
| `_preview.png` | — | quick art-director contact print (logo stacked over the edition strip on a night background), not a deliverable. |

## What's drawn
- **Wordmark**: "LITTLE KETTLE VALLEY" set in an original 7x9-pixel blocky
  font (hand-authored per glyph in `build.py`, not a system font and not
  vanilla Minecraft's logo font) — copper fill, copper_dark drop shadow,
  copper_light bevel highlight on each letter's top/left edge, and a 1px
  ink outline around the whole silhouette so it stays legible over any
  panorama tile behind it.
- **Crest**: the kettle mark from `media/icon/build.py` (`build_mark()`),
  reused so the brand mark stays consistent across icon/logo, scaled to
  64x64 with its own ink halo, centered above the wordmark.
- **Edition strip**: "FORGE 1.20.1" in the same font at a smaller scale,
  sage/cream coloring, centered in the 512x64 strip.

## Method
Same shape-math approach as `media/icon/build.py`: a small dict of 7x9
glyph bitmaps (`#`/`.` strings) covers exactly the letters and digits the
two lines need (L I T E K V A Y, F O R G, digits 0/1/2, period). A layout
function concatenates glyphs into a native-resolution boolean grid, then
`render_wordmark()` draws it in four passes — outline, drop shadow, flat
fill, bevel highlight — before scaling up with `Image.NEAREST` so the
pixels stay crisp at any size. The kettle crest is pulled in by importing
`media/icon/build.py` directly (`importlib`) rather than copy-pasting the
kettle-drawing code.

## Iteration notes
First pass sized the title at scale 6 with the crest at 96px, which blew
past the row-175 budget the vanilla logo texture leaves for content (title
bottom landed at row 196). Dropped the crest to 64px and the title to
scale 5, and the edition strip from scale 4 to scale 3 for the same
reason on its own 54-row budget — both now clear their limits with a
comfortable margin. Checked the wordmark against both a night background
and a cream background; the ink outline keeps it readable either way.
