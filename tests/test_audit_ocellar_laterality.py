import unittest

from flyai.audit_ocellar_laterality import analyze


class LateralityAuditTest(unittest.TestCase):
    def test_recounts_distinct_photos_by_side_and_full_ipsilateral_chain(self):
        def edge(pre, post, pre_role, post_role, pre_side, post_side):
            return {"pre_root_id": pre, "post_root_id": post, "pre_role": pre_role,
                    "post_role": post_role, "pre_side": pre_side, "post_side": post_side,
                    "pair_synapses": 5}
        screen = {"candidate_pairs": [
            edge("pL", "oL", "photoreceptor", "OCG01", "left", "left"),
            edge("pR", "oL", "photoreceptor", "OCG01", "right", "left"),
            edge("pL", "oR", "photoreceptor", "OCG01", "left", "right"),
            edge("oL", "dL", "OCG01", "DNp20", "left", "left"),
            edge("oR", "dL", "OCG01", "DNp20", "right", "left"),
            edge("pL", "dL", "photoreceptor", "DNp20", "left", "left"),
        ], "two_hop_paths_by_pair_summed_synapse_threshold": {"5": [{
            "output_root_id": "dL", "direct_photoreceptors": 1,
            "direct_ocg_inputs": 2, "two_hop_photoreceptors": 2,
        }]}}
        row = analyze(screen, 5)[0]
        self.assertEqual(row["two_hop_unique_total"], 2)
        self.assertEqual(row["two_hop_photoreceptors_by_side"],
                         {"left": 1, "right": 1, "center": 0})
        self.assertEqual(row["full_ipsilateral_two_hop_photoreceptors"], 1)
        self.assertEqual(row["ocg_inputs_by_side"],
                         {"left": 1, "right": 1, "center": 0})

    def test_rejects_saved_screen_disagreement(self):
        screen = {"candidate_pairs": [{
            "pre_root_id": "p", "post_root_id": "d", "pre_role": "photoreceptor",
            "post_role": "DNp28", "pre_side": "left", "post_side": "left",
            "pair_synapses": 5,
        }], "two_hop_paths_by_pair_summed_synapse_threshold": {"5": [{
            "output_root_id": "d", "direct_photoreceptors": 2,
            "direct_ocg_inputs": 0, "two_hop_photoreceptors": 0,
        }]}}
        with self.assertRaises(ValueError):
            analyze(screen, 5)
