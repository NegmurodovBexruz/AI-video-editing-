# QA, traps and fallbacks

## Traps (read before decoding)

- **Silent head/tail:** measure speech with `silencedetect` (highpass 120 Hz, −38 dB, 0.35 s). **Cut from the measured voice onset, not from the ASR word start** — ASR often stamps the first word 0.3–0.4 s early. Start 0.1–0.15 s before the onset; the hook rises on the onset. End ≤ 0.8 s after the last voiced sound and let the end card start on the last word (over live footage), so no silent standing remains. After rendering, run `silencedetect` on the delivered file: no silence at the head, ≤ 0.5 s at the tail. Trimming silence at the ends is not retiming speech, but it is still the user's call at gate 1.
- **LOG / flat footage:** if the contact sheet looks grey and low-contrast (lifted blacks, desaturated skin), it is a log profile. Normalise before the style grade: levels 0.07→0 and 0.88→1, S-curve blend 45 %, saturation ×1.35; check skin and whites on a frame. The light style grade alone leaves it grey.
- **Source fps:** phone/camera sources are often 50/60 fps. Decode with `fps=30` *before* `scale`, or the picture runs at half speed against the audio.
- **Frame counts:** don't assume `duration × fps`; read frames until EOF.
- **Matte:** compute it once for the whole clip at ~half resolution with a video matting model (temporal state = no flicker) and stream it; transform it with exactly the same crop as the footage.
- **Memory:** stream every video (one frame in memory); run heavy jobs one at a time.
- **Text encodings:** write `.env`/config files as UTF-8 *without* BOM; allow inline comments (`KEY=value # note`) when parsing.
- **Audio tools:** some loudness/sound builders need the duration to be a multiple of 0.01 s and break on a one-sample mismatch — pad to the next 0.05 s and trim at mux with `-shortest`.

## Generation (credits and inserts)

- Preflight the cost (`get_cost`) for each model/setting before gate 1; quote totals.
- Stills first (2 variants), review side by side, then i2v from the chosen still (5 s, silent, 9:16). Prompt the grade ("muted cool steel-blue, deep navy shadows") to match the footage, and add "no text, no watermark, no people" unless needed.
- For transformations use start + end image.
- Write job ids to a ledger before waiting. On a timeout, never resubmit blindly — resolve the original job first.
- If the generator answers with a *preset recommendation* instead of a job, decline it (pass the declined preset id) unless it truly fits.
- Real, recognisable places/buildings: AI may get them wrong — say so; prefer a licensed photo from the user.
- **Children, bodies, medical/hygiene topics:** prefer stylised figures (vinyl-toy / clay look) over photoreal people, and diagrams over bodies where the point is mechanical. If the generator's safety filter refuses a prompt (`nsfw`), **do not rephrase to get around it** — switch that beat to a drawn diagram or graphic and tell the user. Refused jobs were not charged on Higgsfield; still log them.
- To keep one figure consistent across two images, generate the first, then pass it as `image_references` to the second.
- Animating a still costs an i2v credit and risks another refusal; a digital push (1.00 → 1.06 over the beat) in the compositor is often enough.
- Maps: real geodata (e.g. OpenStreetMap via Overpass with a User-Agent header), styled in brand colours, with the data credit on screen. If a route is approximate, say by how much (e.g. "~54 km straight, shown as 50").

## Checklist after every range render

Extract frames at each device's entry, middle and exit; look at them.

- [ ] Picture and speech in sync (check a hard consonant at a cut).
- [ ] Every text readable: contrast against what is *actually* behind it (bright sky, similar colour).
- [ ] No text touches the frame edge, the captions band (y 1360–1520) or the speaker's face.
- [ ] Behind-speaker words still read with the speaker in front.
- [ ] Labels in free space, leaders pointing at the right part.
- [ ] Counters land exactly on the target on the right word; digits not garbled mid-roll.
- [ ] Moving heads (route, camera follow) never leave the frame.
- [ ] Transitions: no one-frame flash of the wrong scene at the start/end.
- [ ] Brand: only brand colours/fonts; logo unmodified.
- [ ] Facts on screen = the user's decisions; captions' changed words listed.
- [ ] Ending over live footage, no frozen frame.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP; no banned sounds.

## Fallbacks when a tool is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Matte model | Skip behind-speaker words; put hook words above the head on a dark gradient | "Text can't go behind you without a matte" |
| Image/video generator | Use the user's photos or licensed stock stills with a slow push | which inserts become stills |
| Music/SFX generator or licence | Synthesized material family + synth bed | quality is lower than a composed track |
| Speech-to-text | Ask for the script; align by hand | timings may be ±0.1 s |
