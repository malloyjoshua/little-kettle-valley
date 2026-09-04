#!/usr/bin/env python3
"""Build the Little Kettle Valley Easy NPC presets from story/npcs.json.

Usage: make_npc_presets.py <npcs.json> <pack_dir> [--check]
  <pack_dir>  the pack root, e.g. .../Minecraft/pack
  --check     parse-validate only, write nothing

Writes  <pack>/kubejs/data/valley/easy_npc/preset/<key>.npc.snbt   (the ONLY path Easy NPC accepts)
        <pack>/kubejs/server_scripts/valley_greetings.js              (GENERATED -- never hand-edit)

The greeting pools are the second output. Each resident's ON_INTERACTION runs
`/valley greet <key> <before|after> @initiator` instead of a pair of
/info_message lines, so the only string the generator ever emits into Cmd is 20-46
characters with no quotes in it, and the lines themselves are chat, not a screen
title -- which is what lets a resident have five of them instead of one.

The second, "compat" tree at <pack>/kubejs/data/valley/preset/ was deleted on
2026-09-02. PresetSecurity#isAllowedDataPresetPath rejects any resource path
that does not start with "easy_npc/preset/", so those files could never load;
all they did was double the packwiz index and give a future editor two places
to change a line of dialogue and one of them wrong.

Structure is the jar's own base preset:
  unzip -p server/mods/easy_npc-*.jar data/easy_npc/api/preset/base/humanoid.npc.snbt
with only fields whose names appear in the jar's classes:
  ActionDataEntry      -> Type Cmd ExecAsUser PermLevel ConditionDataSet
  ConditionDataEntry   -> Type Name Operation Value
  ConditionDataSet     -> nested key "ConditionDataSet" holding the list
  SkinDataEntry        -> Type
  PresetMetadata       -> access author category created description entityTypeId modified name variantType version

Three things verified in the jars that the preset MUST respect:
  1. PresetSecurity#isAllowedDataPresetPath -- a data preset resource path must start with
     "easy_npc/preset/". valley:preset/x.npc.snbt is rejected; valley:easy_npc/preset/x.npc.snbt works.
  2. PresetAccess#isUsableByCommand -- access:"INTERNAL" (what the base template ships with)
     cannot be imported by command. Every valley preset is access:"PUBLIC".
  3. FTBQuestsCommands -- "open_book" takes an optional quest_object and NO player argument; it
     opens for the source player. So the book action is /ftbquests open_book with ExecAsUser:1b,
     which pack/config/easy_npc/security.cfg already allows (executeAsUserCommandAllowList.ALL).

Exit 1 on any validation failure."""
import sys, json, uuid, pathlib, struct

VARIANTS = {
    'easy_npc:humanoid': {'ALEX','ARI','EFE','KAI','MAKENA','NOOR','STEVE','SUNNY','ZURI',
                          'JAYJASONBO','PROFESSOR_01','SECURITY_01','KNIGHT_01','KNIGHT_02'},
    'easy_npc:humanoid_slim': {'ALEX','ARI','EFE','KAI','MAKENA','NOOR','STEVE','SUNNY','ZURI','KAWORRU'},
}
OPERATIONS = {'NONE','EQUALS','NOT_EQUALS','GREATER_THAN','GREATER_THAN_OR_EQUALS','LESS_THAN','LESS_THAN_OR_EQUALS'}
CREATED_MS = 1788000000000  # fixed so regenerating produces byte-identical files

errors = []


# ---------------------------------------------------------------- SNBT emitter
class Raw(str):
    """Emitted verbatim (byte/int-array/single-quoted literals)."""


