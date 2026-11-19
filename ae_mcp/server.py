r"""After Effects MCP server for the editing agent (AP-1077). stdio JSON-RPC, Python stdlib only, Windows.

Every call starts its own After Effects process (`AfterFX.com -m -noui -r`), works on a project file inside the
job folder, saves it and exits, so AE never holds memory between calls. The project file is the state.

Tools
  ae_run     run ExtendScript (ES3) against <job>/<project>; lib.jsx helpers are loaded; returns result + log
  ae_frames  render single frames of a comp to PNG so the agent can look at them (Read the files)
  ae_render  render a comp with aerender and encode it: H.264 MP4, or ProRes 4444 MOV with alpha

Guards: the job folder must lie under AE_MCP_ROOTS; files stay inside the job folder; one AE at a time; a running
After Effects that this server did not start is never touched (refused); at least AE_MIN_FREE_GB of free RAM.

Env: AE_DIR (Support Files folder), AE_MCP_ROOTS (os.pathsep list), AE_MIN_FREE_GB (default 3).
"""
import ctypes
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
AE_DIR = Path(os.environ.get("AE_DIR", r"D:\AE\Adobe\Adobe After Effects 2025\Support Files"))
AFX, AERENDER = AE_DIR / "AfterFX.com", AE_DIR / "aerender.exe"
DEFAULT_ROOTS = os.pathsep.join([str(REPO / "projects" / "jobs"), str(REPO / "projects" / "jobs_dryrun")])
MIN_FREE_GB = float(os.environ.get("AE_MIN_FREE_GB", "3"))
LOCK = Path(tempfile.gettempdir()) / "ap1077_ae_mcp.lock"
RUN_TIMEOUT, RENDER_TIMEOUT = 900, 7200
NO_WINDOW = 0x08000000
VERSION = "0.1.0"
MAX_FRAMES = 12


class ToolError(Exception):
    pass


def roots():
    return [Path(p).resolve() for p in os.environ.get("AE_MCP_ROOTS", DEFAULT_ROOTS).split(os.pathsep) if p.strip()]


# ---------- guards ----------

def job_path(job_dir):
    if not job_dir:
        raise ToolError("job_dir kerak")
    p = Path(job_dir).resolve()
    if not p.is_dir():
        raise ToolError("job_dir topilmadi: %s" % p)
    if not any(p == r or r in p.parents for r in roots()):
        raise ToolError("job_dir ruxsat etilgan papkalar ichida emas: %s" % p)
    return p


def inside(job, rel, what="path"):
    if not rel or not isinstance(rel, str):
        raise ToolError("%s kerak" % what)
    p = (job / rel).resolve()
    if p != job and job not in p.parents:
        raise ToolError("%s job papkasidan tashqarida: %s" % (what, rel))
    return p


def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def ae_processes():
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq AfterFX.exe", "/FO", "CSV", "/NH"], capture_output=True,
                       text=True, creationflags=NO_WINDOW)
    return [line for line in r.stdout.splitlines() if line.startswith('"AfterFX.exe"')]


def pid_alive(pid):
    r = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"], capture_output=True, text=True,
                       creationflags=NO_WINDOW)
    return '"%d"' % pid in r.stdout


