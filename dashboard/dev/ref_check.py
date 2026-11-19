r"""Reference-first style evidence check against a dry-run server (no credits):
the server analyses reference videos frame by frame before the agent, the task carries the user's "ref_use"
choice and the analysis folders, and a reference-vs-result sheet is made after the video.

usage: python -I dev/ref_check.py http://127.0.0.1:8051 <folder with "raw test.mp4">
"""
import json
import sys
import time
import urllib.error
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


def run(body, refs):
    s, j = req("POST", "/api/jobs", body)
    if s != 201:
        return s, j
    jid = j["id"]
    req("PUT", "/api/jobs/%s/upload?kind=raw&name=raw%%20test.mp4" % jid, raw=(MEDIA / "raw test.mp4").read_bytes())
    for n in refs:
        req("PUT", "/api/jobs/%s/upload?kind=ref&name=%s" % (jid, n), raw=(MEDIA / "raw test.mp4").read_bytes())
    req("POST", "/api/jobs/%s/submit" % jid, {})
    for _ in range(240):
        s, j = req("GET", "/api/jobs/" + jid)
        if j["state"] in ("done", "failed"):
            return 200, j
        time.sleep(1)
    raise SystemExit("job did not finish")


jobs_dir = Path(req("GET", "/api/health")[1]["jobs_dir"])
s, b = req("POST", "/api/jobs", {"style": "auto", "title": "x", "level": "min", "ref_use": "copy-everything"})
check("unknown ref_use refused", s == 400, (s, b))
s, b = req("POST", "/api/jobs", {"style": "auto", "title": "x", "level": "min", "ref_like": "a" * 1501})
check("too long 'what I liked' refused", s == 400 and "juda uzun" in b.get("error", ""), (s, b))

LIKE = "so'zlar bittadan   sakrab chiqsin\n\n0:12 dagi tez zoom o'tishi. Musiqasi kerak emas"
s, j = run({"style": "auto", "title": "ref rhythm", "level": "min", "ref_use": "rhythm", "ref_text": "ritm tez bo'lsin",
            "ref_like": LIKE}, ["ref_a.mp4"])
d = jobs_dir / j["id"]
check("job done", j["state"] == "done", j.get("error"))
check("ref_use stored", j.get("ref_use") == "rhythm")
ra = j.get("ref_analysis") or []
check("server analysed the reference", len(ra) == 1 and ra[0]["ok"] and (d / ra[0]["dir"] / "report.json").is_file(), ra)
rep = json.loads((d / ra[0]["dir"] / "report.json").read_text(encoding="utf-8")) if ra and ra[0]["ok"] else {}
check("analysis has sheets and frames", rep.get("images", {}).get("sheets") and rep.get("images", {}).get("frames"), list(rep.get("images", {})))
task = (d / "AGENT_TASK.md").read_text(encoding="utf-8")
check("task: no unfilled placeholders", "{{" not in task)
check("task: ref_use line", "`rhythm`: pacing, cut rhythm and transitions only" in task)
check("'what I liked' stored, whitespace tidied", j.get("ref_like") == "so'zlar bittadan sakrab chiqsin\n0:12 dagi tez zoom o'tishi. Musiqasi kerak emas",
      j.get("ref_like"))
check("task: user's liked parts quoted, binding, tagged in the style card",
      "  > so'zlar bittadan sakrab chiqsin" in task and "  > 0:12 dagi tez zoom" in task
      and "in their own words** (binding" in task and "`(user-liked)`" in task, task[task.find("What the user asked"):][:900])
check("task: analysis folder listed", ra and ra[0]["dir"] in task)
check("task: style evidence rules", "Style evidence" in task and "style_card.md" in task and "Take the style, never the content" in task)
check("task: auto choice scores plugins", "Score every plugin" in task and "plugin+reference" in task and "cannot watch videos" in task)
check("progress shows the analysis", any("Referens tahlili tayyor" in l for l in j.get("progress", [])))
check("reference vs result sheet made", j.get("ref_compare") == "work/ref_compare.jpg" and (d / "work" / "ref_compare.jpg").is_file(), j.get("ref_compare"))

s, k = run({"style": "pod_glow", "title": "no refs", "level": "min", "ref_like": "bu e'tiborsiz qolishi kerak"}, [])
task2 = (jobs_dir / k["id"] / "AGENT_TASK.md").read_text(encoding="utf-8")
check("no refs: no analysis, no sheet", not k.get("ref_analysis") and not k.get("ref_compare"))
check("no refs: task says so", "(no reference videos)" in task2 and "{{" not in task2)
check("no refs: 'what I liked' not put in the task", "e'tiborsiz qolishi" not in task2)
check("explicit style: source inferred as plugin", k.get("style_source") in ("plugin", None) or k.get("style_source") == "plugin", k.get("style_source"))

# The new form sends only the user's own words, with no preset/category selection.
s, free = run({"title": "freeform reference", "usd_cap": 5, "ref_like": LIKE}, ["ref_free.mp4"])
free_task = (jobs_dir / free["id"] / "AGENT_TASK.md").read_text(encoding="utf-8")
check("freeform reference with standalone budget finishes", free.get("state") == "done"
      and free.get("level") is None and free.get("credit_cap") == 90, free.get("error"))
check("freeform task uses the user's words without assuming all features",
      "do not assume they requested every visual feature" in free_task
      and "  > so'zlar bittadan sakrab chiqsin" in free_task)

# ---- "Shu uslubni saqlash" ----
check("auto job with a reference: style from the reference, card stored",
      j.get("style_source") == "reference" and j.get("style_card") == "work/style_card.md", (j.get("style_source"), j.get("style_card")))
s, b = req("POST", "/api/jobs/%s/save-style" % k["id"], {"title": "x"})
check("plugin-made video cannot be saved as a new style", s == 400, (s, b))
s, sj = req("POST", "/api/jobs/%s/save-style" % j["id"], {"title": "Ref Look"})
check("save-style starts a style job", s == 201 and sj.get("kind") == "style" and sj.get("state") == "queued" and sj.get("from_job") == j["id"], (s, sj))
if s == 201:
    sd = jobs_dir / sj["id"] / "input" / "refs"
    names = sorted(p.name for p in sd.iterdir())
    check("samples copied: reference + finished video + style card + note",
          "ref_a.mp4" in names and ("natija_%s.mp4" % j["id"]) in names and "style_card.md" in names and "brief.txt" in names, names)
    check("source job links to the style job", req("GET", "/api/jobs/" + j["id"])[1].get("saved_style_job") == sj["id"])
    for _ in range(120):
        st = req("GET", "/api/jobs/" + sj["id"])[1]
        if st["state"] in ("done", "failed"):
            break
        time.sleep(1)
    check("style job finishes and registers the style", st["state"] == "done" and st.get("new_style"), (st["state"], st.get("error")))
    task3 = (jobs_dir / sj["id"] / "AGENT_TASK.md").read_text(encoding="utf-8")
    check("style task lists the result video as a sample", ("natija_%s.mp4" % j["id"]) in task3)
print("ALL PASS" if not fails else "%d FAIL" % fails)
sys.exit(1 if fails else 0)
