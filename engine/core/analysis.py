"""Analysis steps shared by all styles. Each step reads/writes files in <job>/work and can be re-run alone.

prepare  -> work/src30.mp4 (30 fps working copy), work/speech.wav, work/meta.json
cuts     -> work/cuts.json      (hard cuts inside the take, frame indices)
asr      -> work/words_raw.json (faster-whisper large-v3, or an imported transcript)
onsets   -> work/words.json     (every word snapped to its audible onset)
matte    -> work/matte.mp4      (person alpha, RVM)
track    -> work/track.json     (zero-lag head track per frame, normalised to the working copy)
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

from . import config, media


def _w(job):
    d = Path(job) / "work"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_meta(job):
    return json.loads((_w(job) / "meta.json").read_text(encoding="utf-8"))


def _even(x):
    return int(round(x / 2)) * 2


# ---------------------------------------------------------------- prepare

def prepare(job, raw, start=0.0, end=None):
    wd = _w(job)
    p = media.probe(raw)
    end = p["duration"] if end is None else min(end, p["duration"])
    h = min(p["h"], config.WORK_MAX_H)
    w = _even(p["w"] * h / p["h"])
    h = _even(h)
    seg = ["-ss", "%.3f" % start, "-to", "%.3f" % end]
    media.run(["ffmpeg", "-v", "error", "-y"] + seg + ["-i", str(raw), "-vf",
               "fps=%d,scale=%d:%d:flags=lanczos" % (config.FPS, w, h),
               "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p", "-an",
               str(wd / "src30.mp4")])
    if p["has_audio"]:
        media.run(["ffmpeg", "-v", "error", "-y"] + seg + ["-i", str(raw), "-vn", "-ac", "2", "-ar", "48000",
                   "-c:a", "pcm_s16le", str(wd / "speech.wav")])
    n = int(media.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                       "stream=nb_read_packets", "-of", "csv=p=0", str(wd / "src30.mp4")]).stdout.strip())
    meta = {"raw": str(raw), "src": p, "start": start, "end": end, "fps": config.FPS,
            "work_w": w, "work_h": h, "n": n, "has_audio": p["has_audio"]}
    warn = []
    if p["h"] < 1920:
        warn.append("source is %dx%d: below 1080x1920, punches will look soft" % (p["w"], p["h"]))
    if abs(p["w"] / p["h"] - 9 / 16) > 0.02:
        warn.append("source aspect %.3f is not 9:16: the frame is cover-cropped around the head" % (p["w"] / p["h"]))
    if (p.get("color_transfer") or "") in ("arib-std-b67", "smpte2084") or "log" in str(p.get("pix_fmt")):
        warn.append("source may be HDR/LOG (%s): grade it before the edit" % p.get("color_transfer"))
    if abs(p["fps"] - config.FPS) > 0.05 and abs(p["fps"] * 2 - config.FPS) > 0.05 and abs(p["fps"] - 2 * config.FPS) > 0.05:
        warn.append("source %.3f fps -> 30 fps by frame repeat/drop (no interpolation)" % p["fps"])
    meta["warnings"] = warn
    (wd / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return meta


# ---------------------------------------------------------------- cuts

def cuts(job):
    """Hard cuts: a frame-difference spike well above the clip's motion and >= 3x the frames just before it.
    Repeated frames (fps conversion) give zero differences, so the statistics use non-zero ones; the spike is
    compared with the frames before it only, because motion after a cut is often high too."""
    wd, m = _w(job), load_meta(job)
    pw = 90
    ph = _even(pw * m["work_h"] / m["work_w"])
    prev, d = None, []
    for fr in media.frames(wd / "src30.mp4", pw, ph, "gray", scale="area"):
        f = fr.astype(np.float32)
        d.append(0.0 if prev is None else float(np.abs(f - prev).mean()))
        prev = f
    d = np.array(d)
    nz = d[d > 0.3]
    med = float(np.median(nz)) if len(nz) else 0.0
    mad = float(np.median(np.abs(nz - med))) if len(nz) else 0.0
    thr = max(8.0, med + 6 * mad)
    out = []
    for k in range(1, len(d)):
        pre = float(np.median(d[max(1, k - 4):k])) if k > 1 else 0.0
        nxt = d[k + 1] if k + 1 < len(d) else 0.0
        if d[k] > thr and d[k] > 3 * max(pre, 1.0) and d[k] > 1.3 * nxt:
            if not out or k - out[-1] > 3:
                out.append(k)
    res = {"cuts": out, "times": [round(k / config.FPS, 3) for k in out], "threshold": round(thr, 2)}
    (wd / "cuts.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


# ---------------------------------------------------------------- asr

def asr(job, lang=None, model="large-v3", words_file=None):
    """Transcribe with faster-whisper, or import a transcript (our format or ElevenLabs Scribe)."""
    wd, m = _w(job), load_meta(job)
    out = wd / "words_raw.json"
    if words_file:
        d = json.loads(Path(words_file).read_text(encoding="utf-8"))
        ws = d["words"] if isinstance(d, dict) else d
        words = []
        for w in ws:
            if "start_us" in w:          # ElevenLabs Scribe
                t = (w.get("text") or "").strip()
                if not t or w.get("type") in ("spacing", "audio_event"):
                    continue
                s, e = w["start_us"] / 1e6, w["end_us"] / 1e6
            else:
                t, s, e = w["word"].strip(), float(w["start"]), float(w["end"])
            s, e = s - m["start"], e - m["start"]           # to the trimmed clock
            if e <= 0 or s >= m["end"] - m["start"] or not t:
                continue
            words.append({"word": t, "start": round(max(0, s), 3), "end": round(e, 3), "p": w.get("p", 1.0)})
        lang_ = (d.get("language") if isinstance(d, dict) else None) or lang
        out.write_text(json.dumps({"language": lang_, "model": "imported", "words": words}, ensure_ascii=False,
                                  indent=1), encoding="utf-8")
        return len(words)
    if not config.ASR_PYTHON.exists():
        raise RuntimeError("ASR python not found: %s (set ENGINE_ASR_PYTHON)" % config.ASR_PYTHON)
    src = wd / "speech.wav"
    subprocess.run([str(config.ASR_PYTHON), "-I", str(Path(__file__).with_name("asr_worker.py")), str(src),
                    str(out), lang or "auto", model], check=True)
    return len(json.loads(out.read_text(encoding="utf-8"))["words"])


# ---------------------------------------------------------------- onsets

def onsets(job):
    """Snap each ASR word start to the nearest spectral-flux onset in [start-0.15, start+0.10]."""
    wd = _w(job)
    SR = 16000
    pcm = media.run(["ffmpeg", "-v", "error", "-i", str(wd / "speech.wav"), "-ac", "1", "-ar", str(SR),
                     "-f", "f32le", "-"]).stdout
    x = np.frombuffer(pcm, np.float32)
    hop, win = 160, 512
    n = max(0, (len(x) - win) // hop)
    peaks_t, flux = np.array([]), np.zeros(1)
    if n > 5:
        # chunked STFT keeps memory flat for long clips
        flux = np.zeros(n, np.float32)
        db = np.zeros(n, np.float32)
        freqs = np.fft.rfftfreq(win, 1 / SR)
        band = (freqs >= 80) & (freqs <= 4000)
        prev = None
        hann = np.hanning(win).astype(np.float32)
        for a in range(0, n, 4000):
            b = min(n, a + 4000)
            idx = np.arange(win)[None, :] + hop * np.arange(a, b)[:, None]
            fr = x[idx] * hann[None, :]
            lm = np.log1p(100 * np.abs(np.fft.rfft(fr, axis=1))[:, band])
            first = lm[:1] if prev is None else prev
            flux[a:b] = np.maximum(0, np.diff(lm, axis=0, prepend=first)).sum(axis=1)
            db[a:b] = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1) + 1e-10) + 1e-6)
            prev = lm[-1:]
        flux = flux / (np.percentile(flux, 99) + 1e-9)
        pk = [k for k in range(2, n - 2) if flux[k] >= 0.12 and flux[k] == flux[k - 2:k + 3].max()
              and db[min(n - 1, k + 2)] > db.max() - 40]
        peaks_t = np.array(pk) * hop / SR + 0.010
    words = json.loads((wd / "words_raw.json").read_text(encoding="utf-8"))["words"]
    res, last = [], -1.0
    for i, w in enumerate(words):
        s = w["start"]
        cand = peaks_t[(peaks_t >= s - 0.15) & (peaks_t <= s + 0.10) & (peaks_t > last + 0.06)] if len(peaks_t) else []
        if len(cand):
            near = cand[np.argsort(np.abs(cand - s))[:2]]
            st = [flux[min(len(flux) - 1, int(round((t - 0.010) * SR / hop)))] for t in near]
            on = float(near[int(np.argmax(st))])
            if abs(near[0] - s) < abs(on - s) and max(st) < 1.6 * st[0]:
                on = float(near[0])
            src = "flux"
        else:
            on, src = max(s, last + 0.06), "asr"
        on = round(on, 3)
        res.append({"i": i, "word": w["word"], "asr": s, "onset": on, "end": w["end"], "src": src,
                    "p": w.get("p", 1.0)})
        last = on
    (wd / "words.json").write_text(json.dumps(res, ensure_ascii=False, indent=0), encoding="utf-8")
    return sum(r["src"] == "flux" for r in res), len(res)


# ---------------------------------------------------------------- matte

def matte(job):
    import onnxruntime as ort
    wd, m = _w(job), load_meta(job)
    mh = min(config.MATTE_H, m["work_h"])
    mw = _even(m["work_w"] * mh / m["work_h"])
    so = ort.SessionOptions()
    so.intra_op_num_threads = 6
    sess = ort.InferenceSession(str(config.RVM_MODEL), so, providers=["CPUExecutionProvider"])
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    ratio = np.array([0.4 if mh >= 1000 else 0.6], np.float32)
    enc = media.encoder(wd / "matte.mp4", mw, mh, fmt="gray", crf=6, preset="medium")
    k = 0
    for fr in media.frames(wd / "src30.mp4", mw, mh, "rgb24", scale="area"):
        src = fr.transpose(2, 0, 1)[None].astype(np.float32) / 255
        _, pha, *rec = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                                       "downsample_ratio": ratio})
        enc.stdin.write((pha[0, 0] * 255).clip(0, 255).astype(np.uint8).tobytes())
        k += 1
    enc.stdin.close()
    enc.wait()
    m.update(matte_w=mw, matte_h=mh)
    (wd / "meta.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    return k


# ---------------------------------------------------------------- head track

def _interp(v):
    v = np.array(v, float)
    ok = ~np.isnan(v)
    if ok.sum() == 0:
        return v
    i = np.arange(len(v))
    return np.interp(i, i[ok], v[ok])


def _smooth(v):
    """Centred median-5 then centred mean-3: removes detector jitter, no lag."""
    n = len(v)
    a = np.array([np.median(v[max(0, i - 2):min(n, i + 3)]) for i in range(n)])
    return np.array([a[max(0, i - 1):min(n, i + 2)].mean() for i in range(n)])


def track(job):
    """Head per frame from the person matte (top, head run) + Haar face box; zero-lag smoothing per shot.
    Output values are normalised to the working copy (x / width, y / height); fw = face width / width."""
    import cv2
    wd, m = _w(job), load_meta(job)
    W = config.TRACK_W
    H = _even(W * m["work_h"] / m["work_w"])
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    prof = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    mins = int(0.12 * W)
    rows = []
    for i, (img, mt) in enumerate(zip(media.frames(wd / "src30.mp4", W, H, "gray", scale="area"),
                                      media.frames(wd / "matte.mp4", W, H, "gray", scale="area"))):
        a = mt > 128
        ys = np.where(a.any(axis=1))[0]
        rec = {"f": i}
        if len(ys):
            top = int(ys[0])
            band = a[top:top + max(2, int(0.10 * H))]
            r = min(H - 1, top + int(0.07 * H))
            rc = np.where(a[r])[0]
            if len(rc) and band.any():
                cx = float(np.mean(np.where(band)[1]))
                runs = np.split(rc, np.where(np.diff(rc) > 1)[0] + 1)
                run = min(runs, key=lambda q: abs((q[0] + q[-1]) / 2 - cx))
                rec.update(top=top / H, mcx=cx / W, hw=(run[-1] - run[0] + 1) / W, hl=run[0] / W, hr=run[-1] / W)
            rec["cov"] = float(a.mean())
        eq = cv2.equalizeHist(img)
        faces = casc.detectMultiScale(eq, 1.1, 5, minSize=(mins, mins))
        if len(faces) == 0:
            faces = prof.detectMultiScale(eq, 1.1, 4, minSize=(mins, mins))
            if len(faces) == 0:
                ff = prof.detectMultiScale(cv2.flip(eq, 1), 1.1, 4, minSize=(mins, mins))
                faces = [(W - x - w, y, w, h) for (x, y, w, h) in ff]
        if len(faces):
            x, y, w, h = max(faces, key=lambda q: q[2] * q[3])
            rec.update(fx=(x + w / 2) / W, fy=(y + h / 2) / H, fw=w / W, fh=h / H)
        rows.append(rec)
    (wd / "track_raw.json").write_text(json.dumps(rows), encoding="utf-8")

    N = len(rows)
    cj = json.loads((wd / "cuts.json").read_text(encoding="utf-8")) if (wd / "cuts.json").exists() else {"cuts": []}
    bounds = sorted(set([0] + [c for c in cj["cuts"] if 0 < c < N] + [N]))
    hx, hy, fw = (np.full(N, np.nan) for _ in range(3))
    mcx, top, mhw = (np.full(N, np.nan) for _ in range(3))
    ar = H / W
    for r in rows:
        i = r["f"]
        if "mcx" in r:
            mcx[i], top[i], mhw[i] = r["mcx"], r["top"], r["hw"]
        # a Haar box is a face only if it sits on the matte's head: same x, just under the head top, not wider
        # than the head (clasped hands at chest height also fire the detector)
        if ("fx" in r and "mcx" in r and abs(r["fx"] - r["mcx"]) < 0.10 and 0.08 < r["fw"] < 0.85
                and 0 < r["fy"] - r["top"] < 1.3 * r["hw"] / ar and r["fw"] < 1.7 * r["hw"]):
            hx[i], hy[i], fw[i] = r["fx"], r["fy"], r["fw"] * 0.80     # Haar box is wider than the face
    HX, HY, FW = np.zeros(N), np.zeros(N), np.zeros(N)
    shots = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        sx, sy, sw = hx[a:b].copy(), hy[a:b].copy(), fw[a:b].copy()
        mx, mt_, mw = _interp(mcx[a:b]), _interp(top[a:b]), _interp(mhw[a:b])
        haar = float(np.mean(~np.isnan(sx)))
        if np.isnan(sx).all():
            if np.isnan(mx).all():            # no person at all in this shot
                mx, mt_, mw = np.full(b - a, 0.5), np.full(b - a, 0.25), np.full(b - a, 0.3)
            sx, sw = mx.copy(), mw * 0.80
            sy = mt_ + 0.55 * sw / ar          # face centre ~0.55 face widths below the head top
        else:
            off_y = np.nanmedian(sy - mt_)
            for k in range(len(sx)):
                if np.isnan(sx[k]):
                    sx[k], sy[k], sw[k] = mx[k], mt_[k] + off_y, np.nan
            for k in range(1, len(sx)):
                if abs(sx[k] - sx[k - 1]) > 0.06 or abs(sy[k] - sy[k - 1]) > 0.06 / ar:
                    sx[k], sy[k] = np.nan, np.nan
            sx, sy = _interp(sx), _interp(sy)
            sw = _interp(sw) if not np.isnan(sw).all() else mw * 0.80
        HX[a:b], HY[a:b], FW[a:b] = _smooth(sx), _smooth(sy), _smooth(sw)
        shots.append({"f0": int(a), "f1": int(b), "haar": round(haar, 3),
                      "hx": [round(float(HX[a:b].min()), 3), round(float(HX[a:b].max()), 3)],
                      "fw": round(float(FW[a:b].mean()), 3)})
    res = {"n": N, "bounds": bounds, "shots": shots,
           "hx": [round(float(v), 4) for v in HX], "hy": [round(float(v), 4) for v in HY],
           "fw": [round(float(v), 4) for v in FW],
           "hl": [r.get("hl") for r in rows], "hr": [r.get("hr") for r in rows], "top": [r.get("top") for r in rows]}
    (wd / "track.json").write_text(json.dumps(res), encoding="utf-8")
    return shots
