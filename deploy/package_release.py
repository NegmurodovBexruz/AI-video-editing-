"""Build a source ZIP from the working tree, excluding secrets and local job data.

Run from any directory: python -I deploy/package_release.py
The ZIP is written to release/, with per-file SHA-256 hashes inside its manifest.
"""
import datetime
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = (".dockerignore", ".gitignore", ".gitattributes", ".env.example",
              "Dockerfile", "docker-compose.yml", "README.md", "HANDOFF.md", "DEPLOY.md", "LICENSE",
              "deploy/Caddyfile")
SOURCE_DIRS = ("dashboard", "engine", "styles", "scripts", "deploy", "ae_mcp", "third_party")
SUFFIXES = {".py", ".md", ".json", ".cmd", ".ps1", ".html", ".css", ".js", ".jsx",
            ".ttf", ".woff2", ".sh", ".txt", ".yml"}
EXCLUDED = {"__pycache__", "node_modules", ".venv", ".git", ".claude", "design",
            "_codex_version_20261106"}
MODEL = "models/rvm_mobilenetv3_fp32.onnx"


def payload():
    paths = {ROOT / name for name in ROOT_FILES}
    for name in SOURCE_DIRS:
        for p in (ROOT / name).rglob("*"):
            rel = p.relative_to(ROOT)
            if not p.is_file() or EXCLUDED.intersection(rel.parts):
                continue
            if p.suffix.lower() in SUFFIXES and p.name != ".claude.json" and not p.name.startswith(".env"):
                paths.add(p)
    paths.update((ROOT / "assets").glob("*.ttf"))
    paths.add(ROOT / MODEL)
    paths.add(ROOT / "refs/ref_ba_20261109/analysis.md")
    result = {}
    for p in sorted(paths):
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            raise RuntimeError("Unsafe release path: " + str(p))
        raw = p.read_bytes()  # Missing required files fail the build.
        if p.suffix == ".sh":
            raw = raw.replace(b"\r\n", b"\n")
        result[p.relative_to(ROOT).as_posix()] = raw
    return result


def check_secrets(files):
    known = []
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8-sig").splitlines():
            key, sep, value = line.partition("=")
            if sep and not key.lstrip().startswith("#") and re.search(r"KEY|TOKEN|PASSWORD|SECRET", key):
                value = value.split(" #", 1)[0].strip().strip("\"'")
                if len(value) >= 8:
                    known.append(value.encode())
    patterns = (rb"sk-ant-[A-Za-z0-9_-]{20,}", rb"sk_[A-Za-z0-9]{25,}",
                rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    for name, raw in files.items():
        if Path(name).suffix in {".onnx", ".ttf", ".woff2"}:
            continue
        if any(secret in raw for secret in known) or any(re.search(p, raw) for p in patterns):
            # Print only the filename, never the matching secret.
            raise RuntimeError("Possible credential in release file: " + name)


def git_info():
    def run(*args):
        try:
            return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    status = run("status", "--porcelain")
    return {"base_commit": run("rev-parse", "HEAD"),
            "has_uncommitted_changes": bool(status) if status is not None else None,
            "source": "current working tree; not git archive HEAD"}


def main():
    files = payload()
    check_secrets(files)
    stamp = datetime.datetime.now(datetime.timezone.utc)
    manifest = {"issue": "AP-1077", "created_utc": stamp.isoformat(), "git": git_info(),
        "excluded": [".env and credentials", "OAuth and sessions", "git history", "local jobs/media",
                     "Docker volumes/images", "cache, venv, node_modules", "Whisper model cache"],
        "files": [{"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                  for name, raw in files.items()]}
    files["PACKAGE_MANIFEST.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    folder = ROOT / "release"
    folder.mkdir(exist_ok=True)
    out = folder / ("AP-1077-montaj-server-" + stamp.strftime("%Y%m%d") + ".zip")
    if out.exists():
        raise RuntimeError("Release already exists; preserve it or choose a new output date: " + str(out))
    with zipfile.ZipFile(out, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, raw in files.items():
            entry = zipfile.ZipInfo("montaj/" + name, stamp.timetuple()[:6])
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | (0o755 if name.endswith(".sh") else 0o644)) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(entry, raw)
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:
            raise RuntimeError("ZIP integrity check failed")
    print(json.dumps({"zip": str(out), "files": len(files), "bytes": out.stat().st_size,
                      "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
