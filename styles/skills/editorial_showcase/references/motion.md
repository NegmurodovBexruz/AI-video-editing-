# Motion defaults

Frame counts below assume 30 fps. Preserve durations in seconds at another output rate. These are authored defaults for the combined style; adjust for speech, reading time and source movement.

| Action | Duration / shape |
|---|---|
| Supporting-caption entry | 4–6 f, small rise + opacity + blur-to-sharp, ease-out |
| Supporting-caption exit | 3–5 f, small downward offset + fade; overlap limited by `captions.md` |
| Heading/accent entry | 6–10 f, restrained offset/fade; accent follows its own spoken cue |
| Message card | 8–12 f from 0.90–0.95 scale to 1.0, fade; no overshoot required |
| Lower-demo entry | 12–24 f vertical slide, ease-out; longer only if the layout needs reading time |
| Composition into phone/screen | 10–16 f uniform shrink; frame and content remain registered |
| Perspective panel handoff | 18–30 f total; mild pullback, yaw generally within 10–20 degrees, push to flat final view |
| Document page change | Hard cut or 6–10 f zoom-blur; never blur the only readable hold |
| Paper drift | Continuous gentle pan/scale, around 2–5% per second; slower for longer terms |
| Return to presenter | Hard cut by default; optional small roll up to 3 degrees settling over 8–12 f |

Use ease-out for arrivals, ease-in for departures and a smooth ease-in-out for camera travel. Ease curves are implementation choices, not inferred original settings.

Only one large spatial transition at a section boundary. Do not combine a flash, panel carousel, zoom blur and camera roll on the same cut. No full-white flash is required by this style. A clean cut is preferable when a transition interrupts reading or covers a key word.

## Rendering contract

- All animation derives from the composition's timeline, not wall-clock time or accumulated playback state.
- Clip visibility is explicit before/after its interval; seeking must not reveal the first visible keyframe early.
- Use fixed source times/crops for media and deterministic seeds for any texture. Scrubbing to a frame must reproduce the export.
- Apply safe-zone checks after parent camera/panel transforms. Test the transition at entry, middle and exit; verify no gap, doubled frame or stale caption.
- Preserve real motion at the end. Check the last two seconds at the actual delivered frame rate, allowing expected source-rate frame repeats without creating a frozen hold.
