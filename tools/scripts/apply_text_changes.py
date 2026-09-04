#!/usr/bin/env python3
"""apply_text_changes.py - apply a writing-audit change list to the pack's SOURCE text.

Reads docs/audit/changes-final.json (a list of {id, kind, file, locator, old, new})
and replaces `old` with `new` at the place the locator names, and ONLY when `old`
matches what is there today, byte for byte. Nothing is guessed: a change whose
`old` cannot be found, or can be found in more than one place, is reported as a
MISS and the file is left alone.

Three locator families:

  1. Structured JSON  - story/quests/*.json, story/npcs.json, and the Patchouli /
     advancement JSON under pack/. The locator is a path
     ("quests[q01].rewards[9].toast.title"). The file is parsed with a
     position-tracking JSON reader, the target string is verified against `old`,
     and the raw bytes of that one string are spliced. Every other byte of the
     file - indent width, key order, escaping style - is untouched.

     A `rewards[N].command` locator points at a Minecraft command, and `old` is
     the FLATTENED player-facing text inside it ("Marnie: some line"), not the
     command. Single-component commands get their one text replaced; two-component
     tellraws ("Marnie: " + body) get only the body component replaced, so colour
     and italic keys survive.

  2. Text files - the hand-written .js and .mcfunction, where the locator is prose
     ("line 958 ... v.say(player,'Marnie',...)"). The string is found by content,
     not by line: `old` is searched for under a small set of source encodings
     (raw, single-quote-escaped, double-quote-escaped, doubly-escaped) and in a
     view of the file where adjacent JS string literals joined by `+` have been
     spliced together, so a sentence broken across three source lines still
     matches. The match must be unique. The replacement is escaped for whichever
     quote character actually opens the literal it lands in.

  3. Generated files - town_plan.js and the act1/setup .mcfunctions are output of
     tools/scripts/plan_town.py; valley_greetings.js and the easy_npc presets are
     output of make_npc_presets.py. Edits aimed at those are redirected to the
     source that generates them (see REDIRECT), so re-running the generator keeps
     the change instead of reverting it.

Usage:
    tools/venv/bin/python tools/scripts/apply_text_changes.py [--dry-run] [changes.json]
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.chdir(ROOT)

# Files that are generated: an edit aimed at them is applied to their source.
REDIRECT = {
    'pack/kubejs/server_scripts/town_plan.js': 'tools/scripts/plan_town.py',
    'pack/kubejs/data/valley/functions/act1/cottage.mcfunction': 'tools/scripts/plan_town.py',
    'pack/kubejs/data/valley/functions/act1/square_path.mcfunction': 'tools/scripts/plan_town.py',
    'pack/kubejs/data/valley/functions/setup/place_ruin.mcfunction': 'tools/scripts/plan_town.py',
    'pack/kubejs/server_scripts/valley_greetings.js': 'story/npcs.json',
}

STRUCTURED = ('.json',)

# story/npcs.json stores each resident's headline line twice: once as `greeting`
# (what Easy NPC shows) and once as `greetings[0]` (head of the pool valley_greetings
# reads). make_npc_presets.py refuses to build unless the two agree, so a change to
# the head of a pool is mirrored onto the headline field. Same string, same
# decision, second copy - not a second edit.
MIRROR = {
    'greetings[0]': 'greeting',
    'greetings_after[0]': 'greeting_after',
}


def mirrored(change):
    """The twin of an npcs.json pool-head change, or None."""
    if change['file'] != 'story/npcs.json':
        return None
    for pool, headline in MIRROR.items():
        if change['locator'].endswith('.' + pool):
            twin = dict(change)
            twin['locator'] = change['locator'][:-len(pool)] + headline
            twin['id'] = change['id'] + '+mirror'
            return twin
    return None


# =============================================================================
# 1. A JSON reader that remembers where every string lives in the raw text
# =============================================================================
class Span(str):
    """A decoded JSON string that also knows its [start, end) in the raw text."""
    start = -1
    end = -1

    @classmethod
    def make(cls, value, start, end):
        s = cls(value)
        s.start = start
        s.end = end
        return s


_WS = ' \t\n\r'
_ESCAPES = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f',
            'n': '\n', 'r': '\r', 't': '\t'}


class PosJSON:
    """Minimal JSON parser. Values are ordinary Python objects except strings,
    which come back as Span so a caller can splice the original bytes."""

    def __init__(self, text):
        self.t = text
        self.i = 0

    def parse(self):
        v = self.value()
        self.ws()
        return v

    def ws(self):
        while self.i < len(self.t) and self.t[self.i] in _WS:
            self.i += 1

    def value(self):
        self.ws()
        c = self.t[self.i]
        if c == '{':
            return self.obj()
        if c == '[':
            return self.arr()
        if c == '"':
            return self.string()
        if self.t.startswith('true', self.i):
            self.i += 4
            return True
        if self.t.startswith('false', self.i):
            self.i += 5
            return False
        if self.t.startswith('null', self.i):
            self.i += 4
            return None
        m = re.compile(r'-?\d+(\.\d+)?([eE][-+]?\d+)?').match(self.t, self.i)
        if not m:
            raise ValueError('bad JSON at offset %d' % self.i)
        self.i = m.end()
        raw = m.group(0)
        return float(raw) if ('.' in raw or 'e' in raw or 'E' in raw) else int(raw)

    def obj(self):
        out = {}
        self.i += 1
        self.ws()
        if self.t[self.i] == '}':
            self.i += 1
            return out
        while True:
            self.ws()
            k = str(self.string())
            self.ws()
            assert self.t[self.i] == ':', self.i
            self.i += 1
            out[k] = self.value()
            self.ws()
            c = self.t[self.i]
            self.i += 1
            if c == '}':
                return out
            assert c == ',', self.i

    def arr(self):
        out = []
        self.i += 1
        self.ws()
        if self.t[self.i] == ']':
            self.i += 1
            return out
        while True:
            out.append(self.value())
            self.ws()
            c = self.t[self.i]
            self.i += 1
            if c == ']':
                return out
            assert c == ',', self.i

    def string(self):
        start = self.i
        assert self.t[self.i] == '"'
        self.i += 1
        buf = []
        while True:
            c = self.t[self.i]
            if c == '"':
                self.i += 1
                return Span.make(''.join(buf), start, self.i)
            if c == '\\':
                e = self.t[self.i + 1]
                if e == 'u':
                    buf.append(chr(int(self.t[self.i + 2:self.i + 6], 16)))
                    self.i += 6
                else:
                    buf.append(_ESCAPES[e])
                    self.i += 2
                continue
            buf.append(c)
            self.i += 1


def json_escape_body(s, ascii_only):
    """The inside of a JSON string literal, without the surrounding quotes."""
    return json.dumps(s, ensure_ascii=ascii_only)[1:-1]


# =============================================================================
# 2. Locator paths
# =============================================================================
def parse_path(loc):
    """'quests[q01].rewards[9].toast.title' -> [('key','quests'),('sel','q01'),...]"""
    out = []
    i = 0
    while i < len(loc):
        if loc[i] == '.':
            i += 1
            continue
        m = re.compile(r'[A-Za-z_][A-Za-z0-9_]*').match(loc, i)
        if m:
            out.append(('key', m.group(0)))
            i = m.end()
            continue
        m = re.compile(r'\[([^\]]*)\]').match(loc, i)
        if m:
            token = m.group(1)
            out.append(('idx', int(token)) if re.fullmatch(r'-?\d+', token)
                       else ('sel', token))
            i = m.end()
            continue
        raise ValueError('cannot parse locator %r at %d' % (loc, i))
    return out


def step(cur, kind, val, first):
    if kind == 'key':
        if isinstance(cur, dict) and val in cur:
            return cur[val]
        # "rewards[9].toast.title": the reward IS the toast, it is not nested
        # inside one - the segment names the reward's type.
        if isinstance(cur, dict) and cur.get('type') == val:
            return cur
        # "entry.pages[0].text" / "category.name": the first segment names the
        # document, not a key inside it.
        if first:
            return cur
        raise KeyError(val)
    if kind == 'idx':
        return cur[val]
    # 'sel': a key= lookup, either into a keyed list or onto a keyed object
    if isinstance(cur, list):
        for item in cur:
            if isinstance(item, dict) and item.get('key') == val:
                return item
        raise KeyError(val)
    if isinstance(cur, dict):
        if cur.get('key') == val:
            return cur
        if val in cur:
            return cur[val]
    raise KeyError(val)


def navigate(root, path):
    cur = root
    for n, (kind, val) in enumerate(path):
        cur = step(cur, kind, val, n == 0)
    return cur


# =============================================================================
# 3. Commands: the flattened "Speaker: body" inside a title/tellraw payload
# =============================================================================
def command_span(cmd_span, old, new, ascii_only):
    """Return (start, end, replacement_text) inside the raw file for a command
    whose rendered text is `old`. Offsets are absolute (cmd_span carries its
    own start). Returns None when `old` is not what the command says."""
    body_start = cmd_span.start + 1          # skip the opening quote
    raw = json_escape_body(str(cmd_span), ascii_only)
    # The command's own text is JSON inside the command string, so the value we
    # are looking for is escaped once more than the surrounding file string.
    def hunt(text_value, replacement):
        needle = json_escape_body(json_escape_body(text_value, ascii_only), ascii_only)
        repl = json_escape_body(json_escape_body(replacement, ascii_only), ascii_only)
        if raw.count(needle) != 1:
            return None
        i = raw.index(needle)
        return (body_start + i, body_start + i + len(needle), repl)

    hit = hunt(old, new)
    if hit:
        return hit
    # Two-component tellraw: component 0 is "Speaker: ", component 1 the body.
    if ': ' in old:
        cut = old.index(': ') + 2
        prefix, body = old[:cut], old[cut:]
        if new.startswith(prefix):
            return hunt(body, new[cut:])
    return None


# =============================================================================
# 4. Structured JSON changes
# =============================================================================
def apply_structured(text, ascii_only, change):
    """Return (start, end, replacement) or a string explaining the miss."""
    root = PosJSON(text).parse()
    path = parse_path(change['locator'])
    try:
        target = navigate(root, path)
    except (KeyError, IndexError, TypeError) as err:
        return 'locator did not resolve (%s)' % err

    if path[-1] == ('key', 'command'):
        if not isinstance(target, Span):
            return 'command is not a string'
        hit = command_span(target, change['old'], change['new'], ascii_only)
        if hit is None:
            return 'old text not found (once) inside the command'
        return hit

    if not isinstance(target, Span):
        return 'locator resolved to %s, not a string' % type(target).__name__
    if str(target) != change['old']:
        return 'old mismatch: file has %r' % str(target)[:120]
    return (target.start, target.end,
            '"' + json_escape_body(change['new'], ascii_only) + '"')


# =============================================================================
# 5. Text files (.js, .py, .mcfunction)
# =============================================================================
CONCAT = re.compile(r"(['\"])[ \t\r\n]*\+[ \t\r\n]*\1")


def concat_view(text):
    """A view of the file with `'a' + 'b'` splices removed, plus an index map
    back to the original offsets, so a sentence broken across source lines is
    still one searchable run."""
    chars, index = [], []
    i = 0
    while i < len(text):
        m = CONCAT.match(text, i)
        if m:
            i = m.end()
            continue
        chars.append(text[i])
        index.append(i)
        i += 1
    return ''.join(chars), index


def _esc(s, quote):
    out = s.replace('\\', '\\\\').replace('\n', '\\n')
    return out.replace(quote, '\\' + quote)


TRANSFORMS = [
    ('raw', lambda s: s),
    ('sq', lambda s: _esc(s, "'")),
    ('dq', lambda s: _esc(s, '"')),
    ('dq2', lambda s: s.replace('\\', '\\\\\\\\').replace('\n', '\\\\n').replace('"', '\\\\"')),
]


def open_quote_at(text, pos):
    """Which quote character opens the string literal that `pos` sits in.
    Scanned from the start of that line, which is outside a literal in every
    file this touches."""
    line_start = text.rfind('\n', 0, pos) + 1
    quote = None
    i = line_start
    while i < pos:
        c = text[i]
        if quote:
            if c == '\\':
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in '\'"`':
            quote = c
        i += 1
    return quote


def fragment_plans(old, new, kind):
    """Ways to cut (old, new) into pieces that each exist verbatim in a source
    file, most faithful first."""
    yield [(old, new)]
    if old.startswith('"') and old.endswith('"') and new.startswith('"') and new.endswith('"'):
        yield [(old[1:-1], new[1:-1])]
    speaker = re.compile(r"^([A-Z][A-Za-z .'’]{0,20}): ")
    mo, mn = speaker.match(old), speaker.match(new)
    if mo and mn and mo.group(0) == mn.group(0):
        bo, bn = old[mo.end():], new[mn.end():]
        yield [(bo, bn)]
        if bo.startswith('"') and bo.endswith('"') and bn.startswith('"') and bn.endswith('"'):
            yield [(bo[1:-1], bn[1:-1])]
    ph = re.compile(r'(\{[^{}]*\})')
    po, pn = ph.split(old), ph.split(new)
    if len(po) > 1 and len(po) == len(pn) and po[1::2] == pn[1::2]:
        yield list(zip(po[0::2], pn[0::2]))
    if '|' in old and old.count('|') == new.count('|'):
        yield list(zip(old.split('|'), new.split('|')))


def quote_only(s, quote):
    """Escape `quote` in an already-source-encoded string, stepping over the
    backslash pairs that encoding put there so they are not escaped twice."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == '\\':
            out.append(s[i:i + 2])
            i += 2
            continue
        out.append('\\' + c if c == quote else c)
        i += 1
    return ''.join(out)


