# Two Claude sessions share this repo (2026-09-04 night)

- **Little Kettle Valley** (story pack): `pack/`, `story/`, `server/`, `world-master/`, `tools/scripts/*` (server_ctl.sh, sync_server.sh, playthrough.sh). Test server process: `forge/1.20.1 ... unix_args` started from `server/`.
- **Kettle Tech** (no-story edition): `pack-tech/`, `story-tech/`, `server-tech/`.

Rules so we stop killing each other's builds:
1. Only stop a server you started: match the directory in the pattern (`pgrep -f "server-tech/.*unix_args"` vs `pgrep -f "/server/.*unix_args"`), never a bare `unix_args` fallback.
2. Never sync `pack-tech/` into `server/` or `pack/` into `server-tech/`.
3. Stage commits by explicit path only; never `git add -A`.
4. `tools/scripts/*` are shared; edit them additively (flags, env vars), never change defaults the other pack relies on.

## 2026-09-05, the shipped-story pass

Two files moved and one is new; if you are the other session, this is what changed under you.

- **New:** `pack/kubejs/server_scripts/valley_build.js` — every pad, template and fill in the
  pack, behind `/valley build` (permission 2). `valley_finales.js` now refuses all four at
  runtime.
- **New, GENERATED:** `pack/kubejs/server_scripts/valley_sites.js` — the fixed registry as
  `global.valleySites`, `// priority: 2000`. Written by `tools/scripts/plan_town.py --site`
  alongside `valley_sites.json`. Do not hand-edit either.
- `tools/scripts/sync_server.sh` gained an **orphan sweep**: a jar in `server/mods` that the
  index does not name is moved to `scratch/orphan_mods_<stamp>/` and printed. It is additive
  and it is why `server/` can be synced from either pack without a stale mod refusing every
  client join with "mismatched mod channel list" — which is exactly what
  `inventorysorter-1.20.1-23.1.9.jar` was doing on 2026-09-05.
- `tools/scripts/playthrough.sh` is rewritten for the shipped world: it installs
  `world-master/` into `server/world`, salts twenty player blocks, and reads its verdict off
  the region files with the server stopped. It still refuses to start if a Forge server or a
  Minecraft client is already running, and it identifies our server by working directory, not
  by a bare `unix_args` pgrep.
