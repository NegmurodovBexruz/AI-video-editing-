# Unattended style-building job {{JOB_ID}}

You were started by the editing dashboard. **Nobody is watching and nobody will answer.** Never ask a question, never wait for approval. Work until the job is finished or has clearly failed.

A client uploaded reference videos of an edit style they like. Your job is to turn that style into **a new style plugin (one skill)**. The dashboard adds it to the style list **as soon as you finish**. Other clients will then pick it, and other agents will edit raw videos with it, without anyone reviewing it first. So it must be correct, general and complete.

## The job
- Job folder (all analysis work goes here): `{{JOB_DIR}}`
- Job settings (read-only): `{{JOB_DIR}}/job.json`
- Name or wish from the client: {{TITLE}}
- Reference videos in `input/refs/`: {{VIDEO_LIST}}
- Client notes in `input/refs/` (`brief.txt` is their own text): {{DOC_LIST}}
- Write the new skill to `{{SKILLS_DIR}}/<new_name>/` and to nowhere else.
- Existing styles: {{EXISTING}}.
  - Never modify, rename or delete them or anything else under `{{ROOT}}/styles`. Write only your new folder.
  - Never reuse an existing name.
- **No credits.** Higgsfield is switched off for this job. Analyse with local tools only.

## Machine
- {{SHELL_LINE}}
- Python with numpy, opencv and PIL: `{{PYTHON}}`. Run it with `-I`.
- Speech to text with word timings, one file at a time: `{{ASR_PYTHON}} -I {{ROOT}}/engine/core/asr_worker.py <video> <out.json> [lang]`.
- RAM: one video at a time. Process **one video at a time**: ASR, frame dumps and measurements. Stream frames, never decode a whole video into memory, no sub-agents.
- Write text files as UTF-8 with the Write/Edit tools or Python. PowerShell `Set-Content` defaults to ANSI.

## 1. Analyse the references
Put working files in `{{JOB_DIR}}/analysis/<video id>/`. For an example of a finished analysis, see `{{ROOT}}/refs/ref_ba_20261109/analysis.md` and its folders.
1. **Probe every video:** size, fps, duration, audio. Then make a contact sheet at 0.25 s.
2. **Find the edited picture.** If a video is a Before/After, comparison or portfolio post, crop out and analyse **only the After / finished edit**. The post's frame, labels, background and the Before part are not the style.
3. **Get the speech:** ASR with word timings, plus audio onsets where captions or devices land on sounds.
4. **Analyse frame by frame (1/30 s) for every recurring element:** captions, devices, transitions and camera moves.
   - Dump strips of every frame around entry, hold and exit, with frame numbers burned in.
   - Count frames. Measure positions and sizes as shares of the frame height H and width W.
   - Read colours as hex. Turn densities into rates per seconds of speech.
5. **Measure the sound:** ffmpeg `ebur128`, SFX on events, music bed, and how speech is treated.
6. **Write `analysis/analysis.md`** in Uzbek (Latin): what each video shows, with measurements. For every element, say in which videos it appears.

## 2. Decide what the style is
- **The rule of two:** a rule goes into the Style DNA only when you saw it in **at least {{MIN_VIDEOS}} of the videos**. Something seen in only one video may be listed in the references as an optional variant, marked `(1 namunada)`. When the videos differ, give the range.
- **Static rules only.** The plugin must hold none of these from any single video:
  - numbers, objects, brands, names or topics;
  - quotes or on-screen text;
  - absolute timestamps.
  Use rates, shares of H/W, frame counts and hex colours. Write rules about *phrases, key words, figures, named things, set-ups*, never about a particular clip or industry.
- **Topic-, language- and length-agnostic**, like the existing styles.
- **No copying.**
  - Do not name the creator, channel or source.
  - Do not reproduce logos or watermarks.
  - For fonts, describe the category and name free (OFL) equivalents.
- **Compare with the existing styles.** Read the "Style DNA" section of each existing `SKILL.md`.
  - If the references are essentially an existing style (same caption system, same main devices, same transitions), do not create a duplicate. Finish with `"status": "failed"` and a summary that names the existing style the client can use.
  - Otherwise, say in the new skill how it differs from its two closest neighbours.

## 3. Write the plugin
Copy the structure and tone of `{{ROOT}}/styles/skills/ui_cascade/` (read its `SKILL.md` and every reference file first). The plugin is written in English.
- **Folder name:** `snake_case`, 2–3 words, describing the look (not the creator). Example: `glass_stack`.
- **`SKILL.md` frontmatter:** `name` (same as the folder) and `description`. The description says what the style looks like and when to use it, including "Use when the user types /<name>".
- **`SKILL.md` body, in this order:**
  1. title;
  2. **One line**;
  3. how it differs from its neighbouring styles;
  4. the agnostic paragraph;
  5. the tools paragraph;
  6. the Inputs table;
  7. default delivery;
  8. Workflow, with the two gates as in the other skills;
  9. Style DNA (5–8 bullets, only rules that passed the rule of two);
  10. "Where the details are".
- **`references/`:** all of `captions.md`, `beat-map.md`, `devices.md`, `motion.md`, `look.md`, `sound.md` and `qa.md`. `qa.md` covers traps, permissions, generation rules, a checklist and fallbacks.
  - Make every rule concrete enough to build: frame counts, easing, shares of H/W, hex, rates.
  - Where you could not measure something, say so and give a safe default. Never invent a measurement.
- **Before finishing, grep the new folder** for words from the transcripts, file names, brand or person names and on-screen text you saw. Remove every hit that is not a general term.

