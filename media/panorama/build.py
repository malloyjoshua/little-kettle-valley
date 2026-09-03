#!/usr/bin/env python3
"""Little Kettle Valley - title screen panorama builder.

Builds the six cube faces the vanilla title screen slowly rotates through.
The four side faces (0 front, 1 right, 2 back, 3 left) are sliced from one
continuous 4096x1024 painted strip - a dusk valley skyline: night-to-dusk
sky, three parallax hill silhouettes, a handful of lit cottages + lamp
posts along the ridge, a winding snowy road in the foreground, scattered
stars and falling snow. Because the strip is generated from periodic
functions of x (period divides 4096 exactly), the four slices join up into
a believable 360-degree loop. Face 4 (up) is a soft night zenith with
stars; face 5 (down) is a snowy ground texture.

All colors come from media/palette.json; nothing here reuses vanilla
Minecraft artwork.

Run: tools/venv/bin/python media/panorama/build.py
"""
import json
import math
import pathlib
import random

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
PAL = json.loads((ROOT / "media" / "palette.json").read_text())

rng = random.Random(20260903)


def rgb(name):
    h = PAL["colors"][name].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgba(name, a=255):
    return rgb(name) + (a,)


STRIP_W, H = 4096, 1024
FACE = 1024

SKY_NIGHT = np.array(rgb("night"), dtype=np.float32)
SKY_MID = np.array(rgb("sky"), dtype=np.float32)
SKY_DUSK = np.array(rgb("dusk"), dtype=np.float32)
SNOW = np.array(rgb("wool"), dtype=np.float32)
SNOW_SHADE = np.array(rgb("silver"), dtype=np.float32)


def lerp(a, b, t):
    t = np.clip(t, 0.0, 1.0)
    return a * (1 - t)[..., None] + b * t[..., None]


def build_sky(x_cols):
    """Vertical night->dusk gradient, same for every column."""
    y = np.arange(H, dtype=np.float32)
    t1 = np.clip((y - 0) / 520.0, 0, 1)          # night -> mid
    t2 = np.clip((y - 380) / 260.0, 0, 1)        # mid -> dusk near horizon
    col = lerp(SKY_NIGHT, SKY_MID, t1)
    col = lerp(col, SKY_DUSK, t2)
    return np.repeat(col[:, None, :], x_cols, axis=1)  # (H, W, 3)


def hill_curve(x, base, amps_periods, phase=0.0):
    y = np.full_like(x, base, dtype=np.float32)
    for amp, per in amps_periods:
        y = y + amp * np.sin(2 * math.pi * x / per + phase)
    return y


def paint_strip():
    xs = np.arange(STRIP_W, dtype=np.float32)
    img = build_sky(STRIP_W)  # (H, W, 3) float32

    yy = np.arange(H, dtype=np.float32)[:, None]  # (H,1)

    # --- three parallax hill silhouettes, far -> near ---------------------
    far = hill_curve(xs, 560, [(18, 2048), (7, 512)])[None, :]
    far_col = (0.45 * SKY_DUSK + 0.30 * np.array(rgb("sage_dark"), np.float32)
               + 0.25 * SKY_MID)
    mask = yy >= far
    img = np.where(mask[..., None], far_col, img)

    mid = hill_curve(xs, 660, [(26, 1024), (10, 256)], phase=1.3)[None, :]
    mid_col = np.array(rgb("sage_dark"), np.float32) * 0.9
    mask = yy >= mid
    img = np.where(mask[..., None], mid_col, img)

    near = hill_curve(xs, 760, [(22, 682), (9, 170)], phase=2.6)[None, :]
    near_col = np.array(rgb("night"), np.float32) * 0.55 + np.array(rgb("sage_dark"), np.float32) * 0.25
    mask = yy >= near
    img = np.where(mask[..., None], near_col, img)

    # --- foreground snow, gradient + gentle winding road -------------------
    ground_top = 800.0
    gt = np.clip((yy - ground_top) / (H - ground_top), 0, 1)
    ground_col = lerp(SNOW_SHADE, SNOW, gt[:, 0])
    ground_mask = yy >= ground_top
    img = np.where(ground_mask[..., None], ground_col[:, None, :].repeat(STRIP_W, axis=1), img)

    road_col = np.array(rgb("copper_light"), np.float32) * 0.55 + np.array(rgb("dusk"), np.float32) * 0.35
    for y in range(int(ground_top), H, 2):
        t = (y - ground_top) / (H - ground_top)
        half_w = 5 + 46 * t
        cx = (1780 + 220 * math.sin(y * 0.006)) % STRIP_W  # one gentle path near face 1/2
        lo = int(cx - half_w)
        span = int(half_w * 2)
        idx = (np.arange(lo, lo + span) % STRIP_W)
        img[y:y + 2, idx] = road_col

    return np.clip(img, 0, 255).astype(np.uint8)


