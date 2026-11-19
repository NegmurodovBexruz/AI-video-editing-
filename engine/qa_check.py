r"""Static QA for any finished edit, whatever the style (AP-1077). Run by the dashboard server after every job,
and by the agent before delivery. It checks properties of the result, not its content.

usage: python -I engine/qa_check.py <job_dir> [--format 9:16] [--video out/final.mp4] [--lufs -14]
writes <job>/work/qa_check.json; exit code 1 when a check fails.

Checks without extra input: format/size/fps/codecs, loudness + true peak, live ending, black frames, frozen stretches,
"Nima qilindi" timeline present + visual density (from result.json).
Checks that need <job>/work/records.json (written by the agent's compositor, any style):
    {"text": [{"text": "SATURATION", "in": 2.40, "out": 4.50, "onset": 2.38,
               "box": [x0, y0, x1, y1], "visible": 0.62}, ...]}
    in/out   seconds in the final video;  onset  start of the spoken word in the final video (null if not speech)
    box      pixels in the output frame while the text is fully shown
    visible  share of the box NOT covered by other layers (cards, people, objects) at its hold, 0..1
-> caption sync, short flashes, platform safe zones (9:16 only), text out of frame, text hidden behind objects.
Design language (the same file, "devices" list; missing = FAIL on a first run, WARN in a revision):
    {"devices": [{"kind": "price receipt card", "group": "card", "t": [12.0, 16.5], "asked": false}, ...]}
    group    caption | card (cards, panels, labels, checklists, stickers) | graphic (maps, charts, counters, diagrams)
             | insert (B-roll, AI clips, split screens, full-screen cards)
    one entry per continuous appearance; "asked": true only when the user's own words demand exactly this device
-> one caption system, <= 2 kinds of card, <= 3 kinds of card + graphic (how OFTEN they appear is not limited here;
   the timeline density check covers that), and no devices at the Minimal level.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

FORMATS = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080)}
# approximate Reels / TikTok / Shorts UI as shares of W/H (same as engine/qa.py)
ZONES = {"yuqori panel": (0, 0, 1, 0.07), "pastki izoh zonasi": (0, 0.80, 1, 1), "o'ng tugmalar": (0.87, 0.42, 1, 0.88)}
MIN_VISIBLE = 0.60          # a key word may sit behind an object, but at least 60 % of it must stay readable
DENSITY_WARN, DENSITY_FAIL = 6, 8   # visual events in any 10 s window
# Design language: a few looks used consistently (a dense edit is fine; a mix of seven card styles is not).
DEVICE_GROUPS = ("caption", "card", "graphic", "insert")
MAX_CAPTION_KINDS, MAX_CARD_KINDS, MAX_DESIGN_KINDS = 1, 2, 3


def run(cmd, timeout=600):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def probe(video):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)], 60)
    return json.loads(r.stdout or "{}")


def check(rep, cid, name, status, detail):
    rep["checks"].append({"id": cid, "name": name, "status": status, "detail": detail})


def c_format(rep, info, fmt):
    W, H = FORMATS[fmt]
    vs = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    au = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not vs:
        return check(rep, "format", "Format va o'lcham", "fail", "Video oqimi yo'q")
    v = vs[0]
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    n, _, d = (v.get("avg_frame_rate") or "0/1").partition("/")
    fps = float(n) / float(d or 1) if float(d or 1) else 0
    probs = []
    if (w, h) != (W, H):
        probs.append("o'lcham %d×%d, kerak %d×%d (%s)" % (w, h, W, H, fmt))
    if abs(fps - 30) > 0.5:
        probs.append("fps %.2f, kerak 30" % fps)
    if v.get("codec_name") != "h264":
        probs.append("video kodek %s, kerak h264" % v.get("codec_name"))
    if not au:
        probs.append("ovoz yo'q")
    elif au[0].get("codec_name") != "aac":
        probs.append("ovoz kodek %s, kerak aac" % au[0].get("codec_name"))
    check(rep, "format", "Format va o'lcham", "fail" if probs else "ok",
          "; ".join(probs) or "%d×%d, %.0f fps, h264 + aac" % (w, h, fps))


def c_loudness(rep, video, target):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a:0?", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else ""
    mi, mp = re.search(r"I:\s+(-?[\d.]+) LUFS", tail), re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    if not mi:
        return check(rep, "loudness", "Ovoz balandligi", "fail", "O'lchab bo'lmadi (ovoz yo'qmi?)")
    lufs, tp = float(mi.group(1)), float(mp.group(1)) if mp else 0.0
    off = abs(lufs - target)
    st = "ok" if off <= 1.0 and tp <= -1.0 else ("warn" if off <= 2.0 and tp <= -0.5 else "fail")
    check(rep, "loudness", "Ovoz balandligi", st, "%.1f LUFS (maqsad %g), true peak %.1f dBTP (≤ −1)" % (lufs, target, tp))


def gray_frames(video, start=None, sseof=None, w=108, h=192):
    cmd = ["ffmpeg", "-v", "error"] + (["-sseof", str(sseof)] if sseof else []) + (["-ss", str(start)] if start else []) + \
          ["-i", str(video), "-vf", "scale=%d:%d:flags=area,format=gray" % (w, h), "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, timeout=300).stdout
    n = len(raw) // (w * h)
    return np.frombuffer(raw[: n * w * h], np.uint8).reshape(n, h, w).astype(np.float32)


def c_ending(rep, video):
    fr = gray_frames(video, sseof=-2.0)
    if len(fr) < 3:
        return check(rep, "ending", "Oxiri jonli kadr", "warn", "Oxirgi kadrlarni o'qib bo'lmadi")
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    moving = float((d > 0.15).mean())
    st = "ok" if moving >= 0.5 else ("warn" if moving > 0.1 else "fail")
    check(rep, "ending", "Oxiri jonli kadr", st,
          "oxirgi 2 s da kadrlarning %d%% ida harakat bor%s" % (round(moving * 100), "" if st == "ok" else " — oxiri qotib qolgan bo'lishi mumkin"))


def c_black_freeze(rep, video):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vf",
             "blackdetect=d=0.5:pix_th=0.10,freezedetect=n=-60dB:d=3", "-an", "-f", "null", "-"])
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)
    fz = re.findall(r"freeze_start: ([\d.]+)", r.stderr)
    fe = re.findall(r"freeze_duration: ([\d.]+)", r.stderr)
    check(rep, "black", "Qora kadrlar", "warn" if blacks else "ok",
          ", ".join("%.1f–%.1f s" % (float(a), float(b)) for a, b in blacks) or "yo'q")
    check(rep, "freeze", "Qotib qolgan joylar", "warn" if fz else "ok",
          ", ".join("%.1f s dan %.1f s" % (float(a), float(b)) for a, b in zip(fz, fe)) or "3 s dan uzun qotish yo'q")


def c_timeline(rep, job):
    try:
        res = json.loads((job / "result.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        res = {}
    tl = [float(x["t"]) for x in res.get("timeline") or [] if isinstance(x, dict) and "t" in x]
    if not tl:
        check(rep, "timeline", "\"Nima qilindi\" ro'yxati", "warn", "result.json da timeline yo'q")
        return check(rep, "density", "Zichlik", "warn", "timeline yo'q, tekshirilmadi")
    check(rep, "timeline", "\"Nima qilindi\" ro'yxati", "ok", "%d ta hodisa" % len(tl))
    tl.sort()
    best, at = 0, 0.0
    for i, t in enumerate(tl):
        n = sum(1 for u in tl[i:] if u < t + 10)
        if n > best:
            best, at = n, t
    st = "ok" if best <= DENSITY_WARN else ("warn" if best <= DENSITY_FAIL else "fail")
    check(rep, "density", "Zichlik", st, "eng zich 10 s: %d ta hodisa (%.1f s dan), tavsiya ≤ %d" % (best, at, DENSITY_WARN))


def c_records(rep, job, fmt):
    p = job / "work" / "records.json"
    if not p.exists():
        return check(rep, "records", "Titr va grafika yozuvi", "warn", "work/records.json yo'q: titr sinxroni, zonalar va matn ko'rinishi tekshirilmadi")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return check(rep, "records", "Titr va grafika yozuvi", "fail", "records.json o'qib bo'lmadi")
    items = data.get("text") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        return check(rep, "records", "Titr va grafika yozuvi", "warn",
                     "records.json standart formatda emas (\"text\" ro'yxati yo'q): titr sinxroni, zonalar va matn ko'rinishi tekshirilmadi")
    W, H = FORMATS[fmt]
    early, late, short, zone, out, hidden = [], [], [], [], [], []
    for it in items:
        txt = str(it.get("text", ""))[:30]
        t_in, t_out, on = it.get("in"), it.get("out"), it.get("onset")
        if isinstance(t_in, (int, float)) and isinstance(on, (int, float)):
            df = (t_in - on) * 30
            if df < -0.5:
                early.append("%s (%.1f kadr oldin)" % (txt, -df))
            elif df > 3:
                late.append("%s (%.1f kadr kech)" % (txt, df))
        if isinstance(t_in, (int, float)) and isinstance(t_out, (int, float)) and t_out - t_in < 0.2:
            short.append(txt)
        b = it.get("box")
        if isinstance(b, list) and len(b) == 4:
            x0, y0, x1, y1 = b
            if x0 < -2 or y0 < -2 or x1 > W + 2 or y1 > H + 2:
                out.append(txt)
            if fmt == "9:16":
                for zn, (a, bb, c, d) in ZONES.items():
                    if x0 < c * W and x1 > a * W and y0 < d * H and y1 > bb * H:
                        zone.append("%s → %s" % (txt, zn))
        v = it.get("visible")
        if isinstance(v, (int, float)) and v < MIN_VISIBLE:
            hidden.append("%s (%d%% ko'rinadi)" % (txt, round(v * 100)))
    check(rep, "records", "Titr va grafika yozuvi", "ok", "%d ta matn elementi" % len(items))
    check(rep, "sync", "Titr sinxroni", "fail" if early else ("warn" if late else "ok"),
          "; ".join(["erta: " + ", ".join(early[:6])] * bool(early) + ["kech: " + ", ".join(late[:6])] * bool(late)) or "hamma so'z o'z tovushida")
    check(rep, "short", "Juda qisqa chiqqan matn", "warn" if short else "ok", ", ".join(short[:8]) or "yo'q")
    check(rep, "frame", "Kadrdan chiqib ketgan matn", "fail" if out else "ok", ", ".join(out[:8]) or "yo'q")
    if fmt == "9:16":
        check(rep, "zones", "Platforma zonalari", "fail" if zone else "ok", "; ".join(zone[:8]) or "matn tugmalar va izoh zonasiga tushmaydi")
    check(rep, "visible", "Matn ko'rinishi", "fail" if hidden else "ok",
          ", ".join(hidden[:8]) or "hamma matnning kamida %d%% i ko'rinadi" % round(MIN_VISIBLE * 100))


def c_restraint(rep, job, duration):
    """One design language: few kinds of caption, card and graphic. Reads the "devices" list of work/records.json."""
    try:
        data = json.loads((job / "work" / "records.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    devs = data.get("devices") if isinstance(data, dict) else None
    try:
        jj = json.loads((job / "job.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        jj = {}
    level = jj.get("level")
    # A revision changes only what the user's notes ask for: devices kept from the previous version are not the
    # agent's choice now, so over-limit results there warn instead of failing.
    hard = "warn" if int(jj.get("revision") or 0) > 0 else "fail"
    if not isinstance(devs, list):
        return check(rep, "restraint", "Dizayn tili", hard,
                     "records.json da \"devices\" ro'yxati yo'q: dizayn tili tekshirilmadi")
    kinds = {g: set() for g in DEVICE_GROUPS}
    events, bad = [], []          # events: devices the agent chose (not captions, not asked for by the user)
    for d in devs:
        if not isinstance(d, dict):
            continue
        g, kind, t = d.get("group"), " ".join(str(d.get("kind") or "").lower().split()), d.get("t")
        if g not in DEVICE_GROUPS or not kind or not (isinstance(t, list) and len(t) == 2
                                                       and all(isinstance(x, (int, float)) for x in t) and t[1] > t[0]):
            bad.append(str(d.get("kind") or "?")[:30])
            continue
        if g != "caption" and d.get("asked"):
            continue
        kinds[g].add(kind)
        if g != "caption":
            events.append(kind)
    if bad:
        check(rep, "devices", "Effektlar yozuvi", "fail", "noto'g'ri yozuv (group/kind/t): " + ", ".join(bad[:6]))
    cap, card, design = len(kinds["caption"]), len(kinds["card"]), len(kinds["card"] | kinds["graphic"])
    probs = []
    if cap > MAX_CAPTION_KINDS:
        probs.append("%d xil titr uslubi (ko'pi bilan %d): %s" % (cap, MAX_CAPTION_KINDS, ", ".join(sorted(kinds["caption"]))))
    if card > MAX_CARD_KINDS:
        probs.append("%d xil karta (ko'pi bilan %d): %s" % (card, MAX_CARD_KINDS, ", ".join(sorted(kinds["card"]))))
    if design > MAX_DESIGN_KINDS:
        probs.append("%d xil grafik element (ko'pi bilan %d)" % (design, MAX_DESIGN_KINDS))
    check(rep, "kinds", "Dizayn tili", hard if probs else "ok",
          "; ".join(probs) or "%d titr uslubi, %d xil karta, %d xil grafik element" % (cap, card, design))
    if level == "min":   # Minimal: the style's captions, transitions, grade and sound only
        check(rep, "minimal", "Minimal daraja", hard if events else "ok",
              ("Minimal darajada effekt bo'lmasligi kerak: %d ta (%s)" % (len(events), ", ".join(sorted(set(events))[:5])))
              if events else "faqat titr, o'tishlar, rang va ovoz")


def main():
    try:  # python -I ignores PYTHONIOENCODING; Windows consoles default to cp1251/cp866
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--format", default="9:16", choices=list(FORMATS))
    ap.add_argument("--video", default=None)
    ap.add_argument("--lufs", type=float, default=-14.0)
    a = ap.parse_args()
    job = Path(a.job)
    video = Path(a.video) if a.video else job / "out" / "final.mp4"
    rep = {"video": str(video), "format": a.format, "checks": []}
    if not video.exists():
        check(rep, "file", "Video fayl", "fail", "%s yo'q" % video)
    else:
        info = probe(video)
        c_format(rep, info, a.format)
        c_loudness(rep, video, a.lufs)
        c_ending(rep, video)
        c_black_freeze(rep, video)
        c_timeline(rep, job)
        c_records(rep, job, a.format)
        c_restraint(rep, job, float(info.get("format", {}).get("duration") or 0))
    (job / "work").mkdir(exist_ok=True)
    (job / "work" / "qa_check.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    mark = {"ok": "OK  ", "warn": "WARN", "fail": "FAIL"}
    for c in rep["checks"]:
        print("%s %s: %s" % (mark[c["status"]], c["name"], c["detail"]))
    fails = sum(1 for c in rep["checks"] if c["status"] == "fail")
    print("QA: %d/%d ok, %d fail" % (sum(1 for c in rep["checks"] if c["status"] == "ok"), len(rep["checks"]), fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
