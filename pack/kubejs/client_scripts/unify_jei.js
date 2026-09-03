// unify_jei.js — hides the retired half of every unified material from JEI.
// MUST live in kubejs/client_scripts/ — JEIEvents does not exist server-side
// and putting this in server_scripts throws on load.
JEIEvents.hideItems(event => {
  const RETIRED = [
    'geolosys:tin_ingot', 'geolosys:tin_nugget',
    'geolosys:silver_ingot', 'geolosys:silver_nugget',
    'geolosys:lead_ingot', 'geolosys:lead_nugget',
    'geolosys:nickel_ingot', 'geolosys:nickel_nugget',
    'geolosys:zinc_ingot', 'geolosys:zinc_nugget',
    'geolosys:copper_nugget',
    'createaddition:electrum_ingot', 'createaddition:electrum_nugget',
    'createaddition:electrum_block',
    'createdeco:netherite_nugget'
  ]
  RETIRED.forEach(id => event.hide(id))
})