class AELock:
    """One AE job at a time across every copy of this server; refuse while a user-opened AE runs."""

    def __enter__(self):
        if not AFX.exists():
            raise ToolError("After Effects topilmadi: %s (AE_DIR ni sozlang)" % AFX)
        for _ in range(2):
            try:
                fd = os.open(str(LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                break
            except FileExistsError:
                try:
                    other = int(LOCK.read_text().strip() or 0)
                except (OSError, ValueError):
                    other = 0
                if other and other != os.getpid() and pid_alive(other):
                    raise ToolError("Boshqa AE ishi ketyapti (pid %d). Tugashini kuting." % other)
                LOCK.unlink(missing_ok=True)
        else:
            raise ToolError("AE qulfini olib bo'lmadi: %s" % LOCK)
        try:
            if ae_processes():
                raise ToolError("After Effects ochiq. Uni yoping: server ochiq AE oynasiga tegmaydi.")
            free = free_ram_gb()
            if free < MIN_FREE_GB:
                raise ToolError("RAM kam: %.1f GB bo'sh, kamida %.1f GB kerak. Boshqa og'ir jarayonlar tugashini kuting."
                                % (free, MIN_FREE_GB))
        except Exception:
            LOCK.unlink(missing_ok=True)
            raise
        return self

    def __exit__(self, *exc):
        LOCK.unlink(missing_ok=True)


def kill_tree(pid):
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, creationflags=NO_WINDOW)


def run_proc(cmd, log_path, timeout, env=None):
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        p = subprocess.Popen(cmd, stdout=log, stderr=log, stdin=subprocess.DEVNULL, env=env, creationflags=NO_WINDOW)
        try:
            return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_tree(p.pid)
            raise ToolError("Vaqt tugadi (%d s): jarayon to'xtatildi. Log: %s" % (timeout, log_path))


# ---------- ExtendScript wrapper ----------

PRE = r"""
var DATA = P.data, JOB = P.job, LOG = [];
function log(s) { LOG.push(String(s)); }
function path(rel) {
    rel = String(rel).replace(/\\/g, "/");
    if (rel.indexOf("..") >= 0) throw new Error("path outside the job folder: " + rel);
    if (/^[A-Za-z]:\//.test(rel) || rel.charAt(0) === "/") {
        if (rel.toLowerCase().indexOf(JOB.toLowerCase() + "/") !== 0) throw new Error("path outside the job folder: " + rel);
        return rel;
    }
    return JOB + "/" + rel;
}
function __enc(v) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "number") return isFinite(v) ? String(v) : "null";
    if (typeof v === "boolean") return String(v);
    if (typeof v === "string") return '"' + v.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\r/g, "\\r").replace(/\n/g, "\\n").replace(/\t/g, "\\t") + '"';
    var a = [], k;
    if (v instanceof Array) { for (k = 0; k < v.length; k++) a.push(__enc(v[k])); return "[" + a.join(",") + "]"; }
    if (typeof v === "object" && v.constructor === Object) {
        for (k in v) if (v.hasOwnProperty(k)) a.push(__enc(String(k)) + ":" + __enc(v[k]));
        return "{" + a.join(",") + "}";
    }
    return __enc(String(v));
}
function __summary() {
    var out = [], i, it;
    for (i = 1; i <= app.project.numItems; i++) {
        it = app.project.item(i);
        if (it instanceof CompItem) out.push({name: it.name, w: it.width, h: it.height, fps: it.frameRate,
                                               duration: it.duration, layers: it.numLayers});
    }
    return out;
}
"""

GUARD = r"""
if ($.getenv("AP1077_AE_TOKEN") !== P.token) throw new Error("Wrong AE process; refused");
app.exitAfterLaunchAndEval = true;
app.setSavePreferencesOnQuit(false);
var __receipt = new File(P.receipt);
function __record(status, extra) {
    __receipt.encoding = "UTF-8";
    if (!__receipt.open("w")) throw new Error("cannot write receipt");
    extra.status = status; extra.version = app.version; extra.log = LOG;
    __receipt.write(__enc(extra)); __receipt.close();
}
app.beginSuppressDialogs();
try {
    if (app.project && (app.project.file || app.project.numItems > 0)) throw new Error("AE already had a project open; refused");
    var __pf = new File(P.project);
    // app.newProject() crashes AE 2025 in -noui (0xC0000409): the empty project AE starts with is used instead.
    if (__pf.exists) app.open(__pf); else if (!app.project) throw new Error("AE started without a project");
"""

TAIL = r"""
    if (P.save) app.project.save(__pf);
    __record("ok", {result: __RESULT, comps: __summary()});
} catch (__e) {
    __record("failed", {message: __e.toString(), line: __e.line});
}
app.endSuppressDialogs(false);
"""


def js_literal(obj):
    return json.dumps(obj, ensure_ascii=True)


def to_ascii(src):
    """Non-ASCII characters become \\uXXXX escapes (surrogate pairs above the BMP). Valid inside string literals,
    harmless in comments; AE reads the generated .jsx as ASCII."""
    out = []
    for ch in src:
        o = ord(ch)
        if o < 128:
            out.append(ch)
        elif o < 0x10000:
            out.append("\\u%04x" % o)
        else:
            o -= 0x10000
            out.append("\\u%04x\\u%04x" % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return "".join(out)


def build_script(payload, code, mode="run"):
    """mode run: the agent's code body; mode frames: built-in frame grabber."""
    head = "var P = %s;\n" % js_literal(payload) + PRE + (HERE / "lib.jsx").read_text(encoding="utf-8") + GUARD
    head += "    var __RESULT = (function () {\n"
    user = to_ascii(code) + "\n"
    tail = "    })();\n" + TAIL
    src = head + user + tail
    first = head.count("\n") + 1
    return to_ascii(src), first, first + user.count("\n") - 1


def run_jsx(job, payload, code, log_name):
    """Run code in a fresh AE; returns the receipt dict (user-relative error line when it is in the agent's code)."""
    work = job / "ae" / "_calls"
    work.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%H%M%S") + "_" + secrets.token_hex(2)
    token = secrets.token_hex(16)
    receipt = work / ("%s_receipt.json" % stamp)
    payload = dict(payload, token=token, job=job.as_posix(), receipt=receipt.as_posix())
    src, first, last = build_script(payload, code)
    script = work / ("%s_%s.jsx" % (stamp, log_name))
    script.write_text(src, encoding="ascii")
    env = dict(os.environ, AP1077_AE_TOKEN=token)
    t0 = time.time()
    rc = run_proc([str(AFX), "-m", "-noui", "-r", str(script)], work / ("%s_%s.log" % (stamp, log_name)), RUN_TIMEOUT, env)
    if not receipt.exists():
        raise ToolError("AE javob yozmadi (exit %s). Log: %s" % (rc, work / ("%s_%s.log" % (stamp, log_name))))
    r = json.loads(receipt.read_text(encoding="utf-8-sig"))
    r["seconds"] = round(time.time() - t0, 1)
    ln = r.get("line")
    if isinstance(ln, int):
        if first <= ln <= last:
            r["line"] = ln - first + 1
            r["line_text"] = code.splitlines()[ln - first] if ln - first < len(code.splitlines()) else ""
        else:
            r["where"] = "wrapper/lib.jsx (generated script %s, line %d)" % (script.name, ln)
            r.pop("line", None)
    return r


# ---------- tools ----------

def tool_ae_run(a):
    job = job_path(a.get("job_dir"))
    proj = inside(job, a.get("project") or "ae/project.aep", "project")
    if proj.suffix.lower() != ".aep":
        raise ToolError("project .aep bo'lishi kerak")
    proj.parent.mkdir(parents=True, exist_ok=True)
    code = a.get("script") or ""
    if not code.strip():
        raise ToolError("script bo'sh")
    with AELock():
        r = run_jsx(job, {"project": proj.as_posix(), "save": a.get("save", True) is not False,
                          "data": a.get("data") if a.get("data") is not None else {}}, code, "run")
    return r, r.get("status") != "ok"


FRAMES_JSX = r"""
var c = comp(DATA.comp), out = [], i, f, w;
for (i = 0; i < DATA.items.length; i++) {
    f = new File(path(DATA.items[i].file));
    c.saveFrameToPng(DATA.items[i].t, f);
    for (w = 0; !f.exists && w < 600; w++) $.sleep(100);     // the PNG is written asynchronously
    out.push({t: DATA.items[i].t, file: DATA.items[i].file, ok: f.exists});
}
return {fps: c.frameRate, duration: c.duration, frames: out};
"""


def tool_ae_frames(a):
    job = job_path(a.get("job_dir"))
    proj = inside(job, a.get("project") or "ae/project.aep", "project")
    if not proj.exists():
        raise ToolError("project yo'q: %s" % proj)
    comp = a.get("comp") or ""
    times = a.get("times") or []
    if not comp or not isinstance(times, list) or not times or len(times) > MAX_FRAMES:
        raise ToolError("comp va 1..%d ta vaqt (soniya) kerak" % MAX_FRAMES)
    out_dir = inside(job, a.get("out_dir") or "ae/frames", "out_dir")
    out_dir.mkdir(parents=True, exist_ok=True)
    scale = min(1.0, max(0.1, float(a.get("scale") or 0.5)))
    stamp = time.strftime("%H%M%S")
    tag = re.sub(r"[^A-Za-z0-9_-]+", "_", comp)[:30]
    items = [{"t": float(t), "file": (out_dir / ("%s_%s_%07.3fs.png" % (stamp, tag, float(t)))).relative_to(job).as_posix()}
             for t in times]
    with AELock():
        r = run_jsx(job, {"project": proj.as_posix(), "save": False, "data": {"comp": comp, "items": items}},
                    FRAMES_JSX, "frames")
    if r.get("status") != "ok":
        return r, True
    frames = []
    for it in r["result"]["frames"]:
        p = job / it["file"]
        if not it.get("ok") or not p.exists():
            frames.append({"t": it["t"], "error": "kadr yozilmadi"})
            continue
        if scale < 1:
            small = p.with_name(p.stem + "_s.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-vf", "scale=iw*%g:-2" % scale, str(small)],
                           check=True, creationflags=NO_WINDOW)
            os.replace(small, p)
        frames.append({"t": it["t"], "file": it["file"]})
    return {"status": "ok", "frames": frames, "seconds": r.get("seconds"),
            "note": "Read each PNG to look at it (scale %g)." % scale}, any("error" in f for f in frames)


def tool_ae_render(a):
    job = job_path(a.get("job_dir"))
    proj = inside(job, a.get("project") or "ae/project.aep", "project")
    if not proj.exists():
        raise ToolError("project yo'q: %s" % proj)
    comp = a.get("comp") or ""
    if not comp:
        raise ToolError("comp kerak")
    alpha = bool(a.get("alpha"))
    out = inside(job, a.get("output") or ("ae/render/%s.%s" % (re.sub(r"[^A-Za-z0-9_-]+", "_", comp), "mov" if alpha else "mp4")),
                 "output")
    if out.suffix.lower() != (".mov" if alpha else ".mp4"):
        raise ToolError("output %s bo'lishi kerak" % (".mov (alpha)" if alpha else ".mp4"))
    out.parent.mkdir(parents=True, exist_ok=True)
    mid = out.with_name(out.stem + "_aerender.avi")
    log = job / "ae" / "_calls" / ("%s_render.log" % time.strftime("%H%M%S"))
    log.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with AELock():
        rc = run_proc([str(AERENDER), "-project", str(proj), "-comp", comp, "-output", str(mid),
                       "-OMtemplate", "Lossless with Alpha" if alpha else "Lossless", "-sound", "OFF"], log, RENDER_TIMEOUT)
    if not mid.exists():
        raise ToolError("Render chiqmadi (aerender exit %s). Log: %s" % (rc, log))
    t1 = time.time()
    if alpha:
        enc = ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"]
    else:
        enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mid), "-an"] + enc + [str(out)], check=True,
                   creationflags=NO_WINDOW)
    mid.unlink(missing_ok=True)
    return {"status": "ok", "output": out.relative_to(job).as_posix(), "mb": round(out.stat().st_size / 1e6, 1),
            "render_s": round(t1 - t0, 1), "encode_s": round(time.time() - t1, 1),
            "note": "Picture only (no audio). Composite or mux it with the engine/ffmpeg."}, False


