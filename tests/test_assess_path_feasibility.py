import unittest

from flyai.assess_path_feasibility import summarize, validate_rule


class PathFeasibilityTest(unittest.TestCase):
    def test_direct_and_two_hop_routes_use_different_counts(self):
        rows = []
        statuses = {}
        for role in ("DNp20", "DNp22", "DNp28"):
            for side in ("left", "right"):
                root_id = f"{role}_{side}"
                statuses[root_id] = "outlier_seg" if root_id == "DNp28_right" else "(blank)"
                rows.append({"output_root_id": root_id, "role": role, "side": side,
                             "direct_photoreceptors_by_side": {"left": 1, "right": 1, "center": 0},
                             "two_hop_photoreceptors_by_side": {"left": 3, "right": 3, "center": 1},
                             "two_hop_unique_total": 7,
                             "full_ipsilateral_two_hop_photoreceptors": 0 if root_id == "DNp20_left" else 2})
        result = summarize(rows, statuses)
        self.assertFalse(result["left_right_role_feasible"]["DNp20"])
        self.assertTrue(result["left_right_role_feasible"]["DNp28"])
        dnp28 = next(x for x in result["outputs"] if x["output_root_id"] == "DNp28_right")
        self.assertEqual(dnp28["route"], "direct")
        self.assertEqual(dnp28["fully_same_side_photoreceptors"], 1)
        self.assertEqual(dnp28["status"], "outlier_seg")

    def test_rule_requires_ordered_positive_thresholds(self):
        rule = {"primary_min_pair_synapses": 5, "sensitivity_min_pair_synapses": 1,
                "no_behavior_use": True,
                "route_by_output_role": {"DNp20": "two", "DNp22": "two", "DNp28": "one"}}
        self.assertEqual(validate_rule(rule), (5, 1))
        rule["sensitivity_min_pair_synapses"] = 5
        with self.assertRaises(ValueError):
            validate_rule(rule)