def draw_cottage(draw, cx, base_y, seed):
    r = random.Random(seed)
    w = r.randint(30, 42)
    h = r.randint(22, 30)
    wall = rgba("paper")
    wall_shade = rgba("wood_dark")
    roof = rgba("copper_dark")
    door = rgba("kettle_dark")
    lit = rgba("lamp", 245)
    glow = rgba("lamp_glow", 90)
    x0, y0 = cx - w // 2, base_y - h
    draw.rectangle([x0, y0, x0 + w, base_y], fill=wall)
    draw.rectangle([x0 + w - 4, y0, x0 + w, base_y], fill=wall_shade)  # side shade
    draw.polygon([(x0 - 6, y0), (x0 + w // 2, y0 - 16), (x0 + w + 6, y0)], fill=roof)
    dw = 6
    draw.rectangle([cx - dw // 2, base_y - 14, cx + dw // 2, base_y], fill=door)
    wx, wy = x0 + w - 13, y0 + h // 2 - 4
    for rad, al in ((10, 45), (5, 110)):
        draw.ellipse([wx + 4 - rad, wy + 4 - rad, wx + 4 + rad, wy + 4 + rad], fill=(*rgb("lamp_glow"), al))
    draw.rectangle([wx, wy, wx + 8, wy + 8], fill=lit)


def draw_lamp(draw, x, ground_y):
    pole = rgba("copper_dark")
    head = rgba("lamp")
    glow = rgba("lamp_glow", 55)
    top = ground_y - 46
    draw.line([(x, ground_y), (x, top)], fill=pole, width=3)
    for rad in (22, 13):
        draw.ellipse([x - rad, top - rad, x + rad, top + rad], fill=glow)
    draw.ellipse([x - 4, top - 5, x + 4, top + 3], fill=head)


def scatter_stars(draw, seed, count, y_max, x_span, cream_w=None):
    r = random.Random(seed)
    for _ in range(count):
        x = r.uniform(0, x_span)
        y = r.uniform(20, y_max)
        size = r.choice([1, 1, 1, 2])
        a = r.randint(90, 220)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=rgba("cream", a))


def scatter_snow(draw, seed, count, x_span, y_span):
    r = random.Random(seed)
    for _ in range(count):
        x = r.uniform(0, x_span)
        y = r.uniform(0, y_span)
        size = r.choice([1, 1, 2])
        a = r.randint(60, 170)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=rgba("wool", a))


def build_faces_0_3():
    base = Image.fromarray(paint_strip(), "RGB").convert("RGBA")
    overlay = Image.new("RGBA", (STRIP_W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")

    # moon, one soft glow, fixed spot
    mx, my = 2900, 190
    for rad, a in ((110, 22), (70, 40), (40, 70), (22, 140)):
        d.ellipse([mx - rad, my - rad, mx + rad, my + rad], fill=rgba("cream", a))

    scatter_stars(d, seed=1, count=420, y_max=430, x_span=STRIP_W)
    scatter_snow(d, seed=2, count=1400, x_span=STRIP_W, y_span=H)

    # cottages + lamp posts strung along the near ridge, period 512 so the
    # four 1024-wide face slices each get exactly two clusters
    for i, cx in enumerate(range(160, STRIP_W, 512)):
        base_y = int(hill_curve(np.array([float(cx)]), 760, [(22, 682), (9, 170)], phase=2.6)[0]) + 2
        draw_cottage(d, cx, base_y, seed=100 + i)
        draw_lamp(d, cx + 34, base_y + 4)
        if i % 2 == 0:
            draw_lamp(d, cx - 60, base_y + 30)

    full = Image.alpha_composite(base, overlay).convert("RGB")
    names = ["panorama_0.png", "panorama_1.png", "panorama_2.png", "panorama_3.png"]
    for i, name in enumerate(names):
        tile = full.crop((i * FACE, 0, i * FACE + FACE, H))
        tile.save(OUT / name)
        print(f"{name} <- strip x[{i*FACE}:{i*FACE+FACE}]")


def build_face_up():
    yy, xx = np.mgrid[0:FACE, 0:FACE].astype(np.float32)
    cx, cy = FACE / 2, FACE / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (FACE * 0.72)
    t = np.clip(dist, 0, 1)
    zenith = np.array(rgb("night"), np.float32) * 0.7 + np.array(rgb("sky"), np.float32) * 0.3
    edge = np.array(rgb("night"), np.float32)
    col = lerp(zenith, edge, t)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    overlay = Image.new("RGBA", (FACE, FACE), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    scatter_stars(d, seed=7, count=260, y_max=FACE, x_span=FACE)
    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(OUT / "panorama_4.png")
    print("panorama_4.png <- zenith")


def build_face_down():
    yy, xx = np.mgrid[0:FACE, 0:FACE].astype(np.float32)
    rs = np.random.RandomState(99)
    noise = rs.uniform(-10, 10, size=(FACE, FACE)).astype(np.float32)
    base = SNOW[None, None, :] + noise[..., None]
    cx, cy = FACE / 2, FACE / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (FACE * 0.75)
    vign = 1.0 - 0.18 * np.clip(dist, 0, 1)
    base = base * vign[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    overlay = Image.new("RGBA", (FACE, FACE), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")
    r = random.Random(42)
    for _ in range(10):
        x = r.uniform(80, FACE - 80)
        y = r.uniform(80, FACE - 80)
        for dx, dy in ((0, 0), (28, 6)):
            d.ellipse([x + dx - 9, y + dy - 6, x + dx + 9, y + dy + 6], fill=rgba("silver", 70))
    for _ in range(40):
        x = r.uniform(0, FACE)
        y = r.uniform(0, FACE)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=rgba("sage_dark", 90))
    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(OUT / "panorama_5.png")
    print("panorama_5.png <- ground")


def main():
    build_faces_0_3()
    build_face_up()
    build_face_down()

    for i in range(6):
        with Image.open(OUT / f"panorama_{i}.png") as im:
            assert im.size == (1024, 1024) and im.mode == "RGB", f"panorama_{i}.png bad {im.size} {im.mode}"

    # contact-sheet preview: 6 faces in a strip, small
    prev = Image.new("RGB", (256 * 6, 256), rgb("night"))
    for i in range(6):
        with Image.open(OUT / f"panorama_{i}.png") as im:
            prev.paste(im.resize((256, 256), Image.LANCZOS), (i * 256, 0))
    prev.save(OUT / "_preview_strip.png")
    print("built panorama_0..5.png ->", OUT)


if __name__ == "__main__":
    main()
