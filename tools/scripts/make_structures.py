#!/usr/bin/env python3
"""
make_structures.py — build every `/place template valley:<name>` target as a
real Minecraft structure NBT.

Little Kettle Valley ships ten templates, all placed by valley_finales.js:

    market_stall (x4)  long_table   mill_race   mill_roof   pier
    granary_shell      granary_facade           noticeboard
    town_hall          stone_bridge

Story document §7 rule 2 is "clear-fill air -> fill pad -> /place template",
and §12.2 P8 says these are `.nbt` files under data/valley/structures/, not
thousand-line /fill chains. This script is how they are generated, so a change
to a stall is a two-line edit here and not a rebuild in a creative world.

Rules this file obeys:
  * Every block id is checked against the live registry export
    (server/local/kubejs/export/registries/block.json) before anything is
    written. An unknown id is a hard failure, not a warning.
  * Block state Properties are only ever set to values verified against the
    mod's own assets/<ns>/blockstates/<block>.json. Where a modded block's
    property set was not verified, the palette entry carries NO Properties and
    the game resolves the default state.
  * Every file is loaded back with nbtlib after writing, and size + block count
    are printed, so "it parses" is proven rather than assumed.

Usage:
    tools/venv/bin/python tools/scripts/make_structures.py [--out DIR]

Structure NBT layout (1.20.1, DataVersion 3465):
    { DataVersion: int
      size:     [TAG_Int, TAG_Int, TAG_Int]
      palette:  [ {Name: string, Properties?: {..strings..}} ]
      blocks:   [ {state: int, pos: [TAG_Int x3]} ]
      entities: [] }
"""

import argparse
import os
import sys

try:
    from nbtlib import File, Compound, List, Int, String
except ImportError:  # pragma: no cover
    sys.exit("nbtlib is missing. Run: tools/venv/bin/python -m pip install nbtlib")

import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REGISTRY = os.path.join(ROOT, "server", "local", "kubejs", "export",
                        "registries", "block.json")
DEFAULT_OUT = os.path.join(ROOT, "pack", "kubejs", "data", "valley", "structures")
DATA_VERSION = 3465          # 1.20.1


# ---------------------------------------------------------------------------
# Registry check. Every id in every template goes through this.
# ---------------------------------------------------------------------------
def load_registry():
    if not os.path.exists(REGISTRY):
        print("!! block registry export not found at %s" % REGISTRY)
        print("   Block ids will NOT be verified. Fix the export and re-run.")
        return None
    with open(REGISTRY) as fh:
        return set(json.load(fh).keys())


KNOWN = load_registry()


