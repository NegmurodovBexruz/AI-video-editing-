# Motion specs

All values are for a 1080×1920 / 30 fps output. `ease_out` = cubic `1-(1-x)^3`; `ease_in_out` = smoothstep `3x²-2x³`. Times in seconds. Lines are anti-aliased, drawn at sub-pixel precision (×4 fixed point), widths 2–4 px.

## Words

| Device | Spec |
|---|---|
| **Letter rise** | Each letter slides up from below a baseline mask (clip window = cap top − 10 px … baseline + descender). Duration 0.32 s `ease_out`, stagger 35 ms (20 ms for words > 10 letters). Exit: fade 0.25 s. |
| **Motif letter** | A letter whose shape matches the motif (e.g. "O" → pipe/ring cross-section) is replaced by the motif drawn with strokes; it draws on (arc 0→360°) in the same 0.32 s while rising. |
| **Slam** | Number enters at scale 1.22 → 1.00 in 0.18 s `ease_out`, no stagger, plus a hit shake. |
| **Behind speaker** | Composite the word, then multiply its alpha by `1 − matte` (matte transformed with the same crop as the footage). Place it so the head overlaps the lower third of the glyphs. |
| **Slide label** | Small labels: fade 0.3 s + 20–36 px upward slide, `ease_out`. |

## Counters

| Device | Spec |
|---|---|
| **Decimal counter** | `value = target × ease_in_out(progress)`; one decimal while counting (`26,7`), integer at the end (`50`). Decimal comma if the language uses it. |
| **Odometer** | Each digit column scrolls inside a window of `glyph height × 1.3`; the units column rolls continuously, upper columns flip only in the last 25 % of each step (`ease_in_out`). Leading zeros blank. Thin space between thousands. |
| **Plate** | Counter on a dark plate (brand dark, 90 %) when lines or maps run underneath. |

## Transitions (4–13 frames)

| Device | Spec |
|---|---|
| **Iris** | New scene revealed inside a growing circle from (W/2, 0.45 H): radius 40 → diagonal over 0.32 s `ease_in_out`; a double motif ring rides the edge and fades to 40 %. |
| **Brand wipe** | A giant motif shape (full-width band, rounded nose = semicircle of W/2, length ≈ 2 500 px) slides bottom → top in 0.42 s `ease_in_out`. Ahead of the nose: old scene. Behind the tail: new scene. Band: brand dark with two light contour lines inset 60 and 120 px. Start it 0.21 s before the cut so the cut is hidden. |
| **Scan reveal** | A horizontal light line sweeps bottom → top in 0.7 s `ease_in_out`; above it brand dark, below it the new image; glow = Gaussian 14 px. Use for "look inside" moments. |
| **Fly-through** | Last 0.32 s of an insert: zoom 1→5 (`ease_in_out²`) into an opening; then iris the speaker back in from the opening over 0.26 s. |
| **Shrink-to-pin** | Footage scales 1 → 0.03 over 0.55 s `ease_in_out` while its centre travels to the pin; a light frame fades in on it. The map is already drawn behind. |
| **Hard cut** | The default between speaker shots. Most cuts stay hard; transitions are for scene changes. |

## Camera

| Device | Spec |
|---|---|
| **Punch-in** | 1.30–1.45× crop from the source (lossless from 4K into 1080 up to 2×). Cut in on a phrase boundary; optional drift +0.06 over the shot. |
| **Crash zoom** | 1.00 → 1.55 in 0.16 s `ease_out`, centred on the matte's horizontal centroid (EMA 0.15) so a walking speaker stays framed. |
| **Hit shake** | On slams/arrivals: offset `amp·e^(−14t)` with sin/cos at 95/77 rad·s⁻¹, amp 10–16 px, 0.35 s. Max ~5 per 30 s. |
| **Insert entry push** | Inserts start at 1.05× and settle to 1.00 in 0.35 s. |
| **Map camera** | Zoom in log space from ~90 px/km to the fit scale with `ease_out` over ~2.1 s, starting 0.35 s after the shrink; centre moves with the same progress. The route head starts 0.25 s later and is `ease_in_out` so it never leaves the frame. After arrival: slow drift +6 % zoom. |

## Scale visuals

| Device | Spec |
|---|---|
| **Route** | Drawn as the motif (two parallel light lines ±4.5 px) with an accent head (dot 9 px + 26 px glow at 35 %); arrival pulse = expanding ring 0.6 s. |
| **Benchmark** | White dot on the route at the benchmark's fraction, leader line to a two-line label in free space; the part beyond it repainted in the accent colour (9 px) over 0.6 s. |
| **Silhouette stack** | Main image shrinks to 58 % and slides left over 0.55 s; N silhouettes (height ~128 px) pop in a grid on the right, evenly spaced across the number words (rise 30 px, 0.18 s each), then the "×N" label. |
| **Field of shapes** | Hex-packed motif rings (r 9 px, pitch 22 px) appear in order of distance from the bottom centre while the counter runs. Opacity 75 %, occluded by the matte. |
| **Engineering drawing** | Dark disk (86 %), outer and inner contour draw 0.6 s, dimension line grows 0.4 s later, labels 0.6 s and 1.0 s after start, accent callout for the critical dimension. |

## Grade

Footage only (never graphics): mild S-curve (22 % blend toward smoothstep), saturation 0.9, red ×0.985, blue ×1.02. Generated inserts are prompted in the same "muted cool" grade so no extra grade is needed.
