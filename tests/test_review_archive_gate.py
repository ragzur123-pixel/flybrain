import unittest

from flyai.review_archive_gate import AGGREGATE, GRAPH, PRODUCTS, assess


class ArchiveGateTest(unittest.TestCase):
    def setUp(self):
        self.manifest = [{"product": name, "dataset_id": "fafb", "snapshot": "783",
                          "sha256": name[0] * 64, "source_url": f"https://example.test/{name}",
                          "bytes": "10"} for name in sorted(PRODUCTS)]
        self.sources = {"products": [{"product": row["product"], "source_url": row["source_url"],
                                      "expected_bytes": 10, "checksum_type": "md5", "checksum": "abc"}
                                     for row in self.manifest]}
        self.validation = {"dataset_id": "fafb", "snapshot": "783",
                           "manifest_sha256": {row["product"]: row["sha256"] for row in self.manifest},
                           "connections": {"complete": True, "rows": 16847997,
                                           "batches_scanned": 2, "record_batches": 2,
                                           "duplicate_pair_neuropil_rows": 0,
                                           "nonpositive_syn_count": 0,
                                           "pre_ids_absent_from_proofread": 0,
                                           "post_ids_absent_from_proofread": 0}}
        graph_sha = next(row["sha256"] for row in self.manifest if row["product"] == GRAPH)
        aggregate_sha = next(row["sha256"] for row in self.manifest if row["product"] == AGGREGATE)
        self.pairs = {"raw_sha256": graph_sha, "rows_scanned": 16847997,
                      "checks": [{"pre_root_id": str(i), "post_root_id": str(i+100),
                                  "forward_synapses": 6, "forward_rows": [{"neuropil": "OCG", "syn_count": 6}]}
                                 for i in range(10)]}
        self.aggregate = {"release": "Zenodo 10676866",
                          "source_sha256": {GRAPH: graph_sha, AGGREGATE: aggregate_sha},
                          "selected_neurons": 19, "edge_rows_scanned": 16847997,
                          "comparable_regions": 56, "region_comparisons": 58,
                          "violations": [], "not_comparable": [{"neuropil": "UNASGD"}] * 2}
        self.codex = {"archive_sha256": graph_sha, "codex_exports": 10,
                      "matched": 0, "discrepant": 10,
                      "comparison": "publication-time archive vs current Codex export"}

    def result(self):
        return assess(self.manifest, self.sources, self.validation,
                      self.pairs, self.aggregate, self.codex)

    def test_complete_archive_evidence_passes(self):
        self.assertTrue(self.result()["pass"])

    def test_uncovered_pair_or_changed_source_fails(self):
        self.pairs["checks"][0]["forward_rows"][0]["neuropil"] = "UNASGD"
        self.assertFalse(self.result()["pass"])
        self.pairs["checks"][0]["forward_rows"][0]["neuropil"] = "OCG"
        self.validation["manifest_sha256"][GRAPH] = "0" * 64
        self.assertFalse(self.result()["pass"])
