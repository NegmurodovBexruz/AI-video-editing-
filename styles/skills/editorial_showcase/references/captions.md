# Type and caption roles

Read the selected kit in `look.md`. Numbers below are starting values for portrait video; measure the rendered bounds and adapt to other aspect ratios.

## Three roles, one vocabulary

| Role | Starting layout | Behaviour |
|---|---|---|
| Editorial heading | 1–2 short lines, about 0.06–0.10 W cap height, within 0.80 W | Announces the concept at its spoken onset. Keep it away from the face. |
| Expressive accent | One short word/phrase, about 0.7–1.0 of heading size | Italic or handwriting in the single accent colour. It may overlap a heading's empty space, not obscure its letters. |
| Supporting caption | Usually 2–6 words and at most 2 lines, cap height about 0.035–0.05 W | Covers the rest of the speech in a stable reading zone. Split long phrases instead of shrinking to fine print. |

A word belongs to a role, not to several identical overlays at once. When a headline or message carries spoken words, count that towards caption coverage. If a message paraphrases the speech, keep the actual speech in supporting captions or revise the message to match. SRT remains complete regardless of visual role.

## Timing

- Review ASR text, especially names and non-English words. Use reliable alignment or reviewed audible onsets; snapping every word to a nearby energy peak is not proof of correct alignment.
- In word-reveal mode, start the visible word at the first output frame on/after its verified onset; aim for no more than 2 frames of delay at 30 fps.
- In phrase mode, show a short chunk at the first word's onset and report it as chunk timing, not per-word sync. Do not reveal a long future sentence before it is spoken.
- Reserve the final block width before revealing words so earlier words do not recenter or jump.
- Give completed phrases enough reading time, normally at least 0.35 s when the speech allows it. Split or simplify emphasis when the sentence is too fast; never change the speaker's claim to solve a timing problem.
- Subtitles should not outlive their thought or linger across unrelated source cuts. Exceptions, such as one continuous phrase across B-roll, should be intentional.

## Phrase change

Default: incoming phrase rises from about 0.012–0.025 H below its final position and sharpens over 4–6 frames. The outgoing phrase moves down slightly and fades over 3–5 frames. Limit simultaneous readable old/new text to 2 frames. Blur is a transient motion cue, not persistent glow. Use a plain fade or cut when there is insufficient reading time.

On a definition card, build the phrase by meaning and hold the final layout. Do not let scale animation push long words beyond the safe area. On paper, highlight one term at a time on a neutral strip; keep the term sharper than the background document.

## Contrast

Check the worst bright and dark frames of the whole beat. Use a restrained neutral shadow/scrim or move to a solid card if required. Use approximately 4.5:1 contrast as a starting check for small text; then inspect the reduced phone-size frame. Prevent heading/handwriting collisions, edge clipping and UI overlap after all camera transforms.
