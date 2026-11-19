# Captions: one word at a time, with spotlights

**Units.** px are for a 1080×1920 frame; for other frames multiply by `width / 1080`. Vertical positions are shares of the frame height. Times in frames at 30 fps.

## Body words

- **One word on screen at a time** (two only for an inseparable pair like "New York" or a hyphenated name). Each word replaces the previous one with a hard cut.
- Small, white, medium-weight sans, sentence case, ≈ 48–56 px; centred at ≈ 50 % of the height (upper chest). Soft dark shadow for legibility.
- Punctuation dropped except "?" and "!".

## Spotlight words

Spotlight, in this order of priority (topic-agnostic):
1. The speaker's **name** and **role/title**.
2. The **brand / company / project** name.
3. **Places** (city, country, venue).
4. The **decisive verb or result** of the sentence ("started", "built", "won", "moved").
5. The **end point of a journey** ("director", "first client", "our own studio").

Never spotlight fillers, pronouns or numbers that the user hasn't confirmed.

| Property | Value |
|---|---|
| Size | 150–180 px (one word ≤ 85 % of the width; shrink, don't wrap) |
| Weight / case | heavy grotesk, title case as spoken ("Designer", "Berlin") |
| Fill | flat spotlight yellow (default `#FFE600`) |
| Glow | soft outer glow in the same yellow, blur ≈ 24–32 px, 40–60 % |
| Position | centred at ≈ 58–62 % of the height |
| Lead words | the 1–3 small words just before it stay visible, stacked **above** it at body size, left-to-right on one line ("I'm a" → "Designer") |

- About **one spotlight per 1.5–3 s** of speech; never two in a row without at least one body word between, except a name + its role.
- A spotlight holds until the sentence moves on (typically 0.6–1.5 s), then cuts.

### Stack swap

When a second spotlight follows a related first one ("teacher and author"), the new word enters **above** the old one and pushes it down and out in 6–8 f; the new word settles in the spotlight position.

## Script accents

- The second word of a name, brand or place may be written in a **white handwriting script** under (or overlapping) its spotlight, ≈ 0.8–1.0 × the spotlight size, slightly rotated (−6° … 0°).
- It is **written on** stroke by stroke over 10–15 f starting on its word.
- At most one per sentence; never for ordinary words.

## Timing

- Every word (body or spotlight) appears **on its audible onset — first visible frame 0–3 f after it, never before**. ASR word starts drift 0.1–0.3 s; place words on the audio envelope or a forced aligner.
- Exception: a spotlight entering with a stack swap may start its motion up to 6 f early so that it *settles* on its onset.
- Before its onset a word is absent; open every word's track with an explicit invisible key.

## Over B-roll, photos and the split layout

- Same rules and sizes. Over bright images add a soft dark shadow (body) or a stronger glow (spotlight); never a box.
- In the split layout the words sit on the dark lower panel, centred horizontally, at the height that leaves the illustration readable.

## Corrections

Confirm names and spellings at gate 1. Keep the speaker's wording; list every changed word in the README.
