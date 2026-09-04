# Release notes — the `friends` release

One dated entry per time the assets on
<https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends> change.

Hashes here are always computed from the **downloaded release assets**
(`gh release download friends --dir <tmp> --clobber && shasum -a 256 *`), never from a local build
directory — the point is to record what friends actually get, not what a build produced on this Mac.

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
