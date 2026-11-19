# Devices: build specs (1080×1920, 30 fps)

All sizes in px of a 1080×1920 frame, durations in frames at 30 fps (f). `ACCENT` = brand accent (default warm orange gradient, `look.md`). Pop = the pop curve in `motion.md`.

## 1. Capsule → orbit (central concept)

```
 f0      f4         f8                       f45            f50
 full -> capsule -> pull back, rings in  ->  hold, pills   -> snap back to full frame
 frame   window     (dark space)             orbit slowly     (hard cut + hit)
```
- **f0–4:** footage scales 100 → 62 % into a rounded capsule (width 520, height 760, corner radius 260), directional zoom blur during the move; 3 px ACCENT rim with outer glow; background goes black.
- **f4–12:** camera pulls back: capsule shrinks to a 240 px circle centred at y ≈ 760; 3–4 concentric ring strokes (2 px, ACCENT 60–90 % opacity) grow from the centre, radii ≈ 200 / 330 / 470 / 620; one small ACCENT dot (14 px) rides each ring.
- **f8–20:** tag pills pop in staggered by 3 f: dark grey rounded rect (h 44, radius 22, 8 % white border), white person icon + 26 px white label. Pills sit on the rings and drift along them (≈ 6°/s).
- **f12:** the concept as a two-tier caption under the circle (lead-in white 48 px, key ACCENT 92 px) at y ≈ 1010–1060.
- **Exit:** hard cut back to full-frame footage on a phrase boundary, low hit.
- Tag labels: real names only if the user supplied them; otherwise roles ("Host", "Guest", "Creator") or icons only.

## 2. White card + photo (shared experience)

- Background white → very light grey radial (centre `#FFFFFF`, edge `#E9E9E9`).
- Photo card 600×380, rotated −4°…−6° and Y-rotated 15–20° (3D), long soft shadow (distance 30, softness 40, 35 % black).
- Enters from the left with motion blur (f0–6, overshoot), settles, slow drift 1 %/s.
- Small ACCENT italic line above the card (40 px) builds word by word; big condensed ACCENT words (150–190 px) appear *behind* the card on the key word (card occludes them).
- Photo: user's still, a frame grab, or a generated insert (2 people, matching mood, no faces of real people unless supplied).
- Exit: white flash → footage.

## 3. Network (connection)

- 3–5 person icons (56–72 px ACCENT circles with a white person glyph, glow) pop around the speaker in free space (top-left, right shoulder, left chest), stagger 4 f.
- Glowing ACCENT lines (3 px core + 12 px glow at 40 %) draw from icon to icon and towards the speaker in 6–8 f each (trim path 0 → 100 %).
- Icons breathe (scale 100 ↔ 104 %, 1 s). Captions stay on top.
- Never place an icon over the face; check the matte or face box.

## 4. White card + two tiles (collaboration / exchange)

- White → light grey background with a thick ACCENT swoosh (a wide curved band, 40 % of the frame width, from top-right to bottom-left, slight blur on its edges).
- Title: condensed caps (180–220 px), **chrome/silver** fill (vertical gradient `#F5F5F5 → #8C8C8C → #DADADA`), subtle dark bevel/shadow; small dark italic line above (40 px), word by word.
- Two rounded 3D tiles (260×260, radius 40, slight Y-rotation towards each other, soft shadow): left = speaker still, right = generic grey avatar (or second speaker if supplied); a white circular swap icon (64 px) between them, rotating 180° once.
- Whole card enters with a scale-down from 115 % + blur (f0–6); exit white flash.

## 5. Glass lower card (named term + definition)

- Rounded rect 560×150 (radius 24) at y ≈ 1100–1250, centred or left-aligned with 60 px margin.
- Fill: dark grey `#141414` at 75 % with background blur behind it (frosted), 1 px white 12 % border, soft shadow.
- Title: white bold italic 40–44 px; under it a 2 px ACCENT rule (draws left → right, 8 f); sub-line 32 px light grey, **typewriter** (one character per 1–2 f) synced to the explaining words.
- One title word may flash ACCENT once on its spoken word.
- Enter: slide up 30 px + fade (6 f); exit: fade (5 f) on the phrase boundary.

## 6. Hollow "???" (question)

- Three outlined question marks (ACCENT 4 px stroke, no fill, 260–320 px) centred behind the key phrase, staggered pop (3 f apart), then a slow 3 % scale drift. Fade out with the chunk.

## 7. Accent light leak (section turn)

- A large soft radial (ACCENT → transparent), blend mode Add/Screen, sweeps from one side across the frame in 12–18 f, peak opacity 70 %, plus a 4 f exposure lift. One per section turn, ≤ 1 per 20 s.

## 8. White flash cut (speaker switch)

- Last frame of speaker A → 2 frames solid white (100 %, then 60 % over the first frame of B) → speaker B. Low hit on the first white frame.

## Re-frames

- Same speaker: alternate wide (100 %) and tight (125–140 %, face at upper third) on phrase boundaries every 2–4 s. From a 1080p source keep tight ≤ 130 % to stay sharp; from 4K up to 180 %.
