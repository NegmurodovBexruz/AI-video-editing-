"""DRY-RUN checks: cancel a running job; restart the server while a job runs and see it re-attach."""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BASE, MEDIA, PHASE = sys.argv[1], Path(sys.argv[2]), sys.argv[3]


def req(method, path, body=None):
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"X-Dash": "1", "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read() or b"{}")


def new_job(title):
    j = req("POST", "/api/jobs", {"style": "talk_ahead", "title": title, "credit_cap": 1})
    req("PUT", "/api/jobs/%s/upload?kind=raw&name=r.mp4" % j["id"], (MEDIA / "raw test.mp4").read_bytes())
    req("POST", "/api/jobs/%s/submit" % j["id"])
    return j["id"]


def wait_state(jid, states, t=30):
    t0 = time.time()
    while time.time() - t0 < t:
        d = req("GET", "/api/jobs/" + jid)
        if d["state"] in states:
            return d
        time.sleep(0.5)
    return d


if PHASE == "cancel":
    jid = new_job("cancel running")
    d = wait_state(jid, ("running",))
    pid = d.get("pid")
    req("POST", "/api/jobs/%s/cancel" % jid)
    d = wait_state(jid, ("cancelled", "failed", "done"))
    alive = subprocess.run(["tasklist", "/FI", "PID eq %s" % pid], capture_output=True, text=True).stdout
    print("cancel running ->", d["state"], "| agent process gone:", str(pid) not in alive)
elif PHASE == "start":
    jid = new_job("survive restart")
    d = wait_state(jid, ("running",))
    print(jid, d["state"], d.get("pid"))
elif PHASE == "after":
    jid = sys.argv[4]
    d = wait_state(jid, ("done", "failed", "cancelled"), 40)
    print("after restart ->", d["state"], d.get("error"), "| progress lines:", len(d["progress"]))
