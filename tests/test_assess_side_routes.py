"""Structural side-route counts keep paths distinct from unique input cells."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.assess_side_routes import side_route_rows
from flyai.selected_graph import Edge, Node, SelectedGraph, load_selected_graph


ROOT = Path(__file__).resolve().parents[1]


class SideRouteTests(unittest.TestCase):
    def test_one_input_can_have_two_paths_but_one_unique_id(self) -> None:
        nodes = (
            Node("1", "photoreceptor", "left"),
            Node("2", "photoreceptor", "center"),
            Node("3", "photoreceptor", "right"),
            Node("4", "OCG01", "left"),
            Node("5", "OCG01", "right"),
            Node("6", "DNp20", "left"),
            Node("7", "DNp20", "right"),
            Node("8", "DNp22", "left"),
            Node("9", "DNp22", "right"),
        )
        edges = tuple(Edge(pre, post, 5) for pre, post in (
            (0, 3), (0, 4), (1, 3), (2, 4),
            (3, 5), (4, 5), (4, 6), (3, 7), (4, 8)))
        graph = SelectedGraph(nodes, edges, (5, 6, 7, 8), "nodehash", "edgehash")
        rows = side_route_rows(graph)
        left_output = next(row for row in rows if row["role"] == "DNp20" and row["side"] == "left")
        self.assertEqual(left_output["ordered_paths_by_input_side"],
                         {"left": 2, "center": 1, "right": 1})
        self.assertEqual(left_output["unique_inputs_by_side"],
                         {"left": 1, "center": 1, "right": 1})
        self.assertEqual(left_output["same_side_ordered_paths"], 1)

    def test_real_selection_path_totals_match_archived_report(self) -> None:
        import json

        graph = load_selected_graph(ROOT)
        rows = side_route_rows(graph)
        archived = json.loads((ROOT / "data/derived/selected_subnetwork_report.json").read_text(
            encoding="utf-8"))
        by_id = {row["root_id"]: row for row in rows}
        for old in archived["selected_outputs"]:
            row = by_id[old["root_id"]]
            self.assertEqual(sum(row["ordered_paths_by_input_side"].values()),
                             old["distinct_ordered_role_paths"])
            self.assertEqual(row["same_side_unique_inputs"],
                             old["fully_same_side_photoreceptors"])
            self.assertEqual(row["unique_inputs_total"], old["unique_photoreceptors"])


if __name__ == "__main__":
    unittest.main()
