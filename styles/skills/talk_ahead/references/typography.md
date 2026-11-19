# Typography and layout (1080×1920)

## Type roles

| Role | Font (from the brand kit) | Size | Weight | Colour |
|---|---|---|---|---|
| Hook / slam word | Display face | 200–330 px | medium (500) over footage; light only on flat dark cards | light neutral |
| Section title (place, object name) | Display face | 120 px, tracking 8–10 | 500 | light neutral |
| Label / unit | Display face | 44–64 px, tracking 4–18 | 500 | secondary light (e.g. mist) or accent |
| Map place names | Display face | 30 px | 400 | secondary light |
| Captions | Text face (variable, optical size max) | 58 px | 620 | light neutral |
| Data-source credit | Display face | 30 px | 400 | secondary light, bottom-right |

Thin display weights disappear over bright skies and busy footage; use 500 over footage and keep the brand's light weight for flat cards. Headlines: max 2 lines (brand rules may say 3 — still use 2 on vertical video).

## Safe zones

- Captions centred at **y = 1440**. Nothing else goes between y 1360 and 1520 while captions are on.
- Keep the bottom 280 px free of meaningful text (platform UI); only the data credit goes there.
- Behind-speaker words: y 300–820. Counters/plates over full-screen scenes: top plate y 130–500 or middle plate y 960–1370 — pick the one the scene's subject doesn't use.
- Side margins ≥ 40 px; a word that would touch both edges is too big — shrink it (e.g. "57 × 3 MM" at 160 px, not 210).

## Behind-speaker words

- Only on shots where the matte is clean (check one frame per shot).
- The visible parts must still read: the word must extend beyond the speaker on both sides.
- Light type with a soft shadow (blur = size/14, offset size/30, strength 0.6) over footage; on bright sky use the dark brand colour with no shadow.

## Captions

- Chunks of ≤ 22 characters; break at punctuation; never split a proper name ("New-York" stays together; join hyphenated names).
- The word being spoken gets an accent-coloured pill (92 % opacity, padding 14×8 px); other words have a strong shadow (0.9).
- Chunk enters 0.08 s before its first word, 10 px rise + 0.12 s fade; ends at the next chunk or 0.6 s after its last word.
- Fix spelling in captions (missing letters, apostrophes → ‘ ’), and apply the user's fact decisions — but list every changed word in the README.

## Labels on images

- Labels live in empty background (sky, margins, dark backdrop), never on the subject's body.
- Connect a label to its part with a 2 px leader that draws in 0.3 s and ends in a 7 px dot.
- Accent colour on a similarly coloured subject vanishes — check the frame and switch to light neutral.
