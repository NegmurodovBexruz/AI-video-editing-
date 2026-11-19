"""Synthesised accent sounds (numpy only, no licences) and the final mix / loudness master / mux."""
import json
import wave
from pathlib import Path

import numpy as np

from . import media

SR = 48000


class Bank:
    def __init__(self, seed=7):
        self.rng = np.random.default_rng(seed)

    def bandnoise(self, n, lo, hi):
        x = self.rng.standard_normal(n).astype(np.float32)
        X = np.fft.rfft(x)
        fr = np.fft.rfftfreq(n, 1 / SR)
        X[(fr < lo) | (fr > hi)] = 0
        return np.fft.irfft(X, n).astype(np.float32)

    def sweepnoise(self, n, f0, f1):
        out = np.zeros(n, np.float32)
        blk = 960
        for b in range(0, n, blk):
            fc = f0 * (f1 / f0) ** (b / max(1, n - 1))
            seg = self.bandnoise(blk * 2, fc * 0.6, fc * 1.6)[:blk]
            out[b:b + blk] = seg[:len(out[b:b + blk])]
        return out

    @staticmethod
    def norm(x):
        return x / (np.abs(x).max() + 1e-9)

    def whoosh(self, length=0.25, f0=500, f1=3000):
        n = int(length * SR)
        return self.norm(self.sweepnoise(n, f0, f1) * np.sin(np.linspace(0, np.pi, n)) ** 2)

    def crinkle(self, length=0.32):
        n = int(length * SR)
        x = np.zeros(n, np.float32)
        for _ in range(int(length * 260)):
            i = self.rng.integers(0, max(1, n - 400))
            L = int(self.rng.integers(40, 380))
            x[i:i + L] += self.bandnoise(512, 2500, 11000)[:L] * np.exp(-np.linspace(0, 6, L)) * self.rng.uniform(0.3, 1)
        env = np.minimum(1, np.linspace(0, 6, n)) * np.exp(-np.linspace(0, 2.5, n))
        return self.norm((x + self.bandnoise(n, 1500, 9000) * 0.25) * env)

    def thump(self, length=0.35, f=72):
        n = int(length * SR)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.8 * np.exp(-t * 30))) / SR
        x = np.sin(ph) * np.exp(-t * 11)
        k = int(0.004 * SR)
        x[:k] *= np.linspace(0, 1, k)
        return self.norm(x.astype(np.float32))

    def scribble(self, length=0.45):
        n = int(length * SR)
        t = np.arange(n) / SR
        am = 0.55 + 0.45 * np.sin(2 * np.pi * 9 * t + 2 * np.sin(2 * np.pi * 3 * t))
        env = np.minimum(1, t / 0.03) * np.minimum(1, (length - t) / 0.08)
        return self.norm(self.bandnoise(n, 1800, 7000) * am * env)

    def shimmer(self, length=0.40):
        n = int(length * SR)
        t = np.arange(n) / SR
        x = np.zeros(n, np.float32)
        for fq in (1320, 1760, 2640, 3520):
            x += np.sin(2 * np.pi * fq * t + self.rng.uniform(0, 6)).astype(np.float32) * self.rng.uniform(0.5, 1)
        return self.norm((x * 0.35 + self.bandnoise(n, 4000, 12000) * 0.5) * (t / length) ** 2.2)

    def pop(self, length=0.08, f=900):
        n = int(length * SR)
        t = np.arange(n) / SR
        return self.norm((np.sin(2 * np.pi * f * t) * np.exp(-t * 60)).astype(np.float32))


# sound name -> (builder, default gain dB, lead s: the sound starts this much before the event time)
SOUNDS = {
    "whoosh": (lambda b, e: b.whoosh(e.get("length", 0.25), e.get("f0", 500), e.get("f1", 3000)), -28, 0.22),
    "whoosh_down": (lambda b, e: b.whoosh(e.get("length", 0.30), 2200, 400), -27, 0.0),
    "crinkle": (lambda b, e: b.crinkle(e.get("length", 0.32)), -24, 0.12),
    "thump": (lambda b, e: b.thump(e.get("length", 0.35), e.get("f", 72)), -22, 0.0),
    "scribble": (lambda b, e: b.scribble(e.get("length", 0.45)), -29, 0.0),
    "shimmer": (lambda b, e: b.shimmer(e.get("length", 0.40)), -26, 0.40),
    "pop": (lambda b, e: b.pop(), -30, 0.0),
}


