"""End-to-end check of the dashboard API against a running DRY-RUN server (no credits)."""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8051"
MEDIA = Path(sys.argv[2])
H = {"X-Dash": "1"}
ok = True


def req(method, path, body=None, headers=None, raw=False):
    h = dict(H, **(headers or {}))
    data = body
    if isinstance(body, dict):
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            b = resp.read()
            return resp.status, (b if raw else json.loads(b or b"{}")), dict(resp.headers)
    except urllib.error.HTTPError as e:
        b = e.read()
        return e.code, (b if raw else json.loads(b or b"{}")), dict(e.headers)


def check(name, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name + (("  " + str(extra)) if extra and not cond else ""))


s, styles, _ = req("GET", "/api/styles")
ROOT = Path(__file__).resolve().parents[2]
STYLES = Path(os.environ.get("DASH_STYLES", str(ROOT / "styles")))          # Docker: /data/styles
JOBS_DIR = Path(req("GET", "/api/health")[1]["jobs_dir"])                   # the server's own dry-run jobs folder
skill_names = {p.name for p in (STYLES / "skills").iterdir() if (p / "SKILL.md").exists()}
dry = JOBS_DIR / "_dry_skills"     # styles made by dry-run style jobs
skill_names |= {p.name for p in dry.iterdir() if (p / "SKILL.md").exists()} if dry.exists() else set()
n_skills = len(skill_names)
check("all %d styles listed" % n_skills, s == 200 and len(styles) == n_skills, [x["name"] for x in styles])
check("styles have Uzbek notes", all(x["fits"] and x["look"] and x["def"] for x in styles))
s, lv, _ = req("GET", "/api/levels")
check("levels listed", s == 200 and [l["id"] for l in lv["levels"]] == ["min", "std", "rich"] and lv["rate"] == 18, lv)

# level + client $ limit -> credit cap
s, b, _ = req("POST", "/api/jobs", {"style": "pod_glow", "title": "lvl", "level": "rich"})
check("level cap = level max", s == 201 and b["credit_cap"] == 60 and b["level"] == "rich", b)
s, b, _ = req("POST", "/api/jobs", {"style": "pod_glow", "title": "lvl", "level": "rich", "usd_cap": 2})
check("usd cap lowers credit cap", s == 201 and b["credit_cap"] == 36 and b["usd_cap"] == 2, b)
s, b, _ = req("POST", "/api/jobs", {"title": "lvl", "level": "min", "usd_cap": 10})
check("minimal stays 0", s == 201 and b["credit_cap"] == 0, b)
s, b, _ = req("POST", "/api/jobs", {"title": "custom budget", "level": None, "usd_cap": 5})
check("standalone dollar limit has no level ceiling", s == 201 and b["level"] is None
      and b["usd_cap"] == 5 and b["credit_cap"] == 90 and b["level_cap"] == 90, b)
s, b, _ = req("POST", "/api/jobs", {"title": "zero budget", "usd_cap": 0})
check("standalone zero limit stays zero without a level", s == 201 and b["level"] is None
      and b["credit_cap"] == 0 and b["usd_cap"] == 0, b)
s, b, _ = req("POST", "/api/jobs", {"title": "invalid budget", "usd_cap": -1})
check("negative standalone limit rejected", s == 400, b)
s, b, _ = req("POST", "/api/jobs", {"title": "invalid budget", "usd_cap": lv["max_usd"] + 1})
check("standalone limit above maximum rejected", s == 400, b)
s, b, _ = req("POST", "/api/jobs", {"title": "lvl", "level": "huge"})
check("unknown level rejected", s == 400, b)
s, b, _ = req("POST", "/api/jobs", {"title": "lvl", "level": "std", "usd_cap": -1})
check("negative usd rejected", s == 400, b)
s, h, _ = req("GET", "/api/health")
check("health dry_run, own jobs folder", s == 200 and h["dry_run"] and h["styles"] == n_skills
      and h["jobs_dir"].endswith("jobs_dryrun") and not h["worker_disabled"], h)

# writes without the custom header are refused (other websites cannot start jobs)
r = urllib.request.Request(BASE + "/api/jobs", data=b'{"style":"pod_glow"}', method="POST",
                           headers={"Content-Type": "application/json"})
try:
    urllib.request.urlopen(r)
    check("POST without X-Dash refused", False)
except urllib.error.HTTPError as e:
    check("POST without X-Dash refused", e.code == 403)

s, b, _ = req("POST", "/api/jobs", {"style": "nope", "title": "x", "credit_cap": 10})
check("unknown style rejected", s == 400, b)
s, b, _ = req("POST", "/api/jobs", {"style": "pod_glow", "title": "x", "credit_cap": 99999})
check("credit cap bound", s == 400, b)


