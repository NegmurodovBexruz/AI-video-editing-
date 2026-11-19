# Captions: the stack

**Units.** px are for a 1080×1920 frame (scale by width / 1080); vertical positions are shares of `H`, widths of `W`; `FW` = face width in the current frame. Frames at 30 fps.

## The stack

Every phrase (a breath group, 2–9 words) is one stack:

| Part | What | Size | Position | Type |
|---|---|---|---|---|
| **Lead line** | the small words *before* the key word ("When", "We", "for", "this") | 0.8 × small size; function words smaller | directly over the key word, 0.012 H gap | sans semibold, grey → white |
| **Key word** | one word (or a figure with its unit) that carries the phrase | cap height 0.06–0.08 H, width ≤ 0.86 W (shrink to fit) | centred; see *Placement* | heavy grotesk (ExtraBold/Black), natural case, white, soft dark shadow |
| **Lines** | the words *after* the key word, 1–3 centred lines | 0.022–0.026 H; function words ≈ 0.45–0.6 × and dimmer | under the chin, line pitch 0.034 H | sans semibold, grey → white |

- Key words keep the speaker's case: sentence case, names capitalised. No all-caps shouting.
- Function words inside the lines ("and", "with", "we", "is" and the language's equivalents) are small and dimmer. Content words are full size.
- One key word on screen at a time. The stack clears 2 frames before the next stack's first word, or 0.6 s after its last word when the pause is longer than 1 s. Clearing is a 5 f fade.

## Choosing the key word (topic-agnostic, in this order)

1. A figure with its unit ("3 tonnes", "12 cities", "40 %").
2. The name of the thing the phrase is about (a product, place, object).
3. The verb or claim word that carries the sentence ("connected", "longer", "imagine").

Never pronouns, articles or fillers. Merge spoken number words into digits ("twenty by forty" → `20×40`) and list every such change in the README.

## Placement (on the real shots)

- **Long key words** (≥ 0.55 W and no digits) sit **behind the person**: draw them under the person matte, baseline about 0.01 H + cap/2 below the head top. The head covers a few letters in the middle; the word stays readable from its ends.
- **Figures and short key words** sit **fully above the head**: baseline 0.012 H above the head top. A covered digit is a wrong number.
- Never above 0.08 H (top bar) for the key's top.
- **Lines** start 0.05 H under the chin (chin ≈ face centre + 0.68 FW), never over the face or mouth. The last line's baseline stays above `H − 300 px`; nothing right of `W − 140 px`.
- Compute the layout once per stack from the head at the stack's first frame; the stack is screen-fixed afterwards (no head lock).

## Over CGI, product screens and bright frames

- On the interlude and full-screen product beats there is no person: key at 0.20 H + cap/2, lines 0.055 H under it.
- **Bright background check:** if the mean luminance under the key word is > 0.70 (white tunnel end, white site), draw the key and lines in the brand dark colour without shadow. White on white is lost.
- Full-screen product screens may carry a lower caption (0.75–0.85 H) mixing a sans line and an italic serif line. Use it for the sentence that describes the product.

## Timing and animation

- Every word appears on its **audible onset**, first visible frame 0–1 f after it. ASR word starts drift; snap them to the audio envelope or use a forced aligner.
- **Key word:** letters reveal left → right with a soft edge. The whole word is in after 7–8 f, with blur 6 → 0 px over the same time.
- **Small words:** opacity 0 → 1 in 3–4 f, grey (55 %) → white over 4 f, blur 2 → 0.
- A counting key word (a figure that grows) counts with the device that shows it (`devices.md` → *Wave and counter*) and lands exactly on the spoken figure.

## Corrections

Confirm names and figures at gate 1. Keep the speaker's wording. Spelling fixes and digit merges are allowed; list every changed word in the README. When two transcripts disagree on a phrase you cannot verify by ear, keep the one the user approved before and say so.
