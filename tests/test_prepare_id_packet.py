"""Provisional ID packet joins the declared roles to both pinned-style products."""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.prepare_id_packet import packet_rows


class CandidateIdPacketTest(unittest.TestCase):
    def test_role_side_and_proofread_membership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotations = root / "annotations.tsv"
            annotations.write_text(
                "root_id\tcell_type\themibrain_type\tside\tstatus\tpos_x\tpos_y\tpos_z\n"
                "1\tocellar retinula cell\t\tleft\t\t10\t20\t30\n"
                "2\t\tDNp28\tleft\toutlier_seg\t40\t50\t60\n",
                encoding="utf-8",
            )
            proofread = root / "ids.npy"
            np.save(proofread, np.array([1, 2], dtype=np.uint64))
            audit = {"checks": [{"pre_root_id": "1", "post_root_id": "2",
                                 "pre_role": "photoreceptor", "post_role": "DNp28",
                                 "pre_side": "left", "post_side": "left"}]}
            rows = packet_rows(audit, annotations, proofread)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]["status"], "outlier_seg")
            self.assertEqual(rows[1]["position"], "40,50,60")
            audit["checks"][0]["post_side"] = "right"
            with self.assertRaisesRegex(ValueError, "Role/side mismatch"):
                packet_rows(audit, annotations, proofread)
            np.save(proofread, np.array([1], dtype=np.uint64))
            audit["checks"][0]["post_side"] = "left"
            with self.assertRaisesRegex(ValueError, "missing"):
                packet_rows(audit, annotations, proofread)


if __name__ == "__main__":
    unittest.main()
