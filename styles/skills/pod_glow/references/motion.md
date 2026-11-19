# Motion: curves, transitions, frame counts (30 fps)

## Caption words: drop-in

| Frame | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|
| Y offset (× key size) | −0.25 … −0.30 | −0.07 … 0 | +0.03 … +0.05 | 0 |
| Opacity % | 35–50 | 95–100 | 100 | 100 |
| Blur px (at 1080 wide) | 4–6 | 0–1 | 0 | 0 |

The word starts **above** its final place and drops in; ≈ 0.1 s total. The caption block itself never scales or moves. Details and timing rules: `captions.md`.

## Cards, icons, tags (non-caption elements)

| Frame | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Scale % | 80 | 96 | 106 | 108 | 103 | 100 |
| Opacity % | 0 | 70 | 100 | 100 | 100 | 100 |

This pop is for **icons, tag pills, badges, tiles and card titles only**, never for caption words. Keys at f0/f3/f5 = 80/108/100 with ease in/out. Tools whose overshoot easing can't drive opacity (values > 100 % are refused): animate scale with overshoot and opacity separately with ease-out.

## Exits

- Captions: hard cut on the next chunk's first frame (no fade).
- Overlays (network, glass card, ???): 4–5 f fade + 96 % scale.
- Full-screen cards: white flash or hard cut + hit. Never a slow crossfade.

## Transitions

| Transition | Use | Frames |
|---|---|---|
| White flash | speaker switch; out of a white card | 2 f white (100 %, 60 %) |
| Capsule zoom-out | into the orbit card | 4 f into capsule + 8 f pull back, directional zoom blur |
| Scale-down + blur | into a white card | 6 f from 115 % with motion blur |
| Light leak | section turn, on footage | 12–18 f sweep, peak 70 % |
| Hard cut | re-frames, back from orbit | 0 f |

No whip pans, no spins, no glitch, no cube/page transitions.

## Re-frames and camera

- Re-frame cuts on phrase boundaries only, never mid-word.
- Optional slow push on long holds: 100 → 104 % over 3 s.
- Shake: none. This style is smooth; emphasis comes from type and glow, not camera hits.

## Motion blur

On for: cards travelling in, the capsule move, icons popping. Caption words get their blur from the drop-in table above; off during holds (they must be crisp). Off for glass card text.

## Pace check

Count visual events per 10 s (cut, re-frame, card, flash, leak). Target 4–6. Fewer feels static; more than 7 hides the speaker.
