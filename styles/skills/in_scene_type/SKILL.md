---
name: in_scene_type
description: Edit a raw single-presenter talking video (any topic, any language, any length) in the "In-Scene Type" style — the edit never cuts away from the presenter; every phrase becomes a layered type composition inside the shot: one huge condensed key word behind the head (person matte) or in front at the chest, the other words as small clusters beside the head that move with the head, a small accent-colour sub-line, figures in a thin serif italic written on, numbers that spawn from the speaker's gesture, script words written on the body or the room — plus punch / hold / release zoom pulses, zoom-out reveals that make room for big words, and physical transitions between set-ups (cellophane wipe, glow-silhouette flash). Use when the user types /in_scene_type, asks for "in-scene type", "text behind the head", "text that follows the head", or gives a raw talking-head / explainer / advice clip and wants a vertical clip (Reels, Shorts, TikTok).
---

# In-Scene Type

**One line:** the presenter never leaves the screen — the words move into the room with them: behind the head, beside it, across the chest, out of their hands.

How it differs from neighbouring styles: no cut-aways to stages, B-roll or cards; captions are not a strip but **type in depth** (behind / beside / in front of the person), and the small words are **tracked to the head**. The camera breathes with **zoom pulses**; set-ups change through **physical transitions**.

The style is topic- and length-agnostic. Rules talk about *phrases, key words, figures, gestures, set-ups* — never about a subject or a particular clip. Densities are rates per seconds of speech; sizes are shares of the frame or of the face width. When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work: ffmpeg, speech-to-text with word timings, an audio-onset or forced-alignment step, a person matte, a face/head tracker, a compositor or motion-graphics tool, optionally an overlay element for the cellophane transition and a music source. The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it (fps, size, cuts, number of set-ups / cameras). |
| Source resolution above the delivery size | recommended | Zoom pulses are digital; a 4K or 1440p source keeps punches sharp. |
| Script / corrections | no | Spellings, which words are key words. |
| Logos of organisations named | no | On-body logo device — only with permission. |
| Brand kit | no | Accent colour and fonts override. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Other frame sizes: scale px by width / 1080, keep positions as shares of the height.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s), cut detection, word timings, **audio onsets for every word**, person matte and head track for the whole clip (check them on a sheet). Read `references/qa.md` → *Traps*.
2. **Phrase map.** Split the speech into phrases; pick each phrase's key word and its layer (`references/type.md`).
3. **Beat map.** Zoom pulses, reveals, gesture spawns, transitions (`references/beat-map.md`). Plan table: time · phrase · key word · layer · camera move · device · cost.
4. **GATE 1 — plan approval.** Plan, budget, spellings to confirm, logos/permissions. Wait.
5. **Assets.** Fonts installed and glyphs verified for the language; cellophane overlay (stock the user may publish, or generated — 2 variants, pick); logos. Ledger every paid job id before waiting.
6. **Build.** Order: footage + zoom/reframe curve → back layer (huge words) → person matte cut-out → front layer (chest words, numbers, logos) → head-locked clusters and sub-lines → script write-ons → transitions.
7. **QA.** Range renders; every composition's entry/hold/exit frames; per-word sync against the onset list; head-lock check on the tracked clusters; run `references/qa.md`.
8. **Sound.** Speech + optional bed + transition sounds (`references/sound.md`).
9. **GATE 2 — delivery.** File, editable project if the tool makes one, README (sources, permissions, caption changes, credits) and open issues.

## Style DNA

- **Stay on the speaker.** No B-roll, no full-screen cards. Set-ups (framings, rooms, positions) change; the person is always there.
- **Every phrase is a composition.** One key word big, the rest small, each word appearing on its sound; the composition clears when the phrase ends.
- **Type in depth.** Huge condensed key words sit *behind* the head (the head covers part of the letters) or *in front* across the chest; small words float beside the head.
- **Small words ride the head.** Phrase clusters keep their offset from the head every frame — same frame, same distance, no lag, no spring.
- **Mixed families as a system.** Condensed heavy caps for key words, a clean sans for small words, a thin serif italic for figures, a script for one emotional word, a small accent-colour sub-line.
- **Words come from the scene.** A number the speaker shows with fingers appears at the hand; a script word is written on the body or furniture.
- **The camera breathes.** Punch → hold → release on emphasis; a zoom-out reveal before a huge word; one long accelerating push may close a set-up. The final set-up is calm.
- **Physical transitions.** Set-ups change under a cellophane wipe or a glow-silhouette flash; otherwise hard cuts.

## Where the details are

| File | Read it when |
|---|---|
| `references/type.md` | Layers, key-word choice, sizes, positions, fonts, timing, head lock |
| `references/beat-map.md` | Mapping speech to compositions, camera moves and devices; density rates |
| `references/camera.md` | Zoom pulse, reveal, push, reframe — sizes, frame counts, easing |
| `references/devices.md` | Back-word with matte, head-locked cluster, gesture spawn, write-ons, figures, on-body logo, transitions |
| `references/motion.md` | Entry/exit animation of every type layer, frame counts |
| `references/look.md` | Palette, fonts, grade, brand override |
| `references/sound.md` | Bed, transition sounds, mix and loudness |
| `references/qa.md` | Traps, permissions, generation rules, checklist, fallbacks |
