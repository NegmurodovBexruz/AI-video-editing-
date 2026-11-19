---
name: case_reel
description: Edit a raw presenter video that tells a case study — how a brand, agency or freelancer got a result for a client (any industry, any language, any length) — in the "Case Reel" style. The edit follows a fixed story template (number-led hook → client → challenge → strategy → test → result → lesson → call to action), with small whole-chunk captions, headline captions at section openers, slot-roll counters and progress bars for the numbers, partner/platform badges, a 2-frame strobe montage of the work, client B-roll, film-burn light leaks and the agency mark at the CTA. Use when the user types /case_reel, asks for "case reel style", or gives a results/case-study/testimonial-style ad clip and wants a vertical ad (Reels, Shorts, TikTok).
---

# Case Reel

**One line:** a short story with proof — promise a number in the first seconds, show who the client is and what was hard, list what was done, show the work flashing by, land the result numbers, give the lesson, ask for the call.

How it differs from neighbouring styles: it is driven by a **story template** and by **numbers as proof**, not by a look. Captions stay small and calm; energy comes from the hook, the counters, the strobe of the work and the transitions between story sections.

The style is industry- and length-agnostic. Rules talk about *promise, client, challenge, actions, test, results, lesson, call* — never about a sector or a particular campaign. Durations are shares of the runtime and rates per seconds of speech. When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work: ffmpeg, speech-to-text with word timings, an audio-onset or forced-alignment step, a motion-graphics tool or frame compositor, the client's and the agency's own media (or an image generator for clearly illustrative shots), a music source. The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it; note if the hook was shot at a different location. |
| **Result facts** (numbers, period, what was measured) | **yes for any number on screen** | Every counter and number comes from here. Without it, numbers stay only as spoken words in captions, unanimated. |
| Client media (product shots, ads, creatives) + permission | strongly recommended | Client B-roll and the strobe montage. |
| Agency mark, colours, fonts | recommended | CTA mark, accent colour, fonts. Without it, the default kit in `references/look.md` and a text wordmark. |
| Partner/platform marks + permission | no | Badges; otherwise text badges in neutral colours. |
| Script / corrections | no | Names of the client, partners and products. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Captions on every spoken line. Other frame sizes: scale px by width / 1080, keep positions as shares of the height.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s), cut detection, word timings, audio onsets. Read `references/qa.md` → *Traps*.
2. **Story map.** Split the speech into the template sections (`references/structure.md`). Flag missing sections (e.g. no stated challenge) and sections that run long.
3. **Fact check.** List every number and claim the speaker says; match each to the user's result facts. Mismatch or no source → question for gate 1. Write down what the screen will say.
4. **Device plan.** Map moments to devices with `references/beat-map.md`. Plan table: time · section · speech · device · source · cost.
5. **GATE 1 — plan approval.** Plan, budget, fact questions, permissions needed (client media, partner marks), uncertain names. Wait.
6. **Assets.** Client media selection, strobe images, marks, fonts; generated shots only where allowed and labelled illustrative. Ledger every paid job id before waiting.
7. **Build** with the chosen tool. Order: footage (with per-section grade) → B-roll and montages → counters, badges and overlays → captions → leaks and transition effects.
8. **QA.** Range renders; entry/hold/exit frames of every device; chunk timing against the onset list; caption contrast on every background; run `references/qa.md`.
9. **Sound.** Speech + music bed + hits/ticks for counters + montage pulse (`references/sound.md`).
10. **GATE 2 — delivery.** File, editable project if the tool makes one, README (sources, facts and their sources, permissions, ledger, credits, caption changes) and open issues.

## Style DNA

- **The template carries the film.** Every section has its job; each section change is marked (headline caption, location or grade change, light leak, montage).
- **Promise in the first seconds.** The hook states the result with a number before anything else, with the boldest type and motion of the film.
- **Numbers are proof, so they move.** Every result number rolls in (slot-roll counter) or fills (progress bar) on the word it is said — and only numbers the user can back up.
- **Small calm captions.** 2–3 word chunks, small white grotesk at ≈ 43 % of the height, shown whole on their first word; headline captions only at section openers.
- **Show the work fast.** "Creative", "ads", "designs", "versions" → a 2-frame strobe montage of the real work.
- **Names get badges.** Partners, platforms and payment/channels named in the strategy pop in as their own badges.
- **Warm, cinematic main location;** client media keeps its commercial look; light leaks bridge them.
- **End on the ask.** The CTA ends with the agency mark on its name over live footage; no frozen frame, no long end card.

## Where the details are

| File | Read it when |
|---|---|
| `references/structure.md` | Splitting the speech into the story template; section lengths and markers |
| `references/captions.md` | Chunking, sizes, positions, headline captions, hook type, timing, contrast |
| `references/beat-map.md` | Mapping moments to devices; density rates |
| `references/devices.md` | Building counters, bars, badges, montages, overlays, leaks, the CTA mark |
| `references/motion.md` | Transitions and exact frame counts |
| `references/look.md` | Grade per section, palette, fonts, brand override |
| `references/sound.md` | Music bed, counter ticks and hits, montage pulse, mix and loudness |
| `references/qa.md` | Traps, facts and permissions, generation rules, checklist, fallbacks |
