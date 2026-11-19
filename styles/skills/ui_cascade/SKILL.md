---
name: ui_cascade
description: Edit a raw single-presenter talking video (any topic, any language, any length) in the "UI Cascade" style — captions build letter by letter into staggered stacks of mixed weights (big white words, dim connector words, small [bracketed] asides, one glowing violet-magenta key word per phrase), figures land on a highlight bar that wipes in, a drifting all-caps accent headline and a drop-cap letter for big statements, named things pop in as glossy 3D app-icon tiles above the head, named pieces of content as a fan of glass cards with counters, longer ideas acted out as full-screen native app scenes (a to-do list, a chat with message bubbles, a button) reached by a fade to white or black, and every camera set-up change cut with a negative/bloom stutter. Use when the user types /ui_cascade, asks for "ui cascade style", "glitch flash with app UI", or gives a talking-head / expert / creator clip and wants a punchy vertical clip (Reels, Shorts, TikTok).
---

# UI Cascade

**One line:** the words pour in letter by letter around the speaker, one word in each phrase glows violet, and whenever the speech names a thing, a piece of content or a routine, it appears as interface — icons, cards, an app screen — with a negative-flash stutter at every cut.

How it differs from neighbouring styles:
- `pod_glow` uses fixed two-tier captions and one concept card per idea; here captions are **free stacks that build letter by letter**, and ideas become **native app scenes** that take over the screen.
- `spotlight_word` shows one word at a time; here a **whole phrase stays and grows** as a stack.
- `in_scene_type` never leaves the speaker; here the edit **does leave**, into full-screen UI.

The style is topic-, language- and length-agnostic. Rules talk about *phrases, key words, figures, named things, named content, routines, conversations, set-ups*, never about an industry or a particular clip. Densities are rates per seconds of speech; sizes are shares of the frame height H and width W. When the user's video or instructions suggest something different, follow the user.

This skill is the style. The agent's own tools do the work:
- ffmpeg;
- speech-to-text with word timings and an audio-onset step;
- a person matte (only for type behind the head);
- a frame compositor or motion-graphics tool;
- an image generator or the user's own media for icon artwork and card thumbnails;
- a music and SFX source.

The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video with speech | yes | The clock. Probe it (fps, size, cuts, number of set-ups). |
| Brand kit (accent colour, fonts, mark) | no | Overrides the violet-magenta accent and the fonts. |
| Logos or artwork of things the speaker names | no | Icon tiles. Use a third-party logo only if the user supplies it or confirms it may be shown; otherwise a neutral pictogram. |
| The speaker's own content (thumbnails, screenshots) | no | Card fans. Without it, neutral placeholder cards, never fake metrics presented as real. |
| Script / corrections | no | Spellings and which words are key words. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Captions on every spoken line except inside app scenes (see `references/beat-map.md`). Other frame sizes: scale px by width / 1080, keep positions as shares of the height.

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe the file, hash it and make a contact sheet (1 frame / 0.5 s). Detect cuts and set-ups, get word timings, then **audio onsets for every word**. Read `references/qa.md` → *Traps*.
2. **Phrase map.** Split speech into phrases. For each phrase choose:
   - its stack layout;
   - its key word (accent);
   - its dim connector words and asides;
   - whether it gets a bar, a headline or a drop-cap.
   See `references/captions.md`.
3. **Device map.** Map moments to devices with `references/beat-map.md`: icon tiles, card fan, app scene, icon-to-button, stutter. Write a plan table: time · speech · stack · key word · device · source · cost.
4. **GATE 1 — plan approval.** Show the plan, the budget, uncertain words, logo permissions and what the user must supply. Wait.
5. **Assets.**
   - Fonts installed, with glyphs verified for the language.
   - Icon artwork and card thumbnails: stills first, 2 variants, pick one.
   - App-scene layouts.
   - SFX.
   - Ledger every paid job id before waiting.
6. **Build.** Layer order: footage → (type behind head, via matte) → icon tiles / card fans → caption stacks → app scenes (full frame) → stutter and bloom transitions.
7. **QA.** Range-render every device's entry, hold and exit frames. Check per-letter cascade timing against the onset list. Run `references/qa.md`.
8. **Sound.** Speech, a low bed, and one SFX per device (`references/sound.md`).
9. **GATE 2 — delivery.** File, editable project if the tool makes one, README (sources, logo permissions, caption changes, credits) and open issues.

## Style DNA

- **Letters pour in.** Every word builds letter by letter, cool-tinted and soft at first, settling to full colour in a few frames. The phrase stays and grows; it clears when the next phrase starts or at a set-up cut.
- **Stacks, not lines.** A phrase is a staggered left-aligned stack over the speaker's upper body. It has big white words, small dim connectors, `[bracketed]` small asides and **one accent key word** in a violet-magenta gradient with glow.
- **Figures sit on a bar.** A number or range lands on an accent bar that wipes in from the left before the figure writes on. A small accent tag holds the unit.
- **Big statements get a headline or a drop-cap.** The headline is all caps, in the accent, above the head, drifting slowly sideways. The drop-cap is a large white first letter with two small lines beside it.
- **Things become icons.** Named objects, brands or services pop in as glossy 3D app-icon tiles that gather in a small cluster above the head, one per item, each on its word.
- **Content becomes cards.** Named videos, posts or works rise as a fan of glass cards with a thumbnail and a small counter.
- **Routines and conversations become app scenes.** A list of chores becomes a to-do app. Excuses or messages become a chat with bubbles. An action becomes a button. These are full-screen and reached by a fade to white or black. They act the speech out instead of transcribing it.
- **Every set-up cut stutters.** A bloom-white frame, two or three negative frames, then a bloom-white frame, with a glitch hit in the sound. Between cuts the footage stays natural.

## Where the details are

| File | Read it when |
|---|---|
| `references/captions.md` | Letter cascade, stack layout, key word, connectors, asides, bar, headline, drop-cap, timing |
| `references/beat-map.md` | Which speech gets which device; density rates; when captions pause |
| `references/devices.md` | Icon tiles, card fan, app scenes, icon-to-button, stutter and bloom transitions |
| `references/motion.md` | Frame counts and easing for every entry, exit and transition |
| `references/look.md` | Palette, fonts, glow, glass material, UI scene look, brand override |
| `references/sound.md` | Bed, SFX per device, mix and loudness |
| `references/qa.md` | Traps, permissions, generation rules, checklist, fallbacks |
