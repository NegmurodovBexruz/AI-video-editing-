# Look: grade, bands, palette, fonts

## Grade

- **Warm, soft, slightly lifted shadows**: white balance warm (+300–600 K equivalent), skin peach/amber, highlights creamy not clipped, saturation −5…−10 % except the accent hues.
- Background: keep it soft (shallow depth of field from the source); if the source is sharp and busy, a light blur on the background via the person matte is allowed (≤ 6 px).
- LOG / flat sources: normalise first (levels, S-curve), then warm.
- Two speakers with different cameras: match exposure and white balance so the cut reads as one room.

## Dark bands (the "lit window")

- Top band: black → transparent gradient over the top **≈ 6–14 %** (120–260 px).
- Bottom band: transparent → black over the bottom **≈ 12–15 %** (230–290 px), reaching ~85 % black at the edge.
- Optional soft vignette on the sides (15–20 % at the corners).
- The bands are part of the look, not a caption background; captions sit in the middle and must not depend on them.

## Palette (default kit)

| Role | Value | Use |
|---|---|---|
| Accent gradient | top `#FFC35A` → bottom `#FF6A00` | key phrases, rings, network lines, rims, hollow marks |
| Accent solid | `#FF8A1F` | thin rules, dots, outlines |
| Black | `#0A0A0A` | dark spaces, bands, glass panels (75 %) |
| White | `#FFFFFF` | lead-ins, labels, icons, white cards |
| Light grey | `#E9E9E9` | white-card edges, chrome mid-tones |
| Stroke | `#2A1400` at 80 % | thin outline around accent key phrases |

**Brand override:** replace the accent gradient with the brand's accent (keep a light top → saturated bottom gradient of the same hue) and keep black/white. One accent only.

## Fonts (free defaults; use the brand's or the user's fonts when given)

| Role | First choice | Alternatives | Notes |
|---|---|---|---|
| Key phrase | **Archivo Italic** variable, `wdth` 120–125, `wght` 800–900 | Montserrat Black Italic, Unbounded Bold (+ faux italic 12°) | must be wide and heavy; check glyphs for the clip's language |
| Lead-in | **the same wide italic family**, `wdth` 120–125, `wght` 650–750, sentence case | Montserrat Bold Italic | lead-in and key are one type system; a narrow round face under a wide key reads as two different styles |
| Labels on cards / tags | Poppins SemiBold/Medium | Inter | UI text only, never caption words |
| Card titles (condensed) | **Bebas Neue** | Oswald Bold, Anton | chrome fill on white cards |
| Typewriter sub-line | Poppins Medium | Inter Medium | |

All are SIL OFL. Install them before building and verify the tool reports the exact face (no silent fallback). Asking a tool for italic on a family that has no italic file can silently switch to a different (even serif) face — load the real italic font file and check a rendered frame. If the user supplies fonts, use those.
