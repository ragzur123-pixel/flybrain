"""Reconcile saved P1 reports for the chosen publication-time v783 baseline."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PRODUCTS = {
    "proofread_connections_783.feather",
    "proofread_root_ids_783.npy",
    "per_neuron_neuropil_count_pre_783.feather",
    "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
}
GRAPH = "proofread_connections_783.feather"
AGGREGATE = "per_neuron_neuropil_count_pre_783.feather"


def assess(manifest: list[dict], sources: dict, validation: dict,
           pairs: dict, aggregate: dict, codex: dict) -> dict:
    """Check report lineage and the archive-specific acceptance conditions."""
    checks = {}
    manifest_by_name = {row["product"]: row for row in manifest}
    source_by_name = {row["product"]: row for row in sources["products"]}
    checks["four_pinned_products"] = (
        len(manifest) == len(PRODUCTS) == len(sources["products"])
        and set(manifest_by_name) == set(source_by_name) == PRODUCTS
        and all(row["dataset_id"] == "fafb" and row["snapshot"] == "783"
                and len(row["sha256"]) == 64 and row["sha256"] == validation["manifest_sha256"].get(name)
                and row["source_url"] == source_by_name[name]["source_url"]
                and int(row["bytes"]) == source_by_name[name]["expected_bytes"]
                and source_by_name[name]["checksum_type"] in ("md5", "git_blob_sha1")
                and bool(source_by_name[name]["checksum"])
                for name, row in manifest_by_name.items())
    )
    graph_sha = manifest_by_name.get(GRAPH, {}).get("sha256")
    aggregate_sha = manifest_by_name.get(AGGREGATE, {}).get("sha256")
    graph = validation["connections"]
    checks["complete_integrity_scan"] = (
        validation["dataset_id"] == "fafb" and validation["snapshot"] == "783"
        and graph["complete"] is True and graph["rows"] == 16847997
        and graph["batches_scanned"] == graph["record_batches"]
        and all(graph[key] == 0 for key in (
            "duplicate_pair_neuropil_rows", "nonpositive_syn_count",
            "pre_ids_absent_from_proofread", "post_ids_absent_from_proofread"))
    )
    checks["ten_reproducible_ordered_pairs"] = (
        pairs["raw_sha256"] == graph_sha and pairs["rows_scanned"] == graph["rows"]
        and len(pairs["checks"]) == 10
        and len({(row["pre_root_id"], row["post_root_id"]) for row in pairs["checks"]}) == 10
        and all(row["forward_synapses"] > 0 and row["forward_synapses"] ==
                sum(part["syn_count"] for part in row["forward_rows"])
                and all(part["neuropil"] != "UNASGD" for part in row["forward_rows"])
                for row in pairs["checks"])
    )
    checks["archive_aggregate_bound"] = (
        aggregate["release"] == "Zenodo 10676866"
        and aggregate["source_sha256"].get(GRAPH) == graph_sha
        and aggregate["source_sha256"].get(AGGREGATE) == aggregate_sha
        and aggregate["selected_neurons"] == 19
        and aggregate["edge_rows_scanned"] == graph["rows"]
        and aggregate["comparable_regions"] == 56
        and aggregate["region_comparisons"] == 58
        and not aggregate["violations"]
        and len(aggregate["not_comparable"]) == 2
        and all(row["neuropil"] == "UNASGD" for row in aggregate["not_comparable"])
    )
    checks["current_codex_disclosed_separately"] = (
        codex["archive_sha256"] == graph_sha and codex["codex_exports"] == 10
        and codex["matched"] == 0 and codex["discrepant"] == 10
        and codex["comparison"] == "publication-time archive vs current Codex export"
    )
    return {"baseline": "publication-time 2024 FAFB v783 archive",
            "checks": checks, "pass": all(checks.values()),
            "limitations": [
                "Current Codex counts are a different product and remain 0/10 matched.",
                "The archive aggregate is a subset bound, not an exact independent pair measurement.",
                "UNASGD is absent from the aggregate; two rows are not comparable.",
                "Circuit IDs, threshold, neurotransmitter signs, and motor decoding remain P2/P4 decisions.",
            ]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    with (root / "data/raw/manifest.csv").open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    read = lambda path: json.loads((root / path).read_text(encoding="utf-8"))
    result = assess(manifest, read("configs/data_sources.json"),
                    read("data/derived/full_validation.json"),
                    read("data/derived/manual_pair_raw_audit.json"),
                    read("data/derived/archive_aggregate_check.json"),
                    read("data/derived/codex_reconciliation.json"))
    output = root / "data/derived/p1_archive_gate_check.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "pass": result["pass"],
                      "checks": result["checks"]}))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
