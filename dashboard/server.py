"""Editing dashboard (AP-1077): local web UI + job runner. Standard library only.

    python server.py            -> http://127.0.0.1:8050
    set DASH_DRY_RUN=1          -> fake agent, no credits (for testing the UI)
"""
import json
import mimetypes
import re
import sys
import urllib.parse
import webbrowser
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auth    # noqa: E402
import config  # noqa: E402
import runner  # noqa: E402
import store   # noqa: E402

WORKER = runner.Worker()
JOB = r"/api/jobs/([A-Za-z0-9_-]{6,80})"
mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("application/x-subrip", ".srt")


class Handler(BaseHTTPRequestHandler):
    server_version = "MontajDash/0.1"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    # ---- helpers ----
    def _send(self, code, body, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200, extra=None):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", extra)

    def _err(self, code, msg):
        # An unread request body (e.g. a refused upload) would break keep-alive: close instead.
        self.close_connection = True
        body = json.dumps({"error": msg}, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8", {"Connection": "close"})

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0].lower()
        return host in config.ALLOWED_HOSTS

    def _write_ok(self):
        # Custom header forces a CORS preflight, which we never answer: other sites cannot start jobs.
        return self._host_ok() and self.headers.get("X-Dash") == "1"

    # ---- login ----
    def _token(self):
        c = SimpleCookie()
        try:
            c.load(self.headers.get("Cookie") or "")
        except Exception:
            return None
        m = c.get(auth.COOKIE)
        return m.value if m else None

    def _user(self):
        """Logged-in user name; 'local' when the login is off (this PC)."""
        return auth.user_for(self._token()) if config.AUTH else "local"

    def _ip(self):
        fwd = (self.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
        return fwd or self.client_address[0]

    def _need_login(self, api):
        if api:
            return self._json({"error": "Avval tizimga kiring", "login": True}, 401)
        self._send(302, b"", "text/plain", {"Location": "/login"})

    def _read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 2_000_000:
            raise ValueError("So'rov juda katta")
        return json.loads(self.rfile.read(n) or b"{}")

    def _static(self, rel):
        base = config.STATIC.resolve()
        f = (base / rel).resolve()
        if base not in f.parents or not f.is_file():
            return self._err(404, "Topilmadi")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        self._send(200, f.read_bytes(), ctype)

    def _file(self, jid, rel, download):
        f = store.resolve_file(jid, rel)
        size = f.stat().st_size
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or f.suffix.lower() in (".md", ".json", ".srt"):
            ctype = (ctype if ctype.startswith("text/") else "text/plain") + "; charset=utf-8"
        start, end, code = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "") or "")
        if m and size:
            if m[1]:
                start = int(m[1])
                end = min(int(m[2]), size - 1) if m[2] else size - 1
            elif m[2]:
                start = max(0, size - int(m[2]))
            if start > end or start >= size:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % size)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            code = 206
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if code == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        if download:
            self.send_header("Content-Disposition",
                             "attachment; filename*=UTF-8''%s" % urllib.parse.quote(f.name))
        self.end_headers()
        if self.command == "HEAD":
            return
        with open(f, "rb") as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = fh.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def _route(self, fn):
        try:
            fn()
        except KeyError:
            self._err(404, "Topilmadi")
        except PermissionError as e:
            self._err(403, str(e))
        except ValueError as e:
            self._err(400, str(e))
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception as e:  # keep the server alive, report the error
            import traceback
            traceback.print_exc()
            try:
                self._err(500, "Server xatosi: %s" % e)
            except Exception:
                pass

    # ---- verbs ----
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        def go():
            if not self._host_ok():
                return self._err(403, "Faqat localhost")
            u = urllib.parse.urlparse(self.path)
            p, q = u.path, urllib.parse.parse_qs(u.query)
            if p.startswith("/static/"):
                return self._static(urllib.parse.unquote(p[len("/static/"):]))
            user = self._user()
            if p == "/login":
                if user:
                    return self._send(302, b"", "text/plain", {"Location": "/"})
                return self._static("login.html")
            if p == "/api/me":
                return self._json({"auth": config.AUTH, "user": user})
            if not user:
                return self._need_login(p.startswith("/api/"))
            if p in ("/", "/index.html"):
                return self._static("index.html")
            if p == "/api/health":
                return self._json(runner.health(WORKER))
            if p == "/api/styles":
                return self._json(store.styles())
            if p == "/api/levels":
                return self._json(store.levels())
            if p == "/api/companies":
                return self._json(store.companies())
            if p == "/api/jobs":
                return self._json(store.all_jobs())
            m = re.fullmatch(JOB, p)
            if m:
                return self._json(store.detail(m[1]))
            m = re.fullmatch(JOB + "/file", p)
            if m:
                return self._file(m[1], q.get("path", [""])[0], q.get("dl", ["0"])[0] == "1")
            self._err(404, "Topilmadi")
        self._route(go)

    def do_POST(self):
        def go():
            if not self._write_ok():
                return self._err(403, "Ruxsat yo'q")
            p = urllib.parse.urlparse(self.path).path
            if p == "/api/login":
                if not config.AUTH:
                    return self._json({"user": "local"})
                b = self._read_json()
                token = auth.login(b.get("user"), b.get("password"), self._ip())
                return self._json({"user": (b.get("user") or "").strip()}, 200, {"Set-Cookie": auth.cookie_header(token)})
            if p == "/api/logout":
                auth.logout(self._token())
                return self._json({"ok": True}, 200, {"Set-Cookie": auth.cookie_header("", clear=True)})
            user = self._user()
            if not user:
                return self._need_login(True)
            if p == "/api/password":
                if not config.AUTH:
                    raise ValueError("Login o'chiq: parol yo'q")
                b = self._read_json()
                auth.change_password(user, b.get("old"), b.get("new"), self._token())
                return self._json({"ok": True})
            if p == "/api/jobs":
                b = self._read_json()
                return self._json(store.create(b.get("style"), b.get("title"), b.get("ref_text"),
                                               credit_cap=b.get("credit_cap"), level=b.get("level"),
                                               usd_cap=b.get("usd_cap"), company=b.get("company"),
                                               fmt=b.get("format"), ref_use=b.get("ref_use"),
                                               ref_like=b.get("ref_like")), 201)
            m = re.fullmatch(r"/api/styles/([a-z][a-z0-9_]{2,40})/delete", p)
            if m:
                return self._json(store.delete_style(m[1]))
            if p == "/api/companies":
                b = self._read_json()
                return self._json(store.create_company(b.get("name"), b.get("note")), 201)
            m = re.fullmatch(r"/api/companies/([a-z0-9-]{1,40})", p)
            if m:
                b = self._read_json()
                return self._json(store.update_company(m[1], b.get("name"), b.get("note"), b.get("archived")))
            m = re.fullmatch(JOB + "/archive", p)
            if m:
                return self._json(store.set_job_archived(m[1], self._read_json().get("archived", True)))
            m = re.fullmatch(JOB + "/save-style", p)
            if m:
                return self._json(store.save_style_from_job(m[1], self._read_json().get("title")), 201)
            m = re.fullmatch(JOB + "/delete", p)
            if m:
                runner.forget_session(store.delete_job(m[1]))
                print("Ish o'chirildi: %s (%s)" % (m[1], user))
                return self._json({"deleted": m[1]})
            m = re.fullmatch(JOB + "/company", p)
            if m:
                return self._json(store.set_job_company(m[1], self._read_json().get("company")))
            if p == "/api/style-jobs":
                b = self._read_json()
                return self._json(store.create_style_job(b.get("title"), b.get("ref_text"), b.get("company")), 201)
            m = re.fullmatch(JOB + "/submit", p)
            if m:
                return self._json(store.submit(m[1]))
            m = re.fullmatch(JOB + "/cancel", p)
            if m:
                return self._json(WORKER.cancel(m[1]))
            m = re.fullmatch(JOB + "/retry", p)
            if m:
                return self._json(store.retry_job(m[1]), 201)
            m = re.fullmatch(JOB + "/feedback", p)
            if m:
                b = self._read_json()
                cap = b.get("credit_cap")
                if cap is None:   # a revision keeps the selected level or standalone dollar limit
                    job = store.load(m[1])
                    cap = job.get("level_cap", job.get("credit_cap", 20)) if job.get("level") or job.get("usd_cap") is not None else 20
                return self._json(store.send_feedback(m[1], b.get("text"), cap))
            self._err(404, "Topilmadi")
        self._route(go)

    def do_PUT(self):
        def go():
            if not self._write_ok():
                return self._err(403, "Ruxsat yo'q")
            if not self._user():
                return self._need_login(True)
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            m = re.fullmatch(JOB + "/upload", u.path)
            if not m:
                return self._err(404, "Topilmadi")
            n = int(self.headers.get("Content-Length") or 0)
            kind = q.get("kind", [""])[0]
            fname = q.get("name", ["file"])[0]
            if kind == "fb":
                name = store.save_feedback_file(m[1], fname, self.rfile, n)
            else:
                name = store.save_upload(m[1], kind, fname, self.rfile, n, note=q.get("note", [""])[0],
                                         required=q.get("required", ["0"])[0] == "1")
            self._json({"name": name}, 201)
        self._route(go)


