"""Exploratory wheel decoder and one bounded software integration fixture."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.decoder_fixture import decode_wheels, run_fixture


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "configs/decoder_fixture_v0.yaml").read_text(encoding="utf-8"))


class DecoderFixtureTests(unittest.TestCase):
    def test_opponent_direction_silence_and_clipping(self) -> None:
        self.assertEqual(decode_wheels((0, 0, 0, 0), CONFIG), (0.6, 0.6))
        left = decode_wheels((1, 0, 1, 0), CONFIG)
        right = decode_wheels((0, 1, 0, 1), CONFIG)
        self.assertAlmostEqual(left[0], 0.1)
        self.assertEqual(left[1], 1.0)
        self.assertEqual(right[0], 1.0)
        self.assertAlmostEqual(right[1], 0.1)
        self.assertAlmostEqual(left[0], right[1])
        self.assertAlmostEqual(left[1], right[0])

    def test_bad_values_and_contract_are_rejected(self) -> None:
        for output in ((0, 0, 0), (0, 0, 0, math.nan), (0, 0, 0, 1.1)):
            with self.assertRaises(ValueError):
                decode_wheels(output, CONFIG)
        changed = dict(CONFIG, output_order=list(reversed(CONFIG["output_order"])))
        with self.assertRaises(ValueError):
            decode_wheels((0, 0, 0, 0), changed)

    def test_fixed_episode_replays_without_hidden_state(self) -> None:
        first = run_fixture(ROOT)
        second = run_fixture(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first["scenario"], "D0")
        self.assertEqual(first["split"], "fixture")
        self.assertGreater(first["steps"], 0)
        self.assertLessEqual(first["steps"], 300)
        self.assertEqual(len(first["path"]), first["steps"] + 1)
        self.assertTrue(all(0 <= speed <= 1 for point in first["path"]
                            for speed in point["command_m_s"]))
        self.assertTrue(all(math.isfinite(value) for point in first["path"]
                            for value in point["pose"]))
        self.assertEqual(set(first["path"][0]["observation"]), {"left", "center", "right"})


if __name__ == "__main__":
    unittest.main()
