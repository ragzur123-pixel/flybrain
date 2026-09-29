"""Codex export reconciliation preserves provenance and reports mismatches."""

import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.reconcile_codex_exports import reconcile


class ReconcileCodexExportsTest(unittest.TestCase):
    def test_mismatch_and_hash_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            export_dir = root / "data/derived/codex_portal_2026-09-26"
            export_dir.mkdir(parents=True)
            file = export_dir / "2.csv"
            with file.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["From", "To", "Neuropil", "Synapses", "Neuro Transmitter"])
                writer.writerow(["1", "2", "OCG", "8", "ACH"])
                writer.writerow(["2", "1", "OCG", "3", "ACH"])
            content = file.read_bytes()
            manifest = [{"post_root_id": "2", "path": "data/derived/codex_portal_2026-09-26/2.csv",
                         "source_url": "https://codex.flywire.ai/app/connectivity?data_version=783&cell_names_or_ids=root_id+%3D%3D+2&show_regions=1&download=csv&dataset=fafb",
                         "bytes": str(len(content)), "sha256": hashlib.sha256(content).hexdigest()}]
            audit = {"portal_verified": False, "raw_sha256": "archive-hash", "checks": [
                {"pre_root_id": "1", "post_root_id": "2", "pre_role": "photoreceptor",
                 "post_role": "DNp28", "pre_side": "left", "post_side": "left", "forward_synapses": 5,
                 "forward_rows": [{"neuropil": "OCG", "syn_count": 5}], "reverse_synapses": 0}]}
            result = reconcile(audit, manifest, root)
            self.assertEqual((result["matched"], result["discrepant"]), (0, 1))
            self.assertEqual(result["pairs"][0]["delta"], 3)
            self.assertEqual(result["pairs"][0]["codex_reverse_synapses"], 3)
            file.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash or size"):
                reconcile(audit, manifest, root)


if __name__ == "__main__":
    unittest.main()
