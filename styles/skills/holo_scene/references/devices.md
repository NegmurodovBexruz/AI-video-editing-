# Devices: build specs

`W`/`H` = frame size, `FW` = face width, `CYAN` = the hologram colour (`look.md`), frames at 30 fps. All in-scene devices are composited onto the graded footage; those that belong *behind* the person are multiplied by (1 − person matte).

## Hologram (the base of most devices)

**Source.** One generated still of the object, **isolated on pure black**, full object in frame, side light. Make 2 variants and pick the one with the clearest silhouette. For an inside / frame / mechanism, generate a **white line drawing on black** instead. Never generate text, digits or logos into a source.

**Layers** (from the source):
- **edge lines:** Canny edges inside the object mask plus the mask's outline, 1–2 px;
- **fill:** the mask × (0.35 + 0.65 × source luminance), drawn at about 22 %;
- **scanlines:** fill × (0.65 + 0.35 · sin(2π·y / 7 px + 0.9·frame)), moving;
- **glow:** blur(lines + fill) at 5 px × 0.6 plus at 14 px × 0.35;
- **flicker:** global × 0.92–1.0, slow.

Blend: screen / add in CYAN.

**Reveal.** A scan line sweeps over the object, top → bottom, or bottom → top for things that grow, in 12–33 f. A bright band rides the scan edge. Never a plain fade-in.

**Size and anchor.** Real-world plausible relative to the person (an object held in the hands ≈ 0.20 H; a hanging object ≈ 0.27 H; a tall structure standing on the floor ≈ 0.75 H). Anchor the object to a real point (hook, palms, floor contact). Add a small cyan ground glow or bounce light on that surface.

**Motion.** Hanging objects sway ±1.5° about the hook (period ≈ 3 s). Objects in hands may turn slightly. Nothing bounces.

## Row lighting / wave and counter (wall of repeated objects)

- Find the repeated objects first: template matching on a clean frame gives their centres and radii. Store them; don't hand-place.
- **Row lighting:** rows light up bottom → top over 1.0 s as cyan outline rings with a faint fill. Hold, then fade over 0.4 s.
- **Wave:** a bright head runs left → right over 1.2–1.3 s; each object flashes as the head passes and keeps a 45 % afterglow.
- **Counter:** the key word counts up with the wave (ease-out over the wave's duration) and lands on the spoken figure. Format with a thin space ("1 250").
- **Converge:** objects light edges → centre in 0.4 s. Use it just before the dive.
- Draw behind the person.

## Object in the hands → skin-to-frame reveal

- The object forms between the open palms on the onset of its name (scan reveal 0.45 s), about 0.20 H tall, top ≥ 0.05 H below the chin.
- When the hands close, it moves up above the clasped hands over 0.5 s (eio) and shrinks ~15 %.
- **Reveal the inside:** the skin hologram fades top → bottom over 0.9 s while the frame/line-drawing hologram brightens in the same place.
- Bounce light: a soft ellipse of the hologram colour on the palms (≈ 30 %, blur 30 px).

## Sparks into place (one becomes many)

- The frame turns hot orange over 0.25 s on a gesture or on the verb.
- It then breaks into 600–900 sparks sampled from its lines.
- Each spark flies to a random real object (wall item) with ease-in over 0.55 s, staggered 0–0.35 s, on a slight upward arc. Each leaves a glow.
- On arrival the objects glow from inside: soft orange body at ≈ 0.72 r, small hot core at 0.30 r, blur 5 / 14 / 36. The rim stays dark. Never solid discs.

## Section drawing (a dimension or spec)

- Draw rings, lines or a profile **on**: arc length 0 → 100 % in 9 f (ease-out). Then hatching and dimension lines appear (6 f). Then labels in a small semibold (e.g. "Ø40 mm", "2 mm").
- Between the hands, below the chin, ≈ 0.24 W across. Fade after the phrase.

## Grow from the surface (models, maps, many copies)

- **Model:** rises from the floor/table contact point, revealed bottom → top over 1.1 s. A cyan ground ring ripples out (60 → 220 px, 0.8 s).
- **Many copies:** small holograms (≈ 0.04–0.05 H, larger in front) drop into rows in front of the model, one every 1.8 s / count. Each falls 60 px with ease-out in 6 f. Each touchdown gets a tiny ring flash.
- Draw behind the person (the person walks in front).

## The dive (CGI interlude, once)

- **Generate:** an image-to-video clip with **first frame = a clean, people-free frame of the real location** and **last frame = pure white**. If the frame needs a 9:16 extension, outpaint it first.
- **Prompt:** "the camera dives into the [opening] and flies fast through its interior; rings/seams pass, strong motion blur, accelerating, ending in pure white light; photorealistic, no text". Make 2 variants and pick the one whose entry is clearest.
- **Cut:** cut into it on the phrase that starts the distance/scale idea, using the clip from its first clear motion. Speed it up ×1.5–2 to fit 2–3 s.
- **Marks:** labels with the claim's steps ("10", "20", "30"…) appear small at the vanishing point and fly outward to alternating walls (scale 0.35 → 2.5 over 0.42 s, every 0.3 s), fading at the end.
- **Exit:** the white end lands on the big figure's onset; the next shot comes out of white (6 f).

## Cutaway with a tracked label (comparison)

- Generated clip, 2–4 s, no text in the prompt.
- Find the compared thing's position at 6–8 times in the clip (grid sheet), interpolate, and keep the label just above it. Size it with the thing's width.
- One label per cutaway, in CYAN, heavy.

## Assembling screen (call to action)

- **Capture the real product:** a website after its preloader (wait for network idle + several seconds, scroll once for lazy images), full-page and viewport captures at the site's desktop width.
- **Place** a flat screen in perspective in free space, above the head or behind the person (matted). The aspect must match the captured window. Keep the key word and lines outside it.
- **Assemble:** a blocky noise dissolve biased to the centre, 0.8 s, with a white particle edge. Then a slow scroll (≈ 900 px of page over 1.8 s, eio) and a cursor that moves to the main button and clicks (scale dip 2 f).
- Soft light spill around the screen (blur 40, ≈ 18 %).

## Full-screen product beat

- The capture or a screen recording fills the frame, with a slow scroll and a lower caption (`captions.md`). 1–4.5 s. Hard cut in and out.

## Moving end card

- Brand dark background with a soft radial lift, the brand mark (from the user's file, white on dark), one line ("Need …?"), the URL in the accent.
- Elements enter in 0.15–0.75 s. Then **keep moving to the last frame**: slow push 1.00 → 1.035, a light sweep over the mark every 1.1 s, faint brand-shape particles drifting, the URL underline growing.
- ≤ 2.5 s. The cut into the card is a 0.2 s white flash.
