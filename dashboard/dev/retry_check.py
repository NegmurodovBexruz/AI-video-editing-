"""Isolated checks for 'Qayta yurgizish' (retry a failed job); never touches the project's jobs or styles."""
import json
import shutil
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
import server
import store


class RetryTests(unittest.TestCase):
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
        d = self.skills / "base_style"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: base_style\ndescription: Test\n---\n")

    def failed_job(self, style="base_style", **extra):
        j = store.create(style, "Savol 2", "Brief matni", level="rich", fmt="9:16", ref_like="titrlar")
        d = store.job_dir(j["id"])
        (d / "input" / "raw" / "raw.mp4").write_bytes(b"raw-video")
        (d / "input" / "refs" / "ref.mp4").write_bytes(b"ref-video")
        (d / "input" / "materials").mkdir()
        (d / "input" / "materials" / "logo.png").write_bytes(b"logo")
        (d / "out").mkdir()
        (d / "out" / "half.mp4").write_bytes(b"half-made")
        fields = dict(state="failed", error="429", raw=["raw.mp4"], refs=j["refs"] + ["ref.mp4"],
                      raw_info=[{"name": "raw.mp4", "duration": 40}],
                      materials=[{"name": "logo.png", "kind": "image", "required": True}])
        fields.update(extra)
        return store.update(j["id"], **fields)

    def test_retry_copies_settings_and_inputs_into_new_queued_job(self):
        src = self.failed_job()
        new = store.retry_job(src["id"])
        self.assertNotEqual(new["id"], src["id"])
        self.assertEqual(new["state"], "queued")
        self.assertEqual(new["retry_of"], src["id"])
        self.assertNotEqual(new["session_id"], src["session_id"])
        for k in ("title", "style", "format", "level", "credit_cap", "level_cap", "ref_like", "raw", "refs",
                  "raw_info", "materials"):
            self.assertEqual(new[k], src[k], k)
        for k in ("error", "finished", "revision"):
            self.assertNotIn(k, new)
        d = store.job_dir(new["id"])
        for rel in ("input/raw/raw.mp4", "input/refs/ref.mp4", "input/refs/brief.txt", "input/materials/logo.png"):
            self.assertTrue((d / rel).is_file(), rel)
        self.assertFalse((d / "out").exists(), "half-made output must not be copied")
        old = store.load(src["id"])
        self.assertEqual(old["state"], "failed")
        self.assertEqual(old["retried_as"], new["id"])
        self.assertTrue((store.job_dir(src["id"]) / "input" / "raw" / "raw.mp4").is_file())

    def test_second_retry_is_refused(self):
        src = self.failed_job()
        store.retry_job(src["id"])
        with self.assertRaisesRegex(ValueError, "allaqachon"):
            store.retry_job(src["id"])
        self.assertEqual(len(store.list_ids()), 2)

    def test_only_failed_jobs(self):
        for state in ("draft", "queued", "running", "done", "cancelled"):
            j = self.failed_job(state=state)
            with self.assertRaisesRegex(ValueError, "Faqat xato"):
                store.retry_job(j["id"])
        exp = self.failed_job(expired=store.now())
        with self.assertRaisesRegex(ValueError, "muddati"):
            store.retry_job(exp["id"])
        self.assertEqual(len(store.list_ids()), 6)

    def test_failed_revision_is_resent_in_place(self):
        j = self.failed_job(state="done", video="out/half.mp4")
        d = store.job_dir(j["id"])
        pend = d / "feedback" / "pending"
        pend.mkdir(parents=True)
        (pend / "ref.png").write_bytes(b"png")
        store.send_feedback(j["id"], "Non burchakdan chiqsin", 130)
        store.update(j["id"], state="failed", error="agent uzildi")
        out = store.retry_job(j["id"])
        self.assertEqual((out["id"], out["state"], out["revision"]), (j["id"], "queued", 2))
        fb = out["feedback"][-1]
        self.assertEqual((fb["text"], fb["files"], fb["credit_cap"]), ("Non burchakdan chiqsin", ["ref.png"], 130))
        self.assertTrue((d / "feedback" / "r2" / "ref.png").is_file())
        self.assertTrue((d / "feedback" / "r1" / "ref.png").is_file(), "the original notes stay")
        self.assertEqual(len(out["versions"]), 1, "v1 kept, no new version from the failed revision")
        self.assertEqual(len(store.list_ids()), 1, "no new job for a revision")
        with self.assertRaisesRegex(ValueError, "Faqat xato"):
            store.retry_job(j["id"])

    def test_failed_revision_with_unsent_files_is_refused(self):
        j = self.failed_job(state="done")
        store.send_feedback(j["id"], "izoh", 20)
        store.update(j["id"], state="failed")
        pend = store.job_dir(j["id"]) / "feedback" / "pending"
        pend.mkdir(parents=True, exist_ok=True)
        (pend / "new.png").write_bytes(b"x")
        with self.assertRaisesRegex(ValueError, "Yuborilmagan"):
            store.retry_job(j["id"])
        self.assertEqual(store.load(j["id"])["state"], "failed")

    def test_deleted_style_refused_without_leftovers(self):
        src = self.failed_job()
        store.delete_style("base_style")
        with self.assertRaisesRegex(ValueError, "o'chirilgan"):
            store.retry_job(src["id"])
        self.assertEqual(store.list_ids(), [src["id"]])
        self.assertNotIn("retried_as", store.load(src["id"]))

    def test_copy_failure_rolls_back(self):
        src = self.failed_job()
        with patch.object(shutil, "copytree", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                store.retry_job(src["id"])
        self.assertEqual(store.list_ids(), [src["id"]])
        self.assertFalse(store.load(src["id"]).get("retried_as"))
        self.assertEqual(store.retry_job(src["id"])["state"], "queued")

    def test_auto_style_and_style_job(self):
        auto = self.failed_job(style="auto")
        self.assertIn("-auto-", store.retry_job(auto["id"])["id"])
        sj = store.create_style_job("Yangi uslub", "izoh")
        d = store.job_dir(sj["id"])
        for n in ("a.mp4", "b.mp4"):
            (d / "input" / "refs" / n).write_bytes(b"v")
        store.update(sj["id"], state="failed", refs=sj["refs"] + ["a.mp4", "b.mp4"])
        new = store.retry_job(sj["id"])
        self.assertEqual((new["kind"], new["state"]), ("style", "queued"))
        self.assertIn("-newstyle-", new["id"])

    def test_api_route_and_guards(self):
        src = self.failed_job()
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
            path = "/api/jobs/%s/retry" % src["id"]
            self.assertEqual(request(path, header=False)[0], 403)
            with patch.object(server.Handler, "_user", return_value=None):
                self.assertEqual(request(path)[0], 401)
            self.assertEqual(len(store.list_ids()), 1)
            code, body = request(path)
            self.assertEqual((code, body["state"], body["retry_of"]), (201, "queued", src["id"]))
            self.assertEqual(request(path)[0], 400)
        finally:
            srv.shutdown()
            srv.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