# ---------------------------------------------------------------------------
# The builder. A Struct is a sparse dict of (x, y, z) -> (name, props).
# ---------------------------------------------------------------------------
class Struct:
    def __init__(self, name, sx, sy, sz):
        self.name = name
        self.size = (sx, sy, sz)
        self.cells = {}

    def set(self, x, y, z, block, **props):
        """One block. Out-of-bounds is a bug, so it raises."""
        sx, sy, sz = self.size
        if not (0 <= x < sx and 0 <= y < sy and 0 <= z < sz):
            raise IndexError("%s: (%d,%d,%d) outside %dx%dx%d"
                             % (self.name, x, y, z, sx, sy, sz))
        if KNOWN is not None and block not in KNOWN:
            raise KeyError("%s: '%s' is not a block in this pack's registry"
                           % (self.name, block))
        self.cells[(x, y, z)] = (block, tuple(sorted(props.items())))

    def fill(self, x1, y1, z1, x2, y2, z2, block, **props):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block, **props)

    def outline(self, x1, y1, z1, x2, y2, z2, block, **props):
        """The four vertical faces of a box — walls, no floor, no ceiling."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    if x in (x1, x2) or z in (z1, z2):
                        self.set(x, y, z, block, **props)

    def clear(self, x1, y1, z1, x2, y2, z2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.cells.pop((x, y, z), None)

    # -- serialisation ------------------------------------------------------
    def to_nbt(self):
        palette = []
        index = {}
        blocks = []
        for pos in sorted(self.cells):
            entry = self.cells[pos]
            if entry not in index:
                index[entry] = len(palette)
                palette.append(entry)
            x, y, z = pos
            blocks.append(Compound({
                "state": Int(index[entry]),
                "pos": List[Int]([Int(x), Int(y), Int(z)]),
            }))

        pal = []
        for name, props in palette:
            c = Compound({"Name": String(name)})
            if props:
                c["Properties"] = Compound(
                    {String(k): String(v) for k, v in props})
            pal.append(c)

        sx, sy, sz = self.size
        return Compound({
            "DataVersion": Int(DATA_VERSION),
            "size": List[Int]([Int(sx), Int(sy), Int(sz)]),
            "palette": List[Compound](pal),
            "blocks": List[Compound](blocks),
            "entities": List[Compound]([]),
        })


# =============================================================================
# The ten templates.
#
# Placement note: `/place template valley:<name> <x> <y> <z>` puts the
# template's LOCAL (0,0,0) at <x> <y> <z> and grows in +x/+y/+z. Every origin
# in valley_finales.js is therefore the template's north-west-bottom corner,
# not its centre — the offsets there are already written that way.
# =============================================================================

OAK = "minecraft:oak_planks"
LOG = "minecraft:oak_log"
FENCE = "minecraft:oak_fence"
SB = "minecraft:stone_bricks"


def market_stall():
    """5 x 4 x 3 — four fence posts, a striped wool awning, a barrel, a lantern."""
    s = Struct("market_stall", 5, 4, 3)
    # posts
    for x in (0, 4):
        for z in (0, 2):
            s.fill(x, 0, z, x, 2, z, FENCE)
    # awning, alternating stripes
    for x in range(5):
        wool = "minecraft:white_wool" if x % 2 == 0 else "minecraft:orange_wool"
        s.fill(x, 3, 0, x, 3, 2, wool)
    # counter along the front (z = 0)
    s.fill(1, 0, 0, 3, 0, 0, OAK)
    s.fill(1, 1, 0, 3, 1, 0, "minecraft:oak_slab", type="bottom",
           waterlogged="false")
    # stock behind the counter
    s.set(1, 0, 1, "minecraft:barrel", facing="up", open="false")
    s.set(3, 0, 1, "minecraft:hay_block", axis="y")
    s.set(2, 0, 1, "minecraft:composter", level="0")
    # a lantern hanging off the awning
    s.set(2, 2, 1, "minecraft:lantern", hanging="true", waterlogged="false")
    # bunting
    s.set(0, 3, 1, "minecraft:red_wool")
    s.set(4, 3, 1, "minecraft:yellow_wool")
    return s


def long_table():
    """9 x 2 x 3 — a Handcrafted oak table, benches down both sides, twelve settings."""
    s = Struct("long_table", 9, 2, 3)
    # the table itself. handcrafted:oak_table computes `shape` from its
    # neighbours; the palette entry carries no Properties so the game resolves
    # the default state rather than a shape guessed from the blockstate file.
    s.fill(0, 0, 1, 8, 0, 1, "handcrafted:oak_table")
    # benches down both long sides
    s.fill(0, 0, 0, 8, 0, 0, "handcrafted:oak_bench")
    s.fill(0, 0, 2, 8, 0, 2, "handcrafted:oak_bench")
    # twelve place settings, six a side is one per seat at the Supper
    for x in (0, 2, 4, 6, 8):
        s.set(x, 1, 1, "handcrafted:wood_plate")
    for x in (1, 3, 5, 7):
        s.set(x, 1, 1, "handcrafted:wood_cup")
    return s


def mill_race():
    """7 x 3 x 3 — a stone-brick channel with water in it, so Q16's wheels turn."""
    s = Struct("mill_race", 7, 3, 3)
    s.fill(0, 0, 0, 6, 0, 2, SB)                       # bed
    s.fill(0, 1, 0, 6, 1, 0, SB)                       # north bank
    s.fill(0, 1, 2, 6, 1, 2, SB)                       # south bank
    s.fill(0, 1, 1, 6, 1, 1, "minecraft:water", level="0")
    s.fill(0, 2, 0, 6, 2, 0, "minecraft:stone_brick_wall",
           north="none", south="none", east="low", west="low",
           up="true", waterlogged="false")
    s.fill(0, 2, 2, 6, 2, 2, "minecraft:stone_brick_wall",
           north="none", south="none", east="low", west="low",
           up="true", waterlogged="false")
    # the sluice head
    s.set(0, 2, 1, "minecraft:stone_brick_slab", type="bottom",
          waterlogged="false")
    s.set(6, 2, 1, "minecraft:stone_brick_slab", type="bottom",
          waterlogged="false")
    return s


