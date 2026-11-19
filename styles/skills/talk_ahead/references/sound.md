# Sound

## Rules

- **Banned:** whoosh, swish, swoosh, air passes, white-noise risers. The user rejected them ("fish/shish").
- **One material family per film**, taken from the brand's world (metal: clangs, rings, ratchets, hatch thuds; glass: taps, chimes; wood: knocks; paper: flips; tech without a material: soft ticks, sub hits, reversed bells). 4–6 sounds, varied by pitch and seed.
- **Every visible event has a sound** at its frame: slams → heavy hit (+ sub drop on the biggest), letter rise/labels → light tick, counters → accelerating ticks ending in a hit, wipes → sub drop, inserts → light ring, arrival on a map → heavy hit, logo → reversed swell ending on a soft hit.
- **Silence before the peak:** pull the music back 0.3–1 s before the biggest hit of the film.

## Levels

- Voice at −16 LUFS-ish, music ducked 10 dB under it, SFX ~2 dB above the bed.
- Master −14 LUFS integrated, true peak ≤ −1 dBTP. Measure with `ebur128=peak=true` and report the numbers.

## Music brief (for a generator or a library search)

Instrumental, sections timed to the beats, e.g. for a 32 s film:

| Section | Length | Feel |
|---|---|---|
| Intro | 3.0 s | sparse drone, material resonance, anticipation |
| Pulse | ~6.8 s | steady muted kick, ticking hats, bass ostinato |
| Build | ~6.8 s | tension, layered percussion, crescendo into the main device |
| Drive | ~6.6 s | full groove under the voice |
| Lift | ~5.0 s | wide pad, big low hits (scale moment) |
| Resolve | ~4.4 s | drums stop, one final hit, long tail under the logo |

Negative styles: vocals, choir, EDM drop, dubstep, whooshes, ukulele/happy corporate.

## Licences (check before generating, not after)

- Use only sounds/music the user may publish commercially. Generator outputs made on a **free tier** usually carry no commercial licence and stay that way after upgrading — check the account tier first (a 402/"paid plan required" answer is the tell), and don't put free-tier outputs in a client deliverable.
- Synthesized sounds (numpy/ffmpeg) are always safe; prefer them over unlicensed files.
- Never download copyrighted tracks.
