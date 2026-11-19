"""Local connection configuration checks; never call a model or expose credentials."""
import json
import os
from pathlib import Path

HIGGSFIELD_URL = "https://mcp.higgsfield.ai/mcp"


def claude_auth(env=None, home=None):
    env = os.environ if env is None else env
    mode = env.get("DASH_CLAUDE_AUTH", "auto").strip().lower()
    method = None
    if mode not in ("auto", "api"):
        return {"mode": mode, "configured": False, "method": None}
    if env.get("ANTHROPIC_API_KEY", "").strip():
        method = "api_key"
    elif env.get("ANTHROPIC_BASE_URL", "").strip() and env.get("ANTHROPIC_AUTH_TOKEN", "").strip():
        method = "gateway"
    elif mode == "auto":
        path = (Path.home() if home is None else Path(home)) / ".claude" / ".credentials.json"
        try:
            credentials = json.loads(path.read_text(encoding="utf-8"))
            oauth = credentials.get("claudeAiOauth", {})
            token = oauth.get("accessToken") if isinstance(oauth, dict) else None
        except (OSError, ValueError, AttributeError):
            token = None
        if env.get("CLAUDE_CODE_OAUTH_TOKEN", "").strip() or token:
            method = "oauth"
    return {"mode": mode, "configured": method is not None, "method": method}


def higgsfield_mcp(home=None):
    """Registration only. OAuth/network connectivity requires the separate CLI check."""
    home = Path.home() if home is None else Path(home)
    path = home / ".claude.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        servers = data.get("mcpServers", {})
        entry = servers.get("higgsfield")
    except (OSError, ValueError, AttributeError):
        return {"configured": False, "registered": False, "connected": None, "error": "config_read"}
    configured = isinstance(entry, dict) and entry.get("type") == "http" and entry.get("url") == HIGGSFIELD_URL
    return {"configured": configured, "registered": entry is not None, "connected": None}
