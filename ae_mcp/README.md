# ae_mcp: After Effects MCP server (AP-1077)

The editing agent gets After Effects 2025 through three MCP tools. It builds motion-graphics devices (cards,
titles, counters, charts, maps, kinetic type) in AE instead of a Python compositor.

| Tool | What it does |
|---|---|
| `ae_run` | runs ExtendScript (ES3) against `<job>/ae/project.aep` (created when missing, saved after); `lib.jsx` helpers are loaded; returns `result`, `log`, the comps, and on error the message and the line in the agent's script |
| `ae_frames` | renders up to 12 frames of a comp to PNG (`comp.saveFrameToPng`, one AE launch) so the agent can look at them |
| `ae_render` | `aerender` → Lossless (with alpha) AVI → ffmpeg: H.264 `.mp4`, or ProRes 4444 `.mov` with alpha for compositing |

**How it runs.** Every call starts its own AE (`AfterFX.com -m -noui -r <script>`). The script writes a receipt
JSON, saves the project and AE exits, so nothing holds memory between calls. A call takes about 8–30 s
(reopening a saved project is the slow part).

**Guards**
- `job_dir` must lie under `AE_MCP_ROOTS` (the dashboard passes its jobs folder), and every file path stays inside the job folder.
- One AE at a time: a lock file in `%TEMP%`.
- An After Effects that the user opened is never touched. The call is refused, and on top of that a per-call token is checked inside AE.
- At least `AE_MIN_FREE_GB` (default 3) of free RAM is required.
- Timeouts: 15 min for a script, 2 h for a render.

**Dashboard wiring.**
- `config.AE_ENABLED` is on when `AfterFX.com` exists, on Windows only. `DASH_AE=0` turns it off; on Linux/Docker it is always off.
- `runner.build_cmd` writes `work/ae_mcp.json` and adds `--mcp-config` and the `mcp__ae__*` tools. Style-building jobs get none.
- The task has an "After Effects" section (`runner.AE_SECTION_ON`): one comp per device, alpha render, composite over the edit, and `ae_frames` before rendering.

**AE traps**
- `app.newProject()` crashes AE 2025 in `-noui` (exit `0xC0000409`). The server reuses the empty project AE starts with.
- Output-module templates in this install: `Lossless`, `Lossless with Alpha`, `High Quality`, `High Quality with Alpha`, `H.264 - Match Render Settings - 5/15/40 Mbps`, `Photoshop`, `TIFF Sequence with Alpha`. There is no PNG sequence template.
- The other traps are listed at the top of `lib.jsx`: `addProperty` invalidates references, text anchor, font fallback, parenting.
- Non-ASCII text (Uzbek) is escaped to `\uXXXX` automatically. Prefer passing it through `data`.

**Tests**
- `dashboard/dev/ae_mcp_check.py` checks the guards, the protocol and the runner wiring, without starting AE.
- Live smoke test, run by hand: `C:\Users\bexru\.claude\scratch_ap1077\mcp_drive.py <calls.json>` with `AE_MCP_ROOTS` set to a scratch folder.
- Verified on 2026-11-17: create, reopen, error line, path escape, 4 frames, mp4 and alpha mov. A headless `claude -p --mcp-config` called `ae_run` successfully.