def locate_fragment(text, view, index, frag_old, frag_new, ext):
    """Find one fragment. Returns (start, end, replacement) or None.

    The encoding that found the text is the encoding the site is written in, so
    the replacement is written the same way; on top of that, a .js/.py literal
    gets its own opening quote escaped, since the new line may contain an
    apostrophe where the old one did not."""
    for name, fn in TRANSFORMS:
        needle = fn(frag_old)
        if not needle:
            continue
        for hay, imap in ((text, None), (view, index)):
            if hay.count(needle) != 1:
                continue
            i = hay.index(needle)
            if imap is None:
                start, end = i, i + len(needle)
            else:
                start, end = imap[i], imap[i + len(needle) - 1] + 1
            # A match that starts one character into an escape sequence is not a
            # match: \\" is not a place where \" begins.
            if start > 0 and text[start - 1] == '\\':
                continue
            repl = fn(frag_new)
            if ext in ('.js', '.py'):
                quote = open_quote_at(text, start)
                repl = quote_only(repl, quote) if quote else quote_only(
                    quote_only(repl, "'"), '"')
            return (start, end, repl)
    return None


def apply_text(text, ext, change):
    view, index = concat_view(text)
    for plan in fragment_plans(change['old'], change['new'], change['kind']):
        edits, ok = [], True
        for frag_old, frag_new in plan:
            if frag_old == frag_new:
                continue
            hit = locate_fragment(text, view, index, frag_old, frag_new, ext)
            if hit is None:
                ok = False
                break
            edits.append(hit)
        if ok and edits:
            edits.sort()
            for a, b in zip(edits, edits[1:]):
                if a[1] > b[0]:
                    ok = False
            if ok:
                return edits
    return 'old text not found exactly once under any source encoding'


