# Worked example: SPC (steel pipe maker), 32.5 s, Uzbek

This shows how the rules turned one video into an edit. Copy the *decisions*, not the content.

**Input:** 4K/60 fps vertical, one speaker, 4 shots (wide crane 0–2.1 s; medium in front of a pipe stack 2.1–23.2 s — one 21 s take; wide walking 23.2–28.9 s; medium 28.9–32.5 s). Brandbook: dark `#122A39`, accent `#9C4932`, light `#F7F8F6`, mist `#C5D4DE`; Space Grotesk + Inter; motif = the pipe in the logo (two concentric circles / two parallel lines with rounded bends).

**Fact check:** the speech said "the statue weighs *two* tonnes, of which *thirty* tonnes are copper" — impossible. 4 200 pipes × 12 m of 57×3 mm (≈ 4.0 kg/m) ≈ 200 t, which also fits "Tashkent TV tower ≈ 30 statues". Word gaps (0.10 s) showed the speaker really said "two"; the user chose to show 200 t. Logged as an open issue.

## Beats → devices

| Time | Speech (gist) | Device | Frame |
|---|---|---|---|
| 0.16–1.20 | "Statue of Liberty…" | Hook: OZODLIK / HAYKALI behind the speaker, the O's are pipe rings | `examples/v2-sheet.jpg` #1–2 |
| 1.20–2.75 | "…symbol of New York" | Iris into AI hero insert of the statue | #3 |
| 2.84–3.74 | "weighs 200 t" | Slam "200" behind speaker + TONNA rise + hit shake | #4 |
| 3.74–7.74 | "30 t copper, the rest an iron frame" | Scan reveal into AI x-ray insert; "30 t / MIS QOBIQ" and "TEMIR KARKAS" in margins with leaders | `examples/v2-xray.jpg` |
| 7.74–9.80 | "if we turn that metal…" | Breathing punch-in 1.30→1.36 | — |
| 9.80–12.94 | "…into our 57×3 pipes" | Brand wipe → morph insert statue→pipes; engineering ring drawing Ø57 / 3 mm; fly into a pipe end | #8–10 |
| 12.94–16.6 | "4 200 pipes of 12 m" | Iris back to speaker; 4 200 motif rings fill the yard behind him; odometer 0→4 200 | `examples/t2-odo.jpg` |
| 16.6–23.2 | "joined: 50 km — longer than a marathon" | Footage shrinks into the plant pin on a brand-styled OSM map; camera pulls back to Tashkent; route draws; 50 KM plate; marathon mark at 42.2 km; +7,8 km in accent | `examples/v2-map.jpg` |
| 23.2–26.7 | "Tashkent TV tower weighs ≈ 30 statues" | Brand wipe → AI tower insert, title rise; tower shrinks aside, 30 statue silhouettes (cut from the x-ray still) pop in, ×30 | #19–20 |
| 26.7–28.06 | (rest of the sentence) | Breathing shot, slow push | — |
| 28.06–28.92 | "Can you imagine?" | Crash zoom + dark question above the head | `examples/t2-q.jpg` |
| 29.0–32.5 | "next post we'll calculate…" | End card over live footage: gradient, logo, slogan rise, double motif line | #22 |

**Generation:** 8 stills (gpt_image_2_5, high, 2k, 2.75 cr) → 4 i2v (kling3_0 pro, 5 s, silent, 8.75 cr) = 57 credits, no regeneration. One request came back as a preset recommendation and was declined.

**What the user corrected along the way** (encode these as defaults): wanted *more* creative motion than a cut-and-caption edit; banned whoosh/swish; wanted the distance on a *real* map starting from where the speaker stands; approximate geography is fine if stated.
