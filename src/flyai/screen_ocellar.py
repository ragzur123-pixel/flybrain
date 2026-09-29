"""Exploratory v783 ocellar-path screen; never selects a final circuit."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc


def candidate_labels(annotations: Path) -> dict[int, dict[str, str]]:
    labels: dict[int, dict[str, str]] = {}
    with annotations.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            role = None
            if row["cell_type"] == "ocellar retinula cell":
                role = "photoreceptor"
            elif row["cell_type"].startswith("OCG01"):
                role = "OCG01"
            elif row["cell_type"] == "DNp22":
                role = "DNp22"
            elif row["hemibrain_type"] in ("DNp20", "DNp28"):
                role = row["hemibrain_type"]
            if role:
                labels[int(row["root_id"])] = {
                    "role": role, "side": row["side"], "status": row["status"] or "(blank)",
                }
    return labels


def screen(path: Path, labels: dict[int, dict[str, str]], batch_rows: int = 50000) -> dict:
    candidate_ids = np.array(sorted(labels), dtype=np.int64)
    pair_weights: Counter[tuple[int, int]] = Counter()
    pair_rows: Counter[tuple[int, int]] = Counter()
    role_rows: Counter[tuple[str, str, str, str]] = Counter()
    role_synapses: Counter[tuple[str, str, str, str]] = Counter()
    with pa.memory_map(str(path), "r") as source:
        reader = ipc.open_file(source)
        for field in ("pre_pt_root_id", "post_pt_root_id", "syn_count"):
            if field not in reader.schema.names:
                raise ValueError(f"Missing connection field: {field}")
        total_rows = 0
        for index in range(reader.num_record_batches):
            batch = reader.get_batch(index)
            total_rows += batch.num_rows
            for start in range(0, batch.num_rows, batch_rows):
                chunk = batch.slice(start, batch_rows)
                pre = chunk.column("pre_pt_root_id").to_numpy()
                post = chunk.column("post_pt_root_id").to_numpy()
                weight = chunk.column("syn_count").to_numpy()
                selected = np.flatnonzero(np.isin(pre, candidate_ids) & np.isin(post, candidate_ids))
                for position in selected:
                    a, b, count = int(pre[position]), int(post[position]), int(weight[position])
                    pair_weights[(a, b)] += count
                    pair_rows[(a, b)] += 1
                    key = (labels[a]["role"], labels[b]["role"], labels[a]["side"], labels[b]["side"])
                    role_rows[key] += 1
                    role_synapses[key] += count

    paths = {}
    photos = {rid for rid, row in labels.items() if row["role"] == "photoreceptor"}
    ocg = {rid for rid, row in labels.items() if row["role"] == "OCG01"}
    outputs = {rid for rid, row in labels.items() if row["role"] in ("DNp20", "DNp22", "DNp28")}
    for threshold in (1, 5):
        photo_to_ocg: dict[int, set[int]] = defaultdict(set)
        ocg_to_output: dict[int, set[int]] = defaultdict(set)
        photo_to_output: dict[int, set[int]] = defaultdict(set)
        for (a, b), count in pair_weights.items():
            if count < threshold:
                continue
            if a in photos and b in ocg:
                photo_to_ocg[b].add(a)
            if a in ocg and b in outputs:
                ocg_to_output[b].add(a)
            if a in photos and b in outputs:
                photo_to_output[b].add(a)
        paths[str(threshold)] = [
            {
                "output_root_id": str(output),
                "output_role": labels[output]["role"],
                "output_side": labels[output]["side"],
                "output_status": labels[output]["status"],
                "direct_ocg_inputs": len(ocg_to_output[output]),
                "direct_photoreceptors": len(photo_to_output[output]),
                "two_hop_photoreceptors": len(set().union(*(photo_to_ocg[node] for node in ocg_to_output[output]))),
            }
            for output in sorted(outputs)
        ]
    return {
        "exploratory": True, "row_count_scanned": total_rows,
        "candidate_id_count": len(candidate_ids),
        "candidate_pair_count": len(pair_weights),
        "candidate_pairs": [
            {
                "pre_root_id": str(a), "post_root_id": str(b),
                "pre_role": labels[a]["role"], "post_role": labels[b]["role"],
                "pre_side": labels[a]["side"], "post_side": labels[b]["side"],
                "pair_synapses": count, "neuropil_rows": pair_rows[(a, b)],
            }
            for (a, b), count in sorted(pair_weights.items())
        ],
        "role_edges": [
            {"pre_role": key[0], "post_role": key[1], "pre_side": key[2], "post_side": key[3],
             "rows": role_rows[key], "synapses": role_synapses[key]}
            for key in sorted(role_rows)
        ],
        "two_hop_paths_by_pair_summed_synapse_threshold": paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    labels = candidate_labels(root / "data/raw/Supplemental_file1_neuron_annotations_v2.1.0.tsv")
    result = screen(root / "data/raw/proofread_connections_783.feather", labels)
    output = root / "data/derived/ocellar_path_screen.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "rows": result["row_count_scanned"],
                      "candidate_pairs": result["candidate_pair_count"],
                      "threshold_paths": result["two_hop_paths_by_pair_summed_synapse_threshold"]}))


if __name__ == "__main__":
    main()
