# Mod decisions

Log of every swap, cut, or pin, with the reason. Newest at the bottom.

| Date | Mod | Decision | Why |
|---|---|---|---|
| 2026-09-02 | Modern Industrialization, Tech Reborn | Not included | Pack moved from Fabric to Forge so Thermal Expansion could be the backbone. |
| 2026-09-02 | Geocluster | Replaced by Geolosys | Geocluster is the Fabric clone; Geolosys is the Forge original. |
| 2026-09-02 | Sodium / Lithium / Krypton | Replaced by Embeddium / Canary; Krypton dropped | Fabric-only; Forge ports used where they exist. |
| 2026-09-02 | Universal Graves | Replaced by Corpse | Fabric-only. Corpse does the same on Forge. |
| 2026-09-02 | Friends For Life | Replaced by Domestication Innovation | Fabric-only, every version. Domestication Innovation adds pet upgrades on Forge. |
| 2026-09-02 | Fancy Beds | Dropped | Not a real mod on either platform; only a resource pack by that name. Beds come from Macaw's and Handcrafted anyway. |
| 2026-09-02 | Bigger Reactors, FTB Quests, FTB Teams, FTB Library, FTB XMod Compat | Sourced from CurseForge | Not on Modrinth. packwiz pulls them with its built-in CurseForge key. |
| 2026-09-02 | Oculus / any shader mod | Not included | Visuals don't matter and the 8 GB Air needs the headroom. |
| 2026-09-02 | Phosphophyllite | Sourced from CurseForge, not the Modrinth "phos" project | Modrinth's "Phosphophyllite" is a different mod by a different author. Bigger Reactors needs BiggerSeries' library, which is CurseForge-only. |
| 2026-09-02 | Quartz | Added from CurseForge | Second required library for Bigger Reactors 0.6.0-beta.10. |
| 2026-09-02 | Duckling, ImmediatelyFast | Pinned to 3.0.0 and 1.2.4+1.20.1 | packwiz's non-interactive picker grabbed NeoForge 1.20.4 and 1.20.2 builds. Both mislabel game versions on Modrinth. |
| 2026-09-02 | EMI | Replaced by JEI | Thermal, Create, AE2, Bigger Reactors and Farmer's Delight all ship JEI plugins natively; EMI would have needed a JEI bridge to show their recipes. One recipe viewer, full coverage. |
| 2026-09-02 | Create Crafts & Additions | Added | Bridges Create rotational power and Thermal/AE2 RF with an alternator and motor. Without it the two power systems never touch. |
| 2026-09-02 | Jade Addons | Added (client) | Hover info for Create and Thermal machines, so "what is this doing" is answered on screen. |
| 2026-09-02 | Dynamic Lights (dynamic-torches) | Removed | It is a bundled datapack that runs a per-tick fill/clear loop of light blocks around every glowing entity, not a client renderer. Real TPS risk on a 3.5 GB client. Torchmaster's Feral Flare Lantern is the pack's carry-light. |
