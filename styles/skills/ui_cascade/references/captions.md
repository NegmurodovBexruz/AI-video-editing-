# Captions: letter cascade and stacks

Units: H = frame height, W = frame width. Sizes are cap heights.

## The letter cascade

- Every word builds **letter by letter**:
  - each letter starts **2 frames** after the previous one;
  - each letter takes **4–5 frames** to go from soft (blurred, ~0 → 100 % opacity, slightly scaled up ~1.1 → 1.0) to settled.
- **Entry tint.** While entering, a white letter carries a cool tint (pale blue) and an accent letter carries a light pink tint. The tint fades to the final colour as the letter settles, so the leading edge of the word always looks a little lighter than the rest.
- **Timing.** A word starts on its **audio onset**, at most 0.15 s before it and never after +0.05 s. A long word may still be cascading when the next word starts; that overlap is part of the look.
- Short words (1–2 letters) appear whole in 3 frames.

## The stack

A phrase is one stack, left-aligned, laid over the speaker's upper body and head area.
- **Vertical position:** between 0.18 H and 0.62 H.
- **Horizontal:** inside 0.06–0.94 W, aligned to the side the speaker is not leaning towards.
- Consecutive lines are **staggered**: each line starts a little further right or left (0.04–0.12 W) than the one above, so the block reads as steps rather than a column.
- Line spacing is tight. Big lines may overlap the line above by up to 15 % of their cap height.

### Word roles

| Role | Look | Size | How many |
|---|---|---|---|
| Big word | white, heavy grotesque, soft shadow | 0.045–0.055 H | 1–3 per phrase |
| **Key word (accent)** | violet-magenta gradient, heavy, outer glow | 0.05–0.06 H, may span 0.6–0.75 W | **exactly one per phrase**, on the word that carries the meaning (the threat, the promise, the result) |
| Connector | white at ~50 % opacity, regular weight | 0.02 H | the function words that link big words |
| Aside | white, medium, inside square brackets `[ ]` | 0.02 H | conditions, softeners, side remarks ("[if]", "[for yourself]"); at most one per phrase |
| Small lead | white, medium | 0.02 H | the 1–2 words that lead into the key word, stacked directly above it |

Never set a whole phrase in big words. Never put two accent words in one phrase.

## The figure bar

For a number, price, range or percentage:
1. An accent-coloured bar wipes in from the left. Height 0.034 H, final width just wider than the figure line (up to ~0.5 W).
2. The figure line writes on over the bar in white: small words regular, the numbers bold.
3. The unit (currency, "per month", "%"…) appears as a **small accent tag** under the right end of the bar, popping in with a short blur.

## The headline

For one big statement per 15–25 s of speech, especially a claim about the viewer's situation:
- all caps, accent gradient with glow, cap height ~0.045 H, at 0.06–0.12 H;
- letters cascade in and the whole line **drifts sideways** at ~0.1–0.2 W per second, so it may run off the frame edge;
- one small aside line under it, which may sit **behind the speaker's head** (matte);
- it stays while the next stack builds below, then clears with the phrase.

## The drop-cap

For a sentence that starts with a short conjunction or a single letter word, or that sums up:
- the first letter is set **large and white** (~0.09 H), at chest height;
- the next two short lines sit small to its right, top-aligned with it;
- an optional third line in the accent sits below.

## Clearing

- A stack clears when the next phrase starts: fade and slight blur, 4 frames.
- Everything clears at a set-up cut (the stutter covers it).
- A stack never outlives its speech by more than 0.5 s.

## Inside app scenes

Captions **pause** during full-screen app scenes; the scene's own text tells the idea. If the speech in that time says something the scene does not show, keep it out rather than overlaying captions on the UI.
