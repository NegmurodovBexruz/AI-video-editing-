# QA, traps and fallbacks

## Traps (read before decoding)

- **Source fps:** decode with `fps=30` before scaling; a 29.97 source drifts against a 30 fps timeline if interpreted wrongly — build at the source rate or conform everything.
- **Frame counts:** read until EOF; never assume duration × fps.
- **Existing cuts:** the source may already be cut between two cameras; detect cuts first and plan re-frames on top of them.
- **ASR timing:** ASR word starts drift 0.1–0.3 s from the audible onset in both directions. Place every caption word on the audio onset (10 ms envelope, band 150–4000 Hz, ≥ 6 dB rise within 30 ms) or a forced aligner; use ASR for word identity only.
- **Product names:** ASR mangles brand and product names — list them at gate 1 with the spelling you intend and ask.
- **Keyframe hold before the first key:** many tools show a track's first keyframe value before that keyframe's time; open every word's and every label's track with an explicit invisible key.
- **Fonts:** a requested weight/italic the family doesn't ship can silently fall back to another face; load real font files and check a rendered frame.
- **Memory:** stream video; one heavy job at a time; close previews while rendering.
- **Text files:** UTF-8 without BOM.

## Marks and permissions

- The brand's own mark: only from the user (logo file or brandbook). Never redraw or "improve" it; if none is supplied, use the brand name as a clean wordmark.
- Third-party marks (tools, clients, partners): show them only when the user supplies them or confirms they may be shown. Otherwise use **text-label tiles/cards** with the item's name, and media that shows what the item makes.
- Portfolio media must be the user's own work or clearly marked as illustrative; never present generated images as real client work without saying so.

## Generation (cards and B-roll)

- Preflight the cost, quote it at gate 1, ledger every job id before waiting, never resubmit after a timeout before resolving the original job.
- Stills first (2 variants), pick from a sheet; animate only when a push isn't enough.
- Prompt the footage grade; "no text, no logos, no watermark" unless the card needs a label.
- No faces of real, identifiable people unless the user supplied them.
- If a safety filter refuses a prompt, don't rephrase around it — switch the beat to a text card and tell the user.

## Checklist after every range render

Extract frames at each device's entry, hold and exit; look at them.

- [ ] Picture and speech in sync (hard consonant at a cut).
- [ ] **Word sync, every word:** each caption word's first visible frame is 1–5 f after its audio onset — never before. Measure it against the onset list (not a sample) and list any early word.
- [ ] Words reveal grey → white in place; no caption movement; the block doesn't re-centre while building.
- [ ] Size hierarchy correct (function words small, content words big); tracking tight but letters not merging into one shape.
- [ ] Captions never over the face; same position on speaker, stage and B-roll; nothing meaningful in the platform UI zones.
- [ ] Stage uses one colour; everything on it white (or the brand dark on a light stage).
- [ ] Diagram cards arrive on their names; labels typed, spelled as confirmed.
- [ ] Badge legible in one glance (≤ 3 words); rings don't cover the captions.
- [ ] Portfolio media: permission/illustrative status recorded.
- [ ] Transitions: no one-frame flash of the wrong shot at a stage entry/exit.
- [ ] Opening sting ≤ 0.7 s; end on the static mark over live footage, no frozen frame.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP after the final encode.
- [ ] README lists caption corrections, sources, permissions, licences, credits spent.

## Fallbacks when a tool is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Brand mark | Brand-name wordmark with the same sting motion | "No mark supplied; the sting uses the name" |
| Person matte | Edge tiles stay in front at the frame edges | — |
| Particle effect | Fast dissolve to grain/noise or a hard cut | "Disintegration simplified" |
| Image generator / portfolio media | Text cards on the stage | which cards became text |
| Music generator / licence | Synthesised bed + SFX | "lower quality than a composed track" |
| Speech-to-text | Ask for the transcript; align by hand | "timings ±0.1 s" |
