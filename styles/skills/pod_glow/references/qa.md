# QA, traps and fallbacks

## Traps (read before decoding)

- **Source fps:** decode with `fps=30` before scaling; a 29.97 source drifts against a 30 fps timeline if it is interpreted wrongly — either build the timeline at the source rate or conform everything to 30.
- **Frame counts:** read until EOF; never assume duration × fps.
- **Multicam podcasts:** the source may already contain cuts. Detect them first; a white flash is added only where the *speaker* changes, not on every existing cut.
- **ASR timing:** ASR word starts are 0.1–0.3 s off the audible onset (both directions), and first words after a pause are often stamped 0.3 s early. Place caption words on the **audio onset** (10 ms envelope, band 150–4000 Hz, a ≥ 6 dB rise within 30 ms), or with a forced aligner; use ASR only for the word identity. Check the hook's first onset with `silencedetect` (highpass 120 Hz, −38 dB, 0.35 s).
- **Keyframe hold before the first key:** many tools show a track's *first* keyframe value before that keyframe's time. A word whose first key is "visible at 2.1 s" is visible from its layer start, i.e. before it is spoken. Always open every word's track with an explicit invisible key at its lifetime start, and verify with the word-sync check below.
- **Analysing a supplied reference video:** never derive motion rules from frames sampled every 0.5 s. Word entries last 2–3 frames; inspect the reference frame by frame (1/30 s, full-resolution crops) for each animated element type, and compare caption frames with the audio envelope, before deciding pacing.
- **Captions over hands/mic:** podcast guests gesture into the caption zone; check every chunk's frames, move the block up when hands cover it.
- **Memory:** stream video; one heavy job at a time. A motion-graphics app, a browser and a compositor running together can exhaust RAM — close previews and render serially.
- **Text files:** UTF-8 without BOM.

## Generation (photo inserts, icons)

- Preflight cost, quote at gate 1, ledger every job id before waiting; never resubmit after a timeout before resolving the original job.
- Stills first (2 variants), pick from a sheet. Prompt the warm grade and "no text, no logos, no watermark".
- No faces of real, identifiable people unless the user supplied the photos; use generic people or silhouettes.
- If the safety filter refuses a prompt, don't rephrase around it — switch the beat to an icon/diagram card and tell the user.

## Checklist after every range render

Extract frames at each device's entry, hold and exit; look at them.

- [ ] Picture and speech in sync (hard consonant at a cut).
- [ ] **Word sync, every word, not a sample:** for each caption word, its first visible frame is 0–3 frames after its audio onset — never before. Measure it (render the caption layer alone or diff consecutive frames in the caption zone, compare with the onset list) and list any word that is early.
- [ ] Words drop in from above in 2–3 frames (see `captions.md`); the caption block itself never scales or slides; nothing rises from below.
- [ ] The key phrase is the meaningful one.
- [ ] Captions readable on the actual background; no caption over eyes/mouth; none in the bottom 280 px.
- [ ] Key-line width ≤ 82 % of the frame; no word touches an edge.
- [ ] Only one accent hue on screen; glow not clipping into a blob.
- [ ] Speaker switches have the white flash; same-speaker re-frames don't.
- [ ] No two full-screen cards back to back; ≥ 2 s breathing after each card.
- [ ] Icons/tags never over the face; names on tags are supplied, not invented.
- [ ] Transitions: no one-frame flash of the wrong shot at a card's start/end.
- [ ] Ending on live footage, no frozen frame.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP; music doesn't mask speech.
- [ ] README lists caption corrections, sources, licences, credits spent.

## Fallbacks when a tool is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Motion-graphics tool with 3D layers | Frame compositor (Python/ffmpeg) or any 2.5D editor; same specs | "3D tiles become 2.5D" |
| Person matte | Keep cards away from the face by a face box; no background blur | — |
| Image generator | User photos / frame grabs on the white cards | which cards use frame grabs |
| Music generator / licence | Synthesised bed + SFX | "lower quality than a composed track" |
| Speech-to-text | Ask for the transcript; align by hand | "timings ±0.1 s" |
| The real fonts | Free equivalents in `look.md` | "close, not identical" |
