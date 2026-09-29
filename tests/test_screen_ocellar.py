"""Check direction and pair-summed thresholds in the exploratory path screen."""

import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.screen_ocellar import candidate_labels, screen


class OcellarScreenTest(unittest.TestCase):
    def test_directed_two_hop_path_uses_pair_summed_weights(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotations = root / "annotations.tsv"
            annotations.write_text(
                "root_id\tcell_type\themibrain_type\tside\tstatus\n"
                "1\tocellar retinula cell\t\tleft\t\n"
                "2\tOCG01a\t\tleft\t\n"
                "3\t\tDNp20\tleft\t\n",
                encoding="utf-8",
            )
            path = root / "connections.feather"
            table = pa.table({
                "pre_pt_root_id": [1, 1, 2, 3],
                "post_pt_root_id": [2, 2, 3, 1],
                "syn_count": [3, 3, 6, 20],
            })
            with pa.OSFile(str(path), "wb") as sink:
                with ipc.new_file(sink, table.schema) as writer:
                    writer.write_table(table)

            result = screen(path, candidate_labels(annotations), batch_rows=2)
            self.assertEqual(result["row_count_scanned"], 4)
            self.assertEqual(result["candidate_pair_count"], 3)
            for threshold in ("1", "5"):
                path_result = result["two_hop_paths_by_pair_summed_synapse_threshold"][threshold][0]
                self.assertEqual(path_result["direct_ocg_inputs"], 1)
                self.assertEqual(path_result["two_hop_photoreceptors"], 1)

    def test_distinguishes_direct_dnp28_from_two_hop_dnp22(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            annotations = root / "annotations.tsv"
            annotations.write_text(
                "root_id\tcell_type\themibrain_type\tside\tstatus\n"
                "1\tocellar retinula cell\t\tleft\t\n"
                "2\tOCG01a\t\tleft\t\n"
                "3\t\tDNp28\tleft\t\n"
                "4\tDNp22\t\tleft\t\n",
                encoding="utf-8",
            )
            table = pa.table({
                "pre_pt_root_id": [1, 1, 2],
                "post_pt_root_id": [2, 3, 4],
                "syn_count": [6, 9, 7],
            })
            path = root / "connections.feather"
            with pa.OSFile(str(path), "wb") as sink:
                with ipc.new_file(sink, table.schema) as writer:
                    writer.write_table(table)

            labels = candidate_labels(annotations)
            self.assertEqual(labels[4]["role"], "DNp22")
            outputs = screen(path, labels)["two_hop_paths_by_pair_summed_synapse_threshold"]["5"]
            by_role = {item["output_role"]: item for item in outputs}
            self.assertEqual(by_role["DNp28"]["direct_photoreceptors"], 1)
            self.assertEqual(by_role["DNp28"]["two_hop_photoreceptors"], 0)
            self.assertEqual(by_role["DNp22"]["direct_photoreceptors"], 0)
            self.assertEqual(by_role["DNp22"]["two_hop_photoreceptors"], 1)


if __name__ == "__main__":
    unittest.main()
