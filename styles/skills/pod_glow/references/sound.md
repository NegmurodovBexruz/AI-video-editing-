# Sound

## Layers

1. **Speech** — untouched timing. Clean with a light de-noise/de-ess if needed; match levels of the two mics.
2. **Music bed** — instrumental, warm, modern (lo-fi-pop / chill-hop / soft future-bass), **~110–125 BPM**, steady kick and soft hats, no vocals. Runs the whole clip; ducked 12–15 dB under speech; may breathe up between sentences.
3. **Transition hits** — a short low hit / sub thump (60–120 Hz body, 150–300 ms) on every white flash, the capsule move and each full-screen card entry.
4. **UI pops** — soft pops/clicks/blips on icons, emoji, tag pills and avatar rows (−8…−12 dB below the hits). Typewriter: very soft ticks, every 2nd character.
5. **Light leak** — a soft reversed swell (0.4–0.6 s) into the leak, optional.

## Rules

- Every visible event that *appears* has a sound at its frame; captions do not (too many).
- Pull the music back (−3 dB, 0.3 s) just before the strongest key phrase of the clip.
- Avoid heavy whooshes; a very short airy swipe under the capsule move is the only exception and must stay below the hit.
- Music ends with the clip on a phrase boundary or a short tail; never a fade that outlasts the picture.

## Levels

- Speech ≈ −16 LUFS short-term, music −28…−31 LUFS under speech, hits peak ~2 dB above the bed.
- Master −14 LUFS integrated, true peak ≤ −1 dBTP. Measure (`ebur128=peak=true`) and report the numbers.

## Licences

- Use only music/SFX the user may publish. Generator outputs on a free tier usually carry no commercial licence. Check the tier first (HTTP 402 / "paid plan required" is the tell).
- Synthesised SFX are always safe. Never download copyrighted tracks.
