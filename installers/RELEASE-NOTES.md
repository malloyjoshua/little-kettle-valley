# Release notes — the `friends` release

One dated entry per time the assets on
<https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends> change.

Hashes here are always computed from the **downloaded release assets**
(`gh release download friends --dir <tmp> --clobber && shasum -a 256 *`), never from a local build
directory — the point is to record what friends actually get, not what a build produced on this Mac.

---

## 2026-09-04 — Final polish: town residuals, quest text, Air render distance

CI run: <https://github.com/malloyjoshua/little-kettle-valley/actions/runs/33851790986> (`863edad`)

| Asset | Size (bytes) | sha256 |
| --- | ---: | --- |
| `LittleKettleValley-Setup.exe` | 56,798,712 | `f22bfff57aad0425d707c990a37ec80256b8de87b91b2032219e147e690e13c4` |
| `LittleKettleValley.dmg` | 47,152,808 | `698d54c19e99a680cae6ef603708fffd23ab8b310d034a27dabc1e6d9056afe0` |
| `LittleKettleValley.zip` | 92,386 | `f93819761f5e3402b0add88c0f0e9fb2de6771b667c1dd32194f71e115c855c6` |
| `Little Kettle Valley - Install Guide.pdf` | 87,179 | `ba04a7e96c2935adde83d6fc43368dc64d256770d1d23814463a02cb91f8571b` |

**What changed:** the source commit, and with it the `.exe` and `.dmg` (both now built from
`863edad` — town residual fixes, quest text edits for spring/summer crop timing, and the
`renderDistance`/`simulationDistance` defaults baked into the instance). `LittleKettleValley.zip`
is byte-identical to the last entry (`f9381976…`, unchanged size) — `pack/index.toml` was already
current and nothing under `dist/CozyTech` changed the zip's contents this round. The PDF is a
fresh `dist/v4/…` build; still not tracked in git (`dist/v*/` stays gitignored), so this entry is
the only record of `ba04a7e9…` anywhere but the release itself.

**Provenance checks that passed:**

- `tools/scripts/release.sh` ran end-to-end: zip rebuild (unchanged), packwiz index refresh (no
  diff), local `.dmg` rebuild, the `installers.yml` workflow triggered and watched to completion
  (`run 33851790986`, job `Windows one-click installer` succeeded in 1m57s including its own
  silent-install/config-rewrite/bundled-JRE/packwiz-bootstrap smoke test), then all four assets
  uploaded to the `friends` release with `--clobber`.
- Hashes above are from `gh release download friends --dir <tmp> --clobber && shasum -a 256 *`,
  i.e. what the release actually serves — not a local build directory.
- `raw.githubusercontent.com/malloyjoshua/little-kettle-valley/main/pack/index.toml` was pulled
  and diffed against the repo's `pack/index.toml` at `HEAD` (`863edad`): byte-identical
  (`31686ece…` both sides).
- `git status` was clean after the run — the release added no further commits (index and zip were
  already current from the pre-release commit).

---

## 2026-09-04 — Windows installer sizes the heap from the machine's RAM

CI run: <https://github.com/malloyjoshua/little-kettle-valley/actions/runs/33832227984> (`32422a1`)

| Asset | Size (bytes) | sha256 |
| --- | ---: | --- |
| `LittleKettleValley-Setup.exe` | 56,798,679 | `a4b16e495eac37503a682a465c34e75ff356a8558d75ca10adc043f40fc37c55` |
| `LittleKettleValley.dmg` | 47,152,247 | `2642335a6b2b0ab14935f8530fea492dd59cfbac480c40c630ffd17c22c7de5d` |
| `LittleKettleValley.zip` | 92,386 | `f93819761f5e3402b0add88c0f0e9fb2de6771b667c1dd32194f71e115c855c6` |
| `Little Kettle Valley - Install Guide.pdf` | 87,179 | `51d51556641a992550d5124123fc199a80ecc0fdb37f34f957012e128b6dec00` |

**What changed:** only the `.exe`. `MaxMemAlloc` is no longer baked at 3584 for everyone; the
installer reads physical RAM at install time and writes 3072 under 12 GB, 3584 for 12–24 GB, 4096
above 24 GB. The dmg, zip and PDF are the same bytes that were already on the release.

**Provenance checks that passed:**

- The `.exe` sha256 above is the same hash the workflow's *Describe artifact* step printed before
  uploading, so the release asset is byte-for-byte the artifact CI built.
- `LittleKettleValley.zip` on the release now matches `dist/LittleKettleValley.zip` on `main`
  (`f9381976…`). It did not before this release: `main` carried an older container (`a34ca7f3…`)
  whose *contents* were byte-identical (same names, sizes and CRC-32s) but whose archive metadata
  differed, which meant CI was building the `.exe` from a zip that was not the zip friends
  download. `tools/scripts/release.sh` now commits and pushes the zip before it triggers the
  workflow, and the workflow was re-run from the committed copy to produce the `.exe` above.
- The installer was silently installed four ways on the runner before upload — into a path with
  spaces (`D:\lkv smoke test\Little Kettle Valley`), into a path with a `#`, and twice more with
  the `/LKVRAMGB` test override — and the bundled JRE ran the instance's verbatim
  `PreLaunchCommand`, which installed 125 mods.
- RAM detection ran for real rather than falling back: the setup log reads
  `PhysicalRamGB: 16378 MB physical -> 16 GB` / `ChosenMaxMemMB: 16 GB -> MaxMemAlloc=3584`, and
  16,378 MB agrees with the 17,174,360,064 bytes Windows itself reports for the runner.

**Known drift, not fixed here:** the PDF on the release is the locally-built `dist/v3/…`
(`51d51556…`). The copy tracked in git is still `dist/v2/…` (`5bfa0543…`, same size, different
bytes). `dist/v*/` is gitignored, so a new guide only reaches the repo if it is force-added — worth
deciding on, but out of scope for this pass.
