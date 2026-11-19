---
name: pod_glow
description: Edit a podcast / interview / conversation clip (one or more speakers at mics, any topic, any language, any length) in the "Pod Glow" style — two-tier key-phrase captions (small white lead-in + big glowing accent key phrase) at chest height whose words land on their sound, white-flash cuts between speakers, one UI-style concept card per idea (orbit rings, connection network, tilted 3D cards, glass lower card, hollow "???"), warm grade with dark top/bottom bands, music bed with hits on transitions. Use when the user types /pod_glow, asks for "pod glow style", or gives a raw podcast/interview/talk clip and wants a premium vertical clip (Reels, Shorts, TikTok).
---

# Pod Glow

**One line:** the guests talk; the screen underlines what they *mean*. Every sentence ends on a glowing key phrase, every idea gets one clean interface-style card, and every change of speaker is a white flash.

This is a different job from a fact explainer (e.g. `talk_ahead`): the content is opinion, feeling and concepts, not numbers and places. Devices therefore show *relationships and emotions* (community, connection, collaboration, frustration, questions), not data.

The style is topic-agnostic and length-agnostic. Rules talk about *key phrases, concepts, emotions, people, questions, named terms* — never about any industry, country or particular clip — and densities are rates per seconds of speech, so the same rules fit a 20-second clip and a 3-minute interview. Nothing in this skill belongs to one video; when a user's own video or reference suggests something different, follow the user.

This skill is the style. The agent's own tools do the work: ffmpeg, speech-to-text with word timings, an audio-onset or forced-alignment step, a motion-graphics tool or frame compositor, an image generator for photo inserts, a music source. The style does not depend on which tool builds it. If one is missing, say what it costs the edit and use the fallback in `references/qa.md`.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw video | yes | The clock. Probe it (fps, size, rotation, audio, number of cameras/speakers). |
| Brand kit | no | Accent colour + fonts. Without it, use the default kit in `references/look.md` (warm orange accent). |
| Speaker names / roles | no | Name tags and lower cards. Never invent names; leave tags generic ("Guest", an icon) if unknown. |
| Reference video | no | Pacing only. If it is used, analyse it frame by frame (`qa.md` → *Analysing a supplied reference*). |
| Script / corrections | no | Ground truth for captions. Without it, flag uncertain words. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC, −14 LUFS integrated, true peak ≤ −1 dBTP. Two-tier captions on every spoken line. Other frame sizes: scale px by width / 1080, keep positions as shares of the height (`captions.md` → *Units*).

## Workflow

Do the phases in order. Stop for the user at the two gates. Never spend credits before gate 1.

1. **Intake.** Probe, hash, contact sheet (1 frame / 0.5 s). Detect cuts (`select=gt(scene,0.22)`) and map **who speaks when** (camera angle + voice). Word-level timings, then **audio onsets for every word** (ASR starts are not onsets). Read `references/qa.md` → *Traps*.
2. **Cut plan.** Choose the clip window (hook in the first second: start on a strong opinion, not on "so, um"). Mark speaker switches, dead pauses (offer jump cuts; don't do them silently) and wide/tight re-frames every 2–3 s.
3. **Phrase map.** Split speech into caption chunks and pick each chunk's key phrase (`references/captions.md`). Map each idea to one device with `references/beat-map.md`. Plan table: time · speech · key phrase · device · source · cost.
4. **GATE 1 — plan approval.** Show the plan, the budget, uncertain words and anything the user must supply (names, photos, logo). Wait.
5. **Assets.** Photo inserts (stills first, 2 variants, then pick), icons, emoji images, fonts installed and verified. Ledger every paid job id before waiting.
6. **Build** with the chosen tool: graded footage, one unit per device, caption words generated from audio onsets. Layer order: graded footage → dark bands → devices → captions → flashes/light leaks.
7. **QA every device and every word.** Render short ranges, look at entry/hold/exit frames, run `references/qa.md` — including the per-word sync check against the onset list (not a sample). Fix, re-render the range, look again.
8. **Sound.** Speech + music bed + transition hits + UI pops (`references/sound.md`).
9. **GATE 2 — delivery.** File, the editable project if the tool makes one, README (sources, ledger, credits, rebuild steps, caption changes) and open issues stated plainly.

## Style DNA (the decisions that make it "Pod Glow")

- **Two-tier captions, centre of frame.** Small white wide-italic lead-in on top, big wide heavy italic accent key phrase below, sitting on the chest/mic at ~61 % height — not at the bottom. The key phrase is the *payoff* of the chunk.
- **Words land on their sound.** Each word appears on its audible onset — never before — and drops in from just above its place in 2–3 frames. The caption block itself never moves.
- **One accent colour, glowing.** Key words carry an accent gradient each, a thin dark outline and a soft shadow/glow. Everything else is white, black or light grey. No second accent.
- **Speaker switch = white flash.** Hard cut with 2 frames of white between speakers. Same-speaker re-frames are plain hard cuts.
- **One concept card per idea, every 5–8 s of speech.** Interface-like and clean: orbit rings, connection network, tilted 3D cards on white, glass lower card, hollow punctuation. Never two cards back to back without the speaker between.
- **The face sits in a lit window.** Warm grade, dark gradient bands top and bottom, a light leak in the accent colour at section changes.
- **Breathing room.** After each card, ≥ 2 s of speaker with captions only.
- **Emotion gets a face.** One 3D emoji on an emotion word (frustration, doubt, joy) at most every ~8 s; an icon badge on a concrete thing (time, money, people).
- **Ending on live footage.** The last key phrase builds word by word over the speaker; no freeze, no end card unless the user supplies a logo/CTA.
- **Sound:** music bed under everything, a low hit on every transition, soft UI pops on icons. No vocal music.

## Where the details are

| File | Read it when |
|---|---|
| `references/captions.md` | Chunking, key-phrase choice, sizes, word timing and entry, styling (phase 1, 3, 6) |
| `references/beat-map.md` | Mapping ideas to devices; density rates for any length (phase 3) |
| `references/devices.md` | Building any card: layout, durations, motion (phase 6) |
| `references/look.md` | Grade, bands, light leak, palette and fonts, brand override |
| `references/motion.md` | Caption drop-in, card pop, transitions, flashes, re-frames, exact frame counts |
| `references/sound.md` | Music bed, hits, pops, mix and loudness |
| `references/qa.md` | Traps before decoding, generation rules, checklist after every render, fallbacks |
