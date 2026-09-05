# Status: 2026-09-05, morning (final)

## Where it stands
Little Kettle Valley was rebuilt overnight on a new foundation. The valley is now one hand-built world that ships with the pack: the farm, the abandoned town, the lantern road, forty dark lamp posts, the sealed Works, the pier, the greenhouse and bathhouse shells and three empty houses all exist from the first second, on real terrain, on a famous seed. The story never builds anything any more. It lights lamps, opens doors, sets furniture into empty air and brings people in. Nothing scripted can touch a block you placed. That is the fix for "the house gets replaced and everything breaks": there is no longer any code path that could do it.

Every claim below was checked by running the real thing, not by reading code.

## Launching (you)
1. Open Prism Launcher, launch **Little Kettle Valley**. The pre-launch step pulls the update, including the world (68 files, 55 MB, one time).
2. Singleplayer: open the world called **Little Kettle Valley**. Do not create a new world; the story lives in this one. Your older worlds are still listed and still work, but they are the old design.
3. You wake on a road with the farm signpost beside you and two lamp posts ahead. Read the letter in your hand, follow the road north to the farm, put the waystone on the hearthstone, hang the door, windows, bed and sconce in the holes. The town is beyond the farm; you will see it when you crest the rise.
4. To make Prism open the world automatically at launch, add these two lines to the instance's `instance.cfg` (the friend packages already have them):
```
JoinServerOnLaunch=true
JoinWorldOnLaunch=Little Kettle Valley
```

## Handing it to your wife
1. Send her `LittleKettleValley.dmg` from the [release page](https://github.com/malloyjoshua/little-kettle-valley/releases/tag/friends). The three steps are drawn on the disk image. She signs in with her Microsoft account and clicks Play; it opens straight into the valley.
2. Memory and render distance are preset for the Air. Measured on this Mac at her exact settings (3072 MB, render 6): 3.9 GB peak while the world loads, 3.2 GB steady in town, no garbage-collection pause over 50 ms, 30 s to the title, 32 s into the world. Comfortable.
3. To play together she connects to your server: address `cynthia-mfc.tun.ply.gg` (the playit tunnel; start it with `tools/scripts/playit_ctl.sh start`). Your server's world is the same valley. Whitelist her name first.

## What changed overnight
- **The world.** Famous seed 5369984945557223422 (lakeside plains with a north ridge), pre-generated 1024 blocks across so nothing stutters on first load. The town is terraced onto the land, each building on its own level with stepped streets between; the road has shoulders, not banks; nine terrain probes pass (straight cut edges, exposed faces, doorsteps, lamp footing, road grade, plaza dry, lake view, road banks, pad material).
- **Arrival.** Spawn is on the far side of the farm so the road order is spawn, farm, town, and the town stays hidden behind the farm's rise until you have a home. A real client showed the first frame was facing the wrong way (a vanilla quirk: the world's spawn angle only applies to respawns); it now turns you up the road before your first frame renders.
- **The story.** Every beat that used to build now only adds. The cottage stands with visible gaps you fill by hand; the stake goes into a socket on the square; the residents move into houses that were always there. Quest text updated to match. All 135 quests, five finales and 21 scenes were played through by an automated client on the shipped world, twice, with zero errors, and twenty blocks salted around the farm and square survived the whole game.
- **The quest book, the Astral way.** Whole chapter visible from the start (greyed, not hidden), one toast per quest completion instead of eleven, a "Read Me First" tab, a tiny "Start Here" chapter, Oda's Counter in a Side Quests group, optional quests marked optional, the book handed over once with one nudge that dismisses itself. Recipe, tutorial and system toasts are blocked by Toast Control.
- **Auto step-up** over one-block edges, no mod needed. **Regions Unexplored** removed so the famous seed looks as advertised and the Air breathes; the structure mods that make exploring good are untouched.
- **Traps closed:** the kettle, the apple press and the chicken nest all drop back into your hand; three quests no longer consume the thing they told you to place; `/valley keepsake` hands back any of 23 story items.


## Structures (2026-09-05 midday)
Josh: "the structures are a little bland." Rebuilt with the mods' richest pieces and two designed buildings: a 37-block meadow tower with a real bell for the church (the only piece in 2,505 templates with both a bell and a door), a quartz fountain at the centre of a ringed square with benches on a trestle instead of chair rows, richer chalets for Marnie and Pip, a fisher's house and a covered boat slip on the lake beside the pier, a real mill race with a head basin, footbridge and wheel pit, a glass barrel-vault greenhouse on copper ribs, a copper-roofed bathhouse with cauldron tubs, hanging name signs at every named door, window boxes, five fenced plots and pens, eight trees and an orchard behind the farm. Every street lantern is gone; the valley is dark until the story lights it. Verified headless twice on fresh copies (5 finales, 21 scenes, every door the story opens now actually opens: that was a real bug, doors written one half at a time snap shut), all probes pass, world repackaged and released.
Still soft: Oda's store and the hedge garden sit 40 blocks north as outliers; the twelve lantern rafts on the lake ship lit; the full client playthrough on this world is pending a window when the Mac is free.

## Numbers
| Thing | Count |
|---|---|
| Mods | 127 |
| Quests | 135 across 8 chapters (Read Me First, Start Here, five acts, Oda's Counter) |
| Shipped world | 68 files, 55 MB, seed 5369984945557223422, spawn -324 75 116 |
| Lamps | 40, all dark at the start, 6 lit by the end of Act I, 40 by Founder's Day |
| Residents | 15 |
| Automated playthroughs on the shipped world | 2 clean (135/135, 0 errors) |

## Honest list of what still reads as generated
The look pass took twenty screenshots in the real client and ranked what a first-time player would notice (`media/look/NOTES.md`, pictures alongside). Fixed this morning: the arrival facing, the farm yard (overgrown again), bare-earth scars, 73 hostile mobs that were baked into the snapshot, the square's ordinary lanterns and cart torches (the square is dark now until Act I lights it), and the step in front of the first frame. Still open, in order of how loudly they show:
- From the ridge, the valley floor shows long parallel contour steps: the terracing's safety rule (no column more than one block above its neighbour) produces a staircase. Fix is in the planner: shorter reach for the grading, or steps that wander.
- The church is an undetailed stone box; the greenhouse is glass stuck on a plank wall; "the mill by the water" is a seven-block gutter. Template and decoration work.
- The residents bunch up at the waystone during finales.
- Render distance ships at 8. Raising it to 12 costs about 600 MB of process memory and no heap; your call.

## Still yours
- Play the first hour yourself before she does. Everything above was seen by an automated client and by me in screenshots, not by a person at the keyboard.
- Whitelist and op yourself on the server (commands in `docs/RUNBOOK.md`), start the playit tunnel when friends want in.
- Her three cute-mod picks, whenever she names them.

## If something breaks
`docs/RUNBOOK.md`: start, stop, backup, the world (never delete `server/world`; `world-master/` is the pristine source), resetting a friend's singleplayer copy, live story fixes, the playthrough harness (`tools/scripts/playthrough.sh`, about 25 minutes).