def retention_loop():
    """Hourly: purge media of jobs older than RETENTION_DAYS (records stay)."""
    import time
    while True:
        try:
            for jid, freed in store.expire_old():
                print("Saqlash muddati tugadi: %s, %.0f MB bo'shatildi" % (jid, freed / 1e6))
        except Exception:
            import traceback
            traceback.print_exc()
        time.sleep(config.RETENTION_CHECK_S)


def main():
    config.JOBS.mkdir(parents=True, exist_ok=True)
    print(auth.bootstrap())
    WORKER.start()
    if config.RETENTION_DAYS > 0 and not WORKER.status()["worker_disabled"]:
        import threading
        threading.Thread(target=retention_loop, name="retention", daemon=True).start()
        print("Saqlash muddati: %d kun (keyin videolar o'chadi, yozuv qoladi)" % config.RETENTION_DAYS)
    srv = ThreadingHTTPServer((config.HOST, config.PORT), Handler)
    srv.daemon_threads = True
    url = "http://%s:%d/" % (config.HOST, config.PORT)
    print("Montaj dashbordi: %s%s" % (url, "  (DRY RUN: soxta agent)" if config.DRY_RUN else ""))
    print("Ishlar papkasi: %s" % config.JOBS)
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("To'xtatildi. Ishlayotgan agent (bo'lsa) davom etadi; dashbord qayta ochilganda unga ulanadi.")


if __name__ == "__main__":
    main()
