"""Idempotent container setup. Registers MCP without a model call or OAuth login."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))
from connections import HIGGSFIELD_URL, claude_auth, higgsfield_mcp


def ensure_higgsfield(home=None, run=None):
    status = higgsfield_mcp(home)
    if status.get("error"):
        raise RuntimeError("Claude MCP sozlamalarini o'qib bo'lmadi; mavjud fayl o'zgartirilmadi.")
    if status["configured"]:
        return False
    if status["registered"]:
        raise RuntimeError("higgsfield nomi boshqa MCP sozlamasi bilan band; mavjud sozlama o'zgartirilmadi.")
    run = subprocess.run if run is None else run
    result = run(["claude", "mcp", "add", "--transport", "http", "--scope", "user", "higgsfield", HIGGSFIELD_URL],
                 capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError("Higgsfield MCP qo'shilmadi; claude mcp add buyrug'ini tekshiring.")
    return True


def main():
    if os.environ.get("DASH_DRY_RUN") == "1":
        print("DRY RUN: tashqi xizmatlar sozlanmaydi.")
        return
    auth = claude_auth()
    if auth["mode"] not in ("auto", "api"):
        raise RuntimeError("DASH_CLAUDE_AUTH faqat api yoki auto bo'lishi mumkin.")
    if auth["configured"]:
        print("Claude API sozlangan." if auth["mode"] == "api" else "Claude kirish sozlamasi mavjud.")
    else:
        print("OGOHLANTIRISH: Claude API kaliti yo'q. .env dagi ANTHROPIC_API_KEY ni kiriting va konteynerni qayta yarating.")
    added = ensure_higgsfield()
    print("Higgsfield MCP qo'shildi." if added else "Higgsfield MCP avvaldan sozlangan.")
    print("Higgsfield OAuth tekshiruvi: python -I /app/deploy/check_connections.py")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
