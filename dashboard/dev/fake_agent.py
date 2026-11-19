"""Stand-in for Claude Code when DASH_DRY_RUN=1: walks through the phases, spends nothing.

Writes the same files a real job writes (progress.log, out/final.mp4, README.md, result.json)
and prints stream-json lines like `claude -p --output-format stream-json`.
"""
import datetime
import json
import shutil
import sys
import time
from pathlib import Path

d = Path(sys.argv[1])
task = Path(sys.argv[2]) if len(sys.argv) > 2 else d / "AGENT_TASK.md"
job = json.loads((d / "job.json").read_text(encoding="utf-8"))
rev = int(job.get("revision") or 0)
fail = "fail" in (job.get("title") or "").lower() and rev == 0


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def progress(msg):
    with open(d / "progress.log", "a", encoding="utf-8") as f:
        f.write("%s — %s\n" % (datetime.datetime.now().strftime("%H:%M"), msg))


emit({"type": "system", "subtype": "init", "model": "fake-agent"})

DRY_RENDERER = '''"""Dry-run renderer (fake agent). Edit spec (job/edit.json): {"style": "<name>", "phrases": []}"""


def build_timeline(job, spec, out_w=1080, out_h=1920):
    return {"n": 0, "words": []}


def validate(tl, spec, meta, fonts):
    return []


def chunk_safe(tl, f):
    return True


def sfx_events(tl, spec):
    return []


class Renderer:
    def __init__(self, job, spec, tl, out_w=1080, out_h=1920):
        self.boxes, self.warnings = [], []

    def render_frame(self, f, src, mat):
        return src

    def face_box(self, f):
        return (0, 0, 0, 0)
'''

