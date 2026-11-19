"""Music analysis: onset envelope, tempo estimate, beat grid and strongest hits.  usage: python -I beats.py <audio> [out.json]"""
import json, subprocess, sys
import numpy as np

src = sys.argv[1]
sr = 22050
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32)
hop, win = 256, 1024
n = 1 + (len(x) - win) // hop
frames = np.lib.stride_tricks.as_strided(x, (n, win), (x.strides[0] * hop, x.strides[0]))
spec = np.abs(np.fft.rfft(frames * np.hanning(win), axis=1))
spec = np.log1p(spec * 10)
flux = np.maximum(np.diff(spec, axis=0), 0).sum(axis=1)
flux = np.concatenate([[0], flux])
flux = (flux - flux.mean()) / (flux.std() + 1e-9)
fps = sr / hop
# low band (kick) flux
freqs = np.fft.rfftfreq(win, 1 / sr)
low = np.maximum(np.diff(spec[:, freqs < 150], axis=0), 0).sum(axis=1)
low = np.concatenate([[0], low]); low = (low - low.mean()) / (low.std() + 1e-9)
# tempo by autocorrelation over 70..180 BPM
ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
lags = np.arange(len(ac))
bpm_range = (lags > fps * 60 / 180) & (lags < fps * 60 / 70)
lag = lags[bpm_range][np.argmax(ac[bpm_range])]
bpm = 60 * fps / lag
period = lag / fps
# phase: best offset maximising flux on grid
best, best_off = -1e9, 0
for off in np.arange(0, period, 0.005):
    idx = ((np.arange(off, len(flux) / fps, period)) * fps).astype(int)
    idx = idx[idx < len(flux)]
    s = flux[idx].sum()
    if s > best:
        best, best_off = s, off
grid = [round(float(t), 3) for t in np.arange(best_off, len(flux) / fps, period)]
# strongest hits
peaks = [i for i in range(2, len(flux) - 2) if flux[i] == flux[i - 2:i + 3].max() and flux[i] > 2.0]
hits = sorted(peaks, key=lambda i: -flux[i])[:25]
rms = np.sqrt((frames ** 2).mean(axis=1))
sec = [round(float(20 * np.log10(rms[int(t * fps):int((t + 1) * fps)].mean() + 1e-9)), 1) for t in range(int(len(x) / sr))]
out = {"bpm": round(float(bpm), 2), "beat_period": round(float(period), 4), "grid_offset": round(float(best_off), 3),
       "grid": grid, "strong_hits": sorted(round(i / fps, 3) for i in hits),
       "kick_hits": sorted(round(i / fps, 3) for i in range(2, len(low) - 2) if low[i] == low[i - 2:i + 3].max() and low[i] > 2.5),
       "rms_db_per_second": sec}
print(json.dumps({k: v for k, v in out.items() if k != "grid"}, indent=1))
if len(sys.argv) > 2:
    json.dump(out, open(sys.argv[2], "w"), indent=1)
