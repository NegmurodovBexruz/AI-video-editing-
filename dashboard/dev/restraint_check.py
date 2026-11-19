"""Isolated checks for the 'Quality' rules (one design language): engine/qa_check.c_restraint and the task text.
How often devices appear is NOT limited (the user wants dense edits); how many different looks they have is."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT / "engine"))
import config
import qa_check
import runner
import store


def dev(kind, group, a, b, asked=False):
    return {"kind": kind, "group": group, "t": [a, b], "asked": asked}


class DesignLanguageQA(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.job = Path(self.tmp.name)
        (self.job / "work").mkdir()
        self.meta({"level": "rich"})

    def meta(self, job):
        (self.job / "job.json").write_text(json.dumps(job), encoding="utf-8")

    def run_qa(self, devices, duration=76.0):
        data = {"text": []}
        if devices is not None:
            data["devices"] = devices
        (self.job / "work" / "records.json").write_text(json.dumps(data), encoding="utf-8")
        rep = {"checks": []}
        qa_check.c_restraint(rep, self.job, duration)
        return {c["id"]: c for c in rep["checks"]}

    def test_dense_but_consistent_edit_passes(self):
        devs = [dev("word captions", "caption", 0, 76)]
        for i in range(24):                      # a device every ~3 s, but only three looks
            devs.append(dev(("price receipt", "glass label", "map")[i % 3], ("card", "card", "graphic")[i % 3],
                            i * 3, i * 3 + 2))
        devs += [dev("ai insert", "insert", 10 + i * 6, 12 + i * 6) for i in range(10)]
        c = self.run_qa(devs)
        self.assertEqual({k: v["status"] for k, v in c.items()}, {"kinds": "ok"})

    def test_f9cc_like_mix_of_looks_fails(self):
        devs = [dev("word captions", "caption", 0, 76), dev("key word pills", "caption", 5, 70)]
        for i, k in enumerate(["hook title", "glass label", "receipt", "percent card", "checklist", "bread stickers"]):
            devs.append(dev(k, "card", i * 10, i * 10 + 7))
        devs += [dev("map", "graphic", 60, 66), dev("chart grid", "graphic", 40, 44)]
        c = self.run_qa(devs)
        self.assertEqual(c["kinds"]["status"], "fail")
        self.assertIn("2 xil titr", c["kinds"]["detail"])
        self.assertIn("6 xil karta", c["kinds"]["detail"])
        self.assertIn("8 xil grafik", c["kinds"]["detail"])

    def test_kind_names_are_normalised(self):
        c = self.run_qa([dev("Price  Receipt", "card", 1, 2), dev("price receipt", "card", 5, 6),
                         dev("glass label", "card", 8, 9)])
        self.assertEqual(c["kinds"]["status"], "ok")

    def test_asked_devices_do_not_count(self):
        devs = [dev("card %d" % i, "card", i * 8, i * 8 + 6, asked=True) for i in range(6)]
        self.assertEqual(self.run_qa(devs)["kinds"]["status"], "ok")

    def test_minimal_allows_no_devices(self):
        self.meta({"level": "min"})
        self.assertEqual(self.run_qa([dev("word captions", "caption", 0, 30)], 30)["minimal"]["status"], "ok")
        self.assertEqual(self.run_qa([dev("label", "card", 3, 5)], 30)["minimal"]["status"], "fail")
        self.meta({"level": "rich"})
        self.assertNotIn("minimal", self.run_qa([dev("label", "card", 3, 5)], 30))

    def test_revision_only_warns(self):
        self.meta({"level": "rich", "revision": 2})
        c = self.run_qa([dev("k%d" % i, "card", i * 5, i * 5 + 2) for i in range(10)])
        self.assertEqual(c["kinds"]["status"], "warn")

    def test_missing_or_broken_list(self):
        self.assertEqual(self.run_qa(None)["restraint"]["status"], "fail", "a first run must list its devices")
        self.meta({"level": "rich", "revision": 1})
        self.assertEqual(self.run_qa(None)["restraint"]["status"], "warn", "older edits revised later only warn")
        self.meta({"level": "rich"})
        c = self.run_qa([{"kind": "x", "group": "sticker", "t": [1, 2]}, {"kind": "", "group": "card", "t": [1, 2]},
                         {"kind": "y", "group": "card", "t": [5, 3]}])
        self.assertEqual(c["devices"]["status"], "fail")


class QualityTask(unittest.TestCase):
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

    def test_task_asks_for_design_language_not_fewer_effects(self):
        j = store.create("base_style", "t", "", level="rich")
        j = store.update(j["id"], raw=["r.mp4"], raw_info=[{"name": "r.mp4", "duration": 85, "w": 1080, "h": 1920,
                                                            "fps": 30, "audio": True}])
        t = runner.render_task(j, store.job_dir(j["id"])).read_text(encoding="utf-8")
        self.assertNotIn("{{", t)
        self.assertIn("## Quality", t)
        self.assertIn('"devices"', t)
        self.assertIn("an idea for every moment that deserves one", t)
        for gone in ("Restraint", "device budget", "Device events", "Room to breathe", "menu, not an order",
                     "keep only the strongest", "clean share"):
            self.assertNotIn(gone, t)


if __name__ == "__main__":
    unittest.main()
