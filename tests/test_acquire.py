"""Behavioral checks for the bounded raw-file acquisition path."""

from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flyai.acquire import AcquisitionError, download_product, load_download_limits  # noqa: E402


class AcquireTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data" / "raw").mkdir(parents=True)
        self.source = self.root / "source.bin"
        self.source.write_bytes(b"directed-connectome-fixture")
        self.limits = {
            "max_file_bytes": 100,
            "max_total_bytes": 100,
            "min_free_disk_bytes_after": 1,
            "timeout_seconds": 5,
            "stream_chunk_bytes": 4,
        }
        self.product = {
            "product": "sample.bin",
            "path": "data/raw/sample.bin",
            "source_url": self.source.as_uri(),
            "expected_bytes": self.source.stat().st_size,
            "checksum_type": "md5",
            "checksum": hashlib.md5(self.source.read_bytes()).hexdigest(),
            "license": "test-only",
            "citation": "test-only",
        }

    def test_success_streams_verified_file_and_records_sha256_once(self) -> None:
        row = download_product(self.root, self.product, self.limits, "fafb", "783")
        target = self.root / self.product["path"]
        self.assertEqual(target.read_bytes(), self.source.read_bytes())
        self.assertEqual(row["sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        with (self.root / "data" / "raw" / "manifest.csv").open(newline="", encoding="utf-8") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [row])
        with self.assertRaisesRegex(AcquisitionError, "already exists"):
            download_product(self.root, self.product, self.limits, "fafb", "783")

    def test_checksum_failure_never_publishes_raw_or_manifest(self) -> None:
        self.product["checksum"] = "0" * 32
        with self.assertRaisesRegex(AcquisitionError, "Checksum mismatch"):
            download_product(self.root, self.product, self.limits, "fafb", "783")
        self.assertFalse((self.root / "data" / "raw" / "sample.bin").exists())
        self.assertTrue((self.root / "data" / "raw" / "sample.bin.part").exists())
        self.assertFalse((self.root / "data" / "raw" / "manifest.csv").exists())

    def test_rejects_path_escape_and_file_cap(self) -> None:
        self.product["path"] = "data/raw/../outside.bin"
        with self.assertRaisesRegex(AcquisitionError, "direct data/raw child"):
            download_product(self.root, self.product, self.limits, "fafb", "783")
        self.product["path"] = "data/raw/sample.bin"
        self.limits["max_file_bytes"] = 1
        with self.assertRaisesRegex(AcquisitionError, "per-file cap"):
            download_product(self.root, self.product, self.limits, "fafb", "783")

    def test_reads_download_limits_and_rejects_duplicate(self) -> None:
        config = self.root / "resources.yaml"
        config.write_text(
            "download:\n"
            + "".join(f"  {key}: {value}\n" for key, value in self.limits.items()),
            encoding="utf-8",
        )
        self.assertEqual(load_download_limits(config), self.limits)
        config.write_text(config.read_text(encoding="utf-8") + "  max_file_bytes: 2\n", encoding="utf-8")
        with self.assertRaisesRegex(AcquisitionError, "duplicate"):
            load_download_limits(config)


if __name__ == "__main__":
    unittest.main()
