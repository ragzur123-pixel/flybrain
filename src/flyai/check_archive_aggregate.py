"""Cross-check archived proofread edges against the release's all-synapse totals.

The per-neuron table includes partners outside the proofread edge list, so its
per-region presynaptic counts are an upper bound, not an equality target.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.validate_raw import verify_manifest


PRODUCTS = {
    "proofread_connections_783.feather",
    "proofread_root_ids_783.npy",
    "per_neuron_neuropil_count_pre_783.feather",
    "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
}


def selected_counts(path: Path, ids: set[int], id_column: str, count_column: str) -> tuple[Counter, int, set[str]]:
    if not ids:
        raise ValueError("No selected neuron IDs")
    watched = np.array(sorted(ids), dtype=np.int64)
    counts: Counter[tuple[int, str]] = Counter()
    total_rows = 0
    all_regions: set[str] = set()
    # OSFile avoids a lingering Windows memory map when small test files close.
    with pa.OSFile(str(path), "rb") as source:
        reader = ipc.open_file(source)
        required = {id_column, "neuropil", count_column}
        if not required.issubset(reader.schema.names):
            raise ValueError(f"{path.name} lacks {sorted(required - set(reader.schema.names))}")
        for batch_index in range(reader.num_record_batches):
            batch = reader.get_batch(batch_index)
            total_rows += batch.num_rows
            id_values = batch.column(id_column).to_numpy()
            positions = np.flatnonzero(np.isin(id_values, watched))
            regions = batch.column("neuropil")
            all_regions.update(region for region in regions.unique().to_pylist() if region)
            weights = batch.column(count_column)
            for position in positions:
                region = regions[position].as_py()
                count = weights[position].as_py()
                if not region or count is None or count <= 0:
                    raise ValueError(f"Invalid selected count in {path.name}")
                counts[(int(id_values[position]), region)] += int(count)
    return counts, total_rows, all_regions


def compare_counts(edge_counts: Counter, total_counts: Counter, ids: set[int],
                   available_regions: set[str]) -> dict:
    rows = []
    violations = []
    not_comparable = []
    for neuron_id in sorted(ids):
        regions = sorted({region for key_id, region in edge_counts | total_counts if key_id == neuron_id})
        for region in regions:
            proofread = edge_counts[(neuron_id, region)]
            all_synapses = total_counts[(neuron_id, region)]
            row = {"pre_root_id": str(neuron_id), "neuropil": region,
                   "proofread_partner_synapses": proofread, "all_partner_synapses": all_synapses,
                   "unproofread_or_excluded_remainder": all_synapses - proofread,
                   "comparable": region in available_regions}
            rows.append(row)
            if region not in available_regions:
                not_comparable.append(row)
            elif proofread > all_synapses:
                violations.append(row)
    return {"selected_neurons": len(ids), "region_comparisons": len(rows),
            "comparable_regions": len(rows) - len(not_comparable),
            "violations": violations, "not_comparable": not_comparable, "rows": rows,
            "proofread_partner_total": sum(edge_counts.values()),
            "all_partner_total": sum(total_counts.values())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    audit = json.loads((root / "data/derived/manual_pair_raw_audit.json").read_text(encoding="utf-8"))
    ids = {int(row[field]) for row in audit["checks"] for field in ("pre_root_id", "post_root_id")}
    if len(audit["checks"]) != 10 or len(ids) != 19:
        raise ValueError("Expected ten planned pairs and 19 distinct IDs")
    edges, edge_rows, edge_regions = selected_counts(root / "data/raw/proofread_connections_783.feather", ids,
                                       "pre_pt_root_id", "syn_count")
    totals, aggregate_rows, aggregate_regions = selected_counts(root / "data/raw/per_neuron_neuropil_count_pre_783.feather", ids,
                                             "pre_pt_root_id", "count")
    result = compare_counts(edges, totals, ids, aggregate_regions)
    result.update({"dataset_id": "fafb", "snapshot": "783", "release": "Zenodo 10676866",
                   "edge_rows_scanned": edge_rows, "aggregate_rows_scanned": aggregate_rows,
                   "aggregate_region_count": len(aggregate_regions),
                   "edge_regions_absent_from_aggregate": sorted(edge_regions - aggregate_regions),
                   "source_sha256": {name: manifest[name]["sha256"] for name in
                                     ("proofread_connections_783.feather", "per_neuron_neuropil_count_pre_783.feather")},
                   "meaning": "For neuropils present in both files, the proofread-pair subtotal must not exceed all-partner presynaptic counts. Regions absent from the entire aggregate file are reported as not comparable, not treated as zero or silently removed. Equality is not expected."})
    output = root / "data/derived/archive_aggregate_check.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "selected_neurons": len(ids),
                      "region_comparisons": result["region_comparisons"],
                      "comparable_regions": result["comparable_regions"],
                      "not_comparable": len(result["not_comparable"]),
                      "violations": len(result["violations"])}))
    if result["violations"]:
        raise ValueError("Proofread edge subtotal exceeds published all-synapse aggregate")


if __name__ == "__main__":
    main()
