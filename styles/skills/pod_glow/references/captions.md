# Captions: the two-tier key-phrase system

Captions are the core of Pod Glow. Every spoken line is captioned; the *shape* of each chunk carries the emphasis.

**Units.** Sizes are given in px for a 1080×1920 frame. For any other frame multiply px by `frame width / 1080`; vertical positions are given as a share of the frame height and stay the same. Times are in frames at 30 fps (1 f ≈ 33 ms); at 25/60 fps keep the same durations in seconds.

## Anatomy of a chunk

```
             the hardest part        ← lead-in: small, white, wide heavy italic, sentence case
        WAS STARTING OVER            ← key phrase: big, ACCENT, wide heavy italic, ALL CAPS
```

- A **chunk** = 2–7 words, one breath. It has a **lead-in** (0–5 small words) and a **key phrase** (1–4 words, ≤ 18 characters per line, max 2 lines).
- Some chunks are lead-in only (filler and connective speech: "and also", "I think", "you know"). About **60–70 %** of chunks earn a key phrase.
- A key phrase may stand alone without a lead-in.

## Choosing the key phrase (topic-agnostic)

Pick, in this order, the words that carry the chunk's meaning:
1. The **claim / stake** ("the hardest part", "nobody tells you").
2. The **concept noun** a card is about ("trust", "community", "the process").
3. An **emotion or judgement** ("exhausting", "so rewarding").
4. A **quantity with its unit** ("two or three years" → key "TWO OR THREE", unit "YEARS" small under it).
5. The **question** of a question sentence ("WHERE DO YOU START").

Never pick fillers (like, so, um, you know), pronouns alone, or the speaker's name.

## Layout

| Element | Size (at 1080 wide) | Style | Position |
|---|---|---|---|
| Lead-in line | 46–54 px | **same wide heavy italic family as the key**, one weight lighter, sentence case; white with a faint vertical white → light-grey gradient; soft dark shadow | centred; ≈ 3.6 % of the height above the key line |
| Key phrase line 1 | 84–104 px (cap height 60–78 px) | heavy **wide** italic, ALL CAPS, accent gradient **per word**, **thin** dark outline + soft drop shadow | centre ≈ 61 % of the height |
| Key phrase line 2 | same | same | line pitch ≈ 0.9 × size |
| Unit / qualifier under a key | 36–44 px | white heavy italic caps | just under the key line |

- The block sits on the chest/mic, **≈ 55–63 % of the height**. Move it up (≈ 50–55 %) when hands or the mic fill that zone; never over the mouth or eyes. Check every chunk against its own frames — speakers gesture into this zone.
- Max key-line width ≈ 82 % of the frame width. Shrink the size, never the margins.
- Compute the **final** centred layout of each line first; every word appears in its final place. Lines never re-centre while words are being added.
- **Hand-set feel:** each word sits slightly off the shared baseline (±0.4–0.9 % of the width) and may be rotated −3° … +2°. Seed the offsets per word so a re-render is identical; neighbours never share the same offset.
- Keep clear of the platform UI: nothing meaningful in the bottom ≈ 15 % of the height or the right ≈ 13 % of the width (vertical platforms).

### Accent fill

- Gradient **inside each word**, diagonal: top-left light (accent light) → bottom-right saturated (accent deep). Neighbouring words read as separate shapes.
- Outline: thin (≈ 2 px at 1080 wide), dark tint of the accent at ~80 %. A thick outline (≥ 5 px) reads as a sticker and is wrong for this style.
- Drop shadow: offset ≈ 4 px down, blur 8–10 px, black 45–55 %. Optional soft outer glow in the accent colour (opacity ≤ 35 %).

## Timing — the rule that matters most

- **A word appears on its audible onset, never before it.** First visible frame = 0–3 f after the syllable onset in the audio.
- Only exception: in fast connected speech the last 1–2 words of a phrase may appear up to 0.2 s early, and only once the phrase is audibly under way.
- ASR word starts are **not** onsets; they are typically 0.1–0.3 s off in either direction. Place words on the audio onset (or a forced aligner); use ASR only to know *which* word.
- Before its onset a word is **completely absent** (opacity 0). Many tools hold the first keyframe's value *before* that keyframe: open every word's track with an explicit invisible key at its lifetime start.
- Lead-in words and key words follow the same per-word rule. A key phrase does not appear together with its lead-in; it builds word by word as the words are said.
- A chunk stays until the next chunk starts, or ≤ 0.5 s after its last word. It leaves with a **hard cut**; a 2–3 f empty gap before the next chunk is normal when the speaker pauses. Chunks never overlap.
- On a speaker switch the chunk ends at the cut.

## Word entry motion (per word)

| Frame after appearing | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|
| Y offset (share of key size) | −0.25 … −0.30 × size (above its place) | −0.07 … 0 | +0.03 … +0.05 (small overshoot) | 0 |
| Opacity | 35–50 % | 95–100 % | 100 % | 100 % |
| Blur | 4–6 px | 0–1 px | 0 | 0 |

- Words **drop in from above**, fast. They do **not** rise from below, slide sideways, or scale-pop.
- The **block never moves**: no scale or position animation on the chunk; only the entering word moves. Words already on screen stay still.
- Easing: ease-out over frames 1–2, a tiny settle on frame 3. Total ≈ 0.1 s.

## Attachments (sparingly)

- **Emoji** (3D-rendered image, not a font glyph): on an emotion word, ≈ 1.2 × key size, hugging the key phrase's right or left end; if there is no room on either side, above the phrase's right end. Appears **with its word** using the same drop-in, then a slight bob (±4 px, 1.2 s). At most one per ~8 s.
- **Icon badge**: a 0.5–0.65 × key size accent-ring circle with a simple white icon (calendar, clock, money, people, pin, check) at the end of the key phrase; appears with the word it belongs to.
- **Avatar row**: a rounded pill (accent outline, dark fill) with 2–4 round avatars under a key phrase that names a group of people. Generic silhouettes or images the user supplied — never real people's faces you were not given.
- **Hollow punctuation**: a giant outlined "???" or "!!!" (accent stroke, no fill, ≈ 3–3.5 × key size) behind the key phrase, appearing with the question or exclamation word.

## Corrections

Fix ASR spelling, keep the speaker's wording. List every changed word in the README. Proper names, jargon and slang the ASR is unsure about go to gate 1 as questions.
