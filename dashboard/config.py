"""Paths and settings for the editing dashboard (AP-1077).

Every path can be overridden from the environment, so the same code runs on this Windows PC (defaults below)
and in the Linux Docker image (see Dockerfile / docker-compose.yml, which set DASH_DATA, DASH_STYLES, ...).
"""
import os
import sys
from pathlib import Path

IS_WIN = os.name == "nt"
DASH = Path(__file__).resolve().parent
ROOT = DASH.parent                      # code root: D:\projects\higgsfield test01 (or /app in Docker)
STATIC = DASH / "static"
# Data root: jobs, companies, login data. Docker mounts a volume here.
DATA = Path(os.environ.get("DASH_DATA", str(ROOT / "projects")))
STYLES = Path(os.environ.get("DASH_STYLES", str(ROOT / "styles")))   # the `styles` plugin

HOST = os.environ.get("DASH_HOST", "127.0.0.1")     # Docker: 0.0.0.0 (the reverse proxy is the only way in)
PORT = int(os.environ.get("DASH_PORT", "8050"))
# Host headers the server answers to (besides localhost), e.g. "montaj.example.uz".
ALLOWED_HOSTS = {"127.0.0.1", "localhost"} | {h.strip().lower() for h in os.environ.get("DASH_ALLOWED_HOSTS", "").split(",") if h.strip()}

_WIN_PY = r"D:\projects\agentic team for editing\.venv\Scripts\python.exe"
# Python the agent uses for the compositor scripts (numpy, opencv, onnxruntime, PIL).
AGENT_PYTHON = Path(os.environ.get("DASH_AGENT_PYTHON", _WIN_PY if IS_WIN else sys.executable))

# DASH_DRY_RUN=1 runs dev/fake_agent.py instead of Claude Code: no credits, no tokens.
DRY_RUN = os.environ.get("DASH_DRY_RUN") == "1"

# After Effects mode (local Windows PC only): when AE is installed, the agent gets the ae_mcp tools for motion
# graphics. DASH_AE=0 switches it off. AE does not exist on Linux, so the Docker server never has it.
AE_DIR = Path(os.environ.get("AE_DIR", r"D:\AE\Adobe\Adobe After Effects 2025\Support Files"))
AE_MCP = ROOT / "ae_mcp" / "server.py"
AE_ENABLED = (os.environ.get("DASH_AE", "auto") != "0" and IS_WIN and (AE_DIR / "AfterFX.com").exists()
              and AE_MCP.exists())
# A dry-run server keeps its own jobs folder, so a real server never picks up test jobs (and vice versa).
JOBS = DATA / ("jobs_dryrun" if DRY_RUN else "jobs")

