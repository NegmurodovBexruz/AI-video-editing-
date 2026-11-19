# QA, traps and fallbacks

## Traps (read before building)

- **Source fps:** convert to 30 fps first. A 25 or 60 fps source drifts against a 30 fps timeline if read wrongly.
- **ASR timing and wording:** word starts drift 0.1–0.3 s; snap to audio onsets. Two transcripts may disagree; never "correct" a phrase you cannot verify by ear without telling the user.
- **Cut detection:** frame-rate conversion repeats frames (zero differences). Compute statistics on non-zero differences and compare a spike with the frames *before* it. Motion after a cut is high too.
- **Head tracker:** face detectors fire on hands, posters and patterns. Accept a face only if it sits on the matte's head (same x, just under the head top, not wider than the head).
- **Zoom and VFX:** footage, matte, holograms, wall objects and captions must use the **same** transform per frame.
- **Website capture:** many sites show a preloader. A plain headless screenshot captures the loader. Wait for network idle + several seconds, scroll once for lazy images, then capture.
- **Covered figures:** a key word with digits behind the head loses digits. Figures go above the head.
- **White on white:** the dive ends white; check type contrast on every bright frame.
- **Frozen ending:** an end card that stops moving is a dead hold. Keep motion to the last frame and check the last 2 s.
- **Memory:** decoded CGI clips at 1080×1920 are ~6 MB per frame. Load each clip in only one render worker, or stream it. Run one heavy job at a time.

## Licences and permissions

- **Speaker:** editing a real person's video with AI needs their consent. Record it in the README. Never change the face or the mouth.
- **Brand marks:** only from the user (file, brandbook or their own website). Never redraw them.
- **Reference photos for holograms** (buildings, products): use freely licensed photos and record author and licence. Check **freedom of panorama** for buildings. Some countries (e.g. Uzbekistan) have none, and commercial use of a building's likeness may need permission. Flag it.
- **Generated media** must not pretend to be real footage of a client's work. Holograms are clearly graphic. Cutaways are illustrative.

## Generation rules

- Preflight every job's cost, quote the total at gate 1, ledger every job id before waiting. Never resubmit after a timeout before the original job's outcome is known.
- **Hologram sources:** a still on pure black, 2 variants, pick from a sheet. For line drawings, white lines on black.
- **The dive:** the first frame must be the real location without people. Extend it to 9:16 if needed. The last frame is pure white. Make 2 variants.
- **Cutaways:** 2 variants, pick the one whose camera move serves the label.
- **Prompts:** no text, digits or logos. Labels are drawn in the compositor.
- Video-edit models without masks re-render the whole frame. If one is used, composite only the masked region back over the raw so the face stays original.

## Checklist after every range render

- [ ] **Word sync, every word:** first visible frame 0–1 f after its onset.
- [ ] One key word on screen. Long keys behind the head stay readable. Figures fully visible above the head.
- [ ] Lines under the chin, never over the face. Bottom 300 px and right 140 px clear.
- [ ] Every hologram sits on its surface (contact glow, plausible size). It is revealed by a scan, and is behind or in front of the person as planned.
- [ ] Wall devices hit the real objects (overlay check on a still).
- [ ] Sparks land in the objects, and the objects glow from inside (no solid discs).
- [ ] The dive: clear entry, marks readable, white end on the big figure. Type readable over white.
- [ ] Cutaway label stays on its object.
- [ ] Screen: aspect correct, no type over it, cursor lands on the button.
- [ ] End card moves to the last frame (mean frame difference over the last 2 s > 0.3 on a 108×192 proxy).
- [ ] Loudness on target, true peak ≤ −1 dBTP on the final file. The low-band drop holds in the stop.
- [ ] README: sources and licences, consent, ledger and credits, caption corrections, decisions, open issues.

## Fallbacks when something is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Person matte | No key words behind the head (all above it); no behind-the-person VFX where the person overlaps | "type and VFX never go behind the person" |
| Image generator | Holograms drawn as geometric wireframes (lines, rings, grids) | "simpler holograms" |
| Video generator | Replace the dive with a code-drawn tunnel of rings and the white flash; no cutaways | "no CGI interlude" |
| Website / product capture | Assembling screen with the brand mark and URL only | "no product on the screen" |
| Brand mark | Wordmark in the key-word font | — |
| Music | Speech + SFX only | — |
| Camera moves strongly | 2D tracking of the surface (planar or point track) for each in-scene device, or fewer devices on static moments | "fewer in-scene effects" |
