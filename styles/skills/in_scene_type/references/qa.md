# QA, traps and fallbacks

## Traps (read before building)

- **Source fps:** convert to the delivery fps before building; a 23.976 or 29.97 source drifts against a 30 fps timeline if interpreted wrongly.
- **Frame counts:** read until EOF.
- **ASR timing:** word starts drift 0.1–0.3 s from the audible onset. Place each word on the audio onset (10 ms envelope, ≥ 6 dB rise within 30 ms) or a forced aligner. In fast connected speech envelope onsets are sparse — use a forced aligner, or align key words by hand on the waveform.
- **Keyframe hold before the first key:** open every word's track with an explicit invisible key, or the word shows before its onset.
- **Matte edges:** hair and fast hands flicker. Check the matte on a sheet before planning back words; drop back words in stretches where it fails.
- **Head tracker:** face detectors jump between false faces (patterns, posters, hands). Reject jumps larger than 0.06 W per frame, interpolate short gaps, smooth only noise. A lagging smoother breaks the head lock.
- **Zoom vs tracking:** apply the zoom curve to the footage **before** computing head positions for locked text, or compute both in the same transform.
- **Digital zoom softness:** know the source resolution; don't plan punches beyond the sharp limit (`camera.md`).
- **Fonts:** check language glyphs in every role (condensed caps fonts often miss letters).
- **Memory:** stream video; one heavy job (matte, tracking, render) at a time.

## Media and permissions

- Logos of organisations: only with the user's permission; record it in the README.
- Cellophane overlay: stock the user may publish, or generated; record the source.
- No faces of real, identifiable people other than the speaker unless supplied.

## Generation (cellophane overlay, if generated)

- Preflight the cost, quote it at gate 1, ledger every job id before waiting; never resubmit after a timeout before resolving the original job.
- Prompt for crumpled clear plastic film moving across a pure black background, bright speculars, no objects, no text. Two variants, pick from a sheet; check it reads in 4–7 frames.
- If a safety filter refuses a prompt, don't rephrase around it — use the glow-silhouette flash instead and tell the user.

## Checklist after every range render

- [ ] **Word sync, every word:** first visible frame 0–3 f after its audio onset (a sliding back word may start moving ≤ 4 f early but stays hidden behind the person until the onset); list any early word.
- [ ] One key word per composition; compositions clear at phrase ends.
- [ ] Back words: matte clean on every frame, the word still readable around the head.
- [ ] **Head lock:** on three clusters, step frame by frame through a head movement — the text keeps its offset in the same frame (no lag, no float); it never covers the face.
- [ ] Big words are screen-fixed (they do not drift with the head).
- [ ] Camera: each punch lands on its word; holds are still; total digital scale within the sharp limit; final set-up calm.
- [ ] Gesture spawns appear at the hand on the onset and stay put.
- [ ] Transitions only at set-up changes; the cut is hidden under the densest frame.
- [ ] Everything inside the platform safe zone.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP after the final encode.
- [ ] README lists caption corrections, media sources, permissions, credits.

## Fallbacks when something is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Person matte | No back words; use front words; no glow-silhouette flash | "no text behind the head" |
| Head tracker | Clusters screen-fixed beside the head's average position, placed with extra margin | "small words don't follow the head" |
| Source at delivery resolution only | Punches ≤ +10 %, reveals by starting zoomed in | softer punches |
| Cellophane overlay | Glow-silhouette flash, or hard cuts | — |
| Font with the language's letters | Nearest font with full coverage in the same role | which font |
| Music | Speech only | — |
| Speech-to-text | Ask for the transcript; align by hand | "timings ±0.1 s" |
