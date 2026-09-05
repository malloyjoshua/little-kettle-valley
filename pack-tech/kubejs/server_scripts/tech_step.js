// valley_step.js — auto step-up. Josh: "we definitely need the auto step up one
// block mod." No mod needed on Forge 1.20.1: the forge:step_height_addition
// attribute raises how tall a step the player walks over without jumping.
// Vanilla is 0.6 (half a block); +0.6 makes a full block a step. Set on every
// login so it survives death, dimension changes and a new install.
PlayerEvents.loggedIn(event => {
  let server = event.server
  let name = event.player.name.string
  server.runCommandSilent('attribute ' + name + ' forge:step_height_addition base set 0.6')
})