def sstr(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def sq(s):
    """Single-quoted SNBT string, for JSON text components."""
    return Raw("'" + str(s).replace('\\', '\\\\').replace("'", "\\'") + "'")


def uuid_array(name):
    """data.UUID as the 4 signed ints Minecraft stores. PresetHandler#importPresetData
    branches on this: same UUID -> update the existing NPC in place (idempotent import)."""
    b = uuid.uuid5(uuid.NAMESPACE_URL, 'copperkettle://npc/' + name).bytes
    return Raw('[I;' + ','.join(str(i) for i in struct.unpack('>4i', b)) + ']')


def emit(v, ind=0):
    pad, pad2 = '  ' * ind, '  ' * (ind + 1)
    if isinstance(v, Raw):
        return str(v)
    if isinstance(v, bool):
        return '1b' if v else '0b'
    if isinstance(v, str):
        return sstr(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, dict):
        if not v:
            return '{}'
        body = ',\n'.join(pad2 + k + ':' + emit(x, ind + 1) for k, x in v.items())
        return '{\n' + body + '\n' + pad + '}'
    if isinstance(v, list):
        if not v:
            return '[]'
        if all(not isinstance(x, (dict, list)) for x in v):
            return '[' + ','.join(emit(x, ind) for x in v) + ']'
        body = ',\n'.join(pad2 + emit(x, ind + 1) for x in v)
        return '[\n' + body + '\n' + pad + ']'
    raise TypeError(type(v))


# ---------------------------------------------------------------- preset build
def condition(c, where):
    if c['operation'] not in OPERATIONS:
        errors.append(f'{where}: unknown condition operation {c["operation"]}')
    if c['type'] != 'SCOREBOARD':
        errors.append(f'{where}: only SCOREBOARD conditions are generated, got {c["type"]}')
    return {'Name': c['name'], 'Operation': c['operation'], 'Type': c['type'], 'Value': int(c['value'])}


def action(a, where):
    if a['type'] != 'COMMAND':
        errors.append(f'{where}: only COMMAND actions are generated, got {a["type"]}')
    cmd = a['cmd']
    if '"' in cmd:
        errors.append(f'{where}: a double quote in Cmd breaks /info_message JSON -- rewrite the line')
    if len(cmd) > 120:
        errors.append(f'{where}: Cmd is {len(cmd)} chars; /info_message renders as a screen title, keep it short')
    if a['exec_as_user'] and cmd.lstrip('/').split(' ')[0] not in ('ftbquests', 'trigger', 'me'):
        errors.append(f'{where}: ExecAsUser command root is not in security.cfg executeAsUserCommandAllowList.ALL')
    e = {'Cmd': cmd, 'ExecAsUser': bool(a['exec_as_user']), 'PermLevel': int(a['perm_level'])}
    if a.get('conditions'):
        e['ConditionDataSet'] = {
            'ConditionDataSet': [condition(c, where) for c in a['conditions']]
        }
    e['Type'] = a['type']
    return dict(sorted(e.items()))


def greetings_js(npcs):
    """The runtime line pools. global.valleyGreetings is a plain object literal
    with no dependency on global.valley, so KubeJS load order does not matter."""
    def js(v):
        return json.dumps(v, ensure_ascii=False)
    lines = [
        '// GENERATED by tools/scripts/make_npc_presets.py from story/npcs.json.',
        '// Do not hand-edit: edit story/npcs.json and re-run the generator.',
        '//',
        "// Read by global.valley.greet() in valley_core.js, which /valley greet",
        '// (valley_finales.js command tree) calls when a resident is right-clicked.',
        '// Element 0 of each pool is the headline line that resident has always had.',
        'global.valleyGreetings = {',
    ]
    body = []
    for n in npcs:
        entry = ['    name: ' + js(n['name'].split(' ')[0]),
                 '    before: [\n      ' + ',\n      '.join(js(x) for x in n['greetings']) + '\n    ]']
        if n.get('greetings_after'):
            entry.append('    after: [\n      ' + ',\n      '.join(js(x) for x in n['greetings_after']) + '\n    ]')
        body.append('  ' + js(n['key']) + ': {\n' + ',\n'.join(entry) + '\n  }')
    lines.append(',\n'.join(body))
    lines.append('}')
    return '\n'.join(lines) + '\n'


def build(n):
    key, et, var = n['key'], n['entity_type'], n['variant']
    where = f'npc {key}'
    if et not in VARIANTS:
        errors.append(f'{where}: entity_type must be easy_npc:humanoid or easy_npc:humanoid_slim, got {et}')
    elif var not in VARIANTS[et]:
        errors.append(f'{where}: {var} is not a {et} skin variant (jar enum)')
    if not n['tags'] or n['tags'][0] != 'valley_npc':
        errors.append(f'{where}: tags must start with valley_npc')
    if n.get('arc') and not n.get('greeting_after'):
        errors.append(f'{where}: has an arc but no greeting_after')
    pools = [('greetings', n.get('greetings')), ('greetings_after', n.get('greetings_after'))]
    if not n.get('greetings'):
        errors.append(f'{where}: no greetings pool')
    elif n['greetings'][0] != n['greeting']:
        errors.append(f'{where}: greetings[0] must be the headline greeting')
    if n.get('greeting_after') and not n.get('greetings_after'):
        errors.append(f'{where}: has greeting_after but no greetings_after pool')
    if n.get('greetings_after') and n['greetings_after'][0] != n['greeting_after']:
        errors.append(f'{where}: greetings_after[0] must be the headline greeting_after')
    for pname, pool in pools:
        for line in (pool or []):
            if not line or not str(line).strip():
                errors.append(f'{where}: empty line in {pname}')

    actions = [action(a, where) for a in n['on_interaction']]
    if not any(a['Cmd'] == '/ftbquests open_book' for a in actions):
        errors.append(f'{where}: no open_book action')

    data = {
        'ActionData': {'ActionEventSet': {'ON_INTERACTION': actions}},
        'ArmorDropChances': [Raw('0.085f')] * 4,
        'ArmorItems': [{}, {}, {}, {}],
        'Brain': {'memories': {}},
        'CanPickUpLoot': False,
        'CustomName': sq(json.dumps({'color': n['color'], 'text': n['name']}, separators=(',', ':'))),
        'CustomNameVisible': True,
        'EasyNPCVersion': 3,
        'HandDropChances': [Raw('0.085f')] * 2,
        'HandItems': [{}, {}],
        'Invulnerable': True,
        'LeftHanded': False,
        'ModelData': {},
        'ObjectiveData': {'HasObjectives': True,
                          'ObjectiveDataSet': [{'Type': 'LOOK_AT_PLAYER'}, {'Type': 'LOOK_AT_RESET'}]},
        'PersistenceRequired': True,
        'SkinData': {'Type': 'DEFAULT'},
        'Status': {'finalized': True},
        'Tags': list(n['tags']),
        'UUID': uuid_array(key),
        'VariantType': var,
        'id': et,
    }
    meta = {
        'access': 'PUBLIC',          # INTERNAL would make it unusable by command
        'author': 'Little Kettle Valley',
        'category': 'Valley',
        'created': Raw(f'{CREATED_MS}L'),
        'description': f'{n["name"]} -- {n["role"]}.',
        'entityTypeId': et,
        'modified': Raw(f'{CREATED_MS}L'),
        'name': n['name'],
        'variantType': var,
        'version': '1.0.0',
    }
    return {'PresetMetadata': meta, 'data': data}


# ---------------------------------------------------------------- main
def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    if len(args) != 2:
        sys.exit(__doc__)
    src, pack = pathlib.Path(args[0]), pathlib.Path(args[1])
    doc = json.loads(src.read_text())
    npcs = doc['npcs']

    real = pack / 'kubejs' / 'data' / 'valley' / 'easy_npc' / 'preset'

    seen, written = set(), []
    for n in npcs:
        if n['key'] in seen:
            errors.append(f'duplicate key {n["key"]}')
        seen.add(n['key'])
        text = emit(build(n)) + '\n'
        try:
            import nbtlib
            nbtlib.parse_nbt(text)
        except ImportError:
            errors.append('nbtlib is not importable -- run with tools/venv/bin/python')
        except Exception as e:
            errors.append(f'{n["key"]}: SNBT does not parse: {e}')
        written.append((n['key'], text))

    if errors:
        for e in errors:
            print('ERROR ' + e, file=sys.stderr)
        sys.exit(1)

    if check:
        print(f'{len(written)} presets parse clean (nothing written)')
        return

    real.mkdir(parents=True, exist_ok=True)
    for key, text in written:
        (real / f'{key}.npc.snbt').write_text(text)
        print(f'  {key}.npc.snbt')

    greet = pack / 'kubejs' / 'server_scripts' / 'valley_greetings.js'
    greet.write_text(greetings_js(npcs))
    n_lines = sum(len(n['greetings']) + len(n.get('greetings_after') or []) for n in npcs)
    print(f'  valley_greetings.js  ({n_lines} lines across {len(npcs)} residents)')

    objectives = doc['meta']['arc_gating']['setup_commands']
    print(f'\n{len(written)} presets -> {real}')
    print('\nvalley_core.js must create these on server load or both greeting lines stay hidden:')
    for c in objectives:
        print('  /' + c)
    print('\nImport a resident with:')
    print('  /easy_npc preset import data valley:easy_npc/preset/<key>.npc.snbt <x> <y> <z>')


if __name__ == '__main__':
    main()
