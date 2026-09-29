"""Independently audit the ten pending v783 manual-check pairs in raw rows."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.prepare_manual_checks import select_checks
from flyai.validate_raw import verify_manifest


def audit_pairs(path: Path, checks: list[dict], batch_rows: int = 50000) -> dict:
    if batch_rows <= 0:
        raise ValueError("batch_rows must be positive")
    ordered = {(int(p["pre_root_id"]), int(p["post_root_id"])): p for p in checks}
    if len(ordered) != len(checks):
        raise ValueError("Repeated directed pair in manual-check packet")
    watched = set(ordered) | {(b, a) for a, b in ordered}
    watched_pre = np.array(sorted({a for a, _ in watched}), dtype=np.int64)
    watched_post = np.array(sorted({b for _, b in watched}), dtype=np.int64)
    rows: dict[tuple[int, int], list[dict]] = defaultdict(list)
    total_rows = 0
    with pa.memory_map(str(path), "r") as source:
        reader = ipc.open_file(source)
        required = {"pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count"}
        if not required.issubset(reader.schema.names):
            raise ValueError("Connection file lacks required pair-audit columns")
        for index in range(reader.num_record_batches):
            batch = reader.get_batch(index)
            total_rows += batch.num_rows
            for start in range(0, batch.num_rows, batch_rows):
                chunk = batch.slice(start, batch_rows)
                pre = chunk.column("pre_pt_root_id").to_numpy()
                post = chunk.column("post_pt_root_id").to_numpy()
                selected = np.flatnonzero(np.isin(pre, watched_pre) & np.isin(post, watched_post))
                weights = chunk.column("syn_count")
                neuropils = chunk.column("neuropil")
                for position in selected:
                    pair = (int(pre[position]), int(post[position]))
                    if pair in watched:
                        rows[pair].append({
                            "neuropil": neuropils[position].as_py(),
                            "syn_count": int(weights[position].as_py()),
                        })
    audited = []
    for (pre, post), planned in ordered.items():
        forward = sorted(rows[(pre, post)], key=lambda row: row["neuropil"])
        reverse = sorted(rows[(post, pre)], key=lambda row: row["neuropil"])
        forward_total = sum(row["syn_count"] for row in forward)
        if forward_total != planned["pair_synapses"] or len(forward) != planned["neuropil_rows"]:
            raise ValueError(f"Raw rows disagree with selected pair {pre}->{post}")
        audited.append({
            "pre_root_id": str(pre), "post_root_id": str(post),
            "pre_role": planned["pre_role"], "post_role": planned["post_role"],
            "pre_side": planned["pre_side"], "post_side": planned["post_side"],
            "forward_synapses": forward_total, "forward_rows": forward,
            "reverse_synapses": sum(row["syn_count"] for row in reverse),
            "reverse_rows": reverse, "portal_status": "pending",
        })
    return {"source": "FAFB v783 raw connection rows", "portal_verified": False,
            "rows_scanned": total_rows, "checks": audited}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", {
        "proofread_connections_783.feather", "proofread_root_ids_783.npy",
        "per_neuron_neuropil_count_pre_783.feather",
        "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
    })
    screen_path = root / "data/derived/ocellar_path_screen.json"
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    if not screen.get("exploratory") or screen["row_count_scanned"] != 16847997:
        raise ValueError("Expected completed v783 candidate screen")
    checks = select_checks(screen["candidate_pairs"])
    result = audit_pairs(root / "data/raw/proofread_connections_783.feather", checks)
    if result["rows_scanned"] != screen["row_count_scanned"]:
        raise ValueError("Raw row count differs from candidate screen")
    result["raw_sha256"] = manifest["proofread_connections_783.feather"]["sha256"]
    result["screen_path"] = "data/derived/ocellar_path_screen.json"
    output = root / "data/derived/manual_pair_raw_audit.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "checks": len(result["checks"]),
                      "rows_scanned": result["rows_scanned"], "portal_verified": False}))


if __name__ == "__main__":
    main()
