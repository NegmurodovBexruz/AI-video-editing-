"""Check API configuration and MCP connectivity without LLM calls or generation."""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))
from connections import claude_auth, higgsfield_mcp


def main():
    auth = claude_auth()
    print("Claude API: " + ("kalit sozlangan (haqiqiy API so'rovi yuborilmadi)" if auth["configured"]
                            and auth["method"] in ("api_key", "gateway") else "API kaliti kiritilmagan"))
    status = higgsfield_mcp()
    connected = False
    if not status["configured"]:
        print("Higgsfield MCP: sozlanmagan yoki sozlama o'qilmadi")
    else:
        try:
            result = subprocess.run(["claude", "mcp", "get", "higgsfield"], capture_output=True,
                                    text=True, timeout=30)
            output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
            connected = result.returncode == 0 and bool(re.search(r"Status:\s*(?:[✓✔]\s*)?Connected\b", output, re.I))
            print("Higgsfield MCP: " + ("ulangan" if connected else "ulanmagan; OAuth kirishi yoki tarmoqni tekshiring"))
        except (OSError, subprocess.TimeoutExpired):
            print("Higgsfield MCP: tekshiruv tugamadi; tarmoq va Claude CLI'ni tekshiring")
    return 0 if auth["configured"] and auth["method"] in ("api_key", "gateway") and connected else 1


if __name__ == "__main__":
    sys.exit(main())