TOOLS = {
    "ae_run": (tool_ae_run, {
        "description": (
            "Run ExtendScript (ES3: var/function only, no let/const/arrow/JSON) in a fresh After Effects against "
            "<job_dir>/<project> (created when missing; saved afterwards unless save=false). Your script is a "
            "function body: `return` a plain object/array/number/string as the result. Globals: DATA (your `data`), "
            "JOB, path(rel), log(s), and lib.jsx helpers: comp(name,w,h,fps,dur), layerByName, keys(prop,[[t,v,ease]]), "
            "tr(layer,'pos'|'scale'|'rot'|'op'|'anchor'), span, fx, blurFx, glowFx, motionBlur, solid, adjustment, "
            "nullAt, shapeRect, rectSize, shapeEllipse, text(comp,str,{font,size,color,just,x,y,anchor}), textRect, "
            "revealIn, exitBlur, footage(rel), image(comp,rel,x,y,mode,w,h,t0,t1), roundRectShape, addMask. "
            "Non-ASCII text is fine inside string literals. Each call takes ~10-20 s. Result has status, result, log, "
            "comps, and on error message + line (line within your script)."),
        "inputSchema": {"type": "object", "required": ["job_dir", "script"], "properties": {
            "job_dir": {"type": "string", "description": "Absolute job folder"},
            "script": {"type": "string", "description": "ExtendScript function body"},
            "project": {"type": "string", "description": "Project path relative to job_dir (default ae/project.aep)"},
            "data": {"description": "Any JSON passed to the script as DATA (use it for text, numbers, file names)"},
            "save": {"type": "boolean", "description": "Save the project after the script (default true)"}}}}),
    "ae_frames": (tool_ae_frames, {
        "description": ("Render single frames of a comp to PNG (aerender) so you can look at your work: Read each "
                        "returned file. Up to %d times per call; scale 0.5 by default." % MAX_FRAMES),
        "inputSchema": {"type": "object", "required": ["job_dir", "comp", "times"], "properties": {
            "job_dir": {"type": "string"}, "comp": {"type": "string"},
            "times": {"type": "array", "items": {"type": "number"}, "description": "Seconds in the comp"},
            "project": {"type": "string"}, "out_dir": {"type": "string", "description": "default ae/frames"},
            "scale": {"type": "number", "description": "0.1..1, default 0.5"}}}}),
    "ae_render": (tool_ae_render, {
        "description": ("Render a comp with aerender (picture only) and encode it: H.264 .mp4, or with alpha=true a "
                        "ProRes 4444 .mov to composite over the raw video. Default output ae/render/<comp>.mp4|mov."),
        "inputSchema": {"type": "object", "required": ["job_dir", "comp"], "properties": {
            "job_dir": {"type": "string"}, "comp": {"type": "string"}, "project": {"type": "string"},
            "output": {"type": "string"}, "alpha": {"type": "boolean"}}}}),
}


