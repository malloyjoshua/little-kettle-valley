#!/usr/bin/env python3
"""
Build installers/windows/LittleKettleValley.ico from the pixel-art kettle icon in media/icon/.

Multi-size .ico (16/24/32/48/64/128/256) so Windows picks the right one for the taskbar, the
Start Menu tile, Explorer detail views and the installer's own title bar. Every size is derived
with NEAREST resampling from the nearest native render so the pixel art stays crisp -- no blur.

The generated .ico is committed, so the GitHub runner does not need Pillow.

    tools/venv/bin/python installers/windows/make_icon.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

SIZES = [16, 24, 32, 48, 64, 128, 256]


def main() -> int:
    here = Path(__file__).resolve().parent
    repo_root = here.parents[1]
    icon_dir = repo_root / "media" / "icon"

    # Native renders available from media/icon/build.py, largest first.
    sources = {}
    for native in (512, 128, 64, 32):
        p = icon_dir / f"icon_{native}.png"
        if p.is_file():
            sources[native] = Image.open(p).convert("RGBA")
    if not sources:
        print(f"no icon_*.png found in {icon_dir}", file=sys.stderr)
        return 1

    frames = []
    for size in SIZES:
        # Pick the smallest native render that is an exact integer multiple/divisor away, else the
        # smallest one that is >= the target so we only ever downscale.
        exact = [n for n in sources if n == size]
        if exact:
            frames.append(sources[size].copy())
            continue
        bigger = sorted(n for n in sources if n >= size)
        base = sources[bigger[0]] if bigger else sources[max(sources)]
        frames.append(base.resize((size, size), Image.NEAREST))

    out = here / "LittleKettleValley.ico"
    # append_images lets us hand Pillow the exact NEAREST-resampled frame for every size; without
    # it the ICO plugin would re-resize the base image with BICUBIC and smear the pixel art.
    frames[-1].save(
        out,
        format="ICO",
        sizes=[(f.width, f.height) for f in frames],
        append_images=frames[:-1],
    )
    print(f"wrote {out} ({out.stat().st_size} B) sizes={[f.width for f in frames]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