def space_events(events, min_gap=1.5):
    """Keep accents >= min_gap s apart; higher priority wins (events carry 'prio', larger = more important)."""
    kept = []
    for e in sorted(events, key=lambda e: -e.get("prio", 0)):
        if all(abs(e["t"] - k["t"]) >= min_gap for k in kept):
            kept.append(e)
    dropped = [e for e in events if e not in kept]
    return sorted(kept, key=lambda e: e["t"]), dropped


def render_sfx(events, dur, out, seed=7):
    b = Bank(seed)
    mix = np.zeros((int(dur * SR) + SR, 2), np.float32)
    for e in events:
        build, gain, lead = SOUNDS[e["sound"]]
        sig = build(b, e)
        g = 10 ** (e.get("gain", gain) / 20)
        i = int((e["t"] - e.get("lead", lead)) * SR)
        if i < 0:
            sig, i = sig[-i:], 0
        n = min(len(sig), len(mix) - i)
        if n <= 0:
            continue
        pan = e.get("pan", 0.0)
        mix[i:i + n, 0] += sig[:n] * g * np.sqrt(0.5 * (1 - pan)) * 1.414
        mix[i:i + n, 1] += sig[:n] * g * np.sqrt(0.5 * (1 + pan)) * 1.414
    mix = mix[:int(dur * SR)]
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())


def finish(job, picture, events, out, bed=None, bed_db=-31.0, target=-14.0, tp_max=-1.0):
    """speech (+ sfx + optional ducked bed) -> loudness master -> mux with the picture -> out. Returns a report."""
    wd = Path(job) / "work"
    speech = wd / "speech.wav"
    dur = float(json.loads(media.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
                                      str(picture)]).stdout)["format"]["duration"])
    sfx = wd / "sfx.wav"
    render_sfx(events, dur, sfx)
    inputs = ["-i", str(speech), "-i", str(sfx)]
    fc = ("[0:a]aresample=48000,highpass=f=70,equalizer=f=6500:t=q:w=2:g=-1.5,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120[s];")
    if bed:
        inputs += ["-stream_loop", "-1", "-i", str(bed)]
        fc += ("[2:a]aresample=48000,volume=%.1fdB[bd];[s]asplit[s1][s2];"
               "[bd][s2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[bdk];"
               "[s1][1:a][bdk]amix=inputs=3:normalize=0:duration=first[m]" % (bed_db + 16))
    else:
        fc += "[s][1:a]amix=inputs=2:normalize=0:duration=first[m]"
    pre = wd / "mix_pre.wav"
    media.run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[m]", "-t", "%.3f" % dur,
               "-ac", "2", "-ar", "48000", "-c:a", "pcm_s24le", str(pre)])
    I, _ = media.loudness(pre)
    gain = target - (I if I is not None else target)
    limit = -1.6
    for attempt in range(3):
        mix = wd / "mix.wav"
        media.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre), "-af",
                   "volume=%.2fdB,alimiter=limit=%.4f:attack=3:release=60:level=disabled" % (gain, 10 ** (limit / 20)),
                   "-c:a", "pcm_s24le", str(mix)])
        media.run(["ffmpeg", "-v", "error", "-y", "-i", str(picture), "-i", str(mix), "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                   "-shortest", str(out)])
        fI, fTP = media.loudness(out)
        if fTP is not None and fTP > tp_max:
            limit -= (fTP - tp_max) + 0.3
            continue
        if fI is not None and abs(fI - target) > 0.5 and attempt < 2:
            gain += target - fI
            continue
        break
    return {"integrated_lufs": fI, "true_peak_dbtp": fTP, "gain_db": round(gain, 2), "limit_db": round(limit, 2),
            "sfx": events}
