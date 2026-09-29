import unittest

from flyai.prepare_candidate_inventory import inventory


class CandidateInventoryTest(unittest.TestCase):
    def row(self, root_id, cell_type, hemibrain_type="", side="left", status=""):
        return {"root_id": str(root_id), "cell_type": cell_type,
                "hemibrain_type": hemibrain_type, "side": side, "status": status,
                "pos_x": "1", "pos_y": "2", "pos_z": "3"}

    def test_uses_actual_annotation_field_and_retains_flag(self):
        rows = inventory([
            self.row(3, "", "DNp28", "right", "outlier_seg"),
            self.row(1, "ocellar retinula cell"),
            self.row(2, "DNp22"),
        ], {1, 2, 3})
        self.assertEqual([r["root_id"] for r in rows], ["1", "2", "3"])
        self.assertEqual([r["annotation_field"] for r in rows],
                         ["cell_type", "cell_type", "hemibrain_type"])
        self.assertEqual(rows[2]["status"], "outlier_seg")

    def test_missing_proofread_id_and_duplicate_are_rejected(self):
        with self.assertRaises(ValueError):
            inventory([self.row(1, "DNp22")], set())
        with self.assertRaises(ValueError):
            inventory([self.row(1, "DNp22"), self.row(1, "DNp22")], {1})
