# Beat map: speech → device

Work from word-level timings. A **beat** is one idea, usually one sentence or clause (2–6 s). Give each beat exactly one *lead device*; small labels may ride on it. Anchor each device's entry to the word that carries the fact (the number, the noun), not to the sentence start.

## Device table

| The speech contains | Lead device | Anchor | Notes |
|---|---|---|---|
| The opening noun / topic (first 0–2 s) | **Hook word behind speaker** — huge rising letters, motif inside a letter | first syllable of the noun | Hook must land before 1.0 s. If the first shot is wide, the speaker occludes the word's middle; that is the point. |
| A thing the footage does not show (landmark, product, organ, machine, place) | **AI insert**, 1.2–4 s, entered by an iris or wipe | the noun | Close-up or hero angle for the first mention; a "technical" view (x-ray, cutaway, exploded) when the speech explains its insides. |
| A number with a unit | **Slam number behind speaker** (≤ 3 digits) or **rolling counter / odometer** (≥ 4 digits or a count-up) | the number word; a counter *finishes* on the last number word | Show the unit smaller beside/below. Thin-space thousands (`4 200`). |
| Composition / parts of a whole ("of which X is…, the rest is…") | **Labelled technical view**: labels in free margins with leader lines to the part | each part's noun | Labels never sit on the subject's body; they live in empty background. |
| Transformation ("if we turn A into B") | **Morph insert** A → B (start/end-frame i2v) | the verb | Exit through the B shape (fly into an opening, iris out) back to the speaker. |
| Dimensions / specs | **Engineering drawing** drawn stroke by stroke over the insert or a dark disk | the first spec number | Dimension lines + callout in the accent colour. |
| A count of many identical things | **Field of motif shapes** filling the background behind the speaker, synced to a counter | count-up spans the number words | Dim the background (dark brand colour, 55–60 %) behind the matte first. |
| A distance or route | **Real map journey**: footage shrinks into a pin at the origin, camera pulls back, the route draws, counter in a plate | route head reaches the end on the distance word | Brand-styled map from real geodata; credit the data source on screen. |
| A comparison to a known benchmark (marathon, football pitch, a tower, a city) | **Benchmark mark** on the same visual + the difference in the accent colour (`+7,8 km`) | benchmark noun | Compute the difference yourself; show it even if the speaker doesn't say it. |
| "X equals N of Y" | **Stack of N silhouettes** of Y beside X (X shrinks aside) | N | Cut the silhouette from an approved insert still; don't draw clip-art. |
| A rhetorical question | **Crash zoom** on the speaker + question in two lines above the head | first word of the question | Question type in the dark brand colour if the background is light. |
| A myth or negation ("X is not always to blame", "it's not about Y") | **Strike-through**: the claimed word behind the speaker, an accent line crosses it on the negating word, a small correction below ("not always") | the negating word | One strike per film; it is the "but" of the story. |
| An announced list ("let's look at the reasons", "three steps") | **Slots**: numbered motif rings (01 · 02 · 03) appear above the head, staggered 0.18 s | the word "reasons/steps" | Then each item opens with its own **number card** (huge number slam + title rise + a tiny scale/icon row) behind a brand wipe. Show empty slots for items the clip doesn't cover — it reads as a series. |
| Two opposite cases ("too small… / too big…") | **Mirrored pair**: same framing, same layout, opposite state; the second may be a drawn cross-section if the first is an image | each case's adjective (big word behind the speaker between them) | Keep titles, label sides and colours identical so the eye compares. |
| Call to action / sign-off | **End card over live footage**: light gradient at top, logo rises, slogan letter-rise, motif line draws under it | ~1.5 s before the clip ends | Never freeze the last frame. |
| Plain narration with no fact | **Breathing shot**: speaker + captions; optional slow push 1.00→1.06 | — | Needed after every dense device. |

## Density rules

- 30 s film: 8–12 devices, 3–4 AI inserts, at least 2 breathing shots.
- Never two full-screen devices back to back without the speaker between them, except a deliberate chain (insert → transformation → map).
- Long single take (> 8 s of one shot): break it with devices behind the speaker and punch-ins (1.30–1.45× from a 4K source) on phrase boundaries, not mid-word.
- A device ends with its beat; it may overlap the next beat's first 0.2 s for the exit animation only.

## Plan table format (gate 1)

| # | Time | Speech | Device | Source | Cost |
|---|---|---|---|---|---|
| 1 | 0.0–2.0 | "…" | Hook word behind speaker → iris into insert | footage + insert | 1 still ×2 + 1 i2v |

End the table with: total credits (from cost preflight), open fact questions, and what the user must supply (photos of real places the AI can't fake reliably, licences).
