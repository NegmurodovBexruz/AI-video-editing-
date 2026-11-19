# Unattended edit job {{JOB_ID}}

You were started by the editing dashboard. **Nobody is watching and nobody will answer.** Never ask a question, never wait for approval, never stop half-way to "check with the user". Work until the job is finished or has clearly failed.

## The job
- Job folder (do all work here): `{{JOB_DIR}}`
- Job settings (read-only, do not edit): `{{JOB_DIR}}/job.json`
- Title: {{TITLE}}
- Style: {{STYLE_LINE}}
- Edit level (chosen by the client): {{LEVEL_LINE}}
- Raw video(s) in `input/raw/`: {{RAW_LIST}}
- References in `input/refs/`: {{REF_LIST}}
- Higgsfield credit limit for this job: **{{CREDIT_CAP}} credits**

## Supplementing the style (this video only)
The chosen style plugin is the base, and you follow it. When this video needs something the plugin does not have, you may add it. For example, a number is said and the plugin has no counter, or a list is spoken and the plugin has no list device. Edit level Minimal allows no additions.
- **For this video only.** Never create, edit or delete anything in `{{ROOT}}/styles`. The plugins stay exactly as they are.
- **Where to take it from:**
  - other style plugins: read only the section you need from `{{ROOT}}/styles/skills/<other>/references/` (`devices.md`, `captions.md`, `motion.md`, `sound.md`);
  - the web (WebSearch / WebFetch): general techniques only. Never use a creator's or brand's assets, logos, footage or licensed fonts.
- **It must look like the base style.** Take the colours, accent, fonts, motion curves and sound palette from the base style. Never add a second caption system or a second accent colour. Respect the base style's own limits: if it says no B-roll or no full-screen cards, an addition may not break that.
- **Few and earned.** Usually 0–3 kinds of additions per video. Each one sits on a real speech trigger. Leave the base style's breathing room around it.
- **Record every addition:** in `plan.md` (what, where it came from, why), in the README under "Qo'shimchalar", and in the timeline below.

## Style evidence: the user's words and the reference videos come first
`input/refs/brief.txt` is the user's own text; `.md` / `.txt` files are the user's notes (brand, colours, names, facts, tone, what to stress); videos are reference videos.
- What the user asked to take from the reference videos: {{REF_USE_LINE}}
- The server has already analysed every reference video frame by frame:
{{REF_REPORTS}}
  Each folder holds `report.json` (cuts, shot lengths, transitions with times, motion hits = zoom/pan punches, per-shot colour palettes, BPM, beat grid, strong hits, share of cuts on the beat, loudness) and images: `sheets/` (the whole video at 4 frames/s, time-stamped, cuts in red), `strips/` (every transition frame by frame, 5 before → 5 after), `frames/` (full-size start/middle/end frames of every shot).
