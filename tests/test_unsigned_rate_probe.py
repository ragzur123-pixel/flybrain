"""Exploratory unsigned response probe: software causality and bounds only."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.selected_graph import Edge, Node, SelectedGraph, load_selected_graph
from flyai.unsigned_rate_probe import UnsignedRateProbe


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/unsigned_rate_probe_v0.yaml"


def tiny_graph() -> SelectedGraph:
    nodes = (Node("1", "photoreceptor", "left"),
             Node("2", "photoreceptor", "right"),
             Node("3", "OCG01", "left"),
             Node("4", "DNp20", "left"), Node("5", "DNp20", "right"),
             Node("6", "DNp22", "left"), Node("7", "DNp22", "right"))
    edges = (Edge(0, 2, 1), Edge(1, 2, 3),
             Edge(2, 3, 2), Edge(2, 4, 2), Edge(2, 5, 2), Edge(2, 6, 2))
    return SelectedGraph(nodes, edges, (3, 4, 5, 6), "n", "e")


def tiny_config() -> dict:
    return {"dt_s": 0.1, "relaxation_fraction_per_step": 0.5,
            "input_channels": ["left", "center", "right"],
            "input_range": [0.0, 1.0],
            "nodes_csv_sha256": "n", "edges_csv_sha256": "e"}


class UnsignedRateProbeTests(unittest.TestCase):
    def test_direction_count_normalization_and_one_step_relay_delay(self) -> None:
        probe = UnsignedRateProbe(tiny_graph(), tiny_config())
        left = {"left": 1.0, "center": 0.0, "right": 0.0}
        self.assertEqual(probe.step(left), (0.0, 0.0, 0.0, 0.0))
        self.assertAlmostEqual(probe.rates_snapshot()[2], 0.125)
        self.assertEqual(probe.step(left), (0.0625,) * 4)
        probe.reset()
        self.assertEqual(probe.step({"left": 0.0, "center": 0.0, "right": 1.0}),
                         (0.0,) * 4)
        self.assertAlmostEqual(probe.rates_snapshot()[2], 0.375)

    def test_silence_reset_replay_and_bad_input_is_transactional(self) -> None:
        probe = UnsignedRateProbe(tiny_graph(), tiny_config())
        cue = {"left": 1.0, "center": 0.0, "right": 0.0}
        sequence = [probe.step(cue) for _ in range(5)]
        before = probe.rates_snapshot()
        for invalid in (
            {"left": math.nan, "center": 0.0, "right": 0.0},
            {"left": -0.1, "center": 0.0, "right": 0.0},
            {"left": 0.0, "center": 0.0},
            {"left": 0.0, "center": 0.0, "right": 0.0, "goal": 1.0},
        ):
            with self.assertRaises(ValueError):
                probe.step(invalid)
            self.assertEqual(probe.rates_snapshot(), before)
        off = {"left": 0.0, "center": 0.0, "right": 0.0}
        for _ in range(40):
            tail = probe.step(off)
        self.assertLess(max(tail), 1e-8)
        probe.reset()
        self.assertEqual([probe.step(cue) for _ in range(5)], sequence)

    def test_selected_graph_is_bounded_and_config_hashes_match(self) -> None:
        graph = load_selected_graph(ROOT)
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        probe = UnsignedRateProbe(graph, config)
        self.assertEqual(probe.step({"left": 1.0, "center": 0.0, "right": 0.0}),
                         (0.0,) * 4)
        response = probe.step({"left": 1.0, "center": 0.0, "right": 0.0})
        self.assertTrue(all(0.0 < value < 1.0 for value in response))
        config["edges_csv_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "graph checksum"):
            UnsignedRateProbe(graph, config)

    def test_rejects_invalid_relaxation(self) -> None:
        config = tiny_config()
        config["relaxation_fraction_per_step"] = 1.1
        with self.assertRaisesRegex(ValueError, "relaxation"):
            UnsignedRateProbe(tiny_graph(), config)


if __name__ == "__main__":
    unittest.main()
