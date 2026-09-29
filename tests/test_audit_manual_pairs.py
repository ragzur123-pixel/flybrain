"""Direction and independent row aggregation for the manual-pair audit."""

import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.audit_manual_pairs import audit_pairs


class ManualPairAuditTest(unittest.TestCase):
    def test_aggregates_forward_rows_and_keeps_reverse_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pairs.feather"
            table = pa.table({
                "pre_pt_root_id": [1, 1, 2, 9],
                "post_pt_root_id": [2, 2, 1, 1],
                "neuropil": ["B", "A", "C", "D"],
                "syn_count": [3, 4, 11, 99],
            })
            with pa.OSFile(str(path), "wb") as sink:
                with ipc.new_file(sink, table.schema) as writer:
                    writer.write_table(table)
            check = {"pre_root_id": "1", "post_root_id": "2", "pre_role": "photo",
                     "post_role": "output", "pre_side": "left", "post_side": "left",
                     "pair_synapses": 7, "neuropil_rows": 2}
            result = audit_pairs(path, [check], batch_rows=2)
            self.assertEqual(result["rows_scanned"], 4)
            self.assertEqual(result["checks"][0]["forward_rows"], [
                {"neuropil": "A", "syn_count": 4}, {"neuropil": "B", "syn_count": 3}])
            self.assertEqual(result["checks"][0]["reverse_synapses"], 11)
            self.assertFalse(result["portal_verified"])
            check["pair_synapses"] = 8
            with self.assertRaisesRegex(ValueError, "disagree"):
                audit_pairs(path, [check])


if __name__ == "__main__":
    unittest.main()
