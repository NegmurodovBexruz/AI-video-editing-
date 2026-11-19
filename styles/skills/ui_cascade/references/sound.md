# Sound

## Layers

1. **Speech.** Cleaned (de-noise, light compression), always on top.
2. **Bed.** A low, steady modern beat or pad under the whole film. It sits 18–22 dB under the speech; in pauses it is audible but never loud. Duck by 3–4 dB more under dense speech.
3. **SFX, one per device, on the device's first frame:**

| Device | Sound | Level under speech peak |
|---|---|---|
| Negative stutter / bloom glitch | short digital glitch + airy whoosh (100–250 ms) | −6 to −10 dB |
| Icon tile | soft pop / bubble | −14 dB |
| Card fan | quick riser-swish while the cards rise | −14 dB |
| Counter dropping | fast ticks, ending on a low thud | −16 dB |
| Button press | UI click | −14 dB |
| Fade to white | soft swoosh | −12 dB |
| List item add / tick | light tick | −18 dB |
| Chat bubble | message pop | −12 dB |
| Figure bar | short swipe | −18 dB |

Letter cascades get **no** sound.

## Rules

- Never cover a spoken word with an SFX louder than −10 dB under it.
- Keep the bed under app scenes; there the SFX carry the rhythm.
- The bed continues to the last frame and fades over the last 0.5–1 s. No hard stop on a frozen frame.

## Loudness

- −14 LUFS integrated, true peak ≤ −1 dBTP, unless the brief asks otherwise.
- Use licensed or generated music and SFX only, and note the source in the README.
