r"""DRY-RUN check of 'Uslub yaratish' (style-building jobs) against a running dry-run server (no credits).

    python -I dev\style_check.py http://127.0.0.1:8051 <folder with "raw test.mp4">
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = sys.argv[1].rstrip("/")
MEDIA = Path(sys.argv[2])
ROOT = Path(__file__).resolve().parents[2]
STYLES = Path(os.environ.get("DASH_STYLES", str(ROOT / "styles")))                       # Docker: /data/styles
NOTES = Path(os.environ.get("DASH_STYLE_NOTES", str(ROOT / "dashboard" / "style_notes.json")))
fails = 0


def req(method, path, body=None, raw=None):
    h = {"X-Dash": "1"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    elif raw is not None:
        data = raw
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def check(name, ok, info=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -> %s" % (info,)))
    fails += 0 if ok else 1


def wait(jid, t=60):
    for _ in range(t * 2):
        s, d = req("GET", "/api/jobs/" + jid)
        if d.get("state") in ("done", "failed", "cancelled"):
            return d
        time.sleep(0.5)
    return d


def style_job(title, n_videos):
    s, job = req("POST", "/api/style-jobs", {"title": title, "ref_text": "Shu uslub yoqdi"})
    jid = job["id"]
    vid = (MEDIA / "raw test.mp4").read_bytes()
    for i in range(n_videos):
        req("PUT", "/api/jobs/%s/upload?kind=ref&name=ref%d.mp4" % (jid, i), raw=vid)
    return s, job, jid


JOBS_DIR = Path(req("GET", "/api/health")[1]["jobs_dir"])      # the server's own dry-run jobs folder
real_before = sorted(p.name for p in (STYLES / "skills").iterdir())
notes_before = NOTES.read_bytes() if NOTES.exists() else b""
s, b = req("GET", "/api/styles")
n0 = len(b)

s, job, jid = style_job("Mening uslubim", 1)
check("style job created", s == 201 and job["kind"] == "style" and job["credit_cap"] == 0, job)
s, b = req("PUT", "/api/jobs/%s/upload?kind=raw&name=x.mp4" % jid, raw=b"x")
check("raw upload refused for a style job", s == 400, b)
s, b = req("POST", "/api/jobs/%s/submit" % jid)
check("1 video refused (need 2)", s == 400 and "2" in b.get("error", ""), b)
req("PUT", "/api/jobs/%s/upload?kind=ref&name=ref_b.mp4" % jid, raw=(MEDIA / "raw test.mp4").read_bytes())
s, b = req("POST", "/api/jobs/%s/submit" % jid)
check("2 videos -> queued", s == 200 and b["state"] == "queued", b)
d = wait(jid)
check("style job done", d["state"] == "done" and d.get("new_style", "").startswith("dry_style_"), (d["state"], d.get("error")))
s, b = req("GET", "/api/styles")
new = [x for x in b if x["name"] == d.get("new_style")]
check("new style is in the list at once", len(b) == n0 + 1 and new and new[0]["def"].startswith("Sinov"), [x["name"] for x in b])
task = (JOBS_DIR / jid / "AGENT_TASK.md").read_text(encoding="utf-8")
check("style task rendered", "{{" not in task and "_dry_skills" in task and "rule of two" in task
      and "pod_glow" in task and "No credits" in task, task[:200])
check("style task asks for a renderer", "renderer.py" in task and "styles_loader.py" in task and "Not a template" in task)
sk_new = JOBS_DIR / "_dry_skills" / d.get("new_style", "?")
check("new style ships renderer.py + example", (sk_new / "renderer.py").is_file() and (sk_new / "renderer_example.json").is_file())
s, b = req("POST", "/api/jobs/%s/feedback" % jid, {"text": "x"})
check("no feedback on style jobs", s == 400, b)

s, job, jid = style_job("norenderer test", 2)
req("POST", "/api/jobs/%s/submit" % jid)
d = wait(jid)
check("style without a renderer is not registered", d["state"] == "failed" and "renderer" in (d.get("error") or ""), d.get("error"))

s, job, jid = style_job("dup test", 2)
req("POST", "/api/jobs/%s/submit" % jid)
d = wait(jid)
check("existing name rejected", d["state"] == "failed" and "avvaldan bor" in (d.get("error") or ""), d.get("error"))

s, job, jid = style_job("fail test", 2)
req("POST", "/api/jobs/%s/submit" % jid)
d = wait(jid)
check("agent failure shown", d["state"] == "failed" and "Soxta xato" in (d.get("error") or ""), d.get("error"))

check("real plugin untouched", sorted(p.name for p in (STYLES / "skills").iterdir()) == real_before)
check("real style_notes.json untouched", (NOTES.read_bytes() if NOTES.exists() else b"") == notes_before)

print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
