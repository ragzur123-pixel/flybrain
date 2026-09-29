"""Synthetic invariant checks for the streaming validator; these are not biology tests."""

from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.validate_raw import ValidationError, scan_connections, verify_manifest  # noqa: E402


def write_feather(path: Path, *, include_syn_count: bool = True) -> None:
    columns = {
        "pre_pt_root_id": pa.array([1, 1, 2], type=pa.int64()),
        "post_pt_root_id": pa.array([2, 2, 2], type=pa.int64()),
        "neuropil": pa.array(["A", "A", "B"], type=pa.string()),
        "syn_count": pa.array([2, 2, 3], type=pa.int64()),
    }
    if not include_syn_count:
        del columns["syn_count"]
    for name in ("gaba_avg", "ach_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg"):
        columns[name] = pa.array([0.1, None, 0.2], type=pa.float64())
    table = pa.table(columns)
    with ipc.new_file(str(path), table.schema) as writer:
        writer.write_table(table, max_chunksize=2)


class ValidateRawTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / "data" / "raw"
        self.derived = self.root / "data" / "derived"
        self.raw.mkdir(parents=True)
        self.derived.mkdir(parents=True)

    def test_counts_direction_duplicate_key_and_null_probability(self) -> None:
        source = self.raw / "connections.feather"
        write_feather(source)
        report = scan_connections(
            source, {1, 2}, self.derived / "keys.sqlite",
            batch_rows=2, max_temp_bytes=1_000_000,
            max_rss_bytes=10_000_000_000, min_free_disk_bytes=1,
        )
        self.assertTrue(report["complete"])
        self.assertEqual(report["rows"], 3)
        self.assertEqual(report["duplicate_pair_neuropil_rows"], 1)
        self.assertEqual(report["self_loops"], 1)
        self.assertEqual(report["syn_count_total"], 7)
        self.assertEqual(report["nulls"]["gaba_avg"], 1)
        self.assertEqual(report["pre_ids_absent_from_proofread"], 0)
        self.assertEqual(report["post_ids_absent_from_proofread"], 0)

    def test_rejects_missing_required_connection_field(self) -> None:
        source = self.raw / "connections.feather"
        write_feather(source, include_syn_count=False)
        with self.assertRaisesRegex(ValidationError, "syn_count"):
            scan_connections(
                source, {1, 2}, self.derived / "keys.sqlite",
                batch_rows=2, max_temp_bytes=1_000_000,
                max_rss_bytes=10_000_000_000, min_free_disk_bytes=1,
            )

    def test_manifest_hash_mismatch_blocks_parsing(self) -> None:
        raw_file = self.raw / "sample.bin"
        raw_file.write_bytes(b"observed")
        manifest = self.raw / "manifest.csv"
        with manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=(
                "dataset_id", "snapshot", "product", "path", "bytes", "sha256"
            ))
            writer.writeheader()
            writer.writerow({
                "dataset_id": "fafb", "snapshot": "783", "product": "sample.bin",
                "path": "data/raw/sample.bin", "bytes": 8,
                "sha256": hashlib.sha256(b"changed!").hexdigest(),
            })
        with self.assertRaisesRegex(ValidationError, "SHA-256 mismatch"):
            verify_manifest(self.root, manifest, {"sample.bin"})


if __name__ == "__main__":
    unittest.main()
