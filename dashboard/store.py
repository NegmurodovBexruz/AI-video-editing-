"""Job folders on disk: projects/jobs/<id>/ with job.json, input/, out/, logs."""
import datetime
import json
import os
import re
import threading
import uuid
from pathlib import Path

import config

_lock = threading.RLock()
ID_RE = re.compile(r"[A-Za-z0-9_-]{6,80}")
STATES = ("draft", "queued", "running", "done", "failed", "cancelled")


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ---------- styles ----------

def _frontmatter(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    out = {}
    if text.startswith("---"):
        block = text.split("---", 2)[1]
        for line in block.splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def _notes():
    notes = {}
    for f in dict.fromkeys([config.STYLE_NOTES, config.NEW_STYLE_NOTES]):
        if f.exists():
            notes.update(json.loads(f.read_text(encoding="utf-8")))
    return notes


def _skill_dirs():
    dirs = {}
    for root in dict.fromkeys([config.SKILLS, config.NEW_SKILLS]):
        if root.exists():
            for p in root.iterdir():
                if p.is_dir() and (p / "SKILL.md").exists():
                    dirs.setdefault(p.name, p)
    return dirs


def styles():
    notes = _notes()
    deleted = deleted_styles()
    out = []
    for name, d in sorted(_skill_dirs().items()):
        if name in deleted:
            continue
        sk = d / "SKILL.md"
        fm = _frontmatter(sk)
        n = notes.get(d.name, {})
        desc = fm.get("description", "")
        out.append({
            "name": d.name,
            "title": n.get("title", d.name),
            "def": n.get("def") or n.get("fits", ""),
            "fits": n.get("fits", ""),
            "look": n.get("look", desc[:220] + ("…" if len(desc) > 220 else "")),
            "tested": bool(n.get("tested", False)),
            "agency": bool(n.get("built_from_refs", False)),
            "from_company": n.get("from_company"),
            "order": n.get("order", 99),
        })
    out.sort(key=lambda s: (s["order"], s["name"]))
    return out


def levels():
    return {
        "rate": config.CREDITS_PER_USD, "default": config.DEFAULT_LEVEL, "max_usd": config.MAX_USD_CAP,
        "levels": [{"id": k, "title": v["title"], "min": v["credits"][0], "max": v["credits"][1]}
                   for k, v in config.LEVELS.items()],
        "formats": [dict(id=k, **v) for k, v in config.FORMATS.items()], "default_format": config.DEFAULT_FORMAT,
        "est": {"base": config.EST_BASE_MIN, "per_sec": config.EST_PER_SEC, "level_add": config.EST_LEVEL_ADD,
                "revision": config.EST_REVISION_MIN},
        "low_balance": config.LOW_BALANCE_KR, "min_short_side": config.MIN_SHORT_SIDE,
        "retention_days": config.RETENTION_DAYS,
    }


def estimate_minutes(seconds, level):
    m = config.EST_BASE_MIN + config.EST_PER_SEC * float(seconds or 0) + config.EST_LEVEL_ADD.get(level or "std", 0)
    return max(5, round(m))


def balance_info():
    """Last Higgsfield balance an agent reported (the dashboard cannot ask Higgsfield itself)."""
    best = None
    for j in all_jobs():
        runs = [(j.get("finished"), j.get("balance_after"))] + [(v.get("finished"), v.get("balance_after")) for v in j.get("versions") or []]
        for at, kr in runs:
            if isinstance(kr, (int, float)) and at and (best is None or at > best[0]):
                best = (at, kr)
    if not best:
        return None
    return {"kr": best[1], "at": best[0], "low": best[1] < config.LOW_BALANCE_KR, "threshold": config.LOW_BALANCE_KR}


def probe(path):
    """ffprobe: size, duration, fps, audio. Raises ValueError when the file is not a readable video."""
    import subprocess
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
                           capture_output=True, text=True, timeout=60)
        info = json.loads(r.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        raise ValueError("Videoni o'qib bo'lmadi (ffprobe)")
    vs = [s for s in info.get("streams", []) if s.get("codec_type") == "video" and s.get("disposition", {}).get("attached_pic") != 1]
    if not vs:
        raise ValueError("Faylda video oqimi yo'q")
    v = vs[0]
    w, h = int(v.get("width") or 0), int(v.get("height") or 0)
    rot = str((v.get("tags") or {}).get("rotate", "")) or next((str(int(abs(d.get("rotation", 0)))) for d in v.get("side_data_list", []) if "rotation" in d), "")
    if rot in ("90", "270"):
        w, h = h, w
    num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
    fps = round(float(num) / float(den or 1), 3) if float(den or 1) else 0
    dur = float(info.get("format", {}).get("duration") or v.get("duration") or 0)
    return {"w": w, "h": h, "fps": fps, "duration": round(dur, 2),
            "audio": any(s.get("codec_type") == "audio" for s in info.get("streams", []))}


def svg_size(path):
    """Measure an SVG (width/height or viewBox) without rendering it. Raises ValueError for a broken file."""
    import re as _re
    import xml.etree.ElementTree as ET
    try:
        root = ET.parse(str(path)).getroot()
    except ET.ParseError as e:
        raise ValueError("SVG fayl buzilgan: %s" % e)
    if not root.tag.lower().endswith("svg"):
        raise ValueError("Bu SVG fayl emas")
    num = lambda v: float(m.group(1)) if (m := _re.match(r"\s*([0-9.]+)", v or "")) else None
    w, h = num(root.get("width")), num(root.get("height"))
    vb = (root.get("viewBox") or "").replace(",", " ").split()
    if (not w or not h) and len(vb) == 4:
        w, h = float(vb[2]), float(vb[3])
    return {"w": int(round(w or 1000)), "h": int(round(h or 1000))}


def probe_image(path):
    """Width/height of a still (ffprobe reads png/jpg/webp/gif). Raises ValueError when unreadable."""
    import subprocess
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "json", str(path)], capture_output=True, text=True, timeout=60)
        st = (json.loads(r.stdout or "{}").get("streams") or [{}])[0]
        w, h = int(st.get("width") or 0), int(st.get("height") or 0)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        w = h = 0
    if not w or not h:
        raise ValueError("Rasmni o'qib bo'lmadi")
    return {"w": w, "h": h}