# ---------- MCP stdio ----------

def reply(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg):
    method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
    if mid is None:                       # notification
        return
    if method == "initialize":
        return reply(mid, {"protocolVersion": params.get("protocolVersion") or "2025-06-18",
                           "capabilities": {"tools": {}}, "serverInfo": {"name": "ae", "version": VERSION}})
    if method == "ping":
        return reply(mid, {})
    if method == "tools/list":
        return reply(mid, {"tools": [dict(name=n, **spec) for n, (_, spec) in TOOLS.items()]})
    if method == "tools/call":
        name = params.get("name")
        if name not in TOOLS:
            return reply(mid, error={"code": -32602, "message": "unknown tool: %s" % name})
        try:
            data, is_error = TOOLS[name][0](params.get("arguments") or {})
        except ToolError as e:
            data, is_error = {"status": "refused", "message": str(e)}, True
        except Exception as e:            # never crash the server on one bad call
            data, is_error = {"status": "error", "message": "%s: %s" % (type(e).__name__, e),
                              "trace": traceback.format_exc()[-1500:]}, True
        return reply(mid, {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=1)}],
                           "isError": bool(is_error)})
    return reply(mid, error={"code": -32601, "message": "method not found: %s" % method})


def main():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply(None, error={"code": -32700, "message": "parse error"})
            continue
        handle(msg)


if __name__ == "__main__":
    main()
