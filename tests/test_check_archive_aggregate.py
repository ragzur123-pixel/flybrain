"""The archived edge subtotal must fit inside its all-synapse aggregate."""

from __future__ import annotations

import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.check_archive_aggregate import compare_counts, selected_counts  # noqa: E402


class ArchiveAggregateTests(unittest.TestCase):
    def test_selected_direction_and_subset_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "counts.feather"
            table = pa.table({"pre_pt_root_id": pa.array([1, 1, 2], type=pa.int64()),
                              "neuropil": ["A", "B", "A"],
                              "count": pa.array([7, 3, 90], type=pa.int64())})
            sink = pa.BufferOutputStream()
            with ipc.new_file(sink, table.schema) as writer:
                writer.write_table(table)
            path.write_bytes(sink.getvalue().to_pybytes())
            counts, rows, regions = selected_counts(path, {1}, "pre_pt_root_id", "count")
            self.assertEqual(rows, 3)
            self.assertEqual(counts, Counter({(1, "A"): 7, (1, "B"): 3}))
            okay = compare_counts(Counter({(1, "A"): 5}), counts, {1}, regions)
            self.assertEqual(okay["violations"], [])
            self.assertEqual(okay["proofread_partner_total"], 5)
            bad = compare_counts(Counter({(1, "A"): 8}), counts, {1}, regions)
            self.assertEqual(len(bad["violations"]), 1)
            self.assertEqual(bad["violations"][0]["neuropil"], "A")
            missing = compare_counts(Counter({(1, "UNASGD"): 1}), counts, {1}, regions)
            self.assertEqual(len(missing["not_comparable"]), 1)
            self.assertEqual(missing["violations"], [])


if __name__ == "__main__":
    unittest.main()