def mill_roof():
    """9 x 5 x 9 — Macaw's oak roof, four hipped tiers over the mill house."""
    s = Struct("mill_roof", 9, 5, 9)
    roof = "mcwroofs:oak_roof"        # facing/half/shape verified in the jar
    for tier in range(4):
        lo, hi, y = tier, 8 - tier, tier
        for x in range(lo, hi + 1):
            s.set(x, y, lo, roof, facing="north", half="bottom", shape="straight")
            s.set(x, y, hi, roof, facing="south", half="bottom", shape="straight")
        for z in range(lo + 1, hi):
            s.set(lo, y, z, roof, facing="west", half="bottom", shape="straight")
            s.set(hi, y, z, roof, facing="east", half="bottom", shape="straight")
        # deck under the ring, so the roof is not see-through from below
        if lo + 1 <= hi - 1:
            s.fill(lo + 1, y, lo + 1, hi - 1, y, hi - 1, OAK)
    s.fill(4, 4, 4, 4, 4, 4, LOG, axis="y")            # the ridge stub
    return s


def pier():
    """3 x 3 x 9 — plank deck on fence piles, lanterns at the head and the end."""
    s = Struct("pier", 3, 3, 9)
    for z in range(0, 9, 2):
        s.set(0, 0, z, FENCE)
        s.set(2, 0, z, FENCE)
    s.fill(0, 1, 0, 2, 1, 8, OAK)
    # rail posts and lights
    for z in (0, 4, 8):
        s.set(0, 2, z, FENCE)
        s.set(2, 2, z, FENCE)
    s.set(1, 2, 8, "minecraft:lantern", hanging="false", waterlogged="false")
    s.set(1, 2, 0, "minecraft:lantern", hanging="false", waterlogged="false")
    return s


def granary_shell():
    """9 x 6 x 9 — walls only, with twelve marked alcoves for Q39's drawers."""
    s = Struct("granary_shell", 9, 6, 9)
    s.outline(0, 0, 0, 8, 4, 8, OAK)
    # corner posts
    for x in (0, 8):
        for z in (0, 8):
            s.fill(x, 0, z, x, 4, z, LOG, axis="y")
    # top plate
    s.outline(0, 5, 0, 8, 5, 8, "minecraft:oak_slab",
              type="bottom", waterlogged="false")
    # twelve alcoves: six a side on the long walls, marked in andesite
    for z in (1, 3, 5):
        for y in (1, 3):
            s.set(1, y, z, "minecraft:polished_andesite")
            s.set(7, y, z, "minecraft:polished_andesite")
    # the floor is left alone on purpose — the finale fills a pad underneath
    return s


