# Captions: editorial white type

**Units.** px are for a 1080×1920 frame; for other frames multiply by `width / 1080`. Vertical positions are shares of the frame height. Times in frames at 30 fps (1 f ≈ 33 ms).

## Chunks

- A **chunk** = one breath, 2–6 words, 1–2 lines. It replaces the previous chunk with a **hard cut** (0–1 empty frame between them). Chunks never overlap.
- Break at punctuation and at pauses ≥ 0.25 s; never split a product or proper name.
- A single strong word may be its own chunk (a closing word, a named item).

## Size hierarchy (the signature)

| Word class | Size (at 1080 wide) | Weight |
|---|---|---|
| Content words (nouns, verbs, adjectives carrying meaning, names, numbers) | 100–115 px | SemiBold–Bold |
| Function words (articles, auxiliaries, pronouns, short prepositions/conjunctions: a, the, of, to, been, is, such, we, it's…) | ≈ 0.6 × content size (60–70 px) | Medium–SemiBold |
| One emphasis word per 2–3 chunks (the claim, the name) | 1.1–1.2 × content size | Bold |

- Mixed sizes share one baseline per line.
- **Tight tracking:** −3 % to −5 % (letters nearly touching). Word gap ≈ 0.15–0.2 em — smaller than normal, so a small word visually attaches to its big neighbour.
- Sentence case, natural punctuation kept (commas, full stops).

## Layout

- The block is **centred by its final width**; lines inside it are **left-aligned**. Words are added left to right in their final positions — the block never re-centres or moves while it builds.
- Block centre ≈ 63–66 % of the height (on the chest, below the mic line). Line pitch ≈ 1.15 × content size. Max line width ≈ 82 % of the frame width.
- Same position on the speaker, on the brand stage and over B-roll. Never over the face.
- Keep clear of platform UI: nothing meaningful in the bottom ≈ 15 % or right ≈ 13 %.

## Style

- Fill pure white. Soft white outer glow (blur ≈ 6–8 px, 20–30 %) plus a faint dark shadow (blur 10 px, 25 %) only where the background is bright. No outlines, no boxes, no colour.
- Font: a neutral grotesk display face (see `look.md`), never condensed, never italic.

## Timing and reveal

- **A word appears on its audible onset — first visible frame 1–5 frames after the onset, never before.** ASR word starts are not onsets (they drift 0.1–0.3 s either way); place words on the audio envelope or a forced aligner.
- Before its onset a word is absent (opacity 0); many tools hold the first keyframe value before that key — always open each word's track with an explicit invisible key.

| Frame after appearing | 1 | 2 | 3 | 4+ |
|---|---|---|---|---|
| Opacity | 35–45 % | 60–70 % | 85–95 % | 100 % |
| Colour | mid grey (white at reduced opacity) | → | → | white |
| Blur | 4–6 px | 2–3 px | 0–1 px | 0 |
| Position / scale | unchanged | unchanged | unchanged | unchanged |

- Words do not move, scale or slide. The reveal is a soft "focus-in" in place.
- A chunk holds until the next chunk starts or ≤ 0.4 s after its last word.

## UI-tag caption (variant, sparingly)

For a spoken list of actions or attributes ("test, tweak, ship…") the chunk can switch to a **UI tag line**: small type (≈ 0.35 × content size) inside a thin outlined box in the stage colour, symbols joining the items (`&`, `#`, `/`, `+`).
- The box draws first (lines extend in 6–10 f), then the items type in word by word on their onsets.
- Placed where the normal caption sits; replaces it for that chunk. At most one per ~30 s.

## Corrections

Product and brand names are the most mis-heard words: confirm spellings at gate 1 and use the official casing. Keep the speaker's wording otherwise; list every changed word in the README.
