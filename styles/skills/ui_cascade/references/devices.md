# Devices

Sizes as shares of H and W. Frame counts are at 30 fps; scale them for other rates.

## Icon tiles

- **Shape:** a rotated square (diamond), width ~0.18 W, glossy 3D look:
  - accent-coloured face;
  - lighter bevel on the upper edges and soft inner gradient;
  - outer glow in the accent;
  - a small round badge hanging under the bottom corner (a dot, a number or a tiny pictogram).
- **Artwork:** the item's pictogram or logo, in white or full colour, centred on the face.
- **Cluster:** above the speaker's head, within 0.08–0.38 H. Tiles fit together as a diamond lattice (2 tiles below, 1 above, or 2 + 2) with small gaps, not overlapping the face.
- **Entry, on the item's word:**
  1. an accent glow blob appears (3 frames);
  2. the tile resolves inside it while sliding ~0.03 W towards its slot and scaling 0.9 → 1.0 (4–6 frames).
- **Hold:** the cluster stays until the list ends, with a slow common drift (≤ 0.01 W per second) and a faint glow pulse.
- **Exit:** with the stack, or covered by the next set-up stutter.

## Card fan

- **Cards:** 3–5 portrait cards (aspect ~3:4) in frosted violet glass:
  - a thumbnail inside;
  - a small label at the bottom;
  - a small counter pill (eye icon + number) on top.
- **Fan:** the centre card is front and upright; the side cards sit behind it, rotated ±8–15° and offset ±0.2 W. The fan sits in the lower half (0.6–0.85 H), in front of the speaker's chest.
- **Entry:**
  1. cards rise from below the frame with motion blur (8–10 frames);
  2. they spread into the fan (8–10 frames), with a slight overshoot.
- **Counter:** a coloured tag line and a counter can animate to the spoken number; a red tag reads as "bad result".
- **Exit:** sink back down with blur (6 frames), or covered by a bloom glitch.

## Icon → button

- A tool's icon arrives on a glass tile:
  - rotates in in 3D (≈30° → 0° around the vertical axis);
  - takes 6–8 frames;
  - lands below the stack.
- On the word that turns the tool into an action, the tile **swaps in one frame** to a white pill button with "+" (or a short verb). The button then wiggles once ("+" ↔ "×", 2 frames each) as if pressed.
- The button can lead into an app scene: it stays visible while the frame fades out.

## App scenes (full screen)

Native, clean, generic system UI: no real app's logo or trade dress.

**Light scene: to-do / notes:**
- white background, one bold title line at ~0.12 H;
- a list of 3–5 items below, each with a round checkbox;
- items add one by one on their words;
- ticking a box fills it and dims the line;
- a faint "+" button at the bottom.

**Dark scene: chat:**
- black background;
- a dark rounded task card at the top (dashed round checkbox, a bold verb, an avatar of the "other person");
- message bubbles (grey pills, small white text) stack under it, one per message, on their words.

**Entry:**
- *Light:* the speaker shot fades to white over ~8 frames while the UI title fades in over the last 3–4 frames.
- *Dark:* the light scene dims to grey (6 frames), then cuts to the dark scene.
- *From speaker:* a fade to black (6–8 frames).

**Exit:** a hard cut or a stutter back to the speaker.

**Text:** the scene's text shows the idea in the speaker's own words, shortened. It must not contradict the speech, and it never invents facts, names or numbers.

## Negative stutter (set-up cuts)

| Order | Frames | Picture |
|---|---|---|
| 1 | 1 | outgoing shot, bloom-white: exposure pushed to near white, with a soft glow |
| 2 | 0–1 | outgoing shot, normal or inverted |
| 3 | 2–3 | incoming shot **inverted** (colour negative: skin turns cyan, darks turn light) |
| 4 | 0–1 | incoming shot, normal |
| 5 | 1 | incoming shot, bloom-white |
| 6 | — | then normal |

- Total 5–7 frames.
- Captions on the outgoing shot smear horizontally on frame 1 and are gone after it.

## Bloom glitch (inside a set-up)

5–6 frames on a punch word:
- **1 bloom-white frame:** text and bright edges smear into horizontal streaks.
- **1 normal frame.**
- **2 inverted frames:** light background.
- **1 normal frame, 1 bloom frame.**

At most twice per film.

## Type behind the head

- An aside under the headline may sit behind the speaker's head. Use the person matte; the head covers part of the line.
- Never hide the key word or a figure.
