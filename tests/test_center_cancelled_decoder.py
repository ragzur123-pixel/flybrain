"""Synthetic center cancellation, cue switches, and bounded fixture replay."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.center_cancelled_decoder import CenterCancelledDecoder, run_fixture
from flyai.selected_graph import load_selected_graph


ROOT = Path(__file__).resolve().parents[1]
PROBE = json.loads((ROOT / "configs/unsigned_rate_probe_v0.yaml").read_text(encoding="utf-8"))
CONFIG = json.loads((ROOT / "configs/decoder_fixture_v1.yaml").read_text(encoding="utf-8"))


def new_decoder() -> CenterCancelledDecoder:
    return CenterCancelledDecoder(load_selected_graph(ROOT), PROBE, CONFIG)


class CenterCancelledDecoderTests(unittest.TestCase):
    def test_center_only_is_neutral_through_on_change_and_off(self) -> None:
        decoder = new_decoder()
        center_values = [0.0, 0.3, 1.0, 0.2, 0.9, 0.0] * 4
        for center in center_values:
            step = decoder.step({"left": 0.0, "center": center, "right": 0.0})
            self.assertAlmostEqual(step["corrected_score"], 0.0, places=12)
            self.assertAlmostEqual(step["command_m_s"][0], 0.6, places=12)
            self.assertAlmostEqual(step["command_m_s"][1], 0.6, places=12)

    def test_center_stream_does_not_change_side_turn_under_switch_and_loss(self) -> None:
        clean = new_decoder()
        mixed = new_decoder()
        side_schedule = [(1.0, 0.0)] * 12 + [(0.0, 1.0)] * 12 + [(0.0, 0.0)] * 24
        center_schedule = [0.2, 1.0, 0.5, 0.0] * 12
        clean_scores, mixed_scores = [], []
        for (left, right), center in zip(side_schedule, center_schedule):
            clean_scores.append(clean.step({"left": left, "center": 0.0,
                                            "right": right})["corrected_score"])
            mixed_scores.append(mixed.step({"left": left, "center": center,
                                            "right": right})["corrected_score"])
        for expected, actual in zip(clean_scores, mixed_scores):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertGreater(clean_scores[11], 0)
        self.assertLess(clean_scores[23], 0)
        self.assertLess(abs(clean_scores[-1]), 1e-6)

    def test_reset_bad_input_and_action_bounds(self) -> None:
        decoder = new_decoder()
        cue = {"left": 1.0, "center": 0.4, "right": 0.0}
        expected = [decoder.step(cue) for _ in range(4)]
        decoder.reset()
        self.assertEqual([decoder.step(cue) for _ in range(4)], expected)
        for bad in ({"left": 0.0, "center": math.nan, "right": 0.0},
                    {"left": 0.0, "center": 0.0, "right": 0.0, "pose": 1.0}):
            with self.assertRaises(ValueError):
                decoder.step(bad)
        replay = new_decoder()
        for _ in range(4):
            replay.step(cue)
        self.assertEqual(decoder.step(cue), replay.step(cue))
        self.assertTrue(all(0 <= speed <= 1 for step in expected
                            for speed in step["command_m_s"]))

    def test_rejects_changed_output_order_and_gain(self) -> None:
        graph = load_selected_graph(ROOT)
        bad_order = dict(CONFIG, output_order=list(reversed(CONFIG["output_order"])))
        with self.assertRaisesRegex(ValueError, "config/version"):
            CenterCancelledDecoder(graph, PROBE, bad_order)
        bad_gain = dict(CONFIG, gain_m_s_per_rate_unit=-1.0)
        with self.assertRaisesRegex(ValueError, "base/gain"):
            CenterCancelledDecoder(graph, PROBE, bad_gain)

    def test_fixed_episode_replays_and_uses_fixture_only(self) -> None:
        first, second = run_fixture(ROOT), run_fixture(ROOT)
        self.assertEqual(first, second)
        self.assertEqual((first["split"], first["scenario"]), ("fixture", "D0"))
        self.assertEqual(len(first["path"]), first["steps"] + 1)
        self.assertLessEqual(first["steps"], 300)
        self.assertEqual(set(first["path"][0]["observation"]),
                         {"left", "center", "right"})


if __name__ == "__main__":
    unittest.main()
