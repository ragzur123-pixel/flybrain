"""Audit seven deterministic selected edges against raw neuropil rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.audit_manual_pairs import audit_pairs
from flyai.compare_circuit_options import PRODUCTS
from flyai.validate_raw import verify_manifest


def select_edges(edges: list[dict]) -> list[dict]:
    groups = {}
    for row in edges:
        if row["pre_role"] == "photoreceptor" and row["post_role"] == "OCG01":
            category = ("photoreceptor_OCG01", row["pre_side"])
        elif row["pre_role"] == "OCG01" and row["post_role"] in ("DNp20", "DNp22"):
            category = (row["post_role"], row["post_side"])
        else:
            raise ValueError("Selected edge has a role outside the chosen path")
        candidate_key = (-int(row["pair_synapses"]), int(row["pre_root_id"]), int(row["post_root_id"]))
        if category not in groups or candidate_key < groups[category][0]:
            groups[category] = (candidate_key, row)
    expected = {("photoreceptor_OCG01", side) for side in ("left", "center", "right")}
    expected |= {(role, side) for role in ("DNp20", "DNp22")
                 for side in ("left", "right")}
    if set(groups) != expected:
        raise ValueError(f"Seven role/side audit categories required, got {set(groups)}")
    return [groups[key][1] for key in sorted(groups)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "data/derived/selected_edge_raw_audit.json"
    document = root / "docs/selected_edge_raw_audit.md"
    if output.exists() or document.exists():
        raise FileExistsError("Selected-edge audit output exists; preserve it")
    report = json.loads((root / "data/derived/selected_subnetwork_report.json").read_text(encoding="utf-8"))
    edge_path = root / "data/derived/selected_subnetwork_edges.csv"
    if hashlib.sha256(edge_path.read_bytes()).hexdigest() != report["edges_csv_sha256"]:
        raise ValueError("Selected edge CSV hash changed")
    with edge_path.open(encoding="utf-8", newline="") as stream:
        selected = select_edges(list(csv.DictReader(stream)))
    for row in selected:
        row["pair_synapses"] = int(row["pair_synapses"])
        row["neuropil_rows"] = int(row["neuropil_rows"])
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    if manifest["proofread_connections_783.feather"]["sha256"] != report["raw_connection_sha256"]:
        raise ValueError("Selected graph's raw baseline changed")
    audited = audit_pairs(root / "data/raw/proofread_connections_783.feather", selected)
    if audited["rows_scanned"] != report["raw_rows_scanned"]:
        raise ValueError("Raw row count changed")
    audited.pop("portal_verified")
    audited["raw_audit_only"] = True
    for check in audited["checks"]:
        check.pop("portal_status")
    audited["selected_edges_sha256"] = report["edges_csv_sha256"]
    audited["raw_connection_sha256"] = report["raw_connection_sha256"]
    output.write_text(json.dumps(audited, indent=2), encoding="utf-8")
    lines = ["# Selected edge raw-row audit — 2026-09-28", "",
             "Seven reproducibly chosen edges were checked against a fresh scan",
             "of the same checksum-pinned 16,847,997-row raw archive. For each",
             "edge, the neuropil-row count and summed `syn_count` agreed with",
             "the selected edge CSV. Reverse directions were counted separately.",
             "This is a raw-file audit, not a current Codex portal comparison or",
             "physiological validation.", "",
             "| Pre role/side → post role/side | Pre ID → post ID | Raw synapses | Raw neuropil rows | Reverse synapses |",
             "| --- | --- | ---: | ---: | ---: |"]
    for check in audited["checks"]:
        lines.append(
            f"| {check['pre_role']} {check['pre_side']} → {check['post_role']} {check['post_side']} | "
            f"`{check['pre_root_id']}` → `{check['post_root_id']}` | "
            f"{check['forward_synapses']} | {len(check['forward_rows'])} | {check['reverse_synapses']} |"
        )
    lines += ["", f"Raw graph SHA-256: `{report['raw_connection_sha256']}`.",
              f"Selected edge CSV SHA-256: `{report['edges_csv_sha256']}`.",
              "The machine-readable JSON records each matched neuropil row.", ""]
    document.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"checks": len(audited["checks"]), "rows": audited["rows_scanned"],
                      "document": str(document)}))


if __name__ == "__main__":
    main()
