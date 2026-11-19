---
name: spotlight_word
description: Edit a raw talking-head video — a person introducing themselves, their work, their path or their company (any topic, any language, any length) — in the "Spotlight Word" style: one small white word at a time, every key word (name, role, brand, place, the decisive verb) spotlighted big in flat yellow with a soft glow and small lead words stacked above it, second words of names written on in a white script, the speaker's work as B-roll joined by tile transitions, place names as huge two-tone type over a photo of the place, type echoes, and a metaphor split layout (presenter in a top window, an illustration of the idea below). Use when the user types /spotlight_word, asks for "spotlight word style", or gives a raw interview/intro/founder/story clip and wants a vertical clip (Reels, Shorts, TikTok).
---

# Spotlight Word

**One line:** the speaker talks in single white words; every word that matters lights up in yellow, and every idea that can be drawn gets drawn — the speaker steps into a small window while the idea plays out underneath.

How it differs from neighbouring styles: captions are not chunks or two-tier phrases but **one word at a time**, with a few **spotlight** words per sentence; graphics are **metaphors and places** shown in a split layout or full frame, not data counters or UI cards.

The style is topic- and length-agnostic. Rules talk about *names, roles, brands, places, journeys, the speaker's work, metaphors* — never about an industry or a particular clip. Densities are rates per seconds of speech; sizes are shares of the frame. When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work: ffmpeg, speech-to-text with word timings, an audio-onset or forced-alignment step, a motion-graphics tool or frame compositor, the speaker's own media (work, photos) or an image generator for illustrations, optionally a music source. The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it (fps, size, cuts, number of cameras). |
| The speaker's work (photos, renders, product shots, screenshots) | strongly recommended | B-roll and tile transitions. Without it, illustrative generated stills — labelled as such. |
| Photos of places named | no | Place devices. Without them, illustrative landmark drawings, never a fake "real" photo. |
| Brand kit (colours, fonts, mark) | no | Override the spotlight colour and fonts; brand name devices. |
| Script / corrections | no | Names and spellings. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Other frame sizes: scale px by width / 1080, keep positions as shares of the height.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s), cut detection, word timings, then **audio onsets for every word**. Read `references/qa.md` → *Traps*.
2. **Spotlight pick.** Mark the spotlight words (`references/captions.md`) and which of them get a script accent.
3. **Idea map.** Map moments to devices with `references/beat-map.md` (place, journey, work, brand, emphasis). Plan table: time · speech · spotlight · device · source · cost.
4. **GATE 1 — plan approval.** Plan, budget, names to confirm, media the user must supply (work, place photos). Wait.
5. **Assets.** Work media selection, illustrations (stills first, 2 variants, pick), fonts installed and verified. Ledger every paid job id before waiting.
6. **Build** with the chosen tool. Order: footage → B-roll / place photos / split layout → devices (patterns, illustrations) → captions → echoes and transition effects.
7. **QA.** Range renders; every device's entry/hold/exit frames; per-word sync against the onset list; run `references/qa.md`.
8. **Sound.** Speech + optional light bed + low hits on the big devices (`references/sound.md`).
9. **GATE 2 — delivery.** File, editable project if the tool makes one, README (sources, media permissions, caption changes, credits) and open issues.

## Style DNA

- **One word at a time.** Small white words replace each other on their sounds; the screen never shows a sentence.
- **Spotlight words.** Names, roles, brands, places and the decisive verb become big, bold, flat yellow with a soft glow; the small words that lead into them stack above. About one spotlight every 1.5–3 s of speech.
- **Script accents.** The second word of a name, brand or place may be written on in a white script under its spotlight — at most one per sentence.
- **Show the work.** When the speaker talks about what they make, their real work fills the frame; consecutive pieces are joined by tile/block transitions.
- **Places get type.** A named place becomes a photo or drawing of it with the name in huge two-tone letters.
- **Journeys get a metaphor.** "From X to Y", "step by step", "all the way to" → split layout: the speaker in a top window, a monochrome metaphor (stairs, road, ladder, bridge…) below, X small at the start, Y in spotlight at the end.
- **Echo for emphasis.** Once or twice per film a spotlight word repeats as a column filling the frame for a beat, then cut.
- **Calm footage, loud type.** The interview keeps its own grade; energy comes from type, cuts to work and the split layout.

## Where the details are

| File | Read it when |
|---|---|
| `references/captions.md` | One-word captions, spotlight choice, sizes, stacking, script accents, timing |
| `references/beat-map.md` | Mapping moments to devices; density rates |
| `references/devices.md` | Building split layout, place type, tile transitions, echo, pattern rise, illustrations |
| `references/motion.md` | Entry/exit motion and frame counts |
| `references/look.md` | Palette, fonts, grade, brand override |
| `references/sound.md` | Optional bed, hits, mix and loudness |
| `references/qa.md` | Traps, media permissions, generation rules, checklist, fallbacks |
