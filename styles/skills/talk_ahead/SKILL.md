---
name: talk_ahead
description: Edit a raw talking-head video in the "Talk Ahead" style — a speaker explains, and every number, named object, comparison, place or question in the speech becomes an on-screen visual (big words behind the speaker, rolling counters, AI-generated inserts, real-map journeys, brand-motif transitions, full word-timed captions, material-based sound). Use when the user types /talk_ahead, asks for "talk ahead style", or gives a raw talking-head / presenter / expert / founder clip (any topic, any language) and wants it edited into a premium vertical explainer (Reels, Shorts, TikTok) — optionally with a brandbook, logo or reference video.
---

# Talk Ahead

**One line:** the speaker talks; the screen proves it. Each fact gets a visual at the exact word it is said, in the brand's own geometry, and the speech is never retimed.

The style is topic-agnostic. Its rules talk about *numbers, objects, comparisons, places, questions* — never about any industry. Do not carry imagery, words or colours from the worked example (`references/example-spc.md`) into a new video; carry only the decisions.

This skill is the style. The agent's own tools do the work: video I/O (ffmpeg), a person matte, an image/video generator (e.g. Higgsfield MCP), optional sound/music generators, speech-to-text. If one is missing, say what that costs the edit and offer the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The edit's clock. Probe it first (fps, size, rotation, audio). |
| Brand kit (brandbook PDF, logo, fonts) | no | Palette HEX, fonts, logo, **one geometric motif**. Without it, build a neutral kit (see `references/brand-motif.md`). |
| Reference video | no | Pacing and energy only. Never copy its layout, words or effects one-to-one. |
| Facts / script | no | Ground truth for numbers. Without it, check the speech's numbers yourself. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Full-speech captions unless the user says otherwise.

## Workflow

Do the phases in order. Stop for the user at the two gates (marked **GATE**). Never spend credits before gate 1.

1. **Intake.** Probe the file, hash it, contact-sheet it (1 frame / 2 s). Detect cuts (`select=gt(scene,0.25)`). Get word-level timings. Compute the person matte once for the whole clip. Extract the brand kit. Read `references/qa.md` → *Traps* before decoding anything.
2. **Fact check.** Recompute every number the speaker says (unit weights, lengths, ratios, sums). Check word gaps: a missing word needs ≥ 0.2 s of silence. If the speech contradicts physics or itself, flag it with the arithmetic and let the user decide what the screen says. Write the decision down.
3. **Beat map.** Split the speech into beats and map each one to a visual device with `references/beat-map.md`. Produce the plan table: time · speech · device · source (footage / generated / graphic / map) · cost. Add a credit estimate from the generator's cost preflight.
4. **GATE 1 — plan approval.** Show the plan, the budget and the open fact questions. Wait.
5. **Generate inserts.** Stills first (2 variants each, 9:16), review them as a sheet, pick, then image-to-video (5 s, silent). Log every job id in a ledger *before* waiting. See `references/qa.md` → *Generation*.
6. **Compose.** Frame-accurate compositor: output time = source time; inserts, cards and maps only change what is shown. Layer order per frame: footage (graded, cropped) → words behind the speaker (occluded by the matte) → scene devices → front labels → end card → captions → hit shake. Specs in `references/motion.md` and `references/typography.md`.
7. **QA every beat.** Render short ranges and look at frames before rendering the whole film. Run the checklist in `references/qa.md`. Fix, re-render the range, look again.
8. **Sound.** Speech + material SFX family + music shaped to the beats, ducked under the voice, mastered. `references/sound.md`.
9. **GATE 2 — delivery.** Hand over the file, a README (sources, ledger, credits spent, rebuild commands) and the open issues, stated plainly.

## Style DNA (the decisions that make it "Talk Ahead")

- **Hook in the first second:** the opening noun in huge type *behind* the speaker, letters rising through a baseline mask, the brand motif inside a letter.
- **Every fact gets a device, at its word.** Numbers count or slam; named things the camera never saw become short AI inserts; comparisons become a scale visual (map, stacked silhouettes, bars that are brand shapes); places become a real map; the closing question gets a crash zoom.
- **One brand motif carries the film.** Derive one shape from the logo and reuse it as letterforms, transition wipes, grids and pins. No second motif.
- **Brand colours only.** Dark brand colour for cards and full-screen motion, one accent for emphasis (active caption word, the "extra" in a comparison), light neutral for type. Never invent a palette.
- **Speech untouched.** No retiming, no re-voicing. Pauses are covered by devices or kept as breathing room; offer jump-cutting dead pauses as an option, don't do it silently.
- **Breathing shots.** After every dense device, leave at least one 1.5–2.5 s stretch of plain speaker with captions only.
- **Ending over live footage.** Logo and slogan rise over the moving final shot; never freeze or clone the last frame.
- **Sound is material, not air.** No whoosh / swish / swoosh. Hits, rings, ticks and sub drops made of the brand's material world; music sections follow the beats.

## Where the details are

| File | Read it when |
|---|---|
| `references/beat-map.md` | Mapping speech to devices (phase 3) |
| `references/motion.md` | Building any device; exact durations, easings, sizes |
| `references/typography.md` | Placing text, behind-speaker words, captions, safe zones |
| `references/brand-motif.md` | Extracting palette/fonts/logo/motif, or building a neutral kit |
| `references/sound.md` | Sound design, music brief, mix and loudness |
| `references/qa.md` | Before decoding (traps), before generating (credits, licences), after every render (checklist) |
| `references/example-spc.md` | A complete worked example, beat by beat, with frames in `references/examples/` |