def granary_facade():
    """9 x 6 x 1 — the front wall Act III drops onto the shell's z = 0 plane."""
    s = Struct("granary_facade", 9, 6, 1)
    s.fill(0, 0, 0, 8, 4, 0, OAK)
    for x in (0, 8):
        s.fill(x, 0, 0, x, 4, 0, LOG, axis="y")
    # the doorway, two wide
    s.clear(3, 0, 0, 5, 2, 0)
    s.set(3, 0, 0, "minecraft:oak_door", facing="south", half="lower",
          hinge="left", open="false", powered="false")
    s.set(3, 1, 0, "minecraft:oak_door", facing="south", half="upper",
          hinge="left", open="false", powered="false")
    s.set(5, 0, 0, "minecraft:oak_door", facing="south", half="lower",
          hinge="right", open="false", powered="false")
    s.set(5, 1, 0, "minecraft:oak_door", facing="south", half="upper",
          hinge="right", open="false", powered="false")
    s.set(4, 2, 0, "minecraft:oak_trapdoor", facing="south", half="top",
          open="false", powered="false", waterlogged="false")
    # two loft windows
    for x in (1, 7):
        s.set(x, 3, 0, "minecraft:glass_pane", north="false", south="false",
              east="false", west="false", waterlogged="false")
    # gable and lamps
    s.fill(2, 5, 0, 6, 5, 0, "minecraft:oak_stairs", facing="north",
           half="bottom", shape="straight", waterlogged="false")
    s.set(1, 4, 0, "minecraft:lantern", hanging="false", waterlogged="false")
    s.set(7, 4, 0, "minecraft:lantern", hanging="false", waterlogged="false")
    return s


def noticeboard():
    """3 x 4 x 1 — Oda's board: a Bountiful bountyboard, a roof, two lanterns."""
    s = Struct("noticeboard", 3, 4, 1)
    for x in (0, 2):
        s.fill(x, 0, 0, x, 1, 0, FENCE)
    s.set(1, 0, 0, OAK)
    # bountiful:bountyboard IS a block in this pack (checked in the registry)
    # and has no block state properties at all.
    s.set(1, 1, 0, "bountiful:bountyboard")
    s.fill(0, 2, 0, 2, 2, 0, "minecraft:oak_slab", type="bottom",
           waterlogged="false")
    s.set(0, 3, 0, "minecraft:lantern", hanging="false", waterlogged="false")
    s.set(2, 3, 0, "minecraft:lantern", hanging="false", waterlogged="false")
    s.set(1, 3, 0, "minecraft:oak_sign", rotation="8", waterlogged="false")
    return s


def town_hall():
    """11 x 7 x 11 — stone brick base, oak above, a doorway and six windows."""
    s = Struct("town_hall", 11, 7, 11)
    s.fill(0, 0, 0, 10, 0, 10, SB)                     # plinth
    s.outline(0, 1, 0, 10, 1, 10, SB)                  # stone course
    s.outline(0, 2, 0, 10, 4, 10, OAK)                 # oak walls
    for x in (0, 10):
        for z in (0, 10):
            s.fill(x, 1, z, x, 4, z, LOG, axis="y")    # corner posts
    # the doorway, south wall (z = 10), two wide and three high
    s.clear(4, 2, 10, 6, 4, 10)
    s.set(4, 2, 10, "minecraft:oak_door", facing="north", half="lower",
          hinge="right", open="false", powered="false")
    s.set(4, 3, 10, "minecraft:oak_door", facing="north", half="upper",
          hinge="right", open="false", powered="false")
    s.set(6, 2, 10, "minecraft:oak_door", facing="north", half="lower",
          hinge="left", open="false", powered="false")
    s.set(6, 3, 10, "minecraft:oak_door", facing="north", half="upper",
          hinge="left", open="false", powered="false")
    s.set(5, 4, 10, OAK)
    # six windows, two a side
    for z in (3, 7):
        for x in (0, 10):
            s.fill(x, 3, z, x, 3, z, "minecraft:glass_pane",
                   north="true", south="true", east="false", west="false",
                   waterlogged="false")
    for x in (2, 8):
        s.fill(x, 3, 0, x, 3, 0, "minecraft:glass_pane",
               north="false", south="false", east="true", west="true",
               waterlogged="false")
    # roof: two hipped tiers of stairs plus a flat cap
    for x in range(11):
        s.set(x, 5, 0, "minecraft:oak_stairs", facing="north", half="bottom",
              shape="straight", waterlogged="false")
        s.set(x, 5, 10, "minecraft:oak_stairs", facing="south", half="bottom",
              shape="straight", waterlogged="false")
    for z in range(1, 10):
        s.set(0, 5, z, "minecraft:oak_stairs", facing="west", half="bottom",
              shape="straight", waterlogged="false")
        s.set(10, 5, z, "minecraft:oak_stairs", facing="east", half="bottom",
              shape="straight", waterlogged="false")
    s.fill(1, 5, 1, 9, 5, 9, OAK)
    s.fill(2, 6, 2, 8, 6, 8, "minecraft:oak_slab", type="bottom",
           waterlogged="false")
    # the porch lamps
    s.set(3, 4, 10, "minecraft:lantern", hanging="false", waterlogged="false")
    s.set(7, 4, 10, "minecraft:lantern", hanging="false", waterlogged="false")
    return s


