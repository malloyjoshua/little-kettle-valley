#!/usr/bin/env python3
"""Branded 6x9 install guide PDF for Little Kettle Valley. Usage: install_guide_pdf.py <out.pdf>"""
import sys, pathlib, json
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT = pathlib.Path(__file__).resolve().parents[2]
PAL = json.loads((ROOT / 'media' / 'palette.json').read_text())['colors']
W, H = 6 * inch, 9 * inch; M = 0.55 * inch
out = pathlib.Path(sys.argv[1])
for name, path in [('Rounded', '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf'), ('Body', '/System/Library/Fonts/Supplemental/Arial.ttf'), ('BodyBold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, path))
c = canvas.Canvas(str(out), pagesize=(W, H)); c.setTitle('Little Kettle Valley: install guide')
CREAM, INK, COPPER, SAGE, LAMP, NIGHT = [HexColor(PAL[k]) for k in ('cream', 'ink', 'copper', 'sage', 'lamp', 'night')]
def page_bg():
    c.setFillColor(CREAM); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(SAGE); c.rect(0, H - 0.22 * inch, W, 0.22 * inch, fill=1, stroke=0)
def text(x, y, s, font='Body', size=10.5, color=INK, leading=None):
    c.setFont(font, size); c.setFillColor(color); c.drawString(x, y, s)
def wrap(x, y, s, width, font='Body', size=10.5, color=INK, leading=16):
    from reportlab.lib.utils import simpleSplit
    for line in simpleSplit(s, font, size, width): text(x, y, line, font, size, color); y -= leading
    return y
def footer(n):
    text(M, 0.35 * inch, 'Little Kettle Valley  ·  put the kettle on', 'Body', 8, COPPER); text(W - M - 0.2 * inch, 0.35 * inch, str(n), 'Body', 8, COPPER)
def numbered_steps(steps, x, y, dot_r=0.16, num_size=12, h1_size=13, body_size=10.5, gap=0.14):
    """Copper numbered-circle steps, same idiom as the original cover page. dot_r/gap are inches. Returns new y."""
    r = dot_r * inch; hx = x + r * 2 + 0.13 * inch
    for i, (h1, body) in enumerate(steps, 1):
        c.setFillColor(COPPER); c.circle(x + r, y - 0.02 * inch, r, fill=1, stroke=0)
        text(x + r * 0.6, y - 0.07 * inch, str(i), 'Rounded', num_size, CREAM)
        text(hx, y, h1, 'Rounded', h1_size, INK); y -= 0.24 * inch
        y = wrap(hx, y, body, W - M - hx, 'Body', body_size, INK, 15) - gap * inch
    return y
def note_box(x, y, w, title, body, title_color=COPPER, box_color=None):
    """A rounded callout box; returns the new y below it."""
    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(body, 'Body', 10, w - 0.4 * inch)
    box_h = 0.3 * inch + 0.2 * inch + len(lines) * 14 + 0.14 * inch
    by = y - box_h
    c.setFillColor(box_color or HexColor(PAL['paper'])); c.roundRect(x, by, w, box_h, 8, fill=1, stroke=0)
    ty = by + box_h - 0.28 * inch
    text(x + 0.2 * inch, ty, title, 'Rounded', 11.5, title_color); ty -= 0.2 * inch
    for line in lines: text(x + 0.2 * inch, ty, line, 'Body', 10, INK); ty -= 14
    return by - 0.16 * inch
# ---------- page 1: cover + Windows
page_bg()
logo = ROOT / 'media' / 'logo' / 'wordmark_2048.png'; mark = ROOT / 'media' / 'icon' / 'mark_512.png'
y = H - M - 0.1 * inch
if logo.exists():
    im = ImageReader(str(logo)); iw, ih = im.getSize(); w = W - 2 * M; h = w * ih / iw; c.drawImage(im, M, y - h, w, h, mask='auto'); y -= h + 0.15 * inch
else:
    text(M, y - 0.4 * inch, 'Little Kettle Valley', 'Rounded', 26, COPPER); y -= 0.6 * inch
text(M, y, 'Install guide for friends. Pick the path for your computer.', 'Body', 10.5, INK); y -= 0.4 * inch
text(M, y, 'Windows', 'Rounded', 15, COPPER); y -= 0.32 * inch
win_steps = [
    ('Download the installer', 'Get LittleKettleValley-Setup.exe from the GitHub release page. Your browser may flag it as uncommonly downloaded — choose Keep.'),
    ('Click through SmartScreen', '"Windows protected your PC" > More info > Run anyway. One-time, because the installer is not code-signed.'),
    ('Install', 'Next > Install. No admin password, nothing else to install — Java is bundled.'),
    ('Sign in', 'Leave "Launch Little Kettle Valley" ticked. Sign in with the Microsoft account that owns Minecraft.'),
    ('Launch', 'Little Kettle Valley > Play. First launch downloads about 125 mods and the valley itself, and takes a few minutes. Then it opens straight into the world — you never make one.'),
]
y = numbered_steps(win_steps, M, y)
y -= 0.05 * inch
y = note_box(M, y, W - 2 * M, 'Why the SmartScreen warning', 'A code-signing certificate costs money and only builds trust over time — the pack itself is free, so there is no cert. The warning is harmless; "Run anyway" is the whole workaround.')
footer(1); c.showPage()
# ---------- page 2: Mac + Manual + join server
page_bg(); y = H - M - 0.1 * inch
if mark.exists():
    im = ImageReader(str(mark)); c.drawImage(im, W - M - 0.34 * inch, y - 0.28 * inch, 0.34 * inch, 0.34 * inch, mask='auto')
text(M, y, 'Mac', 'Rounded', 15, COPPER); y -= 0.32 * inch
mac_steps = [
    ('Drag into Applications', 'Open the .dmg. Drag Prism Launcher onto the Applications shortcut. Leave the window open for step 3.'),
    ('Open Prism, sign in', 'It fetches its own Java automatically — let it, that is normal. Sign in with the Microsoft account that owns Minecraft.'),
    ('Drag the kettle zip onto Prism', 'Or Add Instance > Import. First launch installs the pack — about 125 mods, a few minutes.'),
]
y = numbered_steps(mac_steps, M, y, dot_r=0.15, num_size=11, h1_size=12.5, body_size=10)
y -= 0.03 * inch
y = note_box(M, y, W - 2 * M, 'Gatekeeper, once', 'First open shows a one-time "downloaded from the Internet" confirmation — click Open. That is it: the app is notarized, so you will not see "cannot be opened" and will not need System Settings.')
y -= 0.18 * inch
text(M, y, 'Manual (any launcher)', 'Rounded', 13, INK); y -= 0.24 * inch
y = wrap(M, y, 'Already run a different launcher, or the installers above do not fit? Prism Launcher works the same way everywhere:', W - 2 * M, 'Body', 10, INK, 14) - 0.08 * inch
manual_steps = [
    'Install Prism Launcher (free): prismlauncher.org/download',
    'Sign in with your Microsoft account (Accounts, top right).',
    'Download LittleKettleValley.zip from the release page. Do not unzip it.',
    'Add Instance > Import > pick the zip > OK.',
    'Edit > Settings > Memory: 3072 MB on 8 GB, 3584 on 16 GB, 4096 on 32 GB.',
]
for i, t in enumerate(manual_steps, 1):
    y = wrap(M + 0.22 * inch, y, f'{i}. {t}', W - 2 * M - 0.22 * inch, 'Body', 9.5, INK, 13) - 0.04 * inch
y -= 0.1 * inch
BOX_H = 1.05 * inch; by = y - BOX_H
c.setFillColor(HexColor(PAL['paper'])); c.roundRect(M, by, W - 2 * M, BOX_H, 8, fill=1, stroke=0)
ty = by + BOX_H - 0.3 * inch
text(M + 0.2 * inch, ty, 'Join the server', 'Rounded', 12, COPPER); ty -= 0.22 * inch
wrap(M + 0.2 * inch, ty, 'Multiplayer > Add Server > paste the address Josh sends you. Your name has to be on the whitelist, so tell Josh your exact Minecraft username first.', W - 2 * M - 0.4 * inch, 'Body', 10, INK, 14)
footer(2); c.showPage()
# ---------- page 3: what it is + if it won't start
page_bg(); y = H - M - 0.1 * inch
text(M, y - 0.25 * inch, 'What you are walking into', 'Rounded', 16, COPPER); y -= 0.55 * inch
y = wrap(M, y, 'You inherit a cold house in a quiet valley. A letter, a copper kettle, and forty dark lamp posts. The quest book (press J) always tells you the one next thing to do. Follow it and the town wakes up one neighbour at a time. Forty lamps. Fifteen people. One winter that nobody leaves.', W - 2 * M, 'Body', 10.5, INK, 16) - 0.2 * inch
y = wrap(M, y, 'Two lanes share one world: the cozy lane cooks, farms, fishes, keeps animals and decorates; the tech lane builds machines, a power grid, a storage network, and eventually a reactor. Neither can finish alone. Pick whichever you like, or both.', W - 2 * M, 'Body', 10.5, INK, 16) - 0.3 * inch
text(M, y, 'Good to know', 'Rounded', 13, INK); y -= 0.26 * inch
tips = ['Press J for the quest book. The pinned quest on screen is always the next step.', 'Everyone on the Cozy team shares quest progress. You join it automatically on first login.', 'Vein mining: hold the grave key (`) while you mine an ore and the whole vein comes out.', 'Dying leaves your stuff in a grave only you can open. Nothing is lost.', 'The bounty board at Oda\'s store pays Valley Scrip. Scrip buys tech parts and decor at her counter.']
for t in tips:
    c.setFillColor(SAGE); c.circle(M + 0.06 * inch, y + 0.04 * inch, 0.045 * inch, fill=1, stroke=0)
    y = wrap(M + 0.22 * inch, y, t, W - 2 * M - 0.22 * inch, 'Body', 10, INK, 14) - 0.06 * inch
y -= 0.2 * inch; text(M, y, 'If it will not start', 'Rounded', 13, INK); y -= 0.26 * inch
fixes = ['Memory below 3072 MB is the usual cause. Raise it in Edit > Settings.', 'Shaders: the pack ships without them on purpose. Options > Video > Shader Packs > None.', 'Still stuck: right-click the instance > Minecraft Folder > logs > latest.log, and send that file to Josh.']
for t in fixes:
    c.setFillColor(COPPER); c.circle(M + 0.06 * inch, y + 0.04 * inch, 0.045 * inch, fill=1, stroke=0)
    y = wrap(M + 0.22 * inch, y, t, W - 2 * M - 0.22 * inch, 'Body', 10, INK, 14) - 0.06 * inch
footer(3); c.save(); print('wrote', out)
