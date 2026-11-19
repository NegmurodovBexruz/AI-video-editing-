# Captions: small, calm, chunked

**Units.** px are for a 1080×1920 frame; for other frames multiply by `width / 1080`. Vertical positions are shares of the frame height. Times in frames at 30 fps.

## Body captions (most of the film)

| Property | Value |
|---|---|
| Chunk | 2–3 words (max ~22 characters), one line; break at punctuation and pauses |
| Size | 42–50 px |
| Font / weight | neutral grotesk, Regular–Medium; numbers in **Bold** |
| Case | as spoken (sentence case); product and brand names in their official casing |
| Colour | white |
| Position | centred, ≈ 42–45 % of the height (upper chest, below the chin) |
| Readability | soft dark shadow (blur 8–10 px, 50–60 %) **always**; on bright or white backgrounds add a translucent dark pill (black 35–45 %, radius 0.5 × line height) or switch to near-black type |

- A chunk appears **whole**, with a 2-frame fade-in, and is replaced by the next chunk with a hard cut.
- Numbers in a chunk are bold and may be set one step larger (×1.2).

## Headline captions (section openers)

- At the first line of the Challenge, Result and (optionally) Lesson sections: 2–5 words, 56–66 px, Medium–SemiBold, at ≈ 18–24 % of the height, building **line by line** (each line fades in over 2 frames on its first word). The body caption position stays free while a headline is up.
- At most one headline per section.

## Hook type (first section only)

- Lead words large and light (Light/Regular, 80–100 px) at the top third, appearing on their words.
- **One decorated key phrase** (the "secret / method / mistake" word): caps, outline + soft inner shine, short horizontal speed lines on both sides, letters rolling up into place over 8–12 f, a smaller second word under it.
- Period / scope as a mixed line: small lower-case word + large caps word ("in just one WEEK" pattern).
- After the hook, the style switches to body captions — never keep hook type later in the film.

## Timing

- A chunk's first visible frame is within **0–3 frames after the audible onset of its first word** — never before it. ASR word starts drift 0.1–0.3 s; place chunks on the audio onset or a forced aligner.
- Later words of a chunk may be visible before they are spoken (that is the nature of whole chunks); keep chunks ≤ 3 words so the lead is ≤ ~0.6 s.
- A chunk holds until the next one starts or ≤ 0.5 s after its last word. On a cut to another location the chunk ends at the cut.
- Many tools hold a track's first keyframe value before that key — open every chunk's opacity track with an explicit invisible key.

## When a device replaces the caption

Partner badges, the CTA mark and counters may take the caption's place for their chunk (the badge *is* the caption for a name). Don't show the same words twice.

## Corrections

Client, partner and product names are often mis-heard; confirm spellings at gate 1. Keep the speaker's wording otherwise; list every changed word in the README.
