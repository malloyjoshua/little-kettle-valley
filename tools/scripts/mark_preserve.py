#!/usr/bin/env python3
"""Mark every shipped world file in pack/index.toml as preserve = true.

Why this exists
---------------
`pack/saves/Little Kettle Valley/` is the shipped world: the valley Josh built,
committed into the pack so a friend opens the story instead of generating an
empty one.  packwiz treats it like any other file -- it downloads it on first
install, and on every launch after that it re-hashes it and rewrites anything
that no longer matches the index.

For a world that would be catastrophic.  The moment a player walks anywhere,
their region files stop matching ours, and the next launch would hand them our
copy back: the cottage un-built, the lamps unlit, every chest they filled gone.

packwiz's answer is the `preserve` flag -- the same one `options.txt` already
carries.  The shipped `packwiz-installer.jar` implements it in
`DownloadTask.download()`: when the metadata says preserve and the destination
file already exists, it returns before any hashing or writing.  Write-once-if-
missing.  A fresh install gets the valley; a player who has been living in it
keeps their own.

`packwiz refresh` re-hashes the file and rewrites its `[[files]]` block, but it
does not invent a `preserve` key -- so the flag has to be (re-)applied after a
refresh.  Running this script is idempotent and safe at any time; it only ever
adds the key, never removes one, and never touches a file outside `saves/`.

Usage
-----
    tools/venv/bin/python tools/scripts/mark_preserve.py            # apply
    tools/venv/bin/python tools/scripts/mark_preserve.py --check    # verify only

`--check` exits non-zero if any `saves/` entry is missing the flag, which makes
it usable as a release gate.

The index is edited as text, one `[[files]]` block at a time, rather than being
round-tripped through a TOML writer: packwiz writes the index in its own key
order and with its own quoting, and a Python rewrite would reformat all 380
blocks and produce a diff nobody can read (and a hash churn in pack.toml every
run).  A line insert keeps the diff to the lines that changed.

After running this, `pack.toml`'s recorded index hash is stale -- run
`tools/packwiz refresh` LAST, or rather: refresh first, mark second, and then
re-point pack.toml.  The wrapper `refresh_and_preserve()` below does exactly
that and is what `release.sh` calls.
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "pack"
INDEX = PACK / "index.toml"
PACK_TOML = PACK / "pack.toml"

# Every file under this prefix in the index is a shipped-world file.
PREFIX = "saves/"

FILE_RE = re.compile(r'^file\s*=\s*"(.*)"\s*$')


def parse_blocks(text):
    """Split index.toml into (header, [block, ...]).

    A block is the literal text of one `[[files]]` entry, newline-terminated,
    including the `[[files]]` line and the blank line that follows it.
    """
    lines = text.splitlines(keepends=True)
    header = []
    blocks = []
    cur = None
    for line in lines:
        if line.strip() == "[[files]]":
            if cur is not None:
                blocks.append(cur)
            cur = [line]
        elif cur is None:
            header.append(line)
        else:
            cur.append(line)
    if cur is not None:
        blocks.append(cur)
    return "".join(header), ["".join(b) for b in blocks]


def block_file(block):
    for line in block.splitlines():
        m = FILE_RE.match(line.strip())
        if m:
            return m.group(1)
    return None


def block_has_preserve(block):
    for line in block.splitlines():
        if line.strip().startswith("preserve"):
            return line.strip().endswith("true")
    return False


def add_preserve(block):
    """Insert `preserve = true` after the last non-blank key line of the block."""
    lines = block.splitlines(keepends=True)
    last = max(i for i, l in enumerate(lines) if l.strip())
    lines.insert(last + 1, "preserve = true\n")
    return "".join(lines)


def scan():
    text = INDEX.read_text()
    header, blocks = parse_blocks(text)
    world = [(i, b) for i, b in enumerate(blocks) if (block_file(b) or "").startswith(PREFIX)]
    return text, header, blocks, world


def do_check(verbose=True):
    _, _, _, world = scan()
    missing = [block_file(b) for _, b in world if not block_has_preserve(b)]
    if verbose:
        print(f"{len(world)} file(s) under {PREFIX!r} in {INDEX.relative_to(ROOT)}")
        print(f"{len(world) - len(missing)} marked preserve = true, {len(missing)} missing")
        for f in missing[:10]:
            print(f"  MISSING: {f}")
    return len(world), missing


def do_apply():
    text, header, blocks, world = scan()
    changed = 0
    for i, b in world:
        if not block_has_preserve(b):
            blocks[i] = add_preserve(b)
            changed += 1
    if changed:
        INDEX.write_text(header + "".join(blocks))
    total = len(world)
    print(f"{total} file(s) under {PREFIX!r}: {changed} newly marked, {total - changed} already marked")
    return changed


def repoint_pack_toml():
    """Rewrite pack.toml's [index] hash to match index.toml on disk.

    Editing index.toml invalidates the hash packwiz recorded, and a stale hash
    aborts a friend's install mid-launch.  packwiz itself only recomputes this
    during `refresh`, which would strip the flag we just added -- so we do the
    one-line update ourselves.
    """
    digest = hashlib.sha256(INDEX.read_bytes()).hexdigest()
    text = PACK_TOML.read_text()
    # Anchor on the line, not on trailing whitespace: `\s*$` in MULTILINE also matches the
    # newline and any blank line after it, which silently deleted the blank line between
    # [index] and [versions] on every run. Match only up to the closing quote.
    new, n = re.subn(r'^(hash[ \t]*=[ \t]*)"[0-9a-f]{64}"', rf'\g<1>"{digest}"', text, flags=re.MULTILINE)
    if n != 1:
        raise SystemExit(f"FATAL: expected exactly one index hash line in {PACK_TOML}, found {n}")
    if new != text:
        PACK_TOML.write_text(new)
        print(f"pack.toml index hash -> {digest}")
    else:
        print(f"pack.toml index hash already {digest}")
    return digest


def refresh_and_preserve():
    """`packwiz refresh`, then re-apply the flag, then re-point pack.toml.

    This is the whole invariant in one call, and the only correct order.
    """
    subprocess.run([str(ROOT / "tools" / "packwiz"), "refresh"], cwd=PACK, check=True,
                   stdout=subprocess.DEVNULL)
    do_apply()
    return repoint_pack_toml()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 if any saves/ entry lacks the flag")
    ap.add_argument("--refresh", action="store_true", help="run `packwiz refresh` first, then mark, then re-point pack.toml")
    args = ap.parse_args()

    if args.check:
        total, missing = do_check()
        if total == 0:
            print("FAIL: no saves/ files in the index at all -- was the world copied into pack/saves/?")
            return 1
        return 1 if missing else 0

    if args.refresh:
        refresh_and_preserve()
    else:
        do_apply()
        repoint_pack_toml()
    total, missing = do_check(verbose=False)
    print(f"verify: {total} saves/ entries, {len(missing)} missing the flag")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
