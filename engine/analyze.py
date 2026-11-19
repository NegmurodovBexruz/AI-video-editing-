"""Analyse a raw clip for any style. Steps run one after another (RAM), each can be re-run alone.

usage:
  python -I engine/analyze.py <job> <raw.mp4> [--start S] [--end S] [--lang en] [--words transcript.json]
                              [--steps prepare,cuts,asr,onsets,matte,track,sheet]
Outputs in <job>/work: meta.json, src30.mp4, speech.wav, cuts.json, words_raw.json, words.json, words.txt,
matte.mp4, track.json, sheet.png (1 frame per second, for planning).
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import analysis, media  # noqa: E402

ALL = ["prepare", "cuts", "asr", "onsets", "matte", "track", "sheet"]


def sheet(job):
    wd = Path(job) / "work"
    m = analysis.load_meta(job)
    tw, th = 180, int(180 * m["work_h"] / m["work_w"]) // 2 * 2
    tiles = []
    for i, fr in enumerate(media.frames(wd / "src30.mp4", tw, th, "bgr24", scale="area")):
        if i % 30 == 0:
            t = fr.copy()
            cv2.putText(t, "%.0fs f%d" % (i / 30, i), (4, th - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            tiles.append(t)
    cols = 10
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(str(wd / "sheet.png"), np.vstack(rows))


def words_txt(job):
    wd = Path(job) / "work"
    ws = json.loads((wd / "words.json").read_text(encoding="utf-8"))
    lines = ["%4d  %7.2f  %-6s %s" % (w["i"], w["onset"], w["src"], w["word"]) for w in ws]
    (wd / "words.txt").write_text("  i    onset  src    word\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("raw")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--lang", default=None)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--words", default=None, help="import a transcript instead of running ASR")
    ap.add_argument("--steps", default=",".join(ALL))
    a = ap.parse_args()
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    rep = {}
    for st in ALL:
        if st not in steps:
            continue
        t0 = time.time()
        if st == "prepare":
            m = analysis.prepare(a.job, a.raw, a.start, a.end)
            rep[st] = {"n": m["n"], "work": "%dx%d" % (m["work_w"], m["work_h"]), "warnings": m["warnings"]}
        elif st == "cuts":
            rep[st] = analysis.cuts(a.job)["times"]
        elif st == "asr":
            rep[st] = analysis.asr(a.job, a.lang, a.model, a.words)
        elif st == "onsets":
            nf, n = analysis.onsets(a.job)
            words_txt(a.job)
            rep[st] = "%d/%d words snapped to an onset" % (nf, n)
        elif st == "matte":
            rep[st] = analysis.matte(a.job)
        elif st == "track":
            rep[st] = analysis.track(a.job)
        elif st == "sheet":
            sheet(a.job)
            rep[st] = "work/sheet.png"
        print("%-8s %6.1fs  %s" % (st, time.time() - t0, json.dumps(rep[st], ensure_ascii=False)[:300]), flush=True)
    p = Path(a.job) / "work" / "analysis.json"
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    old.update(rep)
    p.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
