# Devices: build specs

`STAGE` = the brand stage colour pair (centre / edge), `W`/`H` = frame width/height, `f` = frames at 30 fps. px values are at 1080 wide; scale with the frame.

## The brand stage

- Full-frame radial gradient: centre = brand colour (lightest stop at ≈ 50 % / 45 % of the frame), edges ≈ 40 % darker. Optional very slow drift of the centre (≤ 2 % of W over 3 s).
- Everything on it is **white** (lines, labels, rings, type) or **media** (cards). No second colour, no texture.
- Captions keep running on the stage in their usual place and style.

## Branching diagram with item cards

- **Entry (iris-to-dot):** the speaker shot shrinks into a circle (mask) with a soft white rim glow as the stage appears around it (8–10 f); the circle shrinks to a 10–14 px white dot near the top third (4–6 f).
- **Line:** a 3 px white line grows from the dot downwards (6–8 f), then a horizontal branch extends; each new item adds a vertical drop from the branch.
- **Camera:** travels horizontally (or down) along the branch with an ease-in-out move of ≈ 0.6–0.8 s per item, arriving as the item's name is said. Cards already passed slide off-frame.
- **Item card:** rounded rectangle ≈ 0.28 W × 0.42 W, radius ≈ 0.025 W, filled with the item's media (a still or loop from the user, or a generated example of what the item makes). Label above the card: white, ≈ 26–30 px, medium weight, **typed on** (2 f per character) when the name is said.
- Neighbouring cards are partly visible at the frame edges, so the row reads as continuing.
- **Exit:** hard cut back to the speaker, or into an item colour card.

## Item colour card

- Full-frame field in the item's own identity colour; the item card (same spec) enters with a fast horizontal slide + motion blur (4–6 f). One beat only.

## Edge tiles

- White rounded tiles ≈ 0.15–0.2 W, radius ≈ 0.04 W, soft shadow, each with an item's mark or text label, sliding in from the nearest edge (6–8 f, ease-out) and sitting partly off-frame at the top/left/right edges around the speaker — never over the face.
- With a person matte they may sit behind the speaker's shoulders.

## Concept badge

- **Entry:** glitch-smear from the speaker (see `motion.md`), landing on the stage.
- **Logotype:** the concept split into a small word in bold caps (≈ 0.35 × the script word's height, tracked +10 %) and a large word in a flowing script (≈ 0.35–0.45 W wide), white with a soft glow. It **drops in from above** to centre over 12–15 f (ease-out) at ≈ 45 % of the height.
- **Rings:** 2–3 concentric white rings (3–4 px stroke, glow) **expand from the logotype outward**, staggered 6–8 f, radius growing from ≈ 0.2 W to ≈ 0.6 W over ≈ 1 s, fading as they grow; a slight blur-out on exit.
- A paired second phrase gets a second badge with the same layout (rings may already be present).

## Portfolio cards

- Phone-shaped card ≈ 0.42 W × 0.75 W, radius ≈ 0.05 W, the work media inside (cover fit), the brand tag (handle, logo or name) small and white near the bottom inside the card.
- **Entry:** scales from ≈ 0.25 to 1.0 over 10–12 f (ease-out), centred, on the stage; then a slow push 1.00 → 1.05 for the rest of its time.
- Next card: hard cut to the next card at the same size, or the same scale-in.
- Captions keep running over the cards.

## Full-screen showcase B-roll

- The user's work or generated stills/loops on the brief, full frame, hard cut in and out. A slow push (1.00 → 1.06) if the shot is a still.
- Grade it to sit with the footage (`look.md`). Captions on top in their usual place.
- Split screen allowed for two related stills: top/bottom halves.

## Particle disintegration

- The current B-roll or still breaks into fine particles (dust/grain), starting at one edge or one subject and spreading over 1.5–2.5 s; particles drift away with slight turbulence. Sync the start to the change verb.

## Brand-mark sting (open / close)

- **Open (≤ 0.7 s):** the brand mark flies in over the speaker with light-streak trails (3–5 f), blooms to near-white for 2–3 f, then dissolves into pixels/particles revealing the speaker. First caption appears as it clears.
- **Close (last 1.5–2 s):** the same mark returns with streaks and 1–2 frames of RGB-split glitch, then resolves to a **static outline/solid mark** centred over the live footage until the end. The last caption may sit under it.
- Without a mark: use the brand name as a clean wordmark with the same motion.

## UI-tag box

- Thin outlined rectangle (2 px) in the stage colour, with short corner brackets; lines extend from two corners (6–10 f), then items type in word by word inside (`captions.md`).
