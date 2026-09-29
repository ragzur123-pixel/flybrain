"""Meaningful direction, path, and side-policy checks for C04 comparison."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.compare_circuit_options import option_footprint


def node(role: str, side: str) -> dict:
    return {"role": role, "side": side, "status": "(blank)"}


def edge(pre: str, post: str, inventory: dict, count: int = 5) -> dict:
    return {"pre_root_id": pre, "post_root_id": post,
            "pre_role": inventory[pre]["role"], "post_role": inventory[post]["role"],
            "pre_side": inventory[pre]["side"], "post_side": inventory[post]["side"],
            "pair_synapses": count}


class OptionFootprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = {
            "pl": node("photoreceptor", "left"),
            "pr": node("photoreceptor", "right"),
            "ol": node("OCG01", "left"),
            "or": node("OCG01", "right"),
            "dl": node("DNp20", "left"),
            "dr": node("DNp20", "right"),
        }

    def test_strict_side_drops_cross_path_but_preserves_bilateral_paths(self) -> None:
        p = self.inventory
        pairs = [edge("pl", "ol", p), edge("pr", "or", p),
                 edge("pl", "or", p), edge("ol", "dl", p), edge("or", "dr", p)]
        all_sides = option_footprint(pairs, p, ("DNp20",), 5, False)
        strict = option_footprint(pairs, p, ("DNp20",), 5, True)
        self.assertEqual((all_sides["node_count"], all_sides["directed_edge_count"]), (6, 5))
        self.assertEqual((strict["node_count"], strict["directed_edge_count"]), (6, 4))
        self.assertTrue(strict["all_outputs_reachable"])
        self.assertEqual([r["unique_photoreceptors"] for r in strict["outputs"]], [1, 1])

    def test_wrong_direction_and_incomplete_path_do_not_enter_footprint(self) -> None:
        p = self.inventory
        pairs = [edge("ol", "pl", p), edge("or", "dr", p),
                 edge("pl", "ol", p, 4), edge("ol", "dl", p)]
        result = option_footprint(pairs, p, ("DNp20",), 5, False)
        self.assertEqual(result["directed_edge_count"], 0)
        self.assertEqual(result["node_count"], 2)
        self.assertFalse(result["all_outputs_reachable"])

    def test_duplicate_pair_rejected(self) -> None:
        p = self.inventory
        pair = edge("pl", "ol", p)
        with self.assertRaisesRegex(ValueError, "Duplicate ordered pair"):
            option_footprint([pair, pair], p, ("DNp20",), 5, False)


if __name__ == "__main__":
    unittest.main()