def run_job(title, expect):
    s, job, _ = req("POST", "/api/jobs", {"style": "pod_glow", "title": title, "ref_text": "Brend rangi to'q sariq", "credit_cap": 40})
    check("create job (%s)" % title, s == 201 and job["state"] == "draft" and job["refs"] == ["brief.txt"], job)
    jid = job["id"]
    s, b, _ = req("POST", "/api/jobs/%s/submit" % jid)
    check("submit without raw refused", s == 400, b)
    s, b, _ = req("PUT", "/api/jobs/%s/upload?kind=raw&name=evil.exe" % jid, b"MZ")
    check("bad extension refused", s == 400, b)
    s, b, _ = req("PUT", "/api/jobs/%s/upload?kind=ref&name=..%%5C..%%5Cnotes.md" % jid, (MEDIA / "notes.md").read_bytes())
    check("ref doc uploaded, path stripped", s == 201 and b["name"] == "notes.md", b)
    s, b, _ = req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % jid, (MEDIA / "raw test.mp4").read_bytes())
    check("raw uploaded", s == 201 and b["name"] == "raw test.mp4", b)
    s, b, _ = req("POST", "/api/jobs/%s/submit" % jid)
    check("submit -> queued", s == 200 and b["state"] == "queued", b)
    t0 = time.time()
    while time.time() - t0 < 60:
        s, d, _ = req("GET", "/api/jobs/" + jid)
        if d["state"] in ("done", "failed", "cancelled"):
            break
        time.sleep(1)
    check("job ends %s" % expect, d["state"] == expect, (d["state"], d.get("error")))
    check("progress lines read", len(d["progress"]) >= 5, d["progress"])
    check("activity parsed", any(a["k"] == "tool" for a in d["activity"]), d["activity"][:3])
    return jid, d


jid, d = run_job("ok run", "done")
check("video set", d["video"] == "out/final.mp4", d.get("video"))
check("raw probed on upload", (d.get("raw_info") or [{}])[0].get("w") == 720 and d["raw_info"][0]["audio"], d.get("raw_info"))
check("estimate set on submit", isinstance(d.get("est_minutes"), int) and d["est_minutes"] >= 5, d.get("est_minutes"))
check("default format 9:16", d.get("format") == "9:16", d.get("format"))
q = d.get("qa") or {}
check("server ran static QA", q.get("total", 0) >= 6 and isinstance(q.get("checks"), list), q.get("error") or q)
check("timeline read from result.json", (d.get("timeline") or [{}])[0].get("text", "").startswith("Ochilish") and d.get("overall"), d.get("timeline"))
s, body, hdr = req("GET", "/api/jobs/%s/file?path=out/final.mp4" % jid, headers={"Range": "bytes=0-99"}, raw=True)
check("range request 206", s == 206 and len(body) == 100 and hdr.get("Content-Range", "").startswith("bytes 0-99/"), (s, hdr))
s, body, _ = req("GET", "/api/jobs/%s/file?path=..%%2F..%%2F..%%2Fcues.json" % jid, raw=True)
check("path traversal refused", s == 404, s)
task = (JOBS_DIR / jid / "AGENT_TASK.md").read_text(encoding="utf-8")
check("task rendered", "{{" not in task and "styles:pod_glow" in task and "40 credits" in task
      and "1080×1920" in task and "qa_check.py" in task and "records.json" in task)

# formats, input check, archive, balance
s, lv2, _ = req("GET", "/api/levels")
check("formats listed", [f["id"] for f in lv2["formats"]] == ["9:16", "4:5", "1:1", "16:9"] and lv2["default_format"] == "9:16", lv2.get("formats"))
s, b, _ = req("POST", "/api/jobs", {"title": "bad fmt", "level": "min", "format": "2:1"})
check("unknown format refused", s == 400, b)
s, jf, _ = req("POST", "/api/jobs", {"title": "fmt 16:9", "level": "min", "format": "16:9"})
check("format kept", s == 201 and jf["format"] == "16:9", jf)
if (MEDIA / "low.mp4").exists():
    s, b, _ = req("PUT", "/api/jobs/%s/upload?kind=raw&name=low.mp4" % jf["id"], (MEDIA / "low.mp4").read_bytes())
    check("below 720p refused", s == 400 and "720" in b.get("error", ""), b)
