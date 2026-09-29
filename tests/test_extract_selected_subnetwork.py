"""Selected graph invariants: role pairing and directed output reachability."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.extract_selected_subnetwork import (unreachable_to_outputs,
                                                validate_config,
                                                weak_component_sizes)


class SelectedExtractionTests(unittest.TestCase):
    def test_components_and_directed_reachability_are_distinct(self) -> None:
        nodes = ["1", "2", "3", "4"]
        edges = [{"pre_root_id": "1", "post_root_id": "2"},
                 {"pre_root_id": "3", "post_root_id": "2"}]
        self.assertEqual(weak_component_sizes(nodes, edges), [3, 1])
        self.assertEqual(unreachable_to_outputs(nodes, edges, {"2"}), ["4"])
        self.assertEqual(unreachable_to_outputs(nodes, edges, {"1"}), ["2", "3", "4"])

    def test_config_rejects_missing_bilateral_output(self) -> None:
        inventory = {"1": {"role": "DNp20", "side": "left"},
                     "2": {"role": "DNp20", "side": "right"},
                     "3": {"role": "DNp22", "side": "left"},
                     "4": {"role": "DNp22", "side": "left"}}
        config = {"output_roles": ["DNp20", "DNp22"], "side_policy": "all_sides",
                  "min_pair_synapses": 5, "sensitivity_min_pair_synapses": 1,
                  "behavior_data_used_for_selection": False,
                  "output_root_ids": ["1", "2", "3", "4"],
                  "max_nodes": 128, "max_directed_edges": 200}
        with self.assertRaisesRegex(ValueError, "not bilateral"):
            validate_config(config, inventory)


if __name__ == "__main__":
    unittest.main()
