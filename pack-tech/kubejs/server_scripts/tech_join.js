// tech_join.js -- Kettle Tech's entire first-join behaviour.
//
// The story pack's login handler (pack/kubejs/server_scripts/valley_core.js §5)
// does five things: auto-party, first-join letter + deed + kettle, an objective
// polling loop, bossbar re-attach, and a self-dismissing book nudge. Kettle Tech
// keeps ONE of them -- hand over the Quest Book and say where it is.
//
// Deliberately absent, because the whole point of this pack is that nothing
// happens to your world that you did not do yourself:
//   * no world edits, no structure placement, no teleports
//   * no title / subtitle cards
//   * no FTB Teams party command (a solo world already has a team; a second
//     player can /ftbteams party invite when they want shared quest progress)
//   * no repeating nudge -- the line below fires exactly once, ever, and there
//     is no follow-up on later logins
//   * no /give of anything but the book
//
// ONCE PER PLAYER, FOREVER. player.stages is KubeJS's own per-player stage set,
// stored in that player's saved data, so it survives logout, restart and death.
// A player who deletes the book gets it back the normal way (it is craftable),
// not by re-triggering this.

PlayerEvents.loggedIn(event => {
  let player = event.entity
  if (!player) return

  if (player.stages.has('kt_first_join')) return
  player.stages.add('kt_first_join')

  player.give(Item.of('ftbquests:book'))

  // One line. Aqua so it reads as a system note rather than someone talking,
  // and it names both ways in so nobody has to hunt for the keybind.
  player.tell(Text.aqua(
    'Kettle Tech: right-click the Quest Book, or press J. ' +
    'Start Here is the first chapter.'
  ))
})
