# QA, traps and fallbacks

## Traps (read before decoding)

- **Source fps:** decode with `fps=30` before scaling; a 29.97 source drifts against a 30 fps timeline if interpreted wrongly.
- **Frame counts:** read until EOF.
- **ASR timing:** word starts drift 0.1–0.3 s from the audible onset; one-word captions make every error visible. Place each word on the audio onset (10 ms envelope, ≥ 6 dB rise within 30 ms) or a forced aligner. In fast connected speech envelope onsets are sparse — then align with a forced aligner, or by hand on the waveform for spotlight words at least.
- **Keyframe hold before the first key:** open every word's track with an explicit invisible key.
- **Fonts:** script fonts often lack non-English glyphs; check before planning script accents.
- **Memory:** stream video; one heavy job at a time.

## Media and permissions

- Work B-roll: the speaker's/user's own media, with permission recorded in the README.
- Places: the user's photos or clearly illustrative drawings; never present a generated image as a real photo of a real place.
- Third-party logos: only with permission.

## Generation (illustrations, illustrative stills)

- Preflight the cost, quote it at gate 1, ledger every job id before waiting; never resubmit after a timeout before resolving the original job.
- Metaphor and landmark illustrations: monochrome, clean, on a dark or transparent background; stills first (2 variants), pick from a sheet.
- No faces of real, identifiable people unless supplied.
- If a safety filter refuses a prompt, don't rephrase around it — use a simpler drawn shape and tell the user.

## Checklist after every range render

- [ ] **Word sync, every word:** first visible frame 0–3 f after its audio onset (spotlights in a stack swap may *start* ≤ 6 f early and settle on the onset); list any early word.
- [ ] Only one body word on screen at a time; spotlights stack their lead words correctly.
- [ ] Spotlights are the meaningful words (names, roles, brands, places, decisive verbs); about one per 1.5–3 s.
- [ ] Spotlight ≤ 85 % of the width; glow not blooming over the face.
- [ ] Script accents written on, legible, ≤ 1 per sentence.
- [ ] Split layout: presenter's face fully inside the window; illustration readable; labels at the right ends of the metaphor.
- [ ] Place type: two tones match the photo/brand; letters inside the frame; photo status (real/illustrative) recorded.
- [ ] Tile transitions only between pieces of work; no one-frame flash of the wrong image.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP after the final encode.
- [ ] README lists caption corrections, media sources and permissions, credits.

## Fallbacks when something is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Work media | Illustrative stills, or skip the work run and use spotlights only | which shots are illustrative |
| Place photos | Landmark illustration on the dark panel | — |
| Person matte | Pattern rise in front at the frame bottom; no letters behind subjects | — |
| Script font for the language | No script accents | — |
| Music | Speech only (the style works without a bed) | — |
| Speech-to-text | Ask for the transcript; align by hand | "timings ±0.1 s" |