# Style plugins built from client reference videos ("Uslub yaratish") go next to the other skills and
# are listed at once. A dry run writes them to its own jobs folder so tests never touch the real plugin.
SKILLS = STYLES / "skills"
NEW_SKILLS = (JOBS / "_dry_skills") if DRY_RUN else SKILLS
STYLE_NOTES = DASH / "style_notes.json"
NEW_STYLE_NOTES = (JOBS / "_dry_style_notes.json") if DRY_RUN else Path(os.environ.get("DASH_STYLE_NOTES", str(STYLE_NOTES)))
# Persist catalogue removals outside the built-in plugin copied at container startup.
DELETED_STYLES = (JOBS / "_deleted_styles.json") if DRY_RUN else (DATA / "deleted_styles.json")
STYLE_JOB_MIN_VIDEOS = 2
# Client companies of the agency (jobs carry a "company" id; job folders never move).
COMPANIES = (JOBS / "_companies.json") if DRY_RUN else (DATA / "companies.json")
COMPANY_COLORS = ["#2563eb", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#db2777", "#475569"]
# faster-whisper for engine/core/asr_worker.py (own venv on the PC; the same Python in Docker)
ASR_PYTHON = Path(os.environ.get("DASH_ASR_PYTHON", r"D:\projects\plugin_style\.venv\Scripts\python.exe" if IS_WIN else sys.executable))

# ---- login ----
# DASH_AUTH=1 turns the login on (always on in Docker). The first start creates the admin from
# DASH_ADMIN_USER / DASH_ADMIN_PASSWORD; after that the password lives (hashed) in AUTH_DIR/users.json
# and is changed from the dashboard. Local runs on this PC keep it off unless asked.
AUTH = os.environ.get("DASH_AUTH") == "1"
AUTH_DIR = (JOBS / "_auth") if DRY_RUN else (DATA / "auth")
ADMIN_USER = os.environ.get("DASH_ADMIN_USER", "")
ADMIN_PASSWORD = os.environ.get("DASH_ADMIN_PASSWORD", "")
COOKIE_SECURE = os.environ.get("DASH_COOKIE_SECURE") == "1"   # set behind HTTPS
SESSION_DAYS = 14
MIN_PASSWORD = 8

# The agent's shell, as told in its task (tool names and quoting differ).
SHELL_LINE = ("Windows, PowerShell. `ffmpeg` and `ffprobe` are on PATH." if IS_WIN else
              "Linux (Docker), Bash. `ffmpeg` and `ffprobe` are on PATH. Paths use `/`.")

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm", ".mxf", ".mts"}
# Extra materials the user adds to the edit (photos, logos, B-roll clips): input/materials/.
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAT_IMAGE_MIN_SIDE = 600         # a still smaller than this on its short side is flagged as low quality (not refused)
# "Referensdan nima olinsin?" (form): how strongly reference videos drive the look. Default: the whole look.
REF_USES = {
    "all": "the whole look: captions, type, colour, motion, transitions, pacing, sound feel",
    "rhythm": "pacing, cut rhythm and transitions only; the look (captions, colour, devices) stays the base style's",
    "captions": "the caption/type system only (fonts category, size, position, entry/exit, emphasis); the rest stays the base style's",
    "inspire": "inspiration only: keep the base style, borrow at most two ideas from the references, measure nothing to copy",
}
DEFAULT_REF_USE = "all"
REF_LIKE_MAX = 1500              # "Referensda nima yoqdi?" free text (the user's own words), characters
# Idea pass (Standart and Boy): the web is the last source of ideas, capped per job. The server counts the
# agent's calls in agent.log afterwards and shows a QA failure when a cap was broken.
WEB_SEARCH_MAX = 3
WEB_FETCH_MAX = 5
IDEA_TIME_TOLERANCE_S = 1.5     # an accepted idea must show up in the timeline within this many seconds
REF_DOC_EXT = {".md", ".txt"}
DEFAULT_CREDIT_CAP = 60
MAX_CREDIT_CAP = 2000

# Edit levels the client picks instead of a credit number: (min, max) Higgsfield credits.
# min = what the level usually needs, max = the agent's hard cap for the level.
LEVELS = {
    "min":  {"title": "Minimal",  "credits": (0, 0)},
    "std":  {"title": "Standart", "credits": (10, 20)},
    "rich": {"title": "Boy",      "credits": (40, 60)},
}
DEFAULT_LEVEL = "std"
# Higgsfield auto-refill rate on 2026-11-10: 18 credits per US dollar. Higgsfield cost only
# (no Claude tokens, no margin); shown to the client as an approximate $ next to credits.
CREDITS_PER_USD = 18
MAX_USD_CAP = 500

# Output formats the client picks from (one per job).
FORMATS = {
    "9:16": {"w": 1080, "h": 1920, "title": "Vertikal 9:16", "use": "Reels, TikTok, Shorts", "zones": True},
    "4:5":  {"w": 1080, "h": 1350, "title": "Lenta 4:5", "use": "Instagram va Facebook lentasi", "zones": False},
    "1:1":  {"w": 1080, "h": 1080, "title": "Kvadrat 1:1", "use": "Instagram post, LinkedIn", "zones": False},
    "16:9": {"w": 1920, "h": 1080, "title": "Gorizontal 16:9", "use": "YouTube, sayt, taqdimot", "zones": False},
}
DEFAULT_FORMAT = "9:16"
MIN_SHORT_SIDE = 720            # input video: the shorter side must be at least 720 px (720p is accepted)

# Rough edit-time estimate (minutes) from the first real runs: ~34 min for a 31 s video at level Boy.
EST_BASE_MIN = 10
EST_PER_SEC = 0.6
EST_LEVEL_ADD = {"min": -4, "std": 0, "rich": 6}
EST_REVISION_MIN = 12

# Warn when the last known Higgsfield balance is below this (credits): one Boy edit.
LOW_BALANCE_KR = 60
# Retention: N days after a job's last run its media (raw, refs, renders, versions, AI assets, work files) are
# deleted; the record (job.json, README, timeline, costs) stays. 0 = keep forever. Checked every hour.
# On by default only in Docker (Dockerfile sets 14): this PC keeps its older jobs untouched.
RETENTION_DAYS = int(os.environ.get("DASH_RETENTION_DAYS", "0"))
RETENTION_CHECK_S = 3600
# Static QA run by the server after every job (engine/qa_check.py).
QA_SCRIPT = ROOT / "engine" / "qa_check.py"
QA_TIMEOUT_S = 600
