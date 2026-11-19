# Motion

All counts at 30 fps. Easing: ease-out (cubic) for entries, ease-in for exits, unless noted.

| Element | Entry | Hold | Exit |
|---|---|---|---|
| Letter (cascade) | 2-frame stagger; each letter 4–5 frames: opacity 0 → 1, blur ~6 px → 0 (at 1080 wide), scale 1.1 → 1.0, tint → final colour | — | with its stack |
| Short word (1–2 letters) | 3 frames, whole | — | with its stack |
| Stack | builds word by word on onsets | until next phrase | 4 frames: fade + blur, 0.02 W drift up |
| Figure bar | width 0 → full in 8 frames (ease-in-out), from the left edge; text cascades after | with stack | with stack |
| Unit tag | 5 frames: blur + scale 0.8 → 1.0 | with stack | with stack |
| Headline | letter cascade; whole line drifts sideways 0.1–0.2 W/s, linear | until its phrase ends | 4-frame fade |
| Drop-cap letter | 5 frames: blur + fade; lines beside it cascade normally | with stack | with stack |
| Icon tile | 3-frame glow blob, then 4–6 frames: slide ~0.03 W, scale 0.9 → 1.0 | slow drift ≤ 0.01 W/s, glow pulse ±10 % every ~1 s | with stack or under a stutter |
| Card fan | rise 8–10 frames with motion blur, spread 8–10 frames with ~5 % overshoot | gentle float ≤ 0.005 H | sink 6 frames |
| Tool icon tile | 3D swing ≈30° → 0°, 6–8 frames | — | 1-frame swap to button |
| Button wiggle | "+" ↔ "×", 2 frames each, once | — | stays into the scene fade |
| Fade to white (into light scene) | 8 frames; UI title fades in over the last 3–4 | — | — |
| Dim to grey → dark scene | 6 frames dim, then cut | — | — |
| List item | slide 0.02 W from the left + fade, 4 frames, on its word | — | — |
| Checkbox tick | fill 3 frames, line dims to 60 % | — | — |
| Chat bubble | 3 frames as a horizontal motion-blur streak, then scale overshoot to ~1.06 and settle in 5–6 frames | — | — |
| Negative stutter | 5–7 frames total (see `devices.md`) | — | — |
| Bloom glitch | 5–6 frames | — | — |

## Camera

- No digital zoom pulses are needed; the energy is in the type.
- A slow push of ≤ 3 % per set-up is allowed.
- Do not stabilise away the speaker's natural movement.