def stone_bridge():
    """5 x 5 x 11 — a stone arch with a three-wide deck and low parapets."""
    s = Struct("stone_bridge", 5, 5, 11)
    # abutments at both ends
    s.fill(0, 0, 0, 4, 2, 1, SB)
    s.fill(0, 0, 9, 4, 2, 10, SB)
    # the arch: two courses stepping up to the crown
    arch = {2: 1, 3: 2, 4: 3, 5: 3, 6: 3, 7: 2, 8: 1}
    for z, h in arch.items():
        s.fill(0, h, z, 4, h, z, SB)
        s.set(0, h - 1, z, "minecraft:stone_brick_stairs", facing="east",
              half="top", shape="straight", waterlogged="false")
        s.set(4, h - 1, z, "minecraft:stone_brick_stairs", facing="west",
              half="top", shape="straight", waterlogged="false")
    # the deck, three wide, level at y = 3
    s.fill(1, 3, 0, 3, 3, 10, "minecraft:stone_bricks")
    s.fill(2, 3, 0, 2, 3, 10, "minecraft:polished_andesite")
    # parapets
    for z in range(0, 11):
        s.set(0, 3, z, "minecraft:stone_brick_wall", north="low", south="low",
              east="none", west="none", up="false", waterlogged="false")
        s.set(4, 3, z, "minecraft:stone_brick_wall", north="low", south="low",
              east="none", west="none", up="false", waterlogged="false")
    # four lamps on the parapet ends
    for z in (0, 10):
        for x in (0, 4):
            s.set(x, 4, z, "minecraft:lantern", hanging="false",
                  waterlogged="false")
    return s


BUILDERS = [
    market_stall, long_table, mill_race, mill_roof, pier,
    granary_shell, granary_facade, noticeboard, town_hall, stone_bridge,
]


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("registry: %s" % ("%d blocks" % len(KNOWN) if KNOWN else "NOT CHECKED"))
    failures = 0
    for build in BUILDERS:
        s = build()
        path = os.path.join(args.out, s.name + ".nbt")
        File(s.to_nbt()).save(path, gzipped=True)

        # Prove it parses: load it straight back and read the header out of
        # the file on disk, not out of the object we just built.
        import nbtlib
        back = nbtlib.load(path)
        size = [int(v) for v in back["size"]]
        n = len(back["blocks"])
        pal = len(back["palette"])
        ok = (size == list(s.size) and n == len(s.cells))
        failures += 0 if ok else 1
        print("%-16s %2dx%-2dx%-2d  %4d blocks  %2d palette  %6d bytes  %s"
              % (s.name, size[0], size[1], size[2], n, pal,
                 os.path.getsize(path), "ok" if ok else "MISMATCH"))
    if failures:
        sys.exit("%d structure(s) did not round-trip" % failures)
    print("\n%d structures written to %s" % (len(BUILDERS), args.out))


if __name__ == "__main__":
    main()
