"""DRY-RUN check of the feedback / revision flow against a running dry-run server (no credits).

    python -I dev\feedback_check.py http://127.0.0.1:8051 <folder with "raw test.mp4">
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = sys.argv[1].rstrip("/")
MEDIA = Path(sys.argv[2])
fails = 0


def req(method, path, body=None, raw=None, headers=None):
    h = {"X-Dash": "1", **(headers or {})}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    elif raw is not None:
        data = raw
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            txt = resp.read()
            is_json = (resp.headers.get("Content-Type") or "").startswith("application/json")
            return resp.status, (json.loads(txt) if is_json else txt)
    except urllib.error.HTTPError as e:
        txt = e.read()
        return e.code, (json.loads(txt) if txt[:1] == b"{" else txt)


def check(name, ok, info=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -> %s" % (info,)))
    fails += 0 if ok else 1


def wait(jid, states=("done", "failed", "cancelled"), t=60):
    for _ in range(t * 2):
        s, d = req("GET", "/api/jobs/" + jid)
        if d.get("state") in states:
            return d
        time.sleep(0.5)
    return d


raw = (MEDIA / "raw test.mp4").read_bytes()
s, job = req("POST", "/api/jobs", {"style": "pod_glow", "title": "feedback test", "credit_cap": 0})
jid = job["id"]
req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % jid, raw=raw)
s, _ = req("PUT", "/api/jobs/%s/upload?kind=fb&name=note.png" % jid, raw=b"x")
check("feedback upload refused before the job ends", s == 400, s)
req("POST", "/api/jobs/%s/submit" % jid)
s, _ = req("POST", "/api/jobs/%s/feedback" % jid, {"text": "x"})
check("feedback refused while queued/running", s == 400, s)
d = wait(jid)
check("first run done", d["state"] == "done" and d.get("video"), d.get("state"))

s, _ = req("POST", "/api/jobs/%s/feedback" % jid, {"text": "   "})
check("empty feedback refused", s == 400, s)
s, _ = req("PUT", "/api/jobs/%s/upload?kind=fb&name=evil.exe" % jid, raw=b"MZ")
check("bad feedback file type refused", s == 400, s)
s, up = req("PUT", "/api/jobs/%s/upload?kind=fb&name=..%%2F..%%2Fshot.png" % jid, raw=b"\x89PNG fake")
check("feedback file uploaded, path stripped", s == 201 and up.get("name") == "shot.png", (s, up))

note = "[0:04.5] titr kattaroq bo'lsin\nlogoni olib tashlang"
s, d = req("POST", "/api/jobs/%s/feedback" % jid, {"text": note, "credit_cap": 5})
check("feedback accepted -> queued", s == 200 and d.get("state") == "queued" and d.get("revision") == 1, (s, d.get("state")))
check("previous version archived", (d.get("versions") or [{}])[0].get("video") == "versions/v1/final.mp4", d.get("versions"))
check("cap set for the revision", d.get("credit_cap") == 5, d.get("credit_cap"))
d = wait(jid)
check("revision 1 done", d["state"] == "done" and d.get("video") == "out/final.mp4", (d.get("state"), d.get("error")))
check("revision summary is the new one", "tuzatish 1" in (d.get("summary") or "").lower(), d.get("summary"))
fbk = (d.get("feedback") or [{}])[0]
check("feedback stored with text and file", fbk.get("text") == note and fbk.get("files") == ["shot.png"], fbk)
s, body = req("GET", "/api/jobs/%s/file?path=versions/v1/final.mp4" % jid)
check("v1 video served", s == 200 and len(body) == len(raw), s)
s, body = req("GET", "/api/jobs/%s/file?path=feedback/r1/feedback.md" % jid)
check("feedback.md saved", s == 200 and note.encode() in body, s)
s, body = req("GET", "/api/jobs/%s/file?path=feedback/r1/TASK.md" % jid)
check("revision task rendered", s == 200 and b"{{" not in body and b"Revision 1" in body, body[:80])
check("progress shows the revision", any("Tuzatish 1" in x for x in d.get("progress") or []), d.get("progress"))

s, d = req("POST", "/api/jobs/%s/feedback" % jid, {"text": "yana bitta", "credit_cap": 0})
d = wait(jid)
check("second revision -> 2 archived versions", d.get("revision") == 2 and len(d.get("versions") or []) == 2, d.get("versions"))
check("based_on points at v2", d["feedback"][-1].get("based_on") == 2, d["feedback"][-1])

# level job: the client sends no credit number, the revision gets the job's level cap
s, job = req("POST", "/api/jobs", {"style": "pod_glow", "title": "level fb", "level": "std", "usd_cap": 0.5})
check("level job cap from $", s == 201 and job.get("credit_cap") == 9 and job.get("level_cap") == 9, job)
req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % job["id"], raw=raw)
req("POST", "/api/jobs/%s/submit" % job["id"])
wait(job["id"])
s, d = req("POST", "/api/jobs/%s/feedback" % job["id"], {"text": "[0:01.5] raqam sekinroq"})
check("revision cap = level cap", s == 200 and d.get("credit_cap") == 9, (s, d.get("credit_cap")))
d = wait(job["id"])
s, body = req("GET", "/api/jobs/%s/file?path=feedback/r1/TASK.md" % job["id"])
check("revision task has level + timeline", s == 200 and b"**Standart.**" in body and b'"timeline"' in body, body[:80])
check("revision timeline kept", (d.get("timeline") or [{}])[0].get("t") == 0, d.get("timeline"))

# A standalone dollar budget must also survive revisions without reverting to the legacy 20-credit cap.
for amount, cap in [(5, 90), (0, 0), (120, 2160)]:
    s, job = req("POST", "/api/jobs", {"title": "custom budget fb", "usd_cap": amount})
    req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % job["id"], raw=raw)
    req("POST", "/api/jobs/%s/submit" % job["id"])
    wait(job["id"])
    s, d = req("POST", "/api/jobs/%s/feedback" % job["id"], {"text": "[0:01] titr kattaroq"})
    check("standalone $%s budget kept for revision" % amount,
          s == 200 and d.get("level") is None and d.get("usd_cap") == amount
          and d.get("credit_cap") == cap, (s, d))
    wait(job["id"])

print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
