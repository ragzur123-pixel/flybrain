"""Tests for reproducible, visible manual-check selection."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.prepare_manual_checks import STRATA, select_checks


class PrepareManualChecksTest(unittest.TestCase):
    def test_ten_stratified_pairs_with_distinct_sources(self):
        pairs = []
        for group, (pre_role, post_role, pre_side, post_side, needed) in enumerate(STRATA):
            for index in range(needed):
                pairs.append({
                    "pre_root_id": str(group * 10 + index + 1),
                    "post_root_id": str(group + 100),
                    "pre_role": pre_role, "post_role": post_role,
                    "pre_side": pre_side, "post_side": post_side,
                    "pair_synapses": 20 - index,
                })
            pairs.append({
                **pairs[-1], "post_root_id": str(group + 200),
                "pair_synapses": 4,
            })
        checks = select_checks(pairs)
        self.assertEqual(len(checks), 10)
        self.assertTrue(all(pair["pair_synapses"] >= 5 for pair in checks))
        self.assertEqual(len({pair["pre_root_id"] for pair in checks}), 10)


if __name__ == "__main__":
    unittest.main()