if job.get("kind") == "style":
    # Dry-run style job: writes a minimal skill into jobs_dryrun/_dry_skills (never the real plugin).
    for msg in ("Videolar tekshirildi", "Kadrma-kadr tahlil (soxta)", "Plagin yozilmoqda"):
        emit({"type": "assistant", "message": {"content": [{"type": "text", "text": msg + "."}]}})
        progress(msg)
        time.sleep(1)
    title = (job.get("title") or "").lower()
    if "fail" in title:
        res = {"status": "failed", "summary": "Soxta xato: videolar har xil uslubda."}
    else:
        name = "pod_glow" if "dup" in title else "dry_style_" + job["id"][-4:]
        sk = d.parent / "_dry_skills" / name
        (sk / "references").mkdir(parents=True, exist_ok=True)
        (sk / "SKILL.md").write_text("---\nname: %s\ndescription: dry-run style\n---\n\n# Dry style\n" % name,
                                     encoding="utf-8")
        for f in ("captions.md", "beat-map.md", "devices.md", "motion.md", "look.md", "sound.md", "qa.md"):
            (sk / "references" / f).write_text("# %s\n" % f, encoding="utf-8")
        if "norenderer" not in title:      # a style job must ship an engine renderer; "norenderer" tests the refusal
            (sk / "renderer.py").write_text(DRY_RENDERER, encoding="utf-8")
            (sk / "renderer_example.json").write_text('{"style": "%s", "phrases": []}\n' % name, encoding="utf-8")
        res = {"status": "done", "style_name": name, "title": "Dry Style " + job["id"][-4:],
               "def": "Sinov: soxta uslub, kadrma-kadr tahlilsiz", "fits": "Sinov", "look": "Sinov",
               "summary": "Soxta uslub yaratildi.", "open_issues": [], "videos_used": 2}
    (d / "result.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    progress("Tayyor: " + res.get("style_name", "xato"))
    emit({"type": "result", "subtype": "success", "is_error": False, "result": res["status"], "num_turns": 4})
    sys.exit(0)
if rev:
    fb = " ".join((d / "feedback" / ("r%d" % rev) / "feedback.md").read_text(encoding="utf-8").split())
    steps = [
        ("Read", {"file_path": str(task)}, "Tuzatish %d: izohlar o'qildi (%s)" % (rev, fb[:60] or "faqat fayl")),
        ("PowerShell", {"command": "python -I compose.py --range ..."}, "O'zgarishlar qayta render qilinmoqda"),
    ]
else:
    steps = [
        ("Skill", {"skill": "styles:" + job["style"]}, "Uslub yuklandi: " + job["style"]),
        ("PowerShell", {"command": "ffprobe input\\raw\\..."}, "Raw video tekshirildi"),
        ("mcp__higgsfield__balance", {}, "Higgsfield balansi olindi (soxta)"),
        ("Write", {"file_path": str(d / "plan.md")}, "Reja yozildi (plan.md)"),
        ("PowerShell", {"command": "python -I compose.py ..."}, "Render qilinmoqda"),
    ]
    if job.get("level") in ("std", "rich"):   # idea pass: one web search (several when the title asks to break the cap)
        n_ws = 4 if "webover" in (job.get("title") or "").lower() else 1
        steps[3:3] = [("WebSearch", {"query": "how to visualise a list in a talking-head reel"}, "G'oya qidirildi (internet)")] * n_ws
        (d / "ideas.md").write_text(
            "| t | trigger | words | idea | source | status | reason |\n|---|---|---|---|---|---|---|\n"
            "| 0 | phrase | \"soxta ibora\" | kalit ibora katta yozuv | plugin:%s devices.md | qabul | ochilish |\n"
            "| 1.5 | number | \"96 marta\" | raqam animatsiyasi | web:https://example.com/tips | qabul | raqam |\n"
            "| 1.8 | claim | \"eng yaxshi\" | yulduzcha belgi | — | rad | zichlik limiti |\n" % job["style"], encoding="utf-8")
for name, inp, msg in steps:
    emit({"type": "assistant", "message": {"content": [
        {"type": "text", "text": msg + "."}, {"type": "tool_use", "name": name, "input": inp}]}})
    progress(msg)
    time.sleep(1.5)

if not rev:
    (d / "plan.md").write_text("# Soxta reja\n\nDRY RUN: hech narsa generatsiya qilinmadi.\n", encoding="utf-8")
if fail:
    (d / "result.json").write_text(json.dumps({"status": "failed", "summary": "Soxta xato: sarlavhada 'fail' bor."},
                                              ensure_ascii=False), encoding="utf-8")
    emit({"type": "result", "subtype": "success", "is_error": False, "result": "failed on purpose", "num_turns": 5})
    sys.exit(0)

(d / "out").mkdir(exist_ok=True)
raw = sorted((d / "input" / "raw").iterdir())
shutil.copyfile(raw[0], d / "out" / "final.mp4")
readme = d / "README.md"
text = readme.read_text(encoding="utf-8") if readme.exists() else "# Soxta natija\n\nDRY RUN: `out/final.mp4` — raw videoning nusxasi.\n"
if rev:
    text += "\n## Tuzatish %d\n\nDRY RUN: izoh o'qildi, video qayta nusxa qilindi.\n" % rev
readme.write_text(text, encoding="utf-8")
_refvids = [r for r in job.get("refs", []) if r.lower().endswith((".mp4", ".mov", ".webm", ".mkv"))]
_auto = job["style"] == "auto"
if _refvids:   # a real agent writes the style card from the reference analysis; the fake one leaves a stub
    (d / "work").mkdir(exist_ok=True)
    (d / "work" / "style_card.md").write_text("# Uslub kartasi (soxta)\n\n- titr: sans, 0.06 H (ref: %s 1.0s)\n" % _refvids[0], encoding="utf-8")
_mats = job.get("materials") or []
_miss = "matmiss" in (job.get("title") or "").lower()
_mrep = []
_free = [m["name"] for m in _mats if not m.get("required")]
for _i, _m in enumerate(_mats):
    _use = (_m.get("required") and not _miss) or (bool(_free) and _m["name"] == _free[0])
    _mrep.append({"file": _m["name"], "used": bool(_use), "t": [0.5, 1.5] if _use else [],
                  "how": "soxta: kartada ko'rsatildi" if _use else "", "reason": "" if _use else "soxta: zichlik limiti"})
(d / "work").mkdir(exist_ok=True)   # a real agent lists every device for the restraint QA; the fake one, its two
(d / "work" / "records.json").write_text(json.dumps({"text": [], "devices": [
    {"kind": "soxta titr", "group": "caption", "t": [0.0, 1.9]},
    {"kind": "ochilish sarlavhasi", "group": "card", "t": [0.0, 0.8]},
    {"kind": "raqam", "group": "graphic", "t": [1.5, 1.9]}]}, ensure_ascii=False), encoding="utf-8")
(d / "result.json").write_text(json.dumps({
    "materials": _mrep,
    "status": "done", "style": "custom:dry_ref" if (_auto and _refvids) else job["style"],
    "style_source": ("reference" if _refvids else "plugin") if _auto else None,
    "style_card": "work/style_card.md" if _refvids else None,
    "video": "out/final.mp4", "credits_spent": 0, "balance_before": 0,
    "balance_after": 0, "open_issues": ["Bu DRY RUN edi."],
    "timeline": [{"t": 0, "text": "Ochilish: kalit ibora katta yozuv bilan", "quote": "soxta ibora"},
                 {"t": 1.5, "text": "Raqam animatsiyasi", "quote": "96 marta"}],
    "overall": "DRY RUN: butun video bo'ylab hech narsa o'zgarmadi (raw nusxa).",
    "summary": ("Soxta tuzatish %d bajarildi." % rev) if rev else "Soxta ish: raw video nusxa qilindi, kredit sarflanmadi."},
    ensure_ascii=False), encoding="utf-8")
progress("Tayyor: out/final.mp4" + (" (tuzatish %d)" % rev if rev else ""))
emit({"type": "result", "subtype": "success", "is_error": False, "result": "done", "num_turns": 6})
