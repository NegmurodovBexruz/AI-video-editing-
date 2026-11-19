"""Login for the dashboard (on when config.AUTH): users with PBKDF2 password hashes, cookie sessions.

Files (in config.AUTH_DIR, never in git):
    users.json      {"<login>": {"role": "superuser", "algo": "pbkdf2_sha256", "iter": N, "salt": hex, "hash": hex, ...}}
    sessions.json   {"<sha256 of the cookie token>": {"user": "<login>", "exp": epoch}}
The cookie holds a random token; only its hash is stored, so a leaked sessions.json cannot be replayed.
The first start creates the admin from DASH_ADMIN_USER / DASH_ADMIN_PASSWORD; later the password is changed
from the dashboard ("Parolni o'zgartirish") and the env value is ignored.
"""
import datetime
import hashlib
import hmac
import json
import os
import secrets
import threading
import time

import config

COOKIE = "dash_session"
ITER = 310_000
_lock = threading.RLock()
_fails = {}            # ip -> (count, blocked_until)
MAX_FAILS, BLOCK_S = 5, 60


def _f(name):
    return config.AUTH_DIR / name


def _read(name, default):
    p = _f(name)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return default


def _write(name, obj):
    config.AUTH_DIR.mkdir(parents=True, exist_ok=True)
    p = _f(name)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    if os.name != "nt":
        os.chmod(tmp, 0o600)
    os.replace(tmp, p)


def _hash(pw, salt_hex, iters=ITER):
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt_hex), iters).hex()


def _record(pw):
    salt = secrets.token_hex(16)
    return {"algo": "pbkdf2_sha256", "iter": ITER, "salt": salt, "hash": _hash(pw, salt)}


def _tok(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def bootstrap():
    """Create the first user from the environment. Returns a short status line for the server log."""
    if not config.AUTH:
        return "login o'chiq (DASH_AUTH=1 emas)"
    with _lock:
        users = _read("users.json", {})
        if users:
            return "login yoqiq: %d ta foydalanuvchi" % len(users)
        if not config.ADMIN_USER or len(config.ADMIN_PASSWORD) < config.MIN_PASSWORD:
            raise SystemExit("DASH_AUTH=1, lekin foydalanuvchi yo'q: DASH_ADMIN_USER va DASH_ADMIN_PASSWORD (kamida %d belgi) bering"
                             % config.MIN_PASSWORD)
        users[config.ADMIN_USER] = dict(_record(config.ADMIN_PASSWORD), role="superuser",
                                        created=datetime.datetime.now().isoformat(timespec="seconds"))
        _write("users.json", users)
        return "login yoqiq: '%s' (superuser) yaratildi" % config.ADMIN_USER


def login(user, pw, ip):
    user, pw = (user or "").strip(), pw or ""
    now = time.time()
    with _lock:
        cnt, until = _fails.get(ip, (0, 0))
        if until > now:
            raise PermissionError("Juda ko'p noto'g'ri urinish. %d soniyadan keyin qayta urining." % int(until - now + 1))
        rec = _read("users.json", {}).get(user)
    # always hash, so a missing user takes as long as a wrong password
    ok = hmac.compare_digest(_hash(pw, rec["salt"], rec["iter"]) if rec else _hash(pw, "00" * 16), rec["hash"] if rec else "x")
    with _lock:
        if not ok:
            cnt += 1
            _fails[ip] = (0, now + BLOCK_S) if cnt >= MAX_FAILS else (cnt, 0)
            time.sleep(0.4)
            raise PermissionError("Login yoki parol noto'g'ri")
        _fails.pop(ip, None)
        token = secrets.token_urlsafe(32)
        sessions = {k: v for k, v in _read("sessions.json", {}).items() if v.get("exp", 0) > now}
        sessions[_tok(token)] = {"user": user, "exp": now + config.SESSION_DAYS * 86400}
        _write("sessions.json", sessions)
        return token


def user_for(token):
    if not token:
        return None
    with _lock:
        s = _read("sessions.json", {}).get(_tok(token))
        if not s or s.get("exp", 0) < time.time():
            return None
        return s["user"] if s["user"] in _read("users.json", {}) else None


def logout(token):
    if not token:
        return
    with _lock:
        sessions = _read("sessions.json", {})
        if sessions.pop(_tok(token), None) is not None:
            _write("sessions.json", sessions)


def change_password(user, old, new, keep_token):
    new = new or ""
    if len(new) < config.MIN_PASSWORD:
        raise ValueError("Yangi parol kamida %d belgidan iborat bo'lsin" % config.MIN_PASSWORD)
    with _lock:
        users = _read("users.json", {})
        rec = users.get(user)
        if not rec or not hmac.compare_digest(_hash(old or "", rec["salt"], rec["iter"]), rec["hash"]):
            raise PermissionError("Joriy parol noto'g'ri")
        rec.update(_record(new), changed=datetime.datetime.now().isoformat(timespec="seconds"))
        _write("users.json", users)
        # log out every other session of this user (e.g. a forgotten browser)
        keep = _tok(keep_token) if keep_token else None
        sessions = {k: v for k, v in _read("sessions.json", {}).items() if v.get("user") != user or k == keep}
        _write("sessions.json", sessions)


def cookie_header(token, clear=False):
    parts = ["%s=%s" % (COOKIE, "" if clear else token), "Path=/", "HttpOnly", "SameSite=Lax",
             "Max-Age=%d" % (0 if clear else config.SESSION_DAYS * 86400)]
    if config.COOKIE_SECURE:
        parts.append("Secure")
    return "; ".join(parts)
