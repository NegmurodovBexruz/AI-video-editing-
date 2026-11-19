r"""Reference vs result contact sheet: does the finished video look like the references it was meant to follow?

usage: python -I ref_compare.py <job_dir> [--video out/final.mp4]
Reads <job>/work/refs/<ref>/report.json (written by ref_analyze.py) and the final video, writes
<job>/work/ref_compare.jpg: one row per sampled moment, the reference frame on the left, the result at the same
relative position of the film on the right, both labelled. Rows are matched by position (10 %, 25 %, ...),
not by content, so the sheet shows look (type, colour, layout, density), not a shot-by-shot copy.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

POS = (0.08, 0.25, 0.42, 0.58, 0.75, 0.92)
TILE_H = 420


def frame_at(video, t):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "f.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % t, "-i", str(video), "-frames:v", "1", "-q:v", "3", str(p)])
        return cv2.imread(str(p)) if p.exists() else None


def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def fit(img, h=TILE_H):
    if img is None:
        img = np.zeros((h, int(h * 9 / 16), 3), np.uint8)
    return cv2.resize(img, (max(1, int(img.shape[1] * h / img.shape[0])), h), interpolation=cv2.INTER_AREA)


def label(img, text):
    cv2.putText(img, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def ref_frame(ref_dir, rep, pos):
    """The shot that covers this position: its middle frame (full size, written by ref_analyze)."""
    t = pos * rep["duration"]
    shot = next((s for s in rep["shots"] if s["start"] <= t < s["end"]), rep["shots"][-1])
    p = (shot.get("frames") or {}).get("mid")
    return (cv2.imread(str(ref_dir / p)) if p else None), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--video", default="out/final.mp4")
    a = ap.parse_args()
    job = Path(a.job)
    video = job / a.video
    refs = sorted(p.parent for p in (job / "work" / "refs").glob("*/report.json"))
    if not refs or not video.exists():
        raise SystemExit("nothing to compare (no reference analysis or no video)")
    dur = duration(video)
    rows = []
    for i, pos in enumerate(POS):
        rd = refs[i % len(refs)]                       # several references: take turns
        rep = json.loads((rd / "report.json").read_text(encoding="utf-8"))
        rimg, rt = ref_frame(rd, rep, pos)
        oimg = frame_at(video, pos * dur)
        left = label(fit(rimg), "REF %s  %.1fs" % (rep["file"][:22], rt))
        right = label(fit(oimg), "NATIJA  %.1fs" % (pos * dur))
        gap = np.full((TILE_H, 12, 3), 24, np.uint8)
        rows.append(np.hstack([left, gap, right]))
    w = max(r.shape[1] for r in rows)
    rows = [np.hstack([r, np.full((TILE_H, w - r.shape[1], 3), 24, np.uint8)]) if r.shape[1] < w else r for r in rows]
    sep = np.full((10, w, 3), 24, np.uint8)
    sheet = np.vstack([x for r in rows for x in (r, sep)][:-1])
    out = job / "work" / "ref_compare.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(out)


if __name__ == "__main__":
    main()
