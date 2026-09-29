"""Predeclared train-split moving-cue software smoke checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.dynamic_smoke import run_smoke


ROOT = Path(__file__).resolve().parents[1]


class DynamicSmokeTests(unittest.TestCase):
    def test_replays_on_train_seed_and_records_only_available_phases(self) -> None:
        report = run_smoke(ROOT)
        self.assertEqual(report, run_smoke(ROOT))
        self.assertEqual((report["split"], report["seed"]), ("train", 20000))
        self.assertEqual([run["scenario"] for run in report["runs"]], ["D0", "D4"])
        for run in report["runs"]:
            self.assertEqual(len(run["path"]), run["steps"] + 1)
            self.assertEqual(run["path"][0]["cue_source"], "goal")
            self.assertEqual(set(run["path"][0]["observation"]),
                             {"left", "center", "right"})
            self.assertTrue(all(0 <= speed <= 1 for point in run["path"][1:]
                                for speed in point["command_m_s"]))
            if run["steps"] >= 40:
                self.assertEqual(run["path"][40]["cue_source"], "upper")
            if run["steps"] >= 70:
                self.assertEqual(run["path"][70]["cue_source"], "lower")
            if run["steps"] >= 100:
                self.assertEqual(run["path"][100]["cue_source"], "off")
            if run["steps"] >= 120:
                self.assertEqual(run["path"][120]["cue_source"], "goal")

    def test_d4_matches_clean_prefix_then_changes_applied_motor(self) -> None:
        clean, altered = run_smoke(ROOT)["runs"]
        for step in range(21):
            self.assertEqual(clean["path"][step]["observation"],
                             altered["path"][step]["observation"])
            self.assertEqual(clean["path"][step]["pose"],
                             altered["path"][step]["pose"])
        self.assertNotEqual(clean["path"][21]["applied_wheels_m_s"],
                            altered["path"][21]["applied_wheels_m_s"])


if __name__ == "__main__":
    unittest.main()
