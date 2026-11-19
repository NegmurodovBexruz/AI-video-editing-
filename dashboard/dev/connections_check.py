"""Offline checks: API auth selection, idempotent MCP setup, and no secret disclosure."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "deploy"))
import connections
import runner
import setup_connections
import check_connections


class ConnectionsCheck(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def auth(self, **env):
        return connections.claude_auth(env, self.home)

    def test_api_key(self):
        status = self.auth(DASH_CLAUDE_AUTH="api", ANTHROPIC_API_KEY="test-secret")
        self.assertTrue(status["configured"])
        self.assertEqual(status["method"], "api_key")
        self.assertNotIn("test-secret", json.dumps(status))

    def test_gateway_needs_credentials_not_just_url(self):
        for env in [{"ANTHROPIC_BASE_URL": "https://example.invalid"},
                    {"ANTHROPIC_AUTH_TOKEN": "test-secret"}, {"ANTHROPIC_API_KEY": "  "}]:
            self.assertFalse(self.auth(DASH_CLAUDE_AUTH="api", **env)["configured"])
        self.assertEqual(self.auth(DASH_CLAUDE_AUTH="api", ANTHROPIC_BASE_URL="https://example.invalid",
                                   ANTHROPIC_AUTH_TOKEN="test-secret")["method"], "gateway")

    def test_api_mode_ignores_subscription_login(self):
        (self.home / ".claude").mkdir()
        (self.home / ".claude" / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {"accessToken": "test-secret"}}))
        self.assertFalse(self.auth(DASH_CLAUDE_AUTH="api", CLAUDE_CODE_OAUTH_TOKEN="test-secret")["configured"])
        self.assertEqual(self.auth()["method"], "oauth")

    def test_auto_mode_keeps_local_oauth_support(self):
        self.assertEqual(self.auth(CLAUDE_CODE_OAUTH_TOKEN="test-secret")["method"], "oauth")
        self.assertFalse(self.auth(DASH_CLAUDE_AUTH="wrong")["configured"])

    def test_mcp_credentials_alone_are_not_claude_login(self):
        (self.home / ".claude").mkdir()
        path = self.home / ".claude" / ".credentials.json"
        for content in ('{}', '{"mcpOAuth": {"higgsfield": {"accessToken": "mcp-only"}}}',
                        'broken-json', '{"claudeAiOauth": null}'):
            path.write_text(content)
            self.assertFalse(self.auth()["configured"])

    def test_missing_key_blocks_real_agent_before_launch(self):
        with patch.dict(os.environ, {"DASH_CLAUDE_AUTH": "api"}, clear=True), \
                patch.object(runner.config, "DRY_RUN", False), patch.object(runner, "claude_exe", return_value="claude"):
            with self.assertRaisesRegex(RuntimeError, "API kaliti"):
                runner.build_cmd({}, self.home, self.home / "task.md")

    def test_fake_agent_needs_no_credentials(self):
        with patch.dict(os.environ, {"DASH_CLAUDE_AUTH": "api"}, clear=True), patch.object(runner.config, "DRY_RUN", True):
            self.assertIn("fake_agent.py", " ".join(runner.build_cmd({}, self.home, self.home / "task.md")))

    def test_mcp_setup_registers_only_expected_endpoint(self):
        run = Mock(return_value=subprocess.CompletedProcess([], 0))
        self.assertTrue(setup_connections.ensure_higgsfield(self.home, run))
        args = run.call_args.args[0]
        self.assertEqual(args, ["claude", "mcp", "add", "--transport", "http", "--scope", "user",
                                "higgsfield", connections.HIGGSFIELD_URL])

    def test_mcp_registration_is_idempotent_and_preserves_auth(self):
        path = self.home / ".claude.json"
        content = json.dumps({"mcpServers": {"higgsfield": {"type": "http", "url": connections.HIGGSFIELD_URL}},
                              "otherSetting": "keep-me"})
        path.write_text(content)
        run = Mock()
        self.assertFalse(setup_connections.ensure_higgsfield(self.home, run))
        run.assert_not_called()
        self.assertEqual(path.read_text(), content)
        self.assertIsNone(connections.higgsfield_mcp(self.home)["connected"])

    def test_wrong_endpoint_and_broken_json_are_not_overwritten(self):
        path = self.home / ".claude.json"
        for content in ["broken-json", json.dumps({"mcpServers": {"higgsfield": {"type": "http", "url": "https://example.invalid"}}})]:
            path.write_text(content)
            run = Mock()
            with self.assertRaises(RuntimeError):
                setup_connections.ensure_higgsfield(self.home, run)
            run.assert_not_called()
            self.assertEqual(path.read_text(), content)

    def test_failed_registration_is_not_reported_as_ready(self):
        run = Mock(return_value=subprocess.CompletedProcess([], 1))
        with self.assertRaises(RuntimeError):
            setup_connections.ensure_higgsfield(self.home, run)

    def test_diagnostics_probe_mcp_only_and_hide_cli_secrets(self):
        auth = {"configured": True, "method": "api_key"}
        for stdout, expected in [("Status: ✓ Connected", 0), ("Status: Needs authentication", 1), ("Status: Not connected", 1)]:
            result = subprocess.CompletedProcess([], 0, stdout + "\nsecret-header-value", "")
            with patch.object(check_connections, "claude_auth", return_value=auth), \
                    patch.object(check_connections, "higgsfield_mcp", return_value={"configured": True}), \
                    patch.object(check_connections.subprocess, "run", return_value=result) as run, \
                    patch("builtins.print") as output:
                self.assertEqual(check_connections.main(), expected)
                self.assertEqual(run.call_args.args[0], ["claude", "mcp", "get", "higgsfield"])
                self.assertNotIn("secret-header-value", str(output.call_args_list))


if __name__ == "__main__":
    unittest.main(verbosity=2)
