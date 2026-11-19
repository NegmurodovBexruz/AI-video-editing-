---
name: brand_stage
description: Edit a raw single-presenter video in which someone speaks for a brand, studio, agency or product (any topic, any language, any length) in the "Brand Stage" style — minimal white editorial captions (content words big, function words small, each word revealed grey-to-white on its sound), regular cut-aways from the speaker to a full-screen brand-colour stage (branching diagram of named items, item cards, concept badges with glowing rings, portfolio cards), full-screen showcase B-roll with captions on top, a brand-mark sting at the start and end, iris-to-dot / glitch-smear / particle transitions. Use when the user types /brand_stage, asks for "brand stage style", or gives a presenter/founder/agency clip and wants a premium vertical clip (Reels, Shorts, TikTok).
---

# Brand Stage

**One line:** the presenter talks; whenever they name things, show work or land a big idea, the film steps onto the brand's own stage — a full-screen field of the brand colour where items, ideas and work are presented like a keynote — then cuts straight back to the speaker.

How it differs from neighbouring styles: it is not a fact explainer (no counters, maps or words behind the speaker) and not a podcast style (no glowing two-tier captions). Its signature is **restraint on the speaker** (white minimal type only) and **show on the stage** (everything graphic happens in the brand-colour space or in full-screen B-roll).

The style is topic-, brand- and length-agnostic. Rules talk about *named items, lists, concepts, claims, own work, transformations, the brand mark* — never about an industry or a particular clip. Densities are rates per seconds of speech. When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work: ffmpeg, speech-to-text with word timings, an audio-onset or forced-alignment step, a person matte (optional), a motion-graphics tool or frame compositor, an image/video generator or the user's own media for B-roll and cards, a music source. The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it (fps, size, rotation, audio, cuts already in it). |
| Brand kit (logo/mark, colours, fonts) | strongly recommended | Stage colour, the mark for the stings, fonts. Without it, use the default kit in `references/look.md` and a text wordmark instead of a mark. |
| Portfolio / case media | no | Portfolio cards and B-roll. Without it, generated stills on the brief — say so. |
| Logos of named third-party products | no | Only if the user supplies them or confirms they may be shown; otherwise text-label tiles (`qa.md` → *Marks*). |
| Script / corrections | no | Ground truth for captions; product names are often mis-heard. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Captions on every spoken line. Other frame sizes: scale px by width / 1080, keep positions as shares of the height.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s), cut detection, word timings, then **audio onsets for every word**. Read `references/qa.md` → *Traps*.
2. **Story map.** Mark what the speech does sentence by sentence: names items, lists actions, states a concept, shows own work, describes change, closes. Mark section turns.
3. **Stage plan.** Map moments to devices with `references/beat-map.md`, respecting the density rates. Plan table: time · speech · device · source · cost.
4. **GATE 1 — plan approval.** Plan, budget, uncertain names, what the user must supply (mark, colours, portfolio, logo permissions). Wait.
5. **Assets.** Mark, fonts, stage colours, cards/B-roll (stills first, 2 variants, pick), item labels. Ledger every paid job id before waiting.
6. **Build** with the chosen tool. Order: graded footage → stage sections and B-roll → item/portfolio cards → captions → stings and transition effects.
7. **QA every device and every word.** Short range renders; entry/hold/exit frames; per-word sync against the onset list; run `references/qa.md`.
8. **Sound.** Speech + music bed + hits on stage entries + sting sound (`references/sound.md`).
9. **GATE 2 — delivery.** File, editable project if the tool makes one, README (sources, ledger, credits, rebuild steps, caption changes, logo permissions) and open issues.

## Style DNA

- **Quiet speaker, loud stage.** On the speaker: footage + white captions only (the one exception is a UI-tag caption). Every graphic idea moves to the brand stage or to full-screen B-roll.
- **Editorial captions.** White, tight-tracked grotesk, sentence case; content words big, function words ≈ 0.6 × size; a block centred at ≈ 64 % height with lines left-aligned; each word appears in place on its audible onset, grey and soft first, white 3–4 frames later. No colour, no boxes, no movement.
- **One stage colour.** The brand colour as a full-screen radial field (lighter centre, darker edges). Everything on it is white or media. A named third-party item may get its own colour card for a beat, never a second house colour.
- **Name it → show it.** Named items become cards on a branching line that the camera travels along, each card arriving as its name is said.
- **Big idea → badge.** A concept the speaker leans on becomes a logotype (small caps word + large script word) inside expanding glowing rings.
- **Own work → portfolio cards.** Phone-shaped rounded cards scaling in on the stage, the brand tag inside each.
- **Transitions with intent.** Iris-to-dot into a diagram, glitch-smear into a badge, particle disintegration on "change" words, hard cuts back to the speaker.
- **Bookended by the mark.** A brand-mark sting opens (≤ 0.7 s) and closes the film; the end holds the static mark over live footage, never a frozen frame.
- **Rhythm:** speaker ≈ 50–60 % of the runtime; a stage or B-roll moment every 10–15 s; speaker shots 3–8 s.

## Where the details are

| File | Read it when |
|---|---|
| `references/captions.md` | Chunking, size hierarchy, layout, word timing and reveal, UI-tag captions |
| `references/beat-map.md` | Mapping speech to devices; density rates for any length |
| `references/devices.md` | Building the stage, diagram, cards, badges, B-roll, stings |
| `references/motion.md` | Transitions and exact frame counts |
| `references/look.md` | Grade, stage colour, palette, fonts, brand override |
| `references/sound.md` | Music bed, hits, sting sound, mix and loudness |
| `references/qa.md` | Traps, marks and permissions, generation rules, checklist, fallbacks |