# =============================================================================
# 6. Driver
# =============================================================================
def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    changes_path = pathlib.Path(args[0] if args else 'docs/audit/changes-final.json')
    changes = json.loads(changes_path.read_text())

    # Group by the file that is actually edited, so each file is read once,
    # every edit is verified against that one snapshot, and the splices are
    # applied back to front.
    mirrors = [m for m in (mirrored(c) for c in changes) if m]
    by_file = {}
    for change in changes + mirrors:
        target = REDIRECT.get(change['file'], change['file'])
        by_file.setdefault(target, []).append(change)

    applied, mirrored_n, missed, edits_by_file = 0, 0, [], {}
    for target, group in sorted(by_file.items()):
        path = pathlib.Path(target)
        if not path.exists():
            for change in group:
                missed.append((change, 'file does not exist: %s' % target))
            continue
        text = path.read_text()
        ascii_only = all(ord(c) < 128 for c in text)
        ext = path.suffix
        spans = []
        for change in group:
            if ext in STRUCTURED:
                result = apply_structured(text, ascii_only, change)
                result = [result] if isinstance(result, tuple) else result
            else:
                result = apply_text(text, ext, change)
            if isinstance(result, str):
                missed.append((change, result))
                continue
            spans.extend((s, e, r, change['id']) for s, e, r in result)
            if change['id'].endswith('+mirror'):
                mirrored_n += 1
            else:
                applied += 1

        spans.sort()
        for a, b in zip(spans, spans[1:]):
            if a[1] > b[0]:
                raise SystemExit('overlapping edits in %s: %s and %s'
                                 % (target, a[3], b[3]))
        out = text
        for s, e, r, _ in reversed(spans):
            out = out[:s] + r + out[e:]
        edits_by_file[target] = len(spans)
        if not dry and out != text:
            path.write_text(out)

    print('changes read : %d' % len(changes))
    print('applied      : %d' % applied)
    print('missed       : %d' % len(missed))
    print('mirrored     : %d of %d npcs.json headline fields' % (mirrored_n, len(mirrors)))
    for target in sorted(edits_by_file):
        print('  %-60s %3d edits' % (target, edits_by_file[target]))
    for change, why in missed:
        print('MISS %s  %s  %s' % (change['id'], change['file'], change['locator']))
        print('     %s' % why)
        print('     old: %r' % change['old'][:160])
    return 1 if missed else 0


if __name__ == '__main__':
    sys.exit(main())
