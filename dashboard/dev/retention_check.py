r"""Retention + delete check against a dry-run server started with DASH_RETENTION_DAYS=14.
Ages a finished job by editing its job.json, runs the same purge the server runs hourly (store.expire_old,
same jobs folder), then checks the API. Also checks full deletion.

usage (same env as the server: DASH_DRY_RUN=1, DASH_DATA/DASH_STYLES if set):
    python -I dev/retention_check.py http://127.0.0.1:8051 <folder with "raw test.mp4">
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DASH_DRY_RUN", "1")
os.environ.setdefault("DASH_RETENTION_DAYS", "14")
import config  # noqa: E402
import store   # noqa: E402

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
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def check(name, cond, extra=""):
    global fails
    fails += 0 if cond else 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % extra))


def finished_job(title):
    s, j = req("POST", "/api/jobs", {"style": "pod_glow", "title": title, "level": "min"})
    jid = j["id"]
    req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % jid, raw=(MEDIA / "raw test.mp4").read_bytes())
    req("POST", "/api/jobs/%s/submit" % jid, {})
    for _ in range(120):
        s, j = req("GET", "/api/jobs/" + jid)
        if j["state"] in ("done", "failed"):
            return j
        time.sleep(1)
    raise SystemExit("job did not finish")


s, lv = req("GET", "/api/levels")
check("levels report retention", lv.get("retention_days") == 14, lv.get("retention_days"))
jobs_dir = Path(req("GET", "/api/health")[1]["jobs_dir"])
check("checker and server share the jobs folder", jobs_dir.resolve() == config.JOBS.resolve(), (jobs_dir, config.JOBS))

# ---- retention ----
j = finished_job("retention")
jid, d = j["id"], jobs_dir / j["id"]
fin = datetime.datetime.fromisoformat(j["finished"])
check("finished job has expires_at = finished + 14 d",
      j.get("expires_at") and abs((datetime.datetime.fromisoformat(j["expires_at"]) - fin).days - 14) == 0, j.get("expires_at"))
check("job has media before purge", (d / "out" / "final.mp4").exists() and any((d / "input" / "raw").iterdir()))
store.expire_old()
check("a young job is not purged", (d / "out" / "final.mp4").exists())
old = (datetime.datetime.now() - datetime.timedelta(days=20)).isoformat(timespec="seconds")
store.update(jid, finished=old)
purged = dict(store.expire_old())
s, j = req("GET", "/api/jobs/" + jid)
check("old job purged", jid in purged and j.get("expired") and j.get("video") is None and j.get("expires_at") is None, j.get("expired"))
check("media gone (raw, render)", not (d / "out" / "final.mp4").exists() and not (d / "input" / "raw").exists())
check("record kept (job.json, progress.log)", (d / "job.json").exists() and (d / "progress.log").exists())
check("purge noted in progress", any("muddati tugadi" in l for l in j.get("progress", [])))
s, b = req("POST", "/api/jobs/%s/feedback" % jid, {"text": "x"})
check("feedback on an expired job refused", s == 400, (s, b))
check("purge is idempotent", jid not in dict(store.expire_old()))

# ---- delete ----
k = finished_job("delete me")
kid = k["id"]
s, b = req("POST", "/api/jobs/%s/delete" % kid, {})
check("finished job deleted", s == 200 and b.get("deleted") == kid, (s, b))
check("deleted job is gone from the API", req("GET", "/api/jobs/" + kid)[0] == 404)
check("deleted job folder is gone from disk", not (jobs_dir / kid).exists())
check("deleted job not listed", all(x["id"] != kid for x in req("GET", "/api/jobs")[1]))
s, q = req("POST", "/api/jobs", {"style": "pod_glow", "title": "busy", "level": "min"})
req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % q["id"], raw=(MEDIA / "raw test.mp4").read_bytes())
req("POST", "/api/jobs/%s/submit" % q["id"], {})
s, b = req("POST", "/api/jobs/%s/delete" % q["id"], {})
check("queued/running job cannot be deleted", s == 400, (s, b))
s, b = req("POST", "/api/jobs/%s/delete" % jid, {})
check("expired job can be deleted", s == 200, (s, b))
print("ALL PASS" if not fails else "%d FAIL" % fails)
sys.exit(1 if fails else 0)
