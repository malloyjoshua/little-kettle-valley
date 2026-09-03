// =============================================================================
// hide.js - JEI cleanup for the Little Kettle Valley
// KubeJS 2001.6.5 / Forge 1.20.1. MUST live in kubejs/client_scripts/ -
// JEIEvents does not exist server-side and throws on load in server_scripts.
// =============================================================================
// Replaces the old pack/kubejs/client_scripts/unify_jei.js (deleted).
//
// RULE: only hide an item whose producers unify.js actually removed.
// Hiding an item a machine still spits out means JEI cannot explain something
// the player is holding - that is the "disconnected experience" this pack is
// supposed to avoid. So:
//   HIDDEN     = unify.js HARD_RETIRE set (Geolosys duplicate ingots/nuggets;
//                every producer was a vanilla crafting/smelting recipe and was
//                removed by id or by type-scoped output filter).
//   NOT HIDDEN = createaddition:electrum_* (Create's Mixer and Crushing Wheels
//                still emit these), createdeco:netherite_nugget (still the only
//                legal input to the Netherite Coin press).
//
// event.hide() takes ONE ingredient per call - there is no array overload on
// HideJEIEventJS in this build. Always .forEach.
// =============================================================================

JEIEvents.hideItems(event => {

  // ---------------------------------------------------------------------------
  // 1. Retired duplicate metals - unobtainable after unify.js.
  // ---------------------------------------------------------------------------
  let RETIRED = [
    'geolosys:tin_ingot', 'geolosys:tin_nugget',
    'geolosys:silver_ingot', 'geolosys:silver_nugget',
    'geolosys:lead_ingot', 'geolosys:lead_nugget',
    'geolosys:nickel_ingot', 'geolosys:nickel_nugget',
    'geolosys:zinc_ingot', 'geolosys:zinc_nugget',
    'geolosys:copper_nugget'
  ]

  // ---------------------------------------------------------------------------
  // 2. Genuinely unreachable items - no producing recipe is active in this pack
  //    at all, so they can only ever appear in a creative menu.
  //    create:crushed_raw_quicksilver: forge:ores/quicksilver and
  //    forge:raw_materials/quicksilver do not exist in this pack (Thermal's
  //    mercury analogue is named "cinnabar" and is never tagged as quicksilver),
  //    so both of Create's producing recipes self-disable on forge:tag_empty.
  // ---------------------------------------------------------------------------
  let UNREACHABLE = [
    'create:crushed_raw_quicksilver'
  ]

  // ---------------------------------------------------------------------------
  // 3. Thermal ores retired by config. Once World.Features.{Tin,Lead,Silver,
  //    Nickel}.Enable = false (see scratch/config_edits.json), Thermal's own raw
  //    items have no source - Geolosys clusters are the single raw item per
  //    metal. Their INGOTS stay visible; they are the canonical ones.
  //    NOTE: leave these commented until that config edit ships, otherwise you
  //    hide items the world is still generating.
  // ---------------------------------------------------------------------------
  let RETIRED_THERMAL_RAW = [
    'thermal:raw_tin',
    'thermal:raw_lead',
    'thermal:raw_silver',
    'thermal:raw_nickel'
  ]

  RETIRED.forEach(id => event.hide(id))
  UNREACHABLE.forEach(id => event.hide(id))
  RETIRED_THERMAL_RAW.forEach(id => event.hide(id))
})
