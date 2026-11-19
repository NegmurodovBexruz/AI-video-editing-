---
name: holo_scene
description: Edit a raw presenter video (one speaker, any topic, any language, any length) in the "Holo Scene" style — stacked kinetic captions (a tiny lead word, one huge key word that sits behind the presenter's head, small centred lines under the chin, every word on its sound), cyan hologram VFX placed inside the real shots on the real things the speaker talks about (objects built from light in the hands, surfaces that light up row by row, a model that grows out of the floor or a table, parts that break into sparks and fly into place), one full-CGI interlude where the camera dives into the subject and flies through it, a product/site screen that assembles from particles, full-screen product screens with captions, and a moving end card with the brand mark. Use when the user types /holo_scene, asks for "hologram style", "VFX inside the shot", "like the agency case video", or gives a presenter clip for a brand, product, service or a fact explainer and wants a premium vertical clip (Reels, Shorts, TikTok).
---

# Holo Scene

**One line:** the presenter talks in a real place; every claim is proven *in that place* — light draws the thing they name onto the real objects, and once per film the camera dives into the subject.

How it differs from neighbouring styles:
- `in_scene_type` stays on the speaker with type only.
- `brand_stage` cuts away to a flat brand-colour stage.
- `case_reel` montages the client's work.
- Holo Scene keeps the real location and **adds believable light-objects to it**: cyan holograms locked to real surfaces, hands, floors and walls. It has one CGI fly-through and one assembling screen.

The style is topic-, brand- and length-agnostic. Rules talk about:
- **claims:** *named things, quantities, mechanisms, comparisons*;
- **surfaces:** *hands, a wall of repeated objects, a floor, a table, the space above the head*;
- **set-ups.**

They never talk about an industry or one clip. Densities are rates per seconds of speech; sizes are shares of the frame or of the face width (FW). When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work:
- ffmpeg, speech-to-text with word timings, an audio-onset step;
- a person matte and a head track;
- a frame compositor;
- an image generator (sources for holograms, the first frame of the interlude), a video generator (the interlude and optional cutaways), optionally a music generator;
- a headless browser when a website is the product.

The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it (fps, size, cuts, set-ups). A static or slow camera makes in-scene VFX easy; strong camera motion needs tracking (`qa.md`). |
| Brand kit (mark, colours, fonts) | strongly recommended | End card, screen, accent. Without it: default kit in `look.md`, wordmark instead of a mark. |
| Product / website URL or screenshots | recommended | The assembling screen and the full-screen product beats. |
| Script / corrections | no | Spellings, figures, which words are key words. |
| Photos of objects that must look exact (buildings, products) | no | References for the hologram source stills. Check their licence (`qa.md`). |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. If the user has a house loudness (e.g. −10 LUFS), use it. Captions on every spoken word; deliver an SRT too.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s), cut detection, word timings, **audio onsets for every word**, person matte and head track. Then a **placement sheet**: one frame per set-up with a 10 % grid. Mark where the hands, the face, the free floor or table, the repeated objects and the space above the head are. Read `references/qa.md` → *Traps*.
2. **Claim map.** Sentence by sentence, mark what the speech does: names a thing, states a quantity, explains a mechanism, compares, turns, calls to action. Pick the key word of each phrase (`captions.md`).
3. **VFX plan.** Map claims to devices and surfaces with `references/beat-map.md`. Respect the densities: one interlude, one screen, one VFX per set-up minimum. Plan table: time · phrase · key word · surface · device · source (code / generated still / generated clip / screenshot) · cost.
4. **GATE 1: plan approval.** Show the plan, the budget, the spellings and figures to confirm, the licences and permissions. Wait.
5. **Assets.** Hologram source stills on pure black (2 variants, pick). Interlude: first frame from the real location, last frame white (2 variants, pick). Website capture after its preloader. Brand mark. Music. Ledger every paid job id before waiting.
6. **Build.** Order:
   - graded footage with the zoom curve;
   - **behind-the-person layer** (key word, wall and floor holograms, screen);
   - person matte cut-out;
   - **front layer** (holograms in the hands, drawings, sparks);
   - small caption lines;
   - grain.

   The CGI interlude and the full-screen product beats replace the footage; captions continue over them.
7. **QA.** Range renders at every device's entry, hold and exit. Check per-word sync against the onset list and run `references/qa.md`.
8. **Sound.** Speech, music bed aligned to the film's big hit and stop, SFX on every VFX event (`references/sound.md`).
9. **GATE 2: delivery.** File, SRT, README (sources and licences, ledger, credits, caption changes, decisions, rebuild steps) and open issues.

## Style DNA

- **The place is the stage.** Footage of the real location stays on screen most of the time (≥ 70 %). VFX are added *to* it, never instead of it, except the one interlude and the product screens.
- **Light proves the claim.** What the speaker names appears as a cyan hologram on the real surface it belongs to: in the hands, on the wall of objects, out of the floor or table, above the head. Holograms have bright edge lines, a faint scan-lined fill and a soft glow. They are revealed by a scan line, never just faded in.
- **Stacked captions.** One tiny lead word, one huge key word, small centred lines under the chin. Long key words sit **behind the head**, so the person covers a few letters. Figures and short key words sit **fully readable above the head**. Small words grow from grey to white on their sound.
- **One dive.** Once per film the camera dives into the subject (an opening, a screen, a box, a product) and flies through a CGI interior. Marks of the claim pass on the walls; the dive ends in white. The camera comes out into the next beat.
- **The product assembles.** A screen or panel with the real product or website builds itself out of particles in the location, behind the presenter, and a cursor uses it.
- **Parts become the whole.** At least once a hologram breaks into sparks that fly into real objects, or a wave runs across repeated objects while a counter counts up. Quantities are *shown happening*.
- **One accent light.** Cyan holograms (hot orange only for heat or metal). White type, a soft dark shadow. No second hologram colour.
- **Moving end card.** The brand mark on the brand dark colour with a short line and the URL. Something moves on it until the last frame, and it is ≤ 2.5 s long.

## Where the details are

| File | Read it when |
|---|---|
| `references/captions.md` | Stack layout, key-word choice and placement, sizes, word timing, readability over bright frames |
| `references/beat-map.md` | Claim → device and surface; densities; story shapes; plan table |
| `references/devices.md` | Building every hologram and device: sources, layers, placement, frame counts |
| `references/motion.md` | Entries, exits, transitions, camera, frame counts |
| `references/look.md` | Palette, fonts, grade, brand override |
| `references/sound.md` | Music bed alignment, SFX per device, mix and loudness |
| `references/qa.md` | Traps, licences and permissions, generation rules, checklist, fallbacks |
