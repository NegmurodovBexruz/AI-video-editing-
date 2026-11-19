# QA, traps and fallbacks

## Traps (read before decoding)

- **Source fps:** decode with `fps=30` before scaling; a 29.97 source drifts against a 30 fps timeline if interpreted wrongly.
- **Frame counts:** read until EOF; never assume duration × fps.
- **Two locations / cameras:** the hook is often recorded separately; check audio level and sync at the switch.
- **ASR timing:** word starts drift 0.1–0.3 s from the audible onset; place chunks on the audio onset or a forced aligner.
- **ASR numbers:** "twelve hundred" vs "1,200", "two and a half million" vs "250,000" — never take a number from ASR alone; take it from the fact sheet and match the spoken form.
- **Names:** client, partner and product names are often mis-heard — confirm at gate 1.
- **Keyframe hold before the first key:** open every chunk/counter track with an explicit invisible key.
- **Fonts:** check the counter font has tabular figures, or digits will jitter while rolling.
- **Memory:** stream video; one heavy job at a time.

## Facts, claims and permissions (ads are public claims)

- **Every number on screen must match the user's fact sheet** (value, unit, period). If the speaker's number differs from the facts, ask at gate 1; never "round up" or animate an unbacked number.
- Never add numbers the speaker didn't say.
- Client media: only with the client's/user's permission; record it in the README. Generated shots are allowed only as clearly illustrative inserts and never as "the client's work".
- Partner/platform marks: only with permission; otherwise neutral text badges.
- The agency mark comes from the user; never redraw it.

## Generation

- Preflight the cost, quote it at gate 1, ledger every job id before waiting; never resubmit after a timeout before resolving the original job.
- Prompt the target grade; "no text, no logos, no watermark".
- No faces of real, identifiable people unless supplied.
- If a safety filter refuses a prompt, don't rephrase around it — switch the beat to a text or graphic device and tell the user.

## Checklist after every range render

Extract frames at each device's entry, hold and exit; look at them.

- [ ] Picture and speech in sync at every cut, including the hook → main location switch.
- [ ] **Chunk timing, every chunk:** first visible frame 0–3 f after its first word's audio onset — never before. Measure it against the onset list and list any early chunk.
- [ ] **Caption contrast on every background** — especially on white/bright product shots (pill or dark type applied where needed).
- [ ] Every section change has exactly one marker; no presenter stretch > 8 s without a change.
- [ ] Every on-screen number matches the fact sheet (value, unit, period, abbreviation).
- [ ] Counter digits land exactly on the value; no width jitter; metric word spelled right.
- [ ] Partner badges appear on their names, stacked cleanly, permissions recorded.
- [ ] Strobe montage: 2 f per image, no image twice in a row, caption holds.
- [ ] Leaks: no one-frame flash of the wrong shot; tint settles within 6 f.
- [ ] CTA ends on live footage with the agency mark; no frozen frame.
- [ ] Loudness −14 LUFS ±0.5, true peak ≤ −1 dBTP after the final encode.
- [ ] README lists facts and sources, permissions, caption corrections, licences, credits.

## Fallbacks when something is missing

| Missing | Fallback | Tell the user |
|---|---|---|
| Fact sheet | Numbers stay as plain caption text, no counters | "Numbers aren't animated without a source" |
| Client media | Text cards naming the deliverables, or clearly illustrative generated shots | which shots are illustrative |
| Enough work images for a montage (< 8) | A slower montage (4 f per image) or a 2×2 grid | — |
| Agency mark | Agency name as a clean wordmark | — |
| Partner permission | Neutral text badges | — |
| Music licence | Synthesised bed + SFX | "lower quality than a composed track" |
| Speech-to-text | Ask for the transcript; align by hand | "timings ±0.1 s" |
