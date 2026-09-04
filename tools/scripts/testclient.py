#!/usr/bin/env python3
"""Offline test client for verifying the pack on this Mac (mod-developer style; no account involved).
Usage: testclient.py install            -> installs Minecraft 1.20.1 + Forge 47.4.10 + assets into tools/client
       testclient.py command <gamedir> [--world NAME] [--xmx 3584] [--user NAME] -> prints the launch command (JSON list)
"""
import sys, json, pathlib, uuid, hashlib
import minecraft_launcher_lib as mll
ROOT = pathlib.Path(__file__).resolve().parents[2]
MCDIR = ROOT / 'tools' / 'client'
JAVA = ROOT / 'tools' / 'jdk17' / 'Contents' / 'Home' / 'bin' / 'java'
FORGE = '1.20.1-47.4.10'
def offline_uuid(name):
    """The uuid an offline-mode SERVER gives this login name: Java's
    UUID.nameUUIDFromBytes("OfflinePlayer:<name>"), i.e. an MD5 with the
    version-3 bits set. A uuid3 over the DNS namespace is NOT the same value,
    and the mismatch makes the client log
    "FTB Teams will not be able to function correctly!" and disables the team
    UI on the client — which is exactly the subsystem the two-player latch
    test depends on."""
    return uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:' + name).encode('utf-8')).digest(), version=3)

def progress():
    state = {'max': 0}
    return {'setStatus': lambda s: print('  ' + s), 'setProgress': lambda v: None, 'setMax': lambda m: state.update(max=m)}
if sys.argv[1] == 'install':
    print('installing forge', FORGE)
    mll.forge.install_forge_version(FORGE, str(MCDIR), callback=progress(), java=str(JAVA))
    vs = [v['id'] for v in mll.utils.get_installed_versions(str(MCDIR))]
    print('installed versions:', vs)
elif sys.argv[1] == 'command':
    gamedir = sys.argv[2]
    world = None; xmx = '3584'; user = 'packtester'
    if '--world' in sys.argv: world = sys.argv[sys.argv.index('--world') + 1]
    if '--xmx' in sys.argv: xmx = sys.argv[sys.argv.index('--xmx') + 1]
    # A second offline client needs its own login name AND its own offline uuid,
    # or the server rejects the join as a duplicate profile. Both come from here.
    if '--user' in sys.argv: user = sys.argv[sys.argv.index('--user') + 1]
    vs = [v['id'] for v in mll.utils.get_installed_versions(str(MCDIR)) if 'forge' in v['id']]
    version = vs[0]
    opts = {
        'username': user, 'uuid': str(offline_uuid(user)), 'token': '0',
        'executablePath': str(JAVA), 'jvmArguments': [f'-Xmx{xmx}M', '-Xms1024M', '-XX:+UseG1GC', '-XX:+UnlockExperimentalVMOptions', '-XX:G1NewSizePercent=20', '-XX:G1ReservePercent=20', '-XX:MaxGCPauseMillis=50', '-XX:G1HeapRegionSize=32M'],
        'gameDirectory': gamedir, 'launcherName': 'packtester', 'launcherVersion': '1',
    }
    if world: opts['quickPlaySingleplayer'] = world
    if '--server' in sys.argv: opts['quickPlayMultiplayer'] = sys.argv[sys.argv.index('--server') + 1]
    cmd = mll.command.get_minecraft_command(version, str(MCDIR), opts)
    print(json.dumps(cmd))
