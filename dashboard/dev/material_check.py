r"""Extra materials check (dry run, no credits): photos and clips are uploaded with a note and a "required" flag,
the server probes them and makes contact sheets for clips, the task lists them with the rules, and after delivery the
QA counts used materials and fails when a required one was not used.

usage: python -I dev/material_check.py http://127.0.0.1:8051 <folder with "raw test.mp4">
"""
import json
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE, MEDIA = sys.argv[1].rstrip("/"), Path(sys.argv[2])
fails = 0


def req(method, path, body=None, raw=None):
    h = {"X-Dash": "1"}
    data = raw
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def check(name, cond, extra=""):
    global fails
    fails += 0 if cond else 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (extra,)))


tmp = Path(tempfile.mkdtemp())
big = tmp / "product.png"
small = tmp / "tiny_logo.png"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=orange:size=1200x1200", "-frames:v", "1", str(big)], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:size=200x120", "-frames:v", "1", str(small)], check=True)
broll = MEDIA / "raw test.mp4"


def run(title, mats):
    s, j = req("POST", "/api/jobs", {"style": "pod_glow", "title": title, "level": "std"})
    jid = j["id"]
    req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % jid, raw=(MEDIA / "raw test.mp4").read_bytes())
    for path, name, note, required in mats:
        q = urllib.parse.urlencode({"kind": "mat", "name": name, "note": note, "required": "1" if required else "0"})
        s, b = req("PUT", "/api/jobs/%s/upload?%s" % (jid, q), raw=path.read_bytes())
        if s != 201:
            print("upload failed", name, s, b)
    req("POST", "/api/jobs/%s/submit" % jid, {})
    for _ in range(240):
        j = req("GET", "/api/jobs/" + jid)[1]
        if j["state"] in ("done", "failed"):
            return j
        time.sleep(1)
    raise SystemExit("job did not finish")


s, b = req("POST", "/api/jobs", {"style": "pod_glow", "title": "bad mat", "level": "min"})
s2, b2 = req("PUT", "/api/jobs/%s/upload?kind=mat&name=notes.txt" % b["id"], raw=b"hello")
check("a non-media material is refused", s2 == 400, (s2, b2))
svg = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120"><rect x="10" y="10" width="100" height="100" '
       b'rx="20" fill="#2563eb"/><text x="130" y="80" font-size="60">Logo</text></svg>')
s3, b3 = req("PUT", "/api/jobs/%s/upload?kind=mat&name=logo.svg&note=oxirida%%20logo&required=1" % b["id"], raw=svg)
jb = req("GET", "/api/jobs/" + b["id"])[1]
lm = next((x for x in jb.get("materials") or [] if x.get("name") == "logo.svg"), {})
jd = Path(req("GET", "/api/health")[1]["jobs_dir"]) / b["id"] / "input" / "materials"
check("SVG kept as uploaded (no server conversion), measured from its viewBox",
      s3 == 201 and lm.get("vector") is True and lm.get("kind") == "image" and (lm.get("w"), lm.get("h")) == (400, 120)
      and lm.get("low") is False and lm.get("required") is True and (jd / "logo.svg").is_file() and not (jd / "logo.png").exists(), (s3, b3, lm))
s4, b4 = req("PUT", "/api/jobs/%s/upload?kind=mat&name=broken.svg" % b["id"], raw=b"<svg><not closed")
check("a broken SVG is refused with a message", s4 == 400 and "SVG" in b4.get("error", ""), (s4, b4))

jobs_dir = Path(req("GET", "/api/health")[1]["jobs_dir"])
mats = [(big, "product.png", "mahsulot, narx aytilganda", True), (small, "tiny_logo.png", "oxirida logo", False),
        (broll, "office broll.mp4", "", False)]
j = run("materials ok", mats)
check("job done", j["state"] == "done", j.get("error"))
m = {x["name"]: x for x in j.get("materials") or []}
check("materials stored with kind, size, note, flag",
      m.get("product.png", {}).get("kind") == "image" and m["product.png"]["w"] == 1200 and m["product.png"]["required"] is True
      and m["product.png"]["note"].startswith("mahsulot") and m.get("office broll.mp4", {}).get("kind") == "video", m)
check("small image flagged low quality", m.get("tiny_logo.png", {}).get("low") is True and m["product.png"]["low"] is False)
ma = j.get("materials_analysis") or []
check("clip got contact sheets", len(ma) == 1 and ma[0]["ok"] and (jobs_dir / j["id"] / ma[0]["dir"] / "report.json").is_file(), ma)
task = (jobs_dir / j["id"] / "AGENT_TASK.md").read_text(encoding="utf-8")
check("task lists materials with note and REQUIRED", "input/materials/product.png" in task and "**REQUIRED**" in task
      and "mahsulot, narx aytilganda" in task and "**blurry/low resolution**" in task and "{{" not in task)
check("task rules: use sharp files as they are, AI-improve blurry ones, required must appear",
      "Use each file as it is when it is sharp" in task and "upscale_image" in task and "AI qayta yaratdi" in task
      and "REQUIRED materials must appear" in task and "`material:<file>`" in task)
check("task weights: user's words high, references medium, style medium to lower",
      "**high**" in task and "**medium**" in task and "**medium to lower**" in task)
qa = {c["name"]: c for c in (j.get("qa") or {}).get("checks", [])}
check("QA counts used materials", qa.get("Materiallar", {}).get("detail", "").startswith("3 tadan 2 tasi"), qa.get("Materiallar"))
check("QA: required used -> ok", qa.get("Majburiy materiallar", {}).get("status") == "ok", qa.get("Majburiy materiallar"))
check("report kept on the job", any(r["file"] == "office broll.mp4" and not r["used"] and r["reason"] for r in j.get("materials_report") or []), j.get("materials_report"))

k = run("materials matmiss", mats[:1])
qk = {c["name"]: c for c in (k.get("qa") or {}).get("checks", [])}
check("QA fails when a required material was not used", qk.get("Majburiy materiallar", {}).get("status") == "fail", qk.get("Majburiy materiallar"))
print("ALL PASS" if not fails else "%d FAIL" % fails)
sys.exit(1 if fails else 0)
