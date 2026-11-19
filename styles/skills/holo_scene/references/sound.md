# Sound

## Layers

1. **Speech:** untouched timing. Chain: high-pass 80 Hz, −2 dB around 300 Hz, +2 dB around 4 kHz, de-esser, compressor 3:1.
2. **Music bed:** industrial/tech cinematic instrumental. Under speech it is ducked 8–10 dB (sidechain).
3. **SFX on every VFX event:**
   - **Hologram scan-in:** a short airy shimmer (≤ 0.45 s), ending on the reveal.
   - **Row lighting:** rising pings, one per row group, panned across.
   - **Wave and counter:** a clink cascade that follows the wave left → right.
   - **Skin → frame:** a glassy ring, then a low thump when the frame is revealed.
   - **Hot frame / sparks:** a short sizzle, then a low thump when the metal reaches the objects.
   - **Section drawing:** one tick.
   - **The dive:** the film's only whoosh (0.5 s), a sub under it, soft thups for the wall marks.
   - **Big figure:** a sub boom (45–55 Hz, 1.8 s) on its onset.
   - **Grow from the floor:** a low thump and a shimmer; very soft taps for each copy that drops.
   - **Screen assemble:** a shimmer; the cursor click is a tick.
   - **End card:** a metal ring sting with a short sub.

## Aligning the music

- Generated music does not follow timestamps in a prompt. **Generate 2 variants, measure** the energy curve (RMS and < 150 Hz per 0.5 s), find the strongest impact, and shift the track so that impact lands on the big figure's onset.
- **Stop:** cut the music hard (40 ms fade) before the question or the turn. Leave speech alone for 0.8–1 s, then bring back a quiet tail of the same track (−5 dB, 0.35 s fade-in) as the outro.

## Rules

- Never two accents closer than 0.15 s except cascades. Cascades stay ≥ 6 dB below single accents.
- No SFX during the silent stop.
- Only one whoosh per film, under the dive.

## Levels and checks

- Master to the delivery loudness (default −14 LUFS; a house target such as −10 LUFS needs gain plus a limiter, iterated). True peak ≤ −1 dBTP **measured on the final AAC file**.
- Check that the low band (< 80 Hz) drops by ≥ 10 dB in the stop against the second before it, and that the low-band peak sits within ±0.2 s of the big figure.
- Speech stays intelligible in mono and on a phone speaker.

## Licences

Use only music and SFX the user may publish. Generator outputs follow that platform's terms; check them and record them in the README. Synthesised SFX are always safe.
