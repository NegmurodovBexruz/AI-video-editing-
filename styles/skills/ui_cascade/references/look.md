# Look

## Palette (default kit)

| Role | Value |
|---|---|
| Accent core | `#C000E6` |
| Accent highlight (top of gradient, glow) | `#EE39FA` |
| Accent deep (bottom of gradient) | `#8A00C2` |
| Glass (cards, tool tiles) | `#7638CC` at 60–75 % opacity, with a white 1 px rim at 30 % |
| Caption white | `#FFFFFF` |
| Connector white | `#FFFFFF` at 50 % |
| Entry tint (white words) | `#9FD3FF` |
| Entry tint (accent words) | `#FFB3F5` |
| "Bad result" tag | `#FF2A2A` |
| Light scene | background `#FFFFFF`, text `#111111`, secondary `#8A8A8A`, button `#E9E9E9` |
| Dark scene | background `#000000`, card `#1C1C1E`, bubble `#3A3A3C`, text `#FFFFFF` |

Brand override: replace the three accent values with the brand colour (core, +25 % lightness, −25 % lightness). Keep one accent; never add a second.

## Accent treatment

- Key words, the figure bar, headlines and tiles use a vertical gradient (highlight at the top → core → deep at the bottom).
- Outer glow in the highlight colour: radius ~0.012 H, 50–60 % opacity.
- Over a bright background, keep the glow but add a soft dark shadow (black at 35 %, offset 0.002 H) so the edge stays readable.

## Fonts (free / OFL)

| Use | Font | Notes |
|---|---|---|
| Big words, key word, headline, drop-cap | **Inter Black** or **Montserrat ExtraBold** | tight tracking (−2 %) |
| Connectors, asides, small lead | **Inter Medium** | asides keep the square brackets in the same font |
| App scenes | **Inter** (SemiBold titles, Regular body) | a system-UI feel |

Verify that every glyph of the video's language exists in the chosen font before rendering (Cyrillic, Latin extended, etc.).

## Footage

- Keep the speaker's own grade.
- Optional light polish: contrast +5 %, saturation −5 %. The accent should be the most saturated colour on screen.
- No vignette, no heavy LUT.

## Glass material

- Frosted glass for cards and the tool tile:
  - background blur of what is behind (radius ~0.01 H);
  - violet tint;
  - thin white rim;
  - soft drop shadow below (black at 40 %).
- Thumbnails inside cards are sharp, with rounded corners of 0.012 H.

## Icon tiles

- A glossy, plastic or enamel look: accent face with a lighter upper bevel, a subtle specular highlight in the top corner, and a soft outer glow.
- Pictograms in white line or filled style, or the supplied logo.
