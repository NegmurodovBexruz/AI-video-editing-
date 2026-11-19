# Brand kit and the motif

## Extract from a brandbook

1. **Palette:** read HEX codes printed on the colour page; never sample swatches from a raster. Assign roles: *dark* (cards, wipes, map ground), *accent* (one warm/strong colour for emphasis), *light neutral* (type), *secondary light* (labels, roads, lines), *mid neutral* (rarely).
2. **Fonts:** display face and text face named on the typography pages. Get the official OFL/licensed files (e.g. the font's own repository); record source and licence. Never substitute silently — if a font is missing, say so and propose the closest licensed alternative.
3. **Logo:** use the original file. If only a raster page exists, make an alpha from the ink (luminance threshold, e.g. `alpha = clip((0.93 − L)/(0.93 − 0.25))`) and fill it with the brand dark; never redraw, stretch or recolour it beyond the brandbook's own variants. Respect the clear space.
4. **Tone of voice:** if the brandbook says "calm / precise / responsible", keep the reference's *pace*, drop its *loudness* (no neon, glitch, rainbow).

## Derive the motif

Pick **one** shape that is already in the logo or the brand's graphic elements page — the thing the company makes or stands for, reduced to strokes. Examples of the kind of reduction (not to be reused literally): a pipe → two concentric circles / two parallel lines with rounded bends; a leaf → one vein curve; a lens → aperture blades; a chat app → a speech-bubble corner.

Use it everywhere, in this order of importance:
1. Inside the hook word (replace the matching letter).
2. As the transition wipe (the shape scaled to full screen).
3. As lines and routes (route on the map, comparison bars).
4. As grids/fields for counts.
5. As pins and rings (map origin, arrival pulse).

Draw it as strokes in the light colours over the dark colour. Fill only for wipes and plates.

## No brandbook

Search for the brand's official site or social pages first. Never cut a logo out of a retailer's packaging photo or redraw it — leave the logo slot empty in the end card and ask the user for the official file. Meanwhile build a neutral kit and tell the user: dark `#14171C`, accent `#E0573B`, light `#F5F5F2`, secondary `#B9C2CC`; display face Space Grotesk, text face Inter (both OFL). Keep colours as parameters so the real palette is a one-line swap. Motif: derive from the topic's main object as above (e.g. a liquid drop for absorbency, a ring for fit), or a plain double ring.
