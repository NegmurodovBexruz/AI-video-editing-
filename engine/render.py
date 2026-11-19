"""Render the picture of an edit from <job>/edit.json with the style named in it.

usage:
  python -I engine/render.py <job> [--out work/picture.mp4] [--range F0 F1] [--preview] [--workers N|auto]
  python -I engine/render.py <job> --frames 120,340,900 --outdir work/qa_frames     (PNG stills)
  python -I engine/render.py <job> --check                                          (plan checks only)
--preview renders at 540x960 (about 3-4x faster) for checking timing and layout; the final is always full size.
"""
import argparse
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path

ENG = Path(__file__).resolve().parent
sys.path.insert(0, str(ENG))
import cv2  # noqa: E402

from core import config, media, styles_loader  # noqa: E402


def load(job, preview):
    spec = json.loads((Path(job) / "edit.json").read_text(encoding="utf-8"))
    st = styles_loader.load(spec["style"])
    W, H = (540, 960) if preview else (config.OUT_W, config.OUT_H)
    tl = st.build_timeline(job, spec, W, H)
    return spec, st, tl, W, H


def plates(job, f0):
    m = json.loads((Path(job) / "work" / "meta.json").read_text(encoding="utf-8"))
    wd = Path(job) / "work"
    return (media.frames(wd / "src30.mp4", m["work_w"], m["work_h"], "bgr24", start_frame=f0),
            media.frames(wd / "matte.mp4", m["matte_w"], m["matte_h"], "gray", start_frame=f0))


def render_range(job, preview, f0, f1, out, boxes_out):
    spec, st, tl, W, H = load(job, preview)
    f1 = min(f1, tl["n"] - 1)
    r = st.Renderer(job, spec, tl, W, H)
    src, mat = plates(job, f0)
    enc = media.encoder(out, W, H)
    t0, recs = time.time(), []
    for f in range(f0, f1 + 1):
        try:
            a, b = next(src), next(mat)
        except StopIteration:
            break
        fr = r.render_frame(f, a, b)
        enc.stdin.write(fr.tobytes())
        recs.append({"f": f, "b": [[x[0], x[1], *x[2]] for x in r.boxes], "face": [round(v) for v in r.face_box(f)]})
        if (f - f0) % 150 == 0:
            el = time.time() - t0
            print("frame %d/%d  %.2f s/frame" % (f, f1, el / max(1, f - f0)), flush=True)
    enc.stdin.close()
    enc.wait()
    with open(boxes_out, "w", encoding="utf-8") as fh:
        for rec in recs:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return r.warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--out", default=None)
    ap.add_argument("--range", nargs=2, type=int, default=None)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--workers", default="1")
    ap.add_argument("--boxes", default=None)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    job = Path(a.job)
    wd = job / "work"
    spec, st, tl, W, H = load(job, a.preview)
    meta = json.loads((wd / "meta.json").read_text(encoding="utf-8"))
    if a.check or (not a.frames and not a.range):
        from core import text as T
        F = {r: T.font_path(r, spec.get("fonts")) for r in T.FONT_FILES}
        problems = st.validate(tl, spec, meta, F)
        tl_out = {k: v for k, v in tl.items() if k != "words"}
        (wd / "timeline.json").write_text(json.dumps(tl_out, ensure_ascii=False), encoding="utf-8")
        print("plan checks:", "ok" if not problems else "")
        for p in problems:
            print("  -", p)
        if a.check:
            return
    if a.frames:
        r = st.Renderer(job, spec, tl, W, H)
        outdir = Path(a.outdir or wd / "qa_frames")
        outdir.mkdir(parents=True, exist_ok=True)
        for f in sorted(int(x) for x in a.frames.split(",")):
            s_, m_ = plates(job, f)
            fr = r.render_frame(f, next(s_), next(m_))
            cv2.imwrite(str(outdir / ("f%05d.png" % f)), fr)
        print("frames ->", outdir)
        return
    f0, f1 = a.range if a.range else (0, tl["n"] - 1)
    out = Path(a.out or (wd / ("preview.mp4" if a.preview else "picture.mp4")))
    boxes = Path(a.boxes or out.with_suffix(".boxes.jsonl"))
    nw = a.workers
    if nw == "auto":
        free = media.free_ram_gb()
        nw = 3 if free >= 8 else (2 if free >= 5 else 1)
    nw = max(1, int(nw))
    t0 = time.time()
    if nw == 1 or f1 - f0 < 200:
        warns = render_range(job, a.preview, f0, f1, out, boxes)
    else:
        step = (f1 - f0 + 1) // nw
        cuts = [f0]
        for k in range(1, nw):
            b = f0 + k * step
            while not st.chunk_safe(tl, b):
                b += 1
            cuts.append(b)
        cuts.append(f1 + 1)
        procs, parts = [], []
        for k in range(nw):
            part = wd / ("_part%d.mp4" % k)
            parts.append(part)
            cmd = [sys.executable, "-I", str(Path(__file__)), str(job), "--range", str(cuts[k]), str(cuts[k + 1] - 1),
                   "--out", str(part), "--boxes", str(part.with_suffix(".boxes.jsonl"))] + (["--preview"] if a.preview else [])
            procs.append(subprocess.Popen(cmd))
        codes = [p.wait() for p in procs]
        if any(codes):
            raise SystemExit("a render worker failed: %s" % codes)
        lst = wd / "_parts.txt"
        lst.write_text("".join("file '%s'\n" % p.as_posix() for p in parts), encoding="utf-8")
        media.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        with open(boxes, "w", encoding="utf-8") as fh:
            for p in parts:
                fh.write(p.with_suffix(".boxes.jsonl").read_text(encoding="utf-8"))
                p.with_suffix(".boxes.jsonl").unlink()
                p.unlink()
        lst.unlink()
        warns = []
    print("rendered %s in %.0f s (%d worker%s)" % (out, time.time() - t0, nw, "s" if nw > 1 else ""))
    for w in sorted(set(warns)):
        print("  !", w)


if __name__ == "__main__":
    main()
