"""QA of a rendered edit: word sync, platform safe zones, face clearance, frozen ending, loudness, contact sheet.

usage: python -I engine/qa.py <job> [--video out/final.mp4] [--boxes work/picture.boxes.jsonl]
Writes work/qa.json and work/qa_sheet.png (key frames with the platform UI zones in red).
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import media, styles_loader  # noqa: E402

# approximate Reels / TikTok / Shorts UI, shares of W/H (see the platform-framer skill for exact zones)
ZONES = {"top bar": (0, 0, 1, 0.07), "caption area": (0, 0.80, 1, 1), "action rail": (0.87, 0.42, 1, 0.88)}


def sync(tl):
    rows, bad, shown = [], [], set()
    words, N, fps = tl["words"], tl["n"], tl["fps"]
    keys = []
    for c in tl["comps"]:
        for it in c["items"]:
            fx = c["exit_small_f"] if it["role"] in ("cluster", "sub") else c["exit_f"]
            end = min(N - 1, fx + 4)
            on = words[it["words"][0]]["onset"]
            delay = it["f"] - on * fps
            vis = end - it["f"] + 1
            shown.update(it["words"])
            if delay < 0:
                bad.append("EARLY %r comp %d (%.2f f)" % (it["text"], c["id"], delay))
            if delay > 3:
                bad.append("LATE %r comp %d (%.2f f)" % (it["text"], c["id"], delay))
            if vis < 6:
                bad.append("SHORT %r comp %d visible %d f" % (it["text"], c["id"], vis))
            if it["role"] not in ("cluster", "sub"):
                keys.append((it["f"], c["exit_f"] + 4, c["id"], it["text"]))
    keys.sort()
    for x, y in zip(keys, keys[1:]):
        if y[0] <= x[1]:
            bad.append("KEY OVERLAP %r (comp %d) with %r (comp %d) for %d f" % (x[3], x[2], y[3], y[2], x[1] - y[0] + 1))
    missing = [i for i in range(len(words)) if i not in shown]
    return {"items": sum(len(c["items"]) for c in tl["comps"]), "words_shown": len(shown), "words": len(words),
            "missing": missing, "problems": bad}


def boxes_check(path, W, H):
    zone_hits, face_hits = {}, {}
    nfr = 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        nfr += 1
        fx0, fy0, fx1, fy1 = r["face"]
        fwp = fx1 - fx0
        for role, txt, x0, y0, x1, y1 in r["b"]:
            for zn, (a, b, c, d) in ZONES.items():
                if x0 < c * W and x1 > a * W and y0 < d * H and y1 > b * H:
                    k = "%s | %s '%s'" % (zn, role, txt)
                    zone_hits[k] = zone_hits.get(k, 0) + 1
            if role in ("cluster", "sub"):
                g = 0.15 * fwp
                if x0 < fx1 + g and x1 > fx0 - g and y0 < fy1 and y1 > fy0:
                    k = "%s '%s'" % (role, txt)
                    face_hits[k] = face_hits.get(k, 0) + 1
    return nfr, zone_hits, face_hits


def frozen_end(video, n=15):
    p = media.probe(video)
    w, h = 108, 192
    fr = list(media.frames(video, w, h, "gray", scale="area"))[-n:]
    d = [float(np.abs(fr[i].astype(np.float32) - fr[i - 1]).mean()) for i in range(1, len(fr))]
    return {"last_frames_mean_diff": [round(x, 2) for x in d], "frozen": bool(d) and max(d) < 0.15,
            "duration": p["duration"]}


def contact(video, frames, out, W, H):
    tiles = []
    for f in frames:
        b = media.frame_at(video, f / 30 + 0.001, W, H)
        im = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
        ov = im.copy()
        for (a, b_, c, d) in ZONES.values():
            cv2.rectangle(ov, (int(a * W), int(b_ * H)), (int(c * W), int(d * H)), (0, 0, 255), -1)
        im = cv2.addWeighted(ov, 0.30, im, 0.70, 0)
        im = cv2.resize(im, (270, 480), interpolation=cv2.INTER_AREA)
        cv2.putText(im, "f%d %.2fs" % (f, f / 30), (4, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        tiles.append(im)
    cols = 6
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(str(out), np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--video", default=None)
    ap.add_argument("--boxes", default=None)
    a = ap.parse_args()
    job = Path(a.job)
    wd = job / "work"
    spec = json.loads((job / "edit.json").read_text(encoding="utf-8"))
    st = styles_loader.load(spec["style"])
    tl = st.build_timeline(job, spec)
    video = Path(a.video or job / "out" / "final.mp4")
    if not video.exists():
        video = wd / "picture.mp4"
    boxes = Path(a.boxes or wd / "picture.boxes.jsonl")
    rep = {"sync": sync(tl)}
    if boxes.exists():
        nfr, zh, fh = boxes_check(boxes, 1080, 1920)
        rep["safe_zone_frames"] = zh
        rep["face_overlap_frames"] = fh
        rep["frames_checked"] = nfr
    rep["ending"] = frozen_end(video)
    sj = wd / "sound.json"
    if sj.exists():
        s = json.loads(sj.read_text(encoding="utf-8"))
        rep["loudness"] = {"lufs": s["integrated_lufs"], "true_peak": s["true_peak_dbtp"],
                           "ok": abs(s["integrated_lufs"] + 14) <= 0.5 and s["true_peak_dbtp"] <= -1.0}
    keyf = sorted({min(tl["n"] - 1, (c["key_f"] or c["f_start"]) + 8) for c in tl["comps"]})
    contact(video, keyf, wd / "qa_sheet.png", 1080, 1920)
    (wd / "qa.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    s = rep["sync"]
    print("sync: %d/%d words on screen, %d problems" % (s["words_shown"], s["words"], len(s["problems"])))
    for p in s["problems"][:20]:
        print("  -", p)
    if "safe_zone_frames" in rep:
        print("safe zones: %d text/zone overlaps over %d frames" % (len(rep["safe_zone_frames"]), rep["frames_checked"]))
        for k, v in sorted(rep["safe_zone_frames"].items(), key=lambda x: -x[1])[:12]:
            print("  - %s: %d f" % (k, v))
        print("face clearance: %d items closer than 0.15 FW" % len(rep["face_overlap_frames"]))
        for k, v in sorted(rep["face_overlap_frames"].items(), key=lambda x: -x[1])[:12]:
            print("  - %s: %d f" % (k, v))
    e = rep["ending"]
    print("ending: %s (last diffs %s)" % ("FROZEN" if e["frozen"] else "live", e["last_frames_mean_diff"][-5:]))
    if "loudness" in rep:
        print("loudness: %.1f LUFS, %.1f dBTP %s" % (rep["loudness"]["lufs"], rep["loudness"]["true_peak"],
                                                    "ok" if rep["loudness"]["ok"] else "OUT OF SPEC"))
    print("contact sheet: work/qa_sheet.png")


if __name__ == "__main__":
    main()
