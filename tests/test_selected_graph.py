"""Checks for the route-independent selected graph interface."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.selected_graph import load_selected_graph


ROOT = Path(__file__).resolve().parents[1]


class SelectedGraphTests(unittest.TestCase):
    def test_verified_archive_graph_has_bilateral_named_outputs(self) -> None:
        graph = load_selected_graph(ROOT)
        self.assertEqual((len(graph.nodes), len(graph.edges)), (119, 169))
        self.assertEqual(sum(edge.pair_synapses for edge in graph.edges), 4434)
        self.assertEqual(set(graph.outputs), {
            ("DNp20", "left"), ("DNp20", "right"),
            ("DNp22", "left"), ("DNp22", "right")})
        self.assertEqual(len(graph.input_indices("center")), 33)
        self.assertTrue(all(graph.nodes[edge.pre_index].role == "photoreceptor" and
                            graph.nodes[edge.post_index].role == "OCG01"
                            or graph.nodes[edge.pre_index].role == "OCG01" and
                            graph.nodes[edge.post_index].role in {"DNp20", "DNp22"}
                            for edge in graph.edges))

    def copied_graph(self, directory: Path) -> Path:
        (directory / "data/derived").mkdir(parents=True)
        (directory / "configs").mkdir()
        for name in ("selected_subnetwork_nodes.csv", "selected_subnetwork_edges.csv",
                     "selected_subnetwork_report.json"):
            shutil.copyfile(ROOT / "data/derived" / name, directory / "data/derived" / name)
        shutil.copyfile(ROOT / "configs/subnetwork_selection.yaml",
                        directory / "configs/subnetwork_selection.yaml")
        return directory

    def test_rejects_tampered_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copied_graph(Path(tmp))
            edge_path = root / "data/derived/selected_subnetwork_edges.csv"
            edge_path.write_bytes(edge_path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_selected_graph(root)

    def test_rejects_role_mismatch_even_with_updated_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copied_graph(Path(tmp))
            edge_path = root / "data/derived/selected_subnetwork_edges.csv"
            content = edge_path.read_text(encoding="utf-8")
            edge_path.write_text(content.replace(",photoreceptor,OCG01,", ",OCG01,OCG01,", 1),
                                 encoding="utf-8", newline="")
            report_path = root / "data/derived/selected_subnetwork_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["edges_csv_sha256"] = hashlib.sha256(edge_path.read_bytes()).hexdigest()
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "metadata"):
                load_selected_graph(root)


if __name__ == "__main__":
    unittest.main()
