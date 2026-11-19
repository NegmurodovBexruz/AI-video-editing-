# Type: layers, sizes, positions, timing, head lock

**Units.** px are for a 1080×1920 frame; for other frames multiply by `width / 1080`. Vertical positions are shares of the frame height `H`; widths are shares of the frame width `W`; `FW` = the speaker's face width in the current frame. Times in frames (f) at 30 fps.

## Phrase compositions

- Split the speech into phrases of 2–8 words (a breath group or clause). Each phrase gets **one key word** and one **layer** for it; the other words are small.
- The composition builds word by word on the onsets and **clears at the phrase end** (all its parts exit together, or the small words go first and the key word last).
- Show (almost) every spoken word somewhere in the composition. Drop pure fillers ("um", "well") and stammers; list removed words in the README.
- Never more than one key word on screen.

### Choosing the key word (topic-agnostic, in this order)

1. A figure (number, percentage, amount, count).
2. The word that carries the claim or the contrast ("free", "never", "everyone", "anywhere", "affordable").
3. A name of a place, organisation or thing the phrase is about.
4. The verb that decides the sentence.

Not pronouns, articles or fillers. When nothing stands out, the phrase has no key word: small words only.

## The layers

| Layer | What | Size | Position | Font |
|---|---|---|---|---|
| **Back word** | huge key word **behind the head and shoulders** (person matte over it) | width 0.80–0.95 W, cap height 0.09–0.14 H | vertical centre at the head's upper half or just above it | heavy condensed grotesk, ALL CAPS |
| **Front word** | huge key word **in front**, across the chest or waist | width 0.75–0.92 W | 0.52–0.66 H | heavy condensed grotesk, ALL CAPS |
| **Chest word** | big key word or figure in front, smaller than a front word | cap height 0.045–0.07 H | 0.55–0.65 H, centred on the body | bold sans, sentence case as spoken |
| **Figure** | percentages, prices, big numbers when said as the punch of the phrase | cap height 0.06–0.08 H | above the head or at the chest | thin serif italic |
| **Cluster** | the other words of the phrase, 1–4 short lines, **head-locked** | cap height 0.018–0.026 H | beside the head: horizontal offset 0.7–1.3 FW from the face centre, top line near eye level; on the side with more free space | regular sans, lower case as spoken |
| **Sub-line** | 1–4 small words under a chest/front/back word, completing it | cap height 0.016–0.022 H | directly under the key word, left-aligned or centred to it | regular sans in the **accent colour** |
| **Script word** | one emotional or evaluative word written by hand on the body, furniture or empty space | height 0.05–0.08 H | on a calm surface, never on the face | handwriting script, white |

- Back words and front words: **one per 5–8 s of speech**; chest words and figures fill the rest; small-only phrases are fine.
- Back word only when the background behind the head is plain enough to read the letters around it; otherwise use a front word.
- A back word may be **white** (solid) or **grey and semi-transparent** (40–60 % — it reads as part of the wall). Use the grey version when the word is a label rather than the punch.
- Clusters and sub-lines never cover the face, the mouth or the eyes; keep ≥ 0.15 FW from the face edge.
- Everything inside the platform safe zone; check with the platform overlay before delivery.

## Head lock (clusters, sub-lines under a chest word, chest words near the head)

- Track the head every frame (face centre; or head-top + face centre when the face turns). Smooth only to remove detector jitter (≤ 2 px noise), **never with a lag**.
- The text keeps its offset from the head: text position = head position + offset fixed at the composition's first frame. Gain 1.0–1.2 (1.0 = locked to the face centre; up to 1.2 when anchored to the upper body so it does not drift against the shoulders).
- Lag 0 frames. No spring, no delayed follow — the text must look printed in the room next to the person.
- Locked text scales with the footage: when the frame zooms, the offset and the size scale with it.
- **Big words are not head-locked.** Back words, front words and figures stay fixed on the screen (the zoom moves the person behind/under them). Their only motion is their own entry/exit animation.

## Timing

- Every word (any layer) appears **on its audible onset — first visible frame 0–3 f after it, never before**. ASR word starts drift 0.1–0.3 s; place words on the audio envelope or a forced aligner.
- A blurred entry starts on the onset and becomes sharp during the entry; it does not start early.
- Exception: a back word that slides in from behind the head may start its motion up to 4 f before its onset so that it is readable on the onset — it must still be hidden behind the person (fully matted) before the onset.
- Before its onset a word is absent; open every word's track with an explicit invisible key.
- A composition holds until the next phrase starts; if the pause is longer than 0.8 s, clear it 4–6 f into the pause.

## Corrections

Confirm spellings at gate 1. Keep the speaker's wording; list every changed word in the README.
