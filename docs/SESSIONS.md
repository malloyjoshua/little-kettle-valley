# Two Claude sessions share this repo (2026-09-04 night)

- **Little Kettle Valley** (story pack): `pack/`, `story/`, `server/`, `world-master/`, `tools/scripts/*` (server_ctl.sh, sync_server.sh, playthrough.sh). Test server process: `forge/1.20.1 ... unix_args` started from `server/`.
- **Kettle Tech** (no-story edition): `pack-tech/`, `story-tech/`, `server-tech/`.

Rules so we stop killing each other's builds:
1. Only stop a server you started: match the directory in the pattern (`pgrep -f "server-tech/.*unix_args"` vs `pgrep -f "/server/.*unix_args"`), never a bare `unix_args` fallback.
2. Never sync `pack-tech/` into `server/` or `pack/` into `server-tech/`.
3. Stage commits by explicit path only; never `git add -A`.
4. `tools/scripts/*` are shared; edit them additively (flags, env vars), never change defaults the other pack relies on.
