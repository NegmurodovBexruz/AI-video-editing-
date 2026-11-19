# Devices: build specs

`W`/`H` = frame width/height, `FW` = face width, `f` = frames at 30 fps, px at 1080 wide (scale with the frame). `ACC` = accent colour (default warm amber, see `look.md`).

## Back word (text behind the subject)

- Needs a clean **person matte** for every frame of the word's life (hair edges feathered 1–3 px). Composite order: footage → back word → person cut-out → front layers.
- The head and shoulders cover part of the letters; at least half of every letter that carries the word's shape stays visible. Shift the word horizontally rather than hide a letter that makes it unreadable.
- Entries (pick one per film for consistency, a second one for variety):
  - **Blur-settle:** opacity 0 → 100 % over 4 f, gaussian blur 18–28 px → 0 and scale 1.08 → 1.00 over 6–12 f, ease-out.
  - **Slide from behind:** the word slides 0.15–0.30 W out from behind the head to its place over 8–12 f, ease-out, already fully opaque, revealed by the matte.
- Exit: blur 0 → 16 px + opacity → 0 over 4–6 f, or hard cut with the transition.
- The word is **screen-fixed**; the footage zooms behind it.

## Front word

- Same entry as the back word (blur-settle), drawn in front of everything. Width 0.75–0.92 W, centred, 0.52–0.66 H.
- Soft shadow (black 30–40 %, blur 20 px) only when the chest area is bright.

## Head-locked cluster

- 1–4 short lines, left-aligned (right-aligned if placed left of the head), line spacing 1.15×.
- Each word appears on its onset: opacity 0 → 100 % in 3–4 f with a short blur 6 → 0 px, or grey-to-white (grey 55 % → white over 4 f).
- Position follows the head every frame (`type.md` → *Head lock*). Size and offset scale with the footage zoom.
- Exit: all lines together, blur 0 → 8 px + opacity → 0 in 4–6 f.

## Sub-line

- Under a chest/front/back word, in `ACC`; words appear on their onsets (2–3 f fade). If the key word above it is head-locked, the sub-line is head-locked too; if the key word is screen-fixed, so is the sub-line.

## Figure (thin serif italic)

- Revealed **left to right** over 8–14 f: a soft-edged wipe (feather 0.03 W) with a 6–10 px blur at the wipe edge, or stroke write-on if the font is a single-line font.
- Small words that complete it ("up to", "per year") follow as a cluster or sub-line.

## Gesture spawn (number from the hand)

- When the speaker shows a count with fingers (or holds up / points at something that the word names): the figure appears **at the hand** on its onset with blur 20 → 0 px and opacity 0 → 100 % over 5–7 f.
- It stays where it appeared (screen-fixed) when the hand moves away; it does not follow the hand.
- Needs the hand's position at the onset frame (hand tracker, or by hand at one frame). No punch during the spawn.

## Script word (written on)

- White handwriting script written stroke by stroke over 10–15 f starting on its onset, on a calm surface (clothes, furniture, table, wall) — never across the face.
- Slight rotation (−8° … +8°) following the surface. Glued to the footage under it (track the surface or use the footage transform) if the camera moves during its life.
- Exit with its composition (fade 4–6 f).

## On-body logo

- A named organisation's mark, white or its own colours, ≈ 0.25–0.40 W wide, on the chest below the collar, glued to the footage (moves with the zoom and the body).
- Entry: fade + blur 4–6 f on the name's onset. Hold 1–2 s. Exit with a transition or a fade.
- Only with the user's permission to use the mark.

## Cellophane wipe (set-up change)

- A sheet of crumpled clear plastic with bright specular highlights sweeps or crumples across the whole frame. Total 4–7 f; the cut to the next set-up happens under its densest frame.
- Build: an overlay clip of real plastic on black (screen/add blend) or on a key; or a generated element. Highlights must be brighter than the footage; tint neutral.
- Sound: a short plastic crinkle.

## Glow-silhouette flash (set-up change)

- The speaker's matte turns into a white glowing silhouette: 1 f outline glow, then 2–3 f the whole silhouette bright white with a wide bloom (blur 40–80 px) over the darkened shot, then hard cut to the next set-up (optionally 1–2 f of the bloom fading over the new shot).
- Needs the person matte. Use for a turn in the story (a new idea, "but…", a reveal).

## Reframe jump

- Inside a set-up, a hard cut to a different crop (±8–15 %) on a phrase boundary; hides a jump in the take. Never during a word.
