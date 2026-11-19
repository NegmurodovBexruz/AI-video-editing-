"""Checks for the After Effects MCP server and its wiring into the runner. No After Effects is started:
AE calls are refused (missing AE) or patched; the live AE smoke test is manual (see ae_mcp/README.md)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "ae_mcp"))
import config
import runner
import server as ae
import store


class ServerGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "jobs"
        self.job = self.root / "j1"
        self.job.mkdir(parents=True)
        self.env = patch.dict(os.environ, {"AE_MCP_ROOTS": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_job_dir_must_be_under_roots(self):
        self.assertEqual(ae.job_path(str(self.job)), self.job.resolve())
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        for bad in (str(other), str(self.root / "missing"), ""):
            with self.assertRaises(ae.ToolError):
                ae.job_path(bad)

    def test_paths_stay_inside_job(self):
        j = self.job.resolve()
        self.assertEqual(ae.inside(j, "ae/project.aep"), j / "ae" / "project.aep")
        for bad in ("../x.aep", "..\\..\\x.aep", "C:/Windows/x.aep", ""):
            with self.assertRaises(ae.ToolError):
                ae.inside(j, bad)

    def test_ascii_escaping(self):
        self.assertEqual(ae.to_ascii("o\u02bbzbek — 😀"), "o\\u02bbzbek \\u2014 \\ud83d\\ude00")
        src, first, last = ae.build_script({"x": "\u02bb"}, "var a = 1;\nreturn a;")
        src.encode("ascii")
        lines = src.splitlines()
        self.assertEqual(lines[first - 1], "var a = 1;")
        self.assertEqual(lines[last - 1], "return a;")
        self.assertNotIn("app.newProject();", src, "newProject crashes AE in -noui")

    def test_refuses_without_after_effects(self):
        with patch.object(ae, "AFX", Path(self.tmp.name) / "nope" / "AfterFX.com"):
            data, err = self._call("ae_run", {"job_dir": str(self.job), "script": "return 1;"})
        self.assertTrue(err)
        self.assertIn("topilmadi", data["message"])

    def test_refuses_when_user_ae_is_open_or_ram_low(self):
        fake = Path(self.tmp.name) / "AfterFX.com"
        fake.write_text("")
        with patch.object(ae, "AFX", fake), patch.object(ae, "ae_processes", return_value=['"AfterFX.exe","1"']):
            data, err = self._call("ae_run", {"job_dir": str(self.job), "script": "return 1;"})
        self.assertIn("ochiq", data["message"])
        with patch.object(ae, "AFX", fake), patch.object(ae, "ae_processes", return_value=[]), \
                patch.object(ae, "free_ram_gb", return_value=1.0):
            data, err = self._call("ae_run", {"job_dir": str(self.job), "script": "return 1;"})
        self.assertIn("RAM kam", data["message"])
        self.assertFalse(ae.LOCK.exists(), "the lock is released after a refusal")

    def _call(self, name, args):
        out = []
        with patch.object(ae, "reply", side_effect=lambda mid, result=None, error=None: out.append(result or error)):
            ae.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": name, "arguments": args}})
        r = out[0]
        return json.loads(r["content"][0]["text"]), r["isError"]

    def test_stdio_protocol(self):
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "nope"},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "ae_run", "arguments": {}}}]
        r = subprocess.run([sys.executable, "-I", str(ROOT / "ae_mcp" / "server.py")], capture_output=True, text=True,
                           input="\n".join(json.dumps(m) for m in msgs) + "\n", encoding="utf-8", timeout=60,
                           env=dict(os.environ, AE_MCP_ROOTS=str(self.root)))
        out = [json.loads(x) for x in r.stdout.splitlines()]
        self.assertEqual([o["id"] for o in out], [1, 2, 3, 4], "no reply to the notification")
        self.assertEqual(out[0]["result"]["serverInfo"]["name"], "ae")
        self.assertEqual(out[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual({t["name"] for t in out[1]["result"]["tools"]}, {"ae_run", "ae_frames", "ae_render"})
        self.assertEqual(out[2]["error"]["code"], -32601)
        self.assertTrue(out[3]["result"]["isError"])
        self.assertIn("job_dir", json.loads(out[3]["result"]["content"][0]["text"])["message"])


class RunnerWiring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        sk = root / "skills" / "base_style"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text("---\nname: base_style\n---\n")
        self.o = patch.multiple(config, DATA=root, JOBS=root / "jobs_dryrun", SKILLS=root / "skills",
                                NEW_SKILLS=root / "jobs_dryrun" / "_dry_skills", STYLE_NOTES=root / "n.json",
                                NEW_STYLE_NOTES=root / "jobs_dryrun" / "_n.json",
                                DELETED_STYLES=root / "jobs_dryrun" / "_del.json", DRY_RUN=True, AUTH=False)
        self.o.start()
        self.addCleanup(self.o.stop)

    def job(self, **kw):
        j = store.create("base_style", "t", "", level="rich", fmt="9:16")
        return store.update(j["id"], raw=["r.mp4"], raw_info=[{"name": "r.mp4", "duration": 30, "w": 1080, "h": 1920,
                                                                 "fps": 30, "audio": True}], **kw)

    def cmd(self, job, enabled):
        with patch.object(config, "AE_ENABLED", enabled), patch.object(runner.config, "DRY_RUN", False), \
                patch.object(runner, "claude_exe", return_value="claude"), \
                patch.object(runner.connections, "claude_auth", return_value={"mode": "auto", "configured": True}):
            d = store.job_dir(job["id"])
            return runner.build_cmd(store.load(job["id"]), d, d / "AGENT_TASK.md"), d

    def test_ae_tools_and_mcp_config_when_enabled(self):
        c, d = self.cmd(self.job(), True)
        allowed = c[c.index("--allowedTools") + 1].split(",")
        self.assertTrue(set(runner.AE_TOOLS) <= set(allowed))
        cfg = json.loads(Path(c[c.index("--mcp-config") + 1]).read_text(encoding="utf-8"))["mcpServers"]["ae"]
        self.assertEqual(cfg["args"][-1], str(config.AE_MCP))
        self.assertEqual(cfg["env"]["AE_MCP_ROOTS"], str(config.JOBS))

    def test_no_ae_when_disabled_or_style_job(self):
        c, _ = self.cmd(self.job(), False)
        self.assertNotIn("--mcp-config", c)
        self.assertFalse(set(runner.AE_TOOLS) & set(c[c.index("--allowedTools") + 1].split(",")))
        sj = store.create_style_job("s", "x")
        c, _ = self.cmd(sj, True)
        self.assertNotIn("--mcp-config", c)

    def test_task_text_both_ways(self):
        for enabled, want in ((True, "mcp__ae__ae_render"), (False, "not available on this machine")):
            with patch.object(config, "AE_ENABLED", enabled):
                j = self.job()
                t = runner.render_task(j, store.job_dir(j["id"])).read_text(encoding="utf-8")
            self.assertNotIn("{{", t)
            self.assertIn("## After Effects", t)
            self.assertIn(want, t)
            if enabled:
                self.assertIn("1080×1920", t.split("## After Effects")[1])

    def test_revision_task_line(self):
        j = self.job(state="done")
        j = store.send_feedback(j["id"], "titr kattaroq", 20)
        for enabled, want in ((True, "ae_frames"), (False, "not available")):
            with patch.object(config, "AE_ENABLED", enabled):
                t = runner.render_task(j, store.job_dir(j["id"])).read_text(encoding="utf-8")
            self.assertNotIn("{{", t)
            self.assertIn(want, t)


if __name__ == "__main__":
    unittest.main()
