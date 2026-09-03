# Panorama — Little Kettle Valley

The six cube faces the vanilla title screen slowly rotates through: a dusk
valley skyline with lit cottages and lamp posts along a snowy ridge, a
winding road in the foreground, and a starry sky.

Run `tools/venv/bin/python media/panorama/build.py` to rebuild everything
in this folder from scratch.

## Outputs
| File | Size | Face |
|---|---|---|
| `panorama_0.png` .. `panorama_3.png` | 1024x1024 RGB each | front / right / back / left — four adjacent slices of one continuous 4096x1024 painted strip |
| `panorama_4.png` | 1024x1024 RGB | up — soft night zenith with stars |
| `panorama_5.png` | 1024x1024 RGB | down — snowy ground texture |
| `_preview_strip.png` | 1536x256 | six faces side by side at small size, art-director contact sheet, not a deliverable |

## What's drawn
- **Sky**: vertical night -> sky -> dusk gradient (same for every column),
  built with numpy so it's a smooth blend rather than banded.
- **Three parallax hill silhouettes** (far/mid/near), each a sine-wave
  horizon (`hill_curve`) with periods that divide the 4096 strip width
  evenly, so the rolling shape repeats cleanly across the loop instead of
  showing a seam.
- **Cottages + lamp posts**: eight small clusters strung along the near
  ridge (every 512px, so each 1024-wide face gets two), each a paper-cream
  cottage with a copper_dark roof, a lit window with a soft glow, a small
  door, and one or two nearby lamp posts (copper pole + glowing lamp head).
- **Foreground**: a snow gradient (silver -> wool) with one gently winding
  copper/dusk road that tapers with distance, plus a moon (concentric soft
  cream glows) and scattered stars/falling snow drawn on a transparent
  overlay and composited over the painted base.
- **Up face**: a radial night/sky gradient (lighter at the zenith, darker
  at the rim) with its own star scatter.
- **Down face**: a numpy noise-textured snow plane with a soft vignette,
  a few faint footprint pairs, and small sage tuft flecks.

## Method
The four side faces are generated as one continuous 4096-wide strip (numpy
for the gradient/hill/ground fills, PIL `ImageDraw` on an RGBA overlay for
cottages/lamps/stars/snow/moon), then cropped into four 1024x1024 tiles —
so the horizon, road, and star field are genuinely continuous across the
face-to-face boundaries instead of four independently-random images. Up
and down faces are generated standalone since they don't need to match
the rotation. All colors come from `media/palette.json`; nothing here
reuses vanilla Minecraft artwork.

## Iteration notes
First pass had two problems caught on review: the far hill's haze color
was a muddy olive/khaki (a straight dusk/sage_dark blend pulled too much
green), fixed by blending in some sky-blue for a cooler atmospheric-
perspective haze; and the foreground road wound so fast and wide (large
sine amplitude relative to face width) that it drew a sharp hairpin hook
instead of a gentle curve, fixed by slowing the winding rate and shrinking
the amplitude so it reads as one soft path near the front/right faces.
Cottages were also hard to read against the dark hill in v1 (near-black
walls, oversized glow blobs reading as bushes) — repainted with pale
paper-cream walls, a smaller/tighter window glow, and an added door for
scale, which reads clearly even at the small in-game panorama size.
