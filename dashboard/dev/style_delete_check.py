"""Isolated style deletion checks; never writes to the project's styles or jobs."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
import config
import runner
import server
import store


class StyleDeleteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.jobs = self.root / "jobs_dryrun"
        self.skills = self.root / "styles" / "skills"
        self.notes = self.root / "notes.json"
        self.notes.write_text(json.dumps({"base_style": {"title": "Base"}}))
        self.overrides = patch.multiple(config, DATA=self.root, JOBS=self.jobs,
            SKILLS=self.skills, NEW_SKILLS=self.jobs / "_dry_skills",
            STYLE_NOTES=self.notes, NEW_STYLE_NOTES=self.jobs / "_dry_style_notes.json",
            DELETED_STYLES=self.jobs / "_deleted_styles.json", DRY_RUN=True, AUTH=False)
        self.overrides.start()
        self.addCleanup(self.overrides.stop)
        for name, root in [("base_style", self.skills), ("custom_style", config.NEW_SKILLS)]:
            d = root / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text("---\nname: %s\ndescription: Test\n---\n" % name)
            (d / "renderer.py").write_text("# retained for historical edits\n")

    def test_catalogue_removal_retains_assets_and_notes(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        for name in ("base_style", "custom_style"):
            self.assertEqual(store.delete_style(name), {"deleted": name})
            self.assertNotIn(name, store.style_names())
            self.assertIn(name, store.reserved_style_names())
        for p, content in before.items():
            self.assertEqual(p.read_bytes(), content)
        self.assertEqual(store.style_names(), set())

    def test_idempotent_and_names_cannot_be_reused(self):
        store.delete_style("custom_style")
        before = config.DELETED_STYLES.read_bytes()
        store.delete_style("custom_style")
        self.assertEqual(before, config.DELETED_STYLES.read_bytes())
        self.assertIsNotNone(store.register_style("custom_style", {}))
        with self.assertRaises(ValueError):
            store.create("custom_style", "", "")

    def test_existing_jobs_and_feedback_survive(self):
        ids = []
        for state in ("queued", "running", "done"):
            j = store.create("custom_style", state, "")
            store.update(j["id"], state=state)
            ids.append(j["id"])
        before = {jid: store.load(jid) for jid in ids}
        store.delete_style("custom_style")
        self.assertEqual({jid: store.load(jid) for jid in ids}, before)
        revised = store.send_feedback(ids[-1], "Titrni kattalashtir", 0)
        self.assertEqual(revised["state"], "queued")
        self.assertEqual(revised["style"], "custom_style")
        self.assertTrue((config.NEW_SKILLS / "custom_style" / "renderer.py").is_file())

    def test_draft_with_deleted_style_cannot_submit(self):
        j = store.create("base_style", "draft", "")
        store.update(j["id"], raw=["test.mp4"])
        store.delete_style("base_style")
        with self.assertRaisesRegex(ValueError, "o'chirilgan"):
            store.submit(j["id"])
        self.assertEqual(store.load(j["id"])["state"], "draft")
        self.assertNotIn("base_style", runner.style_line({"style": "auto", "refs": []}))

    def test_rejects_invalid_and_unknown_names(self):
        for name in ("../base_style", "base/style", "", "BASE", "..\\base_style"):
            with self.assertRaises(ValueError):
                store.delete_style(name)
        with self.assertRaises(KeyError):
            store.delete_style("unknown_style")
        self.assertFalse(config.DELETED_STYLES.exists())

    def test_persists_in_fresh_process_and_isolates_dry_run(self):
        store.delete_style("base_style")
        # Simulate entrypoint copying the original built-in back over the same folder.
        (self.skills / "base_style" / "SKILL.md").write_text("---\nname: base_style\n---\n")
        env = dict(os.environ, DASH_DATA=str(self.root), DASH_STYLES=str(self.root / "styles"), DASH_DRY_RUN="1")
        code = "import sys; sys.path.insert(0, sys.argv[1]); import store; assert 'base_style' not in store.style_names()"
        subprocess.run([sys.executable, "-I", "-c", code, str(ROOT / "dashboard")], env=env, check=True)
        self.assertFalse((self.root / "deleted_styles.json").exists())

    def test_api_write_and_auth_guards(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        def request(path, header=True):
            req = urllib.request.Request("http://127.0.0.1:%d%s" % (srv.server_port, path),
                method="POST", headers={"X-Dash": "1"} if header else {})
            try:
                with urllib.request.urlopen(req) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                with e:
                    return e.code, json.loads(e.read())
        try:
            path = "/api/styles/base_style/delete"
            self.assertEqual(request(path, header=False)[0], 403)
            with patch.object(server.Handler, "_user", return_value=None):
                self.assertEqual(request(path)[0], 401)
            self.assertIn("base_style", store.style_names())
            self.assertEqual(request(path), (200, {"deleted": "base_style"}))
            self.assertEqual(request(path)[0], 200)
            self.assertEqual(request("/api/styles/unknown_style/delete")[0], 404)
            self.assertNotIn("base_style", store.style_names())
        finally:
            srv.shutdown()
            srv.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
