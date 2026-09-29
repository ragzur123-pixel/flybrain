import csv
import math
import unittest
from pathlib import Path

from sys import path as sys_path
sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.episode_record import EPISODE_FIELDS, run_fixed_command


CONFIG = Path(__file__).resolve().parents[1] / "configs/environment_v1.yaml"


class EpisodeRecordTests(unittest.TestCase):
    def test_success_and_completed_failure_use_full_guide_schema(self):
        success = run_fixed_command(CONFIG, scenario="D0", episode_id=0)
        failure = run_fixed_command(CONFIG, scenario="D4", episode_id=1)
        for row in (success, failure):
            self.assertEqual(tuple(row), EPISODE_FIELDS)
            self.assertEqual(row["split"], "fixture")
            self.assertEqual(row["seed_group"], "fixture_s0001")
            self.assertEqual(row["shortest_valid_path"], "")
            self.assertGreater(row["wall_seconds"], 0)
            self.assertTrue(math.isfinite(row["path_length"]))
            self.assertTrue(math.isfinite(row["return"]))
        self.assertEqual((success["success"], success["termination_reason"], success["steps"]),
                         (1, "goal", 79))
        self.assertEqual((failure["success"], failure["termination_reason"], failure["steps"]),
                         (0, "timeout", 300))
        self.assertEqual(failure["collisions"], 0)

    def test_saved_fixture_matches_recomputed_deterministic_fields(self):
        path = CONFIG.parents[1] / "data/derived/environment_episodes_fixture.csv"
        if not path.exists():
            self.skipTest("Fixture CSV is generated separately")
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(tuple(reader.fieldnames), EPISODE_FIELDS)
            saved = list(reader)
        self.assertEqual(len(saved), 2)
        for i, scenario in enumerate(("D0", "D4")):
            recomputed = run_fixed_command(CONFIG, scenario=scenario, episode_id=i)
            for field in EPISODE_FIELDS:
                if field != "wall_seconds":
                    self.assertEqual(saved[i][field], str(recomputed[field]))


if __name__ == "__main__":
    unittest.main()
