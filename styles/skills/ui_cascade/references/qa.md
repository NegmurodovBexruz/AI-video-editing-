# QA, traps and fallbacks

## Traps

- **ASR word starts are not onsets.** Detect the audio onset of each word. Cascades that start late look sluggish; more than 0.15 s early looks like a teleprompter.
- **Two accent words in one phrase** kill the hierarchy. Exactly one.
- **Over-stacking.** More than 5 lines or more than ~10 words in one stack becomes a wall. Split the phrase.
- **Stacks over the face.** The stack may cover the chest and shoulders, never the eyes or mouth. Check every stack against the face box on its first and last frame.
- **Stutter without a set-up change.** The negative stutter belongs to camera set-up cuts. Use the bloom glitch inside a set-up, at most twice.
- **App scenes that transcribe.** The scene acts the idea out; it is not a caption board. Keep 3–5 short items or bubbles.
- **Fake real-world UI.** Do not copy a real app's logo, icon set or exact layout. Use the generic look in `look.md`.
- **Fake proof.** Counters and numbers on cards come from the speech or the user's data. Otherwise use neutral placeholders and say so.
- **Third-party marks.** Logos on icon tiles only with the user's permission; otherwise use pictograms.
- **Glyph gaps.** Brackets, quotes and the language's letters must exist in the font; check before rendering.
- **Platform UI.** Keep stacks out of the bottom 0.18 H and the right 0.12 W where the app buttons sit, except full-screen app scenes, which are short.

## Generation rules (when artwork or thumbnails are generated)

- Icon artwork: a black or flat background, a single object or pictogram, no text; 2 variants, pick one.
- Card thumbnails: neutral, clearly illustrative, and labelled as AI-made in the README.
- Never generate a real person's likeness or a real brand's product unless the user supplies it.

## Checklist (every render)

- [ ] Every spoken word appears in a stack, except during app scenes; spelling is checked against the script or corrections.
- [ ] Every word starts within −0.15…+0.05 s of its onset; the letter stagger is 2 frames.
- [ ] One accent word per stack; connectors at 50 %; asides in brackets.
- [ ] Figures sit on a bar; units are in the tag; the numbers match the speech.
- [ ] Icon tiles land on their words and do not cover the face.
- [ ] The card fan's counters are truthful or marked as placeholders.
- [ ] App scenes: generic UI, short text, entry and exit as specified.
- [ ] Every set-up cut has a 5–7 frame stutter; at most 2 bloom glitches.
- [ ] The speaker is on screen ≥ 60 % of the time; the last 2 s are live, not frozen.
- [ ] Sound: bed under speech, SFX per device, −14 LUFS / ≤ −1 dBTP.
- [ ] Safe areas for the target platform.

## Fallbacks

| Missing | Do instead |
|---|---|
| Person matte | Put the aside under the headline in front of the head and shift it so it does not cover the face. |
| Logos / permission | White pictograms on the tiles. |
| The speaker's content for cards | Neutral placeholder thumbnails (gradient + simple shape), labelled. |
| Image generator | Draw pictograms and UI as vector shapes in the compositor. |
| Music | A simple generated pulse bed, or no bed with SFX only; say so. |
| No set-up changes in the raw | No stutters; use at most 2 bloom glitches on punch words. |