s, b, _ = req("PUT", "/api/jobs/%s/upload?kind=raw&name=fake.mp4" % jf["id"], b"not a video at all")
check("non-video refused", s == 400, b)
s, h2, _ = req("GET", "/api/health")
check("health has balance field", "balance" in h2, h2)
s, b, _ = req("POST", "/api/jobs/%s/archive" % jid, {"archived": True})
check("job archived", s == 200 and b.get("archived") is True, b)
s, b, _ = req("POST", "/api/jobs/%s/archive" % jid, {"archived": False})
check("job unarchived", s == 200 and b.get("archived") is False, b)

# no style chosen -> auto: the agent is told to choose
s, job, _ = req("POST", "/api/jobs", {"title": "auto", "level": "rich", "usd_cap": 1})
check("no style -> auto", s == 201 and job["style"] == "auto", job)
req("PUT", "/api/jobs/%s/upload?kind=raw&name=a.mp4" % job["id"], (MEDIA / "raw test.mp4").read_bytes())
req("POST", "/api/jobs/%s/submit" % job["id"])
t0 = time.time()
while time.time() - t0 < 60:
    s, d, _ = req("GET", "/api/jobs/" + job["id"])
    if d["state"] in ("done", "failed"):
        break
    time.sleep(1)
task = (JOBS_DIR / job["id"] / "AGENT_TASK.md").read_text(encoding="utf-8")
check("auto task: evidence-first choice (words, references, scored plugins, web, own)", "{{" not in task and "derive it from evidence" in task
      and "styles:<name>" in task and "holo_scene" in task and "WebSearch" in task and "Score every plugin" in task
      and "custom:" in task and d["state"] == "done", d["state"])
check("task has level, supplement rules, timeline", "**Boy.**" in task and "Supplementing the style" in task
      and "Never create, edit or delete anything in" in task and '"timeline"' in task and "18 credits" in task)

jid2, d2 = run_job("fail run", "failed")
check("failure reason shown", "Soxta xato" in (d2.get("error") or ""), d2.get("error"))

# cancel a queued job
s, job, _ = req("POST", "/api/jobs", {"style": "case_reel", "title": "cancel me", "credit_cap": 5})
req("PUT", "/api/jobs/%s/upload?kind=raw&name=a.mp4" % job["id"], (MEDIA / "raw test.mp4").read_bytes())
s, b, _ = req("POST", "/api/jobs/%s/cancel" % job["id"])
check("cancel draft", s == 200 and b["state"] == "cancelled", b)

# companies: create, duplicate refused, job with company, move job, unknown company refused
import uuid as _uuid
cname = "Test Co " + _uuid.uuid4().hex[:4]
s, co, _ = req("POST", "/api/companies", {"name": cname})
check("company created", s == 201 and co["name"] == cname and co["initials"] == "TC" and co["color"].startswith("#"), co)
s, b, _ = req("POST", "/api/companies", {"name": cname.upper()})
check("duplicate company refused", s == 400, b)
s, lst, _ = req("GET", "/api/companies")
check("company listed", any(c["id"] == co["id"] for c in lst), lst)
s, j1, _ = req("POST", "/api/jobs", {"title": "co job", "level": "min", "company": co["id"]})
check("job keeps company", s == 201 and j1["company"] == co["id"], j1)
s, b, _ = req("POST", "/api/jobs", {"title": "co job", "level": "min", "company": "no-such-co"})
check("unknown company refused", s == 400, b)
s, b, _ = req("POST", "/api/jobs/%s/company" % jid, {"company": co["id"]})
check("job moved to company", s == 200 and b["company"] == co["id"], b)
s, b, _ = req("POST", "/api/jobs/%s/company" % jid, {"company": None})
check("job moved back to no company", s == 200 and b["company"] is None, b)
s, b, _ = req("POST", "/api/companies/%s" % co["id"], {"name": cname + " Group"})
check("company renamed", s == 200 and b["name"] == cname + " Group", b)
s, b, _ = req("POST", "/api/companies/%s" % co["id"], {"archived": True})
check("company archived (not deleted)", s == 200 and b.get("archived") is True, b)
s, b, _ = req("POST", "/api/jobs", {"title": "co job", "level": "min", "company": co["id"]})
check("archived company refused for new jobs", s == 400 and "arxiv" in b.get("error", ""), b)
s, lst, _ = req("GET", "/api/companies")
check("archived company still listed", any(c["id"] == co["id"] and c.get("archived") for c in lst), lst)
s, b, _ = req("POST", "/api/companies/%s" % co["id"], {"archived": False})
check("company unarchived", s == 200 and not b.get("archived"), b)

s, page, _ = req("GET", "/", raw=True)
check("index served", s == 200 and b"Montaj studiyasi" in page)
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