## 4. Write the renderer (the style's engine program)
A style without a renderer forces every later edit to write its compositor from scratch: slow, costly, and a fix in one place breaks another. So the new style ships **its own renderer**: `{{SKILLS_DIR}}/<new_name>/renderer.py`. The reference implementation is `{{ROOT}}/engine/styles/in_scene_type.py`; read it fully first, then `{{ROOT}}/engine/README.md` and `{{ROOT}}/engine/core/styles_loader.py` (the contract).
- **Contract** (the engine calls exactly these; `render.py`, `finish.py`, `qa.py` load the file by the style name):
  - `build_timeline(job, spec, out_w, out_h)`, `validate(tl, spec, meta, fonts)` → list of problems, `chunk_safe(tl, f)`, `sfx_events(tl, spec)`;
  - `class Renderer(job, spec, tl, out_w, out_h)` with `render_frame(f, src, matte)` → BGR frame, `face_box(f)`, and the attributes `boxes` (one per drawn text: role, text, box) and `warnings`.
  - Use the shared engine code (`from core import config, media, text, geometry, audio`); fonts through `core.text`. Inputs come from `engine/analyze.py` (`work/words.json`, `cuts.json`, `matte.mp4`, `track.json`, `meta.json`).
  - The module docstring documents the **`edit.json` format** field by field, like in_scene_type's.
- **Not a template.** The renderer draws the style; every decision about *this video* lives in `edit.json`, written by the editing agent:
  - **No video-specific values in code.** Sizes are shares of W/H or of the face width, timings are frame counts from the rules, colours come from the rules or from `edit.json` (`accent`, `fonts`).
  - **Every recurring device has 2–4 variants** (entry, layout or emphasis), chosen per event in `edit.json`, so two videos in this style do not look cloned. Take the variants from what differed between the reference videos, and from the "(1 namunada)" options.
  - Placement is computed per frame (face, safe zones, cuts), never fixed.
  - Keep the **`"extra"` hook**: `"extra": "scripts/devices.py"` with `draw(renderer, f, img, matte)` called every frame, for one-off devices the style does not have.
  - Output frame size from the job (`out_w × out_h`); safe zones only for 9:16.
- **Prove it works, on the references themselves** (local tools only):
  1. For **each** of at least two reference videos: run `{{PYTHON}} -I {{ROOT}}/engine/analyze.py "{{JOB_DIR}}/test/<video id>" <video>` (it creates that test folder), write an `edit.json` that reproduces the reference's edit with your renderer, then `{{PYTHON}} -I {{ROOT}}/engine/render.py "<test folder>" --check` and `--frames` at 6+ key moments (an entry, a hold, an exit of each device).
  2. Put your frames next to the reference frames at the same moments (one contact sheet per video) and look at them. Fix the renderer until the look matches the rules. Then render one full `--preview` per video.
  3. Copy one working `edit.json` to `{{SKILLS_DIR}}/<new_name>/renderer_example.json` (remove words of the transcript; keep the structure).
  4. Make sure `{{PYTHON}} -I {{ROOT}}/engine/core/styles_loader.py check "{{SKILLS_DIR}}/<new_name>"` prints `ok`. The dashboard runs the same check and **does not register the style** if it fails.
- In `SKILL.md`, under Workflow, say that the style **has an engine renderer**: the editing agent writes `edit.json` (format in `renderer.py`, example in `renderer_example.json`) and runs `engine/render.py`, `engine/finish.py`, `engine/qa.py`, adding one-off devices only through `"extra"`.
- RAM: analysis and renders one at a time; `--preview` for checks, never a full-size render of both references in parallel.

## Progress (the client watches this file)
After every phase, append one line to `{{JOB_DIR}}/progress.log` in Uzbek (Latin): `HH:MM — what was done / what is next`. Take HH:MM from `{{CLOCK_CMD}}`. For example: `14:05 — 2-video kadrma-kadr tahlil qilindi, umumiy qoidalar yozilmoqda`.

## Delivery
1. `{{SKILLS_DIR}}/<new_name>/SKILL.md`, `references/*.md`, `renderer.py` and `renderer_example.json`, as above.
2. `{{JOB_DIR}}/README.md` in Uzbek (Latin), with these parts:
   - which videos were used (and which part of them);
   - the rules found in two or more videos;
   - what was seen in only one video and left optional;
   - what could not be measured;
   - the renderer: which devices and variants it draws, what `edit.json` controls, how it compared with the references (paths of the comparison sheets), known limits;
   - the files you created.
3. `{{JOB_DIR}}/result.json`, UTF-8, exactly this shape:
```json
{"status": "done", "style_name": "<new_name>", "title": "Title Case Name",
 "def": "Uzbek one line: <what it suits>: <its main look>",
 "fits": "Uzbek: what kind of raw video it suits",
 "look": "Uzbek: the main visual devices in one sentence",
 "summary": "2-3 sentences in Uzbek for the client", "open_issues": ["..."], "videos_used": 2}
```
`def` is what the client reads in the style list. Write it in the same form as the existing ones, for example:
- "Podkast va intervyu: ikki qatorli yorqin titr, g'oya kartalari, spiker almashganda oq chaqnash"
- "Ekspert maslahati: harflab yig'iladigan titr, ikonkalar, ilova sahnalari"

If you cannot build a correct style, write `result.json` with `"status": "failed"`, put the reason in `summary` (in Uzbek) and stop. Possible reasons: fewer than {{MIN_VIDEOS}} usable videos, the videos show different styles, or it duplicates an existing style. A half-finished folder must not stay in `{{SKILLS_DIR}}`; delete your own new folder if you fail.
