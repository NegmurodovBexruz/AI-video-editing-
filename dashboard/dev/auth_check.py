"""Login check. Start a dry-run server with the login on first:
    DASH_DRY_RUN=1 DASH_PORT=8051 DASH_AUTH=1 DASH_ADMIN_USER=tester DASH_ADMIN_PASSWORD=start-pass-1 python -I server.py --no-browser
usage: python -I dev/auth_check.py http://127.0.0.1:8051 tester start-pass-1
(Changes the password and back again; leaves the user as it found it.)
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE, USER, PW = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
OK = 0


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(NoRedirect)


def req(method, path, body=None, cookie=None, dash=True):
    h = {}
    if dash:
        h["X-Dash"] = "1"
    if cookie:
        h["Cookie"] = cookie
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        resp = opener.open(r, timeout=30)
    except urllib.error.HTTPError as e:
        resp = e
    raw = resp.read()
    try:
        j = json.loads(raw)
    except ValueError:
        j = None
    return resp.status if hasattr(resp, "status") else resp.code, resp.headers, j


def check(cond, what):
    global OK
    if not cond:
        raise AssertionError(what)
    OK += 1
    print("ok  ", what)


def cookie_of(headers):
    sc = headers.get("Set-Cookie") or ""
    return sc.split(";")[0], sc


code, h, _ = req("GET", "/")
check(code == 302 and h.get("Location") == "/login", "/ without login -> 302 /login")
code, _, j = req("GET", "/api/jobs")
check(code == 401 and j.get("login"), "API without login -> 401")
code, _, _ = req("GET", "/login")
check(code == 200, "login page is public")
code, _, _ = req("GET", "/static/app.css")
check(code == 200, "static files are public")
code, _, j = req("GET", "/api/me")
check(code == 200 and j["auth"] is True and j["user"] is None, "/api/me says: login on, nobody logged in")

code, _, j = req("POST", "/api/login", {"user": USER, "password": "wrong-password"})
check(code == 403, "wrong password refused")
code, _, _ = req("POST", "/api/login", {"user": USER, "password": PW}, dash=False)
check(code == 403, "login without X-Dash header refused")
code, h, j = req("POST", "/api/login", {"user": USER, "password": PW})
ck, raw = cookie_of(h)
check(code == 200 and ck.startswith("dash_session=") and "HttpOnly" in raw and "SameSite=Lax" in raw, "login ok, HttpOnly SameSite cookie set")
code, _, j = req("GET", "/api/jobs", cookie=ck)
check(code == 200 and isinstance(j, list), "API works with the cookie")
code, _, j = req("GET", "/api/me", cookie=ck)
check(j["user"] == USER, "/api/me returns the user")
code, _, _ = req("GET", "/", cookie=ck)
check(code == 200, "dashboard page opens when logged in")

code, h2, _ = req("POST", "/api/login", {"user": USER, "password": PW})
ck2, _ = cookie_of(h2)
code, _, j = req("POST", "/api/password", {"old": "nope-nope", "new": "new-pass-123"}, cookie=ck)
check(code == 403, "password change with a wrong old password refused")
code, _, j = req("POST", "/api/password", {"old": PW, "new": "short"}, cookie=ck)
check(code == 400, "too short new password refused")
code, _, j = req("POST", "/api/password", {"old": PW, "new": "new-pass-123"}, cookie=ck)
check(code == 200, "password changed")
check(req("GET", "/api/jobs", cookie=ck)[0] == 200, "own session survives the change")
check(req("GET", "/api/jobs", cookie=ck2)[0] == 401, "other sessions of the user are logged out")
check(req("POST", "/api/login", {"user": USER, "password": PW})[0] == 403, "old password no longer works")
code, h3, _ = req("POST", "/api/login", {"user": USER, "password": "new-pass-123"})
check(code == 200, "new password works")
req("POST", "/api/password", {"old": "new-pass-123", "new": PW}, cookie=ck)

code, h, _ = req("POST", "/api/logout", cookie=ck)
check(code == 200 and "Max-Age=0" in (h.get("Set-Cookie") or ""), "logout clears the cookie")
check(req("GET", "/api/jobs", cookie=ck)[0] == 401, "session dead after logout")

ck4, _ = cookie_of(req("POST", "/api/login", {"user": USER, "password": PW})[1])
jobs_dir = Path(req("GET", "/api/health", cookie=ck4)[2]["jobs_dir"])
utext = (jobs_dir / "_auth" / "users.json").read_text(encoding="utf-8")
check(PW not in utext and '"hash"' in utext and ck4.split("=", 1)[1] not in (jobs_dir / "_auth" / "sessions.json").read_text(),
      "users.json holds only a hash; sessions.json holds no raw token")
for i in range(5):
    req("POST", "/api/login", {"user": USER, "password": "bad-%d" % i})
code, _, j = req("POST", "/api/login", {"user": USER, "password": PW})
check(code == 403 and "urinish" in (j or {}).get("error", ""), "5 wrong tries block the IP for a minute")
print("\nALL %d LOGIN CHECKS PASSED" % OK)