def style_names():
    return {s["name"] for s in styles()}


def deleted_styles():
    f = config.DELETED_STYLES
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def reserved_style_names():
    """Keep deleted names reserved: historical edits still need their original files."""
    return set(_skill_dirs()) | set(_notes()) | set(deleted_styles())


def delete_style(name):
    """Remove from future selection, retaining assets for queued edits and revisions."""
    if not STYLE_NAME_RE.fullmatch(name or ""):
        raise ValueError("Uslub nomi noto'g'ri")
    with _lock:
        deleted = deleted_styles()
        if name not in deleted:
            if name not in _skill_dirs():
                raise KeyError(name)
            deleted[name] = {"deleted_at": now()}
            f = config.DELETED_STYLES
            f.parent.mkdir(parents=True, exist_ok=True)
            tmp = f.with_name(f.name + ".tmp")
            tmp.write_text(json.dumps(deleted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            os.replace(tmp, f)
    return {"deleted": name}


# ---------- new styles built from client references ----------

STYLE_NAME_RE = re.compile(r"[a-z][a-z0-9_]{2,40}")


def renderer_problem(skill_dir):
    """A new style must ship an engine renderer (renderer.py) that passes the contract check. Returns an error or None.
    Run in the agent's Python (numpy, cv2) as a separate process, so a broken file can never hurt the server."""
    import subprocess
    script = config.ROOT / "engine" / "core" / "styles_loader.py"
    try:
        r = subprocess.run([str(config.AGENT_PYTHON), "-I", str(script), "check", str(skill_dir)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "Renderer tekshiruvi ishga tushmadi: %s" % e
    if r.returncode != 0:
        return "Uslub renderer'i yaroqsiz: %s" % " ".join((r.stdout or r.stderr or "?").split())[:400]
    if not (Path(skill_dir) / "renderer_example.json").is_file():
        return "renderer_example.json yo'q (agent renderer'ni namuna edit.json bilan topshirishi kerak)"
    return None


def register_style(name, note, company=None):
    """Validate a skill folder the agent built and add its card to the style list. Returns an error or None."""
    if not STYLE_NAME_RE.fullmatch(name or ""):
        return "Uslub nomi noto'g'ri: %r (kichik lotin harflari, raqam, _)" % name
    if name in deleted_styles():
        return "Bu uslub o'chirilgan; boshqa nom tanlang: %s" % name
    d = config.NEW_SKILLS / name
    sk = d / "SKILL.md"
    if not sk.is_file():
        return "%s topilmadi" % sk
    if _frontmatter(sk).get("name") != name:
        return "SKILL.md dagi name '%s' papka nomiga teng emas" % _frontmatter(sk).get("name")
    missing = [f for f in ("captions.md", "beat-map.md", "devices.md", "motion.md", "look.md", "sound.md", "qa.md")
               if not (d / "references" / f).is_file()]
    if missing:
        return "references\\ da yo'q: %s" % ", ".join(missing)
    err = renderer_problem(d)
    if err:
        return err
    card = {k: " ".join(str(note.get(k) or "").split())[:300] for k in ("title", "def", "fits", "look")}
    if not card["title"] or not card["def"]:
        return "result.json da title va def bo'lishi kerak"
    with _lock:
        f = config.NEW_STYLE_NOTES
        notes = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        if not config.DRY_RUN and name in _notes():   # built-in + custom notes (Docker keeps them in two files)
            return "Bu nom ro'yxatda allaqachon bor: %s" % name
        order = max([v.get("order", 0) for v in _notes().values()] + [0]) + 1
        notes[name] = dict(order=order, tested=False, built_from_refs=True, from_company=company, **card)
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_name(f.name + ".tmp")
        tmp.write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(tmp, f)
    return None


# ---------- companies ----------

def companies():
    f = config.COMPANIES
    if not f.exists():
        return []
    return json.loads(f.read_text(encoding="utf-8"))


def _save_companies(items):
    f = config.COMPANIES
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.name + ".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, f)


def _initials(name):
    words = [w for w in re.split(r"[\s\-_.]+", name) if w]
    s = "".join(w[0] for w in words[:2]) if len(words) > 1 else name[:2]
    return s.upper()


def create_company(name, note=None):
    name = " ".join((name or "").split())[:80]
    if not name:
        raise ValueError("Kompaniya nomini yozing")
    with _lock:
        items = companies()
        if any(c["name"].lower() == name.lower() for c in items):
            raise ValueError("Bunday kompaniya bor: %s" % name)
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30] or "kompaniya"
        cid, i = base, 2
        while any(c["id"] == cid for c in items):
            cid, i = "%s-%d" % (base, i), i + 1
        c = {"id": cid, "name": name, "initials": _initials(name),
             "color": config.COMPANY_COLORS[len(items) % len(config.COMPANY_COLORS)],
             "note": " ".join((note or "").split())[:200], "created": now()}
        items.append(c)
        _save_companies(items)
    return c


def update_company(cid, name=None, note=None, archived=None):
    with _lock:
        items = companies()
        c = next((x for x in items if x["id"] == cid), None)
        if not c:
            raise KeyError(cid)
        if archived is not None:          # companies are archived, never deleted
            c["archived"] = bool(archived)
        if name is not None:
            name = " ".join(name.split())[:80]
            if not name:
                raise ValueError("Kompaniya nomini yozing")
            if any(x["name"].lower() == name.lower() and x["id"] != cid for x in items):
                raise ValueError("Bunday kompaniya bor: %s" % name)
            c["name"], c["initials"] = name, _initials(name)
        if note is not None:
            c["note"] = " ".join(note.split())[:200]
        _save_companies(items)
    return c


def _company_id(company):
    company = (company or "").strip() or None
    if company:
        c = next((x for x in companies() if x["id"] == company), None)
        if not c:
            raise ValueError("Bunday kompaniya yo'q: %s" % company)
        if c.get("archived"):
            raise ValueError("Kompaniya arxivlangan: %s" % c["name"])
    return company


def set_job_company(job_id, company):
    return update(job_id, company=_company_id(company))


def set_job_archived(job_id, archived):
    job = load(job_id)
    if archived and job["state"] in ("queued", "running"):
        raise ValueError("Ishlayotgan ishni arxivlab bo'lmaydi")
    return update(job_id, archived=bool(archived))


# ---------- job files ----------

def job_dir(job_id):
    if not ID_RE.fullmatch(job_id or ""):
        raise KeyError(job_id)
    d = config.JOBS / job_id
    if not (d / "job.json").exists():
        raise KeyError(job_id)
    return d


def load(job_id):
    with _lock:
        return json.loads((job_dir(job_id) / "job.json").read_text(encoding="utf-8"))


def _save(d, job):
    tmp = d / "job.json.tmp"
    tmp.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    # Windows refuses to replace a file another thread or process has open for reading (a UI poll, an
    # antivirus scan): retry briefly instead of losing the update.
    for attempt in range(20):
        try:
            os.replace(tmp, d / "job.json")
            return
        except PermissionError:
            if attempt == 19:
                raise
            import time
            time.sleep(0.05 * (attempt + 1))


def update(job_id, **fields):
    with _lock:
        d = job_dir(job_id)
        job = json.loads((d / "job.json").read_text(encoding="utf-8"))
        job.update(fields)
        _save(d, job)
        return job


AUTO = "auto"          # no style chosen: the agent picks the best-fitting style itself


def _credit_cap(level, usd_cap, credit_cap):
    """A level or standalone $ limit -> credits. Combined caps and bare credits support older clients."""
    if level is None and usd_cap is None and credit_cap is not None:
        try:
            cap = float(credit_cap)
        except (TypeError, ValueError):
            raise ValueError("Kredit limiti son bo'lishi kerak")
        if not 0 <= cap <= config.MAX_CREDIT_CAP:
            raise ValueError("Kredit limiti 0 dan %d gacha bo'lishi kerak" % config.MAX_CREDIT_CAP)
        return None, None, cap
    custom = level is None and usd_cap not in (None, "")
    level = None if custom else (level or config.DEFAULT_LEVEL)
    if not custom and level not in config.LEVELS:
        raise ValueError("Bunday daraja yo'q: %s" % level)
    cap = None if custom else float(config.LEVELS[level]["credits"][1])
    usd = None
    if usd_cap not in (None, ""):
        try:
            usd = float(usd_cap)
        except (TypeError, ValueError):
            raise ValueError("Dollar limiti son bo'lishi kerak")
        if not 0 <= usd <= config.MAX_USD_CAP:
            raise ValueError("Dollar limiti 0 dan %d gacha bo'lishi kerak" % config.MAX_USD_CAP)
        usd_credits = float(int(usd * config.CREDITS_PER_USD))
        cap = usd_credits if custom else min(cap, usd_credits)
    return level, usd, cap


def create_style_job(title, ref_text, company=None):
    """'Uslub yaratish': the client uploads reference videos, the agent builds a new style plugin. No credits."""
    company = _company_id(company)
    jid = "%s-newstyle-%s" % (datetime.datetime.now().strftime("%y%m%d-%H%M%S"), uuid.uuid4().hex[:4])
    d = config.JOBS / jid
    with _lock:
        (d / "input" / "refs").mkdir(parents=True)
        refs = []
        if (ref_text or "").strip():
            (d / "input" / "refs" / "brief.txt").write_text(ref_text.strip() + "\n", encoding="utf-8")
            refs.append("brief.txt")
        job = {
            "id": jid, "kind": "style", "title": (title or "").strip()[:120], "style": "new_style", "company": company,
            "level": None, "usd_cap": None, "credit_cap": 0.0, "level_cap": 0.0,
            "created": now(), "session_id": str(uuid.uuid4()), "state": "draft", "raw": [], "refs": refs,
        }
        _save(d, job)
    return job


SAVEABLE_SOURCES = ("reference", "plugin+reference", "web", "own")


def save_style_from_job(job_id, title):
    """'Shu uslubni saqlash': turn the look of a finished video into a new style plugin (a style-building job).
    Samples = the job's reference videos + the finished video itself (the user liked it, so it is a second,
    independent sample of the same look: the rule of two holds even with one reference). The style card and the
    user's words go in as notes. Files are copied, so the source job's retention never touches the new job."""
    import shutil
    src = load(job_id)
    d0 = job_dir(job_id)
    if src.get("kind") == "style":
        raise ValueError("Bu uslub yaratish ishi")
    if src["state"] != "done" or not src.get("video") or src.get("expired"):
        raise ValueError("Uslubni faqat tayyor (muddati tugamagan) videodan saqlash mumkin")
    if src.get("style_source") not in SAVEABLE_SOURCES:
        raise ValueError("Bu video tayyor uslubda (%s) qilingan: u allaqachon ro'yxatda bor" % (src.get("style_used") or src.get("style")))
    refs = [r for r in src.get("refs", []) if Path(r).suffix.lower() in config.VIDEO_EXT]
    if len(refs) + 1 < config.STYLE_JOB_MIN_VIDEOS:
        raise ValueError("Kamida %d ta namuna kerak: bu ishda referens video yo'q" % config.STYLE_JOB_MIN_VIDEOS)
    title = (title or "").strip() or ("%s uslubi" % (src.get("title") or job_id))[:120]
    note = ["Bu uslub mijozga yoqqan videodan saqlanmoqda (ish %s)." % job_id,
            "Namunalar: referens video(lar) va shu ishning natija videosi (natija_%s.mp4). Natija ham to'liq namuna:" % job_id,
            "u referenslardan olingan ko'rinishning amaldagi ko'rinishi. Ikkalasida takrorlangan qoidalar uslub DNK'siga kiradi.",
            "style_card.md — o'sha ishda agent referensdan o'lchagan qoidalar (manbalari bilan)."]
    if (d0 / "input" / "refs" / "brief.txt").is_file():
        note += ["", "Mijozning o'sha ishdagi so'zlari:", (d0 / "input" / "refs" / "brief.txt").read_text(encoding="utf-8").strip()]
    job = create_style_job(title, "\n".join(note), src.get("company"))
    d = job_dir(job["id"])
    copied = []
    for r in refs:
        shutil.copy2(d0 / "input" / "refs" / r, d / "input" / "refs" / r)
        copied.append(r)
    fin = "natija_%s.mp4" % job_id
    shutil.copy2(d0 / src["video"], d / "input" / "refs" / fin)
    copied.append(fin)
    card = d0 / "work" / "style_card.md"
    if card.is_file():
        shutil.copy2(card, d / "input" / "refs" / "style_card.md")
        copied.append("style_card.md")
    update(job["id"], refs=job["refs"] + copied, from_job=job_id)
    update(job_id, saved_style_job=job["id"])
    return submit(job["id"])


def create(style, title, ref_text, credit_cap=None, level=None, usd_cap=None, company=None, fmt=None, ref_use=None,
           ref_like=None):
    style = (style or "").strip() or AUTO
    if style != AUTO and style not in style_names():
        raise ValueError("Bunday uslub yo'q: %s" % style)
    company = _company_id(company)
    fmt = fmt or config.DEFAULT_FORMAT
    if fmt not in config.FORMATS:
        raise ValueError("Bunday format yo'q: %s" % fmt)
    ref_use = ref_use or config.DEFAULT_REF_USE
    if ref_use not in config.REF_USES:
        raise ValueError("Referensdan nima olinishi noto'g'ri: %s" % ref_use)
    # the user's own words on what they liked in the reference videos (optional; outranks the preset above)
    ref_like = "\n".join(" ".join(x.split()) for x in str(ref_like or "").strip().splitlines() if x.strip())
    if len(ref_like) > config.REF_LIKE_MAX:
        raise ValueError("\"Referensda nima yoqdi\" juda uzun: %d belgidan oshmasin" % config.REF_LIKE_MAX)
    level, usd, cap = _credit_cap(level, usd_cap, credit_cap)
    jid = "%s-%s-%s" % (datetime.datetime.now().strftime("%y%m%d-%H%M%S"), style, uuid.uuid4().hex[:4])
    d = config.JOBS / jid
    with _lock:
        (d / "input" / "raw").mkdir(parents=True)
        (d / "input" / "refs").mkdir(parents=True)
        refs = []
        if (ref_text or "").strip():
            (d / "input" / "refs" / "brief.txt").write_text(ref_text.strip() + "\n", encoding="utf-8")
            refs.append("brief.txt")
        job = {
            "id": jid, "title": (title or "").strip()[:120], "style": style, "company": company, "format": fmt,
            "level": level, "usd_cap": usd, "credit_cap": cap, "level_cap": cap, "ref_use": ref_use,
            "ref_like": ref_like, "created": now(), "session_id": str(uuid.uuid4()),
            "state": "draft", "raw": [], "refs": refs,
        }
        _save(d, job)
    return job


def _safe_name(name):
    base = Path(name.replace("\\", "/")).name
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", base).strip(" .") or "file"
    return base[:150]


def save_upload(job_id, kind, name, stream, length, note=None, required=False):
    """Stream an uploaded file into input/raw, input/refs or input/materials (extra images and clips for the edit)."""
    job = load(job_id)
    if job["state"] != "draft":
        raise ValueError("Fayl faqat ish boshlanishidan oldin qo'shiladi")
    name = _safe_name(name)
    ext = Path(name).suffix.lower()
    if kind == "raw":
        if job.get("kind") == "style":
            raise ValueError("Uslub yaratishda videolar referens sifatida yuklanadi")
        if ext not in config.VIDEO_EXT:
            raise ValueError("Raw video formati qo'llanmaydi: %s" % ext)
        sub = "raw"
    elif kind == "ref":
        if ext not in config.VIDEO_EXT | config.REF_DOC_EXT:
            raise ValueError("Referens faqat .md, .txt yoki video bo'ladi: %s" % ext)
        if name.lower() == "brief.txt":
            name = "brief_file.txt"
        sub = "refs"
    elif kind == "mat":
        if job.get("kind") == "style":
            raise ValueError("Uslub yaratish ishiga material qo'shilmaydi")
        if ext not in config.VIDEO_EXT | config.IMAGE_EXT | {".svg"}:
            raise ValueError("Material rasm (png, jpg, webp, svg) yoki video (mp4, mov…) bo'ladi: %s" % ext)
        sub = "materials"
    else:
        raise ValueError("kind raw, ref yoki mat bo'lishi kerak")
    folder = job_dir(job_id) / "input" / sub
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    i = 2
    while target.exists():
        target = folder / ("%s_%d%s" % (Path(name).stem, i, Path(name).suffix))
        i += 1
    part = target.with_name(target.name + ".part")
    left = length
    with open(part, "wb") as f:
        while left > 0:
            chunk = stream.read(min(1 << 20, left))
            if not chunk:
                break
            f.write(chunk)
            left -= len(chunk)
    if left:
        part.unlink(missing_ok=True)
        raise ValueError("Yuklash uzilib qoldi")
    os.replace(part, target)
    info = None
    if kind == "raw":          # input check: a readable video, shorter side >= 720 px (720p is accepted)
        try:
            info = probe(target)
        except ValueError:
            target.unlink(missing_ok=True)
            raise
        if min(info["w"], info["h"]) < config.MIN_SHORT_SIDE:
            target.unlink(missing_ok=True)
            raise ValueError("Video sifati past: %d×%d. Kamida 720p kerak (qisqa tomoni %d px)."
                             % (info["w"], info["h"], config.MIN_SHORT_SIDE))
        info["name"] = target.name
    if kind == "mat":
        # Every material is kept exactly as uploaded (no server-side conversion). A vector (SVG) is only measured;
        # the agent draws it at the size it needs. A blurry still is improved by the agent (AI upscale/regeneration).
        vector = ext == ".svg"
        try:
            mi = svg_size(target) if vector else probe(target) if ext in config.VIDEO_EXT else probe_image(target)
        except ValueError:
            target.unlink(missing_ok=True)
            raise
        is_video = ext in config.VIDEO_EXT
        low = (not vector) and min(mi["w"], mi["h"]) < (config.MIN_SHORT_SIDE if is_video else config.MAT_IMAGE_MIN_SIDE)
        rec = {"name": target.name, "kind": "video" if is_video else "image", "w": mi["w"], "h": mi["h"],
               "duration": mi.get("duration"), "note": " ".join(str(note or "").split())[:300],
               "required": bool(required), "low": low, "vector": vector}
        with _lock:
            job = load(job_id)
            job["materials"] = job.get("materials", []) + [rec]
            _save(job_dir(job_id), job)
        return target.name
    with _lock:
        job = load(job_id)
        key = "raw" if kind == "raw" else "refs"
        job[key] = job.get(key, []) + [target.name]
        if info:
            job["raw_info"] = job.get("raw_info", []) + [info]
        _save(job_dir(job_id), job)
    return target.name


def submit(job_id):
    job = load(job_id)
    if job["state"] != "draft":
        raise ValueError("Ish allaqachon yuborilgan")
    if job.get("kind") != "style" and job["style"] in deleted_styles():
        raise ValueError("Bu uslub o'chirilgan. Yangi video uchun boshqa uslub tanlang")
    if job.get("kind") == "style":
        n = sum(1 for r in job.get("refs", []) if Path(r).suffix.lower() in config.VIDEO_EXT)
        if n < config.STYLE_JOB_MIN_VIDEOS:
            raise ValueError("Uslub yaratish uchun kamida %d ta video kerak" % config.STYLE_JOB_MIN_VIDEOS)
    elif not job.get("raw"):
        raise ValueError("Kamida bitta raw video kerak")
    secs = sum(i.get("duration", 0) for i in job.get("raw_info") or [])
    est = estimate_minutes(secs, job.get("level")) if job.get("kind") != "style" else 30
    return update(job_id, state="queued", queued_at=now(), est_minutes=est)


# ---------- feedback / revisions ----------
# A finished job can be sent back with the user's notes. The current result is archived to
# versions/v<N>/, the notes go to feedback/r<N>/, and the job is queued again as revision N.

FEEDBACK_STATES = ("done", "failed", "cancelled")
FB_EXT = config.VIDEO_EXT | config.REF_DOC_EXT | {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf",
                                                   ".mp3", ".wav", ".m4a", ".aac", ".srt", ".json"}
MAX_FEEDBACK_TEXT = 20_000


def save_feedback_file(job_id, name, stream, length):
    """Stream one feedback attachment into feedback/pending/ (moved into the revision on send)."""
    job = load(job_id)
    if job.get("kind") == "style":
        raise ValueError("Uslub yaratish ishiga tuzatish yuborilmaydi")
    if job["state"] not in FEEDBACK_STATES:
        raise ValueError("Tuzatish faqat tugagan ishga yuboriladi")
    if job.get("expired"):
        raise ValueError("Bu ishning saqlash muddati tugagan, fayllari o'chirilgan")
    name = _safe_name(name)
    if Path(name).suffix.lower() not in FB_EXT:
        raise ValueError("Bu fayl turi qabul qilinmaydi: %s" % Path(name).suffix)
    folder = job_dir(job_id) / "feedback" / "pending"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    i = 2
    while target.exists():
        target = folder / ("%s_%d%s" % (Path(name).stem, i, Path(name).suffix))
        i += 1
    part = target.with_name(target.name + ".part")
    left = length
    with open(part, "wb") as f:
        while left > 0:
            chunk = stream.read(min(1 << 20, left))
            if not chunk:
                break
            f.write(chunk)
            left -= len(chunk)
    if left:
        part.unlink(missing_ok=True)
        raise ValueError("Yuklash uzilib qoldi")
    os.replace(part, target)
    return target.name


def _archive_current(d, job):
    """Move the current result into versions/v<N>/ and return its record (or None if no video)."""
    n = len(job.get("versions") or []) + 1
    video = d / (job.get("video") or "out/final.mp4")
    if not video.is_file():
        return None
    vdir = d / "versions" / ("v%d" % n)
    vdir.mkdir(parents=True, exist_ok=True)
    os.replace(video, vdir / "final.mp4")
    for extra in list((d / "out").glob("*.srt")) + [d / "result.json"]:
        if extra.is_file():
            os.replace(extra, vdir / extra.name)
    readme = d / "README.md"
    if readme.is_file():
        (vdir / "README.md").write_bytes(readme.read_bytes())   # the agent keeps editing the live README
    return {
        "n": n, "video": "versions/v%d/final.mp4" % n, "revision": job.get("revision", 0),
        "finished": job.get("finished"), "credits_spent": job.get("credits_spent"),
        "summary": job.get("summary"), "style_used": job.get("style_used"),
        "timeline": job.get("timeline"), "overall": job.get("overall"), "qa": job.get("qa"),
        "balance_after": job.get("balance_after"),
    }


def send_feedback(job_id, text, credit_cap):
    text = (text or "").strip()
    if len(text) > MAX_FEEDBACK_TEXT:
        raise ValueError("Izoh juda uzun")
    try:
        cap = float(credit_cap)
    except (TypeError, ValueError):
        raise ValueError("Kredit limiti son bo'lishi kerak")
    with _lock:
        job = load(job_id)
        max_cap = config.MAX_CREDIT_CAP
        if job.get("level") is None and job.get("usd_cap") is not None:
            max_cap = max(max_cap, job["level_cap"])
        if not 0 <= cap <= max_cap:
            raise ValueError("Kredit limiti 0 dan %d gacha bo'lishi kerak" % max_cap)
        if job.get("kind") == "style":
            raise ValueError("Uslub yaratish ishiga tuzatish yuborilmaydi")
        if job["state"] not in FEEDBACK_STATES:
            raise ValueError("Tuzatish faqat tugagan ishga yuboriladi")
        if job.get("expired"):
            raise ValueError("Bu ishning saqlash muddati tugagan, fayllari o'chirilgan. Yangi video yarating.")
        d = job_dir(job_id)
        pending = d / "feedback" / "pending"
        attached = sorted(p.name for p in pending.iterdir() if p.is_file()) if pending.exists() else []
        if not text and not attached:
            raise ValueError("Izoh yozing yoki fayl qo'shing")
        rev = int(job.get("revision", 0)) + 1
        rdir = d / "feedback" / ("r%d" % rev)
        rdir.mkdir(parents=True, exist_ok=True)
        for name in attached:
            os.replace(pending / name, rdir / name)
        (rdir / "feedback.md").write_text(text + "\n", encoding="utf-8", newline="\n")
        versions = list(job.get("versions") or [])
        rec = _archive_current(d, job)
        if rec:
            versions.append(rec)
        with open(d / "progress.log", "a", encoding="utf-8") as f:
            f.write("%s — Tuzatish %d yuborildi%s\n" % (datetime.datetime.now().strftime("%H:%M"), rev,
                                                     " (%d fayl)" % len(attached) if attached else ""))
        fb = list(job.get("feedback") or [])
        fb.append({"n": rev, "text": text, "files": attached, "created": now(), "credit_cap": cap,
                   "based_on": rec["n"] if rec else None})
        job.update(
            revision=rev, versions=versions, feedback=fb, state="queued", queued_at=now(), est_minutes=config.EST_REVISION_MIN,
            credit_cap=cap, started=None, finished=None, exit_code=None, error=None, summary=None, qa=None,
            open_issues=[], video=None, credits_spent=None, balance_before=None, balance_after=None,
            timeline=None, overall=None, auto_retries=0, auto_retry_reason=None, not_before=None,
        )
        _save(d, job)
        return job


# ---------- retry a failed run ----------
# 'Qayta yurgizish': a failed first run (e.g. a 429 from Claude) is copied into a NEW job with the same settings
# and input files, and queued. A new folder and Claude session keep the failed run's half-made files out. The
# failed job stays as a record and points to its copy (retried_as), so a double click cannot queue it twice.
# A failed revision is retried in place: the same notes and files go again as the next revision, so the
# earlier versions and the agent's session stay (the job leaves 'failed', so a double click is refused too).

RETRY_KEYS = ("kind", "title", "style", "company", "format", "level", "usd_cap", "credit_cap", "level_cap",
              "ref_use", "ref_like", "raw", "refs", "raw_info", "materials")


def _retry_revision(job):
    import shutil
    rev = int(job["revision"])
    entry = next((f for f in job.get("feedback") or [] if f.get("n") == rev), None)
    if not entry:
        raise ValueError("Tuzatish %d ning izohi topilmadi" % rev)
    d = job_dir(job["id"])
    pending = d / "feedback" / "pending"
    if pending.is_dir() and any(pending.iterdir()):
        raise ValueError("Yuborilmagan tuzatish fayllari bor: avval ularni yuboring yoki olib tashlang")
    pending.mkdir(parents=True, exist_ok=True)
    src_dir = d / "feedback" / ("r%d" % rev)
    for name in entry.get("files") or []:
        if (src_dir / name).is_file():
            shutil.copy2(src_dir / name, pending / name)
    try:
        out = send_feedback(job["id"], entry.get("text") or "", entry.get("credit_cap", job.get("credit_cap", 20)))
    except Exception:
        for p in pending.iterdir():
            p.unlink(missing_ok=True)
        raise
    with open(d / "progress.log", "a", encoding="utf-8") as f:
        f.write("%s — Tuzatish %d qayta yurgizildi (tuzatish %d sifatida)\n"
                % (datetime.datetime.now().strftime("%H:%M"), rev, out["revision"]))
    return out


def retry_job(job_id):
    import shutil
    with _lock:
        src = load(job_id)
        if src["state"] != "failed":
            raise ValueError("Faqat xato bilan tugagan ish qayta yurgiziladi")
        if src.get("expired"):
            raise ValueError("Bu ishning saqlash muddati tugagan, fayllari o'chirilgan. Yangi video yarating.")
        if src.get("revision"):
            return _retry_revision(src)
        if src.get("retried_as"):
            raise ValueError("Bu ish allaqachon qayta yurgizilgan: %s" % src["retried_as"])
        if src.get("kind") != "style" and src["style"] in deleted_styles():
            raise ValueError("Bu uslub o'chirilgan. Yangi video uchun boshqa uslub tanlang")
        d0 = job_dir(job_id)
        if not (d0 / "input").is_dir():
            raise ValueError("Ishning kirish fayllari topilmadi")
        tag = "newstyle" if src.get("kind") == "style" else src["style"]
        jid = "%s-%s-%s" % (datetime.datetime.now().strftime("%y%m%d-%H%M%S"), tag, uuid.uuid4().hex[:4])
        update(job_id, retried_as=jid)          # claim first: the copy below runs outside the lock
    d = config.JOBS / jid
    try:
        shutil.copytree(d0 / "input", d / "input")
        job = {k: src[k] for k in RETRY_KEYS if k in src}
        job.update(id=jid, created=now(), session_id=str(uuid.uuid4()), state="draft", retry_of=job_id)
        with _lock:
            _save(d, job)
        job = submit(jid)
    except Exception:
        shutil.rmtree(d, ignore_errors=True)
        update(job_id, retried_as=None)
        raise
    with open(d0 / "progress.log", "a", encoding="utf-8") as f:
        f.write("%s — Qayta yurgizildi: yangi ish %s\n" % (datetime.datetime.now().strftime("%H:%M"), jid))
    return job


def list_ids():
    if not config.JOBS.exists():
        return []
    return [p.name for p in config.JOBS.iterdir() if (p / "job.json").exists()]


def all_jobs():
    out = []
    for jid in list_ids():
        try:
            out.append(_with_expiry(load(jid)))
        except (KeyError, ValueError, OSError):
            continue
    out.sort(key=lambda j: j.get("created", ""), reverse=True)
    return out


def next_queued():
    t = now()
    q = [j for j in all_jobs() if j.get("state") == "queued" and not (j.get("not_before") and j["not_before"] > t)]
    q.sort(key=lambda j: j.get("queued_at", j.get("created", "")))
    return q[0] if q else None


# ---------- what the agent wrote ----------

def progress(job_id, limit=200):
    p = job_dir(job_id) / "progress.log"
    if not p.exists():
        return []
    raw = p.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[-limit:]


def _short(v, n):
    v = " ".join(str(v).split())
    return v if len(v) <= n else v[: n - 1] + "…"


def _tool_line(name, inp):
    inp = inp or {}
    if name.startswith("mcp__higgsfield__"):
        return "Higgsfield: " + name[len("mcp__higgsfield__"):]
    if name in ("PowerShell", "Bash"):
        return "%s: %s" % (name, _short(inp.get("command", ""), 160))
    if name in ("Read", "Write", "Edit"):
        return "%s: %s" % (name, _short(inp.get("file_path", ""), 160))
    if name == "Skill":
        return "Skill: " + str(inp.get("skill", ""))
    if name in ("Grep", "Glob"):
        return "%s: %s" % (name, _short(inp.get("pattern", ""), 120))
    if name in ("WebSearch", "WebFetch"):
        return "%s: %s" % (name, _short(inp.get("query") or inp.get("url", ""), 140))
    return name


def activity(job_id, limit=80):
    """Readable events from the agent's stream-json log (tail only)."""
    p = job_dir(job_id) / "agent.log"
    if not p.exists():
        return [], None
    size = p.stat().st_size
    with open(p, "rb") as f:
        f.seek(max(0, size - 600_000))
        data = f.read()
    events, result = [], None
    for line in data.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        t = o.get("type")
        if t == "system" and o.get("subtype") == "init":
            events.append({"k": "init", "v": "Claude Code ishga tushdi (%s)" % o.get("model", "")})
        elif t == "assistant":
            for c in (o.get("message") or {}).get("content") or []:
                if c.get("type") == "text" and c.get("text", "").strip():
                    events.append({"k": "text", "v": _short(c["text"], 500)})
                elif c.get("type") == "tool_use":
                    events.append({"k": "tool", "v": _tool_line(c.get("name", ""), c.get("input"))})
        elif t == "result":
            result = {
                "subtype": o.get("subtype"), "is_error": o.get("is_error"),
                "text": _short(o.get("result", ""), 2000), "turns": o.get("num_turns"),
                "duration_ms": o.get("duration_ms"),
            }
    return events[-limit:], result


def outputs(job_id):
    d = job_dir(job_id)
    files = []
    for sub in ("out", "."):
        folder = d / sub
        if not folder.exists():
            continue
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix.lower() in {".mp4", ".mov", ".srt", ".md", ".json"} \
                    and f.name not in {"job.json", "AGENT_TASK.md"}:
                rel = f.relative_to(d).as_posix()
                files.append({"path": rel, "size": f.stat().st_size})
    return files


def detail(job_id):
    job = _with_expiry(load(job_id))
    events, result = activity(job_id)
    job["progress"] = progress(job_id)
    job["activity"] = events
    job["agent_result"] = result
    job["files"] = outputs(job_id)
    return job


def feedback_dir(job_id, rev):
    return job_dir(job_id) / "feedback" / ("r%d" % int(rev))


def resolve_file(job_id, rel):
    d = job_dir(job_id).resolve()
    f = (d / rel).resolve()
    if d not in f.parents or not f.is_file():
        raise KeyError(rel)
    return f


# ---------- retention and deletion ----------
# Media is kept RETENTION_DAYS after the job's last run (a new revision restarts the clock); then it is purged
# and the job record stays as "muddati tugadi". The user can also delete a finished job completely.

KEEP_EXT = {".json", ".md", ".txt", ".log", ".srt", ".py"}      # small text: the record of what was done
WIPE_DIRS = ("work", "gen")                                       # working files and AI assets: everything goes


def _last_run(job):
    return job.get("finished") or job.get("queued_at") or job.get("created")


def expires_at(job):
    if config.RETENTION_DAYS <= 0 or job.get("expired") or job.get("state") not in FEEDBACK_STATES:
        return None
    try:
        t = datetime.datetime.fromisoformat(_last_run(job))
    except (TypeError, ValueError):
        return None
    return (t + datetime.timedelta(days=config.RETENTION_DAYS)).isoformat(timespec="seconds")


def _with_expiry(job):
    job["expires_at"] = expires_at(job)
    return job


def purge_media(job_id):
    """Delete the job's media, keep its record. Returns freed bytes."""
    import shutil
    with _lock:
        job = load(job_id)
        if job["state"] not in FEEDBACK_STATES:
            raise ValueError("Ishlayotgan ishning fayllari o'chirilmaydi")
        d = job_dir(job_id)
        freed = 0
        for p in sorted(d.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            rel = p.relative_to(d)
            if p.is_file():
                if rel.parts[0] in WIPE_DIRS or p.suffix.lower() not in KEEP_EXT:
                    freed += p.stat().st_size
                    p.unlink(missing_ok=True)
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
        for w in WIPE_DIRS:
            if (d / w).exists():
                shutil.rmtree(d / w, ignore_errors=True)
        versions = [dict(v, video=None) for v in job.get("versions") or []]
        update(job_id, expired=now(), video=None, versions=versions, purged_mb=round(freed / 1e6, 1))
    with open(d / "progress.log", "a", encoding="utf-8") as f:
        f.write("%s — Saqlash muddati tugadi: videolar va fayllar o'chirildi (%.0f MB), yozuv qoldi\n"
                % (datetime.datetime.now().strftime("%H:%M"), freed / 1e6))
    return freed


def expire_old():
    """Purge every finished job whose retention time has passed. Returns [(job_id, freed_bytes)]."""
    done, t = [], now()
    for j in all_jobs():
        e = j.get("expires_at")
        if e and e <= t:
            try:
                done.append((j["id"], purge_media(j["id"])))
            except (ValueError, OSError) as ex:
                print("retention: %s: %s" % (j["id"], ex))
    return done


def delete_job(job_id):
    """Delete a finished job completely (folder and record). Returns its Claude session id."""
    import shutil
    import stat
    with _lock:
        job = load(job_id)
        if job["state"] in ("queued", "running"):
            raise ValueError("Ish hali ishlayapti: avval to'xtating, keyin o'chiring")
        d = job_dir(job_id)

        def _force(func, path, _exc):           # Windows: read-only files
            os.chmod(path, stat.S_IWRITE)
            func(path)
        try:
            shutil.rmtree(d, onerror=_force)
        except OSError as e:
            raise ValueError("O'chirib bo'lmadi (fayl band bo'lishi mumkin, sahifani yangilab qayta urining): %s" % e)
    return job.get("session_id")
