---
name: editorial_showcase
description: Edit a single-presenter service explainer, portfolio presentation, product introduction or qualitative case in the Editorial Showcase style. Pair editorial serif type and a short expressive accent with message cards, definition cards, document scenes, lower-screen demos and three-row showcases. Choose when the speech alternates explanation with examples or work to show, or when the user requests /styles:editorial_showcase. A metrics-led case, podcast or uninterrupted type-only presenter edit is better served by its own style.
---

# Editorial Showcase

**One line:** explain the idea with editorial type, show the work in moving panels, then return to the presenter.

One visual language has two jobs: **explanation** uses type, messages and documents; **demonstration** uses actual media, a lower-screen demo or three horizontal rows. Select devices by what the speech does, not by a requirement to use every effect.

The rules are independent of topic, brand, language, runtime and rendering tool. The user's brief and approved decisions take precedence over defaults. All timings and dimensions in the references are starting values for this combined style, not claims about an original project's settings.

## Inputs

| Input | Required | Use |
|---|---|---|
| Raw presenter video with speech | yes | Timing, framing and spoken content. |
| Work/product media, document pages or website recording | recommended | Evidence and showcase panels. Without it, use labelled concept diagrams or stay on the presenter; do not fabricate a portfolio. |
| Brand kit | optional | Fonts, one accent colour and an optional supplied mark. |
| Transcript/corrections and reference notes | optional | Spellings, section structure and intended emphasis. |
| Platform/output requirements | optional | Aspect ratio, UI-safe areas and audio target. |

Default delivery: 1080×1920, 30 fps, H.264 + AAC; −14 LUFS integrated, true peak ≤ −1 dBTP. Scale layouts with frame dimensions and adapt safe areas to the destination. Supply captions throughout the spoken content, an SRT, rebuild instructions and any unresolved issues.

## Style DNA

- **Speech chooses the scene.** Request → message; definition → type card; components → document scene; actual work → demo; several complementary views → three-row showcase. Read [beat-map.md](references/beat-map.md).
- **One type kit, two families at most.** Editorial serif carries the idea. One short italic or handwritten accent adds emphasis. Supporting captions stay readable and consistent; see [captions.md](references/captions.md) and [look.md](references/look.md).
- **One house accent.** Dark and light neutral surfaces unify presenter overlays, cards and panels. Supplied work retains its own colours.
- **Demonstration has depth.** A lower demo can grow into a screen; a perspective panel can hand off to a three-row showcase. Rows carry complementary views of the same subject. Fine detail gets its own close-up.
- **Restrained transitions.** Hard cuts are normal. Use a panel transition at an explanation/demo boundary and a small blur/slide for changing text. No mandatory flashes, holograms, counters or opening logo sting.
- **Return to a person.** Finish the point and CTA on live footage where available. The final two seconds retain intentional movement; never manufacture a frozen tail.

## Workflow

1. **Inspect.** Probe video/audio and existing cuts; obtain and review word timings. Reuse the host project's analysis outputs when available. Check one frame per setup for the face, hands, free text space and demo clearance. Read [qa.md](references/qa.md) before planning.
2. **Map the speech.** Read [beat-map.md](references/beat-map.md). Mark definitions, requests, lists, demonstrations and the close. Record which supplied asset supports each proposed showcase. Missing media changes the plan, not the facts.
3. **Set the kit and plan.** Read [look.md](references/look.md) and [captions.md](references/captions.md). Write `plan.md`: time/range, spoken phrase, function, device, source, caption role, transition and cost. Read only the selected device sections in [devices.md](references/devices.md), plus [motion.md](references/motion.md).
4. **Gate 1 — review the concrete plan.** Present the plan, unresolved spellings, missing media and any paid-generation quote. If this plan is already approved or the host job explicitly delegates planning decisions, record the decisions and proceed within that authorization. A style choice alone does not authorize paid generation. Do not repeat an approval already given.
5. **Build.** Use the existing renderer when one is available. Otherwise keep the compositor and creative specification inside the job folder and reuse shared analysis/media/text/audio helpers; do not rewrite the shared engine. Layer order: footage or neutral scene → work panels/device → text → restrained transition. Most devices need no person matte; use tracking only when a surface placement actually needs it.
6. **Preview and correct.** Render entry/hold/exit ranges of the chosen devices. Apply [qa.md](references/qa.md), including caption coverage and readability at phone size. Sound follows [sound.md](references/sound.md). After the full export, check the actual encoded file rather than only the project timeline.
7. **Gate 2 — deliver for review.** Video, SRT, editable specification/project, README with asset sources, caption changes, accepted decisions, costs if any, rebuild steps and remaining issues. Respect the host's result-file contract. A technical pass is not user approval of the edit.

## Selection boundaries

Use this when editorial explanation and visual examples belong in the same film. `case_reel` prioritizes case structure and measured results; `brand_stage` uses a brand-colour stage and diagrams; `spotlight_word` prioritizes single-word emphasis; `in_scene_type` stays within the presenter shot. Do not silently combine those styles' full effect lists with this one.

For a very short or media-poor clip, retain the type kit and choose one justified device. Do not generate scenes merely to fill a quota. Render behaviour must be tested on the new footage; the existence of this skill does not imply a dedicated engine renderer.
