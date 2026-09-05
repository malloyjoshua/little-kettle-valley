#!/usr/bin/env python3
"""snapshot_dress.py -- the two things a freshly built world-master needs before it ships.

`scratch/master_build.sh build` produces a correct world and a scruffy SNAPSHOT. Two
defects come out of the build itself rather than out of the plan, they were both found and
hand-fixed during the 2026-09-05 look pass (media/look/NOTES.md, "Fixed this pass" items 4
and 5), and a hand fix does not survive the next rebuild. So they are a script:

  1. LevelName. A world built by a server is called "world". The pack ships it as a save
     the player opens from the single-player list, where "world" is what an empty world is
     called.

  2. Litter and hostiles. A build is forty seconds of a live server running eighteen
     thousand commands: every `fill` that replaces a block a template had already put down
     drops it, and the region files end up carrying hundreds of `minecraft:item` entities
     that the player would walk into on her first morning. The look pass measured 73
     hostiles saved into the shipped snapshot as well -- 35 of them creepers, in a cozy
     pack, on the first load. Both are stripped here, off the region files, so it does not
     matter whether the chunk was loaded when the server stopped.

Passive animals, villagers, item frames, paintings, armour stands, minecarts and the
pack's own placed entities are all KEPT: they are the valley.

  tools/venv/bin/python tools/scripts/snapshot_dress.py --world world-master \
      --name "Little Kettle Valley"
"""
import argparse, collections, gzip, io, pathlib, struct, sys, zlib

sys.path.insert(0, 'tools/scripts')
import nbtlib  # noqa: E402

HOSTILE = set("""
zombie husk drowned zombie_villager zombified_piglin skeleton stray wither_skeleton
creeper spider cave_spider enderman endermite witch slime magma_cube blaze ghast
silverfish guardian elder_guardian shulker phantom pillager vindicator evoker ravager
vex hoglin zoglin piglin piglin_brute warden breeze bogged
""".split())
LITTER = {'minecraft:item', 'minecraft:experience_orb', 'minecraft:arrow',
          'minecraft:spectral_arrow', 'minecraft:eye_of_ender'}


def is_litter(eid):
    return eid in LITTER


def is_hostile(eid):
    ns, _, name = eid.partition(':')
    return ns == 'minecraft' and name in HOSTILE


def read_region(path):
    """-> {index: (timestamp, nbtlib.File)}, in the file's own slot order."""
    data = path.read_bytes()
    out = {}
    for i in range(1024):
        off = struct.unpack('>I', b'\x00' + data[i * 4:i * 4 + 3])[0]
        if off == 0:
            continue
        ts = struct.unpack('>I', data[4096 + i * 4:4096 + i * 4 + 4])[0]
        st = off * 4096
        ln = struct.unpack('>I', data[st:st + 4])[0]
        comp = data[st + 4]
        raw = data[st + 5:st + 4 + ln]
        if comp == 2:
            raw = zlib.decompress(raw)
        elif comp == 1:
            raw = gzip.decompress(raw)
        out[i] = (ts, nbtlib.File.parse(io.BytesIO(raw)))
    return out


def write_region(path, chunks):
    """Re-pack a whole region file: header, then every chunk from sector 2 onward."""
    loc = bytearray(4096)
    tsb = bytearray(4096)
    body = bytearray()
    sector = 2
    for i in sorted(chunks):
        ts, nbt = chunks[i]
        buf = io.BytesIO()
        nbt.write(buf, byteorder='big')
        blob = zlib.compress(buf.getvalue())
        payload = struct.pack('>IB', len(blob) + 1, 2) + blob
        pad = (-len(payload)) % 4096
        payload += b'\x00' * pad
        n = len(payload) // 4096
        if n > 255:
            raise SystemExit('chunk %d does not fit an .mca sector count' % i)
        loc[i * 4:i * 4 + 3] = struct.pack('>I', sector)[1:]
        loc[i * 4 + 3] = n
        tsb[i * 4:i * 4 + 4] = struct.pack('>I', ts)
        body += payload
        sector += n
    path.write_bytes(bytes(loc) + bytes(tsb) + bytes(body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', required=True)
    ap.add_argument('--name', default='Little Kettle Valley')
    ap.add_argument('--sites', default='pack/kubejs/data/valley/valley_sites.json')
    ap.add_argument('--radius', type=int, default=128,
                    help='hostiles are stripped only this far from spawn, the farm and '
                         'the anchor -- 128 covers the whole valley and reaches none of '
                         'the three pillager outposts, which are 200, 345 and 411 blocks '
                         'out and are part of the world. Litter is stripped everywhere.')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    W = pathlib.Path(args.world)

    # ---- 1. the name -------------------------------------------------------------
    lvl = W / 'level.dat'
    f = nbtlib.File.parse(io.BytesIO(gzip.decompress(lvl.read_bytes())))
    root = f[''] if '' in f else f
    was = str(root['Data']['LevelName'])
    if was != args.name:
        root['Data']['LevelName'] = nbtlib.String(args.name)
        if not args.dry_run:
            buf = io.BytesIO()
            f.write(buf, byteorder='big')
            lvl.write_bytes(gzip.compress(buf.getvalue()))
        print('  LevelName %r -> %r' % (was, args.name))
    else:
        print('  LevelName already %r' % args.name)

    # ---- 2. the litter and the hostiles -------------------------------------------
    import json
    site = json.load(open(args.sites))
    homes = [site['spawn'], site['anchor'], site['hearth']]

    def near(e):
        pos = [float(v) for v in e['Pos']]
        return any(max(abs(pos[0] - h[0]), abs(pos[2] - h[2])) <= args.radius for h in homes)

    killed = collections.Counter()
    kept = 0
    for mca in sorted((W / 'entities').glob('*.mca')):
        chunks = read_region(mca)
        touched = False
        for i, (ts, nbt) in chunks.items():
            croot = nbt[''] if '' in nbt else nbt
            ents = croot.get('Entities')
            if ents is None:
                continue
            keep = []
            for e in ents:
                eid = str(e['id'])
                if is_litter(eid) or (is_hostile(eid) and near(e)):
                    killed[eid] += 1
                    touched = True
                else:
                    keep.append(e)
                    kept += 1
            if len(keep) != len(ents):
                croot['Entities'] = nbtlib.List[nbtlib.Compound](keep)
        if touched and not args.dry_run:
            write_region(mca, chunks)
    if killed:
        print('  stripped %d entities across %d kinds, %d kept:'
              % (sum(killed.values()), len(killed), kept))
        for k, v in killed.most_common():
            print('    %-40s %d' % (k, v))
    else:
        print('  no litter and no hostiles in %d entities' % kept)


if __name__ == '__main__':
    main()
