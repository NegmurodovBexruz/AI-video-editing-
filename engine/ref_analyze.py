r"""Deterministic reference-video analysis, run by the server before the idea agent (no credits, no Claude).

usage: python -I ref_analyze.py <video> <out_dir>

Writes into out_dir:
    report.json        cuts, shots (length, palette, motion), transitions (type guess), motion hits (zoom/pan punches),
                       audio (BPM, beats, strong hits, loudness, share of cuts on the beat), coverage stats
    sheets/sheet_NN.jpg   the whole video at 4 frames/s, 6x5 per sheet, time stamped, cuts marked red
    strips/strip_NN.jpg   every transition frame by frame (5 before .. 5 after), 4 transitions per page
    frames/shot_NN_{a,m,z}.jpg   full-size frames (long side <= 1080) from each shot: start, middle, end
One decode pass for analysis + one select pass for the full-size frames; frames are streamed (low RAM).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

AW = 160            # analysis width (px)
SW = 300            # sheet thumbnail width
STW = 200           # strip thumbnail width
SHEET_FPS = 4
STRIP_HALF = 5
MAX_FULL_FRAMES = 60
MAX_STRIPS = 32
HERE = Path(__file__).resolve().parent


def probe(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(v)],
                       capture_output=True, text=True, timeout=60)
    info = json.loads(r.stdout or "{}")
    vs = [s for s in info.get("streams", []) if s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic") != 1]
    if not vs:
        raise SystemExit("no video stream")
    s = vs[0]
    num, _, den = (s.get("avg_frame_rate") or s.get("r_frame_rate") or "30/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    return {"w": int(s["width"]), "h": int(s["height"]), "fps": round(fps, 3),
            "duration": float(info.get("format", {}).get("duration") or s.get("duration") or 0),
            "audio": any(x.get("codec_type") == "audio" for x in info.get("streams", []))}


def even(x):
    return max(2, int(round(x / 2.0)) * 2)


def decode(v, w, h):
    """Yield (index, frame at SW width, RGB) for every frame."""
    sh = even(h * SW / w)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(v), "-vf", "scale=%d:%d" % (SW, sh), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=10 ** 7)
    n, i = SW * sh * 3, 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield i, np.frombuffer(b, np.uint8).reshape(sh, SW, 3)
        i += 1
    p.stdout.close()
    p.wait()


def label(img, text, color=(255, 255, 255)):
    cv2.putText(img, text, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return img


def hist(rgb):
    h = cv2.calcHist([rgb], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]).ravel()
    return h / (h.sum() + 1e-9)


def tile(images, cols, pad=4, bg=(18, 18, 24)):
    if not images:
        return None
    h, w = images[0].shape[:2]
    rows = (len(images) + cols - 1) // cols
    out = np.full((rows * (h + pad) + pad, cols * (w + pad) + pad, 3), bg, np.uint8)
    for k, im in enumerate(images):
        r, c = divmod(k, cols)
        out[pad + r * (h + pad): pad + r * (h + pad) + h, pad + c * (w + pad): pad + c * (w + pad) + w] = im[:h, :w]
    return out


def save(path, rgb):
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])


def palette(pixels, k=5):
    px = pixels.reshape(-1, 3).astype(np.float32)
    if len(px) > 6000:
        px = px[np.random.default_rng(0).choice(len(px), 6000, replace=False)]
    k = min(k, len(px))
    _, lab, cen = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0), 2, cv2.KMEANS_PP_CENTERS)
    share = np.bincount(lab.ravel(), minlength=k) / len(lab)
    order = np.argsort(-share)
    return [{"hex": "#%02x%02x%02x" % tuple(int(c) for c in cen[i]), "share": round(float(share[i]), 2)} for i in order]


def analyse(v, out):
    v, out = Path(v), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    info = probe(v)
    fps = info["fps"] or 30.0
    sheet_step = max(1, int(round(fps / SHEET_FPS)))
    ah = even(info["h"] * AW / info["w"])
    yy, xx = np.mgrid[0:ah, 0:AW].astype(np.float32)
    rx, ry = xx - AW / 2, yy - ah / 2
    rr = np.sqrt(rx ** 2 + ry ** 2) + 1e-6

    lum, gdiff, hdiff, mag, zoom, panx, pany, hists, smalls = [], [], [], [], [], [], [], [], []
    sheet_thumbs, prev_g, prev_h = [], None, None   # sheet thumbs kept JPEG-encoded in memory (~20 KB each)
    for i, f in decode(v, info["w"], info["h"]):
        a = cv2.resize(f, (AW, ah), interpolation=cv2.INTER_AREA)
        g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
        hh = hist(a)
        lum.append(float(g.mean()))
        hists.append(hh)
        smalls.append(cv2.resize(a, (32, even(32 * ah / AW)), interpolation=cv2.INTER_AREA))
        if prev_g is None:
            gdiff.append(0.0); hdiff.append(0.0); mag.append(0.0); zoom.append(0.0); panx.append(0.0); pany.append(0.0)
        else:
            gdiff.append(float(np.abs(g.astype(np.int16) - prev_g).mean()))
            hdiff.append(float(0.5 * np.abs(hh - prev_h).sum()))
            fl = cv2.calcOpticalFlowFarneback(prev_g.astype(np.uint8), g, None, 0.5, 2, 9, 2, 5, 1.1, 0)
            fx, fy = fl[..., 0], fl[..., 1]
            mag.append(float(np.sqrt(fx ** 2 + fy ** 2).mean() / AW * 100))           # % of width per frame
            zoom.append(float(((rx * fx + ry * fy) / rr).mean() / (AW / 2) * 100))   # + = content moves outward = zoom in
            panx.append(float(fx.mean() / AW * 100)); pany.append(float(fy.mean() / AW * 100))
        prev_g, prev_h = g.astype(np.int16), hh
        if i % sheet_step == 0:
            sheet_thumbs.append((i, cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 85])[1]))
    n = len(lum)
    if n < 2:
        raise SystemExit("could not decode frames")
    T = lambda i: round(i / fps, 3)

    # ---- cuts (hard) ----
    hd, gd = np.array(hdiff), np.array(gdiff)
    cuts = []
    for i in range(1, n):
        lo, hi = max(1, i - 2), min(n, i + 3)
        if hd[i] > 0.38 and gd[i] > 10 and hd[i] >= hd[lo:hi].max() and (not cuts or i - cuts[-1] >= 3):
            cuts.append(i)
    # ---- soft transitions (dissolve / wipe / morph): big change over ~16 frames without a hard cut ----
    soft, W = [], 8
    H = np.array(hists)
    i = W
    while i < n - W:
        far = 0.5 * np.abs(H[i + W] - H[i - W]).sum()
        if far > 0.45 and not any(abs(i - c) <= W for c in cuts) and hd[i - W:i + W].max() < 0.38:
            soft.append(i)
            i += 2 * W
        else:
            i += 2
    L = np.array(lum)

    def kind(i, is_soft):
        win = L[max(0, i - 3): min(n, i + 4)]
        if win.max() > 225 and L[max(0, i - 6)] < 200:
            return "flash (oq chaqnash)"
        if win.min() < 18 and L[max(0, i - 6)] > 30:
            return "qora orqali"
        return "yumshoq (dissolve/wipe/morph)" if is_soft else "keskin kesim"
    trans = sorted([{"t": T(c), "frame": c, "type": kind(c, False)} for c in cuts] + [{"t": T(s), "frame": s, "type": kind(s, True)} for s in soft],
                   key=lambda x: x["frame"])

    # ---- motion hits (punch zooms, whips, shakes) away from cuts ----
    M, Z = np.array(mag), np.array(zoom)
    near_cut = np.zeros(n, bool)
    for c in cuts:
        near_cut[max(0, c - 1): c + 2] = True
    mm = M[~near_cut] if (~near_cut).any() else M
    thr = float(mm.mean() + 2 * mm.std())
    hits = []
    for i in range(2, n - 2):
        if not near_cut[i] and M[i] > thr and M[i] == M[i - 2:i + 3].max() and M[i] > 0.6:
            z, px, py = Z[i], panx[i], pany[i]
            kind_m = ("zoom in" if z > 0 else "zoom out") if abs(z) > max(abs(px), abs(py)) else ("pan/whip gorizontal" if abs(px) >= abs(py) else "pan/whip vertikal")
            hits.append({"t": T(i), "type": kind_m, "strength": round(float(M[i]), 2)})
    hits = sorted(hits, key=lambda x: -x["strength"])[:30]
    hits.sort(key=lambda x: x["t"])

    # ---- shots ----
    bounds = [0] + cuts + [n]
    shots, full_req = [], []
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        idx = np.linspace(a, b - 1, num=min(5, b - a)).astype(int)
        pix = np.concatenate([smalls[j].reshape(-1, 3) for j in idx])
        dur = (b - a) / fps
        shots.append({"n": k + 1, "start": T(a), "end": T(b), "dur": round(dur, 2), "palette": palette(pix),
                      "motion": round(float(M[a + 1:b].mean()) if b - a > 1 else 0.0, 2),
                      "zoom": round(float(Z[a + 1:b].mean()) if b - a > 1 else 0.0, 3)})
        want = [("m", (a + b - 1) // 2)] + ([("a", min(a + 2, b - 1)), ("z", max(b - 3, a))] if dur >= 1.0 else [])
        full_req.append((k + 1, want))
    # cap full-size frames: middles first, then starts/ends
    sel = [(s, tag, fr) for s, want in full_req for tag, fr in want if tag == "m"]
    extra = [(s, tag, fr) for s, want in full_req for tag, fr in want if tag != "m"]
    if len(sel) > MAX_FULL_FRAMES:
        sel = [sel[int(j)] for j in np.linspace(0, len(sel) - 1, MAX_FULL_FRAMES)]
    sel += extra[: max(0, MAX_FULL_FRAMES - len(sel))]
    sel.sort(key=lambda x: x[2])

    # ---- full-size frames: one select pass ----
    fdir = out / "frames"
    fdir.mkdir(exist_ok=True)
    for old in fdir.glob("*.jpg"):
        old.unlink()
    if sel:
        expr = "+".join("eq(n\\,%d)" % fr for _, _, fr in sel)
        scale = "scale='if(gt(iw,ih),min(1080,iw),-2)':'if(gt(iw,ih),-2,min(1080,ih))'"
        with tempfile.TemporaryDirectory(dir=str(out)) as td:   # same drive as out: Path.replace cannot cross drives
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vf", "select='%s',%s" % (expr, scale), "-fps_mode", "passthrough",
                            "-q:v", "3", str(Path(td) / "f_%04d.jpg")], check=True)
            made = sorted(Path(td).glob("f_*.jpg"))
            for (s, tag, fr), src in zip(sel, made):
                dst = fdir / ("shot_%02d_%s.jpg" % (s, tag))
                src.replace(dst)
                for sh in shots:
                    if sh["n"] == s:
                        sh.setdefault("frames", {})[{"a": "start", "m": "mid", "z": "end"}[tag]] = "frames/" + dst.name

    # ---- sheets (whole video, cuts marked) ----
    cutset = set(cuts)
    sdir = out / "sheets"
    sdir.mkdir(exist_ok=True)
    for old in sdir.glob("*.jpg"):
        old.unlink()
    thumbs = []
    for i, buf in sheet_thumbs:
        im = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)       # bytes hold RGB order (encoded as-is)
        cut_here = any(i - sheet_step < c <= i for c in cutset)
        if cut_here:
            cv2.rectangle(im, (0, 0), (im.shape[1] - 1, im.shape[0] - 1), (255, 40, 40), 4)
        thumbs.append(label(im, "%.2fs%s" % (i / fps, "  CUT" if cut_here else "")))
    per = 30
    sheets = []
    for k in range(0, len(thumbs), per):
        p = sdir / ("sheet_%02d.jpg" % (k // per + 1))
        save(p, tile(thumbs[k:k + per], 6))
        sheets.append("sheets/" + p.name)

    # ---- strips (each transition frame by frame) ----
    tdir = out / "strips"
    tdir.mkdir(exist_ok=True)
    for old in tdir.glob("*.jpg"):
        old.unlink()
    tsel = trans if len(trans) <= MAX_STRIPS else [trans[int(j)] for j in np.linspace(0, len(trans) - 1, MAX_STRIPS)]
    want = sorted({j for tr in tsel for j in range(tr["frame"] - STRIP_HALF, tr["frame"] + STRIP_HALF + 1) if 0 <= j < n})
    strip_store = {}
    if want:   # second pass: only the frames around transitions, at strip size
        sh = even(info["h"] * STW / info["w"])
        expr = "+".join("between(n\\,%d\\,%d)" % (tr["frame"] - STRIP_HALF, tr["frame"] + STRIP_HALF) for tr in tsel)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(v), "-vf", "select='%s',scale=%d:%d" % (expr, STW, sh), "-fps_mode", "passthrough",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=10 ** 7)
        size = STW * sh * 3
        for j in want:
            b = p.stdout.read(size)
            if len(b) < size:
                break
            strip_store[j] = np.frombuffer(b, np.uint8).reshape(sh, STW, 3).copy()
        p.stdout.close()
        p.wait()
    rows = []
    for tr in tsel:
        c = tr["frame"]
        row = []
        for j in range(c - STRIP_HALF, c + STRIP_HALF + 1):
            if 0 <= j < n and j in strip_store:
                im = strip_store[j].copy()
                label(im, "%+d  %.2fs" % (j - c, j / fps), (255, 80, 80) if j == c else (255, 255, 255))
                row.append(im)
        if row:
            rows.append((tr, row))
    strips = []
    for k in range(0, len(rows), 4):
        page = [im for _, row in rows[k:k + 4] for im in (row + [np.zeros_like(row[0])] * (2 * STRIP_HALF + 1 - len(row)))]
        p = tdir / ("strip_%02d.jpg" % (k // 4 + 1))
        save(p, tile(page, 2 * STRIP_HALF + 1))
        strips.append({"file": "strips/" + p.name, "transitions": [r[0]["t"] for r in rows[k:k + 4]]})
    strip_store.clear()

    # ---- audio ----
    audio = {"has_audio": info["audio"]}
    if info["audio"]:
        with tempfile.TemporaryDirectory() as td:
            wav, bj = Path(td) / "a.wav", Path(td) / "b.json"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(v), "-vn", "-ac", "1", "-ar", "22050", str(wav)], check=True)
            r = subprocess.run([sys.executable, "-I", str(HERE / "sound" / "beats.py"), str(wav), str(bj)], capture_output=True, text=True)
            if bj.exists():
                b = json.loads(bj.read_text())
                grid, strong = np.array(b["grid"] or [0.0]), np.array(b["strong_hits"] or [-9.0])
                ct = np.array([c / fps for c in cuts]) if cuts else np.array([])
                on_beat = float(np.mean([np.abs(grid - t).min() < 0.07 for t in ct])) if len(ct) else None
                on_hit = float(np.mean([np.abs(strong - t).min() < 0.07 for t in ct])) if len(ct) else None
                audio.update(bpm=b["bpm"], beat_period=b["beat_period"], grid_offset=b["grid_offset"], strong_hits=b["strong_hits"][:25],
                             cuts_on_beat=None if on_beat is None else round(on_beat, 2), cuts_on_strong_hit=None if on_hit is None else round(on_hit, 2),
                             rms_db_per_second=b["rms_db_per_second"])
            else:
                audio["beats_error"] = (r.stderr or "")[-300:]
        lr = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", str(v), "-vn", "-af", "ebur128", "-f", "null", "-"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lr.stderr)
        if m:
            audio["loudness_lufs"] = float(m[-1])

    # ---- report ----
    lens = np.array([s["dur"] for s in shots])
    dur = n / fps
    curve = [{"t": round(k / 10, 1), "motion": round(float(M[int(k / 10 * fps): int((k + 1) / 10 * fps)].mean()), 2),
              "lum": round(float(L[int(k / 10 * fps): int((k + 1) / 10 * fps)].mean()), 1)}
             for k in range(int(dur * 10)) if int(k / 10 * fps) < n]
    report = {
        "file": v.name, "width": info["w"], "height": info["h"], "fps": fps, "frames": n, "duration": round(dur, 2),
        "rhythm": {"cuts": len(cuts), "soft_transitions": len(soft), "cuts_per_10s": round(len(cuts) / dur * 10, 1) if dur else 0,
                   "shot_len_mean": round(float(lens.mean()), 2), "shot_len_median": round(float(np.median(lens)), 2),
                   "shot_len_min": round(float(lens.min()), 2), "shot_len_max": round(float(lens.max()), 2)},
        "transitions": [{k: x[k] for k in ("t", "type")} for x in trans],
        "motion_hits": hits, "shots": shots, "audio": audio,
        "motion_curve_10hz": curve,
        "images": {"sheets": sheets, "strips": strips, "frames": sorted("frames/" + p.name for p in fdir.glob("*.jpg"))},
        "coverage": {"sheet_fps": round(fps / sheet_step, 2), "sheet_frames": len(thumbs), "strip_transitions": len(rows),
                     "transitions_total": len(trans), "full_frames": len(list(fdir.glob("*.jpg"))), "whole_video": True},
        "notes": ("motion = optical flow, % of frame width per frame; zoom > 0 = zoom in. Transition and motion types are "
                  "guesses from pixels: confirm them on the strips and sheets."),
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    a = report["audio"]
    print("%s: %.1fs, %d cuts (%.1f/10s), %d soft, %d motion hits, %d sheets, %d strip pages, %d frames%s" % (
        v.name, dur, len(cuts), report["rhythm"]["cuts_per_10s"], len(soft), len(hits), len(sheets), len(strips),
        report["coverage"]["full_frames"], (", %.0f BPM" % a["bpm"]) if a.get("bpm") else ""))
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    analyse(sys.argv[1], sys.argv[2])
