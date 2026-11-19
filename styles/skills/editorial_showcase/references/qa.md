# QA and fallbacks

## Before building

- Probe source rate, rotation, audio offset and existing cuts. Use an explicit output timebase; a nominal duration is not an exact frame count.
- Review ASR against speech and supplied copy. Low confidence, especially for names and non-English text, is an unresolved item rather than permission to silently rewrite a sentence.
- Inspect supplied reference videos with a full overview and finer frame sequences at transitions/type changes. Distinguish directly observed behaviour from chosen implementation defaults.
- Match every evidence panel to its source. Missing portfolio media is a design constraint, not a reason to invent evidence.
- Test the actual glyphs, weights and italic face. Keep two font families maximum and one house accent. Do not modify shared engine files to work around one job's layout.

## Review ranges and final export

| Check | Evidence needed |
|---|---|
| Speech coverage | Every spoken word is represented in the visual-caption roles and SRT; any intentional omission is documented. |
| Timing | Measured word timings for word-reveal mode, or first-word timing for chunk mode; label the mode honestly. |
| Legibility | Phone-size frame at each device's hold, plus the worst bright/dark frame. No heading/handwriting collision. |
| Layout | Face/hands and platform controls clear after all transforms; no long term leaving the card or paper strip. |
| Lower demo | Presenter remains usable; caption strip does not hide the shown interaction. |
| Showcase rows | Complementary views with sensible crops; detail needing comprehension gets a close-up. |
| Message/document truth | Quoted text is exact or marked as paraphrase; illustrative content is distinguished from actual work. |
| Panel handoff | Entry/middle/exit show no gaps, mirrored content, incorrect crop or stale caption. Final panel is readable. |
| Template hygiene | No sample brand, fabricated value, placeholder copy or unrelated logo. Inspect text embedded inside media too. |
| Ending | Last two seconds retain purposeful movement; no frozen extension or truncated spoken tail. |
| File and sound | Intended frame count/duration, resolution, frame rate, codecs, audio sync and post-encode loudness. |

Inspect the rendered file as well as renderer-generated boxes/timelines. A self-reported empty problem list does not prove the text is visible, the message is correct or the edit feels good. Keep unresolved perceptual checks separate from measured passes.

## Missing capability or input

| Missing | Fallback |
|---|---|
| Actual portfolio/screens | Presenter + approved concept card; request assets only if actual demonstration is essential to the brief. |
| Three useful views | One/two panels; no filler row. |
| Readable handwriting/glyphs | Editorial + utility kit; serif italic is the expressive accent. |
| Headroom for title | Side placement or a definition card; no title cropped above the frame. |
| Stable surface track | Flat wordmark or omit the surface mark. |
| 2.5D renderer | Straight lower-demo reveal or a hard cut; keep the type kit. |
| Music source | Speech with sparse permitted effects, or speech alone. |
| Reliable ASR/alignment | Review against supplied transcript; disclose remaining uncertainty rather than claiming frame accuracy. |

## Cost and authorization

Supplied media and local compositing are the default. When paid generation is genuinely needed, obtain the exact quote before submission and stay within the user's existing approval. If approval is absent, use the no-cost fallback or present that concrete quote; a skill invocation is not spending permission. Record every submitted job ID/cost before waiting. Resolve an existing job before resubmitting after a timeout.

Use supplied marks as supplied and keep source/permission notes with the job. An illustrative replacement must not be presented as a real product interface, testimonial or delivered client project.

## Completion status

Report technical checks, visual review and user approval as separate facts. Follow the host's output/result schema, state any fallback, and do not mark the style as tested in a shared catalog merely because its specification exists. That status needs an actual raw-to-output trial and review.