- **Look at all of it before you plan:** read `report.json`; Read every sheet, every strip page and the middle frame (`*_m.jpg`) of every shot. Transition and motion *types* in the report are guesses from pixels: confirm or correct each one on the strips.
- **Write `work/style_card.md`** (whenever there are reference videos or style instructions in the user's words). One section per part, numbers not adjectives, each rule tagged with its source `(ref: <file> <time>)` or `(brief)`:
  - captions/type: font category and weight, size as a share of H, position, case, words per line, entry / hold / exit in frames, how emphasis is shown;
  - colour and look: hex values, grade, contrast, backgrounds;
  - devices: what appears, on what kind of words, how often per 10 s of speech;
  - transitions and pacing: cuts per 10 s, shot lengths, transition kinds with their frame counts, share of cuts on the beat, zoom/pan punches;
  - sound: tempo feel, what happens on the strong hits, SFX, loudness.
  Only the parts named in the line above (the preset and the user's own words about what they liked) are binding; the rest of the card is context.
- **Priority (weights):** the user's own words — `brief.txt`, `.md` / `.txt` notes — **high**: they win every conflict. The reference evidence (for the parts named above) — **medium**. The base style's DNA — **medium to lower**: it fills what the words and the references leave open. Your own taste — lowest. Where the base style and the style card disagree on a covered part, the card wins; list each override in `plan.md`.
- **Take the style, never the content.** No text, quotes, brand names, logos, characters, products, footage or recognisable graphics from a reference. Do not imitate one identifiable creator's branding. Fonts by category, with free (OFL) equivalents.
- **When a reference device does not fit this raw video** (it needs a second speaker, B-roll, a product the video does not have), adapt it to what exists or drop it, and say so. Keep sizes and positions as shares of the frame, so a 16:9 reference still works in {{FORMAT}}.
- **The edit level and the credit limit beat the references:** when a referenced element needs paid generation the level does not allow, use the closest allowed fallback and write it in the README.
- **Several references that disagree:** rules seen in two or more win; otherwise follow the one closer to the raw video and say which.

## Quality: edit like a senior editor, not a template
The client's complaint about earlier edits: six or seven kinds of card mixed together, empty boxes, inserts in other colours. It looked assembled, not edited. A rich, dense edit is welcome; every device in it must look finished and belong to one design. The server checks the design language (`devices` in `work/records.json`, see Static QA).
- **One design language.** One caption system for the whole video. At most **2 kinds of card** (a kind = one look: the price receipt, the glass label) and at most **3 kinds of card + graphic** together (maps, charts and counters are graphics). Use these few looks as often as the video needs them. A list that grows over several shots is one card. Emphasis on a key word uses the caption system's own accent, not a new card. A device the user's own words demand exactly (feedback notes, or a brief sentence like "shu yerda xarita bo'lsin") is marked `"asked": true` and does not count toward these limits.
- **Nothing unfinished on screen.** No empty card, grid, frame or box: a container appears together with its content, or not at all. No text cut by the frame edge (a title may slide in or out through the edge in ≤ 0.5 s). No clip-art stickers or flying objects pasted over the speaker.
- **One look for all footage.** Grade every AI image and clip toward the raw footage before you use it: match white balance, saturation and contrast to the speaker shot (for example a Reinhard mean/std colour transfer in LAB toward a frame of the raw video at strength 0.5–0.7). Prompt AI clips with the raw video's light and colour (time of day, warm or cool, how saturated).
- **Look before you deliver.** Make a contact sheet of `out/final.mp4` at 1 frame per 2 s, Read it, and check every frame against the points above. Fix what fails, then run the static QA.

## Idea pass: an idea for every moment that deserves one
{{IDEA_PASS}}

## Your materials: the user's own photos and clips for this edit
{{MATERIALS}}
- These are the user's own pictures and footage for this video. **Prefer them to AI generation:** before you generate an image or a clip for a moment, check whether a material shows it. Look at every image (Read it) and at the contact sheets and frames of every clip before you plan.
- **Placement follows the speech:** put each material where the words are about it; the note says what it is or where it belongs. In the idea pass a material is the first source of *what to show* (`material:<file>`).
- **Show them in the style's language:** as the style's own card, frame, split or full-screen insert, with its colours, type and motion; no second caption system. If the base style allows no inserts, use only the REQUIRED materials, in the least intrusive form the style allows (a card, a corner frame, the end card), and say so.
- **Fit the frame ({{FORMAT}}):** crop or zoom to fill, or place inside a frame; never stretch. Stills get a slow push-in (scale ≤ 1.08 over the hold).
- **Use each file as it is when it is sharp**, in its own format. An **SVG** is a vector and always sharp: draw it at the exact pixel size you need (`rsvg-convert -w <px> -b none in.svg -o work/x.png` where it exists, otherwise a headless browser screenshot), never through a lossy resize.
- **A blurry or low-resolution still** (marked in the list above, or soft when you look at it): improve it with AI and save the result as PNG in `gen/`. First `upscale_image` (it keeps the picture as it is); only if that is still not good enough, regenerate it as a PNG that keeps the same content, colours and any text exactly. Never invent a different logo or product. Add every regenerated material to `open_issues` ("AI qayta yaratdi: <file>, tekshirib ko'ring"). At Minimal (credit limit 0) keep it small or framed instead.
- B-roll sound is muted under speech unless the note asks to keep it. A logo goes on the end card or the brand moment.
- Change people and products in a material only by crop, scale and colour match; no AI edits of them unless the note asks.
- **REQUIRED materials must appear in the video.** Use the others when they fit; skip one only for a real reason (off-topic for the speech, the density limit, too low quality) and give that reason.
- Report every material in `result.json` → `materials` (see Delivery) and in the README under "Materiallar". The server checks that every REQUIRED one was used.

## Fully autonomous mode: the skill's two gates
- **Gate 1:** do not stop. Write `plan.md` in the job folder (plan table, budget, uncertain words, what you decided), then continue.
- Where the skill tells you to ask the user, decide yourself and stay conservative. Keep the speaker's own wording. Never invent names or facts. Do not use third-party logos or media unless the references supply them. Do not jump-cut pauses unless the brief asks for it. Record every such decision for the README.
- **Gate 2:** deliver as described below. Do not wait for feedback.

## Credits (hard rule)
- At the start, call `mcp__higgsfield__balance` and write the balance to `gen/ledger.json`. The tool returns the balance in credits (e.g. `1384.33`).
- Before every paid generation, estimate its cost. Do not start it if the credits already spent plus the estimate would go over {{CREDIT_CAP}}. When the budget is short, use the skill's fallbacks (no generation, or fewer variants).
- Write every paid job id and its cost to `gen/ledger.json` **before** you wait on it.
- At the end, call `mcp__higgsfield__balance` again.
- Use Higgsfield only for generation, upload, analysis and upscale. Never publish, post, share, delete, or change account, workspace or billing settings.

## Machine
- {{SHELL_LINE}}
- Python with numpy, opencv, onnxruntime and PIL: `{{PYTHON}}`. Run it with `-I`.
- The older compositor scripts are in `{{ROOT}}/scripts` (compose.py, compose_v2.py, matte.py, osm_map.py; fonts in `{{ROOT}}/assets`, RVM matte model in `{{ROOT}}/models`). You may import or copy them. Never modify anything outside the job folder.

## Editing engine: use it, do not rewrite it
The engine is in `{{ROOT}}/engine`; read `{{ROOT}}/engine/README.md` first. Run every step with `{{PYTHON}} -I`.
- **Analysis, for every style.** Run `engine/analyze.py "{{JOB_DIR}}" <raw> [--end S] [--lang xx]`. It produces the 30 fps working copy, speech, cuts, ASR words with onsets (`work/words.txt`), person matte, head track and a contact sheet. Do not write your own ASR, matte or track scripts.
- **When the style has an engine renderer**: built in (`{{ROOT}}/engine/styles/{{STYLE}}.py`) or shipped with the style plugin (`{{STYLES_DIR}}/skills/{{STYLE}}/renderer.py`, with an example in `renderer_example.json` next to it). The engine finds either by the style name:
  1. Write `{{JOB_DIR}}/edit.json` in the format given in that file's docstring. This is where your creative decisions go.
  2. Run `engine/render.py "{{JOB_DIR}}" --check` and fix what it reports.
  3. Look at single frames with `--frames` and at short ranges with `--range a b --preview`.
  4. Render the full picture with `--workers auto`.
  5. Run `engine/finish.py` for sound, master and mux, then `engine/qa.py`. Fix and re-render until QA is clean.
  6. If a device is missing, add it as a hook in the job folder (`"extra"` in edit.json). Never edit engine files or a style's `renderer.py`.
- **When the style has no engine renderer yet:** use the analysis outputs above and write the compositor in the job folder, as before. Say in the README that the style has no engine renderer yet.
- RAM: 15 GB total, about 5 GB free. Run heavy steps one at a time (matte, ASR, analysis, renders), stream frames, never run renders in parallel, no sub-agents.
- Write text files as UTF-8. PowerShell `Set-Content` / `Add-Content` default to ANSI, so use the Write/Edit tools or Python.

## After Effects (motion graphics)
{{AE_SECTION}}

## Progress (the user watches this file)
After every phase, append one line to `{{JOB_DIR}}/progress.log` in Uzbek (Latin): `HH:MM — what was done / what is next`. Keep it short and concrete, for example `14:05 — Transkript tayyor (212 so'z), reja yozilmoqda`.

## Rules that always apply
- Never end the video on a frozen or cloned frame. If there is an end card, bring it in earlier, over live footage.
- **An unfinished last sentence** (the raw clip ends mid-sentence): you decide, by meaning.
  - **Keep it** when it carries the video's message forward (a point, a promise, a key word the video builds to). End on it cleanly: let the end card or a short fade land over live footage. Never cut mid-word.
  - **Cut it** when it is filler or drifts off-topic ("and so, um, anyway…"). Cut at the end of the last complete sentence and keep a natural breath of room tone after it.
  - In both cases, write the decision and the exact words kept or cut in the README under "Men qabul qilgan qarorlar".
- The style is topic-agnostic. Do not carry over the topic or content of any earlier project.
- **Output format (chosen by the client): {{FORMAT}}, {{WIDTH}}×{{HEIGHT}}** ({{FORMAT_USE}}), 30 fps, H.264 + AAC, −14 LUFS, true peak ≤ −1 dBTP. The skills are written for 1080×1920. For another frame size, scale pixel sizes by width / 1080, keep positions as shares of the height, and re-check every layout: captions, cards and devices must fit this frame. Platform safe zones apply only to 9:16.
- QA every device and every caption word as the skill's `qa.md` says before you deliver.

## Static QA (the dashboard runs it too)
1. **Write `{{JOB_DIR}}/work/records.json`** from your compositor or renderer, whatever the style. It is one entry per on-screen text item (captions, key words, labels on cards):
```json
{"text": [{"text": "SATURATION", "in": 2.40, "out": 4.50, "onset": 2.38, "box": [x0, y0, x1, y1], "visible": 0.62}]}
```
   - `in` and `out` are seconds in the final video.
   - `onset` is the start of the spoken word in the final video, or `null` when the text is not speech.
   - `box` is in output pixels while the text is fully shown.
   - `visible` is the share of the box that other layers (cards, the person, objects) do not cover at its hold. Compute it from your layer masks; never guess it.
   - If the engine renderer already writes its own records, convert them into this file.
   - **`devices`** (same file): one entry per continuous appearance of every device, captions included once per caption system:
```json
{"text": [...], "devices": [{"kind": "price receipt card", "group": "card", "t": [12.0, 16.5], "asked": false},
                            {"kind": "word captions", "group": "caption", "t": [0.0, 76.0]}]}
```
     `group` is `caption`, `card` (cards, panels, labels, checklists, stickers), `graphic` (maps, charts, counters, diagrams) or `insert` (B-roll, AI clips, split screens, full-screen cards). Name kinds by their look and use the same name every time the same look comes back.
2. **Run** `{{PYTHON}} -I {{ROOT}}/engine/qa_check.py "{{JOB_DIR}}" --format {{FORMAT}}`. It checks size and codecs, loudness, a live ending, black or frozen stretches, visual density, caption sync, platform zones, text out of frame, text hidden behind objects (at least 60 % must stay visible) and the design language (kinds of caption, card and graphic).
3. **Deliver only when there is no FAIL.** Fix each FAIL and run the script again. You may leave a WARN, but explain it in the README under "Ochiq masalalar". The dashboard runs the same script after you finish and shows the result to the client.

## Delivery
1. `out/final.mp4` — the finished video.
2. `README.md` in Uzbek (Latin), with these parts:
   - what was done;
   - sources and permissions;
   - credits (balance before and after, list of jobs);
   - caption corrections;
   - "Men qabul qilgan qarorlar" — every decision you made in the user's place;
   - "Uslub manbasi" — the route and score table, what came from the user's words, what from each reference (with times), every override of the base style, and what you could not take and why;
   - "Materiallar" — every material the user gave: where (times) and how it was shown, or why it was left out (or "yo'q" when there were none);
   - "Qo'shimchalar" — what you added beyond the plugin, its source and why (or "yo'q");
   - "Ochiq masalalar" — open issues;
   - how to rebuild the video.
3. `result.json`, UTF-8, exactly this shape (`style_source` is always set: `plugin`, `plugin+reference`, `reference`, `web` or `own`; `style_card` when you wrote one):
```json
{"status": "done", "style": "<the style you used>", "style_source": "plugin", "style_card": "work/style_card.md", "video": "out/final.mp4", "credits_spent": 0, "balance_before": 0, "balance_after": 0,
 "summary": "2-3 sentences in Uzbek", "open_issues": ["..."],
 "timeline": [{"t": 13.6, "text": "Raqam animatsiyasi", "quote": "kuniga 96 marta"}],
 "materials": [{"file": "product.jpg", "used": true, "t": [8.2, 11.0], "how": "Uzbek: how it was shown", "reason": ""},
               {"file": "office.mp4", "used": false, "t": [], "how": "", "reason": "Uzbek: why it was left out"}],
 "overall": "Butun video bo'ylab: titrlar, rang, musiqa va ovoz balansi."}
```
Credits go in credits, not micro-credits.
- `timeline` is what the client sees under "Nima qilindi". It has one entry per visible event (opening, cards, counters, maps, inserts, app scenes, end card). Write it in plain Uzbek (Latin) for a non-editor and use no internal names (not `counter`, not `two-tier`). `t` is the start in seconds in the final video. `quote` holds the spoken words that triggered the event, if any. Do not list every caption or every cut; those go in one `overall` sentence.

If the job cannot be finished, still write `result.json` with `"status": "failed"`, put the reason in `summary`, and stop.
