"""Isolated checks for automatic recovery: a run interrupted by a dashboard restart or a Claude 429 goes back in
the queue ONCE (same job, same revision, same session); a second failure stays failed. Never touches real jobs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
import config
import runner
import store


class AutoRetryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.jobs = self.root / "jobs_dryrun"
        self.skills = self.root / "styles" / "skills"
        d = self.skills / "base_style"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: base_style\ndescription: Test\n---\n")
        self.overrides = patch.multiple(config, DATA=self.root, JOBS=self.jobs, SKILLS=self.skills,
            NEW_SKILLS=self.jobs / "_dry_skills", STYLE_NOTES=self.root / "notes.json",
            NEW_STYLE_NOTES=self.jobs / "_dry_style_notes.json",
            DELETED_STYLES=self.jobs / "_deleted_styles.json", DRY_RUN=True, AUTH=False)
        self.overrides.start()
        self.addCleanup(self.overrides.stop)
        self.worker = runner.Worker()

    def running_job(self, **extra):
        j = store.create("base_style", "t", "brief", level="rich")
        fields = dict(state="running", raw=["raw.mp4"], started=store.now(), pid=999999)
        fields.update(extra)
        return store.update(j["id"], **fields)

    def log(self, jid):
        return (store.job_dir(jid) / "progress.log").read_text(encoding="utf-8")

    # ---- dashboard restart ----

    def test_interrupted_run_is_requeued_once_then_fails(self):
        j = self.running_job()
        with patch.object(runner, "pid_alive", return_value=False):
            self.worker._recover()
        d = store.load(j["id"])
        self.assertEqual((d["state"], d["auto_retries"], d["pid"], d.get("not_before")), ("queued", 1, None, None))
        self.assertIn("qayta navbatga", self.log(j["id"]))
        store.update(j["id"], state="running", pid=999999)          # it ran again and the dashboard died again
        with patch.object(runner, "pid_alive", return_value=False):
            self.worker._recover()
        d = store.load(j["id"])
        self.assertEqual(d["state"], "failed")
        self.assertIn("allaqachon ishlatilgan", d["error"])

    def test_interrupted_revision_keeps_its_revision(self):
        j = self.running_job(revision=2, feedback=[{"n": 2, "text": "x"}], credit_cap=130)
        with patch.object(runner, "pid_alive", return_value=False):
            self.worker._recover()
        d = store.load(j["id"])
        self.assertEqual((d["state"], d["revision"], d["credit_cap"]), ("queued", 2, 130))

    def test_live_agent_is_not_requeued(self):
        j = self.running_job()
        with patch.object(runner, "pid_alive", return_value=True), patch.object(runner, "wait_pid", return_value=0), \
                patch.object(self.worker, "_finish") as fin:
            self.worker._recover()
        fin.assert_called_once_with(j["id"], 0)
        self.assertNotIn("auto_retries", store.load(j["id"]))

    def test_new_feedback_resets_the_retry_budget(self):
        j = self.running_job()
        runner.auto_requeue(j["id"], "test")
        store.update(j["id"], state="done")
        self.assertEqual(store.send_feedback(j["id"], "yana", 20)["auto_retries"], 0)

    # ---- Claude 429 ----

    def finish_with(self, jid, result_text, status=None):
        d = store.job_dir(jid)
        (d / "agent.log").write_text(json.dumps({"type": "result", "is_error": True, "result": result_text}) + "\n",
                                     encoding="utf-8")
        if status:
            (d / "result.json").write_text(json.dumps({"status": status, "summary": result_text}), encoding="utf-8")
        self.worker._finish(jid, 1)
        return store.load(jid)

    def test_rate_limit_waits_then_retries_once(self):
        j = self.running_job()
        d = self.finish_with(j["id"], "API Error: Request rejected (429) · rate_limit_error")
        self.assertEqual((d["state"], d["auto_retries"]), ("queued", 1))
        self.assertGreater(d["not_before"], store.now())
        self.assertIsNone(store.next_queued(), "a delayed job is not picked before its time")
        store.update(j["id"], not_before="2000-01-01T00:00:00")
        self.assertEqual(store.next_queued()["id"], j["id"])
        store.update(j["id"], state="running")
        d = self.finish_with(j["id"], "API Error: 429 again")
        self.assertEqual(d["state"], "failed")

    def test_other_failures_are_not_retried(self):
        a = self.finish_with(self.running_job()["id"], "Some other API error")
        self.assertEqual(a["state"], "failed")
        b = self.finish_with(self.running_job()["id"], "Higgsfield 429", status="failed")   # the agent's own verdict
        self.assertEqual(b["state"], "failed")
        c = self.running_job()
        self.worker.cancelled.add(c["id"])
        self.assertEqual(self.finish_with(c["id"], "429")["state"], "cancelled")

    # ---- the retried run resumes the same Claude session ----

    def test_retried_first_run_resumes_session(self):
        j = self.running_job()
        d = store.job_dir(j["id"])
        with patch.object(runner.config, "DRY_RUN", False), patch.object(runner, "claude_exe", return_value="claude"), \
                patch.object(runner.connections, "claude_auth", return_value={"mode": "auto", "configured": True}), \
                patch.object(runner, "can_resume", return_value=True):
            fresh = runner.build_cmd(store.load(j["id"]), d, d / "AGENT_TASK.md")
            runner.auto_requeue(j["id"], "Dashbord qayta ishga tushdi")
            again = runner.build_cmd(store.load(j["id"]), d, d / "AGENT_TASK.md")
        self.assertIn("--session-id", fresh)
        self.assertNotIn("NOTE", fresh[2])
        self.assertEqual(again[again.index("--resume") + 1], j["session_id"])
        self.assertIn("Dashbord qayta ishga tushdi", again[2])


if __name__ == "__main__":
    unittest.main()
